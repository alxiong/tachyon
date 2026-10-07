#!/usr/bin/env python3
"""Assemble a clean, single-speaker sample set for cloning Sean's voice in ElevenLabs.

    .venv/bin/python build_clone_set.py

Inputs (all local, gitignored), each with a <name>.words.json from transcribe_sample.py:
  audio/samples/chapter0.mp3              Sean reading our chapter 0: the target register
  audio/samples/youtube/zconvi_sean.mp3   Sean's ZconVI talk: more of his voice and cadence

Output: audio/clone/
  sean_NN.mp3        utterances cut at natural pauses, loudness-normalized, 6-30 s each
  manifest.json      source, time range, text, pitch before/after, and why each
                     candidate was kept or dropped

Instant voice cloning (IVC) wants a few minutes of clean, consistent speech; more audio
is not better if it mixes rooms or styles. So chapter 0 goes in whole (it is the exact
narration register, and Alex's preferred reference), and the talk contributes only its
cleanest stretches, up to BUDGET.

The talk is livelier than the narration: higher pitch (median ~105 Hz against ~92 Hz)
and wider swings. Each talk clip's pitch contour is therefore remapped onto chapter 0's
statistics in semitones, f' = m0 + (f - m1) * min(1, s0 / s1), with Praat's PSOLA
(parselmouth), which keeps formants and so keeps it sounding like Sean. The spread only
ever shrinks: the talk's swings are already narrower than the narration's, and its
liveliness is pitch height and vocal effort, not range.

Vocal effort (and a different mic and room) shows up as spectral balance: projected
speech carries more upper-mid energy. So all talk clips get one EQ, the difference
between chapter 0's and the talk's long-term average spectrum in third-octave bands,
smoothed over five bands (single bands mostly reflect which words were said, not the
channel) and clamped to ±MAX_EQ_DB. Loudness is then normalized like the chapter 0 clips.
"""
import json, os, statistics, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FFMPEG = "/home/alex/work/tachyon_wt1/video/bin/ffmpeg"
OUT = f"{HERE}/audio/clone"
SR = 16000

# Sean's prepared talk only: from his first word (1:04, after the sponsor bumper) to just
# before he starts reading audience questions aloud (30:12). Set from the transcript.
TALK = f"{HERE}/audio/samples/youtube/zconvi_sean.mp3"
TALK_SPAN = (63.5, 1812.0)
CH0 = f"{HERE}/audio/samples/chapter0.mp3"

MIN_LEN, MAX_LEN = 6.0, 30.0   # seconds per utterance
SPLIT_GAP = 0.45               # cut utterances at pauses at least this long
BUDGET = 8 * 60                # total seconds across all clips (IVC sweet spot: 1-10 min)
F0_TOL = 0.25                  # utterance median pitch within ±25% of Sean's median
MIN_SNR_DB = 25.0              # speech RMS over the quietest 10% of frames
MAX_EQ_DB = 6.0                # cap on any band of the talk-to-narration EQ
FILLERS = {"um", "uh", "er", "ah", "hmm"}
# The talk is spontaneous; a clone learns disfluencies too, so any filler or stutter
# ("the the") disqualifies a clip. Chapter 0 is read narration and is exempt.


def pitch_stats(path):
    """Median and robust spread (IQR / 1.349) of voiced F0, in semitones re 100 Hz."""
    import parselmouth
    f = parselmouth.Sound(path).to_pitch(time_step=0.01, pitch_floor=60, pitch_ceiling=300)
    f = f.selected_array["frequency"]
    st = 12 * np.log2(f[f > 0] / 100.0)
    q1, med, q3 = np.percentile(st, [25, 50, 75])
    return float(med), float((q3 - q1) / 1.349)


def match_pitch(wav_in, wav_out, target):
    """Remap the clip's pitch contour onto target (median, spread) with PSOLA."""
    import parselmouth
    from parselmouth.praat import call
    m1, s1 = pitch_stats(wav_in)
    m0, s0 = target
    k = min(1.0, s0 / s1)
    snd = parselmouth.Sound(wav_in)
    manip = call(snd, "To Manipulation", 0.01, 60, 300)
    tier = call(manip, "Extract pitch tier")
    call(tier, "Formula", f"100 * 2 ^ (({m0} + (12 * log2(self / 100) - {m1}) * {k}) / 12)")
    call([manip, tier], "Replace pitch tier")
    call(manip, "Get resynthesis (overlap-add)").save(wav_out, "WAV")
    return (m1, s1), pitch_stats(wav_out)


def ltas_db(paths, centers):
    """Long-term average spectrum in third-octave bands (dB), pooled over files."""
    psd, n = 0.0, 0
    for p in paths:
        raw = subprocess.run([FFMPEG, "-loglevel", "error", "-i", p, "-f", "f32le", "-ac", "1",
                              "-ar", "44100", "-"], capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.float32)
        fr = x[: len(x) // 2048 * 2048].reshape(-1, 2048)
        fr = fr[np.sqrt(np.mean(fr ** 2, axis=1)) > 0.01]  # speech frames only
        psd = psd + np.sum(np.abs(np.fft.rfft(fr * np.hanning(2048), axis=1)) ** 2, axis=0)
        n += len(fr)
    freqs = np.fft.rfftfreq(2048, 1 / 44100)
    out = []
    for fc in centers:
        band = (freqs >= fc / 2 ** (1 / 6)) & (freqs < fc * 2 ** (1 / 6))
        out.append(10 * np.log10(np.mean(psd[band] / n) + 1e-20))
    return np.array(out)


def talk_eq(ch0_wavs, talk_wavs):
    """ffmpeg firequalizer filter moving the talk's spectrum onto chapter 0's."""
    centers = 100 * 2 ** (np.arange(0, 19) / 3)          # 100 Hz .. 6.4 kHz
    diff = ltas_db(ch0_wavs, centers) - ltas_db(talk_wavs, centers)
    mid = (centers >= 300) & (centers <= 3000)
    diff = np.convolve(np.pad(diff, 2, mode="edge"), np.ones(5) / 5, mode="valid")  # broad trend only
    diff = np.clip(diff - np.mean(diff[mid]), -MAX_EQ_DB, MAX_EQ_DB)  # shape only; loudnorm sets level
    entries = ";".join(f"entry({fc:.0f},{g:.1f})" for fc, g in zip(centers, diff))
    return f"firequalizer=gain_entry='{entries}'", dict(zip((int(c) for c in centers), np.round(diff, 1).tolist()))


def load(path):
    raw = subprocess.run([FFMPEG, "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def snr_db(x):
    fr = x[: len(x) // 400 * 400].reshape(-1, 400)  # 25 ms frames
    e = np.sqrt(np.mean(fr ** 2, axis=1)) + 1e-9
    return float(20 * np.log10(np.percentile(e, 90) / np.percentile(e, 10)))


def utterances(words, span):
    lo, hi = span or (0, 1e9)
    words = [w for w in words if lo <= w["s"] and w["e"] <= hi]
    cur = []
    for w in words:
        if cur and (w["s"] - cur[-1]["e"] >= SPLIT_GAP and cur[-1]["e"] - cur[0]["s"] >= MIN_LEN
                    or w["e"] - cur[0]["s"] > MAX_LEN):
            yield cur
            cur = []
        cur.append(w)
    if cur:
        yield cur


def candidates(path, span, sean_f0, source):
    data = json.load(open(os.path.splitext(path)[0] + ".words.json"))
    audio = load(path)
    for utt in utterances(data["words"], span):
        s, e = utt[0]["s"], utt[-1]["e"]
        x = audio[int(s * SR):int(e * SR)]
        pitches = [w["f0"] for w in utt if w["f0"]]
        f0 = statistics.median(pitches) if pitches else None
        why = []
        if e - s < MIN_LEN:
            why.append("short")
        if f0 is None or abs(f0 / sean_f0 - 1) > F0_TOL:
            why.append(f"pitch {f0}")  # another speaker, or laughter/music
        toks = [w["w"].lower().strip(".,?!;:") for w in utt]
        if source != "chapter0":
            if FILLERS & set(toks):
                why.append("filler")
            if any(a == b for a, b in zip(toks, toks[1:])):
                why.append("stutter")
        if np.max(np.abs(x)) > 0.99:
            why.append("clipped")
        snr = snr_db(x)
        if snr < MIN_SNR_DB:
            why.append(f"snr {snr:.0f}dB")
        yield {"source": source, "s": s, "e": e, "dur": round(e - s, 2), "f0": f0,
               "snr_db": round(snr, 1), "text": " ".join(w["w"] for w in utt),
               "keep": not why, "why": why}


def main():
    sean_f0 = json.load(open(os.path.splitext(CH0)[0] + ".words.json"))["median_f0_hz"]
    ch0 = list(candidates(CH0, None, sean_f0, "chapter0"))
    talk = list(candidates(TALK, TALK_SPAN, sean_f0, "zconvi"))
    # Chapter 0 first (target register), then the cleanest talk clips until the budget.
    chosen, total = [], 0.0
    for c in ch0 + sorted((c for c in talk if c["keep"]), key=lambda c: -c["snr_db"]):
        if c["keep"] and total + c["dur"] <= BUDGET:
            chosen.append(c)
            total += c["dur"]
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.startswith("sean_") and f.endswith(".mp3"):
            os.remove(f"{OUT}/{f}")
    # Chapter 0's pitch statistics are the target for every talk clip.
    tmp = f"{OUT}/_tmp"
    os.makedirs(tmp, exist_ok=True)
    subprocess.run([FFMPEG, "-loglevel", "error", "-y", "-i", CH0, "-ac", "1", f"{tmp}/ch0.wav"],
                   check=True)
    target = pitch_stats(f"{tmp}/ch0.wav")
    # Pass 1: cut every clip (50 ms handles, high-pass for rumble); pitch-match the talk.
    staged = []
    for i, c in enumerate(chosen, 1):
        src = CH0 if c["source"] == "chapter0" else TALK
        c["file"] = f"sean_{i:02d}.mp3"
        raw = f"{tmp}/{i:02d}_raw.wav"
        subprocess.run([FFMPEG, "-loglevel", "error", "-y", "-ss", str(max(0, c["s"] - 0.05)),
                        "-to", str(c["e"] + 0.15), "-i", src, "-ac", "1", "-ar", "44100",
                        "-af", "highpass=f=70", raw], check=True)
        if c["source"] == "zconvi":
            adj = f"{tmp}/{i:02d}_adj.wav"
            before, after = match_pitch(raw, adj, target)
            c["pitch_st_before"] = [round(v, 2) for v in before]
            c["pitch_st_after"] = [round(v, 2) for v in after]
            raw = adj
        staged.append((c, raw))
    # Pass 2: one spectral-balance EQ for all talk clips, then the same loudness for all
    # (EBU R128 to -18 LUFS, peaks <= -3 dBFS).
    eq, eq_curve = talk_eq([r for c, r in staged if c["source"] == "chapter0"],
                           [r for c, r in staged if c["source"] == "zconvi"])
    for c, raw in staged:
        af = "loudnorm=I=-18:TP=-3:LRA=11"
        if c["source"] == "zconvi":
            af = f"{eq},{af}"
        subprocess.run([FFMPEG, "-loglevel", "error", "-y", "-i", raw, "-af", af,
                        "-b:a", "192k", f"{OUT}/{c['file']}"], check=True)
    for f in os.listdir(tmp):
        os.remove(f"{tmp}/{f}")
    os.rmdir(tmp)
    json.dump({"sean_median_f0_hz": sean_f0, "target_pitch_st": [round(v, 2) for v in target],
               "talk_eq_db": eq_curve,
               "talk_span": TALK_SPAN, "total_s": round(total, 1),
               "chosen": chosen, "rejected": [c for c in ch0 + talk if not c["keep"]]},
              open(f"{OUT}/manifest.json", "w"), indent=1)
    by = {k: sum(c["dur"] for c in chosen if c["source"] == k) for k in ("chapter0", "zconvi")}
    print(f"{len(chosen)} clips, {total / 60:.1f} min "
          f"(chapter0 {by['chapter0']:.0f}s, zconvi {by['zconvi']:.0f}s); "
          f"rejected {sum(not c['keep'] for c in ch0 + talk)}")


if __name__ == "__main__":
    main()

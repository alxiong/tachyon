#!/usr/bin/env python3
"""Transcribe a human narration sample with cadence and tone markup.

    .venv/bin/python transcribe_sample.py audio/samples/chapter0.mp3

Writes next to the input:
  <name>.words.json     every word: text, start, end, loudness (dB vs median), f0 (Hz)
  <name>.transcript.md  readable transcript with prosody markup (legend at the top)

Runs locally (faster-whisper medium.en, CPU int8); nothing leaves the machine.
Fillers ("um", "uh", "so") are kept on purpose: they are part of the cadence.
"""
import json, os, statistics, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

FFMPEG = "/home/alex/work/tachyon_wt1/video/bin/ffmpeg"
SR = 16000
PAUSE_SHOW = 0.35    # gaps at least this long are written out as [0.8s]
PARA_GAP = 1.6       # gaps at least this long start a new paragraph
LOUD_DB = 5.0        # word this much louder than its neighbours reads as stressed
SOFT_DB = -8.0       # this much quieter than its neighbours reads as dropped / aside


def load(path: str) -> np.ndarray:
    raw = subprocess.run([FFMPEG, "-loglevel", "error", "-i", path, "-f", "f32le",
                          "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def rms_db(x: np.ndarray) -> float:
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)


def f0(x: np.ndarray) -> float | None:
    """Median pitch over 40 ms frames by autocorrelation (75–300 Hz); None if unvoiced."""
    n, hop, out = int(0.04 * SR), int(0.01 * SR), []
    lo, hi = SR // 300, SR // 75
    for i in range(0, len(x) - n, hop):
        fr = x[i:i + n] - np.mean(x[i:i + n])
        if np.sqrt(np.mean(fr ** 2)) < 0.01:
            continue
        ac = np.correlate(fr, fr, "full")[n - 1:]
        lag = lo + int(np.argmax(ac[lo:hi]))
        if ac[lag] > 0.45 * ac[0]:
            out.append(SR / lag)
    return float(np.median(out)) if out else None


def main(path: str) -> None:
    audio = load(path)
    model = WhisperModel("medium.en", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(
        audio, language="en", word_timestamps=True, vad_filter=False,
        condition_on_previous_text=True,
        # Priming with disfluencies keeps whisper from silently cleaning them up.
        initial_prompt="Um, so, uh, we have, like, Tachyon, tachygrams, Ragu, nullifiers, Zcash, Orchard.")
    words = []
    for seg in segs:
        for w in seg.words:
            s, e = w.start, w.end
            clip = audio[int(s * SR):int(e * SR)]
            words.append({"w": w.word.strip(), "s": round(s, 3), "e": round(e, 3),
                          "db": float(rms_db(clip)) if len(clip) else -99.0, "f0": f0(clip) if len(clip) > SR * 0.06 else None})
        print(f"{seg.end:6.1f}s", seg.text.strip()[:70], flush=True)

    med_db = statistics.median(w["db"] for w in words)
    pitches = [w["f0"] for w in words if w["f0"]]
    med_f0 = statistics.median(pitches) if pitches else 0
    for w in words:
        w["db"] = round(w["db"] - med_db, 1)
        w["f0"] = round(w["f0"]) if w["f0"] else None
    # Stress is judged against the neighbouring words (±4), not the whole take, so
    # ordinary phrase-initial loudness and declination don't read as emphasis.
    for i, w in enumerate(words):
        nb = [x["db"] for x in words[max(0, i - 4):i + 5] if x is not w]
        w["rel_db"] = round(w["db"] - statistics.median(nb), 1)

    base = os.path.splitext(path)[0]
    json.dump({"median_f0_hz": round(med_f0), "words": words}, open(base + ".words.json", "w"), indent=0)

    # Render markup.
    total = words[-1]["e"] - words[0]["s"]
    spoken = sum(w["e"] - w["s"] for w in words)
    lines = [f"# Transcript: {os.path.basename(path)}", "",
             f"> {len(words)} words in {total:.0f} s: {60 * len(words) / total:.0f} wpm overall, "
             f"{60 * len(words) / spoken:.0f} wpm while speaking. Median pitch {med_f0:.0f} Hz.",
             "> Markup: `[0.8s]` pause; **word** stressed (≥ +5 dB vs neighbours); _word_ dropped (≤ −8 dB);",
             "> `↗`/`↘` pitch at a sentence end rises/falls vs the speaker's median; `«fast»`/`«slow»`",
             "> brackets a clause spoken > 25% faster/slower than the speaker's own average.",
             "> Paragraph breaks are pauses ≥ 1.6 s. Whisper may still smooth some disfluencies.", ""]
    avg_dur = spoken / len(words)
    para, out_words = [], []

    def flush_clause(clause):
        if not clause:
            return
        dur = sum(w["e"] - w["s"] for w in clause) / len(clause)
        text = " ".join(fmt(w) for w in clause)
        if len(clause) >= 4 and dur < 0.75 * avg_dur:
            text = f"«fast» {text} «/fast»"
        elif len(clause) >= 4 and dur > 1.25 * avg_dur:
            text = f"«slow» {text} «/slow»"
        para.append(text)

    def fmt(w):
        t = w["w"]
        core = t.strip(".,?!;:")
        tail = t[len(core):] if t.startswith(core) else ""
        if w["rel_db"] >= LOUD_DB:
            t = f"**{core}**{tail}"
        elif w["rel_db"] <= SOFT_DB:
            t = f"_{core}_{tail}"
        if tail and tail[0] in ".?!" and w["f0"] and med_f0:
            t += " ↗" if w["f0"] > 1.12 * med_f0 else " ↘" if w["f0"] < 0.9 * med_f0 else ""
        return t

    clause = []
    for i, w in enumerate(words):
        gap = w["s"] - words[i - 1]["e"] if i else 0.0
        if gap >= PAUSE_SHOW:
            flush_clause(clause); clause = []
            if gap >= PARA_GAP:
                para.append(f"[{gap:.1f}s]")
                lines.append(" ".join(para)); lines.append(""); para = []
            else:
                para.append(f"[{gap:.1f}s]")
        clause.append(w)
    flush_clause(clause)
    lines.append(" ".join(para))
    open(base + ".transcript.md", "w").write("\n".join(lines) + "\n")
    print("wrote", base + ".transcript.md")


if __name__ == "__main__":
    main(sys.argv[1])

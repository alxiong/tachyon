#!/usr/bin/env python3
"""Generate per-scene narration for v2 from NARRATION.md with ElevenLabs.

Each voice has its own settings, respellings and output directory, so voices never
overwrite each other's takes:
  brian -> audio/raw/scene-X.Y.mp3, audio/final/scene-X.Y.mp3          (the v1 stock voice)
  sean  -> audio/sean/raw/scene-X.Y.mp3, audio/sean/final/scene-X.Y.mp3  (Sean's clone)
  sts   -> audio/sts/raw/scene-X.Y.mp3, audio/sts/final/scene-X.Y.mp3    (Brian, Sean's delivery)
Raw is one clip per scene (a retake costs one scene); final adds the voice's speed factor,
any sentence-gap lengthening, and a 1 s lead-in pad. Voices with character timings also
write <dir>/words.json: word start/end times in the final clip, spelled as in NARRATION.md,
for the animation anchors (scenes/style.py).

    .venv/bin/python generate_audio.py --voice sean 2.1 2.2 2.3   # some scenes
    .venv/bin/python generate_audio.py --voice sean               # all scenes
    .venv/bin/python generate_audio.py --voice sean --dry-run     # normalized text + chars
    .venv/bin/python generate_audio.py --voice sean --finalize-only  # redo speed/pad, no credits
"""

import base64
import json
import os
import re
import subprocess
import sys

import numpy as np

from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv("/home/alex/work/tachyon_wt1/.env")

MODEL_ID = "eleven_multilingual_v2"
FFMPEG = "/home/alex/work/tachyon_wt1/video/bin/ffmpeg"

VOICES = {
    "brian": {
        "voice_id": "nPczCjzI2devNBz1zQrb",  # Brian (v1 voice)
        "settings": {"stability": 0.38, "similarity_boost": 0.80, "style": 0.45,
                     "use_speaker_boost": True},
        "speed": 1.145,  # 1.08 (v1) x 1.06 (Alex, 2026-10-04: slightly brisker)
        "dir": "audio",
        # Respellings chosen by Alex from audio/samples/.
        "respell": {"tachyon": "Tackeon", "tachygram": "takkigram", "psi": "psy", "ragu": "Rah-goo"},
        "pause_mode": "tag",  # legacy: ElevenLabs <break> tags (the existing takes use these)
        "pause": 0.6,
        "held_pause": 0.6,
    },
    "sean": {
        # Instant clone from audio/clone/ (clone_voice.py, 2026-10-07): Sean's chapter 0
        # read plus his ZconVI talk, pitch/EQ-matched to the read.
        "voice_id": "IcLWy0lTx58dBwMajoEh",
        # Clones drift from the speaker at high style/low stability; keep similarity high.
        "settings": {"stability": 0.45, "similarity_boost": 0.85, "style": 0.15,
                     "use_speaker_boost": True},
        "speed": 1.0,  # in-sentence pace already matches Sean (~200 wpm while speaking)
        # The clone stops ~0.34 s at a sentence end where Sean stops ~0.79 s (his chapter 0
        # take; commas already match). Adding the difference to every sentence-end gap keeps
        # the clone's own variation and lands on Sean's spread (p25/p75 ~0.6/1.0 s).
        "sentence_gap_add": 0.45,
        "dir": "audio/sean",
        # Closest to Sean's own takes (audio/samples/pron/sean_*.wav) by log-mel DTW over
        # clone candidates in audio/samples/pron/clone/; confirm by ear.
        # "prover" was read like the "prov" in "proverb" (Alex, 2026-10-07).
        "respell": {"tachyon": "Takion", "tachygram": "takkigram", "psi": "psy", "ragu": "Rag-oo",
                    "prover": "proover"},
        # <break> tags made the model render noise inside the pauses. Instead the text goes
        # out without them, and digital silence is inserted at each ⟨pause⟩ afterwards,
        # located by the character timings that come back with the audio.
        "pause_mode": "silence",
        "pause": 0.6,       # added on top of the model's own gap there
        "held_pause": 1.0,  # replaces sentence_gap_add where both fall on the same gap
    },
    "sts": {
        # Brian (the v1 stock voice) with Sean's delivery as far as settings carry it
        # (Alex, 2026-10-08). eleven_v3 rises and falls like Sean's own read converted into
        # Brian (pitch spread 4.1 st for both; Brian on v2 with the Sean clone converted came
        # out flatter at 3.4 st), but it reads slowly, so the take is sped up to Sean's
        # in-sentence pace afterwards. Per-scene speech-to-speech from the Sean clone would
        # cost ~1,000 credits per minute on top of the TTS, more than the budget held.
        "voice_id": "nPczCjzI2devNBz1zQrb",
        "model": "eleven_v3",
        "context": False,  # v3 takes no previous_text/next_text
        "settings": {"stability": 0.5, "similarity_boost": 0.85, "style": 0.0,
                     "use_speaker_boost": True},  # v3 stability is 0, 0.5 or 1
        "speed": 1.3,  # v3 reads ~30% slower than Sean (~195 wpm in-sentence on the chapter 0 read)
        "sentence_gap_median": 0.79,  # Sean's median sentence-end gap, after the speed-up
        "dir": "audio/sts",
        # Closest to Sean's clips (audio/samples/pron/sean_*.wav) by log-mel DTW over Brian v3
        # candidates in audio/samples/pron/brian_v3/; confirm by ear.
        "respell": {"tachyon": "Tak-ee-on", "tachygram": "Tak-ee-gram", "psi": "psy",
                    "ragu": "Ra-goo", "prover": "proover"},
        "pause_mode": "silence",
        "pause": 0.6,
        "held_pause": 1.0,
    },
}


def parse_scenes(path: str) -> list[tuple[str, str]]:
    scenes, cur, buf = [], None, []
    for line in open(path):
        m = re.match(r"### (\d+\.\d+) —", line)
        if m:
            if cur:
                scenes.append((cur, "".join(buf)))
            cur, buf = m.group(1), []
        elif line.startswith(("#", ">", "---")):
            continue
        elif cur:
            buf.append(line)
    if cur:
        scenes.append((cur, "".join(buf)))
    return scenes


def normalize(body: str, voice: dict) -> str:
    """Respelled scene text. Pauses stay as ⟦p:SECONDS⟧ markers; see split()."""
    sp = voice["respell"]
    # Placeholders first, so a respelling can't be re-matched by a later pattern.
    for word in sorted(sp, key=len, reverse=True):
        body = re.sub(rf"\b{word}(s?)\b", lambda m: f"@{word.upper()}@{m.group(1)}", body,
                      flags=re.IGNORECASE)
    for word, rep in sp.items():
        body = body.replace(f"@{word.upper()}@", rep)
    # A held pause (the animation plays) is a little longer than a breath.
    body = re.sub(r"⟨pause:[^⟩]*⟩", f"⟦p:{voice['held_pause']}⟧", body)
    body = body.replace("⟨pause⟩", f"⟦p:{voice['pause']}⟧")
    body = body.replace("*", "").replace("`", "")
    paras = [re.sub(r"\s+", " ", p).strip() for p in body.split("\n\n")]
    return "\n\n".join(p for p in paras if p)


def paths(voice: dict, sid: str) -> tuple[str, str]:
    d = f"{HERE}/{voice['dir']}"
    return f"{d}/raw/scene-{sid}.mp3", f"{d}/final/scene-{sid}.mp3"


def split(body: str, voice: dict) -> tuple[str, list[tuple[int, float]]]:
    """(text sent to the API, [(character index in that text, pause seconds)]).

    In "tag" mode the markers become <break> tags and the list is empty. In "silence"
    mode the markers are dropped from the text, and each pause is recorded at the
    position just after the last character before it.
    """
    marker = r"\s*⟦p:([0-9.]+)⟧\s*"
    if voice["pause_mode"] == "tag":
        return re.sub(marker, lambda m: f' <break time="{m.group(1)}s" /> ', body).strip(), []
    out, pauses, pos = "", [], 0
    for m in re.finditer(marker, body):
        out += body[pos:m.start()]
        pauses.append((len(out), float(m.group(1))))
        nxt = body[m.end():m.end() + 1]
        if out and nxt and not out[-1].isspace() and not nxt.isspace():
            out += " "
        pos = m.end()
    out += body[pos:]
    lead = len(out) - len(out.lstrip())
    return out.strip(), [(max(0, i - lead), sec) for i, sec in pauses]


def spoken(body: str, voice: dict) -> str:
    """The scene text as actually spoken (no pause markers or break tags)."""
    text = split(body, voice)[0]
    return re.sub(r"\s+", " ", re.sub(r"<break[^>]*/>", " ", text)).strip()


def save_alignment(raw: str, chars, starts, ends) -> None:
    json.dump({"chars": list(chars), "starts": list(starts), "ends": list(ends)},
              open(raw.replace(".mp3", ".align.json"), "w"))


def alignment(raw: str, body: str, voice: dict) -> dict:
    """Character timings for the scene's own script text (NARRATION.md is the authority).

    New renders save these from the timestamped TTS call. A raw clip rendered without
    them is aligned against its script text with ElevenLabs forced alignment, once.
    """
    cache = raw.replace(".mp3", ".align.json")
    if not os.path.exists(cache):
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
        with open(raw, "rb") as f:
            r = client.forced_alignment.create(file=f, text=spoken(body, voice))
        save_alignment(raw, [c.text for c in r.characters], [c.start for c in r.characters],
                       [c.end for c in r.characters])
    return json.load(open(cache))


def sentence_gaps(al: dict) -> list[tuple[float, float]]:
    """(end of a sentence's last character, start of the next sentence) from the script's
    own punctuation: a . ? or ! followed by whitespace, skipping break-tag characters."""
    chars, starts, ends = al["chars"], al["starts"], al["ends"]
    text = "".join(chars)
    tags = [m.span() for m in re.finditer(r"<break[^>]*/>", text)]
    in_tag = lambda i: any(lo <= i < hi for lo, hi in tags)
    gaps = []
    for i, ch in enumerate(chars):
        if ch in ".?!" and not in_tag(i) and (i + 1 == len(chars) or chars[i + 1].isspace()):
            nxt = next((j for j in range(i + 1, len(chars))
                        if not chars[j].isspace() and not in_tag(j)), None)
            if nxt is not None:
                gaps.append((ends[i], starts[nxt]))
    return gaps


def gap_around(al: dict, idx: int) -> tuple[float, float]:
    """(end of the last character before text position idx, start of the next one)."""
    chars, starts, ends = al["chars"], al["starts"], al["ends"]
    p = next((j for j in range(idx - 1, -1, -1) if not chars[j].isspace()), None)
    n = next((j for j in range(idx, len(chars)) if not chars[j].isspace()), None)
    t0 = ends[p] if p is not None else 0.0
    t1 = starts[n] if n is not None else ends[-1]
    return t0, max(t0, t1)


def insert_silences(raw: str, body: str, voice: dict) -> str:
    """Insert digital silence at the quietest point of each gap that needs one:
    ⟨pause⟩ markers (in "silence" mode) and sentence ends (sentence_gap_add). Where both
    fall on the same gap, the pause wins rather than adding up."""
    sr = 44100
    x = np.frombuffer(subprocess.run([FFMPEG, "-loglevel", "error", "-i", raw, "-f", "f32le",
                                      "-ac", "1", "-ar", str(sr), "-"],
                                     capture_output=True, check=True).stdout, np.float32)
    al = alignment(raw, body, voice)
    want = {}  # gap (t0, t1) -> seconds of silence to insert there
    gaps = sentence_gaps(al)
    add = voice.get("sentence_gap_add", 0.0)
    if "sentence_gap_median" in voice and gaps:
        # Lift this take's median sentence-end gap to the target, keeping its variation.
        target = voice["sentence_gap_median"] * voice["speed"]  # in the take's own time
        add = max(0.0, target - float(np.median([b - a for a, b in gaps])))
    for gap in gaps:
        want[gap] = add
    _, pauses = split(body, voice)
    for idx, sec in pauses:  # pause lengths are meant after the speed-up
        want[gap_around(al, idx)] = sec * voice["speed"]
    cuts = []
    for (t0, t1), sec in sorted(want.items()):
        if sec <= 0:
            continue
        lo, hi = int(t0 * sr), int(t1 * sr)
        if hi - lo > 441:  # quietest 10 ms window inside the gap
            env = np.convolve(x[lo:hi] ** 2, np.ones(441), mode="valid")
            at = lo + int(np.argmin(env)) + 220
        else:
            at = (lo + hi) // 2
        cuts.append((at, sec))
    parts, prev = [], 0
    for at, sec in cuts:
        parts += [x[prev:at], np.zeros(int(sec * sr), np.float32)]
        prev = at
    parts.append(x[prev:])
    out = raw.replace(".mp3", ".paced.wav")
    subprocess.run([FFMPEG, "-loglevel", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", "1",
                    "-i", "-", out], input=np.concatenate(parts).tobytes(), check=True)
    return out, [(at / sr, sec) for at, sec in cuts]


def words(al: dict, voice: dict, cuts: list[tuple[float, float]]) -> list[dict]:
    """Words of the spoken text with start/end times in the final clip. A respelled word
    is written back in the script's spelling (only its normalized form matters to the
    anchors, so "Rag-oo's" comes back as "Ragus")."""
    back = {_norm(rep): word for word, rep in voice["respell"].items()}
    chars, starts, ends = al["chars"], al["starts"], al["ends"]
    # A silence inserted exactly at a word's end (a pause closing the scene) comes after it.
    shift = lambda t, end=False: (t + sum(sec for at, sec in cuts if (at < t if end else at <= t))
                                  ) / voice["speed"] + 1.0
    out = []
    for m in re.finditer(r"\S+", "".join(chars)):
        w, n = m.group(), _norm(m.group())
        for rep, word in back.items():
            if n in (rep, rep + "s"):
                w = word.capitalize() + n[len(rep):] if m.group()[0].isupper() else word + n[len(rep):]
        out.append({"w": w, "s": round(shift(starts[m.start()]), 3),
                    "e": round(shift(ends[m.end() - 1], end=True), 3)})
    return out


def _norm(w: str) -> str:
    return re.sub(r"[^a-z0-9]", "", w.lower())


def save_words(voice: dict, sid: str, ws: list[dict]) -> None:
    path = f"{HERE}/{voice['dir']}/words.json"
    data = json.load(open(path)) if os.path.exists(path) else {}
    data[sid] = ws
    # One line per scene: compact, and a retake only changes its own line in a diff.
    rows = [f"{json.dumps(sid)}: {json.dumps(ws, separators=(',', ':'))}"
            for sid, ws in sorted(data.items(), key=lambda kv: [int(x) for x in kv[0].split(".")])]
    open(path, "w").write("{\n" + ",\n".join(rows) + "\n}\n")


def finalize(voice: dict, sid: str, body: str) -> None:
    raw, out = paths(voice, sid)
    src, cuts = raw, []
    if voice.get("sentence_gap_add") or voice["pause_mode"] == "silence":
        src, cuts = insert_silences(raw, body, voice)
    tempo = f"atempo={voice['speed']}," if voice["speed"] != 1.0 else ""
    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error", "-i", src,
         "-filter:a", f"{tempo}adelay=1000|1000", "-b:a", "160k", out],
        check=True, capture_output=True,  # mp3 muxer spams harmless dts warnings
    )
    if src != raw:
        os.remove(src)
    if os.path.exists(raw.replace(".mp3", ".align.json")):
        save_words(voice, sid, words(alignment(raw, body, voice), voice, cuts))


def main() -> None:
    args = sys.argv[1:]
    name = args[args.index("--voice") + 1] if "--voice" in args else "brian"
    voice = VOICES[name]
    args = [a for a in args if a not in ("--voice", name)]
    dry = "--dry-run" in args
    scenes = [(sid, normalize(b, voice)) for sid, b in parse_scenes(f"{HERE}/NARRATION.md")]
    if "--finalize-only" in args:  # re-time existing raw clips, no API calls
        for sid, body in scenes:
            if os.path.exists(paths(voice, sid)[0]):
                finalize(voice, sid, body)
        print(f"finalized {name} at {voice['speed']}")
        return
    only = {a for a in args if not a.startswith("--")}
    todo = [s for s in scenes if not only or s[0] in only]
    print(f"{name}: {len(todo)} scenes, {sum(len(split(b, voice)[0]) for _, b in todo)} chars")
    if dry:
        for sid, b in todo:
            text, pauses = split(b, voice)
            print(f"--- {sid} --- ({len(pauses)} pauses inserted in post)\n{text}\n")
        return

    from elevenlabs.client import ElevenLabs

    for sub in ("raw", "final"):
        os.makedirs(f"{HERE}/{voice['dir']}/{sub}", exist_ok=True)
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    index = {sid: i for i, (sid, _) in enumerate(scenes)}
    for sid, body in todo:
        i = index[sid]
        prev_tail = spoken(scenes[i - 1][1], voice)[-280:] if i > 0 else None
        next_head = spoken(scenes[i + 1][1], voice)[:280] if i + 1 < len(scenes) else None
        text, _ = split(body, voice)
        # The timestamped call returns character timings for exactly the text we sent.
        r = client.text_to_speech.convert_with_timestamps(
            voice_id=voice["voice_id"],
            text=text,
            model_id=voice.get("model", MODEL_ID),
            output_format="mp3_44100_128",
            voice_settings=voice["settings"],
            **({"previous_text": prev_tail, "next_text": next_head}
               if voice.get("context", True) else {}),
        )
        raw = paths(voice, sid)[0]
        with open(raw, "wb") as f:
            f.write(base64.b64decode(r.audio_base_64))
        al = r.alignment
        if "".join(al.characters) != text:  # pause positions index into `text`
            print(f"scene {sid}: alignment text differs from the text sent", flush=True)
        save_alignment(raw, al.characters, al.character_start_times_seconds,
                       al.character_end_times_seconds)
        finalize(voice, sid, body)
        print(f"scene {sid}: {len(text)} chars", flush=True)

    sub = client.user.subscription.get()
    print(f"account usage: {sub.character_count} / {sub.character_limit}")


if __name__ == "__main__":
    main()

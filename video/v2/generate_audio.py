#!/usr/bin/env python3
"""Generate per-scene narration for v2 from NARRATION.md with ElevenLabs.

Raw clips -> audio/raw/scene-X.Y.mp3 (one per scene, so a retake costs one scene).
Final clips -> audio/final/scene-X.Y.mp3 (1.08x speed + 1 s lead-in pad, as in v1).

    .venv/bin/python generate_audio.py            # all scenes
    .venv/bin/python generate_audio.py 2.3 5.4    # retakes
    .venv/bin/python generate_audio.py --dry-run  # print normalized text + char count
    .venv/bin/python generate_audio.py --finalize-only  # redo speed/pad from raw, no credits
"""

import os
import re
import subprocess
import sys

from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv("/home/alex/work/tachyon_wt1/.env")

VOICE_ID = "nPczCjzI2devNBz1zQrb"  # Brian (v1 voice)
MODEL_ID = "eleven_multilingual_v2"
VOICE_SETTINGS = {
    "stability": 0.38,
    "similarity_boost": 0.80,
    "style": 0.45,
    "use_speaker_boost": True,
}
PAUSE_TAG = '<break time="0.6s" />'
SPEED = 1.145  # 1.08 (v1) x 1.06 (Alex, 2026-10-04: slightly brisker)
FFMPEG = "/home/alex/work/tachyon_wt1/video/bin/ffmpeg"

# Pronunciation respellings, chosen by Alex from audio/samples/.
RESPELL = [
    (r"\btachygram(s?)\b", r"TACHYGRAM\1"),
    (r"\btachyon\b", "TACHYON"),
    (r"\bpsi\b", "PSI"),
    (r"\bragu\b", "RAGU"),
]
TACHYON = "Tackeon"  # Sean/Alex 2026-10-05 (sample r3_t1); was "Tackion"
TACHYGRAM = "takkigram"  # sample g3
PSI = "psy"  # sample 3
RAGU = "Rah-goo"  # like the sauce (sample r3_t2), 2026-10-05


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


def normalize(body: str) -> str:
    for pat, rep in RESPELL:
        body = re.sub(pat, rep, body, flags=re.IGNORECASE)
    body = body.replace("TACHYGRAM", TACHYGRAM).replace("TACHYON", TACHYON).replace("PSI", PSI).replace("RAGU", RAGU)
    body = re.sub(r"⟨pause(?::[^⟩]*)?⟩", PAUSE_TAG, body).replace("*", "").replace("`", "")
    paras = [re.sub(r"\s+", " ", p).strip() for p in body.split("\n\n")]
    return "\n\n".join(p for p in paras if p)


def finalize(sid: str) -> None:
    raw = f"{HERE}/audio/raw/scene-{sid}.mp3"
    out = f"{HERE}/audio/final/scene-{sid}.mp3"
    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error", "-i", raw,
         "-filter:a", f"atempo={SPEED},adelay=1000|1000", "-b:a", "160k", out],
        check=True, capture_output=True,  # mp3 muxer spams harmless dts warnings
    )


def main() -> None:
    args = sys.argv[1:]
    dry = "--dry-run" in args
    if "--finalize-only" in args:  # re-time existing raw clips, no API calls
        for sid, _ in parse_scenes(f"{HERE}/NARRATION.md"):
            finalize(sid)
        print("finalized all scenes at", SPEED)
        return
    only = {a for a in args if not a.startswith("--")}
    scenes = [(sid, normalize(b)) for sid, b in parse_scenes(f"{HERE}/NARRATION.md")]
    todo = [s for s in scenes if not only or s[0] in only]
    print(f"{len(todo)} scenes, {sum(len(b) for _, b in todo)} chars")
    if dry:
        for sid, b in todo:
            print(f"--- {sid} ---\n{b}\n")
        return

    from elevenlabs.client import ElevenLabs

    os.makedirs(f"{HERE}/audio/raw", exist_ok=True)
    os.makedirs(f"{HERE}/audio/final", exist_ok=True)
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    index = {sid: i for i, (sid, _) in enumerate(scenes)}
    for sid, body in todo:
        i = index[sid]
        prev_tail = scenes[i - 1][1][-280:] if i > 0 else None
        next_head = scenes[i + 1][1][:280] if i + 1 < len(scenes) else None
        audio = client.text_to_speech.convert(
            voice_id=VOICE_ID,
            text=body,
            model_id=MODEL_ID,
            output_format="mp3_44100_128",
            voice_settings=VOICE_SETTINGS,
            previous_text=prev_tail,
            next_text=next_head,
        )
        with open(f"{HERE}/audio/raw/scene-{sid}.mp3", "wb") as f:
            for chunk in audio:
                f.write(chunk)
        finalize(sid)
        print(f"scene {sid}: {len(body)} chars", flush=True)

    sub = client.user.subscription.get()
    print(f"account usage: {sub.character_count} / {sub.character_limit}")


if __name__ == "__main__":
    main()

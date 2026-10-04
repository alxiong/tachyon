#!/usr/bin/env python3
"""Generate per-scene narration audio from NARRATION.md with ElevenLabs.

Voice: Brian (deep, resonant), tuned for a sense of discovery:
lower stability -> more dynamic intonation; style boost -> more expressive.
One MP3 per scene in audio/, so retakes only cost one scene.
"""

import os
import re
import sys

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv("/home/alex/work/tachyon_wt1/.env")

VOICE_ID = "nPczCjzI2devNBz1zQrb"  # Brian
MODEL_ID = "eleven_multilingual_v2"
VOICE_SETTINGS = {
    "stability": 0.38,         # lower = livelier, more discovery
    "similarity_boost": 0.80,
    "style": 0.45,             # expressive emphasis
    "use_speaker_boost": True,
}
OUT_DIR = "audio"
PAUSE_TAG = '<break time="0.6s" />'


def parse_scenes(path: str) -> list[tuple[str, str]]:
    text = open(path).read()
    # Drop the footer (Totals/Pacing/On-screen notes) after the last ---
    text = re.split(r"\n\*\*Totals:\*\*", text)[0]
    scenes: list[tuple[str, str]] = []
    cur_id, buf = None, []

    def flush():
        if cur_id is not None:
            body = "\n".join(buf).strip()
            if body:
                scenes.append((cur_id, body))

    for line in text.splitlines():
        m = re.match(r"### (\d+\.\d+) —", line)
        if m:
            flush()
            cur_id, buf = m.group(1), []
            continue
        if line.startswith("## ") or line.strip() == "---":
            continue
        if cur_id is not None:
            buf.append(line)
    flush()
    return scenes


def normalize(body: str) -> str:
    body = body.replace("⟨pause⟩", PAUSE_TAG)
    # Pronunciation respellings (ElevenLabs reads "Tachyon" as ta-CHI-on):
    body = re.sub(r"\btachyon\b", "Tack-ee-on", body, flags=re.IGNORECASE)
    body = re.sub(r"\btachygram(s?)\b", r"tack-ee-gram\1", body, flags=re.IGNORECASE)
    body = body.replace("*", "").replace("`", "")
    # collapse whitespace but keep paragraph breaks (natural pauses)
    paras = [re.sub(r"\s+", " ", p).strip() for p in body.split("\n\n")]
    return "\n\n".join(p for p in paras if p)


def main() -> None:
    only = set(sys.argv[1:])  # optional scene ids for retakes, e.g. 2.3 5.4
    os.makedirs(OUT_DIR, exist_ok=True)
    scenes = [(sid, normalize(b)) for sid, b in parse_scenes("NARRATION.md")]
    total_chars = sum(len(b) for _, b in scenes)
    print(f"{len(scenes)} scenes, {total_chars} chars total")

    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    for i, (sid, body) in enumerate(scenes):
        if only and sid not in only:
            continue
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
        path = f"{OUT_DIR}/scene-{sid}.mp3"
        with open(path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        print(f"wrote {path} ({len(body)} chars)")

    sub = client.user.subscription.get()
    print(f"account usage: {sub.character_count} / {sub.character_limit}")


if __name__ == "__main__":
    main()

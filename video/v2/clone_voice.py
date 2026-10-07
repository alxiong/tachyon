#!/usr/bin/env python3
"""Create (or recreate) Sean's instant voice clone in ElevenLabs from audio/clone/.

    .venv/bin/python clone_voice.py            # create, print the new voice_id
    .venv/bin/python clone_voice.py --replace  # delete the previous clone (by name) first

Run build_clone_set.py first. IVC caps the number of sample files, so the 6-30 s clips
are merged in manifest order (chapter 0 first) into files of at most ~MERGE_S seconds,
with a short silence between clips.
"""
import json, os, subprocess, sys
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
FFMPEG = "/home/alex/work/tachyon_wt1/video/bin/ffmpeg"
CLONE = f"{HERE}/audio/clone"
NAME = "Sean (Tachyon narration)"
MERGE_S = 60.0
GAP_S = 0.4


def merged_files():
    chosen = json.load(open(f"{CLONE}/manifest.json"))["chosen"]
    groups, cur, dur = [], [], 0.0
    for c in chosen:
        if cur and dur + c["dur"] > MERGE_S:
            groups.append(cur)
            cur, dur = [], 0.0
        cur.append(c["file"])
        dur += c["dur"] + GAP_S
    groups.append(cur)
    os.makedirs(f"{CLONE}/upload", exist_ok=True)
    out = []
    for i, g in enumerate(groups, 1):
        path = f"{CLONE}/upload/sean_part{i:02d}.mp3"
        inputs, chain = [], ""
        for j, f in enumerate(g):
            inputs += ["-i", f"{CLONE}/{f}"]
            chain += f"[{j}]aresample=44100,aformat=channel_layouts=mono,apad=pad_dur={GAP_S}[a{j}];"
        chain += "".join(f"[a{j}]" for j in range(len(g))) + f"concat=n={len(g)}:v=0:a=1"
        subprocess.run([FFMPEG, "-loglevel", "error", "-y", *inputs, "-filter_complex", chain,
                        "-b:a", "192k", path], check=True)
        out.append(path)
    return out


def main():
    load_dotenv("/home/alex/work/tachyon_wt1/.env")
    from elevenlabs.client import ElevenLabs
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    if "--replace" in sys.argv:
        for v in client.voices.search(search=NAME).voices:
            if v.name == NAME:
                client.voices.delete(v.voice_id)
                print("deleted", v.voice_id)
    files = merged_files()
    print(len(files), "sample files")
    handles = [open(f, "rb") for f in files]
    try:
        voice = client.voices.ivc.create(
            name=NAME,
            files=handles,
            remove_background_noise=False,  # clips are already clean; denoising dulls timbre
            # The SDK json-encodes labels itself, and omitting them sends an invalid value.
            labels={"language": "en", "gender": "male"},
            description="Sean Bowe, cloned from his own chapter 0 read and his ZconVI talk "
                        "(pitch/EQ-matched to the read). For the Tachyon explainer only.",
        )
    finally:
        for h in handles:
            h.close()
    print("voice_id", voice.voice_id)


if __name__ == "__main__":
    main()

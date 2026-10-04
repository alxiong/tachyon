#!/usr/bin/env python3
"""Force-align final narration clips: word timestamps -> audio/words.json.

Decodes with ffmpeg to f32 PCM (faster-whisper's own pyav decode clashes with av 19),
transcribes with base.en (int8, CPU) and word_timestamps=True.
    .venv/bin/python align.py            # all clips
    .venv/bin/python align.py 2.3 5.4    # refresh some (merged into words.json)
"""
import glob, json, os, re, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

HERE = os.path.dirname(os.path.abspath(__file__))
FFMPEG = "/home/alex/work/tachyon_wt1/video/bin/ffmpeg"
OUT = f"{HERE}/audio/words.json"


def load(path: str) -> np.ndarray:
    raw = subprocess.run([FFMPEG, "-loglevel", "error", "-i", path, "-f", "f32le",
                          "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def main() -> None:
    only = set(sys.argv[1:])
    data = json.load(open(OUT)) if os.path.exists(OUT) else {}
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    for path in sorted(glob.glob(f"{HERE}/audio/final/scene-*.mp3")):
        sid = re.search(r"scene-(\d+\.\d+)", path).group(1)
        if only and sid not in only:
            continue
        segs, _ = model.transcribe(load(path), word_timestamps=True, language="en")
        words = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)}
                 for seg in segs for w in seg.words]
        data[sid] = words
        print(sid, len(words), "words", flush=True)
    json.dump(data, open(OUT, "w"), indent=0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Mux each scene of chapter N with its narration and concat -> v2/video/chN.mp4.

Scene cuts: where a scene opens on exactly the previous scene's last frame (a chained
seam, built with a final-state builder), the cut is left alone. Every other cut dips
through black: the outgoing scene fades out over the last FADE seconds of its visual
tail (after the narration has ended) and the incoming one fades in over the first FADE
seconds of its 1 s lead-in (before the narration starts), so no word is ever faded and
the audio timing is untouched. The chapter's last scene also holds its final frame for
an extra TAIL seconds while it fades, and the next chapter fades in from black.

    .venv/bin/python scenes/build_chapter.py 3        # one chapter
    .venv/bin/python scenes/build_chapter.py --seams  # print every seam's frame difference
"""
import glob, os, re, subprocess, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FF = "/home/alex/work/tachyon_wt1/video/bin/ffmpeg"
AUDIO = os.path.join(ROOT, os.environ.get("NARRATION_AUDIO", "audio/sts"), "final")
FADE = float(os.environ.get("FADE", 0.4))
TAIL = float(os.environ.get("TAIL", 0.5))
CHAINED = 0.01  # mean |pixel difference| (0..1) below which a seam counts as chained
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30",
       "-video_track_timescale", "15360"]


def scenes() -> list[str]:
    sids = [re.search(r"scene-(\d+\.\d+)", p).group(1) for p in glob.glob(f"{AUDIO}/scene-*.mp3")]
    return sorted(sids, key=lambda s: [int(x) for x in s.split(".")])


def video(sid: str) -> str:
    return f"{ROOT}/renders/Scene{sid.replace('.', '')}.mp4"


def duration(path: str) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", path], capture_output=True, text=True).stdout)


def frame(path: str, last: bool) -> np.ndarray:
    pos = ["-sseof", "-0.05"] if last else ["-ss", "0"]
    raw = subprocess.run([FF, "-loglevel", "error", *pos, "-i", path, "-frames:v", "1",
                          "-vf", "scale=480:270", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).astype(np.float32) / 255


def seam(a: str, b: str) -> float:
    """Mean difference between a's last frame and b's first frame."""
    return float(np.abs(frame(video(a), True) - frame(video(b), False)).mean())


def build(n: str) -> None:
    allsids = scenes()
    sids = [s for s in allsids if s.split(".")[0] == n]
    tmp = tempfile.mkdtemp()
    parts = []
    for i, sid in enumerate(sids):
        v, a = video(sid), f"{AUDIO}/scene-{sid}.mp3"
        h = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=height", "-of", "csv=p=0", v], capture_output=True, text=True).stdout
        if h.strip() != "1080":
            sys.exit(f"refusing: {v} is {h.strip()}p")
        last = i == len(sids) - 1
        prev = allsids[allsids.index(sid) - 1] if allsids.index(sid) > 0 else None
        # A chapter opens from black (the previous one faded out); inside a chapter, only
        # unchained seams dip.
        fade_in = i == 0 or seam(prev, sid) > CHAINED
        fade_out = last or seam(sid, sids[i + 1]) > CHAINED
        d = duration(v)
        vf = []
        if last:
            vf.append(f"tpad=stop_mode=clone:stop_duration={TAIL}")
        if fade_in:
            vf.append(f"fade=t=in:st=0:d={FADE}")
        if last:  # the held tail is the fade
            vf.append(f"fade=t=out:st={d}:d={TAIL}")
        elif fade_out:
            vf.append(f"fade=t=out:st={d - FADE}:d={FADE}")
        out = f"{tmp}/{sid}.mp4"
        vargs = ["-vf", ",".join(vf), *ENC] if vf else ["-c:v", "copy"]
        subprocess.run([FF, "-y", "-loglevel", "error", "-i", v, "-i", a, *vargs,
                        "-af", "apad", "-shortest", "-c:a", "aac", "-b:a", "160k", out], check=True)
        parts.append(out)
        print(f"  {sid}: fade in {'yes' if fade_in else 'no (chained)'}, "
              f"fade out {'yes' if fade_out else 'no (chained)'}")
    lst = f"{tmp}/list.txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    os.makedirs(f"{ROOT}/video", exist_ok=True)
    dst = f"{ROOT}/video/ch{n}.mp4"
    subprocess.run([FF, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", dst], check=True)
    print(f"video/ch{n}.mp4 {duration(dst):.1f}s")


if __name__ == "__main__":
    if sys.argv[1] == "--seams":
        s = scenes()
        for a, b in zip(s, s[1:]):
            print(f"{a} -> {b}: {seam(a, b):.4f}")
    else:
        for n in sys.argv[1:]:
            build(n)

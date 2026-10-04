"""Tachyon video design system: brand palette + small helpers.

Role mapping: wallet = GOLD, OSS = CYAN, shared evidence = STAR, hot = FLARE.
"""

import math
import os

from manimlib import *

# Brand palette (tachyon-website _variables.scss)
VOID = "#020204"
GOLD = "#D4A017"
AMBER = "#E8820C"
FLARE = "#FF6B00"
CYAN = "#4A9EA0"
STAR = "#FFFAF0"
TXT = "#c8c4bf"
MUT = "#9a958a"
DIM = "#77726a"

FONT = "New Computer Modern"  # the project's ONLY face; all text goes through typst, see label()
LOGO_PNG = "/home/alex/work/tachyon_wt1/video/assets/brand/tachyon-logo-1000.png"


def _esc_typst(s):
    """Escape typst markup specials so prose renders verbatim."""
    out = []
    for ch in s:
        if ch in "\\#$[]*_`@<>~":
            out.append("\\" + ch)
        elif ch == "\n":
            out.append(" \\ ")
        else:
            out.append(ch)
    body = "".join(out)
    # a leading "1. " / "+ " / "- " / "/ " would start a typst list or enum item
    body = _re.sub(r"^(\s*)(\d+)\.", r"\1\2\\.", body)
    body = _re.sub(r"^(\s*)([+\-/=])(\s)", r"\1\\\2\3", body)
    return body


def label(s, size=34, color=TXT, weight="NORMAL"):
    """Prose label in New Computer Modern (the project's single face), via typst."""
    body = _esc_typst(s)
    if str(weight).upper() == "BOLD":
        body = f'#text(weight: "bold")[{body}]'
    return mtex(body, size=size, color=color, math=False)


def heading(s, size=52, color=STAR):
    return label(s, size=size, color=color, weight="BOLD")


def sans_label(s, size=34, color=TXT, weight="NORMAL"):
    """Deprecated alias of label(). The project has ONE face (New Computer Modern, via
    typst); a pango Text here would render a second one, so this no longer does that."""
    return label(s, size=size, color=color, weight=weight)


def panel(width, height, color=GOLD, fill_opacity=0.05, stroke_opacity=0.8,
          stroke_width=2.4, radius=0.18):
    p = RoundedRectangle(width=width, height=height, corner_radius=radius)
    p.set_fill(color, fill_opacity)
    p.set_stroke(color, stroke_width, stroke_opacity)
    return p


def chip(s, color=GOLD, size=30, pad=0.28):
    t = label(s, size=size, color=color)
    box = RoundedRectangle(
        width=t.get_width() + 2 * pad,
        height=t.get_height() + 1.6 * pad,
        corner_radius=0.12,
    )
    box.set_fill(color, 0.08)
    box.set_stroke(color, 2, 0.6)
    box.move_to(t)
    return VGroup(box, t)


class TimedScene(Scene):
    """Scene with a hard target duration, padded via self.pad_to(t).

    Every pad_to() also runs the layout linter (see lint_layout) on the current
    frame and appends findings to anim/lint/<SceneName>.txt. Read that file after
    every render; an empty file is the goal. Set LAYOUT_LINT=0 to disable.
    """

    def pad_to(self, t: float):
        if os.environ.get("LAYOUT_LINT", "1") != "0":
            lint_layout(self)
            if self.time > t + 0.25:
                # pad_to can only wait: the beat that should start at t starts late
                self._lint = getattr(self, "_lint", {})
                self._lint[("late", round(t, 2))] = (
                    f"[t={self.time:6.1f}] late     beat anchored at {t:.2f}s starts "
                    f"{self.time - t:.2f}s late (trim run_times before it)")
        if t > self.time:
            self.wait(t - self.time)

    def tear_down(self):
        if os.environ.get("LAYOUT_LINT", "1") != "0":
            lint_layout(self)
            _lint_flush(self)
        super().tear_down()


def proof_token(radius=0.16):
    """A wallet's proof: gold core + amber ring."""
    core = Dot(ORIGIN, radius=radius).set_fill(GOLD, 1.0)
    ring = Circle(radius=radius * 1.8)
    ring.set_stroke(AMBER, 2.5, 0.9)
    ring.set_fill(opacity=0)
    return VGroup(ring, core)


def checkmark(size=0.5, color=GOLD):
    a = Line(ORIGIN, 0.35 * size * (RIGHT + DOWN), stroke_width=5, stroke_color=color)
    b = Line(a.get_end(), a.get_end() + size * (RIGHT + UP), stroke_width=5, stroke_color=color)
    return VGroup(a, b)


def add_shimmer(cells, amp=0.13, speed=1.6):
    """Gentle per-cell opacity breathing, so the frame never goes dead."""
    for i, sq in enumerate(cells):
        sq.shimmer_t = 0.0
        sq.shimmer_base = sq.get_fill_opacity()

        def up(m, dt, ph=0.77 * i):
            m.shimmer_t += dt
            m.set_fill(opacity=m.shimmer_base * (1 + amp * math.sin(speed * m.shimmer_t + ph)))
        sq.add_updater(up)


def clear_shimmer(cells):
    for sq in cells:
        sq.clear_updaters()


# ---- data-driven narration anchors -----------------------------------------
import json as _json
import re as _re

_WORDS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "words.json")
try:
    WORDS = _json.load(open(_WORDS_PATH))
except FileNotFoundError:
    WORDS = {}


def _norm(w):
    return _re.sub(r"[^a-z0-9]", "", w.lower())


def anchor(sid: str, phrase: str, occ: int = 1) -> float:
    """Start time of the occ-th occurrence of `phrase` in scene `sid`'s narration."""
    words = WORDS[sid]
    target = [_norm(x) for x in phrase.split()]
    seq = [_norm(w) for _, w in words]
    hits = 0
    for i in range(len(seq) - len(target) + 1):
        if seq[i:i + len(target)] == target:
            hits += 1
            if hits == occ:
                return words[i][0]
    raise ValueError(f"anchor not found in {sid}: {phrase!r}")


def scene_T(sid: str, tail: float = 0.8) -> float:
    """Target scene duration: final audio length + a short visual tail."""
    import subprocess as _sp
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "audio", "final", f"scene-{sid}.mp3")
    out = _sp.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                   "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return float(out.strip()) + tail


def anchor_any(sid: str, phrases, occ: int = 1) -> float:
    """First phrase from `phrases` that matches; tolerant of transcription quirks."""
    for p in phrases:
        try:
            return anchor(sid, p, occ)
        except (ValueError, KeyError):
            continue
    raise ValueError(f"no anchor matched in {sid}: {phrases}")


def key_chip(s, color=MUT, size=26, pad=0.16):
    t = label(s, size=size, color=color)
    box = RoundedRectangle(width=t.get_width() + 2 * pad,
                           height=t.get_height() + 2.2 * pad, corner_radius=0.1)
    box.set_fill(color, 0.07)
    box.set_stroke(color, 1.8, 0.7)
    box.move_to(t)
    return VGroup(box, t)


def bead(color=FLARE, r=0.09, opacity=0.95):
    return Dot(ORIGIN, radius=r).set_fill(color, opacity)


def factor_tile(s="", color=GOLD, w=0.62, h=0.78):
    box = RoundedRectangle(width=w, height=h, corner_radius=0.08)
    box.set_fill(color, 0.1)
    box.set_stroke(color, 1.8, 0.8)
    if s:
        t = label(s, size=20, color=color).move_to(box)
        return VGroup(box, t)
    return VGroup(box)


def sponge_icon(w=1.5, h=0.9, color=AMBER):
    body = RoundedRectangle(width=w, height=h, corner_radius=0.12)
    body.set_fill(color, 0.08)
    body.set_stroke(color, 2.0, 0.85)
    waves = VGroup(*[
        Line(body.get_left() + RIGHT * 0.25 + UP * dy,
             body.get_right() + LEFT * 0.25 + UP * dy,
             stroke_width=1.6, stroke_color=color, stroke_opacity=0.6)
        for dy in (-0.2, 0.0, 0.2)
    ])
    tag = label("Poseidon", size=18, color=color).next_to(body, DOWN, buff=0.1)
    return VGroup(body, waves, tag)


def cross_out(mob, color=FLARE):
    return Line(mob.get_corner(DL) + 0.08 * DL, mob.get_corner(UR) + 0.08 * UR,
                stroke_color=color, stroke_width=4)


def block(w=0.56, h=0.42):
    b = RoundedRectangle(width=w, height=h, corner_radius=0.07)
    b.set_fill(STAR, 0.08)
    b.set_stroke(STAR, 1.8, 0.75)
    return b


def chain_link(a, b):
    return Line(a.get_right(), b.get_left(), buff=0.03,
                stroke_width=3, stroke_color=DIM, stroke_opacity=0.9)


def proof_card(scale=1.0):
    c = panel(0.95 * scale, 0.65 * scale, color=GOLD, fill_opacity=0.08)
    ck = checkmark(0.26 * scale).move_to(c.get_center())
    return VGroup(c, ck)


def envelope(w=1.6, h=1.0, color=CYAN, tex_label=r"f(X)"):
    """Classic sealed-envelope icon with a Tex label: a committed polynomial."""
    body = RoundedRectangle(width=w, height=h, corner_radius=0.04)
    body.set_fill(color, 0.10)
    body.set_stroke(color, 2.4, 0.95)
    apex = body.get_center() + DOWN * 0.04 * h
    flap = VGroup(
        Line(body.get_corner(UL), apex, stroke_width=2.0, stroke_color=color,
             stroke_opacity=0.85),
        Line(body.get_corner(UR), apex, stroke_width=2.0, stroke_color=color,
             stroke_opacity=0.85),
    )
    tag = mtex(tex_label, size=int(24 * h), color=color)
    tag.move_to(body.get_center() + LEFT * 0.22 * w + DOWN * 0.26 * h)
    return VGroup(body, flap, tag)


def bracket(mob, color=STAR, buff=0.12, tick=0.14, below=False):
    """LaTeX-free horizontal brace substitute: bar + end ticks + center nub."""
    x0, x1 = mob.get_left()[0], mob.get_right()[0]
    if below:
        y = mob.get_bottom()[1] - buff
        tdir, ndir = 1, -1
    else:
        y = mob.get_top()[1] + buff
        tdir, ndir = -1, 1
    sw = dict(stroke_width=2.5, stroke_color=color)
    main = Line(np.array([x0, y, 0]), np.array([x1, y, 0]), **sw)
    t1 = Line(np.array([x0, y, 0]), np.array([x0, y + tdir * tick, 0]), **sw)
    t2 = Line(np.array([x1, y, 0]), np.array([x1, y + tdir * tick, 0]), **sw)
    nub = Line(np.array([(x0 + x1) / 2, y, 0]),
               np.array([(x0 + x1) / 2, y + ndir * tick, 0]), **sw)
    return VGroup(main, t1, t2, nub)


# ---- typst-backed math rendering (no texlive needed) ------------------------
import hashlib as _hashlib
import subprocess as _sp

_TYPST_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "typst_cache")
_PT2UNIT = 8.0 / 810.0  # 1080p frame: 8 scene units = 810pt page height


PROSE_FONT = "New Computer Modern"  # the one face; math uses NCM Math automatically
# Symbols NCM's text face lacks (⇒ ∝ ∪ ≤ ⊆ ⌐ ✓ ✗) live in its companion MATH face,
# drawn to match Computer Modern exactly — take them from there before any sans.
# DejaVu is last-resort only; if it ever shows up on screen, something needs fixing.
FONT_STACK = (PROSE_FONT, "New Computer Modern Math", "DejaVu Sans")


def _typst_svg(body: str) -> tuple[str, float]:
    """Compile a typst snippet to SVG (cached). Returns (svg_path, height_pt).

    typst only *warns* (exit 0) when a font family is missing and silently
    substitutes another, so a typo in PROSE_FONT would render the whole video in
    a fallback face unnoticed. Treat that warning as fatal.
    """
    stack = ", ".join(f'"{f}"' for f in (PROSE_FONT,) + FONT_STACK[1:])
    src = ('#set page(width: auto, height: auto, margin: 2pt, fill: none)\n'
           f'#set text(font: ({stack}), '
           'size: 48pt, fill: rgb("#ffffff"))\n' + body + '\n')
    h = _hashlib.md5(src.encode()).hexdigest()
    os.makedirs(_TYPST_CACHE, exist_ok=True)
    svg = os.path.join(_TYPST_CACHE, h + ".svg")
    if not os.path.exists(svg):
        typ = os.path.join(_TYPST_CACHE, h + ".typ")
        with open(typ, "w") as f:
            f.write(src)
        r = _sp.run(["typst", "compile", typ, svg], check=True, capture_output=True,
                    text=True)
        if "unknown font family" in (r.stderr or ""):
            raise RuntimeError(
                f"typst could not find a font and silently substituted one:\n"
                f"{r.stderr.strip()}\nInstall it or fix PROSE_FONT in style.py.")
    hdr = open(svg).read(300)
    hpt = float(_re.search(r'height="([0-9.]+)pt"', hdr).group(1))
    return svg, hpt


class _RawSVG(SVGMobject):
    """SVGMobject that keeps the file's own units (no bbox normalization).

    manimgl normalizes to the INK bounding box (height=2), which makes glyph size
    depend on ascenders/descenders — 'selective disclosure' would render ~25%
    larger than 'proving ≠ authorizing' at the same requested size. Keeping raw
    units (typst svg user units == pt) lets us scale uniformly by pt → scene units.
    """
    height = None


def mtex(tex, size=36, color=STAR, math=True):
    """Math (typst syntax) rendered through typst, loaded at true metrics."""
    body = f"$ {tex} $" if math else tex
    svg, hpt = _typst_svg(body)
    m = _RawSVG(svg)
    m.scale(_PT2UNIT * (size / 48.0))
    m.set_fill(color, 1.0)
    m.set_stroke(width=0)
    m.font_pt = size              # read by the layout linter (TimedScene.pad_to)
    m.base_h = max(m.get_height(), 1e-6)
    m.lint_text = tex[:40]
    return m


def itex(s, size=24, color=None):
    """Italic prose label in the serif face (zcash_keys.png side labels).

    Supports \\n for explicit line breaks (centered, like the png's side labels).
    """
    body = _esc_typst(s)
    if "\\ " in body:
        body = f"#align(center)[{body}]"
    return mtex(f"#emph[{body}]", size=size, color=(color or MUT), math=False)


def tex_chip(tex, color=GOLD, size=32, pad=0.2):
    t = mtex(tex, size=size, color=color)
    box = RoundedRectangle(width=t.get_width() + 2 * pad,
                           height=t.get_height() + 2.4 * pad, corner_radius=0.1)
    box.set_fill(color, 0.07)
    box.set_stroke(color, 1.8, 0.7)
    box.move_to(t)
    return VGroup(box, t)


# ---- zcash_keys.png palette (legacy key diagrams keep the canonical colors) --
PNG_SK = "#B9A5E8"      # spending key (lavender)
PNG_SPEND = "#E583DF"   # expanded spending key (magenta)
PNG_PROOF = "#F8837F"   # proof authorizing key (salmon)
PNG_FVK = "#FBA51F"     # full viewing key (orange)
PNG_IVK = "#FAF49B"     # incoming viewing key (pale yellow)
PNG_ADDR = "#7FD98C"    # shielded payment address (green)
PNG_OVK = "#CBA36B"     # outgoing viewing key (tan)
PNG_INK = "#141414"     # box borders + box text (dark, on light fills)
PNG_ARROW = "#C8C4BF"   # arrows, redrawn light for the dark background


def kbox(texs, fill, size=30, pad=0.22, gap=0.55):
    """A zcash_keys.png-style rounded box: light fill, dark border, dark Tex."""
    labels = VGroup(*[mtex(t, size=int(size * 1.5), color=PNG_INK) for t in texs])
    labels.arrange(RIGHT, buff=gap)
    box = RoundedRectangle(width=labels.get_width() + 2 * pad + 0.2,
                           height=max(labels.get_height() + 2.0 * pad, 0.52),
                           corner_radius=0.18)
    box.set_fill(fill, 1.0)
    box.set_stroke(PNG_INK, 2.0, 1.0)
    labels.move_to(box)
    return VGroup(box, labels)


def contour(mob=None, center=ORIGIN, w=1.0, h=1.0, color=GOLD, buff=0.16,
            wobble=0.055, seed=3, stroke_width=3.0):
    """Irregular hand-drawn loop around a mobject (or an explicit w×h at center).

    The canonical highlight for regions of a raster diagram — never dim the rest.
    """
    import random
    rng = random.Random(seed)
    if mob is not None:
        w = mob.get_width() + 2 * buff
        h = mob.get_height() + 2 * buff
        center = mob.get_center()
    p1, p2 = rng.uniform(0, TAU), rng.uniform(0, TAU)
    pts = []
    n = 28
    for i in range(n + 1):
        th = TAU * i / n
        r = 1.0 + wobble * math.sin(2 * th + p1) + wobble * 0.7 * math.sin(3 * th + p2)
        pts.append(np.array([0.5 * w * r * math.cos(th),
                             0.5 * h * r * math.sin(th), 0]))
    vm = VMobject()
    vm.set_points_smoothly(pts)
    vm.set_fill(opacity=0)
    vm.set_stroke(color, stroke_width, 0.95)
    vm.move_to(center)
    return vm


def dashed_box(mob=None, center=ORIGIN, w=1.0, h=1.0, color=GOLD, buff=0.1,
               dash=0.16, gap=0.1, stroke_width=2.6, radius=0.08):
    """Dashed rounded rectangle (manimgl has no DashedVMobject)."""
    if mob is not None:
        w = mob.get_width() + 2 * buff
        h = mob.get_height() + 2 * buff
        center = mob.get_center()
    rect = RoundedRectangle(width=w, height=h, corner_radius=min(radius, 0.3 * min(w, h)))
    rect.move_to(center)
    L = rect.get_arc_length()
    n = max(6, int(L / (dash + gap)))
    segs = VGroup()
    for i in range(n):
        a = i / n
        b = a + (dash / (dash + gap)) / n
        s = VMobject()
        k = 8
        s.set_points_smoothly([rect.point_from_proportion(a + (b - a) * j / k)
                               for j in range(k + 1)])
        s.set_fill(opacity=0)
        s.set_stroke(color, stroke_width, 0.95)
        segs.add(s)
    return segs


def karrow(a, b, star=False):
    """Thin arrow in the zcash_keys.png style (manim Arrow's quad shaft is too fat)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    v = b - a
    L = max(float(np.linalg.norm(v)), 1e-9)
    u = v / L
    tip_len = min(0.17, 0.45 * L)
    n = np.array([-u[1], u[0], 0.0])
    shaft = Line(a, b - u * tip_len * 0.8, stroke_width=2.2, stroke_color=PNG_ARROW)
    tip = Polygon(b, b - u * tip_len + n * 0.07, b - u * tip_len - n * 0.07)
    tip.set_fill(PNG_ARROW, 1.0)
    tip.set_stroke(width=0)
    g = VGroup(shaft, tip)
    if star:
        s = mtex("*", size=26, color=PNG_ARROW)
        s.move_to((a + b) / 2 + RIGHT * 0.18)
        g.add(s)
    return g


# ==== layout system (2026-10-04 presentation pass) ===========================
# The frame is 14.22 x 8 units. Every scene composes into three bands:
#
#   TITLE band   y in [ 3.0,  3.75]  scene_title(): the question this beat poses
#   STAGE        y in [-2.75, 2.85]  the diagram; fills the width it needs
#   CAPTION band y in [-3.75, -3.0]  caption(): one takeaway line, on its word
#
# Text sizes (pt at 1080p). Nothing a viewer must read goes below FS_MIN.
FS_TITLE = 46   # scene / beat titles
FS_HEAD = 38    # hero formulas, big callouts
FS_BODY = 32    # captions, bullets, main formulas
FS_LABEL = 28   # diagram labels, chip text
FS_SMALL = 24   # secondary annotations (sparingly)
FS_MIN = 22     # hard floor for anything meant to be read (linter enforces)

FRAME_X = FRAME_WIDTH / 2     # 7.11
FRAME_Y = FRAME_HEIGHT / 2    # 4.0
SAFE_X = 6.75                 # keep ink inside |x| <= SAFE_X
SAFE_Y = 3.7                  # ... and |y| <= SAFE_Y
TITLE_Y = 3.3
CAPTION_Y = -3.35
STAGE_TOP = 2.75
STAGE_BOTTOM = -2.75
STAGE_CENTER = np.array([0.0, (STAGE_TOP + STAGE_BOTTOM) / 2, 0.0])

# Common split: diagram on the left ~60%, argument text on the right ~40%.
DIAGRAM_REGION = (-6.6, 1.6, STAGE_BOTTOM, STAGE_TOP)   # (x0, x1, y0, y1)
NOTES_REGION = (2.1, 6.7, STAGE_BOTTOM, STAGE_TOP)
FULL_STAGE = (-6.6, 6.6, STAGE_BOTTOM, STAGE_TOP)

# Stroke weights: readable on a dark background at 1080p.
SW_THIN = 2.2
SW = 3.0
SW_BOLD = 4.5


def region_center(region):
    x0, x1, y0, y1 = region
    return np.array([(x0 + x1) / 2, (y0 + y1) / 2, 0.0])


def fit_in(mob, region=FULL_STAGE, max_scale=None, align=None):
    """Scale `mob` to fit inside `region` (x0, x1, y0, y1) and center it there.

    Shrinks if too big; grows up to `max_scale` (default: no growth) if small.
    `align` = LEFT/RIGHT/UP/DOWN pins that edge to the region's edge instead.
    """
    x0, x1, y0, y1 = region
    w, h = x1 - x0, y1 - y0
    s = min(w / max(mob.get_width(), 1e-6), h / max(mob.get_height(), 1e-6))
    s = min(s, 1.0 if max_scale is None else max_scale)
    mob.scale(s)
    mob.move_to(region_center(region))
    if align is not None:
        edge = region_center(region) + np.array([align[0] * w / 2, align[1] * h / 2, 0])
        mob.align_to(edge, align)
    return mob


def scene_title(s, color=STAR, size=FS_TITLE):
    """PPT-style title, top-center. Use for the question a beat poses."""
    return heading(s, size=size, color=color).move_to(UP * TITLE_Y)


def caption(s, color=TXT, size=FS_BODY):
    """One takeaway line in the caption band (bottom center)."""
    return label(s, size=size, color=color).move_to(UP * CAPTION_Y)


def rich(parts, size=FS_BODY, buff=0.14):
    """A line with per-run colors: rich([("one note,", TXT), ("many nullifiers", FLARE)]).

    Runs may be prose (str) or math: pass ("$psi$", GOLD) and it renders via typst
    inline math. Runs sit on a common BASELINE: each is compiled after a '|' strut
    (identical ink box for every run at one size); every run is shifted so its strut
    bottom sits at y=0, then the struts are discarded — so descenders ('p', 'y') and
    subscripts don't lift a run off the line. Returns VGroup of runs (animate per run).
    """
    out = VGroup()
    x = 0.0
    for text, color in parts:
        is_math = text.startswith("$") and text.endswith("$") and len(text) > 1
        body = "|" + (text if is_math else _esc_typst(text))
        m = mtex(body, size=size, color=color, math=False)
        strut = m.submobjects[0]
        m.remove(strut)
        m.shift(UP * (-strut.get_bottom()[1]))
        m.shift(RIGHT * (x - m.get_left()[0]))
        x = m.get_right()[0] + buff
        m.base_h = max(m.get_height(), 1e-6)
        m.lint_text = text[:40]
        out.add(m)
    out.center()
    return out


def bullets(items, size=FS_BODY, color=TXT, mark_color=GOLD, buff=0.32, width=None):
    """Left-aligned bullet list. items: str, (str, color), or a ready mobject.

    Returns VGroup of rows (each row = VGroup(mark, text)) so rows can be
    revealed one at a time on their spoken words: FadeIn(rows[i], shift=0.2*RIGHT).
    """
    rows = VGroup()
    for it in items:
        if isinstance(it, Mobject):
            t = it
        elif isinstance(it, tuple):
            t = label(it[0], size=size, color=it[1])
        else:
            t = label(it, size=size, color=color)
        mark = Dot(radius=0.055 * size / 30).set_fill(mark_color, 1.0)
        row = VGroup(mark, t)
        t.next_to(mark, RIGHT, buff=0.22)
        mark.match_y(t)
        rows.add(row)
    rows.arrange(DOWN, buff=buff, aligned_edge=LEFT)
    if width is not None and rows.get_width() > width:
        rows.set_width(width)
    return rows


def tarrow(a, b, color=MUT, width=SW_THIN, buff=0.08, tip=0.18, opacity=1.0):
    """Thin themed arrow from point/mobject a to point/mobject b.

    Mobject endpoints snap to the facing edge (via Line's buff logic), so arrows
    start/stop just outside boxes instead of piercing them.
    """
    ln = Line(a, b, buff=buff)
    s, e = ln.get_start(), ln.get_end()
    v = e - s
    L = max(float(np.linalg.norm(v)), 1e-9)
    u = v / L
    tl = min(tip, 0.45 * L)
    n = np.array([-u[1], u[0], 0.0])
    shaft = Line(s, e - u * tl * 0.8, stroke_width=width, stroke_color=color,
                 stroke_opacity=opacity)
    head = Polygon(e, e - u * tl + n * tl * 0.42, e - u * tl - n * tl * 0.42)
    head.set_fill(color, opacity)
    head.set_stroke(width=0)
    return VGroup(shaft, head)


def pill(s, color=GOLD, size=FS_LABEL, pad_x=0.32, pad_y=0.16, fill=0.12, math=False):
    """Rounded pill with a label (proof-tree step names, roles, tags)."""
    t = mtex(s, size=size, color=color) if math else label(s, size=size, color=color)
    h = t.get_height() + 2 * pad_y
    box = RoundedRectangle(width=t.get_width() + 2 * pad_x, height=h,
                           corner_radius=h / 2)
    box.set_fill(color, fill)
    box.set_stroke(color, SW_THIN, 0.9)
    t.move_to(box)
    return VGroup(box, t)


def boxed(mob, color=MUT, pad=0.25, fill=0.05, radius=0.15, stroke=SW_THIN, opacity=0.8):
    """Wrap any mobject in a rounded panel sized to it (pad on all sides)."""
    box = RoundedRectangle(width=mob.get_width() + 2 * pad,
                           height=mob.get_height() + 2 * pad, corner_radius=radius)
    box.set_fill(color, fill)
    box.set_stroke(color, stroke, opacity)
    box.move_to(mob)
    return VGroup(box, mob)


def dock(mob, corner=UL, scale=0.42, buff=0.3):
    """Animate-ready target for 'old context shrinks to a corner'.

    Usage: self.play(mob.animate.scale(0.42).to_corner(UL, buff=0.3).fade(0.3))
    Keep docked text >= FS_MIN effective size or drop the text before docking.
    """
    return mob.scale(scale).to_corner(corner, buff=buff)


# ---- layout linter -----------------------------------------------------------
_LINT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lint")


def _vis_opacity(m):
    op = 0.0
    for sm in m.get_family():
        if sm.has_points():
            try:
                op = max(op, float(sm.get_fill_opacity()))
            except Exception:
                pass
    return op


def _bbox(m):
    return (m.get_left()[0], m.get_right()[0], m.get_bottom()[1], m.get_top()[1])


def _seg_hits_box(p, q, box):
    """Liang-Barsky: does segment p->q pass through the box interior?"""
    x0, x1, y0, y1 = box
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if abs(pp) < 1e-12:
            if qq < 0:
                return False
        else:
            r = qq / pp
            if pp < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
            if t0 > t1:
                return False
    return True


def lint_layout(scene):
    """Check the current frame for text that is off-frame, too small, overlapping
    other text, or crossed by a line. Findings accumulate on the scene and are
    written to anim/lint/<Scene>.txt at tear-down (deduplicated)."""
    found = getattr(scene, "_lint", None)
    if found is None:
        found = scene._lint = {}
    texts, lines = [], []
    seen = set()
    for top in scene.mobjects:
        for m in top.get_family():
            if id(m) in seen:
                continue
            seen.add(id(m))
            if hasattr(m, "font_pt"):
                if _vis_opacity(m) > 0.2 and m.get_width() > 1e-3:
                    texts.append(m)
            elif isinstance(m, Line) and m.has_points():
                try:
                    if float(m.get_stroke_opacity()) > 0.2 and m.get_stroke_width() > 0.5:
                        lines.append(m)
                except Exception:
                    pass
    t = round(scene.time, 1)

    def add(kind, key, msg):
        k = (kind, key)
        if k not in found:
            found[k] = f"[t={t:6.1f}] {kind:8s} {msg}"

    boxes = []
    for m in texts:
        eff = m.font_pt * m.get_height() / m.base_h
        name = repr(getattr(m, "lint_text", "?"))
        x0, x1, y0, y1 = _bbox(m)
        if eff < FS_MIN - 0.5 and _vis_opacity(m) > 0.5:
            add("small", name, f"{name} renders at {eff:.0f}pt (< {FS_MIN})")
        if x0 < -SAFE_X - 0.25 or x1 > SAFE_X + 0.25 or y0 < -SAFE_Y - 0.2 or y1 > SAFE_Y + 0.2:
            add("offframe", name, f"{name} bbox x[{x0:.2f},{x1:.2f}] y[{y0:.2f},{y1:.2f}] outside safe area")
        boxes.append((m, name, (x0, x1, y0, y1)))
    for i in range(len(boxes)):
        mi, ni, bi = boxes[i]
        ai = (bi[1] - bi[0]) * (bi[3] - bi[2])
        for j in range(i + 1, len(boxes)):
            mj, nj, bj = boxes[j]
            ix = min(bi[1], bj[1]) - max(bi[0], bj[0])
            iy = min(bi[3], bj[3]) - max(bi[2], bj[2])
            if ix > 0 and iy > 0:
                aj = (bj[1] - bj[0]) * (bj[3] - bj[2])
                if ix * iy > 0.08 * min(ai, aj):
                    add("overlap", tuple(sorted((ni, nj))), f"{ni} overlaps {nj}")
    for ln in lines:
        p, q = ln.get_start(), ln.get_end()
        for m, name, (x0, x1, y0, y1) in boxes:
            sx, sy = 0.15 * (x1 - x0), 0.2 * (y1 - y0)
            inner = (x0 + sx, x1 - sx, y0 + sy, y1 - sy)
            if inner[0] < inner[1] and inner[2] < inner[3] and _seg_hits_box(p, q, inner):
                add("crossing", (name, tuple(np.round(p, 1)), tuple(np.round(q, 1))),
                    f"a line {np.round(p[:2], 2)}->{np.round(q[:2], 2)} crosses {name}")


def _lint_flush(scene):
    os.makedirs(_LINT_DIR, exist_ok=True)
    path = os.path.join(_LINT_DIR, f"{type(scene).__name__}.txt")
    with open(path, "w") as f:
        for msg in sorted(getattr(scene, "_lint", {}).values()):
            f.write(msg + "\n")

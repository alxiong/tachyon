"""Act 5 — quadratic residue filters. Anchored to anim/words.json timestamps.

Render:  ./qa.sh act5.py Scene51 [fast]     (one scene at a time)
Layout:  title band (the question) / stage (the diagram) / caption band (the takeaway),
         see the layout system at the bottom of style.py.

Scene chaining: each scene opens on the previous scene's final frame, rebuilt by the
shared builders below (qr_ring_docked / batched_parts / decomp_parts / scale_parts),
so the act plays as one continuous take.
"""

import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manimlib import *
from style import *
import style as _style

P = 29
QRS = {pow(i, 2, P) for i in range(1, P)}  # quadratic residues mod 29
R_OFF = 3                                    # the 5.2 discriminant offset


def qr_color(v):
    return CYAN if (v % P) in QRS else AMBER


# ---- local helpers ------------------------------------------------------------

def strike(mob, color=FLARE):
    """Deliberate strike-through (a polyline, so the layout linter ignores it)."""
    vm = VMobject()
    vm.set_points_as_corners([mob.get_corner(DL) + 0.08 * DL, mob.get_corner(UR) + 0.08 * UR])
    vm.set_stroke(color, SW_BOLD, 1.0)
    return vm


def ptex(s, size=FS_LABEL, color=TXT):
    """Prose with inline typst math ('$x$ is a square'): one baseline, NCM + NCM Math."""
    return mtex(s, size=size, color=color, math=False)


def blist(items, size=FS_BODY, color=TXT, mark_color=GOLD, pitch=None):
    """Bullet list on a fixed BASELINE pitch (style.bullets() stacks ink boxes, so a
    row with descenders sits visibly lower than one without). items: str or ptex body."""
    pitch = pitch or size * _style._PT2UNIT * 1.55
    rows = VGroup()
    for k, s in enumerate(items):
        m = mtex("|" + s, size=size, color=color, math=False)
        strut = m.submobjects[0]
        sb, sh = strut.get_bottom()[1], strut.get_height()
        m.remove(strut)
        m.base_h = max(m.get_height(), 1e-6)
        m.lint_text = s[:40]
        y = -k * pitch
        m.shift(UP * (y - sb))
        m.shift(RIGHT * (0.24 - m.get_left()[0]))
        mark = Dot(radius=0.055 * size / 30).set_fill(mark_color, 1.0)
        mark.move_to(np.array([0.0, y + 0.42 * sh, 0]))
        rows.add(VGroup(mark, m))
    return rows


def bucket(w=1.2, h=0.8, color=STAR, bits="", cover=(0.0, 1.0), stroke_op=0.95,
           bits_size=FS_LABEL):
    """A routing bucket: rounded box, profile-bit tag, epoch-coverage mini bar.

    Children: [box, (bits), track, seg] — seg (the coverage bar) is always [-1].
    """
    box = RoundedRectangle(width=w, height=h, corner_radius=0.1)
    box.set_fill(color, 0.10)
    box.set_stroke(color, SW_THIN, stroke_op)
    g = VGroup(box)
    if bits:
        t = mtex(f'"{bits}"', size=bits_size, color=color)
        t.move_to(box.get_center() + UP * 0.07 * h / 0.8)
        g.add(t)
    track = Line(box.get_corner(DL) + RIGHT * 0.14 + UP * 0.15 * h / 0.8,
                 box.get_corner(DR) + LEFT * 0.14 + UP * 0.15 * h / 0.8,
                 stroke_width=3.5, stroke_color=DIM, stroke_opacity=0.8)
    g.add(track)
    x0, x1 = track.get_start()[0], track.get_end()[0]
    seg = Line(np.array([x0 + cover[0] * (x1 - x0), track.get_start()[1], 0]),
               np.array([x0 + cover[1] * (x1 - x0), track.get_start()[1], 0]),
               stroke_width=4.5, stroke_color=color, stroke_opacity=1.0)
    g.add(seg)
    return g


def bucket_morph(src, dst, copy=True, bits=True):
    """Part-wise bucket morph (box->box, track->track, seg->seg, bits->bits): never a
    scribble from mismatched submobject counts."""
    T = TransformFromCopy if copy else ReplacementTransform
    anims = [T(src[0], dst[0]), T(src[-2], dst[-2]), T(src[-1], dst[-1])]
    sb, db = len(src) == 4, len(dst) == 4
    if sb and db and getattr(src[1], "lint_text", 1) == getattr(dst[1], "lint_text", 2):
        anims.append(T(src[1], dst[1]))
    else:
        if db and bits:   # one FadeIn per target: a second one would begin() on the
            anims.append(FadeIn(dst[1], scale=0.8))   # already-faded label, ending invisible
        if sb and not copy:
            anims.append(FadeOut(src[1]))
    return anims


def edge(a, b, color=DIM, opacity=0.6):
    """A routing-network strand from bucket a (bottom) to bucket b (top)."""
    return Line(a.get_bottom(), b.get_top(), buff=0.06, stroke_width=SW_THIN,
                stroke_color=color, stroke_opacity=opacity)


def swap_title(old, new):
    """Staggered title swap: the old title clears before the new one lands (a
    simultaneous cross-fade overlaps the two strings' glyphs into a garble)."""
    return AnimationGroup(FadeOut(old, shift=UP * 0.15), FadeIn(new, shift=UP * 0.15),
                          lag_ratio=0.85)


def lamp(on_color=GOLD, r=0.19):
    c = Circle(radius=r)
    c.set_stroke(on_color, SW_THIN, 0.9)
    c.set_fill(on_color, 0.0)
    return c


def fit_width(mob, w):
    if mob.get_width() > w:
        mob.set_width(w)
    return mob


# ---- 5.2 builders (5.3 opens on 5.2's final frame) ------------------------------

RING_C = np.array([-3.5, 0.15, 0])
RADIUS = 2.15
RING_DOCK = np.array([-6.0, 3.05, 0])
PICK = 4          # profile 1010 under R_0 = 3: first bit matches its ring colour


def ring_pos(v):
    th = TAU * (v - 1) / (P - 1)
    return RING_C + RADIUS * np.array([np.sin(th), np.cos(th), 0])


def qr_ring():
    r = SimpleNamespace()
    r.dots = {v: Dot(ring_pos(v), radius=0.1).set_fill(TXT, 0.9) for v in range(1, P)}
    r.ring = VGroup(*r.dots.values())
    r.zero = Dot(RING_C, radius=0.1).set_fill(DIM, 0.9)
    r.ztag = mtex("0", size=FS_SMALL, color=MUT).next_to(r.zero, DOWN, buff=0.12)
    r.ftag = mtex('FF_p without {0}', size=FS_BODY, color=MUT).move_to(RING_C + UP * 0.7)
    r.halo = Circle(radius=0.22).set_stroke(GOLD, SW, 1.0).move_to(r.dots[PICK])
    return r


def qr_ring_docked():
    """5.2's ring in its final, docked state (all classes under R, −R on the QR side)."""
    r = qr_ring()
    for v, d in r.dots.items():
        d.set_fill(qr_color(v + R_OFF) if (v + R_OFF) % P else CYAN, 0.95)
    g = VGroup(r.ring, r.zero, r.halo)
    g.scale(0.3).move_to(RING_DOCK).fade(0.3)
    return g


AX_Y, AX_X0, UX, UY = -2.2, -6.3, 0.37, 0.3
ROOTS_X = [4, 7, 9, 13, 16]       # quadratic residues mod 29
ROOTS_Y = [2, 6, 3, 10, 4]        # one square root of each (2^2=4, 6^2=7, ...)
G_COEF = np.polyfit(ROOTS_X, ROOTS_Y, 4)   # the real interpolant: a smooth g(X)
BRX = 3.95                                  # batched-test right column centre


def ax_pt(x, y=0.0):
    return np.array([AX_X0 + UX * x, AX_Y + UY * y, 0])


def batched_parts():
    """The batched-QR-test diagram (5.2 part two), every piece in its final place."""
    p = SimpleNamespace()
    p.axis = Line(ax_pt(-0.2), ax_pt(18.2), stroke_width=SW_THIN, stroke_color=DIM)
    p.rdots = VGroup(*[Dot(ax_pt(x), radius=0.1).set_fill(CYAN, 1.0) for x in ROOTS_X])
    p.rlabs = VGroup(*[mtex(f'x_{i+1}', size=FS_SMALL, color=CYAN)
                       .next_to(p.rdots[i], DOWN, buff=0.16) for i in range(5)])
    p.facc = mtex('f(X) = product_i (X - x_i)', size=FS_HEAD, color=STAR)
    p.facc.move_to(np.array([BRX, 2.1, 0]))
    p.sqf = label("square-free, by the uniqueness rule", size=FS_SMALL, color=MUT)
    p.sqf.next_to(p.facc, DOWN, buff=0.2)
    p.lifted = VGroup(*[Dot(ax_pt(x, y), radius=0.09).set_fill(GOLD, 1.0)
                        for x, y in zip(ROOTS_X, ROOTS_Y)])
    p.lifts = VGroup(*[DashedLine(ax_pt(x), ax_pt(x, y), stroke_width=2.0,
                                  stroke_color=GOLD, stroke_opacity=0.6)
                       for x, y in zip(ROOTS_X, ROOTS_Y)])
    p.curve = VMobject()
    p.curve.set_points_smoothly([ax_pt(x, np.polyval(G_COEF, x))
                                 for x in np.linspace(3.92, 16.15, 90)])
    p.curve.set_stroke(GOLD, SW, 0.95)
    p.glab = mtex('g(X)', size=FS_BODY, color=GOLD)
    p.glab.next_to(ax_pt(14.1, 11.9), UP, buff=0.12)
    p.iden = mtex('g(X)^2 - X = f(X) dot h(X)', size=44, color=STAR)
    fit_width(p.iden, 5.4).move_to(np.array([BRX, 0.55, 0]))
    p.hwit = rich([("the quotient", MUT), ("$h$", GOLD), ("is the witness", MUT)],
                  size=FS_SMALL, buff=0.1)
    p.hwit.next_to(p.iden, DOWN, buff=0.22)
    p.env_g = envelope(1.45, 0.95, color=GOLD, tex_label="g")
    p.env_h = envelope(1.45, 0.95, color=GOLD, tex_label="h")
    p.envs = VGroup(p.env_g, p.env_h).arrange(RIGHT, buff=0.45)
    p.envs.move_to(np.array([BRX, -0.95, 0]))
    r_x = 11.0
    p.probe = Line(ax_pt(r_x, 9.0), ax_pt(r_x, -0.7), stroke_width=SW, stroke_color=STAR)
    p.rlab = mtex("r", size=FS_LABEL, color=STAR).next_to(p.probe.get_end(), DOWN,
                                                          buff=0.08)
    p.lhs = mtex('g(r)^2 - r', size=FS_HEAD, color=GOLD)
    p.eqs = mtex('=', size=FS_HEAD, color=STAR)
    p.rhs = mtex('f(r) dot h(r)', size=FS_HEAD, color=CYAN)
    p.check = VGroup(p.lhs, p.eqs, p.rhs).arrange(RIGHT, buff=0.25)
    p.ok = checkmark(0.42, color=GOLD).next_to(p.check, RIGHT, buff=0.3)
    VGroup(p.check, p.ok).move_to(np.array([BRX, -2.25, 0]))
    nqrv = tex_chip('g(X)^2 - c dot X = f(X) dot h(X)', color=AMBER, size=FS_LABEL)
    nqrl = label("non-residue version:", size=FS_LABEL, color=AMBER)
    p.nrow = VGroup(nqrl, nqrv).arrange(RIGHT, buff=0.3).move_to(UP * CAPTION_Y)
    p.title = scene_title("the batched QR test", color=GOLD)
    p.final = [p.axis, p.rdots, p.rlabs, p.facc, p.sqf, p.lifts, p.lifted, p.curve,
               p.glab, p.iden, p.hwit, p.envs, p.probe, p.rlab, p.check, p.ok, p.nrow,
               p.title]
    return p


# ---- 5.3 builders (5.4 opens on 5.3's final frame) ------------------------------

MIX = [CYAN, AMBER, CYAN, AMBER, AMBER, CYAN, CYAN, AMBER, CYAN]
FC = np.array([-3.75, 1.5, 0])


def decomp_parts():
    """The QR-decomposition diagram + check column (5.3), in its START state."""
    p = SimpleNamespace()
    p.fbox = panel(3.6, 1.55, color=STAR, fill_opacity=0.05).move_to(FC)
    p.flab = mtex('f(X)', size=FS_BODY, color=STAR).next_to(p.fbox, LEFT, buff=0.25)
    p.beads = VGroup(*[bead(c, 0.15) for c in MIX])
    p.beads.arrange_in_grid(2, 5, buff=0.42).move_to(FC)
    p.amb_i = [i for i, c in enumerate(MIX) if c == AMBER]
    p.cy_i = [i for i, c in enumerate(MIX) if c == CYAN]
    rchip = tex_chip('R', color=STAR, size=FS_BODY)
    rlab = label("discriminant", size=FS_SMALL, color=MUT)
    p.rg = VGroup(rchip, rlab).arrange(DOWN, buff=0.12).next_to(p.fbox, RIGHT, buff=0.35)
    QY = -0.95
    p.q0 = panel(2.7, 1.35, color=AMBER, fill_opacity=0.06).move_to(np.array([-5.0, QY, 0]))
    p.q1 = panel(2.7, 1.35, color=CYAN, fill_opacity=0.06).move_to(np.array([-2.1, QY, 0]))
    p.q0lab = rich([("$q_0 (X)$", AMBER), ("non-residues", AMBER)], size=FS_LABEL, buff=0.15)
    p.q0lab.next_to(p.q0, DOWN, buff=0.15)
    p.q1lab = rich([("$q_1 (X)$", CYAN), ("residues", CYAN)], size=FS_LABEL, buff=0.15)
    p.q1lab.next_to(p.q1, DOWN, buff=0.15)
    p.a0 = tarrow(p.fbox.get_bottom() + LEFT * 0.6, p.q0.get_top() + RIGHT * 0.3,
                  color=AMBER, width=SW)
    p.a1 = tarrow(p.fbox.get_bottom() + RIGHT * 0.6, p.q1.get_top() + LEFT * 0.3,
                  color=CYAN, width=SW)
    # children: copies of the parent's roots (the parent keeps ghosts: f = q0 * q1)
    p.kid0 = VGroup(*[bead(AMBER, 0.15) for _ in p.amb_i]).arrange(RIGHT, buff=0.3)
    p.kid0.move_to(p.q0)
    p.kid1 = VGroup(*[bead(CYAN, 0.15) for _ in p.cy_i]).arrange(RIGHT, buff=0.22)
    p.kid1.move_to(p.q1)
    p.slots = VGroup(*[bead(CYAN, 0.15) for _ in range(6)]).arrange(RIGHT, buff=0.12)
    p.slots.move_to(p.q1)    # 6 slots: the 5 residues + the exceptional value −R
    # −R is one of f's roots (the exceptional value): it sits in the parent's 10th slot
    grid10 = VGroup(*[bead(STAR, 0.15) for _ in range(10)])
    grid10.arrange_in_grid(2, 5, buff=0.42).move_to(FC)
    p.beads.move_to(grid10[:9].get_center()).align_to(grid10, UL)
    p.mr = Dot(radius=0.15).set_fill(STAR, 1.0).move_to(grid10[9])
    p.mr_ghost = p.mr.copy().set_fill(STAR, 0.3)
    p.mrtag = mtex('-R', size=FS_LABEL, color=STAR)
    names = [
        label("conservation", size=FS_LABEL, color=TXT),
        label("residues are pure", size=FS_LABEL, color=CYAN),
        label("non-residues are pure", size=FS_LABEL, color=AMBER),
        rich([("$-R$", STAR), ("is kept out of", TXT), ("$q_0$", AMBER)],
             size=FS_LABEL, buff=0.1),
    ]
    p.forms = [
        mtex('f(r) = q_0 (r) dot q_1 (r)', size=FS_HEAD, color=STAR),
        mtex('g_1 (r)^2 - (r + R) = q_1 (r) h_1 (r)', size=FS_HEAD, color=CYAN),
        mtex('g_0 (r)^2 - c dot (r + R) = q_0 (r) h_0 (r)', size=FS_HEAD, color=AMBER),
        mtex('q_0 (-R) != 0', size=FS_HEAD, color=STAR),
    ]
    p.lamps = VGroup(*[lamp() for _ in range(4)])
    p.nums = VGroup(*[mtex(str(i + 1), size=FS_SMALL, color=GOLD) for i in range(4)])
    p.rows = VGroup()
    for lp, nm, n, f in zip(p.lamps, p.nums, names, p.forms):
        nm.move_to(lp)
        txt = VGroup(n, f).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        txt.next_to(lp, RIGHT, buff=0.3).align_to(lp, UP).shift(UP * 0.05)
        p.rows.add(VGroup(lp, nm, txt))
    p.rows.arrange(DOWN, buff=0.48, aligned_edge=LEFT)
    p.rows.move_to(np.array([3.5, 0.0, 0])).align_to(np.array([0.45, 0, 0]), LEFT)
    fit_width(p.rows, 6.3)
    p.wall = Line(p.q0.get_corner(UL) + RIGHT * 0.1, p.q0.get_corner(UR) + LEFT * 0.1,
                  stroke_width=6, stroke_color=GOLD)
    p.comp = label("everything from here on is composition", size=FS_BODY, color=TXT)
    p.comp.move_to(UP * CAPTION_Y)
    p.title = scene_title("QR decomposition", color=GOLD)
    return p


def decomp_final(p):
    """Put decomp_parts() into 5.3's END state; returns the on-screen mobjects."""
    for i in range(len(MIX)):
        p.beads[i].set_fill(opacity=0.3)
    for b, s in zip(p.kid1, p.slots[:5]):
        b.move_to(s)
    p.mr.set_fill(CYAN, 1.0).move_to(p.slots[5])
    p.beads.add(p.mr_ghost)
    for lp in p.lamps:
        lp.set_fill(GOLD, 0.35).set_stroke(GOLD, SW, 1.0)
    p.icon = VGroup(p.fbox, p.beads, p.a0, p.a1, p.q0, p.q1, p.kid0, p.kid1, p.mr)
    p.texts = VGroup(p.flab, p.rg, p.q0lab, p.q1lab, p.rows, p.comp)
    return [p.title, p.icon, p.texts]


ICON_C = np.array([-5.85, 3.1, 0])   # 5.4: the atomic relation docked top-left
ICON_S = 0.26


# ---- 5.4 builders (5.5 opens on 5.4's final frame) ------------------------------

def scale_parts():
    p = SimpleNamespace()
    p.title = scene_title("does the address space suffice?")
    p.s1 = mtex('50 "K tx/s" times 2 "weeks" times 8 "tg/tx" < 4.84 times 10^11 '
                '"tachygrams"', size=FS_BODY + 2, color=TXT)
    p.s2 = mtex('(4.84 times 10^11) / 7936 < 6.1 times 10^7 "root buckets"',
                size=FS_BODY + 2, color=TXT)
    k = min(1.0, 12.6 / max(p.s1.get_width(), p.s2.get_width()))
    p.s1.scale(k).move_to(UP * 2.05)
    p.s2.scale(k).move_to(UP * 0.95)
    p.s2b = mtex('=> quad approx 26 "rounds"', size=FS_HEAD, color=STAR).move_to(UP * -0.1)
    p.cells = VGroup(*[Square(0.3) for _ in range(32)]).arrange(RIGHT, buff=0.06)
    p.cells.move_to(UP * -1.65)
    for i, c in enumerate(p.cells):
        if i < 26:
            c.set_fill(GOLD, 0.55).set_stroke(GOLD, SW_THIN, 0.95)
        else:
            c.set_fill(GOLD, 0.0).set_stroke(MUT, SW_THIN, 0.9)
    p.s3 = mtex('"profile budget:" 32 "bits"', size=FS_BODY, color=GOLD)
    p.s3.next_to(p.cells, UP, buff=0.25)
    p.rounds_br = bracket(p.cells[:26], color=GOLD, below=True, buff=0.1)
    p.rounds_lab = label("one bit per round", size=FS_LABEL, color=GOLD)
    p.rounds_lab.next_to(p.rounds_br, DOWN, buff=0.12)
    p.slack_br = bracket(p.cells[26:], color=CYAN, below=True, buff=0.1)
    p.slack_lab = label("slack", size=FS_LABEL, color=CYAN)
    p.slack_lab.next_to(p.slack_br, DOWN, buff=0.12)
    p.body = VGroup(p.s1, p.s2, p.s2b, p.cells, p.s3, p.rounds_br, p.rounds_lab,
                    p.slack_br, p.slack_lab)
    return p


class Scene51(TimedScene):
    """5.1 — Bucketing by an intrinsic address."""

    def construct(self):
        A = lambda p, o=1: anchor("5.1", p, o)
        AA = lambda ps, o=1: anchor_any("5.1", ps, o)

        # "here's the target, stated like a theorem" — the title band holds the goal
        thm = mtex('"prove:" quad "nf" in.not "epoch"_e', size=FS_TITLE, color=STAR)
        thm.move_to(UP * TITLE_Y)
        self.wait(0.6)
        self.play(Write(thm), run_time=1.6)

        # "a closed epoch holding N tachygrams": the act-4 wall, centre stage
        env = envelope(3.4, 2.05, color=CYAN, tex_label=r"e(X)")
        env.move_to(UP * 0.2)
        deg = mtex('"deg" e = 4.8 times 10^8', size=FS_LABEL, color=FLARE)
        deg.next_to(env, DOWN, buff=0.3)
        self.pad_to(A("closed epoch") - 0.3)
        self.play(FadeIn(env, scale=1.1), run_time=0.9)
        self.pad_to(A("holding") - 0.2)
        self.play(FadeIn(deg, shift=UP * 0.12), run_time=0.6)
        self.pad_to(A("nowhere") - 0.2)
        self.play(Indicate(thm, color=GOLD, scale_factor=1.04), run_time=0.8)
        cost = label("at amortized sublinear cost", size=FS_LABEL, color=GOLD)
        cost.next_to(thm, DOWN, buff=0.16)
        self.pad_to(A("sublinear") - 0.5)
        self.play(FadeIn(cost, shift=UP * 0.15), run_time=0.7)

        # "the plan is bucketing" — the polynomial shatters into a grid of buckets
        GRID_C = np.array([-2.75, -0.3, 0])
        grid = VGroup(*[RoundedRectangle(width=0.74, height=0.74, corner_radius=0.08)
                        for _ in range(32)])
        for sq in grid:
            sq.set_fill(CYAN, 0.10)
            sq.set_stroke(CYAN, SW_THIN, 0.8)
        grid.arrange_in_grid(4, 8, buff=0.2)
        grid.move_to(np.array([0, -0.3, 0]))
        shards = [env[0].copy() for _ in grid]
        self.pad_to(A("plan is bucketing") - 0.4)
        self.play(FadeOut(env), FadeOut(deg),
                  LaggedStart(*[ReplacementTransform(s, g) for s, g in zip(shards, grid)],
                              lag_ratio=0.025),
                  run_time=1.5)
        add_shimmer(grid, amp=0.25)

        # notes column: the hash-table contrast (the grid makes room on the left)
        NX = 4.35
        self.pad_to(A("plenty of structures") - 0.2)
        self.play(grid.animate.move_to(GRID_C), run_time=1.0)
        owner = key_chip("hash table: the owner routes", color=MUT, size=FS_LABEL)
        owner.move_to(np.array([NX, 1.75, 0]))
        self.pad_to(A("hash table buckets") - 0.5)
        self.play(FadeIn(owner, shift=UP * 0.2), run_time=0.8)
        self.pad_to(A("nothing is trusted") - 0.3)
        ox = strike(owner)
        self.play(ShowCreation(ox), owner.animate.fade(0.35), run_time=0.7)

        # "the queried element itself must be able to compute which bucket"
        q = bead(GOLD, 0.14).move_to(np.array([NX - 0.9, 0.35, 0]))
        qtag = mtex("x", size=FS_BODY, color=GOLD).next_to(q, LEFT, buff=0.15)
        self.pad_to(A("queried element") - 0.3)
        self.play(FadeIn(q, scale=1.6), FadeIn(qtag), run_time=0.6)
        bits = VGroup(*[mtex(f'"{b}"', size=FS_BODY, color=(CYAN if b == "1" else AMBER))
                        for b in "1011"])
        bits.arrange(RIGHT, buff=0.18).next_to(q, RIGHT, buff=0.4)
        self.pad_to(A("compute which bucket") - 0.4)
        self.play(LaggedStart(*[FadeIn(m, scale=1.4) for m in bits], lag_ratio=0.25),
                  run_time=1.0)
        # home in on exactly one bucket (top row — keeps the approach clear)
        target = grid[3]
        q_to = target.get_top() + UP * 0.27
        self.pad_to(A("no help no table") - 0.6)
        self.play(q.animate.move_to(q_to),
                  qtag.animate.next_to(q_to, LEFT, buff=0.26),
                  bits.animate.next_to(q_to, UP, buff=0.2),
                  run_time=1.1)
        self.play(target.animate.set_stroke(GOLD, SW_BOLD, 1.0).set_fill(GOLD, 0.25),
                  run_time=0.4)

        # "and a verifier must be able to check both"
        ver_h = label("a verifier checks:", size=FS_LABEL, color=MUT)
        ver = blist(["the address is checkable", "the bucket is faithful"],
                    size=FS_LABEL, color=TXT, mark_color=STAR)
        verg = VGroup(ver_h, ver).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        verg.move_to(np.array([NX, 0.0, 0]))
        self.pad_to(A("verifier must") - 0.4)
        self.play(FadeIn(verg, shift=UP * 0.15), run_time=0.7)

        # "three properties"
        self.pad_to(A("three properties") - 0.5)
        self.play(FadeOut(owner), FadeOut(ox), FadeOut(verg), run_time=0.5)
        props_h = label("an address that is:", size=FS_LABEL, color=MUT)
        props = blist(["deterministic, intrinsic", "balanced", "circuit-cheap"],
                      size=FS_BODY, color=STAR, mark_color=GOLD)
        propg = VGroup(props_h, props).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        propg.move_to(np.array([NX, 0.2, 0]))
        self.play(FadeIn(props_h), run_time=0.3)
        self.pad_to(A("deterministic and intrinsic") - 0.3)
        self.play(FadeIn(props[0], shift=RIGHT * 0.2), run_time=0.7)
        self.pad_to(AA(["balanced buckets come out", "balanced buckets"]) - 0.3)
        self.play(FadeIn(props[1], shift=RIGHT * 0.2), run_time=0.7)
        self.pad_to(AA(["in circuit cheap", "circuit cheap"]) - 0.3)
        self.play(FadeIn(props[2], shift=RIGHT * 0.2), run_time=0.7)

        # "hash the element?" — and the in-circuit cost explosion (caption band)
        hashc = tex_chip('"addr" = H(x) thin ?', color=MUT, size=FS_LABEL)
        costx = label("a hash in circuit, per element, per level", size=FS_LABEL,
                      color=FLARE)
        VGroup(hashc, costx).arrange(RIGHT, buff=0.6).move_to(UP * CAPTION_Y)
        self.pad_to(A("hash the element") - 0.4)
        self.play(FadeIn(hashc, shift=UP * 0.15), run_time=0.7)
        self.pad_to(A("times every element") - 0.6)
        self.play(FadeIn(costx), run_time=0.8)
        hx = strike(hashc)
        self.pad_to(A("much cheaper") - 0.3)
        self.play(ShowCreation(hx), hashc.animate.fade(0.35),
                  costx.animate.fade(0.35), run_time=0.7)

        # "hiding in the field itself ... since Gauss" — clear, then name it
        self.pad_to(A("field itself") - 0.3)
        clear_shimmer(grid)
        self.play(FadeOut(VGroup(grid, q, qtag, bits, propg, hashc, hx, costx, thm, cost)),
                  run_time=0.8)
        tease = heading("quadratic residues", size=56, color=GOLD).move_to(UP * 0.2)
        self.pad_to(A("since gauss") - 0.6)
        self.play(Write(tease), run_time=1.3)
        self.pad_to(scene_T("5.1"))


class Scene52(TimedScene):
    """5.2 — Number theory detour (approved verbatim narration)."""

    def construct(self):
        A = lambda p, o=1: anchor("5.2", p, o)
        AA = lambda ps, o=1: anchor_any("5.2", ps, o)

        # continuity: 5.1 ends on this heading, centered
        tease = heading("quadratic residues", size=56, color=GOLD).move_to(UP * 0.2)
        self.add(tease)
        title = scene_title("quadratic residues", color=GOLD)
        r = qr_ring()
        dots, ring = r.dots, r.ring

        # "take a prime field and set zero aside"
        self.wait(0.4)
        self.play(AnimationGroup(
            ReplacementTransform(tease, title),
            AnimationGroup(LaggedStart(*[FadeIn(m, scale=1.3) for m in ring],
                                       lag_ratio=0.03), FadeIn(r.ftag)),
            lag_ratio=0.35), run_time=1.6)
        self.play(FadeIn(r.zero, scale=1.5), FadeIn(r.ztag), run_time=0.6)

        # "split exactly in half" — residues cyan, the rest amber
        self.pad_to(A("split exactly in half") - 0.2)
        self.play(LaggedStart(*[dots[v].animate.set_fill(qr_color(v), 0.95)
                                for v in range(1, P)], lag_ratio=0.02),
                  run_time=1.4)

        def leg(text, c):
            t = label(text, size=FS_LABEL, color=c)
            d = Dot(radius=0.1).set_fill(c, 1.0).next_to(t, LEFT, buff=0.15)
            return VGroup(d, t)
        leg1 = leg("squares (QR)", CYAN)
        leg2 = leg("non-squares", AMBER)
        legend = VGroup(leg1, leg2).arrange(RIGHT, buff=0.6)
        legend.move_to(RING_C[0] * RIGHT + DOWN * 2.62)
        self.pad_to(A("quadratic residues") - 0.3)
        self.play(FadeIn(leg1), FadeIn(leg2), run_time=0.7)

        # notes column: one constraint each way
        NL = 1.0   # notes left edge

        def note_row(chip, text, y):
            row = VGroup(chip, text)
            text.next_to(chip, RIGHT, buff=0.35)
            row.move_to(np.array([0, y, 0]))
            row.align_to(np.array([NL, 0, 0]), LEFT)
            return row

        c1 = tex_chip('y^2 = x', color=CYAN, size=FS_BODY)
        c1t = ptex("$x$ is a square", size=FS_LABEL, color=TXT)
        row1 = note_row(c1, c1t, 2.1)
        self.pad_to(A("root y as advice") - 0.5)
        self.play(FadeIn(c1, scale=1.1), run_time=0.7)
        self.pad_to(A("y squared equals x") - 0.2)
        self.play(FadeIn(c1t, shift=RIGHT * 0.15),
                  Indicate(c1, color=CYAN, scale_factor=1.1), run_time=0.8)

        # "a classic flip: multiply by a non-residue"
        c2 = tex_chip('y^2 = c dot x', color=AMBER, size=FS_BODY)
        c2t = ptex("$x$ is a non-square", size=FS_LABEL, color=TXT)
        row2 = note_row(c2, c2t, 1.2)
        self.pad_to(A("classic flip") - 0.3)
        self.play(TransformFromCopy(c1, c2), run_time=0.9)
        cfix = rich([("$c$", AMBER), (": a fixed public non-residue", MUT)],
                    size=FS_SMALL, buff=0.06)
        cfix.next_to(row2, DOWN, buff=0.2).align_to(row2, LEFT).shift(RIGHT * 0.1)
        self.pad_to(A("public non residue c") - 0.3)
        self.play(FadeIn(cfix), run_time=0.6)
        self.pad_to(A("y squared equals cx") - 0.2)
        self.play(FadeIn(c2t, shift=RIGHT * 0.15),
                  Indicate(c2, color=AMBER, scale_factor=1.1), run_time=0.8)

        # "slide everything by an offset R" — the ring re-colors
        sh = tex_chip('x -> x + R', color=STAR, size=FS_BODY)
        disc = label("a QR discriminant", size=FS_LABEL, color=STAR)
        row3 = note_row(sh, disc, -0.25)
        self.pad_to(A("slide everything") - 0.3)
        self.play(FadeIn(sh, shift=LEFT * 0.3), run_time=0.7)
        self.play(LaggedStart(*[dots[v].animate.set_fill(
            qr_color(v + R_OFF) if (v + R_OFF) % P != 0 else STAR, 0.95)
            for v in range(1, P)], lag_ratio=0.02), run_time=1.3)
        self.pad_to(A("qr discriminant") - 0.3)
        self.play(FadeIn(disc, shift=RIGHT * 0.15), run_time=0.6)

        # "k discriminants give every field element a k-bit profile"
        # (the first bit is the class this element shows under the current R)
        self.pad_to(A("k discriminants") - 0.3)
        pick = dots[PICK]
        halo = r.halo
        bstr = "".join("1" if (PICK + R_OFF + j) % P in QRS else "0" for j in range(4))
        prof = VGroup(*[mtex(f'"{b}"', size=FS_BODY, color=(CYAN if b == "1" else AMBER))
                        for b in bstr])
        prof.arrange(RIGHT, buff=0.14)
        prof.next_to(pick, RIGHT, buff=0.35)
        self.play(ShowCreation(halo), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(m, scale=1.5) for m in prof], lag_ratio=0.3),
                  run_time=1.2)
        classes = tex_chip('2^k "classes"', color=GOLD, size=FS_BODY)
        bal = ptex("nearly balanced, from $x$ alone", size=FS_SMALL, color=MUT)
        row4 = note_row(classes, bal, -1.15)
        self.pad_to(A("two to the k classes") - 0.3)
        self.play(FadeIn(classes), FadeIn(bal), run_time=0.7)

        # "one edge case: x = −R" — zero is neither class
        self.pad_to(A("one edge case") - 0.3)
        xr = dots[P - R_OFF]
        edge_t = mtex('x = -R', size=FS_LABEL, color=STAR)
        edge_t.next_to(xr, LEFT, buff=0.25)
        self.play(FadeIn(edge_t), xr.animate.set_fill(STAR, 1.0).scale(1.6),
                  run_time=0.8)
        self.pad_to(A("neither class") - 0.3)
        self.play(xr.animate(rate_func=there_and_back).scale(1.5), run_time=0.8)
        conv = rich([("$x = -R$", STAR), ("goes to the residue side", CYAN)],
                    size=FS_BODY)
        enf = label("enforced, not just stated", size=FS_BODY, color=FLARE)
        VGroup(conv, enf).arrange(RIGHT, buff=0.5).move_to(UP * CAPTION_Y)
        self.pad_to(A("residue side") - 0.5)
        self.play(xr.animate.set_fill(CYAN, 0.95).scale(1 / 1.6),
                  FadeIn(conv, shift=UP * 0.15), run_time=0.8)
        self.pad_to(A("enforced not just stated") - 0.3)
        self.play(FadeIn(enf, shift=UP * 0.15), run_time=0.7)

        # "a claimed non-residue bit needs an extra witness, x + R ≠ 0"
        wit = tex_chip('x + R != 0', color=AMBER, size=FS_BODY)
        witt = label("witness for a non-residue bit", size=FS_SMALL, color=MUT)
        row5 = note_row(wit, witt, -2.05)
        self.pad_to(A("extra witness") - 0.4)
        self.play(FadeIn(row5, shift=UP * 0.15), run_time=0.8)
        self.pad_to(A("square root zero") - 0.5)
        self.play(Indicate(wit, color=AMBER, scale_factor=1.08), run_time=0.8)

        # ---- part two: the batched test --------------------------------------
        # "we need the test for a whole bucket at once" — the ring docks top-left
        self.pad_to(A("whole bucket at once") - 0.6)
        title2 = scene_title("a whole bucket at once", color=GOLD)
        docked = VGroup(ring, r.zero, halo)
        self.play(FadeOut(VGroup(row1, row2, cfix, row3, row4, row5, legend,
                                 conv, enf, r.ftag, r.ztag, prof, edge_t)),
                  docked.animate.scale(0.3).move_to(RING_DOCK).fade(0.3),
                  swap_title(title, title2),
                  run_time=1.1)

        b = batched_parts()
        self.pad_to(A("buckets accumulator") - 0.5)
        self.play(ShowCreation(b.axis), Write(b.facc), run_time=1.1)
        self.play(LaggedStart(*[FadeIn(m, scale=1.4) for m in b.rdots], lag_ratio=0.1),
                  FadeIn(b.rlabs), run_time=1.0)
        self.pad_to(A("square free") - 0.4)
        self.play(FadeIn(b.sqf), run_time=0.7)

        # "interpolate a polynomial g through the points (x_i, y_i)"
        self.pad_to(A("interpolate") - 0.3)
        self.play(LaggedStart(*[AnimationGroup(ShowCreation(b.lifts[i]),
                                               TransformFromCopy(b.rdots[i], b.lifted[i]))
                                for i in range(5)], lag_ratio=0.15),
                  run_time=1.6)
        self.play(ShowCreation(b.curve), FadeIn(b.glab), run_time=1.2)

        # "g² − X vanishes at every x_i, so f divides it" — the left side is written
        # first, then slides into place as the right side arrives (glyph-for-glyph)
        n0 = len(mtex('g(X)^2 - X', size=44).submobjects)
        iden0 = b.iden[:n0].copy().move_to(np.array([BRX, 0.55, 0]))
        self.pad_to(A("vanishes") - 0.6)
        self.play(Write(iden0), run_time=0.9)
        self.pad_to(A("f divides it") - 0.2)
        self.play(ReplacementTransform(iden0, b.iden[:n0]),
                  FadeIn(b.iden[n0:], shift=LEFT * 0.3), run_time=0.9)
        self.pad_to(A("quotient h") - 0.2)
        self.play(FadeIn(b.hwit), run_time=0.6)

        # "the prover commits to g and h"
        self.pad_to(A("commits to g and h") - 0.4)
        self.play(FadeIn(b.env_g, scale=1.15), FadeIn(b.env_h, scale=1.15), run_time=0.8)

        # "the verifier throws one random point r"
        self.pad_to(A("throws one random point") - 0.3)
        self.play(ShowCreation(b.probe), FadeIn(b.rlab), run_time=0.8)
        self.pad_to(AA(["g of r squared", "checks g of r"]) - 0.2)
        self.play(FadeIn(b.lhs, shift=UP * 0.15), run_time=0.7)
        self.play(FadeIn(b.eqs), FadeIn(b.rhs, shift=UP * 0.15), run_time=0.7)
        cap = label("one identity, one random point: every root certified at once",
                    size=FS_LABEL, color=TXT).move_to(UP * CAPTION_Y)
        self.pad_to(A("one identity") - 0.2)
        self.play(ShowCreation(b.ok), FadeIn(cap, shift=UP * 0.15), run_time=0.6)
        self.pad_to(A("certified at once") - 0.4)
        self.play(LaggedStart(*[Indicate(d, color=CYAN, scale_factor=1.7)
                                for d in b.rdots], lag_ratio=0.1), run_time=1.1)

        # "the non-residue version just carries the factor c"
        self.pad_to(A("factor c") - 0.8)
        self.play(FadeOut(cap, shift=DOWN * 0.15), FadeIn(b.nrow, shift=UP * 0.15),
                  run_time=0.8)

        # "that's the whole batched QR test"
        self.pad_to(A("batched qr test") - 0.5)
        self.play(swap_title(title2, b.title),
                  Indicate(VGroup(b.iden, b.check), color=GOLD, scale_factor=1.04),
                  run_time=1.2)
        self.pad_to(scene_T("5.2"))


class Scene53(TimedScene):
    """5.3 — QR decomposition: one split, four checks."""

    def construct(self):
        A = lambda p, o=1: anchor("5.3", p, o)
        AA = lambda ps, o=1: anchor_any("5.3", ps, o)

        # continuity: open on 5.2's final frame
        b = batched_parts()
        docked = qr_ring_docked()
        self.add(docked, *b.final)
        p = decomp_parts()
        beads, cyans = p.beads, [p.beads[i] for i in p.cy_i]

        # "the batched test checks a bucket that's already pure" — its five residues
        # gather into a pure bucket; everything else clears
        self.wait(0.3)
        rest = VGroup(docked, *[m for m in b.final if m is not b.rdots and m is not b.title])
        pure_row = VGroup(*[bead(CYAN, 0.15) for _ in range(5)]).arrange(RIGHT, buff=0.42)
        pure_row.move_to(FC)
        self.play(FadeOut(rest),
                  *[d.animate.move_to(t).scale(1.5) for d, t in zip(b.rdots, pure_row)],
                  run_time=1.3)
        pure = label("already pure", size=FS_LABEL, color=CYAN)
        pure.next_to(p.fbox, DOWN, buff=0.3)
        self.pad_to(A("bucket") - 0.4)
        self.play(ShowCreation(p.fbox), run_time=0.6)
        self.pad_to(A("already pure") - 0.3)
        self.play(FadeIn(pure, shift=UP * 0.1), run_time=0.6)

        # "take a mixed bucket": the residues settle in, non-residues join
        mixed = label("a mixed bucket", size=FS_LABEL, color=MUT)
        mixed.next_to(p.fbox, DOWN, buff=0.3)
        self.pad_to(A("mixed bucket") - 0.4)
        self.play(*[ReplacementTransform(d, c) for d, c in zip(b.rdots, cyans)],
                  LaggedStart(*[FadeIn(p.beads[i], scale=1.4) for i in p.amb_i],
                              lag_ratio=0.15),
                  FadeIn(p.flab), FadeOut(pure, shift=DOWN * 0.15),
                  FadeIn(mixed, shift=DOWN * 0.15), run_time=1.1)

        # "the atomic relation — QR decomposition"
        self.pad_to(A("atomic relation") - 0.3)
        self.play(swap_title(b.title, p.title), FadeOut(mixed), run_time=1.0)

        # "input: f and a discriminant R"
        self.pad_to(A("discriminant r") - 0.4)
        self.play(FadeIn(p.rg, shift=LEFT * 0.2), run_time=0.7)

        # "output: two buckets" — children are copies; the parent keeps ghosts
        self.pad_to(A("output 2 buckets") - 0.3)
        self.play(ShowCreation(p.a0), ShowCreation(p.a1),
                  ShowCreation(p.q0), ShowCreation(p.q1), run_time=0.9)
        self.pad_to(A("q0 holds the non residues") - 0.2)
        self.play(FadeIn(p.q0lab),
                  LaggedStart(*[TransformFromCopy(beads[i], k)
                                for i, k in zip(p.amb_i, p.kid0)], lag_ratio=0.1),
                  *[beads[i].animate.set_fill(opacity=0.3) for i in p.amb_i],
                  run_time=1.1)
        self.pad_to(A("q1 holds the residues") - 0.2)
        self.play(FadeIn(p.q1lab),
                  LaggedStart(*[TransformFromCopy(beads[i], k)
                                for i, k in zip(p.cy_i, p.kid1)], lag_ratio=0.1),
                  *[beads[i].animate.set_fill(opacity=0.3) for i in p.cy_i],
                  run_time=1.1)

        # "four checks certify the split" — a lamp column on the right
        lamps, rows = p.lamps, p.rows
        self.pad_to(A("4 checks certify") - 0.3)
        self.play(LaggedStart(*[FadeIn(VGroup(lp, nm)) for lp, nm in zip(lamps, p.nums)],
                              lag_ratio=0.15), run_time=0.9)
        fixed = rich([("commit first, then all four checks at one random point", MUT),
                      ("$r$", MUT)], size=FS_LABEL, buff=0.1).move_to(UP * CAPTION_Y)
        self.pad_to(A("commitments are fixed") - 0.5)
        self.play(FadeIn(fixed, shift=UP * 0.15), run_time=0.6)

        def light(i, rt=0.9):
            self.play(lamps[i].animate.set_fill(GOLD, 0.35).set_stroke(GOLD, SW, 1.0),
                      FadeIn(rows[i][2], shift=LEFT * 0.15), run_time=rt)

        # check 1 — conservation: every parent root reappears in exactly one child
        self.pad_to(A("check 1 conservation") - 0.2)
        light(0)
        pairs = list(zip(p.amb_i, p.kid0)) + list(zip(p.cy_i, p.kid1))
        pairs.sort(key=lambda t: t[0])
        self.pad_to(A("nothing added nothing dropped") - 0.2)
        self.play(LaggedStart(*[AnimationGroup(Indicate(beads[i], color=STAR,
                                                        scale_factor=1.6),
                                               Indicate(k, scale_factor=1.6))
                                for i, k in pairs], lag_ratio=0.08), run_time=1.0)
        self.pad_to(A("factorization of the parent") - 0.5)
        self.play(Indicate(VGroup(p.q0lab[0], p.q1lab[0]), color=STAR, scale_factor=1.12),
                  run_time=0.8)

        # checks 2 and 3 — purity
        self.pad_to(A("checks 2 and 3") - 0.2)
        light(1)
        light(2)
        self.pad_to(A("flip factor c") - 0.4)
        self.play(Indicate(p.forms[2], color=AMBER, scale_factor=1.06), run_time=0.7)

        # check 4 — the enforced convention
        mr, mrtag = p.mr, p.mrtag
        self.pad_to(A("check 4") - 0.2)
        self.play(FadeIn(mr, scale=1.5), run_time=0.6)
        self.play(Indicate(mr, color=STAR, scale_factor=1.8), run_time=0.6)
        # it drifts toward the wrong side, leaving its ghost in the parent
        near_q0 = p.q0.get_top() + UP * 0.32 + LEFT * 0.7
        mrtag.next_to(near_q0, LEFT, buff=0.15)
        self.add(p.mr_ghost, mr)
        self.pad_to(A("vacuously") - 0.6)
        self.play(mr.animate.move_to(near_q0), FadeIn(mrtag, shift=LEFT * 0.2),
                  run_time=0.9)
        vac = tex_chip('0^2 = c dot 0', color=FLARE, size=FS_LABEL)
        vac.move_to(np.array([-3.55, -2.55, 0]))
        self.pad_to(A("0 squared equals c times 0") - 0.2)
        self.play(FadeIn(vac, scale=1.1), run_time=0.8)
        self.pad_to(A("wrong side") - 0.3)
        self.play(Indicate(vac, color=FLARE, scale_factor=1.1), run_time=0.7)

        # "one nonzero evaluation — q0 at −R"
        self.pad_to(A("q0 at minus r") - 0.6)
        light(3)
        self.play(ShowCreation(p.wall), run_time=0.5)
        # bounced into q1: the residues make room for it
        near_q1 = p.q1.get_top() + UP * 0.32
        self.pad_to(A("nowhere to go but q1") - 0.4)
        self.play(mr.animate.move_to(near_q1),
                  mrtag.animate.next_to(near_q1, RIGHT, buff=0.15),
                  run_time=0.8)
        self.play(*[k.animate.move_to(s) for k, s in zip(p.kid1, p.slots[:5])],
                  mr.animate.set_fill(CYAN, 1.0).move_to(p.slots[5]),
                  FadeOut(mrtag), FadeOut(vac), FadeOut(p.wall), run_time=0.8)
        self.pad_to(A("its enforced") - 0.3)
        self.play(Indicate(rows[3][2], color=GOLD, scale_factor=1.06), run_time=0.6)

        # "one discriminant, one split, four evaluations"
        recap = rich([("one discriminant", GOLD), ("$->$", MUT), ("one split", GOLD),
                      ("$->$", MUT), ("four checks", GOLD)], size=FS_BODY, buff=0.2)
        recap.move_to(UP * CAPTION_Y)
        self.pad_to(A("one discriminant one split") - 0.1)
        self.play(FadeOut(fixed, shift=DOWN * 0.15),
                  LaggedStart(*[FadeIn(m, shift=UP * 0.15) for m in recap], lag_ratio=0.3),
                  run_time=1.2)
        self.pad_to(A("composition") - 0.6)
        self.play(FadeOut(recap, shift=DOWN * 0.15), FadeIn(p.comp, shift=UP * 0.15),
                  run_time=0.8)
        self.pad_to(scene_T("5.3"))


class Scene54(TimedScene):
    """5.4 — Routing: decompose–merge rounds and the jagged frontier."""

    def construct(self):
        A = lambda p, o=1: anchor("5.4", p, o)
        AA = lambda ps, o=1: anchor_any("5.4", ps, o)

        def set_caption(new, old=None, rt=0.6):
            new.move_to(UP * CAPTION_Y)
            anims = [FadeIn(new, shift=UP * 0.15)]
            if old is not None:
                anims.append(FadeOut(old, shift=DOWN * 0.15))
            self.play(*anims, run_time=rt)
            return new

        # ---- continuity: 5.3's final frame; the split docks as an icon ----------
        dp = decomp_parts()
        self.add(*decomp_final(dp))
        icon = dp.icon
        title = scene_title("routing")
        self.wait(0.3)
        self.play(FadeOut(dp.texts),
                  icon.animate.scale(ICON_S).move_to(ICON_C).fade(0.2),
                  swap_title(dp.title, title), run_time=1.3)

        # ---- the input: anchor chain + root buckets --------------------------
        CH_Y = 2.35
        ROW = [1.3, 0.15, -1.0, -2.15]   # routing-network levels (final layout)
        LOW = 1.15                       # round 1 is built this much lower, then scrolls up
        BH = 0.72
        blocks = VGroup(*[block(0.5, 0.38) for _ in range(8)])
        blocks.arrange(RIGHT, buff=0.38)
        s_a = block(0.5, 0.38).set_stroke(GOLD, SW_THIN, 0.95)
        s_b = block(0.5, 0.38).set_stroke(GOLD, SW_THIN, 0.95)
        s_a.next_to(blocks, LEFT, buff=0.38)
        s_b.next_to(blocks, RIGHT, buff=0.38)
        chain = VGroup(s_a, blocks, s_b).move_to(np.array([0.9, CH_Y, 0]))
        links = VGroup(*[chain_link(blocks[i], blocks[i + 1]) for i in range(7)])
        slinks = VGroup(chain_link(s_a, blocks[0]), chain_link(blocks[7], s_b))
        chain_lab = label("one epoch", size=FS_LABEL, color=MUT)
        chain_lab.next_to(s_a, LEFT, buff=0.35)
        self.pad_to(A("shape of the input") - 0.4)
        self.play(LaggedStart(*[FadeIn(b) for b in [s_a, *blocks, s_b]], lag_ratio=0.07),
                  ShowCreation(links), ShowCreation(slinks), FadeIn(chain_lab),
                  run_time=1.4)

        QW = 0.25  # coverage quarter width
        RX = [-4.65, -1.55, 1.55, 4.65]
        roots = VGroup(*[bucket(2.2, BH, STAR, "", (i * QW, (i + 1) * QW))
                         .move_to(np.array([RX[i], ROW[0] - LOW, 0])) for i in range(4)])
        spans = [SurroundingRectangle(VGroup(blocks[2 * i], blocks[2 * i + 1]), buff=0.06)
                 .round_corners(0.1).set_stroke(STAR, SW_THIN, 0.9) for i in range(4)]
        self.pad_to(A("bounded root buckets") - 0.4)
        self.play(LaggedStart(*[AnimationGroup(TransformFromCopy(spans[i], roots[i][0]),
                                               FadeIn(roots[i][1:], shift=DOWN * 0.2))
                                for i in range(4)], lag_ratio=0.15),
                  run_time=1.5)
        cap = label("root buckets, each covering a contiguous stretch of the chain",
                    size=FS_LABEL, color=TXT)
        self.pad_to(A("contiguous stretch") - 0.4)
        cap = set_caption(cap, rt=0.5)

        # ---- one routing round: decompose, then merge ------------------------
        title2 = scene_title("one round: decompose, then merge")
        self.pad_to(A("two moves") - 0.4)
        self.play(swap_title(title, title2), run_time=0.7)

        def rlabel(s, y):
            return mtex(s, size=FS_LABEL, color=MUT).move_to(np.array([-6.4, y, 0]))

        # decompose: each root bucket splits into an NQR(0) and QR(1) child
        kids = VGroup()
        for i in range(4):
            k0 = bucket(1.3, BH, AMBER, "0", (i * QW, (i + 1) * QW), bits_size=FS_BODY)
            k1 = bucket(1.3, BH, CYAN, "1", (i * QW, (i + 1) * QW), bits_size=FS_BODY)
            k0.move_to(np.array([RX[i] - 0.74, ROW[1] - LOW, 0]))
            k1.move_to(np.array([RX[i] + 0.74, ROW[1] - LOW, 0]))
            kids.add(VGroup(k0, k1))
        e_dec = VGroup(*[edge(roots[i], kids[i][j], (AMBER, CYAN)[j])
                         for i in range(4) for j in range(2)])
        r1 = rlabel("R_1", (ROW[0] + ROW[1]) / 2 - LOW)
        self.pad_to(A("decompose") - 0.2)
        self.play(LaggedStart(*[AnimationGroup(ShowCreation(e_dec[2 * i]),
                                               ShowCreation(e_dec[2 * i + 1]),
                                               *bucket_morph(roots[i], kids[i][0]),
                                               *bucket_morph(roots[i], kids[i][1]))
                                for i in range(4)], lag_ratio=0.12),
                  roots.animate.fade(0.5), FadeIn(r1),
                  Indicate(icon, color=GOLD, scale_factor=1.25), run_time=1.8)
        self.pad_to(A("one new profile bit") - 0.6)
        cap = set_caption(rich([("each child: its parent's anchor range", TXT),
                                ("+ one profile bit", GOLD)], size=FS_LABEL), cap, rt=0.7)

        # merge: adjacent same-profile children fuse (capacity blocks one pair)
        self.pad_to(A("merge") - 0.2)
        m00 = bucket(2.0, BH, AMBER, "0", (0.0, 0.5), bits_size=FS_BODY)
        m01 = bucket(2.0, BH, CYAN, "1", (0.0, 0.5), bits_size=FS_BODY)
        m10 = bucket(2.0, BH, AMBER, "0", (0.5, 1.0), bits_size=FS_BODY)
        m11a = bucket(1.5, BH, CYAN, "1", (0.5, 0.75), bits_size=FS_BODY)
        m11b = bucket(1.5, BH, CYAN, "1", (0.75, 1.0), bits_size=FS_BODY)
        merged = VGroup(m00, m01, m10, m11a, m11b).arrange(RIGHT, buff=0.35)
        merged.move_to(np.array([0, ROW[2] - LOW, 0]))
        src = {m00: [kids[0][0], kids[1][0]], m01: [kids[0][1], kids[1][1]],
               m10: [kids[2][0], kids[3][0]], m11a: [kids[2][1]], m11b: [kids[3][1]]}
        e_mrg = {m: VGroup(*[edge(k, m, m[0].get_stroke_color()) for k in ks])
                 for m, ks in src.items()}

        def merge_anims(ms):
            out = []
            for m in ms:
                out += [ShowCreation(e_mrg[m])]
                for k in src[m]:
                    out += bucket_morph(k, m)
            return out
        self.play(*merge_anims([m00, m01]), run_time=1.0)
        self.play(*merge_anims([m10, m11a, m11b]), kids.animate.fade(0.5), run_time=1.0)
        full = label("over capacity: stays split", size=FS_SMALL, color=FLARE)
        full.next_to(VGroup(m11a, m11b), DOWN, buff=0.16)
        self.pad_to(A("within capacity") - 0.4)
        self.play(FadeIn(full), run_time=0.6)
        self.pad_to(A("multi set union") - 0.3)
        cap = set_caption(rich([("$Q = q_a dot q_b$", STAR),
                                ("multiply the polynomials: no new trust", MUT)],
                               size=FS_LABEL, buff=0.35), cap, rt=0.7)
        self.pad_to(A("no new trust") - 0.4)
        self.play(Indicate(cap[0], color=GOLD, scale_factor=1.08), run_time=0.6)

        # "watch what the two moves preserve"
        self.pad_to(A("splits keep anchor ranges") - 0.3)
        segs = VGroup(*[m[-1] for m in merged])
        self.play(LaggedStart(*[Indicate(s, color=GOLD, scale_factor=1.5)
                                for s in segs], lag_ratio=0.1), run_time=1.2)
        self.pad_to(A("purer in profile") - 0.4)
        cap = set_caption(label("purer in profile, wider in history", size=FS_BODY,
                                color=GOLD), cap, rt=0.7)

        # ---- run it to the end: one full-epoch bucket per profile ------------
        self.pad_to(A("run it to the end") - 0.3)
        title3 = scene_title("after every round")
        self.play(FadeOut(full), FadeOut(cap, shift=DOWN * 0.15),
                  swap_title(title2, title3),
                  VGroup(chain, links, slinks, chain_lab).animate.fade(0.45),
                  VGroup(roots, kids, merged, e_dec, *e_mrg.values(), r1)
                  .animate.shift(UP * LOW),
                  run_time=1.0)
        finals = VGroup(*[bucket(2.2, BH, c, bb, (0.0, 1.0), bits_size=FS_BODY)
                          for bb, c in [("00", AMBER), ("01", CYAN), ("10", AMBER),
                                        ("11", CYAN)]])
        finals.arrange(RIGHT, buff=0.6).move_to(np.array([0, ROW[3], 0]))
        f_src = {0: [m00, m10], 1: [m00, m10], 2: [m01, m11a, m11b], 3: [m01, m11a, m11b]}
        e_r2 = VGroup()
        e_r2_by = {}
        for fi, ms in f_src.items():
            for m in ms:
                e = edge(m, finals[fi], finals[fi][0].get_stroke_color())
                e_r2.add(e)
                e_r2_by[(fi, id(m))] = e
        r2 = rlabel("R_2", (ROW[2] + ROW[3]) / 2)
        self.play(LaggedStart(*[ShowCreation(e) for e in e_r2], lag_ratio=0.05),
                  LaggedStart(*[FadeIn(f, shift=DOWN * 0.2) for f in finals],
                              lag_ratio=0.15),
                  FadeIn(r2), run_time=1.5)
        self.pad_to(A("one bucket per address") - 0.3)
        cap = set_caption(label("one bucket per profile, each spanning the whole epoch",
                                size=FS_BODY, color=STAR), rt=0.8)

        # "embarrassingly parallel: splits independent, merges local, in flight"
        def wave(lines):
            return AnimationGroup(*[ShowPassingFlash(l.copy().set_stroke(GOLD, 5, 1.0),
                                                     time_width=0.6) for l in lines])
        self.pad_to(A("embarrassingly parallel") - 0.3)
        par = label("parallel, streaming, in flight", size=FS_BODY, color=CYAN)
        cap = set_caption(par, cap, rt=0.8)
        all_mrg = [e for g in e_mrg.values() for e in g]
        self.pad_to(A("splits are independent") - 0.2)
        self.play(wave(e_dec), run_time=0.9)
        self.pad_to(A("merges are local") - 0.2)
        self.play(wave(all_mrg), run_time=0.9)
        self.pad_to(A("in flight") - 0.3)
        self.play(wave(e_r2), run_time=0.9)
        self.pad_to(A("stamps arrive") - 0.4)
        self.play(Indicate(VGroup(blocks[6], blocks[7]), color=GOLD, scale_factor=1.25),
                  run_time=0.8)

        # ---- reality is slightly jagged --------------------------------------
        # the first round scrolls away; depth-1 / depth-2 / depth-3 rows remain
        self.pad_to(A("slightly jagged") - 0.4)
        title4 = scene_title("the jagged frontier", color=FLARE)
        up = (ROW[0] - ROW[2]) * UP
        keep = VGroup(merged, e_r2, finals, r2)
        self.play(FadeOut(VGroup(roots, kids, e_dec, *e_mrg.values(), r1)),
                  swap_title(title3, title4),
                  FadeOut(cap, shift=DOWN * 0.15), run_time=0.9)
        self.play(keep.animate.shift(up), run_time=0.9)
        # "a few profiles still hold multiple partial buckets": 11 is really two
        p11a = bucket(1.05, BH, CYAN, "11", (0.0, 0.75), bits_size=FS_BODY)
        p11b = bucket(1.05, BH, CYAN, "11", (0.75, 1.0), bits_size=FS_BODY)
        VGroup(p11a, p11b).arrange(RIGHT, buff=0.1).move_to(finals[3])
        partial_tag = label("partial coverage", size=FS_SMALL, color=FLARE)
        partial_tag.next_to(VGroup(p11a, p11b), DOWN, buff=0.16)
        re_e = []
        for m, tgt in [(m01, p11a), (m11a, p11a), (m11b, p11b)]:
            e = e_r2_by[(3, id(m))]
            re_e.append(e.animate.put_start_and_end_on(
                m.get_bottom() + DOWN * 0.06, tgt.get_top() + UP * 0.06))
        self.pad_to(A("multiple partial buckets") - 0.4)
        self.play(*bucket_morph(finals[3], p11a), *bucket_morph(finals[3], p11b),
                  FadeOut(finals[3]), *re_e, FadeIn(partial_tag), run_time=1.1)
        self.add(p11a, p11b)

        # "partial rounds, touching only the unresolved profiles"
        f110 = bucket(1.05, BH, AMBER, "110", (0.0, 1.0))
        f111 = bucket(1.05, BH, CYAN, "111", (0.0, 1.0))
        f110.move_to(np.array([p11a.get_x(), ROW[2], 0]))
        f111.move_to(np.array([p11b.get_x(), ROW[2], 0]))
        e_r3 = VGroup(*[edge(pp, f, f[0].get_stroke_color())
                        for pp in (p11a, p11b) for f in (f110, f111)])
        r3 = mtex("R_3", size=FS_LABEL, color=MUT)   # only the unresolved profile
        r3.next_to(np.array([p11b.get_right()[0], (ROW[1] + ROW[2]) / 2, 0]), RIGHT,
                   buff=0.3)
        self.pad_to(A("partial rounds") - 0.3)
        self.play(LaggedStart(*[ShowCreation(e) for e in e_r3], lag_ratio=0.1),
                  *bucket_morph(p11a, f110), *bucket_morph(p11b, f110, bits=False),
                  *bucket_morph(p11a, f111), *bucket_morph(p11b, f111, bits=False),
                  FadeOut(partial_tag), FadeIn(r3), run_time=1.4)
        self.play(VGroup(p11a, p11b).animate.fade(0.5), run_time=0.5)

        # the jagged frontier edge
        self.pad_to(A("different depths") - 0.3)
        fy0 = ROW[1] - BH / 2 - 0.2
        fy1 = ROW[2] - BH / 2 - 0.2
        xs = (finals[2].get_right()[0] + p11a.get_left()[0]) / 2
        frontier = VMobject()
        frontier.set_points_as_corners([
            np.array([finals[0].get_left()[0] - 0.2, fy0, 0]),
            np.array([xs, fy0, 0]),
            np.array([xs, fy1, 0]),
            np.array([f111.get_right()[0] + 0.2, fy1, 0]),
        ])
        frontier.set_stroke(FLARE, SW, 0.95)
        depth_a = label("depth 2", size=FS_SMALL, color=FLARE)
        depth_a.next_to(np.array([finals[1].get_x(), fy0, 0]), DOWN, buff=0.12)
        depth_b = label("depth 3", size=FS_SMALL, color=FLARE)
        depth_b.next_to(np.array([(f110.get_x() + f111.get_x()) / 2, fy1, 0]), DOWN,
                        buff=0.12)
        self.play(ShowCreation(frontier), FadeIn(depth_a), FadeIn(depth_b), run_time=1.2)

        # prefix partition bar
        self.pad_to(A("prefix partition") - 0.3)
        bar_y = -2.42
        widths = [(0.0, 0.25, AMBER, "00"), (0.25, 0.5, CYAN, "01"),
                  (0.5, 0.75, AMBER, "10"), (0.75, 0.875, AMBER, "110"),
                  (0.875, 1.0, CYAN, "111")]
        BARW = 9.0
        BARX0 = -BARW / 2
        parts = VGroup()
        for x0, x1, c, bb in widths:
            rr = Rectangle(width=BARW * (x1 - x0) - 0.06, height=0.42)
            rr.set_fill(c, 0.35)
            rr.set_stroke(c, SW_THIN, 0.95)
            rr.move_to(np.array([BARX0 + BARW * (x0 + x1) / 2, bar_y, 0]))
            t = mtex(f'"{bb}"', size=FS_SMALL, color=c).move_to(rr)
            parts.add(VGroup(rr, t))
        self.play(LaggedStart(*[FadeIn(pp, shift=UP * 0.1) for pp in parts],
                              lag_ratio=0.12), run_time=1.3)
        cap = set_caption(label("a prefix partition of the field", size=FS_BODY,
                                color=TXT), rt=0.5)
        self.pad_to(A("no overlaps and no gaps") - 0.3)
        self.play(Indicate(parts, color=STAR, scale_factor=1.04), run_time=0.9)
        leaves5 = [finals[0], finals[1], finals[2], f110, f111]
        self.pad_to(AA(["covers the full epic", "covers the full epoch"]) - 0.4)
        self.play(LaggedStart(*[Indicate(f[-1], color=GOLD, scale_factor=1.5)
                                for f in leaves5], lag_ratio=0.1), run_time=1.1)

        # ---- grinding and the trust model ------------------------------------
        self.pad_to(A("adversarial question") - 0.4)
        title5 = scene_title("could someone grind one bucket full?")
        self.play(FadeOut(VGroup(frontier, depth_a, depth_b, parts)),
                  FadeOut(cap, shift=DOWN * 0.15),
                  swap_title(title4, title5),
                  VGroup(finals[0], finals[2], f110, f111).animate.fade(0.5),
                  VGroup(merged, e_r2, e_r3, p11a, p11b, r2, r3).animate.fade(0.6),
                  run_time=0.8)
        GY = -1.85
        adv = panel(1.9, 1.15, color=FLARE, fill_opacity=0.06)
        adv.move_to(np.array([-5.4, GY, 0]))
        adv_lab = label("grinder", size=FS_LABEL, color=FLARE).move_to(adv)
        self.play(ShowCreation(adv), FadeIn(adv_lab), run_time=0.7)
        self.pad_to(A("grind commitments") - 0.3)
        shots = VGroup(*[bead(FLARE, 0.1).move_to(adv.get_top()) for _ in range(3)])
        self.play(LaggedStart(*[s.animate.move_to(finals[1].get_center()
                                                  + 0.3 * (i - 1) * RIGHT + DOWN * 0.12)
                                for i, s in enumerate(shots)], lag_ratio=0.2),
                  run_time=1.1)
        self.pad_to(A("past capacity") - 0.3)
        self.play(VGroup(finals[1], shots).animate(rate_func=there_and_back).scale(1.18),
                  run_time=0.8)

        # "only if they can predict the discriminants" — the OSS glass
        self.pad_to(A("predict the discriminants") - 0.4)
        glass = panel(3.4, 1.5, color=CYAN, fill_opacity=0.18, stroke_opacity=0.95)
        glass.move_to(np.array([-1.75, GY, 0]))
        hidden = mtex('R_0 = thin ?', size=FS_HEAD, color=CYAN)
        hidden.move_to(glass.get_center() + UP * 0.28)
        g_lab = label("sampled privately by the OSS", size=FS_SMALL, color=CYAN)
        g_lab.move_to(glass.get_center() + DOWN * 0.38)
        self.play(ShowCreation(glass), FadeIn(hidden), FadeIn(g_lab),
                  FadeOut(shots), run_time=0.9)
        step = tex_chip('R_(j+1) = R_j + 1', color=STAR, size=FS_LABEL)
        step.next_to(glass, RIGHT, buff=0.35)
        self.pad_to(A("one each round") - 0.5)
        self.play(FadeIn(step, shift=LEFT * 0.15), run_time=0.7)
        self.pad_to(A("reveals it only after") - 0.2)
        cap = set_caption(rich([("$R_0$", GOLD), ("is revealed only after the epoch closes",
                                                  GOLD)], size=FS_BODY), rt=0.5)
        self.play(glass.animate.set_fill(CYAN, 0.04), run_time=0.4)

        # trust model
        t1 = label("bad discriminants: unbalanced, never unsound", size=FS_BODY,
                   color=TXT)
        t2 = label("soundness lives in the four checks", size=FS_BODY, color=GOLD)
        self.pad_to(A("cannot forge a split") - 0.4)
        cap = set_caption(t1, cap, rt=0.7)
        self.pad_to(A("four checks") - 0.3)
        cap = set_caption(t2, cap, rt=0.7)
        self.play(Indicate(icon, color=GOLD, scale_factor=1.25), run_time=0.8)
        self.pad_to(A("simply ignored") - 0.4)
        self.play(VGroup(adv, adv_lab).animate.fade(0.7), run_time=0.7)

        # scale check: 26 rounds of a 32-bit budget
        self.pad_to(A("address space suffice") - 0.4)
        sp = scale_parts()
        self.play(FadeOut(VGroup(glass, hidden, g_lab, step, adv, adv_lab, finals[0],
                                 finals[1], finals[2], f110, f111, p11a, p11b, merged,
                                 e_r2, e_r3, r2, r3, chain, links, slinks, chain_lab,
                                 icon)),
                  FadeOut(cap), swap_title(title5, sp.title), run_time=0.8)
        self.pad_to(A("address space suffice") + 0.5)
        self.play(FadeIn(sp.s1, shift=UP * 0.15), run_time=0.8)
        self.pad_to(A("60 million") - 0.6)
        self.play(FadeIn(sp.s2, shift=UP * 0.15), run_time=0.8)
        self.pad_to(A("26 rounds") - 0.6)
        self.play(FadeIn(sp.s2b, shift=UP * 0.15),
                  LaggedStart(*[FadeIn(c, scale=0.6) for c in sp.cells[:26]],
                              lag_ratio=0.08),
                  run_time=1.4)
        self.play(ShowCreation(sp.rounds_br), FadeIn(sp.rounds_lab), run_time=0.5)
        self.pad_to(A("32 bits") - 0.4)
        self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in sp.cells[26:]],
                              lag_ratio=0.15),
                  FadeIn(sp.s3, shift=UP * 0.1), run_time=0.8)
        self.pad_to(A("plenty of slack") - 0.3)
        self.play(ShowCreation(sp.slack_br), FadeIn(sp.slack_lab, shift=DOWN * 0.1),
                  Indicate(sp.s3, color=GOLD, scale_factor=1.08), run_time=0.8)
        self.pad_to(scene_T("5.4"))


class Scene55(TimedScene):
    """5.5 — The evidence tree."""

    def construct(self):
        A = lambda p, o=1: anchor("5.5", p, o)
        AA = lambda ps, o=1: anchor_any("5.5", ps, o)

        # continuity: open on 5.4's final frame (the scale check)
        sp = scale_parts()
        self.add(sp.title, sp.body)

        # "routing leaves one proof per final bucket"
        # A complete two-level rate-4 tree keeps the arity visible and exact.
        N_LEAF = 16
        LY = -2.15
        LY0 = -0.2          # the row first sits centre stage, then drops to make room
        leaves = VGroup(*[
            bucket(0.68, 0.56, (CYAN if i & 1 else AMBER), f"{i:04b}",
                   (0.0, 1.0), bits_size=FS_MIN)
            for i in range(N_LEAF)
        ])
        leaves.arrange(RIGHT, buff=0.12).move_to(np.array([0, LY, 0]))
        proofs = VGroup(*[proof_card(0.42).next_to(lv, UP, buff=0.12) for lv in leaves])
        # tree geometry, computed in the final layout
        MID_Y, ROOT_Y = 0.0, 1.75
        mids = VGroup(*[Circle(radius=0.2).set_stroke(STAR, SW_THIN, 0.95)
                        .set_fill(STAR, 0.1) for _ in range(4)])
        for k, m in enumerate(mids):
            m.move_to(np.array([leaves[4 * k:4 * k + 4].get_center()[0], MID_Y, 0]))
        root = Circle(radius=0.3).set_stroke(STAR, SW, 1.0)
        root.set_fill(STAR, 0.14)
        root.move_to(np.array([0, ROOT_Y, 0]))
        edges_lo = VGroup(*[Line(proofs[i].get_top(), mids[i // 4].get_bottom(), buff=0.06,
                                 stroke_width=SW_THIN, stroke_color=DIM)
                            for i in range(N_LEAF)])
        edges_lo2 = VGroup(*[Line(leaves[i].get_top(), mids[i // 4].get_bottom(), buff=0.06,
                                  stroke_width=SW_THIN, stroke_color=DIM)
                             for i in range(N_LEAF)])
        edges_hi = VGroup(*[Line(m.get_top(), root.get_bottom(), buff=0.06,
                                 stroke_width=SW_THIN, stroke_color=DIM)
                            for m in mids])
        row = VGroup(leaves, proofs)
        row.shift(UP * (LY0 - LY))

        title = scene_title("one proof per final bucket")
        self.wait(0.3)
        self.play(FadeOut(sp.body, shift=UP * 0.3), swap_title(sp.title, title),
                  LaggedStart(*[FadeIn(lv, shift=UP * 0.2) for lv in leaves],
                              lag_ratio=0.05),
                  run_time=0.9)
        self.pad_to(A("one proof per final bucket") - 0.3)
        self.play(LaggedStart(*[FadeIn(pp, scale=1.2) for pp in proofs], lag_ratio=0.08),
                  run_time=1.0)
        many = label("potentially millions of proofs per epoch", size=FS_BODY, color=FLARE)
        self.pad_to(A("millions") - 0.3)
        self.play(FadeIn(many.move_to(UP * CAPTION_Y), shift=UP * 0.15),
                  LaggedStart(*[Indicate(pp, color=FLARE, scale_factor=1.2)
                                for pp in proofs], lag_ratio=0.04), run_time=1.0)
        self.pad_to(A("one more fold") - 0.3)
        self.play(FadeOut(many, shift=DOWN * 0.15), run_time=0.5)

        # "gathers its final buckets into a Merkle tree — the evidence tree"
        self.pad_to(A("gathers") - 0.3)
        self.play(row.animate.shift(DOWN * (LY0 - LY)), run_time=0.9)
        self.play(ShowCreation(edges_lo), FadeIn(mids), run_time=0.9)
        self.pad_to(AA(["merkle tree", "a merkle tree"]) - 0.3)
        self.play(ShowCreation(edges_hi), FadeIn(root, scale=1.2), run_time=0.7)
        title2 = scene_title("the evidence tree", color=GOLD)
        self.pad_to(A("evidence tree") - 0.3)
        self.play(swap_title(title, title2), run_time=1.0)
        sponge = sponge_icon(1.2, 0.7).scale(1.3)
        sponge.move_to(np.array([-5.3, 1.75, 0]))
        arity = label("arity 4 = sponge rate", size=FS_SMALL, color=AMBER)
        arity.next_to(sponge, DOWN, buff=0.2)
        self.pad_to(A("poseidon hashes") - 0.3)
        self.play(FadeIn(sponge, scale=1.05), run_time=0.7)
        self.pad_to(AA(["arity forward", "arity four", "arity 4"]) - 0.2)
        self.play(FadeIn(arity), LaggedStart(*[Indicate(e, color=AMBER, scale_factor=1.0)
                                               for e in edges_lo[:4]], lag_ratio=0.1),
                  run_time=0.7)
        depth = mtex('2^26 "leaves" -> "depth" 13', size=FS_SMALL, color=MUT)
        depth.next_to(root, LEFT, buff=0.45).shift(UP * 0.15)
        self.play(FadeIn(depth), run_time=0.5)

        # "each leaf binds everything a query will need"
        card = panel(3.3, 2.0, color=STAR, fill_opacity=0.04)
        card.move_to(np.array([4.95, 1.75, 0]))
        card_h = label("each leaf binds", size=FS_SMALL, color=MUT)
        card_h.next_to(card.get_top(), DOWN, buff=0.15)
        fields = VGroup(
            mtex('e, quad s_("in"), s_("out")', size=FS_LABEL, color=TXT),
            mtex('R_0, quad (j, b)', size=FS_LABEL, color=TXT),
            mtex('"Com"(q_b)', size=FS_LABEL, color=GOLD),
        )
        fields.arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        fields.next_to(card_h, DOWN, buff=0.18)
        hl = leaves[15][0].copy().set_stroke(GOLD, SW, 1.0).set_fill(opacity=0)
        zoom = DashedLine(proofs[15].get_top() + UP * 0.05, card.get_bottom() + RIGHT * 0.6,
                          stroke_width=SW_THIN, stroke_color=MUT)
        self.pad_to(A("each leaf binds") - 0.3)
        self.play(ShowCreation(card), FadeIn(card_h), ShowCreation(hl),
                  ShowCreation(zoom), run_time=0.8)
        self.pad_to(A("both sentinels") - 0.6)
        self.play(FadeIn(fields[0], shift=LEFT * 0.15), run_time=0.7)
        self.pad_to(A("starting discriminant") - 0.3)
        self.play(FadeIn(fields[1], shift=LEFT * 0.15), run_time=0.7)
        self.pad_to(A("buckets polynomial") - 0.7)
        self.play(FadeIn(fields[2], shift=LEFT * 0.15), run_time=0.7)

        # "one folded proof... throw the routing proofs away"
        fold = proof_card(0.85).next_to(root, RIGHT, buff=0.35)
        self.pad_to(A("one folded proof") - 0.2)
        self.play(TransformFromCopy(proofs, fold), run_time=1.4)
        self.pad_to(A("routing proofs away") - 0.3)
        self.play(FadeOut(proofs), Transform(edges_lo, edges_lo2), FadeOut(zoom),
                  run_time=0.9)
        self.pad_to(A("single authenticated root") - 0.3)
        self.play(Indicate(root, color=GOLD, scale_factor=1.3), run_time=0.9)

        # ---- queries ---------------------------------------------------------
        self.pad_to(A("queries become small") - 0.3)
        self.play(FadeOut(VGroup(card, card_h, fields, hl, sponge, arity, depth)),
                  run_time=0.6)

        # membership: authenticate a leaf, open at the value: zero
        mem = label("membership", size=FS_BODY, color=CYAN)
        mem.move_to(np.array([-4.9, 2.05, 0]))
        q1 = bead(CYAN, 0.13).next_to(mem, DOWN, buff=0.3)
        self.pad_to(A("membership") - 0.2)
        self.play(FadeIn(mem), FadeIn(q1, scale=1.5), run_time=0.7)
        path1 = VGroup(edges_lo[2], edges_hi[0])
        self.pad_to(A("authenticate any leaf") - 0.2)
        self.play(q1.animate.next_to(leaves[2], UP, buff=0.14),
                  path1.animate.set_stroke(CYAN, SW_BOLD, 1.0),
                  mids[0].animate.set_stroke(CYAN, SW, 1.0),
                  leaves[2][0].animate.set_stroke(CYAN, SW, 1.0),
                  run_time=1.0)
        open0 = rich([("$q_b (x) = 0$", CYAN), ("present", CYAN)], size=FS_BODY, buff=0.35)
        self.pad_to(A("value zero") - 0.4)
        self.play(FadeIn(open0.move_to(UP * CAPTION_Y), shift=UP * 0.15), run_time=0.7)
        noaddr = label("no address check needed", size=FS_LABEL, color=MUT)
        noaddr.move_to(np.array([-4.9, 1.35, 0]))
        self.pad_to(A("no address check") - 0.2)
        self.play(FadeIn(noaddr), run_time=0.6)
        self.pad_to(A("whichever bucket holds") - 0.4)
        self.play(Indicate(leaves[2], color=CYAN, scale_factor=1.12), run_time=0.8)

        # non-membership: derive the profile, check it selects the leaf
        self.pad_to(A("non membership") - 0.2)
        nmem = label("non-membership: the nullifier's question", size=FS_BODY, color=GOLD)
        nmem.move_to(np.array([0, 2.05, 0])).align_to(np.array([-6.5, 0, 0]), LEFT)
        fit_width(nmem, 5.6)
        nf = bead(FLARE, 0.13).move_to(np.array([-5.2, 1.3, 0]))
        nftag = mtex('"nf"', size=FS_LABEL, color=FLARE).next_to(nf, LEFT, buff=0.15)
        self.play(path1.animate.set_stroke(DIM, SW_THIN, 1.0),
                  mids[0].animate.set_stroke(STAR, SW_THIN, 0.95),
                  leaves[2][0].animate.set_stroke(CYAN, SW_THIN, 0.95),
                  FadeOut(VGroup(open0, noaddr, mem, q1)),
                  FadeIn(nmem), FadeIn(nf, scale=1.5), FadeIn(nftag), run_time=0.7)
        dbits = VGroup(*[mtex(f'"{bb}"', size=FS_BODY, color=(CYAN if bb == "1" else AMBER))
                         for bb in "1011"])
        dbits.arrange(RIGHT, buff=0.14).next_to(nf, RIGHT, buff=0.35)
        dnote = rich([("profile from", MUT), ("$R_0$", MUT)], size=FS_SMALL, buff=0.1)
        dnote.next_to(dbits, RIGHT, buff=0.35)
        self.pad_to(AA(["derive your elements profile", "derive your element"]) - 0.2)
        self.play(LaggedStart(*[FadeIn(m, scale=1.4) for m in dbits], lag_ratio=0.2),
                  FadeIn(dnote), run_time=1.0)
        path2 = VGroup(edges_lo[11], edges_hi[2])
        self.pad_to(A("selects this very leaf") - 0.3)
        self.play(nf.animate.next_to(leaves[11], UP, buff=0.14),
                  nftag.animate.next_to(leaves[11], UP, buff=0.1).shift(LEFT * 0.45),
                  FadeOut(dnote),
                  path2.animate.set_stroke(GOLD, SW_BOLD, 1.0),
                  mids[2].animate.set_stroke(GOLD, SW, 1.0),
                  leaves[11][0].animate.set_stroke(GOLD, SW, 1.0),
                  run_time=1.1)
        openn = rich([("$q_b (\"nf\") != 0$", GOLD), ("absent from this bucket", GOLD)],
                     size=FS_BODY, buff=0.35)
        self.pad_to(A("open non zero") - 0.2)
        self.play(FadeIn(openn.move_to(UP * CAPTION_Y), shift=UP * 0.15), run_time=0.7)
        upg = rich([("absent from this bucket", TXT), ("$=>$", GOLD),
                    ("absent from the epoch", STAR)], size=FS_BODY, buff=0.3)
        self.pad_to(A("upgrades") - 0.3)
        self.play(FadeOut(openn, shift=DOWN * 0.15),
                  FadeIn(upg.move_to(UP * CAPTION_Y), shift=UP * 0.15), run_time=0.8)

        # ---- the before/after cost cards -------------------------------------
        self.pad_to(A("before and after") - 0.3)
        title3 = scene_title("epoch-wide exclusion, before and after")
        tree = VGroup(leaves, mids, root, edges_lo, edges_hi, fold)
        self.play(FadeOut(VGroup(nmem, upg, nf, nftag, dbits, tree)),
                  swap_title(title2, title3), run_time=1.0)
        CW, CH, CY = 5.7, 3.9, -0.05
        before = panel(CW, CH, color=FLARE, fill_opacity=0.05).move_to(np.array([-3.15, CY, 0]))
        after = panel(CW, CH, color=GOLD, fill_opacity=0.05).move_to(np.array([3.15, CY, 0]))
        bh = label("before: one epoch polynomial", size=FS_LABEL, color=MUT)
        b1 = mtex('"deg" e = 4.8 times 10^8', size=FS_HEAD, color=FLARE)
        b2 = mtex('16 "minutes"', size=72, color=FLARE)
        b3 = label("per evaluation", size=FS_BODY, color=FLARE)
        bcol = VGroup(bh, b1, b2, b3).arrange(DOWN, buff=0.3).move_to(before)
        ah = label("after: the evidence tree", size=FS_LABEL, color=MUT)
        a1 = mtex('<= 13 "Poseidon hashes"', size=FS_HEAD, color=GOLD)
        a2 = mtex('+ 1', size=72, color=GOLD)
        a3 = label("bounded opening", size=FS_BODY, color=GOLD)
        acol = VGroup(ah, a1, a2, a3).arrange(DOWN, buff=0.3).move_to(after)
        arr = tarrow(before.get_right(), after.get_left(), color=STAR, width=SW)
        self.pad_to(A("half a billion") - 1.2)
        self.play(ShowCreation(before), FadeIn(bh), FadeIn(b1), run_time=0.9)
        self.pad_to(A("16 minutes") - 0.3)
        self.play(FadeIn(b2, scale=1.2), FadeIn(b3), run_time=0.7)
        self.pad_to(A("13 poseidon hashes") - 0.3)
        self.play(ShowCreation(arr), ShowCreation(after), FadeIn(ah), FadeIn(a1),
                  run_time=0.8)
        self.pad_to(A("bounded opening") - 0.3)
        self.play(FadeIn(a2, scale=1.2), FadeIn(a3), run_time=0.7)
        shared = label("routed once, in flight, by a service; shared by every query",
                       size=FS_LABEL, color=CYAN)
        self.pad_to(AA(["heavy roading", "heavy routing"]) - 0.3)
        self.play(FadeIn(shared.move_to(UP * CAPTION_Y), shift=UP * 0.15), run_time=0.8)
        self.pad_to(AA(["sub linear exclusion", "sublinear exclusion"]) - 0.4)
        final = scene_title("sublinear exclusion", color=GOLD)
        self.play(swap_title(title3, final),
                  Indicate(after, color=GOLD, scale_factor=1.04), run_time=1.1)
        self.pad_to(scene_T("5.5"))

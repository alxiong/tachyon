"""Act 2 — nullifiers that evolve. Anchored to anim/words.json timestamps.

Render:  manimgl act2.py Scene21 Scene22 Scene23 -w

Layout (style.py bands): title band on top, stage in the middle, caption band at
the bottom. The epoch axis lives in the lower stage (AX_Y) in 2.1/2.2; in 2.3 the
wallet / service / quotient rows share epoch columns COL(i), so "same epoch"
always means "same column".
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manimlib import *
from style import *


# ---- act-local vocabulary ----------------------------------------------------

AX_Y = -2.05          # epoch axis baseline (2.1, 2.2)
AX_X0 = -5.25
AX_DX = 1.5
BEAD_R = 0.13


def epoch_axis(n=8):
    """Epoch axis: a line, ticks, e_i labels below, bead slots above."""
    xs = [AX_X0 + i * AX_DX for i in range(n)]
    line = Line(np.array([xs[0] - 0.6, AX_Y, 0]), np.array([xs[-1] + 0.6, AX_Y, 0]),
                stroke_width=SW_THIN, stroke_color=DIM)
    ticks = VGroup(*[Line(np.array([x, AX_Y - 0.08, 0]), np.array([x, AX_Y + 0.08, 0]),
                          stroke_width=SW_THIN, stroke_color=DIM) for x in xs])
    labels = VGroup(*[mtex(f"e_{i}", size=FS_SMALL, color=MUT)
                      .move_to(np.array([x, AX_Y - 0.4, 0])) for i, x in enumerate(xs)])
    slots = [np.array([x, AX_Y + 0.33, 0]) for x in xs]
    return VGroup(line, ticks), labels, slots


def actor(name, color, w=3.7, h=2.25):
    """A role panel with its name inside, at the top."""
    box = panel(w, h, color=color, fill_opacity=0.06)
    tag = label(name, size=FS_LABEL, color=color)
    tag.move_to(box.get_top() + DOWN * 0.34)
    return VGroup(box, tag)


def sponge(color=AMBER):
    """Poseidon sponge: a body with absorb waves, name underneath."""
    body = RoundedRectangle(width=1.9, height=1.1, corner_radius=0.14)
    body.set_fill(color, 0.10)
    body.set_stroke(color, SW, 0.9)
    waves = VGroup(*[Line(body.get_left() + RIGHT * 0.3 + UP * dy,
                          body.get_right() + LEFT * 0.3 + UP * dy,
                          stroke_width=SW_THIN, stroke_color=color, stroke_opacity=0.6)
                     for dy in (-0.24, 0.0, 0.24)])
    tag = label("Poseidon", size=FS_SMALL, color=color).next_to(body, DOWN, buff=0.14)
    return VGroup(body, waves, tag)


def derive_pipeline():
    """nk, psi -> Poseidon -> mk, the wallet-side derivation (2.2, reused in 2.3)."""
    sp = sponge().move_to(LEFT * 3.0 + UP * 0.55)
    nk = tex_chip('"nk"', color=GOLD, size=FS_LABEL).move_to(LEFT * 5.6 + UP * 1.05)
    psi = tex_chip('psi', color=GOLD, size=FS_LABEL).move_to(LEFT * 5.6 + UP * 0.05)
    mk = tex_chip('"mk"', color=AMBER, size=FS_BODY).move_to(LEFT * 0.75 + UP * 0.68)
    a1 = tarrow(nk, sp[0], color=GOLD)
    a2 = tarrow(psi, sp[0], color=GOLD)
    a3 = tarrow(sp[0], mk, color=AMBER)
    who = label("in the wallet", size=FS_LABEL, color=GOLD)
    who.move_to(LEFT * 3.0 + UP * 1.75)
    return VGroup(nk, psi, sp, mk, a1, a2, a3, who)


def oss_box():
    """The service's inbox: a cyan panel with its name on top."""
    box = panel(4.6, 3.15, color=CYAN, fill_opacity=0.05).move_to(RIGHT * 4.15 + UP * 0.3)
    tag = label("syncing service (OSS)", size=FS_LABEL, color=CYAN)
    tag.move_to(box.get_top() + DOWN * 0.34)
    return VGroup(box, tag)


def pair_chip(i, hexs, color=CYAN):
    return tex_chip(f'({i}, thick "{hexs}…")', color=color, size=FS_LABEL, pad=0.14)


PAIRS = [(3, "9f3c"), (4, "e071"), (5, "5bd2")]
DECOYS = [(3, "c84a"), (4, "1e9b"), (5, "7a06")]


def pair_column(items, x, color=CYAN):
    col = VGroup(*[pair_chip(i, h, color) for i, h in items])
    col.arrange(DOWN, buff=0.18).move_to(np.array([x, 0.05, 0]))
    return col


def broken_link(a, b):
    mid = (a + b) / 2
    l1 = Line(a, mid + LEFT * 0.2, stroke_width=SW, stroke_color=MUT)
    l2 = Line(mid + RIGHT * 0.2, b, stroke_width=SW, stroke_color=MUT)
    x = VGroup(Line(mid + 0.16 * UL, mid + 0.16 * DR, stroke_width=SW_BOLD, stroke_color=FLARE),
               Line(mid + 0.16 * UR, mid + 0.16 * DL, stroke_width=SW_BOLD, stroke_color=FLARE))
    return VGroup(l1, l2, x)


def strike_mark(mob, color=FLARE):
    """Deliberate strike-through, drawn as a polyline (not a Line) so the layout
    linter's line-crosses-text check doesn't flag it. Same look as cross_out()."""
    vm = VMobject()
    vm.set_points_as_corners([mob.get_corner(DL) + 0.08 * DL, mob.get_corner(UR) + 0.08 * UR])
    vm.set_stroke(color, 4, 1.0)
    return vm


def adopt(scene, group, mob):
    """group.add(mob) for a mob that is already on screen at top level.

    Without removing the top-level entry the scene draws `mob` twice (once on
    its own, once as part of `group`), which doubles translucent fills/strokes:
    a dimmed tile then looks undimmed, a 0.75-fill square looks brighter."""
    group.add(mob)
    drawn = any(group in m.get_family() for m in scene.mobjects if m is not mob)
    if drawn and mob in scene.mobjects:
        scene.mobjects.remove(mob)


def crack(box, color=FLARE):
    """A zigzag fracture down the middle of `box` (polyline: the linter ignores it)."""
    top, bot = box.get_top() + DOWN * 0.06, box.get_bottom() + UP * 0.06
    n = 7
    pts = [top + (bot - top) * k / n + RIGHT * (0.09 if k % 2 else -0.09) * (0 < k < n)
           for k in range(n + 1)]
    vm = VMobject()
    vm.set_points_as_corners(pts)
    vm.set_stroke(color, SW, 1.0)
    return vm


def dimmed(mob, k):
    """Copy of `mob` with every fill/stroke opacity scaled by k (fade() is absolute
    in manimgl and would turn translucent panels into slabs)."""
    t = mob.copy()
    for a, b in zip(mob.get_family(), t.get_family()):
        if a.has_points():
            b.set_fill(opacity=min(1.0, a.get_fill_opacity() * k))
            b.set_stroke(opacity=min(1.0, a.get_stroke_opacity() * k))
    return t


# ---- 2.3 grid: epoch columns shared by the wallet / service / quotient rows ----

COL_X0 = -4.3
COL_DX = 0.78
ROW_W = 1.25         # wallet row y
ROW_S = 0.15         # service row y
ROW_Q = -0.95        # quotient row y
IDX_Y = 1.9          # epoch index row y (the title band sits above it)
LBL_X = -5.05        # right edge of the row labels


def COL(i, y):
    return np.array([COL_X0 + i * COL_DX, y, 0])


def ftile(i, color):
    box = RoundedRectangle(width=0.66, height=0.62, corner_radius=0.08)
    box.set_fill(color, 0.12)
    box.set_stroke(color, SW_THIN, 0.9)
    t = mtex(f"F_({i})", size=29, color=color).move_to(box)
    return VGroup(box, t)


def row_label(tex, color, y, math=True):
    m = mtex(tex, size=FS_BODY, color=color) if math else label(tex, size=FS_BODY, color=color)
    m.move_to(np.array([0, y, 0])).align_to(np.array([LBL_X, 0, 0]), RIGHT)
    return m


def range_band(i0, i1, y, color):
    w = (i1 - i0) * COL_DX + 0.62
    band = RoundedRectangle(width=w, height=0.56, corner_radius=0.28)
    band.set_fill(color, 0.10)
    band.set_stroke(color, SW_THIN, 0.6)
    band.move_to((COL(i0, y) + COL(i1, y)) / 2)
    return band


# ==============================================================================

class Scene21(TimedScene):
    """2.1 — Why one nullifier per note has to go."""

    def construct(self):
        A = lambda p, o=1: anchor("2.1", p, o)
        AA = lambda ps, o=1: anchor_any("2.1", ps, o)

        # "remember the deal": validator window + wallet proof, at stage top
        validator = actor("validator", FLARE).move_to(LEFT * 4.6 + UP * 1.3)
        vrow = VGroup(*[Square(side_length=0.36).set_fill(FLARE, 0.75)
                        .set_stroke(AMBER, 1.0, 0.5) for _ in range(6)])
        vrow.arrange(RIGHT, buff=0.1).move_to(validator[0].get_center() + DOWN * 0.25)
        wallet = actor("wallet", GOLD).move_to(UP * 1.3)
        token = proof_token(0.26).move_to(wallet[0].get_center() + DOWN * 0.22)
        # The three role panels hold the centre of the stage, enlarged, until the
        # chain arrives below them ("hits the chain"); then they shrink back and
        # rise to their working size/position (y = 1.3) to make room.
        RISE, K = 1.3, 1.12
        vg, wg = VGroup(validator, vrow), VGroup(wallet, token)
        # until the service exists, the pair is centred; it slides left for the OSS
        SLIDE = 2.3
        for g in (vg, wg):
            g.scale(K).shift(DOWN * RISE + RIGHT * SLIDE)
        self.wait(0.5)
        self.play(LaggedStart(FadeIn(vg, shift=UP * 0.2), FadeIn(wg, shift=UP * 0.2),
                              lag_ratio=0.35), run_time=1.3)
        add_shimmer(vrow, amp=0.22, speed=1.8)

        deal = rich([("consensus keeps a window,", FLARE), ("you keep a proof", GOLD)])
        deal.move_to(UP * CAPTION_Y)
        self.pad_to(A("consensus keeps a window") - 0.25)
        self.play(FadeIn(deal[0], shift=UP * 0.15),
                  Indicate(vrow, color=FLARE, scale_factor=1.08), run_time=0.7)
        self.pad_to(A("you keep a proof") - 0.25)
        self.play(FadeIn(deal[1], shift=UP * 0.15),
                  Indicate(token, color=GOLD, scale_factor=1.2), run_time=0.7)

        # "refreshing every time a block lands": the window rolls (oldest pruned),
        # and the wallet's proof ticks along with it
        self.pad_to(A("refreshing every time") - 0.25)
        clear_shimmer(vrow)
        step = vrow[1].get_x() - vrow[0].get_x()
        for _ in range(2):
            new = vrow[0].copy().move_to(vrow[-1].get_center() + RIGHT * step).set_opacity(0)
            old = vrow[0]
            self.play(FadeOut(old, shift=LEFT * 0.2),
                      VGroup(*vrow[1:]).animate.shift(LEFT * step),
                      new.animate.set_fill(FLARE, 0.75).set_stroke(AMBER, 1.0, 0.5)
                      .shift(LEFT * step),
                      Indicate(token, color=AMBER, scale_factor=1.15), run_time=0.75)
            vrow.remove(old)
            adopt(self, vrow, new)
        add_shimmer(vrow, amp=0.22, speed=1.8)

        # "your phone is not going to track the chain around the clock"
        zzz = label("z z z", size=FS_BODY, color=MUT)
        zzz.next_to(wallet[0], UR, buff=-0.25).shift(UP * 0.35)
        self.pad_to(A("around the clock") - 1.0)
        self.play(FadeIn(zzz, shift=UP * 0.2), Transform(token, dimmed(token, 0.35)), run_time=0.8)

        # "hand the refresh work to a service ... an OSS"
        oss = actor("syncing service (OSS)", CYAN).move_to(RIGHT * 4.6 + UP * 1.3)
        oss.scale(K).shift(DOWN * RISE)
        self.pad_to(A("outsource") - 0.35)
        self.play(FadeOut(deal), VGroup(vg, wg, zzz).animate.shift(LEFT * SLIDE),
                  FadeIn(oss, shift=LEFT * 0.6), run_time=1.0)
        self.pad_to(A("syncing service") - 0.25)
        self.play(Indicate(oss[1], color=CYAN, scale_factor=1.1), run_time=0.6)

        # "but watch what the service needs": the question goes up as a title
        q1 = scene_title("what does the service need to know?")
        self.pad_to(AA(["watch what the service needs", "watch what"]) - 0.2)
        self.play(FadeIn(q1, shift=DOWN * 0.15), run_time=0.8)

        # "it must know the nullifier": the bead travels, and is remembered
        nf = bead(FLARE, BEAD_R).move_to(token)
        nf_tag = mtex('"nf"', size=FS_LABEL, color=FLARE).next_to(nf, RIGHT, buff=0.15)
        nfg = VGroup(nf, nf_tag)
        self.pad_to(A("know the nullifier") - 1.0)
        self.play(FadeIn(nfg, scale=1.5), run_time=0.6)
        self.play(nfg.animate.move_to(oss[0].get_center() + DOWN * 0.25), run_time=1.0)
        self.pad_to(A("one time globally unique") - 0.25)
        self.play(Indicate(nfg, color=FLARE, scale_factor=1.25), run_time=0.7)

        # "the moment your spend hits the chain ... that one's mine"
        axis, ax_labels, slots = epoch_axis()
        self.pad_to(A("hits the chain") - 1.0)
        self.play(vg.animate.scale(1 / K).shift(UP * RISE),
                  VGroup(wallet, token, zzz).animate.scale(1 / K, about_point=wallet[0].get_center())
                  .shift(UP * RISE),
                  VGroup(oss, nfg).animate.scale(1 / K, about_point=oss[0].get_center())
                  .shift(UP * RISE),
                  ShowCreation(axis), FadeIn(ax_labels, lag_ratio=0.05), run_time=1.2)
        token_lit = proof_token(0.26).move_to(token)
        spent = bead(FLARE, BEAD_R).move_to(slots[5])
        self.play(FadeIn(spent, scale=2.0), run_time=0.5)
        trace = DashedLine(nf.get_center() + DOWN * 0.18, spent.get_center() + UP * 0.18,
                           stroke_color=FLARE, stroke_width=SW)
        mine = label("“that one's mine”", size=FS_BODY, color=FLARE)
        mine.next_to(trace.get_center(), LEFT, buff=0.35)
        self.play(ShowCreation(trace), run_time=0.8)
        self.pad_to(A("points and says") - 0.2)
        self.play(FadeIn(mine, shift=RIGHT * 0.2), run_time=0.6)
        donated = caption("outsourced your sync, donated your privacy", color=FLARE)
        self.pad_to(A("donated your privacy") - 0.4)
        self.play(FadeIn(donated, shift=UP * 0.15),
                  Indicate(mine, color=FLARE, scale_factor=1.1), run_time=0.8)

        # "think about what property we'd want instead"
        self.pad_to(A("what property") - 0.5)
        q2 = scene_title("what property do we want instead?")
        self.play(FadeOut(VGroup(trace, mine, spent, nfg, zzz, donated)),
                  FadeTransform(q1, q2), Transform(token, token_lit), run_time=0.9)
        y_mid = -0.35
        handed = bead(CYAN, BEAD_R).move_to(np.array([2.6, y_mid, 0]))
        h_tag = label("checked by the service", size=FS_LABEL, color=CYAN)
        h_tag.next_to(handed, DOWN, buff=0.22)
        revealed = bead(GOLD, BEAD_R).move_to(np.array([-2.6, y_mid, 0]))
        r_tag = label("published at spend", size=FS_LABEL, color=GOLD)
        r_tag.next_to(revealed, DOWN, buff=0.22)
        self.pad_to(A("checks on your behalf") - 0.6)
        # beads are emitted from their owner (a panel -> dot morph smears a slab)
        seed = handed.copy().scale(0.5).move_to(oss[0]).set_opacity(0)
        self.play(ReplacementTransform(seed, handed), FadeIn(h_tag), run_time=0.8)
        self.pad_to(A("eventually publish") - 0.5)
        seed = revealed.copy().scale(0.5).move_to(token).set_opacity(0)
        self.play(ReplacementTransform(seed, revealed), FadeIn(r_tag), run_time=0.8)
        # each bead sits on its owner's side: the service's under the OSS, the spent one
        # under the wallet (short, direct emission paths)
        bl = broken_link(revealed.get_center() + RIGHT * 0.3, handed.get_center() + LEFT * 0.3)
        self.pad_to(AA(["connectable", "shouldn't be"]) - 0.4)
        self.play(ShowCreation(bl[0]), ShowCreation(bl[1]), run_time=0.5)
        self.play(ShowCreation(bl[2]), run_time=0.4)
        same_note = caption("…but both must refer to the same note")
        self.pad_to(A("same note") - 0.6)
        self.play(FadeIn(same_note, shift=UP * 0.15), run_time=0.7)

        # "one note, many nullifier values, one per epoch"
        self.pad_to(A("one note") - 0.7)
        psi = tex_chip('"note" thick psi', color=GOLD, size=FS_BODY).move_to(UP * (y_mid - 0.2))
        self.play(FadeOut(VGroup(handed, h_tag, revealed, r_tag, bl, same_note)),
                  FadeIn(psi, scale=1.15), run_time=0.7)
        beads = VGroup(*[bead(FLARE, BEAD_R).move_to(s) for s in slots])
        one_many = rich([("one note,", GOLD), ("many nullifiers,", FLARE),
                         ("one per epoch", TXT)])
        one_many.move_to(UP * CAPTION_Y)
        self.pad_to(A("many nullifier values") - 0.3)
        # each epoch's value is emitted by the note: small seeds leave the chip
        # and settle onto their epoch slots (a dot-to-dot morph, no shape scribble)
        seeds = [b.copy().scale(0.4).move_to(psi).set_opacity(0) for b in beads]
        self.play(LaggedStart(*[Transform(sd, b) for sd, b in zip(seeds, beads)],
                              lag_ratio=0.1),
                  Indicate(psi, color=GOLD, scale_factor=1.06),
                  FadeIn(one_many[:2], shift=UP * 0.15), run_time=1.6)
        self.remove(*seeds)
        self.add(beads)
        self.pad_to(AA(["one per epoch", "one per epic"]) - 0.2)
        self.play(FadeIn(one_many[2], shift=UP * 0.15),
                  LaggedStart(*[Indicate(l, color=STAR, scale_factor=1.25) for l in ax_labels],
                              lag_ratio=0.06), run_time=1.0)
        add_shimmer(beads, amp=0.2)
        self.pad_to(A("nothing about the rest") - 0.3)
        self.play(FadeOut(psi), run_time=0.6)

        # "the epochs you delegate" vs "a value it has never seen"
        self.pad_to(AA(["you delegate", "delegate"]) - 0.5)
        deleg = VGroup(*beads[1:5])
        br = bracket(deleg, color=CYAN, buff=0.2)
        br_tag = label("delegated to the service", size=FS_LABEL, color=CYAN)
        br_tag.next_to(br, UP, buff=0.12)
        self.play(GrowFromCenter(br), FadeIn(br_tag, shift=DOWN * 0.1),
                  *[b.animate.set_fill(CYAN) for b in deleg], run_time=0.8)
        self.pad_to(A("never seen") - 0.6)
        ring = Circle(radius=0.26).set_stroke(GOLD, SW, 1.0).move_to(beads[6])
        unseen = label("spent with this one", size=FS_LABEL, color=GOLD)
        unseen.move_to(np.array([beads[6].get_x(), br_tag.get_y(), 0]))
        self.play(ShowCreation(ring), FadeIn(unseen, shift=DOWN * 0.1),
                  beads[6].animate.set_fill(GOLD), run_time=0.8)

        # "the heart of Tachyon" + the broken invariant
        self.pad_to(A("the heart") - 0.6)
        title = scene_title("evolving nullifiers", color=GOLD)
        clear_shimmer(vrow)   # a live shimmer updater would hold the squares lit mid-fade
        self.play(FadeOut(VGroup(validator, vrow, wallet, token, oss, one_many)),
                  FadeTransform(q2, title), run_time=1.2)
        banner = boxed(mtex('1 "note" = 1 "nullifier"', size=FS_HEAD, color=STAR),
                       color=STAR, pad=0.3, fill=0.06)
        banner.move_to(LEFT * 3.2 + UP * 0.9)
        since = label("since Zerocash", size=FS_LABEL, color=MUT)
        since.next_to(banner, UP, buff=0.2)
        self.pad_to(AA(["zero cash", "since zero"]) - 0.3)
        self.play(FadeIn(since, shift=DOWN * 0.1), run_time=0.6)
        self.pad_to(AA(["one invariant", "invariant"]) - 0.4)
        self.play(FadeIn(banner, scale=1.08), run_time=0.7)
        self.pad_to(A("break the invariant") - 0.2)
        strike = strike_mark(banner)
        self.play(ShowCreation(strike), Transform(banner, dimmed(banner, 0.5)), run_time=0.9)

        # "two debts": IOUs that the rest of the video pays
        self.pad_to(A("two debts") - 0.3)
        debts = bullets([("debt 1: a new derivation", AMBER),
                         ("debt 2: a new double-spend rule", AMBER)],
                        size=FS_BODY, mark_color=AMBER, buff=0.4)
        debts.move_to(RIGHT * 3.3 + UP * 0.9)
        self.pad_to(AA(["a derivation", "derivation"]) - 0.3)
        self.play(FadeIn(debts[0], shift=LEFT * 0.3), run_time=0.7)
        self.pad_to(AA(["double spend rule", "spend rule"]) - 0.4)
        self.play(FadeIn(debts[1], shift=LEFT * 0.3), run_time=0.7)
        pays = caption("the rest of this video pays them", color=TXT)
        self.pad_to(A("pays those debts") - 0.6)
        self.play(FadeIn(pays, shift=UP * 0.15),
                  Indicate(debts, color=GOLD, scale_factor=1.05), run_time=0.9)
        self.pad_to(scene_T("2.1"))


class Scene22(TimedScene):
    """2.2 — The derivation."""

    def construct(self):
        A = lambda p, o=1: anchor("2.2", p, o)
        AA = lambda ps, o=1: anchor_any("2.2", ps, o)

        # Reconstruct 2.1's final idea; the derivation grows out of its first debt.
        title = scene_title("evolving nullifiers", color=GOLD)
        axis, ax_labels, slots = epoch_axis()
        beads = VGroup(*[bead(FLARE, BEAD_R).move_to(s) for s in slots])
        debts = bullets([("debt 1: a new derivation", AMBER),
                         ("debt 2: a new double-spend rule", AMBER)],
                        size=FS_BODY, mark_color=AMBER, buff=0.4)
        debts.move_to(RIGHT * 3.3 + UP * 0.9)
        # 2.1's leftovers, so the cut is seamless; they clear on the first beat
        for i in range(1, 5):
            beads[i].set_fill(CYAN)
        beads[6].set_fill(GOLD)
        br = bracket(VGroup(*beads[1:5]), color=CYAN, buff=0.2)
        br_tag = label("delegated to the service", size=FS_LABEL, color=CYAN)
        br_tag.next_to(br, UP, buff=0.12)
        ring = Circle(radius=0.26).set_stroke(GOLD, SW, 1.0).move_to(beads[6])
        unseen = label("spent with this one", size=FS_LABEL, color=GOLD)
        unseen.move_to(np.array([beads[6].get_x(), br_tag.get_y(), 0]))
        banner = boxed(mtex('1 "note" = 1 "nullifier"', size=FS_HEAD, color=STAR),
                       color=STAR, pad=0.3, fill=0.06)
        banner.move_to(LEFT * 3.2 + UP * 0.9)
        since = label("since Zerocash", size=FS_LABEL, color=MUT).next_to(banner, UP, buff=0.2)
        strike = strike_mark(banner)
        banner = dimmed(banner, 0.5)
        pays = caption("the rest of this video pays them", color=TXT)
        extras = VGroup(br, br_tag, ring, unseen, banner, since, strike, pays)
        self.add(title, axis, ax_labels, beads, debts, extras)
        self.wait(0.4)
        self.play(FadeOut(extras), *[b.animate.set_fill(FLARE) for b in beads], run_time=0.6)
        add_shimmer(beads, amp=0.25, speed=2.0)
        self.pad_to(A("derivation first") - 0.2)
        self.play(FadeOut(debts[1]), debts[0].animate.scale(1.15).move_to(UP * 0.7),
                  run_time=0.9)

        # "a keyed function": the debt becomes the ideal functionality
        formula = mtex('"nf"_e = "KDF"("nk", psi, e)', size=FS_HEAD + 18, color=STAR)
        formula.move_to(UP * 0.7)
        self.pad_to(A("keyed function") - 0.6)
        self.play(FadeOut(title, shift=UP * 0.2),
                  FadeTransform(debts[0], formula), run_time=1.1)
        self.pad_to(A("nullifier key psi") - 0.25)
        self.play(Indicate(formula, color=GOLD, scale_factor=1.05), run_time=0.6)

        # "deterministic, one value per epoch": two evaluations land on the same bead
        det = label("same inputs, same value: one per epoch", size=FS_LABEL, color=TXT)
        det.next_to(slots[2], UP, buff=0.45).set_x(slots[2][0] + 1.6)
        self.pad_to(A("deterministic") - 0.3)
        clear_shimmer(beads)
        self.play(*[b.animate.set_fill(FLARE, 0.3) for i, b in enumerate(beads) if i != 2],
                  run_time=0.4)
        # evaluate twice at the same epoch: both drops land on the same bead
        for _ in range(2):
            drop = Dot(radius=0.07).set_fill(STAR, 1.0).move_to(formula.get_bottom() + DOWN * 0.15)
            self.play(drop.animate(rate_func=rush_into).move_to(beads[2]), run_time=0.45)
            self.remove(drop)
            self.play(Flash(beads[2], color=FLARE, flash_radius=0.3), run_time=0.3)
        self.play(FadeIn(det, shift=DOWN * 0.1), run_time=0.5)

        # "pseudorandom, so values don't link"
        rnd = label("pseudorandom: values don't link", size=FS_LABEL, color=TXT)
        rnd.move_to(det)
        self.pad_to(A("pseudorandom") - 0.3)
        self.play(beads.animate.set_fill(FLARE, 0.95), FadeTransform(det, rnd), run_time=0.8)
        add_shimmer(beads, amp=0.35, speed=2.6)

        # "instantiates it with Poseidon ... per-note master key mk"
        pipe = derive_pipeline()
        nk, psi, sp, mk, a1, a2, a3, who = pipe
        # the pipeline is built centred on the stage; it slides left when the
        # service arrives on the right ("what does the service receive?")
        PIPE_DX = 3.0
        pipe.shift(RIGHT * PIPE_DX)
        self.pad_to(A("with poseidon") - 1.0)
        self.play(FadeOut(rnd), formula.animate.scale((FS_HEAD + 6) / (FS_HEAD + 18))
                  .move_to(UP * TITLE_Y), run_time=0.7)
        self.play(FadeIn(sp, scale=1.05), FadeIn(who), run_time=0.6)
        self.pad_to(A("hash the nullifier key") - 0.1)
        self.play(FadeIn(nk, shift=RIGHT * 0.2), FadeIn(psi, shift=RIGHT * 0.2), run_time=0.6)
        self.play(ShowCreation(a1), ShowCreation(a2),
                  run_time=0.6)
        self.pad_to(A("master key") - 0.3)
        self.play(ShowCreation(a3), FadeIn(mk, shift=RIGHT * 0.2, scale=1.2), run_time=0.7)

        # "one permutation squeezes a whole window ... rate 4, four epochs per squeeze"
        self.pad_to(A("one permutation") - 0.2)
        clear_shimmer(beads)
        self.play(FadeOut(beads), run_time=0.4)
        new_beads = VGroup(*[bead(FLARE, BEAD_R).move_to(s) for s in slots])
        for g in range(2):
            grp = new_beads[4 * g:4 * g + 4]
            starts = [b.copy().move_to(sp[0]).scale(0.5).set_opacity(0) for b in grp]
            self.play(sp[0].animate(rate_func=there_and_back).scale(0.9),
                      LaggedStart(*[Transform(s, b) for s, b in zip(starts, grp)],
                                  lag_ratio=0.12), run_time=1.1)
            self.remove(*starts)
            self.add(grp)
        rate_br = bracket(new_beads[:4], color=AMBER, buff=0.2)
        rate_tag = label("one squeeze, four epochs", size=FS_LABEL, color=AMBER)
        rate_tag.next_to(rate_br, UP, buff=0.12)
        self.pad_to(AA(["rate 4", "rate four"]) - 0.3)
        self.play(GrowFromCenter(rate_br), FadeIn(rate_tag, shift=DOWN * 0.1), run_time=0.8)
        add_shimmer(new_beads, amp=0.2, speed=2.0)
        cheap = caption("in circuit: about as cheap as a batch of nullifiers gets")
        self.pad_to(A("in circuit") - 0.2)
        self.play(FadeIn(cheap, shift=UP * 0.15), run_time=0.7)

        # "what does the service receive? bare pairs"
        ob = oss_box()
        self.pad_to(A("service receive") - 0.6)
        self.play(FadeOut(VGroup(rate_br, rate_tag, cheap)),
                  pipe.animate.shift(LEFT * PIPE_DX), FadeIn(ob, shift=LEFT * 0.3),
                  run_time=1.0)
        reals = pair_column(PAIRS, ob[0].get_x() + 1.05)
        self.pad_to(AA(["bare pairs", "bear pairs"]) - 0.6)
        # each value travels into the inbox as a bead, then unpacks into its pair
        # (a dot -> chip morph would smear the bead into a filled slab)
        flights = [new_beads[i].copy().clear_updaters() for i in (3, 4, 5)]
        self.play(LaggedStart(*[fl.animate.move_to(r) for fl, r in zip(flights, reals)],
                              lag_ratio=0.2), run_time=0.8)
        self.play(*[FadeOut(fl, scale=0.5) for fl in flights],
                  LaggedStart(*[FadeIn(r, scale=0.7) for r in reals], lag_ratio=0.15),
                  run_time=0.5)
        self.pad_to(A("an epic index") - 0.2)
        self.play(*[Indicate(r, color=STAR, scale_factor=1.06) for r in reals], run_time=0.6)

        # "no key material. no note. no evidence ..."
        nos = rich([("no key material,", MUT), ("no note,", MUT),
                    ("no evidence the values relate to anything", MUT)], size=FS_LABEL)
        nos.move_to(UP * CAPTION_Y)
        for k, ph in enumerate(["no key material", "no note", "no evidence"]):
            self.pad_to(A(ph) - 0.2)
            self.play(FadeIn(nos[k], shift=UP * 0.15), run_time=0.5)

        # "a genuine sync request and a list of decoys are indistinguishable"
        self.pad_to(A("genuine sync request") - 0.25)
        self.play(Indicate(reals, color=CYAN, scale_factor=1.04), run_time=0.7)
        decoys = pair_column(DECOYS, ob[0].get_x() - 1.05)
        q = label("?", size=FS_HEAD, color=CYAN).move_to(
            (decoys.get_right() + reals.get_left()) / 2)
        self.pad_to(A("list of decoys") - 0.4)
        self.play(LaggedStart(*[FadeIn(d, shift=RIGHT * 0.3) for d in decoys], lag_ratio=0.15),
                  run_time=0.9)
        self.pad_to(A("indistinguishable") - 0.2)
        self.play(FadeIn(q, scale=1.4), run_time=0.5)
        same = caption("real or decoy, the service does the same work", color=CYAN)
        self.pad_to(A("same work") - 0.5)
        self.play(FadeOut(nos), FadeIn(same, shift=UP * 0.15), run_time=0.7)

        # "the glue that binds ... comes later, on the wallet side"
        glue = caption("the binding to a real note happens later, in the wallet", color=GOLD)
        self.pad_to(A("glue that binds") - 0.35)
        self.play(FadeOut(same), FadeIn(glue, shift=UP * 0.15),
                  Indicate(who, color=GOLD, scale_factor=1.1), run_time=0.8)

        # "every evaluation you haven't revealed is indistinguishable from random"
        hidden = VGroup(*[new_beads[i] for i in (0, 1, 2, 6, 7)])
        clear_shimmer(new_beads)
        noise = caption("unrevealed values: indistinguishable from random", color=TXT)
        self.pad_to(A("every evaluation") - 0.3)
        self.play(FadeOut(glue), FadeIn(noise, shift=UP * 0.15),
                  *[b.animate.set_fill(DIM, 0.6) for b in hidden], run_time=0.9)
        add_shimmer(hidden, amp=0.6, speed=3.2)
        add_shimmer(VGroup(*[new_beads[i] for i in (3, 4, 5)]), amp=0.15)
        self.pad_to(A("delegation included") - 0.3)
        self.play(*[Indicate(new_beads[i], color=CYAN, scale_factor=1.4) for i in (3, 4, 5)],
                  Indicate(reals, color=CYAN, scale_factor=1.05), run_time=0.8)

        # "from here on: nf_e = f_mk(e)"
        short = mtex('"nf"_e = f_"mk" (e)', size=FS_HEAD + 6, color=STAR).move_to(UP * TITLE_Y)
        self.pad_to(A("from here on") - 0.3)
        self.play(FadeOut(noise), TransformMatchingShapes(formula, short), run_time=1.0)
        self.pad_to(AA(["f sub mk", "sub mk"]) - 0.2)
        self.play(Indicate(short, color=GOLD, scale_factor=1.08), run_time=0.7)
        self.pad_to(scene_T("2.2"))


class Scene23(TimedScene):
    """2.3 — The ranged nullifier commitment: indexed multisets from cubes."""

    def construct(self):
        A = lambda p, o=1: anchor("2.3", p, o)
        AA = lambda ps, o=1: anchor_any("2.3", ps, o)

        # Reconstruct the derivation's final frame.
        short = mtex('"nf"_e = f_"mk" (e)', size=FS_HEAD + 6, color=STAR).move_to(UP * TITLE_Y)
        axis, ax_labels, slots = epoch_axis()
        beads = VGroup(*[bead(FLARE if i in (3, 4, 5) else DIM, BEAD_R).move_to(s)
                         for i, s in enumerate(slots)])
        pipe = derive_pipeline()
        ob = oss_box()
        reals = pair_column(PAIRS, ob[0].get_x() + 1.05)
        decoys = pair_column(DECOYS, ob[0].get_x() - 1.05)
        self.add(short, axis, ax_labels, beads, pipe, ob, reals, decoys)
        self.wait(0.5)

        # "the wallet derives nullifiers, and the service tests them"
        self.pad_to(A("wallet derives") - 0.2)
        self.play(Indicate(pipe[3], color=GOLD, scale_factor=1.15), run_time=0.7)
        self.pad_to(A("tests them") - 0.4)
        self.play(Indicate(reals, color=CYAN, scale_factor=1.05), run_time=0.7)

        # "here's the gap": two rows on shared epoch columns
        idx = VGroup(*[mtex(str(i), size=FS_SMALL, color=MUT).move_to(COL(i, IDX_Y))
                       for i in range(10)])
        idx_l = row_label("epoch", MUT, IDX_Y, math=False).scale(FS_SMALL / FS_BODY)
        idx_l.align_to(np.array([LBL_X, 0, 0]), RIGHT)
        wl = row_label("wallet", GOLD, ROW_W, math=False)
        sl = row_label("service", CYAN, ROW_S, math=False)
        wbeads = VGroup(*[bead(GOLD, BEAD_R).move_to(COL(i, ROW_W)) for i in range(9)])
        sbeads = VGroup(*[bead(CYAN, BEAD_R).move_to(COL(i, ROW_S)) for i in range(2, 6)])
        # The real pairs stay: they become the service row. The e_i labels
        # become the epoch index row, the axis beads become the wallet row.
        gap_t = scene_title("the gap: an indexed containment")
        self.pad_to(A("the gap") - 0.6)
        self.play(FadeOut(VGroup(pipe, ob[0], ob[1], decoys)),
                  FadeTransform(short, gap_t), run_time=0.9)
        self.pad_to(A("range of epochs") - 1.2)
        wband = range_band(0, 8, ROW_W, GOLD)
        wtag = mtex("R", size=FS_BODY, color=GOLD).next_to(wband, RIGHT, buff=0.2)
        self.play(*[FadeTransform(ax_labels[i], idx[i]) for i in range(8)],
                  FadeIn(idx[8:]), FadeIn(idx_l), FadeIn(wl), FadeOut(axis),
                  ReplacementTransform(beads, VGroup(*wbeads[:8])),
                  FadeIn(wbeads[8], scale=1.5), run_time=1.2)
        self.play(FadeIn(wband), FadeIn(wtag), run_time=0.5)
        add_shimmer(wbeads, amp=0.22, speed=1.8)
        sband = range_band(2, 5, ROW_S, CYAN)
        stag = mtex("S", size=FS_BODY, color=CYAN).next_to(sband, RIGHT, buff=0.2)
        self.pad_to(A("sub range") - 0.6)
        self.play(FadeIn(sl), FadeIn(sbeads[0], scale=1.5),
                  LaggedStart(*[FadeTransform(reals[k], sbeads[k + 1])
                                for k in range(3)], lag_ratio=0.15),
                  FadeIn(sband), FadeIn(stag), run_time=1.1)
        add_shimmer(sbeads, amp=0.22, speed=1.8)

        # "prove a containment ... right values, at the right epochs"
        sub = mtex('S subset.eq R', size=FS_HEAD + 6, color=STAR)
        sub_note = VGroup(label("same values,", size=FS_LABEL, color=TXT),
                          label("same epochs", size=FS_LABEL, color=TXT)).arrange(DOWN, buff=0.12)
        sub_note.next_to(sub, DOWN, buff=0.3)
        claim = VGroup(sub, sub_note)
        claim_side = claim.copy().move_to(RIGHT * 5.0 + UP * 0.7)
        # while nothing else is on the lower stage, the claim sits there, centred
        # under the rows; it moves to the right margin when the VC beat needs room
        claim.move_to(np.array([COL(4.5, 0)[0], -1.45, 0]))
        self.pad_to(A("containment") - 0.3)
        self.play(Write(sub), run_time=0.9)
        self.pad_to(A("exactly what i derived") - 0.3)
        self.play(FadeIn(sub_note[0], shift=UP * 0.1), run_time=0.5)
        ties = VGroup(*[DashedLine(COL(i, ROW_S) + UP * 0.2, COL(i, ROW_W) + DOWN * 0.2,
                                   stroke_width=SW_THIN, stroke_color=STAR,
                                   dash_length=0.06) for i in range(2, 6)])
        self.pad_to(A("right epochs") - 0.3)
        self.play(FadeIn(sub_note[1], shift=UP * 0.1),
                  LaggedStart(*[ShowCreation(t) for t in ties], lag_ratio=0.1), run_time=0.8)

        # "both sides built their commitments incrementally ... where the range ends"
        self.pad_to(A("incrementally") - 0.4)
        nwb = bead(GOLD, BEAD_R).move_to(COL(9, ROW_W))
        nsb = bead(CYAN, BEAD_R).move_to(COL(6, ROW_S))
        self.play(FadeIn(nwb, scale=1.6), wband.animate.become(range_band(0, 9, ROW_W, GOLD)),
                  wtag.animate.next_to(range_band(0, 9, ROW_W, GOLD), RIGHT, buff=0.2),
                  run_time=0.8)
        self.play(FadeIn(nsb, scale=1.6), sband.animate.become(range_band(2, 6, ROW_S, CYAN)),
                  stag.animate.next_to(range_band(2, 6, ROW_S, CYAN), RIGHT, buff=0.2),
                  ties.animate.fade(1), run_time=0.8)
        adopt(self, wbeads, nwb)
        adopt(self, sbeads, nsb)
        self.remove(ties)
        ends = caption("built step by step, end unknown in advance")
        self.pad_to(A("without knowing") - 0.3)
        self.play(FadeIn(ends, shift=UP * 0.15), run_time=0.7)

        # "the textbook answer is a vector commitment ... RSA groups or pairings"
        vc = pill("vector commitment", color=MUT, size=FS_BODY).move_to(LEFT * 3.4 + DOWN * 1.4)
        vc_tag = label("RSA groups or pairings", size=FS_LABEL, color=MUT)
        vc_tag.next_to(vc, DOWN, buff=0.22)
        self.pad_to(A("textbook answer") - 0.3)
        self.play(FadeOut(ends), claim.animate.move_to(claim_side), run_time=0.9)
        self.pad_to(A("vector commitment") - 0.3)
        self.play(FadeIn(vc, shift=UP * 0.15), run_time=0.6)
        self.pad_to(AA(["rsa groups", "rsa"]) - 0.3)
        self.play(FadeIn(vc_tag, shift=UP * 0.1), run_time=0.6)
        self.pad_to(A("these circuits") - 0.4)
        vc_x = strike_mark(VGroup(vc, vc_tag))
        self.play(ShowCreation(vc_x), Transform(vc, dimmed(vc, 0.5)),
                  Transform(vc_tag, dimmed(vc_tag, 0.5)), run_time=0.6)

        # "a standard VC defends against a prover who commits to anything"
        anyp = label("a free prover commits to anything", size=FS_LABEL, color=FLARE)
        anyp.move_to(RIGHT * 2.9 + DOWN * 1.05)
        self.pad_to(A("commits to anything") - 0.4)
        self.play(FadeIn(anyp, shift=UP * 0.1), run_time=0.6)

        # "every single update is proven correct against the previous commitment"
        states = VGroup(*[tex_chip(f"C_{i}", color=GOLD, size=FS_BODY, pad=0.16)
                          for i in range(4)])
        states.arrange(RIGHT, buff=0.85).move_to(RIGHT * 2.9 + DOWN * 1.85)
        links = VGroup(*[tarrow(states[i], states[i + 1], color=GOLD) for i in range(3)])
        checks = VGroup(*[checkmark(0.22).next_to(links[i], UP, buff=0.08) for i in range(3)])
        self.pad_to(A("never free floating") - 0.3)
        self.play(FadeOut(anyp), LaggedStart(*[FadeIn(s, shift=RIGHT * 0.15) for s in states],
                                             lag_ratio=0.15), run_time=0.9)
        self.pad_to(A("proven correct") - 0.3)
        self.play(LaggedStart(*[AnimationGroup(ShowCreation(l), ShowCreation(c))
                                for l, c in zip(links, checks)], lag_ratio=0.3), run_time=1.0)
        honest = caption("honest construction, enforced by the PCD", color=GOLD)
        self.pad_to(A("honest construction") - 0.3)
        self.play(FadeIn(honest, shift=UP * 0.15), run_time=0.7)
        self.pad_to(A("opens up") - 0.3)
        self.play(Indicate(honest, color=GOLD, scale_factor=1.05), run_time=0.6)

        # "take the pair ... encode it as one cubic factor"
        FY = -1.55
        pair = mtex('(i, thick "nf"_i)', size=FS_HEAD + 6, color=GOLD).move_to(UP * FY)
        self.pad_to(A("here's the design") - 0.3)
        design_t = scene_title("the design: one cubic factor per epoch")
        self.play(FadeOut(VGroup(vc, vc_tag, vc_x, states, links, checks, honest, sub, sub_note)),
                  FadeTransform(gap_t, design_t), run_time=0.8)
        self.pad_to(A("take the pair") - 0.3)
        self.play(FadeTransform(wbeads[4].copy().clear_updaters(), pair), Indicate(wbeads[4], color=GOLD),
                  run_time=0.9)
        v1 = mtex('F_i (X) = ((i+1) X + "nf"_i)', size=FS_HEAD + 6, color=STAR)
        v2 = mtex('F_i (X) = ((i+1) X + "nf"_i)^3', size=FS_HEAD + 6, color=STAR)
        v3 = mtex('F_i (X) = ((i+1) X + "nf"_i)^3 - c', size=FS_HEAD + 6, color=STAR)
        for v in (v1, v2, v3):
            v.move_to(UP * FY)
        v1.align_to(v3, LEFT).align_to(v3, DOWN)
        v2.align_to(v3, LEFT).align_to(v3, DOWN)
        self.pad_to(A("cubic factor") - 0.2)
        self.play(TransformMatchingShapes(pair, v1), run_time=1.0)
        self.pad_to(A("cubed") - 0.3)
        self.play(TransformMatchingShapes(v1, v2), run_time=0.6)
        self.pad_to(A("minus c") - 0.2)
        self.play(TransformMatchingShapes(v2, v3), run_time=0.6)

        # "c is a fixed public non-cube; p ≡ 1 mod 3, so c = 2"
        cl = rich([("c: a fixed public non-cube.", TXT),
                   ('$p equiv 1 med ("mod" 3),$', MUT), ("so", TXT), ("$c = 2$", AMBER)],
                  size=FS_BODY)
        cl.move_to(UP * (FY - 1.0))
        self.pad_to(A("non cube") - 0.6)
        self.play(FadeIn(cl[0], shift=UP * 0.12), run_time=0.6)
        self.pad_to(A("congruent") - 0.5)
        self.play(FadeIn(cl[1], shift=UP * 0.12), run_time=0.6)
        self.pad_to(AA(["c equals two", "c equals 2"]) - 0.4)
        self.play(FadeIn(cl[2:], shift=UP * 0.12), run_time=0.6)

        # "the wallet's commitment is the product of these factors, one per epoch"
        wtiles = VGroup(*[ftile(i, GOLD).move_to(COL(i, ROW_W)) for i in range(10)])
        stiles = VGroup(*[ftile(i, CYAN).move_to(COL(i, ROW_S)) for i in range(2, 7)])
        gR = row_label('g_R (X)', GOLD, ROW_W)
        gS = row_label('g_S (X)', CYAN, ROW_S)
        # the factor formula stays on the lower stage, sliding right to make room
        # for the product it defines
        rem = v3.copy().scale(FS_HEAD / (FS_HEAD + 6))
        gdef = mtex('g_R (X) = product_i F_i (X)', size=FS_HEAD, color=GOLD)
        VGroup(gdef, rem).arrange(RIGHT, buff=1.0).move_to(UP * (FY - 0.2))
        gdef.shift(DOWN * 0.13)   # the product's limits pull its centre up: match baselines
        self.pad_to(A("product of these") - 0.8)
        clear_shimmer(wbeads)
        self.play(FadeOut(cl), Transform(v3, rem),
                  FadeOut(VGroup(wband, wtag, idx, idx_l)),
                  ReplacementTransform(wbeads, wtiles), FadeTransform(wl, gR),
                  run_time=1.4)
        add_shimmer([t[0] for t in wtiles], amp=0.18, speed=1.7)
        self.pad_to(A("one per epoch") - 0.4)
        self.play(FadeIn(gdef, shift=UP * 0.1), Indicate(gR, color=GOLD), run_time=0.7)

        # "append the next epoch ... a single random-point check"
        self.pad_to(A("append") - 0.3)
        nt = ftile(10, GOLD).move_to(COL(10, ROW_W))
        self.play(FadeIn(nt, shift=LEFT * 0.3), run_time=0.7)
        adopt(self, wtiles, nt)
        chk = caption("append: multiply in one factor, check it at one random point", color=STAR)
        self.pad_to(A("random point") - 0.3)
        self.play(FadeIn(chk, shift=UP * 0.15), Indicate(nt, color=STAR), run_time=0.7)
        self.pad_to(AA(["never had to fix", "the end point"]) - 0.4)
        dots = mtex("dots.c", size=FS_HEAD, color=GOLD).next_to(nt, RIGHT, buff=0.25)
        openend = label("no fixed endpoint", size=FS_LABEL, color=GOLD)
        openend.next_to(nt, UP, buff=0.3).align_to(dots, RIGHT)
        self.play(FadeIn(dots, shift=LEFT * 0.2), FadeIn(openend), run_time=0.7)
        self.pad_to(A("grows as long") - 0.2)
        self.play(Indicate(dots, color=GOLD, scale_factor=1.3), run_time=0.6)

        # "the service builds the same kind of product over its sub-range"
        self.pad_to(AA(["same kind of product", "sub range"]) - 0.6)
        clear_shimmer(sbeads)
        self.play(FadeOut(VGroup(sband, stag, openend, chk)),
                  ReplacementTransform(sbeads, stiles), FadeTransform(sl, gS),
                  run_time=1.2)
        add_shimmer([t[0] for t in stiles], amp=0.18, speed=1.7)

        # "containment has a shape ... divisibility"
        div = scene_title("containment = divisibility")
        self.pad_to(A("divisibility") - 0.5)
        self.play(FadeTransform(design_t, div), FadeOut(v3), FadeOut(gdef), run_time=1.0)
        self.pad_to(A("divisible by") - 0.3)
        self.play(Indicate(gS, color=CYAN, scale_factor=1.1),
                  Indicate(gR, color=GOLD, scale_factor=1.1), run_time=0.8)

        # "the wallet exhibits the quotient"
        qcols = [0, 1, 7, 8, 9, 10]
        qtiles = VGroup(*[ftile(i, AMBER).move_to(COL(i, ROW_Q)) for i in qcols])
        gQ = row_label('q(X)', AMBER, ROW_Q)
        self.pad_to(A("the quotient") - 1.0)
        clear_shimmer([wtiles[i][0] for i in qcols])
        self.play(*[Transform(wtiles[i], dimmed(wtiles[i], 0.4)) for i in qcols],
                  *[TransformFromCopy(wtiles[i], q) for i, q in zip(qcols, qtiles)],
                  FadeIn(gQ, shift=UP * 0.1), run_time=1.4)
        self.pad_to(A("all three commitments") - 0.3)
        self.play(LaggedStart(*[Indicate(m, scale_factor=1.15) for m in (gR, gS, gQ)],
                              lag_ratio=0.25), run_time=1.0)

        # "one evaluation at a random point checks the product identity"
        ident = mtex('g_R (r) = g_S (r) dot q(r)', size=FS_HEAD + 6, color=STAR)
        ident.move_to(LEFT * 1.2 + DOWN * 2.05)
        self.pad_to(A("one evaluation") - 0.6)
        self.play(Write(ident), run_time=1.2)
        self.pad_to(A("product identity") - 0.3)
        self.play(Indicate(ident, color=GOLD, scale_factor=1.06), run_time=0.8)

        # "the polynomial-oracle capability ... in your pocket"
        env = envelope(1.6, 1.0).move_to(RIGHT * 5.2 + DOWN * 2.0)
        env_tag = label("Ragu's oracle", size=FS_LABEL, color=CYAN).next_to(env, DOWN, buff=0.15)
        probe = tarrow(env[0].get_left(), ident.get_right(), color=CYAN, buff=0.15)
        self.pad_to(A("polynomial oracle") - 0.5)
        self.play(FadeIn(env, scale=1.15), FadeIn(env_tag), run_time=0.7)
        self.play(ShowCreation(probe), run_time=0.5)
        self.pad_to(A("your pocket") - 0.3)
        self.play(Indicate(env, color=CYAN, scale_factor=1.1), run_time=0.7)
        free = caption("the check costs the proof system almost nothing", color=CYAN)
        self.pad_to(A("almost nothing") - 0.6)
        self.play(FadeIn(free, shift=UP * 0.15), run_time=0.6)

        # soundness: rows shrink to the left, the argument lands on the right
        rows = VGroup(wtiles, stiles, qtiles, gR, gS, gQ, dots)
        rows.save_state()
        why = scene_title("why does divisibility prove anything?")
        self.pad_to(A("believe divisibility") - 0.6)
        self.play(FadeOut(VGroup(ident, env, env_tag, probe, free)),
                  FadeTransform(div, why),
                  rows.animate.scale(0.8).move_to(np.array([-2.55, 0.65, 0])), run_time=1.0)
        pts = bullets([
            mtex('$Y^3 - c$ is irreducible', size=FS_LABEL, color=STAR, math=False),
            mtex('$Y -> (i+1) X + "nf"_i$ \\ keeps it irreducible', size=FS_LABEL,
                 color=TXT, math=False),
            mtex('unique factorization ⇒ \\ the factors are recoverable', size=FS_LABEL,
                 color=TXT, math=False),
        ], size=FS_LABEL, mark_color=GOLD, buff=0.38)
        pts.move_to(np.array([4.35, 0.65, 0])).align_to(np.array([2.15, 0, 0]), LEFT)
        # one factor, blown up on the lower stage: every attempt to split it cracks
        # and heals ("refuses to factor"); then it folds back into its row
        big_box = RoundedRectangle(width=5.4, height=1.3, corner_radius=0.14)
        big_box.set_fill(GOLD, 0.10).set_stroke(GOLD, SW, 0.9)
        big_box.move_to(np.array([-2.55, -1.65, 0]))
        y3 = mtex('Y^3 - c', size=FS_HEAD + 6, color=GOLD).move_to(big_box)
        y3b = mtex('((i+1) X + "nf"_i)^3 - c', size=FS_HEAD, color=GOLD).move_to(big_box)
        big = VGroup(big_box, y3)

        def refuse():
            cr = crack(big_box)
            self.play(ShowCreation(cr), run_time=0.45)
            self.play(FadeOut(cr), big.animate(rate_func=there_and_back).scale(1.04),
                      run_time=0.5)

        self.pad_to(A("factors were chosen") - 0.3)
        self.play(FadeIn(big, scale=0.9), run_time=0.7)
        self.pad_to(A("irreducible") - 0.4)
        self.play(FadeIn(pts[0], shift=LEFT * 0.2), run_time=0.6)
        self.pad_to(AA(["isn't a cubed", "isn't a"]) - 0.1)
        refuse()
        self.pad_to(A("affine") - 0.4)
        self.play(FadeIn(pts[1], shift=LEFT * 0.2), FadeTransform(y3, y3b), run_time=0.8)
        big = VGroup(big_box, y3b)
        self.pad_to(A("keeps it irreducible") - 0.1)
        refuse()
        self.pad_to(A("unique factorization") - 0.4)
        self.play(FadeIn(pts[2], shift=LEFT * 0.2), run_time=0.6)
        home = wtiles[4].copy()
        self.play(FadeTransform(big, home), run_time=0.8)
        self.remove(home)
        self.play(LaggedStart(*[Indicate(t, color=GOLD, scale_factor=1.12) for t in wtiles],
                              lag_ratio=0.06), run_time=1.2)

        # "the only escape hatch ... a nontrivial cube root of unity"
        omega = mtex('(i+1, thick "nf") = omega dot (j+1, thick "nf"\') thick ?',
                     size=FS_BODY, color=FLARE)
        omega.move_to(np.array([0.0, -1.2, 0]))
        self.pad_to(A("escape hatch") - 0.4)
        self.play(FadeIn(omega, shift=UP * 0.12), run_time=0.7)
        self.pad_to(A("cube root of unity") - 0.3)
        self.play(Indicate(omega, color=FLARE, scale_factor=1.06), run_time=0.7)

        # "epoch indices are 32-bit ... the cube root of unity is field-sized"
        # scale comparison, centred under the whole stage (bit-lengths to scale)
        bx0, blen = -4.4, 4.8
        bar1 = Line(np.array([bx0, -1.95, 0]), np.array([bx0 + blen * 32 / 255, -1.95, 0]),
                    stroke_width=12, stroke_color=GOLD)
        bar2 = Line(np.array([bx0, -2.55, 0]), np.array([bx0 + blen, -2.55, 0]),
                    stroke_width=12, stroke_color=FLARE)
        t1 = mtex('i + 1 < 2^32', size=FS_LABEL, color=GOLD).next_to(bar1, RIGHT, buff=0.3)
        t2 = mtex('omega approx 2^255 thick "(field-sized)"', size=FS_LABEL, color=FLARE)
        t2.next_to(bar2, RIGHT, buff=0.3)
        self.pad_to(AA(["32 bit", "indices"]) - 0.4)
        self.play(ShowCreation(bar1), FadeIn(t1), run_time=0.7)
        self.pad_to(A("cube root of unity", 2) - 0.3)
        self.play(ShowCreation(bar2), FadeIn(t2), run_time=1.0)
        self.pad_to(A("never meet") - 0.3)
        omega_x = strike_mark(omega)
        self.play(ShowCreation(omega_x), omega.animate.fade(0.4), run_time=0.6)

        # "multiplication commutes ... a multiset, not a sequence"
        caveat = scene_title("one honest caveat", color=FLARE)
        # the rows come back a little lower than before: with the index row gone,
        # this centres the three rows between the title and the caption
        CAV_DY = 0.0   # the grid already sits centred between title and caption
        self.pad_to(A("honest caveat") - 0.4)
        self.play(FadeOut(VGroup(pts, omega, omega_x, bar1, bar2, t1, t2)),
                  FadeTransform(why, caveat), Restore(rows), run_time=1.0)
        self.pad_to(A("commutes") - 0.3)
        perm = [3, 0, 4, 1, 2]
        spots = [t.get_center().copy() for t in stiles]
        self.play(*[stiles[i].animate(path_arc=PI / 2).move_to(spots[perm[i]])
                    for i in range(5)], run_time=1.0)
        ms = caption("divisibility sees a multiset, not a sequence", color=FLARE)
        self.pad_to(A("not a sequence") - 0.5)
        self.play(FadeIn(ms, shift=UP * 0.15), run_time=0.6)
        self.pad_to(A("skip one") - 0.3)
        clear_shimmer([t[0] for t in stiles])
        lit = stiles[2].copy()
        self.play(Transform(stiles[2], dimmed(stiles[2], 0.15)), run_time=0.5)
        self.play(Transform(stiles[2], lit), run_time=0.4)
        self.play(*[stiles[i].animate.move_to(spots[i]) for i in range(5)], run_time=0.8)

        # "order comes from counters and endpoint checks ... a sentinel"
        ys = ROW_S - CAV_DY
        post_l = Line(COL(2, ys) + LEFT * 0.48 + DOWN * 0.42,
                      COL(2, ys) + LEFT * 0.48 + UP * 0.42,
                      stroke_width=SW_BOLD + 2, stroke_color=STAR)
        post_r = Line(COL(6, ys) + RIGHT * 0.48 + DOWN * 0.42,
                      COL(6, ys) + RIGHT * 0.48 + UP * 0.42,
                      stroke_width=SW_BOLD + 2, stroke_color=STAR)
        order = caption("order: counters + endpoint checks, step by step", color=STAR)
        self.pad_to(A("counters and endpoint checks") - 0.4)
        self.play(FadeOut(ms), FadeIn(order, shift=UP * 0.15),
                  ShowCreation(post_l), ShowCreation(post_r), run_time=0.9)
        self.pad_to(A("step by step") - 0.3)
        self.play(LaggedStart(*[Indicate(t, color=STAR, scale_factor=1.12) for t in stiles],
                              lag_ratio=0.15), run_time=1.0)
        snt = label("sentinels", size=FS_BODY, color=STAR)
        snt.move_to(np.array([COL(4, 0)[0], -2.2, 0]))
        sa = VGroup(tarrow(snt.get_corner(UL) + RIGHT * 0.1, post_l.get_bottom(), color=STAR),
                    tarrow(snt.get_corner(UR) + LEFT * 0.1, post_r.get_bottom(), color=STAR))
        self.pad_to(AA(["sentinel"]) - 0.4)
        self.play(FadeIn(snt, shift=UP * 0.12), ShowCreation(sa), run_time=0.8)

        # "hold the idea: cheap indexed containment, by unique factorization"
        summary = scene_title("indexed containment, by unique factorization", color=GOLD)
        self.pad_to(A("hold the idea") - 0.3)
        self.play(FadeTransform(caveat, summary), FadeOut(order), run_time=1.2)
        self.pad_to(scene_T("2.3"))

"""Act 3 — one accumulator for everything. Anchored to anim/words.json timestamps.

Render:  ./qa.sh act3.py Scene31   (or: manimgl act3.py Scene31 Scene32 -w)
Layout:  title band / stage / caption band from style.py (FS_* type scale).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manimlib import *
from style import *


# ---- scene-local vocabulary --------------------------------------------------

LINE_Y = 0.55
LINE_X0 = -5.6
LINE_UNIT = 0.7           # value v -> x = LINE_X0 + v * LINE_UNIT, v in [0, 16]
ROW_Y = -1.55             # the factored product f(X) = (X - a)(X - b)...
ROW_MAX_W = 12.6


def vx(v, y=LINE_Y):
    return np.array([LINE_X0 + v * LINE_UNIT, y, 0])


def number_line():
    line = Line(vx(-0.5), vx(16.5), stroke_width=SW_THIN, stroke_color=DIM)
    ticks = VGroup(*[Line(vx(v) + 0.09 * DOWN, vx(v) + 0.09 * UP,
                          stroke_width=1.6, stroke_color=DIM)
                     for v in range(0, 17, 2)])
    return VGroup(line, ticks)


def root_dot(v, color=GOLD):
    return Dot(vx(v), radius=0.12).set_fill(color, 1.0)


def ftile(tex, color=GOLD, size=26):
    """A factor of the product polynomial, in math type."""
    t = mtex(tex, size=size, color=color)
    box = RoundedRectangle(width=t.get_width() + 0.28,
                           height=0.72, corner_radius=0.1)
    box.set_fill(color, 0.10)
    box.set_stroke(color, SW_THIN, 0.85)
    t.move_to(box)
    return VGroup(box, t)


def strike(mob, color=FLARE, width=SW_BOLD, opacity=1.0):
    """Deliberate strike-through. A polyline, not a Line, so the layout linter
    (which flags lines crossing text) leaves intentional cross-outs alone."""
    vm = VMobject()
    vm.set_points_as_corners([mob.get_corner(DL) + 0.08 * DL,
                              mob.get_corner(UR) + 0.08 * UR])
    vm.set_stroke(color, width, opacity)
    return vm


def curved_tarrow(a, b, angle=-0.6, color=GOLD, width=SW, tip=0.2):
    """A thin arc arrow in the tarrow style (manim's CurvedArrow tip is too heavy)."""
    arc = ArcBetweenPoints(np.asarray(a, float), np.asarray(b, float), angle=angle)
    end = arc.get_end()
    u = end - arc.point_from_proportion(0.97)
    u = u / max(float(np.linalg.norm(u)), 1e-9)
    n = np.array([-u[1], u[0], 0.0])
    arc = ArcBetweenPoints(np.asarray(a, float), end - u * tip * 0.8, angle=angle)
    arc.set_stroke(color, width, 1.0).set_fill(opacity=0)
    head = Polygon(end, end - u * tip + n * tip * 0.42, end - u * tip - n * tip * 0.42)
    head.set_fill(color, 1.0).set_stroke(width=0)
    return VGroup(arc, head)


def grow_tarrow(arrow, **kw):
    """Draw a tarrow's shaft, then let its head land (no half-drawn head outline)."""
    return Succession(ShowCreation(arrow[0], run_time=0.75),
                      FadeIn(arrow[1], scale=0.5, run_time=0.25), **kw)


def swap_title(old, new):
    """Old title lifts away, then the new one rises into place (never overlapping)."""
    return LaggedStart(FadeOut(old, shift=UP * 0.3), FadeIn(new, shift=UP * 0.3),
                       lag_ratio=0.85)


def merkle_tree(center, color=MUT, leaf_color=GOLD):
    """A 3-level Merkle tree with gold commitment leaves."""
    root = np.array([center[0], center[1] + 1.2, 0])
    mids = [root + np.array([dx, -1.0, 0]) for dx in (-1.3, 1.3)]
    leaves = [np.array([center[0] + dx, center[1] - 0.8, 0])
              for dx in (-1.95, -0.65, 0.65, 1.95)]
    edges = VGroup(*[Line(root, m, stroke_width=SW_THIN, stroke_color=color)
                     for m in mids],
                   *[Line(mids[i // 2], l, stroke_width=SW_THIN, stroke_color=color)
                     for i, l in enumerate(leaves)])
    nodes = VGroup(Dot(root, radius=0.12).set_fill(color, 1.0),
                   *[Dot(m, radius=0.11).set_fill(color, 1.0) for m in mids])
    leaf_dots = VGroup(*[Dot(l, radius=0.13).set_fill(leaf_color, 1.0)
                         for l in leaves])
    return VGroup(edges, nodes, leaf_dots), leaf_dots


def nf_grid(center, rows=3, cols=4):
    p = panel(3.7, 2.6, color=FLARE, fill_opacity=0.04).move_to(center)
    beads = VGroup(*[bead(FLARE, 0.12).move_to(
        center + np.array([(c - (cols - 1) / 2) * 0.78,
                           (r - (rows - 1) / 2) * 0.66, 0]))
        for r in range(rows) for c in range(cols)])
    return VGroup(p, beads), beads


def probe(v, color=STAR, top=2.1):
    """A vertical evaluation probe hitting the number line at value v."""
    return DashedLine(vx(v, top), vx(v, LINE_Y + 0.14),
                      stroke_width=3.0, stroke_color=color)


def domino(color=STAR):
    """An action as a domino: one card, two tachygram pips."""
    card = panel(1.6, 1.0, color=color, fill_opacity=0.07)
    pips = VGroup(bead(STAR, 0.11).move_to(card.get_center() + LEFT * 0.36),
                  bead(STAR, 0.11).move_to(card.get_center() + RIGHT * 0.36))
    return VGroup(card, pips)


def tx_card(tex, color=GOLD, n_beads=1, bead_colors=None, w=2.1):
    """A mempool transaction: a card with its tachygram tags and beads."""
    card = panel(w, 1.15, color=color, fill_opacity=0.08)
    tag = mtex(tex, size=FS_LABEL, color=bead_colors[0] if bead_colors else FLARE)
    tag.move_to(card.get_center() + UP * 0.22)
    cols = bead_colors or [FLARE] * n_beads
    beads = VGroup(*[bead(c, 0.11) for c in cols]).arrange(RIGHT, buff=0.55)
    beads.move_to(card.get_center() + DOWN * 0.27)
    return VGroup(card, beads, tag)


class Scene31(TimedScene):
    """3.1 — Tachygrams: erasing the commitment/nullifier distinction."""

    def construct(self):
        A = lambda p, o=1: anchor("3.1", p, o)
        AA = lambda ps, o=1: anchor_any("3.1", ps, o)

        # ---- "two data structures": the Merkle tree and the nullifier set ----
        # diagrams first (on "what the pool actually maintains"), then the title
        tree, leaf_dots = merkle_tree(np.array([-3.4, 0.2, 0]))
        grid, grid_beads = nf_grid(np.array([3.4, 0.2, 0]))
        tree.scale(1.3)
        grid.scale(1.3)
        title = scene_title("two questions, two data structures")
        self.pad_to(A("actually maintains") - 0.4)
        self.play(LaggedStartMap(FadeIn, VGroup(*tree[0], *tree[1], *tree[2]),
                                 lag_ratio=0.05),
                  LaggedStartMap(FadeIn, VGroup(grid[0], *grid_beads),
                                 lag_ratio=0.04), run_time=1.6)
        add_shimmer(grid_beads, amp=0.18)
        self.pad_to(A("two data structures") - 0.4)
        self.play(FadeIn(title, shift=DOWN * 0.2), run_time=0.9)

        # "is this commitment in the pool?" / "has this nullifier appeared?"
        Q_Y = grid.get_bottom()[1] - 0.62
        q1 = VGroup(label("membership", size=FS_BODY, color=GOLD),
                    label("is this commitment in the pool?", size=FS_SMALL, color=TXT))
        q1.arrange(DOWN, buff=0.14).move_to(np.array([tree.get_x(), Q_Y, 0]))
        self.pad_to(A("is this commitment") - 0.3)
        self.play(FadeIn(q1, shift=UP * 0.15),
                  Indicate(leaf_dots, color=GOLD, scale_factor=1.2), run_time=0.9)
        q2 = VGroup(label("non-membership", size=FS_BODY, color=FLARE),
                    label("has this nullifier appeared?", size=FS_SMALL, color=TXT))
        q2.arrange(DOWN, buff=0.14).move_to(np.array([grid.get_x(), Q_Y, 0]))
        self.pad_to(A("has this nullifier") - 0.3)
        self.play(FadeIn(q2, shift=UP * 0.15),
                  Indicate(grid_beads, color=FLARE, scale_factor=1.12), run_time=0.9)

        # ---- "a polynomial accumulator": number line + factored product ----
        # the two questions stay on screen: they drop into the caption band, where
        # each one gets its answer from the same evaluation
        nline = number_line()
        BAND_X = 3.3
        m_ans = mtex("<==> f(x) = 0", size=FS_BODY, color=GOLD)
        n_ans = mtex("<==> f(x) != 0", size=FS_BODY, color=FLARE)
        # each band line (question + its answer) ends up centered at x = -/+ BAND_X
        m_line = VGroup(q1[0].copy(), m_ans).arrange(RIGHT, buff=0.2)
        n_line = VGroup(q2[0].copy(), n_ans).arrange(RIGHT, buff=0.2)
        m_line.move_to(np.array([-BAND_X, CAPTION_Y, 0]))
        n_line.move_to(np.array([BAND_X, CAPTION_Y, 0]))
        self.pad_to(A("polynomial accumulator") - 0.5)
        self.play(FadeOut(q1[1]), FadeOut(q2[1]),
                  q1[0].animate.move_to(m_line[0]),
                  q2[0].animate.move_to(n_line[0]),
                  tree.animate.scale(0.4).move_to(np.array([-5.6, 2.45, 0])).fade(0.25),
                  grid.animate.scale(0.4).move_to(np.array([5.6, 2.45, 0])).fade(0.25),
                  ShowCreation(nline), run_time=1.2)

        roots = [2, 5, 9, 12]
        dots = VGroup(*[root_dot(v) for v in roots])
        f_eq = mtex("f(X) =", size=FS_LABEL, color=TXT)
        tiles = VGroup(*[ftile(f"(X - {v})") for v in roots])
        VGroup(f_eq, *tiles).arrange(RIGHT, buff=0.1).move_to(UP * ROW_Y)
        acc_tag = mtex('"tg"_"acc" = "Com"(f)', size=FS_LABEL, color=MUT)
        acc_tag.move_to(np.array([-4.3, ROW_Y + 0.85, 0]))
        deg_pos = np.array([4.6, ROW_Y + 0.85, 0])

        def deg_tex(n):
            return mtex(f'"deg" f = {n}', size=FS_LABEL, color=MUT).move_to(deg_pos)

        deg = deg_tex(4)
        self.pad_to(A("whose roots are your set") - 0.8)
        self.play(LaggedStart(*[FadeIn(d, shift=DOWN * 0.5) for d in dots],
                              lag_ratio=0.12),
                  LaggedStart(*[FadeIn(t) for t in tiles], lag_ratio=0.12),
                  FadeIn(f_eq), FadeIn(acc_tag), FadeIn(deg), run_time=1.5)

        def row_to_target(*new):
            """Re-flow f(X) = (...)(...) centered, capped to the stage width.

            Tiles in `new` are snapped to their landing slot (the caller fades them
            in there); only the tiles already on screen slide. Tiles are added to
            the scene one by one, never via the `tiles` group, so tiles.add(t)
            does not pop t onto the screen before its FadeIn.
            """
            members = [f_eq, *tiles]
            slots = VGroup(*[m.copy() for m in members])
            slots.arrange(RIGHT, buff=0.1)
            if slots.get_width() > ROW_MAX_W:
                slots.set_width(ROW_MAX_W)
            slots.move_to(UP * ROW_Y)
            anims = []
            for m, c in zip(members, slots):
                if m in new:
                    m.replace(c)
                else:
                    anims.append(Transform(m, c))
            return AnimationGroup(*anims)

        def enter(t, d=LEFT):
            """A new factor fades into its slot once the row has made room."""
            return FadeIn(t, shift=0.3 * d,
                          rate_func=squish_rate_func(smooth, 0.45, 1.0))

        # membership probe: f(5) = 0
        self.pad_to(A("show membership") - 0.2)
        p1 = probe(5, color=GOLD)
        r1 = mtex("f(5) = 0", size=FS_BODY, color=GOLD).next_to(p1, UP, buff=0.12)
        self.play(ShowCreation(p1), run_time=0.5)
        self.play(FadeIn(r1, scale=1.15), Indicate(dots[1], color=GOLD), run_time=0.7)
        self.pad_to(A("zero") - 0.3)
        self.play(FadeIn(m_ans, shift=LEFT * 0.15), run_time=0.6)

        # non-membership probe: f(7) = 100
        self.pad_to(A("show non membership") - 0.2)
        p2 = probe(7, color=FLARE)
        r2 = mtex("f(7) = 100", size=FS_BODY, color=FLARE).next_to(p2, UP, buff=0.12)
        r2.shift(RIGHT * 0.5)
        self.play(ShowCreation(p2), run_time=0.5)
        self.play(FadeIn(r2, scale=1.15), run_time=0.7)
        self.pad_to(A("but zero") - 0.3)
        self.play(FadeIn(n_ans, shift=LEFT * 0.15), run_time=0.6)

        # "the same single evaluation answers both"
        self.pad_to(A("same single evaluation") - 0.3)
        self.play(Indicate(r1, color=GOLD, scale_factor=1.12),
                  Indicate(r2, color=FLARE, scale_factor=1.12), run_time=0.9)
        sym = caption("one evaluation answers both questions", color=STAR)
        self.pad_to(A("no asymmetry") - 0.4)
        self.play(FadeTransform(VGroup(q1[0], m_ans, q2[0], n_ans), sym, stretch=False),
                  run_time=0.9)

        # "drives the design" — the act's thesis replaces the question
        title2 = scene_title("one accumulator for everything", color=GOLD)
        self.pad_to(A("drives the design") - 0.4)
        self.play(swap_title(title, title2), FadeOut(sym), run_time=1.2)

        # "stops paying rent ... merges them" — both structures dissolve into the line
        self.pad_to(A("stops paying rent") - 0.4)
        self.play(tree.animate.fade(0.5), grid.animate.fade(0.5), run_time=0.7)
        self.pad_to(A("merges them") - 0.3)
        clear_shimmer(grid_beads)
        cm_dot = root_dot(14)
        nf_dot = root_dot(1, FLARE)
        self.play(tree.animate.scale(0.2).move_to(vx(4)).fade(1),
                  grid.animate.scale(0.2).move_to(vx(10)).fade(1),
                  FadeOut(p1), FadeOut(p2), FadeOut(r1), FadeOut(r2),
                  run_time=1.0)
        self.remove(tree, grid)

        # "every element ... is a tachygram: 32 bytes, pseudorandom"
        tg_name = key_chip("tachygram", color=STAR, size=FS_BODY)
        tg_kind = label("32 bytes, pseudorandom", size=FS_SMALL, color=MUT)
        tg_chip = VGroup(tg_name, tg_kind).arrange(RIGHT, buff=0.3)
        tg_chip.move_to(UP * 2.25)
        self.pad_to(AA(["a tacky gram", "a tachygram"]) - 0.3)
        self.play(FadeIn(tg_chip, scale=1.08), run_time=0.8)

        # output -> cm, spend -> nf_e; new factor tiles join the product
        cm_tag = mtex('"cm"', size=FS_LABEL, color=GOLD).next_to(cm_dot, UP, buff=0.16)
        t_cm = ftile('(X - "cm")', color=GOLD)
        t_cm.next_to(tiles, RIGHT, buff=0.1)
        tiles.add(t_cm)
        self.pad_to(A("note commitment") - 0.8)
        self.play(FadeIn(cm_dot, shift=DOWN * 0.6), FadeIn(cm_tag),
                  enter(t_cm), row_to_target(t_cm), run_time=0.9)
        nf_tag = mtex('"nf"_e', size=FS_LABEL, color=FLARE).next_to(nf_dot, UP, buff=0.16)
        t_nf = ftile('(X - "nf"_e)', color=FLARE)
        t_nf.next_to(tiles, RIGHT, buff=0.1)
        tiles.add(t_nf)
        self.pad_to(AA(["an epic nullifier", "an epoch nullifier"]) - 0.5)
        self.play(FadeIn(nf_dot, shift=DOWN * 0.6), FadeIn(nf_tag),
                  enter(t_nf), row_to_target(t_nf), run_time=0.9)
        deg6 = deg_tex(6)
        self.play(ReplacementTransform(deg, deg6), run_time=0.4)
        deg = deg6

        # "you can't tell which is which" — everything turns star-white
        dots.add(cm_dot, nf_dot)
        self.pad_to(A("which is which") - 0.5)
        self.play(*[d.animate.set_fill(STAR, 1.0) for d in dots],
                  *[t[0].animate.set_fill(STAR, 0.10).set_stroke(STAR, SW_THIN, 0.85)
                    for t in tiles],
                  *[t[1].animate.set_fill(STAR, 1.0) for t in tiles],
                  FadeOut(cm_tag), FadeOut(nf_tag), run_time=1.1)

        # "one larger anonymity set"
        anon = bracket(VGroup(dots), color=STAR, buff=0.3)
        anon_tag = label("one anonymity set", size=FS_LABEL, color=STAR)
        anon_tag.next_to(anon, UP, buff=0.12)
        self.pad_to(A("anonymity set") - 0.6)
        self.play(FadeOut(tg_chip), GrowFromCenter(anon), FadeIn(anon_tag), run_time=0.8)
        add_shimmer(dots, amp=0.15)

        # "the algebra is the other half of the bargain"
        self.pad_to(A("the algebra") - 0.3)
        self.play(FadeOut(anon), FadeOut(anon_tag), run_time=0.7)

        # insert: a dot drops, a factor slides in, degree ticks
        self.pad_to(A("insert an element") - 0.2)
        d15 = root_dot(15, STAR)
        t15 = ftile('(X - "tg")', color=STAR)
        t15.next_to(tiles, RIGHT, buff=0.1)
        tiles.add(t15)
        ins_t = caption("insert = multiply by one linear factor")
        deg7 = deg_tex(7)
        self.play(FadeIn(d15, shift=DOWN * 0.6), enter(t15),
                  row_to_target(t15), ReplacementTransform(deg, deg7),
                  FadeIn(ins_t), run_time=1.0)
        dots.add(d15)
        deg = deg7

        # union: a second set zippers onto the line, the products multiply
        self.pad_to(A("union two sets") - 0.4)
        gline = Line(np.array([1.6, 1.95, 0]), np.array([4.6, 1.95, 0]),
                     stroke_width=SW_THIN, stroke_color=CYAN)
        gd1 = Dot(np.array([2.3, 1.95, 0]), radius=0.12).set_fill(CYAN, 1.0)
        gd2 = Dot(np.array([3.9, 1.95, 0]), radius=0.12).set_fill(CYAN, 1.0)
        g_tag = mtex("g(X)", size=FS_LABEL, color=CYAN).next_to(gline, LEFT, buff=0.2)
        uni_t = caption("union = multiply the polynomials")
        self.play(ShowCreation(gline), FadeIn(gd1), FadeIn(gd2), FadeIn(g_tag),
                  FadeOut(ins_t), FadeIn(uni_t), run_time=0.8)
        tg1 = ftile("(X - 3)", color=CYAN)
        tg2 = ftile("(X - 11)", color=CYAN)
        tg1.next_to(tiles, RIGHT, buff=0.1)
        tg2.next_to(tg1, RIGHT, buff=0.1)
        tiles.add(tg1, tg2)
        deg9 = deg_tex(9)
        self.play(gd1.animate.move_to(vx(3)), gd2.animate.move_to(vx(11)),
                  FadeOut(gline), FadeOut(g_tag),
                  enter(tg1, UP), enter(tg2, UP),
                  row_to_target(tg1, tg2), ReplacementTransform(deg, deg9), run_time=1.3)
        deg = deg9
        nopre = caption("no preconditions: multisets just work", color=MUT)
        self.pad_to(A("no preconditions") - 0.3)
        self.play(FadeOut(uni_t), FadeIn(nopre), run_time=0.6)

        # remove a subset: divide, exactly
        self.pad_to(A("remove a subset") - 0.2)
        tiles.remove(tg1, tg2)
        div_t = caption("remove = divide, exactly")
        deg7b = deg_tex(7)
        self.play(gd1.animate.shift(UP * 0.9).set_opacity(0),
                  gd2.animate.shift(UP * 0.9).set_opacity(0),
                  tg1.animate.shift(DOWN * 0.5).set_opacity(0),
                  tg2.animate.shift(DOWN * 0.5).set_opacity(0),
                  row_to_target(), FadeOut(nopre), FadeIn(div_t),
                  ReplacementTransform(deg, deg7b), run_time=1.1)
        deg = deg7b
        self.remove(gd1, gd2, tg1, tg2)

        # "every set operation is a polynomial operation"
        corr = VGroup(key_chip("set operation", color=STAR, size=FS_LABEL),
                      mtex("<->", size=FS_BODY, color=MUT),
                      key_chip("polynomial operation", color=STAR, size=FS_LABEL))
        corr.arrange(RIGHT, buff=0.3).move_to(UP * CAPTION_Y)
        self.pad_to(A("polynomial operation") - 0.9)
        self.play(FadeOut(div_t), FadeIn(corr, scale=1.05), run_time=0.9)

        # "checks with one random-point evaluation"
        self.pad_to(A("random point evaluation") - 0.6)
        pr = probe(7.6, color=STAR)
        pr_tag = mtex('checkmark "at random" r', size=FS_LABEL, color=STAR)
        pr_tag.next_to(pr, UP, buff=0.12)
        self.play(ShowCreation(pr), FadeIn(pr_tag), run_time=0.8)
        self.pad_to(A("lean on this") - 0.3)
        self.play(FadeOut(pr), FadeOut(pr_tag), FadeOut(corr), run_time=0.6)

        # ---- "one subtlety": binding is not list-correctness -----------------
        # the number line has done its job; the product row moves up to be audited
        self.pad_to(A("one subtlety") - 0.3)
        clear_shimmer(dots)
        row = VGroup(f_eq, *tiles)
        title3 = scene_title("does the commitment match the list?")
        self.play(FadeOut(nline), FadeOut(dots),
                  row.animate.shift(UP * 3.15),
                  acc_tag.animate.shift(UP * 3.15).fade(0.2),
                  deg.animate.shift(UP * 3.15).fade(0.2),
                  swap_title(title2, title3),
                  run_time=1.0)

        AUD_Y = -0.7
        env = envelope(2.5, 1.55, color=CYAN, tex_label="f(X)")
        env.move_to(np.array([-4.5, AUD_Y, 0]))
        self.pad_to(A("binding says") - 0.4)
        self.play(FadeIn(env, scale=1.1), run_time=0.8)
        # the argument sits on the right, beside the envelope
        NOTE_X = 0.9
        bind = label("binding: one polynomial inside", size=FS_BODY, color=CYAN)
        bind.move_to(np.array([0, AUD_Y + 0.3, 0])).align_to(np.array([NOTE_X, 0, 0]), LEFT)
        self.play(FadeIn(bind, shift=LEFT * 0.2), run_time=0.6)
        notroots = label("…but which roots?", size=FS_BODY, color=MUT)
        notroots.next_to(bind, DOWN, buff=0.3).align_to(bind, LEFT)
        self.pad_to(A("roots you were told") - 0.5)
        self.play(FadeIn(notroots, shift=LEFT * 0.2), run_time=0.6)

        # a ghost root sneaks into the committed polynomial: f becomes f~
        t_ghost = ftile("(X - 7)", color=FLARE)
        t_ghost.move_to(np.array([-1.5, AUD_Y, 0]))
        ghost_t = label("an extra root", size=FS_SMALL, color=FLARE)
        ghost_t.next_to(t_ghost, UP, buff=0.18)
        self.pad_to(A("extra root") - 0.3)
        self.play(FadeIn(t_ghost, shift=LEFT * 0.3), FadeIn(ghost_t), run_time=0.9)
        sneak = tarrow(t_ghost, env[0], color=FLARE, width=SW, buff=0.12)
        f_bad = mtex("tilde(f)(X)", size=env[2].font_pt, color=FLARE)
        f_bad.move_to(env[2], aligned_edge=LEFT)
        self.play(grow_tarrow(sneak), run_time=0.5)
        self.play(FadeTransform(env[2], f_bad), run_time=0.7)

        # "audited against its published list"
        self.pad_to(A("published list") - 1.2)
        lbr = bracket(tiles, color=GOLD, buff=0.14, below=True)
        lbr_tag = label("the published list", size=FS_LABEL, color=GOLD)
        lbr_tag.next_to(lbr, DOWN, buff=0.1)
        self.play(GrowFromCenter(lbr), FadeIn(lbr_tag),
                  FadeOut(bind), FadeOut(notroots), run_time=0.9)

        # y_r = prod(r - tg_i), field ops only
        AUD_X = 3.4
        self.pad_to(A("multiplies out") - 0.3)
        yr = mtex('y_r = product_i (r - "tg"_i)', size=FS_HEAD, color=GOLD)
        yr.move_to(np.array([AUD_X, AUD_Y + 0.2, 0]))
        self.play(Write(yr, run_time=1.2))
        fo = label("field arithmetic only, no group operations", size=FS_SMALL, color=MUT)
        fo.next_to(yr, DOWN, buff=0.22)
        self.pad_to(A("pure field arithmetic") - 0.3)
        self.play(FadeIn(fo), run_time=0.6)

        # the PCS check catches the mismatch
        self.pad_to(A("proof system checks") - 0.3)
        claim = mtex('tilde(f)(r) != y_r', size=FS_HEAD, color=FLARE)
        claim.move_to(np.array([AUD_X, AUD_Y - 1.5, 0]))
        self.play(Write(claim, run_time=0.9))
        self.play(ShowCreation(strike(t_ghost)), ghost_t.animate.fade(0.5),
                  run_time=0.8)

        # soundness: D / |F|
        self.pad_to(A("false claim") - 0.2)
        snd = tex_chip('"Pr"["false claim survives"] approx D \\/ abs(bb(F))',
                       color=STAR, size=FS_LABEL)
        snd.move_to(UP * CAPTION_Y)
        self.play(FadeIn(snd, shift=UP * 0.2), run_time=0.9)
        self.pad_to(A("negligible") - 0.3)
        self.play(Indicate(snd, color=GOLD, scale_factor=1.08), run_time=0.8)
        self.pad_to(scene_T("3.1"))


class Scene32(TimedScene):
    """3.2 — Actions, stamps, and two tachygrams each."""

    def construct(self):
        A = lambda p, o=1: anchor("3.2", p, o)
        AA = lambda ps, o=1: anchor_any("3.2", ps, o)

        # ---- the question, then the Orchard action card, fields included ----
        title = scene_title("where do tachygrams come from?")
        self.pad_to(0.6)
        self.play(FadeIn(title, shift=DOWN * 0.2), run_time=0.9)

        # the two cards start centered; they slide left when the rk formulas arrive
        CARD_Y, CARD_W, CARD_H = 0.15, 3.0, 4.3
        CARD_X0 = 1.65          # cards at -/+ CARD_X0 while centred
        SLIDE = 3.3
        FS_CHIP = 34
        orch = panel(CARD_W, CARD_H, color=MUT, fill_opacity=0.04)
        orch.move_to(np.array([-CARD_X0, CARD_Y, 0]))
        orch_t = label("Orchard action", size=FS_BODY, color=MUT)
        orch_t.next_to(orch, UP, buff=0.16)
        f_rk = tex_chip('"rk"', color=GOLD, size=FS_CHIP, pad=0.2)
        f_cv = tex_chip('"cv"', color=GOLD, size=FS_CHIP, pad=0.2)
        f_nf = tex_chip('"nf"', color=FLARE, size=FS_CHIP, pad=0.2)
        f_cm = tex_chip('"cm"', color=GOLD, size=FS_CHIP, pad=0.2)
        f_etc = label("…", size=FS_CHIP, color=MUT)
        ofields = VGroup(f_rk, f_cv, f_nf, f_cm, f_etc)
        ofields.arrange(DOWN, buff=0.24).move_to(orch)
        self.pad_to(AA(["build the tacky on transaction",
                        "build the tachyon transaction"]) - 0.4)
        self.play(ShowCreation(orch), FadeIn(orch_t),
                  LaggedStart(*[FadeIn(f) for f in ofields], lag_ratio=0.12),
                  run_time=1.4)

        # the Tachyon action: just two values
        tach = panel(CARD_W, CARD_H, color=GOLD, fill_opacity=0.05)
        tach.move_to(np.array([CARD_X0, CARD_Y, 0]))
        tach_t = label("Tachyon action", size=FS_BODY, color=GOLD)
        tach_t.next_to(tach, UP, buff=0.16).match_y(orch_t)
        self.pad_to(A("just two values") - 1.2)
        self.play(ShowCreation(tach), FadeIn(tach_t), run_time=0.8)
        t_rk = tex_chip('"rk"', color=GOLD, size=FS_CHIP, pad=0.2)
        t_cv = tex_chip('"cv"', color=GOLD, size=FS_CHIP, pad=0.2)
        t_rk.match_y(f_rk).match_x(tach)
        t_cv.match_y(f_cv).match_x(tach)
        self.pad_to(AA(["a randomized key", "randomized key"]) - 0.2)
        self.play(TransformFromCopy(f_rk, t_rk), run_time=0.7)
        self.pad_to(A("value commitment") - 0.3)
        self.play(TransformFromCopy(f_cv, t_cv), run_time=0.7)

        # "notice what's missing" — nf/cm have no slot
        self.pad_to(A("notice what's missing") - 0.2)
        # the empty slot spans the free space under cv, clear of the chip
        s_top, s_bot = t_cv.get_bottom()[1] - 0.3, tach.get_bottom()[1] + 0.35
        slot = dashed_box(center=np.array([tach.get_x(), (s_top + s_bot) / 2, 0]),
                          w=1.5, h=s_top - s_bot, color=DIM, stroke_width=2.2)
        self.play(ShowCreation(slot), run_time=0.6)
        self.pad_to(AA(["orchard's action", "orchards action"]) - 0.3)
        ring_nf = VGroup(dashed_box(f_nf, color=FLARE, buff=0.08),
                         dashed_box(f_cm, color=GOLD, buff=0.08))
        self.play(ShowCreation(ring_nf), run_time=0.8)
        self.pad_to(AA(["tachyons can't", "tacky ons can't"]) - 0.2)
        nope = label("no slot", size=FS_LABEL, color=FLARE).move_to(slot)
        self.play(FadeIn(nope), run_time=0.6)

        # "pinning a moving part" — nf wiggles
        self.pad_to(A("a moving part") - 0.6)
        self.play(VGroup(f_nf, ring_nf[0]).animate(rate_func=wiggle).shift(RIGHT * 0.15),
                  run_time=1.0)

        # "the tachygrams travel elsewhere — in the stamp": the question's answer
        self.pad_to(A("travel elsewhere") - 0.3)
        pouch = panel(CARD_W, 0.85, color=STAR, fill_opacity=0.05)
        pouch.next_to(tach, DOWN, buff=0.22)
        pouch_t = label("stamp", size=FS_LABEL, color=STAR)
        pouch_t.next_to(pouch, RIGHT, buff=0.25)
        self.play(ShowCreation(pouch), FadeIn(pouch_t), FadeOut(nope),
                  FadeOut(slot), FadeOut(ring_nf), run_time=0.8)
        b1 = bead(FLARE, 0.12).move_to(pouch.get_center() + LEFT * 0.5)
        b2 = bead(GOLD, 0.12).move_to(pouch.get_center() + RIGHT * 0.5)
        # the nf / cm fields themselves leave the Orchard card (one object each)
        # and become the stamp's two tachygram beads
        self.play(f_nf.animate(path_arc=-0.6).scale(0.6).move_to(b1),
                  f_cm.animate(path_arc=-0.6).scale(0.6).move_to(b2), run_time=1.0)
        self.play(FadeTransform(f_nf, b1), FadeTransform(f_cm, b2), run_time=0.45)
        ofields.remove(f_nf, f_cm)
        self.play(b1.animate.set_fill(STAR, 1.0),
                  b2.animate.set_fill(STAR, 1.0), run_time=0.45)
        add_shimmer(VGroup(b1, b2), amp=0.18)

        # make room on the right for the rk story
        cards = VGroup(orch, orch_t, ofields, tach, tach_t, t_rk, t_cv, pouch, pouch_t,
                       b1, b2)
        self.pad_to(AA(["with tacky grams out", "with tachygrams out"]) - 0.2)
        self.play(cards.animate.shift(LEFT * SLIDE), run_time=1.1)

        # alpha = PRF(cm || theta) ties the action to its note
        COL_X = tach.get_right()[0] + 1.6
        alpha_f = mtex('alpha = "PRF"("cm" parallel theta)', size=FS_HEAD, color=GOLD)
        alpha_f.move_to(np.array([0, 1.95, 0])).align_to(np.array([COL_X, 0, 0]), LEFT)
        self.pad_to(A("something else") - 0.3)
        tie = DashedLine(t_rk.get_right() + RIGHT * 0.1,
                         alpha_f.get_left() + LEFT * 0.15,
                         stroke_width=SW_THIN, stroke_color=GOLD)
        self.play(ShowCreation(tie), run_time=0.6)
        self.pad_to(A("alpha is derived") - 0.3)
        self.play(Write(alpha_f, run_time=1.1))

        # spend rk vs output rk
        spend_f = mtex('"spend:" quad "rk" = "ak" + [alpha] G', size=FS_BODY, color=GOLD)
        spend_f.move_to(np.array([0, 1.0, 0])).align_to(alpha_f, LEFT)
        self.pad_to(AA(["a spends rk", "spends rk"]) - 0.2)
        self.play(Write(spend_f, run_time=1.0))
        out_f = mtex('"output:" quad "rk" = [alpha] G', size=FS_BODY, color=AMBER)
        out_f.move_to(np.array([0, 0.2, 0])).align_to(alpha_f, LEFT)
        self.pad_to(AA(["an output's rk", "outputs rk"]) - 0.2)
        self.play(Write(out_f, run_time=1.0))
        noauth = caption("an output carries no authority — the binding signature funds it",
                         color=MUT, size=FS_LABEL)
        self.pad_to(A("no authority") - 0.3)
        self.play(FadeIn(noauth), run_time=0.6)

        # hot device signs outputs; only spends wake the hardware wallet
        hot = key_chip("outputs: a hot device signs", color=AMBER, size=FS_LABEL)
        hot.move_to(np.array([0, -0.85, 0])).align_to(alpha_f, LEFT)
        self.pad_to(A("hot device") - 0.6)
        self.play(FadeIn(hot, shift=LEFT * 0.3), run_time=0.7)
        cold = key_chip("spends: wake the hardware wallet", color=GOLD, size=FS_LABEL)
        cold.next_to(hot, DOWN, buff=0.25).align_to(hot, LEFT)
        self.pad_to(A("hardware wallet") - 0.6)
        self.play(FadeIn(cold, shift=LEFT * 0.3), run_time=0.7)

        # both rk flavors are uniform points
        self.pad_to(A("uniformly random points") - 0.4)
        pt1 = bead(STAR, 0.12)
        pt2 = bead(STAR, 0.12)
        uni_l = label("both rk: uniform points, indistinguishable on chain",
                      size=FS_LABEL, color=STAR)
        uni = VGroup(VGroup(pt1, pt2).arrange(RIGHT, buff=0.25), uni_l)
        uni.arrange(RIGHT, buff=0.3).move_to(UP * CAPTION_Y)
        self.play(FadeOut(noauth),
                  TransformFromCopy(spend_f[-1], pt1),
                  TransformFromCopy(out_f[-1], pt2), FadeIn(uni_l), run_time=1.1)

        # value balance: one line, then move on
        vb = caption("value balance: binding signature, exactly as before ✓",
                     color=MUT, size=FS_LABEL)
        self.pad_to(A("value balance") - 0.3)
        self.play(FadeOut(uni), FadeIn(vb), run_time=0.6)
        self.pad_to(A("moving on") - 0.2)
        self.play(FadeOut(vb), run_time=0.5)

        # ---- the cross-epoch race ------------------------------------------
        # the Tachyon action itself becomes the spend waiting in the mempool
        WALL_X = 1.8
        EPOCH_W = 3.6
        LANE_Y = 0.3
        lane = RoundedRectangle(width=12.4, height=1.8, corner_radius=0.22)
        lane.set_stroke(DIM, SW_THIN, 0.9).set_fill(STAR, 0.02)
        lane.move_to(np.array([0.1, LANE_Y, 0]))
        wall = Line(np.array([WALL_X, LANE_Y - 0.95, 0]), np.array([WALL_X, LANE_Y + 1.0, 0]),
                    stroke_width=SW_BOLD, stroke_color=FLARE)
        EL_Y = LANE_Y + 1.3
        e_l = mtex('e', size=FS_BODY, color=MUT).move_to(np.array([WALL_X - EPOCH_W / 2, EL_Y, 0]))
        e_r = mtex('e + 1', size=FS_BODY, color=MUT).move_to(np.array([WALL_X + EPOCH_W / 2, EL_Y, 0]))
        lane_t = label("mempool", size=FS_LABEL, color=MUT)
        lane_t.move_to(np.array([0, EL_Y, 0])).align_to(lane.get_left() + RIGHT * 0.3, LEFT)

        TX_Y = LANE_Y - 0.05
        tx1 = tx_card('"nf"_e', color=GOLD, bead_colors=[STAR])
        tx1.move_to(np.array([-4.3, TX_Y, 0]))
        clear_shimmer(VGroup(b1, b2))
        rest = VGroup(orch, orch_t, ofields, pouch, pouch_t, b1, b2, tie,
                      alpha_f, spend_f, out_f, hot, cold)
        title_r = scene_title("the epoch rolls over in the mempool")
        self.pad_to(A("now a puzzle") - 0.4)
        self.play(FadeOut(rest), swap_title(title, title_r),
                  ReplacementTransform(tach, tx1[0],
                                       rate_func=squish_rate_func(smooth, 0.3, 1.0)),
                  *[m.animate(rate_func=squish_rate_func(smooth, 0.3, 1.0))
                    .move_to(tx1[0]).scale(0.3).set_opacity(0)
                    for m in (tach_t, t_rk, t_cv)],
                  run_time=1.1)
        self.remove(tach_t, t_rk, t_cv)
        self.play(FadeIn(lane), FadeIn(lane_t), ShowCreation(wall),
                  FadeIn(e_l), FadeIn(e_r), run_time=0.9)
        self.add(tx1[0])     # the lane was drawn after the card: keep the card on top

        # the single-nullifier spend drifts toward the boundary
        self.pad_to(AA(["for epoch e", "for epic e"]) - 0.5)
        self.play(FadeIn(tx1[1], scale=1.4), FadeIn(tx1[2], shift=DOWN * 0.1),
                  run_time=0.6)
        self.remove(*tx1)
        self.add(tx1)
        self.play(tx1.animate.move_to(np.array([-1.6, TX_Y, 0])), run_time=1.8)
        self.pad_to(A("rolls over") - 0.3)
        self.play(tx1.animate.move_to(np.array([0.55, TX_Y, 0])),
                  wall.animate(rate_func=there_and_back).set_stroke(width=9),
                  run_time=1.5)

        # stale at the wall
        self.pad_to(A("now stale") - 0.2)
        stale_x = strike(tx1)
        self.play(ShowCreation(stale_x), tx1.animate.fade(0.5), run_time=0.8)
        stale_t = label("stale", size=FS_BODY, color=FLARE)
        stale_t.next_to(lane, DOWN, buff=0.2).match_x(tx1)
        self.play(FadeIn(stale_t), run_time=0.4)

        # nobody can refresh it but you: not the miner, not the service
        WHO_Y = -1.75
        you = key_chip("only you can re-prove", color=GOLD, size=FS_LABEL)
        miner = key_chip("miner", color=MUT, size=FS_LABEL)
        oss = key_chip("service", color=CYAN, size=FS_LABEL)
        VGroup(you, miner, oss).arrange(RIGHT, buff=0.6).move_to(np.array([0, WHO_Y, 0]))
        self.pad_to(A("but you") - 0.3)
        self.play(FadeIn(you, shift=UP * 0.15), run_time=0.5)
        # each chip is read first (~0.6 s), then struck with a light line that
        # leaves the word legible underneath
        miner_x = strike(miner[0], width=SW_THIN, opacity=0.75)
        oss_x = strike(oss[0], width=SW_THIN, opacity=0.75)
        self.pad_to(AA(["not the minor", "not the miner"]) - 0.5)
        self.play(FadeIn(miner, shift=UP * 0.15), run_time=0.35)
        self.wait(0.6)
        self.play(ShowCreation(miner_x), run_time=0.3)
        self.pad_to(A("not the service") - 0.25)
        self.play(FadeIn(oss, shift=UP * 0.15), run_time=0.35)
        self.wait(0.6)
        self.play(ShowCreation(oss_x), run_time=0.3)
        oss_why = label("never learns future nullifiers", size=FS_SMALL, color=CYAN)
        oss_why.next_to(oss, DOWN, buff=0.2)
        self.pad_to(A("never learns") - 0.2)
        self.play(FadeIn(oss_why, shift=UP * 0.1), run_time=0.6)
        ux = caption("forced refresh: bad UX, and a timing side channel", color=FLARE)
        self.pad_to(AA(["bad ux", "bad u x"]) - 0.3)
        self.play(FadeIn(ux), run_time=0.7)

        # the fix: two adjacent nullifiers, valid across the boundary
        self.pad_to(A("blunt and effective") - 0.3)
        self.play(FadeOut(stale_x), FadeOut(stale_t), FadeOut(ux),
                  FadeOut(VGroup(you, miner, oss, miner_x, oss_x, oss_why)),
                  tx1.animate.fade(0.3), run_time=0.7)
        tx2 = tx_card('"nf"_e, thin "nf"_(e+1)', color=GOLD,
                      bead_colors=[STAR, STAR], w=2.6)
        tx2.move_to(np.array([-4.3, TX_Y, 0]))
        self.pad_to(A("two adjacent nullifiers") - 0.3)
        self.play(FadeIn(tx2, shift=RIGHT * 0.4), FadeOut(tx1), run_time=0.9)
        self.pad_to(AA(["epix e and", "epochs e and"]) - 0.3)
        self.play(Indicate(tx2[2], color=GOLD, scale_factor=1.15), run_time=0.8)
        # the next boundary appears; tx2 crosses the first one still valid
        wall2 = Line(np.array([WALL_X + EPOCH_W, LANE_Y - 0.95, 0]),
                     np.array([WALL_X + EPOCH_W, LANE_Y + 1.0, 0]),
                     stroke_width=SW, stroke_color=DIM)
        e_r2 = mtex('e + 2', size=FS_BODY, color=DIM)
        e_r2.move_to(np.array([WALL_X + EPOCH_W + 0.55, EL_Y, 0]))
        self.play(tx2.animate.move_to(np.array([WALL_X + EPOCH_W / 2, TX_Y, 0])),
                  ShowCreation(wall2), FadeIn(e_r2), run_time=1.5)
        buf = bracket(Line(wall.get_bottom(), wall2.get_bottom()), color=GOLD,
                      buff=0.12, below=True)
        buf_t = label("a full epoch of buffer", size=FS_LABEL, color=GOLD)
        buf_t.next_to(buf, DOWN, buff=0.1)
        self.pad_to(A("full epoch of buffer") - 0.1)
        self.play(GrowFromCenter(buf), FadeIn(buf_t), run_time=0.7)

        # outputs pad with a dummy tachygram
        ROW2_Y = -1.95
        outc = tx_card('"cm"', color=AMBER, bead_colors=[STAR], w=2.2)
        outc[2].set_fill(STAR, 1.0)
        outc[1].shift(LEFT * 0.35)
        outc.move_to(np.array([-4.2, ROW2_Y, 0]))
        o_t = label("output", size=FS_LABEL, color=AMBER).next_to(outc, LEFT, buff=0.25)
        self.pad_to(A("stay indistinguishable") - 0.9)
        self.play(FadeIn(outc, shift=UP * 0.2), FadeIn(o_t), run_time=0.8)
        dummy = bead(STAR, 0.11)
        dummy.move_to(outc[1].get_center() + RIGHT * 0.7)
        dummy_ring = Circle(radius=0.2).set_stroke(MUT, 2.0, 0.9)
        dummy_ring.set_fill(opacity=0)
        dummy_ring.move_to(dummy)
        dummy_t = label("dummy", size=FS_SMALL, color=MUT)
        dummy_t.next_to(outc, DOWN, buff=0.15).match_x(dummy)
        self.pad_to(AA(["dummy tacky gram", "dummy tachygram"]) - 0.3)
        self.play(FadeIn(dummy, scale=1.6), ShowCreation(dummy_ring),
                  FadeIn(dummy_t), run_time=0.9)

        # two tachygrams per action, always — identical dominoes
        self.pad_to(A("per action") - 0.8)
        dom1 = domino().move_to(np.array([-0.95, ROW2_Y, 0]))
        dom2 = domino().move_to(np.array([0.95, ROW2_Y, 0]))
        always = caption("two tachygrams per action — always", color=STAR)
        # card -> card, tachygram beads -> pips; the tags and the dummy ring dissolve
        self.play(ReplacementTransform(tx2[0], dom2[0]),
                  ReplacementTransform(tx2[1], dom2[1]),
                  FadeOut(tx2[2], shift=DOWN * 0.3),
                  ReplacementTransform(outc[0], dom1[0]),
                  ReplacementTransform(VGroup(outc[1][0], dummy), dom1[1]),
                  FadeOut(outc[2]), FadeOut(dummy_ring),
                  FadeOut(o_t), FadeOut(dummy_t), FadeOut(buf), FadeOut(buf_t),
                  run_time=1.2)
        self.play(FadeIn(always), run_time=0.5)

        # without padding, arity leaks the split
        self.pad_to(A("without the padding") - 0.2)
        leak = mtex('"spends" = t - n', size=FS_BODY, color=FLARE)
        leak.move_to(np.array([4.0, ROW2_Y + 0.3, 0]))
        self.play(Write(leak, run_time=0.9))
        self.pad_to(A("would leak") - 0.1)
        padfix = mtex('t = 2 n', size=FS_BODY, color=STAR)
        padfix.next_to(leak, DOWN, buff=0.3)
        leak_x = strike(leak)
        self.play(ShowCreation(leak_x), FadeIn(padfix, shift=UP * 0.15),
                  run_time=0.9)

        # ---- the stamp -------------------------------------------------------
        # built centered; it slides left when aggregation needs the right half
        self.pad_to(A("packaged by the stamp") - 0.4)
        race = VGroup(lane, lane_t, wall, wall2, e_l, e_r, e_r2,
                      leak, leak_x, padfix, always)
        stamp = panel(7.0, 3.0, color=STAR, fill_opacity=0.04)
        stamp.move_to(np.array([0, 0.95, 0]))
        title2 = scene_title("the stamp")
        self.play(FadeOut(race), swap_title(title_r, title2),
                  dom1.animate.scale(0.75).move_to(stamp.get_center() + UP * 0.85 + LEFT * 0.9),
                  dom2.animate.scale(0.75).move_to(stamp.get_center() + UP * 0.85 + RIGHT * 0.9),
                  ShowCreation(stamp), run_time=1.3)
        sub = label("the bundle's PCD proof", size=FS_LABEL, color=MUT)
        sub.next_to(title2, RIGHT, buff=0.4)
        VGroup(title2.generate_target(), sub).arrange(RIGHT, buff=0.4, aligned_edge=DOWN)
        VGroup(title2.target, sub).move_to(UP * TITLE_Y)
        self.pad_to(AA(["pcd proof", "p c d proof"]) - 0.3)
        self.play(MoveToTarget(title2), FadeIn(sub, shift=LEFT * 0.2), run_time=0.7)

        # public inputs: acc_act, acc_tg, anchor
        pi_t = label("public inputs", size=FS_SMALL, color=MUT)
        pi_t.move_to(stamp.get_center() + DOWN * 0.05)
        self.pad_to(A("public inputs") - 0.2)
        self.play(FadeIn(pi_t), run_time=0.5)
        c_act = tex_chip('"acc"_"act"', color=GOLD, size=FS_BODY)
        c_tg = tex_chip('"acc"_"tg"', color=STAR, size=FS_BODY)
        c_anchor = key_chip("anchor", color=CYAN, size=FS_BODY)
        pis = VGroup(c_act, c_tg, c_anchor)
        pis.arrange(RIGHT, buff=0.45).move_to(stamp.get_center() + DOWN * 0.8 + LEFT * 0.45)
        self.pad_to(A("action descriptions") - 0.4)
        self.play(FadeIn(c_act, scale=1.1), run_time=0.7)
        act_sub = mtex('"acc"_"act" = "Com"(product_i (X - "Pos"("rk"_i, "cv"_i)))',
                       size=FS_LABEL, color=TXT)
        act_sub.next_to(stamp, DOWN, buff=0.3).align_to(stamp, LEFT)
        self.play(FadeIn(act_sub), run_time=0.6)
        self.pad_to(AA(["gram accumulator", "tachygram accumulator"]) - 0.3)
        self.play(FadeIn(c_tg, scale=1.1), run_time=0.7)
        self.pad_to(A("called an anchor") - 0.3)
        self.play(FadeIn(c_anchor, scale=1.1), run_time=0.7)
        nxt = label("built next", size=FS_SMALL, color=CYAN)
        nxt.next_to(c_anchor, RIGHT, buff=0.25)       # inside the stamp, beside it
        self.pad_to(A("a new word") - 0.2)
        self.play(FadeIn(nxt), Indicate(c_anchor, color=CYAN, scale_factor=1.12),
                  run_time=0.9)

        # the tachygram list rides in public; both accumulators audited
        tg_list = VGroup(*[bead(STAR, 0.1) for _ in range(6)])
        tg_list.arrange(RIGHT, buff=0.3)
        tg_list.next_to(act_sub, DOWN, buff=0.45).align_to(stamp, LEFT).shift(RIGHT * 0.15)
        list_t = label("published tachygram list", size=FS_SMALL, color=MUT)
        list_t.next_to(tg_list, RIGHT, buff=0.35)
        self.pad_to(A("rides along") - 0.4)
        self.play(LaggedStart(*[FadeIn(m, scale=1.4) for m in tg_list], lag_ratio=0.1),
                  FadeIn(list_t), run_time=0.9)
        add_shimmer(tg_list, amp=0.2)
        audit_eq = mtex('y_r = product_i (r - "tg"_i)', size=FS_LABEL, color=GOLD)
        audit_ok = checkmark(0.3, color=GOLD)
        audit = VGroup(audit_eq, audit_ok).arrange(RIGHT, buff=0.25)
        audit.move_to(UP * CAPTION_Y).align_to(stamp, LEFT)
        self.pad_to(A("audited against their lists") - 0.3)
        self.play(FadeIn(audit, shift=UP * 0.15), run_time=0.8)

        # stamps aggregate — the stamp makes room, many fold into one
        stamp_grp = VGroup(stamp, pi_t, pis, act_sub, tg_list, list_t,
                           audit, dom1, dom2, nxt)
        self.pad_to(A("stamps also aggregate") - 0.4)
        AGG_L, AGG_R = 2.4, 4.7      # constituents column, aggregate column
        self.play(stamp_grp.animate.shift(LEFT * 2.3), run_time=0.7)
        minis = VGroup(*[proof_card(0.95) for _ in range(3)])
        minis.arrange(DOWN, buff=0.35).move_to(np.array([AGG_L, 0.95, 0]))
        self.play(LaggedStart(*[FadeIn(m, shift=LEFT * 0.2) for m in minis],
                              lag_ratio=0.15), run_time=0.8)
        agg = proof_card(1.6).move_to(np.array([AGG_R, 0.95, 0]))
        agg_t = label("aggregate", size=FS_LABEL, color=GOLD).next_to(agg, UP, buff=0.18)
        self.pad_to(A("folded into one proof") - 0.3)
        self.play(*[m.animate.scale(0.4).move_to(agg).fade(1) for m in minis],
                  FadeIn(agg, scale=1.1), FadeIn(agg_t), run_time=1.2)
        self.remove(minis)
        refs = VGroup(*[mtex('"tx"_' + str(i + 1), size=FS_LABEL, color=MUT)
                        .move_to(np.array([AGG_L, 1.95 - i * 1.0, 0]))
                        for i in range(3)])
        arrows = VGroup(*[tarrow(r, agg, color=DIM, buff=0.15) for r in refs])
        self.pad_to(A("pointing at the aggregate") - 0.4)
        self.play(LaggedStart(*[FadeIn(r) for r in refs], lag_ratio=0.15),
                  LaggedStart(*[grow_tarrow(a) for a in arrows], lag_ratio=0.15),
                  run_time=1.0)
        later = key_chip("details: after the proof tree", color=MUT, size=FS_SMALL)
        later.next_to(VGroup(refs, agg), DOWN, buff=0.45)
        self.pad_to(A("story comes later") - 0.3)
        self.play(FadeIn(later), run_time=0.6)

        # ---- memo / txid hygiene --------------------------------------------
        # the stamp becomes the stamp entry of the authorizing data; the two
        # action dominoes become the actions entry of the effecting data
        PX = -2.0
        ID_X = 4.0
        EFF_Y, AUTH_Y = 0.8, -1.5
        eff = panel(6.0, 1.9, color=GOLD, fill_opacity=0.04)
        eff.move_to(np.array([PX, EFF_Y, 0]))
        eff_t = label("effecting data", size=FS_LABEL, color=GOLD)
        eff_t.move_to(eff.get_corner(UL) + np.array([0.25, -0.35, 0]), aligned_edge=LEFT)
        e_act = key_chip("actions (rk, cv)", color=GOLD, size=FS_LABEL)
        e_da = tex_chip('"da_digest"', color=GOLD, size=FS_LABEL)
        VGroup(e_act, e_da).arrange(RIGHT, buff=0.4).move_to(eff.get_center() + DOWN * 0.3)
        txid = tex_chip('"txid"', color=GOLD, size=FS_BODY)
        txid.move_to(np.array([ID_X, EFF_Y, 0]))
        a1 = tarrow(eff, txid, color=GOLD, width=SW)
        auth = panel(6.0, 1.9, color=AMBER, fill_opacity=0.04)
        auth.move_to(np.array([PX, AUTH_Y, 0]))
        auth_t = label("authorizing data", size=FS_LABEL, color=AMBER)
        auth_t.move_to(auth.get_corner(UL) + np.array([0.25, -0.35, 0]), aligned_edge=LEFT)
        au_sig = key_chip("auth sigs", color=AMBER, size=FS_LABEL)
        au_st = tex_chip('"stamp" thin pi', color=AMBER, size=FS_LABEL)
        VGroup(au_sig, au_st).arrange(RIGHT, buff=0.5).move_to(auth.get_center() + DOWN * 0.3)
        wtxid = tex_chip('"wtxid"', color=AMBER, size=FS_BODY)
        wtxid.move_to(np.array([ID_X, AUTH_Y, 0]))
        a2 = tarrow(auth, wtxid, color=AMBER, width=SW)
        title_m = scene_title("last housekeeping: the memo")

        self.pad_to(A("last housekeeping") - 1.4)
        clear_shimmer(tg_list)
        self.play(FadeOut(VGroup(agg, agg_t, refs, arrows, later)),
                  FadeOut(VGroup(pi_t, pis, act_sub, tg_list, list_t, audit, nxt)),
                  FadeOut(dom1[1]), FadeOut(dom2[1]),
                  swap_title(VGroup(title2, sub), title_m), run_time=0.7)
        self.play(ReplacementTransform(stamp, au_st[0]),
                  ReplacementTransform(dom1[0], e_act[0]),
                  dom2[0].animate.move_to(e_act[0]).match_height(e_act[0]).set_opacity(0),
                  run_time=0.8)
        self.remove(dom2)
        self.play(FadeIn(au_st[1]), FadeIn(e_act[1]),
                  ShowCreation(eff), FadeIn(eff_t), ShowCreation(auth), FadeIn(auth_t),
                  FadeIn(au_sig), grow_tarrow(a1), grow_tarrow(a2),
                  FadeIn(txid), FadeIn(wtxid), run_time=0.8)
        self.add(e_act, au_st)       # keep the morphed chips above their panels

        # the memo commits into txid via da_digest
        memo = tex_chip('"memo" = ("tag", "ct")', color=STAR, size=FS_LABEL)
        memo.move_to(np.array([e_da.get_x(), 2.3, 0]))
        self.pad_to(A("the memo") - 0.2)
        self.play(FadeIn(memo, shift=DOWN * 0.2), run_time=0.7)
        self.pad_to(A("dedicated digest") - 0.6)
        self.play(FadeTransform(memo.copy(), e_da),
                  memo.animate.fade(0.4), run_time=1.0)
        self.pad_to(AA(["affecting data", "effecting data"]) - 0.3)
        self.play(Indicate(eff_t, color=GOLD, scale_factor=1.1), run_time=0.7)

        # aggregation rewrites the stamp — authorizing data is malleable
        self.pad_to(A("aggregation rewrites") - 0.3)
        new_st = tex_chip('"stamp" thin pi\'', color=AMBER, size=FS_LABEL)
        new_st.move_to(au_st)
        self.play(au_st.animate.shift(DOWN * 0.6).set_opacity(0),
                  FadeIn(new_st, shift=DOWN * 0.3),
                  Indicate(wtxid, color=AMBER, scale_factor=1.12), run_time=1.1)
        self.remove(au_st)
        mal = label("rewritable in flight", size=FS_SMALL, color=AMBER)
        mal.move_to(auth.get_corner(UR) + np.array([-0.25, -0.35, 0]), aligned_edge=RIGHT)
        self.pad_to(A("rewritable in flight") - 0.4)
        self.play(FadeIn(mal), run_time=0.6)

        # the memo isn't: every auth signature covers da_digest
        self.pad_to(AA(["memo isn't", "memo isnt"]) - 0.2)
        shield = RoundedRectangle(width=e_da.get_width() + 0.18,
                                  height=e_da.get_height() + 0.18, corner_radius=0.14)
        shield.move_to(e_da).set_stroke(GOLD, 3.5, 1.0).set_fill(opacity=0)
        self.play(ShowCreation(shield), run_time=0.7)
        cover = curved_tarrow(au_sig.get_top() + 0.06 * UP,
                              shield.get_bottom() + 0.06 * DOWN, angle=-0.7,
                              color=GOLD)
        gap_y = (eff.get_bottom()[1] + auth.get_top()[1]) / 2
        arc_pts = [cover[0].point_from_proportion(a / 40) for a in range(41)]
        cross = min(arc_pts, key=lambda q: abs(q[1] - gap_y))
        sig_t = label("signed over", size=FS_SMALL, color=GOLD)
        sig_t.move_to(np.array([cross[0] + 0.3, gap_y, 0]), aligned_edge=LEFT)
        self.pad_to(A("signature covers") - 0.3)
        self.play(grow_tarrow(cover), FadeIn(sig_t), run_time=0.9)

        # relayers: proof replaceable, payload sealed
        rel1 = label("proof: replaceable", size=FS_LABEL, color=AMBER)
        rel1.next_to(wtxid, DOWN, buff=0.3)
        self.pad_to(AA(["relayers can replace", "relayers"]) - 0.2)
        self.play(FadeIn(rel1), run_time=0.6)
        rel2 = label("payload: sealed", size=FS_LABEL, color=GOLD)
        rel2.next_to(txid, DOWN, buff=0.3)
        self.pad_to(A("cannot touch") - 0.2)
        self.play(FadeIn(rel2), run_time=0.6)

        # ZIP-244 made the same call
        zip_c = key_chip("ZIP 244 made the same call", color=STAR, size=FS_LABEL)
        zip_c.move_to(UP * CAPTION_Y)
        self.pad_to(AA(["zip 244", "zip two forty four"]) - 0.2)
        self.play(FadeIn(zip_c, shift=UP * 0.2), run_time=0.8)
        self.pad_to(scene_T("3.2"))

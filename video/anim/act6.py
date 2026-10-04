"""Act 6 — the proof tree: shared evidence. Anchored to anim/words.json.

Render:  ./qa.sh act6.py Scene61   (one scene at a time; see AGENT_GUIDE.md)

Scene chaining: every scene after 6.1 opens on the previous scene's final frame,
rebuilt by the module-level builders below (bridge61/legend61, build62/final62,
tally63, timeline64/final64), and grows its first beat out of it.
"""

import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manimlib import *
from style import *


# ---- act-6 glyph helpers ----------------------------------------------------

def step_pill(name, color=GOLD, size=FS_LABEL):
    """A proof-tree step: stadium pill with the spec's step name."""
    return pill(name, color=color, size=size)


def header_box(tex, color=GOLD, size=26, pad=0.18):
    """A PCD header: sharp-cornered box around its mono name + fields."""
    t = mtex(tex, size=size, color=color)
    box = RoundedRectangle(width=t.get_width() + 2 * pad,
                           height=t.get_height() + 2.6 * pad,
                           corner_radius=0.05)
    box.set_fill(color, 0.07)
    box.set_stroke(color, SW_THIN, 0.85)
    box.move_to(t)
    return VGroup(box, t)


def flow(a, b, color=MUT, buff=0.1):
    """Edge-to-edge diagram arrow (mobject endpoints snap to facing edges)."""
    return tarrow(a, b, color=color, width=SW_THIN, buff=buff)


def mini_tree(s=1.0, color=STAR):
    """Evidence tree: root, two internals, four leaf buckets."""
    root = Dot(radius=0.07 * s).set_fill(color, 1.0).move_to(UP * 0.5 * s)
    l1 = Dot(radius=0.06 * s).set_fill(color, 0.95).move_to(LEFT * 0.34 * s)
    r1 = Dot(radius=0.06 * s).set_fill(color, 0.95).move_to(RIGHT * 0.34 * s)
    leaves = VGroup(*[Square(side_length=0.18 * s)
                      .set_fill(color, 0.3).set_stroke(color, 1.6, 0.9)
                      for _ in range(4)])
    leaves.arrange(RIGHT, buff=0.12 * s).move_to(DOWN * 0.45 * s)
    sw = dict(stroke_width=2.0, stroke_color=color, stroke_opacity=0.75)
    edges = VGroup(
        Line(root.get_center(), l1.get_center(), **sw),
        Line(root.get_center(), r1.get_center(), **sw),
        Line(l1.get_center(), leaves[0].get_top(), **sw),
        Line(l1.get_center(), leaves[1].get_top(), **sw),
        Line(r1.get_center(), leaves[2].get_top(), **sw),
        Line(r1.get_center(), leaves[3].get_top(), **sw),
    )
    return VGroup(edges, root, l1, r1, leaves)


def sentinel_gate(h=1.0, color=STAR):
    bar = RoundedRectangle(width=0.16, height=h, corner_radius=0.07)
    bar.set_fill(color, 0.75)
    bar.set_stroke(color, 1.8, 0.95)
    return bar


def eq_pin(m1, m2, color=STAR, sym="="):
    """Equality bridge between two fields: two line stubs + medallion."""
    a = m1.get_right() + 0.15 * RIGHT
    b = m2.get_left() + 0.15 * LEFT
    mid = (a + b) / 2
    r = 0.2 if len(sym) == 1 else 0.27
    u = (b - a) / max(np.linalg.norm(b - a), 1e-9)
    sw = dict(stroke_width=SW_THIN, stroke_color=color, stroke_opacity=0.9)
    ln = VGroup(Line(a, mid - u * r, **sw), Line(mid + u * r, b, **sw))
    med = Circle(radius=r).move_to(mid).set_fill(VOID, 1.0)
    med.set_stroke(color, 1.8, 0.95)
    eq = mtex(sym, size=FS_SMALL, color=color).move_to(med)
    return VGroup(ln, med, eq)


def check_row(text, size=FS_SMALL, color=MUT, math=False):
    """Checklist row: empty box + text. The tick goes into row[0] later."""
    box = Square(0.26).set_stroke(MUT, 1.8, 0.9).set_fill(opacity=0)
    t = mtex(text, size=size, color=color) if math else label(text, size=size, color=color)
    return VGroup(box, t).arrange(RIGHT, buff=0.22)


def stamp_chip(color=GOLD, size=26):
    return header_box('mono("Stamp"){"acc"_"act", "acc"_"tg", "anchor"}',
                      color=color, size=size)


def strike(mob, color=FLARE):
    """Deliberate strike-through (a polyline, so the layout linter ignores it)."""
    vm = VMobject()
    vm.set_points_as_corners([mob.get_corner(DL) + 0.08 * DL, mob.get_corner(UR) + 0.08 * UR])
    vm.set_stroke(color, SW_BOLD, 1.0)
    return vm


def x_mark(center, r=0.17, color=FLARE, width=SW_BOLD):
    """A two-stroke X (polylines, so the linter does not read it as a crossing line)."""
    out = VGroup()
    for d1, d2 in ((UL, DR), (UR, DL)):
        vm = VMobject()
        vm.set_points_as_corners([center + r * d1, center + r * d2])
        vm.set_stroke(color, width, 1.0)
        out.add(vm)
    return out


def lane(y0, y1, color, name, x0=-6.6, x1=4.2):
    """A role lane: faint band + italic role name at its top-left."""
    band = RoundedRectangle(width=x1 - x0, height=y1 - y0, corner_radius=0.18)
    band.move_to(np.array([(x0 + x1) / 2, (y0 + y1) / 2, 0]))
    band.set_fill(color, 0.045)
    band.set_stroke(color, 1.6, 0.35)
    t = itex(name, size=FS_SMALL, color=color)
    t.move_to(band.get_corner(UL) + np.array([0.15 + t.get_width() / 2, -0.24, 0]))
    return VGroup(band, t)


def swap(old, new, lag=0.85):
    """Staggered swap for different text: old fully out, then new in (no stacking)."""
    return LaggedStart(FadeOut(old, shift=UP * 0.15), FadeIn(new, shift=UP * 0.15),
                       lag_ratio=lag)


def absorb(mob, target):
    """Animation: mob flies into target's center, shrinking and fading (consumed)."""
    return mob.animate.move_to(target.get_center()).scale(0.2).set_opacity(0)


# ---- the epoch axis used by 6.3 --------------------------------------------
AX_Y = -2.5
AX_X0 = -6.1
AX_DX = 1.72


def slot_x(i):
    return AX_X0 + AX_DX * i


def epoch_axis63(n=8):
    axis = Line(np.array([AX_X0 - 0.45, AX_Y, 0]),
                np.array([slot_x(n - 1) + 0.6, AX_Y, 0]),
                stroke_width=SW_THIN, stroke_color=DIM)
    ticks = VGroup()
    for i in range(n):
        if i == 1:
            t = mtex('e_"incl"', size=FS_SMALL, color=GOLD)
        else:
            t = mtex(f'e_{i}', size=FS_SMALL, color=MUT)
        t.move_to(np.array([slot_x(i), AX_Y - 0.36, 0]))
        ticks.add(t)
    slots = [np.array([slot_x(i), AX_Y + 0.3, 0]) for i in range(n)]
    return axis, ticks, slots


def sentinel_pos(i):
    """Sentinel between epochs i-1 and i, on the axis."""
    return np.array([slot_x(i) - AX_DX / 2, AX_Y, 0])


# ---- 6.1 final-frame builders (also used to open 6.2) -----------------------
TX61 = 1.0                              # tree center x
BRIDGE_REGION = (-6.6, 0.9, -2.3, 2.3)  # where the bridge sits beside the legend


def bridge61():
    """Parent step + two child headers + equality pins, at their center layout."""
    B = SimpleNamespace()
    B.root = step_pill("step", color=GOLD, size=FS_BODY).move_to(np.array([TX61, 1.75, 0]))
    B.f_l = VGroup(mtex('"cm"', size=FS_BODY, color=GOLD),
                   mtex('"sntl"_e', size=FS_BODY, color=GOLD),
                   mtex('e', size=FS_BODY, color=GOLD))
    B.f_r = VGroup(mtex('"cm"', size=FS_BODY, color=CYAN),
                   mtex('"sntl"_e', size=FS_BODY, color=CYAN),
                   mtex('e + 1', size=FS_BODY, color=CYAN))
    for f in (B.f_l, B.f_r):
        f.arrange(DOWN, buff=0.38)
    box_l = panel(2.1, 2.3, color=GOLD, fill_opacity=0.05)
    box_r = panel(2.1, 2.3, color=CYAN, fill_opacity=0.05)
    box_l.move_to(np.array([TX61 - 3.0, -0.75, 0]))
    box_r.move_to(np.array([TX61 + 3.0, -0.75, 0]))
    B.f_l.move_to(box_l)
    B.f_r.move_to(box_r)
    for a_, b_ in zip(B.f_l, B.f_r):
        b_.match_y(a_)
    B.box_l, B.box_r = box_l, box_r
    B.hdr_l = VGroup(box_l, B.f_l)
    B.hdr_r = VGroup(box_r, B.f_r)
    B.hl_t = label("left header", size=FS_SMALL, color=GOLD).next_to(box_l, DOWN, buff=0.15)
    B.hr_t = label("right header", size=FS_SMALL, color=CYAN).next_to(box_r, DOWN, buff=0.15)
    B.rd = VGroup(flow(box_l, B.root), flow(box_r, B.root))
    B.pins = VGroup(eq_pin(B.f_l[0], B.f_r[0]), eq_pin(B.f_l[1], B.f_r[1]),
                    eq_pin(B.f_l[2], B.f_r[2], sym="+1"))
    B.grp = VGroup(B.root, B.hdr_l, B.hdr_r, B.rd, B.pins, B.hl_t, B.hr_t)
    return B


def legend61():
    """The three-color legend panel with white's two forms and the reusing wallets."""
    L = SimpleNamespace()
    L.lg = panel(5.4, 5.5, color=MUT, fill_opacity=0.03).move_to(np.array([3.95, 0.0, 0]))
    rows = []
    for sw_color, main, sub in (
            (GOLD, "wallet", "sees the note"),
            (CYAN, "service", "sees opaque values"),
            (STAR, "shared evidence", "reused by everyone")):
        sw = Square(side_length=0.36).set_fill(sw_color, 0.85).set_stroke(sw_color, 1.5, 0.95)
        t1 = label(main, size=FS_BODY, color=sw_color)
        t2 = label(sub, size=FS_SMALL, color=TXT)
        txt = VGroup(t1, t2).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        rows.append(VGroup(sw, txt).arrange(RIGHT, buff=0.35))
    L.rows = VGroup(*rows).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
    L.rows.move_to(L.lg.get_center() + UP * 1.15).align_to(L.lg.get_left() + RIGHT * 0.45, LEFT)
    seg = VGroup(*[block(0.5, 0.36) for _ in range(3)]).arrange(RIGHT, buff=0.26)
    L.chainseg = VGroup(seg, VGroup(chain_link(seg[0], seg[1]), chain_link(seg[1], seg[2])))
    L.tr = mini_tree(1.15)
    VGroup(L.chainseg, L.tr).arrange(RIGHT, buff=1.0).move_to(L.lg.get_center() + DOWN * 0.85)
    L.tr_t = label("closed epochs", size=FS_MIN, color=MUT).next_to(L.tr, DOWN, buff=0.14)
    L.cs_t = label("active epoch", size=FS_MIN, color=MUT).match_y(L.tr_t)
    L.cs_t.match_x(L.chainseg)
    L.wallets = VGroup(*[key_chip("wallet", color=GOLD, size=FS_MIN) for _ in range(3)])
    L.wallets.arrange(RIGHT, buff=0.3).move_to(L.lg.get_center() + DOWN * 2.25)
    L.closing = caption("one party's work, everyone's evidence", color=STAR)
    L.title = scene_title("three colors, three roles")
    return L


class Scene61(TimedScene):
    """6.1 — Steps, headers, bridging."""

    def construct(self):
        A = lambda p, o=1: anchor("6.1", p, o)
        AA = lambda ps, o=1: anchor_any("6.1", ps, o)

        # "we have all the parts" — one recap chip per spoken part
        parts = VGroup(
            key_chip("evolving nullifiers", color=FLARE, size=FS_BODY),
            key_chip("accumulators", color=AMBER, size=FS_BODY),
            key_chip("anchors", color=STAR, size=FS_BODY),
            key_chip("evidence trees", color=STAR, size=FS_BODY),
        )
        parts.arrange(RIGHT, buff=0.45).move_to(UP * 0.3)
        for i, ph in enumerate(("evolving", "accumulators", "anchors", "evidence trees")):
            self.pad_to(A(ph) - 0.3)
            self.play(FadeIn(parts[i], shift=DOWN * 0.2), run_time=0.6)

        # "one spendability proof" — the parts are consumed into one proof card
        card = proof_card(1.8).move_to(UP * 1.0)
        t1 = scene_title("one proof, many contributors")
        self.pad_to(A("spendability proof") - 0.6)
        self.play(LaggedStart(*[absorb(p, card) for p in parts], lag_ratio=0.08),
                  FadeIn(card, scale=1.5), FadeIn(t1, shift=DOWN * 0.15), run_time=1.0)
        self.remove(parts)

        # "pieces made by different parties who must learn nothing"
        trio = VGroup()
        icons = [proof_token(0.2),
                 VGroup(*[bead(CYAN, 0.08) for _ in range(4)]).arrange(RIGHT, buff=0.16),
                 mini_tree(1.1)]
        for col, ic, nm in ((GOLD, icons[0], "wallet"), (CYAN, icons[1], "service"),
                            (STAR, icons[2], "everyone")):
            p = panel(2.4, 1.5, color=col, fill_opacity=0.06)
            ic.move_to(p)
            t = itex(nm, size=FS_LABEL, color=col).next_to(p, DOWN, buff=0.15)
            trio.add(VGroup(p, ic, t))
        trio.arrange(RIGHT, buff=1.3).move_to(DOWN * 1.45)
        self.pad_to(A("different parties") - 0.5)
        self.play(LaggedStartMap(lambda m: FadeIn(m, scale=1.1), trio,
                                 lag_ratio=0.2), run_time=0.9)
        xs = VGroup()
        for i in range(2):
            mid = (trio[i][0].get_right() + trio[i + 1][0].get_left()) / 2
            xs.add(x_mark(mid))
        self.pad_to(A("learn nothing") - 0.4)
        self.play(LaggedStartMap(ShowCreation, xs, lag_ratio=0.4), run_time=0.6)

        # "three monolithic statements: output, spend, bundle"
        self.pad_to(A("three monolithic") - 0.7)
        self.play(FadeOut(trio), FadeOut(xs),
                  card.animate.scale(0.6).to_corner(UR, buff=0.45).fade(0.3),
                  run_time=0.9)
        slabs = VGroup()
        for name in ("Output", "Spend", "Bundle"):
            s = panel(2.6, 3.2, color=MUT, fill_opacity=0.04)
            t = label(name, size=FS_BODY, color=TXT).move_to(s.get_top() + DOWN * 0.45)
            lines = VGroup(*[Line(LEFT * 0.85, RIGHT * (0.85 - 0.35 * (i % 3 == 2)),
                                  stroke_width=2.2, stroke_color=DIM)
                             .shift(DOWN * 0.36 * i) for i in range(6)])
            lines.next_to(t, DOWN, buff=0.35)
            lines.align_to(s.get_left() + RIGHT * 0.45, LEFT)
            slabs.add(VGroup(s, lines, t))
        slabs.arrange(RIGHT, buff=0.6).move_to(DOWN * 0.45)
        self.play(LaggedStart(*[FadeIn(VGroup(sl[0], sl[1]), shift=UP * 0.25) for sl in slabs],
                              lag_ratio=0.25), run_time=1.1)
        for i, ph in enumerate(("output", "spend", "bundle")):
            self.pad_to(A(ph) - 0.25)
            self.play(FadeIn(slabs[i][2], shift=DOWN * 0.1),
                      slabs[i][0].animate.set_stroke(STAR, opacity=1.0), run_time=0.45)

        # "think of them as the contract"
        br = bracket(slabs, color=STAR, buff=0.25)
        contract = itex("the contract", size=FS_BODY, color=STAR)
        contract.next_to(br, UP, buff=0.18)
        self.pad_to(A("the contract") - 0.5)
        self.play(GrowFromCenter(br), FadeIn(contract),
                  *[sl[0].animate.set_stroke(MUT, opacity=0.8) for sl in slabs], run_time=0.8)

        # "the realization is a tree of steps": the contract docks top-left and the
        # spendability proof (docked top-right) becomes the tree's root step
        self.pad_to(A("realization") - 0.4)
        minis = VGroup()
        for name in ("Output", "Spend", "Bundle"):
            mp = panel(1.75, 0.72, color=MUT, fill_opacity=0.05)
            mt = label(name, size=FS_LABEL, color=TXT).move_to(mp)
            minis.add(VGroup(mp, mt))
        minis.arrange(RIGHT, buff=0.15)
        mini_t = itex("the contract", size=FS_SMALL, color=STAR)
        mini_t.next_to(minis, UP, buff=0.12)
        slabdock = VGroup(mini_t, minis)
        slabdock.move_to(np.array([0, 0, 0])).align_to(np.array([-6.6, STAGE_TOP, 0]), UL)
        t2 = scene_title("the proof tree")

        root = step_pill("step", color=GOLD, size=FS_BODY).move_to(np.array([TX61, 1.5, 0]))
        chl = step_pill("step", color=GOLD, size=FS_BODY).move_to(np.array([TX61 - 3.0, -0.3, 0]))
        chr_ = step_pill("step", color=CYAN, size=FS_BODY).move_to(np.array([TX61 + 3.0, -0.3, 0]))
        toks = VGroup(*[proof_token(0.15).move_to(np.array([TX61 + x, -2.2, 0]))
                        for x in (-4.2, -1.8, 1.8, 4.2)])
        edges = VGroup(
            flow(chl, root), flow(chr_, root),
            flow(toks[0], chl), flow(toks[1], chl),
            flow(toks[2], chr_), flow(toks[3], chr_),
        )
        self.play(*[ReplacementTransform(slabs[i][0], minis[i][0]) for i in range(3)],
                  *[ReplacementTransform(slabs[i][2], minis[i][1]) for i in range(3)],
                  *[FadeOut(slabs[i][1], shift=UP * 0.3) for i in range(3)],
                  ReplacementTransform(contract, mini_t), FadeOut(br),
                  absorb(card, root), FadeIn(root, scale=1.5), swap(t1, t2), run_time=1.1)
        self.remove(card)
        self.play(LaggedStart(FadeIn(chl), FadeIn(chr_), ShowCreation(edges[0]),
                              ShowCreation(edges[1]), lag_ratio=0.15), run_time=0.9)
        self.play(LaggedStart(*[AnimationGroup(FadeIn(toks[i]), ShowCreation(edges[2 + i]))
                                for i in range(4)], lag_ratio=0.12), run_time=0.9)

        # "one bounded circuit... takes up to two child proofs"
        self.pad_to(A("bounded circuit") - 0.4)
        self.play(Indicate(root, color=GOLD, scale_factor=1.12), run_time=0.8)
        self.pad_to(A("two child proofs") - 0.4)
        gl = proof_token(0.11).move_to(chl.get_top() + UP * 0.32)
        gr = proof_token(0.11).move_to(chr_.get_top() + UP * 0.32)
        slot_y = root.get_bottom()[1] - 0.32
        self.play(FadeIn(gl, scale=1.5), FadeIn(gr, scale=1.5), run_time=0.4)
        self.play(gl.animate.move_to(np.array([TX61 - 0.6, slot_y, 0])),
                  gr.animate.move_to(np.array([TX61 + 0.6, slot_y, 0])), run_time=0.7)

        # "verifies part of the contract": a fragment of Spend joins the inputs
        self.pad_to(A("part of the contract") - 0.6)
        frag = panel(0.5, 0.3, color=MUT, fill_opacity=0.25).move_to(np.array([TX61, slot_y, 0]))
        self.play(TransformFromCopy(minis[1][0], frag), Indicate(minis[1], color=STAR),
                  run_time=0.8)

        # "folds everything into a new proof"
        self.pad_to(A("folds everything") - 0.3)
        out_tok = proof_token(0.16).move_to(root.get_top() + UP * 0.6)
        self.play(absorb(gl, root), absorb(gr, root), absorb(frag, root),
                  root[0].animate(rate_func=there_and_back).scale(0.9), run_time=0.8)
        self.remove(gl, gr, frag)
        self.play(FadeIn(out_tok, scale=1.5, shift=UP * 0.2), run_time=0.5)

        # "what a step publishes is its header"
        t3 = scene_title("what a step promises")
        self.pad_to(A("publishes") - 0.5)
        self.play(swap(t2, t3), run_time=0.9)
        self.pad_to(A("its header") - 0.5)
        hdr = header_box('{e, "cm", "sntl", dots}', color=GOLD, size=FS_LABEL)
        hdr.next_to(out_tok, RIGHT, buff=0.5)
        hdr_ar = flow(out_tok, hdr, color=GOLD)
        self.play(FadeIn(hdr, shift=RIGHT * 0.2), ShowCreation(hdr_ar), run_time=0.7)
        pub = caption("a step's header is its public input")
        self.pad_to(A("public input") - 0.4)
        self.play(FadeIn(pub, shift=UP * 0.1), run_time=0.6)

        # "the soundness discipline is bridging" — children become their headers
        self.pad_to(A("soundness discipline") - 0.6)
        t4 = scene_title("bridging the seams")
        self.play(FadeOut(VGroup(toks, edges, out_tok, hdr, hdr_ar, pub)), swap(t3, t4),
                  run_time=0.8)
        B = bridge61()
        self.play(LaggedStart(AnimationGroup(absorb(chl, B.box_l), absorb(chr_, B.box_r)),
                              AnimationGroup(FadeIn(B.hdr_l, scale=1.5),
                                             FadeIn(B.hdr_r, scale=1.5)), lag_ratio=0.55),
                  FadeIn(B.hl_t), FadeIn(B.hr_t),
                  root.animate.move_to(B.root), run_time=1.0)
        self.remove(chl, chr_)
        self.play(ShowCreation(B.rd), run_time=0.5)

        # equality pins snap, one per spoken field
        pin_cm, pin_sn, pin_e = B.pins
        for pin, ph, lead in ((pin_cm, "same note commitment", 0.4),
                              (pin_sn, "matching sentinel", 0.4),
                              (pin_e, "the adjoining", 0.3)):
            self.pad_to(A(ph) - lead)
            self.play(ShowCreation(pin[0]), FadeIn(pin[1:], scale=1.4), run_time=0.7)

        # "sound exactly when the bridges don't leak"
        self.pad_to(A("bridges don't leak") - 0.5)
        self.play(*[Indicate(p, color=STAR, scale_factor=1.06) for p in B.pins],
                  run_time=0.9)

        # a field that disagrees: red flash, then restored
        self.pad_to(A("seam unchecked") - 0.6)
        f_r = B.f_r
        bad = mtex('"sntl"\'', size=FS_BODY, color=FLARE).move_to(f_r[1])
        xpin = x_mark(pin_sn[1].get_center(), r=0.2)
        self.play(Transform(f_r[1], bad),
                  pin_sn[0].animate.set_stroke(FLARE),
                  pin_sn[1].animate.set_stroke(FLARE),
                  pin_sn[2].animate.set_fill(FLARE, 0.0), run_time=0.5)
        self.play(ShowCreation(xpin), run_time=0.4)
        good = mtex('"sntl"_e', size=FS_BODY, color=CYAN).move_to(f_r[1])
        self.play(FadeOut(xpin), Transform(f_r[1], good),
                  pin_sn[0].animate.set_stroke(STAR),
                  pin_sn[1].animate.set_stroke(STAR),
                  pin_sn[2].animate.set_fill(STAR, 1.0), run_time=0.8)

        # "three colors sort the cast" — the bridge moves left, legend on the right
        self.pad_to(A("three colors") - 0.5)
        bridge_grp = VGroup(root, B.hdr_l, B.hdr_r, B.rd, B.pins, B.hl_t, B.hr_t)
        tgt = bridge_grp.copy()
        fit_in(tgt, BRIDGE_REGION)
        L = legend61()
        self.play(bridge_grp.animate.replace(tgt, stretch=False),
                  FadeOut(slabdock), swap(t4, L.title), run_time=1.0)
        self.pad_to(A("gold steps") - 0.6)
        self.play(ShowCreation(L.lg), FadeIn(L.rows[0], shift=RIGHT * 0.25), run_time=0.8)
        self.pad_to(AA(["science steps", "cyan steps"]) - 0.4)
        self.play(FadeIn(L.rows[1], shift=RIGHT * 0.25), run_time=0.7)
        self.pad_to(A("white is shared") - 0.3)
        self.play(FadeIn(L.rows[2], shift=RIGHT * 0.25), run_time=0.7)

        # anchor-chain segments + evidence trees as white's two forms
        self.pad_to(A("anchor chain segments") - 0.5)
        self.play(FadeIn(L.chainseg, lag_ratio=0.1), FadeIn(L.cs_t), run_time=0.8)
        self.pad_to(A("trees for closed") - 0.4)
        self.play(FadeIn(L.tr, lag_ratio=0.1), FadeIn(L.tr_t), run_time=0.8)

        # "built once per epoch, and every wallet in the pool reuses it"
        self.pad_to(A("every wallet") - 0.3)
        self.play(LaggedStart(*[FadeIn(w, shift=UP * 0.15) for w in L.wallets],
                              lag_ratio=0.2), run_time=0.7)
        self.pad_to(A("reuses it") - 0.4)
        src = VGroup(L.chainseg, L.tr)
        beads = VGroup(*[bead(STAR, 0.07).move_to(src.get_bottom() + UP * 0.1)
                         for _ in L.wallets])
        self.add(beads)
        self.play(LaggedStart(*[AnimationGroup(absorb(b, w), Indicate(w, color=GOLD))
                                for b, w in zip(beads, L.wallets)], lag_ratio=0.15),
                  run_time=0.9)
        self.remove(beads)

        # "one party's work, everyone's evidence"
        self.pad_to(A("partys work") - 0.4)
        self.play(Write(L.closing), run_time=1.2)
        self.pad_to(scene_T("6.1"))


# ---- 6.2 builders (also used to open 6.3) -----------------------------------
ROW62 = 1.75     # the step-flow row
DET62 = 0.25     # the details row under it
LIFT62 = -0.62   # where the stamp rides above the chain


def build62():
    """Every 6.2 object at its initial position (Scene62 animates them)."""
    P = SimpleNamespace()
    P.title = scene_title("same-epoch spend", color=GOLD)
    P.blocks = VGroup(*[block(0.72, 0.5) for _ in range(8)])
    P.blocks.arrange(RIGHT, buff=0.42)
    P.blocks.move_to(np.array([0, -2.15, 0])).align_to(np.array([-6.35, 0, 0]), LEFT)
    P.links = VGroup(*[chain_link(P.blocks[i], P.blocks[i + 1]) for i in range(7)])
    P.ticks = VGroup(*[Line(b.get_bottom() + DOWN * 0.1, b.get_bottom() + DOWN * 0.3,
                            stroke_width=SW, stroke_color=DIM) for b in P.blocks])
    P.gate = sentinel_gate(1.1).next_to(P.blocks[-1], RIGHT, buff=0.5)
    P.gate_t = mtex('"sntl"_(e+1)', size=FS_SMALL, color=STAR).next_to(P.gate, RIGHT, buff=0.15)
    P.ep_t = label("the current epoch", size=FS_SMALL, color=MUT)
    P.ep_t.next_to(VGroup(P.blocks[4], P.blocks[6]), DOWN, buff=0.45)
    P.cm_dot = Dot(radius=0.12).set_fill(GOLD, 1.0)
    P.cm_dot.move_to(P.blocks[1].get_top() + UP * 0.32)
    P.cm_t = mtex('"cm"', size=FS_LABEL, color=GOLD).next_to(P.cm_dot, UP, buff=0.1)
    # checklist panel: the audit, filled in as steps land
    P.cl_panel = panel(3.0, 3.9, color=MUT, fill_opacity=0.03).move_to(np.array([5.15, 0.75, 0]))
    P.cl_title = label("the contract, audited", size=FS_SMALL, color=TXT)
    P.cl_title.move_to(P.cl_panel.get_top() + DOWN * 0.35)
    P.rows = VGroup(*[check_row(t) for t in (
        "creation root", "note opens", "adjacent nullifiers", "bundle union", "anchor lift")])
    P.rows.arrange(DOWN, buff=0.36, aligned_edge=LEFT)
    P.rows.next_to(P.cl_title, DOWN, buff=0.35).align_to(P.cl_panel.get_left() + RIGHT * 0.25, LEFT)
    P.items = VGroup(*[r[1] for r in P.rows])
    P.cl_ticks = VGroup(*[checkmark(0.2, color=GOLD).move_to(r[0]).shift(UP * 0.03)
                          for r in P.rows])
    # the creation anchor marker: gold tick + "anchor"; it rides along with the lift
    P.anc_t = mtex('"anchor"', size=FS_SMALL, color=GOLD)
    P.anc_t.next_to(P.ticks[1], RIGHT, buff=0.12).shift(DOWN * 0.05)
    P.mline = P.ticks[1].copy().set_stroke(GOLD, SW_BOLD, 1.0)
    P.mk = VGroup(P.mline, P.anc_t)
    # the lift
    P.lift_t = step_pill("StampLift").move_to(np.array([-0.4, ROW62, 0]))
    P.ac = header_box('mono("AnchorChain"){"anchor"_L, "anchor"_R}', color=STAR, size=FS_SMALL)
    P.ac.move_to(np.array([-0.4, DET62 + 0.15, 0]))
    P.ac_ar = flow(P.ac, P.lift_t, color=STAR)
    P.merged = stamp_chip(color=GOLD, size=FS_SMALL).move_to(np.array([-0.4, DET62, 0]))
    P.finger = DashedLine(P.ticks[1].get_bottom() + DOWN * 0.05,
                          P.ticks[1].get_bottom() + DOWN * 0.45,
                          stroke_color=FLARE, stroke_width=SW)
    P.which = label("anchored here, it names the note", size=FS_SMALL, color=FLARE)
    P.which.next_to(P.finger, DOWN, buff=0.1).align_to(P.blocks[0], LEFT)
    P.blur = label("lifted: blurred into the epoch", size=FS_SMALL, color=GOLD)
    P.blur.move_to(P.which).align_to(P.which, LEFT)
    return P


def lift_x62(P, i):
    return P.blocks[i].get_x()


def final62(P):
    """Apply 6.2's end-of-scene state to a fresh build62()."""
    P.blocks[0].fade(0.5)
    P.merged.move_to(np.array([lift_x62(P, 5), LIFT62, 0]))
    P.mk.shift(RIGHT * (P.ticks[5].get_x() - P.ticks[1].get_x()))
    for it in P.items:
        it.set_color(TXT)
    P.visible = VGroup(P.title, P.blocks, P.links, P.ticks, P.gate, P.gate_t, P.cm_dot,
                       P.cm_t, P.cl_panel, P.cl_title, P.rows, P.cl_ticks, P.lift_t, P.ac,
                       P.ac_ar, P.merged, P.mk, P.blur)
    return P


class Scene62(TimedScene):
    """6.2 — Same-epoch spend: the minimal tree."""

    def construct(self):
        A = lambda p, o=1: anchor("6.2", p, o)
        AA = lambda ps, o=1: anchor_any("6.2", ps, o)

        # open on 6.1's final frame
        B = bridge61()
        fit_in(B.grp, BRIDGE_REGION)
        L = legend61()
        self.add(B.grp, L.lg, L.rows, L.chainseg, L.cs_t, L.tr, L.tr_t, L.wallets, L.closing,
                 L.title)

        # the white anchor-chain segment grows into the current epoch's chain
        P = build62()
        self.pad_to(0.3)
        self.play(LaggedStart(FadeOut(VGroup(B.grp, L.lg, L.rows, L.cs_t, L.tr, L.tr_t,
                                             L.wallets, L.closing)),
                              ReplacementTransform(L.chainseg, VGroup(P.blocks, P.links)),
                              lag_ratio=0.4), run_time=1.5)
        self.play(swap(L.title, P.title), FadeIn(P.ticks, lag_ratio=0.05), FadeIn(P.ep_t),
                  FadeIn(P.gate, shift=LEFT * 0.1), FadeIn(P.gate_t), run_time=1.0)
        blocks, ticks = P.blocks, P.ticks
        add_shimmer(blocks, amp=0.10, speed=1.2)

        # the note is created inside it: no history to its left
        cm_dot, cm_t = P.cm_dot, P.cm_t
        self.pad_to(AA(["created in the current", "the note was created"]) - 0.4)
        self.play(FadeIn(cm_dot, scale=1.6), FadeIn(cm_t), run_time=0.7)
        self.pad_to(A("no history") - 0.4)
        noh = label("nothing to exclude", size=FS_SMALL, color=MUT)
        noh.next_to(blocks[0], DOWN, buff=0.45).align_to(blocks[0], LEFT)
        self.play(FadeIn(noh, shift=RIGHT * 0.2), blocks[0].animate.fade(0.5), run_time=0.7)

        # checklist panel: the audit, filled in as steps land
        self.play(ShowCreation(P.cl_panel), FadeIn(P.cl_title),
                  FadeIn(P.rows, lag_ratio=0.1), run_time=1.0)
        items, cl_ticks = P.items, P.cl_ticks

        # "no service needed"
        svc = key_chip("service", color=CYAN, size=FS_LABEL).move_to(np.array([-2.2, 0.55, 0]))
        svc_x = strike(svc)
        self.pad_to(A("no service") - 0.3)
        self.play(FadeIn(svc, scale=1.1), run_time=0.4)
        self.pad_to(A("needed") - 0.2)
        self.play(ShowCreation(svc_x), run_time=0.4)

        # SpendableInit — gold
        init = step_pill("SpendableInit").move_to(np.array([-5.15, ROW62, 0]))
        self.pad_to(AA(["spendable in it", "spendable init"]) - 0.4)
        self.play(FadeIn(init, scale=1.1), FadeOut(VGroup(svc, svc_x)), run_time=0.7)
        self.pad_to(A("creation block") - 0.3)
        self.play(Indicate(blocks[1], color=GOLD, scale_factor=1.25), run_time=0.7)

        # cm is a root of the creating stamp's accumulator; compute its anchor
        self.pad_to(A("a root of") - 0.6)
        acc = tex_chip('a_T ("cm") = 0', color=GOLD, size=FS_LABEL)
        acc.move_to(np.array([-5.15, DET62, 0]))
        ghost = cm_dot.copy()
        acc_ar = flow(init, acc, color=GOLD)
        self.play(ghost.animate.move_to(acc.get_center()).set_opacity(0.0),
                  FadeIn(acc), ShowCreation(acc_ar), run_time=0.9)
        self.remove(ghost)
        self.pad_to(AA(["stamps anchor", "stamp's anchor"]) - 0.4)
        self.play(ticks[1].animate.set_stroke(GOLD, SW_BOLD, 1.0), FadeIn(P.anc_t),
                  run_time=0.7)

        # out comes the first header: NoteSpendable
        ns = header_box('mono("NoteSpendable"){"cm", e, "anchor"}', color=GOLD,
                        size=FS_LABEL)
        ns.move_to(np.array([-1.35, ROW62, 0]))
        ar1 = flow(init, ns)
        self.pad_to(A("the first header") - 0.4)
        self.play(ShowCreation(ar1), FadeIn(ns, shift=RIGHT * 0.2), run_time=0.8)
        self.play(FadeOut(acc), FadeOut(acc_ar), run_time=0.4)
        # "this commitment, this epoch, this anchor": the field and its source flash
        nst = ns[1]
        for ph, field, src in (("this commitment", nst[14:16], VGroup(cm_dot, cm_t)),
                               ("this epoch", nst[17:18], P.ep_t),
                               ("this anchor", nst[19:25], P.anc_t)):
            self.pad_to(A(ph) - 0.25)
            self.play(Indicate(field, color=STAR, scale_factor=1.3),
                      Indicate(src, color=STAR), run_time=0.6)
        self.play(ShowCreation(cl_ticks[0]), items[0].animate.set_color(TXT), run_time=0.5)

        # "cache it" + hardware wallet
        self.pad_to(A("cash it") - 0.3)
        cached = ns.copy()
        self.play(cached.animate.scale(0.82).move_to(np.array([-4.55, DET62, 0])),
                  run_time=0.8)
        hw = key_chip("hardware wallet: sign now", color=GOLD, size=FS_SMALL)
        hw.next_to(cached, DOWN, buff=0.3)
        self.pad_to(A("hardware wallet") - 0.4)
        self.play(FadeIn(hw, shift=UP * 0.15), run_time=0.6)

        # SpendBind — open the note, four checks on their words, two nullifiers
        sb = step_pill("SpendBind").move_to(np.array([2.35, ROW62, 0]))
        ar2 = flow(ns, sb)
        self.pad_to(A("spend bind") - 0.3)
        self.play(ShowCreation(ar2), FadeIn(sb, scale=1.1), run_time=0.7)
        checks = VGroup(
            mtex('"pk"', size=FS_LABEL, color=TXT),
            mtex('"cm"', size=FS_LABEL, color=TXT),
            mtex('v in [0, 2^64)', size=FS_LABEL, color=TXT),
            mtex('"rk"', size=FS_LABEL, color=TXT),
        )
        checks.arrange_in_grid(2, 2, h_buff=0.75, v_buff=0.35)
        cmarks = VGroup(*[checkmark(0.17).next_to(c, RIGHT, buff=0.12) for c in checks])
        note_card = panel(VGroup(checks, cmarks).get_width() + 0.7,
                          VGroup(checks, cmarks).get_height() + 0.55,
                          color=GOLD, fill_opacity=0.06)
        VGroup(note_card, checks, cmarks).move_to(np.array([1.55, DET62, 0]))
        self.pad_to(A("open the note") - 0.4)
        self.play(FadeIn(note_card, scale=1.05), FadeIn(checks, lag_ratio=0.1), run_time=0.8)
        for i, ph in enumerate(("payment key", "the commitment", "value range",
                                "spending authority")):
            self.pad_to(A(ph) - 0.25)
            self.play(ShowCreation(cmarks[i]), Indicate(checks[i], color=GOLD), run_time=0.45)
        self.pad_to(A("adjacent nullifiers") - 0.6)
        nfs = VGroup(bead(FLARE, 0.12), bead(FLARE, 0.12)).arrange(RIGHT, buff=0.35)
        nf_t = mtex('"nf"_e, thin "nf"_(e+1)', size=FS_LABEL, color=FLARE)
        nfg = VGroup(nfs, nf_t).arrange(RIGHT, buff=0.3)
        nfg.next_to(note_card, DOWN, buff=0.3)
        self.play(FadeIn(nfs, scale=1.5), FadeIn(nf_t), run_time=0.8)
        self.play(ShowCreation(cl_ticks[1]), ShowCreation(cl_ticks[2]),
                  items[1].animate.set_color(TXT),
                  items[2].animate.set_color(TXT), run_time=0.5)

        # the result: a one-action Stamp (the cached header has done its job)
        st = stamp_chip(color=GOLD, size=FS_SMALL).move_to(np.array([1.55, DET62, 0]))
        self.pad_to(A("one action stamp") - 0.5)
        self.play(absorb(VGroup(note_card, checks, cmarks, nfg), st), FadeIn(st, scale=1.5),
                  FadeOut(VGroup(cached, hw)), run_time=0.8)

        # StampMerge: the output branch's stamp joins
        self.pad_to(A("stamp merge") - 0.3)
        ost = stamp_chip(color=GOLD, size=FS_SMALL).move_to(np.array([-2.35, DET62, 0]))
        ost_t = itex("from the output branch", size=FS_SMALL, color=MUT)
        ost_t.next_to(ost, DOWN, buff=0.15)
        self.play(FadeIn(ost, shift=DOWN * 0.15), FadeIn(ost_t), run_time=0.7)
        self.pad_to(A("both accumulators") - 0.5)
        mg = step_pill("StampMerge").move_to(np.array([-0.4, ROW62, 0]))
        merged = P.merged
        self.play(FadeIn(mg), FadeOut(VGroup(init, ar1, ns, ar2, sb)), run_time=0.6)
        merged2 = merged.copy()
        mg_ar = flow(merged, mg)
        self.play(ReplacementTransform(st, merged), ReplacementTransform(ost, merged2),
                  FadeOut(ost_t), run_time=1.0)
        self.remove(merged2)
        self.play(ShowCreation(mg_ar), run_time=0.4)
        self.pad_to(A("under one proof") - 0.4)
        self.play(ShowCreation(cl_ticks[3]), items[3].animate.set_color(TXT), run_time=0.6)

        # StampLift: the stamp drops onto its anchor and rides the chain forward;
        # the gold anchor marker rides with it
        self.pad_to(AA(["stamp lifts", "stamp lift"]) - 0.3)
        mk = P.mk
        self.remove(P.anc_t)
        self.add(mk)
        ticks[1].set_stroke(DIM, SW, 1.0)
        self.play(swap(mg, P.lift_t, lag=0.6), FadeOut(mg_ar),
                  merged.animate.move_to(np.array([lift_x62(P, 1) + 0.9, LIFT62, 0])),
                  run_time=0.9)
        self.pad_to(A("anchor chain evidence") - 0.9)
        self.play(FadeIn(P.ac, shift=UP * 0.15), ShowCreation(P.ac_ar), run_time=0.7)
        dx14 = ticks[4].get_x() - ticks[1].get_x()
        self.play(merged.animate.move_to(np.array([lift_x62(P, 4), LIFT62, 0])),
                  mk.animate.shift(RIGHT * dx14), run_time=1.4)
        self.play(ShowCreation(cl_ticks[4]), items[4].animate.set_color(TXT), run_time=0.5)

        # a chain segment never contains a sentinel: the gate repels
        self.pad_to(A("never contains") - 0.4)
        self.play(Indicate(P.gate, color=STAR, scale_factor=1.2), run_time=0.7)
        self.pad_to(A("cannot cross") - 0.3)
        edge_x = P.gate.get_x() - 0.15 - merged.get_width() / 2
        dxb = edge_x - merged.get_x()
        self.play(merged.animate(rate_func=there_and_back).shift(RIGHT * dxb),
                  mk.animate(rate_func=there_and_back).shift(RIGHT * dxb), run_time=1.2)
        self.pad_to(A("exclusion obligation") - 0.5)
        skip_t = label("beyond: an unproven epoch", size=FS_SMALL, color=FLARE)
        skip_t.next_to(P.gate, DOWN, buff=0.35).align_to(P.gate, LEFT).shift(LEFT * 0.3)
        self.play(FadeIn(skip_t, shift=DOWN * 0.1), FadeOut(P.ep_t), run_time=0.7)

        # lifting isn't cosmetic: the creation anchor points at the note
        self.pad_to(A("anchored exactly") - 0.5)
        self.play(FadeOut(noh), FadeOut(skip_t), run_time=0.4)
        self.play(ShowCreation(P.finger), FadeIn(P.which),
                  Indicate(VGroup(cm_dot, cm_t), color=FLARE), run_time=0.9)
        self.pad_to(AA(["blurs that", "blurs"]) - 0.5)
        dx45 = ticks[5].get_x() - ticks[4].get_x()
        self.play(FadeOut(P.finger), swap(P.which, P.blur, lag=0.6),
                  merged.animate.move_to(np.array([lift_x62(P, 5), LIFT62, 0])),
                  mk.animate.shift(RIGHT * dx45), run_time=1.0)

        # the audit is complete
        self.pad_to(A("checklist") - 0.3)
        self.play(Indicate(VGroup(P.cl_panel, P.cl_title, P.rows, cl_ticks),
                           color=GOLD, scale_factor=1.04), run_time=0.9)
        clear_shimmer(blocks)
        self.pad_to(scene_T("6.2"))


# ---- 6.3 tally builder (also used to open 6.4) ------------------------------

def tally63():
    """'What did the service learn?': saw / never-saw panels in final layout."""
    T = SimpleNamespace()
    T.title = scene_title("what did the service learn?", color=STAR)
    T.oss_p = panel(6.0, 5.3, color=CYAN, fill_opacity=0.04).move_to(np.array([3.4, -0.3, 0]))
    T.oss_t = label("what it saw", size=FS_BODY, color=CYAN)
    T.oss_t.move_to(T.oss_p.get_top() + DOWN * 0.45)
    T.pairs = VGroup(*[tex_chip(f'({i}, thin "nf"_{i})', color=TXT, size=FS_LABEL)
                       for i in (2, 3, 4)]).arrange(DOWN, buff=0.25)
    T.rng = tex_chip('[s_L, s_R)', color=CYAN, size=FS_LABEL)
    T.seen = VGroup(T.pairs, T.rng).arrange(DOWN, buff=0.4)
    T.seen.next_to(T.oss_t, DOWN, buff=0.45).set_x(T.oss_p.get_x() - 1.4)
    T.decoys = T.pairs.copy().fade(0.45)
    T.decoys.match_y(T.pairs).set_x(T.oss_p.get_x() + 1.4)
    T.dec_t = itex("decoys look the same", size=FS_SMALL, color=MUT)
    T.dec_t.next_to(T.decoys, DOWN, buff=0.3)
    T.nev_p = panel(6.0, 5.3, color=FLARE, fill_opacity=0.03).move_to(np.array([-3.4, -0.3, 0]))
    T.nev_t = label("what it never saw", size=FS_BODY, color=FLARE).match_y(T.oss_t)
    T.nev_t.set_x(T.nev_p.get_x())
    T.nos = VGroup(
        tex_chip('"cm"', color=TXT, size=FS_BODY),
        key_chip("the note", color=TXT, size=FS_BODY),
        key_chip("another service's work", color=TXT, size=FS_BODY),
        key_chip("the spend anchor", color=TXT, size=FS_BODY),
    ).arrange(DOWN, buff=0.36)
    T.nos.next_to(T.nev_t, DOWN, buff=0.5).set_x(T.nev_p.get_x())
    T.strikes = VGroup(*[strike(n) for n in T.nos])
    T.gold_t = caption("everything that ties it to your note ran in gold", color=GOLD)
    T.all = VGroup(T.title, T.oss_p, T.oss_t, T.seen, T.decoys, T.dec_t, T.nev_p, T.nev_t,
                   T.nos, T.strikes, T.gold_t)
    return T


class Scene63(TimedScene):
    """6.3 — Past-epoch spend: binding delegated work to the note."""

    def construct(self):
        A = lambda p, o=1: anchor("6.3", p, o)
        AA = lambda ps, o=1: anchor_any("6.3", ps, o)

        # open on 6.2's final frame
        P = final62(build62())
        self.add(P.visible)

        # the note is several epochs old: the one-epoch chain shrinks into a single
        # slot of an epoch axis (presented mid-stage, docked low when the tree comes)
        axis, eticks, slots = epoch_axis63()
        cm_dot = Dot(radius=0.12).set_fill(GOLD, 1.0).move_to(slots[1])
        cm_t = mtex('"cm"', size=FS_LABEL, color=GOLD).next_to(cm_dot, LEFT, buff=0.12)
        axis_grp = VGroup(axis, eticks, cm_dot, cm_t)
        LIFT_AX = UP * 2.3
        axis_grp.shift(LIFT_AX)
        chain = VGroup(P.blocks, P.links, P.ticks, P.gate)
        self.pad_to(0.3)
        self.play(FadeOut(VGroup(P.title, P.gate_t, P.cl_panel, P.cl_title, P.rows, P.cl_ticks,
                                 P.lift_t, P.ac, P.ac_ar, P.merged, P.mk, P.blur)),
                  run_time=0.6)
        self.play(chain.animate.set_width(AX_DX * 0.8).move_to(axis.get_center() * UP
                                                             + RIGHT * slot_x(1)).set_opacity(0),
                  ReplacementTransform(P.cm_dot, cm_dot), ReplacementTransform(P.cm_t, cm_t),
                  ShowCreation(axis), FadeIn(eticks, lag_ratio=0.06), run_time=1.1)
        self.remove(chain)
        in_t = label("inclusion", size=FS_LABEL, color=GOLD).next_to(cm_dot, UP, buff=0.35)
        self.pad_to(A("inclusion") - 0.3)
        self.play(FadeIn(in_t, shift=DOWN * 0.1), Indicate(eticks[1], color=GOLD), run_time=0.7)
        self.pad_to(A("exclusion") - 0.4)
        ex_br = bracket(VGroup(*[eticks[i] for i in range(2, 8)]), color=FLARE, buff=0.5)
        ex_t = label("exclusion: every epoch since", size=FS_LABEL, color=FLARE)
        ex_t.next_to(ex_br, UP, buff=0.12)
        self.play(GrowFromCenter(ex_br), FadeIn(ex_t), run_time=0.8)

        # two branches, built independently, bridged at the end
        self.pad_to(A("two branches") - 0.4)
        b1_l = label("branch one", size=FS_BODY, color=GOLD).move_to(in_t)
        b2_l = label("branch two", size=FS_BODY, color=STAR).move_to(ex_t)
        self.play(swap(in_t, b1_l, lag=0.6), swap(ex_t, b2_l, lag=0.6),
                  ex_br.animate.set_color(STAR), run_time=0.8)
        self.pad_to(A("bridged") - 0.4)
        arc = ArcBetweenPoints(b1_l.get_top() + UP * 0.15, b2_l.get_top() + UP * 0.15,
                               angle=-TAU / 7)
        arc.set_stroke(STAR, SW_THIN, 0.9)
        med = VGroup(Circle(radius=0.2).set_fill(VOID, 1.0).set_stroke(STAR, 1.8, 0.95),
                     mtex("=", size=FS_SMALL, color=STAR))
        med.move_to(arc.point_from_proportion(0.5))
        self.play(ShowCreation(arc), FadeIn(med, scale=1.4), run_time=0.8)

        # ---- branch one: all gold -------------------------------------------
        b1_t = scene_title("branch one: the creation epoch", color=GOLD, size=42)
        self.pad_to(A("branch one") - 0.4)
        self.play(swap(b1_l, b1_t, lag=0.7), FadeOut(VGroup(b2_l, ex_br, arc, med)),
                  run_time=0.9)
        self.pad_to(A("all gold") - 0.3)
        self.play(Indicate(VGroup(cm_dot, cm_t), color=GOLD), run_time=0.6)

        R1, R2 = 1.6, -0.6
        self.pad_to(A("evidence tree") - 0.9)
        self.play(axis_grp.animate.shift(-LIFT_AX), run_time=0.8)
        tree = mini_tree(1.7).move_to(np.array([slot_x(1), -0.55, 0]))
        tree_t = label("evidence tree", size=FS_SMALL, color=STAR)
        tree_t.next_to(tree, UP, buff=0.15)
        tline = DashedLine(tree.get_bottom() + DOWN * 0.08, cm_dot.get_top() + UP * 0.06,
                           stroke_color=STAR, stroke_width=SW_THIN, stroke_opacity=0.7)
        self.play(FadeIn(tree, lag_ratio=0.08), FadeIn(tree_t), ShowCreation(tline),
                  run_time=0.8)
        add_shimmer(tree[4], amp=0.12, speed=1.25)

        # "open two leaves: one for the commitment, one for the nullifier"
        op_nf = VGroup(key_chip("opening", color=STAR, size=FS_SMALL),
                       mtex('"nf"_(e_"incl")', size=FS_LABEL, color=STAR)).arrange(RIGHT, buff=0.15)
        op_cm = VGroup(key_chip("opening", color=STAR, size=FS_SMALL),
                       mtex('"cm"', size=FS_LABEL, color=STAR)).arrange(RIGHT, buff=0.15)
        op_nf.move_to(np.array([-1.55, R1, 0]))
        op_cm.move_to(np.array([-1.55, R2, 0]))
        e_nf = flow(tree, op_nf, color=STAR)
        e_cm = flow(tree, op_cm, color=STAR)
        self.pad_to(A("open two leaves") - 0.4)
        self.play(Indicate(VGroup(tree[4][1], tree[4][2]), color=STAR, scale_factor=1.5),
                  run_time=0.6)
        self.pad_to(A("for the commitment") - 0.3)
        self.play(FadeIn(op_cm, scale=1.5), Indicate(tree[4][2], color=STAR), ShowCreation(e_cm), run_time=0.7)
        self.pad_to(A("nullifier at") - 0.4)
        self.play(FadeIn(op_nf, scale=1.5), Indicate(tree[4][1], color=STAR), ShowCreation(e_nf), run_time=0.7)

        # NoteUnspentInit: its work lands in the notes column, row by row
        nui = step_pill("NoteUnspentInit").move_to(np.array([1.45, R1, 0]))
        a1 = flow(op_nf, nui)
        self.pad_to(AA(["note unspent in it", "note unspent init"]) - 0.4)
        self.play(FadeIn(nui, scale=1.1), ShowCreation(a1), run_time=0.8)
        NX = 3.35

        def note_row(mob, y):
            return mob.move_to(np.array([0, y, 0])).align_to(np.array([NX, 0, 0]), LEFT)
        nbar = Line(np.array([NX - 0.22, 2.5, 0]), np.array([NX - 0.22, -0.05, 0]),
                    stroke_width=SW, stroke_color=GOLD, stroke_opacity=0.6)
        nbar_ar = tarrow(nui.get_right() + RIGHT * 0.1, np.array([NX - 0.3, R1, 0]),
                         color=GOLD, width=SW_THIN)
        self.pad_to(A("ownership keys") - 0.5)
        wit = note_row(tex_chip('"note", ("ak", "nk")', color=GOLD, size=FS_LABEL), 2.15)
        self.play(ShowCreation(nbar), ShowCreation(nbar_ar), FadeIn(wit, shift=RIGHT * 0.1),
                  run_time=0.7)
        self.pad_to(AA(["rederives", "re derives"]) - 0.3)
        nf_row = note_row(VGroup(bead(FLARE, 0.12), mtex('"nf"_(e_"incl")', size=FS_LABEL,
                                                         color=FLARE),
                                 label("re-derived", size=FS_SMALL, color=TXT))
                          .arrange(RIGHT, buff=0.2), 1.45)
        self.play(FadeIn(nf_row, shift=RIGHT * 0.1), run_time=0.6)
        self.pad_to(A("its address") - 0.3)
        addr = VGroup(Square(0.22).set_fill(CYAN, 0.9), Square(0.22).set_fill(AMBER, 0.9),
                      Square(0.22).set_fill(CYAN, 0.9)).arrange(RIGHT, buff=0.06)
        for sq in addr:
            sq.set_stroke(width=0)
        addr_row = note_row(VGroup(addr, label("its address", size=FS_SMALL, color=TXT))
                            .arrange(RIGHT, buff=0.25), 0.82)
        self.play(FadeIn(addr_row, lag_ratio=0.2), run_time=0.6)
        self.pad_to(A("selects") - 0.3)
        self.play(Indicate(addr, color=STAR), Indicate(op_nf, color=STAR),
                  Indicate(tree[4][1], color=STAR, scale_factor=1.6), run_time=0.8)
        self.pad_to(A("opens the bucket") - 0.4)
        qb = tex_chip('q_b ("nf") != 0', color=GOLD, size=FS_LABEL)
        qb_row = note_row(qb, 0.15)
        self.play(FadeIn(qb, scale=1.1), run_time=0.7)
        self.pad_to(A("absent") - 0.3)
        absent = VGroup(label("absent", size=FS_LABEL, color=GOLD), checkmark(0.2))
        absent.arrange(RIGHT, buff=0.12).next_to(qb, RIGHT, buff=0.25)
        self.play(FadeIn(absent[0]), ShowCreation(absent[1]), run_time=0.5)

        # SpendableReinit bridges in the cm leaf
        sri = step_pill("SpendableReinit").move_to(np.array([1.45, R2, 0]))
        self.pad_to(AA(["spendable re net", "spendable reinit",
                        "spendable re in it"]) - 0.4)
        a2 = flow(op_cm, sri)
        a3 = flow(nui, sri)
        self.play(FadeIn(sri, scale=1.1), ShowCreation(a2), ShowCreation(a3), run_time=0.9)
        self.pad_to(A("zero this time") - 0.4)
        qcm = tex_chip('q_(b\') ("cm") = 0', color=GOLD, size=FS_LABEL)
        present = VGroup(label("present", size=FS_LABEL, color=GOLD), checkmark(0.2))
        present.arrange(RIGHT, buff=0.12)
        q2_row = note_row(VGroup(qcm, present).arrange(RIGHT, buff=0.25), R2 - 0.05)
        self.play(FadeIn(q2_row, scale=1.05), run_time=0.8)

        # a clean NoteSpendable
        ns = header_box('mono("NoteSpendable"){"cm", e_"incl"+1, "sntl"}', color=GOLD,
                        size=FS_LABEL)
        ns.move_to(np.array([1.45, -1.72, 0]))
        self.pad_to(A("clean note spendable") - 0.4)
        a4 = flow(sri, ns)
        self.play(ShowCreation(a4), FadeIn(ns, shift=DOWN * 0.2), run_time=0.9)

        # "the same evidence tree answered both"
        self.pad_to(A("notice the shape") - 0.4)
        self.play(Indicate(VGroup(tree, tree_t), color=STAR, scale_factor=1.08), run_time=0.9)
        self.pad_to(A("both membership") - 0.4)
        self.play(Indicate(qcm, color=GOLD, scale_factor=1.1),
                  Indicate(qb, color=GOLD, scale_factor=1.1), run_time=0.8)
        self.pad_to(A("consulted anyone") - 0.6)
        b1_cap = caption("one tree answered both, and nobody was asked", color=GOLD)
        self.play(FadeIn(b1_cap, shift=UP * 0.1), run_time=0.8)

        # ---- branch two: wallet lane over service lane -----------------------
        # branch one's result waits in the right column, where the branches will join
        self.pad_to(A("branch two") - 0.4)
        b1 = VGroup(tree, tree_t, tline, op_nf, op_cm, e_nf, e_cm, nui, a1, nbar, nbar_ar,
                    wit, nf_row, addr_row, qb_row, absent, sri, a2, a3, q2_row, a4, b1_cap)
        clear_shimmer(tree[4])
        JX = 5.45                     # the join column
        ns2 = header_box('mono("NoteSpendable") \\ {"cm", e_"incl"+1, "sntl"}', color=GOLD,
                         size=FS_SMALL).move_to(np.array([JX, 1.7, 0]))
        br1_t = itex("from branch one", size=FS_SMALL, color=GOLD).next_to(ns2, UP, buff=0.15)
        b2_t = scene_title("branch two: the delegated epochs", color=STAR, size=42)
        w_lane = lane(0.5, 2.75, GOLD, "wallet")
        s_lane = lane(-1.45, 0.35, CYAN, "service")
        ns_morph = (ReplacementTransform(ns, ns2)
                    if len(ns[1].submobjects) == len(ns2[1].submobjects)
                    else FadeTransform(ns, ns2))
        self.play(FadeOut(b1), ns_morph, swap(b1_t, b2_t), run_time=1.1)
        self.play(FadeIn(w_lane), FadeIn(s_lane), FadeIn(br1_t), run_time=0.6)

        WR, WT = 1.85, 0.95      # wallet lane: pill row, tile row
        SR = -0.6                # service lane row
        WX = -0.3                # center of the fused window row (Com(g_R) stays in-lane)

        def tile(i, color):
            t = factor_tile("", color=color, w=0.62, h=0.62).add(
                label(f"F{i}", size=FS_SMALL, color=color))
            t[1].move_to(t[0])
            return t

        def tiles(rng, color):
            return VGroup(*[tile(i, color) for i in rng]).arrange(RIGHT, buff=0.08)

        # "the ranged commitment, the cubic factors, finally click together"
        wrow = tiles(range(2, 10), GOLD).move_to(np.array([WX, WT, 0]))
        ghost = tiles(range(2, 10), DIM)
        scat = [(-4.6, 2.1), (-2.9, 1.0), (-1.2, 2.2), (0.6, 1.1), (2.3, 2.05), (3.6, 0.95),
                (-3.7, 1.55), (1.4, 1.6)]
        for g, (x, y) in zip(ghost, scat):
            g.move_to(np.array([x, y, 0])).rotate(0.25 * ((x * 7) % 3 - 1))
        self.pad_to(A("range commitment") - 0.3)
        self.play(LaggedStart(*[FadeIn(g, scale=1.5) for g in ghost], lag_ratio=0.1),
                  run_time=1.0)
        self.pad_to(A("clicks together") - 0.4)
        self.play(LaggedStart(*[Transform(g, w.copy().set_color(DIM).set_stroke(DIM, 1.8, 0.8))
                                for g, w in zip(ghost, wrow)], lag_ratio=0.06),
                  run_time=0.9)
        self.pad_to(AA(["the wallet gold", "wallet gold"]) - 0.4)
        self.play(FadeOut(ghost), Indicate(w_lane[1], color=GOLD, scale_factor=1.3),
                  run_time=0.6)

        # NoteSeed -> NoteMaster
        nseed = step_pill("NoteSeed").move_to(np.array([-4.9, WR, 0]))
        self.pad_to(A("note seed") - 0.3)
        self.play(FadeIn(nseed, scale=1.1), run_time=0.6)
        nm = header_box('mono("NoteMaster"){"cm", "mk"}', color=GOLD, size=FS_LABEL)
        nm.move_to(np.array([-4.9, WT, 0]))
        self.pad_to(A("reusable header") - 0.4)
        a5 = flow(nseed, nm)
        self.play(ShowCreation(a5), FadeIn(nm, shift=DOWN * 0.15), run_time=0.8)

        # NullifierDerive x2 -> windows of factor tiles
        self.pad_to(AA(["nullifier derives squeezes",
                        "nullifier derive squeezes"]) - 0.4)
        nd1 = step_pill("NullifierDerive").move_to(np.array([WX - 1.6, WR, 0]))
        nd2 = step_pill("NullifierDerive").move_to(np.array([WX + 1.6, WR, 0]))
        self.play(FadeIn(nd1), FadeIn(nd2), run_time=0.7)
        tilesA = tiles(range(2, 6), GOLD).move_to(np.array([WX - 1.6, WT, 0]))
        tilesB = tiles(range(6, 10), GOLD).move_to(np.array([WX + 1.6, WT, 0]))
        self.pad_to(A("windows of nullifiers") - 0.5)
        self.play(LaggedStart(*[FadeIn(m, shift=DOWN * 0.15) for m in (*tilesA, *tilesB)],
                              lag_ratio=0.08), run_time=1.2)
        self.pad_to(A("those cubic factors") - 0.4)
        self.play(Indicate(VGroup(tilesA, tilesB), color=GOLD, scale_factor=1.05),
                  run_time=0.8)

        # NullifierFuse -> one range
        self.pad_to(A("nullifier fuse") - 0.3)
        fuse = step_pill("NullifierFuse").move_to(np.array([WX, WR, 0]))
        self.play(FadeIn(fuse), FadeOut(nd1), FadeOut(nd2), run_time=0.6)
        g_r = mtex('"Com"(g_R)', size=FS_LABEL, color=GOLD)
        g_r.next_to(wrow, RIGHT, buff=0.25)
        self.pad_to(A("one range") - 0.5)
        self.play(ReplacementTransform(VGroup(*tilesA), VGroup(*wrow[:4])),
                  ReplacementTransform(VGroup(*tilesB), VGroup(*wrow[4:])),
                  FadeIn(g_r), FadeOut(fuse), run_time=1.1)

        # ---- the service side, cyan ------------------------------------------
        self.pad_to(AA(["the service cyan", "service cyan"]) - 0.3)
        self.play(Indicate(s_lane[1], color=CYAN, scale_factor=1.3), run_time=0.6)
        useed = step_pill("UnspentSeed", color=CYAN).move_to(np.array([-4.9, SR, 0]))
        self.pad_to(A("unspent seed") - 0.3)
        self.play(FadeIn(useed, scale=1.1), run_time=0.6)
        emptyr = tex_chip('[s_L, s_L), thin "Com"(1)', color=CYAN, size=FS_SMALL)
        emptyr.move_to(np.array([-1.95, SR, 0]))
        self.pad_to(A("empty range") - 0.3)
        a6 = flow(useed, emptyr, color=CYAN)
        self.play(ShowCreation(a6), FadeIn(emptyr, shift=RIGHT * 0.15), run_time=0.7)

        # evidence trees over the closed epochs; a sentinel pawl on the axis
        ulift = step_pill("UnspentLift", color=CYAN).move_to(np.array([1.0, SR, 0]))
        a7 = flow(emptyr, ulift, color=CYAN)
        trees = VGroup(*[mini_tree(0.62).move_to(np.array([slot_x(i), -1.95, 0]))
                         for i in (2, 3, 4)])
        tree_leaves = VGroup(*[leaf for tree_i in trees for leaf in tree_i[4]])
        pawl = Triangle().scale(0.15).rotate(PI).set_fill(CYAN, 1.0).set_stroke(width=0)
        pawl.move_to(sentinel_pos(2) + UP * 0.3)
        self.pad_to(A("unspent lift") - 0.4)
        self.play(FadeIn(ulift, scale=1.1), ShowCreation(a7),
                  FadeIn(trees, lag_ratio=0.15), FadeIn(pawl), run_time=0.9)
        add_shimmer(tree_leaves, amp=0.14, speed=1.3)

        srow = VGroup()
        # lift #1: opening -> non-membership -> append factor -> advance sentinel
        self.pad_to(A("tree opening") - 0.7)
        oc1 = key_chip("opening", color=STAR, size=FS_MIN).move_to(trees[0])
        self.play(oc1.animate.next_to(ulift, DOWN, buff=0.12), run_time=0.8)
        self.pad_to(A("non membership", 2) - 0.4)
        q1 = tex_chip('q_b ("nf"_2) != 0', color=CYAN, size=FS_SMALL)
        q1.move_to(np.array([3.15, SR, 0]))
        self.play(absorb(oc1, ulift), FadeIn(q1, scale=1.1), run_time=0.7)
        self.remove(oc1)
        self.pad_to(A("index factor") - 0.5)
        st1 = tile(2, CYAN).move_to(np.array([2.75, SR, 0]))
        srow.add(st1)
        self.play(absorb(q1, st1), FadeIn(st1, scale=1.5), run_time=0.7)
        self.remove(q1)
        self.pad_to(A("one sentinel forward") - 0.5)
        self.play(pawl.animate.move_to(sentinel_pos(3) + UP * 0.3), run_time=0.8)

        # lift #2, fast
        oc2 = key_chip("opening", color=STAR, size=FS_MIN).move_to(trees[1])
        st2 = tile(3, CYAN).next_to(st1, RIGHT, buff=0.08)
        srow.add(st2)
        self.play(absorb(oc2, ulift), run_time=0.6)
        self.remove(oc2)
        self.play(FadeIn(st2, shift=DOWN * 0.1),
                  pawl.animate.move_to(sentinel_pos(4) + UP * 0.3), run_time=0.8)

        # cannot skip an epoch, repeat one, or shuffle the order
        def bad_attempt(start, toward):
            oc = key_chip("opening", color=STAR, size=FS_MIN)
            oc.move_to(start)
            self.play(FadeIn(oc), run_time=0.3)
            self.play(oc.animate(rate_func=there_and_back).move_to(toward), run_time=0.6)
            x_ = strike(oc)
            self.play(ShowCreation(x_), run_time=0.3)
            return VGroup(oc, x_)
        self.pad_to(A("skip an epoch") - 0.5)
        skip = bad_attempt(np.array([slot_x(5), -1.95, 0]), np.array([slot_x(5) - 0.6, -1.15, 0]))
        self.pad_to(A("repeat one") - 0.4)
        self.play(FadeOut(skip), run_time=0.3)
        rep = bad_attempt(np.array([sentinel_pos(3)[0], -2.0, 0]), np.array([slot_x(3) - 0.3, -1.1, 0]))
        self.pad_to(A("ratchet") - 0.4)
        oneway = tarrow(np.array([sentinel_pos(2)[0], AX_Y - 0.78, 0]),
                        np.array([sentinel_pos(5)[0], AX_Y - 0.78, 0]), color=CYAN, width=SW)
        ow_t = label("one way", size=FS_SMALL, color=CYAN)
        ow_t.next_to(oneway, RIGHT, buff=0.18)
        self.play(FadeOut(rep), ShowCreation(oneway), FadeIn(ow_t), run_time=0.8)

        # ---- UnspentBind: the quotient check, at the join ---------------------
        self.pad_to(A("unspent bind") - 0.4)
        clear_shimmer(tree_leaves)
        ub = step_pill("UnspentBind").move_to(np.array([JX, 0.15, 0]))
        g_s = mtex('"Com"(g_S)', size=FS_LABEL, color=CYAN).move_to(np.array([0, SR, 0]))
        g_s.align_to(g_r, LEFT)
        self.play(FadeOut(VGroup(useed, emptyr, ulift, a6, a7, trees, pawl, oneway,
                                 ow_t, nseed, nm, a5)),
                  srow[0].animate.move_to(np.array([wrow[0].get_x(), SR, 0])),
                  srow[1].animate.move_to(np.array([wrow[1].get_x(), SR, 0])),
                  FadeIn(g_s), run_time=1.0)
        j1 = flow(g_r, ub, color=GOLD)
        j2 = flow(g_s, ub, color=CYAN)
        self.play(FadeIn(ub, scale=1.1), ShowCreation(j1), ShowCreation(j2), run_time=0.7)
        self.pad_to(A("quotient check") - 0.5)
        ident = mtex('g_R (z) = g_S (z) dot q(z)', size=FS_LABEL, color=STAR)
        ident.move_to(np.array([0, -1.95, 0])).align_to(np.array([6.5, 0, 0]), RIGHT)
        self.play(Write(ident), run_time=1.1)
        self.pad_to(AA(["divides the wallets", "divides the wallet's"]) - 0.5)
        q_br = bracket(VGroup(*wrow[2:]), color=AMBER, buff=0.12)
        q_t = mtex('q(z)', size=FS_LABEL, color=AMBER).next_to(q_br, UP, buff=0.1)
        self.play(*[wrow[i][0].animate.set_stroke(AMBER).set_fill(AMBER, 0.12)
                    for i in range(2, 8)],
                  *[wrow[i][1].animate.set_fill(AMBER) for i in range(2, 8)],
                  GrowFromCenter(q_br), FadeIn(q_t), run_time=1.2)

        # every factor binds an epoch to a value
        self.pad_to(A("factor binds") - 0.5)
        zoom = tex_chip('((i+1) X + "nf"_i)^3 - c', color=GOLD, size=FS_BODY)
        zoom.move_to(np.array([-4.1, 1.75, 0]))
        self.play(FadeIn(zoom, scale=1.5), Indicate(wrow[0], color=STAR),
                  run_time=0.9)
        self.pad_to(A("exact epoch") - 0.4)
        self.play(Indicate(zoom, color=GOLD, scale_factor=1.08), run_time=0.8)
        self.pad_to(A("delegated work") - 0.4)
        bound = caption("delegated work, bound to a note the service never saw",
                        color=GOLD)
        self.play(FadeIn(bound, shift=UP * 0.1), run_time=0.8)

        # SpendableLift seams the bound range onto the running proof
        self.pad_to(A("spendable lift") - 0.4)
        bridge_t = scene_title("the bridge", color=GOLD)
        nu = header_box('mono("NoteUnspent"){"cm", s_L, s_R, "sntl", "sntl"\'}',
                        color=GOLD, size=FS_SMALL)
        sl = step_pill("SpendableLift")
        ns_line = header_box('mono("NoteSpendable"){"cm", e_"incl"+1, "sntl"}', color=GOLD,
                             size=FS_SMALL)
        VGroup(ns_line, sl, nu).arrange(RIGHT, buff=0.8).move_to(UP * 1.45)
        ns_back = (ReplacementTransform(ns2, ns_line)
                   if len(ns2[1].submobjects) == len(ns_line[1].submobjects)
                   else FadeTransform(ns2, ns_line))
        self.play(FadeOut(VGroup(w_lane, s_lane, wrow, srow, g_r, g_s, q_br, q_t, zoom,
                                 ident, j1, j2, bound, br1_t)), swap(b2_t, bridge_t),
                  run_time=0.8)
        self.play(LaggedStart(ns_back, AnimationGroup(absorb(ub, nu), FadeIn(nu, scale=1.5)),
                              FadeIn(sl, scale=1.1), lag_ratio=0.5), run_time=1.3)
        self.pad_to(A("endpoint to endpoint") - 0.4)
        pin1 = eq_pin(ns_line, sl, color=STAR)
        pin2 = eq_pin(sl, nu, color=STAR)
        self.play(ShowCreation(pin1), ShowCreation(pin2), run_time=0.8)
        self.pad_to(AA(["finishes as before", "finishes"]) - 0.5)
        sbq = step_pill("SpendBind").move_to(np.array([sl.get_x(), 0.0, 0]))
        sb_ar = flow(sl, sbq)
        self.play(FadeIn(sbq, scale=1.1), ShowCreation(sb_ar), run_time=0.7)

        # UnspentMerge: adjacent ranges join
        self.pad_to(A("several services") - 0.4)
        ra = tex_chip('[s_L, s_M)', color=CYAN, size=FS_LABEL)
        rb = tex_chip('[s_M, s_R)', color=CYAN, size=FS_LABEL)
        VGroup(ra, rb).arrange(RIGHT, buff=0.4).move_to(np.array([nu.get_x(), -1.3, 0]))
        self.play(FadeIn(ra, shift=UP * 0.1), FadeIn(rb, shift=UP * 0.1), run_time=0.6)
        self.pad_to(A("unspent merge") - 0.3)
        rm = tex_chip('[s_L, s_R)', color=CYAN, size=FS_LABEL)
        rm.move_to(np.array([nu.get_x(), -1.3, 0]))
        um = step_pill("UnspentMerge", color=CYAN).move_to(np.array([nu.get_x(), 0.0, 0]))
        um_a = flow(rm, um, color=CYAN)
        um_b = flow(um, nu, color=CYAN)
        self.play(ra.animate.move_to(rm).set_opacity(0), rb.animate.move_to(rm).set_opacity(0),
                  FadeIn(rm, scale=1.5), FadeIn(um, scale=1.1), run_time=0.8)
        self.remove(ra, rb)
        self.play(ShowCreation(um_a), ShowCreation(um_b), run_time=0.4)
        self.pad_to(A("endpoint discipline") - 0.4)
        self.play(Indicate(rm, color=CYAN, scale_factor=1.1), run_time=0.7)

        # ---- the privacy tally -----------------------------------------------
        T = tally63()
        self.pad_to(A("tally what") - 0.5)
        self.play(FadeOut(VGroup(nu, sl, sbq, sb_ar, pin1, pin2, rm, um, um_a, um_b,
                                 ns_line, axis, eticks, cm_dot, cm_t)),
                  swap(bridge_t, T.title), run_time=0.9)
        self.play(ShowCreation(T.oss_p), ShowCreation(T.nev_p),
                  FadeIn(T.oss_t), FadeIn(T.nev_t), run_time=1.0)
        self.pad_to(A("index value pairs") - 0.6)
        self.play(FadeIn(T.seen, lag_ratio=0.15), run_time=0.9)
        self.pad_to(A("from decoys") - 0.6)
        self.play(FadeIn(T.decoys, lag_ratio=0.15), FadeIn(T.dec_t), run_time=0.8)
        for ph, idx in ((["no commitment"], 0), (["no note"], 1),
                        (["another services work", "another service's work"], 2),
                        (["no spend anchor"], 3)):
            self.pad_to(AA(ph) - 0.35)
            self.play(FadeIn(T.nos[idx]), ShowCreation(T.strikes[idx]), run_time=0.55)

        self.pad_to(A("happened in gold") - 0.6)
        self.play(Write(T.gold_t), run_time=1.0)
        self.play(Indicate(T.gold_t, color=GOLD, scale_factor=1.06), run_time=0.7)
        self.pad_to(scene_T("6.3"))


# ---- 6.4 builders (also used to open 6.5) -----------------------------------
TL64 = 0.0


def timeline64():
    """The consensus timeline: epochs e-1, e, (e+1), sentinels, tip, target anchor."""
    W = SimpleNamespace()
    W.tl = Line(np.array([-6.4, TL64, 0]), np.array([6.3, TL64, 0]),
                stroke_width=SW, stroke_color=DIM)
    W.g1 = sentinel_gate(0.9).move_to(np.array([-2.2, TL64, 0]))
    W.g2 = sentinel_gate(0.9).move_to(np.array([2.2, TL64, 0]))
    W.e_old = mtex('e - 1', size=FS_BODY, color=MUT).move_to(np.array([-4.3, 0.72, 0]))
    W.e_cur = mtex('e', size=FS_BODY, color=MUT).move_to(np.array([0.0, 0.72, 0]))
    W.e_nxt = mtex('e + 1', size=FS_BODY, color=MUT).move_to(np.array([4.25, 0.72, 0]))
    W.tip = Line(UP * 0.22, DOWN * 0.22, stroke_width=SW_BOLD, stroke_color=TXT)
    W.tip.move_to(np.array([1.1, TL64, 0]))
    W.tip_t = label("tip", size=FS_SMALL, color=TXT).next_to(W.tip, DOWN, buff=0.12)
    W.tgt = Triangle().scale(0.13).set_fill(GOLD, 1).set_stroke(width=0)
    W.tgt.move_to(np.array([-0.8, TL64 - 0.3, 0]))
    W.tgt_t = label("target anchor", size=FS_SMALL, color=GOLD).next_to(W.tgt, DOWN, buff=0.1)
    W.win = RoundedRectangle(width=8.4, height=2.2, corner_radius=0.18)
    W.win.set_stroke(FLARE, SW, 0.95).set_fill(FLARE, 0.06)
    W.win.move_to(np.array([-2.0, 0.12, 0]))
    W.win_t = label("duplicate window", size=FS_LABEL, color=FLARE)
    W.win_t.next_to(W.win, DOWN, buff=0.12).align_to(W.win, RIGHT)
    NY = -1.85
    W.nf1 = bead(FLARE, 0.13).move_to(np.array([-0.8, NY, 0]))
    W.nf2 = bead(FLARE, 0.13).move_to(np.array([3.0, NY, 0]))
    W.nf1_t = mtex('"nf"_e', size=FS_LABEL, color=FLARE).next_to(W.nf1, DOWN, buff=0.15)
    W.nf2_t = mtex('"nf"_(e+1)', size=FS_LABEL, color=FLARE).next_to(W.nf2, DOWN, buff=0.15)
    W.ring1 = Circle(radius=0.24).set_stroke(GOLD, 2.4, 0.95).move_to(W.nf1)
    W.ring2 = Circle(radius=0.24).set_stroke(GOLD, 2.4, 0.95).move_to(W.nf2)
    W.pair_br = bracket(VGroup(W.nf1_t, W.nf2_t), color=GOLD, buff=0.15, below=True)
    W.seam_x = x_mark(W.g2.get_center(), r=0.3, color=GOLD)
    W.grid = VGroup(*[Square(side_length=0.17).set_fill(FLARE, 0.65)
                      .set_stroke(AMBER, 0.6, 0.35) for _ in range(96)])
    W.grid.arrange_in_grid(6, 16, buff=0.05)
    W.grid.move_to(np.array([-3.5, 2.35, 0]))
    W.perm = heading("two epochs wide. permanently.", size=FS_HEAD, color=GOLD)
    W.perm.move_to(np.array([1.6, 2.3, 0]))
    return W


WIN_B64 = np.array([2.05, 0.12, 0])     # the window during case B (and at the end)


def caged_grid(W):
    """The opening's hot set, re-laid as a faint band inside the two-epoch window."""
    tgt = W.grid.copy()
    tgt.arrange_in_grid(4, 24, buff=0.06)
    tgt.set_width(W.win.get_width() - 0.5)
    tgt.move_to(WIN_B64)
    for sq in tgt:
        sq.set_fill(FLARE, 0.12).set_stroke(AMBER, 0.6, 0.12)
    return tgt


def final64(W):
    W.win.move_to(WIN_B64)
    W.win_t.align_to(np.array([6.25, 0, 0]), RIGHT)
    W.grid.become(caged_grid(W))
    W.visible = VGroup(W.grid, W.tl, W.g1, W.g2, W.e_old, W.e_cur, W.e_nxt, W.tip, W.tip_t,
                       W.tgt, W.tgt_t, W.win, W.win_t, W.nf1, W.nf2, W.nf1_t, W.nf2_t,
                       W.ring1, W.ring2, W.pair_br, W.seam_x, W.perm)
    return W


class Scene64(TimedScene):
    """6.4 — Consensus: the two-epoch window."""

    def construct(self):
        A = lambda p, o=1: anchor("6.4", p, o)
        AA = lambda ps, o=1: anchor_any("6.4", ps, o)

        # open on 6.3's final frame; all of it folds into one stamp
        T = tally63()
        self.add(T.all)
        VY = 0.0                 # centred on the stage until the work bars arrive
        st = key_chip("stamp", color=GOLD, size=FS_BODY).move_to(np.array([5.0, VY, 0]))
        self.pad_to(0.1)
        self.play(LaggedStart(T.all.animate.scale(0.1).move_to(st).set_opacity(0),
                              FadeIn(st, scale=1.5), lag_ratio=0.5), run_time=1.0)
        self.remove(T.all)

        # the validator's desk
        title = scene_title("what's left for the validator?", color=STAR)
        val = panel(3.6, 2.4, color=FLARE, fill_opacity=0.05).move_to(np.array([-4.4, VY, 0]))
        val_t = label("validator", size=FS_LABEL, color=FLARE).next_to(val, DOWN, buff=0.18)
        self.pad_to(AA(["validators desk", "validator's desk"]) - 0.9)
        self.play(ShowCreation(val), FadeIn(val_t), FadeIn(title),
                  st.animate.move_to(val.get_center()), run_time=1.0)

        # four things, per stamp
        self.pad_to(A("four things") - 0.4)
        rows = VGroup(
            check_row("the target anchor is canonical", size=FS_BODY),
            check_row('e = e_"cur" " or " e_"cur" - 1', size=FS_BODY, math=True),
            check_row("accumulators match their lists", size=FS_BODY),
            check_row("one folded proof verifies", size=FS_BODY),
        )
        rows.arrange(DOWN, buff=0.42, aligned_edge=LEFT)
        rows.move_to(np.array([0, VY, 0])).align_to(np.array([-1.6, 0, 0]), LEFT)
        self.play(FadeIn(rows, lag_ratio=0.1), run_time=0.9)
        vt = []
        for ph, i in ((["canonical history"], 0), (["current one"], 1),
                      (["published lists"], 2), (["folded proof"], 3)):
            self.pad_to(AA(ph) - 0.3)
            tick = checkmark(0.24).move_to(rows[i][0]).shift(UP * 0.03)
            vt.append(tick)
            self.play(ShowCreation(tick), rows[i][1].animate.set_fill(TXT), run_time=0.55)
            if i == 2:
                # "the cheap field-operations audit" is spoken before "folded proof"
                self.pad_to(A("field operations") - 0.4)
                fo = pill("field ops only", color=GOLD, size=FS_SMALL)
                fo.next_to(rows[2], RIGHT, buff=0.3)
                self.play(FadeIn(fo, shift=LEFT * 0.1), run_time=0.5)

        # constant-ish work
        self.pad_to(A("constant ish") - 0.4)
        bar_h = Line(ORIGIN, RIGHT * 10.0, stroke_width=12, stroke_color=DIM)
        bar_v = Line(ORIGIN, RIGHT * 0.8, stroke_width=12, stroke_color=GOLD)
        bars = VGroup(bar_h, bar_v).arrange(DOWN, buff=0.75, aligned_edge=LEFT)
        bars.move_to(np.array([0, -1.95, 0])).align_to(np.array([-6.3, 0, 0]), LEFT)
        bt1 = label("history the proof covers", size=FS_SMALL, color=MUT)
        bt1.next_to(bar_h, UP, buff=0.12, aligned_edge=LEFT)
        bt2 = label("validator work: about constant", size=FS_SMALL, color=GOLD)
        bt2.next_to(bar_v, RIGHT, buff=0.3)
        upper = VGroup(val, val_t, st, rows, *vt, fo)
        self.play(upper.animate.shift(UP * 0.9), run_time=0.6)
        self.play(ShowCreation(bar_h), FadeIn(bt1), run_time=0.7)
        self.play(ShowCreation(bar_v), FadeIn(bt2), run_time=0.6)
        self.pad_to(A("validation delivered") - 0.6)
        deliv = rich([("client-side validation, delivered", STAR)])
        deliv.add(checkmark(0.24, color=STAR).next_to(deliv, RIGHT, buff=0.2))
        deliv.move_to(UP * CAPTION_Y)
        self.play(FadeIn(deliv, scale=1.1), run_time=0.8)

        # read the guarantee precisely: the timeline
        W = timeline64()
        self.pad_to(A("guarantee precisely") - 0.6)
        proves_t = scene_title("what a stamp proves", color=STAR)
        self.play(FadeOut(VGroup(bars, bt1, bt2, deliv, st, val, val_t, rows,
                                 VGroup(*vt), fo)), swap(title, proves_t),
                  run_time=1.0)
        self.play(ShowCreation(W.tl), FadeIn(W.g1), FadeIn(W.g2), FadeIn(W.e_old),
                  FadeIn(W.e_cur), FadeIn(W.tip), FadeIn(W.tip_t), FadeIn(W.tgt),
                  FadeIn(W.tgt_t), run_time=1.1)
        self.pad_to(A("proves exclusion before") - 0.5)
        claim = bracket(Line(np.array([-6.3, TL64, 0]), W.g1.get_center()), color=STAR,
                        buff=1.1, below=True)
        claim_t = label("proven exclusion, up to here", size=FS_SMALL, color=STAR)
        claim_t.next_to(claim, DOWN, buff=0.12)
        self.play(GrowFromCenter(claim), FadeIn(claim_t), run_time=0.9)
        self.pad_to(A("nothing about") - 0.4)
        hatch = VGroup(*[VMobject().set_points_as_corners(
            [np.array([-2.0 + 0.4 * i, TL64 - 0.25, 0]), np.array([-1.75 + 0.4 * i, TL64 + 0.25, 0])])
            .set_stroke(FLARE, 2.0, 0.6) for i in range(8)])
        self.play(ShowCreation(hatch, lag_ratio=0.08), run_time=0.8)
        self.pad_to(A("still being written") - 0.4)
        writ = label("still being written", size=FS_SMALL, color=FLARE)
        writ.next_to(W.tip, UP, buff=0.75).shift(RIGHT * 0.5)
        self.play(FadeIn(writ), run_time=0.6)

        # the rule: one window over current + preceding epochs
        win, win_t = W.win, W.win_t
        self.pad_to(AA(["the rule keep", "the rule"]) - 0.4)
        self.play(FadeOut(VGroup(hatch, writ, claim, claim_t)),
                  ShowCreation(win), FadeIn(win_t), run_time=0.9)
        self.pad_to(A("deterministic order") - 0.5)
        qbeads = VGroup(*[bead(AMBER, 0.11) for _ in range(3)])
        qbeads.arrange(RIGHT, buff=0.35).move_to(np.array([5.0, 1.9, 0]))
        q_t = label("candidates, in order", size=FS_SMALL, color=AMBER)
        q_t.next_to(qbeads, UP, buff=0.15)
        self.play(FadeIn(qbeads, lag_ratio=0.2), FadeIn(q_t), run_time=0.5)
        # check at the window's edge, then insert into the current epoch
        self.pad_to(A("check then insert") - 0.4)
        door = np.array([W.g2.get_x(), 0.42, 0])
        slots_in = [np.array([-1.75 + 0.42 * i, 0.42, 0]) for i in range(3)]
        for i, b in enumerate(qbeads):
            self.play(b.animate.move_to(door), run_time=0.22)
            self.play(b.animate.move_to(slots_in[i]),
                      Flash(door, color=STAR, flash_radius=0.24, line_length=0.12,
                            num_lines=10), run_time=0.33)

        # why two epochs? the grace period
        self.pad_to(A("why two epochs") - 0.4)
        why = scene_title("why two epochs?")
        self.play(swap(proves_t, why), FadeOut(q_t), run_time=0.9)
        self.pad_to(A("grace period") - 0.4)
        grace = bracket(Line(np.array([-0.8, TL64, 0]), np.array([4.6, TL64, 0])),
                        color=GOLD, buff=1.4)
        grace_t = label("targets e, still accepted in e + 1", size=FS_SMALL, color=GOLD)
        grace_t.next_to(grace, UP, buff=0.12)
        self.play(FadeIn(W.e_nxt), GrowFromCenter(grace), FadeIn(grace_t), run_time=0.9)

        # our pair of published nullifiers
        nf1, nf2 = W.nf1, W.nf2
        self.pad_to(A("published nullifiers") - 0.5)
        self.play(FadeOut(VGroup(grace, grace_t, qbeads)),
                  FadeIn(nf1, scale=1.4), FadeIn(nf2, scale=1.4),
                  FadeIn(W.nf1_t), FadeIn(W.nf2_t),
                  ShowCreation(W.ring1), ShowCreation(W.ring2), run_time=1.0)

        # case A: accepted during e
        self.pad_to(AA(["excepted during e", "accepted during e"]) - 0.4)
        caseA = pill("accepted during e", color=GOLD, size=FS_LABEL)
        caseA.move_to(np.array([-4.3, 2.15, 0]))
        self.play(FadeIn(caseA), run_time=0.5)
        self.pad_to(A("collides") - 0.5)
        r1 = bead(AMBER, 0.12).move_to(np.array([-0.8, 2.0, 0]))
        self.play(FadeIn(r1), run_time=0.3)
        self.play(r1.animate.move_to(nf1.get_center()), run_time=0.5)
        self.play(Flash(nf1, color=FLARE, flash_radius=0.45), FadeOut(r1), run_time=0.5)
        # a rival targeting e-1: its next-epoch nullifier is the same nf_e
        self.pad_to(A("minus one published") - 0.6)
        r2 = bead(AMBER, 0.12).move_to(np.array([-4.3, 0.4, 0]))
        r2b = bead(AMBER, 0.1).move_to(r2)
        self.play(FadeIn(r2, scale=1.4), run_time=0.4)
        self.add(r2b)
        self.play(r2b.animate.move_to(nf1.get_center()), run_time=0.6)
        self.play(Flash(nf1, color=FLARE, flash_radius=0.45),
                  FadeOut(r2), FadeOut(r2b), run_time=0.5)
        self.pad_to(A("anything older") - 0.4)
        hist = bracket(Line(np.array([-6.3, TL64, 0]), W.g1.get_center()), color=STAR,
                       buff=1.35, below=True)
        hist_t = label("inside the proven history", size=FS_SMALL, color=STAR)
        hist_t.next_to(hist, DOWN, buff=0.1)
        self.play(GrowFromCenter(hist), FadeIn(hist_t), run_time=0.8)

        # case B: accepted during e+1 — the window slides
        self.pad_to(A("during e plus one") - 0.5)
        caseB = pill("accepted during e + 1", color=GOLD, size=FS_LABEL).move_to(caseA)
        self.play(swap(caseA, caseB, lag=0.6), FadeOut(hist), FadeOut(hist_t),
                  win.animate.move_to(WIN_B64),
                  win_t.animate.align_to(np.array([6.25, 0, 0]), RIGHT), run_time=0.9)
        self.pad_to(A("either epoch") - 0.4)
        r3 = bead(AMBER, 0.12).move_to(np.array([-0.8, 2.0, 0]))
        r4 = bead(AMBER, 0.12).move_to(np.array([3.0, 2.0, 0]))
        self.play(FadeIn(r3), FadeIn(r4), run_time=0.3)
        self.play(r3.animate.move_to(nf1.get_center()),
                  r4.animate.move_to(nf2.get_center()), run_time=0.5)
        self.play(Flash(nf1, color=FLARE, flash_radius=0.45),
                  Flash(nf2, color=FLARE, flash_radius=0.45),
                  FadeOut(r3), FadeOut(r4), run_time=0.5)
        self.pad_to(A("earlier acceptance") - 0.4)
        self.play(Indicate(VGroup(nf1, W.ring1), color=FLARE, scale_factor=1.3), run_time=0.7)

        # the adjacent pair overlaps every boundary
        self.pad_to(A("adjacent pair") - 0.4)
        self.play(GrowFromCenter(W.pair_br),
                  Indicate(VGroup(nf1, nf2, W.ring1, W.ring2), color=GOLD, scale_factor=1.15),
                  run_time=0.8)
        self.pad_to(A("no seam") - 0.3)
        self.play(ShowCreation(W.seam_x), run_time=0.5)

        # the opening's monster, tamed: it now lives inside the two-epoch window
        grid = W.grid
        self.pad_to(A("monster") - 0.5)
        self.play(FadeOut(VGroup(caseB, why)), FadeIn(grid, lag_ratio=0.01), run_time=1.1)
        add_shimmer(grid, amp=0.18)
        g_t = label("the set nobody could prune", size=FS_SMALL, color=FLARE)
        g_t.next_to(grid, UP, buff=0.15)
        self.play(FadeIn(g_t), run_time=0.5)
        self.pad_to(A("two epochs wide") - 0.5)
        clear_shimmer(grid)
        self.bring_to_back(grid)
        self.play(Transform(grid, caged_grid(W)), FadeOut(g_t),
                  Indicate(win, color=GOLD, scale_factor=1.03), run_time=1.0)
        add_shimmer(grid, amp=0.25)
        self.pad_to(A("permanently") - 0.4)
        self.play(Write(W.perm), run_time=1.0)
        clear_shimmer(grid)
        self.pad_to(scene_T("6.4"))


class Scene65(TimedScene):
    """6.5 — Aggregation."""

    def construct(self):
        A = lambda p, o=1: anchor("6.5", p, o)
        AA = lambda ps, o=1: anchor_any("6.5", ps, o)

        # open on 6.4's final frame; its timeline becomes this epoch's anchor line
        W = final64(timeline64())
        self.add(W.visible)
        TY = -1.45
        tl = Line(np.array([-6.4, TY, 0]), np.array([4.9, TY, 0]),
                  stroke_width=SW, stroke_color=DIM)
        tx = [-5.6 + 1.9 * i for i in range(6)]
        aticks = VGroup(*[Line(UP * 0.15, DOWN * 0.15, stroke_width=SW, stroke_color=MUT)
                          .move_to(np.array([x, TY, 0])) for x in tx])
        gate = sentinel_gate(1.0).move_to(np.array([4.85, TY, 0]))
        gate_t = mtex('"sntl"', size=FS_SMALL, color=STAR).next_to(gate, RIGHT, buff=0.15)
        tl_t = label("anchors in this epoch", size=FS_SMALL, color=MUT)
        tl_t.next_to(VGroup(aticks[0], aticks[2]), DOWN, buff=0.25)
        title = scene_title("aggregation")
        rest = VGroup(*[m for m in W.visible if m is not W.tl and m is not W.g2])
        self.pad_to(0.3)
        self.play(LaggedStart(AnimationGroup(FadeOut(rest), ReplacementTransform(W.tl, tl),
                                             ReplacementTransform(W.g2, gate)),
                              Write(title), lag_ratio=0.9), run_time=1.8)
        self.play(FadeIn(aticks, lag_ratio=0.1), FadeIn(tl_t), FadeIn(gate_t), run_time=0.8)

        # finished stamps from different transactions, each at its own anchor
        self.pad_to(A("finished stamps") - 0.4)
        stamps, seals = VGroup(), VGroup()
        for i in range(4):
            s = key_chip(f"stamp, tx{i + 1}", color=GOLD, size=FS_LABEL)
            s.move_to(np.array([tx[i], TY + 0.75, 0]))
            seal = Circle(radius=0.11).set_stroke(AMBER, 2.4, 1.0).set_fill(AMBER, 0.45)
            seal.move_to(s.get_corner(UR) + 0.04 * UR)
            stamps.add(s)
            seals.add(seal)
        self.play(LaggedStart(*[AnimationGroup(FadeIn(s, shift=UP * 0.2), FadeIn(seals[i]),
                                               aticks[i].animate.set_stroke(GOLD, SW_BOLD))
                                for i, s in enumerate(stamps)], lag_ratio=0.15),
                  run_time=1.2)

        # lift each to a common anchor: rise into a stack, then slide along the epoch
        self.pad_to(A("lift each") - 0.3)
        target_x = tx[4]
        ys = [2.1 - 0.72 * i for i in range(4)]
        self.play(*[VGroup(stamps[i], seals[i]).animate.shift(UP * (ys[i] - stamps[i].get_y()))
                    for i in range(4)], run_time=0.7)
        self.pad_to(A("common anchor") - 0.4)
        self.play(*[VGroup(stamps[i], seals[i]).animate.shift(RIGHT * (target_x - stamps[i].get_x()))
                    for i in range(4)],
                  *[aticks[i].animate.set_stroke(MUT, SW) for i in range(4)],
                  aticks[4].animate.set_stroke(GOLD, SW_BOLD), run_time=1.0)
        self.pad_to(A("across the sentinel") - 0.4)
        self.play(Indicate(gate, color=STAR, scale_factor=1.25), run_time=0.7)

        # union, multiply, fold
        ops = VGroup(
            tex_chip('union thin "tachygrams"', color=TXT, size=FS_LABEL),
            tex_chip('times thin "accumulators"', color=TXT, size=FS_LABEL),
            tex_chip('"fold the proofs"', color=TXT, size=FS_LABEL),
        )
        ops.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        ops.move_to(np.array([0, 1.4, 0])).align_to(np.array([-6.2, 0, 0]), LEFT)
        self.pad_to(AA(["union the tacky", "union the tachygrams"]) - 0.3)
        self.play(FadeIn(ops[0], shift=RIGHT * 0.2), run_time=0.5)
        self.pad_to(A("multiply the accumulators") - 0.3)
        self.play(FadeIn(ops[1], shift=RIGHT * 0.2), run_time=0.5)
        self.pad_to(A("fold the proofs") - 0.3)
        agg = key_chip("aggregate stamp", color=GOLD, size=FS_BODY)
        agg.move_to(np.array([target_x, 0.6, 0]))
        tok = proof_token(0.15).next_to(agg, UP, buff=0.25)
        self.play(FadeIn(ops[2], shift=RIGHT * 0.2), run_time=0.5)
        self.play(*[absorb(stamps[i], agg) for i in range(4)],
                  *[absorb(seals[i], agg) for i in range(4)], run_time=0.7)
        self.remove(stamps, seals)
        self.play(FadeIn(agg, scale=1.15), FadeIn(tok, scale=1.4), run_time=0.5)

        # each covered transaction keeps a pointer
        self.pad_to(A("pointer") - 0.9)
        txs = VGroup(*[key_chip(f"tx{i + 1}", color=GOLD, size=FS_LABEL) for i in range(4)])
        txs.arrange(RIGHT, buff=0.5).move_to(np.array([target_x, -0.45, 0]))
        txseals = VGroup(*[Circle(radius=0.09).set_stroke(AMBER, 2.2, 1).set_fill(AMBER, 0.45)
                           .move_to(t.get_corner(UR) + 0.03 * UR) for t in txs])
        ptrs = VGroup(*[flow(t, agg, color=MUT) for t in txs])
        self.play(FadeIn(txs, lag_ratio=0.1), FadeIn(txseals, lag_ratio=0.1), run_time=0.8)
        self.play(LaggedStartMap(ShowCreation, ptrs, lag_ratio=0.12), run_time=0.8)

        # signatures and balance stay per transaction
        self.pad_to(A("signatures") - 0.3)
        sig_t = label("signatures + balance: per transaction", size=FS_SMALL, color=AMBER)
        sig_t.next_to(txs, LEFT, buff=0.4)
        self.play(LaggedStart(*[Indicate(s, color=AMBER, scale_factor=1.5)
                                for s in txseals], lag_ratio=0.1),
                  FadeIn(sig_t), run_time=1.0)
        self.pad_to(AA(["never authority"]) - 0.5)
        pna = caption("aggregation touches proofs, never authority")
        self.play(FadeIn(pna, shift=UP * 0.1), run_time=0.7)

        # one proof where there would have been fifty
        self.pad_to(AA(["verified 50", "verified fifty"]) - 1.2)
        fifty = label("50 proofs", size=FS_BODY, color=MUT)
        one = label("1 aggregate proof", size=FS_BODY, color=GOLD)
        arr = mtex('->', size=FS_BODY, color=TXT)
        VGroup(fifty, arr, one).arrange(RIGHT, buff=0.35).move_to(UP * CAPTION_Y)
        self.play(FadeOut(pna), FadeIn(fifty), run_time=0.5)
        self.play(ShowCreation(strike(fifty)), FadeIn(arr), FadeIn(one, scale=1.3),
                  run_time=0.8)

        # the mechanism, already seen
        self.pad_to(A("already seen") - 0.6)
        self.play(Indicate(tok, color=GOLD, scale_factor=1.3), run_time=0.9)
        self.pad_to(scene_T("6.5"))

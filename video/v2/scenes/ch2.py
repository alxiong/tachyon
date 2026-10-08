"""Chapter 2 — Birth: one accumulator, one stamp, one chain (scenes 2.1, 2.2, 2.3).

All arithmetic shown on screen is real arithmetic in F_13.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style import *  # noqa: E402,F403
from style import _norm  # noqa: E402


def WEND(sid, phrase, occ=1):
    """End time (s) of the last word of `phrase`: where a held pause after it begins."""
    import re as _r
    t = anchor(sid, phrase, occ)
    n = len([w for w in _r.split(r"[\s\-]+", phrase.split("|")[0]) if _norm(w)])
    ws = WORDS[sid]
    i = next(k for k, x in enumerate(ws) if abs(x["s"] - t) < 1e-6)
    got = 0
    while True:
        got += max(1, len([q for q in _r.split(r"[\s\-]+", ws[i]["w"]) if _norm(q)]))
        if got >= n:
            return ws[i]["e"]
        i += 1


def mini_tree(color=STAR):
    pts = [[0, 0.8], [-0.8, 0.0], [0.8, 0.0], [-1.2, -0.8], [-0.4, -0.8], [0.4, -0.8], [1.2, -0.8]]
    dots = VGroup(*[Dot([x, y, 0], radius=0.07).set_fill(color, 0.9) for x, y in pts])
    edges = VGroup(*[Line(dots[p].get_center(), dots[c].get_center(), stroke_width=SW_THIN,
                          stroke_color=MUT) for p, c in [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]])
    return VGroup(edges, dots)


def mini_grid(rows=5, cols=7):
    g = VGroup(*[Square(0.22).set_stroke(width=0).set_fill(FLARE, 0.6) for _ in range(rows * cols)])
    return g.arrange_in_grid(rows, cols, buff=0.05)


def strike(mob, color=FLARE):
    vm = VMobject()
    vm.set_points_as_corners([mob.get_corner(DL) + 0.06 * DL, mob.get_corner(UR) + 0.06 * UR])
    vm.set_stroke(color, SW_BOLD, 1.0)
    return vm


def field_cards(names, color=STAR, size=FS_LABEL, w=None):
    """A row of labeled field slots (an action description, a tx field list)."""
    cells = VGroup()
    for n in names:
        t = mtex(n, size=size, color=color)
        box = Rectangle(width=(w or max(0.9, t.get_width() + 0.35)), height=0.72)
        box.set_stroke(color, SW_THIN, 0.85).set_fill(color, 0.05)
        t.move_to(box)
        cells.add(VGroup(box, t))
    return cells.arrange(RIGHT, buff=0)


class Scene21(TimedScene):
    def construct(self):
        SID = "2.1"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731

        title = scene_title("A set as the roots of a polynomial")
        self.wait(0.5)
        self.play(Write(title), run_time=1.0)

        # --- a concrete set in F_13 ------------------------------------------------------
        fl = FieldLine(width=10.6).move_to(UP * 1.2)
        F13 = mtex('FF_13', size=FS_HEAD, color=MUT).next_to(fl, LEFT, buff=0.3).shift(UP * 0.1)
        S = mtex('S = {2, 7, 11}', size=FS_HEAD, color=GOLD).move_to(UP * 2.35)
        self.pad_to(A("numbers two") - 0.1)
        self.play(FadeIn(S[:3]), FadeIn(S[3:5]), run_time=0.4)
        self.pad_to(A("seven") - 0.1)
        self.play(FadeIn(S[5:7]), run_time=0.3)
        self.pad_to(A("eleven") - 0.1)
        self.play(FadeIn(S[7:]), run_time=0.3)
        self.pad_to(A("field with") - 0.2)
        self.play(FadeIn(fl), run_time=0.6)
        self.pad_to(A("thirteen") - 0.1)
        self.play(FadeIn(F13), run_time=0.5)
        roots = {x: fl.root(x) for x in (2, 7, 11)}

        # f(X) built factor by factor
        parts = VGroup(mtex("f(X) =", size=FS_HEAD, color=STAR),
                       mtex("(X - 2)", size=FS_HEAD, color=GOLD),
                       mtex("(X - 7)", size=FS_HEAD, color=GOLD),
                       mtex("(X - 11)", size=FS_HEAD, color=GOLD)).arrange(RIGHT, buff=0.18)
        parts.move_to(DOWN * 0.35)
        self.pad_to(A("build the polynomial") - 0.2)
        self.play(FadeIn(parts[0]), run_time=0.6)
        for i, cue in enumerate(("x minus two", "x minus seven", "x minus eleven")):
            self.pad_to(A(cue) - 0.15)
            self.play(FadeIn(parts[i + 1], shift=LEFT * 0.15), run_time=0.5)
        # pause: each factor drops its root onto the field line
        self.pad_to(WEND(SID, "eleven", 2))
        seeds = [roots[x].copy().move_to(parts[i + 1].get_top() + UP * 0.15) for i, x in enumerate((2, 7, 11))]
        self.play(LaggedStart(*[Succession(FadeIn(sd, scale=2.0, run_time=0.25),
                                           ReplacementTransform(sd, roots[x], path_arc=-0.5, run_time=0.5))
                                for sd, x in zip(seeds, (2, 7, 11))], lag_ratio=0.3), run_time=0.8)
        self.play(FadeOut(S), *[Flash(roots[x].get_center(), color=GOLD, flash_radius=0.25) for x in roots],
                  run_time=0.3)
        self.pad_to(A("committing") - 0.05)
        env = envelope(1.9, 1.15, color=CYAN, tex_label="f(X)").next_to(parts, RIGHT, buff=0.7)
        acc = label("accumulator", size=FS_LABEL, color=CYAN).next_to(env, DOWN, buff=0.2)
        self.play(FadeIn(env, scale=0.8), run_time=0.7)
        self.pad_to(A("accumulator") - 0.1)
        self.play(FadeIn(acc), run_time=0.5)

        # --- membership = one evaluation -----------------------------------------------------
        p7 = fl.probe(7, color=GOLD, h=1.3)
        r7 = mtex("f(7) = 0", size=FS_HEAD, color=GOLD).move_to(DOWN * 1.7 + LEFT * 2.6)
        self.pad_to(A("single evaluation") - 0.2)
        self.play(Indicate(parts, color=STAR, scale_factor=1.05), run_time=0.8)
        self.pad_to(A("seven gives") - 0.2)
        self.play(ShowCreation(p7), run_time=0.5)
        self.pad_to(A("zero") - 0.2)
        inn = label("in", size=FS_BODY, color=GOLD).next_to(r7, DOWN, buff=0.3)
        self.play(FadeIn(VGroup(r7, inn), shift=UP * 0.1), Flash(fl.n2p(7), color=GOLD), run_time=0.6)
        p5 = fl.probe(5, color=FLARE, h=1.3)
        r5 = mtex("f(5) = 3 dot (-2) dot (-6) = 10 eq.not 0", size=FS_HEAD, color=FLARE)
        r5.move_to(DOWN * 1.7 + RIGHT * 2.4)
        self.pad_to(A("five gives") - 0.2)
        self.play(ShowCreation(p5), run_time=0.5)
        self.pad_to(A("nonzero") - 0.3)
        self.play(FadeIn(r5, shift=UP * 0.1), run_time=0.7)
        out = label("out", size=FS_BODY, color=FLARE).next_to(r5, DOWN, buff=0.3)
        self.pad_to(A("isn't in") - 0.2)
        self.play(FadeIn(out), run_time=0.4)
        self.pad_to(A("query part") - 0.3)
        qport = label("Ragu's query part", size=FS_LABEL, color=CYAN).next_to(env, UP, buff=0.25)
        self.play(FadeIn(qport, shift=DOWN * 0.1), Indicate(env, color=CYAN), run_time=0.8)

        # --- two structures become one -------------------------------------------------------
        self.pad_to(A("right now") - 0.2)
        stage1 = VGroup(fl, F13, *roots.values(), parts, p7, p5, r7, r5, inn, out, qport)
        self.play(FadeOut(stage1), FadeOut(acc), env.animate.move_to(ORIGIN + DOWN * 0.2).fade(1),
                  run_time=0.8)
        tree = mini_tree().move_to(LEFT * 3.6 + DOWN * 0.2)
        grid = mini_grid().move_to(RIGHT * 3.6 + DOWN * 0.2)
        tl = label("Merkle tree: membership of cm", size=FS_LABEL, color=STAR).next_to(tree, DOWN, buff=0.35)
        gl = label("set: non-membership of nf", size=FS_LABEL, color=FLARE).next_to(grid, DOWN, buff=0.35)
        self.pad_to(A("two different structures") - 0.3)
        self.play(FadeIn(tree), FadeIn(grid), run_time=0.8)
        self.pad_to(A("merkle tree") - 0.1)
        self.play(FadeIn(tl), run_time=0.5)
        self.pad_to(A("a set for") - 0.1)
        self.play(FadeIn(gl), run_time=0.5)
        self.pad_to(A("one structure") - 0.2)
        self.play(Indicate(VGroup(tree, grid), color=CYAN, scale_factor=1.05), run_time=0.8)
        # pause: the tree and the grid dissolve into one accumulator
        self.pad_to(WEND(SID, "tachyon doesn't"))
        one = envelope(2.2, 1.35, color=CYAN, tex_label="f(X)").move_to(DOWN * 0.2)
        one_l = VGroup(label("one accumulator", size=FS_BODY, color=CYAN),
                       mtex('f(X) = scripts(product)_i (X - "tg"_i)', size=FS_BODY, color=CYAN)).arrange(DOWN, buff=0.2)
        one_l.next_to(one, DOWN, buff=0.3)
        self.play(tree.animate.scale(0.25).move_to(one).set_opacity(0),
                  grid.animate.scale(0.25).move_to(one).set_opacity(0), FadeOut(VGroup(tl, gl)),
                  FadeIn(one, scale=1.6, rate_func=squish_rate_func(smooth, 0.35, 1.0)), run_time=1.0)
        self.remove(tree, grid)
        self.pad_to(A("every member") - 0.1)
        self.play(FadeIn(one_l), run_time=0.6)
        self.pad_to(A("tachygram") - 0.4)
        chips = VGroup(tg_chip('"cm"', color=GOLD), tg_chip('"nf"', color=FLARE), tg_chip('"tg"'),
                       tg_chip('"tg"'), tg_chip('"tg"')).arrange(RIGHT, buff=0.35).move_to(DOWN * 2.6)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in chips[2:]], lag_ratio=0.2), run_time=0.8)
        blob = label("a 32-byte blob", size=FS_LABEL, color=MUT).next_to(chips, RIGHT, buff=0.4)
        self.pad_to(A("thirty two") - 0.1)
        self.play(FadeIn(blob), run_time=0.4)
        self.pad_to(A("note commitment") - 0.2)
        self.play(FadeIn(chips[0], shift=UP * 0.2), run_time=0.5)
        self.pad_to(A("nullifier") - 0.2)
        self.play(FadeIn(chips[1], shift=UP * 0.2), run_time=0.5)
        self.pad_to(A("can't tell|cant tell") - 0.2)
        same = VGroup(tg_chip('"tg"').move_to(chips[0]), tg_chip('"tg"').move_to(chips[1]))
        self.play(Transform(chips[0], same[0]), Transform(chips[1], same[1]), run_time=0.8)

        # --- the dictionary ------------------------------------------------------------------
        self.pad_to(A("set operations") - 0.2)
        self.play(FadeOut(VGroup(one, one_l, chips, blob)), run_time=0.6)
        fl2 = FieldLine(width=7.0).move_to(LEFT * 2.6 + UP * 1.5)
        rts = VGroup(*[fl2.root(x) for x in (2, 7, 11)])
        hdr = VGroup(label("set", size=FS_BODY, color=MUT), label("polynomial", size=FS_BODY, color=MUT))
        rows_src = [("insert x", 'times (X - x)'), ("remove x", 'div (X - x)'),
                    ("union", 'f dot g'), ("subset", 'g divides f')]
        rows = VGroup(*[VGroup(label(a, size=FS_BODY, color=STAR), mtex(b, size=FS_BODY, color=GOLD))
                        for a, b in rows_src])
        table = VGroup(hdr, *rows)
        for k, r in enumerate(table):
            y = 0.35 - 0.62 * k
            r[0].move_to([-5.9, y, 0], aligned_edge=LEFT)
            r[1].move_to([-2.9, y, 0], aligned_edge=LEFT)
        note1 = label("no disjointness needed", size=FS_LABEL, color=MUT).move_to([0.2, rows[2].get_y(), 0], aligned_edge=LEFT)
        note2 = label("exact division", size=FS_LABEL, color=MUT).move_to([0.2, rows[3].get_y(), 0], aligned_edge=LEFT)
        self.play(FadeIn(fl2), FadeIn(rts), FadeIn(hdr), run_time=0.8)
        new = fl2.root(4, color=GOLD)
        self.pad_to(A("inserting") - 0.2)
        self.play(FadeIn(rows[0]), FadeIn(new, shift=DOWN * 0.5), run_time=0.6)
        self.pad_to(A("removing") - 0.2)
        self.play(FadeIn(rows[1]), FadeOut(new, shift=UP * 0.5), run_time=0.6)
        self.pad_to(A("union") - 0.2)
        self.play(FadeIn(rows[2]), run_time=0.5)
        self.pad_to(A("disjoint") - 0.3)
        self.play(FadeIn(note1), run_time=0.4)
        self.pad_to(A("subset") - 0.2)
        self.play(FadeIn(rows[3]), run_time=0.5)
        self.pad_to(A("exact division") - 0.2)
        self.play(FadeIn(note2), run_time=0.4)
        self.pad_to(A("single random point") - 0.3)
        rp = label("each: one identity at one random point", size=FS_BODY, color=CYAN)
        rp.move_to(UP * CAPTION_Y)
        self.play(FadeIn(rp, shift=UP * 0.1), run_time=0.6)
        # pause: the dictionary completes, every row ticked off
        ticks = VGroup(*[checkmark(0.34, color=CYAN).move_to([-0.35, r.get_y(), 0]) for r in rows])
        self.pad_to(WEND(SID, "single random point"))
        self.play(LaggedStart(*[ShowCreation(t) for t in ticks], lag_ratio=0.25), run_time=0.9)

        # --- multiset; consensus makes it square-free ----------------------------------------------
        self.pad_to(A("multiplicity") - 0.3)
        dup = fl2.root(7, color=FLARE).shift(UP * 0.28)
        sq = mtex("(X - 7)^2", size=FS_BODY, color=FLARE).next_to(fl2, RIGHT, buff=0.5)
        self.play(FadeOut(VGroup(table, note1, note2, rp, ticks)), FadeIn(dup, shift=DOWN * 0.3), FadeIn(sq), run_time=0.8)
        ms = label("a multiset", size=FS_BODY, color=STAR).next_to(sq, DOWN, buff=0.3)
        self.pad_to(A("multiset") - 0.2)
        self.play(FadeIn(ms), run_time=0.4)
        self.pad_to(A("refuses") - 0.2)
        x = strike(sq)
        self.play(ShowCreation(x), FadeOut(dup, shift=UP * 0.3), run_time=0.5)
        self.pad_to(A("distinct roots") - 0.3)
        sf = label("distinct roots (square-free)", size=FS_BODY, color=GOLD).move_to(DOWN * 0.6 + LEFT * 2.6)
        self.play(FadeOut(VGroup(sq, x, ms)), FadeIn(sf, shift=UP * 0.1), run_time=0.7)
        self.play(Indicate(rts, color=GOLD, scale_factor=1.4), run_time=0.8)

        # --- binding is not correctness -----------------------------------------------------------
        self.pad_to(A("one subtlety") - 0.2)
        self.play(FadeOut(sf), fl2.animate.move_to(UP * 1.4), rts.animate.shift(RIGHT * 2.6 + DOWN * 0.1),
                  run_time=0.8)
        env2 = envelope(1.9, 1.15, color=CYAN, tex_label="f(X)").move_to(LEFT * 4.2 + DOWN * 1.0)
        pub = VGroup(*[tg_chip(str(v)) for v in (2, 7, 11)]).arrange(RIGHT, buff=0.25)
        pub.move_to(RIGHT * 3.6 + DOWN * 1.0)
        pub_l = label("published tachygrams", size=FS_LABEL, color=MUT).next_to(pub, DOWN, buff=0.25)
        self.pad_to(A("commitment binding") - 0.2)
        self.play(FadeIn(env2, scale=0.8), run_time=0.7)
        bind = label("opens to one polynomial", size=FS_LABEL, color=CYAN).next_to(env2, DOWN, buff=0.25)
        self.pad_to(A("opens to") - 0.2)
        self.play(FadeIn(bind), run_time=0.5)
        self.pad_to(A("published roots") - 0.3)
        neq = mtex('"roots"(f) =^? {2, 7, 11}', size=FS_BODY, color=STAR).move_to(DOWN * 1.0)
        self.play(FadeIn(pub), FadeIn(pub_l), FadeIn(neq), run_time=0.8)
        ghost = fl2.root(4, color=FLARE)
        ghost_ring = Circle(radius=0.2).set_stroke(FLARE, SW_THIN).move_to(ghost)
        self.pad_to(A("extra root") - 0.2)
        self.play(FadeIn(ghost, shift=DOWN * 0.4), ShowCreation(ghost_ring), run_time=0.5)
        self.pad_to(A("drop one") - 0.2)
        self.play(rts[2].animate.set_fill(DIM, 0.5), run_time=0.5)
        lie = mtex("f(4) = 0 ?!", size=FS_BODY, color=FLARE).next_to(ghost, UP, buff=0.75)
        p4 = fl2.probe(4, color=FLARE, h=0.65)
        # pause: the probe hits the ghost root and the query lies
        self.pad_to(WEND(SID, "wrong answers"))
        self.play(ShowCreation(p4), run_time=0.4)
        self.play(FadeIn(lie, shift=DOWN * 0.1), Flash(ghost.get_center(), color=FLARE, flash_radius=0.3),
                  run_time=0.6)

        # the audit: y_r computed by the verifier from the list
        self.pad_to(A("checks each") - 0.3)
        self.play(FadeOut(VGroup(neq, lie, bind, p4)), run_time=0.5)
        self.pad_to(A("picks a random") - 0.2)
        rr = mtex("r = 9", size=FS_BODY, color=STAR).move_to(UP * 0.0)
        self.play(FadeIn(rr), run_time=0.5)
        yr = mtex("y_r = (9-2)(9-7)(9-11) = 11", size=FS_BODY, color=STAR).next_to(pub_l, DOWN, buff=0.3)
        yr.set_x(2.6)
        self.pad_to(A("computes the product") - 0.2)
        self.play(TransformFromCopy(pub, yr), run_time=1.0)
        fo = label("field ops only, no group work", size=FS_LABEL, color=MUT).next_to(yr, DOWN, buff=0.2)
        self.pad_to(A("field operations") - 0.2)
        self.play(FadeIn(fo), run_time=0.5)
        self.pad_to(A("open at") - 0.3)
        op = mtex("f(9) = 11 dot (9-4) = 3 eq.not 11", size=FS_BODY, color=FLARE).next_to(env2, DOWN, buff=0.3)
        op.align_to(env2, LEFT)
        self.play(FadeIn(op, shift=UP * 0.1), run_time=0.7)
        self.play(Flash(op.get_right(), color=FLARE), Indicate(ghost, color=FLARE), run_time=0.7)
        self.pad_to(A("false polynomial") - 0.2)
        pr = mtex(r'Pr["false passes"] <= D \/ |FF|', size=FS_HEAD, color=STAR).move_to(UP * CAPTION_Y)
        self.play(FadeIn(pr, shift=UP * 0.1), run_time=0.8)
        self.pad_to(scene_T(SID))


class Scene22(TimedScene):
    def construct(self):
        SID = "2.2"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731

        self.wait(0.3)
        title = scene_title("The action and the stamp")
        self.play(Write(title), run_time=1.0)

        # --- Tachyon action: (rk, cv) -----------------------------------------------------------
        self.pad_to(A("output action") - 0.2)
        oa = label("output action", size=FS_BODY, color=GOLD).move_to(UP * 1.75 + RIGHT * 2.5)
        self.play(FadeIn(oa), run_time=0.5)
        tach = field_cards(['"rk"', '"cv"'], color=GOLD, size=FS_HEAD, w=1.4).next_to(oa, DOWN, buff=0.3)
        gl_rk = rich([('$"rk"$', GOLD), ("randomized key", MUT)], size=FS_SMALL)
        gl_cv = rich([('$"cv"$', GOLD), ("value commitment", MUT)], size=FS_SMALL)
        gloss = VGroup(gl_rk, gl_cv).arrange(DOWN, buff=0.14, aligned_edge=LEFT).next_to(tach, DOWN, buff=0.25)
        self.pad_to(A("two values") - 0.2)
        self.play(FadeIn(tach[0].submobjects[0]), FadeIn(tach[1].submobjects[0]), run_time=0.5)
        self.pad_to(A("randomized key") - 0.1)
        self.play(FadeIn(tach[0][1]), FadeIn(gl_rk), run_time=0.4)
        self.pad_to(A("value commitment") - 0.1)
        self.play(FadeIn(tach[1][1]), FadeIn(gl_cv), run_time=0.4)
        spend = field_cards(['"rk"', '"cv"'], color=GOLD, size=FS_HEAD, w=1.4).next_to(gloss, DOWN, buff=0.75)
        spend.match_x(tach)
        sa = label("spend action", size=FS_BODY, color=GOLD).next_to(spend, UP, buff=0.15)
        self.pad_to(A("spend actions and output") - 0.2)
        self.play(TransformFromCopy(tach, spend), FadeIn(sa), run_time=0.8)

        # Orchard comparison
        self.pad_to(A("orchard's action|orchards action") - 0.3)
        orch = field_cards(['"cv"', '"rt"', '"nf"', '"rk"', '"cm"_x', '"epk"', 'dots'], color=TXT, size=FS_LABEL)
        orch.move_to(LEFT * 3.6 + UP * 0.8)
        ol = label("Orchard action", size=FS_BODY, color=TXT).next_to(orch, UP, buff=0.2)
        self.play(FadeIn(orch), FadeIn(ol), run_time=0.7)
        self.pad_to(A("the nullifier") - 0.1)
        self.play(orch[2].animate.set_color(FLARE), run_time=0.4)
        self.pad_to(A("note commitment") - 0.1)
        self.play(orch[4].animate.set_color(FLARE), run_time=0.4)
        self.pad_to(A("pulls both") - 0.2)
        self.play(orch[2].animate.shift(DOWN * 1.1), orch[4].animate.shift(DOWN * 1.1), run_time=0.7)
        # pause: what is left of Orchard's card morphs into Tachyon's (rk, cv)
        orch_t = field_cards(['"rk"', '"cv"'], color=GOLD, size=FS_HEAD, w=1.4).move_to(orch.get_center() + UP * 0.0)
        orch_t.match_y(VGroup(orch[0], orch[1]))
        self.pad_to(WEND(SID, "both of them out"))
        self.play(FadeOut(VGroup(orch[1], orch[5], orch[6])),
                  ReplacementTransform(orch[3], orch_t[0]), ReplacementTransform(orch[0], orch_t[1]),
                  run_time=0.9)
        wobble = label("not fixed: evolves per epoch", size=FS_LABEL, color=FLARE)
        wobble.next_to(VGroup(orch[2], orch[4]), DOWN, buff=0.3)
        self.pad_to(A("won't stay|wont stay") - 0.2)
        self.play(FadeIn(wobble), WiggleOutThenIn(orch[2]), run_time=0.9)

        # binding via the randomizer
        self.pad_to(A("instead") - 0.2)
        self.play(FadeOut(VGroup(orch_t, orch[2], orch[4], ol, wobble)),
                  VGroup(oa, tach, gloss, sa, spend).animate.shift(LEFT * 5.0), run_time=0.9)
        al = mtex('alpha = "PRF"("cm" || theta)', size=FS_HEAD, color=GOLD).move_to(RIGHT * 2.6 + UP * 1.2)
        self.pad_to(A("alpha is") - 0.2)
        self.play(Write(al), run_time=1.0)
        out_rk = mtex('"output:" quad "rk" = [alpha] thin G', size=FS_BODY, color=STAR)
        sp_rk = mtex('"spend:" quad "rk" = "ak" + [alpha] thin G', size=FS_BODY, color=STAR)
        VGroup(out_rk, sp_rk).arrange(DOWN, buff=0.35, aligned_edge=LEFT).next_to(al, DOWN, buff=0.5)
        self.pad_to(A("for an output") - 0.2)
        self.play(FadeIn(out_rk, shift=UP * 0.1), run_time=0.6)
        self.pad_to(A("for a spend") - 0.2)
        self.play(FadeIn(sp_rk, shift=UP * 0.1), run_time=0.6)

        # side effect: hot device signs outputs
        self.pad_to(A("side effect") - 0.2)
        sk = rich([("output signing key:", TXT), ("$alpha$", GOLD)], size=FS_BODY).next_to(sp_rk, DOWN, buff=0.55)
        sk.align_to(sp_rk, LEFT)
        self.play(FadeIn(sk), run_time=0.6)
        self.pad_to(A("spend authority") - 0.2)
        na = label("no spend authority needed", size=FS_LABEL, color=MUT).next_to(sk, DOWN, buff=0.2).align_to(sk, LEFT)
        self.play(FadeIn(na), run_time=0.5)
        self.pad_to(A("hot device") - 0.2)
        hot = label("hot device signs, no custody round trip", size=FS_LABEL, color=GOLD).next_to(na, DOWN, buff=0.2)
        hot.align_to(sk, LEFT)
        self.play(FadeIn(hot, shift=RIGHT * 0.1), run_time=0.5)
        self.pad_to(A("uniformly random") - 0.2)
        uni = label("both rk: uniform points, indistinguishable", size=FS_LABEL, color=STAR)
        uni.next_to(hot, DOWN, buff=0.2).align_to(sk, LEFT)
        self.play(FadeIn(uni), Indicate(VGroup(tach[0], spend[0]), color=GOLD), run_time=0.7)

        # --- what an output proves -------------------------------------------------------------
        self.pad_to(A("what does an output") - 0.2)
        self.play(FadeOut(VGroup(al, out_rk, sp_rk, sk, na, hot, uni, sa, spend, gloss)),
                  VGroup(oa, tach).animate.move_to(LEFT * 4.3 + UP * 0.9), run_time=0.8)
        stmt = bullets([mtex('"cv" = [-v] thin G + ["rcv"] thin H', size=FS_BODY, color=STAR),
                        mtex('0 <= v <= v_"max"', size=FS_BODY, color=STAR),
                        mtex('"cm" = "Com"("pk", v, psi; "rcm")', size=FS_BODY, color=STAR),
                        mtex('"rk" = [alpha] thin G, quad alpha = "PRF"("cm" || theta)', size=FS_BODY, color=STAR),
                        mtex('"cm" eq.not 0, quad "tg"_bot eq.not 0', size=FS_BODY, color=STAR)],
                       mark_color=GOLD, buff=0.3)
        stmt.move_to(RIGHT * 1.6 + DOWN * 0.1)
        sh = label("the output proves", size=FS_BODY, color=MUT).next_to(stmt, UP, buff=0.35).align_to(stmt, LEFT)
        self.play(FadeIn(sh), run_time=0.4)
        for i, cue in enumerate(["hides minus", "in range", "opens to this", "bound to", "no published"]):
            self.pad_to(A(cue) - 0.2)
            self.play(FadeIn(stmt[i], shift=RIGHT * 0.2), run_time=0.45)
        miss = VGroup(pill('"anchor"', color=MUT, math=True), pill("e", color=MUT, math=True)).arrange(RIGHT, buff=0.4)
        miss.next_to(tach, DOWN, buff=0.7)
        self.pad_to(A("no anchor") - 0.2)
        self.play(FadeIn(miss[0]), run_time=0.4)
        self.pad_to(A("no epoch") - 0.1)
        self.play(FadeIn(miss[1]), run_time=0.4)
        self.play(ShowCreation(strike(miss[0])), ShowCreation(strike(miss[1])), run_time=0.5)
        hist = label("history can't affect an output", size=FS_LABEL, color=MUT).next_to(miss, DOWN, buff=0.25)
        self.play(FadeIn(hist), run_time=0.4)

        # --- action multiset -------------------------------------------------------------------
        self.pad_to(A("bundle's actions|bundles actions") - 0.3)
        self.play(FadeOut(Group(*[m for m in self.mobjects if m is not title])), run_time=0.6)
        acts = VGroup(*[field_cards(['"rk"_' + str(i), '"cv"_' + str(i)], color=GOLD, size=FS_LABEL, w=1.0)
                        for i in (1, 2, 3)]).arrange(DOWN, buff=0.3).move_to(LEFT * 4.5 + DOWN * 0.2)
        self.play(LaggedStart(*[FadeIn(a, shift=RIGHT * 0.2) for a in acts], lag_ratio=0.2), run_time=0.8)
        ai = mtex('a_i = "Poseidon"("rk"_i, "cv"_i)', size=FS_BODY, color=STAR).move_to(UP * 0.7 + RIGHT * 1.3)
        aacc = mtex('"acc"^"act" = "Com"(scripts(product)_i (X - a_i))', size=FS_BODY, color=CYAN).next_to(ai, DOWN, buff=0.5)
        self.pad_to(A("hashed") - 0.3)
        self.play(TransformFromCopy(acts, ai), run_time=1.0)
        self.pad_to(A("accumulated") - 0.2)
        self.play(FadeIn(aacc, shift=UP * 0.1), run_time=0.7)
        self.pad_to(A("action accumulator") - 0.2)
        self.play(Indicate(aacc, color=CYAN), run_time=0.7)

        # --- the stamp ---------------------------------------------------------------------------
        self.pad_to(A("next up") - 0.2)
        self.play(FadeOut(VGroup(acts, ai)), aacc.animate.scale(0.85).to_edge(LEFT, buff=0.6).shift(UP * 1.4 + LEFT * 0.0),
                  run_time=0.8)
        st = stamp_card(n_slots=2, w=4.4).scale(1.15).move_to(RIGHT * 1.6 + DOWN * 0.1)
        self.pad_to(A("the stamp") - 0.1)
        self.play(FadeIn(st.frame), Write(st.title), run_time=0.8)
        pcd = label("the bundle's PCD proof", size=FS_LABEL, color=MUT).next_to(st, UP, buff=0.25)
        self.pad_to(A("proof carrying") - 0.4)
        ptok = proof_token(0.16).next_to(st.title, RIGHT, buff=0.3)
        self.play(FadeIn(pcd), FadeIn(ptok), run_time=0.6)
        self.pad_to(A("public inputs") - 0.2)
        self.play(FadeIn(st.pis, shift=UP * 0.1), run_time=0.6)
        self.pad_to(A("publishes") - 0.2)
        self.play(FadeIn(st.slots), run_time=0.5)
        cmchip = tg_chip('"cm"', color=GOLD).move_to(LEFT * 5.6 + UP * 2.6)
        self.pad_to(A("our note's|our notes") - 0.2)
        self.play(cmchip.animate.move_to(st.slots[0]), run_time=0.9)
        self.pad_to(A("second slot") - 0.2)
        qs = mtex("?", size=FS_HEAD, color=STAR).move_to(st.slots[1])
        self.play(Indicate(st.slots[1], color=STAR, scale_factor=1.2), FadeIn(qs), run_time=0.7)

        # --- txid vs wtxid ----------------------------------------------------------------------
        self.pad_to(A("where the stamp lives") - 0.2)
        stamp_g = VGroup(st, cmchip, qs, ptok)
        self.play(FadeOut(VGroup(aacc, pcd, title)),
                  stamp_g.animate.scale(0.8).move_to(RIGHT * 4.0 + DOWN * 1.6), run_time=0.8)
        eff_h = itex("effecting data", size=FS_BODY, color=STAR)
        eff_f = VGroup(mtex('"acc"^"act"', size=FS_BODY, color=STAR), mtex('v^"bal"', size=FS_BODY, color=STAR),
                       mtex('"digest"("memo")', size=FS_BODY, color=STAR)).arrange(RIGHT, buff=0.4)
        eff = boxed(VGroup(eff_h, eff_f).arrange(DOWN, buff=0.25), color=STAR, pad=0.3)
        eff.move_to(LEFT * 3.0 + UP * 0.9)
        txid = label("txid", size=FS_HEAD, color=STAR).next_to(eff, UP, buff=0.2)
        self.pad_to(A("transaction id commits") - 0.2)
        self.play(FadeIn(eff[0]), FadeIn(txid), run_time=0.6)
        self.pad_to(A("effecting data") - 0.1)
        self.play(FadeIn(eff_h, shift=UP * 0.1), run_time=0.5)
        for i, cue in enumerate([("action accumulator", 3), ("value balance", 1), ("digest of the", 1)]):
            self.pad_to(A(*cue) - 0.15)
            self.play(FadeIn(eff_f[i], shift=UP * 0.1), run_time=0.45)
        auth_h = itex("authorization data", size=FS_BODY, color=AMBER)
        sigs = mtex('{sigma^"act"} quad sigma^"bind"', size=FS_BODY, color=AMBER)
        auth = boxed(VGroup(auth_h, sigs).arrange(DOWN, buff=0.25), color=AMBER, pad=0.3)
        auth.move_to(RIGHT * 3.4 + UP * 0.9)
        self.pad_to(A("stamp and the signatures") - 0.2)
        self.play(FadeIn(auth[0]), FadeIn(sigs), stamp_g.animate.next_to(auth, DOWN, buff=0.25), run_time=0.8)
        self.pad_to(A("authorization data") - 0.1)
        self.play(FadeIn(auth_h, shift=UP * 0.1), run_time=0.5)
        mal = label("malleable by design", size=FS_LABEL, color=AMBER).next_to(auth, UP, buff=0.2)
        self.pad_to(A("malleable") - 0.2)
        self.play(FadeIn(mal), run_time=0.4)
        # a user updates the stamp
        self.pad_to(A("update a stamp") - 0.2)
        st2 = stamp_card(n_slots=2, w=4.4, color=AMBER).scale(1.15 * 0.8).move_to(stamp_g)
        st2c = tg_chip('"cm"', color=GOLD).scale(0.8).move_to(st2.slots[0])
        self.play(FadeOut(stamp_g, shift=RIGHT * 0.6), FadeIn(VGroup(st2, st2c), shift=RIGHT * 0.6), run_time=0.8)
        wt = mtex('"wtxid" = "txid" || "auth_digest"', size=FS_BODY, color=STAR).move_to(DOWN * 2.6 + LEFT * 1.6)
        self.pad_to(A("witness transaction") - 0.3)
        self.play(FadeIn(wt), run_time=0.5)
        chg = label("changes", size=FS_LABEL, color=AMBER).next_to(wt, RIGHT, buff=0.3)
        self.play(FadeIn(chg), Indicate(wt, color=AMBER), run_time=0.6)
        self.pad_to(A("but not") - 0.1)
        ok = label("txid unchanged", size=FS_LABEL, color=STAR).next_to(txid, RIGHT, buff=0.4)
        self.play(FadeIn(ok), Indicate(txid, color=STAR), run_time=0.6)
        self.pad_to(A("memo is safe") - 0.2)
        self.play(Indicate(eff_f[2], color=GOLD), run_time=0.8)
        sig_arrow = tarrow(sigs.get_left() + LEFT * 0.3, eff.get_right(), color=GOLD, width=SW)
        cov = rich([("every signature covers", GOLD), ('$"digest"("memo")$', GOLD), ("via the sighash", GOLD)],
                   size=FS_LABEL)
        cov.next_to(eff, DOWN, buff=0.35).align_to(eff, LEFT)
        self.pad_to(A("every signature") - 0.2)
        self.play(ShowCreation(sig_arrow), FadeIn(cov), run_time=0.9)
        self.pad_to(scene_T(SID))


class Scene23(TimedScene):
    def construct(self):
        SID = "2.3"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731

        title = scene_title("The anchor chain")
        self.wait(0.3)
        self.play(Write(title), run_time=1.0)

        # --- a hash chain ticking per stamp: 4 anchors, 3 unhurried absorptions ----------------------
        nodes = VGroup(*[Circle(radius=0.3).set_stroke(STAR, SW).set_fill(STAR, 0.08) for _ in range(4)])
        nodes.arrange(RIGHT, buff=2.4).move_to(UP * 0.6)
        links = VGroup(*[Arrow(a.get_right(), b.get_left(), buff=0.08, thickness=2.0, fill_color=MUT)
                         for a, b in zip(nodes[:-1], nodes[1:])])
        names = VGroup(*[mtex(f'"anchor"_{k}', size=FS_LABEL, color=STAR).next_to(n, DOWN, buff=0.22)
                         for k, n in enumerate(nodes)])
        self.pad_to(A("hash chain") - 0.3)
        self.play(FadeIn(nodes[0]), FadeIn(names[0]), run_time=0.6)
        hdr = label("carried in every block header", size=FS_LABEL, color=MUT).next_to(nodes, UP, buff=1.25)
        self.pad_to(A("block header") - 0.2)
        self.play(FadeIn(hdr), run_time=0.5)
        chips = VGroup()
        for i in range(3):
            c = VGroup(tg_chip('"acc"^"tg"', color=CYAN, size=FS_LABEL),
                       tex_chip("i", color=STAR, size=FS_LABEL, pad=0.12)).arrange(RIGHT, buff=0.15)
            c.move_to(links[i].get_center() + UP * 0.75)
            chips.add(c)

        def tick(i, rt):
            self.play(chips[i].animate.scale(0.35).move_to(links[i].get_center()).set_opacity(0),
                      GrowArrow(links[i]), run_time=0.6 * rt)
            self.play(FadeIn(nodes[i + 1], scale=0.6), FadeIn(names[i + 1]),
                      Flash(nodes[i + 1].get_center(), color=CYAN, flash_radius=0.45), run_time=0.4 * rt)

        # one tick per stamp
        self.pad_to(A("ticks") - 0.2)
        self.play(FadeIn(chips[0], shift=DOWN * 0.25), run_time=0.4)
        tick(0, 1.3)
        # the tick absorbs acc^tg, then the epoch number
        self.pad_to(A("tachygram accumulator") - 0.2)
        self.play(FadeIn(chips[1][0], shift=DOWN * 0.25), run_time=0.4)
        self.pad_to(A("current epoch") - 0.1)
        self.play(FadeIn(chips[1][1], shift=DOWN * 0.25), run_time=0.4)
        tick(1, 1.0)
        rule = mtex('"anchor" <- H("anchor"_"old" || i || "acc"^"tg")', size=FS_HEAD, color=STAR).move_to(DOWN * 1.4)
        self.pad_to(A("new anchor is") - 0.2)
        self.play(Write(rule), run_time=1.2)
        self.pad_to(A("the accumulator") - 0.1)
        self.play(FadeIn(chips[2], shift=DOWN * 0.25), run_time=0.4)
        # pause: the next bead absorbs its accumulator chip
        self.pad_to(WEND(SID, "the accumulator"))
        tick(2, 1.0)
        gran = label("finer than a block, coarser than a transaction", size=FS_BODY, color=MUT)
        gran.next_to(rule, DOWN, buff=0.4)
        self.pad_to(A("granularity") - 0.2)
        self.play(FadeIn(gran), run_time=0.6)

        # --- sentinels ---------------------------------------------------------------------------
        self.pad_to(A("every transition") - 0.3)
        self.play(FadeOut(VGroup(rule, gran, hdr, chips)), VGroup(nodes, links, names).animate.shift(LEFT * 1.5),
                  run_time=0.8)
        gate = sentinel_gate(h=1.4, color=STAR).move_to(nodes[-1].get_center() + RIGHT * 1.1)
        sn = Circle(radius=0.26).set_stroke(STAR, SW_BOLD).set_fill(STAR, 0.35).move_to(nodes[-1].get_center() + RIGHT * 2.3)
        sl = Arrow(nodes[-1].get_right(), sn.get_left(), buff=0.08, thickness=2.0, fill_color=STAR)
        sname = mtex('"sntl"_i', size=FS_LABEL, color=STAR).next_to(sn, DOWN, buff=0.22)
        self.pad_to(A("a sentinel") - 0.3)
        self.play(GrowFromCenter(gate), GrowArrow(sl), FadeIn(sn), FadeIn(sname), run_time=0.8)
        srule = mtex('"sntl"_i = H^"epoch" ("anchor"_(i-1, "end") || i)', size=FS_HEAD, color=STAR).move_to(DOWN * 1.4)
        self.pad_to(A("domain separated") - 0.2)
        self.play(Write(srule), run_time=1.2)
        self.pad_to(A("even one with") - 0.3)
        rail = EpochRail(first=4, last=10)
        empty = label("an empty epoch still has two posts", size=FS_LABEL, color=MUT).next_to(srule, DOWN, buff=0.35)
        self.play(FadeIn(rail), FadeIn(empty), run_time=0.6)
        self.play(Indicate(VGroup(rail.gate(7), rail.gate(8)), color=STAR, scale_factor=1.5), run_time=0.6)
        self.pad_to(A("exactly one") - 0.3)
        segs = VGroup(*[Line(rail.gate(e).get_center(), rail.gate(e + 1).get_center(),
                             stroke_color=[GOLD, CYAN, AMBER][e % 3], stroke_width=SW_BOLD, stroke_opacity=0.8)
                        for e in range(4, 11)])
        self.play(LaggedStart(*[ShowCreation(s) for s in segs], lag_ratio=0.1), run_time=1.0)

        # --- our note's stamp lands in epoch 5 -------------------------------------------------------
        self.pad_to(A("our note's stamp") - 0.5)
        self.play(FadeOut(VGroup(nodes, links, names, gate, sn, sl, sname, srule, empty, segs)), run_time=0.6)
        st = stamp_card(n_slots=2, w=3.4).scale(0.85).move_to(UP * 1.0)
        cmc = tg_chip('"cm"', color=GOLD, size=FS_LABEL).scale(0.85).move_to(st.slots[0])
        self.play(FadeIn(VGroup(st, cmc)), run_time=0.4)
        self.pad_to(A("landing") - 0.1)
        self.play(VGroup(st, cmc).animate.move_to(rail.center_of(5) + UP * 1.3), run_time=0.9)
        self.pad_to(A("epoch five") - 0.1)
        self.play(Indicate(rail.label_of(5), color=GOLD), run_time=0.5)
        # pause: our bead lands in epoch five
        b5 = bead(GOLD, r=0.13).move_to(rail.center_of(5))
        tag5 = label("our stamp", size=FS_SMALL, color=GOLD).next_to(b5, UP, buff=0.3)
        self.pad_to(WEND(SID, "epoch five"))
        self.play(VGroup(st, cmc).animate.scale(0.18).move_to(rail.center_of(5)).set_opacity(0), FadeIn(b5, scale=0.3),
                  run_time=0.6)
        self.play(FadeIn(tag5), Flash(b5.get_center(), color=GOLD), run_time=0.5)

        # --- why per stamp ---------------------------------------------------------------------------
        self.pad_to(A("why we anchor") - 0.2)
        q = label("why per stamp, not per block?", size=FS_HEAD, color=STAR).move_to(UP * 2.0)
        self.play(FadeIn(q), run_time=0.6)
        L = VGroup(label("per stamp", size=FS_BODY, color=GOLD, weight="BOLD"),
                   rich([('$"acc"^"tg"$', CYAN), ("already checked", TXT)], size=FS_LABEL),
                   label("validator just hashes it in", size=FS_LABEL, color=TXT)).arrange(DOWN, buff=0.25)
        R = VGroup(label("per block", size=FS_BODY, color=FLARE, weight="BOLD"),
                   label("re-accumulate every tachygram", size=FS_LABEL, color=TXT),
                   label("interpolate the product", size=FS_LABEL, color=TXT),
                   label("commit to it: an MSM", size=FS_LABEL, color=FLARE)).arrange(DOWN, buff=0.25)
        L.move_to(LEFT * 3.4 + DOWN * 0.2)
        R.move_to(RIGHT * 3.4 + DOWN * 0.4)
        self.pad_to(A("validator work") - 0.2)
        self.play(FadeIn(L[0]), run_time=0.4)
        self.pad_to(A("checked cheaply") - 0.3)
        self.play(FadeIn(L[1]), run_time=0.4)
        self.pad_to(A("just hashes") - 0.3)
        self.play(FadeIn(L[2]), run_time=0.4)
        self.pad_to(A("per block anchor") - 0.2)
        self.play(FadeIn(R[0]), run_time=0.4)
        for i, cue in enumerate(["re accumulating", "interpolating", "committing"]):
            self.pad_to(A(cue) - 0.2)
            self.play(FadeIn(R[i + 1], shift=RIGHT * 0.1), run_time=0.4)
        self.pad_to(A("multi") - 0.2)
        self.play(Indicate(R[3], color=FLARE, scale_factor=1.08), run_time=0.8)
        crit = label("on the critical path of block validation", size=FS_BODY, color=FLARE).move_to(DOWN * 1.95)
        self.pad_to(A("critical path") - 0.2)
        self.play(FadeIn(crit, shift=UP * 0.1), run_time=0.7)
        self.pad_to(scene_T(SID))

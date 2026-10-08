"""Chapter 4 — Exclusion at scale: quadratic residue filters (scenes 4.1–4.5)."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style import *  # noqa: E402,F403


# ---- local helpers ---------------------------------------------------------------
def env(tex, color=CYAN, w=1.5, h=1.0, size=FS_LABEL):
    """Committed polynomial as a sealed envelope, label always >= FS_LABEL."""
    body = RoundedRectangle(width=w, height=h, corner_radius=0.05)
    body.set_fill(color, 0.10).set_stroke(color, SW, 0.95)
    apex = body.get_center() + DOWN * 0.05 * h
    flap = VGroup(Line(body.get_corner(UL), apex), Line(body.get_corner(UR), apex))
    flap.set_stroke(color, SW_THIN, 0.8)
    tag = mtex(tex, size=size, color=color)
    tag.move_to(body.get_bottom() + UP * (tag.get_height() / 2 + 0.1))
    g = VGroup(body, flap, tag)
    g.body, g.tag = body, tag
    return g


def bucket(w=1.2, h=0.8, color=STAR, fill=0.06, tex=None, size=FS_LABEL):
    """A bounded bucket of tachygrams (open-top tray)."""
    box = RoundedRectangle(width=w, height=h, corner_radius=0.08)
    box.set_fill(color, fill).set_stroke(color, SW, 0.9)
    g = VGroup(box)
    g.box = box
    if tex is not None:
        t = mtex(tex, size=size, color=color).move_to(box)
        g.add(t)
        g.tag = t
    return g


def lamp(i, tex, color=GOLD, size=FS_LABEL):
    """A numbered check-lamp: circle with digit + identity on its right."""
    c = Circle(radius=0.22).set_stroke(color, SW, 0.9).set_fill(color, 0.0)
    n = mtex(str(i), size=FS_SMALL, color=color).move_to(c)
    t = mtex(tex, size=size, color=TXT).next_to(c, RIGHT, buff=0.3)
    g = VGroup(c, n, t)
    g.circle, g.num, g.text = c, n, t
    return g


def lit(l, color=GOLD):
    return AnimationGroup(l.circle.animate.set_fill(color, 0.85), l.num.animate.set_color(VOID),
                          l.text.animate.set_color(STAR))


def digits_seq(values, size, color):
    return [mtex(v, size=size, color=color) for v in values]


def counter_anim(holder, digits, pos, aligned=ORIGIN, rate=rush_from):
    def tick(m, a):
        k = min(int(rate(a) * (len(digits) - 1) + 0.5), len(digits) - 1)
        m.become(digits[k].copy().move_to(pos, aligned_edge=aligned))
    return UpdateFromAlphaFunc(holder, tick)


def word_at(sid, phrase, occ=1):
    """Start time of the LAST word of the occ-th match of `phrase` (e.g. "are one" -> "one")."""
    import style as _st
    seq = _st._seq(sid)
    target = [_st._norm(x) for x in re.split(r"[\s\-]+", phrase) if _st._norm(x)]
    hits = 0
    for i in range(len(seq) - len(target) + 1):
        if [w for _, w in seq[i:i + len(target)]] == target:
            hits += 1
            if hits == occ:
                return seq[i + len(target) - 1][0]
    raise ValueError(f"anchor not found in {sid}: {phrase!r}")


def word_end(sid, phrase, occ=1):
    """End time of the last word of `phrase`: where a held pause's silence begins."""
    import style as _st
    t = word_at(sid, phrase, occ)
    for x in _st.WORDS[sid]:
        if abs(x["s"] - t) < 1e-6:
            return x["e"]
    return t


def mini_ragu():
    """Small Ragu glyph showing only its query port (cyan), for 'served by Ragu's query part'."""
    body = RoundedRectangle(width=1.7, height=0.9, corner_radius=0.12)
    body.set_fill("#0b0b10", 1.0).set_stroke(MUT, SW, 0.9)
    name = label("Ragu", size=FS_BODY, color=STAR).move_to(body)
    port = Dot(body.get_left(), radius=0.09).set_fill(CYAN, 1)
    q = label("query", size=FS_LABEL, color=CYAN).next_to(body, DOWN, buff=0.12)
    g = VGroup(body, name, port, q)
    g.port = port
    return g


def docked_note():
    """Alex (2026-10-04): no docked note card in chapters 2-4. Kept as an empty
    placeholder so scene code that adds/keeps `note` stays unchanged."""
    return VGroup()


# =================================================================================
class Scene41(TimedScene):
    """The epoch accumulator, and the wall."""

    def construct(self):
        SID = "4.1"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731

        note = docked_note()
        rail = EpochRail(first=4, last=10)
        self.add(note, rail)
        self.wait(0.3)

        # nf_6 in epoch 6?
        hl = Rectangle(width=rail.seg, height=0.55).move_to(rail.center_of(6))
        hl.set_fill(CYAN, 0.18).set_stroke(CYAN, SW_THIN, 0.8)
        nf6 = tg_chip('"nf"_6', color=GOLD).move_to(rail.center_of(6, dy=1.0))
        q = rich([('$"nf"_6 in.not$', STAR), ("epoch 6", CYAN), ("?", STAR)], size=FS_HEAD)
        q.move_to(UP * TITLE_Y)
        self.play(FadeIn(hl), FadeIn(nf6, shift=0.2 * DOWN), run_time=0.8)
        self.pad_to(A("never appeared") - 0.3)
        self.play(FadeIn(q, lag_ratio=0.2), run_time=1.0)

        # naive: test against every stamp's accumulator
        self.pad_to(A("naive") - 0.2)
        m = 6
        envs = VGroup(*[env(f'f_{i + 1}', color=STAR, w=1.35, h=0.9) for i in range(m)])
        envs.arrange(RIGHT, buff=0.35).move_to(UP * 1.2)
        beads = VGroup(*[bead(STAR, r=0.07).move_to(
            rail.center_of(6) + RIGHT * (-0.42 + 0.17 * i)) for i in range(m)])
        self.play(LaggedStart(*[FadeIn(b, scale=0.4) for b in beads], lag_ratio=0.1),
                  LaggedStart(*[FadeIn(e, shift=0.2 * UP) for e in envs], lag_ratio=0.1),
                  nf6.animate.move_to(DOWN * 0.6), run_time=1.4)
        probes = VGroup(*[tarrow(nf6.get_top(), e.get_bottom(), color=FLARE, width=SW_THIN)
                          for e in envs])
        self.pad_to(A("every stamp's") - 0.2)
        self.play(LaggedStart(*[GrowArrow(p) if False else ShowCreation(p) for p in probes],
                              lag_ratio=0.15), run_time=1.2)
        cost1 = label("one test per stamp", size=FS_LABEL, color=FLARE).next_to(nf6, RIGHT, buff=0.4)
        self.play(FadeIn(cost1), run_time=0.5)

        # union is multiplication -> e(X)
        self.pad_to(A("union is multiplication") - 0.2)
        prod = mtex('e(X) = f_1 (X) dot f_2 (X) dots.c f_m (X)', size=FS_HEAD, color=STAR)
        prod.move_to(UP * 1.2)
        self.play(FadeOut(VGroup(probes, cost1, nf6)), run_time=0.5)
        self.pad_to(A("multiply all") - 0.1)
        self.play(ReplacementTransform(envs, prod), run_time=1.4)
        self.pad_to(A("one epoch accumulator") - 0.2)
        E = env("e(X)", color=CYAN, w=2.6, h=1.6, size=FS_HEAD).move_to(UP * 1.2 + LEFT * 3.2)
        self.play(prod.animate.scale(0.75).next_to(E, RIGHT, buff=0.6), FadeIn(E, scale=0.8),
                  run_time=1.0)
        self.pad_to(A("whose roots") - 0.1)
        roots_lab = label("roots: every tachygram of epoch 6", size=FS_LABEL, color=CYAN)
        roots_lab.next_to(E, DOWN, buff=0.3)
        self.play(FadeIn(roots_lab), run_time=0.6)

        # proven against the anchor chain with random point checks
        self.pad_to(A("proves it correct") - 0.2)
        chk = mtex('e(r) = product_i f_i (r)', size=FS_BODY, color=STAR)
        chk.next_to(prod, DOWN, buff=0.45)
        links = VGroup(*[Line(beads[i].get_center(), beads[i + 1].get_center(),
                              stroke_color=STAR, stroke_width=SW_THIN) for i in range(m - 1)])
        self.play(ShowCreation(links), run_time=0.6)
        self.pad_to(A("random point") - 0.2)
        rdot = Dot(radius=0.07).set_fill(STAR, 1).next_to(chk, LEFT, buff=0.3)
        self.play(FadeIn(chk, shift=0.1 * UP), Flash(chk.get_center(), color=STAR, flash_radius=0.8),
                  run_time=0.9)
        self.remove(rdot)

        # served by Ragu's query part (folded into the proof system's claims), not a step circuit
        self.pad_to(A("query part") - 0.4)
        rg = mini_ragu().move_to(RIGHT * 5.3 + UP * 1.2)
        qarr = tarrow(chk.get_right() + RIGHT * 0.15, rg.port.get_center() + LEFT * 0.12, color=CYAN,
                      width=SW_THIN)
        self.play(FadeIn(rg, shift=0.2 * LEFT), run_time=0.6)
        self.play(ShowCreation(qarr), Flash(rg.port.get_center(), color=CYAN, flash_radius=0.3), run_time=0.6)

        # degree as high as the PCS allows
        self.pad_to(A("as high") - 0.3)
        deg = mtex('deg e = N', size=FS_BODY, color=CYAN).next_to(chk, DOWN, buff=0.35)
        deg_note = label("bounded by the PCS, not by a step circuit", size=FS_LABEL, color=MUT)
        deg_note.next_to(deg, DOWN, buff=0.2)
        self.play(FadeIn(deg), FadeIn(deg_note), run_time=0.8)
        self.pad_to(A("paid once") - 0.2)
        once = label("linear work, paid once, shared", size=FS_LABEL, color=CYAN)
        once.next_to(roots_lab, DOWN, buff=0.25)
        self.play(FadeIn(once, shift=0.1 * UP), run_time=0.7)

        # run the numbers
        self.pad_to(A("run the numbers") - 0.2)
        stage = VGroup(prod, chk, deg, deg_note, roots_lab, once, rg, qarr)
        self.play(FadeOut(stage), E.animate.scale(0.8).move_to(LEFT * 4.6 + UP * 0.9), run_time=0.9)
        card = bullets([
            ("100 TPS, all 2-in-2-out", TXT),
            ("two-week epoch", TXT),
        ], size=FS_BODY, mark_color=CYAN).move_to(RIGHT * 1.2 + UP * 1.4)
        self.pad_to(A("modest") - 0.2)
        self.play(FadeIn(card[0], shift=0.2 * RIGHT), run_time=0.6)
        self.pad_to(A("two week") - 0.3)
        self.play(FadeIn(card[1], shift=0.2 * RIGHT), run_time=0.6)
        self.pad_to(A("four hundred and eighty") - 0.3)
        N = rich([("$N > 4.8 times 10^8$", CYAN), ("tachygrams", TXT)], size=FS_HEAD)
        N.next_to(card, DOWN, buff=0.45).align_to(card, LEFT)
        self.play(FadeIn(N, scale=1.1), run_time=0.8)
        self.pad_to(A("inner product") - 0.4)
        ipa = label("Bulletproofs-style IPA: verifier linear in the degree", size=FS_LABEL, color=MUT)
        ipa.next_to(N, DOWN, buff=0.4).align_to(card, LEFT)
        self.play(FadeIn(ipa), run_time=0.7)

        # stopwatch past 16:00
        self.pad_to(A("single verification") - 0.3)
        dial = Circle(radius=0.9).set_stroke(STAR, SW).move_to(LEFT * 4.6 + DOWN * 1.35)
        hand = Line(dial.get_center(), dial.get_center() + UP * 0.75, stroke_color=FLARE,
                    stroke_width=SW_BOLD)
        vals = [f'{m_:d}:00' for m_ in range(0, 17)]
        digs = digits_seq([f'"{v}"' for v in vals], FS_HEAD, FLARE)
        clock_txt = digs[0].copy()
        cpos = dial.get_right() + RIGHT * 1.6 + UP * 0.35
        clock_txt.move_to(cpos)
        # the degree counter (the IPA verifier's work) under the stopwatch digits
        dvals = [f"{m_} times 10^{e_}" for e_ in range(1, 9) for m_ in (1, 2, 5)
                 if (e_, m_) < (8, 5)] + ["4.8 times 10^8"]
        ddigs = digits_seq(dvals, FS_BODY, CYAN)
        deg_lab = mtex('"deg" =', size=FS_BODY, color=TXT)
        deg_lab.next_to(cpos + DOWN * 0.75, LEFT, buff=0.0).align_to(clock_txt, LEFT)
        dpos = deg_lab.get_right() + RIGHT * 0.2
        deg_txt = mtex("0", size=FS_BODY, color=CYAN).move_to(dpos, aligned_edge=LEFT)
        self.play(FadeIn(dial), FadeIn(hand), FadeIn(clock_txt), FadeIn(deg_lab), FadeIn(deg_txt),
                  run_time=0.5)
        # pause beat: the counter spins to 4.8e8 and the stopwatch passes 16:00, in the silence
        self.pad_to(word_end(SID, "sixteen minutes") - 0.1)
        tint = FullScreenRectangle().set_fill(FLARE, 0.12).set_stroke(width=0)
        self.play(Rotate(hand, -TAU * 2.6, about_point=dial.get_center()),
                  counter_anim(clock_txt, digs, cpos, rate=linear),
                  counter_anim(deg_txt, ddigs, dpos, aligned=LEFT, rate=linear),
                  FadeIn(tint, rate_func=squish_rate_func(smooth, 0.55, 1.0)), run_time=1.2)

        # the target
        self.pad_to(A("the target") - 0.5)
        self.play(FadeOut(VGroup(tint, dial, hand, clock_txt, deg_lab, deg_txt, card, N, ipa, q)),
                  E.animate.fade(0.5), run_time=0.5)
        tgt_t = scene_title("The target")
        goal = bullets([
            rich([("non-membership over a", TXT), ("whole epoch", CYAN)], size=FS_BODY),
            rich([("amortized cost", TXT), ("sublinear in N", CYAN)], size=FS_BODY),
            rich([("no huge polynomial", TXT), ("near the query", CYAN)], size=FS_BODY),
        ], mark_color=CYAN, buff=0.4).move_to(RIGHT * 1.0 + UP * 0.6)
        self.play(Write(tgt_t), run_time=0.5)
        self.pad_to(A("prove non") - 0.1)
        self.play(FadeIn(goal[0], shift=0.2 * RIGHT), run_time=0.6)
        self.pad_to(A("amortized") - 0.1)
        self.play(FadeIn(goal[1], shift=0.2 * RIGHT), run_time=0.6)
        self.pad_to(A("any huge") - 0.1)
        self.play(FadeIn(goal[2], shift=0.2 * RIGHT), Indicate(E, color=FLARE), run_time=0.8)
        self.pad_to(scene_T(SID))


# =================================================================================
class Scene42(TimedScene):
    """Bucketing by an address the element computes itself; the QR detour."""

    def construct(self):
        SID = "4.2"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731

        note = docked_note()
        E = env("e(X)", color=CYAN, w=2.6, h=1.6, size=FS_HEAD).move_to(UP * 0.4)
        self.add(note, E)
        self.wait(0.3)

        # shatter into buckets
        self.pad_to(A("split the epoch") - 0.2)
        rows, cols = 3, 6
        buckets = VGroup(*[bucket(1.15, 0.7, color=CYAN, fill=0.05) for _ in range(rows * cols)])
        buckets.arrange_in_grid(rows, cols, buff=0.3).move_to(DOWN * 0.3 + RIGHT * 0.8)
        self.play(ReplacementTransform(VGroup(E), buckets, lag_ratio=0.02), run_time=1.4)
        # query computes its own address
        self.pad_to(A("value being queried") - 0.3)
        x = tg_chip("x", color=GOLD).move_to(LEFT * 5.2 + DOWN * 0.3)
        self.play(FadeIn(x, shift=0.3 * RIGHT), run_time=0.6)
        self.pad_to(A("its own bucket") - 0.3)
        bits = mtex("0 thin 1 thin 1 thin 0", size=FS_BODY, color=GOLD).next_to(x, UP, buff=0.3)
        self.play(Write(bits), run_time=0.9)
        target = buckets[1 * cols + 3]
        self.pad_to(A("exactly one") - 0.3)
        self.play(VGroup(x, bits).animate.next_to(target, UP, buff=0.12).scale(0.8),
                  *[b.animate.fade(0.6) for b in buckets if b is not target],
                  target.box.animate.set_stroke(GOLD, SW_BOLD), run_time=1.2)
        self.pad_to(A("one opening") - 0.2)
        one = rich([("one opening against", TXT), ("one small bucket", GOLD)], size=FS_BODY)
        one.move_to(DOWN * 2.6)
        self.play(FadeIn(one), run_time=0.7)
        # pause beat: the query opens its one bucket
        self.pad_to(word_end(SID, "one small bucket") + 0.02)
        hit = SurroundingRectangle(target, buff=0.08).set_stroke(GOLD, SW_BOLD)
        self.play(ShowCreationThenFadeOut(hit), Flash(target.get_center(), color=GOLD, flash_radius=0.7),
                  target.box.animate(rate_func=there_and_back).set_fill(GOLD, 0.35), run_time=1.0)

        # requirements
        self.pad_to(A("so we need"))
        self.play(FadeOut(VGroup(one, x, bits)), buckets.animate.scale(0.6).to_edge(LEFT, buff=0.5),
                  run_time=0.8)
        req = bullets(["computed from the element itself", "splits any set evenly",
                       "cheap to prove in a circuit"], mark_color=CYAN, buff=0.4)
        req.move_to(RIGHT * 2.2 + UP * 0.3)
        self.pad_to(A("computes from itself") - 0.3)
        self.play(FadeIn(req[0], shift=0.2 * RIGHT), run_time=0.5)
        self.pad_to(A("splits sets") - 0.2)
        self.play(FadeIn(req[1], shift=0.2 * RIGHT), run_time=0.5)
        self.pad_to(A("cheap to prove") - 0.2)
        self.play(FadeIn(req[2], shift=0.2 * RIGHT), run_time=0.5)
        self.pad_to(A("quadratic residues") - 0.2)
        nt = rich([("exactly that:", TXT), ("quadratic residues", CYAN)], size=FS_BODY).next_to(req, DOWN, buff=0.5)
        self.play(FadeIn(nt, shift=0.1 * UP), run_time=0.7)

        # the F_13 clock
        self.pad_to(A("in a prime") - 0.1)
        self.play(FadeOut(VGroup(buckets, req, nt)), run_time=0.5)
        clock = F13Clock(radius=1.95, center=LEFT * 3.4 + DOWN * 0.15, show_zero=True)
        ftitle = mtex("FF_13", size=FS_HEAD, color=STAR).move_to(clock.c + RIGHT * 2.9 + UP * 1.9)
        self.play(FadeIn(clock, lag_ratio=0.05), FadeIn(ftitle), run_time=0.6)
        self.pad_to(A("set zero aside") - 0.1)
        self.play(clock.zero.animate.fade(0.8).shift(DOWN * 0.1), run_time=0.6)
        cols_ = clock.qr_colors(0)
        self.pad_to(A("are squares") - 0.1)
        qr_l = label("squares: quadratic residues", size=FS_LABEL, color=CYAN)
        nqr_l = label("non-squares", size=FS_LABEL, color=AMBER)
        legend = VGroup(qr_l, nqr_l).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        legend.move_to([clock.c[0], -3.0, 0])
        self.play(FadeIn(qr_l), run_time=0.4)
        self.pad_to(A("half of them are not") - 0.1)
        self.play(FadeIn(nqr_l), run_time=0.5)
        # list the squares as spoken: each dot turns cyan on its word
        for k, ph in zip((1, 3, 4, 9, 10, 12),
                         ("squares are one", "three", "four", "nine", "ten", "twelve")):
            self.pad_to(word_at(SID, ph) - 0.05)
            self.play(clock.dot(k).animate(rate_func=smooth).set_fill(CYAN, 1),
                      Indicate(clock.num(k), color=CYAN, scale_factor=1.3), run_time=0.35)
        # pause beat: the rest of the ring turns amber, residues pulse
        self.pad_to(word_end(SID, "and twelve") + 0.02)
        self.play(*[d.animate.set_fill(c, 1) for d, c in cols_ if c == AMBER],
                  *[d.animate(rate_func=there_and_back).scale(1.35) for d, c in cols_ if c == CYAN],
                  run_time=0.85)

        # one constraint for QR
        self.pad_to(A("proving that x is a square") - 0.2)
        right_x = 2.6
        sq = rich([("$x in \"QR\":$", CYAN), ("hand the circuit", TXT), ("$y$", STAR)], size=FS_BODY)
        sq.move_to([right_x, 2.2, 0])
        self.play(FadeIn(sq), run_time=0.7)
        self.pad_to(A("checks that y") - 0.1)
        eq1 = mtex("y^2 = x", size=FS_HEAD, color=CYAN).next_to(sq, DOWN, buff=0.3)
        c1 = label("1 constraint", size=FS_LABEL, color=MUT).next_to(eq1, RIGHT, buff=0.4)
        self.play(Write(eq1), FadeIn(c1), run_time=0.8)

        # the flip
        self.pad_to(A("not a square") - 0.2)
        nsq = rich([("$x in.not \"QR\":$", AMBER), ("a classic flip", TXT)], size=FS_BODY)
        nsq.next_to(eq1, DOWN, buff=0.55).align_to(sq, LEFT)
        self.play(FadeIn(nsq), run_time=0.6)
        times2 = mtex("x |-> 2x", size=FS_HEAD, color=STAR).move_to(clock.c)
        self.pad_to(A("multiplying by") - 0.2)
        self.play(FadeIn(times2), clock.zero.animate.set_opacity(0), run_time=0.5)
        self.pad_to(A("swaps the two") - 0.3)
        sw = mtex('"non-square" times x : "QR" <-> "NQR"', size=FS_LABEL, color=TXT)
        sw.next_to(nsq, DOWN, buff=0.3).align_to(sq, LEFT)
        self.play(FadeIn(sw), run_time=0.6)
        # every dot's color travels to position 2k
        movers = VGroup()
        anims = []
        for d, c in cols_:
            k = list(clock.dots).index(d) + 1
            m_ = Dot(d.get_center(), radius=0.13).set_fill(c, 1)
            movers.add(m_)
            tgt = clock.dot((2 * k) % 13).get_center()
            anims.append(m_.animate(path_arc=-PI / 3).move_to(tgt))
        # pause beat: multiplying by two swaps the colors (in the silence after "classes")
        self.pad_to(word_end(SID, "two classes") + 0.02)
        self.add(movers)
        self.play(*anims, run_time=1.1)
        self.pad_to(A("fixed public") - 0.1)
        # back to the canonical coloring
        self.play(FadeOut(movers), FadeOut(times2), run_time=0.6)
        eq2 = mtex("y^2 = c dot x", size=FS_HEAD, color=AMBER).next_to(sw, DOWN, buff=0.35)
        eq2.align_to(sq, LEFT)
        cnote = rich([("$c$", AMBER), ("public non-residue (here", TXT), ("$c = 2$", AMBER), (")", TXT)],
                     size=FS_LABEL).next_to(eq2, DOWN, buff=0.2).align_to(sq, LEFT)
        self.pad_to(A("y squared equals c") - 0.2)
        self.play(Write(eq2), FadeIn(cnote), run_time=0.9)
        self.pad_to(A("again that's one constraint") - 0.1)
        c2 = label("1 constraint", size=FS_LABEL, color=MUT).next_to(eq2, RIGHT, buff=0.4)
        self.play(FadeIn(c2), run_time=0.4)

        # offset R: discriminant
        self.pad_to(A("shift everything") - 0.2)
        rhs = VGroup(sq, eq1, c1, nsq, sw, eq2, cnote, c2)
        self.play(FadeOut(rhs), run_time=0.6)
        shift_l = mtex('"is" x + R "a square?"', size=FS_HEAD, color=STAR).move_to([right_x, 2.3, 0])
        self.play(FadeIn(shift_l), run_time=0.6)
        R = 1
        cols1 = clock.qr_colors(R)
        Rlab = mtex("R = 1", size=FS_BODY, color=STAR).move_to(clock.c)
        self.pad_to(A("qr discriminant") - 0.1)
        disc = label("a QR discriminant", size=FS_BODY, color=CYAN).next_to(shift_l, DOWN, buff=0.3)
        self.play(FadeIn(disc, shift=0.1 * UP), run_time=0.6)
        # pause beat: sliding R recolors the ring
        self.pad_to(word_end(SID, "qr discriminant") + 0.02)
        self.play(*[d.animate.set_fill(c if c != STAR else CYAN, 1) for d, c in cols1],
                  FadeIn(Rlab, shift=0.15 * RIGHT), run_time=1.0)
        self.pad_to(A("roughly in half") - 0.3)
        half = label("cuts any fixed set roughly in half", size=FS_LABEL, color=TXT)
        half.next_to(disc, DOWN, buff=0.25)
        self.play(FadeIn(half), run_time=0.6)

        # k-bit profile for x = 3
        self.pad_to(A("with k") - 0.2)
        prof_rows = VGroup()
        for j, Rj in enumerate((0, 1, 2)):
            v = (3 + Rj) % 13
            bit = "1" if (v == 0 or v in QR13) else "0"
            col = CYAN if bit == "1" else AMBER
            r_ = rich([(f"$R_{j} = {Rj}:$", TXT), (f"$3 + {Rj} = {v}$", TXT), (f"$-> {bit}$", col)],
                      size=FS_BODY)
            prof_rows.add(r_)
        prof_rows.arrange(DOWN, aligned_edge=LEFT, buff=0.22).next_to(half, DOWN, buff=0.45)
        prof_rows.align_to(shift_l, LEFT)
        self.play(LaggedStart(*[FadeIn(r_, shift=0.2 * RIGHT) for r_ in prof_rows], lag_ratio=0.3),
                  Indicate(clock.dot(3), color=GOLD, scale_factor=1.8), run_time=1.4)
        self.pad_to(A("bit profile") - 0.2)
        prof = rich([("profile of 3:", TXT), ("$b = (1, 1, 0)$", GOLD)], size=FS_BODY)
        prof.next_to(prof_rows, DOWN, buff=0.35).align_to(shift_l, LEFT)
        self.play(FadeIn(prof, scale=1.1), run_time=0.7)
        self.pad_to(A("two to the k") - 0.2)
        cls = mtex('2^k "classes, nearly equal size"', size=FS_LABEL, color=TXT)
        cls.next_to(prof, DOWN, buff=0.25).align_to(shift_l, LEFT)
        self.play(FadeIn(cls), run_time=0.6)

        # edge case x = -R
        self.pad_to(A("one edge case") - 0.2)
        self.play(FadeOut(VGroup(disc, half, prof_rows, prof, cls)), run_time=0.6)
        ec = mtex('x = -R = 12 => x + R = 0', size=FS_BODY, color=STAR).next_to(shift_l, DOWN, buff=0.45)
        self.pad_to(A("x equals minus") - 0.1)
        d12 = clock.dot(12)
        self.play(FadeIn(ec), d12.animate.set_fill(STAR, 1).scale(1.4), run_time=0.8)
        self.pad_to(A("neither") - 0.1)
        neither = label("neither a square nor a non-square", size=FS_LABEL, color=MUT)
        neither.next_to(ec, DOWN, buff=0.25)
        self.play(FadeIn(neither), run_time=0.5)
        self.play(*[Flash(d12.get_center(), color=STAR, flash_radius=0.35)], run_time=0.6)
        self.pad_to(A("by convention") - 0.1)
        conv = rich([("convention:", TXT), ("residue side", CYAN)], size=FS_BODY).next_to(neither, DOWN, buff=0.35)
        ring12 = Circle(radius=0.26).set_stroke(CYAN, SW_BOLD).move_to(d12)
        self.play(FadeIn(conv), ShowCreation(ring12), run_time=0.8)
        self.pad_to(A("enforced") - 0.1)
        enf = label("enforced, not just stated", size=FS_LABEL, color=GOLD).next_to(conv, DOWN, buff=0.25)
        self.play(FadeIn(enf), run_time=0.5)
        self.pad_to(A("claimed non") - 0.2)
        wit = rich([("NQR bit also needs", TXT), ("$x + R != 0$", AMBER), ("(inverse witness)", MUT)],
                   size=FS_LABEL).next_to(enf, DOWN, buff=0.35)
        self.play(FadeIn(wit, shift=0.1 * UP), run_time=0.8)
        self.pad_to(A("otherwise") - 0.1)
        bad = mtex('y^2 = c dot 0 => y = 0', size=FS_BODY, color=FLARE).next_to(wit, DOWN, buff=0.3)
        self.play(FadeIn(bad), run_time=0.6)
        self.pad_to(A("square root of zero") + 0.2)
        strike = VMobject().set_points_as_corners([bad.get_left() + LEFT * 0.08,
                                                   bad.get_right() + RIGHT * 0.08])
        strike.set_stroke(FLARE, SW)  # polyline, not a Line: an intended strike-through
        self.play(ShowCreation(strike), run_time=0.5)
        self.pad_to(scene_T(SID))


# =================================================================================
class Scene43(TimedScene):
    """The batched QR test, and one decomposition with four checks."""

    def construct(self):
        SID = "4.3"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731

        note = docked_note()
        self.add(note)
        self.wait(0.3)
        self.pad_to(A("certify a whole") - 0.3)
        title = scene_title("Certify a whole bucket at once")
        self.play(Write(title), run_time=0.9)

        # bucket accumulator over F_13: roots 3, 4, 9 (all squares)
        fl = FieldLine(width=7.4, y=-2.2).shift(LEFT * 2.7)
        xs = (3, 4, 9)
        ys = {3: 4, 4: 2, 9: 3}          # y^2 = x in F_13
        self.pad_to(A("take a bucket's") - 0.2)
        roots = VGroup(*[fl.root(x, color=CYAN, r=0.12) for x in xs])
        f_eq = mtex("f(X) = (X - 3)(X - 4)(X - 9)", size=FS_BODY, color=STAR)
        f_eq.move_to(UP * 2.2 + LEFT * 2.6)
        self.play(FadeIn(fl), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(r_, scale=0.3) for r_ in roots], lag_ratio=0.2),
                  Write(f_eq), run_time=1.2)
        self.pad_to(A("every member is a square") - 0.2)
        sqs = label("every member is a square", size=FS_LABEL, color=CYAN).next_to(f_eq, DOWN, buff=0.25)
        sqs.align_to(f_eq, LEFT)
        self.play(FadeIn(sqs), *[Flash(r_.get_center(), color=CYAN, flash_radius=0.3) for r_ in roots],
                  run_time=0.8)
        self.pad_to(A("refuses duplicates") - 0.3)
        dist = label("no duplicates: distinct roots", size=FS_LABEL, color=MUT).next_to(sqs, DOWN, buff=0.2)
        dist.align_to(f_eq, LEFT)
        self.play(FadeIn(dist), run_time=0.6)

        # interpolate g through (x_i, y_i)
        k = 0.38
        pts = {x: fl.n2p(x) + UP * (k * ys[x] + 0.3) for x in xs}
        self.pad_to(A("interpolate") - 0.2)
        dots = VGroup(*[Dot(pts[x], radius=0.09).set_fill(STAR, 1) for x in xs])
        stems = VGroup(*[DashedLine(fl.n2p(x), pts[x], dash_length=0.06).set_stroke(MUT, SW_THIN) for x in xs])
        tags = VGroup(*[mtex(f"({x}, {ys[x]})", size=FS_SMALL, color=STAR).next_to(pts[x], UP, buff=0.15)
                        for x in xs])
        self.play(ShowCreation(stems), FadeIn(dots, scale=0.3), run_time=0.8)
        self.pad_to(A("through the points") - 0.1)
        curve = VMobject().set_points_smoothly([
            fl.n2p(1.6) + UP * (k * 5.2 + 0.3), pts[3], pts[4], fl.n2p(6.5) + UP * (k * 1.6 + 0.3),
            pts[9], fl.n2p(10.6) + UP * (k * 4.0 + 0.3)])
        curve.set_stroke(GOLD, SW)
        g_lab = mtex("g", size=FS_BODY, color=GOLD).next_to(curve.get_end(), RIGHT, buff=0.15)
        self.play(FadeIn(tags), ShowCreation(curve), FadeIn(g_lab), run_time=1.4)
        self.pad_to(A("square root of") - 0.2)
        yy = mtex("y_i^2 = x_i", size=FS_BODY, color=STAR).next_to(dist, DOWN, buff=0.3).align_to(f_eq, LEFT)
        self.play(FadeIn(yy), run_time=0.6)

        # g^2 - X vanishes on every member -> f divides it
        rx = 2.9
        self.pad_to(A("vanishes") - 0.4)
        v1 = mtex("g(x_i)^2 - x_i = 0", size=FS_BODY, color=STAR).move_to([rx + 1.4, 2.2, 0])
        self.play(Write(v1), *[Indicate(r_, color=GOLD, scale_factor=1.6) for r_ in roots], run_time=1.0)
        self.pad_to(A("f divides") - 0.2)
        hdef = mtex("h(X) = (g(X)^2 - X) / f(X)", size=FS_BODY, color=STAR)
        hdef.next_to(v1, DOWN, buff=0.4)
        self.play(FadeIn(hdef, shift=0.1 * DOWN), run_time=0.8)
        self.pad_to(A("witness") - 0.2)
        wl = label("the quotient h is the witness", size=FS_LABEL, color=GOLD).next_to(hdef, DOWN, buff=0.2)
        self.play(FadeIn(wl), run_time=0.5)
        self.pad_to(A("prover commits") - 0.2)
        eg = env("g", color=GOLD, w=1.0, h=0.75).move_to([rx + 0.6, -0.2, 0])
        eh = env("h", color=GOLD, w=1.0, h=0.75).next_to(eg, RIGHT, buff=0.35)
        self.play(FadeIn(eg, shift=0.2 * DOWN), FadeIn(eh, shift=0.2 * DOWN), run_time=0.7)
        self.pad_to(A("random point") - 0.2)
        rp = fl.n2p(5)
        probe = Line(rp + UP * 2.4, rp, stroke_color=STAR, stroke_width=SW)
        rl = mtex("r = 5", size=FS_BODY, color=STAR).next_to(probe.get_top(), RIGHT, buff=0.12)
        self.play(ShowCreation(probe), FadeIn(rl), run_time=0.6)
        self.pad_to(A("and checks") - 0.2)
        lhs = mtex("g(r)^2 - r", size=FS_HEAD, color=STAR)
        eqs = mtex("=", size=FS_HEAD, color=STAR)
        rhs = mtex("f(r) dot h(r)", size=FS_HEAD, color=STAR)
        chk = VGroup(lhs, eqs, rhs).arrange(RIGHT, buff=0.2).move_to([rx + 1.0, -1.35, 0])
        self.play(Write(chk), run_time=1.2)
        # pause beat: both sides print the same element (F_13, r = 5: g(5) = 12, f(5) = 5, h(5) = 7)
        lv = mtex("12^2 - 5 = 9", size=FS_LABEL, color=GOLD).next_to(lhs, DOWN, buff=0.22)
        rv = mtex("5 dot 7 = 9", size=FS_LABEL, color=GOLD).next_to(rhs, DOWN, buff=0.22)
        rv.align_to(lv, DOWN)  # same baseline
        self.pad_to(word_end(SID, "h of r") + 0.02)
        self.play(FadeIn(lv, shift=0.15 * DOWN), FadeIn(rv, shift=0.15 * DOWN), run_time=0.6)
        self.play(Flash(lv[-1].get_center(), color=GOLD, flash_radius=0.3),
                  Flash(rv[-1].get_center(), color=GOLD, flash_radius=0.3), run_time=0.5)
        self.pad_to(A("one identity") - 0.2)
        ok = checkmark(0.4, GOLD).next_to(chk, RIGHT, buff=0.25)
        allsq = label("every root of f is a square", size=FS_LABEL, color=CYAN).next_to(VGroup(lv, rv), DOWN, buff=0.2)
        self.play(ShowCreation(ok), FadeIn(allsq), run_time=0.8)
        self.pad_to(A("non residue version") - 0.2)
        nv = mtex("g(r)^2 - c(r + R) = f(r) dot h(r)", size=FS_LABEL, color=AMBER)
        nv.next_to(allsq, DOWN, buff=0.3)
        self.play(FadeIn(nv), run_time=0.7)
        self.pad_to(A("replaces") - 0.1)
        rep = mtex("X |-> X + R", size=FS_LABEL, color=TXT).next_to(nv, DOWN, buff=0.2)
        self.play(FadeIn(rep), run_time=0.5)

        # split a bucket under R = 1
        self.pad_to(A("split a bucket") - 0.6)
        old = VGroup(fl, roots, f_eq, sqs, dist, dots, stems, tags, curve, g_lab, yy, v1, hdef, wl,
                     eg, eh, probe, rl, chk, lv, rv, ok, allsq, nv, rep)
        self.play(FadeOut(old), title.animate.become(scene_title("Split one bucket: four checks")),
                  run_time=0.6)
        members = (2, 4, 5, 7, 10, 12)
        R = 1
        fbox = bucket(4.6, 1.0, color=STAR).move_to(LEFT * 3.4 + UP * 1.6)
        flab = mtex("f", size=FS_BODY, color=STAR).next_to(fbox, LEFT, buff=0.2)
        chips = VGroup(*[tg_chip(str(x), color=STAR, size=FS_LABEL) for x in members])
        chips.arrange(RIGHT, buff=0.18).move_to(fbox)
        self.pad_to(A("under a discriminant") - 0.2)
        rlab = mtex("R = 1", size=FS_BODY, color=STAR).next_to(fbox, UP, buff=0.2)
        self.play(FadeIn(fbox), FadeIn(flab), LaggedStart(*[FadeIn(c) for c in chips], lag_ratio=0.1),
                  FadeIn(rlab), run_time=1.0)
        q0box = bucket(2.6, 1.0, color=AMBER).move_to(LEFT * 4.9 + DOWN * 0.4)
        q1box = bucket(1.6, 1.0, color=CYAN).move_to(LEFT * 1.9 + DOWN * 0.4)
        q0l = mtex("q_0", size=FS_BODY, color=AMBER).next_to(q0box, DOWN, buff=0.15)
        q1l = mtex("q_1", size=FS_BODY, color=CYAN).next_to(q1box, DOWN, buff=0.15)
        q0n = label("non-residues", size=FS_LABEL, color=AMBER).next_to(q0l, DOWN, buff=0.1)
        q1n = label("residues", size=FS_LABEL, color=CYAN).next_to(q1l, DOWN, buff=0.1)
        self.pad_to(A("two pieces") - 0.2)
        self.play(FadeIn(q0box), FadeIn(q1box), run_time=0.6)
        is_q = {x: ((x + R) % 13 == 0 or (x + R) % 13 in QR13) for x in members}
        n0 = [c for x, c in zip(members, chips) if not is_q[x]]
        n1 = [c for x, c in zip(members, chips) if is_q[x]]
        tgt0 = VGroup(*[c.copy() for c in n0]).arrange(RIGHT, buff=0.15).move_to(q0box)
        tgt1 = VGroup(*[c.copy() for c in n1]).arrange(RIGHT, buff=0.15).move_to(q1box)
        self.pad_to(A("q zero") - 0.2)
        self.play(FadeIn(q0l), FadeIn(q0n), run_time=0.5)
        self.pad_to(A("q one") - 0.2)
        self.play(FadeIn(q1l), FadeIn(q1n), run_time=0.5)
        # pause beat: the discriminant blade cleaves the bucket into amber and cyan
        self.pad_to(word_end(SID, "holds the residues") + 0.02)
        blade = Line(fbox.get_left() + LEFT * 0.35, fbox.get_right() + RIGHT * 0.35)
        blade.set_stroke(STAR, SW_BOLD, 1.0)
        self.play(LaggedStart(
            ShowCreationThenFadeOut(blade),
            AnimationGroup(*[c.animate.move_to(t).set_color(AMBER) for c, t in zip(n0, tgt0)],
                           *[c.animate.move_to(t).set_color(CYAN) for c, t in zip(n1, tgt1)]),
            lag_ratio=0.3), run_time=1.05)

        # four lamps
        L = VGroup(
            lamp(1, "f(r) = q_0 (r) dot q_1 (r)"),
            lamp(2, "g_1 (r)^2 - (r + R) = q_1 (r) dot h_1 (r)"),
            lamp(3, "g_0 (r)^2 - c(r + R) = q_0 (r) dot h_0 (r)"),
            lamp(4, "q_0 (-R) != 0"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        names = ["decomposition", "QR purity", "NQR purity", "zero convention"]
        tags_ = VGroup(*[label(n, size=FS_LABEL, color=MUT) for n in names])
        L.move_to(RIGHT * 2.9 + DOWN * 0.1)
        for t_, l_ in zip(tags_, L):
            t_.next_to(l_.circle, UP, buff=0.05).align_to(l_.text, LEFT)
        L.arrange(DOWN, aligned_edge=LEFT, buff=0.6).move_to(RIGHT * 2.9 + DOWN * 0.2)
        for t_, l_ in zip(tags_, L):
            t_.next_to(l_.text, UP, buff=0.08).align_to(l_.text, LEFT)
        self.pad_to(A("four checks") - 0.05)
        self.play(LaggedStart(*[FadeIn(l_.circle) for l_ in L], lag_ratio=0.15),
                  LaggedStart(*[FadeIn(l_.num) for l_ in L], lag_ratio=0.15), run_time=0.8)
        for i, ph in enumerate(("first is decomposition", "second", "third", "fourth")):
            self.pad_to(A(ph) - 0.2)
            self.play(FadeIn(L[i].text, shift=0.1 * RIGHT), FadeIn(tags_[i]), lit(L[i]), run_time=0.8)
        # why lamp 4
        self.pad_to(A("enforces the convention") - 0.2)
        self.play(Indicate(L[3], color=GOLD, scale_factor=1.05), run_time=0.8)
        self.pad_to(A("product of linear") - 0.3)
        q0f = mtex("q_0 (X) = (X - 4)(X - 5)(X - 7)(X - 10)", size=FS_LABEL, color=AMBER)
        q0f.move_to(LEFT * 3.4 + DOWN * 2.6)
        self.play(FadeIn(q0f), run_time=0.7)
        self.pad_to(A("isn't one of its roots") - 0.4)
        nz = mtex("-R = 12 in.not q_0", size=FS_LABEL, color=STAR).next_to(q0f, DOWN, buff=0.2)
        self.play(FadeIn(nz), run_time=0.6)
        self.pad_to(A("forced into") - 0.4)
        c12 = n1[-1]
        ring = Circle(radius=0.32).set_stroke(GOLD, SW_BOLD).move_to(c12)
        self.play(ShowCreation(ring), Indicate(c12, color=GOLD, scale_factor=1.3), run_time=0.8)
        self.pad_to(scene_T(SID))


# =================================================================================
def range_box(x0, x1, y, color, h=0.55, tex=None, size=FS_LABEL, pad=0.08):
    """A bucket drawn so its x-extent IS its anchor range."""
    b = RoundedRectangle(width=(x1 - x0) - 2 * pad, height=h, corner_radius=0.07)
    b.set_fill(color, 0.12).set_stroke(color, SW, 0.95).move_to([(x0 + x1) / 2, y, 0])
    g = VGroup(b)
    g.box = b
    g.x0, g.x1 = x0, x1
    if tex is not None:
        t = mtex(tex, size=size, color=color)
        t.move_to(b.get_left() + RIGHT * (t.get_width() / 2 + 0.25))
        g.add(t)
        g.tag = t
    return g



# ---- routing network (mechanic follows v1 act5 Scene54) -------------------------
def rbucket(w=1.3, h=0.72, color=STAR, bits="", cover=(0.0, 1.0), bits_size=FS_BODY):
    """A routing bucket: box, profile-bit tag, and an anchor-coverage mini bar.

    Children: [box, (bits), track, seg]; seg (coverage within the epoch) is [-1].
    """
    box = RoundedRectangle(width=w, height=h, corner_radius=0.1)
    box.set_fill(color, 0.10).set_stroke(color, SW_THIN, 0.95)
    g = VGroup(box)
    if bits:
        t = mtex(f'"{bits}"', size=bits_size, color=color)
        t.move_to(box.get_center() + UP * 0.08)
        g.add(t)
    yb = box.get_bottom()[1] + 0.13
    track = Line([box.get_left()[0] + 0.14, yb, 0], [box.get_right()[0] - 0.14, yb, 0],
                 stroke_width=3.5, stroke_color=DIM, stroke_opacity=0.8)
    x0, x1 = track.get_start()[0], track.get_end()[0]
    seg = Line([x0 + cover[0] * (x1 - x0), yb, 0], [x0 + cover[1] * (x1 - x0), yb, 0],
               stroke_width=4.5, stroke_color=color, stroke_opacity=1.0)
    g.add(track, seg)
    return g


def rmorph(src, dst, copy=True, bits=True):
    """Part-wise bucket morph (box, track, seg, bits) so counts never mismatch."""
    T = TransformFromCopy if copy else ReplacementTransform
    anims = [T(src[0], dst[0]), T(src[-2], dst[-2]), T(src[-1], dst[-1])]
    if len(dst) == 4 and bits:
        anims.append(FadeIn(dst[1], scale=0.8))
    return anims


def redge(a, b, color=DIM, opacity=0.7):
    return Line(a.get_bottom(), b.get_top(), buff=0.06, stroke_width=SW_THIN,
                stroke_color=color, stroke_opacity=opacity)


class Scene44(TimedScene):
    """Routing: summaries -> root buckets -> decompose/merge rounds -> jagged frontier."""

    def construct(self):
        SID = "4.4"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731

        note = docked_note()
        self.add(note)
        self.wait(0.3)
        title = scene_title("Routing a whole epoch")
        self.play(Write(title), run_time=0.8)

        # the epoch strip: sntl_6 ... sntl_7
        XL, XR, YS = -5.6, 5.6, -2.85
        strip = Line([XL, YS, 0], [XR, YS, 0], stroke_color=DIM, stroke_width=SW)
        g6 = sentinel_gate(0.6).move_to([XL, YS, 0])
        g7 = sentinel_gate(0.6).move_to([XR, YS, 0])
        s6 = mtex('"sntl"_6', size=FS_LABEL, color=STAR).next_to(g6, LEFT, buff=0.15)
        s7 = mtex('"sntl"_7', size=FS_LABEL, color=STAR).next_to(g7, RIGHT, buff=0.15)
        self.pad_to(A("streams in") - 0.4)
        self.play(ShowCreation(strip), FadeIn(g6), FadeIn(s6), run_time=0.7)
        nb = 16
        bxs = [XL + (i + 0.5) * (XR - XL) / nb for i in range(nb)]
        beads = VGroup(*[bead(STAR, r=0.08).move_to([x, YS, 0]) for x in bxs])
        self.play(LaggedStart(*[FadeIn(b, shift=0.4 * LEFT) for b in beads], lag_ratio=0.25),
                  run_time=2.0)
        self.add(g7, s7)

        # bounded summaries: 4 stamps each
        bounds = [XL, -2.8, 0.0, 2.8, XR]
        self.pad_to(A("bounded summaries") - 0.3)
        brs = VGroup(*[bracket(Line([bounds[i] + 0.1, YS, 0], [bounds[i + 1] - 0.1, YS, 0]),
                               color=MUT, buff=0.2) for i in range(4)])
        sums = VGroup(*[range_box(bounds[i], bounds[i + 1], -1.85, STAR, tex=f"p_{i + 1}") for i in range(4)])
        self.play(LaggedStart(*[ShowCreation(b) for b in brs], lag_ratio=0.2), run_time=1.0)
        self.pad_to(A("one product") - 0.2)
        self.play(LaggedStart(*[FadeIn(s, shift=0.2 * UP) for s in sums], lag_ratio=0.2), run_time=1.0)
        self.pad_to(A("anchor range") - 0.2)
        rng = label("each covers an anchor range", size=FS_LABEL, color=MUT).next_to(title, DOWN, buff=0.35)
        self.play(FadeIn(rng), run_time=0.5)
        self.pad_to(A("summary grows") - 0.2)
        grow = mtex("p'(r) = p(r) dot a_T (r)", size=FS_BODY, color=STAR).next_to(rng, DOWN, buff=0.3)
        self.play(Write(grow), run_time=0.9)
        self.pad_to(A("absorbing") - 0.2)
        absorb = label("and absorbs the stamp into its anchor", size=FS_LABEL, color=MUT)
        absorb.next_to(grow, DOWN, buff=0.2)
        self.play(FadeIn(absorb), run_time=0.6)
        self.pad_to(A("never crosses") - 0.2)
        self.play(Flash(g6[1].get_center(), color=STAR), Flash(g7[1].get_center(), color=STAR),
                  Indicate(g6, color=GOLD), Indicate(g7, color=GOLD), run_time=0.9)
        # ---- routing network: roots -> R1 split -> merge -> R2 -> partial R3 ----
        ROW = [1.75, 0.65, -0.45, -1.55]
        CAP_Y = 2.5
        RX = [(bounds[i] + bounds[i + 1]) / 2 for i in range(4)]
        QW = 0.25

        def caption_at(m):
            m.move_to([-0.7, CAP_Y, 0])
            return m

        def swap_cap(new, old=None, rt=0.6):
            caption_at(new)
            if old is None:
                self.play(FadeIn(new, shift=0.1 * UP), run_time=rt)
            else:  # staggered: a simultaneous cross-fade garbles the two strings
                self.play(AnimationGroup(FadeOut(old, shift=0.1 * DOWN), FadeIn(new, shift=0.1 * UP),
                                         lag_ratio=0.85), run_time=rt + 0.2)
            return new

        def rlab(tex, y):
            return mtex(tex, size=FS_LABEL, color=MUT).move_to([-6.35, y, 0])

        self.pad_to(A("root bucket") - 0.4)
        roots = VGroup(*[rbucket(2.3, 0.72, STAR, "", (i * QW, (i + 1) * QW)).move_to([RX[i], ROW[0], 0])
                         for i in range(4)])
        self.play(FadeOut(VGroup(rng, grow, absorb)),
                  *[ReplacementTransform(sums[i], roots[i]) for i in range(4)], run_time=1.0)
        cap = swap_cap(label("root buckets: empty profile, each a contiguous range", size=FS_LABEL, color=MUT),
                       rt=0.4)

        # one routing round: decompose ...
        self.pad_to(A("service routes") - 0.2)
        rd = pill("routing round", color=CYAN).move_to([5.25, CAP_Y, 0])
        self.play(FadeIn(rd), run_time=0.5)
        self.pad_to(A("decomposes every") - 0.2)
        kids = VGroup()
        for i in range(4):
            k0 = rbucket(1.25, 0.72, AMBER, "0", (i * QW, (i + 1) * QW)).move_to([RX[i] - 0.7, ROW[1], 0])
            k1 = rbucket(1.25, 0.72, CYAN, "1", (i * QW, (i + 1) * QW)).move_to([RX[i] + 0.7, ROW[1], 0])
            kids.add(VGroup(k0, k1))
        e_dec = VGroup(*[redge(roots[i], kids[i][j], (AMBER, CYAN)[j]) for i in range(4) for j in range(2)])
        r1 = rlab("R_1", (ROW[0] + ROW[1]) / 2)
        self.play(LaggedStart(*[AnimationGroup(ShowCreation(e_dec[2 * i]), ShowCreation(e_dec[2 * i + 1]),
                                               *rmorph(roots[i], kids[i][0]), *rmorph(roots[i], kids[i][1]))
                                for i in range(4)], lag_ratio=0.12),
                  roots.animate.fade(0.5), FadeIn(r1), run_time=1.8)
        self.pad_to(A("roughly halves") - 0.2)
        cap = swap_cap(rich([("each child: its parent's anchor range", TXT), ("+ one profile bit", GOLD)],
                            size=FS_LABEL), cap)

        # ... then merge adjacent same-profile children within capacity
        self.pad_to(A("merges neighbors") - 0.2)
        m00 = rbucket(2.0, 0.72, AMBER, "0", (0.0, 0.5))
        m01 = rbucket(2.0, 0.72, CYAN, "1", (0.0, 0.5))
        m10 = rbucket(2.0, 0.72, AMBER, "0", (0.5, 1.0))
        m11a = rbucket(1.5, 0.72, CYAN, "1", (0.5, 0.75))
        m11b = rbucket(1.5, 0.72, CYAN, "1", (0.75, 1.0))
        merged = VGroup(m00, m01, m10, m11a, m11b).arrange(RIGHT, buff=0.35).move_to([0, ROW[2], 0])
        msrc = {m00: [kids[0][0], kids[1][0]], m01: [kids[0][1], kids[1][1]],
                m10: [kids[2][0], kids[3][0]], m11a: [kids[2][1]], m11b: [kids[3][1]]}
        e_mrg = {m: VGroup(*[redge(k, m, m[0].get_stroke_color()) for k in ks]) for m, ks in msrc.items()}

        def merge_anims(ms):
            out = []
            for m in ms:
                out.append(ShowCreation(e_mrg[m]))
                for n_, k in enumerate(msrc[m]):
                    out += rmorph(k, m, bits=(n_ == 0))  # one FadeIn per label, else it ends invisible
            return out
        self.play(*merge_anims([m00, m01]), run_time=1.0)
        self.play(*merge_anims([m10, m11a, m11b]), kids.animate.fade(0.5), run_time=1.0)
        self.pad_to(A("as long as") - 0.2)
        full = label("over capacity: stays split", size=FS_LABEL, color=FLARE)
        full.next_to(VGroup(m11a, m11b), DOWN, buff=0.14)
        self.play(m11a.animate.shift(RIGHT * 0.1), m11b.animate.shift(LEFT * 0.1), run_time=0.3)
        self.play(m11a.animate.shift(LEFT * 0.1), m11b.animate.shift(RIGHT * 0.1), FadeIn(full), run_time=0.4)
        self.pad_to(A("union check") - 0.2)
        cap = swap_cap(rich([("$q_M = q_L dot q_R$", STAR), ("the union check again: no new trust", MUT)],
                            size=FS_LABEL), cap)

        def wave(lines, color=GOLD):
            return AnimationGroup(*[ShowPassingFlash(l.copy().set_stroke(color, 5, 1.0), time_width=0.6)
                                    for l in lines])
        all_mrg = [e for g_ in e_mrg.values() for e in g_]
        # pause beat: one routing round replayed: split, then merge
        self.pad_to(word_end(SID, "nothing new to trust") + 0.02)
        self.play(Succession(wave(e_dec), wave(all_mrg)), run_time=1.0)

        # ranges underneath: decomposition keeps, merge joins
        self.pad_to(A("underneath all") - 0.1)
        cap = swap_cap(label("watch the anchor-range bars", size=FS_LABEL, color=GOLD), cap)
        self.pad_to(A("decomposition keeps") - 0.2)
        self.play(LaggedStart(*[AnimationGroup(Indicate(roots[i][-1], color=GOLD, scale_factor=1.6),
                                               Indicate(kids[i][0][-1], color=GOLD, scale_factor=1.6),
                                               Indicate(kids[i][1][-1], color=GOLD, scale_factor=1.6))
                                for i in range(4)], lag_ratio=0.15), run_time=1.6)
        self.pad_to(A("joins two adjacent") - 0.2)
        self.play(Indicate(kids[0][0][-1], color=GOLD, scale_factor=1.6),
                  Indicate(kids[1][0][-1], color=GOLD, scale_factor=1.6),
                  Indicate(m00[-1], color=GOLD, scale_factor=1.6),
                  ShowPassingFlash(e_mrg[m00].copy().set_stroke(GOLD, 5, 1.0), time_width=0.6),
                  run_time=1.2)

        # round by round: R2 brings one full-epoch bucket per profile
        self.pad_to(A("round by round") - 0.2)
        finals = VGroup(*[rbucket(2.2, 0.72, c, bb, (0.0, 1.0))
                          for bb, c in [("00", AMBER), ("01", CYAN), ("10", AMBER), ("11", CYAN)]])
        finals.arrange(RIGHT, buff=0.6).move_to([0, ROW[3], 0])
        fsrc = {0: [m00, m10], 1: [m00, m10], 2: [m01, m11a, m11b], 3: [m01, m11a, m11b]}
        e_r2, e_r2_by = VGroup(), {}
        for fi, ms in fsrc.items():
            for m in ms:
                e = redge(m, finals[fi], finals[fi][0].get_stroke_color())
                e_r2.add(e)
                e_r2_by[(fi, id(m))] = e
        r2 = rlab("R_2", (ROW[2] + ROW[3]) / 2)
        self.play(FadeOut(full), LaggedStart(*[ShowCreation(e) for e in e_r2], lag_ratio=0.05),
                  LaggedStart(*[FadeIn(f, shift=0.2 * DOWN) for f in finals], lag_ratio=0.15),
                  merged.animate.fade(0.3), FadeIn(r2), run_time=1.6)
        self.pad_to(A("spans the entire") - 0.2)
        cap = swap_cap(label("one bucket per profile, each spanning the whole epoch", size=FS_LABEL,
                             color=STAR), cap)
        self.play(LaggedStart(*[Indicate(f[-1], color=GOLD, scale_factor=1.4) for f in finals],
                              lag_ratio=0.1), run_time=1.0)
        self.pad_to(A("in parallel") - 0.2)
        cap = swap_cap(label("parallel  ·  streaming  ·  while the epoch is live", size=FS_LABEL,
                             color=CYAN), cap)
        self.play(wave(e_dec), run_time=0.8)
        self.play(wave(all_mrg), run_time=0.8)
        self.play(wave(e_r2), run_time=0.8)
        # pause beat: zoom out over the braided network, every round flowing at once
        self.pad_to(word_end(SID, "still live") + 0.02)
        self.play(self.frame.animate.scale(1.18), wave(e_dec, CYAN), wave(all_mrg, CYAN), wave(e_r2, CYAN),
                  run_time=1.1)

        # stragglers: profile 11 is really two partial buckets -> partial round R3
        self.pad_to(A("lag behind") - 0.2)
        up = (ROW[0] - ROW[2]) * UP
        keep = VGroup(merged, e_r2, finals, r2, *e_mrg.values())
        self.play(FadeOut(VGroup(roots, kids, e_dec, r1)), FadeOut(cap, shift=0.1 * DOWN),
                  self.frame.animate.scale(1 / 1.18), run_time=0.7)
        self.play(keep.animate.shift(up), FadeOut(VGroup(*e_mrg.values())), run_time=0.9)
        p11a = rbucket(1.05, 0.72, CYAN, "11", (0.0, 0.75))
        p11b = rbucket(1.05, 0.72, CYAN, "11", (0.75, 1.0))
        VGroup(p11a, p11b).arrange(RIGHT, buff=0.1).move_to(finals[3])
        ptag = label("partial coverage", size=FS_LABEL, color=FLARE).next_to(VGroup(p11a, p11b), DOWN, buff=0.14)
        re_e = []
        for m, tgt in [(m01, p11a), (m11a, p11a), (m11b, p11b)]:
            e = e_r2_by[(3, id(m))]
            re_e.append(e.animate.put_start_and_end_on(m.get_bottom() + DOWN * 0.06, tgt.get_top() + UP * 0.06))
        self.play(*rmorph(finals[3], p11a), *rmorph(finals[3], p11b), FadeOut(finals[3]), *re_e,
                  FadeIn(ptag), run_time=1.1)
        self.add(p11a, p11b)
        self.pad_to(A("another partial") - 0.3)
        f110 = rbucket(1.05, 0.72, AMBER, "110", (0.0, 1.0), bits_size=FS_LABEL)
        f111 = rbucket(1.05, 0.72, CYAN, "111", (0.0, 1.0), bits_size=FS_LABEL)
        f110.move_to([p11a.get_x(), ROW[2], 0])
        f111.move_to([p11b.get_x(), ROW[2], 0])
        e_r3 = VGroup(*[redge(pp, f, f[0].get_stroke_color()) for pp in (p11a, p11b) for f in (f110, f111)])
        r3 = mtex("R_3", size=FS_LABEL, color=MUT).next_to(
            np.array([p11b.get_right()[0], (ROW[1] + ROW[2]) / 2, 0]), RIGHT, buff=0.3)
        pr = pill("partial round", color=CYAN).move_to([5.25, CAP_Y, 0])
        self.play(LaggedStart(*[ShowCreation(e) for e in e_r3], lag_ratio=0.1),
                  *rmorph(p11a, f110), *rmorph(p11b, f110, bits=False),
                  *rmorph(p11a, f111), *rmorph(p11b, f111, bits=False),
                  FadeOut(ptag), FadeIn(r3), FadeOut(rd), FadeIn(pr), run_time=1.4)
        self.play(VGroup(p11a, p11b).animate.fade(0.5), run_time=0.4)

        # the jagged frontier
        self.pad_to(A("jagged frontier") - 0.3)
        jag = label("the jagged frontier", size=FS_BODY, color=FLARE)
        cap = swap_cap(jag)
        fy0 = ROW[1] - 0.36 - 0.2
        fy1 = ROW[2] - 0.36 - 0.2
        xs = (finals[2].get_right()[0] + p11a.get_left()[0]) / 2
        frontier = VMobject()
        frontier.set_points_as_corners([[finals[0].get_left()[0] - 0.2, fy0, 0], [xs, fy0, 0], [xs, fy1, 0],
                                        [f111.get_right()[0] + 0.2, fy1, 0]])
        frontier.set_stroke(FLARE, SW, 0.95)
        self.pad_to(A("different depths") - 0.2)
        da = label("depth 2", size=FS_LABEL, color=FLARE).next_to(np.array([finals[1].get_x(), fy0, 0]), DOWN, buff=0.12)
        db = label("depth 3", size=FS_LABEL, color=FLARE).next_to(
            np.array([(f110.get_x() + f111.get_x()) / 2 - 1.6, fy1, 0]), DOWN, buff=0.12)
        self.play(ShowCreation(frontier), FadeIn(da), FadeIn(db), run_time=1.0)
        # prefix partition of the field
        self.pad_to(A("partition the field") - 0.3)
        BARW, bar_y = 9.0, ROW[3] - 0.15
        parts = VGroup()
        for x0, x1, c, bb in [(0.0, 0.25, AMBER, "00"), (0.25, 0.5, CYAN, "01"), (0.5, 0.75, AMBER, "10"),
                              (0.75, 0.875, AMBER, "110"), (0.875, 1.0, CYAN, "111")]:
            rr = Rectangle(width=BARW * (x1 - x0) - 0.06, height=0.46).set_fill(c, 0.3).set_stroke(c, SW_THIN, 0.95)
            rr.move_to([-BARW / 2 + BARW * (x0 + x1) / 2, bar_y, 0])
            parts.add(VGroup(rr, mtex(f'"{bb}"', size=FS_LABEL, color=STAR).move_to(rr)))
        pf = label("a prefix partition of the field", size=FS_LABEL, color=MUT).next_to(parts, RIGHT, buff=0.3)
        pf.next_to(parts, DOWN, buff=0.12)
        self.play(LaggedStart(*[FadeIn(pp, shift=0.1 * UP) for pp in parts], lag_ratio=0.12), FadeIn(pf),
                  run_time=1.2)
        self.pad_to(A("from sentinel to sentinel") - 0.4)
        finished = [finals[0], finals[1], finals[2], f110, f111]
        self.play(*[Indicate(f[-1], color=GOLD, scale_factor=1.5) for f in finished],
                  Flash(g6[1].get_center(), color=STAR), Flash(g7[1].get_center(), color=STAR), run_time=0.9)
        # pause beat: finished buckets click onto the finish rail, sntl_6 -> sntl_7
        self.pad_to(word_end(SID, "sentinel to sentinel") + 0.02)
        rail_lines = VGroup(*[Line([XL + 0.1, YS - 0.2 - 0.075 * i, 0], [XR - 0.1, YS - 0.2 - 0.075 * i, 0],
                                   stroke_width=4.0, stroke_color=f[-1].get_stroke_color())
                              for i, f in enumerate(finished)])
        self.play(LaggedStart(*[TransformFromCopy(f[-1], ln) for f, ln in zip(finished, rail_lines)],
                              lag_ratio=0.18), run_time=0.75)
        self.play(Flash(g6[1].get_center(), color=GOLD, flash_radius=0.4),
                  Flash(g7[1].get_center(), color=GOLD, flash_radius=0.4), run_time=0.4)
        self.pad_to(A("seal step") - 0.2)
        seals = VGroup(*[checkmark(0.26, GOLD).move_to(f[0].get_corner(UR) + 0.02 * DOWN) for f in finished])
        sl = label("sealed: both sentinels checked", size=FS_LABEL, color=GOLD)
        self.play(LaggedStart(*[ShowCreation(s_) for s_ in seals], lag_ratio=0.15), run_time=0.8)
        cap = swap_cap(sl, cap, rt=0.5)

        # in the proof tree: split + two descents
        self.pad_to(A("in the proof tree") - 0.3)
        self.play(FadeOut(VGroup(merged, e_r2, finals[:3], p11a, p11b, f110, f111, e_r3, r2, r3, frontier,
                                 da, db, parts, pf, seals, cap, pr, brs, beads, rail_lines)), run_time=0.6)
        P = bucket(1.6, 0.7, color=STAR, tex="p").move_to(LEFT * 4.6 + UP * 1.2)
        split = step_pill("split", color=CYAN).next_to(P, RIGHT, buff=0.8)
        sides = VGroup(bucket(1.2, 0.6, AMBER, tex="q_0"), bucket(1.2, 0.6, CYAN, tex="q_1")).arrange(DOWN, buff=0.3)
        sides.next_to(split, RIGHT, buff=0.8)
        a1 = tarrow(P, split, color=MUT)
        a2 = tarrow(split, sides, color=MUT)
        self.play(FadeIn(P), FadeIn(split), ShowCreation(a1), run_time=0.7)
        self.pad_to(A("proves the product") - 0.2)
        sp_chk = mtex("p = q_0 q_1, quad q_0 (-R) != 0", size=FS_LABEL, color=STAR).next_to(VGroup(P, split), DOWN, buff=0.45)
        self.play(FadeIn(sides), ShowCreation(a2), FadeIn(sp_chk), run_time=0.9)
        self.pad_to(A("two descents") - 0.2)
        d0 = step_pill("descend", color=CYAN).move_to(RIGHT * 3.0 + UP * 1.7)
        d1 = step_pill("descend", color=CYAN).move_to(RIGHT * 3.0 + DOWN * 0.3)
        o0 = bucket(1.2, 0.6, AMBER, tex="q_0").next_to(d0, RIGHT, buff=0.6)
        o1 = bucket(1.2, 0.6, CYAN, tex="q_1").next_to(d1, RIGHT, buff=0.6)
        self.play(FadeIn(d0), FadeIn(d1), ShowCreation(tarrow(sides, d0, color=MUT)),
                  ShowCreation(tarrow(sides, d1, color=MUT)), run_time=0.8)
        self.pad_to(A("returns one side") - 0.2)
        self.play(FadeIn(o0, shift=0.2 * RIGHT), FadeIn(o1, shift=0.2 * RIGHT),
                  ShowCreation(tarrow(d0, o0, color=AMBER)), ShowCreation(tarrow(d1, o1, color=CYAN)), run_time=0.8)
        self.pad_to(A("checks the purity") - 0.2)
        pc0 = rich([("checks purity of", MUT), ("$q_1$", CYAN)], size=FS_LABEL).next_to(d0, DOWN, buff=0.15)
        pc1 = rich([("checks purity of", MUT), ("$q_0$", AMBER)], size=FS_LABEL).next_to(d1, DOWN, buff=0.15)
        self.play(FadeIn(pc0), FadeIn(pc1), run_time=0.7)
        self.pad_to(A("both buckets are|certified pure") - 0.3)
        pure = label("both children derived: both buckets certified pure", size=FS_BODY, color=GOLD)
        pure.move_to(DOWN * 1.9)
        self.play(FadeIn(pure, shift=0.1 * UP), run_time=0.7)

        # grinding: R_0 private until the epoch closes
        self.pad_to(A("what about an attacker") - 0.3)
        keep = (note, title, strip, g6, g7, s6, s7)
        tree_old = VGroup(*[m for m in self.mobjects if isinstance(m, VMobject) and not any(m is k for k in keep)])
        self.play(FadeOut(tree_old), run_time=0.6)
        tgt = bucket(1.4, 0.8, color=STAR).move_to(LEFT * 2.5 + UP * 0.6)
        atk = VGroup(*[tg_chip('"tg"', color=FLARE, size=FS_SMALL) for _ in range(5)])
        atk.arrange(DOWN, buff=0.12).move_to(LEFT * 5.6 + UP * 0.6)
        self.play(FadeIn(tgt), LaggedStart(*[FadeIn(c, shift=0.2 * RIGHT) for c in atk], lag_ratio=0.1),
                  run_time=0.8)
        self.pad_to(A("overload") - 0.2)
        self.play(LaggedStart(*[c.animate.move_to(tgt).scale(0.5) for c in atk], lag_ratio=0.12), run_time=1.0)
        self.play(FadeOut(atk), run_time=0.3)
        self.pad_to(A("stay unpredictable") - 0.3)
        oss = panel(3.6, 2.4, color=CYAN, fill_opacity=0.06).move_to(RIGHT * 3.0 + UP * 0.6)
        oss_l = label("service", size=FS_LABEL, color=CYAN).next_to(oss, UP, buff=0.12)
        dialc = Circle(radius=0.55).set_stroke(STAR, SW).move_to(oss.get_center() + LEFT * 0.7)
        needle = Line(dialc.get_center(), dialc.get_center() + UP * 0.45, stroke_color=GOLD, stroke_width=SW)
        r0 = mtex("R_0", size=FS_BODY, color=GOLD).next_to(dialc, RIGHT, buff=0.3)
        glass = Rectangle(width=3.3, height=2.1).move_to(oss).set_fill(STAR, 0.10).set_stroke(STAR, SW_THIN, 0.6)
        self.play(FadeIn(oss), FadeIn(oss_l), FadeIn(dialc), FadeIn(needle), FadeIn(r0), run_time=0.8)
        self.pad_to(A("samples its first") - 0.2)
        self.play(Rotate(needle, -2.3, about_point=dialc.get_center()), FadeIn(glass), run_time=0.9)
        priv = label("private", size=FS_LABEL, color=STAR).next_to(oss, DOWN, buff=0.15)
        self.play(FadeIn(priv), run_time=0.4)
        self.pad_to(A("steps it up") - 0.3)
        step_eq = mtex("R_(j+1) = R_j + 1", size=FS_BODY, color=STAR).next_to(priv, DOWN, buff=0.25)
        self.play(Write(step_eq), run_time=0.8)
        self.pad_to(A("reveals it only") - 0.2)
        self.play(FadeOut(glass), Transform(priv, label("revealed after the epoch closes", size=FS_LABEL,
                                                         color=GOLD).move_to(priv)),
                  Flash(g7[1].get_center(), color=GOLD), run_time=0.9)
        self.pad_to(A("affects balance") - 0.2)
        bal = rich([("affects", TXT), ("balance", CYAN), (", never", TXT), ("soundness", GOLD)], size=FS_BODY)
        bal.move_to(LEFT * 2.5 + DOWN * 1.2)
        self.play(FadeIn(bal), run_time=0.7)
        self.pad_to(A("badly balanced") - 0.3)
        ign = label("a badly balanced routing can simply be ignored", size=FS_LABEL, color=MUT)
        ign.next_to(bal, DOWN, buff=0.25)
        self.play(FadeIn(ign), run_time=0.7)

        # scale card
        self.pad_to(A("even at") - 0.3)
        self.play(FadeOut(VGroup(tgt, oss, oss_l, dialc, needle, r0, priv, step_eq, bal, ign)), run_time=0.5)
        card = VGroup(
            mtex('50"K TPS" times 8 "tg" times 2 "weeks"  <  4.84 times 10^11 "tachygrams"', size=FS_BODY, color=STAR),
            mtex('<  6.1 times 10^7 "root buckets at" 8000 "entries"', size=FS_BODY, color=STAR),
            mtex('k <= 26 "  within a 32-bit profile"', size=FS_BODY, color=GOLD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        cb = boxed(card, color=CYAN, pad=0.35, fill=0.05).move_to(UP * 0.4)
        self.play(FadeIn(cb[0]), LaggedStart(*[FadeIn(c, shift=0.1 * UP) for c in card], lag_ratio=0.3),
                  run_time=1.5)
        self.pad_to(scene_T(SID))


# =================================================================================
class Scene45(TimedScene):
    """The evidence tree: fold final buckets under one root; price the query."""

    def construct(self):
        SID = "4.5"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731

        note = docked_note()
        self.add(note)
        self.wait(0.3)
        title = scene_title("The evidence tree")
        self.play(Write(title), run_time=0.7)

        # many final buckets, one proof each
        n = 16
        xs = np.linspace(-5.4, 5.4, n)
        YL, YM, YR = -0.7, 0.75, 2.05
        cols = [CYAN if i % 3 else AMBER for i in range(n)]
        leaves = VGroup(*[bucket(0.52, 0.42, color=cols[i], fill=0.15).move_to([xs[i], YL, 0]) for i in range(n)])
        toks = VGroup(*[proof_token(0.09).next_to(leaves[i], DOWN, buff=0.15) for i in range(n)])
        self.play(LaggedStart(*[FadeIn(l_, shift=0.1 * UP) for l_ in leaves], lag_ratio=0.04),
                  LaggedStart(*[FadeIn(t_) for t_ in toks], lag_ratio=0.04), run_time=1.2)
        lot = label("one proof per final bucket", size=FS_LABEL, color=FLARE).move_to(DOWN * 1.75)
        self.play(FadeIn(lot), run_time=0.5)

        # fold into a quaternary Poseidon Merkle tree
        self.pad_to(A("folds") - 0.2)
        mids = VGroup(*[Dot([xs[4 * k:4 * k + 4].mean(), YM, 0], radius=0.1).set_fill(STAR, 1) for k in range(4)])
        root = Dot([0, YR, 0], radius=0.14).set_fill(STAR, 1)
        e1 = VGroup(*[Line(leaves[i].get_top(), mids[i // 4].get_center(), stroke_color=MUT,
                           stroke_width=SW_THIN) for i in range(n)])
        e2 = VGroup(*[Line(mids[k].get_center(), root.get_center(), stroke_color=MUT, stroke_width=SW_THIN)
                      for k in range(4)])
        self.play(ShowCreation(e1), FadeIn(mids), run_time=0.9)
        self.play(ShowCreation(e2), FadeIn(root), FadeOut(lot),
                  *[t_.animate.move_to(root).scale(0.3).set_opacity(0) for t_ in toks], run_time=1.1)
        self.remove(toks)
        rglow = GlowDot(root.get_center(), color=STAR, radius=0.5)
        self.add(rglow, root)
        self.pad_to(A("evidence tree") - 0.2)
        rl = label("one root", size=FS_LABEL, color=STAR).next_to(root, RIGHT, buff=0.3)
        self.play(FadeIn(rl), Flash(root.get_center(), color=STAR, flash_radius=0.3, line_length=0.12), run_time=0.7)
        self.pad_to(A("arity four") - 0.4)
        ar = rich([("Poseidon Merkle tree,", TXT), ("arity 4", STAR), ("= sponge rate", MUT)], size=FS_LABEL)
        ar.next_to(root, LEFT, buff=0.45)
        self.play(FadeIn(ar), *[Indicate(m_, color=STAR, scale_factor=1.6) for m_ in mids], run_time=0.9)

        # one leaf's payload
        self.pad_to(A("each leaf binds") - 0.2)
        L = leaves[5]
        ring = SurroundingRectangle(L, buff=0.08).set_stroke(GOLD, SW_BOLD)
        parts = [('$($', TXT), ('$e,$', STAR), ('$"sntl"_e, "sntl"_(e+1),$', STAR), ('$R_0,$', GOLD),
                 ('$j, b,$', CYAN), ('$"Com"(q_b)$', CYAN), ('$)$', TXT)]
        payload = rich(parts, size=FS_HEAD, buff=0.12).move_to(DOWN * 2.35)
        conn = DashedLine(L.get_bottom(), payload.get_top(), dash_length=0.07).set_stroke(GOLD, SW_THIN)
        self.play(ShowCreation(ring), ShowCreation(conn), FadeIn(payload[0]), FadeIn(payload[-1]), run_time=0.6)
        for idx, ph in ((1, "binds the epoch"), (2, "two sentinels"), (3, "first discriminant"),
                        (4, "profile"), (5, "bucket's commitment")):
            self.pad_to(A(ph) - 0.15)
            self.play(FadeIn(payload[idx], shift=0.1 * UP), run_time=0.45)
        self.pad_to(A("single root") - 0.2)
        self.play(Flash(root.get_center(), color=STAR, flash_radius=0.3, line_length=0.12), run_time=0.6)
        # pause beat: buckets fold up the rate-4 tree, the root glows: epoch 6's certificate
        self.pad_to(word_end(SID, "single root") + 0.02)
        rl6 = label("one root for epoch 6", size=FS_LABEL, color=STAR).move_to(rl, aligned_edge=LEFT)
        up1 = AnimationGroup(*[ShowPassingFlash(e.copy().set_stroke(STAR, 4, 1.0), time_width=0.7) for e in e1])
        up2 = AnimationGroup(*[ShowPassingFlash(e.copy().set_stroke(STAR, 5, 1.0), time_width=0.7) for e in e2])
        self.play(Succession(up1, up2, AnimationGroup(rglow.animate(rate_func=there_and_back).scale(1.8),
                                                       Flash(root.get_center(), color=STAR, flash_radius=0.35,
                                                             line_length=0.12))),
                  AnimationGroup(FadeOut(rl), FadeIn(rl6), lag_ratio=0.85), run_time=1.0)
        rl = rl6
        # a single leaf is a valid tree
        self.pad_to(A("doesn't have to") - 0.2)
        mini_l = bucket(0.52, 0.42, color=CYAN, fill=0.15)
        mini_r = Dot(radius=0.11).set_fill(STAR, 1).next_to(mini_l, UP, buff=0.5)
        mini = VGroup(mini_l, mini_r, Line(mini_l.get_top(), mini_r.get_center(), stroke_color=MUT,
                                         stroke_width=SW_THIN))
        mini.move_to(RIGHT * 5.3 + DOWN * 1.75)
        self.pad_to(A("single leaf") - 0.2)
        ml = label("one leaf: still valid", size=FS_LABEL, color=TXT).next_to(mini, DOWN, buff=0.15)
        self.play(FadeIn(mini), FadeIn(ml), run_time=0.7)
        self.pad_to(A("already a proven") - 0.2)
        self.play(Indicate(mini_l, color=GOLD, scale_factor=1.3), run_time=0.7)

        # queries
        self.pad_to(A("for membership") - 0.9)
        self.play(FadeOut(VGroup(payload, conn, mini, ml, ring, ar)), run_time=0.6)
        path = VGroup(e1[5].copy(), e2[1].copy()).set_stroke(GOLD, SW_BOLD)
        self.pad_to(A("for membership") - 0.15)
        mem = rich([("membership:", GOLD), ("authenticate a leaf", TXT)], size=FS_BODY).move_to(LEFT * 2.6 + DOWN * 1.7)
        self.play(FadeIn(mem), ShowCreation(path), run_time=0.9)
        self.pad_to(A("check that the value") - 0.2)
        z = mtex('q_b ("cm") = 0', size=FS_BODY, color=GOLD).next_to(mem, DOWN, buff=0.25).align_to(mem, LEFT)
        self.play(FadeIn(z), run_time=0.6)
        self.pad_to(A("no profile") - 0.1)
        np_ = label("no profile needed", size=FS_LABEL, color=MUT).next_to(z, RIGHT, buff=0.4)
        self.play(FadeIn(np_), run_time=0.5)
        self.pad_to(A("divides the epochs") - 0.4)
        dv = label("every bucket divides the epoch's polynomial", size=FS_LABEL, color=MUT)
        dv.next_to(z, DOWN, buff=0.2).align_to(mem, LEFT)
        self.play(FadeIn(dv), run_time=0.6)

        # rail with one root per closed epoch
        self.pad_to(A("that's how our") - 0.4)
        rail = EpochRail(first=4, last=10)
        tree_icons = VGroup(*[VGroup(Dot(radius=0.1).set_fill(STAR, 1)) .move_to(rail.center_of(e, dy=0.42))
                              for e in (5, 6, 7, 8)])
        self.play(FadeOut(VGroup(mem, z, np_, dv)), FadeIn(rail),
                  LaggedStart(*[FadeIn(t_, scale=0.5) for t_ in tree_icons], lag_ratio=0.15), run_time=0.8)
        self.pad_to(A("found in epoch five") - 0.2)
        cm = tg_chip('"cm"', color=GOLD).move_to(rail.center_of(5, dy=1.15))
        self.play(FadeIn(cm, shift=0.2 * DOWN), Flash(tree_icons[0].get_center(), color=GOLD), run_time=0.7)

        # non-membership
        self.pad_to(A("for non") - 0.2)
        # right of the epoch-8 tree icon, between the leaves and the rail (clear of every rail glyph)
        nm = VGroup(
            label("non-membership:", size=FS_LABEL, color=CYAN),
            rich([("re-derive discriminants from", TXT), ("$R_0$", GOLD)], size=FS_LABEL),
            rich([("bits of", TXT), ('$"nf"_6$', GOLD), ("select this leaf", TXT)], size=FS_LABEL),
            mtex('q_b ("nf"_6) != 0', size=FS_BODY, color=CYAN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        nm.move_to([2.45, -1.12, 0], aligned_edge=UL)
        self.play(FadeIn(nm[0]), FadeIn(nm[1]), run_time=0.7)
        self.pad_to(A("bits select") - 0.3)
        self.play(FadeIn(nm[2]), run_time=0.5)
        self.pad_to(A("nonzero there") - 0.3)
        self.play(FadeIn(nm[3]), run_time=0.5)
        self.pad_to(A("nullifier for epoch six") - 0.2)
        nf = tg_chip('"nf"_6', color=GOLD).move_to(rail.center_of(6, dy=1.15))
        ck = checkmark(0.3, GOLD).next_to(nf, RIGHT, buff=0.15)
        self.play(FadeIn(nf, shift=0.2 * DOWN), run_time=0.5)
        self.play(ShowCreation(ck), run_time=0.4)

        # compare with the wall
        self.pad_to(A("so the sixteen") - 0.8)
        self.play(FadeOut(VGroup(leaves, e1, e2, mids, path, rl, nm)), FadeOut(Group(root, rglow)), run_time=0.6)
        wall = VGroup(mtex('e(X) : "deg" approx 4.8 times 10^8', size=FS_BODY, color=FLARE),
                      label("more than 16 minutes to verify", size=FS_LABEL, color=FLARE)).arrange(DOWN, buff=0.2)
        newc = VGroup(label("evidence tree", size=FS_BODY, color=STAR),
                      label("at most 13 hashes + one bounded opening", size=FS_LABEL, color=GOLD)).arrange(DOWN, buff=0.2)
        wb = boxed(wall, color=FLARE, pad=0.3).move_to(LEFT * 3.3 + UP * 0.9)
        nb_ = boxed(newc, color=GOLD, pad=0.3).move_to(RIGHT * 3.2 + UP * 0.9)
        arr = tarrow(wb, nb_, color=GOLD, width=SW)
        self.pad_to(A("sixteen minute") - 0.2)
        self.play(FadeIn(wb), run_time=0.6)
        self.pad_to(A("turned into") - 0.2)
        self.play(GrowFromPoint(arr, wb.get_right()), FadeIn(nb_, shift=0.2 * LEFT), run_time=0.9)
        self.pad_to(A("routing ran once") - 0.3)
        once = label("routing ran once, in flight; building the tree is the only post-epoch work",
                     size=FS_LABEL, color=MUT).move_to(DOWN * 0.7)
        self.play(FadeIn(once), run_time=0.7)

        # building the tree is the only post-close work: the roots on the rail glow
        self.pad_to(A("building the tree") - 0.1)
        self.play(*[Flash(t_.get_center(), color=STAR, flash_radius=0.3) for t_ in tree_icons],
                  *[t_.animate(rate_func=there_and_back).scale(1.6) for t_ in tree_icons], run_time=1.0)
        self.pad_to(scene_T(SID))

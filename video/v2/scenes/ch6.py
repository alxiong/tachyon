"""Chapter 6 — Landing: consensus and aggregation (scenes 6.1, 6.2).

6.1 explains the two-epoch duplicate window through the grace-period double spend:
spend A targets epoch 9 but is held into epoch 10; spend B targets epoch 10 with an
honest proof. Single nullifiers miss; adjacent pairs collide; the window catches the
pushed-further variant.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style import *  # noqa: E402,F403

ACC_ACT = '"acc"^"act"'
ACC_TG = '"acc"^"tg"'


def nf_chip(sub, color=STAR, size=FS_LABEL):
    return tex_chip(f'"nf"_({sub})', color=color, size=size, pad=0.1)


def tg_pair(kind, e=9, color=STAR, size=FS_SMALL + 2):
    """The two tachygrams one action carries: spend (nf_e, nf_e+1) or output (cm, tg_bot)."""
    if kind == "spend":
        a, b = nf_chip(str(e), color, size), nf_chip(str(e + 1), color, size)
    else:
        a = tex_chip('"cm"', color=color, size=size, pad=0.1)
        b = tex_chip('"tg"_bot', color=color, size=size, pad=0.1)
    return VGroup(a, b).arrange(RIGHT, buff=0.1)


def action_row(kind, e=9, color=STAR, size=FS_SMALL + 2):
    name = label(kind, size=FS_SMALL if size < FS_LABEL else FS_LABEL - 1, color=MUT)
    pr = tg_pair(kind, e, color, size)
    row = VGroup(name, pr).arrange(RIGHT, buff=0.22)
    box = SurroundingRectangle(row, buff=0.1).set_stroke(DIM, SW_THIN, 0.8).round_corners(0.06)
    g = VGroup(box, name, pr)
    g.box, g.name, g.pair = box, name, pr
    return g


def action_stamp(kinds=("spend", "output"), e=9, title="Stamp", color=STAR, size=FS_SMALL + 2):
    """A stamp drawn as what it covers: public inputs over its actions, each with two tachygrams."""
    t = label(title, size=FS_LABEL, color=color)
    pis = mtex(f'({ACC_ACT}, {ACC_TG}, "anchor")', size=FS_SMALL + 2, color=TXT)
    rows = VGroup(*[action_row(k, e, STAR, size) for k in kinds]).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
    inner = VGroup(t, pis, rows).arrange(DOWN, buff=0.16)
    frame = RoundedRectangle(width=inner.get_width() + 0.4, height=inner.get_height() + 0.34,
                             corner_radius=0.12).set_stroke(color, SW, 0.95).set_fill(color, 0.04)
    frame.move_to(inner)
    g = VGroup(frame, t, pis, rows)
    g.frame, g.title, g.pis, g.rows = frame, t, pis, rows
    return g


def spend_card(name, target, pair_eps, color):
    """An attacker spend: title + its published nullifier chips (1 or 2)."""
    t = label(f"spend {name}", size=FS_LABEL, color=color)
    tgt = label(f"targets epoch {target}", size=FS_SMALL, color=MUT)
    chips = VGroup(*[nf_chip(str(x), color, FS_LABEL) for x in pair_eps]).arrange(RIGHT, buff=0.1)
    inner = VGroup(VGroup(t, tgt).arrange(DOWN, buff=0.06), chips).arrange(DOWN, buff=0.16)
    frame = RoundedRectangle(width=max(2.3, inner.get_width() + 0.4), height=inner.get_height() + 0.3,
                             corner_radius=0.12).set_stroke(color, SW).set_fill(color, 0.06)
    frame.move_to(inner)
    g = VGroup(frame, t, tgt, chips)
    g.frame, g.chips = frame, chips
    return g


def tag_chip(letter, color):
    """A tiny lettered tag marking where a spend landed on the rail."""
    c = RoundedRectangle(width=0.42, height=0.42, corner_radius=0.08).set_stroke(color, SW_THIN).set_fill(color, 0.12)
    t = label(letter, size=FS_SMALL, color=color).move_to(c)
    return VGroup(c, t)


def sig_seal(color=GOLD, r=0.22):
    c = Circle(radius=r).set_fill(color, 0.15).set_stroke(color, SW_THIN)
    t = mtex("sigma", size=FS_SMALL, color=color).move_to(c)
    return VGroup(c, t)


def x_mark(center, size=0.14, color=FLARE):
    a, b = VMobject(), VMobject()
    a.set_points_as_corners([center + size * UL, center + size * DR])
    b.set_points_as_corners([center + size * UR, center + size * DL])
    return VGroup(a, b).set_stroke(color, SW_BOLD)


class Scene61(TimedScene):
    def retitle(self, text):
        new = scene_title(text)
        anims = [FadeOut(self.title, shift=0.2 * UP), FadeIn(new, shift=0.2 * UP)]
        self.title = new
        return anims

    def construct(self):
        SID = "6.1"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731
        self.wait(0.3)

        # --- the validator's four checks --------------------------------------------------------
        self.title = scene_title("What's left for the validator")
        self.pad_to(A("what's left") - 0.3)
        self.play(Write(self.title), run_time=1.0)
        st = action_stamp(("spend", "spend", "output", "output")).move_to(RIGHT * 4.3 + UP * 0.1)
        self.play(FadeIn(st), run_time=0.8)
        items = [
            rich([("target", TXT), ('$"anchor"$', STAR), ("is canonical; its epoch is", TXT),
                  ('$e_"cur"$', STAR), ("or", TXT), ('$e_"cur" - 1$', STAR)], size=FS_LABEL),
            rich([(f'${ACC_ACT}$', STAR), ("matches the actions", TXT)], size=FS_LABEL),
            rich([(f'${ACC_TG}$', STAR), ("matches the published tachygrams", TXT)], size=FS_LABEL),
            rich([("one PCD proof verifies", TXT)], size=FS_LABEL),
        ]
        checks = bullets(items, size=FS_LABEL, buff=0.42, width=7.4).move_to(LEFT * 2.75 + UP * 0.3)
        marks = VGroup(*[checkmark(0.28, GOLD).move_to(row[0]) for row in checks])
        hls = [st.pis, st.rows, VGroup(*[r.pair for r in st.rows]), st.frame]
        for i, ph in enumerate(["target anchor", "action accumulator", "tachygram accumulator", "one proof"]):
            self.pad_to(A(ph) - 0.2)
            self.play(FadeIn(checks[i], shift=0.15 * RIGHT), run_time=0.6)
            self.play(FadeOut(checks[i][0]), FadeIn(marks[i], scale=0.5),
                      Indicate(hls[i], color=GOLD, scale_factor=1.04), run_time=0.6)
        self.pad_to(A("balance") - 0.2)
        orch = label("balance and signatures: exactly as in Orchard", size=FS_LABEL, color=MUT)
        orch.next_to(checks, DOWN, buff=0.5).align_to(checks, LEFT)
        self.play(FadeIn(orch), run_time=0.7)

        # --- what the stamp claims --------------------------------------------------------------
        self.pad_to(A("be precise") - 0.3)
        self.play(FadeOut(VGroup(checks, marks, orch, st)),
                  *self.retitle("What the stamp claims"), run_time=0.9)
        rail = EpochRail(first=6, last=10, width=12.4, y=-2.0, label_size=FS_LABEL)
        ep_w = label("epoch", size=FS_SMALL, color=MUT).next_to(rail.labels[0], LEFT, buff=0.35)
        self.play(FadeIn(rail), FadeIn(ep_w), run_time=0.7)
        self.pad_to(A("proves exclusion") - 0.1)
        x0 = rail.gates[0].get_center()[0] - 0.4
        x9 = rail.gate(9).get_center()[0]
        band = Rectangle(width=x9 - x0, height=0.3).set_fill(GOLD, 0.35).set_stroke(GOLD, SW_THIN)
        band.move_to([(x0 + x9) / 2, rail.y + 0.4, 0])
        band_lab = label("proven: exclusion since the inclusion epoch, before epoch 9", size=FS_LABEL, color=GOLD)
        band_lab.next_to(band, UP, buff=0.15).align_to(band, LEFT)
        self.play(GrowFromEdge(band, LEFT), FadeIn(band_lab), run_time=1.0)
        self.pad_to(A("the sentinel") - 0.1)
        s9 = mtex('"sntl"_9', size=FS_LABEL, color=STAR).next_to(rail.gate(9), DOWN, buff=0.15).shift(RIGHT * 0.45)
        self.play(rail.gate(9).animate.set_stroke(STAR, SW_BOLD), FadeIn(s9),
                  Flash(rail.gate(9).get_top(), color=STAR), run_time=0.8)
        self.pad_to(A("target anchor", 2) - 0.2)
        tgt = Triangle().set_fill(FLARE, 1).set_stroke(width=0).scale(0.15).rotate(PI)
        tgt.move_to(rail.center_of(9) + RIGHT * 0.5 + UP * 0.3)
        tgt_lab = mtex('"anchor"', size=FS_LABEL, color=FLARE).next_to(tgt, RIGHT, buff=0.15)
        self.play(FadeIn(tgt, shift=0.2 * DOWN), FadeIn(tgt_lab), run_time=0.6)
        self.pad_to(A("not an exclusion") - 0.1)
        gap = DashedLine(rail.gate(9).get_center() + UP * 0.3, tgt.get_left(), dash_length=0.08)
        gap.set_stroke(FLARE, SW)
        notend = label("the target anchor is not an exclusion endpoint", size=FS_LABEL, color=FLARE)
        notend.next_to(band_lab, UP, buff=0.35).align_to(band, LEFT)
        self.play(ShowCreation(gap), FadeIn(notend), run_time=0.8)
        self.pad_to(A("duplicates inside") - 0.1)
        e9box = Rectangle(width=rail.seg - 0.08, height=2.4).set_stroke(FLARE, SW).set_fill(FLARE, 0.05)
        e9box.move_to(rail.center_of(9, dy=1.3))
        job = label("duplicates in epoch 9: consensus's job", size=FS_LABEL, color=FLARE).next_to(e9box, UP, buff=0.15)
        job.align_to(e9box, RIGHT)
        self.play(ShowCreation(e9box), FadeIn(job), FadeOut(notend), run_time=0.8)
        self.pad_to(A("has to publish") - 0.2)
        n9 = nf_chip("9", color=GOLD).move_to(rail.center_of(9, dy=1.3))
        self.play(FadeIn(n9, shift=0.2 * DOWN), run_time=0.6)

        # --- the rule: one duplicate window, current + preceding epoch -----------------------------
        self.pad_to(A("double spend rule") - 0.4)
        self.play(FadeOut(VGroup(job, e9box, gap, tgt, tgt_lab, n9, band_lab)),
                  band.animate.set_fill(GOLD, 0.18), *self.retitle("The new double-spend rule"),
                  run_time=0.9)
        self.pad_to(A("duplicate window") - 0.2)
        WH = 3.5
        win = Rectangle(width=2 * rail.seg - 0.1, height=WH).set_stroke(FLARE, SW_BOLD).set_fill(FLARE, 0.06)
        win.move_to((rail.center_of(8) + rail.center_of(9)) / 2 + UP * (WH / 2 + 0.05))
        win_lab = label("duplicate window", size=FS_LABEL, color=FLARE).next_to(win, UP, buff=0.12)
        self.play(ShowCreation(win), FadeIn(win_lab), run_time=0.8)
        self.pad_to(A("current epic|current epoch") - 0.1)
        cl = VGroup(label("preceding", size=FS_SMALL, color=FLARE).move_to(rail.center_of(8, dy=WH - 0.25)),
                    label("current", size=FS_SMALL, color=FLARE).move_to(rail.center_of(9, dy=WH - 0.25)))
        self.play(FadeIn(cl, lag_ratio=0.4), run_time=0.8)
        self.pad_to(A("candidates") - 0.3)
        queue = VGroup(*[tg_chip('"tg"', color=STAR, size=FS_SMALL) for _ in range(3)]).arrange(RIGHT, buff=0.15)
        queue.move_to(rail.center_of(10, dy=2.2))
        ql = label("candidates, in order", size=FS_SMALL, color=MUT).next_to(queue, UP, buff=0.12)
        self.play(FadeIn(queue, lag_ratio=0.2), FadeIn(ql), run_time=0.6)
        slots = [rail.center_of(9, dy=1.6) + LEFT * 0.62 + RIGHT * 0.62 * k for k in range(3)]
        self.pad_to(A("each one checked") - 0.1)
        for c, p in zip(queue, slots):
            self.play(c.animate.move_to(p), run_time=0.3)
            self.play(Flash(p, color=GOLD, flash_radius=0.3, line_length=0.12), run_time=0.2)

        # --- think like a double spender: the grace period ---------------------------------------
        self.pad_to(A("why that shape") - 0.2)
        self.play(FadeOut(VGroup(queue, ql, cl, win, win_lab, band, rail, ep_w, s9)),
                  *self.retitle("Think like a double spender"), run_time=0.9)
        R = EpochRail(first=8, last=11, width=12.0, y=-2.55, label_size=FS_LABEL)
        R.labels.shift(DOWN * 0.05)
        R_w = label("epoch", size=FS_SMALL, color=MUT).next_to(R.labels[0], LEFT, buff=0.35)
        snt = VGroup(*[mtex(f'"sntl"_({e})', size=FS_SMALL, color=STAR).next_to(R.gate(e), DOWN, buff=0.12)
                       for e in (9, 10, 11)])
        self.play(FadeIn(R), FadeIn(R_w), FadeIn(snt), run_time=0.8)

        self.pad_to(A("grace period") - 0.2)
        grace = Rectangle(width=2 * R.seg - 0.12, height=0.34).set_fill(GOLD, 0.22).set_stroke(GOLD, SW_THIN)
        grace.move_to((R.center_of(9) + R.center_of(10)) / 2 + UP * 0.45)
        grace_lab = label("a stamp targeting 9 is accepted during 9 or 10", size=FS_LABEL, color=GOLD)
        grace_lab.next_to(grace, UP, buff=0.12)
        self.play(GrowFromCenter(grace), run_time=0.7)
        self.pad_to(A("still accepted") - 0.3)
        self.play(FadeIn(grace_lab, shift=0.1 * UP), run_time=0.6)

        # two spends of the same note
        self.pad_to(A("builds two spends") - 0.2)
        cardA = spend_card("A", 9, [9], STAR).move_to(LEFT * 3.2 + UP * 1.55)
        cardB = spend_card("B", 10, [10], AMBER).move_to(RIGHT * 3.2 + UP * 1.55)
        note = mtex('"note"_5', size=FS_LABEL, color=GOLD).move_to(UP * 2.35)
        linkA = DashedLine(note.get_left() + LEFT * 0.1, cardA.get_top() + RIGHT * 0.6, dash_length=0.07).set_stroke(GOLD, SW_THIN)
        linkB = DashedLine(note.get_right() + RIGHT * 0.1, cardB.get_top() + LEFT * 0.6, dash_length=0.07).set_stroke(GOLD, SW_THIN)
        chipsA, chipsB = cardA.chips, cardB.chips
        cardA.remove(chipsA)
        cardB.remove(chipsB)
        self.play(FadeIn(note), ShowCreation(linkA), ShowCreation(linkB), run_time=0.6)
        self.pad_to(A("the first targets") - 0.2)
        self.play(FadeIn(cardA, shift=0.2 * DOWN), run_time=0.6)
        self.pad_to(A("held back") - 0.2)
        hold = label("held back", size=FS_SMALL, color=STAR).next_to(cardA, DOWN, buff=0.12)
        self.play(FadeIn(hold), run_time=0.4)
        landA = Dot(R.center_of(10) + LEFT * 0.45, radius=0.11).set_fill(STAR, 1)
        pathA = VGroup()
        labA = tag_chip("A", STAR).next_to(landA, UP, buff=0.12)
        self.pad_to(A("10 begins|begins") - 0.3)
        self.play(FadeOut(grace_lab), FadeIn(landA, scale=2),
                  TransformFromCopy(cardA.frame, labA[0]), FadeIn(labA[1]), run_time=0.9)

        self.pad_to(A("the second targets") - 0.2)
        self.play(FadeIn(cardB, shift=0.2 * DOWN), run_time=0.6)
        landB = Dot(R.center_of(10) + RIGHT * 0.45, radius=0.11).set_fill(AMBER, 1)
        tagB = tag_chip("B", AMBER).next_to(landB, UP, buff=0.12)
        self.play(FadeIn(landB, scale=2), TransformFromCopy(cardB.frame, tagB[0]), FadeIn(tagB[1]), run_time=0.7)
        self.pad_to(A("both proofs") - 0.2)
        okA = checkmark(0.26, GOLD).next_to(cardA.frame, RIGHT, buff=0.15)
        okB = checkmark(0.26, GOLD).next_to(cardB.frame, LEFT, buff=0.15)
        honest = label("both proofs honest", size=FS_LABEL, color=GOLD).move_to(UP * 1.4)
        self.play(ShowCreation(okA), ShowCreation(okB), FadeIn(honest), run_time=0.7)

        # B's exclusion covers epoch 9; nf_9 truly never appeared there
        self.pad_to(A("the second one proves") - 0.2)
        xB = Rectangle(width=R.gate(10).get_center()[0] - (R.x0 - 0.3), height=0.28)
        xB.set_fill(AMBER, 0.28).set_stroke(AMBER, SW_THIN)
        xB.move_to([(R.gate(10).get_center()[0] + R.x0 - 0.3) / 2, R.y + 0.42, 0])
        xB_lab = label("B: exclusion through epoch 9", size=FS_LABEL, color=AMBER)
        xB_lab.next_to(xB, UP, buff=0.12).align_to(xB, LEFT)
        self.play(FadeOut(VGroup(honest, hold, grace)), GrowFromEdge(xB, LEFT), FadeIn(xB_lab), run_time=0.8)
        self.pad_to(A("never appeared") - 0.2)
        e9 = Rectangle(width=R.seg - 0.1, height=1.1).set_stroke(AMBER, SW).set_fill(AMBER, 0.04)
        e9.move_to(R.center_of(9, dy=1.65))
        no9 = rich([('$"nf"_9$', STAR), ("not here", TXT)], size=FS_LABEL).move_to(e9)
        self.play(ShowCreation(e9), FadeIn(no9), run_time=0.7)
        self.pad_to(A("that's true") - 0.1)
        ck9 = checkmark(0.3, GOLD).next_to(no9, DOWN, buff=0.15)
        self.play(ShowCreation(ck9), run_time=0.4)
        self.pad_to(A("didn't land") - 0.2)
        self.play(Indicate(e9, color=STAR, scale_factor=1.03), run_time=0.6)
        self.pad_to(A("it landed") - 0.1)
        self.play(Flash(landA.get_center(), color=STAR, flash_radius=0.4), Indicate(labA, color=STAR), run_time=0.7)

        # single-nullifier world: no collision
        self.pad_to(A("if each spend") - 0.2)
        world = label("if each spend published one nullifier", size=FS_LABEL, color=MUT).move_to(UP * 2.95)
        self.play(FadeOut(VGroup(xB, xB_lab, e9, no9, ck9, okA, okB, note, linkA, linkB)),
                  *self.retitle("One nullifier per spend?"), FadeIn(world), run_time=0.8)
        self.pad_to(A("the first would") - 0.2)
        self.play(FadeIn(chipsA, scale=1.3), run_time=0.5)
        self.pad_to(A("the second the") - 0.2)
        self.play(FadeIn(chipsB, scale=1.3), run_time=0.5)
        dA = chipsA[0].copy()
        dB = chipsB[0].copy()
        self.play(dA.animate.move_to(R.center_of(10, dy=1.7) + LEFT * 0.45),
                  dB.animate.move_to(R.center_of(10, dy=1.7) + RIGHT * 0.45), run_time=0.7)
        self.pad_to(A("nothing would collide") - 0.2)
        miss = label("no collision: double spend slips through", size=FS_LABEL, color=FLARE)
        miss.next_to(VGroup(dA, dB), UP, buff=0.35)
        self.play(FadeIn(miss), Flash(R.center_of(10, dy=1.1), color=FLARE, flash_radius=0.7), run_time=0.8)

        # pair world: collide on nf_10
        self.pad_to(A("that's why every", 2) - 0.2)
        pairA = spend_card("A", 9, [9, 10], STAR).move_to(cardA)
        pairB = spend_card("B", 10, [10, 11], AMBER).move_to(cardB)
        world2 = label("every spend also publishes the next epoch's nullifier", size=FS_LABEL, color=GOLD).move_to(UP * 2.95)
        cardA.add(chipsA)
        cardB.add(chipsB)
        self.play(FadeOut(VGroup(dA, dB, miss)), Transform(world, world2),
                  *self.retitle("Adjacent pairs"), run_time=0.8)
        self.pad_to(A("the first spend reveals") - 0.2)
        self.play(ReplacementTransform(cardA, pairA), run_time=0.6)
        self.pad_to(A("the second reveals") - 0.2)
        self.play(ReplacementTransform(cardB, pairB), run_time=0.6)
        self.pad_to(A("they collide") - 0.6)
        pA = pairA.chips.copy()
        pB = pairB.chips.copy()
        tA = pA.copy().move_to(R.center_of(10, dy=1.75))
        tB = pB.copy()
        tB.shift(tA[1].get_center() + DOWN * 0.62 - tB[0].get_center())
        self.play(Transform(pA, tA), Transform(pB, tB), run_time=0.6)
        hitA, hitB = pA[1], pB[0]
        self.play(Flash(hitA.get_center() + DOWN * 0.31, color=FLARE, flash_radius=0.5),
                  hitA.animate.set_color(FLARE), hitB.animate.set_color(FLARE), run_time=0.5)
        caught = rich([("collide on", FLARE), ('$"nf"_10$', FLARE)], size=FS_LABEL).next_to(tA, UP, buff=0.3)
        self.play(FadeIn(caught), run_time=0.3)

        # push further: B held to epoch 11 -> the window
        self.pad_to(A("the window") - 0.3)
        self.play(FadeOut(VGroup(pA, pB, caught, world)),
                  *self.retitle("And the window?"), run_time=0.7)
        self.pad_to(A("push one step") - 0.2)
        landB2 = Dot(R.center_of(11), radius=0.11).set_fill(AMBER, 1)
        pathB2 = VGroup()
        labB = tag_chip("B", AMBER).next_to(landB2, UP, buff=0.12)
        self.pad_to(A("until epoch 11|until epic 11|until") - 0.2)
        self.play(ReplacementTransform(landB, landB2), ReplacementTransform(tagB, labB), run_time=0.9)
        self.pad_to(A("now the colliding") - 0.2)
        cA = pairA.chips[1].copy()
        cB = pairB.chips[0].copy()
        self.play(cA.animate.move_to(R.center_of(10, dy=1.05)), cB.animate.move_to(R.center_of(11, dy=1.05)),
                  run_time=0.8)
        self.pad_to(A("a window over") - 0.2)
        W2 = Rectangle(width=2 * R.seg - 0.1, height=2.0).set_stroke(FLARE, SW_BOLD).set_fill(FLARE, 0.05)
        W2.move_to((R.center_of(10) + R.center_of(11)) / 2 + UP * 1.05)
        W2l = VGroup(label("preceding", size=FS_SMALL, color=FLARE).move_to(R.center_of(10, dy=1.85)),
                     label("current", size=FS_SMALL, color=FLARE).move_to(R.center_of(11, dy=1.85)))
        self.play(ShowCreation(W2), FadeIn(W2l), run_time=0.8)
        self.pad_to(A("holds both") - 0.2)
        link = Line(cA.get_right(), cB.get_left(), stroke_color=FLARE, stroke_width=SW)
        self.play(ShowCreation(link), cA.animate.set_color(FLARE), cB.animate.set_color(FLARE), run_time=0.5)
        self.pad_to(A("catches it") - 0.1)
        self.play(Flash(link.get_center(), color=FLARE, flash_radius=0.6), run_time=0.6)
        self.pad_to(A("anything older") - 0.2)
        old = Rectangle(width=R.gate(10).get_center()[0] - (R.x0 - 0.3), height=0.26)
        old.set_fill(GOLD, 0.25).set_stroke(GOLD, SW_THIN)
        old.move_to([(R.gate(10).get_center()[0] + R.x0 - 0.3) / 2, R.y + 0.4, 0])
        old_lab = label("older: already proven excluded", size=FS_LABEL, color=GOLD)
        old_lab.next_to(old, UP, buff=0.12).align_to(old, LEFT)
        self.play(GrowFromEdge(old, LEFT), FadeIn(old_lab), run_time=0.8)

        # a set
        self.pad_to(A("come as a set") - 0.6)
        stage = VGroup(pairA, pairB, landA, pathA, labA, landB2, pathB2, labB, cA, cB, link, W2, W2l, old, old_lab)
        self.play(FadeOut(stage), *self.retitle("They come as a set"), run_time=0.7)
        p1 = VGroup(nf_chip("e", GOLD, FS_BODY), nf_chip("e+1", GOLD, FS_BODY)).arrange(RIGHT, buff=0.12)
        p1l = label("adjacent pair", size=FS_LABEL, color=GOLD).next_to(p1, DOWN, buff=0.2)
        plus = mtex("+", size=FS_HEAD, color=STAR)
        w1 = VGroup(*[Rectangle(width=1.1, height=0.8).set_stroke(FLARE, SW).set_fill(FLARE, 0.06) for _ in range(2)])
        w1.arrange(RIGHT, buff=0)
        w1l = label("two-epoch window", size=FS_LABEL, color=FLARE).next_to(w1, DOWN, buff=0.2)
        setg = VGroup(VGroup(p1, p1l), plus, VGroup(w1, w1l)).arrange(RIGHT, buff=0.8).move_to(UP * 0.4 + LEFT * 0.0)
        self.play(FadeIn(setg, lag_ratio=0.3), run_time=0.9)
        self.pad_to(A("together") - 0.2)
        gapl = label("close the gap the grace period opened", size=FS_BODY, color=GOLD).next_to(setg, DOWN, buff=0.6)
        self.play(FadeIn(gapl, shift=0.1 * UP), run_time=0.7)

        # --- callback: the set consensus must hold ---------------------------------------------------
        self.pad_to(A("and look") - 0.3)
        self.play(FadeOut(VGroup(setg, gapl, R, R_w, snt)),
                  *self.retitle("The set consensus holds"), run_time=0.8)
        big = VGroup(*[Square(0.13).set_stroke(width=0).set_fill(FLARE, 0.5) for _ in range(18 * 34)])
        big.arrange_in_grid(18, 34, buff=0.035).move_to(LEFT * 2.2 + DOWN * 0.3)
        big_lab = label("all of history", size=FS_LABEL, color=MUT).next_to(big, DOWN, buff=0.2)
        small = VGroup(*[Square(0.13).set_stroke(width=0).set_fill(FLARE, 0.85) for _ in range(18 * 2)])
        small.arrange_in_grid(18, 2, buff=0.035).move_to(RIGHT * 4.6 + DOWN * 0.3)
        small_lab = label("two epochs", size=FS_LABEL, color=FLARE).next_to(small, DOWN, buff=0.2)
        self.play(FadeIn(big, lag_ratio=0.0005), FadeIn(big_lab), run_time=0.9)
        self.pad_to(A("not all") - 0.2)
        self.play(big.animate.fade(0.75), big_lab.animate.fade(0.4), run_time=0.7)
        self.pad_to(A("two epics|two epochs") - 0.2)
        self.play(FadeIn(small, lag_ratio=0.02), FadeIn(small_lab), run_time=0.6)
        self.pad_to(A("bounded") - 0.1)
        bnd = label("bounded, forever", size=FS_BODY, color=GOLD).next_to(small, UP, buff=0.3)
        self.play(FadeIn(bnd, shift=0.1 * DOWN), Indicate(small, color=GOLD, scale_factor=1.04), run_time=0.7)
        self.pad_to(scene_T(SID))


class Scene62(TimedScene):
    def construct(self):
        SID = "6.2"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731
        self.wait(0.3)
        title = scene_title("Aggregation")
        self.pad_to(A("aggregation") - 0.3)
        self.play(Write(title), run_time=0.8)

        # epoch 9's anchor chain up to "now"; sntl_10 lies in the future
        y = -2.55
        g9 = sentinel_gate(h=0.9).move_to([-6.2, y, 0])
        g10 = sentinel_gate(h=0.9).move_to([6.2, y, 0]).set_opacity(0.35)
        now_x = 4.2
        chain = Line([-6.2, y, 0], [now_x, y, 0], stroke_color=MUT, stroke_width=SW)
        future = DashedLine([now_x, y, 0], [6.2, y, 0], dash_length=0.1).set_stroke(DIM, SW_THIN)
        xs = list(np.linspace(-5.4, 3.8, 9))
        ticks = VGroup(*[Dot([x, y, 0], radius=0.07).set_fill(STAR, 0.9) for x in xs])
        l9 = mtex('"sntl"_9', size=FS_LABEL, color=STAR).next_to(g9, DOWN, buff=0.12)
        l10 = mtex('"sntl"_10', size=FS_LABEL, color=MUT).next_to(g10, DOWN, buff=0.12)
        now = Triangle().set_fill(FLARE, 1).set_stroke(width=0).scale(0.13).rotate(PI).move_to([now_x, y + 0.3, 0])
        now_l = label("now", size=FS_SMALL, color=FLARE).next_to(now, UP, buff=0.08)
        ep = label("epoch 9 anchor chain", size=FS_SMALL, color=MUT).move_to([-1.0, y - 0.45, 0])
        self.play(ShowCreation(chain), ShowCreation(future), FadeIn(g9), FadeIn(g10), FadeIn(ticks, lag_ratio=0.1),
                  FadeIn(l9), FadeIn(l10), FadeIn(now), FadeIn(now_l), FadeIn(ep), run_time=0.9)

        # three finished stamps from different transactions, at different anchors
        kinds = [("spend", "output"), ("spend", "spend", "output"), ("output",)]
        stamps = VGroup(*[action_stamp(k, title=f"Stamp · tx{i + 1}", size=FS_LABEL) for i, k in enumerate(kinds)])
        for st_ in stamps:
            st_.scale(0.85)
        stamps.arrange(RIGHT, buff=0.4, aligned_edge=DOWN).move_to(UP * 0.7 + LEFT * 0.9)
        at = [ticks[1], ticks[4], ticks[6]]
        legs = VGroup(*[DashedLine(s.get_bottom(), a.get_center(), dash_length=0.07).set_stroke(MUT, SW_THIN)
                        for s, a in zip(stamps, at)])
        anc = VGroup(*[mtex('"anchor"', size=FS_SMALL, color=STAR).next_to(a, UP, buff=0.12) for a in at])
        self.pad_to(A("takes finished") - 0.2)
        self.play(LaggedStart(*[FadeIn(s, shift=0.2 * DOWN) for s in stamps], lag_ratio=0.15),
                  ShowCreation(legs), run_time=0.9)

        # StampLift each to one common anchor, never past now (and never past a sentinel)
        self.pad_to(A("lifts them") - 0.1)
        common = ticks[8]
        cdot = Dot(common.get_center(), radius=0.12).set_fill(GOLD, 1)
        lift = step_pill("StampLift", color=GOLD).next_to(stamps, RIGHT, buff=0.4).shift(DOWN * 0.3)
        newlegs = VGroup(*[DashedLine(s.get_bottom(), common.get_center(), dash_length=0.07).set_stroke(GOLD, SW_THIN)
                           for s in stamps])
        self.play(FadeIn(lift), FadeIn(cdot, scale=2), ReplacementTransform(legs, newlegs), run_time=0.9)
        cl = label("common anchor", size=FS_SMALL, color=GOLD).next_to(cdot, DOWN, buff=0.45)
        self.play(FadeIn(cl), run_time=0.3)
        self.pad_to(A("never across") - 0.3)
        ghost = Dot([now_x, y, 0], radius=0.1).set_fill(FLARE, 1)
        self.play(FadeIn(ghost), run_time=0.2)
        self.play(ghost.animate.move_to([6.4, y, 0]), rate_func=there_and_back, run_time=0.7)
        self.play(FadeOut(ghost), Flash(g10.get_top(), color=FLARE, flash_radius=0.3), run_time=0.3)

        # StampMerge: union actions + tachygrams, multiply accumulators, fuse proofs
        self.pad_to(A("merges them") - 0.2)
        merge = step_pill("StampMerge", color=GOLD).move_to(UP * 2.55 + RIGHT * 3.6)
        self.play(FadeIn(merge), FadeOut(VGroup(newlegs, cl, lift, chain, future, g9, g10, ticks, l9, l10,
                                                  now, now_l, ep, cdot)), run_time=0.5)
        all_kinds = [k for ks in kinds for k in ks]
        agg = action_stamp(tuple(all_kinds), title="aggregate stamp", color=GOLD, size=FS_LABEL)
        agg.scale(0.85).move_to(RIGHT * 3.6 + DOWN * 0.25)
        u_lab = label("union the actions + tachygrams", size=FS_LABEL, color=TXT)
        mul = mtex(f'{ACC_TG} = {ACC_TG}_1 dot {ACC_TG}_2 dot {ACC_TG}_3', size=FS_LABEL, color=GOLD)
        fuse = label("fuse the three proofs into one", size=FS_LABEL, color=TXT)
        ops = VGroup(u_lab, mul, fuse).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to(LEFT * 3.4 + UP * 0.6)
        self.pad_to(A("union") - 0.1)
        src_rows = [r for s in stamps for r in s.rows]
        self.play(*[ReplacementTransform(r, t) for r, t in zip(src_rows, agg.rows)],
                  ReplacementTransform(VGroup(*[s.frame for s in stamps]), agg.frame),
                  FadeOut(VGroup(*[VGroup(s.title, s.pis) for s in stamps])),
                  FadeIn(VGroup(agg.title, agg.pis)), FadeIn(u_lab, shift=0.1 * RIGHT), run_time=0.8)
        self.pad_to(A("multiply") - 0.1)
        self.play(FadeIn(mul, shift=0.1 * RIGHT), run_time=0.5)
        self.pad_to(A("fuse the") - 0.1)
        toks = VGroup(*[proof_token(0.12).move_to(LEFT * (4.6 - 0.6 * k) + DOWN * 1.3) for k in range(3)])
        one = proof_token(0.16).next_to(agg.frame, RIGHT, buff=0.2).align_to(agg.frame, UP)
        self.play(FadeIn(fuse, shift=0.1 * RIGHT), FadeIn(toks), run_time=0.4)
        self.play(*[t.animate.move_to(one) for t in toks], run_time=0.5)
        self.remove(toks)
        self.add(one)

        # same shape -> merges again
        self.pad_to(A("same shape") - 0.2)
        shape = label("same shape as any stamp", size=FS_SMALL, color=GOLD).next_to(agg, DOWN, buff=0.15)
        self.play(FadeIn(shape), Indicate(agg.frame, color=GOLD, scale_factor=1.03), run_time=0.6)
        self.pad_to(A("merge again") - 0.3)
        st4 = action_stamp(("spend",), title="Stamp · tx4", size=FS_LABEL).scale(0.85).move_to(LEFT * 3.4 + DOWN * 1.6)
        self.play(FadeOut(VGroup(ops, merge)), FadeIn(st4, shift=0.2 * RIGHT), run_time=0.4)
        agg2 = action_stamp(tuple(all_kinds + ["spend"]), title="aggregate stamp", color=GOLD, size=FS_LABEL)
        agg2.scale(0.85).move_to(RIGHT * 3.6 + DOWN * 0.25)
        merge2 = step_pill("StampMerge", color=GOLD).move_to(LEFT * 0.2 + DOWN * 1.6)
        self.play(FadeIn(merge2), run_time=0.3)
        self.play(ReplacementTransform(agg.rows, agg2.rows[:-1]), ReplacementTransform(st4.rows, agg2.rows[-1:]),
                  ReplacementTransform(agg.frame, agg2.frame), ReplacementTransform(VGroup(agg.title, agg.pis),
                                                                                   VGroup(agg2.title, agg2.pis)),
                  FadeOut(VGroup(st4.frame, st4.title, st4.pis, merge2, shape)),
                  one.animate.next_to(agg2.frame, RIGHT, buff=0.2).align_to(agg2.frame, UP), run_time=0.8)

        # constituents: keep balance + signatures, swap stamp for a wtxid reference
        self.pad_to(A("each covered") - 0.3)
        txs = VGroup()
        for k in range(4):
            box = RoundedRectangle(width=4.6, height=0.62, corner_radius=0.1).set_stroke(STAR, SW_THIN).set_fill(STAR, 0.04)
            name = label(f"tx{k + 1}", size=FS_SMALL, color=STAR).move_to(box.get_left() + RIGHT * 0.4)
            seal = sig_seal(r=0.19).next_to(name, RIGHT, buff=0.22)
            bal = mtex('v^"bal"', size=FS_SMALL, color=GOLD).next_to(seal, RIGHT, buff=0.2)
            stp = label("stamp", size=FS_SMALL, color=MUT).next_to(bal, RIGHT, buff=0.35)
            txs.add(VGroup(box, name, seal, bal, stp))
        txs.arrange(DOWN, buff=0.15).move_to(LEFT * 3.5 + DOWN * 0.1)
        tx_lab = label("covered transactions", size=FS_LABEL, color=TXT).next_to(txs, UP, buff=0.15)
        self.play(FadeIn(txs, lag_ratio=0.1), FadeIn(tx_lab), run_time=0.7)
        self.pad_to(A("reference") - 0.3)
        refs = VGroup(*[mtex('-> "wtxid"_"agg"', size=FS_SMALL, color=GOLD).move_to(t[4], aligned_edge=LEFT)
                        for t in txs])
        self.play(*[FadeOut(t[4], shift=0.2 * UP) for t in txs],
                  LaggedStart(*[FadeIn(r, shift=0.1 * RIGHT) for r in refs], lag_ratio=0.15), run_time=0.9)
        self.pad_to(A("balance and signatures") - 0.2)
        stay = label("balance + signatures stay per transaction", size=FS_SMALL, color=GOLD).next_to(txs, DOWN, buff=0.2)
        self.play(*[Indicate(VGroup(t[2], t[3]), color=GOLD, scale_factor=1.25) for t in txs], FadeIn(stay),
                  run_time=0.8)
        self.pad_to(A("only proof") - 0.2)
        once = label("one proof, verified once", size=FS_LABEL, color=GOLD).next_to(agg2, DOWN, buff=0.2)
        self.play(FadeIn(once), Indicate(one, color=GOLD, scale_factor=1.4), run_time=0.7)
        self.pad_to(A("incentive") - 0.1)
        self.play(Flash(agg2.get_center(), color=GOLD, flash_radius=1.4), run_time=0.6)
        self.pad_to(scene_T(SID))

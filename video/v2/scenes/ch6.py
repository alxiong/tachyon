"""Chapter 6 — Landing: consensus and aggregation (scenes 6.1, 6.2).

6.1 explains the two-epoch duplicate window through the grace-period double spend:
spend A targets epoch 9 but is held into epoch 10; spend B targets epoch 10 with an
honest proof. Single nullifiers miss; adjacent pairs collide; the window catches the
pushed-further variant.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style import *  # noqa: E402,F403
from style import _norm  # noqa: E402

ACC_ACT = '"acc"^"act"'
ACC_TG = '"acc"^"tg"'


def WEND(sid, phrase, occ=1):
    """End time (s) of the last word of `phrase`: where a held pause after it begins."""
    t = anchor(sid, phrase, occ)
    n = len([w for w in re.split(r"[\s\-]+", phrase.split("|")[0]) if _norm(w)])
    ws = WORDS[sid]
    i = next(k for k, x in enumerate(ws) if abs(x["s"] - t) < 1e-6)
    got = 0
    while True:
        got += max(1, len([q for q in re.split(r"[\s\-]+", ws[i]["w"]) if _norm(q)]))
        if got >= n:
            return ws[i]["e"]
        i += 1


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
        anims = [LaggedStart(FadeOut(self.title, shift=0.2 * UP), FadeIn(new, shift=0.2 * UP), lag_ratio=0.85)]
        self.title = new
        return anims

    def construct(self):
        SID = "6.1"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731
        self.wait(0.3)

        # --- the validator's four checks --------------------------------------------------------
        self.title = scene_title("What's left for the validator")
        self.pad_to(A("validator") - 0.3)
        self.play(Write(self.title), run_time=1.0)
        st = action_stamp(("spend", "spend", "output", "output")).move_to(RIGHT * 4.3 + UP * 0.1)
        self.pad_to(A("each stamp") - 0.1)
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
        self.pad_to(A("current epoch") - 0.1)
        cl = VGroup(label("preceding", size=FS_SMALL, color=FLARE).move_to(rail.center_of(8, dy=WH - 0.25)),
                    label("current", size=FS_SMALL, color=FLARE).move_to(rail.center_of(9, dy=WH - 0.25)))
        self.play(FadeIn(cl, lag_ratio=0.4), run_time=0.8)
        self.pad_to(A("candidates") - 0.3)
        queue = VGroup(*[tg_chip('"tg"', color=STAR, size=FS_SMALL) for _ in range(3)]).arrange(RIGHT, buff=0.15)
        queue.move_to(rail.center_of(10, dy=2.2))
        ql = label("candidates, in order", size=FS_SMALL, color=MUT).next_to(queue, UP, buff=0.12)
        self.play(FadeIn(queue, lag_ratio=0.2), FadeIn(ql), run_time=0.6)
        slots = [rail.center_of(9, dy=1.6) + LEFT * 0.62 + RIGHT * 0.62 * k for k in range(3)]
        self.pad_to(A("each one is checked") - 0.1)
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
        self.pad_to(A("the first one targets") - 0.2)
        self.play(FadeIn(cardA, shift=0.2 * DOWN), run_time=0.6)
        self.pad_to(A("held back") - 0.2)
        hold = label("held back", size=FS_SMALL, color=STAR).next_to(cardA, DOWN, buff=0.12)
        self.play(FadeIn(hold), run_time=0.4)
        landA = Dot(R.center_of(10) + LEFT * 0.45, radius=0.11).set_fill(STAR, 1)
        pathA = VGroup()
        labA = tag_chip("A", STAR).next_to(landA, UP, buff=0.12)
        self.pad_to(A("ten begins") - 0.3)
        self.play(FadeOut(grace_lab), FadeIn(landA, scale=2),
                  TransformFromCopy(cardA.frame, labA[0]), FadeIn(labA[1]), run_time=0.9)

        self.pad_to(A("the second one targets") - 0.2)
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
        self.pad_to(A("the second would") - 0.2)
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
        # pause: the two spends' tokens collide on ten
        self.pad_to(WEND(SID, "collide on ten"))
        self.play(FadeIn(caught, shift=0.1 * UP),
                  Flash(hitA.get_center() + DOWN * 0.31, color=FLARE, flash_radius=0.8, line_length=0.25),
                  VGroup(hitA, hitB).animate.scale(1.15), rate_func=there_and_back, run_time=0.9)

        # push further: B held to epoch 11 -> the window
        self.pad_to(A("the window") - 0.3)
        self.play(FadeOut(VGroup(pA, pB, caught, world)),
                  *self.retitle("And the window?"), run_time=0.7)
        self.pad_to(A("push one step") - 0.2)
        landB2 = Dot(R.center_of(11), radius=0.11).set_fill(AMBER, 1)
        pathB2 = VGroup()
        labB = tag_chip("B", AMBER).next_to(landB2, UP, buff=0.12)
        self.pad_to(A("until epoch eleven") - 0.2)
        self.play(ReplacementTransform(landB, landB2), ReplacementTransform(tagB, labB), run_time=0.9)
        self.pad_to(A("now the colliding") - 0.2)
        cA = pairA.chips[1].copy()
        cB = pairB.chips[0].copy()
        self.play(cA.animate.move_to(R.center_of(10, dy=1.05)), cB.animate.move_to(R.center_of(11, dy=1.05)),
                  run_time=0.8)
        self.pad_to(A("a window over") - 0.2)
        W2 = Rectangle(width=2 * R.seg - 0.1, height=2.0).set_stroke(FLARE, SW_BOLD).set_fill(FLARE, 0.05)
        W2.move_to((R.center_of(9) + R.center_of(10)) / 2 + UP * 1.05)
        self.play(ShowCreation(W2), run_time=0.6)
        # epoch 11 is current: the window slides to (10, 11)
        self.pad_to(A("the current and") - 0.1)
        W2l = VGroup(label("preceding", size=FS_SMALL, color=FLARE).move_to(R.center_of(10, dy=1.85)),
                     label("current", size=FS_SMALL, color=FLARE).move_to(R.center_of(11, dy=1.85)))
        self.play(W2.animate.shift(RIGHT * R.seg), FadeIn(W2l, lag_ratio=0.3), run_time=0.8)
        self.pad_to(A("holds both") - 0.2)
        link = Line(cA.get_right(), cB.get_left(), stroke_color=FLARE, stroke_width=SW)
        self.play(ShowCreation(link), run_time=0.5)
        self.pad_to(A("catches it") - 0.1)
        self.play(cA.animate.set_color(FLARE), cB.animate.set_color(FLARE), W2.animate.set_fill(FLARE, 0.12),
                  run_time=0.4)
        # pause: the window catches the collision
        self.pad_to(WEND(SID, "catches it"))
        gotcha = label("caught", size=FS_LABEL, color=FLARE).next_to(W2, UP, buff=0.12)
        self.play(Flash(link.get_center(), color=FLARE, flash_radius=0.7, line_length=0.25),
                  FadeIn(gotcha, scale=1.3), run_time=0.8)
        self.pad_to(A("anything older") - 0.2)
        old = Rectangle(width=R.gate(10).get_center()[0] - (R.x0 - 0.3), height=0.26)
        old.set_fill(GOLD, 0.25).set_stroke(GOLD, SW_THIN)
        old.move_to([(R.gate(10).get_center()[0] + R.x0 - 0.3) / 2, R.y + 0.4, 0])
        old_lab = label("older: already proven excluded", size=FS_LABEL, color=GOLD)
        old_lab.next_to(old, UP, buff=0.12).align_to(old, LEFT)
        self.play(GrowFromEdge(old, LEFT), FadeIn(old_lab), run_time=0.8)

        # a set
        self.pad_to(A("so together") - 0.3)
        stage = VGroup(pairA, pairB, landA, pathA, labA, landB2, pathB2, labB, cA, cB, link, W2, W2l, gotcha, old, old_lab)
        self.play(FadeOut(stage), *self.retitle("They work as a set"), run_time=0.7)
        p1 = VGroup(nf_chip("e", GOLD, FS_BODY), nf_chip("e+1", GOLD, FS_BODY)).arrange(RIGHT, buff=0.12)
        p1l = label("adjacent pair", size=FS_LABEL, color=GOLD).next_to(p1, DOWN, buff=0.2)
        plus = mtex("+", size=FS_HEAD, color=STAR)
        w1 = VGroup(*[Rectangle(width=1.1, height=0.8).set_stroke(FLARE, SW).set_fill(FLARE, 0.06) for _ in range(2)])
        w1.arrange(RIGHT, buff=0)
        w1l = label("two-epoch window", size=FS_LABEL, color=FLARE).next_to(w1, DOWN, buff=0.2)
        setg = VGroup(VGroup(p1, p1l), plus, VGroup(w1, w1l)).arrange(RIGHT, buff=0.8).move_to(UP * 0.4 + LEFT * 0.0)
        self.play(FadeIn(setg, lag_ratio=0.3), run_time=0.9)
        self.pad_to(A("close the gap") - 0.2)
        gapl = label("close the gap the grace period opened", size=FS_BODY, color=GOLD).next_to(setg, DOWN, buff=0.6)
        self.play(FadeIn(gapl, shift=0.1 * UP), run_time=0.7)

        # --- callback: the set consensus must hold ---------------------------------------------------
        self.pad_to(A("and consensus now") - 0.3)
        big = VGroup(*[Square(0.13).set_stroke(width=0).set_fill(FLARE, 0.5) for _ in range(18 * 34)])
        big.arrange_in_grid(18, 34, buff=0.035).move_to(LEFT * 2.2 + DOWN * 0.3)
        big_lab = label("all of history (the prologue's set)", size=FS_LABEL, color=MUT).next_to(big, DOWN, buff=0.2)
        small = VGroup(*[Square(0.13).set_stroke(width=0).set_fill(FLARE, 0.85) for _ in range(18 * 2)])
        small.arrange_in_grid(18, 2, buff=0.035).move_to(RIGHT * 4.6 + DOWN * 0.3)
        small_lab = label("two epochs", size=FS_LABEL, color=FLARE).next_to(small, DOWN, buff=0.2)
        self.play(FadeOut(VGroup(setg, gapl, R, R_w, snt)), *self.retitle("The set consensus holds"), run_time=0.9)
        self.pad_to(A("two epochs") - 0.2)
        self.play(FadeIn(small, lag_ratio=0.02), FadeIn(small_lab), run_time=0.7)
        self.pad_to(A("instead of all") - 0.2)
        self.play(FadeIn(big, lag_ratio=0.0005), FadeIn(big_lab), run_time=0.9)
        # pause: the two-epoch grid beside the original from the prologue
        self.pad_to(WEND(SID, "all of history"))
        bnd = label("bounded, forever", size=FS_BODY, color=GOLD).next_to(small, UP, buff=0.3)
        self.play(big.animate.fade(0.6), FadeIn(bnd, shift=0.1 * DOWN), small.animate.set_fill(FLARE, 1.0),
                  run_time=0.8)
        self.pad_to(scene_T(SID))




# ===================================================================================================
# Aggregation (6.2 life cycle, 6.3 what it buys). Vocabulary: a stamp is a "slab" (the 2.2 stamp card
# reduced to its silhouette: frame, proof token, tachygram pouch); a transaction body is a small grey
# card with two signature seals. StampLift / StampMerge reuse the 5.2 step pills.
# ===================================================================================================
SLAB_W, SLAB_H, BODY_H = 0.82, 0.7, 0.32


def slab(w=SLAB_W, h=SLAB_H, color=STAR, fill=0.10):
    """A stamp slab: frame + proof token + two-slot tachygram pouch."""
    k = h / SLAB_H
    fr = RoundedRectangle(width=w, height=h, corner_radius=0.1 * k)
    fr.set_stroke(color, SW if k > 0.6 else SW_THIN, 0.95).set_fill(color, fill)
    tok = proof_token(0.085 * k).move_to(fr.get_center() + UP * 0.1 * h)
    tok[0].set_stroke(width=2.5 * max(k, 0.5))
    pouch = VGroup(*[RoundedRectangle(width=0.27 * w, height=0.15 * h, corner_radius=0.025 * k)
                     .set_stroke(color, 1.4, 0.75).set_fill(color, 0.06) for _ in range(2)])
    pouch.arrange(RIGHT, buff=0.08 * w).move_to(fr.get_center() + DOWN * 0.28 * h)
    g = VGroup(fr, tok, pouch)
    g.frame, g.tok, g.pouch = fr, tok, pouch
    return g


def tx_body(w=SLAB_W, h=BODY_H):
    """A transaction body: effecting data + signatures (the two gold seals)."""
    box = RoundedRectangle(width=w, height=h, corner_radius=0.06).set_stroke(TXT, SW_THIN, 0.9).set_fill(TXT, 0.08)
    seals = VGroup(*[Circle(radius=0.055).set_stroke(GOLD, 1.6).set_fill(GOLD, 0.35) for _ in range(2)])
    seals.arrange(RIGHT, buff=0.1 * w).move_to(box)
    g = VGroup(box, seals)
    g.box, g.seals = box, seals
    return g


def bundle():
    """A standalone bundle: its own stamp slab riding on the transaction body."""
    s_, b_ = slab(), tx_body()
    b_.next_to(s_, DOWN, buff=0.05)
    g = VGroup(s_, b_)
    g.slab, g.body = s_, b_
    return g


def ref_stub(w=0.5, h=0.15):
    """The reference a covered transaction keeps in place of its stamp."""
    return RoundedRectangle(width=w, height=h, corner_radius=0.05).set_stroke(GOLD, 1.8).set_fill(GOLD, 0.45)


def sig_seal2(color=GOLD, r=0.22):
    c = Circle(radius=r).set_fill(color, 0.15).set_stroke(color, SW_THIN)
    t = mtex("sigma", size=FS_LABEL, color=color).move_to(c)
    return VGroup(c, t)


def lamp_row(text_mob):
    lamp = Circle(radius=0.16).set_stroke(DIM, SW_THIN).set_fill(GOLD, 0)
    row = VGroup(lamp, text_mob)
    text_mob.next_to(lamp, RIGHT, buff=0.3)
    lamp.match_y(text_mob)
    row.lamp, row.text = lamp, text_mob
    return row


def pulse(mob, s=1.12):
    """Scale there-and-back (an Indicate that never recolours chips or panels)."""
    return mob.animate.scale(s).set_anim_args(rate_func=there_and_back)


def lit(row):
    return row.lamp.animate.set_fill(GOLD, 0.9).set_stroke(GOLD, SW_THIN)


def counter_anim(holder, digits, pos, aligned=ORIGIN, rate=smooth):
    def tick(m, a):
        k = min(int(rate(a) * (len(digits) - 1) + 0.5), len(digits) - 1)
        m.become(digits[k].copy().move_to(pos, aligned_edge=aligned))
    return UpdateFromAlphaFunc(holder, tick)


def edge(child, parent, opacity=0.55):
    return Line(child.get_top(), parent.get_bottom(), stroke_color=STAR, stroke_width=SW_THIN,
                stroke_opacity=opacity)


def merge_anims(c1, c2, parent, edges):
    """StampMerge, drawn: the two children's copies fly up and fuse into the parent slab."""
    return [LaggedStart(AnimationGroup(FadeOut(c1.copy(), shift=parent.get_center() - c1.get_center()),
                                       FadeOut(c2.copy(), shift=parent.get_center() - c2.get_center())),
                        FadeIn(parent, scale=0.7), lag_ratio=0.45),
            *[ShowCreation(e) for e in edges]]


def tree_layout(n_leaves, x0, x1, y0, dy, w, h):
    """Binary merge tree: levels[0] = leaves ... levels[-1] = [root]; edges[l] connect level l to l+1."""
    xs = list(np.linspace(x0, x1, n_leaves))
    levels, edges = [], []
    y = y0
    while True:
        lvl = VGroup(*[slab(w, h, fill=0.22 if len(xs) == 1 else 0.10).move_to([x, y, 0]) for x in xs])
        levels.append(lvl)
        if len(xs) == 1:
            break
        xs = [(xs[2 * i] + xs[2 * i + 1]) / 2 for i in range(len(xs) // 2)]
        y += dy
    for l in range(len(levels) - 1):
        edges.append(VGroup(*[edge(levels[l][2 * i + j], levels[l + 1][i]) for i in range(len(levels[l + 1]))
                              for j in (0, 1)]))
    return levels, edges


# ---- 6.2 layout (block phase), shared with final62() ------------------------------------------------
BLK_Y = 1.3
AGG_X = -5.25
BX = [-3.85 + 1.33 * k for k in range(8)]
BUS_Y = 1.98


def block62():
    frame = RoundedRectangle(width=12.7, height=2.15, corner_radius=0.18).set_stroke(STAR, SW, 0.8)
    frame.set_fill(STAR, 0.03).move_to([0, 1.42, 0])
    blab = label("block", size=FS_LABEL, color=STAR).move_to([5.75, 2.22, 0])
    agg = slab(fill=0.22).move_to([AGG_X, BLK_Y, 0])
    wt = mtex('"wtxid"_"agg"', size=FS_LABEL, color=GOLD).move_to([AGG_X, BUS_Y, 0])
    bundles = VGroup(*[bundle().move_to([x, BLK_Y, 0]) for x in BX])
    refs = VGroup(*[ref_stub().move_to([b.body.get_x(), b.body.get_top()[1] + 0.16, 0]) for b in bundles])
    ticks = VGroup(*[Line(r.get_top(), [r.get_x(), BUS_Y, 0], stroke_color=GOLD, stroke_width=1.8,
                          stroke_opacity=0.8) for r in refs])
    bus = tarrow([BX[-1], BUS_Y, 0], wt.get_right() + RIGHT * 0.05, color=GOLD, width=1.8, tip=0.16, buff=0)
    return dict(frame=frame, blab=blab, agg=agg, wt=wt, bundles=bundles, refs=refs, ticks=ticks, bus=bus)


def checklist62():
    rows = VGroup(
        lamp_row(label("the tachygrams are distinct", size=FS_BODY, color=TXT)),
        lamp_row(label("its coverage matches the transactions pointing at it", size=FS_BODY, color=TXT)),
        lamp_row(rich([("one", TXT), ("aggregated", GOLD), ("proof verifies", TXT)], size=FS_BODY)),
    ).arrange(DOWN, buff=0.36, aligned_edge=LEFT)
    rows.move_to([-0.6, -1.35, 0])
    return rows


def final62():
    """Last frame of 6.2, rebuilt exactly (6.3 opens on it)."""
    b = block62()
    rows = checklist62()
    for r in rows:
        r.lamp.set_fill(GOLD, 0.9).set_stroke(GOLD, SW_THIN)
    title = scene_title("Validating an aggregate")
    bodies = VGroup(*[x.body for x in b["bundles"]])
    return title, b, bodies, rows


class Scene62(TimedScene):
    def swap_title(self, text):
        new = scene_title(text)
        old, self.title = self.title, new
        return LaggedStart(FadeOut(old, shift=0.2 * UP), FadeIn(new, shift=0.2 * UP), lag_ratio=0.85)

    def construct(self):
        SID = "6.2"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731
        W = lambda p, o=1: WEND(SID, p, o)  # noqa: E731
        self.wait(0.3)
        self.title = scene_title("From many stamps to one")
        self.pad_to(A("so far") - 0.2)
        self.play(Write(self.title), run_time=1.0)

        # --- standalone vs aggregate bundle ----------------------------------------------------------
        one = bundle().scale(1.9).move_to([-3.6, 0.2, 0])
        one_l = label("standalone bundle", size=FS_BODY, color=TXT).next_to(one, DOWN, buff=0.3)
        self.pad_to(A("standalone bundle") - 0.2)
        self.play(FadeIn(one, shift=0.2 * UP), FadeIn(one_l), run_time=0.8)
        own = label("its own stamp", size=FS_LABEL, color=STAR).next_to(one.slab, RIGHT, buff=0.4)
        self.pad_to(A("its own stamp") - 0.2)
        self.play(FadeIn(own, shift=0.1 * LEFT), pulse(one.slab, 1.08), run_time=0.6)

        many = VGroup(*[bundle() for _ in range(4)]).arrange(RIGHT, buff=0.22).move_to([-3.6, 0.35, 0])
        many_l = label("standalone bundles", size=FS_BODY, color=TXT).next_to(many, DOWN, buff=0.35)
        self.pad_to(A("aggregation turns") - 0.2)
        self.play(ReplacementTransform(one, many[0]), FadeIn(many[1:], lag_ratio=0.2), FadeOut(own),
                  LaggedStart(FadeOut(one_l), FadeIn(many_l), lag_ratio=0.8), run_time=0.9)
        ab_bodies = VGroup(*[tx_body() for _ in range(4)]).arrange(RIGHT, buff=0.12)
        ab_slab = slab(fill=0.22)
        ab = VGroup(ab_slab, ab_bodies).arrange(RIGHT, buff=0.25, aligned_edge=DOWN).move_to([3.6, 0.35, 0])
        ab_l = label("aggregate bundle", size=FS_BODY, color=STAR).next_to(ab, DOWN, buff=0.35).match_y(many_l)
        arr = tarrow(many.get_right() + RIGHT * 0.1, ab.get_left() + LEFT * 0.1, color=MUT, width=SW)
        self.pad_to(A("aggregate bundle") - 0.3)
        self.play(ShowCreation(arr), TransformFromCopy(VGroup(*[m.body for m in many]), ab_bodies),
                  *[FadeOut(m.slab.copy(), shift=ab_slab.get_center() - m.slab.get_center(), scale=0.6)
                    for m in many],
                  FadeIn(ab_slab), FadeIn(ab_l), run_time=1.0)
        self.pad_to(A("single stamp") - 0.1)
        self.play(ab_slab.animate.scale(1.15), rate_func=there_and_back, run_time=0.5)
        self.play(Flash(ab_slab.get_center(), color=STAR, flash_radius=0.6), run_time=0.4)

        # pause: standalone bundles stream into the mempool, each with its own stamp
        lane = RoundedRectangle(width=13.2, height=1.75, corner_radius=0.2).set_stroke(DIM, SW_THIN, 0.9)
        lane.set_fill(DIM, 0.04).move_to([0, 0.75, 0])
        mp_l = label("mempool", size=FS_LABEL, color=MUT).next_to(lane, UP, buff=0.1).align_to(lane, LEFT).shift(RIGHT * 0.2)
        pool = VGroup(*[bundle().move_to([-5.85 + 1.3 * k, 0.75, 0]) for k in range(10)])
        self.pad_to(W("single stamp"))
        self.play(FadeOut(VGroup(many, many_l, arr, ab, ab_l)), FadeIn(lane), FadeIn(mp_l),
                  LaggedStart(*[FadeIn(b, shift=RIGHT * 1.2) for b in pool], lag_ratio=0.12), run_time=1.1)

        # --- the life cycle --------------------------------------------------------------------------
        self.pad_to(A("life cycle") - 0.4)
        self.play(self.swap_title("The life cycle"), run_time=0.8)
        wal = VGroup(*[Dot([b.get_x(), -0.75, 0], radius=0.09).set_fill(GOLD, 1) for b in pool])
        wal_a = VGroup(*[tarrow(d.get_top(), b.get_bottom(), color=GOLD, width=SW_THIN, opacity=0.8)
                         for d, b in zip(wal, pool)])
        wal_l = label("wallets", size=FS_LABEL, color=GOLD).move_to([0, -1.2, 0])
        self.pad_to(A("wallets publishing") - 0.2)
        self.play(LaggedStart(*[FadeIn(d, scale=2) for d in wal], lag_ratio=0.06),
                  LaggedStart(*[ShowCreation(a) for a in wal_a], lag_ratio=0.06), FadeIn(wal_l), run_time=0.9)
        aggr = pill("aggregator", color=TXT).move_to([0, -1.25, 0])
        self.pad_to(A("an aggregator") - 0.1)
        self.play(FadeOut(VGroup(wal, wal_a, wal_l)), FadeIn(aggr, scale=0.8), run_time=0.7)
        picked = [0, 1, 3, 4, 5, 6, 8, 9]
        unp = VGroup(pool[2], pool[7])
        picks = VGroup(*[tarrow(pool[k].get_bottom(), aggr.get_top(), color=MUT, width=1.8, opacity=0.8) for k in picked])
        self.pad_to(A("picks") - 0.1)
        self.play(LaggedStart(*[ShowCreation(p) for p in picks], lag_ratio=0.05), unp.animate.fade(0.7),
                  run_time=0.8)
        B = VGroup(*[pool[k] for k in picked])
        X8 = [-5.25 + 1.5 * k for k in range(8)]
        self.pad_to(A("combines") - 0.1)
        self.play(FadeOut(picks), FadeOut(unp), *[b.animate.move_to([x, 0.75, 0]) for b, x in zip(B, X8)],
                  run_time=0.8)

        # anyone can aggregate; relay
        npos = [(-5.0, -1.9), (-3.2, -2.55), (-1.7, -1.85), (1.7, -1.9), (3.3, -2.55), (5.0, -1.85), (0, -2.6)]
        nodes = VGroup(*[Circle(radius=0.13).set_stroke(TXT, SW_THIN, 0.8).set_fill(TXT, 0.1).move_to([x, y, 0])
                         for x, y in npos])
        links = [(0, 1), (1, 2), (2, 6), (6, 4), (4, 3), (3, 5), (2, 3)]
        net = VGroup(*[Line(nodes[i].get_center(), nodes[j].get_center(), buff=0.13, stroke_color=TXT,
                            stroke_width=1.6, stroke_opacity=0.5) for i, j in links])
        net.add(Line(aggr.get_bottom(), nodes[6].get_top(), stroke_color=TXT, stroke_width=1.6, stroke_opacity=0.5))
        anyone = label("anyone can aggregate", size=FS_LABEL, color=MUT).move_to([-4.3, -1.15, 0])
        self.pad_to(A("anyone can aggregate") - 0.3)
        self.play(FadeIn(nodes, lag_ratio=0.1), ShowCreation(net), FadeIn(anyone), run_time=0.9)
        m1 = slab(0.36, 0.3).move_to(nodes[0])
        m2 = slab(0.36, 0.3).move_to(nodes[5])
        path1 = VMobject().set_points_as_corners([nodes[0].get_center(), nodes[1].get_center(),
                                                  nodes[2].get_center(), nodes[3].get_center()])
        self.pad_to(A("relayed") - 0.1)
        self.add(m1)
        self.play(MoveAlongPath(m1, path1), run_time=0.7)
        self.pad_to(A("merged again") - 0.1)
        self.play(FadeIn(m2), m2.animate.move_to(nodes[3]), run_time=0.4)
        self.play(FadeOut(m2, scale=0.5), Flash(nodes[3].get_center(), color=STAR, flash_radius=0.35), run_time=0.4)
        miner = pill("miner", color=TXT).move_to(aggr)
        self.pad_to(A("a miner") - 0.2)
        self.play(LaggedStart(FadeOut(aggr), FadeIn(miner), lag_ratio=0.8),
                  VGroup(nodes, net, m1, anyone).animate.fade(0.7), run_time=0.7)
        inc = boxed(rich([("incentive:", TXT), ("more transactions, more fees", GOLD)], size=FS_LABEL),
                    color=TXT, pad=0.16).move_to([3.4, -1.25, 0])
        self.pad_to(A("incentive") - 0.2)
        self.play(FadeIn(inc, shift=0.1 * LEFT), run_time=0.6)
        self.pad_to(A("every byte") - 0.1)
        self.play(*[b.slab.frame.animate.set_stroke(FLARE, SW_BOLD) for b in B], rate_func=there_and_back,
                  run_time=0.8)
        self.pad_to(A("more fees") - 0.1)
        self.play(inc.animate.scale(1.08), rate_func=there_and_back, run_time=0.5)
        only = label("the only aggregator here", size=FS_SMALL, color=MUT)
        miner_t = miner.copy().move_to([5.6, 2.3, 0])
        only.next_to(miner_t, LEFT, buff=0.25)
        self.pad_to(A("only aggregator") - 0.3)
        self.play(FadeOut(VGroup(nodes, net, m1, anyone, inc)), miner.animate.move_to(miner_t), FadeIn(only),
                  run_time=0.9)

        # --- lift to a common anchor -------------------------------------------------------------------
        RY = -2.3
        now_x, CX = 4.6, 4.2
        g9 = sentinel_gate(h=0.8).move_to([-6.2, RY, 0])
        g10 = sentinel_gate(h=0.8).move_to([6.2, RY, 0]).fade(0.5)
        chain = Line([-6.2, RY, 0], [now_x, RY, 0], stroke_color=STAR, stroke_width=SW, stroke_opacity=0.7)
        future = DashedLine([now_x, RY, 0], [6.2, RY, 0], dash_length=0.1).set_stroke(DIM, SW_THIN)
        tx_ = list(np.linspace(-5.7, 4.2, 12))
        ticks = VGroup(*[Dot([x, RY, 0], radius=0.06).set_fill(STAR, 0.9) for x in tx_])
        l9 = mtex('"sntl"_9', size=FS_LABEL, color=STAR).next_to(g9, DOWN, buff=0.1).shift(RIGHT * 0.35)
        l10 = mtex('"sntl"_10', size=FS_LABEL, color=MUT).next_to(g10, DOWN, buff=0.1).shift(LEFT * 0.35)
        nowm = Triangle().set_fill(FLARE, 1).set_stroke(width=0).scale(0.11).rotate(PI).move_to([now_x, RY + 0.28, 0])
        now_l = label("now", size=FS_SMALL, color=FLARE).next_to(nowm, RIGHT, buff=0.1)
        ep = label("epoch 9 anchor chain", size=FS_SMALL, color=MUT).move_to([-1.0, RY - 0.45, 0])
        rail = VGroup(chain, future, g9, g10, ticks, l9, l10, nowm, now_l, ep)
        self.pad_to(A("the first thing") - 0.1)
        self.play(self.swap_title("Lift to a common anchor"), FadeIn(rail, lag_ratio=0.05), run_time=0.9)
        AX = [tx_[i] for i in (0, 1, 3, 4, 6, 7, 9, 10)]

        def marker(x, color=STAR):
            return Triangle().set_fill(color, 1).set_stroke(width=0).scale(0.1).rotate(PI).move_to([x, RY + 0.2, 0])
        marks = VGroup(*[marker(x) for x in AX])
        legs = VGroup(*[DashedLine(b.get_bottom(), m.get_top(), dash_length=0.07).set_stroke(MUT, 1.8)
                        for b, m in zip(B, marks)])
        self.pad_to(A("different anchors") - 0.2)
        self.play(LaggedStart(*[FadeIn(m, shift=0.15 * DOWN) for m in marks], lag_ratio=0.08),
                  LaggedStart(*[ShowCreation(l) for l in legs], lag_ratio=0.08), run_time=0.9)
        lift = step_pill("StampLift", GOLD).move_to([5.45, -0.95, 0])
        self.pad_to(A("lifts each") - 0.2)
        self.play(FadeIn(lift, scale=0.8), run_time=0.5)
        cdot = Dot([CX, RY, 0], radius=0.11).set_fill(GOLD, 1)
        cl = label("common anchor", size=FS_SMALL, color=GOLD).move_to([CX - 0.5, RY - 0.45, 0])
        self.pad_to(A("single common anchor") - 0.1)
        self.play(FadeIn(cdot, scale=2), FadeIn(cl), run_time=0.5)
        self.pad_to(A("same spending epoch") - 0.1)
        self.play(chain.animate.set_stroke(STAR, SW_BOLD, 1.0), rate_func=there_and_back, run_time=0.8)
        ghost = marker(CX, FLARE)
        self.pad_to(A("never across") - 0.3)
        self.play(FadeIn(ghost), run_time=0.2)
        self.play(ghost.animate.move_to([6.3, RY + 0.2, 0]), rate_func=there_and_back, run_time=0.7)
        self.play(FadeOut(ghost), Flash(g10.get_top(), color=FLARE, flash_radius=0.3), run_time=0.4)
        self.pad_to(A("stamplift step") - 0.2)
        self.play(lift.animate.scale(1.12), rate_func=there_and_back, run_time=0.6)
        # pause: stamps slide to a common anchor
        legs2 = VGroup(*[DashedLine(b.get_bottom(), [CX, RY + 0.3, 0], dash_length=0.07).set_stroke(GOLD, 1.8)
                         for b in B])
        self.pad_to(W("as before"))
        self.play(*[m.animate.move_to([CX, RY + 0.2, 0]) for m in marks], ReplacementTransform(legs, legs2),
                  run_time=1.0)
        par = label("no lift depends on another: all in parallel", size=FS_LABEL, color=GOLD).move_to([-1.3, -1.0, 0])
        self.pad_to(A("no lift") - 0.1)
        self.play(FadeOut(legs2), FadeIn(par), run_time=0.6)
        self.pad_to(A("all run") - 0.1)
        self.play(*[Flash(b.slab.get_center(), color=GOLD, flash_radius=0.5, line_length=0.15) for b in B],
                  run_time=0.8)

        # --- merge up a binary tree -----------------------------------------------------------------------
        levels, edges = tree_layout(8, -5.25, 5.25, -1.35, 1.1, SLAB_W, SLAB_H)
        L0 = levels[0]
        RB = 0.8
        row_t = [np.array([-4.2 + 1.2 * k, -2.45, 0]) for k in range(8)]
        self.pad_to(A("share an anchor") - 0.3)
        self.play(self.swap_title("Merge up a binary tree"),
                  FadeOut(VGroup(rail, marks, cdot, cl, lift, par, lane, mp_l, miner, only)),
                  *[b.animate.scale(RB).move_to(p) for b, p in zip(B, row_t)], run_time=0.9)
        self.pad_to(A("merge them") - 0.2)
        self.play(*[TransformFromCopy(b.slab, l) for b, l in zip(B, L0)], run_time=0.8)

        # StampMerge in detail on the first pair
        def card(chips, n=2, w=3.4):
            c = stamp_card(n_slots=n, w=w).scale(0.8)
            ch = VGroup(*[tg_chip(t, color=STAR, size=FS_LABEL + 2).scale(0.8).move_to(s)
                          for t, s in zip(chips, c.slots)])
            tok = proof_token(0.1).next_to(c.title, RIGHT, buff=0.25)
            g = VGroup(c, ch, tok)
            g.card, g.chips, g.ptok = c, ch, tok
            return g
        cA = card(['"tg"_1', '"tg"_2']).move_to([-4.55, 0.6, 0])
        cB = card(['"tg"_3', '"tg"_4']).move_to([-1.35, 0.6, 0])
        out = stamp_card(n_slots=4, w=3.4).scale(0.8).move_to([4.55, 0.6, 0])
        otok = proof_token(0.1).next_to(out.title, RIGHT, buff=0.25)
        mp = step_pill("StampMerge", GOLD).move_to([1.2, 0.6, 0])
        a1 = tarrow(cB.get_right(), mp.get_left(), color=MUT)
        a2 = tarrow(mp.get_right(), out.get_left(), color=MUT)
        self.pad_to(A("takes two stamps") - 0.2)
        self.play(FadeOut(L0[2:]), FadeOut(B),
                  GrowFromPoint(cA, L0[0].get_center()), GrowFromPoint(cB, L0[1].get_center()),
                  FadeIn(mp, scale=0.8), ShowCreation(a1), run_time=0.9)
        self.pad_to(A("returns one") - 0.2)
        self.play(FadeIn(VGroup(out.frame, out.title, out.pis, out.slots)), ShowCreation(a2), run_time=0.6)
        self.pad_to(A("unions") - 0.2)
        chips = VGroup(*cA.chips, *cB.chips)
        self.play(*[c.animate.move_to(s) for c, s in zip(chips, out.slots)], run_time=0.8)
        mul = mtex(f'{ACC_TG} = {ACC_TG}_1 dot {ACC_TG}_2', size=FS_LABEL, color=GOLD).next_to(out, DOWN, buff=0.3)
        self.pad_to(A("multiplies") - 0.2)
        self.play(FadeIn(mul, shift=0.1 * UP), out.pis.animate.set_color(GOLD), run_time=0.7)
        self.pad_to(A("fuses") - 0.2)
        self.play(FadeOut(cA.ptok, shift=otok.get_center() - cA.ptok.get_center()),
                  FadeOut(cB.ptok, shift=otok.get_center() - cB.ptok.get_center()), FadeIn(otok, scale=0.6),
                  run_time=0.7)
        n10 = levels[1][0]
        outg = VGroup(out, chips, otok)
        self.play(FadeOut(VGroup(cA.card, cB.card, mp, a1, a2, mul)),
                  FadeOut(outg, shift=n10.get_center() - outg.get_center(), scale=0.25),
                  FadeIn(n10, scale=0.6), ShowCreation(edges[0][0]), ShowCreation(edges[0][1]),
                  FadeIn(L0[2:]), FadeIn(B), run_time=1.0)
        self.pad_to(A("pair the stamps") - 0.2)
        anims = []
        for i in (1, 2, 3):
            anims += merge_anims(L0[2 * i], L0[2 * i + 1], levels[1][i], [edges[0][2 * i], edges[0][2 * i + 1]])
        self.play(*anims, run_time=0.8)
        self.pad_to(A("pair the results") - 0.2)
        anims = []
        for i in (0, 1):
            anims += merge_anims(levels[1][2 * i], levels[1][2 * i + 1], levels[2][i],
                                 [edges[1][2 * i], edges[1][2 * i + 1]])
        self.play(*anims, run_time=0.8)
        self.pad_to(A("binary tree") - 0.2)
        self.play(*[e.animate.set_stroke(STAR, SW, 1.0) for e in (*edges[0], *edges[1])],
                  rate_func=there_and_back, run_time=0.6)
        # pause: the merge tree folds up to a single stamp
        root = levels[3][0]
        agl = label("aggregate stamp", size=FS_LABEL, color=STAR).next_to(root, RIGHT, buff=0.3)
        self.pad_to(W("one stamp left"))
        self.play(*merge_anims(levels[2][0], levels[2][1], root, list(edges[2])), FadeIn(agl), run_time=1.0)

        # --- overlap needs no rule -----------------------------------------------------------------------
        tree = VGroup(*levels[:3], *edges, root)
        p1 = boxed(VGroup(tg_chip('"tg"_3'), tg_chip('"tg"_7')).arrange(RIGHT, buff=0.12), color=STAR, pad=0.14)
        p2 = boxed(VGroup(tg_chip('"tg"_7'), tg_chip('"tg"_9')).arrange(RIGHT, buff=0.12), color=STAR, pad=0.14)
        VGroup(p1, p2).arrange(RIGHT, buff=0.6).move_to([4.0, 1.2, 0])
        ovl = label("two overlapping sets", size=FS_LABEL, color=MUT).next_to(VGroup(p1, p2), UP, buff=0.25)
        self.pad_to(A("consensus refuses") - 0.3)
        self.play(tree.animate.scale(0.6).move_to([-3.0, 0.55, 0]), FadeOut(agl), FadeIn(VGroup(p1, p2, ovl), lag_ratio=0.2),
                  run_time=0.9)
        dup = VGroup(p1[1][1], p2[1][0])
        self.pad_to(A("duplicate tachygrams") - 0.1)
        self.play(dup.animate.set_color(FLARE), *[Flash(d.get_center(), color=FLARE, flash_radius=0.45) for d in dup],
                  run_time=0.6)
        self.pad_to(A("overlapping") - 0.3)
        self.play(p1.animate.move_to([3.15, 0.05, 0]), p2.animate.move_to([4.85, 0.05, 0]), run_time=0.7)
        xm = x_mark(np.array([4.0, 0.05, 0]), size=0.35)
        ref = label("could never land", size=FS_LABEL, color=FLARE).move_to([4.0, -0.85, 0])
        self.pad_to(A("never land") - 0.1)
        self.play(ShowCreation(xm), FadeIn(ref), run_time=0.6)
        norule = label("nothing extra to enforce", size=FS_LABEL, color=GOLD).next_to(ref, DOWN, buff=0.3)
        self.pad_to(A("nothing extra") - 0.1)
        self.play(FadeIn(norule, shift=0.1 * UP), run_time=0.5)

        # --- assembling the block --------------------------------------------------------------------------
        b = block62()
        frame, blab, agg, wt = b["frame"], b["blab"], b["agg"], b["wt"]
        self.pad_to(A("when the miner") - 0.1)
        self.play(self.swap_title("Assembling the block"),
                  FadeOut(VGroup(p1, p2, ovl, xm, ref, norule, *levels[:3], *edges)), run_time=0.9)
        self.pad_to(A("assembles the block") - 0.1)
        self.play(FadeIn(frame), FadeIn(blab), run_time=0.6)
        self.pad_to(A("carries the aggregate") - 0.2)
        self.play(ReplacementTransform(root, agg), FadeIn(wt), run_time=0.8)
        self.pad_to(A("every transaction it") - 0.2)
        self.play(*[bb.animate.scale(1 / RB).move_to(t) for bb, t in zip(B, b["bundles"])], run_time=1.0)
        self.pad_to(A("drops") - 0.15)
        self.play(LaggedStart(*[FadeOut(bb.slab, shift=DOWN * 0.9) for bb in B], lag_ratio=0.05), run_time=0.7)
        self.pad_to(A("points at") - 0.1)
        self.play(LaggedStart(*[FadeIn(r, scale=0.5) for r in b["refs"]], lag_ratio=0.04),
                  LaggedStart(*[ShowCreation(t) for t in b["ticks"]], lag_ratio=0.04),
                  ShowCreation(b["bus"]), run_time=0.8)
        self.pad_to(A("witness transaction") - 0.1)
        self.play(wt.animate.scale(1.15), rate_func=there_and_back, run_time=0.6)
        # pause: each transaction swaps its stamp for a reference
        swp = rich([("each transaction:", TXT), ("stamp", STAR), ("$->$", MUT), ("reference to", TXT),
                    ('$"wtxid"_"agg"$', GOLD)], size=FS_LABEL).move_to(UP * CAPTION_Y)
        self.pad_to(W("id instead"))
        self.play(LaggedStart(*[pulse(r, 1.35) for r in b["refs"]], lag_ratio=0.08),
                  FadeIn(swp, shift=0.1 * UP), run_time=1.0)

        # the 2.2 txid / wtxid split, for one covered transaction
        eff_h = itex("effecting data", size=FS_LABEL, color=STAR)
        eff_f = VGroup(mtex(ACC_ACT, size=FS_LABEL, color=STAR), mtex('v^"bal"', size=FS_LABEL, color=STAR),
                       mtex('"digest"("memo")', size=FS_LABEL, color=STAR)).arrange(RIGHT, buff=0.35)
        eff = boxed(VGroup(eff_h, eff_f).arrange(DOWN, buff=0.2), color=STAR, pad=0.22).move_to([-3.3, -1.35, 0])
        txid = label("txid", size=FS_BODY, color=STAR).next_to(eff, UP, buff=0.1).align_to(eff, LEFT)
        auth_h = itex("authorization data", size=FS_LABEL, color=AMBER)
        seals = VGroup(sig_seal2(), sig_seal2()).arrange(RIGHT, buff=0.2)
        old_st = slab(0.62, 0.5)
        slot = VGroup(seals, old_st).arrange(RIGHT, buff=0.45)
        auth = boxed(VGroup(auth_h, slot).arrange(DOWN, buff=0.2), color=AMBER, pad=0.22).move_to([3.1, -1.35, 0])
        auth.match_y(eff)
        new_ref = ref_stub(0.62, 0.2).move_to(old_st)
        wtf = mtex('"wtxid" = "txid" || "auth_digest"', size=FS_LABEL, color=STAR).move_to([-0.3, -2.62, 0])
        diag = VGroup(eff, txid, auth)
        self.pad_to(A("and that's why") - 0.1)
        self.play(FadeOut(swp), GrowFromPoint(diag, B[0].body.get_center()), run_time=0.9)
        self.pad_to(A("authorization data") - 0.1)
        self.play(auth[0].animate.set_stroke(AMBER, SW_BOLD), auth_h.animate.scale(1.1), rate_func=there_and_back,
                  run_time=0.6)
        self.pad_to(A("swapping") - 0.1)
        self.play(FadeOut(old_st, shift=DOWN * 0.3), FadeIn(new_ref, shift=DOWN * 0.3), run_time=0.6)
        chg = label("changes", size=FS_LABEL, color=AMBER).next_to(wtf, RIGHT, buff=0.3)
        self.pad_to(A("changes the witness") - 0.1)
        self.play(FadeIn(wtf), FadeIn(chg), run_time=0.5)
        self.play(wtf.animate.set_color(AMBER), rate_func=there_and_back, run_time=0.4)
        unch = label("unchanged", size=FS_LABEL, color=STAR).next_to(txid, RIGHT, buff=0.3)
        self.pad_to(A("never the transaction") - 0.1)
        self.play(FadeIn(unch), pulse(txid, 1.15), run_time=0.6)
        oks = VGroup(*[checkmark(0.22, GOLD).next_to(s, UP, buff=0.04) for s in seals])
        self.pad_to(A("every signature") - 0.1)
        self.play(*[ShowCreation(o) for o in oks], *[Flash(s.get_center(), color=GOLD, flash_radius=0.35) for s in seals],
                  run_time=0.6)

        # --- validating an aggregate ------------------------------------------------------------------------
        rows = checklist62()
        self.pad_to(A("on the other end") - 0.3)
        self.play(self.swap_title("Validating an aggregate"),
                  FadeOut(VGroup(diag, new_ref, wtf, chg, unch, oks)), run_time=0.9)
        self.pad_to(A("tachygrams are distinct") - 0.2)
        self.play(FadeIn(rows[0], shift=0.1 * RIGHT), run_time=0.5)
        self.pad_to(A("distinct") - 0.05)
        self.play(lit(rows[0]), run_time=0.4)
        self.pad_to(A("coverage") - 0.3)
        self.play(FadeIn(rows[1], shift=0.1 * RIGHT), run_time=0.5)
        self.pad_to(A("pointing at it") - 0.1)
        self.play(lit(rows[1]), VGroup(b["ticks"], b["bus"], b["refs"]).animate.set_color(STAR)
                  .set_anim_args(rate_func=there_and_back), run_time=0.6)
        self.pad_to(A("one aggregated") - 0.3)
        self.play(FadeIn(rows[2], shift=0.1 * RIGHT), run_time=0.4)
        self.pad_to(A("aggregated") - 0.1)
        self.play(rows[2].text[1].animate.scale(1.15), agg.animate.scale(1.18), rate_func=there_and_back, run_time=0.5)
        self.play(Flash(agg.get_center(), color=STAR, flash_radius=0.7), lit(rows[2]), run_time=0.5)
        self.pad_to(scene_T(SID))


# ---- 6.3: what aggregation buys ------------------------------------------------------------------------
# Numbers (scenes.md 6.3 "Content"; the narration rounds them): step 1.2 s; NU7 block 25 s - 4 s reserved
# = 21 s -> 17 steps = 1 lift + 16 merge levels -> 2^16 = 65,536 tx/block (~2,600/s).
# Proof 7.4 KB; 2-in-2-out tx ~1.15 KB. 2 MB: 2e6 / 8,520 ~ 235 standalone ("about 230");
# (2e6 - 7,400) / 1,150 ~ 1,733 aggregated (~70/s); proof share 7,400 / 1,733 ~ 4.3 B.
# 20 MB: (2e7 - 7,400) / 1,150 ~ 17,385 (~700/s); 1 + 15 = 16 steps, 19.2 s <= 21 s.
# Not modelled (deliberately absent from the budget): the time to compress the final aggregate.
STEP_S, BLOCK_S, RESERVE_S = 1.2, 25.0, 4.0
PROOF_B, TX_B = 7400, 1150
N_STANDALONE = int(2_000_000 / (PROOF_B + TX_B))            # 234
N_AGG_2MB = int((2_000_000 - PROOF_B) / TX_B)              # 1,732
assert int((BLOCK_S - RESERVE_S) / STEP_S) == 17 and 2 ** 16 == 65536
assert 230 <= N_STANDALONE <= 236 and 1700 <= N_AGG_2MB <= 1740
assert 17000 <= int((20_000_000 - PROOF_B) / TX_B) <= 17400 and 16 * STEP_S <= BLOCK_S - RESERVE_S


def tri_levels(n, base=3.0, x=-4.6, y0=-2.6, dy=0.22, color=STAR):
    """Schematic merge tree of n levels: stacked level bars narrowing to the root."""
    bars = VGroup()
    for i in range(n):
        w = max(base * (1 - i / 16), 0.12)
        bars.add(Rectangle(width=w, height=dy * 0.55).set_stroke(width=0).set_fill(color, 0.55)
                 .move_to([x, y0 + i * dy, 0]))
    bars[-1].set_fill(STAR, 0.95)
    return bars


def hbar(x0, x1, y, h, color, opacity):
    return Rectangle(width=max(x1 - x0, 1e-3), height=h).set_stroke(width=0).set_fill(color, opacity).move_to(
        [(x0 + x1) / 2, y, 0])


def texture(x0, x1, y, h, step=0.12, color=VOID, opacity=0.5):
    """Hairline seams between thin transaction slabs (a sample, not one per transaction)."""
    g = VGroup()
    x = x0 + step
    while x < x1 - 1e-3:
        g.add(Rectangle(width=0.012, height=h).set_stroke(width=0).set_fill(color, opacity).move_to([x, y, 0]))
        x += step
    return g


class Scene63(TimedScene):
    def swap_title(self, text):
        new = scene_title(text)
        old, self.title = self.title, new
        return LaggedStart(FadeOut(old, shift=0.2 * UP), FadeIn(new, shift=0.2 * UP), lag_ratio=0.85)

    def construct(self):
        SID = "6.3"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731
        W = lambda p, o=1: WEND(SID, p, o)  # noqa: E731
        title, b, bodies, rows = final62()
        self.title = title
        blockg = VGroup(b["frame"], b["blab"], b["wt"], bodies, b["refs"], b["ticks"], b["bus"])
        self.add(title, blockg, b["agg"], rows)
        self.wait(0.3)
        self.pad_to(A("concrete numbers") - 0.3)
        self.play(self.swap_title("What aggregation buys"), FadeOut(rows), run_time=0.9)

        # --- latency: the merge tree, with a depth counter -------------------------------------------
        levels, edges = tree_layout(8, -5.6, 0.35, -2.2, 1.0, 0.62, 0.5)
        root = levels[3][0]
        self.pad_to(A("latency") - 0.3)
        self.play(self.swap_title("Latency"), FadeOut(blockg), ReplacementTransform(b["agg"], root), run_time=0.9)
        down = [n for l in (2, 1, 0) for n in levels[l]]
        self.play(LaggedStart(*[GrowFromPoint(n, root.get_center()) for n in down], lag_ratio=0.04),
                  LaggedStart(*[ShowCreation(e) for l in (2, 1, 0) for e in edges[l]], lag_ratio=0.04),
                  run_time=1.1)
        lifts = VGroup(*[tarrow([n.get_x(), -2.95, 0], n.get_bottom(), color=GOLD, width=SW_THIN, tip=0.14)
                         for n in levels[0]])
        self.pad_to(A("lifts run") - 0.2)
        self.play(*[ShowCreation(a) for a in lifts],
                  *[n.frame.animate.set_stroke(GOLD, SW_BOLD).set_anim_args(rate_func=there_and_back)
                    for n in levels[0]], run_time=0.7)
        RX = 1.9
        r1 = rich([("all lifts, in parallel:", TXT), ("1 step", GOLD)], size=FS_BODY)
        r1.move_to([RX, 1.25, 0], aligned_edge=LEFT)
        self.pad_to(A("one proving step") - 0.2)
        self.play(FadeIn(r1, shift=0.1 * LEFT), run_time=0.5)
        self.pad_to(A("binary tree") - 0.2)
        for l in (1, 2, 3):
            self.play(*[pulse(n, 1.15) for n in levels[l]], run_time=0.3)
        nl = mtex('N = 8 "transactions"', size=FS_LABEL, color=STAR).move_to([-2.6, -3.25, 0])
        self.pad_to(A("a block of n") - 0.1)
        self.play(FadeIn(nl, shift=0.1 * UP), run_time=0.5)
        r2 = rich([("merges, a binary tree:", TXT), ("$log_2 N$", GOLD), ("steps", GOLD)], size=FS_BODY)
        r2.move_to([RX, 0.55, 0], aligned_edge=LEFT)
        self.pad_to(A("log n") - 0.2)
        self.play(FadeIn(r2, shift=0.1 * LEFT), run_time=0.5)
        # pause: a depth counter beside the merge tree
        ys = [-2.2, -1.2, -0.2, 0.8, 1.8]
        depth = VGroup(*[mtex(str(i + 1), size=FS_BODY, color=GOLD).move_to([1.05, y, 0]) for i, y in enumerate(ys)])
        dbar = Line([1.45, ys[0], 0], [1.45, ys[3], 0], stroke_color=GOLD, stroke_width=SW_THIN, stroke_opacity=0.7)
        r3 = mtex('N = 8 : quad 1 + 3 = 4 "steps"', size=FS_BODY, color=STAR).move_to([RX, -0.15, 0], aligned_edge=LEFT)
        self.pad_to(W("log n more"))
        self.play(LaggedStart(*[FadeIn(d, scale=1.4) for d in depth[:4]], lag_ratio=0.25), ShowCreation(dbar),
                  FadeIn(r3), run_time=1.0)
        # doubling the traffic adds one level
        L16, E16 = tree_layout(16, -5.75, 0.55, -2.2, 1.0, 0.31, 0.26)
        self.pad_to(A("doubling") - 0.2)
        old_nodes = [n for l in range(4) for n in levels[l]]
        new_left = [L16[l][i] for l in range(4) for i in range(len(levels[l]))]
        new_right = [L16[l][i] for l in range(4) for i in range(len(levels[l]), 2 * len(levels[l]))]
        nl2 = mtex('N = 16 "transactions"', size=FS_LABEL, color=STAR).move_to(nl)
        r3b = mtex('N = 16 : quad 1 + 4 = 5 "steps"', size=FS_BODY, color=STAR).move_to(r3, aligned_edge=LEFT)
        dbar2 = Line([1.45, ys[0], 0], [1.45, ys[4], 0], stroke_color=GOLD, stroke_width=SW_THIN, stroke_opacity=0.7)
        lifts16 = VGroup(*[tarrow([n.get_x(), -2.95, 0], n.get_bottom(), color=GOLD, width=1.6, tip=0.1)
                           for n in L16[0]])
        self.play(*[ReplacementTransform(o, n) for o, n in zip(old_nodes, new_left)],
                  *[TransformFromCopy(o, n) for o, n in zip(old_nodes, new_right)],
                  FadeOut(VGroup(*edges)), FadeIn(VGroup(*E16)), FadeIn(L16[4][0], scale=0.6),
                  ReplacementTransform(lifts, lifts16[:8]), FadeIn(lifts16[8:]),
                  LaggedStart(FadeOut(nl), FadeIn(nl2), lag_ratio=0.8),
                  LaggedStart(FadeOut(r3), FadeIn(r3b), lag_ratio=0.8), ReplacementTransform(dbar, dbar2),
                  run_time=1.1)
        plus = label("doubling N: one more step", size=FS_LABEL, color=GOLD).move_to([RX, -0.75, 0], aligned_edge=LEFT)
        self.pad_to(A("one more step") - 0.1)
        self.play(FadeIn(depth[4], scale=1.5), FadeIn(plus, shift=0.1 * LEFT),
                  Flash(L16[4][0].get_center(), color=GOLD, flash_radius=0.4), run_time=0.6)
        r4 = rich([("$approx 1.2 \"s\"$", GOLD), ("per step", TXT)], size=FS_BODY).move_to([RX, -1.45, 0], aligned_edge=LEFT)
        r5 = label("on a consumer laptop, today", size=FS_LABEL, color=MUT).move_to([RX, -2.05, 0], aligned_edge=LEFT)
        self.pad_to(A("one point two") - 0.2)
        self.play(FadeIn(r4, shift=0.1 * LEFT), run_time=0.5)
        self.pad_to(A("consumer laptop") - 0.1)
        self.play(FadeIn(r5, shift=0.1 * LEFT), run_time=0.5)

        # --- the block-time budget ----------------------------------------------------------------------
        tree16 = VGroup(*L16, *E16, lifts16)
        tri5 = tri_levels(5)
        lev = mtex('5 "levels"', size=FS_BODY, color=STAR).move_to([-4.6, -3.1, 0])
        self.pad_to(A("now after") - 0.1)
        self.play(self.swap_title("The block-time budget"),
                  FadeOut(VGroup(r1, r2, r3b, r4, r5, depth, dbar2, plus, nl2)),
                  FadeOut(tree16, scale=0.6, shift=DOWN * 0.6), FadeIn(tri5, lag_ratio=0.1), FadeIn(lev),
                  run_time=0.9)
        X0, X1 = -2.3, 6.4
        PS = (X1 - X0) / BLOCK_S
        BY = 1.75
        xr = X1 - RESERVE_S * PS
        outline = Rectangle(width=X1 - X0, height=0.46).set_stroke(STAR, SW_THIN, 0.9).move_to([(X0 + X1) / 2, BY, 0])
        hdr = rich([("block time after NU7:", TXT)], size=FS_LABEL)
        hdr.move_to([X0, BY + 0.55, 0], aligned_edge=LEFT)
        t25 = mtex('25 "s"', size=FS_LABEL, color=STAR).next_to(hdr, RIGHT, buff=0.2)
        self.pad_to(A("nu7") - 0.1)
        self.play(FadeIn(hdr), ShowCreation(outline), run_time=0.6)
        self.pad_to(A("twenty five seconds") - 0.1)
        self.play(FadeIn(t25, scale=1.3), run_time=0.4)
        res = hbar(xr, X1, BY, 0.46, DIM, 0.55)
        res_l = rich([("$4 \"s\"$", MUT), ("reserved: transmission, node logic", MUT)], size=FS_SMALL)
        res_l.move_to([X1, BY - 0.5, 0], aligned_edge=RIGHT)
        self.pad_to(A("reserve four seconds") - 0.2)
        self.play(FadeIn(res), FadeIn(res_l), run_time=0.6)
        agg_seg = hbar(X0, xr, BY, 0.46, GOLD, 0.16)
        agg_l = rich([("$21 \"s\"$", GOLD), ("aggregation", GOLD)], size=FS_SMALL).move_to([X0, BY - 0.5, 0], aligned_edge=LEFT)
        self.pad_to(A("twenty one seconds") - 0.2)
        self.play(FadeIn(agg_seg), FadeIn(agg_l), run_time=0.6)
        cw = STEP_S * PS
        cells = VGroup(*[Rectangle(width=cw - 0.05, height=0.34).set_stroke(GOLD, 1.4, 0.9).set_fill(GOLD, 0.35)
                         .move_to([X0 + (i + 0.5) * cw, BY, 0]) for i in range(17)])
        eq = rich([("17 steps", GOLD), ("=", TXT), ("1 lift", STAR), ("+", TXT), ("16 merge levels", GOLD)],
                  size=FS_BODY).move_to([(X0 + X1) / 2, BY - 1.15, 0])
        self.pad_to(A("seventeen steps") - 0.2)
        self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in cells], lag_ratio=0.08), FadeIn(eq[0]), run_time=0.9)
        self.pad_to(A("one for anchor") - 0.1)
        self.play(cells[0].animate.set_fill(STAR, 0.8).set_stroke(STAR), FadeIn(eq[1:3]), run_time=0.5)
        self.pad_to(A("sixteen levels") - 0.1)
        self.play(FadeIn(eq[3:]), *[pulse(c, 1.15) for c in cells[1:]], run_time=0.6)
        # pause: the merge tree grows to sixteen levels
        tri16 = tri_levels(16)
        lev16 = mtex('16 "levels"', size=FS_BODY, color=STAR).move_to([-4.6, -3.1, 0])
        digs = [mtex(f'{k} "levels"', size=FS_BODY, color=STAR) for k in range(5, 17)]
        self.pad_to(W("binary merging"))
        self.play(ReplacementTransform(tri5, tri16[:5]), LaggedStart(*[FadeIn(t, shift=0.1 * UP) for t in tri16[5:]],
                                                                       lag_ratio=0.3),
                  counter_anim(lev, digs, lev.get_center()), run_time=1.1)
        self.remove(lev)
        self.add(lev16)
        n1 = mtex('2^16 = "65,536" "transactions per block"', size=FS_BODY, color=STAR)
        n2 = rich([("$approx \"2,600\"$", GOLD), ("per second", TXT)], size=FS_BODY)
        n3 = label("from a single miner", size=FS_BODY, color=MUT)
        nums = VGroup(n1, n2, n3).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([X0 + 0.2, -1.2, 0],
                                                                                      aligned_edge=LEFT)
        self.pad_to(A("sixty four thousand") - 0.2)
        self.play(FadeIn(n1, shift=0.1 * UP), run_time=0.6)
        self.pad_to(A("twenty six hundred") - 0.2)
        self.play(FadeIn(n2, shift=0.1 * UP), run_time=0.5)
        self.pad_to(A("single miner") - 0.2)
        self.play(FadeIn(n3, shift=0.1 * UP), run_time=0.5)

        # --- size ------------------------------------------------------------------------------------------
        self.pad_to(A("size is the other") - 0.3)
        self.play(self.swap_title("Size"),
                  FadeOut(VGroup(tri16, lev16, outline, hdr, t25, res, res_l, agg_seg, agg_l, cells, eq, nums)),
                  run_time=0.9)
        KB = 2.4 / 7.4                       # scene units per KB, upper comparison
        PH = 1.3
        pslab = RoundedRectangle(width=7.4 * KB, height=PH, corner_radius=0.1).set_stroke(FLARE, SW).set_fill(FLARE, 0.22)
        pslab.move_to([-4.6, 1.55, 0])
        ptok = proof_token(0.14).move_to(pslab)
        p_l = label("compressed proof", size=FS_LABEL, color=FLARE).next_to(pslab, DOWN, buff=0.18)
        p_kb = mtex('approx "7.4 KB"', size=FS_LABEL, color=FLARE).next_to(pslab, UP, buff=0.15)
        self.pad_to(A("a compressed proof") - 0.1)
        self.play(FadeIn(pslab), FadeIn(ptok), FadeIn(p_l), run_time=0.6)
        self.pad_to(A("seven point four") - 0.2)
        self.play(FadeIn(p_kb, scale=1.3), run_time=0.5)
        items = [("8 tachygrams", '8 times 32 "B"'),
                 ('4 actions ("rk", "cv")', '4 times 64 "B"'),
                 ("4 action signatures", '4 times 64 "B"'),
                 ("binding signature", '64 "B"'),
                 ("small encrypted memo", 'approx 256 "B"'),
                 ("pointer to the covering stamp", '32 "B"')]
        TL, TR = 0.2, 6.5
        th = label("a 2-in, 2-out transaction", size=FS_LABEL, color=STAR).move_to([TL, 2.5, 0], aligned_edge=LEFT)
        rws = VGroup()
        for i, (t, v) in enumerate(items):
            if "(" in t:
                lt = rich([("4 actions", TXT), ('$("rk", "cv")$', TXT)], size=FS_LABEL)
            else:
                lt = label(t, size=FS_LABEL, color=TXT)
            y = 1.98 - 0.44 * i
            lt.move_to([TL, y, 0], aligned_edge=LEFT)
            vv = mtex(v, size=FS_LABEL, color=STAR).move_to([TR, y, 0], aligned_edge=RIGHT)
            rws.add(VGroup(lt, vv))
        tot = rich([("total", TXT), ('$approx "1.15 KB"$', STAR)], size=FS_BODY).move_to([TR, -0.75, 0],
                                                                                      aligned_edge=RIGHT)
        rule = Line([TL, -0.42, 0], [TR, -0.42, 0], stroke_color=DIM, stroke_width=SW_THIN)
        self.pad_to(A("a two in two out") - 0.1)
        self.play(FadeIn(th), run_time=0.5)
        for i, cue in enumerate(["eight tachygrams", "four actions", "four sixty four byte", "binding signature",
                                 "small encrypted memo", "a pointer"]):
            self.pad_to(A(cue) - 0.15)
            self.play(FadeIn(rws[i], shift=0.1 * LEFT), run_time=0.45)
        self.pad_to(A("one point one five") - 0.2)
        self.play(ShowCreation(rule), FadeIn(tot, shift=0.1 * UP), run_time=0.6)
        # pause: a block bar, proof share against payload
        txb = Rectangle(width=1.15 * KB, height=PH).set_stroke(STAR, SW_THIN).set_fill(STAR, 0.3)
        txb.move_to([pslab.get_right()[0] + 0.9, 1.55, 0])
        tx_l = label("transaction", size=FS_LABEL, color=STAR).next_to(txb, DOWN, buff=0.18).align_to(txb, LEFT)
        tx_kb = mtex('approx "1.15 KB"', size=FS_LABEL, color=STAR).next_to(txb, UP, buff=0.15).align_to(txb, LEFT)
        BX0, BX1, BH = -5.8, 5.8, 0.42
        Y1, Y2 = -0.85, -2.3
        o1 = Rectangle(width=BX1 - BX0, height=BH).set_stroke(STAR, SW_THIN, 0.8).move_to([0, Y1, 0])
        o2 = Rectangle(width=BX1 - BX0, height=BH).set_stroke(STAR, SW_THIN, 0.8).move_to([0, Y2, 0])
        b1l = label("2 MB block, without aggregation", size=FS_LABEL, color=TXT).move_to([BX0, Y1 + 0.45, 0], aligned_edge=LEFT)
        b2l = label("2 MB block, with aggregation", size=FS_LABEL, color=TXT).move_to([BX0, Y2 + 0.45, 0], aligned_edge=LEFT)
        self.pad_to(W("one point one five kilobytes"))
        self.play(FadeOut(VGroup(rws, rule, th), shift=(txb.get_center() - rws.get_center()) * 0.4, scale=0.4),
                  FadeIn(txb, scale=0.5), ReplacementTransform(tot, tx_kb), FadeIn(tx_l),
                  ShowCreation(o1), FadeIn(b1l), ShowCreation(o2), FadeIn(b2l), run_time=1.0)
        # without aggregation: every transaction hauls its own proof
        U = (BX1 - BX0) / 2_000_000
        pw, prw = (PROOF_B + TX_B) * U, PROOF_B * U
        fill1 = VGroup()
        for k in range(N_STANDALONE):
            x = BX0 + k * pw
            fill1.add(hbar(x, x + prw, Y1, BH - 0.04, FLARE, 0.8), hbar(x + prw, x + pw, Y1, BH - 0.04, STAR, 0.95))
        self.pad_to(A("without aggregation") - 0.1)
        self.play(GrowFromEdge(fill1, LEFT), run_time=1.2)
        six = mtex('"proof" > 6 times "transaction"', size=FS_BODY, color=FLARE).move_to([2.6, 1.55, 0])
        self.pad_to(A("more than six") - 0.1)
        self.play(FadeIn(six, shift=0.1 * LEFT), pulse(pslab, 1.06), run_time=0.6)
        c1 = rich([("$approx 230$", STAR), ("transactions", TXT)], size=FS_LABEL).move_to([BX1, Y1 + 0.45, 0],
                                                                                           aligned_edge=RIGHT)
        self.pad_to(A("two hundred and thirty") - 0.2)
        self.play(FadeIn(c1, shift=0.1 * UP), run_time=0.5)
        # with aggregation: one proof, then thin slabs
        xp = BX0 + PROOF_B * U
        sliver = hbar(BX0, xp, Y2, BH - 0.04, FLARE, 1.0)
        body2 = hbar(xp, xp + N_AGG_2MB * TX_B * U, Y2, BH - 0.04, STAR, 0.8)
        tex2 = texture(xp, body2.get_right()[0], Y2, BH - 0.04)
        fill2 = VGroup(sliver, body2, tex2)
        self.pad_to(A("with aggregation") - 0.1)
        self.play(GrowFromEdge(fill2, LEFT), run_time=1.0)
        onep = label("one proof", size=FS_LABEL, color=FLARE).move_to([BX0 + 0.75, Y2 - 0.62, 0])
        onea = tarrow(onep.get_top() + LEFT * 0.55, [BX0 + 0.03, Y2 - BH / 2, 0], color=FLARE, width=SW_THIN, tip=0.14)
        self.pad_to(A("a single proof") - 0.1)
        self.play(FadeIn(onep), ShowCreation(onea), Flash(sliver.get_center(), color=FLARE, flash_radius=0.3),
                  run_time=0.6)
        c2 = rich([("$approx \"1,700\"$", STAR), ("transactions", TXT)], size=FS_LABEL).move_to(
            [BX1, Y2 + 0.45, 0], aligned_edge=RIGHT)
        c2r = rich([("$approx 70$", GOLD), ("per second", TXT)], size=FS_LABEL).move_to([BX1, Y2 - 0.62, 0],
                                                                                        aligned_edge=RIGHT)
        self.pad_to(A("seventeen hundred") - 0.2)
        self.play(FadeIn(c2, shift=0.1 * UP), run_time=0.5)
        self.pad_to(A("seventy") - 0.2)
        self.play(FadeIn(c2r, shift=0.1 * UP), run_time=0.5)
        share = rich([("proof per transaction:", TXT), ('$"7.4 KB"$', FLARE), ("$->$", MUT), ('$approx 4 "B"$', GOLD)],
                     size=FS_BODY).move_to([2.6, 0.65, 0])
        self.pad_to(A("share of the proof") - 0.2)
        self.play(FadeIn(share[:2], shift=0.1 * UP), run_time=0.4)
        self.pad_to(A("drops") - 0.1)
        self.play(FadeIn(share[2]), FadeIn(share[3], shift=0.35 * DOWN), share[1].animate.fade(0.5), run_time=0.6)

        # --- size, not proving, is the ceiling ------------------------------------------------------------
        self.pad_to(A("really size") - 0.3)
        self.play(self.swap_title("Size, not proving, is the ceiling"),
                  FadeOut(VGroup(pslab, ptok, p_l, p_kb, txb, tx_l, tx_kb, six, share, o1, b1l, fill1, c1, onep, onea,
                                 c2, c2r)),
                  VGroup(o2, fill2, b2l).animate.shift(UP * 2.4), run_time=1.0)
        YB = Y2 + 2.4
        o20 = Rectangle(width=BX1 - BX0, height=BH).set_stroke(STAR, SW_THIN, 0.8).move_to([0, YB, 0])
        b20 = label("20 MB block, with aggregation", size=FS_LABEL, color=TXT).move_to([BX0, YB + 0.45, 0],
                                                                                    aligned_edge=LEFT)
        two_l = label("2 MB", size=FS_SMALL, color=MUT).move_to([BX0 + 0.58, YB - 0.5, 0])
        self.pad_to(A("twenty megabytes") - 0.2)
        self.play(VGroup(o2, fill2).animate.stretch(0.1, 0, about_edge=LEFT), ShowCreation(o20),
                  LaggedStart(FadeOut(b2l), FadeIn(b20), lag_ratio=0.8), FadeIn(two_l), run_time=0.9)
        U20 = U / 10
        xp20 = BX0 + PROOF_B * U20
        body20 = hbar(xp20, xp20 + 17385 * TX_B * U20, YB, BH - 0.04, STAR, 0.8)
        tex20 = texture(xp20, body20.get_right()[0], YB, BH - 0.04, step=0.15)
        self.pad_to(A("that fits") - 0.1)
        self.play(FadeOut(VGroup(o2, fill2[1:])), GrowFromEdge(VGroup(body20, tex20), LEFT), run_time=0.9)
        self.add(fill2[0])
        c3 = rich([("$approx \"17,000\"$", STAR), ("transactions", TXT)], size=FS_LABEL).move_to(
            [BX1, YB + 0.45, 0], aligned_edge=RIGHT)
        c3r = rich([("$approx 700$", GOLD), ("per second", TXT)], size=FS_BODY).move_to([BX1, YB - 0.6, 0],
                                                                                       aligned_edge=RIGHT)
        self.pad_to(A("seventeen thousand") - 0.15)
        self.play(FadeIn(c3, shift=0.1 * UP), run_time=0.5)
        self.pad_to(A("seven hundred") - 0.2)
        self.play(FadeIn(c3r, shift=0.1 * UP), run_time=0.5)
        # pause: block bar grows, seven hundred per second
        sweep = Rectangle(width=0.08, height=BH + 0.2).set_stroke(width=0).set_fill(GOLD, 0.9).move_to([BX0, YB, 0])
        self.pad_to(W("seven hundred per second"))
        self.add(sweep)
        self.play(sweep.animate.move_to([BX1, YB, 0]), pulse(c3r, 1.12), run_time=0.9)
        self.remove(sweep)
        # proving still fits in the 21 s window
        WS = 0.42
        wx0, wy = BX0, -1.55
        win = Rectangle(width=21 * WS, height=0.42).set_stroke(GOLD, SW, 0.9).move_to([wx0 + 21 * WS / 2, wy, 0])
        win_l = rich([("aggregation window:", TXT), ("$21 \"s\"$", GOLD)], size=FS_LABEL).move_to(
            [wx0, wy + 0.5, 0], aligned_edge=LEFT)
        self.pad_to(A("proving them") - 0.1)
        self.play(ShowCreation(win), FadeIn(win_l), run_time=0.6)
        st16 = VGroup(*[Rectangle(width=STEP_S * WS - 0.05, height=0.32).set_stroke(GOLD, 1.4).set_fill(
            STAR if i == 0 else GOLD, 0.8 if i == 0 else 0.4).move_to([wx0 + (i + 0.5) * STEP_S * WS, wy, 0])
            for i in range(16)])
        feq = rich([("$16 times 1.2 \"s\"$", STAR), ("$= 19.2 \"s\" <= 21 \"s\"$", GOLD)], size=FS_BODY)
        feq.move_to([wx0, wy - 0.7, 0], aligned_edge=LEFT)
        self.pad_to(A("sixteen steps") - 0.3)
        self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in st16], lag_ratio=0.12), FadeIn(feq[0]), run_time=1.1)
        okm = checkmark(0.32, GOLD).next_to(win, RIGHT, buff=0.3)
        self.pad_to(A("nineteen seconds") - 0.1)
        self.play(FadeIn(feq[1], shift=0.1 * LEFT), ShowCreation(okm), run_time=0.6)

        # --- one proof per block -------------------------------------------------------------------------------
        self.pad_to(A("one proof per block") - 0.4)
        ps = RoundedRectangle(width=0.9, height=0.9, corner_radius=0.1).set_stroke(FLARE, SW).set_fill(FLARE, 0.25)
        ps.move_to([-5.6, 0.6, 0])
        pst = proof_token(0.12).move_to(ps)
        trf = Rectangle(width=0.6, height=0.9).set_stroke(STAR, SW_THIN).set_fill(STAR, 0.35)
        trf.move_to(ps.get_right() + RIGHT * 0.12, aligned_edge=LEFT)
        trl = label("transactions", size=FS_LABEL, color=STAR).next_to(trf, UP, buff=0.15).align_to(trf, LEFT)
        pl = label("one proof", size=FS_LABEL, color=FLARE).next_to(ps, UP, buff=0.15)
        trl.shift(RIGHT * max(0, pl.get_right()[0] + 0.3 - trl.get_left()[0]))
        self.play(self.swap_title("One proof per block"),
                  FadeOut(VGroup(o20, fill2[0], body20, tex20, b20, two_l, c3, c3r, win, win_l, st16, feq, okm)),
                  FadeIn(VGroup(ps, pst, pl)), FadeIn(trf), FadeIn(trl), run_time=0.9)
        mx0, my = -5.15, -1.1
        meter_l = label("the proof's share of each transaction", size=FS_LABEL, color=MUT).move_to(
            [mx0, my + 0.5, 0], aligned_edge=LEFT)
        meter = Rectangle(width=4.0, height=0.3).set_stroke(width=0).set_fill(FLARE, 0.8).move_to([mx0, my, 0],
                                                                                                aligned_edge=LEFT)
        self.pad_to(A("the proof's share") - 0.2)
        self.play(FadeIn(meter_l), GrowFromEdge(meter, LEFT), run_time=0.6)
        grow = ValueTracker(0.0)
        x_left = trf.get_left()[0]

        def upd_tr(m):
            w = 0.6 + grow.get_value() * (6.1 - x_left - 0.6)
            m.stretch_to_fit_width(w).move_to([x_left, m.get_y(), 0], aligned_edge=LEFT)

        def upd_meter(m):
            w = 0.6 + grow.get_value() * (6.1 - x_left - 0.6)
            m.stretch_to_fit_width(4.0 * 0.6 / w).move_to([mx0, my, 0], aligned_edge=LEFT)
        trf.add_updater(upd_tr)
        meter.add_updater(upd_meter)
        self.pad_to(A("shrinks") - 0.4)
        self.play(grow.animate.set_value(1.0), run_time=1.6)
        trf.clear_updaters()
        meter.clear_updaters()
        nb = rich([("proof size:", TXT), ("no longer the bottleneck", GOLD)], size=FS_BODY).move_to([0, -2.2, 0])
        self.pad_to(A("proof size stops") - 0.2)
        self.play(FadeIn(nb, shift=0.1 * UP), run_time=0.6)
        left = rich([("what's left:", TXT), ("delivering the notes", STAR)], size=FS_BODY).move_to([0, -2.95, 0])
        self.pad_to(A("delivering the notes") - 0.2)
        self.play(FadeIn(left, shift=0.1 * UP), run_time=0.7)
        self.pad_to(scene_T(SID))

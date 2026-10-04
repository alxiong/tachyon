"""Act 7 — the payment protocol. Anchored to anim/words.json timestamps.

Render:  ./qa.sh act7.py Scene71   (and Scene72), then ./build_act.sh 7

Layout: title band (scene_title) / stage / caption band (caption), per style.py.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manimlib import *
from style import *
from style import _esc_typst


# ---- scene-local vocabulary --------------------------------------------------

def db_cyl(w=2.2, h=1.5, color=CYAN):
    """A database cylinder: elliptical top, straight sides, curved bottom."""
    eh = 0.32 * w / 2.2 + 0.08
    top = Ellipse(width=w, height=eh)
    top.set_fill(color, 0.14)
    top.set_stroke(color, SW, 0.95)
    top.move_to(UP * h / 2)
    left = Line(UP * h / 2 + LEFT * w / 2, DOWN * h / 2 + LEFT * w / 2,
                stroke_color=color, stroke_width=SW, stroke_opacity=0.95)
    right = Line(UP * h / 2 + RIGHT * w / 2, DOWN * h / 2 + RIGHT * w / 2,
                 stroke_color=color, stroke_width=SW, stroke_opacity=0.95)
    bot = Arc(start_angle=PI, angle=PI, radius=w / 2)
    bot.stretch(eh / w, 1)
    bot.move_to(DOWN * h / 2 + DOWN * eh / 4)
    bot.set_stroke(color, SW, 0.95)
    mid = Arc(start_angle=PI, angle=PI, radius=w / 2)
    mid.stretch(eh / w, 1)
    mid.move_to(UP * h / 6 + DOWN * eh / 4)
    mid.set_stroke(color, SW_THIN, 0.45)
    body = Rectangle(width=w, height=h)
    body.set_fill(color, 0.06)
    body.set_stroke(width=0)
    return VGroup(body, mid, bot, left, right, top)


def bl_label(s, size=FS_LABEL, color=TXT):
    """label() whose local y=0 is a fixed typographic line (strut bottom), so
    sibling labels placed at one y share a baseline ("memos" vs "first contact"
    otherwise sit at different heights: next_to aligns ink, not baselines)."""
    m = mtex("|" + _esc_typst(s), size=size, color=color, math=False)
    strut = m.submobjects[0]
    m.remove(strut)
    m.shift(UP * (-strut.get_bottom()[1]))
    m.base_h = max(m.get_height(), 1e-6)
    m.lint_text = s[:40]
    return m


def db_unit(name, sub, color=CYAN):
    """Cylinder + name + one-line subtitle, stacked on shared baselines."""
    c = db_cyl(color=color)
    y0 = c.get_bottom()[1]
    t = bl_label(name, size=FS_LABEL, color=color)
    t.shift(UP * (y0 - 0.62)).set_x(c.get_x())
    s = bl_label(sub, size=FS_SMALL, color=MUT)
    s.shift(UP * (y0 - 1.05)).set_x(c.get_x())
    return VGroup(c, t, s)


def four_dbs():
    dbs = VGroup(db_unit("memos", "per epoch"),
                 db_unit("first contact", "handshakes"),
                 db_unit("tachygrams", "per epoch"),
                 db_unit("registry", "addresses"))
    dbs.arrange(RIGHT, buff=0.9, aligned_edge=UP).move_to(UP * 0.85)
    return dbs


def tg_highlight(tg):
    """Target state of the 'watch the tachygram one' highlight (outline only:
    the body rectangle and the inner arc must not pick up a bold stroke)."""
    cyl = tg[0]
    VGroup(*cyl[2:]).set_stroke(GOLD, SW_BOLD, 1.0)
    cyl[1].set_stroke(GOLD, SW_THIN, 0.5)
    tg[1].set_color(GOLD)
    return tg


def proof_card_group(tg):
    card = proof_card(1.3).move_to(tg[0].get_center() + DOWN * 3.15 + LEFT * 2.6)
    c_lab = label("spendability proof", size=FS_LABEL, color=GOLD)
    c_lab.next_to(card, RIGHT, buff=0.3)
    return card, c_lab


def swap_title(old, new):
    """Title change between different strings: slide out/in (a glyph morph
    between unrelated strings scribbles)."""
    return [LaggedStart(FadeOut(old, shift=UP * 0.4), FadeIn(new, shift=UP * 0.4),
                        lag_ratio=0.55)]


def lockbox(w=1.3, h=1.0, color=CYAN):
    """A keyed lockbox for one tag in the schedule."""
    box = RoundedRectangle(width=w, height=h, corner_radius=0.12)
    box.set_fill(color, 0.10)
    box.set_stroke(color, SW, 0.95)
    shackle = Arc(start_angle=0, angle=PI, radius=0.2 * w)
    shackle.set_stroke(color, SW, 0.95)
    shackle.next_to(box, UP, buff=0)
    hole = VGroup(
        Dot(radius=0.07 * w).set_fill(color, 1.0),
        Line(ORIGIN, DOWN * 0.16 * w, stroke_color=color, stroke_width=SW_BOLD),
    )
    hole[1].shift(DOWN * 0.05 * w)
    hole.move_to(box.get_center())
    return VGroup(box, shackle, hole)


def qr_glyph(n=5, s=0.26, color=MUT):
    """A QR-code pictogram (fixed pattern, not random)."""
    on = {(0, 0), (0, 1), (1, 0), (0, 4), (0, 3), (1, 4), (4, 0), (3, 0),
          (4, 1), (2, 2), (4, 3), (3, 3), (2, 4), (4, 4), (1, 2)}
    cells = VGroup()
    for i in range(n):
        for j in range(n):
            if (i, j) in on:
                c = Square(side_length=s)
                c.set_fill(color, 0.9)
                c.set_stroke(width=0)
                c.move_to(RIGHT * j * s + DOWN * i * s)
                cells.add(c)
    frame = Square(side_length=n * s + 0.18)
    frame.set_fill(opacity=0)
    frame.set_stroke(color, SW_THIN, 0.8)
    frame.move_to(cells.get_center())
    return VGroup(frame, cells)


def wallet_panel(center, w=2.6, h=1.9):
    box = panel(w, h, color=GOLD, fill_opacity=0.07).move_to(center)
    lab = label("wallet", size=FS_LABEL, color=GOLD).next_to(box, DOWN, buff=0.18)
    tok = proof_token(0.17).move_to(box.get_center())
    return box, lab, tok


def memo_icon(color=CYAN, w=0.42, h=0.3):
    """A tiny sealed memo (envelope) riding above a block."""
    body = RoundedRectangle(width=w, height=h, corner_radius=0.03)
    body.set_fill(color, 0.18)
    body.set_stroke(color, SW_THIN, 0.95)
    apex = body.get_center() + DOWN * 0.03
    flap = VGroup(Line(body.get_corner(UL), apex, stroke_width=1.6, stroke_color=color),
                  Line(body.get_corner(UR), apex, stroke_width=1.6, stroke_color=color))
    return VGroup(body, flap)


def cipher_row(tag_tex, color=CYAN):
    t = tex_chip(tag_tex, color=color, size=FS_LABEL, pad=0.14)
    c = key_chip("ciphertext", color=MUT, size=FS_SMALL, pad=0.14)
    return VGroup(t, c).arrange(RIGHT, buff=0.3)


def x_mark(center, size=0.22, color=FLARE, width=SW):
    a = Line(center + size * UL, center + size * DR, stroke_color=color, stroke_width=width)
    b = Line(center + size * UR, center + size * DL, stroke_color=color, stroke_width=width)
    return VGroup(a, b)


# ---- 7.1 ----------------------------------------------------------------------

class Scene71(TimedScene):
    """7.1 — The other half of the split."""

    def construct(self):
        A = lambda p, o=1: anchor("7.1", p, o)
        AA = lambda ps, o=1: anchor_any("7.1", ps, o)

        # "the shielded core is done ... the key-structure split"
        shp = panel(4.8, 3.0, color=GOLD, fill_opacity=0.06).move_to(LEFT * 3.4 + UP * 0.2)
        sh_lab = label("shielded protocol", size=FS_BODY, color=GOLD)
        sh_lab.next_to(shp, DOWN, buff=0.3)
        ck = checkmark(0.7).move_to(shp.get_center() + LEFT * 0.12)
        sh_done = label("done", size=FS_LABEL, color=GOLD).next_to(ck, RIGHT, buff=0.3)
        pay = panel(4.8, 3.0, color=CYAN, fill_opacity=0.02, stroke_opacity=0.35)
        pay.move_to(RIGHT * 3.4 + UP * 0.2)
        pay_lab = label("payment protocol", size=FS_BODY, color=MUT)
        pay_lab.next_to(pay, DOWN, buff=0.3)
        q = label("?", size=72, color=MUT).move_to(pay.get_center())
        self.wait(0.6)
        self.play(FadeIn(shp), FadeIn(sh_lab, shift=UP * 0.15), ShowCreation(ck),
                  FadeIn(sh_done), run_time=1.2)
        cut = DashedLine(UP * 2.4, DOWN * 2.2, stroke_color=STAR, stroke_width=SW)
        self.pad_to(A("key structure split") - 0.3)
        self.play(ShowCreation(cut), FadeIn(pay), FadeIn(pay_lab, shift=UP * 0.15),
                  FadeIn(q, scale=1.3), run_time=1.0)

        # "time to pay that debt" — the payment side takes the whole stage
        self.pad_to(A("pay that debt") - 0.4)
        title = scene_title("the payment protocol", color=CYAN)
        self.play(FadeOut(VGroup(shp, sh_lab, ck, sh_done), shift=LEFT * 0.6),
                  FadeOut(cut), FadeOut(VGroup(pay, q)),
                  *swap_title(pay_lab, title), run_time=1.2)

        # "the enemy is trial decryption" — wallet + the whole chain of memos
        wbox, wlab, token = wallet_panel(LEFT * 4.9 + UP * 1.25)
        blocks = VGroup(*[block(0.95, 0.66) for _ in range(9)])
        blocks.arrange(RIGHT, buff=0.42).move_to(DOWN * 1.75 + RIGHT * 0.1)
        links = VGroup(*[chain_link(blocks[i], blocks[i + 1]) for i in range(8)])
        memos = VGroup(*[memo_icon().next_to(b, UP, buff=0.16) for b in blocks])
        chain_lab = label("every memo on chain", size=FS_SMALL, color=MUT)
        chain_lab.next_to(blocks, DOWN, buff=0.25)
        self.pad_to(A("trial decryption") - 1.1)
        self.play(FadeIn(wbox), FadeIn(wlab), FadeIn(token),
                  LaggedStart(*[FadeIn(b) for b in blocks], lag_ratio=0.06),
                  ShowCreation(links, lag_ratio=0.06),
                  LaggedStart(*[FadeIn(m, shift=DOWN * 0.1) for m in memos], lag_ratio=0.06),
                  run_time=1.5)
        cap = caption("trial decryption: try to open every memo")
        self.play(FadeIn(cap, shift=UP * 0.15), FadeIn(chain_lab), run_time=0.6)

        # "attempts every memo on chain" — the wallet's key sweeps; almost all miss
        self.pad_to(A("every memo") - 0.3)
        sweep = RoundedRectangle(width=0.8, height=1.55, corner_radius=0.1)
        sweep.set_stroke(GOLD, SW, 0.95).set_fill(GOLD, 0.06)
        sweep.move_to(VGroup(memos[0], blocks[0]))
        xs = VGroup(*[x_mark(m.get_center() + UP * 0.42, 0.1, MUT, SW_THIN)
                      for m in memos])
        self.play(FadeIn(sweep), run_time=0.3)
        self.play(sweep.animate.move_to(VGroup(memos[-1], blocks[-1])),
                  LaggedStart(*[AnimationGroup(m.animate.set_opacity(0.35), ShowCreation(x))
                                for m, x in zip(memos, xs)], lag_ratio=0.25),
                  run_time=1.6)
        self.play(FadeOut(sweep), run_time=0.3)

        # three costs, beside the wallet, landing on their words
        costs = bullets(["linear in everyone's traffic",
                         "leaks timing to the server",
                         "melts under load (sandblasting)"],
                        size=FS_BODY, color=TXT, mark_color=FLARE, buff=0.36)
        costs.next_to(wbox, RIGHT, buff=1.0).align_to(wbox, UP).shift(UP * 0.15)
        self.pad_to(A("linear work") - 0.2)
        self.play(FadeIn(costs[0], shift=RIGHT * 0.2), run_time=0.6)
        self.pad_to(A("leaks your timing") - 0.2)
        self.play(FadeIn(costs[1], shift=RIGHT * 0.2), run_time=0.6)
        self.pad_to(A("sandblasting") - 0.3)
        self.play(FadeIn(costs[2], shift=RIGHT * 0.2), run_time=0.6)
        self.pad_to(A("melts under") - 0.2)
        flood = VGroup(*[memo_icon(FLARE).move_to(m.get_center() + UP * 0.4)
                         for m in memos])
        self.play(LaggedStart(*[FadeIn(f, shift=DOWN * 0.3) for f in flood], lag_ratio=0.05),
                  costs[2][1].animate.set_color(FLARE), run_time=1.0)
        self.play(FadeOut(flood), run_time=0.4)

        # "the replacement is private information retrieval"
        self.pad_to(A("private information retrieval") - 0.9)
        SV_W, SV_H, SV_C = 4.3, 4.2, RIGHT * 2.0 + UP * 0.05
        server = panel(SV_W, SV_H, color=CYAN, fill_opacity=0.05).move_to(SV_C)
        s_lab = label("PIR server", size=FS_LABEL, color=CYAN).next_to(server, UP, buff=0.18)
        rows = VGroup(*[cipher_row(f'"tag"_{i}') for i in range(4)])
        slots = VGroup(*[cipher_row(f'"tag"_{i}') for i in range(5)])
        slots.arrange(DOWN, buff=0.2).move_to(server)
        for r, sl in zip(rows, slots):
            r.move_to(sl)
        # the on-chain memos become indexed database rows
        # clear the trial-decryption layer first, then build the server
        self.play(FadeOut(VGroup(costs, xs, cap, chain_lab)),
                  FadeOut(VGroup(blocks, links)),
                  FadeOut(VGroup(*memos[4:]), shift=UP * 0.3),
                  run_time=0.6)
        self.play(FadeIn(server, scale=0.96), FadeIn(s_lab),
                  VGroup(wbox, wlab, token).animate.shift(DOWN * 1.2),
                  *[FadeTransform(memos[i], rows[i]) for i in range(4)],
                  run_time=1.2)
        pir_cap = caption("PIR: fetch an entry without revealing which one")
        self.play(FadeIn(pir_cap, shift=UP * 0.15), run_time=0.6)

        # "senders publish each encrypted memo under a short tag"
        self.pad_to(A("short tag") - 1.2)
        sender = bead(STAR, 0.13).move_to(RIGHT * 5.6 + DOWN * 2.0)
        sd_lab = label("sender", size=FS_SMALL, color=MUT).next_to(sender, DOWN, buff=0.15)
        new_row = cipher_row('"tag"_4').scale(0.9)
        new_row.next_to(sender, UP, buff=0.3)
        self.play(FadeIn(sender, scale=1.4), FadeIn(sd_lab), run_time=0.5)
        self.play(FadeIn(new_row, shift=UP * 0.2), run_time=0.5)
        self.play(new_row.animate.scale(1 / 0.9).move_to(slots[4]), run_time=0.9)
        rows.add(new_row)

        # "a recipient who knows the tag asks a PIR server for it"
        self.pad_to(A("asks a PIR server") - 0.6)
        qtag = tex_chip('"tag"_2', color=GOLD, size=FS_LABEL, pad=0.14)
        qtag.next_to(wbox, DOWN, buff=0.75)
        q_arrow = tarrow(wbox.get_right() + DOWN * 0.3, server.get_left() + DOWN * 0.3 + LEFT * 0.05,
                         color=GOLD, width=SW)
        self.play(FadeIn(qtag, scale=1.2), run_time=0.5)
        self.play(ShowCreation(q_arrow),
                  qtag.animate.next_to(q_arrow, DOWN, buff=0.15), run_time=0.9)

        # "answers without learning which entry it served" — every row looks alike
        self.pad_to(A("without learning") - 0.3)
        huh = label("which one?", size=FS_LABEL, color=CYAN)
        huh.next_to(s_lab, RIGHT, buff=0.35)
        self.play(LaggedStart(*[r.animate(rate_func=there_and_back).scale(1.06)
                                for r in rows], lag_ratio=0.1),
                  FadeIn(huh), run_time=1.2)
        answer = rows[2].copy()
        self.play(answer.animate.next_to(wbox, DOWN, buff=0.75),
                  FadeOut(qtag), run_time=1.0)

        # "a black box with one promise — retrieval without a trace"
        self.pad_to(A("black box") - 0.4)
        shade = panel(SV_W, SV_H, color=CYAN, fill_opacity=0.55, stroke_opacity=1.0)
        shade.set_fill(VOID, 0.82)
        shade.move_to(server)
        bb = label("black box", size=FS_HEAD, color=CYAN).move_to(server)
        self.play(FadeIn(shade), FadeOut(huh), rows.animate.set_opacity(0.12),
                  FadeIn(bb, scale=1.1), run_time=0.8)
        promise = caption("one promise: retrieval without a trace", color=STAR)
        self.pad_to(A("retrieval without a trace") - 0.4)
        self.play(FadeOut(pir_cap, shift=UP * 0.15), FadeIn(promise, shift=UP * 0.15),
                  run_time=0.7)

        # "four bounded databases" — the cylinders, one per spoken name
        self.pad_to(A("four bounded databases") - 0.7)
        self.play(FadeOut(VGroup(server, s_lab, rows, shade, bb, q_arrow, answer,
                                 sender, sd_lab, wbox, wlab, token, promise)),
                  run_time=0.6)
        dbs = four_dbs()
        cue = [A("per epoch memos"), A("first contact handshakes"),
               AA(["tack e grams and", "tachygrams and"]), A("address registry")]
        for g, t in zip(dbs, cue):
            self.pad_to(t - 0.3)
            self.play(FadeIn(g, shift=UP * 0.25), run_time=0.5)

        # "watch the tachygram one" — it feeds the spendability proofs
        self.pad_to(A("watch the") - 0.2)
        tg = dbs[2]
        others = VGroup(dbs[0], dbs[1], dbs[3])
        tg.generate_target()
        tg_highlight(tg.target)
        self.play(MoveToTarget(tg), others.animate.fade(0.5), run_time=0.9)
        self.pad_to(A("spendability proofs") - 1.0)
        card, c_lab = proof_card_group(tg)
        raw = VGroup(*[bead(STAR, 0.09).move_to(tg[0].get_center()) for _ in range(4)])
        self.add(raw)
        self.play(LaggedStart(*[b.animate.move_to(card.get_center() + 0.18 * RIGHT * (i - 1.5))
                                for i, b in enumerate(raw)], lag_ratio=0.15),
                  FadeIn(card), FadeIn(c_lab), run_time=1.0)
        self.play(FadeOut(raw), Indicate(card, color=GOLD, scale_factor=1.08), run_time=0.6)

        # "without revealing which note they hold"
        self.pad_to(A("which note they hold") - 0.5)
        hid = caption("the server never learns which note you hold", color=GOLD)
        self.play(FadeIn(hid, shift=UP * 0.15), run_time=0.8)
        self.pad_to(scene_T("7.1"))


# ---- 7.2 ----------------------------------------------------------------------

class Scene72(TimedScene):
    """7.2 — ML-KEM addresses and the tag schedule."""

    def construct(self):
        A = lambda p, o=1: anchor("7.2", p, o)
        AA = lambda ps, o=1: anchor_any("7.2", ps, o)

        # Reconstruct 7.1's final frame exactly: title, four databases with the
        # tachygram one highlighted, the spendability card, the closing caption.
        prev_title = scene_title("the payment protocol", color=CYAN)
        prev_dbs = four_dbs()
        tg_highlight(prev_dbs[2])
        for k in (0, 1, 3):
            prev_dbs[k].fade(0.5)
        p_card, p_clab = proof_card_group(prev_dbs[2])
        p_cap = caption("the server never learns which note you hold", color=GOLD)
        self.add(prev_title, prev_dbs, p_card, p_clab, p_cap)

        # "an address is two keys"
        title = scene_title("an address is two keys")
        card = panel(10.4, 4.3, color=GOLD, fill_opacity=0.05).move_to(UP * 0.05)
        addr_eq = mtex('"addr" = ("pk", thin "ek")', size=FS_HEAD + 10, color=STAR)
        addr_eq.move_to(card.get_center() + UP * 1.2)
        pk_chip = tex_chip('"pk"', color=GOLD, size=FS_HEAD + 4, pad=0.22)
        ek_chip = tex_chip('"ek"', color=AMBER, size=FS_HEAD + 4, pad=0.22)
        pk_chip.move_to(card.get_center() + DOWN * 0.15 + LEFT * 2.5)
        ek_chip.move_to(card.get_center() + DOWN * 0.15 + RIGHT * 2.5)
        met = itex("the payment key you've met", size=FS_BODY, color=TXT)
        met.next_to(pk_chip, DOWN, buff=0.35)
        kem = itex("ML-KEM encapsulation key", size=FS_BODY, color=TXT)
        kem.next_to(ek_chip, DOWN, buff=0.35)
        self.wait(0.3)
        self.play(FadeOut(VGroup(prev_dbs, p_card, p_clab), shift=DOWN * 0.3),
                  FadeOut(p_cap), *swap_title(prev_title, title), run_time=0.8)
        self.play(FadeIn(card), Write(addr_eq), run_time=1.0)
        self.pad_to(A("payment key") - 0.3)
        self.play(FadeIn(pk_chip, scale=1.15), FadeIn(met, shift=UP * 0.1), run_time=0.7)
        self.pad_to(A("encapsulation key for") - 0.2)
        self.play(FadeIn(ek_chip, scale=1.15), FadeIn(kem, shift=UP * 0.1), run_time=0.7)
        self.pad_to(A("minted fresh") - 0.3)
        fresh = caption("both minted fresh for every sender", color=STAR)
        self.play(FadeIn(fresh, shift=UP * 0.15),
                  Indicate(VGroup(pk_chip, ek_chip), color=STAR, scale_factor=1.06),
                  run_time=0.9)

        # "the diversified-address trick is gone" — Orchard flashback (legacy colors)
        self.pad_to(A("diversified address trick") - 0.7)
        title2 = scene_title("why diversification dies")
        addr_pill = pill('"addr" = ("pk", "ek")', color=GOLD, size=FS_LABEL, math=True)
        addr_pill.to_corner(UR, buff=0.3)
        self.play(FadeOut(VGroup(met, kem, fresh, card, pk_chip, ek_chip)),
                  ReplacementTransform(addr_eq, addr_pill[1]), FadeIn(addr_pill[0]),
                  *swap_title(title, title2), run_time=1.1)
        # the tree fills the left column top to bottom
        LX = -3.85
        ivk = kbox(['"ivk"'], PNG_IVK, size=36)
        ivk.move_to(RIGHT * LX + DOWN * 1.45)
        addrs = VGroup(*[kbox([f'"addr"_(d_{i})'], PNG_ADDR, size=30) for i in (1, 2, 3)])
        addrs.arrange(RIGHT, buff=0.4).move_to(RIGHT * LX + UP * 1.85)
        if addrs.get_left()[0] < -6.45:
            addrs.shift(RIGHT * (-6.45 - addrs.get_left()[0]))
        ivk.set_x(addrs.get_x())
        arrows = VGroup(*[karrow(ivk.get_top() + UP * 0.08, a.get_bottom() + DOWN * 0.08)
                          for a in addrs])
        orch = label("Orchard", size=FS_LABEL, color=MUT).next_to(ivk, DOWN, buff=0.25)
        self.pad_to(A("orchard mints") - 0.4)
        self.play(FadeIn(ivk), FadeIn(orch), run_time=0.7)
        self.play(LaggedStart(*[AnimationGroup(ShowCreation(ar), FadeIn(a, shift=UP * 0.15))
                                for ar, a in zip(arrows, addrs)], lag_ratio=0.2),
                  run_time=1.3)

        # "all decrypt under one incoming viewing key"
        self.pad_to(A("one incoming viewing key") - 0.4)
        self.play(ivk.animate(rate_func=there_and_back).scale(1.15),
                  *[ar[0].animate(rate_func=there_and_back).set_stroke(GOLD, 4.0)
                    for ar in arrows], run_time=1.0)

        # "the algebra behind that is discrete log" — right-hand argument column
        RX = 3.75
        self.pad_to(A("discrete log") - 0.8)
        dlog = mtex('"addr"_d = ["ivk"] thin G_d', size=FS_HEAD, color=TXT)
        dlog.move_to(RIGHT * RX + UP * 2.05)
        dl_tag = itex("discrete log", size=FS_LABEL, color=MUT).next_to(dlog, DOWN, buff=0.2)
        self.play(Write(dlog), FadeIn(dl_tag), run_time=1.0)

        # "a future quantum adversary ... retroactively"
        self.pad_to(A("quantum adversary") - 0.3)
        qa = pill("quantum adversary", color=FLARE, size=FS_LABEL)
        qa.move_to(RIGHT * RX + UP * 0.3)
        self.play(FadeIn(qa, scale=1.15), run_time=0.6)
        bolt = tarrow(qa, dl_tag, color=FLARE, width=SW, buff=0.1)
        self.play(ShowCreation(bolt), dlog.animate.set_color(FLARE), run_time=0.8)
        self.pad_to(A("retroactively") - 0.4)
        self.play(ivk[0].animate.set_stroke(FLARE, 4.0, 1.0), run_time=0.7)
        self.pad_to(A("entire incoming history") - 0.5)
        self.play(LaggedStart(*[a[0].animate.set_stroke(FLARE, 4.0, 1.0) for a in addrs],
                              lag_ratio=0.15),
                  *[ar[0].animate.set_stroke(FLARE, 3.0) for ar in arrows],
                  *[ar[1].animate.set_fill(FLARE) for ar in arrows],
                  run_time=1.0)
        past = caption("one recovered key reads your entire incoming history", color=FLARE)
        self.play(FadeIn(past, shift=UP * 0.15), run_time=0.5)

        # "lattice KEMs offer no analogue"
        self.pad_to(A("lattice kems") - 0.4)
        kem_tag = label("ML-KEM:", size=FS_BODY, color=TXT)
        no_dk = label("no shared-key diversification", size=FS_BODY, color=MUT)
        kem_row = VGroup(kem_tag, no_dk).arrange(RIGHT, buff=0.25)
        kem_row.move_to(RIGHT * (RX - 0.55) + DOWN * 0.8)
        self.play(FadeIn(kem_row, shift=RIGHT * 0.2), run_time=0.7)
        x_nodk = x_mark(no_dk.get_right() + RIGHT * 0.42, 0.2, FLARE, SW_BOLD)
        self.play(ShowCreation(x_nodk), no_dk.animate.set_color(DIM), run_time=0.6)

        # "every sender gets a genuinely fresh key pair"
        self.pad_to(A("genuinely fresh") - 0.5)
        pairs = VGroup(*[tex_chip(f'("pk"_{i}, "ek"_{i})', color=GOLD, size=FS_LABEL, pad=0.14)
                         for i in (1, 2, 3)])
        pairs.arrange(RIGHT, buff=0.35).move_to(RIGHT * RX + DOWN * 2.15)
        senders = VGroup(*[label(f"sender {i}", size=FS_SMALL, color=MUT)
                           .next_to(p, UP, buff=0.15) for i, p in zip((1, 2, 3), pairs)])
        self.play(FadeOut(past),
                  LaggedStart(*[AnimationGroup(FadeIn(p, scale=1.1), FadeIn(s))
                                for p, s in zip(pairs, senders)], lag_ratio=0.2),
                  run_time=1.1)
        self.pad_to(A("convenience dies") - 0.4)
        conv = caption("gone: one key that scans everything", color=MUT)
        self.play(FadeIn(conv, shift=UP * 0.15), run_time=0.6)

        # "tags bring the convenience back" — the tag schedule stage
        self.pad_to(A("tags bring") - 0.6)
        flashback = VGroup(ivk, orch, addrs, arrows, dlog, dl_tag, qa, bolt,
                           kem_row, x_nodk, pairs, senders, conv)
        title3 = scene_title("the tag schedule", color=GOLD)
        self.play(FadeOut(flashback), *swap_title(title2, title3), run_time=1.0)
        self.pad_to(A("effective incoming viewing key") - 0.3)
        eff = mtex('"ivk"_("eff") = ("tag"_0, "tag"_1, dots, thin "dk")',
                   size=FS_HEAD, color=STAR)
        eff.move_to(UP * 2.05)
        self.play(Write(eff), run_time=1.2)

        # "for first contact, the tag is a hash of the encapsulation key"
        CH_Y = -0.45
        self.pad_to(A("for first contact") - 0.4)
        boxes = VGroup(*[lockbox(color=CYAN) for _ in range(5)])
        boxes.arrange(RIGHT, buff=0.95).move_to(UP * CH_Y)
        blinks = VGroup(*[chain_link(boxes[i][0], boxes[i + 1][0]) for i in range(4)])
        b0 = boxes[0]
        b0[0].set_stroke(AMBER, SW_BOLD, 1.0).set_fill(AMBER, 0.12)
        b0[1].set_stroke(AMBER)
        b0[2].set_color(AMBER)
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.15) for b in boxes], lag_ratio=0.1),
                  ShowCreation(blinks, lag_ratio=0.1), run_time=1.2)
        self.pad_to(A("hash of the encapsulation key") - 0.3)
        t0 = mtex('"tag"_0 = H("ek")', size=FS_LABEL, color=AMBER)
        t0.next_to(b0, DOWN, buff=0.3)
        self.play(Write(t0), Indicate(b0, color=AMBER, scale_factor=1.1), run_time=1.0)

        # "a single PIR lookup finds the handshake"
        self.pad_to(A("single PIR lookup") - 0.4)
        one = pill("one PIR query", color=STAR, size=FS_SMALL)
        one.next_to(b0, UP, buff=0.4)
        pulse = Circle(radius=0.8).set_stroke(STAR, SW, 1.0).move_to(b0)
        self.play(FadeIn(one, shift=DOWN * 0.1), ShowCreation(pulse), run_time=0.7)
        self.play(pulse.animate.scale(1.5).set_stroke(opacity=0), run_time=0.6)
        self.remove(pulse)

        # The handshake yields K; that same secret drives every later tag.
        shared = tex_chip('K', color=GOLD, size=FS_LABEL, pad=0.14)
        shared_lab = label("shared secret", size=FS_SMALL, color=GOLD)
        k_grp = VGroup(shared, shared_lab).arrange(RIGHT, buff=0.2)
        k_grp.next_to(boxes[1], UP, buff=0.4).align_to(boxes[1], LEFT)
        k_grp.match_y(one)
        seed = Dot(b0.get_center(), radius=0.09).set_fill(AMBER, 1.0)
        self.add(seed)
        self.play(seed.animate.move_to(shared.get_center()), run_time=0.6)
        self.play(FadeIn(k_grp), FadeOut(seed), run_time=0.4)

        # "every later note tags itself with a hash of the shared secret and a counter"
        self.pad_to(A("every later note") - 0.3)
        tis = VGroup(*[mtex(f'H(K, {i})', size=FS_LABEL, color=CYAN)
                       .next_to(boxes[i], DOWN, buff=0.3).match_y(t0) for i in (1, 2, 3, 4)])
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in tis], lag_ratio=0.15),
                  run_time=1.3)
        cursor = Triangle().scale(0.1).rotate(PI).set_fill(GOLD, 1).set_stroke(width=0)
        cursor.next_to(boxes[1], UP, buff=0.08)
        self.play(FadeIn(cursor), run_time=0.2)
        self.play(cursor.animate.next_to(boxes[4], UP, buff=0.08), run_time=0.9)
        self.play(FadeOut(cursor), run_time=0.2)

        # "random access" — hop straight to a later box, skipping the rest
        self.pad_to(A("random access") - 0.3)
        h0 = shared_lab.get_right() + RIGHT * 0.15
        h1 = boxes[3][1].get_top() + UP * 0.12
        arc = ArcBetweenPoints(h0, h1, angle=-0.7).set_stroke(GOLD, SW)
        u = normalize(arc.get_end() - arc.pfp(0.97))
        n = np.array([-u[1], u[0], 0])
        tip = Polygon(h1, h1 - 0.2 * u + 0.09 * n, h1 - 0.2 * u - 0.09 * n)
        tip.set_fill(GOLD, 1).set_stroke(width=0)
        hop = VGroup(arc, tip)
        ra = label("random access", size=FS_SMALL, color=GOLD)
        ra.next_to(arc.pfp(0.5), UP, buff=0.12)
        self.play(ShowCreation(hop), FadeIn(ra),
                  Indicate(boxes[3], color=GOLD, scale_factor=1.12), run_time=1.0)

        # "keeps the sequence opaque to everyone else"
        self.pad_to(A("sequence opaque") - 0.3)
        opq = caption("random access for you, opaque to everyone else", color=TXT)
        self.play(FadeIn(opq, shift=UP * 0.15), run_time=0.6)

        # "shrinks the wallet's persistent state to an index and a counter per channel"
        # (spec #discovery: per sender, the ek's HD index and the notes-seen count)
        self.pad_to(A("persistent state") - 0.3)
        state = tex_chip('"state" = ("idx"_"ek", thin n)', color=GOLD, size=FS_BODY, pad=0.18)
        st_lab = itex("per channel", size=FS_LABEL, color=GOLD)
        st_row = VGroup(state, st_lab).arrange(RIGHT, buff=0.35)
        st_row.move_to(DOWN * 2.4)
        self.play(FadeIn(state, scale=1.1), run_time=0.7)
        self.pad_to(A("per channel") - 0.2)
        self.play(FadeIn(st_lab, shift=LEFT * 0.1), run_time=0.5)

        # "the costs, stated honestly" — chain moves up, three cost columns below
        self.pad_to(A("costs stated honestly") - 0.6)
        title4 = scene_title("the costs", color=AMBER)
        sched = VGroup(boxes, blinks, t0, tis)
        self.play(FadeOut(VGroup(eff, k_grp, hop, ra, one, opq, st_row)),
                  *swap_title(title3, title4),
                  sched.animate.shift(UP * 2.35), run_time=0.9)

        COL_Y = -1.6
        self.pad_to(A("a kem ciphertext") - 0.3)
        # area-honest: 32 B square vs ~1 KB slab (32x the area)
        slab = Rectangle(width=2.4, height=0.95).set_fill(AMBER, 0.22).set_stroke(AMBER, SW, 1)
        epk = Square(side_length=np.sqrt(2.4 * 0.95 / 32)).set_fill(MUT, 0.9)
        epk.set_stroke(MUT, SW_THIN, 1)
        size_cmp = VGroup(epk, slab).arrange(RIGHT, buff=0.55, aligned_edge=DOWN)
        size_cmp.move_to(LEFT * 4.3 + UP * COL_Y)
        epk_lab = mtex('"epk"', size=FS_SMALL, color=MUT).next_to(epk, UP, buff=0.15)
        slab_in = rich([("KEM ciphertext", AMBER), ("$c$", AMBER)], size=FS_SMALL, buff=0.12)
        slab_in.move_to(slab)
        epk_sz = mtex('32 "B"', size=FS_SMALL, color=MUT)
        slab_sz = mtex('approx 1 "KB"', size=FS_LABEL, color=AMBER)
        self.play(FadeIn(epk), FadeIn(epk_lab), GrowFromCenter(slab), FadeIn(slab_in),
                  run_time=0.9)
        self.pad_to(A("kilobyte") - 0.2)
        slab_sz.next_to(slab, DOWN, buff=0.3)
        epk_sz.match_x(epk).align_to(slab_sz, DOWN)
        self.play(FadeIn(slab_sz, shift=UP * 0.1), FadeIn(epk_sz, shift=UP * 0.1), run_time=0.6)

        # "only first contact carries one, and follow-ups ride free"
        self.pad_to(A("only first contact") - 0.3)
        mini_box = Rectangle(width=0.85, height=0.42).set_fill(AMBER, 0.22)
        mini_box.set_stroke(AMBER, SW_THIN, 1)
        mini_c = mtex('c', size=FS_LABEL, color=AMBER)
        mini = VGroup(mini_box, mini_c).next_to(t0, DOWN, buff=0.2)
        mini_c.move_to(mini_box)
        self.play(TransformFromCopy(slab, mini_box), TransformFromCopy(slab_in[1], mini_c),
                  run_time=0.8)
        self.pad_to(AA(["notes ride free", "notes right free", "ride free",
                        "right free"]) - 0.3)
        frees = VGroup(*[label("free", size=FS_SMALL, color=GOLD).next_to(t, DOWN, buff=0.2)
                         .match_y(mini) for t in tis])
        self.play(LaggedStart(*[FadeIn(f, shift=UP * 0.1) for f in frees], lag_ratio=0.12),
                  run_time=0.8)

        # "unlinkable payments to the same recipient require separate channels"
        self.pad_to(A("separate channels") - 1.0)
        ch_a = VGroup(*[lockbox(0.55, 0.42, color=CYAN) for _ in range(3)]).arrange(RIGHT, buff=0.22)
        ch_b = VGroup(*[lockbox(0.55, 0.42, color=GOLD) for _ in range(3)]).arrange(RIGHT, buff=0.22)
        chans = VGroup(ch_a, ch_b).arrange(DOWN, buff=0.35)
        ch_lab = label("one channel each", size=FS_LABEL, color=TXT)
        ch_lab.align_to(slab_sz, DOWN)
        chans.next_to(ch_lab, UP, buff=0.3)
        VGroup(chans, ch_lab).set_x(0)
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.1) for b in [*ch_a, *ch_b]],
                              lag_ratio=0.08), FadeIn(ch_lab), run_time=1.0)

        # "the full address outgrows a QR code" — the registry serves it
        self.pad_to(A("qr code") - 0.8)
        qr = qr_glyph()
        reg = db_cyl(1.3, 0.9, color=CYAN)
        reg_lab = label("registry", size=FS_LABEL, color=CYAN)
        reg_lab.align_to(slab_sz, DOWN).set_x(4.4)
        qr.next_to(reg_lab, UP, buff=0.3).set_x(3.1)
        reg.match_y(qr).set_x(5.7)
        qx = x_mark(qr.get_center(), 0.55, FLARE, SW_BOLD)
        self.play(FadeIn(qr), run_time=0.5)
        self.play(ShowCreation(qx), run_time=0.5)
        self.pad_to(A("short digest") - 0.6)
        dig = mtex('H("addr")', size=FS_SMALL, color=CYAN).next_to(reg, UP, buff=0.22)
        reg_arrow = tarrow(qr.get_right(), reg.get_left(), color=CYAN, buff=0.15)
        self.play(FadeIn(reg), FadeIn(dig, shift=DOWN * 0.1), ShowCreation(reg_arrow),
                  FadeIn(reg_lab), run_time=0.9)

        # "the first is recovery" — state posted in the opaque data field
        self.pad_to(A("the first is recovery") - 1.0)
        title5 = scene_title("recovery", color=GOLD)
        cost_stage = VGroup(sched, mini, frees, epk, epk_lab, epk_sz, slab, slab_in, slab_sz,
                            chans, ch_lab, qr, qx, reg, dig, reg_arrow, reg_lab)
        self.play(FadeOut(cost_stage), FadeOut(addr_pill), *swap_title(title4, title5),
                  run_time=0.8)
        wbox, wlab, token = wallet_panel(UP * 1.2, w=3.0, h=2.0)
        blocks = VGroup(*[block(1.15, 0.72) for _ in range(8)])
        blocks.arrange(RIGHT, buff=0.42).move_to(DOWN * 1.35)
        links = VGroup(*[chain_link(blocks[i], blocks[i + 1]) for i in range(7)])
        tip = label("tip", size=FS_LABEL, color=MUT).next_to(blocks[-1], UP, buff=0.2)
        self.play(FadeIn(wbox), FadeIn(wlab), FadeIn(token),
                  LaggedStart(*[FadeIn(b) for b in blocks], lag_ratio=0.06),
                  ShowCreation(links, lag_ratio=0.06), FadeIn(tip), run_time=1.3)
        st_ct = key_chip("state", color=GOLD, size=FS_SMALL, pad=0.12)
        st_ct.move_to(wbox.get_center() + DOWN * 0.55)
        self.pad_to(A("minimal state") - 0.3)
        self.play(FadeIn(st_ct, scale=1.2), token.animate.shift(UP * 0.25), run_time=0.5)
        self.pad_to(A("on chain encrypted") - 0.3)
        self.play(st_ct.animate.move_to(blocks[2]), run_time=0.9)
        enc = caption("posted on chain, encrypted", color=GOLD)
        self.play(FadeIn(enc, shift=UP * 0.15),
                  blocks[2].animate.set_stroke(GOLD, SW, 0.9), run_time=0.5)
        self.pad_to(A("opaque data field") - 0.4)
        da = label("opaque data field", size=FS_SMALL, color=MUT)
        da.next_to(blocks[2], DOWN, buff=0.36)
        self.play(FadeIn(da, shift=UP * 0.1), run_time=0.6)

        # "a wallet starting from a bare mnemonic scans backward from the tip"
        self.pad_to(AA(["bare mnemonic", "bear mnemonic"]) - 0.5)
        mn = key_chip("mnemonic", color=GOLD, size=FS_LABEL)
        mn.move_to(wbox.get_center())
        self.play(FadeOut(token), FadeIn(mn), FadeOut(enc), run_time=0.5)
        sweep = RoundedRectangle(width=1.4, height=0.98, corner_radius=0.1)
        sweep.set_stroke(GOLD, SW, 0.95).set_fill(GOLD, 0.06).move_to(blocks[7])
        back_lab = caption("scan backward from the tip", color=GOLD)
        self.play(FadeIn(sweep), FadeIn(back_lab, shift=UP * 0.15), run_time=0.4)
        self.play(sweep.animate.move_to(blocks[2]), run_time=2.4)
        self.pad_to(A("decrypts it") - 0.3)
        back = st_ct.copy()
        self.play(back.animate.move_to(wbox.get_center() + DOWN * 0.55),
                  FadeOut(sweep), run_time=0.9)
        token.move_to(wbox.get_center() + UP * 0.25)
        self.play(FadeOut(mn), FadeIn(token), run_time=0.5)
        resume = caption("decrypt, resume fast sync", color=GOLD)
        self.play(FadeOut(back_lab), FadeIn(resume, shift=UP * 0.15), run_time=0.5)

        # "the second is Faerie gold" — the nullifier check at the door
        self.pad_to(AA(["fairy gold", "faerie gold"]) - 1.0)
        title6 = scene_title("Faerie gold", color=FLARE)
        ROW_Y = 0.55
        W_C = LEFT * 4.5 + UP * ROW_Y
        held = VGroup(*[bead(GOLD, 0.13) for _ in range(4)]).arrange(RIGHT, buff=0.4)
        held.move_to(W_C + DOWN * 0.1)
        h_lab = label("notes you hold", size=FS_LABEL, color=GOLD)
        h_lab.next_to(W_C + DOWN * 1.0, DOWN, buff=0.18)
        self.play(FadeOut(VGroup(blocks, links, tip, st_ct, da, back, resume, token)),
                  *swap_title(title5, title6),
                  wbox.animate.move_to(W_C),
                  FadeTransform(wlab, h_lab), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(b, scale=1.3) for b in held], lag_ratio=0.15),
                  run_time=0.6)
        note = bead(CYAN, 0.15).move_to(RIGHT * 5.5 + UP * ROW_Y)
        n_lab = label("incoming note", size=FS_LABEL, color=CYAN).next_to(note, UP, buff=0.2)
        self.play(FadeIn(note, scale=1.4), FadeIn(n_lab), run_time=0.6)
        sponge = sponge_icon(2.0, 1.2)
        sponge[2].scale(1.25).next_to(sponge[0], DOWN, buff=0.12)
        sponge.move_to(RIGHT * 1.3 + UP * ROW_Y)
        sponge.shift(UP * (ROW_Y - sponge[0].get_center()[1]))
        self.pad_to(A("computes its nullifier") - 0.4)
        self.play(FadeIn(sponge, scale=1.05), FadeOut(n_lab),
                  note.animate.move_to(sponge[0].get_right() + LEFT * 0.35),
                  run_time=0.9)
        self.pad_to(A("reference epoch") - 0.4)
        nf_ref = mtex('"nf"_("ref") = f_("mk")(e_("ref"))', size=FS_BODY, color=STAR)
        nf_ref.next_to(sponge, DOWN, buff=0.3)
        self.play(Write(nf_ref), run_time=0.9)
        self.pad_to(A("compares it") - 0.3)
        cmp = tarrow(sponge[0].get_left(), wbox.get_right(), color=STAR, buff=0.12)
        cmp_lab = label("compare", size=FS_SMALL, color=MUT).next_to(cmp, UP, buff=0.12)
        self.play(ShowCreation(cmp), FadeIn(cmp_lab), run_time=0.8)

        # "a reused psi collides immediately"
        self.pad_to(A("reused psi") - 0.3)
        dup = bead(FLARE, 0.13).move_to(sponge[0].get_center())
        self.add(dup)
        self.play(dup.animate.move_to(held[1].get_center()), run_time=0.9)
        self.pad_to(A("collides") - 0.2)
        clash = Circle(radius=0.32).set_stroke(FLARE, SW_BOLD, 1.0).move_to(held[1])
        col = rich([("reused", FLARE), ("$psi$", FLARE), (": collision", FLARE)],
                   size=FS_LABEL, buff=0.1)
        col[2].shift(LEFT * 0.08)
        col.next_to(h_lab, DOWN, buff=0.3)
        self.play(ShowCreation(clash), FadeIn(col, shift=UP * 0.1), run_time=0.6)

        # "a targeted collision would be a second preimage on the PRF"
        self.pad_to(A("second pre image") - 0.8)
        tgt = rich([("targeted collision", TXT), ("$=>$", MUT),
                    ("a second preimage on the PRF", FLARE)], size=FS_BODY)
        tgt.move_to(RIGHT * 2.0 + DOWN * 2.05)
        self.play(FadeIn(tgt, shift=UP * 0.15), run_time=0.8)

        # "both attacks get caught at the door"
        self.pad_to(A("caught at the door") - 0.4)
        door = caption("both attacks: caught at the door", color=GOLD)
        self.play(FadeIn(door, shift=UP * 0.15),
                  wbox.animate.set_stroke(GOLD, SW_BOLD, 1.0), run_time=0.9)
        self.pad_to(scene_T("7.2"))

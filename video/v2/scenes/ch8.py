"""Chapter 8 — Quantum posture, and the cascade (scenes 8.1, 8.2).

Ported from v1's anim/act8.py (Alex: its audit table and cascade are better), re-anchored
to v2's 8.1/8.2 narration (v1 text, regenerated in the v2 voice).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from style import *  # noqa: E402,F403
from style import _esc_typst  # noqa: E402


# ---- baseline-true text (local; proposed for style.py) -----------------------
# label()/heading() are positioned by their INK box, so "privacy" (descenders)
# and "soundness" (none) sit at different baselines when both are move_to'd to
# one y. tl() compiles each string after a '|' strut (identical metrics for every
# string at one size), records where the strut's centre was, then drops it:
# at_y(m, y) puts the LINE centre at y, so siblings share a baseline.

def tl(s, size=FS_BODY, color=TXT, bold=False):
    """One run of text (or $math$) whose line box, not ink, is used for placement."""
    is_math = s.startswith("$") and s.endswith("$") and len(s) > 1
    body = s if is_math else _esc_typst(s)
    if bold:
        body = f'#text(weight: "bold")[{body}]'
    m = mtex("|" + body, size=size, color=color, math=False)
    strut = m.submobjects[0]
    m.remove(strut)
    m.line_c_off = strut.get_center()[1] - m.get_bottom()[1]
    m.base_h = max(m.get_height(), 1e-6)
    m.lint_text = s[:40]
    return m


def at_y(m, y):
    """Shift m so its line centre (not its ink centre) sits at y."""
    m.shift(UP * (y - m.get_bottom()[1] - m.line_c_off))
    return m


def row(parts, size=FS_BODY, buff=0.16):
    """Runs on one shared baseline: parts = [(text, color[, bold]), ...]."""
    runs = VGroup()
    x = 0.0
    for p in parts:
        m = tl(p[0], size=size, color=p[1], bold=(len(p) > 2 and p[2]))
        at_y(m, 0.0)
        m.shift(RIGHT * (x - m.get_left()[0]))
        x = m.get_right()[0] + buff
        runs.add(m)
    runs.line_c_off = -runs.get_bottom()[1]
    return runs


def title_at(s, color=STAR, size=FS_TITLE):
    return at_y(tl(s, size=size, color=color, bold=True), TITLE_Y)


# ---- act-local glyphs ----------------------------------------------------------

def broken_x(center, size=0.16, color=FLARE):
    return VGroup(
        Line(center + size * UL, center + size * DR, stroke_width=SW_BOLD,
             stroke_color=color),
        Line(center + size * UR, center + size * DL, stroke_width=SW_BOLD,
             stroke_color=color),
    )


def status(text, y, x_left, color=GOLD, mark=True, size=FS_LABEL):
    """A table verdict: drawn checkmark + word (no ✓ glyph, so no font fallback)."""
    t = at_y(tl(text, size=size, color=color), y)
    if not mark:
        t.align_to([x_left, 0, 0], LEFT)
        return VGroup(t)
    ck = checkmark(0.3, color)
    ck.set_stroke(width=4)
    ck.move_to([x_left, y, 0], aligned_edge=LEFT)
    t.next_to(ck, RIGHT, buff=0.16)
    at_y(t, y)
    return VGroup(ck, t)


def url_label(url, size, color):
    """A URL as plain text: typst markup would auto-link it, and the link's hit-box
    would load as a filled rectangle over the text."""
    return mtex(f'#"{url}"', size=size, color=color, math=False)


def title_pair(size=FS_TITLE):
    """'private today -> sound after an upgrade' — the act's thesis line."""
    p = row([("private today", GOLD, True), ("$->$", MUT),
             ("sound after an upgrade", CYAN, True)], size=size, buff=0.3)
    return p


def tbd_card():
    """8.1's closing card (also 8.2's opening frame): the lattice slot, still open."""
    tbd = at_y(tl("to be determined", size=56, color=STAR, bold=True), 0.38)
    tbd.set_x(0)
    sub = at_y(tl("by design, not blocked", size=FS_BODY, color=GOLD), -0.5)
    sub.set_x(0)
    box = panel(tbd.get_width() + 1.6, 2.3, color=CYAN, fill_opacity=0.05)
    box.move_to([0, -0.04, 0])
    return box, tbd, sub


def breathe(mob, amp=0.012, speed=0.9):
    """Slow scale breathing for raster/heavy mobjects (shimmer works on fills only)."""
    mob.breath_t = 0.0
    mob.breath_h = mob.get_height()

    def up(m, dt):
        m.breath_t += dt
        m.set_height(m.breath_h * (1 + amp * math.sin(speed * m.breath_t)))
    mob.add_updater(up)


# 8.1 audit table geometry (left ~60% of the stage; rk explainer on the right).
# While only the table is on screen it sits centred (offset TX); it slides left
# when the rk explainer needs the right column.
COL_OBJ = -5.75     # object chip centers
COL_ASM = -4.75     # assumption column left edge
COL_ST = -1.55      # verdict column left edge
TAB_X0, TAB_X1 = -6.7, 1.95
TX = -(TAB_X0 + TAB_X1) / 2
ROW_Y = [1.45, 0.72, -0.01, -0.74, -1.47, -2.2]
HEAD_Y = 2.3
EXPL_X = 4.3        # rk explainer column center


class Scene81(TimedScene):
    """8.1 — Private today, sound after an upgrade."""

    def construct(self):
        SID = "8.1"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731

        # ---- the stance ------------------------------------------------------
        title1 = title_at("the quantum question")
        self.pad_to(A("quantum one") - 0.5)
        self.play(FadeIn(title1, shift=UP * 0.2), run_time=0.8)

        # the thesis lands big on stage, half by half, on its words ...
        thesis = title_pair(size=58)
        thesis.move_to(UP * 0.2)
        self.pad_to(A("private today") - 0.3)
        self.play(FadeIn(thesis[0], shift=UP * 0.15),
                  FadeOut(title1, shift=UP * 0.3), run_time=0.7)
        self.pad_to(A("sound after") - 0.3)
        self.play(FadeIn(thesis[1], shift=RIGHT * 0.15),
                  FadeIn(thesis[2], shift=UP * 0.15), run_time=0.7)

        # ... then rises into the title band as the two panels open beneath it
        title2 = title_pair().move_to(UP * TITLE_Y)
        at_y(title2, TITLE_Y)
        PW, PH = 6.4, 5.3
        priv = panel(PW, PH, color=GOLD).move_to(LEFT * 3.4)
        snd = panel(PW, PH, color=CYAN).move_to(RIGHT * 3.4)
        hy = priv.get_top()[1] - 0.55
        priv_h = at_y(tl("privacy", size=FS_HEAD, color=GOLD, bold=True), hy)
        priv_h.set_x(priv.get_x())
        snd_h = at_y(tl("soundness", size=FS_HEAD, color=CYAN, bold=True), hy)
        snd_h.set_x(snd.get_x())
        add_shimmer([priv, snd], amp=0.18, speed=1.1)
        self.pad_to(A("asymmetry") - 0.3)
        self.play(ReplacementTransform(thesis, title2), run_time=0.9)
        self.play(ShowCreation(priv), ShowCreation(snd),
                  FadeIn(priv_h, shift=DOWN * 0.1), FadeIn(snd_h, shift=DOWN * 0.1),
                  run_time=0.9)

        # privacy: must hold retroactively; harvest now, decrypt later
        priv_sub = at_y(tl("must hold retroactively", size=FS_BODY), hy - 0.62)
        priv_sub.set_x(priv.get_x())
        self.pad_to(A("retroactively") - 0.4)
        self.play(FadeIn(priv_sub, shift=UP * 0.1), run_time=0.6)

        blocks = VGroup(*[block(0.8, 0.56) for _ in range(5)])
        blocks.arrange(RIGHT, buff=0.36).move_to(priv.get_center() + UP * 0.3)
        links = VGroup(*[chain_link(blocks[i], blocks[i + 1]) for i in range(4)])
        chain_l = tl("today's chain", size=FS_SMALL, color=MUT)
        chain_l.next_to(blocks, UP, buff=0.16)
        archive = panel(4.6, 0.9, color=FLARE, fill_opacity=0.06)
        archive.move_to(priv.get_center() + DOWN * 0.8)
        self.pad_to(A("today's chain") - 0.3)
        self.play(LaggedStart(*[FadeIn(b, shift=RIGHT * 0.1) for b in blocks],
                              lag_ratio=0.12),
                  LaggedStart(*[ShowCreation(l) for l in links], lag_ratio=0.12),
                  FadeIn(chain_l), run_time=0.9)
        hcopy = blocks.copy()
        self.pad_to(A("harvested now") - 0.2)
        self.play(ShowCreation(archive),
                  hcopy.animate.scale(0.62).move_to(archive.get_center()).fade(0.2),
                  run_time=1.2)
        harv = row([("harvest now", FLARE), ("$->$", FLARE), ("decrypt later", FLARE)],
                   size=FS_LABEL, buff=0.18)
        harv.set_x(priv.get_x())
        at_y(harv, archive.get_bottom()[1] - 0.36)
        self.pad_to(A("hardware arrives") - 0.4)
        self.play(FadeIn(harv, shift=UP * 0.1), run_time=0.6)
        pq_chip = key_chip("already post-quantum", color=GOLD, size=FS_LABEL)
        pq_chip.move_to(priv.get_bottom() + UP * 0.5)
        add_shimmer([pq_chip[0]], amp=0.18, speed=1.3)
        self.pad_to(A("already be post quantum") - 0.3)
        self.play(FadeIn(pq_chip, shift=UP * 0.15), run_time=0.7)

        # soundness: nobody forges, nobody steals — only at spend time
        snd_rows = bullets([tl("nobody forges"), tl("nobody steals")],
                           mark_color=CYAN, buff=0.36)
        snd_rows.move_to(snd.get_center() + UP * 0.55)
        self.pad_to(A("nobody forges") - 0.4)
        self.play(FadeIn(snd_rows[0], shift=RIGHT * 0.2), run_time=0.5)
        self.pad_to(A("nobody steals") - 0.2)
        self.play(FadeIn(snd_rows[1], shift=RIGHT * 0.2), run_time=0.5)
        snd_sub = at_y(tl("only matters at spend time", size=FS_BODY), -0.8)
        snd_sub.set_x(snd.get_x())
        self.pad_to(A("spend time") - 0.5)
        self.play(FadeIn(snd_sub, shift=UP * 0.1), run_time=0.6)
        wait_chip = key_chip("can wait for an upgrade", color=CYAN, size=FS_LABEL)
        wait_chip.move_to(snd.get_bottom() + UP * 0.5)
        add_shimmer([wait_chip[0]], amp=0.18, speed=1.3)
        self.pad_to(A("coordinated network upgrade") - 0.3)
        self.play(FadeIn(wait_chip, shift=UP * 0.15), run_time=0.7)

        # ---- the audit table ---------------------------------------------------
        off = [TX]          # current table x-offset (centred until the rk beat)
        table = []          # every table mobject that slides with it

        def tc(m):
            m.shift(RIGHT * off[0])
            table.append(m)
            return m

        hdrs = VGroup(
            at_y(tl("on chain", size=FS_LABEL, color=MUT), HEAD_Y).set_x(COL_OBJ),
            at_y(tl("assumption", size=FS_LABEL, color=MUT), HEAD_Y)
            .align_to([COL_ASM, 0, 0], LEFT),
            at_y(tl("against a quantum adversary", size=FS_LABEL, color=MUT), HEAD_Y)
            .align_to([COL_ST, 0, 0], LEFT),
        )
        tc(hdrs)
        rule = tc(Line([TAB_X0, HEAD_Y - 0.33, 0], [TAB_X1, HEAD_Y - 0.33, 0],
                       stroke_width=SW_THIN, stroke_color=DIM))
        objs = ['"pk", "cm"', '"nf"_e', '"memo"', '"cv"', '"rk"', '"bsk"']
        chips = VGroup(*[tex_chip(t, color=STAR, size=FS_LABEL, pad=0.12).move_to([COL_OBJ, y, 0])
                         for t, y in zip(objs, ROW_Y)])
        tc(chips)

        def asm(text, i, color=TXT):
            m = at_y(tl(text, size=FS_LABEL, color=color), ROW_Y[i])
            return tc(m.align_to([COL_ASM, 0, 0], LEFT))

        def verdict(text, i, color=GOLD, mark=True):
            return tc(status(text, ROW_Y[i], COL_ST, color=color, mark=mark))

        def row_bar(i, color=FLARE):
            r = RoundedRectangle(width=TAB_X1 - TAB_X0, height=0.64, corner_radius=0.12)
            r.set_fill(color, 0.08)
            r.set_stroke(color, SW_THIN, 0.9)
            return r.move_to([(TAB_X0 + TAB_X1) / 2 + off[0], ROW_Y[i], 0])

        # "audit today's chain": the chain's blocks become the on-chain objects
        rest = VGroup(priv, priv_h, priv_sub, links, chain_l, hcopy, archive, harv,
                      pq_chip, snd, snd_h, snd_rows, snd_sub, wait_chip)
        src = list(blocks) + [blocks[-1].copy()]
        self.pad_to(A("audit todays chain|audit today's chain") - 0.3)
        clear_shimmer([priv, snd, pq_chip[0], wait_chip[0]])   # else fills re-assert
        self.play(FadeOut(rest), run_time=0.5)
        self.play(LaggedStart(*[ReplacementTransform(b, c[0]) for b, c in zip(src, chips)],
                              lag_ratio=0.08),
                  LaggedStart(*[FadeIn(c[1]) for c in chips], lag_ratio=0.08),
                  FadeIn(hdrs), ShowCreation(rule), run_time=1.1)
        self.remove(*[c[0] for c in chips], *[c[1] for c in chips])
        self.add(chips)
        add_shimmer([c[0] for c in chips], amp=0.15, speed=1.4)

        bar = row_bar(0)
        self.pad_to(A("owner fields") - 0.3)
        self.play(FadeIn(bar), run_time=0.5)
        a0, v0 = asm("Poseidon", 0), verdict("post-quantum", 0)
        self.pad_to(A("Poseidon") - 0.2)
        self.play(FadeIn(a0), FadeIn(v0, shift=RIGHT * 0.15), run_time=0.6)
        self.pad_to(A("nullifiers") - 0.2)
        self.play(bar.animate.move_to(row_bar(1)), run_time=0.5)
        a1, v1 = asm("PRF", 1), verdict("post-quantum", 1)
        self.pad_to(A("prf outputs") - 0.2)
        self.play(FadeIn(a1), FadeIn(v1, shift=RIGHT * 0.15), run_time=0.6)
        self.pad_to(A("memos") - 0.2)
        self.play(bar.animate.move_to(row_bar(2)), run_time=0.5)
        a2, v2 = asm("ML-KEM + symmetric", 2), verdict("post-quantum", 2)
        self.pad_to(A("ml chem|ml kem") - 0.1)
        self.play(FadeIn(a2), FadeIn(v2, shift=RIGHT * 0.15), run_time=0.6)
        self.pad_to(A("quantum safe already") - 0.3)
        self.play(FadeOut(bar),
                  *[Indicate(v, color=GOLD, scale_factor=1.12) for v in (v0, v1, v2)],
                  run_time=0.9)

        # "the discrete-log survivors are three"
        dl = VGroup(*[asm("discrete log", i, AMBER) for i in (3, 4, 5)])
        self.pad_to(A("survivors") - 0.5)
        self.play(LaggedStart(*[FadeIn(m, shift=RIGHT * 0.15) for m in dl],
                              lag_ratio=0.15),
                  *[chips[i].animate.set_color(AMBER) for i in (3, 4, 5)],
                  run_time=1.0)
        bar = row_bar(3, AMBER)
        self.pad_to(A("value commitments") - 0.1)
        self.play(FadeIn(bar), run_time=0.4)
        self.pad_to(A("randomized keys") - 0.1)
        self.play(bar.animate.move_to(row_bar(4)), run_time=0.4)
        self.pad_to(A("binding key") - 0.1)
        self.play(bar.animate.move_to(row_bar(5)), run_time=0.4)

        # cv is perfectly hiding — nothing to decrypt
        v3 = verdict("perfectly hiding", 3)
        self.pad_to(A("perfectly hiding") - 0.3)
        self.play(bar.animate.move_to(row_bar(3)), FadeIn(v3, shift=RIGHT * 0.15),
                  run_time=0.7)

        # rk under the quantum attack: the table makes room on the right
        rk_eq = mtex('"rk" = ["ask" + alpha] G', size=FS_BODY, color=STAR)
        rk_eq.move_to([EXPL_X, 1.95, 0])
        shift_back = off[0]
        off[0] = 0.0
        self.pad_to(A("the randomized key") - 0.3)
        self.play(*[m.animate.shift(LEFT * shift_back) for m in table],
                  bar.animate.move_to(row_bar(4)), run_time=0.9)
        self.play(FadeIn(rk_eq, shift=LEFT * 0.2), run_time=0.6)
        askalpha = mtex('"ask" + alpha', size=FS_HEAD + 6, color=STAR)
        askalpha.move_to([EXPL_X, 0.45, 0])
        dlog = tarrow(rk_eq, askalpha, color=FLARE, width=SW, buff=0.14)
        dlog_l = tl("quantum DLog", size=FS_SMALL, color=FLARE)
        dlog_l.next_to(dlog, RIGHT, buff=0.18)
        self.pad_to(A("takes its discrete log") - 0.2)
        self.play(GrowFromPoint(dlog, dlog[0].get_start()), FadeIn(dlog_l), run_time=0.7)
        self.pad_to(A("sk plus alpha|ask plus alpha") - 0.2)
        self.play(TransformFromCopy(rk_eq[4:9], askalpha), run_time=0.9)
        mask = row([("$alpha =$", AMBER), ("a fresh PRF mask", TXT)], size=FS_LABEL,
                   buff=0.14)
        mask.set_x(EXPL_X)
        at_y(mask, askalpha.get_bottom()[1] - 0.42)
        self.pad_to(A("alpha is") - 0.3)
        self.play(FadeIn(mask, shift=UP * 0.12), run_time=0.7)

        ident = key_chip("your identity", color=GOLD, size=FS_LABEL)
        ident.move_to([EXPL_X, -2.05, 0])
        dash = DashedLine(mask.get_bottom() + DOWN * 0.12, ident.get_top() + UP * 0.08,
                          stroke_color=MUT, stroke_width=SW_THIN)
        self.pad_to(A("random looking") - 0.3)
        self.play(FadeIn(ident), ShowCreation(dash), run_time=0.8)
        bx = broken_x(dash.get_center())
        v4 = verdict("links to nothing", 4)
        self.pad_to(A("linkable to nothing") - 0.2)
        self.play(ShowCreation(bx), FadeIn(v4, shift=RIGHT * 0.15), run_time=0.7)

        # verdict: forgery — theft, not exposure — the half that can wait
        v5 = verdict("forgery possible", 5, color=FLARE, mark=False)
        head = [("quantum power today", TXT), ("$=>$", MUT), ("forgery", FLARE, True)]
        vl = row(head)
        vl.set_x(0)
        at_y(vl, CAPTION_Y)
        self.pad_to(A("is forgery") - 0.4)
        self.play(bar.animate.move_to(row_bar(5)), FadeIn(v5, shift=RIGHT * 0.15),
                  FadeIn(vl, shift=UP * 0.15), run_time=0.8)
        full = row(head + [("—", MUT), ("theft, not exposure", TXT)])
        full.set_x(0)
        at_y(full, CAPTION_Y)
        self.pad_to(A("theft") - 0.1)
        self.play(*[m.animate.move_to(f) for m, f in zip(vl, full[:3])],
                  FadeIn(full[3:], shift=LEFT * 0.15), run_time=0.6)
        full2 = row(head + [("—", MUT), ("the half that can wait", CYAN)])
        full2.set_x(0)
        at_y(full2, CAPTION_Y)
        self.pad_to(A("allowed to wait") - 0.4)
        self.play(*[m.animate.move_to(f) for m, f in zip(vl, full2[:3])],
                  full[3].animate.move_to(full2[3]),
                  FadeOut(full[4], shift=UP * 0.15),
                  FadeIn(full2[4], shift=UP * 0.15),
                  run_time=0.8)

        # ---- the upgrade: two swaps -------------------------------------------
        audit = VGroup(*table, bar, v4, v5, rk_eq, dlog, dlog_l, askalpha, mask, ident,
                       dash, bx, vl, full[3], full2[4])
        up_title = title_at("two coordinated swaps")
        self.pad_to(A("upgrade comes") - 0.3)
        clear_shimmer([c[0] for c in chips])
        self.play(FadeOut(audit),
                  LaggedStart(FadeOut(title2, shift=UP * 0.3),
                              FadeIn(up_title, shift=UP * 0.3), lag_ratio=0.6),
                  run_time=1.0)

        # swap 1: authorization. Centred while it is the only thing on stage;
        # slides into the left column when the PCD proof needs the right one.
        SX = 3.3
        LX0 = -6.6
        head1 = at_y(tl("first swap: authorization", size=FS_HEAD, color=GOLD,
                        bold=True), 2.3)
        head1.set_x(0)
        self.pad_to(A("first authorization") - 0.2)
        self.play(FadeIn(head1, shift=UP * 0.2), run_time=0.7)

        pq_sig = pill("post-quantum signature", color=CYAN)
        rr = pill("re-randomize", color=MUT)
        sig_row = VGroup(pq_sig, rr).arrange(RIGHT, buff=0.95)
        sig_row.move_to([LX0 + 3.3 + SX, 1.25, 0])
        arr_pr = tarrow(pq_sig, rr, color=MUT, width=SW, buff=0.12)
        sub_dl = tl("re-randomization is intrinsically discrete-log",
                    size=FS_SMALL, color=FLARE)
        sub_dl.next_to(sig_row, DOWN, buff=0.24)
        self.pad_to(A("intrinsically discrete log") - 0.6)
        self.play(FadeIn(pq_sig, shift=RIGHT * 0.15), FadeIn(rr, shift=RIGHT * 0.15),
                  GrowFromPoint(arr_pr, arr_pr[0].get_start()),
                  FadeIn(sub_dl), run_time=0.9)
        prx = broken_x(arr_pr[0].get_center(), size=0.16)
        self.pad_to(A("signature does it") - 0.2)
        self.play(ShowCreation(prx), run_time=0.5)

        # the circuit: prove knowledge of a signature instead
        circuit = panel(6.6, 2.2, color=STAR, fill_opacity=0.04)
        circuit.move_to([LX0 + 3.3 + SX, -1.35, 0])
        add_shimmer([circuit], amp=0.18, speed=1.2)
        circ_h = tl("in circuit, in zero knowledge", size=FS_SMALL, color=MUT)
        circ_h.move_to(circuit.get_top() + DOWN * 0.38)
        self.pad_to(A("zero knowledge instead") - 0.4)
        self.play(ShowCreation(circuit), FadeIn(circ_h), run_time=0.8)
        stmt = tl("prove: I know a valid post-quantum signature", size=FS_LABEL)
        stmt.move_to(circuit.get_center() + UP * 0.02)
        self.pad_to(A("prove in circuit") - 0.2)
        self.play(FadeIn(stmt), run_time=0.7)
        capss = key_chip("CAPSS: cheap exactly there", color=CYAN, size=FS_SMALL)
        capss.move_to(circuit.get_bottom() + UP * 0.42)
        self.pad_to(A("schemes like caps|schemes like capss") - 0.2)
        self.play(FadeIn(capss, shift=UP * 0.15), run_time=0.7)

        # authorization folds into the transaction's PCD proof
        swap1_left = [pq_sig, rr, arr_pr, sub_dl, prx, circuit, circ_h, stmt, capss]
        RX = 4.5
        token = proof_token(0.24).move_to([RX - 1.2, 1.3, 0])
        token_l = tl("PCD proof", size=FS_LABEL, color=GOLD)
        token_l.next_to(token, RIGHT, buff=0.3)
        self.pad_to(A("authorization then") - 0.3)
        self.play(*[m.animate.shift(LEFT * SX) for m in swap1_left],
                  head1.animate.align_to([LX0, 0, 0], LEFT),
                  FadeIn(token, scale=0.8), FadeIn(token_l, shift=LEFT * 0.1),
                  run_time=1.0)
        fly = VGroup(circuit, circ_h, stmt, capss).copy()
        fly.clear_updaters()
        self.pad_to(A("folds into") - 0.1)
        self.play(fly.animate.scale(0.08).move_to(token.get_center()).set_opacity(0),
                  run_time=0.9)
        self.remove(fly)
        self.pad_to(A("pcd proof") - 0.1)
        self.play(Indicate(token, color=GOLD, scale_factor=1.3), run_time=0.6)

        # rk leaves the action description
        action = panel(3.2, 1.2, color=STAR, fill_opacity=0.04).move_to([RX, -0.2, 0])
        add_shimmer([action], amp=0.18, speed=1.25)
        action_l = tl("action description", size=FS_SMALL, color=MUT)
        action_l.next_to(action, UP, buff=0.14)
        rk_chip = tex_chip('"rk"', color=AMBER, size=FS_LABEL)
        cv_chip = tex_chip('"cv"', color=STAR, size=FS_LABEL)
        inner = VGroup(rk_chip, cv_chip).arrange(RIGHT, buff=0.4).move_to(action)
        self.pad_to(A("the randomized key", 2) - 0.4)
        self.play(ShowCreation(action), FadeIn(action_l), FadeIn(inner), run_time=0.7)
        self.pad_to(A("leaves the action") - 0.2)
        self.play(FadeOut(rk_chip, shift=RIGHT * 1.2),
                  cv_chip.animate.move_to(action.get_center()), run_time=0.9)

        # the note-to-action binding returns as an explicit statement constraint
        note = key_chip("note", color=GOLD, size=FS_LABEL).move_to([RX, -2.25, 0])
        p0, p1 = note.get_top() + UP * 0.06, action.get_bottom() + DOWN * 0.06
        alink = DashedLine(p0, p1, stroke_color=AMBER, stroke_width=SW_THIN)
        alpha_l = mtex("alpha", size=FS_BODY, color=AMBER)
        alpha_l.next_to(alink, RIGHT, buff=0.2)
        self.pad_to(A("note to action binding") - 0.3)
        self.play(FadeIn(note), ShowCreation(alink), FadeIn(alpha_l), run_time=0.8)
        solid = Line(p0, p1, stroke_color=GOLD, stroke_width=SW)
        constraint_l = tl("explicit constraint", size=FS_SMALL, color=GOLD)
        constraint_l.next_to(solid, RIGHT, buff=0.2)
        self.pad_to(A("explicit constraint") - 0.4)
        self.play(FadeOut(alink), ShowCreation(solid),
                  FadeOut(alpha_l, shift=UP * 0.15),
                  FadeIn(constraint_l, shift=UP * 0.15), run_time=0.9)

        # swap 2: the proof system — left column keeps a summary of swap 1
        swap1 = VGroup(*swap1_left, token, token_l, action, action_l, cv_chip, note,
                       solid, constraint_l)
        RX0 = 0.6
        summary1 = bullets([tl("prove a PQ signature in circuit"),
                            tl("it folds into the PCD proof"),
                            row([('$"rk"$', TXT), ("leaves the action", TXT)], buff=0.12)],
                           mark_color=GOLD, buff=0.5)
        summary1.move_to([0, -0.3, 0]).align_to([LX0, 0, 0], LEFT)
        head2 = at_y(tl("second swap: the proof system", size=FS_HEAD, color=CYAN,
                        bold=True), 2.3)
        head2.align_to([RX0, 0, 0], LEFT)
        divider = Line([0.15, 2.6, 0], [0.15, -2.6, 0], stroke_width=SW_THIN,
                       stroke_color=DIM)
        self.pad_to(A("second the proof system") - 0.2)
        clear_shimmer([circuit, action])
        self.play(FadeOut(swap1), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in summary1],
                              lag_ratio=0.2),
                  ShowCreation(divider), FadeIn(head2, shift=UP * 0.2), run_time=1.0)

        BW, BX = 4.0, RX0 + 2.0
        top_blk = panel(BW, 0.95, color=STAR, fill_opacity=0.05).move_to([BX, 1.05, 0])
        top_l = tl("recursive folding", size=FS_LABEL, color=STAR).move_to(top_blk)
        dl_blk = panel(BW, 0.95, color=AMBER, fill_opacity=0.05).move_to([BX, -0.2, 0])
        dl_l = tl("discrete-log commitments", size=FS_LABEL, color=AMBER)
        dl_l.move_to(dl_blk)
        add_shimmer([top_blk, dl_blk], amp=0.18, speed=1.2)
        self.pad_to(A("ragus|raghus|ragu's") - 0.2)
        self.play(LaggedStart(FadeIn(VGroup(top_blk, top_l), shift=UP * 0.2),
                              FadeIn(VGroup(dl_blk, dl_l), shift=UP * 0.2),
                              lag_ratio=0.3), run_time=1.0)
        lat_blk = panel(BW, 0.95, color=CYAN, fill_opacity=0.05)
        add_shimmer([lat_blk], amp=0.18, speed=1.2)
        lat_l = tl("lattice commitments", size=FS_LABEL, color=CYAN)
        lat = VGroup(lat_blk, lat_l)
        lat_l.move_to(lat_blk)
        lat.move_to([BX, -0.2, 0])
        self.pad_to(A("lattice based folding") - 0.5)
        clear_shimmer([dl_blk])
        self.play(LaggedStart(
            FadeOut(VGroup(dl_blk, dl_l), shift=DOWN * 0.7),
            FadeIn(lat, shift=LEFT * 3.0),
            lag_ratio=0.45), run_time=1.4)
        surv = status("survives", top_blk.get_y(), top_blk.get_right()[0] + 0.25)
        self.pad_to(A("recursive structure") - 0.2)
        self.play(FadeIn(surv, shift=LEFT * 0.15), run_time=0.7)
        chg = tl("the hardness assumption changes", size=FS_LABEL)
        chg.next_to(lat, DOWN, buff=0.42).align_to(lat, LEFT)
        self.pad_to(A("hardness assumption") - 0.2)
        self.play(FadeIn(chg, shift=UP * 0.1), run_time=0.7)
        research = key_chip("concrete constructions: active research", color=MUT,
                            size=FS_SMALL)
        research.next_to(chg, DOWN, buff=0.36).align_to(lat, LEFT)
        self.pad_to(A("active research") - 0.3)
        self.play(FadeIn(research, shift=UP * 0.1), run_time=0.7)

        # "the honest status: to be determined — by design, not blocked":
        # the lattice slot itself grows into the closing card
        box, tbd, tbd_sub = tbd_card()
        self.pad_to(A("to be determined") - 0.5)
        clear_shimmer([top_blk])
        self.play(FadeOut(VGroup(head1, summary1, divider, head2, top_blk, top_l,
                                 surv, chg, research), run_time=0.6),
                  Transform(lat_blk, box), FadeTransform(lat_l, tbd), run_time=1.1)
        self.pad_to(A("by design") - 0.2)
        self.play(FadeIn(tbd_sub, shift=UP * 0.12), run_time=0.6)
        self.pad_to(scene_T(SID))


# 8.2 cascade geometry: cause (right-aligned) -> effect (left-aligned)
CAUSE_X = -0.7
EFFECT_X = 0.55
CASCADE_Y = [2.25, 1.53, 0.81, 0.09, -0.63, -1.35, -2.07]
SKEL = 0.28     # skeleton opacity of not-yet-spoken arrows/links


class Scene82(TimedScene):
    """8.2 — Outro: the decision cascade."""

    def construct(self):
        SID = "8.2"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731

        # Reconstruct 8.1's final frame so the act reads as one continuous thought.
        h_title = title_at("two coordinated swaps")
        h_box, h_tbd, h_sub = tbd_card()
        add_shimmer([h_box], amp=0.18, speed=1.2)
        self.add(h_title, h_box, h_tbd, h_sub)

        title = title_at("the decision cascade")
        self.wait(0.6)
        clear_shimmer([h_box])
        self.play(FadeOut(VGroup(h_box, h_tbd, h_sub), shift=UP * 0.25),
                  LaggedStart(FadeOut(h_title, shift=UP * 0.3),
                              FadeIn(title, shift=UP * 0.3), lag_ratio=0.6),
                  run_time=1.0)

        specs = [
            ("the nullifier set can't be pruned", [("validation moves to the client", GOLD)]),
            ("clients can't sync alone", [("syncing gets delegated", CYAN)]),
            ("delegation would leak the spend", [("nullifiers evolve", GOLD)]),
            ("evolving nullifiers go stale", [("a nullifier pair", FLARE),
                                              ("+ a two-epoch window", FLARE)]),
            ("per-stamp history needs composing", [("one accumulator, union by ×", GOLD)]),
            ("its degree explodes", [("QR filters bucket each epoch", AMBER)]),
            ("none of it is affordable alone", [("evidence built once, shared", STAR)]),
        ]
        causes, effects, arrows = VGroup(), VGroup(), VGroup()
        for (c, eff), y in zip(specs, CASCADE_Y):
            cm = at_y(tl(c), y).align_to([CAUSE_X, 0, 0], RIGHT)
            em = row(eff, buff=0.18)
            at_y(em, y).align_to([EFFECT_X, 0, 0], LEFT)
            ar = tarrow([CAUSE_X + 0.15, y, 0], [EFFECT_X - 0.15, y, 0],
                        color=MUT, width=SW_THIN, buff=0)
            causes.add(cm)
            effects.add(em)
            arrows.add(ar)
        # each effect becomes the next cause: a thin connector between rows
        links = VGroup(*[
            Line([EFFECT_X + 0.2, CASCADE_Y[i] - 0.24, 0],
                 [CAUSE_X - 0.2, CASCADE_Y[i + 1] + 0.24, 0],
                 stroke_width=SW_THIN, stroke_color=DIM)
            for i in range(6)])
        if effects[4].get_right()[0] > SAFE_X:
            effects[4].scale((SAFE_X - EFFECT_X) / effects[4].get_width(),
                             about_edge=LEFT)

        # "run the whole design backward ... one breath": the cascade's skeleton
        # (every arrow and hand-off) draws first, faint; each spoken step lights it
        for a in arrows:
            a[0].set_stroke(opacity=SKEL)
            a[1].set_fill(opacity=SKEL)
        links.set_stroke(opacity=SKEL)
        skel = []
        for i in range(7):
            skel.append(ShowCreation(arrows[i][0]))
            skel.append(FadeIn(arrows[i][1]))
            if i < 6:
                skel.append(ShowCreation(links[i]))
        self.pad_to(A("compresses") - 0.6)
        self.play(LaggedStart(*skel, lag_ratio=0.12), run_time=2.0)

        def lit(i):
            return [arrows[i][0].animate.set_stroke(opacity=1.0),
                    arrows[i][1].animate.set_fill(opacity=1.0)]

        def reveal_cause(i, t, lead=0.3):
            self.pad_to(t - lead)
            anims = [FadeIn(causes[i], shift=RIGHT * 0.15)]
            if i > 0:
                anims.append(links[i - 1].animate.set_stroke(opacity=1.0))
            self.play(*anims, run_time=0.6)

        def reveal_effect(i, t, part=None, lead=0.25):
            self.pad_to(t - lead)
            mobs = effects[i] if part is None else effects[i][part]
            anims = [FadeIn(mobs, shift=RIGHT * 0.15)]
            if part in (None, 0):
                anims += lit(i)
            self.play(*anims, run_time=0.6)

        reveal_cause(0, A("the nullifier set"))
        reveal_effect(0, A("so validation"))
        reveal_cause(1, A("clients cant sink|clients cant sync|clients cant"))
        reveal_effect(1, A("so sinking|so syncing"))
        reveal_cause(2, A("delegation would"))
        reveal_effect(2, A("so nullifiers evolve"))
        reveal_cause(3, A("evolving nullifiers would"))
        reveal_effect(3, A("so actions carry"), part=0)
        reveal_effect(3, A("consensus keeps"), part=1, lead=0.1)
        reveal_cause(4, A("history needed") - 0.7)
        reveal_effect(4, A("so one accumulator"))
        reveal_cause(5, A("its degree"))
        reveal_effect(5, A("so quadratic"))
        reveal_cause(6, A("none of it"))
        reveal_effect(6, A("so the expensive"))
        self.pad_to(A("shared by everyone") - 0.2)
        self.play(Indicate(effects[6], color=GOLD, scale_factor=1.06), run_time=0.8)

        # "each decision is forced by the one before it" — a pulse down the chain
        path = []
        for i in range(7):
            path.append(arrows[i][0])
            if i < 6:
                path.append(links[i])
        self.pad_to(A("each decision") - 0.2)
        self.play(LaggedStart(*[
            ShowPassingFlash(m.copy().set_stroke(GOLD, 6, 1.0), time_width=0.7)
            for m in path], lag_ratio=0.25), run_time=2.4)

        # "one principle — the client proves, consensus checks"
        principle = row([("the client proves", GOLD, True), ("$->$", MUT),
                         ("consensus checks", CYAN, True)], size=FS_BODY + 4, buff=0.3)
        principle.set_x(0)
        at_y(principle, CAPTION_Y)
        proves, checks = principle[0], principle[2]
        self.pad_to(A("one principle") - 0.3)
        self.play(FadeIn(principle, shift=UP * 0.2), run_time=0.7)
        self.pad_to(A("client proves") - 0.1)
        self.play(Indicate(proves, color=GOLD, scale_factor=1.06), run_time=0.5)
        self.pad_to(A("consensus checks") - 0.05)
        self.play(Indicate(checks, color=CYAN, scale_factor=1.06), run_time=0.6)

        # end card: the cascade clears first, then the principle rises to the
        # title band (never sweeping through the rows), and the links land large
        cascade = VGroup(causes, effects, arrows, links)
        logo = ImageMobject(LOGO_PNG)
        logo.set_height(1.5)
        logo.move_to(UP * 1.6)
        p_top = principle.copy()
        at_y(p_top, TITLE_Y)
        self.pad_to(A("written down") - 0.6)
        self.play(FadeOut(cascade, shift=DOWN * 0.2, run_time=0.6),
                  FadeOut(title, shift=UP * 0.2, run_time=0.6),
                  FadeOut(principle, shift=DOWN * 0.2, run_time=0.6))
        self.play(FadeIn(logo, scale=1.08), run_time=1.0)
        breathe(logo)

        link1 = url_label("https://tachyon.z.cash", FS_HEAD + 6, GOLD)
        link1.move_to(DOWN * 0.15)
        self.pad_to(A("deep dive") - 0.3)
        self.play(FadeIn(link1, shift=UP * 0.15), run_time=0.7)
        link2 = url_label("https://github.com/tachyon-zcash/tachyon", FS_HEAD + 6, CYAN)
        link2.move_to(DOWN * 1.35)
        if link2.get_width() > 2 * SAFE_X:
            link2.set_width(2 * SAFE_X)
        self.pad_to(A("implementation") - 0.3)
        self.play(FadeIn(link2, shift=UP * 0.15), run_time=0.8)
        self.pad_to(A("right below") - 0.1)
        self.play(Indicate(VGroup(link1, link2), color=STAR, scale_factor=1.04),
                  run_time=0.7)
        thanks = at_y(tl("thanks for watching", size=FS_BODY, color=MUT), CAPTION_Y)
        thanks.set_x(0)
        self.pad_to(A("thanks for watching") - 0.2)
        self.play(FadeIn(thanks, shift=UP * 0.1), run_time=0.8)
        self.pad_to(scene_T(SID))

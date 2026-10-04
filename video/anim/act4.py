"""Act 4 — the anchor chain and the epoch accumulator. Anchored to anim/words.json.

Render:  manimgl act4.py Scene41 Scene42 -w
Layout:  title band (scene_title) / stage / caption band, per style.py.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manimlib import *
from style import *

# ---- 4.1 stage geometry: the chain spans the full stage width ---------------
CHAIN_Y = -0.35          # the anchor chain itself
BLOCK_Y = 1.85           # the blocks whose header carries the anchor
GATE_X = (-6.2, 2.6, 5.0)  # sentinels: sntl_i, sntl_(i+1), sntl_(i+2)
GATE_SUBS = ("i", "i+1", "i+2")  # spec: sntl_i is the FIRST anchor of epoch i
EPOCH_LBL_Y = -1.2       # "epoch i" labels under the chain
RULE_Y = -2.6            # the two hash rules (anchor tick, sentinel tick)

# ---- 4.2 docked chain (true size, legible) ----------------------------------
DOCK_Y = 2.35


class Act4Scene(TimedScene):
    def pad_to(self, t):
        if self.time > t + 0.15:
            print(f"LATE {type(self).__name__}: at {self.time:.2f}s, beat wanted {t:.2f}s")
        super().pad_to(t)


def tgacc_chip(size=26):
    return tex_chip('"tgacc"', color=GOLD, size=size, pad=0.13)


def tx_block(n_stamps, left_x, y=BLOCK_Y, w=None):
    """A block: STAR body, header strip carrying the anchor field, gold stamps.

    n_stamps=0 draws an empty block (an epoch with no transactions still has blocks;
    their headers carry the unchanged anchor)."""
    stamps = VGroup(*[tgacc_chip() for _ in range(n_stamps)])
    if n_stamps:
        stamps.arrange(RIGHT, buff=0.45)
        w = w or stamps.get_width() + 0.7
    else:
        stamps = VGroup(itex("no stamps", size=FS_SMALL, color=MUT))
    body = panel(w, 1.6, color=STAR, fill_opacity=0.03, stroke_opacity=0.75)
    body.move_to(np.array([left_x + w / 2, y, 0]))
    strip = Rectangle(width=w - 0.24, height=0.42)
    strip.set_fill(STAR, 0.07)
    strip.set_stroke(STAR, 1.6, 0.6)
    strip.move_to(body.get_top() + DOWN * 0.33)
    hdr = mtex('"anchor"', size=FS_SMALL, color=STAR).move_to(strip)
    stamps.move_to(body.get_center() + DOWN * 0.27)
    return VGroup(body, strip, hdr, stamps)


def anchor_bead(x, y=CHAIN_Y, r=0.11):
    return Dot(np.array([x, y, 0]), radius=r).set_fill(STAR, 0.95)


def sentinel_post(x, y, sub, size=0.46):
    post = RoundedRectangle(width=size, height=size, corner_radius=0.08)
    post.set_fill(AMBER, 0.2)
    post.set_stroke(AMBER, SW_THIN, 0.95)
    post.move_to(np.array([x, y, 0]))
    return post


def sentinel_gate(x, sub, y=CHAIN_Y):
    """Epoch-boundary post: dashed upright + amber post + sntl tag above."""
    dash = VGroup(
        DashedLine(np.array([x, y + 0.85, 0]), np.array([x, y + 0.3, 0]),
                   stroke_color=AMBER, stroke_width=SW_THIN),
        DashedLine(np.array([x, y - 0.3, 0]), np.array([x, y - 0.6, 0]),
                   stroke_color=AMBER, stroke_width=SW_THIN),
    )
    post = sentinel_post(x, y, sub)
    tag = mtex(f'"sntl"_({sub})', size=FS_SMALL, color=AMBER)
    tag.next_to(dash, UP, buff=0.1)
    return VGroup(dash, post, tag)


def continuation(x, y=CHAIN_Y):
    """A quiet open-ended chain marker."""
    return VGroup(*[
        Line(np.array([x + 0.24 * k, y, 0]), np.array([x + 0.24 * k + 0.13, y, 0]),
             stroke_width=SW, stroke_color=DIM, stroke_opacity=0.9 - 0.25 * k)
        for k in range(3)
    ])


def chain_summary():
    """Docked anchor chain: shared final state of 4.1 / opening state of 4.2."""
    xs = (-4.6, 1.4, 3.6)
    posts = VGroup(*[sentinel_post(x, DOCK_Y, s) for x, s in zip(xs, GATE_SUBS)])
    tags = VGroup(*[mtex(f'"sntl"_({s})', size=FS_SMALL, color=AMBER)
                    .next_to(p, DOWN, buff=0.12) for p, s in zip(posts, GATE_SUBS)])
    bxs = np.linspace(-3.6, 0.4, 5)
    bs = VGroup(*[anchor_bead(x, DOCK_Y, 0.1) for x in bxs])
    ls = VGroup(chain_link(posts[0], bs[0]),
                *[chain_link(bs[k], bs[k + 1]) for k in range(len(bs) - 1)],
                chain_link(bs[-1], posts[1]), chain_link(posts[1], posts[2]))
    for l in ls:
        l.set_stroke(DIM, SW_THIN, 0.9)
    ep = mtex('"epoch" thin i', size=FS_SMALL, color=MUT)
    ep.move_to(np.array([(xs[0] + xs[1]) / 2, DOCK_Y + 0.36, 0]))  # above: 4.2 drops fall from the beads below
    tail = continuation(xs[2] + 0.4, DOCK_Y)
    return VGroup(ls, bs, posts, tags, ep, tail)


def vignette(color=FLARE, n=9, step=0.075, width=14):
    """Soft edge glow: nested frame-sized strokes whose opacity falls off inward.
    Each band keeps its weight in .vig_w; animate with vignette_to(v, level)."""
    v = VGroup()
    for k in range(n):
        r = Rectangle(width=FRAME_WIDTH - 2 * k * step, height=FRAME_HEIGHT - 2 * k * step)
        r.set_fill(opacity=0).set_stroke(color, width, 0.0)
        r.vig_w = (1 - k / n) ** 2
        v.add(r)
    return v


def vignette_to(v, level):
    return [r.animate.set_stroke(opacity=level * r.vig_w) for r in v]


def fix_vinculum(m, color):
    """typst draws a radical's bar as a zero-height stroked path, which our fill-only
    SVG import renders as a hairline. Replace such paths with filled bars."""
    out = VGroup()
    for sm in m.submobjects:
        if sm.get_height() < 1e-3 and sm.get_width() > 0.05:
            t = 0.055 * m.font_pt / 150   # matches the radical stroke weight
            bar = Rectangle(width=sm.get_width(), height=t)
            bar.set_fill(color, 1.0).set_stroke(width=0)
            bar.move_to(sm.get_center() + DOWN * t / 2)
            out.add(bar)
        else:
            out.add(sm)
    out.font_pt, out.base_h, out.lint_text = m.font_pt, max(out.get_height(), 1e-6), m.lint_text
    return out


def gear(r=0.5, color=FLARE):
    ring = Circle(radius=r).set_stroke(color, SW, 0.95).set_fill(opacity=0)
    teeth = VGroup(*[
        Line(ring.get_center() + r * np.array([math.cos(a), math.sin(a), 0]),
             ring.get_center() + 1.3 * r * np.array([math.cos(a), math.sin(a), 0]),
             stroke_width=SW, stroke_color=color)
        for a in np.arange(0, 2 * math.pi, math.pi / 4)
    ])
    hub = Dot(ring.get_center(), radius=0.08).set_fill(color, 1.0)
    return VGroup(ring, teeth, hub)


def stamp_acc(k, w=0.98, h=0.64):
    """A committed tachygram-accumulator polynomial from one accepted stamp."""
    box = RoundedRectangle(width=w, height=h, corner_radius=0.08)
    box.set_fill(STAR, 0.06)
    box.set_stroke(STAR, SW_THIN, 0.75)
    tex = mtex(f'f_{k}', size=FS_MIN + 2, color=STAR).move_to(box)
    return VGroup(box, tex)


class Scene41(Act4Scene):
    """4.1 — Anchors per stamp, sentinels per epoch."""

    def construct(self):
        A = lambda p, o=1: anchor("4.1", p, o)
        AA = lambda ps, o=1: anchor_any("4.1", ps, o)
        stage = VGroup()

        # "we keep saying authenticated history"
        hist = key_chip("“authenticated history”", color=STAR, size=FS_HEAD)
        hist.move_to(UP * 0.4)
        self.pad_to(A("authenticated history") - 0.5)
        self.play(FadeIn(hist, scale=1.1), run_time=0.8)

        # "time to actually build it" — two blocks with stamps inside
        b0 = tx_block(2, -5.75)
        b1 = tx_block(3, b0[0].get_right()[0] + 0.6)
        blk_link = chain_link(b0[0], b1[0])
        blk_link.set_stroke(DIM, SW, 0.9)
        self.pad_to(A("actually build it") - 0.4)
        self.play(FadeOut(hist), ShowCreation(b0[0]), ShowCreation(b1[0]),
                  FadeIn(b0[1]), FadeIn(b0[2]), FadeIn(b1[1]), FadeIn(b1[2]),
                  run_time=1.0)
        self.play(LaggedStart(*[FadeIn(m, scale=1.15) for m in (*b0[3], *b1[3])],
                              lag_ratio=0.12),
                  ShowCreation(blk_link), run_time=0.9)
        chips = VGroup(*[s[0] for s in (*b0[3], *b1[3])])
        add_shimmer(chips, amp=0.2, speed=1.3)
        stage.add(b0, b1, blk_link)

        # "the object is called the anchor chain"
        title = scene_title("the anchor chain", color=GOLD)
        self.pad_to(A("anchor chain") - 0.3)
        self.play(Write(title, run_time=1.0))

        # "a running hash carried in every block header" — genesis bead + epoch label
        genesis = anchor_bead(GATE_X[0])
        ep_i = mtex('"epoch" thin i', size=FS_LABEL, color=MUT)
        ep_i.move_to(np.array([(GATE_X[0] + GATE_X[1]) / 2, EPOCH_LBL_Y, 0]))
        self.pad_to(A("block header") - 0.8)
        self.play(FadeIn(genesis, scale=1.5), FadeIn(ep_i),
                  b0[1].animate.set_stroke(STAR, 2.4, 1.0),
                  b1[1].animate.set_stroke(STAR, 2.4, 1.0), run_time=1.0)
        stage.add(genesis, ep_i)

        # "each accepted stamp ticks it forward" — one bead directly below each stamp
        beads, drops, links = VGroup(), VGroup(), VGroup()

        def tick(stamp, prev):
            nb = anchor_bead(stamp.get_center()[0])
            drop = DashedLine(stamp.get_bottom() + DOWN * 0.06, nb.get_top() + UP * 0.04,
                              stroke_color=DIM, stroke_width=SW_THIN)
            # the genesis bead becomes sntl_i's post later: start the link at the
            # post's edge so it never pierces the (translucent) post
            edge = sentinel_post(GATE_X[0], CHAIN_Y, "") if prev is genesis else prev
            lk = chain_link(edge, nb)
            lk.set_stroke(DIM, SW, 0.9)
            beads.add(nb)
            drops.add(drop)
            links.add(lk)
            return AnimationGroup(TransformFromCopy(stamp, nb), ShowCreation(lk),
                                  ShowCreation(drop))

        self.pad_to(A("ticks it forward") - 0.5)
        self.play(tick(b0[3][0], genesis), run_time=0.75)
        self.play(tick(b0[3][1], beads[-1]), run_time=0.75)
        stage.add(beads, drops, links)

        # "the new anchor is a hash of ..." — the update rule
        rule = mtex('"anchor" <- H("anchor"_"old" parallel i parallel "tgacc")',
                    size=FS_BODY, color=STAR)
        rule.move_to(np.array([0, RULE_Y, 0]))
        self.pad_to(A("previous anchor") - 1.2)
        self.play(Write(rule, run_time=1.1))
        self.play(Indicate(beads[-2], color=STAR, scale_factor=1.6), run_time=0.6)
        self.pad_to(A("epic number") - 0.2)
        self.play(Indicate(ep_i, color=GOLD, scale_factor=1.25), run_time=0.6)
        self.pad_to(A("gram accumulator") - 0.3)
        self.play(Indicate(b0[3][1], color=GOLD, scale_factor=1.2), run_time=0.6)
        self.pad_to(A("whole update") - 0.3)
        self.play(Indicate(rule, color=GOLD, scale_factor=1.06), run_time=0.8)

        # "not per block — per stamp": b1's three stamps tick
        self.pad_to(A("granularity") - 0.3)
        for s in b1[3]:
            self.play(tick(s, beads[-1]), run_time=0.55)
        add_shimmer(beads, amp=0.08, speed=1.5)
        per_stamp = VGroup(*beads[-3:])
        br = bracket(per_stamp, color=GOLD, buff=0.22, below=True)
        per_cap = rich([("the chain ticks once", TXT), ("per stamp", GOLD),
                        ("— not once per block", TXT)])
        per_cap.move_to(UP * CAPTION_Y)
        self.pad_to(A("not per block") - 0.3)
        self.play(GrowFromCenter(br), FadeIn(per_cap, shift=UP * 0.15), run_time=0.8)

        # "in a block of ordinary transactions"
        self.pad_to(A("ordinary transactions") - 0.4)
        self.play(Indicate(b1, color=GOLD, scale_factor=1.04), run_time=0.8)

        # "the chain ticks once per transaction"
        self.pad_to(A("once per transaction") - 0.5)
        self.play(LaggedStart(*[Indicate(b, color=GOLD, scale_factor=1.7)
                                for b in per_stamp], lag_ratio=0.35), run_time=1.1)

        # "exactly one special tick ... the sentinel"
        self.pad_to(A("special tick") - 1.1)
        self.play(FadeOut(br), FadeOut(per_cap),
                  rule.animate.scale(0.88).move_to(np.array([-3.35, RULE_Y, 0])),
                  run_time=0.8)
        gate1 = sentinel_gate(GATE_X[1], GATE_SUBS[1])
        glk1 = chain_link(beads[-1], gate1[1])
        glk1.set_stroke(DIM, SW, 0.9)
        links.add(glk1)
        self.play(ShowCreation(glk1), FadeIn(gate1, scale=1.1), run_time=0.9)
        stage.add(gate1)

        # "a domain-separated hash called the sentinel"
        s_rule = mtex('"sntl"_(i+1) = H^"epoch" ("anchor"_(i, "end") parallel i+1)',
                      size=FS_BODY, color=AMBER)
        s_rule.scale(0.88).move_to(np.array([3.35, RULE_Y, 0]))
        self.pad_to(A("called the sentinel") - 0.8)
        self.play(Write(s_rule, run_time=0.8))

        # "the ordering machinery I promised"
        promised = caption("the ordering machinery, as promised", color=AMBER)
        self.pad_to(A("ordering machinery") - 0.3)
        self.play(FadeIn(promised, shift=UP * 0.15),
                  Indicate(gate1[1], color=AMBER, scale_factor=1.3), run_time=0.9)
        self.pad_to(A("end posts") - 2.3)
        self.play(FadeOut(promised), run_time=0.6)

        # "two authenticated endposts" — the first anchor of epoch i IS sntl_i
        gate0 = sentinel_gate(GATE_X[0], GATE_SUBS[0])
        span_y = EPOCH_LBL_Y - 0.4
        ep_br = bracket(VGroup(gate0[1], gate1[1]), color=AMBER, below=True,
                        buff=gate0[1].get_bottom()[1] - span_y)
        ep_tag = label("each epoch sits between two sentinels", size=FS_SMALL, color=AMBER)
        ep_tag.next_to(ep_br, DOWN, buff=0.12)
        self.pad_to(A("end posts") - 0.5)
        self.play(ReplacementTransform(genesis, gate0), GrowFromCenter(ep_br),
                  FadeIn(ep_tag), run_time=1.0)
        stage.remove(genesis)
        stage.add(gate0)

        # "even an epoch with no transactions at all"
        gate2 = sentinel_gate(GATE_X[2], GATE_SUBS[2])
        # the empty epoch still has blocks; their headers just carry sntl_(i+1)
        bw = 1.7
        b2 = tx_block(0, (GATE_X[1] + GATE_X[2]) / 2 - bw / 2, w=bw)
        blk_link2 = chain_link(b1[0], b2[0])
        blk_link2.set_stroke(DIM, SW, 0.9)
        glk2 = chain_link(gate1[1], gate2[1])
        glk2.set_stroke(DIM, SW, 0.9)
        links.add(glk2)
        empty = mtex('"epoch" thin i+1 thin ("empty")', size=FS_SMALL, color=MUT)
        empty.move_to(np.array([(GATE_X[1] + GATE_X[2]) / 2, EPOCH_LBL_Y, 0]))
        tail = Line(gate2[1].get_right() + RIGHT * 0.04,
                    np.array([5.75, CHAIN_Y, 0]), stroke_width=SW,
                    stroke_color=DIM, stroke_opacity=0.9)
        onward = continuation(5.85)
        self.pad_to(A("no transactions at all") - 0.6)
        self.play(ShowCreation(glk2), FadeIn(gate2, scale=1.1), FadeIn(empty),
                  ShowCreation(tail), FadeIn(onward), ShowCreation(blk_link2),
                  FadeIn(b2, shift=DOWN * 0.15), run_time=1.0)
        stage.add(gate2, empty, tail, onward, b2, blk_link2)

        # "any anchor pins down which epoch it belongs to"
        self.pad_to(A("pins down") - 0.5)
        self.play(beads[3].animate.set_fill(GOLD), Indicate(ep_i, color=GOLD, scale_factor=1.25),
                  run_time=0.8)
        self.play(beads[3].animate.set_fill(STAR), run_time=0.4)

        # "a name for a moment in shielded history ... hang evidence on"
        moment = rich([("an anchor is", TXT), ("a name for a moment", STAR),
                       ("in shielded history", TXT)])
        moment.move_to(UP * CAPTION_Y)
        self.pad_to(A("name for a moment") - 0.4)
        self.play(FadeIn(moment, shift=UP * 0.15), run_time=0.7)
        hang = Line(beads[0].get_bottom(), beads[0].get_bottom() + DOWN * 0.45,
                    stroke_width=SW_THIN, stroke_color=GOLD)
        token = proof_token(0.11).next_to(hang, DOWN, buff=0.04)
        self.pad_to(A("hang evidence") - 0.4)
        self.play(ShowCreation(hang), FadeIn(token, scale=1.3), run_time=0.8)

        # "why per stamp rather than per block?" — compare who does the work
        self.pad_to(A("who does the work") - 0.6)
        question = scene_title("why per stamp, not per block?", color=STAR)
        # shimmer updaters would hold the chips' fill against the fade: stop them first
        clear_shimmer(chips)
        clear_shimmer(beads)
        self.play(FadeOut(VGroup(moment, hang, token, s_rule, rule, ep_br, ep_tag)),
                  FadeOut(stage, shift=UP * 0.3), FadeOut(title, shift=UP * 0.3),
                  run_time=1.0)

        p_l = panel(6.2, 4.7, color=GOLD, fill_opacity=0.04)
        p_l.move_to(np.array([-3.3, -0.25, 0]))
        p_r = panel(6.2, 4.7, color=FLARE, fill_opacity=0.03, stroke_opacity=0.5)
        p_r.move_to(np.array([3.3, -0.25, 0]))
        h_l = pill("per stamp", color=GOLD).move_to(p_l.get_top() + DOWN * 0.5)
        h_r = pill("per block", color=FLARE).move_to(p_r.get_top() + DOWN * 0.5)
        self.play(FadeIn(question, shift=UP * 0.2),
                  ShowCreation(p_l), ShowCreation(p_r), FadeIn(h_l), FadeIn(h_r),
                  run_time=0.8)

        # left: the stamp already proved its accumulator in circuit
        row_y = p_l.get_center()[1] + 0.25
        stamp = tgacc_chip(FS_LABEL).move_to(np.array([p_l.get_left()[0] + 1.15, row_y, 0]))
        card = proof_card(0.85).next_to(stamp, DOWN, buff=0.3)
        cap_l = itex("proven in circuit", size=FS_SMALL, color=MUT)
        cap_l.next_to(card, DOWN, buff=0.15)
        self.pad_to(AA(["proved in circuit", "in circuit"]) - 0.5)
        self.play(FadeIn(stamp, scale=1.1), FadeIn(card, scale=1.1), FadeIn(cap_l),
                  run_time=0.9)

        # "the validator's entire job is one hash"
        sp = sponge_icon(1.3, 0.8).scale(1.3)
        sp.move_to(np.array([p_l.get_center()[0] + 0.25, row_y - 0.15, 0]))
        nb = anchor_bead(p_l.get_right()[0] - 0.75, row_y, 0.14)
        a1 = tarrow(stamp, sp[0], color=GOLD, width=SW)
        a2 = tarrow(sp[0], nb, color=GOLD, width=SW)
        one_hash = label("validator: one hash", size=FS_BODY, color=GOLD)
        one_hash.move_to(p_l.get_bottom() + UP * 0.5)
        self.pad_to(A("one hash") - 1.0)
        self.play(FadeIn(sp, scale=1.05), ShowCreation(a1), run_time=0.6)
        self.play(ShowCreation(a2), FadeIn(nb, scale=1.4), FadeIn(one_hash),
                  run_time=0.7)

        # right: the per-block alternative — rebuild, interpolate, commit
        self.pad_to(A("per block instead") - 0.3)
        tgs = VGroup(*[bead(MUT, 0.07) for _ in range(16)])
        tgs.arrange_in_grid(4, 4, buff=0.22)
        tgs.move_to(np.array([p_r.get_left()[0] + 1.0, row_y - 0.1, 0]))
        self.play(p_r.animate.set_stroke(FLARE, 2.4, 0.85),
                  LaggedStart(*[FadeIn(m, scale=1.4) for m in tgs], lag_ratio=0.05),
                  run_time=0.9)
        steps = bullets(["re-accumulate", "interpolate", "commit"],
                        size=FS_LABEL, color=FLARE, mark_color=FLARE, buff=0.28)
        steps.next_to(tgs, RIGHT, buff=0.6).align_to(tgs, UP).shift(UP * 0.15)
        self.pad_to(AA(["reaccumulate every", "accumulate every"]) - 0.3)
        self.play(FadeIn(steps[0], shift=RIGHT * 0.2), run_time=0.6)
        self.pad_to(A("interpolate") - 0.2)
        self.play(FadeIn(steps[1], shift=RIGHT * 0.2), run_time=0.5)
        self.pad_to(A("commit") - 0.2)
        self.play(FadeIn(steps[2], shift=RIGHT * 0.2), run_time=0.5)

        # "multi-scalar multiplication on the critical path"
        g = gear(0.42)
        g.move_to(np.array([p_r.get_right()[0] - 0.85, steps.get_bottom()[1] - 0.75, 0]))
        msm = label("MSM", size=FS_BODY, color=FLARE).next_to(g, LEFT, buff=0.35)
        g.add_updater(lambda m, dt: m.rotate(1.1 * dt))
        self.pad_to(A("critical path") - 0.6)
        self.play(FadeIn(g, scale=1.2), FadeIn(msm), run_time=0.8)
        cap_r = label("every validator, every block", size=FS_BODY, color=FLARE)
        cap_r.move_to(p_r.get_bottom() + UP * 0.5)
        self.pad_to(A("every validator on every block") - 0.4)
        self.play(FadeIn(cap_r), run_time=0.7)

        # "the prover already volunteered; let them"
        volunteered = caption("the prover already volunteered — let them", color=GOLD)
        ck = checkmark(0.42, GOLD).move_to(h_l.get_right() + RIGHT * 0.55)
        xc = h_r.get_right() + RIGHT * 0.55
        xr = VGroup(Line(xc + 0.2 * UL, xc + 0.2 * DR, stroke_width=SW_BOLD, stroke_color=FLARE),
                    Line(xc + 0.2 * UR, xc + 0.2 * DL, stroke_width=SW_BOLD, stroke_color=FLARE))
        self.pad_to(A("volunteered") - 0.8)
        self.play(FadeIn(volunteered, shift=UP * 0.15), ShowCreation(ck), run_time=0.7)
        self.play(ShowCreation(xr), VGroup(p_r, h_r, tgs, steps, msm, cap_r, g).animate.fade(0.5),
                  run_time=0.8)

        # "every stamp names its place in history" — the chain comes back
        # (clear the comparison first, then rebuild the chain: no double exposure)
        self.pad_to(A("names its place") - 1.5)
        title2 = scene_title("the anchor chain", color=GOLD)
        self.play(FadeOut(VGroup(p_l, h_l, stamp, card, cap_l, sp, nb, a1, a2,
                                 one_hash, p_r, h_r, tgs, steps, g, msm, cap_r,
                                 ck, xr, volunteered, question), shift=UP * 0.2),
                  run_time=0.7)
        g.clear_updaters()
        self.play(FadeIn(stage, shift=DOWN * 0.3), FadeIn(title2, shift=DOWN * 0.2),
                  run_time=0.8)
        add_shimmer(chips, amp=0.2, speed=1.3)
        add_shimmer(beads, amp=0.08, speed=1.5)

        # "every epoch has sealed endpoints"
        self.pad_to(A("sealed end points") - 0.4)
        self.play(*[Indicate(gt[1], color=AMBER, scale_factor=1.35)
                    for gt in (gate0, gate1, gate2)], run_time=0.9)

        # "between this sentinel and that one — these, and only these"
        self.pad_to(A("between this sentinel") - 0.4)
        span = bracket(VGroup(gate0[1], gate1[1]), color=STAR, below=True,
                       buff=gate0[1].get_bottom()[1] - span_y)
        span_tag = rich([("between two sentinels:", TXT),
                         ("exactly these accumulators", STAR)], size=FS_LABEL)
        span_tag.next_to(span, DOWN, buff=0.18)
        self.play(GrowFromCenter(span), FadeIn(span_tag), run_time=1.0)
        self.pad_to(A("only these happened") - 0.3)
        self.play(LaggedStart(*[Indicate(b, color=STAR, scale_factor=1.7)
                                for b in beads], lag_ratio=0.12), run_time=1.1)

        # hand-off: the chain itself slides up and becomes 4.2's docked summary
        ls, bs, posts, tags, ep, stail = chain_summary()
        gates = (gate0, gate1, gate2)
        clear_shimmer(beads)
        clear_shimmer(chips)
        # blocks and labels leave first, so the rising chain never crosses them
        self.play(FadeOut(VGroup(b0, b1, b2, blk_link, blk_link2, drops, empty, tail,
                                 title2, span, span_tag, *[gt[0] for gt in gates])),
                  run_time=0.5)
        self.play(ReplacementTransform(links, ls), ReplacementTransform(beads, bs),
                  ReplacementTransform(VGroup(*[gt[1] for gt in gates]), posts),
                  ReplacementTransform(VGroup(*[gt[2] for gt in gates]), tags),
                  ReplacementTransform(ep_i, ep), ReplacementTransform(onward, stail),
                  run_time=0.9)
        self.pad_to(scene_T("4.1"))


class Scene42(Act4Scene):
    """4.2 — The epoch accumulator, and the wall."""

    def construct(self):
        A = lambda p, o=1: anchor("4.2", p, o)
        AA = lambda ps, o=1: anchor_any("4.2", ps, o)

        # opening state: the anchor chain from 4.1, docked at the top
        mini = chain_summary()
        mbeads = mini[1]
        self.add(mini)

        # "now, use it"
        self.pad_to(A("use it") - 0.4)
        self.play(Indicate(mini, color=STAR, scale_factor=1.03), run_time=0.7)

        # "a note from twenty epochs ago" — the epoch strip and the debt
        row_y = 0.75
        wallet = panel(1.5, 1.05, color=GOLD, fill_opacity=0.06)
        wallet.move_to(np.array([-5.85, row_y, 0]))
        note = tex_chip('"note"', color=GOLD, size=FS_LABEL, pad=0.12).move_to(wallet)
        w_tag = label("wallet", size=FS_SMALL, color=GOLD).next_to(wallet, DOWN, buff=0.12)
        cell_texts = ["i-20", "i-19", "i-18", "i-10", "i-2", "i-1", "i"]
        cells = VGroup()
        for t in cell_texts:
            c = RoundedRectangle(width=1.08, height=0.7, corner_radius=0.08)
            c.set_fill(STAR, 0.05)
            c.set_stroke(STAR, SW_THIN, 0.7)
            lab = mtex(t, size=FS_SMALL, color=TXT).move_to(c)
            cells.add(VGroup(c, lab))
        cells.arrange(RIGHT, buff=0.26).move_to(np.array([0.15, row_y, 0]))
        now = label("now", size=FS_SMALL, color=MUT).next_to(cells[-1], RIGHT, buff=0.25)
        self.pad_to(AA(["20 epics ago", "twenty epochs ago"]) - 0.6)
        self.play(ShowCreation(wallet), FadeIn(w_tag), FadeIn(note, scale=1.2),
                  LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.07),
                  FadeIn(now), run_time=1.2)
        add_shimmer(VGroup(*[c[0] for c in cells]), amp=0.18, speed=1.2)

        # "you owe exclusion proofs for every epoch in between"
        # an owed proof = an empty flare ring (the proof_token's ring, not yet earned)
        owes = VGroup(*[Circle(radius=0.15).set_stroke(FLARE, SW_THIN, 0.95)
                        .set_fill(FLARE, 0.08).next_to(c, DOWN, buff=0.16) for c in cells])
        owe_cap = rich([("owed: one exclusion proof per epoch,", TXT),
                        ('$"nf"_e in.not "epoch" e$', FLARE)])
        owe_cap.move_to(UP * CAPTION_Y)
        self.pad_to(A("exclusion proofs") - 0.4)
        self.play(LaggedStart(*[TransformFromCopy(note[0], o) for o in owes],
                              lag_ratio=0.1),
                  FadeIn(owe_cap, shift=UP * 0.15), run_time=1.3)

        # "one non-membership test per stamp" — one epoch, exploded
        zoom = panel(9.4, 2.5, color=STAR, fill_opacity=0.03, stroke_opacity=0.55)
        zoom.move_to(np.array([0.2, -1.55, 0]))
        stamps = VGroup(*[stamp_acc(k + 1) for k in range(18)])
        stamps.arrange_in_grid(3, 6, h_buff=0.2, v_buff=0.14)
        stamps.move_to(zoom.get_center() + RIGHT * 1.0)
        nf = bead(FLARE, 0.13).move_to(np.array([zoom.get_left()[0] + 0.85, zoom.get_center()[1], 0]))
        nf_tag = mtex('"nf"_i', size=FS_LABEL, color=FLARE).next_to(nf, UP, buff=0.14)
        self.pad_to(A("test per stamp") - 1.0)
        self.play(TransformFromCopy(cells[-1][0], zoom), FadeIn(nf, scale=1.4),
                  FadeIn(nf_tag), FadeOut(owe_cap), run_time=0.9)
        probes = VGroup(*[bead(FLARE, 0.06).move_to(s.get_corner(UR) + DL * 0.12)
                          for s in stamps])
        per_test = caption("one non-membership test per stamp", color=FLARE)
        self.play(LaggedStart(*[FadeIn(s) for s in stamps], lag_ratio=0.03),
                  LaggedStart(*[TransformFromCopy(nf, p) for p in probes], lag_ratio=0.03),
                  FadeIn(per_test), run_time=1.5)
        add_shimmer(VGroup(*[s[0] for s in stamps]), amp=0.2, speed=1.4)

        # "dead end"
        self.pad_to(A("dead end") - 0.3)
        dead_tag = caption("dead end", color=FLARE, size=FS_HEAD)
        self.play(zoom.animate.set_stroke(FLARE, SW, 1.0).set_fill(FLARE, 0.08),
                  FadeTransform(per_test, dead_tag), run_time=0.8)

        # "union is multiplication" — the stamp polynomials converge
        union = pill("union = multiplication", color=GOLD)
        union.move_to(np.array([0.2, 0.35, 0]))
        self.pad_to(A("union is multiplication") - 0.5)
        self.play(zoom.animate.set_stroke(STAR, 2.4, 0.55).set_fill(STAR, 0.03),
                  FadeOut(dead_tag), FadeOut(probes),
                  FadeOut(VGroup(wallet, w_tag, note, cells, now, owes)),
                  FadeIn(union, scale=1.1), run_time=0.9)

        # "multiply all ... together": the product is one accumulator e_i(X)
        env = envelope(2.8, 1.7, color=STAR, tex_label="e_i (X)")
        env.move_to(np.array([0.2, -1.25, 0]))
        prod = mtex('e_i (X) = product_(j in "epoch" i) f_j (X)', size=FS_BODY, color=STAR)
        prod.move_to(UP * CAPTION_Y)
        self.pad_to(A("multiply all") - 0.3)
        clear_shimmer(VGroup(*[s[0] for s in stamps]))
        # the envelope condenses out of the converging stamps (second half of the move)
        late_in = lambda t: smooth(max(0.0, (t - 0.45) / 0.55))
        self.play(LaggedStart(*[s.animate.move_to(env.get_center()).scale(0.3).fade(0.92)
                                for s in stamps], lag_ratio=0.04),
                  FadeIn(env, scale=1.1, rate_func=late_in),
                  FadeIn(prod, shift=UP * 0.15), run_time=1.4)
        self.play(FadeOut(stamps, scale=0.5), FadeOut(zoom), run_time=0.6)
        # "the product is itself an accumulator — over every tachygram the epoch produced"
        self.pad_to(A("itself an accumulator") - 0.3)
        self.play(Indicate(env, color=STAR, scale_factor=1.06), run_time=0.8)
        self.pad_to(A("the epic produced") - 0.6)
        self.play(Indicate(prod[6:], color=GOLD, scale_factor=1.1), run_time=0.8)
        title = scene_title("the epoch accumulator", color=STAR)
        self.pad_to(AA(["epic accumulator", "epoch accumulator"]) - 0.5)
        self.play(Write(title, run_time=1.0))

        # "one test per epoch" — a single query arrow hits the envelope
        self.pad_to(A("hundreds of thousands") - 1.2)
        q = tarrow(nf, env[0], color=GOLD, width=SW_BOLD, buff=0.15)
        hit = mtex('e_i ("nf"_i) != 0', size=FS_LABEL, color=GOLD)
        hit.next_to(q, DOWN, buff=0.18)
        self.play(ShowCreation(q), FadeOut(union), run_time=0.6)
        self.play(FadeIn(hit, scale=1.15), Indicate(env, color=GOLD, scale_factor=1.05),
                  run_time=0.7)

        # "prove it correct against the anchor chain with cheap oracle queries"
        self.pad_to(A("cheap oracle queries") - 1.6)
        drops = VGroup(*[DashedLine(mbeads[k].get_bottom() + DOWN * 0.05,
                                    env[0].get_top() + RIGHT * dx,
                                    stroke_color=CYAN, stroke_width=SW_THIN)
                         for k, dx in ((2, -0.6), (3, 0.0), (4, 0.6))])
        oss = pill("OSS builds it", color=CYAN)
        oss.next_to(env, RIGHT, buff=0.7).shift(UP * 0.45)
        at_r = mtex('e_i (r) = product_j f_j (r)', size=FS_LABEL, color=STAR)
        at_r.next_to(oss, DOWN, buff=0.3)
        self.play(LaggedStart(*[ShowCreation(d) for d in drops], lag_ratio=0.1),
                  Indicate(mbeads[2:], color=CYAN, scale_factor=1.4), run_time=1.0)
        self.play(FadeIn(oss, shift=LEFT * 0.12), FadeIn(at_r, scale=1.1), run_time=0.5)

        # "degree limited only by the commitment setup"
        self.pad_to(A("commitment setup") - 1.4)
        bar_x0 = -1.2
        circ_lim = Line(np.array([bar_x0, -2.8, 0]), np.array([bar_x0 + 1.1, -2.8, 0]),
                        stroke_width=9, stroke_color=DIM)
        circ_tag = label("step circuit", size=FS_SMALL, color=MUT)
        circ_tag.next_to(circ_lim, LEFT, buff=0.25).align_to(np.array([bar_x0 - 0.25, 0, 0]), RIGHT)
        deg_bar = Line(np.array([bar_x0, -3.35, 0]), np.array([bar_x0 + 0.3, -3.35, 0]),
                       stroke_width=9, stroke_color=CYAN)
        srs_tag = label("commitment setup", size=FS_SMALL, color=CYAN)
        srs_tag.next_to(deg_bar, LEFT, buff=0.25)
        srs_tag.align_to(circ_tag, RIGHT)
        self.play(FadeOut(prod), ShowCreation(circ_lim), FadeIn(circ_tag), run_time=0.6)
        self.play(ShowCreation(deg_bar), FadeIn(srs_tag), run_time=0.3)
        self.play(deg_bar.animate.put_start_and_end_on(
            np.array([bar_x0, -3.35, 0]), np.array([6.3, -3.35, 0])), run_time=0.9)

        # "build once, prove once, reuse for every note"
        self.pad_to(A("build once") - 0.3)
        notes = VGroup(*[tex_chip('"note"', color=GOLD, size=FS_SMALL, pad=0.11)
                         for _ in range(3)])
        notes.arrange(DOWN, buff=0.35).move_to(np.array([-5.4, env.get_center()[1], 0]))
        reuse = VGroup(*[tarrow(n, env[0], color=GOLD, width=SW_THIN, buff=0.12)
                         for n in notes])
        once = rich([("build once", GOLD), ("·", MUT), ("prove once", GOLD), ("·", MUT),
                     ("reuse for every note", GOLD)], buff=0.2)
        once.move_to(UP * CAPTION_Y)
        once = VGroup(once[0], VGroup(once[1], once[2]), VGroup(once[3], once[4]))
        self.play(FadeOut(VGroup(nf, nf_tag, q, hit, circ_lim, circ_tag, deg_bar, srs_tag)),
                  LaggedStart(*[FadeIn(n, scale=1.1) for n in notes], lag_ratio=0.15),
                  FadeIn(once[0], shift=UP * 0.15), run_time=0.9)
        self.pad_to(A("prove once") - 0.2)
        self.play(FadeIn(once[1], shift=UP * 0.15),
                  Indicate(VGroup(*drops), color=STAR, scale_factor=1.0), run_time=0.6)
        self.pad_to(A("reuse for every") - 0.3)
        self.play(FadeIn(once[2], shift=UP * 0.15),
                  LaggedStart(*[ShowCreation(r) for r in reuse], lag_ratio=0.15),
                  run_time=0.9)

        # "except — run the numbers"
        self.pad_to(A("run the numbers") - 1.0)
        self.play(FadeOut(VGroup(notes, reuse, once, drops, oss, at_r)),
                  env.animate.move_to(np.array([4.1, 0.75, 0])),
                  run_time=1.1)
        col_x = -2.6
        n1 = mtex('100 "tx/s"', size=FS_HEAD, color=STAR)
        n2 = mtex('times 4 "tachygrams per tx"', size=FS_HEAD, color=STAR)
        n3 = mtex('times "2 weeks"', size=FS_HEAD, color=STAR)
        nums = VGroup(n1, n2, n3).arrange(DOWN, buff=0.32, aligned_edge=RIGHT)
        nums.move_to(np.array([col_x, 0.4, 0]))
        self.pad_to(A("hundred transactions") - 0.3)
        self.play(FadeIn(n1, shift=UP * 0.15), run_time=0.6)
        self.pad_to(A("two and two out") - 0.3)
        self.play(FadeIn(n2, shift=UP * 0.15), run_time=0.6)
        self.pad_to(A("two week epoch") - 0.3)
        self.play(FadeIn(n3, shift=UP * 0.15), run_time=0.6)
        rule_line = Line(np.array([nums.get_left()[0], 0, 0]), np.array([nums.get_right()[0], 0, 0]),
                         stroke_width=SW_THIN, stroke_color=MUT)
        rule_line.next_to(nums, DOWN, buff=0.25)
        total = mtex('approx 4.8 times 10^8 "tachygrams"', size=52, color=AMBER)
        total.next_to(rule_line, DOWN, buff=0.3).align_to(nums, RIGHT)
        self.pad_to(A("480 million") - 0.4)
        self.play(ShowCreation(rule_line), FadeIn(total, scale=1.15), run_time=0.9)

        # "one polynomial, degree half a billion"
        deg = mtex('deg e_i approx 4.8 times 10^8', size=FS_BODY, color=AMBER)
        deg.next_to(env, DOWN, buff=0.3)
        self.pad_to(A("half a billion") - 0.4)
        self.play(FadeTransform(total.copy(), deg), run_time=0.9)

        # "a verifier that's linear in the degree" — numbers collapse to the total
        self.pad_to(A("linear in the degree") - 0.6)
        ox, oy = -5.9, -3.2
        ax_x = Line(np.array([ox, oy, 0]), np.array([ox + 4.2, oy, 0]),
                    stroke_width=SW_THIN, stroke_color=MUT)
        ax_y = Line(np.array([ox, oy, 0]), np.array([ox, oy + 2.4, 0]),
                    stroke_width=SW_THIN, stroke_color=MUT)
        x_lab = label("degree", size=FS_SMALL, color=MUT).next_to(ax_x, RIGHT, buff=0.15)
        y_lab = label("verifier time", size=FS_SMALL, color=FLARE)
        y_lab.next_to(ax_y, UP, buff=0.12).align_to(ax_y, LEFT)
        lin = Line(np.array([ox, oy, 0]), np.array([ox + 3.9, oy + 2.1, 0]),
                   stroke_width=SW_BOLD, stroke_color=FLARE)
        self.play(FadeOut(VGroup(n1, n2, n3, rule_line)),
                  total.animate.scale(0.8).move_to(np.array([-3.0, 0.95, 0])),
                  ShowCreation(ax_x), ShowCreation(ax_y), FadeIn(x_lab), FadeIn(y_lab),
                  run_time=0.8)
        self.play(ShowCreation(lin), run_time=0.7)

        # "north of sixteen minutes" — the stopwatch and the flare tint
        wc = np.array([1.2, -1.65, 0])
        watch = Circle(radius=0.95).set_stroke(STAR, SW, 0.95).set_fill(opacity=0).move_to(wc)
        crown = Rectangle(width=0.22, height=0.16).set_fill(STAR, 0.9).set_stroke(width=0)
        crown.next_to(watch, UP, buff=0.02)
        hand = Line(wc, wc + UP * 0.75, stroke_width=SW_BOLD, stroke_color=FLARE)
        wtime = mtex('> 16 "min"', size=72, color=FLARE)
        wtime.next_to(watch, RIGHT, buff=0.45)
        per_check = label("for one evaluation check", size=FS_SMALL, color=MUT)
        per_check.next_to(wtime, DOWN, buff=0.15).align_to(wtime, LEFT)
        tint = vignette()
        self.add(tint)
        self.pad_to(AA(["16 minutes", "sixteen minutes"]) - 0.8)
        self.play(ShowCreation(watch), FadeIn(crown), FadeIn(hand), run_time=0.5)
        self.play(Rotate(hand, -4 * PI, about_point=wc),
                  FadeIn(wtime, scale=1.1), FadeIn(per_check),
                  *vignette_to(tint, 0.22), run_time=1.3)

        # "per spend, per epoch crossed"
        mults = label("× every spend   × every epoch crossed", size=FS_BODY, color=FLARE)
        mults.move_to(np.array([3.6, CAPTION_Y + 0.05, 0]))
        self.pad_to(A("per spend per") - 0.2)
        self.play(FadeIn(mults, shift=UP * 0.15), run_time=0.8)

        # "the idea survives; the size doesn't"
        verdict = scene_title("the idea survives — the size doesn't", color=STAR)
        self.pad_to(A("idea survives") - 0.3)
        self.play(FadeTransform(title, verdict), *vignette_to(tint, 0.12),
                  run_time=0.8)

        # "the failure is informative" — clear the wall, keep the polynomial
        self.pad_to(A("failure is informative") - 0.5)
        self.play(FadeOut(VGroup(total, ax_x, ax_y, x_lab, y_lab, lin, watch, crown, hand,
                                 wtime, per_check, mults, deg)),
                  *vignette_to(tint, 0.0),
                  env.animate.move_to(np.array([0, -0.35, 0])),
                  run_time=1.2)

        # "nothing was wrong with testing against one polynomial" — the query still works
        nf3 = bead(FLARE, 0.13).move_to(np.array([-3.6, -0.35, 0]))
        nf3_tag = mtex('"nf"_i', size=FS_LABEL, color=FLARE).next_to(nf3, UP, buff=0.14)
        q3 = tarrow(nf3, env[0], color=GOLD, width=SW_BOLD, buff=0.15)
        self.pad_to(A("testing against") - 0.5)
        self.play(FadeIn(nf3, scale=1.4), FadeIn(nf3_tag), ShowCreation(q3), run_time=0.7)
        self.play(Indicate(env, color=GOLD, scale_factor=1.05), run_time=0.7)
        self.remove(tint)

        # "too big, because it covered everyone"
        crowd = VGroup(*[bead(MUT, 0.08) for _ in range(6 * 15)])
        crowd.arrange_in_grid(6, 15, buff=0.5)
        crowd.move_to(np.array([0, -0.35, 0]))
        ew, eh = env.get_width() * 1.45 / 2 + 0.3, env.get_height() * 1.45 / 2 + 0.3
        crowd = VGroup(*[d for d in crowd
                         if abs(d.get_x()) > ew or abs(d.get_y() + 0.35) > eh])
        everyone = caption("it covered everyone", color=MUT)
        self.pad_to(AA(["simply too big", "too big"]) - 0.4)
        self.play(FadeOut(VGroup(nf3, nf3_tag, q3)),
                  LaggedStart(*[FadeIn(m, scale=1.3) for m in crowd], lag_ratio=0.02),
                  run_time=0.9)
        self.add(env)
        self.pad_to(A("covered everyone") - 0.4)
        self.play(env.animate.scale(1.45), FadeIn(everyone, shift=UP * 0.15), run_time=0.9)

        # "carve the epoch into pieces"
        # the cuts are drawn ON the big envelope, then each slice becomes its own
        # (smaller) envelope: body->body and flap->flap morphs, labels cross-fade
        pieces = VGroup(*[envelope(2.0, 1.25, color=STAR, tex_label=f"e_(i,{k + 1})")
                          for k in range(5)])
        pieces.arrange(RIGHT, buff=0.42).move_to(np.array([0, -0.4, 0]))
        eb = env[0]
        cuts = VGroup(*[DashedLine(
            np.array([eb.get_left()[0] + eb.get_width() * k / 5, eb.get_top()[1] + 0.2, 0]),
            np.array([eb.get_left()[0] + eb.get_width() * k / 5, eb.get_bottom()[1] - 0.2, 0]),
            stroke_color=GOLD, stroke_width=SW_THIN) for k in range(1, 5)])
        self.pad_to(A("into pieces") - 0.7)
        self.play(FadeOut(crowd), FadeOut(everyone), run_time=0.4)
        self.play(LaggedStart(*[ShowCreation(c) for c in cuts], lag_ratio=0.15),
                  run_time=0.6)
        # swap the body for five identical-looking slices, then pull them apart:
        # each slice grows into its own envelope (flap + label fade in)
        sw_, sh_ = eb.get_width() / 5, eb.get_height()
        # same shape class as the envelope body, so the morph is a pure move+scale
        slices = VGroup(*[RoundedRectangle(width=sw_, height=sh_, corner_radius=0.04)
                          .set_fill(STAR, eb.get_fill_opacity())
                          .set_stroke(STAR, 2.4, 0.95)
                          .move_to(np.array([eb.get_left()[0] + sw_ * (k + 0.5), eb.get_y(), 0]))
                          for k in range(5)])
        self.remove(eb)
        self.add(slices, env[1], env[2], cuts)
        self.play(*[ReplacementTransform(sl, p[0]) for sl, p in zip(slices, pieces)],
                  FadeOut(VGroup(env[1], env[2], cuts)),
                  *[FadeIn(VGroup(p[1], p[2]),
                           rate_func=lambda t: smooth(max(0.0, (t - 0.75) / 0.25)))
                    for p in pieces],
                  run_time=1.0)
        self.remove(*[m for p in pieces for m in p])
        self.add(pieces)

        # "your nullifier only ever faces one small piece"
        nf2 = bead(FLARE, 0.14).move_to(np.array([pieces[3].get_center()[0] - 1.6, 1.25, 0]))
        nf2_tag = mtex('"nf"_i', size=FS_LABEL, color=FLARE).next_to(nf2, LEFT, buff=0.18)
        route = tarrow(nf2, pieces[3][0], color=GOLD, width=SW_BOLD, buff=0.12)
        self.pad_to(A("one small piece") - 0.8)
        self.play(FadeIn(nf2, scale=1.4), FadeIn(nf2_tag), run_time=0.5)
        self.play(ShowCreation(route),
                  *[p.animate.fade(0.6) for k, p in enumerate(pieces) if k != 3],
                  run_time=0.9)

        # "everyone agrees, verifiably, which piece is yours"
        agree = rich([("everyone agrees", STAR), ("— verifiably —", GOLD),
                      ("which piece is yours", STAR)])
        agree.move_to(UP * CAPTION_Y)
        ck = checkmark(0.5, GOLD).next_to(pieces[3], DOWN, buff=0.3)
        self.pad_to(A("which piece is yours") - 0.5)
        self.play(FadeIn(agree, shift=UP * 0.15), ShowCreation(ck), run_time=0.8)
        self.pad_to(A("strange sounding") - 0.3)
        self.play(Indicate(agree, color=STAR, scale_factor=1.06), run_time=0.7)

        # "the answer comes from 150-year-old number theory" — the QR tease
        self.pad_to(A("the answer comes") - 0.2)
        self.play(FadeOut(VGroup(mini, pieces, nf2, nf2_tag, route, agree, ck, verdict)),
                  run_time=0.6)
        # the QR tease: "does x have a square root mod p?" — the question act 5 answers
        sq = fix_vinculum(mtex("sqrt(x)", size=210, color=GOLD), GOLD)
        qr = mtex('x equiv y^2 med (mod p) thin ?', size=FS_HEAD + 6, color=STAR)
        oldnum = itex("150-year-old number theory", size=FS_BODY, color=MUT)
        tease = VGroup(sq, qr, oldnum).arrange(DOWN, buff=0.55)
        tease.move_to(STAGE_CENTER + UP * 0.1)
        self.play(FadeIn(sq, scale=0.8), run_time=0.8)
        self.pad_to(A("number theory") - 0.6)
        self.play(FadeIn(qr, shift=UP * 0.15), run_time=0.6)
        self.play(FadeIn(oldnum, shift=UP * 0.1), run_time=0.6)
        self.add(sq)
        self.pad_to(scene_T("4.2"))

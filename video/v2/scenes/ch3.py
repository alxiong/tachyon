"""Chapter 3 — Time passes: nullifiers that evolve (scenes 3.1, 3.2, 3.3)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style import *  # noqa: E402,F403


def now_cursor(rail, e):
    tri = Triangle().set_fill(STAR, 1).set_stroke(width=0).scale(0.11).rotate(PI)
    tri.move_to(rail.center_of(e, dy=0.32))
    lab = label("now", size=FS_SMALL, color=STAR).next_to(tri, UP, buff=0.08)
    return VGroup(tri, lab)


def nf_chip(sub, color=STAR, size=FS_LABEL):
    tex = f'"nf"_({sub})' if sub != "" else '"nf"'
    return tex_chip(tex, color=color, size=size, pad=0.12)


def side_panel(title, color, w=4.0, h=2.9, center=ORIGIN):
    p = panel(w, h, color=color, fill_opacity=0.04).move_to(center)
    t = label(title, size=FS_BODY, color=color).next_to(p, UP, buff=0.15)
    g = VGroup(p, t)
    g.box, g.title = p, t
    return g


class Scene31(TimedScene):
    def construct(self):
        SID = "3.1"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731

        rail = EpochRail(first=4, last=10)
        birth = bead(GOLD, r=0.11).move_to(rail.center_of(5))
        cur = now_cursor(rail, 5)
        self.add(rail, birth, cur)
        self.wait(0.3)

        # --- time passes ----------------------------------------------------------
        self.pad_to(A("epoch 6|epic 6") - 0.2)
        self.play(cur.animate.move_to(now_cursor(rail, 6)), Flash(rail.gate(6).get_center(), color=STAR),
                  run_time=0.8)
        self.pad_to(A("then 7") - 0.1)
        self.play(cur.animate.move_to(now_cursor(rail, 7)), Flash(rail.gate(7).get_center(), color=STAR),
                  run_time=0.8)
        self.pad_to(A("sits there") - 0.2)
        self.play(Indicate(birth, color=GOLD, scale_factor=1.8), Flash(birth.get_center(), color=GOLD), run_time=1.0)

        wallet = side_panel("wallet", GOLD, center=LEFT * 4.2 + UP * 0.6)
        tok = proof_token(0.22).move_to(wallet.box.get_center() + UP * 0.3)
        tok_lab = label("exclusion proof", size=FS_LABEL, color=GOLD).next_to(tok, DOWN, buff=0.3)
        self.pad_to(A("exclusion proof") - 0.4)
        self.play(FadeIn(wallet), FadeIn(tok, scale=0.5), FadeIn(tok_lab), run_time=0.9)
        self.pad_to(A("every stamp") - 0.2)
        stamps = VGroup()
        for e, dx in [(6, -0.3), (6, 0.25), (7, -0.15), (7, 0.3)]:
            b = Square(0.16).rotate(PI / 4).set_fill(STAR, 0.9).set_stroke(width=0)
            stamps.add(b.move_to(rail.center_of(e, dy=0.0) + RIGHT * dx))
        rings = VGroup()
        for i, s in enumerate(stamps):
            r = Circle(radius=0.4 + 0.08 * i).set_stroke(AMBER, 1.8, 0.8).move_to(tok)
            rings.add(r)
            self.play(FadeIn(s, scale=0.4), ShowCreation(r), run_time=0.55)

        # --- outsource to an OSS --------------------------------------------------------
        self.pad_to(A("nobody wants") - 0.2)
        wallet.save_state()
        self.play(wallet.animate.fade(0.5), run_time=0.8)
        oss = side_panel("service", CYAN, center=RIGHT * 4.2 + UP * 0.6)
        self.pad_to(A("hand the job") - 0.2)
        self.play(FadeIn(oss), run_time=0.7)
        moving = VGroup(tok, rings)
        self.play(moving.animate.move_to(oss.box.get_center() + UP * 0.3),
                  tok_lab.animate.next_to(oss.box.get_center() + UP * 0.3 + DOWN * 0.65, DOWN, buff=0.0),
                  run_time=1.0)
        self.pad_to(A("oblivious") - 0.2)
        oss_full = label("oblivious syncing service (OSS)", size=FS_LABEL, color=CYAN)
        oss_full.next_to(oss.box, UP, buff=0.15)
        self.play(Transform(oss.title, oss_full), run_time=0.9)
        self.pad_to(A("watches the chain") - 0.2)
        more = VGroup()
        for e, dx in [(7, 0.0), (8, -0.25), (8, 0.25)]:
            b = Square(0.16).rotate(PI / 4).set_fill(STAR, 0.9).set_stroke(width=0)
            more.add(b.move_to(rail.center_of(e) + RIGHT * dx))
        stamps[3].shift(RIGHT * 0.0)
        self.play(cur.animate.move_to(now_cursor(rail, 8)), run_time=0.5)
        for b in more:
            self.play(FadeIn(b, scale=0.4), Indicate(tok, color=CYAN, scale_factor=1.25), run_time=0.45)

        # --- the problem: the OSS must know nf --------------------------------------------
        self.pad_to(A("here's the problem") - 0.2)
        title = scene_title("The service must know nf")
        self.play(Write(title), FadeOut(tok_lab), run_time=1.2)
        self.pad_to(A("has to know") - 0.3)
        wnf = nf_chip("", color=GOLD).move_to(wallet.box.get_center() + DOWN * 0.6)
        self.play(Restore(wallet), FadeIn(wnf), run_time=0.6)
        onf = wnf.copy()
        self.play(onf.animate.move_to(oss.box.get_center() + DOWN * 0.75).set_color(CYAN), run_time=0.9)
        self.pad_to(A("whoever knows") - 0.2)
        self.play(cur.animate.move_to(now_cursor(rail, 9)), run_time=0.6)
        spent_nf = nf_chip("", color=FLARE).move_to(rail.center_of(9, dy=0.95))
        spend_mark = Triangle().set_fill(FLARE, 1).set_stroke(width=0).scale(0.12).rotate(PI)
        spend_mark.move_to(rail.center_of(9))
        self.pad_to(A("recognizes") - 0.2)
        self.play(FadeIn(spent_nf, shift=0.2 * DOWN), GrowFromCenter(spend_mark), run_time=0.8)
        link = DashedLine(onf.get_bottom(), spent_nf.get_top(), dash_length=0.1)
        link.set_stroke(FLARE, SW)
        self.pad_to(A("the moment") - 0.1)
        self.play(ShowCreation(link), run_time=0.9)
        self.pad_to(A("exactly when") - 0.2)
        same = label("same value: linked!", size=FS_LABEL, color=FLARE).next_to(link.get_center(), LEFT, buff=0.2)
        self.play(FadeIn(same), Flash(spent_nf.get_center(), color=FLARE, flash_radius=0.5), run_time=0.8)
        self.pad_to(A("privacy disaster") - 0.1)
        self.play(Indicate(same, color=FLARE, scale_factor=1.15), run_time=0.8)

        # --- the fix: evolve per epoch ------------------------------------------------------
        self.pad_to(A("fix is") - 0.6)
        title2 = scene_title("Fix: one nullifier per epoch")
        self.play(FadeOut(VGroup(link, same, spent_nf, onf, wnf)), Transform(title, title2), run_time=0.9)
        self.pad_to(A("different nullifier") - 0.4)
        chips = VGroup(*[nf_chip(str(e), color=STAR, size=FS_SMALL).move_to(rail.center_of(e, dy=1.15))
                         for e in range(4, 11)])
        self.play(LaggedStart(*[FadeIn(c, shift=0.15 * UP) for c in chips], lag_ratio=0.12), run_time=1.4)
        self.pad_to(A("share with") - 0.2)
        share = chips[2].copy()
        self.play(share.animate.move_to(oss.box.get_center() + DOWN * 0.75).set_color(CYAN),
                  chips[2].animate.set_color(CYAN), run_time=1.0)
        self.pad_to(A("reveal") - 0.2)
        rev = chips[5].copy()
        self.play(chips[5].animate.set_color(FLARE), rev.animate.scale(1.25).set_color(FLARE).move_to(
            rail.center_of(9, dy=1.75)), run_time=0.9)
        link2 = DashedLine(share.get_left(), rev.get_right(), dash_length=0.1).set_stroke(MUT, SW)
        self.play(ShowCreation(link2), run_time=0.6)
        cross = Cross(link2, stroke_color=GOLD, stroke_width=[0, 5, 0]).scale(0.25)
        unl = label("unlinkable", size=FS_LABEL, color=GOLD).next_to(link2, LEFT, buff=0.3)
        self.play(ShowCreation(cross), FadeIn(unl), link2.animate.set_stroke(opacity=0.3), run_time=0.7)

        # --- the cost: an invariant breaks ------------------------------------------------------
        self.pad_to(A("worked on") - 0.2)
        stage = VGroup(wallet, oss, tok, rings, share, rev, link2, cross, unl, title)
        self.play(FadeOut(stage), run_time=0.8)
        banner = mtex('1 "note" = 1 "nullifier"', size=FS_HEAD + 6, color=STAR).move_to(UP * 1.4)
        frame_b = SurroundingRectangle(banner, buff=0.3).set_stroke(STAR, SW).round_corners(0.12)
        self.play(FadeIn(banner), ShowCreation(frame_b), run_time=0.8)
        self.pad_to(A("breaks") - 0.1)
        crack = VMobject().set_points_as_corners([
            frame_b.get_top() + LEFT * 0.2, banner.get_center() + RIGHT * 0.25 + UP * 0.3,
            banner.get_center() + LEFT * 0.2, banner.get_center() + RIGHT * 0.15 + DOWN * 0.3,
            frame_b.get_bottom() + LEFT * 0.1]).set_stroke(FLARE, SW_BOLD)
        self.play(ShowCreation(crack), run_time=0.6)
        self.pad_to(A("one note") - 0.2)
        old = label("since Zerocash", size=FS_LABEL, color=MUT).next_to(frame_b, DOWN, buff=0.25)
        self.play(FadeIn(old), VGroup(banner, frame_b, crack).animate.fade(0.3), run_time=0.7)
        self.pad_to(A("owes us") - 0.2)
        owes = bullets(["a new way to derive nullifiers", "a new rule against double spending"],
                       size=FS_BODY, mark_color=GOLD).move_to(DOWN * 0.95)
        self.pad_to(A("a new way") - 0.1)
        self.play(FadeIn(owes[0], shift=0.2 * RIGHT), run_time=0.7)
        self.pad_to(A("a new rule") - 0.1)
        self.play(FadeIn(owes[1], shift=0.2 * RIGHT), run_time=0.7)
        self.pad_to(A("derivation comes") - 0.1)
        nxt = label("next", size=FS_LABEL, color=GOLD).next_to(owes[0], RIGHT, buff=0.4)
        self.play(FadeIn(nxt), Indicate(owes[0], color=GOLD, scale_factor=1.05), run_time=0.8)
        self.pad_to(A("the rule comes") - 0.1)
        later = label("at the validator", size=FS_LABEL, color=MUT).next_to(owes[1], RIGHT, buff=0.4)
        self.play(FadeIn(later), run_time=0.7)
        self.pad_to(scene_T(SID))


class Scene32(TimedScene):
    def construct(self):
        SID = "3.2"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731

        self.wait(0.3)

        # --- the ideal functionality ---------------------------------------------------
        self.pad_to(A("deterministic") - 0.3)
        ideal = rich([('$"nf"_e = "KDF"($', STAR), ('$"nk"$', GOLD), ('$,$', STAR), ('$psi$', GOLD),
                      ('$,$', STAR), ('$e$', STAR), ('$)$', STAR)], size=FS_HEAD + 6, buff=0.06).move_to(UP * 2.0)
        self.play(Write(ideal), run_time=1.2)
        nk_box = SurroundingRectangle(ideal[1], buff=0.08).set_stroke(GOLD, SW_THIN)
        self.pad_to(A("nullifier key") - 0.1)
        self.play(ShowCreation(nk_box), run_time=0.5)
        self.pad_to(A("psi|notes psi") - 0.1)
        psi_box = SurroundingRectangle(ideal[3], buff=0.08).set_stroke(GOLD, SW_THIN)
        self.play(ReplacementTransform(nk_box, psi_box), Indicate(ideal[3], color=GOLD, scale_factor=1.3),
                  run_time=0.7)
        self.pad_to(A("epic e|epoch e") - 0.1)
        e_box = SurroundingRectangle(ideal[5], buff=0.08).set_stroke(STAR, SW_THIN)
        self.play(ReplacementTransform(psi_box, e_box), run_time=0.5)
        props = bullets(["outputs look random",
                         "binds the spending authority and the note",
                         rich([("unlinkable across epochs without", TXT), ('$"nk"$', GOLD)], size=FS_BODY)],
                        size=FS_BODY).move_to(DOWN * 0.3)
        self.pad_to(A("look random") - 0.4)
        self.play(FadeOut(e_box), FadeIn(props[0], shift=0.2 * RIGHT), run_time=0.6)
        self.pad_to(A("bind both") - 0.2)
        self.play(FadeIn(props[1], shift=0.2 * RIGHT), run_time=0.6)
        self.pad_to(A("stay unlinkable") - 0.2)
        self.play(FadeIn(props[2], shift=0.2 * RIGHT), run_time=0.6)

        # --- constrained PRF: too costly -------------------------------------------------
        self.pad_to(A("constrained") - 0.2)
        self.play(FadeOut(props), ideal.animate.scale(0.75).to_edge(UP, buff=0.4),
                  run_time=0.9)
        cprf = boxed(VGroup(label("constrained PRF", size=FS_BODY, color=STAR),
                            label("delegate a key for a range of epochs", size=FS_LABEL, color=MUT)
                            ).arrange(DOWN, buff=0.18), color=MUT, pad=0.3).move_to(DOWN * 0.6)
        self.play(FadeIn(cprf, shift=0.2 * UP), run_time=0.8)
        self.pad_to(A("ggm") - 0.3)
        ggm = label("GGM tree: expensive in a circuit", size=FS_BODY, color=FLARE).next_to(cprf, DOWN, buff=0.35)
        self.play(FadeIn(ggm), run_time=0.7)
        self.pad_to(A("expensive") + 0.2)
        x_out = Cross(cprf, stroke_color=FLARE, stroke_width=[0, 6, 0])
        self.play(ShowCreation(x_out), cprf.animate.fade(0.5), run_time=0.6)

        # --- simpler: user derives, OSS gets bare pairs ------------------------------------------
        self.pad_to(A("simpler route") - 0.6)
        self.play(FadeOut(VGroup(cprf, ggm, x_out)), run_time=0.6)
        wallet = side_panel("wallet: derives + proves", GOLD, w=4.4, h=3.6, center=LEFT * 4.0 + DOWN * 0.6)
        oss = side_panel("service: bare pairs", CYAN, w=4.4, h=3.6, center=RIGHT * 4.0 + DOWN * 0.6)
        self.pad_to(A("the user derives") - 0.2)
        self.play(FadeIn(wallet), run_time=0.7)
        pairs = VGroup(*[mtex(f'({i}, "nf"_{i})', size=FS_LABEL, color=GOLD) for i in (6, 7, 8)])
        pairs.arrange(DOWN, buff=0.22).move_to(wallet.box)
        self.play(LaggedStart(*[FadeIn(p, shift=0.1 * RIGHT) for p in pairs], lag_ratio=0.25), run_time=0.9)
        self.pad_to(A("gets nothing") - 0.3)
        self.play(FadeIn(oss), run_time=0.6)
        bare = pairs.copy()
        self.play(bare.animate.move_to(oss.box.get_center() + LEFT * 0.9).set_color(TXT), run_time=1.0)
        self.pad_to(A("no evidence") - 0.2)
        mini = note_card(size=FS_BODY).scale(0.7).move_to(UP * 1.05)
        self.play(FadeIn(mini, scale=0.8), run_time=0.4)
        nolink = DashedLine(mini.get_bottom() + DOWN * 0.05, bare.get_top() + UP * 0.1, dash_length=0.1)
        nolink.set_stroke(MUT, SW_THIN, 0.8)
        nx = Cross(Square(0.3).move_to(nolink.get_center()), stroke_color=FLARE, stroke_width=[0, 5, 0])
        self.play(ShowCreation(nolink), run_time=0.6)
        self.play(ShowCreation(nx), run_time=0.4)
        self.pad_to(A("decoy") - 0.4)
        decoy = VGroup(*[mtex(f'({i}, "nf"\')', size=FS_LABEL, color=TXT) for i in (3, 4, 5)])
        decoy.arrange(DOWN, buff=0.22).move_to(oss.box.get_center() + RIGHT * 1.0)
        q1 = label("real?", size=FS_SMALL, color=MUT).next_to(bare, DOWN, buff=0.2)
        q2 = label("decoy?", size=FS_SMALL, color=MUT).next_to(decoy, DOWN, buff=0.2)
        self.play(FadeIn(decoy, shift=0.1 * LEFT), FadeIn(q1), FadeIn(q2), run_time=0.8)
        self.pad_to(A("binding back") - 0.2)
        back = tarrow(oss.box.get_left() + DOWN * 1.2, wallet.box.get_right() + DOWN * 1.2, color=GOLD, width=SW)
        back_lab = label("binding: later, on the wallet", size=FS_LABEL, color=GOLD).next_to(back, DOWN, buff=0.12)
        self.play(GrowArrow(back) if False else ShowCreation(back), FadeIn(back_lab), run_time=0.9)

        # --- concretely: mk and the sponge ---------------------------------------------------------
        self.pad_to(A("concretely") - 0.3)
        self.play(FadeOut(VGroup(wallet, oss, pairs, bare, nolink, nx, decoy, q1, q2, back, back_lab, mini)),
                  FadeOut(ideal), run_time=0.8)
        mk_eq = rich([('$"mk" = "Poseidon"^"mk" ("nk",$', GOLD), ('$psi$', GOLD), ('$)$', GOLD)],
                     size=FS_HEAD, buff=0.06).move_to(UP * 2.4)
        self.pad_to(A("master key") - 0.3)
        self.play(Write(mk_eq), run_time=1.1)
        self.pad_to(A("doing its job") - 0.6)
        self.play(Indicate(mk_eq[1], color=STAR, scale_factor=1.5), Flash(mk_eq[1].get_center(), color=GOLD),
                  run_time=0.9)

        rail = EpochRail(first=4, last=11, width=12.4, y=-3.0)
        sp_body = RoundedRectangle(width=2.0, height=1.0, corner_radius=0.12).set_fill(AMBER, 0.08)
        sp_body.set_stroke(AMBER, SW, 0.9)
        sp_waves = VGroup(*[Line(sp_body.get_left() + RIGHT * 0.25 + UP * dy, sp_body.get_right() + LEFT * 0.25 + UP * dy,
                                 stroke_width=1.6, stroke_color=AMBER, stroke_opacity=0.6) for dy in (-0.2, 0, 0.2)])
        sp_tag = label("Poseidon", size=FS_SMALL, color=AMBER).next_to(sp_body, LEFT, buff=0.25)
        sp = VGroup(sp_body, sp_waves, sp_tag).move_to(UP * 0.35)
        mk_in = tex_chip('"mk"', color=GOLD, size=FS_LABEL).next_to(sp_body, UP, buff=0.35)
        self.pad_to(A("one poseidon") - 0.2)
        self.play(FadeIn(rail), FadeIn(sp), FadeIn(mk_in, shift=0.2 * RIGHT), run_time=0.9)
        perm1 = mtex('"Permute"("mk", 1)', size=FS_LABEL, color=AMBER).next_to(sp_body, RIGHT, buff=0.5)
        self.pad_to(A("squeezes") - 0.1)
        self.play(mk_in.animate.move_to(sp_body).set_opacity(0), FadeIn(perm1), run_time=0.8)
        out1 = VGroup(*[nf_chip(str(e), color=GOLD, size=FS_SMALL).move_to(sp.get_bottom() + DOWN * 0.4)
                        for e in range(4, 8)])
        self.play(LaggedStart(*[o.animate.move_to(rail.center_of(e, dy=0.75)) for o, e in zip(out1, range(4, 8))],
                              lag_ratio=0.15), run_time=1.3)
        rate = label("Rate = 4: one permutation, four epochs", size=FS_LABEL, color=AMBER).move_to(UP * 1.55)
        self.pad_to(A("rate four|rate 4") - 0.2)
        self.play(FadeIn(rate), run_time=0.6)
        br1 = bracket(out1, color=AMBER, buff=0.15)
        self.pad_to(A("four through seven|4 through 7") - 0.1)
        self.play(ShowCreation(br1), run_time=0.6)
        self.pad_to(A("the next gives") - 0.2)
        perm2 = mtex('"Permute"("mk", 2)', size=FS_LABEL, color=AMBER).move_to(perm1)
        out2 = VGroup(*[nf_chip(str(e), color=GOLD, size=FS_SMALL).move_to(sp.get_bottom() + DOWN * 0.4)
                        for e in range(8, 12)])
        self.play(Transform(perm1, perm2), run_time=0.4)
        self.play(LaggedStart(*[o.animate.move_to(rail.center_of(e, dy=0.75)) for o, e in zip(out2, range(8, 12))],
                              lag_ratio=0.15), run_time=1.0)
        br2 = bracket(out2, color=AMBER, buff=0.15)
        self.play(ShowCreation(br2), run_time=0.3)
        self.pad_to(A("from here on") - 0.2)
        short = mtex('"nf"_e = f_"mk" (e)', size=FS_HEAD, color=STAR)
        short_box = boxed(short, color=STAR, pad=0.22).move_to(RIGHT * 4.6 + UP * 1.55)
        self.play(FadeOut(rate), FadeIn(short_box, shift=0.2 * LEFT), run_time=0.9)

        # --- security in one line -----------------------------------------------------------------
        self.pad_to(A("security") - 0.2)
        self.play(FadeOut(VGroup(sp, perm1, mk_eq)), short_box.animate.to_edge(UP, buff=0.4),
                  run_time=0.9)
        sec = label("unrevealed nullifiers stay indistinguishable from random", size=FS_BODY, color=STAR)
        sec.move_to(UP * 1.8)
        self.play(FadeIn(sec), run_time=0.8)
        carried = bullets(["balance", "privacy against the sender (never learns nk)",
                           "unlinkability across epochs, delegation included"], size=FS_BODY).move_to(UP * 0.1)
        self.pad_to(A("carries balance|balance") - 0.1)
        self.play(FadeIn(carried[0], shift=0.2 * RIGHT), run_time=0.5)
        self.pad_to(A("privacy against") - 0.1)
        self.play(FadeIn(carried[1], shift=0.2 * RIGHT), run_time=0.5)
        self.pad_to(A("and unlinkability") - 0.1)
        self.play(FadeIn(carried[2], shift=0.2 * RIGHT), run_time=0.5)
        self.pad_to(A("holds a list") - 0.2)
        held = VGroup(out1[2], out1[3], out2[0])
        lst = SurroundingRectangle(held, buff=0.12).set_stroke(CYAN, SW)
        lst_lab = label("the service's list", size=FS_LABEL, color=CYAN).next_to(lst, UP, buff=0.12)
        self.play(ShowCreation(lst), FadeIn(lst_lab), held.animate.set_color(CYAN), run_time=0.8)
        self.pad_to(A("beyond that list") - 0.2)
        rest = VGroup(out1[0], out1[1], out2[1], out2[2], out2[3])
        self.play(rest.animate.fade(0.6), run_time=0.7)

        # --- the cross-epoch race --------------------------------------------------------------------
        self.pad_to(A("timing problem") - 0.3)
        self.play(FadeOut(VGroup(sec, carried, short_box, lst, lst_lab, out1, out2, br1, br2, rail)),
                  run_time=0.6)
        title = scene_title("The cross-epoch race")
        lane = Line(LEFT * 6.0, RIGHT * 6.0, stroke_color=DIM, stroke_width=SW).shift(DOWN * 0.5)
        lane_lab = label("mempool", size=FS_LABEL, color=MUT).next_to(lane, DOWN, buff=0.2).to_edge(LEFT, buff=0.6)
        gate = sentinel_gate(h=2.4).move_to(RIGHT * 1.5 + DOWN * 0.5)
        e_lab = mtex("e", size=FS_BODY, color=MUT).next_to(gate, LEFT, buff=0.9).shift(DOWN * 0.7)
        e1_lab = mtex("e + 1", size=FS_BODY, color=MUT).next_to(gate, RIGHT, buff=0.9).shift(DOWN * 0.7)
        self.play(Write(title), ShowCreation(lane), FadeIn(lane_lab), FadeIn(gate), FadeIn(e_lab),
                  FadeIn(e1_lab), run_time=0.8)
        self.pad_to(A("say a spend") - 0.2)
        tx = VGroup(RoundedRectangle(width=1.7, height=1.0, corner_radius=0.1).set_stroke(STAR, SW).set_fill(STAR, 0.05),
                    nf_chip("e", color=STAR, size=FS_SMALL))
        tx[1].move_to(tx[0])
        tx_lab = label("spend", size=FS_SMALL, color=TXT).next_to(tx[0], UP, buff=0.1)
        txg = VGroup(tx, tx_lab).move_to(LEFT * 3.5 + UP * 0.45)
        self.play(FadeIn(txg, shift=0.3 * RIGHT), run_time=0.7)
        self.pad_to(A("waits") - 0.1)
        self.play(txg.animate.shift(RIGHT * 2.0), run_time=1.2)
        self.pad_to(A("ticks over") - 0.2)
        self.play(gate.animate.move_to(LEFT * 3.2 + DOWN * 0.5), e_lab.animate.shift(LEFT * 4.7),
                  e1_lab.animate.shift(LEFT * 4.7), run_time=1.0)
        self.pad_to(A("stale") - 0.3)
        self.play(tx[0].animate.set_stroke(FLARE), tx[1].animate.set_color(FLARE),
                  FadeIn(label("stale", size=FS_LABEL, color=FLARE).next_to(tx[0], RIGHT, buff=0.2)),
                  run_time=0.6)
        stale = self.mobjects[-1]
        self.pad_to(A("nobody else") - 0.1)
        who = VGroup(label("miner", size=FS_LABEL, color=TXT), label("service", size=FS_LABEL, color=CYAN))
        who.arrange(DOWN, buff=0.3).move_to(RIGHT * 4.6 + UP * 1.5)
        xs = VGroup(*[Cross(w, stroke_color=FLARE, stroke_width=[0, 4, 0]) for w in who])
        cant = label("can't refresh it", size=FS_LABEL, color=FLARE).next_to(who, DOWN, buff=0.3)
        self.pad_to(A("not the minor|not the miner") - 0.2)
        self.play(FadeIn(who[0]), ShowCreation(xs[0]), FadeIn(cant), run_time=0.6)
        self.pad_to(A("not the service") - 0.1)
        self.play(FadeIn(who[1]), ShowCreation(xs[1]), run_time=0.6)
        self.pad_to(A("so every spend") - 0.3)
        tx2 = VGroup(RoundedRectangle(width=2.6, height=1.0, corner_radius=0.1).set_stroke(GOLD, SW).set_fill(GOLD, 0.05),
                     VGroup(nf_chip("e", color=GOLD, size=FS_SMALL), nf_chip("e+1", color=GOLD, size=FS_SMALL)).arrange(RIGHT, buff=0.15))
        tx2[1].move_to(tx2[0])
        tx2.move_to(tx[0])
        self.play(FadeOut(stale), ReplacementTransform(tx, tx2), FadeOut(VGroup(who, xs, cant)), run_time=0.9)
        self.pad_to(A("plus one", 2) - 0.2)
        ok = label("valid on both sides of the boundary", size=FS_LABEL, color=GOLD).next_to(tx2, DOWN, buff=0.25)
        self.play(FadeIn(ok), Flash(gate.get_top(), color=GOLD), run_time=0.8)

        # --- the empty slot: padding -----------------------------------------------------------------
        self.pad_to(A("remember") - 0.3)
        st = stamp_card().move_to(LEFT * 3.4 + UP * 0.3)
        cm = tg_chip('"cm"', color=GOLD).move_to(st.slots[0])
        self.play(FadeOut(VGroup(lane, lane_lab, gate, e_lab, e1_lab, tx2, tx_lab, ok)),
                  Transform(title, scene_title("Every action carries two tachygrams")),
                  FadeIn(st), FadeIn(cm), run_time=0.7)
        self.pad_to(A("empty slot") - 0.1)
        self.play(Indicate(st.slots[1], color=STAR, scale_factor=1.25), run_time=0.7)
        self.pad_to(A("dummy") - 0.3)
        dummy = tg_chip('"tg"_bot', color=MUT).move_to(st.slots[1])
        dummy_lab = mtex('"tg"_bot = H("random")', size=FS_LABEL, color=MUT).next_to(st, DOWN, buff=0.3)
        self.play(FadeIn(dummy, scale=0.5), FadeIn(dummy_lab), run_time=0.8)
        # without padding: arity leak
        self.pad_to(A("without it") - 0.2)
        sp_dom = VGroup(label("spend", size=FS_LABEL, color=TXT),
                        VGroup(tg_chip('"nf"_e'), tg_chip('"nf"_(e+1)')).arrange(RIGHT, buff=0.12))
        sp_dom.arrange(RIGHT, buff=0.3)
        out_dom = VGroup(label("output", size=FS_LABEL, color=TXT), VGroup(tg_chip('"cm"')))
        out_dom.arrange(RIGHT, buff=0.3)
        doms = VGroup(sp_dom, out_dom).arrange(DOWN, buff=0.4, aligned_edge=LEFT).move_to(RIGHT * 3.4 + UP * 0.6)
        self.play(FadeIn(sp_dom), run_time=0.6)
        self.pad_to(A("output just one") - 0.2)
        self.play(FadeIn(out_dom), run_time=0.6)
        self.pad_to(A("counting") - 0.2)
        leak = mtex('"spends" = t - n', size=FS_BODY, color=FLARE).next_to(doms, DOWN, buff=0.45)
        leak_lab = label("tachygram count leaks the split", size=FS_LABEL, color=FLARE).next_to(leak, DOWN, buff=0.15)
        self.play(FadeIn(leak), FadeIn(leak_lab), run_time=0.8)
        self.pad_to(A("with the padding") - 0.2)
        pad_chip = tg_chip('"tg"_bot', color=MUT).next_to(out_dom[1][0], RIGHT, buff=0.12)
        two = mtex("t = 2 n", size=FS_BODY, color=GOLD).move_to(leak)
        self.play(FadeIn(pad_chip, scale=0.5), Transform(leak, two), FadeOut(leak_lab), run_time=0.8)
        self.pad_to(A("exactly two") - 0.2)
        self.play(Indicate(VGroup(sp_dom[1], out_dom[1], pad_chip), color=GOLD, scale_factor=1.08), run_time=0.8)
        self.pad_to(scene_T(SID))


def xi(i, x0=-5.6, step=1.4):
    return x0 + (i - 4) * step


def ftile(i, color=GOLD, w=1.1, h=0.7):
    box = RoundedRectangle(width=w, height=h, corner_radius=0.08).set_fill(color, 0.12)
    box.set_stroke(color, SW_THIN, 0.9)
    t = mtex(f"F_({i})", size=FS_LABEL, color=color).move_to(box)
    return VGroup(box, t)


class Scene33(TimedScene):
    def construct(self):
        SID = "3.3"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731
        YR, YS = 1.55, 0.25

        self.wait(0.3)
        self.pad_to(A("first real") - 0.3)
        title = scene_title("Ranged nullifier commitment")
        self.play(Write(title), run_time=1.0)

        # --- the two ranges -------------------------------------------------------------
        R = VGroup(*[nf_chip(str(i), color=GOLD, size=FS_LABEL).move_to([xi(i), YR, 0]) for i in range(4, 12)])
        S = VGroup(*[nf_chip(str(i), color=CYAN, size=FS_LABEL).move_to([xi(i), YS, 0]) for i in (6, 7, 8)])
        rl = rich([("wallet", GOLD), ('$R = [4, 12)$', GOLD)], size=FS_LABEL).next_to(R, LEFT, buff=0.3)
        rl.next_to(R, UP, buff=0.3).align_to(R, LEFT)
        sl = rich([("service", CYAN), ('$S = [6, 9)$', CYAN)], size=FS_LABEL).next_to(S, DOWN, buff=0.3)
        self.pad_to(A("the wallet has") - 0.2)
        self.play(LaggedStart(*[FadeIn(c, shift=0.1 * DOWN) for c in R], lag_ratio=0.1), FadeIn(rl), run_time=1.6)
        self.pad_to(A("the service has") - 0.2)
        self.play(LaggedStart(*[FadeIn(c, shift=0.1 * UP) for c in S], lag_ratio=0.2), FadeIn(sl), run_time=1.2)
        self.pad_to(A("committed") - 0.2)
        s_box = SurroundingRectangle(S, buff=0.12).set_stroke(CYAN, SW_THIN, 0.8)
        self.play(ShowCreation(s_box), run_time=0.6)
        self.pad_to(A("eventually") - 0.2)
        ups = VGroup(*[tarrow(s.get_top(), R[i - 4].get_bottom(), color=STAR, width=SW_THIN)
                       for s, i in zip(S, (6, 7, 8))])
        self.play(LaggedStart(*[ShowCreation(u) for u in ups], lag_ratio=0.3), run_time=1.2)
        self.pad_to(A("same epic index|same epoch index") - 0.1)
        idx = label("same index, same value", size=FS_LABEL, color=STAR).next_to(ups, RIGHT, buff=0.5)
        self.play(FadeIn(idx), run_time=0.6)
        self.pad_to(A("both sides build") - 0.1)
        self.play(LaggedStart(*[Indicate(c, color=GOLD, scale_factor=1.15) for c in R], lag_ratio=0.12),
                  LaggedStart(*[Indicate(c, color=CYAN, scale_factor=1.15) for c in S], lag_ratio=0.3),
                  run_time=2.2)

        # --- why not a vector commitment ----------------------------------------------------
        self.pad_to(A("vector commitment") - 0.2)
        vc = label("vector commitment?", size=FS_BODY, color=STAR).move_to(DOWN * 1.6 + LEFT * 3.3)
        self.play(FadeIn(vc), FadeOut(idx), run_time=0.6)
        self.pad_to(A("rsa") - 0.2)
        rsa = label("RSA groups or pairings", size=FS_LABEL, color=MUT).next_to(vc, DOWN, buff=0.25)
        self.play(FadeIn(rsa), run_time=0.6)
        self.pad_to(A("neither is friendly") - 0.1)
        st1 = Line(VGroup(vc, rsa).get_left(), VGroup(vc, rsa).get_right(), stroke_color=FLARE, stroke_width=SW)
        unf = label("not circuit-friendly", size=FS_LABEL, color=FLARE).next_to(rsa, DOWN, buff=0.2)
        self.play(ShowCreation(st1), FadeIn(unf), run_time=0.7)
        self.pad_to(A("prover can|proverb can") - 0.4)
        std = label("standard VC: prover may commit to anything", size=FS_LABEL, color=MUT)
        std.move_to(DOWN * 1.6 + RIGHT * 3.2)
        self.play(FadeIn(std), run_time=0.6)
        self.pad_to(A("every update") - 0.2)
        here = label("here: every update proven honest", size=FS_LABEL, color=GOLD).next_to(std, DOWN, buff=0.3)
        self.play(FadeIn(here, shift=0.1 * UP), run_time=0.7)
        self.pad_to(A("honest") - 0.1)
        ck = checkmark(0.35, GOLD).next_to(here, RIGHT, buff=0.2)
        self.play(ShowCreation(ck), run_time=0.5)
        self.pad_to(A("opens up") - 0.2)
        ds = label("a bigger design space", size=FS_LABEL, color=GOLD).next_to(here, DOWN, buff=0.25)
        self.play(FadeIn(ds), run_time=0.6)

        # --- the cubic factor ---------------------------------------------------------------
        self.pad_to(A("encode each pair") - 0.3)
        self.play(FadeOut(VGroup(vc, rsa, st1, unf, std, here, ck, ds, ups)), run_time=0.7)
        F = rich([('$F_(i, "nf"_i)(X) = ($', STAR), ('$(i+1)$', GOLD), ('$X +$', STAR), ('$"nf"_i$', GOLD),
                  ('$)^3$', STAR), ('$- c$', AMBER)], size=FS_HEAD + 4, buff=0.06).move_to(DOWN * 1.75)
        src = R[2].copy()
        self.play(src.animate.move_to(F.get_center()).set_opacity(0), FadeIn(F[0]), run_time=0.9)
        self.pad_to(A("take i plus|take I plus") - 0.1)
        pos = label("position", size=FS_LABEL, color=GOLD).next_to(F[1], DOWN, buff=0.3)
        self.play(FadeIn(F[1], scale=1.3), FadeIn(pos), run_time=0.6)
        self.pad_to(A("times x") - 0.1)
        val = label("value", size=FS_LABEL, color=GOLD).next_to(F[3], DOWN, buff=0.3)
        self.play(FadeIn(F[2]), FadeIn(F[3], scale=1.3), FadeIn(val), run_time=0.7)
        self.pad_to(A("cube that") - 0.1)
        self.play(FadeIn(F[4], scale=1.3), run_time=0.5)
        self.pad_to(A("subtract") - 0.1)
        cl = label("fixed public constant", size=FS_LABEL, color=AMBER).next_to(F[5], UP, buff=0.3)
        self.play(FadeIn(F[5], scale=1.3), FadeIn(cl), run_time=0.6)

        self.pad_to(A("multiply these") - 0.2)
        tiles = VGroup(*[ftile(i).move_to([xi(i), YR, 0]) for i in range(4, 12)])
        # keep the factor definition on screen (left) beside the product (right)
        F_tgt = F.copy()
        F_tgt.scale(min(1.0, 6.1 / F_tgt.get_width())).move_to([-3.35, -1.75, 0])
        g_R = mtex('g_R (X) = product_(i in R) F_(i, "nf"_i)(X)', size=FS_HEAD, color=GOLD)
        g_R.move_to([3.35, -1.75, 0])
        self.play(LaggedStart(*[ReplacementTransform(c, t) for c, t in zip(R, tiles)], lag_ratio=0.08),
                  FadeOut(VGroup(pos, val, cl)), Transform(F, F_tgt), run_time=1.2)
        self.play(TransformFromCopy(F, g_R), run_time=0.8)
        self.pad_to(A("index multi") - 0.3)
        ims = label("an indexed multiset", size=FS_LABEL, color=GOLD).next_to(g_R, DOWN, buff=0.3)
        self.play(FadeIn(ims), run_time=0.6)
        self.pad_to(A("appending") - 0.2)
        t12 = ftile(12).move_to([xi(12), YR, 0])
        open_end = DashedLine(t12.get_right() + RIGHT * 0.1, t12.get_right() + RIGHT * 0.7, dash_length=0.08)
        open_end.set_stroke(GOLD, SW_THIN)
        self.play(FadeIn(t12, shift=0.4 * LEFT), run_time=0.7)
        self.pad_to(A("no fixed") - 0.2)
        self.play(ShowCreation(open_end), FadeIn(label("no fixed endpoint", size=FS_LABEL, color=GOLD)
                                                 .next_to(t12, DOWN, buff=0.25)), run_time=0.7)
        nfe = self.mobjects[-1]

        # --- containment is division -------------------------------------------------------
        self.pad_to(A("containment") - 0.3)
        S_tiles = VGroup(*[ftile(i, color=CYAN).move_to([xi(i), YS, 0]) for i in (6, 7, 8)])
        self.play(FadeOut(VGroup(t12, open_end, nfe, ims)), FadeOut(s_box),
                  LaggedStart(*[ReplacementTransform(c, t) for c, t in zip(S, S_tiles)], lag_ratio=0.1),
                  run_time=1.0)
        self.pad_to(A("quotient") - 0.2)
        qs = VGroup(*[tiles[i - 4] for i in (4, 5, 9, 10, 11)])
        q_row = VGroup(*[ftile(i, color=STAR).move_to([xi(i), YS - 1.0, 0]) for i in (4, 5, 9, 10, 11)])
        q_lab = mtex("q", size=FS_BODY, color=STAR).next_to(q_row, LEFT, buff=0.35)
        self.play(*[TransformFromCopy(a, b) for a, b in zip(qs, q_row)], FadeIn(q_lab), run_time=1.0)
        div = mtex("g_R (X) = g_S (X) dot q(X)", size=FS_HEAD, color=STAR).move_to(DOWN * 2.75)
        self.pad_to(A("its product") - 0.1)
        self.play(TransformFromCopy(g_R, div), sl.animate.fade(0.4), run_time=1.0)
        self.pad_to(A("all three") - 0.1)
        fixed = label("commit all three, then the challenge", size=FS_LABEL, color=MUT)
        fixed.next_to(div, DOWN, buff=0.18)
        self.play(FadeIn(fixed), run_time=0.6)
        self.pad_to(A("random challenge") - 0.1)
        rr = mtex("g_R (r) = g_S (r) dot q(r)", size=FS_HEAD, color=GOLD).move_to(div)
        self.play(Transform(div, rr), run_time=0.8)
        self.pad_to(A("one identity") - 0.1)
        ck2 = checkmark(0.4, GOLD).next_to(div, RIGHT, buff=0.3)
        self.play(ShowCreation(ck2), Flash(div.get_center(), color=GOLD, flash_radius=2.2), run_time=0.8)
        self.pad_to(A("query port") - 0.4)
        rg = pill("Ragu query port", color=CYAN, size=FS_LABEL).next_to(div, RIGHT, buff=1.0)
        rg_halo = VGroup()
        self.play(FadeIn(rg, shift=0.2 * LEFT), Flash(rg.get_left(), color=CYAN), run_time=0.7)

        # --- soundness ----------------------------------------------------------------------------
        self.pad_to(A("why is this sound") - 0.3)
        self.play(FadeOut(VGroup(tiles, S_tiles, q_row, q_lab, div, fixed, ck2, rg, rg_halo, rl, sl, F, g_R)),
                  Transform(title, scene_title("Why it's sound")), run_time=0.9)
        clock = F13Clock(radius=1.8, center=LEFT * 4.2 + DOWN * 0.4)
        lines = VGroup(
            mtex("p equiv 1 med (mod 3)", size=FS_BODY, color=STAR),
            rich([('$c = 2$', AMBER), ("is a public non-cube", TXT)], size=FS_BODY),
            rich([('$Y^3 - c$', STAR), ("is irreducible", TXT)], size=FS_BODY),
            rich([("so is", TXT), ('$((i+1) X + "nf"_i)^3 - c$', STAR), (", since", TXT), ('$i + 1 != 0$', GOLD)],
                 size=FS_BODY),
        ).arrange(DOWN, buff=0.38, aligned_edge=LEFT).move_to(RIGHT * 2.3 + UP * 0.9)
        self.pad_to(A("our field") - 0.2)
        self.play(FadeIn(lines[0], shift=0.1 * RIGHT), run_time=0.6)
        self.pad_to(A("fix c") - 0.2)
        self.play(FadeIn(lines[1], shift=0.1 * RIGHT), run_time=0.6)
        self.pad_to(A("irreducible") - 0.6)
        self.play(FadeIn(lines[2], shift=0.1 * RIGHT), run_time=0.6)
        self.pad_to(A("invertible") - 0.2)
        self.play(FadeIn(lines[3], shift=0.1 * RIGHT), run_time=0.8)
        self.pad_to(A("13 elements") - 0.4)
        f13 = mtex("bb(F)_13", size=FS_BODY, color=MUT).next_to(clock, UP, buff=0.3)
        self.play(FadeIn(clock), FadeIn(f13), run_time=0.9)
        self.pad_to(A("cubes are") - 0.1)
        cube_lab = label("cubes", size=FS_LABEL, color=GOLD).move_to(clock.c)
        self.play(FadeIn(cube_lab), run_time=0.3)
        for k, ph in [(1, "1 5"), (5, "5 8"), (8, "8 and 12"), (12, "12 and 2")]:
            self.pad_to(A(ph) - 0.05)
            self.play(clock.dot(k).animate.set_fill(GOLD, 1).scale(1.4), clock.num(k).animate.set_color(GOLD),
                      run_time=0.25)
        self.pad_to(A("isn't among") - 0.3)
        two = clock.dot(2)
        ring2 = Circle(radius=0.28).set_stroke(AMBER, SW_BOLD).move_to(two)
        not_c = label("2 is not a cube", size=FS_LABEL, color=AMBER).next_to(clock.num(2), RIGHT, buff=0.25)
        self.play(ShowCreation(ring2), two.animate.set_fill(AMBER, 1), FadeIn(not_c), run_time=0.7)
        self.pad_to(A("unique factorization") - 0.2)
        forge = rich([("forgery needs", TXT), ('$(a_1, b_1) = omega (a_2, b_2)$', FLARE), (",", TXT),
                      ('$omega^3 = 1$', FLARE)], size=FS_BODY).next_to(lines, DOWN, buff=0.55).align_to(lines, LEFT)
        self.play(FadeIn(forge[0]), run_time=0.6)
        self.pad_to(A("cube root") - 0.4)
        self.play(FadeIn(forge[1:]), run_time=0.8)
        self.pad_to(A("below 2|below to") - 0.3)
        scale_cmp = rich([('$i < 2^32$', GOLD), ("but", TXT), ('$omega$', FLARE), ("is a ~255-bit element", TXT)],
                         size=FS_BODY).next_to(forge, DOWN, buff=0.35).align_to(forge, LEFT)
        self.play(FadeIn(scale_cmp[:1]), run_time=0.5)
        self.pad_to(A("enormous") - 0.2)
        self.play(FadeIn(scale_cmp[1:]), run_time=0.6)
        self.pad_to(A("that collision") - 0.1)
        st2 = Line(forge.get_left(), forge.get_right(), stroke_color=GOLD, stroke_width=SW)
        imp = label("impossible", size=FS_LABEL, color=GOLD).next_to(forge, RIGHT, buff=0.2)
        imp.shift(LEFT * max(0, imp.get_right()[0] - 6.6))
        imp.next_to(scale_cmp, DOWN, buff=0.3).align_to(scale_cmp, LEFT)
        self.play(ShowCreation(st2), FadeIn(imp), run_time=0.5)

        # --- inclusion, not order: sentinels -----------------------------------------------------------
        self.pad_to(A("one caution") - 0.3)
        self.play(FadeOut(VGroup(clock, f13, cube_lab, ring2, not_c, lines, forge, scale_cmp, st2, imp)),
                  Transform(title, scene_title("Inclusion, not order")), run_time=0.8)
        row = VGroup(*[ftile(i, color=CYAN) for i in (6, 7, 8)]).arrange(RIGHT, buff=0.35).move_to(UP * 0.5)
        prod = mtex("g_S = F_6 dot F_7 dot F_8", size=FS_BODY, color=CYAN).next_to(row, DOWN, buff=0.45)
        self.play(FadeIn(row), FadeIn(prod), run_time=0.6)
        self.pad_to(A("commutative") - 0.3)
        p0, p2 = row[0].get_center().copy(), row[2].get_center().copy()
        self.play(row[0].animate(path_arc=PI / 2).move_to(p2), row[2].animate(path_arc=PI / 2).move_to(p0), run_time=1.0)
        same = label("same product", size=FS_LABEL, color=MUT).next_to(prod, DOWN, buff=0.2)
        self.play(FadeIn(same), run_time=0.4)
        self.pad_to(A("not order") - 0.2)
        no_ord = label("division proves inclusion, not order", size=FS_BODY, color=FLARE).next_to(same, DOWN, buff=0.35)
        self.play(FadeIn(no_ord), run_time=0.6)
        self.pad_to(A("order and contiguity") - 0.2)
        self.play(row[0].animate(path_arc=PI / 2).move_to(p0), row[2].animate(path_arc=PI / 2).move_to(p2), run_time=0.8)
        ctr = VGroup(*[mtex(str(i), size=FS_LABEL, color=CYAN).next_to(t, UP, buff=0.18) for t, i in zip(row, (6, 7, 8))])
        self.play(FadeIn(ctr, lag_ratio=0.3), run_time=0.6)
        self.pad_to(A("sentinel endpoints") - 0.1)
        g0 = sentinel_gate(h=1.4).next_to(row, LEFT, buff=0.35)
        g1 = sentinel_gate(h=1.4).next_to(row, RIGHT, buff=0.35)
        self.play(GrowFromCenter(g0), GrowFromCenter(g1), run_time=0.7)
        self.pad_to(A("remember that word") - 0.1)
        word = label("sentinel", size=FS_HEAD, color=STAR).next_to(g1, RIGHT, buff=0.4)
        self.play(FadeIn(word, shift=0.1 * LEFT), Indicate(g0), Indicate(g1), run_time=0.9)
        self.pad_to(A("sentinel to sentinel") - 0.2)
        self.play(Flash(g0.get_top(), color=STAR), Flash(g1.get_top(), color=STAR), run_time=0.7)
        self.pad_to(scene_T(SID))

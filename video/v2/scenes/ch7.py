"""Chapter 7 — The other half: the payment protocol (scene 7.1)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style import *  # noqa: E402,F403

PAY = AMBER  # payment-protocol accent in this chapter


def key_pair_chip(top, color):
    return tex_chip(top, color=color, size=FS_LABEL, pad=0.14)


def db_cylinder(name, color=STAR, w=1.9, h=1.2):
    top = Ellipse(width=w, height=0.36).set_stroke(color, SW_THIN).set_fill(color, 0.08)
    body_l = Line(top.get_left(), top.get_left() + DOWN * h, stroke_color=color, stroke_width=SW_THIN)
    body_r = Line(top.get_right(), top.get_right() + DOWN * h, stroke_color=color, stroke_width=SW_THIN)
    bot = Arc(start_angle=PI, angle=PI, radius=1).stretch_to_fit_width(w).stretch_to_fit_height(0.18)
    bot.set_stroke(color, SW_THIN).move_to(top.get_center() + DOWN * h + DOWN * 0.09)
    lab = label(name, size=FS_SMALL, color=color).move_to(top.get_center() + DOWN * h / 2)
    return VGroup(top, body_l, body_r, bot, lab)


def memo_env(tag_tex, color=TXT, tag_color=PAY):
    body = RoundedRectangle(width=1.3, height=0.8, corner_radius=0.05)
    body.set_fill(color, 0.06).set_stroke(color, SW_THIN, 0.8)
    flap = VGroup(Line(body.get_corner(UL), body.get_center() + DOWN * 0.05, stroke_width=1.6, stroke_color=color),
                  Line(body.get_corner(UR), body.get_center() + DOWN * 0.05, stroke_width=1.6, stroke_color=color))
    tag = tex_chip(tag_tex, color=tag_color, size=FS_SMALL, pad=0.08).next_to(body, UP, buff=0.08)
    return VGroup(body, flap, tag)


class Scene71(TimedScene):
    def construct(self):
        SID = "7.1"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731
        self.wait(0.4)

        # --- the cut, recalled ------------------------------------------------------------------
        self.pad_to(A("the cut") - 0.2)
        sh = panel(5.8, 3.4, color=GOLD, fill_opacity=0.04).move_to(LEFT * 3.4)
        pp = panel(5.8, 3.4, color=PAY, fill_opacity=0.04).move_to(RIGHT * 3.4)
        sh_t = label("shielded protocol", size=FS_HEAD, color=GOLD).move_to(sh.get_top() + DOWN * 0.45)
        pp_t = label("payment protocol", size=FS_HEAD, color=PAY).move_to(pp.get_top() + DOWN * 0.45)
        sh_b = mtex('"pk" = "Com"("ak", "nk")', size=FS_LABEL, color=TXT).move_to(sh.get_center() + DOWN * 0.25)
        pp_b = label("addresses, memos, discovery, viewing", size=FS_LABEL, color=TXT)
        pp_b.move_to(pp.get_center() + DOWN * 0.25)
        cut = DashedLine(UP * 2.0, DOWN * 2.0, dash_length=0.12).set_stroke(STAR, SW, 0.8)
        self.play(FadeIn(VGroup(sh, sh_t, sh_b)), FadeIn(VGroup(pp, pp_t, pp_b)), ShowCreation(cut),
                  run_time=1.0)
        self.pad_to(A("delivering notes") - 0.2)
        self.play(sh.animate.fade(0.6), sh_t.animate.set_opacity(0.4), sh_b.animate.set_opacity(0.4),
                  Indicate(pp_t, color=PAY), run_time=0.8)
        self.pad_to(A("sketch") - 0.2)
        cred = label("a sketch of ValarGroup's design", size=FS_LABEL, color=MUT).next_to(pp, DOWN, buff=0.3)
        self.play(FadeIn(cred), run_time=0.6)

        # --- address = (pk, ek) ----------------------------------------------------------------------
        self.pad_to(A("addresses a pair|a pair") - 0.3)
        self.play(FadeOut(VGroup(sh, sh_t, sh_b, pp, pp_t, pp_b, cut, cred)), run_time=0.6)
        addr = mtex('"addr" = ("pk", "ek")', size=FS_HEAD, color=STAR).move_to(UP * 2.4)
        self.play(Write(addr), run_time=0.9)
        pk = key_pair_chip('"pk" = "Com"("ak", "nk")', GOLD).move_to(LEFT * 3.2 + UP * 1.05)
        ek = key_pair_chip('"ek"', PAY).move_to(RIGHT * 3.2 + UP * 1.05)
        ek_l = label("ML-KEM encapsulation key", size=FS_LABEL, color=PAY).next_to(ek, DOWN, buff=0.2)
        self.pad_to(A("the payment key") - 0.1)
        self.play(TransformFromCopy(addr, pk), run_time=0.7)
        self.pad_to(A("encapsulation key") - 0.6)
        self.play(TransformFromCopy(addr, ek), FadeIn(ek_l), run_time=0.8)
        self.pad_to(A("both fresh") - 0.2)
        senders = VGroup()
        for i, x in enumerate((-4.2, 0, 4.2)):
            s = label(f"sender {i + 1}", size=FS_LABEL, color=TXT)
            pr = mtex(f'("pk"_{i + 1}, "ek"_{i + 1})', size=FS_LABEL, color=STAR)
            senders.add(VGroup(s, pr).arrange(DOWN, buff=0.15).move_to([x, -1.2, 0]))
        self.play(LaggedStart(*[FadeIn(s, shift=0.15 * UP) for s in senders], lag_ratio=0.25), run_time=1.0)
        fresh = label("fresh per sender", size=FS_LABEL, color=GOLD).move_to(DOWN * 2.5)
        self.play(FadeIn(fresh), run_time=0.4)

        # --- why not diversification ------------------------------------------------------------------
        self.pad_to(A("why not") - 0.2)
        self.play(FadeOut(VGroup(addr, pk, ek, ek_l, senders, fresh)), run_time=0.6)
        title = scene_title("Why not Orchard-style diversification?")
        self.play(Write(title), run_time=1.0)
        ivk = tex_chip('"ivk"', color=STAR, size=FS_HEAD).move_to(LEFT * 3.4 + DOWN * 0.6)
        dks = VGroup(*[tex_chip(f'[ "ivk" ] G_(d_{i})', color=TXT, size=FS_BODY, pad=0.14) for i in (1, 2, 3)])
        for k, d in enumerate(dks):
            d.move_to(LEFT * 3.4 + np.array([(k - 1) * 2.3, 1.3, 0]))
        spokes = VGroup(*[Line(ivk.get_top(), d.get_bottom(), buff=0.08, stroke_color=MUT, stroke_width=SW_THIN)
                          for d in dks])
        self.pad_to(A("diversified keys") - 0.3)
        self.play(FadeIn(ivk), LaggedStart(*[FadeIn(d, shift=0.1 * UP) for d in dks], lag_ratio=0.2),
                  LaggedStart(*[ShowCreation(s) for s in spokes], lag_ratio=0.2), run_time=1.0)
        self.pad_to(A("share one") - 0.2)
        self.play(Indicate(ivk, color=STAR, scale_factor=1.15), run_time=0.7)
        self.pad_to(A("break one") - 0.3)
        lens = Circle(radius=0.55).set_stroke(FLARE, SW_BOLD).move_to(dks[0])
        self.play(ShowCreation(lens), dks[0].animate.set_color(FLARE), run_time=0.7)
        self.pad_to(A("recovers it") - 0.2)
        self.play(ivk.animate.set_color(FLARE), Flash(ivk.get_center(), color=FLARE), run_time=0.7)
        self.pad_to(A("every incoming") - 0.3)
        notes = VGroup(*[mtex('"note"', size=FS_LABEL, color=FLARE) for _ in range(6)])
        notes.arrange(RIGHT, buff=0.3).move_to(LEFT * 3.4 + DOWN * 2.2)
        pf = VGroup(label("past", size=FS_SMALL, color=MUT).next_to(notes, LEFT, buff=0.25),
                    label("future", size=FS_SMALL, color=MUT).next_to(notes, RIGHT, buff=0.25))
        self.play(LaggedStart(*[FadeIn(n, scale=0.6) for n in notes], lag_ratio=0.12), run_time=0.9)
        self.pad_to(A("past and future") - 0.1)
        self.play(FadeIn(pf), run_time=0.5)
        # ML-KEM: no shared dk
        self.pad_to(A("post quantum") - 0.5)
        mk_t = label("ML-KEM", size=FS_HEAD, color=PAY).move_to(RIGHT * 3.4 + UP * 1.4)
        pairs = VGroup(*[mtex(f'("ek"_{i}, "dk"_{i})', size=FS_BODY, color=TXT) for i in (1, 2, 3)])
        pairs.arrange(DOWN, buff=0.3).next_to(mk_t, DOWN, buff=0.35)
        pq = label("post-quantum", size=FS_LABEL, color=GOLD).next_to(mk_t, RIGHT, buff=0.3)
        self.play(FadeIn(mk_t), FadeIn(pq), LaggedStart(*[FadeIn(p) for p in pairs], lag_ratio=0.2),
                  run_time=1.0)
        self.pad_to(A("sharing one") - 0.3)
        nos = label("no shared decryption key", size=FS_LABEL, color=FLARE).next_to(pairs, DOWN, buff=0.3)
        self.play(FadeIn(nos), run_time=0.6)

        # --- tags -------------------------------------------------------------------------------------
        self.pad_to(A("so discovery") - 0.2)
        self.play(FadeOut(VGroup(title, ivk, dks, spokes, lens, notes, pf, mk_t, pairs, pq, nos)), run_time=0.7)
        ttl = scene_title("Tags")
        self.pad_to(A("thats tags") - 0.3)
        self.play(Write(ttl), run_time=0.6)
        envs = VGroup(memo_env('"tag"_0'), memo_env('"tag"_1'), memo_env('"tag"_2'), memo_env('"tag"_3'))
        envs.scale(1.35).arrange(RIGHT, buff=0.9).move_to(UP * 1.0)
        self.pad_to(A("each encrypted") - 0.2)
        self.play(LaggedStart(*[FadeIn(e, shift=0.2 * UP) for e in envs], lag_ratio=0.15), run_time=1.0)
        self.pad_to(A("first contact") - 0.2)
        f0 = mtex('"tag"_0 = H("ek")', size=FS_BODY, color=STAR).move_to(LEFT * 3.4 + DOWN * 0.9)
        self.play(envs[0][2].animate.set_color(STAR), Indicate(envs[0], color=STAR), FadeIn(f0), run_time=0.9)
        self.pad_to(A("before it knows") - 0.2)
        nb = label("found before the shared secret is known", size=FS_LABEL, color=MUT).next_to(f0, DOWN, buff=0.2)
        self.play(FadeIn(nb), run_time=0.6)
        self.pad_to(A("every later") - 0.2)
        fi = mtex('"tag"_i = H(K, i)', size=FS_BODY, color=PAY).move_to(RIGHT * 3.0 + DOWN * 0.9)
        self.play(FadeIn(fi), *[Indicate(e[2], color=PAY) for e in envs[1:]], run_time=0.9)
        props = VGroup(label("predictable to the two parties", size=FS_LABEL, color=GOLD),
                       label("opaque to everyone else", size=FS_LABEL, color=TXT),
                       label("fresh for every note", size=FS_LABEL, color=TXT))
        props.arrange(DOWN, buff=0.16, aligned_edge=LEFT).next_to(fi, DOWN, buff=0.25)
        for p_, w in zip(props, ["predictable", "opaque", "fresh for every"]):
            self.pad_to(A(w) - 0.2)
            self.play(FadeIn(p_, shift=0.1 * RIGHT), run_time=0.5)

        # --- PIR instead of trial decryption -------------------------------------------------------------
        self.pad_to(A("instead of") - 0.2)
        self.play(FadeOut(VGroup(ttl, envs, f0, nb, fi, props)), run_time=0.6)
        cts = VGroup(*[RoundedRectangle(width=0.5, height=0.36, corner_radius=0.05).set_stroke(MUT, SW_THIN)
                       .set_fill(MUT, 0.08) for _ in range(14)]).arrange(RIGHT, buff=0.12).move_to(UP * 2.0)
        trial = label("trial decryption", size=FS_LABEL, color=MUT).next_to(cts, DOWN, buff=0.25)
        scan = Rectangle(width=0.6, height=0.5).set_stroke(FLARE, SW).move_to(cts[0])
        self.play(FadeIn(cts, lag_ratio=0.05), FadeIn(trial), FadeIn(scan), run_time=0.7)
        self.play(scan.animate.move_to(cts[-1]), run_time=1.0, rate_func=linear)
        strike = Line(trial.get_left(), trial.get_right(), stroke_color=FLARE, stroke_width=SW)
        self.play(ShowCreation(strike), FadeOut(scan), run_time=0.4)
        self.pad_to(A("looks up") - 0.2)
        wal = boxed(label("wallet", size=FS_LABEL, color=GOLD), color=GOLD, pad=0.18).move_to(LEFT * 4.6 + DOWN * 0.8)
        memo_db = db_cylinder("memo DB", PAY).move_to(RIGHT * 0.2 + DOWN * 0.6)
        q_ar = tarrow(wal.get_right(), memo_db.get_left() + DOWN * 0.1, color=GOLD)
        q_l = mtex('"tag"_i', size=FS_LABEL, color=GOLD).next_to(q_ar, UP, buff=0.12)
        self.play(FadeIn(wal), FadeIn(memo_db), run_time=0.6)
        self.pad_to(A("private information") - 0.3)
        self.play(ShowCreation(q_ar), FadeIn(q_l), run_time=0.7)
        pir = label("PIR", size=FS_BODY, color=STAR).next_to(memo_db, UP, buff=0.25)
        self.play(FadeIn(pir), run_time=0.4)
        self.pad_to(A("reveals nothing") - 0.2)
        blind = label("server learns nothing about the query", size=FS_LABEL, color=MUT).next_to(memo_db, RIGHT, buff=0.4)
        self.play(FadeIn(blind), run_time=0.6)
        self.pad_to(A("the same machinery") - 0.2)
        tg_db = db_cylinder("tachygram DB", STAR).move_to(RIGHT * 0.2 + DOWN * 2.35)
        self.play(FadeOut(blind), memo_db.animate.shift(UP * 0.5), pir.animate.shift(UP * 0.5),
                  FadeIn(tg_db, shift=0.2 * UP), run_time=0.8)
        self.pad_to(A("privately supplies") - 0.2)
        sp = step_pill("SpendableInit", GOLD).move_to(RIGHT * 4.6 + DOWN * 1.9)
        feed = tarrow(tg_db.get_right(), sp.get_left(), color=STAR)
        feed_l = label("stamp + anchor data", size=FS_SMALL, color=STAR).next_to(feed, UP, buff=0.1)
        self.play(ShowCreation(feed), FadeIn(feed_l), FadeIn(sp, shift=0.1 * LEFT), run_time=0.9)

        # --- Faerie gold -------------------------------------------------------------------------------------
        self.pad_to(A("gold") - 0.6)
        pir_part = VGroup(cts, trial, strike, wal, memo_db, q_ar, q_l, pir, tg_db, sp, feed, feed_l)
        self.play(FadeOut(pir_part), run_time=0.6)
        fg = scene_title("Faerie gold")
        self.play(Write(fg), run_time=0.7)
        self.pad_to(A("no canonical") - 0.2)
        noc = rich([("no canonical position, so no", TXT), ("$psi$", GOLD), ("binding like Orchard's", TXT),
                    ("$rho$", GOLD)], size=FS_BODY).move_to(UP * 2.1)
        self.play(FadeIn(noc), run_time=0.8)
        n1 = note_card(filled=True).move_to(LEFT * 3.6 + UP * 0.6)
        n2 = note_card(filled=True).move_to(LEFT * 3.6 + DOWN * 1.0)
        for n in (n1, n2):
            n.texts[2].set_color(FLARE)
        self.pad_to(A("checks each") - 0.3)
        self.play(FadeIn(n1, shift=0.2 * RIGHT), FadeIn(n2, shift=0.2 * RIGHT), run_time=0.8)
        nf1 = mtex('"nf"_(e^*)', size=FS_HEAD, color=STAR).move_to(RIGHT * 1.4 + UP * 0.6)
        nf2 = mtex('"nf"_(e^*)', size=FS_HEAD, color=STAR).move_to(RIGHT * 1.4 + DOWN * 1.0)
        ar1 = tarrow(n1.get_right(), nf1.get_left(), color=MUT)
        ar2 = tarrow(n2.get_right(), nf2.get_left(), color=MUT)
        self.pad_to(A("reference epoch") - 0.4)
        ref = label("at a fixed reference epoch", size=FS_LABEL, color=MUT).move_to(RIGHT * 1.4 + DOWN * 2.3)
        self.play(ShowCreation(ar1), ShowCreation(ar2), FadeIn(nf1), FadeIn(nf2), FadeIn(ref), run_time=0.9)
        self.pad_to(A("reused") - 0.2)
        self.play(Indicate(n1.texts[2], color=FLARE, scale_factor=1.4),
                  Indicate(n2.texts[2], color=FLARE, scale_factor=1.4), run_time=0.7)
        self.pad_to(A("collides") - 0.2)
        eqc = mtex("=", size=FS_HEAD, color=FLARE).move_to((nf1.get_center() + nf2.get_center()) / 2)
        keep = label("collision: keep one", size=FS_BODY, color=FLARE).next_to(eqc, RIGHT, buff=0.8)
        self.play(FadeIn(eqc, scale=1.5), Flash(eqc.get_center(), color=FLARE), FadeIn(keep), run_time=0.8)
        self.pad_to(scene_T(SID))

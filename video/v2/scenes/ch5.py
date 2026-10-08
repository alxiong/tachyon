"""Chapter 5 — The proof tree: spending our notes (scenes 5.1, 5.2, 5.3)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style import *  # noqa: E402,F403
from style import _lint_flush  # noqa: E402


# ---- local helpers -------------------------------------------------------------------

def hdr(name, fields, color=WALLET, size=FS_SMALL):
    """Header with individually addressable fields: g.fields[i] (for bridging pins)."""
    parts = [(f'$mono("{name}")$', color), ("$\\{$", color)]
    for i, f in enumerate(fields):
        sep = "," if i < len(fields) - 1 else ""
        parts.append((f"${f}{sep}$", color))
    parts.append(("$\\}$", color))
    r = rich(parts, size=size, buff=0.07)
    box = Rectangle(width=r.get_width() + 0.36, height=r.get_height() + 0.3)
    box.set_fill(color, 0.08).set_stroke(color, SW_THIN, 0.9).move_to(r)
    g = VGroup(box, r)
    g.box, g.text = box, r
    g.fields = VGroup(*r[2:2 + len(fields)])
    return g


def up_arrow(a, b, color=MUT):
    """Edge from child (a) up to parent (b): child top -> parent bottom."""
    return tarrow(a.get_top(), b.get_bottom(), color=color, width=SW_THIN, buff=0.08)


def pin(f1, f2, color=STAR, depth=0.55):
    """Bridging pin: a bowed arc under two equal fields, with '=' at its lowest point."""
    p1 = f1.get_bottom() + DOWN * 0.08
    p2 = f2.get_bottom() + DOWN * 0.08
    arc = ArcBetweenPoints(p1, p2, angle=PI / 3)
    arc.set_stroke(color, SW, 0.95)
    mid = arc.point_from_proportion(0.5)
    eq = mtex("=", size=FS_LABEL, color=color)
    disc = Circle(radius=0.2).set_fill(VOID, 1).set_stroke(color, SW_THIN).move_to(mid)
    eq.move_to(disc)
    return VGroup(arc, disc, eq)


def word_end(sid, phrase, occ=1):
    """End time of `phrase` (its last word) in the final clip: where a ⟨pause⟩ silence begins."""
    import re as _r
    t0 = anchor(sid, phrase, occ)
    last = _r.sub(r"[^a-z0-9]", "", _r.split(r"[\s\-]+", phrase.split("|")[0].strip())[-1].lower())
    for x in WORDS[sid]:
        if x["s"] >= t0 - 1e-6 and _r.sub(r"[^a-z0-9]", "", x["w"].lower()).endswith(last):
            return x["e"]
    raise ValueError(f"word_end: {phrase!r} not found in {sid}")


def flow_dot(path_mob, color=STAR):
    d = Dot(radius=0.07).set_fill(color, 1)
    d.move_to(path_mob.get_start())
    return d


def hw_wallet(color=GOLD):
    body = RoundedRectangle(width=1.0, height=1.5, corner_radius=0.14)
    body.set_fill(color, 0.06).set_stroke(color, SW_THIN, 0.9)
    screen = RoundedRectangle(width=0.7, height=0.5, corner_radius=0.06).set_stroke(color, 1.6, 0.8)
    screen.move_to(body.get_top() + DOWN * 0.42)
    btns = VGroup(*[Dot(radius=0.07).set_fill(color, 0.8) for _ in range(2)]).arrange(RIGHT, buff=0.25)
    btns.move_to(body.get_bottom() + UP * 0.35)
    lab = label("hardware wallet", size=FS_SMALL, color=color).next_to(body, DOWN, buff=0.12)
    return VGroup(body, screen, btns, lab)


class FrameLintScene(TimedScene):
    """TimedScene whose layout lint sees what the CAMERA sees: when self.frame has moved or
    zoomed (5.2 climbs the tree), world-space mobjects are mapped into frame space for the
    lint pass only (frame-fixed ones, like the rail, already are), then mapped back."""

    def _lint_in_frame_space(self):
        fr = self.frame
        c, k = fr.get_center().copy(), fr.get_height() / FRAME_HEIGHT
        moved = [m for m in self.mobjects if m is not fr and not m.is_fixed_in_frame()]
        warp = np.linalg.norm(c) > 1e-3 or abs(k - 1) > 1e-3
        if warp:
            for m in moved:
                m.shift(-c).scale(1 / k, about_point=ORIGIN)
        lint_layout(self)
        if warp:
            for m in moved:
                m.scale(k, about_point=ORIGIN).shift(c)

    def pad_to(self, t: float):
        if os.environ.get("LAYOUT_LINT", "1") != "0":
            self._lint_in_frame_space()
            if self.time > t + 0.25:
                self._lint = getattr(self, "_lint", {})
                self._lint[("late", round(t, 2))] = (
                    f"[t={self.time:6.1f}] late     beat anchored at {t:.2f}s starts "
                    f"{self.time - t:.2f}s late (trim run_times before it)")
        if t > self.time:
            self.wait(t - self.time)

    def tear_down(self):
        if os.environ.get("LAYOUT_LINT", "1") != "0":
            self._lint_in_frame_space()
            _lint_flush(self)
        Scene.tear_down(self)


# ======================================================================================
class Scene51(FrameLintScene):
    def construct(self):
        SID = "5.1"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731

        self.wait(0.4)
        title = scene_title("What does the actual proof look like?")

        # --- three monolithic statements --------------------------------------------------
        def card(name, items, color):
            head = label(name, size=FS_HEAD, color=color)
            rows = bullets(items, size=FS_LABEL, color=TXT, mark_color=color, buff=0.24)
            inner = VGroup(head, rows).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
            return boxed(inner, color=color, pad=0.3, fill=0.04)

        spend = card("Spend statement", ["note integrity", "spend authority", "inclusion",
                                         "past exclusion", "spend-time nullifiers"], GOLD)
        output = card("Output statement", ["value commitment", "value range", "note commitment",
                                           "dummy tachygram", "authorization"], GOLD)
        bundle = card("Bundle statement", ["per-action validity", "action multiset",
                                           "tachygram association", "accumulator integrity"], STAR)
        cards = VGroup(spend, output, bundle).arrange(RIGHT, buff=0.4, aligned_edge=UP)
        fit_in(cards, (-6.7, 6.7, -2.9, 2.5), max_scale=1.5)
        self.pad_to(A("a spend has") - 0.45)
        self.play(FadeIn(title), FadeIn(spend, shift=0.2 * UP), run_time=0.8)
        self.pad_to(A("so does an output") - 0.1)
        self.play(FadeIn(output, shift=0.2 * UP), run_time=0.7)
        self.pad_to(A("so does the bundle") - 0.1)
        self.play(FadeIn(bundle, shift=0.2 * UP), run_time=0.7)
        self.pad_to(A("in one piece") - 0.3)
        self.play(*[Indicate(c[0], color=FLARE, scale_factor=1.03) for c in cards], run_time=0.8)

        # --- break them into steps ------------------------------------------------------------
        self.pad_to(A("into steps") - 0.3)
        groups = []
        for c, names, col in ((spend, ["SpendableInit", "SpendBind"], GOLD),
                              (output, ["OutputSeed"], GOLD),
                              (bundle, ["StampMerge", "StampLift"], STAR)):
            ps = VGroup(*[step_pill(n, color=col) for n in names]).arrange(UP, buff=0.5)
            ps.move_to(c)
            groups.append(ps)
        # shatter: each card breaks apart and its steps take its place (no glyph-scribble morph)
        shards = []
        for c in cards:
            for k, piece in enumerate(c.family_members_with_points()):
                ang = (k * 2.399) % TAU
                shards.append(FadeOut(piece, shift=0.45 * np.array([np.cos(ang), np.sin(ang), 0])))
        self.play(LaggedStart(AnimationGroup(*shards),
                              LaggedStart(*[FadeIn(g, scale=1.25) for g in groups], lag_ratio=0.15),
                              lag_ratio=0.35), run_time=0.9)
        self.remove(*cards)

        # ⟨pause: statement cards shatter into a tree of steps⟩ — the pills settle into the tree
        self.pad_to(word_end(SID, "into steps") - 0.05)
        (p_init, p_bind), (p_out,), (p_merge, p_lift) = groups
        tree_pos = {p_init: [-3.2, -2.3, 0], p_bind: [-3.2, -0.75, 0], p_out: [3.2, -0.75, 0],
                    p_merge: [0, 0.75, 0], p_lift: [0, 2.15, 0]}
        tgt = {p: p.copy().move_to(pos) for p, pos in tree_pos.items()}
        t_edges = VGroup(up_arrow(tgt[p_init], tgt[p_bind]), up_arrow(tgt[p_bind], tgt[p_merge]),
                         up_arrow(tgt[p_out], tgt[p_merge]), up_arrow(tgt[p_merge], tgt[p_lift]))
        self.play(*[p.animate.move_to(pos) for p, pos in tree_pos.items()], run_time=0.6)
        self.play(LaggedStart(*[ShowCreation(e) for e in t_edges], lag_ratio=0.25), run_time=0.45)

        # --- one generic step --------------------------------------------------------------------
        self.pad_to(A("a step is") - 0.15)
        step = RoundedRectangle(width=3.6, height=1.0, corner_radius=0.5)
        step.set_fill(STAR, 0.06).set_stroke(STAR, SW, 0.95).move_to(DOWN * 0.15)
        step_t = label("step: a bounded circuit", size=FS_LABEL, color=STAR).move_to(step)
        tree_all = VGroup(*groups, t_edges)
        self.play(LaggedStart(AnimationGroup(FadeOut(title),
                                             tree_all.animate.scale(0.25).move_to(step).set_opacity(0)),
                              FadeIn(VGroup(step, step_t), scale=0.8), lag_ratio=0.5), run_time=0.8)
        self.remove(tree_all)

        self.pad_to(A("two child proofs") - 0.3)
        kids = VGroup()
        kid_arrows = VGroup()
        for sx in (-1, 1):
            tok = proof_token(0.2).move_to(np.array([3.0 * sx, -2.35, 0]))
            hl = label("header", size=FS_SMALL, color=MUT).next_to(tok, RIGHT, buff=0.2)
            kids.add(VGroup(tok, hl))
            kid_arrows.add(tarrow(tok.get_top() + UP * 0.05,
                                  step.get_bottom() + RIGHT * 0.8 * sx, color=MUT))
        self.play(LaggedStart(*[FadeIn(k, shift=0.2 * UP) for k in kids], lag_ratio=0.3),
                  LaggedStart(*[GrowArrow(a) if False else ShowCreation(a) for a in kid_arrows],
                              lag_ratio=0.3), run_time=1.0)
        self.pad_to(A("private witness") - 0.3)
        wit = boxed(label("private witness", size=FS_SMALL, color=TXT), color=MUT, pad=0.14)
        wit.move_to(LEFT * 5.0 + DOWN * 0.15)
        wit_arrow = tarrow(wit.get_right(), step.get_left(), color=MUT)
        self.play(FadeIn(wit, shift=0.2 * RIGHT), ShowCreation(wit_arrow), run_time=0.7)
        self.pad_to(A("checks part") - 0.2)
        ck = checkmark(0.35, color=GOLD).next_to(step, RIGHT, buff=0.3)
        part = label("checks part of the statement", size=FS_SMALL, color=GOLD).next_to(ck, RIGHT, buff=0.2)
        self.play(ShowCreation(ck), FadeIn(part), run_time=0.7)
        self.pad_to(A("emits a new proof") - 0.2)
        out_tok = proof_token(0.24).move_to(UP * 1.55)
        out_arrow = tarrow(step.get_top(), out_tok.get_bottom() + DOWN * 0.08, color=MUT)
        self.play(ShowCreation(out_arrow), FadeIn(out_tok, scale=0.5), run_time=0.7)
        self.pad_to(A("is a header") - 0.2)
        out_hdr = boxed(label("header: the public output", size=FS_LABEL, color=STAR),
                        color=STAR, pad=0.16).next_to(out_tok, RIGHT, buff=0.3)
        self.play(FadeIn(out_hdr, shift=0.1 * LEFT), run_time=0.6)
        self.pad_to(A("the data in") - 0.1)
        data = label("the data in proof-carrying data", size=FS_SMALL, color=MUT)
        data.next_to(out_hdr, UP, buff=0.18)
        self.play(FadeIn(data), run_time=0.6)
        self.pad_to(A("headers flow") - 0.1)
        paths = list(kid_arrows) + [out_arrow]
        dots = [Dot(p[0].get_start(), radius=0.08).set_fill(STAR, 1) for p in paths]
        self.play(*[MoveAlongPath(d, p[0]) for d, p in zip(dots[:2], paths[:2])], run_time=0.8)
        self.play(FadeOut(VGroup(*dots[:2])), MoveAlongPath(dots[2], out_arrow[0]), run_time=0.7)
        self.play(FadeOut(dots[2]), Flash(out_tok.get_center(), color=STAR), run_time=0.5)

        # --- bridging -------------------------------------------------------------------------------
        self.pad_to(A("a parent bridges") - 0.9)
        generic = VGroup(step, step_t, kids, kid_arrows, wit, wit_arrow, ck, part, out_tok,
                         out_arrow, out_hdr, data)
        self.play(FadeOut(generic), run_time=0.5)
        left = hdr("NoteSpendable", ['"cm"', "6", '"sntl"_6'], GOLD, size=FS_LABEL)
        right = hdr("NoteUnspent", ['"cm"', "6", "9", '"sntl"_6', '"sntl"_9'], GOLD, size=FS_LABEL)
        VGroup(left, right).arrange(RIGHT, buff=0.7).move_to(DOWN * 0.6)
        parent = step_pill("SpendableLift", GOLD).move_to(UP * 1.7)
        e1 = up_arrow(left, parent)
        e2 = up_arrow(right, parent)
        self.play(FadeIn(left, shift=0.2 * UP), FadeIn(right, shift=0.2 * UP), run_time=0.7)
        self.pad_to(A("bridges") - 0.2)
        self.play(FadeIn(parent), ShowCreation(e1), ShowCreation(e2), run_time=0.6)
        self.pad_to(A("loads both") - 0.2)
        self.play(Indicate(left.box, color=STAR, scale_factor=1.04),
                  Indicate(right.box, color=STAR, scale_factor=1.04), run_time=0.8)
        eqs = VGroup()
        marks = VGroup()

        def bridge(i, j, a, b, word):
            self.pad_to(A(word) - 0.3)
            def ul(f):
                w = f.get_width() * (0.75 if f is not right.fields[-1] and f is not left.fields[-1] else 0.95)
                c = f.get_bottom() + DOWN * 0.07 + LEFT * (f.get_width() - w) / 2
                return Line(c + LEFT * w / 2, c + RIGHT * w / 2, stroke_color=STAR, stroke_width=SW_BOLD)
            r1, r2 = ul(left.fields[i]), ul(right.fields[j])
            row = VGroup(mtex(a, size=FS_BODY, color=STAR), mtex("=", size=FS_BODY, color=STAR),
                         mtex(b, size=FS_BODY, color=STAR), checkmark(0.3, GOLD)).arrange(RIGHT, buff=0.2)
            eqs.add(row)
            eqs.arrange(RIGHT, buff=0.9).move_to(DOWN * 2.2)
            marks.add(r1, r2)
            self.play(ShowCreation(r1), ShowCreation(r2), FadeIn(row, shift=0.1 * UP),
                      *[r.animate.move_to(r.get_center()) for r in eqs[:-1]], run_time=0.7)

        bridge(0, 0, '"cm"', '"cm"', "same note commitment")
        bridge(2, 3, '"sntl"_6', '"sntl"_6', "matching sentinels")
        bridge(1, 1, "6", "6", "the same epoch")
        p_cm, p_s, p_e = eqs, marks, VGroup()
        self.pad_to(A("sound exactly") - 0.3)
        cap = rich([("sound", STAR), ("$<==>$", STAR), ("every shared field bridged", STAR)], size=FS_BODY)
        cap = boxed(cap, color=STAR, pad=0.16).move_to([0, CAPTION_Y, 0])
        self.play(FadeIn(cap, shift=0.1 * UP), run_time=0.8)
        self.pad_to(A("gets bridged") - 0.1)
        self.play(*[Flash(m.get_center(), color=STAR, flash_radius=0.25, line_length=0.12) for m in marks],
                  run_time=0.7)

        # --- three colors --------------------------------------------------------------------------
        self.pad_to(A("three colors") - 0.4)
        self.play(FadeOut(VGroup(left, right, parent, e1, e2, p_cm, p_s, p_e, cap)), run_time=0.6)
        legend_title = scene_title("Three roles")
        self.play(FadeIn(legend_title), run_time=0.5)
        rows = VGroup()
        specs = [(step_pill("wallet step", GOLD), "runs on the wallet, sees the note", GOLD),
                 (step_pill("service step", CYAN), "runs on a service, sees only opaque values", CYAN),
                 (boxed(label("shared evidence", size=FS_LABEL, color=STAR), color=STAR, pad=0.16),
                  "anyone can use it", STAR)]
        for icon, text, col in specs:
            t = label(text, size=FS_BODY, color=TXT)
            rows.add(VGroup(icon, t))
        for r in rows:
            r[1].next_to(r[0], RIGHT, buff=0.5)
        rows.arrange(DOWN, buff=0.55, aligned_edge=LEFT).move_to(UP * 0.4)
        for r in rows:
            r[1].shift(RIGHT * (rows.get_left()[0] + 3.4 - r[1].get_left()[0]))
        self.pad_to(A("gold steps") - 0.2)
        self.play(FadeIn(rows[0], shift=0.2 * RIGHT), run_time=0.7)
        self.pad_to(A("cyan steps") - 0.2)
        self.play(FadeIn(rows[1], shift=0.2 * RIGHT), run_time=0.7)
        self.pad_to(A("white is") - 0.2)
        self.play(FadeIn(rows[2], shift=0.2 * RIGHT), run_time=0.7)
        self.pad_to(A("anchor chain segments") - 0.2)
        ac = header_box("AnchorChain", '"anchor"_L, "anchor"_R', color=STAR, size=FS_LABEL)
        ac_t = label("active epoch", size=FS_SMALL, color=MUT)
        et = header_box("EvidenceTree", 'e, "root"', color=STAR, size=FS_LABEL)
        et_t = label("closed epochs", size=FS_SMALL, color=MUT)
        g1 = VGroup(ac, ac_t).arrange(DOWN, buff=0.15)
        g2 = VGroup(et, et_t).arrange(DOWN, buff=0.15)
        VGroup(g1, g2).arrange(RIGHT, buff=1.2).move_to(DOWN * 2.3)
        self.play(FadeIn(g1, shift=0.2 * UP), run_time=0.7)
        self.pad_to(A("evidence trees") - 0.2)
        self.play(FadeIn(g2, shift=0.2 * UP), run_time=0.7)
        self.pad_to(scene_T(SID))


# ======================================================================================
class Scene52(FrameLintScene):
    def construct(self):
        SID = "5.2"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731

        rail = EpochRail(first=4, last=10)
        self.add(rail)
        self.wait(0.4)

        # --- now = 9, a second note ----------------------------------------------------------
        self.pad_to(A("simplest spend") - 0.4)
        title = scene_title("Same-epoch spend")
        self.play(Write(title), run_time=0.9)
        self.pad_to(A("now epoch") - 0.2)
        now_x = rail.center_of(9)[0] + 0.4
        now = DashedLine([now_x, rail.y, 0], [now_x, rail.y + 1.3, 0], dash_length=0.07)
        now.set_stroke(STAR, SW, 0.9)
        now_l = label("now", size=FS_SMALL, color=STAR).next_to(now, UP, buff=0.1)
        self.play(FadeIn(now, shift=0.2 * DOWN), FadeIn(now_l), Indicate(rail.label_of(9), color=STAR),
                  run_time=0.8)
        self.pad_to(A("another note") - 0.3)
        b9_pos = rail.center_of(9) + LEFT * 0.6
        b9 = bead(GOLD, r=0.11).move_to(b9_pos)
        n9 = mtex('"note"_9', size=FS_LABEL, color=GOLD).move_to(b9_pos + UP * 1.0)
        self.play(FadeIn(n9, shift=0.2 * DOWN), run_time=0.7)
        self.play(GrowFromCenter(b9), Flash(b9_pos, color=GOLD, flash_radius=0.3),
                  n9.animate.move_to(b9_pos + UP * 0.62), run_time=0.8)
        self.pad_to(A("any exclusion") - 0.2)
        span = Line(rail.gate(9).get_center(), b9_pos, stroke_color=MUT, stroke_width=SW_BOLD)
        nothing = label("nothing to exclude", size=FS_LABEL, color=MUT)
        nothing.next_to(rail.center_of(8, dy=0.0), UP, buff=0.75)
        nothing_arrow = tarrow(nothing.get_bottom(), span.get_center() + UP * 0.12, color=MUT)
        self.play(ShowCreation(span), run_time=0.6)
        self.pad_to(A("nothing to exclude") - 0.3)
        self.play(FadeIn(nothing), ShowCreation(nothing_arrow), run_time=0.7)

        # --- SpendableInit ----------------------------------------------------------------------
        X_L, X_R = -3.3, 3.3
        Y0, Y1, Y2, Y3 = -2.0, 0.1, 2.2, 4.3
        HD = 0.95
        frame = self.frame
        for m in (rail, b9, n9, now, now_l):
            m.fix_in_frame()
        self.pad_to(A("the first step") - 0.2)
        self.play(FadeOut(VGroup(title, nothing, nothing_arrow, span, n9)), run_time=0.5)
        s_init = step_pill("SpendableInit", GOLD).move_to([X_L, Y0, 0])
        self.pad_to(A("spendableinit") - 0.3)
        self.play(FadeIn(s_init, scale=0.8), run_time=0.6)
        notes = VGroup(
            rich([("witness:", MUT), ("the creation stamp's data", TXT)], size=FS_LABEL),
            rich([("proves", MUT), ('$f^"tg" ("cm") = 0$', GOLD)], size=FS_LABEL),
            rich([("computes", MUT), ("the anchor it produced", TXT)], size=FS_LABEL),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([3.0, -0.2, 0])
        self.pad_to(A("takes the creation") - 0.2)
        self.play(FadeIn(notes[0], shift=0.1 * LEFT), run_time=0.6)
        self.pad_to(A("proves that") - 0.2)
        self.play(FadeIn(notes[1], shift=0.1 * LEFT), run_time=0.6)
        self.pad_to(A("computes") - 0.2)
        self.play(FadeIn(notes[2], shift=0.1 * LEFT), run_time=0.6)
        self.pad_to(A("outcomes|out comes") - 0.2)
        h_sp = hdr("NoteSpendable", ['"cm"', "9", '"anchor"'], GOLD, size=FS_LABEL).move_to([X_L, Y0 + HD, 0])
        a0 = up_arrow(s_init, h_sp)
        self.play(ShowCreation(a0), FadeIn(h_sp, shift=0.15 * UP), run_time=0.8)
        self.pad_to(A("its commitment") - 0.1)
        for f, w in ((0, "its commitment"), (1, "its epic|its epoch"), (2, "that anchor")):
            if f:
                self.pad_to(A(w) - 0.1)
            self.play(Indicate(h_sp.fields[f], color=STAR, scale_factor=1.25), run_time=0.5)
        self.pad_to(A("cache it") - 0.2)
        self.play(FadeOut(notes), run_time=0.4)
        hw = hw_wallet().move_to([2.0, -0.75, 0])
        cached = rich([("cached", GOLD)], size=FS_LABEL).next_to(h_sp, RIGHT, buff=0.3)
        self.play(FadeIn(cached), run_time=0.5)
        self.pad_to(A("hardware wallet") - 0.3)
        cp_box, cp_txt = h_sp.box.copy(), h_sp.text.copy()
        cp = VGroup(cp_box, cp_txt)
        # the miniature in the device screen is an icon, not text to read: its glyphs dim as they shrink
        self.play(FadeIn(hw, shift=0.2 * LEFT), run_time=0.5)
        k_hw = 0.62 / h_sp.get_width()
        self.play(cp_box.animate.scale(k_hw).move_to(hw[1]),
                  cp_txt.animate.scale(k_hw).move_to(hw[1]).set_opacity(0.4), run_time=0.8)

        # --- SpendBind -----------------------------------------------------------------------------
        self.pad_to(A("then spendbind") - 0.45)
        self.play(FadeOut(VGroup(hw, cp, cached)), run_time=0.4)
        s_bind = step_pill("SpendBind", GOLD).move_to([X_L, Y1, 0])
        a1 = up_arrow(h_sp, s_bind)
        self.play(ShowCreation(a1), FadeIn(s_bind, scale=0.8), run_time=0.6)
        checks = bullets([
            mtex('"pk" = "Com"("ak", "nk")', size=FS_LABEL, color=TXT),
            mtex('"cm" = "Com"("pk", v, psi; "rcm")', size=FS_LABEL, color=TXT),
            mtex('0 <= v <= v_"max"', size=FS_LABEL, color=TXT),
            mtex('"rk" = "ak" + [alpha] G', size=FS_LABEL, color=TXT),
            mtex('"nf"_9, "nf"_10', size=FS_LABEL, color=FLARE),
        ], size=FS_LABEL, buff=0.26).move_to([3.1, -0.2, 0])
        for i, w in enumerate(["payment key", "recomputes", "value is", "binds", "derives the two"]):
            self.pad_to(A(w) - 0.25)
            self.play(FadeIn(checks[i], shift=0.1 * LEFT), run_time=0.5)
        self.pad_to(A("a stamp for") - 0.2)
        h_st = hdr("Stamp", ['"acc"^"act"', '"acc"^"tg"', '"anchor"'], GOLD, size=FS_LABEL).move_to([X_L, Y1 + HD, 0])
        a2 = up_arrow(s_bind, h_st)
        self.play(ShowCreation(a2), FadeIn(h_st, shift=0.15 * UP), run_time=0.7)

        # --- OutputSeed, StampMerge ---------------------------------------------------------------
        self.pad_to(A("an output gets") - 0.3)
        self.play(FadeOut(checks), run_time=0.4)
        s_out = step_pill("OutputSeed", GOLD).move_to([X_R, Y1, 0])
        h_out = hdr("Stamp", ['"acc"^"act"', '"acc"^"tg"', '"anchor"'], GOLD, size=FS_LABEL).move_to([X_R, Y1 + HD, 0])
        a3 = up_arrow(s_out, h_out)
        self.pad_to(A("outputseed") - 0.3)
        self.play(FadeIn(s_out, scale=0.8), run_time=0.5)
        self.play(ShowCreation(a3), FadeIn(h_out, shift=0.15 * UP), run_time=0.6)
        self.pad_to(A("stampmerge") - 0.35)
        s_merge = step_pill("StampMerge", GOLD).move_to([0, Y2, 0])
        self.play(frame.animate.move_to(UP * 0.7), s_init.animate.fade(0.5), run_time=0.5)
        a4, a5 = up_arrow(h_st, s_merge), up_arrow(h_out, s_merge)
        self.play(ShowCreation(a4), ShowCreation(a5), FadeIn(s_merge, scale=0.8), run_time=0.7)
        self.pad_to(A("multiplying") - 0.2)
        mul = mtex('f_1 (X) dot f_2 (X)', size=FS_LABEL, color=GOLD).next_to(s_merge, RIGHT, buff=0.4)
        mul.shift(UP * 0.55)
        uni = label("union is multiplication", size=FS_LABEL, color=MUT).next_to(mul, UP, buff=0.15)
        self.play(FadeIn(mul, shift=0.1 * LEFT), FadeIn(uni), run_time=0.6)

        # --- StampLift -------------------------------------------------------------------------------
        self.pad_to(A("the last step") - 0.25)
        h_m = hdr("Stamp", ['"acc"^"act"', '"acc"^"tg"', '"anchor"'], GOLD, size=FS_LABEL)
        h_m.move_to([0, Y2 + HD, 0])
        a6 = up_arrow(s_merge, h_m)
        self.play(FadeOut(VGroup(mul, uni)), ShowCreation(a6), FadeIn(h_m, shift=0.15 * UP), run_time=0.6)
        lower = VGroup(s_init, h_sp, a0, s_bind, a1, h_st, a2, s_out, h_out, a3, a4, a5, s_merge)
        lower_saved = lower.copy()
        self.play(FadeOut(lower), frame.animate.move_to(UP * 2.8), run_time=0.7)
        s_lift = step_pill("StampLift", GOLD).move_to([0, Y3, 0])
        self.pad_to(A("stamplift") - 0.15)
        a7 = up_arrow(h_m, s_lift)
        self.play(ShowCreation(a7), FadeIn(s_lift, scale=0.8), run_time=0.5)
        self.pad_to(A("shared anchor") - 0.3)
        ach = hdr("AnchorChain", ['"anchor"', '"anchor"^prime'], STAR, size=FS_LABEL)
        ach.move_to([4.4, Y3, 0])
        a8 = tarrow(ach.get_left(), s_lift.get_right(), color=STAR, width=SW_THIN)
        self.play(FadeIn(ach, shift=0.2 * LEFT), ShowCreation(a8), run_time=0.7)
        self.pad_to(A("later anchor") - 0.6)
        h_f = hdr("Stamp", ['"acc"^"act"', '"acc"^"tg"', '"anchor"^prime'], GOLD, size=FS_LABEL)
        h_f.move_to([0, Y3 + HD, 0])
        a9 = up_arrow(s_lift, h_f)
        sq = Triangle().scale(0.13).rotate(PI).set_fill(STAR, 1).set_stroke(width=0)
        sq.move_to(b9_pos + UP * 0.3)
        sq_l = label("anchor", size=FS_SMALL, color=STAR).next_to(sq, UP, buff=0.1)
        mk = VGroup(sq, sq_l).fix_in_frame()
        self.play(ShowCreation(a9), FadeIn(h_f, shift=0.15 * UP), FadeIn(mk), run_time=0.6)
        lifted_x = rail.center_of(9)[0] - 0.3           # stays left of "now" (center + 0.4); label clears the line
        self.play(mk.animate.shift(RIGHT * (lifted_x - sq.get_x())), run_time=0.8)
        self.pad_to(A("contains no") - 0.1)
        self.play(Indicate(ach, color=STAR, scale_factor=1.05), run_time=0.6)
        self.pad_to(A("never cross") - 0.6)
        g10 = rail.gate(10)
        # the lift is bounded by "now" (no chain exists beyond it) and never reaches the sentinel
        seg = Line(np.array([b9_pos[0], rail.y + 0.12, 0]), np.array([now.get_x(), rail.y + 0.12, 0]),
                   stroke_color=STAR, stroke_width=SW_BOLD).fix_in_frame()
        self.play(ShowCreation(seg), run_time=0.5)
        self.play(Flash(g10.get_top(), color=FLARE, flash_radius=0.3),
                  g10.animate.set_stroke(FLARE, SW_BOLD), run_time=0.6)
        self.play(g10.animate.set_stroke(STAR, SW), FadeOut(seg), run_time=0.3)
        self.pad_to(A("without it") - 0.2)
        ghost = sq.copy().set_fill(FLARE, 0.9).move_to(b9_pos + UP * 0.3).fix_in_frame()
        link = DashedLine(ghost.get_center(), b9.get_center(), dash_length=0.06).set_stroke(FLARE, SW)
        link.fix_in_frame()
        why = label("anchor points at the creation", size=FS_LABEL, color=FLARE)
        why.next_to(rail.center_of(7, dy=0.9), UP, buff=0).fix_in_frame()
        self.play(FadeIn(ghost), ShowCreation(link), FadeIn(why), run_time=0.8)
        self.pad_to(A("lifting is") - 0.2)
        why2 = label("lifted: unlinkable", size=FS_LABEL, color=GOLD).move_to(why).fix_in_frame()
        self.play(FadeOut(VGroup(ghost, link)), ReplacementTransform(why, why2),
                  Flash(sq.get_center(), color=GOLD, flash_radius=0.3), run_time=0.9)

        # ⟨pause: the full base tree, checklist complete⟩
        self.pad_to(word_end(SID, "unlinkable") - 0.05)
        s_init, s_bind, s_out, s_merge = lower_saved[0], lower_saved[3], lower_saved[7], lower_saved[12]
        h_sp = lower_saved[1]
        clauses = [("inclusion", s_init), ("note integrity, spend authority", s_bind),
                   ("spend-time nullifiers", s_bind), ("past exclusion: none needed", None),
                   ("output statement", s_out)]
        cl_rows = VGroup()
        for text, m in clauses:
            box_ = Square(0.3).set_stroke(MUT, SW_THIN).set_fill(opacity=0)
            cl_rows.add(VGroup(box_, label(text, size=FS_LABEL, color=TXT if m is not None else MUT))
                        .arrange(RIGHT, buff=0.22))
        cl_rows.arrange(DOWN, buff=0.24, aligned_edge=LEFT).move_to([-4.6, 4.05, 0])
        ticks = VGroup(*[checkmark(0.3, GOLD).move_to(r[0]) for r in cl_rows])
        self.play(FadeOut(VGroup(why2, rail, mk, b9, now, now_l)),
                  FadeIn(lower_saved), FadeIn(cl_rows),
                  frame.animate.move_to(UP * 1.62).set_height(FRAME_HEIGHT * 1.06), run_time=0.8)
        # one Indicate per step (two overlapping Indicates on SpendBind would leave it stuck lit)
        firsts = [m if m is not None and all(m is not c[1] for c in clauses[:i]) else None
                  for i, (_, m) in enumerate(clauses)]
        self.play(LaggedStart(*[AnimationGroup(ShowCreation(t), *([Indicate(m, color=STAR, scale_factor=1.08)]
                                                                 if m is not None else []))
                                for t, m in zip(ticks, firsts)], lag_ratio=0.3), run_time=1.0)

        # --- every spend ends this way ---------------------------------------------------------------
        for m, t in ((s_bind, A("spendbind merge")), (s_merge, A("merge and lift")),
                     (s_lift, A("and lift") + 0.15)):
            self.pad_to(t - 0.15)
            self.play(Indicate(m, color=STAR, scale_factor=1.12), run_time=0.45)
        self.pad_to(A("an older note") - 0.1)
        older = mtex('"note"_5', size=FS_BODY, color=GOLD).next_to(h_sp, LEFT, buff=0.45)
        self.play(FadeIn(older, shift=0.2 * RIGHT), run_time=0.7)
        self.pad_to(A("what feeds") - 0.2)
        box_q = SurroundingRectangle(h_sp, buff=0.1).set_stroke(FLARE, SW)
        o_arrow = tarrow(older.get_right(), box_q.get_left(), color=GOLD)
        self.play(ShowCreation(box_q), ShowCreation(o_arrow), run_time=0.7)
        self.pad_to(scene_T(SID))


def evidence_tree_glyph(color=STAR, w=3.0, h=1.3):
    """Small quaternary Merkle tree: root, 4 nodes, 16 leaves. Returns (group, leaves, root)."""
    root = Dot(UP * h / 2, radius=0.08).set_fill(color, 1)
    mids = VGroup(*[Dot([(-w / 2) + (i + 0.5) * w / 4, 0, 0], radius=0.06).set_fill(color, 0.9)
                    for i in range(4)])
    leaves = VGroup(*[Dot([(-w / 2) + (i + 0.5) * w / 16, -h / 2, 0], radius=0.045).set_fill(color, 0.8)
                      for i in range(16)])
    edges = VGroup(*[Line(root.get_center(), m.get_center(), stroke_width=1.6, stroke_color=MUT)
                     for m in mids])
    edges.add(*[Line(mids[i // 4].get_center(), l.get_center(), stroke_width=1.2, stroke_color=MUT)
                for i, l in enumerate(leaves)])
    g = VGroup(edges, root, mids, leaves)
    return g, leaves, root


def tile(lbl, color):
    return factor_tile("", color=color, w=0.62, h=0.62).add(
        mtex(lbl, size=FS_SMALL, color=color))


def tile_row(idxs, color):
    ts = VGroup()
    for i in idxs:
        t = factor_tile("", color=color, w=0.62, h=0.62)
        t.add(mtex(f"F_{i}", size=FS_SMALL, color=color).move_to(t[0]))
        ts.add(t)
    ts.arrange(RIGHT, buff=0.06)
    return ts


class Scene53(FrameLintScene):
    def construct(self):
        SID = "5.3"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731

        rail = EpochRail(first=4, last=10)
        b5 = bead(GOLD, r=0.11).move_to(rail.center_of(5))
        n5 = mtex('"note"_5', size=FS_LABEL, color=GOLD).next_to(b5, UP, buff=0.3)
        self.add(rail, b5)
        self.wait(0.4)

        # --- three parts ------------------------------------------------------------------------
        self.pad_to(A("our original note") - 0.2)
        self.play(FadeIn(n5, shift=0.15 * DOWN), Flash(b5.get_center(), color=GOLD), run_time=0.9)
        y_br = rail.y + 0.32

        def seg_bracket(e0, e1, color, text):
            x0 = rail.gate(e0).get_center()[0] + 0.06
            x1 = rail.gate(e1).get_center()[0] - 0.06
            dummy = Line([x0, y_br, 0], [x1, y_br, 0])
            br = bracket(dummy, color=color, buff=0.0)
            t = label(text, size=FS_SMALL, color=color).next_to(br, UP, buff=0.08)
            return VGroup(br, t)

        parts = VGroup(seg_bracket(5, 6, GOLD, "inclusion"), seg_bracket(6, 9, CYAN, "delegated"),
                       seg_bracket(9, 10, GOLD, "spend"))
        self.pad_to(A("three parts") - 0.4)
        self.play(FadeOut(n5),
                  LaggedStart(*[FadeIn(p, shift=0.1 * UP) for p in parts], lag_ratio=0.35), run_time=1.2)

        # ======== movement 1: inclusion epoch (wallet-only) ========================================
        self.pad_to(A("lets start") - 0.1)
        self.play(parts[1].animate.fade(0.6), parts[2].animate.fade(0.6),
                  Indicate(parts[0], color=GOLD), run_time=0.8)
        tree, leaves, root = evidence_tree_glyph(w=4.4, h=1.5)
        tree.move_to([0, -1.3, 0])
        tree_l = mtex('"evidence tree"_5', size=FS_LABEL, color=STAR).next_to(tree, LEFT, buff=0.4)
        self.pad_to(A("evidence tree") - 0.3)
        self.play(FadeIn(tree, lag_ratio=0.05), FadeIn(tree_l), run_time=1.0)

        def opening(leaf, text_parts, pos):
            chip = boxed(rich(text_parts, size=FS_LABEL), color=STAR, pad=0.14).move_to(pos)
            path = VGroup(Line(root.get_center(), leaf.get_center(), stroke_color=GOLD, stroke_width=SW))
            return chip, path

        op_nf, path_nf = opening(leaves[5], [("bucket for", TXT), ('$"nf"_5$', STAR)], [-3.4, -0.55, 0])
        op_cm, path_cm = opening(leaves[12], [("bucket for", TXT), ('$"cm"$', STAR)], [3.4, -0.55, 0])
        self.pad_to(A("once at the bucket") - 0.2)
        self.play(ShowCreation(path_nf), leaves[5].animate.set_fill(GOLD, 1).scale(1.8), run_time=0.6)
        self.play(TransformFromCopy(leaves[5], op_nf), run_time=0.7)
        self.pad_to(A("and once") - 0.1)
        self.play(ShowCreation(path_cm), leaves[12].animate.set_fill(GOLD, 1).scale(1.8), run_time=0.6)
        self.play(TransformFromCopy(leaves[12], op_cm), run_time=0.7)

        self.pad_to(A("noteunspentinit") - 0.3)
        p_init = step_pill("NoteUnspentInit", GOLD).move_to([-3.4, 0.55, 0])
        e_a = up_arrow(op_nf, p_init)
        wit = rich([("note +", TXT), ('$("ak", "nk")$', GOLD)], size=FS_LABEL).next_to(p_init, LEFT, buff=0.25)
        wit.shift(RIGHT * max(0, -6.5 - wit.get_left()[0]) + UP * 0.55)
        self.play(ShowCreation(e_a), FadeIn(p_init, scale=0.8), run_time=0.6)
        self.play(FadeIn(wit, shift=0.15 * RIGHT), run_time=0.5)
        notes = VGroup(
            mtex('"nf"_5 = f_"mk" (5)', size=FS_LABEL, color=GOLD),
            rich([("profile selects", TXT), ("$q_b$", STAR)], size=FS_LABEL),
            mtex('q_b ("nf"_5) != 0', size=FS_LABEL, color=FLARE),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT).move_to([0.2, 1.1, 0])
        for i, w in enumerate(["derives", "profile", "proves its|absent"]):
            self.pad_to(A(w) - 0.25)
            self.play(FadeIn(notes[i], shift=0.1 * LEFT), run_time=0.5)
        h_un = hdr("NoteUnspent", ['"cm"', "5", "6", '"sntl"_5', '"sntl"_6'], GOLD, size=FS_LABEL)
        h_un.move_to([-3.4, 1.5, 0])
        self.pad_to(A("absent") + 0.45)
        e_b = up_arrow(p_init, h_un)
        self.play(FadeOut(VGroup(notes, wit)), ShowCreation(e_b), FadeIn(h_un, shift=0.1 * UP), run_time=0.6)
        self.pad_to(A("spendablereinit") - 0.2)
        p_re = step_pill("SpendableReinit", GOLD).move_to([0.6, 2.35, 0])
        e_c = tarrow(h_un.get_top(), p_re.get_left(), color=MUT)
        e_d = tarrow(op_cm.get_top(), p_re.get_right() + DOWN * 0.1, color=MUT)
        self.play(FadeIn(p_re, scale=0.8), ShowCreation(e_c), ShowCreation(e_d), run_time=0.7)
        self.pad_to(A("membership") - 0.2)
        memb = mtex('q_(b^prime) ("cm") = 0', size=FS_LABEL, color=GOLD).next_to(op_cm, DOWN, buff=0.25)
        self.play(FadeIn(memb, shift=0.1 * DOWN), run_time=0.6)
        self.pad_to(A("same sentinels|same epoch") - 0.1)
        self.play(Indicate(h_un.fields[3:5], color=STAR, scale_factor=1.15), run_time=0.7)
        self.pad_to(A("what comes out") - 0.2)
        h_sp6 = hdr("NoteSpendable", ['"cm"', "6", '"sntl"_6'], GOLD, size=FS_LABEL)
        h_sp6.next_to(p_re, RIGHT, buff=0.5)
        e_e = tarrow(p_re.get_right(), h_sp6.get_left(), color=MUT)
        self.play(ShowCreation(e_e), FadeIn(h_sp6, shift=0.1 * RIGHT), run_time=0.8)
        self.pad_to(A("start of epoch") - 0.1)
        self.play(Flash(rail.gate(6).get_top(), color=GOLD, flash_radius=0.3),
                  rail.gate(6).animate.set_stroke(GOLD, SW_BOLD), run_time=0.7)
        # ⟨pause: the spendable header glows⟩
        self.pad_to(word_end(SID, "start of epoch six") - 0.05)
        self.play(h_sp6.box.animate.set_fill(GOLD, 0.22).set_stroke(GOLD, SW_BOLD),
                  ShowPassingFlash(h_sp6.box.copy().set_stroke(STAR, SW_BOLD + 2), time_width=0.5), run_time=0.9)

        # ======== movement 2: epochs 6..8 ===========================================================
        self.pad_to(A("epochs six through") - 0.15)
        m1 = VGroup(tree, tree_l, path_nf, path_cm, op_nf, op_cm, p_init, e_a, h_un, e_b, p_re, e_c,
                    e_d, memb, e_e)
        dock_sp = h_sp6.copy().scale(0.86).move_to([0, 3.25, 0])
        self.play(FadeOut(m1), Transform(h_sp6, dock_sp), parts[0].animate.fade(0.6),
                  parts[1].animate.set_opacity(1), run_time=0.9)
        self.play(Indicate(parts[1], color=CYAN), run_time=0.6)

        XO, XW = 3.3, -3.3
        # OSS side
        self.pad_to(A("on the service") - 0.2)
        oss_l = label("service", size=FS_BODY, color=CYAN).move_to([XO, 2.35, 0])
        p_us = step_pill("UnspentSeed", CYAN).move_to([XO, -1.95, 0])
        self.play(FadeIn(oss_l), FadeIn(p_us, scale=0.8), run_time=0.6)

        def arb(s_r, com):
            return hdr("Unspent", ["6", str(s_r), com], CYAN, size=FS_LABEL).move_to([XO, -1.05, 0])
        h_arb = arb(6, '"Com"(1)')
        e1 = up_arrow(p_us, h_arb)
        self.pad_to(A("empty range") - 0.3)
        self.play(ShowCreation(e1), FadeIn(h_arb, shift=0.1 * UP), run_time=0.6)
        p_ul = step_pill("UnspentLift", CYAN).move_to([XO, 0.15, 0])
        e2 = up_arrow(h_arb, p_ul)
        self.pad_to(A("each unspentlift") - 0.2)
        self.play(ShowCreation(e2), FadeIn(p_ul, scale=0.8), run_time=0.6)
        row_s = VGroup()
        pawl = Triangle().scale(0.13).rotate(PI).set_fill(CYAN, 1).set_stroke(width=0)
        pawl.move_to(rail.gate(6).get_bottom() + DOWN * 0.05).shift(DOWN * 0.0)
        pawl.next_to(rail.gate(6), UP, buff=0.02).shift(UP * 0.62)

        # UnspentLift runs once per epoch: a self-loop on the pill, pulsed on every cycle
        lc = p_ul.get_right() + RIGHT * 0.38
        arc = Arc(radius=0.34, start_angle=0.8 * PI, angle=-1.6 * PI, arc_center=lc)
        arc.set_stroke(CYAN, SW).set_fill(opacity=0)
        end, prev = arc.get_end(), arc.point_from_proportion(0.96)
        u = (end - prev) / max(np.linalg.norm(end - prev), 1e-6)
        n = np.array([-u[1], u[0], 0.0])
        head = Polygon(end + u * 0.08, end - u * 0.12 + n * 0.09, end - u * 0.12 - n * 0.09)
        head.set_fill(CYAN, 1).set_stroke(width=0)
        loop = VGroup(arc, head)
        loop_l = label("once per epoch", size=FS_SMALL, color=CYAN).next_to(loop, RIGHT, buff=0.15)

        def pulse_loop():
            return ShowPassingFlash(arc.copy().set_stroke(STAR, SW_BOLD + 2), time_width=0.6)

        def pawl_to(e):
            return pawl.animate.next_to(rail.gate(e), UP, buff=0.02).shift(UP * 0.62)

        def lift_cycle(i, times=None, rt=0.6):
            """One UnspentLift: opening -> nonzero -> cubic factor -> advance one sentinel.
            times = (open, nonzero, factor, advance) anchors; None = one compact beat."""
            op = boxed(rich([("bucket for", TXT), (f'$"nf"_{i}$', STAR)], size=FS_LABEL), color=STAR,
                       pad=0.12).move_to([XO + 2.0, 1.75, 0])
            ne = mtex(f'q_b ("nf"_{i}) != 0', size=FS_LABEL, color=FLARE).next_to(p_ul, LEFT, buff=0.35)
            t = tile_row([i], CYAN)[0].move_to([XO, 1.0, 0])
            row_s.add(t)
            target = row_s.copy().arrange(RIGHT, buff=0.06).move_to([XO, 1.0, 0])
            new = arb(i + 1, '"Com"(g_S)')
            if times:
                self.pad_to(times[0])
                self.play(FadeIn(op, shift=0.2 * DOWN), run_time=rt)
                self.pad_to(times[1])
                self.play(op.animate.scale(0.4).move_to(p_ul).set_opacity(0), FadeIn(ne), run_time=rt)
                self.remove(op)
                self.pad_to(times[2])
                self.play(FadeIn(t, shift=0.2 * UP), Transform(row_s, target), FadeTransform(holder[0], new),
                          run_time=rt)
                self.pad_to(times[3])
                self.play(pawl_to(i + 1), FadeOut(ne), pulse_loop(), run_time=0.9)
            else:
                self.add(op)
                self.play(op.animate.scale(0.4).move_to(p_ul).set_opacity(0),
                          FadeIn(t, shift=0.2 * UP), Transform(row_s, target), FadeTransform(holder[0], new),
                          pawl_to(i + 1), pulse_loop(), run_time=0.6)
                self.remove(op)
            holder[0] = new

        holder = [h_arb]
        self.add(pawl)
        self.play(ShowCreation(loop), FadeIn(loop_l), run_time=0.5)
        lift_cycle(6, (A("evidence tree opening") - 0.4, A("proves one") - 0.2,
                       A("multiplies one") - 0.2, A("advances from") - 0.1))
        self.play(Flash(rail.gate(7).get_top(), color=CYAN, flash_radius=0.25), run_time=0.5)
        self.pad_to(A("cant skip") - 0.1)
        self.play(Indicate(pawl, color=FLARE, scale_factor=1.6), run_time=0.6)
        self.pad_to(A("reorder them") - 0.1)
        self.play(pulse_loop(), run_time=0.6)
        # ⟨pause: a skip attempt jams the ratchet⟩
        self.pad_to(word_end(SID, "reorder them") - 0.05)
        self.play(pawl_to(9), run_time=0.4, rate_func=there_and_back)
        jam = mtex("times.big", size=FS_HEAD, color=FLARE).move_to(rail.gate(9).get_center())
        self.play(FadeIn(jam, scale=1.6), run_time=0.3)
        self.play(FadeOut(jam), run_time=0.3)
        # the loop keeps turning: epochs 7 and 8, while "the service never learns which note"
        self.pad_to(A("the service never") - 0.4)
        lift_cycle(7)
        lift_cycle(8)
        self.pad_to(A("which note") - 0.2)
        q = rich([("which note?", CYAN), ("unknown", MUT)], size=FS_LABEL).next_to(oss_l, DOWN, buff=0.2)
        self.play(FadeIn(q), run_time=0.6)

        # wallet side
        self.pad_to(A("meanwhile") - 0.2)
        wal_l = label("wallet", size=FS_BODY, color=GOLD).move_to([XW, 2.35, 0])
        p_ns = step_pill("NoteSeed", GOLD).move_to([XW, -1.95, 0])
        self.play(FadeIn(wal_l), run_time=0.5)
        self.pad_to(A("noteseed") - 0.2)
        self.play(FadeIn(p_ns, scale=0.8), run_time=0.5)
        h_nm = hdr("NoteMaster", ['"cm"', '"mk"'], GOLD, size=FS_LABEL).move_to([XW, -1.05, 0])
        e3 = up_arrow(p_ns, h_nm)
        self.pad_to(A("master key") - 0.3)
        self.play(ShowCreation(e3), FadeIn(h_nm, shift=0.1 * UP), run_time=0.6)
        p_d1 = step_pill("NullifierDerive", GOLD).move_to([XW - 1.6, 0.15, 0])
        p_d2 = step_pill("NullifierDerive", GOLD).move_to([XW + 1.6, 0.15, 0])
        e4, e5 = up_arrow(h_nm, p_d1), up_arrow(h_nm, p_d2)
        self.pad_to(A("each nullifierderive") - 0.2)
        self.play(ShowCreation(e4), ShowCreation(e5), FadeIn(p_d1, scale=0.8), FadeIn(p_d2, scale=0.8),
                  run_time=0.7)
        w1 = tile_row(range(4, 8), GOLD).scale(0.95).move_to([XW - 1.6, 1.0, 0])
        w2 = tile_row(range(8, 12), GOLD).scale(0.95).move_to([XW + 1.6, 1.0, 0])
        self.pad_to(A("four up to") - 0.2)
        self.play(LaggedStart(*[FadeIn(t, shift=0.15 * UP) for t in w1], lag_ratio=0.2), run_time=0.7)
        self.pad_to(A("then eight") - 0.1)
        self.play(LaggedStart(*[FadeIn(t, shift=0.15 * UP) for t in w2], lag_ratio=0.2), run_time=0.7)
        self.pad_to(A("nullifierfuse") - 0.2)
        p_fu = step_pill("NullifierFuse", GOLD).move_to([XW, 1.75, 0])
        self.play(FadeIn(p_fu, scale=0.8), run_time=0.5)
        row_r = VGroup(*w1, *w2)
        target_r = row_r.copy().arrange(RIGHT, buff=0.05).move_to([XW, 2.55, 0])
        self.pad_to(A("into one commitment") - 0.2)
        self.play(Transform(row_r, target_r), FadeOut(wal_l), run_time=0.9)
        r_lab = mtex("g_R, quad R = [4, 12)", size=FS_LABEL, color=GOLD).next_to(p_fu, RIGHT, buff=0.35)
        self.play(FadeIn(r_lab), run_time=0.5)

        # ======== movement 3: the join ==============================================================
        self.pad_to(A("the join") - 0.3)
        m2 = VGroup(p_us, e1, holder[0], e2, p_ul, oss_l, q, p_ns, e3, h_nm, e4, e5, p_d1, p_d2, p_fu, r_lab, loop, loop_l,
                    pawl)
        tgt_r = row_r.copy().arrange(RIGHT, buff=0.05).move_to([0, 1.35, 0])
        tgt_s = row_s.copy()
        for k, t in enumerate(tgt_s):
            t.move_to(tgt_r[2 + k].get_center() + DOWN * 1.05)
        self.play(FadeOut(m2), Transform(row_r, tgt_r), Transform(row_s, tgt_s),
                  parts[1].animate.fade(0.6), run_time=1.0)
        lab_r = mtex("g_R", size=FS_LABEL, color=GOLD).next_to(row_r, LEFT, buff=0.3)
        lab_s = mtex("g_S", size=FS_LABEL, color=CYAN).next_to(row_s, LEFT, buff=0.3)
        p_ub = step_pill("UnspentBind", GOLD).move_to([0, -1.35, 0])
        self.pad_to(A("unspentbind") - 0.2)
        self.play(FadeIn(lab_r), FadeIn(lab_s), FadeIn(p_ub, scale=0.8), run_time=0.6)
        self.pad_to(A("sits inside") - 0.2)
        sub = mtex("[6, 9) subset.eq [4, 12)", size=FS_LABEL, color=STAR).next_to(p_ub, RIGHT, buff=0.4)
        self.play(FadeIn(sub, shift=0.1 * LEFT), run_time=0.6)
        self.pad_to(A("runs the division") - 0.2)
        eq = mtex("g_R = g_S dot q", size=FS_BODY, color=GOLD).move_to([0, -0.55, 0])
        self.play(FadeIn(eq, shift=0.1 * UP), run_time=0.7)
        self.pad_to(A("divides the") - 0.3)
        # the service's factors stack onto the wallet's matching ones...
        self.play(*[row_s[k].animate.next_to(row_r[2 + k], UP, buff=0.04) for k in range(3)], run_time=1.0)
        # ⟨pause: the service's stack lifts out of the wallet's⟩
        self.pad_to(word_end(SID, "divides the wallets") - 0.05)
        self.play(FadeOut(VGroup(*row_s, *row_r[2:5]), shift=0.9 * UP), FadeOut(lab_s), run_time=0.55)
        rest = VGroup(row_r[0], row_r[1], *row_r[5:])
        rest_t = rest.copy().arrange(RIGHT, buff=0.05).move_to([0, 1.35, 0])
        q_lab = mtex("q", size=FS_LABEL, color=GOLD).next_to(rest_t, RIGHT, buff=0.3)
        ck = checkmark(0.3, GOLD).next_to(eq, RIGHT, buff=0.25)
        self.play(Transform(rest, rest_t), FadeIn(q_lab), lab_r.animate.next_to(rest_t, LEFT, buff=0.3),
                  ShowCreation(ck), run_time=0.55)
        self.pad_to(A("becomes about") - 0.4)
        h_nu = hdr("NoteUnspent", ['"cm"', "6", "9", '"sntl"_6', '"sntl"_9'], GOLD, size=FS_LABEL)
        h_nu.move_to([2.6, -1.35, 0])
        self.play(FadeOut(VGroup(rest, q_lab, sub, ck, lab_r)), eq.animate.scale(0.8).move_to([0, 1.9, 0]),
                  p_ub.animate.move_to([-1.2, -2.0, 0]), run_time=0.6)
        h_nu.next_to(p_ub, RIGHT, buff=0.6)
        e6 = tarrow(p_ub.get_right(), h_nu.get_left(), color=MUT)
        self.play(ShowCreation(e6), FadeIn(h_nu, shift=0.1 * RIGHT), run_time=0.7)

        self.pad_to(A("spendablelift") - 0.3)
        self.play(h_sp6.animate.scale(1 / 0.86).move_to([-3.4, 0.25, 0]), FadeOut(eq), run_time=0.8)
        p_sl = step_pill("SpendableLift", GOLD).move_to([0, 1.3, 0])
        e7 = tarrow(h_sp6.get_top(), p_sl.get_left(), color=MUT)
        e8 = tarrow(h_nu.get_top(), p_sl.get_right(), color=MUT)
        self.play(FadeIn(p_sl, scale=0.8), ShowCreation(e7), ShowCreation(e8), run_time=0.7)
        self.pad_to(A("sentinels match") - 0.3)
        u1 = Underline(h_sp6.fields[2], buff=0.05).set_stroke(STAR, SW_BOLD)
        u2 = Underline(h_nu.fields[3], buff=0.05).set_stroke(STAR, SW_BOLD)
        self.play(ShowCreation(u1), ShowCreation(u2), run_time=0.6)
        self.pad_to(A("and now") - 0.2)
        h_sp9 = hdr("NoteSpendable", ['"cm"', "9", '"sntl"_9'], GOLD, size=FS_LABEL).move_to([0, 2.35, 0])
        e9 = up_arrow(p_sl, h_sp9)
        self.play(ShowCreation(e9), FadeIn(h_sp9, shift=0.1 * UP), run_time=0.7)
        self.pad_to(A("through the start") - 0.1)
        self.play(Flash(rail.gate(9).get_top(), color=GOLD, flash_radius=0.3),
                  rail.gate(9).animate.set_stroke(GOLD, SW_BOLD), parts[2].animate.set_opacity(1),
                  run_time=0.8)

        # --- same as before: bind, merge, lift -------------------------------------------------------
        self.pad_to(A("from there") - 0.2)
        old = VGroup(h_sp6, h_nu, p_ub, e6, p_sl, e7, e8, u1, u2, e9)
        self.play(FadeOut(old), h_sp9.animate.move_to([-4.45, -0.6, 0]), run_time=0.8)
        chain = VGroup(step_pill("SpendBind", GOLD), step_pill("StampMerge", GOLD),
                       step_pill("StampLift", GOLD))
        chain.arrange(RIGHT, buff=0.9).move_to([2.45, -0.6, 0])
        arrows = VGroup(tarrow(h_sp9.get_right(), chain[0].get_left(), color=MUT),
                        tarrow(chain[0].get_right(), chain[1].get_left(), color=MUT),
                        tarrow(chain[1].get_right(), chain[2].get_left(), color=MUT))
        self.pad_to(A("spendbind derives") - 0.2)
        self.play(FadeIn(chain[0], scale=0.8), ShowCreation(arrows[0]), run_time=0.6)
        nfs = mtex('"nf"_9, "nf"_10', size=FS_LABEL, color=FLARE).next_to(chain[0], DOWN, buff=0.25)
        self.play(FadeIn(nfs), run_time=0.4)
        self.pad_to(A("stampmerge joins") - 0.2)
        other = boxed(rich([("Stamp", GOLD), ('$("note"_9 + "outputs")$', GOLD)], size=FS_LABEL), color=GOLD,
                      pad=0.12).next_to(chain[1], DOWN, buff=0.7)
        e_o = tarrow(other.get_top(), chain[1].get_bottom(), color=MUT)
        self.play(FadeIn(chain[1], scale=0.8), ShowCreation(arrows[1]), FadeIn(other, shift=0.2 * DOWN),
                  ShowCreation(e_o), run_time=0.8)
        self.pad_to(A("one stamplift") - 0.2)
        self.play(FadeIn(chain[2], scale=0.8), ShowCreation(arrows[2]), run_time=0.6)
        fin = boxed(label("one stamp: 2 spends, 2 outputs", size=FS_LABEL, color=STAR), color=STAR,
                    pad=0.14).next_to(chain[2], UP, buff=0.7)
        fin.shift(LEFT * max(0, fin.get_right()[0] - 6.5))
        e_f = tarrow(chain[2].get_top(), fin.get_bottom(), color=MUT)
        self.pad_to(A("target anchor") - 0.2)
        tgt_a = bead(STAR, r=0.09).move_to(rail.center_of(9) + RIGHT * 0.15)
        self.play(GrowFromCenter(tgt_a), Flash(tgt_a.get_center(), color=STAR, flash_radius=0.3),
                  Indicate(chain[2], color=STAR, scale_factor=1.1), run_time=0.7)
        # ⟨pause: the full tree: one stamp, two spends, two outputs⟩
        self.pad_to(word_end(SID, "anchor in epoch nine") - 0.05)
        self.play(ShowCreation(e_f), FadeIn(fin, shift=0.1 * UP), run_time=0.6)
        self.play(Flash(fin.get_center(), color=STAR, flash_radius=fin.get_width() / 2 + 0.2, line_length=0.2),
                  run_time=0.5)

        # --- UnspentMerge one-liner -------------------------------------------------------------------
        self.pad_to(A("several services") - 0.3)
        spend_part = VGroup(h_sp9, chain, arrows, nfs, other, e_o, fin, e_f, tgt_a)
        self.play(FadeOut(spend_part), run_time=0.6)
        ha = hdr("Unspent", ["6", "8", '"sntl"_6', '"sntl"_8'], CYAN, size=FS_LABEL)
        hb = hdr("Unspent", ["8", "9", '"sntl"_8', '"sntl"_9'], CYAN, size=FS_LABEL)
        VGroup(ha, hb).arrange(RIGHT, buff=0.6).move_to([0, -1.4, 0])
        p_um = step_pill("UnspentMerge", CYAN).move_to([0, 0.2, 0])
        ea, eb = up_arrow(ha, p_um), up_arrow(hb, p_um)
        self.play(FadeIn(ha, shift=0.1 * UP), FadeIn(hb, shift=0.1 * UP), run_time=0.7)
        self.pad_to(A("unspentmerge") - 0.2)
        self.play(FadeIn(p_um, scale=0.8), ShowCreation(ea), ShowCreation(eb), run_time=0.6)
        self.pad_to(A("end sentinel") - 0.3)
        ua = Underline(ha.fields[3], buff=0.05).set_stroke(STAR, SW_BOLD)
        ub = Underline(hb.fields[2], buff=0.05).set_stroke(STAR, SW_BOLD)
        hm = hdr("Unspent", ["6", "9", '"sntl"_6', '"sntl"_9'], CYAN, size=FS_LABEL).move_to([0, 1.35, 0])
        em = up_arrow(p_um, hm)
        self.play(ShowCreation(ua), ShowCreation(ub), run_time=0.5)
        self.play(ShowCreation(em), FadeIn(hm, shift=0.1 * UP), run_time=0.6)

        # --- privacy bottom line -------------------------------------------------------------------------
        self.pad_to(A("so what does") - 0.3)
        q_title = scene_title("What does a service learn?")
        self.play(FadeOut(VGroup(ha, hb, p_um, ea, eb, ua, ub, hm, em)), run_time=0.6)
        self.play(FadeIn(q_title, shift=0.1 * DOWN), run_time=0.7)
        sees = rich([("a service sees:", CYAN), ('$(i, "nf"_i)$', STAR)], size=FS_BODY)
        sees2 = label("and ranges it can't tell apart from decoys", size=FS_BODY, color=TXT)
        VGroup(sees, sees2).arrange(DOWN, buff=0.25).move_to([0, 1.75, 0])
        self.pad_to(A("only sees") - 0.2)
        self.play(FadeIn(sees, shift=0.1 * DOWN), run_time=0.7)
        self.pad_to(A("and ranges") - 0.15)
        self.play(FadeIn(sees2, shift=0.1 * DOWN), run_time=0.7)
        never_t = label("never sees:", size=FS_BODY, color=CYAN).move_to([-4.2, 0.2, 0])
        items = ["the commitment", "the note", "another service's work", "where the spend lands"]
        rows = VGroup(*[VGroup(mtex("times", size=FS_BODY, color=FLARE), label(t, size=FS_BODY, color=TXT))
                        .arrange(RIGHT, buff=0.25) for t in items])
        rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT).next_to(never_t, RIGHT, buff=0.5).align_to(never_t, UP)
        self.pad_to(A("never sees") - 0.2)
        self.play(FadeIn(never_t), FadeIn(rows[0], shift=0.1 * RIGHT), run_time=0.6)
        for r, w in zip(rows[1:], ["the note another", "another", "where the spend"]):
            self.pad_to(A(w) - 0.15)
            self.play(FadeIn(r, shift=0.1 * RIGHT), run_time=0.4)
        self.pad_to(scene_T(SID))

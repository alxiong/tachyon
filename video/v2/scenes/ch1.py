"""Chapter 1 — Ownership, stripped down (scenes 1.1, 1.2, 1.3).

1.1 highlights the real spec figure (book/src/assets/zcash_keys.png) by pixel-mapped
overlays (never dimming the raster); pixel helpers adapted from v1 anim/act1.py.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style import *  # noqa: E402,F403

ASSETS = "/home/alex/work/tachyon_wt1/video/assets"
ZK_PNG = "/home/alex/work/tachyon_wt1/book/src/assets/zcash_keys.png"
ZK_ORCHARD_PNG = os.path.join(ASSETS, "zcash_keys_orchard.png")

# ---- pixel-space regions (raster coordinates, y down) --------------------------
FULL_DIMS = (2020.0, 828.0)
CROP_DIMS = (670.0, 770.0)          # crop (1320, 30)-(1990, 800) of the full png
CROP_SRC = (1320, 30, 1990, 800)
SPROUT_KEYS = (215, 175, 432, 348)
ORCHARD_PANEL = (1312, 35, 1978, 800)
O_ADDR = (1510, 182, 1773, 237)
O_DKIVK = (1508, 286, 1702, 341)
O_OVK = (1737, 286, 1808, 341)
O_AK = (1535, 443, 1607, 493)
O_NK = (1624, 442, 1697, 494)


def crop_box(b):
    x0, y0, x1, y1 = b
    return (x0 - 1320, y0 - 30, x1 - 1320, y1 - 30)


C_ADDR, C_DKIVK, C_OVK, C_AK, C_NK = map(crop_box, (O_ADDR, O_DKIVK, O_OVK, O_AK, O_NK))
C_DIVERS = (196, 148, 266, 240)
C_OTHERS = {"d": (203, 158, 252, 202), "pkd": (372, 158, 442, 202),
            "dk": (198, 258, 252, 305), "ivk": (316, 258, 378, 305),
            "ovk": (408, 255, 480, 310), "rivk": (398, 413, 478, 462)}
OTHER_KEYS = [("d", '"d"', PNG_ADDR), ("pkd", '"pk"_"d"', PNG_ADDR),
              ("dk", '"dk"', PNG_IVK), ("ivk", '"ivk"', PNG_IVK),
              ("ovk", '"ovk"', PNG_OVK), ("rivk", '"rivk"', PNG_FVK)]

CROP_H = 6.2
CROP_POS = np.array([-6.6 + 0.5 * CROP_H * CROP_DIMS[0] / CROP_DIMS[1], -0.3, 0])
NOTES_X = -0.75
COL_X = 3.0


def pix(img, dims, box):
    x0, y0, x1, y1 = box
    W, H = dims
    ul = img.get_corner(UL)
    w, h = img.get_width(), img.get_height()
    c = np.array([ul[0] + (x0 + x1) / 2 / W * w, ul[1] - (y0 + y1) / 2 / H * h, 0])
    return c, (x1 - x0) / W * w, (y1 - y0) / H * h


def pix_rect(img, dims, box, color=GOLD, buff=0.08, stroke_width=4.0):
    c, w, h = pix(img, dims, box)
    r = RoundedRectangle(width=w + 2 * buff, height=h + 2 * buff, corner_radius=0.1)
    r.set_fill(opacity=0).set_stroke(color, stroke_width, 1.0).move_to(c)
    return r


def pix_contour(img, dims, box, seed=3, color=GOLD, buff=0.14, **kw):
    c, w, h = pix(img, dims, box)
    return contour(center=c, w=w + 2 * buff, h=h + 2 * buff, seed=seed, color=color, **kw)


def pix_dash(img, dims, box, color=GOLD, buff=0.08, **kw):
    c, w, h = pix(img, dims, box)
    return dashed_box(center=c, w=w + 2 * buff, h=h + 2 * buff, color=color, **kw)


def strike(mob, color=FLARE):
    """Deliberate strike-through (polyline, so the layout linter ignores it)."""
    vm = VMobject()
    vm.set_points_as_corners([mob.get_corner(DL) + 0.08 * DL, mob.get_corner(UR) + 0.08 * UR])
    vm.set_stroke(color, SW_BOLD, 1.0)
    return vm


def force_block(n, head, rows):
    badge = VGroup(Circle(radius=0.3).set_stroke(GOLD, SW_THIN, 1.0).set_fill(GOLD, 0.12),
                   mtex(str(n), size=FS_BODY, color=GOLD))
    badge[1].move_to(badge[0])
    h = label(head, size=FS_HEAD, color=STAR, weight="BOLD")
    top = VGroup(badge, h)
    h.next_to(badge, RIGHT, buff=0.28)
    badge.match_y(h)
    body = VGroup(*rows).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
    body.next_to(h, DOWN, buff=0.24, aligned_edge=LEFT)
    return VGroup(top, body)


def eq_row(eq, note):
    return VGroup(eq, note).arrange(RIGHT, buff=0.45, aligned_edge=DOWN)


SEAM_Y = -0.615
HEAD_Y = 3.33
PAY_TOP_Y = -1.12


def make_blade():
    return Line([NOTES_X + 0.1, SEAM_Y, 0], [6.6, SEAM_Y, 0], stroke_width=SW_BOLD, stroke_color=GOLD)


def bands():
    core = panel(13.5, 4.15, color=GOLD, fill_opacity=0.03).move_to([0, 1.62, 0])
    pay = panel(13.5, 2.95, color=CYAN, fill_opacity=0.03).move_to([0, -2.25, 0])
    core_head = label("Shielded protocol", size=FS_BODY, color=GOLD, weight="BOLD")
    core_head.move_to([-6.45, HEAD_Y, 0], aligned_edge=LEFT)
    pay_head = label("Payment protocol", size=FS_BODY, color=CYAN, weight="BOLD")
    pay_head.move_to([-6.45, PAY_TOP_Y, 0], aligned_edge=LEFT)
    core_def = itex("bind every note to an owner; only the owner spends", size=FS_LABEL, color=TXT)
    core_def.move_to([6.45, HEAD_Y, 0], aligned_edge=RIGHT)
    pay_def = itex("get every note to its recipient", size=FS_LABEL, color=TXT)
    pay_def.move_to([6.45, PAY_TOP_Y, 0], aligned_edge=RIGHT)
    seam = Line(LEFT * 6.55, RIGHT * 6.55, stroke_width=SW_BOLD, stroke_color=GOLD).move_to(UP * SEAM_Y)
    return core, pay, core_head, pay_head, core_def, pay_def, seam


def cut_buys():
    core_name = label("a smaller, stable shielded core", size=FS_HEAD, color=GOLD, weight="BOLD")
    core_box = panel(core_name.get_width() + 1.0, 1.25, color=GOLD, fill_opacity=0.1).move_to([0, 2.05, 0])
    core_name.move_to(core_box)
    stable = label("cleaner security assumptions to audit", size=FS_BODY, color=STAR).move_to([0, 0.6, 0])
    modules = VGroup(*[key_chip(t, color=CYAN, size=FS_BODY) for t in
                       ["payment protocol A", "payment protocol B", "payment protocol C"]])
    modules.arrange(RIGHT, buff=0.7).move_to([0, -2.0, 0])
    evolve = label("two halves evolving in parallel", size=FS_BODY, color=CYAN).move_to([0, -3.05, 0])
    return core_box, core_name, stable, modules, evolve


def prop_chip(t, color):
    c = key_chip(t, color=color, size=FS_BODY, pad=0.18)
    back = c[0].copy().set_fill(VOID, 1.0).set_stroke(width=0)
    return VGroup(back, c)


def xmark(size=0.26, color=FLARE):
    a, b = VMobject(), VMobject()
    a.set_points_as_corners([size * (UL / 2), size * (DR / 2)])
    b.set_points_as_corners([size * (UR / 2), size * (DL / 2)])
    return VGroup(a, b).set_stroke(color, SW, 1.0)


class Scene11(TimedScene):
    def construct(self):
        SID = "1.1"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731

        full = ImageMobject(ZK_PNG)
        full.set_width(13.4 * 0.96).move_to(DOWN * 0.05)
        self.wait(0.5)
        self.play(FadeIn(full, scale=1.03), run_time=1.6)
        self.play(full.animate.set_width(13.4).move_to(DOWN * 0.05), run_time=5.5, rate_func=smooth)

        # Sprout: two keys
        self.pad_to(A("sprout") - 0.2)
        r_sprout = pix_rect(full, FULL_DIMS, SPROUT_KEYS)
        self.play(ShowCreation(r_sprout), run_time=0.5)
        self.pad_to(A("two keys") - 0.1)
        self.play(Indicate(r_sprout, color=GOLD, scale_factor=1.05), run_time=0.8)
        # Orchard: not that
        self.pad_to(A("orchard's key diagram|orchards key diagram") - 0.2)
        r_orch = pix_rect(full, FULL_DIMS, ORCHARD_PANEL)
        self.play(FadeOut(r_sprout), ShowCreation(r_orch), run_time=0.7)
        self.pad_to(A("where did all") - 0.3)
        title = scene_title("Where did all of this come from?")
        self.play(Write(title), run_time=1.2)

        # zoom: the Orchard panel lifts out, the forces read beside it
        crop = ImageMobject(ZK_ORCHARD_PNG)
        c, w, h = pix(full, FULL_DIMS, CROP_SRC)
        crop.set_height(h).move_to(c)
        self.pad_to(A("first reason") - 0.4)
        self.add(crop)
        self.play(crop.animate.set_height(CROP_H).move_to(CROP_POS), FadeOut(full),
                  FadeOut(r_orch), FadeOut(title), run_time=1.3)

        f1 = force_block(1, "proving ≠ authorizing", [
            label("hardware wallets can't run a prover", size=FS_BODY, color=TXT),
            label("so spends are signed, outside the proof", size=FS_BODY, color=TXT),
            mtex('"rk" = "ak" + [alpha] thin G', size=FS_HEAD, color=GOLD),
        ])
        f2 = force_block(2, "owning ≠ receiving", [
            label("the address also carries the transmission key", size=FS_BODY, color=TXT),
            eq_row(mtex('"pk"_d = ["ivk"] thin g_d', size=FS_HEAD, color=GOLD),
                   mtex('fresh $d$, one $"ivk"$', size=FS_LABEL + 2, color=TXT, math=False)),
        ])
        f3 = force_block(3, "selective disclosure", [
            label("show your flows without spend authority", size=FS_BODY, color=TXT),
            eq_row(mtex('"ovk"', size=FS_HEAD, color=GOLD),
                   label("and the rest of the viewing family", size=FS_LABEL + 2, color=TXT)),
        ])
        forces = VGroup(f1, f2, f3).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_in(forces, (NOTES_X, 6.7, -3.3, 2.85), align=LEFT)
        gap = (2.8 - (-3.25) - sum(f.get_height() for f in forces)) / 2
        forces.arrange(DOWN, buff=min(max(gap, 0.4), 1.2), aligned_edge=LEFT)
        forces.move_to([NOTES_X, 0, 0], aligned_edge=LEFT).align_to(UP * 2.8, UP)

        live = []

        def circle_out(box, t, seed, run=0.6):
            self.pad_to(t - 0.2)
            cm = pix_contour(crop, CROP_DIMS, box, seed=seed, stroke_width=4.0)
            live.append(cm)
            self.play(ShowCreation(cm), run_time=run)

        def reveal(m, t, run=0.6):
            self.pad_to(t - 0.2)
            self.play(FadeIn(m, shift=LEFT * 0.15), run_time=run)

        # reason 1
        self.play(FadeIn(f1[0], shift=LEFT * 0.25), run_time=0.7)
        reveal(f1[1][0], A("hardware wallets"))
        reveal(f1[1][1], A("authorization became|became a signature"))
        self.pad_to(A("re randomized|rerandomized") - 0.3)
        self.play(Write(f1[1][2]), run_time=1.0)
        circle_out(C_AK, A("secret witness"), seed=5)
        self.pad_to(A("instance carries") - 0.2)
        self.play(Indicate(f1[1][2], color=GOLD, scale_factor=1.08), run_time=0.8)

        # reason 2
        self.pad_to(A("second reason") - 0.3)
        self.play(FadeIn(f2[0], shift=LEFT * 0.25), f1.animate.fade(0.45),
                  *[FadeOut(c) for c in live], run_time=0.7)
        live.clear()
        circle_out(C_ADDR, A("the address does"), seed=11)
        reveal(f2[1][0], A("carries the transmission"))
        self.pad_to(A("diversified addresses") - 0.2)
        c_div = pix_contour(crop, CROP_DIMS, C_DIVERS, seed=17, stroke_width=4.0, buff=0.1)
        self.play(ShowCreation(c_div), FadeOut(live.pop()), FadeIn(f2[1][1][0], shift=LEFT * 0.15),
                  run_time=0.8)
        live.append(c_div)
        reveal(f2[1][1][1], A("single incoming"))
        circle_out(C_DKIVK, A("detect every"), seed=23)

        # reason 3
        self.pad_to(A("third reason") - 0.3)
        self.play(FadeIn(f3[0], shift=LEFT * 0.25), f2.animate.fade(0.45),
                  *[FadeOut(c) for c in live], run_time=0.7)
        live.clear()
        reveal(f3[1][0], A("without handing"))
        self.pad_to(A("outgoing viewing key") - 0.2)
        cm = pix_contour(crop, CROP_DIMS, C_OVK, seed=29, stroke_width=4.0)
        live.append(cm)
        self.play(ShowCreation(cm), FadeIn(f3[1][1][0], shift=LEFT * 0.15), run_time=0.7)
        reveal(f3[1][1][1], A("viewing family"))

        # which keys enforce ownership? only two.
        self.pad_to(A("look at the diagram") - 0.2)
        self.play(FadeOut(forces, shift=UP * 0.15), *[FadeOut(c) for c in live], run_time=0.8)
        live.clear()
        who = label("which keys enforce ownership?", size=FS_HEAD, color=STAR, weight="BOLD")
        who.move_to([COL_X, 2.3, 0])
        self.pad_to(A("which of these") - 0.2)
        self.play(FadeIn(who, shift=DOWN * 0.15), run_time=0.7)
        self.pad_to(A("only two") - 0.3)
        d_ak = pix_dash(crop, CROP_DIMS, C_AK, stroke_width=3.2)
        d_nk = pix_dash(crop, CROP_DIMS, C_NK, stroke_width=3.2)
        self.play(ShowCreation(d_ak), ShowCreation(d_nk), run_time=0.6)

        def lift(target, box):
            c, w, h = pix(crop, CROP_DIMS, box)
            s = target.copy()
            s.set_height(h).move_to(c)
            return s

        ak = kbox(['"ak"'], PNG_FVK, size=42).move_to([1.85, 0.95, 0])
        nk = kbox(['"nk"'], PNG_FVK, size=42).move_to([4.35, 0.95, 0])
        ak_name = itex("authorizes spends", size=FS_LABEL, color=TXT).next_to(ak, DOWN, buff=0.22)
        nk_name = itex("derives nullifiers", size=FS_LABEL, color=TXT).next_to(nk, DOWN, buff=0.22)
        self.pad_to(A("nullifier key") - 0.2)
        self.play(ReplacementTransform(lift(nk, C_NK), nk), run_time=0.7)
        self.pad_to(A("derives nullifiers") - 0.1)
        self.play(FadeIn(nk_name, shift=UP * 0.1), run_time=0.5)
        self.pad_to(A("authorization key") - 0.2)
        self.play(ReplacementTransform(lift(ak, C_AK), ak), run_time=0.7)
        self.pad_to(A("authorizes spends") - 0.1)
        self.play(FadeIn(ak_name, shift=UP * 0.1), run_time=0.5)

        rest = label("everything else: transmission and viewing", size=FS_BODY, color=TXT)
        rest.move_to([COL_X, -1.35, 0])
        others = VGroup(*[kbox([t], col, size=24) for _, t, col in OTHER_KEYS]).arrange(RIGHT, buff=0.22)
        fit_in(others, (NOTES_X + 0.1, 6.6, -2.8, -1.9))
        others.set_y(-2.35)
        self.pad_to(A("everything else") - 0.2)
        self.play(FadeIn(rest, shift=UP * 0.1),
                  LaggedStart(*[ReplacementTransform(lift(k, C_OTHERS[n]), k)
                                for (n, _, _), k in zip(OTHER_KEYS, others)], lag_ratio=0.12),
                  run_time=1.3)
        self.pad_to(A("serves transmission") + 1.0)
        blade = make_blade()
        self.play(ShowCreation(blade), run_time=0.7, rate_func=rush_into)
        self.pad_to(scene_T(SID))


class Scene12(TimedScene):
    """1.2 — the cut, as two stacked bands split at the seam (layered, not peers)."""

    def construct(self):
        SID = "1.2"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731

        # reconstruct 1.1's last frame
        crop = ImageMobject(ZK_ORCHARD_PNG).set_height(CROP_H).move_to(CROP_POS)
        d_ak = pix_dash(crop, CROP_DIMS, C_AK, stroke_width=3.2)
        d_nk = pix_dash(crop, CROP_DIMS, C_NK, stroke_width=3.2)
        ak = kbox(['"ak"'], PNG_FVK, size=42).move_to([1.85, 0.95, 0])
        nk = kbox(['"nk"'], PNG_FVK, size=42).move_to([4.35, 0.95, 0])
        ak_name = itex("authorizes spends", size=FS_LABEL, color=TXT).next_to(ak, DOWN, buff=0.22)
        nk_name = itex("derives nullifiers", size=FS_LABEL, color=TXT).next_to(nk, DOWN, buff=0.22)
        who = label("which keys enforce ownership?", size=FS_HEAD, color=STAR, weight="BOLD").move_to([COL_X, 2.3, 0])
        rest = label("everything else: transmission and viewing", size=FS_BODY, color=TXT).move_to([COL_X, -1.35, 0])
        others = VGroup(*[kbox([t], col, size=24) for _, t, col in OTHER_KEYS]).arrange(RIGHT, buff=0.22)
        fit_in(others, (NOTES_X + 0.1, 6.6, -2.8, -1.9))
        others.set_y(-2.35)
        blade = make_blade()
        self.add(crop, d_ak, d_nk, ak, nk, ak_name, nk_name, who, rest, others, blade)

        # --- the knife becomes the seam: core above, payment below -------------------
        core, pay, core_head, pay_head, core_def, pay_def, seam = bands()
        self.pad_to(A("cuts along") - 0.2)
        self.play(crop.animate.shift(LEFT * 7.5), VGroup(d_ak, d_nk).animate.shift(LEFT * 7.5),
                  FadeOut(who, shift=UP * 0.2), ReplacementTransform(blade, seam),
                  VGroup(ak, nk, ak_name, nk_name).animate.shift([-COL_X, 0.05, 0]),
                  rest.animate.move_to([0, -1.75, 0]), others.animate.move_to([0, -2.7, 0]),
                  run_time=1.2)
        self.remove(crop, d_ak, d_nk)
        self.pad_to(A("on one side") - 0.2)
        self.play(ShowCreation(core), FadeIn(core_head, shift=RIGHT * 0.2), run_time=0.8)
        self.pad_to(A("bind every") - 0.2)
        self.play(FadeIn(core_def, shift=LEFT * 0.15), run_time=0.6)
        self.pad_to(A("other side") - 0.2)
        self.play(ShowCreation(pay), FadeIn(pay_head, shift=RIGHT * 0.2), run_time=0.8)
        self.pad_to(A("everything about") - 0.2)
        self.play(FadeIn(pay_def, shift=LEFT * 0.15), FadeOut(rest, shift=DOWN * 0.15),
                  LaggedStart(*[FadeOut(k, shift=DOWN * 0.2) for k in others], lag_ratio=0.08), run_time=0.8)
        names = ["addresses", "memo encryption", "note discovery", "viewing"]
        services = VGroup(*[key_chip(t, color=CYAN, size=FS_BODY, pad=0.18) for t in names])
        services[1].move_to([-0.95, -1.85, 0], aligned_edge=RIGHT)
        services[0].next_to(services[1], LEFT, buff=0.45)
        services[2].move_to([0.95, -1.85, 0], aligned_edge=LEFT)
        services[3].next_to(services[2], RIGHT, buff=0.45)
        for item, cue in zip(services, ["addresses", "memo", "discovery", "viewing"]):
            self.pad_to(A(cue) - 0.15)
            self.play(FadeIn(item, shift=UP * 0.15), run_time=0.45)

        # --- (ak, nk) -> pk = Com(ak, nk) ----------------------------------------------------
        aknk = kbox(['"ak"', '"nk"'], PNG_FVK, size=34).move_to([0, 0.8, 0])
        self.pad_to(A("owner field") - 0.3)
        self.play(ReplacementTransform(ak[0], aknk[0]), Transform(nk[0], aknk[0].copy(), remover=True),
                  ReplacementTransform(ak[1][0], aknk[1][0]), ReplacementTransform(nk[1][0], aknk[1][1]),
                  ak_name.animate.next_to(aknk, LEFT, buff=0.4), nk_name.animate.next_to(aknk, RIGHT, buff=0.4),
                  run_time=0.9)
        pk = kbox(['"pk"'], PNG_ADDR, size=34).move_to([0, 2.35, 0])
        ak_pk = karrow(aknk[0].get_top(), pk[0].get_bottom())
        pk_eq = mtex('"pk" = "Com"("ak", "nk")', size=FS_HEAD, color=GOLD).next_to(pk, RIGHT, buff=0.55)
        pk_name = itex("payment key", size=FS_LABEL, color=TXT).next_to(pk, LEFT, buff=0.4)
        self.pad_to(A("payment key") - 0.3)
        self.play(FadeIn(pk, scale=1.2), ShowCreation(ak_pk), FadeIn(pk_name), run_time=0.7)
        self.pad_to(A("binding commitment") - 0.2)
        self.play(Write(pk_eq), run_time=0.9)

        # two favors of a hash commitment
        self.pad_to(A("built from") - 0.25)
        self.play(FadeOut(VGroup(ak_name, nk_name)), run_time=0.45)
        favors = bullets(["one succinct owner field", "quantum-recoverable today"], size=FS_BODY, color=STAR)
        favors.move_to([1.3, 1.35, 0], aligned_edge=UL)
        ring = contour(pk_eq, color=GOLD, buff=0.2, seed=41, stroke_width=SW)
        self.pad_to(A("succinct") - 0.3)
        self.play(ShowCreation(ring), FadeIn(favors[0], shift=RIGHT * 0.2), run_time=0.6)
        self.pad_to(A("quantum") - 0.3)
        self.play(FadeIn(favors[1], shift=RIGHT * 0.2), run_time=0.55)
        bare = VGroup(label("bare", size=FS_BODY, color=FLARE),
                      tex_chip('"ak"', color=FLARE, size=FS_BODY)).arrange(RIGHT, buff=0.2)
        bare.move_to([-6.2, 2.3, 0], aligned_edge=LEFT)
        risk = label("harvest now,\ndecrypt later", size=FS_BODY, color=FLARE, weight="BOLD")
        risk.next_to(bare, DOWN, buff=0.3, aligned_edge=LEFT)
        self.pad_to(A("handing") - 0.3)
        self.play(FadeIn(bare, shift=RIGHT * 0.15), run_time=0.55)
        self.pad_to(A("harvest") - 0.3)
        xx = strike(bare[1])
        self.play(ShowCreation(xx), FadeIn(risk, shift=UP * 0.1), run_time=0.7)
        self.pad_to(A("hash commitment to it") - 0.3)
        safe = VGroup(checkmark(0.34, GOLD), label("a hash commitment\nreveals neither key", size=FS_BODY,
                                                   color=GOLD, weight="BOLD")).arrange(RIGHT, buff=0.25)
        safe.move_to([-6.2, 0.95, 0], aligned_edge=LEFT)
        self.play(FadeOut(VGroup(bare, xx, risk)), FadeIn(safe), Indicate(pk_eq, color=GOLD, scale_factor=1.08),
                  run_time=0.75)

        # wallets define the derivation underneath; ak, nk cross the seam
        hd = VGroup(dashed_box(w=2.3, h=0.6, color=CYAN, stroke_width=2.4),
                    label("HD wallet", size=FS_LABEL, color=STAR)).move_to([0, -2.72, 0])
        sk = kbox(['"sk"'], PNG_SK, size=24).next_to(hd, LEFT, buff=0.75)
        sk_hd = karrow(sk[0].get_right(), hd[0].get_left() + LEFT * 0.03)
        hd_top, kb_bot = hd[0].get_top()[1] + 0.03, aknk[0].get_bottom()[1]
        hd_ak, hd_nk = [karrow(np.array([g.get_x(), hd_top, 0]), np.array([g.get_x(), kb_bot, 0])) for g in aknk[1]]
        self.pad_to(A("doesn't even|doesnt even") - 0.2)
        self.play(FadeIn(sk, shift=UP * 0.1), ShowCreation(sk_hd), FadeIn(hd), run_time=0.7)
        self.play(ShowCreation(hd_ak), ShowCreation(hd_nk), run_time=0.7)
        looks = itex("only rule: look freshly sampled", size=FS_LABEL, color=GOLD).move_to([3.6, -0.2, 0])
        self.pad_to(A("freshly sampled") - 0.3)
        self.play(FadeIn(looks, shift=UP * 0.1), Indicate(seam, color=STAR, scale_factor=1.0), run_time=0.6)
        deriv = itex("wallet standards (ZIP-32)", size=FS_LABEL, color=CYAN).next_to(hd, RIGHT, buff=0.45)
        self.pad_to(A("derivation paths") - 0.2)
        self.play(FadeIn(deriv, shift=LEFT * 0.15), run_time=0.6)

        # --- security properties sort across the seam ----------------------------------------
        ownership = VGroup(aknk, pk, ak_pk, pk_eq, pk_name, ring, favors, safe, services, hd, sk, deriv,
                           sk_hd, hd_ak, hd_nk, looks)
        texts = ["ledger indistinguishability", "balance", "note privacy", "unlinkability vs payment key",
                 "unlinkability vs ivk holder", "Faerie-gold resistance"]
        loose = VGroup(*[prop_chip(t, TXT) for t in texts])
        grid = [[1, 0, 5], [2, 3, 4]]
        col_w = [max(loose[grid[r][c]].get_width() for r in range(2)) for c in range(3)]
        gap = 0.45
        x = -(sum(col_w) + 2 * gap) / 2
        col_x = []
        for w in col_w:
            col_x.append(x + w / 2)
            x += w + gap
        for r, y in enumerate([1.8, 0.62]):
            for c in range(3):
                loose[grid[r][c]].move_to([col_x[c], y, 0])
        finals = VGroup(*[prop_chip(t, GOLD if i < 4 else CYAN) for i, t in enumerate(texts)])
        for i in range(4):
            finals[i].move_to(loose[i])
        finals[4].move_to([-1.9, -2.3, 0])
        finals[5].move_to([2.6, -2.3, 0])
        self.pad_to(A("security properties") - 0.6)
        self.play(FadeOut(ownership, lag_ratio=0.02), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(loose[i], scale=0.92) for i in (1, 0, 5, 2, 3, 4)], lag_ratio=0.1),
                  run_time=0.9)
        for i, cue in zip(range(4), ["ledger", "balance", "note privacy", "spend unlinkability"]):
            self.pad_to(A(cue) - 0.2)
            self.play(ReplacementTransform(loose[i], finals[i]), run_time=0.5)
        self.pad_to(A("full unlinkability") - 0.2)
        self.play(ReplacementTransform(loose[4], finals[4]), run_time=0.9)
        self.pad_to(A("resistance") - 0.2)
        self.play(ReplacementTransform(loose[5], finals[5]), run_time=0.9)
        self.pad_to(A("payment protocol's job|payment protocols job") - 0.2)
        self.play(Indicate(VGroup(finals[4], finals[5]), color=CYAN, scale_factor=1.03), run_time=0.6)

        # --- the chain's role splits too: DA layer --------------------------------------------
        # the chain is shielded-side infrastructure (upper band); the payload is the payment
        # protocol's (lower band) and rides up into a block, never parsed
        blocks = VGroup(*[block(w=1.1, h=0.66) for _ in range(8)]).arrange(RIGHT, buff=0.42).move_to([0, 0.45, 0])
        links = VGroup(*[chain_link(blocks[i], blocks[i + 1]) for i in range(7)])
        chain_label = label("the chain: a data-availability layer", size=FS_BODY, color=GOLD).move_to([0, 1.35, 0])
        cipher = tex_chip('mono("9f c3 07 4a 1c")', color=CYAN, size=FS_BODY).move_to([2.6, -2.25, 0])
        cipher_tag = itex("encrypted payment data", size=FS_LABEL, color=CYAN).next_to(cipher, LEFT, buff=0.35)
        self.pad_to(A("chain's role|chains role") - 0.3)
        self.play(FadeOut(finals), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(b, shift=LEFT * 0.2) for b in blocks], lag_ratio=0.08),
                  LaggedStart(*[ShowCreation(l) for l in links], lag_ratio=0.08), run_time=1.0)
        self.pad_to(A("data availability") - 0.3)
        self.play(FadeIn(chain_label), run_time=0.5)
        self.pad_to(A("encrypted payment") - 0.3)
        self.play(FadeIn(cipher, scale=1.15), FadeIn(cipher_tag), run_time=0.6)
        landed = blocks[5].copy().set_fill(CYAN, 0.45).set_stroke(CYAN, SW, 1.0)
        self.pad_to(A("rides") - 0.2)
        self.play(FadeOut(cipher_tag), run_time=0.3)
        self.play(cipher.animate.scale(0.45).move_to(blocks[5]).set_opacity(0),
                  FadeIn(landed, rate_func=squish_rate_func(smooth, 0.5, 1.0)), run_time=1.0)
        self.remove(cipher)
        blind = label("the core carries it, never parses it", size=FS_HEAD, color=GOLD, weight="BOLD").move_to([0, 2.3, 0])
        self.pad_to(A("carries those") - 0.3)
        self.play(FadeIn(blind, shift=DOWN * 0.15), Indicate(landed, color=CYAN), run_time=0.7)

        # --- two familiar pieces don't change ---------------------------------------------------
        mech_head = label("unchanged mechanisms", size=FS_HEAD, color=STAR, weight="BOLD").move_to([0, 2.45, 0])
        row1 = VGroup(key_chip("RedPallas spend authorization", color=GOLD, size=FS_BODY, pad=0.18),
                      itex("under", size=FS_LABEL, color=TXT),
                      tex_chip('"rk" = ["ask" + alpha] thin G', color=GOLD, size=FS_BODY)).arrange(RIGHT, buff=0.3)
        row2 = VGroup(key_chip("binding signature", color=GOLD, size=FS_BODY, pad=0.18),
                      itex("over", size=FS_LABEL, color=TXT),
                      key_chip("homomorphic value commitments", color=GOLD, size=FS_BODY, pad=0.18)).arrange(RIGHT, buff=0.3)
        body = VGroup(row1, row2).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_in(body, (-6.4, 6.4, 0.35, 1.95))
        self.pad_to(A("familiar") - 0.4)
        self.play(FadeOut(VGroup(blocks, links, landed, chain_label, blind)), run_time=0.5)
        self.play(FadeIn(mech_head, shift=DOWN * 0.15), run_time=0.5)
        self.pad_to(A("spend authorization") - 0.2)
        self.play(FadeIn(row1, shift=RIGHT * 0.15), run_time=0.7)
        self.pad_to(A("value balance") - 0.2)
        self.play(FadeIn(row2, shift=RIGHT * 0.15), run_time=0.7)
        self.pad_to(A("exactly as") - 0.2)
        same = itex("exactly as in Sapling and Orchard", size=FS_LABEL, color=MUT).next_to(body, DOWN, buff=0.22)
        self.play(FadeIn(same), run_time=0.5)

        # --- what the cut buys ---------------------------------------------------------------------
        core_box, core_name, stable, modules, evolve = cut_buys()
        self.pad_to(A("so what") - 0.1)
        self.play(FadeOut(VGroup(mech_head, body, same), shift=UP * 0.15), run_time=0.6)
        self.pad_to(A("smaller surface") - 0.3)
        self.play(FadeIn(core_box, scale=1.05), FadeIn(core_name, scale=1.05), run_time=0.65)
        self.pad_to(A("cleaner") - 0.3)
        self.play(FadeIn(stable, shift=UP * 0.1), run_time=0.55)
        self.pad_to(A("two halves") - 0.35)
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.2) for m in modules], lag_ratio=0.25),
                  FadeIn(evolve, shift=UP * 0.1), run_time=0.9)
        self.pad_to(scene_T(SID))


class Scene13(TimedScene):
    def construct(self):
        SID = "1.3"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731

        core, pay, core_head, pay_head, core_def, pay_def, seam = bands()
        core_box, core_name, stable, modules, evolve = cut_buys()
        frame12 = VGroup(core, pay, core_head, pay_head, core_def, pay_def, seam, stable, modules, evolve)
        self.add(frame12, core_box, core_name)
        card = note_card(filled=False, size=FS_HEAD, slot_w=1.5, slot_h=1.0).move_to(UP * 1.25)
        title = scene_title("A Tachyon note")
        self.wait(0.3)
        self.play(FadeOut(VGroup(frame12, core_name), lag_ratio=0.02), run_time=0.8)
        self.pad_to(A("here's the note|heres the note") - 0.3)
        self.play(ReplacementTransform(core_box, card.frame), FadeIn(card.slots, lag_ratio=0.1), Write(title),
                  run_time=1.2)
        names = ["payment key", "value", "psi", "trapdoor"]
        cues = ["payment key", "value", "field called", "trapdoor"]
        cap = VGroup()
        for i, (cue, nm) in enumerate(zip(cues, names)):
            self.pad_to(A(cue) - 0.15)
            t = card.texts[i]
            lab = label(nm if nm != "psi" else "note identity", size=FS_LABEL, color=MUT)
            lab.next_to(card.slots[i], DOWN, buff=0.22)
            cap.add(lab)
            self.play(t.animate.set_opacity(1), FadeIn(lab, shift=UP * 0.1), run_time=0.5)

        # cm = Com(pk, v, psi; rcm), Poseidon
        self.pad_to(A("its commitment") - 0.2)
        cm = mtex('"cm" = "Com"("pk", v, psi; "rcm")', size=FS_HEAD, color=STAR).move_to(DOWN * 0.55 + LEFT * 0.9)
        self.play(FadeOut(cap), TransformFromCopy(card.texts, cm), run_time=1.2)
        self.pad_to(A("poseidon") - 0.3)
        sp = sponge_icon(1.6, 0.9, color=GOLD)
        sp.remove(sp[2])
        sp_lab = label("Poseidon", size=FS_LABEL, color=GOLD).next_to(sp, DOWN, buff=0.12)
        sp.add(sp_lab)
        sp.next_to(cm, RIGHT, buff=0.6)
        self.play(FadeIn(sp, shift=LEFT * 0.2), run_time=0.7)
        self.pad_to(A("purely symmetric") - 0.2)
        sym = label("purely symmetric", size=FS_BODY, color=GOLD).next_to(cm, DOWN, buff=0.35)
        self.play(FadeIn(sym, shift=UP * 0.1), run_time=0.6)

        # contrast: Sapling / Orchard
        self.pad_to(A("compare") - 0.2)
        old = VGroup(label("Sapling / Orchard: Pedersen-style", size=FS_BODY, color=TXT),
                     mtex('"cm" = [v] G + ["rcm"] H + dots', size=FS_BODY, color=TXT)).arrange(DOWN, buff=0.22)
        old.move_to(DOWN * 2.45 + LEFT * 0.9)
        self.play(FadeIn(old, shift=UP * 0.15), run_time=0.8)
        self.pad_to(A("discrete log") - 0.2)
        dl = label("discrete log", size=FS_LABEL, color=FLARE).next_to(old, RIGHT, buff=0.5)
        self.play(FadeIn(dl), run_time=0.5)
        self.pad_to(A("extra rules") - 0.2)
        rules = label("+ wallet rules on rcm", size=FS_LABEL, color=FLARE).next_to(dl, DOWN, buff=0.15).align_to(dl, LEFT)
        self.play(FadeIn(rules), run_time=0.5)
        self.pad_to(A("doesn't need|doesnt need") - 0.3)
        self.play(VGroup(old, dl, rules).animate.fade(0.6), Indicate(sym, color=GOLD), run_time=0.8)

        # that leaves psi
        self.pad_to(A("that leaves") - 0.2)
        self.play(FadeOut(VGroup(old, dl, rules)), run_time=0.5)
        psi_slot = card.slots[2]
        hl = SurroundingRectangle(psi_slot, buff=0.06).set_stroke(GOLD, SW_BOLD)
        self.play(ShowCreation(hl), card.texts[2].animate.set_color(GOLD), run_time=0.6)
        self.pad_to(A("pseudo") - 0.2)
        ident = label("pseudorandom note identity, from the wallet's master key", size=FS_LABEL, color=GOLD)
        ident.next_to(card, UP, buff=0.3)
        self.play(FadeOut(title), FadeIn(ident, shift=DOWN * 0.1), run_time=0.7)
        self.pad_to(A("hold on") - 0.2)
        self.play(Indicate(card.texts[2], color=GOLD, scale_factor=1.3), run_time=0.8)
        # every nullifier hangs off psi: faint future beads
        self.pad_to(A("every nullifier") - 0.2)
        rail = EpochRail(first=4, last=10)
        beads = VGroup(*[bead(FLARE, r=0.1).move_to(rail.center_of(e)) for e in range(4, 11)])
        threads = VGroup(*[Line(psi_slot.get_bottom(), b.get_center(), stroke_color=FLARE,
                                stroke_width=SW_THIN, stroke_opacity=0.45) for b in beads])
        self.play(FadeOut(VGroup(sym, sp)), cm.animate.set_opacity(0), FadeIn(rail),
                  LaggedStart(*[ShowCreation(t) for t in threads], lag_ratio=0.08),
                  LaggedStart(*[FadeIn(b, scale=0.4) for b in beads], lag_ratio=0.08), run_time=1.4)

        # so where does cm go?
        self.pad_to(A("note exists") - 0.2)
        self.play(FadeOut(VGroup(threads, beads, rail, ident, hl)), card.texts[2].animate.set_color(STAR),
                  cm.animate.set_opacity(1).move_to(ORIGIN), run_time=0.8)
        self.pad_to(A("where does") - 0.2)
        q = label("where does it go?", size=FS_HEAD, color=STAR).next_to(cm, DOWN, buff=0.45)
        self.play(FadeOut(card, shift=UP * 0.2), FadeIn(q, shift=UP * 0.1),
                  Indicate(cm, color=GOLD), run_time=1.0)
        self.pad_to(scene_T(SID))

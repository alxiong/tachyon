"""Act 1 — the two separations. Anchored to anim/words.json phrase timestamps.

Scene11 shows the actual spec diagram (book/src/assets/zcash_keys.png) as a raster
image — the audience has seen this exact figure — and highlights components by
pixel-coordinate overlays (contours / dashed boxes), never by dimming the raster.
Scene12 carves the tachyon_keys.svg tree out of Orchard's ak/nk and builds the
shielded/payment split around it.

Render:  manimgl act1.py Scene11 Scene12 Scene13 -w
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manimlib import *
from style import *

ASSETS = "/home/alex/work/tachyon_wt1/video/assets"
ZK_PNG = "/home/alex/work/tachyon_wt1/book/src/assets/zcash_keys.png"
ZK_ORCHARD_PNG = os.path.join(ASSETS, "zcash_keys_orchard.png")

# ---- pixel-space regions (original raster coordinates, y down) ---------------
FULL_DIMS = (2020.0, 828.0)
CROP_DIMS = (670.0, 770.0)  # crop box (1320, 30)-(1990, 800) of the full png

SPROUT_KEYS = (215, 175, 432, 348)
SPROUT_PANEL = (55, 40, 600, 730)
SAPLING_PANEL = (600, 40, 1285, 800)   # inside the ink gutters (585-605, 1270-1328)
ORCHARD_PANEL = (1312, 35, 1978, 800)

# Orchard components in full-image space
O_ADDR = (1510, 182, 1773, 237)
O_INDEX = (1480, 243, 1545, 268)
O_DKIVK = (1508, 286, 1702, 341)
O_OVK = (1737, 286, 1808, 341)
O_AK = (1535, 443, 1607, 493)
O_NK = (1624, 442, 1697, 494)
O_RIVK = (1715, 442, 1796, 494)
O_ASK = (1517, 591, 1608, 646)
O_SK = (1621, 695, 1705, 751)


def crop_box(full_box):
    x0, y0, x1, y1 = full_box
    return (x0 - 1320, y0 - 30, x1 - 1320, y1 - 30)


C_ADDR, C_INDEX, C_DKIVK, C_OVK = map(crop_box, (O_ADDR, O_INDEX, O_DKIVK, O_OVK))
C_AK, C_NK, C_RIVK, C_ASK, C_SK = map(crop_box, (O_AK, O_NK, O_RIVK, O_ASK, O_SK))
C_DIVERS = (196, 148, 266, 240)  # crop space: the d slot + "index" (clear of "Diversifier")
# the non-ownership keys, crop space (sources for the "everything else" row)
C_OTHERS = {"d": (203, 158, 252, 202), "pkd": (372, 158, 442, 202),
            "dk": (198, 258, 252, 305), "ivk": (316, 258, 378, 305),
            "ovk": (408, 255, 480, 310), "rivk": (398, 413, 478, 462)}
CROP_SRC = (1320, 30, 1990, 800)  # where the crop lives in the full raster


def pix(img, dims, box):
    """Map a raster-pixel box onto a placed ImageMobject: (center, w, h)."""
    x0, y0, x1, y1 = box
    W, H = dims
    ul = img.get_corner(UL)
    w, h = img.get_width(), img.get_height()
    c = np.array([ul[0] + (x0 + x1) / 2 / W * w,
                  ul[1] - (y0 + y1) / 2 / H * h, 0])
    return c, (x1 - x0) / W * w, (y1 - y0) / H * h


def pix_rect(img, dims, box, color=GOLD, buff=0.08, stroke_width=3.0):
    c, w, h = pix(img, dims, box)
    r = RoundedRectangle(width=w + 2 * buff, height=h + 2 * buff, corner_radius=0.1)
    r.set_fill(opacity=0)
    r.set_stroke(color, stroke_width, 1.0)
    r.move_to(c)
    return r


def pix_contour(img, dims, box, seed=3, color=GOLD, buff=0.14, **kw):
    c, w, h = pix(img, dims, box)
    return contour(center=c, w=w + 2 * buff, h=h + 2 * buff, seed=seed,
                   color=color, **kw)


def pix_dash(img, dims, box, color=GOLD, buff=0.08, **kw):
    c, w, h = pix(img, dims, box)
    return dashed_box(center=c, w=w + 2 * buff, h=h + 2 * buff, color=color, **kw)


# ---- shared layout -----------------------------------------------------------
# Scene11: the Orchard crop fills the left of the stage; the three forces read
# beside it. Its last frame ends on a horizontal knife at SEAM_Y between the two
# ownership keys (above) and everything else (below). Scene12 opens on that frame
# and simply extends the knife into the seam between the two protocol bands.
CROP_H = 6.2
CROP_POS = np.array([-6.6 + 0.5 * CROP_H * CROP_DIMS[0] / CROP_DIMS[1], -0.3, 0])
NOTES_X = -0.75                     # left edge of the text column beside the crop
COL_X = 3.0                         # center of that column
AK_POS = np.array([1.85, 0.95, 0])  # ak left of nk, as in the figure
NK_POS = np.array([4.35, 0.95, 0])

SEAM_Y = -0.615
PAY_TOP_Y = -1.12                   # heading row of the payment band
HEAD_Y = 3.33                       # heading row of the core band
OTHER_KEYS = [("d", '"d"', PNG_ADDR), ("pkd", '"pk"_"d"', PNG_ADDR),
              ("dk", '"dk"', PNG_IVK), ("ivk", '"ivk"', PNG_IVK),
              ("ovk", '"ovk"', PNG_OVK), ("rivk", '"rivk"', PNG_FVK)]


def strike(mob, color=FLARE):
    """Deliberate strike-through (a polyline, so the layout linter ignores it)."""
    vm = VMobject()
    vm.set_points_as_corners([mob.get_corner(DL) + 0.08 * DL, mob.get_corner(UR) + 0.08 * UR])
    vm.set_stroke(color, SW_BOLD, 1.0)
    return vm


def xmark(size=0.26, color=FLARE):
    """A small hand-set ✗ (two polylines; not a Line, not a font glyph)."""
    a, b = VMobject(), VMobject()
    a.set_points_as_corners([size * (UL / 2), size * (DR / 2)])
    b.set_points_as_corners([size * (UR / 2), size * (DL / 2)])
    g = VGroup(a, b)
    g.set_stroke(color, SW, 1.0)
    return g


def orchard_crop():
    crop = ImageMobject(ZK_ORCHARD_PNG)
    crop.set_height(CROP_H)
    crop.move_to(CROP_POS)
    return crop


def two_keys():
    """The two ownership keys pulled out of the figure, with their names."""
    ak = kbox(['"ak"'], PNG_FVK, size=42).move_to(AK_POS)
    nk = kbox(['"nk"'], PNG_FVK, size=42).move_to(NK_POS)
    ak_name = itex("authorization key", size=FS_LABEL, color=TXT).next_to(ak, DOWN, buff=0.22)
    nk_name = itex("nullifier key", size=FS_LABEL, color=TXT).next_to(nk, DOWN, buff=0.22)
    return ak, nk, ak_name, nk_name


def ownership_head():
    return label("who may spend?", size=FS_HEAD, color=STAR, weight="BOLD").move_to(
        [COL_X, 2.3, 0])


def else_line():
    return label("everything else: moving or viewing notes", size=FS_BODY,
                 color=TXT).move_to([COL_X, -1.35, 0])


def other_keys():
    row = VGroup(*[kbox([t], c, size=24) for _, t, c in OTHER_KEYS])
    row.arrange(RIGHT, buff=0.22)
    fit_in(row, (NOTES_X + 0.1, 6.6, -2.8, -1.9))
    row.set_y(-2.35)
    return row


def make_blade():
    return Line([NOTES_X + 0.1, SEAM_Y, 0], [6.6, SEAM_Y, 0], stroke_width=SW_BOLD,
                stroke_color=GOLD)


def force_block(n, head, rows):
    """A numbered force: gold badge + headline, then indented support rows."""
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
    """A gold formula with a short gray gloss beside it, on one baseline-ish row."""
    return VGroup(eq, note).arrange(RIGHT, buff=0.45, aligned_edge=DOWN)


class Scene11(TimedScene):
    """1.1 — Why Zcash keys got complicated (over the real spec figure)."""

    def construct(self):
        A = lambda p, o=1: anchor("1.1", p, o)
        AA = lambda ps, o=1: anchor_any("1.1", ps, o)

        # the figure everyone has seen, straight from the spec, as big as the stage;
        # it eases in a slow push while the opening sentences set up the question
        full = ImageMobject(ZK_PNG)
        full.set_width(13.4 * 0.955)
        full.move_to(DOWN * 0.05)
        self.wait(0.5)
        self.play(FadeIn(full, scale=1.03), run_time=1.6)
        title = scene_title("why do Zcash keys keep getting more complicated?")
        t_title = A("why do zcash") - 0.15
        self.play(full.animate.set_width(13.4).move_to(DOWN * 0.05),
                  run_time=t_title - self.time - 0.05, rate_func=smooth)
        self.pad_to(t_title)
        self.play(Write(title), run_time=1.6)

        def flash(box, t, hold=0.75, color=GOLD, out=True):
            self.pad_to(t - 0.15)
            r = pix_rect(full, FULL_DIMS, box, color=color, stroke_width=4.0)
            self.play(ShowCreation(r), run_time=0.35)
            if out:
                self.wait(hold - 0.35)
                self.play(FadeOut(r), run_time=0.3)
            return r

        # Sprout: just two keys
        flash(SPROUT_KEYS, A("sprout needed"), hold=2.2)
        # "By Sapling, the diagram has grown ..."
        flash(SAPLING_PANEL, A("by sapling"), hold=1.3)
        # ... and the key families get named on Orchard, the baseline going forward
        flash((O_ASK[0], O_ASK[1], O_SK[2], O_SK[3]), A("spending keys"), hold=1.1)
        flash(O_AK, A("authorization keys"), hold=1.0)
        flash(O_NK, A("nullifier keys"), hold=1.0)
        flash((O_DKIVK[0], O_DKIVK[1], O_OVK[2], O_OVK[3]), A("viewing keys"), hold=0.9)
        flash((O_INDEX[0], O_ADDR[1], O_ADDR[2], O_INDEX[3]), A("diversifiers"), hold=0.8)
        orch_rect = flash(ORCHARD_PANEL, A("orchard inherits"), out=False)

        # zoom: lift the Orchard panel out, Sprout and Sapling bow out with it
        crop = ImageMobject(ZK_ORCHARD_PNG)
        c, w, h = pix(full, FULL_DIMS, CROP_SRC)
        crop.set_height(h)
        crop.move_to(c)
        self.pad_to(A("worth naming") - 0.2)
        self.add(crop)
        self.play(crop.animate.set_height(CROP_H).move_to(CROP_POS),
                  FadeOut(full), FadeOut(orch_rect), run_time=1.6)

        # the three forces, numbered, in one text column beside the figure.
        # Each force: a prose reason, then a gold formula/key with a short gloss.
        f1 = force_block(1, "proving ≠ authorizing", [
            label("hardware wallets can't prove, so spends get signed",
                  size=FS_BODY, color=TXT),
            mtex('"rk" = "ak" + [alpha] thin G', size=FS_HEAD, color=GOLD),
        ])
        f2 = force_block(2, "owning ≠ receiving", [
            label("the chain is the bulletin board: memos in-band",
                  size=FS_BODY, color=TXT),
            eq_row(mtex('"pk"_d = ["ivk"] thin g_d', size=FS_HEAD, color=GOLD),
                   mtex('fresh $d$, same $"ivk"$', size=FS_LABEL + 2, color=TXT, math=False)),
        ])
        f3 = force_block(3, "selective disclosure", [
            label("watching outgoing notes takes its own key",
                  size=FS_BODY, color=TXT),
            eq_row(mtex('"ovk"', size=FS_HEAD, color=GOLD),
                   label("and the rest of the viewing-key family", size=FS_LABEL + 2,
                         color=TXT)),
        ])
        forces = VGroup(f1, f2, f3).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_in(forces, (NOTES_X, 6.7, -3.3, 2.85), align=LEFT)
        # spread the three blocks over the full column height (no empty bottom)
        gap = (2.8 - (-3.25) - sum(f.get_height() for f in forces)) / 2
        forces.arrange(DOWN, buff=min(max(gap, 0.4), 1.2), aligned_edge=LEFT)
        forces.move_to([NOTES_X, 0, 0], aligned_edge=LEFT).align_to(UP * 2.8, UP)

        live_contours = []

        def circle_out(box, t, seed, run=0.7):
            self.pad_to(t - 0.2)
            cm = pix_contour(crop, CROP_DIMS, box, seed=seed, stroke_width=4.0)
            live_contours.append(cm)
            self.play(ShowCreation(cm), run_time=run)
            return cm

        def reveal(m, t, run=0.6):
            self.pad_to(t)
            self.play(FadeIn(m, shift=LEFT * 0.15), run_time=run)

        # force 1
        self.pad_to(A("first force") - 0.3)
        self.play(FadeIn(f1[0], shift=LEFT * 0.25), run_time=0.7)
        reveal(f1[1][0], AA(["snark proofs", "generate snark"]) - 0.3)
        self.pad_to(AA(["re randomize", "rerandomize"]) - 0.3)
        self.play(Write(f1[1][1]), run_time=1.0)
        circle_out(C_AK, A("witness"), seed=5)
        self.pad_to(A("public instance") - 0.4)
        self.play(Indicate(f1[1][1], color=GOLD, scale_factor=1.08), run_time=0.8)

        # force 2 — force 1 recedes so the eye follows the new line
        self.pad_to(A("second force") - 0.3)
        self.play(FadeIn(f2[0], shift=LEFT * 0.25), f1.animate.fade(0.45),
                  *[FadeOut(c) for c in live_contours], run_time=0.7)
        live_contours.clear()
        c_addr = circle_out(C_ADDR, AA(["address does both", "the address does"]), seed=11)
        reveal(f2[1][0], A("bulletin board") - 0.5, run=0.7)
        # the address contour hands off to the diversifier slot
        self.pad_to(A("diversified addresses") - 0.2)
        live_contours.remove(c_addr)
        c_div = pix_contour(crop, CROP_DIMS, C_DIVERS, seed=17, stroke_width=4.0, buff=0.1)
        live_contours.append(c_div)
        self.play(ShowCreation(c_div), FadeOut(c_addr), run_time=0.7)
        reveal(f2[1][1][0], A("transmission keys") - 0.3, run=0.7)
        reveal(f2[1][1][1], A("incoming viewing key") - 0.3, run=0.6)
        circle_out(C_DKIVK, A("scanning") - 0.6, seed=23, run=0.6)

        # force 3
        self.pad_to(A("third force") - 0.3)
        self.play(FadeIn(f3[0], shift=LEFT * 0.25), f2.animate.fade(0.45),
                  *[FadeOut(c) for c in live_contours], run_time=0.7)
        live_contours.clear()
        reveal(f3[1][0], A("letting someone") - 0.3)
        self.pad_to(A("outgoing viewing key") - 0.2)
        cm = pix_contour(crop, CROP_DIMS, C_OVK, seed=29, stroke_width=4.0)
        live_contours.append(cm)
        self.play(ShowCreation(cm), FadeIn(f3[1][1][0], shift=LEFT * 0.15), run_time=0.7)
        reveal(f3[1][1][1], A("family") - 0.4)

        # "step back": the forces recede together, the figure takes the eye again
        self.pad_to(A("step back") - 0.2)
        self.play(f3.animate.fade(0.45), *[FadeOut(c) for c in live_contours], run_time=0.8)
        live_contours.clear()

        # exactly two keys matter: ak and nk, dashed out of the figure
        who = ownership_head()
        self.pad_to(A("enforcing ownership") - 0.6)
        self.play(FadeOut(forces, shift=UP * 0.15), run_time=0.5)   # clear first ...
        self.play(FadeIn(who, shift=DOWN * 0.15), run_time=0.5)       # ... then the question
        self.pad_to(A("exactly two") - 0.4)
        dash_ak = pix_dash(crop, CROP_DIMS, C_AK, stroke_width=3.2)
        dash_nk = pix_dash(crop, CROP_DIMS, C_NK, stroke_width=3.2)
        self.play(ShowCreation(dash_ak), ShowCreation(dash_nk), lag_ratio=0.15, run_time=0.6)

        def lift(target, box):
            """A copy of `target` sized onto a raster box (same structure: clean morph)."""
            c, w, h = pix(crop, CROP_DIMS, box)
            s = target.copy()
            s.set_height(h)
            s.move_to(c)
            return s

        ak_big, nk_big, ak_name, nk_name = two_keys()
        self.pad_to(A("nullifier key") - 0.2)
        self.play(ReplacementTransform(lift(nk_big, C_NK), nk_big),
                  FadeIn(nk_name, shift=UP * 0.1), run_time=0.7)
        self.pad_to(A("authorization key") - 0.2)
        self.play(ReplacementTransform(lift(ak_big, C_AK), ak_big),
                  FadeIn(ak_name, shift=UP * 0.1), run_time=0.7)

        # everything else: the other keys leave the figure for the lower row
        rest, others = else_line(), other_keys()
        self.pad_to(A("everything else") - 0.2)
        self.play(FadeIn(rest, shift=UP * 0.1),
                  LaggedStart(*[ReplacementTransform(lift(k, C_OTHERS[n]), k)
                                for (n, _, _), k in zip(OTHER_KEYS, others)],
                              lag_ratio=0.12),
                  run_time=1.3)

        # the knife: one horizontal cut, ownership above, everything else below
        self.pad_to(A("the knife") - 0.3)
        blade = make_blade()
        self.play(ShowCreation(blade), run_time=0.7, rate_func=rush_into)
        self.pad_to(scene_T("1.1"))


# ---- Scene12 layout: two bands split at the seam -------------------------------
def bands():
    core = panel(13.5, 4.15, color=GOLD, fill_opacity=0.03).move_to([0, 1.62, 0])
    pay = panel(13.5, 2.95, color=CYAN, fill_opacity=0.03).move_to([0, -2.25, 0])
    core_head = heading("shielded core", size=FS_BODY, color=GOLD)
    core_head.move_to([-6.45, HEAD_Y, 0], aligned_edge=LEFT)
    pay_head = heading("payment protocol", size=FS_BODY, color=CYAN)
    pay_head.move_to([-6.45, PAY_TOP_Y, 0], aligned_edge=LEFT)
    core_def = itex("owns note identity and spend authority", size=FS_LABEL, color=TXT)
    core_def.move_to([6.45, HEAD_Y, 0], aligned_edge=RIGHT)
    pay_def = itex("delivers note data to recipients", size=FS_LABEL, color=TXT)
    pay_def.move_to([6.45, PAY_TOP_Y, 0], aligned_edge=RIGHT)
    seam = Line(LEFT * 6.55, RIGHT * 6.55, stroke_width=SW_BOLD, stroke_color=GOLD
                ).move_to(UP * SEAM_Y)
    return core, pay, core_head, pay_head, core_def, pay_def, seam


def cut_buys():
    """Scene12's last beat (also Scene13's opening frame)."""
    core_name = heading("a small, stable shielded core", size=FS_HEAD, color=GOLD)
    core_box = panel(core_name.get_width() + 1.0, 1.25, color=GOLD,
                     fill_opacity=0.1).move_to([0, 2.05, 0])
    core_name.move_to(core_box)
    stable = label("audited and upgraded on its own", size=FS_BODY, color=STAR).move_to(
        [0, 0.6, 0])
    modules = VGroup(*[key_chip(s, color=CYAN, size=FS_BODY) for s in
                       ["payment protocol A", "payment protocol B", "payment protocol C"]])
    modules.arrange(RIGHT, buff=0.7).move_to([0, -2.0, 0])
    evolve = label("free to evolve or compete, without touching consensus", size=FS_BODY,
                   color=CYAN).move_to([0, -3.05, 0])
    return core_box, core_name, stable, modules, evolve


def prop_chip(s, color):
    """Security-property chip with an opaque backing (it may sit over band edges)."""
    c = key_chip(s, color=color, size=FS_BODY, pad=0.18)
    back = c[0].copy().set_fill(VOID, 1.0).set_stroke(width=0)
    return VGroup(back, c)


class Scene12(TimedScene):
    """1.2 — Tachyon's ownership cut and its consequences, in two bands."""

    def construct(self):
        A = lambda p, o=1: anchor("1.2", p, o)
        AA = lambda ps, o=1: anchor_any("1.2", ps, o)

        # reconstruct Scene11's last frame
        title = scene_title("why do Zcash keys keep getting more complicated?")
        crop = orchard_crop()
        dash_ak = pix_dash(crop, CROP_DIMS, C_AK, stroke_width=3.2)
        dash_nk = pix_dash(crop, CROP_DIMS, C_NK, stroke_width=3.2)
        ak_big, nk_big, ak_name, nk_name = two_keys()
        who, rest, others, blade = ownership_head(), else_line(), other_keys(), make_blade()
        self.add(crop, dash_ak, dash_nk, ak_big, nk_big, ak_name, nk_name, who, rest,
                 others, blade, title)

        # the knife runs the full width and becomes the seam: core above, payment below
        core, pay, core_head, pay_head, core_def, pay_def, seam = bands()
        self.pad_to(A("separates") - 0.3)
        # (an ImageMobject fading over black washes out to a gray slab: slide it off)
        self.play(crop.animate.shift(LEFT * 7.5), VGroup(dash_ak, dash_nk).animate.shift(
                  LEFT * 7.5), FadeOut(VGroup(title, who), shift=UP * 0.2),
                  ReplacementTransform(blade, seam),
                  VGroup(ak_big, nk_big, ak_name, nk_name).animate.shift(
                      [-COL_X, 0.05, 0]),
                  rest.animate.move_to([0, -1.75, 0]),
                  others.animate.move_to([0, -2.7, 0]),
                  run_time=1.2)
        self.remove(crop, dash_ak, dash_nk)
        self.play(ShowCreation(core), ShowCreation(pay), FadeIn(core_head, shift=RIGHT * 0.2),
                  FadeIn(pay_head, shift=RIGHT * 0.2), run_time=1.0)

        # --- ownership: (ak, nk) -> pk
        aknk = kbox(['"ak"', '"nk"'], PNG_FVK, size=34).move_to([0, 0.8, 0])
        self.pad_to(A("shielded protocol keeps") - 0.2)
        self.play(FadeIn(core_def, shift=LEFT * 0.15), run_time=0.6)
        self.pad_to(A("two ownership") - 0.2)
        self.play(ReplacementTransform(ak_big[0], aknk[0]),
                  Transform(nk_big[0], aknk[0].copy(), remover=True),
                  ReplacementTransform(ak_big[1][0], aknk[1][0]),
                  ReplacementTransform(nk_big[1][0], aknk[1][1]),
                  ak_name.animate.next_to(aknk, LEFT, buff=0.4),
                  nk_name.animate.next_to(aknk, RIGHT, buff=0.4),
                  run_time=0.9)

        pk = kbox(['"pk"'], PNG_ADDR, size=34).move_to([0, 2.35, 0])
        ak_pk = karrow(aknk[0].get_top(), pk[0].get_bottom())
        pk_eq = mtex('"pk" = "Com"("ak", "nk")', size=FS_HEAD, color=GOLD)
        pk_eq.next_to(pk, RIGHT, buff=0.55)
        pk_name = itex("payment key", size=FS_LABEL, color=TXT).next_to(pk, LEFT, buff=0.4)
        self.pad_to(AA(["owner feel", "owner field"]) - 0.3)
        self.play(FadeIn(pk, scale=1.2), ShowCreation(ak_pk), FadeIn(pk_name), run_time=0.7)
        self.pad_to(AA(["binding hash", "a binding"]) - 0.2)
        self.play(Write(pk_eq), run_time=0.9)
        self.pad_to(A("authorization key") - 0.15)
        self.play(Indicate(aknk[1][0], color=PNG_INK, scale_factor=1.3),
                  Indicate(ak_name, color=GOLD, scale_factor=1.05), run_time=0.6)
        self.pad_to(A("nullifier key") - 0.15)
        self.play(Indicate(aknk[1][1], color=PNG_INK, scale_factor=1.3),
                  Indicate(nk_name, color=GOLD, scale_factor=1.05), run_time=0.6)

        # --- the payment protocol takes custody of the rest
        self.pad_to(A("takes custody") - 0.3)
        self.play(FadeIn(pay_def, shift=LEFT * 0.15), FadeOut(rest, shift=DOWN * 0.15),
                  LaggedStart(*[FadeOut(k, shift=DOWN * 0.2) for k in others],
                              lag_ratio=0.08), run_time=0.8)
        names = ["addresses", "memo encryption", "note discovery", "viewing"]
        phrases = ["addresses", "memo encryption", "note discovery", "viewing capabilities"]
        services = VGroup(*[key_chip(s, color=CYAN, size=FS_BODY, pad=0.18) for s in names])
        # two left of center, two right, leaving a lane up the middle for the derivation
        services[1].move_to([-0.95, -1.85, 0], aligned_edge=RIGHT)
        services[0].next_to(services[1], LEFT, buff=0.45)
        services[2].move_to([0.95, -1.85, 0], aligned_edge=LEFT)
        services[3].next_to(services[2], RIGHT, buff=0.45)
        for item, phrase in zip(services, phrases):
            self.pad_to(A(phrase) - 0.15)
            self.play(FadeIn(item, shift=UP * 0.15), run_time=0.45)

        # wallets define their own key derivation underneath
        hd = VGroup(dashed_box(w=2.3, h=0.6, color=CYAN, stroke_width=2.4),
                    label("HD wallet", size=FS_LABEL, color=STAR)).move_to([0, -2.72, 0])
        sk = kbox(['"sk"'], PNG_SK, size=24).next_to(hd, LEFT, buff=0.75)
        deriv = itex("wallet-defined key derivation", size=FS_LABEL, color=CYAN)
        deriv.next_to(hd, RIGHT, buff=0.45)
        sk_hd = karrow(sk[0].get_right(), hd[0].get_left() + LEFT * 0.03)
        hd_top, kb_bot = hd[0].get_top()[1] + 0.03, aknk[0].get_bottom()[1]
        hd_ak, hd_nk = [karrow(np.array([g.get_x(), hd_top, 0]), np.array([g.get_x(), kb_bot, 0]))
                        for g in aknk[1]]
        self.pad_to(AA(["while it's defined", "wallets define"]) - 0.2)
        self.play(FadeIn(sk, shift=UP * 0.1), ShowCreation(sk_hd), FadeIn(hd),
                  FadeIn(deriv, shift=LEFT * 0.15), run_time=0.7)
        self.play(ShowCreation(hd_ak), ShowCreation(hd_nk), run_time=0.7)

        # --- two quiet favors, argued beside the commitment
        self.pad_to(A("commitment does") - 0.25)
        self.play(FadeOut(VGroup(ak_name, nk_name)), run_time=0.45)
        compact_ring = contour(pk_eq, color=GOLD, buff=0.2, seed=41, stroke_width=SW)
        favors = bullets(["one compact owner field", "quantum-recoverable today"],
                         size=FS_BODY, color=STAR)
        favors.move_to([1.3, 1.35, 0], aligned_edge=UL)
        self.pad_to(A("single compact value") - 0.4)
        self.play(ShowCreation(compact_ring), FadeIn(favors[0], shift=RIGHT * 0.2),
                  run_time=0.6)
        self.pad_to(A("quantum recoverable") - 0.3)
        self.play(FadeIn(favors[1], shift=RIGHT * 0.2), run_time=0.55)

        # the contrast lives in the upper-left of the core band
        bare = VGroup(label("bare", size=FS_BODY, color=FLARE),
                      tex_chip('"ak"', color=FLARE, size=FS_BODY)).arrange(RIGHT, buff=0.2)
        bare.move_to([-6.2, 2.3, 0], aligned_edge=LEFT)
        risk = label("harvest now,\ndecrypt later", size=FS_BODY, color=FLARE,
                     weight="BOLD").next_to(bare, DOWN, buff=0.3, aligned_edge=LEFT)
        self.pad_to(AA(["handing your bare", "bare authorization"]) - 0.3)
        self.play(FadeIn(bare, shift=RIGHT * 0.15), run_time=0.55)
        self.pad_to(A("harvest now") - 0.3)
        xx = strike(bare[1])
        self.play(ShowCreation(xx), FadeIn(risk, shift=UP * 0.1), run_time=0.7)
        self.pad_to(AA(["commitment to it isn't", "it isn't"]) - 0.3)
        safe = VGroup(checkmark(0.34, GOLD),
                      label("a hash commitment\nreveals neither key", size=FS_BODY,
                            color=GOLD, weight="BOLD")).arrange(RIGHT, buff=0.25)
        safe.move_to([-6.2, 0.95, 0], aligned_edge=LEFT)
        self.play(FadeOut(VGroup(bare, xx, risk)), FadeIn(safe),
                  Indicate(pk_eq, color=GOLD, scale_factor=1.08), run_time=0.75)

        # --- payment data rides the chain; the core never reads it
        ownership = VGroup(aknk, pk, ak_pk, pk_eq, pk_name, compact_ring, favors, safe,
                           services, hd, sk, deriv, sk_hd, hd_ak, hd_nk)
        blocks = VGroup(*[block(w=1.1, h=0.66) for _ in range(8)]).arrange(RIGHT, buff=0.42)
        blocks.move_to([0, -2.75, 0])
        links = VGroup(*[chain_link(blocks[i], blocks[i + 1]) for i in range(7)])
        chain_label = label("the public chain: a data-availability layer", size=FS_BODY,
                            color=CYAN).move_to([0, -1.78, 0])
        cipher = tex_chip('mono("9f c3 07 4a 1c")', color=CYAN, size=FS_BODY).move_to(
            [-4.0, 1.35, 0])
        cipher_tag = itex("encrypted payment data", size=FS_LABEL, color=CYAN).next_to(
            cipher, UP, buff=0.22)
        self.pad_to(A("travels on chain") - 1.3)
        self.play(FadeOut(ownership, lag_ratio=0.02), run_time=0.75)
        self.play(LaggedStart(*[FadeIn(b, shift=LEFT * 0.2) for b in blocks],
                              lag_ratio=0.08),
                  LaggedStart(*[ShowCreation(l) for l in links], lag_ratio=0.08),
                  FadeIn(chain_label), FadeIn(cipher, scale=1.15), FadeIn(cipher_tag),
                  run_time=1.0)
        # the ciphertext drops straight through the core band onto a block
        landed = blocks[5].copy().set_fill(CYAN, 0.45).set_stroke(CYAN, SW, 1.0)
        self.pad_to(AA(["encrypted like memos", "encrypted like"]) - 0.2)
        self.play(FadeOut(cipher_tag), run_time=0.3)
        self.play(cipher.animate.scale(0.45).move_to(blocks[5]).set_opacity(0),
                  FadeIn(landed, rate_func=squish_rate_func(smooth, 0.5, 1.0)), run_time=1.0)
        self.remove(cipher)

        blind = heading("the core stays blind", size=FS_HEAD, color=GOLD).move_to([0, 2.3, 0])
        self.pad_to(A("just bytes") - 0.2)
        self.play(FadeIn(blind, shift=DOWN * 0.15), run_time=0.5)
        nos = VGroup()
        for s in ["parses them", "constrains them", "pays circuit cost"]:
            t = label("nothing " + s, size=FS_BODY, color=TXT)
            nos.add(VGroup(xmark(), t).arrange(RIGHT, buff=0.22))
        nos.arrange(RIGHT, buff=0.75).move_to([0, 1.2, 0])
        if nos.get_width() > 12.6:
            nos.set_width(12.6)
        for item, phrase in zip(nos, ["nothing parses", "nothing constrains", "circuit costs"]):
            self.pad_to(A(phrase) - 0.15)
            self.play(FadeIn(item, shift=UP * 0.15), run_time=0.4)
        pass_through = label("payment data passes through consensus untouched",
                             size=FS_BODY, color=STAR).move_to([0, 0.15, 0])
        self.pad_to(AA(["data availability layer", "data availability"]) - 0.4)
        self.play(FadeIn(pass_through), Indicate(chain_label, color=CYAN, scale_factor=1.05),
                  Indicate(landed, color=CYAN), run_time=0.7)
        self.pad_to(A("stays blind") - 0.2)
        self.play(Indicate(blind, color=GOLD, scale_factor=1.08), run_time=0.65)

        # --- guarantees: Orchard's core held them all; the seam now sorts them.
        # A 3x2 grid in the core band; the two that move out sit in the right column
        # (Faerie above ivk, so each drop has a clear path through the seam).
        texts = ["ledger indistinguishability", "balance", "note privacy",
                 "unlinkability vs payment keys", "unlinkability vs ivk holder",
                 "Faerie-gold resistance"]
        loose = VGroup(*[prop_chip(s, TXT) for s in texts])
        grid = [[1, 0, 5], [2, 3, 4]]            # rows of indices into texts
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
        finals = VGroup(*[prop_chip(s, GOLD if i < 4 else CYAN) for i, s in enumerate(texts)])
        for i in range(4):
            finals[i].move_to(loose[i])
        finals[4].move_to([-1.9, -2.3, 0])   # drop path clears the band heading
        finals[5].move_to([2.6, -2.3, 0])
        self.pad_to(A("security properties") - 0.6)
        self.play(FadeOut(VGroup(blocks, links, landed, chain_label, blind, nos,
                                 pass_through)), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(loose[i], scale=0.92) for i in (1, 0, 5, 2, 3, 4)],
                              lag_ratio=0.12), run_time=1.0)
        self.pad_to(A("same seam") - 0.2)
        self.play(Indicate(seam, color=STAR, scale_factor=1.0), run_time=0.6)
        for i, t in zip(range(4), [A("ledger"), A("balance"), A("note privacy"),
                                   A("spend unlinkability")]):
            self.pad_to(t - 0.2)
            self.play(ReplacementTransform(loose[i], finals[i]), run_time=0.5)
        self.pad_to(AA(["only ever saw", "payment keys"]) - 0.3)
        self.play(Indicate(finals[3][1][1], color=STAR, scale_factor=1.0), run_time=0.5)
        self.pad_to(A("stronger flavor") - 0.2)
        self.play(ReplacementTransform(loose[4], finals[4]), run_time=0.9)
        self.pad_to(A("incoming viewing key") - 0.3)
        self.play(Indicate(finals[4][1][1], color=STAR, scale_factor=1.0), run_time=0.5)
        self.pad_to(AA(["fairy gold", "faerie gold"]) - 0.2)
        self.play(ReplacementTransform(loose[5], finals[5]), run_time=0.9)
        self.pad_to(AA(["responsibilities"]) - 0.3)
        self.play(Indicate(VGroup(finals[4][1][1], finals[5][1][1]), color=STAR,
                           scale_factor=1.0),
                  run_time=0.65)

        # --- the two unchanged mechanisms; the payment side keeps its two duties
        mech_head = heading("unchanged mechanisms", size=FS_HEAD, color=STAR).move_to(
            [0, 2.45, 0])

        def head_col(name, tag):
            return VGroup(label(name, size=FS_BODY, color=STAR, weight="BOLD"),
                          itex(tag, size=FS_LABEL, color=MUT)).arrange(
                DOWN, buff=0.1, aligned_edge=LEFT)

        h1, h2 = head_col("spend authorization", "as in Orchard"), \
            head_col("value balance", "as in Sapling")
        red = key_chip("RedPallas signature", color=GOLD, size=FS_BODY, pad=0.18)
        under = itex("under", size=FS_LABEL, color=TXT)
        rk = tex_chip('"rk" = ["ask" + alpha] thin G', color=GOLD, size=FS_BODY)
        rk[0].stretch_to_fit_height(red[0].get_height())   # same chip height per row
        vals = key_chip("homomorphic value commitments", color=GOLD, size=FS_BODY, pad=0.18)
        bind = key_chip("binding signature", color=GOLD, size=FS_BODY, pad=0.18)
        colw = max(h1.get_width(), h2.get_width())
        row1 = VGroup(red, under, rk).arrange(RIGHT, buff=0.3)
        row2 = VGroup(vals, bind).arrange(RIGHT, buff=0.9)
        vb_arrow = tarrow(vals, bind, color=TXT)
        body = VGroup(h1, h2, row1, row2, vb_arrow)
        h1.move_to([0, 1.35, 0], aligned_edge=LEFT)
        h2.move_to([0, 0.05, 0], aligned_edge=LEFT)
        row1.move_to([colw + 0.6, 1.35, 0], aligned_edge=LEFT)
        row2.move_to([colw + 0.6, 0.05, 0], aligned_edge=LEFT)
        vb_arrow.become(tarrow(vals, bind, color=TXT))
        fit_in(body, (-6.4, 6.4, -0.25, 1.95))
        self.pad_to(A("two familiar") - 0.3)
        self.play(FadeOut(VGroup(*finals[:4]), shift=UP * 0.15),
                  VGroup(finals[4], finals[5]).animate.fade(0.45), run_time=0.6)
        self.play(FadeIn(mech_head, shift=DOWN * 0.15), run_time=0.5)
        self.pad_to(A("spend authorization") - 0.2)
        self.play(FadeIn(h1, shift=RIGHT * 0.15), run_time=0.5)
        self.pad_to(AA(["red palace", "redpallas"]) - 0.2)
        self.play(FadeIn(red, shift=RIGHT * 0.15), run_time=0.5)
        self.pad_to(AA(["re randomized key", "rerandomized key"]) - 0.2)
        self.play(FadeIn(under), FadeIn(rk, shift=RIGHT * 0.15), run_time=0.6)
        self.pad_to(AA(["value balances", "value balance"]) - 0.2)
        self.play(FadeIn(h2, shift=RIGHT * 0.15), run_time=0.5)
        self.pad_to(A("homomorphic") - 0.2)
        self.play(FadeIn(vals, shift=RIGHT * 0.15), run_time=0.5)
        self.pad_to(A("binding signature") - 0.25)
        self.play(ShowCreation(vb_arrow), FadeIn(bind, shift=RIGHT * 0.15), run_time=0.6)
        self.pad_to(AA(["same mechanisms"]) - 0.3)
        mck = checkmark(0.34).next_to(mech_head, RIGHT, buff=0.35)
        self.play(ShowCreation(mck), run_time=0.45)

        # --- what the cut buys
        core_box, core_name, stable, modules, evolve = cut_buys()
        self.pad_to(A("what does") - 0.1)
        self.play(FadeOut(VGroup(mech_head, mck, body), shift=UP * 0.15),
                  FadeOut(VGroup(finals[4], finals[5]), shift=DOWN * 0.15), run_time=0.65)
        self.pad_to(AA(["small stable", "a small"]) - 0.3)
        self.play(FadeIn(core_box, scale=1.05), FadeIn(core_name, scale=1.05), run_time=0.65)
        self.pad_to(A("audited") - 0.3)
        self.play(FadeIn(stable, shift=UP * 0.1), run_time=0.55)
        self.pad_to(A("and payment protocols") - 0.35)
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.2) for m in modules], lag_ratio=0.25),
                  run_time=0.75)
        self.pad_to(A("free to evolve") - 0.2)
        self.play(FadeIn(evolve, shift=UP * 0.1), run_time=0.6)
        self.pad_to(scene_T("1.2"))


class Scene13(TimedScene):
    """1.3 — The Tachyon note: four fields, one symmetric hash, and psi."""

    def construct(self):
        A = lambda p, o=1: anchor("1.3", p, o)
        AA = lambda ps, o=1: anchor_any("1.3", ps, o)

        # reconstruct Scene12's last frame
        core, pay, core_head, pay_head, core_def, pay_def, seam = bands()
        core_box, core_name, stable, modules, evolve = cut_buys()
        frame12 = VGroup(core, pay, core_head, pay_head, core_def, pay_def, seam, stable,
                         modules, evolve)
        self.add(frame12, core_box, core_name)

        # "the note that core maintains": the core's box becomes the note card
        title = scene_title("the Tachyon note")
        cells = VGroup(*[panel(2.75, 1.95, color=GOLD, fill_opacity=0.04,
                               stroke_opacity=0.55, stroke_width=SW_THIN)
                         for _ in range(4)])
        cells.arrange(RIGHT, buff=0.25).move_to(UP * 0.2)   # stage center; lifts at the hash
        card = panel(cells.get_width() + 0.5, cells.get_height() + 0.4, color=GOLD,
                     fill_opacity=0.05).move_to(cells)
        self.pad_to(0.4)
        self.play(FadeOut(frame12), FadeOut(core_name), run_time=0.5)
        self.play(ReplacementTransform(core_box, card), run_time=0.6)
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.6)
        self.pad_to(A("four fields") - 0.2)
        self.play(LaggedStart(*[ShowCreation(c) for c in cells], lag_ratio=0.15),
                  run_time=0.8)
        add_shimmer(cells, amp=0.18, speed=1.2)

        specs = [('"pk"', "payment key", STAR, A("payment key")),
                 ('v', "value", STAR, A("a value")),
                 ('psi', "note identity", GOLD, A("note identity")),
                 ('"rcm"', "trapdoor", STAR, AA(["trap door", "trapdoor"]))]
        syms, caps = VGroup(), VGroup()
        for (tex, cap, color, t), cell in zip(specs, cells):
            s = mtex(tex, size=60, color=color)
            s.move_to(cell.get_center() + UP * 0.25)
            c = label(cap, size=FS_LABEL, color=TXT).move_to(cell.get_center() + DOWN * 0.52)
            self.pad_to(t - 0.2)
            self.play(FadeIn(s, scale=1.3), FadeIn(c, shift=UP * 0.1), run_time=0.5)
            syms.add(s)
            caps.add(c)

        # Poseidon hashes all four -> cm
        sponge = sponge_icon().scale(1.3).move_to([0, -0.55, 0])
        note = VGroup(card, cells, syms, caps)
        self.pad_to(AA(["the note commitment", "note commitment hashes"]) - 0.3)
        self.play(note.animate.shift(UP * 1.3), run_time=0.7)
        self.play(FadeIn(sponge, scale=1.1), run_time=0.5)
        self.pad_to(A("poseidon") - 0.5)
        flying = []
        for s in syms:
            cpy = s.copy()
            cpy.generate_target()
            cpy.target.move_to(sponge[0].get_center()).scale(0.3).set_opacity(0)
            flying.append(MoveToTarget(cpy, remover=True))
        cm_eq = mtex('"cm" = "Poseidon"("pk", v, psi, "rcm")', size=FS_HEAD, color=GOLD)
        cm_eq.move_to(DOWN * 2.05)
        self.play(LaggedStart(*flying, lag_ratio=0.12), run_time=1.0)
        self.play(FadeIn(cm_eq, shift=DOWN * 0.2), run_time=0.7)

        # the one deliberate change: Pedersen out, symmetric only
        self.pad_to(AA(["sappling and orchard", "sapling and orchard"]) - 0.4)
        group_r = VGroup(sponge, cm_eq)
        self.play(group_r.animate.shift(RIGHT * 3.2), run_time=0.9)
        ped_tag = label("Sapling / Orchard", size=FS_BODY, color=TXT, weight="BOLD")
        ped = tex_chip('"cm" in G', color=MUT, size=FS_HEAD)
        ped_sub = label("Pedersen-style: a curve point", size=FS_LABEL, color=TXT)
        cp = label("discrete-log assumption", size=FS_LABEL, color=FLARE)
        ped_col = VGroup(ped_tag, ped, ped_sub, cp).arrange(DOWN, buff=0.26)
        ped_col.move_to([-3.6, -1.55, 0])
        self.pad_to(AA(["peterson style", "peterson"]) - 0.3)
        self.play(FadeIn(ped_tag, shift=RIGHT * 0.15), FadeIn(ped, shift=RIGHT * 0.15),
                  FadeIn(ped_sub, shift=RIGHT * 0.15), run_time=0.7)
        self.pad_to(A("curve points") - 0.2)
        self.play(Indicate(ped, color=MUT, scale_factor=1.06), run_time=0.5)
        self.pad_to(AA(["discrete log"]) - 0.2)
        self.play(FadeIn(cp, shift=UP * 0.1), run_time=0.5)
        self.pad_to(A("purely symmetric") - 0.3)
        xx = strike(ped)
        sym_tag = label("purely symmetric", size=FS_BODY, color=GOLD, weight="BOLD")
        sym_tag.next_to(cm_eq, DOWN, buff=0.3)
        self.play(ShowCreation(xx), FadeIn(sym_tag, shift=UP * 0.1), run_time=0.8)

        # hiding against a quantum adversary: the probe stops at the shield
        q_tag = label("quantum\nadversary", size=FS_LABEL, color=FLARE)
        q_tag.move_to([6.65, -0.15, 0], aligned_edge=RIGHT)
        hit = np.array([cm_eq.get_right()[0] - 0.45, cm_eq.get_top()[1] + 0.16, 0])
        probe = tarrow(q_tag.get_bottom() + DOWN * 0.18, hit, color=FLARE, width=SW, tip=0.24)
        shield = SurroundingRectangle(cm_eq, buff=0.14)
        shield.set_stroke(GOLD, SW, 0.95)
        self.pad_to(A("quantum adversary") - 0.5)
        self.play(FadeIn(q_tag), ShowCreation(probe), run_time=0.7)
        self.play(ShowCreation(shield), run_time=0.45)
        self.play(probe.animate.shift((q_tag.get_bottom() - hit) * 0.08).set_opacity(0.35),
                  run_time=0.5)
        nd = mtex('no special discipline on $"rcm"$', size=FS_LABEL, color=TXT, math=False)
        nd.next_to(sym_tag, DOWN, buff=0.2)
        self.pad_to(A("no special discipline") - 0.3)
        self.play(FadeIn(nd, shift=UP * 0.1), run_time=0.6)

        # the field to watch: psi
        self.pad_to(A("field to watch") - 0.9)
        q_stuff = VGroup(probe, q_tag, shield, ped_col, xx, sym_tag, nd, cm_eq)
        self.play(FadeOut(q_stuff, shift=DOWN * 0.15), FadeOut(sponge, shift=DOWN * 0.15),
                  run_time=0.7)
        psi_dash = dashed_box(cells[2], buff=0.07, stroke_width=3.0)
        self.play(ShowCreation(psi_dash), Indicate(syms[2], color=GOLD, scale_factor=1.15),
                  run_time=0.7)
        psi_big = mtex("psi", size=130, color=GOLD)
        traits = bullets(["pseudorandom identity", "fixed at creation",
                          "known to sender and recipient"], size=FS_BODY, color=STAR, buff=0.3)
        VGroup(psi_big, traits).arrange(RIGHT, buff=0.9).move_to([0, -1.35, 0])
        self.play(TransformFromCopy(syms[2], psi_big), run_time=0.9)
        for m, t in zip(traits, [AA(["pseudo random identity", "pseudorandom"]),
                                 A("fixed at creation"),
                                 AA(["known to sender", "sender and recipient"])]):
            self.pad_to(t - 0.2)
            self.play(FadeIn(m, shift=RIGHT * 0.2), run_time=0.5)

        # Orchard: one nullifier. Tachyon: a family of them.
        row_y1, row_y2 = -0.65, -2.45
        orch = label("Orchard", size=FS_BODY, color=TXT, weight="BOLD").move_to(
            [-6.5, row_y1, 0], aligned_edge=LEFT)
        psi_s = mtex("psi", size=FS_HEAD + 6, color=GOLD).move_to([-3.9, row_y1, 0])
        nf1 = VGroup(bead(FLARE, 0.15), mtex('"nf"', size=FS_BODY, color=FLARE))
        nf1.arrange(RIGHT, buff=0.15).move_to([-1.0, row_y1, 0])
        arr1 = tarrow(psi_s, nf1, color=TXT, width=SW, buff=0.2)
        self.pad_to(A("in orchard") - 0.3)
        self.play(FadeOut(traits, shift=RIGHT * 0.2), ReplacementTransform(psi_big, psi_s),
                  FadeIn(orch, shift=RIGHT * 0.15), run_time=0.7)
        self.play(ShowCreation(arr1), run_time=0.4)
        self.pad_to(A("one nullifier") - 0.1)
        self.play(FadeIn(nf1, scale=1.2), run_time=0.5)

        tach = label("Tachyon", size=FS_BODY, color=GOLD, weight="BOLD").move_to(
            [-6.5, row_y2, 0], aligned_edge=LEFT)
        psi_t = mtex("psi", size=FS_HEAD + 6, color=GOLD).move_to([-3.9, row_y2, 0])
        axis = Line([-2.95, row_y2, 0], [6.55, row_y2, 0], stroke_width=SW_THIN,
                    stroke_color=DIM)
        xs = [-2.2 + i * 1.6 for i in range(6)]
        ticks = VGroup(*[mtex(f"e_{i}", size=FS_LABEL, color=MUT).move_to([x, row_y2 - 0.5, 0])
                         for i, x in enumerate(xs)])
        self.pad_to(AA(["in tachyon", "tachyon p"]) - 0.3)
        self.play(FadeIn(tach, shift=RIGHT * 0.15), TransformFromCopy(psi_s, psi_t),
                  ShowCreation(axis),
                  LaggedStart(*[FadeIn(t, shift=UP * 0.1) for t in ticks], lag_ratio=0.1),
                  run_time=0.9)
        beads = VGroup(*[bead(FLARE, 0.15).move_to([x, row_y2, 0]) for x in xs])
        fam = label("one nullifier per epoch", size=FS_BODY, color=FLARE).move_to(
            [(xs[0] + xs[-1]) / 2, row_y2 + 0.62, 0])
        self.pad_to(A("seed") - 0.25)
        self.play(LaggedStart(*[GrowFromPoint(b, psi_t.get_right()) for b in beads],
                              lag_ratio=0.15),
                  run_time=0.85)
        self.pad_to(A("family") - 0.2)
        self.play(Indicate(beads, color=GOLD, scale_factor=1.12), FadeIn(fam, shift=UP * 0.1),
                  run_time=0.8)
        self.pad_to(scene_T("1.3"))

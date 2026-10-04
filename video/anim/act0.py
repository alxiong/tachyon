"""Act 0 — cold open, anchored to word timestamps resolved from anim/words.json.

Anchors are phrase lookups (style.anchor), so regenerated audio re-syncs by
re-running the alignment step — no hand-retiming. Audio files are the padded
1.08x finals (1 s lead-in), so anchor times already include the padding.

Layout (2026-10-04 pass): two-column stage in 0.1 (commitments | nullifiers),
validator ↔ wallet stage in 0.2, all text on the style.py type scale.

Render:  manimgl act0.py Scene01 Scene02 -w
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manimlib import *
from style import *

T_01 = scene_T("0.1")
T_02 = scene_T("0.2")

LX, RX = -3.55, 3.55      # column centers in 0.1
CELL, CBUF = 0.42, 0.09   # nullifier cell side + gap
GRID_Y = 0.75             # nullifier grid centre while it grows
WALL_ROWS, WALL_COLS = 14, 6
WALL_H, WALL_X = 6.0, 4.1


def binary_tree(depth=4, width=5.6, height=3.4, color=MUT):
    nodes, edges = VGroup(), VGroup()
    levels = []
    for d in range(depth + 1):
        row = VGroup()
        n = 2 ** d
        y = height / 2 - d * (height / depth)
        for i in range(n):
            x = -width / 2 + (i + 0.5) * (width / n)
            dot = Dot(np.array([x, y, 0]), radius=0.075 if d < depth else 0.065)
            dot.set_fill(color, 1.0)
            row.add(dot)
        levels.append(row)
        nodes.add(row)
    for d in range(depth):
        for i, child in enumerate(levels[d + 1]):
            parent = levels[d][i // 2]
            edges.add(Line(parent.get_center(), child.get_center(),
                           stroke_width=SW_THIN, stroke_color=color, stroke_opacity=0.75))
    return nodes, edges, levels


def cells(n, side=CELL, opacity_lo=0.45):
    g = VGroup()
    for k in range(n):
        sq = Square(side_length=side)
        heat = opacity_lo + (0.95 - opacity_lo) * ((k * 7919) % 97) / 97
        sq.set_fill(FLARE, heat)
        sq.set_stroke(AMBER, 1.0, 0.4)
        g.add(sq)
    return g


def wall_layout(g):
    """The final 'wall' arrangement shared by the end of 0.1 and the start of 0.2."""
    g.arrange_in_grid(n_rows=WALL_ROWS, n_cols=WALL_COLS, buff=0.06)
    g.set_height(WALL_H).move_to(RIGHT * WALL_X)
    return g


def question():
    q = VGroup(heading("who actually needs", size=54, color=GOLD),
               heading("to remember all this?", size=54, color=GOLD))
    q.arrange(DOWN, buff=0.3)
    q.move_to(LEFT * 2.3)
    return q


def two_line(a, b, size=FS_LABEL, color=TXT, leading=1.3):
    """Two centred lines on fixed baselines (leading x size). Each line keeps its
    invisible '|' strut, so the group's bounding box is the same whatever glyphs it
    holds — sibling cards centred alike get identical text rows."""
    lines = VGroup()
    step = leading * size * 8.0 / 810.0          # pt -> scene units (1080p)
    for k, s in enumerate((a, b)):
        m = label("|" + s, size=size, color=color)
        strut = m.submobjects[0]
        m.remove(strut)
        m.base_h = max(m.get_height(), 1e-6)
        strut.set_opacity(0)
        row = VGroup(strut, m)
        row.shift(UP * (-k * step - strut.get_bottom()[1]))
        m.set_x(0)
        strut.match_x(m)   # invisible; centred so it never shifts the optical centre
        lines.add(row)
    return lines


def strike(mob, color=FLARE, over=0.12):
    """Deliberate horizontal strike-through. A polyline VMobject, not a Line, so the
    layout linter (which flags Lines crossing text) leaves intentional strikes alone."""
    y = mob.get_center()[1]
    vm = VMobject()
    vm.set_points_as_corners([np.array([mob.get_left()[0] - over, y, 0]),
                              np.array([mob.get_right()[0] + over, y, 0])])
    vm.set_stroke(color, SW_BOLD, 1.0)
    return vm


def rich_line(parts, size=FS_BODY, buff=0.16, weight="NORMAL"):
    """Like style.rich(), but baseline-aligned: each run is rendered after a '|'
    strut (same ink box for every run), aligned on the strut, then the strut is
    dropped — so descenders ('p', 'y') don't lift a run off the line. Runs may be
    any mobject (e.g. an arrow), which is centred on the x-height."""
    runs = VGroup()
    for text, color in parts:
        if isinstance(text, Mobject):
            runs.add(VGroup(text))
            continue
        m = label("|" + text, size=size, color=color, weight=weight)
        strut = m.submobjects[0]
        m.remove(strut)
        m.base_h = max(m.get_height(), 1e-6)
        runs.add(VGroup(strut.set_opacity(0), m))
    runs.arrange(RIGHT, buff=buff, aligned_edge=DOWN)
    struts = [r[0] for r in runs if len(r) == 2]
    if struts:
        # math axis ≈ 45% up the '|' strut (which spans descender..ascender)
        axis = struts[0].get_bottom()[1] + 0.45 * struts[0].get_height()
        for r in runs:
            if len(r) == 1:
                r[0].set_y(axis)
    return VGroup(*[r[-1] for r in runs])


class Scene01(TimedScene):
    """0.1 — Two sets, two fates."""

    def construct(self):
        A = lambda p, o=1: anchor("0.1", p, o)
        AA = lambda ps, o=1: anchor_any("0.1", ps, o)

        # lead-in second, then title under the opening sentence
        logo = ImageMobject(LOGO_PNG)
        logo.set_height(1.8)
        title = heading("Scaling Zcash with Tachyon", size=60)
        card = Group(logo, title).arrange(DOWN, buff=0.45)
        self.wait(0.5)
        self.play(FadeIn(logo, scale=1.08), FadeIn(title, shift=UP * 0.2), run_time=1.2)
        l_title = heading("note commitments", size=FS_HEAD).move_to([LX, 3.1, 0])
        r_title = heading("nullifiers", size=FS_HEAD).move_to([RX, 3.1, 0])
        nodes, edges, levels = binary_tree()
        tree = VGroup(edges, nodes).move_to([LX, 0.35, 0])
        grid = cells(42).arrange_in_grid(n_rows=6, n_cols=7, buff=CBUF)
        grid.move_to([RX, GRID_Y, 0])
        divider = Line(UP * 3.0, DOWN * 3.0, stroke_width=SW_THIN,
                       stroke_color=DIM, stroke_opacity=0.7)

        # "two growing sets": the card lifts away while the split stage draws in,
        # seeded with each set's first element — never an empty frame
        self.pad_to(A("two growing sets") - 1.0)
        self.play(LaggedStart(
            FadeOut(card, shift=UP * 0.4),
            AnimationGroup(ShowCreation(divider),
                           FadeIn(levels[0], scale=1.5),
                           LaggedStart(*[FadeIn(c, scale=1.6) for c in grid[0:7]],
                                       lag_ratio=0.1)),
            lag_ratio=0.45), run_time=1.6)

        # "every transaction adds note commitments and, eventually, nullifiers.
        #  They grow at the same rate" — lockstep growth fed by tx dots; each column
        # title lands on its word inside the build
        pending = [(A("note commitments") - 0.3, l_title), (A("nullifiers") - 0.3, r_title)]

        def due(t_end):
            out = []
            while pending and pending[0][0] < t_end:
                out.append(FadeIn(pending.pop(0)[1], shift=UP * 0.15))
            return out

        self.pad_to(A("every transaction") - 0.1)
        for d in range(1, 6):
            # each batch of transactions feeds both sets at once: a gold commitment
            # dot to the tree's next level, a flare nullifier dot to the grid's next
            # row. Dots fade in while flying and dissolve into what they create.
            feeders, flights = [], []
            targets = [(FLARE, grid[7 * d].get_center())]
            if d < 5:
                targets.append((GOLD, levels[d][0].get_center()))
            for col, dest in targets:
                f = Dot(UP * 2.55, radius=0.08).set_fill(col, 0)
                feeders.append(f)
                flights.append(f.animate.move_to(dest).set_fill(opacity=1))
            self.play(*flights, *due(self.time + 0.5), run_time=0.5)
            grow = [LaggedStart(*[FadeIn(c, scale=1.6) for c in grid[7 * d:7 * (d + 1)]],
                                lag_ratio=0.12)]
            if d < 5:
                lv = levels[d - 1][0].get_center()[1]
                new_edges = VGroup(*[e for e in edges if abs(e.get_start()[1] - lv) < 0.01])
                grow += [LaggedStartMap(GrowFromCenter, levels[d], lag_ratio=0.03),
                         ShowCreation(new_edges, lag_ratio=0.03)]
            self.play(*grow, *[FadeOut(f, scale=0.4) for f in feeders],
                      *due(self.time + 0.5), run_time=0.8)
        assert not pending
        add_shimmer(grid)

        # "the tree is append only" — focus swings left
        self.pad_to(AA(["append", "penned only", "pend only"]) - 0.2)
        self.play(grid.animate.set_opacity(0.5), r_title.animate.set_opacity(0.45),
                  run_time=0.8)
        for sq in grid:
            sq.shimmer_base = sq.get_fill_opacity()

        # "needs its root"
        root_glow = Dot(levels[0][0].get_center(), radius=0.13).set_fill(GOLD, 1)
        root_label = label("root", size=FS_LABEL, color=GOLD)
        root_label.next_to(root_glow, RIGHT, buff=0.25)
        self.pad_to(A("its root") - 0.2)
        self.play(FadeIn(root_glow, scale=2.2), FadeIn(root_label, shift=LEFT * 0.1),
                  run_time=0.7)
        self.play(Indicate(root_glow, color=GOLD, scale_factor=1.4), run_time=0.7)

        # "push the whole thing to disk and forget about it"
        disk = panel(5.6, 1.0, color=MUT, fill_opacity=0.06)
        disk.move_to([LX, -2.35, 0])
        disk_label = label("disk", size=FS_LABEL, color=MUT)
        disk_label.move_to(disk.get_left() + RIGHT * 0.75)
        body = VGroup(edges, *levels[1:])
        self.pad_to(A("to disk") - 1.0)
        self.play(FadeIn(disk, shift=UP * 0.2), FadeIn(disk_label), run_time=0.7)
        self.play(body.animate.scale(0.22).move_to(disk.get_center() + RIGHT * 0.6)
                  .set_opacity(0.45), run_time=1.8, rate_func=smooth)
        self.play(VGroup(body, disk, disk_label).animate.fade(0.2), run_time=0.9)

        # "the nullifier set gets no such luck" — focus swings right
        self.pad_to(A("no such luck") - 0.6)
        self.play(grid.animate.set_opacity(1.0),
                  r_title.animate.set_opacity(1.0),
                  VGroup(l_title, root_label).animate.set_opacity(0.45),
                  root_glow.animate.set_opacity(0.6),
                  run_time=1.0)
        for sq in grid:
            sq.shimmer_base = sq.get_fill_opacity()

        # "the validator has to answer"
        probe_src = grid.get_bottom() + DOWN * 1.0
        q_txt = label("seen before?", size=FS_BODY, color=STAR)
        q_txt.next_to(probe_src, DOWN, buff=0.15)
        target = grid[17]
        probe = Line(probe_src, target.get_center(),
                     stroke_width=SW, stroke_color=STAR, stroke_opacity=0.95)
        self.pad_to(A("has to answer") - 0.2)
        self.play(ShowCreation(probe), FadeIn(q_txt, shift=UP * 0.1), run_time=0.7)
        target_fill = target.get_fill_opacity()
        target.clear_updaters()   # hold the probed cell steady while it is lit
        self.play(target.animate.set_fill(STAR, 1.0), run_time=0.3)

        # "not recently — ever."
        self.pad_to(A("not recently") - 0.1)
        self.play(LaggedStartMap(
            lambda m: m.animate(rate_func=there_and_back).set_fill(STAR, 1.0),
            grid[-7:], lag_ratio=0.08), run_time=0.9)
        self.pad_to(A("ever", 3) - 0.1)  # 3rd: the emphatic "Ever." (2nd is "nullifier ever appeared")
        self.play(LaggedStartMap(
            lambda m: m.animate(rate_func=there_and_back).set_fill(STAR, 1.0),
            grid, lag_ratio=0.015), run_time=1.6)
        # the probe retracts; the probed cell cools back to its own heat
        self.play(Uncreate(probe), FadeOut(q_txt, shift=DOWN * 0.1),
                  target.animate.set_fill(FLARE, target_fill), run_time=0.5)
        add_shimmer([target])

        # "the entire history of the chain" — rows run oldest (top) to newest (bottom),
        # so older history arrives ABOVE: the grid steps down to make room
        older = cells(14, opacity_lo=0.3).arrange_in_grid(n_rows=2, n_cols=7, buff=CBUF)
        drop = 2 * (CELL + CBUF)
        older.next_to(grid, UP, buff=CBUF).shift(DOWN * drop)
        self.pad_to(A("entire history") - 0.2)
        self.play(grid.animate.shift(DOWN * drop),
                  LaggedStart(*[FadeIn(c, shift=DOWN * 0.15) for c in reversed(older)],
                              lag_ratio=0.05),
                  run_time=1.2)

        # "fast... critical path of consensus"
        full_set = VGroup(grid, older)

        def ram_around(m):
            r = panel(m.get_width() + 0.5, m.get_height() + 0.5,
                      color=FLARE, fill_opacity=0.0, stroke_opacity=0.95, stroke_width=SW)
            return r.move_to(m.get_center())

        ram = ram_around(full_set)
        ram_label = label("in memory, on the critical path", size=FS_LABEL, color=FLARE)
        ram_label.next_to(ram, DOWN, buff=0.25)
        self.pad_to(A("be fast") - 0.2)
        self.play(ShowCreation(ram), run_time=0.9)
        self.pad_to(A("critical path") - 0.2)
        self.play(FadeIn(ram_label, shift=UP * 0.1), run_time=0.7)

        # "and it only grows"
        self.pad_to(A("only grows") - 0.3)
        self.play(VGroup(full_set, ram).animate.scale(1.06), run_time=1.2)

        # "Now scale that." — more history arrives; the whole set refits the column
        extra = cells(28, opacity_lo=0.35).arrange_in_grid(n_rows=4, n_cols=7, buff=CBUF)
        extra.match_width(full_set).next_to(full_set, DOWN, buff=CBUF * 1.06)
        everything = VGroup(grid, older, extra)
        target_set = everything.copy().set_height(5.0).move_to([RX, -0.15, 0])
        extra.become(target_set[2])
        self.pad_to(A("scale that") - 0.2)
        self.play(FadeOut(ram_label), run_time=0.4)
        self.play(Transform(grid, target_set[0]), Transform(older, target_set[1]),
                  Transform(ram, ram_around(target_set)), run_time=1.2)
        self.play(LaggedStartMap(FadeIn, extra, lag_ratio=0.03), run_time=1.0)

        # counter lands on 500 exactly on the word — left column, above the disk
        t500 = A("500")
        tracker = ValueTracker(0)
        NUM_PT = 120

        def numeral(v):
            return label(str(int(round(v))), size=NUM_PT, color=FLARE)

        num = numeral(0)
        unit = label("GB / day", size=FS_HEAD + 6, color=STAR)
        stat = VGroup(numeral(500), unit).arrange(RIGHT, buff=0.35)
        # share a baseline: the digits and the 'G' both sit on it ('/' and 'y' descend)
        unit.shift(UP * (stat[0].get_bottom()[1] - unit[0].get_bottom()[1]))
        stat.move_to([LX, 0.0, 0])
        num_right = stat[0].get_corner(DR)

        def tick(m):
            m.become(numeral(tracker.get_value()))
            m.move_to(num_right, aligned_edge=DR)

        num.add_updater(tick)
        self.pad_to(t500 - 2.4)
        self.play(VGroup(l_title, root_glow, root_label).animate.set_opacity(0.3),
                  FadeIn(num), run_time=0.4)
        self.play(tracker.animate.set_value(500), run_time=2.0, rate_func=rush_into)
        num.clear_updaters()
        self.play(FadeIn(unit, shift=UP * 0.1), run_time=0.6)

        # "not per year — per day."
        per_year = label("per year", size=FS_BODY, color=MUT)
        per_year.next_to(VGroup(num, unit), DOWN, buff=0.45)
        strike_ = strike(per_year)
        self.pad_to(A("not per year") - 0.1)
        self.play(FadeIn(per_year), run_time=0.5)
        self.play(ShowCreation(strike_), per_year.animate.set_opacity(0.6), run_time=0.5)
        self.pad_to(A("per day", 2) - 0.1)
        self.play(Indicate(unit, color=FLARE, scale_factor=1.2), run_time=0.8)

        # "no consensus node holds that in RAM"
        self.pad_to(A("in ram") - 0.3)
        self.play(ram.animate(rate_func=there_and_back).set_stroke(FLARE, 7, 1.0).scale(1.03),
                  run_time=1.0)

        # "this isn't a proving problem" — the takeaway, captioned on its words
        cap = rich_line([("not a proving problem:", TXT), ("a set nobody can prune", FLARE)])
        cap.move_to(UP * CAPTION_Y)
        self.pad_to(A("proving problem") - 0.3)
        self.play(FadeIn(cap, shift=UP * 0.15), run_time=0.8)

        # "never allowed itself to prune" — a cut is offered below the oldest rows,
        # and refused: nothing leaves the set
        clear_shimmer(grid)
        clear_shimmer([target])
        y_cut = (older[-1].get_bottom()[1] + grid[0].get_top()[1]) / 2
        cut = DashedLine([ram.get_left()[0] - 0.35, y_cut, 0],
                         [ram.get_right()[0] + 0.35, y_cut, 0],
                         dash_length=0.14, stroke_width=SW, stroke_color=STAR)
        self.pad_to(A("prune") - 1.0)
        self.play(ShowCreation(cut, lag_ratio=0.0), run_time=0.6)
        self.play(cut.animate.set_stroke(FLARE, SW, 1.0),
                  WiggleOutThenIn(cut, scale_value=1.0, rotation_angle=0.025 * TAU),
                  ram.animate(rate_func=there_and_back).set_stroke(FLARE, 7, 1.0),
                  run_time=0.8)
        self.play(FadeOut(cut, shift=LEFT * 0.2), run_time=0.4)

        # "That's the wall."
        self.pad_to(A("the wall") - 0.3)
        all_cells = VGroup(*older, *grid, *extra)   # oldest -> newest
        # cells settle into the wall oldest-first: a cascade, not a simultaneous jumble
        wall_slots = wall_layout(all_cells.copy())
        self.play(
            LaggedStart(*[Transform(c, t) for c, t in zip(all_cells, wall_slots)],
                        lag_ratio=0.006),
            FadeOut(ram), FadeOut(r_title), FadeOut(cap),
            FadeOut(VGroup(num, unit, per_year, strike_, l_title, root_glow, root_label,
                           disk, disk_label, body, levels[0], divider), shift=LEFT * 0.3),
            run_time=1.0,
        )

        # "built to remove" — the mark arrives and squares up to the wall
        mark = ImageMobject(LOGO_PNG)
        mark.set_height(1.5)
        mark.move_to(LEFT * 6.0 + DOWN * 0.2)
        self.pad_to(A("built to remove") - 0.6)
        self.play(FadeIn(mark, shift=RIGHT * 0.5), run_time=0.6)
        self.play(mark.animate.move_to(RIGHT * (WALL_X - 2.3)), run_time=1.0)

        # "who actually needs to remember all this?"
        self.pad_to(A("the question") - 0.2)
        clean_wall = all_cells.copy().set_opacity(0)
        self.add(clean_wall)
        old_stage = Group(*[m for m in self.mobjects if m is not clean_wall])
        self.play(old_stage.animate.set_opacity(0),
                  clean_wall.animate.set_opacity(0.12), run_time=0.9)
        self.remove(old_stage)
        q = question()
        self.pad_to(A("who actually") - 0.2)
        self.play(Write(q, run_time=2.0, lag_ratio=0.2))
        self.pad_to(T_01)


class Scene02(TimedScene):
    """0.2 — The thesis: client-side validation."""

    def construct(self):
        A = lambda p, o=1: anchor("0.2", p, o)
        AA = lambda ps, o=1: anchor_any("0.2", ps, o)

        # open on Scene01's final frame (seamless cut)
        wall_hot = wall_layout(cells(WALL_ROWS * WALL_COLS, opacity_lo=0.35))
        wall = wall_hot.copy().set_opacity(0.12)
        q = question()
        self.add(wall, q)

        # "one principle" — the question becomes the principle (title band);
        # runs share one baseline ('p' in "proves" must not lift that run)
        flow = tarrow(ORIGIN, RIGHT * 1.0, color=STAR, width=SW)
        principle = rich_line([("the client proves", GOLD), (flow, None),
                               ("consensus checks", GOLD)],
                              size=FS_TITLE, buff=0.35, weight="BOLD")
        principle.move_to(UP * TITLE_Y)
        self.pad_to(A("one principle") - 0.8)
        self.play(FadeTransform(q, principle), run_time=0.8)

        # "move validation off the critical path... onto the client"
        # the panel row starts vertically centred on the stage (nothing below it yet)
        # and lifts by LIFT when the pruned-history / chain rows need the lower stage
        STAGE_Y, LIFT = 0.0, 0.6
        validator = panel(4.8, 3.4, color=FLARE, fill_opacity=0.05)
        validator.move_to([-4.15, STAGE_Y, 0])
        v_label = label("validator", size=FS_LABEL, color=FLARE)
        v_label.next_to(validator, DOWN, buff=0.22)
        wallet = panel(4.0, 3.4, color=GOLD, fill_opacity=0.06)
        wallet.move_to([4.5, STAGE_Y, 0])
        w_label = label("wallet", size=FS_LABEL, color=GOLD)
        w_label.next_to(wallet, DOWN, buff=0.22)

        self.pad_to(A("move validation") - 0.3)
        # the wall comes back to heat (per-cell, not a flat slab) and steps forward
        self.play(Transform(wall, wall_hot.set_height(3.4).move_to([0, STAGE_Y, 0])),
                  run_time=1.2)
        self.play(FadeIn(validator, scale=1.04), FadeIn(v_label, shift=UP * 0.1),
                  run_time=0.8)

        # window: one row of recent cells inside the validator panel
        n_slots = 7
        slot_w = 0.5
        def slot(i):
            # follows the panel wherever it currently is
            x0 = validator.get_center()[0] - slot_w * (n_slots - 1) / 2
            return np.array([x0 + i * slot_w, validator.get_top()[1] - 0.75, 0])

        def window_cell(op):
            return (Square(side_length=0.38).set_fill(FLARE, op)
                    .set_stroke(AMBER, 1.0, 0.45))

        # the wall runs oldest (top) -> newest (bottom): the window is the NEWEST rows
        window_src = VGroup(*wall[-14:])
        row = VGroup(*[window_cell(0.55 + 0.4 * ((i * 37) % 7) / 7).move_to(slot(i))
                       for i in range(n_slots)])
        self.play(ReplacementTransform(window_src, row), run_time=1.0)
        live = list(row)
        add_shimmer(live)

        def roll():
            """One consecutive roll: a new cell enters right, all shift left one
            slot, the oldest leaves left. Returns the animations."""
            clear_shimmer(live)
            fresh = window_cell(0.9).move_to(slot(n_slots - 1))
            oldest = live.pop(0)
            anims = [FadeIn(fresh, shift=LEFT * slot_w),
                     *[c.animate.move_to(slot(i)) for i, c in enumerate(live)],
                     FadeOut(oldest, shift=LEFT * slot_w)]
            live.append(fresh)
            return anims

        # "onto the client" — the rest of the burden becomes the wallet's proof
        self.pad_to(A("onto the client") - 0.4)
        self.play(FadeIn(wallet, scale=1.04), FadeIn(w_label, shift=UP * 0.1), run_time=0.6)
        burden = VGroup(*wall[:-14])
        token = proof_token(0.26)
        token.move_to(wallet.get_center())
        # the cells stream into the wallet and condense into its proof token
        # (a staggered flight, not a 70-to-2 morph, which smears into a blob)
        dest = token.get_center()
        self.play(LaggedStart(
            LaggedStart(*[c.animate.move_to(dest).scale(0.25).set_opacity(0)
                          for c in reversed(burden)], lag_ratio=0.012),
            FadeIn(token, scale=2.5),
            lag_ratio=0.55), run_time=1.6)
        self.remove(burden)

        # "consensus only has to check a proof"
        self.pad_to(A("check a proof") - 1.4)
        ghost = token.copy()
        g_at = validator.get_center() + DOWN * 0.55 + LEFT * 0.35
        self.play(ghost.animate.move_to(g_at), run_time=1.0)
        check = checkmark(0.5).next_to(ghost, RIGHT, buff=0.3)
        self.play(ShowCreation(check), run_time=0.6)
        self.play(FadeOut(ghost, scale=0.6), FadeOut(check), run_time=0.6)
        add_shimmer(live)

        # "a rolling window of recent history... everything older gets pruned"
        self.pad_to(A("rolling window") - 0.5)
        cap = rich_line([("the validator keeps", TXT), ("a rolling window", FLARE),
                         ("of recent history", TXT)])
        cap.move_to(UP * CAPTION_Y)
        self.play(FadeIn(cap, shift=UP * 0.12), run_time=0.7)
        for k in range(3):
            self.play(*roll(), run_time=0.9)
        add_shimmer(live)
        self.play(FadeOut(cap), run_time=0.4)

        # "the spender shows up carrying the missing piece... appears nowhere"
        self.pad_to(AA(["spender shows up", "spenders shows up", "shows up"]) - 0.4)
        clear_shimmer(live)
        stage = VGroup(validator, v_label, wallet, w_label, *live)
        self.play(stage.animate.shift(UP * LIFT),
                  token.animate.move_to([0, STAGE_Y + LIFT + 0.2, 0]), run_time=1.0)
        add_shimmer(live)
        past = cells(10, side=0.4, opacity_lo=0.2).arrange(RIGHT, buff=0.09)
        past.move_to([0, -1.95, 0])
        past.set_opacity(0.3)
        past_label = label("pruned history", size=FS_LABEL, color=MUT)
        past_label.next_to(past, DOWN, buff=0.2)
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.1) for c in past], lag_ratio=0.06),
                  FadeIn(past_label), run_time=0.8)
        # the proof's claim, checked against every pruned cell
        excl = mtex('"nf" in.not "pruned past"', size=FS_BODY, color=GOLD)
        excl.move_to([0, (token.get_bottom()[1] + past.get_top()[1]) / 2 - 0.1, 0])
        self.pad_to(A("appears nowhere") - 0.9)
        self.play(
            LaggedStart(*[c.animate(rate_func=there_and_back).set_stroke(GOLD, 3.0, 1.0)
                          for c in past], lag_ratio=0.12),
            FadeIn(excl, shift=DOWN * 0.1),
            run_time=1.8,
        )
        self.play(FadeOut(excl), FadeOut(past, shift=DOWN * 0.1),
                  FadeOut(past_label, shift=DOWN * 0.1),
                  token.animate.move_to(wallet.get_center()), run_time=1.0)

        # "a moving target" — a real hash chain; the validator's window is its tail
        BW, STEP, CY = 0.8, 1.22, -2.45
        x0 = -STEP * 3.5            # centred once all 8 blocks have landed
        blocks = [block(BW, 0.56) for _ in range(5)]
        for i, b in enumerate(blocks):
            b.move_to([x0 + STEP * i, CY, 0])
        links = [chain_link(blocks[i], blocks[i + 1]) for i in range(4)]
        blocks[0].fade(0.6)   # already outside the window: pruned (fade, not set_opacity)

        def win_brace():
            return bracket(VGroup(*blocks[-4:]), color=FLARE)

        brace = win_brace()
        b_label = label("validator's window", size=FS_LABEL, color=FLARE)
        b_label.next_to(brace, UP, buff=0.12)
        self.pad_to(A("moving target") - 0.3)
        self.play(LaggedStart(*[FadeIn(b, shift=RIGHT * 0.15) for b in blocks],
                              lag_ratio=0.12),
                  LaggedStart(*[ShowCreation(l) for l in links], lag_ratio=0.12),
                  LaggedStart(Animation(Mobject()), GrowFromCenter(brace),
                              FadeIn(b_label, shift=UP * 0.1), lag_ratio=0.5),
                  run_time=1.2)

        # each append: the block lands, the window slides one block (in the chain
        # AND in the validator's row), and the new block folds into the proof
        pcd = rich_line([("each new block folds into", TXT), ("a fresh proof", GOLD)])
        pcd.move_to(UP * CAPTION_Y)
        beats = [A("every new block") - 0.2, A("incrementally") - 0.3, A("folds") - 0.2]
        for k, t in enumerate(beats):
            if k == 2:
                self.pad_to(A("each update") - 0.2)
                self.play(FadeIn(pcd, shift=UP * 0.1), run_time=0.6)
            self.pad_to(t)
            nb = block(BW, 0.56)
            nb.move_to(blocks[-1].get_center() + RIGHT * STEP)
            lk = chain_link(blocks[-1], nb)
            leaving = blocks[-4]
            blocks.append(nb)
            links.append(lk)
            self.play(FadeIn(nb, shift=LEFT * 0.25), ShowCreation(lk),
                      Transform(brace, win_brace()),
                      b_label.animate.shift(RIGHT * STEP),
                      leaving.animate.fade(0.6),
                      *roll(), run_time=0.8)
            ghost = nb.copy()
            ghost.set_fill(GOLD, 0.4)
            self.play(ghost.animate.move_to(token.get_center()).scale(0.5).set_opacity(0),
                      run_time=0.8)
            self.remove(ghost)
            self.play(token[0].animate(rate_func=there_and_back).scale(1.45)
                      .set_stroke(GOLD, 4, 1.0), run_time=0.5)
        add_shimmer(live)

        # "Tachyon runs on Ragu" — the wallet docks (icon only), the box takes stage
        self.pad_to(A("Tachyon runs") - 0.4)
        clear_shimmer(live)
        docked = VGroup(wallet, token)
        self.play(FadeOut(VGroup(validator, v_label, *live, w_label)),
                  docked.animate.scale(0.38).to_corner(DL, buff=0.3),
                  FadeOut(VGroup(*blocks, *links, brace, b_label, pcd)),
                  FadeOut(principle, shift=UP * 0.2), run_time=1.2)

        # while it holds nothing but its name, the box is sized to that name (a closed
        # black box); it opens to full size when the two facts arrive
        big_box = panel(10.4, 5.3, color=STAR, fill_opacity=0.03, stroke_opacity=0.7)
        big_box.move_to(UP * 0.2)
        box_title = heading("Ragu", size=FS_TITLE)
        sub_a = label("a recursive proof system", size=FS_LABEL, color=MUT)
        sub_b = label("treated as a black box", size=FS_LABEL, color=MUT)
        head = VGroup(box_title, sub_a).arrange(RIGHT, buff=0.45)
        # share a baseline: 'R' and 'a' both sit on it
        sub_a.shift(UP * (box_title[0].get_bottom()[1] - sub_a[0].get_bottom()[1]))
        box = panel(head.get_width() + 1.6, 2.2, color=STAR, fill_opacity=0.03,
                    stroke_opacity=0.7).move_to(UP * 0.2)
        head.move_to(box)
        sub_b.move_to(sub_a, aligned_edge=LEFT)
        sub_b.shift(UP * (sub_a[0].get_bottom()[1] - sub_b[0].get_bottom()[1]))
        self.play(ShowCreation(box), FadeIn(box_title, shift=DOWN * 0.1),
                  FadeIn(sub_a, shift=DOWN * 0.1), run_time=1.2)
        # "built for exactly this" — callback to the incremental proof the wallet holds
        self.pad_to(A("exactly this") - 0.2)
        self.play(Indicate(token, color=GOLD, scale_factor=1.5), run_time=0.8)
        self.pad_to(A("not going to open") - 0.15)
        self.play(box.animate(rate_func=there_and_back).set_stroke(STAR, 4.5, 1.0),
                  FadeTransform(sub_a, sub_b), run_time=1.3)

        ROW1, ROW2 = 1.0, -0.95
        NX, TX = -4.45, 0.2      # number column, text column (left edge)
        one = heading("1", size=FS_HEAD, color=AMBER).move_to([NX, ROW1, 0])
        two = heading("2", size=FS_HEAD, color=AMBER).move_to([NX, ROW2, 0]).set_opacity(0.35)
        self.pad_to(A("only need two") - 0.1)
        head_shift = (big_box.get_top()[1] - 0.35 - head.get_top()[1]) * UP
        self.play(Transform(box, big_box), VGroup(box_title, sub_b).animate.shift(head_shift),
                  run_time=0.8)
        self.play(FadeIn(one, shift=RIGHT * 0.12),
                  FadeIn(two, shift=RIGHT * 0.12), run_time=0.7)

        # fact 1: two proofs fold into one — and become the token the wallet carries
        self.pad_to(A("folds proofs into proofs") - 0.3)
        p1 = Dot(radius=0.26).set_fill(GOLD, 1.0).move_to([-3.4, ROW1, 0])
        p2 = Dot(radius=0.26).set_fill(AMBER, 1.0).move_to([-1.9, ROW1, 0])
        f1 = label("cheap proof folding", size=FS_BODY, color=TXT)
        f1.move_to([TX, ROW1, 0], aligned_edge=LEFT)
        self.play(FadeIn(p1, scale=1.3), FadeIn(p2, scale=1.3),
                  FadeIn(f1, shift=RIGHT * 0.12), run_time=0.9)
        mid = np.array([-2.65, ROW1, 0])
        folded = proof_token(0.26).move_to(mid)
        self.play(p1.animate.move_to(mid), p2.animate.move_to(mid), run_time=0.8)
        self.play(ReplacementTransform(VGroup(p1, p2), folded), run_time=0.7)
        # ...which is exactly the concentric mark the wallet is carrying
        self.play(Indicate(token, color=GOLD, scale_factor=1.6), run_time=0.8)

        # fact 2: committed polynomial = sealed envelope f(X); a native query → f(5) = 97
        self.pad_to(A("second") - 0.2)
        self.play(VGroup(one, folded, f1).animate.fade(0.5),
                  two.animate.set_opacity(1.0), run_time=0.8)
        env = envelope(1.9, 1.15)
        env.move_to([-1.95, ROW2, 0])
        self.pad_to(A("committed polynomials") - 1.2)
        query = mtex("x = 5", size=FS_BODY, color=GOLD)
        query.move_to([-3.6, ROW2, 0])
        self.play(FadeIn(query, shift=RIGHT * 0.1), FadeIn(env, scale=1.1), run_time=0.9)
        # one spot inside the sealed envelope, opened by a native query
        spot = RoundedRectangle(width=0.26, height=0.19, corner_radius=0.03)
        spot.set_fill(STAR, 0.95)
        spot.set_stroke(width=0)
        spot.move_to(env[0].get_center() + RIGHT * 0.5 + DOWN * 0.22)
        evaltex = mtex("f(5) = 97", size=FS_HEAD + 4, color=GOLD)
        f2 = label("native polynomial evaluation", size=FS_BODY, color=TXT)
        notc = label("in-circuit constraints", size=FS_LABEL, color=MUT)
        fact2 = VGroup(evaltex, f2, notc).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        fact2.move_to([TX, ROW2 - 0.15, 0], aligned_edge=LEFT)
        notc_x = strike(notc, color=FLARE, over=0.08)
        qarrow = tarrow(query.get_right() + RIGHT * 0.12, spot.get_center() + LEFT * 0.06,
                        color=GOLD, width=SW_THIN)
        self.play(ShowCreation(qarrow), FadeIn(spot, scale=1.5), run_time=0.5)
        self.play(FadeIn(evaltex, shift=RIGHT * 0.12), run_time=0.8)
        self.play(FadeIn(f2, shift=RIGHT * 0.12), run_time=0.6)
        # "...not as circuit constraints"
        self.pad_to(A("not as circuit") - 0.2)
        self.play(FadeIn(notc), run_time=0.4)
        self.play(ShowCreation(notc_x), notc.animate.set_opacity(0.6), run_time=0.5)

        # "keep that in your pocket" — the Ragu box collapses into a corner badge
        badge_env = envelope(0.75, 0.46)[:2]
        badge = VGroup(proof_token(0.13), badge_env, label("Ragu", size=FS_LABEL, color=STAR))
        badge.arrange(RIGHT, buff=0.28)
        badge = boxed(badge, color=STAR, pad=0.18, fill=0.04)
        badge.to_corner(DR, buff=0.3)
        self.pad_to(A("your pocket") - 0.8)
        ragu = VGroup(box, box_title, sub_b, one, two, folded, f1, query, env, spot, qarrow,
                      fact2, notc_x)
        self.play(FadeOut(docked),
                  ragu.animate.scale(0.18).move_to(badge).set_opacity(0),
                  FadeIn(badge, scale=1.6),
                  run_time=1.4)
        self.remove(ragu)

        # "four moves" — the plan takes the main stage
        names = [("the key", "split"), ("evolving", "nullifiers"),
                 ("one", "accumulator"), ("shared", "evidence")]
        keys = ["key structure", "that evolve", "accumulator", "proof tree"]
        cards = VGroup()
        for i, (a, b) in enumerate(names):
            c = panel(2.85, 3.1, color=GOLD, fill_opacity=0.06)
            n = heading(str(i + 1), size=60, color=AMBER)
            t = two_line(a, b, size=FS_BODY, color=STAR)
            VGroup(n, t).arrange(DOWN, buff=0.3).move_to(c)
            cards.add(VGroup(c, n, t))
        # numbers and text share baselines across cards (descenders vary per card):
        # lining digits sit on the baseline, two_line() rows are baseline-fixed
        for c in cards[1:]:
            c[1].align_to(cards[0][1], DOWN)
            c[2].match_y(cards[0][2])
        cards.arrange(RIGHT, buff=0.5).move_to(DOWN * 0.05)
        arrows = VGroup(*[
            tarrow(cards[i][0].get_right(), cards[i + 1][0].get_left(),
                   color=MUT, width=SW, buff=0.08)
            for i in range(3)
        ])
        plan = scene_title("the plan: four moves")
        self.pad_to(A("four moves") - 0.2)
        self.play(FadeIn(plan, shift=DOWN * 0.15), run_time=0.6)
        for i, key in enumerate(keys):
            self.pad_to(A(key) - 0.2)
            anims = [FadeIn(cards[i], shift=UP * 0.35, scale=1.05)]
            if i > 0:
                anims.append(GrowFromPoint(arrows[i - 1], arrows[i - 1].get_left()))
            self.play(*anims, run_time=0.9)

        self.pad_to(A("built once") - 0.2)
        self.play(Indicate(cards[3], color=GOLD, scale_factor=1.06), run_time=1.0)
        self.pad_to(T_02)

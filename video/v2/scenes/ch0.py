"""Chapter 0 — Prologue: the set nobody can prune (scenes 0.1, 0.2)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style import *  # noqa: E402,F403


def merkle_tree(depth=4, width=5.0, height=3.0, color=STAR):
    """Binary tree, root on top. Returns (levels, edges); levels[0] = [root]."""
    levels = []
    for d in range(depth):
        n = 2 ** d
        y = height / 2 - d * height / (depth - 1)
        xs = [(-width / 2 + (i + 0.5) * width / n) for i in range(n)]
        levels.append(VGroup(*[
            Dot([x, y, 0], radius=0.075 if d < depth - 1 else 0.065).set_fill(color, 0.9)
            for x in xs]))
    edges = VGroup()
    for d in range(1, depth):
        for i, c in enumerate(levels[d]):
            p = levels[d - 1][i // 2]
            edges.add(Line(p.get_center(), c.get_center(), stroke_width=SW_THIN,
                           stroke_color=MUT, stroke_opacity=0.7))
    return levels, edges


def nf_grid(rows, cols, cell=0.26, gap=0.06, opacity=0.55):
    g = VGroup(*[
        Square(cell).set_stroke(width=0).set_fill(FLARE, opacity)
        for _ in range(rows * cols)])
    g.arrange_in_grid(rows, cols, buff=gap)
    return g


def title_card():
    """Logo + title (v1 act0 cold-open card). Shared by Scene00 and Scene01's first frame."""
    logo = ImageMobject(LOGO_PNG)
    logo.set_height(1.8)
    title = heading("Scaling Zcash with Tachyon", size=60)
    return Group(logo, title).arrange(DOWN, buff=0.45)


def word_end(sid, phrase, occ=1):
    """End time of the last word of the occ-th `phrase` (a held pause starts here)."""
    import re
    seq = []
    for x in WORDS[sid]:
        parts = [p for p in re.split(r"[\s\-]+", x["w"]) if re.sub(r"[^a-z0-9]", "", p.lower())]
        for p in parts or [x["w"]]:
            seq.append((x["e"], re.sub(r"[^a-z0-9]", "", p.lower())))
    target = [re.sub(r"[^a-z0-9]", "", w.lower()) for w in re.split(r"[\s\-]+", phrase)]
    target = [w for w in target if w]
    hits = 0
    for i in range(len(seq) - len(target) + 1):
        if [w for _, w in seq[i:i + len(target)]] == target:
            hits += 1
            if hits == occ:
                return seq[i + len(target) - 1][0]
    raise ValueError(f"phrase not found in {sid}: {phrase!r}")


class Scene00(TimedScene):
    """0.0 — 2 s silent title card (audio/final/scene-0.0.mp3 is silence)."""

    def construct(self):
        card = title_card()
        logo, title = card
        self.wait(0.2)
        self.play(FadeIn(logo, scale=1.08), FadeIn(title, shift=UP * 0.2), run_time=1.1)
        self.pad_to(2.0)


class Scene01(TimedScene):
    def construct(self):
        SID = "0.1"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731
        E = lambda p, o=1: word_end(SID, p, o)  # noqa: E731

        # --- two sets, same growth -------------------------------------------
        levels, edges = merkle_tree(depth=4, width=4.6, height=2.6)
        tree = VGroup(edges, *levels).move_to(LEFT * 3.4 + UP * 0.35)
        grid = nf_grid(6, 10).move_to(RIGHT * 3.4 + UP * 0.35)
        lt = label("note commitments", size=FS_HEAD, color=STAR).next_to(tree, UP, buff=0.45)
        rt = label("nullifiers", size=FS_HEAD, color=FLARE).next_to(grid, UP, buff=0.45)
        rt.match_y(lt)
        divider = DashedLine(UP * 2.9, DOWN * 2.6, dash_length=0.12).set_stroke(DIM, SW_THIN, 0.6)

        leaves = levels[-1]
        inner = VGroup(*levels[1:-1])
        root = levels[0]
        card = title_card()  # continuity: open on Scene00's final frame, lift it away
        self.add(card)
        self.play(FadeOut(card, shift=0.4 * UP), run_time=0.6)
        self.play(ShowCreation(divider), FadeIn(lt, shift=0.2 * DOWN),
                  FadeIn(rt, shift=0.2 * DOWN), run_time=1.0)
        self.play(FadeIn(root, scale=0.5), FadeIn(inner, scale=0.5), ShowCreation(edges),
                  LaggedStart(*[FadeIn(l, scale=0.4) for l in leaves[:2]], lag_ratio=0.3),
                  LaggedStart(*[FadeIn(c, scale=0.4) for c in grid[:20]], lag_ratio=0.05),
                  run_time=1.8)
        # "one entry for every note that's created" -> a leaf per created note
        self.pad_to(A("one entry") - 0.2)
        self.play(LaggedStart(*[FadeIn(l, scale=0.4) for l in leaves[2:4]], lag_ratio=0.4),
                  run_time=1.2)
        # "and then one for every note that's spent" -> a cell per spent note
        self.pad_to(A("then one for") - 0.2)
        self.play(LaggedStart(*[FadeIn(c, scale=0.4) for c in grid[20:40]], lag_ratio=0.04),
                  run_time=1.2)
        # PAUSE: both sets grow side by side, in lockstep
        self.pad_to(E("note that's spent"))
        waves = [AnimationGroup(FadeIn(leaves[4 + k], scale=0.4),
                                *[FadeIn(c, scale=0.4) for c in grid[40 + 5 * k:45 + 5 * k]])
                 for k in range(4)]
        self.play(LaggedStart(*waves, lag_ratio=0.45), run_time=1.2)

        # --- left: append-only tree, prunes down to its frontier ------------------------
        self.pad_to(A("on the left") - 0.2)
        self.play(Indicate(lt, color=GOLD, scale_factor=1.08),
                  rt.animate.set_opacity(0.45), grid.animate.set_opacity(0.25), run_time=1.0)
        self.pad_to(A("append only") - 0.2)
        app = label("append-only", size=FS_LABEL, color=MUT).move_to(LEFT * 3.4 + DOWN * 1.55)
        self.play(FadeIn(app, shift=0.1 * UP), run_time=0.6)
        # frontier = one node per level along the right edge
        frontier = VGroup(*[levels[d][-1] for d in range(len(levels))])
        others = VGroup(*[levels[d][i] for d in range(1, len(levels))
                          for i in range(len(levels[d]) - 1)])
        self.pad_to(A("tree's frontier") - 0.2)
        self.play(*[d.animate.set_fill(GOLD, 1).scale(1.4) for d in frontier], run_time=0.9)
        self.pad_to(A("one hash per level") - 0.2)
        self.play(LaggedStart(*[Flash(d.get_center(), color=GOLD, flash_radius=0.28)
                                for d in frontier], lag_ratio=0.3), run_time=1.0)
        self.pad_to(A("everything else") - 0.2)
        self.play(others.animate.set_opacity(0.4), edges.animate.set_opacity(0.3), run_time=0.8)
        # PAUSE: the tree prunes down to its frontier; O(log n) settles beside it
        self.pad_to(E("its size"))
        olog = mtex("O(log n)", size=FS_BODY, color=GOLD).next_to(frontier, LEFT, buff=0.7)
        olog.match_y(frontier)
        self.play(LaggedStart(*[FadeOut(m, scale=0.5) for m in reversed(others)], lag_ratio=0.06),
                  FadeOut(edges), run_time=0.85)
        self.play(FadeIn(olog, shift=0.15 * RIGHT), run_time=0.4)

        # --- right: exclusion against all history, in memory ---------------------------
        self.pad_to(A("on the right") - 0.2)
        left_all = VGroup(lt, frontier, app, olog)
        self.play(left_all.animate.fade(0.65), rt.animate.set_opacity(1),
                  grid.animate.set_opacity(0.55), run_time=0.8)
        self.play(Indicate(rt, color=FLARE, scale_factor=1.08), run_time=0.6)
        self.pad_to(A("every transaction") - 0.2)
        tx = mtex('"nf"', size=FS_BODY, color=STAR)
        tx_box = boxed(tx, color=STAR, pad=0.14, fill=0.08).move_to(RIGHT * 3.4 + DOWN * 2.1)
        self.play(FadeIn(tx_box, shift=0.3 * UP), run_time=0.7)
        # probes sweep every cell: exclusion vs ALL history
        self.pad_to(A("exclusion test") - 0.3)
        ask = mtex('"nf" in.not "history" ?', size=FS_BODY, color=STAR).next_to(tx_box, RIGHT, buff=0.3)
        ask.shift(LEFT * max(0, ask.get_right()[0] - 6.6))
        sweep = Rectangle(width=0.08, height=grid.get_height() + 0.3).set_fill(STAR, 0.7)
        sweep.set_stroke(width=0).move_to(grid.get_left() + LEFT * 0.1)
        self.play(FadeIn(ask), run_time=0.6)
        self.play(sweep.animate.move_to(grid.get_right() + RIGHT * 0.1), run_time=1.6,
                  rate_func=linear)
        self.play(FadeOut(sweep), run_time=0.3)
        # memory frame on the critical path
        self.pad_to(A("in memory") - 0.3)
        ram = SurroundingRectangle(grid, buff=0.2).set_stroke(FLARE, SW, 0.9)
        ram_lab = label("memory", size=FS_LABEL, color=FLARE).next_to(ram, RIGHT, buff=0.15)
        ram_lab.rotate(PI / 2).next_to(ram, RIGHT, buff=0.12)
        self.play(ShowCreation(ram), FadeIn(ram_lab), run_time=0.6)
        self.pad_to(A("critical path") - 0.2)
        crit = label("on every validator's critical path", size=FS_LABEL, color=FLARE)
        crit.next_to(ram, DOWN, buff=0.25)
        self.play(FadeOut(VGroup(tx_box, ask)), FadeIn(crit, shift=0.1 * UP), run_time=0.8)

        # --- Visa-level throughput: the grid outgrows everything ---------------------------
        self.pad_to(A("make matters worse") - 0.3)
        self.play(FadeOut(VGroup(left_all, divider, crit, ram_lab)), run_time=0.8)
        self.pad_to(A("visa level") - 0.2)
        big = nf_grid(22, 44, cell=0.2, gap=0.045, opacity=0.5).move_to(DOWN * 0.15)
        order = sorted(range(len(big)), key=lambda i: np.linalg.norm(big[i].get_center() - grid.get_center()))
        self.play(FadeOut(VGroup(grid, ram)), rt.animate.move_to(UP * TITLE_Y),
                  LaggedStart(*[FadeIn(big[i], scale=0.3) for i in order], lag_ratio=0.0012),
                  run_time=3.4)
        steps = list(range(0, 501, 25))
        digits = [mtex(str(v), size=64, color=STAR) for v in steps]
        counter = digits[0].copy()
        unit = label("GB / day", size=FS_HEAD, color=STAR)
        plate = RoundedRectangle(width=5.4, height=1.4, corner_radius=0.15)
        plate.set_fill(VOID, 0.92).set_stroke(FLARE, SW, 1.0).move_to(UP * 0.1)
        anchor_pt = plate.get_center() + LEFT * 0.45
        unit.next_to(anchor_pt + RIGHT * 0.05, RIGHT, buff=0.25)
        counter.move_to(anchor_pt, aligned_edge=RIGHT)
        # "nothing in it can ever be thrown away"
        self.pad_to(A("thrown away") - 0.4)
        never = label("never prunable", size=FS_BODY, color=FLARE).next_to(plate, DOWN, buff=0.3)
        never_bg = BackgroundRectangle(never, color=VOID, fill_opacity=0.9, buff=0.12)
        self.play(FadeIn(never_bg), FadeIn(never, shift=0.1 * UP), run_time=0.6)

        # PAUSE: the counter rolls to 500 GB / day
        def tick(m, a):
            k = min(int(rush_from(a) * (len(digits) - 1) + 0.5), len(digits) - 1)
            m.become(digits[k].copy().move_to(anchor_pt, aligned_edge=RIGHT))
        self.pad_to(E("thrown away"))
        self.add(plate, counter, unit)
        self.play(FadeIn(plate), FadeIn(unit), UpdateFromAlphaFunc(counter, tick), run_time=1.2)
        # a nullifier from ten years ago still blocks today's double spend
        self.pad_to(A("ten years") - 0.3)
        old = big[len(big) - 44]  # bottom-left cell
        ring = Circle(radius=0.22).set_stroke(STAR, SW_BOLD).move_to(old)
        probe = Line(UP * 3.0 + LEFT * 4.0, old.get_center(), stroke_color=STAR, stroke_width=SW)
        self.play(ShowCreation(ring), old.animate.set_fill(STAR, 1), run_time=0.7)
        self.pad_to(A("double spend") - 0.4)
        self.play(ShowCreation(probe), run_time=0.6)
        self.play(Flash(old.get_center(), color=FLARE, flash_radius=0.35), run_time=0.6)

        # --- a fundamental scaling limitation ----------------------------------------------
        self.pad_to(A("fundamental") - 0.2)
        self.play(FadeOut(VGroup(probe, ring, never, never_bg, plate, counter, unit)),
                  big.animate.set_opacity(0.85), run_time=0.8)
        self.pad_to(A("nobody can prune") - 1.0)
        punch = label("One set nobody can prune.", size=FS_TITLE, color=STAR)
        punch_bg = BackgroundRectangle(punch, color=VOID, fill_opacity=0.92, buff=0.25)
        self.play(FadeIn(punch_bg), Write(punch), run_time=1.2)
        self.pad_to(scene_T(SID))


class Scene02(TimedScene):
    def construct(self):
        SID = "0.2"
        A = lambda p, o=1: anchor(SID, p, o)  # noqa: E731
        E = lambda p, o=1: word_end(SID, p, o)  # noqa: E731

        # rebuild the end-state of 0.1 compactly: the hot grid, center
        grid = nf_grid(10, 20, cell=0.2, gap=0.045, opacity=0.55).move_to(DOWN * 0.1)
        self.add(grid)
        self.wait(0.4)

        # --- principle --------------------------------------------------------------------
        self.pad_to(A("one principle") - 0.3)
        title = scene_title("Client-side validation")
        self.play(Write(title), run_time=1.0)
        val = panel(5.0, 3.8, color=FLARE, fill_opacity=0.04).move_to(LEFT * 3.6 + DOWN * 0.2)
        val_lab = label("consensus", size=FS_BODY, color=FLARE).next_to(val, UP, buff=0.15)
        wal = panel(5.0, 3.8, color=GOLD, fill_opacity=0.04).move_to(RIGHT * 3.6 + DOWN * 0.2)
        wal_lab = label("client", size=FS_BODY, color=GOLD).next_to(wal, UP, buff=0.15)
        self.pad_to(A("move validation") - 0.2)
        self.play(grid.animate.scale(0.9).move_to(val.get_center()),
                  FadeIn(val), FadeIn(val_lab), run_time=1.2)
        self.pad_to(A("onto the client") - 0.3)
        arr = tarrow(val.get_right(), wal.get_left(), color=GOLD, width=SW)
        self.play(FadeIn(wal), FadeIn(wal_lab), GrowFromPoint(arr, val.get_right()), run_time=1.0)

        # --- consensus keeps a recent window; older history is cut loose ----------------------
        cols = 20
        recent = VGroup(*[grid[r * cols + c] for r in range(10) for c in range(cols - 3, cols)])
        older = VGroup(*[grid[r * cols + c] for r in range(10) for c in range(cols - 3)])
        self.pad_to(A("consensus keeps only") - 0.2)
        self.play(recent.animate.set_fill(FLARE, 0.9), older.animate.set_fill(FLARE, 0.4),
                  run_time=0.8)
        self.pad_to(A("recent history") - 0.2)
        win_lab = label("recent window", size=FS_LABEL, color=FLARE)
        win_lab.next_to(recent, DOWN, buff=0.18).align_to(recent, RIGHT)
        self.play(FadeIn(win_lab, shift=0.1 * UP), run_time=0.6)
        self.pad_to(A("pruned from") - 0.3)
        cut = DashedLine(UP, DOWN, dash_length=0.08).set_stroke(STAR, SW, 0.9)
        cut.set_height(grid.get_height() + 0.3).move_to(
            (recent.get_left() + older.get_right()) / 2)
        self.play(ShowCreation(cut), run_time=0.6)
        # PAUSE: the grid is scissored; the older history flies off to the client
        self.pad_to(E("validator state"))
        older.generate_target()
        older.target.scale(0.4).move_to(wal.get_center() + LEFT * 1.4 + UP * 0.7)
        older.target.set_fill(FLARE, 0.35)
        kept = VGroup(recent, win_lab)
        self.play(MoveToTarget(older, path_arc=-0.5),
                  kept.animate.move_to(val.get_center()), FadeOut(cut), run_time=1.1)

        self.pad_to(A("a proof") - 0.3)
        tok = proof_token(0.22).move_to(wal.get_center() + RIGHT * 0.9 + UP * 0.6)
        claim = rich([('$"nf"$', STAR), ("appears nowhere in", TXT), ("older history", MUT)],
                     size=FS_LABEL)
        claim.set_max_width(wal.get_width() - 0.4).move_to(wal.get_center() + DOWN * 0.75)
        self.play(FadeIn(tok, scale=0.4), run_time=0.7)
        self.pad_to(A("doesn't appear") - 0.2)
        self.play(FadeIn(claim, lag_ratio=0.3), run_time=1.2)

        # --- the proof must keep up with every block ------------------------------------------
        self.pad_to(A("every new block") - 0.4)
        blocks = VGroup(*[block(0.5, 0.36) for _ in range(6)]).arrange(RIGHT, buff=0.35)
        blocks.move_to(DOWN * 2.75)
        links = VGroup(*[chain_link(a, b) for a, b in zip(blocks[:-1], blocks[1:])])
        chain_lab = label("chain", size=FS_LABEL, color=MUT).next_to(blocks, LEFT, buff=0.3)
        self.play(FadeIn(blocks[:2]), ShowCreation(links[0]), FadeIn(chain_lab), run_time=0.6)
        rings = VGroup()
        for i in range(2, 6):
            r = Circle(radius=0.22 * 1.8 + 0.09 * (i - 1)).set_stroke(AMBER, 1.8, 0.8)
            r.move_to(tok)
            rings.add(r)

        def grow(i):
            self.play(FadeIn(blocks[i], shift=0.2 * LEFT), ShowCreation(links[i - 1]),
                      ShowCreation(rings[i - 2]), run_time=0.55)
        grow(2)
        grow(3)
        self.pad_to(A("built incrementally") - 0.2)
        grow(4)
        self.pad_to(A("proof carrying data") - 0.1)
        pcd = label("proof-carrying data", size=FS_LABEL, color=GOLD)
        pcd.next_to(claim, DOWN, buff=0.35)
        self.play(FadeIn(pcd, shift=0.1 * LEFT), run_time=0.7)
        self.pad_to(A("extended a little") - 0.2)
        grow(5)

        # --- Ragu: a black box with two parts -------------------------------------------------
        self.pad_to(A("all of this is running") - 0.2)
        stage_old = VGroup(val, val_lab, recent, win_lab, older, wal, wal_lab, arr, tok, rings,
                           claim, pcd, blocks, links, chain_lab, title)
        self.play(FadeOut(stage_old, lag_ratio=0.02), run_time=1.0)
        ragu = ragu_box().move_to(UP * 0.4)
        self.pad_to(A("on ragu") - 0.4)
        self.play(FadeIn(ragu.body), Write(ragu.name), run_time=1.0)
        facts = label("Halo lineage  ·  Pasta curves  ·  no trusted setup", size=FS_LABEL, color=MUT)
        facts.next_to(ragu, DOWN, buff=0.4)
        self.pad_to(A("halo") - 0.3)
        self.play(FadeIn(facts, lag_ratio=0.1), run_time=1.4)
        self.pad_to(A("two parts") - 0.3)
        self.play(FadeOut(facts), FadeIn(ragu.port_fuse, scale=2), FadeIn(ragu.port_query, scale=2),
                  run_time=0.7)

        # fuse part
        self.pad_to(A("fuse part") - 0.2)
        self.play(FadeIn(ragu.lab_fuse), Indicate(ragu.port_fuse, color=GOLD, scale_factor=1.8),
                  run_time=0.8)
        self.pad_to(A("two proofs") - 0.3)
        p1 = proof_token(0.18).move_to(LEFT * 6.0 + UP * 1.4)
        p2 = proof_token(0.18).move_to(LEFT * 6.0 + DOWN * 0.6)
        work = label("+ new work", size=FS_LABEL, color=TXT).move_to(LEFT * 5.5 + UP * 0.4)
        self.play(FadeIn(p1, scale=0.5), FadeIn(p2, scale=0.5), FadeIn(work), run_time=0.8)
        self.play(p1.animate.move_to(ragu.port_fuse), p2.animate.move_to(ragu.port_fuse),
                  work.animate.move_to(ragu.port_fuse).scale(0.3).set_opacity(0), run_time=1.0)
        self.pad_to(A("hands back") - 0.2)
        out = proof_token(0.24).move_to(ragu.port_fuse)
        self.remove(p1, p2, work)
        self.play(out.animate.move_to(LEFT * 5.6 + DOWN * 2.2), run_time=0.7)
        out_home = out.get_center().copy()
        self.pad_to(A("single proof") - 0.1)
        one = label("one proof", size=FS_LABEL, color=GOLD).next_to(out, RIGHT, buff=0.25)
        self.play(FadeIn(one), run_time=0.5)

        # query part
        self.pad_to(A("query part") - 0.2)
        self.play(FadeIn(ragu.lab_query), Indicate(ragu.port_query, color=CYAN, scale_factor=1.8),
                  run_time=0.8)
        self.pad_to(A("commit to a polynomial") - 0.2)
        env = envelope(1.5, 0.95, color=CYAN, tex_label="f(X)").move_to(RIGHT * 5.4 + UP * 1.6)
        self.play(FadeIn(env, shift=0.2 * DOWN), run_time=0.7)
        self.pad_to(A("name a point") - 0.2)
        pt = mtex("r = 5", size=FS_BODY, color=STAR).next_to(env, DOWN, buff=0.3)
        self.play(FadeIn(pt), run_time=0.5)
        self.play(env.animate.scale(0.5).move_to(ragu.port_query).set_opacity(0),
                  pt.animate.scale(0.5).move_to(ragu.port_query).set_opacity(0), run_time=0.5)
        self.remove(env, pt)
        self.pad_to(A("get back its value") - 0.1)
        val_out = mtex("f(5) = 97", size=FS_BODY, color=CYAN).move_to(ragu.port_query)
        self.play(val_out.animate.move_to(RIGHT * 5.3 + DOWN * 2.2), run_time=0.9)

        # PAUSE: both parts at work -- fuse merges two tokens, query answers one evaluation
        self.pad_to(E("its value"))
        p3 = proof_token(0.18).move_to(LEFT * 6.0 + UP * 1.4)
        self.play(FadeIn(p3, scale=0.5), run_time=0.2)
        self.play(out.animate.move_to(ragu.port_fuse), p3.animate.move_to(ragu.port_fuse),
                  run_time=0.4)
        self.remove(p3)
        self.play(out.animate.move_to(out_home), run_time=0.4)
        self.play(Flash(out_home, color=GOLD, flash_radius=0.45),
                  Flash(ragu.port_query.get_center(), color=CYAN, flash_radius=0.4),
                  val_out.animate.scale(1.12).set_color(STAR), run_time=0.3)
        self.play(val_out.animate.scale(1 / 1.12).set_color(CYAN), run_time=0.2)

        # evaluation claims are exposed and folded into the proof's own claims
        self.pad_to(A("evaluation claims") - 0.2)
        self.play(Indicate(val_out, color=STAR, scale_factor=1.12), run_time=0.8)
        self.pad_to(A("fold them") - 0.2)
        native = label("native: folded into the proof system's own claim", size=FS_LABEL, color=CYAN)
        native.next_to(ragu, UP, buff=0.5)
        seed = val_out.copy()
        self.play(seed.animate.move_to(out_home).scale(0.2).set_opacity(0),
                  FadeIn(native, shift=0.1 * DOWN), run_time=0.9)
        self.remove(seed)
        self.play(Flash(out_home, color=CYAN, flash_radius=0.45), run_time=0.5)
        self.pad_to(A("not paying") - 0.2)
        cc = label("not in circuit constraints", size=FS_LABEL, color=MUT).next_to(native, UP, buff=0.2)
        # intentional strike-through: a polyline, so the line-crosses-text lint skips it
        strike = VMobject().set_points_as_corners([cc.get_left(), cc.get_right()])
        strike.set_stroke(FLARE, SW)
        self.play(FadeIn(cc), run_time=0.5)
        self.pad_to(A("circuit constraints") + 0.3)
        self.play(ShowCreation(strike), run_time=0.5)
        self.pad_to(A("for performance") - 0.2)
        halo = SurroundingRectangle(VGroup(ragu.port_query, ragu.lab_query), buff=0.15)
        halo.set_stroke(CYAN, SW_BOLD).round_corners(0.1)
        self.play(VGroup(out, one, ragu.lab_fuse, ragu.port_fuse).animate.set_opacity(0.3),
                  ShowCreation(halo), run_time=0.9)
        self.pad_to(A("pretty critical") - 0.1)
        self.play(Flash(ragu.port_query.get_center(), color=CYAN, flash_radius=0.5), run_time=0.7)

        # --- epochs, and our note ------------------------------------------------------------
        self.pad_to(A("divided into") - 0.8)
        dock_target = VGroup(ragu, halo)
        self.play(FadeOut(VGroup(out, one, val_out, native, cc, strike, ragu.lab_fuse, ragu.lab_query)),
                  dock_target.animate.scale(0.6).to_corner(UR, buff=0.3), run_time=0.9)
        rail = EpochRail(first=4, last=10)
        self.play(ShowCreation(rail.line), LaggedStart(*[ShowCreation(g) for g in rail.gates],
                                                       lag_ratio=0.1),
                  FadeIn(rail.labels, lag_ratio=0.1), run_time=1.1)
        self.pad_to(A("long stretches") - 0.2)
        ep_word = label("epoch", size=FS_SMALL, color=MUT).next_to(rail.labels[0], LEFT, buff=0.3)
        mini = VGroup()
        for e in range(4, 11):
            bs = VGroup(*[block(0.24, 0.18) for _ in range(3)]).arrange(RIGHT, buff=0.06)
            bs.move_to(rail.center_of(e, dy=0.38))
            mini.add(bs)
        self.play(FadeIn(ep_word), LaggedStart(*[FadeIn(b, shift=0.1 * DOWN) for b in mini],
                                                lag_ratio=0.12), run_time=1.4)

        self.pad_to(A("follow one note") - 0.3)
        card = note_card(filled=False).move_to(UP * 0.6)
        card_lab = label("our note", size=FS_BODY, color=GOLD).next_to(card, UP, buff=0.3)
        self.play(FadeIn(card, scale=0.9), FadeIn(card_lab), run_time=1.0)
        self.pad_to(A("born in") - 0.1)
        birth = bead(GOLD, r=0.12).move_to(card.get_bottom())
        self.play(birth.animate.move_to(rail.center_of(5, dy=0.0)), run_time=1.0)
        self.pad_to(A("five") - 0.1)
        born = label("born", size=FS_SMALL, color=GOLD).move_to(rail.center_of(5, dy=0.95))
        self.play(FadeIn(born), Flash(birth.get_center(), color=GOLD, flash_radius=0.3),
                  run_time=0.6)
        self.pad_to(A("spent in") - 0.1)
        spend = Triangle().set_fill(FLARE, 1).set_stroke(width=0).scale(0.13).rotate(PI)
        spend.move_to(rail.center_of(9, dy=0.0))
        spent = label("spent", size=FS_SMALL, color=FLARE).move_to(rail.center_of(9, dy=0.95))
        self.play(GrowFromCenter(spend), FadeIn(spent), run_time=0.8)
        # PAUSE: the note card docks; its life 5 -> 9 draws itself along the rail
        self.pad_to(E("epoch nine"))
        span = Line(rail.center_of(5), rail.center_of(9), stroke_color=GOLD, stroke_width=SW,
                    stroke_opacity=0.6)
        self.play(VGroup(card, card_lab).animate.scale(0.75).to_corner(UL, buff=0.35),
                  ShowCreation(span), run_time=1.0)
        life = rich([("born", GOLD), ("$5$", GOLD), ("·", MUT), ("spent", FLARE), ("$9$", FLARE)],
                    size=FS_SMALL)
        life.next_to(card, DOWN, buff=0.2).align_to(card, LEFT)
        self.play(FadeIn(life, lag_ratio=0.2), run_time=0.4)
        # "...exactly when this note needs it": the docked card answers with a pulse
        self.pad_to(A("this note needs") - 0.2)
        self.play(VGroup(card, card_lab, life).animate.scale(1.08), rate_func=there_and_back,
                  run_time=0.8)
        self.pad_to(scene_T(SID))

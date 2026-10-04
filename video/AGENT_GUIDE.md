# Tachyon Explainer Video — Agent Guide

You are iterating on **one act** of a 3Blue1Brown-style explainer video. This file is
the complete working contract: every principle, workflow, and gotcha learned so far.
Read the linked files **only for your act** — do not pull the whole script into context.

## File map

| Path | What it is | Read policy |
|---|---|---|
| `SCRIPT.md` | Staged script: per-scene narration beats, VISUAL plans, design system, locked decisions | Read the header sections + **your act only** |
| `NARRATION.md` | Verbatim narration (matches the recorded audio) | Your act's scenes only |
| `anim/style.py` | Design system code: palette, helpers, typst math, anchors | Read fully (it's short) |
| `anim/act{N}.py` | Scene code, one file per act | Yours only |
| `anim/words.json` | Word-level timestamps for all 26 scenes (forced alignment of final audio) | Query it, don't read it raw |
| `audio/final/scene-X.Y.mp3` | Final narration clips: 1.08× speed + 1 s lead-in pad | Mux source |
| `audio/scene-X.Y.mp3` | Raw ElevenLabs output (pre-speed/pad) | Don't touch |
| `generate_audio.py` | ElevenLabs generation + retakes (`python generate_audio.py 2.3` retakes one scene) | Only for approved retakes |
| `anim/renders/SceneXY.mp4` | Rendered scenes (no audio) | Output |
| `demo/act{N}.mp4` | The deliverable per act (scenes + audio, concatenated) | Output |
| `book/src/revisit.md` | The authoritative spec | Reference for content questions |

## Hard rules

1. **Iterate per act.** Touch only your `anim/act{N}.py` and `demo/act{N}.mp4`. Never merge acts.
2. **Never spend ElevenLabs credits without Alex's explicit instruction.** Audio exists for all scenes. A retake is justified only for a pronunciation bug Alex confirms. After ANY retake: re-run speed/pad + re-align that scene (workflow below) — all its anchors shift.
3. **Never edit NARRATION.md text** — it matches recorded audio. Narration changes require Alex's approval + a retake.
4. **No LaTeX, no texlive, ever.** manim's `Tex`, `TexText`, and `Brace` are banned (they shell out to `latex`, which is not installed). Math goes through typst (below). For braces use `style.bracket(...)`.
5. Alex reviews each act by watching `demo/act{N}.mp4`. Rebuild it after every change; keep the same filename.

## Environment

- Python venv: `video/.venv` (manimgl 1.7.2 from 3b1b git). Render from `video/anim/`:
  `../.venv/bin/manimgl act0.py Scene01 -w` → writes `anim/renders/Scene01.mp4`.
- ffmpeg: system `ffmpeg` lacks libx264; **always use `video/bin/ffmpeg`** for encoding
  (manimgl is already configured to it via `anim/custom_config.yml`). `ffprobe` (system) is fine.
- `typst` is on PATH (0.15). Font: **New Computer Modern for EVERYTHING** — prose via
  typst `label()`/`heading()`/`itex()`, formulas via `mtex()` in New Computer Modern Math.
  Text and math are the same family (the LaTeX/3b1b look). Never introduce another face.
  The stack is `style.FONT_STACK` = NCM → NCM Math → DejaVu Sans. **DejaVu is a tripwire,
  not a choice**: NCM's *text* face lacks ⇒ ∝ ∪ ≤ ⊆ ⌐ ✓ ✗, which its *math* face supplies
  in matching Computer Modern weight — if a glyph reaches DejaVu it appears as an obviously
  heavier sans intruder. Subscript/superscript unicode (₁ ₂ ² ³) exists in NEITHER NCM face:
  never type it, write real math (`x_1`, `2^32`) via `mtex`.
  `_typst_svg` raises if typst reports `unknown font family` — typst otherwise warns and
  silently substitutes while still exiting 0, which would recolour the whole video unnoticed.

## Design system (full spec in SCRIPT.md header — load it)

- Deep-space background (#020204), brand palette: GOLD #D4A017, AMBER #E8820C,
  FLARE #FF6B00, CYAN #4A9EA0, STAR warm-white, TXT/MUT/DIM grays. All constants in `style.py`.
- **One typeface everywhere (Alex's 2026-10-03 call): New Computer Modern.**
  `label()`/`heading()`/`itex()` render through typst in NCM; `mtex()` math uses NCM Math —
  same family, so text and formulas match. **Never construct a manim `Text`/pango
  mobject** — that is the only way to get a second face on screen. `sans_label()` is now
  just an alias of `label()`. Need per-word colors (the old `Text(t2c=...)`)? Build a
  `VGroup` of `label()`s and `.arrange(RIGHT)`. Typst falls back NCM → DejaVu for missing
  glyphs (✗, ≠ all work).
- **Highlighting raster diagrams (e.g. the zcash_keys.png figure): never dim the image.**
  Circle components with `contour(...)` (irregular hand-drawn loop) or `dashed_box(...)`,
  placed via pixel-coordinate mapping (see `pix*` helpers in act1.py).
- **Role mapping (never deviate):** wallet/user = GOLD · OSS/service = CYAN ·
  shared evidence = STAR · hot/alert/cost = FLARE · QR residue = CYAN, non-residue = AMBER.
- **Exception:** legacy Zcash key diagrams use the canonical `book/src/assets/zcash_keys.png`
  colors (PNG_* constants in style.py, `kbox`/`karrow` helpers), sk at the BOTTOM, arrows up.
  Audience memory of that diagram outranks our theme. New Tachyon-side objects revert to brand colors.
- Spec SVGs in `book/src/assets/` are **content clues, not layouts**: take the topology and
  field names, redraw in our style. Never transplant their look.
- Established glyph vocabulary (reuse, don't reinvent): proof token = concentric ring+dot
  (`proof_token`), committed polynomial = sealed envelope with typst `f(X)` (`envelope`),
  Poseidon = sponge icon, nullifier = flare bead, validator/wallet/OSS = labeled `panel`s,
  blockchain = linked `block`s via `chain_link`, epoch axis with `e_i` ticks.

## 3b1b animation principles (the reason demo v1 was rejected)

1. **Continuity over cuts.** Objects morph and travel (`ReplacementTransform`, `TransformFromCopy`);
   new ideas grow out of things already on screen. Never fade-everything-out/fade-next-in.
   Each scene's opening state should reconstruct the previous scene's final frame when they chain.
2. **The frame is always alive.** Subtle idle motion (`add_shimmer`) while narration talks.
   No dead static holds.
3. **Emphasis lands ON the spoken word** (see sync workflow). When the voice says "ever,"
   the flash happens at the word "ever." This is the single highest-value property of the video.
4. **Show, don't label.** An evaluation query is an arrow hitting a spot on an envelope,
   not a bullet point. Text supports the picture, never replaces it.
5. **Old context shrinks to a corner** (scale + fade, keep legible) instead of vanishing —
   and can pulse later for callbacks (e.g. the wallet token during the fold explanation).
6. **Staggered, eased motion.** `LaggedStart(Map)` everywhere; nothing pops in instantly.

### Taste rules from Alex's reviews (treat as binding)

- **Concrete beats abstract.** `f(5) = 97`, not `f(x) = y`. Two circles folding into the
  wallet's token, not an abstract loop icon.
- **Semantic exactness.** A rolling window prunes the OLDEST element, consecutively, inside
  its container. A blockchain is a hash chain of linked blocks, not floating dots. If the
  animation's mechanics contradict the data structure's semantics, it's wrong.
- **All math in math type** (typst), never spelled out in the sans face. `pk_d` as sans text is ugly.
- Titles are PPT-style: top, centered. Diagrams first, then the title poses the question.
- Reasons/arguments get textified into succinct bullets BESIDE the diagram, landing on their words.
- Docked/background elements must never occlude main-stage content; main content takes upper-center.
- Scene lead-in: audio has a 1 s pad; don't start substantive motion before ~0.5 s.

## Layout & readability standard (2026-10-04 presentation pass — binding)

Alex's verdict on the first full draft: content right, presentation "far from passing
grade" (tiny text, content huddled in one quadrant, collisions). The fix is codified in
the layout system at the bottom of `style.py`:

- **Bands:** `scene_title()` at TITLE_Y (top) · stage between STAGE_TOP/STAGE_BOTTOM ·
  `caption()` at CAPTION_Y (bottom takeaway). Diagrams FILL the stage: `fit_in(mob, region)`
  with FULL_STAGE, or DIAGRAM_REGION (left ~60%) + NOTES_REGION (right ~40%) for
  diagram-plus-argument beats. Balance the frame; no half-empty screens.
- **Type scale:** FS_TITLE 46 · FS_HEAD 38 · FS_BODY 32 · FS_LABEL 28 · FS_SMALL 24 ·
  **FS_MIN 22 floor** for anything meant to be read (effective size, after scaling).
- **Helpers:** `pill` (step names/tags), `boxed`, `bullets` (row-by-row reveal), `rich`
  (per-run colors, prose+math), `tarrow` (themed thin arrow, snaps to box edges).
  Strokes: SW_THIN 2.2 / SW 3.0 / SW_BOLD 4.5. DIM was brightened; `panel` defaults are
  more opaque.
- **Layout linter:** every `pad_to()` lints the live frame (text < 22pt, text off the safe
  area, text/text overlap, a line crossing a label) → `anim/lint/<Scene>.txt`. Drive it to
  zero; justify any survivor.
- **Tooling:** `anim/qa.sh actN.py SceneNM [fast]` = render + 4×5 contact sheet
  (`anim/qa/<Scene>/sheet.png`) + optional full frames (`QA_TIMES="12 40"`) + lint print.
  `fast` is 480p for iteration only. `anim/build_act.sh N` muxes + concats → `demo/actN.mp4`
  (refuses non-1080p renders). `anim/lint_all.sh [acts]` = ~2-minute skip-mode sweep of
  every scene: exact beat timing + layout lint, no video. The linter also reports
  **late** beats (a `pad_to(t)` reached after t: run_times before it overflow the gap).
- **Anchor occurrence trap:** `anchor(sid, "ever", 2)` counts every match, including
  inside other sentences. Print the neighbouring words when choosing `occ` (the 0.1
  "Ever." flash fired on the wrong "ever" for two review rounds).

## Math: typst (not LaTeX)

`style.py` provides, all compiled via local `typst` and cached in `anim/typst_cache/`:

- `mtex('"pk" = "Com"("ak", "nk")', size=32, color=GOLD)` — math, **typst syntax**:
  quoted strings = upright roman (`"pk"_"d"`), bare letters italic math (`f(X)`),
  `alpha`, `psi`, `->`, `thin`. NOT LaTeX commands.
- `itex("Spending key", size=24)` — italic serif prose (diagram side labels).
- `tex_chip(...)` — math in a rounded chip; `key_chip(...)` — prose chip (sans is fine for prose).
- `kbox([...], PNG_FVK)` — zcash_keys.png-style box (light fill, dark border, dark math text).

## Audio→animation sync workflow (the core discipline)

Scenes are **beat-anchored to word timestamps**. Never hand-time a beat.

1. Anchors: `anchor("2.3", "cubic factor")` → start time (s) of that phrase in the final clip;
   `anchor_any(sid, [alternates])` for transcription-risky phrases. Scene code:
   `self.pad_to(A("phrase") - lead)` before the beat's `self.play(...)`.
2. **Validate every anchor phrase against `anim/words.json` BEFORE rendering** (a 10-line
   script: normalize words, search the phrase). Whisper quirks seen so far: epoch→"epic",
   bare→"bear", Pedersen→"peterson", trapdoor→"trap door", append-only→"a penned only",
   Tachyon→"tacky on" (that one is CORRECT — the TTS respells it), psi→"P-E-S-I"/"sesci",
   Faerie→"fairy", RedPallas→missing. When in doubt use `anchor_any` with 2–3 alternates.
3. Budget run_times: the sum of `run_time`s between two anchors must be < the gap, or
   everything after runs late (`pad_to` can only wait, not rewind).
4. Scene duration: end with `self.pad_to(scene_T("2.3"))` — auto-derived from the audio file.
5. If audio is ever retaken: `ffmpeg -filter:a "atempo=1.08,adelay=1000|1000"` raw → final,
   then re-run faster-whisper alignment (see `anim/words.json` generation in git history /
   memory: feed ffmpeg-decoded f32 arrays, pyav clash), then re-validate anchors. Anchors
   are phrase-based, so scenes re-sync without retiming.

## Render → QA → ship loop

```bash
cd video/anim
../.venv/bin/manimgl actN.py SceneNM -w                       # render
../../bin/ffmpeg -ss <t> -i renders/SceneNM.mp4 -frames:v 1 qa2/x.png   # extract frames
# READ the PNGs (you can view images). QA at sync-critical anchor times:
#   does the on-screen event match the spoken word at that timestamp?
#   any overlap/occlusion/clipping? colors on-role? math in math type?
# mux + rebuild the act deliverable:
../bin/ffmpeg -i anim/renders/SceneNM.mp4 -i audio/final/scene-N.M.mp3 \
  -c:v copy -c:a aac -b:a 160k /tmp/mNM.mp4                   # per scene
# concat all scenes of the act (ffmpeg concat demuxer) -> demo/actN.mp4
```

**Frame-QA is mandatory before telling Alex an act is ready.** Every bug so far
(overlaps, mangled transforms, stray objects) was caught by reading frames, not logs.

## manimgl gotchas (each cost a render cycle)

- `.animate.arrange_in_grid(...)` arranges a group's CHILDREN — flatten to leaf mobjects first
  (`VGroup(*a, *b)`).
- **Playing any animation re-adds its mobject on top.** An `ImageMobject.animate` will cover
  text/boxes that were above it — `self.add(those)` right after the play to re-raise them.
  `TransformFromCopy(src, target)` adds `target` top-level at clean-up: transform into the
  WHOLE group (box+label), never into just the box of a labeled group.
- `Arrow` has a fat quad shaft (`thickness=3.0` default) — for thin diagram arrows use
  `style.karrow` (Line + small Polygon tip).
- `label()`/`mtex()` load SVGs at true typst metrics (`_RawSVG`): same `size` ⇒ same glyph
  scale regardless of ascenders/descenders. Don't `set_height` typst mobjects to equalize
  heights across different strings — that reintroduces the distortion. **Note:** this fix
  (2026-10-03) made most text slightly smaller than the pre-fix renders, because manimgl
  used to stretch each string's ink box to the full line height. Layouts tuned before it
  still work, but have a little more air; re-check buffs if a group looks loose.
- typst markup traps in `label()`: leading `1.` / `+` / `-` would start a list (escaped by
  `_esc_typst` now); in MATH mode `q_b (x)` needs the space, or `b(x)` is parsed as a call.
- `set_opacity(0.5)` on a filled panel makes a gray slab — use `.fade(x)` to dim groups.
- `DecimalNumber` counters: re-`next_to` inside the updater or digits overflow their layout.
- `FunctionGraph` needs a 3-tuple `x_range`.
- Objects created mid-loop (links, cross-outs, ghosts) must be tracked in a list/var and
  explicitly faded — anything untracked haunts later beats.
- Local imports in scene files need `sys.path.insert(0, dirname(abspath(__file__)))`.
- `LaggedStartMap`/`AnimationGroup(group=...)` ADD THE WHOLE GROUP to the scene. For a
  staggered partial reveal (e.g. lamps now, their texts later) use
  `LaggedStart(*[FadeIn(m) for m in subset])` — never Map over the parent group.
- typst `label()` text that starts with `+`, `-`, or `N.` becomes a typst LIST
  (`_esc_typst` doesn't cover list markers) — reword the line.
- typst math `q_b(x)` parses `b(x)` as a function call and swallows it into the
  subscript; write `q_b (x)` (space before the paren).
- `Scene.time` exists; `pad_to`/`scene_T` build on it (see `TimedScene`).
- Shell cwd can reset between commands — use absolute paths in scripts.

### Morph / fade gotchas (2026-10-04 stringent pass)

- **Scribble morphs:** `ReplacementTransform`/`Transform` between *different* strings, or the
  same string in a different weight (`label` → bold `scene_title`), smears glyphs. Same text →
  `FadeTransform`; different text → staggered swap (old fully out, then new in, `lag_ratio≈0.85`).
  A simultaneous FadeOut-up/FadeIn-up of titles visibly stacks them.
- Panel/chip → dot (or dot → chip/formula) via `TransformFromCopy`/`ReplacementTransform` flies a
  filled slab. Emit a small transparent seed at the source and morph the seed, or move a dot then
  unpack. Multi-source "consumed into" → absorb (move + scale 0.2 + fade, then `remove`).
- `FadeTransform` stretches by default (`stretch=True`): pill↔box cross-fades get distorted glyphs.
- Identical glyph sequences (one-line vs two-line typst header) DO morph cleanly glyph-by-glyph —
  check submobject counts. Indexing an `mtex` gives glyphs in order (e.g. `hdr[14:16]` = "cm").
- Rectangle → RoundedRectangle morphs skew through parallelograms; same class on both ends.
- `add_shimmer` updaters re-assert fill after a FadeOut (ghosts) or FadeIn (early pop):
  `clear_shimmer` before any fade, re-add afterwards.
- `Indicate` on a `kbox`/opaque-backed chip recolours the backing/text unreadable, and with
  `scale_factor>1` overflows the chip; use a `there_and_back` scale pulse or flash only the text.
  `Indicate(m)` in the same `play()` as `m.animate.move_to` wins and drops the move.
- Two animations on the same mobject in one `play()` (two FadeIns; FadeIn + MoveToTarget of a
  parent group): the later `begin()` snapshots the other's state — the mobject ends invisible or
  pops in at full opacity. One animation per target.
- `group.add(x)` when `group` is already on screen shows `x` immediately; when `x` is ALSO a
  top-level scene mobject it gets drawn twice (doubled translucency). Reveal children
  individually; adopt into groups by removing the top-level entry first.
- manimgl `FadeIn(m, scale=s)` STARTS at 1/s (pass s>1 to grow in); `FadeOut(scale=s)` ends at s.
- `set_opacity` on low-fill shapes (block, panel) RAISES fill → brighter grey slab; dim with
  `.fade()`. To dim a heat grid and restore it, Transform back to a kept hot copy.
- Fading/shrinking an `ImageMobject` washes it into a grey slab — slide it off-frame instead.
- `ShowCreation` on a filled RoundedRectangle sweeps a fill wedge; FadeIn filled panels.
- `play(..., run_time=x)` overrides each animation's own run_time; use LaggedStart or separate plays.
- typst √ bar comes through as a zero-height path (hairline); rebuild it as a filled Rectangle.
- In NCM Math, ✗ next to prose reads as an italic X — strike the chip, or draw an x-mark polyline.
- Text centred by ink (`move_to`) sits on different baselines when strings differ in
  ascenders/descenders; sibling rows of labels need baseline anchoring (strut trick, as `rich()`).
- `manimgl ... -s` without `-w` opens a preview window and hangs; always `-s -w`.
- Subagents share the session scratchpad — use a per-act subfolder for helper scripts.

### Scene chaining pattern (recommended for every act)

Module-level "final-state builder" functions (e.g. `final62()`) rebuild a scene's last frame
exactly; the next scene opens on that build and grows its first beat out of it. Acts 0, 2, 4,
5, 6, 7, 8 now chain this way with pixel-identical seams.

## Narration/content rules (if you ever propose text changes)

- Style guide lives in SCRIPT.md header: inductive 3b1b/O'Donnell pedagogy, "intelligent
  person with nothing to prove," no act-number references in speech, no print-cadence
  fragments, `⟨pause⟩` only around math-heavy beats.
- Terminology: QrBucketTree is renamed **evidence tree**; don't pin volatile tree-step names
  (PR #223 still churning). Content truth comes from `book/src/revisit.md` only.

## Current state (2026-10-04, after the stringent pass)

- All 9 acts (26 scenes) went through a two-round stringent viewer pass (per-act agents, then a
  coordinator contact-sheet review). Every `demo/actN.mp4` is rebuilt from 1080p renders, every
  scene is audio + 0.8 s, and `lint_all.sh` reports **0 findings on all 26 scenes** (all former
  strike-through survivors now use local polyline `strike()` helpers).
- Titles are lowercase sentence case everywhere ("the Tachyon note"); title changes use a
  staggered swap; 6.1 now has PPT titles throughout. Most scene seams are pixel-identical
  (final-state builders, see above).
- Nothing older than this pass can be restored: `video/` is untracked in git.

### Content corrections made in the pass (Alex to confirm)

- **Act 4 sentinels** relabelled to the spec rule (revisit.md §epochs): sntl_i is the FIRST
  anchor of epoch i, epoch i spans sntl_i..sntl_{i+1}, sntl_{i+1} = H^epoch(anchor_{i,end} ‖ i+1).
- **7.2 per-sender state chip** now `state = (idx_ek, n)` (was `(K, i)`); K is only cached.
- **5.3** the example bucket now contains −R as a real (10th) root, routed to q₁ by the
  zero-value rule (q₀(−R) ≠ 0) — fixes a 9-parent/10-children count mismatch.
- **1.2** band labels "SHIELDED CORE"/"PAYMENT PROTOCOL" → lowercase bold (style call).

### Open items (fix, then delete the line)

- **style.py promotion backlog.** Acts carry local copies of the same helpers; promote and
  de-duplicate (requires re-rendering every act that switches): `strike`/`x_mark` (0,1,2,3,5,6),
  `swap_title`/`swap` (3,5,6,7,8), `absorb` (6), `adopt` (2), baseline helpers `bl_label` (7) /
  `two_line`, `rich_line` (0) / `tl`, `at_y`, `row` (8) / `blist`, `ptex` (5), `grow_tarrow`,
  `curved_tarrow` (3), `vignette` (4), `fix_vinculum` (4), `crack` (2), `breathe` (8),
  `prop_chip`/`xmark` (1). `scene_title`/`caption` should adopt baseline anchoring.
- Minor known compositional gaps (judged acceptable): 2.1 77–81 s title+axis only; 4.2 0–8 s
  lower stage empty; 5.2 81–96 s sparse left stage; 5.4 grind and 5.5 cost cards have no
  shimmer (static holds); 3.2 ~160 s aggregate box alone ~1.5 s.
- Sub-second transitional overlaps left in place: 1.2 ~89.5 s chip drop over heading;
  3.2 ~84 s Tachyon card over fading Orchard card; 7.2 ~61 s pulse ring over tag₀ label.
- **Linter blind spot:** it checks text against text and lines, not shape against shape, and
  can't see mid-transition stacking (title cross-fades). Contact-sheet review by a second pair
  of eyes caught ~25 issues the per-act self-QA missed — keep it in the loop.
- ElevenLabs budget used ≈ 40k/131k characters. Voice: Brian, settings in `generate_audio.py`.

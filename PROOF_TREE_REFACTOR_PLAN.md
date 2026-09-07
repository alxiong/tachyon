# Proof Tree Refactor Plan

> Resynced 2026-09-07. The QR bucket technique proposed in book-alex is now **implemented**:
> the working branch is `l/quadratic-residue` (tip `69b1352` = origin/main `a301af4` (#188)
> + 8 QR commits), documented code-side in `book/src/proof-tree.md` (same branch). The spec
> advanced past this file's old pin: `b67d6a1` (QR-predicated partition network, `#pn`),
> `c95f421` (multiset action accumulator), `1402591` (proof tree adapted to the partition
> network). Design is now **largely converged**; what remains is (a) a naming merge, (b) a
> short list of real design divergences to settle with L, (c) the anchor-side QR tree, and
> (d) Alex's non-step gaps. Broader sequencing lives in `ROADMAP.md`.
>
> Pinned refs: spec = `book/src/revisit.md` @ `book-alex` local `1402591` (**origin branch is
> gone — re-push**; pre-rebase backup still at `backup-book-alex-pre-rebase` = `6d92a3c`);
> code = `l/quadratic-residue` @ `69b1352`; code doc = `book/src/proof-tree.md` @ same.
> Old #196 is superseded by this branch.

## Where the designs converged

- **QR epoch evidence**: one partition of an epoch's tachygrams by QR profile, one
  exclusion query per note per epoch. Implemented (`stamp/proof/qr.rs`, 11 steps).
- **Filter/discriminant entropy** (old joint item 3): resolved in the spec's favor — code
  now derives from the epoch's closing anchor (`R_1 = H(boundary)`, `2a56bda`), i.e. the
  spec's ending sentinel `R_0 = H(sntl_{e+1})`. Base index differs (`R_1` vs `R_0`), cosmetic.
- **Stamp header shape**: spec `c95f421` moved `rk, cv` off the leaf headers into a multiset
  action accumulator — spec `Stamp{actacc, tgacc, anchor}` now equals code
  `StampHeader (action_commit, stamp_tg_commit, anchor)`. This independently validates the
  `lazy-multiset` / `ActionSetPoly` resting design.
- **Summaries** (old joint item 1): #188 landed on main (`a301af4`); the QR tree uses them
  as roots (`QrSummaryIntakeInit`).
- **#196 rebase** (old joint item 2): moot — `l/quadratic-residue` sits on origin/main
  post-#183/#199/#188.

## Naming map

Code names are authoritative for shipped shapes; spec names for vocabulary the book chapters
share. Verdicts: **rename** = same object, pick one name; **spec moves** = code design is the
agreed one, rewrite revisit.md; **code moves** = spec design is the agreed one; **D#** = real
divergence, see next section.

### Headers

| Code (fields) | Spec (fields) | Verdict / proposal |
|---|---|---|
| `StampHeader (action_commit, stamp_tg_commit, anchor)` | `Stamp{actacc, tgacc, anchor}` | **rename → `Stamp`**. Shapes identical. |
| `SpendableHeader (cm, (epoch, present_nf), anchor)` | `Spendable{cm, e, anchor}` | **rename → `Spendable`**; `present_nf` field is D7. |
| `NullifierDerivation (cm, epoch_start, nf_commit, epoch_end)` | `Nullifiers{cm, k, r_0, n, Com(g_n)}` | **rename → `Nullifiers`** (`r_0=epoch_start`, `n=epoch_end-epoch_start`, `Com(g_n)=nf_commit`). Spec drops `k` from this header (D10). |
| `NfMasterHeader (cm, mk)` | — (spec carries `k` on `Nullifiers`) | **spec moves** (D10). Rename → `NfMaster` (suffix policy). |
| `ArbitraryUnspent (anchor_prev, (epoch_start, nf_start), elapsed, (epoch_last, nf_last), anchor_last)` | `Unspent{s_0, m, sntl_s0, sntl_s0+m, Com(g_m)}` | **rename → `Unspent`** (`elapsed = Com(g_m)`). Field divergence (nf caches + real anchors vs counters + sentinels) is D6. |
| `Unspent (cm, anchor_prev, (epoch_start, nf_start), (epoch_last, nf_last), anchor_last)` | `VerifiedUnspent{cm, s_0, m, sntl_s0, sntl_s0+m}` | **rename → `VerifiedUnspent`**. ⚠ swap hazard: today's code `Unspent` is the spec's `VerifiedUnspent`, not the spec's `Unspent`. |
| `SpendHeader (cm, present_nf, nf_next, anchor)` | — (spec `SpendBind` emits `Stamp` directly) | **spec moves** (D9). Rename → `Spend`. |
| `OutputHeader (cm, pad)` | — (spec `OutputSeed` emits `Stamp` directly) | **spec moves** (D9). Rename → `Output`. |
| `Summary (epoch, anchor_prev, anchor_last, acc_commit)` | root bucket `Root{anchor_L, anchor_R, n, Com(p)}` | **spec moves** (D5): adopt `Summary`; no count `n`, no `B` target under the adaptive tree (D3). |
| `QrIntake (epoch, anchor_prev, anchor_last, boundary, profile{depth,bits}, discriminant, contents)` | in-progress bucket / `Tachygrams{σ, anchor_L, anchor_R, j, b, R_j, Com(q^tg_b)}` | **spec moves** (D2/D3). Mapping: `σ=boundary`, `j=profile.depth`, `b=profile.bits`, `R_j=discriminant`. Code also carries `epoch` explicitly. |
| `QrIntakeSides (…, residue, non_residue)` | `TachygramsPartition_s`, `s ∈ {permuted, left, checked}` | **spec moves** (D2): one intermediate state instead of three. |
| `QrBucket (epoch, anchor_prev, anchor_last, boundary, profile, discriminant, contents)` | final `Tachygrams` with `(anchor_L, anchor_R) = (sntl_i, sntl_{i+1})` | **spec moves**, but right-endpoint convention differs: code spans `[opening anchor, terminal anchor]`, one link short of `boundary` (`af33672`); spec spans sentinel-to-sentinel. Feeds D6. |
| `QrFilter (epoch, boundary, profile, discriminant, residue_filter, non_residue_filter)` | — (spec query recomputes profile bits) | **spec adopts** (D4): code invention, no counterpart. |
| `QrProfileClaim (epoch, boundary, profile, discriminant, value, non_residue_filter, sequence)` | — | **spec adopts** (D4); value-generic per `af33672`. |
| `AnchorChain (start, end)` | `AnchorRoot{anchor_L, anchor_R, n, Com(p^anchor)}` + `AnchorChain{σ, anchor_L, anchor_R, j, b, R_j, Com(q^anchor_b)}` | **code moves** (D1). ⚠ name collision: same name, different objects — code's is a flat interval, spec's is a QR query bucket. The flat header likely retires when the anchor tree lands. |

### Steps (32 registered @ `stamp/proof/mod.rs`)

| Code | Spec | Verdict |
|---|---|---|
| `NfMasterSeed` | base relation of `NullifierDerive` | keep split (D10); aligned. |
| `NfDerive` | `NullifierDerive` continuation | **spec moves** (D10): 16-wide window per step, not 1. Name: keep `NfDerive`. |
| `NullifierFuse` | — (spec extends only by continuation) | **spec adds**: window concatenation exists and is load-bearing. |
| `SpendableInit` | `SpendableInit` | aligned (conditional creation-stamp membership). Code's extra `NullifierDerivation` input pins `present_nf` — consequence of D7. |
| `SummarySpendableInit`, `QrSpendableInit` | `SpendableReinit` | **D8** — same role (past-epoch bootstrap), different inputs and anchor-authentication model. |
| `SpendableLift` | `SpendableLift` | aligned name; continuity mechanics differ (D7). |
| `UnspentBind` | `UnspentBind` | aligned. Spec's explicit `m>0` + `[s_0,s_0+m) ⊆ [r_0,r_0+n)` counter checks are dropped in code — divisibility of indexed factors subsumes them (documented in proof-tree.md §binding). Spec should drop the counters with D6. |
| `UnspentSeed` (one stamp, one exclusion) | `UnspentSeed` (empty segment at `sntl_s0`) | ⚠ same name, **different semantics** (D6). |
| `EndEpochUnspentSeed` | — (sentinel advance is internal to `UnspentLift`) | D6. |
| `UnspentFuse` | `UnspentMerge` | D6: code composes inclusive spans sharing a junction epoch (divides the junction factor out); spec multiplies disjoint half-open counter ranges. If code model wins, name stays `UnspentFuse`. |
| `SummaryUnspentInit`, `QrUnspentInit` | `UnspentLift` (one query clears a whole epoch) | `QrUnspentInit` is the epoch-granular analog; D6 for composition model. |
| `SummarySeed`, `SummaryAdvance` | `RootSeed`, `RootAppend` (+ `RootPad`) | **spec moves** (D5); `RootPad` dies with the fixed-shape tree (D3). |
| `QrSummaryIntakeInit`, `QrStampIntakeSeed` | root-bucket preparation (step 1 of `#pn`) | **spec moves** (D5). |
| `QrIntakeSplit`, `QrSideDescend` | `TachygramsPartition`, `Tachygrams{Left,Right}Check`, `Tachygrams{Left,Right}Extract` | **spec moves** (D2): 2-step split + sibling-attest replaces the 5-step state machine. |
| `QrIntakeMerge` | implicit in pairwise partition of same-profile buckets | **spec moves** (D3): merge is a separate step in the adaptive tree. |
| `QrBucketSeal` | "final range check" (inside the query) | **spec moves**: sealing is its own step pinning both epoch ends (`2a56bda`, `af33672`). |
| `QrFilterSeed`, `QrFilterDescend`, `QrProfileAttest` | — | **spec adopts** (D4). |
| `SpendBind` | `SpendBind` (monolithic: note reopen + cv/rk/value-range + nf pair) | ⚠ same name, **narrower coverage** in code (nf pair only); D9. |
| `SpendStamp`, `OutputBind`, `OutputStamp` | `OutputSeed` / tail of spec `SpendBind` | D9. |
| `MergeStamp` | `StampMerge` | **rename → `StampMerge`** (noun+verb, both docs' stated convention). |
| `StampLift` | `StampLift` | aligned name; semantics gap is D1 (endpoint copy vs same-epoch ancestry proof). |
| `AnchorSeed`, `AnchorFuse` | `AnchorRootSeed/Append/Pad`, `AnchorPartition`, `Anchor{Left,Right}Check`, `Anchor{Left,Right}Extract` | **code moves** (D1). |

### Terminology (book merge)

| Spec (revisit.md) | Code (proof-tree.md / rustdoc) | Proposal |
|---|---|---|
| sentinel `sntl_e` | epoch-opening / boundary anchor (`H_ep(prev_last, epoch)` domain) | keep **sentinel** as the reader-facing word; define it as the epoch-domain anchor. |
| filter `R_j` | discriminant `R_j` | **discriminant** — "filter" now names the `QrFilter` path polynomials; the spec's use must be renamed to avoid the clash. |
| OSS | sync service | pick one; **OSS** is shorter and already scoped in spec tables. |
| partition network, layer `j` | intake tree, routing, descend, depth | follows D2/D3 outcome; adaptive tree suggests code vocabulary. |
| `(j, b)` public fields | `QrProfile{depth, bits}` register | code shape; spec can present it as `(j, b)`. |
| "lift" = OSS epoch advance (`UnspentLift`) | "lift" = advancing a stamp/spendable over a segment; segments are made by `Seed/Init` | reserve **lift** for consumer-side advance (code usage); OSS-side is seed/init/fuse. |
| suffix policy | code has `*Header` suffixes on 5 headers | drop suffixes everywhere (spec convention): `Stamp`, `Spendable`, `Spend`, `Output`, `NfMaster`. |

Rename mechanics: header suffix IDs and step registration indices are fixed independent of
Rust names, so the renames are code-cosmetic; serde field names and both book chapters ride
along in the same PR.

## Design divergences to settle (D1–D10)

- **D1 — Anchor-side QR evidence (code moves; the big remaining build).** Spec builds the
  same partition network over anchors (`AnchorRoot`/`AnchorChain`), filters online from the
  *starting* sentinel, so `StampLift` proves same-epoch ancestry (profile query on the old
  anchor + `Epoch()` equalities + no sentinel in range) and `SpendableReinit` authenticates
  the creation anchor. Code still has flat `AnchorSeed`/`AnchorFuse` segments and a
  `StampLift` that copies endpoints; anchors tie to history only via consensus membership of
  the eventual published stamp. Owner/sequencing TBD with L; the intake/split/descend/seal +
  filter machinery should be reusable with an anchor-domain root step.
- **D2 — Partition step decomposition (spec moves).** Spec: pair two same-profile buckets,
  then a 5-step state machine (`Partition_permuted → LeftCheck → RightCheck →
  Left/RightExtract`), proving *both* sides pure before either extraction ("child complete,
  not merely pure"). Code: `QrIntakeSplit` (product/permutation check → `QrIntakeSides`) +
  one `QrSideDescend` per emitted side, attesting the **sibling** (`4e81369`): completeness
  of the emitted child is direct, and a stray wrong-class member is tolerated because it only
  tightens consumer openings (membership needs no profile at all — any bucket divides the
  epoch's stamp polynomials). Weaker guarantee, argued sufficient in proof-tree.md
  §qr-epoch-evidence; L should sign off on the stray-tolerance argument before the spec
  section is rewritten.
- **D3 — Tree geometry (spec moves).** Spec: roots bounded by `B = 8,000` (max 8,096), pad
  with empty roots to `n = 2^k`, fixed `k` layers, every leaf full-epoch at depth `k`. Code:
  adaptive — split when contents exceed polynomial capacity (`MAX_BUCKET_SIZE` dropped,
  `323bfdd`), `QrIntakeMerge` rejoins same-profile spans, leaves sit at whatever depth
  routing stopped, depth `< 64` (profile side-register width, also the two-paths-one-profile
  bound). The spec's open tail-bound "parameter-selection question" dissolves; the padding
  steps die.
- **D4 — Query mechanics (spec adopts; main code-side invention to upstream).** Spec: a
  single query step re-derives `R_0..R_j` and every profile bit in-circuit, with a fixed
  maximum layer. Code: a per-profile `QrFilter` lineage records the path as two polynomials
  sorted by side (`QrFilterSeed`/`QrFilterDescend`); `QrProfileAttest` settles the whole
  residue side in one identity `g(y)^2 − (value + y) = P_res(y)·h_res(y)` at one challenge
  (value-generic claim, `af33672`); `QrUnspentInit` adds the non-residue half, the
  exceptional `−value` opening, and the bucket opening, checking claim/bucket agreement on
  `(epoch, boundary, profile, discriminant)`. Query cost is depth-independent and the filter
  is built once per profile per epoch, shared across all queries.
- **D5 — Roots (spec moves).** Spec's `RootSeed`/`RootAppend`(+`Pad`) with a count `n`
  become `Summary`/`SummarySeed`/`SummaryAdvance` (#188) plus the direct
  `QrStampIntakeSeed` shortcut for stamps that fill a polynomial alone. Summaries also serve
  non-QR consumers (`SummaryUnspentInit`, `SummarySpendableInit`), which the spec lacks.
- **D6 — Absence-segment algebra (discuss; recommendation: spec moves).** Spec: counter
  header `Unspent{s_0, m, …}`; `UnspentLift` consumes one full-epoch `Tachygrams` bucket per
  step (query + indexed factor + sentinel-to-sentinel advance, crossings internal); segments
  abut exactly at sentinels; `UnspentMerge` multiplies disjoint adjacent ranges; evidence is
  full-epoch **only**. Code: segment algebra — `QrUnspentInit` emits a single-epoch segment
  spanning `[opening anchor, terminal anchor]` (one link short of the sentinel);
  `EndEpochUnspentSeed` is the explicit crossing between consecutive epochs' segments;
  `UnspentFuse` composes inclusive spans sharing a junction epoch; boundary `(epoch, nf)`
  caches ride the header instead of counters; and sub-epoch granularities the spec dropped
  (per-stamp `UnspentSeed`, `SummaryUnspentInit`) remain for recent/partial history. The code
  model is implemented, more general (mid-epoch positions, active-epoch tails before QR
  evidence exists), and is what `SpendableLift` adjacency is written against. Spec should
  adopt it, keeping the full-epoch QR path as the recommended OSS mode; alternatively L may
  argue for quantizing to sentinels and deleting the per-stamp path — decide together.
- **D7 — Spendable continuity (spec moves).** Spec `Spendable{cm, e, anchor}` lifts by
  counter equalities (`e_old = s_0`, `anchor_old = sntl_s0`). Code carries
  `(epoch, present_nf)` and checks per-lift nullifier continuity + anchor adjacency, which
  supports mid-epoch positions (D6), gives `SpendBind` a pre-challenge-fixed factor for the
  published pair, and lets the lineage state its position without a derivation in hand.
  Consequence: code `SpendableInit` consumes a `NullifierDerivation` to pin `present_nf`,
  which spec's `SpendableInit` doesn't need.
- **D8 — Past-epoch bootstrap (settle with L).** Spec `SpendableReinit`: one step bridging
  `AnchorChain × Tachygrams` over `e_incl`, reopening the note, deriving `nf_{e_incl}`
  in-step, and authenticating the creation stamp's anchor via an anchor-bucket query. Code:
  `QrSpendableInit` consumes the note's `Unspent` over the creation epoch (QR segment +
  `UnspentBind` — nf absence and `cm` arrive on the header, no note reopen) and the
  `QrBucket`, opens the bucket at `cm` for zero, requires span equality, and emits at the
  epoch's terminal anchor; creation-anchor authentication is deferred to consensus membership
  of the eventual spend (free `pre_cm_anchor` model). Two questions for L: (i) once D1
  lands, does reinit-time anchor authentication become required, or does the downstream
  closure argument stand? (ii) is avoiding the note reopen (nf genuineness via derivation
  divisibility instead) acceptable spec-side? `SummarySpendableInit` is the summary-granular
  variant of the same role.
- **D9 — Leaf step granularity (spec moves).** Spec fuses each leaf into one step
  (`OutputSeed`; monolithic `SpendBind` emitting `Stamp`). Code splits bind/stamp
  (`SpendBind`+`SpendStamp`, `OutputBind`+`OutputStamp`) so the note is witnessed only in
  the terminal step, bind headers stay point-free, and rerandomization sits at the trust
  boundary; also keeps each circuit inside the gate bound. proof-tree.md documents the
  phantom-note and rerandomization rationale; spec should adopt the split or explicitly
  present its leaves as fused-for-exposition.
- **D10 — Derivation granularity (spec moves; landed #199/#183).** Spec: one nullifier per
  continuation, `k` carried on every `Nullifiers` header. Code: `NfMasterSeed` confines
  `nk`/`mk` (`mk` rides only `NfMaster`, consumed by `NfDerive`), `NfDerive` squeezes a
  16-wide window natively with derived (not witnessed) range, `NullifierFuse` concatenates.
  Spec's `Nullifiers` header drops `k`.

## Non-step gaps (owned by Alex, see `ROADMAP.md`)

- **Verify cost model (old D7 roadmap item)**: branch `acc-correct` @ `a3a1d6f`, now based
  on the lazy-multiset commit (as `b173509` + clippy `316dc4f`). The former `wip-acc-tg`
  stash **landed** as `e3bf543` (leaf stamp set-commitment enforcement via
  `enforce_poly_roots`, no in-circuit MSMs) + `bc721e9` (shared-challenge polynomial
  openings) + `a3a1d6f` (self-contained rustdoc). **Remaining host half** unchanged:
  `ProofStamp::is_accumulating()` still recomputes by interpolation+MSM; the FS eval-claim
  alternative needs mock ragu to verify recorded poly-query claims at `verify` time (today
  `Application::fuse` discards them). Coordinate with L before extending the mock. Both
  branches predate the QR work — rebase over `l/quadratic-residue` once it merges.
- **Lazy set-form stamp sets**: PR branch = `lazy-multiset` @ `c0a20cb` (amended 2026-09-04
  with the guarded-pow streaming-eval fix from LucidSamuel's #201 review). `acc-correct`
  still sits on the pre-amend `b173509` — rebase with
  `git rebase --onto c0a20cb b173509 acc-correct` before PRing. Design history (three rejected action-side reworks, archived at
  `action-list-header` = `18202f7`; the "resting design" = `ActionSetPoly` stays) is
  recorded in this file's git history @ `69b1352^` — not repeated here since spec `c95f421`
  adopted the multiset actacc, closing the question in the resting design's favor. Still
  open for L: can real ragu absorb variable-length header vectors natively? If yes, the
  archived raw-list design becomes viable again. Keep-alive insights from the dropped work:
  wire order = descriptor-sorted order invariant (`apply_signatures`/`Plan::commitment`);
  `Tachyon-Actions` personalization reuse (`hActionsTachyon` vs `hStampActionsTachyon`) —
  a dedicated `Tachyon-StampActs` personalization is a one-line hardening to raise with L.
- **Consensus/node layer** (spec `#consensus-rule`, `#anchor`): sentinel tick,
  `Epoch(anchor)` map, canonical-anchor membership, `e ∈ {cur, cur−1}` acceptance, 2-epoch
  duplicate-tachygram window. Only exists as the test-only `PoolSim`.
- **Wire/serde** for QR buckets / filters / epoch evidence — shapes look settled on
  `l/quadratic-residue`; blocked on the naming merge to avoid double-renaming serde fields.

## Joint items with L

1. **Naming merge execution** — agree the tables above, then one mechanical rename PR on the
   code (`Stamp`, `Spendable`, `Spend`, `Output`, `NfMaster`, `Nullifiers`, `Unspent`/
   `VerifiedUnspent` swap, `StampMerge`) and one spec rewrite of `#pn`/`#prooftree` to the
   intake/split/descend/seal + filter-poly decomposition (D2–D5) with the terminology table
   applied (discriminant vs filter, sentinel definition, lift verb).
2. **D1 anchor-side QR tree** — ownership and step shapes (reuse intake machinery with an
   anchor-domain root?); unblocks real `StampLift` same-epoch ancestry and the D8 question.
3. **D6 segment algebra vs sentinel counters** and **D8 reinit anchor-authentication** —
   the two places the designs still genuinely disagree; everything else is one side adopting
   the other's landed improvement.
4. **Ragu question** (carried over): native variable-length header vectors; also mock-ragu
   poly-query claim verification for the acc-correct host half.

## Spec residue (book-alex, quick fixes)

- Stale plan-era vocabulary in `#witness` (now ~L2360–2364): `SpendableHeader`,
  `NullifierHeader`, `UnspentHeader`, "Prefix or Infix".
- `#past-epoch-spend` ~L1940: "emitting `SpendStamp`" — that header no longer exists after
  `c95f421`; leaves emit `Stamp`.
- ~~`AnchorChain` leaf overflow bound unspecified~~ — resolved by `b67d6a1` (root-bucket
  target B applies to both trees); dissolves anyway under D3.
- ~~Reconcile the two evidence-construction timings~~ — resolved by `b67d6a1`/`1402591`
  (anchor filters online from starting sentinel, tachygram partitioning post-epoch).
- `origin/book-alex` is gone — re-push the branch so the pins above resolve for L.

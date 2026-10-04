# Scaling Zcash with Tachyon — v2 Staged Script (Draft 3)

> Status: **flow APPROVED (draft 3, 2026-10-04).** Narration draft in `NARRATION.md`, awaiting review. No audio, no animation until the narration is approved.
> Stage 1 (this file): scene flow + narration beats + visual plan.
> Stage 2 (after approval): verbatim narration per scene, reviewed again.
> Stage 3: ElevenLabs audio → manimgl animation → assembly.

## Overview

- **Topic**: the Tachyon shielded protocol, top to bottom, per `book/src/revisit.md`.
- **Hook**: *Prove that a coin was never spent, when nobody keeps the list of spent coins.*
- **Target audience**: Zcash protocol engineers fluent in Sapling/Orchard internals
  (key tree, `rk` re-randomization, binding signature, Pedersen `cv`, Merkle anchors).
  Strong algebra (finite fields, polynomial identities, Schwartz–Zippel) assumed.
  No "what is Zcash." Orchard is the diff baseline throughout.
- **Estimated length**: ~44 min of narration at the current beat budget (one video, eight chapters). Slightly over 40 is acceptable.
- **Key insight**: one primitive, *a commitment to the polynomial whose roots are
  your set*, carries almost the whole design. Zero/nonzero evaluations give membership
  and non-membership. Polynomial multiplication and division give set union and
  subset. Random-point identities let a folding proof system check all of it cheaply
  and natively. Every later construction is this primitive plus one more idea.
- **Ragu**: a black box with two stated capabilities (fuse proofs; it is designed
  to expose evaluation queries on committed polynomials natively, outside the step
  circuit). Stated once in the prologue. Never explained.

## Narrative arc

The video follows **one note**, note₅, from its birth in epoch 5 to its spend four
epochs later. A second, fresh note, note₉, is received in the spend epoch and spent
in the same transaction. note₉ gives the proof tree its base case. The notes are
labeled by birth epoch (on screen as subscripts), so the labels imply no teaching
order.
Every mechanism enters exactly when that note needs it. First the note needs an
owner (the key split). Then it needs a place in the pool (the polynomial
accumulator, the stamp, the anchor chain). Then time passes, and the note needs to
prove it was never spent without revealing anything to its helpers (evolving
nullifiers, the ranged commitment). The proof has to stay cheap at real
throughput (QR filters, the evidence tree). The proof itself has a shape (the proof
tree). Finally the spend lands, and consensus and aggregation take over. The
payment protocol and the quantum posture close the loop opened in chapter 1.

Each chapter ends on the question the next one answers. That is the cascade the
outro replays.

### The running example (fixed for the whole video)

| Fact | Value |
|---|---|
| note₅ (protagonist) created (output) in | epoch **5** |
| note₉ (fresh) created (output) in | epoch **9**, so it is a same-epoch spend |
| One transaction in epoch 9 spends note₅ and note₉, and creates outputs | 2-in-2-out, target anchor in epoch **9** |
| Each spend publishes | its own `nf_9`, `nf_10` |
| Inclusion-epoch exclusion (wallet-only, singleton path) | epoch 5 |
| Delegated to an OSS | `S = [6, 9)`: pairs `(6, nf_6), (7, nf_7), (8, nf_8)` |
| Wallet's local derivation, `Rate = 4`, `G = 1` | windows `[4, 8)` and `[8, 12)`, fused to `R = [4, 12)` |
| Toy field for every on-screen arithmetic example | `F_13` (13 ≡ 1 mod 3 and mod 4; squares {1,3,4,9,10,12}; cubes {1,5,8,12}; `c = 2` is a non-square **and** a non-cube) |

The toy field lets us show real numbers on screen (concrete beats abstract). The
narration always says when we return to the real Pasta field.

### What changed from the v1 script (for review)

- **Structure.** v1 taught the mechanisms in spec order, as topics. v2 orders them by
  the note's life. The content decisions locked in v1 still hold (binding signature
  demoted, no GGM, aggregation in one breath, PIR as a black box, a one-line
  `#nf-sec`).
- **Synced to the current spec.** These were added or fixed: the singleton
  inclusion-epoch path (`NoteUnspentInit` → `SpendableReinit`); the
  stamp-summary → QR-intake → split / descend / merge / seal pipeline;
  a membership query needs no profile;
  output `rk = [α]G` and the hot-device signing benefit; the scope of the stamp's
  claim ("the target anchor is not an exclusion endpoint").
- **Naming.** "Evidence tree" replaces QrBucketTree. Tree-internal step names are
  not spoken. Leaf openings are called "evidence-tree openings."
- **Visual spine.** Three persistent objects replace per-scene diagrams:
  (1) **the note card**, our protagonist, docked in a corner;
  (2) **the epoch rail** along the bottom, with sentinel gates, which fills in as time passes;
  (3) **the field line**, a number line of field elements where roots sit and probes strike.
  The QR detour and the soundness sidebars use a fourth, **the `F_13` clock**.

---

## Chapter 0 — Prologue: the set nobody can prune (~3 min)

### Scene 0.1 — Two sets, two fates
**Duration**: ~80 s
**Purpose**: Name the scaling wall. Make the audience feel why nullifiers, not commitments, are the problem.

#### Visual Elements
- Split stage. Left: a commitment Merkle tree accreting leaves. Right: a nullifier set as a hot grid inside a "RAM" frame.
- Incoming transactions fire membership probes into the grid.
- A counter rolls to "500 GB / day".

#### Content
Every pool since Zerocash keeps two growing sets. They grow at the same rate, but their costs differ. The commitment tree is append-only. Consensus needs only its root, so the tree can sink to disk. The nullifier set must answer "never seen before?" for every input, against all of history, in memory, on the critical path. At Visa throughput that is about 500 GB of new state per day.

#### Narration Notes
- Open on the picture, not the claim. The first line is a question: "Which of these two sets is the problem?"
- End: "That's the wall. Not proof size. Not bandwidth. One set nobody can prune."

#### Technical Notes
- Merkle tree: `VGroup` of `Line`s + `Dot`s grown with `LaggedStart(ShowCreation)`; leaves fade and drift down to a "disk" slab, root stays lit.
- Grid: `VGroup(*squares).arrange_in_grid`; probes as `Line` flashes; overflow via `self.frame` pull-back.

### Scene 0.2 — The thesis, the black box, and our protagonist
**Duration**: ~100 s
**Purpose**: State client-side validation, state the Ragu interface once, and introduce the note we will follow.

#### Visual Elements
- The hot grid is scissored. A thin "recent window" stays with the validator. The rest flies to wallets, each holding a proof token.
- A "Ragu" black box with two labeled ports: **fuse** (two proof tokens in, one out) and **query** (an envelope `Com(f)` + a point `r` in, `f(r)` out).
- A fresh note card appears and docks top-left. The epoch rail draws itself along the bottom, ticks 4…10, with a "now" cursor at 5.

#### Content
- Tachyon's principle is client-side validation. Move validation off consensus and onto the client wherever possible. Consensus keeps only recent nullifiers. The spender proves that the nullifier is absent from older history.
- That proof must stay current as blocks land, so it is built incrementally, as proof-carrying data.
- The black box: Tachyon runs on Ragu, a Halo-lineage PCD on the Pasta cycle with no trusted setup. It has two capabilities. (1) **Fuse**: take up to two child proofs plus a witness, and emit one proof. (2) **Query**: Ragu is designed to expose evaluation queries on committed polynomials to the application. Those claims are folded into the proof system's own running claim instead of being arithmetized in the step circuit. *The second capability carries most of this design.*
- No further Ragu properties are discussed.
- "We'll follow one note: born in epoch 5, spent in epoch 9. Every piece of Tachyon shows up exactly when this note needs it." (note₉ is introduced later, in Ch. 5, where it is needed.)

#### Narration Notes
- The Ragu statement is deliberately short and flat: an interface contract, not a tutorial.
- The note intro is the emotional hinge of the opening. Slow down.

#### Technical Notes
- Black box: `RoundedRectangle` + two port `Arrow`s; reused later as a tiny glyph whenever an oracle query fires.
- Note card: a 4-slot `VGroup` (pk | v | ψ | rcm). Its slots fill in during Ch. 1. Keep the card as one persistent mobject across the scenes of a chapter (rebuilt at the start of each scene file in the same position).

---

## Chapter 1 — Ownership, stripped down (~5 min)

### Scene 1.1 — Why Zcash keys got complicated
**Duration**: ~110 s
**Purpose**: The diff baseline. Show that Orchard's key tree serves three jobs, only one of which is ownership.

#### Visual Elements
- The canonical `zcash_keys.png` diagram, kept in its own colors (audience memory). Sprout's two keys appear beside it for contrast.
- Three highlight passes, each circling a subgraph with hand-drawn contours (never dim the raster).

#### Content
- Sprout needed a payment key and an encryption key. Orchard's diagram is not that. Why?
- Reason 1: proving and authorizing separated. Hardware wallets can't prove, so authorization became a signature, and unlinkable signatures re-randomize: `ak` in the witness, `rk = ak + [α]G` in the instance.
- Reason 2: the address does two jobs. It declares the owner and carries the transmission key. Diversified addresses exist to refresh the transmission key while `ivk` stays fixed.
- Reason 3: selective disclosure. That adds `ovk` and the viewing-key family.
- The observation: of all this material, exactly two keys enforce ownership. `nk` derives nullifiers. `ak` authorizes spends.

#### Narration Notes
Inductive: the question first, then the three reasons, then the observation. No drama.

#### Technical Notes
- `ImageMobject` for the PNG plus pixel-mapped contour overlays. Re-add overlays after any image animation (draw-order gotcha).

### Scene 1.2 — The cut
**Duration**: ~110 s
**Purpose**: Tachyon's first decision. The shielded protocol keeps only ownership. The payment protocol owns everything else.

#### Visual Elements
- A vertical blade cuts the key tangle. Left box: shielded protocol, `(ak, nk) → pk = Com(ak, nk)`. Right box: payment protocol, holding addresses, memo encryption, discovery, and viewing.
- A security-property ledger splits half left, half right.
- An encrypted envelope passes *through* the shielded box untouched (the DA layer).

#### Content
- The payment key `pk = Com(ak, nk)` is a binding, hash-based commitment. It gives a succinct owner field and quantum recoverability. Publishing `ak`, a Schnorr key, to senders is a harvest-now-decrypt-later risk. `Com(ak, nk)` is not.
- The shielded protocol never constrains how `ak` and `nk` are derived. It requires only that they are indistinguishable from random. Derivation paths belong to wallet standards (ZIP-32 style).
- Security properties split. The shielded core keeps ledger indistinguishability, balance, note privacy (in-band and OOB), and spend unlinkability against an attacker who holds only the payment key. Full unlinkability under `ivk` access, and Faerie-gold resistance, move to the payment protocol. Faerie gold comes back in Ch. 7.
- The chain becomes a DA layer for payment-protocol bytes. The shielded protocol carries them and never parses them.
- Unchanged from Orchard, and named once: RedPallas spend authorization, `rk = [ask + α]G`; the binding signature over homomorphic `cv`s.
- The payoff: smaller upgrade scope, isolated assumptions, and the two halves can evolve in parallel.

#### Technical Notes
- The cut: `Line` with a glow sweep; children `ReplacementTransform` into the two boxes.

### Scene 1.3 — The note
**Duration**: ~70 s
**Purpose**: Fill in the protagonist's card. Plant ψ.

#### Visual Elements
- The note card's four slots fill: `pk`, `v`, `ψ`, `rcm`. A Pedersen expression morphs into a Poseidon sponge icon. ψ stays highlighted.

#### Content
- `Note = (pk, v, ψ, rcm)`; `cm = Com(pk, v, ψ; rcm)` with Poseidon. The commitment is purely symmetric.
- Contrast: Sapling and Orchard use Pedersen variants, which rest on discrete log. Orchard needs extra wallet rules on `rcm` derivation for quantum recoverability. Tachyon doesn't.
- ψ is the note's pseudorandom identity. "Keep an eye on ψ. Every nullifier this note will ever have hangs off it."
- Close on the next question: the note exists. Where does `cm` go?

---

## Chapter 2 — Birth: one accumulator, one stamp, one chain (~6 min)

### Scene 2.1 — A set as the roots of a polynomial
**Duration**: ~130 s
**Purpose**: Introduce the primitive that carries the whole video, concretely and with the full set↔polynomial dictionary.

#### Visual Elements
- **The field line** appears (`F_13` labels for now). Roots drop on it as dots. Beneath, the factored product `(X − 2)(X − 7)(X − 11)` builds factor by factor. A degree counter ticks.
- A probe (vertical line) hits 7 → the evaluation snaps to 0 (gold, "member"). A probe hits 5 → nonzero (flare, "not a member"). Same probe, both answers.
- The dictionary is shown live: insert = multiply, remove = divide, union = product, subset = exact division.
- The Merkle tree and the nullifier grid from 0.1 dissolve into this one object.

#### Content
- Commit to `f(X) = ∏(X − x_i)`. Membership is `f(x) = 0`. Non-membership is `f(x) ≠ 0`. Ragu's query port answers both, natively.
- If one structure answers both questions at the same cost, why keep commitments and nullifiers apart? Tachyon doesn't. Every member is a **tachygram**: a 32-byte blob, a note commitment in an output or a nullifier in a spend. They are indistinguishable on chain. (Bonus: one anonymity set instead of two.)
- It is a *multiset*: tests ignore multiplicity, and union needs no disjointness precondition. Consensus nevertheless rejects duplicates, so every canonical per-epoch accumulator is square-free. Plant this; the QR test needs it in Ch. 4.
- The subtlety this audience will raise: binding ≠ correctness. A commitment opens to one polynomial, but nothing says that polynomial has the published roots. A ghost root sneaks in, and the probe lies. The fix: the verifier computes `y_r = ∏(r − tg_i)` itself (field operations only, no group work) and checks the claim `(tgacc, r, y_r)`. Soundness: `D / |F|`.

#### Narration Notes
This is the conceptual spine. Name it explicitly: "Almost everything else in this video is this one idea plus one more."

#### Technical Notes
- `NumberLine` (manimgl) with integer ticks 0–12; roots as `Dot`s with `GlowDot` halos.
- Product: build the equation from separate typeset parts so factors can slide in and out with `TransformMatchingTex`/manual `ReplacementTransform`.

### Scene 2.2 — The action and the stamp
**Duration**: ~120 s
**Purpose**: How our note's `cm` enters the pool. The action description, the output statement, and the stamp.

#### Visual Elements
- An Orchard action card `(cv, rt, nf, rk, cmx, epk, …)` morphs into Tachyon's `(rk, cv)`. `cm` detaches and drops into a "tachygram pouch" on the stamp. A second, empty slot sits beside it in the pouch, unexplained for now: "we'll come back to this."
- The stamp card: public inputs `(actacc, tgacc, anchor)` plus the published tachygram list.
- The txid / wtxid split, drawn as stable fields vs malleable fields (redrawn from `tachyon_tx.svg`, in brand colors).

#### Content
- The action description is `(rk, cv)`. No `nf`, no `cm`. Evolving nullifiers (coming soon) are not static enough to live there. The note binds to the action through `rk`'s randomizer: `α = PRF(cm ‖ θ)`. For an output, `rk = [α]G`. For a spend, `rk = ak + [α]G`.
- An output's signing key is `α` itself. A hot device signs outputs with no custody round-trip, because creating a note needs no authority (the binding signature already enforces funding). Both forms of `rk` are uniform points.
- The output statement on one card: `cv = [−v]G + [rcv]H`; `0 ≤ v ≤ MAX_MONEY`; `cm` integrity; `rk = [α]G`; nonzero tachygrams. No anchor, no epoch: history can't affect an output.
- The action multiset: `a_i = Poseidon(rk_i, cv_i)`, `actacc = Com(∏(X − a_i))`. Same primitive, second use.
- A **stamp** is the bundle's PCD proof, with public inputs `(actacc, tgacc, anchor)`. It also publishes the tachygram multiset.
- Thirty seconds of txid hygiene. `txid` commits to `actacc ‖ v_bal ‖ da_digest`. Memo bytes are effecting data through `da_digest`. Stamps live in `auth_digest`, so a relayer can rewrite them (aggregation will) without touching `txid`. Every signature covers `da_digest` through `SIGHASH`.

#### Technical Notes
- The pouch with an empty second slot is a deliberate visual debt. It is repaid in 3.2.

### Scene 2.3 — The anchor chain
**Duration**: ~100 s
**Purpose**: Where the stamp lands, and the epoch structure everything later depends on.

#### Visual Elements
- **The epoch rail** comes alive. Each stamp is a bead absorbing a `tgacc` chip: `anchor ← H(anchor_old ‖ i ‖ tgacc)`. Sentinel gates stand at the epoch transitions. Our note's stamp lands as a bead inside epoch 5 and is marked.
- A split-screen cost card: validator-as-hasher (one hash per stamp) vs validator-as-accumulator (an MSM gear grinding over the whole block).

#### Content
- The anchor chain is a hash chain carried in the block header. It ticks once per stamp, which is sub-block and above transaction granularity. Binding `i` at every tick lets a proof authenticate which epoch a segment belongs to.
- At every epoch transition consensus appends one domain-separated sentinel, `sntl_i = H^epoch(anchor_{i−1,end} ‖ i)`. Every epoch, even an empty one, has two authenticated boundary posts, and every canonical anchor maps to exactly one epoch.
- Why per stamp, not per block? Validator work. A stamp's `tgacc` is already checked by the cheap `y_r` trick, so the validator just hashes it in. A per-block anchor would force every validator to re-accumulate, interpolate, and commit (an MSM) on the critical path.
- Close: "Our note is in. Now the clock moves."

---

## Chapter 3 — Time passes: nullifiers that evolve (~6.5 min)

### Scene 3.1 — Why one nullifier per note has to go
**Duration**: ~100 s
**Purpose**: The privacy failure that forces evolving nullifiers.

#### Visual Elements
- The "now" cursor slides from epoch 5 toward 9. The wallet's proof token has to tick forward at every bead, which is tedious, so the wallet hands its work to an OSS robot (cyan).
- First version: the wallet gives the OSS `nf`. Later the same `nf` appears on chain, and a dotted flare line snaps from the OSS's memory to the spend. Rewind. Now each epoch has its own value, and the line fails to connect.
- A banner, "1 note = 1 nullifier", cracks.

#### Content
- To refresh an exclusion proof for `nf`, a service must know `nf`, and whoever knows your nullifier recognizes your spend.
- The fix: one nullifier per epoch. What you share in epoch 6 is unlinkable to what you reveal at spend time.
- Name the cost this audience will flag. This breaks a Zerocash-era invariant: one note, one globally unique nullifier. Tachyon now owes us a new derivation and a new double-spend rule. The rule arrives in Ch. 6.

### Scene 3.2 — The derivation, and two nullifiers per spend
**Duration**: ~130 s
**Purpose**: The concrete KDF, the delegation shape, and the cross-epoch race that explains the empty pouch slot.

#### Visual Elements
- A sponge with input `mk = Poseidon^mk(nk, ψ)` (the ψ slot on the note card pulses) squeezes 4 nullifiers per permutation onto the epoch rail: `nf_4 … nf_7` from one permute, `nf_8 … nf_11` from the next.
- The OSS receives grey opaque beads `(6, nf_6), (7, nf_7), (8, nf_8)`. A decoy list sits beside them, and the OSS cannot tell the two apart.
- The race: a transaction in a mempool lane drifts toward the 9|10 sentinel gate. A single-nullifier version shatters at the gate. The `(nf_9, nf_10)` version carries a bridge over it.
- The pouch from 2.2: an output's second slot fills with a dummy `tg_⊥`. Spend and output become identical two-pip dominoes.

#### Content
- Ideal functionality: `nf_e = KDF(nk, ψ, e)`. It is pseudorandom, binds both the authority and the note, and is unlinkable across epochs without `nk`.
- Constrained PRFs would let you delegate a key, but the GGM candidate is circuit-expensive. Tachyon keeps derivation with the user. The OSS gets bare `(i, nf_i)` pairs with no note-binding evidence. "A valid sync request may equally be a decoy." Binding happens later, on the wallet.
- Construction: `mk = Poseidon^mk(nk, ψ)`; `nf_e = Poseidon^nf.Permute(mk, ⌊e/Rate⌋)[e mod Rate]`. One permutation yields a Rate-sized window. From here on, write `nf_e = f_mk(e)`.
- Security, one line: unrevealed evaluations stay indistinguishable from random. That single property carries balance, note privacy against the sender (who never learns `nk`), and spend unlinkability across epochs, delegation included (delegation is *list-bounded*).
- The race: if a spend proves only `nf_e`, the epoch can tick while it waits in the mempool. Nobody else can refresh it: the miner can't, and neither can the OSS, which never learns spend-time values. So every spend reveals `(nf_e, nf_{e+1})`, and every output pads with a dummy `tg_⊥ = H^{cm⊥}(r_⊥)`. Without padding, `t` against `n` leaks the split (`s = t − n`). With padding, `t = 2n`. The leak was only arity, since tachygrams ride as one flat multiset.

### Scene 3.3 — The ranged nullifier commitment
**Duration**: ~170 s
**Purpose**: The first real math set piece. How the wallet will later prove that the OSS tested *its* nullifiers, index by index, without the OSS learning anything.

#### Visual Elements
- Two rails: wallet range `R = [4, 12)` above, OSS range `S = [6, 9)` below, with a containment bracket.
- Each `(i, nf_i)` bead crystallizes into a cubic-factor tile `F_{i,nf_i}(X) = ((i+1)X + nf_i)³ − c`. Tiles multiply into a growing stack (factor stacks, not curves). The stack grows one tile at a time, and its right end stays open.
- Division: the OSS stack lifts out of the wallet stack, leaving the quotient `q`. A random probe `r` strikes all three, and the equality lights gold.
- Soundness sidebar on the `F_13` clock: `Y³ − 2` takes no cube value on the clock (the cubes are {1, 5, 8, 12}, and 2 is not among them). Then the ω-collision is drawn and crossed out by the scale comparison: `2^32` epochs against a ~255-bit ω.

#### Content
- The need. The wallet derives over `R`. The OSS tests over `S`. The wallet must prove that every `(i, nf_i)` the OSS tested is one it derived, at the same index, and both sides grow incrementally across many PCD steps.
- A vector commitment would do it, but the known ones live on RSA or pairings, which are circuit-hostile. One relaxation saves us: here every update is *proven* honest against the running commitment, which expands the design space.
- Encode position and value together as an irreducible cubic factor. Commit to `g_R(X) = ∏_{i∈R} F_{i,nf_i}(X)`, an **indexed multiset**, extended one factor at a time with no fixed endpoint.
- Subset is division: exhibit `q` with `g_R = g_S · q`. All three commitments are fixed before the challenge `r`, so the check is one identity at one point, and the second port of the black box does the work.
- Soundness. `p ≡ 1 mod 3`, so `c = 2` is a public non-cube, and `Y³ − c` is irreducible. Invertible affine substitutions keep it irreducible (`a = i + 1 ≠ 0`). Unique factorization does the rest. The only forgery window is `(a₁, b₁) = ω(a₂, b₂)` with `ω³ = 1`, which is impossible for `i < 2^32`. The range of `i` isn't constrained directly: the increments are enforced, and out-of-range values break the anchors.
- A caution: division is commutative, so it proves inclusion, not order. Order and contiguity come from counters and **sentinel** endpoints, checked as each side is built. "Hold that word. The OSS will ratchet from sentinel to sentinel."

#### Narration Notes
Mark this scene with ⟨pause⟩ beats around the factor definition and the soundness argument.

---

## Chapter 4 — Exclusion at scale: quadratic residue filters (~8 min) — *centerpiece*

### Scene 4.1 — The epoch accumulator, and the wall
**Duration**: ~90 s
**Purpose**: The naive exclusion and why it fails at scale. Set the target.

#### Visual Elements
- Inside epoch 6 on the rail, the per-stamp polynomials zipper-multiply into one `e(X)`. Its degree counter spins to 4.8 × 10⁸, and a verifier stopwatch runs past 16:00. The frame tints flare.

#### Content
- To prove `nf_6 ∉ epoch 6`, testing every stamp's accumulator is wasteful. Union is multiplication, so build the epoch accumulator `e(X) = ∏ f_i^tg(X)`, proven correct against the anchor chain by random-point queries. The queries are served by the folding scheme, not a step circuit, so `e(X)` may have as high a degree as the PCS allows, independent of any step-circuit size limit. That work is linear, but it is paid once and amortized.
- Framing: `e(X)` is the strawman. Ragu can technically support a very high degree. Tachyon chooses to allow only bounded degree, and this scene shows why the QR trick is needed.
- Run the numbers. At 100 TPS, all 2-in-2-out, over a two-week epoch, there are more than 4.8 × 10⁸ tachygrams. With a Bulletproofs-style PCS and its linear-time verifier, one verification takes more than 16 minutes. That doesn't ship.
- Target: epoch-wide non-membership at sublinear amortized cost, with no high-degree polynomial anywhere near query time.

### Scene 4.2 — Bucketing by an address the element computes itself
**Duration**: ~140 s
**Purpose**: The bucketing idea, and the number theory that makes the address cheap to prove (QR, the flip, discriminants, the −R convention).

#### Visual Elements
- `e(X)` shatters into a grid of small buckets. A query element computes a bit string over its head and homes in on exactly one bucket.
- **The `F_13` clock**: 12 nonzero dots, half cyan (QR {1, 3, 4, 9, 10, 12}) and half amber (NQR). Multiplying by `c = 2` swaps the colors in place: the flip. Sliding the offset R recolors the ring. The `x = −R` dot blinks white and is assigned to the QR side.

#### Content
- Partition the epoch so that a queried value can compute its own bucket address. Exclusion then becomes one opening against one bounded bucket.
- Detour. Over a prime field the nonzero elements split exactly in half. Proving `x ∈ QR` takes one advice root and one constraint, `y² = x`. Proving `x ∈ NQR` uses the flip: with a fixed public non-residue `c`, `y² = c·x`.
- A **QR discriminant** asks whether `x + R` is a square. `k` discriminants give a `k`-bit **profile** and `2^k` near-balanced classes, computed from `x` alone. The edge case: `x = −R` goes to the residue side by convention, and a claimed non-residue bit needs `x + R ≠ 0` (an inverse witness), or `−R` could take the NQR branch with root 0.

### Scene 4.3 — The batched QR test and one decomposition
**Duration**: ~130 s
**Purpose**: Certify a whole bucket's class with one identity, then split a bucket with four checks.

#### Visual Elements
- On the field line, roots `x_i` carry lifted square roots `y_i`. An interpolating curve `g` threads through them. `g(X)² − X` collapses onto `f · h`, the probe `r` strikes, and both sides print the same element.
- One bucket cleaves under a discriminant blade into `q₀` (amber, NQR) and `q₁` (cyan, QR). Four lamps light in turn, each with its identity.

#### Content
- Batched test: given a square-free `f = ∏(X − x_i)` with all roots QR, interpolate `g(x_i) = y_i`. Then `g² − X` vanishes on every root, so `f` divides it. Commit to `g` and `h = (g² − X)/f`, and check `g(r)² − r = f(r)·h(r)`. The NQR version carries `c`, and an offset replaces `X` by `X + R`. Square-freeness, guaranteed by the consensus duplicate rule, is what makes interpolation possible.
- Decomposition of `f` into `q₀`, `q₁`. Four checks at one random point: (1) `f(r) = q₀(r)·q₁(r)`; (2) QR purity of `q₁`; (3) NQR purity of `q₀`; (4) `q₀(−R) ≠ 0`, which enforces the zero convention because `q₀` is a product of linear factors, and check 1 then forces `−R` into `q₁`.

### Scene 4.4 — Routing: decompose, merge, and a jagged frontier
**Duration**: ~150 s
**Purpose**: How an OSS builds full-epoch, bounded buckets in flight. The signature animation of the video.

#### Visual Elements
- The stream: stamps along epoch 6 roll into bounded **summaries** (each a product polynomial plus an anchor range), which become root buckets.
- A routing round station: each bucket splits into amber and cyan, adjacent same-profile children fuse when they fit, and an unmergeable child stays solo. Anchor ranges are drawn as brackets under each bucket: decomposition keeps the bracket, merge joins two adjacent brackets.
- A zoom-out shows the braided network across rounds. The frontier edge is visibly jagged, and finished full-epoch buckets click onto a finish rail spanning `sntl_6 → sntl_7`.
- The discriminant dial sits behind the OSS's glass until the epoch closes. An adversary aiming tachygrams at one bucket finds nothing to aim at.

#### Content
- While epoch 6 is live, the OSS summarizes stamps into bounded summaries (`p'(r) = p(r)·a_T(r)`, advancing the anchor). Each summary becomes a root bucket with profile `(j, b) = (0, 0)`. A summary never crosses a sentinel.
- A round decomposes every bucket under the next discriminant, which roughly halves each one. It then merges adjacent outputs with the same extended profile whenever the union fits capacity. Merging is just the union check, with nothing new to trust.
- The invariant: decomposition preserves anchor ranges, and merges join contiguous ones. So many partial-epoch buckets become one full-epoch bucket per profile. The routing is parallel, streaming, and runs in flight.
- Stragglers get **partial rounds** for only the unresolved profiles. The result is a jagged frontier: final profiles at different depths, forming a prefix partition of the field, each spanning the whole epoch. A seal checks `sntl_6` and `sntl_7`.
- How a split becomes proof steps, in one sentence: the split step proves the product identity and the `−R` check, then each of two descents returns one side while checking the *opposite* side's purity. Deriving both children therefore checks the purity of both buckets, so the four decomposition checks all hold. No further subtlety is discussed (the spec has the full story).
- Grinding: discriminants must be unpredictable while users choose tachygrams. Each OSS samples `R₀` privately, uses `R_{j+1} = R_j + 1`, and reveals `R₀` after the close. Choice affects balance, never soundness. A biased network can be ignored in favor of an honest one. Consecutive offsets have negligible correlation (one character-sum footnote on screen).
- Scale, **as an on-screen card only** (the narration says one sentence: "Even at fifty thousand transactions per second, a 32-bit profile has room to spare"). The card reads: 50K TPS × 8 tachygrams × 2 weeks < 4.84 × 10¹¹ tachygrams; < 6.1 × 10⁷ root buckets at 8,000 entries; k ≤ 26 within the 32-bit budget.

### Scene 4.5 — The evidence tree
**Duration**: ~90 s
**Purpose**: Compress the final buckets into one reusable certificate, and price the query.

#### Visual Elements
- Final buckets fold upward into a quaternary (rate-4 Poseidon) tree, and one root glows star-white over epoch 6 on the rail. The same happens for epochs 5, 7, and 8: one root per closed epoch.
- Query: our `nf_6` climbs a Merkle path and opens its bucket, nonzero. Our `cm` in epoch 5 opens a bucket, zero, with no profile computed.
- Cost cards: `e(X)`: deg 4.8 × 10⁸, 16 min → bucket: ≤ 13 hashes + one bounded opening.

#### Content
- After the close the OSS folds any chosen set of final-bucket proofs into one **evidence tree**. Each leaf binds the epoch, both sentinels, `R₀`, the depth `j`, the profile `b`, and `Com(q_b)`. Its public output is one root. A one-leaf tree is valid too, because coverage isn't required: every leaf is already a sound full-epoch bucket.
- Membership: authenticate the leaf, then check `q_b(x) = 0`. No profile is needed, since every bucket divides the epoch polynomial. Non-membership: re-derive the first `j` discriminants from `R₀`, check that `x`'s bits encode `b`, and check `q_b(x) ≠ 0`.
- Since routing ran in flight, tree construction is the only post-epoch work on the critical path. Built once per epoch, it serves every wallet. That is the "shared evidence" of the blog post's title.

---

## Chapter 5 — The proof tree: spending our notes (~7 min)

### Scene 5.1 — Steps, headers, bridges
**Duration**: ~80 s
**Purpose**: The PCD vocabulary and the role colors, set up quickly.

#### Visual Elements
- The three monolithic statements (Output, Spend, Bundle) flash as cards, then shatter into a tree of small steps.
- A generic step consumes two headers. Equality pins snap matching fields together, and a mismatched pin repels with a flare flash.
- Legend: gold = wallet steps (see the note), cyan = OSS steps (see opaque values), star-white = shared evidence (`AnchorChain` for the active epoch, evidence trees for closed epochs).

#### Content
- A step is a bounded circuit. It takes up to two child proofs plus private witness, checks part of a statement, and emits a **header**, the "data" in proof-carrying data. Parents **bridge** children by equality-checking shared fields: the same `cm`, matching sentinels. A sound decomposition is exactly *enough bridging*.

### Scene 5.2 — Same-epoch spend: the base tree
**Duration**: ~100 s
**Purpose**: The simplest complete spend, and the important base case. It introduces the steps every spend shares (`SpendBind`, `OutputSeed`, `StampMerge`, `StampLift`), so the past-epoch tree in 5.3 only adds what is new.

#### Visual Elements
- Now = 9. The wallet holds a second note, **note₉**, received earlier in epoch 9. A new note card docks under note₅'s. Its creation bead sits inside epoch 9 on the rail.
- The tree grows node by node, bottom-up: `SpendableInit → NoteSpendable{cm_B, 9, anchor}` → `SpendBind → Stamp`. `OutputSeed → Stamp` comes in from the side for an output. `StampMerge` joins them. `StampLift` slides the merged stamp along a star-white `AnchorChain` and bounces off the 9|10 sentinel gate.
- A checklist beside the tree ticks each clause of the monolithic Spend/Output statements as the step that covers it lights.

#### Content
- `SpendableInit` takes the creation stamp's data as witness, proves `cm` is a root of that stamp's accumulator, and computes the stamp's resulting anchor. A same-epoch note needs no exclusion, since it didn't exist before that stamp. The wallet can cache this as soon as the creation block finalizes, and hand it to a hardware wallet early for spend-time signing in parallel.
- `SpendBind` opens the note and checks `pk = Com(ak, nk)`, `cm`, the value range, `rk = ak + [α]G` with `α = PRF(cm ‖ θ)`, and `(nf_e, nf_{e+1})`. It emits a per-action `Stamp`. `OutputSeed` covers the whole output statement in one step.
- `StampMerge` multiplies both accumulators (union is multiplication, again) and checks equal anchors.
- `StampLift` consumes `AnchorChain{anchor_L, anchor_R}` evidence and moves the stamp to a later anchor in the same epoch. The chain admits no sentinel transition, so a lift cannot cross an epoch. The lift hides the exact inclusion anchor, so spend unlinkability depends on it.
- Close: "Every spend ends this way: `SpendBind`, merge, lift. The only question is what feeds `SpendBind` when the note is older."

### Scene 5.3 — Past-epoch spend: note₅
**Duration**: ~190 s
**Purpose**: The full past-epoch tree, built over the running example. Only the part under `SpendBind` is new. This is where the Ch. 3 promise is paid.

#### Visual Elements
- The 5.2 tree shrinks to the right and stays legible. note₅'s card pulses. The rail lights three regions: epoch 5 (inclusion, singleton path), epochs 6–8 (delegated), and epoch 9 (spend).
- **Branch A (gold, epoch 5)**: two openings of epoch 5's evidence tree, one for `cm` and one for `nf_5`. `NoteUnspentInit` → `NoteUnspent{cm, 5, 6, sntl_5, sntl_6}`; `SpendableReinit` → `NoteSpendable{cm, 6, sntl_6}`.
- **Branch B (cyan, epochs 6–8)**: `UnspentSeed` (empty range, `g = 1`), then a **ratchet**. Each `UnspentLift` consumes one evidence-tree opening, proves `q_b(nf_i) ≠ 0`, appends one cubic tile, and clicks the pawl forward one sentinel. A skip attempt jams the pawl.
- **Branch C (gold, local)**: `NoteSeed → NoteMaster{cm, mk}`; two `NullifierDerive` windows `[4, 8)` and `[8, 12)`; `NullifierFuse → NoteNullifiers{cm, 4, 12, Com(g_R)}`.
- `UnspentBind` replays the Ch. 3 division animation in context: the OSS stack `[6, 9)` lifts out of the wallet stack `[4, 12)`. Then `SpendableLift` seams `NoteSpendable{cm, 6, sntl_6}` with `NoteUnspent{cm, 6, 9, …}` → `NoteSpendable{cm, 9, sntl_9}`.
- The join: that header feeds the *same* `SpendBind` as in 5.2, which derives note₅'s `(nf_9, nf_10)` → `Stamp`. The docked 5.2 tree slides back in. `StampMerge` combines note₅'s stamp with note₉'s spend-and-output stamp, and one `StampLift` moves the result to the transaction's target anchor inside epoch 9. Result: one stamp, two spends, two outputs, eight tachygrams.

#### Content
- The inclusion epoch is special and wallet-only. One step re-derives `nf_5` from the note and keys, matches its profile, and proves non-membership. A second step joins that with the `cm` membership opening for the same epoch and sentinels. Out comes a fully established spendable proof at the start of epoch 6.
- Later epochs split the work. The wallet derives and commits locally, in group-aligned windows. The OSS holds only opaque pairs, ratchets one epoch per lift, and cannot skip, repeat, or reorder an epoch.
- `UnspentBind` makes note-independent work note-specific: it requires `s_L < s_R` and `[6, 9) ⊆ [4, 12)`, then runs the quotient check. `SpendableLift` enforces the forward seam (`e_old = s_L`, `anchor_old = sntl_{s_L}`, and so on).
- Multiple OSSs: `UnspentMerge` joins adjacent ranges with sentinel equality before binding (one line, plus a quick visual).
- Privacy bottom line, stated plainly. An OSS sees opaque pairs and ranges, indistinguishable from decoys. It never sees `cm`, the note, another OSS's proof, or the spend anchor. Request timing and range policy remain wallet-level concerns.

#### Narration Notes
This is the longest scene, so pace it in three movements (branch A, branches B+C, the join with note₉'s tree). Each movement ends with its header glowing. In the narration, "branch A" etc. are visual labels only. Speak of "the inclusion epoch", "the OSS's range", and "the wallet's range".

---

## Chapter 6 — Landing: consensus and aggregation (~3.5 min)

### Scene 6.1 — The validator and the two-epoch window
**Duration**: ~130 s
**Purpose**: The new double-spend rule and why two nullifiers make the grace period safe.

#### Visual Elements
- The validator checklist (4 items) ticks.
- A timeline (redrawn from `consensus_window.svg`): where the stamp's claims end. Exclusion runs up to `sntl_9`; the target anchor is *not* an exclusion endpoint.
- A sliding two-epoch duplicate window. The race cases play out as colliding tokens, and each collision site flashes its catcher.
- Callback: the hot grid from 0.1 returns, now two epochs wide, shown to scale next to the original monster.

#### Content
- Per stamp, the validator: checks that the anchor is canonical; checks `Epoch(anchor) ∈ {cur, cur − 1}`; checks `actacc` against the action digests and `tgacc` against the published list (the `y_r` trick); and verifies one PCD proof. Balance and signatures are unchanged from Orchard.
- Scope: the stamp proves exclusion strictly *before* epoch `e`. Duplicates inside `e` are consensus's job, so every spend targeting `e` must publish `nf_e`.
- The rule: one duplicate window over the current and preceding epochs, with deterministic check-then-insert ordering. A conflict can come from the window, an earlier bundle in the same block, or an earlier tachygram in the same bundle.
- Walk the two acceptance cases for our epoch-9 stamp (it carries both notes' pairs; take note₅'s). Accepted in 9: a rival targeting 9 shares `nf_9`; a rival targeting 8 published `nf_9` as its next value; anything older lies in proven history. Accepted in 10: rivals targeting 9 or 10 share `nf_9` or `nf_10`; a rival targeting 8 accepted during 9 is still in the window, and earlier rivals are caught by past exclusion. The overlapping adjacent pair is what makes the grace period safe.

### Scene 6.2 — Aggregation, in one breath
**Duration**: ~50 s
**Purpose**: The network-level fold.

#### Visual Elements
- Mempool stamps slide to one common anchor tick, never across a sentinel, then fold into a single aggregate. Per-transaction signature seals stay attached to each constituent, and their stamps become `wtxid` references.

#### Content
- Lift each stamp to a common anchor in the same epoch. `StampMerge` unions the multisets, multiplies the accumulators, and folds the proofs. The aggregate has the same shape as a standalone stamp and can merge again. Balance and authorization stay per constituent. Verification amortizes, so the economics favor aggregating.

---

## Chapter 7 — The other half: the payment protocol (~2 min)

### Scene 7.1 — Addresses, tags, and private retrieval
**Duration**: ~120 s
**Purpose**: Close the Ch. 1 loop, briefly: what replaces Orchard's transmission key, and how a wallet finds its notes and builds its witnesses. This is a sketch of ValarGroup's design, not a deep dive.

#### Visual Elements
- An address card `addr = (pk, ek)` with two freshness dials: `ek` per sender, tag per note.
- A quantum lens over `[ivk]G_d`: one recovered `ivk` opens every incoming note, past and future.
- A tag chain: `tag₀ = H(ek)` glows differently from `tag_1, tag_2, …`.
- PIR as a black box: one silent hand reaches into a database that can't see where it reached. The epoched tachygram DB wires back into the Ch. 5 tree.
- Faerie gold: two incoming notes with a reused ψ collide at the reference-epoch nullifier, and the wallet keeps one.

#### Content
- `addr = (pk, ek)`: the payment key plus an ML-KEM encapsulation key, both fresh per sender.
- Why not diversify? `[ivk]G_d` is not quantum-private: break one discrete log and every incoming note, past and future, is exposed. ML-KEM has no "same `dk`, many unlinkable `ek`" analogue. Tags restore cheap discovery. The schedule is `tag₀ = H(ek)` for first contact, then `tag_i = H(K, i)` under the shared secret. A tag must be fresh per note, because it appears on chain.
- Trial decryption is replaced by PIR lookups by tag. The epoched tachygram DB also serves the spendability witnesses from Ch. 5, privately.
- Faerie gold, as promised in Ch. 1. Notes have no canonical position, so the wallet checks each incoming note's nullifier at a reference epoch, and a reused ψ collides there.
- Dropped for time (the spec covers them): the KEM ciphertext size and first-contact shape, the PKI DB, and AEAD state recovery.

---

## Chapter 8 — Quantum posture, and the cascade (~2.5 min)

### Scene 8.1 — Private today, sound after an upgrade
**Duration**: ~80 s

#### Visual Elements
- The on-chain objects pass under a quantum lens. Commitments, nullifiers, and memos stay opaque. `rk` resolves to `ask + α`, but α pixelates the link. Then a two-row upgrade card: a signature seal becomes a proof node, and a DL block becomes a lattice block.

#### Content
- The bar is asymmetric. Privacy must hold retroactively, because of harvest-now-decrypt-later. Soundness only has to hold at spend time.
- Audit, in one sweep. `pk`, `cm`, and the nullifiers are symmetric, and memos are ML-KEM. The discrete-log leftovers are `cv` (perfectly hiding) and `rk`, whose discrete log is masked by a fresh `α`. The quantum threat is forgery, not a privacy break.
- The upgrade, in two lines. Authorization becomes an in-circuit proof of knowledge of a PQ signature (CAPSS-style), folded into the PCD proof. Ragu's DL commitments get swapped for lattice folding, and the structure stays.

### Scene 8.2 — Outro: the cascade
**Duration**: ~60 s

#### Visual Elements
- The camera pulls back over the whole rail. Our note's journey (birth bead, delegated ratchet, evidence roots, spend) is visible at once. The chapter cards then reconnect into one dependency chain.

#### Content
- Replay. An unprunable set forced client-side validation. Delegation forced evolving nullifiers. Evolving nullifiers forced two-nullifier actions and the two-epoch window. Epochs forced one polynomial accumulator, which unified commitments and nullifiers. Its degree forced QR filters. And all of it forced a proof tree whose expensive evidence is built once and shared.
- "Each move is forced by the last."
- Pointers: the Deep Dive at tachyon.z.cash, Sean's posts and [BM25], github.com/tachyon-zcash/tachyon.

---

## Transitions & Flow

- **Persistent spine.** The note card is docked top-left from 0.2 onward and pulses when its fields matter (ψ in 3.2, `cm` in 2.2 and 5.3). The epoch rail sits along the bottom from 0.2 onward; "now" advances 5 → 9 over Ch. 3–5. The field line appears in 2.1 and returns in 3.3, 4.3, and 4.5.
- **Visual debts, repaid**: the empty pouch slot (2.2 → 3.2), the word "sentinel" (3.3 → 4.4/5.3), the shared spend steps (5.2 → 5.3), square-freeness (2.1 → 4.3), Faerie gold and `ivk` unlinkability (1.2 → 7.1), the hot grid (0.1 → 6.1).
- **Chapter boundaries end on a question**, spoken: "Where does `cm` go?" / "Now the clock moves." / "Can exclusion be cheap?" / "What does the proof actually look like?" / "What does the validator still do?" / "Who carries the rest?"
- **Within scenes**: transform, don't replace. Old context shrinks to a corner and stays legible, ready for callbacks.

## Color Palette (brand theme, 3b1b discipline)

- **Background**: deep space `#020204`. A subtle star field appears on title cards only.
- **Gold `#D4A017`**: wallet/user, and "member / zero" evaluations.
- **Cyan `#4A9EA0`**: OSS/service; QR (residue) class.
- **Amber `#E8820C`**: NQR (non-residue) class; secondary accent.
- **Flare `#FF6B00`**: danger, cost, stale, "nonzero / not a member".
- **Star-white**: shared evidence (anchor chains, evidence trees).
- **Text**: `#c8c4bf` primary, `#9a958a` muted.
- The legacy `zcash_keys.png` keeps its canonical colors (audience memory outranks the theme).
- **Type**: Computer Modern everywhere (the 3b1b look). Math is typeset; prose labels use CMU Serif. One face family across the whole video, with a 22 pt effective floor.

## Mathematical Content (to typeset)

`rk = ak + [α]G`, `rk = [α]G`, `α = PRF(cm ‖ θ)`, `pk = Com(ak, nk)`, `cm = Com(pk, v, ψ; rcm)`,
`cv = [v]G + [rcv]H`, `f(X) = ∏(X − tg_i)`, `y_r = ∏(r − tg_i)`, `a_i = Poseidon(rk_i, cv_i)`,
`anchor ← H(anchor_old ‖ i ‖ tgacc)`, `sntl_i = H^epoch(anchor_{i−1,end} ‖ i)`,
`mk = Poseidon^mk(nk, ψ)`, `nf_e = Poseidon^nf.Permute(mk, ⌊e/Rate⌋)[e mod Rate]`,
`F_{i,nf_i}(X) = ((i+1)X + nf_i)³ − c`, `g_R = g_S · q`, `(a₁X + b₁)³ = (a₂X + b₂)³ ⇔ (a₁,b₁) = ω(a₂,b₂)`,
`y² = x`, `y² = c·x`, `g(r)² − (r + R) = f(r)·h(r)`, `f = q₀ q₁`, `q₀(−R) ≠ 0`, `R_{j+1} = R_j + 1`,
`p'(r) = p(r)·a_T(r)`, `addr = (pk, ek)`, `tag₀ = H(ek)`, `tag_i = H(K, i)`, `ivk^Tachyon = (tag, dk)`.

## Technical Notes (whole video)

- **Engine**: ManimGL (3b1b) in `v2/.venv`, scenes as `InteractiveScene` subclasses, following `/manimgl-best-practices`. One file per chapter in `v2/scenes/`.
- **Math typesetting: typst (decided 2026-10-04 after a failed `Tex` smoke test).** With `dvisvgm` installed, native `Tex` still fails with the texlive subset on this machine. manimgl hard-codes `\documentclass[preview]{standalone}` (no `standalone.cls`). The default template needs ~12 absent packages (`amssymb`, `babel`, `physics`, …). A hand-rolled `article` template still fails: the CM Type1 `.pfb` outlines and Metafont `mf` are missing (so no glyph paths, and `cmex7` can't even be generated), and dvips's `tex.pro`/`color.pro` headers are missing (so `xcolor` breaks dvisvgm). Following Alex's rule (no full texlive), v2 renders math with typst → SVG in New Computer Modern (Math). That keeps the CM look. Per-part coloring and matching transforms are built by composing separately typeset pieces.
- **Audio sync**: per-scene clips with word-level timestamps; beats anchored to spoken words, never hand-timed.
- **Output layout**: `v2/scenes/` (code), `v2/audio/` (narration), `v2/renders/` (silent scene renders), `v2/video/` (muxed chapters and final cut).

## Implementation Order (after script + narration approval)

1. Shared style module: palette, the note card, the epoch rail, the field line, the `F_13` clock, the Ragu black-box glyph.
2. Ch. 2 + Ch. 3 first. They define the spine objects every later chapter reuses.
3. Ch. 4 (centerpiece; the longest build).
4. Ch. 5 (reuses the Ch. 3–4 objects).
5. Ch. 0, 1, 6, 7, 8.
6. Assembly.

## Decisions log

### Round 1 (2026-10-04, Alex)

1. **Toy field `F_13`**: keep. All on-screen arithmetic examples are concrete.
2. **Same-epoch spend**: not a counterfactual. It is the base case and an important
   case, taught first (5.2) so that `SpendBind`, `OutputSeed`, `StampMerge`, and
   `StampLift` are familiar before the past-epoch tree. To keep it in the running
   example, a second note₉ (received in epoch 9) is spent in the same transaction
   as note₅.
3. **Routing descent subtlety**: say only that each descent checks the opposite
   side's purity, so deriving both children ensures both buckets are pure.
   Completeness-vs-purity is left out (the spec has it).
4. **Payment protocol**: about 2 min, one scene (7.1).
5. **F1**: say "Ragu is designed to expose…" polynomial queries.
6. **F2**: the spec is right. `e(X)` is a strawman. Ragu can technically support a
   high degree, but Tachyon chooses bounded degree. `e(X)` motivates the QR filter.
7. **F3**: stay silent on Ragu's properties (no ZK caveat).
8. **F4**: ignore compressed-stamp details for now.
9. **Minor**: "fuse" is fine. Use the zkalc estimate as stated (similar on Vesta and
   Pallas). `D/|F|` is good enough.
10. **Typesetting**: try `Tex` with the installed packages (dvisvgm now present),
    and fall back to typst if full texlive would be needed. The result was a fall
    back to typst (see Technical Notes).

### Round 2 (2026-10-04, Alex)

1. **Two notes**: approved. They are labeled by birth epoch (note₅, note₉) instead of
   A/B, so naming implies no order. They stay in one transaction for animation
   convenience: `StampMerge` then joins the two trees naturally. Separate
   transactions would also be valid.
2. **Title**: keep *Scaling Zcash with Tachyon*.
3. **Length**: slightly over 40 min is fine. Kept: 1.1 and 1.2 as separate scenes;
   the txid beat (effecting data vs updatable authorization data); both acceptance
   cases. Applied: the 4.4 scale numbers became an on-screen card; 8.1 was cut
   to ~80 s.

## Open questions for review

None. Flow approved by Alex (2026-10-04). Verbatim narration: `NARRATION.md` (draft 1, awaiting review).

### Round 3 (2026-10-04, Alex's review of the full cut)

- Ch1: horizontal split kept. The DA-layer chain sits in the shielded band, and the encrypted payload originates in the payment band.
- Notation: the accumulators are `acc^act` and `acc^tg` everywhere (replacing actacc/tgacc). Header name: `Unspent` (replacing ArbitraryUnspent).
- Ch2: the anchor chain is cut to 4 stamp ticks with slower absorption. Ch2–4: no docked note card, and titles are centered.
- Ch3: the F-factor expansion and g_R stay on screen together.
- Ch4: the split/merge routing mechanic follows v1 act5 Scene54 (demo/act5.mp4 from 5:12).
- Ch5: note₅'s dot is hidden while note₉ is discussed. The StampLift "anchor" marker never passes "now". The docked notes are removed.
- Ch6: a stamp is drawn as actions carrying 2 tachygrams each. 6.1 is re-narrated around the grace-period double-spend attack (the pair plus the two-epoch window come as a set); the two-case walk-through was dropped. 6.2 aggregation is redrawn.
- Ch8: replaced by v1's 8.1/8.2 text and act8 animation (audit table, cascade), with audio regenerated in v2's voice.

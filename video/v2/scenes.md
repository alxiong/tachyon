# Scaling Zcash with Tachyon — v2 Staged Script (Draft 4)

> Status: **flow approved (draft 3, 2026-10-04); synced to `NARRATION.md` Draft 2 (Sean's voice) on 2026-10-08.**
> Stage 1 (this file): scene flow + visual plan, one section per narration scene.
> Stage 2: verbatim narration, `NARRATION.md` (the authority for wording and for every `⟨pause: …⟩` anchor).
> Stage 3: audio → manimgl animation → assembly. Audio is moving to an AI voice (Brian) carrying
> Sean's prosody via ElevenLabs speech-to-speech, rendered scene by scene.
>
> Every held `⟨pause: label⟩` in the narration is listed below, in order, as **Pause beats**
> under its scene, and each one names the visual event that fills it.

## Overview

- **Topic**: the Tachyon shielded protocol, top to bottom, per `book/src/revisit.md`.
- **Hook**: *Prove that a coin was never spent, when nobody keeps the list of spent coins.*
- **Target audience**: Zcash protocol engineers fluent in Sapling/Orchard internals
  (key tree, `rk` re-randomization, binding signature, Pedersen `cv`, Merkle anchors).
  Strong algebra (finite fields, polynomial identities, Schwartz–Zippel) assumed.
  No "what is Zcash." Orchard is the diff baseline throughout.
- **Estimated length**: ~50 min of narration (26 scenes, eight chapters plus the prologue),
  estimated from the Draft 2 word count at Sean's pace (~200 wpm while speaking) plus the held pauses.
- **Key insight**: one primitive, *a commitment to the polynomial whose roots are
  your set*, carries almost the whole design. Zero/nonzero evaluations give membership
  and non-membership. Polynomial multiplication and division give set union and
  subset. Random-point identities let a folding proof system check all of it cheaply
  and natively. Every later construction is this primitive plus one more idea.
- **Ragu**: a black box with two parts (the fuse part and the query part). Stated once
  in the prologue. Never explained.

## Narrative arc

The video follows **one note**, note₅, from its birth in epoch 5 to its spend four
epochs later. A second, fresh note, note₉, is received in the spend epoch and spent
in the same transaction. note₉ gives the proof tree its base case. The notes are
labeled by birth epoch (on screen as subscripts), so the labels imply no teaching
order.
Every mechanism enters exactly when that note needs it. First the note's keys (the
separation of spend authorization from note transmission). Then a place in the pool
(the polynomial accumulator, the stamp, the anchor chain). Then time passes, and the
note needs to prove it was never spent without revealing anything to its helpers
(evolving nullifiers, the ranged commitment). The proof has to stay cheap at real
throughput (QR filters, the evidence tree). The proof itself has a shape (the proof
tree). Finally the spend lands, and consensus and aggregation take over. The
payment protocol and the quantum posture close the loop opened in chapter 1.

Scenes start on their first fact and end on their last one (narration rule 5: no
narrator bridges). The cascade is replayed once, in the outro.

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
  demoted, GGM named once only as the rejected constrained-PRF candidate, PIR as a
  black box, a one-line `#nf-sec`). Aggregation, once a single breath, is now two
  scenes (round 4).
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
**Duration**: ~75 s
**Purpose**: Name the scaling wall. Make the audience feel why nullifiers, not commitments, are the problem.

#### Visual Elements
- Split stage, both sets growing side by side at the same rate. Left: a commitment Merkle tree accreting leaves. Right: a nullifier set as a hot grid inside a "RAM" frame.
- The tree prunes down to its frontier: interior nodes and old leaves dissolve, one hash per level stays lit along the right edge, and a small "O(log n)" tag settles beside it.
- Incoming transactions fire membership probes into the grid.
- A counter rolls to "500 GB / day".

#### Pause beats
1. *both sets grow side by side* — both structures grow in lockstep, one entry per created note and one per spent note.
2. *the tree prunes down to its frontier* — the Merkle tree collapses to its frontier (one node per level).
3. *counter rolls to 500 GB / day* — the counter beside the grid.

#### Content
Every shielded pool keeps two sets, growing at roughly the same rate: one entry per created note, one per spent note. The commitment tree is append-only, so to keep appending, validators only need its frontier (one hash per level). Everything else can be pruned today, and the state validators keep for the tree grows only logarithmically with its size. The nullifier set must answer "never seen before?" for every input, against all of history, in memory, on the critical path of every validator. At Visa-level throughput it grows by about 500 GB a day, and nothing in it can ever be thrown away: a ten-year-old nullifier still has to block a double spend today. A linearly growing set that nobody can prune.

#### Narration Notes
- The opening line is a statement ("Every shielded pool in Zcash has two sets…"), with the picture already growing.
- End on the fact: "It's a linearly growing set that nobody can prune."

#### Technical Notes
- Merkle tree: `VGroup` of `Line`s + `Dot`s grown with `LaggedStart(ShowCreation)`. The prune is a staggered fade of everything except the frontier path; the frontier nodes stay lit. No "disk" slab: the point is that the tree's state shrinks, not that it moves.
- Grid: `VGroup(*squares).arrange_in_grid`; probes as `Line` flashes; overflow via `self.frame` pull-back.

### Scene 0.2 — The thesis, the black box, and our protagonist
**Duration**: ~110 s
**Purpose**: State client-side validation, state the Ragu interface once, and introduce the note we will follow.

#### Visual Elements
- The hot grid is scissored. A thin "recent window" stays with the validator, labeled as kept by consensus. The rest is pruned from validator state and flies to wallets, each holding a proof token.
- The proof token extends a little at each new block (proof-carrying data, built incrementally).
- A "Ragu" black box with two labeled parts: **fuse** (two proof tokens plus a little new work in, one out) and **query** (an envelope `Com(f)` + a point `r` in, `f(r)` out).
- The epoch rail draws itself along the bottom (epochs as long stretches of blocks), ticks 4…10. A fresh note card appears and docks top-left, marked "born 5, spent 9".

#### Pause beats
1. *the grid is scissored, older history flies to wallets* — the cut, then the older history flying off.
2. *fuse and query parts animate* — the fuse part merges two tokens, then the query part answers one evaluation.
3. *note card docks, epoch rail draws itself* — the protagonist docks and the rail draws.

#### Content
- Tachyon starts from one principle: move validation off the critical path of consensus and onto the client whenever we can. Consensus keeps only recent nullifiers, and everything older can be pruned from validator state. The spender proves that the nullifier is absent from that older history.
- That proof can't be made once and forgotten. Each block adds history to cover, so it is built incrementally as proof-carrying data, extended a little as the chain moves.
- The black box: Tachyon runs on Ragu, a PCD system in the Halo lineage, over the Pasta curves, with no trusted setup. Two parts. (1) **Fuse**: two proofs and a little new work in, one proof out. (2) **Query**: commit to a polynomial, name a point, get back its value. Ragu is designed to expose these evaluation claims directly and fold them into the proof system's own claims, so they cost no circuit constraints. "For performance, as we'll see, this is pretty critical."
- Time is divided into epochs, long stretches of blocks. We follow one note, born in epoch 5 and spent in epoch 9, and every piece of Tachyon shows up exactly when this note needs it. (note₉ is introduced later, in 5.2, where it is needed.)

#### Narration Notes
- The Ragu statement is deliberately short and flat: an interface contract, not a tutorial.
- The note intro is the emotional hinge of the opening. Slow down.

#### Technical Notes
- Black box: `RoundedRectangle` + two part `Arrow`s; reused later as a tiny glyph whenever a query fires.
- Note card: a 4-slot `VGroup` (pk | v | ψ | rcm). Its slots fill in during Ch. 1. Keep the card as one persistent mobject across the scenes of a chapter (rebuilt at the start of each scene file in the same position).

---

## Chapter 1 — Ownership, stripped down (~5 min)

### Scene 1.1 — Why Zcash keys got complicated
**Duration**: ~120 s
**Purpose**: The diff baseline. Show that Orchard's key tree serves three jobs, only one of which is ownership.

#### Visual Elements
- Opening: the note card with a fan of keys behind it ("each note is associated with a family of keys").
- The canonical `zcash_keys.png` diagram, kept in its own colors (audience memory). Sprout's two keys (payment key, encryption key) appear beside it for contrast.
- Three highlight passes, each circling a subgraph with hand-drawn contours (never dim the raster):
  1. authorization: `ak` in the witness, `rk = ak + [α]G` in the instance, with a small "α = randomizer" tag;
  2. transmission: the transmission key and diversified addresses, with `ivk` detecting every incoming note for the same owner;
  3. viewing: `ovk` and the viewing family.
- Final pass: `nk` ("derives nullifiers") and `ak` ("authorizes the spending of notes") stay circled; the rest is tagged "transmission and viewing".

#### Pause beats
1. *Orchard's key diagram beside Sprout's two keys* — the two diagrams side by side.

#### Content
- In Zcash a note is associated with a family of keys; we start by examining that structure.
- Sprout (after the Zerocash paper) needed only a payment key and an encryption key. Orchard's diagram is far more complicated. Why?
- Reason 1: proving and authorizing became different roles. Hardware wallets can't run a computationally heavy proving algorithm, so from Sapling on, authorization is a signature made outside the proof. A fixed key would link every spend by the same owner, so the key is re-randomized: the authorization key `ak` in the witness, the randomized key `rk = ak + [α]G` in the instance, `α` the randomizer.
- Reason 2: the address does two jobs. It declares the owner and carries the transmission key, which the sender uses to encrypt the note's secrets that go on chain. Diversified addresses refresh the transmission key per sender while one `ivk` still detects every incoming note for the same owner.
- Reason 3: selective disclosure (show flows to an auditor without spend authority). That adds `ovk` and the viewing-key family.
- The observation: exactly two keys enforce ownership. `nk` derives nullifiers. `ak` authorizes the spending of notes. Everything else serves transmission and viewing.

#### Narration Notes
Inductive: the question first, then the three reasons, then the observation. No drama.

#### Technical Notes
- `ImageMobject` for the PNG plus pixel-mapped contour overlays. Re-add overlays after any image animation (draw-order gotcha).
- `rk = ak + [α]G` and the "α = randomizer" tag are typst (`mtex`), landing on "randomizer".

### Scene 1.2 — Separating authorization from transmission
**Duration**: ~145 s
**Purpose**: Tachyon's first decision. Spend authorization and note transmission become two different protocols: the shielded protocol keeps only ownership, the payment protocol owns everything else.

#### Visual Elements
- A blade separates the key tangle into two boxes, landing on "separates the concerns". Left (or top band): shielded protocol, `(ak, nk) → pk = Com(ak, nk)`. Right (or bottom band): payment protocol, holding addresses, memo encryption, note discovery, and viewing.
- `pk = Com(ak, nk)` with two property chips: **succinct** and **quantum-recoverable** (the "*and*" lands as both chips light together). A sender holding a quantum lens tries `ak` directly (harvest-now, decrypt-later risk) and then `Com(ak, nk)` (opaque).
- A small "ZIP wallet standard / wallet implementation" tag on the derivation arrows into `ak`, `nk`.
- A security-property ledger divides between the two boxes. A Faerie gold mini-glyph sits on the payment side: two incoming notes sharing one nullifier, only one spendable.
- The ledger as a data-availability layer: an encrypted memo envelope passes *through* the shielded box untouched, labeled "opaque bytes".
- Unchanged pieces, named once: RedPallas seal with the same re-randomized key; binding signature over homomorphic `cv`s.
- Payoff chips on the shielded side: "streamlined, stable core", "isolated assumptions for auditing"; on the payment side: "designs evolve in parallel, no pool upgrade".

#### Pause beats
1. *the blade cuts the key tangle into two boxes* — the separation itself. (The label keeps the picture; the voice says "separates the concerns of spend authorization and note transmission".)

#### Content
- Tachyon separates the concerns of spend authorization and note transmission into two different protocols. The shielded protocol's job shrinks to the minimum the pool needs: bind every note to an owner, and make sure only that owner can spend it. The payment protocol owns everything about getting a note to its recipient: addresses, memo encryption, note discovery, viewing.
- The owner field becomes a payment key `pk = Com(ak, nk)`, a binding commitment we instantiate with symmetric primitives, so it is succinct *and* quantum-recoverable today. Handing `ak` (a Schnorr verification key) directly to every sender, who may have a quantum computer, is a harvest-now, decrypt-later risk. A hash commitment to it is not.
- The shielded protocol never constrains how `ak` and `nk` are derived, only that they look freshly sampled. Concrete derivation paths are up to the wallet implementation or a ZIP wallet standard.
- Security properties are divided too. The shielded core keeps ledger indistinguishability, balance, note privacy, and spend unlinkability against an attacker holding only the payment key. Full unlinkability against a viewing-key holder, and resistance to Faerie gold (a sender pays you twice with notes sharing a nullifier, so only one can ever be spent), move to the payment protocol. Faerie gold comes back in Ch. 7.
- The ledger also becomes a data-availability layer. Encrypted memos are still transmitted on chain; the shielded protocol carries them as opaque bytes and never parses or interprets them.
- Unchanged from Orchard: RedPallas spend authorization with the same re-randomized key; the binding signature over homomorphic value commitments.
- The payoff: a streamlined, stable shielded core; cleaner isolation of security assumptions for auditing; and payment-protocol designs that can evolve in parallel without upgrading the shielded pool.

#### Technical Notes
- The blade: `Line` with a glow sweep; children `ReplacementTransform` into the two boxes.
- Faerie gold glyph: two note cards with one shared flare nullifier bead; one card greys out.

### Scene 1.3 — The note
**Duration**: ~45 s
**Purpose**: Fill in the protagonist's card. Plant ψ.

#### Visual Elements
- The note card's four slots fill: `pk`, `v`, `ψ`, `rcm`. `cm = Com(pk, v, ψ; rcm)` appears beneath with a Poseidon sponge icon. A Pedersen expression (Sapling/Orchard) sits beside it and is crossed out. ψ stays highlighted, with a faint arrow from the wallet's master key into ψ and a faint arrow out of ψ toward "nullifiers".

#### Pause beats
None.

#### Content
- `Note = (pk, v, ψ, rcm)`; `cm = Com(pk, v, ψ; rcm)`, instantiated with Poseidon, a sponge hash, so it is purely symmetric.
- Contrast: Sapling and Orchard use Pedersen variants, which rest on discrete log. Orchard needs extra wallet rules on `rcm` derivation for quantum recoverability. Tachyon's commitment doesn't.
- ψ is the note's pseudorandom identity, derived from the wallet's master key and used as a seed to derive the note's nullifiers. The scene ends there (no bridge question).

---

## Chapter 2 — Birth: one accumulator, one stamp, one chain (~6.5 min)

### Scene 2.1 — A set as the roots of a polynomial
**Duration**: ~145 s
**Purpose**: Introduce the primitive that carries the whole video, concretely and with the full set↔polynomial dictionary.

#### Visual Elements
- **The field line** appears (`F_13` labels for now). Roots 2, 7, 11 drop on it as dots. Beneath, the factored product `(X − 2)(X − 7)(X − 11)` builds factor by factor. Committing seals it into an envelope labeled "accumulator" (a short commitment to the whole set).
- A probe (vertical line) hits 7 → the evaluation snaps to 0 (gold, "member"). A probe hits 5 → nonzero (flare, "not a member"). A tiny Ragu query glyph fires for both.
- The Merkle tree and the nullifier grid from 0.1 dissolve into this one accumulator. A "tachygram" chip (32 bytes, `cm` or `nf`, indistinguishable) labels the roots.
- The dictionary is shown live: insert = multiply, remove = divide, union = product (no disjointness needed), subset = exact division, all checkable at one random point.
- A ghost root sneaks into the envelope and the probe gives a wrong answer; then the verifier computes `y_r = ∏(r − tg_i)` itself and the envelope opens at `r` to that value.

#### Pause beats
1. *roots drop on the field line, product builds factor by factor*
2. *Merkle tree and nullifier grid dissolve into one accumulator*
3. *the dictionary completes*
4. *a ghost root sneaks in, the probe lies* — the extra root makes the query give a wrong answer.

#### Content
- Take {2, 7, 11} in `F_13`; build `f(X) = ∏(X − x_i)`; committing gives an accumulator. Membership is one evaluation: `f(7) = 0`, `f(5) ≠ 0`. Both answers come from Ragu's query part.
- Today every pool keeps a Merkle tree for commitment membership and a set for nullifier non-membership. If one structure answers both at the same cost, why keep them apart? Tachyon doesn't. Every member is a **tachygram**, a 32-byte blob that might be a note commitment or a nullifier; on chain you can't tell which.
- The dictionary: insert multiplies by a factor, remove divides it out, union is the product (no disjointness required), subset is a divisor, so containment is exact division. Each is checkable at a single random point.
- Evaluation ignores multiplicity, so strictly this is a multiset, but consensus refuses duplicate tachygrams, so every accumulator that matters has distinct roots. (Plant this: the QR test needs it in 4.3.)
- Binding ≠ correctness. The commitment opens to one polynomial, but nothing says it has the published roots; a prover could add or drop a root and queries would give wrong answers. The verifier picks `r`, computes `y_r = ∏(r − tg_i)` with field operations only (no group work), and asks the commitment to open at `r` to that value. A false polynomial passes with probability at most `D / |F|`.

#### Narration Notes
This is the conceptual spine. The narration does not announce it; the picture does (the dissolving tree and grid).

#### Technical Notes
- `NumberLine` (manimgl) with integer ticks 0–12; roots as `Dot`s with `GlowDot` halos.
- Product: build the equation from separate typeset parts so factors can slide in and out (manual `ReplacementTransform`).

### Scene 2.2 — The action and the stamp
**Duration**: ~160 s
**Purpose**: How our note's `cm` enters the pool. The action description, the output statement, and the stamp.

#### Visual Elements
- An output action creates the note. Tachyon's action description: two values, `(rk, cv)`, labeled "randomized key" and "value commitment". A second card shows that spend actions and output actions share this same description.
- An Orchard action card `(cv, rt, nf, rk, cmx, epk, …)` morphs into Tachyon's `(rk, cv)`; `nf` and `cm` detach.
- The binding through α: `α = PRF(cm ‖ θ)`; output `rk = [α]G`, spend `rk = ak + [α]G`. A hot device signs outputs with key α, no custody round trip. Both `rk` forms resolve to uniform points: a spend card and an output card become indistinguishable by their `rk`.
- The output statement on one card: `cv` hides `−v`; `0 ≤ v ≤ MAX_MONEY`; `cm` opens to this note; `rk` bound to `cm` through α; no published tachygram is zero. "No anchor, no epoch."
- The action accumulator: each `(rk, cv)` hashes through Poseidon into `a_i`, accumulated like before into `acc^act`.
- The stamp card: public inputs `(acc^act, acc^tg, anchor)` plus the published tachygram list. `cm` drops into the tachygram pouch, and a second, empty slot sits beside it, unexplained ("we'll fill it in later").
- The txid / wtxid split, drawn as two field groups: *effecting data* (`acc^act`, value balance, memo digest) feeding `txid`, and *authorization data* (the stamp and the signatures) feeding `wtxid`. The two category names appear in italics as they are spoken. A user swaps the stamp: `wtxid` flickers, `txid` stays lit. The memo digest is tied to every signature through the sighash.

#### Pause beats
1. *Orchard's action card morphs into (rk, cv)*
2. (short `⟨pause⟩` after "that's the action accumulator", before the stamp enters.)

#### Content
- The action description is `(rk, cv)`, shared by spend actions and output actions. No `nf`, no `cm`: nullifiers won't stay fixed (coming soon), so they can't live in a static description. The note binds to its action through `rk`'s randomizer: `α = PRF(cm ‖ θ)` with fresh entropy θ. Output `rk = [α]G`; spend `rk = ak + [α]G`.
- An output's signing key is α itself. Creating a note needs no spend authority, because the binding signature already guarantees outputs are funded, so a hot device can sign outputs without a round trip to custody. Both forms of `rk` are uniform points, so nobody can tell a spend action from an output action by its `rk`.
- The output statement (see the card). No anchor and no epoch, because history can't affect an output.
- The action multiset: `a_i = Poseidon(rk_i, cv_i)`, accumulated into `acc^act`. Same primitive, second use.
- A **stamp** is the bundle's PCD proof, with public inputs `(acc^act, acc^tg, anchor)`, publishing the tachygrams alongside. Our `cm` is one of them; the empty second slot is a visual debt.
- Where the stamp lives: `txid` commits only to *effecting data* (`acc^act`, the value balance, a digest of the memo bytes). The stamp and the signatures are *authorization data*, malleable by design. A user can update a stamp, which changes the `wtxid` but not the `txid`. The memo is safe from that rewriting because every signature covers its digest through the sighash.

#### Technical Notes
- The pouch with an empty second slot is a deliberate visual debt. It is repaid in 3.2.
- Keep the txid / wtxid diagram as a module-level builder; 6.2 rebuilds it.

### Scene 2.3 — The anchor chain
**Duration**: ~85 s
**Purpose**: Where the stamp lands, and the epoch structure everything later depends on.

#### Visual Elements
- **The epoch rail** comes alive as a hash chain in the block header. Each stamp is a bead absorbing an `acc^tg` chip and the epoch number: `anchor ← H(anchor_old ‖ i ‖ acc^tg)`. A granularity strip: finer than a block, coarser than a transaction.
- Sentinel gates appear at the epoch transitions: `sntl_i = H^epoch(anchor_{i−1,end} ‖ i)`. Every epoch, even an empty one, gets two authenticated boundaries.
- Our note's stamp lands as a bead inside epoch 5 and is marked.
- A split-screen cost card: validator-as-hasher (one hash per stamp) vs validator-as-accumulator (re-accumulate, interpolate, commit: an MSM gear grinding on the critical path of block validation).

#### Pause beats
1. *beads absorb accumulator chips along the rail*
2. *our bead lands in epoch five*

#### Content
- The anchor chain is a hash chain carried in the block header. It ticks once per stamp, absorbing the stamp's `acc^tg` with the current epoch number, so the chain moves at a granularity finer than a block but coarser than a transaction.
- At every epoch transition consensus appends one sentinel, a domain-separated hash of the old epoch's last anchor and the new epoch's number. Every epoch, even an empty one, gets two authenticated boundaries, and every canonical anchor belongs to exactly one epoch.
- Why per stamp, not per block? Validator work. A stamp's `acc^tg` is already checked cheaply against its published list, so the validator just hashes it in. A per-block anchor would make every validator re-accumulate every tachygram, interpolate, and commit (an MSM) on the critical path of block validation. The scene ends on that fact.

---

## Chapter 3 — Time passes: nullifiers that evolve (~7 min)

### Scene 3.1 — Why one nullifier per note has to go
**Duration**: ~90 s
**Purpose**: The privacy failure that forces evolving nullifiers.

#### Visual Elements
- Epochs 6 and 7 begin: the "now" cursor slides, and the wallet's proof token has to tick forward at every bead.
- The wallet hands its work to a cyan service, labeled "oblivious syncing service (OSS)".
- First version: the wallet gives the OSS `nf`. Later the same `nf` appears on chain, and a dotted flare line snaps from the service to the spend. Rewind: each epoch has its own value (`nf_6`, …, `nf_9`), and the line fails to connect.
- A banner, "1 note = 1 nullifier", cracks. Two IOU chips remain: "new derivation" and "new double-spend rule".

#### Pause beats
1. *the now-cursor slides, the proof token ticks at every bead*
2. *a flare line snaps from the service to the spend*
3. *rewind: per-epoch values, the line fails to connect*

#### Content
- Keeping the note spendable means keeping its exclusion proof current, because every stamp that lands is new history to cover. Nobody wants their wallet online for that, so the wallet hands the job to a service (Sean's name: an oblivious syncing service).
- To prove a nullifier absent, the service must know it, and whoever knows the nullifier recognizes the spend.
- The fix: the nullifier evolves, a different value per epoch. What the wallet shares for epoch 6 is unlinkable to what it reveals at the epoch-9 spend.
- This breaks the Zerocash-era invariant of one note, one globally unique nullifier. Tachyon now owes a new derivation (next scene) and a new double-spend rule (Ch. 6).

### Scene 3.2 — The derivation, and two nullifiers per spend
**Duration**: ~165 s
**Purpose**: The concrete KDF, the delegation shape, and the cross-epoch race that explains the empty pouch slot.

#### Visual Elements
- Ideal functionality card: `nf_e = KDF(nk, ψ, e)`, with three property chips (random-looking; binds authority and note; unlinkable across epochs without `nk`).
- A constrained-PRF key (GGM tree, the Goldreich–Goldwasser–Micali construction) is shown and set aside as circuit-expensive.
- The OSS receives grey opaque beads `(6, nf_6), (7, nf_7), (8, nf_8)`. A decoy list sits beside them, and the OSS cannot tell the two apart.
- A sponge with input `mk = Poseidon^mk(nk, ψ)` (the ψ slot on the note card pulses) squeezes 4 nullifiers per permutation onto the epoch rail: `nf_4 … nf_7` from one permutation, `nf_8 … nf_11` from the next. Then the notation `nf_e = f_mk(e)`.
- The race: a transaction in a mempool lane drifts toward the sentinel gate between `e` and `e+1`. A single-nullifier version shatters at the gate. The `(nf_e, nf_{e+1})` version passes.
- The pouch from 2.2: an output's second slot fills with a dummy tachygram (hash of random bytes). Spend and output become identical two-pip dominoes.

#### Pause beats
1. *the sponge squeezes four nullifiers per permutation onto the rail*
2. *a single-nullifier transaction shatters at the sentinel gate*
3. *spend and output become identical two-pip dominoes*

#### Content
- Ideal: a deterministic function of `nk`, ψ, and `e`, random-looking, binding both the spending authority and the note, unlinkable across epochs without `nk`.
- A constrained PRF would let the wallet delegate a key for a range of epochs, but the known candidate (built from a GGM tree) is expensive in a circuit. Tachyon takes the simpler route: the user derives and proves the nullifiers, and the service gets bare `(epoch, nullifier)` pairs with no evidence linking them to any note. A real sync request could just as well be a decoy list. Binding to the note happens later, on the wallet.
- Construction: `mk = Poseidon^mk(nk, ψ)`; one Poseidon permutation of `mk` squeezes a window of Rate nullifiers. With Rate 4, one permutation gives epochs 4–7, the next 8–11. From here on, `nf_e = f_mk(e)`.
- Security: any unrevealed nullifier stays indistinguishable from random. That one property carries balance, privacy against the sender (who made the note but never learns `nk`), and unlinkability across epochs, even under delegation.
- The race: a spend proving only `nf_e` waits in the mempool, the epoch ticks to `e+1`, and the proof is stale. Nobody else can refresh it: not the miner, and not the service, which never learns spend-time nullifiers. So every spend reveals `(nf_e, nf_{e+1})`.
- The empty slot: an output fills it with a dummy tachygram. Without padding, counting tachygrams against actions reveals the spend/output split. With it, every action carries exactly two.

### Scene 3.3 — The ranged nullifier commitment
**Duration**: ~175 s
**Purpose**: The first real math set piece. How the wallet will later prove that the OSS tested *its* nullifiers, index by index, without the OSS learning anything.

#### Visual Elements
- Two rails: wallet range `R = [4, 12)` above, OSS range `S = [6, 9)` below, with a containment bracket. Both sides build "a little at a time" across proof steps.
- A vector-commitment card (RSA / pairings) set aside as circuit-hostile; then a "proven-honest updates" chip: the commitment no longer defends against a malicious committer.
- Each `(i, nf_i)` bead crystallizes into a cubic-factor tile `F_{i,nf_i}(X) = ((i+1)X + nf_i)³ − c`. Tiles multiply into a growing stack (factor stacks, not curves), labeled "indexed multiset". The stack grows one tile at a time, and its right end stays open.
- Division: the OSS stack lifts out of the wallet stack, leaving the quotient `q`. A random probe `r` strikes all three, and the equality lights gold (Ragu query glyph).
- Soundness sidebar on the `F_13` clock: the cubes {1, 5, 8, 12} light, and 2 is not among them. Then the ω-collision is drawn and crossed out by the scale comparison: epochs below `2^32` against an enormous ω.
- Caution chip: "division proves inclusion, not order"; order and contiguity come from counters and sentinel endpoints.

#### Pause beats
1. (short `⟨pause⟩` before the encoding, after "opens up the design space".)
2. (short `⟨pause⟩` after the factor definition.)
3. *tiles stack one at a time, right end open*
4. *the service's stack lifts out of the wallet's, leaving q*
5. (short `⟨pause⟩` after "So why is this sound?")
6. *the thirteen-element clock: two is not a cube*

#### Content
- The need. The wallet derives over `R` (say 4 to 12). The service tested `S` (6, 7, 8) and committed to what it tested. The wallet must prove every pair the service tested is one it derived, at the same epoch index, and both sides build incrementally across many proof steps.
- A vector commitment would do it, but the known schemes with subvector openings live on RSA groups or pairings, which are unfriendly to our circuits. In a standard vector commitment the prover can commit to anything; here every update is proven correct against its running value, so honest committing is enforced by the proofs and the commitment needn't defend against a malicious committer. That opens up the design space.
- Encode each pair as a factor binding position and value: `((i+1)X + nf_i)³ − c`. Multiply over the range: a commitment to an **indexed multiset**, extended one factor at a time with no fixed endpoint.
- Containment is division: the wallet exhibits `q` with `g_R = g_S · q`. All three commitments are fixed before the challenge `r`, and the check is one identity at one point through Ragu's query part.
- Soundness. `p ≡ 1 mod 3`, so `c = 2` is a public non-cube, `Y³ − c` is irreducible, and so is every invertible affine substitution (`i + 1 ≠ 0`). In `F_13` the cubes are {1, 5, 8, 12}. With unique factorization, a forgery needs two different pairs with the same factor, which happens only when they differ by a nontrivial cube root of unity ω; epochs are below `2^32` and ω is an enormous field element, so that never happens.
- Caution: multiplication is commutative, so division proves inclusion, not order. Order and contiguity come from counters and from sentinel endpoints, checked as each side is built.

---

## Chapter 4 — Exclusion at scale: quadratic residue filters (~10 min) — *centerpiece*

### Scene 4.1 — The epoch accumulator, and the wall
**Duration**: ~85 s
**Purpose**: The naive exclusion and why it fails at scale. Set the target.

#### Visual Elements
- The task: our `nf_6` against all of epoch 6.
- Inside epoch 6 on the rail, the per-stamp polynomials zipper-multiply into one `e(X)`, proven against the anchor chain by random-point checks (Ragu query glyph, no step circuit). A "paid once, shared by every service" tag.
- The numbers card: 100 TPS, 2-in-2-out, two weeks → > 4.8 × 10⁸ tachygrams. A Bulletproofs-style IPA verifier, linear in the degree. The degree counter spins to 4.8 × 10⁸, and a verifier stopwatch runs past 16:00. The frame tints flare.
- Target card: non-membership over a whole epoch, sublinear amortized cost, no huge polynomial near the query.

#### Pause beats
1. *degree counter spins to 4.8 × 10⁸, stopwatch passes 16:00*

#### Content
- Testing every stamp's accumulator is wasteful. Union is multiplication, so multiply the epoch's stamp polynomials into one epoch accumulator `e(X)`, whose roots are every tachygram of the epoch, proven against the anchor chain with random-point checks. Those queries are served by Ragu's query part, folded into the proof system's own claims, not a step circuit, so `e(X)` may have as high a degree as the PCS allows. The work is linear, but paid once and shared by every service that needs it.
- Framing: `e(X)` is the strawman. Ragu can technically support a very high degree; Tachyon chooses bounded degree, and the numbers show why.
- The numbers (see the card): one verification would take more than 16 minutes.
- Target: epoch-wide non-membership at sublinear amortized cost, with no huge polynomial anywhere near the query.

### Scene 4.2 — Bucketing by an address the element computes itself
**Duration**: ~140 s
**Purpose**: The bucketing idea, and the number theory that makes the address cheap to prove (QR, the flip, discriminants, the −R convention).

#### Visual Elements
- `e(X)` shatters into a grid of small buckets. A query element computes a bit string over its head and homes in on exactly one bucket.
- A requirements card: computed from itself; splits sets evenly; cheap in a circuit → "quadratic residues".
- **The `F_13` clock**: 12 nonzero dots, half cyan (QR {1, 3, 4, 9, 10, 12}) and half amber (NQR). `y² = x` (one constraint). Multiplying by `c = 2` swaps the colors in place: the flip, `y² = c·x` (one constraint).
- Sliding the offset R recolors the ring ("QR discriminant"). A k-bit profile chip, `2^k` near-equal classes.
- The `x = −R` dot blinks white and is assigned to the residue side, with an "x + R ≠ 0" witness chip on the non-residue branch.

#### Pause beats
1. *e(X) shatters into buckets, a query homes in on one*
2. (short `⟨pause⟩` before the QR detour.)
3. *the clock: residues cyan, non-residues amber*
4. *multiplying by two swaps the colors*
5. *sliding R recolors the ring*

#### Content
- Split the epoch into buckets so a query looks in one. That works if the queried value can compute its own bucket from itself alone: then it belongs to exactly one bucket, and if it ever appeared in the epoch it is in there. Non-membership over the epoch becomes one opening against one small bucket.
- The address must be computed by the element itself, split sets evenly, and be cheap to prove. Quadratic residues are exactly that.
- Over a prime field, the nonzero elements split exactly in half: squares (QRs) and non-squares. Proving `x ∈ QR` is one constraint, `y² = x`. Proving `x ∈ NQR` uses the flip: multiplying by a non-square swaps the classes, so with a fixed public non-residue `c`, `y² = c·x` is one constraint.
- A **QR discriminant** asks the same question about `x + R`. One discriminant halves any fixed set; `k` of them give a `k`-bit **profile** and `2^k` near-equal classes, computed from `x` alone.
- Edge case: `x = −R` makes the shifted value zero. By convention it goes to the residue side, and that is enforced: a claimed non-residue bit needs a witness that `x + R ≠ 0`, or `−R` could take the non-residue branch with a square root of zero.

### Scene 4.3 — The batched QR test and one decomposition
**Duration**: ~120 s
**Purpose**: Certify a whole bucket's class with one identity, then split a bucket with four checks.

#### Visual Elements
- On the field line, roots `x_i` carry lifted square roots `y_i`. An interpolating curve `g` threads through them. `g(X)² − X` collapses onto `f · h`, the probe `r` strikes, and both sides print the same element.
- One bucket cleaves under a discriminant blade into `q₀` (amber, NQR) and `q₁` (cyan, QR). Four lamps light in turn, each with its identity: (1) `f = q₀ q₁`, (2) `q₁` all residues, (3) `q₀` all non-residues, (4) `q₀(−R) ≠ 0`. The `−R` dot is then forced into `q₁`.

#### Pause beats
1. (short `⟨pause⟩` after the interpolation of `g`.)
2. *both sides print the same element*
3. *the blade cleaves the bucket into amber and cyan*

#### Content
- Batched test: bucket accumulator `f = ∏(X − x_i)`, all roots squares. Consensus refuses duplicates, so the roots are distinct and we can interpolate `g` through `(x_i, y_i)`. Then `g² − X` vanishes on every member, `f` divides it, and the quotient `h` is the witness. The prover commits to `g` and `h`; the verifier checks `g(r)² − r = f(r)·h(r)`. One identity at one point certifies every root of `f` is a square. The non-residue version carries `c`; an offset replaces `X` by `X + R`.
- To split a bucket under `R`, break `f` into `q₀` (non-residues) and `q₁` (residues). Four checks at a random point: (1) decomposition, `f = q₀·q₁`, no root added or dropped; (2) every root of `q₁` is a residue; (3) every root of `q₀` is a non-residue; (4) `q₀(−R) ≠ 0`. Because `q₀` is a product of linear factors, (4) means `−R` isn't its root, and with (1), `−R`, if present, is forced into `q₁`.

### Scene 4.4 — Routing: decompose, merge, and a jagged frontier
**Duration**: ~170 s
**Purpose**: How an OSS builds full-epoch, bounded buckets in flight. The signature animation of the video.

#### Visual Elements
- The stream: stamps along epoch 6 roll into bounded **summaries** (each a product polynomial plus an anchor range), which become root buckets with an empty profile. A summary never crosses a sentinel.
- A routing round station: each bucket splits into amber and cyan, adjacent same-profile children merge when they fit, and an unmergeable child stays solo. Anchor ranges are drawn as brackets under each bucket: decomposition keeps the bracket, merge joins two adjacent brackets.
- A zoom-out shows the braided network across rounds, running in parallel and streaming while the epoch is live.
- Stragglers get partial rounds. The frontier edge is visibly jagged, and finished full-epoch buckets click onto a finish rail spanning `sntl_6 → sntl_7`. A seal step checks both sentinels.
- The proof-tree view of one split: a split step (product + `−R` check) with two descents, each returning one side and checking the other side's purity.
- Grinding: an attacker trying random tachygrams to pile into one bucket finds the discriminant dial hidden behind the OSS's glass until the epoch closes (`R₀` private, `R_{j+1} = R_j + 1`, revealed after).
- Scale card (on screen only): 50K TPS fits in a 32-bit profile.

#### Pause beats
1. *one routing round: split, then merge*
2. *zoom out over the braided network*
3. *finished buckets click onto the finish rail*

#### Content
- While epoch 6 is live, the service rolls consecutive stamps into bounded summaries (one product polynomial each, plus the anchor range covered), growing by a random-point check that the new product is the old one times the next stamp's accumulator, and absorbing that stamp into its anchor. A summary never crosses a sentinel; each becomes a root bucket with an empty profile.
- A routing round decomposes every bucket under the next discriminant (roughly halving each), then merges neighbors with the same profile whenever the union still fits. Merging is the union check again, nothing new to trust.
- Anchor ranges are tracked underneath: decomposition keeps a range, a merge joins two adjacent ranges. Round by round, partial pieces of a profile become one bucket spanning the whole epoch. Rounds run in parallel, stream, and run while the epoch is live.
- Stragglers get another, partial round. The result is a jagged frontier: final profiles at different depths that together partition the field, each covering the whole epoch from sentinel to sentinel. After the close, a seal step checks both sentinels.
- In the proof tree, each split is one step proving the product and the `−R` check, then two descents; each returns one side and checks the purity of the other, so once both children are derived both buckets are certified pure.
- Grinding (trying random values until enough land in one bucket to overload it): discriminants must stay unpredictable while tachygrams are chosen. Each service samples its first offset privately, steps it by one per round, and reveals it after the close. The choice affects balance, never soundness; a badly balanced routing can be ignored in favor of an honest service's.
- Scale, as an on-screen card (the narration says one sentence: even at 50K TPS, a 32-bit profile has room to spare). The card reads: 50K TPS × 8 tachygrams × 2 weeks < 4.84 × 10¹¹ tachygrams; < 6.1 × 10⁷ root buckets at 8,000 entries; k ≤ 26 within the 32-bit budget.

### Scene 4.5 — The evidence tree
**Duration**: ~85 s
**Purpose**: Compress the final buckets into one reusable certificate, and price the query.

#### Visual Elements
- Final buckets fold upward into an arity-4 Poseidon tree (matching the sponge's rate), and one root glows star-white over epoch 6 on the rail. Leaf contents: epoch, two sentinels, first discriminant, profile and depth, `Com(q_b)`. A one-leaf tree is shown valid too.
- Query: our `cm` in epoch 5 opens a bucket, zero, with no profile computed. Our `nf_6` re-derives the discriminants, its bits select a leaf, and the bucket is nonzero there.
- Cost cards: `e(X)`: 16 min linear verification → evidence tree: ≤ 13 hashes + one bounded opening.

#### Pause beats
1. *buckets fold into a rate-4 tree, a root glows over epoch six*

#### Content
- One proof per final bucket would be a lot to keep around. After the close, the service folds any set of final-bucket proofs into one **evidence tree**, a Poseidon Merkle tree of arity 4. Each leaf binds the epoch, both sentinels, the first discriminant, the profile and depth, and the bucket's commitment; the output is one root. Coverage isn't required: even a single leaf is valid, because each leaf is already a proven full-epoch bucket.
- Membership: authenticate a leaf, check the value is a root of its bucket. No profile needed, since every bucket divides the epoch's polynomial (that is how our `cm` is found in epoch 5). Non-membership: re-derive the discriminants, check the value's bits select this leaf, check the bucket is nonzero there (that is how our epoch-6 nullifier is cleared).
- The sixteen-minute linear verification became at most thirteen hashes plus one bounded opening. Routing ran once, in flight; building the tree is the only work left after the close.

---

## Chapter 5 — The proof tree: spending our notes (~6 min)

### Scene 5.1 — Steps, headers, bridges
**Duration**: ~75 s
**Purpose**: The PCD vocabulary and the role colors, set up quickly.

#### Visual Elements
- The three monolithic statements (Output, Spend, Bundle) flash as cards, then shatter into a tree of small steps.
- A generic step consumes two child headers plus a private witness and emits a header; headers flow upward.
- A parent loads both headers. Equality pins snap matching fields together (same `cm`, matching sentinels, same epoch), and a mismatched pin repels with a flare flash. A "sound ⇔ every shared field bridged" chip.
- Legend: gold = wallet steps (see the note), cyan = service steps (see opaque values), star-white = shared evidence (anchor chain segments for the active epoch, evidence trees for closed epochs).

#### Pause beats
1. *statement cards shatter into a tree of steps*

#### Content
- The scene opens directly on the statements (no bridge line). A spend, an output, and the bundle each have long statements; we break them into steps. A step is a bounded circuit: up to two child proofs plus private witness, checks part of the statement, emits a **header**, the "data" in proof-carrying data. Headers flow from children to parents.
- A parent **bridges** its children by checking that fields which must agree do agree. Breaking a statement into steps is sound exactly when every field two steps share gets bridged.
- Three colors from here on (see the legend).

### Scene 5.2 — Same-epoch spend: the base tree
**Duration**: ~115 s
**Purpose**: The simplest complete spend, and the important base case. It introduces the steps every spend shares (`SpendBind`, `OutputSeed`, `StampMerge`, `StampLift`), so the past-epoch tree in 5.3 only adds what is new.

#### Visual Elements
- Now = 9. The wallet holds a second note, **note₉**, received earlier in epoch 9. Its creation bead sits inside epoch 9 on the rail. A "nothing to exclude" chip.
- The tree grows node by node, bottom-up: `SpendableInit → NoteSpendable{cm, 9, anchor}` (cached; a hardware wallet can take it early) → `SpendBind → Stamp`. `OutputSeed → Stamp` comes in from the side for an output. `StampMerge` joins them. `StampLift` slides the merged stamp along a star-white anchor chain segment and bounces off the 9|10 sentinel gate.
- A checklist beside the tree ticks each clause of the monolithic Spend/Output statements as the step that covers it lights.
- A small unlinkability beat: without the lift, the stamp's anchor points straight at the note's creation bead.

#### Pause beats
1. *the full base tree, checklist complete*

#### Content
- Epoch 9; the wallet also received a note earlier in this epoch. Spending a note in its creation epoch needs no exclusion proof, since it didn't exist before.
- `SpendableInit` takes the creation stamp's data as witness, proves `cm` is a root of that stamp's accumulator, and computes that stamp's anchor. Its header says "spendable", with commitment, epoch, and anchor. The wallet can build it once the creation block is final, cache it, or hand it to a hardware wallet early.
- `SpendBind` opens the note and checks the spend statement: `pk` matches `ak` and `nk`, `cm` recomputes, the value is in range, `rk` is bound through α, and the nullifiers for 9 and 10 are derived. It emits a stamp for this one action. `OutputSeed` covers the whole output statement in one step. `StampMerge` joins stamps by multiplying their accumulators.
- `StampLift` consumes a shared anchor chain segment and moves the stamp to a later anchor. The segment contains no sentinel, so a lift can't cross an epoch. The lift is part of what keeps the spend unlinkable: without it, the anchor would point at the note's creation.
- Every spend ends with `SpendBind`, merge, and lift. For an older note, the only thing that changes is what feeds `SpendBind` (stated as a fact, not a question).

### Scene 5.3 — Past-epoch spend: note₅
**Duration**: ~180 s
**Purpose**: The full past-epoch tree, built over the running example. Only the part under `SpendBind` is new. This is where the Ch. 3 promise is paid.

#### Visual Elements
- Opening: note₅'s card pulses; the rail lights its three parts: epoch 5 (inclusion, wallet only), epochs 6–8 (delegated), epoch 9 (spend). The 5.2 tree is shrunk to the side and stays legible.
- **Branch A (gold, epoch 5)**: two openings of epoch 5's evidence tree, one for `cm` and one for `nf_5`. `NoteUnspentInit` → `Unspent{cm, 5, 6, sntl_5, sntl_6}`; `SpendableReinit` → `NoteSpendable{cm, 6, sntl_6}`, which glows.
- **Branch B (cyan, epochs 6–8)**: `UnspentSeed` (empty range, `g = 1`), then a **ratchet**. Each `UnspentLift` consumes one evidence-tree opening, proves one opaque nullifier absent, appends one cubic tile, and clicks the pawl forward one sentinel. A skip attempt jams the pawl.
- **Branch C (gold, local)**: `NoteSeed → NoteMaster{cm, mk}`; two `NullifierDerive` windows `[4, 8)` and `[8, 12)`; `NullifierFuse → NoteNullifiers{cm, 4, 12, Com(g_R)}`.
- `UnspentBind` replays the Ch. 3 division in context: the service stack `[6, 9)` lifts out of the wallet stack `[4, 12)`. Then `SpendableLift` joins `NoteSpendable{cm, 6, sntl_6}` with `Unspent{cm, 6, 9, …}` (sentinels matched where the two meet) → `NoteSpendable{cm, 9, sntl_9}`.
- The join: that header feeds the *same* `SpendBind` as in 5.2, which derives note₅'s `(nf_9, nf_10)` → `Stamp`. The docked 5.2 tree slides back in. `StampMerge` combines note₅'s stamp with note₉'s spend and the outputs, and one `StampLift` moves the result to the transaction's target anchor inside epoch 9. Result: one stamp, two spends, two outputs.
- A short side beat: two services' ranges joined by `UnspentMerge` (end sentinel = start sentinel).
- Closing privacy card: what a service sees (opaque values, ranges indistinguishable from decoys) vs never sees (`cm`, the note, another service's work, where the spend lands).

#### Pause beats
1. *the spendable header glows*
2. *a skip attempt jams the ratchet*
3. *the service's stack lifts out of the wallet's*
4. *the full tree: one stamp, two spends, two outputs*

#### Content
- Opens on the fact: note₅ was born in epoch 5 and is spent in epoch 9, so its history splits into three parts.
- The birth epoch stays on the wallet, because there the wallet must show both that the note exists and that it wasn't already spent. It opens epoch 5's evidence tree twice (nullifier bucket, commitment bucket). `NoteUnspentInit` re-derives the nullifier, checks its profile selects the bucket, and proves it absent; `SpendableReinit` joins that with the membership opening for the same epoch and sentinels. Out comes a spendable header valid from the start of epoch 6.
- Epochs 6–8 are where delegation pays off. Service side: `UnspentSeed`, then one `UnspentLift` per epoch (one opening, one absence proof, one cubic factor, one sentinel advance), unable to skip, repeat, or reorder; the service never learns which note this is. Wallet side: `NoteSeed` emits the master key header; each `NullifierDerive` squeezes one window (4–8, 8–12); `NullifierFuse` joins them over 4–12.
- The join: `UnspentBind` checks the service's range is nonempty and inside the wallet's, then runs the division, which turns delegated, note-independent work into work about this note. `SpendableLift` joins the result onto the spendable header, checking that sentinels match where they meet. The note is now spendable through the start of epoch 9.
- From there it is the simple spend: `SpendBind` derives nullifiers for 9 and 10, `StampMerge` joins this stamp with the other spend and the outputs, one `StampLift` moves everything to the target anchor in epoch 9.
- Several services for different ranges: `UnspentMerge` joins adjacent results before binding, with one's end sentinel equal to the other's start.
- What a service learns: only opaque values and ranges it can't tell from decoys. Never the commitment, the note, another service's work, or where the spend lands.

#### Narration Notes
This is the longest scene, so pace it in three movements (branch A, branches B+C, the join with note₉'s tree). Each movement ends with its header glowing. "Branch A" etc. are visual labels only; the narration speaks of the birth epoch, the service side, and the wallet side.

---

## Chapter 6 — Landing: consensus and aggregation (~7.5 min)

### Scene 6.1 — The validator and the two-epoch window
**Duration**: ~170 s
**Purpose**: The new double-spend rule, told through the grace-period attack, and why two nullifiers plus a two-epoch window close it.

#### Visual Elements
- The validator checklist (4 items) ticks: target anchor canonical with epoch current or previous; `acc^act` matches the actions; `acc^tg` matches the published list (random-point check); one proof verifies. A footnote chip: balance and signatures as in Orchard.
- A timeline (redrawn from `consensus_window.svg`): the stamp's exclusion claim runs up to `sntl_9`; the target anchor is *not* an exclusion endpoint; duplicates inside epoch 9 are consensus's job.
- The two-epoch duplicate window (current + preceding epoch), with check-then-insert ordering.
- The attack: two spends of the same note. Spend 1 targets epoch 9 and is held until epoch 10; spend 2 targets epoch 10. Both proofs are honest. With single nullifiers nothing collides; with adjacent pairs the tokens collide on 10.
- The attacker pushes spend 2 to epoch 11: the colliding values land in epochs 10 and 11, and the sliding window still holds both and catches it.
- Callback: the hot grid from 0.1 returns, now two epochs wide, shown to scale next to the original monster.

#### Pause beats
1. *the two spends' tokens collide on ten*
2. *the window slides and catches the collision*
3. *the two-epoch grid beside the original from the prologue*

#### Content
- For each stamp, a validator does four checks (see the checklist). Balance and signatures work as in Orchard.
- Scope: a stamp proves exclusion strictly before the target epoch, up to the sentinel that opens it. The target anchor is not an exclusion endpoint, so every spend targeting epoch 9 must publish its nullifier for 9.
- The rule: one duplicate window holding every tachygram from the current and the preceding epoch; candidates processed in a fixed order, each checked, then inserted.
- Why that shape: the grace period (a stamp targeting 9 is still accepted during 10) admits the attack above. Publishing only the own-epoch nullifier lets the two spends reveal 9 and 10 with no collision. Publishing the adjacent pair makes them collide on 10. Delaying further puts the colliding values in 10 and 11, which the two-epoch window still holds. Anything older is inside history the stamp already proves excluded.
- Together, the adjacent pair and the two-epoch window close the gap the grace period opened, and consensus holds two epochs of tachygrams instead of all of history.

### Scene 6.2 — Aggregation: from many stamps to one
**Duration**: ~130 s
**Purpose**: Walk the aggregation life cycle from the ZIP (`draft-tachyon-aggregation-protocol`) using only steps the audience already knows (`StampLift`, `StampMerge`), and repay the 2.2 debt: *why* the stamp lives in authorization data.

#### Visual Elements
- **Standalone bundles arrive.** Transaction cards stream into a mempool lane, each carrying its own stamp slab (the 2.2 stamp card, small) at a *different* anchor tick on the epoch rail. The slabs are visibly heavy compared to the card body. Labels: "standalone bundle" vs, later, "aggregate bundle".
- **Who aggregates.** A miner glyph (neutral `#c8c4bf` outline, no new role color) with an "incentive: more transactions, more fees" chip; a faint relay network behind it, then dimmed ("anyone can aggregate; here, only the miner").
- **The lift.** Every stamp slides along a star-white anchor chain segment to one common tick inside the same spending epoch, all in parallel, and bounces off the sentinel gate if pushed across it (callback to 5.2).
- **The merge tree.** Stamps pair up. Each pair fuses with `StampMerge` into one slab (accumulators multiply, tachygram pouches union, proofs fuse), then the results pair, up a binary tree to one star-white aggregate slab. A one-frame inset: two overlapping pouches try to merge and the duplicate tachygram flashes flare and the slab refuses to form.
- **Assembly.** The 2.2 txid / wtxid diagram returns. Each covered transaction's stamp slab *drops* away (the word lands on "drops") and a thin pointer to the aggregate's `wtxid` *points at* it (lands on "points at"). The `txid` field stays lit, the `wtxid` field flickers. The signature seals do not move.
- **Validation.** A three-lamp checklist (tachygrams distinct, coverage matches, one *aggregated* proof verifies) lights in turn. The last lamp sits beside a single slab.

#### Pause beats
1. *standalone bundles stream into the mempool, each with its own stamp*
2. *stamps slide to a common anchor*
3. *the merge tree folds up to a single stamp*
4. *each transaction swaps its stamp for a reference*

#### Content
- So far every transaction has been a *standalone bundle*, one with its own stamp. Aggregation turns many standalone bundles into one *aggregate bundle* with a single stamp.
- The life cycle: wallets publish standalone bundles; an aggregator picks some and combines them. In the full protocol anyone can aggregate, and aggregates can be relayed and merged again. The miner has the strongest incentive (every proof byte saved is room for more transactions, thus more fees), so here the miner is the only aggregator. The ZIP explicitly allows a miner to aggregate privately during block assembly.
- The lift: stamps target different anchors, so the miner lifts each to one common anchor inside the same spending epoch, never across a sentinel, with the same `StampLift` step. No lift depends on another, so they run in parallel.
- The merge: `StampMerge` takes two stamps and returns one (unions the tachygrams, multiplies the accumulators, fuses the proofs), up a binary tree to one stamp. Overlap needs no rule: consensus refuses duplicate tachygrams, so a merge of overlapping sets could never land.
- Assembly: the block carries the aggregate plus every covered transaction; each covered transaction drops its own stamp and points at the aggregate's `wtxid`. This is why the stamp lives in authorization data: swapping it changes the witness ID, never the `txid`, so every signature stays valid.
- Validation: tachygrams distinct, the aggregate's coverage matches the transactions pointing at it, and one aggregated proof verifies.

#### Narration Notes
- Calm, procedural. This is a pipeline, so let the diagram carry it and hold a beat on each stage (the four held pauses above).
- Do not name `hStampActionsTachyon`, adjuncts, or `tachyonAggregateId` on screen. Those belong in the ZIP.

#### Technical Notes
- Reuse the 5.2 `StampLift` and `StampMerge` animations at small scale. Build the merge tree from `VGroup` rows of slabs with `ReplacementTransform` pairs per level, and keep the level index as a `ValueTracker` so 6.3's depth counter attaches to the same mobject.
- Rebuild the 2.2 txid / wtxid diagram from the shared builder rather than re-deriving it.
- Keep the stamp slabs the same size as in 2.2, and scale the whole group down together, so the audience recognizes them.

### Scene 6.3 — What aggregation buys
**Duration**: ~140 s
**Purpose**: Put the amortized cost of aggregation into perspective with first-order numbers for latency and size. The conclusion matters more than the arithmetic, so the screen carries cards, not a spreadsheet.

#### Visual Elements
- **Latency card.** The merge tree from 6.2 reappears with a depth counter beside it: "lift (1) + merges (log₂ N)". Doubling N adds one level. A "1.2 s / step, consumer laptop" chip.
- **Block-time card.** A 25 s block timeline labeled "after NU7": 4 s reserved for data transmission and node logic unrelated to the block proposal | 21 s for aggregation (highlighted) = 17 steps = 1 lift + 16 merge levels. The merge tree grows to sixteen levels; a counter reads 2¹⁶ = 65,536 transactions, ~2,600 per second, one miner.
- **Size card.** A transaction body broken into its parts (8 tachygrams, 4 `(rk, cv)` actions, 4 × 64 B action signatures, the binding signature, the encrypted memo, the pointer to the covering stamp) → ~1.15 KB, beside a 7.4 KB proof slab. Two 2 MB block bars, drawn to scale. *Without aggregation*: ~230 transaction slabs, each with a proof slab more than six times its own body. *With aggregation*: one proof slab at the front and ~1,700 thin slabs behind it (~70/s). A counter beside the second bar: "proof per tx: 7.4 KB → ~4 B".
- **Scale-up card.** "Size, not proving, is the ceiling." The aggregated bar stretches to 20 MB (~17K transactions, ~700/s). The step counter reads 16, and a stopwatch runs 16 × 1.2 s = 19.2 s, finishing inside the 21 s window.
- **Close.** One proof slab per block alone on screen; its per-transaction share shrinking as the bar grows.

#### Pause beats
1. *a depth counter beside the merge tree*
2. *the merge tree grows to sixteen levels*
3. *a block bar, proof share against payload*
4. *block bar grows, seven hundred per second*

#### Content
- **Simplification, carried over from 6.2.** Wallets send standalone bundles, and the miner aggregates alone.
- **Latency.** All lifts are independent, so with enough cores they cost one proving step. The merges form a binary tree, so N stamps add ⌈log₂ N⌉ steps; doubling traffic costs one more step. A step is ~1.2 s on a consumer laptop today (measured locally, multicore on; the unoptimized figure in Ragu PR #873 was ~2 s). After NU7 the block time is 25 s; reserving 4 s for data transmission and node logic unrelated to proposing the block leaves 21 s: 21 / 1.2 ≈ 17 steps, 1 lift + 16 merge levels, up to 2¹⁶ = 65,536 stamps per block (~2.6K per second) from a single miner.
- **Size.** A compressed proof is ~7.4 KB (Ragu PR #462 after the revdot optimization). A 2-in, 2-out aggregated transaction is ~1.15 KB: 8 tachygrams × 32 B = 256 B; 4 actions × (cv, rk) × 32 B = 256 B; 4 action signatures × 64 B = 256 B; the 64 B binding signature; ~256 B of symmetric AEAD ciphertext; the ~32 B pointer to the aggregate stamp; plus small fields. Alone, a transaction swaps the pointer for its own 7.4 KB stamp, a proof more than 6× its own size: 2,000,000 / ~8,520 ≈ 235 per 2 MB block (narrated as "about two hundred and thirty"). Aggregated, the block carries one proof: (2,000,000 − 7,400) / 1,150 ≈ 1,733 per block (~69 per second), ~7× more, and each transaction's share of the proof falls to ~4.3 B.
- **Scale-up.** Size is the ceiling, not proving, so raise the limit to 20 MB: (20,000,000 − 7,400) / 1,150 ≈ 17,385 transactions, ~695 per second at 25 s blocks. Covering 17K takes 1 lift + 15 merges = 16 steps (2¹⁵ = 32,768 ≥ 17,385), 16 × 1.2 s = 19.2 s ≤ 21 s. The 2 MB block (~1,733 tx) needs only 1 + 11 = 12 steps, 14.4 s.
- **Bottom line.** One proof per block. Its share of each transaction shrinks as traffic grows, so proof size stops being the bottleneck. What remains is delivering the notes.

#### Narration Notes
- The scene opens by saying what it is for ("to put the amortized cost of aggregation into perspective"). Do not read the derivations. State each result once, with the animation showing the inputs. Never say "first-order" or hedge more than the single "unoptimized" caveat.
- The ML-KEM first-contact ciphertext (~2 KB) is deliberately omitted from the ~1.15 KB (it would dominate block space). If a viewer asks, it is a payment-protocol cost, and it is the reason a larger block limit is on the table at all. This stays out of the narration.

#### Technical Notes
- The size bars are `Rectangle`s sized by a single scale constant, with the slab counts drawn from the numbers above (235 and 1,733). Draw only a sample of slabs and let the rest be a texture fill, and keep the counters as `DecimalNumber` with `ChangeDecimalToValue`.
- Keep the numbers in one `numbers.py` in the shared style module so the narration, the cards and the checks can't drift apart. The derivations above are the source of truth, and an assert in that module should recompute them.
- Not modelled, and absent from the budget: the time to *compress* the final aggregate. Flag it in a code comment, not on screen.

---

## Chapter 7 — The other half: the payment protocol (~2 min)

### Scene 7.1 — Addresses, tags, and private retrieval
**Duration**: ~115 s
**Purpose**: Close the Ch. 1 loop, briefly: what replaces Orchard's transmission key, and how a wallet finds its notes and builds its witnesses. This is a sketch of ValarGroup's design, not a deep dive.

#### Visual Elements
- Opening card: "delivering notes = payment protocol", with a ValarGroup credit.
- An address card `addr = (pk, ek)` with an "ML-KEM: NIST post-quantum key encapsulation" gloss and two freshness dials: `ek` per sender, tag per note.
- A quantum lens over `[ivk]G_d`: one recovered `ivk` opens every incoming note, past and future.
- A tag chain: `tag₀ = H(ek)` (first contact) glows differently from `tag_i = H(K, i)` (shared secret + counter).
- PIR as a black box: one silent hand fetches entries from a server that can't see which ones it asked for. The tachygram database wires back into the Ch. 5 tree (stamp and anchor data for the spend proof).
- Faerie gold: two incoming notes with a reused ψ collide at the reference-epoch nullifier, and the wallet keeps one.

#### Pause beats
1. *a quantum lens over i-v-k opens every note*

#### Content
- Delivering notes is the payment protocol's job; the leading design is ValarGroup's, sketched here. (No "the cut we made" callback.)
- `addr = (pk, ek)`: the payment key plus an ML-KEM encapsulation key (the NIST post-quantum KEM standard), both fresh per sender.
- Why not diversify? `[ivk]G_d` is not quantum-private: break one discrete log, recover `ivk`, and every incoming note, past and future, is exposed. ML-KEM has no analogue of many unlinkable keys sharing one decryption key.
- Tags restore cheap discovery. First contact: `tag₀ = H(ek)`, so the recipient finds the handshake before knowing the shared secret. Later: `tag_i = H(K, i)`, predictable to the two parties, opaque to everyone else, fresh per note because tags appear on chain.
- Trial decryption is replaced by private information retrieval of tags (the server never learns which entries were fetched). The same machinery includes a tachygram database that privately supplies the stamp and anchor data the spend proof needs.
- Faerie gold, as promised in Ch. 1. Notes have no canonical position, so the shielded protocol can't bind ψ the way Orchard binds ρ; the wallet checks each incoming note's nullifier at a fixed reference epoch against the notes it holds, and a reused ψ collides there.
- Dropped for time (the spec covers them): the KEM ciphertext size and first-contact shape, the PKI DB, and AEAD state recovery.

---

## Chapter 8 — Quantum posture, and the cascade (~3.5 min)

### Scene 8.1 — Private today, sound after an upgrade
**Duration**: ~130 s

#### Visual Elements
- An asymmetry card: privacy must hold retroactively (harvest now, decrypt later) vs soundness only at spend time (wait for a coordinated upgrade).
- The audit table (v1 act8 style): owner fields and note commitments (Poseidon), nullifiers (PRF outputs), memos (ML-KEM + symmetric) are already quantum-safe; value commitments, randomized keys, and the binding key rest on discrete log.
- The quantum lens: `cv` stays opaque (perfectly hiding). `rk` resolves to `ask + α` (`ask` labeled "secret key behind `ak`"), but α pixelates the link.
- A two-row upgrade card: a signature seal becomes a proof node (in-circuit proof of a PQ signature, CAPSS-style; `rk` leaves the action; the note-to-action binding becomes an explicit constraint), and a DL block becomes a lattice block (lattice-based folding; recursive structure kept; "active research" tag).

#### Pause beats
1. *the quantum lens: alpha pixelates the link*

#### Content
- Tachyon's stance is private today and sound after an upgrade, deliberately asymmetric. Privacy must hold retroactively because today's chain can be harvested now and decrypted when the hardware arrives. Soundness (nobody forges, nobody steals) only matters at spend time, so it can wait for a coordinated network upgrade.
- Audit: owner fields and commitments are Poseidon, nullifiers PRF outputs, memos ML-KEM plus symmetric encryption, so all already quantum-safe. Left on discrete log: value commitments, randomized keys, the binding key. The value commitment is perfectly hiding. A quantum computer can take `rk`'s discrete log and recover `ask + α`, but α is a fresh PRF mask, so it gets a random-looking scalar that links to nothing. The full power of a quantum computer against today's Tachyon is forgery, the half that can wait.
- The upgrade has two swaps. Authorization: re-randomization is intrinsically discrete-log and no PQ signature does it, so unlinkability comes from zero knowledge, proving in circuit knowledge of a valid PQ signature (schemes like CAPSS are built for that). Authorization folds into the PCD proof, `rk` leaves the action description, and the α binding becomes an explicit constraint. The proof system: Ragu's DL commitments swap for lattice-based folding; the recursive structure survives and only the hardness assumption changes. Concrete lattice constructions are still active research.

### Scene 8.2 — Outro: the cascade
**Duration**: ~70 s

#### Visual Elements
- The camera pulls back over the whole rail. Our note's journey (birth bead, delegated ratchet, evidence roots, spend) is visible at once.
- The cascade replays as a chain of chapter cards, each one lighting as its line is spoken, then the cards reconnect into one dependency chain.
- Close: "the client proves, consensus checks", then the links card (Deep Dive at tachyon.z.cash, Sean's blog posts, the Ragu book, GitHub).

#### Pause beats
1. *the camera pulls back over the note's whole journey* (opens the scene, before any speech)
2. *chapter cards reconnect into one chain*

#### Content
- Run backward: the nullifier set couldn't be pruned, so validation moved to the client. Clients can't sync alone, so syncing was delegated. Delegation would leak the spend, so nullifiers evolve. Evolving nullifiers would go stale in the mempool, so actions carry a pair and consensus keeps a two-epoch window. Per-stamp history needed composing, so one accumulator, with union by multiplication. Its degree exploded, so quadratic residues bucket each epoch. And none of it is affordable alone, so the expensive evidence is built once, proven once, and shared by everyone.
- Each decision is forced by the one before it, and all follow from one principle: the client proves, and consensus checks.
- Pointers: the Deep Dive at tachyon.z.cash, Sean's blog posts, the Ragu book, and the open implementation on GitHub (links below the video).

---

## Transitions & Flow

- **Persistent spine.** The note card is docked top-left from 0.2 onward and pulses when its fields matter (ψ in 1.3 and 3.2, `cm` in 2.2 and 5.3). The epoch rail sits along the bottom from 0.2 onward; "now" advances 5 → 9 over Ch. 3–5. The field line appears in 2.1 and returns in 3.3, 4.3, and 4.5. (Round 3 removed the docked card from Ch. 2–5 scenes where it crowds the stage.)
- **Visual debts, repaid**: the empty pouch slot (2.2 → 3.2), the word "sentinel" (3.3 → 4.4/5.3), the shared spend steps (5.2 → 5.3), distinct roots (2.1 → 4.3), Faerie gold and `ivk` unlinkability (1.2 → 7.1), the hot grid (0.1 → 6.1), the txid / wtxid split and *authorization data* (2.2 → 6.2), the unprunable-set wall (0.1) answered with per-block numbers (6.3).
- **Chapter boundaries end on a fact, not a spoken question** (narration rule 5). The visual handoff carries the continuity: the last frame of each chapter is the first frame of the next, via final-state builders.
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
`anchor ← H(anchor_old ‖ i ‖ acc^tg)`, `sntl_i = H^epoch(anchor_{i−1,end} ‖ i)`,
`mk = Poseidon^mk(nk, ψ)`, `nf_e = Poseidon^nf.Permute(mk, ⌊e/Rate⌋)[e mod Rate]`, `nf_e = f_mk(e)`,
`F_{i,nf_i}(X) = ((i+1)X + nf_i)³ − c`, `g_R = g_S · q`, `(a₁X + b₁)³ = (a₂X + b₂)³ ⇔ (a₁,b₁) = ω(a₂,b₂)`,
`y² = x`, `y² = c·x`, `g(r)² − (r + R) = f(r)·h(r)`, `f = q₀ q₁`, `q₀(−R) ≠ 0`, `R_{j+1} = R_j + 1`,
`p'(r) = p(r)·a_T(r)`, `addr = (pk, ek)`, `tag₀ = H(ek)`, `tag_i = H(K, i)`, `rk ↦ ask + α`, `2¹⁶ = 65,536`.

## Technical Notes (whole video)

- **Engine**: ManimGL (3b1b) in `v2/.venv`, scenes as `TimedScene` subclasses, following `/manimgl-best-practices`. One file per chapter in `v2/scenes/`.
- **Math typesetting: typst (decided 2026-10-04 after a failed `Tex` smoke test).** With `dvisvgm` installed, native `Tex` still fails with the texlive subset on this machine. manimgl hard-codes `\documentclass[preview]{standalone}` (no `standalone.cls`). The default template needs ~12 absent packages (`amssymb`, `babel`, `physics`, …). A hand-rolled `article` template still fails: the CM Type1 `.pfb` outlines and Metafont `mf` are missing (so no glyph paths, and `cmex7` can't even be generated), and dvips's `tex.pro`/`color.pro` headers are missing (so `xcolor` breaks dvisvgm). Following Alex's rule (no full texlive), v2 renders math with typst → SVG in New Computer Modern (Math). That keeps the CM look. Per-part coloring and matching transforms are built by composing separately typeset pieces.
- **Audio sync**: per-scene clips with word-level timestamps; beats anchored to spoken words, never hand-timed. Every held `⟨pause: label⟩` is a silent gap in the audio, and the visual event named here plays inside it.
- **Output layout**: `v2/scenes/` (code), `v2/audio/` (narration), `v2/renders/` (silent scene renders), `v2/video/` (muxed chapters and final cut).

## Implementation Order

1. Shared style module: palette, the note card, the epoch rail, the field line, the `F_13` clock, the Ragu black-box glyph.
2. Ch. 2 + Ch. 3 first. They define the spine objects every later chapter reuses.
3. Ch. 4 (centerpiece; the longest build).
4. Ch. 5 (reuses the Ch. 3–4 objects).
5. Ch. 0, 1, 6, 7, 8.
6. Assembly.

(Most of this exists in `v2/scenes/`; the Draft 2 narration now drives a re-sync pass rather than a fresh build. New: 6.3.)

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

None open on flow. Narration: `NARRATION.md` Draft 2 (Sean's voice, rules 1–5).

### Round 3 (2026-10-04, Alex's review of the full cut)

- Ch1: horizontal split kept. The DA-layer chain sits in the shielded band, and the encrypted payload originates in the payment band.
- Notation: the accumulators are `acc^act` and `acc^tg` everywhere (replacing actacc/tgacc). Header name: `Unspent` (replacing ArbitraryUnspent).
- Ch2: the anchor chain is cut to 4 stamp ticks with slower absorption. Ch2–4: no docked note card, and titles are centered.
- Ch3: the F-factor expansion and g_R stay on screen together.
- Ch4: the split/merge routing mechanic follows v1 act5 Scene54 (demo/act5.mp4 from 5:12).
- Ch5: note₅'s dot is hidden while note₉ is discussed. The StampLift "anchor" marker never passes "now". The docked notes are removed.
- Ch6: a stamp is drawn as actions carrying 2 tachygrams each. 6.1 is re-narrated around the grace-period double-spend attack (the pair plus the two-epoch window come as a set); the two-case walk-through was dropped. 6.2 aggregation is redrawn.
- Ch8: replaced by v1's 8.1/8.2 text and act8 animation (audit table, cascade), with audio regenerated in v2's voice.

### Round 4 (2026-10-05, aggregation expanded)

- Ch6: aggregation grows from one breath (old 6.2) into two scenes. 6.2 walks the life cycle from the ZIP with the miner as sole aggregator. 6.3 is the cost story (latency and size), chosen over the p2p-relay route because it answers the prologue's scaling wall; relay details (coverage digests, adjuncts, overlap handling) stay in the ZIP.
- Numbers: the PCD step takes 1.2 s (Alex's local multicore benchmark; the earlier 2 s figure from Ragu PR #873 would allow only 10 steps, 1 lift + 9 merges = 512 stamps). At 1.2 s, the 20 s window allows 16 steps (1 lift + 15 merge levels): 2¹⁵ = 32,768 stamps, ~1.3K per second. Size is the binding ceiling. Size figures: 7.4 KB proof, ~770 B per transaction, ~245 → ~2,594 transactions per 2 MB block, ~26K at 20 MB (~1K/s).
- Revised (2026-10-08, Alex): reserve 4 s, so 21 s and 17 steps (1 lift + 16 merge levels), 2¹⁶ = 65,536 stamps, ~2.6K per second. Per Alex's slides, a transaction also carries four 64 B action signatures, the binding signature and the pointer to the aggregate stamp, which puts it nearer 1.15 KB than 768 B: ~235 → ~1,733 per 2 MB block (~70/s), ~17K at 20 MB (~700/s). Size is the binding ceiling by a wider margin.
- Open: the compression time for the final aggregate is not in the budget.

### Round 5 (2026-10-08, full sync to NARRATION Draft 2)

- Synced every scene to `NARRATION.md` Draft 2 (Sean's voice, plus Alex's rule 5 pass: no narrator bridges, mechanism over metaphor, terms defined at first use). Each scene now lists its **Pause beats**, one per narration `⟨pause⟩`, in order, so animation anchors can be checked against the script.
- Removed stale material: the 0.1 "disk slab" (the commitment tree now prunes to its frontier, logarithmic state); spoken chapter-ending questions ("Where does `cm` go?", "Now the clock moves.", 5.2's closing question); the "cut along that line" framing (1.2 is now "separating authorization from transmission"); the 6.1 two-case acceptance walk-through (replaced by the grace-period attack, per round 3).
- Added visual targets for newly glossed terms: α as the randomizer (1.1); Faerie gold (1.2); succinct *and* quantum-recoverable (1.2); accumulator as a short commitment (2.1); *effecting data* / *authorization data* (2.2); GGM (3.2); grinding (4.4); *drops* / *points at* and the *aggregated* proof (6.2); NU7 and the consumer laptop (6.3); ML-KEM and PIR glosses (7.1); `ask` as the secret key behind `ak` (8.1).
- 6.3 size story corrected to ~1.15 KB per transaction (~230 → ~1,700 per 2 MB block, ~70/s; ~17K at 20 MB, ~700/s) and latency to 21 s / 17 steps / 2¹⁶.
- Durations re-estimated from the Draft 2 word count (~50 min total; Ch. 4 ~10 min). Audio is moving to Brian with Sean's prosody (speech-to-speech), one clip per scene.

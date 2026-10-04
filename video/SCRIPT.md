# Scaling Zcash with Tachyon — Staged Video Script (Draft 3)

**Title:** *Scaling Zcash with Tachyon*
(alt, if we want the core insight in the title: *Tachyon: Scaling Zcash with Prunable Nullifiers*)
**Format:** one video, ~38–42 min at ~150 wpm. Acts serve as chapter markers, not episode cuts.
**Style:** 3Blue1Brown-grade visual explainer (manimgl), ElevenLabs narration.
**Audience:** Zcash engineers fluent in Orchard *and* Sapling internals. Strong math maturity. No "what is Zcash" padding. Sapling/Orchard are the diff baselines throughout: they did X, Tachyon does Y, and here is the forcing function.
**Authoritative source:** `book/src/revisit.md`. Ragu internals are out of scope. Folding, PCD recursion, and online polynomial oracle queries are black-box capabilities. Act 0 states the interface once, and the rest of the video uses it.
**Terminology:** `QrBucketTree` is renamed **evidence tree** (`EvidenceTree`, PR #223). The script uses "evidence tree" everywhere and avoids pinning tree-step names that are still churning in that PR. Bucket/routing step names from revisit.md are unaffected.

### Visual design system (brand-aligned)

Source: `~/work/tachyon-website/sass/_variables.scss`; logos in `video/assets/brand/`.

- **Background:** deep space (`--bg-void #000001` / `--bg-deep #020204`). Matches manim's native black; subtle star field (`--star-white rgba(255,250,240,.7)`) permitted in title/transition cards only, never behind math.
- **Core palette:** gold `#D4A017` (primary accent), amber `#E8820C` (secondary), flare `#FF6B00` (hot/alert/cost-explosion), cyan `#4A9EA0` (cool accent). Text: `#c8c4bf` primary, `#9a958a` secondary.
- **Role mapping** (replaces the spec diagrams' blue/red/green convention — the video does NOT reuse spec colors): **wallet/user = gold**, **OSS/service = cyan**, **shared evidence = warm star-white**, **danger/hot/stale = flare**. QR classes: residue = cyan, non-residue = amber.
- **Logo:** the T-in-broken-ring mark opens and closes the video; its gradient (flare→gold) is the only gradient in use.
- **Fonts:** NOT the website's system-font stack (deliberate deviation). Math: manim's LaTeX (CMU). Labels/UI: one clean geometric sans, chosen at animation time.
- **Spec SVGs/mermaids are reference clues, not layouts.** They tell us *what* to show (topology, ranges, field names) — the composition, pacing, and styling are the video's own. Never transplant a spec diagram's look; redraw its content in this system.

### Style guide (applies to every later pass)

**Written text and stage directions** follow ASD-STE100: short sentences, one claim per sentence, active voice, one fixed name per concept (the spec's name), no synonym rotation.

**Narration** is colloquial and relaxed. The 20-word cap does not bind speech; flamboyance does. Rules:

- Speak like an intelligent person who has nothing to prove.
- Teach inductively (3b1b, Ryan O'Donnell): start from the motivating question. Build intuition through concrete examples and progressively harder cases. Only then introduce the formal machinery.
- After each definition or theorem, connect it back to the larger mental model. Make the structure of the subject explicit: not just what is true, but why anyone would think of it, and how to reuse the idea.
- No drama words ("beautifully," "ruthlessly," "elegant"). A metaphor survives only if the animation draws it.
- Em-dashes rare. Fragments allowed for pacing, sparingly — but no print-cadence fragments that sound odd aloud ("Two loose ends, tied."). If it wouldn't survive being said to a colleague, rewrite it.
- Never reference chapters by number in narration ("as we saw in Act Three") — listeners don't track act boundaries. Recall by content: "the union-by-multiplication trick," "the opaque data field the protocol never reads."
- Contractions and direct address are fine. This is spoken language.
- Pacing: `⟨pause⟩` markers (~600 ms) around math-heavy beats only; slight slow-down applies to marked passages, never whole scenes.

---

## Act 0 — Cold open: the set nobody can prune (~3 min) ✅ approved

### Scene 0.1 — Two sets, two fates `[90s]` (spec: #nf intro)

**Narration beats:**
- Every shielded pool since Zerocash keeps two growing sets: note commitments and nullifiers. They grow at the same rate. Their costs do not.
- The commitment tree is append-only and lazy. Consensus only needs its root. The tree itself can sit on disk. Disk is cheap.
- The nullifier set is the opposite. Every transaction must show its input nullifiers never appeared before. That's an exclusion test against all of history. It runs in memory, on the critical path of consensus.
- At Visa throughput, this set grows by about 500 GB per day. That's the wall. Not proof speed. Not bandwidth. One set nobody can prune.

**VISUAL:** Split screen. Left: Merkle tree accretes leaves, grays out, sinks "to disk"; only the root stays lit. Right: nullifier set as a flare-hot grid in "RAM"; each incoming tx fires a membership probe into it; the grid outgrows the frame; a counter runs to 500 GB/day.

### Scene 0.2 — The thesis: client-side validation `[90s]` (spec: #philosophy)

**Narration beats:**
- Tachyon's answer is one principle: move validation off consensus and onto the client, wherever possible.
- Consensus keeps a rolling window of recent nullifiers. The spender arrives with a proof: this nullifier appears nowhere in older history.
- That proof must stay current as each block lands. So it's built incrementally, with proof-carrying data.
- Ragu interface, stated once: Tachyon runs on Ragu, a recursive proof system. Treat it as a black box with two capabilities. One: it folds proofs into proofs, cheaply. Two: it answers evaluation queries against committed polynomials natively, outside the circuit. Remember the second one. Most of this design stands on it.
- Roadmap: four moves, four chapters. A split in the key structure. Nullifiers that evolve. One polynomial accumulator with sublinear exclusion. A proof tree with shared evidence.
- (Decision locked: open with this scaling hook, then honor the spec's vantage point in Act 1.)

**VISUAL:** The flare-hot grid from 0.1 gets scissored. A thin "recent window" stays with the validator node. The rest flies out to wallet icons, each carrying a small glowing proof token that ticks forward as blocks land. Roadmap: four chapter cards.

---

## Act 1 — The two separations (~5 min) ✅ approved with notes (folded in)

### Scene 1.1 — Why Zcash keys got complicated `[2 min]` (spec: intro + #decouple)

**Narration beats:**
- Sprout needed one payment key and one encryption key. Sapling's key diagram is not that, and Orchard's isn't either. What happened?
- Reason one: proof generation and transaction authorization are different jobs. Hardware wallets can't prove, so from Sapling on, authorization became a signature. Unlinkable signatures must re-randomize. That gives you `ak` in the witness and `rk = ak + [α]G` in the instance.
- Reason two: note ownership and note transmission are different jobs too. The address does both. It declares the owner, and it carries the transmission key for in-band memos. Diversified addresses exist for one reason: refresh the transmission key while `ivk` stays fixed.
- Reason three: selective disclosure. That adds `ovk` and the viewing-key family.
- Now the observation. Out of all this material, exactly two keys enforce ownership: `nk` for nullifiers, `ak` for spend authorization. Everything else serves transmission and viewing.

**VISUAL:** The actual Orchard key-derivation diagram, drawn as a tangle (Sapling's shown briefly beside it for the lineage). Each "reason" lights up the subgraph it caused (rk/α loop; d/ivk/pk_d branch; ovk branch). Then everything dims except `ak` and `nk`, pulsing.

### Scene 1.2 — Tachyon's cut: shielded protocol vs payment protocol `[~2 min]` (spec: #decouple, #payment-key)

**Narration beats:**
- Tachyon cuts along that line.
- The shielded protocol keeps only what ownership needs. The owner field of every note becomes `pk = Com(ak, nk)`: a binding hash commitment.
- The payment protocol gets everything else: addresses, memo encryption, discovery, viewing.
- The hash commitment buys two things. The owner field is succinct. And it's quantum-recoverable today. Publishing `ak`, a Schnorr verification key, to your senders is a harvest-now-decrypt-later risk. `Com(ak, nk)` is not.
- The chain's role splits too. Beyond maintaining the pool, it serves as a data-availability layer. In-band secrets still travel on chain, encrypted, like today's memos. But the shielded protocol never interprets or parses those bytes. No circuit cost. Pure pass-through, for payment protocols and wallet implementations to define.
- Security properties split the same way. One slide, no dwelling. The shielded core keeps ledger indistinguishability, balance, note privacy, and spend unlinkability against payment-key-only attackers. Full spend unlinkability under `ivk` access, and Faerie resistance, move to the payment protocol.
- Two familiar pieces don't change at all. Spend authorization: RedPallas, `rk = [ask + α]G`, same as Orchard. And value balance: the binding signature, a proof of knowledge of the blinding factor behind the homomorphic value commitments. Same mechanism since Sapling. We'll name it once more in Act 3 and never dwell on it.

**VISUAL:** A vertical cut through the key tangle. Two boxes form: "Shielded protocol: (ak, nk) → pk = Com(ak,nk)" and "Payment protocol: ek, tags, discovery (Act 7)." The security-property ledger slides half left, half right. DA beat: encrypted memo bytes flow *through* the shielded box untouched, drawn as a sealed envelope passing a sleeping circuit.

### Scene 1.3 — The Tachyon note `[90s]` (spec: #note)

**Narration beats:**
- A Tachyon note is `(pk, v, ψ, rcm)`. Its commitment: `cm = Com(pk, v, ψ; rcm)`. Poseidon. Purely symmetric.
- ψ is a pseudo-random, per-note identity. Keep it in view. It will seed every nullifier this note ever has.
- Contrast: Sapling and Orchard commit with Pedersen variants, which rest on discrete log. The symmetric `cm` gives quantum recoverability with no extra wallet rules for `rcm`.
- Transition: one field of this note, ψ, is about to do a lot of work.

**VISUAL:** Note as a 4-slot card, each slot annotated. A Pedersen `[v]G + …` expression morphs into a Poseidon sponge icon. The ψ slot stays highlighted into the act transition.

---

## Act 2 — Nullifiers that evolve (~6.5 min) ✅ approved

### Scene 2.1 — Why one nullifier per note has to go `[2 min]` (spec: #nf)

**Narration beats:**
- Recap from Act 0. The node keeps a recent window. The user proves exclusion from older history. PCD keeps that proof current, block by block.
- Nobody wants to sync all day. So you outsource the work to an oblivious syncing service. An OSS.
- Here's the problem. To refresh an exclusion proof for `nf`, the OSS must know `nf`. And whoever knows your nullifier recognizes your spend when it lands on chain. Privacy gone.
- The fix: nullifiers evolve, one value per epoch. The value you hand the OSS in epoch e is unlinkable to the value you reveal at spend time.
- Say the cost out loud, because this audience will ask. This breaks an invariant as old as Zerocash: one note, one globally unique nullifier. Tachyon now owes us two things. A new derivation. A new double-spend rule. Both are coming.

**VISUAL:** Wallet hands `nf` to an OSS robot. Later the same `nf` appears on chain; a dotted red line snaps from OSS memory to the spend. Rewind. Now the handed-over value and the spent value are different random strings; the red line fails to connect. A banner cracks: "1 note = 1 nullifier."

### Scene 2.2 — The derivation `[75s]` (spec: #nf)

**Narration beats:**
- The ideal functionality: `nf_e = KDF(nk, ψ, e)`. Outputs look random. Each one binds the spend authority and the note.
- Tachyon keeps derivation with the user. The OSS receives bare `(i, nf_i)` pairs. No note-binding evidence at all. A real sync request and a decoy list look identical. The binding happens later, on the user's side.
- The concrete construction: a per-note master key `mk = Poseidon(nk, ψ)`. One sponge permutation squeezes a whole Rate-sized window of nullifiers. Cheap to batch in circuit.
- Security, in one line: any secure KDF instantiation works here, because every evaluation you haven't revealed stays indistinguishable from random. That single property is what carries unlinkability across epochs, delegation included.
- From here on, write `nf_e = f_mk(e)`.

**VISUAL:** Sponge squeezes 4 nullifiers per permutation, tiling an epoch axis. The OSS receives a list of gray opaque beads; some carry a "decoy?" tag even the OSS can't read. A revealed subset of beads lights up; the rest stay visibly random static.

### Scene 2.3 — The ranged nullifier commitment: indexed multisets from cubes `[3.5 min]` (spec: #nf-flow; asset: `nf_commit.svg`)

*The first real math set piece. Give it screen time.*

**Narration beats:**
- Here's the gap left by the last scene. The wallet derives `(i, nf_i)` over a range R. The OSS tests some subrange S and commits to what it tested. The wallet must prove: everything the OSS tested is exactly what I derived, index by index. And both commitments grow incrementally.
- A vector commitment would do this. The known ones live on RSA or pairings. Both are circuit-hostile.
- One relaxation saves us. In a standard VC, the prover can commit to anything. Here, every update is proven correct against the running commitment. Honest commitment, enforced. That opens the design space.
- The trick: encode the pair `(i, nf_i)` as a cubic factor, `F(X) = ((i+1)X + nf_i)³ − c`. Here c is a fixed public non-cube. The field has p ≡ 1 mod 3, so c = 2 works.
- Commit to the running product `g_R(X) = ∏ F(X)`. That's an indexed multiset. It grows one epoch at a time, and the endpoint stays open.
- The subset proof is division. Exhibit a quotient q with `g_R = g_S · q`. Fix all three commitments, then check the identity at one random point. This is the first place Ragu's polynomial oracle does real work.
- Now soundness, because you'll want it. `Y³ − c` is irreducible over F_p. Every invertible affine substitution keeps it irreducible. Unique factorization does the rest. The one forgery window: two factors that match up to a cube root of unity ω. But epochs sit below 2³², and ω is a ~255-bit scalar. That collision can't happen.
- One caution. Division is commutative. So it proves inclusion, not order. Order and contiguity come from counters and sentinel endpoints, enforced while the commitment is built. Remember the word "sentinel." Act 4 pays it off.

**VISUAL:** Adapt `nf_commit.svg` (wallet range R above, OSS subrange S below, the containment arrow). Each `(i, nf_i)` bead crystallizes into a cubic factor tile. Tiles multiply into a growing product (shown as factor stacks, not curves). Division: the OSS stack lifts out of the wallet stack, leaving the quotient; a random-point probe `r` strikes all three; equality lights gold. Soundness sidebar: `Y³−c` refuses to factor; the ω collision is drawn, then crossed out with the 2³² vs 255-bit scale comparison.

---

## Act 3 — One accumulator for everything (~5 min) ✅ approved with note (folded in)

### Scene 3.1 — Tachygrams: erasing the commitment/nullifier distinction `[2 min]` (spec: #acc)

**Narration beats:**
- Today every pool runs two structures, because the two jobs look different: a Merkle tree answers membership, a nullifier set answers non-membership.
- Now look at a polynomial accumulator: commit to the polynomial whose roots are your set, `Com(∏(X − tg_i))`. Membership: `f(x) = 0`. Non-membership: `f(x) ≠ 0`. The same single evaluation query answers both. Zero or nonzero.
- That symmetry is the realization that drives the design. If one structure serves both tests at the same cost, why keep commitments and nullifiers apart at all? Unify them.
- So every member is a **tachygram**: a 32-byte blob. A note commitment, in an output. An epoched nullifier, in a spend. On chain you can't tell them apart. And an accidental benefit falls out of the merge: one bigger set means a larger anonymity set.
- Ragu serves these evaluation queries natively, outside the circuit.
- The multiset algebra is the other half of the value. Insert an element: multiply by its factor `(X − tg)`. Remove one: divide by it. Union of two sets: multiply the polynomials, no disjointness condition. Difference: exact division. Every set operation is a polynomial operation, checkable at one random point. Act 4 uses this to compose whole epochs.
- One subtlety, straight from the spec. Commitment binding says `tgacc` opens to one polynomial. It does not say that polynomial matches the published list. A cheating prover can add a root or drop one. So Tachyon checks `tgacc` against the list directly. The verifier computes `y_r = ∏(r − tg_i)` itself. Field operations only; no group work. Then the PCS checks the claim `(tgacc, r, y_r)`. Soundness: D/|F|.

**VISUAL:** The centerpiece here is the set-operation ↔ polynomial-operation correspondence, shown live. Split view: top, a set of points on a number line; bottom, the factored polynomial. Add an element: a point drops onto the line *and* a factor `(X − tg)` slides into the product, degree counter ticks up. Remove one: the point lifts off *and* its factor divides out. Union: two lines zipper together while the two products multiply. Membership probe: a vertical line hits a root, eval snaps to 0, gold; non-membership lands between roots, nonzero, flare — same probe, both answers. Then the Merkle tree and nullifier grid from Act 0 dissolve into this one structure. The attack: a ghost root sneaks in; the `y_r = ∏(r−tg_i)` audit catches the mismatch.

### Scene 3.2 — Actions, stamps, and two tachygrams each `[3 min]` (spec: #tx, #race; asset: `tachyon_tx.svg`)

**Narration beats:**
- The action description shrinks to `(rk, cv)`. Spends and outputs share the format.
- Unlike Sapling and Orchard, no nullifier and no `cm` in the description. Evolving nullifiers aren't static enough to live there. Instead, the note binds to `rk` through its randomizer: `α = PRF(cm ‖ θ)`. A spend has `rk = ak + [α]G`. An output has `rk = [α]G`.
- Side benefit: an output's signing key is just α. A hot device signs outputs. No custody round-trip. Only spends touch `ask`. Both forms of `rk` are uniform points on chain.
- Value balance: same binding-signature mechanism as Sapling and Orchard, as we said in Act 1. Moving on.
- Now the cross-epoch race. Suppose a spend proves only `nf_e`. The epoch can tick to e+1 while the transaction waits in the mempool. Nobody else can refresh the proof. Not the miner. Not the OSS, which never learns future nullifiers, least of all at spend time. The transaction goes stale. Bad UX, and a timing side channel.
- The fix: every spend reveals both `nf_e` and `nf_{e+1}`. To keep spends and outputs identical in shape, every output adds a dummy tachygram next to its `cm`. Every action carries exactly two.
- For the footnote readers: without padding, tachygram count t against action count n leaks the split, s = t − n. With padding, t = 2n always. The leak was only arity. Tachygrams ride in one flat multiset, so which action is which never shows.
- A **stamp** is the bundle's PCD proof. Public inputs: `(actacc, tgacc, anchor)`, plus the published tachygram multiset. `actacc` commits to `∏(X − Poseidon(rk_i, cv_i))`.
- Stamps aggregate: fold many finished transactions into one proof, and let each covered transaction swap its stamp for a `wtxid` reference. How that works is Act 6's business.
- Thirty seconds of txid hygiene. Memo bytes ride as an opaque DA blob, committed through `da_digest` inside the effecting data. Aggregation rewrites stamps, which rewrites `auth_digest` and `wtxid`. But it can't touch the memo: every authorization signature covers `da_digest` through `SIGHASH`. ZIP-244 made the same choice.

**VISUAL:** Adapt `tachyon_tx.svg` (green stable fields vs orange malleable fields) for the txid/wtxid beat. Action card morphs from Orchard's (rk, cv, nf, cm, …) to Tachyon's two fields; the nf/cm fields detach and drop into the stamp's tachygram pouch. Race timeline: a tx floats in a mempool lane toward an epoch-boundary wall; the single-nullifier version shatters at the wall; the `(nf_e, nf_{e+1})` version carries a bridge over it. Padding: spend and output become identical dominoes, two pips each.

---

## Act 4 — The anchor chain and the epoch accumulator (~4 min) ✅ approved

*(From here on, the spec ships purpose-built diagrams. The animation pass reads each referenced SVG in `book/src/assets/` as a content reference — topology, ranges, field names — and redraws it in the video's own visual system. See the design-system note: clues, not layouts.)*

### Scene 4.1 — Anchors per stamp, sentinels per epoch `[2 min]` (spec: #anchor; asset: `anchor_chain.svg`)

**Narration beats:**
- The anchor chain is a hash chain in the block header. It ticks once per stamp: `anchor ← H(anchor_old ‖ i ‖ tgacc)`. Sub-block granularity, above the transaction.
- At each epoch transition, consensus appends exactly one domain-separated **sentinel**: `sntl_i = H(anchor_end ‖ i)`. Every epoch gets two authenticated boundary posts, even an empty one. Every canonical anchor maps to exactly one epoch.
- Why per stamp, not per block? Validator work. The stamp already proved its `tgacc` correct in circuit. The validator just hashes it in. A per-block anchor would make every validator rebuild a block-wide accumulator: re-accumulate, interpolate, commit. That's an MSM on the critical path. The Act-0 philosophy says no.

**VISUAL:** Animate `anchor_chain.svg`: the bead chain ticks along a timeline, each bead absorbing a stamp's tgacc chip; sentinel gates stand at epoch transitions, stamped with the epoch number. Split-screen cost comparison: validator-as-hasher (one hash per stamp) vs validator-as-accumulator (a giant MSM gear grinding).

### Scene 4.2 — The epoch accumulator, and why it's still not enough `[2 min]` (spec: #anchor tail)

**Narration beats:**
- Naive exclusion tests `nf_e` against every stamp accumulator in the epoch. Use the union operation instead. Multiply all stamp polynomials into one epoch accumulator `e(X)`.
- Anyone — typically an OSS — proves `e(X)` correct against the anchor chain with cheap oracle queries. The degree is bounded by the SRS, not by any step circuit. The work is linear in the epoch's stamps. But you pay once and amortize.
- Now run the numbers, slowly, on screen. 100 TPS, two-in-two-out, a two-week epoch: about 4.8 × 10⁸ tachygrams. Our Bulletproofs-style PCS has a linear-time verifier. One verification: over 16 minutes. That doesn't ship.
- So the target for the next act: epoch-wide non-membership, amortized cost sublinear in N, and no high-degree polynomial anywhere near query time.

**VISUAL:** Animate the spec's inline epoch-product diagram: per-stamp polynomials along the epoch zipper-multiply into one huge e(X). Its degree counter spins to 4.8×10⁸. A verification stopwatch runs past 16:00; the frame tints flare. Hard cut to a clean "√" symbol: the QR tease.

---

## Act 5 — Quadratic residue filters (~8 min) — *the centerpiece* ✅ approved (rename folded in)

### Scene 5.1 — Bucketing by an intrinsic address `[90s]` (spec: #qr intro)

**Narration beats:**
- Restate the goal like a theorem: prove `nf ∉ epoch`, at amortized sublinear cost.
- The idea is bucketing. Partition the epoch's tachygrams so the queried element can compute its own bucket address. Then exclusion is one opening against one bucket.
- The address is a **QR profile**: k bits. Bit j answers one question: is `x + R_j` a square? Deterministic. Intrinsic to the element. Roughly balanced. Cheap to prove in circuit.

**VISUAL:** The 4.8×10⁸-root polynomial shatters into a grid of small buckets. A query element glows, computes a bit string overhead (√? √? √? …), and homes in on exactly one bucket.

### Scene 5.2 — Number theory detour `[2 min]` (spec: detour + #batch-qr) — **FULL NARRATION (approved)**

> Take a prime field and set zero aside. The elements that remain split exactly in half. Half are squares — quadratic residues. Half are not. And this property is nearly free to prove in a circuit. To show x is a square, hand the circuit a root y as advice. One constraint: y² = x. To show x is *not* a square, use a classic flip. Multiply by a non-residue, and the class inverts. So fix a public non-residue c. Then y² = c·x is one constraint certifying x is a non-square.
>
> Now slide everything by an offset R, and ask the same question about x + R. That's a *QR discriminant*. One discriminant cuts any fixed set roughly in half. k discriminants give every field element a k-bit profile. Two-to-the-k classes, nearly balanced, computed from x alone. One edge case: x = −R. The shifted value is zero, and zero is neither class. By convention it goes to the residue side. And that convention has to be enforced, not just stated. You'll see why in a minute. One more detail: a claimed non-residue bit needs an extra witness, x + R ≠ 0. Without it, −R could take the non-residue branch with square root zero.
>
> One element at a time is cheap. But we need the test for a whole bucket at once. The polynomial view makes that easy. Take the bucket's accumulator f(X): the product of (X − x_i) over its members. Consensus's uniqueness rule makes it square-free. Suppose every member is a residue. Interpolate a polynomial g through the points (x_i, y_i), where y_i is a square root of x_i. Then g(X)² − X vanishes at every x_i. So f divides it, and the quotient h is the witness. The prover commits to g and h. The verifier throws one random point r and checks g(r)² − r = f(r)·h(r). One identity. One random point. The squareness of every root of f, certified at once. The non-residue version just carries the factor c. That's the whole batched QR test, and it's the only new algebra the rest of this act needs.

**VISUAL:** Field elements as a ring of dots, colored cyan (QR) / amber (NQR) in a perfect half-split. A sliding offset R re-colors the ring. The −R exception dot blinks white. Batched test: roots x_i on an axis; their square roots lift onto an interpolated curve g; the expression g² − (X+R) collapses onto f·h; the random probe r strikes; both sides print the same field element.

### Scene 5.3 — QR decomposition: one split, four checks `[90s]` (spec: #partition; asset: `qr_decomp.svg`)

**Narration beats:**
- The atomic relation: split one square-free bucket f into q₀, the non-residues, and q₁, the residues, under a discriminant R.
- Four checks at one random point. Name them:
  1. Decomposition: `f(r) = q₀(r)·q₁(r)`. No root added, none dropped.
  2. QR purity of q₁: the batched test.
  3. NQR purity of q₀: the batched test, with the factor c.
  4. Zero-value assignment: `q₀(−R) ≠ 0`. This enforces the convention from the last scene. q₀ is a product of linear factors, so a nonzero opening at −R proves −R is not inside it. Check 1 then forces it into q₁.

**VISUAL:** Animate `qr_decomp.svg`: one bucket cleaves in two under a discriminant blade. Four check-lamps light in sequence, each with its one-line identity. Lamp 4 gets a short "why" beat: the −R dot gets pushed to the residue side.

### Scene 5.4 — Routing: decompose–merge rounds and the jagged frontier `[2.5 min]` (spec: #qr-routing; assets: `routing_round.svg`, `jagged.svg`, `qr_routing_network.svg`)

**Narration beats:**
- The epoch arrives as a stream of bounded **root buckets**. Each covers a contiguous anchor range.
- A routing round does two things. Decompose every bucket under the next discriminant; that roughly halves each one. Then merge adjacent outputs that share the extended profile, whenever the union fits capacity. Merging is the multiset-union check again. Nothing new to trust.
- Track the invariant. Decomposition preserves anchor ranges. Merges join contiguous ones. So routing turns many partial-epoch buckets into one full-epoch bucket per profile.
- Rounds parallelize, and they stream. All of this runs in flight, during the epoch.
- Capacity fluctuations leave stragglers. Those get **partial rounds**, only for the unresolved profiles. The result is a **jagged frontier**: final profiles at different depths. Together they form a prefix partition of the field, and every final bucket spans the whole epoch.
- Grinding. The discriminants must stay unpredictable while users can still pick tachygrams. So each OSS samples R₀ privately, steps `R_{j+1} = R_j + 1`, and reveals R₀ only after the epoch closes. Discriminant choice affects balance, never soundness. A biased network gets ignored; use an honest OSS's instead. Consecutive offsets correlate negligibly. One character-sum footnote on screen; no dwelling.
- Scale check. 50K TPS for two weeks: under 4.84 × 10¹¹ tachygrams, under 6.1 × 10⁷ root buckets. About 26 rounds. The 32-bit profile budget has slack.

**VISUAL:** The signature animation of the video, built from the three spec assets. `routing_round.svg` → one station: buckets split into cyan/amber, same-color neighbors fuse, the orange unmergeable bucket stays solo. `qr_routing_network.svg` → zoom out to the full braided stream across stations. `jagged.svg` → the frontier edge, visibly jagged; completed full-epoch buckets click into a finish rail. Then: an adversary aims tachygrams at one bucket, but the discriminant dial sits behind OSS glass until epoch close.

### Scene 5.5 — The evidence tree `[90s]` (spec: #qr-bucket-tree; asset: `qr_tree.svg`; renamed per PR #223)

**Narration beats:**
- One proof per final bucket is too much to keep and serve. After the epoch closes, the OSS folds any set of final buckets into one **evidence tree**.
- A rate-4 Poseidon Merkle tree. Each leaf binds the epoch, both sentinels, R₀, the depth j, the profile b, and `Com(q_b)`. Output: one authenticated root. At 2²⁶ buckets, depth 13.
- Query time: authenticate a leaf with its Merkle path. Membership needs no profile check at all. Any root of an authenticated bucket is a root of the epoch polynomial. Non-membership derives the profile bits from R₀, checks they select this leaf, then opens `q_b(x) ≠ 0`.
- Set this against the Act-4 wall. The 16-minute linear scan became 13 Poseidon hashes and one bounded-degree opening. The routing ran once, in flight, at a service. Every query in the epoch shares it.

**VISUAL:** Animate `qr_tree.svg`: final buckets from 5.4's rail fold upward into a quaternary tree. A query element re-runs its bucket descent *as* a Merkle path. Side-by-side cost cards: "e(X): deg 4.8×10⁸, 16 min" vs "bucket: ≤13 hashes + 1 opening."

---

## Act 6 — The proof tree: shared evidence (~6.5 min) ✅ approved (rename + aggregation demotion folded in)

*(Parallels the blog post, one level deeper: actual steps and headers, plus the bridging discipline.)*

### Scene 6.1 — Steps, headers, bridging `[90s]` (spec: #prooftree intro, #shared-headers; asset: `shared_headers.svg`)

**Narration beats:**
- Flash the monolithic statements: Output, Spend, bundle. One slide, no read-through. They're the contract. The tree is the realization.
- Decompose them into bounded **steps**. Each step folds up to two child proofs, checks part of a statement, and emits a **header**: the PCD public input.
- Parents **bridge** their children. Load both headers; equality-check the fields that must agree. Same `cm`. Matching sentinels. A sound decomposition is exactly this: enough bridging.
- The cast, in the video's role colors. Gold: wallet steps, which see the note. Cyan: OSS steps, which see opaque values. Star-white: shared evidence anyone can consume. Active-epoch `AnchorChain` segments, and closed-epoch **evidence trees** with their leaf openings. Shared evidence is built once per epoch and reused by every wallet. That's the "shared evidence" from the blog post title, now with exact interfaces.

**VISUAL:** Legend scene establishing the three role colors (gold/cyan/star-white), content per `shared_headers.svg` (anchor chains may touch the active tip; evidence trees exist only for closed epochs). A generic step consumes two headers; equality pins snap matching fields together like magnets; a mismatched pin repels with a red flash.

### Scene 6.2 — Same-epoch spend: the minimal tree `[90s]` (spec: #same-epoch-spend; asset: spec mermaid)

**Narration beats:**
- Start with the simplest case: spend a note in its creation epoch. No OSS at all.
- `SpendableInit` proves `cm` is a root of its creation stamp's accumulator, and computes that stamp's anchor. Out comes `NoteSpendable{cm, e, anchor}`. Cache it the moment the creation block finalizes. Ship it to a hardware wallet early.
- `SpendBind` opens the note. It checks `pk`, `cm`, the value range, spend authority, and derives `(nf_e, nf_{e+1})`. Out comes a per-action `Stamp`.
- `StampMerge` multiplies the accumulators across actions. `StampLift` consumes shared `AnchorChain` evidence and moves the stamp to a later anchor. A chain admits no sentinel transition, so a lift can't cross an epoch. And the lift isn't a convenience. It hides the exact inclusion anchor. Spend unlinkability requires that.
- Close with a checklist: each step maps to named clauses of the monolithic statement. Nothing dropped.

**VISUAL:** The spec's same-epoch flow, redrawn and animated node by node in the role colors. The statement checklist ticks off per step. The lift slides a stamp along the anchor chain and bounces off a sentinel gate.

### Scene 6.3 — Past-epoch spend: binding delegated work to the note `[2.5 min]` (spec: #past-epoch-spend, #extend-range; assets: spec mermaids, `tx_flow.svg`)

**Narration beats:**
- Now the full machine: a past-epoch spend. Two independent branches, joined at the end.
- Branch one: the inclusion epoch. User-only, a singleton path. Open the inclusion epoch's evidence tree twice. Once for `cm`, once for `nf_{e_incl}`. `NoteUnspentInit` witnesses the note and `(ak, nk)`, re-derives the nullifier, matches its QR profile, and proves `q_b(nf) ≠ 0`. `SpendableReinit` joins that with the `cm` opening. Out comes a fully established `NoteSpendable` at `e_incl + 1`.
- Branch two: the later epochs. This is where Act 2's promise gets kept.
- Wallet side: `NoteSeed` emits `NoteMaster{cm, mk}`. `NullifierDerive` squeezes bounded windows into the ranged commitment. `NullifierFuse` glues windows together.
- OSS side: `UnspentSeed` starts an empty range. Each `UnspentLift` consumes one evidence-tree leaf opening, proves one non-membership, appends one indexed cubic factor, and advances sentinel to sentinel. It can't skip an epoch. It can't repeat one. It can't reorder.
- `UnspentBind` runs the quotient check from Act 2: everything the OSS tested is contained in what the wallet derived, with indices. `SpendableLift` seams the result onto the spendable proof. Sentinel equality, again. `SpendBind` finishes as before.
- Multiple OSSs compose: `UnspentMerge` joins adjacent ranges with endpoint checks.
- State the privacy bottom line plainly. An OSS sees opaque pairs and ranges. It can't tell them from decoys. It never sees `cm`, the note, another OSS's proof, or the spend anchor. The binding runs entirely on the wallet.

**VISUAL:** The two mermaid diagrams redrawn in the role colors; `tx_flow.svg` as the orienting overview before diving in. The `UnspentLift` ratchet: a pawl clicks sentinel to sentinel; an attempt to skip an epoch physically fails. `UnspentBind` replays the Act-2 division animation, now in context. The payoff of scene 2.3.

### Scene 6.4 — Consensus: the two-epoch window `[90s]` (spec: #consensus-rule; asset: `consensus_window.svg`)

**Narration beats:**
- What does the validator still do? Per stamp: check the anchor is canonical. Check the target epoch is current or preceding. Check `tgacc` against the published list — the field-ops-only check from Act 3. Verify one folded proof.
- Scope the stamp's claim carefully, because the spec does. It proves exclusion *before* epoch e. The target anchor is not an exclusion endpoint. Duplicates inside epoch e are consensus's job.
- The rule: one duplicate window over the current and preceding epochs, processed in deterministic order.
- Why two epochs, and why two nullifiers? Walk both acceptance cases. Accepted in e: a competitor targeting e shares `nf_e`; one targeting e−1 published `nf_e` as its next-epoch value; anything older sits inside the proven history. Accepted in e+1: a competitor targeting e shares `nf_e`; one targeting e+1 shares `nf_{e+1}`; one accepted during e is still in the window. The adjacent pair overlaps the boundary. That overlap is what makes the grace period safe.
- Callback to Act 0: the hot grid is back. But now it's two epochs wide. Forever.

**VISUAL:** Animate `consensus_window.svg`: the timeline with inclusion anchor, sentinels, target anchor, and where each historical claim ends. A sliding two-epoch window; race cases play out as colliding tokens; each collision site flashes its catcher: window / same block / own bundle / proven history. Final shot: the Act-0 monster set next to the bounded window, to scale.

### Scene 6.5 — Aggregation `[40s]` (spec: #aggregation)

**Narration beats:**
- Aggregation, in one breath, because PCD does the heavy lifting. Lift finished stamps to a common anchor, never across a sentinel. Union the multisets, multiply the accumulators, fold the proofs. One stamp now covers many transactions.
- Balance and authorization stay per constituent. Verification amortizes, so the economics favor it. The full story lives in the aggregation chapter; we wave at it and move on.

**VISUAL:** Mempool stamps align onto one anchor tick, then fold into a single aggregate. Per-tx signature seals visibly stay attached to each constituent.

---

## Act 7 — The payment protocol (~4.5 min) ✅ approved (PIR kept as black box)

### Scene 7.1 — The other half of the split `[60s]` (spec: #payment, #pirdb)

**Narration beats:**
- Act 1 left transmission to the payment protocol. Here's the sketch of ValarGroup's design.
- The pain it must kill: trial-decryption sync. Linear in chain length. Leaks metadata. And sandblasting showed what happens under load.
- The replacement is PIR: private information retrieval. The sender publishes `(tag, encrypted memo)`. The recipient retrieves by tag, and the server learns nothing about the query. How PIR achieves that is out of scope; we use it as a black box.
- Four bounded databases: the epoched memo DB, the first-contact DB, the epoched tachygram DB, and a PKI DB. Note the third one. It also feeds spendability witnesses. That's the bridge back to Act 6.

**VISUAL:** Trial decryption: a wallet grinds through every ciphertext on chain. PIR: one silent hand reaches into a database that can't see where it reached. Four DB cylinders, labeled; the tachygram DB wires back to the Act-6 tree.

### Scene 7.2 — ML-KEM addresses and the tag schedule `[2 min]` (spec: #address, #discovery)

**Narration beats:**
- An address is `addr = (pk, ek)`. Both fresh per sender.
- Why not Sapling/Orchard-style diversification? `[ivk]G_d` breaks retroactively under a quantum adversary. One recovered `ivk` opens every incoming note, past and future. And ML-KEM has no shared-dk analogue; no LWE trick gives you one. So `dk` is per sender, and the "one ivk scans everything" convenience is gone.
- Tags restore it. The effective incoming viewing key is `(tag, dk)`. The schedule: `tag₀ = H(ek)` for first contact. The recipient doesn't hold K yet, and this makes the handshake findable in one PIR query. After that, `tag_i = H(K, i)`. Random access, minimal state: one index and one counter per channel.
- Two freshness schedules, stated once. `ek` refreshes per sender, against colluding senders. Tags appear on chain, so they must be fresh per note.
- State the costs honestly. A KEM ciphertext is 768 bytes to 1.5 KB. Only first-contact transactions carry it; follow-ups omit it. Why that's fine, in one sentence: the simulator emits both shapes at random, so ledger indistinguishability holds. Unlinkable payments to one recipient need separate channels, by design. And the address is too big for a QR code, so a hash-indexed PKI database serves the full address on demand.
- Recovery, in one breath. The wallet posts its minimal state on chain, AEAD-encrypted, in the DA field. From a bare mnemonic: reverse-scan for your state ciphertext, decrypt, resume fast sync.
- And Faerie gold, as promised in Act 1. The wallet checks each incoming note's nullifier at a reference epoch against the notes it holds. A reused ψ collides there. A targeted collision is a second preimage on the PRF. Blocked either way.

**VISUAL:** Address card with two freshness dials: per-sender `ek`, per-note tag. Tag sequence as a chain of keyed lockboxes; the `H(ek)` first box glows differently. Size comparison: a 32-byte `epk` dot next to a 1.5 KB ML-KEM ciphertext slab. (Adapt `ek_and_tag.svg` for the derivation beat.)

---

## Act 8 — Quantum posture + outro (~3 min) ✅ approved

### Scene 8.1 — Private today, sound after an upgrade `[2 min]` (spec: #pq)

**Narration beats:**
- The bar is asymmetric. Privacy must hold retroactively: an adversary can harvest today's chain and decrypt later. Soundness only has to hold at spend time, so it can wait for a coordinated upgrade.
- Audit the chain. `pk` and `cm`: Poseidon commitments. Nullifiers: PRF outputs. Memos: ML-KEM. All post-quantum.
- The discrete-log objects left: `cv`, `rk`, and the binding key. `cv` is perfectly hiding. And a quantum DLog on `rk` yields `ask + α` — but α is a fresh PRF mask. The result links to nothing. So the quantum attack is forgery, not a privacy break.
- The upgrade has two pieces. One: no post-quantum signature re-randomizes. So replace signature verification with an in-circuit proof of signature knowledge. Circuit-friendly schemes like CAPSS target exactly this. Authorization then folds into the PCD proof. `rk` leaves the action description. And the note-to-action binding, today through α, must return as an explicit statement constraint. Two: swap Ragu's discrete-log commitments for lattice folding. The folding structure stays. The assumption changes. The construction is honestly TBD.

**VISUAL:** On-chain objects pass through a "quantum lens": commitments, nullifiers, and memos stay opaque; `rk` resolves to `ask + α`, but α pixelates the link back to any identity. Upgrade panel: a signature seal morphs into a proof node absorbed by the stamp; the PCS layer of a proof stack swaps from a DL block to a lattice block.

### Scene 8.2 — Outro: the decision cascade `[60s]`

**Narration beats:**
- Replay the cascade in thirty seconds. An unprunable set forced client-side validation. Client-side validation forced delegated syncing. Delegation forced evolving nullifiers. Evolving nullifiers forced two-nullifier actions and the epoch window. Epochs forced one polynomial accumulator. Its degree forced QR filters. And all of it forced a proof tree whose expensive evidence is built once and shared.
- Each move is forced by the last. The design is a cascade, not a grab bag.
- Pointers, spoken and on screen: the Deep Dive at tachyon.z.cash (plus Sean's posts and the Ragu book) and github.com/tachyon-zcash/tachyon. End card with both links. Out.

**VISUAL:** The four Act-0 chapter cards reconnect into one dependency chain. The camera pulls back to show the full map of everything built during the video.

---

## Decisions locked (2026-10-03, Alex's round-1 review)

1. **One video** (~40 min), acts as chapters. No episode split.
2. **Cold open**: scaling hook stays; Act 1 honors the spec's key-structure vantage point.
3. **Demoted/dropped**: binding-signature recap ("same as Sapling/Orchard," one-line PoK description lives in 1.2 only); nf-analysis alternatives (dropped entirely — no GGM); aggregation details (one breath, "PCD folding does the heavy lifting"); PIR internals (explicit black box).
4. **#nf-sec**: no dedicated scene, no distributed analysis. One line in 2.2: a secure KDF instantiation suffices because unrevealed evaluations stay unpredictable.
5. **Tone**: 5.2 sample approved; it is the template for the full narration pass.
6. **Rename**: QrBucketTree → evidence tree (PR #223); script avoids volatile tree-step names.
7. **Spec assets**: the spec's SVGs (`anchor_chain`, `qr_decomp`, `routing_round`, `jagged`, `qr_routing_network`, `qr_tree`, `shared_headers`, `consensus_window`, `tx_flow`, `nf_commit`, `tachyon_tx`, `ek_and_tag`) are content clues only. One consistent animation style throughout; never force a spec diagram's layout into the video.
8. **Brand**: theme colors from tachyon-website (gold/amber/flare/cyan on deep space); role mapping wallet=gold, OSS=cyan, shared=star-white, hot=flare. Fonts deliberately NOT the website's (Alex finds them under-designed); choose our own at animation time.

## Production pipeline

1. ~~Script flow approval~~ ✅ done (this draft reflects it).
2. **Full narration pass** — expand beats to verbatim narration per the style guide and the 5.2 template. **Alex reviews once more. This is the last gate before ElevenLabs credits.**
3. **Audio** — ElevenLabs TTS, one clip per scene for easy retakes. Voice TBD; generate 2–3 voice samples on one paragraph first (pennies of credit).
4. **Animation** — manimgl scenes per act, synced to clip durations. Read each referenced SVG in `book/src/assets/` and adapt its layout; redraw the spec's mermaid content in the role colors (gold/cyan/star-white).
5. **Assembly** — ffmpeg concat + audio mux.

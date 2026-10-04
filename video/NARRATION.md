# Scaling Zcash with Tachyon — Full Narration (Draft 2, pending Alex's review)

Verbatim spoken text, one block per scene. This is the last gate before ElevenLabs audio.

Notes for review:
- Target pace ~150 wpm; word counts per scene are marked against the staged durations. Under-length is deliberate in visual-heavy scenes (animation gets air).
- Math is written speakably ("a k plus alpha times G"). A mechanical TTS-normalization pass (symbols → spoken strings, pronunciation hints like "O S S", "psi") happens at audio time and won't change wording.
- Role colors in speech follow the brand mapping: wallet = gold, service = cyan, shared evidence = white.

---

## Act 0 — Cold open

### 0.1 — Two sets, two fates (~215 w / 90 s)

If you've worked on Zcash, you know the shielded pool keeps two growing sets. Every transaction adds note commitments and, eventually, nullifiers. They grow at the same rate, but they live very different lives.

The commitment side is easy to serve. The tree is append-only, and consensus only ever needs its root. A validator can push the whole thing to disk and forget about it. Storage is cheap, and nobody's in a hurry to read old leaves.

The nullifier set gets no such luck. When a transaction spends a note, the validator has to answer: has this nullifier ever appeared before? Not recently. Ever. That's a membership test against the entire history of the chain, and it has to be fast, because it sits on the critical path of consensus. So the whole set lives in memory, and it only grows.

Now scale that. At Visa-level throughput, the nullifier set grows by roughly five hundred gigabytes per day. Not per year. Per day. No consensus node holds that in RAM, and no amount of proving cleverness fixes it, because this isn't a proving problem. It's a data structure the protocol never allowed itself to prune.

That's the wall Tachyon is built to remove. And the question it starts from is simple: who actually needs to remember all this?

### 0.2 — The thesis: client-side validation (~230 w / 90 s)

Tachyon's answer is one principle, applied everywhere it can be: move validation off the critical path of consensus, and onto the client. If a transacting user can prove their own correctness, consensus only has to check a proof.

For nullifiers, that looks like this. The consensus node keeps a rolling window of recent history. Everything older gets pruned. And the spender shows up carrying the missing piece: a proof that their nullifier appears nowhere in the pruned past.

Of course, that proof is a moving target. Every new block is more history to be excluded from. So the proof is built incrementally, with proof-carrying data: each update folds the previous proof and the new blocks into a fresh one.

Tachyon runs on Ragu, a recursive proof system built for exactly this. We're not going to open Ragu up in this video. We only need two facts about it. First, it folds proofs into proofs, cheaply — that's what makes incremental updates viable. Second, and this one matters more than it sounds: it can check evaluation claims against committed polynomials natively, as part of the proof system itself, not as circuit constraints. Keep that in your pocket. Most of what follows is built on it.

So here's the plan. Four moves. A separation in the key structure. Nullifiers that evolve. One polynomial accumulator with fast exclusion. And a proof tree whose expensive parts are built once and shared.

---

## Act 1 — The two separations

### 1.1 — Why Zcash keys got complicated (~290 w / 2 min)

Before any of that, Tachyon makes a decision about keys, and it shapes everything downstream. To see why, ask a question you've probably asked yourself while reading the protocol spec: why do Zcash keys keep getting more complicated?

Sprout needed a payment key and an encryption key. Two keys. By Sapling, the diagram has grown spending keys, authorization keys, nullifier keys, viewing keys, diversifiers. Orchard inherits most of it. None of this is accidental — each piece earns its place. It's worth naming what forced each one.

First force: proving and authorizing are different jobs. In Zerocash, a valid proof was ownership — nothing else needed. But hardware wallets can't generate SNARK proofs, so Sapling split authorization into a signature. And a fixed verification key would link every spend from the same owner, so the signature has to re-randomize. That's why a k lives in the proof's witness, and a randomized r k lives in the public instance.

Second force: owning a note and receiving a note are different jobs. The address does both. It declares who owns the note, and it carries a transmission key, because the sender has to deliver the note's secrets somewhere — Zcash uses the chain itself as the bulletin board, with encrypted memos in-band. Diversified addresses exist for exactly one reason: hand out fresh-looking transmission keys while keeping one incoming viewing key for scanning.

Third force: selective disclosure. Letting someone watch your outgoing notes takes its own key. That's where the outgoing viewing key and the rest of the viewing-key family come from.

Now step back and look at the diagram with fresh eyes. For enforcing ownership — deciding who may spend — exactly two keys matter: the nullifier key, and the authorization key. Everything else is about moving or viewing notes. That observation is the knife Tachyon cuts with.

### 1.2 — Tachyon's cut (~300 w / 2 min)

Tachyon separates the shielded protocol from the payment protocol along that exact line.

The shielded protocol keeps the two ownership keys, and nothing else. Every note's owner field becomes p k: a binding hash commitment to the pair — authorization key, nullifier key. The payment protocol takes custody of the rest: addresses, memo encryption, note discovery, viewing capabilities. Wallets define their own key derivation underneath it.

The commitment does two quiet favors. One, the owner field is a single compact value, whatever stands behind it. Two, it's quantum-recoverable today. Handing your bare authorization key — a Schnorr verification key — to everyone who pays you is a harvest-now, decrypt-later liability. A hash commitment to it isn't.

What about the data the payment protocol needs to move? It still travels on chain, encrypted, like memos today. But to the shielded protocol, it's just bytes. Nothing parses them, nothing constrains them, nothing pays circuit costs for them. The chain doubles as a data-availability layer, and the shielded core stays blind to what it carries.

The security properties split along the same seam. The shielded core keeps ledger indistinguishability, balance, note privacy, and spend unlinkability against anyone who only ever saw your payment keys. The stronger flavor — unlinkability against someone holding your incoming viewing key — and Faerie-gold resistance become the payment protocol's responsibilities.

And two familiar mechanisms survive untouched. Spend authorization is Orchard's: RedPallas signatures under a re-randomized key. Value balance is Sapling's: homomorphic value commitments, and a binding signature proving knowledge of the net blinding factor. Same mechanisms, same security arguments. We'll point at them once more and otherwise leave them alone.

What does the cut buy? A small, stable shielded core that can be audited and upgraded on its own — and payment protocols free to evolve, or compete, without touching consensus.

### 1.3 — The Tachyon note (~140 w / 90 s, visuals carry the rest)

Here's the note that core maintains. Four fields: the payment key, a value, a note identity psi, and a commitment trapdoor. The note commitment hashes all four with Poseidon.

That's a smaller diff than it looks, with one deliberate change. Sapling and Orchard commit to notes with Pedersen-style commitments — curve points, discrete-log assumptions. Tachyon's note commitment is purely symmetric: hiding against a quantum adversary, with no special discipline on how the wallet derives the trapdoor.

The field to watch is psi. It's a pseudorandom identity, fixed at creation, known to sender and recipient. In Orchard, the analogous value feeds one nullifier. In Tachyon, psi is about to become the seed of an entire family of them.

---

## Act 2 — Nullifiers that evolve

### 2.1 — Why one nullifier per note has to go (~290 w / 2 min)

Now the main event. Remember the deal we set up at the start: consensus keeps a window, you keep a proof, and that proof needs refreshing every time a block lands.

Realistically, your phone is not going to track the chain around the clock. The natural move is to outsource: hand the refresh work to a service. Tachyon calls it an oblivious syncing service — an O S S.

But watch what the service needs. To prove your nullifier absent from new history, it must know the nullifier. And a nullifier is a one-time, globally unique value. The moment your spend hits the chain, the service — or anyone it shared your value with — points and says: that one's mine. You've outsourced your sync and donated your privacy.

Think about what property we'd want instead. The value the service checks on your behalf, and the value you eventually publish, shouldn't be connectable. But they have to refer to the same note, or the proof means nothing. So: one note, many nullifier values — one per epoch of chain history — where seeing some of them tells you nothing about the rest. The service checks the epochs you delegate. You spend with a value it has never seen.

That's an evolving nullifier, and it's the heart of Tachyon. It's also a genuinely radical edit. Since Zerocash, every design in this family has leaned on one invariant: a note has exactly one nullifier, globally unique in the pool. Double-spend prevention was a membership check against that uniqueness. Break the invariant, and you owe two debts. A derivation that makes per-epoch values unlinkable, yet bound to the note. And a double-spend rule that works when the same note answers to different names in different epochs. The rest of this video pays those debts.

### 2.2 — The derivation (~200 w / 75 s)

The derivation first. What we want is a keyed function: the nullifier at epoch e equals a K D F of the nullifier key, psi, and e. Deterministic, so the note has exactly one value per epoch. Pseudorandom, so values don't link.

Tachyon instantiates it with Poseidon. Hash the nullifier key and psi into a per-note master key, m k. Then one permutation of the sponge squeezes out a whole window of consecutive epoch nullifiers at once — with rate four, four epochs per squeeze. In circuit, that's about as cheap as a batch of nullifiers gets.

What does the service receive? Bare pairs: an epoch index, an opaque value. No key material, no note, no evidence the values relate to anything at all. A genuine sync request and a list of decoys are indistinguishable — the service does the same work either way. The glue that binds its work back to a real note comes later, on the wallet side.

On security, one line covers it: with a sound K D F, every evaluation you haven't revealed is indistinguishable from random. That single property carries unlinkability across epochs — delegation included.

From here on, we'll just write: the nullifier at epoch e is f sub m k of e.

### 2.3 — The ranged nullifier commitment (~530 w / 3.5 min)

So the wallet derives nullifiers, and the service tests them. Here's the gap nobody's closed yet. The wallet derived values for a range of epochs. The service tested values for some sub-range, and committed to the ones it tested. The wallet has to prove a containment: everything the service tested is exactly what I derived — right values, at the right epochs. And both sides built their commitments incrementally, over many proof steps, without knowing in advance where the range ends.

The textbook answer is a vector commitment with subvector openings. The textbook constructions live on RSA groups or pairings, and neither belongs anywhere near these circuits.

But notice the relaxation our setting allows. A standard vector commitment defends against a prover who commits to anything it wants. Our commitments are never free-floating: every single update is proven correct against the previous commitment, inside the PCD. When honest construction is enforced, you get to design the commitment around the proof. The space opens up.

Here's the design. Take the pair — epoch i, nullifier value — and encode it as one cubic factor: open paren, i plus one, times X, plus the nullifier, close paren, cubed, minus c. ⟨pause⟩ The constant c is a fixed public non-cube; our field has p congruent to one mod three, so c equals two does the job. The wallet's commitment over its range is the product of these factors, one per epoch. To append the next epoch, multiply in one more factor, and prove the multiplication with a single random-point check. Notice what we never had to fix: the endpoint. The product grows as long as it needs to.

The service builds the same kind of product over its sub-range. ⟨pause⟩ And now containment has a shape any algebraist would reach for: divisibility. If the service's set really is contained in the wallet's, the wallet's polynomial is divisible by the service's. So the wallet exhibits the quotient, all three commitments get fixed, and one evaluation at a random point checks the product identity. This, by the way, is the first real work done by the polynomial-oracle capability I asked you to keep in your pocket. The check costs the proof system almost nothing.

Why should you believe divisibility proves anything? Because of how the factors were chosen. Y cubed minus c is irreducible when c isn't a cube — and substituting any invertible affine function of X for Y keeps it irreducible. So each factor is irreducible, and unique factorization makes the multiset of factors recoverable from the product. ⟨pause⟩ The only escape hatch would be two different pairs producing the same factor — and that requires their coefficients to differ by a nontrivial cube root of unity. Epoch indices are thirty-two-bit integers; the cube root of unity is on the order of the field size. Those two never meet.

One honest caveat before we move on. Multiplication commutes, so divisibility sees a multiset, not a sequence. Nothing about the quotient says the service processed epochs in order, or didn't skip one. Order comes from somewhere else: counters and endpoint checks, enforced step by step as the commitments are built. You'll meet that machinery in a few minutes, when we give the chain an authenticated timeline. It's called a sentinel. For now, hold the idea: cheap indexed containment, by unique factorization.

---

## Act 3 — One accumulator for everything

### 3.1 — Tachygrams (~320 w / 2 min)

Let's zoom back out, look at what the pool actually maintains, and tidy it.

Every Zcash pool so far runs two data structures, because the two questions sound different. Is this commitment in the pool? A Merkle tree answers membership. Has this nullifier appeared? A set answers non-membership.

Now price those questions against a polynomial accumulator. Commit to the polynomial whose roots are your set. To show membership, evaluate at the element: zero. To show non-membership, evaluate at the element: anything but zero. The same single evaluation answers both questions. There's no asymmetry left.

That symmetry is the observation that drives the design. If one structure serves both tests at the same cost, the distinction between commitments and nullifiers stops paying rent. So Tachyon merges them. Every element in the accumulator is a tachygram: thirty-two bytes, pseudorandom. An output contributes its note commitment; a spend contributes an epoch nullifier. On chain, you can't tell which is which — and as a side effect, everything now hides in one larger anonymity set.

The algebra is the other half of the bargain. Insert an element: multiply by its linear factor. Union two sets: multiply the polynomials — no preconditions, multisets just work. Remove a subset: divide, exactly. Every set operation you'd want is a polynomial operation, and each one checks with one random-point evaluation. We're about to lean on this hard.

One subtlety the spec is careful about, so we will be too. Binding says the commitment opens to one polynomial. It does not say that polynomial has the roots you were told. A dishonest prover could commit to a polynomial with an extra root, or one root short, and flip a membership answer at will. So every accumulator is audited against its published list. The verifier multiplies out r minus each tachygram, at a random r — pure field arithmetic, no group operations — and the proof system checks the committed polynomial agrees. A false claim survives with probability about degree over field size, which is negligible.

### 3.2 — Actions, stamps, and two tachygrams each (~470 w / 3 min)

Where do tachygrams come from? Transactions. Let's build the Tachyon transaction and see what had to change.

An action — the uniform unit of transfer, as in Orchard — is described on chain by just two values now: a randomized key r k, and a value commitment. Notice what's missing. Orchard's action carries its nullifier and new commitment right in the description. Tachyon's can't. Nullifiers evolve, so pinning one into the stable transaction identifier would be pinning a moving part. The tachygrams travel elsewhere — in the stamp, which we'll get to in a moment.

With tachygrams out of the description, something else has to tie the action to its note. That job lands on r k's randomizer: alpha is derived as a P R F of the note commitment. A spend's r k is a k plus alpha times G — spending authority, freshly masked. An output's r k is just alpha times G — no authority at all, because creating a note needs none; the binding signature already ensures outputs are funded. Pleasant consequence: an output can be signed by a hot device, no custody round-trip. Only spends wake the hardware wallet. And both flavors of r k are uniformly random points, indistinguishable on chain.

Value balance: binding signature over homomorphic value commitments, exactly as we said in Act One. Moving on.

Now, a puzzle created by evolving nullifiers. Say your spend proves the nullifier for epoch e — and the transaction sits in the mempool while the epoch rolls over. The proof is now stale. Nobody can fix it but you. Not the miner. Not the service, which never learns future nullifiers — least of all at spend time. A forced refresh is bad UX; worse, it's a timing side channel. Tachyon's fix is blunt and effective: every spend proves and reveals two adjacent nullifiers, epochs e and e plus one. A full epoch of buffer. And so that spends and outputs stay indistinguishable, every output publishes a dummy tachygram alongside its commitment. Two tachygrams per action, always. Without the padding, counting tachygrams against actions would leak how many were spends.

All of this is packaged by the stamp: the bundle's PCD proof. Its public inputs: an accumulator over the action descriptions, the tachygram accumulator, and something called an anchor. That's a new word, and it's the next thing we build. The tachygram list rides along in public, and both accumulators get audited against their lists, exactly as in the last scene. Stamps also aggregate — many transactions folded into one proof, each constituent pointing at the aggregate — but that story comes later, once we've built the proof tree.

Last housekeeping: the memo. Those opaque payment bytes commit into the transaction i d through a dedicated digest, inside the effecting data. Aggregation rewrites a transaction's stamp — that's authorizing data, rewritable in flight. The memo isn't. Every authorization signature covers it. Relayers can replace your proof; they cannot touch your payload. ZIP two-forty-four made the same call, for the same reason.

---

## Act 4 — The anchor chain and the epoch accumulator

### 4.1 — Anchors per stamp, sentinels per epoch (~270 w / 2 min)

We keep saying "authenticated history." Time to actually build it.

The object is called the anchor chain: a running hash carried in every block header. Each accepted stamp ticks it forward. The new anchor is a hash of the previous anchor, the epoch number, and the stamp's tachygram accumulator. That's the whole update. The granularity is worth noticing: not per block — per stamp. In a block of ordinary transactions, the chain ticks once per transaction.

At every epoch boundary, consensus adds exactly one special tick: a domain-separated hash called the sentinel — the ordering machinery I promised when we left the nullifier commitment hanging. Sentinels give every epoch two authenticated endposts — even an epoch with no transactions at all. And because the epoch number is hashed into every tick, any anchor pins down which epoch it belongs to. An anchor is a name for a moment in shielded history. One that a proof can hang evidence on.

Why per stamp rather than per block? Because of who does the work. The stamp already proved, in circuit, that its accumulator matches its tachygrams. So the validator's entire job is one hash. Make the anchor per block instead, and someone has to build a block-wide accumulator — re-accumulate every tachygram, interpolate, commit. That's multi-scalar multiplication on the critical path, for every validator, on every block. The client-side-validation principle says: the prover already volunteered; let them.

So now every stamp names its place in history, and every epoch has sealed endpoints. What we bought is the ability to say, inside a proof: between this sentinel and that one, these accumulators — and only these — happened.

### 4.2 — The epoch accumulator, and the wall (~280 w / 2 min)

Now use it. You hold a note from twenty epochs ago, and you owe exclusion proofs for every epoch in between. Done naively, that's one non-membership test per stamp, across every stamp in twenty epochs. Dead end.

First improvement: the accumulator algebra we just built — union is multiplication. Multiply all of an epoch's stamp polynomials together. The product is itself an accumulator — over every tachygram the epoch produced. Call it the epoch accumulator. One non-membership test per epoch, instead of hundreds of thousands. Whoever builds it can prove it correct against the anchor chain with cheap oracle queries. And because those queries are served by the proof system rather than a circuit, the polynomial's degree is limited only by the commitment setup. Build once, prove once, reuse for every note in the pool. The amortization is exactly what we want.

Except — run the numbers. A modest hundred transactions per second, two-in two-out, for a two-week epoch: around four hundred eighty million tachygrams. One polynomial, degree half a billion. Our Bulletproofs-flavored commitment scheme has a verifier that's linear in the degree. Checking one evaluation against that polynomial takes north of sixteen minutes. Per spend, per epoch crossed. The idea survives; the size doesn't.

Here's the thing, though: the failure is informative. Nothing was wrong with testing against one polynomial. The polynomial was simply too big, because it covered everyone. What we need is the same trick at a smaller scale. Carve the epoch into pieces, such that your nullifier only ever faces one small piece — and such that everyone agrees, verifiably, which piece is yours. That's a strange-sounding requirement. The answer comes from hundred-and-fifty-year-old number theory.

---

## Act 5 — Quadratic residue filters

### 5.1 — Bucketing by an intrinsic address (~215 w / 90 s)

Here's the target, stated like a theorem. For a nullifier, and a closed epoch holding N tachygrams: prove the nullifier appears nowhere in the epoch, at amortized cost sublinear in N.

The plan is bucketing, with a twist. Plenty of structures bucket a set — a hash table buckets a set. The twist is who needs to know the address. When you query a hash table, you trust the table's owner to have routed elements honestly. Here, nothing is trusted. The queried element itself must be able to compute which bucket it belongs to — from its own value, no help, no table. And a verifier must be able to check both that computation, and the claim that the bucket is faithful to the epoch.

So we need a function from field elements to short addresses, with three properties. Deterministic and intrinsic: the address depends only on the element. Balanced: buckets come out roughly equal, so no bucket grows back toward half a billion. And circuit-cheap: the element and the bucket-builder both have to prove facts about addresses, constantly.

Hash the element? Deterministic and balanced, sure. But now every address claim is a hash evaluation in circuit — times every element, times every level of routing. There's something much cheaper hiding in the field itself. It's been there since Gauss.

### 5.2 — Number theory detour (approved verbatim, ~400 w / 2 min)

Take a prime field and set zero aside. The elements that remain split exactly in half. Half are squares — quadratic residues. Half are not. And this property is nearly free to prove in a circuit. To show x is a square, hand the circuit a root y as advice. One constraint: y squared equals x. To show x is *not* a square, use a classic flip. Multiply by a non-residue, and the class inverts. So fix a public non-residue c. Then y squared equals c x is one constraint certifying x is a non-square.

Now slide everything by an offset R, and ask the same question about x plus R. That's a QR discriminant. One discriminant cuts any fixed set roughly in half. k discriminants give every field element a k-bit profile. Two-to-the-k classes, nearly balanced, computed from x alone. One edge case: x equals minus R. The shifted value is zero, and zero is neither class. By convention it goes to the residue side. And that convention has to be enforced, not just stated. You'll see why in a minute. One more detail: a claimed non-residue bit needs an extra witness, x plus R nonzero. Without it, minus R could take the non-residue branch with square root zero.

One element at a time is cheap. But we need the test for a whole bucket at once. The polynomial view makes that easy. Take the bucket's accumulator f of X: the product of X minus x i over its members. Consensus's uniqueness rule makes it square-free. Suppose every member is a residue. Interpolate a polynomial g through the points x i, y i, where y i is a square root of x i. Then g squared minus X vanishes at every x i. So f divides it, and the quotient h is the witness. The prover commits to g and h. The verifier throws one random point r, and checks: g of r, squared, minus r, equals f of r times h of r. One identity. One random point. The squareness of every root of f, certified at once. The non-residue version just carries the factor c. That's the whole batched QR test, and it's the only new algebra the rest of the construction needs.

### 5.3 — QR decomposition: one split, four checks (~225 w / 90 s)

The batched test checks a bucket that's already pure. Routing needs the active version: take a mixed bucket, and split it, verifiably.

So here's the atomic relation — QR decomposition. Input: one square-free bucket polynomial f, and a discriminant R. Output: two buckets. q zero holds the non-residues, q one holds the residues. Four checks certify the split, all at one random point, all after the commitments are fixed.

Check one, conservation: f equals q zero times q one at the random point. Nothing added, nothing dropped. The two children are exactly a factorization of the parent.

Checks two and three, purity: the batched test from the last scene, once per side. Every root of q one is a residue; every root of q zero a non-residue, using the flip factor c.

Check four is the edge case we promised to enforce. The exceptional value, minus R, satisfies the non-residue identity vacuously — zero squared equals c times zero. Nothing in checks two or three keeps it out of the wrong side. But q zero is a product of linear factors, so one nonzero evaluation — q zero at minus R — proves minus R is not among its roots. Combined with conservation, it has nowhere to go but q one. So the convention isn't just stated — it's enforced.

One discriminant, one split, four evaluations. Everything from here on is composition.

### 5.4 — Routing and the jagged frontier (~370 w / 2.5 min)

Now compose it. Remember the shape of the input: the epoch arrives as a stream. Bounded root buckets, each covering a contiguous stretch of the anchor chain.

A routing round does two moves. Decompose: split every bucket under the round's discriminant. Each bucket roughly halves, and each child inherits its parent's anchor range, plus one new profile bit. ⟨pause⟩ Merge: wherever two adjacent buckets now carry the same profile, multiply them back together — as long as the product stays within capacity. Merging is just multiset union — multiply the polynomials, the same operation we've been using all along. It needs no new trust.

Watch what the two moves preserve. Splits keep anchor ranges. Merges concatenate adjacent ones. So as rounds stack up, buckets get purer in profile and wider in history. Run it to the end, and you get, for each profile, a single bounded bucket covering the entire epoch. That's the destination: one bucket per address, each spanning everything. ⟨pause⟩

The rounds are embarrassingly parallel — splits are independent, merges are local — and the whole network runs in flight, while the epoch is still open, as stamps arrive.

Reality is slightly jagged. Capacity is a hard bound and luck varies, so after the planned rounds, a few profiles still hold multiple partial buckets. Those continue: partial rounds, touching only the unresolved profiles. Different profiles finish at different depths. The finished set forms a prefix partition of the field: unequal depths, but no overlaps and no gaps, and every final bucket covers the full epoch. ⟨pause⟩

One adversarial question before the payoff. The addresses are balanced for fixed sets — but users choose their tachygrams after seeing the chain. Could someone grind commitments that all land in one bucket, and blow it past capacity? Only if they can predict the discriminants. So the service samples its starting offset privately, steps it by one each round, and reveals it only after the epoch closes. And notice the trust model. A bad choice of discriminants can unbalance buckets, but it cannot forge a split — soundness lives in the four checks, not in the choice. A lopsided routing network is simply ignored, in favor of an honest one.

Does the address space suffice? Fifty thousand transactions per second, for two weeks, is under half a trillion tachygrams — about sixty million root buckets, so roughly twenty-six rounds. The design budgets thirty-two bits of profile, so there's plenty of slack.

### 5.5 — The evidence tree (~235 w / 90 s)

Routing leaves one proof per final bucket. Potentially millions of proofs to store and hand out. One more fold fixes that.

After the epoch closes, the service gathers its final buckets into a Merkle tree — the evidence tree. Poseidon hashes, arity four to match the sponge rate. Each leaf binds everything a query will need: the epoch, both sentinels, the starting discriminant, the profile and its depth, and the commitment to that bucket's polynomial. One folded proof attests that every leaf descends from valid full-epoch routing. The service can then throw the routing proofs away. What remains, per epoch, is a single authenticated root.

Queries become small. Membership — was this commitment in the epoch? Authenticate any leaf containing it, and open the polynomial at the value: zero. No address check needed; a root of an honest bucket is a tachygram of the epoch, whichever bucket holds it. Non-membership — the question nullifiers ask — derive your element's profile from the revealed discriminant, check it selects this very leaf, and open: nonzero. The address check is what upgrades "absent from this bucket" to "absent from the epoch."

Now set the before and after side by side. A few minutes ago, epoch-wide exclusion meant one evaluation against a polynomial of degree half a billion: sixteen minutes. Now it means thirteen Poseidon hashes and one bounded opening — the heavy routing done once, in flight, by a service, and shared by every query in the epoch. That's the sublinear exclusion we ordered.

---

## Act 6 — The proof tree: shared evidence

### 6.1 — Steps, headers, bridging (~230 w / 90 s)

At this point we have all the parts: evolving nullifiers, accumulators, anchors, evidence trees. What remains is assembly. One spendability proof, built from pieces made by different parties — who must learn nothing about each other.

The spec writes the requirements as three monolithic statements: output, spend, bundle. We won't read them; think of them as the contract. The realization is a tree of steps. Each step is one bounded circuit. It takes up to two child proofs, verifies part of the contract, and folds everything into a new proof. What a step publishes is its header — the public input that summarizes the computation beneath it.

The soundness discipline is bridging. A parent reads both children's headers and equality-checks every field they must agree on: the same note commitment, the matching sentinel, the adjoining epoch. Decomposing a monolithic statement into a tree is sound exactly when the bridges don't leak — when no field that matters crosses a seam unchecked.

Three colors sort the cast, and we'll keep them to the end. Gold steps run on the wallet; they see the note. Cyan steps run at a service; they see opaque values. White is shared evidence, consumable by anyone: anchor-chain segments for the active epoch, evidence trees for closed ones. White is built once per epoch, and every wallet in the pool reuses it. One party's work, everyone's evidence.

### 6.2 — Same-epoch spend (~230 w / 90 s)

Warm up with the easiest spend: the note was created in the current epoch. No history to exclude — the note didn't exist before. No service needed.

Step one, SpendableInit — gold. The moment the creation block is final, the wallet proves its commitment is a root of the creating stamp's accumulator, and computes that stamp's anchor. Out comes the first header: NoteSpendable. This commitment, this epoch, this anchor. Cache it. It's also exactly what a hardware wallet needs, so signing can start in parallel.

Step two, SpendBind. Open the note; check the payment key, the commitment, the value range, the spending authority; derive the two adjacent nullifiers. The result is a one-action stamp.

StampMerge multiplies stamps together — both accumulators at once — gathering the bundle's actions under one proof.

And StampLift slides a finished stamp forward along the anchor chain, consuming white anchor-chain evidence. Two details matter. A chain segment never contains a sentinel, so a lift cannot cross into a new epoch — crossing would silently skip an exclusion obligation. And lifting isn't cosmetic. A stamp anchored exactly at its note's creation block points a finger at which note it spends. Moving the anchor forward blurs that.

Every clause of the contract lands in some step. The checklist on screen is the audit — pause the video if you want to match them up.

### 6.3 — Past-epoch spend (~390 w / 2.5 min)

Now the real thing: the note is several epochs old. Inclusion in its creation epoch; exclusion through every epoch since. Two branches, built independently, bridged at the end.

Branch one covers the creation epoch, and it's all gold. From that epoch's evidence tree, open two leaves: one for the commitment, one for the nullifier at the inclusion epoch. NoteUnspentInit witnesses the note and both ownership keys, re-derives that nullifier, derives its address, checks the address selects the opened leaf, and opens the bucket: nonzero. Absent. SpendableReinit bridges in the commitment's own leaf — zero this time, present — and emits a clean NoteSpendable, valid from the next epoch on. Notice the shape: the same evidence tree answered both membership and non-membership, and the wallet never consulted anyone.

Branch two covers the delegated epochs. This is where the delegation machinery — the ranged commitment, the cubic factors — finally clicks together. On the wallet, gold: NoteSeed reopens the note once, and emits a small reusable header carrying the commitment and the master key. NullifierDerive squeezes windows of nullifiers and builds the ranged commitment — those cubic factors. NullifierFuse multiplies windows into one range.

At the service, cyan: UnspentSeed opens an empty range. Each UnspentLift consumes one evidence-tree opening, proves one epoch's non-membership, appends that epoch's indexed factor, and moves exactly one sentinel forward. The seams are equality checks on sentinels, so the service cannot skip an epoch, repeat one, or shuffle the order. The ratchet turns one way.

The bridge is UnspentBind — gold, and the payoff of those cubic factors. One quotient check: the service's product divides the wallet's. Because every factor binds an epoch to a value, divisibility here means each value the service tested is the true nullifier for that exact epoch. Delegated work, bound to a note the service never saw.

SpendableLift seams the bound range onto the running proof — endpoint to endpoint — and SpendBind finishes as before. If you split the range across several services, UnspentMerge joins adjacent results under the same endpoint discipline.

Tally what any service learned: index-value pairs, and a range. Indistinguishable from decoys. No commitment, no note, no sight of another service's work, no spend anchor. Everything that ties the work to your note happened in gold.

### 6.4 — Consensus: the two-epoch window (~240 w / 90 s)

All of this lands on a validator's desk. What's left to check?

Per stamp, four things. The target anchor occurs in canonical history. Its epoch is the current one, or the one before. The accumulators match their published lists — the cheap field-operations audit you've already seen. And one folded proof verifies. Constant-ish work, no matter how much history the proof covers. That's client-side validation, delivered.

But read the stamp's guarantee precisely. It proves exclusion before the target epoch — and nothing about the target epoch itself. It can't; that epoch is still being written. Fresh duplicates are consensus's half of the bargain. The rule: keep every tachygram from the current and preceding epochs in one window. Process candidates in deterministic order. Check, then insert.

Why two epochs? Because of the mempool grace period — a stamp targeting epoch e is still acceptable in e plus one. Walk the cases, with the two published nullifiers in hand. Accepted during e: a rival spend targeting e collides on the epoch-e nullifier. One targeting e minus one published that same value as its next-epoch nullifier. Anything older is already inside the proof's history. Accepted during e plus one: rivals targeting either epoch collide on one of the pair, and an earlier acceptance is still in the window. The adjacent pair overlaps every boundary. No seam to slip through.

And that's the monster from the opening, tamed. The unbounded set is now two epochs wide. Permanently.

### 6.5 — Aggregation (~100 w / 40 s)

Aggregation, briefly — the folding structure makes it almost free. Take finished stamps from different transactions. Lift each to a common anchor — within the epoch, never across a sentinel. Union the tachygrams, multiply the accumulators, fold the proofs. One stamp now vouches for all of them, and each covered transaction keeps a pointer to it. Signatures and balance stay per transaction; aggregation touches proofs, never authority. The block verifies one proof where it would have verified fifty — so aggregators get paid to make verification cheaper. The details fill a chapter. The mechanism, you've already seen.

---

## Act 7 — The payment protocol

### 7.1 — The other half of the split (~165 w / 60 s)

The shielded core is done. But way back at the key-structure split, we banished note transmission to the payment protocol. Time to pay that debt. Here's the design ValarGroup is building.

The enemy is trial decryption. Today, a wallet attempts every memo on chain. Linear work that grows with everyone else's traffic, leaks your timing to whoever serves you blocks, and — as the sandblasting incident demonstrated — melts under adversarial load.

The replacement is private information retrieval. Senders publish each encrypted memo under a short tag. A recipient who knows the tag asks a PIR server for it, and the server answers without learning which entry it served. How PIR pulls that off is its own rabbit hole; for today it's a black box with one promise — retrieval without a trace.

The protocol keeps four bounded databases: per-epoch memos, first-contact handshakes, per-epoch tachygrams, and an address registry. Watch the tachygram one. It's how wallets gather the raw material for the spendability proofs we just built, without revealing which note they hold.

### 7.2 — ML-KEM addresses and the tag schedule (~300 w / 2 min)

An address is two keys: the payment key you've met, plus an encapsulation key for M L KEM. Both are minted fresh for every sender.

They have to be fresh, because the diversified-address trick is gone — and it's worth being precise about why. Orchard mints unlinkable addresses that all decrypt under one incoming viewing key. The algebra behind that is discrete log, so a future quantum adversary can recover the viewing key from old chain data, retroactively, and read your entire incoming history. Lattice KEMs offer no analogue of that shared-key diversification. So every sender gets a genuinely fresh key pair, and the one-key-scans-everything convenience dies with the vulnerability.

Tags bring the convenience back. The effective incoming viewing key becomes the tag sequence plus the decapsulation key. For first contact, the tag is simply a hash of the encapsulation key — the recipient doesn't hold a shared secret yet, and this way, a single PIR lookup finds the handshake. Every later note tags itself with a hash of the shared secret and a counter. That gives the recipient random access, keeps the sequence opaque to everyone else, and shrinks the wallet's persistent state to an index and a counter per channel.

The costs, stated honestly. A KEM ciphertext is a kilobyte, give or take — so only first contact carries one, and follow-up notes ride free. Unlinkable payments to the same recipient require separate channels; that's by design. And the full address outgrows a QR code, so a registry database serves it from a short digest.

Before we close this chapter, let's tie up two threads we left hanging earlier. The first is recovery. The wallet periodically posts its minimal state on chain, encrypted, inside that opaque data field the shielded protocol carries but never reads. A wallet starting from a bare mnemonic scans backward from the tip, finds its state ciphertext, decrypts it, and resumes fast syncing. The second is Faerie gold. When a note arrives, the wallet computes its nullifier at a fixed reference epoch and compares it against the notes it already holds. A reused psi collides immediately, and a targeted collision would be a second preimage on the P R F. Both attacks get caught at the door.

---

## Act 8 — Quantum posture + outro

### 8.1 — Private today, sound after an upgrade (~290 w / 2 min)

One question left: the quantum one. Tachyon's stance fits in a sentence: private today, sound after an upgrade. The asymmetry is deliberate. Privacy has to hold retroactively — today's chain can be harvested now and decrypted whenever the hardware arrives, so anything guarding privacy must already be post-quantum. Soundness — nobody forges, nobody steals — only matters at spend time, so it can wait for a coordinated network upgrade.

Audit today's chain against that bar. Owner fields and note commitments: Poseidon. Nullifiers: P R F outputs. Memos: M L KEM, plus symmetric encryption. All of it quantum-safe already. The discrete-log survivors are three: value commitments, randomized keys, and the binding key. The value commitment is perfectly hiding — there's nothing to decrypt. And the randomized key? A quantum computer takes its discrete log and recovers a s k plus alpha — where alpha is a fresh P R F mask. A random-looking scalar, linkable to nothing. So the full quantum power against today's Tachyon is forgery. Theft, not exposure. Which is precisely the half that's allowed to wait.

When the upgrade comes, two swaps. First, authorization. Re-randomization is intrinsically discrete-log; no post-quantum signature does it. The replacement recovers unlinkability from zero knowledge instead: prove, in circuit, that you know a valid post-quantum signature. Schemes like CAPSS are built to be cheap exactly there. Authorization then folds into the transaction's PCD proof, the randomized key leaves the action description entirely — and the note-to-action binding it used to carry through alpha gets re-established as an explicit constraint in the statement. Second, the proof system itself: Ragu's discrete-log commitments swap for lattice-based folding. The recursive structure that makes spendability proofs incremental survives; the hardness assumption underneath changes. The concrete lattice constructions are active research. The honest status: to be determined — by design, not blocked.

### 8.2 — Outro: the decision cascade (~150 w / 60 s)

Run the whole design backward, and it compresses into one breath. The nullifier set couldn't be pruned — so validation moved to the client. Clients can't sync alone — so syncing got delegated. Delegation would leak the spend — so nullifiers evolve. Evolving nullifiers would go stale in the mempool — so actions carry a pair, and consensus keeps a two-epoch window. Per-stamp history needed composing — so one accumulator, with union by multiplication. Its degree exploded — so quadratic residues bucket each epoch. And none of it would be affordable alone — so the expensive evidence is built once, proven once, and shared by everyone.

Each decision is forced by the one before it. That's the takeaway: Tachyon isn't a bag of tricks. It's one principle — the client proves, consensus checks — followed to its conclusions.

Everything in this video is written down, in much more detail, in the Deep Dive at tachyon dot z dot cash, alongside Sean's posts and the Ragu book. The implementation is open, on our GitHub. Both links are right below. Thanks for watching.

---

**Totals:** ~6,400 words ≈ 42 min at 150 wpm.
**Pacing convention:** `⟨pause⟩` marks a ~600 ms break, inserted only around math-heavy beats (2.3, 5.4). At audio time these become TTS break tags, and only the marked passages get a slightly slower delivery — never a whole scene.
**On-screen at outro:** https://tachyon.z.cash and https://github.com/tachyon-zcash/tachyon rendered as end-card links while the last lines are spoken.

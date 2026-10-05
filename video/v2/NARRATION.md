# Scaling Zcash with Tachyon — v2 Narration (Draft 1)

> Verbatim narration, one section per scene, matching `scenes.md` Draft 3.
> Written to be read aloud, by a human narrator or by TTS.
>
> Pronunciation: "Tachyon" is TACK-ee-on, "tachygram" is TACK-ee-gram, "Ragu" is
> ra-GOO (like the sauce), "psi" is "sigh". Short key names are written hyphenated as
> they should be spoken ("r-k", "n-k", "c-m"). Greek letters are spelled out.
> Step names (SpendBind, StampLift, …) are written as single CamelCase words.
>
> Pauses come in two kinds:
> - `⟨pause⟩` is a short breath (~0.6 s), used only around math-heavy beats.
> - `⟨pause: what's on screen⟩` is a held beat. The voice stops while the named
>   visual plays, and the animation decides how long it lasts (typically 1–3 s). The
>   label is an anchor for syncing the animation to the script, and is never spoken.
>
> Voice (from Sean's review, PR #2), applies to every line:
> 1. Collaborative, not commanding. "We" and "let's" do things; the narration never
>    barks imperatives at the viewer ("Take…", "Multiply…", "Notice…", "Remember…").
> 2. No filler. Cut any line that restates what the previous sentence or the animation
>    already showed, and any witty capper or tag line after a point has landed
>    ("Theft, not exposure", "That doesn't ship"). Transitions are one short clause.
> 3. Let the picture talk. When an animation is doing the explaining, the narration
>    stops for it (a held `⟨pause: …⟩`) instead of talking over it or describing it.

---

## Chapter 0 — Prologue

### 0.1 — Two sets, two fates

Here are two sets. Every shielded pool since Zerocash keeps both of them, and they grow at the same rate: one entry for every note created, one for every note spent. Which of them is the problem? ⟨pause: both sets grow side by side⟩

On the left, note commitments. They live in an append-only Merkle tree. To keep appending, a node only needs the tree's frontier: one hash per level. So everything else can be pruned already today, and the long-term cost of the tree is logarithmic. ⟨pause: the tree prunes down to its frontier⟩

On the right, nullifiers. Every transaction has to show that its input nullifiers have never appeared before. That's an exclusion test against all of history, so the whole set sits in memory, on the critical path of every validator.

At Visa-level throughput, this set grows by about five hundred gigabytes a day, and nothing in it can ever be thrown away. ⟨pause: counter rolls to 500 GB / day⟩ A nullifier from ten years ago still has to block a double spend today.

That's the fundamental scaling limitation: a linearly-growing set nobody can prune.

### 0.2 — The thesis, the black box, and our protagonist

Tachyon's answer starts from one principle: move validation off the critical path of consensus, and onto the client, wherever you can. Consensus keeps only the nullifiers from recent history. Everything older gets cut loose. ⟨pause: the grid is scissored, older history flies to wallets⟩ The spender arrives with a proof instead: my nullifier appears nowhere in that older history.

That proof can't be made once and forgotten. Every new block is more history it has to cover. So it's built incrementally, as proof-carrying data, extended a little each time the chain moves.

All of this runs on Ragu, a proof-carrying data system in the Halo lineage, over the Pasta curves, with no trusted setup. We'll treat it as a black box with two ports. The fuse port takes up to two proofs and a bit of new work, and hands back a single proof that covers all of it. The query port answers evaluations: we commit to a polynomial, name a point, and get back its value there. ⟨pause: fuse and query ports animate⟩ Ragu is designed to expose these evaluation claims to the application directly, and to fold them into the proof system's own running claim, instead of paying for them in circuit constraints. That query port will be critical, as we'll see.

Time in Tachyon is cut into epochs, long stretches of blocks. To go through the design, we'll follow one note. It's born in epoch five, and it's spent in epoch nine. ⟨pause: note card docks, epoch rail draws itself⟩ Every piece of Tachyon will show up exactly when this note needs it.

---

## Chapter 1 — Ownership, stripped down

### 1.1 — Why Zcash keys got complicated

Before the note can exist, it needs an owner.

The first Zcash shielded protocol, Sprout, following the original Zerocash, needed two keys: a payment key and an encryption key. Orchard's key diagram is much more complicated, but why? ⟨pause: Orchard's key diagram beside Sprout's two keys⟩

The first reason is that proving and authorizing turned into different roles. Hardware wallets are resource-constrained, and they can't run a prover. So from Sapling on, authorization became a signature, made outside the proof. But a signature under a fixed key would link every spend by the same owner. So the key gets re-randomized each time. a-k sits in the secret witness, and the instance carries r-k, which is a-k plus alpha times G.

The second reason is that the address does two jobs at once. It declares who owns the note. And it carries the transmission key, which the sender uses to encrypt the note's secrets on chain. Diversified addresses exist for that second job. They refresh the transmission key for each sender, while a single incoming viewing key, i-v-k, can still detect every incoming note.

The third reason is selective disclosure. A user may want to show their incoming or outgoing flows to someone without handing over spend authority. That brings in the outgoing viewing key, and the rest of the viewing family.

So which of these keys actually enforce ownership? Only two. The nullifier key, n-k, derives nullifiers. The authorization key, a-k, authorizes spends. Everything else serves transmission and viewing.

### 1.2 — The cut

Tachyon cuts along exactly that line. ⟨pause: the blade cuts the key tangle into two boxes⟩

On one side sits the shielded protocol. Its job shrinks to the minimum the pool needs: bind every note to an owner, and make sure only that owner can spend it. On the other side sits the payment protocol. It owns everything about getting a note to its recipient: addresses, memo encryption, note discovery, and viewing.

The owner field of every note becomes a payment key, p-k: a binding commitment to the pair a-k and n-k. Built from a hash, that gives you two things. It's succinct. And it's quantum-recoverable today. Handing a-k, a Schnorr verification key, to every sender is a harvest-now, decrypt-later risk. A hash commitment to it is not.

The shielded protocol doesn't even constrain how a-k and n-k are derived. It only requires that they look like freshly sampled keys. Derivation paths are the wallet standard's business.

Security properties split along the same line. The shielded core keeps ledger indistinguishability, balance, note privacy, and spend unlinkability against an attacker who holds just your payment key. Full unlinkability against someone who holds your viewing key, and resistance to Faerie gold, become the payment protocol's job.

The chain's role splits too. Besides maintaining the pool, it becomes a data-availability layer. Encrypted payment data still rides on chain, but the shielded protocol carries those bytes without ever parsing them.

Two familiar pieces don't change at all. Spend authorization is still RedPallas, with the same re-randomized key. And value balance is still the binding signature over homomorphic value commitments, exactly as in Sapling and Orchard.

The cut buys a smaller surface for each upgrade, cleaner security assumptions to audit, and two halves that can evolve in parallel.

### 1.3 — The note

With an owner in hand, here's the note itself. A Tachyon note has four fields: the payment key p-k, the value v, a field called psi, and a commitment trapdoor, r-c-m.

Its commitment, c-m, commits to p-k, v, and psi, under the trapdoor r-c-m. It's built from Poseidon, a sponge hash, so it's purely symmetric.

Sapling and Orchard use variants of the Pedersen commitment. Those rest on discrete log, and Orchard has to put extra rules on how wallets derive r-c-m to stay quantum-recoverable. Tachyon's commitment doesn't need them.

That leaves psi. It's a pseudorandom identity for the note, derived from the wallet's master key, and every nullifier this note will ever have hangs off it.

So the note exists. Where does its commitment go?

---

## Chapter 2 — Birth

### 2.1 — A set as the roots of a polynomial

Let's take a set: the numbers two, seven and eleven, in the field with thirteen elements. We build the polynomial whose roots are exactly those members: X minus two, times X minus seven, times X minus eleven. ⟨pause: roots drop on the field line, product builds factor by factor⟩ Committing to it gives an accumulator.

Membership is a single evaluation. Seven gives zero. Five gives something nonzero, so five isn't in the set. Both answers come from Ragu's query port.

Today every pool keeps two different structures, because the two jobs look different: a Merkle tree for the membership of commitments, and a set for the non-membership of nullifiers. If one structure answers both questions at the same cost, why keep them apart? Tachyon doesn't. ⟨pause: Merkle tree and nullifier grid dissolve into one accumulator⟩ Every member of this one accumulator is a tachygram: a thirty-two byte blob that might be a note commitment, or might be a nullifier. On chain, you can't tell which.

Set operations become polynomial operations. Inserting an element multiplies by its factor. Removing one divides it out. The union of two sets is the product of their polynomials, with no requirement that they be disjoint. And a subset is a divisor, so containment is exact division. Every one of these can be checked at a single random point. ⟨pause: the dictionary completes⟩

Evaluation ignores multiplicity, so strictly this is a multiset. But consensus refuses duplicate tachygrams, so every accumulator that matters in practice has distinct roots.

There's one subtlety. Commitment binding says the accumulator opens to one polynomial. It doesn't say that polynomial has the published roots. A prover could slip in an extra root, or drop one, and the queries would lie. ⟨pause: a ghost root sneaks in, the probe lies⟩ So Tachyon checks each accumulator against its published list of tachygrams. The verifier picks a random point r, and computes the product of r minus each tachygram itself, with field operations only, no group work. Then it asks the commitment to open at r to that value. A false polynomial survives with probability at most its degree over the size of the field.

### 2.2 — The action and the stamp

Now the note enters the pool. It's created by an output action, and in Tachyon an action description is just two values: a randomized key, r-k, and a value commitment, c-v. Spends and outputs share that shape.

Orchard's action carries the nullifier and the note commitment right in the description. Tachyon pulls both out. ⟨pause: Orchard's action card morphs into (rk, cv)⟩ Nullifiers here won't stay fixed, as we'll see, so they can't live in a static description. Instead, the note binds to its action through r-k's randomizer. Alpha is a PRF of the note commitment and some fresh entropy, theta. For an output, r-k is just alpha times G. For a spend, it's a-k plus alpha times G.

As a side effect, an output's signing key is alpha itself. Creating a note needs no spend authority, because the binding signature already guarantees that outputs are funded. So a hot device can sign outputs with no round trip to custody. And both forms of r-k are uniformly random points, so nobody can tell them apart.

What does an output prove? Its value commitment hides minus v. The value is in range, at most the total money supply. The commitment c-m opens to this note. The key r-k is bound to c-m through alpha. And no published tachygram is zero. There's no anchor and no epoch: history can't affect an output.

A bundle's actions form a multiset too. Each action's r-k and c-v are hashed with Poseidon, and the results are accumulated just as before. That's the action accumulator.

Next, the stamp. A stamp is the bundle's proof-carrying data proof. Its public inputs are the action accumulator, the tachygram accumulator, and an anchor. Alongside, it publishes the tachygrams themselves. Our note's commitment is one of them, with a second slot right next to it that we'll fill later.

As for where the stamp lives, the transaction ID commits only to effecting data: the action accumulator, the value balance, and a digest of the memo bytes. The stamp sits with the signatures, in the authorization data, which is malleable by design. A relayer can swap a stamp. That changes the witness transaction ID, but not the transaction ID. And the memo is safe from that rewriting, because every signature covers its digest through the sighash.

### 2.3 — The anchor chain

The stamp lands on the anchor chain. This is a hash chain carried in the block header, and it ticks once per stamp. Each tick absorbs the stamp's tachygram accumulator, along with the current epoch number: the new anchor is the hash of the old anchor, the epoch, and the accumulator. ⟨pause: beads absorb accumulator chips along the rail⟩ So the chain moves at a granularity finer than a block, but coarser than a transaction.

At every transition between epochs, consensus appends one special tick, a sentinel: a domain-separated hash of the last anchor of the old epoch and the new epoch's number. Every epoch, even one with no stamps at all, gets two authenticated boundary posts. And every anchor on the canonical chain belongs to exactly one epoch.

Here's our note's stamp, landing inside epoch five. ⟨pause: our bead lands in epoch five⟩

Why anchor per stamp, and not per block? Because of validator work. Each stamp already carries its accumulator, checked cheaply against its published list. So a validator just hashes it in. A per-block anchor would make every validator rebuild a block-wide accumulator from scratch: re-accumulate every tachygram, interpolate the product, and commit to it. That's a multi-scalar multiplication on the critical path.

---

## Chapter 3 — Time passes

### 3.1 — Why one nullifier per note has to go

Epoch six begins. Then seven. ⟨pause: the now-cursor slides, the proof token ticks at every bead⟩ Our note sits there unspent, and its owner wants it to stay spendable. That means keeping its exclusion proof current, because every stamp that lands is new history the proof has to cover.

Nobody wants their wallet online for that. So the wallet hands the job to a service, an oblivious syncing service, or O-S-S. It watches the chain, and keeps the proof up to date.

But here's the problem. To prove a nullifier is absent from history, the service has to know the nullifier. And whoever knows the nullifier recognizes the spend the moment it lands on chain. ⟨pause: a flare line snaps from the service to the spend⟩

Tachyon's fix is to let the nullifier evolve. A note gets a different nullifier in every epoch. The value the wallet shares with the service for epoch six is unlinkable to the value it reveals when it spends in epoch nine. ⟨pause: rewind: per-epoch values, the line fails to connect⟩

This breaks an invariant as old as Zerocash: one note, one globally unique nullifier. So Tachyon needs two things: a new way to derive nullifiers, which comes next, and a new rule against double spending, which comes when we reach the validator.

### 3.2 — The derivation, and two nullifiers per spend

The ideal is a deterministic function of three inputs: the nullifier key n-k, the note's psi, and the epoch, e. Its outputs should look random, bind both the spending authority and the note, and stay unlinkable across epochs to anyone without n-k.

A constrained PRF would let the wallet hand the service a key that only works for a range of epochs. But the known candidate, built from a GGM tree, is expensive in a circuit. Tachyon takes a simpler route. The user derives the nullifiers, and proves them. The service gets nothing but bare pairs: an epoch, and a nullifier value. No evidence linking them to any note at all. A real syncing request could just as well be a decoy list. The binding back to the note happens later, on the wallet's side.

Concretely, the wallet first derives a per-note master key, m-k, as a Poseidon hash of n-k and psi. Then one Poseidon permutation of m-k squeezes out a whole window of nullifiers at once, as many as the sponge's rate. With rate four, one permutation gives epochs four through seven, and the next gives eight through eleven. ⟨pause: the sponge squeezes four nullifiers per permutation onto the rail⟩ From here on, we'll just write the nullifier at epoch e as f of m-k, at e.

Any nullifier that hasn't been revealed stays indistinguishable from random. That carries balance, privacy against the sender, who made the note but never learns n-k, and unlinkability across epochs, delegation included.

There's also a timing problem. Suppose a spend proves only the nullifier for the current epoch, e. It waits in the mempool, and the epoch ticks over to e plus one. ⟨pause: a single-nullifier transaction shatters at the sentinel gate⟩ Now the proof is stale, and nobody else can refresh it. Not the miner, and not the service, which never learns spend-time nullifiers. So every spend reveals two nullifiers: the one for epoch e, and the one for e plus one.

That's the empty slot next to our note's commitment: an output fills it with a dummy tachygram, the hash of random bytes. Without it, a spend would show two tachygrams and an output just one, and counting tachygrams against actions would reveal how many of each a bundle has. With the padding, every action carries exactly two. ⟨pause: spend and output become identical two-pip dominoes⟩

### 3.3 — The ranged nullifier commitment

The wallet has derived nullifiers over a range of epochs, R, from four up to twelve. The service has tested a subrange, S: epochs six, seven, and eight. And it has committed to what it tested. Eventually the wallet has to prove that every pair the service tested is one it derived itself, at the same epoch index. And both sides build their commitments a little at a time, across many proof steps.

A vector commitment would do this. But the known schemes with subvector openings live on RSA groups or on pairings, and neither is friendly to our circuits. In a standard vector commitment, though, the prover can commit to anything, so the scheme has to defend against that. Here, every update to a commitment is itself proven correct against its running value. Honest committing is enforced, and that opens up the design space.

⟨pause⟩

So let's encode each pair as a polynomial factor that binds both position and value. For epoch i, with nullifier n-f-i, we take i plus one, times X, plus n-f-i, cube it, and subtract a constant, c. ⟨pause⟩ Multiplying these factors over the whole range gives a commitment to an indexed multiset. Appending the next epoch is one more multiplication, so the range can keep growing, with no fixed endpoint. ⟨pause: tiles stack one at a time, right end open⟩

Containment is division. The wallet exhibits a quotient, q, so that its product equals the service's product times q. ⟨pause: the service's stack lifts out of the wallet's, leaving q⟩ All three commitments are fixed before a random challenge, r, and the check is one identity at one point, through Ragu's query port.

Why is this sound? ⟨pause⟩ Our field has p equal to one, mod three, so we can fix c equal to two, a public non-cube. Then Y cubed minus c is irreducible, and so is every invertible affine substitution of it, since i plus one is never zero. In the field with thirteen elements, the cubes are one, five, eight, and twelve, and two isn't among them. ⟨pause: the thirteen-element clock: two is not a cube⟩ With unique factorization, the only way to forge is for two different pairs to produce the same factor. That happens only when they differ by a nontrivial cube root of unity, omega. But epochs are below two to the thirty-two, and omega is an enormous field element, so that collision never happens.

One caution. Multiplication is commutative, so division proves inclusion, not order. Order and contiguity come from counters, and from sentinel endpoints, checked as each side is built.

---

## Chapter 4 — Exclusion at scale

### 4.1 — The epoch accumulator, and the wall

So the service has to prove that our nullifier for epoch six never appeared anywhere in epoch six. How?

The naive way tests it against every stamp's accumulator in the epoch. But union is multiplication, so we can multiply all of the epoch's stamp polynomials into one epoch accumulator, e of X, whose roots are every tachygram published that epoch. The service proves it correct against the anchor chain with random-point checks. And since those queries are served by the folding scheme rather than a step circuit, e of X can have as high a degree as the commitment scheme allows. The work is linear in the epoch, but it's paid once, and shared.

Let's run the numbers. A modest one hundred transactions per second, all two-in, two-out, over a two-week epoch, gives more than four hundred and eighty million tachygrams. Our polynomial commitment uses a Bulletproofs-style inner product argument, and its verifier is linear in the degree. A single verification would take more than sixteen minutes. ⟨pause: degree counter spins to 4.8 × 10⁸, stopwatch passes 16:00⟩

So the target is to prove non-membership over a whole epoch, at an amortized cost sublinear in its size, with no huge polynomial anywhere near the query.

### 4.2 — Bucketing by an address the element computes itself

The idea is to split the epoch into buckets, so a query only has to look in one of them. That works if the value being queried can work out its own bucket, from nothing but itself. Then it belongs to exactly one bucket, and if it ever appeared in the epoch, it has to be in there. Non-membership over the whole epoch becomes one opening, against one small bucket. ⟨pause: e(X) shatters into buckets, a query homes in on one⟩

So we need an address that a field element computes from itself, that splits sets evenly, and that's cheap to prove in a circuit. Quadratic residues are exactly that.

⟨pause⟩

In a prime field, setting zero aside, the remaining elements split exactly in half. Half of them are squares, the quadratic residues. Half are not. In the field with thirteen elements, the squares are one, three, four, nine, ten, and twelve. ⟨pause: the clock: residues cyan, non-residues amber⟩

Proving that x is a square takes one constraint: the circuit gets a root, y, and checks that y squared equals x. Proving that x is not a square uses a classic flip. Multiplying by a non-square swaps the two classes. ⟨pause: multiplying by two swaps the colors⟩ So with a fixed public non-residue, c, y squared equals c times x certifies that x is a non-square. Again, one constraint.

Now let's shift everything by an offset, R, and ask the same question about x plus R. That's a QR discriminant. ⟨pause: sliding R recolors the ring⟩ One discriminant cuts any fixed set roughly in half. With k of them, every element gets a k-bit profile, sorting the field into two to the k classes of nearly equal size, all computed from x alone.

One edge case. If x equals minus R, the shifted value is zero, which is neither a square nor a non-square. By convention, it goes to the residue side. And that has to be enforced, not just stated. A claimed non-residue bit also needs a witness that x plus R is nonzero. Otherwise minus R could take the non-residue branch, with a square root of zero.

### 4.3 — The batched QR test, and one decomposition

One element at a time is cheap. But we need to certify a whole bucket. The polynomial view makes that easy.

Let's take a bucket's accumulator, f, the product of X minus x-i over its members, and suppose every member is a square. Consensus refuses duplicates, so the roots are distinct. That means we can interpolate a polynomial, g, through the points x-i, y-i, where each y-i is a square root of x-i. ⟨pause⟩ Now g squared minus X vanishes at every member. So f divides it, and the quotient, h, is the witness. The prover commits to g and h. The verifier throws a random point, r, and checks that g of r, squared, minus r, equals f of r times h of r. ⟨pause: both sides print the same element⟩ One identity, at one point, certifies that every root of f is a square. The non-residue version carries the constant c, and an offset R just replaces X with X plus R.

Now let's use it to split a bucket.

Under a discriminant R, split f into two pieces: q-zero, holding the non-residues, and q-one, holding the residues. ⟨pause: the blade cleaves the bucket into amber and cyan⟩ Four checks at a random point keep that split honest. First, decomposition: f equals q-zero times q-one, so no root was added, and none was dropped. Second, every root of q-one is a residue. Third, every root of q-zero is a non-residue. And fourth, q-zero at minus R is nonzero. That last one enforces the convention. q-zero is a product of linear factors, so a nonzero value at minus R means minus R isn't one of its roots. Together with the first check, if minus R is in the bucket at all, it's forced into q-one.

### 4.4 — Routing: decompose, merge, and a jagged frontier

Now let's build buckets for a whole epoch, at scale. An epoch doesn't arrive all at once. It streams in, stamp by stamp. So while epoch six is live, the service rolls consecutive stamps into bounded summaries: one product polynomial each, plus the anchor range it covers. A summary grows by checking, at a random point, that the new product is the old one times the next stamp's accumulator, and by absorbing that stamp into its anchor. A summary never crosses a sentinel. Each one becomes a root bucket, with an empty profile.

Then the service routes. A routing round does two things. It decomposes every bucket under the next discriminant, which roughly halves each one. Then it merges neighbors that ended up with the same profile, as long as their union still fits in a bucket. Merging is just the union check again, so there's nothing new to trust. ⟨pause: one routing round: split, then merge⟩

Underneath, the anchor ranges are tracked too. Decomposition keeps a bucket's range. A merge joins two adjacent ranges into one. So round by round, many partial pieces of a profile become one bucket that spans the entire epoch. The rounds run in parallel, they stream, and they run while the epoch is still live. ⟨pause: zoom out over the braided network⟩

Some profiles lag behind. Fluctuations in size leave a few of them still in pieces, and only those get another, partial round. That leaves a jagged frontier: final profiles at different depths, together partitioning the field, each one covering the whole epoch from sentinel to sentinel. ⟨pause: finished buckets click onto the finish rail⟩ Once the epoch closes, a seal step checks both sentinels.

In the proof tree, each split is one step that proves the product and the minus-R check, followed by two descents. Each descent returns one side, and checks the purity of the other side. With both children derived, both buckets are certified pure.

What about an attacker who grinds tachygrams to overload a single bucket? The discriminants have to stay unpredictable while tachygrams are being chosen. So each service samples its first offset privately, steps it up by one each round, and reveals it only after the epoch closes. That choice affects balance, never soundness. The proofs certify any choice, and a badly balanced routing can simply be ignored in favor of an honest service's.

And even at fifty thousand transactions per second, a thirty-two bit profile has room to spare.

### 4.5 — The evidence tree

Serving one proof per final bucket would be a lot to keep around. So after the epoch closes, the service folds any set of final-bucket proofs into one evidence tree. It's a Poseidon Merkle tree with arity four, matching the sponge's rate. Each leaf binds the epoch, its two sentinels, the first discriminant, the bucket's profile and depth, and the bucket's commitment. The output is a single root. ⟨pause: buckets fold into a rate-4 tree, a root glows over epoch six⟩ The tree doesn't have to include every bucket. Even a single leaf is valid, because each leaf is already a proven full-epoch bucket.

For membership, we authenticate a leaf, and check that the value is a root of its bucket. No profile is needed, because every bucket divides the epoch's polynomial, so any root is a tachygram from that epoch. That's how our note's commitment will be found in epoch five. For non-membership, we re-derive the discriminants, check that the value's bits select this leaf, and check that the bucket is nonzero there. That's how our nullifier for epoch six will be cleared.

The sixteen-minute linear verification became at most thirteen hashes, and one opening of bounded degree. The routing ran once, in flight, and building the tree is the only work left after the epoch closes.

---

## Chapter 5 — The proof tree

### 5.1 — Steps, headers, bridges

So what does the actual proof look like?

A spend has to satisfy a long statement. So does an output, and so does the bundle that glues them together. We don't prove those in one piece. We break them into steps. ⟨pause: statement cards shatter into a tree of steps⟩ A step is a bounded circuit. It takes up to two child proofs and some private witness, checks part of the statement, and emits a new proof whose public output is a header: the data, in proof-carrying data. Headers flow upward, from children to parents.

A parent bridges its children. It loads both headers, and checks that the fields which have to agree really do: the same note commitment, matching sentinels, the same epoch. A decomposition is sound exactly when there's enough bridging.

From here on, three colors. Gold steps run on the wallet, and see the note. Cyan steps run on a service, and see only opaque values. And white is shared evidence that anyone can use: anchor chain segments for the active epoch, and evidence trees for closed ones.

### 5.2 — Same-epoch spend: the base tree

Let's start with the simplest spend. It's now epoch nine, and the wallet also received another note earlier in this same epoch. Spending a note in the epoch it was created needs no exclusion proof at all. It didn't exist before, so there's nothing to exclude.

The first step, SpendableInit, takes the creation stamp's data as witness, proves that the note's commitment is a root of that stamp's accumulator, and computes the anchor that stamp produced. Out comes a header that says: this note is spendable, with its commitment, its epoch, and that anchor. The wallet can build it as soon as the creation block is final, and cache it, or even hand it to a hardware wallet early.

Then SpendBind opens the note. It checks the payment key against a-k and n-k, recomputes the commitment, checks the value range, binds r-k through alpha, and derives the two nullifiers, for epochs nine and ten. It emits a stamp for this one action. An output gets its stamp from a single step, OutputSeed, which covers the whole output statement. And StampMerge joins stamps by multiplying their accumulators.

Finally, StampLift. It consumes a shared anchor chain segment, and moves the stamp to a later anchor. That segment contains no sentinel, so a lift can never cross into another epoch. And the lift isn't just a convenience. Without it, the stamp's anchor would point right at the note's creation. Lifting is part of what keeps the spend unlinkable. ⟨pause: the full base tree, checklist complete⟩

Every spend ends this way: SpendBind, merge, lift. The only question is what feeds SpendBind when the note is older.

### 5.3 — Past-epoch spend: our original note

Now our original note: born in epoch five, spent in epoch nine. Its history splits into three parts.

First, the epoch it was born in. This part stays on the wallet. The wallet opens epoch five's evidence tree twice: once at the bucket for its epoch-five nullifier, and once at the bucket for its commitment. NoteUnspentInit opens the note with its keys, re-derives that nullifier, checks that its profile selects the bucket, and proves it's absent. SpendableReinit then joins that with the commitment's membership opening, for the same epoch and the same sentinels. Out comes a fully established spendable header, valid from the start of epoch six. ⟨pause: the spendable header glows⟩

Second, epochs six through eight. Here the work splits. On the service, UnspentSeed starts an empty range. Then each UnspentLift consumes one evidence-tree opening, proves one opaque nullifier absent, multiplies one cubic factor into the service's commitment, and advances from one sentinel to the next. It can't skip an epoch, repeat one, or reorder them. ⟨pause: a skip attempt jams the ratchet⟩ And the service never learns which note this is.

Meanwhile, the wallet derives its own range. NoteSeed opens the note once, and emits its master key header. Each NullifierDerive squeezes out one window: four up to eight, then eight up to twelve. NullifierFuse joins them into one commitment, over four to twelve.

Third, the join. UnspentBind checks that the service's range is nonempty and sits inside the wallet's, and then runs the division from before: the service's product divides the wallet's. ⟨pause: the service's stack lifts out of the wallet's⟩ That's the moment the delegated, note-independent work becomes about this note. SpendableLift then seams the result onto the spendable header, with sentinel equality at the seam. And now the note is spendable through the start of epoch nine.

From there, it's the same as before. SpendBind derives the nullifiers for nine and ten. StampMerge joins this stamp with the other spend and the outputs, and one StampLift moves the whole thing to the transaction's target anchor, in epoch nine. ⟨pause: the full tree: one stamp, two spends, two outputs⟩

If the wallet uses several services for different ranges, UnspentMerge joins adjacent results before binding, checking that one's end sentinel is the other's start.

As for privacy, a service sees opaque values and ranges it can't tell from decoys. It never sees the commitment, the note, another service's work, or where the spend lands.

---

## Chapter 6 — Landing

### 6.1 — The validator and the two-epoch window

So what's left for the validator? Per stamp, four checks. The target anchor is in canonical history, and its epoch is either the current one, or the one before. The action accumulator matches the actions, and the tachygram accumulator matches the published list, using the cheap random-point check. And one proof verifies. Balance and signatures work exactly as in Orchard.

Let's be precise about what the stamp claims. It proves exclusion strictly before the target epoch. For our spend, that means up to the sentinel that opens epoch nine. The target anchor is not an exclusion endpoint. Duplicates inside epoch nine are consensus's job. That's why every spend targeting epoch nine has to publish its nullifier for nine.

So here's the new double-spend rule. Consensus keeps one duplicate window, holding every tachygram from the current epoch and the one before. Candidates are processed in a fixed order, each one checked, then inserted.

Why that shape? Let's think like a double spender, and recall the grace period we allowed, so that a transaction waiting in the mempool doesn't go stale: a stamp targeting epoch nine is still accepted during epoch ten. So the attacker builds two spends of the same note. The first targets epoch nine, and is held back until epoch ten begins. The second targets epoch ten. Both proofs are honest. The second one proves that its nullifier for epoch nine never appeared in epoch nine, and that's true, because the first spend didn't land in epoch nine. It landed in ten.

If each spend published only its own epoch's nullifier, the first would reveal the value for nine, the second the value for ten, and nothing would collide. That's why every spend also publishes the next epoch's nullifier. The first spend reveals nine and ten. The second reveals ten and eleven. They collide on ten. ⟨pause: the two spends' tokens collide on ten⟩

And the window? The attacker can push one step further, and hold the second spend back until epoch eleven. Now the colliding values land in different epochs, ten and eleven. A window over the current and the preceding epoch still holds both, and catches it. ⟨pause: the window slides and catches the collision⟩ Anything older falls inside the history a stamp already proves excluded.

Together, the adjacent pair and the two-epoch window close the gap the grace period opened. And consensus now holds two epochs of tachygrams, not all of history. ⟨pause: the two-epoch grid beside the original from the prologue⟩

### 6.2 — Aggregation

Finally, aggregation. A miner, or anyone else, takes finished stamps from different transactions, lifts them to a common anchor in the same epoch, never across a sentinel, and merges them with the very same StampMerge: union the multisets, multiply the accumulators, fuse the proofs. ⟨pause: stamps slide to a common anchor and fold into one⟩ The aggregate has the same shape as any stamp, so it can merge again. Each covered transaction drops its own stamp for a reference to the aggregate's witness transaction ID. Balance and signatures stay with each transaction. Only proof verification is shared, and that's an incentive to aggregate.

---

## Chapter 7 — The other half

### 7.1 — Addresses, tags, and private retrieval

The cut we made at the start left the payment protocol in charge of delivering notes. Here's a sketch of the leading design, being built by ValarGroup.

An address is a pair: the payment key, and an ML-KEM encapsulation key, both fresh for each sender. Why not Orchard-style diversification? Because it isn't quantum-private. All those diversified keys share one incoming viewing key, and anyone who can break one discrete log recovers it, exposing every incoming note, past and future. ⟨pause: a quantum lens over i-v-k opens every note⟩ ML-KEM is post-quantum, but it has no analogue of many unlinkable keys sharing one decryption key.

So discovery needs a different shortcut, and that's tags. Each encrypted memo carries a short tag. The first-contact tag is a hash of the encapsulation key, so the recipient can find the handshake before it knows the shared secret. Every later tag is a hash of the shared secret and a counter: predictable to the two parties, opaque to everyone else, and fresh for every note, since tags appear on chain.

Instead of trial-decrypting the whole chain, the wallet looks up its tags with private information retrieval, which reveals nothing about the query. The same machinery includes a tachygram database, which privately supplies the stamp and anchor data the spend proof needs.

Finally, Faerie gold. Tachyon's notes have no canonical position, so the shielded protocol can't bind psi the way Orchard binds rho. Instead, the wallet checks each incoming note's nullifier at a fixed reference epoch against the notes it already holds. A reused psi collides right there.

---

## Chapter 8 — Quantum posture, and the cascade

### 8.1 — Private today, sound after an upgrade

That leaves the quantum question. Tachyon's stance is private today, sound after an upgrade, and the asymmetry is deliberate. Privacy has to hold retroactively. Today's chain can be harvested now and decrypted whenever the hardware arrives, so anything guarding privacy must already be post-quantum. Soundness, meaning nobody forges and nobody steals, only matters at spend time, so it can wait for a coordinated network upgrade.

Let's audit today's chain against that bar. Owner fields and note commitments: Poseidon. Nullifiers: P R F outputs. Memos: M L KEM, plus symmetric encryption. All of it quantum-safe already. The discrete-log survivors are three: value commitments, randomized keys, and the binding key. The value commitment is perfectly hiding, so there's nothing to decrypt. And the randomized key? A quantum computer takes its discrete log and recovers a s k plus alpha, where alpha is a fresh P R F mask, so it gets a random-looking scalar that links to nothing. ⟨pause: the quantum lens: alpha pixelates the link⟩ So the full quantum power against today's Tachyon is forgery, which is the half that can wait for the upgrade.

When the upgrade comes, two swaps. First, authorization. Re-randomization is intrinsically discrete-log, and no post-quantum signature does it. The replacement recovers unlinkability from zero knowledge instead: prove, in circuit, that you know a valid post-quantum signature. Schemes like CAPSS are built to be cheap exactly there. Authorization then folds into the transaction's PCD proof, the randomized key leaves the action description entirely, and the note-to-action binding it used to carry through alpha gets re-established as an explicit constraint in the statement. Second, the proof system itself: Ragu's discrete-log commitments swap for lattice-based folding. The recursive structure that makes spendability proofs incremental survives, and the hardness assumption underneath changes. The concrete lattice constructions are active research.

### 8.2 — Outro: the decision cascade

⟨pause: the camera pulls back over the note's whole journey⟩

Running the whole design backward: the nullifier set couldn't be pruned, so validation moved to the client. Clients can't sync alone, so syncing got delegated. Delegation would leak the spend, so nullifiers evolve. Evolving nullifiers would go stale in the mempool, so actions carry a pair, and consensus keeps a two-epoch window. Per-stamp history needed composing, so one accumulator, with union by multiplication. Its degree exploded, so quadratic residues bucket each epoch. And none of it would be affordable alone, so the expensive evidence is built once, proven once, and shared by everyone. ⟨pause: chapter cards reconnect into one chain⟩

Each decision is forced by the one before it, all following one principle: the client proves, and consensus checks.

Everything in this video is written down, in much more detail, in the Deep Dive at tachyon dot z dot cash, alongside Sean's posts and the Ragu book. The implementation is open, on our GitHub. Both links are right below. Thanks for watching.

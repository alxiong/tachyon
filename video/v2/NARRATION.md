# Scaling Zcash with Tachyon — v2 Narration (Draft 1)

> Verbatim narration, one section per scene, matching `scenes.md` Draft 3.
> This is the last gate before ElevenLabs credits.
>
> Conventions for the TTS pass (applied by the generator, not edited here):
> "Tachyon" and "tachygram" get the v1 respellings. Short key names are written
> hyphenated as they should be spoken ("r-k", "n-k", "c-m"). Greek letters are spelled
> out. `⟨pause⟩` is a ~0.6 s break, used only around math-heavy beats.
> Step names (SpendBind, StampLift, …) are written as single CamelCase words.

---

## Chapter 0 — Prologue

### 0.1 — Two sets, two fates

Here are two sets. Every shielded pool since Zerocash keeps both of them, and they grow at the same rate: one entry for every note created, one for every note spent. So which of them is the problem?

On the left, note commitments. They live in an append-only Merkle tree, and consensus only ever needs its root. The tree itself can sink to disk, and disk is cheap.

On the right, nullifiers. Every transaction has to show that its input nullifiers have never appeared before. That's an exclusion test against all of history, and a node can't afford to answer it from disk. So the whole set sits in memory, on the critical path of every validator.

At Visa-level throughput, this set grows by about five hundred gigabytes a day, and nothing in it can ever be thrown away. A nullifier from ten years ago still has to block a double spend today.

That's the fundamental scaling limitation: a linearly-growing set nobody can prune.

### 0.2 — The thesis, the black box, and our protagonist

Tachyon's answer starts from one principle: move validation off the critical path of consensus, and onto the client, wherever you can. Consensus keeps only the nullifiers from recent history. Everything older gets cut loose. And the spender arrives with a proof: my nullifier appears nowhere in that older history.

That proof can't be made once and forgotten. Every new block is more history it has to cover. So it's built incrementally, as proof-carrying data, extended a little each time the chain moves.

All of this runs on Ragu, a proof-carrying data system in the Halo lineage, over the Pasta curves, with no trusted setup. We'll treat it as a black box with two ports. The first one fuses. Give it up to two proofs and a bit of new work, and it hands back a single proof that covers all of it. The second one answers queries. Commit to a polynomial, name a point, and get back its value there. Ragu is designed to expose these evaluation claims to the application directly, and to fold them into the proof system's own running claim, instead of paying for them in circuit constraints. The second part will be critical, as we'll see.

Time in Tachyon is cut into epochs, long stretches of blocks. And here's how we'll go through the design. We'll follow one note. It's born in epoch five, and it's spent in epoch nine. Every piece of Tachyon will show up exactly when this note needs it.

---

## Chapter 1 — Ownership, stripped down

### 1.1 — Why Zcash keys got complicated

Before the note can exist, it needs an owner.

The first Zcash shielded protocol, Sprout, following the original Zerocash, needed two keys: a payment key and an encryption key. Orchard's key diagram is much more complicated, but why?

The first reason is that proving and authorizing turned into different roles. Hardware wallets are resource-constrained, and they can't run a prover. So from Sapling on, authorization became a signature, made outside the proof. But a signature under a fixed key would link every spend by the same owner. So the key gets re-randomized each time. a-k sits in the secret witness, and the instance carries r-k, which is a-k plus alpha times G.

The second reason is that the address does two jobs at once. It declares who owns the note. And it carries the transmission key, which the sender uses to encrypt the note's secrets on chain. Diversified addresses exist for that second job. They refresh the transmission key for each sender, while a single incoming viewing key, i-v-k, can still detect every incoming note.

The third reason is selective disclosure. You want to show your incoming or outgoing flows to someone without handing them spend authority. That brings in the outgoing viewing key, and the rest of the viewing family.

Now look at the diagram again, and ask: which of these keys actually enforce ownership? Only two. The nullifier key, n-k, derives nullifiers. The authorization key, a-k, authorizes spends. Everything else serves transmission and viewing.

### 1.2 — The cut

Tachyon cuts along exactly that line.

On one side sits the shielded protocol. Its job shrinks to the minimum the pool needs: bind every note to an owner, and make sure only that owner can spend it. On the other side sits the payment protocol. It owns everything about getting a note to its recipient: addresses, memo encryption, note discovery, and viewing.

The owner field of every note becomes a payment key, p-k: a binding commitment to the pair a-k and n-k. Built from a hash, that gives you two things. It's succinct. And it's quantum-recoverable today. Handing a-k, a Schnorr verification key, to every sender is a harvest-now, decrypt-later risk. A hash commitment to it is not.

The shielded protocol doesn't even constrain how a-k and n-k are derived. It only requires that they look like freshly sampled keys. Derivation paths are the wallet standard's business.

Security properties split along the same line. The shielded core keeps ledger indistinguishability, balance, note privacy, and spend unlinkability against an attacker who holds just your payment key. Full unlinkability against someone who holds your viewing key, and resistance to Faerie gold, become the payment protocol's job.

The chain's role splits too. Besides maintaining the pool, it becomes a data-availability layer. Encrypted payment data still rides on chain, but the shielded protocol carries those bytes without ever parsing them.

Two familiar pieces don't change at all. Spend authorization is still RedPallas, with the same re-randomized key. And value balance is still the binding signature over homomorphic value commitments, exactly as in Sapling and Orchard.

So what does the cut buy? A smaller surface for each upgrade, cleaner security assumptions to audit, and two halves that can evolve in parallel.

### 1.3 — The note

With an owner in hand, here's the note itself. A Tachyon note has four fields: the payment key p-k, the value v, a field called psi, and a commitment trapdoor, r-c-m.

Its commitment, c-m, commits to p-k, v, and psi, under the trapdoor r-c-m. And it's built from Poseidon, a sponge hash. Purely symmetric.

Compare that with Sapling and Orchard, which use variants of the Pedersen commitment. Those rest on discrete log, and Orchard has to put extra rules on how wallets derive r-c-m to stay quantum-recoverable. Tachyon's commitment doesn't need them.

That leaves psi. It's a pseudorandom identity for the note, derived from the wallet's master key. It does nothing visible yet. But hold on to it, because every nullifier this note will ever have hangs off psi.

So the note exists. Where does its commitment go?

---

## Chapter 2 — Birth

### 2.1 — A set as the roots of a polynomial

Take a set. Say the numbers two, seven and eleven, in the field with thirteen elements. Now build the polynomial whose roots are exactly those members: X minus two, times X minus seven, times X minus eleven. Commit to it, and you have an accumulator.

Membership is a single evaluation. Plug in seven, and you get zero. Plug in five, and you get something nonzero, so five isn't in the set. It's the same query either way: zero means in, nonzero means out. And that query is exactly what Ragu's second port answers.

Now notice what that means. Today every pool keeps two different structures, because the two jobs look different: a Merkle tree for the membership of commitments, and a set for the non-membership of nullifiers. If one structure answers both questions at the same cost, why keep them apart? Tachyon doesn't. Every member of this one accumulator is a tachygram: a thirty-two byte blob that might be a note commitment, or might be a nullifier. On chain, you can't tell which.

Set operations become polynomial operations. Inserting an element multiplies by its factor. Removing one divides it out. The union of two sets is the product of their polynomials, with no requirement that they be disjoint. And a subset is a divisor, so containment is exact division. Every one of these can be checked at a single random point.

Evaluation ignores multiplicity, so strictly this is a multiset. But consensus refuses duplicate tachygrams, so every accumulator that matters in practice has distinct roots. That fact will come back.

One subtlety you might already be thinking about. Commitment binding says the accumulator opens to one polynomial. It doesn't say that polynomial has the published roots. A prover could slip in an extra root, or drop one, and the queries would lie. So Tachyon checks each accumulator against its published list of tachygrams. The verifier picks a random point r, and computes the product of r minus each tachygram itself, with field operations only, no group work. Then it asks the commitment to open at r to that value. A false polynomial survives with probability at most its degree over the size of the field.

### 2.2 — The action and the stamp

Now the note enters the pool. It's created by an output action, and in Tachyon an action description is just two values: a randomized key, r-k, and a value commitment, c-v. That's it, and spends and outputs share that shape.

Orchard's action carries the nullifier and the note commitment right in the description. Tachyon pulls both out. Nullifiers here won't stay fixed, as we'll see, so they can't live in a static description. Instead, the note binds to its action through r-k's randomizer. Alpha is a PRF of the note commitment and some fresh entropy, theta. For an output, r-k is just alpha times G. For a spend, it's a-k plus alpha times G.

That has a nice side effect. An output's signing key is alpha itself. Creating a note needs no spend authority, because the binding signature already guarantees that outputs are funded. So a hot device can sign outputs with no round trip to custody. And both forms of r-k are uniformly random points, so nobody can tell them apart.

What does an output prove? Its value commitment hides minus v. The value is in range, at most the total money supply. The commitment c-m opens to this note. The key r-k is bound to c-m through alpha. And no published tachygram is zero. Notice what's missing: no anchor, and no epoch. History can't affect an output.

A bundle's actions form a multiset too. Hash each action's r-k and c-v with Poseidon, and accumulate the results, exactly as before. That's the action accumulator.

And now the object everything else orbits: the stamp. A stamp is the bundle's proof-carrying data proof. Its public inputs are the action accumulator, the tachygram accumulator, and an anchor. Alongside, it publishes the tachygrams themselves. Our note's commitment is one of them. And there's a second slot right next to it. Leave it empty for now. We'll come back to it.

One more thing, about where the stamp lives. The transaction ID commits only to effecting data: the action accumulator, the value balance, and a digest of the memo bytes. The stamp sits with the signatures, in the authorization data, which is malleable by design. A relayer can swap a stamp. That changes the witness transaction ID, but not the transaction ID. And the memo is safe from that rewriting, because every signature covers its digest through the sighash.

### 2.3 — The anchor chain

The stamp lands on the anchor chain. This is a hash chain carried in the block header, and it ticks once per stamp. Each tick absorbs the stamp's tachygram accumulator, along with the current epoch number: the new anchor is the hash of the old anchor, the epoch, and the accumulator. So the chain moves at a granularity finer than a block, but coarser than a transaction.

At every transition between epochs, consensus appends one special tick, a sentinel: a domain-separated hash of the last anchor of the old epoch and the new epoch's number. Every epoch, even one with no stamps at all, gets two authenticated boundary posts. And every anchor on the canonical chain belongs to exactly one epoch.

Here's our note's stamp, landing inside epoch five.

Why anchor per stamp, and not per block? Because of validator work. Each stamp already carries its accumulator, checked cheaply against its published list. So a validator just hashes it in. A per-block anchor would make every validator rebuild a block-wide accumulator from scratch: re-accumulate every tachygram, interpolate the product, and commit to it. That's a multi-scalar multiplication on the critical path, which is exactly what client-side validation is meant to avoid.

Our note is in the pool. Now the clock starts moving.

---

## Chapter 3 — Time passes

### 3.1 — Why one nullifier per note has to go

Epoch six begins. Then seven. Our note sits there unspent, and its owner wants it to stay spendable. That means keeping its exclusion proof current, because every stamp that lands is new history the proof has to cover.

Nobody wants their wallet online for that. So you hand the job to a service, an oblivious syncing service, or O-S-S. It watches the chain, and keeps your proof up to date.

But here's the problem. To prove a nullifier is absent from history, the service has to know the nullifier. And whoever knows your nullifier recognizes your spend the moment it lands on chain. The service could tell exactly when this note gets spent. That's a privacy disaster.

Tachyon's fix is to let the nullifier evolve. A note gets a different nullifier in every epoch. The value you share with the service for epoch six is unlinkable to the value you reveal when you spend in epoch nine.

If you've worked on Zcash, you'll notice what that costs. It breaks an invariant as old as Zerocash: one note, one globally unique nullifier. So Tachyon now owes us two things. A new way to derive nullifiers, and a new rule against double spending. The derivation comes next. The rule comes when we reach the validator.

### 3.2 — The derivation, and two nullifiers per spend

The ideal is a deterministic function of three inputs: the nullifier key n-k, the note's psi, and the epoch, e. Its outputs should look random, bind both the spending authority and the note, and stay unlinkable across epochs to anyone without n-k.

A constrained PRF would let you hand the service a key that only works for a range of epochs. But the known candidate, built from a GGM tree, is expensive in a circuit. Tachyon takes a simpler route. The user derives the nullifiers, and proves them. The service gets nothing but bare pairs: an epoch, and a nullifier value. No evidence linking them to any note at all. A real syncing request could just as well be a decoy list. The binding back to the note happens later, on the wallet's side.

Concretely, the wallet first derives a per-note master key, m-k, as a Poseidon hash of n-k and psi. That's psi doing its job. Then one Poseidon permutation of m-k squeezes out a whole window of nullifiers at once, as many as the sponge's rate. With rate four, one permutation gives epochs four through seven, and the next gives eight through eleven. From here on, we'll just write the nullifier at epoch e as f of m-k, at e.

Security fits in one line. Any nullifier you haven't revealed stays indistinguishable from random. That's what carries balance, privacy against the sender, who made the note but never learns n-k, and unlinkability across epochs, delegation included. A service holds a list, and nothing beyond that list.

Now a timing problem. Say a spend proves only the nullifier for the current epoch, e. It waits in the mempool, and the epoch ticks over to e plus one. Now the proof is stale, and nobody else can refresh it. Not the miner, and not the service, which never learns spend-time nullifiers. So every spend reveals two nullifiers: the one for epoch e, and the one for e plus one.

And remember that empty slot next to our note's commitment? An output fills it with a dummy tachygram, the hash of random bytes. Without it, a spend would show two tachygrams and an output just one, and counting tachygrams against actions would reveal how many of each a bundle has. With the padding, every action carries exactly two.

### 3.3 — The ranged nullifier commitment

Now for the first real piece of math. Here's the situation. The wallet has derived nullifiers over a range of epochs, R, from four up to twelve. The service has tested a subrange, S: epochs six, seven, and eight. And it has committed to what it tested. Eventually the wallet has to prove that every pair the service tested is one it derived itself, at the same epoch index. And both sides build their commitments a little at a time, across many proof steps.

A vector commitment would do this. But the known schemes with subvector openings live on RSA groups or on pairings, and neither is friendly to our circuits. One observation gets us out. In a standard vector commitment, the prover can commit to anything, so the scheme has to defend against that. Here, every update to a commitment is itself proven correct against its running value. Honest committing is enforced, and that opens up the design space.

⟨pause⟩

So encode each pair as a polynomial factor that binds both position and value. For epoch i, with nullifier n-f-i, take i plus one, times X, plus n-f-i. Cube that, and subtract a constant, c. ⟨pause⟩ Multiply these factors over the whole range, and you have a commitment to an indexed multiset. Appending the next epoch is one more multiplication, so the range can keep growing, with no fixed endpoint.

Containment is division. The wallet exhibits a quotient, q, so that its product equals the service's product times q. All three commitments are fixed before a random challenge, r, and the check is one identity at one point. That's Ragu's query port doing real work for the first time.

Why is this sound? ⟨pause⟩ Our field has p equal to one, mod three, so we can fix c equal to two, a public non-cube. Then Y cubed minus c is irreducible, and so is every invertible affine substitution of it, since i plus one is never zero. In the field with thirteen elements you can see it directly: the cubes are one, five, eight, and twelve, and two isn't among them. With unique factorization, the only way to forge is for two different pairs to produce the same factor. That happens only when they differ by a nontrivial cube root of unity, omega. But epochs are below two to the thirty-two, and omega is an enormous field element. That collision can't occur.

One caution. Multiplication is commutative, so division proves inclusion, not order. Order and contiguity come from counters, and from sentinel endpoints, checked as each side is built. Remember that word. The service is going to advance from sentinel to sentinel.

---

## Chapter 4 — Exclusion at scale

### 4.1 — The epoch accumulator, and the wall

So the service has to prove that our nullifier for epoch six never appeared anywhere in epoch six. How?

The naive way tests it against every stamp's accumulator in the epoch. But union is multiplication. So multiply all of the epoch's stamp polynomials into one epoch accumulator, e of X, whose roots are every tachygram published that epoch. The service proves it correct against the anchor chain with random-point checks. And since those queries are served by the folding scheme rather than a step circuit, e of X can have as high a degree as the commitment scheme allows. The work is linear in the epoch, but it's paid once, and shared.

Now run the numbers. A modest one hundred transactions per second, all two-in, two-out, over a two-week epoch, gives more than four hundred and eighty million tachygrams. Our polynomial commitment uses a Bulletproofs-style inner product argument, and its verifier is linear in the degree. A single verification would take more than sixteen minutes. That doesn't ship.

So here's the target. Prove non-membership over a whole epoch, at an amortized cost sublinear in its size, with no huge polynomial anywhere near the query.

### 4.2 — Bucketing by an address the element computes itself

The idea is to split the epoch into buckets, so a query only has to look in one of them. That works if the value being queried can work out its own bucket, from nothing but itself. Then it belongs to exactly one bucket, and if it ever appeared in the epoch, it has to be in there. Non-membership over the whole epoch becomes one opening, against one small bucket.

So we need an address that a field element computes from itself, that splits sets evenly, and that's cheap to prove in a circuit. Number theory has exactly that.

⟨pause⟩

Take a prime field, and set zero aside. The remaining elements split exactly in half. Half of them are squares, the quadratic residues. Half are not. In the field with thirteen elements, the squares are one, three, four, nine, ten, and twelve.

Proving that x is a square takes one constraint: hand the circuit a root, y, and check that y squared equals x. Proving that x is not a square uses a classic flip. Multiplying by a non-square swaps the two classes. Watch: multiply everything by two, and the colors trade places. So fix a public non-residue, c, and then y squared equals c times x certifies that x is a non-square. Again, one constraint.

Now shift everything by an offset, R, and ask the same question about x plus R. That's a QR discriminant. One discriminant cuts any fixed set roughly in half. Use k of them, and every element gets a k-bit profile, sorting the field into two to the k classes of nearly equal size, all computed from x alone.

One edge case. If x equals minus R, the shifted value is zero, which is neither a square nor a non-square. By convention, it goes to the residue side. And that has to be enforced, not just stated. A claimed non-residue bit also needs a witness that x plus R is nonzero. Otherwise minus R could take the non-residue branch, with a square root of zero.

### 4.3 — The batched QR test, and one decomposition

One element at a time is cheap. But we need to certify a whole bucket. The polynomial view makes that easy.

Take a bucket's accumulator, f, the product of X minus x-i over its members, and suppose every member is a square. Remember that consensus refuses duplicates, so the roots are distinct. That means we can interpolate a polynomial, g, through the points x-i, y-i, where each y-i is a square root of x-i. ⟨pause⟩ Now g squared minus X vanishes at every member. So f divides it, and the quotient, h, is the witness. The prover commits to g and h. The verifier throws a random point, r, and checks that g of r, squared, minus r, equals f of r times h of r. One identity, at one point, certifies that every root of f is a square. The non-residue version carries the constant c, and an offset R just replaces X with X plus R.

That's the only new algebra we need. Now let's use it to split a bucket.

Under a discriminant R, split f into two pieces: q-zero, holding the non-residues, and q-one, holding the residues. Four checks at a random point keep that split honest. First, decomposition: f equals q-zero times q-one, so no root was added, and none was dropped. Second, every root of q-one is a residue. Third, every root of q-zero is a non-residue. And fourth, q-zero at minus R is nonzero. That last one enforces the convention. q-zero is a product of linear factors, so a nonzero value at minus R means minus R isn't one of its roots. Together with the first check, if minus R is in the bucket at all, it's forced into q-one.

### 4.4 — Routing: decompose, merge, and a jagged frontier

Now build buckets for a whole epoch, at scale. An epoch doesn't arrive all at once. It streams in, stamp by stamp. So while epoch six is live, the service rolls consecutive stamps into bounded summaries: one product polynomial each, plus the anchor range it covers. A summary grows by checking, at a random point, that the new product is the old one times the next stamp's accumulator, and by absorbing that stamp into its anchor. A summary never crosses a sentinel. Each one becomes a root bucket, with an empty profile.

Then the service routes. A routing round does two things. It decomposes every bucket under the next discriminant, which roughly halves each one. Then it merges neighbors that ended up with the same profile, as long as their union still fits in a bucket. Merging is just the union check again, so there's nothing new to trust.

Now track the anchor ranges underneath. Decomposition keeps a bucket's range. A merge joins two adjacent ranges into one. So round by round, many partial pieces of a profile become one bucket that spans the entire epoch. The rounds run in parallel, they stream, and they run while the epoch is still live.

Some profiles lag behind. Fluctuations in size leave a few of them still in pieces, and only those get another, partial round. That leaves a jagged frontier: final profiles at different depths, together partitioning the field, each one covering the whole epoch from sentinel to sentinel. Once the epoch closes, a seal step checks both sentinels.

In the proof tree, each split is one step that proves the product and the minus-R check, followed by two descents. Each descent returns one side, and checks the purity of the other side. Derive both children, and both buckets are certified pure.

What about an attacker who grinds tachygrams to overload a single bucket? The discriminants have to stay unpredictable while tachygrams are being chosen. So each service samples its first offset privately, steps it up by one each round, and reveals it only after the epoch closes. That choice affects balance, never soundness. The proofs certify any choice, and a badly balanced routing can simply be ignored in favor of an honest service's.

And even at fifty thousand transactions per second, a thirty-two bit profile has room to spare.

### 4.5 — The evidence tree

Serving one proof per final bucket would be a lot to keep around. So after the epoch closes, the service folds any set of final-bucket proofs into one evidence tree. It's a Poseidon Merkle tree with arity four, matching the sponge's rate. Each leaf binds the epoch, its two sentinels, the first discriminant, the bucket's profile and depth, and the bucket's commitment. The output is a single root. The tree doesn't have to include every bucket. Even a single leaf is valid, because each leaf is already a proven full-epoch bucket.

Queries go like this. For membership, authenticate a leaf, and check that the value is a root of its bucket. No profile is needed, because every bucket divides the epoch's polynomial, so any root is a tachygram from that epoch. That's how our note's commitment will be found in epoch five. For non-membership, re-derive the discriminants, check that the value's bits select this leaf, and check that the bucket is nonzero there. That's how our nullifier for epoch six will be cleared.

Compare that with the wall. A sixteen-minute linear verification became at most thirteen hashes, and one opening of bounded degree. The routing ran once, in flight, and building the tree is the only work left after the epoch closes. One evidence tree per epoch, built once, shared by every wallet.

---

## Chapter 5 — The proof tree

### 5.1 — Steps, headers, bridges

We've collected every ingredient. So what does the actual proof look like?

A spend has to satisfy a long statement. So does an output, and so does the bundle that glues them together. You don't prove those in one piece. You break them into steps. A step is a bounded circuit. It takes up to two child proofs and some private witness, checks part of the statement, and emits a new proof whose public output is a header: the data, in proof-carrying data. Headers flow upward, from children to parents.

A parent bridges its children. It loads both headers, and checks that the fields which have to agree really do: the same note commitment, matching sentinels, the same epoch. A decomposition is sound exactly when there's enough bridging.

From here on, three colors. Gold steps run on the wallet, and see the note. Cyan steps run on a service, and see only opaque values. And white is shared evidence that anyone can use: anchor chain segments for the active epoch, and evidence trees for closed ones.

### 5.2 — Same-epoch spend: the base tree

Start with the simplest spend. It's now epoch nine, and the wallet also received another note earlier in this same epoch. Spending a note in the epoch it was created needs no exclusion proof at all. It didn't exist before, so there's nothing to exclude.

The first step, SpendableInit, takes the creation stamp's data as witness, proves that the note's commitment is a root of that stamp's accumulator, and computes the anchor that stamp produced. Out comes a header that says: this note is spendable, with its commitment, its epoch, and that anchor. The wallet can build it as soon as the creation block is final, and cache it, or even hand it to a hardware wallet early.

Then SpendBind opens the note. It checks the payment key against a-k and n-k, recomputes the commitment, checks the value range, binds r-k through alpha, and derives the two nullifiers, for epochs nine and ten. It emits a stamp for this one action. An output gets its stamp from a single step, OutputSeed, which covers the whole output statement. And StampMerge joins stamps by multiplying their accumulators. Union is multiplication, again.

Finally, StampLift. It consumes a shared anchor chain segment, and moves the stamp to a later anchor. That segment contains no sentinel, so a lift can never cross into another epoch. And the lift isn't just a convenience. Without it, the stamp's anchor would point right at the note's creation. Lifting is part of what keeps the spend unlinkable.

Every spend ends this way: SpendBind, merge, lift. The only question is what feeds SpendBind when the note is older.

### 5.3 — Past-epoch spend: our original note

Now our original note: born in epoch five, spent in epoch nine. Its history splits into three parts.

First, the epoch it was born in. This part stays on the wallet. The wallet opens epoch five's evidence tree twice: once at the bucket for its epoch-five nullifier, and once at the bucket for its commitment. NoteUnspentInit opens the note with its keys, re-derives that nullifier, checks that its profile selects the bucket, and proves it's absent. SpendableReinit then joins that with the commitment's membership opening, for the same epoch and the same sentinels. Out comes a fully established spendable header, valid from the start of epoch six.

Second, epochs six through eight. Here the work splits. On the service, UnspentSeed starts an empty range. Then each UnspentLift consumes one evidence-tree opening, proves one opaque nullifier absent, multiplies one cubic factor into the service's commitment, and advances from one sentinel to the next. It can't skip an epoch, repeat one, or reorder them. And the service never learns which note this is.

Meanwhile, the wallet derives its own range. NoteSeed opens the note once, and emits its master key header. Each NullifierDerive squeezes out one window: four up to eight, then eight up to twelve. NullifierFuse joins them into one commitment, over four to twelve.

Third, the join. UnspentBind checks that the service's range is nonempty and sits inside the wallet's, and then runs the division from before: the service's product divides the wallet's. That's the moment the delegated, note-independent work becomes about this note. SpendableLift then seams the result onto the spendable header, with sentinel equality at the seam. And now the note is spendable through the start of epoch nine.

From there, it's the same as before. SpendBind derives the nullifiers for nine and ten. StampMerge joins this stamp with the other spend and the outputs, and one StampLift moves the whole thing to the transaction's target anchor, in epoch nine.

If the wallet uses several services for different ranges, UnspentMerge joins adjacent results before binding, checking that one's end sentinel is the other's start.

And the privacy bottom line. A service sees opaque values and ranges it can't tell from decoys. It never sees the commitment, the note, another service's work, or where the spend lands.

---

## Chapter 6 — Landing

### 6.1 — The validator and the two-epoch window

So what's left for the validator? Per stamp, four checks. The target anchor is in canonical history, and its epoch is either the current one, or the one before. The action accumulator matches the actions, and the tachygram accumulator matches the published list, using the cheap random-point check. And one proof verifies. Balance and signatures work exactly as in Orchard.

Let's be precise about what the stamp claims. It proves exclusion strictly before the target epoch. For our spend, that means up to the sentinel that opens epoch nine. The target anchor is not an exclusion endpoint. Duplicates inside epoch nine are consensus's job. That's why every spend targeting epoch nine has to publish its nullifier for nine.

So here's the new double-spend rule. Consensus keeps one duplicate window, holding every tachygram from the current epoch and the one before. Candidates are processed in a fixed order, each one checked, then inserted.

Why that shape? Think like a double spender. Remember the grace period we allowed, so that a transaction waiting in the mempool doesn't go stale: a stamp targeting epoch nine is still accepted during epoch ten. So the attacker builds two spends of the same note. The first targets epoch nine, and is held back until epoch ten begins. The second targets epoch ten. Both proofs are honest. The second one proves that its nullifier for epoch nine never appeared in epoch nine, and that's true, because the first spend didn't land in epoch nine. It landed in ten.

If each spend published only its own epoch's nullifier, the first would reveal the value for nine, the second the value for ten, and nothing would collide. That's why every spend also publishes the next epoch's nullifier. The first spend reveals nine and ten. The second reveals ten and eleven. They collide on ten.

And the window? The attacker can push one step further, and hold the second spend back until epoch eleven. Now the colliding values land in different epochs, ten and eleven. A window over the current and the preceding epoch still holds both, and catches it. Anything older falls inside the history a stamp already proves excluded.

So the adjacent pair and the two-epoch window come as a set. Together, they close the gap the grace period opened.

And look at the set consensus has to hold now. Not all of history. Two epochs. Bounded, forever.

### 6.2 — Aggregation, in one breath

Finally, aggregation, in one breath. A miner, or anyone else, takes finished stamps from different transactions, lifts them to a common anchor in the same epoch, never across a sentinel, and merges them with the very same StampMerge: union the multisets, multiply the accumulators, fuse the proofs. The aggregate has the same shape as any stamp, so it can merge again. Each covered transaction drops its own stamp for a reference to the aggregate's witness transaction ID. Balance and signatures stay with each transaction. Only proof verification is shared, and that's an incentive to aggregate.

---

## Chapter 7 — The other half

### 7.1 — Addresses, tags, and private retrieval

The cut we made at the start left the payment protocol in charge of delivering notes. Here's a sketch of the leading design, being built by ValarGroup.

An address is a pair: the payment key, and an ML-KEM encapsulation key, both fresh for each sender. Why not Orchard-style diversification? Because it isn't quantum-private. All those diversified keys share one incoming viewing key, and anyone who can break one discrete log recovers it, exposing every incoming note, past and future. ML-KEM is post-quantum, but it has no analogue of many unlinkable keys sharing one decryption key.

So discovery needs a different shortcut, and that's tags. Each encrypted memo carries a short tag. The first-contact tag is a hash of the encapsulation key, so the recipient can find the handshake before it knows the shared secret. Every later tag is a hash of the shared secret and a counter: predictable to the two parties, opaque to everyone else, and fresh for every note, since tags appear on chain.

Instead of trial-decrypting the whole chain, the wallet looks up its tags with private information retrieval, which reveals nothing about the query. The same machinery includes a tachygram database, which privately supplies the stamp and anchor data the spend proof needs.

And Faerie gold, as promised. Tachyon's notes have no canonical position, so the shielded protocol can't bind psi the way Orchard binds rho. Instead, the wallet checks each incoming note's nullifier at a fixed reference epoch against the notes it already holds. A reused psi collides right there.

---

## Chapter 8 — Quantum posture, and the cascade

### 8.1 — Private today, sound after an upgrade

One question left: the quantum one. Tachyon's stance fits in a sentence: private today, sound after an upgrade. The asymmetry is deliberate. Privacy has to hold retroactively. Today's chain can be harvested now and decrypted whenever the hardware arrives, so anything guarding privacy must already be post-quantum. Soundness, meaning nobody forges and nobody steals, only matters at spend time, so it can wait for a coordinated network upgrade.

Audit today's chain against that bar. Owner fields and note commitments: Poseidon. Nullifiers: P R F outputs. Memos: M L KEM, plus symmetric encryption. All of it quantum-safe already. The discrete-log survivors are three: value commitments, randomized keys, and the binding key. The value commitment is perfectly hiding, so there's nothing to decrypt. And the randomized key? A quantum computer takes its discrete log and recovers a s k plus alpha, where alpha is a fresh P R F mask. A random-looking scalar, linkable to nothing. So the full quantum power against today's Tachyon is forgery. Theft, not exposure. Which is precisely the half that's allowed to wait.

When the upgrade comes, two swaps. First, authorization. Re-randomization is intrinsically discrete-log, and no post-quantum signature does it. The replacement recovers unlinkability from zero knowledge instead: prove, in circuit, that you know a valid post-quantum signature. Schemes like CAPSS are built to be cheap exactly there. Authorization then folds into the transaction's PCD proof, the randomized key leaves the action description entirely, and the note-to-action binding it used to carry through alpha gets re-established as an explicit constraint in the statement. Second, the proof system itself: Ragu's discrete-log commitments swap for lattice-based folding. The recursive structure that makes spendability proofs incremental survives, and the hardness assumption underneath changes. The concrete lattice constructions are active research. The honest status: to be determined, by design, not blocked.

### 8.2 — Outro: the decision cascade

Run the whole design backward, and it compresses into one breath. The nullifier set couldn't be pruned, so validation moved to the client. Clients can't sync alone, so syncing got delegated. Delegation would leak the spend, so nullifiers evolve. Evolving nullifiers would go stale in the mempool, so actions carry a pair, and consensus keeps a two-epoch window. Per-stamp history needed composing, so one accumulator, with union by multiplication. Its degree exploded, so quadratic residues bucket each epoch. And none of it would be affordable alone, so the expensive evidence is built once, proven once, and shared by everyone.

Each decision is forced by the one before it. That's the takeaway: Tachyon isn't a bag of tricks. It's one principle, the client proves and consensus checks, followed to its conclusions.

Everything in this video is written down, in much more detail, in the Deep Dive at tachyon dot z dot cash, alongside Sean's posts and the Ragu book. The implementation is open, on our GitHub. Both links are right below. Thanks for watching.

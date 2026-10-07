# Scaling Zcash with Tachyon — v2 Narration (Draft 2, Sean's voice)

> Verbatim narration, one section per scene, matching `scenes.md` Draft 3.
> Written to be read aloud, by Sean or by a clone of Sean's voice.
>
> Pronunciation: Sean's own recording is the reference, not a respelling. Clips cut
> from his chapter 0 take: `audio/samples/pron/sean_tachyon_{1,2,3}.wav` and
> `sean_ragu_{1,2}.wav`. "tachygram" follows his "Tachyon"; "psi" is "sigh". Short
> key names are written hyphenated as they should be spoken ("r-k", "n-k", "c-m").
> Greek letters are spelled out. Step names (SpendBind, StampLift, …) are written as
> single CamelCase words.
>
> Pauses come in two kinds:
> - `⟨pause⟩` is a short breath (~0.6 s), used only around math-heavy beats.
> - `⟨pause: what's on screen⟩` is a held beat. The voice stops while the named
>   visual plays, and the animation decides how long it lasts (typically 1–3 s). The
>   label is an anchor for syncing the animation to the script, and is never spoken.
>
> Voice, applies to every line:
> 1. Collaborative, not commanding (PR #2). "We" and "let's" do things; the narration
>    never barks imperatives at the viewer ("Take…", "Multiply…", "Notice…").
> 2. No filler (PR #2). Cut lines that restate what was just said or shown, and witty
>    cappers after a point has landed ("Theft, not exposure"). Connective words are not
>    filler: rule 4 wants them.
> 3. Let the picture talk (PR #2). When an animation is doing the explaining, the
>    narration stops for it (a held `⟨pause: …⟩`) instead of talking over it.
> 4. Talk like Sean (from his chapter 0 recording, `audio/samples/chapter0.transcript.md`,
>    and his ZconVI talk on Zcash scalability, `audio/samples/youtube/zconvi_sean.transcript.md`):
>    - **Full sentences, never telegrams.** Every clause gets its verb. Not "On the
>      left, note commitments." but "On the left are note commitments." Not "Per stamp,
>      four checks." but "For each stamp, there are four checks."
>    - **Chain clauses with plain connectives** ("and then", "and that's", "so",
>      "but") instead of stacking short sentences or colons. Two or three ideas per
>      sentence is normal.
>    - **Gloss a new term with "which is" / "which are"**, in passing: "Ragu, which is
>      a proof-carrying data system…", "epochs, which are long stretches of blocks".
>    - **Light hedges and softeners, sparingly**: "roughly", "really", "just", "a
>      little bit", "pretty", "actually", "let's say". About one every few sentences,
>      never two in a row.
>    - **Framing phrases that set up a turn**: "The trick is that…", "And to make
>      matters worse…", "For performance, as we'll see, this is pretty critical."
>    - **Progressive and future forms where he'd use them**: "the set is sitting in
>      memory", "this is running on Ragu", "we're going to follow one note".
>    - **Concrete actors** ("validators", "the spender") over abstractions ("a node"),
>      and no quoted first-person voice ("my nullifier appears nowhere").
>    - **Open on a statement, not a teaser question.** Questions are fine mid-scene
>      when they set up the answer, but the scene starts by saying something.
>    - **Pace.** He talks fast (~200 wpm while speaking, in both recordings) and lets the
>      pauses do the breathing: ~0.5–1 s between sentences, ~1.5–2 s between paragraphs.
>    - **Turn openers**: "So…", "Now…", and "Well, …" to answer his own question ("Why
>      would you want this? Well, …"). Not every sentence; one per paragraph at most.
>    - **His stock phrases, sparingly**: "of course", "basically", "for example", "by the
>      way", "in other words", "it turns out". At most one per paragraph.
>    - **Tell it as a story about the viewer's wallet**: "your wallet hands the job off",
>      "we spend our note". Descriptive "you", never imperative.
>    - **Own the names he coined**: "I call this an oblivious syncing service".
>    - **An occasional tag question** ("…, right?") when a point should feel obvious.
>    - **Not carried over** from the talk: "um", "uh", false starts, and repeated words.
>      Those are live-speech artifacts, and a cloned voice would learn them.

---

## Chapter 0 — Prologue

### 0.1 — Two sets, two fates

Every shielded pool in Zcash has two sets, and they grow at roughly the same rate, which is one entry for every note that's created, and then one for every note that's spent. ⟨pause: both sets grow side by side⟩

On the left are note commitments, and these live in an append-only Merkle tree. To keep appending, validators only really need the tree's frontier, so, like, one hash per level, but everything else can actually be pruned today. And the long-term cost of this tree is logarithmic. ⟨pause: the tree prunes down to its frontier⟩

But on the right are nullifiers. Every transaction has to show that its input nullifiers haven't appeared before on chain, and that's an exclusion test against all of history, so the whole set is sitting in memory on the critical path of every validator.

And to make matters worse, at Visa-level throughput, this set's growing by about five hundred gigabytes a day, and nothing in it can ever be thrown away. ⟨pause: counter rolls to 500 GB / day⟩ A nullifier from ten years ago still has to block a double spend today, and that's a fundamental scaling limitation. It's a linearly growing set that nobody can prune.

### 0.2 — The thesis, the black box, and our protagonist

Tachyon's solution to this starts from one principle, which is to move validation off the critical path of consensus and onto the client whenever we can. Consensus keeps only nullifiers from the recent history, and then everything older than that gets cut loose. ⟨pause: the grid is scissored, older history flies to wallets⟩ The spender just has to have a proof that their nullifier doesn't appear anywhere in that older history.

The trick is that that proof can't be made once and forgotten. Every new block has more history that it has to cover, so it's built incrementally as proof-carrying data, and it's extended a little each time as the chain moves.

All of this is running on Ragu, which is a proof-carrying data system in the Halo lineage, over the Pasta curves with no trusted setup. We'll treat it as a black box with two parts. The fuse part takes two proofs and a little bit of new work, and then hands back a single proof that covers all of it. The query part answers evaluations. We commit to a polynomial, we name a point, we get back its value. ⟨pause: fuse and query parts animate⟩ Ragu is designed to expose these evaluation claims directly and to fold them into the proof system's own claims, so that you're not paying for them in circuit constraints. For performance, as we'll see, this is pretty critical.

Time in Tachyon is cut into epochs, which are long stretches of blocks. To go through the design, we're going to follow one note. It's born in epoch, let's say, five, and it's spent in epoch nine. ⟨pause: note card docks, epoch rail draws itself⟩ And every piece of Tachyon is going to show up exactly when this note needs it.

---

## Chapter 1 — Ownership, stripped down

### 1.1 — Why Zcash keys got complicated

Before the note can exist, it needs an owner.

The first Zcash shielded protocol, Sprout, which followed the original Zerocash paper, really only needed two keys, which were a payment key and an encryption key. Orchard's key diagram is a lot more complicated than that, so why is that? ⟨pause: Orchard's key diagram beside Sprout's two keys⟩

The first reason is that proving and authorizing turned into different roles. Hardware wallets, for example, are pretty resource-constrained, and they can't really run a prover. So from Sapling on, authorization became a signature that's made outside the proof. But a signature under a fixed key would link every spend by the same owner, so the key gets re-randomized each time. a-k sits in the secret witness, and the instance carries r-k, which is a-k plus alpha times G.

The second reason is that the address is actually doing two jobs at once. It declares who owns the note, and it also carries the transmission key, which the sender uses to encrypt the note's secrets on chain. Diversified addresses exist for that second job. They refresh the transmission key for each sender, while a single incoming viewing key, i-v-k, can still detect every incoming note.

The third reason is selective disclosure. You might want to show your incoming or outgoing flows to, say, an auditor, without handing over spend authority, and that's what brings in the outgoing viewing key and the rest of the viewing family.

So which of these keys are actually enforcing ownership? Well, it turns out it's only two of them. The nullifier key, n-k, derives nullifiers, and the authorization key, a-k, authorizes spends. Everything else is really serving transmission and viewing.

### 1.2 — The cut

Tachyon cuts along exactly that line. ⟨pause: the blade cuts the key tangle into two boxes⟩

On one side sits the shielded protocol, and its job shrinks to the minimum the pool needs, which is to bind every note to an owner and make sure that only that owner can spend it. On the other side sits the payment protocol, which owns everything about getting a note to its recipient, so addresses, memo encryption, note discovery, and viewing.

The owner field of every note becomes a payment key, p-k, which is a binding commitment to the pair a-k and n-k. Because it's built from a hash, that gives us two things. It's succinct, and it's quantum-recoverable today. Handing out a-k, which is a Schnorr verification key, to every sender is a harvest-now, decrypt-later risk, but a hash commitment to it is not.

The shielded protocol doesn't even constrain how a-k and n-k are derived. It only requires that they look like freshly sampled keys, and the derivation paths are really the wallet standard's business.

The security properties split along the same line. The shielded core keeps ledger indistinguishability, balance, note privacy, and spend unlinkability against an attacker who holds just your payment key. Full unlinkability against someone who holds your viewing key, and resistance to Faerie gold, become the payment protocol's job.

The chain's role splits too. Besides maintaining the pool, it becomes a data-availability layer. Encrypted payment data still rides on chain, but the shielded protocol just carries those bytes without ever parsing them.

Of course, a couple of familiar pieces don't change at all. Spend authorization is still RedPallas, with the same re-randomized key, and value balance is still the binding signature over homomorphic value commitments, exactly like in Sapling and Orchard.

So what the cut really buys us is a smaller surface for each upgrade, cleaner security assumptions to audit, and two halves that can evolve in parallel.

### 1.3 — The note

With an owner in hand, let's look at the note itself. A Tachyon note has four fields, which are the payment key p-k, the value v, a field called psi, and a commitment trapdoor, r-c-m.

Its commitment, c-m, commits to p-k, v, and psi, under the trapdoor r-c-m. It's built from Poseidon, which is a sponge hash, so it's purely symmetric.

Sapling and Orchard use variants of the Pedersen commitment, which rest on discrete log, and Orchard actually has to put extra rules on how wallets derive r-c-m to stay quantum-recoverable. Tachyon's commitment doesn't need any of that.

That leaves psi, which is a pseudorandom identity for the note, derived from the wallet's master key. And as we'll see, every nullifier this note will ever have hangs off of it.

So now the note exists. Where does its commitment go?

---

## Chapter 2 — Birth

### 2.1 — A set as the roots of a polynomial

Let's take a set, say the numbers two, seven and eleven, in the field with thirteen elements. We build the polynomial whose roots are exactly those members, so X minus two, times X minus seven, times X minus eleven. ⟨pause: roots drop on the field line, product builds factor by factor⟩ Committing to it gives us an accumulator.

Membership is just a single evaluation. Seven gives zero, and five gives something nonzero, so five isn't in the set. Both of these answers come from Ragu's query part.

Right now, every pool keeps two different structures, because the two jobs look different. There's a Merkle tree for the membership of commitments, and a set for the non-membership of nullifiers. But if one structure can answer both questions at the same cost, why keep them apart at all? Well, Tachyon doesn't. ⟨pause: Merkle tree and nullifier grid dissolve into one accumulator⟩ Every member of this one accumulator is a tachygram, which is a thirty-two byte blob that might be a note commitment, or might be a nullifier, and on chain you can't tell which.

Set operations become polynomial operations. Inserting an element multiplies by its factor, and removing one divides it out. The union of two sets is the product of their polynomials, and there's no requirement that they be disjoint. And a subset is a divisor, so containment is exact division. Every one of these can be checked at a single random point. ⟨pause: the dictionary completes⟩

Evaluation ignores multiplicity, so strictly speaking this is a multiset. But consensus refuses duplicate tachygrams, so every accumulator that matters in practice has distinct roots.

Now, there's one subtlety here. Commitment binding says that the accumulator opens to one polynomial, but it doesn't say that polynomial has the published roots. A prover could slip in an extra root, or drop one, and then the queries would lie. ⟨pause: a ghost root sneaks in, the probe lies⟩ So Tachyon checks each accumulator against its published list of tachygrams. The verifier picks a random point r, and computes the product of r minus each tachygram itself, using only field operations, so there's no group work. Then it asks the commitment to open at r to that value. A false polynomial survives with probability at most its degree over the size of the field.

### 2.2 — The action and the stamp

Now the note enters the pool. It's created by an output action, and in Tachyon an action description is just two values: a randomized key, r-k, and a value commitment, c-v. Spends and outputs both share that shape.

Orchard's action carries the nullifier and the note commitment right in the description, but Tachyon pulls both of them out. ⟨pause: Orchard's action card morphs into (rk, cv)⟩ Nullifiers here won't stay fixed, as we'll see, so they can't live in a static description. Instead, the note binds to its action through r-k's randomizer. Alpha is a PRF of the note commitment and some fresh entropy, theta. For an output, r-k is just alpha times G, and for a spend, it's a-k plus alpha times G.

A nice side effect is that an output's signing key is alpha itself. Creating a note doesn't need any spend authority, because the binding signature already guarantees that outputs are funded. So, for example, a hot device can sign outputs without a round trip to custody. And both forms of r-k are uniformly random points, so nobody can tell them apart.

So what does an output actually prove? Its value commitment hides minus v, and the value is in range, so at most the total money supply. The commitment c-m opens to this note, the key r-k is bound to c-m through alpha, and no published tachygram is zero. There's no anchor and no epoch in there, because history can't affect an output.

A bundle's actions form a multiset too. Each action's r-k and c-v are hashed with Poseidon, and the results are accumulated just like before, and that's the action accumulator.

Next up is the stamp. A stamp is the bundle's proof-carrying data proof. Its public inputs are the action accumulator, the tachygram accumulator, and an anchor, and alongside that, it publishes the tachygrams themselves. Our note's commitment is one of them, and there's a second slot right next to it that we'll fill in later.

As for where the stamp lives, the transaction ID commits only to effecting data, which is the action accumulator, the value balance, and a digest of the memo bytes. The stamp sits with the signatures, in the authorization data, which is malleable by design. So a relayer can swap out a stamp, and that changes the witness transaction ID, but not the transaction ID. And the memo is safe from that rewriting, because every signature covers its digest through the sighash.

### 2.3 — The anchor chain

The stamp then lands on the anchor chain. This is a hash chain that's carried in the block header, and it ticks once per stamp. Each tick absorbs the stamp's tachygram accumulator along with the current epoch number, so the new anchor is the hash of the old anchor, the epoch, and the accumulator. ⟨pause: beads absorb accumulator chips along the rail⟩ That means the chain moves at a granularity that's finer than a block, but coarser than a transaction.

At every transition between epochs, consensus appends one special tick, called a sentinel, which is a domain-separated hash of the last anchor of the old epoch and the new epoch's number. So every epoch, even one with no stamps at all, gets two authenticated boundary posts, and every anchor on the canonical chain belongs to exactly one epoch.

Here's our note's stamp, landing inside epoch five. ⟨pause: our bead lands in epoch five⟩

You might be wondering why we anchor per stamp, and not per block. It really comes down to validator work. Each stamp already carries its accumulator, which is checked cheaply against its published list, so a validator just hashes it in. A per-block anchor would make every validator rebuild a block-wide accumulator from scratch, which means re-accumulating every tachygram, interpolating the product, and committing to it. That's a multi-scalar multiplication sitting right on the critical path.

---

## Chapter 3 — Time passes

### 3.1 — Why one nullifier per note has to go

Epoch six begins, and then seven. ⟨pause: the now-cursor slides, the proof token ticks at every bead⟩ Our note is just sitting there unspent, and its owner wants it to stay spendable. That means keeping its exclusion proof current, because every stamp that lands is new history that the proof has to cover.

Nobody really wants to keep their wallet online for that, so your wallet hands the job off to a service. I call this an oblivious syncing service, or O-S-S. In other words, it watches the chain and keeps your proof up to date for you.

But there's a privacy problem here, which is that to prove a nullifier is absent from history, the service has to know the nullifier. And whoever knows the nullifier is going to recognize the spend the moment it lands on chain, right? ⟨pause: a flare line snaps from the service to the spend⟩

Tachyon's fix for this is to let the nullifier evolve, so a note gets a different nullifier in every epoch. The value the wallet shares with the service for epoch six is unlinkable to the value it reveals when it spends in epoch nine. ⟨pause: rewind: per-epoch values, the line fails to connect⟩

This breaks an invariant that's as old as Zerocash, which is one note, one globally unique nullifier. So Tachyon now needs two things. One is a new way to derive nullifiers, which we'll get to next, and the other is a new rule against double spending, which comes when we reach the validator.

### 3.2 — The derivation, and two nullifiers per spend

Ideally, we want a deterministic function of three inputs, which are the nullifier key n-k, the note's psi, and the epoch, e. Its outputs should look random, bind both the spending authority and the note, and stay unlinkable across epochs to anyone who doesn't have n-k.

A constrained PRF would let the wallet hand the service a key that only works for a range of epochs. But the known candidate, which is built from a GGM tree, is pretty expensive in a circuit. So Tachyon takes a simpler route. The user derives the nullifiers and proves them, and the service gets nothing but bare pairs of an epoch and a nullifier value, with no evidence linking them to any note at all. In fact, a real syncing request could just as well be a decoy list. The binding back to the note happens later, on the wallet's side.

Concretely, the wallet first derives a per-note master key, m-k, as a Poseidon hash of n-k and psi. Then one Poseidon permutation of m-k squeezes out a whole window of nullifiers at once, as many as the sponge's rate. With a rate of four, one permutation gives epochs four through seven, and the next one gives eight through eleven. ⟨pause: the sponge squeezes four nullifiers per permutation onto the rail⟩ From here on, we'll just write the nullifier at epoch e as f of m-k, at e.

The security argument basically comes down to one property, which is that any nullifier that hasn't been revealed stays indistinguishable from random. That one property carries balance, privacy against the sender, who made the note but never learns n-k, and unlinkability across epochs, even when the wallet delegates.

There's also a timing problem, though. Let's say a spend proves only the nullifier for the current epoch, e. It waits in the mempool, and then the epoch ticks over to e plus one. ⟨pause: a single-nullifier transaction shatters at the sentinel gate⟩ Now the proof is stale, and nobody else can refresh it. The miner can't, and neither can the service, which never learns spend-time nullifiers. So every spend reveals two nullifiers, the one for epoch e and the one for e plus one.

And that's what the empty slot next to our note's commitment is for. An output fills it with a dummy tachygram, which is just the hash of some random bytes. Without it, a spend would show two tachygrams and an output just one, so counting tachygrams against actions would reveal how many of each a bundle has. With the padding, every action carries exactly two. ⟨pause: spend and output become identical two-pip dominoes⟩

### 3.3 — The ranged nullifier commitment

The wallet has derived nullifiers over a range of epochs, R, let's say from four up to twelve. The service has tested a subrange, S, which is epochs six, seven, and eight, and it's committed to what it tested. Eventually the wallet has to prove that every pair the service tested is one it derived itself, at the same epoch index. And both sides are building their commitments a little bit at a time, across many proof steps.

Now, a vector commitment would do this, but the known schemes with subvector openings live on RSA groups or on pairings, and neither of those is friendly to our circuits. In a standard vector commitment, though, the prover can commit to anything, so the scheme has to defend against that. Here, every update to a commitment is itself proven correct against its running value. So honest committing is enforced, and that really opens up the design space.

⟨pause⟩

So let's encode each pair as a polynomial factor that binds both position and value. For epoch i, with nullifier n-f-i, we take i plus one, times X, plus n-f-i, cube it, and subtract a constant, c. ⟨pause⟩ Multiplying these factors over the whole range gives us a commitment to an indexed multiset. Appending the next epoch is just one more multiplication, so the range can keep growing, with no fixed endpoint. ⟨pause: tiles stack one at a time, right end open⟩

Containment is then just division. The wallet exhibits a quotient, q, so that its product equals the service's product times q. ⟨pause: the service's stack lifts out of the wallet's, leaving q⟩ All three commitments are fixed before a random challenge, r, and the check is one identity at one point, through Ragu's query part.

So why is this sound? ⟨pause⟩ Our field has p equal to one, mod three, so we can fix c equal to two, which is a public non-cube. Then Y cubed minus c is irreducible, and so is every invertible affine substitution of it, since i plus one is never zero. In the field with thirteen elements, the cubes are one, five, eight, and twelve, and two isn't among them. ⟨pause: the thirteen-element clock: two is not a cube⟩ With unique factorization, the only way to forge is for two different pairs to produce the same factor, and that happens only when they differ by a nontrivial cube root of unity, omega. But epochs are below two to the thirty-two, and omega is an enormous field element, so that collision never happens.

One word of caution here. Multiplication is commutative, so division proves inclusion, but not order. Order and contiguity come from counters, and from sentinel endpoints, which are checked as each side is built.

---

## Chapter 4 — Exclusion at scale

### 4.1 — The epoch accumulator, and the wall

So the service has to prove that our nullifier for epoch six never appeared anywhere in epoch six. How does it do that?

The naive way is to test it against every stamp's accumulator in the epoch. But union is multiplication, so we can multiply all of the epoch's stamp polynomials into one epoch accumulator, e of X, whose roots are every tachygram published that epoch. The service proves it correct against the anchor chain with random-point checks. And since those queries are served by the folding scheme rather than a step circuit, e of X can have as high a degree as the commitment scheme allows. The work is linear in the epoch, but it's paid once, and shared.

Let's run the numbers on that. A pretty modest one hundred transactions per second, all two-in, two-out, over a two-week epoch, gives us more than four hundred and eighty million tachygrams. Our polynomial commitment uses a Bulletproofs-style inner product argument, and its verifier is linear in the degree, so a single verification would take more than sixteen minutes. ⟨pause: degree counter spins to 4.8 × 10⁸, stopwatch passes 16:00⟩

So the target is to prove non-membership over a whole epoch, at an amortized cost that's sublinear in its size, without any huge polynomial anywhere near the query.

### 4.2 — Bucketing by an address the element computes itself

The idea is to split the epoch into buckets, so that a query only has to look in one of them. That works if the value being queried can work out its own bucket, from nothing but itself. Then it belongs to exactly one bucket, and if it ever appeared in the epoch, it has to be in there. So non-membership over the whole epoch becomes one opening, against one small bucket. ⟨pause: e(X) shatters into buckets, a query homes in on one⟩

So we need an address that a field element computes from itself, that splits sets evenly, and that's cheap to prove in a circuit. And quadratic residues turn out to be exactly that.

⟨pause⟩

In a prime field, if we set zero aside, the remaining elements split exactly in half. Half of them are squares, which we call the quadratic residues, and half of them are not. In the field with thirteen elements, the squares are one, three, four, nine, ten, and twelve. ⟨pause: the clock: residues cyan, non-residues amber⟩

Proving that x is a square takes one constraint. The circuit gets a root, y, and checks that y squared equals x. Proving that x is not a square uses a classic trick, which is that multiplying by a non-square swaps the two classes. ⟨pause: multiplying by two swaps the colors⟩ So with a fixed public non-residue, c, y squared equals c times x certifies that x is a non-square, and again, that's one constraint.

Now let's shift everything by an offset, R, and ask the same question about x plus R. That's what we call a QR discriminant. ⟨pause: sliding R recolors the ring⟩ One discriminant cuts any fixed set roughly in half. With k of them, every element gets a k-bit profile, which sorts the field into two to the k classes of nearly equal size, all computed from x alone.

There's one edge case. If x equals minus R, the shifted value is zero, which is neither a square nor a non-square. By convention, it goes to the residue side, and that has to be enforced, not just stated. So a claimed non-residue bit also needs a witness that x plus R is nonzero. Otherwise minus R could take the non-residue branch, with a square root of zero.

### 4.3 — The batched QR test, and one decomposition

One element at a time is cheap, but we need to certify a whole bucket, and the polynomial view makes that pretty easy.

Let's take a bucket's accumulator, f, the product of X minus x-i over its members, and suppose every member is a square. Consensus refuses duplicates, so the roots are distinct, and that means we can interpolate a polynomial, g, through the points x-i, y-i, where each y-i is a square root of x-i. ⟨pause⟩ Now g squared minus X vanishes at every member, so f divides it, and the quotient, h, is the witness. The prover commits to g and h. The verifier throws out a random point, r, and checks that g of r, squared, minus r, equals f of r times h of r. ⟨pause: both sides print the same element⟩ So one identity, at one point, certifies that every root of f is a square. The non-residue version carries the constant c, and an offset R just replaces X with X plus R.

Now let's use that to split a bucket.

Under a discriminant R, we split f into two pieces, q-zero, which holds the non-residues, and q-one, which holds the residues. ⟨pause: the blade cleaves the bucket into amber and cyan⟩ Four checks at a random point keep that split honest. The first is decomposition, so f equals q-zero times q-one, which means no root was added, and none was dropped. The second is that every root of q-one is a residue, and the third is that every root of q-zero is a non-residue. And the fourth is that q-zero at minus R is nonzero. That last one is what enforces the convention. q-zero is a product of linear factors, so a nonzero value at minus R means minus R isn't one of its roots. Together with the first check, if minus R is in the bucket at all, it's forced into q-one.

### 4.4 — Routing: decompose, merge, and a jagged frontier

Now let's build buckets for a whole epoch, at scale. An epoch doesn't arrive all at once. It streams in, stamp by stamp. So while epoch six is live, the service rolls consecutive stamps into bounded summaries, which are one product polynomial each, plus the anchor range they cover. A summary grows by checking, at a random point, that the new product is the old one times the next stamp's accumulator, and by absorbing that stamp into its anchor. A summary never crosses a sentinel, and each one becomes a root bucket, with an empty profile.

Then the service routes. A routing round does two things. First, it decomposes every bucket under the next discriminant, which roughly halves each one. Then it merges neighbors that ended up with the same profile, as long as their union still fits in a bucket. Merging is just the union check again, so there's nothing new to trust. ⟨pause: one routing round: split, then merge⟩

Underneath all of this, the anchor ranges are being tracked too. Decomposition keeps a bucket's range, and a merge joins two adjacent ranges into one. So round by round, lots of partial pieces of a profile become one bucket that spans the entire epoch. And the rounds run in parallel, they stream, and they run while the epoch is still live. ⟨pause: zoom out over the braided network⟩

Some profiles lag behind, though. Fluctuations in size leave a few of them still in pieces, and only those get another, partial round. That leaves what we call a jagged frontier, which is final profiles at different depths that together partition the field, and each one covers the whole epoch from sentinel to sentinel. ⟨pause: finished buckets click onto the finish rail⟩ Once the epoch closes, a seal step checks both sentinels.

In the proof tree, each split is one step that proves the product and the minus-R check, followed by two descents. Each descent returns one side, and checks the purity of the other side. So once both children are derived, both buckets are certified pure.

What about an attacker who grinds tachygrams to overload a single bucket? The discriminants have to stay unpredictable while tachygrams are being chosen. So each service samples its first offset privately, steps it up by one each round, and reveals it only after the epoch closes. That choice affects balance, but never soundness. The proofs certify any choice, and a badly balanced routing can just be ignored in favor of an honest service's.

And in case you're worried about scale, even at fifty thousand transactions per second, a thirty-two bit profile still has plenty of room to spare.

### 4.5 — The evidence tree

Serving one proof per final bucket would be a lot to keep around. So after the epoch closes, the service folds any set of final-bucket proofs into one evidence tree. It's a Poseidon Merkle tree with arity four, which matches the sponge's rate. Each leaf binds the epoch, its two sentinels, the first discriminant, the bucket's profile and depth, and the bucket's commitment, and the output is a single root. ⟨pause: buckets fold into a rate-4 tree, a root glows over epoch six⟩ The tree doesn't have to include every bucket. Even a single leaf is valid, because each leaf is already a proven full-epoch bucket.

For membership, we authenticate a leaf, and check that the value is a root of its bucket. No profile is needed, because every bucket divides the epoch's polynomial, so any root is a tachygram from that epoch, and that's how our note's commitment will be found in epoch five. For non-membership, we re-derive the discriminants, check that the value's bits select this leaf, and check that the bucket is nonzero there, and that's how our nullifier for epoch six will be cleared.

So the sixteen-minute linear verification turned into at most thirteen hashes, plus one opening of bounded degree. The routing ran once, in flight, and building the tree is the only work that's left after the epoch closes.

---

## Chapter 5 — The proof tree

### 5.1 — Steps, headers, bridges

Now that we have all the pieces, let's look at what the actual proof looks like.

A spend has to satisfy a pretty long statement, and so does an output, and so does the bundle that glues them together. We don't prove those in one piece. Instead, we break them into steps. ⟨pause: statement cards shatter into a tree of steps⟩ A step is a bounded circuit. It takes up to two child proofs and some private witness, checks part of the statement, and emits a new proof whose public output is a header, which is the data in proof-carrying data. Headers flow upward, from children to parents.

A parent bridges its children. It loads both headers, and checks that the fields which have to agree really do, like the same note commitment, matching sentinels, or the same epoch. A decomposition is sound exactly when there's enough bridging.

From here on, we'll use three colors. Gold steps run on the wallet, and they see the note. Cyan steps run on a service, and they only see opaque values. And white is shared evidence that anyone can use, which is anchor chain segments for the active epoch, and evidence trees for the closed ones.

### 5.2 — Same-epoch spend: the base tree

Let's start with the simplest spend. It's now epoch nine, and the wallet also received another note earlier in this same epoch. Spending a note in the epoch it was created doesn't need any exclusion proof at all, because it didn't exist before, so there's nothing to exclude.

The first step, SpendableInit, takes the creation stamp's data as witness, proves that the note's commitment is a root of that stamp's accumulator, and computes the anchor that stamp produced. Out comes a header that basically says this note is spendable, with its commitment, its epoch, and that anchor. The wallet can build it as soon as the creation block is final, and cache it, or even hand it to a hardware wallet early.

Then SpendBind opens the note, and this is where the spend statement actually gets checked. It makes sure the payment key matches a-k and n-k, recomputes the commitment, checks that the value is in range, binds r-k through alpha, and then derives the two nullifiers for epochs nine and ten. What it emits is a stamp for just this one action. An output gets its stamp from a single step, OutputSeed, which covers the whole output statement. And StampMerge joins stamps by multiplying their accumulators.

The last step is StampLift, which consumes a shared anchor chain segment and moves the stamp to a later anchor. That segment contains no sentinel, so a lift can never cross into another epoch. And the lift isn't just a convenience, by the way. Without it, the stamp's anchor would point right at the note's creation, so lifting is actually part of what keeps the spend unlinkable. ⟨pause: the full base tree, checklist complete⟩

And it turns out every spend ends this way, with SpendBind, merge, and lift. So the only question left is what feeds SpendBind when the note is older.

### 5.3 — Past-epoch spend: our original note

So now let's go back to our original note, which was born in epoch five and is being spent in epoch nine. Its history splits into three parts.

Let's start with the epoch it was born in. This part stays on the wallet, because in that one epoch the wallet has to show both that the note exists and that it wasn't already spent. So it opens epoch five's evidence tree twice, once at the bucket for its epoch-five nullifier, and once at the bucket for its commitment. NoteUnspentInit opens the note with its keys and re-derives that nullifier, and then it checks that the nullifier's profile selects the bucket and proves it's absent. SpendableReinit then joins that with the commitment's membership opening, for the same epoch and the same sentinels. What comes out is a fully established spendable header, which is valid from the start of epoch six. ⟨pause: the spendable header glows⟩

Epochs six through eight are where delegation pays off, because here the work splits between the service and the wallet. On the service side, UnspentSeed starts an empty range, and then each UnspentLift consumes one evidence-tree opening, proves one opaque nullifier absent, multiplies one cubic factor into the service's commitment, and advances from one sentinel to the next. It can't skip an epoch, repeat one, or reorder them. ⟨pause: a skip attempt jams the ratchet⟩ And the whole time, the service never learns which note this is.

Meanwhile, the wallet is deriving its own range. NoteSeed opens the note once, and emits its master key header. Each NullifierDerive squeezes out one window, so four up to eight, and then eight up to twelve, and NullifierFuse joins them into one commitment, over four to twelve.

And then there's the join, which is where everything comes together. UnspentBind checks that the service's range is nonempty and sits inside the wallet's, and then runs the division from before, so the service's product divides the wallet's. ⟨pause: the service's stack lifts out of the wallet's⟩ That's the moment where the delegated, note-independent work becomes about this specific note. SpendableLift then seams the result onto the spendable header, with sentinel equality at the seam. And now the note is spendable through the start of epoch nine.

From there, it's basically the same as the simple spend. SpendBind derives the nullifiers for nine and ten, StampMerge joins this stamp with the other spend and the outputs, and one StampLift moves the whole thing to the transaction's target anchor in epoch nine. ⟨pause: the full tree: one stamp, two spends, two outputs⟩

And by the way, if the wallet uses several services for different ranges, UnspentMerge joins adjacent results before binding, and checks that one's end sentinel is the other's start.

So what does a service actually learn? It only sees opaque values, and ranges that it can't tell apart from decoys. It never sees the commitment, the note, another service's work, or where the spend lands.

---

## Chapter 6 — Landing

### 6.1 — The validator and the two-epoch window

So now the transaction reaches a validator, and for each stamp, the validator only has to do four checks. The first is that the target anchor is in canonical history, and that its epoch is either the current one or the one before. Then the action accumulator has to match the actions, and the tachygram accumulator has to match the published list, using the cheap random-point check. And finally, one proof has to verify. Balance and signatures, of course, work exactly like they do in Orchard.

Let's be precise about what the stamp is actually claiming. It proves exclusion strictly before the target epoch, so for our spend, that means up to the sentinel that opens epoch nine. The target anchor is not an exclusion endpoint, and duplicates inside epoch nine are consensus's job. That's why every spend targeting epoch nine has to publish its nullifier for nine.

So here's the new double-spend rule. Consensus keeps one duplicate window, which holds every tachygram from the current epoch and the one before. Candidates are processed in a fixed order, and each one is checked, then inserted.

Why that shape? Let's think like a double spender for a second, and recall the grace period we allowed, so that a transaction waiting in the mempool doesn't go stale. A stamp targeting epoch nine is still accepted during epoch ten. So the attacker builds two spends of the same note. The first one targets epoch nine, and is held back until epoch ten begins. The second one targets epoch ten. Both proofs are honest. The second one proves that its nullifier for epoch nine never appeared in epoch nine, and that's true, because the first spend didn't land in epoch nine. It landed in ten.

If each spend only published its own epoch's nullifier, the first would reveal the value for nine, the second would reveal the value for ten, and nothing would collide. That's why every spend also publishes the next epoch's nullifier. So the first spend reveals nine and ten, the second reveals ten and eleven, and they collide on ten. ⟨pause: the two spends' tokens collide on ten⟩

And what about the window? The attacker can push one step further, and hold the second spend back until epoch eleven. Now the colliding values land in different epochs, ten and eleven. But a window over the current and the preceding epoch still holds both, and it catches it. ⟨pause: the window slides and catches the collision⟩ Anything older than that falls inside the history that a stamp already proves is excluded.

So together, the adjacent pair and the two-epoch window close the gap that the grace period opened. And consensus now only holds two epochs of tachygrams, instead of all of history. ⟨pause: the two-epoch grid beside the original from the prologue⟩

### 6.2 — Aggregation: from many stamps to one

So far, every transaction has been a standalone bundle, which is one with its own stamp, proven by its own wallet. Aggregation turns many standalone bundles into one aggregate bundle, with a single stamp. ⟨pause: standalone bundles stream into the mempool, each with its own stamp⟩

Let's follow the life cycle, starting with wallets publishing their standalone bundles. An aggregator then picks some of them and combines them. In the full protocol, anyone can aggregate, and aggregates can be relayed and merged again. But a miner has the strongest reason to do it, because every byte of proof that's saved is room for more fees. So here, we'll just let the miner be the only aggregator.

The first thing the miner has to deal with is that the stamps are targeting different anchors. So it lifts each one to a single common anchor, inside one epoch, and never across a sentinel. It's the same StampLift as before. ⟨pause: stamps slide to a common anchor⟩ And no lift depends on another one, so they can all run at once.

Once they share an anchor, the miner can merge them. StampMerge takes two stamps and returns one. It unions the tachygrams, multiplies the accumulators, and fuses the proofs. We pair the stamps up, then pair the results, and keep going up a binary tree until there's only one stamp left. ⟨pause: the merge tree folds up to a single stamp⟩ Consensus refuses duplicate tachygrams, so a merge of two overlapping sets could never land on chain, and there's nothing extra to enforce.

When the miner assembles the block, it carries the aggregate, along with every transaction it covers. But each covered transaction drops its own stamp, and points at the aggregate's witness transaction ID instead. ⟨pause: each transaction swaps its stamp for a reference⟩ And that's why the stamp lives in the authorization data. Swapping it changes the witness ID, but never the transaction ID, so every signature stays valid.

And on the other end, a validator checks that the tachygrams are distinct, that the aggregate's coverage matches the transactions pointing at it, and that one proof verifies. It's just one proof, no matter how many transactions it covers.

### 6.3 — What aggregation buys

So let's put some numbers on this, with the simplification we just made, which is that wallets send standalone bundles and the miner aggregates alone.

Let's start with latency, and the good news is that all of the lifts run in parallel, so together they cost one proving step. The merges form a binary tree, so a block of N transactions adds log N more. ⟨pause: a depth counter beside the merge tree⟩ With enough cores, doubling the traffic only costs one more step. Today, a step takes about one point two seconds on a laptop.

So how much time does the miner actually have? A block comes every twenty-five seconds. If we subtract two seconds to send it out, and another two to verify it and run the rest of the node, we're left with about twenty seconds, which is sixteen steps, so one lift and fifteen levels of merging. ⟨pause: the merge tree grows to fifteen levels⟩ Fifteen levels cover more than thirty-two thousand transactions, which is over thirteen hundred per second, from a single miner.

Size is the other half of the story. A compressed proof is about seven point four kilobytes. A two-in, two-out transaction is only about seven hundred and seventy bytes, which is eight tachygrams, four actions of r-k and c-v, and a small encrypted memo. ⟨pause: a block bar, proof share against payload⟩ Without aggregation, every transaction is hauling around a proof that's ten times its own size, and a two-megabyte block holds about two hundred and forty of them. With aggregation, the block carries a single proof, and fits about twenty-six hundred. So each transaction's share of the proof drops from seven kilobytes to under three bytes.

So it's really size, and not proving, that's the ceiling. Let's say we raise the block limit to twenty megabytes. That fits about twenty-six thousand transactions, which is roughly a thousand per second. ⟨pause: block bar grows, a thousand per second⟩ And proving them still fits in the window, at sixteen steps and about nineteen seconds.

So a validator checks one proof per block, and the proof's share of each transaction shrinks as traffic grows. Proof size stops being the bottleneck, and what's left is delivering the notes themselves.

---

## Chapter 7 — The other half

### 7.1 — Addresses, tags, and private retrieval

The cut we made at the start left the payment protocol in charge of delivering notes. So let's sketch the leading design, which is being built by ValarGroup.

An address is a pair of the payment key and an ML-KEM encapsulation key, and both of them are fresh for each sender. So why not use Orchard-style diversification? Well, because it isn't quantum-private. All those diversified keys share one incoming viewing key, and anyone who can break one discrete log recovers it, which exposes every incoming note, past and future. ⟨pause: a quantum lens over i-v-k opens every note⟩ ML-KEM is post-quantum, but it doesn't have an analogue of many unlinkable keys sharing one decryption key.

So discovery needs a different shortcut, and that's where tags come in. Each encrypted memo carries a short tag. The first-contact tag is a hash of the encapsulation key, so the recipient can find the handshake before it knows the shared secret. Every later tag is a hash of the shared secret and a counter, which is predictable to the two parties, opaque to everyone else, and fresh for every note, since tags appear on chain.

So instead of trial-decrypting the whole chain, your wallet looks up its tags with private information retrieval, which reveals nothing about the query. And it turns out the same machinery also includes a tachygram database, which privately supplies the stamp and anchor data that the spend proof needs.

And finally, there's Faerie gold. Tachyon's notes don't have a canonical position, so the shielded protocol can't bind psi the way Orchard binds rho. Instead, the wallet checks each incoming note's nullifier at a fixed reference epoch against the notes it already holds, and a reused psi collides right there.

---

## Chapter 8 — Quantum posture, and the cascade

### 8.1 — Private today, sound after an upgrade

That leaves the quantum question. Tachyon's stance is private today and sound after an upgrade, and that asymmetry is deliberate. Privacy has to hold retroactively, because today's chain can be harvested now and decrypted whenever the hardware arrives, so anything guarding privacy has to already be post-quantum. Soundness, meaning that nobody forges and nobody steals, only matters at spend time, so it can wait for a coordinated network upgrade.

So let's audit today's chain against that bar. Owner fields and note commitments are Poseidon, nullifiers are P R F outputs, and memos are M L KEM plus symmetric encryption, so all of that is already quantum-safe. That leaves three things that still rest on discrete log, which are value commitments, randomized keys, and the binding key. The value commitment is perfectly hiding, so there's nothing to decrypt there. And what about the randomized key? A quantum computer can take its discrete log and recover a s k plus alpha, but alpha is a fresh P R F mask, so what it gets is a random-looking scalar that doesn't link to anything. ⟨pause: the quantum lens: alpha pixelates the link⟩ So the full power of a quantum computer against today's Tachyon is forgery, which is the half that can wait for the upgrade.

When the upgrade comes, there are two swaps. The first one is authorization, and the problem there is that re-randomization is intrinsically discrete-log, and no post-quantum signature does it. So the replacement recovers unlinkability from zero knowledge instead, by proving in circuit that you know a valid post-quantum signature. Schemes like CAPSS are built to be cheap exactly there. Authorization then folds into the transaction's PCD proof, the randomized key leaves the action description entirely, and the note-to-action binding it used to carry through alpha gets re-established as an explicit constraint in the statement. The second swap is the proof system itself, where Ragu's discrete-log commitments get swapped for lattice-based folding. The recursive structure that makes spendability proofs incremental survives, and only the hardness assumption underneath changes. The concrete lattice constructions are still active research.

### 8.2 — Outro: the decision cascade

⟨pause: the camera pulls back over the note's whole journey⟩

If we run the whole design backward, the nullifier set couldn't be pruned, so validation moved to the client. Clients can't sync alone, so syncing got delegated. Delegation would leak the spend, so nullifiers evolve. Evolving nullifiers would go stale in the mempool, so actions carry a pair, and consensus keeps a two-epoch window. Per-stamp history needed composing, so we got one accumulator, with union by multiplication. Its degree exploded, so quadratic residues bucket each epoch. And none of it would be affordable alone, so the expensive evidence is built once, proven once, and shared by everyone. ⟨pause: chapter cards reconnect into one chain⟩

Each decision is forced by the one before it, and they all follow from one principle, which is that the client proves, and consensus checks.

Everything in this video is written down, in a lot more detail, in the Deep Dive at tachyon dot z dot cash, alongside my blog posts and the Ragu book. The implementation is open, on our GitHub, and both links are right below. Thanks for watching.

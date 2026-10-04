Scaling Zcash with Tachyon: how private payments can scale without every node remembering every nullifier forever.

Every shielded pool keeps a nullifier set that only grows and can never be pruned. Tachyon removes that wall by moving validation to the client. We follow one note from its birth to its spend four epochs later, and every piece of the design appears exactly when that note needs it:
- a split between the shielded protocol and the payment protocol;
- nullifiers that evolve per epoch, so syncing can be delegated without leaking the spend;
- a single polynomial accumulator for commitments and nullifiers;
- quadratic-residue filters that make epoch-wide exclusion cheap;
- a proof tree whose expensive evidence is built once and shared;
- a two-epoch consensus window;
- a post-quantum posture.

Learn more
🌐 Tachyon project: https://tachyon.z.cash
💻 Implementation: https://github.com/tachyon-zcash/tachyon
📖 Deep Dive: https://tachyon.z.cash/_book/revisit
🔗 Zcash: https://z.cash

Chapters
0:00 Two sets, two fates: the nullifier set nobody can prune
0:59 Client-side validation, Ragu as a black box, and our note
2:22 Why Zcash keys keep getting more complicated
3:56 The cut: shielded protocol vs payment protocol
5:39 The Tachyon note
6:31 A set as the roots of a polynomial: tachygrams
8:47 The action and the stamp
11:06 The anchor chain: anchors per stamp, sentinels per epoch
12:21 Why one nullifier per note has to go
13:33 Evolving nullifiers, and two per spend
15:38 The ranged nullifier commitment: indexed multisets from cubes
18:06 The epoch accumulator, and the wall
19:13 Bucketing, and a quadratic-residue detour in F₁₃
21:04 The batched QR test and one decomposition
22:41 Routing: decompose, merge, and a jagged frontier
24:56 The evidence tree
26:11 Proof steps, headers, and bridges
27:07 Same-epoch spend: the base proof tree
28:48 Past-epoch spend: binding delegated work to the note
31:07 Consensus: the grace-period attack and the two-epoch window
33:16 Aggregation
33:51 The payment protocol: addresses, tags, private retrieval
35:26 Private today, sound after a quantum upgrade
37:26 The decision cascade

Topics covered
Zcash, Tachyon, shielded transactions, nullifiers, evolving nullifiers, note commitments, zero-knowledge proofs, recursive proofs, proof-carrying data (PCD), polynomial commitments, polynomial accumulators, quadratic residues, Orchard, Sapling, Ragu, oblivious syncing, private information retrieval (PIR), ML-KEM, post-quantum cryptography, client-side validation, blockchain scaling.

This video is for Zcash engineers and cryptographers who already know Orchard well and want to see why Tachyon is designed the way it is.

#Zcash #Tachyon #ZeroKnowledge #zkSNARK #Cryptography #Privacy #Blockchain #PostQuantum

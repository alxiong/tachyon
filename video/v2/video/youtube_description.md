Scaling Zcash with Tachyon: how private payments can scale without every node remembering every nullifier forever.

Every shielded pool keeps a nullifier set that only grows and can never be pruned. Tachyon removes that wall by moving validation to the client. We follow one note from its birth to its spend four epochs later, and every piece of the design appears exactly when that note needs it:
- a separation of spend authorization (the shielded protocol) from note transmission (the payment protocol);
- nullifiers that evolve per epoch, so syncing can be delegated without leaking the spend;
- a single polynomial accumulator for commitments and nullifiers;
- quadratic-residue filters that make epoch-wide exclusion cheap;
- a proof tree whose expensive evidence is built once and shared;
- a two-epoch consensus window;
- aggregation of many stamps into one proof per block, and what it costs;
- a post-quantum posture.

Learn more
🌐 Tachyon project: https://tachyon.z.cash
💻 Implementation: https://github.com/tachyon-zcash/tachyon
📖 Deep Dive: https://tachyon.z.cash/_book/revisit
🔗 Zcash: https://z.cash

Chapters
0:00 Two sets, two fates: the nullifier set nobody can prune
1:04 Client-side validation, Ragu as a black box, and our note
2:36 Why Zcash keys got complicated
4:30 Separating spend authorization from note transmission
6:48 The Tachyon note
7:32 A set as the roots of a polynomial: tachygrams
9:48 The action and the stamp
12:16 The anchor chain: anchors per stamp, sentinels per epoch
13:34 Why one nullifier per note has to go
14:49 Evolving nullifiers, and two per spend
17:16 The ranged nullifier commitment: indexed multisets from cubes
19:55 The epoch accumulator, and the wall
21:12 Bucketing, and a quadratic-residue detour in F₁₃
23:15 The batched QR test and one decomposition
24:59 Routing: decompose, merge, and a jagged frontier
27:32 The evidence tree
28:47 Proof steps, headers, and bridges
29:51 Same-epoch spend: the base proof tree
31:33 Past-epoch spend: binding delegated work to the note
34:16 Consensus: the grace-period attack and the two-epoch window
36:55 Aggregation: from many stamps to one
38:52 What aggregation buys: latency and block size
41:02 The payment protocol: addresses, tags, private retrieval
42:46 Private today, sound after a quantum upgrade
44:56 The decision cascade

Topics covered
Zcash, Tachyon, shielded transactions, nullifiers, evolving nullifiers, note commitments, zero-knowledge proofs, recursive proofs, proof-carrying data (PCD), polynomial commitments, polynomial accumulators, quadratic residues, Orchard, Sapling, Ragu, oblivious syncing, private information retrieval (PIR), ML-KEM, proof aggregation, post-quantum cryptography, client-side validation, blockchain scaling.

This video is for Zcash engineers and cryptographers who already know Orchard well and want to see why Tachyon is designed the way it is.

#Zcash #Tachyon #ZeroKnowledge #zkSNARK #Cryptography #Privacy #Blockchain #PostQuantum

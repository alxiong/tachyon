Scaling Zcash with Tachyon: how private payments can scale without every node remembering every nullifier forever.

Zcash's privacy comes from nullifiers, and the set of nullifiers only ever grows. This video explains Tachyon, a protocol redesign that moves validation to the client. Wallets prove their notes are unspent, validators check one small proof, and nobody has to store or search the whole nullifier history. We build the whole design from the ground up: evolving nullifiers, polynomial accumulators, epoch anchors, quadratic-residue bucketing, recursive proof trees, and a post-quantum-ready payment protocol.

Learn more
🌐 Tachyon project: https://tachyon.z.cash
💻 Implementation: https://github.com/tachyon-zcash/tachyon
📖 Deep Dive: https://tachyon.z.cash/_book/revisit
🔗 Zcash: https://z.cash

Chapters
0:00 Two sets, two fates: why nullifiers can't be pruned
1:16 The thesis: client-side validation
2:41 Why Zcash keys keep getting more complicated
4:44 The cut: shielded protocol vs payment protocol
6:52 The Tachyon note
7:38 Why one nullifier per note has to go
9:29 Evolving nullifiers: the derivation
10:51 The ranged nullifier commitment (indexed multisets from cubes)
14:16 Tachygrams: one accumulator for commitments and nullifiers
16:26 Actions, stamps, and two tachygrams each
19:41 Anchors per stamp, sentinels per epoch
21:26 The epoch accumulator, and why it isn't enough
23:18 Bucketing by an intrinsic address
24:36 Number theory detour: quadratic residues
26:51 QR decomposition: one split, four checks
28:24 Routing: decompose and merge rounds
30:59 The evidence tree
32:41 Proof steps, headers, and bridging
34:08 Same-epoch spend: the minimal proof tree
35:38 Past-epoch spend: binding delegated work to the note
38:18 Consensus: the two-epoch window
39:49 Aggregation
40:29 The payment protocol: private retrieval
41:38 ML-KEM addresses and the tag schedule
44:04 Private today, sound after a quantum upgrade
46:15 The decision cascade: how the design fits together

Topics covered
Zcash, Tachyon, shielded transactions, nullifiers, note commitments, zero-knowledge proofs, recursive proofs, proof-carrying data (PCD), polynomial commitments, polynomial accumulators, quadratic residues, Orchard, Sapling, Ragu, private information retrieval (PIR), ML-KEM, post-quantum cryptography, client-side validation, blockchain scaling, privacy coins.

This video is for readers who already know the basics of Zcash/Orchard and want to see why Tachyon is designed the way it is.

#Zcash #Tachyon #ZeroKnowledge #zkSNARK #Cryptography #Privacy #Blockchain #postquantum 

use core::marker::PhantomData;

use corez::io::{self, Read, Write};
use derive_more::{Debug, Display, Eq as TotalEq, Error, PartialEq};
use ff::Field as _;
use group::{Curve as _, Group as _};
use lazy_static::lazy_static;
use pasta_curves::{Eq, Fp};

use super::{
    EpochIndex, TachygramSetCommit,
    anchor_kind::{AnchorKind, Erased, Sentinel, Stamped},
};
use crate::{digest::poseidon, serialization};

lazy_static! {
    static ref ANCHOR_GENESIS: Fp = poseidon::anchor_next_epoch(Fp::ZERO, Fp::ZERO);
}

/// Errors that can occur when advancing an anchor.
#[derive(Debug, Display, Error, PartialEq, TotalEq)]
pub enum AnchorError {
    /// The provided tachygram set is the identity point.
    #[display("next stamp cannot be the identity point")]
    NextStampZero,
    /// The provided tachygram set is empty.
    #[display("next stamp cannot be empty")]
    NextStampEmpty,
    /// The provided epoch index is zero.
    #[display("next epoch cannot be zero")]
    NextEpochZero,
}

/// Running anchor over the consensus state.
///
/// The kind parameter records provenance where it is statically known:
/// [`next_stamp`](Self::next_stamp) mints an `Anchor<Stamped>` and
/// [`next_epoch`](Self::next_epoch) mints an `Anchor<Sentinel>` — the two
/// domain-separated hash advancements. The default [`Erased`] kind is for
/// positions where provenance is not statically knowable (the wire, free step
/// witnesses, and header slots admitting either kind); typed anchors enter
/// those positions only through the explicit [`erase`](Self::erase) seam.
///
/// The kind never reaches circuits, hashes, or serialized bytes: every kind
/// encodes to the same single [`Fp`], so header encodings and the wire format
/// are identical to an untyped anchor's.
///
/// Typed kinds cannot be forged from a bare field element; only the erased
/// kind can:
///
/// ```compile_fail
/// use pasta_curves::Fp;
/// use zcash_tachyon::{Anchor, anchor_kind::Sentinel};
///
/// let forged: Anchor<Sentinel> = Anchor::<Sentinel>::from(Fp::zero());
/// ```
#[derive(Clone, Copy, Debug, Ord, PartialEq, PartialOrd, TotalEq)]
pub struct Anchor<K: AnchorKind = Erased>(Fp, #[debug(skip)] PhantomData<K>);

impl<K: AnchorKind> Anchor<K> {
    /// Advance the anchor to the next stamp in the present epoch.
    ///
    /// Available for every kind: an epoch's first stamp legitimately chains
    /// off the sentinel that opened it.
    ///
    /// The present epoch index may be zero, within the genesis epoch.
    ///
    /// # Errors
    ///
    /// Fails if `stamp_commit` is the identity point or a commitment to an
    /// empty set.
    pub fn next_stamp(
        self,
        present_epoch: EpochIndex,
        &stamp_commit: &TachygramSetCommit,
    ) -> Result<Anchor<Stamped>, AnchorError> {
        if *stamp_commit.as_ref() == Eq::identity() {
            Err(AnchorError::NextStampZero)
        } else if stamp_commit == TachygramSetCommit::default() {
            Err(AnchorError::NextStampEmpty)
        } else {
            Ok(Anchor(
                poseidon::anchor_next_stamp(
                    self.0,
                    present_epoch.into(),
                    stamp_commit.as_ref().to_affine(),
                ),
                PhantomData,
            ))
        }
    }

    /// Advance the anchor to the next epoch boundary, minting that epoch's
    /// sentinel.
    ///
    /// Available for every kind: a silent epoch's terminal anchor *is* the
    /// sentinel that opened it, so a crossing may tick off a sentinel.
    ///
    /// # Errors
    ///
    /// Fails if `next_epoch` is zero.
    pub fn next_epoch(self, next_epoch: EpochIndex) -> Result<Anchor<Sentinel>, AnchorError> {
        if next_epoch == EpochIndex(0) {
            Err(AnchorError::NextEpochZero)
        } else {
            Ok(Anchor(
                poseidon::anchor_next_epoch(self.0, next_epoch.into()),
                PhantomData,
            ))
        }
    }

    /// Forget this anchor's statically known provenance.
    ///
    /// This is the one-way seam through which typed anchors enter kind-unaware
    /// positions (header data, wire values, free witnesses).
    #[must_use]
    pub const fn erase(self) -> Anchor<Erased> {
        Anchor(self.0, PhantomData)
    }

    /// Assume a provenance for an anchor of unknown kind, without any check.
    ///
    /// Escape hatch for witness reconstruction and tests, where an anchor
    /// arrives as a bare field element (the wire carries no kind tag). The
    /// assumption is the caller's assertion; nothing verifies it, and
    /// soundness must not rest on it.
    #[must_use]
    pub const fn assume(anchor: Anchor<Erased>) -> Self {
        Self(anchor.0, PhantomData)
    }

    /// Write a 32-byte anchor.
    pub fn write<W: Write>(&self, mut writer: W) -> io::Result<()> {
        serialization::write_fp(&mut writer, &self.0)
    }
}

impl Anchor {
    /// Read a 32-byte anchor.
    ///
    /// The wire carries no kind tag, so a parsed anchor is always [`Erased`].
    pub fn read<R: Read>(mut reader: R) -> io::Result<Self> {
        serialization::read_fp(&mut reader).map(Self::from)
    }
}

impl Anchor<Sentinel> {
    /// The leading epoch boundary for epoch zero.
    #[must_use]
    pub fn genesis() -> Self {
        Self(*ANCHOR_GENESIS, PhantomData)
    }
}

impl Default for Anchor {
    /// The leading epoch boundary for epoch zero, with its sentinel kind
    /// erased.
    fn default() -> Self {
        Anchor::<Sentinel>::genesis().erase()
    }
}

impl<K: AnchorKind> From<Anchor<K>> for Fp {
    fn from(anchor: Anchor<K>) -> Self {
        anchor.0
    }
}

impl From<Fp> for Anchor {
    /// Forge an anchor of unknown kind from a bare field element.
    ///
    /// Typed kinds cannot be forged this way; see [`Anchor::assume`].
    fn from(fp: Fp) -> Self {
        Self(fp, PhantomData)
    }
}

impl From<Anchor<Stamped>> for Anchor {
    fn from(anchor: Anchor<Stamped>) -> Self {
        anchor.erase()
    }
}

impl From<Anchor<Sentinel>> for Anchor {
    fn from(anchor: Anchor<Sentinel>) -> Self {
        anchor.erase()
    }
}

#[cfg(test)]
mod tests {
    use pasta_curves::Eq;
    use rand::{SeedableRng as _, rngs::StdRng};

    use super::*;
    use crate::{Tachygram, TachygramSetPoly};

    #[test]
    fn order_matters() {
        let rng = &mut StdRng::seed_from_u64(0);
        let first = TachygramSetPoly::from_iter([Tachygram::random(&mut *rng)]).commit();
        let second = TachygramSetPoly::from_iter([Tachygram::random(&mut *rng)]).commit();

        let forward = Anchor::default()
            .next_stamp(EpochIndex(7), &first)
            .unwrap()
            .next_stamp(EpochIndex(7), &second)
            .unwrap();

        let reverse = Anchor::default()
            .next_stamp(EpochIndex(7), &second)
            .unwrap()
            .next_stamp(EpochIndex(7), &first)
            .unwrap();

        assert_ne!(forward, reverse);
    }

    #[test]
    fn next_stamp_rejects_invalid_sets() {
        let rng = &mut StdRng::seed_from_u64(0);

        // The identity commitment is not a valid set
        {
            let anchor = Anchor::from(Fp::random(&mut *rng));
            let zero_set = TachygramSetCommit::from(Eq::identity());

            let Err(AnchorError::NextStampZero) = anchor.next_stamp(EpochIndex(7), &zero_set)
            else {
                panic!("should not be able to advance with an identity stamp");
            };
        }

        // An empty set commits to a constant polynomial
        {
            let anchor = Anchor::from(Fp::random(&mut *rng));
            let one_set = TachygramSetCommit::default();

            let Err(AnchorError::NextStampEmpty) = anchor.next_stamp(EpochIndex(1), &one_set)
            else {
                panic!("should not be able to advance with an empty stamp");
            };
        }
    }

    #[test]
    fn next_epoch_rejects_epoch_zero() {
        let rng = &mut StdRng::seed_from_u64(0);

        let anchor = Anchor::from(Fp::random(rng));

        let Err(AnchorError::NextEpochZero) = anchor.next_epoch(EpochIndex(0)) else {
            panic!("should not be able to advance to epoch zero");
        };
    }

    #[test]
    fn genesis_matches_erased_default() {
        assert_eq!(Anchor::<Sentinel>::genesis().erase(), Anchor::default());
    }

    #[test]
    fn kinds_flow_through_advancement() {
        let rng = &mut StdRng::seed_from_u64(0);
        let commit = TachygramSetPoly::from_iter([Tachygram::random(rng)]).commit();

        // An epoch's first stamp chains off a sentinel; further stamps chain
        // off stamped anchors.
        let genesis: Anchor<Sentinel> = Anchor::genesis();
        let first: Anchor<Stamped> = genesis.next_stamp(EpochIndex(0), &commit).unwrap();
        let second: Anchor<Stamped> = first.next_stamp(EpochIndex(0), &commit).unwrap();

        // A silent epoch's crossing ticks a sentinel off a sentinel.
        let silent: Anchor<Sentinel> = genesis.next_epoch(EpochIndex(1)).unwrap();
        let after_silent: Anchor<Sentinel> = silent.next_epoch(EpochIndex(2)).unwrap();

        // Erasure reaches the same values the untyped path computes.
        assert_eq!(
            second.erase(),
            Anchor::default()
                .next_stamp(EpochIndex(0), &commit)
                .unwrap()
                .next_stamp(EpochIndex(0), &commit)
                .unwrap()
                .erase(),
        );
        assert_eq!(
            after_silent.erase(),
            Anchor::default()
                .next_epoch(EpochIndex(1))
                .unwrap()
                .next_epoch(EpochIndex(2))
                .unwrap()
                .erase(),
        );

        // An assumed kind round-trips the underlying value.
        let assumed = Anchor::<Sentinel>::assume(silent.erase());
        assert_eq!(assumed.erase(), silent.erase());
    }
}

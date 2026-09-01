use core::ops::Mul;

use derive_more::{Debug, Eq as TotalEq, From, Into, PartialEq};
use pasta_curves::{Eq, Fp};
use ragu::Polynomial;

use crate::{
    collections::indexed_multiset::IndexedMultiset, nullifier::Nullifier, primitives::EpochIndex,
};

/// Pedersen commitment to a nullifier sequence.
#[derive(Clone, Copy, Debug, From, Into, PartialEq, TotalEq)]
pub struct NfSeqCommit(Eq);

/// Witness for a nullifier sequence, held in indexed-multiset form: the
/// product of its members' encodings, one per member, realized into a
/// [`Polynomial`] lazily and memoized.
#[derive(Clone, Debug, Default, PartialEq, TotalEq)]
pub struct NfSeqPoly(IndexedMultiset);

impl NfSeqPoly {
    /// Build the sequence for one contiguous run: the members of the
    /// consecutive epochs starting at `epoch_start`.
    #[must_use]
    pub fn new(epoch_start: EpochIndex, nfs: &[Nullifier]) -> Self {
        Self(
            (epoch_start.into()..)
                .zip(nfs.iter().copied().map(Fp::from))
                .collect(),
        )
    }

    /// Deterministic (untrapdoored) commitment to the sequence polynomial,
    /// memoized until the sequence changes.
    #[must_use]
    pub fn commit(&self) -> NfSeqCommit {
        NfSeqCommit(self.0.commit())
    }

    /// Evaluate the sequence polynomial at a given point, streaming over the
    /// members without realizing the coefficients.
    #[must_use]
    pub fn eval(&self, x: Fp) -> Fp {
        self.0.eval(x)
    }

    /// The quotient witness `self / divisor`, computed as the multiset
    /// difference of the members instead of by polynomial division.
    ///
    /// Returns [`None`] when `divisor` is not a sub-multiset of `self`, in
    /// which case no polynomial quotient exists either.
    #[must_use]
    pub fn quotient(&self, divisor: &Self) -> Option<Self> {
        self.0.quotient(&divisor.0).map(Self)
    }
}

impl AsRef<Polynomial> for NfSeqPoly {
    /// The realized (memoized) sequence polynomial.
    ///
    /// # Panics
    ///
    /// If the realization exceeds the polynomial coefficient cap.
    fn as_ref(&self) -> &Polynomial {
        self.0.realize()
    }
}

impl Mul for NfSeqPoly {
    type Output = Self;

    /// Multiset union: the product of two sequences' member multisets. The
    /// coefficient cap applies only once the product is realized.
    fn mul(self, rhs: Self) -> Self {
        Self(self.0.union(&rhs.0))
    }
}

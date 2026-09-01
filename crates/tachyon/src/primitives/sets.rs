use corez::io::{self, Read, Write};
use derive_more::{AsRef, Debug, Eq as TotalEq, From, Into, PartialEq};
use group::Curve as _;
use pasta_curves::{Eq, Fp};
use ragu::Polynomial;

use super::{ActionDigest, Tachygram};
use crate::{collections::multiset::Multiset, serialization};

/// Pedersen commitment to a stamp's tachygram set.
#[derive(AsRef, Clone, Copy, Debug, From, Into, PartialEq, TotalEq)]
pub struct TachygramSetCommit(Eq);

impl TachygramSetCommit {
    /// Read as an affine point from the consensus wire format.
    pub fn read<R: Read>(mut reader: R) -> io::Result<Self> {
        let commit = serialization::read_eq_affine(&mut reader)?;
        Ok(Self(commit.into()))
    }

    /// Write as an affine point to the consensus wire format.
    pub fn write<W: Write>(&self, mut writer: W) -> io::Result<()> {
        serialization::write_eq_affine(&mut writer, &self.0.to_affine())?;
        Ok(())
    }
}

impl Default for TachygramSetCommit {
    /// A commitment to an empty set.
    fn default() -> Self {
        Self(Multiset::default().commit())
    }
}

/// Pedersen commitment to a stamp's action-digest set.
#[derive(AsRef, Clone, Copy, Debug, From, Into, PartialEq, TotalEq)]
pub struct ActionSetCommit(Eq);

impl ActionSetCommit {
    /// Read as an affine point from the consensus wire format.
    pub fn read<R: Read>(mut reader: R) -> io::Result<Self> {
        let commit = serialization::read_eq_affine(&mut reader)?;
        Ok(Self(commit.into()))
    }

    /// Write as an affine point to the consensus wire format.
    pub fn write<W: Write>(&self, mut writer: W) -> io::Result<()> {
        serialization::write_eq_affine(&mut writer, &self.0.to_affine())?;
        Ok(())
    }
}

impl Default for ActionSetCommit {
    /// A commitment to an empty set.
    fn default() -> Self {
        Self(Multiset::default().commit())
    }
}

/// Witness for a stamp's tachygram set, held in multiset form: the members
/// are the roots of the encoded polynomial, realized into a [`Polynomial`]
/// lazily and memoized alongside its commitment. Non-repeating in practice
/// (a stamp's tachygrams are unique on the wire), but the representation
/// stays a general multiset: a repeated member repeats its factor.
#[derive(Clone, Debug, Default, PartialEq, TotalEq)]
pub struct TachygramSetPoly(Multiset);

/// Witness for a stamp's action-digest set, held in multiset form: the
/// members are the roots of the encoded polynomial, realized into a
/// [`Polynomial`] lazily and memoized alongside its commitment. Multiplicity
/// is load-bearing here: a stamp covering an action twice must not be
/// confusable with one covering it once.
#[derive(Clone, Debug, Default, PartialEq, TotalEq)]
pub struct ActionSetPoly(Multiset);

impl TachygramSetPoly {
    /// Deterministic (untrapdoored) commitment to the set polynomial,
    /// memoized until the set changes.
    #[must_use]
    pub fn commit(&self) -> TachygramSetCommit {
        TachygramSetCommit(self.0.commit())
    }

    /// Evaluate the set polynomial at a given point, streaming over the
    /// members without realizing the coefficients.
    #[must_use]
    pub fn eval(&self, x: Fp) -> Fp {
        self.0.eval(x)
    }

    /// Multiset union: adds the members' multiplicities, matching the
    /// product of the encoded polynomials with no polynomial arithmetic
    /// involved.
    #[must_use]
    pub fn union(&self, other: &Self) -> Self {
        Self(self.0.union(&other.0))
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

impl ActionSetPoly {
    /// Deterministic (untrapdoored) commitment to the set polynomial,
    /// memoized until the set changes.
    #[must_use]
    pub fn commit(&self) -> ActionSetCommit {
        ActionSetCommit(self.0.commit())
    }

    /// Evaluate the set polynomial at a given point, streaming over the
    /// members without realizing the coefficients.
    #[must_use]
    pub fn eval(&self, x: Fp) -> Fp {
        self.0.eval(x)
    }

    /// Multiset union: adds the members' multiplicities, matching the
    /// product of the encoded polynomials with no polynomial arithmetic
    /// involved.
    #[must_use]
    pub fn union(&self, other: &Self) -> Self {
        Self(self.0.union(&other.0))
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

impl AsRef<Polynomial> for TachygramSetPoly {
    /// The realized (memoized) set polynomial.
    ///
    /// # Panics
    ///
    /// If the realization exceeds the polynomial coefficient cap.
    fn as_ref(&self) -> &Polynomial {
        self.0.realize()
    }
}

impl AsRef<Polynomial> for ActionSetPoly {
    /// The realized (memoized) set polynomial.
    ///
    /// # Panics
    ///
    /// If the realization exceeds the polynomial coefficient cap.
    fn as_ref(&self) -> &Polynomial {
        self.0.realize()
    }
}

impl FromIterator<ActionDigest> for ActionSetPoly {
    fn from_iter<I: IntoIterator<Item = ActionDigest>>(iter: I) -> Self {
        Self(iter.into_iter().map(Fp::from).collect())
    }
}

impl FromIterator<Tachygram> for TachygramSetPoly {
    fn from_iter<I: IntoIterator<Item = Tachygram>>(iter: I) -> Self {
        Self(iter.into_iter().map(Fp::from).collect())
    }
}

#[cfg(test)]
mod tests {
    use rand::{SeedableRng as _, rngs::StdRng};

    use super::*;

    #[test]
    fn collecting_a_repeated_tachygram_keeps_its_multiplicity() {
        let rng = &mut StdRng::seed_from_u64(2);
        let tg = Tachygram::random(rng);

        let repeated = TachygramSetPoly::from_iter([tg, tg]);
        let single = TachygramSetPoly::from_iter([tg]);
        assert_ne!(repeated, single);
        assert_ne!(repeated.commit(), single.commit());
    }

    #[test]
    fn union_and_quotient_stay_in_set_form() {
        let rng = &mut StdRng::seed_from_u64(5);
        let left = TachygramSetPoly::from_iter([Tachygram::random(&mut *rng)]);
        let right = TachygramSetPoly::from_iter([Tachygram::random(&mut *rng)]);

        let union = left.union(&right);
        assert_eq!(union.quotient(&right), Some(left.clone()));
        assert_eq!(union.quotient(&left), Some(right.clone()));
        assert_eq!(left.quotient(&right), None);
    }
}

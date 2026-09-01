//! # Multiset
//!
//! A multiset of members encoded as the roots of a monic polynomial, with
//! multiplicity:
//!
//! $$
//!   S(X) = \prod_{m \in S}{(X - m)^{\mathsf{count}(m)}}
//! $$
//!
//! ## Set form
//!
//! Unique factorization means the member multiset *is* the polynomial, so
//! [`Multiset`] keeps the members as its canonical representation -- a
//! [`BTreeMap`] count-map -- and defers realization into coefficient form
//! until [committed](Multiset::commit). Operating on the set form is much
//! cheaper: union is a count merge rather than a coefficient convolution, the
//! quotient witness is count subtraction rather than polynomial division, and
//! evaluation streams over members without materializing coefficients.
//!
//! The stamp sets built on this type are non-repeating in practice (a stamp's
//! tachygrams are unique on the wire), but the representation stays a general
//! multiset: a repeated member contributes a repeated factor, which is what
//! lets a commitment to $(X-m)^2$ stay distinguishable from one to $(X-m)$.

extern crate alloc;

use alloc::{
    collections::{BTreeMap, btree_map::Entry},
    vec::Vec,
};
use core::{cell::OnceCell, cmp::Eq as TotalEq, num::NonZero};

use ff::Field as _;
use pasta_curves::{Eq, Fp};
use ragu::{Polynomial, poly_with_roots};

/// A multiset of members held as polynomial roots, kept in set form.
///
/// The encoded [`Polynomial`] is realized lazily -- at first
/// [`realize`](Self::realize) or [`commit`](Self::commit) -- and memoized
/// until the next mutation. Equality considers the members only, never the
/// memoized realization.
///
/// # Construction
///
/// There is no `new`: collect members from any iterator, or
/// [`insert`](Self::insert)/[`Extend`] into an existing multiset.
#[derive(Clone, Debug, Default)]
pub(crate) struct Multiset {
    /// Member multiplicities, keyed by the member.
    members: BTreeMap<Fp, NonZero<u32>>,
    /// Memoized realization of the encoded polynomial.
    realized: OnceCell<Polynomial>,
    /// Memoized commitment to the realized polynomial.
    commitment: OnceCell<Eq>,
}

impl Multiset {
    /// Insert one member, incrementing its multiplicity.
    ///
    /// # Panics
    ///
    /// If one member's multiplicity exceeds `u32::MAX`, far beyond the
    /// realizable coefficient capacity.
    pub(crate) fn insert(&mut self, member: Fp) {
        self.reset_memo();
        match self.members.entry(member) {
            Entry::Occupied(mut occupied) => {
                #[expect(
                    clippy::expect_used,
                    reason = "a multiplicity beyond u32::MAX cannot be realized anyway"
                )]
                let bumped = occupied
                    .get()
                    .checked_add(1)
                    .expect("multiplicity overflow");
                *occupied.get_mut() = bumped;
            },
            Entry::Vacant(vacant) => {
                vacant.insert(NonZero::<u32>::MIN);
            },
        }
    }

    /// Multiset union: adds the multiplicities of the two operands, matching
    /// the product of their encoded polynomials.
    ///
    /// # Panics
    ///
    /// If one member's multiplicity exceeds `u32::MAX`, far beyond the
    /// realizable coefficient capacity.
    #[must_use]
    pub(crate) fn union(&self, other: &Self) -> Self {
        let mut members = self.members.clone();
        for (&key, &count) in &other.members {
            match members.entry(key) {
                Entry::Occupied(mut occupied) => {
                    #[expect(
                        clippy::expect_used,
                        reason = "a multiplicity beyond u32::MAX cannot be realized anyway"
                    )]
                    let merged = occupied
                        .get()
                        .checked_add(count.get())
                        .expect("multiplicity overflow");
                    *occupied.get_mut() = merged;
                },
                Entry::Vacant(vacant) => {
                    vacant.insert(count);
                },
            }
        }
        Self {
            members,
            ..Self::default()
        }
    }

    /// Multiset difference `self \ divisor`: the quotient witness of the
    /// encoded polynomials, computed by count subtraction instead of
    /// polynomial division.
    ///
    /// Returns [`None`] when `divisor` is not a sub-multiset of `self`, in
    /// which case no polynomial quotient exists either.
    #[must_use]
    pub(crate) fn quotient(&self, divisor: &Self) -> Option<Self> {
        let mut members = self.members.clone();
        for (&key, &needed) in &divisor.members {
            let Entry::Occupied(mut occupied) = members.entry(key) else {
                return None;
            };
            let remaining = occupied.get().get().checked_sub(needed.get())?;
            match NonZero::new(remaining) {
                Some(count) => *occupied.get_mut() = count,
                None => {
                    occupied.remove();
                },
            }
        }
        Some(Self {
            members,
            ..Self::default()
        })
    }

    /// Evaluate the encoded polynomial at `x` by streaming over the members,
    /// without realizing the coefficients. A repeated member contributes its
    /// factor by square-and-multiply; the (near-universal) multiplicity-one
    /// case pays no exponentiation at all.
    #[must_use]
    pub(crate) fn eval(&self, x: Fp) -> Fp {
        self.members
            .iter()
            .map(|(&member, &count)| {
                let factor = x - member;
                if count.get() == 1 {
                    factor
                } else {
                    factor.pow([NonZero::<u64>::from(count).get()])
                }
            })
            .product()
    }

    /// Realize (and memoize) the encoded polynomial in coefficient form.
    ///
    /// # Panics
    ///
    /// If the realization exceeds the polynomial coefficient cap.
    pub(crate) fn realize(&self) -> &Polynomial {
        self.realized.get_or_init(|| {
            let mut roots = Vec::new();
            for (&member, &count) in &self.members {
                for _ in 0..count.get() {
                    roots.push(member);
                }
            }
            Polynomial::from_coeffs(poly_with_roots(&roots))
        })
    }

    /// Deterministic (untrapdoored) commitment to the realized polynomial,
    /// memoized alongside the realization.
    ///
    /// # Panics
    ///
    /// If the realization exceeds the polynomial coefficient cap.
    #[must_use]
    pub(crate) fn commit(&self) -> Eq {
        *self.commitment.get_or_init(|| self.realize().commit())
    }

    fn reset_memo(&mut self) {
        self.realized.take();
        self.commitment.take();
    }
}

impl PartialEq for Multiset {
    fn eq(&self, other: &Self) -> bool {
        self.members == other.members
    }
}

impl TotalEq for Multiset {}

impl Extend<Fp> for Multiset {
    fn extend<T: IntoIterator<Item = Fp>>(&mut self, iter: T) {
        for member in iter {
            self.insert(member);
        }
    }
}

impl FromIterator<Fp> for Multiset {
    fn from_iter<T: IntoIterator<Item = Fp>>(iter: T) -> Self {
        let mut set = Self::default();
        set.extend(iter);
        set
    }
}

#[cfg(test)]
mod tests {
    use core::iter;

    use ff::Field as _;
    use rand::{SeedableRng as _, rngs::StdRng};

    use super::*;

    fn random_set(rng: &mut StdRng, len: usize) -> Multiset {
        iter::repeat_with(|| Fp::random(&mut *rng))
            .take(len)
            .collect()
    }

    #[test]
    fn streaming_evaluation_matches_the_realization() {
        let rng = &mut StdRng::seed_from_u64(12);
        for len in (0..6).chain([32]) {
            let set = random_set(rng, len);
            let x = Fp::random(&mut *rng);
            assert_eq!(set.eval(x), set.realize().eval(x));
        }
    }

    #[test]
    fn empty_multiset_encodes_the_constant_one() {
        let rng = &mut StdRng::seed_from_u64(14);
        let empty = Multiset::default();
        assert_eq!(empty.eval(Fp::random(&mut *rng)), Fp::ONE);
        assert_eq!(empty.realize().eval(Fp::random(rng)), Fp::ONE);
    }

    #[test]
    fn union_matches_realized_product() {
        let rng = &mut StdRng::seed_from_u64(17);
        let left = random_set(rng, 3);
        // The right operand overlaps the left entirely: shared members'
        // multiplicities add, exactly as the product's factors do.
        let right = random_set(rng, 4).union(&left);
        let union = left.union(&right);
        let x = Fp::random(&mut *rng);
        assert_eq!(union.eval(x), left.eval(x) * right.eval(x));
        assert_eq!(union.realize().eval(x), left.eval(x) * right.eval(x));
    }

    #[test]
    fn union_quotient_roundtrip() {
        let rng = &mut StdRng::seed_from_u64(23);
        let set = random_set(rng, 5);
        let complement = random_set(rng, 3);
        let union = set.union(&complement);
        assert_eq!(union.quotient(&complement), Some(set.clone()));
        assert_eq!(union.quotient(&set), Some(complement));
        assert_eq!(union.quotient(&union), Some(Multiset::default()));
    }

    #[test]
    fn quotient_by_non_sub_multiset_is_none() {
        let rng = &mut StdRng::seed_from_u64(29);
        let set = random_set(rng, 4);
        let disjoint = random_set(rng, 2);
        assert_eq!(set.quotient(&disjoint), None);

        // A divisor with excess multiplicity of a present member is not a
        // sub-multiset either.
        let doubled = set.union(&set);
        assert_eq!(set.quotient(&doubled), None);
        assert_eq!(doubled.quotient(&set), Some(set));
    }

    #[test]
    fn multiplicity_is_maintained() {
        let rng = &mut StdRng::seed_from_u64(31);
        let member = Fp::random(&mut *rng);
        let x = Fp::random(&mut *rng);

        let mut repeated = Multiset::default();
        repeated.insert(member);
        repeated.insert(member);

        let single_at_x = iter::once(member).collect::<Multiset>().eval(x);
        assert_eq!(repeated.eval(x), single_at_x.square());
        assert_eq!(repeated.realize().eval(x), single_at_x.square());
        assert_ne!(
            repeated.commit(),
            iter::once(member).collect::<Multiset>().commit()
        );

        // Structurally, the realization carries the repeated factor in full:
        // exactly (X - m)^2 = m^2 - 2mX + X^2, degree matching the total
        // multiplicity.
        let coeffs: Vec<Fp> = repeated.realize().iter_coeffs().collect();
        assert_eq!(
            coeffs.iter().rposition(|coeff| coeff != &Fp::ZERO),
            Some(2),
            "degree must equal the total multiplicity"
        );
        assert_eq!(
            coeffs[..3],
            [member.square(), -member.double(), Fp::ONE],
            "realization must be (X - m)^2 exactly"
        );
    }

    #[test]
    fn memoized_realization_resets_on_mutation() {
        let rng = &mut StdRng::seed_from_u64(37);
        let mut members: Vec<Fp> = iter::repeat_with(|| Fp::random(&mut *rng))
            .take(3)
            .collect();

        let mut set: Multiset = members.iter().copied().collect();
        let stale_commitment = set.commit();

        members.push(Fp::random(&mut *rng));
        set.insert(members[3]);

        assert_ne!(set.commit(), stale_commitment);
        assert_eq!(
            set.commit(),
            members.into_iter().collect::<Multiset>().commit()
        );
    }
}

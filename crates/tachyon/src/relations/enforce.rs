//! Steps confirm relations among committed polynomials through the two
//! framework hooks [`StepCtx::derive_challenge`] and
//! [`StepCtx::enforce_poly_query`]; [`with_shared_challenge`] packages the
//! discipline those hooks demand.
//!
//! The shape: the caller lists every committed polynomial operand up front;
//! the relation commits each one, derives a single challenge `z` from all
//! the commitments, and hands `z` plus a [`PolyQueries`] handle to the
//! caller's closure. What to do with the challenge is the caller's: which
//! operands to open, at which points (the challenge, a statement point,
//! several points on one operand), and which algebraic identities to check
//! over the opened evals. Each [`PolyQueries::open`] records the opening
//! claim `(commitment, point, eval)` and returns that same eval, so the
//! value checked is the value opened, by construction. The relation only
//! *records* claims; actually verifying them is the proof system's job, not
//! done here.
//!
//! The challenge is shared deliberately. In practice the proof system grants
//! a step one evaluation challenge, derived only once the whole transcript
//! is fixed, so the commitments must all be collected before the challenge
//! exists and every randomized point check must run at that one point.
//! Collecting the operands up front models this; deriving a fresh internal
//! challenge per relation would not survive the real prover. Steps that must
//! absorb scalar-binding points alongside their commitments (e.g.
//! `SpendBind`'s `G_0 · nf_next`) still derive their challenge inline, under
//! the same collect-first discipline.
//!
//! Soundness rests on Schwartz-Zippel: every operand commitment is absorbed
//! into `z`, so the operands are fixed *before* `z` exists, and an identity
//! among openings at a random `z` pins the corresponding polynomial identity
//! (a union bound over the closure's checks, error `~Σ deg/|F|`). An input
//! that is **not** a committed operand (a raw scalar, say) is not absorbed
//! into `z` and is not pinned this way: it must already be statement-fixed
//! -- a header-bound value, a value derived in-circuit from bound values, or
//! a free scalar pinned by a binding point absorbed into some challenge --
//! and the call site states each such input's pin.
//!
//! # Caller obligation: binding
//!
//! The openings prove identities among the polynomials passed; pinning
//! *which* polynomials those are is the caller's job. Every operand the
//! surrounding statement relies on must have its commitment grounded in a
//! statement-fixed value -- a public input, a prior-step output, a
//! transcript/header-absorbed value, or a consensus/output-checked
//! commitment -- and the binding holds only once that chain actually
//! terminates in such a value (a fresh witness, or a commitment merely
//! threaded onward, is not itself enough). The binding target is the
//! commitment *point* (`= operand.commit()`); trailing-zero coefficients
//! collapse under [`Polynomial::commit`], so this is commitment-identity,
//! not the literal coefficient vector.
//!
//! Implementation invariant: an eval enters an identity check only as an
//! [`PolyQueries::open`] return value, which is the eval recorded in that
//! opening's claim. A closure must never evaluate a polynomial itself -- a
//! recomputed or separately witnessed eval could diverge from the opened one
//! and break soundness.

use ff::Field as _;
use pasta_curves::{Eq, Fp};
use ragu::{Error, Result, ctx::StepCtx, polynomial::Polynomial};

/// The committed operands of one shared-challenge session: opens operands at
/// caller-chosen points, recording one claim per opening.
pub(crate) struct PolyQueries<'ctx, 'step, 'poly, const N: usize> {
    ctx: &'ctx mut StepCtx<'step>,
    operands: [&'poly Polynomial; N],
    commits: [Eq; N],
}

impl<const N: usize> PolyQueries<'_, '_, '_, N> {
    /// Open operand `index` at `point`: records the opening claim
    /// `(commitment, point, eval)` and returns the eval -- the one value
    /// that is both checked and opened.
    ///
    /// Errors on an out-of-range index (a call-site bug).
    pub(crate) fn open(&mut self, index: usize, point: Fp) -> Result<Fp> {
        let (operand, commit) = self
            .operands
            .get(index)
            .zip(self.commits.get(index))
            .ok_or_else(|| Error::InvalidWitness("poly query index out of range".into()))?;

        let eval = operand.eval(point);
        self.ctx.enforce_poly_query(*commit, point, eval)?;
        Ok(eval)
    }

    /// Open every operand at `point` (typically the shared challenge),
    /// returning the evals in operand order.
    pub(crate) fn open_all(&mut self, point: Fp) -> Result<[Fp; N]> {
        let mut evals = [Fp::ZERO; N];
        for (index, eval) in evals.iter_mut().enumerate() {
            *eval = self.open(index, point)?;
        }
        Ok(evals)
    }
}

/// Derive the step's shared Fiat-Shamir challenge over the given committed
/// operands, then run the caller's point checks.
///
/// Commits every operand, derives one challenge `z` absorbing all the
/// commitments, and calls `checks(z, queries)`: the closure opens whichever
/// operands its identities need, at `z` or at statement-fixed points, via
/// the [`PolyQueries`] handle, and states each identity as an
/// `enforce_zero`-style equation over the opened evals, `z`, and any
/// statement-fixed scalars it captures.
///
/// A step calls this once, listing every committed operand its point checks
/// touch, so all of them share the step's single challenge.
pub(crate) fn with_shared_challenge<'poly, const N: usize>(
    ctx: &mut StepCtx<'_>,
    operands: [&'poly Polynomial; N],
    checks: impl FnOnce(Fp, PolyQueries<'_, '_, 'poly, N>) -> Result<()>,
) -> Result<()> {
    let commits = operands.map(Polynomial::commit);
    let z = ctx.derive_challenge(&commits)?;

    checks(
        z,
        PolyQueries {
            ctx,
            operands,
            commits,
        },
    )
}

//! Stamp header and stamp-producing/transforming steps.

extern crate alloc;

use alloc::{vec, vec::Vec};

use pasta_curves::{Ep, Eq, Fp, Fq};
use ragu::{
    Header, Index, Step, Suffix,
    constraint::{enforce_equal_point, enforce_zero},
};

use super::{output::OutputHeader, pool::AnchorChain, spend::SpendHeader};
use crate::{
    ActionSetPoly, TachygramSetPoly,
    constants::MAX_MONEY,
    entropy::ActionRandomizer,
    keys::{ProofAuthorizingKey, private},
    note::Note,
    primitives::{ActionDigest, ActionSetCommit, Anchor, TachygramSetCommit, effect},
    relations::enforce::with_shared_challenge,
    value,
};

/// Header for a stamp, representing either a single action or many
/// transactions.
///
/// `action_commit` and `stamp_tg_commit` are Pedersen commitments to
/// the action-digest and tachygram sets. Per spec, only stamps carry
/// the tachygram accumulator (`stamp_tg_commit` = $\mathsf{tgacc}$).
/// Each leaf step ([`OutputStamp`], [`SpendStamp`]) witnesses both set
/// polynomials and enforces them against statement-fixed roots at the
/// step's shared Fiat-Shamir challenge (revisit.md `#acc-correct`) —
/// the action set
/// against the action the step derives, the tachygram set against the
/// pair bound on the left bind header. [`MergeStamp`] binds its
/// witnessed input sets to the child headers and enforces each output
/// commitment as the product of its inputs.
///
/// `anchor` is freely witnessed at [`OutputStamp`]; at [`SpendStamp`]
/// it threads from the left [`SpendHeader`]; at [`MergeStamp`]
/// the step constrains `left.anchor == right.anchor`; at
/// [`StampLift`] it advances to the right [`AnchorChain`] segment's
/// `end` after constraining `segment.start == old_anchor`.
#[derive(Debug)]
pub struct StampHeader;

impl Header for StampHeader {
    /// `(action_commit, stamp_tg_commit, anchor)`. The two commitments
    /// are enforced at each producing step per revisit.md
    /// `#acc-correct` against that step's action and the left bind
    /// header's tachygram pair. `anchor` is freely witnessed at
    /// [`OutputStamp`], threaded from the left [`SpendHeader`] at
    /// [`SpendStamp`], equality-constrained at [`MergeStamp`], or
    /// advanced over an [`AnchorChain`] at [`StampLift`].
    type Data = (ActionSetCommit, TachygramSetCommit, Anchor);

    const SUFFIX: Suffix = Suffix::new(11);

    fn encode(data: &Self::Data) -> (Vec<Fp>, Vec<Fq>, Vec<Ep>, Vec<Eq>) {
        (
            vec![Fp::from(data.2)],
            Vec::new(),
            Vec::new(),
            vec![Eq::from(data.0), Eq::from(data.1)],
        )
    }
}

/// Proves an output's action and publishes its stamp.
///
/// Mirrors [`SpendStamp`]: re-witnesses the note (bound to the
/// [`OutputHeader`]'s `cm`), derives the value commitment `cv` and the
/// randomized action key `rk`, and enforces the one-action set plus the
/// stamp accumulator over the two-element tachygram set `{cm, pad}` that
/// [`OutputBind`](super::output::OutputBind) already settled.
#[derive(Debug)]
pub struct OutputStamp;

impl Step for OutputStamp {
    type Aux<'source> = ();
    type Left = OutputHeader;
    type Output = StampHeader;
    type Right = ();
    /// `(rcv, alpha, note, anchor, action_set, tachygram_set)`.
    type Witness<'source> = (
        value::Trapdoor,
        ActionRandomizer<effect::Output>,
        Note,
        Anchor,
        ActionSetPoly,
        TachygramSetPoly,
    );

    const INDEX: Index = Index::new(11);

    fn witness<'source>(
        &self,
        ctx: &mut ragu::StepCtx<'_>,
        (rcv, alpha, note, anchor, action_set, tachygram_set): Self::Witness<'source>,
        (cm, pad): <Self::Left as Header>::Data,
        _right: <Self::Right as Header>::Data,
    ) -> ragu::Result<(<Self::Output as Header>::Data, Self::Aux<'source>)> {
        if u64::from(note.value) > MAX_MONEY {
            return Err(ragu::Error::InvalidWitness(
                "OutputStamp: note value exceeds maximum".into(),
            ));
        }
        enforce_zero(
            Fp::from(note.commitment()) - Fp::from(cm),
            "OutputStamp: note does not match the bound output",
        )?;

        let cv = rcv.commit(-note.value);
        let rk = private::ActionSigningKey::new(&alpha).derive_action_public();
        let action_digest = ActionDigest::new(cv, rk).map_err(|_err| {
            ragu::Error::InvalidWitness("OutputStamp: action digest construction failed".into())
        })?;

        // Both witnessed sets open at the step's shared challenge and must
        // equal the product of their statement-fixed root factors: the action
        // digest is in-circuit from the witnessed note above; the tachygram
        // pair rides the bind header, fixed by the recursive verification of
        // the left PCD.
        with_shared_challenge(
            ctx,
            [action_set.as_ref(), tachygram_set.as_ref()],
            |z, mut queries| {
                let [action_at_z, tachygrams_at_z] = queries.open_all(z)?;
                enforce_zero(
                    action_at_z - (z - Fp::from(action_digest)),
                    "OutputStamp: action set does not commit to the action",
                )?;
                enforce_zero(
                    tachygrams_at_z - (z - Fp::from(cm)) * (z - Fp::from(pad)),
                    "OutputStamp: tachygram set does not commit to the bound pair",
                )
            },
        )?;

        Ok(((action_set.commit(), tachygram_set.commit(), anchor), ()))
    }
}

/// Proves a spend's action and publishes its stamp.
///
/// Focused like [`OutputStamp`] on the action: re-witnesses the spent note
/// (bound to the [`SpendHeader`]'s `cm`), derives the value commitment `cv`
/// and the randomized action key `rk`, and enforces the one-action set plus
/// the stamp accumulator over the two-element tachygram set
/// `{present_nf, nf_next}` (the pair [`SpendBind`](super::spend::SpendBind)
/// already confirmed against the covering derivation).
#[derive(Debug)]
pub struct SpendStamp;

impl Step for SpendStamp {
    type Aux<'source> = ();
    type Left = SpendHeader;
    type Output = StampHeader;
    type Right = ();
    /// `(note, rcv, alpha, pak, action_set, tachygram_set)`.
    type Witness<'source> = (
        Note,
        value::Trapdoor,
        ActionRandomizer<effect::Spend>,
        ProofAuthorizingKey,
        ActionSetPoly,
        TachygramSetPoly,
    );

    const INDEX: Index = Index::new(13);

    fn witness<'source>(
        &self,
        ctx: &mut ragu::StepCtx<'_>,
        (note, rcv, alpha, pak, action_set, tachygram_set): Self::Witness<'source>,
        (cm, present_nf, nf_next, anchor): <Self::Left as Header>::Data,
        _right: <Self::Right as Header>::Data,
    ) -> ragu::Result<(<Self::Output as Header>::Data, Self::Aux<'source>)> {
        if u64::from(note.value) > MAX_MONEY {
            return Err(ragu::Error::InvalidWitness(
                "SpendStamp: note value exceeds maximum".into(),
            ));
        }
        enforce_zero(
            Fp::from(note.pk) - Fp::from(pak.derive_payment_key()),
            "SpendStamp: pak not related to note",
        )?;
        enforce_zero(
            Fp::from(note.commitment()) - Fp::from(cm),
            "SpendStamp: note does not match the spend",
        )?;

        let cv = rcv.commit(note.value);
        let rk = pak.ak.derive_action_public(&alpha);
        let action_digest = ActionDigest::new(cv, rk).map_err(|_err| {
            ragu::Error::InvalidWitness("SpendStamp: action digest construction failed".into())
        })?;

        // Both witnessed sets open at the step's shared challenge and must
        // equal the product of their statement-fixed root factors: the action
        // digest is in-circuit from the witnessed note above; the nullifier
        // pair rides the bind header, fixed by the recursive verification of
        // the left PCD.
        with_shared_challenge(
            ctx,
            [action_set.as_ref(), tachygram_set.as_ref()],
            |z, mut queries| {
                let [action_at_z, tachygrams_at_z] = queries.open_all(z)?;
                enforce_zero(
                    action_at_z - (z - Fp::from(action_digest)),
                    "SpendStamp: action set does not commit to the action",
                )?;
                enforce_zero(
                    tachygrams_at_z - (z - Fp::from(present_nf)) * (z - Fp::from(nf_next)),
                    "SpendStamp: tachygram set does not commit to the nullifier pair",
                )
            },
        )?;

        Ok(((action_set.commit(), tachygram_set.commit(), anchor), ()))
    }
}

/// Transaction assembly and aggregation.
#[derive(Debug)]
pub struct MergeStamp;

impl Step for MergeStamp {
    type Aux<'source> = ();
    type Left = StampHeader;
    type Output = StampHeader;
    type Right = StampHeader;
    /// `(left, merged, right)`, each an `(action_set, tachygram_set)` pair.
    type Witness<'source> = (
        (ActionSetPoly, TachygramSetPoly),
        (ActionSetPoly, TachygramSetPoly),
        (ActionSetPoly, TachygramSetPoly),
    );

    const INDEX: Index = Index::new(14);

    fn witness<'source>(
        &self,
        ctx: &mut ragu::StepCtx<'_>,
        (
            (left_action_set, left_tachygram_set),
            (merged_action_set, merged_tachygram_set),
            (right_action_set, right_tachygram_set),
        ): Self::Witness<'source>,
        (left_action_commit, left_tachygram_commit, left_anchor): <Self::Left as Header>::Data,
        (right_action_commit, right_tachygram_commit, right_anchor): <Self::Right as Header>::Data,
    ) -> ragu::Result<(<Self::Output as Header>::Data, Self::Aux<'source>)> {
        // Same-anchor constraint.
        enforce_zero(
            Fp::from(left_anchor) - Fp::from(right_anchor),
            "MergeStamp: anchors must match",
        )?;

        // Bind the witnessed left/right input sets to the public commitments on
        // the headers.
        enforce_equal_point(
            Eq::from(left_action_set.commit()),
            Eq::from(left_action_commit),
            "MergeStamp: left action accumulator must commit to header commit",
        )?;
        enforce_equal_point(
            Eq::from(right_action_set.commit()),
            Eq::from(right_action_commit),
            "MergeStamp: right action accumulator must commit to header commit",
        )?;
        enforce_equal_point(
            Eq::from(left_tachygram_set.commit()),
            Eq::from(left_tachygram_commit),
            "MergeStamp: left tachygram accumulator must commit to header commit",
        )?;
        enforce_equal_point(
            Eq::from(right_tachygram_set.commit()),
            Eq::from(right_tachygram_commit),
            "MergeStamp: right tachygram accumulator must commit to header commit",
        )?;

        // Confirm both unions at the step's shared challenge: all six
        // commitments are absorbed before it is derived, and each merged set
        // must open to the product of its inputs' openings.
        with_shared_challenge(
            ctx,
            [
                left_action_set.as_ref(),
                right_action_set.as_ref(),
                merged_action_set.as_ref(),
                left_tachygram_set.as_ref(),
                right_tachygram_set.as_ref(),
                merged_tachygram_set.as_ref(),
            ],
            |z, mut queries| {
                let [
                    left_action,
                    right_action,
                    merged_action,
                    left_tg,
                    right_tg,
                    merged_tg,
                ] = queries.open_all(z)?;
                enforce_zero(
                    merged_action - left_action * right_action,
                    "MergeStamp: merged action set must be the product of left and right action sets",
                )?;
                enforce_zero(
                    merged_tg - left_tg * right_tg,
                    "MergeStamp: merged tachygram set must be the product of left and right tachygram sets",
                )
            },
        )?;

        Ok((
            (
                merged_action_set.commit(),
                merged_tachygram_set.commit(),
                left_anchor,
            ),
            (),
        ))
    }
}

/// Advance a stamp's anchor by absorbing an [`AnchorChain`]: the
/// segment's `start` must equal the stamp's `old_anchor`, and the new
/// anchor is the segment's `end`.
#[derive(Debug)]
pub struct StampLift;

impl Step for StampLift {
    type Aux<'source> = ();
    type Left = StampHeader;
    type Output = StampHeader;
    type Right = AnchorChain;
    type Witness<'source> = ();

    const INDEX: Index = Index::new(15);

    fn witness<'source>(
        &self,
        _ctx: &mut ragu::StepCtx<'_>,
        (): Self::Witness<'source>,
        (left_action_commit, left_tachygram_commit, old_anchor): <Self::Left as Header>::Data,
        (segment_start, segment_end): <Self::Right as Header>::Data,
    ) -> ragu::Result<(<Self::Output as Header>::Data, Self::Aux<'source>)> {
        // The anchor segment must root at the stamp's old anchor.
        enforce_zero(
            Fp::from(segment_start) - Fp::from(old_anchor),
            "StampLift: segment start must equal stamp old_anchor",
        )?;

        let data = (left_action_commit, left_tachygram_commit, segment_end);
        Ok((data, ()))
    }
}

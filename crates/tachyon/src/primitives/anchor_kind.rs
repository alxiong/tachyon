//! Compile-time provenance markers for anchors.
//!
//! [`Stamped`] and [`Sentinel`] are zero-sized marker types recording how an
//! [`Anchor`](super::Anchor) was produced: [`Anchor::next_stamp`] mints a
//! `Anchor<Stamped>` and [`Anchor::next_epoch`] mints a `Anchor<Sentinel>`, so
//! a typed anchor certifies which domain-separated hash produced it. [`Erased`]
//! marks the positions where an anchor's kind is not statically knowable: the
//! wire (which carries no kind tag), free step witnesses, and header slots that
//! legitimately admit either kind. Erasure is explicit and one-way via
//! [`Anchor::erase`]; the reverse direction is the documented, unchecked
//! [`Anchor::assume`].
//!
//! The markers never reach circuits, hashes, or serialized bytes; they are
//! host-side API clarity only.
//!
//! [`Anchor::next_stamp`]: super::Anchor::next_stamp
//! [`Anchor::next_epoch`]: super::Anchor::next_epoch
//! [`Anchor::erase`]: super::Anchor::erase
//! [`Anchor::assume`]: super::Anchor::assume

use derive_more::{Debug, Eq as TotalEq, PartialEq};

mod sealed {
    pub trait Sealed: Copy {}
    impl Sealed for super::Erased {}
    impl Sealed for super::Stamped {}
    impl Sealed for super::Sentinel {}
}

/// Sealed trait marking an anchor's provenance kind.
pub trait AnchorKind: sealed::Sealed + Send + Sync + 'static {}

/// Kind-unknown anchor marker: the wire, free witnesses, and mixed header
/// slots.
///
/// This is the default kind, so a bare `Anchor` is an anchor of unknown
/// provenance.
#[derive(Clone, Copy, Debug, Ord, PartialEq, PartialOrd, TotalEq)]
pub struct Erased;

/// Marker for an anchor produced by a stamp advancement
/// ([`Anchor::next_stamp`](super::Anchor::next_stamp)).
#[derive(Clone, Copy, Debug, Ord, PartialEq, PartialOrd, TotalEq)]
pub struct Stamped;

/// Marker for an epoch-boundary anchor (a *sentinel*, also called the boundary
/// domain), produced by an epoch tick
/// ([`Anchor::next_epoch`](super::Anchor::next_epoch)).
#[derive(Clone, Copy, Debug, Ord, PartialEq, PartialOrd, TotalEq)]
pub struct Sentinel;

impl AnchorKind for Erased {}
impl AnchorKind for Stamped {}
impl AnchorKind for Sentinel {}

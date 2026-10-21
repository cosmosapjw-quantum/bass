# (no title)
URL: https://raw.githubusercontent.com/Lokathor/wide/main/Cargo.toml

[package]
name = "wide"
description = "A crate to help you go wide."
version = "1.7.1"
authors = ["Lokathor <zefria@gmail.com>"]
autotests = false
repository = "https://github.com/Lokathor/wide"
readme = "README.md"
keywords = ["simd", "wide", "lokathor"]
categories = ["data-structures", "hardware-support"]
edition = "2024"
license = "Zlib OR Apache-2.0 OR MIT"

# When updating, also update CI workflows and the badge in the README.
rust-version = "1.89"

[features]
default = ["std"]

# Activate `std` within the crate. Currently this gives a much faster `sqrt`
# impl when an explicit hardware sqrt isn't available.
std = []
serde = ["dep:serde_core"]

[dependencies]
serde_core = { version = "1", default-features = false, optional = true }
bytemuck = { version = "1.24.0", features = ["avx512_simd"] }

[dev-dependencies]
bincode = { version = "1.3.3" }
criterion = { version = "0.7.0", default-features = false }

[[test]]
name = "tests"
path = "tests/main.rs"

[[bench]]
name = "fma_benchmarks"
harness = false

[[bench]]
name = "math_benchmarks"
harness = false

[[bench]]
name = "u8_shift"
harness = false


# (no title)
URL: https://raw.githubusercontent.com/sarah-quinones/pulp/main/pulp/Cargo.toml

[package]
name = "pulp"
version = "0.23.0"
edition = "2024"
authors = ["sarah quiñones <sarah@veganb.tw>"]
description = "safe generic simd"
readme = "../README.md"
repository = "https://github.com/sarah-quinones/pulp/"
license = "MIT"
keywords = ["simd"]

[dependencies]
pulp-macro = { version = "0.1.1", path = "../pulp-macro", optional = true }
pulp-wasm-simd-flag = { version = "0.1.1", path = "../pulp-wasm-simd-flag", default-features = false }
bytemuck = { version = "1.15", features = ["aarch64_simd", "wasm_simd"] }
num-complex = { version = "0.4.4", default-features = false, features = ["bytemuck"] }
libm = { version = "0.2", default-features = false }
reborrow = "0.5"
cfg-if = "1.0.0"
pastey = "0.2"

[target.'cfg(any(target_arch = "x86", target_arch = "x86_64"))'.dependencies]
raw-cpuid = { version = "11.5.0", default-features = false }

[features]
default = [
 "std",
 "x86-v3",
 "relaxed-simd",
]
nightly = [
 "bytemuck/nightly_stdsimd",
]
std = []

x86-v3 = []
x86-v4 = [ "bytemuck/avx512_simd" ]

relaxed-simd = ["pulp-wasm-simd-flag/relaxed-simd"]

macro = ["dep:pulp-macro"]

[dev-dependencies]
aligned-vec = "0.6.0"
assert_approx_eq = "1.1.0"
criterion = "0.5.0"
diol = { version = "0.8.3", default-features = false }
rand = "0.8.5"

[build-dependencies]
version_check = "0.9.5"

[[bench]]
name = "bench"
harness = false

[[example]]
name = "dot_product"
doc-scrape-examples = true

[[example]]
name = "basic"
doc-scrape-examples = true

[package.metadata.docs.rs]
all-features = true
rustdoc-args = ["--cfg", "docsrs"]
cargo-args = ["-Zunstable-options", "-Zrustdoc-scrape-examples"]
targets = [
 "x86_64-unknown-linux-gnu",
 "aarch64-apple-darwin",
 "wasm32-unknown-unknown",
]


# (no title)
URL: https://raw.githubusercontent.com/rayon-rs/rayon/v1.12.0/src/iter/mod.rs

//! Traits for writing parallel programs using an iterator-style interface
//!
//! You will rarely need to interact with this module directly unless you have
//! need to name one of the iterator types.
//!
//! Parallel iterators make it easy to write iterator-like chains that
//! execute in parallel: typically all you have to do is convert the
//! first `.iter()` (or `iter_mut()`, `into_iter()`, etc) method into
//! `par_iter()` (or `par_iter_mut()`, `into_par_iter()`, etc). For
//! example, to compute the sum of the squares of a sequence of
//! integers, one might write:
//!
//! ```rust
//! use rayon::prelude::*;
//! fn sum_of_squares(input: &[i32]) -> i32 {
//! input.par_iter()
//! .map(|i| i * i)
//! .sum()
//! }
//! ```
//!
//! Or, to increment all the integers in a slice, you could write:
//!
//! ```rust
//! use rayon::prelude::*;
//! fn increment_all(input: &mut [i32]) {
//! input.par_iter_mut()
//! .for_each(|p| *p += 1);
//! }
//! ```
//!
//! To use parallel iterators, first import the traits by adding
//! something like `use rayon::prelude::*` to your module. You can
//! then call `par_iter`, `par_iter_mut`, or `into_par_iter` to get a
//! parallel iterator. Like a [regular iterator][], parallel
//! iterators work by first constructing a computation and then
//! executing it.
//!
//! In addition to `par_iter()` and friends, some types offer other
//! ways to create (or consume) parallel iterators:
//!
//! - Slices (`&[T]`, `&mut [T]`) offer methods like `par_split` and
//! `par_windows`, as well as various parallel sorting
//! operations. See [the `ParallelSlice` trait] for the full list.
//! - Strings (`&str`) offer methods like `par_split` and `par_lines`.
//! See [the `ParallelString` trait] for the full list.
//! - Various collections offer [`par_extend`], which grows a
//! collection given a parallel iterator. (If you don't have a
//! collection to extend, you can use [`collect()`] to create a new
//! one from scratch.)
//!
//! [the `ParallelSlice` trait]: crate::slice::ParallelSlice
//! [the `ParallelString` trait]: crate::str::ParallelString
//! [`par_extend`]: ParallelExtend
//! [`collect()`]: ParallelIterator::collect()
//!
//! To see the full range of methods available on parallel iterators,
//! check out the [`ParallelIterator`] and [`IndexedParallelIterator`]
//! traits.
//!
//! If you'd like to build a custom parallel iterator, or to write your own
//! combinator, then check out the [split] function and the [plumbing] module.
//!
//! [regular iterator]: Iterator
//! [split]: split()
//! [plumbing]: plumbing
//!
//! Note: Several of the `ParallelIterator` methods rely on a `Try` trait which
//! has been deliberately obscured from the public API. This trait is intended
//! to mirror the unstable `std::ops::Try` with implementations for `Option` and
//! `Result`, where `Some`/`Ok` values will let those iterators continue, but
//! `None`/`Err` values will exit early.
//!
//! A note about
//! [dyn compatiblity](https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility):
//! It is currently _not_ possible to wrap a `ParallelIterator` (or any trait
//! that depends on it) using a `Box ` or other kind of
//! dynamic allocation, because `ParallelIterator` is **not dyn-compatible**.
//! (This keeps the implementation simpler and allows extra optimizations.)

use self::plumbing::*;
use self::private::Try;
pub use either::Either;
use std::cmp::Ordering;
use std::collections::LinkedList;
use std::iter::{Product, Sum};
use std::ops::{Fn, RangeBounds};

pub mod plumbing;

#[cfg(test)]
mod test;

// There is a method to the madness here:
//
// - These modules are private but expose certain types to the end-user
// (e.g., `enumerate::Enumerate`) -- specifically, the types that appear in the
// public API surface of the `ParallelIterator` traits.
// - In **this** module, those public types are always used unprefixed, which forces
// us to add a `pub use` and helps identify if we missed anything.
// - In contrast, items that appear **only** in the body of a method,
// e.g. `find::find()`, are always used **prefixed**, so that they
// can be readily distinguished.

mod blocks;
mod chain;
mod chunks;
mod cloned;
mod collect;
mod copied;
mod empty;
mod enumerate;
mod extend;
mod filter;
mod filter_map;
mod find;
mod find_first_last;
mod flat_map;
mod flat_map_iter;
mod flatten;
mod flatten_iter;
mod fold;
mod fold_chunks;
mod fold_chunks_with;
mod for_each;
mod from_par_iter;
mod inspect;
mod interleave;
mod interleave_shortest;
mod intersperse;
mod len;
mod map;
mod map_with;
mod multizip;
mod noop;
mod once;
mod panic_fuse;
mod par_bridge;
mod positions;
mod product;
mod reduce;
mod repeat;
mod rev;
mod skip;
mod skip_any;
mod skip_any_while;
mod splitter;
mod step_by;
mod sum;
mod take;
mod take_any;
mod take_any_while;
mod try_fold;
mod try_reduce;
mod try_reduce_with;
mod unzip;
mod update;
mod walk_tree;
mod while_some;
mod zip;
mod zip_eq;

pub use self::{
 blocks::{ExponentialBlocks, UniformBlocks},
 chain::Chain,
 chunks::Chunks,
 cloned::Cloned,
 copied::Copied,
 empty::{empty, Empty},
 enumerate::Enumerate,
 filter::Filter,
 filter_map::FilterMap,
 flat_map::FlatMap,
 flat_map_iter::FlatMapIter,
 flatten::Flatten,
 flatten_iter::FlattenIter,
 fold::{Fold, FoldWith},
 fold_chunks::FoldChunks,
 fold_chunks_with::FoldChunksWith,
 inspect::Inspect,
 interleave::Interleave,
 interleave_shortest::InterleaveShortest,
 intersperse::Intersperse,
 len::{MaxLen, MinLen},
 map::Map,
 map_with::{MapInit, MapWith},
 multizip::MultiZip,
 once::{once, Once},
 panic_fuse::PanicFuse,
 par_bridge::{IterBridge, ParallelBridge},
 positions::Positions,
 repeat::{repeat, repeat_n, Repeat, RepeatN},
 rev::Rev,
 skip::Skip,
 skip_any::SkipAny,
 skip_any_while::SkipAnyWhile,
 splitter::{split, Split},
 step_by::StepBy,
 take::Take,
 take_any::TakeAny,
 take_any_while::TakeAnyWhile,
 try_fold::{TryFold, TryFoldWith},
 update::Update,
 walk_tree::{
 walk_tree, walk_tree_postfix, walk_tree_prefix, WalkTree, WalkTreePostfix, WalkTreePrefix,
 },
 while_some::WhileSome,
 zip::Zip,
 zip_eq::ZipEq,
};

#[allow(deprecated)]
pub use repeat::repeatn;

/// `IntoParallelIterator` implements the conversion to a [`ParallelIterator`].
///
/// By implementing `IntoParallelIterator` for a type, you define how it will
/// transformed into an iterator. This is a parallel version of the standard
/// library's [`std::iter::IntoIterator`] trait.
pub trait IntoParallelIterator {
 /// The parallel iterator type that will be created.
 type Iter: ParallelIterator;

 /// The type of item that the parallel iterator will produce.
 type Item: Send;

 /// Converts `self` into a parallel iterator.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// println!("counting in parallel:");
 /// (0..100).into_par_iter()
 /// .for_each(|i| println!("{}", i));
 /// ```
 ///
 /// This conversion is often implicit for arguments to methods like [`zip`].
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let v: Vec<_> = (0..5).into_par_iter().zip(5..10).collect();
 /// assert_eq!(v, [(0, 5), (1, 6), (2, 7), (3, 8), (4, 9)]);
 /// ```
 ///
 /// [`zip`]: IndexedParallelIterator::zip()
 fn into_par_iter(self) -> Self::Iter;
}

/// `IntoParallelRefIterator` implements the conversion to a
/// [`ParallelIterator`], providing shared references to the data.
///
/// This is a parallel version of the `iter()` method
/// defined by various collections.
///
/// This trait is automatically implemented
/// `for I where &I: IntoParallelIterator`. In most cases, users
/// will want to implement [`IntoParallelIterator`] rather than implement
/// this trait directly.
pub trait IntoParallelRefIterator<'data> {
 /// The type of the parallel iterator that will be returned.
 type Iter: ParallelIterator;

 /// The type of item that the parallel iterator will produce.
 /// This will typically be an `&'data T` reference type.
 type Item: Send + 'data;

 /// Converts `self` into a parallel iterator.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let v: Vec<_> = (0..100).collect();
 /// assert_eq!(v.par_iter().sum:: (), 100 * 99 / 2);
 ///
 /// // `v.par_iter()` is shorthand for `(&v).into_par_iter()`,
 /// // producing the exact same references.
 /// assert!(v.par_iter().zip(&v)
 /// .all(|(a, b)| std::ptr::eq(a, b)));
 /// ```
 fn par_iter(&'data self) -> Self::Iter;
}

impl<'data, I: 'data + ?Sized> IntoParallelRefIterator<'data> for I
where
 &'data I: IntoParallelIterator,
{
 type Iter = <&'data I as IntoParallelIterator>::Iter;
 type Item = <&'data I as IntoParallelIterator>::Item;

 fn par_iter(&'data self) -> Self::Iter {
 self.into_par_iter()
 }
}

/// `IntoParallelRefMutIterator` implements the conversion to a
/// [`ParallelIterator`], providing mutable references to the data.
///
/// This is a parallel version of the `iter_mut()` method
/// defined by various collections.
///
/// This trait is automatically implemented
/// `for I where &mut I: IntoParallelIterator`. In most cases, users
/// will want to implement [`IntoParallelIterator`] rather than implement
/// this trait directly.
pub trait IntoParallelRefMutIterator<'data> {
 /// The type of iterator that will be created.
 type Iter: ParallelIterator;

 /// The type of item that will be produced; this is typically an
 /// `&'data mut T` reference.
 type Item: Send + 'data;

 /// Creates the parallel iterator from `self`.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let mut v = vec![0usize; 5];
 /// v.par_iter_mut().enumerate().for_each(|(i, x)| *x = i);
 /// assert_eq!(v, [0, 1, 2, 3, 4]);
 /// ```
 fn par_iter_mut(&'data mut self) -> Self::Iter;
}

impl<'data, I: 'data + ?Sized> IntoParallelRefMutIterator<'data> for I
where
 &'data mut I: IntoParallelIterator,
{
 type Iter = <&'data mut I as IntoParallelIterator>::Iter;
 type Item = <&'data mut I as IntoParallelIterator>::Item;

 fn par_iter_mut(&'data mut self) -> Self::Iter {
 self.into_par_iter()
 }
}

/// Parallel version of the standard iterator trait.
///
/// The combinators on this trait are available on **all** parallel
/// iterators. Additional methods can be found on the
/// [`IndexedParallelIterator`] trait: those methods are only
/// available for parallel iterators where the number of items is
/// known in advance (so, e.g., after invoking `filter`, those methods
/// become unavailable).
///
/// For examples of using parallel iterators, see [the docs on the
/// `iter` module][iter].
///
/// [iter]: self
pub trait ParallelIterator: Sized + Send {
 /// The type of item that this parallel iterator produces.
 /// For example, if you use the [`for_each`] method, this is the type of
 /// item that your closure will be invoked with.
 ///
 /// [`for_each`]: #method.for_each
 type Item: Send;

 /// Executes `OP` on each item produced by the iterator, in parallel.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// (0..100).into_par_iter().for_each(|x| println!("{:?}", x));
 /// ```
 fn for_each (self, op: OP)
 where
 OP: Fn(Self::Item) + Sync + Send,
 {
 for_each::for_each(self, &op)
 }

 /// Executes `OP` on the given `init` value with each item produced by
 /// the iterator, in parallel.
 ///
 /// The `init` value will be cloned only as needed to be paired with
 /// the group of items in each rayon job. It does not require the type
 /// to be `Sync`.
 ///
 /// # Examples
 ///
 /// ```
 /// use std::sync::mpsc::channel;
 /// use rayon::prelude::*;
 ///
 /// let (sender, receiver) = channel();
 ///
 /// (0..5).into_par_iter().for_each_with(sender, |s, x| s.send(x).unwrap());
 ///
 /// let mut res: Vec<_> = receiver.iter().collect();
 ///
 /// res.sort();
 ///
 /// assert_eq!(&res[..], &[0, 1, 2, 3, 4])
 /// ```
 fn for_each_with<OP, T>(self, init: T, op: OP)
 where
 OP: Fn(&mut T, Self::Item) + Sync + Send,
 T: Send + Clone,
 {
 self.map_with(init, op).collect()
 }

 /// Executes `OP` on a value returned by `init` with each item produced by
 /// the iterator, in parallel.
 ///
 /// The `init` function will be called only as needed for a value to be
 /// paired with the group of items in each rayon job. There is no
 /// constraint on that returned type at all!
 ///
 /// # Examples
 ///
 /// ```
 /// use rand::Rng;
 /// use rayon::prelude::*;
 ///
 /// let mut v = vec![0u8; 1_000_000];
 ///
 /// v.par_chunks_mut(1000)
 /// .for_each_init(
 /// || rand::rng(),
 /// |rng, chunk| rng.fill(chunk),
 /// );
 ///
 /// // There's a remote chance that this will fail...
 /// for i in 0u8..=255 {
 /// assert!(v.contains(&i));
 /// }
 /// ```
 fn for_each_init<OP, INIT, T>(self, init: INIT, op: OP)
 where
 OP: Fn(&mut T, Self::Item) + Sync + Send,
 INIT: Fn() -> T + Sync + Send,
 {
 self.map_init(init, op).collect()
 }

 /// Executes a fallible `OP` on each item produced by the iterator, in parallel.
 ///
 /// If the `OP` returns `Result::Err` or `Option::None`, we will attempt to
 /// stop processing the rest of the items in the iterator as soon as
 /// possible, and we will return that terminating value. Otherwise, we will
 /// return an empty `Result::Ok(())` or `Option::Some(())`. If there are
 /// multiple errors in parallel, it is not specified which will be returned.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 /// use std::io::{self, Write};
 ///
 /// // This will stop iteration early if there's any write error, like
 /// // having piped output get closed on the other end.
 /// (0..100).into_par_iter()
 /// .try_for_each(|x| writeln!(io::stdout(), "{:?}", x))
 /// .expect("expected no write errors");
 /// ```
 fn try_for_each<OP, R>(self, op: OP) -> R
 where
 OP: Fn(Self::Item) -> R + Sync + Send,
 R: Try + Send,
 {
 fn ok >(_: (), _: ()) -> R {
 R::from_output(())
 }

 self.map(op).try_reduce(<()>::default, ok)
 }

 /// Executes a fallible `OP` on the given `init` value with each item
 /// produced by the iterator, in parallel.
 ///
 /// This combines the `init` semantics of [`for_each_with()`] and the
 /// failure semantics of [`try_for_each()`].
 ///
 /// [`for_each_with()`]: #method.for_each_with
 /// [`try_for_each()`]: #method.try_for_each
 ///
 /// # Examples
 ///
 /// ```
 /// use std::sync::mpsc::channel;
 /// use rayon::prelude::*;
 ///
 /// let (sender, receiver) = channel();
 ///
 /// (0..5).into_par_iter()
 /// .try_for_each_with(sender, |s, x| s.send(x))
 /// .expect("expected no send errors");
 ///
 /// let mut res: Vec<_> = receiver.iter().collect();
 ///
 /// res.sort();
 ///
 /// assert_eq!(&res[..], &[0, 1, 2, 3, 4])
 /// ```
 fn try_for_each_with<OP, T, R>(self, init: T, op: OP) -> R
 where
 OP: Fn(&mut T, Self::Item) -> R + Sync + Send,
 T: Send + Clone,
 R: Try + Send,
 {
 fn ok >(_: (), _: ()) -> R {
 R::from_output(())
 }

 self.map_with(init, op).try_reduce(<()>::default, ok)
 }

 /// Executes a fallible `OP` on a value returned by `init` with each item
 /// produced by the iterator, in parallel.
 ///
 /// This combines the `init` semantics of [`for_each_init()`] and the
 /// failure semantics of [`try_for_each()`].
 ///
 /// [`for_each_init()`]: #method.for_each_init
 /// [`try_for_each()`]: #method.try_for_each
 ///
 /// # Examples
 ///
 /// ```
 /// use rand::{Rng, TryRngCore};
 /// use rayon::prelude::*;
 ///
 /// let mut v = vec![0u8; 1_000_000];
 ///
 /// v.par_chunks_mut(1000)
 /// .try_for_each_init(
 /// || rand::rng(),
 /// |rng, chunk| rng.try_fill_bytes(chunk),
 /// )
 /// .expect("expected no rand errors");
 ///
 /// // There's a remote chance that this will fail...
 /// for i in 0u8..=255 {
 /// assert!(v.contains(&i));
 /// }
 /// ```
 fn try_for_each_init<OP, INIT, T, R>(self, init: INIT, op: OP) -> R
 where
 OP: Fn(&mut T, Self::Item) -> R + Sync + Send,
 INIT: Fn() -> T + Sync + Send,
 R: Try + Send,
 {
 fn ok >(_: (), _: ()) -> R {
 R::from_output(())
 }

 self.map_init(init, op).try_reduce(<()>::default, ok)
 }

 /// Counts the number of items in this parallel iterator.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let count = (0..100).into_par_iter().count();
 ///
 /// assert_eq!(count, 100);
 /// ```
 fn count(self) -> usize {
 fn one (_: T) -> usize {
 1
 }

 self.map(one).sum()
 }

 /// Applies `map_op` to each item of this iterator, producing a new
 /// iterator with the results.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let mut par_iter = (0..5).into_par_iter().map(|x| x * 2);
 ///
 /// let doubles: Vec<_> = par_iter.collect();
 ///
 /// assert_eq!(&doubles[..], &[0, 2, 4, 6, 8]);
 /// ```
 fn map<F, R>(self, map_op: F) -> Map<Self, F>
 where
 F: Fn(Self::Item) -> R + Sync + Send,
 R: Send,
 {
 Map::new(self, map_op)
 }

 /// Applies `map_op` to the given `init` value with each item of this
 /// iterator, producing a new iterator with the results.
 ///
 /// The `init` value will be cloned only as needed to be paired with
 /// the group of items in each rayon job. It does not require the type
 /// to be `Sync`.
 ///
 /// # Examples
 ///
 /// ```
 /// use std::sync::mpsc::channel;
 /// use rayon::prelude::*;
 ///
 /// let (sender, receiver) = channel();
 ///
 /// let a: Vec<_> = (0..5)
 /// .into_par_iter() // iterating over i32
 /// .map_with(sender, |s, x| {
 /// s.send(x).unwrap(); // sending i32 values through the channel
 /// x // returning i32
 /// })
 /// .collect(); // collecting the returned values into a vector
 ///
 /// let mut b: Vec<_> = receiver.iter() // iterating over the values in the channel
 /// .collect(); // and collecting them
 /// b.sort();
 ///
 /// assert_eq!(a, b);
 /// ```
 fn map_with<F, T, R>(self, init: T, map_op: F) -> MapWith<Self, T, F>
 where
 F: Fn(&mut T, Self::Item) -> R + Sync + Send,
 T: Send + Clone,
 R: Send,
 {
 MapWith::new(self, init, map_op)
 }

 /// Applies `map_op` to a value returned by `init` with each item of this
 /// iterator, producing a new iterator with the results.
 ///
 /// The `init` function will be called only as needed for a value to be
 /// paired with the group of items in each rayon job. There is no
 /// constraint on that returned type at all!
 ///
 /// # Examples
 ///
 /// ```
 /// use rand::Rng;
 /// use rayon::prelude::*;
 ///
 /// let a: Vec<_> = (1i32..1_000_000)
 /// .into_par_iter()
 /// .map_init(
 /// || rand::rng(), // get the thread-local RNG
 /// |rng, x| if rng.random() { // randomly negate items
 /// -x
 /// } else {
 /// x
 /// },
 /// ).collect();
 ///
 /// // There's a remote chance that this will fail...
 /// assert!(a.iter().any(|&x| x < 0));
 /// assert!(a.iter().any(|&x| x > 0));
 /// ```
 fn map_init<F, INIT, T, R>(self, init: INIT, map_op: F) -> MapInit<Self, INIT, F>
 where
 F: Fn(&mut T, Self::Item) -> R + Sync + Send,
 INIT: Fn() -> T + Sync + Send,
 R: Send,
 {
 MapInit::new(self, init, map_op)
 }

 /// Creates an iterator which clones all of its elements. This may be
 /// useful when you have an iterator over `&T`, but you need `T`, and
 /// that type implements `Clone`. See also [`copied()`].
 ///
 /// [`copied()`]: #method.copied
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let a = [1, 2, 3];
 ///
 /// let v_cloned: Vec<_> = a.par_iter().cloned().collect();
 ///
 /// // cloned is the same as .map(|&x| x), for integers
 /// let v_map: Vec<_> = a.par_iter().map(|&x| x).collect();
 ///
 /// assert_eq!(v_cloned, vec![1, 2, 3]);
 /// assert_eq!(v_map, vec![1, 2, 3]);
 /// ```
 fn cloned<'a, T>(self) -> Cloned 
 where
 T: 'a + Clone + Send,
 Self: ParallelIterator (self) -> Copied 
 where
 T: 'a + Copy + Send,
 Self: ParallelIterator (self, inspect_op: OP) -> Inspect<Self, OP>
 where
 OP: Fn(&Self::Item) + Sync + Send,
 {
 Inspect::new(self, inspect_op)
 }

 /// Mutates each item of this iterator before yielding it.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let par_iter = (0..5).into_par_iter().update(|x| {*x *= 2;});
 ///
 /// let doubles: Vec<_> = par_iter.collect();
 ///
 /// assert_eq!(&doubles[..], &[0, 2, 4, 6, 8]);
 /// ```
 fn update (self, update_op: F) -> Update<Self, F>
 where
 F: Fn(&mut Self::Item) + Sync + Send,
 {
 Update::new(self, update_op)
 }

 /// Applies `filter_op` to each item of this iterator, producing a new
 /// iterator with only the items that gave `true` results.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let mut par_iter = (0..10).into_par_iter().filter(|x| x % 2 == 0);
 ///
 /// let even_numbers: Vec<_> = par_iter.collect();
 ///
 /// assert_eq!(&even_numbers[..], &[0, 2, 4, 6, 8]);
 /// ```
 fn filter (self, filter_op: P) -> Filter<Self, P>
 where
 P: Fn(&Self::Item) -> bool + Sync + Send,
 {
 Filter::new(self, filter_op)
 }

 /// Applies `filter_op` to each item of this iterator to get an `Option`,
 /// producing a new iterator with only the items from `Some` results.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let mut par_iter = (0..10).into_par_iter()
 /// .filter_map(|x| {
 /// if x % 2 == 0 { Some(x * 3) }
 /// else { None }
 /// });
 ///
 /// let even_numbers: Vec<_> = par_iter.collect();
 ///
 /// assert_eq!(&even_numbers[..], &[0, 6, 12, 18, 24]);
 /// ```
 fn filter_map<P, R>(self, filter_op: P) -> FilterMap<Self, P>
 where
 P: Fn(Self::Item) -> Option + Sync + Send,
 R: Send,
 {
 FilterMap::new(self, filter_op)
 }

 /// Applies `map_op` to each item of this iterator to get nested parallel iterators,
 /// producing a new parallel iterator that flattens these back into one.
 ///
 /// See also [`flat_map_iter`](#method.flat_map_iter).
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let a = [[1, 2], [3, 4], [5, 6], [7, 8]];
 ///
 /// let par_iter = a.par_iter().cloned().flat_map(|a| a.to_vec());
 ///
 /// let vec: Vec<_> = par_iter.collect();
 ///
 /// assert_eq!(&vec[..], &[1, 2, 3, 4, 5, 6, 7, 8]);
 /// ```
 fn flat_map<F, PI>(self, map_op: F) -> FlatMap<Self, F>
 where
 F: Fn(Self::Item) -> PI + Sync + Send,
 PI: IntoParallelIterator,
 {
 FlatMap::new(self, map_op)
 }

 /// Applies `map_op` to each item of this iterator to get nested serial iterators,
 /// producing a new parallel iterator that flattens these back into one.
 ///
 /// # `flat_map_iter` versus `flat_map`
 ///
 /// These two methods are similar but behave slightly differently. With [`flat_map`],
 /// each of the nested iterators must be a parallel iterator, and they will be further
 /// split up with nested parallelism. With `flat_map_iter`, each nested iterator is a
 /// sequential `Iterator`, and we only parallelize _between_ them, while the items
 /// produced by each nested iterator are processed sequentially.
 ///
 /// When choosing between these methods, consider whether nested parallelism suits the
 /// potential iterators at hand. If there's little computation involved, or its length
 /// is much less than the outer parallel iterator, then it may perform better to avoid
 /// the overhead of parallelism, just flattening sequentially with `flat_map_iter`.
 /// If there is a lot of computation, potentially outweighing the outer parallel
 /// iterator, then the nested parallelism of `flat_map` may be worthwhile.
 ///
 /// [`flat_map`]: #method.flat_map
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 /// use std::cell::RefCell;
 ///
 /// let a = [[1, 2], [3, 4], [5, 6], [7, 8]];
 ///
 /// let par_iter = a.par_iter().flat_map_iter(|a| {
 /// // The serial iterator doesn't have to be thread-safe, just its items.
 /// let cell_iter = RefCell::new(a.iter().cloned());
 /// std::iter::from_fn(move || cell_iter.borrow_mut().next())
 /// });
 ///
 /// let vec: Vec<_> = par_iter.collect();
 ///
 /// assert_eq!(&vec[..], &[1, 2, 3, 4, 5, 6, 7, 8]);
 /// ```
 fn flat_map_iter<F, SI>(self, map_op: F) -> FlatMapIter<Self, F>
 where
 F: Fn(Self::Item) -> SI + Sync + Send,
 SI: IntoIterator,
 {
 FlatMapIter::new(self, map_op)
 }

 /// An adaptor that flattens parallel-iterable `Item`s into one large iterator.
 ///
 /// See also [`flatten_iter`](#method.flatten_iter).
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let x: Vec<Vec<_>> = vec![vec![1, 2], vec![3, 4]];
 /// let y: Vec<_> = x.into_par_iter().flatten().collect();
 ///
 /// assert_eq!(y, vec![1, 2, 3, 4]);
 /// ```
 fn flatten(self) -> Flatten 
 where
 Self::Item: IntoParallelIterator,
 {
 Flatten::new(self)
 }

 /// An adaptor that flattens serial-iterable `Item`s into one large iterator.
 ///
 /// See also [`flatten`](#method.flatten) and the analogous comparison of
 /// [`flat_map_iter` versus `flat_map`](#flat_map_iter-versus-flat_map).
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let x: Vec<Vec<_>> = vec![vec![1, 2], vec![3, 4]];
 /// let iters: Vec<_> = x.into_iter().map(Vec::into_iter).collect();
 /// let y: Vec<_> = iters.into_par_iter().flatten_iter().collect();
 ///
 /// assert_eq!(y, vec![1, 2, 3, 4]);
 /// ```
 fn flatten_iter(self) -> FlattenIter 
 where
 Self::Item: IntoIterator,
 {
 FlattenIter::new(self)
 }

 /// Reduces the items in the iterator into one item using `op`.
 /// The argument `identity` should be a closure that can produce
 /// "identity" value which may be inserted into the sequence as
 /// needed to create opportunities for parallel execution. So, for
 /// example, if you are doing a summation, then `identity()` ought
 /// to produce something that represents the zero for your type
 /// (but consider just calling `sum()` in that case).
 ///
 /// # Examples
 ///
 /// ```
 /// // Iterate over a sequence of pairs `(x0, y0), ..., (xN, yN)`
 /// // and use reduce to compute one pair `(x0 + ... + xN, y0 + ... + yN)`
 /// // where the first/second elements are summed separately.
 /// use rayon::prelude::*;
 /// let sums = [(0, 1), (5, 6), (16, 2), (8, 9)]
 /// .par_iter() // iterating over &(i32, i32)
 /// .cloned() // iterating over (i32, i32)
 /// .reduce(|| (0, 0), // the "identity" is 0 in both columns
 /// |a, b| (a.0 + b.0, a.1 + b.1));
 /// assert_eq!(sums, (0 + 5 + 16 + 8, 1 + 6 + 2 + 9));
 /// ```
 ///
 /// **Note:** unlike a sequential `fold` operation, the order in
 /// which `op` will be applied to reduce the result is not fully
 /// specified. So `op` should be [associative] or else the results
 /// will be non-deterministic. And of course `identity()` should
 /// produce a true identity.
 ///
 /// [associative]: https://en.wikipedia.org/wiki/Associative_property
 fn reduce<OP, ID>(self, identity: ID, op: OP) -> Self::Item
 where
 OP: Fn(Self::Item, Self::Item) -> Self::Item + Sync + Send,
 ID: Fn() -> Self::Item + Sync + Send,
 {
 reduce::reduce(self, identity, op)
 }

 /// Reduces the items in the iterator into one item using `op`.
 /// If the iterator is empty, `None` is returned; otherwise,
 /// `Some` is returned.
 ///
 /// This version of `reduce` is simple but somewhat less
 /// efficient. If possible, it is better to call `reduce()`, which
 /// requires an identity element.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 /// let sums = [(0, 1), (5, 6), (16, 2), (8, 9)]
 /// .par_iter() // iterating over &(i32, i32)
 /// .cloned() // iterating over (i32, i32)
 /// .reduce_with(|a, b| (a.0 + b.0, a.1 + b.1))
 /// .unwrap();
 /// assert_eq!(sums, (0 + 5 + 16 + 8, 1 + 6 + 2 + 9));
 /// ```
 ///
 /// **Note:** unlike a sequential `fold` operation, the order in
 /// which `op` will be applied to reduce the result is not fully
 /// specified. So `op` should be [associative] or else the results
 /// will be non-deterministic.
 ///
 /// [associative]: https://en.wikipedia.org/wiki/Associative_property
 fn reduce_with (self, op: OP) -> Option 
 where
 OP: Fn(Self::Item, Self::Item) -> Self::Item + Sync + Send,
 {
 fn opt_fold (op: impl Fn(T, T) -> T) -> impl Fn(Option, T) -> Option {
 move |opt_a, b| match opt_a {
 Some(a) => Some(op(a, b)),
 None => Some(b),
 }
 }

 fn opt_reduce (op: impl Fn(T, T) -> T) -> impl Fn(Option, Option) -> Option {
 move |opt_a, opt_b| match (opt_a, opt_b) {
 (Some(a), Some(b)) => Some(op(a, b)),
 (Some(v), None) | (None, Some(v)) => Some(v),
 (None, None) => None,
 }
 }

 self.fold(<_>::default, opt_fold(&op))
 .reduce(<_>::default, opt_reduce(&op))
 }

 /// Reduces the items in the iterator into one item using a fallible `op`.
 /// The `identity` argument is used the same way as in [`reduce()`].
 ///
 /// [`reduce()`]: #method.reduce
 ///
 /// If a `Result::Err` or `Option::None` item is found, or if `op` reduces
 /// to one, we will attempt to stop processing the rest of the items in the
 /// iterator as soon as possible, and we will return that terminating value.
 /// Otherwise, we will return the final reduced `Result::Ok(T)` or
 /// `Option::Some(T)`. If there are multiple errors in parallel, it is not
 /// specified which will be returned.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// // Compute the sum of squares, being careful about overflow.
 /// fn sum_squares >(iter: I) -> Option {
 /// iter.into_par_iter()
 /// .map(|i| i.checked_mul(i)) // square each item,
 /// .try_reduce(|| 0, i32::checked_add) // and add them up!
 /// }
 /// assert_eq!(sum_squares(0..5), Some(0 + 1 + 4 + 9 + 16));
 ///
 /// // The sum might overflow
 /// assert_eq!(sum_squares(0..10_000), None);
 ///
 /// // Or the squares might overflow before it even reaches `try_reduce`
 /// assert_eq!(sum_squares(1_000_000..1_000_001), None);
 /// ```
 fn try_reduce<T, OP, ID>(self, identity: ID, op: OP) -> Self::Item
 where
 OP: Fn(T, T) -> Self::Item + Sync + Send,
 ID: Fn() -> T + Sync + Send,
 Self::Item: Try,
 {
 try_reduce::try_reduce(self, identity, op)
 }

 /// Reduces the items in the iterator into one item using a fallible `op`.
 ///
 /// Like [`reduce_with()`], if the iterator is empty, `None` is returned;
 /// otherwise, `Some` is returned. Beyond that, it behaves like
 /// [`try_reduce()`] for handling `Err`/`None`.
 ///
 /// [`reduce_with()`]: #method.reduce_with
 /// [`try_reduce()`]: #method.try_reduce
 ///
 /// For instance, with `Option` items, the return value may be:
 /// - `None`, the iterator was empty
 /// - `Some(None)`, we stopped after encountering `None`.
 /// - `Some(Some(x))`, the entire iterator reduced to `x`.
 ///
 /// With `Result` items, the nesting is more obvious:
 /// - `None`, the iterator was empty
 /// - `Some(Err(e))`, we stopped after encountering an error `e`.
 /// - `Some(Ok(x))`, the entire iterator reduced to `x`.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let files = ["/dev/null", "/does/not/exist"];
 ///
 /// // Find the biggest file
 /// files.into_par_iter()
 /// .map(|path| std::fs::metadata(path).map(|m| (path, m.len())))
 /// .try_reduce_with(|a, b| {
 /// Ok(if a.1 >= b.1 { a } else { b })
 /// })
 /// .expect("Some value, since the iterator is not empty")
 /// .expect_err("not found");
 /// ```
 fn try_reduce_with<T, OP>(self, op: OP) -> Option 
 where
 OP: Fn(T, T) -> Self::Item + Sync + Send,
 Self::Item: Try,
 {
 try_reduce_with::try_reduce_with(self, op)
 }

 /// Parallel fold is similar to sequential fold except that the
 /// sequence of items may be subdivided before it is
 /// folded. Consider a list of numbers like `22 3 77 89 46`. If
 /// you used sequential fold to add them (`fold(0, |a,b| a+b)`,
 /// you would wind up first adding 0 + 22, then 22 + 3, then 25 +
 /// 77, and so forth. The **parallel fold** works similarly except
 /// that it first breaks up your list into sublists, and hence
 /// instead of yielding up a single sum at the end, it yields up
 /// multiple sums. The number of results is nondeterministic, as
 /// is the point where the breaks occur.
 ///
 /// So if we did the same parallel fold (`fold(0, |a,b| a+b)`) on
 /// our example list, we might wind up with a sequence of two numbers,
 /// like so:
 ///
 /// ```notrust
 /// 22 3 77 89 46
 /// | |
 /// 102 135
 /// ```
 ///
 /// Or perhaps these three numbers:
 ///
 /// ```notrust
 /// 22 3 77 89 46
 /// | | |
 /// 102 89 46
 /// ```
 ///
 /// In general, Rayon will attempt to find good breaking points
 /// that keep all of your cores busy.
 ///
 /// ### Fold versus reduce
 ///
 /// The `fold()` and `reduce()` methods each take an identity element
 /// and a combining function, but they operate rather differently.
 ///
 /// `reduce()` requires that the identity function has the same
 /// type as the things you are iterating over, and it fully
 /// reduces the list of items into a single item. So, for example,
 /// imagine we are iterating over a list of bytes `bytes: [128_u8,
 /// 64_u8, 64_u8]`. If we used `bytes.reduce(|| 0_u8, |a: u8, b:
 /// u8| a + b)`, we would get an overflow. This is because `0`,
 /// `a`, and `b` here are all bytes, just like the numbers in the
 /// list (I wrote the types explicitly above, but those are the
 /// only types you can use). To avoid the overflow, we would need
 /// to do something like `bytes.map(|b| b as u32).reduce(|| 0, |a,
 /// b| a + b)`, in which case our result would be `256`.
 ///
 /// In contrast, with `fold()`, the identity function does not
 /// have to have the same type as the things you are iterating
 /// over, and you potentially get back many results. So, if we
 /// continue with the `bytes` example from the previous paragraph,
 /// we could do `bytes.fold(|| 0_u32, |a, b| a + (b as u32))` to
 /// convert our bytes into `u32`. And of course we might not get
 /// back a single sum.
 ///
 /// There is a more subtle distinction as well, though it's
 /// actually implied by the above points. When you use `reduce()`,
 /// your reduction function is sometimes called with values that
 /// were never part of your original parallel iterator (for
 /// example, both the left and right might be a partial sum). With
 /// `fold()`, in contrast, the left value in the fold function is
 /// always the accumulator, and the right value is always from
 /// your original sequence.
 ///
 /// ### Fold vs Map/Reduce
 ///
 /// Fold makes sense if you have some operation where it is
 /// cheaper to create groups of elements at a time. For example,
 /// imagine collecting characters into a string. If you were going
 /// to use map/reduce, you might try this:
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let s =
 /// ['a', 'b', 'c', 'd', 'e']
 /// .par_iter()
 /// .map(|c: &char| format!("{}", c))
 /// .reduce(|| String::new(),
 /// |mut a: String, b: String| { a.push_str(&b); a });
 ///
 /// assert_eq!(s, "abcde");
 /// ```
 ///
 /// Because reduce produces the same type of element as its input,
 /// you have to first map each character into a string, and then
 /// you can reduce them. This means we create one string per
 /// element in our iterator -- not so great. Using `fold`, we can
 /// do this instead:
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let s =
 /// ['a', 'b', 'c', 'd', 'e']
 /// .par_iter()
 /// .fold(|| String::new(),
 /// |mut s: String, c: &char| { s.push(*c); s })
 /// .reduce(|| String::new(),
 /// |mut a: String, b: String| { a.push_str(&b); a });
 ///
 /// assert_eq!(s, "abcde");
 /// ```
 ///
 /// Now `fold` will process groups of our characters at a time,
 /// and we only make one string per group. We should wind up with
 /// some small-ish number of strings roughly proportional to the
 /// number of CPUs you have (it will ultimately depend on how busy
 /// your processors are). Note that we still need to do a reduce
 /// afterwards to combine those groups of strings into a single
 /// string.
 ///
 /// You could use a similar trick to save partial results (e.g., a
 /// cache) or something similar.
 ///
 /// ### Combining fold with other operations
 ///
 /// You can combine `fold` with `reduce` if you want to produce a
 /// single value. This is then roughly equivalent to a map/reduce
 /// combination in effect:
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let bytes = 0..22_u8;
 /// let sum = bytes.into_par_iter()
 /// .fold(|| 0_u32, |a: u32, b: u8| a + (b as u32))
 /// .sum:: ();
 ///
 /// assert_eq!(sum, (0..22).sum()); // compare to sequential
 /// ```
 fn fold<T, ID, F>(self, identity: ID, fold_op: F) -> Fold<Self, ID, F>
 where
 F: Fn(T, Self::Item) -> T + Sync + Send,
 ID: Fn() -> T + Sync + Send,
 T: Send,
 {
 Fold::new(self, identity, fold_op)
 }

 /// Applies `fold_op` to the given `init` value with each item of this
 /// iterator, finally producing the value for further use.
 ///
 /// This works essentially like `fold(|| init.clone(), fold_op)`, except
 /// it doesn't require the `init` type to be `Sync`, nor any other form
 /// of added synchronization.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let bytes = 0..22_u8;
 /// let sum = bytes.into_par_iter()
 /// .fold_with(0_u32, |a: u32, b: u8| a + (b as u32))
 /// .sum:: ();
 ///
 /// assert_eq!(sum, (0..22).sum()); // compare to sequential
 /// ```
 fn fold_with<F, T>(self, init: T, fold_op: F) -> FoldWith<Self, T, F>
 where
 F: Fn(T, Self::Item) -> T + Sync + Send,
 T: Send + Clone,
 {
 FoldWith::new(self, init, fold_op)
 }

 /// Performs a fallible parallel fold.
 ///
 /// This is a variation of [`fold()`] for operations which can fail with
 /// `Option::None` or `Result::Err`. The first such failure stops
 /// processing the local set of items, without affecting other folds in the
 /// iterator's subdivisions.
 ///
 /// Often, `try_fold()` will be followed by [`try_reduce()`]
 /// for a final reduction and global short-circuiting effect.
 ///
 /// [`fold()`]: #method.fold
 /// [`try_reduce()`]: #method.try_reduce
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let bytes = 0..22_u8;
 /// let sum = bytes.into_par_iter()
 /// .try_fold(|| 0_u32, |a: u32, b: u8| a.checked_add(b as u32))
 /// .try_reduce(|| 0, u32::checked_add);
 ///
 /// assert_eq!(sum, Some((0..22).sum())); // compare to sequential
 /// ```
 fn try_fold<T, R, ID, F>(self, identity: ID, fold_op: F) -> TryFold<Self, R, ID, F>
 where
 F: Fn(T, Self::Item) -> R + Sync + Send,
 ID: Fn() -> T + Sync + Send,
 R: Try + Send,
 {
 TryFold::new(self, identity, fold_op)
 }

 /// Performs a fallible parallel fold with a cloneable `init` value.
 ///
 /// This combines the `init` semantics of [`fold_with()`] and the failure
 /// semantics of [`try_fold()`].
 ///
 /// [`fold_with()`]: #method.fold_with
 /// [`try_fold()`]: #method.try_fold
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let bytes = 0..22_u8;
 /// let sum = bytes.into_par_iter()
 /// .try_fold_with(0_u32, |a: u32, b: u8| a.checked_add(b as u32))
 /// .try_reduce(|| 0, u32::checked_add);
 ///
 /// assert_eq!(sum, Some((0..22).sum())); // compare to sequential
 /// ```
 fn try_fold_with<F, T, R>(self, init: T, fold_op: F) -> TryFoldWith<Self, R, F>
 where
 F: Fn(T, Self::Item) -> R + Sync + Send,
 R: Try + Send,
 T: Clone + Send,
 {
 TryFoldWith::new(self, init, fold_op)
 }

 /// Sums up the items in the iterator.
 ///
 /// Note that the order in items will be reduced is not specified,
 /// so if the `+` operator is not truly [associative] \(as is the
 /// case for floating point numbers), then the results are not
 /// fully deterministic.
 ///
 /// [associative]: https://en.wikipedia.org/wiki/Associative_property
 ///
 /// Basically equivalent to `self.reduce(|| 0, |a, b| a + b)`,
 /// except that the type of `0` and the `+` operation may vary
 /// depending on the type of value being produced.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let a = [1, 5, 7];
 ///
 /// let sum: i32 = a.par_iter().sum();
 ///
 /// assert_eq!(sum, 13);
 /// ```
 fn sum (self) -> S
 where
 S: Send + Sum + Sum,
 {
 sum::sum(self)
 }

 /// Multiplies all the items in the iterator.
 ///
 /// Note that the order in items will be reduced is not specified,
 /// so if the `*` operator is not truly [associative] \(as is the
 /// case for floating point numbers), then the results are not
 /// fully deterministic.
 ///
 /// [associative]: https://en.wikipedia.org/wiki/Associative_property
 ///
 /// Basically equivalent to `self.reduce(|| 1, |a, b| a * b)`,
 /// except that the type of `1` and the `*` operation may vary
 /// depending on the type of value being produced.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// fn factorial(n: u32) -> u32 {
 /// (1..n+1).into_par_iter().product()
 /// }
 ///
 /// assert_eq!(factorial(0), 1);
 /// assert_eq!(factorial(1), 1);
 /// assert_eq!(factorial(5), 120);
 /// ```
 fn product (self) -> P
 where
 P: Send + Product + Product,
 {
 product::product(self)
 }

 /// Computes the minimum of all the items in the iterator. If the
 /// iterator is empty, `None` is returned; otherwise, `Some(min)`
 /// is returned.
 ///
 /// Note that the order in which the items will be reduced is not
 /// specified, so if the `Ord` impl is not truly associative, then
 /// the results are not deterministic.
 ///
 /// Basically equivalent to `self.reduce_with(|a, b| Ord::min(a, b))`.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let a = [45, 74, 32];
 ///
 /// assert_eq!(a.par_iter().min(), Some(&32));
 ///
 /// let b: [i32; 0] = [];
 ///
 /// assert_eq!(b.par_iter().min(), None);
 /// ```
 fn min(self) -> Option 
 where
 Self::Item: Ord,
 {
 self.reduce_with(Ord::min)
 }

 /// Computes the minimum of all the items in the iterator with respect to
 /// the given comparison function. If the iterator is empty, `None` is
 /// returned; otherwise, `Some(min)` is returned.
 ///
 /// Note that the order in which the items will be reduced is not
 /// specified, so if the comparison function is not associative, then
 /// the results are not deterministic.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let a = [-3_i32, 77, 53, 240, -1];
 ///
 /// assert_eq!(a.par_iter().min_by(|x, y| x.cmp(y)), Some(&-3));
 /// ```
 fn min_by (self, f: F) -> Option 
 where
 F: Sync + Send + Fn(&Self::Item, &Self::Item) -> Ordering,
 {
 fn min (f: impl Fn(&T, &T) -> Ordering) -> impl Fn(T, T) -> T {
 move |a, b| match f(&a, &b) {
 Ordering::Greater => b,
 _ => a,
 }
 }

 self.reduce_with(min(f))
 }

 /// Computes the item that yields the minimum value for the given
 /// function. If the iterator is empty, `None` is returned;
 /// otherwise, `Some(item)` is returned.
 ///
 /// Note that the order in which the items will be reduced is not
 /// specified, so if the `Ord` impl is not truly associative, then
 /// the results are not deterministic.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let a = [-3_i32, 34, 2, 5, -10, -3, -23];
 ///
 /// assert_eq!(a.par_iter().min_by_key(|x| x.abs()), Some(&2));
 /// ```
 fn min_by_key<K, F>(self, f: F) -> Option 
 where
 K: Ord + Send,
 F: Sync + Send + Fn(&Self::Item) -> K,
 {
 fn key<T, K>(f: impl Fn(&T) -> K) -> impl Fn(T) -> (K, T) {
 move |x| (f(&x), x)
 }

 fn min_key<T, K: Ord>(a: (K, T), b: (K, T)) -> (K, T) {
 match (a.0).cmp(&b.0) {
 Ordering::Greater => b,
 _ => a,
 }
 }

 let (_, x) = self.map(key(f)).reduce_with(min_key)?;
 Some(x)
 }

 /// Computes the maximum of all the items in the iterator. If the
 /// iterator is empty, `None` is returned; otherwise, `Some(max)`
 /// is returned.
 ///
 /// Note that the order in which the items will be reduced is not
 /// specified, so if the `Ord` impl is not truly associative, then
 /// the results are not deterministic.
 ///
 /// Basically equivalent to `self.reduce_with(|a, b| Ord::max(a, b))`.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let a = [45, 74, 32];
 ///
 /// assert_eq!(a.par_iter().max(), Some(&74));
 ///
 /// let b: [i32; 0] = [];
 ///
 /// assert_eq!(b.par_iter().max(), None);
 /// ```
 fn max(self) -> Option 
 where
 Self::Item: Ord,
 {
 self.reduce_with(Ord::max)
 }

 /// Computes the maximum of all the items in the iterator with respect to
 /// the given comparison function. If the iterator is empty, `None` is
 /// returned; otherwise, `Some(max)` is returned.
 ///
 /// Note that the order in which the items will be reduced is not
 /// specified, so if the comparison function is not associative, then
 /// the results are not deterministic.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let a = [-3_i32, 77, 53, 240, -1];
 ///
 /// assert_eq!(a.par_iter().max_by(|x, y| x.abs().cmp(&y.abs())), Some(&240));
 /// ```
 fn max_by (self, f: F) -> Option 
 where
 F: Sync + Send + Fn(&Self::Item, &Self::Item) -> Ordering,
 {
 fn max (f: impl Fn(&T, &T) -> Ordering) -> impl Fn(T, T) -> T {
 move |a, b| match f(&a, &b) {
 Ordering::Greater => a,
 _ => b,
 }
 }

 self.reduce_with(max(f))
 }

 /// Computes the item that yields the maximum value for the given
 /// function. If the iterator is empty, `None` is returned;
 /// otherwise, `Some(item)` is returned.
 ///
 /// Note that the order in which the items will be reduced is not
 /// specified, so if the `Ord` impl is not truly associative, then
 /// the results are not deterministic.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let a = [-3_i32, 34, 2, 5, -10, -3, -23];
 ///
 /// assert_eq!(a.par_iter().max_by_key(|x| x.abs()), Some(&34));
 /// ```
 fn max_by_key<K, F>(self, f: F) -> Option 
 where
 K: Ord + Send,
 F: Sync + Send + Fn(&Self::Item) -> K,
 {
 fn key<T, K>(f: impl Fn(&T) -> K) -> impl Fn(T) -> (K, T) {
 move |x| (f(&x), x)
 }

 fn max_key<T, K: Ord>(a: (K, T), b: (K, T)) -> (K, T) {
 match (a.0).cmp(&b.0) {
 Ordering::Greater => a,
 _ => b,
 }
 }

 let (_, x) = self.map(key(f)).reduce_with(max_key)?;
 Some(x)
 }

 /// Takes two iterators and creates a new iterator over both.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let a = [0, 1, 2];
 /// let b = [9, 8, 7];
 ///
 /// let par_iter = a.par_iter().chain(b.par_iter());
 ///
 /// let chained: Vec<_> = par_iter.cloned().collect();
 ///
 /// assert_eq!(&chained[..], &[0, 1, 2, 9, 8, 7]);
 /// ```
 fn chain (self, chain: C) -> Chain<Self, C::Iter>
 where
 C: IntoParallelIterator,
 {
 Chain::new(self, chain.into_par_iter())
 }

 /// Searches for **some** item in the parallel iterator that
 /// matches the given predicate and returns it. This operation
 /// is similar to [`find` on sequential iterators][find] but
 /// the item returned may not be the **first** one in the parallel
 /// sequence which matches, since we search the entire sequence in parallel.
 ///
 /// Once a match is found, we will attempt to stop processing
 /// the rest of the items in the iterator as soon as possible
 /// (just as `find` stops iterating once a match is found).
 ///
 /// [find]: Iterator::find()
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let a = [1, 2, 3, 3];
 ///
 /// assert_eq!(a.par_iter().find_any(|&&x| x == 3), Some(&3));
 ///
 /// assert_eq!(a.par_iter().find_any(|&&x| x == 100), None);
 /// ```
 fn find_any (self, predicate: P) -> Option 
 where
 P: Fn(&Self::Item) -> bool + Sync + Send,
 {
 find::find(self, predicate)
 }

 /// Searches for the sequentially **first** item in the parallel iterator
 /// that matches the given predicate and returns it.
 ///
 /// Once a match is found, all attempts to the right of the match
 /// will be stopped, while attempts to the left must continue in case
 /// an earlier match is found.
 ///
 /// For added performance, you might consider using `find_first` in conjunction with
 /// [`by_exponential_blocks()`][IndexedParallelIterator::by_exponential_blocks].
 ///
 /// Note that not all parallel iterators have a useful order, much like
 /// sequential `HashMap` iteration, so "first" may be nebulous. If you
 /// just want the first match that discovered anywhere in the iterator,
 /// `find_any` is a better choice.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let a = [1, 2, 3, 3];
 ///
 /// assert_eq!(a.par_iter().find_first(|&&x| x == 3), Some(&3));
 ///
 /// assert_eq!(a.par_iter().find_first(|&&x| x == 100), None);
 /// ```
 fn find_first (self, predicate: P) -> Option 
 where
 P: Fn(&Self::Item) -> bool + Sync + Send,
 {
 find_first_last::find_first(self, predicate)
 }

 /// Searches for the sequentially **last** item in the parallel iterator
 /// that matches the given predicate and returns it.
 ///
 /// Once a match is found, all attempts to the left of the match
 /// will be stopped, while attempts to the right must continue in case
 /// a later match is found.
 ///
 /// Note that not all parallel iterators have a useful order, much like
 /// sequential `HashMap` iteration, so "last" may be nebulous. When the
 /// order doesn't actually matter to you, `find_any` is a better choice.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let a = [1, 2, 3, 3];
 ///
 /// assert_eq!(a.par_iter().find_last(|&&x| x == 3), Some(&3));
 ///
 /// assert_eq!(a.par_iter().find_last(|&&x| x == 100), None);
 /// ```
 fn find_last (self, predicate: P) -> Option 
 where
 P: Fn(&Self::Item) -> bool + Sync + Send,
 {
 find_first_last::find_last(self, predicate)
 }

 /// Applies the given predicate to the items in the parallel iterator
 /// and returns **any** non-None result of the map operation.
 ///
 /// Once a non-None value is produced from the map operation, we will
 /// attempt to stop processing the rest of the items in the iterator
 /// as soon as possible.
 ///
 /// Note that this method only returns **some** item in the parallel
 /// iterator that is not None from the map predicate. The item returned
 /// may not be the **first** non-None value produced in the parallel
 /// sequence, since the entire sequence is mapped over in parallel.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let c = ["lol", "NaN", "5", "5"];
 ///
 /// let found_number = c.par_iter().find_map_any(|s| s.parse().ok());
 ///
 /// assert_eq!(found_number, Some(5));
 /// ```
 fn find_map_any<P, R>(self, predicate: P) -> Option 
 where
 P: Fn(Self::Item) -> Option + Sync + Send,
 R: Send,
 {
 fn yes (_: &T) -> bool {
 true
 }
 self.filter_map(predicate).find_any(yes)
 }

 /// Applies the given predicate to the items in the parallel iterator and
 /// returns the sequentially **first** non-None result of the map operation.
 ///
 /// Once a non-None value is produced from the map operation, all attempts
 /// to the right of the match will be stopped, while attempts to the left
 /// must continue in case an earlier match is found.
 ///
 /// Note that not all parallel iterators have a useful order, much like
 /// sequential `HashMap` iteration, so "first" may be nebulous. If you
 /// just want the first non-None value discovered anywhere in the iterator,
 /// `find_map_any` is a better choice.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let c = ["lol", "NaN", "2", "5"];
 ///
 /// let first_number = c.par_iter().find_map_first(|s| s.parse().ok());
 ///
 /// assert_eq!(first_number, Some(2));
 /// ```
 fn find_map_first<P, R>(self, predicate: P) -> Option 
 where
 P: Fn(Self::Item) -> Option + Sync + Send,
 R: Send,
 {
 fn yes (_: &T) -> bool {
 true
 }
 self.filter_map(predicate).find_first(yes)
 }

 /// Applies the given predicate to the items in the parallel iterator and
 /// returns the sequentially **last** non-None result of the map operation.
 ///
 /// Once a non-None value is produced from the map operation, all attempts
 /// to the left of the match will be stopped, while attempts to the right
 /// must continue in case a later match is found.
 ///
 /// Note that not all parallel iterators have a useful order, much like
 /// sequential `HashMap` iteration, so "first" may be nebulous. If you
 /// just want the first non-None value discovered anywhere in the iterator,
 /// `find_map_any` is a better choice.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let c = ["lol", "NaN", "2", "5"];
 ///
 /// let last_number = c.par_iter().find_map_last(|s| s.parse().ok());
 ///
 /// assert_eq!(last_number, Some(5));
 /// ```
 fn find_map_last<P, R>(self, predicate: P) -> Option 
 where
 P: Fn(Self::Item) -> Option + Sync + Send,
 R: Send,
 {
 fn yes (_: &T) -> bool {
 true
 }
 self.filter_map(predicate).find_last(yes)
 }

 #[doc(hidden)]
 #[deprecated(note = "parallel `find` does not search in order -- use `find_any`, \\
 `find_first`, or `find_last`")]
 fn find (self, predicate: P) -> Option 
 where
 P: Fn(&Self::Item) -> bool + Sync + Send,
 {
 self.find_any(predicate)
 }

 /// Searches for **some** item in the parallel iterator that
 /// matches the given predicate, and if so returns true. Once
 /// a match is found, we'll attempt to stop process the rest
 /// of the items. Proving that there's no match, returning false,
 /// does require visiting every item.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let a = [0, 12, 3, 4, 0, 23, 0];
 ///
 /// let is_valid = a.par_iter().any(|&x| x > 10);
 ///
 /// assert!(is_valid);
 /// ```
 fn any (self, predicate: P) -> bool
 where
 P: Fn(Self::Item) -> bool + Sync + Send,
 {
 self.map(predicate).find_any(bool::clone).is_some()
 }

 /// Tests that every item in the parallel iterator matches the given
 /// predicate, and if so returns true. If a counter-example is found,
 /// we'll attempt to stop processing more items, then return false.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let a = [0, 12, 3, 4, 0, 23, 0];
 ///
 /// let is_valid = a.par_iter().all(|&x| x > 10);
 ///
 /// assert!(!is_valid);
 /// ```
 fn all (self, predicate: P) -> bool
 where
 P: Fn(Self::Item) -> bool + Sync + Send,
 {
 #[inline]
 fn is_false(x: &bool) -> bool {
 !x
 }

 self.map(predicate).find_any(is_false).is_none()
 }

 /// Creates an iterator over the `Some` items of this iterator, halting
 /// as soon as any `None` is found.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 /// use std::sync::atomic::{AtomicUsize, Ordering};
 ///
 /// let counter = AtomicUsize::new(0);
 /// let value = (0_i32..2048)
 /// .into_par_iter()
 /// .map(|x| {
 /// counter.fetch_add(1, Ordering::SeqCst);
 /// if x < 1024 { Some(x) } else { None }
 /// })
 /// .while_some()
 /// .max();
 ///
 /// assert!(value < Some(1024));
 /// assert!(counter.load(Ordering::SeqCst) < 2048); // should not have visited every single one
 /// ```
 fn while_some (self) -> WhileSome 
 where
 Self: ParallelIterator >,
 T: Send,
 {
 WhileSome::new(self)
 }

 /// Wraps an iterator with a fuse in case of panics, to halt all threads
 /// as soon as possible.
 ///
 /// Panics within parallel iterators are always propagated to the caller,
 /// but they don't always halt the rest of the iterator right away, due to
 /// the internal semantics of [`join`]. This adaptor makes a greater effort
 /// to stop processing other items sooner, with the cost of additional
 /// synchronization overhead, which may also inhibit some optimizations.
 ///
 /// [`join`]: crate::join()#panics
 ///
 /// # Examples
 ///
 /// If this code didn't use `panic_fuse()`, it would continue processing
 /// many more items in other threads (with long sleep delays) before the
 /// panic is finally propagated.
 ///
 /// ```should_panic
 /// use rayon::prelude::*;
 /// use std::{thread, time};
 ///
 /// (0..1_000_000)
 /// .into_par_iter()
 /// .panic_fuse()
 /// .for_each(|i| {
 /// // simulate some work
 /// thread::sleep(time::Duration::from_secs(1));
 /// assert!(i > 0); // oops!
 /// });
 /// ```
 fn panic_fuse(self) -> PanicFuse {
 PanicFuse::new(self)
 }

 /// Creates a fresh collection containing all the elements produced
 /// by this parallel iterator.
 ///
 /// You may prefer [`collect_into_vec()`] implemented on
 /// [`IndexedParallelIterator`], if your underlying iterator also implements
 /// it. [`collect_into_vec()`] allocates efficiently with precise knowledge
 /// of how many elements the iterator contains, and even allows you to reuse
 /// an existing vector's backing store rather than allocating a fresh vector.
 ///
 /// See also [`collect_vec_list()`] for collecting into a
 /// `LinkedList<Vec >`.
 ///
 /// [`collect_into_vec()`]: IndexedParallelIterator::collect_into_vec()
 /// [`collect_vec_list()`]: Self::collect_vec_list()
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let sync_vec: Vec<_> = (0..100).into_iter().collect();
 ///
 /// let async_vec: Vec<_> = (0..100).into_par_iter().collect();
 ///
 /// assert_eq!(sync_vec, async_vec);
 /// ```
 ///
 /// You can collect a pair of collections like [`unzip`](#method.unzip)
 /// for paired items:
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let a = [(0, 1), (1, 2), (2, 3), (3, 4)];
 /// let (first, second): (Vec<_>, Vec<_>) = a.into_par_iter().collect();
 ///
 /// assert_eq!(first, [0, 1, 2, 3]);
 /// assert_eq!(second, [1, 2, 3, 4]);
 /// ```
 ///
 /// Or like [`partition_map`](#method.partition_map) for `Either` items:
 ///
 /// ```
 /// use rayon::prelude::*;
 /// use rayon::iter::Either;
 ///
 /// let (left, right): (Vec<_>, Vec<_>) = (0..8).into_par_iter().map(|x| {
 /// if x % 2 == 0 {
 /// Either::Left(x * 4)
 /// } else {
 /// Either::Right(x * 3)
 /// }
 /// }).collect();
 ///
 /// assert_eq!(left, [0, 8, 16, 24]);
 /// assert_eq!(right, [3, 9, 15, 21]);
 /// ```
 ///
 /// You can even collect an arbitrarily-nested combination of pairs and `Either`:
 ///
 /// ```
 /// use rayon::prelude::*;
 /// use rayon::iter::Either;
 ///
 /// let (first, (left, right)): (Vec<_>, (Vec<_>, Vec<_>))
 /// = (0..8).into_par_iter().map(|x| {
 /// if x % 2 == 0 {
 /// (x, Either::Left(x * 4))
 /// } else {
 /// (-x, Either::Right(x * 3))
 /// }
 /// }).collect();
 ///
 /// assert_eq!(first, [0, -1, 2, -3, 4, -5, 6, -7]);
 /// assert_eq!(left, [0, 8, 16, 24]);
 /// assert_eq!(right, [3, 9, 15, 21]);
 /// ```
 ///
 /// All of that can _also_ be combined with short-circuiting collection of
 /// `Result` or `Option` types:
 ///
 /// ```
 /// use rayon::prelude::*;
 /// use rayon::iter::Either;
 ///
 /// let result: Result<(Vec<_>, (Vec<_>, Vec<_>)), _>
 /// = (0..8).into_par_iter().map(|x| {
 /// if x > 5 {
 /// Err(x)
 /// } else if x % 2 == 0 {
 /// Ok((x, Either::Left(x * 4)))
 /// } else {
 /// Ok((-x, Either::Right(x * 3)))
 /// }
 /// }).collect();
 ///
 /// let error = result.unwrap_err();
 /// assert!(error == 6 || error == 7);
 /// ```
 fn collect (self) -> C
 where
 C: FromParallelIterator,
 {
 C::from_par_iter(self)
 }

 /// Unzips the items of a parallel iterator into a pair of arbitrary
 /// `ParallelExtend` containers.
 ///
 /// You may prefer to use `unzip_into_vecs()`, which allocates more
 /// efficiently with precise knowledge of how many elements the
 /// iterator contains, and even allows you to reuse existing
 /// vectors' backing stores rather than allocating fresh vectors.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let a = [(0, 1), (1, 2), (2, 3), (3, 4)];
 ///
 /// let (left, right): (Vec<_>, Vec<_>) = a.par_iter().cloned().unzip();
 ///
 /// assert_eq!(left, [0, 1, 2, 3]);
 /// assert_eq!(right, [1, 2, 3, 4]);
 /// ```
 ///
 /// Nested pairs can be unzipped too.
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let (values, (squares, cubes)): (Vec<_>, (Vec<_>, Vec<_>)) = (0..4).into_par_iter()
 /// .map(|i| (i, (i * i, i * i * i)))
 /// .unzip();
 ///
 /// assert_eq!(values, [0, 1, 2, 3]);
 /// assert_eq!(squares, [0, 1, 4, 9]);
 /// assert_eq!(cubes, [0, 1, 8, 27]);
 /// ```
 fn unzip<A, B, FromA, FromB>(self) -> (FromA, FromB)
 where
 Self: ParallelIterator,
 FromA: Default + Send + ParallelExtend,
 FromB: Default + Send + ParallelExtend,
 A: Send,
 B: Send,
 {
 unzip::unzip(self)
 }

 /// Partitions the items of a parallel iterator into a pair of arbitrary
 /// `ParallelExtend` containers. Items for which the `predicate` returns
 /// true go into the first container, and the rest go into the second.
 ///
 /// Note: unlike the standard `Iterator::partition`, this allows distinct
 /// collection types for the left and right items. This is more flexible,
 /// but may require new type annotations when converting sequential code
 /// that used type inference assuming the two were the same.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let (left, right): (Vec<_>, Vec<_>) = (0..8).into_par_iter().partition(|x| x % 2 == 0);
 ///
 /// assert_eq!(left, [0, 2, 4, 6]);
 /// assert_eq!(right, [1, 3, 5, 7]);
 /// ```
 fn partition<A, B, P>(self, predicate: P) -> (A, B)
 where
 A: Default + Send + ParallelExtend,
 B: Default + Send + ParallelExtend,
 P: Fn(&Self::Item) -> bool + Sync + Send,
 {
 unzip::partition(self, predicate)
 }

 /// Partitions and maps the items of a parallel iterator into a pair of
 /// arbitrary `ParallelExtend` containers. `Either::Left` items go into
 /// the first container, and `Either::Right` items go into the second.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 /// use rayon::iter::Either;
 ///
 /// let (left, right): (Vec<_>, Vec<_>) = (0..8).into_par_iter()
 /// .partition_map(|x| {
 /// if x % 2 == 0 {
 /// Either::Left(x * 4)
 /// } else {
 /// Either::Right(x * 3)
 /// }
 /// });
 ///
 /// assert_eq!(left, [0, 8, 16, 24]);
 /// assert_eq!(right, [3, 9, 15, 21]);
 /// ```
 ///
 /// Nested `Either` enums can be split as well.
 ///
 /// ```
 /// use rayon::prelude::*;
 /// use rayon::iter::Either::*;
 ///
 /// let ((fizzbuzz, fizz), (buzz, other)): ((Vec<_>, Vec<_>), (Vec<_>, Vec<_>)) = (1..20)
 /// .into_par_iter()
 /// .partition_map(|x| match (x % 3, x % 5) {
 /// (0, 0) => Left(Left(x)),
 /// (0, _) => Left(Right(x)),
 /// (_, 0) => Right(Left(x)),
 /// (_, _) => Right(Right(x)),
 /// });
 ///
 /// assert_eq!(fizzbuzz, [15]);
 /// assert_eq!(fizz, [3, 6, 9, 12, 18]);
 /// assert_eq!(buzz, [5, 10]);
 /// assert_eq!(other, [1, 2, 4, 7, 8, 11, 13, 14, 16, 17, 19]);
 /// ```
 fn partition_map<A, B, P, L, R>(self, predicate: P) -> (A, B)
 where
 A: Default + Send + ParallelExtend,
 B: Default + Send + ParallelExtend,
 P: Fn(Self::Item) -> Either<L, R> + Sync + Send,
 L: Send,
 R: Send,
 {
 unzip::partition_map(self, predicate)
 }

 /// Intersperses clones of an element between items of this iterator.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let x = vec![1, 2, 3];
 /// let r: Vec<_> = x.into_par_iter().intersperse(-1).collect();
 ///
 /// assert_eq!(r, vec![1, -1, 2, -1, 3]);
 /// ```
 fn intersperse(self, element: Self::Item) -> Intersperse 
 where
 Self::Item: Clone,
 {
 Intersperse::new(self, element)
 }

 /// Creates an iterator that yields `n` elements from *anywhere* in the original iterator.
 ///
 /// This is similar to [`IndexedParallelIterator::take`] without being
 /// constrained to the "first" `n` of the original iterator order. The
 /// taken items will still maintain their relative order where that is
 /// visible in `collect`, `reduce`, and similar outputs.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let result: Vec<_> = (0..100)
 /// .into_par_iter()
 /// .filter(|&x| x % 2 == 0)
 /// .take_any(5)
 /// .collect();
 ///
 /// assert_eq!(result.len(), 5);
 /// assert!(result.windows(2).all(|w| w[0] < w[1]));
 /// ```
 fn take_any(self, n: usize) -> TakeAny {
 TakeAny::new(self, n)
 }

 /// Creates an iterator that skips `n` elements from *anywhere* in the original iterator.
 ///
 /// This is similar to [`IndexedParallelIterator::skip`] without being
 /// constrained to the "first" `n` of the original iterator order. The
 /// remaining items will still maintain their relative order where that is
 /// visible in `collect`, `reduce`, and similar outputs.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let result: Vec<_> = (0..100)
 /// .into_par_iter()
 /// .filter(|&x| x % 2 == 0)
 /// .skip_any(5)
 /// .collect();
 ///
 /// assert_eq!(result.len(), 45);
 /// assert!(result.windows(2).all(|w| w[0] < w[1]));
 /// ```
 fn skip_any(self, n: usize) -> SkipAny {
 SkipAny::new(self, n)
 }

 /// Creates an iterator that takes elements from *anywhere* in the original iterator
 /// until the given `predicate` returns `false`.
 ///
 /// The `predicate` may be anything -- e.g. it could be checking a fact about the item, a
 /// global condition unrelated to the item itself, or some combination thereof.
 ///
 /// If parallel calls to the `predicate` race and give different results, then the
 /// `true` results will still take those particular items, while respecting the `false`
 /// result from elsewhere to skip any further items.
 ///
 /// This is similar to [`Iterator::take_while`] without being constrained to the original
 /// iterator order. The taken items will still maintain their relative order where that is
 /// visible in `collect`, `reduce`, and similar outputs.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let result: Vec<_> = (0..100)
 /// .into_par_iter()
 /// .take_any_while(|x| *x < 50)
 /// .collect();
 ///
 /// assert!(result.len() <= 50);
 /// assert!(result.windows(2).all(|w| w[0] < w[1]));
 /// ```
 ///
 /// ```
 /// use rayon::prelude::*;
 /// use std::sync::atomic::AtomicUsize;
 /// use std::sync::atomic::Ordering::Relaxed;
 ///
 /// // Collect any group of items that sum <= 1000
 /// let quota = AtomicUsize::new(1000);
 /// let result: Vec<_> = (0_usize..100)
 /// .into_par_iter()
 /// .take_any_while(|&x| {
 /// quota.fetch_update(Relaxed, Relaxed, |q| q.checked_sub(x))
 /// .is_ok()
 /// })
 /// .collect();
 ///
 /// let sum = result.iter().sum:: ();
 /// assert!(matches!(sum, 902..=1000));
 /// ```
 fn take_any_while (self, predicate: P) -> TakeAnyWhile<Self, P>
 where
 P: Fn(&Self::Item) -> bool + Sync + Send,
 {
 TakeAnyWhile::new(self, predicate)
 }

 /// Creates an iterator that skips elements from *anywhere* in the original iterator
 /// until the given `predicate` returns `false`.
 ///
 /// The `predicate` may be anything -- e.g. it could be checking a fact about the item, a
 /// global condition unrelated to the item itself, or some combination thereof.
 ///
 /// If parallel calls to the `predicate` race and give different results, then the
 /// `true` results will still skip those particular items, while respecting the `false`
 /// result from elsewhere to skip any further items.
 ///
 /// This is similar to [`Iterator::skip_while`] without being constrained to the original
 /// iterator order. The remaining items will still maintain their relative order where that is
 /// visible in `collect`, `reduce`, and similar outputs.
 ///
 /// # Examples
 ///
 /// ```
 /// use rayon::prelude::*;
 ///
 /// let result: Vec<_> = (0..100)
 /// .into_par_iter()
 /// .skip_any_while(|x| *x < 50)
 /// .collect();
 ///
 /// assert!(result.len() >= 50);
 /// assert!(result.windows(2).all(|w| w[0] < w[1]));
 /// ```
 fn skip_any_while (self, predicate: P) -> SkipAnyWhile<Self, P>
 where
 P: Fn(&Self::Item) -> bool + Sync + Send,
 {
 SkipAnyWhile::new(self, predicate)
 }

 /// Collects this iterator into a linked list of vectors.
 ///
 /// This is useful when you need to condense a parallel iterator into a collection,
 /// but have no specific requirements for what that collection should be. If you
 /// plan to store the collection longer-term, `Vec ` is, as always, likely the
 /// best default choice, despite the overhead that comes from concatenating each
 /// vector. Or, if this is an `IndexedParallelIterator`, you should also prefer to
 /// just collect to a `Vec `.
 ///
 /// Internally, most [`FromParallelIterator`]/[`ParallelExtend`] implementations
 /// use this strategy; each job collecting their chunk of the iterator to a `Vec `
 /// and those chunks getting merged into a `LinkedList`, before then extending the
 /// collection with each vector. This is a very efficient way to collect an
 /// unindexed parallel iterator, without much intermediate data movement.
 ///
 /// # Examples
 ///
 /// ```
 /// # use std::collections::LinkedList;
 /// use rayon::prelude::*;
 ///
 /// let result: LinkedList<Vec<_>> = (0..=100)
 /// .into_par_iter()
 /// .filter(|x| x % 2 == 0)
 /// .flat_map(|x| 0..x)
 /// .collect_vec_list();
 ///
 /// // `par_iter.collect_vec_list().into_iter().flatten()` turns
 /// // a parallel iterator into a serial one
 /// let total_len = result.into_iter().flatten().count();
 /// assert_eq!(total_len, 2550);
 /// ```
 fn collect_vec_list(self) -> LinkedList<Vec > {
 match extend::fast_collect(self) {
 Either::Left(vec) => {
 let mut list = LinkedList::new();
 if !vec.is_empty() {
 list.push_back(vec);
 }
 list
 }
 Either::Right(list) => list,
 }
 }

 /// Internal method used to define the behavior of this parallel
 /// iterator. You should not need to call this directly.
 ///
 /// This method causes the iterator `self` to start producing
 /// items and to feed them to the consumer `consumer` one by one.
 /// It may split the consumer before doing so to create the
 /// opportunity to produce in parallel.
 ///
 /// See the [README] for more details on the internals of parallel
 /// iterators.
 ///
 /// [README]: https://github.com/rayon-rs/rayon/blob/main/src/iter/plumbing/README.md
 fn drive_unindexed (self, consumer: C) -> C::Result
 where
 C: UnindexedConsumer;

 /// Internal method used to define the behavior of this parallel
 /// iterator. You should not need to call this directly.
 ///
 /// Returns the number of items produced by this iterator, if known
 /// statically. This can be used by consumers to trigger special fast
 /// paths. Therefore, if `Some(_)` is returned, this iterator must only
 /// use the (indexed) `Consumer` methods when driving a consumer, such
 /// as `split_at()`. Calling `UnindexedConsumer::split_off_left()` or
 /// other `UnindexedConsumer` methods -- or returning an inaccurate
 /// value -- may result in panics.
 ///
 /// This method is currently used to optimize `collect` for want
 /// of true Rust specialization; it may be removed when
 /// specialization is stable.
 fn op

# f64x4 in wide - Rust
URL: https://docs.rs/wide/1.7.1/wide/struct.f64x4.html

f64x4 in wide - Rust

Source 

```
pub struct f64x4 { /* private fields */ }
```

Expand description

A SIMD vector with four elements of type `f64`.

See the crate level documentation for more information about SIMD vectors.

## Implementations§

Source§ impl f64x4 The following functionality exists for all SIMD vectors. 

Source pub const fn new(array: [f64; 4]) -> Self

Converts an array to a SIMD vector.

Source pub const fn splat(elem: f64) -> Self

Constructs a new SIMD vector with all elements set to the given value.

Source pub const fn to_array(self) -> [f64; 4]

Converts a SIMD vector to an array.

Source pub const fn as_array(&self) -> &[f64; 4]

Returns an array reference containing the entire SIMD vector.

Source pub const fn as_mut_array(&mut self) -> &mut [f64; 4]

Returns a mutable array reference containing the entire SIMD vector.

Source pub const fn from_ne_bytes(bytes: [u8; 32]) -> Self

Creates a SIMD vector from a native-endian byte array.

The bytes are interpreted as the raw memory representation of the vector. This is equivalent to the `from_ne_bytes` functions on the primitive scalar types, but operates on the entire vector at once.

This is the inverse of `to_ne_bytes`.

Source pub const fn to_ne_bytes(self) -> [u8; 32]

Returns the raw memory representation of `self` as a native-endian byte array.

This is the inverse of `from_ne_bytes`.

Source pub fn simd_eq (self, other: Rhs) -> >:: Output where Self: CmpEq,

Returns a mask that checks if each element of `self` is equal to the corresponding element of `other`.

Source pub fn simd_ne (self, other: Rhs) -> >:: Output where Self: CmpNe,

Returns a mask that checks if each element of `self` is not equal to the corresponding element of `other`.

Source pub fn simd_lt (self, other: Rhs) -> >:: Output where Self: CmpLt,

Returns a mask that checks if each element of `self` is less than the corresponding element of `other`.

Source pub fn simd_gt (self, other: Rhs) -> >:: Output where Self: CmpGt,

Returns a mask that checks if each element of `self` is greater than the corresponding element of `other`.

Source pub fn simd_le (self, other: Rhs) -> >:: Output where Self: CmpLe,

Returns a mask that checks if each element of `self` is less than or equal to the corresponding element of `other`.

Source pub fn simd_ge (self, other: Rhs) -> >:: Output where Self: CmpGe,

Returns a mask that checks if each element of `self` is greater than or equal to the corresponding element of `other`.

Source pub fn reduce_add(self) -> f64

Reducing addition. Returns the sum of the vector’s elements.

Equivalent to `self[0] + self[1] + ...`.

##### § Unspecified precision

The order of addition is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn reduce_mul(self) -> f64

Reducing multiplication. Returns the product of the vector’s elements.

Equivalent to `self[0] * self[1] * ...`.

##### § Unspecified precision

The order of multiplication is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn bitselect(self, if_one: Self, if_zero: Self) -> Self

Bitwise selection.

For each bit of `self`:

- If the bit is one, return the corresponding bit of `if_one`
- If the bit is zero, return the corresponding bit of `if_zero`

If you know `self` is a mask, meaning each element is either all zeros or all ones, consider using `select` which is faster.

Source pub fn select (self, if_true: Output, if_false: Output) -> Output where Self: Select,

Lanewise SIMD selection.

For each lane:

- If all bits of `self` are one, return the corresponding lane of `if_true`
- If all bits of `self` are zero, return the corresponding lane of `if_false`

This function assumes `self` is a mask, meaning each element is either all zeros or all ones. For bitwise selection use `bitselect`.

In addition to selecting SIMD vectors, this method can be used to select composite types (e.g., a downstream `Vec3 ` structure) if you implement `Select for Simd`.

Source pub fn to_bitmask(self) -> u32

Converts to a bitmask, where each bit is `1` if the element of `self` is true or `0` if the element of `self` is false.

Each bit of the output corresponds to an element of `self`. The least significant bit corresponds to the lowest element. Remaining bits are `0`.

This function assumes `self` is a mask, meaning each element is either all zeros or all ones. If the input is not a mask, the result is unspecified.

Source pub fn any(self) -> bool

Returns `true` if any element of `self` is true.

This function assumes `self` is a mask, meaning each element is either all zeros or all ones. If the input is not a mask, the result is unspecified.

Source pub fn all(self) -> bool

Returns `true` if all elements of `self` are true.

This function assumes `self` is a mask, meaning each element is either all zeros or all ones. If the input is not a mask, the result is unspecified.

Source pub fn none(self) -> bool

Returns `true` if none of the elements of `self` are true.

This function assumes `self` is a mask, meaning each element is either all zeros or all ones. If the input is not a mask, the result is unspecified.

Source pub fn shuffle(self, indices: u64x4) -> Self

Returns a SIMD vector whose elements are selected from `self` using the corresponding runtime `indices`.

If an index is out of bounds, the corresponding result element is unspecified.

Equivalent to `[self[indices[0]], self[indices[1]], ..., self[[indices[N - 1]]]]`.

##### § Type-specific guarantees

For `u8x16` and `i8x16`, it is guaranteed that for out of bounds indices, if the high bit of an index is set, zero is returned. Otherwise, either zero is returned or the index wraps around, non-deterministically.

For all other 8-bit types, it is guaranteed that for out of bounds indices, either zero is returned or the index wraps around, non-deterministically (unlike other types, which can return arbitrary values).

Source pub fn shuffle_zeroing(self, indices: u64x4) -> Self

Returns a SIMD vector whose elements are selected from `self` using the corresponding runtime `indices`.

If an index is out of bounds, the corresponding result element is the number zero.

Equivalent to `[self[indices[0]], self[indices[1]], ..., self[[indices[N - 1]]]]` with a zero fallback.

Source pub fn shuffle_wrapping(self, indices: u64x4) -> Self

Returns a SIMD vector whose elements are selected from `self` using the corresponding runtime `indices`.

Indices are wrapped by the number of elements in `self`.

Equivalent to `[self[indices[0] % N], self[indices[1] % N], ..., self[[indices[N - 1] % N]]]`.

Source pub fn transpose(data: [f64x4; 4]) -> [f64x4; 4]

Transposes an array of SIMD vectors interpreted as a square matrix.

Currently this function is only accelerated on `avx`.

Source pub fn blend(self, if_true: Self, if_false: Self) -> Self👎 Deprecated since 1.6.0: split into `select` and `bitselect` functions 

Elementwise selection.

For each element of `self`:

- If all bits are one, return the corresponding element of `if_true`
- If all bits are zero, return the corresponding element of `if_false`

Originally this function did not specify whether it supported per-bit selection, or if it assumed `self` is a mask, meaning each element is either all zeros or all ones (for better performance). Because of this, `blend` has been split into two new functions: `select` and `bitselect`.

Source§ impl f64x4 The following functionality exists for all SIMD vectors of floats. 

Source pub const ONE: Self

A SIMD vector with all elements set to `1.0`.

Source pub const HALF: Self

A SIMD vector with all elements set to `0.5`.

Source pub const ZERO: Self

A SIMD vector with all elements set to `0.0`.

Source pub const EPSILON: Self

A SIMD vector with all elements set to `f64::EPSILON`.

Source pub const MIN: Self

A SIMD vector with all elements set to `f64::MIN`.

Source pub const MIN_POSITIVE: Self

A SIMD vector with all elements set to `f64::MIN_POSITIVE`.

Source pub const MAX: Self

A SIMD vector with all elements set to `f64::MAX`.

Source pub const NAN: Self

A SIMD vector with all elements set to `f64::NAN`.

Source pub const INFINITY: Self

A SIMD vector with all elements set to `f64::INFINITY`.

Source pub const NEG_INFINITY: Self

A SIMD vector with all elements set to `f64::NEG_INFINITY`.

Source pub const E: Self

A SIMD vector with all elements set to Euler’s number (e).

Source pub const FRAC_1_PI: Self

A SIMD vector with all elements set to 1/π.

Source pub const FRAC_2_PI: Self

A SIMD vector with all elements set to 2/π.

Source pub const FRAC_2_SQRT_PI: Self

A SIMD vector with all elements set to 2/sqrt(π).

Source pub const FRAC_1_SQRT_2: Self

A SIMD vector with all elements set to 1/sqrt(2).

Source pub const FRAC_PI_2: Self

A SIMD vector with all elements set to π/2.

Source pub const FRAC_PI_3: Self

A SIMD vector with all elements set to π/3.

Source pub const FRAC_PI_4: Self

A SIMD vector with all elements set to π/4.

Source pub const FRAC_PI_6: Self

A SIMD vector with all elements set to π/6.

Source pub const FRAC_PI_8: Self

A SIMD vector with all elements set to π/8.

Source pub const LN_2: Self

A SIMD vector with all elements set to ln(2).

Source pub const LN_10: Self

A SIMD vector with all elements set to ln(10).

Source pub const LOG2_E: Self

A SIMD vector with all elements set to log 2 (e).

Source pub const LOG10_E: Self

A SIMD vector with all elements set to log 10 (e).

Source pub const LOG10_2: Self

A SIMD vector with all elements set to log 10 (2).

Source pub const LOG2_10: Self

A SIMD vector with all elements set to log 2 (10).

Source pub const PI: Self

A SIMD vector with all elements set to Archimedes’ constant (π).

Source pub const SQRT_2: Self

A SIMD vector with all elements set to sqrt(2).

Source pub const TAU: Self

A SIMD vector with all elements set to the full circle constant (τ).

Equal to 2π.

Source pub fn is_nan(self) -> Self

Returns a mask that checks if each element is NaN.

Source pub fn is_inf(self) -> Self

Returns a mask that checks if each element is infinity (either positive or negative).

Source pub fn is_finite(self) -> Self

Returns a mask that checks if each element is neither infinite nor NaN.

Source pub fn is_sign_positive(self) -> Self

Returns a mask that checks if each element has a positive sign, including `+0.0`, NaNs with positive sign bit and positive infinity.

Source pub fn is_sign_negative(self) -> Self

Returns a mask that checks if each element has a negative sign, including `-0.0`, NaNs with negative sign bit and negative infinity.

Source pub fn recip(self) -> Self

Returns the reciprocal (inverse) of a number, `1/x`.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

To compute the reciprocal deterministically, use `f64x4::ONE / x`.

Source pub fn recip_sqrt(self) -> Self

Returns the square root of the reciprocal (inverse) of a number, `sqrt(1/x)`.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn to_degrees(self) -> Self

Converts radians to degrees.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn to_radians(self) -> Self

Converts degrees to radians.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn max(self, rhs: Self) -> Self

Returns the maximum between each element of `self` and the corresponding element of `other`, ignoring NaN.

For each lane, if exactly one of the arguments is NaN, then the other argument is returned. If both arguments are NaN, the return value is NaN. If the inputs compare equal (such as for the case of `+0.0` and `-0.0`), either input may be returned non-deterministically.

See `fast_max` for a faster variant that does not handle NaNs.

Source pub fn fast_max(self, rhs: Self) -> Self

Returns the maximum between each element of `self` and the corresponding element of `other`, not specifying behavior for NaNs.

For each lane, if both arguments are NaN, the return value is NaN. If the inputs compare equal (such as for the case of `+0.0` and `-0.0`), or if exactly one of the arguments is NaN, either input may be returned non-deterministically.

See `max` for a slower variant that does handle NaNs.

Source pub fn min(self, rhs: Self) -> Self

Returns the minimum between each element of `self` and the corresponding element of `other`, ignoring NaN.

For each lane, if exactly one of the arguments is NaN, then the other argument is returned. If both arguments are NaN, the return value is NaN. If the inputs compare equal (such as for the case of `+0.0` and `-0.0`), either input may be returned non-deterministically.

See `fast_min` for a faster variant that does not handle NaNs.

Source pub fn fast_min(self, rhs: Self) -> Self

Returns the minimum between each element of `self` and the corresponding element of `other`, not specifying behavior for NaNs.

For each lane, if both arguments are NaN, the return value is NaN. If the inputs compare equal (such as for the case of `+0.0` and `-0.0`), or if exactly one of the arguments is NaN, either input may be returned non-deterministically.

See `min` for a slower variant that does handle NaNs.

Source pub fn midpoint(self, other: Self) -> Self

Calculates the midpoint (average) between `self` and `other`.

This returns NaN when either argument is NaN or if a combination of +inf and -inf is provided as arguments.

This function currently returns a less precise result than `f64::midpoint` in order to gain performance, but this may change in the future.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub const fn to_bits(self) -> u64x4

Raw transmutation to unsigned integer vector.

Note that this function preserves the bitwise value, and not the numeric value.

Source pub const fn from_bits(bits: u64x4) -> Self

Raw transmutation from unsigned integer vector.

Note that this function preserves the bitwise value, and not the numeric value.

Source pub fn clamp(self, min: Self, max: Self) -> Self

Restrict a value to a certain interval unless it is NaN.

If `self`, `min` or `max` are NaN, the result is NaN. If `min > max`, the result is `min`. If inputs compare equal (such as for the case of `+0.0` and `-0.0`), either input may be returned non-deterministically.

See `fast_clamp` for a faster variant that does not handle `min` or `max` being NaN.

Source pub fn fast_clamp(self, min: Self, max: Self) -> Self

Restrict a value to a certain interval unless it is NaN.

If `self` is NaN, the result is NaN. If `min > max`, the result is `min`. If inputs compare equal (such as for the case of `+0.0` and `-0.0`), or if `min` or `max` are NaN, any input may be returned non-deterministically.

See `clamp` for a slower variant that also handles `min` or `max` being NaN.

Source pub fn abs(self) -> Self

Computes the absolute value of `self`.

This function always returns the precise result.

Source pub fn signum(self) -> Self

Returns numbers representing the sign of each element.

- `1.0` if the element is positive, `+0.0`, or `INFINITY`
- `-1.0` if the element is negative, `-0.0`, or `NEG_INFINITY`
- NaN if the element is NaN

This matches the behavior of `f32::signum`.

Source pub fn copysign(self, sign: Self) -> Self

Returns numbers composed of the magnitudes of `self` and the signs of `sign`.

Equal to `self` if the sign of `self` and `sign` are the same, otherwise equal to `-self`. Even if `self` or `sign` are NaN, the result is the exact bit pattern of `self` with the sign bit of `sign`.

Source pub fn flip_signs(self, sign: Self) -> Self

Flips the sign of `self` based on the sign of `sign`.

If `sign` has a positive sign, the result is `self`. If `sign` has a negative sign, the result is `-self`. Even if `self` or `sign` are NaN, the result is the exact bit pattern of `self` with a sign flipped based on the sign bit of `sign`.

Source pub fn floor(self) -> Self

Returns the largest integer less than or equal to each input element.

This function always returns the precise result.

Source pub fn ceil(self) -> Self

Returns the smallest integer greater than or equal to each input element.

This function always returns the precise result.

Source pub fn round(self) -> Self

Returns the nearest integer to each input element. If a value is half-way between two integers, round away from `0.0`.

This function always returns the precise result.

For most targets architectures, `round` is slower than `round_ties_even`. If you do not care about the difference, consider using that instead.

Source pub fn round_int(self) -> i64x4

Returns the nearest integer to each input element.

The result for values half-way between two integers is currently not specified.

This saturates out of range values and turns NaNs to `0`. See `fast_round_int` for a faster variant that does not handle out of range values or NaNs.

Source pub fn fast_round_int(self) -> i64x4

Returns the nearest integer to each input element.

The result for values half-way between two integers is currently not specified.

This function does not handle out of range values or NaNs. See `round_int` for a slower variant that does handle out of range values and NaNs.

Source pub fn round_ties_even(self) -> Self

Returns the nearest integer to each input element. Rounds half-way cases to the number with an even least significant digit.

This function always returns the precise result.

Source pub fn trunc(self) -> Self

Returns the integer part of each input element. This means that non-integer numbers are always truncated towards zero.

This function always returns the precise result.

Source pub fn trunc_int(self) -> i64x4

Returns the integer part of each input element. This means that non-integer numbers are always truncated towards zero.

This saturates out of range values and turns NaNs to `0`. See `fast_trunc_int` for a faster variant that does not handle out of range values or NaNs.

Source pub fn fast_trunc_int(self) -> i64x4

Returns the integer part of each input element. This means that non-integer numbers are always truncated towards zero.

This function does not handle out of range values or NaNs. See `trunc_int` for a slower variant that does handle out of range values and NaNs.

Source pub fn fract(self) -> Self

Returns the fractional part of each input element.

This function always returns the precise result.

Source pub fn mul_add(self, a: Self, b: Self) -> Self

Fused multiply-add. Computes `(self * a) + b`.

If there is hardware FMA support, this computes the result with only one rounding error. If not, this falls back to separate multiply and add operations, resulting in two rounding errors. Note that in the future, this function may change to always having one rounding error, at the cost of worse performance.

##### § Platform-specific behavior (may change in the future)

- On `x86`/`x86_64` with AVX+FMA: Uses 256-bit `vfmadd` (single rounding, best accuracy)
- On `x86`/`x86_64` with AVX only: Uses `(self * m) + a` (two roundings)
- Other platforms: Delegates to `f64x2` (may use NEON FMA or fallback)

Source pub fn mul_sub(self, a: Self, b: Self) -> Self

Fused multiply-sub. Computes `(self * a) - b`.

If there is hardware FMA support, this computes the result with only one rounding error. If not, this falls back to separate multiply and add operations, resulting in two rounding errors. Note that in the future, this function may change to always having one rounding error, at the cost of worse performance.

##### § Platform-specific behavior (may change in the future)

- On `x86`/`x86_64` with AVX+FMA: Uses 256-bit `vfmsub` (single rounding, best accuracy)
- On `x86`/`x86_64` with AVX only: Uses `(self * m) - s` (two roundings)
- Other platforms: Delegates to `f64x2` (may use NEON FMA or fallback)

Source pub fn mul_neg_add(self, a: Self, b: Self) -> Self

Fused multiply-negate-add. Computes `-(self * a) + b`.

If there is hardware FMA support, this computes the result with only one rounding error. If not, this falls back to separate multiply and add operations, resulting in two rounding errors. Note that in the future, this function may change to always having one rounding error, at the cost of worse performance.

##### § Platform-specific behavior (may change in the future)

- On `x86`/`x86_64` with AVX+FMA: Uses 256-bit `vfnmadd` (single rounding, best accuracy)
- On `x86`/`x86_64` with AVX only: Uses `a - (self * m)` (two roundings)
- Other platforms: Delegates to `f64x2` (may use NEON FMA or fallback)

Source pub fn mul_neg_sub(self, a: Self, b: Self) -> Self

Fused multiply-negate-sub. Computes `-(self * a) - b`.

If there is hardware FMA support, this computes the result with only one rounding error. If not, this falls back to separate multiply and add operations, resulting in two rounding errors. Note that in the future, this function may change to always having one rounding error, at the cost of worse performance.

##### § Platform-specific behavior (may change in the future)

- On `x86`/`x86_64` with AVX+FMA: Uses 256-bit `vfnmsub` (single rounding, best accuracy)
- On `x86`/`x86_64` with AVX only: Uses `-(self * m) - s` (two roundings)
- Other platforms: Delegates to `f64x2` (may use NEON FMA or fallback)

Source pub fn div_euclid(self, rhs: Self) -> Self

Calculates Euclidean division, the matching function for `rem_euclid`.

This computes the integer `n` such that `self = n * rhs + self.rem_euclid(rhs)`. In other words, the result is `self / rhs` rounded to the integer `n` such that `self >= n * rhs`.

This function is not guaranteed to exactly match `f64::div_euclid`.

Source pub fn rem_euclid(self, rhs: Self) -> Self

Calculates the least nonnegative remainder of `self` when divided by `rhs`.

In particular, the return value `r` satisfies `0.0 <= r < rhs.abs()` in most cases. However, due to a floating point round-off error it can result in `r == rhs.abs()`, violating the mathematical definition, if `self` is much smaller than `rhs.abs()` in magnitude and `self < 0.0`. This result is not an element of the function’s codomain, but it is the closest floating point number in the real numbers and thus fulfills the property `self == self.div_euclid(rhs) * rhs + self.rem_euclid(rhs)` approximately.

This function is not guaranteed to exactly match `f64::rem_euclid`.

Source pub fn powf_simd(self, n: Self) -> Self

Raises each element of the number `self` to the corresponding element of the floating point power `n`.

This function cannot be named simply `powf`, because a now deprecated function already uses that name.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn sqrt(self) -> Self

Returns the square root of a number for each input element.

Returns NaN if `self` is a negative number other than `-0.0`.

This function always returns the precise result.

Source pub fn exp(self) -> Self

Returns `e^(self)`, (the exponential function) for each input element.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next. Calculate the exponent of a packed `f64x4`

Source pub fn exp2(self) -> Self

Returns `2^(self)` for each input element.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn ln(self) -> Self

Returns the natural logarithm of a number for each input element.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn log2(self) -> Self

Returns the base 2 logarithm of a number for each input element.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn log10(self) -> Self

Returns the base 10 logarithm of a number for each input element.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn cbrt(self) -> Self

Returns the cube root of a number for each input element.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn sin(self) -> Self

Computes the sine of a number (in radians) for each input element.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn cos(self) -> Self

Computes the cosine of a number (in radians) for each input element.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn tan(self) -> Self

Computes the tangent of a number (in radians) for each input element.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn asin(self) -> Self

Computes the arcsine of a number for each input element. Return value is in radians in the range [-pi/2, pi/2] or NaN if the number is outside the range [-1, 1].

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn acos(self) -> Self

Computes the arccosine of a number for each input element. Return value is in radians in the range [0, pi] or NaN if the number is outside the range [-1, 1].

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn atan(self) -> Self

Computes the arctangent of a number for each input element. Return value is in radians in the range [-pi/2, pi/2].

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn atan2(self, x: Self) -> Self

Computes the four quadrant arctangent of each element of `self` (`y`) and the corresponding element of `other` (`x`) in radians.

| `x` | `y` | Piecewise Definition | Range |
| --- | --- | --- | --- |
| `>= +0` | `>= +0` | `arctan(y/x)` | `[+0, +pi/2]` |
| `>= +0` | `<= -0` | `arctan(y/x)` | `[-pi/2, -0]` |
| `<= -0` | `>= +0` | `arctan(y/x) + pi` | `[+pi/2, +pi]` |
| `<= -0` | `<= -0` | `arctan(y/x) - pi` | `[-pi, -pi/2]` |

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn sin_cos(self) -> (Self, Self)

Simultaneously computes the sine and cosine of a number `x` for each input element. Returns `(sin(x), cos(x))`.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn asin_acos(self) -> (Self, Self)

Simultaneously computes the arcsine and arccosine of a number `x` for each input element. Returns `(asin(x), acos(x))`.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn exp_m1(self) -> Self

Returns `e^(self) - 1` for each input element in a way that is accurate even if a number is close to zero.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn ln_1p(self) -> Self

Returns `ln(1+n)` (natural logarithm) for each input element more accurately than if the operations were performed separately.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn sinh(self) -> Self

Returns the hyperbolic sine (`(e^self - e^(-self))/2`) for each input element.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn cosh(self) -> Self

Returns the hyperbolic cosine (`(e^self + e^(-self))/2`) for each input element.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn tanh(self) -> Self

Returns the hyperbolic tangent (`sinh(self)/cosh(self)`) for each input element.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn pow_f64x4(self, n: Self) -> Self👎 Deprecated since 1.6.0: renamed to `powf_simd` 

Raises each element of the number `self` to the corresponding element of the floating point power `n`.

This function has been renamed to `powf_simd`.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source pub fn powf(self, n: f64) -> Self👎 Deprecated since 1.6.0: use `x.powf_simd(splat(n))` instead 

Raises each element of the number `self` to the scalar floating point power `n`.

This function has been deprecated because it raises all elements of `x` to the same power, even though that brings no performance benefit. Use `x.powf_simd(f64x4::splat(n))` instead.

##### § Unspecified precision

The precision of this function is non-deterministic. This means it varies by platform, version, and can even differ within the same execution from one invocation to the next.

Source§ impl f64x4 The following functionality exists only for `f64x4`, or only for particular types inconsistently. 

Source pub fn from_i32x4(v: i32x4) -> Self

Converts each element from `i32` to `f64`.

## Trait Implementations§

Source§ impl Add for f64x4

Source§ fn add(self, rhs: Self) -> Self:: Output

Computes addition for each element of `self` and the corresponding element of `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `+` operator.

Source§ impl Add<& f64> for f64x4

Source§ fn add(self, rhs: & f64) -> Self:: Output

Computes addition for each element of `self` and the uniform scalar `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `+` operator.

Source§ impl Add<& f64> for & f64x4

Source§ fn add(self, rhs: & f64) -> Self:: Output

Computes addition for each element of `self` and the uniform scalar `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `+` operator.

Source§ impl Add<& f64x4> for f64x4

Source§ fn add(self, rhs: &Self) -> Self:: Output

Computes addition for each element of `self` and the corresponding element of `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `+` operator.

Source§ impl Add<& f64x4> for f64

Source§ fn add(self, rhs: & f64x4) -> Self:: Output

Computes addition for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `+` operator.

Source§ impl Add<& f64x4> for & f64x4

Source§ fn add(self, rhs: & f64x4) -> Self:: Output

Computes addition for each element of `self` and the corresponding element of `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `+` operator.

Source§ impl Add<& f64x4> for & f64

Source§ fn add(self, rhs: & f64x4) -> Self:: Output

Computes addition for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `+` operator.

Source§ impl Add< f64> for f64x4

Source§ fn add(self, rhs: f64) -> Self:: Output

Computes addition for each element of `self` and the uniform scalar `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `+` operator.

Source§ impl Add< f64> for & f64x4

Source§ fn add(self, rhs: f64) -> Self:: Output

Computes addition for each element of `self` and the uniform scalar `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `+` operator.

Source§ impl Add< f64x4> for f64

Source§ fn add(self, rhs: f64x4) -> Self:: Output

Computes addition for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `+` operator.

Source§ impl Add< f64x4> for & f64x4

Source§ fn add(self, rhs: f64x4) -> Self:: Output

Computes addition for each element of `self` and the corresponding element of `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `+` operator.

Source§ impl Add< f64x4> for & f64

Source§ fn add(self, rhs: f64x4) -> Self:: Output

Computes addition for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `+` operator.

Source§ impl AddAssign for f64x4

Source§ fn add_assign(&mut self, rhs: Self)

Computes addition for each element of `self` and the corresponding element of `rhs`.

This always returns the precise result.

Source§ impl AddAssign<& f64> for f64x4

Source§ fn add_assign(&mut self, rhs: & f64)

Computes addition for each element of `self` and the uniform scalar `rhs`.

This always returns the precise result.

Source§ impl AddAssign<& f64x4> for f64x4

Source§ fn add_assign(&mut self, rhs: &Self)

Computes addition for each element of `self` and the corresponding element of `rhs`.

This always returns the precise result.

Source§ impl AddAssign< f64> for f64x4

Source§ fn add_assign(&mut self, rhs: f64)

Computes addition for each element of `self` and the uniform scalar `rhs`.

This always returns the precise result.

Source§ impl AlignTo for f64x4

Source§ type Elem = f64

The element type of this SIMD vector.

Source§ fn simd_align_to( slice: &[Self:: Elem], ) -> (&[Self:: Elem], &[Self], &[Self:: Elem])

A SIMD variant of `align_to`.

Source§ fn simd_align_to_mut( slice: &mut [Self:: Elem], ) -> (&mut [Self:: Elem], &mut [Self], &mut [Self:: Elem])

A SIMD variant of `align_to_mut`.

Source§ impl Binary for f64x4

Source§ fn fmt(&self, f: &mut Formatter<'_>) -> Result

Formats the value using the given formatter. Read more

Source§ impl BitAnd for f64x4

Source§ fn bitand(self, rhs: Self) -> Self:: Output

Computes bitwise AND for each element of `self` and the corresponding element of `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `&` operator.

Source§ impl BitAnd<& f64> for f64x4

Source§ fn bitand(self, rhs: & f64) -> Self:: Output

Computes bitwise AND for each element of `self` and the uniform scalar `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `&` operator.

Source§ impl BitAnd<& f64> for & f64x4

Source§ fn bitand(self, rhs: & f64) -> Self:: Output

Computes bitwise AND for each element of `self` and the uniform scalar `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `&` operator.

Source§ impl BitAnd<& f64x4> for f64x4

Source§ fn bitand(self, rhs: &Self) -> Self:: Output

Computes bitwise AND for each element of `self` and the corresponding element of `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `&` operator.

Source§ impl BitAnd<& f64x4> for f64

Source§ fn bitand(self, rhs: & f64x4) -> Self:: Output

Computes bitwise AND for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `&` operator.

Source§ impl BitAnd<& f64x4> for & f64x4

Source§ fn bitand(self, rhs: & f64x4) -> Self:: Output

Computes bitwise AND for each element of `self` and the corresponding element of `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `&` operator.

Source§ impl BitAnd<& f64x4> for & f64

Source§ fn bitand(self, rhs: & f64x4) -> Self:: Output

Computes bitwise AND for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `&` operator.

Source§ impl BitAnd< f64> for f64x4

Source§ fn bitand(self, rhs: f64) -> Self:: Output

Computes bitwise AND for each element of `self` and the uniform scalar `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `&` operator.

Source§ impl BitAnd< f64> for & f64x4

Source§ fn bitand(self, rhs: f64) -> Self:: Output

Computes bitwise AND for each element of `self` and the uniform scalar `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `&` operator.

Source§ impl BitAnd< f64x4> for f64

Source§ fn bitand(self, rhs: f64x4) -> Self:: Output

Computes bitwise AND for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `&` operator.

Source§ impl BitAnd< f64x4> for & f64x4

Source§ fn bitand(self, rhs: f64x4) -> Self:: Output

Computes bitwise AND for each element of `self` and the corresponding element of `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `&` operator.

Source§ impl BitAnd< f64x4> for & f64

Source§ fn bitand(self, rhs: f64x4) -> Self:: Output

Computes bitwise AND for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `&` operator.

Source§ impl BitAndAssign for f64x4

Source§ fn bitand_assign(&mut self, rhs: Self)

Computes bitwise AND for each element of `self` and the corresponding element of `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ impl BitAndAssign<& f64> for f64x4

Source§ fn bitand_assign(&mut self, rhs: & f64)

Computes bitwise AND for each element of `self` and the uniform scalar `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ impl BitAndAssign<& f64x4> for f64x4

Source§ fn bitand_assign(&mut self, rhs: &Self)

Computes bitwise AND for each element of `self` and the corresponding element of `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ impl BitAndAssign< f64> for f64x4

Source§ fn bitand_assign(&mut self, rhs: f64)

Computes bitwise AND for each element of `self` and the uniform scalar `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ impl BitOr for f64x4

Source§ fn bitor(self, rhs: Self) -> Self:: Output

Computes bitwise OR for each element of `self` and the corresponding element of `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `|` operator.

Source§ impl BitOr<& f64> for f64x4

Source§ fn bitor(self, rhs: & f64) -> Self:: Output

Computes bitwise OR for each element of `self` and the uniform scalar `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `|` operator.

Source§ impl BitOr<& f64> for & f64x4

Source§ fn bitor(self, rhs: & f64) -> Self:: Output

Computes bitwise OR for each element of `self` and the uniform scalar `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `|` operator.

Source§ impl BitOr<& f64x4> for f64x4

Source§ fn bitor(self, rhs: &Self) -> Self:: Output

Computes bitwise OR for each element of `self` and the corresponding element of `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `|` operator.

Source§ impl BitOr<& f64x4> for f64

Source§ fn bitor(self, rhs: & f64x4) -> Self:: Output

Computes bitwise OR for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `|` operator.

Source§ impl BitOr<& f64x4> for & f64x4

Source§ fn bitor(self, rhs: & f64x4) -> Self:: Output

Computes bitwise OR for each element of `self` and the corresponding element of `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `|` operator.

Source§ impl BitOr<& f64x4> for & f64

Source§ fn bitor(self, rhs: & f64x4) -> Self:: Output

Computes bitwise OR for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `|` operator.

Source§ impl BitOr< f64> for f64x4

Source§ fn bitor(self, rhs: f64) -> Self:: Output

Computes bitwise OR for each element of `self` and the uniform scalar `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `|` operator.

Source§ impl BitOr< f64> for & f64x4

Source§ fn bitor(self, rhs: f64) -> Self:: Output

Computes bitwise OR for each element of `self` and the uniform scalar `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `|` operator.

Source§ impl BitOr< f64x4> for f64

Source§ fn bitor(self, rhs: f64x4) -> Self:: Output

Computes bitwise OR for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `|` operator.

Source§ impl BitOr< f64x4> for & f64x4

Source§ fn bitor(self, rhs: f64x4) -> Self:: Output

Computes bitwise OR for each element of `self` and the corresponding element of `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `|` operator.

Source§ impl BitOr< f64x4> for & f64

Source§ fn bitor(self, rhs: f64x4) -> Self:: Output

Computes bitwise OR for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `|` operator.

Source§ impl BitOrAssign for f64x4

Source§ fn bitor_assign(&mut self, rhs: Self)

Computes bitwise OR for each element of `self` and the corresponding element of `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ impl BitOrAssign<& f64> for f64x4

Source§ fn bitor_assign(&mut self, rhs: & f64)

Computes bitwise OR for each element of `self` and the uniform scalar `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ impl BitOrAssign<& f64x4> for f64x4

Source§ fn bitor_assign(&mut self, rhs: &Self)

Computes bitwise OR for each element of `self` and the corresponding element of `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ impl BitOrAssign< f64> for f64x4

Source§ fn bitor_assign(&mut self, rhs: f64)

Computes bitwise OR for each element of `self` and the uniform scalar `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ impl BitXor for f64x4

Source§ fn bitxor(self, rhs: Self) -> Self:: Output

Computes bitwise XOR for each element of `self` and the corresponding element of `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `^` operator.

Source§ impl BitXor<& f64> for f64x4

Source§ fn bitxor(self, rhs: & f64) -> Self:: Output

Computes bitwise XOR for each element of `self` and the uniform scalar `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `^` operator.

Source§ impl BitXor<& f64> for & f64x4

Source§ fn bitxor(self, rhs: & f64) -> Self:: Output

Computes bitwise XOR for each element of `self` and the uniform scalar `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `^` operator.

Source§ impl BitXor<& f64x4> for f64x4

Source§ fn bitxor(self, rhs: &Self) -> Self:: Output

Computes bitwise XOR for each element of `self` and the corresponding element of `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `^` operator.

Source§ impl BitXor<& f64x4> for f64

Source§ fn bitxor(self, rhs: & f64x4) -> Self:: Output

Computes bitwise XOR for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `^` operator.

Source§ impl BitXor<& f64x4> for & f64x4

Source§ fn bitxor(self, rhs: & f64x4) -> Self:: Output

Computes bitwise XOR for each element of `self` and the corresponding element of `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `^` operator.

Source§ impl BitXor<& f64x4> for & f64

Source§ fn bitxor(self, rhs: & f64x4) -> Self:: Output

Computes bitwise XOR for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `^` operator.

Source§ impl BitXor< f64> for f64x4

Source§ fn bitxor(self, rhs: f64) -> Self:: Output

Computes bitwise XOR for each element of `self` and the uniform scalar `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `^` operator.

Source§ impl BitXor< f64> for & f64x4

Source§ fn bitxor(self, rhs: f64) -> Self:: Output

Computes bitwise XOR for each element of `self` and the uniform scalar `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `^` operator.

Source§ impl BitXor< f64x4> for f64

Source§ fn bitxor(self, rhs: f64x4) -> Self:: Output

Computes bitwise XOR for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `^` operator.

Source§ impl BitXor< f64x4> for & f64x4

Source§ fn bitxor(self, rhs: f64x4) -> Self:: Output

Computes bitwise XOR for each element of `self` and the corresponding element of `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `^` operator.

Source§ impl BitXor< f64x4> for & f64

Source§ fn bitxor(self, rhs: f64x4) -> Self:: Output

Computes bitwise XOR for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ type Output = f64x4

The resulting type after applying the `^` operator.

Source§ impl BitXorAssign for f64x4

Source§ fn bitxor_assign(&mut self, rhs: Self)

Computes bitwise XOR for each element of `self` and the corresponding element of `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ impl BitXorAssign<& f64> for f64x4

Source§ fn bitxor_assign(&mut self, rhs: & f64)

Computes bitwise XOR for each element of `self` and the uniform scalar `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ impl BitXorAssign<& f64x4> for f64x4

Source§ fn bitxor_assign(&mut self, rhs: &Self)

Computes bitwise XOR for each element of `self` and the corresponding element of `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ impl BitXorAssign< f64> for f64x4

Source§ fn bitxor_assign(&mut self, rhs: f64)

Computes bitwise XOR for each element of `self` and the uniform scalar `rhs`.

This operator is not implemented for primitive scalar floats, but its behavior here is the same as for integers.

Source§ impl Clone for f64x4

Source§ fn clone(&self) -> f64x4

Returns a duplicate of the value. Read more

1.0.0 (const: unstable) · Source§ fn clone_from(&mut self, source: &Self)

Performs copy-assignment from `source`. Read more

Source§ impl CmpEq for f64x4

Source§ type Output = f64x4

👎

Deprecated since 1.5.0: 

use the inherent function `simd_eq` instead

The type returned by `simd_eq`.

Source§ fn simd_eq(self, rhs: Self) -> Self:: Output

👎

Deprecated since 1.5.0: 

use the inherent function `simd_eq` instead

Returns a mask that checks if each element of `self` is equal to the corresponding element of `rhs`. Read more

Source§ impl CmpEq< f64> for f64x4

Source§ type Output = f64x4

👎

Deprecated since 1.5.0: 

use the inherent function `simd_eq` instead

The type returned by `simd_eq`.

Source§ fn simd_eq(self, rhs: f64) -> Self:: Output

👎

Deprecated since 1.5.0: 

use the inherent function `simd_eq` instead

Returns a mask that checks if each element of `self` is equal to the corresponding element of `rhs`. Read more

Source§ impl CmpGe for f64x4

Source§ type Output = f64x4

👎

Deprecated since 1.5.0: 

use the inherent function `simd_ge` instead

The type returned by `simd_ge`.

Source§ fn simd_ge(self, rhs: Self) -> Self:: Output

👎

Deprecated since 1.5.0: 

use the inherent function `simd_ge` instead

Returns a mask that checks if each element of `self` is greater than or equal to the corresponding element of `rhs`. Read more

Source§ impl CmpGe< f64> for f64x4

Source§ type Output = f64x4

👎

Deprecated since 1.5.0: 

use the inherent function `simd_ge` instead

The type returned by `simd_ge`.

Source§ fn simd_ge(self, rhs: f64) -> Self:: Output

👎

Deprecated since 1.5.0: 

use the inherent function `simd_ge` instead

Returns a mask that checks if each element of `self` is greater than or equal to the corresponding element of `rhs`. Read more

Source§ impl CmpGt for f64x4

Source§ type Output = f64x4

👎

Deprecated since 1.5.0: 

use the inherent function `simd_gt` instead

The type returned by `simd_gt`.

Source§ fn simd_gt(self, rhs: Self) -> Self:: Output

👎

Deprecated since 1.5.0: 

use the inherent function `simd_gt` instead

Returns a mask that checks if each element of `self` is greater than the corresponding element of `rhs`. Read more

Source§ impl CmpGt< f64> for f64x4

Source§ type Output = f64x4

👎

Deprecated since 1.5.0: 

use the inherent function `simd_gt` instead

The type returned by `simd_gt`.

Source§ fn simd_gt(self, rhs: f64) -> Self:: Output

👎

Deprecated since 1.5.0: 

use the inherent function `simd_gt` instead

Returns a mask that checks if each element of `self` is greater than the corresponding element of `rhs`. Read more

Source§ impl CmpLe for f64x4

Source§ type Output = f64x4

👎

Deprecated since 1.5.0: 

use the inherent function `simd_le` instead

The type returned by `simd_le`.

Source§ fn simd_le(self, rhs: Self) -> Self:: Output

👎

Deprecated since 1.5.0: 

use the inherent function `simd_le` instead

Returns a mask that checks if each element of `self` is less than or equal to the corresponding element of `rhs`. Read more

Source§ impl CmpLe< f64> for f64x4

Source§ type Output = f64x4

👎

Deprecated since 1.5.0: 

use the inherent function `simd_le` instead

The type returned by `simd_le`.

Source§ fn simd_le(self, rhs: f64) -> Self:: Output

👎

Deprecated since 1.5.0: 

use the inherent function `simd_le` instead

Returns a mask that checks if each element of `self` is less than or equal to the corresponding element of `rhs`. Read more

Source§ impl CmpLt for f64x4

Source§ type Output = f64x4

👎

Deprecated since 1.5.0: 

use the inherent function `simd_lt` instead

The type returned by `simd_lt`.

Source§ fn simd_lt(self, rhs: Self) -> Self:: Output

👎

Deprecated since 1.5.0: 

use the inherent function `simd_lt` instead

Returns a mask that checks if each element of `self` is less than the corresponding element of `rhs`. Read more

Source§ impl CmpLt< f64> for f64x4

Source§ type Output = f64x4

👎

Deprecated since 1.5.0: 

use the inherent function `simd_lt` instead

The type returned by `simd_lt`.

Source§ fn simd_lt(self, rhs: f64) -> Self:: Output

👎

Deprecated since 1.5.0: 

use the inherent function `simd_lt` instead

Returns a mask that checks if each element of `self` is less than the corresponding element of `rhs`. Read more

Source§ impl CmpNe for f64x4

Source§ type Output = f64x4

👎

Deprecated since 1.5.0: 

use the inherent function `simd_ne` instead

The type returned by `simd_ne`.

Source§ fn simd_ne(self, rhs: Self) -> Self:: Output

👎

Deprecated since 1.5.0: 

use the inherent function `simd_ne` instead

Returns a mask that checks if each element of `self` is not equal to the corresponding element of `rhs`. Read more

Source§ impl CmpNe< f64> for f64x4

Source§ type Output = f64x4

👎

Deprecated since 1.5.0: 

use the inherent function `simd_ne` instead

The type returned by `simd_ne`.

Source§ fn simd_ne(self, rhs: f64) -> Self:: Output

👎

Deprecated since 1.5.0: 

use the inherent function `simd_ne` instead

Returns a mask that checks if each element of `self` is not equal to the corresponding element of `rhs`. Read more

### impl Copy for f64x4

Source§ impl Debug for f64x4

Source§ fn fmt(&self, f: &mut Formatter<'_>) -> Result

Formats the value using the given formatter. Read more

Source§ impl Default for f64x4

Source§ fn default() -> f64x4

Returns the “default value” for a type. Read more

Source§ impl Display for f64x4

Source§ fn fmt(&self, f: &mut Formatter<'_>) -> Result

Formats the value using the given formatter. Read more

Source§ impl Div for f64x4

Source§ fn div(self, rhs: Self) -> Self:: Output

Computes division for each element of `self` and the corresponding element of `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `/` operator.

Source§ impl Div<& f64> for f64x4

Source§ fn div(self, rhs: & f64) -> Self:: Output

Computes division for each element of `self` and the uniform scalar `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `/` operator.

Source§ impl Div<& f64> for & f64x4

Source§ fn div(self, rhs: & f64) -> Self:: Output

Computes division for each element of `self` and the uniform scalar `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `/` operator.

Source§ impl Div<& f64x4> for f64x4

Source§ fn div(self, rhs: &Self) -> Self:: Output

Computes division for each element of `self` and the corresponding element of `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `/` operator.

Source§ impl Div<& f64x4> for f64

Source§ fn div(self, rhs: & f64x4) -> Self:: Output

Computes division for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `/` operator.

Source§ impl Div<& f64x4> for & f64x4

Source§ fn div(self, rhs: & f64x4) -> Self:: Output

Computes division for each element of `self` and the corresponding element of `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `/` operator.

Source§ impl Div<& f64x4> for & f64

Source§ fn div(self, rhs: & f64x4) -> Self:: Output

Computes division for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `/` operator.

Source§ impl Div< f64> for f64x4

Source§ fn div(self, rhs: f64) -> Self:: Output

Computes division for each element of `self` and the uniform scalar `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `/` operator.

Source§ impl Div< f64> for & f64x4

Source§ fn div(self, rhs: f64) -> Self:: Output

Computes division for each element of `self` and the uniform scalar `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `/` operator.

Source§ impl Div< f64x4> for f64

Source§ fn div(self, rhs: f64x4) -> Self:: Output

Computes division for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `/` operator.

Source§ impl Div< f64x4> for & f64x4

Source§ fn div(self, rhs: f64x4) -> Self:: Output

Computes division for each element of `self` and the corresponding element of `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `/` operator.

Source§ impl Div< f64x4> for & f64

Source§ fn div(self, rhs: f64x4) -> Self:: Output

Computes division for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `/` operator.

Source§ impl DivAssign for f64x4

Source§ fn div_assign(&mut self, rhs: Self)

Computes division for each element of `self` and the corresponding element of `rhs`.

This always returns the precise result.

Source§ impl DivAssign<& f64> for f64x4

Source§ fn div_assign(&mut self, rhs: & f64)

Computes division for each element of `self` and the uniform scalar `rhs`.

This always returns the precise result.

Source§ impl DivAssign<& f64x4> for f64x4

Source§ fn div_assign(&mut self, rhs: &Self)

Computes division for each element of `self` and the corresponding element of `rhs`.

This always returns the precise result.

Source§ impl DivAssign< f64> for f64x4

Source§ fn div_assign(&mut self, rhs: f64)

Computes division for each element of `self` and the uniform scalar `rhs`.

This always returns the precise result.

Source§ impl From<&[f64]> for f64x4

Source§ fn from(value: &[f64]) -> Self

Converts a slice to a SIMD vector, filling in zeros if there are not enough elements, and panicking if there are too many elements.

Note that in the future, handling of too many elements may change.

Source§ impl From<[f64; 4]> for f64x4

Source§ fn from(arr: [f64; 4]) -> Self

Converts an array to a SIMD vector.

Source§ impl From<__m256d> for f64x4 Available on x86-64 only.

Source§ fn from(value: __m256d) -> Self

Converts a native intrinsics SIMD type to a high-level SIMD type.

Source§ impl From< f64> for f64x4

Source§ fn from(elem: f64) -> Self

Converts a single value to a SIMD vector by setting all elements to that value.

Source§ impl From< f64x4> for [f64; 4]

Source§ fn from(simd: f64x4) -> Self

Converts a SIMD vector to an array.

Source§ impl From< f64x4> for __m256d Available on x86-64 only.

Source§ fn from(value: f64x4) -> Self

Converts a high-level SIMD type to a native intrinsics SIMD type.

Source§ impl From< i32x4> for f64x4

Source§ fn from(v: i32x4) -> Self

Converts to this type from the input type.

Source§ impl LowerExp for f64x4

Source§ fn fmt(&self, f: &mut Formatter<'_>) -> Result

Formats the value using the given formatter. Read more

Source§ impl LowerHex for f64x4

Source§ fn fmt(&self, f: &mut Formatter<'_>) -> Result

Formats the value using the given formatter. Read more

Source§ impl Mul for f64x4

Source§ fn mul(self, rhs: Self) -> Self:: Output

Computes multiplication for each element of `self` and the corresponding element of `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `*` operator.

Source§ impl Mul<& f64> for f64x4

Source§ fn mul(self, rhs: & f64) -> Self:: Output

Computes multiplication for each element of `self` and the uniform scalar `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `*` operator.

Source§ impl Mul<& f64> for & f64x4

Source§ fn mul(self, rhs: & f64) -> Self:: Output

Computes multiplication for each element of `self` and the uniform scalar `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `*` operator.

Source§ impl Mul<& f64x4> for f64x4

Source§ fn mul(self, rhs: &Self) -> Self:: Output

Computes multiplication for each element of `self` and the corresponding element of `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `*` operator.

Source§ impl Mul<& f64x4> for f64

Source§ fn mul(self, rhs: & f64x4) -> Self:: Output

Computes multiplication for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `*` operator.

Source§ impl Mul<& f64x4> for & f64x4

Source§ fn mul(self, rhs: & f64x4) -> Self:: Output

Computes multiplication for each element of `self` and the corresponding element of `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `*` operator.

Source§ impl Mul<& f64x4> for & f64

Source§ fn mul(self, rhs: & f64x4) -> Self:: Output

Computes multiplication for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `*` operator.

Source§ impl Mul< f64> for f64x4

Source§ fn mul(self, rhs: f64) -> Self:: Output

Computes multiplication for each element of `self` and the uniform scalar `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `*` operator.

Source§ impl Mul< f64> for & f64x4

Source§ fn mul(self, rhs: f64) -> Self:: Output

Computes multiplication for each element of `self` and the uniform scalar `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `*` operator.

Source§ impl Mul< f64x4> for f64

Source§ fn mul(self, rhs: f64x4) -> Self:: Output

Computes multiplication for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `*` operator.

Source§ impl Mul< f64x4> for & f64x4

Source§ fn mul(self, rhs: f64x4) -> Self:: Output

Computes multiplication for each element of `self` and the corresponding element of `rhs`.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `*` operator.

Source§ impl Mul< f64x4> for & f64

Source§ fn mul(self, rhs: f64x4) -> Self:: Output

Computes multiplication for the uniform scalar `self` and each element of `rhs`, returning a SIMD vector.

This always returns the precise result.

Source§ type Output = f64x4

The resulting type after applying the `*` operator.

Source§ impl MulAssign for f64x4

Source§ fn mul_assign(&mut self, rhs: Self)

Computes multiplication for each element of `self` and the corresponding element of `rhs`.

This always returns the precise result.

Source§ impl MulAssign<& f64> for f64x4

Source§ fn mul_assign(&mut self, rhs: & f64)

Computes multiplication for each element of `self` and the uniform scalar `rhs`.

This always returns the precise result.

Source§ impl MulAssign<& f64x4> for f64x4

Source§ fn mul_assign(&mut self, rhs: &Self)

Computes multiplication for each element of `self` and the corresponding element of `rhs`.

This always returns the precise result.

Source§ impl MulAssign< f64> for f64x4

Sour

# _mm256_sqrt_pd in core::arch::x86_64 - Rust
URL: https://doc.rust-lang.org/1.94.1/core/arch/x86_64/fn._mm256_sqrt_pd.html

_mm256_sqrt_pd in core::arch::x86_64 - Rust

Function 

_mm256_

sqrt_

1.27.0 · Source 

```
pub fn _mm256_sqrt_pd(a: __m256d) -> __m256d
```

Available on x86-64 and target feature `avx` only.

Expand description

Returns the square root of packed double-precision (64-bit) floating point elements in `a`.

Intel’s documentation

# _mm256_div_pd in core::arch::x86_64 - Rust
URL: https://doc.rust-lang.org/1.94.1/core/arch/x86_64/fn._mm256_div_pd.html

_mm256_div_pd in core::arch::x86_64 - Rust

Function 

_mm256_

1.27.0 (const: unstable) · Source 

```
pub fn _mm256_div_pd(a: __m256d, b: __m256d) -> __m256d
```

Available on x86-64 and target feature `avx` only.

Expand description

Computes the division of each of the 4 packed 64-bit floating-point elements in `a` by the corresponding packed elements in `b`.

Intel’s documentation

Error fetching https://sundials.readthedocs.io/en/latest/cvode/Usage/SIM.html: CRAWL_NOT_FOUND
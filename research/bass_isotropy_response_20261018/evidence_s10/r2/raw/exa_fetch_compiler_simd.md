# Auto-Vectorization in LLVM - LLVM
URL: https://llvm.org/docs/Vectorizers.html

Auto-Vectorization in LLVM - LLVM

# Auto-Vectorization in LLVM#

LLVM has two vectorizers: The Loop Vectorizer, which operates on Loops, and the SLP Vectorizer. These vectorizers focus on different optimization opportunities and use different techniques. The SLP vectorizer merges multiple scalars that are found in the code into vectors while the Loop Vectorizer widens instructions in loops to operate on multiple consecutive iterations.

Both the Loop Vectorizer and the SLP Vectorizer are enabled by default.

### Usage#

The Loop Vectorizer is enabled by default, but it can be disabled through clang using the command line flag:

```
$ clang ... -fno-vectorize  file.c

```

#### Command line flags#

The loop vectorizer uses a cost model to decide on the optimal vectorization factor and unroll factor. However, users of the vectorizer can force the vectorizer to use specific values. Both ‘clang’ and ‘opt’ support the flags below.

Users can control the vectorization SIMD width using the command line flag “-force-vector-width”.

```
$ clang  -mllvm -force-vector-width=8 ...
$ opt -loop-vectorize -force-vector-width=8 ...

```

Users can control the unroll factor using the command line flag “-force-vector-interleave”

```
$ clang  -mllvm -force-vector-interleave=2 ...
$ opt -loop-vectorize -force-vector-interleave=2 ...

```

#### Pragma loop hint directives#

The `#pragma clang loop` directive allows loop vectorization hints to be specified for the subsequent for, while, do-while, or c++11 range-based for loop. The directive allows vectorization and interleaving to be enabled or disabled. Vector width as well as interleave count can also be manually specified. The following example explicitly enables vectorization and interleaving:

```
#pragma clang loop vectorize(enable) interleave(enable)
while(...) {
  ...
}

```

The following example implicitly enables vectorization and interleaving by specifying a vector width and interleaving count:

```
#pragma clang loop vectorize_width(2) interleave_count(2)
for(...) {
  ...
}

```

See the Clang language extensions for details.

### Diagnostics#

Many loops cannot be vectorized including loops with complicated control flow, unvectorizable types, and unvectorizable calls. The loop vectorizer generates optimization remarks which can be queried using command line options to identify and diagnose loops that are skipped by the loop-vectorizer.

Optimization remarks are enabled using:

`-Rpass=loop-vectorize` identifies loops that were successfully vectorized.

`-Rpass-missed=loop-vectorize` identifies loops that failed vectorization and indicates if vectorization was specified.

`-Rpass-analysis=loop-vectorize` identifies the statements that caused vectorization to fail. If in addition `-fsave-optimization-record` is provided, multiple causes of vectorization failure may be listed (this behavior might change in the future).

Consider the following loop:

```
#pragma clang loop vectorize(enable)
for (int i = 0; i < Length; i++) {
  switch(A[i]) {
  case 0: A[i] = i*2; break;
  case 1: A[i] = i;   break;
  default: A[i] = 0;
  }
}

```

The command line `-Rpass-missed=loop-vectorize` prints the remark:

```
no_switch.cpp:4:5: remark: loop not vectorized: vectorization is explicitly enabled [-Rpass-missed=loop-vectorize]

```

And the command line `-Rpass-analysis=loop-vectorize` indicates that the switch statement cannot be vectorized.

```
no_switch.cpp:4:5: remark: loop not vectorized: loop contains a switch statement [-Rpass-analysis=loop-vectorize]
  switch(A[i]) {
  ^

```

To ensure line and column numbers are produced include the command line options `-gline-tables-only` and `-gcolumn-info`. See the Clang user manual for details

### Features#

The LLVM Loop Vectorizer has a number of features that allow it to vectorize complex loops.

#### Loops with unknown trip count#

The Loop Vectorizer supports loops with an unknown trip count. In the loop below, the iteration `start` and `finish` points are unknown, and the Loop Vectorizer has a mechanism to vectorize loops that do not start at zero. In this example, ‘n’ may not be a multiple of the vector width, and the vectorizer has to execute the last few iterations as scalar code. Keeping a scalar copy of the loop increases the code size.

```
void bar(float *A, float* B, float K, int start, int end) {
  for (int i = start; i < end; ++i)
    A[i] *= B[i] + K;
}

```

#### Runtime Checks of Pointers#

In the example below, if the pointers A and B point to consecutive addresses, then it is illegal to vectorize the code because some elements of A will be written before they are read from array B.

Some programmers use the ‘restrict’ keyword to notify the compiler that the pointers are disjointed, but in our example, the Loop Vectorizer has no way of knowing that the pointers A and B are unique. The Loop Vectorizer handles this loop by placing code that checks, at runtime, if the arrays A and B point to disjointed memory locations. If arrays A and B overlap, then the scalar version of the loop is executed.

```
void bar(float *A, float* B, float K, int n) {
  for (int i = 0; i < n; ++i)
    A[i] *= B[i] + K;
}

```

#### Reductions#

In this example the `sum` variable is used by consecutive iterations of the loop. Normally, this would prevent vectorization, but the vectorizer can detect that ‘sum’ is a reduction variable. The variable ‘sum’ becomes a vector of integers, and at the end of the loop the elements of the array are added together to create the correct result. We support a number of different reduction operations, such as addition, multiplication, XOR, AND and OR.

```
int foo(int *A, int n) {
  unsigned sum = 0;
  for (int i = 0; i < n; ++i)
    sum += A[i] + 5;
  return sum;
}

```

Fully vectorizing reductions requires reordering operations, which is problematic for floating-point arithmetic because it is not associative; therefore results may depend on the evaluation order.

Changing floating-point results is implicitly prohibited by the C and C++ standards, therefore LLVM supports vectorizing floating point reductions only when at least the `-fassociative-math -fno-signed-zeros -fno-trapping-math` subset of `-ffast-math` is used on most targets. On some targets, such as AArch64 and RISC-V, LLVM can generate ordered reductions that preserve the exact result, enabling limited, standards-compliant vectorization. However, ordered reductions are typically less efficient than traditionally vectorized reductions, therefore enabling floating-point reordering may still result in more performant reductions on these targets.

#### Inductions#

In this example the value of the induction variable `i` is saved into an array. The Loop Vectorizer knows to vectorize induction variables.

```
void bar(float *A, int n) {
  for (int i = 0; i < n; ++i)
    A[i] = i;
}

```

#### If Conversion#

The Loop Vectorizer is able to “flatten” the IF statement in the code and generate a single stream of instructions. The Loop Vectorizer supports any control flow in the innermost loop. The innermost loop may contain complex nesting of IFs, ELSEs and even GOTOs.

```
int foo(int *A, int *B, int n) {
  unsigned sum = 0;
  for (int i = 0; i < n; ++i)
    if (A[i] > B[i])
      sum += A[i] + 5;
  return sum;
}

```

#### Pointer Induction Variables#

This example uses the “accumulate” function of the standard c++ library. This loop uses C++ iterators, which are pointers, and not integer indices. The Loop Vectorizer detects pointer induction variables and can vectorize this loop. This feature is important because many C++ programs use iterators.

```
int baz(int *A, int n) {
  return std::accumulate(A, A + n, 0);
}

```

#### Reverse Iterators#

The Loop Vectorizer can vectorize loops that count backwards.

```
void foo(int *A, int n) {
  for (int i = n; i > 0; --i)
    A[i] +=1;
}

```

#### Scatter / Gather#

The Loop Vectorizer can vectorize code that becomes a sequence of scalar instructions that scatter/gathers memory.

```
void foo(int * A, int * B, int n) {
  for (intptr_t i = 0; i < n; ++i)
      A[i] += B[i * 4];
}

```

In many situations the cost model will inform LLVM that this is not beneficial and LLVM will only vectorize such code if forced with “-mllvm -force-vector-width=#”.

#### Vectorization of Mixed Types#

The Loop Vectorizer can vectorize programs with mixed types. The Vectorizer cost model can estimate the cost of the type conversion and decide if vectorization is profitable.

```
void foo(int *A, char *B, int n) {
  for (int i = 0; i < n; ++i)
    A[i] += 4 * B[i];
}

```

#### Global Structures Alias Analysis#

Access to global structures can also be vectorized, with alias analysis being used to make sure accesses don’t alias. Run-time checks can also be added on pointer access to structure members.

Many variations are supported, but some that rely on undefined behaviour being ignored (as other compilers do) are still being left un-vectorized.

```
struct { int A[100], K, B[100]; } Foo;

void foo() {
  for (int i = 0; i < 100; ++i)
    Foo.A[i] = Foo.B[i] + 100;
}

```

#### Vectorization of function calls#

The Loop Vectorizer can vectorize intrinsic math functions. See the table below for a list of these functions.

pow

exp

exp2

sin

cos

sqrt

log

log2

log10

floor

fma

trunc

nearbyint

fmuladd

Note that the optimizer may not be able to vectorize math library functions that correspond to these intrinsics if the library calls access external state such as “errno”. To allow better optimization of C/C++ math library functions, use “-fno-math-errno”.

The loop vectorizer knows about special instructions on the target and will vectorize a loop containing a function call that maps to the instructions. For example, the loop below will be vectorized on Intel x86 if the SSE4.1 roundps instruction is available.

```
void foo(float *f) {
  for (int i = 0; i != 1024; ++i)
    f[i] = floorf(f[i]);
}

```

Many of these math functions are only vectorizable if the file has been built with a specified target vector library that provides a vector implementation of that math function. Using clang, this is handled by the “-fveclib” command line option with one of the following vector libraries: “Accelerate,libmvec,MASSV,SVML,SLEEF,Darwin_libsystem_m,ArmPL,AMDLIBM”

```
$ clang ... -fno-math-errno -fveclib=libmvec file.c

```

#### Partial unrolling during vectorization#

Modern processors feature multiple execution units, and only programs that contain a high degree of parallelism can fully utilize the entire width of the machine. The Loop Vectorizer increases the instruction level parallelism (ILP) by performing partial-unrolling of loops.

In the example below the entire array is accumulated into the variable ‘sum’. This is inefficient because only a single execution port can be used by the processor. By unrolling the code the Loop Vectorizer allows two or more execution ports to be used simultaneously.

```
int foo(int *A, int n) {
  unsigned sum = 0;
  for (int i = 0; i < n; ++i)
      sum += A[i];
  return sum;
}

```

The Loop Vectorizer uses a cost model to decide when it is profitable to unroll loops. The decision to unroll the loop depends on the register pressure and the generated code size.

#### Epilogue Vectorization#

When vectorizing a loop, often a scalar remainder (epilogue) loop is necessary to execute tail iterations of the loop if the loop trip count is unknown or it does not evenly divide the vectorization and unroll factors. When the vectorization and unroll factors are large, it’s possible for loops with smaller trip counts to end up spending most of their time in the scalar (rather than the vector) code. In order to address this issue, the inner loop vectorizer is enhanced with a feature that allows it to vectorize epilogue loops with a vectorization and unroll factor combination that makes it more likely for small trip count loops to still execute in vectorized code. The diagram below shows the CFG for a typical epilogue vectorized loop with runtime checks. As illustrated the control flow is structured in a way that avoids duplicating the runtime pointer checks and optimizes the path length for loops that have very small trip counts.

#### Early Exit Vectorization#

When vectorizing a loop with a single early exit, the loop blocks following the early exit are predicated and the vector loop will always exit via the latch. The loop terminates with a single BranchOnTwoConds VPInstruction, which takes both the early and latch exiting conditions. If the early exiting condition is true, BranchOnTwoConds exits to an intermediate block (`vector.early.exit` below). This intermediate block is responsible for calculating any exit values of loop-defined variables that are used in the early exit block. If the latch exiting condition is true, BranchOnTwoConds exits to the `middle.block` which selects between the exit block and the scalar remainder loop. Otherwise BranchOnTwoConds continues executing the loop by jumping back to the region header.

BranchOnTwoConds is lowered to a chain of conditional branches exiting the vector loop after dissolving loop regions:

### Performance#

This section shows the execution time of Clang on a simple benchmark: gcc-loops. This benchmarks is a collection of loops from the GCC autovectorization page by Dorit Nuzman.

The chart below compares GCC-4.7, ICC-13, and Clang-SVN with and without loop vectorization at -O3, tuned for “corei7-avx”, running on a Sandybridge iMac. The Y-axis shows the time in msec. Lower is better. The last column shows the geomean of all the kernels.

And Linpack-pc with the same configuration. Result is Mflops, higher is better.

### Ongoing Development Directions#

Vectorization Plan
: Modeling the process and upgrading the infrastructure of LLVM’s Loop Vectorizer.

### Details#

The goal of SLP vectorization (a.k.a. superword-level parallelism) is to combine similar independent instructions into vector instructions. Memory accesses, arithmetic operations, comparison operations, PHI-nodes, can all be vectorized using this technique.

For example, the following function performs very similar operations on its inputs (a1, b1) and (a2, b2). The basic-block vectorizer may combine these into vector operations.

```
void foo(float a1, float a2, float b1, float b2, float *A) {
  A[0] = a1*(a1 + b1);
  A[1] = a2*(a2 + b2);
  A[2] = a1*(a1 + b1);
  A[3] = a2*(a2 + b2);
}

```

The SLP-vectorizer processes the code bottom-up, across basic blocks, in search of scalars to combine.

### Usage#

The SLP Vectorizer is enabled by default, but it can be disabled through clang using the command line flag:

```
$ clang -fno-slp-vectorize file.c

```

## The Sandbox Vectorizer#

The Sandbox Vectorizer is an experimental framework for building modular vectorization pipelines on top of Sandbox IR, with a focus on ease of testing and ease of development.

 On this page 

- Auto-Vectorization in LLVM

- The Loop Vectorizer

- Usage

- Command line flags
- Pragma loop hint directives
- Diagnostics
- Features

- Loops with unknown trip count
- Runtime Checks of Pointers
- Reductions
- Inductions
- If Conversion
- Pointer Induction Variables
- Reverse Iterators
- Scatter / Gather
- Vectorization of Mixed Types
- Global Structures Alias Analysis
- Vectorization of function calls
- Partial unrolling during vectorization
- Epilogue Vectorization
- Early Exit Vectorization
- Performance
- Ongoing Development Directions
- The SLP Vectorizer

- Details
- Usage
- The Sandbox Vectorizer

# std::arch - Rust
URL: https://doc.rust-lang.org/1.94.1/std/arch/

std::arch - Rust

# Module arch Copy item path

Expand description

SIMD and vendor intrinsics module.

This module is intended to be the gateway to architecture-specific intrinsic functions, typically related to SIMD (but not always!). Each architecture that Rust compiles to may contain a submodule here, which means that this is not a portable module! If you’re writing a portable library take care when using these APIs!

Under this module you’ll find an architecture-named module, such as `x86_64`. Each `#[cfg(target_arch)]` that Rust can compile to may have a module entry here, only present on that particular target. For example the `i686-pc-windows-msvc` target will have an `x86` module here, whereas `x86_64-pc-windows-msvc` has `x86_64`.

## § Overview

This module exposes vendor-specific intrinsics that typically correspond to a single machine instruction. These intrinsics are not portable: their availability is architecture-dependent, and not all machines of that architecture might provide the intrinsic.

The `arch` module is intended to be a low-level implementation detail for higher-level APIs. Using it correctly can be quite tricky as you need to ensure at least a few guarantees are upheld:

- The correct architecture’s module is used. For example the `arm` module isn’t available on the `x86_64-unknown-linux-gnu` target. This is typically done by ensuring that `#[cfg]` is used appropriately when using this module.
- The CPU the program is currently running on supports the function being called. For example it is unsafe to call an AVX2 function on a CPU that doesn’t actually support AVX2.

As a result of the latter of these guarantees all intrinsics in this module are `unsafe` and extra care needs to be taken when calling them!

## § CPU Feature Detection

In order to call these APIs in a safe fashion there’s a number of mechanisms available to ensure that the correct CPU feature is available to call an intrinsic. Let’s consider, for example, the `_mm256_add_epi64` intrinsics on the `x86` and `x86_64` architectures. This function requires the AVX2 feature as documented by Intel so to correctly call this function we need to (a) guarantee we only call it on `x86`/`x86_64` and (b) ensure that the CPU feature is available

### § Static CPU Feature Detection

The first option available to us is to conditionally compile code via the `#[cfg]` attribute. CPU features correspond to the `target_feature` cfg available, and can be used like so:

ⓘ

```
#[cfg(
    all(
        any(target_arch = "x86", target_arch = "x86_64"),
        target_feature = "avx2"
    )
)]
fn foo() {
    #[cfg(target_arch = "x86")]
    use std::arch::x86::_mm256_add_epi64;
    #[cfg(target_arch = "x86_64")]
    use std::arch::x86_64::_mm256_add_epi64;

    unsafe {
        _mm256_add_epi64(...);
    }
}
```

Here we’re using `#[cfg(target_feature = "avx2")]` to conditionally compile this function into our module. This means that if the `avx2` feature is enabled statically then we’ll use the `_mm256_add_epi64` function at runtime. The `unsafe` block here can be justified through the usage of `#[cfg]` to only compile the code in situations where the safety guarantees are upheld.

Statically enabling a feature is typically done with the `-C target-feature` or `-C target-cpu` flags to the compiler. For example if your local CPU supports AVX2 then you can compile the above function with:

```sh
$ RUSTFLAGS='-C target-cpu=native' cargo build
```

Or otherwise you can specifically enable just the AVX2 feature:

```sh
$ RUSTFLAGS='-C target-feature=+avx2' cargo build
```

Note that when you compile a binary with a particular feature enabled it’s important to ensure that you only run the binary on systems which satisfy the required feature set.

### § Dynamic CPU Feature Detection

Sometimes statically dispatching isn’t quite what you want. Instead you might want to build a portable binary that runs across a variety of CPUs, but at runtime it selects the most optimized implementation available. This allows you to build a “least common denominator” binary which has certain sections more optimized for different CPUs.

Taking our previous example from before, we’re going to compile our binary without AVX2 support, but we’d like to enable it for just one function. We can do that in a manner like:

ⓘ

```
fn foo() {
    #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
    {
        if is_x86_feature_detected!("avx2") {
            return unsafe { foo_avx2() };
        }
    }

    // fallback implementation without using AVX2
}

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "avx2")]
unsafe fn foo_avx2() {
    #[cfg(target_arch = "x86")]
    use std::arch::x86::_mm256_add_epi64;
    #[cfg(target_arch = "x86_64")]
    use std::arch::x86_64::_mm256_add_epi64;

    unsafe { _mm256_add_epi64(...); }
}
```

There’s a couple of components in play here, so let’s go through them in detail!

- First up we notice the `is_x86_feature_detected!` macro. Provided by the standard library, this macro will perform necessary runtime detection to determine whether the CPU the program is running on supports the specified feature. In this case the macro will expand to a boolean expression evaluating to whether the local CPU has the AVX2 feature or not.

Note that this macro, like the `arch` module, is platform-specific. For example calling `is_x86_feature_detected!("avx2")` on ARM will be a compile time error. To ensure we don’t hit this error a statement level `#[cfg]` is used to only compile usage of the macro on `x86`/`x86_64`.
- Next up we see our AVX2-enabled function, `foo_avx2`. This function is decorated with the `#[target_feature]` attribute which enables a CPU feature for just this one function. Using a compiler flag like `-C target-feature=+avx2` will enable AVX2 for the entire program, but using an attribute will only enable it for the one function. Usage of the `#[target_feature]` attribute currently requires the function to also be `unsafe`, as we see here. This is because the function can only be correctly called on systems which have the AVX2 (like the intrinsics themselves).

And with all that we should have a working program! This program will run across all machines and it’ll use the optimized AVX2 implementation on machines where support is detected.

## § Ergonomics

It’s important to note that using the `arch` module is not the easiest thing in the world, so if you’re curious to try it out you may want to brace yourself for some wordiness!

The primary purpose of this module is to enable stable crates on crates.io to build up much more ergonomic abstractions which end up using SIMD under the hood. Over time these abstractions may also move into the standard library itself, but for now this module is tasked with providing the bare minimum necessary to use vendor intrinsics on stable Rust.

## § Other architectures

This documentation is only for one particular architecture, you can find others at:

- `x86`
- `x86_64`
- `arm`
- `aarch64`
- `amdgpu`
- `riscv32`
- `riscv64`
- `mips`
- `mips64`
- `powerpc`
- `powerpc64`
- `nvptx`
- `wasm32`
- `loongarch32`
- `loongarch64`
- `s390x`

## § Examples

First let’s take a look at not actually using any intrinsics but instead using LLVM’s auto-vectorization to produce optimized vectorized code for AVX2 and also for the default platform.

```
fn main() {
    let mut dst = [0];
    add_quickly(&[1], &[2], &mut dst);
    assert_eq!(dst[0], 3);
}

fn add_quickly(a: &[u8], b: &[u8], c: &mut [u8]) {
    #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
    {
        // Note that this `unsafe` block is safe because we're testing
        // that the `avx2` feature is indeed available on our CPU.
        if is_x86_feature_detected!("avx2") {
            return unsafe { add_quickly_avx2(a, b, c) };
        }
    }

    add_quickly_fallback(a, b, c)
}

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "avx2")]
unsafe fn add_quickly_avx2(a: &[u8], b: &[u8], c: &mut [u8]) {
    add_quickly_fallback(a, b, c) // the function below is inlined here
}

fn add_quickly_fallback(a: &[u8], b: &[u8], c: &mut [u8]) {
    for ((a, b), c) in a.iter().zip(b).zip(c) {
        *c = *a + *b;
    }
}
```

Next up let’s take a look at an example of manually using intrinsics. Here we’ll be using SSE4.1 features to implement hex encoding.

```
fn main() {
    let mut dst = [0; 32];
    hex_encode(b"\x01\x02\x03", &mut dst);
    assert_eq!(&dst[..6], b"010203");

    let mut src = [0; 16];
    for i in 0..16 {
        src[i] = (i + 1) as u8;
    }
    hex_encode(&src, &mut dst);
    assert_eq!(&dst, b"0102030405060708090a0b0c0d0e0f10");
}

pub fn hex_encode(src: &[u8], dst: &mut [u8]) {
    let len = src.len().checked_mul(2).unwrap();
    assert!(dst.len() >= len);

    #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
    {
        if is_x86_feature_detected!("sse4.1") {
            return unsafe { hex_encode_sse41(src, dst) };
        }
    }

    hex_encode_fallback(src, dst)
}

// translated from
// <https://github.com/Matherunner/bin2hex-sse/blob/master/base16_sse4.cpp>
#[target_feature(enable = "sse4.1")]
#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
unsafe fn hex_encode_sse41(mut src: &[u8], dst: &mut [u8]) {
    #[cfg(target_arch = "x86")]
    use std::arch::x86::*;
    #[cfg(target_arch = "x86_64")]
    use std::arch::x86_64::*;

    unsafe {
        let ascii_zero = _mm_set1_epi8(b'0' as i8);
        let nines = _mm_set1_epi8(9);
        let ascii_a = _mm_set1_epi8((b'a' - 9 - 1) as i8);
        let and4bits = _mm_set1_epi8(0xf);

        let mut i = 0_isize;
        while src.len() >= 16 {
            let invec = _mm_loadu_si128(src.as_ptr() as *const _);

            let masked1 = _mm_and_si128(invec, and4bits);
            let masked2 = _mm_and_si128(_mm_srli_epi64(invec, 4), and4bits);

            // return 0xff corresponding to the elements > 9, or 0x00 otherwise
            let cmpmask1 = _mm_cmpgt_epi8(masked1, nines);
            let cmpmask2 = _mm_cmpgt_epi8(masked2, nines);

            // add '0' or the offset depending on the masks
            let masked1 = _mm_add_epi8(
                masked1,
                _mm_blendv_epi8(ascii_zero, ascii_a, cmpmask1),
            );
            let masked2 = _mm_add_epi8(
                masked2,
                _mm_blendv_epi8(ascii_zero, ascii_a, cmpmask2),
            );

            // interleave masked1 and masked2 bytes
            let res1 = _mm_unpacklo_epi8(masked2, masked1);
            let res2 = _mm_unpackhi_epi8(masked2, masked1);

            _mm_storeu_si128(dst.as_mut_ptr().offset(i * 2) as *mut _, res1);
            _mm_storeu_si128(
                dst.as_mut_ptr().offset(i * 2 + 16) as *mut _,
                res2,
            );
            src = &src[16..];
            i += 16;
        }

        let i = i as usize;
        hex_encode_fallback(src, &mut dst[i * 2..]);
    }
}

fn hex_encode_fallback(src: &[u8], dst: &mut [u8]) {
    fn hex(byte: u8) -> u8 {
        static TABLE: &[u8] = b"0123456789abcdef";
        TABLE[byte as usize]
    }

    for (byte, slots) in src.iter().zip(dst.chunks_mut(2)) {
        slots[0] = hex((*byte >> 4) & 0xf);
        slots[1] = hex(*byte & 0xf);
    }
}
```

## Re-exports§

`pub use core::arch::*;`

## Macros§

is_

aarch64_

feature_

detected
: Check for the presence of a CPU feature at runtime.
is_

loongarch_

feature_

detected
: Check for the presence of a CPU feature at runtime.
is_

riscv_

feature_

detected
: Check for the presence of a CPU feature at runtime.
is_

s390x_

feature_

detected
: Check for the presence of a CPU feature at runtime.
is_

x86_

feature_

detected
: Check for the presence of a CPU feature at runtime.
is_

arm_

feature_

detected

Experimental
: Check for the presence of a CPU feature at runtime.
is_

mips64_

feature_

detected

Experimental
: Check for the presence of a CPU feature at runtime.
is_

mips_

feature_

detected

Experimental
: Check for the presence of a CPU feature at runtime.
is_

powerpc64_

feature_

detected

Experimental
: Check for the presence of a CPU feature at runtime.
is_

powerpc_

feature_

detected

Experimental
: Check for the presence of a CPU feature at runtime.

# std::simd - Rust
URL: https://doc.rust-lang.org/1.94.1/std/simd/

std::simd - Rust

Source 

🔬 This is a nightly-only experimental API. (`portable_simd` #86656)

Expand description

Portable SIMD module.

This module offers a portable abstraction for SIMD operations that is not bound to any particular hardware architecture.

## § What is “portable”?

This module provides a SIMD implementation that is fast and predictable on any target.

#### § Portable SIMD works on every target

Unlike target-specific SIMD in `std::arch`, portable SIMD compiles for every target. In this regard, it is just like “regular” Rust.

#### § Portable SIMD is consistent between targets

A program using portable SIMD can expect identical behavior on any target. In most regards, `Simd<T, N>` can be thought of as a parallelized `[T; N]` and operates like a sequence of `T`.

This has one notable exception: a handful of older architectures (e.g. `armv7` and `powerpc`) flush subnormal `f32` values to zero. On these architectures, subnormal `f32` input values are replaced with zeros, and any operation producing subnormal `f32` values produces zeros instead. This doesn’t affect most architectures or programs.

#### § Operations use the best instructions available

Operations provided by this module compile to the best available SIMD instructions.

Portable SIMD is not a low-level vendor library, and operations in portable SIMD do not necessarily map to a single instruction. Instead, they map to a reasonable implementation of the operation for the target.

Consistency between targets is not compromised to use faster or fewer instructions. In some cases, `std::arch` will provide a faster function that has slightly different behavior than the `std::simd` equivalent. For example, `_mm_min_ps` 1 can be slightly faster than `SimdFloat::simd_min`, but does not conform to the IEEE standard also used by `f32::min`. When necessary, `Simd<T, N>` can be converted to the types provided by `std::arch` to make use of target-specific functions.

Many targets simply don’t have SIMD, or don’t support SIMD for a particular element type. In those cases, regular scalar operations are generated instead.

---

1. `_mm_min_ps(x, y)` is equivalent to `x.simd_lt(y).select(x, y)` ↩

## Modules§

cmp

Experimental
: Traits for comparing and ordering vectors.
num

Experimental
: Traits for vectors with numeric elements.
prelude

Experimental
: The portable SIMD prelude.
ptr

Experimental
: Traits for vectors of pointers.

## Macros§

simd_

swizzle

Experimental
: Constructs a new SIMD vector by copying elements from selected elements in other vectors.

## Structs§

Lane

Count

Experimental
: Specifies the number of lanes in a SIMD vector as a type.
Mask

Experimental
: A SIMD vector mask for `N` elements of width specified by `Element`.
Simd

Experimental
: A SIMD vector with the shape of `[T; N]` but the operations of `T`.

## Traits§

Mask

Element

Experimental
: Marker trait for types that may be used as SIMD mask elements.
Simd

Cast

Experimental
: Supporting trait for `Simd::cast`. Typically doesn’t need to be used directly.
Simd

Element

Experimental
: Marker trait for types that may be used as SIMD vector elements.
StdFloat

Experimental
: This trait provides a possibly-temporary implementation of float functions that may, in the absence of hardware support, canonicalize to calling an operating system’s `math.h` dynamically-loaded library (also known as a shared object). As these conditionally require runtime support, they should only appear in binaries built assuming OS support: `std`.
Supported

Lane

Count

Experimental
: Statically guarantees that a lane count is marked as supported.
Swizzle

Experimental
: Creates a vector from the elements of another vector.
ToBytes

Experimental
: Converts SIMD vectors to vectors of bytes

## Type Aliases§

f32x1

Experimental
: A SIMD vector with one element of type `f32`.
f32x2

Experimental
: A SIMD vector with two elements of type `f32`.
f32x4

Experimental
: A SIMD vector with four elements of type `f32`.
f32x8

Experimental
: A SIMD vector with eight elements of type `f32`.
f32x16

Experimental
: A SIMD vector with 16 elements of type `f32`.
f32x32

Experimental
: A SIMD vector with 32 elements of type `f32`.
f32x64

Experimental
: A SIMD vector with 64 elements of type `f32`.
f64x1

Experimental
: A SIMD vector with one element of type `f64`.
f64x2

Experimental
: A SIMD vector with two elements of type `f64`.
f64x4

Experimental
: A SIMD vector with four elements of type `f64`.
f64x8

Experimental
: A SIMD vector with eight elements of type `f64`.
f64x16

Experimental
: A SIMD vector with 16 elements of type `f64`.
f64x32

Experimental
: A SIMD vector with 32 elements of type `f64`.
f64x64

Experimental
: A SIMD vector with 64 elements of type `f64`.
i8x1

Experimental
: A SIMD vector with one element of type `i8`.
i8x2

Experimental
: A SIMD vector with two elements of type `i8`.
i8x4

Experimental
: A SIMD vector with four elements of type `i8`.
i8x8

Experimental
: A SIMD vector with eight elements of type `i8`.
i8x16

Experimental
: A SIMD vector with 16 elements of type `i8`.
i8x32

Experimental
: A SIMD vector with 32 elements of type `i8`.
i8x64

Experimental
: A SIMD vector with 64 elements of type `i8`.
i16x1

Experimental
: A SIMD vector with one element of type `i16`.
i16x2

Experimental
: A SIMD vector with two elements of type `i16`.
i16x4

Experimental
: A SIMD vector with four elements of type `i16`.
i16x8

Experimental
: A SIMD vector with eight elements of type `i16`.
i16x16

Experimental
: A SIMD vector with 16 elements of type `i16`.
i16x32

Experimental
: A SIMD vector with 32 elements of type `i16`.
i16x64

Experimental
: A SIMD vector with 64 elements of type `i16`.
i32x1

Experimental
: A SIMD vector with one element of type `i32`.
i32x2

Experimental
: A SIMD vector with two elements of type `i32`.
i32x4

Experimental
: A SIMD vector with four elements of type `i32`.
i32x8

Experimental
: A SIMD vector with eight elements of type `i32`.
i32x16

Experimental
: A SIMD vector with 16 elements of type `i32`.
i32x32

Experimental
: A SIMD vector with 32 elements of type `i32`.
i32x64

Experimental
: A SIMD vector with 64 elements of type `i32`.
i64x1

Experimental
: A SIMD vector with one element of type `i64`.
i64x2

Experimental
: A SIMD vector with two elements of type `i64`.
i64x4

Experimental
: A SIMD vector with four elements of type `i64`.
i64x8

Experimental
: A SIMD vector with eight elements of type `i64`.
i64x16

Experimental
: A SIMD vector with 16 elements of type `i64`.
i64x32

Experimental
: A SIMD vector with 32 elements of type `i64`.
i64x64

Experimental
: A SIMD vector with 64 elements of type `i64`.
isizex1

Experimental
: A SIMD vector with one element of type `isize`.
isizex2

Experimental
: A SIMD vector with two elements of type `isize`.
isizex4

Experimental
: A SIMD vector with four elements of type `isize`.
isizex8

Experimental
: A SIMD vector with eight elements of type `isize`.
isizex16

Experimental
: A SIMD vector with 16 elements of type `isize`.
isizex32

Experimental
: A SIMD vector with 32 elements of type `isize`.
isizex64

Experimental
: A SIMD vector with 64 elements of type `isize`.
mask8x1

Experimental
: A SIMD mask with one element for vectors with 8-bit element types.
mask8x2

Experimental
: A SIMD mask with two elements for vectors with 8-bit element types.
mask8x4

Experimental
: A SIMD mask with four elements for vectors with 8-bit element types.
mask8x8

Experimental
: A SIMD mask with eight elements for vectors with 8-bit element types.
mask8x16

Experimental
: A SIMD mask with 16 elements for vectors with 8-bit element types.
mask8x32

Experimental
: A SIMD mask with 32 elements for vectors with 8-bit element types.
mask8x64

Experimental
: A SIMD mask with 64 elements for vectors with 8-bit element types.
mask16x1

Experimental
: A SIMD mask with one element for vectors with 16-bit element types.
mask16x2

Experimental
: A SIMD mask with two elements for vectors with 16-bit element types.
mask16x4

Experimental
: A SIMD mask with four elements for vectors with 16-bit element types.
mask16x8

Experimental
: A SIMD mask with eight elements for vectors with 16-bit element types.
mask16x16

Experimental
: A SIMD mask with 16 elements for vectors with 16-bit element types.
mask16x32

Experimental
: A SIMD mask with 32 elements for vectors with 16-bit element types.
mask16x64

Experimental
: A SIMD mask with 64 elements for vectors with 16-bit element types.
mask32x1

Experimental
: A SIMD mask with one element for vectors with 32-bit element types.
mask32x2

Experimental
: A SIMD mask with two elements for vectors with 32-bit element types.
mask32x4

Experimental
: A SIMD mask with four elements for vectors with 32-bit element types.
mask32x8

Experimental
: A SIMD mask with eight elements for vectors with 32-bit element types.
mask32x16

Experimental
: A SIMD mask with 16 elements for vectors with 32-bit element types.
mask32x32

Experimental
: A SIMD mask with 32 elements for vectors with 32-bit element types.
mask32x64

Experimental
: A SIMD mask with 64 elements for vectors with 32-bit element types.
mask64x1

Experimental
: A SIMD mask with one element for vectors with 64-bit element types.
mask64x2

Experimental
: A SIMD mask with two elements for vectors with 64-bit element types.
mask64x4

Experimental
: A SIMD mask with four elements for vectors with 64-bit element types.
mask64x8

Experimental
: A SIMD mask with eight elements for vectors with 64-bit element types.
mask64x16

Experimental
: A SIMD mask with 16 elements for vectors with 64-bit element types.
mask64x32

Experimental
: A SIMD mask with 32 elements for vectors with 64-bit element types.
mask64x64

Experimental
: A SIMD mask with 64 elements for vectors with 64-bit element types.
masksizex1

Experimental
: A SIMD mask with one element for vectors with pointer-sized element types.
masksizex2

Experimental
: A SIMD mask with two elements for vectors with pointer-sized element types.
masksizex4

Experimental
: A SIMD mask with four elements for vectors with pointer-sized element types.
masksizex8

Experimental
: A SIMD mask with eight elements for vectors with pointer-sized element types.
masksizex16

Experimental
: A SIMD mask with 16 elements for vectors with pointer-sized element types.
masksizex32

Experimental
: A SIMD mask with 32 elements for vectors with pointer-sized element types.
masksizex64

Experimental
: A SIMD mask with 64 elements for vectors with pointer-sized element types.
u8x1

Experimental
: A SIMD vector with one element of type `u8`.
u8x2

Experimental
: A SIMD vector with two elements of type `u8`.
u8x4

Experimental
: A SIMD vector with four elements of type `u8`.
u8x8

Experimental
: A SIMD vector with eight elements of type `u8`.
u8x16

Experimental
: A SIMD vector with 16 elements of type `u8`.
u8x32

Experimental
: A SIMD vector with 32 elements of type `u8`.
u8x64

Experimental
: A SIMD vector with 64 elements of type `u8`.
u16x1

Experimental
: A SIMD vector with one element of type `u16`.
u16x2

Experimental
: A SIMD vector with two elements of type `u16`.
u16x4

Experimental
: A SIMD vector with four elements of type `u16`.
u16x8

Experimental
: A SIMD vector with eight elements of type `u16`.
u16x16

Experimental
: A SIMD vector with 16 elements of type `u16`.
u16x32

Experimental
: A SIMD vector with 32 elements of type `u16`.
u16x64

Experimental
: A SIMD vector with 64 elements of type `u16`.
u32x1

Experimental
: A SIMD vector with one element of type `u32`.
u32x2

Experimental
: A SIMD vector with two elements of type `u32`.
u32x4

Experimental
: A SIMD vector with four elements of type `u32`.
u32x8

Experimental
: A SIMD vector with eight elements of type `u32`.
u32x16

Experimental
: A SIMD vector with 16 elements of type `u32`.
u32x32

Experimental
: A SIMD vector with 32 elements of type `u32`.
u32x64

Experimental
: A SIMD vector with 64 elements of type `u32`.
u64x1

Experimental
: A SIMD vector with one element of type `u64`.
u64x2

Experimental
: A SIMD vector with two elements of type `u64`.
u64x4

Experimental
: A SIMD vector with four elements of type `u64`.
u64x8

Experimental
: A SIMD vector with eight elements of type `u64`.
u64x16

Experimental
: A SIMD vector with 16 elements of type `u64`.
u64x32

Experimental
: A SIMD vector with 32 elements of type `u64`.
u64x64

Experimental
: A SIMD vector with 64 elements of type `u64`.
usizex1

Experimental
: A SIMD vector with one element of type `usize`.
usizex2

Experimental
: A SIMD vector with two elements of type `usize`.
usizex4

Experimental
: A SIMD vector with four elements of type `usize`.
usizex8

Experimental
: A SIMD vector with eight elements of type `usize`.
usizex16

Experimental
: A SIMD vector with 16 elements of type `usize`.
usizex32

Experimental
: A SIMD vector with 32 elements of type `usize`.
usizex64

Experimental
: A SIMD vector with 64 elements of type `usize`.

# f64x4 in wide - Rust
URL: https://docs.rs/wide/latest/wide/struct.f64x4.html

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

Source pub f

# Simd in pulp - Rust
URL: https://docs.rs/pulp/0.22.3/pulp/trait.Simd.html

Simd in pulp - Rust

Source 

pub trait Simd: Seal + Debug + Copy + Send + Sync + 'static { 

Show 448 associated items

 type m8s: Debug + Copy + Send + Sync + Zeroable + NoUninit + CheckedBitPattern + 'static; type i8s: Debug + Copy + Send + Sync + Pod + 'static; type u8s: Debug + Copy + Send + Sync + Pod + 'static; type m16s: Debug + Copy + Send + Sync + Zeroable + NoUninit + CheckedBitPattern + 'static; type i16s: Debug + Copy + Send + Sync + Pod + 'static; type u16s: Debug + Copy + Send + Sync + Pod + 'static; type m32s: Debug + Copy + Send + Sync + Zeroable + NoUninit + CheckedBitPattern + 'static; type f32s: Debug + Copy + Send + Sync + Pod + 'static; type c32s: Debug + Copy + Send + Sync + Pod + 'static; type i32s: Debug + Copy + Send + Sync + Pod + 'static; type u32s: Debug + Copy + Send + Sync + Pod + 'static; type m64s: Debug + Copy + Send + Sync + Zeroable + NoUninit + CheckedBitPattern + 'static; type f64s: Debug + Copy + Send + Sync + Pod + 'static; type c64s: Debug + Copy + Send + Sync + Pod + 'static; type i64s: Debug + Copy + Send + Sync + Pod + 'static; type u64s: Debug + Copy + Send + Sync + Pod + 'static; const REGISTER_COUNT: usize; const IS_SCALAR: bool = false; const M64_LANES: usize = _; const U64_LANES: usize = _; const I64_LANES: usize = _; const F64_LANES: usize = _; const C64_LANES: usize = _; const M32_LANES: usize = _; const U32_LANES: usize = _; const I32_LANES: usize = _; const F32_LANES: usize = _; const C32_LANES: usize = _; const M16_LANES: usize = _; const U16_LANES: usize = _; const I16_LANES: usize = _; const M8_LANES: usize = _; const U8_LANES: usize = _; const I8_LANES: usize = _; // Required methods fn abs2_c32s(self, a: Self:: c32s) -> Self:: c32s; fn abs2_c64s(self, a: Self:: c64s) -> Self:: c64s; fn abs_max_c32s(self, a: Self:: c32s) -> Self:: c32s; fn abs_max_c64s(self, a: Self:: c64s) -> Self:: c64s; fn add_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: c32s; fn add_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: c64s; fn add_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s; fn add_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s; fn add_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s; fn add_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s; fn add_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s; fn add_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s; fn sub_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: c32s; fn sub_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: c64s; fn sub_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s; fn sub_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s; fn sub_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s; fn sub_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s; fn sub_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s; fn sub_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s; fn sub_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s; fn sub_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s; fn sub_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s; fn sub_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s; fn mul_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: c32s; fn mul_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: c64s; fn mul_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s; fn mul_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s; fn mul_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s; fn mul_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s; fn mul_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s; fn mul_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s; fn mul_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s; fn mul_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s; fn div_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s; fn div_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s; fn equal_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: m8s; fn equal_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: m16s; fn equal_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: m32s; fn equal_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: m64s; fn equal_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: m32s; fn equal_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: m32s; fn equal_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: m64s; fn equal_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: m64s; fn greater_than_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: m8s; fn greater_than_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: m8s; fn greater_than_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: m16s; fn greater_than_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: m16s; fn greater_than_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: m32s; fn greater_than_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: m32s; fn greater_than_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: m64s; fn greater_than_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: m64s; fn greater_than_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: m32s; fn greater_than_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: m64s; fn greater_than_or_equal_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: m8s; fn greater_than_or_equal_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: m8s; fn greater_than_or_equal_u16s( self, a: Self:: u16s, b: Self:: u16s, ) -> Self:: m16s; fn greater_than_or_equal_i16s( self, a: Self:: i16s, b: Self:: i16s, ) -> Self:: m16s; fn greater_than_or_equal_u32s( self, a: Self:: u32s, b: Self:: u32s, ) -> Self:: m32s; fn greater_than_or_equal_i32s( self, a: Self:: i32s, b: Self:: i32s, ) -> Self:: m32s; fn greater_than_or_equal_u64s( self, a: Self:: u64s, b: Self:: u64s, ) -> Self:: m64s; fn greater_than_or_equal_i64s( self, a: Self:: i64s, b: Self:: i64s, ) -> Self:: m64s; fn greater_than_or_equal_f32s( self, a: Self:: f32s, b: Self:: f32s, ) -> Self:: m32s; fn greater_than_or_equal_f64s( self, a: Self:: f64s, b: Self:: f64s, ) -> Self:: m64s; fn less_than_or_equal_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: m8s; fn less_than_or_equal_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: m8s; fn less_than_or_equal_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: m16s; fn less_than_or_equal_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: m16s; fn less_than_or_equal_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: m32s; fn less_than_or_equal_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: m32s; fn less_than_or_equal_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: m64s; fn less_than_or_equal_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: m64s; fn less_than_or_equal_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: m32s; fn less_than_or_equal_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: m64s; fn less_than_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: m8s; fn less_than_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: m8s; fn less_than_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: m16s; fn less_than_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: m16s; fn less_than_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: m32s; fn less_than_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: m32s; fn less_than_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: m64s; fn less_than_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: m64s; fn less_than_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: m32s; fn less_than_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: m64s; fn and_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s; fn and_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s; fn and_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s; fn and_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s; fn or_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s; fn or_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s; fn or_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s; fn or_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s; fn xor_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s; fn xor_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s; fn xor_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s; fn xor_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s; fn min_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s; fn min_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s; fn min_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s; fn min_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s; fn min_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s; fn min_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s; fn min_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s; fn min_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s; fn min_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s; fn min_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s; fn max_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s; fn max_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s; fn max_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s; fn max_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s; fn max_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s; fn max_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s; fn max_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s; fn max_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s; fn max_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s; fn max_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s; fn neg_c32s(self, a: Self:: c32s) -> Self:: c32s; fn neg_c64s(self, a: Self:: c64s) -> Self:: c64s; fn not_m8s(self, a: Self:: m8s) -> Self:: m8s; fn not_u8s(self, a: Self:: u8s) -> Self:: u8s; fn not_m16s(self, a: Self:: m16s) -> Self:: m16s; fn not_u16s(self, a: Self:: u16s) -> Self:: u16s; fn not_m32s(self, a: Self:: m32s) -> Self:: m32s; fn not_u32s(self, a: Self:: u32s) -> Self:: u32s; fn not_m64s(self, a: Self:: m64s) -> Self:: m64s; fn not_u64s(self, a: Self:: u64s) -> Self:: u64s; fn splat_u8s(self, value: u8) -> Self:: u8s; fn splat_i8s(self, value: i8) -> Self:: i8s; fn splat_u16s(self, value: u16) -> Self:: u16s; fn splat_i16s(self, value: i16) -> Self:: i16s; fn splat_u32s(self, value: u32) -> Self:: u32s; fn splat_i32s(self, value: i32) -> Self:: i32s; fn splat_u64s(self, value: u64) -> Self:: u64s; fn splat_i64s(self, value: i64) -> Self:: i64s; fn splat_c32s(self, value: c32) -> Self:: c32s; fn splat_f32s(self, value: f32) -> Self:: f32s; fn splat_c64s(self, value: c64) -> Self:: c64s; fn splat_f64s(self, value: f64) -> Self:: f64s; fn sqrt_f32s(self, a: Self:: f32s) -> Self:: f32s; fn sqrt_f64s(self, a: Self:: f64s) -> Self:: f64s; fn conj_c32s(self, a: Self:: c32s) -> Self:: c32s; fn conj_c64s(self, a: Self:: c64s) -> Self:: c64s; fn conj_mul_add_c32s( self, a: Self:: c32s, b: Self:: c32s, c: Self:: c32s, ) -> Self:: c32s; fn conj_mul_add_c64s( self, a: Self:: c64s, b: Self:: c64s, c: Self:: c64s, ) -> Self:: c64s; fn conj_mul_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: c32s; fn conj_mul_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: c64s; unsafe fn mask_load_ptr_c32s( self, mask: MemMask, ptr: *const c32, ) -> Self:: c32s; unsafe fn mask_load_ptr_c64s( self, mask: MemMask, ptr: *const c64, ) -> Self:: c64s; unsafe fn mask_load_ptr_u8s( self, mask: MemMask, ptr: *const u8, ) -> Self:: u8s; unsafe fn mask_load_ptr_u16s( self, mask: MemMask, ptr: *const u16, ) -> Self:: u16s; unsafe fn mask_load_ptr_u32s( self, mask: MemMask, ptr: *const u32, ) -> Self:: u32s; unsafe fn mask_load_ptr_u64s( self, mask: MemMask, ptr: *const u64, ) -> Self:: u64s; unsafe fn mask_store_ptr_c32s( self, mask: MemMask, ptr: *mut c32, values: Self:: c32s, ); unsafe fn mask_store_ptr_c64s( self, mask: MemMask, ptr: *mut c64, values: Self:: c64s, ); unsafe fn mask_store_ptr_u8s( self, mask: MemMask, ptr: *mut u8, values: Self:: u8s, ); unsafe fn mask_store_ptr_u16s( self, mask: MemMask, ptr: *mut u16, values: Self:: u16s, ); unsafe fn mask_store_ptr_u32s( self, mask: MemMask, ptr: *mut u32, values: Self:: u32s, ); unsafe fn mask_store_ptr_u64s( self, mask: MemMask, ptr: *mut u64, values: Self:: u64s, ); fn mul_add_c32s( self, a: Self:: c32s, b: Self:: c32s, c: Self:: c32s, ) -> Self:: c32s; fn mul_add_c64s( self, a: Self:: c64s, b: Self:: c64s, c: Self:: c64s, ) -> Self:: c64s; fn mul_add_e_f32s( self, a: Self:: f32s, b: Self:: f32s, c: Self:: f32s, ) -> Self:: f32s; fn mul_add_e_f64s( self, a: Self:: f64s, b: Self:: f64s, c: Self:: f64s, ) -> Self:: f64s; fn mul_add_f32s( self, a: Self:: f32s, b: Self:: f32s, c: Self:: f32s, ) -> Self:: f32s; fn mul_add_f64s( self, a: Self:: f64s, b: Self:: f64s, c: Self:: f64s, ) -> Self:: f64s; fn reduce_max_c32s(self, a: Self:: c32s) -> c32; fn reduce_max_c64s(self, a: Self:: c64s) -> c64; fn reduce_max_f32s(self, a: Self:: f32s) -> f32; fn reduce_max_f64s(self, a: Self:: f64s) -> f64; fn reduce_min_c32s(self, a: Self:: c32s) -> c32; fn reduce_min_c64s(self, a: Self:: c64s) -> c64; fn reduce_min_f32s(self, a: Self:: f32s) -> f32; fn reduce_min_f64s(self, a: Self:: f64s) -> f64; fn reduce_product_f32s(self, a: Self:: f32s) -> f32; fn reduce_product_f64s(self, a: Self:: f64s) -> f64; fn reduce_sum_c32s(self, a: Self:: c32s) -> c32; fn reduce_sum_c64s(self, a: Self:: c64s) -> c64; fn reduce_sum_f32s(self, a: Self:: f32s) -> f32; fn reduce_sum_f64s(self, a: Self:: f64s) -> f64; fn rotate_right_c32s(self, a: Self:: c32s, amount: usize) -> Self:: c32s; fn rotate_right_c64s(self, a: Self:: c64s, amount: usize) -> Self:: c64s; fn rotate_right_u32s(self, a: Self:: u32s, amount: usize) -> Self:: u32s; fn rotate_right_u64s(self, a: Self:: u64s, amount: usize) -> Self:: u64s; fn select_u32s( self, mask: Self:: m32s, if_true: Self:: u32s, if_false: Self:: u32s, ) -> Self:: u32s; fn select_u64s( self, mask: Self:: m64s, if_true: Self:: u64s, if_false: Self:: u64s, ) -> Self:: u64s; fn swap_re_im_c32s(self, a: Self:: c32s) -> Self:: c32s; fn swap_re_im_c64s(self, a: Self:: c64s) -> Self:: c64s; fn vectorize (self, op: Op) -> Op:: Output; fn widening_mul_u32s( self, a: Self:: u32s, b: Self:: u32s, ) -> (Self:: u32s, Self:: u32s); fn wrapping_dyn_shl_u32s( self, a: Self:: u32s, amount: Self:: u32s, ) -> Self:: u32s; fn wrapping_dyn_shr_u32s( self, a: Self:: u32s, amount: Self:: u32s, ) -> Self:: u32s; // Provided methods fn abs_f32s(self, a: Self:: f32s) -> Self:: f32s { ... } fn abs_f64s(self, a: Self:: f64s) -> Self:: f64s { ... } fn and_m8s(self, a: Self:: m8s, b: Self:: m8s) -> Self:: m8s { ... } fn and_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s { ... } fn and_m16s(self, a: Self:: m16s, b: Self:: m16s) -> Self:: m16s { ... } fn and_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s { ... } fn and_m32s(self, a: Self:: m32s, b: Self:: m32s) -> Self:: m32s { ... } fn and_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s { ... } fn and_m64s(self, a: Self:: m64s, b: Self:: m64s) -> Self:: m64s { ... } fn and_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s { ... } fn and_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s { ... } fn and_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s { ... } fn or_m8s(self, a: Self:: m8s, b: Self:: m8s) -> Self:: m8s { ... } fn or_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s { ... } fn or_m16s(self, a: Self:: m16s, b: Self:: m16s) -> Self:: m16s { ... } fn or_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s { ... } fn or_m32s(self, a: Self:: m32s, b: Self:: m32s) -> Self:: m32s { ... } fn or_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s { ... } fn or_m64s(self, a: Self:: m64s, b: Self:: m64s) -> Self:: m64s { ... } fn or_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s { ... } fn or_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s { ... } fn or_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s { ... } fn xor_m8s(self, a: Self:: m8s, b: Self:: m8s) -> Self:: m8s { ... } fn xor_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s { ... } fn xor_m16s(self, a: Self:: m16s, b: Self:: m16s) -> Self:: m16s { ... } fn xor_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s { ... } fn xor_m32s(self, a: Self:: m32s, b: Self:: m32s) -> Self:: m32s { ... } fn xor_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s { ... } fn xor_m64s(self, a: Self:: m64s, b: Self:: m64s) -> Self:: m64s { ... } fn xor_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s { ... } fn xor_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s { ... } fn xor_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s { ... } fn add_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s { ... } fn add_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s { ... } fn add_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s { ... } fn add_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s { ... } fn equal_m8s(self, a: Self:: m8s, b: Self:: m8s) -> Self:: m8s { ... } fn equal_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: m8s { ... } fn equal_m16s(self, a: Self:: m16s, b: Self:: m16s) -> Self:: m16s { ... } fn equal_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: m16s { ... } fn equal_m32s(self, a: Self:: m32s, b: Self:: m32s) -> Self:: m32s { ... } fn equal_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: m32s { ... } fn equal_m64s(self, a: Self:: m64s, b: Self:: m64s) -> Self:: m64s { ... } fn equal_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: m64s { ... } fn not_i8s(self, a: Self:: i8s) -> Self:: i8s { ... } fn not_i16s(self, a: Self:: i16s) -> Self:: i16s { ... } fn not_i32s(self, a: Self:: i32s) -> Self:: i32s { ... } fn not_i64s(self, a: Self:: i64s) -> Self:: i64s { ... } fn not_f32s(self, a: Self:: f32s) -> Self:: f32s { ... } fn not_f64s(self, a: Self:: f64s) -> Self:: f64s { ... } fn as_mut_rsimd_u8s(slice: &mut [u8]) -> (&mut [u8], &mut [Self:: u8s]) { ... } fn as_rsimd_u8s(slice: &[u8]) -> (&[u8], &[Self:: u8s]) { ... } fn as_mut_simd_u8s(slice: &mut [u8]) -> (&mut [Self:: u8s], &mut [u8]) { ... } fn as_simd_u8s(slice: &[u8]) -> (&[Self:: u8s], &[u8]) { ... } fn as_uninit_mut_rsimd_u8s( slice: &mut [MaybeUninit< u8>], ) -> (&mut [MaybeUninit< u8>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_u8s( slice: &mut [MaybeUninit< u8>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< u8>]) { ... } fn as_mut_rsimd_i8s(slice: &mut [i8]) -> (&mut [i8], &mut [Self:: i8s]) { ... } fn as_rsimd_i8s(slice: &[i8]) -> (&[i8], &[Self:: i8s]) { ... } fn as_mut_simd_i8s(slice: &mut [i8]) -> (&mut [Self:: i8s], &mut [i8]) { ... } fn as_simd_i8s(slice: &[i8]) -> (&[Self:: i8s], &[i8]) { ... } fn as_uninit_mut_rsimd_i8s( slice: &mut [MaybeUninit< i8>], ) -> (&mut [MaybeUninit< i8>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_i8s( slice: &mut [MaybeUninit< i8>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< i8>]) { ... } fn as_mut_rsimd_u16s(slice: &mut [u16]) -> (&mut [u16], &mut [Self:: u16s]) { ... } fn as_rsimd_u16s(slice: &[u16]) -> (&[u16], &[Self:: u16s]) { ... } fn as_mut_simd_u16s(slice: &mut [u16]) -> (&mut [Self:: u16s], &mut [u16]) { ... } fn as_simd_u16s(slice: &[u16]) -> (&[Self:: u16s], &[u16]) { ... } fn as_uninit_mut_rsimd_u16s( slice: &mut [MaybeUninit< u16>], ) -> (&mut [MaybeUninit< u16>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_u16s( slice: &mut [MaybeUninit< u16>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< u16>]) { ... } fn as_mut_rsimd_i16s(slice: &mut [i16]) -> (&mut [i16], &mut [Self:: i16s]) { ... } fn as_rsimd_i16s(slice: &[i16]) -> (&[i16], &[Self:: i16s]) { ... } fn as_mut_simd_i16s(slice: &mut [i16]) -> (&mut [Self:: i16s], &mut [i16]) { ... } fn as_simd_i16s(slice: &[i16]) -> (&[Self:: i16s], &[i16]) { ... } fn as_uninit_mut_rsimd_i16s( slice: &mut [MaybeUninit< i16>], ) -> (&mut [MaybeUninit< i16>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_i16s( slice: &mut [MaybeUninit< i16>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< i16>]) { ... } fn as_mut_rsimd_u32s(slice: &mut [u32]) -> (&mut [u32], &mut [Self:: u32s]) { ... } fn as_rsimd_u32s(slice: &[u32]) -> (&[u32], &[Self:: u32s]) { ... } fn as_mut_simd_u32s(slice: &mut [u32]) -> (&mut [Self:: u32s], &mut [u32]) { ... } fn as_simd_u32s(slice: &[u32]) -> (&[Self:: u32s], &[u32]) { ... } fn as_uninit_mut_rsimd_u32s( slice: &mut [MaybeUninit< u32>], ) -> (&mut [MaybeUninit< u32>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_u32s( slice: &mut [MaybeUninit< u32>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< u32>]) { ... } fn as_mut_rsimd_i32s(slice: &mut [i32]) -> (&mut [i32], &mut [Self:: i32s]) { ... } fn as_rsimd_i32s(slice: &[i32]) -> (&[i32], &[Self:: i32s]) { ... } fn as_mut_simd_i32s(slice: &mut [i32]) -> (&mut [Self:: i32s], &mut [i32]) { ... } fn as_simd_i32s(slice: &[i32]) -> (&[Self:: i32s], &[i32]) { ... } fn as_uninit_mut_rsimd_i32s( slice: &mut [MaybeUninit< i32>], ) -> (&mut [MaybeUninit< i32>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_i32s( slice: &mut [MaybeUninit< i32>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< i32>]) { ... } fn as_mut_rsimd_u64s(slice: &mut [u64]) -> (&mut [u64], &mut [Self:: u64s]) { ... } fn as_rsimd_u64s(slice: &[u64]) -> (&[u64], &[Self:: u64s]) { ... } fn as_mut_simd_u64s(slice: &mut [u64]) -> (&mut [Self:: u64s], &mut [u64]) { ... } fn as_simd_u64s(slice: &[u64]) -> (&[Self:: u64s], &[u64]) { ... } fn as_uninit_mut_rsimd_u64s( slice: &mut [MaybeUninit< u64>], ) -> (&mut [MaybeUninit< u64>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_u64s( slice: &mut [MaybeUninit< u64>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< u64>]) { ... } fn as_mut_rsimd_i64s(slice: &mut [i64]) -> (&mut [i64], &mut [Self:: i64s]) { ... } fn as_rsimd_i64s(slice: &[i64]) -> (&[i64], &[Self:: i64s]) { ... } fn as_mut_simd_i64s(slice: &mut [i64]) -> (&mut [Self:: i64s], &mut [i64]) { ... } fn as_simd_i64s(slice: &[i64]) -> (&[Self:: i64s], &[i64]) { ... } fn as_uninit_mut_rsimd_i64s( slice: &mut [MaybeUninit< i64>], ) -> (&mut [MaybeUninit< i64>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_i64s( slice: &mut [MaybeUninit< i64>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< i64>]) { ... } fn as_mut_rsimd_c32s(slice: &mut [c32]) -> (&mut [c32], &mut [Self:: c32s]) { ... } fn as_rsimd_c32s(slice: &[c32]) -> (&[c32], &[Self:: c32s]) { ... } fn as_mut_simd_c32s(slice: &mut [c32]) -> (&mut [Self:: c32s], &mut [c32]) { ... } fn as_simd_c32s(slice: &[c32]) -> (&[Self:: c32s], &[c32]) { ... } fn as_uninit_mut_rsimd_c32s( slice: &mut [MaybeUninit< c32>], ) -> (&mut [MaybeUninit< c32>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_c32s( slice: &mut [MaybeUninit< c32>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< c32>]) { ... } fn as_mut_rsimd_f32s(slice: &mut [f32]) -> (&mut [f32], &mut [Self:: f32s]) { ... } fn as_rsimd_f32s(slice: &[f32]) -> (&[f32], &[Self:: f32s]) { ... } fn as_mut_simd_f32s(slice: &mut [f32]) -> (&mut [Self:: f32s], &mut [f32]) { ... } fn as_simd_f32s(slice: &[f32]) -> (&[Self:: f32s], &[f32]) { ... } fn as_uninit_mut_rsimd_f32s( slice: &mut [MaybeUninit< f32>], ) -> (&mut [MaybeUninit< f32>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_f32s( slice: &mut [MaybeUninit< f32>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< f32>]) { ... } fn as_mut_rsimd_c64s(slice: &mut [c64]) -> (&mut [c64], &mut [Self:: c64s]) { ... } fn as_rsimd_c64s(slice: &[c64]) -> (&[c64], &[Self:: c64s]) { ... } fn as_mut_simd_c64s(slice: &mut [c64]) -> (&mut [Self:: c64s], &mut [c64]) { ... } fn as_simd_c64s(slice: &[c64]) -> (&[Self:: c64s], &[c64]) { ... } fn as_uninit_mut_rsimd_c64s( slice: &mut [MaybeUninit< c64>], ) -> (&mut [MaybeUninit< c64>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_c64s( slice: &mut [MaybeUninit< c64>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< c64>]) { ... } fn as_mut_rsimd_f64s(slice: &mut [f64]) -> (&mut [f64], &mut [Self:: f64s]) { ... } fn as_rsimd_f64s(slice: &[f64]) -> (&[f64], &[Self:: f64s]) { ... } fn as_mut_simd_f64s(slice: &mut [f64]) -> (&mut [Self:: f64s], &mut [f64]) { ... } fn as_simd_f64s(slice: &[f64]) -> (&[Self:: f64s], &[f64]) { ... } fn as_uninit_mut_rsimd_f64s( slice: &mut [MaybeUninit< f64>], ) -> (&mut [MaybeUninit< f64>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_f64s( slice: &mut [MaybeUninit< f64>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< f64>]) { ... } fn conj_mul_add_e_c32s( self, a: Self:: c32s, b: Self:: c32s, c: Self:: c32s, ) -> Self:: c32s { ... } fn conj_mul_add_e_c64s( self, a: Self:: c64s, b: Self:: c64s, c: Self:: c64s, ) -> Self:: c64s { ... } fn conj_mul_e_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: c32s { ... } fn conj_mul_e_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: c64s { ... } fn deinterleave_shfl_f32s (self, values: T) -> T { ... } fn deinterleave_shfl_f64s (self, values: T) -> T { ... } fn first_true_m8s(self, mask: Self:: m8s) -> usize { ... } fn first_true_m16s(self, mask: Self:: m16s) -> usize { ... } fn first_true_m32s(self, mask: Self:: m32s) -> usize { ... } fn first_true_m64s(self, mask: Self:: m64s) -> usize { ... } fn interleave_shfl_f32s (self, values: T) -> T { ... } fn interleave_shfl_f64s (self, values: T) -> T { ... } fn mask_between_m8s(self, start: u8, end: u8) -> MemMask { ... } fn mask_between_m16s(self, start: u16, end: u16) -> MemMask { ... } fn mask_between_m32s(self, start: u32, end: u32) -> MemMask { ... } fn mask_between_m64s(self, start: u64, end: u64) -> MemMask { ... } unsafe fn mask_load_ptr_f32s( self, mask: MemMask, ptr: *const f32, ) -> Self:: f32s { ... } unsafe fn mask_load_ptr_f64s( self, mask: MemMask, ptr: *const f64, ) -> Self:: f64s { ... } unsafe fn mask_load_ptr_i8s( self, mask: MemMask, ptr: *const i8, ) -> Self:: i8s { ... } unsafe fn mask_load_ptr_i16s( self, mask: MemMask, ptr: *const i16, ) -> Self:: i16s { ... } unsafe fn mask_load_ptr_i32s( self, mask: MemMask, ptr: *const i32, ) -> Self:: i32s { ... } unsafe fn mask_load_ptr_i64s( self, mask: MemMask, ptr: *const i64, ) -> Self:: i64s { ... } unsafe fn mask_store_ptr_f32s( self, mask: MemMask, ptr: *mut f32, values: Self:: f32s, ) { ... } unsafe fn mask_store_ptr_f64s( self, mask: MemMask, ptr: *mut f64, values: Self:: f64s, ) { ... } unsafe fn mask_store_ptr_i8s( self, mask: MemMask, ptr: *mut i8, values: Self:: i8s, ) { ... } unsafe fn mask_store_ptr_i16s( self, mask: MemMask, ptr: *mut i16, values: Self:: i16s, ) { ... } unsafe fn mask_store_ptr_i32s( self, mask: MemMask, ptr: *mut i32, values: Self:: i32s, ) { ... } unsafe fn mask_store_ptr_i64s( self, mask: MemMask, ptr: *mut i64, values: Self:: i64s, ) { ... } fn mul_add_e_c32s( self, a: Self:: c32s, b: Self:: c32s, c: Self:: c32s, ) -> Self:: c32s { ... } fn mul_add_e_c64s( self, a: Self:: c64s, b: Self:: c64s, c: Self:: c64s, ) -> Self:: c64s { ... } fn negate_mul_add_e_f32s( self, a: Self:: f32s, b: Self:: f32s, c: Self:: f32s, ) -> Self:: f32s { ... } fn negate_mul_add_e_f64s( self, a: Self:: f64s, b: Self:: f64s, c: Self:: f64s, ) -> Self:: f64s { ... } fn negate_mul_add_f32s( self, a: Self:: f32s, b: Self:: f32s, c: Self:: f32s, ) -> Self:: f32s { ... } fn negate_mul_add_f64s( self, a: Self:: f64s, b: Self:: f64s, c: Self:: f64s, ) -> Self:: f64s { ... } fn mul_e_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: c32s { ... } fn mul_e_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: c64s { ... } fn neg_f32s(self, a: Self:: f32s) -> Self:: f32s { ... } fn neg_f64s(self, a: Self:: f64s) -> Self:: f64s { ... } fn partial_load_c32s(self, slice: &[c32]) -> Self:: c32s { ... } fn partial_load_c64s(self, slice: &[c64]) -> Self:: c64s { ... } fn partial_load_f32s(self, slice: &[f32]) -> Self:: f32s { ... } fn partial_load_f64s(self, slice: &[f64]) -> Self:: f64s { ... } fn partial_load_i8s(self, slice: &[i8]) -> Self:: i8s { ... } fn partial_load_i16s(self, slice: &[i16]) -> Self:: i16s { ... } fn partial_load_i32s(self, slice: &[i32]) -> Self:: i32s { ... } fn partial_load_i64s(self, slice: &[i64]) -> Self:: i64s { ... } fn partial_load_u8s(self, slice: &[u8]) -> Self:: u8s { ... } fn partial_load_u16s(self, slice: &[u16]) -> Self:: u16s { ... } fn partial_load_u32s(self, slice: &[u32]) -> Self:: u32s { ... } fn partial_load_u64s(self, slice: &[u64]) -> Self:: u64s { ... } fn partial_store_c32s(self, slice: &mut [c32], values: Self:: c32s) { ... } fn partial_store_c64s(self, slice: &mut [c64], values: Self:: c64s) { ... } fn partial_store_f32s(self, slice: &mut [f32], values: Self:: f32s) { ... } fn partial_store_f64s(self, slice: &mut [f64], values: Self:: f64s) { ... } fn partial_store_i8s(self, slice: &mut [i8], values: Self:: i8s) { ... } fn partial_store_i16s(self, slice: &mut [i16], values: Self:: i16s) { ... } fn partial_store_i32s(self, slice: &mut [i32], values: Self:: i32s) { ... } fn partial_store_i64s(self, slice: &mut [i64], values: Self:: i64s) { ... } fn partial_store_u8s(self, slice: &mut [u8], values: Self:: u8s) { ... } fn partial_store_u16s(self, slice: &mut [u16], values: Self:: u16s) { ... } fn partial_store_u32s(self, slice: &mut [u32], values: Self:: u32s) { ... } fn partial_store_u64s(self, slice: &mut [u64], values: Self:: u64s) { ... } fn rotate_left_c32s(self, a: Self:: c32s, amount: usize) -> Self:: c32s { ... } fn rotate_left_c64s(self, a: Self:: c64s, amount: usize) -> Self:: c64s { ... } fn rotate_left_f32s(self, a: Self:: f32s, amount: usize) -> Self:: f32s { ... } fn rotate_left_f64s(self, a: Self:: f64s, amount: usize) -> Self:: f64s { ... } fn rotate_left_i32s(self, a: Self:: i32s, amount: usize) -> Self:: i32s { ... } fn rotate_left_i64s(self, a: Self:: i64s, amount: usize) -> Self:: i64s { ... } fn rotate_left_u32s(self, a: Self:: u32s, amount: usize) -> Self:: u32s { ... } fn rotate_left_u64s(self, a: Self:: u64s, amount: usize) -> Self:: u64s { ... } fn rotate_right_f32s(self, a: Sel

# ParallelIterator in rayon::iter - Rust
URL: https://docs.rs/rayon/1.12.0/rayon/iter/trait.ParallelIterator.html

ParallelIterator in rayon::iter - Rust

Source 

pub trait ParallelIterator: Sized + Send { type Item: Send; 

Show 59 methods

 // Required method fn drive_unindexed (self, consumer: C) -> C:: Result where C: UnindexedConsumer; // Provided methods fn for_each (self, op: OP) where OP: Fn(Self:: Item) + Sync + Send { ... } fn for_each_with<OP, T>(self, init: T, op: OP) where OP: Fn(&mut T, Self:: Item) + Sync + Send, T: Send + Clone { ... } fn for_each_init<OP, INIT, T>(self, init: INIT, op: OP) where OP: Fn(&mut T, Self:: Item) + Sync + Send, INIT: Fn() -> T + Sync + Send { ... } fn try_for_each<OP, R>(self, op: OP) -> R where OP: Fn(Self:: Item) -> R + Sync + Send, R: Try + Send { ... } fn try_for_each_with<OP, T, R>(self, init: T, op: OP) -> R where OP: Fn(&mut T, Self:: Item) -> R + Sync + Send, T: Send + Clone, R: Try + Send { ... } fn try_for_each_init<OP, INIT, T, R>(self, init: INIT, op: OP) -> R where OP: Fn(&mut T, Self:: Item) -> R + Sync + Send, INIT: Fn() -> T + Sync + Send, R: Try + Send { ... } fn count(self) -> usize { ... } fn map<F, R>(self, map_op: F) -> Map<Self, F> where F: Fn(Self:: Item) -> R + Sync + Send, R: Send { ... } fn map_with<F, T, R>(self, init: T, map_op: F) -> MapWith<Self, T, F> where F: Fn(&mut T, Self:: Item) -> R + Sync + Send, T: Send + Clone, R: Send { ... } fn map_init<F, INIT, T, R>( self, init: INIT, map_op: F, ) -> MapInit<Self, INIT, F> where F: Fn(&mut T, Self:: Item) -> R + Sync + Send, INIT: Fn() -> T + Sync + Send, R: Send { ... } fn cloned<'a, T>(self) -> Cloned where T: 'a + Clone + Send, Self: ParallelIterator (self) -> Copied where T: 'a + Copy + Send, Self: ParallelIterator ```
use rayon::prelude::*;

(0..100).into_par_iter().for_each(|x| println!("{:?}", x));
``````
use std::sync::mpsc::channel;
use rayon::prelude::*;

let (sender, receiver) = channel();

(0..5).into_par_iter().for_each_with(sender, |s, x| s.send(x).unwrap());

let mut res: Vec<_> = receiver.iter().collect();

res.sort();

assert_eq!(&res[..], &[0, 1, 2, 3, 4])
``````
use rand::Rng;
use rayon::prelude::*;

let mut v = vec![0u8; 1_000_000];

v.par_chunks_mut(1000)
    .for_each_init(
        || rand::rng(),
        |rng, chunk| rng.fill(chunk),
    );

// There's a remote chance that this will fail...
for i in 0u8..=255 {
    assert!(v.contains(&i));
}
``````
use rayon::prelude::*;
use std::io::{self, Write};

// This will stop iteration early if there's any write error, like
// having piped output get closed on the other end.
(0..100).into_par_iter()
    .try_for_each(|x| writeln!(io::stdout(), "{:?}", x))
    .expect("expected no write errors");
``````
use std::sync::mpsc::channel;
use rayon::prelude::*;

let (sender, receiver) = channel();

(0..5).into_par_iter()
    .try_for_each_with(sender, |s, x| s.send(x))
    .expect("expected no send errors");

let mut res: Vec<_> = receiver.iter().collect();

res.sort();

assert_eq!(&res[..], &[0, 1, 2, 3, 4])
``````
use rand::{Rng, TryRngCore};
use rayon::prelude::*;

let mut v = vec![0u8; 1_000_000];

v.par_chunks_mut(1000)
    .try_for_each_init(
        || rand::rng(),
        |rng, chunk| rng.try_fill_bytes(chunk),
    )
    .expect("expected no rand errors");

// There's a remote chance that this will fail...
for i in 0u8..=255 {
    assert!(v.contains(&i));
}
``````
use rayon::prelude::*;

let count = (0..100).into_par_iter().count();

assert_eq!(count, 100);
``````
use rayon::prelude::*;

let mut par_iter = (0..5).into_par_iter().map(|x| x * 2);

let doubles: Vec<_> = par_iter.collect();

assert_eq!(&doubles[..], &[0, 2, 4, 6, 8]);
``````
use std::sync::mpsc::channel;
use rayon::prelude::*;

let (sender, receiver) = channel();

let a: Vec<_> = (0..5)
                .into_par_iter()            // iterating over i32
                .map_with(sender, |s, x| {
                    s.send(x).unwrap();     // sending i32 values through the channel
                    x                       // returning i32
                })
                .collect();                 // collecting the returned values into a vector

let mut b: Vec<_> = receiver.iter()         // iterating over the values in the channel
                            .collect();     // and collecting them
b.sort();

assert_eq!(a, b);
``````
use rand::Rng;
use rayon::prelude::*;

let a: Vec<_> = (1i32..1_000_000)
    .into_par_iter()
    .map_init(
        || rand::rng(),  // get the thread-local RNG
        |rng, x| if rng.random() { // randomly negate items
            -x
        } else {
            x
        },
    ).collect();

// There's a remote chance that this will fail...
assert!(a.iter().any(|&x| x < 0));
assert!(a.iter().any(|&x| x > 0));
```(self) -> Cloned where T: 'a + Clone + Send, Self: ParallelIterator ```
use rayon::prelude::*;

let a = [1, 2, 3];

let v_cloned: Vec<_> = a.par_iter().cloned().collect();

// cloned is the same as .map(|&x| x), for integers
let v_map: Vec<_> = a.par_iter().map(|&x| x).collect();

assert_eq!(v_cloned, vec![1, 2, 3]);
assert_eq!(v_map, vec![1, 2, 3]);
```(self) -> Copied where T: 'a + Copy + Send, Self: ParallelIterator ```
use rayon::prelude::*;

let a = [1, 2, 3];

let v_copied: Vec<_> = a.par_iter().copied().collect();

// copied is the same as .map(|&x| x), for integers
let v_map: Vec<_> = a.par_iter().map(|&x| x).collect();

assert_eq!(v_copied, vec![1, 2, 3]);
assert_eq!(v_map, vec![1, 2, 3]);
``````
use rayon::prelude::*;

let a = [1, 4, 2, 3];

// this iterator sequence is complex.
let sum = a.par_iter()
            .cloned()
            .filter(|&x| x % 2 == 0)
            .reduce(|| 0, |sum, i| sum + i);

println!("{}", sum);

// let's add some inspect() calls to investigate what's happening
let sum = a.par_iter()
            .cloned()
            .inspect(|x| println!("about to filter: {}", x))
            .filter(|&x| x % 2 == 0)
            .inspect(|x| println!("made it through filter: {}", x))
            .reduce(|| 0, |sum, i| sum + i);

println!("{}", sum);
``````
use rayon::prelude::*;

let par_iter = (0..5).into_par_iter().update(|x| {*x *= 2;});

let doubles: Vec<_> = par_iter.collect();

assert_eq!(&doubles[..], &[0, 2, 4, 6, 8]);
``````
use rayon::prelude::*;

let mut par_iter = (0..10).into_par_iter().filter(|x| x % 2 == 0);

let even_numbers: Vec<_> = par_iter.collect();

assert_eq!(&even_numbers[..], &[0, 2, 4, 6, 8]);
``````
use rayon::prelude::*;

let mut par_iter = (0..10).into_par_iter()
                        .filter_map(|x| {
                            if x % 2 == 0 { Some(x * 3) }
                            else { None }
                        });

let even_numbers: Vec<_> = par_iter.collect();

assert_eq!(&even_numbers[..], &[0, 6, 12, 18, 24]);
``````
use rayon::prelude::*;

let a = [[1, 2], [3, 4], [5, 6], [7, 8]];

let par_iter = a.par_iter().cloned().flat_map(|a| a.to_vec());

let vec: Vec<_> = par_iter.collect();

assert_eq!(&vec[..], &[1, 2, 3, 4, 5, 6, 7, 8]);
``````
use rayon::prelude::*;
use std::cell::RefCell;

let a = [[1, 2], [3, 4], [5, 6], [7, 8]];

let par_iter = a.par_iter().flat_map_iter(|a| {
    // The serial iterator doesn't have to be thread-safe, just its items.
    let cell_iter = RefCell::new(a.iter().cloned());
    std::iter::from_fn(move || cell_iter.borrow_mut().next())
});

let vec: Vec<_> = par_iter.collect();

assert_eq!(&vec[..], &[1, 2, 3, 4, 5, 6, 7, 8]);
``````
use rayon::prelude::*;

let x: Vec<Vec<_>> = vec![vec![1, 2], vec![3, 4]];
let y: Vec<_> = x.into_par_iter().flatten().collect();

assert_eq!(y, vec![1, 2, 3, 4]);
``````
use rayon::prelude::*;

let x: Vec<Vec<_>> = vec![vec![1, 2], vec![3, 4]];
let iters: Vec<_> = x.into_iter().map(Vec::into_iter).collect();
let y: Vec<_> = iters.into_par_iter().flatten_iter().collect();

assert_eq!(y, vec![1, 2, 3, 4]);
``````
// Iterate over a sequence of pairs `(x0, y0), ..., (xN, yN)`
// and use reduce to compute one pair `(x0 + ... + xN, y0 + ... + yN)`
// where the first/second elements are summed separately.
use rayon::prelude::*;
let sums = [(0, 1), (5, 6), (16, 2), (8, 9)]
           .par_iter()        // iterating over &(i32, i32)
           .cloned()          // iterating over (i32, i32)
           .reduce(|| (0, 0), // the "identity" is 0 in both columns
                   |a, b| (a.0 + b.0, a.1 + b.1));
assert_eq!(sums, (0 + 5 + 16 + 8, 1 + 6 + 2 + 9));
``````
use rayon::prelude::*;
let sums = [(0, 1), (5, 6), (16, 2), (8, 9)]
           .par_iter()        // iterating over &(i32, i32)
           .cloned()          // iterating over (i32, i32)
           .reduce_with(|a, b| (a.0 + b.0, a.1 + b.1))
           .unwrap();
assert_eq!(sums, (0 + 5 + 16 + 8, 1 + 6 + 2 + 9));
``````
use rayon::prelude::*;

// Compute the sum of squares, being careful about overflow.
fn sum_squares<I: IntoParallelIterator<Item = i32>>(iter: I) -> Option<i32> {
    iter.into_par_iter()
        .map(|i| i.checked_mul(i))            // square each item,
        .try_reduce(|| 0, i32::checked_add)   // and add them up!
}
assert_eq!(sum_squares(0..5), Some(0 + 1 + 4 + 9 + 16));

// The sum might overflow
assert_eq!(sum_squares(0..10_000), None);

// Or the squares might overflow before it even reaches `try_reduce`
assert_eq!(sum_squares(1_000_000..1_000_001), None);
``````
use rayon::prelude::*;

let files = ["/dev/null", "/does/not/exist"];

// Find the biggest file
files.into_par_iter()
    .map(|path| std::fs::metadata(path).map(|m| (path, m.len())))
    .try_reduce_with(|a, b| {
        Ok(if a.1 >= b.1 { a } else { b })
    })
    .expect("Some value, since the iterator is not empty")
    .expect_err("not found");
``````notrust
22 3 77 89 46
      |     |
    102   135
``````notrust
22 3 77 89 46
      |  |  |
    102 89 46
``````
use rayon::prelude::*;

let s =
    ['a', 'b', 'c', 'd', 'e']
    .par_iter()
    .map(|c: &char| format!("{}", c))
    .reduce(|| String::new(),
            |mut a: String, b: String| { a.push_str(&b); a });

assert_eq!(s, "abcde");
``````
use rayon::prelude::*;

let s =
    ['a', 'b', 'c', 'd', 'e']
    .par_iter()
    .fold(|| String::new(),
            |mut s: String, c: &char| { s.push(*c); s })
    .reduce(|| String::new(),
            |mut a: String, b: String| { a.push_str(&b); a });

assert_eq!(s, "abcde");
``````
use rayon::prelude::*;

let bytes = 0..22_u8;
let sum = bytes.into_par_iter()
               .fold(|| 0_u32, |a: u32, b: u8| a + (b as u32))
               .sum::<u32>();

assert_eq!(sum, (0..22).sum()); // compare to sequential
``````
use rayon::prelude::*;

let bytes = 0..22_u8;
let sum = bytes.into_par_iter()
               .fold_with(0_u32, |a: u32, b: u8| a + (b as u32))
               .sum::<u32>();

assert_eq!(sum, (0..22).sum()); // compare to sequential
``````
use rayon::prelude::*;

let bytes = 0..22_u8;
let sum = bytes.into_par_iter()
               .try_fold(|| 0_u32, |a: u32, b: u8| a.checked_add(b as u32))
               .try_reduce(|| 0, u32::checked_add);

assert_eq!(sum, Some((0..22).sum())); // compare to sequential
``````
use rayon::prelude::*;

let bytes = 0..22_u8;
let sum = bytes.into_par_iter()
               .try_fold_with(0_u32, |a: u32, b: u8| a.checked_add(b as u32))
               .try_reduce(|| 0, u32::checked_add);

assert_eq!(sum, Some((0..22).sum())); // compare to sequential
``````
use rayon::prelude::*;

let a = [1, 5, 7];

let sum: i32 = a.par_iter().sum();

assert_eq!(sum, 13);
``````
use rayon::prelude::*;

fn factorial(n: u32) -> u32 {
   (1..n+1).into_par_iter().product()
}

assert_eq!(factorial(0), 1);
assert_eq!(factorial(1), 1);
assert_eq!(factorial(5), 120);
``````
use rayon::prelude::*;

let a = [45, 74, 32];

assert_eq!(a.par_iter().min(), Some(&32));

let b: [i32; 0] = [];

assert_eq!(b.par_iter().min(), None);
``````
use rayon::prelude::*;

let a = [-3_i32, 77, 53, 240, -1];

assert_eq!(a.par_iter().min_by(|x, y| x.cmp(y)), Some(&-3));
``````
use rayon::prelude::*;

let a = [-3_i32, 34, 2, 5, -10, -3, -23];

assert_eq!(a.par_iter().min_by_key(|x| x.abs()), Some(&2));
``````
use rayon::prelude::*;

let a = [45, 74, 32];

assert_eq!(a.par_iter().max(), Some(&74));

let b: [i32; 0] = [];

assert_eq!(b.par_iter().max(), None);
``````
use rayon::prelude::*;

let a = [-3_i32, 77, 53, 240, -1];

assert_eq!(a.par_iter().max_by(|x, y| x.abs().cmp(&y.abs())), Some(&240));
``````
use rayon::prelude::*;

let a = [-3_i32, 34, 2, 5, -10, -3, -23];

assert_eq!(a.par_iter().max_by_key(|x| x.abs()), Some(&34));
``````
use rayon::prelude::*;

let a = [0, 1, 2];
let b = [9, 8, 7];

let par_iter = a.par_iter().chain(b.par_iter());

let chained: Vec<_> = par_iter.cloned().collect();

assert_eq!(&chained[..], &[0, 1, 2, 9, 8, 7]);
``````
use rayon::prelude::*;

let a = [1, 2, 3, 3];

assert_eq!(a.par_iter().find_any(|&&x| x == 3), Some(&3));

assert_eq!(a.par_iter().find_any(|&&x| x == 100), None);
``````
use rayon::prelude::*;

let a = [1, 2, 3, 3];

assert_eq!(a.par_iter().find_first(|&&x| x == 3), Some(&3));

assert_eq!(a.par_iter().find_first(|&&x| x == 100), None);
``````
use rayon::prelude::*;

let a = [1, 2, 3, 3];

assert_eq!(a.par_iter().find_last(|&&x| x == 3), Some(&3));

assert_eq!(a.par_iter().find_last(|&&x| x == 100), None);
``````
use rayon::prelude::*;

let c = ["lol", "NaN", "5", "5"];

let found_number = c.par_iter().find_map_any(|s| s.parse().ok());

assert_eq!(found_number, Some(5));
``````
use rayon::prelude::*;

let c = ["lol", "NaN", "2", "5"];

let first_number = c.par_iter().find_map_first(|s| s.parse().ok());

assert_eq!(first_number, Some(2));
``````
use rayon::prelude::*;

let c = ["lol", "NaN", "2", "5"];

let last_number = c.par_iter().find_map_last(|s| s.parse().ok());

assert_eq!(last_number, Some(5));
``````
use rayon::prelude::*;

let a = [0, 12, 3, 4, 0, 23, 0];

let is_valid = a.par_iter().any(|&x| x > 10);

assert!(is_valid);
``````
use rayon::prelude::*;

let a = [0, 12, 3, 4, 0, 23, 0];

let is_valid = a.par_iter().all(|&x| x > 10);

assert!(!is_valid);
``````
use rayon::prelude::*;
use std::sync::atomic::{AtomicUsize, Ordering};

let counter = AtomicUsize::new(0);
let value = (0_i32..2048)
    .into_par_iter()
    .map(|x| {
             counter.fetch_add(1, Ordering::SeqCst);
             if x < 1024 { Some(x) } else { None }
         })
    .while_some()
    .max();

assert!(value < Some(1024));
assert!(counter.load(Ordering::SeqCst) < 2048); // should not have visited every single one
``````
use rayon::prelude::*;
use std::{thread, time};

(0..1_000_000)
    .into_par_iter()
    .panic_fuse()
    .for_each(|i| {
        // simulate some work
        thread::sleep(time::Duration::from_secs(1));
        assert!(i > 0); // oops!
    });
``````
use rayon::prelude::*;

let sync_vec: Vec<_> = (0..100).into_iter().collect();

let async_vec: Vec<_> = (0..100).into_par_iter().collect();

assert_eq!(sync_vec, async_vec);
``````
use rayon::prelude::*;

let a = [(0, 1), (1, 2), (2, 3), (3, 4)];
let (first, second): (Vec<_>, Vec<_>) = a.into_par_iter().collect();

assert_eq!(first, [0, 1, 2, 3]);
assert_eq!(second, [1, 2, 3, 4]);
``````
use rayon::prelude::*;
use rayon::iter::Either;

let (left, right): (Vec<_>, Vec<_>) = (0..8).into_par_iter().map(|x| {
    if x % 2 == 0 {
        Either::Left(x * 4)
    } else {
        Either::Right(x * 3)
    }
}).collect();

assert_eq!(left, [0, 8, 16, 24]);
assert_eq!(right, [3, 9, 15, 21]);
``````
use rayon::prelude::*;
use rayon::iter::Either;

let (first, (left, right)): (Vec<_>, (Vec<_>, Vec<_>))
    = (0..8).into_par_iter().map(|x| {
        if x % 2 == 0 {
            (x, Either::Left(x * 4))
        } else {
            (-x, Either::Right(x * 3))
        }
    }).collect();

assert_eq!(first, [0, -1, 2, -3, 4, -5, 6, -7]);
assert_eq!(left, [0, 8, 16, 24]);
assert_eq!(right, [3, 9, 15, 21]);
``````
use rayon::prelude::*;
use rayon::iter::Either;

let result: Result<(Vec<_>, (Vec<_>, Vec<_>)), _>
    = (0..8).into_par_iter().map(|x| {
        if x > 5 {
            Err(x)
        } else if x % 2 == 0 {
            Ok((x, Either::Left(x * 4)))
        } else {
            Ok((-x, Either::Right(x * 3)))
        }
    }).collect();

let error = result.unwrap_err();
assert!(error == 6 || error == 7);
``````
use rayon::prelude::*;

let a = [(0, 1), (1, 2), (2, 3), (3, 4)];

let (left, right): (Vec<_>, Vec<_>) = a.par_iter().cloned().unzip();

assert_eq!(left, [0, 1, 2, 3]);
assert_eq!(right, [1, 2, 3, 4]);
``````
use rayon::prelude::*;

let (values, (squares, cubes)): (Vec<_>, (Vec<_>, Vec<_>)) = (0..4).into_par_iter()
    .map(|i| (i, (i * i, i * i * i)))
    .unzip();

assert_eq!(values, [0, 1, 2, 3]);
assert_eq!(squares, [0, 1, 4, 9]);
assert_eq!(cubes, [0, 1, 8, 27]);
``````
use rayon::prelude::*;

let (left, right): (Vec<_>, Vec<_>) = (0..8).into_par_iter().partition(|x| x % 2 == 0);

assert_eq!(left, [0, 2, 4, 6]);
assert_eq!(right, [1, 3, 5, 7]);
``````
use rayon::prelude::*;
use rayon::iter::Either;

let (left, right): (Vec<_>, Vec<_>) = (0..8).into_par_iter()
    .partition_map(|x| {
        if x % 2 == 0 {
            Either::Left(x * 4)
        } else {
            Either::Right(x * 3)
        }
    });

assert_eq!(left, [0, 8, 16, 24]);
assert_eq!(right, [3, 9, 15, 21]);
``````
use rayon::prelude::*;
use rayon::iter::Either::*;

let ((fizzbuzz, fizz), (buzz, other)): ((Vec<_>, Vec<_>), (Vec<_>, Vec<_>)) = (1..20)
    .into_par_iter()
    .partition_map(|x| match (x % 3, x % 5) {
        (0, 0) => Left(Left(x)),
        (0, _) => Left(Right(x)),
        (_, 0) => Right(Left(x)),
        (_, _) => Right(Right(x)),
    });

assert_eq!(fizzbuzz, [15]);
assert_eq!(fizz, [3, 6, 9, 12, 18]);
assert_eq!(buzz, [5, 10]);
assert_eq!(other, [1, 2, 4, 7, 8, 11, 13, 14, 16, 17, 19]);
``````
use rayon::prelude::*;

let x = vec![1, 2, 3];
let r: Vec<_> = x.into_par_iter().intersperse(-1).collect();

assert_eq!(r, vec![1, -1, 2, -1, 3]);
``````
use rayon::prelude::*;

let result: Vec<_> = (0..100)
    .into_par_iter()
    .filter(|&x| x % 2 == 0)
    .take_any(5)
    .collect();

assert_eq!(result.len(), 5);
assert!(result.windows(2).all(|w| w[0] < w[1]));
``````
use rayon::prelude::*;

let result: Vec<_> = (0..100)
    .into_par_iter()
    .filter(|&x| x % 2 == 0)
    .skip_any(5)
    .collect();

assert_eq!(result.len(), 45);
assert!(result.windows(2).all(|w| w[0] < w[1]));
``````
use rayon::prelude::*;

let result: Vec<_> = (0..100)
    .into_par_iter()
    .take_any_while(|x| *x < 50)
    .collect();

assert!(result.len() <= 50);
assert!(result.windows(2).all(|w| w[0] < w[1]));
``````
use rayon::prelude::*;
use std::sync::atomic::AtomicUsize;
use std::sync::atomic::Ordering::Relaxed;

// Collect any group of items that sum <= 1000
let quota = AtomicUsize::new(1000);
let result: Vec<_> = (0_usize..100)
    .into_par_iter()
    .take_any_while(|&x| {
        quota.fetch_update(Relaxed, Relaxed, |q| q.checked_sub(x))
            .is_ok()
    })
    .collect();

let sum = result.iter().sum::<usize>();
assert!(matches!(sum, 902..=1000));
``````
use rayon::prelude::*;

let result: Vec<_> = (0..100)
    .into_par_iter()
    .skip_any_while(|x| *x < 50)
    .collect();

assert!(result.len() >= 50);
assert!(result.windows(2).all(|w| w[0] < w[1]));
``````
use rayon::prelude::*;

let result: LinkedList<Vec<_>> = (0..=100)
    .into_par_iter()
    .filter(|x| x % 2 == 0)
    .flat_map(|x| 0..x)
    .collect_vec_list();

// `par_iter.collect_vec_list().into_iter().flatten()` turns
// a parallel iterator into a serial one
let total_len = result.into_iter().flatten().count();
assert_eq!(total_len, 2550);
``` ParallelIterator for rayon::collections::btree_map:: IterMut<'a, K, V>

Source§

#### type Item = (&'a K, &'a mut V)

Source§ impl<'a, K: Sync + 'a, V: Sync + 'a> ParallelIterator for rayon::collections::btree_map:: Iter<'a, K, V>

Source§

#### type Item = (&'a K, &'a V)

Source§ impl<'a, K: Sync, V: Send> ParallelIterator for rayon::collections::hash_map:: IterMut<'a, K, V>

Source§

#### type Item = (&'a K, &'a mut V)

Source§ impl<'a, K: Sync, V: Sync> ParallelIterator for rayon::collections::hash_map:: Iter<'a, K, V>

Source§

#### type Item = (&'a K, &'a V)

Source§ impl<'a, T, I> ParallelIterator for Cloned where I: ParallelIterator , T: 'a + Copy + Send + Sync,

Source§

#### type Item = T

Source§ impl<'a, T: Send> ParallelIterator for rayon::collections::linked_list:: IterMut<'a, T>

Source§

#### type Item = &'a mut T

Source§ impl<'a, T: Send> ParallelIterator for rayon::collections::vec_deque:: IterMut<'a, T>

Source§

#### type Item = &'a mut T

Source§ impl<'a, T: Send> ParallelIterator for rayon::option:: IterMut<'a, T>

Source§

#### type Item = &'a mut T

Source§ impl<'a, T: Send> ParallelIterator for rayon::result:: IterMut<'a, T>

Source§

#### type Item = &'a mut T

Source§ impl<'a, T: Sync + 'a> ParallelIterator for rayon::collections::binary_heap:: Iter<'a, T>

Source§

#### type Item = &'a T

Source§ impl<'a, T: Sync + 'a> ParallelIterator for rayon::collections::btree_set:: Iter<'a, T>

Source§

#### type Item = &'a T

Source§ impl<'a, T: Sync> ParallelIterator for rayon::collections::hash_set:: Iter<'a, T>

Source§

#### type Item = &'a T

Source§ impl<'a, T: Sync> ParallelIterator for rayon::collections::linked_list:: Iter<'a, T>

Source§

#### type Item = &'a T

Source§ impl<'a, T: Sync> ParallelIterator for rayon::collections::vec_deque:: Iter<'a, T>

Source§

#### type Item = &'a T

Source§ impl<'a, T: Sync> ParallelIterator for rayon::option:: Iter<'a, T>

Source§

#### type Item = &'a T

Source§ impl<'a, T: Sync> ParallelIterator for rayon::result:: Iter<'a, T>

Source§

#### type Item = &'a T

Source§ impl<'a> ParallelIterator for rayon::string:: Drain<'a>

Source§

#### type Item = char

Source§ impl<'ch, P: Pattern> ParallelIterator for MatchIndices<'ch, P>

Source§

#### type Item = (usize, &'ch str)

Source§ impl<'ch, P: Pattern> ParallelIterator for Matches<'ch, P>

Source§

#### type Item = &'ch str

Source§ impl<'ch, P: Pattern> ParallelIterator for rayon::str:: Split<'ch, P>

Source§

#### type Item = &'ch str

Source§ impl<'ch, P: Pattern> ParallelIterator for rayon::str:: SplitInclusive<'ch, P>

Source§

#### type Item = &'ch str

Source§ impl<'ch, P: Pattern> ParallelIterator for SplitTerminator<'ch, P>

Source§

#### type Item = &'ch str

Source§ impl<'ch> ParallelIterator for Bytes<'ch>

Source§

#### type Item = u8

Source§ impl<'ch> ParallelIterator for CharIndices<'ch>

Source§

#### type Item = (usize, char)

Source§ impl<'ch> ParallelIterator for Chars<'ch>

Source§

#### type Item = char

Source§ impl<'ch> ParallelIterator for EncodeUtf16<'ch>

Source§

#### type Item = u16

Source§ impl<'ch> ParallelIterator for Lines<'ch>

Source§

#### type Item = &'ch str

Source§ impl<'ch> ParallelIterator for SplitAsciiWhitespace<'ch>

Source§

#### type Item = &'ch str

Source§ impl<'ch> ParallelIterator for SplitWhitespace<'ch>

Source§

#### type Item = &'ch str

Source§ impl<'data, T, P> ParallelIterator for ChunkBy<'data, T, P> where T: Sync, P: Fn(&T, &T) -> bool + Send + Sync,

Source§

#### type Item = &'data [T]

Source§ impl<'data, T, P> ParallelIterator for ChunkByMut<'data, T, P> where T: Send, P: Fn(&T, &T) -> bool + Send + Sync,

Source§

#### type Item = &'data mut [T]

Source§ impl<'data, T, P> ParallelIterator for rayon::slice:: Split<'data, T, P> where P: Fn(&T) -> bool + Sync + Send, T: Sync,

Source§

#### type Item = &'data [T]

Source§ impl<'data, T, P> ParallelIterator for rayon::slice:: SplitInclusive<'data, T, P> where P: Fn(&T) -> bool + Sync + Send, T: Sync,

Source§

#### type Item = &'data [T]

Source§ impl<'data, T, P> ParallelIterator for SplitInclusiveMut<'data, T, P> where P: Fn(&T) -> bool + Sync + Send, T: Send,

Source§

#### type Item = &'data mut [T]

Source§ impl<'data, T, P> ParallelIterator for SplitMut<'data, T, P> where P: Fn(&T) -> bool + Sync + Send, T: Send,

Source§

#### type Item = &'data mut [T]

Source§ impl<'data, T: Send + 'data> ParallelIterator for RChunksExactMut<'data, T>

Source§

#### type Item = &'data mut [T]

Source§ impl<'data, T: Send> ParallelIterator for ChunksExactMut<'data, T>

Source§

#### type Item = &'data mut [T]

Source§ impl<'data, T: Send> ParallelIterator for ChunksMut<'data, T>

Source§

#### type Item = &'data mut [T]

Source§ impl<'data, T: Send> ParallelIterator for rayon::vec:: Drain<'data, T>

Source§

#### type Item = T

Source§ impl<'data, T: Send> ParallelIterator for rayon::slice:: IterMut<'data, T>

Source§

#### type Item = &'data mut T

Source§ impl<'data, T: Send> ParallelIterator for RChunksMut<'data, T>

Source§

#### type Item = &'data mut [T]

Source§ impl<'data, T: Sync, const N: usize> ParallelIterator for ArrayWindows<'data, T, N>

Source§

#### type Item = &'data [T; N]

Source§ impl<'data, T: Sync> ParallelIterator for rayon::slice:: Chunks<'data, T>

Source§

#### type Item = &'data [T]

Source§ impl<'data, T: Sync> ParallelIterator for ChunksExact<'data, T>

Source§

#### type Item = &'data [T]

Source§ impl<'data, T: Sync> ParallelIterator for rayon::slice:: Iter<'data, T>

Source§

#### type Item = &'data T

Source§ impl<'data, T: Sync> ParallelIterator for RChunks<'data, T>

Source§

#### type Item = &'data [T]

Source§ impl<'data, T: Sync> ParallelIterator for RChunksExact<'data, T>

Source§

#### type Item = &'data [T]

Source§ impl<'data, T: Sync> ParallelIterator for Windows<'data, T>

Source§

#### type Item = &'data [T]

Source§ impl<A, B, C, D, E, F, G, H, I, J, K, L> ParallelIterator for MultiZip<(A, B, C, D, E, F, G, H, I, J, K, L)> where A: IndexedParallelIterator, B: IndexedParallelIterator, C: IndexedParallelIterator, D: IndexedParallelIterator, E: IndexedParallelIterator, F: IndexedParallelIterator, G: IndexedParallelIterator, H: IndexedParallelIterator, I: IndexedParallelIterator, J: IndexedParallelIterator, K: IndexedParallelIterator, L: IndexedParallelIterator,

Source§

#### type Item = (:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item)

Source§ impl<A, B, C, D, E, F, G, H, I, J, K> ParallelIterator for MultiZip<(A, B, C, D, E, F, G, H, I, J, K)> where A: IndexedParallelIterator, B: IndexedParallelIterator, C: IndexedParallelIterator, D: IndexedParallelIterator, E: IndexedParallelIterator, F: IndexedParallelIterator, G: IndexedParallelIterator, H: IndexedParallelIterator, I: IndexedParallelIterator, J: IndexedParallelIterator, K: IndexedParallelIterator,

Source§

#### type Item = (:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item)

Source§ impl<A, B, C, D, E, F, G, H, I, J> ParallelIterator for MultiZip<(A, B, C, D, E, F, G, H, I, J)> where A: IndexedParallelIterator, B: IndexedParallelIterator, C: IndexedParallelIterator, D: IndexedParallelIterator, E: IndexedParallelIterator, F: IndexedParallelIterator, G: IndexedParallelIterator, H: IndexedParallelIterator, I: IndexedParallelIterator, J: IndexedParallelIterator,

Source§

#### type Item = (:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item)

Source§ impl<A, B, C, D, E, F, G, H, I> ParallelIterator for MultiZip<(A, B, C, D, E, F, G, H, I)> where A: IndexedParallelIterator, B: IndexedParallelIterator, C: IndexedParallelIterator, D: IndexedParallelIterator, E: IndexedParallelIterator, F: IndexedParallelIterator, G: IndexedParallelIterator, H: IndexedParallelIterator, I: IndexedParallelIterator,

Source§

#### type Item = (:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item)

Source§ impl<A, B, C, D, E, F, G, H> ParallelIterator for MultiZip<(A, B, C, D, E, F, G, H)> where A: IndexedParallelIterator, B: IndexedParallelIterator, C: IndexedParallelIterator, D: IndexedParallelIterator, E: IndexedParallelIterator, F: IndexedParallelIterator, G: IndexedParallelIterator, H: IndexedParallelIterator,

Source§

#### type Item = (:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item)

Source§ impl<A, B, C, D, E, F, G> ParallelIterator for MultiZip<(A, B, C, D, E, F, G)> where A: IndexedParallelIterator, B: IndexedParallelIterator, C: IndexedParallelIterator, D: IndexedParallelIterator, E: IndexedParallelIterator, F: IndexedParallelIterator, G: IndexedParallelIterator,

Source§

#### type Item = (:: Item,:: Item,:: Item,:: Item,:: Item,:: Item,:: Item)

Source§ impl<A, B, C, D, E, F> ParallelIterator for MultiZip<(A, B, C, D, E, F)> where A: IndexedParallelIterator, B: IndexedParallelIterator, C: IndexedParallelIterator, D: IndexedParallelIterator, E: IndexedParallelIterator, F: IndexedParallelIterator,

Source§

#### type Item = (:: Item,:: Item,:: Item,:: Item,:: Item,:: Item)

Source§ impl<A, B, C, D, E> ParallelIterator for MultiZip<(A, B, C, D, E)> where A: IndexedParallelIterator, B: IndexedParallelIterator, C: IndexedParallelIterator, D: IndexedParallelIterator, E: IndexedParallelIterator,

Source§

#### type Item = (:: Item,:: Item,:: Item,:: Item,:: Item)

Source§ impl<A, B, C, D> ParallelIterator for MultiZip<(A, B, C, D)> where A: IndexedParallelIterator, B: IndexedParallelIterator, C: IndexedParallelIterator, D: IndexedParallelIterator,

Source§

#### type Item = (:: Item,:: Item,:: Item,:: Item)

Source§ impl<A, B, C> ParallelIterator for MultiZip<(A, B, C)> where A: IndexedParallelIterator, B: IndexedParallelIterator, C: IndexedParallelIterator,

Source§

#### type Item = (:: Item,:: Item,:: Item)

Source§ impl<A, B> ParallelIterator for Chain<A, B> where A: ParallelIterator, B: ParallelIterator,

Source§

#### type Item =:: Item

Source§ impl<A, B> ParallelIterator for MultiZip<(A, B)> where A: IndexedParallelIterator, B: IndexedParallelIterator,

Source§

#### type Item = (:: Item,:: Item)

Source§ impl<A, B> ParallelIterator for Zip<A, B> where A: IndexedParallelIterator, B: IndexedParallelIterator,

Source§

#### type Item = (:: Item,:: Item)

Source§ impl<A, B> ParallelIterator for ZipEq<A, B> where A: IndexedParallelIterator, B: IndexedParallelIterator,

Source§

#### type Item = (:: Item,:: Item)

Source§ impl ParallelIterator for MultiZip<(A,)> where A
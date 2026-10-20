# (no title)
URL: https://hal.science/hal-00949355v3/file/superaccumulator.pdf

HAL Id: hal-00949355
https://hal.science/hal-00949355v3
Preprint submitted on 9 Feb 2015 (v3), last revised 10 Sep 2015 (v4)
HAL is a multi-disciplinary open access
archive for the deposit and dissemination of scientific research documents, whether they are published or not. The documents may come from
teaching and research institutions in France or
abroad, or from public or private research centers.
L’archive ouverte pluridisciplinaire HAL, est
destinée au dépôt et à la diffusion de documents
scientifiques de niveau recherche, publiés ou non,
émanant des établissements d’enseignement et de
recherche français ou étrangers, des laboratoires
publics ou privés.
HAL Authorization
Numerical Reproducibility for the Parallel Reduction on
Multi- and Many-Core Architectures
Caroline Collange, David Defour, Stef Graillat, Roman Iakymchuk
To cite this version:
Caroline Collange, David Defour, Stef Graillat, Roman Iakymchuk. Numerical Reproducibility for the
Parallel Reduction on Multi- and Many-Core Architectures. 2015. ffhal-00949355v3ff
Numerical Reproducibility for the Parallel Reduction
on Multi- and Many-Core Architectures
Sylvain Collange1, David Defour2, Stef Graillat3, and Roman Iakymchuk3,4
1
INRIA – Centre de recherche Rennes – Bretagne Atlantique
Campus de Beaulieu, F-35042 Rennes Cedex, France
sylvain.collange@inria.fr
2 DALI–LIRMM, Universite de Perpignan, 52 avenue Paul Alduy, F-66860 Perpignan, France ´
david.defour@univ-perp.fr
3
Sorbonne Universites, UPMC Univ Paris 06, UMR 7606, LIP6, F-75005 Paris, France ´
CNRS, UMR 7606, LIP6, F-75005 Paris, France
{stef.graillat, roman.iakymchuk}@lip6.fr
4
Sorbonne Universites, UPMC Univ Paris 06, ICS, F-75005 Paris, France ´
Abstract. On modern multi-core, many-core, and heterogeneous architectures, floating-point computations,
especially reductions, may become non-deterministic and, therefore, non-reproducible mainly due to the nonassociativity of floating-point operations. We introduce an approach to compute the correctly rounded sums of large
floating-point vectors accurately and efficiently, achieving deterministic results by construction. Our multi-level
algorithm consists of two main stages: a filtering stage that relies on fast vectorized floating-point expansions,
and an accumulation stage based on superaccumulators in a high-radix carry-save representation. We present
implementations on recent Intel desktop and server processors, Intel Xeon Phi accelerators, and both AMD and
NVIDIA GPUs. We show that numerical reproducibility and bit-perfect accuracy can be achieved at no additional
cost for large sums that have dynamic ranges of up to 90 orders of magnitude by leveraging arithmetic units that
are left underused by standard reduction algorithms.
Keywords: Parallel floating-point summation, Reproducibility, Accuracy, Kulisch long accumulator, Error-free
transformations, Multi- and many-core architectures.
1 Introduction
The increasing power of current computers enables one to solve more and more complex problems. That leads to a
higher number of floating-point operations to be performed. Each of these operations potentially causes a round-off
error. Because of the round-off error propagation, some problems must be solved with a wider floating-point format.
This is especially the case for applications that carry out very complicated and enormous tasks in scientific fields
such as quantum field theory, supernova simulation, semiconductor physics, or planetary orbit calculations [1]. Since
Exascale computing (1018 operations per second) is likely to be reached within a decade, getting accurate results in
floating-point arithmetic on such computers is an open challenge.
The reproducibility of parallel reductions involving floating-point addition is becoming a serious issue, as noted in
the DARPA Exascale Report [2]. Large-scale summations typically appear within fundamental numerical blocks such
as a dot product or a numerical integration. As floating-point addition is not associative, the result of a summation
may vary from one parallel machine to another or even from one run to another. These discrepancies worsen
on heterogeneous architectures – such as clusters composed of standard CPUs in conjunction with GPUs and/or
accelerators like Intel Xeon Phi – which combine together different programming environments that may follow
different floating-point models and offer different intermediate precision or different operators [3,4]. For instance,
Intel acknowledges in [5] that “there is no way to ensure bit-for-bit reproducibility between code executed on Intel R
Xeon processors and code executed on Intel R Xeon PhiTM co-processors, even for fixed number of threads or for
serial code”. Non-determinism of floating-point calculations in parallel programs causes validation and debugging
issues, and may even lead to deadlocks [6]. We expect these problems will get increasingly critical as the trend
towards large-scale heterogeneous platforms continues.
In this work, we aim at addressing both accuracy and reproducibility in the context of parallel summation. We
advocate to compute the correctly rounded result of the exact sum. The correct rounding criterion guarantees a unique,
well-defined answer, ensuring bit-wise reproducibility. In addition, the correctly-rounded result is also the most
accurate answer possible in the given floating-point format.
1
Without dedicated hardware support, large-scale correctly rounded sums have been considered impractical since
computing the exact sum in software was deemed to be too costly [7]. The current paper revisits this assumption. We
show that: 1. The computation of the exact sum can be carried out at the affordable cost using a large fixed-point
accumulator, which is named a superaccumulator5; 2. The overhead can be made negligible on large sums with low
to moderate dynamic ranges using vectorized floating-point expansions. Besides offering the best possible accuracy
of the result, our approach guarantees the strict reproducibility by always returning the correctly-rounded value of the
exact result.
The paper is organized as follows. Section 2 describes main aspects of floating-point arithmetic and reviews
floating-point expansions as well as superaccumulators. Section 3 presents our multi-level approach to superaccumulation. We expose in Section 4 various implementations and results on multi- and many-core architectures. Finally,
we discuss related works and draw conclusions in Sections 5 and 6, respectively.
2 Floating-Point Arithmetic
Floating-point arithmetic consists in approximating real numbers with a significand, an exponent, and a sign :
x = ± x0.x1 . . . xM−1
| {z }
mantissa
×b
e
, 0 ≤ xi ≤ b − 1, x0 6= 0
where b is the basis (2 in our case), M the precision, and e the exponent that is bounded (emin ≤ e ≤ emax).
The IEEE-754 standard [8], which was revised in 2008, specifies floating-point formats and operations. In this
paper, we consider the binary64 or double-precision format, although our strategy is applicable to the other formats
as well. Floating-point representation of numbers allows to cover a wide dynamic range. Dynamic range is defined
as the absolute ratio between the number with the largest magnitude and the number with the smallest non-zero
magnitude in a set. For instance, binary64 can represent positive numbers from 4.9 × 10−324 to 1.8 × 10308, so it
covers a dynamic range of 3.7 × 10631.
Type Size Mantissa Exponent Unit rounding Interval
binary32 32 bits 23+1 bits 8 bits u = 21−24 ≈ 1, 92 × 10−7 ≈ 10±38
binary64 64 bits 52+1 bits 11 bits u = 21−53 ≈ 2, 22 × 10−16 ≈ 10±308
Fig. 1: Main floating-point formats in IEEE-754.
The standard requires correctly rounded results for the basic arithmetic operations (+, −, ×, /, √ ). It means that
the operations are performed as if the result was first computed with an infinite precision and then rounded to the
floating-point format. Several rounding modes are provided. In this paper, we will assume the rounding-to-nearest
mode. It means that an operation returns the closest floating-point number to the exact result, breaking ties by
rounding to the floating-point number with the even significand.
The non-associativity of floating-point addition occurs due to rounding errors while performing addition of
numbers with different exponents. It leads to the elimination of the lowest-order bits of the sum. For example, in
binary64, (−1 ⊕ 1) ⊕ 2
−53 6= −1 ⊕ (1 ⊕ 2−53) since (−1 ⊕ 1) ⊕ 2−53 = 2−53 and −1 ⊕ (1 ⊕ 2−53) = 0, where
⊕ stands for addition in floating-point arithmetic. In contrast, subtraction between numbers of the same sign and
exponent is always exact. However, due to the cancellation, it amplifies the impact of previous errors. Thus, the
accuracy of a floating-point summation depends on the order of evaluation. More detailed explanation can be found
in the main references in floating-point arithmetic [9,10].
Two approaches exist to perform floating-point addition without incurring round-off errors. The first solution
computes the error which occurred during rounding using floating-point expansions in conjunction with error-free
transformations, see Section 2.1. The second solution exploits the finite range of representable floating-point numbers
by storing every bit in a very long vector of bits, see Section 2.2.
5 We use names Kulisch long accumulator, long accumulator, or superaccumulator interchangeably.
2
2.1 Floating-Point Expansion
In order to perform summations exactly, one has to recover errors which occurred while rounding and keep track of
them. If a and b are two floating-point numbers, r := a ⊕ b is a floating-point number, but not a + b as a general case.
However, in round-to-nearest (which is the case in this paper), the rounding error s := (a+b)−r = (a+b)−(a⊕b)
is a floating-point number and can be computed in floating-point arithmetic. Such an algorithm is called error-free
transformation. The traditional error-free transformation for addition is TwoSum [11], depicted in Alg. 1. The
TwoSum algorithm relies only on floating-point additions and subtractions.
Floating-point expansions represent the result as an unevaluated sum of floating-point numbers, whose components
are ordered by decreasing magnitude with minimal overlap to cover a wide range of exponents. Floating-point
expansions of size 2 and 4 are described in [12] and [13], accordingly. Adding one floating-point number to an
expansion is an iterative operation: the floating-point number is first added to the head of the expansion and the
rounding error is recovered as a floating-point number using an error-free transformation such as TwoSum. The error
is then recursively accumulated to the remaining elements of the expansion.
Algorithm 1 Error-free transformation of the sum of two floating-point numbers.
Function[r, s] = TwoSum(a, b)
1: r ← a ⊕ b
2: z ← r a
3: s ← (a (r z)) ⊕ (b z)
With expansions of size n – that correspond to the unevaluated sum of n floating-point numbers – it is possible to
accumulate floating-point numbers without losing the accuracy as long as every intermediate result can be represented
exactly as a sum of n floating-point numbers. This situation happens when the dynamic range of the sum is lower
than 2
53·n in case of binary64.
The main advantage of this solution is that expansions only involve basic floating-point operations and no memory
access, which allows very efficient implementations on modern architectures thanks to pipelining and SIMD units.
On the one hand, the accuracy of small-size expansions is insufficient for the summation of numerous floating-point
numbers or sums with a large dynamic range. On the other hand, large-size expansions are computationally inefficient
as the complexity of the accumulation algorithm grows linearly with the size of the expansion.
2.2 Superaccumulator
An alternative algorithm to floating-point expansions is based on very long fixed-point accumulators. A fixed-point
representation store numbers using an integral part and a fractional part of fixed size, or equivalently as a scaled
integer. The length of the fixed-point accumulator is selected in such way that it can represent every bit of information
of the input format (binary64 in our case); this covers the range from the minimum representable floating-point
value to the maximum value, independently of the sign. For instance, Kulisch [14] proposed to utilize an accumulator
of 4288 bits to handle dot products of two vectors composed of binary64 values. The summation is performed
without loss of information by accumulating every floating-point input number in the long accumulator, see Fig. 2.
The superaccumulator is the perfect solution to produce the exact result of a very large amount of floating-point
numbers of arbitrary magnitude. However, for a long period this approach was considered impractical as it induces a
very large memory overhead. Furthermore, without dedicated hardware support, its performance is limited by indirect
memory accesses that makes vectorization challenging.
Fig. 2: Kulisch long accumulator.
3
3 Hierarchical Superaccumulation Scheme
Most prior works on exact summation have been targeting severely ill-conditioned problems that could not be
satisfied using the accuracy provided by the conventional floating-point addition. Our objective is different – we are
concerned with computing a deterministic and accuracy-guaranteed result for sums that are typically evaluated using
today’s floating-point arithmetic. We expect such sums to be well-conditioned or mildly ill-conditioned and cover a
commensurate dynamic range (up to 1050).
We follow a multi-level approach shown in Fig. 3. The accumulation of floating-point numbers is split into five
levels. This decomposition suits well the memory hierarchy as well as the nested parallelism of modern architectures.
In addition, such approach makes full use of SIMD, multi-thread, and multi-core parallelism.
Fig. 3: Multi-level summation approach.
The first level consists of floating-point expansions in order to perform fast accumulation of consecutive floatingpoint numbers with similar magnitude. On CPUs and Xeon Phi accelerators, the expansions are vectorized to take
advantage of SIMD units: a vector of input numbers is accumulated in parallel to a vector of expansions. On GPUs,
each thread maintains its own expansion of size n. As tens to thousands of threads running in parallel using their
private registers to store floating-point expansions, this solution ensures the high speed of computations due to the
minimized memory accesses.
4
The second level is invoked only whenever the accuracy provided by expansions is not enough. Threads transmit
to private superaccumulators values that are too small to be accumulated exactly in the expansions as well as the
results of partial sums accumulated during the first step. Private superaccumulators are stored in a fast local memories
like cache (CPU and Xeon Phi) or local memory (GPU). They contain exact partial sums for one thread or a group of
threads, respectively.
In the third level, private superaccumulators within a group of threads are merged into a single scalar superaccumulator. In the fourth level, all scalar superaccumulators within one processor (GPU or MPI process) are combined
together into one single superaccumulator accessible by all threads. This step is performed with the standard parallel
reduction. It is followed by the MPI reduction among nodes. Finally, the fifth level consists in rounding the global
superaccumulator back to the target floating-point format in order to produce the correctly rounded result. One can
notice that levels 2 to 4 of the proposed algorithm have several concepts in common with the histogram problem [15].
We present below a more detailed level-by-level explanation of the proposed approach, illustraded in Fig. 3.
3.1 Level 1: Filtering
We propose to extend the classical approach described in Section 2.1 in order to maintain floating-point expansions
of size n. We maintain a vector of n floating-point numbers as the accumulator. We update this expansion using
error-free transformations (Alg. 2). This new algorithm is amenable to parallelization, vectorization and pipelining by
maintaining and updating multiple expansions in parallel.
Algorithm 2 Floating-point expansion of size n with error-free transformations.
Function = ExpansionAccumulate(x)
1: for i = 0 → n − 1 do
2: (ai, x) ← TwoSum(ai, x)
3: end for
4: if x 6= 0 then
5: Superaccumulate(x)
6: end if
Alg. 2 works as an iterative process: the input number is first added to the head of the expansion. Then, the
rounding error is extracted by the TwoSum algorithm and propagated to the next slot of the expansion. This step is
repeated until the n-th slot of the expansion. Finally, underflows can be detected by checking if the last rounding error
x is non-zero. If this happens, the result of the accumulation cannot be represented with a floating-point expansion of
size n. In this case, the non-zero residue x is forwarded to the scalar superaccumulator (described in Section 3.2). We
also propose a version of Alg. 2 that consists in stopping the accumulation loop as soon as the residue is zero (x ≡ 0).
This technique is called early-exit. Its performance depends on two factors: the distribution of input numbers and the
ability of the architecture to handle irregular branches.
The challenge of optimizing the first step is to select a suitable value of n. A large value of n will lead to
large expansions that eventually reduce the number of calls to the second level (superaccumulator), however this
will increase register usage. A small value of n will impose a limited representation range for the expansion that
will reduce the pressure on registers, but will cause more transfers towards superaccumulators. In both cases, all
components of the floating-point expansion are accumulated into the superaccumulator at the end of the summation.
3.2 Levels 2 and 3: Private and Scalar Superaccumulators
We follow the general approach of the Complete Register implementation proposed by Bohlender and Kulisch [16] and
adapt it to a software implementation. This approach allows to accumulate floating-point numbers in amortized O(1)
time regardless of the length of the long accumulator. The algorithm behind consists of aligning the floating-point
significand and accessing the corresponding words in the accumulator.
We implement the superaccumulator as a vector of 64-bit signed integers that partially overlap by following a
high-radix carry-save scheme [17]. Thanks to this representation, the M leading bits of each digit store the carry
information, delaying the carry propagation to every 2M accumulation steps. Unlike Bohlender’s and Kulisch’s
approach, we use multiple carry-save bits per digit to reduce the frequency of carry propagation. Each digit is
5
responsible for accumulating w = 64 − M bits of the sum; the digit i has a weight of 2
w·i
. The exact sum s is
expressed as
s =
X
h
i=l
2
wiai
, −2
63 ≤ ai < 263, l =
j
emin
w
k
, h =
l
emax
w
m
,
where emin and emax are the smallest and the largest binary floating-point exponents, respectively. In our implementation, we choose w = 56 and M = 8.
The use of 64-bit integer arithmetic allows the digit size w to be greater or equal than the floating-point significand
size (m = 52), so a mantissa may span at most two digits. In order to split the mantissa of the input number x and
accumulate each part to the corresponding digits of the superaccumulator, we use the algorithm depicted in Fig. 4.
This algorithm is based on rounding scaled floating-point numbers. First, the exponent of the input number x is
extracted and used to compute the indexes k and k − 1 of the two consecutive slots in the superaccumulator. Then, x
is scaled by multiplying it by 2
−kw and rounded to the nearest integer. This integer corresponds to the upper bits of
the mantissa that are accumulated to the digit at the index k of the superaccumulator. It is also used to compute the
lower part of the mantissa of x that is added to the digit at the position k − 1 within the superaccumulator. When the
result of the accumulation exceeds the range of the superaccumulator slot, a partial normalization is performed along
the propagation of the carry or the borrow. In this case, the upper M bits of the current digit are transferred to the
next digit until the carry propagation chain stops. The carry or borrow propagation is only needed at most once per
every 2M−1accumulation steps and typically requires only a single propagation step. At the end of the summation, a
complete normalization pass propagates all carries.
Once all input numbers are accumulated into private superaccumulators, these superaccumulators are merged
together within a group of threads into a single scalar superaccumulator. We use the classic reduction algorithm, albeit
with a larger payload than in the customary floating-point case. Reduction is a common parallel primitive available in
highly optimized versions on various systems which we rely on. Each reduction step involves the summation of two
superaccumulators. All digits of the superaccumulators are summed in parallel to take advantage of vectorization and
pipelining. We ensure that no carry can propagate by counting the number of reduction steps that occurred since the
last normalization, and trigger normalizations as required. In practice, 8 carry-save bits enable a normalization-free
reduction across up to 256 threads.
+
+
x
Scale by −kw
xs
Round to nearest int
2
kw 2
(k−1)w
xe
Convert to int
Subtract
acc[k]
acc[k-1]
Accumulate
Accumulate
Check carries and propagate
x
0
s
xr
x
0
e
x
0
r
2
(k+1)w
Scale by w
Convert to int
Fig. 4: Scalar accumulation scheme.
3.3 Levels 4 and 5: Parallel Reduction and Rounding
As for private superaccumulators, we perform the same reduction procedure in order to combine together all
scalar superaccumulators of one processor (MPI process) into one single global superaccumulator. In turn, the
superaccumulators of each node of the cluster are accumulated into a single superaccumulator using the MPI
reduction.
6
To perform the final rounding to the target floating-point format, we first normalize the superaccumulator. Then,
digits are scanned for the most-significant digit that is non-zero (positive) or not minus-one (negative); this mostsignificant digit has the weight k. We compute the sticky bit as a logical OR of digits k − 2 to 0, and add it to the
word k − 2. This sticky bit is used to discriminate between a number that falls exactly between two floating-point
numbers (rounded to the even mantissa) and a number that is slightly higher (rounded up). Finally, words k, k − 1,
and k − 2 are added together by following the Add3 algorithm [18], which is based on round-to-odd rounding.
4 Implementations and Experimental Results
This section details our implementations of the multi-level scheme and presents their evaluation on the whole range of
parallel platforms, which are listed in Tab. 1: desktop and server CPUs, the Intel Xeon Phi many-core accelerator, and
both NVIDIA and AMD GPUs. We verified the accuracy of our implementation by comparing the computed results
with the ones produced by the multiple precision library MPFR [19,20], which is, unfortunately, not multi-threaded.
In case of binary64, we used 2098 bits (emin + emax + mantissa = 1022 + 1023 + 53) within the MPFR library in
order to guarantee the bit-wise accuracy as well as reproducibility of the deterministic sums independently of both
the round-off errors and dynamic ranges.
Table 1: Hardware platforms employed in the experimental evaluation.
A Intel Core i7-4770 (Haswell) 4 cores with Hyper-Threading 3.400 GHz
B Mesu cluster Intel Xeon E5-4650L (Sandy Bridge) 64 nodes with 2 × 8 cores 2.600 GHz
C Intel Xeon Phi 5110P 60 cores × 4-way Multi-Threading 1.053 GHz
D NVIDIA Tesla K20c 13 SMs × 192 CUDA cores 0.705 GHz
E AMD Radeon HD 7970 32 CUs × 64 units 0.925 GHz
4.1 Implementations
Our implementations strive to use all resources of modern processors: SIMD instructions, fused-multiply-and-add
(FMA) instruction, and multi-threading on multi-core CPUs and Xeon Phi; local memory and atomic instructions
on GPUs. For example, on the Intel Haswell architecture, we use AVX intrinsics to benefit from the 4−way SIMD
and implement TwoSum by replacing half of the 6 additions/subtractions by FMAs (multiplying by one). The latter
optimization allows to use both the floating-point adder and FMA units that can run in parallel on the Haswell
micro-architecture. Thread-level parallelism is exposed using OpenMP in order to take advantage of multi-core and
hardware multi-threading. The final inter-node reduction within a cluster is performed using MPI.
On the Intel Xeon Phi 5110P many-core accelerator, we benefit from 8−way SIMD by using 512−bit vector
intrinsics. We perform explicit memory prefetching in order to maximize memory throughput. For the performance
experiments, we use 236 threads with the compact affinity.
We develop separate hand-tuned OpenCL implementation for NVIDIA and AMD GPUs. They use 16 superaccumulators per work group, which are stored in local memory. In order to avoid bank conflicts, superaccumulators are
interleaved together to spread their digits among different memory banks. Concurrency between 16 threads that share
one superaccumulator is resolved through atomic operations.
All provided implementations are parallel multi-threaded implementations.
4.2 Performance scaling
As baselines, we consider several algorithms:
1. A vectorized and parallelized non-deterministic reduction (indicated as “Parallel FP sum” in all figures) that is
computed using vector intrinsics and OpenMP reduction on CPUs and Xeon Phi, and using the standard parallel
reduction algorithm like the one introduced in [15] for histograms on GPUs;
2. The deterministic floating-point reduction provided by the Intel TBB library [21] (referred as “TBB deterministic”);
7
3. The Fast Deterministic Parallel Sum algorithm, Alg. 9 Parallel K-fold Reproducible Sum [7], proposed by Demmel
and Nguyen (cited as “Demmel fast”). We have implemented the Fast Deterministic Parallel Sum algorithm
on the range of architectures including Intel Xeon Phi co-processors and both NVIDIA and AMD GPUs. This
algorithm requires to conduct two reductions: one to find the maximum element and the other for summation. On
CPUs, the reduction is performed using Intel TBB, as OpenMP does not natively support reductions with the
maximum operator. On GPUs, due to the impossibility to perform synchronization among work-groups within
one kernel in OpenCL 1.2, two kernels have to be invoked.
Figs. 5a, 5c, 5e, 6a and 6c present the throughput, which is measured in billions of accumulations per second
(Gacc/s), achieved by the summation algorithms as a function of the input dataset size N of double-precision
floating-point numbers. For these experiments, we use numbers with a dynamic range of one (numbers with identical
exponents), which corresponds to the best case for our method. In the keys of Figs. 5 to 7, “Superacc” corresponds
to our algorithm for computing deterministic sums that is solely based on superaccumulators (Section 3.2); “FPEn
+ Superacc” stands for our algorithm with floating-point expansions of size n (n = 2 : 8) in conjunction with
error-free transformations and superaccumulators when needed; “FPE8EE + Superacc” represents our algorithm with
the expansion of size 8 and the early-exit optimization technique as described in Section 3.1.
We can observe from these plots that on large datasets the performance of the baseline unordered sum as well
as the expansion cache is constrained by the memory bandwidth on all platforms. For instance, both algorithms
achieve 23.3 GB/s on Platform A over the theoretical peak bandwidth of 25.6 GB/s. Indeed, the peak double-precision
performance of this CPU is 218 GFlops. This means that for every double-precision number loaded from memory,
68 floating-point operations could be performed without affecting the total throughput. With only one operation per
input number, the conventional floating-point sum or reduction leaves most computational resources idle waiting for
data from the memory.
When the input dataset fits within caches, the non-reproducible parallel sum outperforms our expansion cache
implementation by a factor of 2 (NVIDIA GPU) to 5 (Intel Haswell). However, the deterministic reduction of TBB
runs two orders of magnitude slower (75 Macc/s on Platform A and 136 Macc/s on Platform C) than our version. The
general-purpose multi-precision MPFR library (not shown) runs one order of magnitude slower at 9.3 Macc/s on
Platform A.
The Fast Deterministic Parallel Sum algorithm requires two passes on the data. In memory-bound scenarios, its
execution takes twice the time of the unordered reduction and other single-pass algorithms. In addition, the overhead
of the second kernel call impacts the performance of the GPU implementation.
A global MPI reduction is the next step within the fourth level. We have implemented the parallel reduction among
compute nodes using MPI Reduce() on the local sums represented as either binary64 or superaccumulators.
Fig. 7a shows the results of performance scaling of our and the other algorithms on the Mesu cluster6 by varying the
number of processors for the summation of 16e06 double-precision floating-point numbers per each MPI process;
such a large dataset size is chosen to ensure the out-of-cache case. For each processor count ranging from 1 to 64 7,
we measure the computation and reduction time of the parallel non-reproducible summation, the TBB deterministic
summation, and our algorithm. These algorithms compute the local sums on each MPI process. Then MPI Reduce()
is applied to calculate the final sum. We attach two MPI processes to each node, that is composed of two Intel
Sandy-Bridge processors. On the figure, the local summation time is colored red and the MPI reduction time is
colored green. Since the MPI reduction time is 2-3 order of magnitude smaller than the local summation time even in
case of superaccumulators, it is hardly visible on the figure. The total runtime of each algorithm is normalized by the
total execution time of the parallel floating-point summation. The TBB deterministic sum is roughly 68 times slower
than the parallel floating-point summation on one node. Hence, we cut this timing in order to provided better picture
of the rest of the results that do not exceed the slowdown of 9 times.
For the whole range of processors, the execution time of each algorithm is dominated by the local summation time
because of the dataset size (out-of-cache case). In addition, due to the equal distribution of computations among MPI
processes (each MPI process sums up 16e06 binary64 numbers), the computation time is roughly equivalent on the
whole range of MPI processes, while the reduction time changes depending on the number of MPI processes involved.
The Fast Deterministic Parallel Sum algorithm is 4.72 times slower than the conventional parallel summation with 64
MPI processes (corresponds to 64 CPUs). In contrast, two of our implementations – floating-point expansions of size
2 and size 8 with the early-exit technique – deliver accurate as well as bit-wise reproducible results. The overhead of
these two implementations compared to the conventional algorithm on 64 CPUs is 10.4 % and 10.2 %, accordingly.
6 http://mesu-smn.dsi.upmc.fr/mediawiki/index.php5/Main_Page#Mesu
7 Due to the extensive workload on the Mesu cluster and the policies there, we can run at most 64 MPI processes, meaning utilize
only a half of the whole cluster.
8
 0
 5
 10
 15
 20
 25
 1000 10000 100000 1e+06 1e+07 1e+08 1e+09
Gacc/s
Array size
Parallel FP sum
Serial FP sum
TBB deterministic
Demmel fast
Superacc
FPE2 + Superacc
FPE4 + Superacc
FPE8EE + Superacc
(a) Platform A.
 0
 5
 10
 15
 20
 25
 1 1e+20 1e+40 1e+60 1e+80 1e+100 1e+120 1e+140
Gacc/s
Dynamic range
Parallel FP Sum
Superacc
FPE2 + Superacc
FPE3 + Superacc
FPE4 + Superacc
FPE8EE + Superacc
(b) Platform A: N = 2e06.
 0
 5
 10
 15
 20
 25
 1000 10000 100000 1e+06 1e+07 1e+08 1e+09
Gacc/s
Array size
Parallel FP sum
Serial sum
TBB deterministic
Demmel fast
Superacc
FPE2 + Superacc
FPE4 + Superacc
FPE8EE + Superacc
(c) Platform B.
 0
 1
 2
 3
 4
 5
 6
 1 1e+20 1e+40 1e+60 1e+80 1e+100 1e+120 1e+140
Gacc/s
Dynamic range
Parallel FP Sum
Superacc
FPE2 + Superacc
FPE3 + Superacc
FPE4 + Superacc
FPE8EE + Superacc
(d) Platform B: N = 2e06.
 0
 5
 10
 15
 20
 25
 1000 10000 100000 1e+06 1e+07 1e+08 1e+09
Gacc/s
Array size
Parallel FP sum
TBB deterministic
Demmel fast
Superacc
FPE2 + Superacc
FPE3 + Superacc
FPE4 + Superacc
FPE8EE + Superacc
(e) Platform C.
 0
 5
 10
 15
 20
 25
 1 1e+20 1e+40 1e+60 1e+80 1e+100 1e+120 1e+140
Gacc/s
Dynamic range
Parallel FP Sum
Superacc
FPE2 + Superacc
FPE3 + Superacc
FPE4 + Superacc
FPE8EE + Superacc
(f) Platform C: N = 67e06.
Fig. 5: The summation performance results on modern desktop and server Intel CPUs as well as the Intel Xeon Phi
co-processor, see Tab. 1; Gacc/s stands for billions of accumulations per second.
We extend our study to analyze the impact of communication (parallel reduction in our case) on the performance
of the above-mentioned algorithms by fixing the number of MPI processes and varying the problem size per each
process, see Fig. 7b. The results show that for the in-cache cases the total computation time is dominated by the
parallel reduction. This is clearly seen for our algorithm since the parallel reduction on superaccumulators takes
much more time than on single binary64. When our implementations are already out-of-cache, but the parallel
summation still benefits from the in-cache scenario, the performance gap between our implementations and the
conventional summation grows and reaches its maximum at n = 1e06. That also corresponds to the results on single
node, see Fig. 5c. For the out-of-cache cases, these performance gap decreases significantly – so that for n = 16e06
9
 0
 2
 4
 6
 8
 10
 12
 14
 16
 18
 1000 10000 100000 1e+06 1e+07 1e+08 1e+09
Gacc/s
Array size
Parallel FP Sum
Demmel fast
Superacc
FPE2 + Superacc
FPE3 + Superacc
FPE4 + Superacc
FPE8 + Superacc
FPE8EE + Superacc
(a) Platform D.
 0
 2
 4
 6
 8
 10
 12
 14
 16
 18
 1 1e+20 1e+40 1e+60 1e+80 1e+100 1e+120 1e+140
Gacc/s
Dynamic range
Parallel FP Sum
Demmel fast
Superacc
FPE2 + Superacc
FPE3 + Superacc
FPE4 + Superacc
FPE8 + Superacc
FPE8EE + Superacc
(b) Platform D: N = 67e06.
 0
 5
 10
 15
 20
 25
 30
 1000 10000 100000 1e+06 1e+07 1e+08 1e+09
Gacc/s
Array size
Parallel FP Sum
Demmel fast
Superacc
FPE2 + Superacc
FPE3 + Superacc
FPE4 + Superacc
FPE8 + Superacc
FPE8EE + Superacc
(c) Platform E.
 0
 5
 10
 15
 20
 25
 30
 1 1e+20 1e+40 1e+60 1e+80 1e+100 1e+120 1e+140
Gacc/s
Dynamic range
Parallel FP Sum
Superacc
FPE2 + Superacc
FPE3 + Superacc
FPE4 + Superacc
FPE8 + Superacc
FPE8EE + Superacc
(d) Platform E; N = 67e06.
Fig. 6: The summation performance results on NVIDIA and AMD GPUs, see Tab. 1.
floating-point expansions of size 2 and size 8 with the early-exit technique (both use superaccumulators when needed)
are only 8.7 % and 9.1 % off the parallel summation performance, respectively.
4.3 Data-dependent performance
We validate the discussed algorithms using various dynamic ranges for the input arrays by generating pseudo-random
numbers following a log-uniform number distribution. This distribution represents the worst case for our algorithm as
the exponents of floating-point numbers follow a uniform distribution. Since running experiments on large datasets
clamps all curves below the memory bandwidth limit on CPUs, we present results on datasets with 2 millions
(Platforms A-C) and 67 millions (Platforms D and E) of elements in order to highlight the difference between
implementations.
Figs. 5b, 5d, 5f, 6b and 6d represent the scenario when the array size is fixed, but the range of its elements varies.
Floating-point expansions adapt dynamically to the range of input numbers. The expansion cache with 8 words and
the early-exit technique saturates the memory bandwidth for dynamic ranges up to 1030, 1090, 1015, 1050, and 1050
on platforms A, B, C, D, and E, accordingly. One can observe that in the worst case, our method is between 3 times
(on Platform E) and 44 times (on Platform C) slower than the non-deterministic sum. However, it still reaches 64% of
the performance of the Demmel’s and Nguyen’s Fast Deterministic Parallel Sum and exceeds the performance of the
serial sum.
The results of the Fast Deterministic Parallel Sum and the TBB deterministic sum algorithms on Platforms A-C
are not represented on the dynamic range figures as their performance does not depend on the value of the inputs. The
runtime of these methods is constant for any dynamic ranges, for example, see Fig. 6b.
10
 0
 2
 4
 6
 8
 10
ParallelFPSumDemmelFastTBBDeterministicSuperaccFPE2+SuperaccFPE4+SuperaccFPE8EE+SuperaccParallelFPSumDemmelFastTBBDeterministicSuperaccFPE2+SuperaccFPE4+SuperaccFPE8EE+SuperaccParallelFPSumDemmelFastTBBDeterministicSuperaccFPE2+SuperaccFPE4+SuperaccFPE8EE+SuperaccParallelFPSumDemmelFastTBBDeterministicSuperaccFPE2+SuperaccFPE4+SuperaccFPE8EE+SuperaccParallelFPSumDemmelFastTBBDeterministicSuperaccFPE2+SuperaccFPE4+SuperaccFPE8EE+SuperaccParallelFPSumDemmelFastTBBDeterministicSuperaccFPE2+SuperaccFPE4+SuperaccFPE8EE+SuperaccParallelFPSumDemmelFastTBBDeterministicSuperaccFPE2+SuperaccFPE4+SuperaccFPE8EE+Superacc
Normilized time to parallel summation
MPI Processes
Computation
Reduction
1 2 4 8 16 32 64
(a) Varying the number of MPI process to sum n = 16e06 elements per each.
 0
 2
 4
 6
 8
 10
ParallelFPSumDemmelFastTBBDeterministicSuperaccFPE2+SuperaccFPE4+SuperaccFPE8EE+SuperaccParallelFPSumDemmelFastTBBDeterministicSuperaccFPE2+SuperaccFPE4+SuperaccFPE8EE+SuperaccParallelFPSumDemmelFastTBBDeterministicSuperaccFPE2+SuperaccFPE4+SuperaccFPE8EE+SuperaccParallelFPSumDemmelFastTBBDeterministicSuperaccFPE2+SuperaccFPE4+SuperaccFPE8EE+SuperaccParallelFPSumDemmelFastTBBDeterministicSuperaccFPE2+SuperaccFPE4+SuperaccFPE8EE+SuperaccParallelFPSumDemmelFastTBBDeterministicSuperaccFPE2+SuperaccFPE4+SuperaccFPE8EE+SuperaccParallelFPSumDemmelFastTBBDeterministicSuperaccFPE2+SuperaccFPE4+SuperaccFPE8EE+SuperaccParallelFPSumDemmelFastTBBDeterministicSuperaccFPE2+SuperaccFPE4+SuperaccFPE8EE+Superacc
Normilized time to parallel summation
Number of values per MPI process
Computation
Reduce
1024 4096 16384 65536 2.6e+05 1e+06 4e+06 16e+06
(b) Fixed the number of MPI processes to 64 and vary the array size.
Fig. 7: Performance scaling on the Mesu cluster.
11
Superaccumulator performance is also close to constant, because of its accumulation time that is O(1) for any
input value. Minor variations occur due to load-store forwarding effects on CPUs and atomic conflicts on NVIDIA
GPUs.
These experiments show that our multi-level algorithm is faster than existing alternatives and it is competitive
with the standard parallel reduction for input vectors with moderate dynamic range. This confirms our assumptions
and objectives stated earlier in Section 3. Moreover, our multi-level algorithm guarantees accurate, deterministic, and
reproducible results for numbers of any dynamic range.
5 Related Works
Many techniques have been proposed to increase the accuracy of floating-point summation. One is based on a long
accumulator as described in Section 2.2. This solution is suitable for hardware implementations due to the constant
accumulation time [16]. A recent analysis of the software cost of long accumulators [22] advocates their usage on
new architectures. However it does not incorporate implementations nor numerical validations.
Another approach to exact summation consists in pure floating-point algorithms. The idea is to store the exact
sum as an expansion or an unevaluated sum of floating-point numbers [23]. However, as we mentioned already, this
solution solely increases the accuracy of basic operations, but it neither reaches bit-accurate results nor is efficient for
large precisions. Therefore, some recent works are focusing on hybrid solutions that store the sum as floating-point
numbers of fixed exponent [24,25] without completely avoiding the previous drawbacks. These algorithms are mainly
sequential and are not suitable for parallel implementations. This is mainly due to the need to scan all the numbers
before starting the computation of the sum. Arbitrary precision libraries – like MPFR [19] – are able to provide
correct rounding. However, they are not designed to achieve acceptable performance for reproducible results. In case
of the MPFR library, it is also not multi-threaded. For instance, our solution is three orders of magnitude faster than
MPFR, see Section 4.
To enhance reproducibility – defined as getting a bitwise identical floating-point result from multiple runs of the
same code – Intel proposed a “Conditional Numerical Reproducibility” (CNR) in its Math Kernel Library (MKL).
However, CNR is slow and does not give any guarantee on the accuracy of the result. Demmel and Nguyen recently
introduced a family of algorithms for reproducible summation in floating-point arithmetic [7]. These algorithms
always returns the same answer. They first compute an absolute bound of the sum and then round all numbers to
a fraction of this bound. So, the addition of the rounded quantities is exact. Since the computed sum may be less
accurate than the non-deterministic one, this solution offers no guarantees on the accuracy. It also induces a twofold
slowdown as data transfers and reductions need to be performed twice: for computing the bound and the sum. As
Section 4 shows, our algorithm is faster in the bandwidth-constrained scenarios with moderate dynamic ranges.
Demmel and Nguyen have also improved the previous results [26] by using one single reduction step among nodes.
Such an improvement yielded roughly 15 % overhead on 2048 processors compared to the Intel MKL dasum(),
but it shows roughly 4.5 times slowdown on 32 processors. Demmel and Nguyen have extended their concept to
reproducible BLAS routines, distributed in their ReproBLAS library8. Arteada et al. [27] used Demmel and Nguyen’s
algorithms with improved communication between nodes based on both one- and two-reductions. They were able
to reach the same accuracy with slightly better performance results (the overhead is within 10 %) compared to the
conventional summation in case of the single reduction algorithm.
6 Conclusions and Future Work
We presented a solution to achieve correct rounding for the floating-point summation problem, along with implementations on multi- and many-core architectures. This yielded results that are both reproducible and accurate to the last
bit. For dataset larger than 107elements with dynamic ranges up to 1015, the proposed approach solves the summation
problem with similar performance as the classic highly optimized parallel floating-point summations; however, the
parallel floating-point summation provides neither correct rounding nor reproducibility. These competitive results
were achieved using the expansion of size 4 on both multi-core platforms and GPUs, and the expansion of size 8 with
the early-exit optimization on Xeon Phi for low to medium dynamic ranges. Such dynamic ranges correspond to the
most common cases that occur in practice. Thanks to the multi-level strategy, we were able to deliver bit-accurate
results for large dynamic ranges at 25% of the parallel floating-point summation performance on multi-core and
GPU platforms. Furthermore, we demonstrated that the multi-level correctly-rounded summation outperforms the
8 http://bebop.cs.berkeley.edu/reproblas/
12
other recently proposed reproducible summation algorithms – like Demmel and Nguyen’s algorithm – while offering
correct rounding.
We followed a multi-level approach for correct rounding that is similar to the one used in elementary functions [28].
This approach consists in optimizing common cases while keeping track of the error in order to route the few difficult
cases to dedicated routines; these routines are more expensive, however they guarantee deterministic and bit-accurate
results. As the performance of hardware architectures becomes increasingly limited by the so-called memory wall,
we expect that the overhead of those dedicated routines will decrease.
We showed that an optimized library implementation of exact summation is viable on current architectures, even
in the absence of dedicated hardware support for long accumulation. By guaranteeing a single well-specified result
for sums, like the IEEE-754 standard does for basic operations, it offers determinism and numerical safety for a cost
that is negligible in most cases. This supports the efforts to make complete

# A Reproducible Accurate Summation Algorithm for High-Performance Computing
URL: https://perso.lip6.fr/Stef.Graillat/papers/SIAMEX14.pdf

## A Reproducible Accurate Summation Algorithm for High-Performance Computing

#### Sylvain Collange 1, David Defour 2, Stef Graillat 3, and Roman Iakymchuk 3

1 INRIA – Centre de recherche Rennes – Bretagne Atlantique Campus de Beaulieu, F-35042 Rennes Cedex, France sylvain.collange@inria.fr 2 DALI–LIRMM, Universite de Perpignan, 52 avenue Paul Alduy, F-66860 Perpignan, France ´ david.defour@univ-perp.fr 3 Sorbonne Universites, UPMC Univ Paris 06, UMR 7606, LIP6, F-75005 Paris, France ´ CNRS, UMR 7606, LIP6, F-75005 Paris, France { stef.graillat, roman.iakymchuk} @lip6.fr

Keywords: Parallel floating-point summation, reproducibility, accuracy, long accumulator, multi-precision, 
multi- and many-core architectures. 
Floating-point (FP) addition is non-associative and parallel reduction involving this operation is a 
serious issue as noted in the DARPA Exascale Report [1]. Such large summations typically appear within 
fundamental numerical blocks such as dot products or numerical integrations. Hence, the result may vary 
from one parallel machine to another or even from one run to another. These discrepancies worsen on 
heterogeneous architectures – such as clusters with GPUs or Intel Xeon Phi processors – which combine 
programming environments that may obey various floating-point models and offer different intermediate 
precision or different operators [2,3]. Such non-determinism of floating-point calculations in parallel 
programs causes validation and debugging issues, and may lead to deadlocks [4]. 
The increasing power of current computers enables one to solve more and more complex problems. 
That, consequently, leads to a higher number of floating-point operations to be performed; each of them 
potentially causing a round-off error. Because of the round-off error propagation, some problems must be 
solved with a wider floating-point format. Two approaches exist to perform floating-point addition without 
incurring round-off errors. The first approach aims at computing the error that is occurred during rounding 
using FP expansions, which are based on an error-free transformation. FP expansions represent the result 
as an unevaluated sum of a fixed number of FP numbers, whose components are ordered in magnitude 
with minimal overlap to cover a wide range of exponents. FP expansions of sizes 2 and 4 are presented 
in [5] and [6], accordingly. The main advantage of this solution is that the expansion can stay in registers 
during the computations. But, the accuracy is insufficient for the summation of numerous FP numbers 
or sums with a huge dynamic range. Moreover, their complexity grows linearly with the size of the 
expansion. An alternative approach to expansions exploits the finite range of representable floating-point 
numbers by storing every bit in a very long vector of bits (accumulator). The length of the accumulator is 
chosen such that every bit of information of the input format can be represented; this covers the range 
from the minimum representable floating-point value to the maximum value, independently of the sign. 
For instance, Kulisch [7] proposed to utilize an accumulator of 4288 bits to handle the accumulation 
of products of 64-bit IEEE floating-point values. The Kulisch accumulator is a solution to produce the 
exact result of a very large amount of floating-point numbers of arbitrary magnitude. However, for a long 
period this approach was considered impractical as it induces a very large memory overhead. Furthermore, 
without dedicated hardware support, its performance is limited by indirect memory accesses that make 
vectorization challenging. 
We aim at addressing both issues of accuracy and reproducibility in the context of summation. We 
advocate to compute the correctly-rounded result of the exact sum. Besides offering strict reproducibility 
through an unambiguous definition of the expected result, our approach guarantees that the result has 
the best accuracy possible. However, the general use of correctly rounded sums has been considered 
impracticable since computing the exact sum was deemed to be too costly [8]. We revisit this assumption 
and show that: 1. The computation of the exact sum can be carried out at the affordable cost using a large 
fixed-point accumulator, which is called a superaccumulator; 2. The overhead can be made negligible on 
large sums with low dynamic range using vectorized FP expansions. 
Most prior works on exact accumulation have been targeting ill-conditioned problems that could not 
be satisfied using the accuracy provided by the conventional floating-point accumulation. We instead focus 
on computing a deterministic and accuracy-guaranteed result for sums that are typically evaluated using 
the floating-point arithmetic today. We expect such sums to be well-conditioned and cover a moderate 
dynamic range. 
We introduce a multi-level algorithm, where the accumulation of FP numbers is split into five levels; 
this decomposition is suitable for the nested parallelism of modern architectures. Thus, the first level 
consists of FP expansions to filter large numbers, which are expected to be the major part of all inputs. 
The second level is only invoked whenever the accuracy provided by expansions is not enough. Threads 
will send the values that are too small to be accumulated exactly in the expansions, as well as the results 
of partial sums accumulated during the first step, to private superaccumulators. During the third step, 
inside each processor, private superaccumulators are merged into a single scalar superaccumulator. In 
the fourth level, all scalar superaccumulators are combined together into one single superaccumulator 
accessible by all threads. Finally, the fifth level consists in rounding the global superaccumulator back to 
the target floating-point format in order to produce the correctly rounded result. 
We present implementations of the multi-level algorithm on the whole range of parallel platforms: Intel 
desktop and server processors, Intel Xeon Phi accelerators, and both NVIDIA and AMD GPUs. These 
implementations strive to use all resources of modern processors: SIMD instructions, fused multiply-add, 
and multi-threading on multi-core CPUs and Xeon Phi; local memory and atomic instructions on GPUs. 
We verify the accuracy of our implementations by comparing the computed results with the ones produced 
by the multiple precision MPFR library [9]. 
We show that the numerical reproducibility and bit-perfect accuracy can be achieved at no additional 
cost for large sums that have dynamic ranges of up to 90 orders of magnitude by leveraging arithmetic units 
that are left underused by standard reduction algorithms. Furthermore, we demonstrate that the multi-level 
correct summation outperforms the other recently proposed reproducible summation algorithms – like the 
Demmel’s and Nguyen’s algorithm [8] – and, moreover, it offers correct rounding. More information can 
be found in our technical report [10]. 

### References

1. Bergman, K., al.: Exascale computing study: Technology challenges in achieving exascale systems. DARPA Report (2008) 
2. Whitehead, N., Fit-Florea, A.: Precision & performance: Floating point and IEEE 754 compliance for NVIDIA GPUs. 
Technical report, NVIDIA (2011) 
3. Corden, M.: Differences in floating-point arithmetic between Intel R Xeon R processors and the Intel R Xeon Phi TM 
coprocessor. Technical report, Intel (2013) 
4. Doertel, K.: Best known method: Avoid heterogeneous precision in control flow calculations. Technical report, Intel (2013) 
5. Li, X.S., al.: Design, implementation and testing of extended and mixed precision BLAS. ACM Transactions on 
Mathematical Software 28(2) (2002) 152–205 
6. Hida, Y., Li, X.S., Bailey, D.H.: Algorithms for quad-double precision floating point arithmetic. In: Proc. 15th IEEE 
Symposium on Computer Arithmetic, IEEE Computer Society Press, Los Alamitos, CA, USA (2001) 155–162 
7. Kulisch, U., Snyder, V.: The exact dot product as basic tool for long interval arithmetic. Computing 91(3) (2011) 307–313 
8. Demmel, J., Nguyen, H.D.: Fast reproducible floating-point summation. In: 21st IEEE Symposium on Computer Arithmetic, 
Austin, Texas, USA. (2013) 163–172 
9. Fousse, L., Hanrot, G., Lefevre, V., P ` elissier, P., Zimmermann, P.: MPFR: A multiple-precision binary floating-point library ´ 
with correct rounding. ACM Trans. Math. Softw. 33(2) (2007) 13 http://www.mpfr.org. 
10. Collange, S., Defour, D., Graillat, S., Iakymchuk, R.: Full-Speed Deterministic Bit-Accurate Parallel Floating-Point 
Summation on Multi- and Many-Core Architectures. Technical Report hal-00949355, INRIA, DALI–LIRMM, LIP6 (2014) 
http://hal.archives-ouvertes.fr/hal-00949355/en/. 
2 



# Using accurate arithmetics to improve numerical reproducibility and stability in parallel applications
URL: https://escholarship.org/content/qt5wm5z58d/qt5wm5z58d.pdf?t=p21mk2
Published: 2000-05-08
Author: Yun He, Chris H. Q. Ding

# Using accurate arithmetics to improve numerical reproducibility and stability in parallel applications

International Conference on Supercomputing. Published: 2000-05-08. 25 citations.

## Authors

- Yun He (Lawrence Berkeley National Laboratory): h-index 13; 525 citations
- Chris H. Q. Ding (Lawrence Berkeley National Laboratory): h-index 70; 27,213 citations

## Topics

- Numerical Methods and Algorithms
- Parallel Computing and Optimization Techniques
- Matrix Theory and Algorithms

## Funding

- U.S. Department of Energy
- Office of Science
- National Energy Research Scientific Computing Center

---

# Using Accurate Arithmetics to Improve Numerical Reproducibility and Stability in Parallel Applications

## Abstract

Numerical reproducibility and stability of large scale scientific simulations, especially climate modeling, on distributed memory parallel computers are becoming critical issues. In particular, global summation of distributed arrays is most susceptible to rounding errors, and their propagation and accumulation cause uncertainty in final simulation results. We analyzed several accurate summation methods and found that two methods are particularly effective to improve (ensure) reproducibility and stability: Kahan's self-compensated summation and Bailey's double-double precision summation. We provide an MPI operator MPLSUMDD to work with MPI collective operations to ensure a scalable implementation on large number of processors. The final methods are particularly simple to adopt in practical codes.

## Introduction and Motivation

One of the pressing issues for large scale numerical simulations on high performance distributed memory computers is numerical reproducibility and stability. Due to finite precisions in computer arithmetics, different ordering of computations will lead to slightly different results, the so called rounding errors. As simulation systems become larger, more data variables are involved . . As simulation time becomes longer, teraflops of calculations are involved. All these indicate that accumulated rounding errors could be substantial. One manifestation of this is that final computational results on different computers, and on the same computer but with different number of processors will differ, even though calculations are carried out using double precision (64-bit).

It is important to distinguish between the high precision required in internal consistent numerical calculations and the expected accuracy of the final results. In climate model simulations, for example, the initial conditions and boundary forcings can seldomly be measured more accurately than a few percent. Thus in most situations, we only require 2 decimal digits accuracy in final results. But this does not imply that 2 decimal digits accuracy arithmetic (or 6-7 bits mantissa plus exponents) can be employed during the internal intermediate calculations. In fact, double precision arithmetic is usually required.

In this paper, we are concerned with the numerical reproducibility and stability of the final computational results, and how the improvements in the internal computations could effect the final outcome. Numerical reproducibility and stability are particularly important in long term (years to decades and century long) simulations of global climate models. It is known that there are multiple stable regions in phase space (see Figure 1 ) that the climate system could be attracted to. However, due to the inherent chaotic nature of the numerical algorithms involved, it is feared that slight changes during calculations could bring the system from one regime to another. One common but expensive solution is to run the same model simulation with identical initial conditions with small perturbation at the level far below the observational accuracy for several times, and take the ensemble average. In a scenario climate experiment, first a controlled run of model simulation with standard parameters is produced. Then a sensitivity run of model simulation with slightly changed parameters, say CO 2 concentration, is produced. The difference between these two runs is computed and the particular effect, say the average surface temperature, is discerned. Without numerical stability, the difference between the controlled run and the sensitivity run could be due to the difference in different regimes, not due to the fine difference in input parameters which is the focus of the scenario study.

On distributed memory parallel computer (MPP) platforms, an additional issue is the reproducibility and stability with regard to number of processors utilized in the simulations. One simulation run on 32 processors should produce "same" or "very close" results as the same simulation run on 64 processors. Sometimes, different number of processors could be involved during different periods of a long term (10 simulated years or more) simulation due to computer resources availability, further demanding reproducibility of the simulation.

Numerical reproducibility of the final results are determined by the internal computations during intermediate steps. Obviously, there are a large number of areas involved in the numerical rounding error propagation. In climate models, one major part is the dynamics, i.e., finite difference solution to the primitive equation. On MPP, stencil updates proceed almost identically as in sequential implementation except the update order changes slightly. If the first order time stepping scheme is used, the order remains unchanged.

In barotropic component of an ocean model [6, 17, 19, 22] ' an elliptic equation is solved using a global linear equation via a conjugate gradient method. In atmospheric data assimilation [5, 7] , a correlation equation is also solved via a conjugate gradient (CG) method. The key parameters Ct, f3 calculated through the global summation (dot product between global vectors) appear to be sensitive to the different summation orders on different number of processors. A slight change on the least significant bits will accumulate quickly into the significant bits in Ct, f3 over several iterations, leading to a different CG trajectory in the multi-dimensional space, and a slightly different solution (see, e.g., [21] ). Although the self-correcting nature of the conjugate gradient method ensures that these different solutions on different number of processors are equally correct regarding to solving the linear equation, this inherent difference generating nature could be significant. It is feared that the multiplicative effects on the small differences in each timestep will eventually lead the system into another stable regime (say from C to A in Figure 1 ), instead of merely wondering around the stable regime C (shifting from C1 to C2).

Another example is the spectral transforms used in many atmospheric models [S, 12] , where global summations are very sensitive to the summation order. (In this case, there is no self-correcting mechanism as in the CG method mentioned above.) There are many other parts in climate models where summation of global arrays is used. In general, experience in distributed memory parallel computing indicates global summation appears to be the most sensitive regarding to rounding error, a fact also known in numerical analysis [13] .

One method to resolve the global summation related reproducibility problem is to use serialized implementation, as used in some ocean models [6, 10] . In this scheme, elements of distributed array are sent to one designated processor, and are summed up in a fixed order on the designated processor. The results are then broadcasted back to all the relevant processors. This scheme guarantees the reproducibility but at the extra cost of communication. On large number of processors, the designated processor has to receive P -1 messages, each from other P -1 processors, in a time linear to P. Clearly this scheme does not scale well to large number of processors [The broadcast back phase can use standard hypercube tree algorithm [11 ] , in log(P) time].

Here we look into another approach to achieve reproducibility by reducing rounding errors with more accurate arithmetic. The basic idea is that rounding errors can be reduced very significantly (sometimes eliminated) by using accurate arithmetics. On a computer with infinitely accurate arithmetics, there is no rounding error. A simple and trivial solution is to use higher precision, say 12S-bit precision arithmetics in the relevant data arrays. However, most computer platforms we know do not support 12S-bit precision arithmetic. By reproducibility and stability, we mean that results of the same simulation running on different computers or on same computer but with different number of processors remain close inside one regime, say C1 and C2. (The "exact" or "absolute" reproducibility, i.e., identical numerical results on different computers, or on different number of processors, or even on different compiler versions or optimization levels, is impossible in our view, and is not our goal.) In contrast, non-reproducibility indicates the simulation results change from one regime to another regime on different computers.

The only exception is Cray PVP (SV1, C90) line of computers, where the 128-bit precision is supported and implemented in software, resulting in huge (factor of 10 or more) performance degradation. The real challenge here is to find a simple and practical method that can effectively improve the numerical reproducibility and stability.

In this paper, we examined several accurate summation methods, III particular, the fixed-point and the multi-precision arithmetics, the self-compensated summation (SCS) and doubly-compensated summation (DCS) methods, and the double-double precision arithmetics. We first examined these methods in sequential computer environment, i.e., on a single processor. Next, promising methods found in the sequential environment are examined in the parallel environment. We provide necessary functions to work together with MPI communication library to utilize these accurate methods in parallel environment.

Our main concern in this paper is to find simple and practical methods to improve the numerical reproducibility between runs on different number of processors on the same distributed memory computer, and also between runs on different computers. We approach this task by using more accurate (than standard double precision) methods in some of the key steps in parallel applications. Although the overall final computation results will be undoubtedly more accurate, that is an added benefit, but is not our primary goal.

## Sea Surface Height Data

Sea surface height (SSH) is the first serious difficulty we encountered in an ocean circulation model development [6] . The variable stores the average sea surface height from the model simulation, which can later be compared with satellite data. Repeating the same simulation on different number of processors leads to different results. This difficulty, along with issues mentioned above, motivated this work. This simple problem serves as a good example for the main ideas of global summation in parallel environment. All methods are tested against this SSH data in this paper (We also used synthetic data in this work, and the results are very similar).

The SSH variable is a two-dimensional sea surface volume (integrated sea surface area times sea surface height) distributed among multiple processors. At each time step, the global summation of the sea surface volume of each model grid is needed in order to calculate the average sea surface height. The absolute value of the data itself is very large (in the order of 10 10 to 10 15 ), with different signs, while the result of the global summation is only of order of 1. Running the model in double precision with different number of processors generate very different global summations, ranging from -100 to 100, making the simulation results totally meaningless.

We saved the SSH data from after one-day simulation as our test data. The 2D array is dimensioned as ssh(120, 64), with a total of 7680 double precision (64-bit) numbers. Other sizes and simulation time will not affect the conclusions reported here (Both the codes used here and the SSH data can be downloaded from our website [18] ).

For the 2D SSH array, the most natural way of global summation is to use the following simple codes: do j = 1, 64 ! index for latitude do i = 1, 120 ! index for longitude sum = sum + ssh(i,j) do j = 1, 64 ! index for latitude do i = 1, 120 ! index for longitude sum = sum + ssh(i,j) Code (1) end do end do

## Code (1) end do end do

We call this order the "longitude first" order, the result of summation is 0.67 (see Table 1 ). If we exchange the do i and do j lines, so that elements with different j index (while i index remain fixed) are summed up first (latitude first), we get 34.4, a totally different result! Sometimes in practice, we need to sum up the array in reversed order, such as do i = 120, 1, -1, denoted as "reverse longitude first", the result would change again, to 0.73.

These results are listed in Table 1 . Clearly the results are summation order dependent on the sequential computer. In fact, we do not know what is the exact correct result, until later with other methods: On a distributed memory computer platform, the 2D SSH array is decomposed into many sub domains among multiple processors. On different number of processors, the order of summation is not guaranteed, and the results are not reproducible! The origin of the rounding error is due to finite representation of a floating point number. A simple example explains the idea best. In double precision, the following Fortran statement S = 1.25 X 10 20 + 555.55 -1.25 x 10 20 will get S = 0.0, instead of S = 555.55. The reason is that when compared to 1.25 x 10 20 , 555.55 is negligibly small, or non-representable. In hardware, 555.55 is simply right-shifted out of CPU registers when the first addition is performed. So the intermediate result of the first addition is 1.25 x 10 20 , which is then cancelled exactly in the subtraction step.

The sea surface height data is one of the extreme cases. For most variables, this dependency on summary ordering is less pronounced. However, this error could propagate to higher digits in the following iterations. Our goal is to find an accurate summation scheme that minimizes this rounding error.

## Fixed-Point Arithmetic

The first method we investigate is a fixed point summation without loss of precision. It is a simple method and can be easily implemented (see [18] for implementation details). we wrote a code to first convert double precision floating point numbers of a global array into an array of integers, a db2int 0 function. Depending upon the dynamical range (maximum and minimum) and precision required, the integer representation chooses a proper fixed point (a scale factor) and one or a few integers to represent each floating point numbers.

These integers are then summed up using standard integer arithmetic, (and sum across the multiple processors using MPLREDUCE with MPI..INTEGER data type) and are finally converted back to double precision numbers, rounding off all lower bits which are nonrepresentable in double precision, by using the int2db 0 function. This method is applied to the 3 number addition example and the correct result 8=555.55 is obtained. We applied this method to the 88H data discussed above, and the summation result is L,ssh(i,j) = 0.35798583924770355

i,j (1)

This result remains the same upon changing the summation orders, convincing us that it is the exact result. (The double-double precision discussed later gives the same result.)

This method requires the users to know the dynamical range before calling the db2int 0 conversion routine. A simple way is to find the maximum and minimum magnitudes of the array. Based on this information, an initialization routine will properly determine the scale factor (the fixed point) and the number of integers (32 bits or 64 bits) required to represent the floating point numbers.

In large simulation codes, however, finding the maximum and minimum in a large array distributed over multiple processors before each array summation is quite inconvenient in many situations. We strive to find methods which are simple to adapt in practical large scale coding.

## Multi-Precision Arithmetic

The above fixed-point arithmetic is a simple example of a class of multi-precision arithmetic software packages which carry out numerical calculations at a pre-specified precision [13] . Brent's BMP [3] is the first complete Fortran package on the multi-precision arithmetics offering a complete set of arithmetic operations as well as the evaluation of some constants and special functions. Bailey's MPFUN [2] is a more sophisticated and more efficiently implemented complete package. He used this package to compute 7r to 29 million decimal (suml, errorl) = SCS (error, c) (sum2, error2) = SCS (sum, suml) (sum3, error3) = SCS (sum2, errorl + error2) 3 Fixed-Point Arithmetic

We applied both SCS and DCS to the 2D sea surface height data, using the straight summation in Code (2) . The results are listed in Table 1 , "latitude first SCS", etc. Now all 4 orders give results with agreement on the first significant decimal digit; in fact they are quite close to the correct result in Eq.(l). This indicates very substantial improvements in rounding error reductions during the summations. We also note that DCS does not seem to outperform the much simpler SCS.

## Sensitivity Regarding to Summation Order

To further study the sensitivity regarding to different summation orders and to see further difference in performance between SCS and DeS, we applied a number of different sorting orders on the SSH data. For simplicity, SSH data is treated as a simple 1D array of 7680 double precision numbers.

This 1D array is easily sorted in 6 different ways as explained in Table 2 . They are summed up from the left to right. For an array of all positive numbers, the increasing order would be the best, since the smaller numbers are added first, and they would accumulate large enough not to be rounded off when added with big numbers. But for arrays with mixed positive and negative numbers, the decreasing magnitude order would be the best, especially when the absolute value of the summation is much smaller than the addends due to the cancellation of most addends. We also tried several other orders. The summation results are shown in Table 3 .. From these results we observe that (1) Using straight double precision summation, different sorted orders always lead to different results ranging from -73.6 to 34.4 , similar to those listed in Table that sorting helps reducing the rounding error in SOS and DOS, but not much in the double precision arithmetic. (3) Among the 6 different orders, the one with decreasing magnitude order produces the correct answer of Eq.(l). Intuitively in this order, the numbers with similar magnitude but oppositive signs are added together first, and then the result is added to the accumulation without much loss of precision. This order is the recommended order in summation of large arrays [20, 13] .

From these observations and results in Table 1 , we conclude first that SOS and DOS always give results very close to the correct result (better results when the array is sorted), and show dramatic improvements over the straight double precision summation. Secondly, the differences between DOS and SOS are also very small: when array is sorted, there is no difference (Table 3 ); when array is unsorted, there is small difference (Table 1 ), but no indication that DeS does better than SOS. Therefore, from now on, we will concentrate on the simpler SOS.

So far, we have studied compensated methods that require no extra storage space (except 1-3 temporary buffer space) at the cost of extra additions. Although no exact tight error bounds can .be given, they improve the accuracy very substantially. Another practical approach is to do truly higher precision arithmetic using existing double precision data representation and OPU arithmetic units.

## Double-Double Precision Arithmetic

In double-double precision arithmetics, each floating point number is represented by two double-precision numbers. In effect, the extra bits in the second double precision number are extended mantissa of the first double precision number. The dynamic range of the double-double precision number remains the same as the double precision number. As an analogy to the self-compensated summation discussed above, one may think that the first double precision number as the summation result and the second double precision number as the estimated rounding error. A suite of Fortran 90 compatible codes are developed by Bailey[l] by using Knuth's [15] trick.

We used this double-double precision codes in the sea surface height data summation. It always gives the same correct result of Eq.(l), irrespective of the 9 different summation orders listed in Tables 1 and 3 ; This indicates the extra precisions (about 53 bits) in the double-double representation is highly effective in reducing the round off errors during the summation.

The double-double arithmetic employs slightly more arithmetic steps. The number of additions increases much more than in the self-compensated method. For a single addition, double-double arithmetic requires 11 double precision additions VB. 4 for the SCS. However, on cache-based processor architectures, the increased CPU arithmetic does not slow down calculation as much as the increased memory access required since we use two double precision numbers for one single double-double number. In practice, on wide range of processors, the double-double arithmetic only slows down by a factor of 2 while getting effective double-double precision.

The double-double arithmetics has also increased memory requirements, which is doubled. However, this is not a real problem in today's computers when DRAM is very plentiful. Furthermore, one can implement the basic arithmetic codes in a way that also requires no increase in memory requirement, similar to the self-compensated methods.

## Summation Across Distributed Memory Processors

Among the above methods we have investigated so far, fixed-point/multi-precision and double-double arithmetics always give the same and correct result. However, as pointed out earlier, the fixed-point arithmetic requires the dynamical range of the data array before the summation which is not practical. The true multi-precision packages require too much effort to adopt regarding the conversion of the data format.

The self-compensated summation emerges as a very simple and effective method as it gives results very close to the exact one in the worst case of SSH data in 9 totally different summation orders (Tables 1 and 3 ). The doubly-compensated summation does not show significant improvement in accuracy over SCS but more arithmetic operations are involved. Double-double arithmetic is easy to be implemented. Thus, we will concentrate on only two summation methods in the distributed systems, i.e., the SCS method and double-double precision arithmetics. DCS method can be adopted in same way as SCS.

In distributed memory environment, each processor will first do the summation on a subsection of the global array covered by the processor. One may use the self-compensated method or the double-double precision arithmetics. The results of this local summation are two double precision numbers: (sum, error) in the SCS and (double, double) in doubledouble arithmetic. In both cases, the result can be represented as a single complex number.

The issue here is how to sum up the pair of numbers on each processor in a consistent way to achieve high accuracy. We investigated a number of different approaches and found a unified and consistent approach. Fortunately, we found that the MPLSUMDD operator discussed above can be "directly" applied to the results of SCS method. Therefore the local summation results of SCS on different processors can be added up using MPLREDUCE with the operator MPLSUMDD. It will carry out the double-double precision arithmetic during the intermediate steps with the tree algorithms typically employed in MPLREDUCE. This is sufficient to produce the exactly correct result in a scalable way.

The reason that the results, the (sum, error) pairs, produced by the SCS (and DCS) method, can be used with MPLSUMDD operator is that the error in the (sum, error) pair is exactly the non-representable portion of the double precision number sum [In other words, suppose on an imagined computer, the mantissa has 106 bits (which is effectively the precision offered by the double-double representation) to represent the exact summation result. On the real computer in IEEE format, a double precision number has mantissa of 53 bits. error would be the portion represented by those lower 53 bits beyond the upper 53 bits representable in the IEEE double precision number]. By design, this nonrepresentable portion is exactly the lower double precision number in the double-double number representation. Therefore, (sum, error) is already in the correct double-double representation. This reveals the intimate relationship between SCSmethod and doubledouble arithmetic. This relation between SCS and double-double arithmetic could also be usedin situations other than summation across processors. Suppose we have several subroutines or modules each producing a (sum, error) pair by employing SCS. Then these SCS results can be directly summed up using the double-double arithmetic without loss of precision. This technique will be very useful for maintaining modularity of large simulation codes.

Note that since DCS has the same representation of the final results as the SCS [(sum3, error3) in'Code (3) VS. (sum1, error1) in Code (2)], this relationship holds for DCS too.

In particular, one may use DCS on local summation, and then double-double arithmetic on global summation.

In summary, we found that SCS method can be effectively combined with double-double precision arithmetics to achieve accurate summation on a distributed global array.

## Practical Implications

Our main results are (a) SCS and double-double arithmetic are very effective; (b) The results of SCS are directly in double-double representation; (c) A simple MPLSUMDD can carry out double-double arithmetic consistently during the summation across processors. Together with our experiences in this work and other large scale ocean and atmospheric model codes, we recommend the followi:o.g steps in adopting the accurate arithmetics in real application codes to improve numerical reproducibility and stability:

(1) Select the parts or modules where global summation plays important roles, such as the conjugate gradient solution of the barotropic equations or the spectral transforms. The very simple self-compensated summation can be easily adopted. The double-double arithmetic can also be easily adopted to guarantee the summation accuracy. The results of different modules are summed up using double-double arithmetic. Results on different processors are summed up using MPLREDUCE with MPLSUMDD.

(2) Carry out test runs of the resulting codes on different computer platforms and on different number of processors to see if the numerical stability, especially reproducibility are improved. If the improvements are small in some measure, it might indicate that more parts of the codes should be considered for modification to adopt the SCS. If the improvements are substantial in some measure, either more parts of the codes should be considered for adoption, or the double-double arithmetic should be adopted on the selected codes for further accuracy enhancements.

Adoption of double-double arithmetics generally requires more memory and slight changes of codes. One technique we found useful is to think of both the (sum, error) in SCS and double-double number as a complex number (see our implementations listed in the Appendices r This is conceptually more consistent than simply using two double numbers in a row, and makes the modifications a little easier. As long as addition and subtraction are concerned, they can be carried out simply as complex numbers. Care must be taken, how-ever, when multiplications and divisions are involved, which are fortunately not the major problems here.

We note that there is an effort to develop XBLAS [4] , extended precision BLAS using the double-double precision arithmetics. With this suite of efficient codes, many intermediate results during matrix-vector operations can be promoted to double-double precision, therefore further improve the reproducibility and stability.

Although we studied effects on summation due to sorted orders, and found sorting array does reduce rounding errors in SCS and DCS, we do not see it as a solution to the reproducibility problem: (1) sorting an array is much slower compared to summation; (2) sorting a distributed array across processors is even more time consuming and unnecessarily complicated. As explained, we believe the SCS and double-double arithmetics could effectively resolve the problem.

## Concluding Remarks

We studied the numerical reproducibility and stability issue on scientific applications, especially in climate simulations, on parallel distributed memory computers. We focus on the dominant issue that affects the reproducibility and stability: the global summation of distributed data arrays. We investigated accurate summation methods and found two particular effective methods which can also be easily implemented and scale well to large number of processors.

Our main point here is that numerical reproducibility and stability can be improved substantially by using high accur~cy in some of the key steps in parallel computations. As a result, the final results will be slightly more accurate; This is a welcome benefit, but of secondary consideration. In fact, we do not propose to use higher precision on all parts of a simulation codes, unless it is shown to be absolutely necessary.

To our knowledge, this work is the first syatematic attempt to address the reproducibility from accurate arithmetic approach. Here we used the SSH data as a validation test of the improvement techniques. How well these techniques perform in practical codes when the variables affect dynamics? Are they adequate? All these require further investigations. We plan to examine the spectral transforms in the CCM atmosphere model [8, 12] and conjugate gradient solver in the POP ocean model [22] .

Figure1: An illustrative diagram of several stable regimes centered around A, B, and C in the multi-dimensional phase space at a simulated time far beyond initial period (spin-up). By reproducibility and stability, we mean that results of the same simulation running on different computers or on same computer but with different number of processors remain close inside one regime, say C1 and C2. (The "exact" or "absolute" reproducibility, i.e., identical numerical results on different computers, or on different number of processors, or even on different compiler versions or optimization levels, is impossible in our view, and is not our goal.) In contrast, non-reproducibility indicates the simulation results change from one regime to another regime on different computers.

integer myPE, totPEs, stat (MPl_STATUS_SlZE), ierr integer MPl_SUMDD, itype external DDPDD complex local_sum, global_sum call MPl_lNlT(ierr) call MPl_COMM_RANK( MPl_COMM_WORLD, myPE, ierr ) call MPl_COMM_SlZE( MPl_COMM_WORLD, totPEs, ierr ) C operator MPI_SUMDD is created based on an external function DDPDD. call MPl_OP_CREATE(DDPDD, .TRUE., MPl_SUMDD, ierr) C assume array(n) is the local part of a global distributed array. local_sum = cmplx (0.0,0.0) do i = 1, n call DDPDD (cmplx(array(i), 0.0), local_sum, 1, itype) enddo C add all local_sums on each PE to PEO with MPl_SUMDD. C global_sum is a complex number, represents final (sum, error). call MPl_REDUCE (local_sum, global_sum, 1, MPl_COMPLEX, MPl_SUMDD,& 0, MPI_COMM_WORLD, ierr) call MPl_FlNALIZE(ierr) end C Modification of original codes written by David H. Bailey. C This subroutine computes ddb(i) = dda(i) + ddb(i) subroutine DDPDD (dda, ddb, len, itype) implicit none real*8 e, t1, t2 integer i, len, itype complex*16 dda(len), ddb(len) do i = 1, len c Compute dda + ddb using Knuth's trick. t1 = real(dda(i)) + real(ddb(i)) e = t1 -real(dda(i)) t2 = ((real(ddb(i)) -e) + (real(dda(i)) -(t1 -e))) & +imag(dda(i)) + imag(ddb(i)) c The result is t1 + t2, after normalization. ddb(i) = cmplx ( t1 + t2, t2 -((t1 + t2) -t1) ) enddo end

Results of the Summation in Different Natural Orders with Different Methods in .Double Precision II Order | I Result Latitude First Reverse Latitude First | 34.414768218994141 32.302734375 | " Longitude First | 0.67326545715332031 Reverse Longitude First 0.734375 Latitude First SCS | 0.3823695182800293 Latitude First DCS | 0.3882288932800293 Longitude First SCS | ij.37443733215332031 Longitude First DCS | 0.32560920715332031

1.(2)In all 6 sorted orders (excluding Order 1 which is same as the Latitude Seven Different Orders of the Array Tested for Summation I I Order I Sequential Order I Example | II

Results of the Summation in Different Sorting Orders with Different Methods in Double Precision (Fixed point arithmetic and double-double precision arithmetics always give the same and correct answer: 0.35798583924770355) | , II Order I Normal Double Precision I SCS | I DCS 1 2 | 34.414768218994141 -70.640625 | 0.3823695182800293 0.359375 | 0.3882288932800293 0.359375 | " 3 | -73.015625 | 0.359375 | 0.359375 4 | 13.859375 | 0.359375 | 0.359375 5 | 14.318659648299217 | 0.35798583924770355 0.35798583924770355 6 | -36.254243895411491 | 0.35812444984912872 0.35812444984912872 7 | -66.640625 | 0.359375 | 0.359375

, DCS gives the identical results as SCS does. They are always between 0.358 and 0.359, very close to the real result of 0.358 (less than 0.4% error). This indicates

Results of Adding Sums and Errors Produced from SCS Separately with Different Number of Processors Using MPLREDUCE need to gather them to one processor, and apply the same sorting and SCS summation algorithm. The test results with 2, 4, 8 or 64 processors are 0.35798583924770355, which is correct. However, as discussed in the introduction, this serialized communication method will not scale well to large number of processors. II Processors I Result | II 2 | 0,35798583924770355 4 | 0.35798583924770355 8 | 1.9829858392477036 64 | 2.2822412103414536 processors, we

## References

D H Bailey A Fortran-90 Suite of Double-Double Precision Programs D. H. Bailey. A Fortran-90 Suite of Double-Double Precision Programs. See webpage at http://www.nersc.gov /'" dhb /mpdist /mpdist.html.

Multiprecision Translation and Execution of Fortran Programs D H Bailey ACM Transactions on Mathematical Software 19 3 Sept. 1993 D. H. Bailey. Multiprecision Translation and Execution of Fortran Programs. ACM Transactions on Mathematical Software, vol. 19, no. 3, Sept. 1993 . pp: 288-319.

A Fortran Multiple Precision Arithmetic Package R P Brent ACM Transactions on Mathematical Software 4 1978 R. P. Brent. A Fortran Multiple Precision Arithmetic Package. ACM Transactions on Mathematical Software, Vol. 4, 1978. pp:57-70.

A Reference Implementation for Extended and Mixed Precision BLAS J Demmel X Li D Bailey M Martin J Iskandar A Kapur In preparation J. Demmel, X. Li, D. Bailey, M. Martin, J. Iskandar, and A. Kapur. A Reference Implementation for Extended and Mixed Precision BLAS. In preparation.

A Parallel Climate Data Assimilation Package C H Q Ding R D Ferraro SIAM NEWS November 1996 C. H.Q. Ding and R. D. Ferraro. A Parallel Climate Data Assimilation Package. SIAM NEWS, November 1996. pp:1-12.

Data Organization and I/O in an Ocean Circulation Model C H Q Ding Y He Number LBNL- 43384 Proceedings of Supercomputing'99 Supercomputing'99 November 1999. May 1999 LBL Report C. H.Q. Ding and Y. He. Data Organization and I/O in an Ocean Circulation Model. Proceedings of Supercomputing'99. November 1999. Also LBL Report Number LBNL- 43384, May 1999.

Atmospheric Data Assimilation on Distributed Parallel Supercomputers C H Q Ding P Lyster J Larson J Guo A Da Silva Lecture Notes in Computer Science P Sloot 1401 April 1998 Springer C. H.Q. Ding, P. Lyster, J. Larson, J. Guo, and A. da Silva. Atmospheric Data Assim- ilation on Distributed Parallel Supercomputers. Lecture Notes in Computer Science, V1401, Ed. P. Sloot et al. Springer, April 1998. pp:115-124.

Design and Performance of a Scalable Parallel Community Climate Model J Drake I Foster J Michalakes B Toonen P Worley Parallel Computing (PCCM2) 21 1571 1995 J. Drake, I. Foster, J. Michalakes, B. Toonen, and P. Worley. Design and Performance of a Scalable Parallel Community Climate Model. Parallel Computing (PCCM2), V21, 1571, 1995.

What Every Computer Scientist Should Know About Floating-Point Arithmetic D Goldberg ACM Computing Surveys March 1991 D. Goldberg. What Every Computer Scientist Should Know About Floating-Point Arithmetic. ACM Computing Surveys, March 1991.

The Explicit Free Surface Method in the GFDL Modular Ocean Model S M Griffies R C Pacanowski M Schmidt V Balaji Monthly Weather Review 1999 Submitted to S.M. Griffies, R. C. Pacanowski, M. Schmidt, and V. Balaji. The Explicit Free Surface Method in the GFDL Modular Ocean Model. Submitted to Monthly Weather Review. 1999.

Solving Problems on Concurrent Processors G Fox M Johnson G Lyzenga S Otto J Salmon D Walker 1988 Vollo Prentice Hall Englewood Cliffs, New Jersey G. Fox, M. Johnson, G. Lyzenga, S. Otto, J. Salmon, D. Walker. Solving Problems on Concurrent Processors. Vollo Prentice Hall. Englewood Cliffs, New Jersey. 1988.

Computational Design of NCAR Community Climate Model J J Hack J M Rosinski D L Williamson B A Boville J E True Sdale Parallel Computing 21 1545 1995 J. J. Hack, J. M. Rosinski, D. L. Williamson, B. A. Boville, and J. E. True sdale, Computational Design of NCAR Community Climate Model. Parallel Computing, V21, 1545, 1995.

Accuracy and Stability of Numerical Algorithms N J Higham 1996 SIAM Press Philadelphia, PA N.J. Higham. Accuracy and Stability of Numerical Algorithms. SIAM Press, Philadel- phia, PA, 1996. .

Further Remarks on Reducing Truncation Errors W Kahan Comm. ACM 40 1965 W. Kahan. Further Remarks on Reducing Truncation Errors. Comm. ACM, p.40, 1965.

The Art of Computer Programming D E Knuth 1969 Addisin-Wesley Press 2 Reading, MA Chapter 4 D. E. Knuth. The Art of Computer Programming. Vol 2, Chapter 4, Arithmetic. Addisin-Wesley Press, Reading, MA, 1969.

D Moore Introduction to Computational Science Spring 1999 Rice University Class Notes for CAAM 420 D. Moore. Class Notes for CAAM 420. Introduction to Compu- tational Science, Rice University, Spring 1999. See webpage at http://www .owlnet.rice.edu/'" caam420 / Outline.html.

The NCAR Ocean Model User's Guide, Version 1 The NCAR Ocean Model User's Guide, Version 1.

Parallel Ocean Model Development at NERSC Parallel Ocean Model Development at NERSC. http://www.nersc.gov /research/S CG/ocean real array(n) complex cc, SCS cc = cmplx (0.0,0.0) do i= 1, n cc = SCS (real(cc), imag(cc) + array(i)) enddo SCS_sum = cc end complex function SCS (a, b) real a, b, sum sum = a + b SCS = cmplx (sum, b - (sum - a)) end B. Doubly-Compenstated Summation Method

MOM 3.0 Manual R C Pacanowski S M Griffies September 1999 Princeton, NJ GFDL Ocean Circulation Group ; Geophysical Fluid Dynamics Laboratory R. C. Pacanowski and S. M. Griffies. MOM 3.0 Manual. GFDL Ocean Circulation Group, Geophysical Fluid Dynamics Laboratory, Princeton, NJ, September 1999.

Algorithms for Arbitrary Precision Floating Point Arithmetic D M Priest On Properties of Floating Point Arithmetics: Numerical Stability and the Cost of Accurate Computations 1992 Mathematics Dept., University of California, Berkeley Ph.D. Thesis. D. M. Priest. Algorithms for Arbitrary Precision Floating Point Arithmetic. On Prop- erties of Floating Point Arithmetics: Numerical Stability and the Cost of Accurate Computations. Ph.D. Thesis. Mathematics Dept., University of California, Berkeley. 1992.

W H Press S A Teukolsky W T Vetterling B P Flannery Numerical Recipes in Fortran: the Art of Scientific Computing Cambridge, UK Cambridge University Press 1992 2nd ed W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery. Numerical Recipes in Fortran: the Art of Scientific Computing. 2nd ed. Cambridge University Press, Cam- bridge, UK, 1992.

Parallel Ocean General Circulation Modeling R D Smith J K Dukowicz R C Malone Physica, D 60 38 1992 R. D. Smith, J. K. Dukowicz, and R. C. Malone. Parallel Ocean Gen- eral Circulation Modeling. Physica, D60, 38. 1992. See webpage• at http://www.acl.lanl.gov/climate/models/pop/.

Second International Workshop for Software Engineering and Code Design for Parallel Meteorological and Oceanographic Applications Scottsdale, AZ June 1998 Second International Workshop for Software Engineering and Code Design for Parallel Meteorological and Oceanographic Applications. Scottsdale, AZ, June 1998.

!I~-nr @l'FJ!..4'4m@ fY!)!"4;D Workshop on Numerical Benchmarks for Climate/Ocean/Weather Modeling Community Boulder, CO June 1999 I3 J:iII#lLA'I ~ ~ @b93 ~ ~ 0 m §l#u':i!L@1o ~•mmA ~ Workshop on Numerical Benchmarks for Climate/Ocean/Weather Modeling Commu- nity. Boulder, CO, June 1999 I3;J'"'!I~-nr @l'FJ!..4'4m@ fY!)!"4;D'"'!'ij:g mj;;J:iII#lLA'I ~ ~ @b93 ~ ~ 0 m §l#u':i!L@1o ~•mmA ~

# wide - Rust
URL: https://docs.rs/wide/latest/wide/

wide - Rust

Source 

Expand description

A crate to help you go wide.

This crate provides SIMD-compatible data types.

When possible, explicit SIMD is used with all the math operations here. As a fallback, the fact that all the lengths of a fixed length array are doing the same thing will often make LLVM notice that it should use SIMD instructions to complete the task. In the worst case, the code just becomes totally scalar (though the math is still correct, at least).

## § Masks

SIMD vector masks are per-element booleans, and are represented by SIMD vectors where each element’s value in bits is either all zeros (`false`) or all ones (`true`).

SIMD versions of functions that regularly return `bool` return masks. For example, `f32::is_sign_positive` returns `bool`, and `f32x4::is_sign_positive` returns an `f32x4` that represents a mask. The `select` method can be used to perform a per-element `if` statement over a mask. For example, for this simple scalar code:

```
let x = 1.0_f32;

let result = if x.is_sign_positive() {
    5.0
} else {
    3.0
};

assert_eq!(result, 5.0);
```

This is the SIMD version:

```
let x = f32x4::new([1.0, -1.0, -1.0, 1.0]);

let result = x.is_sign_positive().select(
    f32x4::splat(5.0),
    f32x4::splat(3.0),
);

assert_eq!(result, f32x4::new([5.0, 3.0, 3.0, 5.0]));
```

To select from two values of a downstream type, implement the `Select` trait.

## § Shuffling

Shuffling, also known as swizzling, creates a new SIMD vector by selecting elements from one or more input vectors according to a set of indices.

Single-input shuffling is performed using the `shuffle` method and its variants. Multi-input shuffling is performed by placing the input vectors in an array and calling the corresponding methods from `ShuffleExt`.

Currently, `wide` only supports runtime-index based shuffling:

```
use wide::{f32x4, ShuffleExt, u32x4};

let simd_a = f32x4::new([0.0, 1.0, 2.0, 3.0]);
let simd_b = f32x4::new([100.0, 101.0, 102.0, 103.0]);

let reverse = simd_a.shuffle(u32x4::new([3, 2, 1, 0]));

assert_eq!(reverse, f32x4::new([3.0, 2.0, 1.0, 0.0]));

// Here, indices `0..4` map to `simd_a`, and indices `4..8` map to `simd_b`
let from_two_vectors = [simd_a, simd_b].shuffle(u32x4::new([2, 3, 4, 5]));

assert_eq!(from_two_vectors, f32x4::new([2.0, 3.0, 100.0, 101.0]));
```

## § NaN bit patterns

Operations on SIMD vectors of floats do not make any guarantees about the specific bit-patterns of output NaN values (meaning the sign bit, quiet/signaling bit, and payload). This is unlike standard library operations on float primitives, which do define rules for what NaN bit patterns are returned.

The reason for this is that enforcing guarantees would add substantial overhead to operations, and is generally not worth it.

## § Wrapping semantics

SIMD vectors of integers treat operators as wrapping, as if `Wrapping ` was used. Thus, SIMD vectors do not implement `wrapping_*` functions, because that is the default behavior. This means there are no overflow checks, even in debug builds.

The reason for this is that for most applications where SIMD is appropriate, it is “not a bug” to wrap, and even debug builds are unlikely to tolerate the loss of performance.

This “no panicking” approach extends to more than just integer overflows. It is also true for things like `f32x4::clamp`. Even though `f32::clamp` panics for invalid inputs, the SIMD version does not, because it may be used with per-element branching, where invalid elements get discarded later by `select`.

## § Casting

The SIMD types implement the `bytemuck::Pod` trait, which means that it is possible to do bitwise casts between SIMD types of the same size with the `bytemuck::cast()` function and others. `bytemuck` is re-exported by this crate for convenience.

This typically does not have much, if any, runtime overhead in optimized builds.

## § Feature flags

- `std`: This causes the feature to link to `std`. 

- Currently this just improves the performance of `sqrt` when an explicit SIMD `sqrt` isn’t available.

## Re-exports§

`pub use bytemuck;`

## Structs§

f32x4
: A SIMD vector with four elements of type `f32`.
f32x8
: A SIMD vector with eight elements of type `f32`.
f32x16
: A SIMD vector with 16 elements of type `f32`.
f64x2
: A SIMD vector with two elements of type `f64`.
f64x4
: A SIMD vector with four elements of type `f64`.
f64x8
: A SIMD vector with eight elements of type `f64`.
i8x16
: A SIMD vector with 16 elements of type `i8`.
i8x32
: A SIMD vector with 32 elements of type `i8`.
i8x64
: A SIMD vector with 64 elements of type `i8`.
i16x8
: A SIMD vector with eight elements of type `i16`.
i16x16
: A SIMD vector with 16 elements of type `i16`.
i16x32
: A SIMD vector with 32 elements of type `i16`.
i32x4
: A SIMD vector with four elements of type `i32`.
i32x8
: A SIMD vector with eight elements of type `i32`.
i32x16
: A SIMD vector with 16 elements of type `i32`.
i64x2
: A SIMD vector with two elements of type `i64`.
i64x4
: A SIMD vector with four elements of type `i64`.
i64x8
: A SIMD vector with eight elements of type `i64`.
u8x16
: A SIMD vector with 16 elements of type `u8`.
u8x32
: A SIMD vector with 32 elements of type `u8`.
u8x64
: A SIMD vector with 64 elements of type `u8`.
u16x8
: A SIMD vector with eight elements of type `u16`.
u16x16
: A SIMD vector with 16 elements of type `u16`.
u16x32
: A SIMD vector with 32 elements of type `u16`.
u32x4
: A SIMD vector with four elements of type `u32`.
u32x8
: A SIMD vector with eight elements of type `u32`.
u32x16
: A SIMD vector with 16 elements of type `u32`.
u64x2
: A SIMD vector with two elements of type `u64`.
u64x4
: A SIMD vector with four elements of type `u64`.
u64x8
: A SIMD vector with eight elements of type `u64`.

## Traits§

AlignTo
: A trait for SIMD variants of `align_to` functions.
CmpEq

Deprecated
: A deprecated trait for the `simd_eq` function.
CmpGe

Deprecated
: A deprecated trait for the `simd_ge` function.
CmpGt

Deprecated
: A deprecated trait for the `simd_gt` function.
CmpLe

Deprecated
: A deprecated trait for the `simd_le` function.
CmpLt

Deprecated
: A deprecated trait for the `simd_lt` function.
CmpNe

Deprecated
: A deprecated trait for the `simd_ne` function.
Select
: A trait for lanewise SIMD selection.
Shuffle

Ext
: An extension trait implemented for arrays of SIMD vectors, which provides shuffling from multiple input vectors.

# Lokathor/wide
URL: https://github.com/Lokathor/wide

# Lokathor/wide

A crate to help you go wide. By which I mean use SIMD stuff.

- Stars: 558
- Forks: 61
- Watchers: 558
- Open issues: 15
- License: Apache License 2.0
- Homepage: https://docs.rs/wide
- Default branch: main
- Created: 2019-09-21T23:19:39Z

## Languages

- Rust

## Topics

- rust
- simd
- zlib-license

## Top Contributors

- Lokathor (294 contributions)
- Noam2Stein (46 contributions)
- mcroomp (31 contributions)
- CryZe (8 contributions)
- ronniec95 (8 contributions)
- waywardmonkeys (6 contributions)
- smu160 (5 contributions)
- RazrFalcon (4 contributions)
- tower120 (3 contributions)
- Shnatsel (3 contributions)

---

## README

License:Zlib
Minimum Rust Version
crates.io
docs.rs

# wide

A crate to help you go wide.

Specifically, this has portable "wide" data types that do their best to be SIMD when possible. It's a near drop-in replacement for std::simd.

On `x86`, `x86_64`, `wasm32` and `aarch64 neon` this is implemented with explicit
intrinsic usage (via safe_arch), and on other
architectures this is done by carefully writing functions so that LLVM hopefully
does the right thing. When Rust stabilizes more explicit intrinsics then they
can go into `safe_arch` and then they can get used here.

## Enabling SIMD instructions in your build

### Aarch64 (64-bit ARM) 

Aarch64 always enables the NEON extension, so `wide` can always take advantage of SIMD on this platform.

### WASM

SIMD is an optional extension for WASM, but it is supported by all modern browsers.

To enable SIMD in your build you need to set `RUSTFLAGS="-C target-feature=+simd128"`, e.g.:
```
RUSTFLAGS="-C target-feature=+simd128" cargo build --target wasm32-wasip1
```

### x86

Rust i686 and x86_64 targets guarantee only the presence of basic operations on 128-bit vectors (SSE2). If you need anything else, you need to explicitly enable the relevant SIMD extensions at build time. For example, this will use all SIMD extensions available on your CPU:
```
RUSTFLAGS='-C target-cpu=native' cargo build --release
```
However, attempting to use an instruction that is not supported by the CPU will crash the program or lead to undefined behavior. Therefore distributing binaries built with SIMD extensions enabled is not recommended.

**Note:** `wide` only supports detecting the available SIMD extensions at build time. Runtime feature detection via `is_x86_feature_detected!` or crates like multiversion do not work with `wide`.

## Rust Version Policy

* The `rust-version` entry of the crate's `Cargo.toml` will be kept accurate to
 the required Rust compiler version.
* A bump in `rust-version` will be released as a change in either the major or
 minor crate version number, but never as part of a patch release. This way,
 users stuck on an old toolchain can always get necessary patch updates for
 their major.minor version of the crate.
* If your build uses Resolver 3 (or later) this will be fine. If you're using a
 Resolver earlier than 3 then **you are responsible** for pinning a maximum
 crate version when you're using an old Rust version.


# wide
URL: https://crates.io/crates/wide

# wide

A crate to help you go wide.

- Version: 1.7.1
- Repository: https://github.com/Lokathor/wide
- Total downloads: 83488228
- Recent downloads: 22277669
- Dependents: 387
- Created: 2019-09-21T19:03:53.121747Z
- Updated: 2026-09-14T17:06:02.853323Z

License: Zlib OR Apache-2.0 OR MIT

MSRV: 1.89

## Keywords

- simd
- wide
- lokathor

## Categories

- Data structures
- Hardware support

## Owners

- Lokathor (Lokathor)

## Dependencies

| Crate | Req | Optional |
| --- | --- | --- |
| bytemuck | ^1.24.0 | no |
| safe_arch | ^1.2.0 | no |
| safe_arch | ^1.2.0 | no |
| serde_core | ^1 | yes |

## Dev Dependencies

| Crate | Req |
| --- | --- |
| bincode | ^1.3.3 |
| criterion | ^0.7.0 |

## Features

- std
- default -> std
- serde -> dep:serde_core

## Version History

| Version | Published | Downloads | Yanked |
| --- | --- | --- | --- |
| 1.7.1 | 2026-09-14T17:06:02.853323Z | 1339125 | no |
| 1.7.0 | 2026-08-27T16:29:07.258913Z | 711246 | no |
| 1.6.1 | 2026-08-07T21:07:07.622946Z | 880172 | no |
| 1.6.0 | 2026-07-30T16:19:13.996593Z | 238819 | yes |
| 1.5.0 | 2026-06-05T17:34:52.763785Z | 2576259 | no |
| 1.4.0 | 2026-05-07T17:44:11.822697Z | 877508 | no |
| 1.3.0 | 2026-04-12T19:29:34.755352Z | 241339 | no |
| 1.2.0 | 2026-03-14T19:06:28.834775Z | 159262 | no |
| 1.1.1 | 2025-12-22T00:41:15.643481Z | 525352 | no |
| 1.1.0 | 2025-12-12T00:14:41.752706Z | 21631 | no |
| 1.0.3 | 2025-12-12T00:09:17.512498Z | 58 | no |
| 1.0.2 | 2025-12-01T01:15:41.312459Z | 34120 | no |
| 1.0.1 | 2025-12-01T00:43:20.895638Z | 179 | no |
| 0.8.3 | 2025-11-16T02:07:52.251370Z | 970583 | no |
| 0.8.2 | 2025-11-08T05:25:42.423112Z | 5589 | no |
| 0.8.1 | 2025-10-09T01:33:42.651245Z | 18809 | no |
| 0.8.0 | 2025-10-03T20:34:56.221405Z | 2168 | no |
| 1.0.0 | 2025-08-26T22:17:15.283206Z | 392 | yes |
| 0.7.34 | 2025-08-26T16:47:00.195330Z | 24692 | yes |
| 0.7.33 | 2025-06-21T04:19:33.196798Z | 40096017 | no |

---

## README

 
 
 
 
 wide 
 A crate to help you go wide. 
 Specifically, this has portable "wide" data types that do their best to be SIMD when possible. It's a near drop-in replacement for std::simd. 
 On x86, x86_64, wasm32 and aarch64 neon this is implemented with explicit
intrinsic usage (via safe_arch), and on other
architectures this is done by carefully writing functions so that LLVM hopefully
does the right thing. When Rust stabilizes more explicit intrinsics then they
can go into safe_arch and then they can get used here. 
 Enabling SIMD instructions in your build 
 Aarch64 (64-bit ARM) 
 Aarch64 always enables the NEON extension, so wide can always take advantage of SIMD on this platform. 
 WASM 
 SIMD is an optional extension for WASM, but it is supported by all modern browsers. 
 To enable SIMD in your build you need to set RUSTFLAGS="-C target-feature=+simd128", e.g.: 
 RUSTFLAGS="-C target-feature=+simd128" cargo build --target wasm32-wasip1
 
 x86 
 Rust i686 and x86_64 targets guarantee only the presence of basic operations on 128-bit vectors (SSE2). If you need anything else, you need to explicitly enable the relevant SIMD extensions at build time. For example, this will use all SIMD extensions available on your CPU: 
 RUSTFLAGS='-C target-cpu=native' cargo build --release
 
 However, attempting to use an instruction that is not supported by the CPU will crash the program or lead to undefined behavior. Therefore distributing binaries built with SIMD extensions enabled is not recommended. 
 Note: wide only supports detecting the available SIMD extensions at build time. Runtime feature detection via is_x86_feature_detected! or crates like multiversion do not work with wide. 
 Rust Version Policy 
 
 The rust-version entry of the crate's Cargo.toml will be kept accurate to
the required Rust compiler version. 
 A bump in rust-version will be released as a change in either the major or
minor crate version number, but never as part of a patch release. This way,
users stuck on an old toolchain can always get necessary patch updates for
their major.minor version of the crate. 
 If your build uses Resolver 3 (or later) this will be fine. If you're using a
Resolver earlier than 3 then you are responsible for pinning a maximum
crate version when you're using an old Rust version. 
 


# pulp
URL: https://crates.io/crates/pulp

# pulp

safe generic simd

- Version: 0.22.3
- Repository: https://github.com/sarah-quinones/pulp/
- Total downloads: 31627014
- Recent downloads: 15359348
- Dependents: 80
- Created: 2022-10-07T05:11:56.244076Z
- Updated: 2026-06-20T00:52:15.348522Z

License: MIT

## Keywords

- simd

## Owners

- sarah-quinones (sarah quiñones)

## Dependencies

| Crate | Req | Optional |
| --- | --- | --- |
| bytemuck | ^1.15 | no |
| cfg-if | ^1.0.0 | no |
| libm | ^0.2 | no |
| num-complex | ^0.4.4 | no |
| paste | ^1 | no |
| pulp-wasm-simd-flag | ^0.1.1 | no |
| raw-cpuid | ^11.5.0 | no |
| reborrow | ^0.5 | no |
| pulp-macro | ^0.1.1 | yes |

## Dev Dependencies

| Crate | Req |
| --- | --- |
| aligned-vec | ^0.6.0 |
| assert_approx_eq | ^1.1.0 |
| criterion | ^0.5.0 |
| diol | ^0.8.3 |
| rand | ^0.8.5 |

## Build Dependencies

| Crate | Req |
| --- | --- |
| version_check | ^0.9.5 |

## Features

- x86-v3
- x86-v4 -> bytemuck/avx512_simd
- macro -> dep:pulp-macro
- std
- nightly -> bytemuck/nightly_stdsimd
- relaxed-simd -> pulp-wasm-simd-flag/relaxed-simd
- default -> std, x86-v3, relaxed-simd

## Version History

| Version | Published | Downloads | Yanked |
| --- | --- | --- | --- |
| 0.22.3 | 2026-06-20T00:52:15.348522Z | 11435157 | no |
| 0.22.2 | 2025-11-15T01:23:36.430471Z | 5109550 | no |
| 0.22.1 | 2025-11-14T14:47:24.045678Z | 1075 | no |
| 0.22.0 | 2025-11-14T12:21:03.084114Z | 1597 | yes |
| 0.21.5 | 2025-04-28T21:23:08.127451Z | 8227190 | no |
| 0.21.4 | 2025-01-14T11:46:56.398181Z | 594037 | no |
| 0.21.3 | 2025-01-09T18:25:17.475628Z | 2774 | yes |
| 0.21.2 | 2025-01-09T18:19:02.196366Z | 638 | yes |
| 0.21.1 | 2025-01-04T10:44:41.246592Z | 4895 | yes |
| 0.21.0 | 2024-12-13T23:13:24.141160Z | 2434 | yes |
| 0.20.1 | 2024-11-29T22:04:38.502194Z | 74299 | no |
| 0.20.0 | 2024-11-29T12:09:12.744227Z | 810 | no |
| 0.19.7 | 2024-11-29T12:07:47.877568Z | 1547 | no |
| 0.19.6 | 2024-11-22T17:28:47.829054Z | 868 | no |
| 0.19.5 | 2024-11-16T14:50:33.837270Z | 988 | no |
| 0.19.4 | 2024-11-13T07:22:02.107349Z | 784 | no |
| 0.19.3 | 2024-11-13T07:04:45.813865Z | 774 | no |
| 0.19.2 | 2024-11-12T23:10:58.387623Z | 834 | no |
| 0.19.1 | 2024-11-10T02:02:18.446820Z | 757 | yes |
| 0.19.0 | 2024-11-09T15:49:10.472012Z | 811 | yes |

---

## README

 pulp is a safe abstraction over SIMD instructions, that allows you to write a function once
and dispatch to equivalent vectorized versions based on the features detected at runtime. 
 
 
 Autovectorization example 
 use pulp::Arch;
fn main(){
 let mut v = (0..1000).map(|i| i as f64).collect::<Vec<_>>();
 let arch = Arch::new();

 arch.dispatch(|| {
 for x in &mut v {
 *x *= 2.0;
 }
 });

 for (i, x) in v.into_iter().enumerate() {
 assert_eq!(x, 2.0 * i as f64);
 }
}
 
 Manual vectorization example 
 use pulp::{Arch, Simd, WithSimd};

struct TimesThree<'a>(&'a mut [f64]);
impl<'a> WithSimd for TimesThree<'a> {
 // No output, the input is modified in place to save time allocating a new vector
 type Output = ();

 #[inline(always)]
 fn with_simd<S: Simd>(self, simd: S) -> Self::Output {
 let v = self.0;
 // the tail is the remainder left after allocating v into simd vectors
 // len(tail) = len(v) % simd_vector_length
 let (head, tail) = S::as_mut_simd_f64s(v);

 // fill the simd vectors with 3.0
 let three = simd.splat_f64s(3.0);

 for x in head {
 *x = simd.mul_f64s(three, *x);
 }
 // the tail is not loaded into simd vectors hence non-simd operations are used
 for x in tail {
 *x = *x * 3.0;
 }
 }
}
fn main() {
 let mut v = (0..1000).map(|i| i as f64).collect::<Vec<_>>();
 let arch = Arch::new();
 arch.dispatch(TimesThree(&mut v)); // dynamically dispatch the function to the correct simd implementation
 for (i, x) in v.into_iter().enumerate() {
 assert_eq!(x, 3.0 * i as f64);
 }
}
 
 Less boilerplate using pulp::with_simd 
 Only available with the macro feature. 
 Requires the first non-lifetime generic parameter, as well as the function's
first input parameter to be the SIMD type. 
 use pulp::Simd;

// the macro creates a `sum` function
#[pulp::with_simd(sum = pulp::Arch::new())]
#[inline(always)]
fn sum_with_simd<'a, S: Simd>(simd: S, v: &'a mut [f64]) {
 let (head, tail) = S::as_mut_simd_f64s(v);

 // fill the simd vectors with 3.0
 let three = simd.splat_f64s(3.0);

 for x in head {
 *x = simd.mul_f64s(three, *x);
 }

 for x in tail {
 *x = *x * 3.0;
 }
}
fn main() {
 let mut v = (0..1000).map(|i| i as f64).collect::<Vec<_>>();
 sum(&mut v);

 for (i, x) in v.into_iter().enumerate() {
 assert_eq!(x, 3.0 * i as f64);
 }
}
 


# rayon
URL: https://crates.io/crates/rayon

# rayon

Simple work-stealing parallelism for Rust

- Version: 1.12.0
- Repository: https://github.com/rayon-rs/rayon
- Docs: https://docs.rs/rayon/
- Total downloads: 608358839
- Recent downloads: 143437345
- Dependents: 11839
- Created: 2015-12-10T22:38:20.637638Z
- Updated: 2026-04-14T00:56:56.454086Z

License: MIT OR Apache-2.0

MSRV: 1.80

## Keywords

- concurrency
- parallel
- thread
- performance
- join

## Categories

- Concurrency

## Owners

- cuviper (Josh Stone)
- nikomatsakis (Niko Matsakis)

## Dependencies

| Crate | Req | Optional |
| --- | --- | --- |
| either | ^1 | no |
| rayon-core | ^1.13.0 | no |
| wasm_sync | ^0.1.0 | yes |

## Dev Dependencies

| Crate | Req |
| --- | --- |
| rand | ^0.9 |
| rand_xorshift | ^0.4 |

## Features

- web_spin_lock -> dep:wasm_sync, rayon-core/web_spin_lock

## Version History

| Version | Published | Downloads | Yanked |
| --- | --- | --- | --- |
| 1.12.0 | 2026-04-14T00:56:56.454086Z | 141013116 | no |
| 1.11.0 | 2025-08-12T23:22:16.331655Z | 131381821 | no |
| 1.10.0 | 2024-03-24T05:24:47.903463Z | 166389578 | no |
| 1.9.0 | 2024-02-27T23:38:14.579401Z | 10163482 | no |
| 1.8.1 | 2024-01-17T17:56:20.488323Z | 9256157 | no |
| 1.8.0 | 2023-09-20T21:46:04.332374Z | 24246888 | no |
| 1.7.0 | 2023-03-04T00:23:26.366201Z | 42852431 | no |
| 1.6.1 | 2022-12-09T23:26:48.216004Z | 12391707 | no |
| 1.6.0 | 2022-11-18T21:10:20.972487Z | 2104310 | no |
| 1.5.3 | 2022-05-13T23:59:21.179941Z | 18450069 | no |
| 1.5.2 | 2022-04-14T00:47:12.164982Z | 3492054 | no |
| 1.5.1 | 2021-05-18T20:10:14.364810Z | 21169047 | no |
| 1.5.0 | 2020-10-21T23:14:56.328049Z | 8507953 | no |
| 1.4.1 | 2020-09-29T22:30:03.510895Z | 624034 | no |
| 1.4.0 | 2020-08-24T21:17:44.175241Z | 941711 | no |
| 1.3.1 | 2020-06-15T18:51:25.698108Z | 2306329 | no |
| 1.3.0 | 2019-12-22T00:53:46.622895Z | 3539749 | no |
| 1.2.1 | 2019-11-21T00:42:30.857891Z | 475788 | no |
| 1.2.0 | 2019-08-31T00:51:55.048189Z | 1702994 | no |
| 1.1.0 | 2019-06-13T01:08:27.339995Z | 1128029 | no |

---

## README

 Rayon 
 
 
 
 
 Rayon is a data-parallelism library for Rust. It is extremely
lightweight and makes it easy to convert a sequential computation into
a parallel one. It also guarantees data-race freedom. (You may also
enjoy this blog post about Rayon, which gives more background
and details about how it works, or this video, from the Rust
Belt Rust conference.) Rayon is
 available on crates.io, and
 API documentation is available on docs.rs. 
 Parallel iterators and more 
 Rayon makes it drop-dead simple to convert sequential iterators into
parallel ones: usually, you just change your foo.iter() call into
 foo.par_iter(), and Rayon does the rest: 
 use rayon::prelude::*;
fn sum_of_squares(input: &[i32]) -> i32 {
 input.par_iter() // <-- just change that!
 .map(|&i| i * i)
 .sum()
}
 
 Parallel iterators take care of deciding how to divide your data
into tasks; it will dynamically adapt for maximum performance. If you
need more flexibility than that, Rayon also offers the join and
 scope functions, which let you create parallel tasks on your own.
For even more control, you can create custom thread pools rather than
using Rayon's default, global thread pool. 
 No data races 
 You may have heard that parallel execution can produce all kinds of
crazy bugs. Well, rest easy. Rayon's APIs all guarantee data-race
freedom, which generally rules out most parallel bugs (though not
all). In other words, if your code compiles, it typically does the
same thing it did before. 
 For the most, parallel iterators in particular are guaranteed to
produce the same results as their sequential counterparts. One caveat:
If your iterator has side effects (for example, sending methods to
other threads through a Rust channel or writing to disk), those side
effects may occur in a different order. Note also that, in some cases,
parallel iterators offer alternative versions of the sequential
iterator methods that can have higher performance. 
 Using Rayon 
 Rayon is available on crates.io. The
recommended way to use it is to add a line into your Cargo.toml such
as: 
 [dependencies]
rayon = "1.12"
 
 To use the parallel iterator APIs, a number of traits have to be in
scope. The easiest way to bring those things into scope is to use the
 Rayon prelude. In
each module where you would like to use the parallel iterator APIs,
just add: 
 use rayon::prelude::*;
 
 Rayon currently requires rustc 1.80.0 or greater. 
 Usage with WebAssembly 
 By default, when building to WebAssembly, Rayon will treat it as any
other platform without multithreading support and will fall back to
sequential iteration. This allows existing code to compile and run
successfully with no changes necessary, but it will run slower as it
will only use a single CPU core. 
 You can build Rayon-based projects with proper multithreading support
for the Web, but you'll need an adapter and some project configuration
to account for differences between WebAssembly threads and threads on
the other platforms. 
 Check out the
 wasm-bindgen-rayon 
docs for more details. 
 Contribution 
 Rayon is an open source project! If you'd like to contribute to Rayon,
check out
 the list of "help wanted" issues.
These are all (or should be) issues that are suitable for getting
started, and they generally include a detailed set of instructions for
what to do. Please ask questions if anything is unclear! Also, check
out the
 Guide to Development 
page on the wiki. Note that all code submitted in PRs to Rayon is
assumed to
 be licensed under Rayon's dual MIT/Apache 2.0 licensing. 
 Quick demo 
 To see Rayon in action, check out the rayon-demo directory, which
includes a number of demos of code using Rayon. For example, run this
command to get a visualization of an N-body simulation. To see the
effect of using Rayon, press s to run sequentially and p to run in
parallel. 
 > cd rayon-demo
> cargo run --release -- nbody visualize
 
 For more information on demos, try: 
 > cd rayon-demo
> cargo run --release -- --help
 
 Other questions? 
 See the Rayon FAQ. 
 License 
 Rayon is distributed under the terms of both the MIT license and the
Apache License (Version 2.0). See LICENSE-APACHE and
 LICENSE-MIT for details. Opening a pull request is
assumed to signal agreement with these licensing terms. 


# ThreadPoolBuilder in rayon - Rust
URL: https://docs.rs/rayon/1.12.0/rayon/struct.ThreadPoolBuilder.html

ThreadPoolBuilder in rayon - Rust

Skip to main content

# Struct ThreadPoolBuilder Copy item path

Source

```
pub struct ThreadPoolBuilder<S = DefaultSpawn> { /* private fields */ }
```

Expand description

Used to create a new ThreadPool or to configure the global rayon thread pool.

### §Creating a ThreadPool

The following creates a thread pool with 22 threads.

```
let pool = rayon::ThreadPoolBuilder::new().num_threads(22).build().unwrap();
```

To instead configure the global thread pool, use build_global():

```
rayon::ThreadPoolBuilder::new().num_threads(22).build_global().unwrap();
```

## Implementations§

§

### impl ThreadPoolBuilder

struct rayon::ThreadPoolBuilder

#### pub fn new() -> ThreadPoolBuilder

struct rayon::ThreadPoolBuilder

Creates and returns a valid rayon thread pool builder, but does not initialize it.

§

struct rayon::ThreadPoolBuilder

### impl ThreadPoolBuilder where S: ThreadSpawn,

Note: the`S: ThreadSpawn` constraint is an internal implementation detail for the default spawn and those set by`spawn_handler`.

#### pub fn build(self) -> Result<ThreadPool, ThreadPoolBuildError>

Creates a new`ThreadPool` initialized using this configuration.

#### pub fn build_global(self) -> Result<(), ThreadPoolBuildError>

Initializes the global thread pool. This initialization is optional. If you do not call this function, the thread pool will be automatically initialized with the default configuration. Calling`build_global` is not recommended, except in two scenarios:

- You wish to change the default configuration.
- You are running a benchmark, in which case initializing may yield slightly more consistent results, since the worker threads will already be ready to go even in the first iteration. But this cost is minimal.

Initialization of the global thread pool happens exactly once. Once started, the configuration cannot be changed. Therefore, if you call`build_global` a second time, it will return an error. An`Ok` result indicates that this is the first initialization of the thread pool.

§

### impl ThreadPoolBuilder

struct rayon::ThreadPoolBuilder

enum core::result::Result struct rayon::ThreadPoolBuildError

#### pub fn build_scoped<W, F, R>( self, wrapper: W, with_pool: F, ) -> Result<R, ThreadPoolBuildError>where W: Fn(ThreadBuilder) + Sync, F: FnOnce(&ThreadPool) -> R,

Creates a scoped`ThreadPool` initialized using this configuration.

This is a convenience function for building a pool using std::thread::scope to spawn threads in a spawn_handler. The threads in this pool will start by calling`wrapper`, which should do initialization and continue by calling`ThreadBuilder::run()`.

##### §Examples

A scoped pool may be useful in combination with scoped thread-local variables.

```

scoped_tls::scoped_thread_local!(static POOL_DATA: Vec<i32>);

fn main() -> Result<(), rayon::ThreadPoolBuildError> {
    let pool_data = vec![1, 2, 3];

    // We haven't assigned any TLS data yet.
    assert!(!POOL_DATA.is_set());

    rayon::ThreadPoolBuilder::new()
        .build_scoped(
            // Borrow `pool_data` in TLS for each thread.
            |thread| POOL_DATA.set(&pool_data, || thread.run()),
            // Do some work that needs the TLS data.
            |pool| pool.install(|| assert!(POOL_DATA.is_set())),
        )?;

    // Once we've returned, `pool_data` is no longer borrowed.
    drop(pool_data);
    Ok(())
}
```

§

### impl ThreadPoolBuilder 

struct rayon::ThreadPoolBuilder

struct rayon::ThreadPoolBuilder

#### pub fn spawn_handler (self, spawn: F) -> ThreadPoolBuilder<CustomSpawn >where F: FnMut(ThreadBuilder) -> Result<(), Error>,

Sets a custom function for spawning threads.

Note that the threads will not exit until after the pool is dropped. It is up to the caller to wait for thread termination if that is important for any invariants. For instance, threads created in std::thread::scope will be joined before that scope returns, and this will block indefinitely if the pool is leaked. Furthermore, the global thread pool doesn’t terminate until the entire process exits!

##### §Examples

A minimal spawn handler just needs to call`run()` from an independent thread.

```
fn main() -> Result<(), rayon::ThreadPoolBuildError> {
    let pool = rayon::ThreadPoolBuilder::new()
        .spawn_handler(|thread| {
            std::thread::spawn(|| thread.run());
            Ok(())
        })
        .build()?;

    pool.install(|| println!("Hello from my custom thread!"));
    Ok(())
}
```

The default spawn handler sets the name and stack size if given, and propagates any errors from the thread builder.

```
fn main() -> Result<(), rayon::ThreadPoolBuildError> {
    let pool = rayon::ThreadPoolBuilder::new()
        .spawn_handler(|thread| {
            let mut b = std::thread::Builder::new();
            if let Some(name) = thread.name() {
                b = b.name(name.to_owned());
            }
            if let Some(stack_size) = thread.stack_size() {
                b = b.stack_size(stack_size);
            }
            b.spawn(|| thread.run())?;
            Ok(())
        })
        .build()?;

    pool.install(|| println!("Hello from my fully custom thread!"));
    Ok(())
}
```

This can also be used for a pool of scoped threads like crossbeam::scope, or std::thread::scope introduced in Rust 1.63, which is encapsulated in build_scoped.

```
fn main() -> Result<(), rayon::ThreadPoolBuildError> {
    std::thread::scope(|scope| {
        let pool = rayon::ThreadPoolBuilder::new()
            .spawn_handler(|thread| {
                let mut builder = std::thread::Builder::new();
                if let Some(name) = thread.name() {
                    builder = builder.name(name.to_string());
                }
                if let Some(size) = thread.stack_size() {
                    builder = builder.stack_size(size);
                }
                builder.spawn_scoped(scope, || {
                    // Add any scoped initialization here, then run!
                    thread.run()
                })?;
                Ok(())
            })
            .build()?;

        pool.install(|| println!("Hello from my custom scoped thread!"));
        Ok(())
    })
}
```

struct rayon::ThreadPoolBuilder

#### pub fn thread_name (self, closure: F) -> ThreadPoolBuilder where F: FnMut(usize) -> String + 'static,

Sets a closure which takes a thread index and returns the thread’s name.

#### pub fn num_threads(self, num_threads: usize) -> ThreadPoolBuilder 

Sets the number of threads to be used in the rayon thread pool.

If you specify a non-zero number of threads using this function, then the resulting thread pools are guaranteed to start at most this number of threads.

If`num_threads` is 0, or you do not call this function, then the Rayon runtime will select the number of threads automatically. At present, this is based on the`RAYON_NUM_THREADS` environment variable (if set), or the number of logical CPUs (otherwise). In the future, however, the default behavior may change to dynamically add or remove threads as needed.

Future compatibility warning: Given the default behavior may change in the future, if you wish to rely on a fixed number of threads, you should use this function to specify that number. To reproduce the current default behavior, you may wish to use std::thread::available_parallelism to query the number of CPUs dynamically.

Old environment variable:`RAYON_NUM_THREADS` is a one-to-one replacement of the now deprecated`RAYON_RS_NUM_CPUS` environment variable. If both variables are specified,`RAYON_NUM_THREADS` will be preferred.

#### pub fn use_current_thread(self) -> ThreadPoolBuilder 

struct rayon::ThreadPoolBuilder

Use the current thread as one of the threads in the pool.

The current thread is guaranteed to be at index 0, and since the thread is not managed by rayon, the spawn and exit handlers do not run for that thread.

Note that the current thread won’t run the main work-stealing loop, so jobs spawned into the thread pool will generally not be picked up automatically by this thread unless you yield to rayon in some way, like via yield_now(), yield_local(), or scope().

##### §Local thread pools

Using this in a local thread pool means the registry will be leaked. In future versions there might be a way of cleaning up the current-thread state.

struct rayon::ThreadPoolBuilder

#### pub fn panic_handler (self, panic_handler: H) -> ThreadPoolBuilder where H: Fn(Box) + Send + Sync + 'static,

Normally, whenever Rayon catches a panic, it tries to propagate it to someplace sensible, to try and reflect the semantics of sequential execution. But in some cases, particularly with the`spawn()` APIs, there is no obvious place where we should propagate the panic to. In that case, this panic handler is invoked.

If no panic handler is set, the default is to abort the process, under the principle that panics should not go unobserved.

If the panic handler itself panics, this will abort the process. To prevent this, wrap the body of your panic handler in a call to`std::panic::catch_unwind()`.

#### pub fn stack_size(self, stack_size: usize) -> ThreadPoolBuilder 

Sets the stack size of the worker threads

#### pub fn breadth_first(self) -> ThreadPoolBuilder 

struct rayon::ThreadPoolBuilder

👎Deprecated:

use`scope_fifo` and`spawn_fifo` for similar effect

(DEPRECATED) Suggest to worker threads that they execute spawned jobs in a “breadth-first” fashion.

Typically, when a worker thread is idle or blocked, it will attempt to execute the job from the top of its local deque of work (i.e., the job most recently spawned). If this flag is set to true, however, workers will prefer to execute in a breadth-first fashion – that is, they will search for jobs at the bottom of their local deque. (At present, workers always steal from the bottom of other workers’ deques, regardless of the setting of this flag.)

If you think of the tasks as a tree, where a parent task spawns its children in the tree, then this flag loosely corresponds to doing a breadth-first traversal of the tree, whereas the default would be to do a depth-first traversal.

Note that this is an “execution hint”. Rayon’s task execution is highly dynamic and the precise order in which independent tasks are executed is not intended to be guaranteed.

This`breadth_first()` method is now deprecated per RFC #1, and in the future its effect may be removed. Consider using scope_fifo() for a similar effect.

struct rayon::ThreadPoolBuilder

#### pub fn start_handler (self, start_handler: H) -> ThreadPoolBuilder where H: Fn(usize) + Send + Sync + 'static,

Sets a callback to be invoked on thread start.

The closure is passed the index of the thread on which it is invoked. Note that this same closure may be invoked multiple times in parallel. If this closure panics, the panic will be passed to the panic handler. If that handler returns, then startup will continue normally.

struct rayon::ThreadPoolBuilder

#### pub fn exit_handler (self, exit_handler: H) -> ThreadPoolBuilder where H: Fn(usize) + Send + Sync + 'static,

Sets a callback to be invoked on thread exit.

The closure is passed the index of the thread on which it is invoked. Note that this same closure may be invoked multiple times in parallel. If this closure panics, the panic will be passed to the panic handler. If that handler returns, then the thread will exit normally.

## Trait Implementations§

§

### impl Debug for ThreadPoolBuilder 

trait core::fmt::Debug struct rayon::ThreadPoolBuilder

§

#### fn fmt(&self, f: &mut Formatter<'_>) -> Result<(), Error>

Formats the value using the given formatter. Read more

§

### impl Default for ThreadPoolBuilder

trait core::default::Default struct rayon::ThreadPoolBuilder

§

#### fn default() -> ThreadPoolBuilder

Returns the “default value” for a type. Read more

## Auto Trait Implementations§

§

### impl !RefUnwindSafe for ThreadPoolBuilder 

trait core::panic::unwind_safe::RefUnwindSafe struct rayon::ThreadPoolBuilder§

### impl !Send for ThreadPoolBuilder 

trait core::marker::Send struct rayon::ThreadPoolBuilder§

### impl !Sync for ThreadPoolBuilder 

trait core::marker::Sync struct rayon::ThreadPoolBuilder§

### impl !UnwindSafe for ThreadPoolBuilder 

trait core::panic::unwind_safe::UnwindSafe struct rayon::ThreadPoolBuilder§

trait core::marker::Freeze struct rayon::ThreadPoolBuilder

### impl Freeze for ThreadPoolBuilder where S: Freeze,

§

trait core::marker::Unpin struct rayon::ThreadPoolBuilder

### impl Unpin for ThreadPoolBuilder where S: Unpin,

§

trait core::marker::UnsafeUnpin struct rayon::ThreadPoolBuilder

### impl UnsafeUnpin for ThreadPoolBuilder where S: UnsafeUnpin,

## Blanket Implementations§

§

### impl Any for Twhere T: 'static + ?Sized,

§

#### fn type_id(&self) -> TypeId

Gets the`TypeId` of`self`. Read more

§

### impl Borrow for Twhere T: ?Sized,

§

#### fn borrow(&self) -> &T

Immutably borrows from an owned value. Read more

§

### impl BorrowMut for Twhere T: ?Sized,

§

#### fn borrow_mut(&mut self) -> &mut T

Mutably borrows from an owned value. Read more

§

### impl From for T

§

#### fn from(t: T) -> T

Returns the argument unchanged.

§

### impl<T, U> Into for Twhere U: From,

§

#### fn into(self) -> U

Calls`U::from(self)`.

That is, this conversion is whatever the implementation of From` for U` chooses to do.

§

### impl IntoEither for T

trait either::into_either::IntoEither

§

#### fn into_either(self, into_left: bool) -> Either<Self, Self> ⓘ

Converts`self` into a Left variant of Either<Self, Self> if`into_left` is`true`. Converts`self` into a Right variant of Either<Self, Self> otherwise. Read more

§

https://docs.rs/either/1.15.0/x86_64-unknown-linux-gnu/either/into_either/trait.IntoEither.html#method.into_either_with enum rayon::iter::Either

#### fn into_either_with (self, into_left: F) -> Either<Self, Self> ⓘwhere F: FnOnce(&Self) -> bool,

Converts`self` into a Left variant of Either<Self, Self> if`into_left(&self)` returns`true`. Converts`self` into a Right variant of Either<Self, Self> otherwise. Read more

§

### impl Pointable for T

trait crossbeam_epoch::atomic::Pointable

§

#### const ALIGN: usize

The alignment of pointer.

§

#### type Init = T

https://docs.rs/crossbeam-epoch/0.9.18/x86_64-unknown-linux-gnu/crossbeam_epoch/atomic/trait.Pointable.html#associatedtype.Init

The type for initializers.

§

#### unsafe fn init(init:::Init) -> usize

https://docs.rs/crossbeam-epoch/0.9.18/x86_64-unknown-linux-gnu/crossbeam_epoch/atomic/trait.Pointable.html#tymethod.init trait crossbeam_epoch::atomic::Pointable type crossbeam_epoch::atomic::Pointable::Init https://doc.rust-lang.org/nightly/std/primitive.usize.html

Initializes a with the given initializer. Read more

§

#### unsafe fn deref<'a>(ptr: usize) -> &'a T

https://docs.rs/crossbeam-epoch/0.9.18/x86_64-unknown-linux-gnu/crossbeam_epoch/atomic/trait.Pointable.html#tymethod.deref https://doc.rust-lang.org/nightly/std/primitive.usize.html https://doc.rust-lang.org/nightly/std/primitive.reference.html

Dereferences the given pointer. Read more

§

#### unsafe fn deref_mut<'a>(ptr: usize) -> &'a mut T

https://docs.rs/crossbeam-epoch/0.9.18/x86_64-unknown-linux-gnu/crossbeam_epoch/atomic/trait.Pointable.html#tymethod.deref_mut https://doc.rust-lang.org/nightly/std/primitive.usize.html https://doc.rust-lang.org/nightly/std/primitive.reference.html

Mutably dereferences the given pointer. Read more

§

#### unsafe fn drop(ptr: usize)

https://docs.rs/crossbeam-epoch/0.9.18/x86_64-unknown-linux-gnu/crossbeam_epoch/atomic/trait.Pointable.html#tymethod.drop https://doc.rust-lang.org/nightly/std/primitive.usize.html

Drops the object pointed to by the given pointer. Read more

§

### impl<T, U> TryFrom for Twhere U: Into,

§

#### type Error = Infallible

The type returned in the event of a conversion error.

§

#### fn try_from(value: U) -> Result<T, >::Error>

Performs the conversion.

§

### impl<T, U> TryInto for Twhere U: TryFrom,

§

#### type Error = >::Error

https://doc.rust-lang.org/nightly/core/convert/trait.TryInto.html#associatedtype.Error trait core::convert::TryFrom type core::convert::TryFrom::Error

The type returned in the event of a conversion error.

§

#### fn try_into(self) -> Result<U, >::Error>

Performs the conversion.
# SciSpace literature lock — BG-02 GR background constraints

**Stage:** `BG_02`  
**Search date:** `2026-09-02 KST`

## Search question

Which peer-reviewed papers derive exact spatially homogeneous Bianchi Einstein
equations in an orthonormal-frame or 3+1 formulation, including Hamiltonian
and momentum constraints, expansion and shear evolution, structure-variable
evolution and constraint propagation, while keeping sign and exceptional-type
issues explicit?

## Admitted methodological cross-checks

1. H. van Elst and C. Uggla, “General relativistic orthonormal frame
   approach,” *Classical and Quantum Gravity* **14** (1997) 2673,
   DOI `10.1088/0264-9381/14/9/021`, arXiv `gr-qc/9603026`.

   Admitted use: the 1+3 orthonormal-frame organization of evolution,
   constraints and spatially homogeneous specialization. The paper does not
   own BASS signs, variable names or off-shell evolution policy.

2. C. G. Hewitt, J. T. Horwood and J. Wainwright, “Asymptotic dynamics of
   the exceptional Bianchi cosmologies,” *Classical and Quantum Gravity*
   **20** (2003) 1743, DOI `10.1088/0264-9381/20/9/311`,
   arXiv `gr-qc/0211071`.

   Admitted use: confirmation that `VI_-1/9` requires an exceptional
   constraint sector rather than a generic `VI_h` diagonal-shear reduction.

3. M. A. H. MacCallum, “A class of homogeneous cosmological models III:
   asymptotic behaviour,” *Communications in Mathematical Physics* **20**
   (1971) 57–84, DOI `10.1007/BF01646733`.

   Admitted use: historical cross-check of homogeneous Class-A/Class-B
   dynamics and asymptotic limits. It is not used as machine formula authority.

4. O. Coussaert and M. Henneaux, “Bianchi cosmological models and gauge
   symmetries,” *Classical and Quantum Gravity* **10** (1993),
   DOI `10.1088/0264-9381/10/8/018`.

   Admitted use: warning that homogeneity-preserving automorphisms and frame
   gauge must be separated from physical evolution.

## Independent project cross-checks

The BG-02 Type-V propagation law is independently reconstructed in Wolfram
from the coordinate metric

```text
ds^2 = -ds^2 + a1(s)^2 dx^2
       + exp(2 A x) a2(s)^2 dy^2
       + exp(2 A x) a3(s)^2 dz^2,
```

using a symmetric residual tensor with orthonormal-frame components
`E^(00)=F` and `E^(01)=C`. This gives

```text
D0 F = -3 H F - 2 (A/a1) C,
D0 C = -(4 H + sigma1) C,
```

with no spatial-coordinate dependence and no `F -> C` feedback. This agrees
with the existing repository metric audit but is re-evaluated in Wolfram.

## Authority boundary

The literature is methodological support only. Formula authority remains the
locked BASS convention, committed Wolfram source, exact residual tests, xAct
runtime identity and immutable Git objects.

This lock does not establish all-eleven-branch support, matter closure,
finite-tilt dynamics, chart-event handling, numerical parity, generic-ell
compilation or scientific validity.

# BASS-8B.2B preflight — finite carrier choice and rate/dual dependency correction

**Date:** 2026-08-24  
**Decision class:** bounded PHYS-MATH / PHYS-MATH-CODE preflight  
**Decision:**

```text
SELECT_GENERIC_VECTOR_PAIRED_REST_TO_NORMAL_PHYSICAL_SCREEN_BUNDLE
RATE_DUAL_BINDING_MOVED_ONTO_CRITICAL_PATH
```

**Execution status:**

```text
BASS-8B.2B.0_CARRIER_CHOICE                  PASS_BOUNDED_DECISION
BASS-8B.2B_FINITE_PROJECTOR_LEFT_AUTHORITY   NOT_YET_PASSED
```

## 1. P0 dependency correction

An earlier DAG-seam decision treated a direction-dependent local collision rate
as though it were one global scalar multiplying the whole carrier. That is valid
only for `lambda I`. It is false for a diagonal multiplication operator whose
entries vary with photon direction.

Let the collision shape be `C_hat` and let the positive local-rate operator be

\[
M_\nu=\operatorname{diag}(\nu_1,\ldots,\nu_N)\otimes I_{\rm fiber},
\qquad C=M_\nu\widehat C.
\]

If every \(\nu_i\neq0\), then

\[
\ker C=\ker\widehat C,
\]

but the left kernel obeys

\[
\ker C^{\mathsf T}=M_\nu^{-\mathsf T}\ker\widehat C^{\mathsf T}.
\]

Thus a direction-dependent multiplier preserves the right equilibrium carrier
but generally changes the paired left invariant and the normalized projector

\[
P_\nu=\frac{r\,a_\nu^{\mathsf T}}{a_\nu^{\mathsf T}r}.
\]

The exact SymPy witness in `source/exact_rate_multiplier_witness.py` proves this
with a two-node rational counterexample. Keeping the old left vector gives a
nonzero exact residual, while the transformed left vector annihilates the full
operator. The projector changes as well.

The project E2 collision-rate authority makes this distinction load-bearing:
normal-time optical-depth rate is

\[
\nu_i=n_e\sigma_T c\,D_{e\leftarrow n,i},
\qquad
D_{e\leftarrow n,i}=\gamma_e(1-\boldsymbol\beta_e\cdot\mathbf e_i),
\]

and the Doppler/relative-flux factor occurs exactly once. The scalar factor
\(n_e\sigma_Tc\) may be separated without changing a nonzero left kernel, but
the direction-dependent factor \(D_i\) may not be deferred when closing row 8
or the normalized full-generator projector.

Therefore the former `BASS-8B.1E.5_DIRECTION_DEPENDENT_Q_LOCAL_RATE` side-node
classification is narrowed:

```text
not required for:  right-kernel existence alone
required for:      full-generator paired left invariant
required for:      normalized projector of the full collision generator
required for:      Pdot/K when the rate-direction map varies
```

This correction does not invalidate BASS-8B.2A. It changes only the ordering
inside BASS-8B.2B.

## 2. Selected finite physical carrier

The selected discrete reference carrier is a generic-vector paired
rest-to-normal moving bundle.

Start from one fixed electron-rest angular quadrature

\[
\{(\mathbf e'_i,w'_i)\}_{i=1}^N.
\]

For a dimensionless electron velocity \(\boldsymbol\beta_e\),
\(|\boldsymbol\beta_e|<1\), define the paired normal-frame node by inverse
aberration and set

\[
D_i=\gamma_e(1-\boldsymbol\beta_e\cdot\mathbf e_i),
\qquad
w_i=w'_iD_i^2,
\]

so that the rest measure is recovered node by node:

\[
\frac{w_i}{D_i^2}=w'_i.
\]

At each node the physical fiber is the Hermitian screen tensor

\[
J_i=P(\mathbf e_i)J_iP(\mathbf e_i),
\qquad
P(\mathbf e_i)=I-\mathbf e_i\mathbf e_i^{\mathsf T},
\]

with four real degrees of freedom. The nine-real tensor packing is retained
only as a redundant ambient embedding for basis-free screen transport.

The discrete unpolarized moving equilibrium is

\[
r_{\beta,i}=\frac12D_i^{-4}P(\mathbf e_i).
\]

The paired left functional must be derived from the same full discrete
collision action, including the selected time/rate multiplier. It is forbidden
to import an axis-aligned Type-II left formula by component substitution.

## 3. Rejected carrier claims

### 3.1 Finite harmonic truncation is not an exact boost carrier

A Lorentz boost acts on the full spin-weighted sky function and mixes harmonic
multipoles across an unbounded \(\ell\) range. A finite \(\ell\)-truncation may
be a convergent numerical approximation, but it is not an exact finite boost
representation and cannot be the authority carrier for this node.

### 3.2 Fixed-normal collocation is not the reference authority lane

A fixed normal-frame grid can converge under refinement and remains useful as a
negative control or explicitly corrected AP lane. It is not selected as the
structure-preserving reference because finite boosts destroy exact low-order
quadrature closure at fixed nodes. The paired moving grid recovers the rest
quadrature node by node.

## 4. Fresh discrete generic-vector witness

The package includes an independent Python witness extending the already
validated axis-aligned formulas to an arbitrary three-vector velocity.

Sweep:

```text
rest grid                  Lebedev-26
orientations               axis / diagonal / generic
speeds                     0.00 to 0.50, 11 values
physical carrier           4N = 104 real dimensions
SO(3) probes               30 random rotations
```

Results:

```text
max paired right-null residual          9.690270078462301e-16
max paired left-null residual           4.185521612064836e-16
max projector-idempotence residual      6.661338147750939e-16
max imaginary eigenvalue                1.5250228651346773e-16
max collision SO(3) covariance residual 8.881784197001252e-15
max projector SO(3) covariance residual 3.9968028886505635e-15
observed physical nullity values         {1}
minimum nonzero spectral gap             2.147904457756587e-1
```

Hostile controls:

```text
omit direction factor in left dual:
  minimum nonzero defect over finite-speed sweep 1.2208845975225841e-3

fixed-normal generic orientation:
  |beta|=0.10 equilibrium residual 2.431108317861103e-7
  |beta|=0.20 equilibrium residual 1.8242100300285373e-5
  |beta|=0.50 equilibrium residual 5.849708359265476e-3
```

This is a discrete numerical witness. It is not a generic-rank proof, not a
continuum finite-electron-tilt theorem, and not yet an authority-row promotion.

## 5. PHYS-MATH audit

### Conventions and dimensions

- Metric signature: \((-+++ )\).
- \(\boldsymbol\beta_e=\mathbf v_e/c\) is dimensionless.
- \(D_i\), \(q_i=1-\boldsymbol\beta_e\cdot\mathbf e_i\), angular weights, and
  normalized projectors are dimensionless.
- \(n_e\sigma_Tc\) has dimensions \(T^{-1}\); division by the normal Hubble
  scalar produces a dimensionless Q-time collision rate.
- The collision shape in this witness is dimensionless; dimensional rate is
  applied exactly once at the external authority boundary.

### Limits and covariance

- \(\boldsymbol\beta_e\to0\): paired nodes and weights reduce exactly to the
  rest grid, \(D_i\to1\), and the rest projector is recovered.
- Proper rotations act covariantly on directions, electron velocity, and the
  ambient tensor carrier; the random SO(3) residuals remain at floating-point
  level.
- The Type-II \(\boldsymbol\beta_e=v_2\mathbf e_2\) lane is admitted only as a
  restriction of the generic-vector formulas.
- The sweep stops at \(|\boldsymbol\beta_e|=0.5\); no near-light-speed
  conditioning claim is made.

### Hidden-assumption correction

The left kernel cannot be specified before the direction-dependent rate/time
operator is specified. A global scalar opacity and a direction-dependent
relative-flux map must not be conflated.

## 6. PHYS-MATH-CODE audit

What is genuinely established:

- one-to-one paired moving grid construction for arbitrary three-vector tilt;
- roundoff-level discrete right null, paired left invariant, idempotence, and
  SO(3) covariance on the tested carrier;
- one physical null mode on the tested 104-dimensional screen carrier;
- fixed-normal and wrong-dual hostile controls fail clearly.

What remains open:

- a hash-pinned exact formula authority for the generic-vector finite-tilt
  collision bundle;
- exact derivation of the full rate-bound left functional from the E2 time
  adapter and chosen carrier;
- bundle differential when nodes, weights, Doppler factors, and screen maps all
  move with \(\boldsymbol\beta_e\);
- `ElectronStateJet -> rate jet -> Pdot -> K` integration;
- independent second implementation or exact CAS witness of the generic-vector
  carrier map;
- refinement/conditioning audit beyond this Lebedev-26 witness;
- row 7/8 re-adjudication.

## 7. Corrected DAG

```text
BASS-8B.2A_TYPED_ELECTRON_STATE_BINDING                  PASS
BASS-8B.2A-R1_EXACT_HOST_REPLAY                          PASS

BASS-8B.2B.0_CARRIER_CHOICE                              PASS_BOUNDED
  -> BASS-8B.2B.1_DIRECTION_DEPENDENT_RATE_DUAL_BINDING  NEXT
  -> BASS-8B.2B.2_GENERIC_VECTOR_BUNDLE_DIFFERENTIAL
  -> BASS-8B.2B.3_PROJECTOR_LEFT_FUNCTIONAL_AUDIT
  -> BASS-8B.3_ROWS7_8_READJUDICATION
```

The older E5 label is absorbed into `BASS-8B.2B.1`; it is no longer a deferred
side node for purposes of row 8 and the full normalized projector.

## 8. Hard boundaries

```text
row 7                         BLOCKED_NO_COMPLETE_PROJECTOR_AUTHORITY
row 8                         BLOCKED_NO_PAIRED_LEFT_INVARIANT
BASS-3 VI0 classifier         DO_NOT_START
solver/runtime/production     DO_NOT_START
Join J1                       BLOCKED
PR / merge / tag              NONE
```

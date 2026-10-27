# R6 independent source/theory review

Reviewer: `/root/b3h_input_recovery`, separate from the contract/theory author
and implementation worker. Method: read-only source comparison and independent
algebra/unit derivation. No scientific code, source root solve, IVP, native
runtime, or previous campaign was executed. Only this review file was written
inside the consumer lane.

## Decision

`PASS_SCOPED_R6`. Findings F1 and F2 are closed by the author's targeted
document corrections, directly read back by this reviewer. Blocking findings0.

The birth moment formula, diagonal finite error inequality, matrix defect
inequality, native-reference distinction, fixed-scale stress/four-force units
and Bianchi-I RHS are correct within the declared domains. Two precise
wording/classification corrections are preserved below with their closure.
They required no scientific rerun and did not change the main formulas.
Root owns the execution/admission decision. This review does not admit a finite photon
absorption transaction or calibrated physical REC geometry.

## Reviewed identities

| File | SHA256 at review |
|---|---|
| FROZEN_CONTRACT.md | 6a869a2cc8e94640e2a01802405035e3cd7b9ae1ae7276ff0162b5105dc20d24 |
| theory/TRANSPORT_AND_GEOMETRY.md | debaa3c691004523bbcb7be67c5684aa845ef811a6b9dd4a24715ac8196153a9 |
| recovered B3c code/bounded_background.py | 1917f49c45cbd637f4d951a21d6e377c3cc3c58798c5e75690317eacabe68044 |
| recovered B3c vendor/finite_exchange.py | 92392b51121b5262323f19083adaad29dabd34ece58da701ba407f3c87d2840e |
| B3f vendor/core.py | bb4a57ed677321ef9e0967953f29a6b125824765138a268c5a0c11904a53d1fa |
| B3f code/cohort_input_error.py | babd838f36712795ab7d19630e97e7481c42735742f27c235b7640993ead769b |

REC source files were independently recovered with exact Git blob matches in
`/workspace/scratch/7aa4d0cea548/b3h_recovery/RECOVERY_MANIFEST.json` from
`rec_bianchi@ea89c97abeb7a663a813f00e9aadddaf0b32a6a9`. The original files,
including both LINE01/LINE02 frozen contracts, native_line_owner.py,
STORED_NATIVE_LYA_STATE.json, SOURCE_PARTITION_FACTS.json and hydrogen.h/c,
were read directly. No inferred newer version replaced them.

Corrected document identities at closure:

| File | SHA256 directly read at closure |
|---|---|
| FROZEN_CONTRACT.md | 1d7beda73480b63e6dda340496da45995dc03887795d2e1aa4b181c2ea05581a |
| theory/TRANSPORT_AND_GEOMETRY.md | d2c56589e4e550555f18ba89a4cde0233e1a4ad19743e910f50b1d2f5ba76778 |

## Verified findings

### V1. Actual source q and birth moments

Recovered B3c `source_arguments` forms `S=sigma/h`, sets f_plus=0 and supplies
the declared effective coincident 2p card to the existing detached owner.
`finite_exchange.commit_emission` assigns the actual finite packets by
`dn=D*A*(1+n.S.n)`. Its Q14 weights are six axis directions with weight1/15
and eight cube-corners with weight3/40. The rule is antipodal and integrates
the second/fourth spherical moments in the theorem exactly in real arithmetic.

Independently contracting the fourth moment with a symmetric STF S gives
`<q n_i n_j>=delta_ij/3+2*S_ij/15`. Thus birth `T00=E*D`, `T0i=0`,
`Tij=E*D*(I/3+2*S/15)` and signed `pi=2*E*D*S/15` agree with the saved owner
packet fields and original source construction. Counts are integrated
densities; a second factor dt would be a units error. The contract excludes
that error. Source-model uncertainty remains distinct from degree-four
polynomial exactness and representation residuals.

The inherited B3f implementation uses the same effective card energy, through
`positive_angular.EB=CARD.energy_J`. Its `ball` returns
INPUT_ERROR_UNSPECIFIED when a radius is null before issuing a certificate.
Reusing that branch with actual birth R=I does not assert a physical total
error bound. The separate energy-uncertainty field is appropriate because
the inherited theorem fixes E.

### V2. Midpoint transport provenance

Recovered B3c `integrate_fixture` takes transport(dt/2), source_kick(dt),
transport(dt/2). `source_kick` stores midpoint N,H,S and deposition epoch,
but not midpoint beta. `packets_at` uses both Delta alpha and Delta beta.
Endpoint PATH contains beta; therefore generic exact saved-cohort endpoint R
cannot be read from those receipts without an additional midpoint value or a
separately controlled reconstruction.

Even ISO's stored binary64 path is not exactly beta=0: the inspected PATH
contains beta1=beta2=3.209131804849689e-36 at tau0.00078125 and final
beta1=beta2=6.374817694738609e-31. Analytic isotropy of the exact model and
byte-exact reconstruction of this particular stored numerical run are
different targets. The present scope keeps this distinction correctly.

R(t_b,t_b)=I is exact at a common event/frame and does not require the missing
midpoint coordinate. Its error radius0 refers only to that same-event map.

### V3. Diagonal transport and determinant bounds

With delta_i=a_i-a_hat_i in [-e_i,e_i],
`|exp(-delta_i)-1|<=exp(e_i)-1`. Multiplication by positive exp(-a_hat_i)
and maximization gives the stated spectral norm bound. No linearization is
used. STF beta removes its trace from the determinant, giving
`|D-Dhat|<=Dhat*expm1(3*e_alpha)`. The latter requires both actual and nominal
beta to satisfy the stated STF condition, not merely a sampled approximate
trace constraint. Independent physical/numerical component radii may be
summed before exponentiation with their origins retained.

### V4. General matrix defect bound

For E=R-Rhat and D=Rhat'+Ahat Rhat,
`E'=-A E-(A-Ahat)Rhat-D`. The Euclidean logarithmic norm is Lipschitz under
the spectral norm, so `mu2(-A)<=mhat+eta=m`. The transition bound and
variation-of-constants inequality yield

```text
||E(T)|| <= exp(mT)*e0 + (eta*M+d)*expm1(mT)/m
```

with the continuous integral limit T at m=0. This is exactly the theorem's
`T*phi1(mT)` form. It is positive also for negative m. The hypotheses must
hold across the interval, and the contract explicitly prevents treating saved
sample residuals as such envelopes. See clarification F2 for the labels on
physical/numerical forcing contributions.

### V5. Native Wien versus standalone Planck

LINE02's frozen contract and native owner use Wien-departure variables and
the direct pair `r0=LYA_FACT*H/(nH*x1s)`, `b0=3*x1s*Dfplus_Lya`.
LINE01 separately declares `1/expm1(E21/TR)+Dfplus_Lya` in a stimulated
standalone model and explicitly distinguishes it from native compressed-source
replay. The new contract/theory preserve that distinction. Native TR is in
eV, so E21/TR has no extra k_B. Native coefficients retain the literal source
LYA_FACT/hPc, while E21 is converted to joules as the frozen contract specifies.

The current source data do not provide finite spectral/time/angular donor
support or a mapping between saved cell averages and the incident line face.
Typed readiness with physical_finite_absorption=false is the appropriate
current output. A source-only scalar binding is useful without making all
future providers prerequisites.

### V6. SI stress/four-force and geometry

For x0=ct, `T00=rho` and `T0i=energy_flux_i/c` all have J/m3. From
`nabla_a T^{ab}=Q^b`, Q has J/m4. Consequently cQ has J/(m3*s), and with
alphaL=kappa*L^2, tau=ct/L,

```text
U = kappa*L^3*Q0 = alphaL*(L/c)*(cQ0)
J = kappa*L^3*Qi = alphaL*(L/c)*(cQi)
```

These dimensions and signs agree with the unchanged core Source arrays and
RHS. The stated Bianchi-I h,sigma,rho,F equations follow directly after
setting n=a=rotation=Lambda=0. The core balances total internal transfers;
an unbalanced pair should be rejected in the ordinary source path.

The stored B3c lower-rest and excitation sectors are cold comoving terms,
and radiation pressure is rho_gamma/3. Applying a stored finite source
transaction again through Q would double-count it; current Q=U=J=0 is correct
for the subsequent algebraic endpoint RHS. Stored nonzero signed pi remains
an instantaneous radiation stress, not a heating rate.

## Clarifications and closure

### F1 — reconstruction wording; low severity, physical claim precision

**Target:** theory section2, `N_b=N0 exp(-3 alpha_b) recovers alpha_b exactly
within the stored representation`.

**Evidence:** the original calculation rounded exp, the product N0*exp,
population construction and serialization. Applying log to the stored density
gives a nominal inverse, not a proof of recovery of the exact original
binary64 alpha or of an exact real alpha. `line.N` is reconstructed from
population stocks as well.

**Impact:** no effect on birth R=I or the moment formula. The word `exactly`
could incorrectly erase numerical reconstruction uncertainty in a later
final-R calculation.

**Minimum correction:** say that the stored positive N supplies
`alpha_b_nom=-log(N_b/N0)/3`; record floating reconstruction error separately
and retain the missing beta/interpolation obligation. No new run is needed.

**Closed:** corrected theory section2 and contract B3g now state nominal
reconstruction with a separate exp/rounding/log arithmetic obligation. The
reviewer read both corrected passages. Birth R=I and moments are unchanged.

### F2 — Duhamel error-origin labels; low severity, conditional-contract precision

**Target:** theory section4, B_phys uses eta*M while B_num uses only d.

**Evidence:** the mathematical hypothesis only says eta bounds A-Ahat; it
does not yet assign all that difference to physical-input uncertainty.

**Impact:** the total bound is correct. Assigning the full eta contribution to
physical input is justified only if the supplied eta indeed has that meaning.

**Minimum correction:** either define eta as the physical-input envelope and
d as represented-path numerical defect in that version, or permit
eta=eta_phys+eta_num with
`B_phys=exp(mT)*e0_phys+eta_phys*M*T*phi1(mT)` and
`B_num=exp(mT)*e0_num+(eta_num*M+d)*T*phi1(mT)`, sharing
`m=mhat+eta_phys+eta_num`. Preserve null origins rather than relabeling them.
No change to the proof or new execution is required.

**Closed:** corrected theory section4 defines Ahat as the exact mathematical
nominal coefficient field, eta as physical/model discrepancy, and D relative
to Ahat as including numerical coefficient evaluation error. This makes the
existing two-term labels valid. The reviewer read that definition directly.

## Remaining scope

This is source/theory R6 review only. New implementation tests, actual output
inspection and final figure/diff review remain separate C6-C9 evidence. A
physical finite donor transaction, source-qualified physical error envelope
and calibrated REC geometry retain their original open dependencies. No
strong no-go claim is made or needed.

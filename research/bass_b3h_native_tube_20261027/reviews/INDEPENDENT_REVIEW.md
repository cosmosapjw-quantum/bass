# Independent R6/C9/R9 review — native finite incoming Lyα tube

Date: 2026-10-27 (Asia/Seoul). Reviewer: separate finite_tube_theory agent.
Implementation author: separate tube_implementation worker; requested model
gpt-6.1-sol, observed runtime model identity not established.

**Independent decision: PASS_SCOPED for the actual represented native
incoming photon tube, its common-volume number/energy tensor, and its
uncollided B3g transport.** The source-matched finite atomic transaction
and new B3i RHS remain INPUT_DEPENDENT/NOT_RUN. Root retains final admission
and publication authority.

## Review method and current base

I read the original native boundary and population conventions, derived the
finite measure and tensor mapping independently, then inspected actual
code, source slice, execution ledger, saved high-precision reference,
comparison supplement, and the rendered PNG. I did not implement or edit
the science code, execute tests, rerun integrals, invoke a native solve, or
regenerate a plot. Read-only file hashing and document writing are metadata
operations, not unreported scientific child runs.

Fresh reads in this review:
- New BASS branch research/bass-b3h-native-tube-20261027:
  786585caeb17ac9b8546da06b29c1f8dcfeaf896, Draft PR200.
- Preserved BASS F2 branch:
  009a1238c09adf889c7421132f530b960cdafb07.
- Central branch:
  5abe0d19df95db730e3e33bae0373c81ba37ce89.
- Central AGENTS:
  429a5a13ee75b1222bc50627f8d5973d01dd21c4, unchanged.
- Parallel BASS PR196–199 heads were observed and remain separate.
- REC actual source:
  d6dbe39a4923439547c01695d9020ba39367ea90.

The input slice matches the source-owned original float64 values by
lossless hexadecimal representation. The initial preparation packet's
right-reference suggestion is preserved; SOURCE_BINDING_ADDENDUM and
the frozen consumer contract explicitly select the left reference.
That is a representation decision, not a change of source physics.

## R6: finite measure, native convention, and physical interpretation

The source's q=1 scalar-FLRW characteristic has Hdt=deta. For a fixed
comoving cell and left reference eta0,
Jv=exp(3u), u=eta-eta0. Thus dmu=G exp(3u)deta dOmega/(4pi).
A photon arriving at E21 pulls back to E0=E21 exp(u), yielding
N0=G integral exp(3u)f and U0=G E21 integral exp(4u)f.

The source-to-Lyα energy ratio gives eta_query=eta-log(Esource/E21).
Because the native TR is proportional to exp(-eta),
Esource/TR(eta_query)=E21/TR(eta). Therefore adding the arriving native
Wien reference to the retarded PL departure is correct. The code retains
the original E21, LYA_FACT, kBoltz, temperature and background constants.

The two actual interpolation segments have strict-past margins
8.49e-5 and 5.278877465967507e-8 in eta. The latter also equals
lag-h>0. Therefore each right interpolation sample precedes its minimum
arrival on the segment. The left segment uses earlier samples and the
second segment uses the source sample at the already-reached left cell
boundary. No future endpoint is imported.

The interval-wide positivity sufficient bound is positive:
min f >= 7.672046131261324e-15. This follows from the PL endpoint minimum
plus the monotone Wien minimum on each segment. No clipping is used.

The T0 and uncollided T1 tensors are isotropic radiation tensors with
Tii=U/3, zero vector flux and zero PSTF stress. They are the selected
incoming-shell component, not the native total radiation state.
B3g R=exp(-h)I and detR=exp(-3h) produce N1=exp(-3h)N0 and
U1=exp(-4h)U0. The same source normalization is used throughout.

The direct crossing propagation loss is positive. Its negative is the
radiation change between the initial shell and each photon's own line
arrival. The full-shell left-to-right work is a second distinct quantity.
Neither is assigned to atomic heat or recoil.

The unresolved atomic packet is correctly limited to this same interval:
x1s, xr_p, opacity, level stocks, and matched QSS/non-Lyα replenishment
and energy ownership. Native direct-pair zero recoil and zero ion/electron
yield are already source-defined conventions. The implementation does not
call the different B3b LINE01 gross-count law to manufacture native
absorption. It refuses the absent atomic packet and performs no B3i RHS.

## C9: code and controls

The exponential-times-PL endpoint basis in tube.py matches the independent
derived integrals. Its short positive series is stable at this cell's
width. The native Wien term uses positive 24-point Gauss quadrature.
reference.py does not call the primary integrator: it reconstructs exact
binary64 inputs as integer ratios and performs independent 70-digit
piecewise quadrature on the total occupation.

The actual first tests attempt failed with PACKAGE_MISSING because mpmath
was absent. Seven controls passed and the mpmath-dependent control errored.
The preserved failed log and freeze remain present. The controller's
targeted environment repair installed mpmath==1.3.0 in the task-local
runtime_deps and changed no source physics, input or tolerance. The
repair tests then passed 8/8. Consume and plot each completed once.
The append-only ledger retains the failed attempt and all costs:
child CPU 2.786822 s; child wall 2.881160140997963 s.
Historical debits and unknown remaining budgets were not reset.

Controls cover constant/affine integration, the shifted segment crossing,
vacuum, nonfinite/negative total occupation, missing atomic inputs, redshift
scaling, native H/nH snapshot consistency, and a manufactured PL+Wien
comparison. This is adequate for the selected finite represented input.
No extra old-campaign regression or native solve is needed for this scope.

## C8/R9: saved raw and numerical interpretation

| Quantity | Saved primary |
|---|---:|
| Native cell indices | 5126–5127 |
| Delta eta | 8.49e-5 |
| Proper duration | 1708251102.5026681 s |
| Crossing capacity | 1.187791651352076e18 m^-3 at V0 |
| Incoming count N0 | 9117.092768838671 m^-3 at V0 |
| Incoming U0 | 1.4898091530925236e-14 J m^-3 at V0 |
| Uncollided N1 | 9114.770941007773 m^-3 at V1 |
| Uncollided U1 | 1.4893032998028835e-14 J m^-3 at V1 |
| Crossing propagation loss | 6.323424461041997e-19 J m^-3 at V0 |
| Full-shell signed propagation change | -1.2647942796986586e-18 J m^-3 at V0 |

The saved-output-only Decimal70 supplement resolves sub-ULP comparison
differences that the main raw's float-projected reference displays as zero:

- N0 signed relative primary/reference difference:
  -2.688299962984027459e-17.
- U0:
  -4.706966050752376951e-17.
- Proper duration:
  -4.182979965611604898e-16.

These are within the frozen 2e-11 numerical representation criterion.
The reference discrepancy is a finite comparison, not an interval
certificate or a physical continuum error radius. Transport residuals
against the stated exponential formula are zero at binary64 precision;
this is not a statement of physical error zero.

The stored eta endpoints differ from the exact-real native affine clock by
-1.73363927380432159e-16 and -1.18991188430284112e-16.
Those are documented representation differences. The code uses local u
and shifted knots to avoid subtracting two nearly equal absolute epochs.

The subtraction estimate U0-E21*N0 differs from the directly integrated
small positive work by -1.4006325520556173e-30 J m^-3,
or -2.2149905651356765e-12 relative to that small work.
The direct positive work integral is authoritative for this diagnostic.
The difference is consistent with cancellation in subtracting large
rounded values, and is not reassigned to an atomic reservoir.

## Figure inspection

I actually opened figures/NATIVE_INCOMING_TUBE.png using view_image.
The two-panel figure is readable and generated from the new saved CSV.
The first panel uses the absolute occupation, native PL departure and
native Wien component. The total and departure almost overlap because
the Wien contribution is small on the selected scale. The second panel
correctly distinguishes exp(3u) and exp(4u) and shows its +1 axis offset.
The plot is a visualization of the represented input and common-volume
weights; it is not a physical uncertainty or continuum convergence plot.
There is no reason to regenerate it.

## Findings and disposition

1. Main comparison fields cast the high-precision reference to binary64
   before subtraction, so N/U displayed zero. Scientific tolerance
   admission is unchanged because the tolerance is much larger than one
   ULP. Closed by NUMERICAL_COMPARISON_DETAIL.json, which preserves the
   untouched main raw and exposes the signed sub-ULP differences.
2. The original main raw had the positive crossing work and a separately
   signed full-shell work, but no explicit negative crossing field.
   Closed by the same supplement, which gives the negative crossing
   change and identifies the different endpoints of the two works.

Neither finding required a scientific rerun. No remaining implementation
or scientific blocking finding exists within the selected photon subunit.

## Accepted scope and preserved open work

Accept the native finite incoming photon tube and uncollided transport
as PASS_SCOPED on the actual represented source input. Physical
eS/en/eE/geometry/temporal/total radii remain null.
Actual upward/downward atomic debits, atomic kick and new B3i RHS remain
null/NOT_RUN. The next minimal action is to supply the same-tube atomic
population/opacity and stock/refill history, then construct one native
finite transaction.

Reuse the completed 512 B3g transport results and two earlier B3i consumes.
Preserve ANISO continuum-finite14 difference 3.447529542803539e-5 separately
from the approximately 1e-11 reconstruction residual and 2e-8 continuum
numerical criterion. Central declared count remains 27/88; global physical
completion remains null and L4=false. No future unselected provider is
introduced as a prerequisite.


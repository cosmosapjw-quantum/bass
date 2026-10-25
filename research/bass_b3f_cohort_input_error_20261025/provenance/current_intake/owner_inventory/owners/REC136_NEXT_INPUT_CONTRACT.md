# Next actual input contract after REC-HISTORY-KS01

## Reuse boundary
THERMO01's completed local primitive J_s and KS01's completed incoming K_s are
reusable only with their exact stored source, coefficients, primitive base,
incoming313 and arithmetic policy. Do not replay THERMO01/RESP01/LINE02/old
campaigns. Native K_0 is a separately represented object. KS01 has supplied a
direct stable certificate and therefore no K_0->K_s transfer assumption is needed.
Use delivery/PUBLICATION_STATE.json and final handoff for actual final refs.

## H5: physical calibration supplier still needed
Original35MB payload admission is now actual: SHA256
d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1,
35239470bytes,7489knots,h=8.49e-5,zstart1700.4825068138662.
Target iz5127,z1099.9986525171403 uses prefix5127,lastindex5126.
All313queries were bound to original outgoing channel owners; cell indices
4770..5125, no thermal-prehistory queries. The nearest strict upper-domain
margin is5.278877512893132e-8 in eta; crossing it is a real admission change.
T0=2.728K,nH0=.18745798773143102m^-3,fsR=meR=1.
These parameter values are linked through the retained input.dat/producer
chain and scalar consistency, not metadata encoded in the photonNPZ itself.

Next finite input task must obtain either:
1. An independently justified reference for the SAME cosmology,source/frame,
prefix and313query domain, with explicit reference and endpoint uncertainty;
or
2. A validated whole-cell curvature/defect bound tied to that same trajectory,
together with any endpoint uncertainty needed for an absolute interpolation
bound. Sampled second differences alone are not a whole-cell physical bound.

For linear interpolation the conditional bound is
epsilon_j <= (1-lambda_j) delta_left + lambda_j delta_right
             + M_cell*(eta_right-eta_left)^2/8,
where each supplied delta and M_cell must be justified for that exact source.
Current physical_epsilon,reference_uncertainty,endpoint_uncertainty,
whole_cell_curvature,absolute_history_bound remain null.
Existing different-cosmology h/2,h/4 trajectories and same-h parity do not
close these obligations. Physical epsilon is not set to the observed
3.219042386314642e-15 normalized reconstruction mismatch.

Before any new IVP/native run, freeze its complete source/input identity,
tolerances/error allocation,actual CPU/wall/RHS/steps budget and acceptance.
The present handoff is not authority to spend an old unit's unused allowance.

## H6: active parallel owner and actual trace
REC_HISTORY02_C5_CHECKPOINT_20261025_f7e85025fa2e.zip is a separate owner's
implementation-present/verification-pending checkpoint. Re-read that owner's
latest receipts before selecting H6 work. Do not restart its Bianchi-I
retarded-crossing/direction/fixed-cell tangent implementation.
Actual incident trace must bind chosen geodesic,direction,frame,
measure/volume/clock,source and query owner. A generic or prescribed frame
test is not an actual REC incident-provider receipt.

## H7: local pair exists; global composition remains
For fixed local source,delta o=J_s delta theta+K_s delta u.
J_s has numerical derivative validation; K_s has a represented binary64
operator enclosure. A composed history/retiming/geometry/thermal-ODE
Jacobian needs the actual delta u pullback,domain/stencil ownership and
corresponding error allocation. The nearest-domain margin above constrains
any retiming probe; holding query time fixed is a different derivative.
The upper norm1.1756272292401908 bounds incoming-to-outgoing amplification;
it is >1 and is not a contraction/global convergence certificate.

## Persistent gates and budget
Physical HOLD; REC_U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global_convergence NOT_RUN; production NOT_APPROVED;REI_activation=false;
first failed REI raw HISTORICAL_LOCAL_ONLY.
Read BUDGET_LEDGER.json for measured new and inherited costs. Older unknown
costs remain unknown. Separate providerIO/full-turn elapsed and remote CAS
CPU from measured local scientific execution; no inferred zeros.
New merge/activation/nativeIVP requires its own actual authorization/scope.


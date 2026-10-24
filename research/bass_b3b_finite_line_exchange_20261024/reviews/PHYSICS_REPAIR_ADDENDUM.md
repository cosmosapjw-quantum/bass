# Physics repair-impact addendum

## Decision and provenance

**PASS_SCOPED_REPAIR_IMPACT.** This addendum accepts the mathematical construction and unchanged figure interpretation of the targeted F1/F2 repair. It supplements [PHYSICS_AND_FIGURE_REVIEW.md](PHYSICS_AND_FIGURE_REVIEW.md); that original review and its original artifact hashes remain unchanged.

The independent code auditor subsequently found an endpoint-loss case outside the original physics figure fixture, plus missing complex-input rejection. Those findings are real failures of the earlier implementation. The original scoped physics pass did not close the independent code gate and must not be presented as universal or first-pass acceptance. The auditor's targeted probe closure is a separate result, not inferred by this addendum.

Reviewed final implementation SHA256:
92392b51121b5262323f19083adaad29dabd34ece58da701ba407f3c87d2840e.

## F1: construct the physical endpoint, preserving remaining excitation

For the admitted \(f=0\) branch and positive initial upper population, the finite-time thick owner has a positive endpoint \(x_1=x_0e^{-v}\). A gross decrement can round to the entire initial upper stock even when this endpoint is representable. Therefore recovering the endpoint as \(n_{u,0}-D\) is numerically unsuitable near complete depletion.

The repaired construction uses the actual owner endpoint directly:
\[
n_{u,1}=Nx_1,\qquad n_{l,1}=N-n_{u,1}.
\]
It checks the relative agreement between \(n_{u,1}/N\) and the owner \(x_1\), and explicitly refuses positive endpoints that underflow. The exact zero-update path preserves the caller's stocks. Existing refusal of an unrepresentable nonzero advance remains.

For \(\alpha_L=\kappa_{\rm grav}L^2\), define the already-owned constant atomic component
\[
\rho_{\rm other}=\rho_{a,0}-\alpha_LE n_{u,0}\ge0.
\]
The repaired atomic state is
\[
\rho_{a,1}=\rho_{\rm other}+\alpha_LE n_{u,1}.
\]
In exact arithmetic this is the same excitation transfer as subtracting \(\alpha_LED\). Constructing the endpoint avoids erasing its positive remaining excitation through a nearly equal subtraction. The constant component is a decomposition of the caller's existing atomic energy, not an added reservoir. An excitation contribution that cannot be represented in the returned sector is explicitly refused; no floor, clipping or population renormalization is introduced.

The positive endpoint and the stable gross decrement are separately useful floating representations. Their conservation consistency remains qualified by the original reported gross/stock-scale bounds; this repair does not promise exact floating complementarity or turn the bounds into interval certificates.

The recorded repaired endpoint fixture at \(\omega=50\) retains
\(n_{u,1}=3.878639060635223\times10^{-14}\ {\rm m}^{-3}\) and
\(\rho_{a,1}=1.3161275159163052\times10^{-24}\),
with zero recorded owner-endpoint relative residual. These values were read from the current validation evidence; they were not recomputed in this addendum.

## F2: enforce the existing real physical domain before core arithmetic

The added finite-real checks precede core State/Source arithmetic. They reject complex geometry, density, flux and source arrays instead of letting an imaginary component propagate or be discarded by a conversion. Scalar state fields are also validated. This enforces the existing physical domain and does not change the real-valued model, frame/clock scope, gross formulas, finite packet weights, L²/L³ conversion or physical tolerances.

## Recorded verification and figure

[REPAIR_HISTORY.json](../results/REPAIR_HISTORY.json) preserves F1/F2, the original red probe evidence and the intermediate assertion-message mismatch. The latter arose because the new endpoint-energy guard correctly rejected an already-invalid huge-background case earlier than the old wording-specific guard. The final recorded validation is **18/18 PASS**, with **49 regenerated figure rows**. These are implementation execution results, not new reviewer executions.

The regenerated PNG SHA256 is
3d961e45554c5eca7f43f11558f2ff192e8ff1b4c2dc6974dae050706db9d5a1,
identical to the image actually opened and inspected in the original review. Its prior visual assessment therefore applies to these exact bytes without another rendering or numerical run. The CSV was regenerated and has a different hash, recorded in the companion JSON; byte identity is claimed only for the PNG.

The figure still depicts a prescribed \(f=0.1\) boundary ledger on the left and a canonical-rest \(f=0\), initial-vacuum finite transaction on the right. Both use synthetic frozen parameters and dimensionless source time. The curves are local source-step evaluations, not a cosmological trajectory. Constraint preservation remains distinct from solving the nonzero initial constraints. The plot does not display or independently validate the new \(\omega=50\) endpoint case.

## Scope and accounting

No full physics review, numerical suite, symbolic computation, IVP or historical replay was repeated. New scientific commands: none; new scientific wall/CPU: 0/0. File/hash inspection is unmeasured review work. No remote backup/publication action was taken by this reviewer.

All original acceptance boundaries remain: \(f>0\) closed-stock absorption, changed-observer event-rate inference, new gross-channel finite-opacity relative certification, production activation and historical B1/B2 closure remain unadmitted. Campaign remaining budgets stay null and budget_reset remains false. Final independent code closure must be read from that reviewer's own receipt.

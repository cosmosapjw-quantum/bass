# Independent contract and mathematics review

Decision: **NO_BLOCKING_CONTRACT_DEFECT**. This is a review of the frozen finite model and reduction contract; implementation and trajectory admission remain pending.

The reviewer did not author the contract, donor, or new implementation. No ODE or benchmark was launched. Source fingerprints and exact pending obligations are in `CONTRACT_REVIEW.json`.

## Reduction argument

For an isotope A of element Z, write its abundance per baryon as Y_A = I_A f_Z. The photo/recombination generator depends on Z, q, T, the imposed UV field, and the common electron density. It does not depend on the isotope label. Therefore dY_A/dt = I_A M_Z(n_e,T,J) f_Z. The same f_Z solves every retained isotope of that element. The common electron density is n_b times the sum over element total inventories multiplied by their mean charge; it preserves this equality. Zero n and T remain zero because the adopted model has no active transmuting source.

With scaled populations, the lift copies the nine H/He/Li charge fractions into the 21-state owner. The geometry lift retains time, b, s, and four even multipole towers. Let P be this constant lift and R its representative restriction. Then RP=I_33. The reduced vector field is R f_full(Pv), and its derivative is R J_full(Pv) P by the chain rule. This includes the atomic electron rank-one term, geometric H derivatives, and electron-opacity feedback. It is not valid for nonzero neutron/tritium initial populations, isotope-dependent rates/initial fractions, or active nuclear transmutation.

The underlying Legendre parity is exact analytically; the unchanged donor uses floating quadrature. Its small even-to-odd leakage is a numerical residual, appropriately compared under the frozen tolerance instead of byte equality. Initial H/D inventory-division rounding has the same interpretation.

## Scope and numerical criteria

The 21 outputs cover the specified primordial inventory including Li6 and Li IV. Their common-fraction relation is an explicit atomic-rate assumption, not a measured equality of isotope-specific atomic physics. The matter anisotropic stress belongs to the donor collisionless nonbaryonic component; gas pressure is isotropic. The dynamic electron density affects photon Thomson scattering; neutrinos remain collisionless.

The adopted temperature and 5–200 eV local UV are specified inputs. The finite UV support and nuclear threshold separation justify zero nuclear photo rate within that source model. They do not justify a zero error for omitted thermal fusion, charge exchange, CI, molecules, or full energy closure. The reaction catalogue must preserve that distinction.

The tensor conventions are consistent: sigma=diag(-s,-s,2s) and pi=diag(-p,-p,2p) give squared Frobenius norms 6s² and 6p², and contraction 6sp. Half-contraction coordinates are full coordinates divided by sqrt(2). Signed component stresses must be summed before taking a norm.

The fixed two-trajectory comparison and retained donor gates are appropriate finite-implementation checks. They are not a continuum-convergence certificate or detailed speed benchmark. Actual code, comparisons, campaign, and plots are the remaining review dependencies.

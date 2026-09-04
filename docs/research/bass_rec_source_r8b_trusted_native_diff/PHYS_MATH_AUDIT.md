# PHYS–MATH Audit — R8B Trusted-Native Differential

## Scope

R8B changes no physical equation. It compares the R7 parent and the R8 source candidate under one fixed native payload. The only source delta is the receiving adapter module.

## Conventions and dimensions

The inherited source action remains

```text
C_t[f] = eta*(1+f)-kappa*f = eta-(kappa-eta)f,
```

with dimensionless occupation `f`, nonnegative primary rates `eta,kappa` of dimension `T^-1`, and signed derived coefficient `chi_affine=kappa-eta`. For `d tau=H dt`, `C_tau=C_t/H`; for ray length `s=ct`, `C_s=C_t/c`. The speed of light remains explicit.

No metric, orientation, tetrad, PSTF, collision, background or transport convention changes between parent and candidate.

## Exact bounded fixture retained

```text
eta=3, kappa=2
full-grid f=(0,1,5)          -> C=(3,4,8)
PSTF f=(0.9,0.2,-0.1,0.05)  -> C=(3.9,0.2,-0.1,0.05)
```

The coefficient action uses explicit unit-field coefficients and therefore does not assume a universal numerical monopole normalization.

## Known limits

- `eta=kappa=0` gives zero source.
- `eta>kappa` is an admissible stimulated-growth branch; negative `chi_affine` is not rejected.
- `H=0` is outside the current expanding-Q-time chart.
- Integrated angular-energy and integrated-J states remain outside the pointwise-spectral adapter domain.
- The constant angular source has `L_source=0`, so the bounded rank condition is `L_work>=L_out`.

## What R8B can establish

A clean parent/candidate differential can establish that the adapter source file does not perturb the existing tested backend behavior or native-payload admission. It cannot establish representation equivalence for a general angular source, a convergence theorem, or physical REC integration.

## Verdict before execution

```text
PHYS_MATH_CONTRACT_CONSISTENT
NO_NEW_PHYSICAL_EQUATION
LOCAL_TRUSTED_NATIVE_DIFFERENTIAL_REQUIRED
NO_PARITY_OR_SOLVER_PROMOTION
```

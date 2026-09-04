# PHYS–MATH audit — R6C cleanliness replay

## Scope

R6C changes no physics equation, source coefficient, frame convention, state representation, numerical tolerance, or backend route. It repairs only the placement of Python package-build artifacts during the parent–candidate differential.

## Preserved source law

```text
C_B[f] = eta (1+f) - kappa f
       = eta - (kappa-eta) f
chi_affine = kappa - eta
```

with

```text
[f] = 1
[eta] = [kappa] = [chi_affine] = T^-1
eta >= 0
kappa >= 0
chi_affine signed
```

For the expanding Q-time chart,

```text
d_tau = H dt
eta_tau = eta/H
kappa_tau = kappa/H
H > 0
```

No ray-length conversion, physical REC rate, grid/PSTF projection, integrated closure, or polarization source is introduced.

## Known controls retained

- source-off identity;
- negative-`chi_affine` stimulated-growth branch;
- signed-zero canonicalization;
- photon/boson statistics binding;
- finite-result firewall;
- target-specific integrated moment-map binding;
- exact two-process source and binding hashes.

## Special-case audit

The path `build/` is a packaging artifact, not a kinetic state or numerical output. Moving its generation from a Git worktree to an exact `git archive` staging export cannot alter the tested source law. The tests themselves continue to import source from the exact worktree through `PYTHONPATH`; the installed distribution metadata comes from the exact archive of the same commit.

## Verdict

```text
PHYS_MATH_UNCHANGED
NO_NEW_APPROXIMATION
NO_NEW_PHYSICS_CLAIM
R6C_AUTHORITY_EFFECT_NONE_UNTIL_EXECUTED
```

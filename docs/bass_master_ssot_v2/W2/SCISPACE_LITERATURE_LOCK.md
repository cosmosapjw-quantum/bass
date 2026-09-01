# SciSpace literature lock — W2 abstract 1+3 geometry

**Search date:** 2026-09-01  
**Role:** methodological and convention-cross-check support only. Project-owned exact residuals remain the formula authority.

## Admitted references

1. Xavier Roy, “On the 1+3 Formalism in General Relativity,” arXiv:`1405.6319`.

   Admitted use: systematic splitting of a Lorentzian manifold by a timelike congruence; spatial metric, extrinsic curvature, Gauss, Codazzi, Ricci relations and evolution identities. W2 uses it to check the coverage of the semantic registry, not to replace the BASS sign lock.

2. Chan Park, “A Covariant Approach to 1+3 Formalism,” arXiv:`1810.06293`.

   Admitted use: covariant 1+3 projection structure and consistency of normal/spatial decomposition terminology.

3. Cyril Pitrou, Xavier Roy and Obinna Umeh, “xPand: An algorithm for perturbing homogeneous cosmologies,” *Classical and Quantum Gravity* **30** (2013) 165002, DOI `10.1088/0264-9381/30/16/165002`.

   Admitted use: evidence for a reproducible Wolfram/xTensor workflow based on a geometrical 3+1 decomposition for homogeneous cosmologies. Perturbation formulas are outside W2.

4. Ivan Agullo, Javier Olmedo and V. Sreenath, “xAct Implementation of the Theory of Cosmological Perturbation in Bianchi I Spacetimes,” *Mathematics* **8** (2020) 290, DOI `10.3390/math8020290`.

   Admitted use: methodology for organizing anisotropic-cosmology calculations in xAct. Bianchi-I perturbation results are not imported as BASS authority.

## Project-owned convention decisions

The references do not decide the BASS convention. W2 independently locks

```text
signature = (-,+,+,+)
n^a n_a = -1
h_ab = g_ab + n_a n_b
K_ab = +h_a^c h_b^d nabla_c n_d
nabla_a n_b = -n_a A_b + K_ab
K_ab = H_geom h_ab + sigma_ab
epsilon_123 = +1
```

The resulting Gauss/Codazzi coefficient ordering is stored in EquationIR and must receive an independent xCoba component/limit proof in W3.

## Exclusions

No admitted reference authorizes claims about all eleven Bianchi branches, the exceptional `VI_{-1/9}` sector, Einstein-background evolution, the generic-ell polarized photon hierarchy, numerical parity, local/global tilt discrimination, or scientific validity.

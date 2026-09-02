# SciSpace package-methodology literature lock

These references justify package selection and the classification of independent
verification axes.  They have `authority_effect=NONE` on BASS signs, formula
ownership, semantic hashes, provider admission, or scientific claims.

## Independent tensor CAS

- K. Peeters, **Cadabra2: computer algebra for field theory revisited**,
  *Journal of Open Source Software* 3 (2018) 1118,
  DOI `10.21105/joss.01118`.

  Admitted role: property-aware tensor canonicalization, Young-projector and
  multi-term tensor-identity checks independent of xAct.

## Independent differential-geometry environment

- E. Gourgoulhon, M. Bejger and M. Mancini,
  **Tensor calculus with open-source software: the SageManifolds project**,
  *Journal of Physics: Conference Series* 600 (2015) 012002,
  DOI `10.1088/1742-6596/600/1/012002`, arXiv `1412.4765`.

  Admitted role: a future independent manifold/chart/tensor implementation
  axis.  It is deferred from XCAS-01 because a full Sage image is outside the
  bounded CI resource envelope.

- T. Birkandan et al., **Symbolic and numerical analysis in general relativity
  with open source computer algebra systems**, *General Relativity and
  Gravitation* 51 (2019) 4, DOI `10.1007/s10714-018-2486-x`,
  arXiv `1703.09738`.

  Admitted role: methodology precedent for comparing SageManifolds,
  Maxima/ctensor and Python GR packages on common witnesses.

## Independent GR package implementations

- B. Shoshany, **OGRe: An Object-Oriented General Relativity Package for
  Mathematica**, *Journal of Open Source Software* 6 (2021) 3416,
  DOI `10.21105/joss.03416`, arXiv `2109.04193`.

- B. Shoshany, **OGRePy: An Object-Oriented General Relativity Package for
  Python**, *Journal of Open Research Software* 13 (2025) 9,
  DOI `10.5334/jors.558`, arXiv `2409.03803`.

  Admitted role: independently implemented coordinate-tensor and Einstein
  tensor witnesses.  OGRePy shares SymPy as the algebra engine and therefore
  is not counted as an independent CAS engine.

## Classification firewall

```text
independent package implementation != independent algebra engine
package installation PASS          != formula PASS
formula PASS                        != BASS semantic promotion
multiple packages on SymPy          != multiple CAS engines
```

Literature and package examples may choose useful regression witnesses.  The
BASS convention lock, exact source pins, declared domains and project-owned
EquationIR remain the only formula authority.

# CE1-AF | same-context blind-referee adversarial audit (one pass)

**Scope:** exact Liouville source derivatives, pressure quadrupole normalization, Einstein σ evolution, source provenance; distinguish program verification from mathematics, avoid auditing unrelated historical branches.

| Question / observed risk | Verification evidence | Resolution / boundary |
|---|---|---|
| Sign of E' and shear work | Direct differential of V√Q yields `E'=-θE-h·P`; independent Wolfram corrected expression outputs `{0,{0,0,0}}` for E and three Pi'. | PASS derived; signs unchanged |
| Sign of stress rank4 contraction | `P_i'=-(θ+2h_i)Pi+Σh_jRij`, `Rij=∫Vr xixj`, sum_j Rij=Pi. Independent finite-difference of ray integrals at arbitrary ell,h. | PASS bounded implementation; `Rij` PSD and trace identities checked |
| Quadrupole normalization / false temperature claim | Independent Y20 / real Y22 direct ray spherical basis vs `alpha20,alpha22`, even-reflection source, Y2±1=0. | PASS normal-frame fractional bolometric; not temperature C_l |
| W relation and shear energy coefficients | `W/E=1/2[σz(3Pz/E-1)+(σx-σy)(Px-Py)/E]`; `σ_i'=-3Hσ_i+Π_i`, `Sσ'=−6HSσ+W` derived. | PASS direct algebra and tests; W is exchange, not entropy |
| Initial W positive improperly generalized | Initial exact original six-cell moment program certifies W0>0.007175 only. Numerical GL W(u)>0 across stored [0,.08] 1604 rows. | Held: full-horizon exact sign NOT CERTIFIED |
| GL convergence mistaken for exact continuum | GL16/64 match ~1e-12 absolute, but true continuum source integration not separately enclosed here. | NUMERIC ONLY; inherited strict source identity is not full run bound |
| Model normalizations / units | Original u=t/Tstar, (-,+,+,+), E/P dimensionless Einstein RHS; raw vs fractional C2 separated. | PASS scoped, no c=1 implicit new assumption |
| Genuine distinct-author review | Native subagents unavailable, same-context symbolic+FD+negative checks not a fresh independent author. | R6/C9 distinct-author NOT_RUN, no false PASS |

**Findings:** one initial Wolfram differentiation attempt incorrectly held exponent parameter as derivative rather than ∂u ell=h; fixed expression evaluated to exact zero. Plot MathText initially rejected `\\frac12`; repaired `\\frac{1}{2}` without changing science. Same-root review is not a new formal whole-code proof.

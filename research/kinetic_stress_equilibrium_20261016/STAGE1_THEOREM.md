# Stage 1: strictly convex BASS FD96 LRS kinetic stress potential

Source base BASS PR166 `02149a6830dfe7ed214b77f5309e38350d2659fb`, original FD96 `bianchi/matter/freestream.py` Git blob `8467932c3281f9d426712b3a582f2aae3a484692`. LRS Bianchi I metric (-,+,+,+) with a_perp=a exp(-b), a_parallel=a exp(2b), s=dot b and user Sigma=sqrt3 |s|/H. Collisionless fixed canonical q, mu, positive W(mu)=1+A P2(mu), -1<=A<=2.

Let r=exp(-x), z=mu^2, k=r^2 q^2, X=k exp(2b)(1-z), Z=k exp(-4b)z, E=sqrt(m^2+X+Z). Kinetic density rho=r^3/N int[rw(q) W(mu) E], Delta=P_parallel-P_perp=r^3/N int[rw W (Z-X/2)/E]=-(1/2)rho_b.

**Exact algebraic identity**:
```
E_bb = [m^2(2X+8Z)+X^2+14XZ+4Z^2]/E^3 > 0
chi_b = Delta_b = -(1/2)rho_bb <0.
```
All numerator terms are nonnegative, strict on a positive-measure angular/radial support. Therefore rho is strictly convex as function of b at fixed canonical source and x. Delta decreases strictly from positive at b→-infinity to negative at b→+infinity. Exactly one stress-neutral root b_*(x,A,m) exists on the **unrestricted mathematical chart**, and minimizes rho at fixed source; it need not be a dynamical GR/shear equilibrium. Physical BASS implementation only accepts |b|<=1, so roots require a separate bound/numeric admission test.

At b=0, Delta=(A/5)(r^3/N) int rw k/sqrt(m^2+k). Thus sign(b_*)=sign(A), root b_*(A=0)=0. For P=k exp(2b), Q=k exp(-4b),
```
g(z)=[Qz-P(1-z)/2]/sqrt(m^2+P(1-z)+Qz)
g_z=[(Q+P/2)m^2+(1-z)(P^2+5PQ)/4+z(PQ+Q^2/2)]/E^3 >0
```
Since P2(z) strictly increases and has mu-uniform mean zero, ∂_A Delta=Cov(P2,g)>0, so implicit derivative db_*/dA=-Delta_A/chi_b>0.

With E0=sqrt(m^2+k), J1=int rw k/E0, J2=int rw k^2/E0^3, R=J2/J1 in (0,1) for m>0:
```
(db_*/dA)|A=0 = 1/(10-2R), hence 0.1 < derivative < 0.125.
b_*^NR(A) = log[(5+2A)/(5-A)] / 6.
```
The nonrelativistic expression is asymptotic only, not finite-m equality. A fixed initial-gauge b_* is NOT a gauge-independent observable and not equivalent to Sigma=0. Neither native REI full chemistry nor Einstein–Boltzmann radiation polarization is admitted.

Symbolic evidence: Wolfram Language independently returned four algebraic zeros for E_bb/g_z and their endpoint rewrites; local SymPy `stage1/test_symbolic.py` also PASS. Primary contextual literature: Heinzle & Uggla 2006 DOI 10.1088/0264-9381/23/10/016; Lee, Nungesser & Tod 2020 DOI 10.1007/s10714-020-02699-7. No claim that the specific BASS root table appears there.

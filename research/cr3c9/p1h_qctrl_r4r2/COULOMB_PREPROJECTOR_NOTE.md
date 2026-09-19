# R4R2-B Coulomb spectral-bin preprojector

The validated object is
[
P_{ell,[E_a,E_b]}=chi_{[E_a,E_b]}(H_C),
qquad
H_C=-{1over2mu}{d^2over dr^2}+{ell(ell+1)over2mu r^2}-{1over r}.
]

A flat energy-normalized validation packet satisfies
[
langle H_Cangle=(E_a+E_b)/2,qquad
mathrm{Var}(H_C)=(E_b-E_a)^2/12.
]

Executed checks:
- max within-bin orthonormality defect: `1.2465353886e-15`;
- max cross-bin overlap norm: `1.1102956687e-12`;
- minimum analytic Coulomb-F shape overlap: `0.9995650377`;
- flat-packet max norm error: `2.2204460493e-16`;
- max packet mean-energy error: `0.0497031771 eV`.

Firewall: this validates the isolated-Coulomb projector only.  Finite-z collision projection is not yet an asymptotic ionization/stripping claim; physical H-H fragmentation requires two-electron spin/exchange and asymptotic channel separation.
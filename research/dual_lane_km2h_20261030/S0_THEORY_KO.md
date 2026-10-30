# BASS KM-2H | user-owned native HYREC-2 and CLASS recombination history × original polarized Einstein Bianchi I

2026-10-30. Parent BASS Draft PR279 immutable HEAD `b7faa761af032c68b86aec0ae30b61b817171669`, inherited source `research/dual_lane_km2g_20261030/neutral_baryons.py` Git blob `c5939affd04f84d8a3ec84f57fdaa92a38345fc0`. All earlier KM2A–G, original photon sky and upper-BASS canonical DAG read only: **9/15**, KM2 **PARTIAL**, zero new upper completed nodes. This is *one source-qualified, conditional microphysics/opacity physical subunit*, not automatic admission of reionization or thermal Compton, no merge/production.

## Exact user-owned primary source authority

- Uploaded HYREC-2 original ZIP SHA256 `f0b8bba1547ae9da83a0e663f57056884c689683396e1cf9a58bee1904040ac0`, 23 archive entries; C files, helium/hydrogen radiative transfer tables, `input.dat` and original `output_xe.dat`.
- Uploaded CLASS original ZIP SHA256 `d1b2e1ce2b49de472e2cca9a327dc51c351e75bc0a2ad37d2e6538df76b289b7`, 332 entries, standalone `class` and embedded HyRec2020.
- Both ZIP CRC PASS. HYREC C executable rebuilt with gcc and user original `input.dat`, 8000 redshift rows z=8000,...,1 **byte identical** to user-provided original `output_xe.dat` SHA256 `1ac2ddad6aa0e3c4080883c71479e2e398669468e4813075ec61bca86b7afc40`.
- CLASS `make -j4 class`, original C HyRec2020 wrapper and independent thermodynamics/background code, using matching h=.6735837, Tcmb0=2.7255 K, Omega_b=.0494142797907188, Omega_cb=.31242079216478097, Omega_k=0, one massive 0.06 eV neutrino, Neff=3.046, YHe=.245, no reionization; FLRW thermodynamics `class_same_parameters_00_thermodynamics.dat`, background `class_same_parameters_00_background.dat`.
- Source overlap audit: `HYREC-2` and embedded CLASS HyRec2020 C source files are almost entirely byte identical (one history.c difference includes a CLASS wrapper correction/whitespace). Their agreement is NOT independent alternative atomic physics. Use it for **source execution and host integration parity**, not distinct-author or independent model certification.

## Exact source definitions and dimensional Thomson coefficient

Metric (-,+,+,+), c kept. `x_e(z)=n_e^*(z)/n_H^*(z)` is **electrons per hydrogen nucleus**, and can exceed one during ionized helium; it is NOT a fraction bounded by 1 at high z. We limit the conditional Bianchi experiment to *post-helium recombination*, 900<=z<=1200, where source `0<x_e<1`, assume primordial helium YHe=.245 neutral. Original FLRW physical hydrogen density today:

    n_H0 = (1-YHe)*Omega_b*3 H0^2/(8*pi*G*m_H),
    n_e^*(z)=x_e(z) n_H0 (1+z)^3.

CLASS output columns: `kappa_prime = a n_e sigma_T Mpc`, units Mpc^-1, and background `H(z) = H_SI(z)*Mpc/c` [Mpc^-1], CLASS conformal distance in Mpc; consequently

    d tau / dz = kappa_prime(z)/H_CLASS(z),
    proper gamma_Thomson(z)=n_e^*(z) sigma_T c [s^-1],
    g_eta(z)=kappa_prime exp[-tau(z)] [Mpc^-1].

Reference at z=1 because standalone HYREC C file has no z=0:

    tau_HYREC(z) = tau_CLASS(z) + integral_1^z
       [kappa_prime_CLASS(z')/H_CLASS(z')]
       [x_e,HYREC(z')/x_e,CLASS(z') - 1] dz'.

This is **FLRW HYREC/CLASS hybrid optical depth** with a common CLASS background, *not* a new independent FLRW Boltzmann solution or a Bianchi-I self-consistent recombination history. Exclude reionization; optical depth and visibility cannot be interpreted as observed CMB visibility without the reionization model and full spectral radiation.

## Bianchi-I coupling with explicit approximation ownership

Preserve original KM2G entire ray-by-ray polarized real Hermitian `P8`, collision Thomson algebra, Einstein H, shear and momentum coframe, and original free-streaming source. Only replace electron opacity by externally provided FLRW ionization field evaluated at an explicit **volume-redshift proxy**:

    z_vol(u) = (1+z_ref)*zeta(u)^(1/3)-1, z_ref=1200,
    n_H^*(u)=(1-YHe)rho_b(u)rho_unit/[(m_p+m_e)c^2 gamma_b(u)^2],
    n_e^*(u) = x_e^FLRW(z_vol(u)) n_H^*(u),
    nu(u) = n_e^*(u)*sigma_T*c*Tstar.

Here `zeta=det A` is the original baryon normal number density dilution. Baryons remain a common-velocity cold mass carrier (p+, e-, H0 and He0), with fractions: charged e/p `(1-YHe)*x_e` split by physical masses, neutral H `(1-YHe)*(1-x_e)`, neutral He `YHe`. Ionized hydrogen protons equal free electrons; total charge and current exactly zero **under common-U constraint**. All neutral/charged species share one bulk U through an ideal, externally imposed infinite collisional lock. Binding energy and chemical heating, finite electron–neutral/ion slip, helium ionization and scattering on neutral H are **not solved**. Source `T_b(z)` is recorded but NOT used in cold bolometric Thomson P8, not a thermal Compton solution. Chemical species reaction rates `x_e'(u)` are external forcing, not a solved non-equilibrium Bianchi I kinetic equation.

Local dimensionful calibration: choose `Tstar=H_BASS(0)/H_CLASS_phys(zref)` so the *initial expansion rate only* equals CLASS at z=1200; retain synthetic BASS kappa=.003, initial baryon/photon normal-energy ratio=3 and original large photon dipole. In this model `Tstar~2.186e5 yr`, initial BASS physical proper hydrogen density is **~5.74× CLASS at z=1200**, and its H(z) later differs. This is NOT a parameter-matched cosmological solution or an observational baryon density. Never erase this discrepancy to get an apparently compatible physical interpretation. Full FLRW and Bianchi results are separate datasets.

## Observable distinctions and acceptance

Run original `n_theta=12,16` (higher resolution required: `n_theta=8` finite-angle force produces constraint drift ~1e-5 at high nu and FAILS scoped old gates, no tolerance widening) for three external-opacity choices: original native HYREC xe(z_vol), embedded CLASS xe(z_vol), and frozen xe(zref) control. Compare original BASS Einstein H/shear and angular-photon anisotropic pressure, proper electron density, all per-ray optical depths, GR Hamiltonian/momentum constraints, native FLRW tau and visibility. Expected nonzero physical differences in photon opacity and sourced shear with external ionization evolution. Numerically verify ntheta16 constraints, exact charge neutrality, dimension/ray opacity, v=0 limit, zero source outside z support fails closed. Admit only `EXPLORATORY_EXTERNAL_FLRW_MICROPHYSICS`, not source-complete Einstein–Boltzmann thermo/spectral production. Upper canonical DAG **9/15**, KM2 PARTIAL, 0 new upper complete, `production_ready=false`, `merge_ready=false`, `auto_next=false`.

## Literature identifiers

Lee & Ali-Haimoud, Phys. Rev. D **102**, 083517 (2020), DOI 10.1103/PhysRevD.102.083517, arXiv:2007.14114; Ali-Haimoud & Hirata, Phys. Rev. D **83**, 043513 (2011), DOI 10.1103/PhysRevD.83.043513, arXiv:1011.3758; Lesgourgues, Comput. Phys. Commun. **182** (2011) 2638-2646, arXiv:1104.2933; Blas et al. CLASS cosmological perturbations papers. The user-supplied original ZIPs are authoritative executable source identities, these literature citations are interpretation and method context.

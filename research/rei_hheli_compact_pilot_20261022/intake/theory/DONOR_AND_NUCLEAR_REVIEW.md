# Source/theory intake: REC atomic donor and exact isotope compression

Date: 2026-10-21 UTC. Read-only donor audit; no ODE campaign, build, benchmark or source modification was run.

## Executable donor

The fetched `rec_bianchi/research/rec_rei_hheli_sandbox_20261021` contains a 62-state coupled implementation: original 40 geometry/radiation coordinates, 21 nucleus/ion populations and Thomson optical depth. Its source-based atomic coefficients, spectrum, analytic electron-feedback Jacobian, original baseline and prior scope reviews are present.

The 21 outputs are n, H1 I/II, D I/II, T I/II, He3 I/II/III, He4 I/II/III, Li6 I/II/III/IV and Li7 I/II/III/IV. H1/D/T share electronic rates; He3/He4 share rates; Li6/Li7 share rates. This equality is an explicit model approximation. Isotope nuclear inventories are separate and are preserved in all output abundance columns.

The adopted local external UV support is 5–200 eV. Photoionization, radiative recombination and dielectronic recombination are active. Neutron and tritium beta-decay maps are implemented, with zero initial populations in the main campaign. The source imposes T(z)=100+11900 Q(z) K and UV scale Q(z)=0.5[1+tanh((7-z)/0.8)]. Electron populations feed CMB Thomson damping, and the coupled H feeds the physical-time chemical rates. The gas temperature and UV reservoir are prescribed; gas energy is a test-fluid diagnostic. The absorbed energy, immediate primary-electron energy and unresolved Li inner-shell energy are separately recorded.

CI, charge exchange, molecules and thermonuclear fusion are explicitly absent. Existing source review accepts the finite conditional number model and does not claim a quantitative omitted-process error bound. There is no reason to replace the working donor with a new uncalibrated chemistry model.

## Exact 21-to-9 population representation

Let I_A be the fixed isotope inventory per baryon and f_Z,q the charge fraction for element Z. The donor uses Y_A,q = I_A f_Z,q. For a shared element, its rates depend on Z,q,T,UV and the single self-consistent electron density, not A. With zero n and T, the weak-decay terms vanish on this subspace. No donor nuclear reaction connects different element inventories.

Write U=diag(scales)^(-1)Y for the donor scaled populations. The 21x9 lift P copies the two H fractions to H1 and D; the three He fractions to He3 and He4; and the four Li fractions to Li6 and Li7. The n and T rows are zero. A 9x21 restriction R selects H1, He4 and Li7. Then R P = I_9, and, in exact arithmetic,

F(P f) = P R F(P f).

The nonlinear electron feedback does not spoil this identity:
ne = nb sum_Z [sum_(A in Z) I_A] sum_q q f_Z,q.
Every isotope of the same element therefore sees the same ne and the same transition generator. The full isotope totals and baryon normalization are recovered by the lift, rather than erased.

The reduced Jacobian is R J P. Coupling to geometry uses the same lift/restriction on the full Jacobian, including derivatives of H and ne. This is a coordinate reduction of the current finite model. It is ineligible if n/T becomes nonzero, an isotope-specific rate/threshold/initial charge fraction is introduced, or a transmuting reaction is enabled. Such changes require the full donor or a new invariant-subspace contract.

A small algebraic check of the actual donor, saved in ISOTOPE_SUBSPACE_CHECK.json, evaluated three distinct (T,UV,nb) inputs without integration. RP was exactly the identity. RHS subspace residuals were 1.26e-29 to 5.05e-29 s^-1 against scales 5.35e-14 to 2.28e-13 s^-1. Jacobian residuals were at roundoff. Initial scaled-population lifting differs by 2.71e-20 from donor bytes because separate inventory divisions round differently. This is a numerical identity, not byte identity.

HE32's exact reflection-even L8 geometry representation supplies 23 coordinates instead of 40. Keeping all four even energy/number towers and the nine population fractions plus tau gives 33 coordinates rather than 62, a 46.8% state-count reduction. This is not a measured speedup. Its proper-density interface is cm^-3, whereas the REC chemistry returns m^-3; the conversion must occur once.

## Network image and nuclear channels

NETWORK19_SCOPE.json transcribes all 19 named reactions from the provided image and gives A/charge conservation residuals (all zero after beta electrons are included). The graphical arrow placement does not faithfully encode every reaction's stoichiometry: use the reaction list for nuclear channels 6–8.

Lithium requires charge IV. Including stable primordial isotopes through lithium adds Li6. Correct decay maps are n -> HII + electron + antineutrino, TI -> He3II + electron + antineutrino, and TII -> He3III + electron + antineutrino under the donor's bound-electron-spectator approximation. REC already has these corrections.

For any finite-support photon flux Phi(E), Gamma_i=integral Phi(E) sigma_i(E) dE vanishes if its support is below the reaction threshold. REC's locally prescribed maximum is 200 eV. The listed nuclear photo thresholds start at 2.224573 MeV; adding the Li6 -> alpha+d channel lowers the minimum to 1.4743 MeV, still more than 7000 times the UV maximum. This is an exact statement for the finite-support UV model. It does not calculate an error bound for omitted thermal nuclear fusion, nor add a MeV source. A claimed full active nineteen-reaction network would need additional thermonuclear rates and a hard-photon/cascade contract.

## Primary external sources

- ACROPOLIS: Depta, Hufnagel and Schmidt-Hoberg, arXiv:2011.06518, DOI 10.1088/1475-7516/2021/03/061: https://arxiv.org/abs/2011.06518
- Author implementation, nuclear channels and thresholds: https://raw.githubusercontent.com/hep-mh/acropolis/main/acropolis/nucl.py . GPL-3.0; this intake extracts scientific threshold facts and does not vendor the implementation.
- ACROPOLIS decay parameter conventions: https://raw.githubusercontent.com/hep-mh/acropolis/main/acropolis/params.py .
- Evaluated Li6 data, 4He(d,gamma)6Li Q=1.4743 MeV: https://nucldata.tunl.duke.edu/nucldata/HTML/A%3D6/06Li_2002.shtml . ACROPOLIS's 3.698892 MeV Li6 entry is the alpha+p+n channel, not a global Li6 threshold.
- AlterBBN v2, arXiv:1806.11095: https://arxiv.org/abs/1806.11095 . This provides context and a possible future thermonuclear implementation, but no code/rate from it was activated here.
- Grackle primary paper, arXiv:1610.09591: its published networks cover H/He/D, not complete Li charge states. It is not a drop-in answer to the present isotope/ion requirement.

SciSpace and Exa were actually used; their retrieved responses are stored alongside this note. Reported repository search failure for external pynucastro was a Git connector 404, not evidence that the public project or reaction data do not exist. Existing atomic donor avoids that dependency.


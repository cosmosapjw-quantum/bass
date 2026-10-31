# KM2O | BASS dossier × VigilODE 교차조사와 물리 DAG 정렬

**As of:** 2026-10-31 KST. **Source owner:** `cosmosapjw-quantum/bass` KM2N PR297 `4137f942d2a95999f4e6627b71042e98f7afc1b7`, immutable.

**Authoritative Dropbox documents:** `/dossier/BASS_Integrated_Dossier.pdf` (rev `65dd5afc2e7910af03d47`, 933,631 bytes), `/dossier/Dossier_II_Kinetic_Transport.pdf` (rev `65dd5afc2e7920af03d47`, 410,288 bytes), plus Dossier I, III–VII read from their connector, all PDF revisions resolved from actual Dropbox metadata. These are **mathematical sources**, not evidence that the present numerical owner code implements the full dossier. No full PDF raw byte checksum was established by reading extracted text.

## Equation-to-owner mapping

- **Dossier II §1.4, Eqs. (1.25)–(1.33)**: frequency drift `dlnE/du=-H-sigma:nn`, angular transport and orthogonal screen rotation. The current original Bianchi-I owner implements the restricted Bianchi-I law and P8 screen; non-LRS generic commutator terms are not incorporated merely by quoting the dossier.
- **Dossier II §1.5, Eqs. (1.40)–(1.44)**: Lorentz Doppler `D=gamma(1-beta·n)`; electron rest angular measure `w_e=w/D²`; first `J_e=D^4 S J_n S^T`; elastic Thomson `G_e=(3/8pi)P_e M_e P_e`; normal gain `nu_rest D_out^-3 J_e` for an energy-per-log-frequency fourth moment. This is precisely the cold-electron **second gain** used here for incoming already-once-scattered *polarized* radiation. Bolometric nine-real-component source factorization does **not** assert a rank-nine result at fixed normal frequency, where Doppler resampling survives.
- **Dossier II §1.6**: thermal electron distributions, finite recoil and stimulated rates require other kernels. **NOT implemented** in KM2O.
- **Dossier IV §§1.4–1.6**: conservative photon spectral storage, shear work and current-defined opacity; a single scattering-order contribution is not a conserved total photon density. Gain/loss energy in the normal frame may differ by electron bulk work while electron-rest gain/loss is elastic.
- **Dossier V §§1.1 and 1.5–1.6**: positive retarded propagation and source-dependent comparison. The separate VigilODE WP2 exact rational certificate is for its OWN damped cubic RHS and has not been transported to BASS polarised Einstein–Boltzmann.
- **Dossier VII**: finite-aperture actual observer/analyzer requires separate sky/instrument integration; KM2O is **not an observed CMB Stokes spectrum**. Dossier I geometry, III atomic processes, VI nuclear reactions are distinct dependencies, not completed by this one source calculation.

## Actual independent project evidence and non-admission

| Lane | Observed current source | Accepted scope | Transfer into BASS KM2O |
|---|---|---|---|
| BASS owner KM2N | PR #297 HEAD `4137f942…`, source 50/50 archived original SHA/CRC | GL12/16 actual Einstein–P8–Peebles original IVP, first scattered polarized spectrum | **REAL original common-source input** |
| VigilODE BASS21 | PR #159 HEAD `0c996df…` | LRS original older BASS 50×193 ray and local Thomson atlas, 164,050 photon ray rows / 820,250 rate rows | **Different owner revision and LRS reduction; no data or DAG promotion** |
| VigilODE non-LRS screen | PR #161 HEAD `1219495…` | Source-free diagonal non-LRS geometric screen and controlled isotropic incident Thomson gain, zero BASS owner IVPs | Analytical special-case check; no general full polarized original-source equivalence |
| VigilODE anisotropic stress gain | PR #162 HEAD `02f16fa…` | Source-free anisotropic *unpolarized incoming* bolometric tensor-gain special case, 288 controlled rows | Does not implement our incoming once-polarized 1200-bin owner source; no source replacement |
| VigilODE WP1 / WP2 | PR #158 HEAD `72bd52d…` / PR #160 HEAD `cf690ad…` | Contractive dissipative ODE work-precision and exact-rational Hermite/Bernstein continuous defect; WP2 dedicated CI success but global authority CI fail | No direct BASS continuum error certificate; different RHS, norm, domain, and source |

The official **VigilODE DAG remains 7/23**; independent successor 0/12. REI central **28/88** and working **33/88** are different denominators. The upper **BASS 9/15 (21 edges)** and **KM2 PARTIAL** remain unchanged, including the separate CE1 branch. The historical root BASS `DAG.json` is an **ACCEL02** `rei.native_moments.dag.v1` file, *not* this scientific upper-graph SSOT; historic `REMAINING-DAG-v3.md` is a distinct Rust-roadmap document. Neither is overwritten.

## This bounded physical unit and next edge

`KM2N exactly-once time-transported polarized Lyα J^[1]` → `KM2O second Thomson frequency/polarization GAIN[J^[1]]` (source-backed GL12 and GL16, five physical epochs each, 12,000 spectral rows, P8 original bolometric parity and independent direct polarized pairwise Thomson audit) → **KM2P retarded J^[2] with second-scattering source and no-third survival NOT_RUN**.

The original BASS owner Einstein/Peebles IVP is **not rerun** in KM2O: only immutable saved real P8 owner data are processed. The new source is a **diagnostic subset** of the already gravitating grey photon field. It is not inserted as additional stress, does not feed Peebles, does not account for full thermal Compton or Lyα atomic transfer. No general angular or temporal error enclosure is claimed. Parent KM2N Simpson/trapezoid difference ~0.0031855 remains inherited numerical caveat, not a certified KM2O continuum error.

**Proof status:** scoped source-replay + finite-angle kernel parity + positive spectral source + direct independent saved-data audit. The exact second-scattered time-dependent photon field, higher-order scattering, atomic line / thermal closure, distinct-author R6/C9 and native subagent are `NOT_RUN`. No promotion or production: `BASS_UPPER=9/15;KM2=PARTIAL;KM2O_SCOPED=1/1_PASS_SCOPED_CONDITIONAL_ON_NEW_HEAD_CI;NEW_UPPER_COMPLETED=0;MERGE=false;PRODUCTION=false;AUTO_NEXT=false`.

# CE1AN | Original six-cell finite-amplitude Weyl curvature and anisotropic work (31 Oct 2026)

**Immutable immediate parent** BASS Draft PR #296 exact HEAD `cdd77fbbd4c9e29c202927e4fac6a6d2a4cd7d0a`. Original six-cell binary64 source SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`. Original massless reflection-even *collisionless* diagonal Bianchi I, (-,+,+,+), Lambda=0, original dimensionless 8piG=1 Einstein equations; u in [0,.08]. No parent mutation, no source replacement, no original h target mutation, no Planck likelihood.

## New physical construction and exact initial jet

For the original energy-preserving dark source direction `D=[[53,-106,53],[-203,406,-203]]/406`, define positive six-cell masses `m_e=m_0+e D`, e in {0, +/- .01, +/- .025, +/- .035}. Initial E, P_i, quartic angular stresses and initial metric h_i and ell_i are identical; the exact sixth-moment transfer is not. Let A_i=sum_jk sigma_j sigma_k delta T_ijk(0), and let `mathcal E_i=C_{0i0i}`. CE1AK/CE1AL jets imply, for *each fixed* positive-family e:

```
Delta_e P_i = (3/2) e A_i u^2 + O_e(u^3)
Delta_e mathcal_E_i = -(3/4) e A_i u^2 + O_e(u^3)
Delta_e WeylSquared = e kappa_C u^2 + O_e(u^3)
kappa_C = -12 sum_i mathcal_E_i(0) A_i <0
```

The interval previously proved for the **derivative** coefficient is `-0.002252 < kappa_C < -0.002079`. There is no order-e²*u² term (Wolfram algebraic coefficient check returned 0). The remainder is not bounded over the full original horizon; **this is not a theorem that Delta_e Weyl² is negative at all continuum times and angles**.

## Original source-owned nonlinear physical calculation

Independent local standalone six-cell generator (source files in user's CE1AN source-inclusive backup) and the GitHub CI reproduction script in this PR use the same immutable owner input, related by scientific equivalence, **not asserted byte-identical implementations**. Three GL orders 8, 16, 24, 401 actual epochs each; seven fully nonlinear positive six-cell source families and one tangent IVP per GL: **24 original Einstein–Vlasov IVPs**, including 18 new nonzero finite-source physical IVPs. Generated **8,421 actual nonlinear physical state rows, of which 7,218 are nonzero-source**, plus **1,203 tangent** and **3,609 secant diagnostic** rows.

Local GL24 u=.08: `dWeyl²/de=-8.412836003744289e-6`; e=+.035 gives `Delta Weyl²=-2.94448801820002e-7` and e=-.035 gives `+2.94449718295231e-7`. For all positive 400 sampled epochs on GL8/16/24 the central finite-source secant of Weyl² was negative. Local maxima: Einstein constraint 2.7911e-13, Weyl decomposition 1.7884e-12, integrated energy first-law log residual 1.2822e-15. These are **numerical DOP853+positive GL estimates**, *not* error enclosures or observational likelihood results.

## Dossier physical bridge (first-order equation and full integrated test)

Dropbox BASS Integrated Dossier, 2026-10-14, chapter 5.4 (Eqs. 5.25–5.30): in diagonal Bianchi I collisionless radiation `E'=-theta E - sum_i h_i P_i=-4HE-W` with `W=sum_i sigma_i(P_i-E/3)`. Evolving one extra diagnostic quadrature `J'=W/E` for *each nonlinear source IVP* verifies
```
log( E(u)*exp(4 sum_i ell_i(u)/3)/E(0) ) + J(u) = 0.
```
This is a direct energy/shear-work validation using original physical data, not a new thermal collision. Dossier 7.6 provides an adjoint/logarithmic-norm method for future continuum error bounds but **not** an already established certificate. The PDFs `/BASS_DERIVATION_DOSSIERS_20260912/BASS_Integrated_Dossier.pdf` (1,107,893 B) and `/dossier/BASS_Integrated_Dossier.pdf` (933,631 B) have near-identical extracted text apart from one terminal newline; **PDF byte identity was not established**.

## VigilODE bridge with strict source independence

VigilODE [PR159](https://github.com/cosmosapjw-quantum/vigilode/pull/159) at `0c996dfb18cec764c457ed9d9ff667d1642e3ed6` has exact geodesic and local Thomson-hazard maps for the independent BASS21 LRS photon source; source/owner differs from CE1. [PR160](https://github.com/cosmosapjw-quantum/vigilode/pull/160) at `cf690ad5ec723052e9eb6f71335f7cb3b43607a6` has a **different cooperative nonlinear RHS** continuous-defect bound; its method may guide CE1 enclosure but its source and numerical bound are **not transported**. Official VigilODE DAG 7/23, BASS CE1 upper 9/15, 21 edges. No upper nodes promoted by this CE1AN unit.

## Published literature, codes, observational data authorities

- Lee, Nungesser & Tod, *On the future of solutions to the massless Einstein–Vlasov system in a Bianchi I cosmology*, Gen. Rel. Grav. 52 (2020), DOI 10.1007/s10714-020-02699-7. Future small-anisotropy asymptotic theorem, **not** this finite-horizon sign.
- Heinzle & Uggla, *Dynamics of the spatially homogeneous Bianchi type I Einstein–Vlasov equations*, Class. Quantum Grav. 23 (2006), DOI 10.1088/0264-9381/23/10/016.
- Fleury, Pitrou & Uzan, *Light propagation in a homogeneous and anisotropic universe*, Phys. Rev. D 91, 043511 (2015), DOI 10.1103/PhysRevD.91.043511, relevant to *geodesic* benchmark.
- Official [CLASS](https://github.com/lesgourg/class_public) and [CAMB](https://github.com/cmbant/CAMB) are mainstream FLRW Boltzmann-code authorities, but **not source-equivalent to original BASS six-cell**.
- ESA Planck [PR3 products](https://pla.esac.esa.int/) DOI 10.5270/esa-gb3sw1a are public observational authority, **not ingested or fitted**.

## Claim / execution gate

Local `python -m pytest -q test_ce1an.py`: 9/9 PASS; under -O also 9/9 with pytest warning; Wolfram 4/4 zero symbolic residuals, same-author hostile audit; independent author R6/C9 **NOT_RUN**, native subagent unavailable. GitHub clean-checkout workflow must be read separately before asserting remote PASS. Source-inclusive local ZIP archived with member hashes. **Upper BASS DAG stays 9/15, CE1 PARTIAL, scoped CE1AN 1/1; new upper completed 0; PRODUCTION HOLD, MERGE HOLD, AUTO_NEXT false.**

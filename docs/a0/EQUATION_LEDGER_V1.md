# BASS Route A — A0 first-slice equation ledger

**Ledger version:** 1

**Project conventions:** `(-,+,+,+)`, BASS Riemann sign from the A0 design, explicit SI
`c` and `G`, physical derivative `D_t=c n^a nabla_a`, and normal-frame stress projections.

This ledger freezes only the equations needed by the first executable slice. Source
equations are not copied across frames or unit systems without the transformation shown.
The later photon formula core is hash-routed by
`docs/a0/PHOTON_FORMULA_CORE_INTAKE_20260810.md` and
`contracts/a0/photon_formula_core_v1.json`; its 96 formula rows are not duplicated or
silently promoted into this FLRW first-slice ledger. Its required ray-length/proper-time
adapter and independent-reproduction gates remain binding on every future photon ledger
row.

## Shared conversion map

Ellis and van Elst use a dimensionless unit timelike vector and geometrized variables in
[arXiv:gr-qc/9812046](https://arxiv.org/pdf/gr-qc/9812046). Their metric is `(-,+,+,+)`
(Eq. 67), their curvature convention is fixed by Eq. 75, and their Einstein equation
absorbs the gravitational coupling into the stress tensor (Eq. 1 and its unit footnote).
For the hypersurface normal used by BASS,

\[
\Theta_{\rm g}=\frac{3H}{c},\qquad
\sigma_{\rm g}^2=\frac{\sigma^2}{c^2},\qquad
\mu_{\rm g}=\frac{8\pi G}{c^4}\rho_{\rm E},\qquad
p_{\rm g}=\frac{8\pi G}{c^4}p,
\qquad n^a\nabla_a=\frac{1}{c}D_t .
\]

Here `rho_E=T_ab n^a n^b` and `p=(1/3)h^ab T_ab` are normal-frame projections. For
tilted matter, `rho_E` is not the matter-rest-frame density.

## Ledger rows

### A0-EQ-GEO-001 — invariant-frame commutator decomposition

Project equation:

\[
[e_\alpha,e_\beta]=C^\gamma{}_{\alpha\beta}e_\gamma,
\qquad
C^\gamma{}_{\alpha\beta}
=\epsilon_{\alpha\beta\delta}n_B^{\delta\gamma}
+a_{B\alpha}\delta^\gamma{}_{\beta}
-a_{B\beta}\delta^\gamma{}_{\alpha},
\qquad n_B^{\alpha\beta}a_{B\alpha}=0 .
\]

- Primary anchor: Pontzen and Challinor,
  [arXiv:0706.2075](https://arxiv.org/pdf/0706.2075), section 2, Eqs. 1--6,
  arXiv PDF pages 1--2. Eq. 5 is the decomposition and Jacobi contraction; Eq. 6 gives
  diagonal `n_B` and `a_B=(a,0,0)`. Their signature is `(-,+,+,+)`.
- Conversion: algebraic index renaming only, with BASS `epsilon_123=+1`. No `c` or stress
  normalization enters.
- Validity/frame: the constant `C` belongs to the Killing/time-invariant invariant frame.
  Pontzen--Challinor Eqs. 7--14 distinguish that frame from the evolving physical
  orthonormal frame. A map is required before using `C` as an orthonormal-frame commutator.
- Dimension: registry structure constants are symbolic Lie-algebra data until a frame scale
  is attached. No implicit physical inverse-length unit is assigned in the registry.
- Checks: exact antisymmetry, exact Jacobi, all-family domain/alias tests, frame-map type
  rejection, and orientation/parity metadata checks.

### A0-EQ-GEO-002 — Jacobi identity

Project equation:

\[
C^m{}_{n[\alpha}C^n{}_{\beta\gamma]}=0 .
\]

- Primary anchor: Pontzen--Challinor section 2, Eqs. 2--3, and Ellis--van Elst
  [arXiv:gr-qc/9812046](https://arxiv.org/pdf/gr-qc/9812046), section 3.1, Eq. 74.
- Conversion: none. For the homogeneous invariant frame, derivative terms in the general
  frame Jacobi identity vanish and the component relation above remains.
- Checks: exact rational/symbolic evaluation before any binary64 conversion; mutation of
  either `a_B` term or an epsilon index must fail at least one family.

### A0-EQ-BG-001 — hypersurface-normal Hamiltonian residual

Project equation:

\[
\mathcal R_H=3H^2-\sigma^2+\frac{c^2}{2}{}^{(3)}R
-\frac{8\pi G}{c^2}\rho_{\rm E}-\Lambda c^2 .
\]

- Primary anchor: Ellis--van Elst section 2.4/2.5, Gauss relation Eqs. 54--55,
  arXiv PDF page 12; curvature-sign anchor Eq. 75, PDF page 17. Eq. 55 is
  `R3=2 mu_g-(2/3)Theta_g^2+2 sigma_g^2+2 Lambda`.
- Conversion: substitute the shared map, rearrange Eq. 55, and multiply by `c^2`:

  \[
  0=3H^2-\sigma^2+\frac{c^2}{2}{}^{(3)}R
  -\frac{8\pi G}{c^2}\rho_{\rm E}-\Lambda c^2 .
  \]

- Validity: the congruence is vorticity-free and admits orthogonal spatial hypersurfaces.
  BASS's homogeneous unit normal satisfies this. Matter may be tilted only if the displayed
  normal-frame projection is used.
- Dimensions: every term is `s^-2`.
- Characterization: Minkowski, flat de Sitter, flat dust, flat radiation, Milne, and the
  next-slice Kasner handoff. Flipping/removing the curvature term must fail Milne.

### A0-EQ-FLRW-001 — total perfect-fluid energy continuity

Project equation:

\[
\mathcal R_{\rho}=D_t\rho_{\rm E}+3H(\rho_{\rm E}+p) .
\]

- Primary anchor: Ellis--van Elst section 2.2.2, general energy equation Eq. 35 and
  perfect-fluid reduction Eq. 37, arXiv PDF page 10.
- Conversion: Eq. 37 is
  `nabla_n mu_g=-Theta_g(mu_g+p_g)`. Substitute the shared map and multiply by
  `c^5/(8 pi G)` to obtain the project equation.
- Validity: first-slice FLRW total stress is a conserved perfect fluid. Interacting
  components require explicit exchange terms that sum to zero; heat flux and anisotropic
  stress require the general Eq. 35 and are not silently dropped.
- Dimensions: every term is `J m^-3 s^-1`.
- Characterization: Minkowski, de Sitter, dust, radiation, and Milne; dust and radiation
  require their analytic `D_t rho_E` values rather than finite differences.

### A0-EQ-FLRW-002 — FLRW H-dot residual

Project equation:

\[
\mathcal R_{\dot H}=D_tH+\frac{4\pi G}{c^2}(\rho_{\rm E}+p)
-\frac{c^2}{6}{}^{(3)}R .
\]

- Primary anchors: Ellis--van Elst Raychaudhuri Eq. 29, arXiv PDF page 9, combined with
  Gauss Eq. 55, PDF page 12. This row is a derived project equation, not a verbatim source
  equation.
- Conversion: in FLRW, Eq. 29 is
  `nabla_n Theta_g=-(1/3)Theta_g^2-(1/2)(mu_g+3p_g)+Lambda`.
  Use Eq. 55 to eliminate `H^2` and `Lambda`, yielding
  `nabla_n H_g+(1/2)(mu_g+p_g)-R3/6=0`; substitute the shared map and multiply by `c^2`.
- Validity: FLRW, vorticity-free, shear-free, perfect-fluid total stress. Later anisotropic
  backgrounds require their own propagation equation and ledger row.
- Dimensions: every term is `s^-2`.
- Characterization: all five FLRW cases. Flipping/removing the curvature term must fail
  Milne; changing any `c` power must fail dimensional and analytic checks.

## Source and mutation gate

Before implementation, a validator must establish that every URL above resolves and that
the cited equation/page exists in the pinned source version. A derivation artifact must
symbolically reproduce the Hamiltonian and H-dot conversions. Required negative controls
mutate metric/Riemann sign, kinematic-versus-ADM sign, one `c` power, one source projection,
one commutator sign, and each curvature coefficient. A mutation test is evidence only when
the unmutated case passes and the intended mutated case fails.

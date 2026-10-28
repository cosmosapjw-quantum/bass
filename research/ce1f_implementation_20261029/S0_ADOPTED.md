# CE1-F independent implementation S0 (adopt existing theory)
SOURCE_PARENT_BRANCH=research/bass-ce1f-tabulated-angular-certificate-20261029
SOURCE_PARENT_COMMIT=a3ddc5ed49d245e87fe393ec17e889dbc77f540d
SOURCE_THEORY=research/ce1f_20261029/THEORY.md
SOURCE_ALGORITHM=research/ce1f_20261029/ALGORITHM.md
SOURCE_PARENT_CE1E=a05906527d7dd5e5f6a653a0e4f7d977679d4a0c
SOURCE_ZIP_SHA256=9105b9ef9dd0494bbb520085b9246bd0cb2e40ce1a6c92b9a776dd260f2a34e2
S0_ZIP_SHA256=04f24f0abb8a8b1698ac076ba3031586cefd0474fd9ce448ca442751ac9a29c0
UPPER_DAG=9/15;CE1=PARTIAL

An existing sibling CE1-F branch contains theory R1–R10 and coding C1–C4. This isolated implementation branch adopts its exact positive first-octant finite-cell model and centered mean-square direction Taylor variance bound, not an independently invented smoothness assumption. Original alternative band-Fourier concept was not published as CE1-F authority.
Physical input: exact rational total cell energies, eight coordinate reflections, piecewise constant with jumps at tabular cell edges. Integer refinement preserves physical input, changes only quadrature. Source uses cell-average q_i² barycenter, no arbitrary geometric midpoint, no raw-mass normalization.
Use MPFR192 RNDD/RNDU source and Hamiltonian initial condition enclosure; compare exact-real stored discrete angular source to continuum, then propagate with all-expanding nonlinear Dini comparison; time integrator excluded. No native agent available in current session. Baseline 39 inherited tests PYTHON_PASS. No parent/main/owner changes or merge.

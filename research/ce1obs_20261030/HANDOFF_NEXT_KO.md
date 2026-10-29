# CE1-OBS scoped closeout | copied handoff (2026-10-30)

PROJECT=cosmosapjw-quantum/bass
UNIT=CE1-OBS-ANGULAR-SKY-20261030
PARENT_PR=258
PARENT_HEAD=0656e98989750de4ea19c510ff2052654aaa3eda
GRANDPARENT_PR=253
GRANDPARENT_HEAD=e4a0feba0e8709d5e996ed8ef4c9c9bf1da4c4d0
CE1P_PACKAGE_SHA256=162097533f0bc88ec5ddee8f10edcc08aaf4b81cbf2e4c14c42982dbf73ca6b7
SOURCE_INPUT_BINARY64_SHA256=022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035
UPPER_DAG=9/15
UPPER_EDGES=21
CE1=PARTIAL
PRODUCTION_READY=false
MERGE_READY=false
AUTO_NEXT=false
R6_C9_DISTINCT_AUTHOR=NOT_RUN

Physics: exactly the original positive reflection-even massless collisionless, expanding diagonal Bianchi-I six-cell source at u in [0,.08], a_i(0)=1, shear=(.2,-.13,-.07), Lambda0. Local observer comoving tetrad. Projection is energy density per observed sky steradian, NOT thermodynamic CMB temperature. No new fluid closure, input measure, spectral model or polarization source.

Science: r=sqrt(sum a_i^-2 n_i^2), e_i=a_i^-1 n_i/r, Jacobian V^-1 r^-3; J_obs=r^4 J0(n(e)); a_lm=V^-1 int r Y_lm*(e(n))dW0. Low multipoles l=0,2,4 computed for six parent history channels and all 41 times; GL40 final a20=.022309840575555663, a22=.015673816332179034, a40=-.008105712278761622. Independent moment/area/parity tests PASS at floating accuracy.

Important distinct concern: stored_ref16 max |a40-GL40| over u is 3.9163204855e-4; pressure certificates do not certify higher harmonics. GL24 and GL40 agree to ~5e-16 but this is noncertified, not continuum enclosure.

Next possible user-authorized unit (NOT started): certifiable l=4 continuum integration/ray-moment enclosure, then boundary-remapped full sky interpolation or separately specified spectral initial conditions. Do not auto-start. Do not merge parent or sibling branches. Recompute from verified original ZIP; reproduce instructions in REPRODUCE.md.

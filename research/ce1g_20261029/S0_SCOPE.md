# CE1-G S0 scope checkpoint (2026-10-29)

Parent: BASS PR239 HEAD 9de0f37955f259b5e9172ce406d1353bf7cc3695; original archive SHA256 3fffaab45822058088b1e87f2c6692e969d33f3c0ebc4b091be3987435c54f4d.

Goal: certified *exact-real continuum ODE vs recorded binary Hermite trajectory* geometry error in selected nonnegative piecewise-constant reflected angular Bianchi-I model, by combining CE1-F angular/source + initial constraint bounds with CE1-C whole-panel MPFR residual.

Fixed physical fixture: mu=[0,.5,1], phi fractions=[0,.25,.75,1], energies=[[.1,.25,.05],[.2,.15,.15]], shear=(.2,-.13,-.07), u in [0,.08], signature (-,+,+,+), Lambda=0, massless collisionless diagonal Bianchi-I. Same physical table under integer refinement.

Target: max_i |Tstar Delta H_i| < 1e-5 if a practical combination meets it; if not, report actual bound without widening threshold. Never infer all-domain, full solver, or formal MPFR-program verification.

Scientific identity: continuum E0=sum exact binary cell energy; exact stored quadrature ray/mass source, binary Hermite cubic; no poststep constraint projection or raw-weight renormalization. Parent CE1-F exact data/target retained. Parent upper DAG 9/15 CE-1 PARTIAL.

R/C stages: theory R1..R10 then coding C1..C10. Native subagents NOT_RUN_TOOL_NOT_EXPOSED; serial execution with SciSpace/Exa literature and Wolfram independent algebra. Current Python 3.13.5 PYTHON_PASS, Rust compiler not in PATH (not relevant to this Python-oracle unit).

Preservation: local create-only stage checkpoints and SHA256, GitHub isolated Draft branch only if write accepted; Google Drive/Dropbox only on actual connector acknowledgements. No owner/main/parent/other-repo mutation, no merge, no force.
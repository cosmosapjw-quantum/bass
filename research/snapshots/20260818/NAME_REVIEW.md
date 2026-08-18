# Project naming review

Current name: **BASS — Bianchi-Boltzmann Anisotropy Solver System**.

BASS is still good: short, memorable, and accurately identifies Bianchi + Boltzmann + anisotropy + solver system. Its main weakness is that the project has grown beyond a solver into an exact transport/formula authority, symbolic compiler, dynamical-manifold analyzer, and generated numerical runtime.

Recommended alternatives:

1. **BATS — Bianchi Anisotropic Transport System**
   - Best compact alternative. “Transport” now describes the project more broadly than “Boltzmann solver.”
   - Covers null-ray, polarized radiative transfer, collision, symbolic lowering and numerical runtime.
   - Drawback: BATS is a very common acronym/name and loses the explicit Boltzmann cue.

2. **BASIS — Bianchi Anisotropy Symbolic-Integrated Solver**
   - Best match to the new symbolic-numeric architecture; “basis” is also mathematically resonant.
   - Drawback: the expansion is slightly forced and understates Boltzmann/radiative transfer.

3. **BOLT — Bianchi Optical Liouville Transport**
   - Strong physics feel and emphasizes exact Liouville/transport.
   - Drawback: does not naturally name the background Einstein/dynamical-system side, and “optical” can sound narrower than photon Boltzmann.

4. **BASS-II / BASS-NG** as an architecture-generation label rather than rename.
   - Keep the established repository/project identity but call the new compiler/runtime generation “BASS-NG” (Next Generation) or “BASS-SymIR”.
   - Lowest migration cost and clearest continuity.

## Recommendation

Keep **BASS** as the project name. Use the expanded subtitle **“Bianchi–Boltzmann Anisotropy & Symbolic Solver System”** or, more naturally in prose, **“BASS: an exact symbolic–numeric Bianchi–Boltzmann transport system.”** Name the new compiler layer **BASS-SymIR** and the generated runtime **BASS-Runtime**. This preserves the strong acronym while acknowledging that the project is now more than a conventional solver.

# WSC-3 web research notes

Primary references checked before implementation:

- Wolfram `NDSolve` DAE documentation: public residual/mass-matrix representations, Pantelides and StructuralMatrix index reduction, and consistent initialization.
- ModelingToolkit structural-transformation internals: `initialize_system_structure -> alias_elimination -> dae_index_lowering -> tearing`.
- ModelingToolkit initialization tutorial: consistent initialization is a separate generated nonlinear system rather than an incidental solver detail.

These sources informed scope separation only. The BASS compiler owns its IR/pass semantics and does not call ModelingToolkit or private `NDSolve`` compiler APIs.

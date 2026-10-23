# G1A: positive homogeneous Vlasov packets and fixed-scale moment bridge

Parent: bass PR182, df2f5c78d49ea27b3d48fd2aaebb4add9f2d7f6e.
Scope selected from the requested next theory+coding loop: an opt-in collisionless
finite-measure closure, with exact same-node Bianchi-I donor mapping, local Lorentz
initialization, general Bianchi characteristic evolution, and finite coupled controls.
No collision/emission operator, chemical/thermal feedback, production activation,
old campaign replay, or global smooth-distribution convergence is included.

S0: read live parent/donor delta, restore source, derive characteristics and measures.
S1: implement/test microscopic momentum and weight evolution, boost and FD96 adapter.
S2: new small curved/tilted controls, fixed-scale Einstein coupling, figures and handoff.
Each phase has a local immutable ZIP plus Git/provider delivery acknowledgement.
R/C labels are traceability, not a fabricated count of independent discoveries.

Variables: tau=c t/L; k=p_phys/Pstar; m=m_phys c/Pstar; E=sqrt(m^2+k.k).
w = kappa L^2 c Pstar times proper-frame packet number density, kappa=8piG/c^4.
Geometry h,s,n,a is copied from the fixed-scale core, signature(-,+,+,+).
Candidate: k'=-h k-s k+R cross k+[(a.k)k-a(k.k)-k cross(n k)]/E;
(log w)'=-3h+2a.k/E. Pressure tensor=sum w kk/E, rho=sum w E, flux=sum w k.
Wolfram exact divergence, energy moment and momentum moment residuals: 0,0,{0,0,0}.

Acceptance fixed before runs: algebra/moment/covariance scaled errors <5e-12;
local Lorentz tensor parity <2e-12 for beta<=0.8; same-node donor moment parity
<2e-12 in source-density units; finite-history constraint and independently evolved
rho/flux versus packet moments <2e-8 scaled; default/tight histories <2e-8 scaled.
Mutations removing class-B weight term or boost weight Jacobian must be detected.
Finite high-order quadrature comparisons are diagnostics, not continuum proofs.

Runtime: current Python and g++ execution PASS. Native subagent NOT_RUN;
serial construction/checking plus actual Wolfram CAS, not independent agent review.
Sandbox HTTP DNS failed; connected GitHub reads worked. No remote host job.

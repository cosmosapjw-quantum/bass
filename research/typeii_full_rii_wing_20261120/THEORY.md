# Source-locked Hummer R_II and BASS Type II outer-wing boundary, 2026-11-20

Parent PR #342 HEAD b23e75dcd2e8145cb161339bf08b6e1f522626f5; original protected BASS main 9c6506e4e2087129a8b674ff10438e5db1a55c9d. All changes inside research/typeii_full_rii_wing_20261120/. BASS upper DAG 9/15 scoped, newly full production nodes0. No parent/main/production mutation.

Metric convention (-,+,+,+), h=2πħ, c and k_B retained. Define x=(ν−ν0)/Δν_D, Δν_D=ν0 sqrt(2k_BT_m/(m_Hc²)), a=A_Lya/(4πΔν_D), and φ_a(x)=H(a,x)/sqrtπ where H(a,x)=Re[w(x+ia)] and ∫φ dx=1.

For scattering angle μ=cosθ, define s=sin(θ/2)=sqrt((1−μ)/2), q=cos(θ/2)=sqrt((1+μ)/2), S=(x+x')/(2q), Y=(x−x')/(2s). A thermal Maxwell velocity decomposes into independent Gaussian components parallel to n+n' and n−n'. Integrating the latter under atom-frame coherent-scattering delta and integrating the former against the Lorentz oscillator line profile gives the classic Hummer 1962 Type-II observer-frame joint distribution:

R_II^(0)(x,x'|μ) = exp(−Y²) H(a/q,S)/(2π s q).

This formula applies 0<θ<π. It is positive, symmetric in x and x', and ∫dx'R_II^(0)=φ_a(x). The conditional kernel is P_II^(0)(x'|x,μ)=R_II^(0)(x,x'|μ)/φ_a(x). At μ=+1 the conditional is δ(x'−x); at μ=−1 its limit is a narrow Lorentz-convolved Gaussian and must be computed without dividing by q=0. The primary source is Hummer, MNRAS125,21 (1962), Section2.2; also Leenaarts, Pereira & Uitenbroek, A&A543 A109 (2012), Eq2 and Dijkstra arXiv1704.03416. The A&A HTML equation displays a missing square in the exponential transcription; the squared exponent follows from Gaussian Maxwell integration and marginal normalization.

**Scope**: This is the exact Hummer type-II formula for classical Doppler redistribution with coherent radiation-damped scattering in the atom's rest frame and sharp lower level, *without recoil*. It does not by itself satisfy full Wien/Bose microscopic detailed balance or include stimulated scattering/polarization. Keep all recoil and thermodynamic corrections as distinct later modeled factors; do not call the prior reversible pair symmetrization an exact Hummer result.

For source transport, reuse the original BASS five-state Type-II normal frame H, Doppler D, frequency κ, J/angle measure, prescribed tracer nHrest/Tm/pion and finite z=1100 source scope, without inventing new observed CMB, cosmological xe or global escape. Extend outer wings with clear finite boundary and convergence witness; keep internal ±20 core crossings and returns.

Four bounded theory+coding paired checkpoints Q1–Q4, each with remote Git readback and host ZIP SHA256+CRC. External FUSE/NTFS mount previously returned ENOSPC on a single fresh 4KiB probe despite ~1.8TB df free, do not repeat unmodified writing without actual repair. StageII historic 11/11 current canonical unproven, Join J1 0/2 FULL PASS HOLD, production=false, merge=false, auto_next=false; subagent NOT_RUN if absent.

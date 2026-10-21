# BASS–REI shared energy-source contract (2026-10-20)

The completed construction supplies one dimensional energy exchange to the donor and radiation equations, with a separate tag for nominal spectral injection and measured deposited energy. The adapter is additive C99, constant memory, and does not select a donor equation of state or activate a cosmological trajectory.

## Exact source and geometry identities

BASS integration baseline is PR174 head a85605302bb0317022eb06b498eb05b9d621de6a, tree e1d04268e647b6cb6d33374b64598fa3ec0d4131. Current REI source was read from RUN19/PR211 c9deb933, native/owner_src/axbi_sources.rs blob 36d24eb13db3fc42321cb0ddb165e003c0a086c7; source ID MD14_Z002_FESC_BB50K_13P6_100_V1. See the sibling rei_bianchi intake for the complete commit and byte identity. The original BASS executed source capsule fixes REI owner 0e25846433170d0f420c4cda44a0bedbf02cd177; the current source function is compared by byte identity, without silently replacing the old capsule.

Use metric signature (-,+,+,+), proper time t, a_perp=a exp(-b), a_parallel=a exp(2b), x=ln a, H=dx/dt>0, s=db/dt, and Sigma=sqrt(3)|s|/H. Spatial curvature is zero in this derivation. Density and pressure are measured in the normal comoving non-tilted orthonormal frame. Every energy density and pressure below has units J/m³. Define Pi=P_parallel−P_perp, radiation mean pressure U_r/3, k=8πG/(3c²), and L=Λc²/3. Donor pressure p_d is an explicit physical input.

The MD14 source owns escape fraction, 13.6–100 eV band, and total angular integration. It computes q_N=f_esc 10^logyield rho_SFR /(Mpc_cm³ n_H0), photons per H nucleus per proper second. Here n_H0 is comoving at a=1. The yield is photons/s per (solar mass/year); no additional year conversion is appropriate. The proper photon rate is the comoving rate times (1+z)^3. For spectral cells, q_H=sum_i q_N f_i E_i in eV/(H nucleus s), where E_i is the photon-weighted mean energy. Its GL weights already represent dmu/2 and sum to one; no extra 4π factor belongs in this bridge. Preserve the owner source's z∈[4,20] and existing spectral quadrature checks.

Set n_H=n_H0/a³ in proper m^-3, with the cm^-3→m^-3 factor 10^6 applied exactly once by the caller. Then Q=(1.602176634×10^-19 J/eV)n_H q_H is J/(m³ s), and S=Q/H is J/m³ per unit ln a. If input q_H is instead per ln a, first form S=(eV→J)n_H q_H and then Q=H S. The adapter requires the clock enum; it never infers a clock from magnitudes.

## Conditional evolution and constraint identity

For an isotropic donor and possibly anisotropic radiation,
\[
\dot H=-H^2-2s^2-\frac{k}{2}(U_d+2U_r+3p_d)+L,\qquad
\dot s=-3Hs+k\Pi,
\]
\[
\dot U_d=-3H(U_d+p_d)-Q,\qquad
\dot U_r=-4HU_r-2s\Pi+Q .
\]
The radiation work term follows from H_perp=H−s and H_parallel=H+2s:
2 H_perp P_perp+H_parallel P_parallel=H U_r+2s Pi. Adding the two energy equations cancels Q exactly in real arithmetic.

Define C=H²−s²−k(U_d+U_r)−L. Substitution gives
\[
\dot C =
-2H^3+2Hs^2+2kH(U_d+U_r)+2HL=-2HC.
\]
The p_d and Pi terms cancel separately. Hence a constraint-satisfying initial state remains constrained for any supplied donor closure for which these equations have a solution. This proof does not determine that closure.

If radiation receives Q+δQ while the donor loses Q, the exact diagnostic is
\[
\dot C+2HC=-k\,\delta Q.
\]
It identifies source-ledger mismatch as a forcing term. At an instantaneous frozen-volume event with common measured ΔU, U_d^+=U_d^-−ΔU and U_r^+=U_r^-+ΔU leave C unchanged. In binary64, observed total rounding defect δE leads to δC=−kδE. Preserve the defect rather than clipping either component.

Wolfram Engine evaluation returned exact residuals {constraint:0, source cancellation:0, mismatch:−kδQ, jump:0}; WOLFRAM_SHARED_Q.json preserves its actual input/output. The tests independently evaluate the polynomial with rational arithmetic. No tensor package was required for this reduced-variable identity; xAct was not executed by this lane.

## Spectral and angular ownership

The nominal spectral energy q_H and actual SourceLedger deposited energy are distinct tagged inputs. The retained native source-deposition residual 5.369926725506957e-12 belongs to discretization/ledger evidence. A conservative donor event must debit exactly the actual radiation event increment. If the physical reservoir supplies the nominal source instead, retain its mismatch explicitly and apply the forcing identity; never silently renormalize the radiation spectrum.

For fixed reference rays, R²=e^(2b)(1−mu0²)+e^(−4b)mu0², mu=mu0 e^(−2b)/R, J=dmu/dmu0=R^-3. Exactly one J enters isotropic local emission. The positive KL projection on finite rays solves alpha_i=q_i exp(lambda P2_i)/Z with d(meanP2)/dλ=Var(P2)>0, under min P2<0<max P2. It corrects newly emitted isotropic sources only. It preserves the factorized monopole, while native spectral-panel intersections can require separately measured scalar-ledger checks. These existing derivations are reused from branches 9c264c0 and 3e38ee2. New isotropic cohorts, old anisotropic radiation, and the manufactured S9 donor remain distinct owners.

## Algorithm and achieved scope

shared_q_bridge.c normalizes the dimensional input using frexp/scalbn so intermediate multiplication cannot spuriously overflow for representable final results. It computes Q and S independently, assigns donor/radiation signs from each common value, and tags the energy interpretation. Invalid frames/clocks, negative or nonfinite data, nonpositive H, true output overflow/underflow, and insufficient donor energy have explicit statuses. Failed calls leave output unchanged. Finite subnormal output is accepted and flagged. No allocation, fast-math, extrapolation, clipping, or implicit source model is used.

The event function returns the requested transfer, floating-point realized debit/credit, and a balance diagnostic calculated from error-free TwoSum residuals. The final sum of those residuals is rounded once. Its assumptions are round-to-nearest binary64, gradual underflow and no fast-math. For donor1e20, radiation1 and transfer1e19 J/m³, rounded debit and credit agree while the exact total-energy loss is1J/m³; the compensated diagnostic returns−1. The public ABI is a pure helper suitable for C, Fortran ISO_C_BINDING, or Rust FFI. Wiring it into native dynamics requires the current owner to provide the radiation increment and physical donor pressure/initial reservoir.

No new impossibility theorem is claimed. The input-dependent missing physical donor model affects the new coupled-history experiment only. Completed S9/S10 controls and source-only normalization work remain usable.

## Research-loop record

R1/C1 fix shared-Q scope and existing BASS/REI identities. R2/C2 reuse the actual source code, completed S9/S10 and fixed-ray results. R3/R4 distinguish proper/comoving density, both clocks, nominal/deposited energy and donor pressure. R5 derives the two constraint identities and event law. R6 uses actual Wolfram algebra; R7/C6–C8 use independent Decimal/Fraction and compiled C. R8 adopts the conditional identity and additive adapter at their stated scope. R9/C3–C5 provide this contract and implementation. C9 independent review is tracked separately; R10/C10 preserve this package and input-specific NCP continuation. Publication/backup acknowledgements are supplied by the parent orchestration, not inferred from local file creation.


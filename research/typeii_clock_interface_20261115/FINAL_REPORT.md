# BASS Type II: separated proper-clock, thermal and radiation interfaces

Parent PR333 immutable HEAD: 27a3c7cfb57e145ed35526d4613de2e9d613d4ea.
Current Draft PR334, branch research/bass-typeii-clock-interface-20261115-r1.
Current unit has four bounded deliverable checkpoints T1..T4, not ten newly completed production nodes.

## Scientific result and definitions
Metric (-,+,+,+), beta=v/c dimensionless; tau_H is dimensionless normal Hubble time, H_n in s^-1. For homogeneous fields, dt_n/ds_e=Gamma and d tau_H=H_n dt_n. Let L=d ln Gamma/d tau_H. Then

x_e'=R_proper/(Gamma H_n),
theta_e=Gamma H_n(3+L),
T_m'=-(2+2L/3)T_m+[K_proper(T_R-T_m)+Q_proper]/(Gamma H_n).

The temperature expression is the fixed-composition, nonrelativistic monatomic gas limit with a specified scalar reservoir; it is not a complete reacting-gas energy equation. K_proper is an inverse-time coefficient and Q_proper has K/s units. With A=2+2L/3,C=K_proper/(Gamma H_n),J=Q_proper/(Gamma H_n), the inherited first-order tracking root is (C T_R+J)/(C+A-1). The fully implicit frozen-coefficient step uses denominator 1+dt(A+C). All three actual native temperature paths were adapted consistently.

Exact local radiation interface for an isotropic normal-frame Planck field: T_e(mu_e)=T_n/[Gamma(1+beta mu_e)], n_gamma,e/n_gamma,n=Gamma, u_e/u_n=Gamma^2(1+beta^2/3), F_e/(c u_n)=-(4/3)Gamma^2 beta. Angular quadrature and Lorentz-transformed stress tensors independently validate these formulas. The normal rest temperature T_n does not itself undergo an arbitrary thermodynamic transformation; T_e(mu_e) parameterizes the directional spectrum. No unique scalar replacement is imposed on the atom kernel.

## Actual native FULL intervention results
Original HYREC computational source/header/atomic-table files remain byte-exact16/16. Original BASS source and all parent evidence stay unchanged. Copies inside this unit's ignored native_run are compiled as FULL with base8.49e-5 and half4.245e-5 atomic steps. The original2248-point H/nH input functions and parent photon geometry are common across the source comparison. Twelve native8000-row histories succeeded: legacy, reaction-only, thermal-only, both, zero-adapter and naive-global-H at each timestep. The zero-clock adapter is byte-identical to legacy at both steps; legacy reproduces the parent FULL.

On mean z300..1700, half-step both versus legacy has maximum absolute xe change 0.0001771603199984817 at z=1242, maximum relative xe change 0.00083796221151798654, and maximum absolute matter-temperature change 0.014168331648988897 K. At z1100: legacy xe=0.1364847021993157; reaction-only0.136585036119467; thermal-only0.1364847019147822; both0.1365850358349204; naive-global-H0.1365555126615443. The both/global difference reaches 7.0368752404625923e-05 somewhere in the studied interval. These are actual re-integrated atom histories, not post-hoc rescaling of xe.

Same original1167-time by26 photon characteristics, same normal H and conserved normal hydrogen current, finite observer mean z300:

| Half-step atom input | tau(+ey) | tau(-ey) | asymmetry |
|---|---:|---:|---:|
| legacy | 42.5861076679153 | 46.8247888657398 | 0.0474067631815891 |
| reaction | 42.5915024106967 | 46.8306870791563 | 0.047406406537839 |
| thermal | 42.5861076273164 | 46.8247888220196 | 0.0474067631913865 |
| both | 42.5915023700966 | 46.8306870354345 | 0.0474064065476314 |
| zero | 42.5861076679153 | 46.8247888657398 | 0.0474067631815891 |
| global | 42.5894119164272 | 46.8283996009095 | 0.0474065246347528 |

Both minus legacy optical-depth changes are +0.0053947021813485208 and +0.005898169694702915 on the two axes. This observable is conditional scalar attenuation, not today's CMB visibility or the full scattering gain/polarization solution.

## Numerical and implementation evidence
Base-to-half maximum absolute xe difference for the both lane is 5.4619542366740603e-07. More directly, the clock-effect difference (both-legacy) changes by at most 1.4498306999399801e-09; at z1100 its change is 4.5682596594431857e-11. These are empirical successive-step checks, not an unproved global convergence theorem.

Gauss8/16 photon integral maximum discrepancy: 1.5595702507198439e-10; independent Simpson discrepancy: 6.8443895884229278e-08; parent optical-depth reproduction discrepancy: 1.4210854715202004e-14. The background clock/radiation source Codazzi residual is 2.8449465006019636e-16.

Ten analytic tests passed normal and optimized Python (20 executions). Native C component probes at eight state/lane combinations validate tracking, differential and implicit thermal paths and the reaction clock to relative 2.1061207394491782e-16 / absolute 1.1102230246251565e-16. Five invalid native clock cases reject with exit7. Fresh FULL-half rebuild/replay is byte-exact. Optimized analysis gives byte-identical JSON/CSV results. Actual logs and source identities are preserved in VERIFICATION.json and NATIVE_RUNS.json.

## Exact radiation result versus missing atomic coupling
On the declared discrete source grid300<=zmean<=1700: maximum energy-density boost 0.0033383808558355987, number-density boost 0.0012511101825938287, absolute dimensionless energy flux 0.066800593269716463. Matching only the boosted energy with one blackbody temperature produces a photon-number mismatch of up to 0.0012500681131990543. These are exact local Lorentz-moment evaluations on a prescribed isotropic normal Planck field, not a global Bianchi radiation solution.

Radiation spectral/angle-dependent photoionization, electron-frame Compton exchange, variable-composition thermal terms, anisotropic line transfer and metric backreaction remain unresolved for the complete physical model. The current experiment implements separated-clock and thermal interfaces while deliberately keeping the old scalar radiation/escape closure. Its limited claim is clear and testable.

## Publication and next action
T1..T4 each have a Git checkpoint, remote HEAD readback, host archive and external-disk identical copy. The final receipt resides outside Git to avoid a self-referential HEAD. Parent/main are not modified. Local unit4/4 scoped complete; BASS upper9/15 scoped/source-mapped, new full upper nodes0. StageII11/11 is historical only and current canonical evidence remains unestablished; JoinJ1 remains0/2 FULL PASS HOLD. No native subagent or distinct-author referee; same-author hostile review completed. Production_ready=false, merge_ready=false, auto_next=false.

Next unit: ELECTRON_FRAME_SPECTRAL_PHOTOIONIZATION_AND_COMPTON_CLOSURE. Use the exact directional photon distribution and original cross-section/rate provenance to derive and validate collision moments before coupling to the native atom paths. Keep the proper reaction clock, thermal expansion and photon propagation separately identifiable.

Primary literature: Ali-Haimoud and Hirata, arXiv:1011.3758; Lee and Ali-Haimoud, arXiv:2007.14114; Ford and O'Connell, arXiv:1310.3238. Source-specific implementation claims rely on the byte-locked original C and current native execution records, not the papers alone.

# REI-F08 S0 original hat spectral support: exact physical counterexample

## Authority and conventions
BASS branch parent is PR #317 at 18e6273f28ea67e472c919de86594f70fd1c81c9. Original REI F08 saved 16000-step source, 16,001 proper-clock H/He material history and 8x16 angular, 17 spectral-node V1 photon checkpoint are copied byte-exact with all SHA256 locks. Metric (-,+,+,+), ds²=-c²dt²+sum_i a_i²dx_i², a_i=exp(H_i t), H_BI=(1.01,.99,1.00)×10^-14 s^-1 and H_FLRW=(1,1,1)×10^-14 s^-1. All proper times 0..10^13 s. Original S0 starts with 0.05 photons per H and injects 5×10^-15 photons per H per second at 13.7 eV; no CMB blackbody.

Exact null characteristics conserve spatial Killing covector: E(t)/E_birth=sqrt(sum_i n_birth_i² exp[-2 H_i (t-t_birth)]). All source photons satisfy E≥13.7 exp(-H_max t), independent of neutral-H absorption, which only removes photons. The source BI lower bound at t=6.25×10^8 s is 13.699913519022955 eV; at t=10^13 s it is 12.383882550536338 eV. Source FLRW final bound is 12.396272627092644 eV.

## Exact original spectral hat suboperator
Original source owner rust/rei_microphysics/src/paired_runtime.rs has frozen SHA256 b6c1d2a07ab51ff02318139ae18387b77f61859c08037347f788524df770ebe7. The original energy_nodes includes E_11=13.675 eV and E_12=13.7 eV. Its endpoint computes r_d=g(q_d,t1)/g(q_d,t0), g(q,t)=sqrt(sum_i q_i² exp(-2H_i t)). It maps each discrete photon energy E_j→E'_j=r_d E_j and applies the nonnegative hat(E'_j,E_nodes,k).

For E_(j-1)<E'_j<E_j, the original two weights are p_lower=(E_j-E'_j)/(E_j-E_(j-1)) and p_upper=1-p_lower. This preserves photon number exactly and the first energy moment, p_lower E_(j-1)+p_upper E_j=E'_j, but generates positive spectral variance (E'_j-E_(j-1))(E_j-E'_j). The original FIRST actual step has E'_12≥13.699913519 eV but assigns positive photon weight to 13.675 eV, which is below *every physically allowed S0 source photon energy* at that time. This is an exact fixed-grid/source-specific counterexample to support-preserving transport, not a general no-go for all photon-conserving methods.

The native 8x16 angular source directions produce total spurious first-step low-node mass 0.00017124946478640907 photons/H for BI, and 0.0001712494648448252/H for FLRW, before photoabsorption. Directional downweights are approximately 0.003394..0.003456. Independent Wolfram extremal Bianchi direction yields E'=13.699913519022955 eV, p_lower=0.0034592390817651613, variance=2.154545466712719e-6 eV².

## Actual original source checkpoint
The two source V1 checkpoint files each contain 2,176 saved photon weights plus 128 guard counts and energies. Their exact SHA256 values are in LOCKED_CHECKPOINT_SHA256SUMS.txt. For BI at t=1e13 s:
- Original photon_n=0.050070816545420574/H and photon energy 0.6419113223206975 eV/H.
- Original below exactly allowed source energy range: 0.011730393740032726/H = 23.427606237241555% (in-grid nodes below 12.38388255 eV PLUS guard exactly once).
- Original sub-10-eV guard: 0.0010016543797005874/H = 2.000475% of original photons.
- FLRW original below exact source support = 23.427273065531154%, showing that anisotropic expansion is not required for the defect.
The actual original source photon_n history already includes the guard. No double counting is allowed.

## Original operator replay and frozen physical absorption
With exact original source 16,000 proper-time steps, original 8x16 sky, original 17 energy nodes, original hat and q-dependent g, and original endpoint source_weights∝exp[-sum_i H_i t]/g(q,t)^3, recompute:
PASSIVE_REMAP_ONLY: original 0.05/H initial + 0.05/H injected, no H I absorption. Final N=0.1/H (up to 1e-14) and redshift-step energy-moment residual ≤6.66e-16 eV/H.
FROZEN_HI_IMPLICIT_ABSORPTION: same original source plus original 16,001-sample H/He x_HII(t) (thus n_HI=n_H[1-x_HII]), original Verner96 HI fit and original *implicit frozen-material* attenuation f(E,t)=1/[1+Δt c n_HI(t) σ_HI(E)] at each 6.25e8 s original endpoint. Gas/thermal solver roots, photo-heating and electron feedback are FROZEN, not replayed.

BI frozen result N=0.05008021641368748/H, versus original 0.050070816545420574/H, relative +0.018773147544770552%; guard=0.0010017367237961723/H, versus original 0.0010016543797005874/H; under-exact-min fraction frozen 23.429788178772085% versus original 23.427606237241555%.
The close replication of the full original support defect by the isolated original hat operator is physically informative, but it is NOT proof that remapping alone explains the entire -6.13040948% independent exact-characteristic vs original F08 total photon discrepancy; gas/root/spectral-collision coupling and source birth/absorption integration differ.

## Constructive physical repair constraint
With only fixed grid nodes 13.675 and 13.7 eV available, an exact redshifted photon at 13.699914 eV cannot be represented with strictly source-supported positive photon counts and exact first moment: the 13.675 node violates physical support while choosing only the 13.7 node changes the mean energy. A physically support-preserving next source-owner representation needs genuine off-grid photon characteristic energy tags, moving/adaptive support boundary, or equivalent exact continuous source-energy moments. Do not directly alter the original REI solver from a BASS worktree.

Literature: Fleury, Pitrou & Uzan (2015) Phys Rev D91 043511 DOI 10.1103/PhysRevD.91.043511; Petkova & Springel (2011) MNRAS 415,3731 DOI 10.1111/j.1365-2966.2011.18986.x. The actual hat operator and V1 physical output are measured from original user-source code/checkpoint, not assumed from literature.

Scientific status: DERIVED original fixed-grid one-step counterexample; numerically checked 16k-step source suboperator; source-owner chemistry/thermal IVP NOT replayed; F08 admission HOLD. REI central 28/88 (Δ0), Working 33/88 nonadditive, Physical Fast 4/7; BASS 9/15 scoped/source-mapped (Δfull0). F05 first original tick161 still not accepted, F09 provider-domain blocked. PRODUCTION HOLD, NO_MERGE, NO_FORCE_PUSH, NO_TOLERANCE_RELAXATION, AUTO_NEXT=false.

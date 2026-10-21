# PILOT01: research and implementation decisions

## Question and execution target

Produce the first actual signed initial-condition sweep for the normalized
shear and anisotropic stress of a non-tilted LRS Bianchi I model on 2026-10-21.
The immediate unit is 81 initial conditions, each with 64 actual coupled steps
from a=0.1999 to a=0.2. This is a warm short-interval preliminary result. It
does not replace a cold z=20 to 4 campaign or a general non-LRS Bianchi I sweep.

The user's current instruction excludes detailed optimization benchmarking.
Implementation equivalence, physical coordinate mapping, source identity and
the owner's existing per-step acceptance gates are still necessary. No new
speedup number will be inferred from execution duration or other models.

## Reconciliation of current evidence

GitHub catalogues cover all returned branch and all-state PR pages for six
repositories: BASS (260 branches, 175 PRs before this new PR), REI (253/211),
VigilODE (183/78), bass_cr (166/89), BASS_HE (86/81), WU088_HH (135/126).
Cataloguing every branch is not equivalent to reading every source line.
Latest relevant source, result, handoff and pending-state records were read;
the raw catalogue and selected immutable identities are in evidence/.

The supplied 20-attachment set and local inventory were inspected as
historical inputs. Latest provider records supersede old pending labels:
BASS S12 actually finished 17 NCP jobs, reusing 16 successful jobs after one
parallel warm-up failure. Its complete returned archive was downloaded and
SHA256-verified. Its 14 manufactured extended histories and existing 64-pack
parallel comparison are reusable evidence, not work to repeat today.

Dropbox folder listings reached their reported ends for the three selected
folders. Drive's large atomic parent returned its 1000-item cap and is not an
exhaustive inventory. Personal Context returned an actual service error.
Thus this study makes no all-conversation or account-wide exhaustive claim.
The available current conversation, attached handoffs, repository records and
downloaded selected backups provide the reconciliation used here.

## Why original C15 is the execution owner

REI PR141 commit 80825585f9fe31d2ee0d5af545ada3fa1f52be72 contains a directly
executable coupled owner: Einstein shear, massless gamma/nu hierarchies,
positive finite-mass Vlasov quadrature, a native MD14 stellar source and
Grackle Case-A H/He chemistry. Its source and rate tables are supplied with
the exact owner snapshot. Later transport/orchestration/rate branches solve
different subsets of the full scientific problem; branch recency alone is
not evidence that they form a compatible closed replacement for C15.

The C15 KAPPA constant is 8*pi*G/(3*c^2). It is the Friedmann coefficient,
not the coefficient in the requested pressure norm. The adapter uses
kappa_time=3*KAPPA and exports both half-contraction and Frobenius norms.
Its pressure D is the sum of the four physical stress contributions. The
owner's switched Pi_total_source is retained separately and is not treated
as a dimensionless Pi. The theory, units and positive initial-family mapping
are derived in physics/THEORY.md and fixed in PILOT_CONTRACT.json.

## Optimization decisions and their evidence

| Candidate | Decision for this pilot | Reason and remaining evidence |
|---|---|---|
| Existing NumPy vectorized angular/radial/source operations | Reuse unchanged | Already inside the selected exact owner; preserves reduction order and physics |
| Shared source/rate/radial/angular preparation | Implement | These constructor fields are invariant across this fixed family; readonly arrays, fresh mutable case state; independent RHS and short-step equivalence checks |
| Independent case/group multiprocessing | Implement | No cross-case physics dependency; deterministic aggregate order; one numeric library thread per worker |
| Adaptive shared-host admission | Implement | Uses affinity, cgroup quotas/usage, sampled idle CPU, available memory and own estimated/resident memory; other jobs continue |
| Exact completed-result reuse | Implement for whole groups | Source/input/toolchain and declared output hashes checked; changing worker width does not change science identity |
| Per-case reuse after regrouping or half-finished group | Defer | Would need a separate case-level receipt layer; existing complete groups are sufficient for this 81-case unit |
| C21K epoch cache | Reuse invariant-only pattern | Its fixed-fixture epoch key cannot be assumed sufficient for evolving C15 gas, radiation and anisotropy |
| RUN19 HHeD dense rate accelerator | Preserve as a future supplier | Different chemistry/source contract; silently replacing the current 129-node owner table would change the scientific experiment |
| HE29 packed atomic kernel / HH block solver | Preserve supplier evidence | Their atomic-state problems are not the C15 evolution kernel; new speedups cannot be transferred between workloads |
| VigilODE latest solver branches | Retain as future candidate | Latest 2026-10-21 plan still lists dense error-enforcement and global-error issues; switching the integrator today would add an independent change |
| Reduced angular order / radial nodes / source spectrum | Do not use as acceleration in this result | Such changes alter discretization error and require an accuracy study excluded from today's task |
| Threaded BLAS inside each worker | Disable | Nested pools can oversubscribe a shared 64-core host; independent cases are the natural parallel unit |
| GPU/JIT/new compiled extension | Defer | Not necessary to complete this small pilot and would introduce a new toolchain/owner-equivalence obligation |

For the current 8-CPU-capped host, group size 3 makes 27 independent jobs and
amortizes fixed preparation across three trajectories. On an actual NCP host
the profile permits up to 64 available cores and 128 GiB, constrained by the
observed machine/cgroup capacity. These are ceilings, not promises of idle
resources. Idle resources may remain if fewer independent jobs are pending.
Completed pilot work should not be repeated just to occupy hardware.

## Physics acceptance and limitations

Each requested coordinate is realized in the common positive initial angular
family W(mu)=1+alpha*P2(mu). The allowed interval is -1<=alpha<=2; the selected
grid needs |alpha|<=0.410579. The initial pressure per alpha is computed from
the actual massless and finite-mass owner moments, including the factor 1/5.
No negative weight or physical stress is clipped. Below the absolute Pi floor
3e-13, signed raw values remain exported with an unresolved label.

Magnitude coordinates do not determine the signed evolution: sigma:pi=2*s*D.
All four nonzero sign combinations are therefore included. The input family
does not claim to close later stress evolution from Sigma and Pi alone;
the original higher multipoles and quadratures continue to evolve.

The original photochemical number, energy and massless number-monopole gates
are preserved. Successful finite-step gates do not establish angular,
spectral or temporal convergence. Tiny thermochemical changes are stored but
not described as resolved effects without a paired error comparison.

Full stellar/emitter and escaped-radiation energy-momentum pairing remains an
open owner-level requirement. Gas nonrest energy is included in the H source;
it must not be reported as missing. The small incremental donor/escape energy
estimate in the scope audit is a conditional fixed-state H estimate, not a
global trajectory or observable error bound. The MD14 source, warm gas IC and
short interval must remain in figure captions and handoffs.

## External literature and software use

SciSpace and Exa located primary Einstein-Vlasov texts. The Lee-Nungesser-Tod
massless Bianchi I paper (arXiv:1911.04937) and Heinzle-Uggla Bianchi I dynamics
paper (gr-qc/0512031) support the geometric/kinetic formulation and dependence
on distribution moments. Their asymptotic results are not transferred to this
driven warm reionization calculation. Wolfram returned the exact tensor
contractions, positive-alpha domain and constraint identity; its symbolic
undefined-global warnings are retained in physics/EVIDENCE.json.

The implementation uses installed NumPy 2.3.5 and SciPy 1.17.0 with the
existing owner PCHIP and DOP853 routines. Official PCHIP documentation explains
the interpolator's shape-preserving behavior; it is not a replacement for the
owner's physics/rate-domain checks. Python subprocess argv execution keeps
each independent job in its own process group and explicit thread environment.

Primary links:
- https://arxiv.org/abs/1911.04937
- https://arxiv.org/abs/gr-qc/0512031
- https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html
- https://docs.python.org/3/library/subprocess.html

## Staging and publication

Stage 1 records intake, obsolete-state reconciliation and the first DAG;
GitHub commit e9f772068569bdbc2b083f89ae3f721262eab11d and a completed Dropbox
upload receipt are recorded. Stage 2 freezes the source, contract and minimal
independent checks before the actual sweep. Stage 3 adds complete histories,
plots, result review and copyable continuation instructions. Each archive has
an immutable content manifest and an external publication/upload receipt.
Archive self-referential hash/receipt rewrites are deliberately avoided.

All changes live on additive BASS draft PR176. No upstream physics owner is
edited, no unrelated process is terminated, and no merge is performed.

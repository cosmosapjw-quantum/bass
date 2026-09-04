# BASS REC Source R8 — Constant-Pair Dual Adapter GREEN Candidate

## Status

The exact R7 local replay observed the intended TDD RED:

```text
PASS_EXPECTED_R7_FULL_GRID_SPECTRAL_PSTF_ADAPTER_RED
12 tests / 10 assertion failures / 0 errors / 2 controls
```

R8 adds one dependency-light production module:

```text
bianchi/source_adapters.py
```

No solver loop, REC atomic physics, native backend route, integrated-state closure, physical face, provider or inference path is changed.

## Bounded contract

One immutable photon/boson constant source pair

```text
C[f] = eta*(1+f)-kappa*f = eta-(kappa-eta)*f
```

is applied to:

1. explicit full spectral/angular occupation samples;
2. caller-declared spectral PSTF/harmonic coefficients with explicit coefficients for the unit field.

Receipts bind source payload, physical state parent, representation, projection contract, time basis and output values. Distinct representations retain distinct representation identities while sharing source and physical-parent identities.

## Time bases

```text
PHYSICAL_TIME  divisor = 1
Q_TIME         divisor = H_s_inv
RAY_LENGTH     divisor = c_m_s
```

Physical-time rates have units `s^-1`; Q-time source values are per dimensionless `tau` when `d tau = H dt`; ray-length values have units `m^-1` after division by explicit `c`.

## Scope firewall

The first adapter accepts only pointwise-spectral photon/boson constant pairs. It rejects radial-integrated angular states and finite integrated-J hierarchies. The PSTF route enforces the constant-source work-rank condition `L_work >= L_out`.

## Required local replay

Run:

```bash
git show <publication-head>:scripts/research/run_bass_rec_source_r8_green_local.sh \
  | BASS_REPO="$HOME/Dropbox/bianchi/bass" bash
```

Required result:

```text
PASS_BASS_REC_SOURCE_R8_CONSTANT_PAIR_DUAL_ADAPTER_GREEN
33 focused tests PASS
deterministic and input-sensitive output hashes
adversarial probes PASS
clean worktree
```

Until that receipt exists, this branch is a source-level GREEN candidate only.

# BASS-8B.2A-R1 local exact-host replay receipt

## Bound state

- Branch: `agent/verify/bass-8b2a-r1-exact-host-20260824`
- Replay source HEAD: `31c121bf923b1091f6eeb013347a21c0e0a29f6c`
- Canonical candidate package identity: `caf3113fe56204652cb844f51cbce90a48e1c00cb1ffa4ff98ae80bd4a670d36`
- E4 authority archive: `BASS8B1E4_TRAJECTORY_ORIENTATION_AUTHORITY_20260823.zip`
- E4 archive SHA-256: `d7590182b52d7bb30f537232993f2bb954a049d530138b0325474633926ec766`
- Runtime: Python 3.13.7 on Ubuntu 24.04.4, JAX CPU backend

## Archive and host binding

- Six archive-part checksum gates: PASS
- ZIP CRC: PASS
- Outer archive SHA-256: PASS
- Detected layout: `repository-root-layout`
- Authority root relative to extraction: `electron_testfield_work/repo`
- Normalized adapter:
  - `normalized-host/source -> <extraction>/electron_testfield_work/repo`
  - `normalized-host/tests -> <extraction>/electron_testfield_work/repo/tests`
- Adapter form: two directory symlinks outside the restored archive
- Complete-root gate: all four owner modules and all four predecessor tests resolved under the same authority repository

## Payload and owner provenance

- Reconstructed candidate payload hashes: 5/5 PASS
- Expected payload hashes: unchanged
- Candidate runner hash: `03bdbc3740d91d14550fc3828f050e3335ce571a0a93d7740e1ce6d06f524de4`
- Owner provenance hashes accepted by the frozen candidate runner: 4/4 PASS
- Owner hashes:
  - `electron.py`: `f5fa2da696453ea0b11cfddeb7f824cd1bdb42596cd4e2947fb7841e1387aafe`
  - `electron_rate.py`: `27fe46756023380078fc503e8fe2ea5e976504314e206f55613d06af61f4be1a`
  - `electron_validity.py`: `58928b738e600a1b379d5d8b4ae79a3279e7997382a7da952f7267ebbb7846fe`
  - `electron_trajectory.py`: `fd7045723df0bbb98077f86c56b5763d4f4d490b8ebaa483d7197ba8c4a30eea`

## First failure and bounded patch

- First exact-replay failure classification: `OPTIONAL_DEPENDENCY_OR_IMPORT_FAILURE`
- Reproduction: candidate focused tests passed 15/15, then real-schedule integration collection failed because restored `bianchi/__init__.py` imports `jax` and the workflow's replay-only environment did not install it.
- Authority dependency provenance: restored `requirements.lock` freezes `jax==0.10.2` and `jaxlib==0.10.2`.
- Single minimal patch: add only those two authority-pinned dependencies to the workflow replay-install block.
- No candidate code, candidate tests, replay runner, owner source, or predecessor tests were modified.
- Targeted closeout: real-schedule integration 3/3 PASS.
- Post-patch workflow validation: `YAML_PARSE_PASS`; all six `run:` blocks pass `bash -n`.

The first attempt to create a Python 3.13 venv also exposed a local launcher-symlink issue before replay: invoking `~/.local/bin/python3.13` recorded the symlink directory as `pyvenv.cfg` home, so `ensurepip` could not import `encodings`. Recreating the temporary venv with the same interpreter's resolved executable fixed that local bootstrap issue. It caused no repository change and is distinct from the classified first exact-replay boundary above.

## Exact replay results

| Gate | Result |
| --- | ---: |
| Candidate focused tests | 15/15 PASS |
| Real independent schedule integrations | 2/2 PASS |
| Real comoving schedule integration | 1/1 PASS |
| E1 `test_electron_test_field.py` | 13/13 PASS; 14 subtests PASS |
| E2 `test_electron_collision_rate.py` | 13/13 PASS; 16 subtests PASS |
| E3 `test_electron_thomson_validity.py` | 20/20 PASS; 16 subtests PASS |
| E4 `test_electron_trajectory_authority.py` | 28/28 PASS |
| Combined predecessor replay | 74/74 PASS; 46 subtests PASS |
| Owner before/after comparison | identical |
| Final marker | `BASS8B2A_EXACT_E1_E4_REPLAY_PASS` |

`owner_before.sha256`, `owner_after.sha256`, and the later `owner_final.sha256` are byte-identical. The later check includes the four separately counted predecessor-suite runs.

## Verdict and claim boundary

`PASS_EXACT_E1_E4_HOST_REPLAY__NO_OWNER_MUTATION`

- Row 7 remains blocked.
- Row 8 remains blocked.
- BASS-8B.2B was not started.
- BASS-3 was not started.
- No authority row was promoted.
- No PR, merge, or tag was created.
- No projector, paired-left-functional, VI0 classifier, solver/runtime, or production wiring work was performed.

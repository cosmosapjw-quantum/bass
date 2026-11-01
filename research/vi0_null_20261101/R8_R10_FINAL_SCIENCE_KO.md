# BASS VI₀ physical null-Liouville 및 움직이는 scalar Kato: R8–R10 최종 과학 판정

**실제 원본:** `cosmosapjw-quantum/bass`, immutably pinned parent PR #311 HEAD `8d15551c2e0127ede4344f0969f8b7e251a09e3e`; BASS main formula identity `9c6506e4e2087129a8b674ff10438e5db1a55c9d`. 이 결과는 원래 Type-II/VI₀ production critical path의 `G-DYN-MANIFOLD-VI0`에 직접 기여하며, CE1/KM2 같은 병렬 과학 subletter를 연장하지 않는다. 기존 CI/생산 원본은 무수정.

## R8: 과학적 판정 및 원래 DAG

정확한 물리식: class-A VI₀ `N=diag(0,p,-r)`, `p,r>0`, `Σ=σ/H`, 시간 `dτ=Hdt`, signature `(-,+,+,+)`, epsilon123=+1의 orthonormal-frame null geodesic은

\[
\begin{aligned}
(n^a)' &= -\Sigma^a{}_b n^b+(\Sigma_{bc}n^bn^c)n^a-\epsilon^a{}_{bc}n^bN^c{}_dn^d+W^a{}_bn^b,\\
(\ln E)'&=-1-\Sigma_{ab}n^an^b,\\
(\ln w)'&=3\Sigma_{ab}n^an^b,\qquad (\ln I)'=-4(1+\Sigma_{ab}n^an^b).
\end{aligned}
\]

여기서 `I0(n)=1`은 **새로운 충돌없는 양의 시험광자장**이며 기존 기하와 상호작용하지 않는다. 따라서 원래 gamma-law fluid와 Einstein 방정식에 복사 스트레스-에너지를 추가하지 않는다. 구면 위 shear 흐름의 `div=3S`, 비가환 곡률 흐름 및 W 회전의 divergence=0이므로, angular volume Jacobian `w`의 진화가 필수다.

시간에 따라 이동하는 ray grid의 original scalar oblique projector:

\[
P=\frac{ra^T}{a^Tr},\quad r_\alpha=\frac{(1-v^2)^2}{(1-v\cdot n_\alpha)^4},\quad a_\alpha=w_\alpha(1-v\cdot n_\alpha),\quad K=[P',P],\quad [K,P]=P'.
\]

`P'`는 **v', n', w' 전체**를 미분한 결과다. 순수 gauge `v'_W=Wv, n'_W=Wn, w'_W=0`에서 P'_W=0인 반면, 물리 shear/curvature에 대한 P'는 일반적으로 0이 아니다. 이 연결은 oblique이며 보편적 unitary transport 증명이 아니다.

**새 과학 결과:** 원본 VI₀ 배경 12개, 서로 다른 각도구적 AXIS6/LEBEDEV26/GL8x16 3개로 총 36개 새로운 photon transport IVP를 풀이; 41 샘플씩 78,720개 실제 ray physics 행, 1,476개 energy/pressure 모멘트 행. 원본 VI₀ 배경 12개를 독립적으로 재적분하되 새 물리학적 중력 IVP 12개를 새로 발견했다고 중복 계상하지 않는다. 양의 시험광자장 `I0=1`은 실제 관측 자료도 자기일관적 광자-matter plasma도 아니다.

최대 스코프 검산: |n²−1| `3.559652572704408e-11` (ODE), |I/E^4−1| `1.9984014443252818e-15`, finite-grid radiative energy moment identity |ρ'+4ρ+Σ:P| `1.7763568394002505e-15`, Kato/oblique projector algebra `2.220446049250313e-16`, 순수 프레임 gauge P'_W `1.1539877807039334e-17`.

12배경 물리상태에서 128광선과 Lebedev26 최종 에너지밀도 차이 최대 `9.769146802729445e-6`, 128대6축 최대 `0.0017285106620045787`. 6축은 고차 이방성의 angular Jacobian을 보존하지 못함: 최종 ∑w−1의 최대 편차 약 `0.05704448533038897` vs GL128 최대 `6.597116135598213e-7`. 이는 원래 *고정된* 저차 구적의 불완전성과 실제 면적 Jacobian의 유한 보간 오차를 구분해야 한다는 경고다.

### CLAIM GATE

- **DERIVED_EXACT (within source/scalar geometry):** BASS 구조상수에서 얻은 null 방향, 에너지, sky divergence/Jacobian, collisionless intensity and first two moments, moving oblique projector의 전체 체인룰.
- **NUMERICALLY_CHECKED_SCOPED:** 36 실제 test-photon transport trajectory groups, 78,720 ray rows; unit sphere error ~3.6e-11, bolometric invariant and moment identity ~2e-15; GL refinement is finite-resolution, not certified uniform convergence.
- **IMPLEMENTATION_VERIFIED_LOCAL:** 15 normal pytest PASS; separate explicit RuntimeError-based RHS-free numerical audit both normal/`python -O` PASS. `python -O pytest` raw assert-optimized output is intentionally not claimed as a scientific validation. In fresh clean GitHub checkout, verify original 7 Git source blobs, then new tests and real physics regeneration before declaring remote CI PASS.
- **NOT_DERIVED/NOT_RUN:** polarization screen parallel transport, collision Thomson source and ionization history, full spectral Einstein–Boltzmann feedback, continuum/angular + global ODE error enclosure, general non-principal/gauge chart and degeneracy, CMB likelihood or Type-II production host preflight.

**원래 BASS DAG:** 2026-08-21 `G-DYN-MANIFOLD-VI0=PARTIAL`, `P-MIG-II-PREFLIGHT=OPEN`, Join J1 **0/2 FULL PASS HOLD**. 다른 15-노드 BASS upper 과학 DAG는 **9/15 scoped/source-mapped 그대로**, 신규 완전 완료 상위 노드 0. 원래 J1 production-ready node도 증가하지 않았다.

## R9: theory-to-code-to-observable provenance

| 정확한 물리식/연산 | 코드 SSOT (본 PR만 새 파일) | 검증 |
|---|---|---|
| `C^a_bc=eps_bcd N^{da}`와 Koszul `Gamma(n,n)` | `source/vi0_null_liouville.py::koszul_connection` | 70 generic symmetric-N independent witnesses, sign mutation |
| `n'=-Σn+Sn−n×Nn+Wn` | `ray_flow`, `null_connection_correction` | exact Bianchi-I conserved momentum, pure-VI0 curvature Hamiltonian |
| `E'/E=-1-S`, `I'/I=-4(1+S)` | `rhs` | independent Bianchi I `E(t)` oracle, saved invariant I/E4 |
| sky Jacobian `(ln w)'=3S` | `sphere_divergence`, `rhs` | spherical-coordinate independent finite differencing, Wolfram rational zero residual, wrong `w'=0` control |
| photon stress-energy moment `ρ'=-4ρ-Σ:P` | `sky_moments`; separate `verify_saved_physics.py` | all 1476 real rows independent recompute, ~1.8e-15 max |
| physical-time complete `v',n',w'` scalar P' and Kato | `projector_chain`, `projector_on_rays` | derivative finite difference, Kato commutator, pure gauge control |
| numerical result & spatial resolution | `integrate_one`, `run`, `grids` | 78,720 full rows, 6/26/128 grids, GL128 vs Leb26/axis data |

`source_guard` requires exact immutable PR311 `vi0_dynamics.py` Git blob SHA1 `aa3c7d5ba4e3aca62efe0c8651df73b5d29ea8f9`, and on GitHub checkout also demands original frozen 7 BASS Git blobs (names/hashes held by parent `ORIGINAL_BLOBS`). Original source is **not changed**; paper results derive from this exact source mathematical model.

Primary context: S. Hervik (2004), *Class. Quantum Grav.* **21** 2301–2317 DOI 10.1088/0264-9381/21/9/007 (7D VI0 tilted fluid state space); A. Pontzen & A. Challinor (2007), *MNRAS* **380** 1387–1398 DOI 10.1111/j.1365-2966.2007.12221.x (tetrad photon propagation), whose near-FLRW perturbative CMB results are NOT used as exact nonperturbative physics oracle. All full nonlinear tensor signs taken from BASS's frozen class-A/Koszul SSOT.

## R10: backup, publication, next atomic science

Phase S0 R1–R4 Git commit `613c845f2ff35719acbf6d2d4f3a247e42c4674d`, S1 R5–R7 Git commit `54f7bed18f3f4f4a11e3f3ad8e983bda676866ed`, S2 R8–R10 new final source+workflow commit (obtain exact HEAD from live PR #312 after publish). Each phase preserves exact SHA+CRC source snapshots in Library `/BASS/VI0_NULL_LIOUVILLE_20261101/` and Google Drive `/Google Drive/BASS/VI0_NULL_LIOUVILLE_20261101/` and includes stage per-node upper DAG counts. Provider ACK and **actual re-download** are recorded separately. S2 includes actual 78,720/1,476 physical data, original parent byte-exact source, 3 PNG + 3 SVG scientific figures, code+tests, and complete handoff; Dropbox NOT_VERIFIED.

One bounded R1–R10 loop closes the **physical null geodesic plus scalar angular Jacobian** within `G-DYN-MANIFOLD-VI0`; do not start next node automatically. For original production path, next choice: VI0 **polarized screen** and full Liouville/Thomson carrier using same source-matched photon bath, or independent Type-II `P-MIG-II-PREFLIGHT` host inventory/roundtrip without production mutation. Distinct-author review NOT_RUN; user expressly requested same-author blind referee, which was performed. Production/merge/auto_next all false.

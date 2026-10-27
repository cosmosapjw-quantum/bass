# B3h 선택 유한 Lyα 입력 — 2026-10-27 재개 조사

## 판정과 곧바로 쓸 수 있는 결과

선택된 z≈1100 effective-H collapsed 2p/1s Lyα의 실제 native source와 strict-past incoming history는 그대로 확보되어 있다. 최신 REC 작업과 REI 병렬 PR235/236은 이 선택 채널의 유한 donor를 추가하지 않았다. 현재 B3h 판정은 `PARTIAL_SOURCE_BOUND_FINITE_DONOR_INPUT_DEPENDENT`로 유지한다. B3g midpoint/transport 작업과 B3i의 이미 검증된 state adapter는 독립적으로 이어갈 수 있다.

이번 조사는 실제 원전·코드 읽기와 조건부 유도이다. 새 과학 실행, IVP, native solve, 기존 캠페인·시험 재실행, 원격 변경은 모두 0이다. 실행 비용 예산을 새로 부여하거나 기존 불명 잔여 예산을 0/양수로 바꾸지 않았다. 현재 자료 취득 비용은 별도 I/O이며 과학 CPU=0이라는 진술로 그 비용까지 0이라고 주장하지 않는다.

다음에 구성할 최소 물리적 연결은 **native incoming face를 지나는 유한 photon crossing measure**다. 기존 35×26 COM cell 평균을 native f_plus로 치환할 필요가 없다. 아래 §4는 원래 HISTORY01 boundary 식에서 직접 얻는 유한 donor/debit 구성을 준다. 실제 시간 지지구간·공통 부피·원자 stock 이력이 공급되면 그대로 적용할 수 있다. 이 조건을 이번에 확보한 실제 입력으로 주장하지 않는다.

## 1. 최신 HEAD·AGENTS·병렬 작업

확인 시점: 2026-10-27 02:57 UTC(11:57 KST) 무렵. 정확한 조회 객체는 `REMOTE_INTAKE_RECEIPTS.json`에 기록한다.

| 대상 | 실제 확인한 HEAD 또는 blob | 의미 |
|---|---|---|
| BASS 기존 consumer branch | `d7dcd731de1a0c59e5e65db5038c333f5abae0bd` | 이전 최종 인계 그대로 |
| 활성 central orchestration branch | `a5db4bac9dafadae29685bbea3cec7f43ab990b2` | 기존 canonical M 그대로 |
| 활성 central AGENTS | `429a5a13ee75b1222bc50627f8d5973d01dd21c4` | delegation/typed identity/anti-starvation 유지 |
| REC PR138 program expansion | `4a8e541030ee2cbd02e26ba671083b705d309d49` | HD parser와 H5 input binding |
| REC LINE02 PR129 | `a7c46fd8338971e2cefa776f5dd7b25a46974990` | 선택 native Lyα owner 후속 변경 없음 |
| REI PR235 coupled followup | `3ab52a286a443622492403d89cd2bf80e58fb722` | moving electron reservoir 구성 |
| REI PR236 native PW19 | `ee94bef85b56d879dc38f184856a5c613575e9e1` | HeII 외부 광원 particle/energy source |
| PR236 AGENTS | `6464cd96b7023e3e91e30246bc93650d4e435a10` | REI 한정 temporary-budget 조항 추가 |

REC의 최신 갱신 open PR30개와 선택된 최신 HEAD의 완전한 tree를 확인했다. 모든 branch 또는 모든 blob을 조사했다는 주장은 하지 않는다. REC tree의 AGENTS 세 개는 `docs/.../survey/atomic/sources/{BASS_HE,WU088_HH,bass_cr}/AGENTS.md`에 있는 다른 저장소의 보관본으로, 선택 REC source의 ancestor 지침이 아니다. root AGENTS 요청은 실제 404였다. 이번 BASS 단위는 최신 central 정책과 현재 사용자 승인 범위에 따른다.

PR236의 추가 budget 조항은 REI continuation의 원래 baseline과 누적 debit에 관한 것이다. 이 원전 읽기는 그 예산을 BASS로 전용하거나 REI의 cap을 재설정하지 않는다. 원본 파일과 새 source update의 identity를 구분한다.

## 2. 선택 REC 원전의 동일성 및 실제 의미

최신 REC tree에서 다음 blob들이 이전 B3b2/B3g source와 일치한다. 동일한 입력·전제의 완료 결과를 재사용한다.

| 선택 원전 | Git blob | 이번에 확인한 역할 |
|---|---|---|
| `trajectory/dynamic_macro_ownership.py` | `a196840d164aa7497b27178c1a38ca0f9627c426` | native atomic full, COM atomic disabled, replacement_complete=false |
| `trajectory/source_derived_parent.py` | `e04e590d43f4c2d7dfa184106fc4492e5bdb63de` | scalar-history 기반 isotropic bootstrap initial state |
| `recoil/frequency_liouville.py` | `95ad73d8095e5b5c19667661e1680a48bd6a5765` | 내부 upwind trace와 별도 제공 native red/blue boundary |
| `native_line_owner.py` | `cb36a10b19b9b60c046383389f9706bd9970222f` | matched direct Lyα pair와 원래 constants |
| `history_boundary.py` | `1aa7f134c332bc4596372df18c7c47306260ecfc` | native-Wien finite optical-depth boundary, 단일 event/boundary owner |
| `z1100_direct_network_node.npz` | `40e49ae67f2894a75f97bace372bb70b9a91ce4a` | 실제 G_i, p_i 및 finite support |
| `pr01c_background_snapshots_v048.npz` | `fdcbb6e84c398773ca4ef084c9d38213f1759670` | 26 방향과 각 가중치 |
| `pr05c2c1b2b1e0_source_derived_parent_v073.npz` | `efb59de1e8f9109282cfdcbefaf7ce136f60ffc9` | 35×26 bootstrap occupation |

`frequency_liouville._face_flux`는 내부 cell에서 선택한 upwind 값을 쓰지만 양 끝 face의 native_red/native_blue는 별도 입력이다. 그 선택은 COM 외곽 x=±21.25 경계이며, Lyα line-side incoming trace와 동일하다고 선언하지 않는다. native virtual313은 원전이 명시하는 zero-width point spikes다. 인접 spike 에너지에서 유한 폭을 추정하지 않는다.

`history_boundary.line_ledger`는 `R=G_NATIVE H q (f_out-f_in)`와 radiation/atomic internal ±E21 R을 반환한다. `occupation_is_boundary_encoding=True`, `extra_radiation_source=0`을 함께 명시한다. 실제 boundary transfer를 state로 적용한 뒤 같은 rate를 radiation Source에 다시 더하면 동일 이전이 두 번 적용된다.

native LINE02의 incoming convention은 Wien departure이고 원래 `LYA_FACT`, `hPc`를 유지한다. 최신 source가 standalone LINE01의 Planck/stimulated convention으로 바뀌었다는 증거는 없다. 이번 조사에서 그 변환, rate 또는 원래 313 query를 재계산하지 않았다.

PR138은 기존 313 query와 626 endpoint slot 및 314×313 Ks를 결속했지만, 실제 continuous defect/stability/tube/curvature coverage=0/313, physical_epsilon/outgoing_bound=null이다. finite Lyα donor나 시간 이력에 물리 반경을 제공하지 않는다. 이 결과는 conditional 계산과 numerical representation anchor를 재사용할 수 있게 한다.

## 3. 최신 REI 병렬 결과의 사용 범위

### PR235 — moving electron reservoir

실제로 읽은 `coupled_followup_20261026/stopping/DERIVATION.md`와 `IMPLEMENTATION_CONTRACT.json`은 electron kinetic-energy finite-volume cells와 reservoir cutoff를 다룬다. 동일한 relative current F_i=j_i−w_i f_i로 number transfer와 energy moment를 결속하고, 움직이는 대표 에너지의 mesh work Σ ė_i n_i를 보존한다. caloric cutoff는 선택된 Maxwell pure-electron reservoir 아래 affine moment I_h=I0+L θ̇를 사용한다.

이 유효한 구성은 향후 finite-energy representation work를 빠뜨리지 않도록 재사용할 수 있다. 현재 API의 source_terms는 none이고, birth source는 별도 owner다. 실제 cutoff density/current와 matched reconstruction이 아직 없으며 actual_endpoint_activation=false다. 따라서 PR235의 ‘finite reservoir’라는 이름만으로 photon/Lyα donor가 확보된 것으로 판정하지 않는다. 이번 선택 채널과는 입자·energy·역할이 다르다.

### PR236 — native PW19 source

실제로 읽은 `coupled_source_20261027/theory/CONTRACT.md`, `ADMISSION.json`은 z=2.479의 isotropic prescribed PW19 광원을 HeII photoionization native callback에 넣는다. 광자 지원은54.42..50000 eV이며 선택 Lyα의 z≈1100, E21=10.198714553953742 eV와 다르다.

21 native abundance와 newborn nonthermal electron count, primary energy, external photon ledger, logT의25개 좌표를 사용한다. w_ext는 명시적으로 **open signed transfer ledger**이고 양수 finite photon inventory가 아니다. pre-assimilation thermal count가 보존되고 selected logT source가0이라는 결과는 검증된 source 소유권 정보다. primary-electron pressure-source interval은 evolved matter stress 또는 geometry closure를 공급하지 않는다.

따라서 이 결과에서 B3i에 즉시 넣을 새 T_ab나 Lyα finite-stock debit을 추출할 수 없다. future selected continuum photoionization 경로의 source adapter 후보로 보존하며, 이번 B3g/B3h 진행의 선행조건으로 추가하지 않는다. 실제로 읽은 PR236 admission은 physical_uncertainties=null, L4_ready=false, full signed stress/history open을 유지한다.

## 4. 원래 native boundary에서 얻는 조건부 유한 donor 구성

원전의 physical occupations를 f_in=f_ref+d_in, f_s=f_ref+xr_p/(3x1s), u=τ/q라 쓰자. f_ref는 원래 native Wien reference다. τ≥0,q>0과 f_in,f_s≥0 아래

    A = 1−exp(−u),  0≤A≤1,
    f_out = (1−A) f_in + A f_s.

선택 incoming characteristic tube에 양의 finite measure dμ를 주면

    N_in  = ∫ f_in dμ,
    D_up  = ∫ A f_in dμ,
    D_down= ∫ A f_s dμ,
    N_out = N_in − D_up + D_down.

따라서 0≤D_up≤N_in, N_out≥0이고, 순 photon 증가 D_net=D_down−D_up는 boundary jump ∫(f_out−f_in)dμ와 같다. 동일 photon을 boundary와 추가 source 양쪽에서 charge하지 않는 조건에서 유한 donor debit을 구성한다. 두 gross count를 따로 유지하여 작은 net의 cancellation과 유한 stock 소모를 구분한다.

isotropic native rest-frame crossing에서 순간 밀도 flux measure는

    dμ = G_NATIVE H(t) q(t,n) J_V(t) dt dΩ/(4π),
    G_NATIVE = 3×10^6×LYA_FACT  [m⁻³],
    J_V(t)=V_phys(t)/V_reference.

J_V는 같은 reference volume으로 event count를 비교할 때 필요한 실제 부피 대응이다. frozen local fixed-volume substep이면 J_V=1이라는 모델 조건을 별도로 선언할 수 있다. 실제 cosmological tube에서 이 조건을 임의로 대입하지 않는다. dμ의 단위는 reference-volume 당 photon phase-space capacity이고 f는 무차원이다.

E21에서 line crossing을 charge하는 source convention 아래 radiation energy 변화는 E21 D_net, atomic internal 변화는 −E21 D_net이다. 원전처럼 recoil-free collapsed line이면 이 거래의 thermal/recoil channel은 그 선언 범위에서0이다. upstream shell의 실제 photon energy가 E21와 다르다면 그 redshift/recoil work는 별도 실제 owner로 연결해야 한다. source마다 다른 energy authority를 맞춘다는 이유로 잔여 에너지를 새 reservoir에 임의로 넣지 않는다.

이 식은 적분 구간 전체에서 source coefficient/population과 photon trace를 연결하는 유한 데이터가 있으면 즉시 사용 가능하다. 현재 snapshot만으로 유한 dt를 임의로 정하고 모든 계수를 그대로 고정하면 **새 frozen local model**을 선택한 것이며 실제 native trajectory를 복구한 것은 아니다. 특히 긴 native history grid interval 동안 gross emission을 초기 n_2p에 charge하면 source의 다른 재공급 owner를 잃을 수 있다. 한 finite transaction에는 시간에 따른 atomic population owner 또는 엄격히 한정된 frozen-step stock 조건이 필요하다.

## 5. 남은 최소 선택 입력과 다음 행동

선택 native Lyα로 진행할 때 확보할 최소 묶음은 다음이다.

1. 실제 incoming characteristic tube의 양의 finite measure, 시간 구간, 공통 부피와 source proper clock 대응.
2. 그 구간의 native incoming trace/원자 source population 및 source-owned opacity, 또는 그 정확한 finite substep.
3. incoming/outgoing/history와 atomic internal/recoil 중 각 이전을 한 번 charge하는 단일 거래 소유권.
4. 필요한 물리 정확도 주장에 대응하는 source/trace/geometry/energy 반경. 현재 null을 numerical residual로 대체하지 않는다.

현재 실제 source code와 input identity에서1–3의 완성된 packet은 발견되지 않았다. 이 정확한 입력 의존성을 유지하고, 복구된 B3c cohort에서의 B3g geometry/transport 유도와 한정된 B3i 변환은 계속한다. 모든 미래 원자·핵·stopping 공급자나 isotope precision을 일괄 요구하지 않는다.

## 원전 경로

모든 URL/commit/blob은 동반 JSON에 실제 tool readback으로 보존했다. 핵심 경로는 다음과 같다.

- BASS F: `research/bass_b3b2_locked_cell_bridge_20261024/intake/rec/REC_FINITE_RECEIVER_REPORT.md`, `theory/SNAPSHOT_BRIDGE_THEORY.md`, `FROZEN_CONTRACT.md`.
- REC 4a8e541: `src/full_bianchi_hyrec/trajectory/dynamic_macro_ownership.py`, `src/full_bianchi_hyrec/recoil/frequency_liouville.py`, `research/rec_history_boundary_20261023/code/history_boundary.py`.
- REI ee94bef: `research/rei_expanded_event_consumer/coupled_followup_20261026/stopping/DERIVATION.md`, `IMPLEMENTATION_CONTRACT.json`; `coupled_source_20261027/theory/CONTRACT.md`, `ADMISSION.json`.

Scientific child execution: NOT_RUN by design. No new strong no-go claim is made. This source intake is ready for parent contract selection and later independent review.

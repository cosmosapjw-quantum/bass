# BASS B3b 관련 저장소 현재 조사

판독 시점: 2026-10-24 02:56:20 UTC (11:56:20 KST).
작업자: `/root/b3b_crossrepo_intake`. 읽기 전용 조사이며 새 과학 실행·IVP·과거 replay·archive 다운로드·원격 mutation은 모두0이다.

## 현재 결론

다음 BASS 작업에는 기존 REC LINE01의 실제 population/source 계약을 좁게 연결하는 경로가 적합하다. 최신 HE-ANG은 측정된 검출전자 window에 대한 유용한 각 moment 결과를 추가했지만, full physical event provider와 HE-EXCHANGE/HE-RESERVOIR는 여전히 별도 입력 의존성이다. REI에는 실제 continuum photoionization receiver가 존재한다. 다만 이 receiver의 상태는 H/He charge fraction과 thermal energy이며 LINE01 upper/lower excitation state와 다르므로 자동으로 대체하지 않는다.

## 조사 범위와 현재 HEAD

두 저장소의 branch 및 open/closed PR metadata는 pagination 끝까지 읽었다. 이것은 각 branch의 모든 source file, 모든 대화 또는 모든 backup byte를 읽었다는 뜻이 아니다. 전체 inventory는 `CROSSREPO_INTAKE.json`, 실제 선택해서 읽은10개 source/contract의 원문과 API blob은 `FETCHED_SOURCE_SNAPSHOTS.json`에 있다.

| 저장소 | branches | open PRs | closed PRs | 판독 |
|---|---:|---:|---:|---|
| cosmosapjw-quantum/BASS_HE | 99 | 94 | 0 | 각1page, exhaustion |
| cosmosapjw-quantum/rei_bianchi | 264 | 208 | 14 | branch100/100/64, open100/100/8, closed14 |

| 대상 | 실제 branch/HEAD | 상태·의미 |
|---|---|---|
| HE PR94 | research/he-ang-ddcs20-window-20261024 / d8bae9f7e24ad3494e399f7ab46c4167a5623d48 | Draft/open, 새 측정 window moment |
| HE PR93 | research/he-ang-source-hex-20261024 / bf3c21a39b1111497ed77667d05b8a853ffe6646 | science15053fe4445a32e0544d644e864fe27780d08743 이후 delivery commit |
| HE PR92 | research/he-ang-provider-contract-20261023 / 0a11bf9e1f6ffcc696625de0caf1c581c27cf7f0 | 기존 source/frame/event 계약 유지 |
| REI PR222 | research/orchestration-sandbox-20261022 / 4d78d35da27c8fc1a6fb291c748e7406e2ad9d7c | central CR_N4 admission 관측 포함 |
| REI PR223 | research/rec-history-admission-observation-20261024 / 44d0a6d8703f50bf3d7548812a1ab13d9b2c3877 | REC ADM01의 별도 observation fork |
| REI PR221 | research/rei-coupled-isotope-contract-20261022 / 8d10231b1f0f788164d5eadbe1bcee0b802cceca | 별도 directional thermochemistry lane |
| REI PR219 | research/rei-isotope-quotient-pilot-20261022 / 6a12f3865d9ea427c1391c41caed8bb7cb7ec00d | 별도 isotope/nuclear pilot lane |

선택한 HE94와 REI222 ref는 조사 마지막에 다시 읽어 위 HEAD와 일치했다. REC actual HEAD/active history thread는 별도 REC intake 및 root 대화 조사가 맡는다. PR223의 관측 pin을 REC live source로 승격하지 않는다.

## 정책과 병렬 작업

현재 REI AGENTS blob은 `429a5a13ee75b1222bc50627f8d5973d01dd21c4`로, 고정 중앙 authority의 것과 동일하다. 실행 전환·제한된 독립 검토·변경된 의존성만 검증·Astra 계약/하위 tier 구현 분담은 변하지 않았다. `research/` 직접 listing에는 별도 AGENTS가 없었다.

HE94 root AGENTS blob은 `8119a57e3c9f7b8c22a3532c9f88e430df1cebbf`다. 원전/유도/수치증거 분리, source domain 유지, unchanged suite 재실행 금지, 독립 검토, 첨부 PDF 재배포 금지를 유지한다. HE의 `research/AGENTS.md`와 선택한 DDCS lane의 AGENTS는404다.

HE94, REC history, REI isotope/thermochemistry, CR_N4 stopping은 병렬 작업 중인 별도 lane으로 취급한다. 외부 실행 host/process/lease는 이 조사에서 관측하지 않았으므로 idle 또는 reservation 부재라고 주장하지 않는다.

## 새 HE 결과의 재사용 범위

실제 현재 `CLAIM_GATE.json`과 `NEXT_DAG.json`을 읽었다. HE-ANG-DDCS20-WINDOW는 Childers et al. (2004) Table IV의 incident20eV, detected energy3–6eV, angle15–120deg에서 양의 bilinear mu/E 보간과 조건부 검출전자 moment/covariance, 지정된 deterministic box의 scalar extrema를 다룬다. source transcript에40수치/8uncertainty를 보존하고 primary32값을 사용한다.

기록된 결과는 N_W=1.918935932462322e-21 m², mean(mu)=0.5215950232, mean(P2)=0.1799846901이며 R6 PASS, C9 PASS_SCOPED다. 이 숫자는 새로 재계산하지 않은 owner 기록이다. Full support/event normalization, joint two-electron law, finite-mass recoil/frame과 source uncertainty는 남아 있다. 따라서 HE-ANG `SOURCE_INPUT_PENDING`, HE-EXCHANGE·HE-RESERVOIR `PROPOSED`를 유지한다. 검출전자 marginal을 BASS photon event source 또는 완결된 reservoir 계약으로 바꾸지 않는다.

## 실제 REI receiver와 LINE01 연결 차이

현재 중앙 tree에서 다음 실제 source를 읽었다.

| source | Git blob | 실제 인터페이스 |
|---|---|---|
| rust/rei_microphysics/src/igm_state.rs | 437365fbe329a10afe292f9dd7eebf549fef804c | IgmGasState(fractions=[HII,HeII,HeIII],w_erg_per_h), PrimaryPacket↔PhotonPacket |
| rust/rei_microphysics/src/axbi_q_advance.rs | 836e5b4e5587e86a32a8734d01b6989c3447343e | advance_frozen_expanding(CovariantPhoton, geometry, H_i, neutrals_cm3, duration_s, slices) |
| research/rei_source_age_bianchi_20261016/src/age_transport.py | f48b45437b80d94ed6619dbec9c75345059ebbc9 | Model, RayLedger, integrate_ray, integrate_source, source-age/cohort reference |

`IgmGasState`는 upper/lower atomic excitation population을 저장하지 않는다. PhotonPacket adapter는 reference-comoving count n_H0=n_H(a)a³를 사용하며 ray phase-space occupation을0으로 설정한다. 이 code가 packet count를 occupation으로 변환한다고 해석할 수 없다.

`advance_frozen_expanding`는 실제 photon stock `photons_per_h`를 exponential survival로 줄이고 `absorbed_per_h[HI,HeI,HeII]`, binding/heat/redshift-work를 반환한다. H/He continuum Verner cross section과 고정 neutral density를 사용하며 이 함수 자체는 gas state를 advance하지 않는다. Proper-time seconds, eV, cm^-3와 해당 covariant photon momentum 계약을 갖는다. 따라서 REC Ly-alpha excitation channel을 그 neutral photoionization sink에 넣으려면 새로운 물리 채널·상태 mapping이 필요하다.

Source-age oracle의 j(y)는 photons/reference-H/dln(a)이며 physical proper-time source와 H(y) 변환을 명시한다. 유한 gas dynamics를 풀지 않고 prescribed opacity·geometry를 사용한다. 기존 README의 sharp pressure envelope·34검사·DOP853 수렴과 초기 fit-cutoff/binding 혼동 실패를 재사용 가능한 과거 근거로만 기록했다. 이를 BASS 사건률의 현재 finite-stock admission으로 확대하지 않았다.

더 완성된 원 source PR160 `8351f21036eeaa079e603159a08269dbe90ce58e`는 native Grackle RR/CI/thermal, PreparedAbsorption, accepted-state rollback을 결합했다. PR206 `00e89bce3060516083d63edb857f1294ee560ea0`는 actual birth/cohort monitor를 추가했다. 이 두 PR의 현재 metadata/body와 PR160 source-directory inventory를 읽었고, 원51/203/4980 검증과 PR206 monitor 결과는 재실행하지 않았다. 이들은 향후 source-age continuum receiver를 위한 실제 재사용 경로이며, 이번 LINE01 bound-bound source 선택과는 상태·channel 계약이 다르다.

## 중앙 기록의 시점 구별

현재 중앙 branch의 `CURRENT_REFRESH.json`에는10월23일의 오래된 PR heads가 남아 있다. `assembly/DAG.json`도 B1–B5에 original author contracts와 `PROPOSED`를 보존하며 BASS PR184/185의 새 관측을 담지 않는다. 이것을 현재 BASS 완료 증거의 취소로 해석하지 않는다.

PR223의 REC observation은 별도 branch이며, 현재 PR222 중앙 tree의 REC-HISTORY `PROPOSED`와 동시에 존재한다. HE 중앙 observation도 PR92/93까지이며 새 PR94 window를 아직 포함하지 않는다. 앞으로 중앙 갱신이 필요하다면 현재 live expected SHA에서 실제 관측 필드만 좁게 추가하고 기존 계약40개·integration edges17개와 다른 lane의 변경을 보존해야 한다.

## 다음 BASS 계약에 넘길 의무

1. 선택한 실제 REC LINE01의 population/source ODE와 stock을 직접 사용한다. 광자 escaping rate의 gross down/up, 정준 frame/clock, atomic internal energy를 보존한다.
2. 다른 저장소의 실제 continuum photon/gas 코드가 존재한다는 사실과, 그 receiver가 선택한 resonance 채널을 이미 수용한다는 주장은 구별한다.
3. B1 exact historical pytest argv/cwd 미확인, B2 selected finite-window 범위, remaining campaign wall/CPU=null, budget_reset=false를 유지한다.
4. HE94의 partial measured window를 full event closure로 사용하지 않는다. bass_cr/WU088_HH에는 이 LINE01 경로의 필요한 직접 의존성을 찾지 않았으므로 새로운 조사·수용 gate를 추가하지 않는다.
5. 이번 source intake의 판단은 source/contract 비교다. 원 numerical arrays에 대한 새 독립 검토나 새 과학 수치 실행으로 기록하지 않는다.

## 확인한 원격 자료

- https://github.com/cosmosapjw-quantum/BASS_HE/pull/94
- https://github.com/cosmosapjw-quantum/BASS_HE/pull/93
- https://github.com/cosmosapjw-quantum/rei_bianchi/pull/222
- https://github.com/cosmosapjw-quantum/rei_bianchi/pull/223
- https://github.com/cosmosapjw-quantum/rei_bianchi/pull/160
- https://github.com/cosmosapjw-quantum/rei_bianchi/pull/206

전체 API 응답 중 source별 정확한 URL·request ref·blob 및 원문은 동반 JSON에서 확인한다. 읽지 않은 본문·실행·백업에 대한 추정은 추가하지 않았다.

## 추가 frontier metadata — 2026-10-24 12:01:09 KST

사용자의 관련 frontier 전수 metadata 요청에 따라 `bass_cr`와 `WU088_HH`의 branch/PR page를 추가로 끝까지 읽었다. `SUPPLEMENTARY_METADATA.json`에 별도로 보존했으며 기존 두 저장소 inventory는 변경하지 않았다. bass_cr는178branches/100PRs(99open,1closed), WU088_HH는151branches/142PRs(142open,0closed)다. 최신 bass_cr PR100의 `8e4e06361d714939513a11f64a27f02822bde2fa`는 C23E D43K 조건부 PI/RR/CX 장부, WU PR142의 `1a8f98719fd3ec87d3acbfb27aeda9936b0bc613`는 PHYS85 nuclear thermal/fast owner 준비 checkpoint다. 후자는 owner가 exact reference/application NOT_RUN을 명시한다. PHYS84 PR141의 준비/lease WAIT도 별도 owner 기록이며 BASS의 현재 runtime 실패로 상속하지 않는다. 두 active lane은 REC LINE01 receiver 직접 의존성에서 제외한다. 이 보충 조사에서는 deep source read·archive download·시험·새 과학 실행·원격 변경이 모두0이다.

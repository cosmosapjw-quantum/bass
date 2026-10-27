# 두 endpoint channel interpolation — 실행 전 readiness

## 현재 관측과 준비 범위

새 unit만 작성했다. 실제 remote readback은 BASS entry `1e8d7ecc90a304fcd1ddf3ea9a98ad14f88248a0`, 중앙 `42cc3a909688d670200ba09c500e2ca83a94fa10`, AGENTS blob `429a5a13ee75b1222bc50627f8d5973d01dd21c4`로 root entry와 일치한다. Root/intake/theory/implementation 네 역할이 실행 중인 것을 실제 inventory로 확인했다.

현재 workspace와 `bass_recovered`는 `.git` checkout이 없는 recovered filesystem snapshot이다. 실제 git status/branch/HEAD 호출은 `NOT_A_GIT_REPOSITORY`를 반환했다. 따라서 local clean/dirty 상태나 branch를 추정하지 않는다. 연결된 Git의 실제 refs와 이전에 게시된 source pin, 로컬 보존 bytes를 대응시켰다. Clone/worktree와 Git mutation은0이다.

기존 QSS unit, S1B/F science·metadata·ZIP은 수정하지 않았다. 현재 과학 함수·새 right map·variable-M solve·tests·consume·plot은 모두0이다. `code_reference/`는 읽고 비교할 원문이며 새 production implementation으로 실행하지 않는다. 새 실행 계약·허용오차·fresh allocation은 root가 고정한다.

## 실제 입력이 갖춘 범위

`inputs/reused/SOURCE_OPERANDS.json`은 admitted science S1B `634c3046ffccc5d00f1ab7588b5834a6eb8053ad`의 원 결과다. SHA256은 `179784a094091324dd85ba727fddca1a592178099e9067ff254d6c44c60dd7bd`다. Endpoint5126과5127 **둘 다** 다음 값이 저장되어 있다.

- 2×2 Trr, 2×311 Trv/Tvr, 3×311 Tvv, sr/sv, Gamma/optical depth, 원 source의 small-tau 결과.
- Pre-diffusion radiative coefficients와 Aup/Adn 및 core139/140 diffusion coefficients. 별도 diffusion을 한 번만 더하는 새 gross-map 구성에 필요한 원문 배열이 있다.
- TR/Tm/nH/H/x1s/xe/xHII, Alpha/Beta/mixing, 실제 absolute population과 Wien shifts.
- 두 level의 admitted Krec/Kion, source constants와 energy owner의 원 parameter.

`NATIVE_QSS_STORED_INPUT_5126_5127.json`에도 양쪽311 incoming/average/outgoing 값과 두 incoming Lyman 값, 실제 energies와 strict-past source witnesses가 있다. 따라서 **두 endpoint gross map을 새로 구성하는 데 필요한 저장 field의 구조적 누락은 없다.** 이 준비 관측이 아직 실행하지 않은 오른쪽 absolute virtual solve/map의 numerical PASS를 주장하지는 않는다.

`FINITE_CHANNEL_RESULT.json`에 이미 계산된 gross map1414개는 **왼쪽 endpoint만**의 결과다. 두 번째 map 결과가 이미 있다는 주장은 하지 않는다. 이전 finite owner inventories·Lyα totals·new RHS는 saved baseline으로 그대로 재사용할 수 있다. Original native exporter/history, diffusion Tm inversions, Phase A rates는 새 unit에서 재실행할 필요가 없다.

## 코드별 재사용 대응

| 보존 코드 | 재사용 가능한 범위 | 새 계약이 필요한 연결 |
|---|---|---|
| `channel_maps_b.build` | C/physical virtual generator·MP Thomas·positive absolute X=a+Bp·directed diffusion·각 event stoichiometry/energy·gross map 구성 | 양쪽 map/Rα 정규화의 actual endpoint density와 common-V0 clock 대응, interpolation parameter와 모델 범위 |
| `mp_b` | MP70 exact binary64 lifting·serialization·norms·tridiagonal elimination·실제 bounds를 기록하는 틀 | 새 variable-M 적분법에 맞는 error propagation 및 root tolerance |
| `finite_b.Clock` | Old exact represented h/eta0/lag/A·실제 incoming 두 구간·native Lyα activity identity·saved moments의 conditional precision 구분 | variable-M solution/finite memory; 새 derivative 및 integration bounds |
| `finite_b.finite` | Initial state, 실제 knot continuity와 error carry를 기록하는 구조 | **상수 M의 K/K²/K³ particular 및 exact Ip/weighted identities는 variable M에 그대로 적용 불가** |
| `owners_b` | Atomic inventory order·stoichiometry·finite donor 의미·source binary eV 단위·gas/ambient 준비·spectral PL/Wien/Planck source·공통 V0 work와 right density 분리 | **상수 map aS+ell·Ip count formula는 새 시간의존 map 적분으로 교체 필요** |
| `core_bridge_b` / preserved vendor | si_to_core/FixedScale·5sector T와Q 분리·한 번의 RHS와 isotropic algebraic comparison 방식 | 새 finite result가 계약의 checks를 통과한 뒤 새 packet에 한 번만 호출 |

`channel_maps_b.build`의 `NH` 인자는 왼쪽 Rα0 계산에서 density normalization으로 사용된다. 오른쪽 endpoint에서 공통 NHref를 그대로 넣을지, 그 시점 proper density를 넣을지는 이름만 보고 결정하지 않는다. 새 contract가 지정하는 `nH(u)=nHref exp(-3u)`와 두 source endpoints의 저장 nH를 명시적으로 대응시켜야 한다.

같은 이름의 event들을 양끝에서 연결할 수 있는 source 배열과 stoichiometry가 저장되어 있다. Krec/Kion 같은 energy parameters는 endpoint마다 다르므로, 시간의존 gross rates와 energy-weighted maps를 어떤 방식으로 함께 보간할지는 root의 과학 계약을 따른다. 구현자가 임의로 product/interpolation rule을 선택하지 않는다.

## 비용·재사용 identity

`inputs/REUSE_INVENTORY.json`에21개 실제 복사 파일의 source path·destination·bytes·SHA256과 endpoint field coverage를 기록했다. 복사량은4,812,856bytes이며 입력 JSON과 코드 원문·vendor/theory reference만 보존했다. 원 native archive를 다운로드하거나 old script를 실행하지 않았다.

`BUDGET_PREPARATION.json`의 새 allocation·remaining은 아직null이다. 이전 fresh allocation은 실제 child15.589431초/wall15.992101595초를 쓴 뒤 closed 상태이며, 남은 arithmetic value는 새 allocation으로 옮기거나 실행 권한으로 해석하지 않는다. 과거 historical remaining도null이다. 준비 CPU는 미측정 unknown이며0이라고 기록하지 않는다.

Requested implementation model은gpt-6.1-sol, actual runtime identity는노출되지않아null이다. 현재 original completion은 이전 채택28/88을 재사용한다. 새 refinement의 완료 증가나 물리 반경을 여기서 정하지 않는다.

## S0 준비 시점의 후속 고정

위 entry 준비 때의 새 allocation null 기록은 당시의 historical observation이다. 현재 root BUDGET_LEDGER.json이 별도 fresh120CPU/300wall/768MiB/1thread를 고정했으며 실행은 아직 release하지 않았다. Root R1_CONTRACT.md는 proper-time convex maps와 endpoint-tagged energy mixture를 선택했다. eθ·jθ의θ² cross model은 선택하지 않았다. 새 production/numerical contract와 실행신호를 기다리며 이 S0는 준비자료만 포함한다. Saved initial spectral_owner/initial sector energies를 직접 재사용하고 old spectral positivity/Planck series는 호출하지 않는다.

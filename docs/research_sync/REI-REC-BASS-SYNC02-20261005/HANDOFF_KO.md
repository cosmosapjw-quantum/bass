# bass: REI-REC-BASS-SYNC02-20261005

공개 전환을 확인한 BASS에 seconds/conformal-seconds/conformal-meters를 구분하는 clock adapter를 준비하고 독립 scoped PROMOTE를 받았다.

입력은 `fecfae3cbf508170513d5ad711e2897d0efe18e1` / 기존 PR132다. 이는 publication commit과 별도다. 공통 Loop1 판정은 `CONFIRMED / PROMOTE_SCOPED_LOOP2_INPUTS`, 동기화 기록은 `state/LOOP1_SYNC.json`이다.

실제로 받은 결과:

- 새 clock API는 기존 normal opacity를 재사용; supplied finite-cell optical-depth/survival/mass 변환 일관성 검증.
- 30 scoped tests 및151 Decimalcases/5001checks PASS.
- 기존 REI H/He→proper electron density→Thomson opacity 연결은 보존하고 D를 한 번 적용한다.

남은 경계:

- whole BASS crate build 미실행.
- 실제 accepted expanding REI history payload가 없으므로 BASS-REI-EXP01 대기.
- UNVERIFIED_FINITE_TEMPERATURE_TAIL와 SCALAR_Q_KERNEL_UNRESOLVED 유지.

Loop2 source-bound pure-H benchmark의 clock/visibility 결과를 수신하고, production expanding consumer는 REI-F08 accepted density/frame/time payload가 온 뒤 실행한다.

병렬 후보:

- BASS-REI-EXP01-PAYLOAD-CONTRACT: properdensity/frame/normal-time/observer-tail 입력과 dt-deta authority 고정; REI chemistry/history source 수정 없음.
- BASS-COLLISION-DOMAIN: 실제 요청된 observable에 필요한 finite-T/tail/scalar-Q 계약; clock adapter PASS를 kinetic/CMB admission으로 전용하지 않음.

보존: cold-Thomson declared model; finite cell measure != continuum quadrature/visibility peak certificate; existing REC/REI dependency pins unless separately changed; original BASS kinetic lane gates.

**Loop2도 완료했다.** 실제 REC→별도 REI 소비기→native RK4 이력→BASS opacity/세 clock visibility를 연결한 pure-H, one-T, prescribed matter-only FLRW(z1200→1000, 초기 xp=0.8) benchmark다. 이력3개와 constant-x control3개, 독립91검사를 통과했고 `PROMOTE_SCOPED_EXPANDING_BENCHMARK` 판정을 받았다. Fine-grid xp 최대절대오차1.9641732684760882e-11, 추가 optical depth 상대오차3.578215511124118e-7, 세 clock 간 tau 최대차4.440892098500626e-15다. 이는 EoR scenario/F05 enclosure/general Bianchi/finite-T admission이 아니다. Actual 결과는 `loop2/evidence/INDEPENDENT_HISTORY_RESULT.json`, 독립 판정은 `review/LOOP2_REVIEW.json`에 있다.

게시 위치는 `docs/research_sync/REI-REC-BASS-SYNC02-20261005`이며 atomic repo에는 같은 task ID의 `consumer_returns/` 연결을 추가한다. 기존 CURRENT/TASKS/원문/실패 receipt는 수정하지 않는다. 기존 branch에 non-force append하며 PR의 draft 상태를 유지한다.

공통 immutable URL: `https://github.com/cosmosapjw-quantum/rei_bianchi/blob/7c10471375837b85d58ec39fe1e8242429b74700/docs/research_sync/REI-REC-BASS-SYNC02-20261005/README_KO.md` — 고정된 최종 과학·계획 commit이다. 직접 ChatGPT 스레드 메시지 전송은 사용할 수 없어 수행하지 않았다. Git/PR handoff 준비와 각 스레드의 실제 수신 ACK는 별개다.

최종 동시 결과: FLRW06 prepared native gate를 실제컴파일/18record/167scalar로 완료했다. 다시 compiler대기 또는 미실행 후보로 선택하지 않는다. 별도 late_FLRW06 반환·review를 읽고 actual accepted-stage와 독립 U/edge 소비자 계약으로 이어간다. CR은 새F04D event jets 완료를 수신했고 다음F04E는 실제F05 receiverbinding을 기다린다.

최종 owner 수신: F05 actual7000steps/MPFI200PASS 완료, F08 conditionalstage140testsPASS·전체 pairedhistory미실행. 이는 `bda0feef` owner 반환 수신이며 여기서 재실행한 결과가 아니다. F04E는 actual F05 receipt와 연결하고 F08 source 동시 수정은 피한다. FLRW06은 양쪽 동시 완료를 하나로 합친다.

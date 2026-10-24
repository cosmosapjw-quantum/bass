# BASS B3a 사건률 adapter — 다음 대화 인수인계

## 현재 기준

- 중앙 authority: `cosmosapjw-quantum/rei_bianchi@0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`, `research/orchestration_longterm_20261023/assembly/HANDOFF_bass_KO.md`.
- 기존 BASS owner: `research/background-kinetic-g1b-20261023@28b7705cbb236c26e1b273335f6da7e9da4d1aaf`, PR184 Draft/open/unmerged.
- 이번 연구 branch: `research/bass-b3a-event-source-20261024`, [PR185](https://github.com/cosmosapjw-quantum/bass/pull/185)는 실제 생성되어 **Draft/open/unmerged**다. 과학 payload commit은 `f4f12a162b446f7fc42759f88d544749435fb35b`, 기존 G1B base 및 실제 expected SHA는 `28b7705cbb236c26e1b273335f6da7e9da4d1aaf`다. 과학 commit의 Git byte readback은61/61 PASS이며 원 응답은 [delivery/PUBLICATION_ACK.json](delivery/PUBLICATION_ACK.json)에 있다. 최종 live branch는 이후 metadata-only 인수인계·receipt commit을 가리킬 수 있으므로 새 턴에서 live ref와 최종 companion receipt를 확인한다. 이 문서 자신의 최종 SHA를 주장하지 않는다.
- 이중 backup은 **DUAL_BACKUP_ACK**: science capsule의 Dropbox completed 및 Google Drive success 응답을 [delivery/BACKUP_ACK.json](delivery/BACKUP_ACK.json)에 보존했다. stage evidence는 누적 capsule 하나로 최종 packaging 때 백업했으며, 각 단계 실행 당시 별도 upload를 했다고 쓰지 않는다. Backup provider ACK/크기 검증은 별도 remote full-byte readback을 뜻하지 않는다.
- 이 B3a source-only 단위의 R1–R10/C1–C10와 외부 전달은 완료다. 초기 packaging/backup checkpoint의 PENDING은 원 receipt의 당시 상태로 보존하며, 현재 publication 상태는 **ACKNOWLEDGED**다. 이후 B3b/c·B4·B5의 미완료와 merge/production 금지는 그대로다.
- 경로: `research/bass_b3a_event_source_20261024/`.
- 원 준비 연구: `BASS_B3A_EVENT_SOURCE_20261024`. 새 구현 단위: `BASS_B3A_REC_EVENT_ADAPTER_20261024`.

## 이번에 실제로 닫은 범위

불변 국소 `dt_proper*dV_proper=dV4/c`당 event measure로 Q와 관측자 의존 K를 구현했다.
기존 kinetic 상태 가중치의 `E_new/E`를 event rate에 적용하지 않는다.
고정 observer의 tensor covariance와 observer 자체의 변경을 구별한다.

A/B at beta=(3/5,0,0): cQ/P=(5/4,3/4,0,0), PiRate_A/P=(3/10,-3/20,-3/20),
PiRate_B/P=(5/22,-5/44,-5/44), 차이=(4/55,-2/55,-2/55).
일반식 `2*b^2/[3*gamma*(3-b^2)]`는 **고정 fixture에 대한 x축 boost**다.
일반 벡터의 속력만 대입하면 틀리며, (1/5,2/5,2/5)에서 차이 xx/P는
`-286408/10384605`다. G1B collisionless radial reduction 반박이 아니다.

실제 REC PR130 HEAD `93e1bdc8298db9a7c16f77d4bf64985a0c3f25aa`의
LINE01 `standalone_detached`를 선택했다. matter-rest local orthonormal frame,
proper-time/density, effective escaping gross down/up를 각각 복원한다.
Native/history의 signed net ledger를 gross로 승격하지 않는다.
반대 source는 atomic excitation internal energy이며 thermal·ionization·electron
yield는0이다. PiRate_hat은 별도 반환하고 현재 BASS Source.pi는 보존한다.

독립 Fraction23/23, 실제 새 Wolfram exact residual0, 초기 adapter12/12,
독립 guard FAIL, targeted RED6실패, 최소 수정 후 targeted3/3와 final15/15,
최종 독립 physics/math+figure 및 code PASS_SCOPED가 모두 원본 기록으로 남아 있다.
원 NumberQ7/16실패→NumericQ/exact-real16/16과 추가4/4는 사용자 receipt의
과거 기록으로 보존하며, 이 새 실행과 합산하지 않는다.

F1은 잘못된 source-origin frame/clock 허용, F2는 frame을 바꾸면 physical
transfer 중복 검사를 우회하는 문제였다. canonical origin/clock 검사와
`(owner, epoch, transfer_id)` key로 닫았다. 정확 zero-source는 별도 검증했다.
최초 실패를 지우거나 모든 단계가 첫 실행에 통과한 것으로 쓰지 않는다.

## 유지할 결손·자원·범위

1. PR184 receipt6373136365의 S1/S2 whole-byte recovery·110 payload·curved process argv/exit0를 재사용한다. 대량 archive 재다운로드, 과거 campaign/IVP replay, 과거 그림 rerender는0이다.
2. B1의 과거 pytest 정확 argv/cwd는 미확인이다. B2는 기존 finite-window selected acceptance만 보존하며, 이번 독립 검토가 과거 raw array 전체의 새 심사였다고 쓰지 않는다.
3. `34.1262904040002`초는 부분 과거 합계다. `remaining_campaign_wall_seconds=null`, `remaining_campaign_cpu_seconds=null`, `budget_reset=false`를 유지한다.
4. 새 계측 비용은 RESOURCE_LEDGER.json을 따른다. Wolfram ceiling25초는 실제 kernel elapsed가 아니다. 새 IVP0, 과거 campaign replay0이다.
5. source-only callback=True는 합성 검사다. 실제 finite photon stock·population advance·source-age/history receiver를 인증하지 않는다. donor reservoir나 positivity clipping을 발명하지 않는다.
6. B3b/c 물리적 transaction, B4 restart, B5 domain admission은 미완료다. global percentage=null. merge·production 활성화 금지.
7. 새 턴의 Python/C++/Wolfram runtime은 실제 probe한다. 이번 턴에는 Python/C++ 실행과 Wolfram 호출이 성공했다. pytest/SymPy의 기본 환경 PACKAGE_MISSING을 container SERVICE_ERROR로 바꾸지 않는다.

## 다음 작업의 짧은 입력문

```text
$physmath-research-loop로 BASS 연구를 이어가라.
중앙 authority는 rei_bianchi@0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17의
research/orchestration_longterm_20261023/assembly/HANDOFF_bass_KO.md다.
BASS research/bass-b3a-event-source-20261024의 실제 최신 ref와 PR 상태,
AGENTS, 병렬 변경, research/bass_b3a_event_source_20261024/HANDOFF_KO.md,
DAG.json, CLAIMS.json, RESOURCE_LEDGER.json, delivery receipt를 먼저 읽어라.
현재 source-only REC LINE01 adapter와 독립 PASS_SCOPED를 재사용하라.
실제 receiver·finite-stock·population transaction 계약을 좁게 확인한 뒤
한 물리적 교환 owner의 다음 bounded 연결을 제안·실행하라.
native/history net ledger를 gross로 바꾸거나 같은 transfer를 두 번 charge하지 마라.
과거 archive·campaign replay 금지, remaining budget=null/budget_reset=false 유지.
실제 runtime probe, 독립 검토, 최신 expected SHA를 거친 후만 push하라.
과학 판정과 단계별 backup/publication ACK를 구분하며 merge/production은 금지한다.
```

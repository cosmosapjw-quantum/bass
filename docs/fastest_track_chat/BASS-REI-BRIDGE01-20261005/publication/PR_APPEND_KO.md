## 2026-10-05: BASS–REI proper-density/Thomson visibility bridge

REI의 새 HHe/FT03 native state는 proper cm^-3를 쓰지만 BASS의 기존 Thomson visibility는 proper m^-3를 받는다. 이전 host dispatcher에는 두 typed state를 연결하는 경로가 없었다.

`rei_visibility` 모듈은 실제 REI source validation을 사용해 전자 population을 SI로 전달하고, 기존 BASS MaterialFrame·ElectronState·visibility 적분을 재사용한다. 반환값에 전자밀도와 방향별 normal-time rate를 포함하므로 D의 중복 적용, 단위·snapshot·observer-tail 소유권을 점검할 수 있다. REI pin을 `41e4592aa494b48929dcd23fc8504c169a98a908`로 갱신하며 REC pin과 기존 seven-kernel 본문은 유지한다.

scoped native20개(bridge10+API1+기존 visibility6+legacy3), 독립 Decimal70 검산786개/native140회, 실제 controlled FT03 두 history(1000/2000 interval) 검산22029개를 통과했다. source identity와 실행 명령은 `evidence/FINAL_INTEGRATION.json`, 독립 검산은 `INDEPENDENT_BRIDGE_RESULT.json`·`CONTROLLED_HISTORY_RESULT.json`에 기록했다. 범위는 정확한 변경 host modules와 actual REI crate를 묶은 scoped native 시험, controlled FT03 finite history의 downstream visibility다. 전체 BASS build·expanding cosmological history·물리적 photon spectrum admission은 이 증분의 완료 주장이 아니다.

FT03 density adapter는 rate-domain admission을 하지 않는다. API clock은 normal seconds이며 conformal 변환은 아직 별도 구현 단위다. RCT default OFF, HE/CR/HH 장기 연구 lane과 기존 scientific gates를 유지한다. 다음 단위는 실제 expanding REI history의 typed export와 `BASS-REI-EXP01` 소비다. 본 PR의 merge 또는 production 전환은 수행하지 않는다.

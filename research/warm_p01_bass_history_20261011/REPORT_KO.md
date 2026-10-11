# Warm P01 → BASS sampled-visibility 실행 사실 보고

- 범위: 검증되어 저장된 warm P01의 17개 proper-time epoch(16셀)를 BASS PR139 커밋 `41fa2d5f6874a6d9eb1a151ff83b2d56f1d2fd25`의 원본 `frame.rs`·`visibility.rs`에 입력한 유한 sampled-visibility component. REI solver나 전체 BASS crate, 구 PR135 adapter를 실행한 것이 아니다.
- 동일성: REI interval JSON, NPZ, provider contract, background 네 고정 SHA와 BASS 두 소스 SHA가 모두 계약과 일치했다. NPZ/JSON 저장 시간 17/17, 이온 상태 51/51이 binary64 비트 단위로 일치했다. 저장된 T는 30000–110000 K 가드 안이고 `nH/(1+z)^3` 최대 상대 차이는 `4.440892098500626e-16`(계약 상한 `1e-11`).
- 구현: 격리된 `receiver.rs`는 원본 BASS `ElectronState::new`와 `integrate_rest_frame_sampled_visibility`를 호출한다. nHe/nH는 계약의 `0.24/(4*0.76)`이고 cm^-3→m^-3 변환은 한 번만 했다. `run_and_validate.py`는 전송된 binary64 입력에서 Decimal 정밀도 80으로 독립 유한 선형 셀 적분·생존·질량 대조를 계산했다.
- 실행: Rust 빌드 1회 exit 0(0.772초), baseline tail0 및 tail0.25 receiver 실질 실행 각 1회 exit 0. 기준 셀의 첫 광학깊이 `1.2799831081953007e-07`, tail0.25에서 `0.2500001279983108`. 각 edge의 n_e/q/τ/생존, 각 cell의 평균 q/질량이 계약 수치 상한 안에 들었다. baseline 최대 n_e/q/평균 q 상대 오차 `1.673e-16`, τ/질량 상대 오차 `3.752e-16`; tail0.25 역시 각각 `1.673e-16`, `2.633e-16`. endpoint tail과 질량 균형도 통과했다.
- 부정 대조 3회: 16-epoch 입력, 잘못된 이온 비율, 음의 observer tail 모두 exit 2로 거부했다. 원시 입력과 명령·stdout·stderr·종료값은 각각 `output/INPUT_*.tsv`, `output/RAW_*.json`; 외부 runner 기록은 `RUNNER_RAW.json`. 첫 실패 없음.
- 예산: 허용된 빌드 1/1, 실질 BASS 실행 2/2, 부정 실행 3/3. chemistry/REI solver·네트워크·기존 작업 트리 수정·게시 모두 0.

이것은 사실 검증 보고이며 과학적 입장은 독립 Astra 검토 전까지 미승인이다. 전 구간 관측자 tail, 화학/표본 수렴, 복사 backreaction, CMB 또는 전역 EoR 승인은 주장하지 않는다.

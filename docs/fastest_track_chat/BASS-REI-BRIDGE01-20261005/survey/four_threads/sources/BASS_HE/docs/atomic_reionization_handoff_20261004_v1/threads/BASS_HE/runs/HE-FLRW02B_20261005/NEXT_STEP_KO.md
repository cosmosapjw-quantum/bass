# HE-FLRW02B owner native completion

상위 상태는 partial이다. input은 rei_bianchi 3dceea736f9aaa363617a9a6a5bb2854d9ff9986이며 c433eaee7b120a5bfb7c35e802c4b218315bf210까지 관련 Rust source는 불변이다. 최신 실제 HEAD와 변경 경로만 대조한다. consumer는 BASS_HE 스레드에서 read-only다.

1. DELIVERY_RECEIPT.json의 전체 ZIP을 확보하고 archive SHA와 MANIFEST.json을 확인한다. 상세 INPUT_IDENTITY, GOLDEN, native proposal 및 실패/성공 로그는 ZIP에 있다.
2. 동일 입력·종별 source reference·두 scale 검사·허용오차를 충족한 mixed native 반환이 이미 있으면 수신한다. pure-H connected_cell의 기존 84시험 반환을 이 mixed gate의 완료로 쓰지 않는다.
3. 없다면 ZIP의 proposed_consumer/he_flrw02_absorption.rs로 기존 제안을 대체한다. 두 버전을 함께 추가하지 않는다. test 위치는 rust/rei_microphysics/tests/he_flrw02_absorption.rs다.

    cargo test --manifest-path rust/rei_microphysics/Cargo.toml --test he_flrw02_absorption --locked -- --nocapture

준비 파일은 이 채팅에서 NOT_COMPILED_NOT_RUN이다. 5e-14 relative+1e-300 absolute를 2e-12로 확대하지 않는다. 신규 함수나 physics wrapper를 만들지 않고 실제 provider/hhe_rhs/homogeneous_photo_rates를 호출한다. 전체 84시험은 단순 전달 때문에 재실행하지 않는다.

반환: exact repo/commit/tree/source/test identity, REFERENCE_INPUT/GOLDEN/proposal SHA256, 명령/exit/stdout/stderr, FLRW02_RESIDUAL 및 FLRW02_REFERENCE 최대 absolute/relative와 label, 두 test 결과, NOT_RUN. 실패면 source/units/species/roundoff/compile 환경을 분리하고 최초 실패를 보존한다.

이 검사는 finite instantaneous absorption binding이다. physical fit accuracy, thermal closure, redshift trajectory, QV geometry 및 full history admission을 인증하지 않는다. RCT/HE-F2/HE-F3/legacy HOLD를 유지한다. owner의 REI-CHAT-FLRW04_EVENT_WEIGHTED_CONSUMER_CONTRACT와 외부 REI-F04 remainder 인증은 서로 별도이며 여기서 재시작하지 않는다.

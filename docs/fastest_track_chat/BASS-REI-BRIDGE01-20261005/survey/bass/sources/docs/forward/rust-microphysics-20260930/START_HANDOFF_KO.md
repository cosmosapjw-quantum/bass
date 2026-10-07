# BASS Rust 우선 미시물리 통합 시작

기준은 `artifact/native-r4-delta-rf02b-20260826-r1`의 `eb01d5e`이다. 현재 `origin/main`은 Rust Cargo 트리가 없는 복구 계보이므로 이 기능 브랜치에서만 작업한다.

REC 검토된 소스는 `d3cc6e0`, REI Rust 전용 정본은 `1bda1e8`이다. 두 커밋을 Cargo Git `rev`로 고정한다. 미시물리 공식은 각 자식 crate가 소유하며 BASS는 프레임, 시계, 단위 경계와 호출만 소유한다.

이 작업은 고정 입력 Rust 구현 통합이며 완전 재결합/재이온화 역사나 물리 생산 판정이 아니다.

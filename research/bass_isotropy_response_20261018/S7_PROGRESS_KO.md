# S7 단계별 실행·게시 기록

## 1. 새 실행 intake와 실행 전 게시

S6 science 04a3a851, closeout a9704c6f를 새 백업과 최신 PR에서 발견해 재사용했다.
신규 S7 source/preregistration commit은 2865f60bf0a247eaab4997c222ad82ae22a4c8fa다.
원격 변경50개 blob과 두 사전등록 바이트를 확인했다. PR comment6264733242.
사전등록 ZIP: BASS_S7_PREREG_COUPLED_NATIVE_20261019_2865f60b.zip,
172803B, SHA2567398aa6268e4d345419652c2f41efe67305b1d049f3d12f1cc7308b699084672.
Drive raw/CRC/manifest51/51 및 Dropbox provider content hash를 확인했다.
Dropbox 직접 raw GET은 URLError였으며 raw readback으로 세지 않는다.

## 2. 실제 실행과 구체적 실패

결합 run01: 36입력 중28이력 완료,8양의 support 실패; 별도benchmark7이력.
원래 binary64 moment observer에서2이력이3e-15 경계 FAIL였다. Hamiltonian,
cohort energy, event, positive weights, parity, frozen stock은 통과했다.
Radiation linear 오차비3.9907757424/3.9953428422, donor midpoint비 약4를 실제 확인했다.
Native run01: 51입력 중42측정,9support 실패. 원본 REI57파일을 무변경 컴파일했다.
b0=.6,nmu32,P24 angular |deltaA|=9.94529756587e-4로1e-6 목표 FAIL이다.
흡수 slab에서도 동일 angular 오차가 남는다. 한 P2 birth의 f64 moment observer도 경계 FAIL였다.
각도·출생시간·bin·source panel 축은 분리했고 원래 실패 기록을 그대로 보존한다.

## 3. 검증기 산술의 제한 수정

저장된 binary64 mu/alpha를 정확한 유리수로 평가하면 문제의 moments는
원래3/10^15 범위 안이다. 곱셈·합산 순서가 경계 오판을 만들었다.
R2는 exact sum(alpha P_l)의 검증만 수정한다. 음의 weight, 정규화 재정의,
허용오차 완화, birth 재가중, source/owner 변경은 없다.
R2 분석 계약을 먼저 게시한 뒤 동일 raw output의 SHA/실행 commit을 묶어 재판정한다.
이는 이미 본 결과에 대한 검증기 수정이며 새 물리 예측의 사전등록으로 포장하지 않는다.
ODE 또는 native 실행을 반복하지 않는다. R2 판정은 아직 실행 전이다.

## 다음 종료 경계

R2 재판정, 실제 결과 문서/DAG, source·readback·handoff 게시와 두-cloud 백업을 마친다.
새 S8/production/fullEoR 작업으로 자동 확대하지 않는다. Full native coupled MD14,
full tangent 실행 및 반응성 전체 이력은 후속 연구다.


## Stage 3 — R2 실제 재판정과 R3 한 이력 수정 사전등록

Stage 2 `c689dcf1`의 2,195,973-byte ZIP은 Drive raw/SHA256/CRC 및 manifest 93/93, Dropbox의 전체 object content hash와 size가 일치했다.

R2는 원래 물리 실행을 반복하지 않았다. Native 808/808 birth exact moment PASS; 42개 물리 측정과 9개 support 실패 불변. 큰 b 정확도 실패 2개는 유지된다. Coupled는 640개 제약 birth 중 하나의 참된 M4 초과를 발견했고 원래 FAIL을 보존했다.

R3는 `b03_n32_P24_K64` 한 이력의 **새 birth**에만 기존 P24 API의 내부 `atol=1e-15`를 지정한다. 최종 exact gate `3/10^15`, support, 원 owner 및 여섯 R2 소스는 동일하다. 두 표적 테스트 PASS; 본 이력은 이 단계 게시와 readback 이후에만 실행한다. 비교는 SHA로 고정한 원래 이력과 GL128 bytes에 대해 시행한다.

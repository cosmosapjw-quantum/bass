# BASS background evolution: 게시 복구 마감

2026-10-23 KST. 과학 결과를 다시 계산한 단계가 아니라, 완료된 연구의 실제 Git 게시와 보존을 복구한 단계다. 원 S2 과학 상태는 R1-R10/C1-C10 PASS_SCOPED이며, 전체 BASS 목표의 G1-G4는 그대로 남는다.

## 실제 게시와 원본 일치

원 기반은 PR181의 797d66580448dad7fc41f2c2db31fe0eb37908bf다. 새 branch research/background-evolution-20261023와 Draft PR182를 만들었다. 복구된 source/result snapshot은 3c14488905e0a51e2f62e197d980116e71679466다. 원 local 준비 commit65dc7b5는 현재 remote 실행 identity가 아니다.

A core/contract: 2bc6a602f199620de735b3d2521b274160db7d4f.
B legacy/Rust: c69911ebf256f338769e4c76ea87bf2771cbabe6.
C theory/results: 99da31016ed34cfc87048aecec0bb83f9fdbfee9.
원본 개행 복원: 3c14488905e0a51e2f62e197d980116e71679466.

원 S2의 선별18파일을 원격 Git blob identity와 대조해 모두 일치했다. 첫 비교에서 THEORY_KO.md 마지막 개행1byte 누락을 검출했으며, 실패 receipt를 보존하고 원래13267bytes/blob da4477a060c4e9d35fac9fd9547ef8028bfbeb9f로 복원했다. 수식/실행 코드/수치값은 변경하지 않았다. 원본 중 나머지135파일은 full S2 archive에 보존하며, 전체153파일을 Git에 모두 게시한 것이 아니다.

## 복구한 과학 내용과 원 실행 근거

Normal-frame gamma-law Omega 보존과 rotating-frame WQ 누락 교정, H로 나누지 않는 fixed-scale proper-time Einstein/sector conservation core, 독립 Rust RHS/constraints, 양의 antipodal massive+radiation stream benchmark를 보존했다. pi_m와 pi_r는 별도로 유지하며 geometry에서는 tensor를 합한다.

원 실행 값: legacy19/19, Rust8/8, core7/7. 12family histories 최대 scaled constraint2.6573681859887917e-12; 7analytic histories 최대 scaled state error2.9095205096668255e-11; 40arbitrary defect states 최대1.092169555785652e-15; 97Python/Rust states/3059components 최대2.684841162521217e-16; 45guards. Streams4free+3reference의 density 비교6.906280621051864e-11, default/tight8.151268934421974e-11이다. 이 수는 과거 실행을 재사용한 것이며 이번 재실행 수는0이다.

닫힌 dust/radiation은 H=0을 지나 수축하는 저장 이력이 있다. 초기 stress가 상쇄된 stream은 성분별 진화 차이로 이후 전단이 생긴다. 원 두 PNG를 직접 읽었고 재렌더하지 않았다. 여섯 방향 이산 분포의 stress isotropy를 분포 전체의 SO(3) isotropy로 확대하지 않는다. Reduced reference는 moment 함수를 공유한다. Rust는 RHS 평가기이며 전체 적분기는 아니다.

-2HC와 기존-3HC는 각각 Raychaudhuri 및 spatial ij-Einstein off-constraint 자유진화의 차이다. 기존 helper를 무조건 잘못된 식으로 바꾸지 않았다. General matter source 입력을 받는 것이 일반 tilted/curved kinetic closure를 구현한 뜻도 아니다.

## 실제 보존

원 S2:1465460bytes, SHA256 2dd239da1c4e6130f2982e99b35ec2274d52f58fc99e94380a76ebc4c776119f. Drive base64 text의 전체 회수/복호화, ZIP CRC,153payload 크기/SHA256와 전체 inventory를 검증했다.

최종 복구 capsule: BASS_BACKGROUND_RECOVERY_FINAL_20261023.zip,1456177bytes, SHA256 ba9c8ddbf8e181d3cb3b96363c3968bec01e0f937c0fa124c3082a9ec5632f69. 원 S2 ZIP 자체와 복구 실패/성공 영수증, 재현 가능한 해시 검사, 다음 인계를 담는다.

Drive1Blul8udl_6L9EyRbncEEhqftryhqaELW: upload 성공 후 전체 원격 ZIP 회수. 원본bytes/SHA256/CRC/9outer payload/중첩S2의 exact bytes 검증 PASS.
Dropbox id:BSpOijBcT10AAAAAAD_v4w: completed ACK와1456177bytes 일치. Dropbox 전체 원격 ZIP 다운로드 검증은 NOT_RUN이다. 양쪽 모두 저장 ACK를 받았지만 양쪽 모두 whole-byte readback했다고 주장하지 않는다.

AB checkpoint도 Dropbox id:BSpOijBcT10AAAAAAD_v3A에 보존했다. 현재 문서/최종 receipt는 포장 이후 추가되므로 이미 동결된 archive 안에 소급 삽입하지 않는다. 마지막 Git commit/PR댓글이 최종 전달 상태를 소유한다.

## 현재 완료와 다음 의무

이번 복구의 새 과학적 적분/build/suite replay/figure rerender는0이다. 현재 Python/C++ probe는 성공했으며 원격 Desktop Commander의 실제 probe는 usage pause로 거절됐다. 기존 독립 science review를 재사용했고 새 독립 reviewer 및 전체 repository CI PASS는 주장하지 않는다.

G1 source-qualified curved/tilted kinetic adapter가 다음 연구다. G2 full thermal/radiative/emitter four-momentum exchange, G3 production/restart, G4 global physical-domain convergence는 남는다. 완료율은 이번 유한 과학20/20과 배송 복구를 분리하며 전체 solver 백분율은 미정이다. main merge, force-push, production 활성화는 하지 않았다.

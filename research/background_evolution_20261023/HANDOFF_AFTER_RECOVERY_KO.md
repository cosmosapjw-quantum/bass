# BASS background evolution: 게시 복구 이후 인계

2026-10-23 KST. 이 문서는 원 S2 과학 인계를 대체하지 않고 실제 게시 상태를 보완한다.

```text
BASS background evolution의 다음 연구를 physmath-research-loop로 이어가라.
repo: cosmosapjw-quantum/bass
PR: 182 (Draft/open; merge하지 않는다)
branch: research/background-evolution-20261023
복구된 source/theory/result snapshot:
3c14488905e0a51e2f62e197d980116e71679466
기반: 797d66580448dad7fc41f2c2db31fe0eb37908bf
unit: research/background_evolution_20261023/

먼저 최신 branch/PR 댓글을 읽고 RECOVERY_FINAL_KO.md,
HANDOFF_AFTER_RECOVERY_KO.md, RECOVERY_DAG.json, RESULTS.json,
THEORY_KO.md, CONTRACT.md, S2_ARCHIVE_LOCK.json을 읽어라.
최신 문서 commit은 source snapshot 이후일 수 있다. 과거 실행 commit으로 소급하지 마라.

원 전체 패키지:
BASS_BACKGROUND_S2_20261023.zip
1465460 bytes, 153 payloads + PACKAGE_MANIFEST.json
SHA256: 2dd239da1c4e6130f2982e99b35ec2274d52f58fc99e94380a76ebc4c776119f
Dropbox: id:BSpOijBcT10AAAAAAD_t3Q
Drive: 1v6iIk8h11Zi078n5L4SsuX5idShTAk46
Drive 파일은 ZIP의 base64 text다. 원본 bytes를 fetch하고 decode한 뒤 위 해시를 확인한다.
현재 runtime에 파일이 없으면 연결 도구로 직접 복구하고, 사용자에게 수동 이동을 요구하지 마라.

Git에는 원본 중 18개 파일과 게시 복구 문서만 선별 게시했다.
validate_background.py, test_background_core.py, 전체 보고서/원 인계/DAG,
원시 NPZ/CSV/PNG, Wolfram/Fraction 검산, 실패 증거 등은 전체 S2를 복구해 읽어라.
Git만으로 전체 과학 재현 패키지가 완성되었다고 가정하지 마라.

R1-R10 및 C1-C10의 기존 scoped science는 완료다.
legacy19, Rust8, core7, 12family/7analytic/rotatingKasner1,
40constraint-derivative/97native states/45guards,
4free+3reference stream histories를 source가 같으면 재실행하지 마라.
이번 게시 복구에서는 새 과학 적분/build/suite replay/그림 재생성이 모두0이었다.
18개 선별 파일 Git blob은 원 S2와 대조 완료했다.
이론노트 마지막 개행1byte 누락은 3c144889에서 원본대로 복원했고 실패 영수증도 보존했다.

다음 준비된 연구는 G1 source-qualified curved/tilted kinetic adapter다.
최근 FD96/non-LRS photon 및 HE36/REC125/REC127의 실제 source/result delta부터 읽어라.
기하 연산자의 일반성을 곧바로 전체 kinetic closure의 완성으로 간주하지 마라.
고정 L, kappa=8*pi*G/c^4, tau=c*t/L, signature(-,+,+,+)를 보존한다.
Source.pressure=kappa*L^2*p_phys
Source.pi=kappa*L^2*Pi_phys (현재 stress)
Source.energy_transfer=kappa*L^3*Q_total/c
Source.momentum_transfer=kappa*L^3*force_density_phys
HE36 J_HE[Pa/s]는 dPi_hat/dtau|react=kappa*L^3*J_HE/c에 연결하며
현재 pi 입력과 혼동하지 마라. HE Q와 reservoir dEth를 두 번 더하지 마라.
Normal/common-bulk frame 변환은 전체 stress-energy와 four-force에 적용한다.
rest/binding/work/emitter/photon reservoir의 실제 owner 없이 compensator를 발명하지 마라.
1/H를 쓰거나 H<0을 거절하는 donor를 turnaround core에 바로 연결하지 마라.

G1 -> G2 complete thermal/radiative/emitter four-momentum closure.
C10+G1 -> G3 production dispatch/restart/adapters.
G1+G2+G3 -> G4 global physical-domain convergence.
전체 완료율은 미정이며 현재20/20 scoped stage를 전체 solver100%로 쓰지 마라.
각 ready group 전에 최신 병렬 변경을 확인하되 완료 계산은 재사용한다.
현재 runtime을 실제 probe하며 과거 환경 실패를 상속하지 마라.
매 단계 source/result/검증/게시/백업 상태를 따로 기록한다.
```

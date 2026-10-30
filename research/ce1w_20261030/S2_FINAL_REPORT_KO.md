# BASS CE1-W · 실제 BASS Rust 기반 MPFR192 시간 패널 수렴 연구

**2026-10-30 · 연구 범위 한정 완료 · 상위 DAG 9/15, CE-1 PARTIAL.**

## 물리·코드 provenance
- 독립 Draft PR #268, 기준 부모 PR #266의 정확한 Git HEAD `2d5076ecb2307cea39c1b608396c34050021ebc3`. 원본 부모, main, 형제 PR 불변, 병합하지 않음.
- 양의 원본 이진 6-cell continuum, 8 반사, 질량 없는 무충돌 전체 팽창 대각 Bianchi I, Λ=0, 계량 (-,+,+,+), `u=t/Tstar`, `ell=ln a`, `h=dell/du`, 초기 shear (.2,-.13,-.07), `u∈[0,.08]`. 원래 엄격한 허용 `max|Δh|<1e-5` 그대로.
- 원본 physical table SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`. 저장 GL6=216 ray 및 GL8=384 ray는 패널 수 4·8·16 전체에 걸쳐 **각 source별 ray·mass SHA 동일**. 새로운 angular quadrature, 온도 spectrum, collision/tilt/polarization 없음.
- 출발 source forcing은 PR #264의 유리수 K=12 전구간 상계로, GL6 `3.010630537202566e-12`, GL8 `6.164277064237367e-14`. 정확 Fraction을 MPFR192 외향구간으로 변환. 본 단계는 source 증명을 재창안하지 않음.
- 출발 코드: `research/ce1v_20261030/cross_certify.py`와 `research/ce1u_20261030/certify_gl_coupled.py`의 CE1-C/G 원본 `residual_taylor_mpfr`, 정확한 Hermite 이진 knot jump 및 기존 양의 Dini propagation. 새로운 `research/ce1w_20261030/time_panels.py`는 **N=4/8/16의 실제 새 RK4/Hermite path 각각**에 대해 전 패널 잔차를 반복 계산함. 각 path.times/states/coefficients SHA는 machine evidence에 보존.

## 같은 source에서 실제 4/8/16패널 MPFR192 인증

| 분포 | 패널 | 초기 h | source h | MPFR 시간+knot h | **총 h 상계** | 동일 CI 계산 초 |
|---|---:|---:|---:|---:|---:|---:|
| GL6 216 rays | 4 | 9.2868214e-17 | 2.4187939e-13 | 8.388529203783612e-7 | **8.388531623506172e-7** | 5.053 |
| GL6 216 rays | 8 | 9.2868214e-17 | 2.4187939e-13 | 1.000656281321961e-7 | **1.0006587010445202e-7** | 10.153 |
| GL6 216 rays | 16 | 9.2868214e-17 | 2.4187939e-13 | 1.2217041571120914e-8 | **1.2217283543376827e-8** | 20.351 |
| GL8 384 rays | 4 | 9.2868214e-17 | 4.9524893e-15 | 8.388529203551374e-7 | **8.388529254004949e-7** | 8.900 |
| GL8 384 rays | 8 | 9.2868214e-17 | 4.9524893e-15 | 1.0006562804905293e-7 | **1.0006563309441047e-7** | 17.721 |
| GL8 384 rays | 16 | 9.2868214e-17 | 4.9524893e-15 | 1.2217041950040127e-8 | **1.2217046995397674e-8** | 35.577 |

이 오차 상계는 각 실행에서 실제로 생성한 **별개의 exact-binary RK4/Hermite path**에 조건부 적용된다. 각 단계 모두 원래 (10^{-5}) 목표 MET이다. GL6의 패널 수 4→8 오차감소 약 8.38배, 8→16 약 8.19배이고 실행시간은 약 2배다. 관측 결과는 약 3차 수렴에 일관되지만, 무한 반복에서의 수렴률에 대한 정리/증명을 대신하지 않는다. GL6는 같은 패널 수에서 GL8과 거의 같은 h bound를 더 작은 wall-time으로 달성한다. **고정된 허용 기준만 만족시키는 최소비용 후보는 여전히 4패널**이고, 16패널의 추가 비용은 보다 엄격한 실제 사용자 요구가 있을 때에만 정당화된다.

## 진짜 native BASS Rust 과학 검산
GitHub CI가 원본 `_rustcore/src/kinetic/comoving.rs` Git blob `a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84`를 고정하고 `rustc 1.94.1`로 `research/ce1r_20261030/sky_time_derivative.rs`를 컴파일하였다. 각 GL6/GL8의 N=4/8/16 경로에서 41개 고유시간 표본의 E/P/E′, 무질량 trace 및 에너지 연속방정식을 별도 Rust binary64로 비교했다. **6/6 경로 PASS**, 전 항목 최대 절대 차이 `2.525757381022231e-14`. 이는 구간 유효성을 입증하는 MPFR 증명이 **아니다**.

## GitHub에서 실행한 실제 검증 및 실패 복구
- 최초 SHA `85751fddca54ecca0a0a17a3c2ba4f49be2daa91`의 CI #40983978817은 Python 구문 괄호 누락으로 **FAIL**. 해당 오류는 과학 계산 시작 전에 발생하였고 S0 ZIP은 정상 생성됨.
- 최소 구문 수정 `3279e1c1c652eedfc6b0ed18668084d19a988405`과 추가 CI compileall `d88219f46d9fbb88bdaf44f4e15891d3c7cd2b77` 뒤 [CI #40984170518](https://github.com/cosmosapjw-quantum/bass/actions/runs/40984170518) **SUCCESS**.
- 이 SUCCESS CI는 6개 신규 MPFR192 전체 패널 증명, 원본 BASS Rust 6×41시점, 독립 데이터 기반 **10/10 pytest PASS**, compileall PASS, S0/S1/S2 각 payload SHA256 ZIP archive 생성 완료.
- 성공한 코드 HEAD `d88219f46d9fbb88bdaf44f4e15891d3c7cd2b77`. S2 문서·영수증 게시로 새 HEAD가 생기면 해당 HEAD의 CI 판정은 별도 관찰하며, 이전 코드 CI의 성공과 혼동하지 않는다.

## 백업과 한계
S0 원본 Git 체크포인트 `9b4e7bdc17ccf87854125c3e261a86a5972bf5a2`, S1 구현 Git 체크포인트 `85751fddca54ecca0a0a17a3c2ba4f49be2daa91`, 수정 코드 `d88219f...`, S2 최종 보고서·handoff와 명세 `research/ce1w_20261030/`. GitHub Actions S0/S1/S2 ZIP 포함 raw numerical JSON을 각각 Google Drive·Dropbox에 **실제 업로드**했고 Drive 전체-byte SHA256와 Dropbox provider content hash/size를 검증했다. Dropbox 전체 bytes readback은 NOT_RUN. 상세 단계별 object ID는 `DELIVERY_RECEIPTS.json`.

**CE1-W 완료 판정은 이 범위에서만 유효**: 전체 BASS DAG **9/15** (21 edges), CE-1 PARTIAL, 새 상위 노드 0. 독립 저자의 실제 R6/C9, 전체 CPython/MPFR/Rust 프로그램 형식증명, 일반 polarized/tilted Einstein-Boltzmann 생산 solver, CMB 관측 likelihood는 미검증. `production_ready=false; merge_ready=false; auto_next=false`. 자동 병합하지 않는다.

**다음 과학 방향:** 이 수렴 데이터를 기준으로 목표 정확도 대비 계산비용을 최적화하거나, CE1보다 상위의 실제 미완료 물리적/생산 경로를 구체화. 4패널이 이미 원래 1e-5 기준을 만족하므로 8/16패널을 무조건 채택하지 않는다. 검증된 source/Time/Native result를 그대로 재사용한다.

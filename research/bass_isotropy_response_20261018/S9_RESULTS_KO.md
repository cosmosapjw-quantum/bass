# S9 실제 Rust history 결과 — 2026-10-20

고정 소스 `4b30957cb008aad8019bb1a673937fc67bd017e8`의 사전등록 여덟 이력을 샌드박스에서 각각 한 번 실행했다. **8/8 완주, 140개의 개별 quality-gate 판정이 모두 통과**했다. 140은 여덟 이력 안의 반복 계약 검사 수이며 140개의 독립 테스트나 물리 모형이 아니다. 기존 S6/S7/S8 이력과 S9 개발·AD 검사는 재실행하지 않았다.

원 결과는 [CAMPAIGN_RETURN](evidence_s9/run_20261020_r1/CAMPAIGN_RETURN.json), 간결한 집계는 [RESULT_SUMMARY](evidence_s9/RESULT_SUMMARY_20261020.json)에 있다. 본 보고서의 과학적 수용 범위는 고정된 manufactured donor와 collisionless cohort의 실제 Rust 적분이다.

최종 그림은 [상태·참조 잔차](evidence_s9/figures_20261020/final/S9_01_trajectories_residuals.png), [고정 gate 대비 오차](evidence_s9/figures_20261020/final/S9_02_fixed_gates.png), [실행량 진단](evidence_s9/figures_20261020/final/S9_03_work_diagnostics.png)이다. [08→07 검수 영수증](evidence_s9/figures_20261020/final/FIGURE_AUDIT08_07.json)은 실제 초기 그림의 겹침을 수정한 뒤 180 mm 폭의 보고용 그림을 승인했다. 원 raw와 28개 그림 입력/source hash를 보존하며, 그림을 만들기 위한 새 적분은 없었다.

## 1. 재개점과 근거

사용자가 지정한 `3694d6e1` 이후의 S6/S7/S8 완료 영수증과 S9 source/preregistration을 GitHub·Dropbox·Google Drive에서 확인했다. 현재 Git tree와 269개 복구 payload blob을 대조하고 과거 버전 19개는 현재 파일 위에 덮어쓰지 않았다. 최신 S9 archive의 SHA256은 `adaa646269168365738bb6c6e7ec67538da0b6109b5d9cb8cac5e4a886a2d9c1`이다. Drive 전체 ZIP/CRC/140 manifest 항목 및 Dropbox provider hash·size·remote manifest를 확인한 뒤 [실제 source gate](evidence_s9/SOURCE_PUBLICATION_GATE.json)를 작성했다.

과거 결과의 자세한 범위는 [재사용 검토](evidence_s9/resume_20261020/science_reuse/S6_S8_REUSE_REVIEW_KO.md)에 있다. 원 S6 refinement 실패38/344, 잡음 위 P4 제약 악화44/238, S8 STRICT_INTERIOR의 inner-P2 precision 실패와 낮은 각도 해상도의 여덟 오차 미달은 보존한다.

## 2. 고정 물리·수치 계약

Non-tilted axisymmetric Bianchi I, signature(-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b), s=dot b, Sigma=sqrt(3)|s|/H를 유지했다. 상태는 h=H/H*, b, y=s/H*, 적분 변수는 x=ln(a/a_ref)다. H*는 고정 역시간 단위이며 h,b,y,x는 무차원이다.

입력은 n=16, b0=.3, y0=.08, donor0=.7, old isotropic=.16, old physical anisotropic=.04, Lambda*=.1, decay_lambda=.7, birth_end=.8, x_end=1.2, K=32다. 기존 S8의153개 primal 출력값은 비교에만 사용했고 미래 birth b(u)를 입력으로 사용하지 않았다. 초기 두 old cohort의 모든 bytes/digest를 보존하며 새 명시적 isotropic birth에만 P24 projection을 적용했다.

실제 API는 pinned VigilODE `a21d573980f66fe02891bd216153443b5352f921`의 `mf_into_ls` GMRES workspace와 `SmallProblem<4>`다. 첫 경로는 analytic JVP와 explicit Ft, 두 번째는 autonomous clock state와 Jacobian의 Ft 열을 사용한다. Birth마다 정확한 endpoint에서 현재 해의 b(u)로 새 cohort를 만들고 immutable bank와 driver/workspace를 새로 시작한다.

P2/P4와 정규화의 최종 기준은 정확한 유리수3/10^15다. 양의 weights·reflection·source frame·고정 REI spectral owner`0e25846433170d0f420c4cda44a0bedbf02cd177`를 유지했다. 여섯 closed history에서 총192개 새 birth record를 검사했다.

## 3. 실제 여덟 이력

| Case | rtol | max abs(h,b,y) reference error | max relative Hamiltonian residual | Accepted steps | 모든 해당 gate |
|---|---:|---:|---:|---:|---|
| closed_mf_into_ls_r0 | 1e-08 | 8.336665e-13 | 2.268381e-12 | 218 | PASS |
| closed_mf_into_ls_r1 | 1e-10 | 8.336665e-13 | 2.268381e-12 | 218 | PASS |
| closed_mf_into_ls_r2 | 1e-12 | 1.432743e-13 | 3.941328e-13 | 305 | PASS |
| flrw_mf_into_ls_fine | 1e-12 | 3.352318e-13 | 7.877560e-13 | 238 | PASS |
| closed_small_clock4_r0 | 1e-08 | 8.359979e-13 | 2.274338e-12 | 218 | PASS |
| closed_small_clock4_r1 | 1e-10 | 8.359979e-13 | 2.274338e-12 | 218 | PASS |
| closed_small_clock4_r2 | 1e-12 | 1.710854e-13 | 4.706398e-13 | 305 | PASS |
| flrw_small_clock4_fine | 1e-12 | 3.681500e-13 | 8.730987e-13 | 232 | PASS |

각 closed history는32번 birth와33개 적분 구간,153개 출력 시각을 가진다. FLRW 대조군은 양의 등방 old stock과 Lambda·dust의 해석해를 별도 synthetic input으로 사용하며 birth는0회다.

전체 최대 Hamiltonian 상대잔차는`2.2743375622205818e-12`(기준1e-11), 독립 complex-step cohort 에너지 항등식 잔차는`2.8503909994791273e-15`(기준1e-11), birth energy jump는`2.1805516491514178e-16`(기준1e-13), 보조 clock 오차는`2.4424906541753444e-15`(기준1e-12)다. donor endpoint 상대오차는 모든 이력에서0으로 기록됐다.

두 fine closed history의 최대 상태 오차는MF`1.4327428132787645e-13`, small-clock`1.7108536809473662e-13`이며 사전등록1e-9를 만족했다. 이는 저장된 고정 S8 수치해와의 비교값이다.

## 4. 허용오차와 실행량 해석

각 solver에서 rtol1e-8과1e-10은 같은 관측 이력과 같은 reported218 accepted/119 output-clipped steps를 보였다. fine rtol1e-12에서는305 accepted/119clipped로 바뀌었다. 출생·요청 출력 endpoint의 step 제한과 허용오차의 관계를 분리해 읽어야 한다. 원 raw에는 모든 내부 step 시각이 없으므로 내부 grid의 bit identity나 이 데이터의 공식 수렴차수는 주장하지 않는다.

개별 closed history의 단회 시간은MF 약.16–.21초, small-clock 약.08–.09초였다. 초기조건·출력 schedule·정확도 기준이 고정된 이 한 실행의 진단값이며 portable speedup 추정이 아니다. 수치기법의 차원과 비용 비교도 이 작은 문제의 실제 범위로 제한한다.

## 5. 현재 환경과 실패 분류

첨부 Rust1.94.1의 rustc/cargo/std만 설치했다. 고정 VigilODE178개 원 파일5,196,962bytes와 Cargo.lock의93개 registry crate checksum을 확인하고 offline `cargo build --locked --bin bass-s9-vigilode`, jobs2를 수행했다. 실제 build exit0, wall144.99973225593567초, fresh binary SHA256`69de3e8739488524cdbe53f9e4bd71f8125717138bf06085b5f51a082060582f`다. 현재 cgroup 제한은8 CPU와8GiB이며 사용자 상한16workers/16GiB보다 작다. 추가 runtime 파일은약1.18GB였다.

전체8case wrapper wall은`1.876594`초다. `/proc` namespace의 가시성 때문에 sampled RSS는 보이는 process의 하한만 제공하며 compiler 또는 campaign의 실제 peakRSS는 미검증으로 기록했다. Shared cgroup lifetime peak를 이번 작업의 peak로 사용하지 않았다. 측정을 위해 scientific history나 compile을 재실행하지 않았다.

기본 sandbox HTTPS의권한 실패는 승인된 읽기 전용 network 경로로 해결했다. 최초 자원 wrapper의psutil부재는`PACKAGE_MISSING`이며 compile/history 이전 실패였다. 표준 라이브러리 경로로 교정했고 원 로그를 보존했다. 이번 scientific8case의 수치·feasibility·solver 실패는0건이다. 기존 S6/S8 실패는 그 원 범위에 계속 남는다.

## 6. 실제 변경과 후속 물리 의무

S9의13개 고정 source와3개 input, balance_p24.rs는 실행 전후 동일하다. 신규 코드는 저장된 raw를 그리는 보고 helper와 제한 실행/독립 관측 도구다. rank1_certificate.py의 docstring은 binary64 polynomial equality가 exact dyadic arithmetic으로 결정 가능하고 algebraic provenance의 역추정이 별개라는 표현으로 교정했다. 모듈 docstring을 제외한 실행 AST는 동일하다.

다음 물리 연결은 공급부(U_d,p_d)와 radiation에 같은Q를 반대 부호로 넣는 것이다. kappa_g=8piG/(3c²), L0=Lambda c²/3일 때 C=H²−s²−kappa_g(U_d+U_gamma)−L0는 연속식과 Raychaudhuri 아래 Cdot=−2HC를 만족한다. Native per-H rate q_H는 proper n_H와 결합해Q=n_H q_H로 바뀌며 eV→J와 시간 Jacobian을 한 번만 적용해야 한다. 실제 MD14의 fesc·spectral band·시간 convention과 에너지를 잃는 물질의 물리적 상태/압력은 다음 source 계약에서 고정한다.

P6 constraint, 넓은 strain/support의 continuum 보증, 실제MD14 native Einstein coupling, 진화하는 reactive/spectral history는 남은 별도 의무다. 현재8개 이력의 재현을 NCP에 다시 요구하지 않는다. 새 native scope가 NCP를 필요로 하면 먼저 source·input·gate와 작은 검증을 완성한 후 compile/작은 호환수정/실행만 넘긴다.

## 7. 실제 결과 독립 검토와 종료 상태

**PHYS-MATH에 이어 PHYS-MATH-CODE 검토를 완료했고 두 판정은 `PASS_SCOPED`다.** 현재 영수증은 [DUAL_REVIEW_RECEIPT](evidence_s9/resume_20261020/science_review/DUAL_REVIEW_RECEIPT.json), 자세한 검토는 [INDEPENDENT_S9_ACTUAL_REVIEW_KO](evidence_s9/resume_20261020/science_review/INDEPENDENT_S9_ACTUAL_REVIEW_KO.md), 직접 재계산값과 파일 identity는 [INDEPENDENT_RECOMPUTATION](evidence_s9/resume_20261020/science_review/INDEPENDENT_RECOMPUTATION.json)에 있다. 기존 development review와 그 실패 기록은 별도 과거 근거로 보존했다.

새 적분이나 기존 `analyze.assess` 호출 없이 저장된 **1,224개 관측 행**을 80자리 Decimal inventory로 재계산했고, **192/192개 birth certificate**를 binary64 값의 정확한 Fraction으로 대조했다. 이는 여섯 closed history의 32회 출생 각각에 대한 certificate이며 서로 다른 192개 angular support를 뜻하지 않는다. 최대 exact birth moment의 수치 표현은 `9.9692153425314e-16`, 최대 정규화 오차는 `1.1102230246251565e-16`로 원 `3/10^15` 기준 안에 있다. 기존 두 old stock의 배열과 digest, 새 birth의 고정 digest, 실제 event state에서의 birth geometry, 오른쪽 bank의 event 출력, 각 closed history의 33개 fresh segment와 153개 출력 시각을 확인했다.

| 독립 재계산 항목 | 최대값 |
|---|---:|
| Hamiltonian 상대잔차, Decimal inventory | `2.2743189570736747e-12` |
| 직접 에너지 미분과 native 에너지·압력의 상대잔차 | `9.364748127632878e-16` |
| Event energy 상대잔차, Decimal inventory | `3.66654245463207e-17` |
| Event RHS/J/F_x와 독립 구성의 scaled 차이 | `2.356231404247763e-16` |
| Native E와 Decimal inventory의 상대차 | `2.3411870319082195e-16` |
| Exact birth moment의 최대 절댓값, 수치 표현 | `9.9692153425314e-16` |
| 보조 clock의 raw 최대 절대오차 | `2.4424906541753444e-15` |

제3절의 원 native/observer binary64 최대값과 이 표의 독립 Decimal 최대값을 분리해서 보존했다. 원 reference 및 analytic FLRW의 binary64 오차값은 정확히 재현됐다. Decimal 해석 FLRW 최대값은 MF `3.3522885227577977e-13`, small-clock `3.6813467598394824e-13`이며 원 binary64 표현과의 끝자리 차이를 수렴 개선으로 해석하지 않는다. Decimal `Cprime+2C`의 scaled 잔차 `1.4712611557081695e-79`는 식의 산술 일치 검산값이다.

r0/r1의 저장된 observations·segments·events·final cohorts는 각 arm 안에서 정확히 동일하다. MF JVP/F_x는 coarse `10246/218`, fine `14335/305`회이며 small-clock의 Jacobian build/direct factorization은 coarse 각각218회, fine 각각305회다. 이는 출력 endpoint 제한과 coarse tolerance plateau의 설명을 지지하며 미출력 내부 step 전체의 동일성이나 공식 수렴차수를 증명하지 않는다.

현재 **S9의 등록된 여덟 이력에 대한 과학 범위와 R8/C9 독립 판정은 완료**다. **R10/C10은 새 결과 게시와 Dropbox·Google Drive의 이중 백업/readback을 진행 중**이다. 실행 전 source/preregistration의 Git·양쪽 cloud readback 완료 기록은 유지한다. 이 보고서는 새 결과 commit 또는 새 cloud backup이 이미 성공했다고 기록하지 않는다. 후속 실제 게시 상태는 [RESULT_SUMMARY](evidence_s9/RESULT_SUMMARY_20261020.json), [DAG](DAG.json), [PUBLICATION_CLOSEOUT](PUBLICATION_CLOSEOUT.json)에서 해당 배송 증거와 함께 갱신한다.


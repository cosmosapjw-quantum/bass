# ACCEL03 연구 결과: 저장 sweep의 이식 가능한 분석과 massive 응력 응답

**판정: PASS_SCOPED_PORTABLE_ANALYSIS_MASSIVE_RESPONSE_AND_NCP_NUMERICAL_EQUIVALENCE.** 완료된 warm729와 새로 도착한 NCP5 실행을 재사용해, 이론 유도·가벼운 샌드박스 검증·코드 구현·preliminary plot·독립 검토를 완료했다. 이 문서가 속한 단계 C의 실제 게시와 백업 상태는 `delivery/`의 후속 영수증으로 연결한다.

- BASS: https://github.com/cosmosapjw-quantum/bass/pull/179
- REI: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/217
- Branch: `research/rei-sigma-pi-sweep-analysis-20261021`
- Directory: `research/rei_sigma_pi_sweep_analysis_20261021`
- 이론/코딩 각 10단계의 증거와 다음 전이는 `DAG.json`, `LOOP_RECORD.json`에 있다.

## 1. 최신 반환을 먼저 수용한 결과

앞선 ACCEL02 인계에서 대기하던 NCP 실행이 이번 조사 전에 완료되어 있었다. 2026-10-21 21:56:42 KST에 끝난 실제 target 실행은 g++13.3.0으로 1회 build하고, 제공된 5사례를 각 2-step으로 실행했다. 5/5 jobs, 원래 8개 gate × 5사례 = 40/40 gate가 통과했다. 수치 thread는 1, 동시 worker 상한은 2였다. 기본 729 계획은 `REUSED_ALL`, pending0, jobs0, launched0이었다.

기존 NCP 반환 문서의 일부 오래된 ‘미실행/미수용’ 문장을 현재 상태로 반복하지 않았다. 새 실제 실행과 이번 독립 수치 판정을 후속 사건으로 기록했다. 원래 문서·실패 기록·source pin은 보존했다. 최초 `python` 명령 부재(exit127)는 `/usr/bin/python3`로 복구된 환경 사건이며, 성공 실행 기록과 함께 남아 있다.

| 권위 | 실제 확인한 값 |
|---|---|
| BASS 실행 source pin | `7fe0e25a28c0e48110c522378e203ffb934cc504` |
| REI 실행 source pin | `231df3ab717dbc112f63b77953f64def08e9bcb5` |
| NCP backend/source ID | `aed4c55a61df37d97d8c0aa309b7875e5eb3629abbd284fe04faf23cb261115d` |
| 반환 archive | `BASS_REI_ACCEL02_NCP_TARGET_20261021_ad92f4207a68.zip` |
| 반환 크기 / SHA256 | 6,003,218 B / `ad92f4207a6845a0326a095cb904792b6d34bf0654f7148fe3c530b47f5e2817` |
| intake 검증 | 실제 1회 GET, size/SHA256/Dropbox block hash/ZIP CRC, 47개 source 결속 확인 |

원 Git commit→tree 연결과 선택한 7개 source blob을 확인했다. 실제 NCP case와 ACCEL02 원 reference를 동일한 고정 기준으로 비교했고, 독립 검토자가 저장 raw에서 최대 차이를 다시 계산했다. 새 solver 실행은 필요하지 않았다.

| 비교량 | 관측 최대 차이 | 기존 허용값 |
|---|---:|---:|
| signed shear | 2.0668852438742e-21 | 5e-14 |
| signed matter stress | 4.119968255444917e-18 | 5e-14 |
| signed radiation stress | 1.0842021724855044e-19 | 5e-14 |
| signed total stress | 4.1384176918272996e-18 | 5e-14 |
| H 상대 차이 | 1.1128439998013552e-16 | 5e-13 |
| Tgas 상대 차이 | 0 | 5e-12 |
| ionization fraction 차이 | 0 | 5e-13 |
| normalized total work | 1.2713960895138061e-21 | 5e-14 |

저장 JSON의 initial+history+final 대조는 20행이다. final이 마지막 history와 중복되므로 실제 서로 다른 저장 시점은 15개다. 새 history CSV에는 15개만 넣었다. 이는 수치 허용오차 내 일치 판정이며 target와 reference의 모든 byte가 같다는 주장은 아니다. 근거: `intake/backups/NCP_TARGET_STORED_CHECK.json`, `evidence/INDEPENDENT_REVIEW.json`.

## 2. 다른 브랜치·저장소·백업과의 관계

연결된 네 관련 저장소의 branch pagination에서 876개 ref를 조사했다. 이전 871개와 비교하면 동일870·변경1·추가5·삭제0이다. 추가에는 직전 조사 뒤 생긴 우리 ACCEL02 두 branch도 포함된다. 이는 해당 광고 ref의 목록 전체를 비교한 결과이며 모든 ref의 모든 파일을 읽었다는 뜻은 아니다. 관련 변경의 원문과 source 결속을 선별해서 확인했다.

| 계열 | 새로 확인한 결과 | ACCEL03에서의 사용 |
|---|---|---|
| REI PR199 | 175 component grid, 237개 z20→2 history, D8의 저장 sample sign-change bracket 완료 | PR147 collisionless/full-Frobenius 비교로 보존; warm 데이터 행과 합치지 않음 |
| BASS_CR PR93 / C21N | 125개 기존 trajectory 재사용, A와 무관한 momentum geometry 준비, massive 응력 미분과 이상적 상쇄 곡률 | 선행 project 유도·준비 재사용 방식에 명시적으로 귀속; C15 radiation 예측으로 이식하지 않음 |
| VigilODE | 별도 manufactured 문제의 NCP 반환, production HOLD 유지 | 동향과 source만 기록; C15 가속 성능 자료로 사용하지 않음 |
| Dropbox | 관련 두 폴더의 전체 직접 목록과 신규 반환 객체 | 실제 NCP archive를 내려받아 수용; 나머지 새 계열은 해당 관측 수준으로 표시 |

Personal Context의 실제 응답은 `Personal context is unavailable for this conversation.`이었다. 따라서 접근할 수 없는 다른 대화에 새 결과가 없다고 결론내리지 않았다. Drive 검색의 반환0 역시 계정 전체 부재를 의미하지 않는다. 정확한 조사 범위·cutoff·source 위치는 `intake/git_conversation/LATEST_DELTA.json`, `intake/backups/BACKUP_DELTA.json`, `CROSSLINEAGE_REUSE.md`에 있다.

## 3. 물리 규약과 데이터 해석

범위는 non-tilted LRS Bianchi I의 warm conditional C15 pilot, a=0.1999→0.2다. 원래 L=8, source grid8×8, massive fraction0.1, mass/T=30과 matter/radiation의 독립 P2 seed를 유지한다. 이번 코드는 solver·radiation collision/emission/UV closure를 바꾸지 않는다.

기존 half-contraction norm을 유지한다. LRS에서 sigma=diag(-s,-s,2s), 각 성분의 pressure difference를 D_X=p_parallel−p_perpendicular라 두면 pi_X=diag(-D_X/3,-D_X/3,2D_X/3)다. proper-time Hubble H_t와 kappa_t=8 pi G/c²를 쓸 때 signed 좌표는 다음과 같다.

\[\widehat\Sigma=\sqrt3\,s/H_t,\qquad \widehat\Pi_X=\kappa_t D_X/(\sqrt3 H_t^2).\]

\[\Sigma=|\widehat\Sigma|,\quad \Pi_X=|\widehat\Pi_X|,\quad \Pi_{\rm total}=|\widehat\Pi_m+\widehat\Pi_r|.\]

기하학적 H=H_t/c와 kappa=8 pi G/c⁴를 함께 사용하면 같은 식이다. Full Frobenius 규약의 Sigma/Pi는 이 half-contraction 값의 sqrt(2)배다. 따라서 사용자가 |tensor|라고 쓴 좌표를 해석할 때 이 규약을 함께 명시해야 한다. 성분 norm을 더한 값과 total tensor의 norm은 다르다. 응력의 signed 합을 먼저 취한다.

shear work는 sigma_ab pi_X^ab=2sD_X이며, kappa_t/H_t³로 정규화하면 2 widehatSigma widehatPi_X다. 원래 saved scalar와 norm/work의 중복 표현을 보존하고, 성분 규모를 기준으로 산술 일관성을 검사했다.

## 4. 실제 유도: massive 응력의 두 국소 응답

물리 energy는 E_phys=sqrt(m²c⁴+c²p²), w=v²/c²=c²p²/E_phys²다. 고정한 초기 k_B T scale로 나눈 원 owner의 계산 변수를 사용하므로 새 자연단위 가정을 도입하지 않는다. W는 comoving momentum label에 고정된 quadrature/distribution weight다.

\[x=\ln(a/a_0),\quad r=e^{-x},\quad u=\mu^2,\quad R^2=e^{2b}(1-u)+e^{-4b}u,\]
\[t=e^{-4b}u/R^2,\quad h=(3t-1)/2,\quad \bar p^2=r^2\bar q^2R^2,\quad E=\sqrt{\bar m^2+\bar p^2},\quad w=\bar p^2/E^2.\]

\[J_2=r^3\sum W Ewh,\qquad J_4=r^3\sum W Ew^2h.\]

x 미분에서는 d_x(Ew)=(-2+w)Ew이고 h는 고정이다. r³ measure의 미분까지 합치면 유한 quadrature 합 자체에 대해

\[\boxed{\partial_xJ_2=-5J_2+J_4}\]

를 얻는다. b 미분에서는 d_b log R²=-4h, d_b(Ew)=-2(2-w)hEw, d_b h=-9t(1-t)이므로

\[\boxed{\partial_bJ_2=-G},\quad G=r^3\sum WEw\{2(2-w)h^2+9t(1-t)\}\ge0.\]

W≥0, 0≤w,t≤1에서 G의 각 항은 비음수가 된다. xdot=H, bdot=s인 owner의 시간 변수에서는

\[\dot J_2=H(-5J_2+J_4)-sG.\]

이 결과는 미분과 무한적분의 교환을 가정한 근사 closure가 아니라, 고정한 유한 가중합을 직접 미분한 항등식이다. 수치 구현의 정확도와 물리 모델의 타당성·전역 오차는 별도로 판단한다.

b=0의 separable 1+alpha_m P2 분포에서는 각도 적분이 2alpha_m/5다. 비영 anisotropy에서 J4/J2는 radial Ew weight로 평균한 w이므로 0과1 사이에 있다. massless limit는 J4=J2여서 fixed-b 응력이 a^-4로, nonrelativistic leading term은 a^-5로 변한다.

초기 shear가0이고 비교 성분이 collisionless massless이며 D_r=-D_m인 이상적 경우에는 d_x(D_m+D_r)=(eta−1)D_m, eta=D4/D_m을 얻는다. 서로 다른 redshift 응답이 상쇄를 풀 수 있다는 설명이다. 실제 warm C15 radiation의 전체 기울기·곡률은 collision/emission/UV 항도 포함하므로 이 비교식을 그대로 적용하지 않는다.

C21N은 이미 관련 mass-shell 응답과 S''(0)=−(1−beta_m)P_m(0)을 유도했다. 이번 단위는 그 선행 결과에 귀속하면서 C15 massive finite-sum의 두 partial derivative를 사용 가능한 진단 코드로 연결했다. CLASS IV의 velocity-weighted higher moment는 J4 표현의 문헌 근거로 참고했다. 해당 논문의 perturbative fluid closure를 C15에 복사하지 않았다.

Wolfram의 실제 계산은 두 per-node derivative residual을 모두 정확히0으로 단순화했고, 양의 정의역에서 G bracket이 음수인 영역을 False로 반환했다. SciSpace와 Exa의 실제 검색, 원전 URL, 채택 범위는 `evidence/SOURCES.json`에 있다. 상세 대수는 `THEORY.md`, CAS 원 입력/출력은 `evidence/WOLFRAM_RESPONSE.json`이다.

## 5. 상쇄 진단과 수치 조건

p=widehatPi_m, r=widehatPi_r, A=|p|+|r|에 대해 q=|p+r|/A는 남은 응력의 성분 대비 비율이고, kappa_sum=A/|p+r|=1/q는 signed 합의 조건수다. A>0에서 q는0과1 사이에 있다. 각 성분 상대 오차가 eps 이하일 때 total의 절대 오차는 eps A 이하이고, total이 비영일 때 상대 오차 한계는 eps kappa_sum이다. 이것은 조건부 산술 bound이며 측정한 solver 오차가 아니다.

A=0이면 비율/조건수를 null로 두고 `ZERO_COMPONENT_SCALE`로 표시한다. 비영 성분이 정확히 상쇄되면 q=0, 발산 조건수는 null와 `EXACT_CANCELLATION`으로 표현한다. 원래 owner의 `cancellation_fraction`은 별도 필드로 유지한다. nominal-zero 요청에서 남는 극소 FP 잔차는 raw로 보존하며, 그림의 중심점을 물리적 상쇄 비율로 해석하지 않도록 표시했다.

합·norm·work 검사에 near-zero total 상대오차를 사용하지 않았다. 관련 성분 규모에 128 eps64를 곱한 고정 기준을 사용했고, 모든 규모가0이면 exact zero를 요구했다. 관측 최대 residual/scale은 NCP2.528508284916226e-16, archived endpoints3.8369107064748666e-16으로 기준 내였다.

## 6. 저장 결과가 보여 주는 preliminary 결과

NCP의 opposite-stress case `native_check_4`는 requested signedSigma=0, signedPi_m=4e-4, signedPi_r=−4e-4다. 마지막 저장값은 다음과 같다.

| a=0.2의 관측량 | NCP 2-step 저장값 |
|---|---:|
| signed matter stress | 3.9959676595999774e-4 |
| signed radiation stress | −3.997885349389876e-4 |
| signed total stress | −1.9176897898990935e-7 |
| signed shear | −4.7955100933306635e-11 |
| 동일 cohort의 zero-stress control을 뺀 shear | −4.795510093313524e-11 |
| residual fraction q | 2.3989555321347894e-4 |
| sum condition number | 4168.480768420568 |

matter/radiation의 큰 signed 응력은 거의 상쇄되지만 두 성분의 변화가 같지 않아 작은 total과 shear가 남는다. 같은 nominal 좌표의 기존 warm64-step `split_0079`에서는 total=−1.9176362919464883e-7, shear=−4.795410954946239e-11이다. 이 두 관측을 수렴 입증으로 바꾸지 않는다. NCP backend의 numerical equivalence 판정은 같은 2-step 원 reference에 대한 위 고정 기준으로 수행했다.

matter만1e-5인 NCP 사례의 최종 shear는 4.996824104575486e-9, radiation만1e-5인 사례는 4.9980229820994064e-9다. 각 응답은 동일 requested initial shear, source/backend/toolchain, nsteps, context, 시작·끝 구간을 가진 control과만 비교한다. 적합한 control이 없으면 null/`MISSING_CONTROL`이며 다른 grid point를 빌리지 않는다.

그림은 저장된 실제 값만 사용한다.

- `results/ncp5/plots/actual_samples_4ff69a0d5fef.png` 및 PDF: 5case×3실제시점, matter/radiation/total/shear history, matched-control shear, opposite-stress q. 68개 plotted point, 204개 scalar 대조.
- `results/baseline729/plots/endpoint_slice_caed0ccd4a58.png` 및 PDF: 정확히 requested signedSigma=0인81좌표, 4개 endpoint scatter panel. 324개 plotted point, 1296개 scalar 대조.
- 각 그림 폴더의 `source_points.csv`, `plot_provenance.json`이 source CSV의 행·필드·값·cohort·hash를 연결한다.

원729의 47,385행 history는 원 archive에 그대로 있다. 이번 endpoint projection은 그 history를 불러오지 않았으므로 history CSV0행이다. 보간·누락 셀 채움·history 재구성은 하지 않았다. 실제 PNG를 구현 담당자, controller, 독립 검토자가 열어 확인했다. PDF 파일은 출력했지만 별도의 print/raster 검토를 수행했다고 주장하지 않는다.

## 7. 코드 변경과 가벼운 검증

| 새 코드 | 구체적 역할 |
|---|---|
| `aggregate.py` | full plan을 예상 사례 집합으로 삼아 completed reuse / pending success / missing을 분리하고 이식 가능한 저장 결과를 읽음 |
| `diagnostics.py` | initialized masked NumPy division, signed 합의 조건, norm/work 재구성, 정확한 cohort control 비교 |
| `plot_sweep.py` | 실제 nsteps·cohort·좌표에 맞는 그림과 source-point table 생성 |
| `moment_response.py` | 원 quadrature 배열에서 J0/J2/J4/G와 두 analytic response 계산; owner/native/solver import 없음 |
| `verify_moment_response.py` | 고정27점의 five-point derivative 대조와 원 입력/stencil 보존 |
| `test_aggregate.py` | 12개 focused saved-data 검증 |

원 fixed729/64step aggregation 가정을 새 경로에서 제거했다. manifest는 pending jobs만 담을 수 있으므로 전체 denominator로 쓰지 않는다. 완료 case의 이름이 바뀌어도 science ID로 pinned CSV를 찾고 요청 label을 보존한다. 불완전 반환은 `PARTIAL`과 명시적 missing ID가 된다. 원 source/science/input, step count, gate, finite row가 잘못되거나 중복 body가 충돌하면 입력 또는 물리 diagnosis를 남긴다.

분석 host의 Python/NumPy가 target와 동일해야 한다고 요구하지 않는다. 저장 plan·manifest·source·toolchain의 상호 결속을 검사한다. 성공 executor receipt의 result hash와 상대 경로를 재사용하며, 이미 저장된 결과를 읽는 경로에서 PreparedContext·native library·compiler·solver를 실행하지 않는다.

| 제한된 검증 | 실제 결과 |
|---|---|
| relocated NCP fixture | 예상5, 성공5, 누락0, history15 |
| archived completion-only plan | 재사용729, pending0, history0; 모든 endpoint 원 scalar/float 보존 |
| 동일 scientific body의 first/second scope | case1, 중복1, history3 |
| focused mutations / aliases / control / cancellation | 12 tests PASS |
| massive response | alpha=[−0.9,0,1.8], x=[0,ln(.2/.1999),.1], b=[−.1,0,.1], 27점 |
| moment quadrature / stencil | 기존96×32, mass/T=30, h=2^-15, 216 stencil evaluations |
| x derivative residual/J0 | 최대1.0715866992998556e-13 ≤2e-9 |
| b derivative residual/J0 | 최대3.6901037780978584e-14 ≤2e-9 |
| 최소 G | 0.012992574995213354, 비음수 기준 통과 |

처음 발생한 NumPy boolean JSON serialization 오류의 stderr를 보존했고, 고정 산술 계수를 Python float로 표현해 수정했다. 허용오차·수식·입력은 바뀌지 않았다. 원 test와 moment matrix를 다시 전부 돌리는 추가 review loop는 만들지 않았다. 독립 검토자는 저장 stencil·CSV·hash를 직접 재계산해 수용했다.

전체 ACCEL03에서 새 ODE0, build0, benchmark0이다. theory/contract는 controller, 구현은 지정된 lower-tier executor, 독립 검토는 fresh reviewer가 맡았다. requested model과 telemetry가 노출되지 않은 actual runtime identity(null)는 구분해 기록했다.

## 8. 최적화 기여와 NCP 자원 운용

기존 ACCEL01의 완료 science-ID 재사용·prepared context·case 단위 재개, ACCEL02의 반사대칭96×16 평가와 fused moments/Neumaier 누적을 그대로 이어 쓴다. ACCEL02는 원96×32 quadrature의 대칭 쌍을 사용한 것이며 새 quadrature나 solver closure가 아니다. 이번 ACCEL03은 완료 데이터를 host 이식 가능하게 집계하고 즉시 그림으로 연결해 새 계산 없이 산출물을 확보하는 경로를 완성했다. array kernel에는 기존 NumPy를, actual-coordinate figure에는 Matplotlib를 재사용했다.

가속비·RSS 절감률·64-core scaling은 측정하지 않았다. 구조적으로 중복된 준비/적분/후처리 요구를 줄인 기여와, 실제 측정된 성능 수치는 구분한다. 사용자가 원하지 않은 상세 성능 캠페인은 수행하지 않았다.

| 자원 | 관측 범위 | 값 |
|---|---|---|
| 현재 연구 sandbox | 2026-10-21 22:13:50 KST | CPU quota8, affinity9, cgroup RAM8GiB, 당시 사용약0.69GiB |
| 완료 pilot 실행 | 기존 원 기록 | 8CPU /8GiB |
| NCP target run | 2026-10-21 21:56:39–42 KST의 저장 관측 | affinity0–63, 총135050526720 B≈125.78GiB, MemAvailable약80.20→80.14GiB |
| NCP 요청 profile | 설정 상한 | 64CPU /128GiB |
| 현재 live NCP 여유 | 이번 sandbox에서 직접 관측하지 않음 | null; 다음 실제 실행 시 재관측 |

기존 `shared_executor.py --profile ncp --max-workers 64`는 생산용 상한이다. 실제 실행은 affinity/cgroup quota/관측 idle CPU/메모리 여유와 pending 수에 의해 제한된다. 각 수치 library thread는1이다. 다른 세션의 프로세스를 종료하지 않고 가용 범위에서 새 case를 배치한다. 현재 계획의 pending0에서64worker를 만들 이유는 없다. 실제 새 case가 주어지면 pending만 compile/prepare/execute하고 새 aggregator와 plotter로 연결한다.

## 9. 단계별 게시·백업·DAG와 인계

| 단계 | 내용 | 상태의 권위 |
|---|---|---|
| A | 최신 반환 조사, 고정 계약, 대수/CAS, 초기DAG | `delivery/STAGEA_PUBLICATION.json`, `delivery/STAGEA_BACKUP.json` |
| B | 구현, bounded raw, portable inputs, 실제 그림 | `delivery/STAGEB_PUBLICATION.json`, `delivery/STAGEB_BACKUP.json` |
| C | 독립 검토, 수용 판정, 본 보고서, handoff, 네 lane 복구본 | `delivery/STAGEC_PUBLICATION.json`, `delivery/STAGEC_BACKUP_VERIFIED.json`, 최종 closeout receipt |

단계 A/B의 provider object·size ACK와 단계 C의 실제 전체 GET byte 검증을 구분한다. 불변 ZIP은 자신의 provider ACK보다 먼저 생성되므로, 실제 후속 ACK는 뒤따르는 Git commit에 남긴다. 자기 hash를 넣기 위해 ZIP을 반복 재생성하지 않는다. 실행 code pin과 문서/receipt closeout commit도 별도로 기록한다.

`CODEX_HANDOFF.md`는 기존 저장소의 고정 객체에서 네 lane을 내보내는 명령과 saved-data 분석 명령을 제공한다. NCP5 실행은 이미 완료·수용됐으므로 다시 지시하지 않는다. `NEXT_THREAD_HANDOFF.md`는 다음 대화에서 최신 반환부터 확인하고 이번 완료 증거를 재사용하도록 하는 복사 가능한 prompt다.

이번 단위의 종료 조건은 충족됐다. 다음 물리 범위는 사용자가 지정하는 새 입력·구간·질문에 맞춰 고정한다. 전체 EoR, 일반 non-LRS, full Q^a closure, 전역 수렴/오차 bound는 이번 판정에 포함되지 않는다.

## 근거

- [고정 계약](FROZEN_CONTRACT.md), [유도](THEORY.md), [선행 결과 귀속](CROSSLINEAGE_REUSE.md).
- [독립 검토](evidence/INDEPENDENT_REVIEW.md), [원 NCP 대조](intake/backups/NCP_TARGET_STORED_CHECK.json).
- [집계 결과](results/ncp5/summary.json), [archived729 결과](results/baseline729/summary.json), [moment raw](evidence/MOMENT_RESPONSE_RAW.json).
- Lesgourgues & Tram, CLASS IV, arXiv:1104.2935: https://arxiv.org/pdf/1104.2935 (sections2.1,3.3,3.4; 채택 범위는 SOURCES.json).
- NumPy divide: https://numpy.org/doc/stable/reference/generated/numpy.divide.html ; Matplotlib scatter: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.scatter.html .

## 게시된 실행 코드 고정점

Stage B 코드와 그림은 실제로 다음 commit에 게시됐다. 후속 보고서/receipt commit은 이 실행 코드를 바꾸지 않는다.

- cosmosapjw-quantum/bass: `b0ea16c9172c8b1553cbdb35cb03460160db1412` (tree `7572f7a4bff60e17c5850a26b1bf4897ab785dc4`).
- cosmosapjw-quantum/rei_bianchi: `39ae7c843ea2d1adf580aff44aebfdedea7e33aa` (tree `a3ca4cc80d3fbec68c78497cdaab9a9a8313a186`).

복사 가능한 실제 export/분석 명령은 `CODEX_HANDOFF.md`를 따른다. 완료된 NCP5를 다시 실행할 전제는 없다.


## 최종 전달 상태

ACCEL03은 `SCOPED_COMPLETE`다. Stage C 과학·인계 본문은 BASS
`9074a788ca6f26384356c6fa57a695dc6f307fc6`, REI
`e4defc4f303203232223ecabe004252761145844`에 실제 게시됐다. 실행 코드의
Stage B pin은 BASS `b0ea16c9172c8b1553cbdb35cb03460160db1412`, REI
`39ae7c843ea2d1adf580aff44aebfdedea7e33aa`로 유지한다.

7,286,437-byte Stage C ZIP은 한 번의 전체 GET으로 SHA256
`049af2b058d83c997c03c092e6ec90ab0f3411c45118719b75bf3f7dc27a04e4`,
size·Dropbox block hash·ZIP CRC·379개 exact member를 확인했다. Stage A/B는
provider ACK·size 확인이며, 전체 GET 검증은 Stage C에 한 번 수행했다. 실제
영수증은 `delivery/FINAL_PUBLICATION.json`과 `STAGEC_BACKUP_VERIFIED.json`이다.

불변 ZIP은 자체 ACK보다 먼저 만들어졌고 최종 영수증은 뒤따르는 Git commit에
있다. 최종 영수증의 게시점은 이 파일을 포함하는 Git commit으로 확인한다.
자기 commit SHA를 본문에 재귀적으로 넣거나 ZIP을 다시 만들지 않는다.
`STAGEC_PACKAGE.json`의 생성 당시 상태는 그대로 보존한 역사적 helper 영수증이다.

NCP5 실행과 그 과학 판정은 이미 완료됐다. ACCEL03 안에 추가 실행·과학 검증은
필요 없다. 이후에는 새 사용자 범위 또는 실제 새 반환 자료의 증거를 먼저 읽고
필요한 최소 작업을 정한다. 완료된 독립 검토나 원 sweep을 반복하지 않는다.

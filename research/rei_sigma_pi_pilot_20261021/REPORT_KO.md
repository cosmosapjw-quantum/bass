# REI: 물질·복사를 독립 설정한 729-case 예비 sweep 완료

2026-10-21 UTC · physmath research loop · 실제 결과와 출처를 보존한 최종 보고

## 1. 완료한 결과

사용자의 추가 지시인 **물질과 복사의 이방응력 분리**를 초기조건에 구현하고,
non-tilted **LRS Bianchi I**의 signed (Sigma, Pi_m, Pi_r) 9×9×9 sweep을
실제로 완료했다. 729개 경우, 243개 독립 group, 초기점과 64 step을 포함한
47,385개 저장 상태가 있다. 고유 receipt 243개가 모두 PASS이며 저장된
5,832개 numerical gate에 실패가 없다. 먼저 수행한 81-case 공통-alpha
pilot도 비교 자료로 보존했다.

물리 범위는 **warm a=0.1999→0.2, z=4.00250125→4**의 조건부 예비 계산이다.
Cold full-EoR 이력, 일반 non-LRS Bianchi I, 전체 stellar/emitter/escape Qᵃ
closure 또는 전역 수렴의 완료를 뜻하지 않는다.

핵심 결과는 초기 물질·복사 응력이 상쇄되어도 이후 상쇄가 유지되지 않는다는
것이다. 초기 signed Sigma=0, Pi_m=+4e-4, Pi_r=-4e-4에서는 최종 signed
Pi_total=-1.91763629195e-7, Sigma=-4.79541095495e-11이다. 성분별 norm의
초기 합은 약 8e-4지만 총 텐서 norm은 roundoff 수준이었다.

실행 물리 owner는 REI PR141 `80825585f9fe31d2ee0d5af545ada3fa1f52be72`,
729-case 실행 adapter source는 BASS `82372ed8db68085868603d4267a630ed9cde6abb`다.
원본 owner bytes는 `vendor/rei_c15/`에 보존했다. 계산 후 plot 표현 변경은
별도 figure provenance로 추적하며 solver/contract의 binding은 바꾸지 않았다.

주요 결과는 `results/split729/aggregate/`에 있다.

- `sigma_pi_split_slices.png/.pdf`: 독립 물질·복사 축의 전단 응답과 초기 상쇄면.
- `sigma_pi_split_components.png/.pdf`: 성분별 변화와 상쇄가 풀리는 실제 이력.
- `cases.csv`: 729개 초기값·최종값·부호·norm·work·수치 검사.
- `history.csv`: 초기점을 포함한 47,385개 실제 상태.
- `METRICS.json`, `summary.json`, figure provenance: 수치 요약 및 source/input/toolchain identity.

독립 검토는 `physics/SPLIT_RESULT_REVIEW.json`, 실행 관측은
`evidence/SPLIT_EXECUTION_OBSERVATIONS.json`, 복사 가능한 후속 지시는
`CODEX_HANDOFF.md`와 `NEXT_THREAD_HANDOFF.md`에 있다. 게시 경로는
[BASS PR176](https://github.com/cosmosapjw-quantum/bass/pull/176)과
[rei_bianchi PR213](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/213)이다.
두 PR은 draft이고 merge하지 않았다. 최종 head/tree와 백업 확인 수준은
`delivery/`의 별도 receipt를 따른다.

## 2. 물질·복사의 정의와 정규화

### 2.1 species를 분리하는 기준

\[
D_m=P_{m,\parallel}-P_{m,\perp}=\texttt{Pi\_massive},
\qquad D_r=\texttt{Pi\_gamma}+\texttt{Pi\_nu}+\texttt{Pi\_UV}.
\]

물질 축은 기존 C15의 **collisionless massive nonbaryonic Vlasov 성분**이다.
H/He baryonic gas와 남은 cold matter는 현재 closure에서 등방이므로 이방응력은
0이다. 복사 축은 photon, owner의 **massless neutrino**, 실제 추적하는 ionizing
UV를 포함한다. UV는 초기에는 비어 있지만 이후에는 매 실제 상태에서 복사에
포함한다. Massive fraction=0.1, m/T=30을 유지했다. 일반 baryon viscosity나
새 massive neutrino 모델을 추가한 것은 아니다.

### 2.2 norm과 signed 좌표

\[
a_\perp=a e^{-b},\quad a_\parallel=a e^{2b},\quad s=\dot b,
\quad \sigma^a{}_b=\mathrm{diag}(-s,-s,2s),
\]
\[
\pi_A{}^a{}_b=\mathrm{diag}(-D_A/3,-D_A/3,2D_A/3),\quad A=m,r.
\]

기본값은 half-contraction norm이다.

\[
\Sigma_h=\frac{\sqrt{\sigma_{ab}\sigma^{ab}/2}}H=\sqrt3\frac{|s|}H,
\qquad
\Pi_{A,h}=\frac{\kappa_t\sqrt{\pi_{A,ab}\pi_A^{ab}/2}}{H^2}
=\frac{\kappa_t|D_A|}{\sqrt3H^2}.
\]

SI 압력/에너지밀도는 Pa=J/m³, H는 s⁻¹이다.
\(\kappa_t=8\pi G/c^2=3\,\mathrm{C15.KAPPA}\)이며, Einstein equation에서
\(\kappa=8\pi G/c^4\)라고 쓸 때는 proper-time 식에 \(\kappa c^2\)가 들어간다.
Frobenius norm을 원하면 각 성분과 총량을 각각 √2배하면 되고 해당 출력 열도
보존했다. 차원이 있는 `Pi_total_source`와 무차원 Pi를 혼동하지 않았다.

Signed 좌표는 \(\widetilde\Sigma_h=\sqrt3s/H\),
\(\widetilde\Pi_{A,h}=\kappa_tD_A/(\sqrt3H^2)\)이다. 이것은 norm이 아니다.
같은 LRS 축을 공유하는 이번 모델에서 총 norm은

\[
\boxed{\Pi_{{\rm tot},h}=|\widetilde\Pi_{m,h}+\widetilde\Pi_{r,h}|}.
\]

두 component norm의 합을 total로 사용하지 않았다. 일반 non-LRS 텐서에서는
상대 방향과 \(\pi_m:\pi_r\) 교차 수축이 필요하므로, 두 양의 scalar만으로는
총 norm이나 evolution이 정해지지 않는다. Einstein source와 work도 분리했다.

\[
\dot s+3Hs=\frac{\kappa_t}{3}(D_m+D_r),\qquad
\sigma_{ab}\pi_A^{ab}=2sD_A.
\]

출력에는 component/total signed 값, 두 convention의 norm, 각각의 work,
work-sum residual과 cancellation fraction이 포함된다.

## 3. 독립 초기조건과 양의 분포

\[
\Sigma_h\in\{0,0.0005,0.001,0.002,0.004\},\qquad
\Pi_{m,h},\Pi_{r,h}\in\{0,0.00005,0.0001,0.0002,0.0004\}.
\]

0은 부호 0, 나머지는 ± 부호를 독립 부여했다. 각 signed axis는 9개다.
물질에는 \(1+\alpha_mP_2(\mu)\), gamma와 massless nu에는
\(1+\alpha_rP_2(\mu)\)라는 독립 angular seed를 사용했다. Gamma와 nu 사이의
angular shape는 이번에는 같은 alpha_r를 공유한다. Even P₂ family는 초기
odd moment/flux가 없고, -1≤alpha_A≤2에서 양의 분포다.

\[
W_m=\rho_{m,\mathrm{ref}}J_{01}/5,\quad
W_r=(\rho_\gamma+\rho_\nu)/5,\quad
H_i=H_{\rm base}/\sqrt{1-\Sigma_h^2/3},
\]
\[
\alpha_A=\frac{\sqrt3H_i^2\widetilde\Pi_{A,h}}{\kappa_tW_A}.
\]

유한질량 quadrature의 J01=0.014042977688245464를 사용했다.
W_m=8.49370460136e-12 Pa, W_r=8.83695058315e-12 Pa이다.
최대 |alpha_m|=0.8377491056, |alpha_r|=0.8052091461이고 최소 angular
weight는 약 0.16225, 0.19479로 양수다. 초기 검토에서는 원래 생성자로 729개
상태를 별도로 만들었고 실제 저장된 초기 상태도 목표값과 일치했다.

실제 초기 최대 absolute 오차는 Sigma 0, Pi_m 3.3610e-18,
Pi_r 1.6263e-19, signed Pi_total 3.4966e-18이다. 허용값은 3e-13이다.
Stress/weight/roundoff를 clipping하지 않았다. 3e-13 미만은 raw 부호와 값을
남기면서 orientation을 unresolved로 표시했다. 이 초기 family는 higher
moments를 지정하는 추가 가정이며, Sigma/Pi 숫자만으로 모든 kinetic evolution이
유일하다는 주장은 하지 않는다.

## 4. 실제 결과와 해석

아래 표는 모두 signed half-contraction 좌표이며 초기 Sigma=0이다.

| 초기 Pi_m | 초기 Pi_r | 최종 Sigma | 최종 Pi_m | 최종 Pi_r | 최종 Pi_total |
|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 1.080e-21 | 2.165e-18 | -8.268e-28 | 2.165e-18 |
| +4e-4 | 0 | +1.99872964e-7 | +3.99596766e-4 | -1.147e-13 | +3.99596766e-4 |
| 0 | +4e-4 | +1.99920918e-7 | -1.368e-13 | +3.99788529e-4 | +3.99788529e-4 |
| +4e-4 | +4e-4 | +3.99793882e-7 | +3.99596766e-4 | +3.99788529e-4 | +7.99385295e-4 |
| +4e-4 | -4e-4 | -4.79541095e-11 | +3.99596766e-4 | -3.99788530e-4 | -1.91763629e-7 |
| -4e-4 | +4e-4 | +4.79541096e-11 | -3.99596766e-4 | +3.99788530e-4 | +1.91763629e-7 |

Matter-only/radiation-only 입력에서 유도된 반대 성분의 약 1e-13 값은
orientation floor보다 작아 resolved 부호 검출로 주장하지 않는다.

### 상쇄의 시간 변화

초기 상쇄면은 81개이며 비영인 두 성분의 상쇄는 72개다. 그 72개에서 최종
total norm은 모두 표시 기준 3e-13을 넘고 범위는 1.38805e-8~2.02077e-7이다.
초기 shear=0인 비영 상쇄 8개에서는 최종 total norm이
2.39705e-8~1.91764e-7, Sigma norm이 5.99426e-12~4.79541e-11이다.
이는 finite calculation과 표시 기준에서의 결과이며 수렴된 물리 검출과 다르다.

두 species의 pressure evolution이 다르다. 위 극단 상쇄 경우의 실제 Pa 응력에서
계산한 유한구간 희석 지수 -ln|D_f/D_i|/Delta ln a는 matter 4.96831,
radiation 4.00900이다. 비상대론적 collisionless pressure의 대략 a^-5,
radiation의 대략 a^-4 한계와 같은 방향이다. 실제 모델은 finite mass,
Thomson, anisotropic expansion과 UV를 포함하므로 이를 정확한 power law로
대체하지 않았다.

N=ln(a/a_i)에 대해 정확한 signed shear 식은

\[
\frac{d\widetilde\Sigma_h}{dN}
=\widetilde\Pi_{{\rm tot},h}
-\left(3+\frac{\dot H}{H^2}\right)\widetilde\Sigma_h.
\]

초기 shear와 total stress가 0이면 total stress가 먼저 O(N), shear가 O(N²)로
생긴다. 선도 근사 0.5 Pi_total,f Delta N은 -4.79529e-11로 실제
-4.79541e-11과 가깝다. 이 근접성은 짧은 구간의 부호·규모 해석이며 새
정확도 상한은 아니다.

### 그림에서 차분한 기준

`_slices` A–D의 전단 응답은 각 경우의 실제 최종 signed Sigma에서
**같은 초기 Sigma, 두 초기 응력이 0인 control의 실제 최종 Sigma**를 뺀 값이다.
공통 배경 전단 감쇠에 가려지던 성분별 stress response를 보여준다. 이 정의를
축·각주·provenance에 명시했다. Raw CSV에는 원래 초기·최종값이 모두 남아 있다.

`_components` A/B는 각 성분의 실제 최종값−실제 초기값, C는 각 저장 시점의
성분−자기 실제 초기값, D는 차분하지 않은 실제 총 tensor norm이다.
Companion-axis 9개 곡선이 거의 겹치는 것은 이번 구간의 약한 교차 의존성이다.
비균일 grid의 실제 midpoint cell을 사용했고 fit·smoothing·미계산점 interpolation은 없다.

### 열화학적 차이의 한계

729개 전체의 최종 온도 span은 5.8460075e-4 K, x_HII span은 2.4273674e-8이다.
같은 초기 Sigma의 두 초기 응력이 0인 control 대비 최대 절대차는 온도
1.6371e-11 K, x_HII 9.992e-16이다. 같은 Sigma에서 모든 응력쌍의 max−min
범위는 온도 2.9104e-11 K, x_HII 1.6653e-15로 roundoff 수준이다. 원래 C15의 64→128 step 차이는
온도 0.06727061 K, x_HII 6.3288151e-6이며 source 8×8→32×8 차이는
0.0849761 K, 2.8373e-7이었다. 선행 차이는 엄밀한 error bound는 아니지만,
이번 tiny thermochemical 반응을 수렴된 검출로 부를 근거가 부족하다.

## 5. 실제 최적화·벡터화·병렬화 결정

**불변 준비 공유:** native source, log-PCHIP rate, cosmology, angular operators,
radial grid를 group마다 한 번 준비하고 readonly로 공유한다. 세 case가 같은
준비를 재사용한다. Alpha 의존 massive weights, proxy, gas, photon cloud,
moments, counters와 evolving state는 case마다 새로 만든다. 원래 경로와
prepared 경로의 초기값·RHS·두 실제 short steps를 필요한 범위에서 비교했고,
split에서도 반대 부호 두 seed의 실제 owner state·freshness·export를 점검했다.

**기존 벡터화 재사용:** C15의 NumPy angular/radial 연산, finite-mass fast
moments와 positive two-node cohort compression을 사용했다. 서로 다른 adaptive
trajectory를 하나의 거대한 vectorized ODE로 묶기보다 group 수준 병렬화가
이번 독립 sweep에 적합하다. RHS reduction 순서, tolerance와 owner source/rate
bytes를 유지했다. 새 speedup 배율이나 RAM 절감률은 측정하지 않았다.

**재사용 경계:** BRPERF01/RUN19의 준비 패턴은 채택하되 chemistry owner가
다른 rate table로 바꾸지 않았다. C21K의 fixed-epoch cache도 현재 상태에
의존하는 kernel을 epoch 이름만으로 재사용하는 방식으로 확장하지 않았다.
VigilODE 최신 plan의 열린 dense/global error 이슈를 확인하고 solver 교체는
이번 pilot 범위에서 제외했다.

**공존 실행기:** 각 group은 독립 process이며 내부 numeric library thread는 1이다.
CPU affinity, cgroup quota·사용량, sampled idle, MemAvailable와 cgroup memory
remaining을 보고 새 작업만 배분한다. 다른 Codex가 있다는 이유로 중단하거나
다른 process/checkout을 변경하지 않는다. Scope lock, 자기 process group,
직접 argv와 shell=False를 사용한다.

Profile 상한은 sandbox 8 CPU/8 GiB, NCP 64 CPU/128 GiB다. 실제 host 한도와
가용량이 더 작으면 그 값이 우선한다. 이번 실행은 현재 host에서 최대 8 active
workers를 관측했다. Worker당 384 MiB는 admission estimate이며 측정된 peak
memory가 아니다. 짧은 worker의 RSS sample=0을 RAM 절감 근거로 사용하지 않는다.
Job timeout 1,800초, resource wait 300초, 새 admission의 scope disk cap 4 GiB와
filesystem 256 MiB reserve를 둔다. 활성 출력까지 강제 절단하는 hard quota는 아니다.

**완료 재사용:** source/input/toolchain identity와 output SHA256이 일치하는 완료
group을 재사용한다. Worker 수와 memory estimate는 science identity에서 분리했다.
첫 3-case group을 폭 1에서 끝낸 뒤 폭 8 전체 실행에서 재사용했다. 전체 실행은
242 PASS+1 SKIPPED_PASS, 고유 성공은 243개다. 부분 group의 개별 case 자동 이관,
group 재분할 시 자동 reuse는 구현하지 않았고 handoff에 한계를 명시했다.

현재 환경에는 이전 승인 SSH key 경로가 없어 새 pilot을 NCP에서 실행하지
않았다. 이를 이유로 오늘 계산을 중단하지 않고 현재 가용 host에서 그림을
완성했다. 다음 Codex는 NCP 환경과 실제 여유를 확인해 새롭거나 미완료인
과학 작업을 배분하면 된다. 완료한 81/729개를 core 사용률만 높이려고 반복할
필요는 없다. 요청대로 상세 성능·최적화 benchmark는 실행하지 않았다.

## 6. 검토, 오류 보존 및 백업

독립 검토에서 243개 raw/receipt의 hash·binding, 전체 9³ grid와 47,385개 상태,
모든 5,832 numerical gate를 확인했다. 원본 JSON과 CSV의 3,450,357개 scalar가
정확히 일치하고, JSON float 2,662,299개가 finite다. Component tensor sum,
norm, work, orientation 및 figure provenance도 독립 검토했다.
이 검사는 finite-step numerical gate이며 전체 Qᵃ closure나 전역 solution error
인증을 대신하지 않는다.

첫 81-case 시도는 NumPy bool JSON export 오류로 성공 저장이 0개였다.
27개 실패 receipt와 traceback을 `results/pilot81/`에 보존했다. Correction
`003550e…`는 scalar export 경계만 고치고 NaN/Infinity 거부·물리식·허용값은
유지했다. 새 manifest/scope에서 81개를 완료했고 그 export를 split에서도 사용했다.

Stage3의 최초 큰 ZIP은 최초 준비 receipt보다 현재 local/remote bytes가
569,741 bytes 작게 관측됐고 원격 full GET에서도
ZIP 종료 레코드 누락을 확인했다. 원인은 UNKNOWN으로 남겼고 해당 객체는
`INVALID_ARCHIVE_DO_NOT_RESTORE`다. 온전한 원자료에서 정확히 454 payload,
37,133,647 bytes를 독립 ZIP 4개로 복구했다. 각각 원격 full GET, 전체 SHA256,
provider blockhash, ZIP CRC와 모든 payload hash를 확인했다. 손상 원본을
덮어쓰거나 삭제하거나 같은 경로로 재시도하지 않았다.

Stage4 source 8파일 백업은 ACK·metadata 크기·업로드 후 로컬 SHA/CRC 확인
수준이다. Remote full GET과 같은 확인 수준으로 표시하지 않는다. Stage5는
729-case 입력·raw·CSV 1,715개 파일, 423,198,268 bytes를 보존하는 별도 백업이다.
동일 byte chunk만 content-address로 공유하고 모든 원본 경로·순서·크기·SHA를
복원 map에 남겼다. 큰 history.csv도 원본을 수정하지 않고 나눴다. 18개 독립
ZIP의 총 크기는 47,297,026 bytes다. 18개 ZIP과 INDEX 모두 원격 full GET을 마쳤고, 원격 사본만으로 원본
1,715개 파일을 재조립해 모든 SHA256이 일치했다. 각 part 식별자와 검증은
`delivery/STAGE5_DATA_DELIVERY.json`에 있다.

## 7. 최신 근거 통합과 외부 연구

이번 조사는 branch/PR 목록을 전체 pagination하고 최신 관련 source·result·handoff를
읽었다. 새 PR 이전 목록 범위는 BASS 260 branches/175 PRs, REI 253/211,
VigilODE 183/78, bass_cr 166/89, BASS_HE 86/81, WU088_HH 135/126이다.
목록 전체와 모든 branch의 모든 파일을 읽었다는 주장은 구분한다.

제공 파일 20개/435,180,795 bytes의 inventory를 기록했다. Dropbox 조사 폴더
세 곳의 직접 자식 61/40/3,273개 목록 끝을 확인하고 선택한 5개 backup은 전체
bytes/hash를 검증했다. Drive atomic 폴더는 1,000개 반환 상한에 도달했고
Personal Context는 실제 service error를 반환했다. 따라서 모든 과거 대화와
계정 전체 저장물을 전수 열람했다고 말할 수 없다. 현재 대화, 제공 handoff,
Git 기록과 선택한 원본 backup을 종합했다.

중요한 갱신은 S12의 실제 NCP 17-job 완료와 성공 16개 재사용이다. 과거
NOT_RUN을 오늘의 backlog로 취급하지 않았다. REI의 기존 완료 결과·aggregate
cap과 다른 Codex 세션의 존재도 새 자동 중단 조건으로 바꾸지 않았다.
자세한 source pin과 비교 판단은 `evidence/latest_intake/`,
`RESEARCH_DECISIONS.md`와 첫 pilot 상세 보고 `PILOT01_REPORT_KO.md`에 있다.

SciSpace와 Exa로 Lee–Nungesser–Tod 및 Heinzle–Uggla의 Bianchi I 원문을
확인하고 tensor/kinetic 구조와 higher moments 의존성을 반영했다. 해당
asymptotic isotropization 정리를 driven warm reionization에 그대로 적용하지
않았다. Wolfram으로 contractions, P₂ moment 1/5, positive-alpha 범위와
constraint identity를 확인했으며 undefined global-symbol warning도 보존했다.

실제 외부 수치 도구는 SciPy PCHIP와 Python process API 등 기존 owner의
공식 구현을 재사용했다. 급한 JIT/MPI/새 solver 도입을 대신해 source identity와
실제 호환성을 유지했다. 실행 환경은 Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0이다.

- [Lee–Nungesser–Tod, arXiv:1911.04937](https://arxiv.org/abs/1911.04937)
- [Heinzle–Uggla, gr-qc/0512031](https://arxiv.org/abs/gr-qc/0512031)
- [SciPy PchipInterpolator 공식 문서](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html)
- [Python subprocess 공식 문서](https://docs.python.org/3/library/subprocess.html)

## 8. DAG와 후속 우선순위

| 단계 | 상태 | 게시·백업 근거 |
|---|---|---|
| 최신 evidence intake | 완료 | e9f7720…, Stage1 |
| 정의·공유 준비·실행기 | 완료 | 0fcf9cc…, Stage2 |
| Export 교정 | 완료 | 003550e…, Stage2.1 |
| 81-case 실제 pilot | 완료 | 0d1864a…, Stage3 검증 복구 parts |
| 독립 물질·복사 구현 | 완료 | 82372ed…, Stage4 |
| 729-case 실제 계산·그림·독립 검토 | 완료 | 최종 결과 commit 및 Stage5 receipt |
| 새로운 NCP 실행 | 이번 환경에서는 미수행 | 키 경로 부재; 현재 host 계산 완료, NCP profile 준비 |
| Full Qᵃ·cold EoR·general non-LRS·수렴 | 열림 | 이번 조건부 pilot의 완료와 분리 |

후속 물리 작업은 stellar/emitter donor의 pressure·IC·reservoir와 실제 radiation
event ΔU를 shared-Q helper에 연결하고, cold regime rate owner 및 full-history
초기조건을 결속하는 순서가 우선이다. 현재 10,000~24,000 K rate table을 약 8 K까지
외삽해 z20→4 그림을 만드는 것은 유효한 확장이 아니다. General tensor orientation과
angular/spectral/global convergence는 별도의 과학 단계로 남긴다.

복사 가능한 지시는 `CODEX_HANDOFF.md`, `NEXT_THREAD_HANDOFF.md`에 있다.
`DAG.json`과 별도 delivery receipt가 계산 완료, 열린 물리 범위, 실제 게시·백업
수준을 구분한다. 과거 Drive의 모호한 write에 새 retry를 추가하지 않았다.

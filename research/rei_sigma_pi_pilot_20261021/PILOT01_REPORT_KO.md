# BASS → REI: 81-case Sigma/Pi 예비 sweep 완료

## 1. 이번 연구 루프의 실제 산출물

2026-10-21에 non-tilted **LRS Bianchi I**의 81개 초기조건을 실제로
적분하고 첫 parameter-sweep 그림을 만들었다. 각 경우는 64개 결합 step을
가지며, 초기점까지 포함한 CSV는 **5,265행**이다. 27개 독립 group의 출력이
모두 저장되었고 원래 C15의 수치 gate를 통과했다. 첫 3개 경우를 저장한
group은 병렬 폭을 1에서 8로 늘린 뒤 hash 확인으로 재사용했다.

이 결과는 **warm a=0.1999→0.2, z=4.00250125→4**의 조건부 예비 계산이다.
원래 C15의 H/He, MD14 source, gamma/nu Boltzmann, massive Vlasov 및 Einstein
shear feedback을 함께 사용한다. Cold z=20→4 이력, 일반 non-LRS Bianchi I,
완전한 stellar/escape Q^a closure, 전역 격자 수렴을 완료했다는 뜻은 아니다.

실행 source는 BASS `003550e04e8d6c316be422f8ac6a15df284e49a5`, 물리 owner는
REI PR141 `80825585f9fe31d2ee0d5af545ada3fa1f52be72`이다. 변경과 결과는
[BASS PR176](https://github.com/cosmosapjw-quantum/bass/pull/176) 및
[REI PR213](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/213)에
추가하는 방식으로 게시했다. 두 PR 모두 draft이며 merge하지 않았다.

주요 결과 파일은 `results/pilot81_v2/aggregate/` 아래에 있다.

- `sigma_pi_response.png/.pdf`: 실제 초기값에 대한 signed 변화량.
- `sigma_pi_pilot.png/.pdf`: endpoint와 원래 trajectory 개요.
- `cases.csv`: 81개 endpoint, 초기값, 에너지 성분, 부호, 보존검사.
- `history.csv`: 각 실제 초기점과 64개 step을 모두 보존한 5,265행.
- `summary.json`, `METRICS.json`, 두 figure provenance: source/input과 수치 요약.

## 2. 최신 branch·repo·백업을 종합한 판단

| 조사 대상 | 확인 범위 | 오늘의 결정 |
|---|---|---|
| BASS | 새 PR 이전 branch 260, PR 175; 최신 S12 source/result/comment | NCP 17-job 완료를 재사용. 오래된 NOT_RUN을 후속 backlog에서 제거 |
| rei_bianchi | branch 253, PR 211; C15/V14/BRPERF01/RUN19/orchestration | 물리 owner C15 유지, 최신 준비/실행 기법만 호환성 확인 후 재사용 |
| VigilODE | branch 183, PR 78; 2026-10-21 최신 plan | solver 교체를 이번 pilot과 묶지 않음. dense error enforcement/global error 이슈가 열려 있음 |
| bass_cr | branch 166, PR 89; C21K와 선행 native 결과 | 불변량 캐시·고정 연산순서·독립 job 패턴 재사용 |
| BASS_HE | branch 86, PR 81; HE29 NCP return | finite packed atomic canary 근거 보존. C15 물리 kernel을 대체하지 않음 |
| WU088_HH | branch 135, PR 126; PHYS70/73 | block/ordered SIMD 기법 공급자. raw intake 및 HH rate의 미완료 상태 보존 |

Branch/PR **목록의 pagination 완료**와 모든 branch의 모든 파일을 읽었다는
주장은 다르다. 이번에는 목록 전체를 확보하고 최신 관련 source, result,
handoff, pending 상태를 선별하여 실제 내용을 읽었다. 20개 제공 파일의
크기·SHA256·archive 목록도 기록했다.

Dropbox의 세 조사 폴더는 각각 61, 40, 3,273개 직접 자식에 대해 반환된
pagination 끝을 확인했다. 선택한 5개 backup은 전체 bytes를 내려받아 hash를
검증했다. Drive의 큰 atomic 폴더는 1,000개 반환 상한에 도달했고,
Personal Context는 실제 service error를 반환했다. 따라서 모든 과거 대화와
계정 전체 저장물을 전수 열람했다고 말할 수 없다. 접근 가능한 현재 대화,
제공된 handoff, Git 기록과 선택한 원본 backup을 종합했다.

가장 중요한 갱신은 S12였다. 2026-10-21의 실제 반환 archive와 댓글에 따르면
17 jobs가 완료됐고, 재시작 때 성공한 16개를 재사용했다. 14개 manufactured
extended histories와 기존 병렬 비교는 이미 끝난 근거다. 오늘 이를 재실행하지
않았다. 같은 이유로 REI의 기존 실행 완료와 aggregate cap에 의한 미실행을
새로운 물리 실패나 오늘의 자동 중단 이유로 바꾸지 않았다.

세부 source pin과 접근 범위는 `evidence/latest_intake/` 및
`RESEARCH_DECISIONS.md`에 있다.

## 3. Sigma/Pi의 정의와 초기조건

이 owner의 LRS metric은

\[
a_\perp=a e^{-b},\qquad a_\parallel=a e^{2b},\qquad s=\dot b
\]

이고 orthonormal frame에서

\[
\sigma^a{}_b=\operatorname{diag}(-s,-s,2s),\qquad
\pi^a{}_b=\operatorname{diag}(-D/3,-D/3,2D/3),\quad
D=P_\parallel-P_\perp.
\]

따라서 \(\sigma_{ab}\sigma^{ab}=6s^2\),
\(\pi_{ab}\pi^{ab}=2D^2/3\), \(\sigma:\pi=2sD\)이다. 기존 C15와
같은 half-contraction norm을 기본값으로 두었다.

\[
\Sigma_h=\sqrt3\frac{|s|}{H},\qquad
\Pi_h=\frac{\kappa_t|D|}{\sqrt3H^2},\qquad
\kappa_t=\frac{8\pi G}{c^2}=3\,\mathrm{C15.KAPPA}.
\]

압력/에너지밀도는 Pa=J/m³, 시간은 초이다. Einstein equation의
\(\kappa=8\pi G/c^4\)를 쓰는 표기에서는 여기의 proper-time 식에
\(\kappa c^2\)가 들어간다. Frobenius norm을 원하면 두 무차원량을 모두
\(\sqrt2\)배하면 되며 해당 열도 출력했다. `Pi_total_source`는 차원이 있는
RHS bookkeeping 값이므로 무차원 Pi와 혼동하지 않았다. 물리적 D는
gamma+nu+massive+UV 네 성분을 실제로 합산했다.

크기만으로는 evolution이 정해지지 않는다. signed 좌표를
\(S=\sqrt3s/H\), \(P=\kappa_tD/(\sqrt3H^2)\)라 쓰면
\(\dot s+3Hs=\kappa_tD/3\)의 결합 부호가 남는다. 그래서 다음 크기
grid의 모든 독립 부호를 포함했다.

\[
\Sigma_h\in\{0,0.0005,0.001,0.002,0.004\},\quad
\Pi_h\in\{0,0.00005,0.0001,0.0002,0.0004\}.
\]

0의 부호는 정확히 0, 나머지는 ±1이다. 각 signed axis가 9개여서 중복 없는
81개 경우가 된다. 분포의 초기 family는 gamma/nu/massive에 공통인
\(W(\mu)=1+\alpha P_2(\mu)\), \(-1\le\alpha\le2\)로 고정했다.
실제 owner의 초기 moment로

\[
W_D=(\rho_\gamma+\rho_\nu+\rho_{m,ref}J_{01})/5,
\quad H_i=H_0/\sqrt{1-\Sigma_h^2/3},
\quad \alpha=\frac{\epsilon_P\sqrt3H_i^2\Pi_h}{\kappa_tW_D}
\]

를 계산했다. 최대 \(|\alpha|=0.4105784436521941\)로 positive family 내부다.
요청값을 clipping하거나 음의 weight를 잘라내지 않았다. 이 family 선택은
초기조건을 완성하기 위한 추가 물리 가정이다. Sigma/Pi 두 숫자만으로 모든
입자 분포의 후속 evolution이 유일해진다는 주장은 하지 않는다.

초기 좌표 오차의 실제 최대값은 Sigma 0, Pi
\(2.7647155398380363\times10^{-18}\)였다. 초기 검증 기준은 각각
\(3\times10^{-13}\)이다. 등방 control의 Pi 약 \(2.16\times10^{-18}\)은
raw quadrature roundoff로 보존하고 unresolved로 표시했다.

## 4. 실제 예비 결과

다음 표의 S/P는 부호를 가진 half-contraction 좌표이다.

| 초기 S | 초기 P | 최종 S | 최종 P |
|---:|---:|---:|---:|
| 0 | 0 | 1.08e-21 | 2.16e-18 |
| 0 | -4e-4 | -1.99897416e-7 | -3.99694547e-4 |
| 0 | +4e-4 | +1.99897416e-7 | +3.99694547e-4 |
| -4e-3 | 0 | -3.99695204e-3 | +1.00580999e-8 |
| +4e-3 | 0 | +3.99695204e-3 | -1.00580799e-8 |
| -4e-3 | -4e-4 | -3.99715194e-3 | -3.99685276e-4 |
| -4e-3 | +4e-4 | -3.99675215e-3 | +3.99705392e-4 |
| +4e-3 | -4e-4 | +3.99675215e-3 | -3.99703824e-4 |
| +4e-3 | +4e-4 | +3.99715194e-3 | +3.99683707e-4 |

초기 전단이 없는 경우에도 anisotropic stress가 전단을 만든다. 초기
응력이 0인 경우에도 이방 팽창이 반대 부호의 응력을 만든다. 같은 크기의
Sigma/Pi에서 상대 부호를 바꾸면 최종 전단 크기가 달라지므로 부호를
보존한 sweep이 필요함을 실제 계산에서 확인할 수 있다. 이는 이 고정
family와 warm short interval의 수치 반응이며 보편적 비선형 안정성 정리는 아니다.

81개 경우 전체의 signed 변화량 범위는 다음과 같다.

- \(\Delta S\): -3.2478527347e-6 ~ +3.2478531270e-6.
- \(\Delta P\): -3.1629266828e-7 ~ +3.1472394647e-7.

응답 그림은 **최종값 − 실제 초기값**을 사용했다. 요청한 nominal initial
value를 빼서 roundoff를 숨기지 않았다. 원래 endpoint 그림도 함께 보존했다.
비균일한 parameter 간격은 실제 좌표의 pcolormesh로 표시했으며, smoothing,
fit 또는 계산하지 않은 점의 interpolation을 하지 않았다.

온도 범위는 12193.427627207691~12193.428211808437 K, x_HII 범위는
0.40881816447530145~0.4088181887489751이다. 전체 span은 각각
5.8460e-4 K, 2.4274e-8이다. 기존 C15의 64→128 step 차이
0.06727061 K와 6.3288151e-6, source 8×8→32×8 차이보다 작다.
이 선행 차이는 엄밀한 error bound는 아니지만, 이번 tiny thermochemical
변화를 수렴된 검출로 부를 수 없다는 판단에는 충분하다. 상세 수렴/성능
benchmark를 추가하지 않고 원자료만 보존했다.

## 5. 실제로 적용한 최적화·경량화·병렬화

**불변 준비의 공유.** Native source, log-PCHIP rate table, angular operators,
radial quadrature와 cosmology 준비를 group마다 한 번 만들고 readonly로
공유한다. 세 case가 같은 준비를 사용한다. alpha에 의존하는 massive weights,
gas, photons, multipoles, proxy, counters는 각 case에서 새로 만든다.
진화 RHS와 합산 순서는 바꾸지 않았다. 원래 생성자와 준비 경로의 네 RHS
평가가 elementwise 동일했고, 같은 입력의 초기점 및 두 실제 step도 일치했다.

**기존 벡터화와 compression의 재사용.** C15의 NumPy angular/radial 연산,
finite-mass fast moments와 positive two-node cohort compression을 그대로
사용했다. Source/rate owner를 바꾸거나 angular/spectral order를 낮추는
방법으로 빠른 결과를 만든 것이 아니다. 기존 문헌/코드의 재사용과 새로운
최적화의 역할을 source identity로 구분했다.

**독립 group 병렬화.** 각 group은 독립된 process이고 내부 numeric library
thread는 1이다. 현재 host의 8 CPU/8 GiB cgroup 상한 안에서 실제 최대
8 active workers가 관측됐다. CPU affinity, quota/usage, sampled idle,
MemAvailable와 cgroup memory remaining을 보고 새 작업만 admission한다.
다른 Codex 작업이 있다는 이유로 중단하지 않고, 다른 process를 종료하거나
다른 checkout을 바꾸지 않았다.

**완료 작업 재사용과 입력 분리.** Source/input/toolchain identity와 output
SHA256을 확인해 성공 group을 재사용한다. Worker 수와 memory estimate는
과학 identity에서 분리했다. 이번 실제 실행에서 first group을 폭 1→8 변경 후
재사용했다. Group 분할을 바꾸거나 부분 완료 group의 개별 case를 자동 이관하는
기능은 구현하지 않았고 그 한계를 명시했다.

**NCP 준비.** NCP profile은 64 cores/128 GiB를 상한으로 하되 실제 host의
quota와 현재 가용량이 더 작으면 그 값을 따른다. Job timeout은 1,800초,
scope disk admission cap은 4 GiB이다. 메모리·디스크는 admission 정책이며
kernel hard quota가 아니다. 현재 receipt의 worker RSS sample은 대부분
0이라 신뢰할 수 있는 peak-memory 측정으로 쓰지 않는다. 완료에 필요한
자원 관측과 검증을 했지만 새 speedup이나 RAM 절감률을 주장하지 않는다.

이 sandbox에는 기존 승인 SSH key path가 없으므로 새 pilot의 NCP 실행은
하지 않았다. 이를 이유로 오늘 계산을 중지하지 않고 가용 sandbox에서
완료했다. 다음 Codex는 이미 완료한 81개를 단지 64 cores를 채우려고 반복하지
않고, 실제 미완료/새 과학 작업을 같은 scheduler로 배분해야 한다.

## 6. 실패·교정·검토를 포함한 실행 기록

최초 source `0fcf9cc…` 실행에서는 27 group의 첫 case가 계산 후 JSON 저장
경계에서 NumPy bool 형식 오류를 냈다. 성공 출력은 0개였고 실패 receipt와
traceback을 모두 보존했다. 이 자료를 완료된 pilot로 계산하지 않았다.

수정 `003550e…`는 NumPy scalar를 정확한 Python scalar로 변환하는 export
경계만 바꿨다. NaN/Infinity 거부, unsupported object 오류, 수치식, tolerance,
gates를 유지했다. 실제 scalar export regression 하나로 이 실패를 확인했다.
수정 source를 먼저 게시·백업한 뒤 새 manifest/scope에서 실행했다.

교정 후 첫 group의 3 cases가 저장과 gate를 통과했고, 전체 실행은
26 PASS + 1 SKIPPED_PASS로 끝났다. 고유 성공 receipt는 27, 고유 case는 81이다.
모든 출력 27개가 receipt의 크기/SHA와 aggregate 목록에 일치하고 source/input
55개도 일치했다. 계산 중 관측한 scope 최대는 약 25.7 MB로 4 GiB보다 작다.

실제 최악의 원래 수치 gate 값:

| 검사 | 실제 최대 | 원래 허용값 |
|---|---:|---:|
| photochemical number | 2.7756e-16 | 5e-12 |
| photochemical energy, eV/H | 7.1054e-15 | 5e-11 |
| gamma number monopole | 0 | 3e-9 |
| neutrino number monopole | 0 | 3e-9 |

이것은 저장된 finite-step numerical gate다. Stellar donor/escaped radiation
전체 Q^a 보존이나 전역 solution error bound를 대신하지 않는다.

## 7. 문헌·수식 확인과 열린 물리 과제

SciSpace와 Exa를 이용해 Lee–Nungesser–Tod의 Bianchi I massless
Einstein–Vlasov 논문과 Heinzle–Uggla의 Bianchi I dynamics 원문을 확인했다.
이들의 geometric/kinetic 구조와 higher-moment 의존성은 사용했지만,
asymptotic isotropization 결과를 driven warm reionization에 그대로
적용하지 않았다. Wolfram은 tensor contractions, angular moment factor 1/5,
positive-alpha domain 및 constraint identity를 확인했다. 반환된 undefined
global-symbol warning도 evidence에 보존했다.

- https://arxiv.org/abs/1911.04937
- https://arxiv.org/abs/gr-qc/0512031
- https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html
- https://docs.python.org/3/library/subprocess.html

다음 과제의 순서는 물리 입력에 의해 정해진다. Stellar/emitter donor의
pressure/IC/reservoir와 실제 radiation event ΔU를 연결해 shared-Q closure를
구체화해야 한다. 그 후 cold regime에 유효한 rate owner와 full-history 초기
상태를 결속해야 한다. 현재 10,000~24,000 K rate table을 약 8 K로 외삽해
z20→4 결과를 만드는 것은 후속 구현의 대안이 될 수 없다. Angular/polarization,
spectral/global convergence와 관측량은 그 다음 단계다.

## 8. DAG·게시·백업

| 단계 | 상태 | 실제 근거 |
|---|---|---|
| 최신 evidence intake | 완료 | branch/PR catalogues, selected full-GET hashes, obsolete S12 상태 교정 |
| 정의·양의 초기 family·scope | 완료 | THEORY, CAS response, C15 audit, frozen contract |
| 준비 공유·가용 자원 실행기 | 완료 | source publication, minimal controls, independent RHS/step review |
| export 오류 교정 | 완료 | 실패 기록 보존, strict scalar regression, corrective commit |
| 81-case actual sweep | 완료 | 27 receipts, 81 unique cases, 5,265 history rows |
| figure·independent result review | 완료 후 publication snapshot에 기록 | raw/CSV/plot provenance와 review JSON |
| source/result publication·backup·handoff | 최종 receipt 참조 | BASS PR176, REI PR213, delivery/ 및 외부 final receipt |
| full Q^a / cold full EoR / general non-LRS | 열림 | 위 조건부 pilot의 완료와 구분 |

Stage 1 intake commit `e9f7720…`, Stage 2 source `0fcf9cc…`, Stage 2.1
export correction `003550e…`의 고정 archive와 Dropbox 완료 ACK가 각각 있다.
최종 package는 source, raw 성공/실패 기록, CSV, figures, review, handoff를
함께 포함한다. 원격 full GET을 하지 않은 신규 upload는 ACK/metadata 확인으로
표시한다. 이전 Drive의 모호한 write 상태에 새 retry를 추가하지 않았다.

복사 가능한 후속 작업은 `CODEX_HANDOFF.md`와 `NEXT_THREAD_HANDOFF.md`를 쓴다.
각 최종 commit/tree 및 archive hash는 자기참조를 피한 별도 delivery receipt에 있다.

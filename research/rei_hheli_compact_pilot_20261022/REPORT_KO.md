# ACCEL04 → PHYS04 → PILOT04 최종 연구 보고서

## 1. 이번에 실제로 끝낸 계산

이 샌드박스에서 non-tilted LRS Bianchi I의 독립 matter/radiation 응력 sweep을
z=20에서 z=2까지 적분했다. 125개 격자 사례와 두 초기 상쇄 사례, 총 127개
사례가 각각 193개 시점을 저장했다. 따라서 본 계산의 history는 24,511행이다.
추가로 원래 62변수 구현의 두 전구간 해를 별도로 계산하여 33변수 구현과
대조했다. 본 sweep과 oracle를 합한 129개 사례 모두 13개 inherited gate를
통과했다. 두 구현의 대조와 실제 배열에서 그림으로의 연결도 통과했다.

이 결과는 지정한 온도와 외부 UV를 사용하는 H–Li 원자망 아래의
preliminary pilot이다. 모든 채택 핵종·전하 상태를 저장하며, 완전한 열·복사
에너지 교환 closure, 모든 가능한 핵반응, 비-LRS 모형 또는 분해능 수렴의
완료를 뜻하지 않는다. 이러한 범위는 실행 전에 FROZEN_CONTRACT.md로 고정했다.

기존 warm729의 729 cases / 243 groups / 47,385행과 ACCEL01–03 결과는
재사용 근거로 보존했다. 그 짧은 구간 a=0.1999→0.2의 결과를 이번 z=20→2
시간 이력으로 대체 표기하거나 단순 연장하지 않았다.

완료 근거:
- results/analysis/SUMMARY.json
- evidence/STAGEB_EXECUTION_RECEIPT.json
- evidence/PAIRED_COMPARISON.json
- evidence/PLOT_VERIFICATION.json
- evidence/PLOT_VISUAL_INSPECTION.json
- evidence/FINAL_RESUME_VERIFICATION.json

최종 독립 검토와 root admission의 실제 상태는 evidence/independent_review/ 및
evidence/ROOT_ADMISSION_C.json을 따른다. 게시·백업은 delivery/의 실제 ACK를 따른다.

## 2. 최신 결과 조사와 재사용 결정

접근 가능한 GitHub repo 7개에서 branch head 1,249개를 수집하고, repo catalog
51개 및 관련 PR·선택 파일을 비교했다. 앞선 4개 repo의 876개 head 기준과
비교한 새 head는 4개, 변경 head는 1개였다. 선택한 76개 파일은 Git blob
정체성을 확인했다. 모든 branch의 모든 파일을 읽었다는 뜻은 아니다.

관련 Dropbox 경로는 직접 listing의 pagination을 끝까지 확인했다.
BASS_BACKUPS 105개, BASS_CR dossier 46개, REI research_backups 55개,
상위 dossier 3,281개, REC 경로 49개, Li rate 경로 35개, root 454개가
조사되었다. 폴더 전체 재귀 복제와는 구별한다. PersonalContext의 과거 대화
조회는 이 대화에서 사용 불가 응답이었고, Drive 검색도 현재 연결에 보이는
자료 범위에 한정된다. 따라서 접근 불가능한 다른 대화까지 조사 완료로
표시하지 않는다. 자세한 실제 응답과 범위는 intake/git/ 및 intake/backups/에 있다.

| 조사 대상 | 확인한 새 상태 | 이번 채택 |
|---|---|---|
| REC119, a949529872eb5ba0e20c7e206fe893e5d544e48c | 최초 조사 시 62상태 H–Li coupled owner, Stage B 준비; 마감 시 새 실행 확인 | 57개 donor 파일 그대로 보존하고 실제 RHS/Jacobian/원자 계수 재사용 |
| BASS_HE HE32, e8bb035d31f59e34734947b9082bdbd60128b799 | 반사 짝수 기하 부분공간 | 40→23 축약의 수학적 구조 재사용; 다른 수치 행렬을 섞지 않음 |
| REI D9, cce008b3fc32c298185b30550b2cd909d74fcd87 | 기존 175 histories ×153 시점의 분석, 새 IVP 0 | source-budget 분석·기준 해 대응 방식 참고 |
| BASS_CR C21N, 8dc5031b3323d4be42a7444843294200aa8887f2 | 새 off-grid 4개 z=20→4 결과와 NCP 재현 | sandbox/NCP 실행 근거를 구분하여 보존 |
| HH132/PHYS77, d43cf2df2c4864ae05049f44301c5b389b80a49c | whole-cell enclosure 근거 | positivity와 유한 표현 범위 검토 |
| toy_bbn, 908c24e478384912b0c547aade5e209b7ec2695f | 12개 REACLIB 반응 source | 향후 핵반응 확장용으로 식별; IGM 온도에 검증 없이 외삽하지 않음 |

새 C21N archive와 REI D9 archive는 실제 GET 후 각각 SHA-256
474534bde84a712c939f8447279e5a821853a223c324d06cc684ea925a6a8561,
bf3547dd6542626d011d51251e1a091d9ac0cca5480d6124c6faca09cfc3d679
으로 확인했다. REC Stage B와 HE32의 더 최근 backup object도 확인했고,
실제 채택 source는 위 고정 Git commit으로 연결했다.

마감 재확인(2026-10-21 16:04 UTC)에서 REC와 HE branch가 작업 중 이동한
것을 발견하여 전체 old/new blob tree를 다시 비교했다. REC의 새 head는
ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7이며 125개 main IVP와 별도
opacity-off control 1개, 총 126개의 고유 z=20→2 실행이 추가되었다.
127개 trajectory 경로 중 하나는 역사적 복구 중복이므로 고유 실행 수에
중복 산입하지 않는다. 기존 과학 코드의 변경은 NumPy scalar JSON 저장
fallback뿐이며 RHS/Jacobian/기하/원자율/model/vendor의 변경은 없었다.
이 새 결과는 별도 donor 실행이고 본 127개와 합산하지 않는다.

HE의 새 head 0c016a11966547d81dbc61117ab45e8f0ab81790에는 52상태
결합 모형과 새로운 표가 추가되었지만, committed science trajectory는 없고
F.C7–F.C10은 pending이었다. 기존 compact transport/vendor는 변하지 않았다.
새 REC의 실행 사실은 반영하되, 검증한 고정 REC kernel과 HE 수학적 구조의
재사용 결정을 유지했다. 이 마감 비교는 REC 628개·HE 81개 변경 파일의
완전한 blob-tree delta를 사용했고, 자세한 근거는
evidence/FINAL_DONOR_DELTA_REVIEW.json 및 .md에 있다.

Exa·SciSpace의 실제 조회는 원자율·핵반응 문턱과 재사용 source를 찾는 데,
Wolfram의 실제 CAS 출력은 전이행렬 보존성, isotope 표현, tensor contraction
검산에 사용했다. 전체 진화계의 타당성을 CAS 한 번으로 증명했다고 표시하지 않는다.

## 3. 물리계와 정규화

정규직교 LRS frame에서

\[
 \sigma_{ab}=\operatorname{diag}(-s,-s,2s),\qquad
 \pi_{A,ab}=\operatorname{diag}(-p_A,-p_A,2p_A).
\]

따라서 full Frobenius convention은

\[
 S_F={\sqrt6\,s\over H},\quad
 P_{A,F}={\sqrt6\,\kappa_t p_A\over H^2},\quad
 \Sigma_F=|S_F|,\quad
 \Pi_{\rm total,F}=|P_{m,F}+P_{r,F}|.
\]

여기서 H는 s^-1, rho와 p는 J m^-3, kappa_t=8πG/c²다.
예전 half-contraction 값은 각각 full 값/√2이며 양쪽을 출력에 저장했다.
matter와 radiation은 부호를 유지하여 합한 뒤 norm을 취한다.
따라서 Pi_total을 Pi_m+Pi_r로 계산하지 않는다.

\[
 H^2={\kappa_t\rho_{\rm total}\over3}+s^2,\qquad
 \dot s+3Hs=\kappa_t(p_m+p_\gamma+p_\nu).
\]

응력의 matter 성분은 fraction=0.1, m/T_ref=30인 별도 collisionless
비바리온 성분이다. 24×12 canonical cell의 Gauss3 packet 2,592개를 유지한다.
바리온 원자 기체는 common-T 등방 모형으로 pi_b=0이다.
radiation은 CMB photon과 collisionless neutrino의 합이다.
원자망이 만드는 전자밀도는 photon Thomson 항에 되먹임한다.
독립적인 초기 pi_m와 pi_r는 채택한 양의 분포 허용영역 안에서 설정했다.

이 구분은 중요하다. 이번 Li 원자망의 추가는 원자 기체에 독립적인
점성응력 방정식을 새로 부여한 것이 아니다. 바리온 응력 자체를 연구하려면
그에 맞는 kinetic/constitutive closure가 추가로 필요하다.

## 4. 모든 채택 isotope/ion 상태와 활성 반응

| 핵종 | 저장 상태 | 초기 number/H1 |
|---|---|---:|
| n | n | 0 |
| H1 | I, II | 1 |
| D | I, II | 2.5e-5 |
| T | I, II | 0 |
| He3 | I, II, III | 1e-5 |
| He4 | I, II, III | 0.08112582781456953 |
| Li6 | I, II, III, IV | 1e-14 |
| Li7 | I, II, III, IV | 5e-10 |

이 21개 heavy state와 charge sum으로 얻는 free electron을 포함한다.
Li IV는 완전 이온화 Li³⁺다. 여기서 '모든 상태'는 표의 primordial inventory와
비음수 전하의 원자 상태를 뜻한다. H⁻, 분자, 더 무거운 원소와 모든 단명 핵공명은
포함 범위가 아니다.

광이온화와 case-A RR/DR을 활성화했다. 같은 원소의 동위원소에는 같은 전자
반응률을 적용한다. n/T beta map은 원래 source에 있으며 이번 n=T=0
초기조건에서는 flux가 정확히 0이다. 첨부 그림의 19개 반응과 각 반응의
활성·0·미구현 상태를 intake/theory/NETWORK19_SCOPE.json에 대응시켰다.

지정 입력은

\[
 Q(z)={1+\tanh[(7-z)/0.8]\over2},\qquad
 T(z)=100+11900Q(z)\ {\rm K}
\]

이고, local isotropic UV number spectrum은 5–200 eV에서 E^-2.5,
late Gamma_HI=1e-12 s^-1이다. 이 UV reservoir는 동적으로 진화시키는
CMB multipole과 별도다. 기체의 열·이온화·흡수 에너지와 필요한 외부 열입력은
진단 장부로 저장했다.

Verner photo/partial-shell 식과 Verner–Ferland·Badnell RR/DR 계수는
고정 donor source에서 재사용했다. Li I inner-shell은 기존 단일 charge-step
근사를 유지하고 primary electron과 unresolved core energy를 구분했다.
첨부 핵망의 광핵반응은 가장 낮은 채택 Li6→alpha+D 문턱 1.4743 MeV조차
UV upper support 200 eV보다 높으므로 현재 유한 UV 모형에서 rate가 0이다.
이 지원영역 논증은 열핵 융합의 생략 오차를 정량화한 것이 아니다.

CI, charge exchange, 분자, secondary electron, 열핵반응과 완전한
thermal/radiative Q^a closure는 남아 있다. 이 항목의 오류를 임의의 0으로
설정하거나 작은 에너지 비만으로 전체 물리 오차 상계라고 주장하지 않는다.
100–12000 K라는 지정 온도 경로 및 전자율 동일성도 모델 입력이다.

## 5. 실제 최적화: 62→33 좌표와 벡터 계산

반사대칭 아래 홀수 multipole을 제거하고 네 energy/number tower의
ell=0,2,4,6,8을 유지했다. elapsed time, b, s와 합쳐 기하는 23변수다.
원래 identically-zero gas placeholder도 이 부분공간에서 제거한다.

같은 원소의 isotope는 동일한 전하분율 f_Z를 공유한다. Y_A,q=I_A f_Z,q를
대입하면 비선형 electron feedback도 공통 계수로 남으므로 H의 2개,
He의 3개, Li의 4개, 총 9개 전하 좌표가 원래 21개를 복원한다.
여기에 optical depth 하나를 더하여 총 33개다.

고정 lift P와 restriction R로 RP=I이며,

\[
 f_{33}(v)=R f_{62}(Pv),\qquad
 J_{33}(v)=R J_{62}(Pv)P.
\]

원래 full62 source를 수정하지 않고 RHS와 analytic Jacobian을 투영했다.
출력에서는 full62 representation과 모든 21개 Y를 다시 저장한다.
해당 부분공간을 벗어나는 비영 n/T, isotope별 초기분율 차이, 홀수 초기
multipole 등은 guard로 거부한다. 다른 물리에서는 원래 full62 경로를
쓰거나 새로운 불변부분공간을 유도해야 한다.

적분 좌표는 46.77% 감소하고 dense Newton 행렬 원소 수는 3,844개에서
1,089개로 줄었다. 이는 행렬 크기의 대수적 감소다. 실제 wall time의 향상률,
전체 RSS 감소율 또는 64-core scaling의 측정으로 해석하지 않는다.

NumPy 배열의 운동량 합산, analytic Jacobian, 원자 계수 및 기존 BDF
solver를 재사용하고 독립 사례를 process 단위로 분산했다. 각 worker의
수치 라이브러리 thread는 1로 제한하여 nested oversubscription을 피했다.
완료한 case는 source/config/output hash로 검증하여 다시 적분하지 않는다.
마지막 기본 명령의 resume 검사에서는 127개를 모두 재사용하고
새 worker 0, 새 integration 0, RHS rerun 0을 확인했다.

## 6. 실제 sweep과 주요 결과

초기 좌표는 다음과 같다. P는 signed coordinate이며 Pi=|P|다.

- Sigma_F,0 = [0, 0.003, 0.03, 0.15, 0.6]
- P_m,F,0 = [-0.0005, -0.00025, 0, 0.0005, 0.001]
- P_r,F,0 = [-0.0012, -0.0006, 0, 0.0006, 0.0012]

이 5×5×5 격자에 S_F,0=0, (P_m,P_r)=(+0.0005,-0.0005)와
(-0.0005,+0.0005)를 추가했다. 모두 x=ln(a/a_ref)∈[0,ln7],
a_ref=1/21의 동일한 193개 저장 시점을 사용한다.

전체 시간 이력의 실제 범위는 Sigma_F∈[0,0.6],
Pi_m,F 최대 0.001, Pi_r,F 최대 0.001868530584,
Pi_total,F 최대 0.002305760975다. 큰 초기 shear의 감쇠와 작은 초기/생성
응력이 함께 보이도록 symlog를 사용했다. 실제 0은 그대로 남겼다.
127개를 faint trajectory로 그리고 대표 사례를 강조했다. 중간 값을
새로 적분하거나 smoothing한 그림은 아니다.

### 초기 응력 상쇄가 유지되지 않는 두 사례

| 초기 (P_m,F,P_r,F) | z=2 S_F | z=2 P_total,F | z=2 q |
|---|---:|---:|---:|
| (+5e-4,-5e-4) | -5.083173802e-5 | -5.437024582e-5 | 0.7377992759 |
| (-5e-4,+5e-4) | +5.082929661e-5 | +5.436537724e-5 | 0.7378080326 |

q=|P_m+P_r|/(|P_m|+|P_r|)다. 초기 q의 실제 값은 각각
2.1684043449710089e-16, 0이며 반올림을 강제로 0으로 바꾸지 않았다.
최대 |S_F|는 각각 약 6.0290e-5와 6.0289e-5다.
같은 zero-shear·zero-stress control의 최대 |S_F|는
3.18925667373614e-20이다. raw shear와 control 차이를 함께 저장·표시했다.

정규화 shear의 식은 S_F'=-(3+H'/H)S_F+P_m,F+P_r,F다.
따라서 초기 상쇄에서는 S_F'(0)=0이지만, massive 성분의 다른 redshift와
photon Thomson damping 때문에 다음 기울기는 일반적으로 0이 아니다.
초기 분리 가능한 P2 massive 분포의 J2≠0에서 beta_m=J4/J2라 하면

\[
 S_F''(0)=(\beta_m-1)P_{m,F}(0)
 -{9\over10}(\Gamma_T/H)_0P_{\gamma,F}(0).
\]

두 사례는 J2≠0이며 0≤beta_m≤1이다. 공통 H 정규화 미분항은 초기
P_m+P_r=0에서 사라진다. 이 국소 유도와 실제 장구간 결과가 연결되지만,
국소식을 전체 시간의 근사해로 대체하지 않았다.

### 채택 원자망에서의 z=2 상태

등방 zero-seed control에서 다음 전하분율을 얻었다. 같은 원소의 isotope
분율 동일성은 채택한 전자율 동일성의 결과다.

| 원소 | I | II | III | IV |
|---|---:|---:|---:|---:|
| H1/D | 2.20672346e-6 | 0.9999977933 | — | — |
| He3/He4 | 1.46510980e-9 | 3.731343884e-4 | 0.9996268641 | — |
| Li6/Li7 | 1.58219324e-12 | 2.86207157e-6 | 0.008262602344 | 0.9917345356 |

Li6와 Li7의 absolute abundance는 초기 inventory가 다르므로 서로 다르다.
그림은 각 isotope inventory에 대한 전하분율이고 CSV에는 actual Y도 있다.
n/T의 inventory는 0이므로 분율은 정의되지 않으며, 해당 panel은 actual Y=0을
그린다. 전체 history에서 음의 Y는 0개이고 isotope 보존 상대잔차의 최대는
2.5132031881233213e-15다. 전체 tau_T(z=2)는 0.0692155866–0.0693407679이지만
이 역시 지정 광원·온도의 모형 결과이며 관측에 맞춘 추론값이 아니다.

## 7. 검증과 실행 중 수정

BDF rtol=2e-8, geometry atol=2e-11, scaled-ion atol=2e-10,
tau atol=2e-11, max_step=0.025를 고정했다. gate 문장은 원래 source와 AST가
같다. 127개 사례에서 13개씩 1,651개 gate가 모두 통과했고 추가 oracle
26개 gate도 통과했다. population positivity, isotope/baryon 보존,
electron 비음수, number monopole, optical depth, tensor sum, 유한 angular
positivity, interval/finite, trace-energy 조건 등을 확인했다.

Einstein constraint 검사는 정의한 대수적 H의 일관성이다. 독립적인
Einstein ODE 잔차 검증이나 연속계 수렴으로 해석하지 않는다.
최대 대수 constraint residual은 5.866434692e-16,
최대 trace-energy/critical-density 진단 비는 2.194064210e-8이었다.
이 비의 작음을 생략한 전체 물리항의 오차 상계로 사용하지 않는다.

| full62 대조 사례 | signed observable 최대 절대차 | isotope fraction 최대 절대차 | tau 최대 절대차 |
|---|---:|---:|---:|
| high corner s04_m04_r04 | 1.207536973e-9 | 2.090016532e-8 | 4.304209766e-11 |
| cancel_positive_matter | 1.045091176e-10 | 2.928706702e-8 | 1.319341858e-11 |
| 실행 전 고정 수용 한계 | 3e-7 | 3e-5 | 3e-7 |

Finite-state lift RHS 잔차는 8.8818e-16, projected Jacobian의 방향 유한차분
잔차는 6.2537e-9였고 각각 고정 한계를 통과했다. 두 전구간 대조는
구현의 동등성 근거이며 momentum/ell/time/atomic-model 수렴 입증이 아니다.

첫 실행의 127개 수치 배열은 끝까지 생성되었으나 마지막 JSON 저장에서
NumPy bool의 직렬화가 실패했다. 원본을 results/pilot에 보존하고 NumPy
scalar만 Python native scalar로 바꾸는 출력 adapter를 수정했다.
동일한 물리와 허용오차로 results/pilot_v2에 재실행해 모든 완료 영수증을
검증했다. donor 57개 파일은 수정하지 않았다. 이전 raw 33,131,538바이트는
로컬 보존이며 A/B/C에 중복하지 않고 실패 로그·receipt를 함께 보존한다.

현재 physical source base:
ee7e9ae76c852079ce86cdd5165624ab2b7fc7a9c672016501ed5da5fb4341d3

그림의 571개 line artist와 250개 discrete sweep point가 실제 저장 배열과
일치했다. CSV 모든 열의 값과 NPZ도 정확한 round-trip을 확인했다.
PNG 네 장과 PDF 네 장을 시각 검사했다. 단계 B/C의 README 및 실행 코드는
authoritative pilot_v2를 가리킨다.

## 8. 가용 자원과 NCP 이식

실제 본 실행 환경은 CPU quota 8, affinity 9, memory limit 8 GiB였다.
실행 계획 표본에서 memory available은 7,634,104,320 bytes(약 7.11 GiB),
현재 cgroup CPU 사용은 약 0.133 core, affinity idle은 약 8.589 cores였다.
이는 그 측정 순간의 headroom이다. 본 sweep은 worker 4개, worker당
수치 thread 1개를 사용했다.

마감 중 2026-10-21 16:02 UTC의 read-only 계획 확인에서도 quota 8 CPU /
8 GiB였고, 가용 메모리는 7,806,840,832 bytes(약 7.27 GiB), CPU reserve
적용 뒤 표본 headroom은 약 6.998 core였다. 이 관측은 실제 적분을 추가하지
않았다. evidence/FINAL_RESOURCE_SNAPSHOT.json에 원값과 시각을 보존했다.

dispatcher는 host load average를 단독 중지 근거로 쓰지 않는다.
실제 cgroup CPU usage delta, affinity 내 idle, memory available, CPU
reserve와 peer reservation을 함께 사용한다. 이미 관측된 사용량과 peer
reservation을 이중 차감하지 않는다. 다른 세션이나 작업을 종료하지 않는다.

NCP target 64 CPU / 128 GiB는 사용자 목표다. 이 대화에서 그 서버의 live
가용량을 직접 측정한 것은 아니다. NCP에서는 --workers auto --max-workers 63
상한을 줄 수 있지만, 실제 affinity/cgroup/memory와 기존 작업을 관측한
admission 결과만큼만 시작한다. 현재 작업의 완료 데이터를 재사용할 때는
새 적분 자체가 필요 없다. 상세 scaling benchmark는 수행하지 않았다.

## 9. 결과 파일과 단계별 전달

그림은 다음 네 종류이며 모두 PNG/PDF가 있다.

1. figures/time_evolution_sigma_pi: Sigma, Pi_m, Pi_r, Pi_total의 127개 시간 이력.
2. figures/isotope_ion_fractions: 21개 상태와 동위원소별 전하분율.
3. figures/cancellation_time_evolution: 두 상쇄 사례의 signed 성분, shear, q.
4. figures/parameter_sweep_slices: 다섯 초기 shear의 실제 5×5 격자 endpoint.

results/analysis/all_histories.csv.gz는 24,511행,
all_histories_plot_source.npz는 대응 배열,
endpoints.csv는 마지막 시점 요약이다.
모든 개별 trajectory.npz는 33변수와 복원 full62, 실제 Y, 두 정규화,
진단 배열 및 원래 initial62를 가진다.

| 단계 | 이번 내용 | 실제 게시/백업의 권위 있는 기록 | 다음 단계 |
|---|---|---|---|
| A | intake, 축약 유도, finite verification, 고정 모델 | delivery/STAGEA_PUBLICATION.json, STAGEA_BACKUP.json | B 실제 실행 |
| B | serializer 수정, 127+2 실행, paired/plot evidence snapshot | delivery/STAGEB_PUBLICATION.json, STAGEB_BACKUP.json | C 독립 검토·전달 |
| C | 전체 성공 raw, 그림, 보고서, handoff, 최종 판정 | delivery/STAGEC_PUBLICATION.json, STAGEC_BACKUP_VERIFIED.json, FINAL_PUBLICATION.json | 사용자가 지정할 다음 물리 범위 |

두 저장소의 branch는 research/rei-hheli-compact-pilot-20261022다.
BASS PR https://github.com/cosmosapjw-quantum/bass/pull/180
REI PR https://github.com/cosmosapjw-quantum/rei_bianchi/pull/220
이전 ACCEL03 branch 위에 쌓은 draft이며 merge하지 않았다.
A/B snapshot은 immutable이고 C의 실제 hash/ACK는 delivery를 따른다.
세 loop의 30개 노드별 진행·게시·백업·다음 단계는 DAG.json과 LOOP_RECORD.json에 있다.

재개할 때 CODEX_HANDOFF.md와 NEXT_THREAD_HANDOFF.md를 사용한다.
완료 raw를 먼저 확인하고 source/config/output identity가 같은 사례는
재적분하지 않는다. 물리를 확장할 경우 기존 계약과 결과를 덮어쓰지 않고
새 contract와 출력 경로를 만든다.

## 10. 다음 물리 범위의 우선순위

지금 완성한 것은 이 샌드박스에서 끝까지 실행 가능한 retained-model
preliminary sweep이다. 후속 연구에서는 먼저 이번 지정 T/UV의 역할을
분리할 수 있는 thermal/radiative energy 교환식을 정하고, 필요한 CI/CX,
secondary-electron, 분자 및 isotope-specific correction을 결정해야 한다.
각 추가 반응의 에너지·전하·핵종 장부와 유효 온도 범위를 정한 뒤 코드에 넣는다.

그 다음 ell/momentum/time/atomic-rate의 각각에 대한 수렴 또는 오차
예산을 검사한다. 모델을 바꾸면 33차원 불변부분공간의 적용 여부를 다시
판정한다. 비영 n/T, 핵종 전환 또는 isotope-specific dynamics를 넣는
경우 지금의 isotope 축약을 그대로 사용할 수 없다. 일반 비-LRS와
full Q^a closure는 별도 계약이 필요하다.

이번 루프는 위 후속 물리의 완료를 주장하지 않으며, 그 후속 실험을 지금
불필요하게 실행하지 않는다. 이미 완료한 127개 및 두 oracle가 다음 연구의
고정 비교 자료다.

## 원전과 내부 근거

- [Verner photoionization and partial-shell source](https://www.pa.uky.edu/~verner/photo.html)
- [Verner–Ferland recombination source](https://www.pa.uky.edu/~verner/rec.html)
- [Badnell RR data and units](https://amdpp.phys.strath.ac.uk/tamoc/DATA/RR/)
- [Badnell DR data](https://amdpp.phys.strath.ac.uk/tamoc/DATA/DR/)
- [ACROPOLIS photodisintegration framework](https://arxiv.org/abs/2011.06518)
- [TUNL Li6 evaluation, alpha+D threshold](https://nucldata.tunl.duke.edu/nucldata/HTML/A%3D6/06Li_2002.shtml)

외부 원전은 물리식·계수·문턱을 지원한다. 이번 실제 결과 수치의 근거는
본 저장소의 고정 raw와 receipt이며 외부 문헌의 실험 결과로 인용하지 않는다.


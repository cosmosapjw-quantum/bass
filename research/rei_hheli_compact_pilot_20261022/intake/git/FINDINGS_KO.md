# ACCEL03 이후 최신 Git source 조사

## 직접 재사용할 코드

`rec_bianchi` PR119, `research/rec-rei-hheli-sandbox-20261021`, commit
`a949529872eb5ba0e20c7e206fe893e5d544e48c`가 이번 요청에 가장 가까운 실행 가능한
기증 코드다. `sources/rec_bianchi/research/rec_rei_hheli_sandbox_20261021/`에
57개 파일, 455,989바이트를 회수했다. 코드·입력·계수·upstream license·검증 결과와
독립 검토를 포함한다. 전체 회수 파일의 Git blob 동일성은 `SOURCE_MANIFEST.json`에
있다. 새 코드를 작성하기 전에 이 실행 경로를 읽어 현재 승인 단위에 연결할 수 있다.

현재 donor DAG의 실제 상태는 `D_COUPLED_CODING_READY_FOR_FIRST_CASE`와
`E_NEW_PILOT=READY_NOT_RUN`이다. 게시된 소스가 있는 사실을 새 전구간 결과 완료로
표현하지 않는다. 최종 production 전에 해당 ref의 후속 실행 반환을 한 번 확인할 수 있다.

### donor 물리 계약

- 핵종 n, H1, D, T, He3, He4, Li6, Li7 및 각각 전하 0..Z: 21개 heavy states.
- 광이온화와 RR/DR를 동적으로 적분하고, 실제 전자밀도가 CMB Thomson 산란에 들어간다.
- isotopic electronic equality를 명시적으로 사용한다. 정확한 isotope-dependent atomic fit이 아니다.
- T(z)=100+11900 Q K, Q=[1+tanh((7-z)/0.8)]/2인 지정 온도, UV 5–200 eV의 E^-2.5 number spectrum,
  late Gamma_HI=1e-12 s^-1이다. UV는 외부 등방·광학적으로 얇은 reservoir다.
- 바리온은 등방 이상기체 pi_b=0, 독립 collisionless 비바리온 성분이 pi_m을 공급한다.
  pi_r=pi_gamma+pi_nu, photon에만 Thomson 감쇠가 작용한다.
- 바리온 thermal/ionization와 UV 에너지는 test-fluid 처리하며 실제 에너지 비율과 순외부 열장부를 저장한다.
- n/T 초기량은 0이다. 약붕괴 maps는 구현되어 있지만 본 pilot의 실제 flux는 0이다.
- CI/CX/음이온/분자/핵융합은 제외한다. 지정 200 eV UV에 의한 MeV 문턱 광핵반응은 활성화되지 않는다.
  따라서 이것은 해당 선택된 number-network 모형의 실제 coupled pilot이며 전체 광핵·열폐쇄 결과라는 주장은 하지 않는다.
- Frobenius convention: Sigma=sqrt(6)|s|/H, Pi=sqrt(6)kappa_t|p|/H²,
  sigma=diag(-s,-s,2s), pi=diag(-p,-p,2p), kappa_t=8piG/c² for SI energy stress.
  원 warm729의 half-contraction convention과 sqrt(2) 대응을 유지한다.
- donor grid: Sigma=[0,.003,.03,.15,.6], signed Pm=[-.0005,-.00025,0,.0005,.001],
  signed Pr=[-.0012,-.0006,0,.0006,.0012], 125 cases, 193 epochs z20→2.

`BASS_HE` PR85 HE32, commit `e8bb035d31f59e34734947b9082bdbd60128b799`는
반사짝수 Legendre 부분공간으로 L8 state 40→23을 정확히 줄이는 compact transport를 게시했다.
홀수 영모드와 gas-energy 영 placeholder를 제거하며 angular cutoff를 낮춘 근사가 아니다.
vendor FV/mass-shell kernel, 원 source lock, 독립 최적화 검토를 함께 회수했다.
그 단위는 최적화 O.C1–C10 완료, physics P.R1 이후 pending이다.

## 전수 ref 조사와 새 결과

owner catalog 51개를 조회하고 직접 관련 7개 repo의 모든 advertised branch 이름/head를
terminal empty page까지 읽었다. 7개 repo 합계는 1,249개다. 이 범위는 브랜치 ref의 전수이며
각 브랜치 모든 파일 본문의 전수를 뜻하지 않는다. 관련 본문·실행기·입력은 선택 회수했다.
개인 대화·원격 NCP 전체 파일시스템 접근은 이 조사에서 주장하지 않는다.

| repo | branch heads | 주요 변화 |
|---|---:|---|
| bass |264|ACCEL03 draft179 완료 head 유지|
| rei_bianchi |258|PR199 D9가 cce008b3…로 전진; ACCEL03 draft217 유지|
| bass_cr |172|C21N offgrid4 sandbox 및 같은4 NCP 반환 완료|
| BASS_HE |90|새 HE32 optimized compact transport|
| WU088_HH |142|PHYS78 nuclide branch는 PHYS77과 동일 head|
| rec_bianchi |137|새 PR119 HHeLi coupled sandbox source|
| vigilode |186|이전 ACCEL03 census 대비 ref 변화 없음|

원 ACCEL03 4-repo census 876 refs 대비 4개 추가, 1개 변경이며 삭제는 없다.
추가된 BASS/REI ACCEL03 두 브랜치는 바로 이 대화의 직전 완료 결과이고,
나머지 두 추가는 C21N offgrid4 sandbox/evidence다.

REI D9는 기존 175개×153 epochs 저장 궤적에서 성분별 integrating-factor shear budget을
계산했다. 최대 scaled residual 1.473444875767401e-6, 기준 2e-5, D8 brackets4를 재사용했고
새 IVP/ODE/moment recomputation은 0이다. 후속 D10은 zero-initial matter-stress generation의
이론·저장자료 intake로 지정되어 있다. 새 HHeLi chemistry donor로 중복계수하지 않는다.

C21N PR95의 실제 branch ref는 `8dc5031b3323d4be42a7444843294200aa8887f2`이고
PR API head는 과거 content `e7729092abc6edbe74f31d0ed82aa84d5506b8d5`를 반환했다.
이 알려진 metadata 지연을 보존한다. Sandbox4와 NCP4는 같은 입력이며 기존125와 합친
고유 입력은129다. 구간 z20→4, collisionless lineage이고 full chemistry z20→2가 아니다.

## 핵반응 소스와 남은 연결

추가 `toy_bbn` main `908c24e478384912b0c547aade5e209b7ec2695f`의 tree와 두 branch를 읽고
`minimal_bbn_rates.py`, `minimal12_reaclib20090121_coeffs.json`, README, third_party를 회수했다.
REACLIB20090121의 np capture, Dp, DD 두 갈래, TD, He3D, He3n, T-alpha→Li7 등
그림12–19에 관련된 원 coefficient가 있다. BBN용 fit의 cold IGM 온도 범위 정확성은
이 intake에서 입증하지 않았으므로 해당 fit을 100–12000 K에 자동 외삽하는 근거가 아니다.
현재 물리 단위가 원자망보다 넓은 핵반응 활성화를 택하면 저온율·threshold·daughter charge 및
에너지 전달 계약을 source별로 연결해야 한다.

REI PR211 RUN19 `c9deb933…`와 PR151 `8a4f5df…`는 기존 pinned source를 유지한다.
REC119 donor가 그 Li RR/DR와 PH1/PH2 광흡수 source를 이미 인용·보존하므로
동일 자료를 다시 구현하는 것보다 기존 source와 검증의 적용범위를 재사용할 수 있다.

## 정책·실행 상태

현재 REI AGENTS blob은 `429a5a13ee75b1222bc50627f8d5973d01dd21c4`이며 기존과 동일하다.
기존 checkout 보존, trusted scientific owner, Astra 계약→lower-tier 구현→fresh Astra 검토,
수치동등성과 byte동일성 구분 정책이 적용된다. 이 intake는 읽기 전용이며 새 ODE·benchmark·NCP·
Git mutation·외부 게시를 실행하지 않았다. 원 Git source body의 회수와 로컬 저장만 수행했다.

근거: `CURRENT_BRANCHES.json`, `BRANCH_DELTA.json`, `LATEST_DELTA.json`,
`SOURCE_MANIFEST.json`, `sources/`의 source-pinned 파일.

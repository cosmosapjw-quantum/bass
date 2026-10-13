# FA-01: 유한 observer cap의 편극 관측

2026-10-14. 원래 Loop10의 21개 단위와 D9.1 통합 완료를 유지한 후속 연구다. 새 결과는 derived / symbolically checked / numerically checked / owner-reviewed이며 외부 독립 심사는 미실행이다.

## 모형과 결과

Exact Kasner p=(2/3,2/3,-1/3), x=t/t_o in [1/2,1], observer e1 cap delta<=0.02 rad, 고정 [0.98,1.02] E_star 대역을 사용한다. Source tensor는 첫 행·열이 0이고 2:3 부분이 [[.7,.1+.05i],[.1-.05i,.3]], absorption은 diag(.4,.4,.8), rotation은 .3(e1 dot e)J_e다. 모든 pixel에서 e2를 screen에 투영한 동일한 물리 analyzer로 읽는다.

Ray, parallel screen, Doppler 및 analyzer의 angular derivative를 포함하여

`mean S(delta) = S(0) + a_delta Laplacian(S)(0) + R`,
`a_delta = <r^2>_cap/4 = delta^2/8 - delta^4/288 + O(delta^6)`

를 유도했다. 새 선형 response IVP에서 (I,Q,U,V)의 중앙 Laplacian은

`(-0.886660466649076, -0.5994860147348973, -0.012540565782918747, 0.07649655868280515)`

다. Complex meridian |z|<=.4의 실제 denominator/generator majorant와 Cauchy estimate로 real cap의 fourth directional derivative를

`M4 = 24*1.61/.38^4 = 1853.116535324315`

로 제한했다. Uniform matrix trace-norm remainder는 `1.61/.38^4 * <r^4>_cap`다. 이 상계는 sampled derivative maximum이 아니다.

| delta rad | 직접 cap I | 첫 보정 후 잔차 | 균일 상계 |
|---|---:|---:|---:|
| .005 | .495489534501404 | 1.40308e-11 | 1.60861e-8 |
| .010 | .495481222225945 | 2.24487e-10 | 2.57376e-7 |
| .020 | .495447975121099 | 3.59183e-9 | 4.11797e-6 |

두 정밀도 직접 각도 계산의 차이는 약1.1e-14 이하였다. 이 수치는 제한된 수렴 비교이며 interval-certified continuum run을 뜻하지 않는다. 새 Wolfram angular checks와 xAct cap-moment/screen contractions를 실행했다.

실제 observer rapidity .02, 같은 새 observer cap .02와 energy band에서는 I=.496542952394109다. Aberration boundary, angular measure, energy Doppler와 analyzer Lorentz/null-gauge map을 모두 포함한다. Normal-cap uniform bound를 이 observer 전체 family에 자동 승계하지 않는다.

## 전체 판본과 백업 identity

Full package: BASS_ALL_BIANCHI_FA01_20261014.zip
Size: 86249135 bytes
SHA256: cf94dc4c1be524ba0eb21531cf56a61c32b8fd9f5b483bb68bcd38e2f336c239

404쪽 갱신 합본, 7권, 새 LaTeX, 771개 canonical 식, 보존 Loop10·postreview와 이번 전체 코드·입력·반환을 포함한다. 동일 ZIP의 Dropbox 및 Google Drive 업로드는 completed/succeeded 응답과 크기로 확인했다. 전체 archive는 계정의 BASS_DERIVATION_DOSSIERS_20260912 폴더에 보관한다. 새 공개공유 권한은 만들지 않았다. Remote restore는 별도로 실행하지 않았다.

이 Git 브랜치는 새 연구 요약·복구 identity·재현 계산·다음 실행문만 추가한다. 기존 main이나 물리 solver를 변경하지 않는다.

## 고정 계약과 다음 연구

SOURCE_CLOCKS.json SHA256: 3a1ac8baa12b612eec855fe78a986aca6db577d5625deab952836e2ccd421d8a
ABUNDANCE_MODEL.json SHA256: 592c2243a6032b75111fb205ea3e103b229f48194d984e3216b2eb5c74ac9098

같은 microscopic event의 R,Q, ABF kappa_s와 full collision derivative, DC*r, admissible Bianchi/VI_-1/9, physical tilt/passive boost, H=0를 유지한다. 숫자는 지정한 Kasner 모형이며 empirical provider errors는 null이다. F-ADT-FRAME-01의 amended S23이 문턱 설명의 현재 원고이고 ADT.1–15는 변경하지 않았다.

다음 FA-02는 finite observer rapidity/pointing의 first/second cap variation과 uniform remainder다. 변경 없는 PNS/AP/F-N-STIM campaign은 반복하지 않는다.

재현: Python, NumPy, SciPy가 있는 환경에서 `python docs/theory/dossier_fa01_20261014/runtime/fa01.py`. 전체 유도와 검산·조판은 위 해시의 full package에 있다.

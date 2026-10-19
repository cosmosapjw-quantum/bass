# S7 native cohort·수송·흡수 검증

## 범위와 실행 전 계약

이 경로는 고정 REI owner `0e25846433170d0f420c4cda44a0bedbf02cd177`의
`AxbiSource`, `CovariantTransport`, `AtomicProvider`를 무변경 컴파일한다.
S3 native adapter, P2/P24 알고리즘, S6 검증을 수정하거나 다시 실행하지 않는다.
새 실행 입력과 gate는 `evidence_s7_native/PREREGISTRATION.json`에 고정하고,
그 파일과 구현의 게시 readback 뒤에만 캠페인을 실행한다.

물리는 non-tilted axisymmetric Bianchi I, signature `(-,+,+,+)`,
`a_perp=a exp(-b)`, `a_parallel=a exp(2b)`, `s=dot b`,
`Sigma=sqrt(3)|s|/H`를 유지한다. 여기의 기하는 처방된
`a=exp(x)/21`, `b=b0+0.2x`, `H=1e-16 s^-1`이다.
Einstein 결합 native 이력이나 반응성 EoR 이력을 실행했다는 뜻이 아니다.

## 1. 실제 owner 이력과 출생 조건

출생 `u∈[0,0.8]`에 midpoint quadrature를 쓰며,
`z=21 exp(-u)-1`, `dt=du/H`를 owner `AxbiSource::at_redshift`에 넣는다.
모든 출생은 원래 50,000 K source cell과 원래 photon fraction을 사용한다.
새 locally isotropic source의 birth angular weights만 prior/P2/P24 중
지정된 방법으로 정한다. 이미 생성된 cohort의 reference-energy cell,
number, support, weights는 이후 기하 관측과 흡수 reference 계산 동안 고정한다.

기존 anisotropic stock은 반사 대칭인 극 방향 두 ray에 각각 `q=5 eV, N=0.0025/H`,
적도 근처 두 ray에 각각 `q=40 eV, N=0.001/H`인 별도 delta population이다.
기존 stock을 재가중하지 않고 매 새 birth를 실제 adapter로 더한다.
영향받지 않은 cell은 bitwise 같아야 하며, P2/P24에서는 전체 cell이
`old + independently formed birth`와 정확히 같아야 한다.
원래 prior injector는 source panel을 순서대로 더하므로 합의 결합순서에 따른
반올림을 별도 상대 ledger gate `1e-11`로 검사한다.

## 2. Per-H 양과 물리적 밀도

Owner의 inventory는 photon/H 및 eV/H이다. 무충돌에서 N/H는 일정하고

\[
 U_H(x)=\sum_k U_{H,k}(u_k)e^{-(x-u_k)}
         \sum_i \alpha^E_{ki}R\bigl(0.2(x-u_k),\mu_{ki}\bigr),
\]

\[
 \Delta P_H(x)=\sum_k U_{H,k}(u_k)e^{-(x-u_k)}
         \sum_i \alpha^E_{ki}D\bigl(0.2(x-u_k),\mu_{ki}\bigr).
\]

여기서 `alpha^E`는 출생 직후 실제 native ray energy를 정규화한 측정값이며,
원래 angular `alpha`와 별도로 저장한다. Python은 이 기록을 읽어 native
관측값을 독립 계산한다. 출생 사이에는

\[
 U_H'+U_H+2b'\Delta P_H=0.
\]

물리적 밀도는 `U=nH0/a^3 U_H`이므로 `U'+4U+2b'ΔP=0`이 된다.
Native per-H inventory에 `a^-4`를 직접 곱하지 않는다.
Native 기하 평가의 5점 미분(`h=1e-3`, `5e-4`)으로 연속식을 검산한다.

## 3. 오차 분리

총 51개 입력은 같은 물리적 설정을 중복 실행하지 않는다.

| 축 | 고정한 것 | 바꾼 것 |
|---|---|---|
| Angular | K=16, bin=96, panel/segment=32 | n_mu=8/16/32; prior/P2/P24; b0=0/0.6/0.9 |
| 출생시간 | n_mu=16, bin=96, panel=32, b0=0 | K=8/16/32/64/128; prior/P2/P24 |
| 흡수 bin | n_mu=16, K=16, P24, panel=64 | bin=24/48/96/192 |
| 흡수 panel | n_mu=16, K=16, P24, bin=96 | panel=8/16/32/64 |
| 흡수 이력·angular | 기준 slab와 나머지 축 고정 | K=8/16/32 및 n_mu=8/16/32 각각 |
| 큰 b 실제 흡수 | n_mu=32, K=16, P24, bin=96, panel=64 | b0=0.6, 관측 b=0.8 |

동일한 출생시간 grid에서 isotropic continuum angular kernel(GL256)과
비교한 `δA`가 angular 오차다. 별도로 같은 finite angular rule을
출생시간 GL96/192로 적분하여 native midpoint 이력의 수렴을 검사한다.
P24의 feasibility 실패는 실패한 첫 birth와 실제 mu support,
독립 mean/lower/upper hull 판정과 함께 남긴다.

## 4. 실제 finite-bin 흡수와 독립 spectrum 기준

관측 시점 `x=1`에 한 번, 고정 opacity와 원래 owner backward-Euler
survival operator를 적용한다. `dt=1e12 s`, `nH=nH0/a^3`,
`(nHI,nHeI,nHeII)=(0.01,0.005,0.002)nH`이다.
흡수율·원자수·열 이력의 자체 결합은 이 실험에 포함하지 않는다.

한 경로는 모든 cohort를 native finite-bin 두 moment 상태로 합친 뒤
`prepare/evaluate`한다. 다른 경로는 같은 operator를 각 cohort에
따로 적용한 뒤 더한다. 두 결과의 차이는 합쳐진 spectrum의 closure 손실이다.
세 번째 독립 기준은 출생 source cell의 원래 연속 blackbody shape를
고정 birth alpha와 함께 직접 적분한다. 원래 photon fraction/GL8 source
normalization과 원래 `AtomicProvider::cross_section`을 그대로 사용하고,
현재 물리적 threshold가 출생 energy에서 위치하는 곳마다 적분 구간을 나눈다.
GL32/64의 차이를 별도로 기록한다.

숫자와 에너지 ledger는 각각
`N_before-N_after-sum(absorbed)` 및
`U_before-U_after-binding-heat`를 검사한다. 기존 gate는 `1e-11`이다.
반응 이후 spectrum의 정확도는 ledger 보존만으로 승인하지 않는다.
별도 탐색 목표는 bin192에서 `|δN|/N_before`, `|δU|/U_before≤1e-4`,
큰 b의 n32 P24에서 `|δA|≤1e-6`이며, 미달하면 실패 그대로 남긴다.

## 5. 실행

NCP의 일반 git checkout에서는 연구 경로에서 다음 명령을 그대로 쓴다.

```bash
python3 run_native_cohorts.py \
  --out /absolute/scratch/bass_s7_native_run \
  --workers 4 --timeout 1800
```

기존 REI checkout이 있으면 `--rei-repo /absolute/rei_bianchi`를 더한다.
57개 owner 파일을 이미 갖고 있으면 `--owner-root /absolute/exact_owner`를 쓴다.
Compiler가 PATH에 없으면 `--rustc /absolute/rustc`를 지정한다.
Owner commit/file blob/SHA256는 자동 검사한다. 사전등록이 git에 clean하게
게시되지 않았으면 실행을 거절한다. API 기반 workspace에서는 실제 원격
readback의 repo/path/commit/blob/SHA256를 담은 `--publication-receipt`를 허용한다.

최대 추가 worker 16, RAM 16GiB, 출력 disk 4GiB, 개별 job 1800초다.
이 실험은 native thread 1, owner staging worker 4를 기본으로 한다.

## 실행 상태

캠페인 실행 전. 새 Rust cohort 테스트 5개와 Python evidence guard 11개의
개발 검증 후 사전등록 게시를 기다린다. 실제 실행·실패·자원 기록은
`evidence_s7_native/`의 immutable receipt에 추가한다.

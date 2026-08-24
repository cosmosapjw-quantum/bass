# 선행 부채 해소 + 코드 이식 (v1.4, 2026-07-29)

v1.3 적대적 감사가 남긴 "정직한 잔여 구멍" 3건을 해소하고, 좌표기저 독립검산을
저장소에 정식 이식했다.

## 부채 A — D22 vorticity: "결함"이 아니라 오개념이었다

v1.2/v1.3 은 유체 vorticity 가 v̇ 에 의존하는 것을 구현 버그로 라벨했다. **틀렸다.**

- 완전 투영 ω_μν = h_μ^α h_ν^β ∇_[β u_α] 은 −u_β a_α 항을 죽이지만(h_ν^β u_β=0),
  v̇ 는 **투영된 부분**(유체 자신의 팽창·shear·vorticity)에도 들어간다. 따라서
  off-shell ω 는 v̇ 에 **실제로 의존**한다 — 이것은 물리다.
- 해소: 관측량은 **on-shell** vorticity 다. 운동량 보존이 유체 가속도를 v 에 평행하게
  만들고(잔차 1.8e−10), 그러면 공간 vorticity 는 **EOS-무관**(4.9e−11), u-직교
  (3.9e−16), 반대칭, v=0 소멸의 깨끗한 관측량이 된다.
- 이전의 mixed-지표 투영 버그(h^d_b 로 짜서 투영이 자명해짐)도 완전 투영형으로 교체.
- 산출물: `audit/d_vorticity.py`, 게이트 5개.

## 부채 B — CS(II) tilt 축소 {v2,v3} 의 완전성 증명

CS(II) 에서 tilt 선형화는 기하와 분리되어 고윳값:
- v1: 3(5γ−6)/4 (교차 6/5)
- v2=v3: 3(7γ−10)/8 (교차 10/7), 해석식과 8.9e−16 일치.

순진하게는 v1 이 먼저(6/5) 불안정. **그러나 v1 은 운동량 구속으로 금지**: 유형 II 는
기하 운동량 G_01 = ε_1bc n_bd σ_c^d = 0 (n=diag(N1,0,0)) 이라 Codazzi C1 = q1 =
3γΩ v1 = 0 → v1=0 (∂C1/∂v1 = 3γΩ ≠ 0, 확인). 물리 임계값은 **10/7** 이고 기하
섹터는 2/3<γ<2 전체에서 sink. 산출물: `audit/d_tilted_II.py`, `thresholds.
cs_II_v1_unconstrained_eigenvalue`, 게이트 4개.

## 부채 C — core.connection3 지표순서 핀

audit 코어의 공간 접속은 Γ^c_{ba}(미분 슬롯 마지막)로, 프레임 엔진의 전치.
외부 소비자 둘 다 대칭 이중축약 P_a=Γ^a_{bc}v^b v^c 에서만 써서 순서 무관.
규약을 docstring 에 명시하고 import 시 S^3 앵커(Ric=2δ, R=6) assertion 으로 핀 —
지표순서가 드리프트하면 즉시 실패.

## 이식 — 좌표기저 독립검산을 저장소에

`bianchi/` 도 프레임 엔진도 import 하지 않는 좌표기저 검산(exp(xM) 실현 + JAX
자동미분)을 `audit/independent/` 로 이식하고 러너 `run_independent.py` 추가:

- partA 구조상수 재판독·Jacobi, partB 프레임 읽기, partC 측지선 전송,
  partD Maxwell curl +ε(1.7e−16 vs 구부호 0.11), partE 회전 프레임 +(R×P) 확인.
- **자기일관 게이트의 공통모드 맹점에 대한 구조적 해답**: 엔진을 속이는 오류가
  엔진을 안 쓰는 검산은 못 속인다.
- 5/5 통과, `independent_manifest.json` 생성.

## 최종 상태

```
pytest              : 138 passed   (v1.3: 134; 신규 debt 테스트 4)
audit/run_all.py    : 72/72 gates  (v1.3: 63; 신규 debt 게이트 9)
audit/independent   : 5/5 parts
```

남은 것(정직): 좌표기저 검산은 아직 단일 알제브라(VI_h flavor) 1점 실현 — 다형
확장은 PR-45 코드생성 단계에서. D22 on-shell vorticity 의 심볼릭 닫힌형은 고차-v
구조라 PR-42 로 이연(솔버는 RHS 의 v̇ 를 넣어 수치로 계산).

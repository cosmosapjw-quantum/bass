# PR 구현 현황

| PR | 내용 | 상태 | 완료 기준 검증 |
|---|---|---|---|
| PR-01 | scaffold + x64 | ✅ | `test_pr01_scaffold` |
| PR-02 | `symbolic/frame.py` 유도 엔진 | ✅ | L0~L4 사다리 (`test_L0`~`test_L4`) |
| PR-03 | `conventions.py` (함정 4종) | ✅ | 9배 함정 검출, Σ 타입분리, 게이지 3회전 |
| PR-04 | `algebra.py` 분류기 | ✅ | 12개 유형, κ 두 경로 일치, 회전 불변 |
| PR-05 | `symbolic/oracles.py` | ✅ | **커널 오염이 A 통과 & B·D 검출**을 테스트로 박제 |
| ~~P0.5~~ | ~~HW93 원문 확보~~ | 삭제 | 유도로 이미 종결 |
| PR-06 | class A 차트 | ✅ | Kasner 원, N_i=0 정확보존, 유형보존 |
| PR-07 | class B 차트 (κ) | ✅ | (b3,c2,c)=(−4,2,6) 재유도, Codazzi 전파, 유형 V 2차원 |
| PR-08 | 예외형 VI\*₋₁/₉ | ✅ | g′ 항등, K=N₋²+4A², A 2배환산 없음, 5 params |
| PR-09 | `integrate.py` | ✅ | scipy Radau/LSODA/DOP853 대조, throw=False, vmap |
| PR-10 | Tier2 정확해 | ✅ | Kasner, CS(II) **Σ₊=(3γ−2)/8**, Heckmann–Schücking, I+Λ, Collins VI_h |
| PR-11 | Layer 0 `general.py` | ✅ | S³ 앵커, class A RHS·궤적 일치, 구속 0 |
| PR-12 | `constraints.py` 투영 | ✅ | 지수증폭 억제 실증 |
| PR-13 | Tier3 교차검증 | ✅ | Layer0↔Layer1 (PR-11 테스트에 포함) |
| PR-14/15 | tilted 유체 | ✅ | **Ω′ 분모 G₊**, V=0·V=1 불변, γ=4/3 전환, 가드 2종 |
| PR-16 | tilted class B (Hervik) | ✅ | Codazzi 비 −3, 회전 3개, Σ₂₃′ 계수 2√3, Σ₊′ 회전항 |
| PR-17 | γ 임계값 | ✅ | 14/9 포함, 6/7 금지, Σ₊·h 의존 함수 |
| PR-18 | 다중 유체 | ✅ | 상대운동 → 비대각 응력 실증 |
| PR-19 | 스칼라장 | ✅ | 보존 항등식, no-hair 등방화 |
| PR-20 | 자기장 | ✅ | EMT 구조, 제약이 유형 V 에서 B=0 강제 |
| PR-21 | Bianchi IX D-차트 | ✅ | G′ 전파(trace-free 필수), **재붕괴 통과** |
| PR-22/23 | 배치 하네스 | ✅ | 메모리 7.2GB 재현, 발산 낭비 6.9배, 청킹 |
| PR-24 | Rodas5 독립구현 | ⏸ 선택 | diffrax Kvaerno5 로 충분. GPL 회피 위해 미착수 |
| PR-25 | `physical.py` | ✅ | de Sitter/먼지 H, Σ_WE vs Σ_θ, BBN |
| PR-26/27 | `analysis/dynamics.py` | ✅ | 고정점·연속법·Lyapunov·극한주기 검출 |

**26/27 완료** (PR-24 는 의도적 보류).

## 다음 후보
- Mussel attractor 수치 재현 (PR-27 벤치마크; `detect_limit_cycle` 준비됨)
- GPU 대규모 스캔 실측 (PR-23 프로파일)
- tilted 유체를 Layer 0 `general` 차트에 결합

---

## v1.1 — 외부검토 대응 (2026-07-29)

외부검토 7개 항목을 **수용 전에 전부 독립 재유도**한 뒤 실제 결함만 수정.
재유도 엔진은 v1.0 파이프라인과 코드를 공유하지 않는 별도 모듈 (`audit/`).

### 확정된 실제 결함 (수정 완료)

| # | 위치 | 내용 |
|---|------|------|
| 1 | `conventions.gauge_rotation_classB` | GENERATOR 부호 반환 ↔ 소비 측은 COMMUTATOR. 저장소 내 유일한 규약 혼용 지점. 부호 3개 전부 반전. |
| 2 | `matter/components.MagneticField.rhs` | 회전항 `-eps R B` → `+eps R B` (마스터 규칙). |
| 3 | `matter/fluid.dv_general` | shear 항 `+2 Sigma.v` → `-Sigma.v`, `(A.v)v` 부호 반전, `-A V^2` 항 누락 → 전면 재유도로 교체. |
| 4 | 문서 §4 | `(gamma,V)->(0,1)` 가 제거가능 0/0 이라는 주장 → 경로의존이므로 삭제. |
| 5 | 문서 §4 | class B + A≠0 에서 비틸트 유체 불가 주장 → 거짓 (Bianchi V open FLRW 반례). |
| 6 | 문서 부록 B | gamma 임계값 표 대폭 오류 → 전면 재작성. |

### 추가된 것

* `conventions.rotation_apply_vector / rotation_apply_tensor` — 마스터 회전 규칙 단일 창구
* `conventions.constraint_propagation_matrix` — 축약 Bianchi 로 유도한 4x4 전파 행렬
* `charts/general.S3_closed` — ^3S_ab 명시 닫힌 형태 (Jacobi 불필요)
* `tests/test_rotation_sign.py` — 17개 회귀 테스트 (순수 회전 프레임 포함)
* `audit/` — 독립 재유도 엔진 + `run_all.py` + `manifest.json` (25/25 통과)
* `requirements.lock`

### 테스트

```
pytest -q      ->  129 passed   (v1.0: 112)
audit/run_all.py ->  25/25 checks passed
```

---

## v1.2 — 유도 라운드 (PR-28~52 착수 전, 2026-07-29)

`DERIVATION-DAG.md` 의 D1–D24 중 임계경로(D2 → D13 → D15 → D16 → D17)를 유도·검증 완료.
스크립트: `audit/d_transport.py`, `d_optical.py`, `d_kinetic.py`, `d_matter.py`.
결과 문서: `DERIVATION-REPORT-v2.md`.  감사 `run_all.py` → **41/41 통과**.

### 발견된 결함 2건

| # | 위치 | 내용 |
|---|------|------|
| 1 | 보고서 식 (1) + 마스터 규칙 | v1.1 이 `Ω_ab Y_b = +(R×Y)_a` 로 적었으나 `Ω_ab ≡ ε_abc R^c` 이면 부호가 반대. 식 (1) 은 v1.0 이 옳았고 v1.1 의 "수정"이 뒤집은 것. **코드는 무사** (`W = −Ω` 로 일관). |
| 2 | `MagneticField.constraints.ampere` | curl 결합의 상대부호가 `−` 였으나 정답은 `+`: `n_ab B^b + eps_abc a^b B^c = 0`. E,B 를 동시에 넣고 프레임 Maxwell 을 풀면 Faraday 와 쌍대 구조로 확정된다. **v1.0 부터의 실제 결함.** 차이는 n≠0 & a≠0 인 class B (III, IV, VI_h, VII_h) 에서만 드러난다. |

### 미해결로 남긴 것

* **D22 vorticity**: ω_ab 가 v̇ 에 의존하면 안 되는데 현재 구현은 의존 (잔차 1.6).
  mixed 지표 투영 대신 완전 투영형으로 다시 짜야 함 — PR-42 선행조건.

### 테스트

```
pytest -q          ->  130 passed   (v1.1: 129)
audit/run_all.py   ->  41/41 checks passed  (v1.1: 25/25)
```


---

## v1.3 — 제3자 적대적 감사 (2026-07-29)

세 독립 트랙 (파이프라인 변이실험 / 코드·테스트 수색 / 좌표기저 완전독립 검산).
상세: `AUDIT-REPORT-v1.3.md`.

### 실결함 수정 6건
1. `audit/d_optical.py` 스크린 전송 — 공간 성분만 전송 (평행이동 위반) → 4-벡터
   전송. 상반성 1.5e-3 → **4.1e-12**.
2. `thresholds.stability_of_CS_II` — 하드코딩 위장 계산 → jacfwd 실선형화
   (+ 유형 II 구속 논증, 독립 해석식 3(7γ−10)/8 대조).
3. `constraints.make_projector` — 미등록 차트 침묵 항등 → 레지스트리 + ValueError,
   tilted-B (C2–C4) 와 IX-D (definition+trace) 투영 구현.
4. `charts/general.aux` — tilted 물질에서 비틸트 q 조용 사용 → `args["q"]` 훅 +
   전 성분 폐포 테스트 + 음성 통제.
5. `audit/d_matter.py` D19 참조식 — R_gen→R_comm 변환 누락 (−2(R×B) 허위 잔차)
   → 수정 후 정확히 0. 엔진·코드·좌표검산 3자 일치 확정.
6. `audit/einstein_frame.py` __main__ — 낡은 오답 참조로 실패 기록 출하 → 수치
   자기검사로 재작성 (4블록 ≤2.1e−14) + 게이트.

### 문서 결함 수정 (코드는 무죄로 판정된 것들)
* 보고서 (cprop) 박스, §5.4 회전 3종, D13/D9 dP 식 — generator-Ω 잔재 → (R×·) 표기.
* "codazzi 부호 잔차" 과대포장 → 축소차트는 시트 무구분임을 명시.
* "2500스텝" 허위, Γ⁰_ab "0 (exact)" 과대표기 정정.

### 게이트·테스트 강화
* run_all 41 → **63 게이트** (계수 게이트 11, 엔진 자기검사 4, 이전 미게이트 판별자 7).
* 공허 테스트 2건 (`M@0==0`, isfinite-only sink) → 실검사로 교체.
* 신규: 스칼라 √(3/2) 고정점 판별, general↔tilted 폐포, 투영기 회귀.

### 생존 확인 (공격에서 살아남은 것)
−8/15 급작응답 (손계산 재유도, f₀ 보편), Maxwell curl +ε (좌표검산 8.3e−17 vs
구부호 1.7e−1), 전사층 전체 (≤1.8e−15), 시드 강건성.

### 정직한 잔여 구멍
좌표기저 검산의 저장소 이식 (현재 /tmp 휘발), D22 vorticity (미해결 유지),
자기일관 게이트의 공통모드 맹점 (구조적 — 독립 좌표 유도만이 근본 해결).

```
pytest 134 passed · run_all 63/63
```

---

## v2.0 구현 착수 (2026-07-29) — M8 기반 + M11 임계경로 척추

DAG (IMPL-DAG.md) 를 따라 착수.  검증된 유도 D1–D24 를 코드로 이식.

### 완료 (6 PR)
| PR | 모듈 | 검증 오라클 | 테스트 |
|---|---|---|---|
| 28 | `physical/chart.py` | de Sitter H=const, 먼지 t=2/(3H), IX D-차트 재붕괴 | test_m8 4 |
| 29 | `physical/frame_transport.py` | det E=e^{3τ}, +Ω 부호, legacy 방향인자 일치 | test_m8 5 |
| 30 | `matter/species.py` | 3종족 어댑터 legacy 재현, ΣQ=0 강제 | test_m8 3 |
| 45 | `rays/weyl.py` + `generate_weyl.py` | tr T = -Ric_kk (2.8e-14), T 대칭 | test_m11 1 |
| 43 | `rays/geodesics.py` | FLRW 1+z=1/a, Kasner 방향의존, \|n̂\|=1 | test_m11 5 |
| 44 | `rays/optical.py` | EdS d_A (8e-9), Etherington, 방향 퍼짐 34% | test_m11 3 |

**임계경로 척추 PR-45→43→44 완성** — 여기가 가장 길고 위험했다.

### 구현 노트
- `physical.py` → `physical/` 패키지로 승격 (legacy re-export 로 하위호환).
- 프레임 Riemann 은 `generate_weyl.py` 가 einstein_frame 에서 144개 비영 성분을
  pickle 로 생성 → `weyl.py` 가 jax lambdify+jit.  좌표검산(D16)과 동일.
- 광학 적분기: 2-패스 (광선+스크린 → 배치 조석행렬 vmap → Jacobi ODE).
  4-벡터 스크린 평행이동(v1.4 부채), O(dt⁴) Jacobi, 6000스텝 relerr 3e-14.
  ★ 함정: z 와 d_A 의 스텝 registration 이 한 칸 어긋나면 O(dt) 오차 (수정됨).

### 상태
```
pytest 159 passed  (v1.4: 138; 신규 M8 12 + M11 rays 9)
```

### 다음 (DAG 순서)
PR-31 (units/initial) → PR-32/33 (g_*, T(ℓ)) → PR-46 (CMB 패턴; 첫 Planck Bianchi 대비)
→ PR-38 (자유흐름) → PR-34/35/36/37 (열역사) → M10 나머지 → PR-49/51/52.

---

## v2.0 진행 2차 (2026-07-29) — M9 열역사 + M11 CMB + M10 자유흐름

### 완료 (5 PR 추가; 누적 11/24)
| PR | 모듈 | 검증 오라클 | 테스트 |
|---|---|---|---|
| 31 | `physical/units.py`+`initial.py` | ΛCDM 나이 13.8 Gyr, z_eq 3400, Ω_γh²=2.47e-5 | test_m9 4 |
| 32 | `thermo/dof.py` | g_*(T≫)=106.75, (g_*,g_*s)(T≪)=(3.36,3.94), 단조 | test_m9 2 |
| 33 | `thermo/temperature.py` | T_ν/T_γ=(4/11)^{1/3}, sℓ³=const, T∝1/ℓ | test_m9 3 |
| 46 | `observables/cmb_pattern.py` | **Bianchi I 순수 사중극** (C₂ 99.85%), 등방 dT/T=0 | test_m11_cmb 4 |
| 38 | `matter/freestream.py` | 등방 π=0, w=1/3, ∇T=0, **−8/15 급작응답** | test_m10 7 |

**첫 Planck-Bianchi 대비 도달** (PR-46): Bianchi I 이 순수 사중극 CMB 패턴을
만드는 것을 확인 (C₂ 지배, C₁=C₃=0).  Planck VII_h vorticity 제한 참조 노출.

### 구현 노트
- `physical.py` 패키지에 units/initial 추가; `thermo/`, `observables/` 신규 패키지.
- numpy 2.x: `np.trapz`→`np.trapezoid`, scipy 1.17: `sph_harm`→`sph_harm_y` 대응.
- 자유흐름: audit/d_kinetic 의 검증 구적을 Species 형태로 이식.  π_ab≠0 이므로
  일반차트 필수.  광자 특성곡선과 코드 공유 (설계 D4).
- CMB 패턴: healpy 없이 직접 구면조화 분해.

### 상태
```
pytest 179 passed  (v2.0-1차: 159; 신규 thermo 9 + CMB 4 + freestream 7)
```

### 다음
PR-34 (질량 중성미자 FD) → PR-35 (암흑에너지 CPL) → PR-36 (재결합 Saha+Peebles)
→ PR-37 (동결) → PR-39/40/41/42 (점성·게이지장·no-hair·congruence) → PR-47/48
(거리·SNIa) → PR-49/51/52 (회귀·통합·보고서).

---

## v2.0 진행 3차 (2026-07-29) — M9 열역사 완성

### 완료 (4 PR 추가; 누적 15/24)
| PR | 모듈 | 검증 오라클 | 테스트 |
|---|---|---|---|
| 34 | `matter/neutrino.py` | m→0: ρ∝a⁻⁴ w=1/3; m≫T: ρ∝a⁻³; Ω_νh²=6.4e-4 | 4 |
| 35 | `matter/dark_energy.py` | Λ 상수, CPL 닫힌형=수치적분, w(a) | 4 |
| 36 | `thermo/recombination.py` | z_*=1090(가시함수), 잔존 x_e=2.3e-4, z_drag | 5 |
| 37 | `thermo/relics.py` | WIMP miracle Ωh²=0.08, **이방→잔존 증가** | 5 |

**M9 열역사 완성** (PR-31~37).  재결합은 RECFAST 급 (잔존 x_e 2.3e-4), 동결은
이방 팽창이 x_f 를 옮기는 Bianchi 고유 효과 포함.

### 구현 노트
- Peebles: n_H0 상수 오류(34× 과소) + α_B 계수(3.8× 과소) 수정 → 잔존 2.3e-4.
- 재결합 이방성은 H(z) 콜백으로만 (설계 D7): 빠른 팽창 → 잔존 전자 증가.
- 동결 Boltzmann ODE 는 강성이라 표준 해석해로 대체 (WIMP miracle 재현).

### 상태
```
pytest 179+27=... (M9 신규 22; 전체 재실행은 M10 후)
```

### 다음
PR-39/40/41/42 (점성·게이지장·no-hair·congruence) → PR-47/48 (거리·SNIa)
→ PR-49/51/52 (회귀·통합·보고서 v2.0).

---

## v2.0 진행 4차 (2026-07-29) — M10 완성 (점성·게이지·no-hair·congruence)

### 완료 (4 PR 추가; 누적 19/24)
| PR | 모듈 | 검증 오라클 | 테스트 |
|---|---|---|---|
| 39 | `matter/viscous.py` | Eckart Π=-2(η/H)Σ 감쇠, TṠ≥0, IS→Eckart | 3 |
| 40 | `matter/gauge_field.py` | curl 상대부호 +, E↔B 쌍대, π trace-free, Σ/H=O(ε) | 6 |
| 41 | `analysis/no_hair.py` | **Wald 지수 d lnΣ/dτ→-3**, H→√(Λ/3), 반례 exp→0 | 6 |
| 42 | `physical/congruence.py` | on-shell ω (D22): u-직교·반대칭·EOS-무관·a∥v, CMB 쌍극 β=\|v\| | 8 |

**M10 완성.**  no-hair 는 Bianchi I+Λ 정확해로 Wald 지수 -3 재현, 이방 인플레이션
게이지장으로 반례(Σ/H→O(ε)≠0) 구성.  congruence 는 D22 v1.4 on-shell vorticity 를
프레임 접속 위에서 재현 (a∥v 잔차 4.3e-11, EOS-무관 <1e-8).

### 구현 노트 — frame_connection 규약 버그 수정 (중요)
- `rays/frame.frame_connection` 의 **공간 블록 지표 순서 오류** 발견·수정.
  `_connection` 이 ³Γ^a_{bc} 를 미분슬롯=**가운데** 지표로 반환하는데 frame.py 는
  마지막 지표로 가정했다.  PR-43/44 는 P_double 의 **대칭축약** x^b x^c 만 써서
  드러나지 않았고, v2.0 의 첫 **비대칭 소비자** congruence 에서 표출 (a∥v 잔차 2.7).
- 수정: 공간 블록에 `swapaxes(C3,1,2)` 적용 → 계약(미분슬롯=마지막) 준수.
  회귀: 전체 220 통과 (ray 9 + cmb 4 + 나머지 207), 광선/광학/CMB 영향 없음.

### 상태
```
pytest 220 passed  (신규 M10: viscous+gauge 9, no-hair+congruence 14)
```

### 다음
PR-47/48 (거리·SNIa 관측량) → PR-49 (FLRW 극한 회귀) → PR-51/52 (통합·보고서 v2.0).

---

## v2.0 진행 5차 (2026-07-29) — M11 관측 브리지 (거리·SNIa)

### 완료 (2 PR 추가; 누적 21/24)
| PR | 모듈 | 검증 오라클 | 테스트 |
|---|---|---|---|
| 47 | `observables/distances.py` | r_s=147.8 Mpc(0.5%), BAO D_M/D_H/D_V vs BOSS ~3%, 이방 AP 사중극∝Σ | 7 |
| 48 | `observables/sn.py` | μ 앵커, shear→사중극·속도→쌍극 분리, Pantheon+ 형식 | 7 |

**독립검산 (BOSS/eBOSS 대조):**
```
z=0.38  D_M/r_s=10.37(10.3)  D_H/r_s=24.47(24.9)
z=0.51  D_M/r_s=13.43(13.4)  D_H/r_s=22.63(22.3)
z=1.48  D_M/r_s=30.07(30.2)  D_H/r_s=12.84(13.3)
```
r_s 는 모듈 자체 Eisenstein-Hu drag_redshift 사용 (자기일관, Planck 0.5% 내).
이방 BAO: 시선 팽창률 H_∥(n̂)=H(1+Σ_ab n̂n̂) → D_H 방향의존, AP 비 C₂∝Σ.
SNIa: shear=사중극·bulk flow=쌍극 (PR-42 CMB 쌍극과 동일 v).

### 상태
```
pytest 234 passed  (fast 221 + rays 9 + cmb 4;  신규 M11: distances+sn 14)
```

### 다음
PR-49 (FLRW 극한 회귀) → PR-51 (batch 비용 갱신) → PR-52 (보고서 v2.0).

---

## v2.0 진행 6차 (2026-07-29) — PR-49 FLRW 극한 회귀

### 완료 (1 PR 추가; 누적 22/24)
| PR | 파일 | 검증 오라클 | 테스트 |
|---|---|---|---|
| 49 | `tests/test_flrw_limit.py` | CLASS/CAMB 대조 + 이방신호 소멸 | 15 |

**독립검산 (Planck2018/CAMB 대조):**
```
D_M(z*)   = 13867.0 Mpc  (CAMB 13869.6, 0.02%)
age t0    = 13.795 Gyr   (Planck 13.797, 0.01%)
r_drag    = 147.07 Mpc   (Aubourg2015 보정, Planck 147.09, 0.01%)
r_drag    = 147.82 Mpc   (물리적분, 0.5%)
Ω_ν h²    = 6.44e-4      (0.06 eV)
z_* (가시) = 1077.6       (Planck 1089.9, 1.1%)
```
정직성 노트: 음향지평 물리적분은 반해석적 ~2% 오차(θ_* 상속) — Aubourg2015 보정식을
정밀 오라클로 병기(`sound_horizon_fit`, CAMB 0.1%).  완전정밀은 Boltzmann 필요.
부수 수정: `recombination_redshift` docstring 정정(Saha x_e=0.5 는 ≈1370, 관측 z_*≈1090
아님 — 가시함수 최대점이 관측값).

### 상태
```
pytest 249 passed  (fast 236 + rays 9 + cmb 4;  신규 FLRW 회귀 15)
```

### 다음
PR-51 (batch 비용 갱신) → PR-52 (보고서 v2.0).  구현 22/24 완료.

---

## v2.0 진행 7차 (2026-07-29) — PR-51/52 통합 + 보고서

### 완료 (2 PR; 누적 24/24 계획 중 22 실질 완료)
| PR | 파일 | 내용 | 테스트 |
|---|---|---|---|
| 51 | `batch.py` (확장) | 광선추적 실측 비용모델 (측지 0.7ms/st, 광학 1.6ms/st) | 6 |
| 52 | `report_v2.tex/pdf` | v2.0 보고서 (수식·검증표·CAMB대조·규약결함·한계·비용) | — |

**비용 실측:** 전천 CMB ΔT/T 143 min, d_A 지도 328 min (numpy 직렬) → GPU 이식 동기.
**보고서:** 6쪽 PDF (xelatex, Noto Serif CJK KR). §5 CAMB 대조, §7 frame_connection 규약
결함 기록, §8 정직한 한계(음향지평 2%).

### 상태 (최종)
```
pytest 255 passed  (fast 242 + rays 9 + cmb 4)
구현: M8-M11 완료.  22개 실질 PR + 보고서.
```

---

## v3.0 진행 2차 (2026-07-29) — R1 완결 + R4 (광학 d_A Rust 이식)

### 완료
| 단계 | 산출 | 차등테스트 | 성능 (2코어) |
|---|---|---|---|
| R1(측지) | `rays/geodesic.rs` + PyO3 + Rayon | z **비트-정확 (0.00e+00)** | 전천 139분 → **0.7초** (≈12,000×) |
| R1(광학) | `rays/optical.rs` 3-패스 + Jacobi RK4 | z 비트-정확, d_A **2.3e-16** | 전천 400분 → **5.2초** (≈4,650×) |
| R4 | 조석행렬 **닫힌형** (탈-sympy) | Riemann 4.4e-16, T_AB 1.4e-14 | JAX/sympy 제거 |

### R4 — 조석의 닫힌형 (핵심 성과)
대각 Bianchi I (N=A=R=0, ³R=0) 에서 Gauss-Codazzi 로 프레임 Riemann 이 닫힌다:
```
K = Hδ+σ,  M = -(K̇+K²)
R_{0a0b}=M_ab,  R_{abcd}=K_ac K_bd - K_ad K_bc,  R_{0abc}=0        (오라클 4.4e-16)
T_AB = -[ w_A·M w_B + (u_A·K u_B)(κ·Kκ) - (u_A·Kκ)(Kκ·u_B) ]        (오라클 1.4e-14)
   w_A = α_A κ - k⁰ u_A,  E_A=(α_A,u_A),  k=(k⁰,κ)
```
→ 144성분 sympy pickle + JAX vmap 을 순수 산술로 대체.  일반 유형은 후속 codegen.

**스크린 직교성 1.1e-15** — v1.4 부채(공간성분만 전송 시 상반성 1.5e-3 편향)가
Rust 포트에서도 4-벡터 전송으로 유지됨을 확인.
**물리 오라클**: EdS 기준해 d_A=(2/H0)(1-(1+z)^{-1/2})/(1+z) <1e-6 (RK4 이산화 수준).

### 상태
```
pytest 276 passed  (fast 263 + rays 9 + cmb 4;  차등테스트 21)
cargo test 2 passed
```

### 다음
R2/R3 (차트 RHS + diffsol BDF/ESDIRK 단일·배치 적분) → 일반유형 조석 codegen →
`bianchi._rustcore` 통합.

---

## v3.0 진행 3차 (2026-07-29) — R2/R3 + 통합 (R-DAG 완주)

### 완료
| 단계 | 산출 | 차등테스트 | 성능 (2코어) |
|---|---|---|---|
| R2 | `ode/charts.rs` (class_a/class_b) + `ode/solve.rs` (diffsol BDF) | RHS **비트-정확 (0.0)**, 궤적 2.4e-10 vs diffrax | — |
| R3 | Rayon 배치 스캔 + 낙오자 격리 | 배치=단일 (1e-12) | K=256 배치 8.5초(JAX warm) → **33 ms** (≈260×) |
| 통합 | `bianchi/backend.py` 단일 디스패치 + 폴백 | 두 경로 일치 8개 시험 | — |

### R3 낙오자 격리 — 실측 검증
JAX batched while_loop 은 `batch × max_steps` 비용(끝난 원소도 본문 실행).  Rayon 은
원소별 독립.  K=256 (15% Kasner 근방) 실측: Rust 229/256 완료, **실패 27개는 전부
Ω<0 비물리 초기조건**이었고 JAX 도 같은 원소에서 발산(0/8).  실패는 솔버 약점이 아니라
초기데이터 발산이며 Rust 는 원소 단위로 격리·보고한다.

### 보존 성질 (Rust 에서도 유지)
- `N_i'=(…)N_i` 곱셈 구조 → N_i=0 과 부호가 **정확히** 보존 (유형 안전성)
- Class B Codazzi C = Σ̃Ñ-Δ²-Σ₊²Ã 궤적 위 <1e-8
- Gauss 항등식 Ω = 1-Σ²-K 궤적 위 <1e-13

### 통합 (계획 §2)
`bianchi.backend` 가 단일 진입점.  검증된 Python 모듈은 **미수정**, 디스패치만 추가.
모든 함수에 `force_python=True` 로 오라클 강제 가능 → 차등테스트가 영구 안전망.

### 상태 (R-DAG: R0·R1·R2·R3·R4 완료, R5 GPU 유예)
```
pytest 292 passed  (fast 279 + rays 9 + cmb 4;  차등 29 + 통합 8)
cargo test 7 passed
```

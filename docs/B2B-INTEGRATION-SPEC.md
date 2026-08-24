# B2b 통합양식 — 외부 재결합/재이온화 모듈 수입 규격 (v1.0, 75차)

이 문서는 **외부 모듈이 도착하기 전에** 이쪽에서 고정한 접합면이다.
소비자 코드는 이미 이력 주입형으로 전환되어 있고 (`bianchi/thermo/history_api.py`),
게이트도 상시 돌고 있다 (`tests/test_b2b_history_api.py`).  외부 모듈은 아래
계약만 만족하면 **코드 수정 없이** 꽂힌다.

## 1. 최소 계약 (필수)

```python
class MyRecombination:                 # 클래스든 모듈이든 무방 (덕 타이핑)
    name: str                          # 예 "hyrec-2.1"
    z_range: tuple[float, float]       # (z_min, z_max) 유효범위
    def x_e(self, z): ...              # 배열→배열, x_e = n_e / n_H
```

선택 (있으면 사용, 없으면 None 로 취급):

```python
    def T_matter(self, z): ...         # 물질온도 [K]
    metadata: dict                     # 오차추정·참조케이스·He 규약·버전
```

가장 쉬운 수입 경로는 **격자 표**를 주는 것이다:

```python
from bianchi.thermo.history_api import TabulatedHistory
hist = TabulatedHistory(z_arr, xe_arr, T_m=Tm_arr, name="recfast-1.5.3",
                        metadata={"dxe_rel": 1e-3, "He": "Y_p=0.24, HeII 포함"})
```

## 2. 단위·규약 (계획 §8 ①)

| 양 | 정의 | 단위 |
|---|---|---|
| z | 적색이동 (1+z = 1/a, 등방 규약) | 무차원 |
| x_e | n_e / n_H — **수소 기준** (He 전자 포함 시 1 초과 가능) | 무차원 |
| n_H | 8.50e−6 · Ω_b h² (1+z)³ (Y_p = 0.24) | cm⁻³ |
| σ_T | 6.6524587e−25 | cm² |
| T_m | 물질(바리온) 온도 | K |

n_H 상수는 `history_api.n_H_cm3` 가 `bianchi.thermo.recombination` 의 값을
**그대로** 재사용한다 (단일 진실원).  다른 Y_p 를 쓰면 metadata 에 명시하고
`n_H_cm3` 를 함께 교체할 것.

## 3. 유효범위와 오차 (계획 §8 ②)

- `z_range` 밖 호출은 **예외**여야 한다 (조용한 외삽 금지 — `validate_history`
  의 `range_guard` 검사가 이를 확인).
- 오차추정은 `metadata["dxe_rel"]` (상대) 또는 `["dxe_abs"]` 로.  들어오면
  게이트 허용치를 그 값으로 스케일한다.

## 4. 참조 케이스 (계획 §8 ③)

최소 1개: (Ω_b h², Ω_m h², h, T₀) 와 그때의 (z_*, τ_reion) — 이쪽 게이트가
`optical_depth` 로 재현해 대조한다.  현 내장 Saha 기준값: z_* = 1284.28
(Ω_b h²=0.0224, h=0.674, 평형 근사이므로 정밀 모듈과는 당연히 다르다 —
**대조는 절차의 검증**이지 물리값 일치 요구가 아니다).

## 5. 이방성 결합 규약 (계획 §8 ④)

기본은 **등방 이력 + 이방 기하**: x_e 는 z 만의 함수, 이방성은 H(z)·방향
스케일인자로만 들어온다.  근거: 재결합기의 이방성은 작고 (Σ ≪ 1), 이력의
방향의존은 2차.  방향의존이 필요해지면 `x_e(z, nhat)` 확장 훅을 열되
`metadata["anisotropic"]=True` 로 **명시 버전 표기**한다.

## 6. 충돌항 경로 (G2 사다리와의 접속)

```python
nu_tau = thomson_rate(hist, z, Omega_b_h2=..., H_of_z=...)   # 무차원 (τ-시간)
```
이 ν 가 G2 사다리 (`collision_ladder.collide`, `grid_coupled.rhs(nu=...)`) 로
그대로 들어간다.  ★ 적용 영역 주의 (75차 실측): **강한 이방성 + 강한 충돌**
조합에서는 불변격자의 물리-프레임 구적이 무너진다 (G2 열화 곡선; 축비 ≳300:1
에서 발산).  재결합기 (약이방) 는 안전 — 그 영역에서 유체 지수를 |Π|/Ω ~4%
보정 이내로 재현함을 시험이 잰다.

## 7. 수입 절차 (체크리스트)

1. `validate_history(hist)` 통과 (7개 검사).
2. `tests/test_b2b_history_api.py` 를 외부 이력으로 파라미터화해 재실행.
3. `optical_depth(hist, z_grid)` 로 z_*·τ 산출 → 참조 케이스 대조.
4. `thomson_rate` 로 ν_τ 곡선 확인 (재결합 전 ≫1, 후 ≪1 — 결합·이탈).
5. G2/I2c 결합 게이트를 그 ν 로 재실행 (약이방 영역).
6. PR-STATUS 에 모듈명·버전·참조케이스·오차추정 기록.

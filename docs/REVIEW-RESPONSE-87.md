# 외부 리뷰 대응 (87차) — 보고서 정정 명세 + 두 lane 구조

외부 리뷰가 지적한 **빨간펜 3건 + 구조 권고 4건**의 정정 명세다.
이 문서는 **결정적(deterministic)** 이어야 한다 — 이전 텍스트와 정정 텍스트를
그대로 적어서, 세션 컨텍스트가 사라져도 누구든 같은 정정을 재현할 수 있게 한다.

★ 작업트리 사정: 87차 시점에 컨테이너가 83차 상태로 회귀해 85·86차 산출물
(`bianchi/q/rate.py`, `bianchi/q/polstate.py`, P9 Rust 바인딩, `audit/p3_*`,
`report/`) 이 소실되었다.  아래 C1–C4 는 **보고서 텍스트 정정**이라 복원 후
기계적으로 적용하면 되고, C5 는 **코드 변경**이라 복원 후 구현한다.
C7 (11유형 커버리지) 은 살아남은 Q-tier 코어만으로 **이번 차에 완료**했다.

---

## C1 · "부스트는 편광면을 돌리지 않는다" 를 좁힌다  [텍스트]

**지적.** 계산이 보여준 것은 정확히는 *내가 정의한* Lorentz-수송 스크린 대표원과
산란면 적응기저에서 **추가적인 in-screen 회전이 없다**는 것이다.  임의의 외부
tetrad/편광 기저를 고정하면 Wigner phase/rotation 이 다시 나타날 수 있다.
결과 자체는 문제없지만 **문장이 결과보다 넓다**.

**정정 (절 제목).**
- 이전: `결과 2 --- 부스트는 편광면을 돌리지 않는다 ($\psi=0$)`
- 이후: `결과 2 --- 정준 수송 스크린 사상에서 $\psi=0$ (부스트)`

**정정 (본문에 추가할 단락).**

> **주장의 범위.** 여기서 $\psi=0$ 은 **정준 수송 스크린 사상**에 대한 진술이다 —
> 스크린 대표원 $W$ ($W^0=0$, $W\!\cdot\!p=0$) 를 Lorentz 수송한 뒤 게이지를
> 복원해 얻은 사상 $S$ 를, 산란면 적응기저 ($m_1\propto P_\perp[v]$) 에서 읽은
> 값이다.  **임의의 외부 tetrad 나 전역 편광 기저를 고정하면 Wigner phase 가
> 다시 나타날 수 있다** — 그것은 기저 선택의 성질이지 $S$ 의 성질이 아니다.
> 이 코드가 기저-없는 텐서 캐리어를 쓰기 때문에 실제 계산에서 그 phase 가
> 등장하지 않는 것이고, "부스트가 편광면을 절대 돌리지 않는다" 는 더 넓은
> 명제를 주장하는 것이 아니다.

**영문 표기 (논문용).** "$\psi = 0$ for the canonical transported screen map"
(NOT "boosts do not rotate the polarization plane").

**초록 정정.**
- 이전: `부스트가 편광면에 **추가 회전을 만들지 않음**($\psi=0$)`
- 이후: `부스트의 **정준 수송 스크린 사상**에 추가 회전이 없음 ($\psi=0$)`

---

## C2 · "E/B 는 선형이론의 언어" 는 **틀렸다**  [텍스트, 물리]

**지적.** E/B 분해 자체는 선형 섭동론에만 속하는 언어가 아니다.  spin-2 장에 대한
전역 분해는 비섭동적으로도 정의할 수 있다.  정량적으로 안 쓰는 **진짜 이유**는
선택한 스크린 기저의 불연속성과 그로 인한 $Q/U$ 비수렴이다.

**정정 (본문).**
- 이전:
  > $E/B$ 는 선형이론의 언어이고, $\arg\min|\hat e|$ 스크린 기저가 구면 위에서
  > 불연속이라 $Q/U$ 가 각 해상도로 수렴하지 않기 때문이다
- 이후:
  > $E/B$ 분해 **자체는** 선형 섭동론 전용 언어가 아니다 — spin-2 장의 전역
  > 분해는 비섭동적으로도 정의된다.  격리하는 이유는 **구현 쪽**이다:
  > 현재 쓰는 국소 스크린 게이지 ($\arg\min|\hat e|$ 기저) 가 구면 위에서
  > 불연속이라 그 위에서 정의한 $Q/U$ 가 각 해상도로 수렴하지 않고, 따라서
  > 전역 spin-2 분해가 **정량적으로 안정적이지 않다**.  연속적인 스크린 게이지
  > (또는 spin-weighted 구면조화 기반) 를 도입하면 정량화할 수 있다 —
  > 그때까지만 diagnostic 이다.

**같은 정정을 반영할 다른 위치.**
- `bianchi/q/polarization.py` : `multipoles_diagnostic` docstring 의
  "★ 정직성 조항: E/B 분해는 **선형이론의 언어**다" 문장.
- `docs/Q-CONTRACT.md` §9 의 관측량 문단.
- `PLAN-P-polarization.md` §2 P6.

---

## C3 · "강성 자체가 없음" 을 좁힌다  [텍스트]

**지적.** 정확 충돌 지수 덕에 **충돌 부분스텝의 안정성 강성**은 제거됐다.
그러나 full operator 에서 수송과 충돌은 비가환이고 $\nu_\tau$ 가 재결합에서
매우 빠르게 변하므로 **분할 정확도 제약은 남는다**.  오차예산의 Strang 2차가
바로 그 증거다.

**정정.**
- 이전: `근사 절환 & 정확 충돌 지수 $\Rightarrow$ 강성 자체가 없음`
- 이후: `근사 절환 & 정확 충돌 지수 $\Rightarrow$ **충돌 부분스텝의 안정성 강성** 제거`

**본문에 추가할 문장.**

> 정확히 말하면 제거된 것은 **충돌 부분스텝의 안정성 강성**이다
> (*stability stiffness eliminated in the collision step*).  수송과 충돌은
> 비가환이고 $\nu_\tau$ 는 재결합에서 급격히 변하므로 **분할 정확도 제약**은
> 남는다 — 오차예산에서 Strang 이 정확히 2차로 나오는 것이 그 증거다.
> 즉 "$\Delta\tau$ 를 안정성 때문에 줄일 필요가 없다" 는 참이고,
> "$\Delta\tau$ 를 정확도 때문에도 줄일 필요가 없다" 는 거짓이다.

**계약 반영.** `contract.NO_APPROXIMATION["approximation_switching"]["what"]` 의
"강성 자체가 소멸" 문구를 "충돌 부분스텝의 안정성 강성이 소멸 (분할 정확도
제약은 남는다)" 로 교체.

---

## C4 · 원자 미시물리 경계를 **대문짝만하게**  [텍스트]

**지적.** 현재 "알려진 간극" 에 Thomson/Kompaneets/Faraday/열전자 같은 수송
근사는 잘 정리돼 있는데, 지금 가장 큰 실제 physics boundary 는 그게 아니다.

**정정.** 초록 직후와 "알려진 간극" 맨 앞에 다음을 **박스로** 넣는다.

> **범위 경계 (가장 큰 것).**
> 이온화 이력 $x_e(z)$ 는 **외부에서 공급**된다.  재결합과 재이온화는 아직
> 자기일관하게 풀리지 않는다.  현재 어댑터는 외부 $x_e(z)$ 를 매 스텝
> 소비하지만, 그 $x_e(z)$ 가 FLRW 팽창과 등방 복사장 아래에서 만들어진
> 것이라면 이는 엄밀히 **external-history lane** 이다.  자체 재결합은
> $H_{\rm Bianchi}$, $f_\gamma(E,\hat e)$, 원자 준위, Ly$\alpha$ 복사수송이
> 함께 되먹임되어야 하며 — 이것은 이 솔버의 마지막 5 % 가 아니라 사실상
> **별도의 physics engine** 이다.

`contract.KNOWN_GAPS` 에 `atomic_ionization_history_is_external` 항목 추가.

---

## C5 · $H$ 정규화를 **두 lane 으로 분리**  [코드 + 텍스트]

**지적.** 모델 $H$ 와 $\Lambda$CDM $H$ 규약이 최대 33.8 % 차이 나고 자기일관
앵커가 외부 앵커의 0.389 배라는 것은 작은 문제가 아니다.  "사용자 선택사항" 으로만
남기면 나중에 recombination shift 를 봤을 때 그게 *anisotropic recombination
physics* 인지 그냥 *$H$ normalization 을 다르게 준 것* 인지 섞인다.

**설계 (복원 후 `bianchi/q/rate.py` + `model.py` 에 구현).**

```
lane = "internal"       # 내부 일관성 lane
  H_anchor  : Gauss 구속이 정하는 값 (Omega_0 에서 유도)
  용도      : "이 기하가 스스로 만드는 재결합 이동" 을 묻는 계산
  주의      : H_0 가 관측값과 다를 수 있다 (그게 정상이다)

lane = "phenomenology"  # 현상론 lane
  H_anchor  : 관측 calibrate 된 (H_0, Omega_i) 에서 온 값
  초기자료  : 그 (H_0, Omega_i) 와 정합하는 Bianchi 초기자료로 시작해야 한다
  용도      : 관측과 직접 비교하는 계산
```

**강제 규칙 (조용한 혼합 금지).**
1. `lane` 을 **필수 인자**로 만든다 (기본값 없음).  둘 중 하나를 명시하게 한다.
2. `Model.summary()` 가 lane 과 그 귀결을 인쇄한다.
3. `lane="internal"` 인데 `H_anchor` 를 외부 값으로 덮어쓰면 **거절**한다.
4. `lane="phenomenology"` 인데 초기자료의 $\Omega_0$ 가 주어진 $\Omega_i$ 와
   어긋나면 **경고가 아니라 예외**를 던진다 (임계는 계약에 등재).
5. 산출물(그림·표)에 lane 을 각인한다.

**예산 (신규 `Q20`).**
```
"Q20": dict(lane_required=True,           # lane 미지정은 예외
            anchor_consistency=1e-3,      # phenomenology lane 의 Omega 정합
            lane_gap_recorded=True)       # 두 lane 의 차이를 실측해 기록
```

---

## C6 · 로드맵 (리뷰어 제안 순서 그대로)  [텍스트]

보고서 말미에 다음 순서를 명시한다.  **transport core 는 여기서 동결**한다.

1. **transport core 동결** — 11유형 커버리지 매트릭스로 기준선 고정. *(완료, C7)*
2. **$H$-anchor 문제를 먼저 닫는다** — 원자물리보다 **앞**이다. *(C5)*
3. **외부 정밀 재결합 provider** 연결 — FLRW 극한에서 HyRec/Recfast 계열과
   $x_e(z)$, 가시함수, $\tau_{\rm opt}$, $z_*$ 를 맞춘다.  native atom solver 불필요.
4. **external-history + anisotropic transport lane** 을 과학적으로 완성.
5. **native Bianchi recombination** 을 별도 프로젝트로 — multi-level atom +
   Ly$\alpha$ transfer 는 마지막 5 % 가 아니라 새 physics engine 하나다.
6. **재이온화** 도 같은 순서 — 외부 $x_e(z)$/source history 먼저, native RT 나중.

**동결 선언.** Kompaneets, Faraday, 비가환 기하 등 수송 확장은 이 로드맵이
3–4 단계를 통과하기 전에는 착수하지 않는다.

---

## C7 · 11 Bianchi 유형 커버리지 매트릭스  [완료]

`scripts/coverage_matrix.py` → `docs/COVERAGE-11TYPES.md`, `report/coverage.json`.
12 항목 (11 표준 유형 + 예외형 VI\*$_{-1/9}$) 전부 분류 왕복·유한성·Jacobi
기계정밀·Codazzi 수렴을 통과한다.

**★★ 이 표가 내 각주를 반증했다.**  처음엔 "class A 는 Codazzi 가 기계정밀" 이라고
적었는데 거짓이다.  기계정밀인 것은 **Bianchi I 뿐**이고 (곡률항이 아예 없다),
곡률이 있는 class A 도 1e−5 수준의 잔차를 갖는다.  차이는 **크기가 아니라
수렴 차수**에 있다:

| 묶음 | 유형 | Codazzi 수렴 차수 |
|---|---|---|
| 평탄 | I | 기계정밀 (2e−16) |
| class A 곡률형 | II, VI₀, VII₀, VIII, IX | **3.52 – 3.72** |
| class B | IV, V, VI_h, VII_h, III, VI\* | **2.28 – 2.70** |

class A 곡률형이 고차인 것은 T4 (N-항의 $\ell\le1$ 모멘트가 정확히 0) 가 저차
오차를 막기 때문이고, class B 가 저차인 것은 A-항이 $\ell=1$ 에 **직접** 작용하기
때문이다 — Q5b 가 등재한 $\mu$-꺾임 축(2.45)과 **같은 축**이다.

그래서 합격 판정을 절대 임계가 아니라 **수렴 차수 ≥ 1.5** 로 두었다.  절대
임계를 쓰면 곡률형 전부가 해상도만 낮으면 탈락하고 해상도를 올리면 통과한다 —
물리가 아니라 격자를 재는 게이트가 된다.

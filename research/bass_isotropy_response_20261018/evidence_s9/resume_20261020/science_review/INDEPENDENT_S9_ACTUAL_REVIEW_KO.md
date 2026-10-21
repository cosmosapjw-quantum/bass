# S9 실제 실행 독립 검토

**판정: PHYS-MATH와 PHYS-MATH-CODE 모두 PASS_SCOPED.** 고정 여덟 이력의 원 `RAW.json`, `PROCESS.json`, `ASSESSMENT.json`, 사전등록과 재사용 S8 reference를 읽고 1,224개 관측 행과 192개 출생 certificate를 독립 계산했다. 기존 `analyze.assess`와 production 함수를 호출하지 않았고 ODE 적분·과거 개발 테스트를 실행하지 않았다. 수용 범위는 고정된 discrete manufactured donor/cohort 모형을 두 실제 VigilODE 경로가 적분한 결과다.

## PHYS-MATH: 방정식과 직접 검산

Non-tilted axisymmetric Bianchi I, `(-,+,+,+)`, `a_perp=a exp(-b)`, `a_parallel=a exp(2b)`를 유지했다. `x=ln(a/a_ref)`, `h=H/H*`, `y=s/H*`, `Sigma=sqrt(3)|y|/h`이고, 공급부는 S8의 pressureless manufactured donor다. 출생 사이에서 bank를 고정하면

\[
\mathcal E_b=-2\Pi,\qquad \mathcal E_x=-4\mathcal E,
\quad \Pi_x=-4\Pi,\quad (\mathcal E_d)_x=-3\mathcal E_d.
\]

각 ray의 `R=sqrt(A+B)`, `A=e^(2d)(1-mu²)`, `B=e^(-4d)mu²`를 80자리 Decimal로 다시 평가했다. 에너지의 궤적 미분은 Legendre 또는 기존 derivative helper를 쓰지 않고 `e^(-4(x-u))sqrt(A+B)`를 직접 미분해 구했다. 그 결과를 원 native가 기록한 에너지·압력과 대조했다. 같은 bank의 RHS, Jacobian, 명시적 `F_x`도 에너지·압력·압력의 b 미분으로 새로 구성해 모든 birth의 전후 callback 기록과 대조했다.

| 독립 검사 | 실제 최대값 |
|---|---:|
| Native E와 Decimal inventory의 상대차 | `2.3411870319082195e-16` |
| 직접 에너지 미분 + native `4E+2(y/h)Pi`의 상대 잔차 | `9.364748127632878e-16` |
| Native donor와 Decimal donor의 상대차 | `6.558169987071305e-16` |
| Event의 RHS/J/F_x와 Decimal 구성의 scaled 차이 | `2.356231404247763e-16` |
| 독립 Hamiltonian 상대잔차 | `2.2743189570736747e-12` |
| 독립 event energy 상대잔차 | `3.66654245463207e-17` |
| Decimal `C'+2C`의 scaled 산술 잔차 | `1.4712611557081695e-79` |

Hamiltonian은 `C=h²-y²-E_d-E-L`을 native가 보고한 C에서 복사하지 않고 독립 inventory로 다시 계산했다. 기존 과학 기준인 Hamiltonian/cohort `1e-11`, event `1e-13`을 유지했다. `C'+2C`의 매우 작은 값은 80자리 산술에서 식이 일치한다는 검산값이다. ODE 해의 오차 크기로 해석하지 않는다.

출생 때 정규화 합 S가 binary64에서 정확한 1은 아닐 수 있으므로, 추가 kernel의 jump를 `Delta E=wS`, `Delta Pi=wM2`, `Delta Q=w[-8S/5-10M2/7+36M4/35]`로 검사했다. donor의 exponential/expm1 반올림과 정규화 오차를 별도로 남기는 이 검산은 `P2=P4=0`만으로 에너지 보존을 대신 판정하지 않는다. 원 event-relative 최대값과 고정밀 재계산값의 차이는 최대 `2.038324318348483e-16`이고 두 값 모두 원 event 기준 안에 있다.

### Reference와 analytic FLRW

기존 S8의 153개 h/b/y 행은 계산 입력으로 가져오지 않고 비교 대상으로만 사용했다. 새 birth b(u)는 각 실제 event state의 두 번째 성분과 정확히 같고, 기존 S8의 미래 birth geometry를 입력에서 찾거나 주입하는 경로는 없다. 원 observer의 reference 최대오차 세 성분을 모두 다시 산출해 정확히 재현했다.

| 입력 | max h/b/y absolute error | 독립 Hamiltonian 상대잔차 |
|---|---:|---:|
| MF r0, r1 | `8.3366646919103e-13` | `2.2683797582253147e-12` |
| MF fine r2 | `1.4327428132787645e-13` | `3.940052198807788e-13` |
| Small clock4 r0, r1 | `8.359979375427429e-13` | `2.2743189570736747e-12` |
| Small clock4 fine r2 | `1.7108536809473662e-13` | `4.707111949666269e-13` |
| MF analytic FLRW | `3.3522885227577977e-13` | `7.87690466845647e-13` |
| Small clock4 analytic FLRW | `3.6813467598394824e-13` | `8.730685878790901e-13` |

FLRW 항목은 `h=sqrt(d0 exp(-3x)+Egamma0 exp(-4x)+L)`, `b=b0`, `y=0`을 80자리로 평가한 값이다. 원 binary64 analytic expression으로 평가하면 원 ASSESSMENT의 값이 정확히 재현되고, 위 고정밀 analytic 값과는 끝자리 반올림 정도만 다르다. 모든 행은 원 `fine_reference_abs=1e-9` 기준 안에 있다.

## PHYS-MATH-CODE: 실제 원자료와 실행 계약

사전등록 SHA는 `7e615ea1820e95b6fb61d7a360d13bf0fb560b6f25883e17ed487e8a3505f507`다. 사전등록에 고정한 source/input hash, 각 case의 허용된 설정, `INPUT.json`과 RAW의 input 일치, PROCESS의 RAW/input/log hash와 exit0를 확인했다. 현재 과학 source와 원래 고정 owner는 바꾸지 않았다.

Fraction은 serialized binary64 값을 정확한 dyadic rational로 바꾸고 `sum(alpha)`, `sum(alpha mu²)`, `sum(alpha mu⁴)`를 먼저 합산했다. 여기서 P2/P4를 구성해 native BigRational certificate와 대조했다. **192/192 출생 certificate가 정확히 일치**하고 원 `3/10^15` 기준을 만족했다. 최대 moment는 `9.9692153425314e-16`, 모든 old+new stock의 최대 정규화 차이는 `1.1102230246251565e-16`이었다. 이는 여섯 closed 이력의 출생 횟수이며 서로 다른 192개 지지라는 뜻은 아니다.

각 case의 old-stock 배열은 입력과 완전히 같고 원 digest 두 개와 일치한다. 새 stock도 출생 때 기록한 digest와 최종 digest가 같다. 매 관측의 inventory를 **같은 final immutable cohort 배열 중 그때 이미 출생한 cohort**로 다시 계산한 값이 native 원자료와 일치했다. 모든 event에서 원 출력의 state는 연속이며 donor/radiation/Pi가 오른쪽 bank의 `*_after`와 정확히 같다.

Closed 이력 각각 33개 fresh bank/driver segment의 경계와 birth exposure, 153개 정확한 출력 시각을 확인했다. MF는 실제 JVP와 F_x 호출을 기록했고, small clock4는 실제 Jacobian build/direct factorization을 기록했다. 새 독립 검토는 raw에 기록된 callback 사용량을 합산해 ASSESSMENT와 정확히 대조했다. Augmented clock의 raw 최대오차는 `2.4424906541753444e-15`로 원 `1e-12` 기준 안에 있다. 네 번째 내부 상태 전체는 별도 출력하지 않았으므로, 그보다 강한 내부 clock trajectory 주장은 하지 않는다.

### r0/r1 plateau의 판정

두 arm 각각 r0와 r1의 `observations`, `segments`, `events`, `final_cohorts`가 **JSON의 모든 수치 값까지 동일**하다. 두 경우 모두 accepted218, output-clipped119, rejected0이다. Fine에서는 accepted305, output-clipped119, rejected0으로 바뀌었다. MF의 JVP/F_x는 각각 coarse10246/218, fine14335/305다. Small은 coarse218, fine305회의 Jacobian build와 direct factorization을 기록했다.

이 자료는 출력 시각에 맞춘 step 제한이 두 coarse tolerance 사이의 차이를 가렸다는 설명과 일치한다. 원 raw에는 내부 모든 step의 t 배열이 없으므로 모든 내부 timestep의 동일성을 직접 증명했다고 표시하지 않는다. 새 순수 차수 수렴률이나 portable speedup을 이 비교에서 산출하지 않는다.

## 판정과 재현

검토 helper `recompute_s9.py`는 Python 표준 라이브러리만 사용한다. 실제 마지막 실행 wall time은 약12초이고 원자료를 수정하지 않았다. 원 PROCESS/ASSESSMENT의 f64 maxima와 이번 독립 Decimal maxima는 구별해서 저장했다. 드문 `/proc` 관측 RSS는 실제 peak의 하한이므로 root wrapper의 약3MB 표본값을 peak로 승격하지 않는다.

```bash
python3 recompute_s9.py \
  --lane /path/to/bass/research/bass_isotropy_response_20261018 \
  --run /path/to/bass/research/bass_isotropy_response_20261018/evidence_s9/run_20261020_r1 \
  --output /path/to/new/INDEPENDENT_RECOMPUTATION.json
```

이 검토에서 수정이 필요한 과학·구현 finding은 발견하지 않았다. S8 n64의 별도 precision failure, 넓은 각도·initial-condition 범위, actual MD14 source의 닫힌 에너지 공급과 native Einstein feedback, native spectral/reactive history의 남은 의무는 그대로 유지한다. S9의 성공은 그 의무들을 닫거나 production/full EoR/merge를 승인하지 않는다.

# S11 독립 C9 결과: 저장된 출력의 정확 수학·각도 응답 검토

**판정: 등록한 범위에서 235/235 PASS.** 새 S11 solver의 완료된 출력만
읽었다. 이 C9 실행에서 solver, compiler, 기존 campaign/history, ODE,
benchmark 또는 NCP를 호출한 횟수는 0회다. 입력과 main evidence의 전체 파일
bytes는 검토 전후 동일했다.

## 실행 identity

main S11 source는 `7fb9b83cba01d37ce4cabbc4772527710601cd96`, tree는
`963a43f26df1f9c6f462b9df9a2c34cf99f525c9`다. 검토한 main receipt는
101개 검사와 14개 projection pair, 12개 양의 결과, 두 개의 예상 infeasibility,
660개 angular response를 갖는다. main의 원시 실행 기록 26개와 모든 pair의
실제 종료 코드·stdout JSON도 저장된 projection 행과 일치했다.

독립 checker `independent_c9_readback.py`의 실행 SHA256은
`f8a4404ca02397afd0c05601a2d7b654ff7398662e1f60003ce19c857c3bbf58`다.
명령, 실제 UTC 시작·종료, stdout/stderr의 hash와 process exit는
`C9_PROCESS_R1.json`에 남겼다. 실제 실행은 한 번이며, 2026-10-20
17:57:00.376201–17:57:01.143479 UTC, exit 0, stderr 0 bytes였다.
외부 process wall은 0.767497초, 내부 측정은 0.713486초, process 최대
RSS는 40,064 KiB였다. 이 수치는 C9 검토의 자원 사용이며 새 solver 성능
benchmark로 해석하지 않는다.

## 서로 독립적인 검사 경로

| 검토 대상 | 방법 | 실제 결과 |
|---|---|---|
| 14개 support·projection pair | exact binary64 방향의 제곱, support factor 다항식의 정확 기대값 | 12 strict interior, 2 infeasible가 등록 상태와 일치 |
| 양쪽 구현의 24개 양의 weight 목록 | Rodrigues 공식의 유리수 Legendre 다항식과 원시 weight 합 | 원래 `3/10^15` normalization/P2/P4 gate, 같은 P6 gate, 양수성과 반사 parity 모두 충족 |
| 12개 실제 저장 weight의 Taylor 행 | 독립 D0–D4 Legendre 전개와 `G=-F'/2`, 정확 급수 나눗셈 | 실제 응답·bias 계수와 P2부터 P12까지 저장 모멘트 전부 정확 일치 |
| 다섯 continuum reference 점 | 양의 composite Simpson, 격자 refinement와 4차 미분 truncation bound | F·G·A 모두 등록 `5e-13` 진단 안에서 일치 |
| 60개 finite-ray response readback | 별도 scalar `fsum`과 직접 ray 식 | 같은 다섯 strain에서 저장 A와 일치 |
| 집계와 identity | 10개 domain, 5개 standalone certificate, main source manifest·원시 실행·입력 bits 대조 | 누락이나 잘못된 PASS 집계 없음 |

정확 certificate는 weight 합으로 재정규화하지 않는다. 원시 normalization
잔차와 각 Legendre 모멘트 자체를 계산했다. 24개 weight 목록 중 가장 큰
정확 잔차는 `b9_n64_P4`의 Rust P4 모멘트로
`1.0280045769226785e-16`이었다. gate `3e-15`는 변경하지 않았다.
모든 정확 분수와 실제 weight·방향 hash는
`c9_readback_r1/EXACT_WEIGHT_READBACK.json`에 있다.

## S8의 pointwise 정밀도 문제와 P246 support 실패의 구분

원래 S8 `INNER_P2_PRECISION_LIMIT`에서 보존한 `b9_n64` birth 11 support는
새 동시 P24 경로에서 양쪽 구현 모두 정확 gate를 통과했다. Python 최대
잔차는 정확히 `11/1152921504606846976`, Rust 최대 잔차는 위의
`1.0280045769226785e-16`이다. 최소 weight는 각각
`0.0030436855068409854`, `0.003043685506840988`로 엄격히 양수다.
방향 hash는 두 경우 모두 원래의
`10983ba1978e2c342d23e034871c9ec3588bae80bf1e0de20442d99850e08417`을
유지했다.

같은 n64 support의 P246은 예상대로 거부됐다. 독립 exact minimum facet
slack은 `-0.019107014686788677`이며, 다른 음성 control
`P24_only_support_P6`의 minimum slack은 정확히 `-1/42`다. 전체 정확
분수·facet 목록은 `c9_readback_r1/EXACT_SUPPORT_READBACK.json`에 있다.

이 차이는 정밀도 실패와 support 제약을 구별한다. `z=mu^2`에 양의 weight를
두면 항상 `E[z^3] <= z_max E[z^2]`이다. 정확 P246 목표에는
`z_max >= (1/7)/(1/5)=5/7`가 필요하지만, 저장된 n64 support의 최대 z는
약 `0.6195099475928701`이다. 더 낮은 P24의 필요조건은 `z_max>=3/5`라서
이 support와 양립할 수 있다. 이는 해당 유한 support에 대한 구체적인
실패 증거다. 모든 angular support에 관한 배제 주장이나 기존 stock의
support 변경 허가가 아니다.

따라서 이번 결과는 **원래 저장 입력에 대한 새 pointwise P24 해법**을
보여준다. 과거 S8 history 실행 결과·실패 receipt는 그대로 남고, 그 history를
재실행하거나 전체 native history의 성공으로 고쳐 쓰지 않는다.

## 독립 scalar reference의 실제 차이

등록한 strain은 `d=-0.6,-0.3,0,0.3,0.6`이다.

| 수량 | main Decimal analytic reference와 독립 Simpson 값의 최대 절대 차이 | 발생 d |
|---|---:|---:|
| F | `1.65209654547353e-16` | -0.3 |
| G | `1.4947003428522293e-16` | -0.6 |
| A=G/F | `8.244345804509617e-17` | -0.6 |

Simpson은 최대 262,144 구간까지 등록한 방식으로 refinement했다. 마지막
두 격자의 최대 변화는 모든 점에서 `2.220446049250313e-16` 이하였고,
분석적 4차 미분식에서 평가한 A truncation bound 추정치는 최대
`7.706752548414715e-15`였다. 해당 bound는 binary64로 평가한 truncation
추정이며 모든 floating 연산을 감싼 outward interval certificate는 아니다.
따라서 이 검토는 등록한 다섯 점의 구현 일치를 `5e-13` 진단으로 판정한다.
80자리 전체가 독립적으로 인증됐다고 주장하지 않는다.

60개 finite-ray readback의 최대 차이는 `P24_only_support_P4`, d=-0.6에서
`1.5925899911076854e-16`이었다. 이는 저장된 유한 quadrature의 계산을
다른 scalar 경로로 확인한 값이다. 그 quadrature와 물리적 continuum 사이의
실제 discretization error를 이 작은 차이로 바꾸어 보고하면 안 된다.

## 이후 해석에서 유지할 범위

독립 Fraction Taylor 검토는 정확 P246 조건의

\[
[d^3](A-A_{iso})=\frac{288}{143}M_8,\qquad
[d^4](A-A_{iso})=-\frac{7200}{2717}M_8+
\frac{136080}{46189}M_{10}
\]

와 실제 저장 weight의 낮은 모멘트·normalization 잔차를 구분한다. 실제
출력의 전체 계수는 그 잔차를 유지한 채 정확하게 확인했다. 고차 제약을
추가해도 임의 finite d의 오차가 항상 단조 감소하는 것은 아니다.

이 C9는 실제 MD14 donor closure·native Einstein/shear shared-Q 결합,
evolving reactive full finite-bin spectral history, 새 Rust client의 full
birth-memory parameter tangent 또는 더 넓은 angular/finite-d 수렴을
완료시키지 않는다. S10의 제한된 source-deposition 잔차
`5.369926725506957e-12`를 full spectral-history 수렴으로 확대하지 않는다.
기존 owner, birth source frame, old stock과 과거 birth weights도 바꾸지 않는다.

기존 S9/S10 및 독립 검토 155/155는 이전 증거로 재사용한다. 여기의 235개는
새 checker의 별도 검사 집합이며 과거 집계에 합쳐서 새 캠페인을 완료한 것처럼
표현하지 않는다. 출력·원시 실행·수학 요약의 전체 파일 hash는
`C9_NUMERICAL_SUMMARY.json`과 각 receipt에 남겨 후속 게시·이중 backup/readback에
사용할 수 있게 했다.

# N4: 기존 native 수신 결과의 C02B 연결

2026-10-11 KST에 최신 BASS PR137–139의 실제 source, 계약, 실행 receipt와 독립 판정을 읽었다. **N4의 두 frozen history 수신은 PR137에서 이미 완료되어 있었다.** 따라서 새 solver, receiver, reference 계산이나 기존 테스트를 실행하지 않고 C02B와 기존 수신 증거의 identity를 연결했다. 상태는 `DONE_SOURCE_REUSED`이며 범위는 FLRW와 초기 전단비 r=+0.1의 각 16,384개 셀이다. REI 전체 14개 sensitivity case에 대한 BASS 수신 판정은 아니다.

기준은 BASS `8904c18e65095cac0fa0526edc364317fcdc953f` ([PR137](https://github.com/cosmosapjw-quantum/bass/pull/137))이며, 현재 연결 branch는 PR139의 `41fa2d5f6874a6d9eb1a151ff83b2d56f1d2fd25`를 부모로 한다. PR139는 추가 wrapper만 도입했고, PR137에서 실행된 `fixed_time_optical_depth`, `with_observer_tail`, `integrate_visibility`의 함수 본문과 PR137 example은 그대로다. 함수 및 source byte identity를 확인했다. 이 identity 검사는 과학 결과를 새로 계산했다는 의미가 아니다.

## 입력과 물리적 의미

원본 열은 `t0_s,t1_s,mean_z0,mean_z1,ne_eff_m3,delta_tau`이다. t는 z=20에서 시작한 proper/normal elapsed seconds, z는 평균 부피 redshift, 전자밀도는 proper m^-3이다. 비틸트 물질계에서는 두 시계가 일치한다. native receiver는 추가 a^-3, (1+z), Doppler 계수를 곱하지 않는다. HeIII·잔여전자·열진화를 역으로 복원하지 않는다.

REI exporter의 유효밀도는

\[
\bar n_{e,i}=\frac{\Delta\tau_{i,\rm REI}}
 {c\sigma_{T,\rm REI}(t_{i+1}-t_i)}
\]

로 정의된 producer quadrature의 셀 평균이다. 그러므로 native 적분과의 일치는 **projection/상수/단위/시계 연결의 검증**이며, 이미 수행된 REI history 정확도의 독립 재검증이 아니다. source/closure는 R15 유효 방출률, HG97 Case-B, T=20,000 K, C_HII=3, 이온화 영역의 HII+HeII 및 filling factor Q이며, 원래 별도 Case-A/native photon network와 혼동하지 않는다.

두 code의 Thomson 상수는 REI 6.6524587321e-29 m², BASS 6.6524587e-29 m²로 다르다. 밀도나 상수를 조용히 수정하지 않고

\[
\Delta\tau_{i,\rm BASS}=\rho\Delta\tau_{i,\rm REI},\qquad
\rho=\sigma_{T,\rm BASS}/\sigma_{T,\rm REI}
=0.9999999951747164\ldots
\]

를 기존 판정과 그대로 유지한다. 두 계수에 공통인 c=299792458 m/s도 명시한다.

## 실제로 재사용한 수신 증거

| quantity | FLRW | r=+0.1 |
|---|---:|---:|
| 최대 backward τ 절대오차 | 4.18991e-16 | 1.82080e-16 |
| 동결 τ 허용오차 | 2.73090e-13 | 2.72900e-13 |
| 최대 셀 확률 상대오차 | 7.49082e-16 | 4.68505e-16 |
| 유한 구간 확률질량 보존오차 | 4.44089e-16 | 2.22045e-16 |

이는 upstream의 `PASS_SCOPED` 실행 및 독립 검토 수치를 읽어 인용한 것이다. 새 수치 PASS를 생성하지 않았다. 첫 V1 literal-header 실패, 이어 raw decimal-text oracle의 832개 cell 실패는 삭제하거나 PASS로 고치지 않았다. V2는 native가 파싱한 binary64 입력을 Decimal60으로 옮기는 oracle로 별도 선언·검토되었으며, 물리·허용오차를 바꾸지 않았다.

새 identity-only 실행은 exit 0이었다. C02B의 producer payload 5개, 기존 receiver source, native 함수 3개, saved stdout 2개의 hash/byte identity가 맞았다. C01과 C02B의 archive identity는 서로 다르지만 그 안의 해당 과학 payload는 같다. 세부는 `evidence/EVIDENCE_IDENTITY.json`에 있다.

## 관측량의 범위와 다음 연결

셀 rate는 q_i=cσ_T n̄_e,i이며 τ_i=Σ_{j≥i}q_jΔt_j이다. native cell probability는 `exp(-tau_right)*[-expm1(-q_i*dt_i)]`이고, segment 끝의 경계 τ_end=0을 사용할 때 `survival[0]+ΣP_i=1`이다. 이는 미래의 segment 끝까지의 조건부 경계 커널이며 interval probability를 재정규화하지 않는다. 실제 observer까지의 tail은 `UNKNOWN`, total/observer visibility는 null이다. 평균 z=20→4를 directional observed-z 구간으로 해석할 수 없다. 또한 셀 평균으로는 실제 내부 visibility peak를 결정할 수 없다.

BASS PR138/139에는 별도로 REI `51da705e4f24bd201444ac3e81db495b50a7d8f7`의 20개 cold IVP snapshot 수신과 5-edge finite schedule visibility가 있다. 그 결과도 읽었으며 full redshift/continuum/late-time 결과로 승격하지 않았다. N1/N2에서 새로운 physical history가 나오면 그 history의 source·density·time·closure를 별도로 고정하여 receiver에 연결해야 한다. 현재 N4를 다시 대기 상태로 만들어 동일 RUN002를 반복할 이유는 없다.

이번 연결 파일은 `ADOPTION.json`이다. REI DAG에서 N4를 `DONE_SOURCE_REUSED`로 바꾸되 새 integration의 독립 closeout은 부모 담당자가 수행한다. 원래 CR/RCT/H/He/열진화 gates는 그대로 유지한다.

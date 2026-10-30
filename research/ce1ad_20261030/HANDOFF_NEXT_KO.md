# BASS CE1-AD | 한정 연구 단위 종료 인계

$physmath-research-loop $scispace $exa $wolfram

```ini
PROJECT=cosmosapjw-quantum/bass
COMPLETED_UNIT=CE1AD_ORIGINAL_CONTINUUM_41SAMPLE_L4_THIRD_GRAM_LAMBDA3_CERT
PARENT_PR=280
PARENT_HEAD=15dd3ad604f0219132984b7b23538ef91aeff87e
ORIGINAL_SOURCE_SHA256=022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035
UPPER_DAG=9/15
UPPER_EDGES=21
CE1=PARTIAL
SCOPED_R_C=18/20
SAMPLED_41_LAMBDA3_CERTIFIED_CONDITIONAL=true
SAMPLED_LAMBDA3_SIMPLE_STRICT_LOWER=3e-12
THIRD_MODE_INTEGRAL_OPERATOR_QUANTITATIVE_BOUND=UNRESOLVED
R6_DISTINCT_AUTHOR=NOT_RUN
C9_DISTINCT_AUTHOR=NOT_RUN
PRODUCTION_READY=false
MERGE_READY=false
AUTO_NEXT=false
STOP_AFTER_ONE_BOUNDED_UNIT=true
```

## 신규 과학

- 기존 Gram-Weyl bound는 ∼7.7e-6으로 λ3∼5.7133e-11을 인증하지 못했지만, 41×3 `X`의 최소 특이값 직접 오차전파로 수정.
- 원본 PR275 MPFR192 exact-hex alpha 41행과 정확 rational √2, Sylvester 증명으로 `σ3(X_GL_ref)>7.549e-6` (GL6/8 둘 다).
- 원본 PR277 geometric+IVP Frobenius ∥ΔX∥ bound, PR270 exact angular source component error를 더함.
- 원래 exact six-cell continuous Einstein–Vlasov 41 sampled λ3 엄격 하계: GL6 >3.0396997379466069e-12, GL8 >3.1376742164558589e-12. 공통 >3e-12. 선행 정리·구현 조건부.
- 새 82 time-sample third-mode X·amplitude·derivative 물리 데이터, 두 zero crossing 구간; 실제 GL time-sampled source 데이터에서 산출한 관측량. 원시 CMB temp/polarization likelihood 아님.

## 재현

```
python research/ce1ac_20261030/source/l4_kinematic_history.py
python research/ce1ad_20261030/source/restore_original_inputs.py
python research/ce1ad_20261030/source/certify_sampled_lambda3.py
python research/ce1ad_20261030/source/physical_third_mode_atlas.py
python -m pytest -q research/ce1ad_20261030/source/test_ce1ad.py
```

S0/S1/S2 ZIP와 20개 R/C stage checkpoint는 다음 스레드의 exact paths에 있고, GitHub 새 Draft HEAD/CI는 실제 게시 후 readback metadata를 SSOT로 한다. 이전 PR #273/#275/#277/#280, main, sibling KM2 계열에는 mutation하지 않는다.

**다음 후보만**: quantitative continuous-time spectral gap 또는 independent distinct-author R6/C9 및 CE1 full completion gate. 추가 승인 없이 후속 node 실행하거나 merge하지 않는다.

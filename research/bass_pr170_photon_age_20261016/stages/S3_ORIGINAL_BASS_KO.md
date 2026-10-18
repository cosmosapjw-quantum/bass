# S3 | 실제 BASS Einstein–Vlasov b(x)에서 old/born photon angular stress 연구

Source owner는 [BASS PR169](https://github.com/cosmosapjw-quantum/bass/pull/169) `6fb32b51390e4f722692505bf7a3ace2448aada6`, 이전 PR164 source-formula tangent Git blob `1cab2bf7eab5a306ab207206ca3a0fc793dc9163`, 실제 canonical FD96 source Git blob `8467932c3281f9d426712b3a582f2aae3a484692`이다. 원래 FD96 massive Einstein 진화 및 source reference를 읽기만 했으며 원본 repository는 수정하지 않았다.

## 실제 실행

`python run_bass_campaign.py --out evidence/S3_CAMPAIGN_FINAL` (ChatGPT isolated container; native REI 및 NCP NOT_RUN). 총 18개 과학적 경우(질량 3,30,300; 초기 사중극 A±0.5; old photons only, source-only, combined), 각 65시각 = **1,170 physics rows**. Born-at-u source는 **제조된 양의 isotropic bolometric source** `S(x)=0.25 exp(-0.8x)[1+0.15 sin(4x)]`이며 원래 REI/MD14 질량당 광자수/emissivity가 아니다. rho_old=1은 arbitrary positive tracer-density unit이다.

- 모든 경우 positive principal photon pressures, exact birth-time redshift stress and independent local two-state memory ODE 확인.
- 최대 |U,M| birth quadrature와 독립 DOP853 ODE 차: `1.0400992567216605e-11` (무차원 tracer energy unit 또는 energy × b).
- 최대 직접 energy-work+dilution+birth ledger 절대잔차: `2.7200464103316335e-15` (같은 physical volume energy density unit).
- Exact vs linear source-age stress의 전체 궤적 최대 분율 차 `3.913921903492959e-4`, 음/양 A 양쪽 포함. 원래 BASS A=0.5,m=3 경우 source-old combined 끝점: `b=0.00149040868198984`, `Delta_photon=-1.933712985750175e-05` (선택한 tracer unit); m=30 `Delta=-4.1222756302371193e-7`; m=300 `Delta=-4.184981604961442e-9`.
- Born-only / old-only / combined 물리량은 같은 고정 b(x)에서 원리적으로 가산적이며 회귀 테스트로 확인했다.
- 더 큰 제조 변형 `b(x)=0.28 sin(1.6x)+0.02x`에 대한 나이·각도 독립 GL16/32/64 및 GL256 comparison: 예로 angular GL8의 Delta 이산 차이는 `5.7222e-7`, GL16은 `2.9706e-10`, GL32는 `1.2707e-16`이다. 이는 SOURCE MANUFACTURED angle quadrature, not Verner cutoff, not rigorous continuous integration bound.

## 독립 old-radiation stress/backreaction 상계, 원래 Ωr 재고 대체

사용자 REI 입력 `Omega_r=9.2e-5`는 원래 BASS IVP의 H²에 이미 완전히 포함된다. 이는 photons+other ultrarelativistic species의 rounded isotropic stock이므로, `f_gamma` fraction of that EXISTING Omega_r, `0<=f_gamma<=1`, 재고를 새로 더하지 않고 **born before x=0, initially isotropic, collisionless**이라고 선택하는 조건부 1차 응답을 `coupled_lrs_gamma.py`에서 별도로 계산한다. 공급원 `S=0`, 광자 흡수, gas recoil, 수정한 H² isotropic matter budget 없음.

```
Delta_gamma(x)/A = -(8/5) f_gamma (Omega_r/a_ref^4)e^(-4x) B(x)
v'_A=-3v_A+[H0²/(H_ref Hbar)]{C_m(alpha-kappa B) + Delta_gamma/A}
B'=H_ref v_A/Hbar
```

`f_gamma=0`는 BASS PR169 original massive-only tangent에 회귀한다. 엄밀한 dust-lower-bound retarded contraction estimate는

```
q_gamma <= (16/15) f_gamma Omega_r / [Omega_m(1-f_m)a_ref] (1-e^-X)
```

여기서 `f_m=0.1`, `X=ln(21/5)`이면 최대 `0.005538389182833628`. massive + old-gamma 총 수축 상계는 질량 3/30/300에서 `0.0702810282, 0.00750719949, 0.00555866809`, 모두 1 미만. Numerically `f_gamma=1`에서 마지막 b_A에 대한 old-photon shear backreaction suppression은 각각 **0.0857856%, 0.0896739%, 0.0898160%**였다. Source-age born new photons 실험의 isotropic stock은 이 background에 추가하지 않았고 그러므로 이 수치를 native chemistry/EoR full source가 낳는 backreaction으로 간주하지 않는다.

원래 nonlinear BASS 예에서 source-free initial radiation의 Delta_gamma/Delta_massive at x_end (all existing Ωr fully collisionless assumption) 는 m=3/30/300, A=+0.5에서 약 `−0.00716808, −0.00955714, −0.00962998`. 이 endpoint local stress 비와 integrated shear suppression은 다른 observable이고 직접 같을 이유가 없다.

## 결함·수정·남은 범위

첫 S3 테스트에서 JSON 결과 필드명을 max_abs_memory_U_M... 대신 max_memory_U_M...로 잘못 참조하는 **test-only KeyError**가 발생했다. 실행 코드·물리 입력을 변경하지 않고 테스트 참조만 교정하여 독립 11개 S3 테스트와 S2 포함 총 **31/31 unittest PASS**. 두 로그 보존.

본 결과는 derivative-free collisionless photon/source-age operator와 **nonlinear BASS prescribed b** 및 old-only first-order Einstein coupling을 구분한 것입니다. Emission/absorption reaction partner, native H/He, actual gamma/nu opacity, photon number/spectrum, polarization, gas momentum Q^a, full EoR, original REI PR173 threshold optics 또는 NCP speedups는 NOT_RUN/HOLD. 최종 입수·과학적 승인은 별도 검증이 필요.

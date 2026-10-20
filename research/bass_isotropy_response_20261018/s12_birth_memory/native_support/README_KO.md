# 완료된 native 각도 원자료로 검사하는 고정 P24 지지점

이 후속 단위는 S8에서 이미 완료된 `b9_n64_prior` 행의 **실제 native 각도**를 읽어, 동일한 고정 64-ray 지지점 위에서 P2/P4 영점 조건을 만족하는 양의 birth 가중치가 존재할 수 있는지 판정한다. 새 geometry, projector, ODE, photon history를 실행하지 않는다. 이 문서를 작성한 시점에는 새 exact observer를 실행하지 않았다. 첫 불가능 birth의 번호는 실행 결과로 결정하며, birth 13이라는 예상치를 결과로 쓰지 않는다.

## 1. 원자료와 mode 독립성

[원 행](inputs/B9_N64_PRIOR_ORIGINAL_ROW.json)은 완료된 S8 gzip의 0-based 9번째 행을 줄바꿈 없이 그대로 추출한 127,969 bytes다. SHA256은 `6d186ca2885afb4f3fd53cfa03ba243e3444338ad87f921d53914f91ff197f76`이다. [INPUT_PROVENANCE.json](INPUT_PROVENANCE.json)에 d0 archive commit, 원 URL, gzip 959,031 bytes/SHA256/Git blob, 압축 해제 전체 SHA256와 추출 위치를 기록했다. Observer는 원 gzip 전체를 읽어 이 관계와 18행 completion owner를 검증한다. 이는 옛 계산의 재실행이 아니다.

`prior` 행의 가중치를 P24 해로 쓰지 않는다. 오직 μ, reference ν, u, b와 고정 구성만 사용한다. b0=0.9, beta=0.2, n_mu=64, n_energy=96, cells_per_segment=32, cohorts=16, x_observe=1.0이 원 실패 case와 같다. u는 원 probe의 `0.8*(j+0.5)/16.0`, b는 `0.9+0.2*u`의 **연산 순서까지** 대조한다. [원 실패 입력](inputs/ORIGINAL_S8_FAILURE.json)의 birth11 μ 64개 및 reference ν 64개는 각 binary64 bit와 대조한다. 원 `INNER_P2_PRECISION_LIMIT` 기록은 보존한다.

[원 probe](baseline_probe/native_angular_refinement.rs)의 geometry 생성 및 ray_geometry 호출은 mode 분기보다 먼저 실행된다. mode는 weights와 inject 경로를 선택하며 geometry에 전달되지 않는다. 고정 owner `0e25846433170d0f420c4cda44a0bedbf02cd177`의 [ray_geometry](owner_readback/rust/rei_microphysics/src/axbi_covariant_transport.rs)는 reference direction과 geometry snapshot에서 μ를 만들며 기존 photon state와 birth weights를 읽지 않는다. [CharacteristicRay](owner_readback/rust/rei_microphysics/src/bianchi_i.rs)와 [축대칭 geometry](owner_readback/rust/rei_microphysics/src/axisym_contract.rs)의 readback identity는 [owner manifest](owner_readback/READBACK.json)에 있다. 따라서 완료된 prior 행의 support는 같은 schedule의 P24 attempt에도 적용된다.

## 2. 기존 gate를 포함하는 정확한 증명

저장된 binary64 μ를 정확한 유리수로 읽고 $z_i=\mu_i^2$로 둔다. 반사쌍의 같은 z를 합치더라도 양성의 의미는 유지된다. $\alpha_i\ge0$에 대해 $n=\sum_i\alpha_i$, $M_2=\sum_i\alpha_i P_2(\mu_i)$, $M_4=\sum_i\alpha_i P_4(\mu_i)$이면

$$
\sum_i\alpha_i z_i=\frac n3+\frac{2M_2}3,\qquad
\sum_i\alpha_i z_i^2=\frac n5+\frac{4M_2}7+\frac{8M_4}{35}.
$$

정렬된 서로 다른 z의 moment polygon은 인접 두 점 a,c의 `(z-a)(z-c)`와 양 끝점의 `-(z-z_min)(z-z_max)`가 만드는 모든 facet으로 주어진다. 두 다항식 모두 실제 이산 지지점에서 음수가 아니다. 목표 (1/3,1/5)가 모든 facet의 양의 쪽이면 완전한 2차원 내부이고, 모든 지지점에 엄밀히 양의 weight를 주는 해가 존재한다. 경계의 해는 모든 weight 양성을 승인하지 않으며, 음의 facet은 정확한 목표가 밖에 있음을 뜻한다. 이 존재 판정은 부동소수점 KL 반복의 수렴을 대신하지 않는다.

일반적인 $q(z)=a_0+a_1z+a_2z^2$에 대해

$$
\sum_i\alpha_i q(z_i)=An+BM_2+CM_4,\quad
A=a_0+\frac{a_1}3+\frac{a_2}5,\quad
B=\frac{2a_1}3+\frac{4a_2}7,\quad C=\frac{8a_2}{35}.
$$

기존 절대 gate $\epsilon=3/10^{15}$, 즉 $|n-1|,|M_2|,|M_4|\le\epsilon$을 유지한다. 따라서

$$
A+\epsilon(|A|+|B|+|C|)<0
$$

인 facet이 있으면 어떤 비음수 weight도 그 세 gate를 동시에 통과하지 못한다. 모든 계산이 exact Fraction이므로 작은 음수를 임의로 영점으로 바꾸지 않는다. 음수 weights나 완화한 tolerance를 도입하지 않는다.

간단한 독립 필요조건도 기록한다. $Z=\max_i z_i$이면 $q=z(Z-z)\ge0$이므로 정확한 isotropic 목표에는 $Z\ge3/5$가 필요하다. 이 다항식의 A=Z/3−1/5, B=2Z/3−4/7, C=−8/35를 위 식에 넣으면 원 tolerance를 포함한 불가능 증명이 된다. Z≥3/5만으로 가능성을 승인하지 않고 반드시 전체 facet도 확인한다.

## 3. geometry 해석과 오차 범위

Non-tilted axisymmetric Bianchi I, (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b)를 유지한다. 같은 represented reference ν와 b에서 이상적인 geometry는

$$
z_{\rm ideal}=\frac{\nu^2}{e^{6b}(1-\nu^2)+\nu^2}
$$

를 준다. 이것으로 실제 native μ를 대체하지 않는다. owner에는 hypot 정규화 등 부동소수점 연산이 있으므로 actual μ와 ideal 식은 rounding bits가 다를 수 있다. 증명은 저장된 실제 μ만으로 완결된다.

해석 보조로 x=6b≥0에서 N=64의 양의 Taylor 합 S_N과 다음 항 t_(N+1)를 exact Fraction으로 만든다. x<N+2이면

$$
S_N\le e^x\le S_N+\frac{t_{N+1}}{1-x/(N+2)}.
$$

이를 z 식의 분모에 넣어 엄밀한 유리수 구간을 얻고, actual z_max와 구간 양 끝점의 최대 거리로 native와 ideal 값의 차이를 상계한다. libm의 ulp 정확도를 가정하지 않는다.

## 4. 실행·판정 범위

[사전등록](PREREGISTRATION.json)과 [observer](certify_support.py)를 실제 Git commit에 먼저 게시하고 전체 bytes/SHA256/Git blob readback을 받아야 한다. Observer는 그 source binding과 SOURCE_MANIFEST를 대조한다. 입력은 원 gzip이며 출력은 exact certificate16개, 원 token/bit readback, 고정 유리수 control3개다. 이 새 산술 점검만 1worker,60초,256MiB 안에서 수행한다.

새 source commit은 observer의 identity다. 원 S8 archive commit, owner commit, S12 compile-only source를 합치지 않는다. Observer는 compile receipt나 binary에 의존하지 않는다. 초기 geometry Rust 초안은 사용하지 않으며 실행0회의 로컬 초안으로 남긴다.

S11의 birth11 pointwise repair는 재사용한다. 이후 같은 고정 support에 불가능 판정이 나면 원 precision 실패와 구분된 **뒤쪽 birth의 유한 지지점 제한**을 보고한다. 이는 이 고정 n64 case의 단순 재시도가 완전한 16-birth PASS를 보장하지 못한다는 뜻이며, continuum이나 모든 P24 알고리즘의 불가능성은 아니다. 원 stock, birth weights, source frame, owner, schedule은 바꾸지 않는다. native finite-bin 전체 보존, 실제 MD14 정규화, shared-Q Einstein/shear coupling, full spectral history와 full EoR 완료를 주장하지 않는다.

## 5. 원문 근거

- [원 S8 압축 evidence](https://raw.githubusercontent.com/cosmosapjw-quantum/bass/d0c0313d6c063037fd8e067744aee66235df1a58/research/bass_isotropy_response_20261018/evidence_s8_native/run01/NATIVE_ANGULAR_REFINEMENT.jsonl.gz)
- [고정 owner ray geometry](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/0e25846433170d0f420c4cda44a0bedbf02cd177/rust/rei_microphysics/src/axbi_covariant_transport.rs)
- [고정 owner characteristic pullback](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/0e25846433170d0f420c4cda44a0bedbf02cd177/rust/rei_microphysics/src/bianchi_i.rs)
- [완료된 S11 positive KL 이론](https://github.com/cosmosapjw-quantum/bass/blob/85d5833b4486d14855b84a9d967f5819788d05e5/research/bass_isotropy_response_20261018/s11_p246/THEORY.md)

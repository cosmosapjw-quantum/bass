# BASS KM-2H | 원본 HYREC-2 × CLASS FLRW 회귀실험 (FLRW-FIRST)

- 날짜: 2026-10-30; 기존 BASS PR279 HEAD `b7faa761af032c68b86aec0ae30b61b817171669` 불변 부모.
- 구간: 정확히 FLRW 재결합·광학깊이·전자 수밀도·Thomson 불투명도 비교. KM2H Bianchi-I 실험은 이 단계에서 새로 실행하지 않음.
- 상위 DAG **9/15, KM2 PARTIAL, 새 상위 노드 0**; production=false, merge=false, auto_next=false.

## 실제 재실행과 환경

* 사용자 업로드 HYREC-2 원본 ZIP SHA256 `f0b8bba1547ae9da83a0e663f57056884c689683396e1cf9a58bee1904040ac0`.
* CLASS 원본 ZIP SHA256 `d1b2e1ce2b49de472e2cca9a327dc51c351e75bc0a2ad37d2e6538df76b289b7`.
* HYREC-2는 원본 C 소스에서 `gcc -O3 hyrectools.c helium.c hydrogen.c history.c energy_injection.c hyrec.c -lm -o hyrec_regression`로 새 컴파일 후 `./hyrec_regression < input.dat`를 실행. 초기 `gcc -lm -O3 ...` 실험은 링커 순서 문제로 FAIL했고 코드/물리 오류가 아니었음. 실행 출력은 `output_xe.dat`이며 원본 코드가 그 파일을 제거하고 다시 생성하므로 별도 사본에서 실행했음.
* CLASS는 이전에 사용자가 첨부한 소스로 만든 `class` 바이너리를 새로운 단독 작업 디렉터리에서 실행. 코어를 새로 재컴파일했다는 주장은 하지 않음. 입력은 동봉한 HYREC `input.dat`의 `h,Omega_b,Omega_cb,YHe,Neff,m_ncdm,T0`를 맞추고 재이온화를 끈 독립 ini.
* fresh native stdout의 물리 출력: `z_rec=1088.669130`, `z_*=1089.753288`, `z_d=1059.971729`, `r_s(z_rec)=144.665737 Mpc`, reionization disabled.
* 실제 FLRW native HYREC 8000 원시 행. 각도/재결합 비교 그리드 `z=1..1600` 1600행.

## 원본 바이트 회귀

- HYREC native 새 출력 366893 bytes SHA256 `1ac2ddad6aa0e3c4080883c71479e2e398669468e4813075ec61bca86b7afc40`; 보존된 초기 원본 파일과 byte identity PASS.
- CLASS thermodynamics 새 출력 8557352 bytes SHA256 `43e38f89b97db00b9ffc65125fe8c2e2871e3ce8b6583cb4146a1636187aeb06`; 최초 native reference와 byte identity PASS.
- CLASS background 새 출력 23080779 bytes SHA256 `c1abe910f79ffc7c2b57abd545d063f6c7725b1e3267f81c9631c2e9805f76c9`; reference byte identity PASS.
- 세 출력의 일치성은 **같은 실제 소스/입력/환경에서의 회귀**이지 HYREC와 CLASS의 완전히 별도 원자물리 이론 인증이 아님. CLASS HyRec2020과 HYREC-2는 원자 C 소스를 상당 부분 공유함.

## 새 물리 계산과 독립 단위 검사

CLASS `kappa_prime` [Mpc^-1]은 conformal optical-depth derivative, HYREC 표의 xe는 수소 원자핵당 전자비이며 고온일 때 1보다 클 수 있음.

`n_e(z)=n_H0 (1+z)^3 x_e(z)`,
`Gamma_T(z)=n_e(z) sigma_T c` [s^-1],
`kappa_prime(z)=n_e(z) sigma_T Mpc/(1+z)` [Mpc^-1].

CLASS κ(z) 및 H(z)를 사용해 HYREC xe를 같은 FLRW 배경에서 hybrid opacity로 교체했고, τ는 
`tau_hybrid(1)=tau_CLASS(1)`, `d(tau_hybrid-tau_CLASS)/dz=kappa_CLASS_prime/H_CLASS * (xe_HYREC/xe_CLASS-1)`로 적분하였다. **HYREC가 독립적으로 τ 전 이력을 계산했다는 뜻이 아님**.

- CLASS native `z_rec=1088.669130`와 `z_star=1089.753288`. HYREC/CLASS-H 혼합 `z_star=1089.759980740`, 차이 `0.006692740`.
- `800 ≤ z ≤ 1500` 최대 `|xe_HYREC/xe_CLASS-1|=0.00026128657945` (z=804). `z=1100` 상대 차이 `-3.05411537869e-05`.
- `800 ≤ z ≤ 1500` 최대 물질 온도차 `0.6357814468 K`; 최대 optical-depth 절대차 `0.000266690355531`.
- CLASS κ'에서 역산한 `nH0=0.189982435793 m^-3`; z=300..1500 source identity 잔차 `1.43676537334e-09`; FLRW SI opacity identity 잔차 `1.4367651513e-09`.
- `z=1100` Γ_T/H_CLASS = `14.2631433727`.
- 1-z 격자의 HYREC/CLASS-H hybrid visibility 최대점은 z≈1089 ±1. CLASS의 native `z_rec=1088.669`와 미세차이를 0으로 오인하지 않고 **그리드 정확도 차이로 별도 기록**.

## Blind-style hostile self review and limits

15개 별도 pytest를 fresh Python3.13.5/Numpy2.3.5/SciPy1.17.0에서 실행. 최종 `15 passed` (실제 stdout 첨부). 체크: 파일 원본 해시, 바이너리 재생성 byte identity, HYREC 8000행/FLRW 1600행, CLASS native visibility 항등식, SI·Mpc 차원, 독립 H0ΩbYHe nH0 근사, 광학깊이 경계, 재이온화 제외, 고적색편이 xe>1, 음속/온도 nonnegative, 변조 실패 및 Bianchi claim guard.

**가장 중요한 실패모드:** 최신 HYREC 출력과 CLASS HyRec2020은 공유 소스를 가지므로 `x_e` 차이가 작다는 것은 상이한 원자물리 모형의 독립 일치가 아니다. HYREC/CLASS 비교 광학깊이는 CLASS H(z)에 의존. 사용자 BASS GR 모델의 `κ=0.003`, 합성 밀도비 `3.0`과 CLASS의 `Ω_b=0.049414...`는 동일한 Einstein 물질 초기조건이 아님. 본 결과로 비등방 원자 재결합률, spectral photon redistribution, x_e의 공간 방향 의존성을 입증할 수 없음. 이후 Bianchi 결합은 **새로운 외부-input 근사**로 별도 scope gate 필요.

References: Lee & Ali-Haïmoud (2020), "HYREC-2: a highly accurate sub-millisecond recombination code", arXiv:2007.14114, https://arxiv.org/abs/2007.14114. HYREC-2 original https://github.com/nanoomlee/HYREC-2. CLASS original https://github.com/lesgourg/class_public.

## 결정

`FLRW_REGRESSION=IMPLEMENTATION_VERIFIED_NUMERICALLY_CHECKED`, `Bianchi_I_ionization_admitted=NO`; top BASS 9/15, KM2 PARTIAL; no more new physics nodes until explicitly instructed.

# BASS→REI IGM: S0 13.7 eV 광자의 실제 방출부터 관측까지 단일 Thomson 산란

2026-11-01, source-conditional scientific report, Draft/HOLD.

## 원본 권한과 이번에 완성한 물리 과정
원래 REI F08 S0 H/He 두 모델(Bianchi I, FLRW) 원본의 16,001 proper-second 전자/H I 이력과 13.7 eV 단색 초기 0.05 photons/H, 지속 5e-15 photons/H/s 등방 방출을 직접 사용했다. BASS parent PR317 HEAD 18e6273f28ea67e472c919de86594f70fd1c81c9의 original source 12/12 SHA를 직접 재확인하며 BASS main, original REI code, 원래 허용오차 및 생산 계산은 변형하지 않는다.

이번 계산은 original source birth→exact Bianchi null energy/direction→incoming Verner H I photoabsorption and zero-prior-Thomson survival→cold Thomson scattering with two-polarization density matrix→outgoing energy-specific H I absorption and zero-future-Thomson survival→directional photon redshift, exact solid-angle Jacobian and parallel-transported observer Stokes를 하나의 인과적 LoS 적분으로 연결한다. 원본 S0의 H/He matter-clock/방출 prescription은 source-matched지만 원본 F08 discrete photon occupation의 exact replay는 아니다.

Original prescribed metric: H=(1.01,0.99,1.00)*10^-14 s^-1; FLRW reference H=(1,1,1)*10^-14 s^-1; signature (-,+,+,+), c=29979245800 cm/s, sigmaT=6.6524587051e-25 cm². Observer t_o=5e12 or 1e13 proper s is **not** today's cosmological z=0. Units: E1 Stokes eV / original comoving H / observed sr; N1 photons / original comoving H / observed sr. Polarization P/I dimensionless.

## 실제 물리 출력 (실행 완료)

2 branches × 2 proper-time observer epochs × 16×32 sky = **2,048** observer Stokes records; scatter chronology 2×2×12 Gauss scattering nodes = **48** time-conditional model records, not independent observations. Input photon birth 32 midpoint panels plus initial impulse, incident GL 8×16 and source-threshold-split HI Simpson8, outgoing 16×32 and postscatter HI Simpson8.

| Background | t_o [proper s] | Sky mean P1/I1 | Sky max P1/I1 | Integrated N1 / H | Integrated U1 [eV/H] | Mean t_birth [s] | Mean t_scatter [s] |
|---|---:|---:|---:|---:|---:|---:|---:|
| BI | 5e12 | 8.069394713541601e-4 | 1.2791074704292327e-3 | 2.262705075021274e-7 | 2.9622753882106233e-6 | 4.636191011298012e11 | 2.689100533374352e12 |
| BI | 1e13 | 6.659993492154344e-4 | 1.0556073919410736e-3 | 5.525993890961326e-7 | 6.9590942241923665e-6 | 1.6066770220418196e12 | 5.636203149345558e12 |
| FLRW | 5e12 | 2.7478514141053675e-15 | 4.176887755227365e-15 | 2.2627266083560162e-7 | 2.9623051872477447e-6 | 4.6361723192287355e11 | 2.6891017956141797e12 |
| FLRW | 1e13 | 2.7669233723169257e-15 | 4.196102687000351e-15 | 5.526044863124993e-7 | 6.959163292009336e-6 | 1.6066704294853196e12 | 5.636202560385757e12 |

New source-conditioned sky CSV SHA256 4b6de40b1d3327127e9eccc955520961fedee50059c9f0be31453e4291dbb031. New chronology CSV SHA256 6ad951b13d6ecedaf6384f67de29791477cbef438d0a327603a0e4e314596d1c.

## 수학과 계산 검증
- Wolfram exact angular Thomson cross-section normalization integral = 1; exact Bianchi min source energy 12.383882550536338 eV.
- Original local gain limit at t_scatter=t_observer agrees with prior PR317 source-gain at the same source/birth/angular quadrature.
- Full source-locked standard 17/17 and python -O 17/17 local unit tests PASS; source 12 original immutable inputs SHA256 PASS.
- Independent tetrad/screen ODE RK4 vs spin-two parallel transport analytic chi: 1.371515748194163e-16 rad phase residual for a nontrivial Bianchi null ray.
- Separate pure-stdlib full-output audit 2,048/2,048 Stokes sky, 48/48 scattering chronology, Stokes positivity, causal mean birth≤scatter≤observer PASS; antipodal parity max relative residual 4.783352229680565e-15; FLRW max P1/I1 4.196102687000351e-15.
- Scoped numerical sensitivity for one fixed BI observer epoch and same outgoing directions: (scatter8,birth16,GL8×16) vs (scatter12,birth32,GL12×24) mean-I +1.3774895328722003e-4, representative P +2.2504207798053066e-3. Scatter12 birth16 vs finest mean-I +2.7847683821136116e-5, P +2.2084781019349187e-4. Scatter12 birth32 GL8×16 vs finest mean-I +3.527585779039555e-9, P -2.6184469703594004e-7. This verifies sampled-quadrature sensitivity only, not physical-model accuracy, not formal numerical error bound.

## 적대적 과학 주장 제한과 drift watchdog
Crucial difference from previous PR317: this is an actual **retarded emission/scatter/observer transfer** with real energy-specific outgoing absorption and polarized screen, not a repeated local angular atlas. However the independently reconstructed continuum S0 photon distribution still differs from original F08 discrete photon population by -6.13% at final time and yields the previously documented support discrepancy (original numerical below-10-eV guard ≈0.0010016543797005872 photons/H although exact monochromatic born-13.7-eV null floor is 12.383882550536338 eV). We do not assert the sole source of this discrepancy or silently substitute original F08 photon owner. The first scattering is treated passively on frozen original matter and metric; no backreaction, no multiple-scatter field, no independent physical/atomic-model error bound, no observed Planck CMB.

This is one original-source-prescription-matched BASS first-scattered observer physics **science unit**. One-time production and an appropriate same-author hostile pass; distinct-author referee and native subagents NOT_RUN. Stop source-only follow-on atlases. To reach central REI, first resolve F05 tick160→161 original owner admission and/or F09 valid-provider binding, and original photon state equivalence for full polarized LoS.

REI CENTRAL **28/88 REPORTED**, WORKING 33/88 nonadditive, PHYSICAL FAST 4/7 REPORTED; BASS upper 9/15 scoped/source-mapped (fully complete count unknown), Δcanonical=0, Δfully completed BASS upper=0. Production HOLD, Draft unmerged, no force push, no tolerance or original owner mutation, AUTO_NEXT=false.

## Publication and preservation
One open/unmerged BASS scientific Draft [PR #319](https://github.com/cosmosapjw-quantum/bass/pull/319) stacked on immutable PR317 parent. Stage A original theory+code+tests commit cb8cec8d4d163f437b0fd1a3d3d91153b0068b58. All physics model results, numerical evidence, stage records and exact source-preserving backup belong to this ONE Draft. CI status is not asserted before actual final-HEAD logs.

Local source-inclusive 29-member ZIP /home/cosmosapjw/archives/BASS_REI_F08_S0_RETARDED_ONCE_SOURCE_FULL_20261101.zip preserved as 6,517,294 bytes, SHA256 fb73d717a0f3939128364a5ac94812ab507d8e18a78d802f5ada61ff7bd0b775. Independent cold extraction CRC/source SHA12/12, 17 unit tests, 2,048+48 record audit, and 128+16 smaller physics rerun PASS. No second-provider binary cloud readback claim. CI on the final Draft HEAD must be verified separately.

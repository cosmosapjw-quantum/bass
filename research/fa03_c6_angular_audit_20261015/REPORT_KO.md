# FA03 C6: 복소 각도 해석성과 독립 고정밀 편광 수송 검증

**선택 실행:** `physmath-research-loop 1.3.0`, BASS FA03 코딩 **C6** 구현 검증. 요청에 포함된 이론 연구는 실제 angular regularity/aliasing 유도로 수행했다. 이전 R5–R10 이론 루프를 재실행하거나 승인 없이 새 R1–R10 전체 사이클을 시작한 것은 아니다. 기반은 C5 commit `26a289c4669382f7d25ddc12abc9bb9628bc542f`. 원 R7 FA02/FA03 bytes 및 R8 fixed36 coefficient certificate **절대 불변**.

## 1. 보존된 수학·물리 정의

Signature ((-+++)\), Kasner ((2/3,2/3,-1/3)), observer ((\chi,\psi)=(1/125,1/100)), cap radius (δ=1/50\) rad, normalized solid-angle measure. Integration direction (x=t/t_o\in[1/2,1]), zero incoming 2×2 Hermitian coherency, energy band (e\in[49/50,51/50]). Source `P3`, absorption `K3=diag(0.4,0.4,0.8)`, screen rotation (0.3e_1 J_2), and actual moment source terms `M3=1.0004`, `M4=1.000800032` preserved. Analytic ε=0 six states (S_0,S_1,S_2,V_0,V_1,W_0) with original real non-grey (|ε|<=0.1). **FA03 R8 <4.75e-7 trace-norm bound is for exact finite36-ray only.**

For GL inclination (u\in[-1,1]), (μ=\cos r=1-(1+u)\sin^2(δ/2)). Normalized angular cap is precisely (du/2\,dφ/(2π)). GL2 and above integrate its first two μ moments exactly, but the propagated integrand need not be polynomial in μ or φ.

## 2. Constructive angular strip regularity theorem

Fix (x\in[1/2,1]), (r\in[0,1/50]). Extend azimuth (φ) holomorphically with (|\Imφ|\le4). For any complex φ there, (|\sinφ|,|\cosφ|\le\cosh 4<28). Therefore (writing `m0,m1,m2` for rotated local ray and (L=\cosh\chi+\sinh\chi\,m_0)),

[
|m_0-1|<\frac{\psi^2+\delta^2}{2}+\psi\delta\,28=\frac{117}{20000}<.006,\qquad
|m_1|<\psi+28\delta=.57.
]

Since (L=e^\chi+\sinh\chi(m_0-1)), (e^\chi>1), χ=1/125 and (σ:=\sinh\chi<.009), we have (|L|>.99). The boosted direction (n_0=(\sinh\chi+\cosh\chi\,m_0)/L), (n_1=m_1/L), (n_2=m_2/L) obeys the conservative rational bounds

[
|n_0-1|<.007,quad |n_1|<.58,quad |n_2|<.57.
]

Consequently the three potentially dangerous square-root factors remain in strictly safe disks:
[
|m_1^2|<.3249,qquad
|n_0^2+n_1^2-1|<.350449,qquad
|(1-x^2)n_2^2|<.243675 .
]
All are strictly less than one. Thus the branches defining (\sqrt{1-m_1^2}), (\sqrt{n_0^2+n_1^2}), (\sqrt{1-(1-x^2)n_2^2}), together with every matrix source/absorption coefficient, are analytic in the strip. For finite (x\in[.5,1]), the exact FA03 finite-dimensional ODE solution inherits angular holomorphy. Elementary strict inequalities were checked using exact Fraction and Wolfram 15.0.1 (χ,ψ,δ constants frozen). This proves an **analyticity domain, not a numerical supremum**.

For a matrix-valued 2π-periodic integrand (F(φ)) with (φ)-strip norm sup (M_4\ge\sup_{|\Imφ|\le4}\|F\|), Fourier coefficients obey (‖\widehat F_m\u2016\le M_4 e^{-4|m|}). Exact discrete Fourier aliasing of the (N)-point equispaced trapezoid yields

[
Q_NF-\langle F\rangle_\phi=\sum_{k\in\mathbb{Z}\setminus\{0\}}\widehat F_{kN}e^{ikN\alpha},
\quad
\|Q_NF-\langle F\rangle_\phi\|\le\frac{2M_4}{e^{4N}-1}.
]

At N=12 the coefficient multiplying still-unknown (M_4) is (2.85032816548\times10^{-21}), at N=16 it is (3.20762178110\times10^{-28}). **The actual (M_4) interval majorant has NOT been calculated, and neither has the radial GL3 remainder or true ODE time error.** These conditions are not a final continuum-cap certificate. Primary method literature: Trefethen and Weideman, *SIAM Review* 56 (2014), DOI [10.1137/130932132](https://doi.org/10.1137/130932132), Theorem 3.2; transfer angular-performance context Bestard Jaume et al., *A&A* (2021), DOI [10.1051/0004-6361/202039424](https://doi.org/10.1051/0004-6361/202039424). Both papers are methods, **not** claimed sources of BASS-specific numerical bounds.

The manufactured counterexample (F=\cos(12φ)) is infinitely smooth; its true mean is zero, but unshifted N=12 nodes return one. A 0.37-node shift returns (\cos(2π\times .37)) instead. This falsifies the general claim that small grid-to-grid differences on one source guarantee angular accuracy for all functions.

## 3. Actual independent 70-digit *source* computation

`mp_cap_snapshot.py` reconstructs original `fa02.setup` + `fa03.fields` without importing the original runtime solver, and evaluates the 2×2 emissivity matrix in mpmath70. A single ray's B,H,G was compared to the immutable NumPy source, agreeing in IEEE64 to B (3.33\times10^{-16}), H,G (1.11\times10^{-16}). This is not byte identity or independent physics law derivation. At (x=.7):

| rule | 70dps source-matrix component max diff vs GL6×24 |
|--|--:|
| GL2×8 | (6.972615721867\times10^{-18}) |
| GL3×12 | (5.261638801410\times10^{-26}) |
| GL3×16 | (9.630352203498\times10^{-28}) |
| GL4×16 | (4.241798404916\times10^{-34}) |

Azimuth-grid rotation +0.37node for GL3×12 gives (8.192545216981\times10^{-26}). These values resolve genuine angular dependence hidden below binary64.

## 4. Independent mpmath **full grey S0 transport** execution

`mp_full_grey.py` implements independent 2×2 matrix RK4 (\dot F=B-GF-FG^T) with same zero IC; no call to frozen NumPy integrator during the solution. Exact original model source geometry from independent mpmath coefficients, 65dps. For 64 RK4 steps:

| ray rule | whole-S0 max matrix-component difference vs GL4×16 |
|--|--:|
| GL3×12 | (2.04330333642804\times10^{-26}) |
| GL3×16 | (4.52192977832700\times10^{-28}) |
| GL4×16 | reference |

A separate **50dps, 32-step** run independently obtained (2.04330331988569\times10^{-26}) (GL3×12 vs GL4×16), differing by only ∼(8.1\times10^{-9}) relatively from the 64-step angular discrepancy despite the RK4 time truncation in each absolute solution. 64-step GL3×12 Stokes-I `0.49584821383969235052371011254751538541...` is consistent with the archived NumPy 64-step I `0.49584821383969235` to its published digits. This is a **strong implementation and numerical-discretization comparison**, not interval-enclosed ODE error.

The measured source/full-S0 angular differences ∼(10^{-26}) are much smaller than C5's binary64 36ray-to-896ray ∼(6.1\times10^{-16}), confirming its rounding-floor character. No false claim `continuous cap error<10^-26`; full six-state moment/finite-ε highprecision time integration and physical radiation+atom coupling are not yet certified.

## 5. REI owner actual read-only support

`rei_owner_readonly.py` reads only current `STATE.json`, original signed `RETURN.txt`, checkpoint paths, raw receipts and live process table. It refuses outputs inside the active REI repository, refuses overwrite and preserves source STATE byte identity. Actual snapshot HEAD `6cbdb57010a79eb3bbbc6a54b7f1a75d466702fd`, SHA state `1572eeeb12de0b7b700160a8077af25b23e673399479a66906fe788d4efc2fa1`:

- AX07 ZERO complete **scoped conditional**; AX08 signed still IN_PROGRESS; AX11/AX12 PENDING; global scientific admission NOT_ISSUED.
- Four original signed PLUS/MINUS/HALF_PLUS/HALF_MINUS RETURN all `STOPPED_CHECKPOINTED`, `accepted=200000`, `AXBI_RUNTIME_CAP`; all retain original checkpoint. This is not true physical solver failure.
- PLUS continuation `RETURN.txt` absent at readback; observer's historical `LIVE_WORKERS_OR_CHILDREN_HOLD` present. No live targeted solver at snapshot. Descriptive `HALF_MINUS_ORIGINAL_LIVE` remains stale relative to recorded terminal. An absent PID and old observer error cannot prove successful continuation or a physics failure.
- Test with synthetic repo verifies staleness detection, write prohibition, existing-output refusal and true STATE SHA unchanged before/after. Owner solver starts0, owner mutations0.

Current other lanes: rec_bianchi PR86 matches photon source time to exact prescribed background proper-time; BASS_HE PR57 warm P01 4×4/2904 optical Jacobian local derivation; bass_cr PR65 threshold-aware redshift noncommutation counterexample. None of these grants production REI science admission. We did not reuse/modify their code or compete for the Codex worker slot.

## 6. Validation/finish line

One bounded C6 stage: new **18/18** local Python tests passing after actual RED (1 assertion/test contamination +1 missing attribute), plus code compile. Prior C5 15/15 remains unchanged. Local mpmath source (70dps), full grey S0 (65dps/64step, 50dps/32step), Wolfram analytic-strip/Fourier identities all actually executed; no native subagents exposed (`NOT_RUN`). No independent academic science review. **C6 passes implementation validation at specified finite test scope**; C7 physical matching and C8 numerical error certification remain open. Parent BASS original R7/R8 input source/detector and original I–VII untouched.

Next legitimate scientific task is constructing a validated complex-strip propagated norm (M_4) for each six-state/finite-ε output *and* independent GL3 radial quadrature majorant, with actual interval arithmetic, then combining separately with the existing fixed-36 numeric remainder. Avoid any new claim about physical ionization error or observational shear without matched native production data.

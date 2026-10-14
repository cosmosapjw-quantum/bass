# FA03-R9: Bianchi-I 유한 검출기의 비회색 편광 전달 정리와 실행 인터페이스

**2026-10-14. 선택 단계 R9(정식 결과·계산 계약), 후속 R10 미실행.** 앞선 실제 논증·계산의 범위를 수학적으로 다시 명시하고 저장된 계수를 재생산 가능한 함수의 입력으로 연결한다. 새로운 측정·물리원자율, observer 전천 적분, 실제 REI chemistry solve는 수행하지 않는다.

## 1. 보존한 family와 기호

* 권위 원본은 FA02 `b453ea1a984bea55c83dd54a1545e9cd344d90a31ee2e72ab51cb338579e01d5`의 두 observer family이다. 같은 이름의 `72569f…` 3-parameter 판본과 동등화하지 않는다. 기존 I–VII/D9.1, 원 SOURCE_CLOCKS/ABUNDANCE_MODEL은 수정하지 않는다.
* 계량 signature `(-,+,+,+)`, 물리 photon momentum `p^a=(E/c)(u^a+n^a)`, `u·u=-1`, detector fixed `(χ,ψ)=(1/125,1/100)`, cap radius `δ=1/50` rad. Kasner exponents `(2/3,2/3,-1/3)`; dimensionless proper-time ratio `x=t/t_o in [1/2,1]`.
* Detector는 GL3 radial × periodic 12 azimuth **정확한 36-ray positive rule**이다. Angular label `ell`과 normalized weights는 원 R7을 따르며 합 1. Continuous angular cap과 동일한 수학적 대상이 아니다. Detector-fixed band `e=E_w/E_* in [49/50,51/50]`; 이 band의 다항식 moment는 정확한 유리수.
* Local-rest energy `E_rest/E_*=e k(x,χ,ψ,ell)`. Photons/source/absorber normal frame, zero incoming matrix at `x=1/2`; source energy plateau는 beam 경로 전체에서 고정된 동일 다항식 branch. Absorption-only affine model `K(E_rest;ε)=[1+ε(e k-1)]K_0`, `|ε|<=1/10`. Source와 antisymmetric screen rotation은 ε에 따라 바꾸지 않는다. No equilibrium/Kirchhoff or source-feedback assertion.

### [FA3.5, FA3.8–10] Exact differential family

\[
 \frac{dF_e}{dx}=e^3(1+0.1ek)P-(G F_e+F_eG^{T})
       -\epsilon(ek-1)(H F_e+F_eH^{T}),\quad F_e(1/2)=0,
\]

`G=H+Ω`, `H=ΣᵀK_0Σ/2`, `Ωᵀ=-Ω`. Hermitian coherency positivity holds at real ε due to nonnegative source and passive absorption; no clipping is introduced. For `m_j=<e^j>_band`, define `S_j=<e^j F_e|_{ε=0}>` for `j=0,1,2`, `V_j=<e^j ∂ε F_e|_{ε=0}>` for `j=0,1`, and `W_0=<∂ε²F_e|_{ε=0}>`. With `L_G X=GX+XGᵀ`, `{H,X}=HX+XHᵀ`:

\[
\begin{aligned}
S_j'&=(m_{j+3}+0.1m_{j+4}k)P-L_GS_j, &&j=0,1,2,\\
V_j'&=-L_GV_j-\{H,kS_{j+1}-S_j\}, &&j=0,1,\\
W_0'&=-L_GW_0-2\{H,kV_1-V_0\},
\end{aligned}\tag{FA3.8–10}
\]

all initial zero. Six 2×2 matrix ODEs **exactly** close derivatives through second ε-order at ε=0. For **finite ε≠0** this is *not* an exact finite six-moment closure. R6 independent 4-vector screen comparison and the noncommuting loss-factor-two discriminator preserve `∂α k` for mixed observer derivatives [FA3.11]. Those observer derivative coefficients are *not numerically interval enclosed by the current R9 target*.

### [FA03-R9-T1] Finite detector quadratic approximation theorem

Let `J_36(ε)` be the exact 36-ray observer coherency, band-integrated by exact polynomial moments and real propagation, with χ,ψ fixed as above. Let the stored 64-step RK4 reference's exact dyadic values be `\hat S_0,\hat V_0,\hat W_0`. **`W_0` is the actual second derivative, not the quadratic coefficient.** Define

\[
\widehat P_2(ε)=\hat S_0+ε\hat V_0+\tfrac12 ε^2\hat W_0.
\]

For |ε|≤1/10, the following *source-bound* trace-norm bound holds (Schatten 1-norm on the Hermitian screen 2×2 matrix):

\[
 \|J_{36}(ε)-\widehat P_2(ε)\|_1
 \le E_0+|ε|E_1+\tfrac12 ε^2 E_2+C_3|ε|^3,
 \quad C_3=\frac{926402349807}{1953125000000000}.
 \tag{R9.1}
\]

The exact `E_0,E_1,E_2` are the *parent RK4 reference versus PR146 peer interval box* bounds stored as rational pairs in `reference/R7_CROSS_CERTIFICATE.json` state entries `S0,V0,W0`. They should **not** be relabeled as the tiny intrinsic PR146 center radius. The source originally calculated 2304 full time-cell interval residuals and an independent 32-step 20th-order interval Taylor box; the later rational compatibility comparison proved all 24 component mappings and all six matrix containments. The analytic C3 came from R6's ordered Volterra/Duhamel passive-contraction proof. The stronger numerical bound inherits the PR146 certificate.

At the maximum |ε|=1/10,

\[
 E_0+0.1E_1+0.005E_2
 =7.360273381795437\ldots\times10^{-12},\qquad
 \|J_{36}-\widehat P_2\|_1
 \le4.743253633745658\ldots\times10^{-7}<4.75\times10^{-7}.
 \tag{R9.2}
\]

All decimals here are displays of the rational operands/upper bound, not claims of observed physical precision. The independent original R7 residual bound `<4.84e-7` stays valid without PR146; do not retroactively replace it. Physical band intensity requires **exactly once** the original prefactor `c*t_o*E_*²*j_*(e_+-e_-)`; c has not been set to 1. The correct observer cap-label Jacobian cancels the other inverse-square factor in the parent as already established, not a new multiplier.

### [FA03-R9-O1] Reusable intensity, polarization fraction, and eigenvalue interval

Stokes convention is the parent's `V=-2 Im F12`:

\[
 F=\frac12\begin{pmatrix}I+Q&U-iV\\U+iV&I-Q\end{pmatrix},\quad
 p=\sqrt{Q^2+U^2+V^2},\quad \lambda_\pm(F)=\frac{I\pm p}{2},\quad
 \|F\|_1=\max(|I|,p).\tag{R9.3}
\]

Denote the predicted Stokes quartet by `(\hat I,\hat Q,\hat U,\hat V)`, predicted polarized amplitude by `\hat p`, and the right hand side of (R9.1) by `r(ε)`. For any true coherency in the certified trace-norm ball, `|I-\hat I|<=r` and `||\mathbf P-\hat{\mathbf P}||_2<=r` (dual Pauli operator-norm identity). Hence with `\hat I>r`,

\[
\boxed{
\frac{(\hat p-r)_+}{\hat I+r}
\le \frac{\sqrt{Q^2+U^2+V^2}}{I}
\le\frac{\hat p+r}{\hat I-r}}
\tag{R9.4}
\]

and `λ_min(J_36)>= (\hat I-\hat p)/2-r`. One must not confuse the Stokes 3-vector norm with its individual components, nor divide by a nonpositive intensity. In `fa03_contract.py`, exact dyadic reference values and exact error fractions are read with pinned SHA256, `sqrt` is surrounded by an **integer-isqrt** bracket with a 10^-30 step, and output bounds are rational. Negative/positive epsilon cases retain the same source and cap. The tests demonstrate no silent float→rational change and no missing-error→zero coercion.

The R8 global cone lower bound `λ_min(J_36)>0.12548` remains the stronger *uniform* stated result across all ε in [-0.1,0.1]. Values shown by the R9 evaluator at individual ε are additional safe pointwise bounds. This PSD cone margin is a finite-detector **mathematical positivity** result and not observational validation of a CMB polarization pattern.

## 2. Verified use and not-yet-proved extensions

**Promote for this specified use:** Stokes `(I,Q,U,V)` of the fixed 36-ray toy detector with exact rational ε polynomial, trace-norm radius and degree-of-polarization interval for real |ε|≤0.1; symbolic LRS shear/radiation work identities. **Hold** all continuous cap quadrature, numerical joint χ/ψ interval, full finite-ε six-moment closure, exact atomic opacity/provider, self-consistent geometry/thermal/ionizing feedback, non-tilted REI physical detection. A numerical 36-ray certificate is not automatically a statement about any one of these larger models.

Original primary background: Fleury, Pitrou & Uzan (Phys Rev D 91, 043511, 2015, arXiv:1410.8473) on Bianchi I geodesics and Sachs map; Gammie & Leung (ApJ 752, 123, 2012) on covariant coherency transport. Estep (SIAM J Numer Anal 32, 1995, DOI:10.1137/0732001), Han (Applicable Analysis 94, 2015, DOI:10.1080/00036811.2014.992423), and Jawecki et al. (arXiv:1809.03369) motivate residual/error segregation. The explicit six-state closure, numeric bounds and formula (R9.4) in this exact source family are **our direct construction/consequence**, not verbatim theorem claims of those papers. External peer review/novelty comparison are pending.

## 3. Computer interface and tests

Run `python code/fa03_contract.py --epsilon '1/10' --out /new/path/output.json` in the **full capsule**. `--root` can explicitly point to another restored capsule. No writes occur if `--out` is absent; existing output files are refused. `reference/` files must match the SHA256s hardcoded in the tested code; a source mutation raises `HOLD_SOURCE_BYTE_IDENTITY`. The root includes original R6/R7/R8 archives for restoration and actual CAS code/logs. Output field names distinguish dimensionless coherency, interval error, uncalculated angular continuum error (`null`) and calibrated physical brightness (not supplied).

The R9 tests exercise the new evaluator and geometry clock only; they do not rerun 36-ray trajectories, other stages or a physical history. New symbolic R9 xAct eight zero groups are the LRS kinematics, screen and the stress-work coupling `sigma:pi=2s (P_parallel-P_perp)`. Actual Wolfram 15.0.1 separately checked the Stokes/Hermitian eigenstructure and the q^4 clock inequality.

"""
Q0 · **과학적 계약** — 코드보다 먼저 굳히는 규약·단위·오차예산 (76차).

이 모듈은 문서가 아니라 **기계가독 계약**이다.  이후 모든 Q 시험이 여기서
임계값을 읽는다 (시험이 자기 임계를 스스로 정하면 "합격을 위한 조정"이 생긴다).

세 축:
  UNITS        — 단위·시간변수·무차원화
  CONVENTIONS  — 부호·축·정규화 (기존 `bianchi.conventions` 와 패리티 강제)
  ERROR_BUDGET — PR 별 수치 임계 (PLAN-Q §6 게이트 행렬의 기계가독 사본)

그리고 §1 의 정직한 정의:
  NO_APPROXIMATION — "벗는 것" 5종 + 각각을 재는 시험 ID
  DISCRETIZATION   — "남는 것" 5축 + 기대 수렴차수

★ SymBoltz (arXiv:2509.24740, Sletmoen) 의 교훈을 명시 승계한다:
  "approximation-free" 의 핵심은 **근사 절환(approximation switching)의 부재**다.
  tight-coupling ↔ 완전결합, radiation-streaming ↔ 완전계층 같은 **영역별
  방정식 교체**를 하지 않는다.  SymBoltz 는 이를 암시적 강성 적분 + 해석·희소
  야코비안으로 달성한다.  이쪽은 충돌항이 **정확 지수**(PLAN-Q §3 식 ★)라
  **충돌 부분스텝의 안정성 강성**이 소멸하고, 남는 기하 강성만 암시적/해석
  야코비안으로 받는다 (Q10).
  ★ 87차 정정 (외부 리뷰): 원래 "강성 자체가 소멸" 이라고 적었는데 과장이었다.
  수송과 충돌은 비가환이고 nu_tau 가 재결합에서 급변하므로 **분할 정확도 제약은
  남는다** — 오차예산에서 Strang 이 정확히 2차인 것이 그 증거다.
"""
from __future__ import annotations

import numpy as np

CONTRACT_VERSION = "1.0"
PLAN = "PLAN-Q-nonperturbative-backend.md"

# ════════════════════════════════════════════════════════════ 단위·시간
UNITS = {
    "signature": "(-,+,+,+)",
    "natural": "c = G = hbar = 1",
    "time_variable": "tau",
    "dtau_dt": "H",                    # dtau = H dt  (팽창시간; 붕괴는 tau -> -inf)
    "H_normalization": "Wainwright-Ellis (expansion-normalized)",
    "Sigma_def": "sigma_ab / H",
    "N_def": "n_ab / H",
    "A_def": "a_a / H",
    "Omega_def": "rho / (3 H^2)",
    "collision_rate": "nu_tau = sigma_T n_e c / H",   # B2b §6 과 동일 (무차원)
    "momentum": "tetrad components p_alpha; p = |p|, ehat = p/p",
    "mass": "m in units of the momentum grid (m=0 => massless)",
}

# ════════════════════════════════════════════════════════════ 규약
CONVENTIONS = {
    "rotation": "COMMUTATOR",          # bianchi.conventions.ROTATION_CONVENTION
    "levi_civita": "eps_123 = +1",
    "W_matrix": "W_ab = -eps_abc R_c   (벡터 +W@Y, 텐서 +[W,X])",
    "tracefree_5": "(s00, s11, s01, s02, s12) -> s22 = -s00-s11",
    "n_ab_packing": "(n11, n22, n33, n12, n13, n23)",     # 대칭 6성분 순서
    "structure_constants": "C^c_ab = eps_abd n^dc + 2 delta^c_[a a_b]",
    "jacobi": "n^ab a_b = 0",
    "sphere_axes": "Cartesian (x, y, z);  theta from +z, phi from +x",
    "sh_convention": "real spherical harmonics, Condon-Shortley 포함",
    "angular_grid": "Gauss-Legendre in cos(theta) x uniform in phi",
    "radial_grid": "uniform in ln p  (Q4)",
    "thomson_eigenvalues": (1.0, 0.0, 0.1, 0.0),          # k_0, k_1, k_2, k_{l>=3}
    "liouville": "dp_a/dlambda = C^c_ba p_c p^b   (I1a 정리 T1)",
    # ★ Q19 (85차): tau 의 정의 dtau = H dt 와 H = dln a/dt 에서 **정확히**
    #   dln a/dtau = 1  =>  1 + z(tau) = (1+z0) exp(-(tau - tau0)).
    #   이방 배경에서도 a 는 H = adot/a 로 정의된 평균 척도인자이므로 근사가 아니다.
    #   이력(x_e(z))을 tau-적분기에 꽂는 유일한 변환이다 (bianchi/q/rate.py).
    "tau_to_z": "1 + z = (1+z0) exp(-(tau - tau0))   [dln a/dtau = 1]",
    # ★ 85차 정정 (독립 리뷰 M4): "LCDM 을 몰래 대입하지 않는다" 는 **과장**이었다.
    #   rate_mode='model' 은 H 의 **모양**만 모델에서 가져오고, **절대 규모**는
    #   H_anchor 가 정한다 (기본 H_anchor = H_LCDM(z0) ⇒ tau0 에서 두 모드가 일치).
    #   자기일관 앵커는 H_anchor='gauss' 로 Omega_0 에서 유도한다.
    "collision_rate_H": "nu_tau = sigma_T n_e c / H;  rate_mode='model' 은 H 의 "
                        "**모양**을 모델에서, **규모**를 H_anchor 에서 가져온다 "
                        "(기본 앵커 = LCDM H(z0); 자기일관 앵커는 H_anchor='gauss')",
}

# ════════════════════════════════════════════════════════════ 벗는 것 (§1)
NO_APPROXIMATION = {
    "moment_truncation": dict(
        what="l_max / i_max / n_star 및 계층 닫힘(closure) 부재",
        test="tests/test_q5_transport.py::test_no_closure_state_is_f",
    ),
    "collision_linearization": dict(
        what="Thomson 핵의 등방·소-v 전개 부재 (정확 광행차)",
        test="tests/test_q7b_boosted_collision.py::test_exact_vs_ov_expansion_scales_as_v2",
    ),
    "perturbative_expansion": dict(
        what="Sigma/N/A 에 대한 섭동전개 부재 (O(1) 이방성 허용)",
        test="tests/test_q8_einstein_grid.py::test_strong_anisotropy_no_expansion",
    ),
    "approximation_switching": dict(
        what="tight-coupling / radiation-streaming 등 **영역별 방정식 교체** 부재 "
             "(SymBoltz arXiv:2509.24740 와 같은 목표; 수단은 정확 지수).  "
             "★ 87차 정정 (외부 리뷰): 정확 충돌 지수가 제거한 것은 **충돌 "
             "부분스텝의 안정성 강성**이다.  수송과 충돌은 비가환이고 nu_tau 가 "
             "재결합에서 급변하므로 **분할 정확도 제약은 남는다** — 오차예산의 "
             "Strang 2차가 그 증거다.  '강성 자체가 없다' 는 과장이었다.",
        test="tests/test_q7_collision.py::test_no_switching_stiff_limit_exact",
    ),
    "fluid_closure": dict(
        what="rho/q/pi 는 상태가 아니라 격자 구적의 출력",
        test="tests/test_q8_einstein_grid.py::test_sources_are_quadrature_outputs",
    ),
}

# ════════════════════════════════════════════════════════════ 남는 것 (§1)
DISCRETIZATION = {
    #  축                기대 수렴차수         비고
    # ★ 78차 정정: 각 축은 **매끄러운** 피적분함수에서 스펙트럴이지만, 큰 축비의
    # 공변 캐리어 (μ 의 |cosθ| 꺾임) 에서는 대수적 2.45 차다.  두 값을 다 적는다.
    "angular":   dict(order="spectral", order_kinked=2.45,
                      note="GL x uniform; 매끄러움 ⇒ 지수 감쇠, "
                           "μ-꺾임 ⇒ 대수 2.45 (Q5b 실측)"),
    "radial":    dict(order=6.0, note="8점 Lagrange 의 실효차수 하한"),
    "interp":    dict(order=6.0, note="반-라그랑주 스텐실 차수"),
    "time":      dict(order=4.0, note="RK4 / DOP853 기하 블록"),
    "splitting": dict(order=2.0, note="Strang"),
    # ★ 82차 등재 (Mode B) — 둘 다 **지수** 수렴이라 대수 차수가 없다.
    #   ln(오차) 의 감쇠율로 적는다.  실측 스크립트: scripts/q17_convergence.py
    "modeb_angular": dict(order="spectral", decay_rate=0.60,
                          note="Mode A≡Mode B (충돌 포함) 일관성, n_theta 당"),
    "modeb_range": dict(order="spectral", decay_rate=1.74,
                        note="반경 정의역 폭 당 (해상도 아님 — 꼬리가 지수적)"),
}

# ════════════════════════════════════════════════════════════ 오차예산 (§6)
ERROR_BUDGET = {
    "Q1": dict(roundtrip="bitwise", jacobi=1e-15, ricci3=1e-14),
    # Q2 unit_norm: |ê| 보존은 **정확한 흐름의 성질**이고 RK4 는 O(h^4) 로만
    # 따라간다 — 실측 (76차): tau=10 에서 nsub 250→8000 사이 drift 가 정확히
    # 4차로 1.5e-9 → 1.8e-15 (반올림 바닥).  따라서 게이트는 (i) 4차 감쇠,
    # (ii) 명시 해상도 nsub=8000 에서 ≤ 1e-14 두 가지다.
    "Q2": dict(reduce_i1a=1e-13, unit_norm=1e-14, unit_norm_nsub=8000,
               unit_norm_order=(4.0, 0.5), order=(4.0, 0.05), nterm_l01=1e-15),
    "Q3": dict(sh_roundtrip=1e-13, proj_exact=1e-14,
               lebedev_iso=1e-12, lebedev_aniso=1e-9,
               sum_w=1e-13, ee_identity=1e-12),
    "Q4": dict(isotropic=1e-13, shift_order=6.0, tail=1e-10, vs_gl=1e-9),
    "Q5": dict(cross_invariant=1e-8, freestream=1e-10,
               i2b_exponent=(0.234, 0.002), axis_ratio=1e6),
    "Q6": dict(positivity=0, number=1e-12, lna_wall=1000.0),
    "Q7": dict(vs_taylor=1e-13, rate=1e-12, fluid_limit=0.01, stiff_x=1e6,
               number=1e-15),
    "Q7b": dict(v_to_zero=1e-13, v2_exponent=(2.0, 0.1), roundtrip=1e-10),
    "Q8": dict(vacuum=1e-12, fluid=1e-4, constraint_order=(4.0, 0.1),
               gauss_drift=1e-9, switch=1e-12),
    "Q9": dict(momentum_sum=1e-14, nr_limit=1e-6),
    "Q10": dict(strang_order=(2.0, 0.05), event=1e-10),
    # ★ 79차 정정: 스케일링 임계는 **가용 코어수 기준**으로 잰다 (이 환경은 2코어).
    #   원래 적은 6.5×@8코어는 하드웨어 가정이었지, 계약이 아니다.
    "Q11": dict(threads="bitwise", scaling_per_core=0.85,
                vs_python_reference=1e-13),
    "Q12": dict(restart="bitwise"),
    "Q13": dict(seed="bitwise", ks_p=0.05),
    "Q14": dict(roundtrip="bitwise", rss_mb=200),
    "Q15": dict(python_loop=0, overhead_ms=1.0),
    "Q16": dict(ks_p=0.05, i2b_exponent=0.234),
    "Q17": dict(order_tol=0.10, budget_factor=2.0),
    "Q18": dict(golden="bitwise", perf_regress=0.10, suite_minutes=20),
    # ── Q19 · B2b 이력 배선 (85차).  84차까지 이력은 **보관만** 되고 적분기는
    #   상수 nu 를 썼다 — 접합은 참, 소비는 거짓이었다.
    "Q19": dict(tau_z_roundtrip=1e-12,
                nu_dynamic_range=1e6,        # run 구간에서 nu 가 최소 6자릿수 변한다
                history_content_sensitivity=1e-3,   # x_e 를 바꾸면 결과가 바뀐다
                rust_vs_python=1e-13,        # Q11 표준 승계
                optical_depth=1e-3,          # int nu dtau vs 외부 광학깊이 (구적 차)
                strang_order=1.8,            # 시간의존 nu 에서도 2차 유지
                H_convention_gap=1e-3),      # 모델 H vs LCDM H 의 실측 차 (하한)
    # ── Q20 · H 앵커 lane 분리 (87차, 외부 리뷰 C5)
    "Q20": dict(lane_required=True,          # lane 미지정은 예외
                anchor_consistency=1e-3,     # phenomenology lane 의 Omega 정합
                internal_rejects_external=True,   # internal lane 은 외부 앵커 거절
                lane_gap_recorded=0.30),     # 두 lane 의 nu 차이 하한 (실측 0.338)
    # ── P8 · P 층 ↔ Q 층 합성 (84차) · P9 · 부스트·Mode B (85차)
    "P8": dict(freestream_intensity="bitwise",
               freestream_polarization=1e-8,   # 순수 RK4 절단; 각 해상도 무관
               screen_leak=1e-13, trace=1e-13,
               collide_closed_form=1e-6, number=1e-12),
    "P9": dict(psi_boost=1e-14,           # D7: 부스트 하 추가 회전 = 0
               boost_scale=1e-14,         # 배율 1 (1/D 아님)
               boost_roundtrip=1e-13,     # 정지계 왕복 항등
               v_to_zero_order=(1.0, 0.15),   # v->0 에서 O(v) (도플러)
               modeb_rust_vs_python=1e-13,
               modeb_slice_identity=1e-14),   # 반경 슬라이스 = Mode A
    # ── P 티어 (편광, 84차)
    "P0": dict(kcal_eigen=1e-12),
    # ★ 84차 정정: 무편광 왕복에 '비트' 를 요구했다가 철회.  tr = (I/2)(3−1) = I 는
    #   해석적으로 정확하지만 실제로는 세 float 의 합이라 반올림이 남는다.
    #   '비트' 는 P4 의 I-채널 자유흐름에만 남긴다.
    "P2": dict(unpolarized_roundtrip=1e-15, screen_leak=1e-13),
    "PC": dict(vs_taylor=1e-13, stiff_x=1e6, number=1e-14,
               iso_no_polarization=1e-14),
    "PT": dict(vs_coordinate=1e-12, psi_order=(4.0, 0.3)),
    "P4": dict(freestream="bitwise", collide=1e-12),
    "P5": dict(bytes_per_node=72),
    "P6": dict(linear_limit=1e-6),
    # ★ 84차: 사전 등록한 "민감도가 같다" 는 **기각**되었다 (P4 의 귀결).
    #   임계는 이제 "유의미하게 다르다" 의 하한으로 쓰인다.
    "P7": dict(xe_sensitivity_ratio=0.05),
}

# ════════════════════════════════════════════════════════════ 편광 (P0, 84차)
#: ★ 캐리어는 **기저-없는 에르미트 3-텐서** J_ab(ê) 다.
#:   그래서 Stokes 부호 규약 (IAU vs CMB 의 U 부호, V 부호, 스크린 방향) 이
#:   **아예 필요 없다**.  이 사실 자체를 계약에 적어, 나중에 누가 Stokes 기저를
#:   도입하려 할 때 여기서 걸리게 한다.
POLARIZATION = {
    "carrier": "Hermitian 3-tensor J_ab(ehat), J_ab ehat^b = 0",
    "storage": "real symmetric 6 (I + linear pol) + antisymmetric 3 (V) = 9",
    "unpolarized": "J_ab = (I/2)(delta_ab - e_a e_b)",
    "intensity": "I = tr J",
    "stokes_basis_required": False,          # ★ 규약 불필요 (기저-없는 텐서)
    "kernel": "(K J)_ab(e') = (3/8pi) Int dOmega Pi_ac(e') J_cd(e) Pi_db(e')",
    "kernel_rank": 9,                        # ★ ê 적분이 M = Int J dOmega 로 축약
    "kcal": "Kcal[M] = (7/10)M + (1/10)tr(M)delta (sym);  (1/2)A (antisym)",
    "kcal_eigenvalues": (1.0, 0.7, 0.5),     # (trace, stf, anti) — 상시 재계산 대상
    "transport": "scalar transport (x) screen SO(2) rotation psi  (D3)",
    "screen_holonomy_scale": 1.0,            # ★ 배율이 정확히 1 (D3 실측)
    "derivation": "docs/P-DERIVATION.md",
}


def _pol_eigen_parity():
    """★ Kcal 고유값을 **수치 구적으로 재계산**해 상수와 대조 (k_l 조항의 편광판)."""
    from numpy.polynomial.legendre import leggauss
    x, wx = leggauss(48)
    ph = 2 * np.pi * np.arange(96) / 96
    T, P = np.meshgrid(np.arccos(x), ph, indexing="ij")
    w = np.outer(wx, np.full(96, 2 * np.pi / 96)).ravel()
    e = np.stack([np.sin(T) * np.cos(P), np.sin(T) * np.sin(P),
                  np.cos(T)], -1).reshape(-1, 3)
    Pi = np.eye(3)[None] - np.einsum("ai,aj->aij", e, e)

    def kcal_quad(M):
        return (3.0 / (8 * np.pi)) * np.einsum("a,aik,kl,alj->ij", w, Pi, M, Pi)

    tr = np.eye(3)
    stf = np.diag([1.0, -1.0, 0.0])
    anti = np.array([[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
    got = []
    for M in (tr, stf, anti):
        K = kcal_quad(M)
        got.append(float(K[np.abs(M) > 1e-9][0] / M[np.abs(M) > 1e-9][0]))
    ref = POLARIZATION["kcal_eigenvalues"]
    return max(abs(got[i] - ref[i]) for i in range(3)) < 1e-12


def validate_polarization():
    """편광 규약 검사 — CHECKS 와 같은 형식."""
    return {"kcal_eigenvalues": bool(_pol_eigen_parity()),
            "no_stokes_convention": POLARIZATION["stokes_basis_required"] is False,
            "screen_scale_unity": POLARIZATION["screen_holonomy_scale"] == 1.0}


# ════════════════════════════════════════════════════════════ 알려진 간극
#: ★ 숨기지 않는다 — 계약이 주장 범위를 스스로 좁히는 자리 (계획 부록 A.5).
KNOWN_GAPS = {
    # ★★ 87차 (외부 리뷰) — 지금 **가장 큰 실제 physics boundary**.
    "atomic_ionization_history_is_external": dict(
        status="open",
        what="이온화 이력 x_e(z) 는 **외부에서 공급**된다.  재결합·재이온화는 "
             "아직 자기일관하게 풀리지 않는다.",
        what_is_done="어댑터는 외부 x_e(z) 를 **매 스텝 소비**한다 (Q19).  "
                     "nu_tau 동적범위 1.7e12, int nu dtau = 외부 광학깊이 2.1e-9.",
        what_is_not="그 x_e(z) 가 FLRW 팽창과 등방 복사장 아래에서 만들어진 것이면 "
                    "이는 엄밀히 **external-history lane** 이다.  자체 재결합은 "
                    "H_Bianchi, f_gamma(E, ehat), 원자 준위, Lyman-alpha 복사수송이 "
                    "함께 되먹임되어야 한다.",
        scale="이것은 솔버의 마지막 5 % 가 아니라 사실상 **별도의 physics engine** 이다.",
        remedy="로드맵: (1) transport core 동결 (2) H-anchor lane 분리 "
               "(3) 외부 정밀 재결합 provider 를 FLRW 극한에서 대조 "
               "(4) external-history + anisotropic transport lane 완성 "
               "(5) native Bianchi recombination 을 별도 프로젝트로.",
        doc="docs/REVIEW-RESPONSE-87.md C4",
    ),
    "H_normalization_two_lanes": dict(
        status="resolved",                      # 87차 C5
        what="nu_tau 의 절대 규모를 정하는 H 앵커가 사용자 선택사항으로만 남아 "
             "있었다 — 이대로면 recombination shift 가 anisotropic physics 인지 "
             "H normalization 차이인지 **섞인다**.",
        measured="모델 H 와 LCDM H 규약이 최대 33.8 % 차이; Gauss 면 자기일관 "
                 "앵커는 LCDM 앵커의 0.389 배.",
        now="lane 을 **필수 인자**로 강제한다.  lane='internal' 은 Gauss 구속이 "
            "정하는 H 만 허용하고 (외부 앵커 지정은 거절), lane='phenomenology' 는 "
            "관측 calibrate 된 앵커를 쓰되 Omega 정합을 **예외로** 검사한다.  "
            "Model.summary() 와 RateSchedule.describe() 가 lane 을 인쇄한다.",
        test="tests/test_q20_lanes.py",
        doc="docs/REVIEW-RESPONSE-87.md C5",
    ),
    "bianchi_type_coverage": dict(
        status="resolved",                      # 87차 C7
        what="초록이 '11종 전부' 를 주장하는데 대표 회귀가 I/V/VIII/IX 만 눈에 띄었다.",
        now="scripts/coverage_matrix.py -> docs/COVERAGE-11TYPES.md.  12 항목 "
            "(11 표준 + 예외형 VI*_{-1/9}) 전부 분류 왕복·유한성·Jacobi 기계정밀·"
            "Codazzi 수렴 통과.",
        falsification="처음 각주에 'class A 는 Codazzi 가 기계정밀' 이라고 적었다가 "
                      "**표 자신에게 반증**당했다.  기계정밀은 Bianchi I 뿐이고 "
                      "곡률 class A 도 1e-5 잔차를 갖는다.  차이는 크기가 아니라 "
                      "**수렴 차수**다: class A 곡률형 3.52-3.72, class B 2.28-2.70 "
                      "(A-항이 l=1 에 직접 작용 — Q5b 의 mu-꺾임 축과 같은 축).",
        gate="절대 임계가 아니라 **수렴 차수 >= 1.5** 로 판정한다.",
        test="tests/test_coverage_matrix.py",
    ),
    "residual_curvature_advection": dict(
        status="resolved",                      # 78차 Q5b
        what="공변 프레임의 잔여 곡률 이류 — 곡률항 (n, a) 이 방향공간에 만드는 흐름.",
        was="누락된 항: class B Codazzi 3.64e−3, **Δτ 8배 정밀화에도 불변**.",
        now="수렴하는 이산화: 각 해상도 n_θ 12→48 에서 9.1e−4 → 3.0e−5 "
            "(차수 2.45).  Δτ·역추적 부분스텝·보간차수에는 불변 ⇒ **각 축**.",
        why_algebraic="큰 축비에서 μ(q̂) 가 |cosθ|-형 꺾임을 갖는다 — 공변 캐리어의 "
                      "알려진 대수적 수렴 (계획 §1 이 예고한 축).",
        class_a="T4 (N-항 l≤1 = 0) 가 보호 ⇒ 잔여 이류를 켜도 구속 기계정밀.",
        measured_before=3.6424e-3,
        measured_after=3.0189e-5,               # n_theta = 48
        converged_order=2.45,
        remedy="Q5b (구현 완료) — bianchi/q/residual.py; "
               "Mode B (반경 스텐실 결합) 는 79차 `qe_residual_mode_b`",
        test="tests/test_q5b_residual.py::"
             "test_residual_error_converges_with_angular_resolution",
    ),
    # ── P 티어 (84차 독립 검증이 '적혀 있지 않다' 고 지적한 것들)
    "polarization_regime_of_validity": dict(
        status="open",
        what="P 티어 편광 연산자가 **성립하는 영역**을 계약 어디에도 적지 않았다.",
        holds="Thomson 극한 (h nu << m_e c^2), 전자 정지계 산란, 단색 (주파수 이동 없음).",
        excluded="Kompaneets/유도산란, 자기장 (Faraday), 전자 열운동 O(v^2) 보정.",
        boost="O(v) Doppler/광행차는 Q7b 가 스칼라로 다루지만 부스트가 스크린을 "
              "돌리는 각 psi_boost 는 **미유도** (D7).  ⇒ 편광 + 부스트 조합 금지.",
        remedy="D7 유도 후 P-T 에 psi_boost 를 결합하고 resolved 로 바꾼다.",
    ),
    "polarization_scalar_solver_composition": dict(
        status="resolved",                      # 84차 P8
        what="편광 캐리어가 어떤 솔버에도 연결되어 있지 않았다.",
        was="'편광 확장이 기존 수송 솔버를 깨지 않는다' 의 절반 — P/Q 합성 경로의 "
            "I 채널 일치 — 이 실행할 대상이 없어 미증명이었다.",
        now="`bianchi/q/polstate.py` (P8).  J = Ghat * Jhat 로 진폭/모양을 쪼개 "
            "진폭은 기존 Q 경로 그대로.  자유흐름 I 채널이 스칼라 경로와 **비트 "
            "동일** (Bianchi I/V/VIII/IX 전부 0.0), 무편광 유지 3e-9 (각 해상도 "
            "무관, Delta tau 차수 >=2.5), 충돌 차는 P4 닫힌형과 일치.",
        falsification="Jhat 전체를 반-라그랑주 remap 하면 무편광에서 편광이 2.97e-4 "
                      "생겼다 (Delta tau 불변).  해법은 Jhat = Pi/2 + P 로 쪼개 "
                      "**편차 P 만** 이류 — Pi(e_back) 수송은 정확히 Pi(e) 다.",
        remaining="Mode B 결합과 Rust 이식은 다음 증분.",
        test="tests/test_p8_polstate.py",
    ),
    "kcal_eigen_degrades_with_angular_resolution": dict(
        status="measured",
        what="구적 재계산 고유값 오차가 각 해상도에 따라 **커진다**.",
        measured="1.2e-15 (n_theta=16) -> 8.2e-15 (64) -> 2.0e-13 (256); "
                 "d ln err/d ln n_theta ~ +1.24 ⇒ 1e-12 교차는 n_theta ~ 2100.",
        consequence="예산 P0.kcal_eigen = 1e-12 는 실용 해상도에서 안전하지만 "
                    "'해상도를 올리면 좋아진다' 는 직관이 이 게이트엔 거짓이다.",
        remedy="n_theta <= 64 에서는 조치 불필요.  초고해상도면 Kahan 합.",
    ),
    # ── Q19 · B2b 이력 배선 (85차)
    "b2b_history_consumption": dict(
        status="resolved",
        what="B2b 이력이 **접합만** 되고 적분기에서 소비되지 않았다.",
        was="`Collision.thomson(hist)` 가 이력을 보관했지만 `Model.run()` -> "
            "Mode A/B evolve 경로에 들어간 것은 상수 `collision.nu` 였다.  "
            "저장소 전체에 매 스텝 thomson_rate(hist, z) 를 계산하는 경로가 없었다.  "
            "Q15 시험은 `m.collision.history is hist` 까지만 봐서 못 잡았다.",
        now="`bianchi/q/rate.py` (RateSchedule) 가 유일한 통로.  Rust 커널이 "
            "nu_sched(nsteps+1) + h_anchor 로 매 스텝 nu 를 계산한다 "
            "(Python 스텝 루프 0회 유지).  Mode A/B/참조 3경로 전부.",
        gates="nu 동적범위 1.7e12 · 두 이력이 다른 답 · Rust=Python 8.6e-16 · "
              "int nu dtau = 외부 광학깊이 2.0e-9 · 상수 nu 경로 비트 동일",
        test="tests/test_q19_history_wiring.py",
    ),
    "collision_rate_absolute_normalization": dict(
        status="open",
        what="nu_tau 의 **절대 규모**는 H_anchor 가 정하고, 기본 H_anchor 는 "
             "LCDM H(z0) 다 — 모델 자체 H 는 tau0 이후의 **모양**만 준다.",
        measured="tau0 에서 nu_model/nu_lcdm = 1.000000 (정의상).  Delta tau=1 구간에서 "
                 "두 규약의 nu 최대 상대차 0.338, 광학깊이 26.62(lcdm) vs 18.27(model).",
        conflict="Gauss 면에서 나온 Omega_0 (예: 0.99) 는 LCDM 의 z0 복사 밀도와 "
                 "맞지 않는다 (실측 6.63배).  자기일관 앵커는 H = 0.3885 x H_lcdm(z0).",
        remedy="`H_anchor='gauss'` 로 Omega_0 에서 유도하는 경로를 제공하고 "
               "`describe()` 가 앵커 출처를 인쇄한다.  기본값을 바꾸는 것은 "
               "외부 모듈 대조 기준선을 잃는 일이라 사용자 결정으로 남긴다.",
        test="tests/test_q19_history_wiring.py::test_q19_anchor_is_disclosed_and_measured",
    ),
    "strang_half_collide_fusion": dict(
        status="open",
        what="인접 반스텝 충돌이 **비트 단위로 같은 연산자**다 "
             "(nu1(k) == nu0(k+1), 49/49 스텝 실측; collide 는 lnH 를 안 바꾼다).",
        gain="exp(nu h/2) exp(nu h/2) = exp(nu h) 로 융합하면 정확하고 "
             "충돌 비용의 절반이 준다 — 실측 런타임 0.901s -> 약 0.68s (약 25%).",
        why_not_now="융합은 상수 nu 경로의 **비트 패턴**도 바꾸므로 Q18 골든을 "
                    "재생성해야 한다.  성능 항목이라 물리 게이트와 분리해 미룬다.",
    ),
}


# ════════════════════════════════════════════════════════════ 참조 실측
#: 이 계획을 강제한 숫자 (PLAN-Q §0).  게이트가 이 값을 재현해야 한다.
MEASURED = {
    "i2b_grid_exponent": 0.234,        # 절단 없는 격자 (기준)
    "i2b_pstf_lmax8": -0.258,          # PSTF 절단 — 부호 반전
    "i2b_fluid": 1.906,                # 완전유체 극한
    "i2c_gauss": 2e-10,
    "i2c_lna_wall": 300.0,             # Q6 가 제거해야 하는 벽
    "g1b_speedup_wholeloop": 1042.0,
    "collision_3term_vs_expm": 2e-14,  # audit/q_check_collision_exact.py
    # 77차 (Q 층 실행) 실측
    "q5_comoving_exponent": 0.233923,  # I2b 정확격자 +0.233933 과 차 1e−5
    "q5_axis_ratio_reached": 2.2e28,   # 고정 프레임이 기각된 이유
    "q8_classb_codazzi_gap": 3.5533e-3,
    "q7b_y_ratio_dT040": 1.1284,       # 해석 2차식 대비 (고차 보정 13%)
    # 78차 (Q5b)
    "q5b_codazzi_before": 3.6424e-3,   # 잔여 이류 없음 — Δτ 불변
    "q5b_codazzi_after": 3.0189e-5,    # 잔여 이류 있음, n_theta = 48
    "q5b_angular_order": 2.45,
    # 79차 (Q11 전-루프 · Mode B 잔여)
    "q11_rust_vs_python": 2.665e-15,   # 전-루프 ≡ 참조 구현
    "q11_speedup_24x48": 3.0,          # 참조 대비 (참조도 커널은 Rust 라 보수적)
    "q11_member_steps_per_s": 1236.0,  # 24×48, 2코어
    # 80차 (Mode B 정식 결합)
    "modeb_vs_modea_omega": 3.9e-11,   # 진화 후 상대차
    "modeb_freestream_identity": 1e-13,
    "modeb_y_ratio_dT020": 1.10,       # 해석 2차식 대비 상한
    # 81차 (Q7b × Mode B) — 80차 버그와 정정
    "modeb_collide_bug_before": 1.97,  # 공변 슬라이스에서 섞던 오차 (lnĜ)
    "modeb_collide_after": 8.3e-7,     # 16×32, n_p=300 정정 후
    "modeb_flux_v_exponent": 1.0,      # 부스트 플럭스는 v 에 선형
    # 82차 (Mode B 축 등재)
    "modeb_angular_decay": 0.60,       # ln(err) 감쇠율 / n_theta
    "modeb_range_decay": 1.74,         # ln(err) 감쇠율 / 반경폭
    "modeb_err_nt32": 6.36e-10,
}


# ════════════════════════════════════════════════════════════ 검증
def _rot_parity():
    """규약 패리티: Python conventions 와 CONVENTIONS['rotation'] 일치."""
    from bianchi import conventions as C
    return C.ROTATION_CONVENTION.value == CONVENTIONS["rotation"].lower()


def _eps_parity():
    from bianchi import conventions as C
    return float(C.EPS3[0, 1, 2]) == 1.0 and float(C.EPS3[0, 2, 1]) == -1.0


def _w_matrix_parity():
    """W_ab = -eps_abc R_c  ⇔  W @ Y = R × Y."""
    from bianchi import conventions as C
    R = np.array([0.2, -0.5, 0.7])
    Y = np.array([1.0, 2.0, -1.0])
    W = np.asarray(C.rotation_matrix(R))
    return float(np.abs(W @ Y - np.cross(R, Y)).max()) < 1e-15


def _thomson_parity():
    """k_l 을 하드코딩과 대조 — 수치 구적 재계산 (Q7 게이트의 원형)."""
    from numpy.polynomial.legendre import leggauss
    x, w = leggauss(64)
    K = (3.0 / (16.0 * np.pi)) * (1.0 + x ** 2)
    from numpy.polynomial.legendre import legval
    ks = []
    for l in range(4):
        c = np.zeros(l + 1); c[l] = 1.0
        ks.append(2.0 * np.pi * float(np.sum(w * K * legval(x, c))))
    ref = CONVENTIONS["thomson_eigenvalues"]
    return max(abs(ks[l] - ref[l]) for l in range(4)) < 1e-13


CHECKS = {
    "rotation": _rot_parity,
    "levi_civita": _eps_parity,
    "W_matrix": _w_matrix_parity,
    "thomson_eigenvalues": _thomson_parity,
}


def validate_contract():
    """모든 패리티 검사 실행 → {이름: bool}.  하나라도 False 면 계약 위반."""
    return {k: bool(f()) for k, f in CHECKS.items()}


def budget(pr, key):
    """시험이 임계를 **읽어 쓰는** 단일 진입점 (시험이 자기 임계를 정하지 못하게)."""
    try:
        return ERROR_BUDGET[pr][key]
    except KeyError as e:
        raise KeyError(f"계약에 없는 임계: {pr}.{key} — Q-CONTRACT 를 먼저 고쳐라") from e

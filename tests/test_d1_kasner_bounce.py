"""
D1 · **Kasner 튐 사건 검출** — Kasner(BKL) 사상을 인용하지 않고 측정한다.

Mixmaster 궤적은 Kasner 원 근처에 머물다 곡률 벽 하나가 자라며 **튄다**.  튐마다
Kasner 지수가 갈아치워지고 그 이산 사상이 BKL 사상이다.  `bianchi/integrate.py` 에
이벤트 도구(`float_event`)가 있었지만 시험 한 곳에서만 쓰이고 있었다 — 여기서 물리에
쓴다.

★ 이 파일이 고정하는 측정:
  · Kasner 좌표 왕복 — u → p → (Σ₊,Σ₋) → u 가 정확 (원 잔차 ≤ 2.2e−16)
  · ★★ **Bianchi II 를 오라클로**: 벽이 하나라 튐도 한 번이고, 그 사상이 Kasner
    사상의 기본 벽돌이다.  τ 를 **키우며** 재므로 (특이점에서 멀어지는 방향)
    나오는 것은 BKL 의 **역사상**이다:
        u_in  1.300 1.700 2.400 3.100 4.600 7.200
        u_out 1.769 1.588 1.417 1.323 1.217 1.139
        bkl(u_out) = u_in  을 **7e−14 ~ 1.9e−13** 로 되돌린다
  · ★★ **축 배정이 가지를 정한다** (u_in = 3.7):
        (1,0,2) → u_out = u_in + 1 = 4.7        (bkl 의 u≥2 가지의 역)
        (2,0,1) → u_out = 1 + 1/u_in = 1.27027  (bkl 의 1<u<2 가지의 역)
  · ★★ **D1 ↔ D2 연결**: 진공면 Ω=0 의 수치 안정성이 γ 에 달렸다.
        Ω′ = [2q−(3γ−2)]Ω,  Kasner 원에서 지수 = 6 − 3γ
        γ=0 → |Ω(12)| = 1.2e+10 (터짐),  γ=4/3 → 8.9e−07,  γ=2 → 4.6e−15 (중립)
  · ★★ **이벤트가 격자 훑기보다 낫다**: argmax 로 고르면 오차가 Δτ 에 **1차**로만
    준다 (7.2e−2 → 3.6e−2 → 1.8e−2 → 8.8e−3), 이벤트는 Newton 근이다.

★ 반증 기록 둘:
  (a) 처음엔 Kasner 원(Σ²=1) 위에 벽을 그냥 켰다.  차트가 Ω 를 Gauss 로 소거해
      두었으므로 N₁≠0 이 Ω = −K ≠ 0 을 만들고, γ=0 의 지수 +6 에 실려 Σ² 가 1e+10
      으로 터졌다.  → **진공 궤도 위로 사영**하고 γ=2 를 쓴다.
  (b) 고정 τ 로 끊고 u_out 을 읽었더니 벽이 덜 죽어 4.70107 (참값 4.7) 이 나왔다.
      → 벽이 1e−9 아래로 죽을 때까지 이어 적분한다.
"""
import numpy as np
import pytest

from bianchi.analysis import kasner as K


# ═══════════════════════════════ 1. Kasner 좌표 자기검증
@pytest.mark.parametrize("u", [1.0, 1.3, 2.0, 3.7, 9.0])
def test_kasner_coordinates_round_trip(u):
    """★ u → p → (Σ₊,Σ₋) → u 왕복, 그리고 Σp = Σp² = 1."""
    p = K.u_to_exponents(u)
    Sp, Sm = K.sigma_from_exponents(p)
    r = K.kasner_residual(Sp, Sm)
    assert max(r.values()) < 1e-15, r
    assert abs(K.kasner_u(Sp, Sm) - u) < 1e-12


def test_the_wall_grows_exactly_where_sigma_plus_is_below_a_half():
    """★★ d ln N₁/dτ = q − 4Σ₊ 이고 Kasner 원에서 q = 2 — 튐 사건의 정의."""
    for u in (1.5, 3.7):
        p = K.u_to_exponents(u)
        for perm in ((0, 1, 2), (2, 0, 1)):
            Sp, Sm = K.sigma_from_exponents(p[list(perm)])
            from bianchi.charts import class_a as ca
            y = ca.StateA.of(Sp, Sm, 0.0, 0.0, 0.0)
            assert abs(K.wall_rates(y)[0] - (2.0 - 4.0 * Sp)) < 1e-12


# ═══════════════════════════════ 2. ★★ Bianchi II 가 Kasner 사상을 준다
@pytest.mark.parametrize("u_in", [1.3, 2.4, 4.6])
def test_bianchi_II_transition_inverts_the_bkl_map(u_in):
    """★★ **D1 의 핵심** — bkl(u_out) 이 u_in 을 1e−13 로 되돌린다.

    τ 를 키우며 적분하므로 (특이점에서 **멀어지는** 방향) 측정되는 것은 BKL 사상의
    역이다.  인용식을 쓰는 곳은 `bkl_map` 한 줄뿐이고, 나머지는 전부 적분이다.
    """
    r = K.bianchi_II_transition(u_in)
    assert r["bounced"], r
    assert abs(r["inverse"] - u_in) < 1e-10, r
    assert r["circle_out"] < 1e-12, r
    assert abs(r["omega_out"]) < 1e-12, r
    assert abs(r["N1_end"]) < 1e-8, r


def test_the_measured_map_is_not_the_identity():
    """★ 대조군의 세기 — u_out 이 u_in 과 확실히 다르다 (사상이 자명하지 않다)."""
    for u in (1.3, 2.4, 4.6):
        r = K.bianchi_II_transition(u)
        assert abs(r["u_out"] - u) > 0.2, (u, r["u_out"])


def test_axis_assignment_selects_the_branch():
    """★★ 두 배정이 BKL 두 가지의 역을 각각 준다 (u_in + 1  또는  1 + 1/u_in)."""
    u = 3.7
    rows = K.branch_table(u)
    outs = sorted({round(r[1], 8) for r in rows})
    assert len(outs) == 2, rows
    assert abs(outs[0] - (1.0 + 1.0 / u)) < 1e-7, outs
    assert abs(outs[1] - (u + 1.0)) < 1e-7, outs
    for _, _, inv, d in rows:
        assert d < 1e-9, rows


def test_transition_stays_on_the_kasner_circle():
    """★ 튐은 Kasner 원 위의 점을 원 위의 점으로 보낸다 (잔차 ≤ 1e−12)."""
    for u in (1.7, 3.1, 7.2):
        assert K.bianchi_II_transition(u)["circle_out"] < 1e-12


# ═══════════════════════════════ 3. ★★ D1 ↔ D2 — 진공면의 구속 증폭
def test_vacuum_surface_amplification_follows_the_D2_law():
    """★★ Ω=0 면이 지수 6−3γ 로 증폭한다 — γ=2 에서만 중립이다.

    D2 가 물리 단위에서 잰 구속 증폭이 여기서는 **적분이 터지느냐**로 나타난다.
    """
    rows = {g: (e, om, blew) for g, e, om, blew in K.vacuum_surface_amplification()}
    assert rows[0.0][2] is True, rows            # γ=0 → 터진다
    assert rows[2.0][2] is False, rows           # γ=2 → 중립
    assert rows[2.0][1] < 1e-12, rows
    assert rows[4.0 / 3.0][1] < rows[0.0][1], rows
    assert abs(rows[2.0][0]) < 1e-12             # 예측 지수 6−3γ = 0


def test_the_naive_kasner_circle_start_is_not_a_vacuum_orbit():
    """★ **반증 기록** — 벽을 켜면 Σ²=1 은 더 이상 Ω=0 이 아니다."""
    from bianchi.charts import class_a as ca
    Sp, Sm = K.sigma_from_exponents(K.u_to_exponents(3.7)[[2, 0, 1]])
    naive = ca.StateA.of(Sp, Sm, 1e-3, 0.0, 0.0)
    fixed = ca.StateA.of(*K._project_to_vacuum(Sp, Sm, 1e-3), 1e-3, 0.0, 0.0)
    assert abs(float(ca.aux(naive, 2.0)["Omega"])) > 1e-8
    assert abs(float(ca.aux(fixed, 2.0)["Omega"])) < 1e-14


# ═══════════════════════════════ 4. ★★ 이벤트 vs 격자 훑기
def test_grid_scan_only_converges_first_order():
    """★★ argmax 로 튐 시각을 고르면 오차가 Δτ 에 **1차**로만 준다.

    이벤트(Newton 근)는 격자와 무관하다 — 그래서 이 도구를 쓴다.
    """
    e = K.event_beats_grid_scan()
    errs = [r[2] for r in e["rows"]]
    for a, b in zip(errs, errs[1:]):
        assert 1.7 < a / b < 2.4, errs        # Δτ 반감 → 오차 반감
    assert errs[-1] > 1e-3, errs              # 가장 촘촘한 격자도 이벤트에 못 미친다


# ═══════════════════════════════ 5. 대조군
def test_no_wall_means_no_bounce():
    """★ Bianchi I (N = 0) 에서는 이벤트가 안 터진다."""
    assert K.bianchi_I_has_no_bounce() is False


def test_a_decaying_wall_never_bounces():
    """★ Σ₊ > 1/2 로 출발하면 N₁ 이 처음부터 죽어 튐이 없다."""
    assert K.non_growing_wall_never_bounces() is False

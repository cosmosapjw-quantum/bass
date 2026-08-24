"""
PR-17 · 확정된 gamma 임계값 카탈로그  (★ v1.1 에서 전면 수정).

원문(arXiv PDF) 대조로 확정. ★ ar5iv HTML 렌더는 관련 논문 두 편을 본문 중간에서
자르므로 임계값 감사에 쓰면 안 된다 (false negative 발생).

  tilted II   : 2/3 < g < 10/7  -> **비틸트** Collins-Stewart CS(II) 가 sink
                10/7 < g < 14/9 -> 중간 tilt H(II)
                g = 14/9        -> 분기 L(II)
                14/9 < g < 2    -> extreme tilt E(II)
                (Hewitt-Bridson-Wainwright, GRG 33, 65)
  tilted VI_0 : 전체 상태공간에서는 **2/3 과 6/5 둘뿐**.
                3/2 는 불변 부분공간 T_2(VI_0) 안의 전이 (Rosquist-Jantzen).
                4/3 은 T_1(VI_0) 의 단조성 경계이지 sink 분기가 아니다.
                ★ 10/9 는 VI_0 이 **아니라** 예외형 VI*_{-1/9} 소속.
  예외형 VI*_{-1/9} : 2/3<g<10/9 비틸트 Collins; g=10/9 Wainwright 해;
                10/9<g<2 Collinson-French.
  tilted IV, VII_h : **Sigma_+ 의존**. 상수 6/5 로 박지 말 것.
                (Hervik-van den Hoogen-Coley, CQG 22, 607)
  tilted VI_h : 2/3 및 **h 의존** gamma~_h  (-1<h<0, h != -1/9 에서 <6/5,
                h < -1 에서 <4/3).  ★ VI_h 의 sink 는 문헌에서 완전분류 안 됨.
  extreme tilt 개시: **유형 의존** (Coley-Hervik-Lim Table 1) —
                II 14/9 · IV Sigma_+ 의존 · V 6/5 · VI_0 6/5 · VI_h gamma~_h ·
                VII_0 4/3 · VII_h Sigma_+ 의존 · VIII 1.
                "gamma > 4/3" 은 보편값이 아니라 대략적 요약이다.

❌ gamma = 6/7 은 tilt 임계값이 **아니다** — 단조함수 Z_1 의 존재조건(증명 도구).
"""
from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------- 고정 임계값
#: tilted II 의 sink 전이점 (첫 구간은 비틸트 CS(II) 임에 주의)
TILTED_II = (2/3, 10/7, 14/9)

#: tilted VI_0 **전체 상태공간**의 분기 (v1.1: 10/9, 4/3 제거)
TILTED_VI0 = (2/3, 6/5)
#: 불변 부분공간에서만 의미가 있는 값 — 전체 상태공간 분기로 쓰지 말 것
TILTED_VI0_SUBSET = {3/2: "T_2(VI_0) 내부 전이 (Rosquist-Jantzen)",
                     4/3: "T_1(VI_0) 단조성 경계, sink 분기 아님"}

#: 예외형 VI*_{-1/9} (10/9 의 진짜 소속지)
EXCEPTIONAL_VI = (2/3, 10/9)

TILTED_VIh_FIXED = (2/3,)
GENERAL_EXTREME_TILT = 4/3        # 유형 의존값의 대략적 요약치일 뿐

#: extreme tilt 개시 임계값 — 유형별 (Coley-Hervik-Lim Table 1)
#: 값이 None 이면 Sigma_+ 또는 h 의존 -> 아래 함수를 쓸 것
EXTREME_TILT_ONSET = {
    "II": 14/9, "IV": None, "V": 6/5, "VI_0": 6/5, "VI_h": None,
    "VII_0": 4/3, "VII_h": None, "VIII": 1.0,
}

#: 문헌이 완결되지 않은 지점 (조용히 값으로 채우지 말 것)
OPEN_QUESTIONS = {
    "VI_h_sinks": "VI_h 의 sink 는 완전분류되지 않음",
    "extreme_tilt_uniqueness": "extreme tilt 가 sink 여도 유일 미래끌개라는 보장 없음",
}

#: 넣으면 안 되는 값 (회귀 방지)
FORBIDDEN = {6/7: "단조함수 Z_1 존재조건이지 tilt 임계값이 아님"}


def all_fixed_values():
    return tuple(sorted(set(TILTED_II + TILTED_VI0 + EXCEPTIONAL_VI
                            + TILTED_VIh_FIXED + (GENERAL_EXTREME_TILT,))))


def extreme_tilt_onset(bianchi_type, Sigma_p=None, h=None):
    """유형별 extreme-tilt 개시 gamma.  상수가 없으면 의존 함수로 넘긴다."""
    v = EXTREME_TILT_ONSET.get(bianchi_type, "unknown")
    if v is not None and v != "unknown":
        return float(v)
    if bianchi_type in ("IV", "VII_h"):
        if Sigma_p is None:
            raise ValueError(f"{bianchi_type} 는 Sigma_+ 의존 — Sigma_p 를 줘야 한다")
        return float(tilted_IV_extreme_boundary(Sigma_p))
    if bianchi_type == "VI_h":
        if h is None:
            raise ValueError("VI_h 는 h 의존 — h 를 줘야 한다")
        return float(tilted_VIh_boundary(h))
    raise KeyError(f"미분류 유형: {bianchi_type}")


# ---------------------------------------------------------------- Sigma_+ 의존 (IV, VII_h)
def tilted_IV_extreme_boundary(Sigma_p):
    """extremely tilted plane wave 안정 하한: 6/(5 + 2 Sigma_+).

    전역 결론의 '6/5' 는 이 식의 Sigma_+ = 0 값일 뿐이다.
    """
    return 6.0 / (5.0 + 2.0 * np.asarray(Sigma_p))


def tilted_IV_nontilted_upper(Sigma_p):
    """비틸트 plane wave 안정 상한: (4 + Sigma_+)/3."""
    return (4.0 + np.asarray(Sigma_p)) / 3.0


def tilted_IV_nontilted_lower(Sigma_p):
    """비틸트 plane wave 안정 하한: (2 - 4 Sigma_+)/3."""
    return (2.0 - 4.0 * np.asarray(Sigma_p)) / 3.0


def tilted_IV_Epm_lower(Sigma_p):
    """extremely tilted E_pm 안정 하한: 3/(2 - Sigma_+)."""
    return 3.0 / (2.0 - np.asarray(Sigma_p))


def loophole(Sigma_p, gamma0):
    """loophole: gamma_0 < gamma < 6/(5+2 Sigma_+). 안정 고정점이 없는 좁은 영역.

    이 안에 **Mussel attractor** (극한주기의 연속체) 가 있다. 닫힌 형태가 없어
    수치로만 접근 가능 -> M7 의 벤치마크.
    """
    return (float(gamma0), float(tilted_IV_extreme_boundary(Sigma_p)))


# ---------------------------------------------------------------- h 의존 (VI_h)
def tilted_VIh_boundary(h):
    """2(3 + sqrt(-h)) / (5 + 3 sqrt(-h)),  h < 0."""
    s = np.sqrt(-np.asarray(h))
    return 2.0 * (3.0 + s) / (5.0 + 3.0 * s)


# ---------------------------------------------------------------- 수치 판정기
def stability_of_CS_II(gamma):
    """비틸트 Collins-Stewart(II) 의 tilt 선형화 최대 고윳값 — **실제 계산** (v1.3).

    ★ v1.0~v1.2 의 이 함수는 계산하는 척하며 (7g-10)/7 을 하드코딩하고 있었다
      (`lam` 을 0 을 곱해 버림). 적대적 감사(2026-07-29)가 적발. 현재 구현은
      jax.jacfwd 로 dv_general 을 CS(II) 고정점에서 선형화한다.

    구속 논증: 유형 II (n = diag(n1,0,0), a = 0) 의 운동량 구속은
        q_a = eps_abc n_bd sigma_c^d  =>  q_1 ≡ 0  (n 이 1행/1열에만 있음)
    이므로 q_a ∝ gamma Omega v_a 에서 **v_1 tilt 는 구속으로 금지**된다.
    물리적 tilt 부분공간은 {v_2, v_3} 이고, 그 이중항 고윳값이 안정성을 정한다.

    해석 결과 (테스트에서 교차검증):  lambda = (3g-4) - Sigma_+ = 3(7g-10)/8,
    부호 전환 g = 10/7  (Hewitt-Bridson-Wainwright 와 일치).
    """
    import jax
    import jax.numpy as jnp
    from bianchi.matter.fluid import TiltedFluid, dv_general, sources

    g = float(gamma)
    Sp = (3.0 * g - 2.0) / 8.0
    Om = 9.0 / 8.0 - 3.0 * g / 16.0
    N1 = float(np.sqrt(max(9.0 * (2.0 - g) * (3.0 * g - 2.0) / 16.0, 0.0)))
    Sigma = jnp.diag(jnp.asarray([-2.0 * Sp, Sp, Sp]))
    N = jnp.diag(jnp.asarray([N1, 0.0, 0.0]))
    A = jnp.zeros(3)
    R = jnp.zeros(3)

    def f(v):
        fl = TiltedFluid.of(g, Om, v)
        src = sources(fl, Sigma, A)
        return dv_general(fl, src, Sigma, N, A, R)

    J = jax.jacfwd(f)(jnp.zeros(3))
    blk = 0.5 * (J[1:, 1:] + J[1:, 1:].T)          # 구속 허용 {v2, v3} 이중항
    return float(jnp.max(jnp.linalg.eigvalsh(blk)))


def cs_II_tilt_eigenvalue_analytic(gamma):
    """해석식 3(7g-10)/8 — stability_of_CS_II 의 교차검증용 (독립 경로).

    유도 (audit/d_tilted_II.py): CS(II) 에서 tilt 선형화는 기하와 1차로 분리되어
        dv_a/dtau = [(3g-4) delta_ab - Sigma_ab] dv_b
    가 되고 Sigma = diag(-2S+, S+, S+), S+=(3g-2)/8 로부터
        v1: 3(5g-6)/4  (교차 6/5),  v2=v3: 3(7g-10)/8  (교차 10/7).
    """
    return 3.0 * (7.0 * float(gamma) - 10.0) / 8.0


def cs_II_v1_unconstrained_eigenvalue(gamma):
    """v1 방향의 **비구속** 고윳값 3(5g-6)/4 (교차 6/5).

    ★ 이 값은 물리적 임계값이 **아니다**: 유형 II 는 기하 운동량 G_{01} = eps_{1bc}
      n_{bd} sigma_c^d = 0 (n=diag(N1,0,0)) 이라, Codazzi 구속 C_1 = q_1 = g Omega v_1
      = 0 이 v1 을 강제로 0 으로 고정한다.  즉 v1 은 구속면에 접하지 않는 방향이며,
      순진하게 6/5 를 tilt 임계값으로 읽으면 틀린다.  물리적 tilt sink 임계값은
      {v2,v3} 이중항의 10/7 이다 (audit/d_tilted_II.py 로 완전성 확인).
    """
    return 3.0 * (5.0 * float(gamma) - 6.0) / 4.0


def catalog():
    return {
        "tilted_II": TILTED_II,
        "tilted_VI0": TILTED_VI0,
        "exceptional_VI_-1/9": EXCEPTIONAL_VI,
        "tilted_VI0_subset_only": TILTED_VI0_SUBSET,
        "tilted_VIh_fixed": TILTED_VIh_FIXED,
        "tilted_VIh_h_dependent": "2(3+sqrt(-h))/(5+3 sqrt(-h))",
        "tilted_IV_VIIh": {
            "L_stable": "(2-4S+)/3 < gamma < (4+S+)/3",
            "L~_-": "6/(5+2 S+) < gamma < 2,  -1/4 < S+ < 0",
            "F~_pm": "max(6/5, (4+S+)/3) < gamma < min(gamma_0, 3/(2-S+))",
            "E~_pm": "-1/2 < S+ < -1/4,  3/(2-S+) < gamma < 2",
        },
        "extreme_tilt_onset_by_type": EXTREME_TILT_ONSET,
        "general": (f"gamma > {GENERAL_EXTREME_TILT} 는 유형 의존값의 요약치일 뿐 — "
                    "유형별로는 extreme_tilt_onset() 을 쓸 것"),
        "open_questions": OPEN_QUESTIONS,
        "forbidden": FORBIDDEN,
    }

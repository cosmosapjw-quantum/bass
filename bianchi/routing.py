"""
F1 · **유형 → 차트 라우팅** — 11개 Bianchi 유형의 명시적 적분 경로.

분류는 `bianchi.algebra` 가 이미 한다 (PR-04: Jacobi 검사, 기저 독립 κ, det L
1차원리 예외판정).  ★ 처음엔 그걸 모르고 `bianchi/types.py` 를 새로 쓰려다
GateGuard 중복조사에서 걸렸다 — 여기서는 algebra 를 **조합**만 한다:

    classify (algebra) ──> chart_for ──> ic_template ──> 적분(Rust) ──> signature_of_state
                                                              └── 왕복 게이트 (시험)

라우팅 표 (class_b.py 의 κ-커버리지 문서와 정합; κ = 1/h):
    I II VI_0 VII_0 VIII IX → class_a   (IX 는 재붕괴용 대안 type_ix_d)
    V IV                    → class_b (κ=0)
    III VI_h VII_h          → class_b (κ=1/h; III 는 κ=−1 별칭, κ=−9 는 축퇴 — 거부)
    VI*_-1/9                → exceptional
    tilt: class B 계열 → class_b_tilted,  class A 계열 → class_a_tilted (F3 납품)

★ 유형 V 의 함정 (리뷰로 정정): N₊=0 만으로는 V 가 보존되지 않는다 —
  N₊′ = (q+2Σ₊)N₊ + 6Δ 라 Δ 가 N₊ 를 재생성한다.  진화의 불변 부분공간은
  {N₊=Δ=0} 이지만 **Codazzi 는 더 강하다**: N₊=0 ⇒ Ñ=0 ⇒ C = −Δ²−Σ₊²Ã 라
  Ã>0 에서 Δ=0 **그리고 Σ₊=0** 까지 강제한다 (`class_b.type_V_state`).
  Σ₊′=(q−2)Σ₊−2Ñ 이므로 그 면 위에서 Σ₊=0 도 곱셈적으로 보존.

★ 템플릿은 구속면 위에서 만든다 (리뷰 MAJOR 1): V 는 `type_V_state`, 나머지
  class B 는 `on_codazzi_surface` 로 Δ=√(St·Ñ−Σ₊²Ã) 를 풀어 |C| ≤ 1e−12 게이트.
  자유 지정 Δ 는 C = O(10⁻⁴⁻⁵) 로 구속면을 이탈했었다 (반증 기록 — 시험 참조).
"""
from __future__ import annotations

import numpy as np

from bianchi import algebra as AL
from bianchi.backend_policy import require_native

#: class_b 가 축퇴하는 κ — `charts.class_b.KAPPA_EXCEPTIONAL` 과 동일 값
KAPPA_EXCEPTIONAL = -9.0

#: ic_template 의 Codazzi 게이트 (구속면 해가 만족해야 할 |C| 상한; 실측 ~1e-17)
CODAZZI_TOL = 1e-12

CLASS_A_NAMES = ("I", "II", "VI_0", "VII_0", "VIII", "IX")
ALL_NAMES = CLASS_A_NAMES + ("V", "IV", "III", "VI_h", "VII_h", "VI*_-1/9")


def chart_for(bt, tilt=False):
    """BianchiType (또는 이름) → dict(chart, params[, alt, kappa_signature]).

    라우팅 불가는 명시 예외.  ★ tilt=True 의 κ 는 Rust 에 **전달되지 않는다**
    (리뷰 MAJOR 2): `ClassBTilted{gamma}` 는 κ 인자를 무시하고 h 는 상태(λ)에
    산다.  κ 는 서명용 메타데이터로만 `kappa_signature` 에 실어 준다.
    """
    name, kappa = (bt, None) if isinstance(bt, str) else (bt.name, bt.kappa)
    if name in CLASS_A_NAMES:
        if tilt:
            # F3 납품: n-대각 게이지 11-상태 (LRS 축퇴는 차트 LIMITATIONS 참조)
            return {"chart": "class_a_tilted", "params": {}}
        out = {"chart": "class_a", "params": {}}
        if name == "IX":
            out["alt"] = "type_ix_d"               # 재붕괴 추적 (D-정규화)
        return out
    if name == "VI*_-1/9":
        if tilt:
            raise NotImplementedError("예외형 tilted 는 범위 밖 (HHW 비틸트)")
        return {"chart": "exceptional", "params": {}}
    if name in ("V", "IV"):
        kappa = 0.0
    elif name == "III":
        kappa = -1.0
    elif kappa is None:
        raise ValueError(f"{name} 는 κ(=1/h) 가 필요하다 — classify 결과를 넘겨라")
    if abs(kappa - KAPPA_EXCEPTIONAL) < 1e-9:
        raise ValueError("κ = −9 에서 class_b 는 축퇴한다 (Codazzi rank 저하) — "
                         "예외가지는 'VI*_-1/9' 로 라우팅하라")
    if tilt:
        return {"chart": "class_b_tilted", "params": {},
                "kappa_signature": float(kappa)}
    return {"chart": "class_b", "params": {"kappa": float(kappa)}}


def ic_template(bt, seed=1e-2, sigma=(0.06, -0.02), gamma=1.3):
    """대표 초기자료 — 라우팅된 차트의 상태벡터 (+라우팅 dict).

    게이트: 모든 차트 Ω>0, class_b 는 |Codazzi| ≤ CODAZZI_TOL (구속면 위 생성).
    class_b_tilted (11-상태) 템플릿은 H'1(다성분 tilt) 몫 — 여기서는 비틸트만.
    """
    r = chart_for(bt)
    name = bt if isinstance(bt, str) else bt.name
    sp, sm = sigma
    if r["chart"] == "class_a":
        n_diag, _ = AL.CANONICAL[name]
        y = np.array([sp, sm, *(np.sign(n_diag) * seed)])
    elif r["chart"] == "exceptional":
        from bianchi.charts import exceptional as EX
        y = np.asarray(EX.on_g_surface(sp, sm, seed, 3.0 * seed, 2.0 * seed
                                       ).as_array(), float)
    else:
        from bianchi.charts import class_b as CB
        kappa = r["params"]["kappa"]
        at = float(seed)                            # Ã = a² > 0
        st = abs(sm) + seed                         # Σ̃ > 0
        if name == "V":
            y = np.asarray(CB.type_V_state(st, at).as_array(), float)
        else:                                       # IV/III/VI_h/VII_h: Ñ ≥ 0 정의역
            npl = float(np.sqrt(max(kappa * at, 0.0) + seed))
            state, d2 = CB.on_codazzi_surface(sp, st, at, npl, kappa)
            if not float(d2) > 0.0:
                raise ValueError(f"{name} 템플릿: Δ² = {float(d2):.3e} ≤ 0 — "
                                 "구속면 해 없음 (σ/seed 조정 필요)")
            y = np.asarray(state.as_array(), float)
    om, con = _aux_of(r["chart"], y, gamma, r["params"].get("kappa", 0.0))
    if not om > 0.0:
        raise ValueError(f"{name} 템플릿이 물리 영역 밖 (Ω = {om:.3f})")
    if r["chart"] == "class_b" and not abs(con) <= CODAZZI_TOL:
        raise ValueError(f"{name} 템플릿이 Codazzi 면 밖 (C = {con:.3e})")
    return y, r


def _aux_of(chart, y, gamma, kappa):
    """Rust chart_aux → (Ω, 구속잔차) — [1] 을 버리지 않는다 (리뷰 MAJOR 1)."""
    rc = require_native("routing.ic_template")
    om, con = rc.chart_aux(chart, np.asarray(y, float), gamma, kappa)
    return float(om), float(con)


def signature_of_state(chart, y, kappa=None, tol=1e-9):
    """차트 상태 → 유형 이름 — 왕복·보존 감시용.

    감시 내용은 차트마다 다르다 (리뷰 MAJOR 4 — 과대포장 정정):
      · class_a/type_ix_d : N 부호 패턴 (완전 상태 의존)
      · class_b κ=0       : (N₊, Δ) 소멸 여부로 V/IV (상태 의존)
      · class_b κ≠0       : 유형명은 κ 가 결정 (파라미터) — 상태에서는
        **정의역 (Ã>0, Ñ≥0)** 을 검증한다.  Ã≈0 이면 class A 경계라
        V/IV/… 로 이름 붙이는 것 자체가 오류 — 예외.
      · class_b_tilted    : 미구현 (11-상태에서 y[2]/y[5] 는 Σ₁₂/N — 리뷰
        MAJOR 3; (N,λ) 유도는 F3/H'1 몫)
    """
    y = np.asarray(y, float)
    if chart in ("class_a", "type_ix_d", "class_a_tilted"):
        nn = {"class_a": y[2:5], "type_ix_d": y[4:7],
              "class_a_tilted": y[5:8]}[chart]
        scale = max(np.abs(nn).max(), 1e-30)
        signs = [0 if abs(v) <= tol * scale else (1 if v > 0 else -1) for v in nn]
        pos, neg = sum(s > 0 for s in signs), sum(s < 0 for s in signs)
        zero = 3 - pos - neg
        if zero == 3:
            return "I"
        if zero == 2:
            return "II"
        if zero == 1:
            return "VI_0" if (pos == 1 and neg == 1) else "VII_0"
        return "IX" if (pos == 3 or neg == 3) else "VIII"
    if chart == "exceptional":
        return "VI*_-1/9"
    if chart == "class_b_tilted":
        raise NotImplementedError(
            "class_b_tilted 서명은 미구현 — 11-상태의 y[2]/y[5] 는 Σ₁₂/N 이라 "
            "class_b 해석은 오독이다.  (N, λ) 기반 유도는 F3/H'1 에서.")
    if chart == "class_b":
        if kappa is None:
            raise ValueError("class_b 서명에는 κ 가 필요하다")
        if abs(kappa - KAPPA_EXCEPTIONAL) < 1e-9:
            raise ValueError("κ = −9 상태는 exceptional 차트여야 한다 (축퇴)")
        st, de, at, npl = y[1], y[2], y[3], y[4]
        scale = max(np.abs(y).max(), 1e-30)
        if not at > tol * scale:                     # ★ 정의역: Ã = a² > 0
            raise ValueError(f"Ã = {at:.3e} ≤ 0 — class A 경계, class_b 서명 불가")
        n_tilde = (npl * npl - kappa * at) / 3.0
        if n_tilde < -tol * scale:                   # ★ 정의역: Ñ ≥ 0
            raise ValueError(f"Ñ = {n_tilde:.3e} < 0 — class_b 정의역 밖")
        if abs(kappa) < tol:
            return "V" if (abs(npl) <= tol * scale and abs(de) <= tol * scale) \
                else "IV"
        if abs(kappa + 1.0) < 1e-9:
            return "III"
        return "VI_h" if kappa < 0 else "VII_h"
    raise ValueError(f"미지의 차트 {chart!r}")


def roundtrip(name, t_end=2.0, npts=21, gamma=1.3, seed=1e-2):
    """★★ 왕복 게이트의 본체: 분류→라우팅→적분(Rust)→서명이 전 구간 보존되는가."""
    rc = require_native("routing.roundtrip")
    n, a = AL.CANONICAL[name]
    bt = AL.classify(n, a)
    y0, r = ic_template(bt, seed=seed, gamma=gamma)
    kappa = r["params"].get("kappa", 0.0)
    ts = np.linspace(0.0, t_end, npts)
    ys, ok = rc.integrate_background(r["chart"], y0, ts, gamma, kappa)
    sigs = [signature_of_state(r["chart"], ys[i], kappa) for i in range(len(ys))]
    return dict(ok=bool(ok), chart=r["chart"], kappa=kappa, classified=bt.name,
                signatures=sigs, y_final=ys[-1])

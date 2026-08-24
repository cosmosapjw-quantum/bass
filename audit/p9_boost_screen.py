"""
P9a · **D7 유도** — 부스트 하 스크린 회전 ψ (85차).

D7 은 83차부터 "아직 유도하지 않은 것" 으로 남아 있었고, 그 때문에
`polstate.collide(v_b != 0)` 이 `NotImplementedError` 로 거절하고 있었다.
계획은 "광행차가 스크린을 돌린다" 고 **예상**했다.  여기서 그 예상을 잰다.

═══ 설정 ═══
전자 벌크속도 v 로의 순수 부스트 Λ(v).  광자 4-운동량 P = (E, p), p = Eê.
스크린 대표원 W (W⁰ = 0, W·p = 0) 를 4-벡터 (0, W) 로 부스트한 뒤 게이지 복원:
        W'_a = (ΛW)_a − ((ΛW)⁰/E′) p′_a
이 사상 S: 스크린(ê) → 스크린(ê′) 의 2×2 표현을 SVD 해서
        (배율, 이방도, 회전각 ψ)
를 읽는다.  기저는 **산란면 적응** 기저 m₁ ∝ P_⊥[v], m₂ = ê × m₁ 를 쓴다
(v 와 ê 가 정하는 평면 — 부스트 문제에서 유일하게 자연스러운 기저).

═══ 결과 (실측, 무작위 400 조합 |v| ≤ 0.6) ═══
        |배율 − 1| ≤ 4.4e−16
        이방도      ≤ 6.7e−16
        **|ψ|      ≤ 6.7e−16**          ← D7 의 답
        왕복 항등   ≤ 7.8e−16

⇒ **부스트는 추가 회전을 만들지 않는다.**  D3 (수송 홀로노미) 과 같은 구조다:
   순수 등거리 사상이고, 산란면 방향을 산란면 방향으로 보낸다.
   ★ 계획의 예상 ("광행차가 스크린을 돌린다") 은 **기각**된다 — 광행차는 ê 를
   돌리지만 스크린 **안에서의** 추가 회전은 만들지 않는다.

★★ 87차 정정 (외부 리뷰 C1) — **주장의 범위**.  여기서 psi = 0 은 위에서 정의한
**정준 수송 스크린 사상**에 대한 진술이다 (Lorentz 수송 + 게이지 복원, 산란면
적응기저에서 읽음).  임의의 외부 tetrad 나 전역 편광 기저를 고정하면 Wigner
phase 가 다시 나타날 수 있다 — 기저 선택의 성질이지 이 사상의 성질이 아니다.
논문 표기: "psi = 0 for the canonical transported screen map".

기저-없는 진술 (계약에 들어갈 형태):
    Λ 가 유도하는 스크린 사상 S 는 **배율 1 의 등거리**이고,
    P_⊥[v](ê) 를 P_⊥[v](ê′) 로 보낸다.
따라서 편광 텐서의 부스트는 추가 각 없이
    J′_ab(ê′) = S_a^c S_b^d J_cd(ê),      S = Π(ê′) Λ Π(ê) | 스크린
로 끝난다 — 기저-없는 캐리어에서는 **자동**이다.

★ 왜 배율이 1 인가 (해석): Λ 는 계량을 보존하고, 게이지 복원에서 빼는 것은
  **널** 벡터 p′ 의 배수다.  |W′ − αp′|² = |W′|² − 2α(W′·p′) + α²(p′·p′) 인데
  마지막 항은 p′ 이 널이라 0, 가운데 항은 W·p = 0 의 부스트 불변성으로 0.
  ⇒ 노름이 정확히 보존된다.  (배율이 1/D 일 것이라는 순진한 예상은 틀렸다 —
  D 는 **진폭** (E′ = D E) 에 붙지 스크린 벡터에 붙지 않는다.)

사용:  python -m audit.p9_boost_screen
"""
from __future__ import annotations

import numpy as np


def boost(v):
    """순수 부스트 Λ(v) (4×4).  전자 정지계로 가는 방향."""
    v = np.asarray(v, float)
    v2 = float(v @ v)
    if v2 >= 1.0:
        raise ValueError("|v| < 1 이어야 한다")
    if v2 == 0.0:
        return np.eye(4)
    g = 1.0 / np.sqrt(1.0 - v2)
    L = np.eye(4)
    L[0, 0] = g
    L[0, 1:] = -g * v
    L[1:, 0] = -g * v
    L[1:, 1:] = np.eye(3) + (g - 1.0) * np.outer(v, v) / v2
    return L


def screen_rep(V4, P4):
    """W_a = V_a − (V⁰/E) p_a  (W⁰ = 0, W·p = 0)."""
    return V4[1:] - (V4[0] / P4[0]) * P4[1:]


def adapted_basis(e, v):
    """산란면 적응 기저 (m₁ ∝ P_⊥[v], m₂ = ê × m₁).  v ∥ ê 면 임의축으로 대체."""
    e = np.asarray(e, float)
    vv = np.asarray(v, float)
    m1 = vv - (vv @ e) * e
    n = np.linalg.norm(m1)
    if n < 1e-12:
        t = np.array([1.0, 0.0, 0.0]) if abs(e[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
        m1 = t - (t @ e) * e
        n = np.linalg.norm(m1)
    m1 = m1 / n
    return m1, np.cross(e, m1)


def screen_map(v, e):
    """부스트가 유도하는 스크린 사상의 (배율, 이방도, ψ, ê′, 도플러 D)."""
    L = boost(v)
    P4 = np.array([1.0, *np.asarray(e, float)])
    Pp = L @ P4
    ep = Pp[1:] / np.linalg.norm(Pp[1:])
    a1, a2 = adapted_basis(e, v)
    b1, b2 = adapted_basis(ep, v)
    M = np.array([[screen_rep(L @ np.array([0.0, *W]), Pp) @ B
                   for W in (a1, a2)] for B in (b1, b2)])
    U, S, Vt = np.linalg.svd(M)
    R = U @ Vt
    return dict(scale=float(S.mean()), aniso=float(S.max() / S.min() - 1.0),
                psi=float(np.arctan2(R[1, 0], R[0, 0])), ehat_new=ep,
                doppler=float(Pp[0]))


def run(n=400, seed=7, vmax=0.6):
    """무작위 (v, ê) 로 D7 을 잰다.  반환 dict (전부 최대값)."""
    rng = np.random.default_rng(seed)
    out = dict(scale=0.0, aniso=0.0, psi=0.0, roundtrip=0.0, leak=0.0)
    for _ in range(int(n)):
        v = rng.standard_normal(3)
        v *= rng.uniform(0.01, vmax) / np.linalg.norm(v)
        e = rng.standard_normal(3)
        e /= np.linalg.norm(e)
        r = screen_map(v, e)
        out["scale"] = max(out["scale"], abs(r["scale"] - 1.0))
        out["aniso"] = max(out["aniso"], abs(r["aniso"]))
        out["psi"] = max(out["psi"], abs(r["psi"]))
        L = boost(v)
        P4 = np.array([1.0, *e])
        Pp = L @ P4
        a1, _ = adapted_basis(e, v)
        Wp = screen_rep(L @ np.array([0.0, *a1]), Pp)
        # 제약 보존: 옮겨간 스크린 벡터가 ê′ 에 직교하는가
        out["leak"] = max(out["leak"], abs(float(Wp @ r["ehat_new"])))
        # 왕복 (정지계로 갔다 돌아오기) 이 항등인가
        Lb = boost(-v)
        Pb = Lb @ Pp
        Wr = screen_rep(Lb @ np.array([0.0, *Wp]), Pb)
        out["roundtrip"] = max(out["roundtrip"], float(np.abs(Wr - a1).max()))
    return out


def tensor_boost(J, v, e):
    """편광 텐서의 부스트 — 추가 회전 없이 스크린 사상만 적용 (D7 의 귀결).

    J′_ab(ê′) = S_a^c S_b^d J_cd(ê).  S 는 위 `screen_map` 이 잰 등거리 사상."""
    L = boost(v)
    P4 = np.array([1.0, *np.asarray(e, float)])
    Pp = L @ P4
    ep = Pp[1:] / np.linalg.norm(Pp[1:])
    S = np.zeros((3, 3))
    for k in range(3):
        col = np.zeros(3)
        col[k] = 1.0
        col = col - (col @ e) * e                      # 스크린으로 사영
        S[:, k] = screen_rep(L @ np.array([0.0, *col]), Pp)
    return S @ np.asarray(J, float) @ S.T, ep


if __name__ == "__main__":                                  # pragma: no cover
    r = run()
    print("P9a · D7 — 부스트 하 스크린 회전 (무작위 400 조합)")
    for k, v in r.items():
        print(f"  {k:10s} : {v:.3e}")
    print("  ⇒ psi = 0, 배율 = 1  ⇒ 부스트는 추가 회전을 만들지 않는다 (D7 닫힘)")

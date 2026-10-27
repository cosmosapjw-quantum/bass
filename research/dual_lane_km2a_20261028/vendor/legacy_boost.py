"""Archive helper; executable AST compared to current live-read _boost_screen_map."""
import numpy as np
import polarization as PL

def _boost_screen_map(v, e):
    """부스트가 유도하는 스크린 사상 S (M,3,3), 옮겨간 방향 ê′ (M,3), 도플러 𝒟.

    D7 (P9a): S 는 배율 1 의 등거리이고 추가 회전이 없다 ⇒ 여기서 만든 S 를
    두 지표에 적용하는 것으로 편광 부스트가 **끝난다**."""
    v = np.asarray(v, float)
    e = np.atleast_2d(np.asarray(e, float))
    v2 = float(v @ v)
    if v2 >= 1.0:
        raise ValueError("|v_b| < 1 이어야 한다")
    if v2 == 0.0:
        S = np.broadcast_to(np.eye(3), (len(e), 3, 3)).copy()
        return S, e.copy(), np.ones(len(e))
    g = 1.0 / np.sqrt(1.0 - v2)
    ve = e @ v
    D = g * (1.0 - ve)                                   # 도플러 𝒟 (E′ = 𝒟E)
    # 광행차: p′ = p + (g−1)(v·p)v/v² − g E v,  E = 1
    pp = e + ((g - 1.0) * ve / v2)[:, None] * v[None, :] - g * v[None, :]
    ep = pp / np.linalg.norm(pp, axis=1)[:, None]
    # 스크린 사영 → 부스트 → 게이지 복원.  Λ 의 작용:
    #   (ΛW)⁰ = −g(v·W),   (ΛW)^i = W^i + (g−1)(v·W)v^i/v²
    P = PL.screen_proj(e)                                # (M,3,3): 열이 사영된 기저
    Pv = np.einsum("aij,j->ai", P, v)                    # (M,3): v·(열 k)
    W0 = -g * Pv                                         # 시간성분 (열별)
    Wsp = P + ((g - 1.0) / v2) * np.einsum("i,ak->aik", v, Pv)
    S = Wsp - np.einsum("ak,ai->aik", W0 / D[:, None], pp)
    return S, ep, D

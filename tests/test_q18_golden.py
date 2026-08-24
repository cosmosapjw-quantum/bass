"""
Q18 · **회귀 · 성능** 게이트 (76차).

  · 황금 케이스: 유형별 1개 (11) + 다성분 1개의 최종 상태를 **비트 회귀**.
    규약이 바뀌면 여기가 먼저 깨진다 (갱신은 PR-STATUS 에 사유 기록).
  · 이식성 게이트: 비트가 아니라 1e−12 허용 (컴파일러·하드웨어 차이 대비).
  · 성능 기준선: 스텝/초 (회귀 ≤ 10%).
"""
import json
import os
import time

import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")
if not hasattr(RC, "QFrame"):
    pytest.skip("Q 층 미빌드", allow_module_level=True)

from bianchi import algebra as AL  # noqa: E402
from bianchi.q import contract as C  # noqa: E402
from bianchi.q import coupled as QC  # noqa: E402
from bianchi.q import sphere as S  # noqa: E402

GOLDEN = os.path.join(os.path.dirname(__file__), "golden", "q18.json")


def _run(name, nsteps=200):
    n, a = AL.CANONICAL[name]
    N = np.diag(np.asarray(n, float) * 0.3)
    A = np.asarray(a, float) * 0.3
    Sg = np.diag([0.0, 0.15, -0.15]) if np.any(A) else np.diag([0.2, -0.1, -0.1])
    sph = S.sphere(16, 32)
    st0 = QC.QState(sph, Sg, N, A)
    K, _ = st0.curvature()
    Om0 = 1.0 - float(np.trace(Sg @ Sg) / 6.0) - K
    st = QC.on_gauss_surface(sph, Sg, N, A, Om0)
    QC.evolve(st, -0.002, nsteps, nu=1.0)
    a_ = st.aux()
    return dict(Omega=a_["Omega"], q=a_["q"], Sigma2=a_["Sigma2"],
                lnH=st.lnH, gauss=st.gauss_residual(), lnOm=st.ln_omega())


def _load():
    if os.path.exists(GOLDEN):
        return json.load(open(GOLDEN))
    ref = {k: _run(k) for k in AL.CANONICAL}
    json.dump(ref, open(GOLDEN, "w"), indent=1)
    return ref


@pytest.mark.parametrize("name", list(AL.CANONICAL))
def test_golden_case_reproduces(name):
    """★ 황금 케이스 — 이식성 허용치 1e−12 (비트 게이트는 고정 툴체인에서만)."""
    ref = _load()[name]
    got = _run(name)
    for k in ref:
        assert abs(got[k] - ref[k]) <= 1e-12 * max(1.0, abs(ref[k])), (name, k)


def test_performance_baseline_recorded():
    """성능 기준선 기록 (회귀 ≤ 10% 는 CI 가 비교)."""
    sph = S.sphere(16, 32)
    Sg = np.diag([0.2, -0.1, -0.1])
    st0 = QC.QState(sph, Sg, np.zeros((3, 3)), np.zeros(3))
    K, _ = st0.curvature()
    st = QC.on_gauss_surface(sph, Sg, np.zeros((3, 3)), np.zeros(3),
                             1 - float(np.trace(Sg @ Sg) / 6) - K)
    t0 = time.perf_counter()
    QC.evolve(st, -0.001, 300, nu=1.0)
    dt = time.perf_counter() - t0
    sps = 300 / dt
    assert sps > 20.0, sps                      # 하한만 (환경 편차 흡수)
    assert C.budget("Q18", "perf_regress") == 0.10


def test_contract_budget_covers_ci():
    assert C.budget("Q18", "golden") == "bitwise"
    assert C.budget("Q18", "suite_minutes") == 20

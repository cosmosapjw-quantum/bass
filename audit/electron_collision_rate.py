"""Independent numerical audit for the electron relative-flux authority.

The production module supplies the state and public rate.  Expected values are
constructed here from full four-vectors and literal SI/cgs products.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TEST_PATH = ROOT / "tests" / "test_electron_collision_rate.py"
spec = importlib.util.spec_from_file_location("_electron_rate_focused_loader", TEST_PATH)
loader = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = loader
assert spec.loader is not None
spec.loader.exec_module(loader)
EF, ER = loader.EF, loader.ER
ETA = np.diag([-1.0, 1.0, 1.0, 1.0])


def unit(value):
    value = np.asarray(value, float)
    return value / np.linalg.norm(value)


def run(seed=2026082319, count=2000):
    rng = np.random.default_rng(seed)
    maxima = {
        "fluid_covariant": 0.0,
        "normal_covariant": 0.0,
        "observer_chain": 0.0,
        "global_lorentz_scalar": 0.0,
    }
    for _ in range(int(count)):
        def beta():
            return unit(rng.normal(size=3)) * rng.uniform(0.0, 0.92)

        beta_f = beta()
        beta_e = beta()
        direction_f = unit(rng.normal(size=3))
        density = 10.0 ** rng.uniform(-4.0, 14.0)
        state = EF.ElectronTestField.independent(density, beta_e)
        context = ER.ElectronCollisionContext(state)
        base = density * ER.SIGMA_T_M2 * state.c_m_s

        p_f = np.concatenate(([1.0], direction_f))
        p_n = EF.frame_matrix(beta_f, np.zeros(3)) @ p_f
        u_e = EF.normalized_four_velocity(beta_e)
        d_f = -float(u_e @ ETA @ p_n)
        got_f = context.rate_per_fluid_time_s(direction_f, beta_f) / base
        maxima["fluid_covariant"] = max(
            maxima["fluid_covariant"], abs(got_f / d_f - 1.0)
        )

        direction_n = p_n[1:] / p_n[0]
        k_n = np.concatenate(([1.0], direction_n))
        d_n = -float(u_e @ ETA @ k_n)
        got_n = context.rate_per_normal_time_s(direction_n) / base
        maxima["normal_covariant"] = max(
            maxima["normal_covariant"], abs(got_n / d_n - 1.0)
        )
        maxima["observer_chain"] = max(
            maxima["observer_chain"], abs((got_f / p_n[0]) / got_n - 1.0)
        )

        probe = EF.lorentz_boost(beta())
        before = float(u_e @ ETA @ p_n)
        after = float((probe @ u_e) @ ETA @ (probe @ p_n))
        maxima["global_lorentz_scalar"] = max(
            maxima["global_lorentz_scalar"], abs(after - before) / max(abs(before), 1.0)
        )

    canonical_state = EF.ElectronTestField.independent(1.0, [0.6, 0.0, 0.0])
    canonical = ER.ElectronCollisionContext(canonical_state).rate_per_normal_time_s(
        [[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    ) / (ER.SIGMA_T_M2 * canonical_state.c_m_s)

    cgs_rate = 1.0 * ER.SIGMA_T_CM2 * ER.C_CM_S * 2.0
    si_rate = (
        ER.density_cm3_to_m3(1.0)
        * ER.SIGMA_T_M2
        * EF.C_LIGHT_M_S
        * 2.0
    )
    cgs_si_rel = abs(si_rate / cgs_rate - 1.0)

    provenance = ER.ElectronScheduleProvenance("audit:counterstream", "b" * 64)
    midpoint = ER.PrescribedIndependentElectronSchedule(
        [0.0, 1.0], [3.0, 3.0],
        [[0.8, 0.0, 0.0], [-0.8, 0.0, 0.0]],
        provenance=provenance,
    ).at(0.5)
    counterstream_ratio = midpoint.n_e_free / 3.0

    assert max(maxima.values()) < 5.0e-14, maxima
    assert np.max(np.abs(canonical - np.array([0.5, 2.0, 1.25]))) < 3.0e-15
    assert cgs_si_rel < 3.0e-15
    assert abs(counterstream_ratio - 5.0 / 3.0) < 3.0e-15

    return {
        **maxima,
        "canonical_parallel": float(canonical[0]),
        "canonical_head_on": float(canonical[1]),
        "canonical_transverse": float(canonical[2]),
        "cgs_si_relative": float(cgs_si_rel),
        "counterstream_density_ratio": float(counterstream_ratio),
        "cases": int(count),
    }


if __name__ == "__main__":
    report = run()
    for key, value in report.items():
        print(f"{key:31s} {value:.17g}" if isinstance(value, float) else f"{key:31s} {value}")

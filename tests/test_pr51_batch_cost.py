"""PR-51 · 광선추적 비용 모델 테스트."""
import numpy as np
from bianchi import batch


def test_ray_cost_scales_linearly():
    c1 = batch.ray_trace_cost(100, 1000)
    c2 = batch.ray_trace_cost(200, 1000)
    assert abs(c2["wall_s"] - 2 * c1["wall_s"]) < 1e-9
    assert c1["per_ray_ms"] == 1000 * batch.RAY_STEP_MS


def test_optical_costlier_than_geodesic():
    g = batch.ray_trace_cost(1000, 2000)["wall_s"]
    o = batch.optical_map_cost(1000, 2000)["wall_s"]
    assert o > g                                   # 조석 vmap 오버헤드


def test_cmb_map_cost_dir_count():
    c = batch.cmb_map_cost(n_theta=32, n_phi=64, n_steps=1000)
    assert c["n_directions"] == 32 * 64
    assert c["mode"] == "geodesic"
    c_opt = batch.cmb_map_cost(32, 64, 1000, optical=True)
    assert c_opt["wall_s"] > c["wall_s"]


def test_weyl_memory_positive():
    m = batch.weyl_tidal_memory(2000)
    assert m["T_all_MB"] > 0 and m["per_ray_MB"] > m["T_all_MB"]


def test_suite_estimate_total():
    s = batch.observable_suite_estimate(n_theta=32, n_phi=64, n_steps=1000,
                                        n_sn=1700, with_optical=True)
    assert s["total_s"] == sum(s["parts_s"].values())
    assert "dA_map" in s["parts_s"]                # 광학 포함
    assert s["parts_s"]["dA_map"] > s["parts_s"]["cmb_dT"]
    # SN 은 광선추적보다 훨씬 저렴
    assert s["parts_s"]["sn"] < s["parts_s"]["cmb_dT"]


def test_suite_without_optical():
    s = batch.observable_suite_estimate(with_optical=False)
    assert "dA_map" not in s["parts_s"]

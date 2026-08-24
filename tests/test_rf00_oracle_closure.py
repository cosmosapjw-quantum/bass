"""Focused RF-00 proofs that an explicit Python oracle remains transitive."""

import numpy as np

from bianchi import backend as public_backend
from bianchi.backend_policy import BackendPolicy
from bianchi.matter import hierarchy as H
from bianchi.matter import viscous_derived as VD


def test_public_j_moment_python_oracle_is_transitive(monkeypatch):
    seen = []

    def fake_j_moment(*args, backend=None, **kwargs):
        seen.append(backend)
        return 2.0

    monkeypatch.setattr(H, "J_moment", fake_j_moment)
    assert public_backend.j_moment([1.0, 1.0, 1.0], 0.0, 0, 0,
                                   policy=BackendPolicy.PYTHON_ORACLE) == 2.0
    assert seen == ["python"]


def test_public_hierarchy_python_oracle_is_transitive(monkeypatch):
    seen = []

    def fake_integrate(*args, backend=None, **kwargs):
        seen.append(backend)
        return {
            "t": np.array([0.0]),
            "J": [{
                (0, 0): 2.0,
                (0, 1): 3.0,
                (2, 0): np.zeros((3, 3)),
            }],
        }

    monkeypatch.setattr(H, "integrate_hierarchy", fake_integrate)
    result = public_backend.hierarchy_integrate(
        [1.0, 1.0, 1.0], 0.0, 1.0, [0.0, 0.0, 0.0], 0.0,
        policy=BackendPolicy.PYTHON_ORACLE,
    )
    assert seen == ["python"]
    np.testing.assert_array_equal(result["rho"], [2.0])


def test_hierarchy_integrator_forwards_python_oracle_to_all_moments(monkeypatch):
    seen = []

    def fake_j_moment(a_vec, mass, l, i, f0, *, backend=None):
        seen.append(backend)
        return 1.0 if l == 0 else np.zeros((3,) * l)

    def zero_rhs(J, *args, **kwargs):
        return {key: np.zeros_like(np.asarray(value, float))
                for key, value in J.items()}

    monkeypatch.setattr(H, "J_moment", fake_j_moment)
    monkeypatch.setattr(H, "hierarchy_state_rhs", zero_rhs)
    H.integrate_hierarchy(
        [1.0, 1.0, 1.0], 0.0, 1.0, [0.0, 0.0, 0.0], 0.1,
        nsteps=1, l_max=2, i_max=1, backend="python",
    )
    assert seen
    assert set(seen) == {"python"}


def test_public_transport_python_oracle_is_transitive(monkeypatch):
    seen = []

    def fake_transport(*args, backend=None, **kwargs):
        seen.append(backend)
        return {"route": kwargs["route"]}

    monkeypatch.setattr(VD, "transport_coefficients", fake_transport)
    result = public_backend.transport_coefficients(
        0.0, route="hierarchy", policy=BackendPolicy.PYTHON_ORACLE
    )
    assert result == {"route": "hierarchy"}
    assert seen == ["python"]


def test_public_viscous_cross_validate_python_oracle_is_transitive(monkeypatch):
    seen = []

    def fake_cross_validate(*args, backend=None, **kwargs):
        seen.append(backend)
        return {"agree": True}

    monkeypatch.setattr(VD, "cross_validate", fake_cross_validate)
    assert public_backend.viscous_cross_validate(
        0.0, policy=BackendPolicy.PYTHON_ORACLE
    ) == {"agree": True}
    assert seen == ["python"]


def test_viscous_transport_forwards_python_oracle_to_route_b(monkeypatch):
    seen = []

    def fake_j_moment(*args, backend=None, **kwargs):
        seen.append(("moment", backend))
        return 2.0

    def fake_damping(*args, backend=None, **kwargs):
        seen.append(("damping", backend))
        return {"rate_mean": -4.0}

    def fake_source(*args, backend=None, **kwargs):
        seen.append(("source", backend))
        return -8.0 / 15.0

    monkeypatch.setattr(VD.H, "J_moment", fake_j_moment)
    monkeypatch.setattr(VD, "route_b_damping", fake_damping)
    monkeypatch.setattr(VD, "route_b_source", fake_source)
    result = VD.transport_coefficients(0.0, route="hierarchy", backend="python")
    assert seen == [
        ("moment", "python"),
        ("damping", "python"),
        ("source", "python"),
    ]
    assert result["tau_pi"] == 0.25
    assert result["eta"] == 2.0 / 15.0
    assert result["eta_over_rho_H"] == 1.0 / 15.0


def test_viscous_cross_validate_forwards_python_oracle_to_route_b(monkeypatch):
    seen = []

    monkeypatch.setattr(
        VD, "route_a_damping", lambda *args, **kwargs: {"rate_mean": -4.0}
    )
    monkeypatch.setattr(VD, "route_a_source", lambda *args, **kwargs: -8.0 / 15.0)

    def fake_damping(*args, backend=None, **kwargs):
        seen.append(("damping", backend))
        return {"rate_mean": -4.0}

    def fake_source(*args, backend=None, **kwargs):
        seen.append(("source", backend))
        return -8.0 / 15.0

    monkeypatch.setattr(VD, "route_b_damping", fake_damping)
    monkeypatch.setattr(VD, "route_b_source", fake_source)
    result = VD.cross_validate(0.0, backend="python")
    assert seen == [("damping", "python"), ("source", "python")]
    assert result["agree"] is True

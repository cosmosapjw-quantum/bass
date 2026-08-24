"""Focused RF-00 proofs that an explicit Python oracle remains transitive."""

from types import SimpleNamespace

import numpy as np
import pytest

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


def test_tilted_integrator_forwards_oracle_to_initial_state_and_rhs(monkeypatch):
    from bianchi.matter import tilted_integrate as TI

    seen = []

    def fake_initial(*args, backend=None, **kwargs):
        seen.append(("initial", backend))
        return {(0, 0): np.asarray(1.0)}

    def fake_rhs(J, *args, backend=None, **kwargs):
        seen.append(("rhs", backend))
        return {key: np.zeros_like(value) for key, value in J.items()}

    monkeypatch.setattr(TI, "initial_state", fake_initial)
    monkeypatch.setattr(TI, "rhs", fake_rhs)
    monkeypatch.setattr(TI.TMass, "layout", lambda *args: ([(0, 0)], None, 1))
    TI.integrate(object(), 0.0, 0.1, nsteps=1, l_max=0, i_max=0,
                 backend="python")

    assert seen[0] == ("initial", BackendPolicy.PYTHON_ORACLE)
    assert len(seen) == 5
    assert {backend for _, backend in seen} == {BackendPolicy.PYTHON_ORACLE}


def test_tilted_equation_forwards_oracle_to_all_reached_terms(monkeypatch):
    from bianchi.matter import tilted_equation as TE

    seen = []

    def fake_perp(*args, backend=None, **kwargs):
        seen.append(("perp", backend))
        return 0.0

    def fake_div(*args, backend=None, **kwargs):
        seen.append(("div", backend))
        return 0.0

    monkeypatch.setattr(TE.TT, "perp_dot", fake_perp)
    monkeypatch.setattr(TE.TT, "div_contracted", fake_div)
    J = {
        (0, 0): np.asarray(1.0),
        (0, 1): np.asarray(1.0),
        (1, 0): np.zeros(3),
        (2, 0): np.zeros((3, 3)),
    }
    dJ = {key: np.zeros_like(value) for key, value in J.items()}
    geo = {"H": 0.0, "sigma": np.zeros((3, 3)), "omega": np.zeros((3, 3)),
           "udot": np.zeros(3)}
    TE.equation_lhs(
        J, dJ, geo, 0, 0, backend=BackendPolicy.PYTHON_ORACLE
    )
    assert seen == [
        ("perp", BackendPolicy.PYTHON_ORACLE),
        ("div", BackendPolicy.PYTHON_ORACLE),
    ]


def test_tilted_term_oracle_remains_python_in_nested_spatial_call(monkeypatch):
    from bianchi.matter import tilted_terms as TT

    seen = []
    monkeypatch.setattr(
        TT,
        "_selection",
        lambda *args, **kwargs: SimpleNamespace(uses_rust=False),
    )

    def fake_spatial(*args, backend=None, **kwargs):
        seen.append(backend)
        return np.eye(3)

    monkeypatch.setattr(TT, "spatial_derivative", fake_spatial)
    assert TT.div_contracted(
        np.zeros(3), np.zeros(3), {}, backend=BackendPolicy.PYTHON_ORACLE
    ) == 3.0
    assert seen == ["python"]


def test_tilted_trajectory_forwards_oracle_to_integrator_and_exact_reference(
    monkeypatch,
):
    from bianchi.matter import tilted_integrate as TI

    seen = []

    def fake_integrate(*args, backend=None, **kwargs):
        seen.append(("integrate", backend))
        return {"t": [0.1], "J": [{(0, 0): np.asarray(2.0)}]}

    def fake_exact(*args, backend=None, **kwargs):
        seen.append(("exact", backend))
        return 2.0

    bg = SimpleNamespace(
        a=lambda _t: np.ones(3),
        v=lambda _t: np.zeros(3),
    )
    monkeypatch.setattr(TI, "integrate", fake_integrate)
    monkeypatch.setattr(TI.TM, "J_moment_tilted", fake_exact)
    assert TI.trajectory_error(
        bg, 0.0, l_max=0, i_max=0, backend="python"
    ) == {"rho": 0.0}
    assert seen == [
        ("integrate", BackendPolicy.PYTHON_ORACLE),
        ("exact", BackendPolicy.PYTHON_ORACLE),
        ("exact", BackendPolicy.PYTHON_ORACLE),
    ]


def test_type_v_moments_forward_oracle_to_backtrace(monkeypatch):
    from bianchi.matter import freestream as FS
    from bianchi.matter import type_v as TV

    seen = []
    monkeypatch.setattr(FS, "_Q", np.asarray([1.0]))
    monkeypatch.setattr(FS, "_DQ", np.asarray([1.0]))
    monkeypatch.setattr(FS, "_NHAT", np.asarray([[1.0, 0.0, 0.0]]))
    monkeypatch.setattr(FS, "_WANG", np.asarray([1.0]))

    def fake_backtrace(P, *args, backend=None, **kwargs):
        seen.append(backend)
        return P

    monkeypatch.setattr(TV, "back_trace", fake_backtrace)
    result = TV.moments_type_V(
        TV.Background(A=0.0), 0.0, 0.1, l_max=0, i_max=0,
        backend="python",
    )
    assert (0, 0) in result
    assert seen == ["python"]


def test_type_v_exact_reference_keeps_oracle_on_both_sides(monkeypatch):
    from bianchi.matter import type_v as TV

    seen = []

    def fake_type_v(*args, backend=None, **kwargs):
        seen.append(("type_v", backend))
        return {(0, 0): 2.0}

    def fake_exact(*args, backend=None, **kwargs):
        seen.append(("exact", backend))
        return 2.0

    monkeypatch.setattr(TV, "moments_type_V", fake_type_v)
    monkeypatch.setattr(H, "J_moment", fake_exact)
    assert TV.type_I_moment_residual(
        l_max=0, i_max=0, backend="python"
    ) == 0.0
    assert seen == [("type_v", "python"), ("exact", "python"),
                    ("exact", "python")]


def test_type_v_forward_reference_and_push_share_oracle(monkeypatch):
    from bianchi.matter import type_v_coupled as TVC

    seen = []
    monkeypatch.setattr(
        TVC,
        "_selection",
        lambda *args, **kwargs: SimpleNamespace(uses_rust=False),
    )

    def fake_reference(*args, backend=None, **kwargs):
        seen.append(("reference", backend))
        return {(0, 0): 1.0}

    def fake_push(P, W, *args, backend=None, **kwargs):
        seen.append(("push", backend))
        return P, W

    monkeypatch.setattr(TVC.TV, "moments_type_V", fake_reference)
    monkeypatch.setattr(
        TVC, "initial_nodes", lambda *args: (np.zeros((1, 3)), np.ones(1))
    )
    monkeypatch.setattr(TVC, "_push_nodes", fake_push)
    monkeypatch.setattr(
        TVC, "moments_from_nodes", lambda *args: {(0, 0): 1.0}
    )
    assert TVC.forward_vs_backward(
        l_max=0, i_max=0, backend="python"
    ) == 0.0
    assert seen == [
        ("reference", BackendPolicy.PYTHON_ORACLE),
        ("push", BackendPolicy.PYTHON_ORACLE),
    ]


def test_type_v_evolve_explicit_oracle_reaches_selector(monkeypatch):
    from bianchi.matter import type_v_coupled as TVC

    class SelectionReached(Exception):
        pass

    seen = []

    def stop_at_selection(route_id, backend, **domain):
        seen.append((route_id, backend, domain))
        raise SelectionReached

    monkeypatch.setattr(
        TVC, "initial_nodes", lambda *args: (np.zeros((1, 3)), np.ones(1))
    )
    monkeypatch.setattr(
        TVC, "moments_from_nodes", lambda *args: {(0, 0): 1.0}
    )
    monkeypatch.setattr(
        TVC, "initial_expansion", lambda *args: (np.ones(3), None)
    )
    monkeypatch.setattr(TVC, "_selection", stop_at_selection)
    with pytest.raises(SelectionReached):
        TVC.evolve_coupled(
            nsteps=1, check_ansatz=None, backend="python"
        )
    assert seen == [
        ("type_v.evolve_coupled", "python", {"l_max": 2, "i_max": 1})
    ]


def test_cmb_outer_oracle_propagates_to_ray_dispatch(monkeypatch):
    from bianchi.observables import cmb_pattern as CMB

    seen = []

    def fake_ray(_model, nhats, *args, policy=None, **kwargs):
        seen.append(policy)
        return np.zeros(len(nhats))

    monkeypatch.setattr(CMB.backend, "ray_final_z_batch", fake_ray)
    CMB.temperature_pattern_diag_bianchi(
        {}, 1.0, 0.5, n_theta=3, n_phi=4,
        policy=BackendPolicy.PYTHON_ORACLE,
    )
    assert seen == [BackendPolicy.PYTHON_ORACLE]


def test_mixmaster_control_routes_forward_explicit_oracle(monkeypatch):
    from bianchi.analysis import mixmaster as MM

    seen = []

    def fake_bounces(*args, backend=None, **kwargs):
        seen.append(backend)
        return []

    monkeypatch.setattr(MM, "bounce_sequence", fake_bounces)
    assert MM.type_I_never_bounces(backend="python") == 0
    assert seen == ["python"]

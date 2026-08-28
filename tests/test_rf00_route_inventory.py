"""Static RF-00 closure for public wrappers that used to import native code directly."""

from __future__ import annotations

import ast
from pathlib import Path

from bianchi.backend_policy import PUBLIC_ROUTE_INVENTORY, ROUTE_CAPABILITIES


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "bianchi"

DIRECT_NATIVE_ROUTES = {
    "coeff_kernel.lhs_grid": ("coeff_lhs_grid",),
    "coeff_kernel.mass_blocks": ("coeff_mass_blocks",),
    "coeff_kernel.rhs_grid": ("coeff_rhs_grid",),
    "collision_ladder.collide_rust": ("gc_expm_apply",),
    "collision_ladder.strang_evolve_rust": ("gc_strang",),
    "collision_ladder.thomson_matrix_rust": ("gc_thomson",),
    "coupled_tilted.coupled_rhs_rust": ("cp_rhs",),
    "coupled_tilted.rk4_evolve_rust": ("cp_evolve",),
    "q.characteristics.direction_map": ("qc_direction_map",),
    "q.characteristics.rhs_p": ("qc_rhs_p",),
    "q.characteristics.rhs_split": ("qc_rhs_split",),
    "q.collide.collide": ("qx_collide",),
    "q.collide.collide_modeb": ("qx_collide_modeb",),
    "q.collide.kernel_eigenvalues": ("qx_kernel_eigenvalues",),
    "q.comoving.collide_log": ("qm_collide_log",),
    "q.comoving.frame": ("QFrame",),
    "q.comoving.frame_from": ("QFrame",),
    "q.comoving.moments_log": ("qm_moments_log",),
    "q.fast.diagnostics": ("qe_diagnostics",),
    "q.fast.ensemble": ("qe_ensemble",),
    "q.fast.evolve": ("qe_evolve",),
    "q.fast.reduce_det": ("qe_reduce_det",),
    "q.fast.residual_mode_b": ("qe_residual_mode_b",),
    "q.group.classify": ("qg_classify",),
    "q.group.curvature": ("qg_curvature",),
    "q.group.jacobi_residual": ("qg_jacobi",),
    "q.group.kappa": ("qg_kappa",),
    "q.group.ricci3": ("qg_ricci3",),
    "q.group.structure_constants": ("qg_structure_constants",),
    "q.modeb.diagnostics": ("qe_diagnostics",),
    "q.modeb.evolve": ("qe_evolve",),
    "q.polstate.residual_step": ("qt_plan_from_points",),
    "q.residual.residual_step": ("qt_plan_from_points",),
    "q.sphere.sphere": ("QSphere",),
    "q.transport.plan": ("qt_plan_step",),
    "q.transport.radial": ("QRadial",),
    "routing.ic_template": ("chart_aux",),
    "routing.roundtrip": ("integrate_background",),
}


def _production_trees():
    for path in sorted(PACKAGE.rglob("*.py")):
        yield path, ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_production_modules_have_no_direct_native_imports():
    offenders = []
    for path, tree in _production_trees():
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                if any(alias.name == "bianchi_rustcore" for alias in node.names):
                    offenders.append(f"{path.relative_to(ROOT)}:{node.lineno}")
            elif isinstance(node, ast.ImportFrom) and node.module == "bianchi_rustcore":
                offenders.append(f"{path.relative_to(ROOT)}:{node.lineno}")
    assert offenders == []


def test_each_repaired_native_wrapper_uses_a_literal_registered_route():
    observed = set()
    for _, tree in _production_trees():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not node.args:
                continue
            fn = node.func
            is_require = (
                isinstance(fn, ast.Name) and fn.id == "require_native"
            ) or (
                isinstance(fn, ast.Attribute) and fn.attr == "require_native"
            )
            if is_require and isinstance(node.args[0], ast.Constant):
                observed.add(node.args[0].value)
    assert set(DIRECT_NATIVE_ROUTES) <= observed

    for route_id, symbols in DIRECT_NATIVE_ROUTES.items():
        assert ROUTE_CAPABILITIES[route_id].required_symbols == symbols
        record = PUBLIC_ROUTE_INVENTORY[route_id]
        assert record.supported_state.value == "native_required"
        assert record.explicit_oracle_state.value == "unsupported"
        assert record.outside_native_domain_state.value == "unsupported"


def test_historical_use_rust_markers_are_lazy():
    for relative in ("matter/tilted_rust.py", "matter/tilted_terms.py"):
        tree = ast.parse((PACKAGE / relative).read_text(encoding="utf-8"))
        assignments = [
            node for node in tree.body
            if isinstance(node, (ast.Assign, ast.AnnAssign))
            and any(
                isinstance(target, ast.Name) and target.id == "USE_RUST"
                for target in (
                    node.targets if isinstance(node, ast.Assign) else [node.target]
                )
            )
        ]
        assert len(assignments) == 1
        value = assignments[0].value
        assert not (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Name)
            and value.func.id == "available"
        )

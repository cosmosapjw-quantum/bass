"""LINE02 frozen-state exclusive native Ly-alpha owner.

Only the direct Trr[1,1]/sr[1] pair is replaced. Virtual diffusion and frozen
incoming history remain original. This module performs no history or IVP run.
Recovery identity: newly reconstructed code, not byte identity with lost code.
"""
from __future__ import annotations

import ast
from collections import Counter
import csv
from dataclasses import dataclass
import hashlib
import math
from pathlib import Path
import sys
import types
from typing import Any, Iterable

import numpy as np
from scipy.linalg import solve_banded

from escape_moments import angular_moments, validate_inputs

ROOT = Path(__file__).resolve().parents[1]
INPUT_SHA256 = "3a95862b9cd4f924d63020f39fc537b371133af6160e88c3409d8c69fc0c34b7"
SOURCE_SHA256 = "37e00dd8224ddd4d5cec7b2b78c689893996e499b944f38302c5dcc104b61e9f"
ANGULAR_SHA256 = "f8a91ddad8833d4c0079025af81fb8df4b9423da3d87a8363093603922da0c2e"
DONOR_SHA256 = "3d03c35299d529ecaac66f40f5fc78f14ec3099c057005762f112250ee19add9"
LYA_FACT_CM3_INV = 4.662899067555897e15
E21_EV = 10.198714553953742
EV_J = 1.602176634e-19
H_SI = 6.62607015e-34
HBAR_SI = H_SI / (2.0 * math.pi)
C_SI = 299792458.0
K_B_SI = 1.380649e-23
ENERGY_J = E21_EV * EV_J
A_EFFECTIVE_S_INV = (6.2649e8 + 2.0 * 6.2648e8) / 3.0
EPS = np.finfo(float).eps
COUNTERS: Counter[str] = Counter()


def _readonly(value: Any) -> np.ndarray:
    array = np.array(value, dtype=float, copy=True)
    if not np.all(np.isfinite(array)):
        raise ValueError("array contains nonfinite values")
    array.setflags(write=False)
    return array


def _scalar(value: Any, name: str, *, nonnegative: bool = False) -> float:
    if np.ndim(value) != 0 or np.iscomplexobj(value) or isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} must be a finite real scalar")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be finite") from exc
    if not math.isfinite(result) or (nonnegative and result < 0.0):
        raise ValueError(f"{name} is outside its finite real domain")
    return result


def _vector(value: Any, name: str) -> np.ndarray:
    if np.iscomplexobj(value):
        raise ValueError(f"{name} must be real")
    array = np.asarray(value, dtype=float)
    if array.shape != (313,) or not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be a finite 313-vector")
    return array


def checked_denominator(eta: float, summed_scale: float) -> float:
    eta = _scalar(eta, "eta")
    scale = _scalar(summed_scale, "eta summed scale", nonnegative=True)
    if eta <= 64.0 * EPS * scale:
        raise ValueError("rank-one denominator outside the positive margin")
    return eta


def load_original_source() -> tuple[types.ModuleType, dict[str, Any]]:
    """Compile exact dependency-isolated AST nodes; never import native runtime."""
    path = ROOT / "vendor" / "original_hyrec_physical_flux.py"
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("immutable source hash mismatch")
    source = raw.decode("utf-8")
    names = {
        "_readonly_array", "OriginalHyRecTrajectorySnapshot",
        "parse_original_hyrec_snapshot_csv", "dense_original_hyrec_matrix",
        "structured_schur_solution",
    }
    selected, receipts = [], []
    for node in ast.parse(source, filename=str(path)).body:
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            selected.append(node)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
            selected.append(node)
            start = min([node.lineno] + [d.lineno for d in node.decorator_list])
            segment = "\n".join(source.splitlines()[start - 1:node.end_lineno]) + "\n"
            receipts.append({
                "name": node.name, "source_line_start": start,
                "source_line_end": node.end_lineno,
                "source_segment_sha256": hashlib.sha256(segment.encode()).hexdigest(),
            })
    if {row["name"] for row in receipts} != names:
        raise ValueError("missing original AST definition")
    recipe = json_read(ROOT / "provenance" / "AST_REUSE_RECIPE.json")
    expected = {r["name"]: r["source_segment_sha256"] for r in recipe["selected_nodes"]}
    if any(expected[r["name"]] != r["source_segment_sha256"] for r in receipts):
        raise ValueError("original AST segment hash mismatch")
    module = types.ModuleType("line02_original_hyrec_exact_ast")
    module.__file__ = str(path)
    module.__dict__.update({
        "dataclass": dataclass, "math": math, "csv": csv, "Path": Path,
        "Iterable": Iterable, "np": np, "NVIRT": 311,
        "H_PLANCK_EV_S": H_SI / EV_J,
    })
    sys.modules[module.__name__] = module
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), "exec"), module.__dict__)
    return module, {
        "source_module_sha256": SOURCE_SHA256,
        "selection_mode": "EXACT_ORIGINAL_AST_NODES_NOT_REWRITTEN_FUNCTIONS",
        "selected_nodes": receipts,
        "unused_reference": "structured_schur_solution",
        "native_runtime_calls": 0,
    }


def json_read(path: Path) -> Any:
    import json
    return json.loads(path.read_text())


@dataclass(frozen=True)
class OwnerSolution:
    state: np.ndarray
    r_s_inv: float
    b_departure: float
    eta: float
    alpha: float

    @property
    def real(self) -> np.ndarray:
        return self.state[:2]

    @property
    def virtual(self) -> np.ndarray:
        return self.state[2:]


class NativeLineOwner:
    """An exclusive source replacement at one immutable native snapshot."""

    def __init__(self, *, ownership: str = "exclusive_replacement") -> None:
        if ownership != "exclusive_replacement":
            raise ValueError("only exclusive replacement is admitted")
        input_path = ROOT / "inputs" / "ORIGINAL_HYREC_TRAJECTORY_SNAPSHOT.csv"
        if hashlib.sha256(input_path.read_bytes()).hexdigest() != INPUT_SHA256:
            raise ValueError("immutable input hash mismatch")
        for relative, expected in (
            ("code/escape_moments.py", ANGULAR_SHA256),
            ("vendor/hyrec_spike_transfer.py", DONOR_SHA256),
        ):
            if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != expected:
                raise ValueError(f"immutable donor hash mismatch: {relative}")
        self.original, self.reuse = load_original_source()
        self.snapshot = self.original.parse_original_hyrec_snapshot_csv(input_path)
        self.src = self.snapshot
        q = self.snapshot
        self.M = _readonly(self.original.dense_original_hyrec_matrix(q))
        self.s = _readonly(np.concatenate((q.sr, q.sv)))
        self.r0 = LYA_FACT_CM3_INV * q.H_s_inv / (q.nH_cm3 * q.x1s)
        self.b0 = 3.0 * q.x1s * q.Dfplus_Lya
        self.s0 = self.r0 * self.b0
        self.nH_m3 = 1.0e6 * q.nH_cm3
        self.native_tau = A_EFFECTIVE_S_INV / self.r0
        band = np.zeros((3, 311))
        band[0, 1:] = q.Tvv[2, :-1]
        band[1] = q.Tvv[0]
        band[2, :-1] = q.Tvv[1, 1:]
        solved = solve_banded((1, 1), band, np.column_stack((q.Tvr.T, q.sv)))
        COUNTERS["preparation_banded_calls"] += 1
        COUNTERS["preparation_banded_rhs_columns"] += 3
        self.W, self.u = _readonly(solved[:, :2]), _readonly(solved[:, 2])
        self.K = _readonly(q.Trr - q.Trv @ self.W)
        self.j = _readonly(q.sr - q.Trv @ self.u)
        real = np.linalg.solve(self.K, np.column_stack((self.j, [0.0, 1.0])))
        COUNTERS["preparation_real_solve_calls"] += 1
        COUNTERS["preparation_real_rhs_columns"] += 2
        self.x0, self.v = _readonly(real[:, 0]), _readonly(real[:, 1])
        self.X0 = _readonly(np.concatenate((self.x0, self.u - self.W @ self.x0)))
        self.w = _readonly(np.concatenate((self.v, -self.W @ self.v)))
        self.a = float(self.v[1])
        self.gamma0 = self.r0 * self.a
        self.K_condition = float(np.linalg.cond(self.K))

    def parameters(self, r: float, b: float, *, native_owner_active: bool = False) -> tuple[float, float, float]:
        if native_owner_active is not False:
            raise ValueError("native owner must be removed before replacement")
        r = _scalar(r, "r", nonnegative=True)
        b = _scalar(b, "b")
        product = (r - self.r0) * self.a
        eta = checked_denominator(1.0 + product, 1.0 + abs(product))
        if not math.isfinite(r * b):
            raise ValueError("unrepresentable source product")
        return r, b, eta

    def assembled(self, r: float, b: float, *, native_owner_active: bool = False) -> tuple[np.ndarray, np.ndarray]:
        r, b, _ = self.parameters(r, b, native_owner_active=native_owner_active)
        matrix, source = self.M.copy(), self.s.copy()
        matrix[1, 1] += r - self.r0
        source[1] += r * b - self.s0
        COUNTERS["assembled_queries"] += 1
        return matrix, source

    def solution(self, r: float, b: float, *, native_owner_active: bool = False) -> OwnerSolution:
        r, b, eta = self.parameters(r, b, native_owner_active=native_owner_active)
        alpha = math.fsum(((r - self.r0) * (self.b0 - self.x0[1]), r * (b - self.b0))) / eta
        state = _readonly(self.X0 + self.w * alpha)
        COUNTERS["rank_one_solution_queries"] += 1
        return OwnerSolution(state, r, b, eta, alpha)

    def residual(self, state: Any, r: float, b: float, *, native_owner_active: bool = False) -> np.ndarray:
        state = _vector(state, "state")
        r, b, _ = self.parameters(r, b, native_owner_active=native_owner_active)
        result = self.M @ state - self.s
        result[1] += (r - self.r0) * state[1] - (r * b - self.s0)
        COUNTERS["residual_queries"] += 1
        return result

    def residual_jvp(self, state: Any, direction: Any, r: float, b: float,
                     *, dr: float = 0.0, db: float = 0.0) -> np.ndarray:
        state, direction = _vector(state, "state"), _vector(direction, "direction")
        r, b, _ = self.parameters(r, b)
        dr, db = _scalar(dr, "dr"), _scalar(db, "db")
        result = self.M @ direction
        result[1] += (r - self.r0) * direction[1] + (state[1] - b) * dr - r * db
        COUNTERS["residual_jvp_queries"] += 1
        return result

    def solved_drive(self, solution: OwnerSolution) -> float:
        """Stable native departure: do not subtract rounded Xstar_p and b."""
        r, b, eta = self.parameters(solution.r_s_inv, solution.b_departure)
        numerator = math.fsum((self.x0[1] - self.b0, -(1.0 - self.gamma0) * (b - self.b0)))
        return numerator / eta

    def solved_line_rate(self, solution: OwnerSolution) -> float:
        return solution.r_s_inv * self.solved_drive(solution)

    def solution_jvp(self, solution: OwnerSolution, *, dr: float = 0.0, db: float = 0.0) -> np.ndarray:
        r, _, eta = self.parameters(solution.r_s_inv, solution.b_departure)
        dr, db = _scalar(dr, "dr"), _scalar(db, "db")
        result = self.w * (math.fsum((-self.solved_drive(solution) * dr, r * db)) / eta)
        COUNTERS["solution_jvp_queries"] += 1
        return result

    def physical_populations(self, state: Any) -> dict[str, float]:
        state = _vector(state, "state")
        reference = self.src.x1s * math.exp(-E21_EV / self.src.TR_eV_rescaled)
        return {"x1s": self.src.x1s, "x2s": float(state[0] + reference),
                "x2p": float(state[1] + 3.0 * reference)}

    def angular_event(self, tau: float, shear: Any, *, synthetic: bool = False) -> dict[str, Any]:
        data = validate_inputs(tau, shear)
        if not synthetic and data.t != self.native_tau:
            raise ValueError("actual native event must use the pinned native tau")
        moments = angular_moments(data.t, data.tensor, mode="quadrature" if synthetic else "auto")
        C = data.t * moments.mean
        # The analytic thick scalar is exactly one at the admitted approximation order.
        if moments.method == "analytic_thick":
            C = 1.0
        raw_D = data.t * moments.pstf
        D = 0.5 * (raw_D + raw_D.T)
        D = D - np.eye(3) * np.trace(D) / 3.0
        if np.all(data.tensor == 0.0):
            D = np.zeros((3, 3))
        correction = float(np.linalg.norm(D - raw_D, ord="fro"))
        if correction > 64.0 * EPS * abs(C):
            raise ValueError("angular PSTF correction exceeds roundoff budget")
        rbase = A_EFFECTIVE_S_INV / data.t if synthetic else self.r0
        drive = float(self.src.xr[1] - self.b0)
        event_rate = rbase * C * drive
        tensor = ENERGY_J * self.nH_m3 * rbase * drive * D
        COUNTERS["angular_event_queries"] += 1
        return {
            "classification": "SYNTHETIC_OPACITY_CONTROL" if synthetic else "PRESERVED_NATIVE_SCALAR_STATE",
            "tau": data.t, "rbase_s_inv": rbase, "rstar_s_inv": rbase * C,
            "b_departure": self.b0, "driving_departure": drive, "C": C, "D": D,
            "raw_D": raw_D, "PSTF_projection_norm": correction, "shear": data.tensor,
            "method": moments.method, "qmin": moments.qmin, "qmax": moments.qmax,
            "nodes": moments.nodes, "log_delta": -data.t / moments.qmax,
            "delta": represent_log(-data.t / moments.qmax),
            "original_analytic_bounds": moments.analytic_bounds,
            "ledger": event_ledger(event_rate, self.nH_m3, tensor),
            "state_kind": "PRESERVED_SOURCE_XR_NOT_NEW_SOLVED_HISTORY",
        }

    def state_bound(self, rbase: float, b: float, tau: float, shear: Any,
                    *, base_solution: OwnerSolution | None = None) -> dict[str, Any]:
        data = validate_inputs(tau, shear)
        rbase, b, _ = self.parameters(rbase, b)
        base = self.solution(rbase, b) if base_solution is None else base_solution
        if base.r_s_inv != rbase or base.b_departure != b:
            raise ValueError("bound baseline coefficients do not match")
        wbase = self.w / base.eta
        gamma = rbase * float(wbase[1])
        one_minus_gamma = (1.0 - self.gamma0) / base.eta
        log_delta = -data.t / data.qmax
        delta = math.exp(log_delta)
        denominator = 1.0 - gamma * delta
        if gamma < 0.0 or denominator <= 0.0:
            raise ValueError("propagated-bound denominator not positive")
        drive = self.solved_drive(base)
        flux = self.solved_line_rate(base)
        KS = 2.0 * data.tensor / 15.0
        coefficients = {
            "state_inf": float(np.max(np.abs(wbase))) * rbase * abs(drive),
            "flux_per_H_s": abs(flux) * abs(one_minus_gamma),
            "tensor_J_m3_s": ENERGY_J * self.nH_m3 * abs(flux) *
                (math.sqrt(2.0 / 3.0) + gamma * float(np.linalg.norm(KS, ord="fro"))),
        }
        bounds = {}
        for name, coefficient in coefficients.items():
            bounds[name] = ({"log": None, "value": 0.0, "representation": "EXACT_ZERO_COEFFICIENT"}
                            if coefficient == 0.0 else
                            represent_log(math.log(coefficient) + log_delta - math.log(denominator)))
        COUNTERS["state_bound_queries"] += 1
        return {
            "rbase_s_inv": rbase, "b_departure": b, "baseline_state": base.state,
            "baseline_drive": drive, "rounded_state_drive": float(base.state[1] - b),
            "baseline_flux_per_H_s": flux, "wbase": wbase, "gamma": gamma,
            "one_minus_gamma_stable": one_minus_gamma, "denominator": denominator,
            "log_delta": log_delta, "bounds": bounds,
            "claim_scope": "FROZEN_SOURCE_ONLY_NOT_HISTORY_ERROR",
            "floating_evaluation": "NOT_INTERVAL_ARITHMETIC",
        }


def represent_log(logarithm: float) -> dict[str, Any]:
    if logarithm > math.log(sys.float_info.max):
        return {"log": logarithm, "value": None, "representation": "OVERFLOW_USE_LOG"}
    value = math.exp(logarithm)
    return {"log": logarithm, "value": value if value != 0.0 else None,
            "representation": "FLOAT_APPROXIMATION" if value != 0.0 else "UNDERFLOW_USE_LOG"}


def event_ledger(J: float, nH_m3: float, tensor: Any = None) -> dict[str, Any]:
    J, nH_m3 = _scalar(J, "J"), _scalar(nH_m3, "nH_m3")
    if nH_m3 <= 0.0:
        raise ValueError("nH_m3 must be positive")
    tensor = np.zeros((3, 3)) if tensor is None else np.asarray(tensor, dtype=float)
    if tensor.shape != (3, 3) or not np.all(np.isfinite(tensor)):
        raise ValueError("tensor must be finite 3x3")
    R = nH_m3 * J
    energy = ENERGY_J * R
    return {
        "per_H_rate_s_inv": J, "upper_count_m3_s": -R, "lower_count_m3_s": R,
        "photon_count_m3_s": R, "atomic_internal_J_m3_s": -energy,
        "radiation_J_m3_s": energy, "kinetic_heat_J_m3_s": 0.0,
        "electron_yield_m3_s": 0.0, "ionic_yield_m3_s": 0.0,
        "PSTF_injection_J_m3_s": tensor, "odd_momentum_injection": np.zeros(3),
        "scope": "DIRECT_BOUND_BOUND_EVENT_ONLY",
    }


def ledger_invariants(ledger: dict[str, Any]) -> dict[str, Any]:
    R = float(ledger["photon_count_m3_s"])
    E = float(ledger["radiation_J_m3_s"])
    tensor = np.asarray(ledger["PSTF_injection_J_m3_s"])
    residuals = {
        "atomic_number": abs(ledger["upper_count_m3_s"] + ledger["lower_count_m3_s"]),
        "photon_upper": abs(ledger["upper_count_m3_s"] + R),
        "energy": abs(ledger["atomic_internal_J_m3_s"] + E + ledger["kinetic_heat_J_m3_s"]),
        "tensor_trace": abs(float(np.trace(tensor))),
    }
    scales = {"atomic_number": abs(R), "photon_upper": abs(R), "energy": abs(E),
              "tensor_trace": float(np.linalg.norm(tensor, ord="fro"))}
    passed = all(residuals[k] <= 64.0 * EPS * scales[k] for k in residuals)
    return {"passed": passed, "absolute_residuals": residuals, "exchange_scales": scales}


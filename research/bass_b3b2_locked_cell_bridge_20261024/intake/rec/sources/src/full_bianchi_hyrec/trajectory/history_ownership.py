"""Scalar original-HyRec history ownership and accepted-step transactions.

PR-05B3 transfers only the scalar ``Dfplus``/``Dfplus_Ly`` feedback owner.
Sobolev escape, native ``A1s`` diffusion, and completed/Schur ``Tvv`` remain
owned by the canonical October-2012 original-HyRec operator.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import json
import math
import struct
from types import MappingProxyType
from typing import Mapping, Sequence

import numpy as np

from full_bianchi_hyrec.recoil.original_hyrec_native import NVIRT
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    reconstruct_equilibrium_distortion,
    source_escape_factors,
)
from .causal_history import (
    AcceptedRadiationHistory,
    HistoryAppendCandidate,
    HistoryStepLedger,
    OriginalHyRecIncoming,
    construct_original_hyrec_incoming,
    original_hyrec_incoming_jvp,
)
from .causal_history_step import (
    CausalHistoryAcceptedStepProblem,
    CausalHistoryAcceptedStepResult,
    _dynamic_rhs,
    _dynamic_rhs_jvp,
    _relative,
    _source_order_real_virtual_solve,
)
from .primitive_rates import LYMAN_ALPHA_ENERGY_EV
from .primitive_trajectory import AtomicRadiationState
from .time_dependent_native import (
    FrozenCoefficientBackwardEulerResult,
    SourceIdentifiableOriginalHyRecDAE,
)


ACCEPTED_HISTORY_SCHEMA = "PR05B2_ACCEPTED_HISTORY_V1"
_CANONICAL_OWNER = "CANONICAL_ORIGINAL_HYREC"
_E32_EV = 12.087365397278509 - 10.198714553953742
_E42_EV = 12.748393192442178 - 10.198714553953742


class ScalarHistoryFeedbackOwner(str, Enum):
    CANONICAL_CALLBACK = "CANONICAL_CALLBACK"
    TYPED_CHARACTERISTIC_HISTORY = "TYPED_CHARACTERISTIC_HISTORY"


def _normalize_hashes(mapping: Mapping[str, str]) -> Mapping[str, str]:
    normalized: dict[str, str] = {}
    for key, value in mapping.items():
        key_s = str(key)
        value_s = str(value).lower()
        if not key_s or len(value_s) != 64 or any(
            character not in "0123456789abcdef" for character in value_s
        ):
            raise ValueError("source hashes must be nonempty SHA-256 hex values")
        normalized[key_s] = value_s
    if not normalized:
        raise ValueError("at least one required source hash is needed")
    return MappingProxyType(dict(sorted(normalized.items())))


@dataclass(frozen=True)
class ScalarHistoryOwnershipRegistry:
    """Fail-closed owner registry for scalar incoming-history feedback."""

    active_owners: tuple[ScalarHistoryFeedbackOwner, ...]
    required_source_hashes: Mapping[str, str]
    history_schema: str = ACCEPTED_HISTORY_SCHEMA
    sobolev_owner: str = _CANONICAL_OWNER
    a1s_diffusion_owner: str = _CANONICAL_OWNER
    tvv_owner: str = _CANONICAL_OWNER

    def __post_init__(self) -> None:
        owners = tuple(ScalarHistoryFeedbackOwner(owner) for owner in self.active_owners)
        if len(owners) != 1:
            raise ValueError("scalar history feedback requires exactly one active owner")
        object.__setattr__(self, "active_owners", owners)
        object.__setattr__(
            self, "required_source_hashes", _normalize_hashes(self.required_source_hashes)
        )
        schema = str(self.history_schema)
        if not schema:
            raise ValueError("history schema is required")
        object.__setattr__(self, "history_schema", schema)
        for field_name in ("sobolev_owner", "a1s_diffusion_owner", "tvv_owner"):
            value = str(getattr(self, field_name))
            if value != _CANONICAL_OWNER:
                raise ValueError(f"{field_name} must remain under the canonical owner")
            object.__setattr__(self, field_name, value)

    @property
    def active_owner(self) -> ScalarHistoryFeedbackOwner:
        return self.active_owners[0]

    def with_owner(
        self, owner: ScalarHistoryFeedbackOwner
    ) -> "ScalarHistoryOwnershipRegistry":
        return replace(self, active_owners=(ScalarHistoryFeedbackOwner(owner),))

    def validate(
        self,
        history: AcceptedRadiationHistory,
        *,
        candidate: HistoryAppendCandidate | None = None,
    ) -> None:
        if self.history_schema != ACCEPTED_HISTORY_SCHEMA:
            raise ValueError("history schema does not match the accepted PR-05B2 schema")
        observed_hashes = dict(history.grid.source_hashes)
        if observed_hashes != dict(self.required_source_hashes):
            raise ValueError("history source hash registry does not match the owner registry")
        if candidate is None:
            return
        if candidate.parent_sha256 != history.sha256:
            raise ValueError("append candidate parent hash does not match accepted history")
        if candidate.accepted_index != history.accepted_count:
            raise ValueError("append candidate index is not the next accepted index")
        expected_eta = history.grid.eta_start + history.grid.dlna * candidate.accepted_index
        tolerance = 64.0 * np.finfo(float).eps * max(abs(expected_eta), 1.0)
        if not math.isclose(candidate.eta, expected_eta, rel_tol=0.0, abs_tol=tolerance):
            raise ValueError("append candidate eta is not on the accepted history grid")


@dataclass(frozen=True)
class ScalarHistoryParityAudit:
    incoming_virtual_max_abs: float
    incoming_lyman_max_abs: float
    native_rhs_relative: float
    native_solution_relative: float
    electron_rate_relative: float
    outgoing_virtual_relative: float
    outgoing_lyman_relative: float
    average_virtual_relative: float
    append_virtual_max_abs: float
    append_lyman_max_abs: float
    append_average_max_abs: float
    append_candidate_parent_equal: bool
    append_candidate_index_equal: bool
    number_ledger_relative: float
    energy_ledger_relative: float
    atom_source_absolute_W_per_H: float

    @property
    def passed(self) -> bool:
        return (
            self.incoming_virtual_max_abs < 3.0e-25
            and self.incoming_lyman_max_abs < 3.0e-25
            and self.native_rhs_relative < 3.0e-13
            and self.native_solution_relative < 5.0e-12
            and self.electron_rate_relative < 4.0e-13
            and self.outgoing_virtual_relative < 5.0e-12
            and self.outgoing_lyman_relative < 3.0e-12
            and self.average_virtual_relative < 3.0e-12
            and self.append_virtual_max_abs < 3.0e-24
            and self.append_lyman_max_abs < 3.0e-24
            and self.append_average_max_abs < 3.0e-24
            and self.append_candidate_parent_equal
            and self.append_candidate_index_equal
            and self.number_ledger_relative < 3.0e-13
            and self.energy_ledger_relative < 3.0e-13
            and self.atom_source_absolute_W_per_H == 0.0
        )


def _evaluate_from_incoming(
    dae: SourceIdentifiableOriginalHyRecDAE,
    history: AcceptedRadiationHistory,
    incoming: OriginalHyRecIncoming,
) -> CausalHistoryAcceptedStepResult:
    source = dae.source_snapshot
    base = CausalHistoryAcceptedStepProblem(dae=dae, history=history)
    rhs = _dynamic_rhs(dae, incoming)
    solution = _source_order_real_virtual_solve(dae, rhs)
    action = dae.native_matrix_s_inv @ solution
    native_residual = _relative(action, rhs)
    electron_rate = dae.electron_rate_per_lna(source.xe, solution[:2])
    equilibrium = reconstruct_equilibrium_distortion(source, solution)
    one_minus_exp = source_escape_factors(source.Dtau)[2]
    outgoing = incoming.virtual + (equilibrium - incoming.virtual) * one_minus_exp
    outgoing_lyman = np.asarray(
        [
            solution[1] / (3.0 * source.x1s),
            solution[0] / source.x1s * math.exp(-_E32_EV / source.TR_eV_rescaled),
            solution[0] / source.x1s * math.exp(-_E42_EV / source.TR_eV_rescaled),
        ]
    )
    average = solution[2:] / source.x1s
    candidate = HistoryAppendCandidate(
        accepted_index=history.accepted_count,
        eta=history.grid.eta_start + history.grid.dlna * history.accepted_count,
        outgoing_virtual=outgoing,
        outgoing_lyman=outgoing_lyman,
        average_virtual=average,
        parent_sha256=history.sha256,
    )
    ledger = base._conservation_ledger(incoming)
    step_ledger = HistoryStepLedger(
        target_z=source.target_z,
        actual_z=source.z,
        accepted_count_before=history.accepted_count,
        candidate_index=candidate.accepted_index,
        history_before_sha256=history.sha256,
        candidate_parent_sha256=candidate.parent_sha256,
        incoming_virtual_relative=_relative(incoming.virtual, source.Dfplus),
        incoming_lyman_relative=_relative(
            incoming.lyman, np.asarray([source.Dfplus_Lya, source.Dfplus_Lyb])
        ),
        native_residual_relative=native_residual,
        electron_rate_relative=_relative(electron_rate, source.dxHIIdlna),
        outgoing_virtual_relative=_relative(outgoing, source.Dfminus),
        outgoing_lyman_relative=_relative(
            outgoing_lyman,
            np.asarray([source.Dfminus_Lya, source.Dfminus_Lyb, source.Dfminus_Lyg]),
        ),
        average_virtual_relative=_relative(average, source.xv / source.x1s),
        characteristic_number_relative=ledger.number_relative,
        characteristic_energy_relative=ledger.energy_relative,
        interface_atom_source_W_per_H=ledger.interface_atom_source_W_per_H,
    )
    return CausalHistoryAcceptedStepResult(
        incoming=incoming,
        native_rhs_s_inv=rhs,
        native_solution=solution,
        electron_rate_per_lna=electron_rate,
        equilibrium_virtual=equilibrium,
        outgoing_virtual=outgoing,
        outgoing_lyman=outgoing_lyman,
        average_virtual=average,
        append_candidate=candidate,
        native_residual_relative=native_residual,
        electron_rate_relative=_relative(electron_rate, source.dxHIIdlna),
        incoming_virtual_relative=_relative(incoming.virtual, source.Dfplus),
        incoming_lyman_relative=_relative(
            incoming.lyman, np.asarray([source.Dfplus_Lya, source.Dfplus_Lyb])
        ),
        outgoing_virtual_relative=_relative(outgoing, source.Dfminus),
        outgoing_lyman_relative=_relative(
            outgoing_lyman,
            np.asarray([source.Dfminus_Lya, source.Dfminus_Lyb, source.Dfminus_Lyg]),
        ),
        average_virtual_relative=_relative(average, source.xv / source.x1s),
        characteristic_number_relative=ledger.number_relative,
        characteristic_energy_relative=ledger.energy_relative,
        interface_atom_source_W_per_H=ledger.interface_atom_source_W_per_H,
        ledger=step_ledger,
    )


@dataclass(frozen=True)
class ScalarHistoryOwnerSwapProblem:
    """History-owned local DAE and source-parity transition problem."""

    dae: SourceIdentifiableOriginalHyRecDAE
    history: AcceptedRadiationHistory
    registry: ScalarHistoryOwnershipRegistry
    atomic_state: AtomicRadiationState

    def __post_init__(self) -> None:
        self.registry.validate(self.history)
        CausalHistoryAcceptedStepProblem(dae=self.dae, history=self.history)
        self.dae.primitive_problem._validate_state(self.atomic_state)

    def _incoming_for(self, owner: ScalarHistoryFeedbackOwner) -> OriginalHyRecIncoming:
        typed = construct_original_hyrec_incoming(
            self.history, z=self.dae.source_snapshot.z
        )
        selected = ScalarHistoryFeedbackOwner(owner)
        if selected is ScalarHistoryFeedbackOwner.TYPED_CHARACTERISTIC_HISTORY:
            return typed
        source = self.dae.source_snapshot
        return OriginalHyRecIncoming(
            virtual=source.Dfplus,
            lyman=np.asarray([source.Dfplus_Lya, source.Dfplus_Lyb]),
            queries=typed.queries,
            stencils=typed.stencils,
        )

    def evaluate_owner(
        self, owner: ScalarHistoryFeedbackOwner
    ) -> CausalHistoryAcceptedStepResult:
        return _evaluate_from_incoming(
            self.dae, self.history, self._incoming_for(owner)
        )

    def evaluate(self) -> CausalHistoryAcceptedStepResult:
        return self.evaluate_owner(self.registry.active_owner)

    def parity_audit(self) -> ScalarHistoryParityAudit:
        canonical = self.evaluate_owner(ScalarHistoryFeedbackOwner.CANONICAL_CALLBACK)
        typed = self.evaluate_owner(
            ScalarHistoryFeedbackOwner.TYPED_CHARACTERISTIC_HISTORY
        )
        return ScalarHistoryParityAudit(
            incoming_virtual_max_abs=float(
                np.max(np.abs(canonical.incoming.virtual - typed.incoming.virtual))
            ),
            incoming_lyman_max_abs=float(
                np.max(np.abs(canonical.incoming.lyman - typed.incoming.lyman))
            ),
            native_rhs_relative=_relative(
                canonical.native_rhs_s_inv, typed.native_rhs_s_inv
            ),
            native_solution_relative=_relative(
                canonical.native_solution, typed.native_solution
            ),
            electron_rate_relative=_relative(
                canonical.electron_rate_per_lna, typed.electron_rate_per_lna
            ),
            outgoing_virtual_relative=_relative(
                canonical.outgoing_virtual, typed.outgoing_virtual
            ),
            outgoing_lyman_relative=_relative(
                canonical.outgoing_lyman, typed.outgoing_lyman
            ),
            average_virtual_relative=_relative(
                canonical.average_virtual, typed.average_virtual
            ),
            append_virtual_max_abs=float(
                np.max(
                    np.abs(
                        canonical.append_candidate.outgoing_virtual
                        - typed.append_candidate.outgoing_virtual
                    )
                )
            ),
            append_lyman_max_abs=float(
                np.max(
                    np.abs(
                        canonical.append_candidate.outgoing_lyman
                        - typed.append_candidate.outgoing_lyman
                    )
                )
            ),
            append_average_max_abs=float(
                np.max(
                    np.abs(
                        canonical.append_candidate.average_virtual
                        - typed.append_candidate.average_virtual
                    )
                )
            ),
            append_candidate_parent_equal=(
                canonical.append_candidate.parent_sha256
                == typed.append_candidate.parent_sha256
            ),
            append_candidate_index_equal=(
                canonical.append_candidate.accepted_index
                == typed.append_candidate.accepted_index
            ),
            number_ledger_relative=_relative(
                canonical.characteristic_number_relative,
                typed.characteristic_number_relative,
            ),
            energy_ledger_relative=_relative(
                canonical.characteristic_energy_relative,
                typed.characteristic_energy_relative,
            ),
            atom_source_absolute_W_per_H=max(
                abs(canonical.interface_atom_source_W_per_H),
                abs(typed.interface_atom_source_W_per_H),
            ),
        )

    def promote_typed(
        self, audit: ScalarHistoryParityAudit | None = None
    ) -> "ScalarHistoryOwnerSwapProblem":
        result = self.parity_audit() if audit is None else audit
        if not result.passed:
            raise RuntimeError("canonical/typed scalar history parity gate did not pass")
        return replace(
            self,
            registry=self.registry.with_owner(
                ScalarHistoryFeedbackOwner.TYPED_CHARACTERISTIC_HISTORY
            ),
        )

    def residual(
        self,
        state_vector: Sequence[float],
        state_derivative: Sequence[float],
    ) -> np.ndarray:
        state = np.asarray(state_vector, dtype=float)
        derivative = np.asarray(state_derivative, dtype=float)
        if state.shape != (self.dae.layout.local_size,) or derivative.shape != state.shape:
            raise ValueError("state and derivative must have the local DAE size")
        if not np.all(np.isfinite(state)) or not np.all(np.isfinite(derivative)):
            raise ValueError("state and derivative must be finite")
        incoming = self._incoming_for(self.registry.active_owner)
        rhs = _dynamic_rhs(self.dae, incoming)
        result = np.empty_like(state)
        result[0] = derivative[0] - self.dae.electron_rate_per_lna(
            state[0], state[1:3]
        )
        result[1:] = self.dae.native_matrix_s_inv @ state[1:] - rhs
        return result


    def shifted_ijacobian_action(
        self,
        local_direction: Sequence[float],
        *,
        shift: float,
        outgoing_virtual_direction: np.ndarray | None = None,
        outgoing_lyman_direction: np.ndarray | None = None,
        eta_query_directions: Sequence[float] | None = None,
    ) -> np.ndarray:
        direction = np.asarray(local_direction, dtype=float)
        if direction.shape != (self.dae.layout.local_size,) or not np.all(np.isfinite(direction)):
            raise ValueError("local_direction has invalid shape or values")
        action = np.array(
            self.dae.shifted_ijacobian_action(direction, shift=shift), copy=True
        )
        if self.registry.active_owner is ScalarHistoryFeedbackOwner.CANONICAL_CALLBACK:
            return action
        dv = (
            np.zeros_like(self.history.outgoing_virtual)
            if outgoing_virtual_direction is None
            else np.asarray(outgoing_virtual_direction, dtype=float)
        )
        dl = (
            np.zeros_like(self.history.outgoing_lyman)
            if outgoing_lyman_direction is None
            else np.asarray(outgoing_lyman_direction, dtype=float)
        )
        if dv.shape != self.history.outgoing_virtual.shape or dl.shape != self.history.outgoing_lyman.shape:
            raise ValueError("history endpoint directions have invalid shapes")
        incoming = construct_original_hyrec_incoming(
            self.history, z=self.dae.source_snapshot.z
        )
        d_virtual, d_lyman = original_hyrec_incoming_jvp(
            self.history,
            incoming,
            outgoing_virtual_direction=dv,
            outgoing_lyman_direction=dl,
            eta_query_directions=eta_query_directions,
        )
        action[1:] -= _dynamic_rhs_jvp(self.dae, d_virtual, d_lyman)
        return action

    def central_difference_shifted_ijacobian_error(
        self,
        *,
        state_vector: Sequence[float],
        state_derivative: Sequence[float],
        local_direction: Sequence[float],
        outgoing_virtual_direction: np.ndarray,
        outgoing_lyman_direction: np.ndarray,
        shift: float,
        step: float = 1.0e-6,
    ) -> float:
        state = np.asarray(state_vector, dtype=float)
        derivative = np.asarray(state_derivative, dtype=float)
        direction = np.asarray(local_direction, dtype=float)
        dv = np.asarray(outgoing_virtual_direction, dtype=float)
        dl = np.asarray(outgoing_lyman_direction, dtype=float)
        epsilon = float(step)
        if state.shape != (self.dae.layout.local_size,) or derivative.shape != state.shape or direction.shape != state.shape:
            raise ValueError("local finite-difference arrays have invalid shapes")
        if dv.shape != self.history.outgoing_virtual.shape or dl.shape != self.history.outgoing_lyman.shape:
            raise ValueError("history finite-difference arrays have invalid shapes")
        if not math.isfinite(epsilon) or epsilon <= 0.0:
            raise ValueError("step must be positive and finite")
        if self.registry.active_owner is ScalarHistoryFeedbackOwner.TYPED_CHARACTERISTIC_HISTORY:
            plus_history = self.history.perturb(
                outgoing_virtual_direction=dv,
                outgoing_lyman_direction=dl,
                scale=epsilon,
            )
            minus_history = self.history.perturb(
                outgoing_virtual_direction=dv,
                outgoing_lyman_direction=dl,
                scale=-epsilon,
            )
        else:
            plus_history = self.history
            minus_history = self.history
        plus_problem = replace(self, history=plus_history)
        minus_problem = replace(self, history=minus_history)
        plus = plus_problem.residual(
            state + epsilon * direction,
            derivative + epsilon * float(shift) * direction,
        )
        minus = minus_problem.residual(
            state - epsilon * direction,
            derivative - epsilon * float(shift) * direction,
        )
        finite = (plus - minus) / (2.0 * epsilon)
        analytic = self.shifted_ijacobian_action(
            direction,
            shift=shift,
            outgoing_virtual_direction=dv,
            outgoing_lyman_direction=dl,
        )
        return _relative(finite, analytic)

    def frozen_coefficient_backward_euler_step(
        self,
        old_state_vector: Sequence[float],
        *,
        delta_lna: float,
    ) -> FrozenCoefficientBackwardEulerResult:
        old = np.asarray(old_state_vector, dtype=float)
        deta = float(delta_lna)
        if old.shape != (self.dae.layout.local_size,) or not np.all(np.isfinite(old)):
            raise ValueError("old state has invalid shape or values")
        if not math.isfinite(deta) or deta <= 0.0:
            raise ValueError("delta_lna must be positive and finite")
        incoming = self._incoming_for(self.registry.active_owner)
        rhs = _dynamic_rhs(self.dae, incoming)
        native = _source_order_real_virtual_solve(self.dae, rhs)
        d_rate_xe, _ = self.dae._electron_rate_derivatives()
        intercept = self.dae.electron_rate_per_lna(0.0, native[:2])
        denominator = 1.0 / deta - d_rate_xe
        if denominator <= 0.0:
            raise RuntimeError("frozen electron backward-Euler denominator is nonpositive")
        xe_new = (old[0] / deta + intercept) / denominator
        new = np.concatenate((np.asarray([xe_new]), native))
        derivative = np.zeros_like(new)
        derivative[0] = (new[0] - old[0]) / deta
        residual = self.residual(new, derivative)
        electron_scale = max(
            abs(float(derivative[0])),
            abs(self.dae.electron_rate_per_lna(new[0], new[1:3])),
            1.0e-300,
        )
        native_action = self.dae.native_matrix_s_inv @ native
        native_scale = max(
            float(np.max(np.abs(native_action))),
            float(np.max(np.abs(rhs))),
            1.0e-300,
        )
        backward = max(
            abs(float(residual[0])) / electron_scale,
            float(np.max(np.abs(residual[1:]))) / native_scale,
        )
        algebraic = float(np.max(np.abs(residual[1:]))) / native_scale
        source = self.dae.source_snapshot
        equilibrium = np.asarray([1.0, 3.0]) * source.x1s * math.exp(
            -LYMAN_ALPHA_ENERGY_EV / source.TR_eV_rescaled
        )
        physical = native[:2] + equilibrium
        minimum = min(float(xe_new), source.x1s, float(np.min(physical)))
        return FrozenCoefficientBackwardEulerResult(
            state_vector=new,
            converged=bool(backward < 1.0e-11 and minimum > 0.0),
            backward_error=backward,
            algebraic_residual_relative=algebraic,
            minimum_physical_population=minimum,
        )


_TRANSACTION_MAGIC = b"PR05B3_ACCEPTED_STEP_TRANSACTION_V1\n"


class AcceptedStepTransactionStatus(str, Enum):
    """Lifecycle of a proposed accepted-step history update."""

    PENDING = "PENDING"
    COMMITTED = "COMMITTED"
    DISCARDED = "DISCARDED"
    ROLLED_BACK_RESTART_REQUIRED = "ROLLED_BACK_RESTART_REQUIRED"


class AcceptedStepTransaction:
    """Transactional coupling of a local solve, history candidate and restart.

    The accepted history is immutable during a nonlinear attempt.  A successful
    post-step callback may commit the candidate exactly once; rejection leaves
    the parent unchanged; event rollback restores the parent bytes and marks
    the integrator for restart.
    """

    def __init__(
        self,
        *,
        problem: ScalarHistoryOwnerSwapProblem,
        evaluation: CausalHistoryAcceptedStepResult,
        local_state: np.ndarray,
        local_derivative: np.ndarray,
        com_restart_payload: str,
        current_history: AcceptedRadiationHistory | None = None,
        status: AcceptedStepTransactionStatus = AcceptedStepTransactionStatus.PENDING,
        commit_count: int = 0,
        restart_required: bool = False,
    ) -> None:
        if (
            problem.registry.active_owner
            is not ScalarHistoryFeedbackOwner.TYPED_CHARACTERISTIC_HISTORY
        ):
            raise ValueError("accepted-step transaction requires the typed history owner")
        problem.registry.validate(
            problem.history, candidate=evaluation.append_candidate
        )
        state = np.asarray(local_state, dtype=float)
        derivative = np.asarray(local_derivative, dtype=float)
        expected = (problem.dae.layout.local_size,)
        if state.shape != expected or derivative.shape != expected:
            raise ValueError("transaction local arrays must have the local DAE size")
        if not np.all(np.isfinite(state)) or not np.all(np.isfinite(derivative)):
            raise ValueError("transaction local arrays must be finite")
        payload = str(com_restart_payload)
        if not payload:
            raise ValueError("COM restart payload is required")
        status_value = AcceptedStepTransactionStatus(status)
        count = int(commit_count)
        if count not in (0, 1):
            raise ValueError("commit_count must be zero or one")
        if status_value is AcceptedStepTransactionStatus.COMMITTED and count != 1:
            raise ValueError("committed transactions require commit_count one")
        if status_value in (
            AcceptedStepTransactionStatus.PENDING,
            AcceptedStepTransactionStatus.DISCARDED,
        ) and count != 0:
            raise ValueError("pending/discarded transactions require commit_count zero")
        if status_value is AcceptedStepTransactionStatus.ROLLED_BACK_RESTART_REQUIRED:
            if not restart_required:
                raise ValueError("rolled-back transactions require an integrator restart")
        elif restart_required:
            raise ValueError("restart_required is only valid after event rollback")

        self.problem = problem
        self.evaluation = evaluation
        self.parent_history = problem.history
        self.current_history = (
            self.parent_history if current_history is None else current_history
        )
        self.local_state = np.array(state, dtype=float, copy=True, order="C")
        self.local_derivative = np.array(
            derivative, dtype=float, copy=True, order="C"
        )
        self.local_state.setflags(write=False)
        self.local_derivative.setflags(write=False)
        self.com_restart_payload = payload
        self.status = status_value
        self.commit_count = count
        self.restart_required = bool(restart_required)
        self._validate_current_history()

    @classmethod
    def from_problem(
        cls,
        problem: ScalarHistoryOwnerSwapProblem,
        *,
        local_state: Sequence[float],
        local_derivative: Sequence[float],
        com_restart_payload: str,
    ) -> "AcceptedStepTransaction":
        evaluation = problem.evaluate()
        return cls(
            problem=problem,
            evaluation=evaluation,
            local_state=np.asarray(local_state, dtype=float),
            local_derivative=np.asarray(local_derivative, dtype=float),
            com_restart_payload=com_restart_payload,
        )

    def _validate_current_history(self) -> None:
        candidate = self.evaluation.append_candidate
        if self.status is AcceptedStepTransactionStatus.COMMITTED:
            expected = self.parent_history.accept(candidate)
        else:
            expected = self.parent_history
        if self.current_history.to_bytes() != expected.to_bytes():
            raise ValueError("transaction current history is inconsistent with its status")

    def _require_pending(self) -> None:
        if self.status is not AcceptedStepTransactionStatus.PENDING:
            raise RuntimeError("accepted-step transaction is already finalized")

    def commit(self) -> AcceptedRadiationHistory:
        """Commit the append candidate exactly once after a successful step."""

        self._require_pending()
        self.current_history = self.parent_history.accept(
            self.evaluation.append_candidate
        )
        self.status = AcceptedStepTransactionStatus.COMMITTED
        self.commit_count = 1
        self.restart_required = False
        return self.current_history

    def discard(self) -> AcceptedRadiationHistory:
        """Discard a rejected attempt without mutating accepted history."""

        self._require_pending()
        self.current_history = self.parent_history.reject(
            self.evaluation.append_candidate
        )
        self.status = AcceptedStepTransactionStatus.DISCARDED
        self.commit_count = 0
        self.restart_required = False
        return self.current_history

    def rollback_for_event(self) -> AcceptedRadiationHistory:
        """Restore exact parent bytes and require the time integrator to restart."""

        if self.status is AcceptedStepTransactionStatus.ROLLED_BACK_RESTART_REQUIRED:
            raise RuntimeError("accepted-step transaction is already finalized")
        self.current_history = self.parent_history
        self.status = AcceptedStepTransactionStatus.ROLLED_BACK_RESTART_REQUIRED
        self.restart_required = True
        return self.current_history

    def to_bytes(self) -> bytes:
        """Return a deterministic binary restart payload for the transaction."""

        current = self.current_history.to_bytes()
        state = np.asarray(self.local_state, dtype="<f8")
        derivative = np.asarray(self.local_derivative, dtype="<f8")
        com = self.com_restart_payload.encode("utf-8")
        candidate = self.evaluation.append_candidate
        header = {
            "schema": "PR05B3_ACCEPTED_STEP_TRANSACTION_V1",
            "status": self.status.value,
            "commit_count": self.commit_count,
            "restart_required": self.restart_required,
            "owner": self.problem.registry.active_owner.value,
            "parent_history_sha256": self.parent_history.sha256,
            "parent_accepted_count": self.parent_history.accepted_count,
            "candidate_parent_sha256": candidate.parent_sha256,
            "candidate_index": candidate.accepted_index,
            "candidate_eta": candidate.eta,
            "current_history_nbytes": len(current),
            "local_state_shape": list(state.shape),
            "local_state_nbytes": int(state.nbytes),
            "local_derivative_shape": list(derivative.shape),
            "local_derivative_nbytes": int(derivative.nbytes),
            "com_restart_nbytes": len(com),
        }
        encoded = json.dumps(
            header, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
        result = bytearray(_TRANSACTION_MAGIC)
        result.extend(struct.pack(">Q", len(encoded)))
        result.extend(encoded)
        result.extend(current)
        result.extend(state.tobytes(order="C"))
        result.extend(derivative.tobytes(order="C"))
        result.extend(com)
        return bytes(result)

    @classmethod
    def from_bytes(
        cls,
        payload: bytes,
        *,
        problem: ScalarHistoryOwnerSwapProblem,
    ) -> "AcceptedStepTransaction":
        """Restore and validate a deterministic transaction restart payload."""

        if not payload.startswith(_TRANSACTION_MAGIC):
            raise ValueError("unknown accepted-step transaction binary magic")
        offset = len(_TRANSACTION_MAGIC)
        if len(payload) < offset + 8:
            raise ValueError("truncated accepted-step transaction header")
        header_size = struct.unpack(">Q", payload[offset : offset + 8])[0]
        offset += 8
        if len(payload) < offset + header_size:
            raise ValueError("truncated accepted-step transaction header")
        header = json.loads(payload[offset : offset + header_size].decode("utf-8"))
        offset += header_size
        if header.get("schema") != "PR05B3_ACCEPTED_STEP_TRANSACTION_V1":
            raise ValueError("unknown accepted-step transaction schema")
        if header.get("owner") != problem.registry.active_owner.value:
            raise ValueError("transaction owner does not match the supplied problem")
        if header.get("parent_history_sha256") != problem.history.sha256:
            raise ValueError("transaction parent history does not match the supplied problem")
        if int(header.get("parent_accepted_count", -1)) != problem.history.accepted_count:
            raise ValueError("transaction parent count does not match the supplied problem")

        def take(nbytes: int, label: str) -> bytes:
            nonlocal offset
            size = int(nbytes)
            if size < 0 or len(payload) < offset + size:
                raise ValueError(f"truncated {label} block")
            block = payload[offset : offset + size]
            offset += size
            return block

        current = AcceptedRadiationHistory.from_bytes(
            take(header["current_history_nbytes"], "current history")
        )
        state_shape = tuple(int(value) for value in header["local_state_shape"])
        state = np.frombuffer(
            take(header["local_state_nbytes"], "local state"), dtype="<f8"
        ).reshape(state_shape).copy()
        derivative_shape = tuple(
            int(value) for value in header["local_derivative_shape"]
        )
        derivative = np.frombuffer(
            take(header["local_derivative_nbytes"], "local derivative"),
            dtype="<f8",
        ).reshape(derivative_shape).copy()
        com = take(header["com_restart_nbytes"], "COM restart").decode("utf-8")
        if offset != len(payload):
            raise ValueError("trailing bytes in accepted-step transaction payload")

        evaluation = problem.evaluate()
        candidate = evaluation.append_candidate
        if header.get("candidate_parent_sha256") != candidate.parent_sha256:
            raise ValueError("serialized candidate parent does not match source evaluation")
        if int(header.get("candidate_index", -1)) != candidate.accepted_index:
            raise ValueError("serialized candidate index does not match source evaluation")
        eta_tolerance = 64.0 * np.finfo(float).eps * max(abs(candidate.eta), 1.0)
        if not math.isclose(
            float(header.get("candidate_eta")),
            candidate.eta,
            rel_tol=0.0,
            abs_tol=eta_tolerance,
        ):
            raise ValueError("serialized candidate eta does not match source evaluation")

        restored = cls(
            problem=problem,
            evaluation=evaluation,
            local_state=state,
            local_derivative=derivative,
            com_restart_payload=com,
            current_history=current,
            status=AcceptedStepTransactionStatus(header["status"]),
            commit_count=int(header["commit_count"]),
            restart_required=bool(header["restart_required"]),
        )
        if restored.to_bytes() != payload:
            raise ValueError("accepted-step transaction payload is not canonical")
        return restored


__all__ = [
    "ACCEPTED_HISTORY_SCHEMA",
    "AcceptedStepTransaction",
    "AcceptedStepTransactionStatus",
    "ScalarHistoryFeedbackOwner",
    "ScalarHistoryOwnershipRegistry",
    "ScalarHistoryOwnerSwapProblem",
    "ScalarHistoryParityAudit",
]

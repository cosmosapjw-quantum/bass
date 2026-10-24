"""Accepted-step coupling of original-HyRec causal history to the local DAE.

This module implements the source-identifiable PR-05B2 operator.  The 311
virtual radiation variables remain algebraic.  Time dependence enters only
through already accepted outgoing radiation values that are redshifted along
characteristics, exactly as in the October-2012 ``fplus_from_fminus`` routine.

Conventions
-----------
* ``eta = ln(a)`` increases toward the future;
* metric signature is ``(-,+,+,+)``;
* frequencies are ordinary frequencies in Hz;
* the canonical source's eV/cgs quantities are retained only inside its rate
  formulas; public energy diagnostics use explicit ``h`` and ``c``;
* signed distortions are not clipped;
* a pure characteristic/representation crossing has zero atomic source.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np
from scipy.constants import c, h

from full_bianchi_hyrec.recoil.original_hyrec_native import H_PLANCK_EV_S, NVIRT
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    reconstruct_equilibrium_distortion,
    source_escape_factors,
)
from full_bianchi_hyrec.trajectory.causal_history import (
    AcceptedRadiationHistory,
    HistoryAppendCandidate,
    HistoryStepLedger,
    OriginalHyRecIncoming,
    construct_original_hyrec_incoming,
    original_hyrec_incoming_jvp,
)
from full_bianchi_hyrec.trajectory.time_dependent_native import (
    SourceIdentifiableOriginalHyRecDAE,
)


_LYA_FACT_CM3 = 4.662899067555897e15
_LYB_ESCAPE_RATIO = 1.664786871919931
_E32_EV = 12.087365397278509 - 10.198714553953742
_E42_EV = 12.748393192442178 - 10.198714553953742


def _readonly(value: np.ndarray | Sequence[float], shape: tuple[int, ...], name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.shape != shape or not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must have shape {shape} and finite values")
    result = np.array(array, copy=True, dtype=float)
    result.setflags(write=False)
    return result


def _relative(first: np.ndarray | float, second: np.ndarray | float) -> float:
    a = np.asarray(first, dtype=float)
    b = np.asarray(second, dtype=float)
    numerator = float(np.max(np.abs(a - b)))
    denominator = max(float(np.max(np.abs(a))), float(np.max(np.abs(b))), 1.0e-300)
    return numerator / denominator


def _source_lya_rate_s_inv(dae: SourceIdentifiableOriginalHyRecDAE) -> float:
    source = dae.source_snapshot
    return (
        _LYA_FACT_CM3
        * (source.fsR * source.fsR * source.meR) ** 3
        * source.H_s_inv
        / source.nH_cm3
        / source.x1s
    )


def _dynamic_rhs(
    dae: SourceIdentifiableOriginalHyRecDAE,
    incoming: OriginalHyRecIncoming,
) -> np.ndarray:
    """Build the source matrix RHS for arbitrary accepted-history input."""

    source = dae.source_snapshot
    sr = np.array(source.sr, copy=True)
    r_lya = _source_lya_rate_s_inv(dae)
    coefficient_2s_from_lyb = 3.0 * r_lya * source.x1s * _LYB_ESCAPE_RATIO
    coefficient_2p_from_lya = 3.0 * r_lya * source.x1s
    sr[0] += coefficient_2s_from_lyb * (
        incoming.lyman[1] - source.Dfplus_Lyb
    )
    sr[1] += coefficient_2p_from_lya * (
        incoming.lyman[0] - source.Dfplus_Lya
    )
    sv = (
        source.Tvv0_s_inv
        * source.x1s
        * incoming.virtual
        * (1.0 - source.one_minus_Pi)
    )
    result = np.concatenate((sr, sv))
    result.setflags(write=False)
    return result


def _dynamic_rhs_jvp(
    dae: SourceIdentifiableOriginalHyRecDAE,
    incoming_virtual_direction: np.ndarray,
    incoming_lyman_direction: np.ndarray,
) -> np.ndarray:
    source = dae.source_snapshot
    dv = np.asarray(incoming_virtual_direction, dtype=float)
    dl = np.asarray(incoming_lyman_direction, dtype=float)
    if dv.shape != (NVIRT,) or dl.shape != (2,):
        raise ValueError("incoming JVP directions have invalid shapes")
    r_lya = _source_lya_rate_s_inv(dae)
    real = np.asarray(
        [
            3.0 * r_lya * source.x1s * _LYB_ESCAPE_RATIO * dl[1],
            3.0 * r_lya * source.x1s * dl[0],
        ],
        dtype=float,
    )
    virtual = (
        source.Tvv0_s_inv
        * source.x1s
        * (1.0 - source.one_minus_Pi)
        * dv
    )
    return np.concatenate((real, virtual))


def _source_tridiagonal_solve(
    diagonal: np.ndarray,
    upper: np.ndarray,
    lower: np.ndarray,
    rhs: np.ndarray,
) -> np.ndarray:
    """Reproduce ``solveTXeqB`` in canonical C operation order."""

    diag = np.asarray(diagonal, dtype=float)
    up = np.asarray(upper, dtype=float)
    down = np.asarray(lower, dtype=float)
    source = np.asarray(rhs, dtype=float)
    n = diag.size
    if n < 1 or up.shape != (n,) or down.shape != (n,) or source.shape != (n,):
        raise ValueError("invalid tridiagonal source arrays")
    alpha = np.empty(n, dtype=float)
    gamma = np.empty(n, dtype=float)
    alpha[0] = up[0] / diag[0]
    gamma[0] = source[0] / diag[0]
    for index in range(1, n):
        denominator = diag[index] - down[index] * alpha[index - 1]
        alpha[index] = up[index] / denominator
        gamma[index] = (source[index] - down[index] * gamma[index - 1]) / denominator
    solution = np.empty(n, dtype=float)
    solution[-1] = gamma[-1]
    for index in range(n - 2, -1, -1):
        solution[index] = gamma[index] - alpha[index] * solution[index + 1]
    return solution


def _source_order_real_virtual_solve(
    dae: SourceIdentifiableOriginalHyRecDAE, rhs: np.ndarray
) -> np.ndarray:
    """Reproduce canonical ``solve_real_virt`` including accumulation order."""

    source = dae.source_snapshot
    vector = np.asarray(rhs, dtype=float)
    if vector.shape != (2 + NVIRT,):
        raise ValueError("native RHS has invalid shape")
    start = 100  # NSUBLYA - NDIFF/2 = 140 - 40
    stop = 180   # NSUBLYA + NDIFF/2
    inverse_tvr = np.empty((2, NVIRT), dtype=float)
    inverse_rhs = np.empty(NVIRT, dtype=float)
    for real_index in range(2):
        inverse_tvr[real_index, :start] = (
            source.Tvr[real_index, :start] / source.Tvv[0, :start]
        )
        inverse_tvr[real_index, stop:] = (
            source.Tvr[real_index, stop:] / source.Tvv[0, stop:]
        )
        inverse_tvr[real_index, start:stop] = _source_tridiagonal_solve(
            source.Tvv[0, start:stop],
            source.Tvv[2, start:stop],
            source.Tvv[1, start:stop],
            source.Tvr[real_index, start:stop],
        )
    inverse_rhs[:start] = vector[2:][ :start] / source.Tvv[0, :start]
    inverse_rhs[stop:] = vector[2:][stop:] / source.Tvv[0, stop:]
    inverse_rhs[start:stop] = _source_tridiagonal_solve(
        source.Tvv[0, start:stop],
        source.Tvv[2, start:stop],
        source.Tvv[1, start:stop],
        vector[2:][start:stop],
    )
    effective = np.array(source.Trr, copy=True)
    for row in range(2):
        for column in range(2):
            for virtual_index in range(NVIRT):
                effective[row, column] -= (
                    source.Trv[row, virtual_index]
                    * inverse_tvr[column, virtual_index]
                )
    real_rhs = np.array(vector[:2], copy=True)
    for row in range(2):
        for virtual_index in range(NVIRT):
            real_rhs[row] -= source.Trv[row, virtual_index] * inverse_rhs[virtual_index]
    determinant = (
        effective[0, 0] * effective[1, 1]
        - effective[0, 1] * effective[1, 0]
    )
    real = np.asarray(
        [
            (effective[1, 1] * real_rhs[0] - effective[0, 1] * real_rhs[1])
            / determinant,
            (effective[0, 0] * real_rhs[1] - effective[1, 0] * real_rhs[0])
            / determinant,
        ],
        dtype=float,
    )
    virtual = np.empty(NVIRT, dtype=float)
    for index in range(NVIRT):
        virtual[index] = (
            inverse_rhs[index]
            - inverse_tvr[0, index] * real[0]
            - inverse_tvr[1, index] * real[1]
        )
    return np.concatenate((real, virtual))


def _equilibrium_jvp(dae: SourceIdentifiableOriginalHyRecDAE, solution_direction: np.ndarray) -> np.ndarray:
    """Linearized source equilibrium distortion at fixed coefficients."""

    source = dae.source_snapshot
    direction = np.asarray(solution_direction, dtype=float)
    if direction.shape != (2 + NVIRT,):
        raise ValueError("solution_direction has invalid shape")
    real = direction[:2]
    virtual = direction[2:]
    numerator = -real[0] * source.Tvr[0] - real[1] * source.Tvr[1]
    numerator = np.array(numerator, copy=True)
    for index in range(NVIRT):
        if index == 0:
            numerator[index] -= virtual[1] * source.Tvv[2, 0]
        elif index == NVIRT - 1:
            numerator[index] -= virtual[NVIRT - 2] * source.Tvv[1, NVIRT - 1]
        else:
            numerator[index] -= (
                virtual[index + 1] * source.Tvv[2, index]
                + virtual[index - 1] * source.Tvv[1, index]
            )
    denominator = source.x1s * source.one_minus_Pi * source.Tvv0_s_inv
    if np.any(denominator == 0.0):
        raise ValueError("zero equilibrium denominator")
    return numerator / denominator


@dataclass(frozen=True)
class CharacteristicConservationLedger:
    number_relative: float
    energy_relative: float
    interface_atom_source_W_per_H: float
    query_count: int

    def __post_init__(self) -> None:
        for name in ("number_relative", "energy_relative", "interface_atom_source_W_per_H"):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)
        if self.number_relative < 0.0 or self.energy_relative < 0.0:
            raise ValueError("ledger residuals must be nonnegative")
        if self.query_count != 313:
            raise ValueError("source characteristic ledger must contain 313 queries")


@dataclass(frozen=True)
class CausalHistoryStepJVP:
    incoming_virtual: np.ndarray
    incoming_lyman: np.ndarray
    native_solution: np.ndarray
    electron_rate_per_lna: float
    outgoing_virtual: np.ndarray
    outgoing_lyman: np.ndarray
    average_virtual: np.ndarray

    def __post_init__(self) -> None:
        object.__setattr__(self, "incoming_virtual", _readonly(self.incoming_virtual, (NVIRT,), "incoming_virtual"))
        object.__setattr__(self, "incoming_lyman", _readonly(self.incoming_lyman, (2,), "incoming_lyman"))
        object.__setattr__(self, "native_solution", _readonly(self.native_solution, (2 + NVIRT,), "native_solution"))
        object.__setattr__(self, "outgoing_virtual", _readonly(self.outgoing_virtual, (NVIRT,), "outgoing_virtual"))
        object.__setattr__(self, "outgoing_lyman", _readonly(self.outgoing_lyman, (3,), "outgoing_lyman"))
        object.__setattr__(self, "average_virtual", _readonly(self.average_virtual, (NVIRT,), "average_virtual"))
        rate = float(self.electron_rate_per_lna)
        if not math.isfinite(rate):
            raise ValueError("electron-rate JVP must be finite")
        object.__setattr__(self, "electron_rate_per_lna", rate)

    def vector(self) -> np.ndarray:
        return np.concatenate(
            (
                self.incoming_virtual,
                self.incoming_lyman,
                self.native_solution,
                np.asarray([self.electron_rate_per_lna]),
                self.outgoing_virtual,
                self.outgoing_lyman,
                self.average_virtual,
            )
        )


@dataclass(frozen=True)
class CausalHistoryAcceptedStepResult:
    incoming: OriginalHyRecIncoming
    native_rhs_s_inv: np.ndarray
    native_solution: np.ndarray
    electron_rate_per_lna: float
    equilibrium_virtual: np.ndarray
    outgoing_virtual: np.ndarray
    outgoing_lyman: np.ndarray
    average_virtual: np.ndarray
    append_candidate: HistoryAppendCandidate
    native_residual_relative: float
    electron_rate_relative: float
    incoming_virtual_relative: float
    incoming_lyman_relative: float
    outgoing_virtual_relative: float
    outgoing_lyman_relative: float
    average_virtual_relative: float
    characteristic_number_relative: float
    characteristic_energy_relative: float
    interface_atom_source_W_per_H: float
    ledger: HistoryStepLedger

    def __post_init__(self) -> None:
        object.__setattr__(self, "native_rhs_s_inv", _readonly(self.native_rhs_s_inv, (2 + NVIRT,), "native_rhs_s_inv"))
        object.__setattr__(self, "native_solution", _readonly(self.native_solution, (2 + NVIRT,), "native_solution"))
        object.__setattr__(self, "equilibrium_virtual", _readonly(self.equilibrium_virtual, (NVIRT,), "equilibrium_virtual"))
        object.__setattr__(self, "outgoing_virtual", _readonly(self.outgoing_virtual, (NVIRT,), "outgoing_virtual"))
        object.__setattr__(self, "outgoing_lyman", _readonly(self.outgoing_lyman, (3,), "outgoing_lyman"))
        object.__setattr__(self, "average_virtual", _readonly(self.average_virtual, (NVIRT,), "average_virtual"))
        for name in (
            "electron_rate_per_lna",
            "native_residual_relative",
            "electron_rate_relative",
            "incoming_virtual_relative",
            "incoming_lyman_relative",
            "outgoing_virtual_relative",
            "outgoing_lyman_relative",
            "average_virtual_relative",
            "characteristic_number_relative",
            "characteristic_energy_relative",
            "interface_atom_source_W_per_H",
        ):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)

    def response_vector(self) -> np.ndarray:
        return np.concatenate(
            (
                self.incoming.virtual,
                self.incoming.lyman,
                self.native_solution,
                np.asarray([self.electron_rate_per_lna]),
                self.outgoing_virtual,
                self.outgoing_lyman,
                self.average_virtual,
            )
        )


@dataclass(frozen=True)
class CausalHistoryAcceptedStepProblem:
    dae: SourceIdentifiableOriginalHyRecDAE
    history: AcceptedRadiationHistory

    def __post_init__(self) -> None:
        source = self.dae.source_snapshot
        if self.history.accepted_count != source.iz_local:
            raise ValueError(
                "accepted history count must equal the current original-HyRec source index"
            )
        if not np.array_equal(self.history.grid.energy_eV, source.energy_eV):
            raise ValueError("history and source virtual-energy registries differ")
        if not math.isclose(
            self.history.grid.z_start,
            source.zstart,
            rel_tol=0.0,
            abs_tol=64.0 * np.finfo(float).eps * max(source.zstart, 1.0),
        ):
            raise ValueError("history z_start differs from source snapshot")

    def _conservation_ledger(self, incoming: OriginalHyRecIncoming) -> CharacteristicConservationLedger:
        source = self.dae.source_snapshot
        number_errors: list[float] = []
        energy_errors: list[float] = []
        for query in incoming.queries:
            target_zp1 = 1.0 + source.z
            source_zp1 = target_zp1 * query.source_energy_eV / query.target_energy_eV
            nH_source = source.nH_cm3 * (source_zp1 / target_zp1) ** 3
            nu_source = query.source_energy_eV * source.fsR**2 * source.meR / H_PLANCK_EV_S
            nu_target = query.target_energy_eV * source.fsR**2 * source.meR / H_PLANCK_EV_S
            mode_source = 8.0 * math.pi * nu_source**3 / (c**3 * nH_source * 1.0e6)
            mode_target = 8.0 * math.pi * nu_target**3 / (c**3 * source.nH_cm3 * 1.0e6)
            if query.target_kind == "virtual":
                distortion = incoming.virtual[query.target_index]
            else:
                distortion = incoming.lyman[query.target_index]
            number_source = mode_source * distortion
            number_target = mode_target * distortion
            number_errors.append(_relative(number_source, number_target))
            energy_source = h * nu_source * number_source
            energy_target = h * nu_target * number_target
            redshift_work = energy_target - energy_source
            energy_errors.append(
                abs(energy_target - energy_source - redshift_work)
                / max(abs(energy_target), abs(energy_source), 1.0e-300)
            )
        return CharacteristicConservationLedger(
            number_relative=max(number_errors, default=0.0),
            energy_relative=max(energy_errors, default=0.0),
            interface_atom_source_W_per_H=0.0,
            query_count=len(incoming.queries),
        )

    def evaluate(self) -> CausalHistoryAcceptedStepResult:
        source = self.dae.source_snapshot
        incoming = construct_original_hyrec_incoming(self.history, z=source.z)
        rhs = _dynamic_rhs(self.dae, incoming)
        solution = _source_order_real_virtual_solve(self.dae, rhs)
        action = self.dae.native_matrix_s_inv @ solution
        native_residual = _relative(action, rhs)
        electron_rate = self.dae.electron_rate_per_lna(source.xe, solution[:2])
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
            accepted_index=self.history.accepted_count,
            eta=self.history.grid.eta_start
            + self.history.grid.dlna * self.history.accepted_count,
            outgoing_virtual=outgoing,
            outgoing_lyman=outgoing_lyman,
            average_virtual=average,
            parent_sha256=self.history.sha256,
        )
        ledger = self._conservation_ledger(incoming)
        step_ledger = HistoryStepLedger(
            target_z=source.target_z,
            actual_z=source.z,
            accepted_count_before=self.history.accepted_count,
            candidate_index=candidate.accepted_index,
            history_before_sha256=self.history.sha256,
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
                incoming.lyman,
                np.asarray([source.Dfplus_Lya, source.Dfplus_Lyb]),
            ),
            outgoing_virtual_relative=_relative(outgoing, source.Dfminus),
            outgoing_lyman_relative=_relative(
                outgoing_lyman,
                np.asarray(
                    [source.Dfminus_Lya, source.Dfminus_Lyb, source.Dfminus_Lyg]
                ),
            ),
            average_virtual_relative=_relative(average, source.xv / source.x1s),
            characteristic_number_relative=ledger.number_relative,
            characteristic_energy_relative=ledger.energy_relative,
            interface_atom_source_W_per_H=ledger.interface_atom_source_W_per_H,
            ledger=step_ledger,
        )

    def history_jvp(
        self,
        *,
        outgoing_virtual_direction: np.ndarray,
        outgoing_lyman_direction: np.ndarray,
    ) -> CausalHistoryStepJVP:
        source = self.dae.source_snapshot
        incoming = construct_original_hyrec_incoming(self.history, z=source.z)
        d_incoming_virtual, d_incoming_lyman = original_hyrec_incoming_jvp(
            self.history,
            incoming,
            outgoing_virtual_direction=outgoing_virtual_direction,
            outgoing_lyman_direction=outgoing_lyman_direction,
        )
        d_rhs = _dynamic_rhs_jvp(
            self.dae, d_incoming_virtual, d_incoming_lyman
        )
        d_solution = _source_order_real_virtual_solve(self.dae, d_rhs)
        d_electron = float(
            np.dot(self.dae.rates.beta_s_inv / source.H_s_inv, d_solution[:2])
        )
        d_equilibrium = _equilibrium_jvp(self.dae, d_solution)
        one_minus_exp = source_escape_factors(source.Dtau)[2]
        d_outgoing = (
            (1.0 - one_minus_exp) * d_incoming_virtual
            + one_minus_exp * d_equilibrium
        )
        d_lines = np.asarray(
            [
                d_solution[1] / (3.0 * source.x1s),
                d_solution[0] / source.x1s * math.exp(-_E32_EV / source.TR_eV_rescaled),
                d_solution[0] / source.x1s * math.exp(-_E42_EV / source.TR_eV_rescaled),
            ]
        )
        d_average = d_solution[2:] / source.x1s
        return CausalHistoryStepJVP(
            incoming_virtual=d_incoming_virtual,
            incoming_lyman=d_incoming_lyman,
            native_solution=d_solution,
            electron_rate_per_lna=d_electron,
            outgoing_virtual=d_outgoing,
            outgoing_lyman=d_lines,
            average_virtual=d_average,
        )

    def central_difference_history_jvp_error(
        self,
        *,
        outgoing_virtual_direction: np.ndarray,
        outgoing_lyman_direction: np.ndarray,
        step: float = 2.0e-6,
    ) -> float:
        epsilon = float(step)
        if not math.isfinite(epsilon) or epsilon <= 0.0:
            raise ValueError("step must be positive and finite")
        dv = np.asarray(outgoing_virtual_direction, dtype=float)
        dl = np.asarray(outgoing_lyman_direction, dtype=float)
        analytic = self.history_jvp(
            outgoing_virtual_direction=dv,
            outgoing_lyman_direction=dl,
        ).vector()
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
        plus = CausalHistoryAcceptedStepProblem(
            dae=self.dae, history=plus_history
        ).evaluate().response_vector()
        minus = CausalHistoryAcceptedStepProblem(
            dae=self.dae, history=minus_history
        ).evaluate().response_vector()
        finite = (plus - minus) / (2.0 * epsilon)
        return _relative(finite, analytic)


__all__ = [
    "CausalHistoryAcceptedStepProblem",
    "CausalHistoryAcceptedStepResult",
    "CausalHistoryStepJVP",
    "CharacteristicConservationLedger",
]

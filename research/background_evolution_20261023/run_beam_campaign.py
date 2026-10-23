#!/usr/bin/env python3
"""Small new stream campaign; completed historical BASS campaigns are not run."""
from __future__ import annotations
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/bass-background-mpl")
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from core import State, constraints, relative_constraint
from beams import cancellation_model, evaluate, extended_rhs, eliminated_rhs

HERE = Path(__file__).resolve().parent


def scaled_error(a, b):
    return float(np.max(np.abs(a-b)/(1+np.maximum(np.abs(a), np.abs(b)))))


def run(output=None):
    target = Path(output) if output else HERE/"evidence/streams"
    target.mkdir(parents=True, exist_ok=True)
    epochs = np.linspace(0., 3., 193)
    rows, cases, histories = [], {}, {}
    started = time.perf_counter()
    for label, sign in [("cancel_plus", 1.), ("cancel_minus", -1.), ("isotropic", 0.)]:
        models, y0, lam = cancellation_model(sign)
        begin = time.perf_counter()
        sol = solve_ivp(extended_rhs, (0., 3.), y0, args=(models, lam), method="DOP853",
                        t_eval=epochs, rtol=2e-10, atol=2e-12)
        if not sol.success or sol.y.shape != (26, 193):
            raise RuntimeError(f"{label}: {sol.message}; shape={sol.y.shape}")
        reference = solve_ivp(eliminated_rhs, (0., 3.), np.zeros(5), args=(models, lam),
                              method="DOP853", t_eval=epochs, rtol=2e-12, atol=2e-14)
        if not reference.success:
            raise RuntimeError(f"reference {label}: {reference.message}")
        rhos, h_ref, pi_m, pi_r, sigma, defect = [], [], [], [], [], []
        positivity = []
        for j, tau in enumerate(epochs):
            yy = State.unpack(sol.y[:-2, j])
            beta = np.r_[sol.y[-2:, j], -np.sum(sol.y[-2:, j])]
            density, source = evaluate(models, yy.alpha, beta)
            rhos.append(density)
            pr = source.pi+source.pressure[:, None, None]*np.eye(3)
            positivity.append(min(float(np.min(density)), float(np.min(np.linalg.eigvalsh(pr)))))
            pi_m.append(np.diag(source.pi[0]))
            pi_r.append(np.diag(source.pi[1]))
            sigma.append(np.diag(yy.sigma))
            defect.append(relative_constraint(sol.y[:-2, j], lam))
            za = reference.y[:, j]
            beta_ref = np.array([za[1], za[2], -za[1]-za[2]])
            rho_ref, _ = evaluate(models, za[0], beta_ref)
            sigma_ref = np.array([za[3], za[4], -za[3]-za[4]])
            h_ref.append(np.sqrt((np.sum(sigma_ref*sigma_ref)/2+np.sum(rho_ref)+lam)/3))
        rhos, pi_m, pi_r, sigma = map(np.asarray, (rhos, pi_m, pi_r, sigma))
        h_ref, defect = np.asarray(h_ref), np.asarray(defect)
        selected = np.vstack((sol.y[15], sol.y[-2], sol.y[-1], sol.y[1], sol.y[2]))
        reference_error = max(scaled_error(selected, reference.y), scaled_error(sol.y[0], h_ref))
        energy_error = scaled_error(sol.y[16:18].T, rhos)
        init_density, init_source = evaluate(models, 0., np.zeros(3))
        epsilon = 1e-30
        _, source_complex = evaluate(models, 1j*epsilon, np.zeros(3))
        second_derivative = np.imag(np.sum(source_complex.pi, axis=0))/epsilon
        expected_second = -0.9*init_source.pi[0]
        second_error = float(np.max(np.abs(second_derivative-expected_second)))
        case = dict(sign=sign, status="PASS_SCOPED", default_nfev=sol.nfev,
                    reference_nfev=reference.nfev, max_scaled_constraint=float(np.max(defect)),
                    stream_energy_vs_evolved_density=energy_error,
                    independent_eliminated_reference_error=reference_error,
                    minimum_density_or_principal_pressure=min(positivity),
                    initial_total_stress_norm=float(np.linalg.norm(np.sum(init_source.pi, axis=0))),
                    initial_sigma_second_derivative_error=second_error,
                    final_sigma_diagonal=sigma[-1].tolist(),
                    final_pi_m_diagonal=pi_m[-1].tolist(), final_pi_r_diagonal=pi_r[-1].tolist(),
                    elapsed_s=time.perf_counter()-begin)
        if max(case["max_scaled_constraint"], energy_error, reference_error) >= 2e-8 or min(positivity) < 0 or second_error >= 5e-12:
            case["status"] = "FAIL"
        if sign == 0 and float(np.max(np.abs(sigma))) >= 2e-12:
            case["status"] = "FAIL"
        filename = f"{label}.npz"
        np.savez_compressed(target/filename, tau=epochs, state=sol.y, reference=reference.y,
                            reference_h=h_ref, stream_density=rhos, pi_m=pi_m, pi_r=pi_r,
                            sigma=sigma, scaled_constraint=defect)
        case["raw"] = dict(path=filename, sha256=hashlib.sha256((target/filename).read_bytes()).hexdigest())
        cases[label] = case
        histories[label] = (sol.y, sigma, pi_m, pi_r, defect, rhos)
        for j, tau in enumerate(epochs):
            rows.append(dict(case=label, tau=float(tau), alpha=float(sol.y[15, j]), h=float(sol.y[0, j]),
                             sigma_x=float(sigma[j, 0]), sigma_y=float(sigma[j, 1]), sigma_z=float(sigma[j, 2]),
                             pi_m_x=float(pi_m[j, 0]), pi_r_x=float(pi_r[j, 0]),
                             pi_total_x=float(pi_m[j, 0]+pi_r[j, 0]),
                             rho_m=float(sol.y[16, j]), rho_r=float(sol.y[17, j]),
                             beam_rho_m=float(rhos[j, 0]), beam_rho_r=float(rhos[j, 1]),
                             scaled_constraint=float(defect[j])))
    # Same expanding trajectory, tighter tolerance: convergence evidence is new,
    # not a rerun of any archived FD96/chemistry pilot.
    models, y0, lam = cancellation_model(1.)
    tight = solve_ivp(extended_rhs, (0., 3.), y0, args=(models, lam), method="DOP853",
                      t_eval=epochs, rtol=2e-12, atol=2e-14)
    if not tight.success:
        raise RuntimeError(tight.message)
    pair_error = scaled_error(histories["cancel_plus"][0], tight.y)
    np.savez_compressed(target/"cancel_plus_tight.npz", tau=epochs, state=tight.y)
    with (target/"plot_source.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    result = dict(schema="bass.fixed_scale.streams.v1", status="PASS_SCOPED" if pair_error < 2e-8 and all(c["status"] == "PASS_SCOPED" for c in cases.values()) else "FAIL",
                  cases=cases, new_free_evolution_integrations=4, new_eliminated_reference_integrations=3,
                  old_campaign_integrations=0, default_tight_error=pair_error,
                  tau_interval=[0, 3], saved_epochs=193, rows=len(rows),
                  runtime=dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__, platform=platform.platform()),
                  solver={"method":"DOP853", "default_rtol":2e-10, "default_atol":2e-12, "tight_rtol":2e-12, "tight_atol":2e-14},
                  elapsed_s=time.perf_counter()-started,
                  physical_model="positive antipodal-axis collisionless streams; m=3 and m=0; lambda=.3; distinct from FD96", 
                  tensor_convention="fixed-scale STF stress; add tensors before Frobenius norm")
    (target/"RESULTS.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    result = run(sys.argv[1] if len(sys.argv)>1 else None)
    raise SystemExit(0 if result["status"] == "PASS_SCOPED" else 1)

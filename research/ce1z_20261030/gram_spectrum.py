"""CE1-Z: physical rank-three unequal-time K4 Gram spectra from original BASS Rust skies.

Uses immutable PR271 BASS native Rust binary64 sky CSV, not an MPFR evaluation
and not a stochastic covariance/observable likelihood. No IVP rerun.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np

SOURCE_SHA = "022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035"
RUST_BLOB = "a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84"
BASE = Path(__file__).resolve().parents[1] / "ce1y_20261030"
ORDERS = (6, 8)
STEPS = (4, 8, 16)
TIMES = np.linspace(0.0, 0.08, 41)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sky_modes(rows):
    require(len(rows) == 41, "41 original proper-time epochs required")
    u = np.array([float(x["u"]) for x in rows])
    E = np.array([float(x["E"]) for x in rows])
    require(np.isfinite(u).all() and np.max(np.abs(u-TIMES)) < 3e-15, "wrong proper-time grid")
    require(np.isfinite(E).all() and np.min(E) > 0, "invalid positive sky energy")
    a = np.array([[complex(float(r[f"a_4_{m}_re"]), float(r[f"a_4_{m}_im"]))
                   for m in range(-4, 5)] for r in rows])
    require(np.isfinite(a).all(), "nonfinite original Rust l4 coefficients")
    require(np.max(abs(a[:, 1::2])) < 1e-11, "original reflection symmetry changed")
    require(np.max(abs(a.imag)) < 1e-11, "original real reflection-even sky changed")
    for m in range(1, 5):
        require(np.max(abs(a[:, 4-m] - (-1)**m * a[:, 4+m].conj())) < 1e-11,
                "Condon-Shortley reality pair changed")
    # Construct K by *two* independent algebraic representations.
    z = (4*np.pi/E[:, None]) * a
    g = (4*np.pi/E[:, None]) * np.column_stack(
        [a[:, 4].real, np.sqrt(2)*a[:, 6].real, np.sqrt(2)*a[:, 8].real]) / 3
    k9 = z@z.conj().T / 9
    k3 = g@g.T
    require(np.max(abs(k9.imag)) < 1e-12, "nonreal K4 sky")
    require(np.max(abs(k9.real-k3)) < 2e-12, "9-mode vs 3-mode source discrepancy")
    return u, E, g, k3


def analyze_case(sky_csv: Path, kernel_csv: Path, expected_source_sha: str, label: str):
    require(sha256(sky_csv) == expected_source_sha, "original Rust CSV SHA256 changed")
    u, E, g, K = sky_modes(read_rows(sky_csv))
    pairs = read_rows(kernel_csv)
    require(len(pairs) == 1681, "need every one of the 41x41 physical pairs")
    max_gap = 0.0
    radius = None
    for idx, r in enumerate(pairs):
        i, j = divmod(idx, 41)
        require(abs(float(r["u"])-u[i]) < 3e-15 and abs(float(r["v"])-u[j]) < 3e-15,
                "out-of-order real two-time physics")
        gap = abs(float(r["K4_delta_RK4_BASS_Rust"])-K[i, j])
        max_gap = max(max_gap, gap)
        bound = float(r["uniform_total_exact_real_functional_bound_conditional"])
        require(np.isfinite(bound) and bound > 0, "source/geometry bound missing")
        if radius is None:
            radius = bound
        require(abs(bound-radius) < 1e-21, "nonuniform recorded PR270 radius")
    require(max_gap < 2e-12, "original PR271 real K4 pair atlas disagrees with 3-mode Gram")

    # Nonzero eigenvalues of 41x41 K equal those of 3x3 g.T@g.
    eigen = np.linalg.eigvalsh(g.T@g)[::-1]
    require(np.min(eigen) >= -1e-13 and np.all(np.isfinite(eigen)), "Gram PSD failure")
    rank4 = np.linalg.eigvalsh(K)[::-1][3]
    require(abs(rank4) < 2e-12, "unexpected fourth time mode")
    trace = float(eigen.sum())
    purity = float(np.dot(eigen, eigen) / trace**2)
    c0, c1 = float(K[0, 0]), float(K[-1, -1])
    r4 = float(K[0, -1]/np.sqrt(c0*c1))
    d2 = float(c0+c1-2*K[0, -1])
    require(-1-1e-12 < r4 < 1+1e-12 and d2 >= -1e-12, "Gram geometry falsifier")
    # Entrywise exact-real path/continuum kernel bound from PR270:
    # |delta K_ij| <= radius -> ||delta K||_2 <= 41*radius (Weyl).
    # Binary64-center error is NOT proven to lie inside this bound.
    bound41 = float(41*radius)
    return dict(
        case=label, n_epochs=41, num_pairs=1681, source_csv_sha256=sha256(sky_csv),
        original_BASS_Rust_blob=RUST_BLOB,
        E_initial=float(E[0]), E_final=float(E[-1]),
        K4_initial=c0, K4_final=c1, K4_0_final=float(K[0, -1]),
        angular_pattern_cosine_0_final=r4, angular_pattern_distance_squared_0_final=d2,
        max_original_two_time_csv_reconstruction_gap=max_gap,
        numerical_gram_eigenvalues=eigen.tolist(), eigen_fractions=(eigen/trace).tolist(),
        gram_participation_ratio=float(1/purity),
        exact_model_gram_rank_upper=3,
        fourth_41x41_eigenvalue_roundoff=float(rank4),
        pr270_entrywise_conditional_math_radius=radius,
        weyl_41_entrywise_radius=bound41,
        possible_second_mode_margin_not_certified=float(eigen[1]-bound41),
        second_mode_weyl_candidate_positive=bool(eigen[1]>bound41),
        rust_binary64_sky_center_interval_proof="NOT_RUN",
        continuum_second_eigenmode_certified=False,
    )


def analyze_all(input_dir: Path, pair_dir: Path, output: Path):
    prior = json.loads((pair_dir/"SCIENCE_RESULTS.json").read_text())
    require(prior["original_binary64_source_sha256"] == SOURCE_SHA, "original source SHA changed")
    require(prior["parent_pr270_head"] == "614a59acf1bec121cc0f5ef1386488917bba3dc2",
            "frozen source/code predecessor changed")
    require(prior["physical_rows"] == 10086, "original physical pair count changed")
    require(prior["input_numeric_rust_centers_are_NOT_rigorous_MPFR_intervals"],
            "missing original numerical trust ceiling")
    results = {}
    for order in ORDERS:
        for steps in STEPS:
            name = f"GL{order}_STEPS{steps}"
            filename = f"{name}_BASS_RUST_SKY.csv"
            result = analyze_case(input_dir/filename,
                 pair_dir/f"{name}_two_time_K4_1681.csv",
                 prior["input_file_sha256"][filename], name)
            require(result["E_initial"] > 0 and result["E_final"] > 0,
                    "non-positive source energy")
            results[name] = result
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "bass.ce1z.real_k4_gram_spectral_atlas.v1",
        "unit": "CE1Z_BASS_RUST_K4_DETERMINISTIC_GRAM",
        "original_source_sha256": SOURCE_SHA,
        "BASS_native_Rust_blob": RUST_BLOB,
        "parent_pr271_head": "9cf562496cb753fe831e684ccf0b4dd54f5c5d94",
        "parent_pr268_head": "c4d303ebd8294df8a4b564b140b88fc8e57b0e67",
        "theorem": "Reflection-even exact-real l4 K(u,v)=X(u).X(v), X in R3, PSD and rank<=3",
        "physical_scope": "massless collisionless diagonal expanding Bianchi I, Lambda0, (-,+,+,+), original 6 positive exact-binary cells, u in [0,0.08]",
        "interpretation": "single deterministic sky, not ensemble covariance or likelihood",
        "all_six_BASS_native_Rust_source_record_41_epochs_reused": True,
        "new_native_Rust_run": False,
        "native_subagent": "NOT_RUN",
        "distinct_author_R6_C9": "NOT_RUN",
        "continued_MPFR192_intervals": "PR270 conditional exact-real comparison, no new interval",
        "strict_original_h_target": 1e-5,
        "original_h_gate": "MET_BY_FROZEN_PR268_CI_NOT_REEXECUTED",
        "completed_upper_nodes": 9,
        "total_upper_nodes": 15,
        "new_completed_upper_nodes": 0,
        "ce1": "PARTIAL",
        "production_ready": False, "merge_ready": False, "auto_next": False,
        "cases": results,
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False)+"\n")
    print("CE1Z_GRAM_SPECTRAL_PHYSICS_6_CASES_PASS", output, flush=True)
    for k, r in results.items():
        print(k, "r4=", r["angular_pattern_cosine_0_final"],
              "lambda2_fraction=", r["eigen_fractions"][1],
              "Weyl_candidate=", r["second_mode_weyl_candidate_positive"])
    return payload


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--inputs", type=Path, default=BASE/"input")
    p.add_argument("--pairs", type=Path, default=BASE/"data")
    p.add_argument("--output", type=Path, required=True)
    args=p.parse_args()
    analyze_all(args.inputs, args.pairs, args.output)


if __name__ == "__main__":
    main()

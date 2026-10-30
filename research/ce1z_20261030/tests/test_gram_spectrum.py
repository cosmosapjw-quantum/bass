"""Data-grounded science checks for original BASS Rust CE1-Z Gram rank-three physics."""
import csv
import json
from pathlib import Path
import pytest
import numpy as np

from research.ce1z_20261030.gram_spectrum import (
    BASE, SOURCE_SHA, analyze_all, analyze_case, read_rows, sky_modes,
)


def test_six_original_bass_rust_gram_spectra(tmp_path):
    report = analyze_all(BASE/"input", BASE/"data", tmp_path/"summary.json")
    assert report["original_source_sha256"] == SOURCE_SHA
    assert report["completed_upper_nodes"] == 9 and report["total_upper_nodes"] == 15
    assert report["ce1"] == "PARTIAL" and not report["production_ready"]
    assert len(report["cases"]) == 6
    assert sum(r["num_pairs"] for r in report["cases"].values()) == 10086
    assert json.loads((tmp_path/"summary.json").read_text()) == report
    for case in report["cases"].values():
        assert case["n_epochs"] == 41
        assert case["max_original_two_time_csv_reconstruction_gap"] < 2e-12
        assert 0.99 < case["angular_pattern_cosine_0_final"] < 1.0
        assert case["angular_pattern_distance_squared_0_final"] > 0
        assert 1 <= case["gram_participation_ratio"] < 1.001
        assert case["numerical_gram_eigenvalues"][-1] > 0
        assert case["eigen_fractions"][0] > .9999
        assert case["eigen_fractions"][1] > 0
        assert case["exact_model_gram_rank_upper"] == 3
        assert abs(sum(case["eigen_fractions"])-1) < 3e-15
        assert abs(case["fourth_41x41_eigenvalue_roundoff"]) < 2e-12
        assert not case["continuum_second_eigenmode_certified"]


def test_gl8_16_physical_spectral_observables(tmp_path):
    r=analyze_all(BASE/"input", BASE/"data", tmp_path/"out.json")["cases"]["GL8_STEPS16"]
    assert abs(r["K4_0_final"] - .010792679546907028) < 2e-14
    assert abs(r["angular_pattern_cosine_0_final"] - .99951050578909) < 3e-13
    assert abs(r["gram_participation_ratio"] - 1.00017064748712) < 1e-10
    assert abs(r["eigen_fractions"][1] - .00008531633592395) < 2e-10
    assert r["second_mode_weyl_candidate_positive"] # only conditional, not formal binary64 interval proof
    assert r["weyl_41_entrywise_radius"] < r["numerical_gram_eigenvalues"][1]


def test_41_epoch_gram_symmetric_rank_three_and_psd():
    raw=read_rows(BASE/"input/GL6_STEPS4_BASS_RUST_SKY.csv")
    _,_,X,K=sky_modes(raw)
    assert X.shape == (41,3) and K.shape == (41,41)
    assert np.max(abs(K-K.T)) < 1e-15
    v=np.sin(np.arange(41,dtype=float))
    assert float(v@K@v) >= -1e-13
    assert np.linalg.eigvalsh(K)[-4] >= -1e-13
    assert np.linalg.eigvalsh(K)[-4] <= 2e-12


def test_original_source_hash_mutation_rejected(tmp_path):
    src=BASE/"input/GL8_STEPS4_BASS_RUST_SKY.csv"
    tampered=tmp_path/"tampered.csv"
    tampered.write_bytes(src.read_bytes().replace(b"8.99999999999998690e-1", b"8.99999999999998691e-1",1))
    assert tampered.read_bytes()!=src.read_bytes()
    with pytest.raises(ValueError, match="SHA256"):
        analyze_case(tampered, BASE/"data/GL8_STEPS4_two_time_K4_1681.csv",
                     json.loads((BASE/"data/SCIENCE_RESULTS.json").read_text())["input_file_sha256"]["GL8_STEPS4_BASS_RUST_SKY.csv"],
                     "GL8_STEPS4")


def test_negative_energy_rejected():
    rows=read_rows(BASE/"input/GL8_STEPS4_BASS_RUST_SKY.csv")
    rows[0]["E"]="-1"
    with pytest.raises(ValueError, match="positive sky energy"):
        sky_modes(rows)


def test_unphysical_odd_m_rejected():
    rows=read_rows(BASE/"input/GL8_STEPS4_BASS_RUST_SKY.csv")
    rows[1]["a_4_1_re"]=".1"
    with pytest.raises(ValueError, match="reflection symmetry"):
        sky_modes(rows)


def test_non_monotonic_time_rejected():
    rows=read_rows(BASE/"input/GL8_STEPS4_BASS_RUST_SKY.csv")
    rows[1]["u"]=".0003"
    with pytest.raises(ValueError, match="proper-time grid"):
        sky_modes(rows)


def test_numerical_center_is_not_interval_proof(tmp_path):
    r=analyze_all(BASE/"input",BASE/"data",tmp_path/"r.json")
    assert r["continued_MPFR192_intervals"].startswith("PR270 conditional")
    assert all(x["rust_binary64_sky_center_interval_proof"]=="NOT_RUN" for x in r["cases"].values())
    assert r["new_native_Rust_run"] is False

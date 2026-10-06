"""Real standalone production Rust execution. This does NOT test PyO3 integration.

Requires rustc on PATH, intentionally fails rather than skips without a compiler.
"""
from pathlib import Path
import subprocess

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def test_production_rust_codazzi_against_independent_numpy(tmp_path):
    binary = tmp_path / "codazzi-driver"
    subprocess.run(["rustc", "--edition=2021", str(ROOT / "tests/rust/codazzi_driver.rs"),
                    "-o", str(binary)], check=True, capture_output=True, text=True)
    rng = np.random.default_rng(20261006)
    sigma = rng.normal(size=(128, 3, 3))
    n = rng.normal(size=(128, 3, 3))
    # Half physical symmetric tensors, half unrestricted tensors to catch transposes.
    sigma[:64] = (sigma[:64] + sigma[:64].transpose(0, 2, 1)) / 2
    sigma[:64] -= np.trace(sigma[:64], axis1=1, axis2=2)[:, None, None] * np.eye(3) / 3
    n[:64] = (n[:64] + n[:64].transpose(0, 2, 1)) / 2
    a, q = rng.normal(size=(2, 128, 3))
    eps = np.zeros((3, 3, 3))
    eps[0, 1, 2] = eps[1, 2, 0] = eps[2, 0, 1] = 1
    eps[0, 2, 1] = eps[2, 1, 0] = eps[1, 0, 2] = -1
    expected = 3 * np.einsum("nb,nab->na", a, sigma) + np.einsum("abc,nbd,ncd->na", eps, n, sigma) - q
    inputs = np.concatenate([sigma.reshape(-1, 9), n.reshape(-1, 9), a, q], axis=1)
    result = subprocess.run([str(binary)], input="\n".join(" ".join(map(repr, row.tolist())) for row in inputs),
                            check=True, capture_output=True, text=True)
    actual = np.array([list(map(float, line.split())) for line in result.stdout.splitlines()])
    np.testing.assert_allclose(actual, expected, atol=2e-14, rtol=2e-14)

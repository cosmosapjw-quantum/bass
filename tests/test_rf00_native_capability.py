"""Native runtime capability evidence for RF-00."""

from __future__ import annotations

import os
import subprocess
import sys

import pytest


rust = pytest.importorskip("bianchi_rustcore")


def test_rayon_thread_pool_size_reports_an_effective_runtime_value() -> None:
    value = rust.rayon_thread_pool_size()

    assert isinstance(value, int)
    assert value >= 1


@pytest.mark.parametrize("threads", [1, 2])
def test_rayon_thread_pool_size_observes_fresh_process_configuration(
    threads: int,
) -> None:
    env = os.environ.copy()
    env["RAYON_NUM_THREADS"] = str(threads)
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            "import bianchi_rustcore as rust; print(rust.rayon_thread_pool_size())",
        ],
        check=True,
        capture_output=True,
        env=env,
        text=True,
        timeout=30,
    )

    assert int(completed.stdout.strip()) == threads

"""Contention-aware benchmark protocol for the Rust-first migration."""

from .host import ClaimLevel, derive_cpu_sets, parse_cpu_list, probe_host
from .protocol import (
    CONTAMINATION_LIMITS,
    balanced_schedule,
    bootstrap_log_median_ci,
    evaluate_pair,
    summarize_pairs,
)

__all__ = [
    "CONTAMINATION_LIMITS",
    "ClaimLevel",
    "balanced_schedule",
    "bootstrap_log_median_ci",
    "derive_cpu_sets",
    "evaluate_pair",
    "parse_cpu_list",
    "probe_host",
    "summarize_pairs",
]

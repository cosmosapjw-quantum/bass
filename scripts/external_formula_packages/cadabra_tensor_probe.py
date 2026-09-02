#!/usr/bin/env python3
"""Package-native Cadabra2 tensor-symmetry checks.

Cadabra is treated as an independent tensor CAS.  The checks are deliberately
bounded to canonical tensor identities; they do not select BASS conventions or
promote any BASS formula.
"""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path
from typing import Any, Callable


def _zero_text(expr: Any) -> bool:
    text = str(expr).strip().replace(" ", "")
    return text in {"0", "0;", "0.0"}


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("cadabra2.json")
    receipt: dict[str, Any] = {
        "schema_version": "1.0.0",
        "stage_id": "XCAS_01_EXTERNAL_FORMULA_PACKAGE_VERIFICATION",
        "package": "cadabra2",
        "package_axis": "INDEPENDENT_TENSOR_CAS",
        "authority_effect": "NONE",
    }
    try:
        import cadabra2
        from cadabra2 import (
            AntiSymmetric,
            Ex,
            Indices,
            RiemannTensor,
            Symmetric,
            canonicalise,
            collect_terms,
            meld,
        )

        Indices(Ex(r"{a,b,c,d,e,f}"))
        AntiSymmetric(Ex(r"A_{a b}"))
        Symmetric(Ex(r"Q_{a b}"))
        RiemannTensor(Ex(r"R_{a b c d}"))

        tests: dict[str, bool] = {}
        rendered: dict[str, str] = {}

        def run(name: str, source: str, operations: tuple[Callable[[Any], Any], ...]) -> None:
            expr = Ex(source)
            for operation in operations:
                operation(expr)
            collect_terms(expr)
            rendered[name] = str(expr)
            tests[name] = _zero_text(expr)

        run(
            "antisymmetric_symmetric_contraction",
            r"A_{a b} Q_{a b}",
            (canonicalise,),
        )
        run(
            "riemann_first_pair_antisymmetry",
            r"R_{a b c d}+R_{b a c d}",
            (canonicalise,),
        )
        run(
            "riemann_pair_exchange",
            r"R_{a b c d}-R_{c d a b}",
            (canonicalise,),
        )
        run(
            "riemann_first_bianchi",
            r"R_{a b c d}+R_{a c d b}+R_{a d b c}",
            (meld, canonicalise),
        )

        receipt.update(
            {
                "package_version": getattr(cadabra2, "__version__", "UNKNOWN"),
                "tests": tests,
                "rendered": rendered,
                "pass": all(tests.values()),
                "status": "PASS" if all(tests.values()) else "FAIL_FORMULA",
            }
        )
    except Exception as exc:
        receipt.update(
            {
                "status": "BLOCKED_RUNTIME",
                "pass": False,
                "exception_type": type(exc).__name__,
                "exception": str(exc),
                "traceback": traceback.format_exc(),
            }
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

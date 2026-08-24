"""
bianchi — Bianchi 배경 우주론 solver.

PR-01: x64 를 임포트 시점에 강제한다. 설계 §5.5 — float32 는 stiff 구간에서
       "그럴듯한 오답" 또는 max_steps 실패를 낸다. 협상 불가.
"""
import jax as _jax

_jax.config.update("jax_enable_x64", True)

import jax.numpy as _jnp
if _jnp.zeros(1).dtype != _jnp.float64:          # pragma: no cover
    raise RuntimeError(
        "x64 활성화 실패. bianchi 를 jax 배열 생성 '이전에' 임포트해야 한다."
    )

__version__ = "0.1.0"

from bianchi import conventions, algebra          # noqa: E402,F401

__all__ = ["conventions", "algebra", "__version__"]

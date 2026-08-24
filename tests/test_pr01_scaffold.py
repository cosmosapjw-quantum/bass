"""PR-01 완료 기준: x64 활성 + 임포트 정상."""
import jax.numpy as jnp
import bianchi


def test_x64_enabled():
    assert jnp.zeros(1).dtype == jnp.float64
    assert jnp.array(1.0).dtype == jnp.float64


def test_version():
    assert bianchi.__version__

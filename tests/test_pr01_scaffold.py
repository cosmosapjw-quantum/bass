"""PR-01 완료 기준: 명시적 오라클 x64 활성 + 임포트 정상."""
import bianchi
from bianchi.optional_dependencies import require_jax_x64

_, jnp = require_jax_x64(feature=__name__)


def test_x64_enabled():
    assert jnp.zeros(1).dtype == jnp.float64
    assert jnp.array(1.0).dtype == jnp.float64


def test_version():
    assert bianchi.__version__

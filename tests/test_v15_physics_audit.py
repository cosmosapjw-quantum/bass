"""
V15 · **물리 수식 총감사를 게이트로** — 기호 항등(sympy) + 문헌 상수 CRAG.

수치 오라클과 달리 기호 항등은 반올림·격자 의존이 없다: RHS 계수 하나만 틀려도
잔차 다항식이 0 이 아니게 된다.  구속 전파(class A Gauss, class B Codazzi)가
**구속면 밖에서도** 항등으로 닫힘을 고정한다.

★ 반증 기록 (감사자의 오류를 감사가 잡았다): 전단–곡률 분해를 처음
  K̇ = 2qK − 4Σ·S 로 적었더니 잔차가 정확히 +6Σ·S — 총항등이 0 이므로 틀린 것은
  코드가 아니라 분해였고, 참형은 K̇ = 2qK **+ 2Σ·S** (전단→곡률 교환항)다.
"""
import numpy as np
import sympy

from audit import v15_physics_audit as A


def test_class_a_gauss_constraint_propagates_identically():
    """★★ dΩ/dτ = Ω(2q−(3γ−2)) — class A RHS 전 계수의 기호 심판."""
    assert A.class_a_gauss_propagation() == 0


def test_class_a_shear_curvature_exchange_identity():
    """★★ K̇ = 2qK + 2(Σ₊S₊+Σ₋S₋) — 반증으로 확정한 교환항 부호."""
    assert A.class_a_shear_source_identity() == 0


def test_class_b_codazzi_propagates_identically():
    """★★ Ċ = 4(q+Σ₊−1)C — D2 의 측정 전파율이 기호로도 닫힌다."""
    assert A.class_b_codazzi_propagation() == 0


def test_kasner_parametrization_identities():
    a, b, c = A.kasner_roundtrip_identity()
    assert a == 0 and b == 0 and c == 0


def test_constants_match_the_literature():
    """★ web CRAG (2026-08: MathWorld/arXiv) 값과 코드 상수의 일치."""
    for name, code, lit in A.gauss_map_constants():
        assert abs(code - lit) < 1e-12, name


def test_the_wrong_decomposition_is_still_wrong():
    """★ 반증 기록의 감시자 — 옛 목표식(−4Σ·S)이 다시 옳아지면 기록을 고쳐야 한다."""
    Sp, Sm, N1, N2, N3, q = sympy.symbols("Sp Sm N1 N2 N3 q", real=True)
    S3 = sympy.sqrt(3)
    K = sympy.Rational(1, 12) * (N1**2 + N2**2 + N3**2
                                 - 2 * (N1 * N2 + N2 * N3 + N3 * N1))
    Splus = sympy.Rational(1, 6) * ((N2 - N3) ** 2 - N1 * (2 * N1 - N2 - N3))
    Sminus = (N3 - N2) * (N1 - N2 - N3) / (2 * S3)
    dN = [(q - 4 * Sp) * N1, (q + 2 * Sp + 2 * S3 * Sm) * N2,
          (q + 2 * Sp - 2 * S3 * Sm) * N3]
    dK = sum(sympy.diff(K, n) * dn for n, dn in zip((N1, N2, N3), dN))
    wrong = sympy.simplify(dK - (2 * q * K - 4 * (Sp * Splus + Sm * Sminus)))
    assert wrong != 0
    assert sympy.simplify(wrong - 6 * (Sp * Splus + Sm * Sminus)) == 0

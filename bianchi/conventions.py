"""
PR-03 · 규약 고정.

이 모듈의 본체는 상수 몇 개가 아니라 **설계 §9 의 함정 4가지를 코드로 막는 것**이다.
넷 다 '조용히 틀리는' 종류이므로, 각각을 (a) 명시 상수, (b) 타입 분리, (c) 런타임
가드, (d) 테스트로 박제한다.

  함정 1  프레임 각속도 부호 규약     -> ROTATION_CONVENTION + rotation_matrix()
  함정 2  게이지가 회전 3개를 다 씀   -> gauge_rotation_classB() 가 3개 전부 반환
  함정 3  trace-free 를 행렬연산으로  -> tracefree_from_5() 만 사용 (검증 포함)
  함정 4  심볼 충돌 + 순차 치환       -> 심볼릭 층 전용. safe_subs() 제공
  (추가)  WE/Ringstrom 9배 함정       -> Normalization 열거 + 변환맵
  (추가)  Sigma 기호 충돌 (√3 배)      -> ShearScalar 뉴타입
"""
from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Literal

import numpy as np

from bianchi._core_constants import EPS3, SQRT3
from bianchi.optional_dependencies import require_jax_x64

_, jnp = require_jax_x64(feature=__name__)

# ---------------------------------------------------------------- 기본 상수
#: Levi-Civita eps_{abc}, eps_123 = +1
EPS3_J = jnp.asarray(EPS3)


# ================================================================ 함정 1
class RotationConvention(enum.Enum):
    """프레임 각속도 R_a 의 부호 규약.

    COMMUTATOR (채택):
        [e_0, e_a] = -(H d_a^b + sigma_a^b + eps_a^{bc} R_c) e_b
    GENERATOR :
        [e_0, e_a] = -(H d_a^b + sigma_a^b - eps_a^{bc} R_c) e_b

    두 규약은 R^GEN = -R^COMM 로 관계된다.

    ─────────────────────────────────────────────────────────────────────
    ★ 마스터 규칙 (v1.1 재유도로 확정; audit/r1_*.py, r4_*.py, r5d_*.py)

      COMMUTATOR 규약에서 **모든 공간 프레임 지표**는 동일한 항을 받는다:

          벡터   Y_a' ⊃ +(R x Y)_a          = +eps_abc R^b Y^c
          텐서   X_ab' ⊃ +2 eps_{cd<a} R^c X_b>^d
                        = +[W, X]_ab ,  W_ab = -eps_abc R_c = rotation_matrix(R)

      예외 없음: sigma_ab, n_ab, a_a, v_a, B_a, 그리고 구속벡터 C_a 까지 전부
      같은 부호다.  이 규칙은 (i) Jacobi 항등식에서 ndot/adot, (ii) 프레임
      Einstein 텐서의 tracefree ij 성분, (iii) 구속 전파 행렬, (iv) tilted
      fluid 의 nabla^a T_ab = 0 — 네 경로에서 독립적으로 확인되었다.
    ─────────────────────────────────────────────────────────────────────

    ★ shear/N 섹터만 보면 이 부호를 **검출하지 못한다** — 게이지 조건으로 R 을
      풀 때 같은 규약 안에서 자기정합적으로 풀리기 때문이다. 오직 tilt 섹터
      (v_a') 와 자기장(B_a) 만 검출한다 -> tests/test_rotation_sign.py 필수.
    """

    COMMUTATOR = "commutator"
    GENERATOR = "generator"


#: 채택 규약. 모든 유도·codegen 이 이것을 쓴다.
ROTATION_CONVENTION = RotationConvention.COMMUTATOR


def rotation_matrix(R, convention: RotationConvention = ROTATION_CONVENTION):
    """각속도 벡터 -> 반대칭 행렬 W_ab.

    COMMUTATOR 규약에서 진화식에 들어가는 형태는 벡터 `+W @ Y`, 텐서 `+[W, X]`
    이며 W_ab = -eps_abc R_c 다 (부호가 GENERATOR 와 반대).
    """
    W = jnp.einsum("abc,c->ab", EPS3_J, jnp.asarray(R))
    return -W if convention is RotationConvention.COMMUTATOR else W


def rotation_apply_vector(R, Y):
    """공간 벡터의 회전항:  +(R x Y)_a  ( = rotation_matrix(R) @ Y )."""
    return rotation_matrix(R) @ jnp.asarray(Y)


def rotation_apply_tensor(R, X):
    """대칭 2차 텐서의 회전항:  +[W, X]_ab  ( = 2 eps_{cd<a} R^c X_b>^d )."""
    W = rotation_matrix(R)
    X = jnp.asarray(X)
    return W @ X - X @ W


def constraint_propagation_matrix(H, Sigma, A, R):
    """(C_0, C_a) = (Gauss, Codazzi) 잔차의 전파 행렬 M (4x4), dC/dt = M C.

        C_0' = -3H C_0 - 2 A^a C_a
        C_a' = -(4H d_ab + Sigma_ab) C_b + (R x C)_a

    v1.1 에서 프레임 Einstein 텐서의 축약 Bianchi 항등식으로부터 직접 유도.
    선형 동차이므로 C = 0 은 정확히 불변집합이다 (audit/r4_bianchi_constraints.py).
    """
    Sigma = jnp.asarray(Sigma); A = jnp.asarray(A)
    M = jnp.zeros((4, 4))
    M = M.at[0, 0].set(-3.0 * H)
    M = M.at[0, 1:].set(-2.0 * A)
    M = M.at[1:, 1:].set(-4.0 * H * jnp.eye(3) - Sigma + rotation_matrix(R))
    return M


# ================================================================ 함정 3
def tracefree_from_5(s00, s11, s01, s02, s12):
    """독립 5성분에서 trace-free 대칭 3x3 을 만든다.

    ★ `M - tr(M)/3 * I` 로 만들지 말 것: 원소가 복합식이 되어 심볼릭 치환 키로
      쓸 수 없고, 그 결과 치환이 통째로 무시되어도 계산은 '돌아간다'.
    """
    return jnp.array(
        [[s00, s01, s02], [s01, s11, s12], [s02, s12, -s00 - s11]]
    )


def sym_from_6(m00, m11, m22, m01, m02, m12):
    """독립 6성분에서 대칭 3x3 (trace 자유)."""
    return jnp.array(
        [[m00, m01, m02], [m01, m11, m12], [m02, m12, m22]]
    )


def five_from_tracefree(M):
    """trace-free 대칭 3x3 -> 독립 5성분 (역변환)."""
    return jnp.array([M[0, 0], M[1, 1], M[0, 1], M[0, 2], M[1, 2]])


# ================================================================ Sigma 기호 분리
@dataclass(frozen=True)
class ShearScalar:
    """shear 크기 스칼라. 두 정규화가 √3 배 차이나므로 타입으로 분리한다.

      Sigma_WE    = sqrt( (1/6) Sigma_ab Sigma^ab )   (설계 §2.3, 본 코드 기본)
      Sigma_theta = sigma / theta = Sigma_WE / sqrt(3) (관측 문헌 관행)

    섞으면 조용히 √3 배 틀린다. 산술은 같은 kind 끼리만 허용.
    """

    value: float
    kind: Literal["WE", "theta"] = "WE"

    def to(self, kind: Literal["WE", "theta"]) -> "ShearScalar":
        if kind == self.kind:
            return self
        f = 1.0 / SQRT3 if kind == "theta" else SQRT3
        return ShearScalar(self.value * f, kind)

    def __add__(self, other: "ShearScalar") -> "ShearScalar":
        if not isinstance(other, ShearScalar) or other.kind != self.kind:
            raise TypeError(
                f"ShearScalar kind 불일치: {self.kind} vs "
                f"{getattr(other, 'kind', type(other).__name__)}. "
                ".to() 로 명시 변환할 것."
            )
        return ShearScalar(self.value + other.value, self.kind)


# ================================================================ WE / Ringstrom
class Normalization(enum.Enum):
    """Hubble 정규화 규약.

    WE       : N = n/H     , S_pm 계수 1/6, K 계수 1/12    (채택)
    RINGSTROM: N = n/(3H)  , S_pm 계수 1/2 (곱 3), K 계수 3/4

    두 계는 N -> N/3 으로 동치이나, 한쪽의 S_pm 과 다른 쪽의 K 를 섞으면
    곡률항이 정확히 **9배** 틀린다.
    """

    WE = "WE"
    RINGSTROM = "Ringstrom"


NORMALIZATION = Normalization.WE

#: WE 규약의 곡률 계수
K_COEFF_WE = 1.0 / 12.0
S_COEFF_WE = 1.0 / 6.0
#: Ringstrom 규약
K_COEFF_RINGSTROM = 3.0 / 4.0
S_COEFF_RINGSTROM = 1.0 / 2.0


def N_we_to_ringstrom(N):
    """WE 의 N -> Ringstrom 의 N."""
    return jnp.asarray(N) / 3.0


def N_ringstrom_to_we(N):
    return jnp.asarray(N) * 3.0


# ================================================================ Codazzi 부호
#: 운동량 구속의 epsilon 항 상대부호. 접속에서 직접 유도 시 +1 만 해가 존재하고
#: -1 은 해가 없다 (derive.py L4). 좌표계 검산으로 독립 확인 (jet_check C3).
CODAZZI_EPS_SIGN = +1

#: G_0a = CODAZZI_G0A_SIGN * (3 a_b sigma^ab + eps^abc n_bd sigma_c^d)
#: 프레임 Einstein 텐서 생성기가 측정한 값 (gen_frame_einstein.py 앵커).
CODAZZI_G0A_SIGN = -1


def codazzi_residual(Sigma, N, A, q_flux=None):
    """C^a = 3 A_b Sigma^ab + eps^abc N_bd Sigma_c^d - (momentum flux).

    Sigma: (3,3) trace-free, N: (3,3) 대칭, A: (3,), q_flux: (3,) 정규화 운동량밀도.
    """
    Sigma = jnp.asarray(Sigma); N = jnp.asarray(N); A = jnp.asarray(A)
    term_a = 3.0 * jnp.einsum("b,ab->a", A, Sigma)
    term_e = CODAZZI_EPS_SIGN * jnp.einsum("abc,bd,cd->a", EPS3_J, N, Sigma)
    out = term_a + term_e
    if q_flux is not None:
        out = out - jnp.asarray(q_flux)
    return out


# ================================================================ 예외형 정규화
#: A_exc = A_WE (2배 환산 **없음**).
#: Omega = 1 - Sigma^2 - N_-^2 - 4A^2 의 계수 4 는 A 의 재정규화가 아니라
#: HHW 게이지 n23 = 3A 의 산물이다 (derive_exceptional.py 로 확정, U13).
A_EXCEPTIONAL_RESCALE = 1.0


# ================================================================ 함정 2
def gauge_rotation_classB(Sigma_minus, Sigma_12, Sigma_13, lam):
    """Hervik 게이지 유지가 강제하는 프레임 회전 **3개 전부**.

    조건 (i) a 가 e_1 에 고정: A_2' = A_3' = 0   -> R_2, R_3
         (ii) n22 = n33 (즉 N_- = 0)            -> R_1

    ★ R_1 만 켜고 계산하면 shear 방정식이 **전부** 틀리는데 N', lambda', A' 는
      맞아서 통과한 것처럼 보인다. 문헌의 Sigma_+' ⊃ 3(Sigma_12^2+Sigma_13^2)
      항은 곡률도 shear 도 아니라 바로 이 회전항 [W, Sigma] 이다.

    ★ v1.1 부호 정정 (외부검토 R1).  이 함수는 예전에 GENERATOR 부호로 값을
      돌려주면서 rotation_matrix()/charts.general/matter.fluid 는 COMMUTATOR 로
      소비하고 있었다 — 저장소 안에서 두 규약이 섞여 있던 유일한 지점이다.
      A_2' = -sqrt3 Sigma_12 A + (R x A)_2 = 0  =>  R_3 = +sqrt3 Sigma_12
      A_3' = -sqrt3 Sigma_13 A + (R x A)_3 = 0  =>  R_2 = -sqrt3 Sigma_13
      이 부호로 넣어야 Sigma_+' 의 +3(Sigma_12^2+Sigma_13^2) 과
      v_1' 의 -2 sqrt3 (Sigma_12 v_2 + Sigma_13 v_3) 이 동시에 재현된다
      (tests/test_rotation_sign.py 에서 회귀 고정).
    """
    R1 = SQRT3 * Sigma_minus * lam
    R2 = -SQRT3 * Sigma_13
    R3 = SQRT3 * Sigma_12
    return jnp.stack([R1, R2, R3])


# ================================================================ 함정 4 (심볼릭)
def safe_subs(expr, mapping):
    """SymPy 순차치환 오염 방지. 심볼릭 층에서만 사용."""
    return expr.subs(mapping, simultaneous=True)


# ================================================================ 요약
CONVENTION_CARD = f"""
signature      : (-,+,+,+)
frame          : e_0 = n (측지, 비회전), eps_123 = +1
units          : c = 8 pi G = 1
normalization  : {NORMALIZATION.value}  (N = n/H, S_pm 1/6, K 1/12)
rotation sign  : {ROTATION_CONVENTION.value}
                 [e_0,e_a] = -(H d + sigma + eps R) e_b ;  R^GEN = -R^COMM
Codazzi eps    : {CODAZZI_EPS_SIGN:+d}      (G_0a sign {CODAZZI_G0A_SIGN:+d})
A_exceptional  : x{A_EXCEPTIONAL_RESCALE:g}   (2배 환산 없음; 4A^2 는 게이지 n23=3A)
group param    : kappa = 1/h = n2 n3 / A^2   (운동 상수)
shear scalar   : Sigma_WE = sqrt3 * Sigma_theta  (타입 분리 필수)
""".strip()

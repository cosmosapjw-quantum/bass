"""
J2b · **tilted 좌변의 계수공간 조립** — equation_lhs 의 2l+1 표현판 (59차).

구성 (9항):
  · 대수 6항 (H, Ω, D, E, A, B, C): J2 닫힌형 블록 — 임의 l.
    Ω 항은 rot_block ((1/l)·생성자) 에 −l 을 곱해 정확히 −l·pstf(J·W(ω)) 재현.
  · 기하 3항 (⊥J̇, div-con, div-free): geo-별 **추출행렬** — dense 오라클
    (backend="python") 을 정준기저로 사영 (l ≤ 6).  ★ l>6 확장은 구조상수
    닫힌형 유도가 필요 — **J2c 명시 이월** (표현가능성 프로브: 추출행렬이
    블록족 스팬에 기계정밀 분해되는지의 실측이 시험에 있다).

질량행렬 (두 경로):
  경로 A — 닫힌형 블록 조립 (tilted_mass 독스트링 구조를 정준기저로):
      M[(l,i)←(l,i)]     = γ·I
      M[(l,i)←(l+1,i)]   = s_dc·γ·CV_v        (contract_vec_block · v)
      M[(l,i)←(l−1,i+1)] = s_df·(−l/(2l+1))·γ·OV_v   (outer_vec_block · v)
  경로 B — dense LHS 의 J̇-선형부 추출 (J=0; 닫힌형 전혀 안 씀) — 시험 게이트.
  (SVD-기저 tilted_mass 의 O-회전 대조는 선택 3경로 — J1 직교변환 시험이 담보.)
"""
from __future__ import annotations

import numpy as np

from bianchi.matter._coeff_contract import ClosedGeoBlocksContract, omega_vector
from bianchi.matter import pstf_coeff as PC
from bianchi.matter import tilted_terms as TT
from bianchi.matter.hierarchy import L_MAX_SUPPORTED
from bianchi.matter.tilted import SIGNS


def _omega_vec(W):
    """반대칭 ω 행렬 → w (카르테시안), W = +ε·w 규약 (rot_block 과 동일).

    ★ 반증 기록 (59차): 1차 추출부호 (+½[W₂₁−W₁₂,…]) 는 Ω-항 비율 정확 −1
    로 반증됐다 — geo 의 W 에 대해 ε·w_old = −W 였던 것.  부호 정정 후
    핀 |ε·w − W| ≤ 1e−18 이 시험에 있다."""
    return omega_vector(W)


class GeoMats:
    """기하 3항의 (X, Ẋ)-선형 추출행렬 — geo 고정, l ≤ 6, lazy 캐시.

    op(X, dX) = P·x + Q·dx  (x = 정준계수).  perp_dot: l→l; div_con: l+1→l;
    div_free: l−1→l (PSTF 포함).  전부 dense 오라클(backend="python") 사영."""

    _ID_KEYS = ("eup", "edn", "deup", "hmix", "uup", "G")

    def __init__(self, geo):
        self.geo = geo
        self._cache = {}
        # ★ 리뷰 MAJOR: geo 제자리 변이 시 스테일 행렬 (0.77 편차 시연) —
        #   R5a 사고 패턴 (tilted_terms._rc_geo) 과 동일.  배열 id 스냅샷으로
        #   매 추출마다 재검증한다.
        self._geo_ids = tuple(id(geo[k]) for k in self._ID_KEYS)

    def _check_geo(self):
        if tuple(id(self.geo[k]) for k in self._ID_KEYS) != self._geo_ids:
            raise RuntimeError("GeoMats: geo 배열이 교체됨 — 캐시 스테일 위험. "
                               "새 GeoMats(geo) 를 만들 것 (R5a 교훈).")

    def _extract(self, key, l_out, l_in, fn):
        self._check_geo()
        if key in self._cache:
            return self._cache[key]
        if max(l_out, l_in) > L_MAX_SUPPORTED:
            raise ValueError(
                f"기하항 추출은 l ≤ {L_MAX_SUPPORTED} — l>6 은 구조상수 닫힌형"
                " 유도(J2c) 몫")
        nP, nQ = 2*l_out + 1, 2*l_in + 1
        P, Q = np.zeros((nP, nQ)), np.zeros((nP, nQ))
        zero = np.zeros((3,) * l_in) if l_in else 0.0
        for j in range(nQ):
            e = np.zeros(nQ)
            e[j] = 1.0
            X = PC.from_ccoef(e, l_in)
            P[:, j] = PC.to_ccoef(fn(np.asarray(X, float),
                                     np.asarray(zero, float)), l_out)
            Q[:, j] = PC.to_ccoef(fn(np.asarray(zero, float),
                                     np.asarray(X, float)), l_out)
        P.setflags(write=False)
        Q.setflags(write=False)
        self._cache[key] = (P, Q)
        return P, Q

    def perp_dot(self, l):
        return self._extract(("pd", l), l, l,
                             lambda X, dX: TT.perp_dot(X, dX, self.geo,
                                                       backend="python"))

    def div_con(self, l):
        return self._extract(("dc", l), l, l + 1,
                             lambda X, dX: TT.div_contracted(
                                 X, dX, self.geo, backend="python"))

    def div_free(self, l):
        return self._extract(("df", l), l, l - 1,
                             lambda X, dX: TT.div_free_index(
                                 X, dX, self.geo, l, backend="python"))


_GM_CACHE = {}


def geomats_for(geo):
    """geo-배열 id 로 키한 GeoMats 재사용 (리뷰: 매 호출 재구축 ×128 제거)."""
    key = tuple(id(geo[k]) for k in GeoMats._ID_KEYS)
    gm = _GM_CACHE.get(key)
    if gm is None:
        gm = _GM_CACHE[key] = GeoMats(geo)
    return gm


def equation_lhs_coeff(Jc, dJc, geo, l, i, gm=None, signs=None):
    """`tilted_equation.equation_lhs` 의 정준계수판 — 항별 동일 수식."""
    s = SIGNS if signs is None else signs
    if gm is None:
        gm = geomats_for(geo)
    n = l + 2 * i
    H = geo["H"]
    s5 = PC.sigma_to_c5(geo["sigma"])
    w = _omega_vec(geo["omega"])
    u3 = PC.vec_to_c3(geo["udot"])

    def g(ll, ii):
        return np.asarray(Jc[(ll, ii)], float)

    def dg(ll, ii):
        return np.asarray(dJc[(ll, ii)], float)

    P, Q = gm.perp_dot(l)
    out = P @ g(l, i) + Q @ dg(l, i)
    out = out + H * ((3.0 + n) * g(l, i) + (1.0 - n) * g(l, i + 1))
    Pc, Qc = gm.div_con(l)
    out = out + s["divcon"] * (Pc @ g(l + 1, i) + Qc @ dg(l + 1, i))
    if l >= 1:
        cf = l / (2.0 * l + 1.0)
        Pf, Qf = gm.div_free(l)
        out = out + s["divfree"] * (-cf) * (Pf @ g(l - 1, i + 1)
                                            + Qf @ dg(l - 1, i + 1))
        # (Ω): −l·pstf(J·W(ω)) = −l·apply(rot_block, ·, w)   (rot = (1/l)·생성자)
        out = out + s["Omega"] * (-l) * PC.apply_block(PC.rot_block(l),
                                                       g(l, i), w)
        cd = l / (2.0 * l + 1.0)
        GO_v = PC.outer_vec_block(l)
        tD = ((l + n + 1.0) * PC.apply_block(GO_v, g(l - 1, i), u3)
              + (2.0 - n) * PC.apply_block(GO_v, g(l - 1, i + 1), u3))
        out = out + s["D"] * cd * tD
    GC_v = PC.contract_vec_block(l)
    tE = (n - 2.0) * PC.apply_block(GC_v, g(l + 1, i), u3)
    if (l - n) != 0.0:
        tE = tE + (l - n) * PC.apply_block(GC_v, g(l + 1, i - 1), u3)
    out = out + s["E"] * tE
    if l >= 1:
        ca = l / (2.0 * l + 3.0)
        G1 = PC.c1_block(l)
        tA = ((2.0 * n + 3.0) * PC.apply_block(G1, g(l, i), s5)
              + (2.0 - 2.0 * n) * PC.apply_block(G1, g(l, i + 1), s5))
        out = out + s["A"] * ca * tA
    G2 = PC.c2_block(l)
    tB = (n - 1.0) * PC.apply_block(G2, g(l + 2, i), s5)
    if (l - n) != 0.0:
        tB = tB + (l - n) * PC.apply_block(G2, g(l + 2, i - 1), s5)
    out = out + s["B"] * tB
    if l >= 2:
        cc = l * (l - 1.0) / (4.0 * l * l - 1.0)
        GOs = PC.outer_block(l)
        tC = ((n - 1.0) * PC.apply_block(GOs, g(l - 2, i + 2), s5)
              - (l + n + 1.0) * PC.apply_block(GOs, g(l - 2, i + 1), s5))
        out = out + s["C"] * cc * tC
    return out


def mass_blocks_canonical(v, l, signs=None):
    """질량행렬 블록 (경로 A — 닫힌형): (대각, ←(l+1,i), ←(l−1,i+1))."""
    s = SIGNS if signs is None else signs
    gam = 1.0 / np.sqrt(1.0 - float(np.dot(v, v)))
    v3 = PC.vec_to_c3(v)
    diag = gam * np.eye(2*l + 1)
    up = s["divcon"] * gam * np.einsum("pqa,a->pq",
                                       PC.contract_vec_block(l), v3)
    down = (s["divfree"] * (-l / (2.0*l + 1.0)) * gam
            * np.einsum("pqa,a->pq", PC.outer_vec_block(l), v3)) \
        if l >= 1 else None
    return diag, up, down


def mass_blocks_for(geo, l, signs=None):
    """geo 가 나르는 v/γ 로 질량블록 — v 두-진실원 제거 (리뷰 MINOR 2)."""
    return mass_blocks_canonical(geo["v"], l, signs=signs)


# ═══════════════════════════════ J2c · 기하 3항의 닫힌 재구성 (임의 l)
class ClosedGeoBlocks(ClosedGeoBlocksContract):
    """기하 3항을 **합성형 항등**으로 닫아 임의 l 제공 (60차).

    측정 사슬 (audit 없이 시험이 직접 게이트):
      · perp X-부 = 순수 회전 Σw_a·B_a (I·c1 계수 전부 ~1e−17 — 사틀 회전항의
        수치 증명), Q-부 = γI (2.2e−16).
      · div_con/div_free X-부: 순수 cv/ov 스팬은 **실패** (2.8e−2) — V₂-결합
        성분 존재.  합성족 {cv(3), B_x∘cv(9)} 로 정확 (7e−17).
      · ★ 단일-l 적합은 중복방향 최소노름 때문에 타-l 로 **연장 실패** (2.7e−2
        반증) — **결합적합 (l=2,3)** 이 연산자-일관 해를 고정하고 보류 l=4,5,6
        을 ≤2.8e−16 예측 (l-균일 항등의 증명; J1 dense-창 검증과 동일 인식론).
      · Q-부: div_con=γ·CV_v, div_free=γ·OV_v (질량블록과 동일 — 5e−17).
      · l=0 특수화: c1(l3=2)·회전생성자는 스칼라 표현에서 **정확히 소멸**
        (삼각조건) — 영행렬 치환은 패딩이 아니라 그 연산자의 l=0 값.
    """

    _ID_KEYS = GeoMats._ID_KEYS + ("v",)

    def __init__(self, geo, fit_ls=(2, 3)):
        gm = GeoMats(geo)
        self.geo = geo
        self.gamma = float(geo["gamma_lorentz"])
        self.v3 = PC.vec_to_c3(geo["v"])
        # ★ 리뷰: 적합계수·γ·v3 는 __init__ 시점 동결 — geo 배열 교체 시
        #   무언 스테일 (GeoMats 와 동일한 R5a 위험).  id 스냅샷 가드.
        self._geo_ids = tuple(id(geo[k]) for k in self._ID_KEYS)
        self.c_pd = self._joint_fit(lambda l: gm.perp_dot(l)[0],
                                    self._perp_fams, fit_ls)
        self.c_dc = self._joint_fit(lambda l: gm.div_con(l)[0],
                                    self._cv_fams, fit_ls)
        self.c_df = self._joint_fit(lambda l: gm.div_free(l)[0],
                                    self._ov_fams, fit_ls)

    @staticmethod
    def _perp_fams(l):
        f = [np.eye(2*l + 1)]
        if l == 0:                     # l=0: σ-결합(l3=2)·회전생성자 정확 0
            return f + [np.zeros((1, 1))] * 8
        f += [np.einsum("pqk,k->pq", PC.c1_block(l), np.eye(5)[k])
              for k in range(5)]
        f += [l * PC.rot_block(l)[:, :, a] for a in range(3)]
        return f

    @staticmethod
    def _cv_fams(l):
        b = [PC.contract_vec_block(l)[:, :, a] for a in range(3)]
        if l == 0:                     # 회전생성자 = 0 (스칼라 표현)
            return b + [np.zeros((1, 3))] * 9
        R = PC.rot_block(l)
        return b + [l * R[:, :, x] @ b[a] for x in range(3) for a in range(3)]

    @staticmethod
    def _ov_fams(l):
        b = [PC.outer_vec_block(l)[:, :, a] for a in range(3)]
        R = PC.rot_block(l)
        return b + [l * R[:, :, x] @ b[a] for x in range(3) for a in range(3)]

    @staticmethod
    def _joint_fit(getter, famf, ls):
        rows, rhs = [], []
        for l in ls:
            A = np.stack([x.ravel() for x in famf(l)], axis=1)
            rows.append(A)
            rhs.append(getter(l).ravel())
        A, y = np.vstack(rows), np.concatenate(rhs)
        c, *_ = np.linalg.lstsq(A, y, rcond=None)
        if np.abs(A @ c - y).max() > 1e-12:
            raise RuntimeError("ClosedGeoBlocks: 합성형 적합 실패 — 기하 확장?")
        return c

    @staticmethod
    def _recon(c, fams):
        return sum(ci * f for ci, f in zip(c, fams))

    def _check_geo(self):
        if tuple(id(self.geo[k]) for k in self._ID_KEYS) != self._geo_ids:
            raise RuntimeError("ClosedGeoBlocks: geo 배열이 교체됨 — 적합계수 "
                               "스테일 위험. 새로 만들 것 (R5a 교훈).")

    def perp_dot(self, l):
        self._check_geo()
        P = self._recon(self.c_pd, self._perp_fams(l))
        return P, self.gamma * np.eye(2*l + 1)

    def div_con(self, l):
        self._check_geo()
        P = self._recon(self.c_dc, self._cv_fams(l))
        Q = self.gamma * np.einsum("pqa,a->pq", PC.contract_vec_block(l),
                                   self.v3)
        return P, Q

    def div_free(self, l):
        self._check_geo()
        P = self._recon(self.c_df, self._ov_fams(l))
        Q = self.gamma * np.einsum("pqa,a->pq", PC.outer_vec_block(l), self.v3)
        return P, Q

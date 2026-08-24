"""
J2 · 연산자 확장 (vec·rot) + 계층 스왑 유도 기록 (58차).

확정 사슬:
  (1) vec 블록: ov(l−1→l) = √(D_l/(D_{l−1}D₁)) — J1 곱-사영 정리의 벡터판
      (자유상수 없음).  cv(l+1→l) = R_ov(l+1) — 수반항등 (c2 증명과 동형:
      pstf 의 δ-보정은 무대각합 K 와 직교, 대칭 K 가 지표위치를 자유롭게 함;
      랭크 간격 l−1 vs l−2 는 논증에 미사용 — 리뷰 확인).  dense ≤7.8e−16.
      부수정리 (리뷰): cv 의 PSTF-부는 전체다 (대칭·무대각합 입력이면 자동).
  (2) rot 블록 (ω): Gaunt 형 불가 (l+l+1 홀수 패리티 소멸) — 생성자 경로.
      **R_rot(l) = 1/l (슬롯평균 정리)**: 대칭텐서의 단일슬롯 회전을 대칭화
      하면 전체 생성자의 1/l (PSTF 보존).  dense l=1..6 정확 (3.9e−16).
  (3) ★ 변환식 2단 반증·정정: 1차 조립 V·(−iL)·V† 는 dense 대조에서
      "y-축만 부호반전" — 이를 실기저 위상 규약 차이로 **오진**하고 y-플립
      패치로 봉합했었다.  리뷰 진단: 실계수는 c_re = conj(V)·c_cx 이므로
      옳은 변환은 **conj(V)·(+iL)·Vᵀ** — 1차 식은 (i) 켤레 누락 (실행렬
      x,z 축만 반전) + (ii) 전역 부호 (3축 반전) 의 **두 오류가 상쇄**되어
      y-반전으로 위장했다.  교훈 박제: dense 심판이 결과를 지켜도 원인
      오진은 다음 연산자 추가에서 무심판 영역(l>6)의 함정이 된다 — 정정
      후 공동 공변 게이트 ([G,CV]=CV(Wv), [G,C1]=C1(G₂σ), l=8 포함) 신설.
  (4) 계층 스왑: hierarchy_rhs_coeff ≡ dense (전 격자 ≤1e−13), l=10 가동.
      계수 4종 (l/(2l+3), −2i, l(l−1)/(4l²−1), H-항) 라인별 대조 (리뷰).
  (5) rg 영속화: l≤12 (l3∈{1,2}) npz 36KB, 규약 스탬프, 임포트 자동탑재
      (7ms — 콜드 sympy 6.4s 대비; 리뷰 MAJOR "휴면 캐시" 정정).

J2b 이월 (명시): tilted equation_lhs 조립 (질량행렬 포함) — rot/vec 블록
준비 완료, 축 규약 혼용 금지 (rot 카르테시안 vs vec 정준 (y,z,x)) 문서화.

실행: python -m audit.j2_operator_extensions
"""
from __future__ import annotations

import numpy as np

from bianchi.matter import pstf_coeff as PC


def transform_diagnosis(l=3):
    """(3) 의 상쇄 구조 재현: 1차 식 = 정정 식 에 y-플립을 합성한 것."""
    V = PC._real_unitary(l)
    n = 2*l + 1
    m = np.arange(-l, l + 1)
    Lz = np.diag(m).astype(complex)
    Lp = np.zeros((n, n), complex)
    for k in range(n - 1):
        mm = k - l
        Lp[k + 1, k] = np.sqrt(l*(l + 1) - mm*(mm + 1))
    Lm = Lp.conj().T
    Ls = (0.5*(Lp + Lm), -0.5j*(Lp - Lm), Lz)
    out = {}
    for ax, L in enumerate(Ls):
        wrong = (V @ (-1j*L) @ V.conj().T).real
        right = (np.conj(V) @ (1j*L) @ V.T).real
        flip = -1.0 if ax == 1 else 1.0
        out[ax] = float(np.abs(wrong - flip*right).max())
    return out                                      # 전 축 ~1e−16 이어야 함


def report():
    print("== transform diagnosis (wrong = ±right):", transform_diagnosis())
    print("== disk tables loaded:", len(PC._DISK))


if __name__ == "__main__":
    report()

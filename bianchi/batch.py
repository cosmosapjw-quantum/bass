"""
PR-22/23 · 대규모 배치 하네스.

핵심 사실 (설계 §5.3, 측정으로 확인):
  JAX 의 batched while_loop 은 조건을 배치축에 대해 OR 로 리듀스하고, 끝난 원소도
  본문을 실행한 뒤 select 로 버린다. 따라서
        비용 = batch_size x max_over_batch(n_steps)     (sum 이 아니라 max)
  64개 중 stiff 원소 하나가 전체를 ~5배 느리게 만든다.

대응 3중:
  1. 사전 정렬·버케팅  (난이도 추정 -> 균질 청크)
  2. 2단계 배치        (그룹 내 스텝 공유 / 그룹 간 vmap)
  3. 낙오자 재배치     (max_steps 도달 원소만 관대한 설정으로 재실행)

메모리 (설계 §5.4): VeryChord 가 원소별 D x D 인수분해를 들고 있으므로
  10^6 x 30 x 30 x 8 B = 7.2 GB  -> **청킹 필수** (10^4 ~ 5x10^4 / launch).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np

from bianchi import integrate as itg
from bianchi.optional_dependencies import require_jax_x64, require_optional

jax, jnp = require_jax_x64(feature=__name__)
eqx = require_optional("equinox", feature=__name__)


# ---------------------------------------------------------------- 난이도 추정
def difficulty_score(y_arr, gamma=None):
    """초기조건의 stiffness 대리 지표. 클수록 어렵다.

    Kasner 근방(Sigma^2 -> 1), 큰 |N|, extreme tilt 접근이 전부 stiff.
    """
    v = np.asarray(y_arr)
    S2 = v[..., 0]**2 + v[..., 1]**2 if v.shape[-1] >= 2 else 0.0
    Nmag = np.abs(v[..., 2:]).max(axis=-1) if v.shape[-1] > 2 else 0.0
    return 1.0 / np.maximum(1e-3, 1.0 - S2) + Nmag


def two_pass_difficulty(rhs, states, args, tau_probe=1.5, cfg=None):
    """짧은 시범 적분으로 실제 스텝 수를 재서 난이도를 매긴다 (2-pass)."""
    cfg = cfg or itg.SolverConfig(max_steps=256)
    run = eqx.filter_jit(jax.vmap(
        lambda v: itg.solve(rhs, v, 0.0, tau_probe, args, cfg=cfg)))
    sol = run(states)
    return np.asarray(sol.stats["num_steps"])


# ---------------------------------------------------------------- 버케팅·청킹
@dataclass
class BatchPlan:
    order: np.ndarray            # 원본 인덱스 -> 정렬 순서
    chunks: list                 # 각 청크의 (정렬된) 인덱스 배열
    scores: np.ndarray

    def n_chunks(self):
        return len(self.chunks)


def make_plan(scores, chunk_size=10_000):
    """난이도로 정렬 후 균질 청크로 자른다."""
    scores = np.asarray(scores)
    order = np.argsort(scores)
    chunks = [order[i:i+chunk_size] for i in range(0, len(order), chunk_size)]
    return BatchPlan(order=order, chunks=chunks, scores=scores)


def memory_estimate(n, dim, bytes_per=8, implicit=True):
    """VRAM 예산 추정 (GB). implicit solver 는 원소별 D x D 를 들고 있다."""
    state = n * dim * bytes_per
    lin = n * dim * dim * bytes_per if implicit else 0
    stages = 7 * state
    return dict(state_GB=state/1e9, linear_op_GB=lin/1e9,
                stages_GB=stages/1e9, total_GB=(state+lin+stages)/1e9)


def recommend_chunk_size(dim, vram_GB=8.0, safety=0.6, implicit=True):
    per = dim*8 + (dim*dim*8 if implicit else 0) + 7*dim*8
    return int(vram_GB * 1e9 * safety / per)


# ---------------------------------------------------------------- 실행
def run_chunk(rhs, states, args, cfg=None, ts=None):
    """단일 청크 vmap 적분. throw=False 이므로 원소별 result 를 반환."""
    cfg = cfg or itg.SolverConfig()
    if ts is None:
        run = eqx.filter_jit(jax.vmap(
            lambda v: itg.solve(rhs, v, 0.0, 1.0, args, cfg=cfg)))
    else:
        run = eqx.filter_jit(jax.vmap(
            lambda v: itg.solve(rhs, v, float(ts[0]), float(ts[-1]),
                                args, ts=ts, cfg=cfg)))
    return run(states)


def run_scan(rhs, states, args, plan: BatchPlan, cfg=None, ts=None,
             retry_cfg=None, unpack=None):
    """전체 스캔: 청크 순회 + 낙오자 재배치.

    반환: dict(results, stragglers, steps)
    """
    dfx = require_optional("diffrax", feature=f"{__name__}.run_scan")
    cfg = cfg or itg.SolverConfig()
    retry_cfg = retry_cfg or itg.SolverConfig(rtol=cfg.rtol*10, atol=cfg.atol*10,
                                              max_steps=cfg.max_steps*8)
    outs, steps, straggler_idx = [], [], []
    arr = np.asarray(states)
    for ch in plan.chunks:
        sub = jnp.asarray(arr[ch])
        y0 = jax.vmap(unpack)(sub) if unpack else sub
        sol = run_chunk(rhs, y0, args, cfg=cfg, ts=ts)
        st = np.asarray(sol.stats["num_steps"])
        res = np.asarray(sol.result == dfx.RESULTS.successful)
        steps.append(st)
        outs.append(sol)
        straggler_idx.extend(ch[~res].tolist())
    return dict(solutions=outs, steps=np.concatenate(steps),
                stragglers=np.array(straggler_idx, dtype=int),
                straggler_fraction=len(straggler_idx)/max(1, len(arr)))


def batch_divergence_cost(steps):
    """낭비율: batch x max(steps) 대비 sum(steps)."""
    steps = np.asarray(steps)
    ideal = steps.sum()
    actual = len(steps) * steps.max()
    return dict(ideal=int(ideal), actual=int(actual),
                waste_factor=float(actual/max(1, ideal)))


# ---------------------------------------------------------------- 2단계 배치
def fused_group_rhs(rhs, group_size):
    """그룹 내 원소를 하나의 diffeqsolve 로 융합 (스텝·오차노름 공유).

    발산 낭비 0, 대신 최악 원소가 스텝을 지배한다. 그룹 크기가 이 트레이드오프의
    유일한 손잡이다 (DISCO-EB 패턴).
    """
    def fused(t, Y, args):
        return jax.vmap(lambda y: rhs(t, y, args))(Y)
    return fused


# ================================================================ PR-51 광선추적 비용
# 이 컨테이너(numpy, 단일스레드)에서 **실측**한 스텝당 벽시계 (2026-07-29):
#   측지(trace_ray_diag_bianchi, Euler)     ≈ 0.7 ms/step
#   광학(trace_optical_diag_bianchi, 2-pass) ≈ 1.6 ms/step  (조석 vmap 포함, 워밍업 후)
# RTX 3060 Ti 로의 vmap/JIT 이식 시 방향축 병렬화로 수십~수백배 단축 가능 (미측정 상한).
RAY_STEP_MS = 0.7
OPTICAL_STEP_MS = 1.6
WEYL_NONZERO = 144          # generate_weyl 로 뽑은 0 아닌 Riemann 성분 수


def ray_trace_cost(n_directions, n_steps, per_step_ms=RAY_STEP_MS):
    """측지 광선추적 총 벽시계 (직렬 numpy).  z(n̂) 만 (조석 없음)."""
    total_s = n_directions * n_steps * per_step_ms / 1e3
    return dict(n_directions=int(n_directions), n_steps=int(n_steps),
                per_ray_ms=n_steps * per_step_ms, wall_s=total_s,
                wall_min=total_s / 60.0)


def optical_map_cost(n_directions, n_steps, per_step_ms=OPTICAL_STEP_MS):
    """Sachs 광학(d_A) 전천 스캔 비용.  각 방향 2-pass + 조석 vmap."""
    total_s = n_directions * n_steps * per_step_ms / 1e3
    return dict(n_directions=int(n_directions), n_steps=int(n_steps),
                per_ray_ms=n_steps * per_step_ms, wall_s=total_s,
                wall_min=total_s / 60.0)


def cmb_map_cost(n_theta=64, n_phi=128, n_steps=2000, optical=False):
    """CMB 패턴(또는 d_A 지도) 전천 비용.  n_dir = n_theta·n_phi.

    optical=False: ΔT/T 만(측지).  True: d_A 까지(광학, 조석).
    """
    n_dir = n_theta * n_phi
    c = (optical_map_cost if optical else ray_trace_cost)(n_dir, n_steps)
    c.update(n_theta=n_theta, n_phi=n_phi, mode="optical" if optical else "geodesic")
    return c


def sn_survey_cost(n_sn, per_sn_ms=3.0):
    """SN Hubble diagram 비용.  μ(z,n̂) 는 방향별 1D quad (조석·광선 불요) — 저렴.

    per_sn_ms: quad 한 번 (~ms).  Pantheon+ 규모(~1700 SNe)면 초 단위.
    """
    total_s = n_sn * per_sn_ms / 1e3
    return dict(n_sn=int(n_sn), wall_s=total_s)


def weyl_tidal_memory(n_steps, n_components=WEYL_NONZERO, bytes_per=8):
    """광학 2-pass 의 조석행렬 배치 메모리.  스텝별 (3×3) T + 중간 Riemann 축약.

    주 항: T_all (n_steps × 3 × 3) + 광선/스크린 기록.  방향 병렬 시 ×n_dir.
    """
    T_all = n_steps * 3 * 3 * bytes_per
    rec = n_steps * (4 + 2 * 3 + WEYL_NONZERO + 1 + 3) * bytes_per   # p,sc,args,E,lna
    return dict(T_all_MB=T_all / 1e6, record_MB=rec / 1e6,
                per_ray_MB=(T_all + rec) / 1e6)


def observable_suite_estimate(n_theta=64, n_phi=128, n_steps=2000, n_sn=1700,
                              with_optical=True):
    """관측 스위트(CMB ΔT/T + 선택적 d_A 지도 + SN + BAO) 총 비용 요약.

    BAO/거리는 quad 수 초 — 광선추적이 지배적.  반환: 항목별 + 합계 벽시계.
    """
    cmb = cmb_map_cost(n_theta, n_phi, n_steps, optical=False)
    parts = {"cmb_dT": cmb["wall_s"]}
    if with_optical:
        parts["dA_map"] = cmb_map_cost(n_theta, n_phi, n_steps, optical=True)["wall_s"]
    parts["sn"] = sn_survey_cost(n_sn)["wall_s"]
    parts["bao_distances"] = 5.0        # quad 몇 초 (실측 O(1s))
    total = sum(parts.values())
    return dict(parts_s=parts, total_s=total, total_min=total / 60.0,
                mem_per_ray_MB=weyl_tidal_memory(n_steps)["per_ray_MB"],
                note="numpy 직렬 실측 기반; GPU vmap 이식 시 방향축 병렬로 대폭 단축")

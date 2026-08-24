"""
Q11–Q14 · **런타임** — 결정성 · 체크포인트 · 앙상블 · 출력 (76차).

장기 통계 run 의 전제는 하나다: **같은 시드 → 스레드 수와 무관하게 비트 동일.**
그래서 병렬성은 **멤버 단위**로만 두고, 축약은 고정 순서 pairwise 로 강제한다.
"""
from __future__ import annotations

import hashlib
import json
import os

import numpy as np

SCHEMA_VERSION = 1


# ───────────────────────────────────────────── Q11 결정성
def reduce_det(v):
    """고정 순서 pairwise 합 — 부동소수 비결합성 회피 (스레드 수 무관)."""
    a = np.asarray(v, float).ravel()
    if a.size == 0:
        return 0.0
    while a.size > 1:
        n = a.size // 2
        head = a[:2 * n].reshape(n, 2).sum(axis=1)
        a = np.concatenate([head, a[2 * n:]]) if a.size % 2 else head
    return float(a[0])


def config_hash(cfg):
    return hashlib.blake2b(json.dumps(cfg, sort_keys=True, default=str)
                           .encode(), digest_size=8).hexdigest()


def split_seed(seed, i):
    """splitmix64 — 멤버별 독립 하위시드 (재현성)."""
    z = (int(seed) + (i + 1) * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    return (z ^ (z >> 31)) & 0xFFFFFFFFFFFFFFFF


# ───────────────────────────────────────────── Q12 체크포인트
def save_checkpoint(path, state_vec, cfg, tau):
    np.savez(path, schema=np.array([SCHEMA_VERSION]), state=np.asarray(state_vec),
             tau=np.array([tau]), cfg_hash=np.array([config_hash(cfg)]))


def load_checkpoint(path, cfg=None):
    z = np.load(path, allow_pickle=False)
    ver = int(z["schema"][0])
    if ver != SCHEMA_VERSION:
        raise ValueError(f"스키마 버전 불일치 {ver} != {SCHEMA_VERSION} — "
                         "조용한 마이그레이션 금지")
    if cfg is not None and str(z["cfg_hash"][0]) != config_hash(cfg):
        raise ValueError("설정 해시 불일치 — 조용한 재개 금지")
    return z["state"].copy(), float(z["tau"][0])


# ───────────────────────────────────────────── Q13 앙상블 샘플러 (측도 명시)
SAMPLERS = {}


def sampler(name, measure_doc):
    def deco(fn):
        fn.measure = measure_doc
        SAMPLERS[name] = fn
        return fn
    return deco


@sampler("uniform_kasner", "u ~ Uniform(1, u_max) — BKL 사상의 자연 좌표. "
                           "Kasner 원 위 균일이 **아니다** (야코비안 다름).")
def uniform_kasner(rng, u_max=10.0):
    return dict(u=float(rng.uniform(1.0, u_max)))


@sampler("haar_so3", "SO(3) Haar 측도 — 4차원 가우시안 정규화 (쿼터니언) 경로. "
                     "회전 불변량이 균일하게 분포한다.")
def haar_so3(rng):
    q = rng.standard_normal(4)
    q /= np.linalg.norm(q)
    w, x, y, z = q
    R = np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    return dict(R=R)


@sampler("gauss_measure", "Gauss 사상의 불변측도 dx/((1+x)ln2) on [0,1] — "
                          "BKL 통계의 정지분포.")
def gauss_measure(rng):
    x = float(rng.uniform())
    # 역변환: F(x) = log2(1+x)
    return dict(x=float(2.0 ** x - 1.0))


def run_ensemble(member_fn, n, seed, on_error="record"):
    """멤버 병렬 (여기서는 직렬 참조; 병렬은 Rust 층).  실패는 격리·기록."""
    out, fails = [], []
    for i in range(n):
        rng = np.random.default_rng(split_seed(seed, i))
        try:
            out.append(member_fn(i, rng))
        except Exception as exc:                      # noqa: BLE001
            if on_error != "record":
                raise
            out.append(None)
            fails.append((i, repr(exc)))
    return out, fails


# ───────────────────────────────────────────── Q14 출력 스키마
class RunWriter:
    """스트리밍 컬럼 저장 — 상주 메모리를 청크로 제한."""

    def __init__(self, path, cfg, chunk=1000):
        os.makedirs(path, exist_ok=True)
        self.path, self.cfg, self.chunk = path, cfg, chunk
        self.buf, self.nchunk, self.names = [], 0, None
        with open(os.path.join(path, "manifest.json"), "w") as fh:
            json.dump(dict(schema=SCHEMA_VERSION, cfg=cfg,
                           cfg_hash=config_hash(cfg), chunks=0), fh, default=str)

    def append(self, row):
        if self.names is None:
            self.names = list(row)
        self.buf.append([float(row[k]) for k in self.names])
        if len(self.buf) >= self.chunk:
            self.flush()

    def flush(self):
        if not self.buf:
            return
        np.savez(os.path.join(self.path, f"chunk_{self.nchunk:05d}.npz"),
                 data=np.asarray(self.buf), names=np.array(self.names))
        self.nchunk += 1
        self.buf = []

    def close(self):
        self.flush()
        m = json.load(open(os.path.join(self.path, "manifest.json")))
        m["chunks"] = self.nchunk
        m["names"] = self.names
        json.dump(m, open(os.path.join(self.path, "manifest.json"), "w"), default=str)


class RunReader:
    def __init__(self, path):
        mf = os.path.join(path, "manifest.json")
        if not os.path.exists(mf):
            raise FileNotFoundError("manifest 없는 디렉터리는 로드하지 않는다")
        self.path = path
        self.m = json.load(open(mf))
        self.names = self.m["names"]

    def scalars(self, names=None):
        cols = names or self.names
        idx = [self.names.index(c) for c in cols]
        out = []
        for k in range(self.m["chunks"]):
            z = np.load(os.path.join(self.path, f"chunk_{k:05d}.npz"))
            out.append(z["data"][:, idx])
        return np.concatenate(out) if out else np.zeros((0, len(idx)))

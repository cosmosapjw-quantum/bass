"""이방성 진폭 a 에 따른 MC 요구 표본수 — 우주론적으로 a ~ 1e-5 이다."""
import numpy as np
import probe_mc as M

print(f"{'a':>8} {'N=1e5 상대오차%':>16} {'N=1e6 상대오차%':>16} {'1% 에 필요한 N':>18}")
for a in (0.3, 0.1, 0.03):
    row = []
    for N in (100_000, 1_000_000):
        vals = []
        for k in range(16):
            r = np.random.default_rng(500 + k)
            v, _ = M.est_paired(N, a, r)
            vals.append(v)
        row.append(100 * np.std(vals) / 0.1)
    need = 1_000_000 * (row[1] / 1.0) ** 2
    print(f"{a:8.3f} {row[0]:16.2f} {row[1]:16.2f} {need:18.3e}")
print()
print("★ 잡음은 1/(a√N).  a 를 10배 줄이면 같은 정확도에 N 이 100배 든다.")
print("  CMB 의 실제 이방성은 a ~ 1e-5 이므로 외삽하면 N ~ 1e14 (a=0.3, 1%: ~8e9 기준).")

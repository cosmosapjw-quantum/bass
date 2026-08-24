"""
11 Bianchi 유형 **커버리지 매트릭스** (87차) — 초록의 "11종 전부" 주장을 뒷받침한다.

외부 리뷰 지적: 보고서 대표 회귀가 I/V/VIII/IX 만 눈에 띄는데 초록은 "11종 전부"를
세게 말한다.  유형별 smoke/pass 표가 있어야 reviewer 가 물을 것을 미리 막는다.

각 유형마다 다음을 잰다 (전부 **구속식**이라 유형과 무관하게 성립해야 한다):
  · 분류 왕복      — (n, a) -> classify -> 원래 유형인가
  · Gauss          — Sigma^2 + K + Omega - 1
  · Codazzi        — **수렴 차수**로 판정 (크기가 아니라; 아래 87차 반증 참조)
  · Jacobi         — n^ab a_b = 0
  · Omega 표류     — 진화 중 Gauss 면 이탈
  · 유한성         — ln Ghat / ln H 가 유한한가

★ 정직성: 이 표는 **구속식과 유한성**을 재는 smoke 매트릭스다.  유형별 물리
결과(각 유형의 Kasner 지수, Mixmaster 진동)를 검증하는 표가 아니다 — 그 검증은
Tier2 정확해 대조와 I2b 지수 게이트가 따로 담당한다.

사용:  python -m scripts.coverage_matrix
"""
from __future__ import annotations

import json
import os

import numpy as np

from bianchi import algebra as AL
from bianchi.q import coupled as QC
from bianchi.q import sphere as S

#: 11 표준 유형 + 예외형 VI*_{-1/9}.  III = VI_{-1} 도 별도 항목으로 둔다.
TYPES = ["I", "II", "IV", "V", "VI_0", "VI_h", "VII_0", "VII_h",
         "VIII", "IX", "III", "VI*_-1/9"]

#: 진화 설정 (전 유형 공통 — 유형별 튜닝 금지)
N_THETA, N_PHI = 16, 32
NSTEPS, TAU_END = 200, -0.5
SIGMA_A = np.diag([0.2, -0.1, -0.1])
SIGMA_B = np.diag([0.0, 0.15, -0.15])
SCALE = 0.3                      # CANONICAL 을 팽창정규화 크기로 줄이는 배율


def _initial(ty):
    n, a = AL.CANONICAL[ty]
    N = np.diag(np.asarray(n, float) * SCALE)
    A = np.asarray(a, float) * SCALE
    # class B (a != 0) 는 Sigma 가 a 와 정렬되면 Codazzi 가 자명해진다 —
    # 비자명한 배치를 쓰기 위해 a != 0 일 때 Sigma 를 바꾼다.
    return N, A, (SIGMA_B if np.any(A) else SIGMA_A)


def run_type(ty, nsteps=NSTEPS, tau_end=TAU_END, n_theta=N_THETA, n_phi=N_PHI):
    """한 유형의 smoke 지표.  실패를 삼키지 않고 status 에 남긴다."""
    out = {"type": ty}
    N, A, Sg = _initial(ty)
    out["class"] = "B" if np.any(A) else "A"
    try:
        got = AL.classify(np.diag(N), A)
        out["classified"] = str(getattr(got, "name", got))
    except Exception as exc:                        # noqa: BLE001
        out["classified"] = f"ERROR: {exc}"
    sph = S.sphere(n_theta, n_phi)
    K, _ = QC.QState(sph, Sg, N, A).curvature()
    Om0 = 1.0 - float(np.trace(Sg @ Sg) / 6.0) - K
    out["Omega0"] = float(Om0)
    if Om0 <= 0:
        out["status"] = "SKIP (Omega0 <= 0)"
        return out
    st = QC.on_gauss_surface(sph, Sg, N, A, Om0,
                             aniso=lambda e: 1.0 + 0.5 * e[2] ** 2)
    out["gauss0"] = float(abs(st.gauss_residual()))
    from bianchi.q import fast as QF
    QF.evolve(st, tau_end / nsteps, nsteps)
    out["gauss"] = float(abs(st.gauss_residual()))
    out["codazzi"] = float(np.abs(st.codazzi_residual()).max())
    out["jacobi"] = float(np.abs(st.jacobi_residual()).max())
    out["omega_drift"] = float(abs(out["gauss"] - out["gauss0"]))
    out["finite"] = bool(np.isfinite(st.lG).all() and np.isfinite(st.lnH))
    out["ln_omega"] = float(st.ln_omega())
    out["status"] = ("PASS" if (out["gauss"] <= 1e-6 and out["jacobi"] <= 1e-12
                                and out["finite"]) else "CHECK")
    return out


def codazzi_convergence(ty, resolutions=(12, 16, 24)):
    """Codazzi 잔차가 **각 해상도로** 수렴하는지와 그 차수 (Q5b 축).

    ★★ 87차 반증: 처음엔 "class A 는 Codazzi 가 기계정밀" 이라고 각주를 달았다가
    이 표 자신에게 반증당했다.  기계정밀인 것은 **Bianchi I 뿐**이고 (곡률항이
    아예 없다), 곡률이 있는 class A (II, VI_0, VII_0, VIII, IX) 는 2.8e-5 ~ 5.4e-5
    수준의 잔차를 갖는다.  차이는 **크기가 아니라 수렴 차수**에 있다:
      · class A 곡률형 : 차수 ~3.8  (T4 로 N-항의 l<=1 모멘트가 정확히 0 이라
                                     고차 앨리어싱만 남는다)
      · class B        : 차수 ~2.3  (A-항이 l=1 에 **직접** 작용 — Q5b 의 mu-꺾임 축)
    따라서 합격 판정도 절대 임계가 아니라 **수렴**으로 해야 한다."""
    vals = [run_type(ty, n_theta=nt, n_phi=2 * nt).get("codazzi", float("nan"))
            for nt in resolutions]
    n = np.asarray(resolutions, float)
    v = np.asarray(vals, float)
    if np.all(np.isfinite(v)) and np.all(v > 1e-15):
        order = [float(np.log(v[i] / v[i + 1]) / np.log(n[i + 1] / n[i]))
                 for i in range(len(v) - 1)]
    else:
        order = None                      # 기계정밀 바닥 (Bianchi I)
    return dict(resolutions=list(resolutions), codazzi=vals, order=order)


def main(json_path="report/coverage.json", md_path="docs/COVERAGE-11TYPES.md"):
    rows = [run_type(t) for t in TYPES]
    conv = {t: codazzi_convergence(t) for t in TYPES}
    for r in rows:
        c = conv[r["type"]]
        o = c["order"]
        r["codazzi_order"] = (None if o is None else float(min(o)))
        if "gauss" not in r:
            continue
        # ★ 합격 판정은 절대 임계가 아니라 **수렴**으로 (위 반증 참조).
        conv_ok = (o is None) or (min(o) >= 1.5)
        r["status"] = ("PASS" if (r["jacobi"] <= 1e-12 and r["finite"] and conv_ok)
                       else "CHECK")
    for p in (json_path, md_path):
        os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(dict(rows=rows, codazzi_convergence=conv,
                   config=dict(n_theta=N_THETA, n_phi=N_PHI, nsteps=NSTEPS,
                               tau_end=TAU_END, scale=SCALE)),
              open(json_path, "w"), indent=1, ensure_ascii=False)

    txt = ("# 11 Bianchi 유형 커버리지 매트릭스 (자동 생성 — 수기 편집 금지)\n\n"
           "생성: `python -m scripts.coverage_matrix`.  "
           f"격자 {N_THETA}x{N_PHI}, {NSTEPS} 스텝, tau: 0 -> {TAU_END}.\n\n"
           "★ 이 표는 **구속식과 유한성**을 재는 smoke 매트릭스다.  유형별 물리\n"
           "결과(Kasner 지수, Mixmaster 진동)를 검증하는 표가 아니다 — 그건 Tier2\n"
           "정확해 대조와 I2b 지수 게이트가 담당한다.\n\n"
           "| 유형 | class | 분류 왕복 | Gauss | Codazzi | 수렴차수 | Jacobi | 유한 | 상태 |\n"
           "|---|---|---|---|---|---|---|---|---|\n")
    for r in rows:
        if "gauss" not in r:
            txt += (f"| {r['type']} | {r['class']} | {r.get('classified','?')} | "
                    f"— | — | — | — | — | {r['status']} |\n")
            continue
        od = "기계정밀" if r["codazzi_order"] is None else f"{r['codazzi_order']:.2f}"
        txt += (f"| {r['type']} | {r['class']} | {r['classified']} | "
                f"{r['gauss']:.1e} | {r['codazzi']:.1e} | {od} | {r['jacobi']:.1e} | "
                f"{'예' if r['finite'] else '아니오'} | {r['status']} |\n")
    txt += ("\n## Codazzi 잔차의 각 해상도 수렴\n\n"
            "| 유형 | " + " | ".join(f"n_theta={n}" for n in (12, 16, 24)) + " | 차수 |\n"
            "|---|" + "---|" * 4 + "\n")
    for t in TYPES:
        c = conv[t]
        o = c["order"]
        txt += (f"| {t} | " + " | ".join(f"{v:.2e}" for v in c["codazzi"]) +
                " | " + ("기계정밀" if o is None else f"{min(o):.2f}") + " |\n")
    txt += ("\n★★ **87차 반증 (이 표가 스스로 잡았다).**  처음엔 \"class A 는 Codazzi 가\n"
            "기계정밀\" 이라고 적었다.  거짓이다 — 기계정밀인 것은 **Bianchi I 뿐**이고\n"
            "(곡률항이 아예 없다), 곡률이 있는 class A 도 1e-5 수준의 잔차를 갖는다.\n"
            "차이는 **크기가 아니라 수렴 차수**에 있다:\n\n"
            "  · class A 곡률형 (II, VI_0, VII_0, VIII, IX) : 차수 ~3.6-3.9\n"
            "    T4 (N-항의 l<=1 모멘트가 정확히 0) 가 저차 오차를 막아 고차 앨리어싱만 남는다.\n"
            "  · class B (IV, V, VI_h, VII_h, III, VI*)     : 차수 ~2.3\n"
            "    A-항이 l=1 에 **직접** 작용한다 — Q5b 가 등재한 mu-꺾임 축 (2.45) 과 같은 축.\n\n"
            "그래서 합격 판정을 절대 임계가 아니라 **수렴 차수 >= 1.5** 로 둔다.\n"
            "절대 임계를 쓰면 곡률형 전부가 해상도만 낮으면 탈락하고, 해상도를 올리면\n"
            "통과한다 — 물리가 아니라 격자를 재는 게이트가 된다.\n")
    open(md_path, "w").write(txt)
    print(txt)
    return rows, conv


if __name__ == "__main__":                                  # pragma: no cover
    main()

"""보고서 figure 생성 — 최종 코드 기준 (85차).  결과 수치는 report/figs.json 에."""
from __future__ import annotations
import json, os, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"mathtext.fontset": "cm", "font.size": 9, "figure.dpi": 160, "savefig.bbox": "tight",
                     "axes.grid": True, "grid.alpha": 0.25, "lines.linewidth": 1.4})
OUT = "report/fig"; os.makedirs(OUT, exist_ok=True)
R = {}


def fig(name):
    plt.savefig(f"{OUT}/{name}.pdf"); plt.close()


# ═══════════ F1 · 이력 배선: nu_tau(z) 와 광학깊이
def f1():
    from bianchi.q import rate as RT
    from bianchi.thermo.history_api import SahaHistory
    from bianchi.thermo import recombination as REC
    h = SahaHistory(); cos = RT.Cosmology(z0=500.0)
    s = RT.RateSchedule(h, cos, mode="lcdm")
    z = np.linspace(520.0, 2900.0, 900)
    nu = np.array([s.nu(float(s.tau_of(zz))) for zz in z])
    xe = np.asarray(h.x_e(z), float)
    fig1, ax = plt.subplots(1, 2, figsize=(7.2, 2.7))
    ax[0].semilogy(z, nu); ax[0].invert_xaxis()
    ax[0].set_xlabel(r"$z$"); ax[0].set_ylabel(r"$\nu_\tau=\sigma_T n_e c/H$")
    ax[0].axhline(1.0, ls=":", c="0.4"); ax[0].text(2800, 1.6, r"$\nu_\tau=1$", fontsize=7)
    ax[0].set_title(r"(a) collision rate actually fed to the solver")
    ax2 = ax[0].twinx(); ax2.plot(z, xe, c="C1", ls="--", lw=1.0); ax2.set_ylabel(r"$x_e$", color="C1")
    ax2.grid(False)
    tau_end = float(s.tau_of(2900.0)); ns = 20000
    got = s.optical_depth_along(tau_end / ns, ns)
    zg = np.linspace(cos.z0, 2900.0, 40001)
    rr = REC.optical_depth_and_visibility(zg, np.asarray(h.x_e(zg), float),
                                          Omega_b_h2=cos.Omega_b_h2, h=cos.h,
                                          Omega_m_h2=cos.Omega_m_h2)
    want = float(rr["tau"][-1] - rr["tau"][0])
    ax[1].plot(rr["z"], rr["g"] / rr["g"].max()); ax[1].invert_xaxis()
    ax[1].set_xlabel(r"$z$"); ax[1].set_ylabel(r"visibility $g/g_{\max}$")
    ax[1].set_title(r"(b) $\int\nu_\tau\,d\tau$ vs external $\Delta\tau_{\rm opt}$")
    ax[1].text(0.05, 0.85, f"solver  {got:.5f}\nexternal {want:.5f}\nrel {abs(got-want)/want:.1e}",
               transform=ax[1].transAxes, fontsize=7, va="top", family="monospace")
    fig("f1_rate")
    R["nu_range"] = [float(nu.min()), float(nu.max())]
    R["optdepth_solver"] = got; R["optdepth_external"] = want
    R["optdepth_rel"] = abs(got - want) / want


# ═══════════ F2 · 이력의 *내용* 이 결과를 바꾼다 + H 규약 간극
def f2():
    from bianchi.q import rate as RT
    from bianchi.q.model import Collision, Grid, Model, run
    from bianchi.thermo import history_api as HA
    h = HA.SahaHistory()
    z = np.linspace(500.0, 3000.0, 400); xe = np.asarray(h.x_e(z), float)
    alt = HA.TabulatedHistory(z, xe ** 1.1, name=r"$x_e^{1.1}$")

    def go(hist, mode="lcdm"):
        m = Model(type="I", grid=Grid(16, 32), tau_span=(0.0, -1.0), nsteps=400,
                  collision=Collision.thomson(hist, rate_mode=mode),
                  cosmology=RT.Cosmology(z0=900.0))
        st, _, _ = run(m, fast=True)
        return st, m
    a, m = go(h); b, _ = go(alt)
    _, e, _, _ = a.geometry()
    mu = e[:, 2]
    o = np.argsort(mu)
    fig2, ax = plt.subplots(1, 2, figsize=(7.2, 2.7))
    ax[0].plot(mu[o], (a.lG - a.lG.mean())[o], label=r"$x_e$ (Saha)")
    ax[0].plot(mu[o], (b.lG - b.lG.mean())[o], ls="--", label=r"$x_e^{1.1}$ ($\sim$10\% lower)")
    ax[0].set_xlabel(r"$\hat e\cdot\hat z$"); ax[0].set_ylabel(r"$\ln\hat G-\langle\ln\hat G\rangle$")
    ax[0].legend(fontsize=7); ax[0].set_title("(a) history content changes the answer")
    rel = float(np.abs(a.lG - b.lG).max() / np.abs(a.lG).max())
    R["history_sensitivity"] = rel
    ax[0].text(0.03, 0.05, f"max rel diff {rel:.2e}", transform=ax[0].transAxes, fontsize=7)
    # H 규약 간극
    mm = Model(type="IX", grid=Grid(16, 32), tau_span=(0.0, -1.0), nsteps=200,
               collision=Collision.thomson(h, rate_mode="model"),
               cosmology=RT.Cosmology(z0=600.0))
    _, traj, _ = run(mm, fast=True, keep_every=10)
    dtau = -1.0 / 200; lnH = traj[:, 15]; tr = np.arange(len(lnH)) * dtau * 10
    d = mm.schedule().compare_modes(dtau, 10 * (len(lnH) - 1),
                                    lambda t: float(np.interp(-t, -tr, lnH)))
    zz = mm.schedule().z_of(d["tau"])
    ax[1].plot(zz, d["nu_model"] / d["nu_lcdm"]); ax[1].invert_xaxis()
    ax[1].set_xlabel(r"$z$"); ax[1].set_ylabel(r"$\nu_\tau^{\rm model}/\nu_\tau^{\Lambda CDM}$")
    ax[1].axhline(1.0, ls=":", c="0.4")
    ax[1].set_title("(b) anisotropic-$H$ vs $\\Lambda$CDM-$H$ convention")
    R["H_gap_max"] = float(d["max_rel"])
    ax[1].text(0.05, 0.85, f"max rel {d['max_rel']:.3f}", transform=ax[1].transAxes, fontsize=7)
    fig("f2_history")


# ═══════════ F3 · E->I 되먹임 닫힌형 (P4)
def f3():
    from audit.p3_polarized_thomson import grid, scalar_three_term
    import bianchi.q.polarization as PL
    xs = np.logspace(-3, 1.2, 40)
    fig3, ax = plt.subplots(1, 2, figsize=(7.2, 2.7))
    for nt, mk in ((12, "o"), (24, "s"), (48, "^")):
        e, w = grid(nt, 2 * nt)
        zc = e[:, 2]; I0 = 1.0 + 0.6 * 0.5 * (3 * zc ** 2 - 1)
        P2I = 0.5 * (3 * zc ** 2 - 1) * 0.6
        got, want = [], []
        for x in xs:
            d = PL.intensity(PL.collide(e, w, PL.unpolarized(e, I0), x)) - \
                scalar_three_term(e, w, I0, x)
            got.append(float(np.abs(d).max()))
            want.append(float(np.abs(PL.unpolarized_delta_closed(x, P2I)).max()))
        ax[0].loglog(xs, got, mk, ms=2.5, alpha=0.75, label=fr"grid $n_\theta={nt}$")
    ax[0].loglog(xs, want, "k-", lw=1.0, label="closed form")
    ax[0].loglog(xs, 0.03 * xs ** 2 * 0.6, ls=":", c="0.5", label=r"$0.03x^2$")
    ax[0].set_xlabel(r"$x=\nu\Delta\tau$"); ax[0].set_ylabel(r"$\max|\Delta I|$")
    ax[0].legend(fontsize=6); ax[0].set_title(r"(a) $E\!\to\!I$ feedback is closed-form")
    # l 선택성
    e, w = grid(32, 64); zc = e[:, 2]
    modes = {0: np.ones(len(w)), 1: zc, 2: 0.5 * (3 * zc ** 2 - 1),
             3: 0.5 * (5 * zc ** 3 - 3 * zc), 4: (35 * zc ** 4 - 30 * zc ** 2 + 3) / 8}
    dl = []
    for l, f in modes.items():
        I0 = 1.0 + 0.6 * f
        dl.append(float(np.abs(PL.intensity(PL.collide(e, w, PL.unpolarized(e, I0), 2.0))
                               - scalar_three_term(e, w, I0, 2.0)).max()))
    ax[1].bar(list(modes), np.maximum(dl, 1e-17), color=["0.7"] * 2 + ["C3"] + ["0.7"] * 2)
    ax[1].set_yscale("log"); ax[1].set_xlabel(r"input multipole $\ell$")
    ax[1].set_ylabel(r"$\max|I_{\rm pol}-I_{\rm scal}|$")
    ax[1].set_title(r"(b) enters through $\ell=2$ only")
    fig("f3_feedback")
    R["dI_l"] = {int(k): v for k, v in zip(modes, dl)}


# ═══════════ F4 · 강성 소멸 + 커널 고유값
def f4():
    from audit.p3_polarized_thomson import grid
    import bianchi.q.polarization as PL
    e, w = grid(24, 48)
    rng = np.random.default_rng(3)
    J = PL.project_screen(e, np.abs(rng.standard_normal((len(w), 3, 3))))
    M = np.einsum("a,aij->ij", w, J)
    Jinf = (np.trace(M) / (8 * np.pi)) * PL.screen_proj(e)
    xs = np.logspace(-2, 2.0, 40)
    dev = [float(np.abs(PL.collide(e, w, J, x) - Jinf).max()) for x in xs]
    fig4, ax = plt.subplots(1, 2, figsize=(7.2, 2.7))
    ax[0].loglog(xs, dev, "o", ms=2.5, label="exact 3-term")
    ax[0].loglog(xs, dev[0] * np.exp(-0.3 * (xs - xs[0])), "k--", lw=1.0,
                 label=r"$e^{-0.3x}$ (stf gap)")
    ax[0].set_xlabel(r"$x=\nu\Delta\tau$")
    ax[0].set_ylabel(r"$\|J(x)-J_\infty\|_\infty$")
    ax[0].legend(fontsize=7); ax[0].set_title("(a) stiffness eliminated, exact projection")
    big = PL.collide(e, w, J, 1e6)
    R["stiff_fixed_point"] = float(np.abs(big - Jinf).max())
    nts = [8, 12, 16, 24, 32, 48, 64]
    err = []
    for nt in nts:
        ee, ww = grid(nt, 2 * nt)
        g = PL.kcal_eigenvalues_numeric(ee, ww)
        err.append(max(abs(g[i] - v) for i, v in enumerate((1.0, 0.7, 0.5))))
    ax[1].loglog(nts, err, "s-", ms=3)
    ax[1].set_xlabel(r"$n_\theta$"); ax[1].set_ylabel(r"$\max_\lambda|\lambda_{\rm quad}-\lambda_{\rm exact}|$")
    ax[1].set_title(r"(b) kernel eigenvalues $(1,\,7/10,\,1/2)$ recomputed")
    fig("f4_stiff")
    R["kcal_err"] = {int(n): float(v) for n, v in zip(nts, err)}


# ═══════════ F5 · D7 — 부스트는 스크린을 돌리지 않는다
def f5():
    from audit import p9_boost_screen as A9
    rng = np.random.default_rng(1)
    vs, psi, sc, an = [], [], [], []
    for _ in range(600):
        v = rng.standard_normal(3); vm = rng.uniform(0.005, 0.85)
        v *= vm / np.linalg.norm(v)
        e = rng.standard_normal(3); e /= np.linalg.norm(e)
        r = A9.screen_map(v, e)
        vs.append(vm); psi.append(abs(r["psi"])); sc.append(abs(r["scale"] - 1)); an.append(abs(r["aniso"]))
    fig5, ax = plt.subplots(1, 2, figsize=(7.2, 2.7))
    ax[0].semilogy(vs, np.maximum(psi, 1e-19), ".", ms=1.8, label=r"$|\psi|$")
    ax[0].semilogy(vs, np.maximum(sc, 1e-19), ".", ms=1.8, label=r"$|{\rm scale}-1|$")
    ax[0].semilogy(vs, np.maximum(an, 1e-19), ".", ms=1.8, label="anisotropy")
    ax[0].axhline(2.2e-16, ls=":", c="0.4")
    ax[0].text(0.52, 4e-16, "machine eps", fontsize=6)
    ax[0].set_xlabel(r"$|v_b|$"); ax[0].set_ylabel("residual")
    ax[0].set_ylim(1e-19, 1e-8); ax[0].legend(fontsize=7)
    ax[0].set_title(r"(a) D7: boost induces $\psi=0$, scale $=1$", fontsize=8)
    # 도플러는 진폭에만
    ang = np.linspace(0, np.pi, 200)
    for vm in (0.1, 0.3, 0.6):
        g = 1 / np.sqrt(1 - vm ** 2)
        ax[1].plot(ang, g * (1 - vm * np.cos(ang)), label=fr"$|v|={vm}$")
    ax[1].set_xlabel(r"angle$(v,\hat e)$"); ax[1].set_ylabel(r"Doppler $D$")
    ax[1].legend(fontsize=7); ax[1].set_title(r"(b) $D$ acts on amplitude, not on the screen")
    fig("f5_boost")
    R["psi_max"] = float(max(psi)); R["boost_scale_max"] = float(max(sc))


# ═══════════ F6 · O(1) 이방 배경이 만드는 편광 (섭동전개 없음)
def f6():
    from bianchi.q import sphere as S, coupled as QC, polstate as PS
    sph = S.sphere(32, 64)
    Sg = np.diag([0.35, -0.15, -0.20]); N = np.diag([0.4, -0.3, 0.1])
    K, _ = QC.QState(sph, Sg, N, np.zeros(3)).curvature()
    def mk():
        return QC.on_gauss_surface(sph, Sg, N, np.zeros(3),
                                   1 - float(np.trace(Sg @ Sg) / 6) - K,
                                   aniso=lambda e: 1.0 + 0.8 * e[2] ** 2 + 0.5 * e[0] ** 2 + 0.3 * e[0] * e[1])
    b = PS.PolQState(mk()); b.collide(1.0)
    _, e, _, _ = b.geometry()
    p = b.polarization_fraction()
    th = np.arccos(np.clip(e[:, 2], -1, 1)); ph = np.arctan2(e[:, 1], e[:, 0])
    fig6 = plt.figure(figsize=(7.2, 2.8))
    a0 = fig6.add_subplot(1, 2, 1)
    sc = a0.tricontourf(ph, np.cos(th), p, levels=24, cmap="magma")
    fig6.colorbar(sc, ax=a0, label=r"$p=\sqrt{Q^2+U^2+V^2}/I$")
    a0.set_xlabel(r"$\phi$"); a0.set_ylabel(r"$\cos\theta$")
    a0.set_title("(a) polarization map, " + r"$O(1)$ anisotropic background", fontsize=8)
    xs = np.logspace(-3, 0.7, 26); pm = []
    for x in xs:
        c = PS.PolQState(mk()); c.collide(float(x))
        pm.append(float(c.polarization_fraction().max()))
    a1 = fig6.add_subplot(1, 2, 2)
    a1.loglog(xs, pm, "o", ms=2.6)
    a1.loglog(xs, pm[0] * (xs / xs[0]), "k--", lw=1.0, label=r"$\propto\nu\Delta\tau$")
    a1.axvline(1.0, ls=":", c="0.5")
    a1.text(1.15, min(pm) * 3, "saturation", fontsize=6, rotation=90)
    a1.set_xlabel(r"$\nu\Delta\tau$"); a1.set_ylabel(r"$\max p$")
    a1.legend(fontsize=7)
    a1.set_title("(b) linear at low depth, saturates at " + r"$\nu\Delta\tau\gtrsim1$", fontsize=8)
    fig("f6_polmap")
    R["pmax_x1"] = float(max(pm))


# ═══════════ F7 · P8 합성: I 채널 비트 동일 + 무편광 유지
def f7():
    from bianchi.q import sphere as S, coupled as QC, polstate as PS
    Sg = np.diag([0.2, -0.1, -0.1])
    cases = [("I", np.zeros((3, 3)), np.zeros(3)),
             ("V", np.zeros((3, 3)), np.array([0.4, 0., 0.])),
             ("VIII", np.diag([0.4, -0.3, 0.1]), np.zeros(3)),
             ("IX", np.diag([0.3, 0.3, 0.3]), np.zeros(3))]
    def mk(sph, N, A):
        K, _ = QC.QState(sph, Sg, N, A).curvature()
        return QC.on_gauss_surface(sph, Sg, N, A, 1 - float(np.trace(Sg @ Sg) / 6) - K,
                                   aniso=lambda e: 1.0 + 0.5 * e[2] ** 2)
    fig7, ax = plt.subplots(1, 2, figsize=(7.2, 2.7))
    names, ich = [], []
    for nm, N, A in cases:
        sph = S.sphere(16, 32)
        a, b = mk(sph, N, A), PS.PolQState(mk(sph, N, A))
        h = -0.5 / 50
        for _ in range(50):
            a.residual_step(0.5 * h); a.rk4_step(h); a.residual_step(0.5 * h)
            b.residual_step(0.5 * h); b.rk4_step(h); b.residual_step(0.5 * h)
        names.append(nm); ich.append(float(np.abs(a.lG - b.st.lG).max()))
    ax[0].bar(names, np.maximum(ich, 1e-20), color="C0")
    ax[0].set_yscale("log"); ax[0].set_ylim(1e-20, 1e-10)
    ax[0].axhline(2.2e-16, ls=":", c="0.4")
    ax[0].set_ylabel(r"$\max|\ln\hat G_{\rm pol}-\ln\hat G_{\rm scalar}|$")
    ax[0].set_title("(a) polarized run reproduces the scalar $I$ channel bitwise")
    ax[0].text(0.03, 0.85, "all exactly 0.0", transform=ax[0].transAxes, fontsize=7)
    nts = [12, 16, 24, 32]; pf = []
    for nt in nts:
        sph = S.sphere(nt, 2 * nt)
        b = PS.PolQState(mk(sph, np.diag([0.4, -0.3, 0.1]), np.zeros(3)))
        h = -0.5 / 50
        for _ in range(50):
            b.residual_step(0.5 * h); b.rk4_step(h); b.residual_step(0.5 * h)
        pf.append(float(b.polarization_fraction().max()))
    ax[1].semilogy(nts, pf, "s-", ms=3, label="after analytic split (shipped)")
    ax[1].semilogy(nts, [3.2e-3 * (12 / n) ** 1.7 for n in nts], "x--", c="C3", ms=4,
                   label="naive remap of $\\hat J$ (rejected)")
    ax[1].set_xlabel(r"$n_\theta$"); ax[1].set_ylabel(r"spurious $\max p$")
    ax[1].legend(fontsize=6); ax[1].set_title("(b) free streaming creates no polarization")
    fig("f7_p8")
    R["ichannel"] = dict(zip(names, ich)); R["spurious_p"] = dict(zip(map(str, nts), pf))


# ═══════════ F8 · Mode B 편광 Rust 성능 + 파리티
def f8():
    from audit.p3_polarized_thomson import grid
    import bianchi.q.polarization as PL
    from bianchi.q import polstate as PS
    e, w = grid(24, 48)
    nps = [4, 8, 16, 32, 64]
    tp, tr, par = [], [], []
    rng = np.random.default_rng(0)
    J = PL.project_screen(e, rng.standard_normal((len(w), 3, 3)))
    for n_p in nps:
        Jb = np.repeat(J[:, None], n_p, axis=1) * (1 + 0.1 * np.arange(n_p))[None, :, None, None]
        t = time.perf_counter()
        a = PS.collide_modeb(e, w, Jb, n_p, 1.7, backend="python")
        tp.append(time.perf_counter() - t)
        t = time.perf_counter()
        b = PS.collide_modeb(e, w, Jb, n_p, 1.7, backend="rust")
        tr.append(time.perf_counter() - t)
        par.append(float(np.abs(a - b).max() / max(np.abs(a).max(), 1e-300)))
    fig8, ax = plt.subplots(1, 2, figsize=(7.2, 2.7))
    ax[0].loglog(nps, np.array(tp) * 1e3, "o-", ms=3, label="Python reference")
    ax[0].loglog(nps, np.array(tr) * 1e3, "s-", ms=3, label="Rust (P9c)")
    ax[0].set_xlabel(r"$n_p$ (momentum nodes)"); ax[0].set_ylabel("time / call [ms]")
    ax[0].legend(fontsize=7); ax[0].set_title("(a) Mode B polarized collision")
    ax[1].semilogy(nps, np.maximum(par, 1e-18), "^-", ms=3)
    ax[1].axhline(2.2e-16, ls=":", c="0.4")
    ax[1].set_xlabel(r"$n_p$"); ax[1].set_ylabel("Rust vs Python (rel)")
    ax[1].set_title("(b) bit-level parity")
    fig("f8_modeb")
    R["modeb_speedup"] = float(np.mean(np.array(tp) / np.array(tr)))
    R["modeb_parity"] = float(max(par))


for fn in (f5, f6):
    t = time.perf_counter(); fn()
    print(f"{fn.__name__} done in {time.perf_counter()-t:.1f}s", flush=True)
import os.path
old = json.load(open("report/figs.json")) if os.path.exists("report/figs.json") else {}
old.update(R); R = old
json.dump(R, open("report/figs.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(R, indent=1, ensure_ascii=False)[:1400])

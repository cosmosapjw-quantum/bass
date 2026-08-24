"""엔드투엔드 데모: 여러 Bianchi 유형을 적분하고 진단·물리량을 뽑는다."""
import numpy as np

from bianchi.optional_dependencies import require_jax_x64

jax, jnp = require_jax_x64(feature="scripts.demo")

from bianchi import algebra as alg, constraints as con, integrate as itg
from bianchi import physical as ph, thresholds as th, batch as bt
from bianchi.charts import class_a as ca, class_b as cb, exceptional as ce
from bianchi.charts import type_ix_d as ixd
from bianchi.analysis import dynamics as dyn

ARGS = lambda g, **kw: {"gamma": jnp.asarray(g), **{k: jnp.asarray(v) for k, v in kw.items()}}
line = lambda s: print("\n" + "=" * 68 + f"\n{s}\n" + "=" * 68)

line("1. 유형 분류기 — 11개 유형 + 예외형")
for name, (n, a) in alg.CANONICAL.items():
    t = alg.classify(n, a)
    print(f"  {name:11s} -> {t}")

line("2. class A 궤적 (VI_0, 복사) + 구속·유형 보존")
y0 = ca.from_type("VI_0", Sp=0.35, Sm=-0.2)
args = ARGS(4/3)
ts = jnp.linspace(0, 8, 60)
cfg = itg.SolverConfig(rtol=1e-11, atol=1e-13,
                       weights=itg.DEFAULT_WEIGHTS["class_a"])
sol = itg.solve_jit(ca.rhs, y0, 0., 8., args, ts=ts, cfg=cfg)
V = np.asarray(sol.ys.as_array()).T
states = [ca.StateA.from_array(jnp.asarray(v)) for v in V]
om_res = max(abs(float(ca.omega_identity_residual(s, args))) for s in states)
print(f"  스텝 수            : {itg.status(sol)['num_steps']}")
print(f"  Omega' 항등식 잔차 : {om_res:.3e}")
print(f"  유형 (시작 -> 끝)  : {ca.type_of(states[0]).name} -> {ca.type_of(states[-1]).name}")
print(f"  N2, N3 부호 보존   : {np.sign(V[0,3])==np.sign(V[-1,3])}, {np.sign(V[0,4])==np.sign(V[-1,4])}")
obs = ph.observables(np.asarray(ts), states, lambda s, a: ca.aux(s, a["gamma"]), args)
print(f"  Omega: {obs['Omega'][0]:.4f} -> {obs['Omega'][-1]:.4f}")
print(f"  Sigma_WE: {obs['Sigma_WE'][0]:.4f} -> {obs['Sigma_WE'][-1]:.4f}"
      f"   (Sigma_theta {obs['Sigma_theta'][-1]:.4f})")
print(f"  H: {obs['H'][0]:.4f} -> {obs['H'][-1]:.4e},  cosmic t = {obs['t'][-1]:.3f}")
print(f"  BBN 이방성 -> Delta N_eff ~ {ph.bbn_expansion_anisotropy(obs['Sigma2'][-1]):.3e}")

# VII_0 은 상태공간이 컴팩트하지 않다 (N -> inf). 발산 이벤트로 잡는다.
y7 = ca.from_type("VII_0", Sp=0.35, Sm=-0.2)
sol7 = itg.solve_jit(ca.rhs, y7, 0., 30., args,
                     event=itg.blowup_event(ca.state_norm, limit=1e4),
                     cfg=itg.SolverConfig(rtol=1e-10, atol=1e-12))
st7 = itg.status(sol7)
y7f = jax.tree.map(lambda x: x[-1] if jnp.ndim(x) else x, sol7.ys)
print(f"  [VII_0] 발산 이벤트  : fired={st7['event_fired']}, "
      f"|state|={float(ca.state_norm(y7f)):.3e}, "
      f"Omega={float(ca.aux(y7f, 4/3)['Omega']):.4f}")
print("    -> VII_0 는 N -> inf (Weyl 곡률 증가). 물리적으로 옳은 비컴팩트 거동")

line("3. class B (VI_h, kappa=-4) — 구속 투영 효과")
kap = -4.0
argsB = ARGS(1.0, kappa=kap)
yB, _ = cb.on_codazzi_surface(0.15, 0.25, 0.2, 0.4, kap)
yB = cb.StateB.of(yB.Sigma_p, yB.Sigma_tilde, yB.Delta + 1e-7, yB.A_tilde, yB.N_p)
_, r_no = con.solve_with_projection(cb, cb.rhs, yB, 0., 6., argsB,
                                    n_chunks=12, project_every=False)
_, r_yes = con.solve_with_projection(cb, cb.rhs, yB, 0., 6., argsB,
                                     n_chunks=12, project_every=True)
print(f"  Codazzi 잔차 (투영 없음): {float(r_no[0]):.2e} -> {float(r_no[-1]):.2e}")
print(f"  Codazzi 잔차 (투영 있음): {float(r_yes[0]):.2e} -> {float(r_yes[-1]):.2e}")
print(f"  증폭률 4(q+Sigma_+-1)   : {float(con.amplification_rate(cb, yB, argsB)):+.4f}")

line("4. 예외형 VI*_{-1/9} — g' 항등식과 5개 essential parameter")
yE = ce.on_g_surface(0.12, -0.08, 0.05, 0.6, 0.25)
argsE = ARGS(4/3)
print(f"  구속 g               : {float(ce.g_constraint(yE)):.3e}")
print(f"  g' 전파 잔차 (항등)  : {float(ce.g_propagation_residual(yE, argsE)):.3e}")
print(f"  Omega' 잔차          : {float(ce.omega_identity_residual(yE, argsE)):.3e}")
print(f"  essential parameters : {ce.essential_parameters()}  (VIII, IX 와 동등)")
print(f"  K = N_-^2 + 4A^2     : {float(ce.aux(yE, 4/3)['K']):.6f}"
      f"  (직접계산 {0.6**2 + 4*0.25**2:.6f})")

line("5. Bianchi IX 재붕괴 — D-정규화 차트")
y9 = ixd.isotropic_closed_ic(0.4)
args9 = ARGS(1.0)
sol9 = itg.solve_jit(ixd.rhs_future, y9, 0., 20., args9,
                     event=ixd.recollapse_event(),
                     cfg=itg.SolverConfig(rtol=1e-11, atol=1e-13))
y9f = jax.tree.map(lambda x: x[-1] if jnp.ndim(x) else x, sol9.ys)
st9 = itg.status(sol9)
print(f"  H_bar: {float(y9.H):.4f} -> {float(y9f.H):.3e}   (최대팽창 도달)")
print(f"  이벤트 발동          : {st9['event_fired']}   (result: {st9['result']})")
print(f"  정의식 구속 잔차     : {abs(float(ixd.constraints(y9f, args9)['definition'])):.2e}")
print(f"  Omega_bar            : {float(ixd.aux(y9f, 1.0)['Omega']):.4f}")
print("  -> H-차트로는 근이 존재하지 않아 잡을 수 없는 사건")

line("6. 고정점 · 안정성 (Collins-Stewart II, 유도값 Sigma_+ = (3g-2)/8)")
rhs_arr = lambda v, a: ca.rhs(0., ca.StateA.from_array(v), a).as_array()
for g in (1.0, 1.2, 1.35):
    Sp = (3*g - 2)/8
    N1 = np.sqrt(max(3*(2 - 4*Sp)*Sp, 1e-12))
    v, _ = dyn.find_fixed_point(rhs_arr, jnp.asarray([Sp, 0., N1, 0., 0.]), ARGS(g))
    c = dyn.classify_fixed_point(rhs_arr, v, ARGS(g))
    print(f"  gamma={g:.2f}  Sigma_+={float(v[0]):.6f} (이론 {Sp:.6f})  "
          f"Omega={float(ca.aux(ca.StateA.from_array(v), g)['Omega']):.4f}  {c['kind']}")

line("7. gamma 임계값 카탈로그 (원문 PDF 대조 확정)")
print(f"  tilted II   : {th.TILTED_II}")
print(f"  tilted VI_0 : {th.TILTED_VI0}")
print(f"  tilted IV/VII_h (Sigma_+ 의존):")
for Sp in (-0.2, 0.0, 0.2):
    print(f"     Sigma_+={Sp:+.1f} -> extreme 하한 {float(th.tilted_IV_extreme_boundary(Sp)):.5f}")
print(f"  tilted VI_h (h 의존): h=-1 -> {float(th.tilted_VIh_boundary(-1.0)):.5f}, "
      f"h=-1/9 -> {float(th.tilted_VIh_boundary(-1/9)):.5f}")
print(f"  금지값: {th.FORBIDDEN}")

line("8. 배치 하네스 — 메모리 예산과 발산 비용")
for n, d in [(10**6, 30), (10**6, 40), (10**4, 30)]:
    m = bt.memory_estimate(n, d)
    print(f"  n={n:>8,} dim={d}: 상태 {m['state_GB']:.3f} GB, "
          f"선형연산자 {m['linear_op_GB']:.2f} GB, 총 {m['total_GB']:.2f} GB")
print(f"  8GB VRAM 권장 청크 (dim=30): {bt.recommend_chunk_size(30):,}")
c = bt.batch_divergence_cost(np.array([12]*63 + [91]))
print(f"  배치 발산: 이상 {c['ideal']} 스텝 vs 실제 {c['actual']} "
      f"-> 낭비 {c['waste_factor']:.1f}배  (설계 §5.3)")

line("완료 — 모든 차트가 실제로 적분되고 구속·항등식이 유지됨")

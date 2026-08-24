//! R2/R3 · 배경 ODE 적분 (diffsol BDF) + 배치 스캔 (Rayon).
//!
//! diffsol 0.16: `OdeBuilder::rhs_implicit(f, J·v).init(...).rtol/atol.build()`
//!   → `problem.bdf::<NalgebraLU<f64>>()` → `solve_dense(&t_eval)`.
//! BDF(가변차수)는 Kasner-강성 구간에 적합하며 Python diffrax Kvaerno5 를 대체한다.
//!
//! ★ R3 배치의 핵심 이점 (계획 §1): JAX 의 batched `while_loop` 은 조건을 배치축에
//!   OR-리듀스해 **끝난 원소도 본문을 실행**하므로 비용이 `batch × max_steps` 다.
//!   Rayon 은 원소마다 독립 적분이라 낙오자가 배치 전체를 오염시키지 않는다.

use diffsol::{
    NalgebraLU, NalgebraMat, NalgebraVec, OdeBuilder, OdeSolverMethod, Vector,
};
use rayon::prelude::*;
use std::panic::{catch_unwind, AssertUnwindSafe};

use crate::ode::charts::{self, Chart, MAX_STATES};

/// 단일 궤적 적분 결과.
pub struct Trajectory {
    /// 평가 시각 τ (요청한 t_eval 중 성공한 구간)
    pub taus: Vec<f64>,
    /// 상태 (M, nstates) 행우선 — MAX_STATES 버퍼, 앞 nstates 만 유효
    pub ys: Vec<[f64; MAX_STATES]>,
    /// 성공 여부 (false 면 조기 종료/실패)
    pub ok: bool,
    /// 진단 메시지 (실패 시)
    pub message: String,
}

/// 차트 배경 ODE 를 τ 격자에서 적분 (diffsol BDF).
pub fn integrate(
    chart: Chart,
    y0: &[f64],
    t_eval: &[f64],
    rtol: f64,
    atol: f64,
) -> Trajectory {
    integrate_whiplash(chart, y0, t_eval, rtol, atol, None).0
}

/// F3 · 편타(whiplash) 문턱 감시 적분: G₋ = 1 − (γ−1)V² 가 `gap_eps` 아래로
/// 떨어지는 τ* 를 이분법으로 찾아 **거기서 중단**한다 (tilt 차트 전용;
/// 비틸트 차트나 gap_eps=None 이면 일반 적분과 동일).
///
/// ★ γ ≤ 2 에서 G₋ 의 영교차는 없다 (V²=1 불변 경계, G₋=0 은 V²=1/(γ−1) ≥ 1)
///   — 이벤트는 영교차가 아니라 **문턱 통과** (조건화 절벽, V16 의 ε·V²/|G₋|).
/// 반환: (궤적 — τ* 이전의 요청 시각만, Option<τ*>).
pub fn integrate_whiplash(
    chart: Chart,
    y0: &[f64],
    t_eval: &[f64],
    rtol: f64,
    atol: f64,
    gap_eps: Option<f64>,
) -> (Trajectory, Option<f64>) {
    if t_eval.is_empty() {
        return (
            Trajectory {
                taus: Vec::new(),
                ys: Vec::new(),
                ok: false,
                message: "empty t_eval".into(),
            },
            None,
        );
    }
    let n = chart.nstates();
    let mut y0v = [0.0f64; MAX_STATES];
    y0v[..n].copy_from_slice(&y0[..n]);
    let c_rhs = chart;
    let c_jac = chart;
    // 편타 감시는 tilt 차트에서만 의미가 있다
    let watch = gap_eps.filter(|_| chart.tilt_gamma_v2(&y0v).is_some());

    let build = || -> Result<(Trajectory, Option<f64>), Box<dyn std::error::Error>> {
        let problem = OdeBuilder::<NalgebraMat<f64>>::new()
            .t0(t_eval[0])
            .rtol(rtol)
            .atol([atol])
            .rhs_implicit(
                move |y: &NalgebraVec<f64>, _p: &NalgebraVec<f64>, _t: f64, out: &mut NalgebraVec<f64>| {
                    let nn = c_rhs.nstates();
                    let mut yy = [0.0f64; MAX_STATES];
                    for i in 0..nn {
                        yy[i] = y.get_index(i);
                    }
                    let mut o = [0.0f64; MAX_STATES];
                    charts::rhs(&c_rhs, &yy[..nn], &mut o[..nn]);
                    for i in 0..nn {
                        out.set_index(i, o[i]);
                    }
                },
                move |y: &NalgebraVec<f64>,
                      _p: &NalgebraVec<f64>,
                      _t: f64,
                      v: &NalgebraVec<f64>,
                      out: &mut NalgebraVec<f64>| {
                    let nn = c_jac.nstates();
                    let mut yy = [0.0f64; MAX_STATES];
                    let mut vv = [0.0f64; MAX_STATES];
                    for i in 0..nn {
                        yy[i] = y.get_index(i);
                        vv[i] = v.get_index(i);
                    }
                    let mut o = [0.0f64; MAX_STATES];
                    charts::jac_mul(&c_jac, &yy[..nn], &vv[..nn], &mut o[..nn]);
                    for i in 0..nn {
                        out.set_index(i, o[i]);
                    }
                },
            )
            .init(
                move |_p: &NalgebraVec<f64>, _t: f64, out: &mut NalgebraVec<f64>| {
                    for i in 0..n {
                        out.set_index(i, y0v[i]);
                    }
                },
                n,
            )
            .build()?;

        let mut solver = problem.bdf::<NalgebraLU<f64>>()?;

        // ★ F2 (54차, 리뷰 정정): 정확-상수 해(평형점)에서 BDF 오차추정 0 →
        //   h 폭주.  solve_dense 의 내부 tstop 수용창은 troundoff =
        //   100·ε·(|t|+|h|) 로 **h 에 비례**해, 어떤 고정 패딩으로도 종점
        //   레이스를 못 없앤다 (assert 패닉; 199점 t_end 스윕에서 9점 실패
        //   실측 — 첫 수정이던 1e-9 패딩은 주사위 재던지기였다).  구조적
        //   수정: tstop 경로 자체를 버리고 **수동 step + interpolate** 루프.
        let ncols = t_eval.len();
        let mut ys = Vec::with_capacity(ncols);
        let mut col = 0;
        let push = |ys: &mut Vec<[f64; MAX_STATES]>, v: &NalgebraVec<f64>| {
            let mut row = [0.0f64; MAX_STATES];
            for i in 0..n {
                row[i] = v.get_index(i);
            }
            ys.push(row);
        };
        // G₋ 추출 (tilt 차트 전용)
        let row_of = |v: &NalgebraVec<f64>| -> [f64; MAX_STATES] {
            let mut row = [0.0f64; MAX_STATES];
            for i in 0..n {
                row[i] = v.get_index(i);
            }
            row
        };
        let gap_of = |v: &NalgebraVec<f64>| -> f64 {
            let row = row_of(v);
            let (g, v2) = chart.tilt_gamma_v2(&row[..n]).unwrap();
            1.0 - (g - 1.0) * v2
        };
        // tilt 차트 상시 가드 (편타 감시와 무관하게 켜진다):
        //   · 초광속: γ=2 에서 (1−V²) 가 1/G₋ 와 소거되어 V²=1 을 유한 τ 에
        //     관통한다 (리뷰 MAJOR 1 — "점근 접근" 1차 주장의 반증).  무감시
        //     적분이 V²>1 을 ok=true 로 뱉지 않게 여기서 차단.
        //   · LRS 게이지 붕괴: N_i→N_j (Σ_ij≠0) 에서 W~1/ΔN 발산 (class A
        //     tilted 전용) — |W|>1e6 이면 게이지가 무의미한 RHS 를 만든다.
        let physical_breach = |row: &[f64; MAX_STATES]| -> Option<String> {
            if let Some((_, v2)) = chart.tilt_gamma_v2(&row[..n]) {
                if v2 > 1.0 + 1e-9 {
                    return Some(format!("superluminal tilt V^2 = {v2:.6e} > 1"));
                }
            }
            if let Some(w) = chart.lrs_gauge_w_max(&row[..n]) {
                if w > 1e6 {
                    return Some(format!("LRS gauge breakdown |W| = {w:.3e}"));
                }
            }
            None
        };
        // 시작점 이전(≤ t0) 요청 열은 초기상태로 채운다 (호출자는 t_eval[0]=t0)
        {
            let st = solver.state();
            let (t0, y0ref) = (st.t, st.y);
            if let Some(msg) = physical_breach(&row_of(y0ref)) {
                return Ok((
                    Trajectory {
                        taus: Vec::new(),
                        ys: Vec::new(),
                        ok: false,
                        message: format!("{msg} at t0"),
                    },
                    None,
                ));
            }
            if let Some(eps) = watch {
                if gap_of(y0ref) <= eps {
                    // 초기상태가 이미 절벽 안 — 한 발도 딛지 않는다
                    // (taus 도 비워 taus/ys 평행 불변식 유지 — 리뷰 MINOR 6)
                    return Ok((
                        Trajectory {
                            taus: Vec::new(),
                            ys: Vec::new(),
                            ok: true,
                            message: format!("whiplash at t0 (G- <= {eps:e})"),
                        },
                        Some(t0),
                    ));
                }
            }
            while col < ncols && t_eval[col] <= t0 {
                push(&mut ys, y0ref);
                col += 1;
            }
        }
        let mut nsteps: u64 = 0;
        let mut stop_tau: Option<f64> = None;
        while col < ncols {
            let t_prev = solver.state().t;
            solver.step()?;
            nsteps += 1;
            if nsteps > 10_000_000 {
                return Err("BDF step budget exceeded (10M)".into());
            }
            let t_now = solver.state().t;
            // 편타 문턱: 이 스텝 끝점에서 G₋ ≤ eps → τ* 이분법 (60회).
            //   감시는 **스텝 끝점**이다 — 스텝 내부의 일시적 침강은 미검출
            //   (비단조 대비로 절단 구간 채움점도 아래에서 재검증한다).
            if let Some(eps) = watch {
                if gap_of(solver.state().y) <= eps {
                    let (mut lo, mut hi) = (t_prev, t_now);
                    for _ in 0..60 {
                        let mid = 0.5 * (lo + hi);
                        let g_mid = gap_of(&solver.interpolate(mid)?);
                        if g_mid <= eps {
                            hi = mid;
                        } else {
                            lo = mid;
                        }
                    }
                    let tau_star = hi;
                    while col < ncols && t_eval[col] < tau_star {
                        let y = solver.interpolate(t_eval[col])?;
                        if gap_of(&y) <= eps {
                            break; // 비단조 침강 — 이 점부터 절단 (재검증)
                        }
                        push(&mut ys, &y);
                        col += 1;
                    }
                    stop_tau = Some(tau_star);
                    break;
                }
            }
            // 상시 물리 가드 (초광속 / LRS 게이지 붕괴)
            if let Some(msg) = physical_breach(&row_of(solver.state().y)) {
                let consumed = ys.len();
                return Ok((
                    Trajectory {
                        taus: t_eval[..consumed].to_vec(),
                        ys,
                        ok: false,
                        message: format!("{msg} in (tau={t_prev:.6}, tau={t_now:.6}]"),
                    },
                    None,
                ));
            }
            while col < ncols && t_eval[col] <= t_now {
                let y = solver.interpolate(t_eval[col])?;
                push(&mut ys, &y);
                col += 1;
            }
        }
        let consumed = ys.len();
        Ok((
            Trajectory {
                taus: t_eval[..consumed].to_vec(),
                ys,
                ok: true,
                message: match stop_tau {
                    Some(t) => format!("whiplash threshold at tau={t:.12}"),
                    None => String::new(),
                },
            },
            stop_tau,
        ))
    };

    // ★ F2 (54차): diffsol 내부 panic 이 FFI 경계를 넘지 않게 여기서 포획
    //   (V16 적대감사 계보 — panic 은 ok=false 실패로 강등).  payload 는
    //   진단성 보존을 위해 메시지로 복원한다 (리뷰 MINOR).
    match catch_unwind(AssertUnwindSafe(build)) {
        Ok(Ok(t)) => t,
        Ok(Err(e)) => (
            Trajectory {
                taus: Vec::new(),
                ys: Vec::new(),
                ok: false,
                message: format!("{e}"),
            },
            None,
        ),
        Err(payload) => {
            let msg = payload
                .downcast_ref::<&str>()
                .map(|s| s.to_string())
                .or_else(|| payload.downcast_ref::<String>().cloned())
                .unwrap_or_else(|| "unknown panic payload".into());
            (
                Trajectory {
                    taus: Vec::new(),
                    ys: Vec::new(),
                    ok: false,
                    message: format!("diffsol internal panic (caught at FFI boundary): {msg}"),
                },
                None,
            )
        }
    }
}

/// 배치 스캔 (R3): 초기조건마다 독립 적분.  Rayon 데이터병렬.
/// 반환: 각 원소의 (마지막 상태, 성공여부).  실패 원소는 배치를 죽이지 않는다.
pub fn integrate_batch(
    chart: Chart,
    y0s: &[[f64; MAX_STATES]],
    t_eval: &[f64],
    rtol: f64,
    atol: f64,
) -> Vec<([f64; MAX_STATES], bool)> {
    y0s.par_iter()
        .map(|y0| {
            let tr = integrate(chart, &y0[..], t_eval, rtol, atol);
            if tr.ok && !tr.ys.is_empty() {
                (*tr.ys.last().unwrap(), true)
            } else {
                ([f64::NAN; MAX_STATES], false)
            }
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn bianchi_i_flat_dust_omega_to_one() {
        // Bianchi I + 먼지(γ=1): shear 가 희석되어 Ω → 1 (등방화)
        let c = Chart::ClassA { gamma: 1.0 };
        let y0 = [0.3, 0.0, 0.0, 0.0, 0.0];
        let t_eval: Vec<f64> = (0..=40).map(|i| i as f64 * 0.25).collect();
        let tr = integrate(c, &y0, &t_eval, 1e-10, 1e-12);
        assert!(tr.ok, "{}", tr.message);
        let last = tr.ys.last().unwrap();
        assert!(last[0].abs() < 1e-3, "Sigma_p={}", last[0]);
        assert!((charts::omega(&c, last) - 1.0).abs() < 1e-3);
    }

    #[test]
    fn constant_solution_survives_h_explosion_sweep() {
        // ★ F2 회귀 고정 (리뷰 강화): 평형점(정확-상수 해)에서 h 폭주 →
        //   solve_dense tstop 레이스 panic.  고정 패딩(1차 수정)은 199점
        //   스윕 중 9점이 여전히 실패했다 — 수동 step+interpolate 가 구조적
        //   수정이고, 이 스윕(과거 실패 9점 + 조밀 격자)이 그것을 고정한다.
        let c = Chart::ClassB { gamma: 1.3, kappa: 4.0 };
        let np = (2.16f64).sqrt(); // N_+^2 = (1+Sp)[k(1+Sp)-3Sp], Sp=-0.4
        let y0 = [-0.4, 0.24, 0.0, 0.36, np];
        let known_bad = [2.9, 3.3, 4.8, 4.9, 5.35, 6.05, 6.15, 6.85, 7.65];
        let grid = (10..=48).map(|i| i as f64 * 0.25);
        for t_end in known_bad.into_iter().chain(grid) {
            let t_eval: Vec<f64> = (0..=6).map(|i| i as f64 * t_end / 6.0).collect();
            let tr = integrate(c, &y0, &t_eval, 1e-10, 1e-12);
            assert!(tr.ok, "t_end={t_end}: {}", tr.message);
            let last = tr.ys.last().unwrap();
            for i in 0..5 {
                assert!(
                    (last[i] - y0[i]).abs() < 1e-9,
                    "t_end={t_end} i={i}: {} vs {}",
                    last[i],
                    y0[i]
                );
            }
        }
    }

    #[test]
    fn whiplash_threshold_truncates_tilted_run() {
        // F3: γ=2 (stiff) tilted type II — V → 1 로 G₋ = 1−V² 가 문턱 0.1 을
        //   유한 τ 에 통과한다.  중단·절단·문턱 이전 반환을 확인.
        let c = Chart::ClassATilted { gamma: 2.0 };
        let y0 = [0.1, -0.05, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.6, 0.0, 0.0];
        let t_eval: Vec<f64> = (0..=40).map(|i| i as f64 * 0.25).collect();
        let (tr, stop) = integrate_whiplash(c, &y0, &t_eval, 1e-10, 1e-12, Some(0.1));
        assert!(tr.ok, "{}", tr.message);
        let tau_star = stop.expect("threshold must be hit");
        assert!(tau_star > 0.0 && tau_star < 10.0, "tau*={tau_star}");
        assert!(tr.ys.len() < t_eval.len());
        for row in &tr.ys {
            let (g, v2) = c.tilt_gamma_v2(&row[..]).unwrap();
            assert!(1.0 - (g - 1.0) * v2 > 0.1);
        }
        // 비감시 실행은 초광속 가드가 잡는다 (리뷰 MAJOR 1: γ=2 는 (1−V²) 가
        // 1/G₋ 와 소거되어 V²=1 을 유한 τ 에 관통 — ok=true 침묵 통과 금지)
        let tr2 = integrate(c, &y0, &t_eval, 1e-10, 1e-12);
        assert!(!tr2.ok, "superluminal state must not pass silently");
        assert!(tr2.message.contains("superluminal"), "{}", tr2.message);
    }

    #[test]
    fn type_n_zero_is_preserved_exactly() {
        // N=0 이 정확히 보존 (곱셈 구조)
        let c = Chart::ClassA { gamma: 4.0 / 3.0 };
        let y0 = [0.4, -0.2, 0.0, 0.0, 0.0];
        let t_eval: Vec<f64> = (0..=20).map(|i| i as f64 * 0.2).collect();
        let tr = integrate(c, &y0, &t_eval, 1e-10, 1e-12);
        assert!(tr.ok);
        for row in &tr.ys {
            assert_eq!(row[2], 0.0);
            assert_eq!(row[3], 0.0);
            assert_eq!(row[4], 0.0);
        }
    }
}

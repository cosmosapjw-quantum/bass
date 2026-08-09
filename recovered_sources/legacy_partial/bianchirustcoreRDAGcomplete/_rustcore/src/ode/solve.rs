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
    DenseMatrix, NalgebraLU, NalgebraMat, NalgebraVec, OdeBuilder, OdeSolverMethod, Vector,
};
use rayon::prelude::*;

use crate::ode::charts::{self, Chart};

/// 단일 궤적 적분 결과.
pub struct Trajectory {
    /// 평가 시각 τ (요청한 t_eval 중 성공한 구간)
    pub taus: Vec<f64>,
    /// 상태 (M, 5) 행우선
    pub ys: Vec<[f64; 5]>,
    /// 성공 여부 (false 면 조기 종료/실패)
    pub ok: bool,
    /// 진단 메시지 (실패 시)
    pub message: String,
}

/// 차트 배경 ODE 를 τ 격자에서 적분 (diffsol BDF).
pub fn integrate(
    chart: Chart,
    y0: &[f64; 5],
    t_eval: &[f64],
    rtol: f64,
    atol: f64,
) -> Trajectory {
    let n = chart.nstates();
    let y0v = *y0;
    let c_rhs = chart;
    let c_jac = chart;

    let build = || -> Result<Trajectory, Box<dyn std::error::Error>> {
        let problem = OdeBuilder::<NalgebraMat<f64>>::new()
            .t0(t_eval[0])
            .rtol(rtol)
            .atol([atol])
            .rhs_implicit(
                move |y: &NalgebraVec<f64>, _p: &NalgebraVec<f64>, _t: f64, out: &mut NalgebraVec<f64>| {
                    let mut yy = [0.0f64; 5];
                    for i in 0..5 {
                        yy[i] = y.get_index(i);
                    }
                    let mut o = [0.0f64; 5];
                    charts::rhs(&c_rhs, &yy[..5], &mut o[..5]);
                    for i in 0..5 {
                        out.set_index(i, o[i]);
                    }
                },
                move |y: &NalgebraVec<f64>,
                      _p: &NalgebraVec<f64>,
                      _t: f64,
                      v: &NalgebraVec<f64>,
                      out: &mut NalgebraVec<f64>| {
                    let mut yy = [0.0f64; 5];
                    let mut vv = [0.0f64; 5];
                    for i in 0..5 {
                        yy[i] = y.get_index(i);
                        vv[i] = v.get_index(i);
                    }
                    let mut o = [0.0f64; 5];
                    charts::jac_mul(&c_jac, &yy[..5], &vv[..5], &mut o[..5]);
                    for i in 0..5 {
                        out.set_index(i, o[i]);
                    }
                },
            )
            .init(
                move |_p: &NalgebraVec<f64>, _t: f64, out: &mut NalgebraVec<f64>| {
                    for i in 0..5 {
                        out.set_index(i, y0v[i]);
                    }
                },
                n,
            )
            .build()?;

        let mut solver = problem.bdf::<NalgebraLU<f64>>()?;
        let (ys_mat, _stop) = solver.solve_dense(t_eval)?;

        // ys_mat: (nstates, ntimes) 밀집행렬
        let ncols = t_eval.len();
        let mut ys = Vec::with_capacity(ncols);
        for j in 0..ncols {
            let mut row = [0.0f64; 5];
            for i in 0..5 {
                row[i] = ys_mat.get_index(i, j);
            }
            ys.push(row);
        }
        Ok(Trajectory {
            taus: t_eval.to_vec(),
            ys,
            ok: true,
            message: String::new(),
        })
    };

    match build() {
        Ok(t) => t,
        Err(e) => Trajectory {
            taus: Vec::new(),
            ys: Vec::new(),
            ok: false,
            message: format!("{e}"),
        },
    }
}

/// 배치 스캔 (R3): 초기조건마다 독립 적분.  Rayon 데이터병렬.
/// 반환: 각 원소의 (마지막 상태, 성공여부).  실패 원소는 배치를 죽이지 않는다.
pub fn integrate_batch(
    chart: Chart,
    y0s: &[[f64; 5]],
    t_eval: &[f64],
    rtol: f64,
    atol: f64,
) -> Vec<([f64; 5], bool)> {
    y0s.par_iter()
        .map(|y0| {
            let tr = integrate(chart, y0, t_eval, rtol, atol);
            if tr.ok && !tr.ys.is_empty() {
                (*tr.ys.last().unwrap(), true)
            } else {
                ([f64::NAN; 5], false)
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

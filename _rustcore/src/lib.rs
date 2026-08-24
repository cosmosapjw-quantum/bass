//! bianchi_rustcore · R0/R1 — Rust 연산 코어 (규약 패리티 + 측지 광선추적).
//!
//! 경계 규약: rust-numpy 무복사 입력, 연산 중 GIL 해제(`Python::detach`)로 진짜 병렬.
//! 모든 노출 함수는 Python 오라클(`bianchi.conventions`, `bianchi.rays.geodesics`)과
//! 차등테스트(rtol≤1e-10)로 대조된다.

use nalgebra::{Matrix3, Vector3};
use numpy::ndarray::{Array1, Array2};
use numpy::{
    IntoPyArray, PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2, PyReadonlyArray3,
};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

mod core;
mod geom;
mod kinetic;
mod ode;
mod rays;
mod thermo;

use crate::core::conventions;
use crate::rays::{geodesic, optical, tidal};

type RayTraceOutput<'py> = (
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray2<f64>>,
    Bound<'py, PyArray2<f64>>,
);
type OpticalTraceOutput<'py> = (
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray2<f64>>,
    f64,
    f64,
    f64,
);
type Array1Pair<'py> = (Bound<'py, PyArray1<f64>>, Bound<'py, PyArray1<f64>>);
type Array2Array1Pair<'py> = (Bound<'py, PyArray2<f64>>, Bound<'py, PyArray1<f64>>);
type Array1Triple<'py> = (
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray1<f64>>,
);
type MomentHistoryOutput<'py> = (
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray2<f64>>,
);
type TiltedMomentsOutput<'py> = (
    f64,
    f64,
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray2<f64>>,
);
type BounceSequenceOutput<'py> = (
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray1<i64>>,
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray1<f64>>,
);
type MassBlocksOutput<'py> = (
    Bound<'py, PyArray2<f64>>,
    Bound<'py, PyArray2<f64>>,
    Option<Bound<'py, PyArray2<f64>>>,
);
type CoupledEvolutionOutput<'py> = (Bound<'py, PyArray1<f64>>, Option<Bound<'py, PyArray2<f64>>>);
type GroupClassificationOutput = (String, String, Option<f64>, bool, (i32, i32, i32), i32);

#[inline]
fn to_vec3(a: &PyReadonlyArray1<f64>) -> PyResult<Vector3<f64>> {
    let s = a.as_slice()?;
    if s.len() != 3 {
        return Err(PyValueError::new_err("expected length-3 vector"));
    }
    Ok(Vector3::new(s[0], s[1], s[2]))
}

#[inline]
fn to_mat3(a: &PyReadonlyArray2<f64>) -> PyResult<Matrix3<f64>> {
    let v = a.as_array();
    if v.shape() != [3, 3] {
        return Err(PyValueError::new_err("expected 3x3 matrix"));
    }
    Ok(Matrix3::new(
        v[[0, 0]],
        v[[0, 1]],
        v[[0, 2]],
        v[[1, 0]],
        v[[1, 1]],
        v[[1, 2]],
        v[[2, 0]],
        v[[2, 1]],
        v[[2, 2]],
    ))
}

#[inline]
fn mat3_to_py<'py>(py: Python<'py>, m: &Matrix3<f64>) -> Bound<'py, PyArray2<f64>> {
    Array2::from_shape_fn((3, 3), |(i, j)| m[(i, j)]).into_pyarray(py)
}

// ─────────────────────────────── 규약 패리티
#[pyfunction]
fn rotation_matrix<'py>(
    py: Python<'py>,
    r: PyReadonlyArray1<f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    Ok(mat3_to_py(
        py,
        &conventions::rotation_matrix_commutator(&to_vec3(&r)?),
    ))
}

#[pyfunction]
fn tracefree_from_5<'py>(
    py: Python<'py>,
    s00: f64,
    s11: f64,
    s01: f64,
    s02: f64,
    s12: f64,
) -> Bound<'py, PyArray2<f64>> {
    mat3_to_py(py, &conventions::tracefree_from_5(s00, s11, s01, s02, s12))
}

#[pyfunction]
fn p_double<'py>(
    py: Python<'py>,
    n: PyReadonlyArray2<f64>,
    a: PyReadonlyArray1<f64>,
    x: PyReadonlyArray1<f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let p = conventions::p_double(&to_mat3(&n)?, &to_vec3(&a)?, &to_vec3(&x)?);
    Ok(Array1::from_vec(vec![p[0], p[1], p[2]]).into_pyarray(py))
}

// ─────────────────────────────── 광선추적 (R1)
/// 단일 광선.  반환 (ts, zs, Hs, nhats[M,3], lnas[M,3]) — Python hist 리스트에 대응.
#[pyfunction]
#[pyo3(signature = (h0, sigma0, omega0, gamma, nhat, t0, t_end, nsteps = 4000))]
#[allow(clippy::too_many_arguments)]
fn trace_ray_diag<'py>(
    py: Python<'py>,
    h0: f64,
    sigma0: PyReadonlyArray1<f64>,
    omega0: f64,
    gamma: f64,
    nhat: PyReadonlyArray1<f64>,
    t0: f64,
    t_end: f64,
    nsteps: usize,
) -> PyResult<RayTraceOutput<'py>> {
    let sig0 = to_vec3(&sigma0)?;
    let nh = to_vec3(&nhat)?;
    let config = geodesic::RayTraceConfig {
        h0,
        omega0,
        gamma,
        t0,
        t_end,
        nsteps,
    };
    let hist = py.detach(|| geodesic::trace_ray_diag(&sig0, &nh, &config));
    let m = hist.z.len();
    let nhs = Array2::from_shape_fn((m, 3), |(i, j)| hist.nh[i][j]).into_pyarray(py);
    let lnas = Array2::from_shape_fn((m, 3), |(i, j)| hist.lna[i][j]).into_pyarray(py);
    Ok((
        Array1::from_vec(hist.t).into_pyarray(py),
        Array1::from_vec(hist.z).into_pyarray(py),
        Array1::from_vec(hist.h).into_pyarray(py),
        nhs,
        lnas,
    ))
}

/// 배치: 방향 배열(K,3) → 방향별 마지막 z (CMB 패턴의 z(n̂)).  Rayon 데이터병렬.
#[pyfunction]
#[pyo3(signature = (h0, sigma0, omega0, gamma, nhats, t0, t_end, nsteps = 4000))]
#[allow(clippy::too_many_arguments)]
fn trace_rays_batch<'py>(
    py: Python<'py>,
    h0: f64,
    sigma0: PyReadonlyArray1<f64>,
    omega0: f64,
    gamma: f64,
    nhats: PyReadonlyArray2<f64>,
    t0: f64,
    t_end: f64,
    nsteps: usize,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let sig0 = to_vec3(&sigma0)?;
    let view = nhats.as_array();
    if view.ncols() != 3 {
        return Err(PyValueError::new_err("nhats must be shape (K,3)"));
    }
    let dirs: Vec<Vector3<f64>> = view
        .rows()
        .into_iter()
        .map(|row| Vector3::new(row[0], row[1], row[2]))
        .collect();
    let config = geodesic::RayTraceConfig {
        h0,
        omega0,
        gamma,
        t0,
        t_end,
        nsteps,
    };
    let zs = py.detach(|| geodesic::trace_rays_batch_final_z(&sig0, &dirs, &config));
    Ok(Array1::from_vec(zs).into_pyarray(py))
}

// ─────────────────────────────── 광학 d_A (R1 완결 + R4)
/// 단일 널 다발.  반환 dict-유사 튜플 (zs, dAs, lnas[M,3], z_final, dA_final, screen_ortho).
#[pyfunction]
#[pyo3(signature = (h0, sigma0, omega0, gamma, nhat, t0, t_end, nsteps = 4000))]
#[allow(clippy::too_many_arguments)]
fn trace_optical_diag<'py>(
    py: Python<'py>,
    h0: f64,
    sigma0: PyReadonlyArray1<f64>,
    omega0: f64,
    gamma: f64,
    nhat: PyReadonlyArray1<f64>,
    t0: f64,
    t_end: f64,
    nsteps: usize,
) -> PyResult<OpticalTraceOutput<'py>> {
    let sig0 = to_vec3(&sigma0)?;
    let nh = to_vec3(&nhat)?;
    let r =
        py.detach(|| optical::trace_optical_diag(h0, &sig0, omega0, gamma, &nh, t0, t_end, nsteps));
    let m = r.z.len();
    let lnas = Array2::from_shape_fn((m, 3), |(i, j)| r.lna[i][j]).into_pyarray(py);
    Ok((
        Array1::from_vec(r.z).into_pyarray(py),
        Array1::from_vec(r.da).into_pyarray(py),
        lnas,
        r.z_final,
        r.da_final,
        r.screen_ortho,
    ))
}

/// 배치 광학: 방향(K,3) → (zs[K], dAs[K]).  Rayon 데이터병렬.
#[pyfunction]
#[pyo3(signature = (h0, sigma0, omega0, gamma, nhats, t0, t_end, nsteps = 4000))]
#[allow(clippy::too_many_arguments)]
fn trace_optical_batch<'py>(
    py: Python<'py>,
    h0: f64,
    sigma0: PyReadonlyArray1<f64>,
    omega0: f64,
    gamma: f64,
    nhats: PyReadonlyArray2<f64>,
    t0: f64,
    t_end: f64,
    nsteps: usize,
) -> PyResult<Array1Pair<'py>> {
    let sig0 = to_vec3(&sigma0)?;
    let view = nhats.as_array();
    if view.ncols() != 3 {
        return Err(PyValueError::new_err("nhats must be shape (K,3)"));
    }
    let dirs: Vec<Vector3<f64>> = view
        .rows()
        .into_iter()
        .map(|row| Vector3::new(row[0], row[1], row[2]))
        .collect();
    let res = py.detach(|| {
        optical::trace_optical_batch(h0, &sig0, omega0, gamma, &dirs, t0, t_end, nsteps)
    });
    let zs: Vec<f64> = res.iter().map(|p| p.0).collect();
    let das: Vec<f64> = res.iter().map(|p| p.1).collect();
    Ok((
        Array1::from_vec(zs).into_pyarray(py),
        Array1::from_vec(das).into_pyarray(py),
    ))
}

// ─────────────────────────────── 배경 ODE (R2/R3)
fn make_chart(chart: &str, gamma: f64, kappa: f64) -> PyResult<ode::charts::Chart> {
    match chart {
        "class_a" => Ok(ode::charts::Chart::ClassA { gamma }),
        "class_b" => Ok(ode::charts::Chart::ClassB { gamma, kappa }),
        // C2 · 커버리지 차트 셋
        "class_b_tilted" => Ok(ode::charts::Chart::ClassBTilted { gamma }),
        // F3 · tilted class A (n-대각 게이지)
        "class_a_tilted" => Ok(ode::charts::Chart::ClassATilted { gamma }),
        "exceptional" => Ok(ode::charts::Chart::Exceptional { gamma }),
        "type_ix_d" => Ok(ode::charts::Chart::TypeIXD {
            gamma,
            future: false,
        }),
        "type_ix_d_future" => Ok(ode::charts::Chart::TypeIXD {
            gamma,
            future: true,
        }),
        other => Err(PyValueError::new_err(format!(
            "unknown chart '{other}' (class_a / class_b / class_a_tilted / \
             class_b_tilted / exceptional / type_ix_d / type_ix_d_future)"
        ))),
    }
}

/// 상태를 차트 길이에 맞춰 MAX_STATES 버퍼로 (길이 검사 포함).
#[inline]
fn to_yn(
    a: &PyReadonlyArray1<f64>,
    c: &ode::charts::Chart,
) -> PyResult<[f64; ode::charts::MAX_STATES]> {
    let s = a.as_slice()?;
    let n = c.nstates();
    if s.len() != n {
        return Err(PyValueError::new_err(format!(
            "state must have length {n} for this chart, got {}",
            s.len()
        )));
    }
    let mut out = [0.0f64; ode::charts::MAX_STATES];
    out[..n].copy_from_slice(s);
    Ok(out)
}

/// 차트 RHS 단일 평가 (차등테스트용).
#[pyfunction]
#[pyo3(signature = (chart, y, gamma, kappa = 0.0))]
fn chart_rhs<'py>(
    py: Python<'py>,
    chart: &str,
    y: PyReadonlyArray1<f64>,
    gamma: f64,
    kappa: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let c = make_chart(chart, gamma, kappa)?;
    let yy = to_yn(&y, &c)?;
    let n = c.nstates();
    let mut out = [0.0f64; ode::charts::MAX_STATES];
    ode::charts::rhs(&c, &yy[..n], &mut out[..n]);
    Ok(Array1::from_vec(out[..n].to_vec()).into_pyarray(py))
}

/// 보조량 (Omega, Codazzi C).
#[pyfunction]
#[pyo3(signature = (chart, y, gamma, kappa = 0.0))]
fn chart_aux(
    chart: &str,
    y: PyReadonlyArray1<f64>,
    gamma: f64,
    kappa: f64,
) -> PyResult<(f64, f64)> {
    let c = make_chart(chart, gamma, kappa)?;
    let yy = to_yn(&y, &c)?;
    let n = c.nstates();
    Ok((
        ode::charts::omega(&c, &yy[..n]),
        ode::charts::codazzi(&c, &yy[..n]),
    ))
}

/// 단일 궤적 적분 (diffsol BDF).  반환 (ys[M,5], ok).
#[pyfunction]
#[pyo3(signature = (chart, y0, t_eval, gamma, kappa = 0.0, rtol = 1e-10, atol = 1e-12))]
#[allow(clippy::too_many_arguments)]
fn integrate_background<'py>(
    py: Python<'py>,
    chart: &str,
    y0: PyReadonlyArray1<f64>,
    t_eval: PyReadonlyArray1<f64>,
    gamma: f64,
    kappa: f64,
    rtol: f64,
    atol: f64,
) -> PyResult<(Bound<'py, PyArray2<f64>>, bool)> {
    let c = make_chart(chart, gamma, kappa)?;
    let y0a = to_yn(&y0, &c)?;
    let n = c.nstates();
    let ts = t_eval.as_slice()?.to_vec();
    if ts.len() < 2 {
        return Err(PyValueError::new_err("t_eval needs >= 2 points"));
    }
    let tr = py.detach(|| ode::solve::integrate(c, &y0a[..], &ts, rtol, atol));
    let m = tr.ys.len();
    let ys = Array2::from_shape_fn((m, n), |(i, j)| tr.ys[i][j]).into_pyarray(py);
    Ok((ys, tr.ok))
}

/// F3 · 편타(whiplash) 문턱 감시 적분 (tilt 차트 전용).
/// G₋ = 1 − (γ−1)V² < gap_eps 가 되는 τ* 에서 중단 (이분법 60회).
/// 반환: (ys — τ* 이전 요청 시각만 (M', n), ok, hit, tau_hit — 미발생 시 NaN).
///
/// ★ γ ≤ 2 에서 G₋ 영교차는 없다 (V²=1 불변 경계) — 문턱 통과 이벤트다.
#[pyfunction]
#[pyo3(signature = (chart, y0, t_eval, gamma, kappa = 0.0, gap_eps = 1e-3,
                    rtol = 1e-10, atol = 1e-12))]
#[allow(clippy::too_many_arguments)]
fn integrate_background_whiplash<'py>(
    py: Python<'py>,
    chart: &str,
    y0: PyReadonlyArray1<f64>,
    t_eval: PyReadonlyArray1<f64>,
    gamma: f64,
    kappa: f64,
    gap_eps: f64,
    rtol: f64,
    atol: f64,
) -> PyResult<(Bound<'py, PyArray2<f64>>, bool, bool, f64)> {
    let c = make_chart(chart, gamma, kappa)?;
    if c.tilt_gamma_v2(&[0.0; ode::charts::MAX_STATES][..c.nstates()])
        .is_none()
    {
        return Err(PyValueError::new_err(
            "whiplash 감시는 tilt 차트(class_a_tilted/class_b_tilted) 전용",
        ));
    }
    let y0a = to_yn(&y0, &c)?;
    let n = c.nstates();
    let ts = t_eval.as_slice()?.to_vec();
    if ts.len() < 2 {
        return Err(PyValueError::new_err("t_eval needs >= 2 points"));
    }
    let (tr, stop) =
        py.detach(|| ode::solve::integrate_whiplash(c, &y0a[..], &ts, rtol, atol, Some(gap_eps)));
    let m = tr.ys.len();
    let ys = Array2::from_shape_fn((m, n), |(i, j)| tr.ys[i][j]).into_pyarray(py);
    Ok((ys, tr.ok, stop.is_some(), stop.unwrap_or(f64::NAN)))
}

/// 배치 스캔 (R3): 초기조건 (K,5) → (마지막 상태 (K,5), 성공 마스크 (K,)).
/// Rayon 병렬 — 낙오자가 배치 전체를 오염시키지 않는다 (JAX while_loop 대비 이점).
#[pyfunction]
#[pyo3(signature = (chart, y0s, t_eval, gamma, kappa = 0.0, rtol = 1e-10, atol = 1e-12))]
#[allow(clippy::too_many_arguments)]
fn integrate_batch<'py>(
    py: Python<'py>,
    chart: &str,
    y0s: PyReadonlyArray2<f64>,
    t_eval: PyReadonlyArray1<f64>,
    gamma: f64,
    kappa: f64,
    rtol: f64,
    atol: f64,
) -> PyResult<Array2Array1Pair<'py>> {
    let c = make_chart(chart, gamma, kappa)?;
    let n = c.nstates();
    let view = y0s.as_array();
    if view.ncols() != n {
        return Err(PyValueError::new_err(format!("y0s must be shape (K,{n})")));
    }
    let inits: Vec<[f64; ode::charts::MAX_STATES]> = view
        .rows()
        .into_iter()
        .map(|r| {
            let mut b = [0.0f64; ode::charts::MAX_STATES];
            for j in 0..n {
                b[j] = r[j];
            }
            b
        })
        .collect();
    let ts = t_eval.as_slice()?.to_vec();
    let res = py.detach(|| ode::solve::integrate_batch(c, &inits, &ts, rtol, atol));
    let k = res.len();
    let ys = Array2::from_shape_fn((k, n), |(i, j)| res[i].0[j]).into_pyarray(py);
    let ok = Array1::from_vec(res.iter().map(|r| if r.1 { 1.0 } else { 0.0 }).collect())
        .into_pyarray(py);
    Ok((ys, ok))
}

// ─────────────────────────────── C1 · 일반유형 조석 (codegen Riemann)
#[inline]
fn to_args24(a: &PyReadonlyArray1<f64>) -> PyResult<[f64; 24]> {
    let s = a.as_slice()?;
    if s.len() != 24 {
        return Err(PyValueError::new_err(
            "args must have length 24 (weyl.pack_state)",
        ));
    }
    let mut out = [0.0f64; 24];
    out.copy_from_slice(s);
    Ok(out)
}

/// 일반유형 R^a_bcd 를 평탄 (256,) 로 — numpy 에서 reshape(4,4,4,4).
#[pyfunction]
fn riemann_up_general<'py>(
    py: Python<'py>,
    args: PyReadonlyArray1<f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let p = to_args24(&args)?;
    let mut out = [0.0f64; 256];
    crate::rays::riemann_gen::riemann_up(&p, &mut out);
    Ok(Array1::from_vec(out.to_vec()).into_pyarray(py))
}

/// 일반유형 조석행렬 T_AB — Python `weyl.tidal_matrix` 대응.
#[pyfunction]
fn tidal_general<'py>(
    py: Python<'py>,
    args: PyReadonlyArray1<f64>,
    k: PyReadonlyArray1<f64>,
    screen: PyReadonlyArray2<f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let p = to_args24(&args)?;
    let ks = k.as_slice()?;
    if ks.len() != 4 {
        return Err(PyValueError::new_err("k must have length 4"));
    }
    let kv = nalgebra::Vector4::new(ks[0], ks[1], ks[2], ks[3]);
    let sv = screen.as_array();
    if sv.shape() != [2, 4] {
        return Err(PyValueError::new_err("screen must be shape (2,4)"));
    }
    let sc = [
        nalgebra::Vector4::new(sv[[0, 0]], sv[[0, 1]], sv[[0, 2]], sv[[0, 3]]),
        nalgebra::Vector4::new(sv[[1, 0]], sv[[1, 1]], sv[[1, 2]], sv[[1, 3]]),
    ];
    let t = tidal::tidal_general(&p, &kv, &sc);
    Ok(Array2::from_shape_fn((2, 2), |(i, j)| t[(i, j)]).into_pyarray(py))
}

/// Ricci 집속 오라클용:  R_mn k^m k^n.
#[pyfunction]
fn ricci_kk(args: PyReadonlyArray1<f64>, k: PyReadonlyArray1<f64>) -> PyResult<f64> {
    let p = to_args24(&args)?;
    let ks = k.as_slice()?;
    let kv = nalgebra::Vector4::new(ks[0], ks[1], ks[2], ks[3]);
    Ok(tidal::ricci_kk(&p, &kv))
}

// ─────────────────────────────── B1 · 열역학 커널 (Rust)
/// 중성미자 FD (ρ, p, w) 단일 a.  Python `matter.neutrino.neutrino_rho_p` 미러.
#[pyfunction]
#[pyo3(signature = (a, y0, n_species = 1.0))]
fn fd_rho_p(a: f64, y0: f64, n_species: f64) -> (f64, f64, f64) {
    thermo::fd::neutrino_rho_p(a, y0, n_species)
}

/// 배치 FD — a 배열에 대해 (rho[K], p[K], w[K]).  Rayon 병렬.
/// ★ 이것이 B1 의 요점: Python scipy.quad 는 1 ms/호출이라 ODE RHS 안에서 못 쓴다.
#[pyfunction]
#[pyo3(signature = (a, y0, n_species = 1.0))]
fn fd_rho_p_batch<'py>(
    py: Python<'py>,
    a: PyReadonlyArray1<f64>,
    y0: f64,
    n_species: f64,
) -> PyResult<Array1Triple<'py>> {
    let av = a.as_slice()?.to_vec();
    let res: Vec<(f64, f64, f64)> = py.detach(|| {
        use rayon::prelude::*;
        av.par_iter()
            .map(|&ai| thermo::fd::neutrino_rho_p(ai, y0, n_species))
            .collect()
    });
    Ok((
        Array1::from_vec(res.iter().map(|r| r.0).collect()).into_pyarray(py),
        Array1::from_vec(res.iter().map(|r| r.1).collect()).into_pyarray(py),
        Array1::from_vec(res.iter().map(|r| r.2).collect()).into_pyarray(py),
    ))
}

/// g_*(T[GeV]) — Python `thermo.dof.g_star` 미러 (표는 자동생성 공유).
#[pyfunction]
fn g_star(t_gev: f64) -> f64 {
    thermo::dof::g_star(t_gev)
}

/// g_*s(T[GeV]).
#[pyfunction]
fn g_star_s(t_gev: f64) -> f64 {
    thermo::dof::g_star_s(t_gev)
}

// ─────────────────────────────── H2 · 운동론 (구적 + 다극 계층)
#[inline]
fn check_l(l: usize) -> PyResult<()> {
    // ★ 기존 결함 수정: l > L_MAX 에서 `index_table` / `pstf_gen` 이 **panic** 했다
    //   (kin_j_moment 도 마찬가지였다).  Rust panic 이 FFI 를 넘으면 PanicException 이
    //   되어 진단이 어렵고 상태 오염 위험이 있으므로, 경계에서 깨끗한 ValueError 로 막는다.
    if l > kinetic::pstf_gen::L_MAX {
        return Err(PyValueError::new_err(format!(
            "l = {l} 은 지원 범위를 넘는다 (L_MAX = {});              scripts/codegen_pstf.py 의 L_MAX_RUST 를 올리고 재생성하라",
            kinetic::pstf_gen::L_MAX
        )));
    }
    Ok(())
}

fn to_a3(a: &PyReadonlyArray1<f64>) -> PyResult<[f64; 3]> {
    let s = a.as_slice()?;
    if s.len() != 3 {
        return Err(PyValueError::new_err("expected length-3"));
    }
    Ok([s[0], s[1], s[2]])
}

/// 구적 모멘트 J^(i)_{A_l} — 평탄 (3^l,) 반환.  Python `hierarchy.J_moment` 대응.
#[pyfunction]
#[pyo3(signature = (a_vec, mass, l, i, dipole_eps = 0.0, dipole_axis = 2))]
fn kin_j_moment<'py>(
    py: Python<'py>,
    a_vec: PyReadonlyArray1<f64>,
    mass: f64,
    l: usize,
    i: i32,
    dipole_eps: f64,
    dipole_axis: usize,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    check_l(l)?;
    let a = to_a3(&a_vec)?;
    let v = py.detach(|| kinetic::quad::j_moment(&a, mass, l, i, dipole_eps, dipole_axis));
    Ok(Array1::from_vec(v).into_pyarray(py))
}

/// freestream 대응 (ρ, p, π_ab 평탄9).  Python `freestream.moments` 대응.
#[pyfunction]
fn kin_moments<'py>(
    py: Python<'py>,
    a_vec: PyReadonlyArray1<f64>,
    mass: f64,
) -> PyResult<(f64, f64, Bound<'py, PyArray2<f64>>)> {
    let a = to_a3(&a_vec)?;
    let (rho, p, pi) = py.detach(|| kinetic::quad::moments(&a, mass));
    Ok((
        rho,
        p,
        Array2::from_shape_fn((3, 3), |(i, j)| pi[i * 3 + j]).into_pyarray(py),
    ))
}

/// PSTF 사영 (평탄 rank-l 입력·출력) — 차등테스트용.
#[pyfunction]
fn kin_pstf<'py>(
    py: Python<'py>,
    t: PyReadonlyArray1<f64>,
    l: usize,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    check_l(l)?;
    let v = t.as_slice()?.to_vec();
    if v.len() != 3usize.pow(l as u32) {
        return Err(PyValueError::new_err("length must be 3^l"));
    }
    Ok(Array1::from_vec(kinetic::pstf::project(&v, l)).into_pyarray(py))
}

/// 계층 RK4 적분 — 반환 (t[N], rho[N], p[N], pi[N,9]).
#[pyfunction]
#[pyo3(signature = (a0, mass, h, sigma_diag, t_end, nsteps = 40, l_max = 4, i_max = 2,
                    dipole_eps = 0.0))]
#[allow(clippy::too_many_arguments)]
fn kin_integrate<'py>(
    py: Python<'py>,
    a0: PyReadonlyArray1<f64>,
    mass: f64,
    h: f64,
    sigma_diag: PyReadonlyArray1<f64>,
    t_end: f64,
    nsteps: usize,
    l_max: usize,
    i_max: usize,
    dipole_eps: f64,
) -> PyResult<MomentHistoryOutput<'py>> {
    // ★ 계층 RHS 의 (B) 항은 `l + 2 <= l_max` 로 **단순절단**되므로 격자 밖 rank 를
    //   건드리지 않는다.  따라서 필요한 PSTF 한계는 l_max 자체다 (l_max+2 가 아니다).
    check_l(l_max)?;
    let a = to_a3(&a0)?;
    let sg = to_a3(&sigma_diag)?;
    let (ts, rhos, ps, pis) = py.detach(|| {
        kinetic::hierarchy::integrate(&a, mass, h, &sg, t_end, nsteps, l_max, i_max, dipole_eps)
    });
    let n = pis.len();
    let pim = Array2::from_shape_fn((n, 9), |(i, j)| pis[i][j]).into_pyarray(py);
    Ok((
        Array1::from_vec(ts).into_pyarray(py),
        Array1::from_vec(rhos).into_pyarray(py),
        Array1::from_vec(ps).into_pyarray(py),
        pim,
    ))
}

// ─────────────────────────────── H3 · Thomson 충돌항 (두 경로 분리 노출)
use crate::kinetic::collision as coll;

#[inline]
fn to_route(s: &str) -> PyResult<coll::Route> {
    match s {
        "analytic" => Ok(coll::Route::Analytic),
        "numeric" => Ok(coll::Route::Numeric),
        o => Err(PyValueError::new_err(format!(
            "unknown route '{o}' (expected 'analytic' or 'numeric')"
        ))),
    }
}

/// 경로 A — Thomson 위상함수 각적분으로 측정한 λ_l (다극 대수 미사용).
#[pyfunction]
#[pyo3(signature = (l, n_nodes = 200))]
fn kin_thomson_eigenvalue_numeric(l: usize, n_nodes: usize) -> f64 {
    coll::eigenvalue_numeric(l, n_nodes)
}

/// 경로 B — 해석 다극 λ_l = 4π k_l/(2l+1) (적분 미사용).
#[pyfunction]
fn kin_thomson_eigenvalue(l: usize) -> f64 {
    coll::eigenvalue(l)
}

/// Legendre P_l(x) — 경로 A 내부 점화의 차등테스트용 노출.
#[pyfunction]
fn kin_legendre(l: usize, x: f64) -> f64 {
    coll::legendre(l, x)
}

/// 충돌항 C[J^(i)_{A_l}] — 구적 초기조건에서 평탄 (3^l,).
#[pyfunction]
#[pyo3(signature = (a_vec, mass, l, i, n_e_sigma_t, route = "analytic", l_max = 4, i_max = 2,
                    dipole_eps = 0.0))]
#[allow(clippy::too_many_arguments)]
fn kin_collision_term<'py>(
    py: Python<'py>,
    a_vec: PyReadonlyArray1<f64>,
    mass: f64,
    l: usize,
    i: i32,
    n_e_sigma_t: f64,
    route: &str,
    l_max: usize,
    i_max: usize,
    dipole_eps: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let a = to_a3(&a_vec)?;
    let r = to_route(route)?;
    let v = py.detach(|| {
        let s = kinetic::hierarchy::State::from_quadrature(&a, mass, l_max, i_max, dipole_eps, 2);
        coll::collision_term(&s, l, i, n_e_sigma_t, r)
    });
    Ok(Array1::from_vec(v).into_pyarray(py))
}

/// 충돌 계층 RHS 한 항 — 무충돌 RHS + 충돌항.
#[pyfunction]
#[pyo3(signature = (a_vec, mass, h, sigma_diag, l, i, n_e_sigma_t, route = "analytic",
                    l_max = 4, i_max = 2, dipole_eps = 0.0))]
#[allow(clippy::too_many_arguments)]
fn kin_rhs_collisional<'py>(
    py: Python<'py>,
    a_vec: PyReadonlyArray1<f64>,
    mass: f64,
    h: f64,
    sigma_diag: PyReadonlyArray1<f64>,
    l: usize,
    i: i32,
    n_e_sigma_t: f64,
    route: &str,
    l_max: usize,
    i_max: usize,
    dipole_eps: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let a = to_a3(&a_vec)?;
    let sd = to_a3(&sigma_diag)?;
    let r = to_route(route)?;
    let sigma = [sd[0], 0.0, 0.0, 0.0, sd[1], 0.0, 0.0, 0.0, sd[2]];
    let v = py.detach(|| {
        let mut s =
            kinetic::hierarchy::State::from_quadrature(&a, mass, l_max, i_max, dipole_eps, 2);
        s.close_i();
        coll::rhs_one_collisional(&s, h, &sigma, l, i, n_e_sigma_t, r)
    });
    Ok(Array1::from_vec(v).into_pyarray(py))
}

/// 충돌 계층 RK4 적분 — 반환 (t[N], rho[N], p[N], pi[N,9]).
#[pyfunction]
#[pyo3(signature = (a0, mass, h, sigma_diag, n_e_sigma_t, t_end, nsteps = 40, l_max = 4,
                    i_max = 2, dipole_eps = 0.0, route = "analytic"))]
#[allow(clippy::too_many_arguments)]
fn kin_integrate_collisional<'py>(
    py: Python<'py>,
    a0: PyReadonlyArray1<f64>,
    mass: f64,
    h: f64,
    sigma_diag: PyReadonlyArray1<f64>,
    n_e_sigma_t: f64,
    t_end: f64,
    nsteps: usize,
    l_max: usize,
    i_max: usize,
    dipole_eps: f64,
    route: &str,
) -> PyResult<MomentHistoryOutput<'py>> {
    let a = to_a3(&a0)?;
    let sg = to_a3(&sigma_diag)?;
    let r = to_route(route)?;
    let (ts, rhos, ps, pis) = py.detach(|| {
        coll::integrate_collisional(
            &a,
            mass,
            h,
            &sg,
            n_e_sigma_t,
            t_end,
            nsteps,
            l_max,
            i_max,
            dipole_eps,
            r,
        )
    });
    let n = pis.len();
    let pim = Array2::from_shape_fn((n, 9), |(i, j)| pis[i][j]).into_pyarray(py);
    Ok((
        Array1::from_vec(ts).into_pyarray(py),
        Array1::from_vec(rhos).into_pyarray(py),
        Array1::from_vec(ps).into_pyarray(py),
        pim,
    ))
}

/// 유도된 Thomson 점성 — (eta, tau_pi, damping_rate, eta·n_eσ_T/ρ).
#[pyfunction]
#[pyo3(signature = (rho, n_e_sigma_t, h = 0.0, include_thomson_9_10 = true))]
fn kin_thomson_viscosity(
    rho: f64,
    n_e_sigma_t: f64,
    h: f64,
    include_thomson_9_10: bool,
) -> (f64, f64, f64, f64) {
    coll::thomson_viscosity(rho, n_e_sigma_t, h, include_thomson_9_10)
}

/// 긴밀결합 게이트 — (π_qs/ρ, 감쇠율, 소스/ρ).
#[pyfunction]
#[pyo3(signature = (mass, a_vec, h, sigma_diag, n_e_sigma_t, l_max = 4, i_max = 2))]
#[allow(clippy::too_many_arguments)]
fn kin_tight_coupling(
    py: Python<'_>,
    mass: f64,
    a_vec: PyReadonlyArray1<f64>,
    h: f64,
    sigma_diag: PyReadonlyArray1<f64>,
    n_e_sigma_t: f64,
    l_max: usize,
    i_max: usize,
) -> PyResult<(f64, f64, f64)> {
    let a = to_a3(&a_vec)?;
    let sd = to_a3(&sigma_diag)?;
    Ok(py.detach(|| coll::tight_coupling_residual(mass, &a, h, &sd, n_e_sigma_t, l_max, i_max)))
}

/// 자유흐름 극한 잔차 — n_eσ_T=0 에서 정확히 0 이어야 한다.
#[pyfunction]
#[pyo3(signature = (mass, a_vec, h, sigma_diag))]
fn kin_free_streaming_residual(
    py: Python<'_>,
    mass: f64,
    a_vec: PyReadonlyArray1<f64>,
    h: f64,
    sigma_diag: PyReadonlyArray1<f64>,
) -> PyResult<f64> {
    let a = to_a3(&a_vec)?;
    let sd = to_a3(&sigma_diag)?;
    Ok(py.detach(|| coll::free_streaming_limit_residual(mass, &a, h, &sd)))
}

/// RK4 강성 진단 — (n_eσ_T·dt·(1−λ₂), 안정 여부).
#[pyfunction]
fn kin_stiffness_ratio(n_e_sigma_t: f64, dt: f64) -> (f64, bool) {
    coll::stiffness_ratio(n_e_sigma_t, dt)
}

// ─────────────────────────────── H4 · imperfect fluid 유도 (두 경로 분리 노출)
use crate::kinetic::viscous as visc;

/// 경로 A (구적 유한차분) 감쇠 — (성분별[3], 평균, 이방성).
#[pyfunction]
#[pyo3(signature = (mass, a_vec, h = 1.0, dt = 1e-5))]
fn kin_route_a_damping<'py>(
    py: Python<'py>,
    mass: f64,
    a_vec: PyReadonlyArray1<f64>,
    h: f64,
    dt: f64,
) -> PyResult<(Bound<'py, PyArray1<f64>>, f64, f64)> {
    let a = to_a3(&a_vec)?;
    let d = py.detach(|| visc::route_a_damping(mass, &a, h, dt));
    Ok((
        Array1::from_vec(d.per_component.to_vec()).into_pyarray(py),
        d.mean,
        d.anisotropy,
    ))
}

/// 경로 A 소스 계수 (급작응답) — 구적만 사용.
#[pyfunction]
#[pyo3(signature = (mass, delta = 0.002))]
fn kin_route_a_source(py: Python<'_>, mass: f64, delta: f64) -> f64 {
    py.detach(|| visc::route_a_source(mass, delta))
}

/// 경로 B (PSTF 계층) 감쇠 — 등방 a_vec 은 ValueError.
#[pyfunction]
#[pyo3(signature = (mass, a_vec, h = 1.0))]
fn kin_route_b_damping<'py>(
    py: Python<'py>,
    mass: f64,
    a_vec: PyReadonlyArray1<f64>,
    h: f64,
) -> PyResult<(Bound<'py, PyArray1<f64>>, f64, f64)> {
    let a = to_a3(&a_vec)?;
    let d = py
        .detach(|| visc::route_b_damping(mass, &a, h))
        .ok_or_else(|| PyValueError::new_err("a_vec 이 등방이면 π_ab ≡ 0 이라 감쇠율 정의 불가"))?;
    Ok((
        Array1::from_vec(d.per_component.to_vec()).into_pyarray(py),
        d.mean,
        d.anisotropy,
    ))
}

/// 경로 B 손세팅 감쇠 — **구적 전혀 미사용**, 무질량에서 정확히 −4H.
#[pyfunction]
#[pyo3(signature = (h = 1.0, pi_diag = None))]
fn kin_route_b_damping_handset<'py>(
    py: Python<'py>,
    h: f64,
    pi_diag: Option<PyReadonlyArray1<f64>>,
) -> PyResult<(Bound<'py, PyArray1<f64>>, f64)> {
    let pd = match pi_diag {
        Some(v) => to_a3(&v)?,
        None => [0.1, -0.04, -0.06],
    };
    let d = visc::route_b_damping_handset(h, &pd);
    Ok((
        Array1::from_vec(d.per_component.to_vec()).into_pyarray(py),
        d.mean,
    ))
}

/// 경로 B 소스 계수 — 계층 방정식만 사용 (구적은 ρ 규모용).
#[pyfunction]
#[pyo3(signature = (mass, a_vec = None, h = 1.0, sigma_diag = None))]
fn kin_route_b_source(
    py: Python<'_>,
    mass: f64,
    a_vec: Option<PyReadonlyArray1<f64>>,
    h: f64,
    sigma_diag: Option<PyReadonlyArray1<f64>>,
) -> PyResult<f64> {
    let a = match a_vec {
        Some(v) => to_a3(&v)?,
        None => [1.0, 1.0, 1.0],
    };
    let sd = match sigma_diag {
        Some(v) => to_a3(&v)?,
        None => [0.05, -0.02, -0.03],
    };
    Ok(py.detach(|| visc::route_b_source(mass, &a, h, &sd)))
}

/// 유도된 수송계수 — (eta, tau_pi, rho, damping_rate, source_coeff, eta·H/ρ).
#[pyfunction]
#[pyo3(signature = (mass, a_vec, h = 1.0, route = "hierarchy"))]
fn kin_transport_coefficients(
    py: Python<'_>,
    mass: f64,
    a_vec: PyReadonlyArray1<f64>,
    h: f64,
    route: &str,
) -> PyResult<(f64, f64, f64, f64, f64, f64)> {
    let a = to_a3(&a_vec)?;
    let hier = match route {
        "hierarchy" => true,
        "quadrature" => false,
        o => {
            return Err(PyValueError::new_err(format!(
                "unknown route '{o}' (expected 'hierarchy' or 'quadrature')"
            )))
        }
    };
    let t = py
        .detach(|| visc::transport_coefficients(mass, &a, h, hier))
        .ok_or_else(|| PyValueError::new_err("등방 a_vec 은 경로 B 감쇠율이 정의되지 않는다"))?;
    Ok((
        t.eta,
        t.tau_pi,
        t.rho,
        t.damping_rate,
        t.source_coeff,
        t.eta_over_rho_h,
    ))
}

/// ★ 두 경로 교차검증 — (감쇠 상대차, 소스 상대차, 일치 여부).
#[pyfunction]
#[pyo3(signature = (mass, a_vec = None, h = 1.0, tol_damp = 2e-3, tol_src = 5e-3))]
fn kin_cross_validate(
    py: Python<'_>,
    mass: f64,
    a_vec: Option<PyReadonlyArray1<f64>>,
    h: f64,
    tol_damp: f64,
    tol_src: f64,
) -> PyResult<(f64, f64, bool)> {
    let a = match a_vec {
        Some(v) => to_a3(&v)?,
        None => [1.0, 0.85, 1.18],
    };
    py.detach(|| visc::cross_validate(mass, &a, h, tol_damp, tol_src))
        .ok_or_else(|| PyValueError::new_err("등방 a_vec 은 교차검증 불가"))
}

/// Eckart 준정적 η (유도값) = ρ/(15H).
#[pyfunction]
fn kin_eckart_eta(rho: f64, h: f64) -> f64 {
    visc::eckart_eta_from_hierarchy(rho, h)
}

/// 무질량 IS 완화시간 (유도값) τ_π = 1/(4H).
#[pyfunction]
fn kin_relaxation_time(h: f64) -> f64 {
    visc::relaxation_time_massless(h)
}

// ─────────────────────────────── H5-e · tilted (boosted) 구적
/// J′^(i)_{A_l} — tilted 사틀 성분.  v=0 이면 `kin_j_moment` 와 비트-정확.
#[pyfunction]
#[pyo3(signature = (a_vec, v, mass, l, i, dipole_eps = 0.0, dipole_axis = 2))]
#[allow(clippy::too_many_arguments)]
fn kin_j_moment_tilted<'py>(
    py: Python<'py>,
    a_vec: PyReadonlyArray1<f64>,
    v: PyReadonlyArray1<f64>,
    mass: f64,
    l: usize,
    i: i32,
    dipole_eps: f64,
    dipole_axis: usize,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    check_l(l)?;
    let a = to_a3(&a_vec)?;
    let vv = to_a3(&v)?;
    if vv[0] * vv[0] + vv[1] * vv[1] + vv[2] * vv[2] >= 1.0 {
        return Err(PyValueError::new_err("|v| >= 1 은 물리적이지 않다"));
    }
    let out =
        py.detach(|| kinetic::quad::j_moment_tilted(&a, &vv, mass, l, i, dipole_eps, dipole_axis));
    Ok(Array1::from_vec(out).into_pyarray(py))
}

/// tilted 관측자의 (ρ′, p′, q′[3], π′[3,3]).
#[pyfunction]
fn kin_moments_tilted<'py>(
    py: Python<'py>,
    a_vec: PyReadonlyArray1<f64>,
    v: PyReadonlyArray1<f64>,
    mass: f64,
) -> PyResult<TiltedMomentsOutput<'py>> {
    let a = to_a3(&a_vec)?;
    let vv = to_a3(&v)?;
    if vv[0] * vv[0] + vv[1] * vv[1] + vv[2] * vv[2] >= 1.0 {
        return Err(PyValueError::new_err("|v| >= 1 은 물리적이지 않다"));
    }
    let (rho, p, q, pi) = py.detach(|| kinetic::quad::moments_tilted(&a, &vv, mass));
    Ok((
        rho,
        p,
        Array1::from_vec(q.to_vec()).into_pyarray(py),
        Array2::from_shape_fn((3, 3), |(i, j)| pi[i * 3 + j]).into_pyarray(py),
    ))
}

/// ★ boost 대수 자기검증: λ′² = E′² − m² 의 격자 전점 최대 상대잔차.
#[pyfunction]
fn kin_boost_shell_residual(
    py: Python<'_>,
    a_vec: PyReadonlyArray1<f64>,
    v: PyReadonlyArray1<f64>,
    mass: f64,
) -> PyResult<f64> {
    let a = to_a3(&a_vec)?;
    let vv = to_a3(&v)?;
    if vv[0] * vv[0] + vv[1] * vv[1] + vv[2] * vv[2] >= 1.0 {
        return Err(PyValueError::new_err("|v| >= 1 은 물리적이지 않다"));
    }
    Ok(py.detach(|| kinetic::quad::boost_shell_residual(&a, &vv, mass)))
}

// ─────────────────────────────── R1 · type V 결합 진화 (K5b/D2 병목)
#[inline]
fn to_nodes(p: &PyReadonlyArray2<f64>) -> PyResult<Vec<[f64; 3]>> {
    let v = p.as_array();
    if v.shape()[1] != 3 {
        return Err(PyValueError::new_err("P must be (N,3)"));
    }
    Ok((0..v.shape()[0])
        .map(|i| [v[[i, 0]], v[[i, 1]], v[[i, 2]]])
        .collect())
}

/// ★ (ρ, 3p, q, π) — 노드 융합 순회 (Python `moments_from_nodes` 의 포트).
#[pyfunction]
fn tv_moments<'py>(
    py: Python<'py>,
    p: PyReadonlyArray2<f64>,
    w: PyReadonlyArray1<f64>,
    a_vec: PyReadonlyArray1<f64>,
    mass: f64,
) -> PyResult<TiltedMomentsOutput<'py>> {
    let nodes = to_nodes(&p)?;
    let ws = w.as_slice()?.to_vec();
    let a = to_a3(&a_vec)?;
    let (rho, tp, q, pi) = py.detach(|| kinetic::typev::moments(&nodes, &ws, &a, mass));
    Ok((
        rho,
        tp,
        Array1::from_vec(q.to_vec()).into_pyarray(py),
        Array2::from_shape_fn((3, 3), |(i, j)| pi[i * 3 + j]).into_pyarray(py),
    ))
}

/// ★ (Ṗ, Ẇ) — 특성곡선 + Liouville 무게.
#[pyfunction]
fn tv_kinetic_rhs<'py>(
    py: Python<'py>,
    p: PyReadonlyArray2<f64>,
    w: PyReadonlyArray1<f64>,
    a_vec: PyReadonlyArray1<f64>,
    mass: f64,
    a_curv: f64,
) -> PyResult<Array2Array1Pair<'py>> {
    let nodes = to_nodes(&p)?;
    let ws = w.as_slice()?.to_vec();
    let a = to_a3(&a_vec)?;
    let n = nodes.len();
    let (dp, dw) = py.detach(|| {
        let mut dp = vec![[0.0f64; 3]; n];
        let mut dw = vec![0.0f64; n];
        kinetic::typev::kinetic_rhs(&nodes, &ws, &a, mass, a_curv, &mut dp, &mut dw);
        (dp, dw)
    });
    Ok((
        Array2::from_shape_fn((n, 3), |(i, j)| dp[i][j]).into_pyarray(py),
        Array1::from_vec(dw).into_pyarray(py),
    ))
}

/// ★ (q₁, 원천항) — D2b 운동량 법칙 검사 (유한차분 없이).
#[pyfunction]
fn tv_flux_rate(
    py: Python<'_>,
    p: PyReadonlyArray2<f64>,
    w: PyReadonlyArray1<f64>,
    a_vec: PyReadonlyArray1<f64>,
    mass: f64,
    a_curv: f64,
) -> PyResult<(f64, f64)> {
    let nodes = to_nodes(&p)?;
    let ws = w.as_slice()?.to_vec();
    let a = to_a3(&a_vec)?;
    Ok(py.detach(|| kinetic::typev::flux_rate(&nodes, &ws, &a, mass, a_curv)))
}

/// ★★ K5b 결합 진화 전체 — 노드가 Python 으로 되돌아오지 않는다.
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn tv_evolve<'py>(
    py: Python<'py>,
    p: PyReadonlyArray2<f64>,
    w: PyReadonlyArray1<f64>,
    a0: PyReadonlyArray1<f64>,
    da0: PyReadonlyArray1<f64>,
    mass: f64,
    a_curv: f64,
    t_end: f64,
    nsteps: usize,
    project: bool,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let nodes = to_nodes(&p)?;
    let ws = w.as_slice()?.to_vec();
    let a = to_a3(&a0)?;
    let da = to_a3(&da0)?;
    let r = py.detach(|| {
        kinetic::typev::evolve(
            &nodes,
            &ws,
            &a,
            &da,
            kinetic::typev::EvolutionConfig {
                mass,
                av: a_curv,
                t_end,
                nsteps,
                do_project: project,
            },
        )
    });
    let d = pyo3::types::PyDict::new(py);
    let n = r.t.len();
    let v3 = |src: &Vec<[f64; 3]>| Array2::from_shape_fn((n, 3), |(i, j)| src[i][j]);
    d.set_item("t", Array1::from_vec(r.t.clone()).into_pyarray(py))?;
    d.set_item("a", v3(&r.a).into_pyarray(py))?;
    d.set_item("h", v3(&r.h).into_pyarray(py))?;
    d.set_item("pi", v3(&r.pi).into_pyarray(py))?;
    d.set_item("sigma1", Array1::from_vec(r.sigma1).into_pyarray(py))?;
    d.set_item("rho", Array1::from_vec(r.rho).into_pyarray(py))?;
    d.set_item("q1", Array1::from_vec(r.q1).into_pyarray(py))?;
    d.set_item("friedmann", Array1::from_vec(r.friedmann).into_pyarray(py))?;
    d.set_item("codazzi", Array1::from_vec(r.codazzi).into_pyarray(py))?;
    d.set_item("offdiag", Array1::from_vec(r.offdiag).into_pyarray(py))?;
    d.set_item(
        "Hdot_spatial",
        Array1::from_vec(r.hdot_spatial).into_pyarray(py),
    )?;
    d.set_item("Hdot_ray", Array1::from_vec(r.hdot_ray).into_pyarray(py))?;
    d.set_item("qdot_node", Array1::from_vec(r.qdot_node).into_pyarray(py))?;
    d.set_item("qdot_law", Array1::from_vec(r.qdot_law).into_pyarray(py))?;
    d.set_item(
        "qdot_naive",
        Array1::from_vec(r.qdot_naive).into_pyarray(py),
    )?;
    Ok(d)
}

/// ★ R2 · 역방향 특성곡선 (K4b).
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn tv_back_trace<'py>(
    py: Python<'py>,
    p: PyReadonlyArray2<f64>,
    a0: PyReadonlyArray1<f64>,
    rate: PyReadonlyArray1<f64>,
    mass: f64,
    a_curv: f64,
    t: f64,
    nsteps: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let nodes = to_nodes(&p)?;
    let a = to_a3(&a0)?;
    let r = to_a3(&rate)?;
    let n = nodes.len();
    let out = py.detach(|| kinetic::typev::back_trace(&nodes, &a, &r, mass, a_curv, t, nsteps));
    Ok(Array2::from_shape_fn((n, 3), |(i, j)| out[i][j]).into_pyarray(py))
}

/// ★ R2 · 순방향 Liouville 밀기 (K5b).
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn tv_push_nodes<'py>(
    py: Python<'py>,
    p: PyReadonlyArray2<f64>,
    w: PyReadonlyArray1<f64>,
    a0: PyReadonlyArray1<f64>,
    rate: PyReadonlyArray1<f64>,
    mass: f64,
    a_curv: f64,
    t: f64,
    nsteps: usize,
    measure: bool,
) -> PyResult<Array2Array1Pair<'py>> {
    let nodes = to_nodes(&p)?;
    let ws = w.as_slice()?.to_vec();
    let a = to_a3(&a0)?;
    let r = to_a3(&rate)?;
    let n = nodes.len();
    let (pp, ww) = py.detach(|| {
        kinetic::typev::push_nodes(
            &nodes,
            &ws,
            &a,
            &r,
            kinetic::typev::PushConfig {
                mass,
                av: a_curv,
                t,
                nsteps,
                measure,
            },
        )
    });
    Ok((
        Array2::from_shape_fn((n, 3), |(i, j)| pp[i][j]).into_pyarray(py),
        Array1::from_vec(ww).into_pyarray(py),
    ))
}

// ─────────────────────────────── R4 · Mixmaster 튐 수열 (한 번의 적분)
/// ★★ 세 벽을 동시에 감시하며 튐 수열을 낸다.
///
/// 반환 (tau[K], wall[K], u[K], tau_epoch[K], max_n[K], omega[K]).
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn mx_bounce_sequence<'py>(
    py: Python<'py>,
    y0: PyReadonlyArray1<f64>,
    gamma: f64,
    n_bounce: usize,
    tau_max: f64,
    rtol: f64,
    atol: f64,
    h0: f64,
) -> PyResult<BounceSequenceOutput<'py>> {
    let s = y0.as_slice()?;
    if s.len() != 5 {
        return Err(PyValueError::new_err("y0 must have length 5"));
    }
    let y = [s[0], s[1], s[2], s[3], s[4]];
    let b =
        py.detach(|| ode::mixmaster::bounce_sequence(&y, gamma, n_bounce, tau_max, rtol, atol, h0));
    Ok((
        Array1::from_vec(b.iter().map(|x| x.tau).collect()).into_pyarray(py),
        Array1::from_vec(b.iter().map(|x| x.wall as i64).collect()).into_pyarray(py),
        Array1::from_vec(b.iter().map(|x| x.u).collect()).into_pyarray(py),
        Array1::from_vec(b.iter().map(|x| x.tau_epoch).collect()).into_pyarray(py),
        Array1::from_vec(b.iter().map(|x| x.max_n).collect()).into_pyarray(py),
        Array1::from_vec(b.iter().map(|x| x.omega).collect()).into_pyarray(py),
    ))
}

/// ★★ D3 · 로그-벽 튐 수열 — y0 = [Σ₊, Σ₋, w₁, w₂, w₃], w = ln|N|.
///
/// max_n 열은 **로그값** (max w) 이다 — 선형판과 달리 언더플로 없이 깊이를 보고한다.
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn mx_bounce_sequence_log<'py>(
    py: Python<'py>,
    y0: PyReadonlyArray1<f64>,
    signs: PyReadonlyArray1<f64>,
    gamma: f64,
    n_bounce: usize,
    tau_max: f64,
    rtol: f64,
    atol: f64,
    h0: f64,
) -> PyResult<BounceSequenceOutput<'py>> {
    let s = y0.as_slice()?;
    let sg = signs.as_slice()?;
    if s.len() != 5 || sg.len() != 3 {
        return Err(PyValueError::new_err("y0 length 5, signs length 3"));
    }
    let y = [s[0], s[1], s[2], s[3], s[4]];
    let g = [sg[0], sg[1], sg[2]];
    let b = py.detach(|| {
        ode::mixmaster::bounce_sequence_log(&y, &g, gamma, n_bounce, tau_max, rtol, atol, h0)
    });
    Ok((
        Array1::from_vec(b.iter().map(|x| x.tau).collect()).into_pyarray(py),
        Array1::from_vec(b.iter().map(|x| x.wall as i64).collect()).into_pyarray(py),
        Array1::from_vec(b.iter().map(|x| x.u).collect()).into_pyarray(py),
        Array1::from_vec(b.iter().map(|x| x.tau_epoch).collect()).into_pyarray(py),
        Array1::from_vec(b.iter().map(|x| x.max_n).collect()).into_pyarray(py),
        Array1::from_vec(b.iter().map(|x| x.omega).collect()).into_pyarray(py),
    ))
}

// ─────────────────────────────── R5a · 일반 rank tilted 텐서 커널
fn to_geo(
    eup: &PyReadonlyArray2<f64>,
    edn: &PyReadonlyArray2<f64>,
    deup: &PyReadonlyArray2<f64>,
    hmix: &PyReadonlyArray2<f64>,
    uup: &PyReadonlyArray1<f64>,
    gam: &PyReadonlyArray3<f64>,
) -> PyResult<kinetic::tilted_terms::Geo> {
    let mut g = kinetic::tilted_terms::Geo {
        eup: [0.0; 12],
        edn: [0.0; 12],
        deup: [0.0; 12],
        hmix: [0.0; 16],
        uup: [0.0; 4],
        gam: [0.0; 64],
    };
    let (e, d, de, h, u, gm) = (
        eup.as_array(),
        edn.as_array(),
        deup.as_array(),
        hmix.as_array(),
        uup.as_slice()?,
        gam.as_array(),
    );
    if e.shape() != [3, 4] || h.shape() != [4, 4] || gm.shape() != [4, 4, 4] || u.len() != 4 {
        return Err(PyValueError::new_err(
            "geo shapes: eup/edn/deup (3,4), hmix (4,4), uup (4,), G (4,4,4)",
        ));
    }
    for a in 0..3 {
        for m in 0..4 {
            g.eup[a * 4 + m] = e[[a, m]];
            g.edn[a * 4 + m] = d[[a, m]];
            g.deup[a * 4 + m] = de[[a, m]];
        }
    }
    for m in 0..4 {
        g.uup[m] = u[m];
        for n in 0..4 {
            g.hmix[m * 4 + n] = h[[m, n]];
            for r in 0..4 {
                g.gam[m * 16 + n * 4 + r] = gm[[m, n, r]];
            }
        }
    }
    Ok(g)
}

macro_rules! tilted_fn {
    ($name:ident, $call:path, $rank_out:expr) => {
        #[pyfunction]
        #[allow(clippy::too_many_arguments)]
        fn $name<'py>(
            py: Python<'py>,
            x: PyReadonlyArray1<f64>,
            dx: PyReadonlyArray1<f64>,
            r: usize,
            eup: PyReadonlyArray2<f64>,
            edn: PyReadonlyArray2<f64>,
            deup: PyReadonlyArray2<f64>,
            hmix: PyReadonlyArray2<f64>,
            uup: PyReadonlyArray1<f64>,
            gam: PyReadonlyArray3<f64>,
        ) -> PyResult<Bound<'py, PyArray1<f64>>> {
            let g = to_geo(&eup, &edn, &deup, &hmix, &uup, &gam)?;
            let xs = x.as_slice()?.to_vec();
            let ds = dx.as_slice()?.to_vec();
            let _ = $rank_out;
            let out = py.detach(|| $call(&xs, &ds, r, &g));
            Ok(Array1::from_vec(out).into_pyarray(py))
        }
    };
}

tilted_fn!(tt_perp_dot, kinetic::tilted_terms::perp_dot, 0);
tilted_fn!(
    tt_spatial_derivative,
    kinetic::tilted_terms::spatial_derivative,
    1
);
tilted_fn!(tt_div_contracted, kinetic::tilted_terms::div_contracted, -1);
tilted_fn!(tt_div_free_raw, kinetic::tilted_terms::div_free_raw, 1);

// ─────────────────────────────── R5b · tilted 계층 전체 (좌변 + 질량행렬 + RK4)
//
// 기하 한 시각을 **평탄 142 벡터**로 받는다 (Python `bianchi.matter.tilted_rust` 가 싼다):
//   [0..12) eup  [12..24) edn  [24..36) deup  [36..52) hmix  [52..56) uup
//   [56..120) Γ  [120] H  [121..130) σ  [130..139) ω  [139..142) u̇
const TH_GEO_LEN: usize = 142;

fn th_geo(row: &[f64]) -> PyResult<kinetic::tilted_hier::HGeo> {
    if row.len() != TH_GEO_LEN {
        return Err(PyValueError::new_err(format!(
            "geo row must be {TH_GEO_LEN} long, got {}",
            row.len()
        )));
    }
    let mut g = kinetic::tilted_terms::Geo {
        eup: [0.0; 12],
        edn: [0.0; 12],
        deup: [0.0; 12],
        hmix: [0.0; 16],
        uup: [0.0; 4],
        gam: [0.0; 64],
    };
    g.eup.copy_from_slice(&row[0..12]);
    g.edn.copy_from_slice(&row[12..24]);
    g.deup.copy_from_slice(&row[24..36]);
    g.hmix.copy_from_slice(&row[36..52]);
    g.uup.copy_from_slice(&row[52..56]);
    g.gam.copy_from_slice(&row[56..120]);
    let mut h = kinetic::tilted_hier::HGeo {
        base: g,
        h: row[120],
        sigma: [0.0; 9],
        omega: [0.0; 9],
        udot: [0.0; 3],
        gamma: 1.0,
        v: [0.0; 3],
    };
    h.sigma.copy_from_slice(&row[121..130]);
    h.omega.copy_from_slice(&row[130..139]);
    h.udot.copy_from_slice(&row[139..142]);
    Ok(h.finish())
}

fn th_geos(geos: &PyReadonlyArray2<f64>) -> PyResult<Vec<kinetic::tilted_hier::HGeo>> {
    let a = geos.as_array();
    if a.shape()[1] != TH_GEO_LEN {
        return Err(PyValueError::new_err(format!(
            "geo rows must be {TH_GEO_LEN} long, got {}",
            a.shape()[1]
        )));
    }
    (0..a.shape()[0])
        .map(|k| {
            let row: Vec<f64> = (0..TH_GEO_LEN).map(|c| a[[k, c]]).collect();
            th_geo(&row)
        })
        .collect()
}

/// 닫힘 설정: `mode_code` 는 `tilted_closure.MODES` 순서, `n_star < 0` 이면 없음.
fn th_closure(
    mode_code: usize,
    jdot: bool,
    n_star: i32,
) -> PyResult<kinetic::tilted_hier::Closure> {
    let mode = kinetic::tilted_hier::Mode::from_code(mode_code)
        .ok_or_else(|| PyValueError::new_err(format!("unknown mode code {mode_code}")))?;
    Ok(kinetic::tilted_hier::Closure {
        mode,
        jdot,
        n_star: if n_star < 0 { None } else { Some(n_star) },
    })
}

fn th_signs(s: &PyReadonlyArray1<f64>) -> PyResult<kinetic::tilted_hier::Signs> {
    let v = s.as_slice()?;
    if v.len() != 8 {
        return Err(PyValueError::new_err(
            "signs must be [A, B, C, D, E, Omega, divcon, divfree]",
        ));
    }
    Ok(kinetic::tilted_hier::Signs {
        a: v[0],
        b: v[1],
        c: v[2],
        d: v[3],
        e: v[4],
        omega: v[5],
        divcon: v[6],
        divfree: v[7],
    })
}

fn th_mats(v: &[PyReadonlyArray1<f64>]) -> PyResult<Vec<Vec<f64>>> {
    v.iter().map(|x| Ok(x.as_slice()?.to_vec())).collect()
}

/// ★ V16 적대적 감사 수확: ops/bases 가 l_max 보다 짧으면 `pstf`/`to_coef` 의
///   `ops[l]` 인덱싱이 **Rust 패닉**으로 FFI 를 넘었다 (PanicException + 백트레이스).
///   R2 의 `check_l` 과 같은 관례로 경계에서 ValueError 로 막는다.
fn th_check(ops: &[Vec<f64>], bases: &[Vec<f64>], l_max: usize) -> PyResult<()> {
    if ops.len() < l_max + 1 || bases.len() < l_max + 1 {
        return Err(PyValueError::new_err(format!(
            "ops/bases must have l_max+1 = {} entries (got {}, {})",
            l_max + 1,
            ops.len(),
            bases.len()
        )));
    }
    for l in 0..=l_max {
        let d = 3usize.pow(l as u32);
        if l >= 2 && ops[l].len() != d * d {
            return Err(PyValueError::new_err(format!(
                "ops[{l}] must be flat ({d},{d}), got {}",
                ops[l].len()
            )));
        }
        if bases[l].len() != d * (2 * l + 1) {
            return Err(PyValueError::new_err(format!(
                "bases[{l}] must be flat ({d},{}), got {}",
                2 * l + 1,
                bases[l].len()
            )));
        }
    }
    Ok(())
}

/// tilted 계층 RK4 적분 — 반환 (nsteps+1, state_len) 이력.
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn th_integrate<'py>(
    py: Python<'py>,
    j0: PyReadonlyArray1<f64>,
    geos: PyReadonlyArray2<f64>,
    nsteps: usize,
    dt: f64,
    signs: PyReadonlyArray1<f64>,
    ops: Vec<PyReadonlyArray1<f64>>,
    bases: Vec<PyReadonlyArray1<f64>>,
    l_max: usize,
    i_max: usize,
    mode_code: usize,
    jdot: bool,
    n_star: i32,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let cl = th_closure(mode_code, jdot, n_star)?;
    let n = kinetic::tilted_hier::Grid::state_len(l_max, i_max);
    let flat = j0.as_slice()?;
    if flat.len() != n {
        return Err(PyValueError::new_err(format!("j0 must be {n} long")));
    }
    let g = th_geos(&geos)?;
    if g.len() != 3 * nsteps {
        return Err(PyValueError::new_err("geos must hold 3 rows per step"));
    }
    let (s, o, b) = (th_signs(&signs)?, th_mats(&ops)?, th_mats(&bases)?);
    th_check(&o, &b, l_max)?;
    let grid = kinetic::tilted_hier::Grid::from_state(l_max, i_max, flat);
    let hist = py.detach(|| kinetic::tilted_hier::integrate(&grid, &g, nsteps, dt, &s, &o, &b, cl));
    Ok(Array2::from_shape_vec((nsteps + 1, n), hist)
        .map_err(|e| PyValueError::new_err(e.to_string()))?
        .into_pyarray(py))
}

/// 한 스텝의 J̇ (평탄 상태벡터) — 차등시험용.
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn th_rhs<'py>(
    py: Python<'py>,
    j0: PyReadonlyArray1<f64>,
    geo: PyReadonlyArray1<f64>,
    signs: PyReadonlyArray1<f64>,
    ops: Vec<PyReadonlyArray1<f64>>,
    bases: Vec<PyReadonlyArray1<f64>>,
    l_max: usize,
    i_max: usize,
    mode_code: usize,
    jdot: bool,
    n_star: i32,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let cl = th_closure(mode_code, jdot, n_star)?;
    let (s, o, b) = (th_signs(&signs)?, th_mats(&ops)?, th_mats(&bases)?);
    th_check(&o, &b, l_max)?;
    let g = th_geo(geo.as_slice()?)?;
    let nst = kinetic::tilted_hier::Grid::state_len(l_max, i_max);
    if j0.as_slice()?.len() != nst {
        return Err(PyValueError::new_err(format!("j0 must be {nst} long")));
    }
    let grid = kinetic::tilted_hier::Grid::from_state(l_max, i_max, j0.as_slice()?);
    let out = py.detach(|| kinetic::tilted_hier::rhs(&grid, &g, &s, &o, &b, cl));
    let mut flat = Vec::new();
    out.flatten_state(&mut flat);
    Ok(Array1::from_vec(flat).into_pyarray(py))
}

/// 한 스텝의 (F, M) — 포트가 **어디까지** Python 과 같은지 가리는 진단.
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn th_force_and_matrix<'py>(
    py: Python<'py>,
    j0: PyReadonlyArray1<f64>,
    geo: PyReadonlyArray1<f64>,
    signs: PyReadonlyArray1<f64>,
    ops: Vec<PyReadonlyArray1<f64>>,
    bases: Vec<PyReadonlyArray1<f64>>,
    l_max: usize,
    i_max: usize,
    mode_code: usize,
    jdot: bool,
    n_star: i32,
) -> PyResult<Array1Pair<'py>> {
    let cl = th_closure(mode_code, jdot, n_star)?;
    let (s, o, b) = (th_signs(&signs)?, th_mats(&ops)?, th_mats(&bases)?);
    th_check(&o, &b, l_max)?;
    let g = th_geo(geo.as_slice()?)?;
    let nst = kinetic::tilted_hier::Grid::state_len(l_max, i_max);
    if j0.as_slice()?.len() != nst {
        return Err(PyValueError::new_err(format!("j0 must be {nst} long")));
    }
    let grid = kinetic::tilted_hier::Grid::from_state(l_max, i_max, j0.as_slice()?);
    let (f, m) = py.detach(|| kinetic::tilted_hier::force_and_matrix(&grid, &g, &s, &o, &b, cl));
    Ok((
        Array1::from_vec(f).into_pyarray(py),
        Array1::from_vec(m).into_pyarray(py),
    ))
}

// ═══════════════════════════════ J3 · 계수공간 계층 커널 바인딩
/// tilted 좌변 전 격자 1호출.  signs = [A,B,C,D,E,Ω,divcon,divfree].
/// 격자 팩킹·패딩 규약은 `kinetic::coeff_hier` 문서 참조 (l_pad=l_max+2 등).
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn coeff_lhs_grid<'py>(
    py: Python<'py>,
    j: PyReadonlyArray1<f64>,
    dj: PyReadonlyArray1<f64>,
    l_max: usize,
    i_max: usize,
    h: f64,
    s5: PyReadonlyArray1<f64>,
    w: PyReadonlyArray1<f64>,
    u3: PyReadonlyArray1<f64>,
    gamma: f64,
    v3: PyReadonlyArray1<f64>,
    c_pd: PyReadonlyArray1<f64>,
    c_dc: PyReadonlyArray1<f64>,
    c_df: PyReadonlyArray1<f64>,
    signs: PyReadonlyArray1<f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    if l_max > kinetic::coeff_tables::L_KERNEL_MAX {
        return Err(PyValueError::new_err(format!(
            "coeff 커널 벽: l_max ≤ {} (c2 표 l_in=l+2 ≤ 12)",
            kinetic::coeff_tables::L_KERNEL_MAX
        )));
    }
    let need = kinetic::coeff_hier::grid_len(l_max + 2, i_max + 2);
    if j.len()? != need || dj.len()? != need {
        return Err(PyValueError::new_err(format!(
            "격자 길이 {} 필요 (l_pad=l_max+2, i_pad=i_max+2 패딩)",
            need
        )));
    }
    for (name, arr, n) in [
        ("s5", &s5, 5),
        ("w", &w, 3),
        ("u3", &u3, 3),
        ("v3", &v3, 3),
        ("c_pd", &c_pd, 9),
        ("c_dc", &c_dc, 12),
        ("c_df", &c_df, 12),
        ("signs", &signs, 8),
    ] {
        if arr.len()? != n {
            return Err(PyValueError::new_err(format!("{name}: 길이 {n} 필요")));
        }
    }
    let (jv, djv) = (j.as_slice()?.to_vec(), dj.as_slice()?.to_vec());
    let (s5v, wv, u3v, v3v) = (
        s5.as_slice()?.to_vec(),
        w.as_slice()?.to_vec(),
        u3.as_slice()?.to_vec(),
        v3.as_slice()?.to_vec(),
    );
    let (cp, cc, cf, sg) = (
        c_pd.as_slice()?.to_vec(),
        c_dc.as_slice()?.to_vec(),
        c_df.as_slice()?.to_vec(),
        signs.as_slice()?.to_vec(),
    );
    let out = py.detach(|| {
        kinetic::coeff_hier::lhs_grid(
            &jv, &djv, l_max, i_max, h, &s5v, &wv, &u3v, gamma, &v3v, &cp, &cc, &cf, &sg,
        )
    });
    Ok(Array1::from_vec(out).into_pyarray(py))
}

/// 질량블록 (γI, up, down) — down 은 l=0 에서 None.
#[pyfunction]
fn coeff_mass_blocks<'py>(
    py: Python<'py>,
    l: usize,
    gamma: f64,
    v3: PyReadonlyArray1<f64>,
    s_dc: f64,
    s_df: f64,
) -> PyResult<MassBlocksOutput<'py>> {
    // cv 표는 l_out 인덱스 (l_in=l+1 제약은 생성범위에 이미 구움) — 벽은 l ≤ 11.
    if l > kinetic::coeff_tables::CV_MAX_L {
        return Err(PyValueError::new_err(format!(
            "질량블록: cv 표 벽 (l ≤ {})",
            kinetic::coeff_tables::CV_MAX_L
        )));
    }
    if v3.len()? != 3 {
        return Err(PyValueError::new_err("v3: 길이 3 필요"));
    }
    let v3v = v3.as_slice()?.to_vec();
    let (diag, up, down) =
        py.detach(|| kinetic::coeff_hier::mass_blocks(l, gamma, &v3v, s_dc, s_df));
    let n = 2 * l + 1;
    let d2 =
        Array2::from_shape_vec((n, n), diag).map_err(|e| PyValueError::new_err(e.to_string()))?;
    let u2 =
        Array2::from_shape_vec((n, n + 2), up).map_err(|e| PyValueError::new_err(e.to_string()))?;
    let dn = if down.is_empty() {
        None
    } else {
        Some(
            Array2::from_shape_vec((n, n - 2), down)
                .map_err(|e| PyValueError::new_err(e.to_string()))?
                .into_pyarray(py),
        )
    };
    Ok((d2.into_pyarray(py), u2.into_pyarray(py), dn))
}

/// untilted RHS 전 격자 1호출.  signs = [A,B,C].
#[pyfunction]
fn coeff_rhs_grid<'py>(
    py: Python<'py>,
    j: PyReadonlyArray1<f64>,
    l_max: usize,
    i_max: usize,
    h: f64,
    s5: PyReadonlyArray1<f64>,
    signs: PyReadonlyArray1<f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    if l_max > kinetic::coeff_tables::L_KERNEL_MAX {
        return Err(PyValueError::new_err("coeff 커널 벽: l_max ≤ 10"));
    }
    let need = kinetic::coeff_hier::grid_len(l_max + 2, i_max + 2);
    if j.len()? != need {
        return Err(PyValueError::new_err(format!("격자 길이 {} 필요", need)));
    }
    if s5.len()? != 5 || signs.len()? != 3 {
        return Err(PyValueError::new_err("s5 길이 5, signs 길이 3 필요"));
    }
    let jv = j.as_slice()?.to_vec();
    let (s5v, sg) = (s5.as_slice()?.to_vec(), signs.as_slice()?.to_vec());
    let out = py.detach(|| kinetic::coeff_hier::rhs_grid(&jv, l_max, i_max, h, &s5v, &sg));
    Ok(Array1::from_vec(out).into_pyarray(py))
}

// ═══════════════════════════════ I3 · 결합 루프 바인딩
/// 결합 RHS 1회 (차등시험용).  u1(9), u2(45) = Python U_basis 캐리.
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn cp_rhs<'py>(
    py: Python<'py>,
    y: PyReadonlyArray1<f64>,
    gammas: PyReadonlyArray1<f64>,
    kappa: Option<PyReadonlyArray1<f64>>,
    l_max: usize,
    nterm_on: bool,
    u1: PyReadonlyArray1<f64>,
    u2: PyReadonlyArray1<f64>,
    sigma_signs: PyReadonlyArray1<f64>,
    nu_bgk: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    if u1.len()? != 9 || u2.len()? != 45 || sigma_signs.len()? != 3 {
        return Err(PyValueError::new_err("u1(9)/u2(45)/signs(3) 길이"));
    }
    let yv = y.as_slice()?.to_vec();
    let g = gammas.as_slice()?.to_vec();
    let kv = match &kappa {
        Some(k) => Some(k.as_slice()?.to_vec()),
        None => None,
    };
    let u1v = u1.as_slice()?.to_vec();
    let u2v = u2.as_slice()?.to_vec();
    let sg = sigma_signs.as_slice()?;
    let sgn = [sg[0], sg[1], sg[2]];
    let out = py.detach(|| {
        kinetic::coupled::coupled_rhs(
            &yv,
            &g,
            kv.as_deref(),
            l_max,
            nterm_on,
            &u1v,
            &u2v,
            &sgn,
            nu_bgk,
        )
    });
    Ok(Array1::from_vec(out).into_pyarray(py))
}

/// 결합 RK4 루프째 — (최종상태, keep 시 궤적 (nsteps+1, dim)).
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn cp_evolve<'py>(
    py: Python<'py>,
    y0: PyReadonlyArray1<f64>,
    gammas: PyReadonlyArray1<f64>,
    kappa: Option<PyReadonlyArray1<f64>>,
    l_max: usize,
    tau: f64,
    nsteps: usize,
    nterm_on: bool,
    keep: bool,
    u1: PyReadonlyArray1<f64>,
    u2: PyReadonlyArray1<f64>,
    sigma_signs: PyReadonlyArray1<f64>,
    nu_bgk: f64,
) -> PyResult<CoupledEvolutionOutput<'py>> {
    if u1.len()? != 9 || u2.len()? != 45 || sigma_signs.len()? != 3 {
        return Err(PyValueError::new_err("u1(9)/u2(45)/signs(3) 길이"));
    }
    let yv = y0.as_slice()?.to_vec();
    let dim = yv.len();
    let g = gammas.as_slice()?.to_vec();
    let kv = match &kappa {
        Some(k) => Some(k.as_slice()?.to_vec()),
        None => None,
    };
    let u1v = u1.as_slice()?.to_vec();
    let u2v = u2.as_slice()?.to_vec();
    let sg = sigma_signs.as_slice()?;
    let sgn = [sg[0], sg[1], sg[2]];
    let (yt, traj) = py.detach(|| {
        kinetic::coupled::rk4_evolve(
            &yv,
            &g,
            kv.as_deref(),
            l_max,
            tau,
            nsteps,
            nterm_on,
            keep,
            &u1v,
            &u2v,
            &sgn,
            nu_bgk,
        )
    });
    let t2 = if keep {
        Some(
            Array2::from_shape_vec((nsteps + 1, dim), traj)
                .map_err(|e| PyValueError::new_err(e.to_string()))?
                .into_pyarray(py),
        )
    } else {
        None
    };
    Ok((Array1::from_vec(yt).into_pyarray(py), t2))
}

// ═══════════════════════════════ G1b · 격자 충돌 커널 바인딩
/// Thomson 물리핵 (Sinkhorn 보존형) — (n,n) 반환.
#[pyfunction]
fn gc_thomson<'py>(
    py: Python<'py>,
    ehat: PyReadonlyArray2<f64>,
    w: PyReadonlyArray1<f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let n = w.len()?;
    if ehat.as_array().shape() != [n, 3] {
        return Err(PyValueError::new_err("ehat: (n,3) 필요"));
    }
    let e = ehat.as_slice()?.to_vec();
    let wv = w.as_slice()?.to_vec();
    let k = py.detach(|| kinetic::grid_collide::build_thomson(&e, &wv, 400, 1e-15));
    Ok(Array2::from_shape_vec((n, n), k)
        .map_err(|x| PyValueError::new_err(x.to_string()))?
        .into_pyarray(py))
}

/// exp(ν dt (K−I))·g — 테일러 (eigh 없음).
#[pyfunction]
fn gc_expm_apply<'py>(
    py: Python<'py>,
    k: PyReadonlyArray2<f64>,
    g: PyReadonlyArray1<f64>,
    nu_dt: f64,
    tol: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let n = g.len()?;
    if k.as_array().shape() != [n, n] {
        return Err(PyValueError::new_err("K: (n,n) 필요"));
    }
    let kv = k.as_slice()?.to_vec();
    let gv = g.as_slice()?.to_vec();
    let out = py.detach(|| kinetic::grid_collide::expm_apply(&kv, &gv, nu_dt, tol, 64));
    Ok(Array1::from_vec(out).into_pyarray(py))
}

/// Strang 루프째 — ehat_seq (nsteps+1, n, 3), w_seq/mu_seq (nsteps+1, n).
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn gc_strang<'py>(
    py: Python<'py>,
    g0: PyReadonlyArray1<f64>,
    ehat_seq: PyReadonlyArray3<f64>,
    w_seq: PyReadonlyArray2<f64>,
    mu_seq: PyReadonlyArray2<f64>,
    nsteps: usize,
    nu: f64,
    h: f64,
    n_pow: i32,
    tol: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let n = g0.len()?;
    if ehat_seq.as_array().shape() != [nsteps + 1, n, 3]
        || w_seq.as_array().shape() != [nsteps + 1, n]
        || mu_seq.as_array().shape() != [nsteps + 1, n]
    {
        return Err(PyValueError::new_err("시퀀스 형상 (nsteps+1, n[,3])"));
    }
    let gv = g0.as_slice()?.to_vec();
    let e = ehat_seq.as_slice()?.to_vec();
    let wv = w_seq.as_slice()?.to_vec();
    let mv = mu_seq.as_slice()?.to_vec();
    let out = py.detach(|| {
        kinetic::grid_collide::strang_evolve(&gv, &e, &wv, &mv, nsteps, nu, h, n_pow, tol)
    });
    Ok(Array1::from_vec(out).into_pyarray(py))
}

// ═══════════════════════════════ Q1 · 11유형 통합 군 코어 바인딩
use crate::geom::group as qgroup;

fn _grp(n: &PyReadonlyArray1<f64>, a: &PyReadonlyArray1<f64>) -> PyResult<qgroup::BianchiGroup> {
    let ns = n.as_slice()?;
    let as_ = a.as_slice()?;
    if ns.len() != 6 || as_.len() != 3 {
        return Err(PyValueError::new_err(
            "n 은 6성분 (11,22,33,12,13,23), a 는 3성분",
        ));
    }
    Ok(qgroup::BianchiGroup::new(
        [ns[0], ns[1], ns[2], ns[3], ns[4], ns[5]],
        [as_[0], as_[1], as_[2]],
    ))
}

/// 유형 분류 → (name, class, kappa|None, exceptional, signature3, a_sign).
#[pyfunction]
fn qg_classify(
    n: PyReadonlyArray1<f64>,
    a: PyReadonlyArray1<f64>,
) -> PyResult<GroupClassificationOutput> {
    let g = _grp(&n, &a)?;
    let c = g.classify();
    let cls = match c.class {
        qgroup::GroupClass::A => "A",
        qgroup::GroupClass::B => "B",
    };
    Ok((
        c.name.to_string(),
        cls.to_string(),
        c.kappa,
        c.exceptional,
        (c.signature.0[0], c.signature.0[1], c.signature.0[2]),
        c.signature.1,
    ))
}

/// Jacobi 잔차 n^{ab} a_b.
#[pyfunction]
fn qg_jacobi<'py>(
    py: Python<'py>,
    n: PyReadonlyArray1<f64>,
    a: PyReadonlyArray1<f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let g = _grp(&n, &a)?;
    Ok(Array1::from_vec(g.jacobi_residual().to_vec()).into_pyarray(py))
}

/// C^c_{ab} — (3,3,3) 평탄화 (인덱스 c*9 + a*3 + b).
#[pyfunction]
fn qg_structure_constants<'py>(
    py: Python<'py>,
    n: PyReadonlyArray1<f64>,
    a: PyReadonlyArray1<f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let g = _grp(&n, &a)?;
    let c = g.structure_constants();
    let mut v = Vec::with_capacity(27);
    for plane in &c {
        for row in plane {
            v.extend_from_slice(row);
        }
    }
    Ok(Array1::from_vec(v).into_pyarray(py))
}

/// 3D Ricci (3,3) 평탄화.
#[pyfunction]
fn qg_ricci3<'py>(
    py: Python<'py>,
    n: PyReadonlyArray1<f64>,
    a: PyReadonlyArray1<f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let g = _grp(&n, &a)?;
    let r = g.ricci3();
    let mut v = Vec::with_capacity(9);
    for i in 0..3 {
        for j in 0..3 {
            v.push(r[(i, j)]);
        }
    }
    Ok(Array1::from_vec(v).into_pyarray(py))
}

/// (K, ^3S_ab 평탄화 9성분) — 총 10성분.
#[pyfunction]
fn qg_curvature<'py>(
    py: Python<'py>,
    n: PyReadonlyArray1<f64>,
    a: PyReadonlyArray1<f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let g = _grp(&n, &a)?;
    let (k, s3) = g.curvature();
    let mut v = Vec::with_capacity(10);
    v.push(k);
    for i in 0..3 {
        for j in 0..3 {
            v.push(s3[(i, j)]);
        }
    }
    Ok(Array1::from_vec(v).into_pyarray(py))
}

/// kappa = (1/2)[(tr N)^2 - tr(N^2)] / (A.A);  class A 는 None.
#[pyfunction]
fn qg_kappa(n: PyReadonlyArray1<f64>, a: PyReadonlyArray1<f64>) -> PyResult<Option<f64>> {
    Ok(_grp(&n, &a)?.kappa())
}

// ═══════════════════════════════ Q2 · 특성곡선 커널 바인딩
use crate::kinetic::characteristics as qchar;

fn _bg(
    h: f64,
    sigma: &PyReadonlyArray1<f64>,
    rot: &PyReadonlyArray1<f64>,
    n: &PyReadonlyArray1<f64>,
    a: &PyReadonlyArray1<f64>,
) -> PyResult<qchar::Background> {
    let s = sigma.as_slice()?;
    let r = rot.as_slice()?;
    let nn = n.as_slice()?;
    let aa = a.as_slice()?;
    if s.len() != 6 || nn.len() != 6 || r.len() != 3 || aa.len() != 3 {
        return Err(PyValueError::new_err("sigma·n 은 6성분, rot·a 는 3성분"));
    }
    Ok(qchar::Background {
        h,
        sigma: [s[0], s[1], s[2], s[3], s[4], s[5]],
        rot: [r[0], r[1], r[2]],
        n: [nn[0], nn[1], nn[2], nn[3], nn[4], nn[5]],
        a: [aa[0], aa[1], aa[2]],
    })
}

/// dp̂/dt (공변형).  phat (3,) → (3,).
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn qc_rhs_p<'py>(
    py: Python<'py>,
    phat: PyReadonlyArray1<f64>,
    mass: f64,
    h: f64,
    sigma: PyReadonlyArray1<f64>,
    rot: PyReadonlyArray1<f64>,
    n: PyReadonlyArray1<f64>,
    a: PyReadonlyArray1<f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let bg = _bg(h, &sigma, &rot, &n, &a)?;
    let p = phat.as_slice()?;
    if p.len() != 3 {
        return Err(PyValueError::new_err("phat 은 3성분"));
    }
    let out = qchar::char_rhs_p(&[p[0], p[1], p[2]], mass, &bg);
    Ok(Array1::from_vec(out.to_vec()).into_pyarray(py))
}

/// (dê/dt, dln p/dt) 분해형 → 4성분 [de0,de1,de2,dlnp].
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn qc_rhs_split<'py>(
    py: Python<'py>,
    ehat: PyReadonlyArray1<f64>,
    lnp: f64,
    mass: f64,
    h: f64,
    sigma: PyReadonlyArray1<f64>,
    rot: PyReadonlyArray1<f64>,
    n: PyReadonlyArray1<f64>,
    a: PyReadonlyArray1<f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let bg = _bg(h, &sigma, &rot, &n, &a)?;
    let e = ehat.as_slice()?;
    if e.len() != 3 {
        return Err(PyValueError::new_err("ehat 은 3성분"));
    }
    let (de, dl) = qchar::char_rhs_split(&[e[0], e[1], e[2]], lnp, mass, &bg);
    Ok(Array1::from_vec(vec![de[0], de[1], de[2], dl]).into_pyarray(py))
}

/// 방향격자 전체를 dt 만큼 (역)추적 → (ê_out 3M, dln p M) 을 이어붙인 4M 벡터.
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn qc_direction_map<'py>(
    py: Python<'py>,
    ehat: PyReadonlyArray1<f64>,
    mass: f64,
    lnp: f64,
    h0: f64,
    s0: PyReadonlyArray1<f64>,
    r0: PyReadonlyArray1<f64>,
    n0: PyReadonlyArray1<f64>,
    a0: PyReadonlyArray1<f64>,
    h1: f64,
    s1: PyReadonlyArray1<f64>,
    r1: PyReadonlyArray1<f64>,
    n1: PyReadonlyArray1<f64>,
    a1: PyReadonlyArray1<f64>,
    dt: f64,
    substeps: usize,
    renormalize: bool,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let bg0 = _bg(h0, &s0, &r0, &n0, &a0)?;
    let bg1 = _bg(h1, &s1, &r1, &n1, &a1)?;
    let ev = ehat.as_slice()?.to_vec();
    let (eo, dl) = py.detach(|| {
        qchar::direction_map(
            &ev,
            mass,
            lnp,
            &bg0,
            &bg1,
            qchar::CharacteristicStep {
                dt,
                substeps,
                renormalize,
            },
        )
    });
    let mut v = eo;
    v.extend_from_slice(&dl);
    Ok(Array1::from_vec(v).into_pyarray(py))
}

// ═══════════════════════════════ Q3 · 구면 표현층 바인딩
use crate::kinetic::sphere as qsph;

#[pyclass]
pub struct QSphere {
    inner: qsph::SphereGrid,
}

#[pymethods]
impl QSphere {
    #[new]
    fn new(n_theta: usize, n_phi: usize) -> PyResult<Self> {
        if n_theta < 2 || n_phi < 2 {
            return Err(PyValueError::new_err("n_theta, n_phi >= 2"));
        }
        Ok(QSphere {
            inner: qsph::SphereGrid::new(n_theta, n_phi),
        })
    }
    #[getter]
    fn n(&self) -> usize {
        self.inner.len()
    }
    #[getter]
    fn n_theta(&self) -> usize {
        self.inner.n_theta
    }
    #[getter]
    fn n_phi(&self) -> usize {
        self.inner.n_phi
    }
    fn ehat<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        Array1::from_vec(self.inner.ehat.clone()).into_pyarray(py)
    }
    fn weights<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        Array1::from_vec(self.inner.w.clone()).into_pyarray(py)
    }
    fn analyze<'py>(
        &self,
        py: Python<'py>,
        f: PyReadonlyArray1<f64>,
        l_max: usize,
    ) -> PyResult<Bound<'py, PyArray1<f64>>> {
        let fv = f.as_slice()?;
        if fv.len() != self.inner.len() {
            return Err(PyValueError::new_err("f 길이가 격자와 다르다"));
        }
        let a = py.detach(|| qsph::analyze(&self.inner, fv, l_max));
        Ok(Array1::from_vec(a).into_pyarray(py))
    }
    fn synthesize<'py>(
        &self,
        py: Python<'py>,
        a: PyReadonlyArray1<f64>,
        l_max: usize,
    ) -> PyResult<Bound<'py, PyArray1<f64>>> {
        let av = a.as_slice()?;
        if av.len() != qsph::n_coef(l_max) {
            return Err(PyValueError::new_err("a_lm 길이가 (L+1)^2 이 아니다"));
        }
        let f = py.detach(|| qsph::synthesize(&self.inner, av, l_max));
        Ok(Array1::from_vec(f).into_pyarray(py))
    }
    fn synthesize_at<'py>(
        &self,
        py: Python<'py>,
        a: PyReadonlyArray1<f64>,
        l_max: usize,
        pts: PyReadonlyArray1<f64>,
    ) -> PyResult<Bound<'py, PyArray1<f64>>> {
        let av = a.as_slice()?.to_vec();
        let pv = pts.as_slice()?.to_vec();
        let f = py.detach(|| qsph::synthesize_at(&av, l_max, &pv));
        Ok(Array1::from_vec(f).into_pyarray(py))
    }
    fn project_l<'py>(
        &self,
        py: Python<'py>,
        f: PyReadonlyArray1<f64>,
        l: usize,
    ) -> PyResult<Bound<'py, PyArray1<f64>>> {
        let fv = f.as_slice()?;
        let o = py.detach(|| qsph::project_l(&self.inner, fv, l));
        Ok(Array1::from_vec(o).into_pyarray(py))
    }
    /// [rho, q(3), pi(6)] = 10 성분.
    fn moments<'py>(
        &self,
        py: Python<'py>,
        f: PyReadonlyArray1<f64>,
    ) -> PyResult<Bound<'py, PyArray1<f64>>> {
        let fv = f.as_slice()?;
        let (r, q, pi) = qsph::moments(&self.inner, fv);
        let mut v = vec![r];
        v.extend_from_slice(&q);
        v.extend_from_slice(&pi);
        Ok(Array1::from_vec(v).into_pyarray(py))
    }
    fn tail_energy(&self, f: PyReadonlyArray1<f64>, l_cut: usize, l_max: usize) -> PyResult<f64> {
        Ok(qsph::tail_energy(&self.inner, f.as_slice()?, l_cut, l_max))
    }
}

/// 임의 방향에서의 실수 구면조화 (규약 검증용).
#[pyfunction]
fn qs_ylm_at<'py>(
    py: Python<'py>,
    l_max: usize,
    e: PyReadonlyArray1<f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let ev = e.as_slice()?;
    if ev.len() != 3 {
        return Err(PyValueError::new_err("e 는 3성분"));
    }
    Ok(Array1::from_vec(qsph::ylm_at(l_max, &[ev[0], ev[1], ev[2]])).into_pyarray(py))
}

// ═══════════════════════════════ Q4/Q5/Q7 · 반경층 · 수송 · 정확 충돌 바인딩
use crate::kinetic::collide_exact as qcol;
use crate::kinetic::radial as qrad;
use crate::kinetic::transport as qtr;

#[pyclass]
pub struct QRadial {
    inner: qrad::RadialGrid,
}

#[pymethods]
impl QRadial {
    #[new]
    fn new(lnp_min: f64, lnp_max: f64, n: usize) -> PyResult<Self> {
        if n < 4 {
            return Err(PyValueError::new_err("n_p >= 4"));
        }
        Ok(QRadial {
            inner: qrad::RadialGrid::new(lnp_min, lnp_max, n),
        })
    }
    #[getter]
    fn n(&self) -> usize {
        self.inner.len()
    }
    #[getter]
    fn dlnp(&self) -> f64 {
        self.inner.dlnp
    }
    fn ln_p<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        Array1::from_vec(self.inner.ln_p.clone()).into_pyarray(py)
    }
    fn p<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        Array1::from_vec(self.inner.p()).into_pyarray(py)
    }
    /// (offsets, weights) 를 이어붙인 2K 벡터 (앞 K 는 정수 오프셋).
    fn shift_stencil<'py>(
        &self,
        py: Python<'py>,
        dln: f64,
        order: usize,
    ) -> Bound<'py, PyArray1<f64>> {
        let (o, w) = qrad::shift_stencil(&self.inner, dln, order);
        let mut v: Vec<f64> = o.iter().map(|x| *x as f64).collect();
        v.extend_from_slice(&w);
        Array1::from_vec(v).into_pyarray(py)
    }
    #[pyo3(signature=(lnf, dln, order, tail="wien"))]
    fn apply_shift_log<'py>(
        &self,
        py: Python<'py>,
        lnf: PyReadonlyArray1<f64>,
        dln: f64,
        order: usize,
        tail: &str,
    ) -> PyResult<Bound<'py, PyArray1<f64>>> {
        let st = qrad::shift_stencil(&self.inner, dln, order);
        let t = _tail(tail)?;
        let o = qrad::apply_shift_log(&self.inner, lnf.as_slice()?, &st, t);
        Ok(Array1::from_vec(o).into_pyarray(py))
    }
    #[pyo3(signature=(f, dln, order, tail="wien"))]
    fn apply_shift_linear<'py>(
        &self,
        py: Python<'py>,
        f: PyReadonlyArray1<f64>,
        dln: f64,
        order: usize,
        tail: &str,
    ) -> PyResult<Bound<'py, PyArray1<f64>>> {
        let st = qrad::shift_stencil(&self.inner, dln, order);
        let t = _tail(tail)?;
        let o = qrad::apply_shift_linear(&self.inner, f.as_slice()?, &st, t);
        Ok(Array1::from_vec(o).into_pyarray(py))
    }
    fn tail_fit(&self, f: PyReadonlyArray1<f64>) -> PyResult<(f64, f64)> {
        Ok(qrad::tail_fit(&self.inner, f.as_slice()?))
    }
    fn moment(&self, f: PyReadonlyArray1<f64>, k: i32) -> PyResult<f64> {
        Ok(qrad::moment(&self.inner, f.as_slice()?, k))
    }
}

fn _tail(s: &str) -> PyResult<qrad::Tail> {
    match s {
        "wien" => Ok(qrad::Tail::Wien),
        "power" | "powerlaw" => Ok(qrad::Tail::PowerLaw),
        _ => Err(PyValueError::new_err("tail 은 'wien' 또는 'power'")),
    }
}

fn _kernel(s: &str) -> PyResult<qcol::Kernel> {
    match s {
        "thomson" => Ok(qcol::Kernel::Thomson),
        "bgk" | "bgk_iso" => Ok(qcol::Kernel::BgkIsotropic),
        "bgk_cons" => Ok(qcol::Kernel::BgkConservative),
        _ => Err(PyValueError::new_err("kernel 은 thomson|bgk|bgk_cons")),
    }
}

#[pyclass]
pub struct QPlan {
    inner: qtr::TransportPlan,
}

#[pymethods]
impl QPlan {
    #[getter]
    fn jac_min(&self) -> f64 {
        self.inner.jac_min
    }
    #[getter]
    fn s_ang(&self) -> usize {
        self.inner.s_ang
    }
    fn ln_s<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        Array1::from_vec(self.inner.ln_s.clone()).into_pyarray(py)
    }
    fn stencil_weight_sums<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        let s = self.inner.s_ang;
        let v: Vec<f64> = (0..self.inner.n_ang)
            .map(|i| (0..s).map(|k| self.inner.ang_w[i * s + k]).sum())
            .collect();
        Array1::from_vec(v).into_pyarray(py)
    }
    fn apply_mode_a<'py>(
        &self,
        py: Python<'py>,
        g: PyReadonlyArray1<f64>,
        weight_n: f64,
    ) -> PyResult<Bound<'py, PyArray1<f64>>> {
        let gv = g.as_slice()?;
        if gv.len() != self.inner.n_ang {
            return Err(PyValueError::new_err("g 길이가 각격자와 다르다"));
        }
        let o = py.detach(|| qtr::apply_mode_a(gv, &self.inner, weight_n));
        Ok(Array1::from_vec(o).into_pyarray(py))
    }
    #[pyo3(signature=(f, rad, log_state=false, tail="wien"))]
    fn apply_mode_b<'py>(
        &self,
        py: Python<'py>,
        f: PyReadonlyArray1<f64>,
        rad: PyRef<QRadial>,
        log_state: bool,
        tail: &str,
    ) -> PyResult<Bound<'py, PyArray1<f64>>> {
        let fv = f.as_slice()?;
        if fv.len() != self.inner.n_ang * rad.inner.len() {
            return Err(PyValueError::new_err("f 길이가 n_ang*n_p 가 아니다"));
        }
        let t = _tail(tail)?;
        // PyRef 는 !Sync 라 detach 불가 — GIL 보유 상태로 실행 (병렬은 Q11 의 앙상블 층에서)
        let o = qtr::apply_mode_b(fv, &self.inner, &rad.inner, log_state, t);
        Ok(Array1::from_vec(o).into_pyarray(py))
    }
}

#[pyfunction]
#[pyo3(signature=(sph, rad, h0, s0, r0, n0, a0, h1, s1, r1, n1, a1, dt, mass=0.0,
                  lnp_ref=0.0, substeps=4, k_theta=6, k_phi=6, k_rad=8))]
#[allow(clippy::too_many_arguments)]
fn qt_plan_step(
    sph: PyRef<QSphere>,
    rad: Option<PyRef<QRadial>>,
    h0: f64,
    s0: PyReadonlyArray1<f64>,
    r0: PyReadonlyArray1<f64>,
    n0: PyReadonlyArray1<f64>,
    a0: PyReadonlyArray1<f64>,
    h1: f64,
    s1: PyReadonlyArray1<f64>,
    r1: PyReadonlyArray1<f64>,
    n1: PyReadonlyArray1<f64>,
    a1: PyReadonlyArray1<f64>,
    dt: f64,
    mass: f64,
    lnp_ref: f64,
    substeps: usize,
    k_theta: usize,
    k_phi: usize,
    k_rad: usize,
) -> PyResult<QPlan> {
    let bg0 = _bg(h0, &s0, &r0, &n0, &a0)?;
    let bg1 = _bg(h1, &s1, &r1, &n1, &a1)?;
    let plan = match rad {
        Some(r) => qtr::plan_step(
            &sph.inner,
            Some(&r.inner),
            &bg0,
            &bg1,
            dt,
            mass,
            lnp_ref,
            substeps,
            k_theta,
            k_phi,
            k_rad,
        ),
        None => qtr::plan_step(
            &sph.inner, None, &bg0, &bg1, dt, mass, lnp_ref, substeps, k_theta, k_phi, k_rad,
        ),
    };
    Ok(QPlan { inner: plan })
}

/// exp(nu_dt C) f — 정확 3항.
#[pyfunction]
#[pyo3(signature=(sph, f, nu_dt, kernel="thomson"))]
fn qx_collide<'py>(
    py: Python<'py>,
    sph: PyRef<QSphere>,
    f: PyReadonlyArray1<f64>,
    nu_dt: f64,
    kernel: &str,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let k = _kernel(kernel)?;
    let fv = f.as_slice()?;
    let o = qcol::collide_exact(&sph.inner, fv, nu_dt, k);
    Ok(Array1::from_vec(o).into_pyarray(py))
}

#[pyfunction]
#[pyo3(signature=(sph, f, n_p, nu_dt, kernel="thomson"))]
fn qx_collide_modeb<'py>(
    py: Python<'py>,
    sph: PyRef<QSphere>,
    f: PyReadonlyArray1<f64>,
    n_p: usize,
    nu_dt: f64,
    kernel: &str,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let k = _kernel(kernel)?;
    let fv = f.as_slice()?;
    let o = qcol::collide_exact_modeb(&sph.inner, fv, n_p, nu_dt, k);
    Ok(Array1::from_vec(o).into_pyarray(py))
}

/// ★ k_l 수치 재계산 (하드코딩 금지 게이트).
#[pyfunction]
fn qx_kernel_eigenvalues<'py>(py: Python<'py>, l_max: usize) -> Bound<'py, PyArray1<f64>> {
    Array1::from_vec(qcol::kernel_eigenvalues(l_max)).into_pyarray(py)
}

// ═══════════════════════════════ Q5' · 공변 프레임 바인딩 (76차 정정 설계)
use crate::kinetic::comoving as qcm;

#[pyclass(from_py_object)]
#[derive(Clone)]
pub struct QFrame {
    inner: qcm::Frame,
}

#[pymethods]
impl QFrame {
    #[new]
    fn new() -> Self {
        QFrame {
            inner: qcm::Frame::identity(),
        }
    }
    #[staticmethod]
    fn from_matrix(m: PyReadonlyArray1<f64>) -> PyResult<Self> {
        let v = m.as_slice()?;
        if v.len() != 9 {
            return Err(PyValueError::new_err("M 은 9성분 (행 우선)"));
        }
        let mut a = [0.0; 9];
        a.copy_from_slice(v);
        Ok(QFrame {
            inner: qcm::Frame { m: a },
        })
    }
    fn matrix<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        Array1::from_vec(self.inner.m.to_vec()).into_pyarray(py)
    }
    fn det(&self) -> f64 {
        self.inner.det()
    }
    fn step(
        &self,
        s0: PyReadonlyArray1<f64>,
        r0: PyReadonlyArray1<f64>,
        s1: PyReadonlyArray1<f64>,
        r1: PyReadonlyArray1<f64>,
        dtau: f64,
    ) -> PyResult<QFrame> {
        let g = |a: &PyReadonlyArray1<f64>, n: usize| -> PyResult<Vec<f64>> {
            let v = a.as_slice()?;
            if v.len() != n {
                return Err(PyValueError::new_err("길이 오류"));
            }
            Ok(v.to_vec())
        };
        let (a0, b0, a1, b1) = (g(&s0, 6)?, g(&r0, 3)?, g(&s1, 6)?, g(&r1, 3)?);
        let cv6 = |v: &Vec<f64>| [v[0], v[1], v[2], v[3], v[4], v[5]];
        let cv3 = |v: &Vec<f64>| [v[0], v[1], v[2]];
        Ok(QFrame {
            inner: self
                .inner
                .step(&cv6(&a0), &cv3(&b0), &cv6(&a1), &cv3(&b1), dtau),
        })
    }
    /// (ê 평탄화 3M, mu M) 이어붙인 4M.
    fn phys_dirs<'py>(
        &self,
        py: Python<'py>,
        qhat: PyReadonlyArray1<f64>,
    ) -> PyResult<Bound<'py, PyArray1<f64>>> {
        let q = qhat.as_slice()?;
        let (e, mu) = qcm::phys_dirs(&self.inner, q);
        let mut v = e;
        v.extend_from_slice(&mu);
        Ok(Array1::from_vec(v).into_pyarray(py))
    }
    fn ln_phys_weights<'py>(
        &self,
        py: Python<'py>,
        w_com: PyReadonlyArray1<f64>,
        mu: PyReadonlyArray1<f64>,
    ) -> PyResult<Bound<'py, PyArray1<f64>>> {
        let o = qcm::ln_phys_weights(&self.inner, w_com.as_slice()?, mu.as_slice()?);
        Ok(Array1::from_vec(o).into_pyarray(py))
    }
}

/// 물리 프레임 모멘트 (로그공간 상태) → [rho, q(3), pi(6)].
#[pyfunction]
fn qm_moments_log<'py>(
    py: Python<'py>,
    lw: PyReadonlyArray1<f64>,
    lg: PyReadonlyArray1<f64>,
    ehat: PyReadonlyArray1<f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let (r, q, pi) = qcm::moments_log(lw.as_slice()?, lg.as_slice()?, ehat.as_slice()?);
    let mut v = vec![r];
    v.extend_from_slice(&q);
    v.extend_from_slice(&pi);
    Ok(Array1::from_vec(v).into_pyarray(py))
}

/// ★ 공변격자 위 정확 충돌 지수 (로그공간).
#[pyfunction]
#[pyo3(signature=(lw, lg, ehat, nu_dt, kernel="thomson"))]
fn qm_collide_log<'py>(
    py: Python<'py>,
    lw: PyReadonlyArray1<f64>,
    lg: PyReadonlyArray1<f64>,
    ehat: PyReadonlyArray1<f64>,
    nu_dt: f64,
    kernel: &str,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let act = _kernel(kernel)?.active();
    let o = qcm::collide_exact_log(
        lw.as_slice()?,
        lg.as_slice()?,
        ehat.as_slice()?,
        nu_dt,
        &act,
    );
    Ok(Array1::from_vec(o).into_pyarray(py))
}

/// Q5b · 임의 역추적점에서 계획 생성 (잔여 곡률 이류).
#[pyfunction]
#[pyo3(signature=(sph, eb, ln_s, k_theta=6, k_phi=6))]
fn qt_plan_from_points(
    sph: PyRef<QSphere>,
    eb: PyReadonlyArray1<f64>,
    ln_s: PyReadonlyArray1<f64>,
    k_theta: usize,
    k_phi: usize,
) -> PyResult<QPlan> {
    let e = eb.as_slice()?;
    let l = ln_s.as_slice()?;
    if e.len() != 3 * sph.inner.len() || l.len() != sph.inner.len() {
        return Err(PyValueError::new_err("eb 는 3M, ln_s 는 M"));
    }
    Ok(QPlan {
        inner: qtr::plan_from_points(&sph.inner, e, l, k_theta, k_phi),
    })
}

// ═══════════════════════════════ Q11 · 전-루프 + 멤버 병렬 바인딩
use crate::kinetic::qevolve as qev;

#[allow(clippy::too_many_arguments)]
fn _qstate(
    v: &[f64],
    rot: &[f64],
    residual: bool,
    n_p: usize,
    lnq_min: f64,
    lnq_max: f64,
    tail: &str,
    k_rad: usize,
) -> PyResult<qev::QState> {
    if v.len() < 26 || rot.len() != 3 {
        return Err(PyValueError::new_err("상태는 25+M(*n_p), rot 는 3성분"));
    }
    let rad = if n_p > 0 {
        Some(qrad::RadialGrid::new(lnq_min, lnq_max, n_p))
    } else {
        None
    };
    Ok(qev::QState {
        s6: [v[0], v[1], v[2], v[3], v[4], v[5]],
        n6: [v[6], v[7], v[8], v[9], v[10], v[11]],
        a3: [v[12], v[13], v[14]],
        ln_h: v[15],
        m: [
            v[16], v[17], v[18], v[19], v[20], v[21], v[22], v[23], v[24],
        ],
        lg: v[25..].to_vec(),
        rot: [rot[0], rot[1], rot[2]],
        residual,
        jac_min: 1.0,
        n_p,
        rad,
        tail: _tail(tail)?,
        k_rad,
        v_b: None,
    })
}

struct QConfigArgs<'a> {
    dtau: f64,
    nsteps: usize,
    nu: f64,
    kernel: &'a str,
    k_theta: usize,
    k_phi: usize,
    sub: usize,
    keep_every: usize,
}

fn _qcfg(args: QConfigArgs<'_>) -> PyResult<qev::Config> {
    Ok(qev::Config {
        v_b: None,
        dtau: args.dtau,
        nsteps: args.nsteps,
        nu: args.nu,
        kernel: _kernel(args.kernel)?,
        k_theta: args.k_theta,
        k_phi: args.k_phi,
        sub: args.sub,
        keep_every: args.keep_every,
        nu_sched: Vec::new(),
        h_anchor: 0.0,
    })
}

/// Q19 · 이력 배선 검증: nu_sched 는 스텝 경계 nsteps+1 개여야 한다.
/// 비어 있으면 상수 nu (기존 경로, 비트 동일).
fn _attach_sched(cfg: &mut qev::Config, nu_sched: Option<Vec<f64>>, h_anchor: f64) -> PyResult<()> {
    if let Some(v) = nu_sched {
        if v.len() != cfg.nsteps + 1 {
            return Err(PyValueError::new_err(
                "nu_sched 는 nsteps+1 개 (스텝 경계) 여야 한다",
            ));
        }
        if v.iter().any(|x| !x.is_finite() || *x < 0.0) {
            return Err(PyValueError::new_err("nu_sched 에 음수/비유한 값"));
        }
        if h_anchor < 0.0 || !h_anchor.is_finite() {
            return Err(PyValueError::new_err("h_anchor >= 0 이어야 한다"));
        }
        cfg.nu_sched = v;
        cfg.h_anchor = h_anchor;
    } else if h_anchor != 0.0 {
        return Err(PyValueError::new_err("h_anchor 는 nu_sched 와 함께 준다"));
    }
    Ok(())
}

/// ★ 전-루프 진화.  반환 [최종상태(N), 궤적(...)] 을 이어붙인 1D.
#[pyfunction]
#[pyo3(signature=(n_theta, n_phi, state, rot, residual, dtau, nsteps, nu=0.0,
                  kernel="thomson", k_theta=6, k_phi=6, sub=2, keep_every=0,
                  n_p=0, lnq_min=-5.0, lnq_max=5.0, tail="wien", k_rad=8,
                  v_b=None, nu_sched=None, h_anchor=0.0))]
#[allow(clippy::too_many_arguments)]
fn qe_evolve<'py>(
    py: Python<'py>,
    n_theta: usize,
    n_phi: usize,
    state: PyReadonlyArray1<f64>,
    rot: PyReadonlyArray1<f64>,
    residual: bool,
    dtau: f64,
    nsteps: usize,
    nu: f64,
    kernel: &str,
    k_theta: usize,
    k_phi: usize,
    sub: usize,
    keep_every: usize,
    n_p: usize,
    lnq_min: f64,
    lnq_max: f64,
    tail: &str,
    k_rad: usize,
    v_b: Option<Vec<f64>>,
    nu_sched: Option<Vec<f64>>,
    h_anchor: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let v = state.as_slice()?.to_vec();
    let r = rot.as_slice()?.to_vec();
    let mut st = _qstate(&v, &r, residual, n_p, lnq_min, lnq_max, tail, k_rad)?;
    let vb = match &v_b {
        None => None,
        Some(x) if x.len() == 3 => {
            let n2 = x[0] * x[0] + x[1] * x[1] + x[2] * x[2];
            if n2 >= 1.0 {
                return Err(PyValueError::new_err("|v_b| < 1 이어야 한다"));
            }
            if n2 == 0.0 {
                None
            } else {
                Some([x[0], x[1], x[2]])
            }
        }
        _ => return Err(PyValueError::new_err("v_b 는 3성분")),
    };
    st.v_b = vb;
    let mut cfg = _qcfg(QConfigArgs {
        dtau,
        nsteps,
        nu,
        kernel,
        k_theta,
        k_phi,
        sub,
        keep_every,
    })?;
    cfg.v_b = vb;
    _attach_sched(&mut cfg, nu_sched, h_anchor)?;
    let out = py.detach(move || {
        let sph = qsph::SphereGrid::new(n_theta, n_phi);
        let traj = st.evolve(&sph, &cfg);
        let mut o = st.pack();
        o.extend_from_slice(&traj);
        o
    });
    Ok(Array1::from_vec(out).into_pyarray(py))
}

/// ★ 앙상블 — 멤버 병렬 (rayon).  states 는 (n_member * N) 평탄화.
#[pyfunction]
#[pyo3(signature=(n_theta, n_phi, states, n_member, rot, residual, dtau, nsteps,
                  nu=0.0, kernel="thomson", k_theta=6, k_phi=6, sub=2,
                  n_p=0, lnq_min=-5.0, lnq_max=5.0, tail="wien", k_rad=8))]
#[allow(clippy::too_many_arguments)]
fn qe_ensemble<'py>(
    py: Python<'py>,
    n_theta: usize,
    n_phi: usize,
    states: PyReadonlyArray1<f64>,
    n_member: usize,
    rot: PyReadonlyArray1<f64>,
    residual: bool,
    dtau: f64,
    nsteps: usize,
    nu: f64,
    kernel: &str,
    k_theta: usize,
    k_phi: usize,
    sub: usize,
    n_p: usize,
    lnq_min: f64,
    lnq_max: f64,
    tail: &str,
    k_rad: usize,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let v = states.as_slice()?.to_vec();
    let r = rot.as_slice()?.to_vec();
    if n_member == 0 || v.len() % n_member != 0 {
        return Err(PyValueError::new_err(
            "states 길이가 n_member 로 나뉘지 않는다",
        ));
    }
    let n = v.len() / n_member;
    let mut sts = Vec::with_capacity(n_member);
    for i in 0..n_member {
        sts.push(_qstate(
            &v[i * n..(i + 1) * n],
            &r,
            residual,
            n_p,
            lnq_min,
            lnq_max,
            tail,
            k_rad,
        )?);
    }
    let cfg = _qcfg(QConfigArgs {
        dtau,
        nsteps,
        nu,
        kernel,
        k_theta,
        k_phi,
        sub,
        keep_every: 0,
    })?;
    let out = py.detach(move || {
        let sph = qsph::SphereGrid::new(n_theta, n_phi);
        let res = qev::run_ensemble(&sph, sts, &cfg);
        let mut o = Vec::with_capacity(n_member * n);
        for r in res {
            o.extend_from_slice(&r);
        }
        o
    });
    Ok(Array1::from_vec(out).into_pyarray(py))
}

/// (Omega, Pi6, q, gauss) 진단.
#[pyfunction]
#[pyo3(signature=(n_theta, n_phi, state, rot, n_p=0, lnq_min=-5.0, lnq_max=5.0))]
fn qe_diagnostics(
    n_theta: usize,
    n_phi: usize,
    state: PyReadonlyArray1<f64>,
    rot: PyReadonlyArray1<f64>,
    n_p: usize,
    lnq_min: f64,
    lnq_max: f64,
) -> PyResult<Py<PyArray1<f64>>> {
    let st = _qstate(
        state.as_slice()?,
        rot.as_slice()?,
        true,
        n_p,
        lnq_min,
        lnq_max,
        "wien",
        8,
    )?;
    let sph = qsph::SphereGrid::new(n_theta, n_phi);
    let (om, pi, q) = st.sources(&sph);
    let g = st.gauss_residual(&sph);
    let mut v = vec![om];
    v.extend_from_slice(&pi);
    v.push(q);
    v.push(g);
    Ok(Python::attach(|py| {
        Array1::from_vec(v).into_pyarray(py).unbind()
    }))
}

/// ★ Mode B 잔여 이류 (방향 스텐실 + 방향별 반경 시프트 결합).
#[pyfunction]
#[pyo3(signature=(sph, rad, m, f, n6, a3, dtau, k_theta=6, k_phi=6, k_rad=8,
                  sub=2, log_state=false, tail="wien"))]
#[allow(clippy::too_many_arguments)]
fn qe_residual_mode_b<'py>(
    py: Python<'py>,
    sph: PyRef<QSphere>,
    rad: PyRef<QRadial>,
    m: PyReadonlyArray1<f64>,
    f: PyReadonlyArray1<f64>,
    n6: PyReadonlyArray1<f64>,
    a3: PyReadonlyArray1<f64>,
    dtau: f64,
    k_theta: usize,
    k_phi: usize,
    k_rad: usize,
    sub: usize,
    log_state: bool,
    tail: &str,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let mv = m.as_slice()?;
    let nv = n6.as_slice()?;
    let av = a3.as_slice()?;
    if mv.len() != 9 || nv.len() != 6 || av.len() != 3 {
        return Err(PyValueError::new_err("m 9, n6 6, a3 3"));
    }
    let mm = [
        mv[0], mv[1], mv[2], mv[3], mv[4], mv[5], mv[6], mv[7], mv[8],
    ];
    let nn = [nv[0], nv[1], nv[2], nv[3], nv[4], nv[5]];
    let aa = [av[0], av[1], av[2]];
    let t = _tail(tail)?;
    let out = qev::residual_step_mode_b(
        &sph.inner,
        &rad.inner,
        &mm,
        f.as_slice()?,
        &nn,
        &aa,
        dtau,
        k_theta,
        k_phi,
        k_rad,
        sub,
        log_state,
        t,
    );
    Ok(Array1::from_vec(out).into_pyarray(py))
}

/// 고정 순서 pairwise 축약 (Q11 결정성 계약).
#[pyfunction]
fn qe_reduce_det(v: PyReadonlyArray1<f64>) -> PyResult<f64> {
    Ok(qev::reduce_det(v.as_slice()?))
}

// ═══════════════════════════════ P-C / P9c · 편광 충돌 바인딩
use crate::kinetic::pol_collide as qpol;

/// exp(x C) J — 편광 rank-9 3항 (Mode A).  ehat 3M, w M, j 9M.
#[pyfunction]
fn qp_collide<'py>(
    py: Python<'py>,
    ehat: PyReadonlyArray1<f64>,
    w: PyReadonlyArray1<f64>,
    j: PyReadonlyArray1<f64>,
    x: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let e = ehat.as_slice()?;
    let ww = w.as_slice()?;
    let jj = j.as_slice()?;
    if e.len() != 3 * ww.len() || jj.len() != 9 * ww.len() {
        return Err(PyValueError::new_err("ehat 3M, j 9M 이어야 한다"));
    }
    if x < 0.0 {
        return Err(PyValueError::new_err("nu*dt < 0 금지"));
    }
    let o = py.detach(|| qpol::collide(e, ww, jj, x));
    Ok(Array1::from_vec(o).into_pyarray(py))
}

/// P9c · Mode B 편광 충돌.  j[(i*n_p + jj)*9 + k].
#[pyfunction]
fn qp_collide_modeb<'py>(
    py: Python<'py>,
    ehat: PyReadonlyArray1<f64>,
    w: PyReadonlyArray1<f64>,
    j: PyReadonlyArray1<f64>,
    n_p: usize,
    x: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let e = ehat.as_slice()?;
    let ww = w.as_slice()?;
    let jj = j.as_slice()?;
    if n_p == 0 {
        return Err(PyValueError::new_err("n_p >= 1"));
    }
    if e.len() != 3 * ww.len() || jj.len() != 9 * ww.len() * n_p {
        return Err(PyValueError::new_err("ehat 3M, j 9*M*n_p 이어야 한다"));
    }
    if x < 0.0 {
        return Err(PyValueError::new_err("nu*dt < 0 금지"));
    }
    let o = py.detach(|| qpol::collide_modeb(e, ww, jj, n_p, x));
    Ok(Array1::from_vec(o).into_pyarray(py))
}

/// Kcal 고유값 구적 재계산 (하드코딩 금지 게이트의 Rust 판).
#[pyfunction]
fn qp_kcal_eigenvalues<'py>(
    py: Python<'py>,
    ehat: PyReadonlyArray1<f64>,
    w: PyReadonlyArray1<f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let v = qpol::kcal_eigenvalues(ehat.as_slice()?, w.as_slice()?);
    Ok(Array1::from_vec(v.to_vec()).into_pyarray(py))
}

#[pymodule]
fn bianchi_rustcore(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(qp_collide, m)?)?;
    m.add_function(wrap_pyfunction!(qp_collide_modeb, m)?)?;
    m.add_function(wrap_pyfunction!(qp_kcal_eigenvalues, m)?)?;
    m.add_function(wrap_pyfunction!(rotation_matrix, m)?)?;
    m.add_function(wrap_pyfunction!(tracefree_from_5, m)?)?;
    m.add_function(wrap_pyfunction!(p_double, m)?)?;
    m.add_function(wrap_pyfunction!(trace_ray_diag, m)?)?;
    m.add_function(wrap_pyfunction!(trace_rays_batch, m)?)?;
    m.add_function(wrap_pyfunction!(trace_optical_diag, m)?)?;
    m.add_function(wrap_pyfunction!(trace_optical_batch, m)?)?;
    m.add_function(wrap_pyfunction!(chart_rhs, m)?)?;
    m.add_function(wrap_pyfunction!(chart_aux, m)?)?;
    m.add_function(wrap_pyfunction!(integrate_background, m)?)?;
    m.add_function(wrap_pyfunction!(integrate_background_whiplash, m)?)?;
    m.add_function(wrap_pyfunction!(integrate_batch, m)?)?;
    m.add_function(wrap_pyfunction!(riemann_up_general, m)?)?;
    m.add_function(wrap_pyfunction!(tidal_general, m)?)?;
    m.add_function(wrap_pyfunction!(ricci_kk, m)?)?;
    m.add_function(wrap_pyfunction!(fd_rho_p, m)?)?;
    m.add_function(wrap_pyfunction!(fd_rho_p_batch, m)?)?;
    m.add_function(wrap_pyfunction!(g_star, m)?)?;
    m.add_function(wrap_pyfunction!(g_star_s, m)?)?;
    m.add_function(wrap_pyfunction!(kin_j_moment, m)?)?;
    m.add_function(wrap_pyfunction!(kin_moments, m)?)?;
    m.add_function(wrap_pyfunction!(kin_pstf, m)?)?;
    m.add_function(wrap_pyfunction!(kin_integrate, m)?)?;
    // H3 · Thomson 충돌 (두 경로)
    m.add_function(wrap_pyfunction!(kin_thomson_eigenvalue_numeric, m)?)?;
    m.add_function(wrap_pyfunction!(kin_thomson_eigenvalue, m)?)?;
    m.add_function(wrap_pyfunction!(kin_legendre, m)?)?;
    m.add_function(wrap_pyfunction!(kin_collision_term, m)?)?;
    m.add_function(wrap_pyfunction!(kin_rhs_collisional, m)?)?;
    m.add_function(wrap_pyfunction!(kin_integrate_collisional, m)?)?;
    m.add_function(wrap_pyfunction!(kin_thomson_viscosity, m)?)?;
    m.add_function(wrap_pyfunction!(kin_tight_coupling, m)?)?;
    m.add_function(wrap_pyfunction!(kin_free_streaming_residual, m)?)?;
    m.add_function(wrap_pyfunction!(kin_stiffness_ratio, m)?)?;
    // H4 · imperfect fluid 유도 (두 경로)
    m.add_function(wrap_pyfunction!(kin_route_a_damping, m)?)?;
    m.add_function(wrap_pyfunction!(kin_route_a_source, m)?)?;
    m.add_function(wrap_pyfunction!(kin_route_b_damping, m)?)?;
    m.add_function(wrap_pyfunction!(kin_route_b_damping_handset, m)?)?;
    m.add_function(wrap_pyfunction!(kin_route_b_source, m)?)?;
    m.add_function(wrap_pyfunction!(kin_transport_coefficients, m)?)?;
    m.add_function(wrap_pyfunction!(kin_cross_validate, m)?)?;
    m.add_function(wrap_pyfunction!(kin_eckart_eta, m)?)?;
    m.add_function(wrap_pyfunction!(kin_relaxation_time, m)?)?;
    // H5-e · tilted 구적
    m.add_function(wrap_pyfunction!(kin_j_moment_tilted, m)?)?;
    m.add_function(wrap_pyfunction!(kin_moments_tilted, m)?)?;
    m.add_function(wrap_pyfunction!(kin_boost_shell_residual, m)?)?;
    // R1 · type V 결합 진화
    m.add_function(wrap_pyfunction!(tv_moments, m)?)?;
    m.add_function(wrap_pyfunction!(tv_kinetic_rhs, m)?)?;
    m.add_function(wrap_pyfunction!(tv_flux_rate, m)?)?;
    m.add_function(wrap_pyfunction!(tv_evolve, m)?)?;
    m.add_function(wrap_pyfunction!(tv_back_trace, m)?)?;
    m.add_function(wrap_pyfunction!(tv_push_nodes, m)?)?;
    // R4 · Mixmaster 튐 수열
    m.add_function(wrap_pyfunction!(mx_bounce_sequence, m)?)?;
    m.add_function(wrap_pyfunction!(mx_bounce_sequence_log, m)?)?;
    // R5a · tilted 텐서 커널
    m.add_function(wrap_pyfunction!(tt_perp_dot, m)?)?;
    m.add_function(wrap_pyfunction!(tt_spatial_derivative, m)?)?;
    m.add_function(wrap_pyfunction!(tt_div_contracted, m)?)?;
    m.add_function(wrap_pyfunction!(tt_div_free_raw, m)?)?;
    // R5b · tilted 계층 전체
    m.add_function(wrap_pyfunction!(th_integrate, m)?)?;
    m.add_function(wrap_pyfunction!(th_rhs, m)?)?;
    m.add_function(wrap_pyfunction!(th_force_and_matrix, m)?)?;
    // J3 · 계수공간 계층 커널
    m.add_function(wrap_pyfunction!(coeff_lhs_grid, m)?)?;
    m.add_function(wrap_pyfunction!(coeff_mass_blocks, m)?)?;
    m.add_function(wrap_pyfunction!(coeff_rhs_grid, m)?)?;
    // I3 · 결합 루프
    m.add_function(wrap_pyfunction!(cp_rhs, m)?)?;
    m.add_function(wrap_pyfunction!(cp_evolve, m)?)?;
    // G1b · 격자 충돌 커널
    m.add_function(wrap_pyfunction!(gc_thomson, m)?)?;
    m.add_function(wrap_pyfunction!(gc_expm_apply, m)?)?;
    m.add_function(wrap_pyfunction!(gc_strang, m)?)?;

    m.add_function(wrap_pyfunction!(qg_classify, m)?)?;
    m.add_function(wrap_pyfunction!(qg_jacobi, m)?)?;
    m.add_function(wrap_pyfunction!(qg_structure_constants, m)?)?;
    m.add_function(wrap_pyfunction!(qg_ricci3, m)?)?;
    m.add_function(wrap_pyfunction!(qg_curvature, m)?)?;
    m.add_function(wrap_pyfunction!(qg_kappa, m)?)?;

    m.add_function(wrap_pyfunction!(qc_rhs_p, m)?)?;
    m.add_function(wrap_pyfunction!(qc_rhs_split, m)?)?;
    m.add_function(wrap_pyfunction!(qc_direction_map, m)?)?;

    m.add_class::<QSphere>()?;
    m.add_function(wrap_pyfunction!(qs_ylm_at, m)?)?;

    m.add_class::<QRadial>()?;
    m.add_class::<QPlan>()?;
    m.add_function(wrap_pyfunction!(qt_plan_step, m)?)?;
    m.add_function(wrap_pyfunction!(qt_plan_from_points, m)?)?;
    m.add_function(wrap_pyfunction!(qe_evolve, m)?)?;
    m.add_function(wrap_pyfunction!(qe_ensemble, m)?)?;
    m.add_function(wrap_pyfunction!(qe_diagnostics, m)?)?;
    m.add_function(wrap_pyfunction!(qe_residual_mode_b, m)?)?;
    m.add_function(wrap_pyfunction!(qe_reduce_det, m)?)?;
    m.add_function(wrap_pyfunction!(qx_collide, m)?)?;
    m.add_function(wrap_pyfunction!(qx_collide_modeb, m)?)?;
    m.add_function(wrap_pyfunction!(qx_kernel_eigenvalues, m)?)?;

    m.add_class::<QFrame>()?;
    m.add_function(wrap_pyfunction!(qm_moments_log, m)?)?;
    m.add_function(wrap_pyfunction!(qm_collide_log, m)?)?;
    Ok(())
}

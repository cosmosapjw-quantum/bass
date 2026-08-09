//! bianchi_rustcore · R0/R1 — Rust 연산 코어 (규약 패리티 + 측지 광선추적).
//!
//! 경계 규약: rust-numpy 무복사 입력, 연산 중 GIL 해제(`Python::detach`)로 진짜 병렬.
//! 모든 노출 함수는 Python 오라클(`bianchi.conventions`, `bianchi.rays.geodesics`)과
//! 차등테스트(rtol≤1e-10)로 대조된다.

use nalgebra::{Matrix3, Vector3};
use numpy::ndarray::{Array1, Array2};
use numpy::{IntoPyArray, PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

mod core;
mod ode;
mod rays;

use crate::core::conventions;
use crate::rays::{geodesic, optical};

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
        v[[0, 0]], v[[0, 1]], v[[0, 2]],
        v[[1, 0]], v[[1, 1]], v[[1, 2]],
        v[[2, 0]], v[[2, 1]], v[[2, 2]],
    ))
}

#[inline]
fn mat3_to_py<'py>(py: Python<'py>, m: &Matrix3<f64>) -> Bound<'py, PyArray2<f64>> {
    Array2::from_shape_fn((3, 3), |(i, j)| m[(i, j)]).into_pyarray(py)
}

// ─────────────────────────────── 규약 패리티
#[pyfunction]
fn rotation_matrix<'py>(py: Python<'py>, r: PyReadonlyArray1<f64>) -> PyResult<Bound<'py, PyArray2<f64>>> {
    Ok(mat3_to_py(py, &conventions::rotation_matrix_commutator(&to_vec3(&r)?)))
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
) -> PyResult<(
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray2<f64>>,
    Bound<'py, PyArray2<f64>>,
)> {
    let sig0 = to_vec3(&sigma0)?;
    let nh = to_vec3(&nhat)?;
    let hist = py.detach(|| geodesic::trace_ray_diag(h0, &sig0, omega0, gamma, &nh, t0, t_end, nsteps));
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
    let zs = py.detach(|| {
        geodesic::trace_rays_batch_final_z(h0, &sig0, omega0, gamma, &dirs, t0, t_end, nsteps)
    });
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
) -> PyResult<(
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray2<f64>>,
    f64,
    f64,
    f64,
)> {
    let sig0 = to_vec3(&sigma0)?;
    let nh = to_vec3(&nhat)?;
    let r = py.detach(|| {
        optical::trace_optical_diag(h0, &sig0, omega0, gamma, &nh, t0, t_end, nsteps)
    });
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
) -> PyResult<(Bound<'py, PyArray1<f64>>, Bound<'py, PyArray1<f64>>)> {
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
        other => Err(PyValueError::new_err(format!(
            "unknown chart '{other}' (expected 'class_a' or 'class_b')"
        ))),
    }
}

#[inline]
fn to_y5(a: &PyReadonlyArray1<f64>) -> PyResult<[f64; 5]> {
    let s = a.as_slice()?;
    if s.len() != 5 {
        return Err(PyValueError::new_err("state must have length 5"));
    }
    Ok([s[0], s[1], s[2], s[3], s[4]])
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
    let yy = to_y5(&y)?;
    let mut out = [0.0f64; 5];
    ode::charts::rhs(&c, &yy, &mut out);
    Ok(Array1::from_vec(out.to_vec()).into_pyarray(py))
}

/// 보조량 (Omega, Codazzi C).
#[pyfunction]
#[pyo3(signature = (chart, y, gamma, kappa = 0.0))]
fn chart_aux(chart: &str, y: PyReadonlyArray1<f64>, gamma: f64, kappa: f64) -> PyResult<(f64, f64)> {
    let c = make_chart(chart, gamma, kappa)?;
    let yy = to_y5(&y)?;
    Ok((ode::charts::omega(&c, &yy), ode::charts::codazzi(&c, &yy)))
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
    let y0a = to_y5(&y0)?;
    let ts = t_eval.as_slice()?.to_vec();
    if ts.len() < 2 {
        return Err(PyValueError::new_err("t_eval needs >= 2 points"));
    }
    let tr = py.detach(|| ode::solve::integrate(c, &y0a, &ts, rtol, atol));
    let m = tr.ys.len();
    let ys = Array2::from_shape_fn((m, 5), |(i, j)| tr.ys[i][j]).into_pyarray(py);
    Ok((ys, tr.ok))
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
) -> PyResult<(Bound<'py, PyArray2<f64>>, Bound<'py, PyArray1<f64>>)> {
    let c = make_chart(chart, gamma, kappa)?;
    let view = y0s.as_array();
    if view.ncols() != 5 {
        return Err(PyValueError::new_err("y0s must be shape (K,5)"));
    }
    let inits: Vec<[f64; 5]> = view
        .rows()
        .into_iter()
        .map(|r| [r[0], r[1], r[2], r[3], r[4]])
        .collect();
    let ts = t_eval.as_slice()?.to_vec();
    let res = py.detach(|| ode::solve::integrate_batch(c, &inits, &ts, rtol, atol));
    let k = res.len();
    let ys = Array2::from_shape_fn((k, 5), |(i, j)| res[i].0[j]).into_pyarray(py);
    let ok = Array1::from_vec(res.iter().map(|r| if r.1 { 1.0 } else { 0.0 }).collect())
        .into_pyarray(py);
    Ok((ys, ok))
}

#[pymodule]
fn bianchi_rustcore(m: &Bound<'_, PyModule>) -> PyResult<()> {
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
    m.add_function(wrap_pyfunction!(integrate_batch, m)?)?;
    Ok(())
}

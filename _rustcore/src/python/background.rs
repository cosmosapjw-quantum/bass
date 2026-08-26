//! PyO3 adapters for the RF-02B/RF-02C scalar background closure.

use numpy::ndarray::{Array1, Array2};
use numpy::{IntoPyArray, PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict, PyList};

use crate::ode::background::history::{
    BackgroundParameters, BackgroundPhase, EventRecord, FailureCode, FailureRecord,
    GeometryHistory, GeometrySample, NamedValue, RootDirectionClass, SampleKind, SegmentRecord,
    SegmentStatus, SolverTolerances, TrajectoryStatus, TransitionRecord, TypeIxDiagnostics,
    HISTORY_SCHEMA,
};
use crate::ode::background::trajectory::{
    integrate_background as integrate_background_history_native, integrate_background_batch,
    restart_background, BackgroundRequest, ProjectionMode,
};

type Array2Array1Pair<'py> = (Bound<'py, PyArray2<f64>>, Bound<'py, PyArray1<f64>>);

fn make_chart(chart: &str, gamma: f64, kappa: f64) -> PyResult<crate::ode::charts::Chart> {
    match chart {
        "class_a" => Ok(crate::ode::charts::Chart::ClassA { gamma }),
        "class_b" => Ok(crate::ode::charts::Chart::ClassB { gamma, kappa }),
        // C2 · 커버리지 차트 셋
        "class_b_tilted" => Ok(crate::ode::charts::Chart::ClassBTilted { gamma }),
        // F3 · tilted class A (n-대각 게이지)
        "class_a_tilted" => Ok(crate::ode::charts::Chart::ClassATilted { gamma }),
        "exceptional" => Ok(crate::ode::charts::Chart::Exceptional { gamma }),
        "type_ix_d" => Ok(crate::ode::charts::Chart::TypeIXD {
            gamma,
            future: false,
        }),
        "type_ix_d_future" => Ok(crate::ode::charts::Chart::TypeIXD {
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
pub(crate) fn to_yn(
    a: &PyReadonlyArray1<f64>,
    c: &crate::ode::charts::Chart,
) -> PyResult<[f64; crate::ode::charts::MAX_STATES]> {
    let s = a.as_slice()?;
    let n = c.nstates();
    if s.len() != n {
        return Err(PyValueError::new_err(format!(
            "state must have length {n} for this chart, got {}",
            s.len()
        )));
    }
    let mut out = [0.0f64; crate::ode::charts::MAX_STATES];
    out[..n].copy_from_slice(s);
    Ok(out)
}

/// 차트 RHS 단일 평가 (차등테스트용).
#[pyfunction]
#[pyo3(signature = (chart, y, gamma, kappa = 0.0))]
pub(crate) fn chart_rhs<'py>(
    py: Python<'py>,
    chart: &str,
    y: PyReadonlyArray1<f64>,
    gamma: f64,
    kappa: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let c = make_chart(chart, gamma, kappa)?;
    let yy = to_yn(&y, &c)?;
    let n = c.nstates();
    let mut out = [0.0f64; crate::ode::charts::MAX_STATES];
    crate::ode::charts::rhs(&c, &yy[..n], &mut out[..n]);
    Ok(Array1::from_vec(out[..n].to_vec()).into_pyarray(py))
}

/// 보조량 (Omega, Codazzi C).
#[pyfunction]
#[pyo3(signature = (chart, y, gamma, kappa = 0.0))]
pub(crate) fn chart_aux(
    chart: &str,
    y: PyReadonlyArray1<f64>,
    gamma: f64,
    kappa: f64,
) -> PyResult<(f64, f64)> {
    let c = make_chart(chart, gamma, kappa)?;
    let yy = to_yn(&y, &c)?;
    let n = c.nstates();
    Ok((
        crate::ode::charts::omega(&c, &yy[..n]),
        crate::ode::charts::codazzi(&c, &yy[..n]),
    ))
}

pub(crate) fn make_scalar_chart(
    chart: &str,
    gamma: f64,
    kappa: f64,
) -> PyResult<crate::ode::charts::Chart> {
    if !gamma.is_finite() || !kappa.is_finite() {
        return Err(PyValueError::new_err(
            "RF-02B scalar chart parameters must be finite",
        ));
    }
    if chart == "class_b"
        && (kappa - crate::ode::charts::KAPPA_EXCEPTIONAL).abs()
            < crate::ode::charts::KAPPA_EXCEPTIONAL_TOL
    {
        return Err(PyValueError::new_err(
            "class_b is degenerate near kappa = -9; use the exceptional chart",
        ));
    }
    let c = make_chart(chart, gamma, kappa)?;
    if crate::ode::charts::scalar_state_names(&c).is_none() {
        return Err(PyValueError::new_err(format!(
            "'{chart}' is outside the RF-02B scalar chart closure"
        )));
    }
    Ok(c)
}

/// Cross-language packed-state and live-constraint schema receipt.
#[pyfunction]
#[pyo3(signature = (chart, gamma, kappa = 0.0))]
pub(crate) fn scalar_chart_schema(
    chart: &str,
    gamma: f64,
    kappa: f64,
) -> PyResult<(Vec<String>, Vec<String>)> {
    let c = make_scalar_chart(chart, gamma, kappa)?;
    let states = crate::ode::charts::scalar_state_names(&c)
        .expect("make_scalar_chart checked the closure")
        .iter()
        .map(|name| (*name).to_owned())
        .collect();
    let constraints = crate::ode::charts::scalar_constraint_names(&c)
        .expect("make_scalar_chart checked the closure")
        .iter()
        .map(|name| (*name).to_owned())
        .collect();
    Ok((states, constraints))
}

#[inline]
pub(crate) fn to_scalar_yn(
    a: &PyReadonlyArray1<f64>,
    c: &crate::ode::charts::Chart,
) -> PyResult<[f64; crate::ode::charts::MAX_STATES]> {
    let out = to_yn(a, c)?;
    let n = c.nstates();
    if !out[..n].iter().all(|x| x.is_finite()) {
        return Err(PyValueError::new_err(
            "RF-02B scalar chart buffers must be finite",
        ));
    }
    Ok(out)
}

/// Exact algebraic scalar-chart JVP, deliberately not wired into the RF-02C solver yet.
#[pyfunction]
#[pyo3(signature = (chart, y, tangent, gamma, kappa = 0.0))]
pub(crate) fn chart_jvp<'py>(
    py: Python<'py>,
    chart: &str,
    y: PyReadonlyArray1<f64>,
    tangent: PyReadonlyArray1<f64>,
    gamma: f64,
    kappa: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let c = make_scalar_chart(chart, gamma, kappa)?;
    let yy = to_scalar_yn(&y, &c)?;
    let vv = to_scalar_yn(&tangent, &c)?;
    let n = c.nstates();
    let mut out = [0.0f64; crate::ode::charts::MAX_STATES];
    crate::ode::charts::exact_jvp(&c, &yy[..n], &vv[..n], &mut out[..n])
        .map_err(PyValueError::new_err)?;
    Ok(Array1::from_vec(out[..n].to_vec()).into_pyarray(py))
}

/// Ordered live equality constraints for the scalar-chart schema.
#[pyfunction]
#[pyo3(signature = (chart, y, gamma, kappa = 0.0))]
pub(crate) fn chart_constraints<'py>(
    py: Python<'py>,
    chart: &str,
    y: PyReadonlyArray1<f64>,
    gamma: f64,
    kappa: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let c = make_scalar_chart(chart, gamma, kappa)?;
    let yy = to_scalar_yn(&y, &c)?;
    let n = c.nstates();
    let mut out = [0.0f64; crate::ode::charts::MAX_STATES];
    let m = crate::ode::charts::constraint_values(&c, &yy[..n], &mut out)
        .map_err(PyValueError::new_err)?;
    Ok(Array1::from_vec(out[..m].to_vec()).into_pyarray(py))
}

/// Pointwise Gauss-Newton scalar projection.  No integration route calls this implicitly.
#[pyfunction]
#[pyo3(signature = (chart, y, gamma, kappa = 0.0, iters = 3, damping = 1e-12))]
pub(crate) fn chart_project<'py>(
    py: Python<'py>,
    chart: &str,
    y: PyReadonlyArray1<f64>,
    gamma: f64,
    kappa: f64,
    iters: usize,
    damping: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let c = make_scalar_chart(chart, gamma, kappa)?;
    let yy = to_scalar_yn(&y, &c)?;
    let n = c.nstates();
    let mut out = [0.0f64; crate::ode::charts::MAX_STATES];
    crate::ode::charts::project_constraints(&c, &yy[..n], iters, damping, &mut out[..n])
        .map_err(PyValueError::new_err)?;
    Ok(Array1::from_vec(out[..n].to_vec()).into_pyarray(py))
}

/// 단일 궤적 적분 (diffsol BDF).  반환 (ys[M,5], ok).
#[pyfunction]
#[pyo3(signature = (chart, y0, t_eval, gamma, kappa = 0.0, rtol = 1e-10, atol = 1e-12))]
#[allow(clippy::too_many_arguments)]
pub(crate) fn integrate_background<'py>(
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
    let tr = py.detach(|| crate::ode::solve::integrate(c, &y0a[..], &ts, rtol, atol));
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
pub(crate) fn integrate_background_whiplash<'py>(
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
    if c.tilt_gamma_v2(&[0.0; crate::ode::charts::MAX_STATES][..c.nstates()])
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
    let (tr, stop) = py.detach(|| {
        crate::ode::solve::integrate_whiplash(c, &y0a[..], &ts, rtol, atol, Some(gap_eps))
    });
    let m = tr.ys.len();
    let ys = Array2::from_shape_fn((m, n), |(i, j)| tr.ys[i][j]).into_pyarray(py);
    Ok((ys, tr.ok, stop.is_some(), stop.unwrap_or(f64::NAN)))
}

/// 배치 스캔 (R3): 초기조건 (K,5) → (마지막 상태 (K,5), 성공 마스크 (K,)).
/// Rayon 병렬 — 낙오자가 배치 전체를 오염시키지 않는다 (JAX while_loop 대비 이점).
#[pyfunction]
#[pyo3(signature = (chart, y0s, t_eval, gamma, kappa = 0.0, rtol = 1e-10, atol = 1e-12))]
#[allow(clippy::too_many_arguments)]
pub(crate) fn integrate_batch<'py>(
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
    let inits: Vec<[f64; crate::ode::charts::MAX_STATES]> = view
        .rows()
        .into_iter()
        .map(|r| {
            let mut b = [0.0f64; crate::ode::charts::MAX_STATES];
            for j in 0..n {
                b[j] = r[j];
            }
            b
        })
        .collect();
    let ts = t_eval.as_slice()?.to_vec();
    let res = py.detach(|| crate::ode::solve::integrate_batch(c, &inits, &ts, rtol, atol));
    let k = res.len();
    let ys = Array2::from_shape_fn((k, n), |(i, j)| res[i].0[j]).into_pyarray(py);
    let ok = Array1::from_vec(res.iter().map(|r| if r.1 { 1.0 } else { 0.0 }).collect())
        .into_pyarray(py);
    Ok((ys, ok))
}

/// Checked RF-02C projection with an explicit machine-readable certificate.
#[pyfunction]
#[pyo3(signature = (chart, y, gamma, kappa = 0.0, rtol = 1e-10, atol = 1e-12))]
pub(crate) fn chart_project_checked<'py>(
    py: Python<'py>,
    chart: &str,
    y: PyReadonlyArray1<f64>,
    gamma: f64,
    kappa: f64,
    rtol: f64,
    atol: f64,
) -> PyResult<Py<PyDict>> {
    let c = make_chart(chart, gamma, kappa)?;
    let yy = to_yn(&y, &c)?;
    let n = c.nstates();
    let checked = crate::ode::charts::project_constraints_checked(&c, &yy[..n], rtol, atol);
    let certificate = &checked.certificate;
    let result = PyDict::new(py);
    result.set_item(
        "state",
        Array1::from_vec(checked.state[..checked.state_len].to_vec()).into_pyarray(py),
    )?;
    result.set_item("chart", certificate.chart)?;
    result.set_item("state_schema_hash", certificate.state_schema_hash)?;
    result.set_item("rtol", certificate.rtol)?;
    result.set_item("atol", certificate.atol)?;
    result.set_item("damping", certificate.damping)?;
    result.set_item("iterations_attempted", certificate.iterations_attempted)?;
    result.set_item("constraint_names", certificate.constraint_names.clone())?;
    result.set_item(
        "initial_constraints",
        certificate.initial_constraints.clone(),
    )?;
    result.set_item("final_constraints", certificate.final_constraints.clone())?;
    result.set_item(
        "normalized_residual_history",
        certificate.normalized_residual_history.clone(),
    )?;
    let margins = PyList::empty(py);
    for margin in &certificate.domain_margins {
        let item = PyDict::new(py);
        item.set_item("name", margin.name)?;
        item.set_item("raw", margin.raw)?;
        item.set_item("certificate", margin.certificate)?;
        margins.append(item)?;
    }
    result.set_item("domain_margins", margins)?;
    result.set_item("accepted", certificate.accepted)?;
    result.set_item(
        "failure_code",
        certificate.failure_code.map(|code| code.as_str()),
    )?;
    Ok(result.unbind())
}

fn projection_mode_from_str(value: &str) -> PyResult<ProjectionMode> {
    match value {
        "off" => Ok(ProjectionMode::Off),
        "checked_initial" => Ok(ProjectionMode::CheckedInitial),
        "checked_chunk_boundary" => Ok(ProjectionMode::CheckedChunkBoundary),
        _ => Err(PyValueError::new_err(
            "projection_mode must be off, checked_initial, or checked_chunk_boundary",
        )),
    }
}

fn scalar_chart_label(value: &str) -> PyResult<&'static str> {
    match value {
        "class_a" => Ok("class_a"),
        "class_b" => Ok("class_b"),
        "exceptional" => Ok("exceptional"),
        "type_ix_d" => Ok("type_ix_d"),
        "type_ix_d_future" => Ok("type_ix_d_future"),
        _ => Err(PyValueError::new_err(
            "chart is outside the RF-02C scalar execution closure",
        )),
    }
}

#[allow(clippy::too_many_arguments)]
fn make_background_request(
    chart_label: &str,
    initial_state: Vec<f64>,
    requested_taus: Vec<f64>,
    gamma: f64,
    kappa: f64,
    rtol: f64,
    atol: f64,
    projection_mode: &str,
) -> PyResult<BackgroundRequest> {
    let label = scalar_chart_label(chart_label)?;
    let chart = make_scalar_chart(label, gamma, kappa)?;
    Ok(BackgroundRequest {
        chart,
        chart_label: label,
        initial_state,
        requested_taus,
        gamma,
        kappa,
        rtol,
        atol,
        projection_mode: projection_mode_from_str(projection_mode)?,
    })
}

fn named_values_to_dict<'py>(
    py: Python<'py>,
    values: &[NamedValue],
) -> PyResult<Bound<'py, PyDict>> {
    let output = PyDict::new(py);
    for value in values {
        output.set_item(&value.name, value.value)?;
    }
    Ok(output)
}

fn sample_to_dict<'py>(py: Python<'py>, sample: &GeometrySample) -> PyResult<Bound<'py, PyDict>> {
    let output = PyDict::new(py);
    output.set_item("sample_index", sample.sample_index)?;
    output.set_item("segment_id", sample.segment_id)?;
    output.set_item("phase", sample.phase.as_str())?;
    output.set_item("sample_kind", sample.sample_kind.as_str())?;
    output.set_item("tau", sample.tau)?;
    output.set_item(
        "tau_bits",
        crate::ode::background::history::tau_bits_hex(sample.tau_bits),
    )?;
    output.set_item("state", sample.state.clone())?;
    output.set_item("state_sha256", sample.state_sha256.to_hex())?;
    output.set_item("Omega", sample.omega)?;
    output.set_item(
        "equality_constraints",
        named_values_to_dict(py, &sample.equality_constraints)?,
    )?;
    output.set_item(
        "normalized_constraint_residual",
        sample.normalized_constraint_residual,
    )?;
    output.set_item(
        "domain_margins_raw",
        named_values_to_dict(py, &sample.domain_margins_raw)?,
    )?;
    output.set_item(
        "domain_margins_certificate",
        named_values_to_dict(py, &sample.domain_margins_certificate)?,
    )?;
    if let Some(type_ix) = &sample.type_ix {
        output.set_item("H_bar", type_ix.h_bar)?;
        output.set_item("Sigma2", type_ix.sigma2)?;
        output.set_item("definition", type_ix.definition)?;
        output.set_item("trace", type_ix.trace)?;
    }
    Ok(output)
}

fn event_to_dict<'py>(py: Python<'py>, event: &EventRecord) -> PyResult<Bound<'py, PyDict>> {
    let output = PyDict::new(py);
    output.set_item("event_sequence", event.event_sequence)?;
    output.set_item("event_id", &event.event_id)?;
    output.set_item("margin_id", &event.margin_id)?;
    output.set_item("root_multiplicity", event.root_multiplicity)?;
    output.set_item("direction_class", event.direction_class.as_i8())?;
    output.set_item("priority", event.priority)?;
    output.set_item("simultaneous_group", event.simultaneous_group)?;
    output.set_item("sample_index", event.sample_index)?;
    output.set_item(
        "tau_bits",
        crate::ode::background::history::tau_bits_hex(event.tau_bits),
    )?;
    output.set_item("epsilon_g", event.epsilon_g)?;
    output.set_item(
        "epsilon_g_bits",
        crate::ode::background::history::epsilon_bits_hex(event.epsilon_g_bits),
    )?;
    output.set_item("raw_margin", event.raw_margin)?;
    output.set_item("certificate_margin", event.certificate_margin)?;
    output.set_item("segment_terminal", event.segment_terminal)?;
    output.set_item("trajectory_terminal", event.trajectory_terminal)?;
    output.set_item("transition_id", event.transition_id.clone())?;
    Ok(output)
}

fn transition_to_dict<'py>(
    py: Python<'py>,
    transition: &TransitionRecord,
) -> PyResult<Bound<'py, PyDict>> {
    let output = PyDict::new(py);
    output.set_item("transition_sequence", transition.transition_sequence)?;
    output.set_item("transition_id", &transition.transition_id)?;
    output.set_item("event_sequence", transition.event_sequence)?;
    output.set_item("sample_index", transition.sample_index)?;
    output.set_item(
        "tau_bits",
        crate::ode::background::history::tau_bits_hex(transition.tau_bits),
    )?;
    output.set_item("from_chart", &transition.from_chart)?;
    output.set_item("from_phase", transition.from_phase.as_str())?;
    output.set_item("to_chart", &transition.to_chart)?;
    output.set_item("to_phase", transition.to_phase.as_str())?;
    output.set_item("state_map", &transition.state_map)?;
    output.set_item("state_bytes_preserved", transition.state_bytes_preserved)?;
    Ok(output)
}

fn segment_to_dict<'py>(py: Python<'py>, segment: &SegmentRecord) -> PyResult<Bound<'py, PyDict>> {
    let output = PyDict::new(py);
    output.set_item("segment_id", segment.segment_id)?;
    output.set_item("chart", &segment.chart)?;
    output.set_item("phase", segment.phase.as_str())?;
    output.set_item(
        "tau_start_bits",
        crate::ode::background::history::tau_bits_hex(segment.tau_start_bits),
    )?;
    output.set_item(
        "tau_end_bits",
        crate::ode::background::history::tau_bits_hex(segment.tau_end_bits),
    )?;
    output.set_item("start_sample_index", segment.start_sample_index)?;
    output.set_item("end_sample_index", segment.end_sample_index)?;
    output.set_item("status", segment.status.as_str())?;
    Ok(output)
}

fn history_to_dict<'py>(
    py: Python<'py>,
    history: &GeometryHistory,
) -> PyResult<Bound<'py, PyDict>> {
    let output = PyDict::new(py);
    output.set_item("schema", HISTORY_SCHEMA)?;
    output.set_item("route_identity", &history.route_identity)?;
    output.set_item("native_identity", &history.native_identity)?;
    output.set_item("event_registry_hash", &history.event_registry_hash)?;
    output.set_item("initial_chart", &history.initial_chart)?;
    output.set_item("initial_phase", history.initial_phase.as_str())?;
    output.set_item("final_chart", &history.final_chart)?;
    output.set_item("final_phase", history.final_phase.as_str())?;
    let parameters = PyDict::new(py);
    parameters.set_item("gamma", history.parameters.gamma)?;
    parameters.set_item("kappa", history.parameters.kappa)?;
    output.set_item("parameters", parameters)?;
    let tolerances = PyDict::new(py);
    tolerances.set_item("rtol", history.solver_tolerances.rtol)?;
    tolerances.set_item("atol", history.solver_tolerances.atol)?;
    output.set_item("solver_tolerances", tolerances)?;
    output.set_item("state_names", history.state_names.clone())?;

    let segments = PyList::empty(py);
    for segment in &history.segments {
        segments.append(segment_to_dict(py, segment)?)?;
    }
    output.set_item("segments", segments)?;
    let samples = PyList::empty(py);
    for sample in &history.samples {
        samples.append(sample_to_dict(py, sample)?)?;
    }
    output.set_item("samples", samples)?;
    let events = PyList::empty(py);
    for event in &history.events {
        events.append(event_to_dict(py, event)?)?;
    }
    output.set_item("events", events)?;
    let transitions = PyList::empty(py);
    for transition in &history.transitions {
        transitions.append(transition_to_dict(py, transition)?)?;
    }
    output.set_item("transitions", transitions)?;
    output.set_item("status", history.status.as_str())?;
    if let Some(failure) = &history.failure {
        let value = PyDict::new(py);
        value.set_item("code", failure.code.as_str())?;
        value.set_item("detail", &failure.detail)?;
        output.set_item("failure", value)?;
    } else {
        output.set_item("failure", py.None())?;
    }
    Ok(output)
}

fn required_item<'py>(dictionary: &Bound<'py, PyDict>, key: &str) -> PyResult<Bound<'py, PyAny>> {
    dictionary
        .get_item(key)?
        .ok_or_else(|| PyValueError::new_err(format!("history is missing required field '{key}'")))
}

fn parse_bits(value: &str, field: &str) -> PyResult<u64> {
    if value.len() != 16
        || !value
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
    {
        return Err(PyValueError::new_err(format!(
            "{field} must be lowercase fixed-width binary64 hex"
        )));
    }
    u64::from_str_radix(value, 16)
        .map_err(|_| PyValueError::new_err(format!("{field} is not valid binary64 hex")))
}

fn parse_phase(value: &str) -> BackgroundPhase {
    match value {
        "expanding" => BackgroundPhase::Expanding,
        "contracting" => BackgroundPhase::Contracting,
        other => BackgroundPhase::Named(other.to_owned()),
    }
}

fn parse_sample_kind(value: &str) -> PyResult<SampleKind> {
    match value {
        "initial" => Ok(SampleKind::Initial),
        "requested" => Ok(SampleKind::Requested),
        "event_root" => Ok(SampleKind::EventRoot),
        _ => Err(PyValueError::new_err("invalid history sample_kind")),
    }
}

fn parse_segment_status(value: &str) -> PyResult<SegmentStatus> {
    match value {
        "COMPLETED" => Ok(SegmentStatus::Completed),
        "DOMAIN_BOUNDARY" => Ok(SegmentStatus::DomainBoundary),
        "EVENT_TERMINATED" => Ok(SegmentStatus::EventTerminated),
        "TRANSITION_REQUIRED" => Ok(SegmentStatus::TransitionRequired),
        "FAILED" => Ok(SegmentStatus::Failed),
        _ => Err(PyValueError::new_err("invalid history segment status")),
    }
}

fn parse_trajectory_status(value: &str) -> PyResult<TrajectoryStatus> {
    match value {
        "COMPLETED" => Ok(TrajectoryStatus::Completed),
        "COMPLETED_AT_TRANSITION" => Ok(TrajectoryStatus::CompletedAtTransition),
        "DOMAIN_BOUNDARY" => Ok(TrajectoryStatus::DomainBoundary),
        "FAILED_AFTER_ACCEPTED_PREFIX" => Ok(TrajectoryStatus::FailedAfterAcceptedPrefix),
        "FAILED" => Ok(TrajectoryStatus::Failed),
        _ => Err(PyValueError::new_err("invalid history trajectory status")),
    }
}

fn parse_failure_code(value: &str) -> PyResult<FailureCode> {
    let code = match value {
        "INVALID_INPUT" => FailureCode::InvalidInput,
        "INITIAL_DOMAIN_VIOLATION" => FailureCode::InitialDomainViolation,
        "TYPE_IX_DAE_SINGULAR_CHART" => FailureCode::TypeIxDaeSingularChart,
        "UNSUPPORTED_EVENT_EXPRESSION" => FailureCode::UnsupportedEventExpression,
        "UNSUPPORTED_TRANSITION" => FailureCode::UnsupportedTransition,
        "EVENT_CARRIER_NONFINITE" => FailureCode::EventCarrierNonfinite,
        "EVENT_CARRIER_CERTIFICATE_FAILURE" => FailureCode::EventCarrierCertificateFailure,
        "NONADVANCING_ACCEPTED_STEP" => FailureCode::NonadvancingAcceptedStep,
        "EVENT_ROOT_REPRESENTATION_FAILURE" => FailureCode::EventRootRepresentationFailure,
        "RESTART_IDENTITY_MISMATCH" => FailureCode::RestartIdentityMismatch,
        "ACCEPTED_SAMPLE_NONFINITE" => FailureCode::AcceptedSampleNonfinite,
        "ACCEPTED_SAMPLE_SCHEMA_MISMATCH" => FailureCode::AcceptedSampleSchemaMismatch,
        "ACCEPTED_SAMPLE_CONSTRAINT_FAILURE" => FailureCode::AcceptedSampleConstraintFailure,
        "ACCEPTED_SAMPLE_DOMAIN_FAILURE" => FailureCode::AcceptedSampleDomainFailure,
        "PROJECTION_INVALID_INPUT" => FailureCode::ProjectionInvalidInput,
        "PROJECTION_SINGULAR" => FailureCode::ProjectionSingular,
        "PROJECTION_NONFINITE" => FailureCode::ProjectionNonfinite,
        "PROJECTION_NON_MONOTONE" => FailureCode::ProjectionNonMonotone,
        "PROJECTION_NOT_CONVERGED" => FailureCode::ProjectionNotConverged,
        "PROJECTION_PHYSICAL_DOMAIN" => FailureCode::ProjectionPhysicalDomain,
        "SOLVER_FAILURE" => FailureCode::SolverFailure,
        "HISTORY_INVARIANT_VIOLATION" => FailureCode::HistoryInvariantViolation,
        _ => return Err(PyValueError::new_err("invalid history failure code")),
    };
    Ok(code)
}

fn parse_direction(value: i8) -> PyResult<RootDirectionClass> {
    match value {
        -1 => Ok(RootDirectionClass::Decreasing),
        0 => Ok(RootDirectionClass::Tangential),
        1 => Ok(RootDirectionClass::Increasing),
        _ => Err(PyValueError::new_err(
            "invalid history root direction class",
        )),
    }
}

fn named_values_from_dict(dictionary: &Bound<'_, PyDict>) -> PyResult<Vec<NamedValue>> {
    dictionary
        .iter()
        .map(|(name, value)| {
            Ok(NamedValue::new(
                name.extract::<String>()?,
                value.extract::<f64>()?,
            ))
        })
        .collect()
}

fn sample_from_dict(dictionary: &Bound<'_, PyDict>) -> PyResult<GeometrySample> {
    let tau = required_item(dictionary, "tau")?.extract::<f64>()?;
    let tau_bits_text = required_item(dictionary, "tau_bits")?.extract::<String>()?;
    let tau_bits = parse_bits(&tau_bits_text, "sample.tau_bits")?;
    let state = required_item(dictionary, "state")?.extract::<Vec<f64>>()?;
    let state_sha256 = required_item(dictionary, "state_sha256")?.extract::<String>()?;
    let equality = required_item(dictionary, "equality_constraints")?;
    let raw = required_item(dictionary, "domain_margins_raw")?;
    let certificate = required_item(dictionary, "domain_margins_certificate")?;
    let type_ix = if dictionary.get_item("H_bar")?.is_some() {
        Some(TypeIxDiagnostics {
            h_bar: required_item(dictionary, "H_bar")?.extract()?,
            sigma2: required_item(dictionary, "Sigma2")?.extract()?,
            definition: required_item(dictionary, "definition")?.extract()?,
            trace: required_item(dictionary, "trace")?.extract()?,
        })
    } else {
        None
    };
    let sample = GeometrySample::new(
        required_item(dictionary, "sample_index")?.extract()?,
        required_item(dictionary, "segment_id")?.extract()?,
        parse_phase(&required_item(dictionary, "phase")?.extract::<String>()?),
        parse_sample_kind(&required_item(dictionary, "sample_kind")?.extract::<String>()?)?,
        tau,
        state,
        required_item(dictionary, "Omega")?.extract()?,
        named_values_from_dict(equality.cast::<PyDict>()?)?,
        required_item(dictionary, "normalized_constraint_residual")?.extract()?,
        named_values_from_dict(raw.cast::<PyDict>()?)?,
        named_values_from_dict(certificate.cast::<PyDict>()?)?,
        type_ix,
    );
    if sample.tau_bits != tau_bits || sample.state_sha256.to_hex() != state_sha256 {
        return Err(PyValueError::new_err(
            "history sample tau/state byte identity mismatch",
        ));
    }
    Ok(sample)
}

fn event_from_dict(dictionary: &Bound<'_, PyDict>) -> PyResult<EventRecord> {
    let tau_bits = parse_bits(
        &required_item(dictionary, "tau_bits")?.extract::<String>()?,
        "event.tau_bits",
    )?;
    let epsilon_g = required_item(dictionary, "epsilon_g")?.extract::<f64>()?;
    let epsilon_bits = parse_bits(
        &required_item(dictionary, "epsilon_g_bits")?.extract::<String>()?,
        "event.epsilon_g_bits",
    )?;
    if epsilon_g.to_bits() != epsilon_bits {
        return Err(PyValueError::new_err(
            "history event epsilon_g byte identity mismatch",
        ));
    }
    Ok(EventRecord {
        event_sequence: required_item(dictionary, "event_sequence")?.extract()?,
        event_id: required_item(dictionary, "event_id")?.extract()?,
        margin_id: required_item(dictionary, "margin_id")?.extract()?,
        root_multiplicity: required_item(dictionary, "root_multiplicity")?.extract()?,
        direction_class: parse_direction(required_item(dictionary, "direction_class")?.extract()?)?,
        priority: required_item(dictionary, "priority")?.extract()?,
        simultaneous_group: required_item(dictionary, "simultaneous_group")?.extract()?,
        sample_index: required_item(dictionary, "sample_index")?.extract()?,
        tau_bits,
        epsilon_g,
        epsilon_g_bits: epsilon_bits,
        raw_margin: required_item(dictionary, "raw_margin")?.extract()?,
        certificate_margin: required_item(dictionary, "certificate_margin")?.extract()?,
        segment_terminal: required_item(dictionary, "segment_terminal")?.extract()?,
        trajectory_terminal: required_item(dictionary, "trajectory_terminal")?.extract()?,
        transition_id: required_item(dictionary, "transition_id")?.extract()?,
    })
}

fn transition_from_dict(dictionary: &Bound<'_, PyDict>) -> PyResult<TransitionRecord> {
    Ok(TransitionRecord {
        transition_sequence: required_item(dictionary, "transition_sequence")?.extract()?,
        transition_id: required_item(dictionary, "transition_id")?.extract()?,
        event_sequence: required_item(dictionary, "event_sequence")?.extract()?,
        sample_index: required_item(dictionary, "sample_index")?.extract()?,
        tau_bits: parse_bits(
            &required_item(dictionary, "tau_bits")?.extract::<String>()?,
            "transition.tau_bits",
        )?,
        from_chart: required_item(dictionary, "from_chart")?.extract()?,
        from_phase: parse_phase(&required_item(dictionary, "from_phase")?.extract::<String>()?),
        to_chart: required_item(dictionary, "to_chart")?.extract()?,
        to_phase: parse_phase(&required_item(dictionary, "to_phase")?.extract::<String>()?),
        state_map: required_item(dictionary, "state_map")?.extract()?,
        state_bytes_preserved: required_item(dictionary, "state_bytes_preserved")?.extract()?,
    })
}

fn segment_from_dict(dictionary: &Bound<'_, PyDict>) -> PyResult<SegmentRecord> {
    Ok(SegmentRecord {
        segment_id: required_item(dictionary, "segment_id")?.extract()?,
        chart: required_item(dictionary, "chart")?.extract()?,
        phase: parse_phase(&required_item(dictionary, "phase")?.extract::<String>()?),
        tau_start_bits: parse_bits(
            &required_item(dictionary, "tau_start_bits")?.extract::<String>()?,
            "segment.tau_start_bits",
        )?,
        tau_end_bits: parse_bits(
            &required_item(dictionary, "tau_end_bits")?.extract::<String>()?,
            "segment.tau_end_bits",
        )?,
        start_sample_index: required_item(dictionary, "start_sample_index")?.extract()?,
        end_sample_index: required_item(dictionary, "end_sample_index")?.extract()?,
        status: parse_segment_status(&required_item(dictionary, "status")?.extract::<String>()?)?,
    })
}

fn history_from_dict(dictionary: &Bound<'_, PyDict>) -> PyResult<GeometryHistory> {
    if required_item(dictionary, "schema")?.extract::<String>()? != HISTORY_SCHEMA {
        return Err(PyValueError::new_err("history schema identity mismatch"));
    }
    let parameters = required_item(dictionary, "parameters")?;
    let parameters = parameters.cast::<PyDict>()?;
    let tolerances = required_item(dictionary, "solver_tolerances")?;
    let tolerances = tolerances.cast::<PyDict>()?;
    let mut history = GeometryHistory::new(
        required_item(dictionary, "route_identity")?.extract::<String>()?,
        required_item(dictionary, "native_identity")?.extract::<String>()?,
        required_item(dictionary, "event_registry_hash")?.extract::<String>()?,
        required_item(dictionary, "initial_chart")?.extract::<String>()?,
        parse_phase(&required_item(dictionary, "initial_phase")?.extract::<String>()?),
        BackgroundParameters {
            gamma: required_item(parameters, "gamma")?.extract()?,
            kappa: required_item(parameters, "kappa")?.extract()?,
        },
        SolverTolerances {
            rtol: required_item(tolerances, "rtol")?.extract()?,
            atol: required_item(tolerances, "atol")?.extract()?,
        },
        required_item(dictionary, "state_names")?.extract()?,
    );
    history.final_chart = required_item(dictionary, "final_chart")?.extract()?;
    history.final_phase =
        parse_phase(&required_item(dictionary, "final_phase")?.extract::<String>()?);

    let samples = required_item(dictionary, "samples")?;
    for item in samples.cast::<PyList>()?.iter() {
        let sample = sample_from_dict(item.cast::<PyDict>()?)?;
        history.append_sample(sample).map_err(|error| {
            PyValueError::new_err(format!("history sample invariant failed: {error:?}"))
        })?;
    }
    let events = required_item(dictionary, "events")?;
    for item in events.cast::<PyList>()?.iter() {
        let event = event_from_dict(item.cast::<PyDict>()?)?;
        history.append_event(event).map_err(|error| {
            PyValueError::new_err(format!("history event invariant failed: {error:?}"))
        })?;
    }
    let transitions = required_item(dictionary, "transitions")?;
    for item in transitions.cast::<PyList>()?.iter() {
        let transition = transition_from_dict(item.cast::<PyDict>()?)?;
        history.append_transition(transition).map_err(|error| {
            PyValueError::new_err(format!("history transition invariant failed: {error:?}"))
        })?;
    }
    let segments = required_item(dictionary, "segments")?;
    for item in segments.cast::<PyList>()?.iter() {
        let segment = segment_from_dict(item.cast::<PyDict>()?)?;
        history.append_segment(segment).map_err(|error| {
            PyValueError::new_err(format!("history segment invariant failed: {error:?}"))
        })?;
    }
    history.status =
        parse_trajectory_status(&required_item(dictionary, "status")?.extract::<String>()?)?;
    let failure = required_item(dictionary, "failure")?;
    history.failure = if failure.is_none() {
        None
    } else {
        let failure = failure.cast::<PyDict>()?;
        Some(FailureRecord::new(
            parse_failure_code(&required_item(failure, "code")?.extract::<String>()?)?,
            required_item(failure, "detail")?.extract::<String>()?,
        ))
    };
    Ok(history)
}

/// Execute one complete RF-02C native-owned trajectory and return normalized history.
#[pyfunction]
#[pyo3(signature = (chart, y0, t_eval, gamma, kappa = 0.0, rtol = 1e-10, atol = 1e-12, projection_mode = "off"))]
#[allow(clippy::too_many_arguments)]
pub(crate) fn integrate_background_history<'py>(
    py: Python<'py>,
    chart: &str,
    y0: PyReadonlyArray1<f64>,
    t_eval: PyReadonlyArray1<f64>,
    gamma: f64,
    kappa: f64,
    rtol: f64,
    atol: f64,
    projection_mode: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let chart_value = make_scalar_chart(chart, gamma, kappa)?;
    let initial = to_scalar_yn(&y0, &chart_value)?;
    let request = make_background_request(
        chart,
        initial[..chart_value.nstates()].to_vec(),
        t_eval.as_slice()?.to_vec(),
        gamma,
        kappa,
        rtol,
        atol,
        projection_mode,
    )?;
    let history = py.detach(move || integrate_background_history_native(request));
    history_to_dict(py, &history)
}

/// Continue only from a validated stored Type-IX transition root.
#[pyfunction]
pub(crate) fn restart_background_history<'py>(
    py: Python<'py>,
    previous: Bound<'py, PyDict>,
    new_end: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let previous = history_from_dict(&previous)?;
    let history = py.detach(move || restart_background(&previous, new_end));
    history_to_dict(py, &history)
}

/// Execute independent serial members in a bounded native thread pool.
#[pyfunction]
#[pyo3(signature = (chart, y0s, t_eval, gamma, kappa = 0.0, rtol = 1e-10, atol = 1e-12, projection_mode = "off", threads = 1))]
#[allow(clippy::too_many_arguments)]
pub(crate) fn integrate_background_batch_history<'py>(
    py: Python<'py>,
    chart: &str,
    y0s: PyReadonlyArray2<f64>,
    t_eval: PyReadonlyArray1<f64>,
    gamma: f64,
    kappa: f64,
    rtol: f64,
    atol: f64,
    projection_mode: &str,
    threads: usize,
) -> PyResult<Bound<'py, PyList>> {
    let chart_value = make_scalar_chart(chart, gamma, kappa)?;
    let n = chart_value.nstates();
    let states = y0s.as_array();
    if states.ncols() != n {
        return Err(PyValueError::new_err(format!("y0s must be shape (K,{n})")));
    }
    let taus = t_eval.as_slice()?.to_vec();
    let mut requests = Vec::with_capacity(states.nrows());
    for row in states.rows() {
        requests.push(make_background_request(
            chart,
            row.to_vec(),
            taus.clone(),
            gamma,
            kappa,
            rtol,
            atol,
            projection_mode,
        )?);
    }
    let histories = py.detach(move || integrate_background_batch(requests, threads));
    let output = PyList::empty(py);
    for history in &histories {
        output.append(history_to_dict(py, history)?)?;
    }
    Ok(output)
}

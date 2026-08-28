//! RF-02C public geometry route identity adapter.

use numpy::ndarray::Array1;
use numpy::{IntoPyArray, PyArray1, PyReadonlyArray1};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

type GroupClassificationOutput = (String, String, Option<f64>, bool, (i32, i32, i32), i32);

const EXECUTION_ROUTE_IDENTITY: &str = r#"{"convention_hash":"ac824b10e966f7cdb680d4a1a62ccfb414a9479e84f3d72231eeb4c88f649b33","event_registry_hash":"8b3d342328b4549c797fca1c106181657f832a07fafed29eb498450465b43918","execution_contract_v2_hash":"804826b9d5ce2f3333de0558447e351a8050dc8147d268e8a6055b6c5669e51c","identity_schema":"bass-rf02c-public-execution-route/v2","native_capabilities":{"builtin_event_language":["state","parameter","const_f64_bits","add","sub","mul","neg"],"projection_routes":["chart_project","chart_project_checked"],"trajectory_ownership":"one_native_call_per_complete_trajectory","trajectory_routes":["integrate_background_history","restart_background_history","integrate_background_batch_history"]},"native_capability_receipt":"31129e99497c967cf9e09e2d3fdfa974eaa2c49ce4b01f3620da4c7e65215b55","native_payload_identity":"bass-rf02c-native-background-execution-v2","routing":{"class_b_exceptional_kappa":-9.0,"class_b_exceptional_routing_tolerance":1e-09},"routing_fingerprint":"a7689410ac496b952a63fea88b2c9139647087f0ace24e47068301cef25ba4f3","scalar_chart_schema_hash":"6e5fb51e028dc573a3759ac383dac948073e3a7f86f25564f26dfcbc10a10e7a","scalar_state_order":[{"chart":"class_a","constraint_names":[],"state_names":["Sigma_p","Sigma_m","N1","N2","N3"]},{"chart":"class_b","constraint_names":["codazzi"],"state_names":["Sigma_p","Sigma_tilde","Delta","A_tilde","N_p"]},{"chart":"exceptional","constraint_names":["g"],"state_names":["Sigma_p","Sigma_m","Sigma_2","Sigma_x","N_m","A"]},{"chart":"type_ix_d","constraint_names":["definition","trace"],"state_names":["H","S1","S2","S3","N1","N2","N3"]},{"chart":"type_ix_d_future","constraint_names":["definition","trace"],"state_names":["H","S1","S2","S3","N1","N2","N3"]}],"state_schema_hash":"9fa370fa32a5e0d7af7e8d97263db947a579d80c793e2818212b339a4b15e0f1","supported_chart_labels":["class_a","class_b","exceptional","type_ix_d","type_ix_d_future"]}"#;

#[pyfunction]
pub fn rf02c_execution_identity() -> &'static str {
    EXECUTION_ROUTE_IDENTITY
}

#[pyfunction]
pub fn qg_geometry_identity() -> &'static str {
    rf02c_execution_identity()
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
pub(crate) fn qg_classify(
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
pub(crate) fn qg_jacobi<'py>(
    py: Python<'py>,
    n: PyReadonlyArray1<f64>,
    a: PyReadonlyArray1<f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let g = _grp(&n, &a)?;
    Ok(Array1::from_vec(g.jacobi_residual().to_vec()).into_pyarray(py))
}

/// C^c_{ab} — (3,3,3) 평탄화 (인덱스 c*9 + a*3 + b).
#[pyfunction]
pub(crate) fn qg_structure_constants<'py>(
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
pub(crate) fn qg_ricci3<'py>(
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
pub(crate) fn qg_curvature<'py>(
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
pub(crate) fn qg_kappa(
    n: PyReadonlyArray1<f64>,
    a: PyReadonlyArray1<f64>,
) -> PyResult<Option<f64>> {
    Ok(_grp(&n, &a)?.kappa())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rf02c_geometry_identity_binds_frozen_route_fields() {
        assert!(EXECUTION_ROUTE_IDENTITY
            .contains("ac824b10e966f7cdb680d4a1a62ccfb414a9479e84f3d72231eeb4c88f649b33"));
        assert!(EXECUTION_ROUTE_IDENTITY
            .contains("9fa370fa32a5e0d7af7e8d97263db947a579d80c793e2818212b339a4b15e0f1"));
        assert!(EXECUTION_ROUTE_IDENTITY
            .contains("6e5fb51e028dc573a3759ac383dac948073e3a7f86f25564f26dfcbc10a10e7a"));
        assert!(EXECUTION_ROUTE_IDENTITY
            .contains("31129e99497c967cf9e09e2d3fdfa974eaa2c49ce4b01f3620da4c7e65215b55"));
        assert!(EXECUTION_ROUTE_IDENTITY
            .contains("a7689410ac496b952a63fea88b2c9139647087f0ace24e47068301cef25ba4f3"));
        assert!(EXECUTION_ROUTE_IDENTITY.contains("\"class_b_exceptional_kappa\":-9.0"));
        assert!(
            EXECUTION_ROUTE_IDENTITY.contains("\"class_b_exceptional_routing_tolerance\":1e-09")
        );
    }
}

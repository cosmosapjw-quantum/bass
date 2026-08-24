use super::*;

fn lebedev26() -> (Vec<[f64; 3]>, Vec<f64>) {
    let pi = std::f64::consts::PI;
    let a = 1.0 / 3.0_f64.sqrt();
    let b = 1.0 / 2.0_f64.sqrt();
    let mut e = Vec::new();
    let mut w = Vec::new();
    for k in 0..3 {
        for s in [-1.0, 1.0] {
            let mut x = [0.0; 3];
            x[k] = s;
            e.push(x);
            w.push(4.0 * pi / 21.0);
        }
    }
    for zero in 0..3 {
        let idx: Vec<_> = (0..3).filter(|&i| i != zero).collect();
        for s1 in [-1.0, 1.0] {
            for s2 in [-1.0, 1.0] {
                let mut x = [0.0; 3];
                x[idx[0]] = s1 * b;
                x[idx[1]] = s2 * b;
                e.push(x);
                w.push(16.0 * pi / 105.0);
            }
        }
    }
    for sx in [-1.0, 1.0] {
        for sy in [-1.0, 1.0] {
            for sz in [-1.0, 1.0] {
                e.push([sx * a, sy * a, sz * a]);
                w.push(9.0 * pi / 70.0);
            }
        }
    }
    (e, w)
}

type TMat = [[f64; 3]; 3];
fn tproj(e: [f64; 3]) -> TMat {
    let mut p = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            p[i][j] = if i == j { 1.0 } else { 0.0 } - e[i] * e[j];
        }
    }
    p
}
fn tmm(a: &TMat, b: &TMat) -> TMat {
    let mut c = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            for k in 0..3 {
                c[i][j] += a[i][k] * b[k][j];
            }
        }
    }
    c
}
fn tpack(m: &TMat) -> [f64; 9] {
    [
        m[0][0],
        m[1][1],
        m[2][2],
        0.5 * (m[0][1] + m[1][0]),
        0.5 * (m[0][2] + m[2][0]),
        0.5 * (m[1][2] + m[2][1]),
        0.5 * (m[1][2] - m[2][1]),
        0.5 * (m[2][0] - m[0][2]),
        0.5 * (m[0][1] - m[1][0]),
    ]
}
fn tunpack(p: &[f64]) -> TMat {
    [
        [p[0], p[3] + p[8], p[4] - p[7]],
        [p[3] - p[8], p[1], p[5] + p[6]],
        [p[4] + p[7], p[5] - p[6], p[2]],
    ]
}
fn mode_field(e: &[[f64; 3]], t: &TMat) -> Vec<f64> {
    let mut y = Vec::with_capacity(9 * e.len());
    for &x in e {
        let p = tproj(x);
        let j = tmm(&tmm(&p, t), &p);
        y.extend_from_slice(&tpack(&j));
    }
    y
}

#[test]
fn rest_frame_reproduces_trace_stf_and_v_spectrum() {
    let (e, w) = lebedev26();
    let trace = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]];
    let stf = [[1., 0., 0.], [0., -1., 0.], [0., 0., 0.]];
    let anti = [[0., 1., 0.], [-1., 0., 0.], [0., 0., 0.]];
    for (t, lambda) in [(trace, 0.0), (stf, -0.3), (anti, -0.5)] {
        let y = mode_field(&e, &t);
        let c = collision_generator_apply_polarized(&e, &w, 0.0, 1, &y);
        let err = c
            .iter()
            .zip(&y)
            .map(|(ci, yi)| (ci - lambda * yi).abs())
            .fold(0.0, f64::max);
        assert!(err < 8e-14, "lambda={lambda} defect={err:e}");
    }
}

#[test]
fn intensity_quadrupole_sources_linear_polarization_but_isotropy_does_not() {
    let (e, w) = lebedev26();
    let mut yiso = Vec::with_capacity(9 * e.len());
    let mut yani = Vec::with_capacity(9 * e.len());
    for &x in &e {
        let p = tproj(x);
        let ia = 1.0 + 0.8 * (x[2] * x[2] - 1.0 / 3.0);
        let mut ji = p;
        let mut ja = p;
        for i in 0..3 {
            for j in 0..3 {
                ji[i][j] *= 0.5;
                ja[i][j] *= 0.5 * ia;
            }
        }
        yiso.extend_from_slice(&tpack(&ji));
        yani.extend_from_slice(&tpack(&ja));
    }
    let ci = collision_generator_apply_polarized(&e, &w, 0.0, 1, &yiso);
    let ca = collision_generator_apply_polarized(&e, &w, 0.0, 1, &yani);
    assert!(max_abs(&ci) < 8e-14, "isotropic null={:e}", max_abs(&ci));
    let mut pol = 0.0_f64;
    for (k, &x) in e.iter().enumerate() {
        let j = tunpack(&ca[9 * k..9 * k + 9]);
        let p = tproj(x);
        let tr = j[0][0] + j[1][1] + j[2][2];
        let mut tf = j;
        for i in 0..3 {
            for q in 0..3 {
                tf[i][q] -= 0.5 * tr * p[i][q];
            }
        }
        let n = tf.iter().flatten().map(|z| z * z).sum::<f64>().sqrt();
        pol = pol.max(n);
    }
    assert!(pol > 1e-3, "quadrupole polarization={pol:e}");
}

fn dot3(a: [f64; 3], b: [f64; 3]) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}
fn cross3(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}
fn tangent_frame(e: [f64; 3]) -> ([f64; 3], [f64; 3]) {
    let mut k = 0usize;
    if e[1].abs() < e[k].abs() {
        k = 1;
    }
    if e[2].abs() < e[k].abs() {
        k = 2;
    }
    let mut a = [0.0; 3];
    a[k] = 1.0;
    let ae = dot3(a, e);
    let mut u = [a[0] - ae * e[0], a[1] - ae * e[1], a[2] - ae * e[2]];
    let n = dot3(u, u).sqrt();
    for x in &mut u {
        *x /= n;
    }
    let v = cross3(e, u);
    (u, v)
}
fn outer_add(j: &mut TMat, a: [f64; 3], b: [f64; 3], c: f64) {
    for i in 0..3 {
        for k in 0..3 {
            j[i][k] += c * a[i] * b[k];
        }
    }
}
fn stokes_matrix(e: [f64; 3], i0: f64, q: f64, u0: f64, v0: f64) -> TMat {
    let (u, v) = tangent_frame(e);
    let mut j = [[0.0; 3]; 3];
    outer_add(&mut j, u, u, 0.5 * (i0 + q));
    outer_add(&mut j, v, v, 0.5 * (i0 - q));
    outer_add(&mut j, u, v, 0.5 * (u0 + v0));
    outer_add(&mut j, v, u, 0.5 * (u0 - v0));
    j
}
fn cone_margin_and_screen_leak(e: &[[f64; 3]], y: &[f64]) -> (f64, f64) {
    let mut margin = f64::INFINITY;
    let mut leak = 0.0_f64;
    for (n, &dir) in e.iter().enumerate() {
        let j = tunpack(&y[9 * n..9 * n + 9]);
        let (u, v) = tangent_frame(dir);
        let ju = [dot3(j[0], u), dot3(j[1], u), dot3(j[2], u)];
        let jv = [dot3(j[0], v), dot3(j[1], v), dot3(j[2], v)];
        let uju = dot3(u, ju);
        let vjv = dot3(v, jv);
        let ujv = dot3(u, jv);
        let vju = dot3(v, ju);
        let i0 = uju + vjv;
        let q = uju - vjv;
        let u0 = ujv + vju;
        let v0 = ujv - vju;
        let lm = 0.5 * (i0 - (q * q + u0 * u0 + v0 * v0).sqrt());
        margin = margin.min(lm);
        let je = [dot3(j[0], dir), dot3(j[1], dir), dot3(j[2], dir)];
        leak = leak.max(dot3(je, je).sqrt());
    }
    (margin, leak)
}

#[test]
fn deep_rust_collision_exponential_preserves_coherency_cone() {
    let v = 0.1;
    let (e, w) = paired_grid(v);
    let mut y = Vec::with_capacity(9 * e.len());
    for (n, &dir) in e.iter().enumerate() {
        let x = n as f64;
        let i0 = 2.0 + 0.1 * x;
        let q = 0.3 * x.cos();
        let u0 = 0.2 * (0.7 * x).sin();
        let v0 = 0.1 * (0.4 * x).cos();
        y.extend_from_slice(&tpack(&stokes_matrix(dir, i0, q, u0, v0)));
    }
    let z = frozen_collision_step(&e, &w, v, 1, 20.0, &y, KrylovOptions::full(y.len())).unwrap();
    let (margin, leak) = cone_margin_and_screen_leak(&e, &z);
    println!("deep-cone margin={margin:.16e} screen_leak={leak:.16e}");
    assert!(margin > -2e-11, "coherency cone margin={margin:e}");
    assert!(leak < 2e-11, "screen leak={leak:e}");
}

fn l2(x: &[f64]) -> f64 {
    x.iter().map(|z| z * z).sum::<f64>().sqrt()
}

#[test]
fn actual_typeii_schedule_midpoint_kato_is_second_order_in_rust() {
    use typeii_v_schedule::{DT, T_END, V2, V2DOT};
    let (e, w) = rest_grid6();
    let raw: Vec<f64> = (0..9 * e.len())
        .map(|i| ((i * 37 + 11) % 101) as f64 / 53.0 - 0.8)
        .collect();
    let y0 = projector_apply_polarized(&e, &w, V2[0], 1, &raw);
    let hs = [0.05, 0.025, 0.0125, 0.00625, 0.003125];
    let mut errs = Vec::new();
    for &h in &hs {
        let stride = (h / DT).round() as usize;
        assert_eq!(stride % 2, 0);
        let steps = (T_END / h).round() as usize;
        let mut y = y0.clone();
        for k in 0..steps {
            let idx = k * stride + stride / 2;
            y = frozen_kato_step(
                &e,
                &w,
                V2[idx],
                V2DOT[idx],
                1,
                h,
                &y,
                KrylovOptions::full(y.len()),
            )
            .unwrap();
        }
        let py = projector_apply_polarized(&e, &w, V2[V2.len() - 1], 1, &y);
        let d: Vec<f64> = y.iter().zip(&py).map(|(a, b)| a - b).collect();
        errs.push(l2(&d) / l2(&y));
    }
    println!("actual-TypeII Kato endpoint errs={errs:?}");
    for pair in errs.windows(2) {
        let ratio = pair[0] / pair[1];
        assert!(
            (3.85..4.15).contains(&ratio),
            "non-second-order ratio={ratio:e} errs={errs:?}"
        );
    }
    assert!(errs[4] < 4e-10, "finest endpoint defect={:e}", errs[4]);
}

#[test]
fn symmetric_input_does_not_generate_v() {
    let v = 0.1;
    let (e, w) = paired_grid(v);
    // A genuinely linearly polarized symmetric screen field, not merely an
    // unpolarized intensity rescaling.
    let t = [[1.0, 0.2, 0.3], [0.2, -0.4, 0.1], [0.3, 0.1, 0.7]];
    let y = mode_field(&e, &t);
    let c = collision_generator_apply_polarized(&e, &w, v, 1, &y);
    let anti = (0..e.len())
        .flat_map(|i| [c[9 * i + 6], c[9 * i + 7], c[9 * i + 8]])
        .map(f64::abs)
        .fold(0.0, f64::max);
    assert!(anti < 2e-14, "V generated={anti:e}");
}

use bianchi_rustcore::generated::typeii_polarized_stokes::{
    active_rotate_stokes, active_rotate_tensor, packed_to_stokes, passive_rotate_stokes,
    stokes_to_packed, Handedness, ScreenDyad, Stokes, StokesError,
};

fn assert_close(a: f64, b: f64, tol: f64) {
    assert!((a - b).abs() <= tol, "{a:.17e} != {b:.17e}; tol={tol:.3e}");
}

fn assert_stokes_close(a: Stokes, b: Stokes, tol: f64) {
    assert_close(a.i, b.i, tol);
    assert_close(a.q, b.q, tol);
    assert_close(a.u, b.u, tol);
    assert_close(a.v, b.v, tol);
}

fn canonical() -> ScreenDyad {
    ScreenDyad::new([0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], 1e-13).unwrap()
}

#[test]
fn tensor_stokes_roundtrip_seals_existing_pack9_sign() {
    let d = canonical();
    let s = Stokes {
        i: 2.4,
        q: 0.6,
        u: -0.8,
        v: 0.4,
    };
    let p = stokes_to_packed(s, &d).unwrap();
    // Existing BASS pack9/unpack9 convention: packed[8] = -V/2 on (x,y,z).
    assert_close(p[8], -0.5 * s.v, 1e-15);
    assert_stokes_close(packed_to_stokes(&p, &d).unwrap(), s, 2e-15);
}

#[test]
fn passive_rotation_has_negative_spin_two_phase() {
    let s = Stokes {
        i: 2.0,
        q: 0.7,
        u: -0.3,
        v: 0.2,
    };
    for psi in [
        0.0,
        0.17,
        -0.31,
        std::f64::consts::FRAC_PI_4,
        -std::f64::consts::FRAC_PI_2,
    ] {
        let got = passive_rotate_stokes(s, psi).unwrap();
        let (sn, c) = (2.0 * psi).sin_cos();
        let expected = Stokes {
            i: s.i,
            q: c * s.q + sn * s.u,
            u: c * s.u - sn * s.q,
            v: s.v,
        };
        assert_stokes_close(got, expected, 2e-15);
    }
}

#[test]
fn active_rotation_has_positive_spin_two_phase() {
    let s = Stokes {
        i: 1.6,
        q: -0.4,
        u: 0.9,
        v: -0.1,
    };
    for psi in [
        0.0,
        0.23,
        -0.41,
        std::f64::consts::FRAC_PI_4,
        std::f64::consts::FRAC_PI_2,
    ] {
        let got = active_rotate_stokes(s, psi).unwrap();
        let (sn, c) = (2.0 * psi).sin_cos();
        let expected = Stokes {
            i: s.i,
            q: c * s.q - sn * s.u,
            u: sn * s.q + c * s.u,
            v: s.v,
        };
        assert_stokes_close(got, expected, 2e-15);
    }
}

#[test]
fn active_tensor_route_matches_active_stokes_route() {
    let d = ScreenDyad::canonical([0.31, -0.42, 0.852584306]).unwrap();
    let s = Stokes {
        i: 3.0,
        q: 0.4,
        u: -0.7,
        v: 0.25,
    };
    let p = stokes_to_packed(s, &d).unwrap();
    for psi in [-0.61, -0.2, 0.0, 0.37, 1.1] {
        let pr = active_rotate_tensor(&p, d.e(), psi).unwrap();
        let got = packed_to_stokes(&pr, &d).unwrap();
        assert_stokes_close(got, active_rotate_stokes(s, psi).unwrap(), 4e-14);
    }
}

#[test]
fn equal_active_and_passive_rotations_cancel() {
    let s = Stokes {
        i: 1.9,
        q: -0.2,
        u: 0.75,
        v: 0.12,
    };
    for psi in [-0.73, -0.17, 0.33, 0.91] {
        let got = passive_rotate_stokes(active_rotate_stokes(s, psi).unwrap(), psi).unwrap();
        assert_stokes_close(got, s, 3e-15);
    }
}

#[test]
fn handedness_flip_changes_u_and_v_only() {
    let d = canonical();
    let left = d.with_handedness(Handedness::Left);
    let s = Stokes {
        i: 2.1,
        q: 0.8,
        u: -0.5,
        v: 0.3,
    };
    let p = stokes_to_packed(s, &d).unwrap();
    assert_stokes_close(
        packed_to_stokes(&p, &left).unwrap(),
        Stokes {
            i: s.i,
            q: s.q,
            u: -s.u,
            v: -s.v,
        },
        2e-15,
    );
}

#[test]
fn rotations_preserve_intensity_circular_polarization_and_cone_scalar() {
    let s = Stokes {
        i: 3.0,
        q: 0.8,
        u: -0.6,
        v: 0.4,
    };
    let cone = s.cone_scalar();
    for psi in [-2.1, -0.4, 0.0, 0.7, 2.4] {
        for got in [
            passive_rotate_stokes(s, psi).unwrap(),
            active_rotate_stokes(s, psi).unwrap(),
        ] {
            assert_close(got.i, s.i, 1e-15);
            assert_close(got.v, s.v, 1e-15);
            assert_close(got.q * got.q + got.u * got.u, s.q * s.q + s.u * s.u, 3e-15);
            assert_close(got.cone_scalar(), cone, 5e-15);
        }
    }
}

#[test]
fn pure_screen_rotation_does_not_generate_v() {
    let s = Stokes {
        i: 1.0,
        q: 0.4,
        u: 0.2,
        v: 0.0,
    };
    for psi in [-1.3, -0.2, 0.4, 1.7] {
        assert_close(passive_rotate_stokes(s, psi).unwrap().v, 0.0, 0.0);
        assert_close(active_rotate_stokes(s, psi).unwrap().v, 0.0, 0.0);
    }
}

#[test]
fn invalid_dyads_angles_and_states_fail_closed() {
    assert!(matches!(
        ScreenDyad::new([0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0], 1e-12),
        Err(StokesError::InvalidDyad)
    ));
    assert!(matches!(
        passive_rotate_stokes(
            Stokes {
                i: 1.0,
                q: 0.0,
                u: 0.0,
                v: 0.0
            },
            f64::NAN
        ),
        Err(StokesError::NonFiniteAngle)
    ));
    assert!(matches!(
        stokes_to_packed(
            Stokes {
                i: f64::INFINITY,
                q: 0.0,
                u: 0.0,
                v: 0.0
            },
            &canonical()
        ),
        Err(StokesError::NonFiniteStokes)
    ));
}

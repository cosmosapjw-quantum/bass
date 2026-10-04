use rei_microphysics::{hydrogen_step, HydrogenRates};

fn rates(p: f64, c: f64, s: f64, r: f64) -> HydrogenRates {
    HydrogenRates {
        photo_per_s: p,
        collisional_per_s: c,
        secondary_per_s: s,
        recombination_per_s: r,
    }
}
fn close(a: f64, b: f64) {
    assert!(a.is_finite());
    assert!(
        (a - b).abs() <= 4e-14 * b.abs().max(1e-300),
        "{a:e} != {b:e}"
    );
}
#[test]
fn identity_zero_time_and_zero_rates() {
    for x in [0., 0.37, 1.] {
        for (dt, q) in [(0., rates(1., 2., 3., 4.)), (10., rates(0., 0., 0., 0.))] {
            let a = hydrogen_step(x, dt, q).unwrap();
            assert_eq!(a.x_next, x);
            assert_eq!(
                [
                    a.photo_events,
                    a.collisional_events,
                    a.secondary_events,
                    a.recombination_events
                ],
                [0.; 4]
            );
        }
    }
}
#[test]
fn separate_channels_and_equilibrium_balance() {
    let a = hydrogen_step(0.6, 2., rates(0.5, 0.75, 0.25, 1.)).unwrap();
    close(a.x_next, 0.6);
    close(a.photo_events, 0.4);
    close(a.collisional_events, 0.6);
    close(a.secondary_events, 0.2);
    close(a.recombination_events, 1.2);
    let a = hydrogen_step(1., 1., rates(0., 0., 1., 0.)).unwrap();
    assert_eq!(a.x_next, 1.);
    assert_eq!(a.secondary_events, 0.);
}
#[test]
fn limiting_cases() {
    let p = hydrogen_step(0., 0.5, rates(2., 0., 0., 0.)).unwrap();
    close(p.x_next, 0.6321205588285577);
    close(p.photo_events, p.x_next);
    let r = hydrogen_step(1., 0.5, rates(0., 0., 0., 2.)).unwrap();
    close(r.x_next, 0.36787944117144233);
    close(r.recombination_events, 0.6321205588285577);
}
#[test]
fn tiny_depth_retains_creation_from_initially_ionized_gas() {
    let a = hydrogen_step(1., 1., rates(1e-12, 0., 0., 1e-12)).unwrap();
    close(a.photo_events, 4.999999999996667e-25);
    close(a.recombination_events, 9.999999999995e-13);
    let a = hydrogen_step(0., 1., rates(f64::from_bits(1), 0., 0., 0.)).unwrap();
    assert_eq!(a.x_next.to_bits(), 1);
    assert_eq!(a.photo_events.to_bits(), 1);
}
#[test]
fn ledger_and_semigroup() {
    for x in [0., 0.1, 0.6, 1.] {
        for dt in [1e-14, 0.1, 1., 100.] {
            let q = rates(0.5, 0.75, 0.25, 1.);
            let a = hydrogen_step(x, dt, q).unwrap();
            let b = hydrogen_step(x, dt / 2., q).unwrap();
            let c = hydrogen_step(b.x_next, dt / 2., q).unwrap();
            assert!((0. ..=1.).contains(&a.x_next));
            for n in [
                a.photo_events,
                a.collisional_events,
                a.secondary_events,
                a.recombination_events,
            ] {
                assert!(n.is_finite() && n >= 0.);
            }
            let net =
                a.photo_events + a.collisional_events + a.secondary_events - a.recombination_events;
            assert!((a.x_next - x - net).abs() < 1e-13 * (1. + dt));
            assert!((a.x_next - c.x_next).abs() < 2e-15);
            for (u, v, w) in [
                (a.photo_events, b.photo_events, c.photo_events),
                (
                    a.collisional_events,
                    b.collisional_events,
                    c.collisional_events,
                ),
                (a.secondary_events, b.secondary_events, c.secondary_events),
                (
                    a.recombination_events,
                    b.recombination_events,
                    c.recombination_events,
                ),
            ] {
                assert!((u - v - w).abs() < 1e-13 * (1. + dt));
            }
        }
    }
}
#[test]
fn invalid_inputs_and_finite_overflow_reject() {
    for x in [-1., 1.1, f64::NAN, f64::INFINITY] {
        assert!(hydrogen_step(x, 1., rates(1., 0., 0., 1.)).is_err());
    }
    for dt in [-1., f64::NAN, f64::INFINITY] {
        assert!(hydrogen_step(0.5, dt, rates(1., 0., 0., 1.)).is_err());
    }
    for n in [-1., f64::NAN, f64::INFINITY] {
        for q in [
            rates(n, 0., 0., 0.),
            rates(0., n, 0., 0.),
            rates(0., 0., n, 0.),
            rates(0., 0., 0., n),
        ] {
            assert!(hydrogen_step(0.5, 1., q).is_err());
        }
    }
    assert!(hydrogen_step(0.5, 1., rates(1e308, 1e308, 0., 0.)).is_err());
    assert!(hydrogen_step(0.5, 1e308, rates(2., 0., 0., 0.)).is_err());
}

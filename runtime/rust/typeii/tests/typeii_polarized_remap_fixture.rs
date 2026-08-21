use bianchi_rustcore::generated::typeii_polarized_remap::{remap_convex_packed, RemapOptions};

mod fixture {
    include!("support/typeii_polarized_remap_fixture.rs");
}

fn max_abs9(a: &[f64; 9], b: &[f64; 9]) -> f64 {
    (0..9).map(|i| (a[i] - b[i]).abs()).fold(0.0, f64::max)
}

#[test]
fn independent_scipy_shortest_geodesic_fixture_matches() {
    let out = remap_convex_packed(
        &fixture::SOURCE_DIRECTIONS,
        &fixture::SOURCE_STATES,
        &fixture::WEIGHTS,
        fixture::TARGET,
        RemapOptions::default(),
    )
    .unwrap();
    let error = max_abs9(&out.packed, &fixture::EXPECTED_OUTPUT);
    println!("fixture_max_abs_error={error:.17e}");
    println!(
        "minimum_transport_dot={:.17e}",
        out.diagnostics.minimum_transport_dot
    );
    assert!(error < 3.0e-14, "max error={}", error);
    assert!(
        (out.diagnostics.minimum_transport_dot - fixture::EXPECTED_MINIMUM_TRANSPORT_DOT).abs()
            < 5.0e-15
    );
}

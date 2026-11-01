//! Real compiled original RustCore geometry + generated Type-II RHS on 401 exact source states.
use bass_typeii_source_bound_host_check::runtime::typeii_host::{
    OriginalTypeIIBackground, TypeIIState5,
};
use std::io::{self, BufRead};

fn maxdiff(a: &[f64; 5], b: &[f64; 5]) -> f64 {
    a.iter()
        .zip(b)
        .map(|(x, y)| (x - y).abs())
        .fold(0.0, f64::max)
}

fn main() {
    let mut count = 0usize;
    let mut max_source_rhs = 0.0_f64;
    let mut max_codazzi = 0.0_f64;
    let mut max_roundtrip = 0.0_f64;
    let mut max_rhs_tangency = 0.0_f64;
    for line in io::stdin().lock().lines() {
        let line = line.expect("stdin read failed");
        let numbers: Vec<f64> = line
            .split(',')
            .map(|s| s.parse::<f64>().expect("f64 parse"))
            .collect();
        assert_eq!(
            numbers.len(),
            10,
            "each fixture row must contain five state and five rhs scalars"
        );
        let x: [f64; 5] = numbers[0..5].try_into().unwrap();
        let expected: [f64; 5] = numbers[5..10].try_into().unwrap();
        let state = TypeIIState5 { x, gamma: 1.3 };
        let host = state
            .to_host()
            .expect("source fixture violates physical chart");
        let back = host.to_typeii().expect("source host roundtrip invalid");
        let got = OriginalTypeIIBackground::rhs(&host).expect("callback failure");
        let induced = OriginalTypeIIBackground::physical_rhs_four(&host).unwrap();
        let tangent = state.tangent_lift(induced).expect("bad tangent chart");
        let reconstructed = TypeIIState5::from_four(x[0], x[1], x[3], x[4], 1.3)
            .expect("failed physical chart reconstruction");
        max_source_rhs = max_source_rhs.max(maxdiff(&got, &expected));
        max_codazzi = max_codazzi.max(state.codazzi().unwrap().abs());
        max_roundtrip = max_roundtrip
            .max(maxdiff(&x, &back.x))
            .max(maxdiff(&x, &reconstructed.x));
        max_rhs_tangency = max_rhs_tangency.max((tangent[2] - got[2]).abs());
        count += 1;
    }
    assert_eq!(count, 401, "must consume all original 401 states");
    assert!(
        max_source_rhs < 2.0e-12,
        "source RHS mismatch {max_source_rhs}"
    );
    assert!(
        max_codazzi < 1.0e-12,
        "source Codazzi mismatch {max_codazzi}"
    );
    assert!(
        max_roundtrip < 1.0e-12,
        "host map/4D chart mismatch {max_roundtrip}"
    );
    assert!(
        max_rhs_tangency < 5.0e-11,
        "source RHS not 4D tangent {max_rhs_tangency}"
    );
    println!("SOURCE_BOUND_401_PASS rows={count} max_source_rhs={max_source_rhs:.5e} max_codazzi={max_codazzi:.5e} max_roundtrip={max_roundtrip:.5e} max_rhs_tangency={max_rhs_tangency:.5e}");
}

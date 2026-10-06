// Compile the exact production module, not a copy or a substitute extension.
#[path = "../../_rustcore/src/kinetic/constraints.rs"]
mod constraints;
use std::io::{self, BufRead};
fn main() {
    for line in io::stdin().lock().lines() {
        let values: Vec<f64> = line
            .unwrap()
            .split_whitespace()
            .map(|x| x.parse().unwrap())
            .collect();
        assert_eq!(values.len(), 24);
        let result = constraints::codazzi_residual(
            values[0..9].try_into().unwrap(),
            values[9..18].try_into().unwrap(),
            values[18..21].try_into().unwrap(),
            values[21..24].try_into().unwrap(),
        );
        match result {
            Ok(r) => println!("{:.17e} {:.17e} {:.17e}", r[0], r[1], r[2]),
            Err(e) => println!("ERROR: {e}"),
        }
    }
}

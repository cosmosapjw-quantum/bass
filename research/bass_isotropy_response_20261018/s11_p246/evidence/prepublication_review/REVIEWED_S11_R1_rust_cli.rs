//! Compile directly with rustc cli.rs -O -o p246_projector (no Cargo).
//! Usage: p246_projector --isotropic-birth < input.txt
//! Input: order (4 or 6), ray count, then exactly that many mu/prior pairs.
//! Success is provisional until an independent exact moment certificate passes.

mod projector;
use std::io::{self, Read};

fn quoted(text: &str) -> String {
    let mut out = String::from("\"");
    for c in text.chars() {
        match c {
            '\\' => out.push_str("\\\\"),
            '"' => out.push_str("\\\""),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if c.is_control() => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out.push('"');
    out
}

fn fail(status: &str, message: &str, exit: i32) -> ! {
    println!(
        "{{\"status\":{},\"message\":{}}}",
        quoted(status),
        quoted(message)
    );
    std::process::exit(exit)
}

fn array(values: &[f64]) -> String {
    format!(
        "[{}]",
        values
            .iter()
            .map(|x| format!("{:.17e}", x))
            .collect::<Vec<_>>()
            .join(",")
    )
}

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.len() != 1 || args[0] != "--isotropic-birth" {
        fail("NOT_ISOTROPIC_BIRTH","supply --isotropic-birth for a new explicitly isotropic birth; stdin is order n and n mu/prior pairs",2);
    }
    let mut input = String::new();
    // The API has a 4096-ray bound; reject unreasonably large textual inputs as
    // an input-contract error before parsing, independent of solver budgets.
    match io::stdin().take(1_048_577).read_to_string(&mut input) {
        Ok(_) => (),
        Err(e) => fail("INVALID_INPUT", &format!("cannot read stdin: {}", e), 2),
    }
    if input.len() > 1_048_576 {
        fail("INVALID_INPUT", "stdin exceeds one MiB", 2);
    }
    let mut tokens = input.split_whitespace();
    let order: u8 = tokens
        .next()
        .and_then(|v| v.parse().ok())
        .unwrap_or_else(|| fail("INVALID_INPUT", "missing or invalid order", 2));
    let n: usize = tokens
        .next()
        .and_then(|v| v.parse().ok())
        .unwrap_or_else(|| fail("INVALID_INPUT", "missing or invalid ray count", 2));
    if n == 0 || n > 4096 {
        fail("INVALID_INPUT", "ray count must lie in 1..=4096", 2);
    }
    let mut mu = Vec::with_capacity(n);
    let mut prior = Vec::with_capacity(n);
    for i in 0..n {
        let a: f64 = tokens
            .next()
            .and_then(|v| v.parse().ok())
            .unwrap_or_else(|| {
                fail(
                    "INVALID_INPUT",
                    &format!("missing or invalid direction {}", i),
                    2,
                )
            });
        let b: f64 = tokens
            .next()
            .and_then(|v| v.parse().ok())
            .unwrap_or_else(|| {
                fail(
                    "INVALID_INPUT",
                    &format!("missing or invalid prior {}", i),
                    2,
                )
            });
        mu.push(a);
        prior.push(b);
    }
    if tokens.next().is_some() {
        fail("INVALID_INPUT", "extra input tokens", 2);
    }
    match projector::project(&mu,&prior,order,true) {
        Ok(result) => println!(
            "{{\"status\":\"PROJECTED_NEEDS_EXACT_CERTIFICATE\",\"order\":{},\"iterations\":{},\"weights\":{},\"lambda\":{},\"residuals\":{},\"support\":{{\"distinct_squared_nodes\":{},\"facet_count\":{},\"minimum_certified_slack_lower\":{:.17e}}}}}",
            order,result.iterations,array(&result.weights),array(&result.lambda),array(&result.residuals),
            result.support.distinct_squared_nodes,result.support.facet_count,result.support.minimum_certified_slack_lower),
        Err(e) => fail(e.status,&e.message,3),
    }
}

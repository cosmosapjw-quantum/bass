//! Small text protocol for comparing independently exported production callbacks.
use bass_s9_ad_check::{Cohort, FrozenBank};
use std::{fs::OpenOptions, io::{BufRead, BufReader, Write}, path::Path};

fn number(s: &str) -> Result<f64, String> {
    let value: f64 = s.parse().map_err(|_| format!("invalid number {s}"))?;
    if !value.is_finite() { return Err("nonfinite input".into()); }
    Ok(value)
}

fn array(values: [f64; 3]) -> String {
    format!("[{:.17e},{:.17e},{:.17e}]", values[0], values[1], values[2])
}

fn run(input: &Path, output: &Path) -> Result<(), String> {
    let reader = BufReader::new(std::fs::File::open(input).map_err(|e| e.to_string())?);
    let mut writer = OpenOptions::new().write(true).create_new(true).open(output)
        .map_err(|e| e.to_string())?;
    // CASE id x h b y donor_amplitude Lambda time_seed v_h v_b v_y
    // COHORT u b_birth energy_birth
    // RAY mu alpha  (one row per source-frame ray)
    // END_COHORT
    // END_CASE
    let mut current: Option<(String, f64, [f64; 3], f64, [f64; 3], FrozenBank)> = None;
    let mut cohort: Option<Cohort> = None;
    for (line_no, line) in reader.lines().enumerate() {
        let line = line.map_err(|e| e.to_string())?;
        let fields: Vec<_> = line.split_whitespace().collect();
        if fields.is_empty() || fields[0].starts_with('#') { continue; }
        let error = || format!("protocol error at line {}", line_no + 1);
        match fields[0] {
            "CASE" if fields.len() == 12 && current.is_none() && cohort.is_none() => {
                if fields[1].len() > 128 || !fields[1].bytes().all(|b| b.is_ascii_alphanumeric() || b"_-".contains(&b)) {
                    return Err(error());
                }
                let values: Vec<f64> = fields[2..].iter().map(|s| number(s)).collect::<Result<_, _>>()?;
                current = Some((fields[1].into(), values[0], [values[1],values[2],values[3]],
                    values[6], [values[7],values[8],values[9]], FrozenBank { cohorts: vec![],
                    donor_amplitude: values[4], cosmological_constant: values[5] }));
            }
            "COHORT" if fields.len() == 4 && current.is_some() && cohort.is_none() => {
                cohort = Some(Cohort { u: number(fields[1])?, b_birth: number(fields[2])?,
                    energy_birth: number(fields[3])?, mu: vec![], alpha: vec![] });
            }
            "RAY" if fields.len() == 3 && cohort.is_some() => {
                let c = cohort.as_mut().unwrap(); c.mu.push(number(fields[1])?); c.alpha.push(number(fields[2])?);
            }
            "END_COHORT" if fields.len() == 1 && cohort.is_some() && current.is_some() => {
                current.as_mut().unwrap().5.cohorts.push(cohort.take().unwrap());
            }
            "END_CASE" if fields.len() == 1 && current.is_some() && cohort.is_none() => {
                let (id, x, state, time_seed, direction, bank) = current.take().unwrap();
                let result = bank.oracle(x, state, time_seed, direction).map_err(|e| format!("{id}: {e}"))?;
                writeln!(writer, "{{\"id\":\"{id}\",\"rhs\":{},\"jvp\":{},\"partial_t\":{},\"total_direction\":{}}}",
                    array(result.rhs), array(result.jvp), array(result.partial_t), array(result.total_direction))
                    .map_err(|e| e.to_string())?;
            }
            _ => return Err(error()),
        }
    }
    if current.is_some() || cohort.is_some() { return Err("incomplete final case".into()); }
    writer.flush().map_err(|e| e.to_string())
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    if args.len() != 4 || args[1] != "--oracle" {
        eprintln!("usage: bass-s9-ad-check --oracle INPUT.txt NEW_OUTPUT.jsonl");
        std::process::exit(2);
    }
    if let Err(error) = run(Path::new(&args[2]), Path::new(&args[3])) {
        eprintln!("{error}"); std::process::exit(3);
    }
}

//! Dependency-free batch protocol. Compile directly with rustc core_cli.rs.
//! Parsing/preparation, diagnostic evaluation and optional timed repetitions
//! are accounted separately. Exact birth admission belongs to the history
//! adapter; this executable evaluates supplied immutable physical/memory data.
mod core;

use core::{Bank, Cohort, Error, Evaluator, Mode};
use std::hint::black_box;
use std::io::{self, Read, Write};
use std::time::Instant;

#[derive(Clone)]
struct Query {
    x: f64,
    state: [f64; 6],
    direction: [f64; 6],
}

struct Tokens<'a> {
    words: std::str::SplitWhitespace<'a>,
}
impl<'a> Tokens<'a> {
    fn take(&mut self) -> Result<&'a str, Error> {
        self.words
            .next()
            .ok_or_else(|| Error::new("INPUT_TRUNCATED", "expected another token"))
    }
    fn label(&mut self, label: &str) -> Result<(), Error> {
        let got = self.take()?;
        if got != label {
            return Err(Error::new(
                "INPUT_LABEL",
                format!("expected {label}, got {got}"),
            ));
        }
        Ok(())
    }
    fn number(&mut self) -> Result<f64, Error> {
        let s = self.take()?;
        let v: f64 = s.parse().map_err(|_| Error::new("INPUT_FLOAT", s))?;
        if !v.is_finite() {
            return Err(Error::new("INPUT_NONFINITE", s));
        }
        Ok(v)
    }
    fn count(&mut self, max: usize) -> Result<usize, Error> {
        let s = self.take()?;
        let n: usize = s.parse().map_err(|_| Error::new("INPUT_COUNT", s))?;
        if n > max {
            return Err(Error::new("INPUT_LIMIT", format!("{n} exceeds {max}")));
        }
        Ok(n)
    }
}

fn parse(text: &str) -> Result<(Bank, Vec<Query>), Error> {
    let mut t = Tokens {
        words: text.split_whitespace(),
    };
    t.label("BASS_S12_CORE_V1")?;
    t.label("BANK")?;
    let donor0 = t.number()?;
    let decay_lambda = t.number()?;
    let exposure = t.number()?;
    let cosmological_constant = t.number()?;
    let nc = t.count(core::MAX_COHORTS)?;
    let nq = t.count(10_000)?;
    if nq == 0 {
        return Err(Error::new("INPUT_QUERIES", "at least one query required"));
    }
    let mut cohorts = Vec::with_capacity(nc);
    let mut total = 0usize;
    for _ in 0..nc {
        t.label("COHORT")?;
        let u = t.number()?;
        let b_birth = t.number()?;
        let energy_birth = t.number()?;
        let memory_theta = t.number()?;
        let n = t.count(core::MAX_RAYS)?;
        total = total
            .checked_add(n)
            .ok_or_else(|| Error::new("INPUT_LIMIT", "ray count overflow"))?;
        if total > core::MAX_TOTAL_RAYS {
            return Err(Error::new("INPUT_LIMIT", "total rays exceed limit"));
        }
        let (mut mu, mut alpha, mut mu_theta, mut alpha_theta) = (
            Vec::with_capacity(n),
            Vec::with_capacity(n),
            Vec::with_capacity(n),
            Vec::with_capacity(n),
        );
        for _ in 0..n {
            t.label("RAY")?;
            mu.push(t.number()?);
            alpha.push(t.number()?);
            mu_theta.push(t.number()?);
            alpha_theta.push(t.number()?);
        }
        cohorts.push(Cohort {
            u,
            b_birth,
            energy_birth,
            memory_theta,
            mu,
            alpha,
            mu_theta,
            alpha_theta,
        });
    }
    let mut queries = Vec::with_capacity(nq);
    for _ in 0..nq {
        t.label("QUERY")?;
        let x = t.number()?;
        let mut state = [0.0; 6];
        let mut direction = [0.0; 6];
        for v in &mut state {
            *v = t.number()?;
        }
        for v in &mut direction {
            *v = t.number()?;
        }
        queries.push(Query {
            x,
            state,
            direction,
        });
    }
    if t.words.next().is_some() {
        return Err(Error::new("INPUT_TRAILING", "unconsumed input token"));
    }
    Ok((
        Bank {
            cohorts,
            donor0,
            decay_lambda,
            exposure,
            cosmological_constant,
        },
        queries,
    ))
}

fn line(out: &mut impl Write, label: &str, xs: impl IntoIterator<Item = f64>) -> io::Result<()> {
    write!(out, "{label}")?;
    for x in xs {
        write!(out, " {x:.17e}")?;
    }
    writeln!(out)
}

fn run() -> Result<(), Error> {
    let mut mode = None;
    let mut repeat = 0usize;
    let mut args = std::env::args().skip(1);
    while let Some(a) = args.next() {
        match a.as_str() {
            "--mode" if mode.is_none() => {
                mode = Some(Mode::parse(
                    &args
                        .next()
                        .ok_or_else(|| Error::new("ARGS", "missing mode"))?,
                )?);
            }
            "--repeat" if repeat == 0 => {
                let raw = args
                    .next()
                    .ok_or_else(|| Error::new("ARGS", "missing repeat count"))?;
                repeat = raw
                    .parse()
                    .map_err(|_| Error::new("ARGS", "invalid repeat count"))?;
                if repeat == 0 || repeat > 1_000_000 {
                    return Err(Error::new("ARGS", "repeat must be in 1..1000000"));
                }
            }
            _ => {
                return Err(Error::new(
                    "ARGS",
                    "usage: --mode baseline|fused [--repeat N]",
                ));
            }
        }
    }
    let mode = mode.ok_or_else(|| Error::new("ARGS", "--mode is required"))?;
    let mut bytes = Vec::new();
    io::stdin()
        .take(64 * 1024 * 1024 + 1)
        .read_to_end(&mut bytes)
        .map_err(|e| Error::new("INPUT_IO", e.to_string()))?;
    if bytes.len() > 64 * 1024 * 1024 {
        return Err(Error::new("INPUT_LIMIT", "stdin exceeds 64MiB"));
    }
    let input =
        std::str::from_utf8(&bytes).map_err(|_| Error::new("INPUT_UTF8", "UTF-8 required"))?;
    let parse_start = Instant::now();
    let (bank, queries) = parse(input)?;
    let parse_ns = parse_start.elapsed().as_nanos();
    if repeat
        .checked_mul(queries.len())
        .is_none_or(|n| n > 100_000_000)
    {
        return Err(Error::new(
            "WORKLOAD_LIMIT",
            "timed query count exceeds 100000000",
        ));
    }
    let prepare_start = Instant::now();
    let evaluator = Evaluator::new(bank, mode)?;
    let prepare_ns = prepare_start.elapsed().as_nanos();
    let mut rows = Vec::with_capacity(queries.len());
    for q in &queries {
        let e = evaluator.eval(q.x, q.state)?;
        let v = e.jvp(q.direction)?;
        rows.push((e, v));
    }
    let start = Instant::now();
    let mut checksum = 0.0;
    for _ in 0..repeat {
        for q in &queries {
            let e = black_box(evaluator.eval(black_box(q.x), black_box(q.state))?);
            checksum += black_box(e.rhs[0]);
        }
    }
    let elapsed_ns = start.elapsed().as_nanos();
    if !checksum.is_finite() {
        return Err(Error::new("TIMING_CHECKSUM", "nonfinite checksum"));
    }
    let stdout = io::stdout();
    let mut out = io::BufWriter::new(stdout.lock());
    let emit = |out: &mut io::BufWriter<io::StdoutLock<'_>>| -> io::Result<()> {
        writeln!(out, "BASS_S12_CORE_OUTPUT_V1")?;
        writeln!(out, "MODE {}", mode.name())?;
        writeln!(out, "ROWS {}", rows.len())?;
        for (i, (e, jv)) in rows.iter().enumerate() {
            writeln!(out, "ROW {i}")?;
            line(out, "RHS", e.rhs)?;
            line(out, "JVP", *jv)?;
            line(out, "PT", e.partial_t)?;
            line(out, "JAC", e.jacobian.iter().flatten().copied())?;
            line(out, "MOMENTS", e.moments)?;
        }
        out.flush()
    };
    emit(&mut out).map_err(|e| Error::new("OUTPUT_IO", e.to_string()))?;
    eprintln!(
        "{{\"schema\":\"BASS_S12_CORE_TIMING_V1\",\"mode\":\"{}\",\"queries\":{},\"diagnostic_evaluations\":{},\"repeat\":{},\"timed_evaluations\":{},\"parse_ns\":{},\"prepare_ns\":{},\"elapsed_ns\":{},\"checksum\":{:.17e}}}",
        mode.name(),
        queries.len(),
        queries.len(),
        repeat,
        repeat * queries.len(),
        parse_ns,
        prepare_ns,
        elapsed_ns,
        checksum
    );
    Ok(())
}

fn main() {
    if let Err(e) = run() {
        eprintln!("S12_ERROR {} {}", e.code, e.detail);
        let code = if e.code.starts_with("INPUT") || e.code == "ARGS" || e.code == "WORKLOAD_LIMIT"
        {
            2
        } else {
            3
        };
        std::process::exit(code);
    }
}

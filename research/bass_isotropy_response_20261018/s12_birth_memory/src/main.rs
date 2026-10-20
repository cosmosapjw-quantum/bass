//! JSON CLI for the isolated S12 history client.
//!
//! Required hashes are checked before execution. Source identity is an external
//! immutable commit supplied by the published build wrapper; executable and
//! exact stdin hashes are computed here. A checkpoint cannot be resumed with a
//! changed source pin, input byte stream or executable.

use bass_s12_birth_memory::history::{Binding, Input, MAX_INPUT_BYTES, RunOptions, run, sha256};
use serde_json::json;
use std::fs;
use std::io::{self, Read, Write};
use std::path::PathBuf;
use std::process::ExitCode;

struct Args {
    source_commit: String,
    input_sha256: String,
    checkpoint_path: Option<PathBuf>,
    resume_path: Option<PathBuf>,
}
fn parse_args() -> Result<Args, String> {
    let mut source = None;
    let mut input = None;
    let mut checkpoint = None;
    let mut resume = None;
    let mut args = std::env::args().skip(1);
    while let Some(flag) = args.next() {
        let value = args
            .next()
            .ok_or_else(|| format!("missing value for {flag}"))?;
        match flag.as_str() {
            "--source-commit" if source.is_none() => source = Some(value),
            "--input-sha256" if input.is_none() => input = Some(value),
            "--checkpoint" if checkpoint.is_none() => checkpoint = Some(PathBuf::from(value)),
            "--resume" if resume.is_none() => resume = Some(PathBuf::from(value)),
            _ => return Err(format!("unknown or repeated argument {flag}")),
        }
    }
    let source_commit = source.ok_or("--source-commit is required")?;
    let input_sha256 = input.ok_or("--input-sha256 is required")?;
    for (name, value, n) in [("source", &source_commit, 40), ("input", &input_sha256, 64)] {
        if value.len() != n
            || !value
                .bytes()
                .all(|b| b.is_ascii_hexdigit() && !b.is_ascii_uppercase())
        {
            return Err(format!(
                "{name} identity must be {n} lowercase hexadecimal characters"
            ));
        }
    }
    Ok(Args {
        source_commit,
        input_sha256,
        checkpoint_path: checkpoint,
        resume_path: resume,
    })
}
fn fatal(stage: &str, message: &str, context: serde_json::Value) -> ExitCode {
    let value = json!({"schema":"BASS_S12_PROCESS_FAILURE_V1","status":"failed",
        "stage":stage,"error":message,"context":context,"history_executed":false});
    let mut stdout = io::stdout().lock();
    let _ = serde_json::to_writer(&mut stdout, &value);
    let _ = writeln!(stdout);
    eprintln!(
        "{}",
        json!({"schema":"BASS_S12_PROCESS_STATUS_V1","status":"failed",
        "stage":stage,"error":message})
    );
    ExitCode::from(2)
}

fn main() -> ExitCode {
    let args = match parse_args() {
        Ok(a) => a,
        Err(e) => return fatal("arguments", &e, json!({})),
    };
    let mut bytes = Vec::new();
    if let Err(e) = io::stdin()
        .take(MAX_INPUT_BYTES + 1)
        .read_to_end(&mut bytes)
    {
        return fatal("stdin", &e.to_string(), json!({}));
    }
    if bytes.len() as u64 > MAX_INPUT_BYTES {
        return fatal(
            "stdin",
            "input exceeds the fixed 64 MiB limit",
            json!({"bytes_read":bytes.len()}),
        );
    }
    let actual_input = sha256(&bytes);
    if actual_input != args.input_sha256 {
        return fatal(
            "input_hash",
            "exact stdin bytes differ from --input-sha256",
            json!({"expected":args.input_sha256,"actual":actual_input,"bytes":bytes.len()}),
        );
    }
    let input: Input = match serde_json::from_slice(&bytes) {
        Ok(v) => v,
        Err(e) => {
            return fatal(
                "input_json",
                &e.to_string(),
                json!({"input_sha256":actual_input}),
            );
        }
    };
    let executable = match std::env::current_exe() {
        Ok(p) => p,
        Err(e) => return fatal("binary_identity", &e.to_string(), json!({})),
    };
    let binary = match fs::metadata(&executable) {
        Ok(m) if m.is_file() && m.len() <= 256 * 1024 * 1024 => match fs::read(&executable) {
            Ok(b) => b,
            Err(e) => return fatal("binary_identity", &e.to_string(), json!({})),
        },
        Ok(_) => {
            return fatal(
                "binary_identity",
                "executable is not a bounded regular file",
                json!({}),
            );
        }
        Err(e) => return fatal("binary_identity", &e.to_string(), json!({})),
    };
    let binding = Binding {
        source_commit: args.source_commit,
        input_sha256: actual_input,
        binary_sha256: sha256(&binary),
    };
    let options = RunOptions {
        binding: binding.clone(),
        checkpoint_path: args.checkpoint_path,
        resume_path: args.resume_path,
    };
    let receipt = run(input, options);
    let completed = receipt.status == "completed";
    let mut out = io::BufWriter::new(io::stdout().lock());
    if let Err(e) = serde_json::to_writer(&mut out, &receipt)
        .map_err(io::Error::other)
        .and_then(|_| writeln!(out))
        .and_then(|_| out.flush())
    {
        eprintln!(
            "{}",
            json!({"schema":"BASS_S12_PROCESS_STATUS_V1",
            "status":"output_failure","error":e.to_string(),"binding":binding})
        );
        return ExitCode::from(4);
    }
    eprintln!(
        "{}",
        json!({"schema":"BASS_S12_PROCESS_STATUS_V1","status":receipt.status,
        "binding":binding,"segments":receipt.segments.len(),"admitted_births":receipt.events.len(),
        "observations":receipt.observations.len(),"resumed":receipt.resumed,
        "checkpoint_writes":receipt.checkpoint_writes,"elapsed_seconds":receipt.elapsed_seconds})
    );
    ExitCode::from(if completed { 0 } else { 3 })
}

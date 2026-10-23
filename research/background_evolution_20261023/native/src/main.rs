use std::io::{self,BufRead,Write};
use bass_background_fixed_scale::{Sources,rhs,constraints,packed_len};

fn parse_line(line: &str) -> Result<(usize,Vec<f64>,Sources,f64,[f64;3]),String> {
    let tokens: Vec<_>=line.split_whitespace().collect();
    let sectors=tokens.first().ok_or("empty input line")?.parse::<usize>()
        .map_err(|_|"first token must be a nonnegative integer sector count")?;
    let expected=sectors.checked_mul(14).and_then(|n|n.checked_add(21)).ok_or("sector count overflow")?;
    if tokens.len()!=expected { return Err(format!("expected {expected} tokens, received {}",tokens.len())); }
    let values: Result<Vec<f64>,_>=tokens[1..].iter().map(|x|x.parse::<f64>()).collect();
    let values=values.map_err(|_|"invalid floating-point token")?;
    let n=packed_len(sectors).map_err(|e|e.to_string())?;
    let state=values[..n].to_vec();let mut pos=n;
    let pressure=values[pos..pos+sectors].to_vec();pos+=sectors;
    let mut pi5=Vec::with_capacity(sectors);
    for _ in 0..sectors { pi5.push(values[pos..pos+5].try_into().unwrap());pos+=5; }
    let energy_transfer=values[pos..pos+sectors].to_vec();pos+=sectors;
    let mut momentum_transfer=Vec::with_capacity(sectors);
    for _ in 0..sectors { momentum_transfer.push(values[pos..pos+3].try_into().unwrap());pos+=3; }
    let lambda=values[pos];let rotation=values[pos+1..pos+4].try_into().unwrap();
    Ok((sectors,state,Sources {pressure,pi5,energy_transfer,momentum_transfer},lambda,rotation))
}

fn run() -> Result<(),String> {
    let stdin=io::stdin();let stdout=io::stdout();let mut output=io::BufWriter::new(stdout.lock());
    for (number,line) in stdin.lock().lines().enumerate() {
        let line=line.map_err(|e|format!("input read: {e}"))?;
        if line.trim().is_empty() { continue; }
        let context=|e: String|format!("line {}: {e}",number+1);
        let (sectors,state,sources,lambda,rotation)=parse_line(&line).map_err(context)?;
        let derivative=rhs(sectors,&state,&sources,lambda,rotation).map_err(|e|context(e.to_string()))?;
        let diagnostics=constraints(sectors,&state,lambda).map_err(|e|context(e.to_string()))?;
        for (i,value) in derivative.iter().chain(diagnostics.iter()).enumerate() {
            if i>0 { write!(output," ").map_err(|e|e.to_string())?; }
            write!(output,"{value:.17e}").map_err(|e|e.to_string())?;
        }
        writeln!(output).map_err(|e|e.to_string())?;
    }
    output.flush().map_err(|e|e.to_string())
}

fn main() {
    if let Err(e)=run() { eprintln!("{e}");std::process::exit(2); }
}

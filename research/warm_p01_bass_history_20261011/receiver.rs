#![allow(dead_code)]
mod microphysics {
    #[path = "/tmp/WARM_P01_BASS_HISTORY_EXEC28.YBvzfGDh/bass/_rustcore/src/microphysics/frame.rs"]
    pub mod frame;
    #[path = "/tmp/WARM_P01_BASS_HISTORY_EXEC28.YBvzfGDh/bass/_rustcore/src/microphysics/visibility.rs"]
    pub mod visibility;
}
use microphysics::visibility::{ElectronState, integrate_rest_frame_sampled_visibility};
use std::io::{self, Read};

fn parse_f64(s: &str, label: &str) -> Result<f64, String> {
    s.parse::<f64>().map_err(|e| format!("{label}: {e}"))
}
fn run() -> Result<(), String> {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).map_err(|e| e.to_string())?;
    let mut lines = input.lines();
    let head = lines.next().ok_or("missing tail header")?;
    let mut h = head.split('\t');
    if h.next() != Some("TAIL") { return Err("expected TAIL header".into()); }
    let tail = parse_f64(h.next().ok_or("missing tail")?, "tail")?;
    if h.next().is_some() { return Err("extra tail columns".into()); }
    let count_line = lines.next().ok_or("missing count header")?;
    let mut c = count_line.split('\t');
    if c.next() != Some("N") { return Err("expected N header".into()); }
    let n = c.next().ok_or("missing N")?.parse::<usize>().map_err(|e| e.to_string())?;
    if n != 17 || c.next().is_some() { return Err("fixed history requires exactly 17 epochs".into()); }
    let mut rows = Vec::with_capacity(n);
    let mut samples = Vec::with_capacity(n);
    let mut times = Vec::with_capacity(n);
    for i in 0..n {
        let line = lines.next().ok_or_else(|| format!("missing epoch {i}"))?;
        let cols = line.split('\t').collect::<Vec<_>>();
        if cols.len() != 6 { return Err(format!("epoch {i}: expected 6 fields")); }
        let t = parse_f64(cols[0], "time")?;
        let nh = parse_f64(cols[1], "nH")?;
        let nhe = parse_f64(cols[2], "nHe")?;
        let xhii = parse_f64(cols[3], "xHII")?;
        let xheii = parse_f64(cols[4], "xHeII")?;
        let xheiii = parse_f64(cols[5], "xHeIII")?;
        let sample = ElectronState::new(nh, nhe, xhii, xheii, xheiii)
            .map_err(|e| format!("epoch {i}: ElectronState {e:?}"))?;
        rows.push([t, nh, nhe, xhii, xheii, xheiii]);
        times.push(t);
        samples.push(sample);
    }
    if lines.next().is_some() { return Err("extra epochs".into()); }
    let result = integrate_rest_frame_sampled_visibility(&times, &samples, tail)
        .map_err(|e| format!("sampled visibility {e:?}"))?;
    for i in 0..n {
        let row = rows[i];
        println!("E\t{i}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
            row[0], row[1], row[2], row[3], row[4], row[5],
            samples[i].number_density_m3(), result.edge_rates_s_inverse[i],
            result.visibility.optical_depth[i], result.visibility.survival[i]);
    }
    for i in 0..n-1 {
        println!("C\t{i}\t{:.17e}\t{:.17e}",
            result.cell_average_rates_s_inverse[i], result.visibility.interval_probability[i]);
    }
    Ok(())
}
fn main() {
    if let Err(e) = run() {
        eprintln!("{e}");
        std::process::exit(2);
    }
}

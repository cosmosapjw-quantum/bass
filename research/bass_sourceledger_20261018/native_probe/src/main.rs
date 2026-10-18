//! Calls the actual pinned REI CovariantTransport::inject and inventory.
//! Source-only measurement, not absorption/chemistry/Einstein feedback.
//! Stocks: photons and eV per conserved total-H nucleus. No extra a^-3.
#![forbid(unsafe_code)]
use rei_microphysics::axbi_covariant_transport::{CovariantTransport, PhotonState};
use rei_microphysics::axbi_sources::{AxbiSource, SOURCE_ID};
use rei_microphysics::{AxisymmetricPoint, GeometrySnapshot};
use std::collections::HashSet;
use std::fs::{self, OpenOptions};
use std::io::{BufWriter, Write};
use std::path::Path;

const AREF: f64 = 1.0 / 21.0;
const OWNER: &str = env!("BASS_REI_SHA");
const PROBE: &str = env!("BASS_PROBE_SHA");
const SCHEMA: &str = "bass.sourceledger.native.v1";
type R<T> = Result<T, String>;
fn native<T>(value: Result<T, rei_microphysics::ForwardError>) -> R<T> {
    value.map_err(|e| format!("UPSTREAM:{e:?}"))
}
fn real(s: &str) -> R<f64> {
    let v = s.parse::<f64>().map_err(|_| "FLOAT_PARSE")?;
    if !v.is_finite() { return Err("NONFINITE_INPUT".into()); }
    Ok(v)
}
fn integer(s: &str, max: usize) -> R<usize> {
    let v = s.parse::<usize>().map_err(|_| "INTEGER_PARSE")?;
    if v == 0 || v > max { return Err("INTEGER_DOMAIN".into()); }
    Ok(v)
}
fn geometry(fields: &[&str]) -> R<(f64, GeometrySnapshot)> {
    if fields.len() != 4 { return Err("GEOMETRY_COLUMNS".into()); }
    let x = real(fields[0])?;
    let b = real(fields[1])?;
    let h = real(fields[2])?;
    let s = real(fields[3])?;
    if x < 0.0 || x > (21.0_f64 / 5.0).ln() || b.abs() > 0.4 || h <= 0.0 {
        return Err("GEOMETRY_DOMAIN".into());
    }
    let point = native(AxisymmetricPoint::new(AREF * x.exp(), b, h, s))?;
    Ok((x, native(point.snapshot())?))
}
fn array(v: &[f64]) -> R<String> {
    if v.iter().any(|x| !x.is_finite()) { return Err("NONFINITE_OUTPUT".into()); }
    Ok(format!("[{}]", v.iter().map(|x| format!("{x:.17e}")).collect::<Vec<_>>().join(",")))
}
struct Active {
    id: String,
    transport: CovariantTransport,
    state: PhotonState,
    previous: GeometrySnapshot,
    x: f64,
    nh0: f64,
    births: usize,
    ledger_n: f64,
    ledger_u: f64,
    work: f64,
}
impl Active {
    fn new(parts: &[&str]) -> R<Self> {
        // id, nh0, fesc, source panels, angular nodes, energy cells, qmin, qmax
        if parts.len() != 8 { return Err("CASE_COLUMNS".into()); }
        let id = parts[0];
        if id.is_empty() || id.len() > 100 || !id.bytes().all(|c| c.is_ascii_alphanumeric() || b"_-.:".contains(&c)) {
            return Err("CASE_ID".into());
        }
        let nh0 = real(parts[1])?;
        let fesc = real(parts[2])?;
        let nseg = integer(parts[3], 1024)?;
        let nmu = integer(parts[4], 32)?;
        if ![8, 16, 32].contains(&nmu) { return Err("N_MU".into()); }
        let ne = integer(parts[5], 1024)?;
        let qmin = real(parts[6])?;
        let qmax = real(parts[7])?;
        let source = native(AxbiSource::new(nh0, fesc, nseg, nmu))?;
        let reference = native(GeometrySnapshot::new([AREF; 3], [1.0e-16; 3]))?;
        let transport = native(CovariantTransport::new(&source, reference, ne, qmin, qmax))?;
        let state = transport.empty_state();
        Ok(Self { id: id.into(), transport, state, previous: reference, x: 0.0,
                  nh0, births: 0, ledger_n: 0.0, ledger_u: 0.0, work: 0.0 })
    }
    fn move_to(&mut self, parts: &[&str]) -> R<GeometrySnapshot> {
        let (x, g) = geometry(parts)?;
        if x < self.x { return Err("NONMONOTONE_TIME".into()); }
        let before = native(self.transport.inventory(&self.state, &self.previous))?.1;
        let after = native(self.transport.inventory(&self.state, &g))?.1;
        self.work += before - after;
        self.previous = g;
        self.x = x;
        Ok(g)
    }
    fn birth(&mut self, parts: &[&str]) -> R<()> {
        if parts.len() != 5 || self.births >= 4096 { return Err("BIRTH_COLUMNS_OR_CAP".into()); }
        let dt = real(parts[4])?;
        if dt < 0.0 { return Err("NEGATIVE_DT".into()); }
        let g = self.move_to(&parts[..4])?;
        let z = 1.0 / (AREF * self.x.exp()) - 1.0;
        let ledger = native(self.transport.inject(&mut self.state, &g, z, dt))?;
        self.ledger_n += ledger.added_photons_per_h;
        self.ledger_u += ledger.added_energy_ev_per_h;
        self.births += 1;
        native(self.transport.validate_state(&self.state))
    }
    fn finish(mut self, parts: &[&str]) -> R<String> {
        if self.births == 0 { return Err("NO_BIRTH_RECORDS".into()); }
        let g = self.move_to(parts)?;
        native(self.transport.validate_state(&self.state))?;
        let (n, u) = native(self.transport.inventory(&self.state, &g))?;
        let rays = native(self.transport.ray_geometry(&g))?;
        let ne = self.transport.n_energy();
        let mut delta = 0.0;
        let mut dipole = 0.0;
        let mut rn = Vec::with_capacity(rays.len());
        let mut ru = Vec::with_capacity(rays.len());
        for (i, ray) in rays.iter().enumerate() {
            let nn: f64 = self.state.number[i*ne..(i+1)*ne].iter().sum();
            let ur: f64 = self.state.energy_ref[i*ne..(i+1)*ne].iter().sum();
            delta += ur * ray.scale * (3.0 * ray.mu * ray.mu - 1.0) / 2.0;
            dipole += ur * ray.scale * ray.mu;
            rn.push(nn);
            ru.push(ur);
        }
        let min_number = self.state.number.iter().copied().fold(f64::INFINITY, f64::min);
        let pperp = (u - delta) / 3.0;
        let ppar = (u + 2.0 * delta) / 3.0;
        let nh = self.nh0 / (AREF * self.x.exp()).powi(3);
        let dn = n - self.ledger_n;
        let du = u + self.work - self.ledger_u;
        if [n, u, delta, dipole, self.ledger_n, self.ledger_u, self.work, dn, du, nh,
            min_number, pperp, ppar].iter().any(|v| !v.is_finite()) {
            return Err("NONFINITE_OUTPUT".into());
        }
        // Do not silently widen upstream physical acceptance. This check guards
        // the read-only probe's own accumulated inventory/ledger mapping.
        if dn.abs() > 1e-11 * self.ledger_n.abs().max(1e-30)
            || du.abs() > 1e-11 * self.ledger_u.abs().max(1e-30) {
            return Err("PROBE_LEDGER".into());
        }
        Ok(format!(concat!("{{\"schema\":\"{}\",\"id\":\"{}\",\"owner_sha\":\"{}\",",
            "\"probe_sha\":\"{}\",\"source_id\":\"{}\",\"births\":{},",
            "\"inventory_n\":{:.17e},\"inventory_u\":{:.17e},\"delta\":{:.17e},",
            "\"dipole\":{:.17e},\"ledger_n\":{:.17e},\"ledger_u\":{:.17e},",
            "\"work\":{:.17e},\"number_residual\":{:.17e},\"energy_residual\":{:.17e},",
            "\"proper_nh\":{:.17e},\"min_number\":{:.17e},\"pperp\":{:.17e},\"ppar\":{:.17e},",
            "\"ray_number\":{},\"ray_energy_ref\":{}}}"),
            SCHEMA, self.id, OWNER, PROBE, SOURCE_ID, self.births, n, u, delta, dipole,
            self.ledger_n, self.ledger_u, self.work, dn, du, nh, min_number, pperp, ppar,
            array(&rn)?, array(&ru)?))
    }
}
fn run(input: &Path, output: &Path) -> R<usize> {
    let meta = fs::metadata(input).map_err(|e| e.to_string())?;
    if meta.len() > 16 * 1024 * 1024 { return Err("INPUT_SIZE_CAP".into()); }
    let data = fs::read_to_string(input).map_err(|e| e.to_string())?;
    let mut lines = data.lines().filter(|l| !l.trim().is_empty());
    if lines.next() != Some("BASS_SOURCELEDGER_INPUT_V1") { return Err("INPUT_SCHEMA".into()); }
    let mut active: Option<Active> = None;
    let mut seen = HashSet::new();
    let mut reports = Vec::new();
    for line in lines {
        if line.trim().starts_with('#') { continue; }
        let p: Vec<&str> = line.split_whitespace().collect();
        match p[0] {
            "CASE" => {
                if active.is_some() || seen.len() >= 512 { return Err("CASE_NEST_OR_CAP".into()); }
                let c = Active::new(&p[1..])?;
                if !seen.insert(c.id.clone()) { return Err("DUPLICATE_CASE".into()); }
                active = Some(c);
            }
            "BIRTH" => active.as_mut().ok_or("BIRTH_WITHOUT_CASE")?.birth(&p[1..])?,
            "END" => reports.push(active.take().ok_or("END_WITHOUT_CASE")?.finish(&p[1..])?),
            _ => return Err("UNKNOWN_RECORD".into()),
        }
    }
    if active.is_some() || reports.is_empty() { return Err("INCOMPLETE_OR_EMPTY_CASES".into()); }
    // All cases evaluated before opening output; an invalid trailing input
    // cannot turn a partial native data file into apparently complete evidence.
    let f = OpenOptions::new().write(true).create_new(true).open(output).map_err(|e| e.to_string())?;
    let mut writer = BufWriter::new(f);
    for report in &reports { writeln!(writer, "{report}").map_err(|e| e.to_string())?; }
    writeln!(writer, "{{\"schema\":\"bass.sourceledger.complete.v1\",\"count\":{},\"owner_sha\":\"{}\",\"probe_sha\":\"{}\"}}",
             reports.len(), OWNER, PROBE).map_err(|e| e.to_string())?;
    writer.flush().map_err(|e| e.to_string())?;
    Ok(reports.len())
}
fn main() {
    let args: Vec<String> = std::env::args().collect();
    let result = if args.len() == 3 { run(Path::new(&args[1]), Path::new(&args[2])) }
                 else { Err("USAGE: bass_sourceledger_probe INPUT.tsv OUTPUT.jsonl".into()) };
    match result {
        Ok(count) => println!("NATIVE_SOURCELEDGER_COMPLETE rows={count}"),
        Err(e) => { eprintln!("SOURCELEDGER_PROBE_FAIL:{e}"); std::process::exit(3); }
    }
}

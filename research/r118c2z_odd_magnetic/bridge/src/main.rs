use bianchi_rustcore::kinetic::{
    cooling_rays::CoolingRays,
    owned_thomson::{ExternalContribution, ExternalMatter, ThomsonOwner, ThomsonState},
    owned_vlasov::OwnedState,
};
use rei_microphysics::{
    axbi_covariant_driver::{compiled_identity, Driver, DriverConfig, DriverState},
    external_controller::{accepted_step, rejected_step},
    general_history::{GeneralHistory, HistoryPoint},
};
use std::{
    fs,
    io::{BufWriter, Write},
    path::Path,
    time::Instant,
};
const H0: f64 = 2.1842852410855023e-18;
const EV: f64 = 1.602176634e-19;
const RHO0: f64 =
    3. * 299792458. * 299792458. * H0 * H0 / (8. * std::f64::consts::PI * 6.67430e-11);
#[derive(Clone)]
struct State {
    gas: DriverState,
    escape: f64,
    cmb: f64,
    secondary_work: f64,
    cooling: Vec<f64>,
}
struct Coupler {
    d: Driver,
    initial: f64,
    feedback: bool,
    rhs: usize,
    stage_calls: usize,
    cooling: CoolingRays,
    anisotropic_cooling: bool,
    reports: Vec<(f64, [f64; 14])>,
    nmu: usize,
}
fn p(g: &OwnedState) -> HistoryPoint {
    HistoryPoint {
        a: g.a,
        h: g.h,
        f: std::array::from_fn(|i| std::array::from_fn(|j| g.f[(i, j)])),
    }
}
fn map<T>(r: Result<T, rei_microphysics::ForwardError>) -> Result<T, String> {
    r.map_err(|e| format!("{e:?}"))
}
impl Coupler {
    fn ledger(&self, s: &State) -> Result<f64, String> {
        let u = map(self.d.general_moments(&s.gas))?.energy;
        let [w, b] = map(self.d.gas_energy_components(&s.gas))?;
        let l = &s.gas.ledgers;
        Ok(u + w + b - self.initial - l.source_u
            + s.escape
            + s.cmb
            + l.thermal_work
            + l.photon_work
            + s.secondary_work)
    }
}
impl ExternalMatter for Coupler {
    type State = State;
    fn contribution(&mut self, s: &State, g: &OwnedState) -> Result<ExternalContribution, String> {
        if s.gas.a != g.a {
            return Err("clock mismatch".into());
        }
        let nh = self.d.n_h0_cm3 / g.a.powi(3);
        let nhe = self.d.n_he0_cm3 / g.a.powi(3);
        let eos = map(s.gas.gas.eos(nh, nhe))?;
        let ne = eos.electron_density_cm3 * 1e6;
        if !self.feedback {
            return Ok(ExternalContribution {
                rho: 0.,
                pressure: [[0.; 3]; 3],
                photon_rho: 0.,
                ne_m3: ne,
            });
        }
        let m = map(self.d.general_moments(&s.gas))?;
        let [w, b] = map(self.d.gas_energy_components(&s.gas))?;
        let sec = s.escape + s.cmb;
        let cool = self.cooling.moments(&s.cooling, g)?.1;
        let factor = self.d.n_h0_cm3 * 1e6 * EV / RHO0 / g.a.powi(3);
        let rho = factor * (m.energy + w + b - self.initial - s.gas.ledgers.source_u + sec);
        let pressure = std::array::from_fn(|i| {
            std::array::from_fn(|j| {
                factor
                    * (m.pressure[i][j]
                        + if self.anisotropic_cooling {
                            cool[(i, j)]
                        } else if i == j {
                            s.escape / 3.
                        } else {
                            0.
                        }
                        + if i == j { (2. * w + s.cmb) / 3. } else { 0. })
            })
        });
        Ok(ExternalContribution {
            rho,
            pressure,
            photon_rho: factor * (m.energy + sec),
            ne_m3: ne,
        })
    }
    fn advance(
        &mut self,
        s: &State,
        old: &OwnedState,
        mid: &OwnedState,
        end: &OwnedState,
    ) -> Result<State, String> {
        self.stage_calls += 1;
        if self.stage_calls > 20000 {
            return Err("bridge stage cap".into());
        }
        map(self.d.set_general_interval(vec![p(old), p(mid), p(end)]))?;
        let (x, report) = map(self.d.external_trial_report(&s.gas, end.a, &mut self.rhs))?;
        self.reports.push((end.a, report.ordered_values()));
        let a = old.a / end.a;
        let r = mid.a / end.a;
        let de = x.ledgers.escaped_u - s.gas.ledgers.escaped_u;
        let dc = -(x.ledgers.cmb_input - s.gas.ledgers.cmb_input);
        let (cooling, cw) = if self.anisotropic_cooling {
            self.cooling.advance(&s.cooling, old, mid, end, de)?
        } else {
            (s.cooling.clone(), (1. - a) * s.escape + (1. - r) * de)
        };
        let escape = if self.anisotropic_cooling {
            self.cooling.moments(&cooling, end)?.0
        } else {
            a * s.escape + r * de
        };
        let cmb = a * s.cmb + r * dc;
        let work = s.secondary_work + cw + (1. - a) * s.cmb + (1. - r) * dc;
        let next = State {
            gas: x,
            escape,
            cmb,
            secondary_work: work,
            cooling,
        };
        let residual = self.ledger(&next)?;
        let owner = map(self.d.residuals(&next.gas))?.1;
        if (residual - owner).abs() > 1e-12 || residual.abs() > 1e-8 {
            return Err("bridge energy ledger".into());
        }
        Ok(next)
    }
}
fn sha(p: &Path) -> Result<String, String> {
    let out = std::process::Command::new("sha256sum")
        .arg(p)
        .output()
        .map_err(|e| e.to_string())?;
    if !out.status.success() {
        return Err("SHA256 failure".into());
    }
    let s = String::from_utf8(out.stdout).map_err(|e| e.to_string())?;
    let h = s.split_whitespace().next().ok_or("SHA256 output")?;
    if h.len() != 64 || !h.bytes().all(|b| b.is_ascii_hexdigit()) {
        return Err("SHA256 output".into());
    }
    Ok(h.to_owned())
}
fn ident(step: f64, feedback: bool, aniso: bool, nmu: usize) -> Result<String, String> {
    Ok(format!(
        "C2Z_JOINT_V2\n{}\n{:016x} {} {} {nmu}\n",
        sha(&std::env::current_exe().map_err(|e| e.to_string())?)?,
        step.to_bits(),
        feedback,
        aniso
    ))
}
const FILES: [&str; 5] = [
    "rei.txt",
    "bass.txt",
    "bridge.txt",
    "config.cfg",
    "cooling.txt",
];
fn manifest(
    dir: &Path,
    step: f64,
    feedback: bool,
    aniso: bool,
    nmu: usize,
) -> Result<String, String> {
    let mut out = ident(step, feedback, aniso, nmu)?;
    for f in FILES {
        out += &format!("{} {f}\n", sha(&dir.join(f))?)
    }
    Ok(out)
}
fn save_joint(
    out: &Path,
    owner: &ThomsonOwner,
    s: &ThomsonState,
    x: &State,
    cp: &Coupler,
    h: f64,
    rejected: usize,
    step: f64,
    config: &[u8],
) -> Result<(), Box<dyn std::error::Error>> {
    let dir = out.join("checkpoint");
    let tmp = out.join("checkpoint.pending");
    if dir.exists() {
        return Err("checkpoint destination exists".into());
    }
    fs::create_dir(&tmp)?;
    cp.d.save_checkpoint(&tmp.join("rei.txt"), &x.gas)?;
    fs::write(tmp.join("bass.txt"), owner.state_text(s)?)?;
    fs::write(
        tmp.join("bridge.txt"),
        format!(
            "{} {} {}\n{}\n",
            cp.rhs,
            cp.stage_calls,
            rejected,
            [h, x.escape, x.cmb, x.secondary_work, cp.initial]
                .iter()
                .map(|v| format!("{:016x}", v.to_bits()))
                .collect::<Vec<_>>()
                .join(" ")
        ),
    )?;
    fs::write(tmp.join("config.cfg"), config)?;
    fs::write(
        tmp.join("cooling.txt"),
        x.cooling
            .iter()
            .map(|v| format!("{:016x}", v.to_bits()))
            .collect::<Vec<_>>()
            .join(" "),
    )?;
    fs::write(
        tmp.join("MANIFEST"),
        manifest(&tmp, step, cp.feedback, cp.anisotropic_cooling, cp.nmu)?,
    )?;
    fs::rename(tmp, dir)?;
    Ok(())
}
fn restore_joint(
    dir: &Path,
    owner: &ThomsonOwner,
    cp: &mut Coupler,
    step: f64,
    config: &[u8],
) -> Result<(ThomsonState, State, f64, usize), Box<dyn std::error::Error>> {
    if fs::read_to_string(dir.join("MANIFEST"))?
        != manifest(dir, step, cp.feedback, cp.anisotropic_cooling, cp.nmu)?
        || fs::read(dir.join("config.cfg"))? != config
    {
        return Err("joint checkpoint identity mismatch".into());
    }
    let s = owner.restore_state_text(&fs::read_to_string(dir.join("bass.txt"))?)?;
    let text = fs::read_to_string(dir.join("bridge.txt"))?;
    let l = text.lines().collect::<Vec<_>>();
    if l.len() != 2 {
        return Err("bridge checkpoint shape".into());
    }
    let n = l[0]
        .split_whitespace()
        .map(str::parse::<usize>)
        .collect::<Result<Vec<_>, _>>()?;
    let v = l[1]
        .split_whitespace()
        .map(|x| u64::from_str_radix(x, 16).map(f64::from_bits))
        .collect::<Result<Vec<_>, _>>()?;
    if n.len() != 3
        || v.len() != 5
        || !v.iter().all(|x| x.is_finite())
        || v[0] <= 0.
        || v[0] > step
        || v[4] != cp.initial
    {
        return Err("bridge checkpoint domain".into());
    }
    let gas = cp.d.restore_general_checkpoint(&dir.join("rei.txt"))?;
    let g = cp.d.transport.general_history().unwrap().point(gas.a)?;
    let q = p(&s.geometry);
    if gas.a != q.a
        || g.h != q.h
        || g.f != q.f
        || gas.rhs_evaluations != n[0]
        || n[1] < 2 * gas.accepted
    {
        return Err("joint state mismatch".into());
    }
    cp.rhs = n[0];
    cp.stage_calls = n[1];
    let cooling = fs::read_to_string(dir.join("cooling.txt"))?
        .split_whitespace()
        .map(|v| u64::from_str_radix(v, 16).map(f64::from_bits))
        .collect::<Result<Vec<_>, _>>()?;
    let cu = cp.cooling.moments(&cooling, &s.geometry)?.0;
    if cp.anisotropic_cooling && cu != v[1] || !cp.anisotropic_cooling && cu != 0. {
        return Err("cooling checkpoint mismatch".into());
    }
    let x = State {
        cooling,
        gas,
        escape: v[1],
        cmb: v[2],
        secondary_work: v[3],
    };
    if cp.ledger(&x)?.abs() > 1e-8 || owner.constraint_external(&s, &x, cp)?.abs() > 1e-5 {
        return Err("joint checkpoint ledger".into());
    }
    Ok((s, x, v[0], n[2]))
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = std::env::args().skip(1).collect::<Vec<_>>();
    let out = Path::new(&args[1]);
    fs::create_dir(out)?;
    let config_bytes = fs::read(&args[0])?;
    let config = DriverConfig::read(std::str::from_utf8(&config_bytes)?)?;
    let feedback = args[2] == "on";
    let step: f64 = args[3].parse()?;
    let cap: f64 = args[4].parse()?;
    let stop: usize = args[5].parse()?;
    let resume = &args[6];
    let anisotropic_cooling = match args[7].as_str() {
        "rays" => true,
        "iso" => false,
        _ => return Err("cooling mode".into()),
    };
    let local_target = config.local_target;
    let owner = ThomsonOwner::new(0.03, 32, 8, 16, 4, 8, 16)?;
    let mut s = owner.initial(1. / 21., [0.01, 0., 0., 0., 0.0075])?;
    let aend = 1. / (1. + config.end_zbar);
    let mut dummy = p(&s.geometry);
    dummy.a = aend;
    let nmu: usize = args[8].parse()?;
    if ![4, 8].contains(&nmu) {
        return Err("general nmu must be 4 or 8".into());
    }
    let h = GeneralHistory::new(vec![p(&s.geometry), dummy], nmu, 2 * nmu)?;
    let (d, g) = Driver::new_general(config, h)?;
    let initial = d.gas_energy_components(&g)?.iter().sum();
    let cooling = CoolingRays::new(1. / 21., 8, 16)?;
    let mut x = State {
        cooling: cooling.empty(),
        gas: g,
        escape: 0.,
        cmb: 0.,
        secondary_work: 0.,
    };
    let mut cp = Coupler {
        d,
        initial,
        feedback,
        rhs: 0,
        stage_calls: 0,
        cooling,
        anisotropic_cooling,
        reports: Vec::new(),
        nmu,
    };
    fs::write(out.join("rei_source_identity.txt"), compiled_identity())?;
    fs::write(out.join("config.cfg"), fs::read(&args[0])?)?;
    let mut w = BufWriter::new(fs::File::create(out.join("history.csv"))?);
    writeln!(w,"a,z,h,S0,S1,S2,S3,S4,F00,F01,F02,F10,F11,F12,F20,F21,F22,ne,T,xHII,xHeII,xHeIII,J0,Pxx,Pyy,Pzz,Pxy,Pxz,Pyz,thermal,binding,escape,cmb,source,work,ledger,gauss,local_error,cool_pi_norm,cool_Pyz,accepted,rhs,stage_calls,rejected")?;
    let mut errors = BufWriter::new(fs::File::create(out.join("error_components.csv"))?);
    writeln!(errors,"accepted,stage,a,gas0,gas1,gas2,gas3,shape_n,shape_u,pool_n,pool_u,gamma0,gamma1,gamma2,heat0,heat1,heat2")?;
    let begin = Instant::now();
    let mut rejected = 0;
    let mut h = step;
    if resume != "FRESH" {
        (s, x, h, rejected) =
            restore_joint(Path::new(resume), &owner, &mut cp, step, &config_bytes)?;
    }
    let mut status = "COMPLETE";
    loop {
        let g = &s.geometry;
        let m = cp.d.general_moments(&x.gas)?;
        let l = &x.gas.ledgers;
        let eos = x
            .gas
            .gas
            .eos(cp.d.n_h0_cm3 / g.a.powi(3), cp.d.n_he0_cm3 / g.a.powi(3))?;
        let e = cp.d.gas_energy_components(&x.gas)?;
        let f = x.gas.gas.fractions;
        write!(w, "{:.17e},{:.17e},{:.17e}", g.a, 1. / g.a - 1., g.h)?;
        for v in g.s {
            write!(w, ",{v:.17e}")?
        }
        for i in 0..3 {
            for j in 0..3 {
                write!(w, ",{:.17e}", g.f[(i, j)])?
            }
        }
        let work = l.thermal_work + l.photon_work + x.secondary_work;
        let ledger = cp.ledger(&x)?;
        let gauss = owner.constraint_external(&s, &x, &mut cp)?;
        let (cu, mut pr) = cp.cooling.moments(&x.cooling, g)?;
        for i in 0..3 {
            pr[(i, i)] -= cu / 3.;
        }
        let cpi = pr.norm();
        for v in [
            eos.electron_density_cm3,
            eos.temperature_k,
            f[0],
            f[1],
            f[2],
            m.energy,
            m.pressure[0][0],
            m.pressure[1][1],
            m.pressure[2][2],
            m.pressure[0][1],
            m.pressure[0][2],
            m.pressure[1][2],
            e[0],
            e[1],
            x.escape,
            x.cmb,
            l.source_u,
            work,
            ledger,
            gauss,
            x.gas.last_error,
            cpi,
            pr[(1, 2)],
        ] {
            write!(w, ",{v:.17e}")?
        }
        writeln!(
            w,
            ",{},{},{},{}",
            x.gas.accepted, cp.rhs, cp.stage_calls, rejected
        )?;
        if (aend / g.a).ln() < 1e-12 {
            break;
        }
        if x.gas.accepted >= stop {
            status = "CHECKPOINT_COUNT";
            break;
        }
        if begin.elapsed().as_secs_f64() > cap {
            status = "WALL_CAP";
            break;
        }
        let mut du = h.min((aend / g.a).ln());
        // Avoid a rounded overshoot of the exact configured endpoint.
        if g.a * du.exp() > aend {
            du = f64::from_bits(du.to_bits() - 1);
        }
        loop {
            cp.reports.clear();
            match owner.step_external(&s, &x, &mut cp, du) {
                Ok((ss, xx, _)) => {
                    s = ss;
                    x = xx;
                    h = map(accepted_step(du, x.gas.last_error, local_target, step))?;
                    if cp.reports.len() != 2 {
                        return Err("accepted stage report count".into());
                    }
                    for (j, (a, v)) in cp.reports.iter().enumerate() {
                        write!(errors, "{},{j},{a:.17e}", x.gas.accepted)?;
                        for z in v {
                            write!(errors, ",{z:.17e}")?;
                        }
                        writeln!(errors)?;
                    }
                    break;
                }
                Err(e) => {
                    rejected += 1;
                    du = map(rejected_step(du))?;
                    eprintln!("reject {rejected} at a={} h={du:e}: {e}", s.geometry.a);
                    if du < 1e-10 || rejected > 200 {
                        return Err(e.into());
                    }
                }
            }
        }
    }
    w.flush()?;
    errors.flush()?;
    save_joint(out, &owner, &s, &x, &cp, h, rejected, step, &config_bytes)?;
    fs::write(out.join("RETURN.txt"),format!("status={status}\na={:.17e}\naccepted={}\nrejected={rejected}\nrhs={}\nstages={}\nwall_s={:.6}\n",s.geometry.a,x.gas.accepted,cp.rhs,cp.stage_calls,begin.elapsed().as_secs_f64()))?;
    println!(
        "{status} z={} accepted={} rejects={rejected}",
        1. / s.geometry.a - 1.,
        x.gas.accepted
    );
    Ok(())
}

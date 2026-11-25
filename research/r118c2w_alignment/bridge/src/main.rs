use bianchi_rustcore::kinetic::{
    owned_thomson::{ExternalContribution, ExternalMatter, ThomsonOwner},
    owned_vlasov::OwnedState,
};
use rei_microphysics::{
    axbi_covariant_driver::{compiled_identity, Driver, DriverConfig, DriverState},
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
}
struct Coupler {
    d: Driver,
    initial: f64,
    feedback: bool,
    rhs: usize,
    stage_calls: usize,
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
        let factor = self.d.n_h0_cm3 * 1e6 * EV / RHO0 / g.a.powi(3);
        let rho = factor * (m.energy + w + b - self.initial - s.gas.ledgers.source_u + sec);
        let pressure = std::array::from_fn(|i| {
            std::array::from_fn(|j| {
                factor * (m.pressure[i][j] + if i == j { (2. * w + sec) / 3. } else { 0. })
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
        let x = map(self.d.external_trial(&s.gas, end.a, &mut self.rhs))?;
        let a = old.a / end.a;
        let r = mid.a / end.a;
        let de = x.ledgers.escaped_u - s.gas.ledgers.escaped_u;
        let dc = -(x.ledgers.cmb_input - s.gas.ledgers.cmb_input);
        let escape = a * s.escape + r * de;
        let cmb = a * s.cmb + r * dc;
        let work = s.secondary_work + (1. - a) * (s.escape + s.cmb) + (1. - r) * (de + dc);
        let next = State {
            gas: x,
            escape,
            cmb,
            secondary_work: work,
        };
        let residual = self.ledger(&next)?;
        let owner = map(self.d.residuals(&next.gas))?.1;
        if (residual - owner).abs() > 1e-12 || residual.abs() > 1e-8 {
            return Err("bridge energy ledger".into());
        }
        Ok(next)
    }
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = std::env::args().skip(1).collect::<Vec<_>>();
    let out = Path::new(&args[1]);
    fs::create_dir(out)?;
    let config = DriverConfig::read(&fs::read_to_string(&args[0])?)?;
    let feedback = args[2] == "on";
    let step: f64 = args[3].parse()?;
    let cap: f64 = args[4].parse()?;
    let owner = ThomsonOwner::new(0.03, 32, 8, 16, 4, 8, 16)?;
    let mut s = owner.initial(1. / 21., [0.01, 0., 0., 0., 0.0075])?;
    let aend = 1. / (1. + config.end_zbar);
    let mut dummy = p(&s.geometry);
    dummy.a = aend;
    let h = GeneralHistory::new(vec![p(&s.geometry), dummy], 4, 8)?;
    let (d, g) = Driver::new_general(config, h)?;
    let initial = d.gas_energy_components(&g)?.iter().sum();
    let mut x = State {
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
    };
    fs::write(out.join("rei_source_identity.txt"), compiled_identity())?;
    fs::write(out.join("config.cfg"), fs::read(&args[0])?)?;
    let mut w = BufWriter::new(fs::File::create(out.join("history.csv"))?);
    writeln!(w,"a,z,h,S0,S1,S2,S3,S4,F00,F01,F02,F10,F11,F12,F20,F21,F22,ne,T,xHII,xHeII,xHeIII,J0,Pxx,Pyy,Pzz,Pxy,Pxz,Pyz,thermal,binding,escape,cmb,source,work,ledger,gauss,local_error,accepted,rhs,stage_calls,rejected")?;
    let begin = Instant::now();
    let mut rejected = 0;
    let mut h = step;
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
            match owner.step_external(&s, &x, &mut cp, du) {
                Ok((ss, xx, _)) => {
                    s = ss;
                    x = xx;
                    h = (du * 1.5).min(step);
                    break;
                }
                Err(e) => {
                    rejected += 1;
                    du *= 0.5;
                    h = du;
                    eprintln!("reject {rejected} at a={} h={du:e}: {e}", s.geometry.a);
                    if du < 1e-10 || rejected > 200 {
                        return Err(e.into());
                    }
                }
            }
        }
    }
    w.flush()?;
    fs::write(out.join("RETURN.txt"),format!("status={status}\na={:.17e}\naccepted={}\nrejected={rejected}\nrhs={}\nstages={}\nwall_s={:.6}\n",s.geometry.a,x.gas.accepted,cp.rhs,cp.stage_calls,begin.elapsed().as_secs_f64()))?;
    println!(
        "{status} z={} accepted={} rejects={rejected}",
        1. / s.geometry.a - 1.,
        x.gas.accepted
    );
    Ok(())
}

//! R118-C2D: realizable number/energy cell transport. Each cell owns
//! two endpoint masses. For advection only, reconstruct a continuous
//! nonnegative exponential *number density in linear frequency* with
//! exactly those moments. This is a closure, not an exact spectral shape.
//! Use centered detuning moments to resolve small recoil energies.
#[derive(Clone, Copy, Debug, Default)]
pub struct Cell {
    pub left: f64,
    pub right: f64,
}
impl Cell {
    pub fn number(self) -> f64 {
        self.left + self.right
    }
    pub fn moment(self, l: f64, r: f64) -> f64 {
        l * self.left + r * self.right
    }
    fn valid(self) -> bool {
        self.left.is_finite()
            && self.right.is_finite()
            && self.left >= 0.
            && self.right >= 0.
            && self.number().is_finite()
    }
}
#[derive(Clone, Copy, Debug)]
pub struct Reconstruction {
    mass: f64,
    mean: f64,
    k: f64,
    flip: bool,
    atom: Option<f64>,
}
fn small_mean(k: f64) -> f64 {
    if k < 1e-3 {
        let k2 = k * k;
        0.5 - k / 12. + k * k2 / 720. - k * k2 * k2 / 30240.
    } else {
        1. / k - 1. / k.exp_m1()
    }
}
impl Reconstruction {
    pub fn new(cell: Cell) -> Result<Self, String> {
        if !cell.valid() {
            return Err("invalid dual cell".into());
        }
        let mass = cell.number();
        if mass == 0. {
            return Ok(Self {
                mass,
                mean: 0.,
                k: 0.,
                flip: false,
                atom: Some(0.),
            });
        }
        let mean = cell.right / mass;
        if cell.left == 0. || cell.right == 0. {
            return Ok(Self {
                mass,
                mean,
                k: 0.,
                flip: false,
                atom: Some(if cell.left == 0. { 1. } else { 0. }),
            });
        }
        let flip = cell.right > cell.left;
        let target = cell.left.min(cell.right) / mass;
        if target == 0. {
            return Err("dual cell mean underflow".into());
        }
        // mean(k) strictly decreases 1/2 -> 0. The upper bracket
        // 1/target is conservative. Near an endpoint exp(-k) vanishes.
        let mut lo = 0.;
        let mut hi = 1. / target;
        if !hi.is_finite() {
            return Err("unresolved extreme dual mean".into());
        }
        for _ in 0..72 {
            let mid = (lo + hi) * 0.5;
            if small_mean(mid) > target {
                lo = mid
            } else {
                hi = mid
            }
            if hi - lo <= 4. * f64::EPSILON * hi.max(1.) {
                break;
            }
        }
        Ok(Self {
            mass,
            mean,
            k: (lo + hi) * 0.5,
            flip,
            atom: None,
        })
    }
    // Return interval mass and first local moment in original t in [0,1].
    // Disjoint interior intervals use [lo,hi); endpoint t=1 is owned by
    // the last interval. Delta endpoints are handled separately in remap.
    pub fn portion(&self, lo: f64, hi: f64) -> Result<(f64, f64), String> {
        if !lo.is_finite() || !hi.is_finite() || lo < 0. || hi > 1. || hi < lo {
            return Err("invalid reconstruction interval".into());
        }
        if self.mass == 0. || hi == lo {
            return Ok((0., 0.));
        }
        if lo == 0. && hi == 1. {
            return Ok((self.mass, self.mass * self.mean));
        }
        if let Some(t) = self.atom {
            return Ok(if lo <= t && (t < hi || hi == 1. && t == 1.) {
                (self.mass, self.mass * t)
            } else {
                (0., 0.)
            });
        }
        let (l, r) = if self.flip {
            (1. - hi, 1. - lo)
        } else {
            (lo, hi)
        };
        let h = r - l;
        let n = if self.k < 1e-14 {
            self.mass * h
        } else {
            self.mass * (-self.k * l).exp() * (-(-self.k * h).exp_m1()) / (-(-self.k).exp_m1())
        };
        let mean = l + h * small_mean(self.k * h);
        let t = if self.flip { 1. - mean } else { mean };
        if !n.is_finite() || n < 0. || !t.is_finite() {
            return Err("nonfinite exponential overlap".into());
        }
        Ok((n, n * t))
    }
}
#[derive(Clone, Debug)]
pub struct DualTransport {
    pub edges: Vec<f64>,
    pub nu0: f64,
    pub dnu: f64,
    red: usize,
    blue: usize,
}
#[derive(Clone, Debug)]
pub struct Drift {
    pub cells: Vec<Cell>,
    pub escaped_mass: f64,
    pub escaped_x: f64,
    pub work_x: f64,
    pub core_work_x: f64,
    pub face_x: f64,
    pub core_centered_defect: f64,
    pub exterior_centered_defect: f64,
    pub number_defect: f64,
    pub centered_defect: f64,
    pub core_number_defect: f64,
    pub exterior_number_defect: f64,
    pub projection_core_x: f64,
    pub projection_exterior_x: f64,
    pub red_in: f64,
    pub red_out: f64,
    pub blue_in: f64,
    pub blue_out: f64,
    pub atom_energy: f64,
}
fn sum(values: impl Iterator<Item = f64>) -> f64 {
    let (mut s, mut c) = (0., 0.);
    for v in values {
        let y = v - c;
        let t = s + y;
        c = (t - s) - y;
        s = t;
    }
    s
}
impl DualTransport {
    pub fn new(edges: Vec<f64>, nu0: f64, dnu: f64, red: f64, blue: f64) -> Result<Self, String> {
        if edges.len() < 4
            || edges.len() > 8193
            || !nu0.is_finite()
            || nu0 <= 0.
            || !dnu.is_finite()
            || dnu <= 0.
            || edges.iter().any(|x| !x.is_finite() || nu0 + dnu * x <= 0.)
            || edges.windows(2).any(|p| p[0] >= p[1])
        {
            return Err("invalid dual transport mesh".into());
        }
        let red = edges
            .iter()
            .position(|x| *x == red)
            .ok_or("missing red face")?;
        let blue = edges
            .iter()
            .position(|x| *x == blue)
            .ok_or("missing blue face")?;
        if red == 0 || blue >= edges.len() - 1 || red >= blue {
            return Err("invalid domain faces".into());
        }
        Ok(Self {
            edges,
            nu0,
            dnu,
            red,
            blue,
        })
    }
    pub fn number(&self, m: &[Cell]) -> f64 {
        sum(m.iter().map(|v| v.number()))
    }
    pub fn detuning(&self, m: &[Cell]) -> f64 {
        sum(self
            .edges
            .windows(2)
            .zip(m)
            .map(|(p, c)| c.moment(p[0], p[1])))
    }
    pub fn shift(&self, m: &[Cell], dz: f64) -> Result<Drift, String> {
        if m.len() + 1 != self.edges.len()
            || m.iter().any(|x| !x.valid())
            || !dz.is_finite()
            || dz.abs() > 0.1
        {
            return Err("invalid dual frequency shift".into());
        }
        let n0 = self.number(m);
        let x0 = self.detuning(m);
        let f = dz.exp_m1();
        let inv = (-dz).exp_m1();
        let ratio = self.nu0 / self.dnu;
        let xmap = |x: f64| x + f * (ratio + x);
        let pre: Vec<_> = self.edges.iter().map(|x| x + inv * (ratio + x)).collect();
        let mut y = vec![Cell::default(); m.len()];
        let mut raw_x = vec![0.; m.len()];
        let (mut esc, mut xe) = (0., 0.);
        let (mut ri, mut ro, mut bi, mut bo) = (0., 0., 0., 0.);
        let mut core_work = 0.;
        let lo = self.edges[self.red];
        let hi = self.edges[self.blue];
        if dz == 0. {
            return Ok(Drift {
                cells: m.to_vec(),
                escaped_mass: 0.,
                escaped_x: 0.,
                work_x: 0.,
                core_work_x: 0.,
                face_x: 0.,
                core_centered_defect: 0.,
                exterior_centered_defect: 0.,
                number_defect: 0.,
                centered_defect: 0.,
                core_number_defect: 0.,
                exterior_number_defect: 0.,
                projection_core_x: 0.,
                projection_exterior_x: 0.,
                red_in: 0.,
                red_out: 0.,
                blue_in: 0.,
                blue_out: 0.,
                atom_energy: 0.,
            });
        }
        for (i, c) in m.iter().enumerate() {
            let n = c.number();
            if n == 0. {
                continue;
            }
            let l = self.edges[i];
            let r = self.edges[i + 1];
            let w = r - l;
            let rec = Reconstruction::new(*c)?;
            // Endpoint atoms have a unique source cell even at a shared
            // face; zero step is identity. Count crossings by ownership.
            if let Some(t) = rec.atom {
                let old = l + w * t;
                let x = xmap(old);
                core_work += n * (x.clamp(lo, hi) - old.clamp(lo, hi));
                let j = if x < self.edges[0] || x > *self.edges.last().unwrap() {
                    None
                } else {
                    Some(
                        self.edges
                            .partition_point(|v| *v <= x)
                            .saturating_sub(1)
                            .min(m.len() - 1),
                    )
                };
                let was_red = i < self.red;
                let was_blue = i >= self.blue;
                let is_red = x < lo;
                let is_blue = x >= hi;
                if was_red && !is_red {
                    ri += n
                }
                if !was_red && is_red {
                    ro += n
                }
                if was_blue && !is_blue {
                    bi += n
                }
                if !was_blue && is_blue {
                    bo += n
                }
                if let Some(j) = j {
                    let b = (x - self.edges[j]) / (self.edges[j + 1] - self.edges[j]);
                    if !(0. ..=1.).contains(&b) {
                        return Err("atom outside destination".into());
                    }
                    y[j].left += n * (1. - b);
                    y[j].right += n * b;
                    raw_x[j] += n * x;
                } else {
                    esc += n;
                    xe += n * x
                }
                continue;
            }
            let portion = |a: f64, b: f64| -> Result<(f64, f64), String> {
                let u = ((a - l) / w).clamp(0., 1.);
                let v = ((b - l) / w).clamp(0., 1.);
                if v <= u {
                    return Ok((0., 0.));
                }
                let (n, t) = rec.portion(u, v)?;
                Ok((n, l * n + w * t))
            };
            // Independent integrated work while each characteristic is
            // inside COM: integral of clamp(x_new,L,R)-clamp(x_old,L,R).
            let (nl, _) = portion(f64::NEG_INFINITY, lo)?;
            let (nh, _) = portion(hi, f64::INFINITY)?;
            let (_, xc) = portion(lo, hi)?;
            let (nln, _) = portion(f64::NEG_INFINITY, pre[self.red])?;
            let (nhn, _) = portion(pre[self.blue], f64::INFINITY)?;
            let (nc, xcn) = portion(pre[self.red], pre[self.blue])?;
            core_work += lo * (nln - nl) + hi * (nhn - nh) + (xcn - xc) + f * (ratio * nc + xcn);
            let (q, x) = portion(f64::NEG_INFINITY, pre[0])?;
            esc += q;
            xe += x + f * (ratio * q + x);
            let (q, x) = portion(*pre.last().unwrap(), f64::INFINITY)?;
            esc += q;
            xe += x + f * (ratio * q + x);
            for j in 0..y.len() {
                let (q, x) = portion(pre[j], pre[j + 1])?;
                if q == 0. {
                    continue;
                }
                let xm = x + f * (ratio * q + x);
                let wj = self.edges[j + 1] - self.edges[j];
                let b = (xm / q - self.edges[j]) / wj;
                // Exact overlap mean belongs to the destination. Only
                // tolerate round-off in endpoint barycentric arithmetic;
                // never repair a nonrealizable physical state.
                if b < -2e-12 || b > 1. + 2e-12 || !b.is_finite() {
                    return Err(format!("nonrealizable overlap mean {b:e}"));
                }
                let b = b.clamp(0., 1.);
                y[j].left += q * (1. - b);
                y[j].right += q * b;
                raw_x[j] += xm;
            }
            for (face, k) in [(lo, self.red), (hi, self.blue)] {
                let v = pre[k];
                let (q, _) = portion(face.min(v), face.max(v))?;
                if k == self.red {
                    if dz > 0. {
                        ri += q
                    } else {
                        ro += q
                    }
                } else if dz > 0. {
                    bo += q
                } else {
                    bi += q
                }
            }
        }
        let n1 = self.number(&y);
        let x1 = self.detuning(&y);
        let work = f * (ratio * n0 + x0);
        let scale = n0.max(f64::MIN_POSITIVE);
        let xs = (scale * self.edges.iter().map(|x| x.abs()).fold(1., f64::max) + work.abs())
            .max(f64::MIN_POSITIVE);
        let core = |m: &[Cell]| sum(m[self.red..self.blue].iter().map(|x| x.number()));
        let core_change = core(&y) - core(m);
        let crossing = ri + bi - ro - bo;
        let projection_core =
            sum((self.red..self.blue)
                .map(|j| y[j].moment(self.edges[j], self.edges[j + 1]) - raw_x[j]));
        let projection_exterior = sum((0..y.len())
            .filter(|j| *j < self.red || *j >= self.blue)
            .map(|j| y[j].moment(self.edges[j], self.edges[j + 1]) - raw_x[j]));
        let core_x = |m: &[Cell]| {
            sum((self.red..self.blue).map(|j| m[j].moment(self.edges[j], self.edges[j + 1])))
        };
        let dx_core = core_x(&y) - core_x(m);
        let face_x = lo * (ri - ro) + hi * (bi - bo);
        let core_centered_defect = (dx_core - core_work - face_x).abs() / xs;
        let exterior_centered_defect =
            (x1 - x0 - dx_core + xe - (work - core_work) + face_x).abs() / xs;
        Ok(Drift {
            core_work_x: core_work,
            face_x,
            core_centered_defect,
            exterior_centered_defect,
            cells: y,
            escaped_mass: esc,
            escaped_x: xe,
            work_x: work,
            number_defect: (n1 + esc - n0).abs() / scale,
            centered_defect: (x1 + xe - x0 - work).abs() / xs,
            core_number_defect: (core_change - crossing).abs() / scale,
            exterior_number_defect: ((n1 - core(m) - core_change) - (n0 - core(m))
                + crossing
                + esc)
                .abs()
                / scale,
            projection_core_x: projection_core,
            projection_exterior_x: projection_exterior,
            red_in: ri,
            red_out: ro,
            blue_in: bi,
            blue_out: bo,
            atom_energy: 0.,
        })
    }
}

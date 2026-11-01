//! Immutable, opt-in temperature-only rate interpolation. No derivative API.
use crate::{igm_rates::{igm_rates, IgmRates, IgmRateDiagnostics}, ForwardError};
use std::sync::Arc;

pub const MAX_TABLE_NODES: usize = 65537;
pub const IGM_CHANNELS: usize = 15;
/// Selected by the retained sampled-accuracy experiment, not a global bound.
pub const IGM_TABLE_DEFAULT_NODES: usize = 65537;
pub const IGM_DIRECT_EVALUATOR: &str = "IGM_GRACKLE_DIRECT_F64_V1";
pub const IGM_TABLE_EVALUATOR: &str = "IGM_GRACKLE_LOGLINEAR_F64_V1";

/// Coefficient-major log storage. The caller certifies source smoothness and
/// structural zeros; equal zero endpoints alone never certify an interval.
#[derive(Clone, Debug)]
pub struct LogRateGrid<const N: usize> {
    lower: f64, upper: f64, log_lower: f64, inv_step: f64,
    logs: [Vec<f64>; N], blocked: Vec<bool>, zeros: Vec<[bool; N]>,
}
impl<const N: usize> LogRateGrid<N> {
    pub fn build(
        lower: f64, upper: f64, nodes: usize,
        reference: impl Fn(f64) -> Result<[f64; N], ForwardError>,
        blocked: impl Fn(f64, f64) -> bool,
        structural_zero: impl Fn(usize, f64, f64) -> bool,
    ) -> Result<Self, ForwardError> {
        if !lower.is_normal() || !upper.is_normal() || lower <= 0.0 || upper <= lower
            || !(2..=MAX_TABLE_NODES).contains(&nodes) {
            return Err(ForwardError::InvalidInput("RATE_TABLE_GRID"));
        }
        let log_lower = lower.ln();
        let step = (upper.ln() - log_lower) / (nodes - 1) as f64;
        if !step.is_normal() || step <= 0.0 {
            return Err(ForwardError::InvalidInput("RATE_TABLE_GRID"));
        }
        let temperatures: Vec<_> = (0..nodes).map(|i| {
            if i == 0 { lower } else if i + 1 == nodes { upper }
            else { (log_lower + step * i as f64).exp() }
        }).collect();
        let values = temperatures.iter().map(|&t| reference(t)).collect::<Result<Vec<_>, _>>()?;
        let logs = std::array::from_fn(|j| values.iter().map(|v| {
            if v[j].is_normal() && v[j] > 0.0 { v[j].ln() } else { 0.0 }
        }).collect());
        let mut bad = Vec::with_capacity(nodes - 1);
        let mut zeros = Vec::with_capacity(nodes - 1);
        for i in 0..nodes - 1 {
            let mut invalid = blocked(temperatures[i], temperatures[i + 1]);
            let z = std::array::from_fn(|j| {
                let certified = structural_zero(j, temperatures[i], temperatures[i + 1])
                    && values[i][j] == 0.0 && values[i + 1][j] == 0.0;
                if !certified && !(values[i][j].is_normal() && values[i][j] > 0.0
                    && values[i + 1][j].is_normal() && values[i + 1][j] > 0.0) {
                    invalid = true;
                }
                certified
            });
            bad.push(invalid); zeros.push(z);
        }
        Ok(Self { lower, upper, log_lower, inv_step: 1.0 / step,
            logs, blocked: bad, zeros })
    }
    pub fn nodes(&self) -> usize { self.blocked.len() + 1 }
    pub fn domain(&self) -> [f64; 2] { [self.lower, self.upper] }
    pub fn blocked_cells(&self) -> usize { self.blocked.iter().filter(|&&b| b).count() }
    pub fn storage_bytes(&self) -> usize {
        N * self.nodes() * std::mem::size_of::<f64>()
            + self.blocked.len() * (std::mem::size_of::<bool>() + std::mem::size_of::<[bool; N]>())
    }
    fn cell(&self, t: f64) -> Option<(usize, f64)> {
        if !t.is_finite() || t < self.lower || t > self.upper { return None; }
        let x = (t.ln() - self.log_lower) * self.inv_step;
        let i = (x.floor() as usize).min(self.nodes() - 2);
        if self.blocked[i] { None } else { Some((i, (x - i as f64).clamp(0.0, 1.0))) }
    }
    pub fn evaluate(&self, t: f64, reference: impl Fn(f64) -> Result<[f64; N], ForwardError>)
        -> Result<[f64; N], ForwardError> {
        let Some((i, theta)) = self.cell(t) else { return reference(t); };
        Ok(std::array::from_fn(|j| if self.zeros[i][j] { 0.0 } else {
            (self.logs[j][i] + theta * (self.logs[j][i + 1] - self.logs[j][i])).exp()
        }))
    }
    /// Shared coordinates followed by channel-major loops; no SIMD guarantee.
    pub fn evaluate_batch_soa(&self, temperatures: &[f64],
        reference: impl Fn(f64) -> Result<[f64; N], ForwardError>) -> Result<[Vec<f64>; N], ForwardError> {
        let cells: Vec<_> = temperatures.iter().map(|&t| self.cell(t)).collect();
        let direct = temperatures.iter().zip(&cells).map(|(&t, c)| {
            if c.is_none() { reference(t).map(Some) } else { Ok(None) }
        }).collect::<Result<Vec<_>, _>>()?;
        Ok(std::array::from_fn(|j| cells.iter().enumerate().map(|(q, cell)| {
            if let Some((i, theta)) = *cell {
                if self.zeros[i][j] { 0.0 } else {
                    (self.logs[j][i] + theta * (self.logs[j][i + 1] - self.logs[j][i])).exp()
                }
            } else { direct[q].as_ref().unwrap()[j] }
        }).collect()))
    }
    pub fn evaluate_batch_parallel(&self, temperatures: &[f64], workers: usize,
        reference: impl Fn(f64) -> Result<[f64; N], ForwardError> + Sync)
        -> Result<[Vec<f64>; N], ForwardError> {
        if !(1..=4).contains(&workers) { return Err(ForwardError::InvalidInput("RATE_BATCH_WORKERS")); }
        if workers == 1 || temperatures.is_empty() { return self.evaluate_batch_soa(temperatures, reference); }
        let chunk = temperatures.len().div_ceil(workers);
        let parts = std::thread::scope(|scope| {
            let handles: Vec<_> = temperatures.chunks(chunk).map(|ts| {
                let r = &reference;
                scope.spawn(move || self.evaluate_batch_soa(ts, r))
            }).collect();
            handles.into_iter().map(|h| h.join().map_err(|_| ForwardError::InvalidInput("RATE_BATCH_WORKER_PANIC"))?)
                .collect::<Result<Vec<_>, ForwardError>>()
        })?;
        let mut output: [Vec<f64>; N] = std::array::from_fn(|_| Vec::with_capacity(temperatures.len()));
        for part in parts { for (out, data) in output.iter_mut().zip(part) { out.extend(data); } }
        Ok(output)
    }
}

pub fn igm_flat(r: IgmRates) -> [f64; IGM_CHANNELS] {
    [r.ci_cm3_s[0],r.ci_cm3_s[1],r.ci_cm3_s[2],r.rr_cm3_s[0],r.rr_cm3_s[1],r.rr_cm3_s[2],
        r.dr_cm3_s,r.ce_erg[0],r.ce_erg[1],r.ce_erg[2],r.rr_cooling_erg_cm3_s[0],
        r.rr_cooling_erg_cm3_s[1],r.rr_cooling_erg_cm3_s[2],r.dr_raw_cooling_erg_cm3_s,r.freefree_erg_cm3_s]
}
fn low(t: f64) -> bool { t / 11605.0 <= 0.8 }
fn floor_mask(t: f64) -> [bool;3] {
    igm_rates(t).map(|r| std::array::from_fn(|j| r.diagnostics.ci_floor_cm3_s[j] != 0.0)).unwrap()
}
pub fn igm_branch_knots() -> [f64;7] {
    let l = 69.07755278982137;
    [5500.0,9284.0,118348.0/l,13179.0/l,473638.0/l,470000.0/l,94000.0/l]
}
fn unpack(t: f64, mut v: [f64;15], floor: [bool;3]) -> IgmRates {
    for j in 0..3 { if floor[j] { v[j] = 1e-20; } }
    let ce = [v[7],v[8],v[9]];
    IgmRates { ci_cm3_s:[v[0],v[1],v[2]],rr_cm3_s:[v[3],v[4],v[5]],dr_cm3_s:v[6],ce_erg:ce,
        rr_cooling_erg_cm3_s:[v[10],v[11],v[12]],dr_cooling_erg_cm3_s:if low(t){0.0}else{v[13]},
        dr_raw_cooling_erg_cm3_s:v[13],freefree_erg_cm3_s:v[14],
        diagnostics:IgmRateDiagnostics {ci_floor_cm3_s:std::array::from_fn(|j|if floor[j]{v[j]}else{0.0}),
            ce_cap_erg:std::array::from_fn(|j|if [118348.0,13179.0,473638.0][j]/t >69.07755278982137{ce[j]}else{0.0}),
            dr_excluded_erg_cm3_s:if low(t){v[13]}else{0.0},dr_low_branch:low(t)} }
}
/// Immutable Grackle bundle table. Source units and diagnostics are retained.
#[derive(Clone, Debug)]
pub struct IgmRateTable { grid: LogRateGrid<15>, floors: Vec<[bool;3]> }
impl IgmRateTable {
    pub fn build_default() -> Result<Self,ForwardError> { Self::new(IGM_TABLE_DEFAULT_NODES) }
    pub fn new(nodes:usize) -> Result<Self,ForwardError> { Self::with_domain(1.0,1e6,nodes) }
    pub fn with_domain(lower:f64,upper:f64,nodes:usize) -> Result<Self,ForwardError> {
        if lower < 1.0 || upper > 1e6 {return Err(ForwardError::InvalidInput("IGM_TEMPERATURE_DOMAIN"));}
        let grid = LogRateGrid::build(lower,upper,nodes,|t|igm_rates(t).map(igm_flat),|a,b| {
            low(a)!=low(b) || floor_mask(a)!=floor_mask(b)
                || igm_branch_knots().iter().any(|&k|a<=k && k<=b)
        },|j,a,b|j==6 && low(a) && low(b))?;
        let [a,b]=grid.domain(); let h=(b.ln()-a.ln())/(nodes-1)as f64;
        let floors=(0..nodes-1).map(|i|floor_mask(if i==0{a}else{(a.ln()+h*i as f64).exp()})).collect();
        Ok(Self{grid,floors})
    }
    pub fn grid(&self)->&LogRateGrid<15>{&self.grid}
    /// Heap coefficient/mask payload; excludes small vector/struct headers.
    pub fn storage_bytes(&self)->usize{self.grid.storage_bytes()+self.floors.len()*std::mem::size_of::<[bool;3]>()}
    pub fn rates(&self,t:f64)->Result<IgmRates,ForwardError>{
        let Some((i,_))=self.grid.cell(t)else{return igm_rates(t);};
        let values=self.grid.evaluate(t,|t|igm_rates(t).map(igm_flat))?;
        Ok(unpack(t,values,self.floors[i]))
    }
    pub fn batch_soa(&self,ts:&[f64])->Result<[Vec<f64>;15],ForwardError>{
        let mut rows=self.grid.evaluate_batch_soa(ts,|t|igm_rates(t).map(igm_flat))?;
        self.fix_floors(ts,&mut rows); Ok(rows)
    }
    pub fn batch_parallel(&self,ts:&[f64],workers:usize)->Result<[Vec<f64>;15],ForwardError>{
        let mut rows=self.grid.evaluate_batch_parallel(ts,workers,|t|igm_rates(t).map(igm_flat))?;
        self.fix_floors(ts,&mut rows); Ok(rows)
    }
    fn fix_floors(&self,ts:&[f64],rows:&mut[Vec<f64>;15]){
        for(q,&t)in ts.iter().enumerate(){if let Some((i,_))=self.grid.cell(t){for j in 0..3{if self.floors[i][j]{rows[j][q]=1e-20;}}}}
    }
}
/// The default evaluator is the unchanged direct source provider.
#[derive(Clone,Debug,Default)]
pub enum IgmRateBackend { #[default] Direct, Table(Arc<IgmRateTable>) }
impl IgmRateBackend {
    pub fn rates(&self,t:f64)->Result<IgmRates,ForwardError>{match self{Self::Direct=>igm_rates(t),Self::Table(table)=>table.rates(t)}}
    pub fn evaluator_id(&self)->&'static str{match self{Self::Direct=>IGM_DIRECT_EVALUATOR,Self::Table(_)=>IGM_TABLE_EVALUATOR}}
    pub fn prepare(&self,t:f64)->Result<PreparedIgmRates,ForwardError>{Ok(PreparedIgmRates{temperature_k:t,rates:self.rates(t)?,evaluator_id:self.evaluator_id()})}
}
/// Private fields bind a reusable bundle to its exact temperature/evaluator.
#[derive(Clone,Copy,Debug)]
pub struct PreparedIgmRates {temperature_k:f64,rates:IgmRates,evaluator_id:&'static str}
impl PreparedIgmRates {
    pub fn temperature_k(&self)->f64{self.temperature_k}
    pub fn rates(&self)->IgmRates{self.rates}
    pub fn evaluator_id(&self)->&'static str{self.evaluator_id}
}

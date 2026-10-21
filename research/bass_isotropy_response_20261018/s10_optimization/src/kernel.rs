//! Ordered scalar/SIMD terms and immutable-bank bounded caches.
use crate::{Cohort, Evaluation, FrozenBank, Mode};
use serde::Serialize;
use std::sync::{Arc, Mutex};
use std::sync::atomic::{AtomicU64, Ordering};

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum Backend { Scalar, Avx2 }

#[derive(Clone, Copy, Debug, Default, Eq, PartialEq, Serialize)]
pub struct CacheCounters {
    pub enabled: bool,
    pub kernel_evaluations: u64,
    pub rhs_cache_hits: u64,
    pub jvp_cache_hits: u64,
    pub jvp_rhs_transfers: u64,
}

#[derive(Default)]
struct DiagnosticCounters {
    enabled: bool,
    kernel_evaluations: AtomicU64,
    rhs_cache_hits: AtomicU64,
    jvp_cache_hits: AtomicU64,
    jvp_rhs_transfers: AtomicU64,
}
impl DiagnosticCounters {
    fn add(&self, counter: &AtomicU64) {
        if self.enabled { counter.fetch_add(1, Ordering::Relaxed); }
    }
    fn snapshot(&self) -> CacheCounters {
        CacheCounters {enabled:self.enabled,
            kernel_evaluations:self.kernel_evaluations.load(Ordering::Relaxed),
            rhs_cache_hits:self.rhs_cache_hits.load(Ordering::Relaxed),
            jvp_cache_hits:self.jvp_cache_hits.load(Ordering::Relaxed),
            jvp_rhs_transfers:self.jvp_rhs_transfers.load(Ordering::Relaxed)}
    }
}

/// Exact original Neumaier update. Each channel receives the same term bits and
/// the same sequence as S9. No pair reduction or FMA is used.
#[derive(Default)]
struct OrderedSum { sum: f64, correction: f64 }
impl OrderedSum {
    #[inline]
    fn push(&mut self, x: f64) {
        let t = self.sum + x;
        self.correction += if self.sum.abs() >= x.abs() {
            (self.sum - t) + x
        } else { (x - t) + self.sum };
        self.sum = t;
    }
    #[inline]
    fn finish(self) -> f64 { self.sum + self.correction }
}

fn ordered_sum(values: impl Iterator<Item=f64>) -> f64 {
    let mut s = OrderedSum::default();
    for value in values { s.push(value); }
    s.finish()
}

struct PreparedCohort { z: Vec<f64>, alpha: Vec<f64> }

#[derive(Clone, Copy, Eq, PartialEq)]
struct Key([u64; 4]);
impl Key {
    fn new(x:f64, [h,b,y]:[f64;3]) -> Self {
        Self([x.to_bits(),h.to_bits(),b.to_bits(),y.to_bits()])
    }
}

#[derive(Clone)]
struct Entry { key: Key, evaluation: Evaluation }

/// A bank is immutable for this evaluator's entire lifetime. Both slots are
/// bounded to one entry; their bank identity is the owning evaluator itself.
/// No mutable reference to the bank/prepared data is exposed.
pub struct Evaluator {
    bank: Arc<FrozenBank>,
    mode: Mode,
    prepared: Vec<PreparedCohort>,
    backend: Backend,
    rhs_slot: Mutex<Option<Entry>>,
    jvp_slot: Mutex<Option<Entry>>,
    diagnostics: DiagnosticCounters,
}

impl Evaluator {
    pub fn new(bank:FrozenBank, mode:Mode) -> Self {
        Self::construct(Arc::new(bank), mode, false, false)
    }
    pub fn with_diagnostics(bank:FrozenBank, mode:Mode) -> Self {
        Self::construct(Arc::new(bank), mode, true, false)
    }
    /// Exercise the supported scalar fallback even on an AVX2 host.
    pub fn with_scalar_fallback(bank:FrozenBank, mode:Mode) -> Self {
        Self::construct(Arc::new(bank), mode, false, true)
    }
    pub(crate) fn from_arc(bank:Arc<FrozenBank>, mode:Mode) -> Self {
        Self::construct(bank, mode, false, false)
    }
    fn construct(bank:Arc<FrozenBank>, mode:Mode, diagnostics:bool, force_scalar:bool) -> Self {
        let prepared = if mode.prepared() {
            bank.cohorts.iter().map(|c| PreparedCohort {
                z:c.mu.iter().map(|m| m*m).collect(), alpha:c.alpha.clone(),
            }).collect()
        } else { vec![] };
        let mut backend=Backend::Scalar;
        if mode.simd() && !force_scalar {
            #[cfg(target_arch="x86_64")]
            if std::arch::is_x86_feature_detected!("avx2") { backend=Backend::Avx2; }
        }
        Self {bank,mode,prepared,backend,rhs_slot:Mutex::new(None),jvp_slot:Mutex::new(None),
            diagnostics:DiagnosticCounters {enabled:diagnostics,..Default::default()}}
    }
    pub fn backend(&self) -> Backend { self.backend }
    pub fn counters(&self) -> CacheCounters { self.diagnostics.snapshot() }

    fn valid_point(x:f64, state:[f64;3]) -> Result<(),String> {
        if !x.is_finite() || state.iter().any(|v| !v.is_finite()) || state[0]<=0.0 {
            return Err("BACKGROUND_POSITIVE_FINITE_DOMAIN".into());
        }
        Ok(())
    }

    fn lookup(slot:&Mutex<Option<Entry>>,key:Key) -> Option<Evaluation> {
        let guard=slot.lock().unwrap_or_else(|poisoned| poisoned.into_inner());
        guard.as_ref().filter(|e| e.key==key).map(|e| e.evaluation.clone())
    }
    fn store(slot:&Mutex<Option<Entry>>,key:Key,evaluation:&Evaluation) {
        let mut guard=slot.lock().unwrap_or_else(|poisoned| poisoned.into_inner());
        *guard=Some(Entry {key,evaluation:evaluation.clone()});
    }

    pub fn eval(&self,x:f64,state:[f64;3]) -> Result<Evaluation,String> {
        if self.mode==Mode::Baseline {
            self.diagnostics.add(&self.diagnostics.kernel_evaluations);
            return self.bank.eval(x,state);
        }
        Self::valid_point(x,state)?;
        if self.mode.cached() {
            let key=Key::new(x,state);
            if let Some(e)=Self::lookup(&self.rhs_slot,key) {
                self.diagnostics.add(&self.diagnostics.rhs_cache_hits);
                return Ok(e);
            }
            let e=self.uncached(x,state)?;
            Self::store(&self.rhs_slot,key,&e);
            Ok(e)
        } else { self.uncached(x,state) }
    }

    pub fn jvp(&self,x:f64,state:[f64;3],direction:[f64;3]) -> Result<[f64;3],String> {
        if self.mode==Mode::Baseline {
            self.diagnostics.add(&self.diagnostics.kernel_evaluations);
            return self.bank.jvp(x,state,direction);
        }
        // Preserve original error precedence: invalid direction before state.
        if direction.iter().any(|v| !v.is_finite()) { return Err("JVP_DIRECTION_DOMAIN".into()); }
        Self::valid_point(x,state)?;
        let e=if self.mode.cached() {
            let key=Key::new(x,state);
            if let Some(e)=Self::lookup(&self.jvp_slot,key) {
                self.diagnostics.add(&self.diagnostics.jvp_cache_hits);
                e
            } else {
                let e=if let Some(e)=Self::lookup(&self.rhs_slot,key) {
                    self.diagnostics.add(&self.diagnostics.jvp_rhs_transfers);
                    e
                } else { self.uncached(x,state)? };
                Self::store(&self.jvp_slot,key,&e);
                e
            }
        } else { self.uncached(x,state)? };
        Ok(std::array::from_fn(|i| ordered_sum((0..3).map(|k| e.jacobian[i][k]*direction[k]))))
    }

    fn uncached(&self,x:f64,state:[f64;3]) -> Result<Evaluation,String> {
        self.diagnostics.add(&self.diagnostics.kernel_evaluations);
        let [h,b,y]=state;
        let mut totals:[OrderedSum;3]=std::array::from_fn(|_|OrderedSum::default());
        for (index,c) in self.bank.cohorts.iter().enumerate() {
            let prepared=if self.mode.prepared() {Some(&self.prepared[index])} else {None};
            let m=moments(c,prepared,self.backend,x,b);
            for i in 0..3 {totals[i].push(m[i]);}
        }
        let [e,p,pb]=totals.map(OrderedSum::finish);
        let ed=self.bank.donor0*(-3.0*x-self.bank.decay_lambda*self.bank.exposure).exp();
        let fh=(-h*h-2.0*y*y-0.5*ed-e+self.bank.cosmological_constant)/h;
        let rhs=[fh,y/h,-3.0*y+p/h];
        let jacobian=[
            [-2.0-fh/h,2.0*p/h,-4.0*y/h],
            [-y/(h*h),0.0,1.0/h],
            [-p/(h*h),pb/h,-3.0],
        ];
        let partial_t=[(1.5*ed+4.0*e)/h,0.0,-4.0*p/h];
        if rhs.iter().chain(jacobian.iter().flatten()).chain(&partial_t)
            .chain([e,p,pb,ed].iter()).any(|v|!v.is_finite()) {
            return Err("KERNEL_NONFINITE".into());
        }
        Ok(Evaluation {rhs,jacobian,partial_t,energy:e,pi:p,pi_b:pb,donor:ed})
    }
}

#[inline]
fn scalar_terms(z:f64,w:f64,perp:f64,para:f64) -> [f64;3] {
    let (a,c)=(perp*(1.0-z),para*z);
    let r=(a+c).sqrt();
    let n=c-a/2.0;
    let dd=(-4.0*c-a)/r+2.0*n*n/(r*r*r);
    [w*r,w*n/r,w*dd]
}

fn moments(cohort:&Cohort,prepared:Option<&PreparedCohort>,backend:Backend,x:f64,b:f64) -> [f64;3] {
    let d=b-cohort.b_birth;
    let (perp,para)=((2.0*d).exp(),(-4.0*d).exp());
    let factor=cohort.energy_birth*(-4.0*(x-cohort.u)).exp();
    let mut totals:[OrderedSum;3]=std::array::from_fn(|_|OrderedSum::default());
    if let Some(prepared)=prepared {
        let count=prepared.z.len().min(prepared.alpha.len());
        let mut index=0;
        #[cfg(target_arch="x86_64")]
        if backend==Backend::Avx2 {
            while index+4<=count {
                // SAFETY: construct() selected this backend only after AVX2
                // detection. Four in-bounds elements exist in both arrays.
                let terms=unsafe {avx2_terms(prepared.z.as_ptr().add(index),
                    prepared.alpha.as_ptr().add(index),perp,para)};
                for lane in 0..4 {
                    for channel in 0..3 {totals[channel].push(terms[channel][lane]);}
                }
                index+=4;
            }
        }
        #[cfg(not(target_arch="x86_64"))]
        let _=backend;
        for i in index..count {
            let terms=scalar_terms(prepared.z[i],prepared.alpha[i],perp,para);
            for channel in 0..3 {totals[channel].push(terms[channel]);}
        }
    } else {
        for (&m,&w) in cohort.mu.iter().zip(&cohort.alpha) {
            let terms=scalar_terms(m*m,w,perp,para);
            for channel in 0..3 {totals[channel].push(terms[channel]);}
        }
    }
    totals.map(|s|factor*s.finish())
}

/// Conservative AVX2 gate, even though these four-lane floating point
/// instructions themselves need AVX. Original parenthesization is explicit.
#[cfg(target_arch="x86_64")]
#[target_feature(enable="avx2")]
unsafe fn avx2_terms(z:*const f64,w:*const f64,perp:f64,para:f64) -> [[f64;4];3] {
    use std::arch::x86_64::*;
    unsafe {
        let z=_mm256_loadu_pd(z);
        let w=_mm256_loadu_pd(w);
        let two=_mm256_set1_pd(2.0);
        let a=_mm256_mul_pd(_mm256_set1_pd(perp),_mm256_sub_pd(_mm256_set1_pd(1.0),z));
        let c=_mm256_mul_pd(_mm256_set1_pd(para),z);
        let r=_mm256_sqrt_pd(_mm256_add_pd(a,c));
        let n=_mm256_sub_pd(c,_mm256_div_pd(a,two));
        let left=_mm256_div_pd(_mm256_sub_pd(_mm256_mul_pd(_mm256_set1_pd(-4.0),c),a),r);
        let numerator=_mm256_mul_pd(_mm256_mul_pd(two,n),n);
        let denominator=_mm256_mul_pd(_mm256_mul_pd(r,r),r);
        let dd=_mm256_add_pd(left,_mm256_div_pd(numerator,denominator));
        let values=[_mm256_mul_pd(w,r),_mm256_div_pd(_mm256_mul_pd(w,n),r),_mm256_mul_pd(w,dd)];
        let mut result=[[0.0;4];3];
        for i in 0..3 {_mm256_storeu_pd(result[i].as_mut_ptr(),values[i]);}
        result
    }
}

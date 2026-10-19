//! S7: original-owner finite-bin births, frozen survivor transport, and a
//! controlled final-opacity slab. No owner or production evolution is changed.
#![forbid(unsafe_code)]
#[path = "balance.rs"] mod balance;
#[path = "balance_p24.rs"] mod balance_p24;
mod native_adapter;
use native_adapter::{sum, p2, Constraints, Declaration, inject_new_isotropic};
use rei_microphysics::axbi_covariant_transport::{CovariantTransport, PhotonState, FIT_THRESHOLDS_EV};
use rei_microphysics::axbi_sources::{AxbiSource, SOURCE_ID};
use rei_microphysics::{Absorber, AtomicProvider, AxisymmetricPoint, GeometrySnapshot, HHeModel};
use std::fs::OpenOptions;
use std::io::Write;

const OWNER: &str = "0e25846433170d0f420c4cda44a0bedbf02cd177";
const AREF: f64 = 1.0 / 21.0;
const H: f64 = 1e-16;
const END_BIRTH: f64 = 0.8;
const NH0: f64 = 1.88e-7;
const SLAB_DT: f64 = 1e12;
type ResultS<T> = Result<T, String>;
fn native<T>(r: Result<T, rei_microphysics::ForwardError>) -> ResultS<T> { r.map_err(|e| e.to_string()) }
fn arr(xs: &[f64]) -> String { format!("[{}]", xs.iter().map(|x| format!("{x:.17e}")).collect::<Vec<_>>().join(",")) }
fn geometry(x: f64, b0: f64, beta: f64) -> ResultS<GeometrySnapshot> {
    native(native(AxisymmetricPoint::new(AREF * x.exp(), b0 + beta*x, H, beta*H))?.snapshot())
}
fn kernel(d: f64, mu: f64) -> (f64, f64) {
    let a = (2.0*d).exp()*(1.0-mu*mu); let b = (-4.0*d).exp()*mu*mu;
    let r = (a+b).sqrt(); (r, (b-0.5*a)/r)
}
#[derive(Clone, Debug)]
struct Case { id: String, block: String, nmu: usize, ne: usize, cps: usize, k: usize,
    b0: f64, beta: f64, x: f64, mode: String, slab: bool }
impl Case {
    fn parse(line: &str) -> ResultS<Self> {
        let p: Vec<_> = line.split(',').collect();
        if p.len()!=11 { return Err("CASE_COLUMNS".into()); }
        if p[..2].iter().any(|s| s.is_empty() || !s.chars().all(|c| c.is_ascii_alphanumeric() || c=='_')) {
            return Err("CASE_LABEL".into());
        }
        let i = |j: usize| p[j].parse::<usize>().map_err(|_| "CASE_INTEGER".to_string());
        let f = |j: usize| p[j].parse::<f64>().map_err(|_| "CASE_FLOAT".to_string());
        let c = Self { id:p[0].into(), block:p[1].into(), nmu:i(2)?, ne:i(3)?, cps:i(4)?, k:i(5)?,
            b0:f(6)?, beta:f(7)?, x:f(8)?, mode:p[9].into(), slab:match p[10] {"0"=>false,"1"=>true,_=>return Err("CASE_SLAB".into())} };
        if ![8,16,32].contains(&c.nmu) || !(1..=1024).contains(&c.ne) || !(1..=128).contains(&c.cps)
            || !(1..=256).contains(&c.k) || ![c.b0,c.beta,c.x].iter().all(|v|v.is_finite())
            || c.b0.abs()>1.2 || c.beta.abs()>0.3 || !(0.81..=1.1).contains(&c.x)
            || !["prior","P2","P2P4"].contains(&c.mode.as_str()) { return Err("CASE_DOMAIN".into()); }
        Ok(c)
    }
    fn key(&self) -> String { format!("\"case_id\":\"{}\",\"block\":\"{}\",\"n_mu\":{},\"n_energy\":{},\"cells_per_segment\":{},\"cohorts\":{},\"b0\":{:.17e},\"beta\":{:.17e},\"x_observe\":{:.17e},\"mode\":\"{}\",\"slab\":{}",self.id,self.block,self.nmu,self.ne,self.cps,self.k,self.b0,self.beta,self.x,self.mode,self.slab) }
}
fn weights(t: &CovariantTransport, g: &GeometrySnapshot, mode: &str) -> ResultS<Vec<f64>> {
    let rays=native(t.ray_geometry(g))?;
    let mu:Vec<_>=rays.iter().map(|r|r.mu).collect(); let q:Vec<_>=rays.iter().map(|r|r.angular_weight).collect();
    match mode {
        "prior"=>Ok(q),
        "P2"=>balance::project(&mu,&q,3e-15).map(|r|r.weights).map_err(str::to_string),
        "P2P4"=>balance_p24::project(&mu,&q,3e-15).map(|r|r.weights).map_err(str::to_string),
        _=>Err("MODE".into())
    }
}
fn inject(t:&CovariantTransport,s:&mut PhotonState,g:&GeometrySnapshot,z:f64,dt:f64,mode:&str,w:&[f64])->ResultS<()> {
    if mode=="prior" { native(t.inject(s,g,z,dt))?; }
    else { native(inject_new_isotropic(t,s,g,z,dt,Declaration::locally_isotropic_non_tilted(),
        if mode=="P2" {Constraints::P2}else{Constraints::P2P4},w))?; }
    Ok(())
}
fn merge(t:&CovariantTransport,into:&mut PhotonState,extra:&PhotonState)->ResultS<()> {
    native(t.validate_state(into))?; native(t.validate_state(extra))?;
    for k in 0..t.cell_count() {
        if extra.number[k]==0.0 {continue;}
        if into.number[k]==0.0 {into.support_lo[k]=extra.support_lo[k];into.support_hi[k]=extra.support_hi[k];}
        else {into.support_lo[k]=into.support_lo[k].min(extra.support_lo[k]);into.support_hi[k]=into.support_hi[k].max(extra.support_hi[k]);}
        into.number[k]+=extra.number[k];into.energy_ref[k]+=extra.energy_ref[k];
    }
    native(t.validate_state(into))
}
fn stress(t:&CovariantTransport,s:&PhotonState,g:&GeometrySnapshot)->ResultS<f64> {
    let rays=native(t.ray_geometry(g))?;
    Ok(sum(s.energy_ref.iter().enumerate().map(|(k,u)| u*rays[k/t.n_energy()].scale*p2(rays[k/t.n_energy()].mu))))
}
fn old_stock(t:&CovariantTransport,n:usize)->ResultS<PhotonState> {
    let mut s=t.empty_state();
    for j in [0,n-1] {native(t.add_delta(&mut s,j,5.0,0.0025))?;}
    for j in [n/2-1,n/2] {native(t.add_delta(&mut s,j,40.0,0.001))?;}
    Ok(s)
}
#[derive(Clone)]
struct Cohort {u:f64, n:f64, energy:f64, amount:f64, mu:Vec<f64>, alpha:Vec<f64>, energy_alpha:Vec<f64>, state:PhotonState}
fn gl(n:usize)->Vec<(f64,f64)> {
    let legendre=|x:f64| {let (mut a,mut b)=(1.0,x);for k in 2..=n {let q=((2*k-1) as f64*x*b-(k-1) as f64*a)/k as f64;a=b;b=q;} (b,a)};
    let mut v=Vec::with_capacity(n);
    for i in 0..n/2 {let mut x=(std::f64::consts::PI*(i as f64+0.75)/(n as f64+0.5)).cos();
        for _ in 0..50 {let(p,pm)=legendre(x);let d=n as f64*(x*p-pm)/(x*x-1.0);let nx=x-p/d;if (nx-x).abs()<2e-16{x=nx;break;}x=nx;}
        let(p,pm)=legendre(x);let d=n as f64*(x*p-pm)/(x*x-1.0);let w=2.0/((1.0-x*x)*d*d);v.push((-x,w));v.push((x,w));
    }
    v.sort_by(|a,b|a.0.total_cmp(&b.0));v
}
fn shape(e:f64)->f64 {let m=HHeModel::controlled_fixture(); e*e/(e/(50000.0*m.kb_erg_k/m.ev_erg)).exp_m1()}
#[derive(Default,Clone)]
struct Slab {n:f64,u:f64,p:f64,absorbed:[f64;3],binding:f64,heat:f64}
fn direct_slab(source:&AxbiSource, cohorts:&[Cohort], c:&Case, order:usize)->ResultS<Slab> {
    let provider=AtomicProvider::reference();let model=HHeModel::controlled_fixture();
    let species=[Absorber::HI,Absorber::HeI,Absorber::HeII];
    let density=NH0/(AREF*c.x.exp()).powi(3);let absorber=[0.01*density,0.005*density,0.002*density];
    let quad=gl(order);let norm_quad=gl(8);let mut terms=Vec::<Slab>::new();
    let norms:Vec<_>=source.spectral_cells.iter().map(|s| {let mid=0.5*(s.lower_ev+s.upper_ev);let half=0.5*(s.upper_ev-s.lower_ev);sum(norm_quad.iter().map(|(q,w)|w*half*shape(mid+half*q)))}).collect();
    for cohort in cohorts {for (mu,alpha) in cohort.mu.iter().zip(&cohort.alpha) {
        let(r,d)=kernel(c.beta*(c.x-cohort.u),*mu);let f=(cohort.u-c.x).exp()*r;let p=d/r;
        for (cell,norm) in source.spectral_cells.iter().zip(&norms) {
            let amp=cohort.amount*alpha*cell.photon_fraction/norm;
            let mut edges=vec![cell.lower_ev,cell.upper_ev];
            for th in FIT_THRESHOLDS_EV {let cut=th/f;if cut>cell.lower_ev && cut<cell.upper_ev {edges.push(cut);}}
            edges.sort_by(f64::total_cmp);
            for e in edges.windows(2) {let mid=0.5*(e[0]+e[1]);let half=0.5*(e[1]-e[0]);
                let mut term=Slab::default();
                for (q,w) in &quad {
                    let birth_e=mid+half*q;let now_e=f*birth_e;let mut opacity=[0.0;3];
                    for a in 0..3 {opacity[a]=absorber[a]*native(provider.cross_section(species[a],now_e))?;}
                    let original=amp*w*half*shape(birth_e);let n=original/(1.0+SLAB_DT*model.c_cm_s*sum(opacity.iter().copied()));
                    term.n+=n;term.u+=n*now_e;term.p+=n*now_e*p;
                    for a in 0..3 {let event=n*SLAB_DT*model.c_cm_s*opacity[a];term.absorbed[a]+=event;term.binding+=event*model.threshold_ev[a];term.heat+=event*(now_e-model.threshold_ev[a]);}
                }
                terms.push(term);
            }
        }
    }}
    Ok(Slab {n:sum(terms.iter().map(|s|s.n)),u:sum(terms.iter().map(|s|s.u)),p:sum(terms.iter().map(|s|s.p)),
        absorbed:std::array::from_fn(|a|sum(terms.iter().map(|s|s.absorbed[a]))),binding:sum(terms.iter().map(|s|s.binding)),heat:sum(terms.iter().map(|s|s.heat))})
}
fn slab_json(t:&CovariantTransport,source:&AxbiSource,state:&PhotonState,cohorts:&[Cohort],g:&GeometrySnapshot,c:&Case)->ResultS<String> {
    let before=native(t.inventory(state,g))?;let cache=native(t.prepare(state,g))?;
    let density=NH0/(AREF*c.x.exp()).powi(3);let absorber=[0.01*density,0.005*density,0.002*density];
    let out=native(t.evaluate(&cache,absorber,density,SLAB_DT))?;native(t.validate_state(&out.state))?;
    let after=native(t.inventory(&out.state,g))?;let p=stress(t,&out.state,g)?;
    let ref32=direct_slab(source,cohorts,c,32)?;let ref64=direct_slab(source,cohorts,c,64)?;
    // Applying the same operator to separate cohorts preserves information
    // erased by a merged two-moment closure; report that difference as well.
    let mut sep_n=Vec::new();let mut sep_u=Vec::new();let mut sep_p=Vec::new();
    for birth in cohorts {let prepared=native(t.prepare(&birth.state,g))?;let r=native(t.evaluate(&prepared,absorber,density,SLAB_DT))?;let inv=native(t.inventory(&r.state,g))?;sep_n.push(inv.0);sep_u.push(inv.1);sep_p.push(stress(t,&r.state,g)?);}
    Ok(format!(concat!("{{\"dt_s\":{:.17e},\"n_h_cm3\":{:.17e},\"absorber_cm3\":{},\"native_nodes\":{},",
        "\"before_n\":{:.17e},\"before_u\":{:.17e},\"after_n\":{:.17e},\"after_u\":{:.17e},\"after_stress\":{:.17e},",
        "\"absorbed_per_h\":{},\"binding_ev_per_h\":{:.17e},\"heat_ev_per_h\":{:.17e},\"ledger_n_relative\":{:.17e},\"ledger_u_relative\":{:.17e},",
        "\"separate_cohort_n\":{:.17e},\"separate_cohort_u\":{:.17e},\"separate_cohort_stress\":{:.17e},",
        "\"reference32\":{},\"reference64\":{},\"reconstruction_count_defect\":{:.17e},\"reconstruction_energy_defect\":{:.17e}}}"),
        SLAB_DT,density,arr(&absorber),cache.node_count(),before.0,before.1,after.0,after.1,p,arr(&out.absorbed_per_h),out.binding_ev_per_h,out.heat_ev_per_h,
        (before.0-after.0-sum(out.absorbed_per_h.iter().copied()))/before.0,(before.1-after.1-out.binding_ev_per_h-out.heat_ev_per_h)/before.1,
        sum(sep_n.into_iter()),sum(sep_u.into_iter()),sum(sep_p.into_iter()),
        arr(&[ref32.n,ref32.u,ref32.p,ref32.binding,ref32.heat]),arr(&[ref64.n,ref64.u,ref64.p,ref64.binding,ref64.heat]),
        cache.diagnostics.max_count_relative_defect,cache.diagnostics.max_energy_relative_defect))
}
fn row(c:&Case)->ResultS<String> {
    let source=native(AxbiSource::new(NH0,0.2,c.cps,c.nmu))?;
    let reference=native(GeometrySnapshot::new([AREF;3],[H;3]))?;
    let t=native(CovariantTransport::new(&source,reference,c.ne,0.01,5000.0))?;
    let mut total=old_stock(&t,c.nmu)?;let old=total.clone();let old_frozen=old.clone();
    let mut newborns=t.empty_state();let mut cohorts=Vec::new();let mut details=Vec::new();
    let mut max_merge_n=0.0_f64;let mut max_merge_u=0.0_f64;let mut max_cell_add=0.0_f64;let mut max_cell_relative=0.0_f64;
    for j in 0..c.k {
        let u=END_BIRTH*(j as f64+0.5)/c.k as f64;let dt=END_BIRTH/c.k as f64/H;
        let g=geometry(u,c.b0,c.beta)?;let rays=native(t.ray_geometry(&g))?;
        let w=match weights(&t,&g,&c.mode) {Ok(w)=>w,Err(error)=>{
            let mu:Vec<_>=rays.iter().map(|r|r.mu).collect();
            let kind=if error.starts_with("INFEASIBLE") {"FEASIBILITY_FAILURE"}else{"NUMERICAL_FAILURE"};
            return Ok(format!("{{\"schema\":\"bass.native.cohorts.s7.row.v1\",{},\"status\":\"{}\",\"failure\":\"{}\",\"failed_birth\":{},\"failed_u\":{:.17e},\"support_mu\":{}}}",c.key(),kind,error,j,u,arr(&mu)));
        }};
        let z=21.0*(-u).exp()-1.0;let amount=native(source.at_redshift(z))?.per_h_s*dt;
        let mut birth=t.empty_state();inject(&t,&mut birth,&g,z,dt,&c.mode,&w)?;
        let inv=native(t.inventory(&birth,&g))?;let frozen=total.clone();let before=native(t.inventory(&frozen,&g))?;
        inject(&t,&mut total,&g,z,dt,&c.mode,&w)?;
        for k in 0..t.cell_count() {
            for (actual,expected) in [(total.number[k],frozen.number[k]+birth.number[k]),(total.energy_ref[k],frozen.energy_ref[k]+birth.energy_ref[k])] {
                max_cell_add=max_cell_add.max((actual-expected).abs());
                if expected>0.0 {max_cell_relative=max_cell_relative.max((actual/expected-1.0).abs());}
            }
            if birth.number[k]==0.0 && (total.number[k]!=frozen.number[k] || total.energy_ref[k]!=frozen.energy_ref[k]
                || total.support_lo[k]!=frozen.support_lo[k] || total.support_hi[k]!=frozen.support_hi[k]) {
                return Err("UNTOUCHED_OLD_CELL_CHANGED".into());
            }
        }
        let after=native(t.inventory(&total,&g))?;
        max_merge_n=max_merge_n.max(((after.0-before.0-inv.0)/inv.0).abs());max_merge_u=max_merge_u.max(((after.1-before.1-inv.1)/inv.1).abs());
        merge(&t,&mut newborns,&birth)?;
        let mu:Vec<_>=rays.iter().map(|r|r.mu).collect();
        let energy_alpha:Vec<_>=(0..c.nmu).map(|ray|sum(birth.energy_ref[ray*c.ne..(ray+1)*c.ne].iter().map(|e|e*rays[ray].scale))/inv.1).collect();
        details.push(format!("{{\"u\":{:.17e},\"b\":{:.17e},\"z\":{:.17e},\"dt_s\":{:.17e},\"source_amount\":{:.17e},\"n_birth\":{:.17e},\"u_birth\":{:.17e},\"mu\":{},\"alpha\":{},\"energy_alpha\":{}}}",u,c.b0+c.beta*u,z,dt,amount,inv.0,inv.1,arr(&mu),arr(&w),arr(&energy_alpha)));
        cohorts.push(Cohort {u,n:inv.0,energy:inv.1,amount,mu,alpha:w,energy_alpha,state:birth});
    }
    let g=geometry(c.x,c.b0,c.beta)?;let frozen_newborns=newborns.clone();
    let final_inv=native(t.inventory(&newborns,&g))?;let final_p=stress(&t,&newborns,&g)?;
    let old_inv=native(t.inventory(&old,&g))?;let old_p=stress(&t,&old,&g)?;
    let combined=native(t.inventory(&total,&g))?;let combined_p=stress(&t,&total,&g)?;
    let mut pred_u=Vec::new();let mut pred_p=Vec::new();
    for cohort in &cohorts {for ((mu,alpha),actual) in cohort.mu.iter().zip(&cohort.alpha).zip(&cohort.energy_alpha) {
        let(r,d)=kernel(c.beta*(c.x-cohort.u),*mu);let scale=cohort.energy*(cohort.u-c.x).exp();
        pred_u.push(scale*actual*r);pred_p.push(scale*actual*d);
        if *alpha<=0.0 || !alpha.is_finite() {return Err("POSITIVE_BIRTH_WEIGHT_LOSS".into());}
    }}
    let deriv = |h:f64| -> ResultS<f64> {
        let mut v=[0.0;4];for (j,shift) in [-2.0,-1.0,1.0,2.0].iter().enumerate() {v[j]=native(t.inventory(&newborns,&geometry(c.x+shift*h,c.b0,c.beta)?))?.1;}
        Ok((v[0]-8.0*v[1]+8.0*v[2]-v[3])/(12.0*h))
    };
    let residual=(deriv(1e-3)?+final_inv.1+2.0*c.beta*final_p)/final_inv.1;
    let residual_half=(deriv(5e-4)?+final_inv.1+2.0*c.beta*final_p)/final_inv.1;
    let slab=if c.slab {slab_json(&t,&source,&newborns,&cohorts,&g,c)?}else{"null".into()};
    if old!=old_frozen || newborns!=frozen_newborns {return Err("SURVIVOR_STATE_MUTATION".into());}
    Ok(format!(concat!("{{\"schema\":\"bass.native.cohorts.s7.row.v1\",{},\"status\":\"MEASURED\",",
        "\"source_id\":\"{}\",\"n_final\":{:.17e},\"u_final\":{:.17e},\"stress_final\":{:.17e},\"a_response\":{:.17e},",
        "\"predicted_n\":{:.17e},\"predicted_u\":{:.17e},\"predicted_stress\":{:.17e},",
        "\"old_n\":{:.17e},\"old_u\":{:.17e},\"old_stress\":{:.17e},\"combined_n\":{:.17e},\"combined_u\":{:.17e},\"combined_stress\":{:.17e},",
        "\"max_increment_ledger_n_relative\":{:.17e},\"max_increment_ledger_u_relative\":{:.17e},\"max_cell_add_absolute\":{:.17e},\"max_cell_add_relative\":{:.17e},",
        "\"survivors_bitwise_frozen\":true,\"density_conversion\":\"physical U = per-H U * nH0 / a^3\",",
        "\"energy_continuity_per_h_relative\":{:.17e},\"energy_continuity_half_h_relative\":{:.17e},\"derivative_h\":1e-3,",
        "\"births\":[{}],\"absorption\":{}}}"),c.key(),SOURCE_ID,final_inv.0,final_inv.1,final_p,final_p/final_inv.1,
        sum(cohorts.iter().map(|v|v.n)),sum(pred_u.into_iter()),sum(pred_p.into_iter()),old_inv.0,old_inv.1,old_p,combined.0,combined.1,combined_p,
        max_merge_n,max_merge_u,max_cell_add,max_cell_relative,residual,residual_half,details.join(","),slab))
}
fn run(input:&str,output:&str)->ResultS<usize> {
    let data=std::fs::read_to_string(input).map_err(|e|e.to_string())?;
    let cases:Vec<_>=data.lines().filter(|l|!l.is_empty() && !l.starts_with('#')).map(Case::parse).collect::<ResultS<_>>()?;
    let mut file=OpenOptions::new().write(true).create_new(true).open(output).map_err(|e|e.to_string())?;
    for c in &cases {let record=row(c)?;writeln!(file,"{record}").map_err(|e|e.to_string())?;file.flush().map_err(|e|e.to_string())?;}
    writeln!(file,"{{\"schema\":\"bass.native.cohorts.s7.complete.v1\",\"rows\":{},\"owner_commit\":\"{}\",\"source_id\":\"{}\"}}",cases.len(),OWNER,SOURCE_ID).map_err(|e|e.to_string())?;
    Ok(cases.len())
}
fn main() {let a:Vec<_>=std::env::args().collect();let r=if a.len()==3 {run(&a[1],&a[2])}else{Err("USAGE native_cohort_probe CASES.csv OUTPUT.jsonl".into())};
    match r {Ok(n)=>println!("NATIVE_COHORTS_COMPLETE rows={n}"),Err(e)=>{eprintln!("NATIVE_COHORTS_FAIL:{e}");std::process::exit(3);}}
}

#[cfg(test)] mod cohort_tests {
    use super::*;
    #[test] fn changing_geometry_never_changes_saved_cohort_cells() {
        let source=AxbiSource::new(NH0,0.2,8,8).unwrap();let reference=GeometrySnapshot::new([AREF;3],[H;3]).unwrap();
        let t=CovariantTransport::new(&source,reference,48,0.01,5000.0).unwrap();
        let birth_g=geometry(0.2,0.0,0.2).unwrap();let w=weights(&t,&birth_g,"P2P4").unwrap();let mut state=t.empty_state();
        inject(&t,&mut state,&birth_g,21.0*(-0.2_f64).exp()-1.0,1e13,"P2P4",&w).unwrap();let frozen=state.clone();let at_birth=t.inventory(&state,&birth_g).unwrap();
        let now=geometry(1.0,0.0,0.2).unwrap();let later=t.inventory(&state,&now).unwrap();assert_eq!(state,frozen);assert_eq!(at_birth.0,later.0);assert!(later.1<at_birth.1);
        let mu=t.ray_geometry(&birth_g).unwrap();let predicted=at_birth.1*(-0.8_f64).exp()*sum(mu.iter().zip(&w).map(|(r,a)|a*kernel(0.16,r.mu).0));
        assert!((later.1/predicted-1.0).abs()<3e-15);
    }
    #[test] fn different_birth_epochs_merge_without_erasing_anisotropic_stock() {
        let c=Case::parse("fixture,test,8,48,8,3,0.0,0.2,1.0,P2P4,0").unwrap();let text=row(&c).unwrap();
        assert!(text.contains("\"status\":\"MEASURED\""));assert!(text.contains("\"max_cell_add_absolute\":0.00000000000000000e0"));assert!(text.contains("\"survivors_bitwise_frozen\":true"));
    }
    #[test] fn late_infeasibility_is_a_concrete_case_failure() {
        let c=Case::parse("bad_support,test,8,48,8,4,0.3,0.2,1.0,P2P4,0").unwrap();let text=row(&c).unwrap();
        assert!(text.contains("FEASIBILITY_FAILURE"));assert!(text.contains("INFEASIBLE_P24"));assert!(text.contains("support_mu"));
    }
    #[test] fn gl_rule_is_positive_reflection_even_and_integrates_moments() {
        for n in [8,32,64] {let rule=gl(n);assert_eq!(rule.len(),n);assert!(rule.iter().all(|(_,w)|*w>0.0));assert!((sum(rule.iter().map(|(_,w)|*w))-2.0).abs()<1e-14);
            for k in 0..6 {let value=sum(rule.iter().map(|(x,w)|w*x.powi(2*k)));assert!((value-2.0/(2*k+1) as f64).abs()<5e-15);}
        }
    }
    #[test] fn malformed_case_does_not_start_science() {
        for row in ["x,y,4,48,8,2,0,0.2,1,P2,0","x,y,8,48,8,2,NaN,0.2,1,P2,0","x,y,8,48,8,2,0,0.2,1,reset,0"] {assert!(Case::parse(row).is_err());}
    }
}

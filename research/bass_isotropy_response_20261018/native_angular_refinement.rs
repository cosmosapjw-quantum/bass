//! S8 opt-in reference-angle refinement. Original REI spectral owner is unchanged.
//! Existing n=32 stock remains on its original transport; new photons use a new block.
#![forbid(unsafe_code)]
#[path = "balance.rs"] mod balance;
#[path = "balance_p24.rs"] mod balance_p24;
mod native_adapter;
use native_adapter::{sum, p2, Constraints, Declaration, EmissionKind, EmissionFrame, inject_new_isotropic};
use rei_microphysics::axbi_covariant_transport::{CovariantTransport, PhotonState};
use rei_microphysics::axbi_sources::{AngularCell, AxbiSource, SOURCE_ID};
use rei_microphysics::{AxisymmetricPoint, GeometrySnapshot};
use std::fs::OpenOptions;
use std::io::Write;

const OWNER: &str = "0e25846433170d0f420c4cda44a0bedbf02cd177";
const AREF: f64 = 1.0 / 21.0;
const H: f64 = 1e-16;
const NH0: f64 = 1.88e-7;
const INNER_TOL: f64 = 1e-15;
type ResultS<T> = Result<T, String>;
fn native<T>(r: Result<T, rei_microphysics::ForwardError>) -> ResultS<T> { r.map_err(|e| e.to_string()) }
fn arr(xs: &[f64]) -> String { format!("[{}]",xs.iter().map(|x|format!("{x:.17e}")).collect::<Vec<_>>().join(",")) }
fn geometry(x:f64,b0:f64,beta:f64)->ResultS<GeometrySnapshot> {
    native(native(AxisymmetricPoint::new(AREF*x.exp(),b0+beta*x,H,beta*H))?.snapshot())
}
fn kernel(d:f64,mu:f64)->(f64,f64) {
    let a=(2.0*d).exp()*(1.0-mu*mu);let b=(-4.0*d).exp()*mu*mu;
    let r=(a+b).sqrt();(r,(b-0.5*a)/r)
}
fn legendre(n:usize,x:f64)->(f64,f64) {
    let(mut pm,mut p)=(1.0,x);
    for k in 2..=n {let q=((2*k-1) as f64*x*p-(k-1) as f64*pm)/k as f64;pm=p;p=q;}
    (p,pm)
}
/// Same recurrence, Newton stopping rule and mirrored assignment as the pinned
/// owner's source angular() function. Only its permitted order is extended.
fn reference_rule(n:usize)->ResultS<Vec<AngularCell>> {
    if ![32,64,128,256].contains(&n) {return Err("REFINEMENT_ORDER_DOMAIN".into());}
    let mut out=vec![AngularCell{mu:0.0,count_fraction:0.0};n];
    for i in 0..n/2 {
        let mut x=(std::f64::consts::PI*(i as f64+0.75)/(n as f64+0.5)).cos();
        let mut converged=false;
        for _ in 0..32 {
            let(p,pm)=legendre(n,x);let d=n as f64*(x*p-pm)/(x*x-1.0);let next=x-p/d;
            if (next-x).abs()<=2.0*f64::EPSILON {x=next;converged=true;break;}x=next;
        }
        if !converged {return Err("REFINEMENT_GL_ROOT_NOT_CONVERGED".into());}
        let(p,pm)=legendre(n,x);let d=n as f64*(x*p-pm)/(x*x-1.0);
        let w=1.0/((1.0-x*x)*d*d);
        if !w.is_normal() || w<=0.0 || !x.is_finite() || !(0.0..1.0).contains(&x) {
            return Err("REFINEMENT_GL_POSITIVITY".into());
        }
        out[i]=AngularCell{mu:-x,count_fraction:w};out[n-1-i]=AngularCell{mu:x,count_fraction:w};
    }
    if out.windows(2).any(|p|p[0].mu>=p[1].mu)
        || out.iter().enumerate().any(|(i,r)|!r.mu.is_finite() || r.mu.abs()>1.0
            || !r.count_fraction.is_finite() || r.count_fraction<=0.0
            || r.mu != -out[n-1-i].mu || r.count_fraction.to_bits()!=out[n-1-i].count_fraction.to_bits())
        || (sum(out.iter().map(|r|r.count_fraction))-1.0).abs()>3e-14 {
        return Err("REFINEMENT_GL_NORMALIZATION_OR_ORDER".into());
    }
    Ok(out)
}
fn spectral_bits(source:&AxbiSource)->Vec<u64> {
    let mut out=Vec::new();
    for s in &source.spectral_cells {out.extend([s.lower_ev.to_bits(),s.upper_ev.to_bits(),s.energy_ev.to_bits(),s.photon_fraction.to_bits()]);}
    out.extend([source.normalization_relative_residual.to_bits(),source.omitted_blackbody_tail_photon_fraction.to_bits()]);out
}
fn rate_bits(source:&AxbiSource,z:f64)->ResultS<[u64;3]> {
    let r=native(source.at_redshift(z))?;
    Ok([r.comoving_photons_per_s_cmpc3.to_bits(),r.proper_photons_cm3_s.to_bits(),r.per_h_s.to_bits()])
}
fn source_unchanged(base:&AxbiSource,refined:&AxbiSource)->ResultS<()> {
    if spectral_bits(base)!=spectral_bits(refined) {return Err("SPECTRAL_OWNER_MUTATION".into());}
    for z in [4.0,12.0,20.0] {if rate_bits(base,z)?!=rate_bits(refined,z)? {return Err("SOURCE_RATE_MUTATION".into());}}
    Ok(())
}
fn refined_source(base:&AxbiSource,n:usize,declaration:Declaration)->ResultS<AxbiSource> {
    if declaration.kind!=EmissionKind::LocallyIsotropicNewBirth
        || declaration.frame!=EmissionFrame::NonTiltedLocalOrthonormal {
        return Err("REFINEMENT_NEW_ISOTROPIC_SOURCE_DECLARATION_REQUIRED".into());
    }
    if ![64,128,256].contains(&n) {return Err("REFINEMENT_NEW_ORDER_REQUIRED".into());}
    let mut out=base.clone();out.angular_cells=reference_rule(n)?;source_unchanged(base,&out)?;Ok(out)
}
fn bit_digest(bits:impl Iterator<Item=u64>)->String {
    let mut h=0xcbf29ce484222325_u64;
    for word in bits {for b in word.to_le_bytes() {h^=b as u64;h=h.wrapping_mul(0x100000001b3);}}
    format!("{h:016x}")
}
fn state_bits(s:&PhotonState)->Vec<u64> {
    [&s.number,&s.energy_ref,&s.support_lo,&s.support_hi].iter().flat_map(|v|v.iter().map(|x|x.to_bits())).collect()
}
fn sparse_bits(s:&PhotonState)->String {
    let mut rows=Vec::new();
    for k in 0..s.number.len() {
        let v=[s.number[k].to_bits(),s.energy_ref[k].to_bits(),s.support_lo[k].to_bits(),s.support_hi[k].to_bits()];
        if v.iter().any(|x|*x!=0) {rows.push(format!("[{},\"{:016x}\",\"{:016x}\",\"{:016x}\",\"{:016x}\"]",k,v[0],v[1],v[2],v[3]));}
    }
    format!("[{}]",rows.join(","))
}
#[derive(Clone,Debug)]
struct Case {id:String,n:usize,b0:f64,mode:String}
impl Case {
    fn parse(line:&str)->ResultS<Self> {
        let p:Vec<_>=line.split(',').collect();if p.len()!=4 {return Err("CASE_COLUMNS".into());}
        let c=Self{id:p[0].into(),n:p[1].parse().map_err(|_|"CASE_N")?,b0:p[2].parse().map_err(|_|"CASE_B")?,mode:p[3].into()};
        if c.id.is_empty() || !c.id.chars().all(|x|x.is_ascii_alphanumeric()||x=='_')
            || ![64,128,256].contains(&c.n) || ![0.6,0.9].contains(&c.b0)
            || !["prior","P2","P2P4"].contains(&c.mode.as_str()) {return Err("CASE_DOMAIN".into());}
        Ok(c)
    }
    fn key(&self)->String {format!("\"case_id\":\"{}\",\"n_mu\":{},\"b0\":{:.17e},\"mode\":\"{}\",\"n_energy\":96,\"cells_per_segment\":32,\"cohorts\":16,\"beta\":0.2,\"x_observe\":1.0",self.id,self.n,self.b0,self.mode)}
}
fn weights(t:&CovariantTransport,g:&GeometrySnapshot,mode:&str)->ResultS<Vec<f64>> {
    let rays=native(t.ray_geometry(g))?;let mu:Vec<_>=rays.iter().map(|r|r.mu).collect();let q:Vec<_>=rays.iter().map(|r|r.angular_weight).collect();
    match mode {"prior"=>Ok(q),"P2"=>balance::project(&mu,&q,INNER_TOL).map(|r|r.weights).map_err(str::to_string),
        "P2P4"=>balance_p24::project(&mu,&q,INNER_TOL).map(|r|r.weights).map_err(str::to_string),_=>Err("MODE".into())}
}
fn inject(t:&CovariantTransport,s:&mut PhotonState,g:&GeometrySnapshot,z:f64,dt:f64,mode:&str,w:&[f64])->ResultS<[f64;2]> {
    let ledger=if mode=="prior" {native(t.inject(s,g,z,dt))?}else {
        native(inject_new_isotropic(t,s,g,z,dt,Declaration::locally_isotropic_non_tilted(),
            if mode=="P2" {Constraints::P2}else{Constraints::P2P4},w))?.added
    };
    Ok([ledger.added_photons_per_h,ledger.added_energy_ev_per_h])
}
fn merge(t:&CovariantTransport,into:&mut PhotonState,extra:&PhotonState)->ResultS<()> {
    native(t.validate_state(into))?;native(t.validate_state(extra))?;
    for k in 0..t.cell_count() {
        if extra.number[k]==0.0 {continue;}
        if into.number[k]==0.0 {into.support_lo[k]=extra.support_lo[k];into.support_hi[k]=extra.support_hi[k];}
        else {into.support_lo[k]=into.support_lo[k].min(extra.support_lo[k]);into.support_hi[k]=into.support_hi[k].max(extra.support_hi[k]);}
        into.number[k]+=extra.number[k];into.energy_ref[k]+=extra.energy_ref[k];
    }native(t.validate_state(into))
}
fn values(t:&CovariantTransport,s:&PhotonState,g:&GeometrySnapshot)->ResultS<[f64;3]> {
    let (n,u)=native(t.inventory(s,g))?;let rays=native(t.ray_geometry(g))?;
    let p=sum(s.energy_ref.iter().enumerate().map(|(k,u)|u*rays[k/t.n_energy()].scale*p2(rays[k/t.n_energy()].mu)));
    Ok([n,u,p])
}
fn old_stock(t:&CovariantTransport,n:usize)->ResultS<PhotonState> {
    let mut s=t.empty_state();for j in [0,n-1] {native(t.add_delta(&mut s,j,5.0,0.0025))?;}
    for j in [n/2-1,n/2] {native(t.add_delta(&mut s,j,40.0,0.001))?;}Ok(s)
}
struct Cohort {u:f64,energy:f64,mu:Vec<f64>,energy_alpha:Vec<f64>,state:PhotonState}
fn row(c:&Case)->ResultS<String> {
    let base=native(AxbiSource::new(NH0,0.2,32,32))?;
    let source=refined_source(&base,c.n,Declaration::locally_isotropic_non_tilted())?;
    let reference=native(GeometrySnapshot::new([AREF;3],[H;3]))?;
    let old_t=native(CovariantTransport::new(&base,reference.clone(),96,0.01,5000.0))?;
    let old=old_stock(&old_t,32)?;let old_before=state_bits(&old);let old_sparse=sparse_bits(&old);
    let t=native(CovariantTransport::new(&source,reference,96,0.01,5000.0))?;
    if t.cell_count()!=96*c.n || t.transport_threads()!=1 {return Err("NATIVE_REFINED_GRID_SHAPE".into());}
    let nu:Vec<_>=source.angular_cells.iter().map(|r|r.mu).collect();
    let qref:Vec<_>=source.angular_cells.iter().map(|r|r.count_fraction).collect();
    let grid=format!("\"reference_nu\":{},\"reference_count_fraction\":{}",arr(&nu),arr(&qref));
    // Independent same-grid control tests transactional addition. It is not a
    // remesh of old: the persistent old n32 block above never enters this API.
    let mut control=old_stock(&t,c.n)?;let control_initial=control.clone();let mut newborns=t.empty_state();
    let mut cohorts=Vec::new();let mut details=Vec::new();let mut max_n=0.0_f64;let mut max_u=0.0_f64;
    let mut max_cell_abs=0.0_f64;let mut max_cell_rel=0.0_f64;let mut max_reported_ledger=0.0_f64;
    for j in 0..16 {
        let u=0.8*(j as f64+0.5)/16.0;let dt=0.8/16.0/H;let z=21.0*(-u).exp()-1.0;
        let g=geometry(u,c.b0,0.2)?;let rays=native(t.ray_geometry(&g))?;
        let w=match weights(&t,&g,&c.mode) {Ok(w)=>w,Err(e)=> {
            let kind=if e.starts_with("INFEASIBLE") {"FEASIBILITY_FAILURE"}else {"NUMERICAL_FAILURE"};
            let mu:Vec<_>=rays.iter().map(|r|r.mu).collect();
            return Ok(format!("{{\"schema\":\"bass.native.angular.s8.row.v1\",{},{},\"status\":\"{}\",\"failure\":\"{}\",\"failed_birth\":{},\"failed_u\":{:.17e},\"support_mu\":{},\"internal_moment_tolerance\":1e-15}}",c.key(),grid,kind,e,j,u,arr(&mu)));
        }};
        if rate_bits(&base,z)?!=rate_bits(&source,z)? {return Err("BIRTH_SOURCE_RATE_MUTATION".into());}
        let amount=native(base.at_redshift(z))?.per_h_s*dt;
        let mut birth=t.empty_state();let ledger=inject(&t,&mut birth,&g,z,dt,&c.mode,&w)?;
        let inv=native(t.inventory(&birth,&g))?;
        max_reported_ledger=max_reported_ledger.max((ledger[0]/inv.0-1.0).abs()).max((ledger[1]/inv.1-1.0).abs());
        let before=control.clone();let before_inv=native(t.inventory(&before,&g))?;
        inject(&t,&mut control,&g,z,dt,&c.mode,&w)?;
        for k in 0..t.cell_count() {
            for (a,e) in [(control.number[k],before.number[k]+birth.number[k]),(control.energy_ref[k],before.energy_ref[k]+birth.energy_ref[k])] {
                max_cell_abs=max_cell_abs.max((a-e).abs());if e>0.0 {max_cell_rel=max_cell_rel.max((a/e-1.0).abs());}
            }
            if birth.number[k]==0.0 && [control.number[k].to_bits(),control.energy_ref[k].to_bits(),control.support_lo[k].to_bits(),control.support_hi[k].to_bits()]
                !=[before.number[k].to_bits(),before.energy_ref[k].to_bits(),before.support_lo[k].to_bits(),before.support_hi[k].to_bits()] {
                return Err("UNTOUCHED_CONTROL_CELL_CHANGED".into());
            }
        }
        let after=native(t.inventory(&control,&g))?;
        max_n=max_n.max(((after.0-before_inv.0-inv.0)/inv.0).abs());max_u=max_u.max(((after.1-before_inv.1-inv.1)/inv.1).abs());
        merge(&t,&mut newborns,&birth)?;
        let mu:Vec<_>=rays.iter().map(|r|r.mu).collect();let prior:Vec<_>=rays.iter().map(|r|r.angular_weight).collect();
        let energy_alpha:Vec<_>=(0..c.n).map(|r|sum(birth.energy_ref[r*96..(r+1)*96].iter().map(|v|v*rays[r].scale))/inv.1).collect();
        let photon_alpha:Vec<_>=(0..c.n).map(|r|sum(birth.number[r*96..(r+1)*96].iter().copied())/inv.0).collect();
        details.push(format!("{{\"u\":{:.17e},\"b\":{:.17e},\"z\":{:.17e},\"dt_s\":{:.17e},\"source_amount\":{:.17e},\"n_birth\":{:.17e},\"u_birth\":{:.17e},\"mu\":{},\"prior\":{},\"alpha\":{},\"photon_alpha\":{},\"energy_alpha\":{}}}",u,c.b0+0.2*u,z,dt,amount,inv.0,inv.1,arr(&mu),arr(&prior),arr(&w),arr(&photon_alpha),arr(&energy_alpha)));
        cohorts.push(Cohort{u,energy:inv.1,mu,energy_alpha,state:birth});
    }
    let g=geometry(1.0,c.b0,0.2)?;let new_before=state_bits(&newborns);let final_v=values(&t,&newborns,&g)?;
    let old_v=values(&old_t,&old,&g)?;let mut blocks=vec![old_v];
    let mut predicted=Vec::new();
    for birth in &cohorts {
        blocks.push(values(&t,&birth.state,&g)?);
        for (mu,alpha) in birth.mu.iter().zip(&birth.energy_alpha) {let (r,d)=kernel(0.2*(1.0-birth.u),*mu);let amp=birth.energy*(birth.u-1.0).exp()*alpha;predicted.push([amp*r,amp*d]);}
    }
    let combined:[f64;3]=std::array::from_fn(|j|sum(blocks.iter().map(|v|v[j])));
    let control_v=values(&t,&control,&g)?;let initial_v=values(&t,&control_initial,&g)?;
    let derivative=|h:f64|->ResultS<f64> {
        let mut v=[0.0;4];for (j,s) in [-2.0,-1.0,1.0,2.0].iter().enumerate() {v[j]=native(t.inventory(&newborns,&geometry(1.0+s*h,c.b0,0.2)?))?.1;}
        Ok((v[0]-8.0*v[1]+8.0*v[2]-v[3])/(12.0*h))
    };
    let continuity=[(derivative(1e-3)?+final_v[1]+0.4*final_v[2])/final_v[1],(derivative(5e-4)?+final_v[1]+0.4*final_v[2])/final_v[1]];
    let old_after=state_bits(&old);
    if old_before!=old_after || new_before!=state_bits(&newborns) {return Err("FROZEN_BLOCK_CHANGED".into());}
    source_unchanged(&base,&source)?;
    Ok(format!(concat!("{{\"schema\":\"bass.native.angular.s8.row.v1\",{},{},\"status\":\"MEASURED\",\"source_id\":\"{}\",",
        "\"internal_moment_tolerance\":1e-15,\"spectral_bits_identical\":true,\"source_rate_bits_identical\":true,\"spectral_digest_fnv1a64\":\"{}\",",
        "\"n_final\":{:.17e},\"u_final\":{:.17e},\"stress_final\":{:.17e},\"a_response\":{:.17e},\"predicted_u\":{:.17e},\"predicted_stress\":{:.17e},",
        "\"old_n_mu\":32,\"old_cell_count\":3072,\"old_digest_before_fnv1a64\":\"{}\",\"old_digest_after_fnv1a64\":\"{}\",\"old_sparse_before\":{},\"old_sparse_after\":{},",
        "\"old_values\":{},\"combined_block_values\":{},\"same_grid_control_initial\":{},\"same_grid_control_final\":{},",
        "\"max_increment_ledger_n_relative\":{:.17e},\"max_increment_ledger_u_relative\":{:.17e},\"max_native_reported_ledger_relative\":{:.17e},",
        "\"max_cell_add_absolute\":{:.17e},\"max_cell_add_relative\":{:.17e},\"survivors_bitwise_frozen\":true,",
        "\"energy_continuity_relative\":{},\"births\":[{}]}}"),c.key(),grid,SOURCE_ID,bit_digest(spectral_bits(&source).into_iter()),
        final_v[0],final_v[1],final_v[2],final_v[2]/final_v[1],sum(predicted.iter().map(|v|v[0])),sum(predicted.iter().map(|v|v[1])),
        bit_digest(old_before.into_iter()),bit_digest(old_after.into_iter()),old_sparse,sparse_bits(&old),arr(&old_v),arr(&combined),arr(&initial_v),arr(&control_v),
        max_n,max_u,max_reported_ledger,max_cell_abs,max_cell_rel,arr(&continuity),details.join(",")))
}
fn run(input:&str,output:&str)->ResultS<usize> {
    let input=std::fs::read_to_string(input).map_err(|e|e.to_string())?;
    let cases=input.lines().filter(|l|!l.is_empty()).map(Case::parse).collect::<ResultS<Vec<_>>>()?;
    if cases.is_empty() || cases.len()>18 {return Err("CASE_COUNT".into());}
    let mut file=OpenOptions::new().write(true).create_new(true).open(output).map_err(|e|e.to_string())?;
    for c in &cases {writeln!(file,"{}",row(c)?).map_err(|e|e.to_string())?;file.flush().map_err(|e|e.to_string())?;}
    writeln!(file,"{{\"schema\":\"bass.native.angular.s8.complete.v1\",\"rows\":{},\"owner_commit\":\"{}\",\"source_id\":\"{}\"}}",cases.len(),OWNER,SOURCE_ID).map_err(|e|e.to_string())?;
    Ok(cases.len())
}
fn main() {let a:Vec<_>=std::env::args().collect();let r=if a.len()==3 {run(&a[1],&a[2])}else {Err("USAGE native_angular_refinement CASES.csv OUTPUT.jsonl".into())};
    match r {Ok(n)=>println!("NATIVE_ANGULAR_S8_COMPLETE rows={n}"),Err(e)=>{eprintln!("NATIVE_ANGULAR_S8_FAIL:{e}");std::process::exit(3);}}
}

#[cfg(test)] mod s8_tests {
    use super::*;
    #[test] fn extended_generator_matches_original_32_bits() {
        let base=AxbiSource::new(NH0,0.2,8,32).unwrap();let q=reference_rule(32).unwrap();
        for (a,b) in base.angular_cells.iter().zip(q) {assert_eq!(a.mu.to_bits(),b.mu.to_bits());assert_eq!(a.count_fraction.to_bits(),b.count_fraction.to_bits());}
    }
    #[test] fn new_rules_are_positive_mirrored_and_native_indexed() {
        let base=AxbiSource::new(NH0,0.2,8,32).unwrap();
        for n in [64,128,256] {
            let source=refined_source(&base,n,Declaration::locally_isotropic_non_tilted()).unwrap();source_unchanged(&base,&source).unwrap();
            for j in 0..n {assert!(source.angular_cells[j].count_fraction>0.0);assert_eq!(source.angular_cells[j].mu,-source.angular_cells[n-1-j].mu);}
            let t=CovariantTransport::new(&source,GeometrySnapshot::new([AREF;3],[H;3]).unwrap(),24,0.01,5000.0).unwrap();
            let mut state=t.empty_state();t.add_delta(&mut state,n-1,10.0,1.0).unwrap();assert_eq!(t.cell_count(),24*n);assert_eq!(t.inventory(&state,&geometry(0.0,0.0,0.2).unwrap()).unwrap().0,1.0);
        }
    }
    #[test] fn spectral_mutation_and_anisotropic_declaration_are_rejected() {
        let base=AxbiSource::new(NH0,0.2,8,32).unwrap();let mut wrong=base.clone();wrong.spectral_cells[0].energy_ev+=1e-6;
        assert_eq!(source_unchanged(&base,&wrong).unwrap_err(),"SPECTRAL_OWNER_MUTATION");
        assert!(refined_source(&base,64,Declaration{kind:EmissionKind::PhysicallyAnisotropic,frame:EmissionFrame::NonTiltedLocalOrthonormal}).is_err());
        assert!(refined_source(&base,32,Declaration::locally_isotropic_non_tilted()).is_err());
    }
    #[test] fn one_new_birth_uses_margin_and_preserves_old_native_block() {
        let base=AxbiSource::new(NH0,0.2,8,32).unwrap();let source=refined_source(&base,64,Declaration::locally_isotropic_non_tilted()).unwrap();
        let reference=GeometrySnapshot::new([AREF;3],[H;3]).unwrap();
        let old_t=CovariantTransport::new(&base,reference.clone(),24,0.01,5000.0).unwrap();let old=old_stock(&old_t,32).unwrap();let old_bits=state_bits(&old);
        let t=CovariantTransport::new(&source,reference,24,0.01,5000.0).unwrap();let g=geometry(0.1,0.4,0.2).unwrap();
        let w=weights(&t,&g,"P2P4").unwrap();let mut birth=t.empty_state();inject(&t,&mut birth,&g,18.0,1e12,"P2P4",&w).unwrap();
        assert!(t.inventory(&birth,&g).unwrap().0>0.0);assert_eq!(old_bits,state_bits(&old));
        let mu:Vec<_>=t.ray_geometry(&g).unwrap().iter().map(|r|r.mu).collect();assert!(sum(mu.iter().zip(&w).map(|(m,a)|a*p2(*m))).abs()<=INNER_TOL);
    }
    #[test] fn exact_bit_digest_detects_signed_zero_and_old_cell_mutation() {
        let source=AxbiSource::new(NH0,0.2,8,32).unwrap();let t=CovariantTransport::new(&source,GeometrySnapshot::new([AREF;3],[H;3]).unwrap(),24,0.01,5000.0).unwrap();
        let a=t.empty_state();let mut b=a.clone();b.number[0]=-0.0;assert_ne!(state_bits(&a),state_bits(&b));assert_ne!(bit_digest(state_bits(&a).into_iter()),bit_digest(state_bits(&b).into_iter()));
    }
    #[test] fn malformed_or_legacy_science_case_is_rejected() {
        assert!(Case::parse("x,32,0.6,P2P4").is_err());assert!(Case::parse("x,64,0.0,P2P4").is_err());assert!(Case::parse("x,64,NaN,P2").is_err());
    }
}

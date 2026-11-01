//! Prospective S0 paired Bianchi/FLRW history component.  All populations are
//! counts per hydrogen nucleus on fixed physical-energy nodes and fixed q rays.
use crate::*;
use crate::coupled_primary::{primary_stage_root, primary_stage_step_conservative, PrimaryBox, PrimaryPacket, PrimaryStage, PrimaryState};
use std::fmt::Write;

const CHI: [f64;3] = [13.598_434_599_702,24.587_389_011,54.417_76];
const SOURCE: f64 = 5e-15;
const BIRTH: f64 = 13.7;
const FHE: f64 = 0.083;
fn fail(s:&'static str)->ForwardError { ForwardError::InvalidInput(s) }
fn ie(_:impl std::fmt::Debug)->ForwardError { fail("PAIRED_INTERVAL_DOMAIN") }
fn p(x:f64)->Result<Interval,ForwardError>{Interval::point(x).map_err(ie)}
fn add(a:Interval,b:Interval)->Result<Interval,ForwardError>{a.add(&b).map_err(ie)}
fn sub(a:Interval,b:Interval)->Result<Interval,ForwardError>{a.sub(&b).map_err(ie)}
fn mul(a:Interval,b:Interval)->Result<Interval,ForwardError>{a.mul(&b).map_err(ie)}
fn div(a:Interval,b:Interval)->Result<Interval,ForwardError>{a.div(&b).map_err(ie)}
fn nonneg(b:Interval)->Result<Interval,ForwardError>{Interval::new(b.lo.max(0.0),b.hi.max(0.0)).map_err(ie)}
fn add_nonneg(a:Interval,b:Interval)->Result<Interval,ForwardError>{
    if a.hi==0.0 {return Ok(b)}
    if b.hi==0.0 {return Ok(a)}
    nonneg(add(a,b)?)
}
fn contains(b:Interval,x:f64)->bool{b.lo<=x && x<=b.hi}
fn widened(b:Interval,x:f64)->Result<Interval,ForwardError>{Interval::new(b.lo.min(x),b.hi.max(x)).map_err(ie)}

#[derive(Clone,Debug)]
pub struct PairedConfig {pub spectral_subdivisions:usize,pub n_mu:usize,pub n_phi:usize}
#[derive(Clone,Debug)]
pub struct PairedState {
    pub time_s:f64,pub gas:PrimaryState,pub gas_box:[Interval;4],
    pub photons:Vec<f64>,pub photon_boxes:Vec<Interval>,
    pub lower_guard_n:Vec<f64>,pub lower_guard_u:Vec<f64>,
    pub lower_guard_n_box:Vec<Interval>,pub lower_guard_u_box:Vec<Interval>,
    pub redshift_work_ev_per_h:f64,pub thermal_work_ev_per_h:f64,
    pub source_photons_per_h:f64,pub source_energy_ev_per_h:f64,
    pub absorbed_photons_per_h:f64,
    pub ledger_comp:[f64;5],
    pub energy_comp:f64,
}
#[derive(Clone,Debug)]
pub struct PairedTrial {pub state:PairedState,pub local_bound:f64,pub public_width:f64,pub max_ledger:f64,pub audits:Vec<String>}

pub fn energy_nodes(c:&PairedConfig)->Result<Vec<f64>,ForwardError>{
    if c.spectral_subdivisions==0 || c.spectral_subdivisions>1024 || c.n_mu==0 || c.n_phi==0 || c.n_mu>64 || c.n_phi>128 {
        return Err(fail("PAIRED_GRID_DOMAIN"));
    }
    let m=c.spectral_subdivisions;
    let mut v=Vec::with_capacity(4*m+1);
    let edges=[10.0,CHI[0],13.6,BIRTH,20.0];
    for k in 0..4 {for j in 0..m {v.push(edges[k]+(edges[k+1]-edges[k])*(j as f64)/(m as f64));}}
    v.push(20.0);
    if v.windows(2).any(|x|x[0]>=x[1]) {return Err(fail("PAIRED_GRID_RANGE"));}
    Ok(v)
}
pub fn qhat(c:&PairedConfig,d:usize)->[f64;3]{
    let imu=d/c.n_phi;let iphi=d%c.n_phi;
    let mu=-1.0+2.0*((imu as f64)+0.5)/(c.n_mu as f64);
    let phi=2.0*std::f64::consts::PI*((iphi as f64)+0.5)/(c.n_phi as f64);
    let r=(1.0-mu*mu).sqrt();let q=[r*phi.cos(),r*phi.sin(),mu];
    let norm=q[0].hypot(q[1]).hypot(q[2]);q.map(|x|x/norm)
}
fn directions(c:&PairedConfig)->Result<usize,ForwardError>{c.n_mu.checked_mul(c.n_phi).ok_or(fail("PAIRED_GRID_RANGE"))}
fn gas4(s:&PrimaryState)->[f64;4]{[s.fractions[0],s.fractions[1],s.fractions[2],s.w_ev_per_h]}
fn temp_box(g:[Interval;4])->Result<Interval,ForwardError>{
    // Enclose the binary stage nHe/nH, including its multiplication/division
    // rounding, and keep each thermal constant product in interval arithmetic.
    let f=Interval::new(FHE*(1.0-8.0*f64::EPSILON),FHE*(1.0+8.0*f64::EPSILON)).map_err(ie)?;
    let ne=add(g[0],mul(f,add(g[1],mul(p(2.0)?,g[2])?)?)?)?;
    let particles=add(add(p(1.0)?,f)?,ne)?;
    let numerator=mul(mul(p(2.0)?,g[3])?,p(1.602176634e-12)?)?;
    let denominator=mul(mul(p(3.0)?,p(1.380649e-16)?)?,particles)?;
    div(numerator,denominator)
}
fn guard_temperature(g:[Interval;4])->Result<(),ForwardError>{
    let t=temp_box(g)?;
    if t.lo<35_000.0 || t.hi>60_000.0 || t.lo<30_000.0 || t.hi>110_000.0 {Err(fail("PAIRED_TEMPERATURE_GUARD"))} else {Ok(())}
}
fn initial_w()->f64{let x=[0.9,0.3,0.6];let particles=1.0+FHE+x[0]+FHE*(x[1]+2.0*x[2]);1.5*1.380649e-16*50_000.0*particles/1.602176634e-12}
pub fn paired_initial(c:&PairedConfig)->Result<PairedState,ForwardError>{
    let nodes=energy_nodes(c)?;let nd=directions(c)?;
    let mut photons=vec![0.0;nd*nodes.len()];
    for d in 0..nd {photons[d*nodes.len()+3*c.spectral_subdivisions]=0.05/(nd as f64);}
    let photon_boxes=photons.iter().copied().map(p).collect::<Result<Vec<_>,_>>()?;
    let gas=PrimaryState{fractions:[0.9,0.3,0.6],w_ev_per_h:initial_w(),escape_ev_per_h:0.0,
        packets:vec![PrimaryPacket{energy_ev:BIRTH,per_h:0.05}]};
    let g=gas4(&gas);let gas_box=[p(g[0])?,p(g[1])?,p(g[2])?,p(g[3])?];
    guard_temperature(gas_box)?;
    Ok(PairedState{time_s:0.0,gas,gas_box,photons,photon_boxes,
        lower_guard_n:vec![0.0;nd],lower_guard_u:vec![0.0;nd],
        lower_guard_n_box:vec![p(0.0)?;nd],lower_guard_u_box:vec![p(0.0)?;nd],
        redshift_work_ev_per_h:0.0,thermal_work_ev_per_h:0.0,source_photons_per_h:0.0,
        source_energy_ev_per_h:0.0,absorbed_photons_per_h:0.0,ledger_comp:[0.0;5],energy_comp:0.0})
}
fn validate(c:&PairedConfig,s:&PairedState,nodes:&[f64])->Result<(),ForwardError>{
    let n=directions(c)?.checked_mul(nodes.len()).ok_or(fail("PAIRED_GRID_RANGE"))?;
    if s.photons.len()!=n || s.photon_boxes.len()!=n || !s.time_s.is_finite() || s.time_s<0.0 || s.time_s>1e13 {return Err(fail("PAIRED_STATE_DOMAIN"));}
    if s.ledger_comp.iter().any(|x|!x.is_finite()) || [s.redshift_work_ev_per_h,s.thermal_work_ev_per_h,s.source_photons_per_h,s.source_energy_ev_per_h,s.absorbed_photons_per_h].iter().any(|x|!x.is_finite() || *x<0.0){return Err(fail("PAIRED_LEDGER_STATE"));}
    let nd=directions(c)?;
    if s.lower_guard_n.len()!=nd || s.lower_guard_u.len()!=nd || s.lower_guard_n_box.len()!=nd || s.lower_guard_u_box.len()!=nd{return Err(fail("PAIRED_GUARD_LENGTH"));}
    for d in 0..nd {let gn=s.lower_guard_n[d];let gu=s.lower_guard_u[d];let nb=s.lower_guard_n_box[d];let ub=s.lower_guard_u_box[d];
        if !gn.is_finite() || !gu.is_finite() || gn<0.0 || gu<0.0 || nb.lo<0.0 || ub.lo<0.0 || !contains(nb,gn) || !contains(ub,gu) || (gn==0.0 && gu!=0.0) || (gn>0.0 && gu>=10.0*gn){return Err(fail("PAIRED_GUARD_DOMAIN"));}}
    let g=gas4(&s.gas);
    for j in 0..4 {if !g[j].is_finite() || !contains(s.gas_box[j],g[j]){return Err(fail("PAIRED_GAS_BOX"));}}
    for (x,b) in s.photons.iter().zip(&s.photon_boxes){if !x.is_finite() || *x<0.0 || !b.lo.is_finite() || !b.hi.is_finite() || b.lo<0.0 || !contains(*b,*x){return Err(fail("PAIRED_PHOTON_BOX"));}}
    guard_temperature(s.gas_box)?;
    Ok(())
}
fn g_point(q:[f64;3],h:[f64;3],t:f64)->f64{
    let z=(0..3).map(|i|q[i]*q[i]*(-2.0*h[i]*t).exp()).sum::<f64>();z.sqrt()
}
fn g_box(q:[f64;3],h:[f64;3],t:f64)->Result<Interval,ForwardError>{
    let mut z=p(0.0)?;
    for i in 0..3 {let exponent=mul(p(-2.0)?,mul(p(h[i])?,p(t)?)?)?;
        let e=exponent.exp().map_err(ie)?;z=add(z,mul(mul(p(q[i])?,p(q[i])?)?,e)?)?;}
    z.powf(0.5).map_err(ie)
}
fn source_weights(c:&PairedConfig,h:[f64;3],t:f64)->Result<(Vec<f64>,Vec<Interval>),ForwardError>{
    let nd=directions(c)?;let volume=(-(h[0]+h[1]+h[2])*t).exp();
    let sumh=add(add(p(h[0])?,p(h[1])?)?,p(h[2])?)?;
    let volume_box=mul(p(-1.0)?,mul(sumh,p(t)?)?)?.exp().map_err(ie)?;
    let mut raw=Vec::with_capacity(nd);let mut boxes=Vec::with_capacity(nd);
    for d in 0..nd {let q=qhat(c,d);let g=g_point(q,h,t);let gb=g_box(q,h,t)?;
        let j=volume/(g*g*g);let jb=div(volume_box,gb.powf(3.0).map_err(ie)?)?;
        raw.push(j);boxes.push(widened(jb,j)?);
    }
    let total: f64=raw.iter().sum();if !total.is_finite() || total<=0.0{return Err(fail("PAIRED_SOURCE_RANGE"));}
    let mut tb=p(0.0)?;for b in &boxes {tb=add(tb,*b)?;}
    let mut weights=Vec::with_capacity(nd);let mut wb=Vec::with_capacity(nd);
    for d in 0..nd {let a=raw[d]/total;weights.push(a);wb.push(nonneg(widened(div(boxes[d],tb)?,a)?)?);}
    Ok((weights,wb))
}
fn hat(x:f64,nodes:&[f64],j:usize)->f64{
    if j==0 {if x<=nodes[0] {1.0} else if x>=nodes[1] {0.0} else {(nodes[1]-x)/(nodes[1]-nodes[0])}}
    else if j+1==nodes.len(){if x>=nodes[j] {1.0} else if x<=nodes[j-1]{0.0}else{(x-nodes[j-1])/(nodes[j]-nodes[j-1])}}
    else if x<=nodes[j-1] || x>=nodes[j+1]{0.0}
    else if x<=nodes[j]{(x-nodes[j-1])/(nodes[j]-nodes[j-1])}
    else {(nodes[j+1]-x)/(nodes[j+1]-nodes[j])}
}
fn hat_at(x:f64,nodes:&[f64],j:usize)->Result<Interval,ForwardError>{
    if j==0 {if x<=nodes[0]{return p(1.0)}if x>=nodes[1]{return p(0.0)}
        return div(sub(p(nodes[1])?,p(x)?)?,sub(p(nodes[1])?,p(nodes[0])?)?);}
    if j+1==nodes.len(){if x<=nodes[j-1]{return p(0.0)}if x>=nodes[j]{return p(1.0)}
        return div(sub(p(x)?,p(nodes[j-1])?)?,sub(p(nodes[j])?,p(nodes[j-1])?)?);}
    if x<=nodes[j-1] || x>=nodes[j+1]{return p(0.0)}
    if x==nodes[j]{return p(1.0)}
    if x<nodes[j]{div(sub(p(x)?,p(nodes[j-1])?)?,sub(p(nodes[j])?,p(nodes[j-1])?)?)}
    else {div(sub(p(nodes[j+1])?,p(x)?)?,sub(p(nodes[j+1])?,p(nodes[j])?)?)}
}
fn hat_box(x:Interval,nodes:&[f64],j:usize)->Result<Interval,ForwardError>{
    let support_lo=if j==0 {f64::NEG_INFINITY} else {nodes[j-1]};
    let support_hi=if j+1==nodes.len(){f64::INFINITY}else{nodes[j+1]};
    if x.hi<support_lo || x.lo>support_hi {return p(0.0);}
    let a=hat_at(x.lo,nodes,j)?;let b=hat_at(x.hi,nodes,j)?;
    let mut lo=a.lo.min(b.lo);let mut hi=a.hi.max(b.hi);
    if x.lo<=nodes[j] && nodes[j]<=x.hi {hi=1.0;}
    if j>0 && x.lo<=nodes[j-1] && nodes[j-1]<=x.hi {lo=0.0;}
    if j+1<nodes.len() && x.lo<=nodes[j+1] && nodes[j+1]<=x.hi {lo=0.0;}
    Interval::new(lo.max(0.0),hi.min(1.0)).map_err(ie)
}
fn weighted_sum(values:&[f64])->f64{let mut sum=0.0;let mut correction=0.0;for &x in values {let y=x-correction;let t=sum+y;correction=(t-sum)-y;sum=t;}sum}
fn accumulate(sum:f64,correction:f64,x:f64)->(f64,f64){let y=x-correction;let t=sum+y;(t,(t-sum)-y)}
fn photon_energy(s:&PairedState,nodes:&[f64])->f64{weighted_sum(&s.photons.iter().enumerate().map(|(i,x)|x*nodes[i%nodes.len()]).chain(s.lower_guard_u.iter().copied()).collect::<Vec<_>>())}
fn photon_number(s:&PairedState)->f64{weighted_sum(&s.photons.iter().copied().chain(s.lower_guard_n.iter().copied()).collect::<Vec<_>>())}
fn matter_energy(g:&PrimaryState)->f64{g.w_ev_per_h+CHI[0]*g.fractions[0]+FHE*(CHI[1]*g.fractions[1]+(CHI[1]+CHI[2])*g.fractions[2])+g.escape_ev_per_h}
fn site_audit(stage:&PrimaryStage,t:f64,dt:f64,nodes:&[f64],index:&[usize],old:&PrimaryState,parent:&PrimaryBox,root:&crate::coupled_primary::PrimaryRoot,point:&crate::coupled_primary::PrimaryStep,transport_n:f64,transport_u:f64,source_n:f64,source_u:f64)->Result<String,ForwardError>{
    let provider=AtomicProvider::reference();let mut sigma=Vec::new();
    for &k in index {sigma.push([provider.cross_section(Absorber::HI,nodes[k])?,provider.cross_section(Absorber::HeI,nodes[k])?,provider.cross_section(Absorber::HeII,nodes[k])?]);}
    let fi=|x:f64| format!("{:.17e}",x);
    let ar=|a:&[f64]|->String {format!("[{}]",a.iter().map(|x|fi(*x)).collect::<Vec<_>>().join(","))};
    let ib=|a:&[Interval]|->String {format!("[{}]",a.iter().map(|x|ar(&[x.lo,x.hi])).collect::<Vec<_>>().join(","))};
    let mut out=String::new();
    write!(out,"{{\"time_s\":{},\"dt_s\":{},\"n_h_cm3\":{},\"f_he\":{},\"h_mean_per_s\":{},\"energies_ev\":{},\"group_indices\":{},\"sigma_cm2\":[{}],\"old_gas\":{},\"parent_gas\":{},\"parent_photons\":{},\"centre\":{},\"out_gas\":{},\"out_photons\":{},\"preconditioner\":[{}],\"q\":{},\"point_gas\":{},\"point_photons\":{},\"photo_events\":[{}],\"thermal_work\":{},\"transport_n\":{},\"transport_u\":{},\"source_n\":{},\"source_u\":{}}}",
        fi(t),fi(dt),fi(stage.n_h_cm3),fi(stage.f_he),fi(stage.h_mean_per_s),ar(&index.iter().map(|&k|nodes[k]).collect::<Vec<_>>()),format!("[{}]",index.iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",")),sigma.iter().map(|s|ar(s)).collect::<Vec<_>>().join(","),ar(&gas4(old)),ib(&parent.gas),ib(&parent.photons),ar(&root.centre),ib(&root.gas),ib(&root.photons),root.preconditioner.iter().map(|r|ar(r)).collect::<Vec<_>>().join(","),fi(root.q),ar(&gas4(&point.state)),ar(&point.state.packets.iter().map(|p|p.per_h).collect::<Vec<_>>()),point.events.photo_per_h.iter().map(|e|ar(e)).collect::<Vec<_>>().join(","),fi(point.events.thermal_work_ev_per_h),fi(transport_n),fi(transport_u),fi(source_n),fi(source_u)).map_err(|_|fail("PAIRED_AUDIT_WRITE"))?;
    out.pop();
    let factors=old.packets.iter().zip(&point.state.packets).map(|(a,b)|if a.per_h==0.0{1.0}else{b.per_h/a.per_h}).collect::<Vec<_>>();
    let bits=sigma.iter().map(|s|format!("[{}]",s.iter().map(|x|format!("\"{:016x}\"",x.to_bits())).collect::<Vec<_>>().join(","))).collect::<Vec<_>>().join(",");
    write!(out,",\"sigma_bits\":[{}],\"point_factors\":{},\"point_escape_ev_per_h\":{},\"collision_events\":{},\"recombination_events\":{},\"dr_events\":{},\"point_residual\":{}}}",bits,ar(&factors),fi(point.state.escape_ev_per_h),ar(&point.events.collision_per_h),ar(&point.events.recombination_per_h),ar(&point.events.dr_per_h),fi(point.residual)).map_err(|_|fail("PAIRED_AUDIT_WRITE"))?;
    Ok(out)
}
fn endpoint(c:&PairedConfig,h:[f64;3],s:&PairedState,dt:f64,nodes:&[f64])->Result<(PairedState,String,f64),ForwardError>{
    let n=nodes.len();let nd=directions(c)?;let t1=s.time_s+dt;
    let background=ConstantHubbleBackground::new([1.0;3],h)?;
    let snapshot0=background.snapshot(s.time_s)?;let snapshot1=background.snapshot(t1)?;
    let mut transported=vec![0.0;nd*n];let mut tb=vec![p(0.0)?;nd*n];
    let mut guard_n=s.lower_guard_n.clone();let mut guard_u=vec![0.0;nd];
    let mut guard_nb=s.lower_guard_n_box.clone();let mut guard_ub=vec![p(0.0)?;nd];
    for d in 0..nd {let q=qhat(c,d);let r=g_point(q,h,t1)/g_point(q,h,s.time_s);
        let e0=[q[0]*(-h[0]*s.time_s).exp(),q[1]*(-h[1]*s.time_s).exp(),q[2]*(-h[2]*s.time_s).exp()];
        let e0norm=e0[0].hypot(e0[1]).hypot(e0[2]);
        let ray=CharacteristicRay::new(BIRTH,e0.map(|x|x/e0norm),0.0)?;
        let pulled=ray.pullback(&snapshot0,&snapshot1)?;
        if (pulled.energy_ev/BIRTH-r).abs()>1e-12 {return Err(fail("PAIRED_CHARACTERISTIC_PARITY"));}
        let rb=div(g_box(q,h,t1)?,g_box(q,h,s.time_s)?)?;
        if !r.is_finite() || r<=0.0 || !contains(rb,r){return Err(fail("PAIRED_REDSHIFT_RANGE"));}
        guard_u[d]=s.lower_guard_u[d]*r;
        guard_ub[d]=nonneg(widened(mul(s.lower_guard_u_box[d],rb)?,guard_u[d])?)?;
        for j in 0..n {let old=s.photons[d*n+j];let ob=s.photon_boxes[d*n+j];if old==0.0 && ob.hi==0.0{continue;}
            let e=nodes[j]*r;let eb=mul(p(nodes[j])?,rb)?;
            if e>20.0 || eb.hi>20.0{return Err(fail("PAIRED_UPPER_GUARD_UNIMPLEMENTED"));}
            if eb.lo<10.0 {
                let exported=if e<10.0 {old}else{0.0};
                let possible=if eb.hi<10.0 {ob}else{Interval::new(0.0,ob.hi).map_err(ie)?};
                guard_n[d]+=exported;guard_u[d]+=exported*e;
                guard_nb[d]=add_nonneg(guard_nb[d],possible)?;
                guard_ub[d]=add_nonneg(guard_ub[d],nonneg(mul(possible,eb)?)?)?;
            }
            if e<10.0 && eb.hi<10.0 {continue;}
            for k in 0..n {let a=if e<10.0 {0.0}else{hat(e,nodes,k)};let mut ab=hat_box(eb,nodes,k)?;
                if eb.lo<10.0 {ab=Interval::new(0.0,ab.hi).map_err(ie)?;}
                if a==0.0 && ab.hi==0.0{continue;}
                transported[d*n+k]+=old*a;
                tb[d*n+k]=add_nonneg(tb[d*n+k],nonneg(mul(ob,ab)?)?)?;
            }
        }
        guard_nb[d]=nonneg(widened(guard_nb[d],guard_n[d])?)?;
        guard_ub[d]=nonneg(widened(guard_ub[d],guard_u[d])?)?;
    }
    for i in 0..transported.len(){tb[i]=nonneg(widened(tb[i],transported[i])?)?;}
    let old_u=photon_energy(s,nodes);let transport_u=weighted_sum(&transported.iter().enumerate().map(|(i,x)|x*nodes[i%n]).chain(guard_u.iter().copied()).collect::<Vec<_>>());
    let old_n=photon_number(s);let transport_n=weighted_sum(&transported.iter().copied().chain(guard_n.iter().copied()).collect::<Vec<_>>());
    let redshift_loss=old_u-transport_u;
    if redshift_loss < -1e-12 || !redshift_loss.is_finite(){return Err(fail("PAIRED_REDSHIFT_LEDGER"));}
    let (weights,wb)=source_weights(c,h,t1)?;let source_n=dt*SOURCE;let source_u=source_n*BIRTH;let birth_index=3*c.spectral_subdivisions;
    for d in 0..nd {let i=d*n+birth_index;let z=source_n*weights[d];transported[i]+=z;tb[i]=nonneg(widened(add_nonneg(tb[i],mul(p(source_n)?,wb[d])?)?,transported[i])?)?;}
    let mut groups=vec![0.0;n];let mut gc=vec![0.0;n];let mut gb=vec![p(0.0)?;n];
    for d in 0..nd {for k in 0..n {let z=accumulate(groups[k],gc[k],transported[d*n+k]);groups[k]=z.0;gc[k]=z.1;gb[k]=add_nonneg(gb[k],tb[d*n+k])?;}}
    for k in 0..n {gb[k]=nonneg(widened(gb[k],groups[k])?)?;}
    let index:Vec<usize>=(0..n).filter(|&k|groups[k]>0.0 || gb[k].hi>0.0).collect();
    let packets=index.iter().map(|&k|PrimaryPacket{energy_ev:nodes[k],per_h:groups[k]}).collect::<Vec<_>>();
    let old=PrimaryState{fractions:s.gas.fractions,w_ev_per_h:s.gas.w_ev_per_h,escape_ev_per_h:s.gas.escape_ev_per_h,packets};
    let stage=PrimaryStage{n_h_cm3:1e-4*(-h.iter().sum::<f64>()*t1).exp(),f_he:FHE,h_mean_per_s:h.iter().sum::<f64>()/3.0};
    let parent=PrimaryBox{gas:s.gas_box,photons:index.iter().map(|&k|gb[k]).collect()};
    let control=StepControl{max_iterations:200,residual_tolerance:1e-15};
    let (point,energy_comp)=primary_stage_step_conservative(&stage,&old,dt,control,s.energy_comp)?;
    let root=primary_stage_root(&stage,&old,&parent,dt,control)?;
    guard_temperature(root.gas)?;
    let provider=AtomicProvider::reference();let mut out=vec![0.0;nd*n];let mut outb=vec![p(0.0)?;nd*n];
    for (slot,&k) in index.iter().enumerate(){
        let sig=[provider.cross_section(Absorber::HI,nodes[k])?,provider.cross_section(Absorber::HeI,nodes[k])?,provider.cross_section(Absorber::HeII,nodes[k])?];
        let lower=[sub(p(1.0)?,root.gas[0])?,mul(p(FHE)?,sub(sub(p(1.0)?,root.gas[1])?,root.gas[2])?)?,mul(p(FHE)?,root.gas[1])?];
        let mut opacity=p(0.0)?;for a in 0..3 {opacity=add(opacity,mul(lower[a],p(sig[a])?)?)?;}
        let factor=div(p(1.0)?,add(p(1.0)?,mul(p(dt*29979245800.0*stage.n_h_cm3)?,opacity)?)?)?;
        let actual=if groups[k]==0.0 {1.0} else {point.state.packets[slot].per_h/groups[k]};
        for d in 0..nd {let i=d*n+k;out[i]=transported[i]*actual;outb[i]=nonneg(widened(mul(tb[i],factor)?,out[i])?)?;}
    }
    let mut gas=point.state.clone();gas.packets=index.iter().enumerate().map(|(j,&k)|PrimaryPacket{energy_ev:nodes[k],per_h:point.state.packets[j].per_h}).collect();
    let absorbed=weighted_sum(&point.events.photo_per_h.iter().flat_map(|a|a.iter()).copied().collect::<Vec<_>>());
    let thermal=point.events.thermal_work_ev_per_h;
    let increments=[redshift_loss,thermal,source_n,source_u,absorbed];
    let previous=[s.redshift_work_ev_per_h,s.thermal_work_ev_per_h,s.source_photons_per_h,s.source_energy_ev_per_h,s.absorbed_photons_per_h];
    let updated:[(f64,f64);5]=std::array::from_fn(|i|accumulate(previous[i],s.ledger_comp[i],increments[i]));
    let next=PairedState{time_s:t1,gas,gas_box:root.gas,photons:out,photon_boxes:outb,
        lower_guard_n:guard_n,lower_guard_u:guard_u,lower_guard_n_box:guard_nb,lower_guard_u_box:guard_ub,
        redshift_work_ev_per_h:updated[0].0,thermal_work_ev_per_h:updated[1].0,
        source_photons_per_h:updated[2].0,source_energy_ev_per_h:updated[3].0,
        absorbed_photons_per_h:updated[4].0,ledger_comp:updated.map(|v|v.1),energy_comp};
    let nn=photon_number(&next);let uu=photon_energy(&next,nodes);
    let number_res=(transport_n+source_n-nn-absorbed).abs()/(old_n+source_n).max(0.05);
    let stage_input= matter_energy(&old)+transport_u+source_u;
    let stage_output=matter_energy(&next.gas)+uu+thermal;
    let energy_res=(stage_output-stage_input).abs()/(matter_energy(&old)+old_u+source_u).max(0.05*BIRTH);
    let transport_res=(transport_n-old_n).abs()/(old_n+source_n).max(0.05);
    // Prefix cumulative diagnostics do not gate individual steps.
    let max_ledger=number_res.max(energy_res).max(transport_res);
    if max_ledger>1e-12{return Err(fail("PAIRED_LEDGER_GATE"));}
    let audit=site_audit(&stage,t1,dt,nodes,&index,&old,&parent,&root,&point,transport_n,transport_u,source_n,source_u)?;
    Ok((next,audit,max_ledger))
}
fn difference(a:&PairedState,b:&PairedState,nodes:&[f64])->Result<f64,ForwardError>{
    let mut m=0.0_f64;
    for i in 0..3 {let d=sub(a.gas_box[i],b.gas_box[i])?;m=m.max(d.lo.abs().max(d.hi.abs()));}
    let ta=temp_box(a.gas_box)?.ln().map_err(ie)?;let tb=temp_box(b.gas_box)?.ln().map_err(ie)?;
    let d=sub(ta,tb)?;m=m.max(d.lo.abs().max(d.hi.abs()));
    let d=sub(a.gas_box[3],b.gas_box[3])?;m=m.max(d.lo.abs().max(d.hi.abs())/initial_w());
    let mut an=p(0.0)?;let mut bn=p(0.0)?;let mut au=p(0.0)?;let mut bu=p(0.0)?;
    for k in 0..nodes.len(){let mut ag=p(0.0)?;let mut bg=p(0.0)?;
        for dir in 0..a.photons.len()/nodes.len(){ag=add(ag,a.photon_boxes[dir*nodes.len()+k])?;bg=add(bg,b.photon_boxes[dir*nodes.len()+k])?;}
        let z=sub(ag,bg)?;m=m.max(z.lo.abs().max(z.hi.abs())/0.05);
        an=add(an,ag)?;bn=add(bn,bg)?;au=add(au,mul(ag,p(nodes[k])?)?)?;bu=add(bu,mul(bg,p(nodes[k])?)?)?;
    }
    for d in 0..a.lower_guard_n.len(){
        let zn=sub(a.lower_guard_n_box[d],b.lower_guard_n_box[d])?;
        let zu=sub(a.lower_guard_u_box[d],b.lower_guard_u_box[d])?;
        m=m.max(zn.lo.abs().max(zn.hi.abs())/0.05).max(zu.lo.abs().max(zu.hi.abs())/(0.05*BIRTH));
        an=add(an,a.lower_guard_n_box[d])?;bn=add(bn,b.lower_guard_n_box[d])?;
        au=add(au,a.lower_guard_u_box[d])?;bu=add(bu,b.lower_guard_u_box[d])?;
    }
    for (x,y,norm) in [(an,bn,0.05),(au,bu,0.05*BIRTH)] {let z=sub(x,y)?;m=m.max(z.lo.abs().max(z.hi.abs())/norm);}
    Ok(m)
}
fn width(s:&PairedState,nodes:&[f64])->Result<f64,ForwardError>{
    let mut m=0.0_f64;
    for j in 0..3 {m=m.max(s.gas_box[j].hi-s.gas_box[j].lo);}
    let t=temp_box(s.gas_box)?.ln().map_err(ie)?;m=m.max(t.hi-t.lo);
    m=m.max((s.gas_box[3].hi-s.gas_box[3].lo)/initial_w());
    let mut n=p(0.0)?;let mut u=p(0.0)?;
    for k in 0..nodes.len(){let mut g=p(0.0)?;for d in 0..s.photons.len()/nodes.len(){g=add(g,s.photon_boxes[d*nodes.len()+k])?;}
        m=m.max((g.hi-g.lo)/0.05);n=add(n,g)?;u=add(u,mul(g,p(nodes[k])?)?)?;
    }
    for d in 0..s.lower_guard_n.len(){let gn=s.lower_guard_n_box[d];let gu=s.lower_guard_u_box[d];
        m=m.max((gn.hi-gn.lo)/0.05).max((gu.hi-gu.lo)/(0.05*BIRTH));
        n=add(n,gn)?;u=add(u,gu)?;
    }
    m=m.max((n.hi-n.lo)/0.05).max((u.hi-u.lo)/(0.05*BIRTH));Ok(m)
}
pub fn paired_trial(c:&PairedConfig,h:[f64;3],s:&PairedState,dt:f64)->Result<PairedTrial,ForwardError>{
    let nodes=energy_nodes(c)?;validate(c,s,&nodes)?;
    if h.iter().any(|x|!x.is_finite() || *x<0.0) || !dt.is_finite() || dt<1000.0 || s.time_s+dt>1e13 {return Err(fail("PAIRED_TRIAL_DOMAIN"));}
    let (full,a1,l1)=endpoint(c,h,s,dt,&nodes)?;
    let (half,a2,l2)=endpoint(c,h,s,dt/2.0,&nodes)?;
    let (two,a3,l3)=endpoint(c,h,&half,dt/2.0,&nodes)?;
    let local=difference(&full,&two,&nodes)?;let public=width(&two,&nodes)?;let ledger=l1.max(l2).max(l3);
    if local>=2e-4 {return Err(fail("PAIRED_LOCAL_GATE"));}
    if public>=2e-3 {return Err(fail("PAIRED_WIDTH_GATE"));}
    if ledger>1e-12 {return Err(fail("PAIRED_LEDGER_GATE"));}
    Ok(PairedTrial{state:two,local_bound:local,public_width:public,max_ledger:ledger,audits:vec![a1,a2,a3]})
}

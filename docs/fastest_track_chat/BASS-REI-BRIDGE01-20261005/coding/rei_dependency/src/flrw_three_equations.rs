//! Additive source-bound FLRW point diagnostics, not a cosmological solver.
//! Atomic densities are proper cm^-3. Comoving counts in this module are a^3*n
//! per reference comoving cm^3, distinct from the legacy cMpc^-3 storage.
use crate::{Absorber, AtomicProvider, ForwardError, HHeModel, HHeState,
    PhotonNode, RawProcess, RecombinationCase, C_LIGHT, MPC_CM,
    hhe_rhs, homogeneous_photo_rates};

fn nn(x:f64)->Result<(),ForwardError>{
    if x.is_finite()&&x>=0.0 {Ok(())} else {Err(ForwardError::InvalidInput("FLRW_NONFINITE_OR_NEGATIVE"))}
}
fn positive(x:f64)->Result<(),ForwardError>{nn(x)?;if x>0.0{Ok(())}else{Err(ForwardError::InvalidInput("FLRW_NONPOSITIVE"))}}
fn finite(x:f64)->Result<f64,ForwardError>{if x.is_finite(){Ok(x)}else{Err(ForwardError::InvalidInput("FLRW_OVERFLOW"))}}
fn cube(a:f64)->Result<f64,ForwardError>{positive(a)?;let a3=finite(a*a*a)?;positive(a3)?;Ok(a3)}

#[derive(Debug,Clone,Copy)]
pub struct PhotonInput {
    pub scale_factor:f64,
    pub hubble_s:f64,
    pub comoving_photons_cm3:[f64;3],
    pub edge_energy_ev:[f64;4],
    /// Proper spectral number density per eV, evaluated at the FIXED edges.
    pub edge_n_per_cm3_ev:[f64;4],
    pub source_proper_cm3_s:[f64;3],
    pub absorption_proper_cm3_s:[f64;3],
}
#[derive(Debug,Clone,Copy)]
pub struct PhotonBalance {
    pub comoving_dot_cm3_s:[f64;3],
    pub proper_dot_cm3_s:[f64;3],
    pub edge_flux_comoving_cm3_s:[f64;4],
    /// Positive net exit; lower-edge loss minus upper-edge inflow.
    pub boundary_net_loss_comoving_cm3_s:f64,
    pub source_comoving_cm3_s:f64,
    pub absorption_comoving_cm3_s:f64,
    pub summed_balance_residual:f64,
}
/// Fixed-energy FV number balance. Downward FLRW edge flux is a^3*H*E*n_E.
/// Bin averages alone do not determine edge spectra: callers supply that closure.
pub fn photon_balance(input:PhotonInput)->Result<PhotonBalance,ForwardError>{
    let a3=cube(input.scale_factor)?;nn(input.hubble_s)?;
    for x in input.comoving_photons_cm3.into_iter().chain(input.edge_n_per_cm3_ev)
        .chain(input.source_proper_cm3_s).chain(input.absorption_proper_cm3_s){nn(x)?;}
    for i in 0..4 {positive(input.edge_energy_ev[i])?;
        if i>0&&input.edge_energy_ev[i]<=input.edge_energy_ev[i-1]{return Err(ForwardError::InvalidInput("FLRW_EDGES_NOT_INCREASING"));}}
    let mut flux=[0.0;4];let mut dc=[0.0;3];let mut dp=[0.0;3];
    for i in 0..4 {flux[i]=finite(a3*input.hubble_s*input.edge_energy_ev[i]*input.edge_n_per_cm3_ev[i])?;}
    for g in 0..3 {
        dc[g]=finite(a3*(input.source_proper_cm3_s[g]-input.absorption_proper_cm3_s[g])+flux[g+1]-flux[g])?;
        dp[g]=finite(dc[g]/a3-3.0*input.hubble_s*(input.comoving_photons_cm3[g]/a3))?;
    }
    let source=finite(a3*input.source_proper_cm3_s.iter().sum::<f64>())?;
    let absorption=finite(a3*input.absorption_proper_cm3_s.iter().sum::<f64>())?;
    let loss=finite(flux[0]-flux[3])?;
    let residual=finite(dc.iter().sum::<f64>()-(source-absorption-loss))?;
    Ok(PhotonBalance{comoving_dot_cm3_s:dc,proper_dot_cm3_s:dp,
        edge_flux_comoving_cm3_s:flux,boundary_net_loss_comoving_cm3_s:loss,
        source_comoving_cm3_s:source,absorption_comoving_cm3_s:absorption,
        summed_balance_residual:residual})
}

#[derive(Debug,Clone,Copy)]
pub struct CellInput {
    pub scale_factor:f64,pub hubble_s:f64,pub temperature_k:f64,
    pub n_h_proper_cm3:f64,pub x_hii:f64,
    pub case:RecombinationCase,pub include_collisions:bool,
    pub photon_energy_ev:[f64;3],pub photon_proper_cm3:[f64;3],
    pub source_proper_cm3_s:[f64;3],pub other_absorption_proper_cm3_s:[f64;3],
    pub edge_energy_ev:[f64;4],pub edge_n_per_cm3_ev:[f64;4],
}
#[derive(Debug,Clone,Copy)]
pub struct CellResult {
    pub n_h_proper_cm3:f64,pub x_hii:f64,pub photon_proper_cm3:f64,
    pub x_dot_s:f64,pub gamma_hi_s:f64,pub alpha_cm3_s:f64,pub ci_cm3_s:f64,
    pub sigma_hi_cm2:[f64;3],pub electron_proper_cm3:f64,
    pub photo_proper_cm3_s:f64,pub collision_proper_cm3_s:f64,pub recombination_proper_cm3_s:f64,
    pub other_absorption_proper_cm3_s:f64,
    pub photo_bridge_residual_proper_cm3_s:f64,
    pub photon:PhotonBalance,
    pub scale_factor:f64,pub hubble_s:f64,
}
/// Connect the actual public AtomicProvider -> HHeModel -> hhe_rhs paths and
/// compare its photo events against the actual homogeneous_photo_rates bridge.
/// Only the hydrogen number equation is admitted to this diagnostic. The source
/// case is explicit: A primary-only, or B with same-species local OTS recycling.
/// No tracked recombination-photon source is added in either profile.
pub fn connected_cell(input:CellInput)->Result<CellResult,ForwardError>{
    let a3=cube(input.scale_factor)?;nn(input.hubble_s)?;positive(input.n_h_proper_cm3)?;
    nn(input.x_hii)?;if input.x_hii>1.0{return Err(ForwardError::InvalidInput("FLRW_FRACTION_DOMAIN"));}
    let provider=AtomicProvider::reference();
    let alpha=provider.raw_coefficient(RawProcess::K2,input.temperature_k,input.case)?.value;
    let ci=if input.include_collisions{provider.raw_coefficient(RawProcess::K1,input.temperature_k,input.case)?.value}else{0.0};
    let mut model=HHeModel::controlled_fixture();
    model.n_h_cm3=input.n_h_proper_cm3;model.n_he_cm3=0.0;
    model.c_cm_s=C_LIGHT;model.photon_energy_ev=input.photon_energy_ev;
    model.alpha_cm3_s=[alpha,0.0,0.0];model.beta_cm3_s=[ci,0.0,0.0];
    model.sigma_cm2=[[0.0;3];3];
    for g in 0..3{model.sigma_cm2[0][g]=provider.cross_section(Absorber::HI,input.photon_energy_ev[g])?;}
    let state=HHeState{fractions:[input.x_hii,0.0,0.0],
        u_erg_cm3:finite(1.5*model.kb_erg_k*input.temperature_k*input.n_h_proper_cm3*(1.0+input.x_hii))?,
        photon_cm3:input.photon_proper_cm3,escaped_erg_cm3:0.0};
    let event=hhe_rhs(&model,&state)?;
    // The existing du/escaped-energy fields are deliberately not consumed:
    // Case-B OTS thermal recycling is outside this number-only adapter.
    for g in 0..3 {
        if input.photon_energy_ev[g]<input.edge_energy_ev[g]||input.photon_energy_ev[g]>input.edge_energy_ev[g+1] {
            return Err(ForwardError::InvalidInput("FLRW_NODE_OUTSIDE_BIN"));
        }
    }
    let volume=finite((input.scale_factor*MPC_CM).powi(3))?;positive(volume)?;
    let mut nodes=[PhotonNode{energy_ev:0.0,n_comoving_per_cmpc3:0.0};3];
    for g in 0..3 {nodes[g]=PhotonNode{energy_ev:input.photon_energy_ev[g],n_comoving_per_cmpc3:finite(volume*input.photon_proper_cm3[g])?};}
    let bridge=homogeneous_photo_rates(&provider,[input.n_h_proper_cm3*(1.0-input.x_hii),0.0,0.0],input.scale_factor,&nodes)?;
    let mut absorption=[0.0;3];
    for g in 0..3{nn(input.other_absorption_proper_cm3_s[g])?;
        absorption[g]=finite(event.photo_per_cm3_s[0][g]+input.other_absorption_proper_cm3_s[g])?;}
    let photon=photon_balance(PhotonInput{scale_factor:input.scale_factor,hubble_s:input.hubble_s,
        comoving_photons_cm3:input.photon_proper_cm3.map(|n|a3*n),edge_energy_ev:input.edge_energy_ev,
        edge_n_per_cm3_ev:input.edge_n_per_cm3_ev,source_proper_cm3_s:input.source_proper_cm3_s,
        absorption_proper_cm3_s:absorption})?;
    let photo=finite(event.photo_per_cm3_s[0].iter().sum())?;
    Ok(CellResult{n_h_proper_cm3:input.n_h_proper_cm3,x_hii:input.x_hii,
        photon_proper_cm3:finite(input.photon_proper_cm3.iter().sum())?,x_dot_s:event.derivative[0],
        gamma_hi_s:bridge.gamma_per_s[0],alpha_cm3_s:alpha,ci_cm3_s:ci,
        sigma_hi_cm2:model.sigma_cm2[0],electron_proper_cm3:input.n_h_proper_cm3*input.x_hii,
        photo_proper_cm3_s:photo,collision_proper_cm3_s:event.collision_per_cm3_s[0],
        recombination_proper_cm3_s:event.recombination_per_cm3_s[0],
        other_absorption_proper_cm3_s:finite(input.other_absorption_proper_cm3_s.iter().sum())?,
        photo_bridge_residual_proper_cm3_s:finite(photo-bridge.events_proper_per_cm3_s[0])?,
        photon,scale_factor:input.scale_factor,hubble_s:input.hubble_s})
}

#[derive(Debug,Clone,Copy)]
pub struct Ensemble {
    pub x_volume:f64,pub x_mass:f64,pub eta:f64,
    pub x_volume_dot_s:f64,pub x_mass_dot_s:f64,pub eta_dot_s:f64,
    pub mean_n_h_proper_cm3:f64,pub source_per_h_s:f64,
    pub recombination_per_h_s:f64,pub collision_per_h_s:f64,
    pub other_absorption_per_h_s:f64,pub redshift_boundary_per_h_s:f64,
    pub combined_inventory_residual_s:f64,
    pub density_ionization_covariance:f64,
}
fn validate_cell_result(c:&CellResult)->Result<(),ForwardError>{
    // Public CellResult records may be constructed outside connected_cell().
    // Validate each cell BEFORE weighting, so a positive aggregate cannot hide
    // a negative individual density or a zero weight hide nonfinite data.
    positive(c.n_h_proper_cm3)?;positive(c.scale_factor)?;nn(c.hubble_s)?;
    nn(c.x_hii)?;
    if c.x_hii>1.0{return Err(ForwardError::InvalidInput("FLRW_FRACTION_DOMAIN"));}
    for v in [c.photon_proper_cm3,c.gamma_hi_s,c.alpha_cm3_s,c.ci_cm3_s,
        c.electron_proper_cm3,c.photo_proper_cm3_s,c.collision_proper_cm3_s,
        c.recombination_proper_cm3_s,c.other_absorption_proper_cm3_s,
        c.photon.source_comoving_cm3_s,c.photon.absorption_comoving_cm3_s] {nn(v)?;}
    for v in c.sigma_hi_cm2.into_iter().chain(c.photon.edge_flux_comoving_cm3_s){nn(v)?;}
    for v in [c.x_dot_s,c.photo_bridge_residual_proper_cm3_s,
        c.photon.boundary_net_loss_comoving_cm3_s,c.photon.summed_balance_residual]
        .into_iter().chain(c.photon.comoving_dot_cm3_s).chain(c.photon.proper_dot_cm3_s){finite(v)?;}
    Ok(())
}
/// Fixed comoving-volume weights, common FLRW background, no matter boundary
/// flux, and frozen density contrasts. Cells co-expand without peculiar advection,
/// compression, or intercell matter transport. Generic X_V=<x> is NOT geometric Q_V.
pub fn ensemble(cells:&[(f64,CellResult)])->Result<Ensemble,ForwardError>{
    if cells.is_empty(){return Err(ForwardError::InvalidInput("FLRW_EMPTY_ENSEMBLE"));}
    let a=cells[0].1.scale_factor;let h=cells[0].1.hubble_s;let a3=cube(a)?;
    let mut wsum=0.0;let mut n=0.0;let mut vx=0.0;let mut mx=0.0;let mut ng=0.0;
    let mut vdx=0.0;let mut mdx=0.0;let mut dg=0.0;let mut source=0.0;
    let mut recomb=0.0;let mut coll=0.0;let mut other=0.0;let mut loss=0.0;
    for &(w,c) in cells{
        validate_cell_result(&c)?;
        nn(w)?;if c.scale_factor!=a||c.hubble_s!=h{return Err(ForwardError::InvalidInput("FLRW_MIXED_BACKGROUND"));}
        wsum+=w;n+=w*c.n_h_proper_cm3;vx+=w*c.x_hii;mx+=w*c.n_h_proper_cm3*c.x_hii;
        ng+=w*c.photon_proper_cm3;vdx+=w*c.x_dot_s;mdx+=w*c.n_h_proper_cm3*c.x_dot_s;
        dg+=w*c.photon.comoving_dot_cm3_s.iter().sum::<f64>()/a3;
        source+=w*c.photon.source_comoving_cm3_s/a3;recomb+=w*c.recombination_proper_cm3_s;
        coll+=w*c.collision_proper_cm3_s;other+=w*c.other_absorption_proper_cm3_s;
        loss+=w*c.photon.boundary_net_loss_comoving_cm3_s/a3;
    }
    positive(wsum)?;positive(n)?;
    let x_volume=vx/wsum;let x_mass=mx/n;let eta=ng/n;let xm_dot=mdx/n;let eta_dot=dg/n;
    let residual=xm_dot+eta_dot-(source-recomb+coll-other-loss)/n;
    for v in [x_volume,x_mass,eta,vdx/wsum,xm_dot,eta_dot,n/wsum,source/n,recomb/n,coll/n,other/n,loss/n,residual]{finite(v)?;}
    Ok(Ensemble{x_volume,x_mass,eta,x_volume_dot_s:vdx/wsum,x_mass_dot_s:xm_dot,eta_dot_s:eta_dot,
        mean_n_h_proper_cm3:n/wsum,source_per_h_s:source/n,recombination_per_h_s:recomb/n,
        collision_per_h_s:coll/n,other_absorption_per_h_s:other/n,redshift_boundary_per_h_s:loss/n,
        combined_inventory_residual_s:residual,density_ionization_covariance:x_mass-x_volume})
}
#[derive(Debug,Clone,Copy)]
pub struct FillingDefect{
    pub xi:f64,pub xi_dot_s:f64,pub standard_rhs_s:f64,pub observed_defect_s:f64,
    pub storage_term_s:f64,pub boundary_term_s:f64,pub other_term_s:f64,
    pub collision_term_s:f64,pub geometry_density_term_s:f64,pub sink_closure_term_s:f64,
    pub reconstructed_defect_s:f64,pub identity_residual_s:f64,
}
fn validate_ensemble(e:&Ensemble)->Result<(),ForwardError>{
    // Public diagnostic records can be assembled by external callers; do not
    // assume they necessarily came from ensemble(). In particular NaN must not
    // bypass a mass-closure comparison.
    for v in [e.x_volume,e.x_mass,e.eta,e.x_volume_dot_s,e.x_mass_dot_s,e.eta_dot_s,
        e.mean_n_h_proper_cm3,e.source_per_h_s,e.recombination_per_h_s,e.collision_per_h_s,
        e.other_absorption_per_h_s,e.redshift_boundary_per_h_s,
        e.combined_inventory_residual_s,e.density_ionization_covariance]{finite(v)?;}
    for v in [e.x_volume,e.x_mass,e.eta,e.source_per_h_s,e.recombination_per_h_s,
        e.collision_per_h_s,e.other_absorption_per_h_s]{nn(v)?;}
    positive(e.mean_n_h_proper_cm3)?;
    if e.x_volume>1.0||e.x_mass>1.0{return Err(ForwardError::InvalidInput("FLRW_ENSEMBLE_FRACTION_DOMAIN"));}
    Ok(())
}
/// Identity diagnostic using EXTERNALLY SUPPLIED geometric Q_V and dot Q_V.
/// This function does not infer a front/region geometry from local fractions.
pub fn filling_defect(e:Ensemble,q_v:f64,q_v_dot_s:f64,inverse_t_ref_s:f64)->Result<FillingDefect,ForwardError>{
    validate_ensemble(&e)?;
    nn(q_v)?;if q_v>1.0{return Err(ForwardError::InvalidInput("FLRW_Q_DOMAIN"));}
    finite(q_v_dot_s)?;nn(inverse_t_ref_s)?;
    let xi=e.x_mass-q_v;let xidot=e.x_mass_dot_s-q_v_dot_s;
    let standard=e.source_per_h_s-q_v*inverse_t_ref_s;let defect=q_v_dot_s-standard;
    let storage=-e.eta_dot_s;let boundary=-e.redshift_boundary_per_h_s;
    let other=-e.other_absorption_per_h_s;let coll=e.collision_per_h_s;
    let geometry=-xidot;let sink=-(e.recombination_per_h_s-q_v*inverse_t_ref_s);
    let reconstructed=finite(storage+boundary+other+coll+geometry+sink)?;
    Ok(FillingDefect{xi,xi_dot_s:xidot,standard_rhs_s:standard,observed_defect_s:defect,
        storage_term_s:storage,boundary_term_s:boundary,other_term_s:other,
        collision_term_s:coll,geometry_density_term_s:geometry,sink_closure_term_s:sink,
        reconstructed_defect_s:reconstructed,identity_residual_s:finite(defect-reconstructed)?})
}

#[derive(Debug,Clone,Copy)]
pub struct SharpPhaseInput {
    pub q_v:f64,
    pub ionized_density_contrast:f64,
    pub contrast_dot_s:f64,
    /// An external model declaration, not a conclusion inferred from cell x.
    pub fully_ionized_neutral_sharp_phases_declared:bool,
}
#[derive(Debug,Clone,Copy)]
pub struct SharpFillingRhs {
    pub q_v_dot_s:f64,
    pub inventory_q_v_dot_s:f64,
    pub identity_residual_s:f64,
}
/// Conditional sharp-phase inventory closure X_M=Q_V*Delta_I. The caller owns
/// the sharp geometry and Delta_I derivative. Only 0<Q_V<1 is admitted here;
/// endpoint phases need a separately defined one-sided closure. Not a front solver.
pub fn sharp_filling_rhs(e:Ensemble,p:SharpPhaseInput)->Result<SharpFillingRhs,ForwardError>{
    validate_ensemble(&e)?;
    if !p.fully_ionized_neutral_sharp_phases_declared {
        return Err(ForwardError::InvalidInput("FLRW_SHARP_PHASE_NOT_DECLARED"));
    }
    positive(p.q_v)?;positive(p.ionized_density_contrast)?;finite(p.contrast_dot_s)?;
    if p.q_v>=1.0{return Err(ForwardError::InvalidInput("FLRW_SHARP_INTERIOR_PHASE_REQUIRED"));}
    let mass=finite(p.q_v*p.ionized_density_contrast)?;
    if mass>1.0{return Err(ForwardError::InvalidInput("FLRW_SHARP_MASS_EXCEEDS_ONE"));}
    if (mass-e.x_mass).abs()>2e-12*mass.abs().max(e.x_mass.abs())+2e-14 {
        return Err(ForwardError::InvalidInput("FLRW_SHARP_MASS_CLOSURE_MISMATCH"));
    }
    let drift=p.q_v*p.contrast_dot_s;
    let direct=finite((e.x_mass_dot_s-drift)/p.ionized_density_contrast)?;
    let inventory=finite((e.source_per_h_s-e.recombination_per_h_s+e.collision_per_h_s
        -e.other_absorption_per_h_s-e.redshift_boundary_per_h_s-e.eta_dot_s-drift)
        /p.ionized_density_contrast)?;
    Ok(SharpFillingRhs{q_v_dot_s:direct,inventory_q_v_dot_s:inventory,
        identity_residual_s:finite(direct-inventory)?})
}

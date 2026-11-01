//! BASS Type-II production-preflight: pure compile-only *mock* carrier contract.
//! Never wired to `_rustcore` or runtime dispatch. BASS owner main pinned in SOURCE_LOCK.json.
//! Original 5-state Rust source included only in the test module, read-only.
use std::fmt;

pub const SQRT3: f64 = 1.7320508075688772935;
pub const SPEED_OF_LIGHT_SI: f64 = 299_792_458.0;
pub const CODAZZI_TOL: f64 = 1.0e-12; // measured 401 parent original states max ~4e-16

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct TypeII5 {
    /// BASS WE-normalized (SigmaPlus,SigmaMinus,Sigma13,N1,v2).
    pub x: [f64; 5],
    pub gamma: f64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Normalization { BASS_WE, Ringstrom }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum TimeVariable { HubbleEfold, ProperSeconds }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Frame { Normal, ElectronRest }

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct MockHostState {
    /// Existing `_rustcore/src/core/conventions.rs::tracefree_from_5` order:
    /// (S00,S11,S01,S02,S12). NOT the six independent symmetric components.
    pub shear5: [f64; 5],
    /// Existing `_rustcore/src/geom/group.rs::BianchiGroup.n`:
    /// (N11,N22,N33,N12,N13,N23).
    pub n6: [f64; 6],
    pub a3: [f64; 3],
    pub v3: [f64; 3],
    pub omega: f64,
    pub gamma: f64,
    pub normalization: Normalization,
    pub time: TimeVariable,
    pub frame: Frame,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ContractError {
    NonFinite, InvalidGamma, TachyonicTilt, TypeIBoundary,
    NonPositiveMatter, WrongNormalization, WrongClock, WrongFrame,
    OffInvariantSlice, MomentumConstraint, GaussConstraint,
    NonPositiveHubble, NegativeElectronDensity, InvalidCrossSection,
}
impl fmt::Display for ContractError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result { write!(f,"{self:?}") }
}

impl TypeII5 {
    pub fn source_terms(self) -> Result<(f64,f64,f64), ContractError> {
        let [sp,sm,s13,n1,v2]=self.x;
        if !self.x.iter().all(|x|x.is_finite()) {return Err(ContractError::NonFinite)}
        if !self.gamma.is_finite(){return Err(ContractError::NonFinite)}
        if !(self.gamma>0.0 && self.gamma<2.0){return Err(ContractError::InvalidGamma)}
        if !(v2.abs()<1.0) {return Err(ContractError::TachyonicTilt)}
        if !(n1>0.0){return Err(ContractError::TypeIBoundary)}
        let gp=1.0+(self.gamma-1.0)*v2*v2;
        let omega=1.0-sp*sp-sm*sm-s13*s13-n1*n1/12.0;
        if !(omega>0.0){return Err(ContractError::NonPositiveMatter)}
        let q2=3.0*self.gamma*omega*v2/gp;
        let codazzi=-SQRT3*n1*s13-q2;
        Ok((omega,gp,codazzi))
    }
    pub fn validate(self)->Result<f64,ContractError>{
        let (omega,_,c)=self.source_terms()?;
        if c.abs()>CODAZZI_TOL {return Err(ContractError::MomentumConstraint)}
        Ok(omega)
    }
    /// Pure compile-only translation. Does not create a production RustCore StateAT.
    pub fn to_mock_host(self)->Result<MockHostState,ContractError>{
        let omega=self.validate()?;
        let [sp,sm,s13,n1,v2]=self.x;
        Ok(MockHostState{
            shear5:[-2.0*sp,sp+SQRT3*sm,0.0,SQRT3*s13,0.0],
            n6:[n1,0.0,0.0,0.0,0.0,0.0],a3:[0.0;3],v3:[0.0,v2,0.0],
            omega,gamma:self.gamma,
            normalization:Normalization::BASS_WE,time:TimeVariable::HubbleEfold,
            frame:Frame::Normal})
    }
    /// Four independent physical chart coordinates -> original stored 5-state.
    /// Requires N1>0 and a positive Gauss source budget.
    pub fn from_four(sp:f64,sm:f64,n1:f64,v2:f64,gamma:f64)->Result<Self,ContractError>{
        if ![sp,sm,n1,v2,gamma].iter().all(|a|a.is_finite()){return Err(ContractError::NonFinite)}
        if !(gamma>0.0&&gamma<2.0){return Err(ContractError::InvalidGamma)}
        if !(v2.abs()<1.0){return Err(ContractError::TachyonicTilt)}
        if !(n1>0.0){return Err(ContractError::TypeIBoundary)}
        let budget=1.0-sp*sp-sm*sm-n1*n1/12.0;
        if !(budget>0.0){return Err(ContractError::NonPositiveMatter)}
        let gp=1.0+(gamma-1.0)*v2*v2;
        let beta=3.0*gamma*gamma*v2*v2/(n1*n1*gp*gp);
        let omega=2.0*budget/(1.0+(1.0+4.0*beta*budget).sqrt());
        let sigma13=-SQRT3*gamma*omega*v2/(n1*gp);
        let state=Self{x:[sp,sm,sigma13,n1,v2],gamma};
        state.validate()?;
        Ok(state)
    }
}

fn near_zero(value:f64)->bool{value.abs()<=1.0e-14}

impl MockHostState {
    pub fn to_typeii(self)->Result<TypeII5,ContractError>{
        if self.normalization!=Normalization::BASS_WE{return Err(ContractError::WrongNormalization)}
        if self.time!=TimeVariable::HubbleEfold{return Err(ContractError::WrongClock)}
        if self.frame!=Frame::Normal{return Err(ContractError::WrongFrame)}
        if !self.shear5.iter().chain(self.n6.iter()).chain(self.a3.iter())
              .chain(self.v3.iter()).chain([self.omega,self.gamma].iter())
              .all(|x|x.is_finite()){return Err(ContractError::NonFinite)}
        if ![self.shear5[2],self.shear5[4],self.n6[1],self.n6[2],
              self.n6[3],self.n6[4],self.n6[5],self.a3[0],self.a3[1],self.a3[2],
              self.v3[0],self.v3[2]].iter().all(|v| near_zero(*v)){
            return Err(ContractError::OffInvariantSlice)}
        let sp=-self.shear5[0]/2.0;
        let sm=(self.shear5[1]-sp)/SQRT3;
        let state=TypeII5{x:[sp,sm,self.shear5[3]/SQRT3,self.n6[0],self.v3[1]],gamma:self.gamma};
        let omega=state.validate()?;
        if (omega-self.omega).abs()>1.0e-12{return Err(ContractError::GaussConstraint)}
        Ok(state)
    }
}

/// Separate SI clock: only this wrapper knows physical Hubble/sigma_T/electron density.
/// No local-observer boost or alpha scaling is applied implicitly.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct PhysicalThomsonClock {
    pub hubble_per_s:f64,
    pub electron_density_per_m3:f64,
    pub sigma_thomson_m2:f64,
}
impl PhysicalThomsonClock {
    pub fn tau_increment(self,proper_dt_seconds:f64)->Result<f64,ContractError>{
        self.validate()?;
        if !proper_dt_seconds.is_finite()||proper_dt_seconds<0.0{return Err(ContractError::WrongClock)}
        Ok(self.hubble_per_s*proper_dt_seconds)
    }
    fn validate(self)->Result<(),ContractError>{
        if !self.hubble_per_s.is_finite()||self.hubble_per_s<=0.0 {return Err(ContractError::NonPositiveHubble)}
        if !self.electron_density_per_m3.is_finite()||self.electron_density_per_m3<0.0 {return Err(ContractError::NegativeElectronDensity)}
        if !self.sigma_thomson_m2.is_finite()||self.sigma_thomson_m2<=0.0 {return Err(ContractError::InvalidCrossSection)}
        Ok(())
    }
    /// This is the normal-observer scalar rate BEFORE the Type-II generator's
    /// one and only q_alpha=(1-v2*n_y) direction-dependent relative-flux factor.
    pub fn rate_per_hubble_tau(self)->Result<f64,ContractError>{
        self.validate()?;
        Ok(self.electron_density_per_m3*self.sigma_thomson_m2*SPEED_OF_LIGHT_SI/self.hubble_per_s)
    }
    // No public angular-rate callback: original Type-II collision generator already
    // owns q_alpha=(1-v2*n_y). Multiplying an external q_alpha would count it twice.
}

#[cfg(test)]
#[path = "../../../generated/rust/typeii/typeii_background.rs"]
mod generated_typeii_background;

#[cfg(test)]
mod tests {
    use super::*;

    fn max_abs(x:&[f64],y:&[f64])->f64{
        x.iter().zip(y).map(|(a,b)|(a-b).abs()).fold(0.0_f64,f64::max)
    }
    #[test]
    fn fixture_initial_and_end_roundtrip(){
        let samples=[
          [0.2375,0.0,-0.11295198246134101,0.865,0.05],
          [0.23589280617191827,0.0011762626215999644,-0.11111400398542129,0.8656976065419973,0.04916422467912665],
          [0.2344323245610861,0.0022546245729999554,-0.10926301003425215,0.8666051475225526,0.048341364320257395],
          [0.23311696641948262,0.003240396330614939,-0.10740419847472094,0.8677003864710054,0.047531284763414644],
          [0.23194442492523865,0.004138743982585919,-0.10554243482596554,0.8689615028713741,0.046733834290499716]
        ];
        for s in samples {
            let state=TypeII5{x:s,gamma:1.3};let host=state.to_mock_host().unwrap();
            let recovered=host.to_typeii().unwrap();
            assert!(max_abs(&state.x,&recovered.x)<2.0e-16);
            let chart=TypeII5::from_four(s[0],s[1],s[3],s[4],1.3).unwrap();
            assert!(max_abs(&chart.x,&s)<1.0e-12);
            assert_eq!(host.n6,[s[3],0.0,0.0,0.0,0.0,0.0]);
            assert_eq!(host.v3,[0.0,s[4],0.0]);
        }
    }
    #[test]
    fn original_generated_rhs_is_consumable_read_only(){
        let state=[0.2375,0.0,-0.11295198246134101,0.865,0.05];
        let expected=[-0.0336177132003016,0.0245403512235811,0.036593148186233285,0.01170272685712611,-0.016845446584938688];
        let got=generated_typeii_background::rhs(&state,1.3);
        assert!(max_abs(&got,&expected)<2.0e-13);
        let d=[1.0,-2.0,3.0,-4.0,5.0];
        let jvp=generated_typeii_background::jvp(&state,1.3,&d);
        let h=1.0e-6;
        let mut xp=state;let mut xm=state;
        for i in 0..5{xp[i]+=h*d[i];xm[i]-=h*d[i];}
        let yp=generated_typeii_background::rhs(&xp,1.3);
        let ym=generated_typeii_background::rhs(&xm,1.3);
        let fd=std::array::from_fn::<f64,5,_>(|i|(yp[i]-ym[i])/(2.0*h));
        assert!(max_abs(&jvp,&fd)<1.0e-7);
    }
    #[test]
    fn off_slice_or_wrong_shear_sign_is_rejected(){
        let s=TypeII5::from_four(0.2375,0.0,0.865,0.05,1.3).unwrap();
        let mut h=s.to_mock_host().unwrap();h.v3[0]=0.02;
        assert_eq!(h.to_typeii().unwrap_err(),ContractError::OffInvariantSlice);
        let mut h=s.to_mock_host().unwrap();h.shear5[3]=-h.shear5[3];
        assert_eq!(h.to_typeii().unwrap_err(),ContractError::MomentumConstraint);
        let mut h=s.to_mock_host().unwrap();h.shear5[3]/=SQRT3;
        assert_eq!(h.to_typeii().unwrap_err(),ContractError::MomentumConstraint);
        let mut h=s.to_mock_host().unwrap();h.n6[1]=0.1;
        assert_eq!(h.to_typeii().unwrap_err(),ContractError::OffInvariantSlice);
    }
    #[test]
    fn invalid_scalar_inputs_fail_closed(){
        assert_eq!(TypeII5::from_four(0.0,0.0,0.0,0.1,1.3).unwrap_err(),ContractError::TypeIBoundary);
        assert_eq!(TypeII5::from_four(0.0,0.0,1.0,1.0,1.3).unwrap_err(),ContractError::TachyonicTilt);
        assert_eq!(TypeII5::from_four(0.0,0.0,1.0,0.1,2.0).unwrap_err(),ContractError::InvalidGamma);
        assert_eq!(TypeII5::from_four(1.0,0.0,1.0,0.1,1.3).unwrap_err(),ContractError::NonPositiveMatter);
        let s=TypeII5::from_four(0.2375,0.0,0.865,0.05,1.3).unwrap();
        let mut h=s.to_mock_host().unwrap();h.omega+=0.01;
        assert_eq!(h.to_typeii().unwrap_err(),ContractError::GaussConstraint);
    }
    #[test]
    fn wrong_units_and_frame_fail_closed(){
        let s=TypeII5::from_four(0.2375,0.0,0.865,0.05,1.3).unwrap();
        let mut h=s.to_mock_host().unwrap();h.normalization=Normalization::Ringstrom;
        assert_eq!(h.to_typeii().unwrap_err(),ContractError::WrongNormalization);
        let mut h=s.to_mock_host().unwrap();h.time=TimeVariable::ProperSeconds;
        assert_eq!(h.to_typeii().unwrap_err(),ContractError::WrongClock);
        let mut h=s.to_mock_host().unwrap();h.frame=Frame::ElectronRest;
        assert_eq!(h.to_typeii().unwrap_err(),ContractError::WrongFrame);
    }
    #[test]
    fn clock_and_directional_flux_contract(){
        let x=PhysicalThomsonClock{hubble_per_s:2.0e-14,electron_density_per_m3:1.0e8,sigma_thomson_m2:6.6524587321e-29};
        let dt=1.0e13;assert!((x.tau_increment(dt).unwrap()-0.2).abs()<1.0e-15);
        let nu=x.rate_per_hubble_tau().unwrap();
        let original_q_alpha=1.0-0.1*0.6;
        let angle=nu*original_q_alpha; // exactly one source-generated q factor
        assert!((angle-nu*0.94).abs()<1.0e-14);
        assert!((angle-nu*original_q_alpha*original_q_alpha).abs()>1.0e-3);
        let mut bad=x;bad.hubble_per_s=0.0;
        assert_eq!(bad.rate_per_hubble_tau().unwrap_err(),ContractError::NonPositiveHubble);
        bad=x;bad.electron_density_per_m3=-1.0;
        assert_eq!(bad.rate_per_hubble_tau().unwrap_err(),ContractError::NegativeElectronDensity);
    }
    #[test]
    fn exact_nontilt_and_positive_root(){
        let s=TypeII5::from_four(0.05,0.03,0.8,0.0,1.3).unwrap();
        assert_eq!(s.x[2],0.0);assert!(s.validate().unwrap()>0.0);
        let d=TypeII5::from_four(0.1,-0.05,0.65,-0.2,1.3).unwrap();
        assert!(d.x[2]>0.0);assert!(d.validate().unwrap()>0.0);
    }
}
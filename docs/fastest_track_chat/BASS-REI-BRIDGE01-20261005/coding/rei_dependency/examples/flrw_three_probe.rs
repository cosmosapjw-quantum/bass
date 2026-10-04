use rei_microphysics::flrw_three_equations::*;
use rei_microphysics::RecombinationCase;
use std::io::{self,BufRead,Write};
fn triple(v:&[f64],i:usize)->[f64;3]{[v[i],v[i+1],v[i+2]]}
fn four(v:&[f64],i:usize)->[f64;4]{[v[i],v[i+1],v[i+2],v[i+3]]}
fn values(row:usize,v:&[f64])->Result<(),String>{
    print!("{row}");for x in v{print!(",{x:.17e}");}println!();
    io::stdout().flush().map_err(|e|e.to_string())
}
fn cell(v:&[f64],case:RecombinationCase,collisions:bool)->Result<CellResult,String>{
    if v.len()!=25{return Err("cell requires 25 numeric fields".into());}
    connected_cell(CellInput{scale_factor:v[0],hubble_s:v[1],temperature_k:v[2],
        n_h_proper_cm3:v[3],x_hii:v[4],case,include_collisions:collisions,
        photon_proper_cm3:triple(v,5),source_proper_cm3_s:triple(v,8),
        other_absorption_proper_cm3_s:triple(v,11),photon_energy_ev:triple(v,14),
        edge_energy_ev:four(v,17),edge_n_per_cm3_ev:four(v,21)}).map_err(|e|e.to_string())
}
fn run()->Result<(),String>{
    let args:Vec<String>=std::env::args().collect();
    let mode=args.get(1).map(String::as_str).ok_or("mode photon/cell/ensemble required")?;
    let case=match args.get(2).map(String::as_str).unwrap_or("A"){
        "A"=>RecombinationCase::A,"B"=>RecombinationCase::B,_=>return Err("case must be A or B".into())};
    let collisions=match args.get(3).map(String::as_str).unwrap_or("0"){
        "0"=>false,"1"=>true,_=>return Err("collision flag must be 0 or 1".into())};
    match mode{
        "photon"=>println!("row,dN0,dN1,dN2,dn0,dn1,dn2,F0,F1,F2,F3,boundary_net,source_comoving,absorption_comoving,residual"),
        "cell"=>println!("row,alpha,ci,sigma0,sigma1,sigma2,gamma,ne,photo,recombination,collision,dx,photo_bridge_residual,dN0,dN1,dN2,dn0,dn1,dn2,boundary_net,source_comoving,other_absorption_proper,photon_total_proper"),
        "ensemble"=>(),_=>return Err("unknown mode".into())
    }
    io::stdout().flush().map_err(|e|e.to_string())?;
    let mut cells=Vec::new();
    for (index,line) in io::stdin().lock().lines().enumerate(){
        let line=line.map_err(|e|e.to_string())?;
        if line.trim().is_empty()||line.trim_start().starts_with('#'){continue;}
        let v:Vec<f64>=line.split(',').map(|s|s.trim().parse::<f64>()).collect::<Result<_,_>>().map_err(|e|e.to_string())?;
        match mode{
            "photon"=>{
                if v.len()!=19{return Err("photon requires 19 numeric fields".into());}
                let b=photon_balance(PhotonInput{scale_factor:v[0],hubble_s:v[1],comoving_photons_cm3:triple(&v,2),
                    edge_energy_ev:four(&v,5),edge_n_per_cm3_ev:four(&v,9),source_proper_cm3_s:triple(&v,13),
                    absorption_proper_cm3_s:triple(&v,16)}).map_err(|e|e.to_string())?;
                let mut out=b.comoving_dot_cm3_s.to_vec();out.extend(b.proper_dot_cm3_s);out.extend(b.edge_flux_comoving_cm3_s);
                out.extend([b.boundary_net_loss_comoving_cm3_s,b.source_comoving_cm3_s,b.absorption_comoving_cm3_s,b.summed_balance_residual]);
                values(index+1,&out)?;
            },
            "cell"=>{
                let c=cell(&v,case,collisions)?;
                let mut out=vec![c.alpha_cm3_s,c.ci_cm3_s];out.extend(c.sigma_hi_cm2);
                out.extend([c.gamma_hi_s,c.electron_proper_cm3,c.photo_proper_cm3_s,c.recombination_proper_cm3_s,
                    c.collision_proper_cm3_s,c.x_dot_s,c.photo_bridge_residual_proper_cm3_s]);
                out.extend(c.photon.comoving_dot_cm3_s);out.extend(c.photon.proper_dot_cm3_s);
                out.extend([c.photon.boundary_net_loss_comoving_cm3_s,c.photon.source_comoving_cm3_s,
                    c.other_absorption_proper_cm3_s,c.photon_proper_cm3]);values(index+1,&out)?;
            },
            "ensemble"=>{if v.len()!=26{return Err("ensemble requires weight plus 25 cell fields".into());}
                cells.push((v[0],cell(&v[1..],case,collisions)?));},_=>unreachable!()
        }
    }
    if mode=="ensemble"{
        let parse=|i:usize|->Result<f64,String>{args.get(i).ok_or_else(||format!("ensemble requires argument {i}"))?.parse::<f64>().map_err(|e|e.to_string())};
        let q=parse(4)?;let qdot=parse(5)?;let invt=parse(6)?;
        let e=ensemble(&cells).map_err(|e|e.to_string())?;
        let d=filling_defect(e,q,qdot,invt).map_err(|e|e.to_string())?;
        println!("row,XV,XM,eta,XVdot,XMdot,etadot,nbar,source_perH,recomb_perH,coll_perH,other_perH,boundary_perH,combined_residual,covariance,Xi,Xidot,standard_Qrhs,defect_direct,storage,boundary,other,collision,geometry_density,sink_closure,defect_reconstructed,defect_residual");
        values(1,&[e.x_volume,e.x_mass,e.eta,e.x_volume_dot_s,e.x_mass_dot_s,e.eta_dot_s,e.mean_n_h_proper_cm3,
            e.source_per_h_s,e.recombination_per_h_s,e.collision_per_h_s,e.other_absorption_per_h_s,
            e.redshift_boundary_per_h_s,e.combined_inventory_residual_s,e.density_ionization_covariance,
            d.xi,d.xi_dot_s,d.standard_rhs_s,d.observed_defect_s,d.storage_term_s,d.boundary_term_s,
            d.other_term_s,d.collision_term_s,d.geometry_density_term_s,d.sink_closure_term_s,
            d.reconstructed_defect_s,d.identity_residual_s])?;
    }
    Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("{e}");std::process::exit(2)}}

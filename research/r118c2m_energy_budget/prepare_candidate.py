"""Apply opt-in host integration to an exact archived BASS source tree."""
from pathlib import Path
import sys
d=Path(sys.argv[1])
def patch(p,pairs):
    s=p.read_text()
    for old,new in pairs:
        assert s.count(old)==1,(str(p),old[:100],s.count(old))
        s=s.replace(old,new,1)
    p.write_text(s)
patch(d/'_rustcore/Cargo.toml',[
('rei_microphysics = { git = "https://github.com/cosmosapjw-quantum/rei_bianchi.git", rev = "e93661d3b83beb4cb2c381339dde6e860c28e7c1" }','rei_microphysics = { path = "../rei_patch/rust/rei_microphysics" }')])
patch(d/'_rustcore/src/homogeneous_sky/rei_live.rs',[
('axbi_driver::{packet_chemistry_stage, PacketStageInput}', 'axbi_driver::{packet_chemistry_stage, packet_chemistry_stage_budgeted, PacketStageInput}'),
('    pub max_final_rate_error: f64,\n','''    pub max_final_rate_error: f64,
    pub chemistry_signed_ev: f64,
    pub chemistry_absolute_ev: f64,
    pub chemistry_budget_used_ev: f64,
    pub chemistry_max_ratio: f64,
    pub chemistry_last_ev: f64,
    pub chemistry_last_limit_ev: f64,
'''),
('''    if rate_tol.is_some() && width.is_none() {''','''    evolve_energy_budgeted(records,input,width,rate_tol,None)
}
/// Opt-in absolute trajectory chemistry budget, eV/H. Does not relax any
/// original gate; finite precision or an unachievable local target fails closed.
pub fn evolve_energy_budgeted(
    records: &[StepRecord], input: LiveInput, width: Option<f64>,
    rate_tol: Option<f64>, energy_budget_ev: Option<f64>,
) -> Result<LiveResult,String> {
    if energy_budget_ev.is_some_and(|b| !b.is_finite() || b<=0. || b>1e-8) {
        return Err("chemistry energy budget domain".into());
    }
    if rate_tol.is_some() && width.is_none() {'''),
('''    let src = AxbiSource::new(''','''    let eta_span = records.last().unwrap().right.eta-records[0].left.eta;
    if !eta_span.is_finite() || eta_span<=0. {return Err("invalid energy budget interval".into());}
    let src = AxbiSource::new('''),
('''        let q = packet_chemistry_stage(
            PacketStageInput {
                n_h_cm3: nh * 1e-6,
                n_he_cm3: nh * 1e-6 * input.f_he,
                tcmb_k: input.tcmb0_k / am,
            },
            gas,
            &inputs,
            dt,
            &mut counter,
            20_000_000,
        )
        .map_err(|e| format!("REI packet stage eta={:e}: {e}", m.eta))?;''','''        let stage_input = PacketStageInput {
            n_h_cm3: nh * 1e-6,
            n_he_cm3: nh * 1e-6 * input.f_he,
            tcmb_k: input.tcmb0_k / am,
        };
        let limit = energy_budget_ev.map(|b|b*(h/eta_span));
        let q = if let Some(b)=limit {
            packet_chemistry_stage_budgeted(stage_input,gas,&inputs,dt,&mut counter,20_000_000,b)
        } else {
            packet_chemistry_stage(stage_input,gas,&inputs,dt,&mut counter,20_000_000)
        }.map_err(|e|format!("REI packet stage eta={:e} step={} limit={limit:?}: {e}",m.eta,history.len()))?;'''),
('''        gas = q.gas;
        for (p, n)''','''        if let Some(b)=limit {
            // Reconstruct from physical gas and photon output, not the Newton residual.
            let c=HHeModel::controlled_fixture().threshold_ev;
            let fhe=stage_input.n_he_cm3/stage_input.n_h_cm3;
            let d=std::array::from_fn::<_,3,_>(|i|q.gas.fractions[i]-gas.fractions[i]);
            let db=c[0]*d[0]+fhe*(c[1]*d[1]+(c[1]+c[2])*d[2]);
            let defect=thermal(q.gas)?-thermal(gas)?+db-a.energy
                +q.ledgers.escaped_u-q.ledgers.cmb_input;
            if !defect.is_finite() || defect.abs()>b {
                return Err(format!("host chemistry budget mismatch eta={:e}: {defect:e} > {b:e}",m.eta));
            }
            ledger.chemistry_signed_ev+=defect;
            ledger.chemistry_absolute_ev+=defect.abs();
            ledger.chemistry_budget_used_ev+=b;
            ledger.chemistry_max_ratio=ledger.chemistry_max_ratio.max(defect.abs()/b);
            ledger.chemistry_last_ev=defect;
            ledger.chemistry_last_limit_ev=b;
            if ledger.chemistry_absolute_ev>ledger.chemistry_budget_used_ev*(1.+1e-10) {
                return Err("cumulative chemistry budget mismatch".into());
            }
        }
        gas = q.gas;
        for (p, n)''')])
orig=d/'_rustcore/examples/rei_live_characteristics.rs'
dest=orig.with_name('rei_live_energy_budget.rs');dest.write_text(orig.read_text())
patch(dest,[
('rei_live::{evolve_rate_checked, LiveInput}','rei_live::{evolve_energy_budgeted, LiveInput}'),
('a.len() != 8 && a.len() != 9 && a.len() != 10','a.len() != 8 && a.len() != 9 && a.len() != 10 && a.len() != 11'),
('RATE_RELATIVE_TOL]]','RATE_RELATIVE_TOL [ENERGY_BUDGET_EV_PER_H]]]'),
('''    let rate_tol: Option<f64> = a.get(9).map(|v| v.parse()).transpose()?;''','''    let rate_tol: Option<f64> = a.get(9).map(|v| v.parse()).transpose()?;
    let energy_budget: Option<f64> = a.get(10).map(|v| v.parse()).transpose()?;'''),
('let s = evolve_rate_checked(','let s = evolve_energy_budgeted('),
('''        rate_tol,
    )?;''','''        rate_tol,
        energy_budget,
    )?;'''),
('''    let ledger = &s.history.last().unwrap().ledger;''','''    let mut cb=BufWriter::new(fs::File::create(out.join("chemistry_budget.tsv"))?);
    writeln!(cb,"eta\\tlocal_defect_ev\\tlocal_limit_ev\\tsigned_ev\\tabsolute_ev\\tbudget_used_ev\\tmax_ratio")?;
    for row in &s.history {
        let l=&row.ledger;
        writeln!(cb,"{:.17e}\\t{:.17e}\\t{:.17e}\\t{:.17e}\\t{:.17e}\\t{:.17e}\\t{:.17e}",
            row.eta,l.chemistry_last_ev,l.chemistry_last_limit_ev,l.chemistry_signed_ev,
            l.chemistry_absolute_ev,l.chemistry_budget_used_ev,l.chemistry_max_ratio)?;
    }
    cb.flush()?;
    let ledger = &s.history.last().unwrap().ledger;''')])

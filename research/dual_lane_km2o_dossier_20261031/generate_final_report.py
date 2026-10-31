"""Produce measured source-grounded BASS KM2O final paper-style report and next-thread handoff."""
import argparse,hashlib,json,os
from pathlib import Path

def emit(source,audit,dag,outdir):
    source=Path(source);audit=Path(audit);dag=Path(dag);out=Path(outdir)
    a=json.loads(source.read_text());b=json.loads(audit.read_text());d=json.loads(dag.read_text())
    if b['decision']!='PASS_SCOPED' or len(a['measurements'])!=10 or d['graphs']['BASS_upper']['completed']!=9:
        raise ArithmeticError('report requires completed source-backed science and independent audit')
    r={grid:[x for x in a['measurements'] if x['grid']==grid][-1] for grid in ('GL12','GL16')}
    out.mkdir(exist_ok=True,parents=True)
    cols=[('rho_first_photon','Original exactly once scattered photon energy (BASS)'),
          ('second_gain_energy_rate','Second Thomson polarized gain energy rate per u'),
          ('second_gain_linear_polarization_mean','Generated mean linear polarization'),
          ('normal_frequency_centroid','Generated normal-frame log-frequency centroid'),
          ('first_scatter_loss_rate','Original first-order incident loss energy rate'),
          ('rest_frame_elastic_rel_gap','Electron-rest source energy gain/loss relative error'),
          ('original_P8_gain_parity_relative','Original P8 bolometric gain parity'),
          ('frequency_sigma_logbin','Second gain frequency stddev (discrete log bins)')]
    lines=['# BASS KM2O | Dropbox dossier × VigilODE DAG and original second Thomson source',
           '', 'Source HEAD '+os.getenv('GITHUB_SHA','LOCAL_UNATTESTED')+
           '; immutable BASS KM2N PR #297 HEAD `4137f942d2a95999f4e6627b71042e98f7afc1b7`.',
           'Original scientific input: 41-node GL12/GL16 original Einstein–Bianchi-I full polarized P8/Peebles once-scattered fields from source-complete frozen parent. Original electron density/tilt and screen are retained; **NO** new Einstein IVP or Peebles feedback.',
           '', '## Physical source computed, not merely planned',
           'Thomson second-gain source is constructed at actual five original times per grid, 1200 log-frequency cells per event. Dossier II electron-rest elastic polarization kernel `(3/8pi)Pe M_e Pe` acts on incoming once-scattered *polarized* coherency, with exact cold moving-electron Lorentz boost; original P8 parity checked. Exactly 10 real physics epoch records, 12,000 source spectrum bins, 6 PNG science plots. No time propagation of J^[2] or third-scatter survival.',
           '', '| Measured u=0.25 observable | GL12 | GL16 |', '|---|---:|---:|']
    for name,label in cols:lines.append('| '+label+' | '+' | '.join(format(r[g][name],'.13g') for g in ('GL12','GL16'))+' |')
    lines+=['', '## Scope-locked independent verification',
            'All ten original source-glob values agree with preceding owner source-authentic 10-epoch CSV. Independent saved-data physics audit rederives bolometric and polarized 2×2 direct pairwise Thomson kernels without importing the new gain implementation or original BASS RHS. Source audit '+b['decision']+' with residuals: '+json.dumps(b['max_residuals'],sort_keys=True)+'.',
            '', 'DAG and source crosswalk is in `DAG_CROSSWALK_AND_VIGILODE_KO.md`; recorded structured graph is `DAG_RECONCILED.json`. Dropbox BASS Integrated Dossier 2026-10-14 and all seven sections are mathematical baseline; VigilODE PR #159/161/162 are different-source analytic specializations, and WP2 PR #160 cubic error certificate cannot be borrowed as a BASS certificate. Original root BASS DAG.json is ACCEL02 and was untouched.',
            'No observed CMB, thermal Compton, resonance line-core/atomic recoil, photo-excitation or doubled Einstein photon stress. Owner KM2N time discretization 40 panels has ~0.0031855 Simpson-vs-trapezoid contrast, not a certified continuum enclosure.',
            '', '## Actual scoped decision',
            'Upper BASS 9/15 (21 edges), KM2 PARTIAL, **zero newly completed upper nodes**. KM2O scoped 1/1 PASS_SCOPED only for SECOND gain SOURCE with original saved owner physics. Not the evolved twice-scattered J2 field. Production=false; merge=false; auto-next=false; native subagent NOT_RUN; independent-author C9 NOT_RUN. Source data SHA256 '+hashlib.sha256(source.read_bytes()).hexdigest()+'.',
            '', 'GitHub CI and Google Drive/Library readback receipt to be appended to Draft PR after actual provider results, not inferred in this generated report.']
    (out/'S2_FINAL_REPORT_KO.md').write_text('\n'.join(lines)+'\n')
    rec=r['GL16']
    hand=['$physmath-research-loop $scispace $exa $wolfram','PROJECT=BASS','REPO=cosmosapjw-quantum/bass',
          'CURRENT_UNIT=KM2O_DOSSIER_VIGILODE_SECOND_THOMSON_POLARIZED_GAIN',
          'CURRENT_PR=298','CURRENT_HEAD='+os.getenv('GITHUB_SHA','READ_LIVE_HEAD_FIRST'),
          'PARENT_PR=297','IMMUTABLE_PARENT_HEAD=4137f942d2a95999f4e6627b71042e98f7afc1b7',
          'READ_LIVE_HEAD_FIRST=true','ORIGINAL_REAL_EINSTEIN_IVPS_RERUN=0',
          'SOURCE_REAL_GL12_GL16_EPOCHS=10','SPECTRAL_ROWS=12000','SCIENTIFIC_PLOTS=6',
          'GL16_SECOND_GAIN_ENERGY_RATE='+str(rec['second_gain_energy_rate']),
          'GL16_SECOND_GAIN_MEAN_POL='+str(rec['second_gain_linear_polarization_mean']),
          'GL16_NORMAL_FREQUENCY_CENTROID='+str(rec['normal_frequency_centroid']),
          'SAVED_HOSTILE_POLARIZED_PAIR_KERNEL='+b['decision'],
          'GL12_GL16_FINAL_SOURCE_FILES=2_NPZ_SHA256',
          'SOURCE_JSON_SHA256='+hashlib.sha256(source.read_bytes()).hexdigest(),
          'NEW_HEAD_CI=READ_ACTUAL_GITHUB_ACTIONS_RUNS',
          'S0_S1_S2_BACKUP=READ_ACTUAL_PROVIDER_SHA256',
          'DROPBOX_DOSSIER=/dossier/BASS_Integrated_Dossier.pdf',
          'VIGILODE_PR159=DIFFERENT_OWNER',
          'VIGILODE_PR161_162=SOURCE_FREE',
          'VIGILODE_WP2_GLOBAL_CI=FAIL_41186142687',
          'UPPER_BASS_DAG=9/15','UPPER_EDGES=21','KM2=PARTIAL',
          'KM2O_SCOPED=1/1_PASS_SCOPED_CONDITIONAL_ON_NEW_HEAD_CI',
          'NEW_COMPLETED_UPPER_NODES=0','VIGILODE_DAG=7/23','REI_CENTRAL_DAG=28/88','REI_WORKING_DAG=33/88',
          'TWICE_SCATTERED_FIELD_J2=NOT_RUN','HIGHER_THOMSON_GAIN=NOT_RUN',
          'RESONANT_LYA_RECOIL=NOT_RUN','THERMAL_COMPTON=NOT_RUN',
          'DISTINCT_AUTHOR_R6_C9=NOT_RUN','NATIVE_SUBAGENT=NOT_RUN',
          'PRODUCTION_READY=false','MERGE_READY=false','AUTO_NEXT=false','STOP_AFTER_ONE_BOUNDED_UNIT=true']
    (out/'HANDOFF_NEXT_KO.txt').write_text('\n'.join(hand)+'\n')
    print('KM2O_GENERATED_REPORT',len(lines),'GL16_GAIN',rec['second_gain_energy_rate'],flush=True)
    return r

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--audit',required=True,type=Path);p.add_argument('--dag',required=True,type=Path);p.add_argument('--outdir',required=True,type=Path)
    a=p.parse_args();emit(a.source,a.audit,a.dag,a.outdir)

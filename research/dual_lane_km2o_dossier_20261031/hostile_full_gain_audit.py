"""Independent source-data second Thomson audit, no BASS RHS nor new gain-code import.

Reconstructs direct angular Thomson pairwise polarized gain on real original
KM2N first-scattered coherency, then verifies saved 2nd source, 4-momentum,
positive eigenvalues and the ten full spectral data epochs. Explicit errors
under normal and python -O (assert statements intentionally not relied upon).
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np

ORIGINAL_SHA={
 12:'ee6d0972a165a515494cfd310e8367cf85886b7ba18da8bb0bb3b34c8f7da8b0',
 16:'3ebce3e3f1f77d2d75452d87dab664e716eda469664cc14cbb489275b02716d5'}

def demand(ok,kind):
    if not bool(ok):raise ArithmeticError('KM2O_HOSTILE_REFEREE_FAIL: '+kind)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def audit(source, output):
    p=Path(source);root=p.parent;d=json.loads(p.read_text())
    demand(d['UPPER_DAG']=='9/15' and d['KM2']=='PARTIAL' and d['new_upper_completed']==0,'DAG')
    demand(d['parent_HEAD']=='4137f942d2a95999f4e6627b71042e98f7afc1b7','PARENT')
    demand(d['new_owner_Einstein_IVPs']==0 and len(d['measurements'])==10,'SCOPED_EPOCH_COUNT')
    extrema={'spectral_bolometric_relative':0.,'centroid_absolute':0.,
             'polarization_absolute':0.,'electron_rest_moment_relative':0.,
             'direct_polarization_amplitude_relative':0.,'gain_momentum_absolute':0.,
             'gain_vs_original_P8_parity':0.}
    positive_10=0
    for rec in d['measurements']:
        grid=int(rec['grid'][2:]);positive_10+=1
        demand(grid in (12,16),'GRID')
        h=np.asarray(rec['spectral_bins'])
        demand(h.shape==(1200,) and np.all(h>=-1e-22),'SPECTRUM_POSITIVE')
        energy=float(rec['second_gain_energy_rate'])
        demand(0<energy and 0<rec['rho_first_photon'],'SOURCE_POSITIVE')
        extrema['spectral_bolometric_relative']=max(extrema['spectral_bolometric_relative'],abs(h.sum()/energy-1))
        centers=np.linspace(-.5+1/2400,.5-1/2400,1200)
        mean=float(centers@h/energy)
        extrema['centroid_absolute']=max(extrema['centroid_absolute'],abs(mean-rec['normal_frequency_centroid']))
        demand(0<=rec['second_gain_linear_polarization_mean']<=1,'POLARIZATION_RANGE')
        demand(rec['rest_frame_elastic_rel_gap']<5e-6 and rec['original_P8_gain_parity_relative']<2e-8,'THOMSON_SOURCE_P8')
        extrema['gain_vs_original_P8_parity']=max(extrema['gain_vs_original_P8_parity'],rec['original_P8_gain_parity_relative'])
    demand(positive_10==10,'TEN_VALIDATED')
    for grid in (12,16):
        rec=[x for x in d['measurements'] if x['grid']==f'GL{grid}' and x['k']==40][0]
        path=root/rec['source_factorized_npz']; demand(path.is_file(),'SAVED_FIRST_AND_SECOND_SOURCE_MISSING')
        demand(sha(path)==rec['source_factorized_SHA256'],'FACTOR_SOURCE_SHA')
        ledger=root.parent/f'dual_lane_km2n_20261031/results/KM2N_FIRST_SOURCE_LEDGER_GL{grid}.npz'
        if not ledger.exists():
            ledger=root.parent.parent/'dual_lane_km2n_20261031/results'/f'KM2N_FIRST_SOURCE_LEDGER_GL{grid}.npz'
        demand(ledger.is_file() and sha(ledger)==ORIGINAL_SHA[grid],'IMMUTABLE_ORIGINAL_KM2N_LEDGER')
        with np.load(path,allow_pickle=False) as r,np.load(ledger,allow_pickle=False) as l:
            x1=r['first_pol_screen_X1'];x2=r['second_gain_pol_screen'];Me=r['electron_rest_source_Me']
            n=r['original_n'];w=r['original_w'];E=r['normal_screen_E'];F=r['eframe_screen_F'];D=r['original_D'];nu=float(r['original_nu_rest'][0])
            sz=grid*grid*2
            demand(x1.shape==(sz,1200,2,2) and x2.shape==x1.shape and Me.shape==(1200,3,3),'ORIGINAL_SPECTRAL_SCREEN_SHAPE')
            demand(np.max(abs(D-l['D'][40]))<2e-14,'ORIGINAL_DOPPLER_IDENTITY')
            demand(np.min(w)>0 and np.min(D)>0 and nu>0,'ORIGINAL_PHYSICAL_RATE')
            # Independent direct incident electron-rest bolometric 3-tensor M.
            x1bol=x1.sum(axis=1)
            X1e=np.einsum('nia,nab,njb->nij',F,x1bol,F,optimize=True)
            M_direct=np.einsum('n,nij->ij',w*D**2,X1e,optimize=True)
            M_stored=Me.sum(axis=0)
            mrel=float(np.max(abs(M_direct-M_stored))/max(np.max(abs(M_stored)),1e-300))
            extrema['electron_rest_moment_relative']=max(extrema['electron_rest_moment_relative'],mrel)
            demand(mrel<8e-12,'DIRECT_ELECTRON_REST_MOMENT')
            # Pairwise polarization amplitude for source outputs on two very different rays,
            # not the P M P factorization used by the implementation.
            for outgoing in (0,sz//2):
                # A_{j,i} = F_out^T F_in, 2x2; sum w_e D^4 A X1 A^T
                A=np.einsum('ia,nib->nab',F[outgoing],F,optimize=True)
                Jpair=np.einsum('n,nai,nij,nbj->ab',w*D**2,A,x1bol,A,optimize=True)*(3/(8*math.pi))
                rest_gain=F[outgoing].T@M_stored@F[outgoing]*(3/(8*math.pi))
                rel=float(np.max(abs(Jpair-rest_gain))/max(np.max(abs(rest_gain)),1e-300))
                extrema['direct_polarization_amplitude_relative']=max(extrema['direct_polarization_amplitude_relative'],rel)
                demand(rel<1e-11,'DIRECT_2x2_POLARIZED_THOMSON_PAIR_KERNEL')
            bol=x2.sum(axis=1)
            tr=np.trace(bol,axis1=-2,axis2=-1)
            tot=float(w@tr)
            demand(abs(tot/rec['second_gain_energy_rate']-1)<3e-12,'GAIN_ENERGY')
            mom=np.einsum('i,ij->j',w*tr,n)
            err=float(np.max(abs(mom-np.asarray(rec['second_gain_normal_momentum']))))
            extrema['gain_momentum_absolute']=max(extrema['gain_momentum_absolute'],err)
            demand(err<3e-15,'FOUR_MOMENTUM_NORMAL_FRAME')
            eigen=np.linalg.eigvalsh((bol+bol.swapaxes(-2,-1))/2)
            demand(eigen.min()>-1e-12*max(eigen.max(),1e-20),'POLARIZED_SCREEN_PSD')
            tr2=np.einsum('nij,nji->n',bol,bol)
            pfrac=np.sqrt(np.maximum(0.,2*tr2-tr*tr))/np.maximum(tr,1e-300)
            polmean=float(np.sum(w*tr*pfrac)/tot)
            extrema['polarization_absolute']=max(extrema['polarization_absolute'],abs(polmean-rec['second_gain_linear_polarization_mean']))
    for name,bound in {'spectral_bolometric_relative':3e-12,'centroid_absolute':2e-12,
                       'polarization_absolute':3e-12,'electron_rest_moment_relative':8e-12,
                       'direct_polarization_amplitude_relative':1e-11,
                       'gain_momentum_absolute':3e-15}.items():
        demand(extrema[name]<bound,'AUDIT_THRESHOLD_'+name)
    receipt={'schema':'bass.km2o.independent_direct_Thomson_pair_v2',
             'source_JSON_SHA256':sha(p),'normal_and_python_O_safe':True,
             'reimported_BASS_rhs':False,'physically_source_backed_snapshots':10,
             'physical_frequency_bins':12000,'max_residuals':extrema,'decision':'PASS_SCOPED'}
    dest=Path(output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(receipt,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print('KM2O_HOSTILE_SAVED_FULL_GAIN',receipt['decision'],positive_10,extrema,flush=True)
    return receipt

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();audit(a.source,a.output)

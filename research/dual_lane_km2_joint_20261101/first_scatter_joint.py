"""KM2 source-owned photon emission time x exactly-one Thomson scatter time.

Scientific scope: Bianchi I / coupled Einstein-P8-Peebles KM2N original tagged Lyalpha photons,
not a complete CMB last-scattering probability, nor an extra gravitational source.
The original finite GL quadrature and Simpson time panels are intentionally unchanged.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'source_inputs'
OUT = HERE / 'results'
ORIGINAL_PARENT_PR = 308
ORIGINAL_KM2N_HEAD = '4137f942d2a95999f4e6627b71042e98f7afc1b7'
VISIBILITY_HEAD = '6a5cb5d0f3b838f757901ee30f991e85dd9e9484'
ORIGINAL_SHA256 = {
 'KM2K_PACKETS_GL12_GLT8.npz':'dc677740685d760120d56badb5e9073c7b14a6eff2803641fc24259ac9df7e03',
 'KM2K_PACKETS_GL16_GLT8.npz':'caaea73af02ba54313acc14d78e41727409879a0d4286528981704ee857036d6',
 'KM2L_THOMSON_OPTICAL_GL12_GLT8.npz':'785239a5ed6712144741e5d11e84e5288217026e884f873a1d54623b8a55b4fd',
 'KM2L_THOMSON_OPTICAL_GL16_GLT8.npz':'9d8dd5b8c638a5ff48c9c743af2cfeb483057f745132346ab259605d12312911',
 'KM2N_FIRST_SOURCE_LEDGER_GL12.npz':'ee6d0972a165a515494cfd310e8367cf85886b7ba18da8bb0bb3b34c8f7da8b0',
 'KM2N_FIRST_SOURCE_LEDGER_GL16.npz':'3ebce3e3f1f77d2d75452d87dab664e716eda469664cc14cbb489275b02716d5',
 'KM2N_ONCE_POL_SCREEN_GL12_U40.npz':'de93bff3abe775092d87f221ce059834d08fec6307b4ac71484213fbf2cd2df2',
 'KM2N_ONCE_POL_SCREEN_GL16_U40.npz':'89fce4ea3c533212648a88e63e2993ab23df0c31fb55f6a6fe9bc276edc08726',
 'KM2N_ONCE_SCATTER_REAL.json':'dcb98647a7c08c5b503a98900a550198ba1c76f10f94b63a570542c41b504ec4',
}
ALPHA = 3.0/(8.0*math.pi)
N_INTERVALS=40
NG_TIME=8
SNAPSHOTS=(8,16,24,32,40)

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def data_inputs(gl):
    if gl not in (12,16): raise ValueError('only original GL12/GL16 source grids')
    names=(f'KM2K_PACKETS_GL{gl}_GLT8.npz',f'KM2L_THOMSON_OPTICAL_GL{gl}_GLT8.npz',
           f'KM2N_FIRST_SOURCE_LEDGER_GL{gl}.npz',f'KM2N_ONCE_POL_SCREEN_GL{gl}_U40.npz')
    for name in names:
        if sha256(SOURCE/name)!=ORIGINAL_SHA256[name]:
            raise ArithmeticError('KM2N original source byte identity failed '+name)
    datasets=[]
    for name in names:
        with np.load(SOURCE/name,allow_pickle=False) as data:
            datasets.append({k:data[k].copy() for k in data.files})
    return datasets

def owner_packets_at_scatter(pack,opacity,ledger,j):
    """Return original incoming Lyalpha packet's bolometric normal-frame energy.

    Incident packet i was originally created at a source Gauss node and has
    undergone zero Thomson collisions until the first collision at t_j.
    """
    if not 0<j<=40: raise ValueError('first scattering must follow emission')
    upto=j*NG_TIME
    red=pack['Rend'][j][None,:]-pack['Rnode'][:upto]
    depth=opacity['tau_edges'][j][None,:]-opacity['tau_nodes'][:upto]
    if np.min(red)<-2e-12 or np.min(depth)<-2e-12:
        raise ArithmeticError('negative original optical age or redshift')
    if np.max(abs(ledger['tau'][j]-opacity['tau_edges'][j]))>1e-10:
        raise ArithmeticError('original redshift/opacity ray owner broken')
    return pack['source_packets'][:upto]*np.exp(-4*red-np.maximum(depth,0.))

def photon_source_moments(pack,opacity,ledger,j):
    """Each original emission node's Thomson electron-rest 3x3 source tensor.

    Me[j,i] = 1/2 sum_in (w_normal D_in^2) p_i->j P^e_in,
    exactly the frequency-integrated KM2N source, including boost D^4,
    rest angular weights w_e=w/D^2 and tilted-screen projectors F F^T.
    """
    p=owner_packets_at_scatter(pack,opacity,ledger,j)
    F=ledger['F'][j]  # N,3,2; same electron-frame screen along original ray
    D=ledger['D'][j]
    w=ledger['w'][j]
    if p.shape[1]!=len(D) or len(w)!=len(D):raise ArithmeticError('original angular ray identity')
    if min(w)<=0 or min(D)<=0:raise ArithmeticError('unphysical original source')
    P=np.einsum('nac,nbc->nab',F,F,optimize=True)
    base=p*(w*D**2)[None,:]
    M=.5*np.einsum('in,nab->iab',base,P,optimize=True)
    # Original emitted packet's log-frequency after drift to first-collision
    # electron frame. The parent 1200-bin histogram approximates this first
    # spectral moment at finite bin resolution; this calculation does not
    # invent Compton thermal frequency redistribution.
    mu_e=(pack['center_D'][:len(p)]-
          (pack['Rend'][j][None,:]-pack['Rnode'][:len(p)])+
          np.log(D)[None,:])
    My=.5*np.einsum('in,nab->iab',base*mu_e,P,optimize=True)
    if np.min(np.linalg.eigvalsh(M)) < -1e-17*np.max(abs(M)):
        raise ArithmeticError('source-injection coherency not positive semidefinite')
    parent=ledger['Me'][j].sum(axis=0)
    gap=np.max(abs(M.sum(axis=0)-parent))/max(np.max(abs(parent)),1e-300)
    if gap>4e-12:raise ArithmeticError(f'frequency-integrated source owner mismatch at {j}: {gap}')
    return M,My,float(gap)

def quantile_weighted(vals,weights,quantile):
    ids=np.argsort(vals,kind='stable')
    vv=np.asarray(vals)[ids]; ww=np.asarray(weights)[ids]
    return float(vv[np.searchsorted(np.cumsum(ww),quantile*sum(ww),side='left')])

def linear_pol(B):
    sym=.5*(B+B.swapaxes(-1,-2))
    eig=np.linalg.eigvalsh(sym)
    trace=np.trace(sym,axis1=-1,axis2=-2)
    deg=(eig[...,1]-eig[...,0])/np.maximum(trace,1e-300)
    if np.min(eig) < -5e-13*max(float(np.max(abs(eig))),1e-300):
        raise ArithmeticError('unphysical source-conditioned polarization')
    return np.clip(deg,0,1),trace

def compute_one(gl,k,pack,opacity,ledger,original_endpoint,scatters):
    if k not in SNAPSHOTS:raise ValueError('invalid original saved observer snapshot')
    U=float(ledger['time'][k]);N=2*gl*gl; h=U/k
    sw=np.array([1 if j in (0,k) else (4 if j%2 else 2) for j in range(k+1)],float)*h/3
    obs_tau=ledger['tau'][k];obs_mu=ledger['mu'][k];wobs=ledger['w'][k]
    tpacket=pack['sample_times']
    joint=np.zeros((k+1,len(tpacket)),float)
    joint_logfrequency=np.zeros_like(joint)
    per_scatter=np.zeros((k+1,N,2,2),float)
    emission_groups=np.zeros((5,N,2,2),float)
    remap_gap=0.;min_positive=math.inf
    bins=np.linspace(0.,.25,6)
    for j in range(1,k+1):
        M,My,mgap=scatters[j]
        remap_gap=max(remap_gap,mgap)
        D=ledger['D'][j];F=ledger['F'][j]
        ratio=obs_mu/ledger['mu'][j]
        age=obs_tau-ledger['tau'][j]
        if np.min(age)<-2e-12 or np.min(ratio)<=0:
            raise ArithmeticError('noncausal source -> observer')
        fac=ALPHA*ledger['nu'][j]*sw[j]*(ratio**4)*np.exp(-np.maximum(age,0.))*D**(-3)
        K=np.einsum('n,nac,nbc->ab',wobs*fac,F,F,optimize=True)
        shift=-np.log(D)+np.log(ratio)
        Ky=np.einsum('n,nac,nbc->ab',wobs*fac*shift,F,F,optimize=True)
        pair=np.einsum('iab,ab->i',M,K,optimize=True)
        pair_y=np.einsum('iab,ab->i',My,K,optimize=True)+np.einsum('iab,ab->i',M,Ky,optimize=True)
        if np.min(pair)<0:raise ArithmeticError('negative source contribution')
        joint[j,:NG_TIME*j]=pair
        joint_logfrequency[j,:NG_TIME*j]=pair_y
        scale=np.einsum('nac,ab,nbd->ncd',F,M.sum(axis=0),F,optimize=True)
        per_scatter[j]=fac[:,None,None]*scale
        for group in range(5):
            mask=(tpacket[:NG_TIME*j]>=bins[group]) & (tpacket[:NG_TIME*j]<bins[group+1])
            if np.any(mask):
                MG=M[mask].sum(axis=0)
                emission_groups[group]+=fac[:,None,None]*np.einsum('nac,ab,nbd->ncd',F,MG,F,optimize=True)
        min_positive=min(min_positive,float(np.min(np.linalg.eigvalsh(M.sum(axis=0)))))
    B=per_scatter.sum(axis=0);total=float(wobs@np.trace(B,axis1=-1,axis2=-2))
    total_joint=float(joint.sum())
    relative_mass=abs(total_joint/total-1)
    if relative_mass>4e-12:raise ArithmeticError('joint tensor energy mismatch')
    pol,trace=linear_pol(B)
    group_values=[]
    for group in range(5):
        X=emission_groups[group]
        pi,tri=linear_pol(X)
        rho=float(wobs@tri)
        group_values.append(dict(source_emission_bin=f'[{bins[group]:g},{bins[group+1]:g})',energy=rho,
             fraction=rho/total,mean_pol=float(wobs@(tri*pi)/rho) if rho>0 else None))
    if np.max(abs(emission_groups.sum(axis=0)-B))/max(np.max(abs(B)),1e-300)>1e-12:
        raise ArithmeticError('source emission group polarized recombination mismatch')
    refs=json.loads((SOURCE/'KM2N_ONCE_SCATTER_REAL.json').read_text())
    ref=None
    case=refs['cases'][f'GL{gl}']
    for x in case['snapshots']:
        if abs(x['u']-U)<1e-13:ref=x;break
    if ref is None:raise ArithmeticError('original snapshot missing')
    energy_gap=abs(total/ref['rho_exactly_one']-1)
    max_screen_rel=None
    if k==40:
        orig=original_endpoint['screen_bolometric_first_one']
        max_screen_rel=float(np.max(abs(B-orig))/max(np.max(abs(orig)),1e-300))
        if max_screen_rel>1e-11:raise ArithmeticError(f'original KM2N screen field mismatch: {max_screen_rel}')
    if energy_gap>1e-11:raise ArithmeticError(f'original J1 photon energy mismatch {energy_gap}')
    approx_centroid=float(np.sum(joint_logfrequency)/total)
    spectral_centroid_gap=abs(approx_centroid-float(ref['mean_logfreq']))
    # Finite 1200-bin normal/electron-frequency binnings approximate the
    # Gaussian source's continuous first log-moment. Do not call byte identity.
    source_freq_edges=np.asarray(original_endpoint['frequency_edges'])
    step=float(source_freq_edges[1]-source_freq_edges[0])
    if spectral_centroid_gap>step/2:raise ArithmeticError('original spectral centroid not reproduced within parent source bin')
    sumrow=joint.sum(axis=1)
    sumcol=joint.sum(axis=0)
    mean_emit=float(sumcol@tpacket/total)
    mean_scatter=float(sumrow@ledger['time'][:k+1]/total)
    var_emit=float(sumcol@(tpacket-mean_emit)**2/total)
    var_scatter=float(sumrow@(ledger['time'][:k+1]-mean_scatter)**2/total)
    mixed=float(sum((tpacket[:NG_TIME*j]@joint[j,:NG_TIME*j])*ledger['time'][j] for j in range(1,k+1))/total)
    cov=float(mixed-mean_emit*mean_scatter)
    corr=float(cov/np.sqrt(var_emit*var_scatter))
    idx_sc=np.where(sumrow>0)[0]
    idx_em=np.where(sumcol>0)[0]
    first=None;out={
        'gl':f'GL{gl}','k':k,'u_obs':U,'rho_exactly_one':total,
        'rho_original':float(ref['rho_exactly_one']),'rho_relative_gap':energy_gap,
        'max_bolometric_screen_gap':max_screen_rel,
        'joint_mass_relative_gap':relative_mass,
        'rest_source_moment_gap':remap_gap,
        'emission_scatter_positive_pairs':int(np.count_nonzero(joint)),
        'mean_emission_time':mean_emit,'mean_scatter_time':mean_scatter,
        'mean_emission_to_scatter_flight':mean_scatter-mean_emit,
        'mean_scatter_to_observer_time':U-mean_scatter,
        'emission_scatter_time_covariance':cov,'emission_scatter_time_correlation':corr,
        'median_emission_time':quantile_weighted(tpacket[idx_em],sumcol[idx_em],.5),
        'median_scatter_time':quantile_weighted(ledger['time'][idx_sc],sumrow[idx_sc],.5),
        'q10_scatter_time':quantile_weighted(ledger['time'][idx_sc],sumrow[idx_sc],.1),
        'q90_scatter_time':quantile_weighted(ledger['time'][idx_sc],sumrow[idx_sc],.9),
        'mean_linear_polarization':float(wobs@(trace*pol)/total),
        'original_mean_linear_polarization':float(ref['mean_linear_polarization']),
        'emission_groups':group_values,
        'source_quantization':'320 Gauss injection time nodes; first collision 40 Simpson source edges',
        'source_and_code_scoped':'SCATTER_ORDER_EXACTLY_ONE_NO_CMB_POSTERIOR',
    }
    out['linear_polarization_relative_difference']=abs(out['mean_linear_polarization']-out['original_mean_linear_polarization'])
    out['source_packet_estimated_mean_logfreq']=approx_centroid
    out['original_binned_mean_logfreq']=float(ref['mean_logfreq'])
    out['finite_frequency_bin_centroid_absolute_gap']=spectral_centroid_gap
    out['emission_group_logfrequency_centroids']=[
         float(np.sum(joint_logfrequency[:,(tpacket>=bins[g])&(tpacket<bins[g+1])])/
               np.sum(joint[:,(tpacket>=bins[g])&(tpacket<bins[g+1])]))
          if np.sum(joint[:,(tpacket>=bins[g])&(tpacket<bins[g+1])])>0 else None
         for g in range(5)]
    return out,joint,joint_logfrequency,B,per_scatter,emission_groups

def run(dest=OUT):
    dest=Path(dest);dest.mkdir(parents=True,exist_ok=True)
    if sha256(SOURCE/'KM2N_ONCE_SCATTER_REAL.json')!=ORIGINAL_SHA256['KM2N_ONCE_SCATTER_REAL.json']:
        raise ArithmeticError('source KM2N summary SHA mismatch')
    records=[];time_pairs=[];ray_rows=[]
    for gl in (12,16):
        pack,opacity,ledger,orig=data_inputs(gl)
        scatters={j:photon_source_moments(pack,opacity,ledger,j) for j in range(1,41)}
        for k in SNAPSHOTS:
            rec,joint,joint_logfrequency,B,Bj,groups=compute_one(gl,k,pack,opacity,ledger,orig,scatters)
            records.append(rec)
            print('KM2_SOURCE_OWNED_FIRST_SCATTER_JOINT',gl,k,rec['rho_exactly_one'],
                  rec['mean_emission_time'],rec['mean_scatter_time'],rec['mean_linear_polarization'],
                  rec['rho_relative_gap'],flush=True)
            js,is_=np.nonzero(joint)
            time_pairs.extend((f'GL{gl}',k,rec['u_obs'],int(j),int(i),float(ledger['time'][j]),
                               float(pack['sample_times'][i]),float(joint[j,i]),float(joint_logfrequency[j,i]),float(joint[j,i]/rec['rho_exactly_one']))
                              for j,i in zip(js,is_))
            for n in range(len(ledger['w'][k])):
                pol,_=linear_pol(B[n:n+1])
                ray_rows.append((f'GL{gl}',k,rec['u_obs'],n,*map(float,ledger['n'][k,n]),
                                 float(np.trace(B[n])),float(pol[0])))
            if k==40:
                np.savez_compressed(dest/f'KM2_FIRST_SCATTER_JOINT_GL{gl}_U40.npz',
                    joint_emission_scatter_energy=joint,joint_logfrequency_energy=joint_logfrequency,emission_time=pack['sample_times'],
                    scattering_time=ledger['time'],screen_first_scattered_bolometric=B,
                    source_binned_screen=groups,source_binned_edges=np.linspace(0,.25,6),
                    original_observer_directions=ledger['n'][k],
                    original_observer_weights=ledger['w'][k],
                    source_sha256=np.asarray([ORIGINAL_SHA256[f'KM2K_PACKETS_GL{gl}_GLT8.npz']]))
    def csv_write(name,head,rows):
        with (dest/name).open('w',newline='') as f:
            writer=csv.writer(f);writer.writerow(head);writer.writerows(rows)
    csv_write('KM2_FIRST_SCATTER_EMISSION_SCATTER_PAIRS.csv',
         ['GL','observer_k','u_observer','scatter_j','emission_i','u_scatter','u_emission','contribution_rho','logfrequency_weighted_rho','normalized_joint_weight'],time_pairs)
    csv_write('KM2_FIRST_SCATTER_OBSERVER_RAYS.csv',
         ['GL','observer_k','u_observer','ray_id','nx','ny','nz','rho_first_scattered_ray','linear_pol_first_scattered_ray'],ray_rows)
    jsout={'schema':'bass.km2.source_owned_exact_one_emission_scatter_joint.v1',
           'source_pr':297,'source_head':ORIGINAL_KM2N_HEAD,'related_visibility_pr':308,
           'visibility_head':VISIBILITY_HEAD,'source_original_byte_hashes':ORIGINAL_SHA256,
           'time_pairs':len(time_pairs),'ray_snapshots':len(ray_rows),'new_Einstein_IVPs':0,
           'reused_owner_Einstein_IVPs':'source_only original KM2N source data',
           'data':records,'upper_dag':'9/15 scoped/source_mapped','new_upper_completed':0,
           'KM2':'PARTIAL','OB1':'PARTIAL',
           'production_ready':False,'merge_ready':False,'auto_next':False,
           'not_implemented':['all-scattering-orders last-scattering distribution','CMB observed likelihood',
                 'thermal Compton or Lyalpha resonant recoil','absolute observer flux calibration',
                 'CE1AS source-equivalent optics','rigorous angular/time continuum error enclosure']}
    (dest/'KM2_FIRST_SCATTER_JOINT_RESULTS.json').write_text(json.dumps(jsout,indent=2,sort_keys=True,allow_nan=False)+'\n')
    return jsout

if __name__=='__main__':
    args=argparse.ArgumentParser();args.add_argument('--output',type=Path,default=OUT)
    run(args.parse_args().output)

"""Source-locked BASS KM2O: reproduce all ten second Thomson gains from immutable KM2N.

No new Einstein/P8 IVPs; physically original GL12/GL16 41-node KM2N photon
source, ray, coherency and Thomson histories. Only instantaneous second gain;
J2 is NOT yet time-propagated or inserted back into Einstein radiation stress.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,os, tempfile
from pathlib import Path
import numpy as np
from research.dual_lane_km2n_20261031.once_scattered import (
    OBS_EPOCHS, remap_logfreq_source_tensor, propagate_one_scatter, NBINS, MID)
from tilted_collision import TiltedThomson

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ORIGINAL_PARENT_SHA='4137f942d2a95999f4e6627b71042e98f7afc1b7'
LEDGER_SOURCE_SHA={
    12:'ee6d0972a165a515494cfd310e8367cf85886b7ba18da8bb0bb3b34c8f7da8b0',
    16:'3ebce3e3f1f77d2d75452d87dab664e716eda469664cc14cbb489275b02716d5',
}
OLD_CSV=HERE/'KM2O_10_PHYSICAL_SECOND_GAIN_EPOCHS.csv'


def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_ledger(grid):
    path=ROOT/f'research/dual_lane_km2n_20261031/results/KM2N_FIRST_SOURCE_LEDGER_GL{grid}.npz'
    if grid not in LEDGER_SOURCE_SHA or sha256(path)!=LEDGER_SOURCE_SHA[grid]:
        raise ArithmeticError('KM2N original source-ledger SHA256 mismatch')
    with np.load(path,allow_pickle=False) as z:
        if z['Me'].shape!=(41,1200,3,3) or z['time'].shape!=(41,) or z['F'].shape[1]!=grid*grid*2:
            raise ArithmeticError('original finite-sample electron-rest angular source missing')
        arr={name:z[name].copy() for name in z.files}
    return [dict(time=float(arr['time'][i]), Me=arr['Me'][i],F=arr['F'][i],
                 D=arr['D'][i],nu=float(arr['nu'][i]),mu=arr['mu'][i],
                 tau=arr['tau'][i],w=arr['w'][i],n=arr['n'][i],E=arr['E'][i],
                 reference_gain_rate=float(arr['source_gain_rate'][i]))
            for i in range(41)]


def physics_at(grid,k,sources, *,save_field=None):
    if grid not in LEDGER_SOURCE_SHA or k not in OBS_EPOCHS:
        raise ValueError('only source-locked original GL12/16 observation times')
    obs=sources[k]; n=obs['n']; w=obs['w'];D=obs['D'];E=obs['E'];F=obs['F'];nu=obs['nu']
    with tempfile.TemporaryDirectory(prefix=f'km2o_gl{grid}_{k}_') as tmp:
        ephemeral=Path(tmp)/'once.npz'
        once=propagate_one_scatter(sources,k,save_field=ephemeral)
        with np.load(ephemeral,allow_pickle=False) as z:
            X1=z['screen_spectral_first_one'].copy()
    if X1.shape!=(2*grid*grid,NBINS,2,2):
        raise ArithmeticError('wrong original physical spectral coherecy shape')
    if k==40:
        owner=ROOT/f'research/dual_lane_km2n_20261031/results/KM2N_ONCE_POL_SCREEN_GL{grid}_U40.npz'
        with np.load(owner,allow_pickle=False) as z:
            if not np.array_equal(X1,z['screen_spectral_first_one']):
                owner_arr=z['screen_spectral_first_one']
                mismatch=np.abs(X1-owner_arr)
                scale=max(float(np.max(np.abs(owner_arr))),1e-300)
                gap=float(np.max(mismatch))
                rel=gap/scale
                fraction=float(np.count_nonzero(X1!=owner_arr))/X1.size
                raise ArithmeticError('actual KM2N first-scattered screen identity mismatch '
                                      f'max_abs={gap:.17e} relative_max={rel:.17e} '
                                      f'nonidentical_fraction={fraction:.17e} '
                                      f'finite={np.isfinite(X1).all() and np.isfinite(owner_arr).all()}')
    coef=np.linalg.lstsq(np.column_stack((np.ones(len(n)),-n)),D,rcond=None)[0]
    gamma=coef[0]; beta=coef[1:]/gamma
    if not 0<=np.dot(beta,beta)<1:raise ArithmeticError('unphysical electron tilt')
    op=TiltedThomson(n,w,beta)
    if max(np.max(np.abs(op.D-D)),np.max(abs(np.einsum('nij,nja->nia',op.S,E)-F)))>3e-10:
        raise ArithmeticError('electron boost/screen source identity mismatch')
    Xe,gap1=remap_logfreq_source_tensor(X1,np.log(D))
    Xe=Xe*D[:,None,None,None]**4
    # electron-rest first scattered spectral coherency tensor, not a scalar opacity surrogate
    Me=np.einsum('n,nia,nbac,njc->bij',op.we,F,Xe,F,optimize=True)
    Ge=3/(8*math.pi)*np.einsum('nia,bij,njc->nbac',F,Me,F,optimize=True)
    X2,gap2=remap_logfreq_source_tensor(nu*D[:,None,None,None]**(-3)*Ge,-np.log(D))
    B=X2.sum(axis=1); tr=np.trace(B,axis1=1,axis2=2)
    gain=float(w@tr)
    loss_by_ray=nu*D*np.trace(X1.sum(axis=1),axis1=1,axis2=2)
    loss=float(w@loss_by_ray)
    rest_in=float(np.einsum('n,nb->',op.we,np.trace(Xe,axis1=2,axis2=3)))
    rest_out=float(np.einsum('n,nb->',op.we,np.trace(Ge,axis1=2,axis2=3)))
    rest_gap=abs(rest_out/rest_in-1)
    J1=np.einsum('nia,nab,njb->nij',E,X1.sum(axis=1),E,optimize=True)
    original=nu*op.D*np.trace(op.gain(J1),axis1=1,axis2=2)
    parity=float(np.max(np.abs(tr-original))/max(np.max(abs(original)),1e-300))
    if min(gain,loss,rest_in,rest_out)<=0 or parity>2e-8 or rest_gap>5e-6 or max(gap1,gap2)>3e-11:
        raise ArithmeticError('physical Thomson energy, parity or frequency source failed')
    # Real 2x2 polarization on original final screen, not a fictitious global Q/U orientation.
    eigen=np.linalg.eigvalsh((B+B.swapaxes(-1,-2))/2)
    if eigen.min() < -3e-13*max(1e-20,eigen.max()):
        raise ArithmeticError('unphysical negative outgoing polarization eigenvalue')
    tr2=np.einsum('nij,nji->n',B,B)
    pol=np.sqrt(np.maximum(0.,2*tr2-tr**2))/np.maximum(tr,1e-300)
    polmean=float((w*tr)@pol/gain)
    if not 0<=polmean<=1+1e-12:raise ArithmeticError('polarization outside [0,1]')
    hist=np.einsum('n,nb->b',w,np.trace(X2,axis1=2,axis2=3))
    centroid=float(MID@hist/gain)
    second=float(MID**2@hist/gain)
    momentum=np.einsum('n,ni->i',w*tr,n)
    loss_momentum=np.einsum('n,ni->i',w*loss_by_ray,n)
    if abs(hist.sum()/gain-1)>1e-11:raise ArithmeticError('second gain spectral sum mismatch')
    out=dict(grid=f'GL{grid}',k=int(k),u=float(obs['time']),
          rho_first_photon=float(once['rho_exactly_one']),
          second_gain_energy_rate=gain,first_scatter_loss_rate=loss,
          second_gain_linear_polarization_mean=polmean,
          second_gain_linear_polarization_max=float(pol.max()),
          normal_frequency_centroid=centroid,
          frequency_sigma_logbin=math.sqrt(max(0.,second-centroid**2)),
          rest_frame_elastic_rel_gap=rest_gap,
          original_P8_gain_parity_relative=parity,
          frequency_first_remap_error=float(gap1),frequency_second_remap_error=float(gap2),
          spectral_bins=hist.tolist(),second_gain_normal_momentum=momentum.tolist(),
          first_loss_normal_momentum=loss_momentum.tolist(),
          original_source_ledger_SHA256=LEDGER_SOURCE_SHA[grid],
          source_electron_beta=beta.tolist(),
          new_owner_Einstein_IVPs=0)
    if save_field:
        dest=Path(save_field);dest.parent.mkdir(exist_ok=True,parents=True)
        np.savez_compressed(dest,first_pol_screen_X1=X1,second_gain_pol_screen=X2,
            electron_rest_source_Me=Me, original_n=n, original_w=w,
            normal_screen_E=E, eframe_screen_F=F, original_D=D,
            original_nu_rest=np.asarray([nu]), log_frequency_edges=np.linspace(-.5,.5,1201))
        out['source_factorized_npz']=dest.name
        out['source_factorized_SHA256']=sha256(dest)
    return out


def run_all(destination):
    dest=Path(destination); dest.parent.mkdir(parents=True,exist_ok=True)
    measurements=[]
    for grid in (12,16):
        sources=source_ledger(grid)
        for k in OBS_EPOCHS:
            path=dest.parent/f'KM2O_SECOND_GAIN_GL{grid}_U{k}.npz' if k==40 else None
            rec=physics_at(grid,k,sources,save_field=path)
            measurements.append(rec)
            print('KM2O_FULL_REAL_SCIENCE',grid,k,rec['second_gain_energy_rate'],
                  rec['second_gain_linear_polarization_mean'],rec['normal_frequency_centroid'],flush=True)
    if len(measurements)!=10 or sum(len(m['spectral_bins']) for m in measurements)!=12000:
        raise ArithmeticError('not 10 source-backed spectra and 12000 actual bins')
    # The prior local full 10-epoch source table is an independent numerical witness;
    # do not silently overwrite or replace it with less accurately matched data.
    with OLD_CSV.open(newline='') as f:original=list(csv.DictReader(f))
    if len(original)!=10:raise ArithmeticError('historical ten-epoch original source CSV missing')
    for now,old in zip(measurements,original):
        if now['grid']!=old['grid'] or abs(now['u']-float(old['u']))>1e-15:
            raise ArithmeticError('original 10 science epoch identity mismatch')
        for field in ('second_gain_energy_rate','second_gain_linear_polarization_mean','normal_frequency_centroid'):
            value=now[field]; expected=float(old[field])
            error=abs(value-expected)/max(abs(expected),1e-12)
            if error>3e-10:
                raise ArithmeticError('genuine original 10-epoch source discrepancy: '+field)
    data={'schema':'bass.km2o.original_bianchi_second_thomson_full_gain.v2',
          'parent_PR':297,'parent_HEAD':ORIGINAL_PARENT_SHA,
          'source':'immutable KM2N 41-node original Einstein-P8-Peebles original GL12/GL16 fields',
          'spectrum_bins_per_epoch':NBINS,'actual_physics_epoch_count':10,
          'actual_frequency_rows':12000,'new_owner_Einstein_IVPs':0,
          'scoped_status':'NUMERICALLY_CHECKED_NOT_FULL_TWICE_SCATTERED_FIELD',
          'UPPER_DAG':'9/15','KM2':'PARTIAL','new_upper_completed':0,
          'no_second_field_time_propagation':True,
          'production_ready':False,'merge_ready':False,'auto_next':False,
          'measurements':measurements}
    dest.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+'\n')
    return data

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();run_all(a.output)

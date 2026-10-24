"""Frozen one-cohort angular sweep. No trajectories or source integration."""
from pathlib import Path
import json
import numpy as np
import angular_cohort as ac
ROOT=Path(__file__).resolve().parents[1];TARGET=ROOT/'results/COHORT_SWEEP.json'

def write(out):TARGET.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')

def main():
    out=dict(status='RUNNING',dtype='float64',new_IVPs=0,old_campaign_replay=0,fixtures=[],rotation=[],axial={})
    grids={n:ac.sphere_rule(n) for n in [16,32,64]}
    for label,S in ac.SOURCES.items():
        for eta in ac.ETAS:
            C=ac.transport(eta);refs={str(n):ac.moments(S,C,*grids[n]) for n in grids};ref=refs['64']
            row=dict(source=label,eta=eta,S=S.tolist(),C=C.tolist(),reference=refs,
                reference16_32=ac.errors(refs['16'],refs['32']),reference32_64=ac.errors(refs['32'],ref),
                ideal_node_truncation=ac.truncation_bound(C),minimum_birth_q=float(1+np.linalg.eigvalsh(S)[0]),
                minimum_directional_log_expansion=float(np.min(ac.A+eta*np.diag(ac.B))),rules={})
            for name in ['Q14','Q26']:
                value=ac.moments(S,C,*ac.rule(name));lead=ac.leading(label,name)
                signed_e=value['F']-ref['F'];signed_p=np.array(value['P'])-ref['P']
                entry=dict(moments=value,errors=ac.errors(value,ref),signed_energy_error=signed_e,signed_pressure_error=signed_p.tolist(),leading=lead,packet=ac.packet_check(S,C,name))
                if eta>0:
                    ec=lead['energy_coefficient'];pc=np.array(lead['pressure_coefficient'])
                    entry['leading_energy_ratio']=signed_e/(ec*eta**lead['energy_power'])
                    entry['leading_pressure_ratio']=signed_p[np.unravel_index(np.argmax(np.abs(pc)),pc.shape)]/(pc[np.unravel_index(np.argmax(np.abs(pc)),pc.shape)]*eta**lead['pressure_power'])
                    entry['leading_energy_relative_difference']=abs(entry['leading_energy_ratio']-1)
                    entry['leading_pressure_relative_difference']=float(np.max(np.abs(signed_p/eta**lead['pressure_power']-pc)))/float(np.max(np.abs(pc)))
                    entry['leading_energy_status']='RESOLVED' if entry['errors']['energy']>ac.RESOLUTION else 'ROUNDING_UNRESOLVED'
                    entry['leading_pressure_status']='RESOLVED' if entry['errors']['pressure']>ac.RESOLUTION else 'ROUNDING_UNRESOLVED'
                row['rules'][name]=entry
            if eta==1:
                octant=ac.octant_reference(S,C);row['octant32']=octant;row['octant_full_error']=ac.errors(octant,ref)
            out['fixtures'].append(row);write(out)
        C=ac.transport(1.);rotS=ac.O@S@ac.O.T;rotC=ac.O@C@ac.O.T
        rotref=ac.moments(rotS,rotC,*grids[64]);base=next(r for r in out['fixtures'] if r['source']==label and r['eta']==1)
        O4=np.eye(4);O4[1:,1:]=ac.O
        rr=dict(source=label,reference=rotref,reference_covariance_error=ac.tensor_difference(rotref['T'],O4@np.array(base['reference']['64']['T'])@O4.T)/rotref['F'],rules={})
        for name in ['Q14','Q26']:
            n,w=ac.rule(name);fixed=ac.moments(rotS,rotC,n,w);co=ac.moments(rotS,rotC,n@ac.O.T,w)
            cov=O4@np.array(base['rules'][name]['moments']['T'])@O4.T
            rr['rules'][name]=dict(fixed_moments=fixed,co_rotated_moments=co,
                fixed_grid_errors=ac.errors(fixed,rotref),aligned_errors=base['rules'][name]['errors'],
                co_rotation_error=ac.tensor_difference(co['T'],cov)/rotref['F'],
                fixed_orientation_difference=ac.tensor_difference(fixed['T'],cov)/rotref['F'])
        out['rotation'].append(rr);write(out)
    C=np.diag(np.exp([-.15,-.15,.3]));exact=ac.axial_oracle()
    out['axial']=dict(C=C.tolist(),oracle=exact,references={str(n):ac.moments(np.zeros((3,3)),C,*grids[n]) for n in grids})
    out['axial']['errors']={n:ac.errors(v,exact) for n,v in out['axial']['references'].items()}
    out['axial']['ideal_node_truncation']=ac.truncation_bound(C)
    out['normalization']=dict(a=ac.A,n_b_m3=ac.NB,D=ac.D,L_m=1.,Pstar_SI=ac.PSTAR,energy_J=ac.CARD.energy_J,alphaL=ac.SCALE.density_factor,rho_star=ac.RHOSTAR)
    out['status']='COMPLETED';write(out)
    print(json.dumps(dict(output=str(TARGET),fixtures=len(out['fixtures']),rotation_fixtures=len(out['rotation']),new_IVPs=0)))

if __name__=='__main__':main()

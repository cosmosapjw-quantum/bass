#!/usr/bin/env python3
"""Source TypeII photon kinematics, monotonicity and finite line-band diagnostics.
No closed cosmological populations or global escape factor are claimed.
"""
import ast,csv,json,math,subprocess
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp,quad
from scipy.interpolate import PchipInterpolator
from scipy.special import wofz
from line_transfer import *
HERE=Path(__file__).resolve().parent
PARENT='232c033cb961fc3d4f5a98760ea27c834b8b0b55'
def extract(path,name,env):
 fs=[v for v in ast.parse(path.read_text()).body if isinstance(v,ast.FunctionDef) and v.name==name]
 check(len(fs)==1,'source function '+name);exec(compile(ast.Module(body=fs,type_ignores=[]),str(path),'exec'),env)
def main():
 paths=['compiler/validation/generate_typeii_fixture.py','compiler/validation/typeii_fixture_canonical.json','research/typeii_hyrec2_history_20261102/EXTENDED_TYPEII_HYREC2_RAY_26.csv','research/typeii_hyrec2_history_20261102/typeii_extended_window.py','research/typeii_cascade_effective_20261116/SOURCE_TRACE_STATIONARY.csv','research/typeii_native_hyrec_expansion_20261102/R3_TYPEII_HUBBLE_GRID.json']
 locks={}
 for p in paths:
  a=subprocess.check_output(['git','rev-parse',PARENT+':'+p],cwd=ROOT,text=True).strip();b=subprocess.check_output(['git','hash-object',str(ROOT/p)],text=True).strip()
  check(a==b,'parent drift '+p);locks[p]=a
 ns={'np':np,'math':math,'sqrt3':np.sqrt(3)};extract(ROOT/paths[0],'typeii_rhs',ns);ns['rhs']=ns['typeii_rhs'];extract(ROOT/paths[3],'system',ns)
 rhs=ns['rhs'];system=ns['system'];orig=json.loads((ROOT/paths[1]).read_text())['trajectory']['samples'];x0=np.array(orig[0]['state'])
 old=np.genfromtxt(ROOT/paths[2],delimiter=',',names=True).reshape(26,1167);to=old['tau_H'][0];dirs=np.stack((old['n_x'][:,0],old['n_y'][:,0],old['n_z'][:,0]),axis=1)
 H0=json.loads((ROOT/paths[5]).read_text())['H_anchor_source_FLRW_s_inverse'];y0=np.r_[x0,np.log(H0),np.column_stack((dirs,np.zeros(26))).ravel()]
 sol=solve_ivp(system,(0.,float(to[-1])),y0,method='DOP853',rtol=3e-12,atol=5e-14,max_step=.003,dense_output=True);check(sol.success,'original geometry integration')
 yn=sol.sol(to);rr=yn[6:].T.reshape(1167,26,4);parentdirs=np.stack((old['n_x'],old['n_y'],old['n_z']),axis=-1)
 raygap=float(np.max(abs(rr[:,:,:3].transpose(1,0,2)-parentdirs)));egap=float(np.max(abs(rr[:,:,3].T-old['ln_E_normal'])))
 bgap=float(np.max(abs(sol.sol([r['tau'] for r in orig])[:5].T-np.array([r['state'] for r in orig]))))
 check(max(raygap,egap,bgap)<2e-10,'original state/ray overlap')
 def logEa(t):
  y=sol.sol(t);n=y[6:].reshape(26,4);b=y[4];return n[:,3]+np.log((1-b*n[:,1])/np.sqrt(1-b*b))
 derivgap=0.
 for tt in np.linspace(.01,float(to[-1])-.01,19):
  hh=1e-5;fd=(logEa(tt-2*hh)-8*logEa(tt-hh)+8*logEa(tt+hh)-logEa(tt+2*hh))/(12*hh);y=sol.sol(tt)
  d=drift(y[:5],rhs(list(y[:5]),1.3),y[6:].reshape(26,4)[:,:3]);derivgap=max(derivgap,float(max(abs(fd+d['kappa']))))
 check(derivgap<5e-9,'atom frequency logarithmic derivative')
 tr=np.genfromtxt(ROOT/paths[4],delimiter=',',names=True);t=tr['tau_H'];y=sol.sol(t);st=y[:5].T;nr=y[6:].T.reshape(len(t),26,4);hn=np.exp(y[5]);G0=1/np.sqrt(1-x0[4]**2)
 # Explicit density scale for the parent's fixed-ne stationary tracer, not
 # a claim of cosmological electron neutrality or a population re-solve.
 nt=11.223846333047e-6*.0224*(1-.245)*1e6*(1+tr['z_mean'])**3*G0*np.sqrt(1-st[:,4]**2)
 nl=nt*tr['p1s'];nu=nt*tr['p2p'];dn=GRATIO*nl-nu;check(min(dn)>0,'source line inversion')
 dd=[drift(s,rhs(list(s),1.3),nr[i,:,:3]) for i,s in enumerate(st)];kap=np.array([d['kappa'] for d in dd]);D=np.array([d['D'] for d in dd]);bounds=np.array([d['all_sky_lower_bound'] for d in dd]);hr=hn[:,None]*kap/D
 check(np.min(kap)>0,'source rays nonmonotonic')
 tau=ALYA*(C/NU0)**3*dn[:,None]/(8*np.pi*hr);ps=sobolev(tau)
 eps=np.sqrt(2*KB*tr['Tm_K']/(MH*C*C));a=ALYA/(4*np.pi*NU0*eps)
 ratevar=np.maximum.reduce([abs(PchipInterpolator(t,np.log(nl)).derivative()(t)),abs(PchipInterpolator(t,np.log(nu)).derivative()(t)),abs(PchipInterpolator(t,np.log(hn)).derivative()(t))])
 crossing=40*eps[:,None]/kap;variation=crossing*ratevar[:,None]
 wingfrac=eps[:,None]*a[:,None]*tau/np.pi
 tail20=np.array([quad(lambda x:np.real(wofz(x+1j*v))/np.sqrt(np.pi),20,np.inf,epsabs=3e-13,epsrel=2e-10)[0] for v in a]);missing=tau*tail20[:,None]
 with (HERE/'DIRECTIONAL_LINE_DIAGNOSTICS.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['source_index','ray','tau_H','z_mean','D','kappa','H_atom_path_s','formal_sobolev_tau','formal_sobolev_P','crossing_40_Doppler_tauH','source_variation_indicator_20','formal_missing_red_wing_tau_20','formal_tau1_fractional_frequency','all_sky_lower_bound'])
  for i in range(len(t)):
   for j in range(26):w.writerow([i,j,t[i],tr['z_mean'][i],D[i,j],kap[i,j],hr[i,j],tau[i,j],ps[i,j],crossing[i,j],variation[i,j],missing[i,j],wingfrac[i,j],bounds[i]])
 bands=[];probes=[];numbergap=energygap=0.
 for zz in (1700.,1392.,1100.,800.,300.):
  i=int(np.argmin(abs(tr['z_mean']-zz)));bandprobes=[]
  for X in (6.,20.,80.):
   g=line_grid(float(tr['Tm_K'][i]),halfwidth=X,cells=int(16*X));flows=[]
   for j in range(26):
    fb=float(planck(H*g['nu_edges'][-1]/(KB*float(tr['Tn_K'][i])*D[i,j])))
    q=frozen_steady(g,nl[i],nu[i],float(tr['Tm_K'][i]),hr[i,j],fb)
    numbergap=max(numbergap,abs(q['number_residual'])/q['gross_number']);energygap=max(energygap,abs(q['energy_residual'])/(E0*q['gross_number']))
    flows.append(q['red_out']);bands.append([tr['z_mean'][i],j,X,g['band_mass'],fb,q['red_out'],q['blue_in'],q['red_out']-q['blue_in'],q['net_line_emission'],q['geometric_redshift_work']])
   bandprobes.append({'halfwidth_Doppler':X,'profile_mass':g['band_mass'],'all_ray_red_out_range':[float(min(flows)),float(max(flows))]})
  probes.append({'z_mean':float(tr['z_mean'][i]),'n_lower_trace_m3':float(nl[i]),'n_upper_trace_m3':float(nu[i]),'kappa_range':[float(min(kap[i])),float(max(kap[i]))],'Hray_over_Hn_range':[float(min(kap[i]/D[i])),float(max(kap[i]/D[i]))],'formal_tau_range':[float(min(tau[i])),float(max(tau[i]))],'formal_P_range':[float(min(ps[i])),float(max(ps[i]))],'missing_symmetric_red_wing_tau_20_range':[float(min(missing[i])),float(max(missing[i]))],'formal_tau1_fractional_frequency_range':[float(min(wingfrac[i])),float(max(wingfrac[i]))],'source_variation_20_range':[float(min(variation[i])),float(max(variation[i]))],'finite_band':bandprobes})
 check(max(numbergap,energygap)<2e-12,'finite-volume number/energy source ledger')
 with (HERE/'FINITE_LINE_BAND_FLUXES.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['z_mean','ray','halfwidth_Doppler','profile_mass','f_blue','red_out_4pi_equiv_m3_s','blue_in_4pi_equiv_m3_s','boundary_net_m3_s','collision_net_m3_s','redshift_work_J_m3_s']);w.writerows(bands)
 # Exactly replace the parent imposed-bath Lya edge. Other parent channels
 # remain unchanged. This is a local source interface, not new dynamics.
 i=int(np.argmin(abs(tr['z_mean']-1100)));net=cascade.network(float(tr['Tn_K'][i]),float(tr['Tm_K'][i]),float(tr['beta'][i]),float(tr['ne_m3'][i]))
 pp=np.array([tr[k][i] for k in ('p1s','p2s','p2p','p3s','p3p','p3d','pion')]);pp[2]*=1.2;pp/=sum(pp)
 g=line_grid(float(tr['Tm_K'][i]),halfwidth=20,cells=320);occ=np.exp(cascade.bf.log_nbar(H*g['nu'],float(tr['Tn_K'][i]),float(tr['beta'][i])))
 linked=attach_cascade(net,pp,g,occ,float(tr['Tm_K'][i]),nt[i]);old=cascade.energy(net,pp)
 dE=float(cascade.ENERGY@linked['population_derivative_proper'])*nt[i];oldF=linked['removed_old_flux_per_atom']*nt[i]
 ph=old['photon_energy_J_s']*nt[i]-E0*oldF+linked['line']['photon_energy'];kin=old['electron_kinetic_J_s']*nt[i]+linked['line']['kinetic_energy']
 linkerr=float(abs(dE+ph+kin)/(old['gross_energy_J_s']*nt[i]+linked['line']['gross_energy']));check(linkerr<2e-12,'cascade edge-replacement energy')
 result={'parent_head':PARENT,'input_Git_blobs':locks,'source_states':len(t),'directional_records':len(t)*26,'finite_band_records':len(bands),'original_401_state_gap':bgap,'original_1167x26_direction_gap':raygap,'original_normal_logE_gap':egap,'atom_log_frequency_derivative_gap':derivgap,'all_sky_lower_bound_sampled_min':float(min(bounds)),'actual_kappa_range':[float(np.min(kap)),float(np.max(kap))],'finite_volume_number_max_relative_residual':numbergap,'finite_volume_energy_max_relative_residual':energygap,'cascade_replace_energy_relative_residual':linkerr,'source_probes':probes,'density_scope':'fixed-ne parent stationary tracer scaled by nHrest; not closed cosmic baryon/charge evolution','angular_scope':'26 source characteristics; each flux is 4pi-equivalent per ray, not an all-sky quadrature','escape_scope':'formal equal-profile Sobolev and symmetric-Voigt wing audit; finite-band exits are not global escape','transport_scope':'frozen local narrow-line photon count; global geometric dilution/angular focusing and full redistribution not solved','new_xe_or_tau_prediction':False}
 (HERE/'SOURCE_LINE_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
 print('GEOMETRY',json.dumps({k:result[k] for k in ('source_states','directional_records','atom_log_frequency_derivative_gap','all_sky_lower_bound_sampled_min','actual_kappa_range','finite_volume_number_max_relative_residual','finite_volume_energy_max_relative_residual','cascade_replace_energy_relative_residual')}))
 for i in (0,2,4):print('PROBE',json.dumps(probes[i]))
if __name__=='__main__':main()

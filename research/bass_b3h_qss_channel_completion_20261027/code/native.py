"""Transcription of the pinned original HyRec coefficient routines only.

No history integration, source exporter, validation snapshot, or old result
program is imported. Temperatures are source energies k_B T in eV; nH cm^-3.
"""
import math
import re
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'inputs/native_source'
def constants():
    text=(SOURCE/'hydrogen.h').read_text()
    names=['EI','E21','E31','E41','E32','E42','hPc','mH','kBoltz','L2s1s','TR_MIN','TR_MAX','NTR','NTM','TM_TR_MIN','TM_TR_MAX','EFFECT_A','EFFECT_B','EFFECT_C','EFFECT_D','DIFFUSION']
    c={k:float(re.search(r'^#define\s+'+k+r'\s+([\d.eE+\-]+)',text,re.M)[1]) for k in names}
    if any(c[k]!=1 for k in ['EFFECT_A','EFFECT_B','EFFECT_C','EFFECT_D','DIFFUSION']):raise ValueError('frozen source switches changed')
    return c

def weights(f):
    return [f*(f-1)*(2-f)/6,(1+f)*(1-f)*(2-f)/2,(1+f)*f*(2-f)/2,(1+f)*f*(f-1)/6]
def dweights(f):return [(-3*f*f+6*f-2)/6,(3*f*f-4*f-1)/2,(-3*f*f+2*f+2)/2,(3*f*f-1)/6]

class Rates:
    def __init__(self,c):
        self.c=c
        raw=np.loadtxt(SOURCE/'Alpha_inf.dat').reshape(100,40,2)
        self.raw=raw.transpose(2,1,0)
        self.logs=np.array([[[math.log(float(v)) for v in row] for row in level] for level in self.raw])
        self.rraw=np.loadtxt(SOURCE/'R_inf.dat');self.lr=np.array([math.log(float(v)) for v in self.rraw])
        a,b=math.log(c['TR_MIN']),math.log(c['TR_MAX']);h=(b-a)/99
        self.log_grid=[a+i*h for i in range(100)];self.dlog=self.log_grid[1]-self.log_grid[0]
        h=(c['TM_TR_MAX']-c['TM_TR_MIN'])/39
        self.ratio_grid=[c['TM_TR_MIN']+i*h for i in range(40)];self.dt=self.ratio_grid[1]-self.ratio_grid[0]
    def stencil(self,TR,TM):
        c=self.c;q=TM/TR
        if not c['TR_MIN']<=TR<=c['TR_MAX'] or not c['TM_TR_MIN']<=q<=c['TM_TR_MAX']:raise ValueError('native rate table domain')
        tm=max(1,min(37,math.floor((q-c['TM_TR_MIN'])/self.dt)))
        tr=max(1,min(97,math.floor((math.log(TR)-math.log(c['TR_MIN']))/self.dlog)))
        f=(q-c['TM_TR_MIN'])/self.dt-tm;g=(math.log(TR)-math.log(c['TR_MIN']))/self.dlog-tr
        return tm,tr,f,g
    def evaluate(self,TR,TM):
        tm,tr,f,g=self.stencil(TR,TM);w1,w2=weights(f),weights(g);dw=dweights(f)
        alpha=[];equilibrium=[];derivative=[];temps=[]
        for l in range(2):
            temp=[]
            for k in range(4):
                v=self.logs[l,tm-1+k,tr-1:tr+3]
                temp.append(float(v[0])*w2[0]+float(v[1])*w2[1]+float(v[2])*w2[2]+float(v[3])*w2[3])
            loga=temp[0]*w1[0]+temp[1]*w1[1]+temp[2]*w1[2]+temp[3]*w1[3]
            alpha.append(math.exp(loga));derivative.append(sum(temp[k]*dw[k] for k in range(4))/(self.dt*TR))
            v=self.logs[l,39,tr-1:tr+3]
            equilibrium.append(math.exp(float(v[0])*w2[0]+float(v[1])*w2[1]+float(v[2])*w2[2]+float(v[3])*w2[3]));temps.append(temp)
        factor=3.016103031869581e21*TR*math.sqrt(TR)*math.exp(-.25*self.c['EI']/TR)
        beta=[equilibrium[0]*factor,equilibrium[1]*(factor/3.)]
        v=self.lr[tr-1:tr+3];mix=math.exp(float(v[0])*w2[0]+float(v[1])*w2[1]+float(v[2])*w2[2]+float(v[3])*w2[3])
        return dict(Alpha=alpha,DAlpha=[alpha[i]-equilibrium[i] for i in range(2)],Alpha_equilibrium=equilibrium,Beta=beta,R2p2s=mix,dlogAlpha_dTm=derivative,
          interpolation=dict(iTM=tm,iTR=tr,frac_TM=f,frac_logTR=g,DTM_TR=self.dt,DlogTR=self.dlog,temp_log_alpha_rows=temps,partial_derivative_holds_TR=True))

def read_twog(c):
    a=np.loadtxt(SOURCE/'two_photon_tables.dat')
    if a.shape!=(311,5):raise ValueError('native311 rows required')
    total=0.
    for b in range(140):total+=float(a[b,2])
    factor=c['L2s1s']/total
    for b in range(140):a[b,2]*=factor
    return a,dict(sequential_A2s_sum_before=total,normalization_factor=factor,range=[0,140],switches='all A/B/C/D/diffusion=1')

def radiative(TR,twog,c):
    Tvr=np.zeros((2,311));Trv=np.zeros((2,311))
    for b in range(311):
        E,A1,A2,A3,A4=map(float,twog[b]);db=math.exp((E-c['E21'])/TR)
        Tvr[0,b]=-A2/abs(math.exp((E-c['E21'])/TR)-1.)
        Trv[0,b]=Tvr[0,b]*db
        Tvr[1,b]=-math.exp(-c['E32']/TR)/3.*A3/abs(math.exp((E-c['E31'])/TR)-1.)-math.exp(-c['E42']/TR)/3.*A4/abs(math.exp((E-c['E41'])/TR)-1.)
        Trv[1,b]=Tvr[1,b]*3.*db
    return Tvr,Trv

def validate_diffusion(up,dn):
    if np.any(np.asarray(up)<0) or np.any(np.asarray(dn)<0):raise ValueError('negative native diffusion coefficient')

def diffusion(TM,twog,c):
    if not TM>0:raise ValueError('positive source Tm required')
    E=twog[:,0];A1=twog[:,1];up=np.zeros(311);dn=np.zeros(311);DE=c['E21']*c['E21']*2.*TM/c['mH']
    b=100;up[b]=DE/(E[b+1]-E[b])**2*A1[b]
    for b in range(101,139):
        dn[b]=math.exp((E[b]-E[b-1])/TM)*up[b-1]
        up[b]=(DE*A1[b]-(E[b]-E[b-1])**2*dn[b])/(E[b+1]-E[b])**2
    b=139;dn[b]=math.exp((E[b]-E[b-1])/TM)*up[b-1]
    up[b]=(DE*A1[b]-(E[b]-E[b-1])**2*dn[b])/(c['E21']-E[b])**2
    p_dn=math.exp((c['E21']-E[b])/TM)/3.*up[b]
    b=179;dn[b]=DE/(E[b]-E[b-1])**2*A1[b]
    for b in range(178,140,-1):
        up[b]=math.exp((E[b]-E[b+1])/TM)*dn[b+1]
        dn[b]=(DE*A1[b]-(E[b+1]-E[b])**2*up[b])/(E[b]-E[b-1])**2
    b=140;up[b]=math.exp((E[b]-E[b+1])/TM)*dn[b+1]
    dn[b]=(DE*A1[b]-(E[b+1]-E[b])**2*up[b])/(E[b]-c['E21'])**2
    p_up=math.exp((c['E21']-E[b])/TM)/3.*dn[b]
    validate_diffusion(up,dn)
    return up,dn,float(p_up),float(p_dn)

def steady_tm(knot,c,packet):
    st=knot['inherited_completed_inverse_values'];xe=1-st['x1s'];H=st['H_s_inv']
    TR_K=packet['constants_from_prior_packet']['T0_K']*(1+knot['native_z'])
    Y=packet['constants_from_prior_packet']['Y'];fHe=Y/(1-Y)/3.97153
    # Original rec_Tmss source operation order, fsR=meR=1.
    TM_K=TR_K/(1+H/4.91466895548409e-22/TR_K/TR_K/TR_K/TR_K*(1+xe+fHe)/xe)
    return dict(Tm_eV=c['kBoltz']*TM_K,TR_K=TR_K,Tm_K=TM_K,fHe=fHe,xe=xe,
      local_guard_deficit=1-TM_K/TR_K,guard_limit=5e-4,source='history.c::rec_Tmss; no whole-prefix branch claim')

def populate(knot,TM,twog,c,rates):
    st=knot['inherited_completed_inverse_values'];x1=st['x1s'];xe=xH=1-x1;TR=st['TR_eV'];nh=st['nH_cm3'];H=st['H_s_inv']
    s=3.016103031869581e21*TR*math.sqrt(TR)*math.exp(-c['EI']/TR)/nh;Dx=xe*xH-s*x1
    RL=4.662899067555897e15*H/nh/x1
    rt=rates.evaluate(TR,TM);A,DA,B,mix=[rt[n] for n in ['Alpha','DAlpha','Beta','R2p2s']]
    incoming=knot['incoming_virtual'];lya,lyb=knot['incoming_lyman_alpha_beta']
    Trr=np.array([[B[0]+3*mix+3*RL*(1.664786871919931*math.exp(-c['E32']/TR)+1.953125*math.exp(-c['E42']/TR)),-mix],[-3*mix,B[1]+mix+RL]])
    line_in=np.array([3*RL*x1*1.664786871919931*lyb,3*RL*x1*lya])
    continuum_source=np.array([nh*(s*x1*DA[i]+A[i]*Dx) for i in range(2)])
    sr=continuum_source+line_in
    Tvr,Trv=radiative(TR,twog,c);pre_vr=Tvr.copy();pre_rv=Trv.copy()
    for b in range(311):Trr[0,0]-=Tvr[0,b];Trr[1,1]-=Tvr[1,b]
    up,dn,pup,pdn=diffusion(TM,twog,c);Trr[1,1]+=pdn+pup
    Tvv=np.zeros((3,311));tau=np.zeros(311);sv=np.zeros(311);gamma=np.zeros(311);P=np.zeros(311)
    for b in range(311):
        gamma[b]=-(Trv[0,b]+Trv[1,b])+up[b]+dn[b]
        if (100<=b<139) or (140<b<180):Tvv[1,b]=-up[b-1];Tvv[2,b]=-dn[b+1]
        if b==139:Tvv[1,b]=-up[b-1];Tvr[1,b]-=pdn;Trv[1,b]-=up[b]
        if b==140:Tvv[2,b]=-dn[b+1];Tvr[1,b]-=pup;Trv[1,b]-=dn[b]
        lam=c['hPc']/float(twog[b,0]);tau[b]=gamma[b]*x1*lam**3*nh/8/math.pi/H
        P[b]=1-(1-math.exp(-tau[b]))/tau[b] if tau[b]>1e-6 else tau[b]/2-tau[b]**2/6
        Tvv[0,b]=gamma[b]/P[b] if tau[b]>0 else 2/(x1*lam**3*nh/8/math.pi/H)
        sv[b]=Tvv[0,b]*x1*incoming[b]*(1-P[b])
    xr=np.array([x1*st['ys_beta'],x1*st['yp']]);xv=x1*np.array(knot['average_virtual']);q=x1*math.exp(-c['E21']/TR)*np.array([1.,3.]);pop=xr+q
    channels={
      'bound_free':continuum_source-np.array(B)*xr,
      'real_state_mixing':np.array([mix*(xr[1]-3*xr[0]),mix*(3*xr[0]-xr[1])]),
      'Lyalpha':np.array([0.,line_in[1]-RL*xr[1]]),
      'Lybeta_gamma':np.array([line_in[0]-3*RL*(1.664786871919931*math.exp(-c['E32']/TR)+1.953125*math.exp(-c['E42']/TR))*xr[0],0.]),
      'two_photon_Raman':np.array([math.fsum(float(pre_vr[i,b]*xr[i]-pre_rv[i,b]*xv[b]) for b in range(311)) for i in range(2)]),
      'line_center_core_diffusion':np.array([0.,up[139]*xv[139]+dn[140]*xv[140]-(pup+pdn)*xr[1]])}
    return dict(index=knot['index'],Tm=TM,TR=TR,nH_cm3=nh,H_s_inv=H,x1s=x1,xHII=xH,xe=xe,saha_s=s,Dxe2=Dx,RLya=RL,rates=rt,
      Trr=Trr,Trv=Trv,Tvr=Tvr,Tvv=Tvv,sr=sr,sv=sv,Gamma=gamma,Dtau=tau,one_minus_P=P,Aup=up,Adn=dn,A2p_up=pup,A2p_dn=pdn,
      xr=xr,xv=xv,Wien_shift_q=q,absolute_population=pop,line_source=line_in,continuum_source=continuum_source,channels=channels,
      two_photon_pre_diffusion_Tvr=pre_vr,two_photon_pre_diffusion_Trv=pre_rv,
      two_photon_Raman_each_bin=pre_vr*xr[:,None]-pre_rv*xv[None,:],
      virtual_diffusion_neighbor_source=-Tvv[1]*np.r_[0.,xv[:-1]]-Tvv[2]*np.r_[xv[1:],0.])

def solve_virtual(Tvv,rhs):
    d,lower,upper=Tvv;rhs=np.asarray(rhs);out=np.empty_like(rhs);a=np.zeros(311);g=np.empty_like(rhs);denoms=np.empty(311)
    if not d[0]>0:raise ValueError('nonpositive first Thomas denominator')
    denoms[0]=d[0];a[0]=upper[0]/d[0];g[0]=rhs[0]/d[0]
    for i in range(1,311):
        denoms[i]=d[i]-lower[i]*a[i-1]
        if not denoms[i]>0:raise ValueError('nonpositive native Thomas denominator')
        a[i]=upper[i]/denoms[i];g[i]=(rhs[i]-lower[i]*g[i-1])/denoms[i]
    out[-1]=g[-1]
    for i in range(309,-1,-1):out[i]=g[i]-a[i]*out[i+1]
    return out,denoms

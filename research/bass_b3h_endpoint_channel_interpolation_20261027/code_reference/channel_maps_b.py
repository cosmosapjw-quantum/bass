"""New absolute physical gross maps built only from admitted saved operands."""
from mp_b import *

def build(op,knot,c,NH):
    g=op['x1s'];TR=op['TR'];nh=op['nH_cm3'];H=op['H_s_inv'];R0=m(c['LYA_FACT'])*H/(NH/m(10**6))/g
    E=c['energies'];E21=c['E21'];n=311
    A=[[-x for x in row] for row in op['two_photon_pre_diffusion_Tvr']]
    B=[[-x for x in row] for row in op['two_photon_pre_diffusion_Trv']]
    up,dn=op['Aup'],op['Adn'];C=[op['Tvv'][0][b]-op['Gamma'][b] for b in range(n)]
    check('positive virtual C escape coefficients',min(C)>0,min(C))
    diag=[C[b]+B[0][b]+B[1][b]+up[b]+dn[b] for b in range(n)]
    lower=[ZERO]*n;upper=[ZERO]*n
    for b in list(range(100,139))+list(range(140,179)):
        lower[b+1]=-up[b];upper[b]=-dn[b+1]
    emission=[[A[i][b] for i in range(2)] for b in range(n)]
    for b,key,reverse in [(139,'A2p_dn',up[139]),(140,'A2p_up',dn[140])]:
        emission[b][1]+=op[key]
    discrepancy=[abs(diag[b]-op['Tvv'][0][b])/max(abs(diag[b]),abs(op['Tvv'][0][b])) for b in range(n)]
    check('conservative virtual diagonal source reassembly',max(discrepancy)<=m('5e-14'),max(discrepancy),m('5e-14'))
    fin=[knot['incoming_virtual'][b]+mp.exp(-E[b]/TR) for b in range(n)]
    source=[C[b]*g*fin[b] for b in range(n)]
    solved,den=thomas(diag,lower,upper,[[source[b]]+emission[b] for b in range(n)])
    av=[row[0] for row in solved];bv=[row[1:] for row in solved]
    check('positive absolute virtual intercept and response',min(av)>=0 and min(x for row in bv for x in row)>=0)
    # Directed diffusion-only reference currents d=-Tdiff*q.
    qr=op['Wien_shift_q'];qv=op['virtual_Wien_shift'];dr=[ZERO,ZERO];dv=[ZERO]*n
    for b,key,reverse in [(139,'A2p_dn',up[139]),(140,'A2p_up',dn[140])]:
        J=op[key]*qr[1]-reverse*qv[b];dr[1]-=J;dv[b]+=J
    for b in list(range(100,139))+list(range(140,179)):
        J=up[b]*qv[b]-dn[b+1]*qv[b+1];dv[b]-=J;dv[b+1]+=J
    dsol,_=thomas(diag,lower,upper,[[x] for x in dv]);Trv=mp.matrix(op['Trv'])
    cd=mp.matrix(dr)-Trv*mp.matrix([x[0] for x in dsol])
    # Independent native departure→absolute shift, on the reassembled V.
    fullsource=[]
    for b in range(n):
        Vq=diag[b]*qv[b]+(lower[b]*qv[b-1] if b else 0)+(upper[b]*qv[b+1] if b+1<n else 0)
        fullsource.append(op['sv'][b]+dv[b]+sum(op['Tvr'][i][b]*qr[i] for i in range(2))+Vq)
    shift_discrep=[abs(fullsource[b]-source[b])/max(abs(fullsource[b]),abs(source[b]),m('1e-100')) for b in range(n)]
    maps=[]
    def add(name,kind,a,ell,stoich,energy):
        a=a/R0;ell=[x/R0 for x in ell]
        if a<0 or min(ell)<0:raise ValueError('negative gross affine map '+name)
        maps.append(dict(name=name,kind=kind,a=a,ell=ell,stoich=stoich,energy_eV=energy))
    # Energy order atomic, gas, ambient radiation, selected Lyalpha.
    def en(atom=ZERO,gas=ZERO,ambient=ZERO,line=ZERO):return [atom,gas,ambient,line]
    def orientation(name,kind,a,ell,nu,ee):add(name,kind,a,ell,nu,ee)
    for i in range(2):
        chi=c['EI']-E21;kr=op['energy']['Krec_eV'][i];ki=op['energy']['Kion_eV'][i];nu=[0,0,0,-1];nu[1+i]=1
        ell=[ZERO,ZERO];ell[i]=op['rates']['Beta'][i]
        add(f'recombination_{i}','bound_free',nh*op['xe']*op['xHII']*op['rates']['Alpha'][i],[ZERO,ZERO],nu,en(-chi,-kr,chi+kr))
        add(f'ionization_{i}','bound_free',ZERO,ell,[-x for x in nu],en(chi,ki,-chi-ki))
    mix=op['rates']['R2p2s'];add('mix_s_to_p','mixing',ZERO,[3*mix,ZERO],[0,-1,1,0],en());add('mix_p_to_s','mixing',ZERO,[ZERO,mix],[0,1,-1,0],en())
    for i in range(2):
        for b in range(n):
            nu=[1,0,0,0];nu[1+i]=-1;ell=[ZERO,ZERO];ell[i]=A[i][b]
            add(f'radiative_{i}_{b}_down','two_photon_Raman',ZERO,ell,nu,en(-E21,ZERO,E21))
            add(f'radiative_{i}_{b}_up','two_photon_Raman',B[i][b]*av[b],[B[i][b]*x for x in bv[b]],[-x for x in nu],en(E21,ZERO,-E21))
    for b,key,reverse in [(139,'A2p_dn',up[139]),(140,'A2p_up',dn[140])]:
        ee=en(-E21,E21-E[b],E[b]);nu=[1,0,-1,0]
        add(f'core_{b}_down','core_diffusion',ZERO,[ZERO,op[key]],nu,ee)
        add(f'core_{b}_up','core_diffusion',reverse*av[b],[reverse*x for x in bv[b]],[-x for x in nu],[-x for x in ee])
    for b in list(range(100,139))+list(range(140,179)):
        delta=E[b+1]-E[b];ee=en(ZERO,-delta,delta)
        add(f'virtual_{b}_to_{b+1}','virtual_diffusion',up[b]*av[b],[up[b]*x for x in bv[b]],[0,0,0,0],ee)
        add(f'virtual_{b+1}_to_{b}','virtual_diffusion',dn[b+1]*av[b+1],[dn[b+1]*x for x in bv[b+1]],[0,0,0,0],[-x for x in ee])
    for name,coef,gap,Eline,departure in [('beta',m(1.664786871919931),c['E32'],c['E31'],knot['incoming_lyman_alpha_beta'][1]),('gamma',m(1.953125),c['E42'],c['E41'],ZERO)]:
        k=3*R0*coef*mp.exp(-gap/TR);rin=3*R0*coef*g*(departure+mp.exp(-Eline/TR));nu=[1,-1,0,0]
        add(name+'_down','Lybeta_gamma',ZERO,[k,ZERO],nu,en(-E21,ZERO,E21))
        add(name+'_up','Lybeta_gamma',rin,[ZERO,ZERO],[-x for x in nu],en(E21,ZERO,-E21))
    bn=mp.matrix([ZERO,ZERO]);Mn=mp.zeros(2)
    for ch in maps:
        nu=mp.matrix(ch['stoich'][1:3]);bn+=nu*ch['a'];Mn-=nu*mp.matrix([ch['ell']])
    M=Mn.copy();M[1,1]+=1;K=M**-1;col=[sum(M[i,j] for i in range(2)) for j in range(2)];eig=mp.eig(M,left=False,right=False)
    check('constant activity M signs and positive contraction',M[0,1]<=0 and M[1,0]<=0 and min(col)>0 and min(eig)>0,[M,col,eig])
    check('nonnegative activity forcing intercept',min(bn)>=0,bn)
    return dict(Ralpha0=R0,saved_native_Ralpha0=op['RLya'],Ralpha_relative_difference=(R0-op['RLya'])/R0,
      virtual_C=C,virtual_diag=diag,virtual_lower=lower,virtual_upper=upper,virtual_source=source,
      virtual_a=av,virtual_B=bv,virtual_Thomas_denominators=den,virtual_reassembly_entry_relative=discrepancy,
      absolute_positive_source_vs_native_shift_relative=shift_discrep,diffusion_only_d_real=dr,diffusion_only_d_virtual=dv,c_diff=cd,
      full_affine_Wien_shift_real=op['absolute_source_shift_real'],full_affine_Wien_shift_virtual=op['absolute_source_shift_virtual'],
      maps=maps,b_nonLya=bn,M_nonLya=Mn,M=M,K=K,gamma=min(col),eigenvalues=eig,
      model='left non-Lya maps/Ralpha0 frozen in actual activity time; literal absolute diffusion; saved right operator is diagnostic only')

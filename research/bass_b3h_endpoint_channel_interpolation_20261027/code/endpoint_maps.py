"""Raw proper-rate endpoint maps, preserving positive kernel energy tags."""
from mp_b import *
from right_map_source import build_right_normalized

def lifted_channel(ch,scale):
    return dict(name=ch['name'],kind=ch['kind'],a=m(ch['a'])*scale,ell=[m(x)*scale for x in ch['ell']],stoich=list(ch['stoich']),energy_eV=[m(x) for x in ch['energy_eV']])
def aggregate(channels):
    b=mp.matrix([0,0]);M=mp.zeros(2)
    for ch in channels:
        nu=mp.matrix(ch['stoich'][1:3]);b+=nu*ch['a'];M-=nu*mp.matrix([ch['ell']])
    return b,M
def prepare(data):
    prior=data['prior'];ops=data['ops'];packet=data['source_packet'];c=data['constants']
    saved_R0=m(prior['endpoint_maps']['Ralpha0'])
    left=[lifted_channel(ch,saved_R0) for ch in prior['endpoint_maps']['maps']]
    # This is the ONLY physical endpoint-map construction in the new unit.
    # The normalized helper's NH parameter is a proper density, not V0 stock.
    right_proper_density=ops[1]['nH_cm3']*m(10**6)
    right_source=build_right_normalized(ops[1],packet['knots'][1],c,right_proper_density)
    R1=right_source['Ralpha0'];right=[lifted_channel(ch,R1) for ch in right_source['maps']]
    if len(left)!=1414 or len(right)!=1414:raise ValueError('endpoint map cardinality changed')
    for ch0,ch1 in zip(left,right):
        if any(ch0[k]!=ch1[k] for k in ['name','kind','stoich']):raise ValueError('endpoint source tag/stoichiometry mismatch')
        for ch in [ch0,ch1]:
            if ch['a']<0 or min(ch['ell'])<0:raise ValueError('negative endpoint proper-rate map')
            if abs(sum(ch['energy_eV']))>ARITH*max(norm(ch['energy_eV']),m('1e-100')):raise ValueError('tagged endpoint energy sum mismatch')
    b0,M0=aggregate(left);b1,M1=aggregate(right)
    check('raw endpoint proper-rate maps and matched positive tags',True,dict(channels=1414,tags=2828,left_builder_calls=0,right_builder_calls=1))
    def representation(channels):
        bscale=sum(norm(mp.matrix(ch['stoich'][1:3]))*abs(ch['a']) for ch in channels)
        Mscale=sum(norm(mp.matrix(ch['stoich'][1:3]))*max(abs(x) for x in ch['ell']) for ch in channels)
        return dict(b=ARITH*bscale,M=ARITH*Mscale,meaning='declared MP restoration/aggregation allowance on actual gross coefficient scales, conditional on admitted source values')
    return dict(left=left,right=right,b0=b0,b1=b1,M0=M0,M1=M1,delta_b=b1-b0,delta_M=M1-M0,
      coefficient_representation_errors=[representation(left),representation(right)],
      saved_left_Ralpha0=saved_R0,right_normalization_Ralpha1=R1,right_normalization_proper_nH_m3=right_proper_density,
      left_origin='saved1414 activity maps multiplied by saved Ralpha0; no left construction',right_source_diagnostics=right_source,
      energy_choice='endpoint-tagged positive kernel mixture (1-theta)e0*j0+theta*e1*j1; e(theta)*j(theta) cross model not selected',
      left_builder_calls=0,right_builder_calls=1,interior_virtual_solves=0)

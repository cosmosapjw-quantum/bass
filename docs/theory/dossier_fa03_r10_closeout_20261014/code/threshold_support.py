"""Exact-arithmetic source-support diagnostic, NOT a physical photoionization solver.

A conserved source count/mean-energy pair is not enough to preserve the
ionization-inactive support of a below-threshold emitter when projected to nodes.
Only guaranteed leakage is asserted when ALL actual emitted energies are below chi.
"""
from __future__ import annotations
from fractions import Fraction
import json, argparse

class EvidenceHold(ValueError):
    pass


def F(x):
    if isinstance(x, bool):
        raise EvidenceHold('HOLD_BOOLEAN_NOT_ENERGY')
    if isinstance(x, float):
        raise EvidenceHold('HOLD_FLOAT_INPUT_USE_EXACT_DECIMAL_OR_FRACTION')
    try:
        z=Fraction(str(x))
    except (ValueError, ZeroDivisionError) as e:
        raise EvidenceHold('HOLD_NON_RATIONAL_INPUT') from e
    return z


def evaluate(threshold_eV, source_support_min_eV, source_support_max_eV,
             source_mean_eV, node_energy_eV, node_weights):
    chi,mn,mx,em=map(F,[threshold_eV,source_support_min_eV,source_support_max_eV,source_mean_eV])
    if not (0<chi and 0<mn<=em<=mx):
        raise EvidenceHold('HOLD_MISSING_OR_INVALID_SOURCE_SUPPORT')
    if not isinstance(node_energy_eV,(list,tuple)) or not isinstance(node_weights,(list,tuple)) or len(node_energy_eV)!=len(node_weights) or not node_energy_eV:
        raise EvidenceHold('HOLD_NODES_OR_WEIGHTS')
    en=list(map(F,node_energy_eV));wt=list(map(F,node_weights))
    if any(v<=0 for v in en) or any(w<0 for w in wt):
        raise EvidenceHold('HOLD_NEGATIVE_WEIGHT_OR_ENERGY')
    if sum(wt,F(0))!=1:
        raise EvidenceHold('HOLD_PHOTON_COUNT_NOT_CONSERVED')
    if sum((w*v for w,v in zip(wt,en)),F(0))!=em:
        raise EvidenceHold('HOLD_SOURCE_FIRST_ENERGY_MOMENT_NOT_CONSERVED')
    active=sum((w for w,v in zip(wt,en) if v>=chi),F(0))
    if mx<chi:
        verdict='PROVEN_SUBTHRESHOLD_SUPPORT_LEAKAGE' if active>0 else 'PASS_SUPPORT_PRESERVATION_FOR_THIS_INPUT'
    elif mn<chi<=mx:
        verdict='MIXED_SOURCE_SUPPORT_UNRESOLVED';
    else:
        verdict='SOURCE_NOT_SUBTHRESHOLD'
    return {'status':verdict,'count_conserved':True,'first_energy_moment_conserved':True,
            'threshold_eV':str(chi),'source_support_eV':[str(mn),str(mx)],
            'source_mean_eV':str(em),'above_threshold_node_weight':str(active),
            'active_node_basis':'>= threshold','scope':'exact discrete support diagnostic, not weighted cross-section rate, abundance or thermal error',
            'photoionization_error':None,'abundance_error':None,'science_admission':'NOT_ISSUED'}


def demo():
    return evaluate('24.59','23','23','23',['20','30'],['7/10','3/10'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--demo',action='store_true');p.add_argument('--json',type=str)
    args=p.parse_args()
    if args.json: print(json.dumps(evaluate(**json.loads(args.json)),ensure_ascii=False,indent=2))
    else: print(json.dumps(demo(),ensure_ascii=False,indent=2))

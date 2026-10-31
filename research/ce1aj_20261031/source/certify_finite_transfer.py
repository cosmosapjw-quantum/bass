#!/usr/bin/env python3
"""CE1AJ exact-rational constants for a continuum finite-u dark-source bound."""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
import json,sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'ce1ai_20261031'/'source'))
import ce1ai_source_response as source
import certify_dark_initial_jet as prior

def certify():
    source.validate_immutable()
    old=prior.certify()
    E0=F(old['source_E0_exact'])
    ds=F(old['initial_shear_x_minus_y_exact'])
    ss=[F.from_float(float(x)) for x in source.SHEAR]
    assert F(899,1000)<E0<F(901,1000)<1 and sum(ss)==0
    Hsq=(E0+sum(s*s for s in ss)/2)/3
    assert F(55,100)**2<Hsq<F(56,100)**2
    assert F(56,100)+F(1,5)+F(901,1000)*F(2,25)<1
    assert E0*(1-4*F(2,25))>F(3,5)
    assert F(89,100)**2<F(35,44)
    # Using pi < 22/7 and sqrt(35/44)>89/100:
    jetupper=-F(1296,203)*ds/E0*F(3,8)*F(89,100)
    assert jetupper < -F(3,4)
    T=sum(abs(F(int(v),406)) for v in source.DARK_INTEGER.ravel())
    assert T==F(512,203) and T<3
    # E>3/5; |E'|<4, |E''|<34; N=M's baseline counterpart.
    # |f|<=3, |f'|<=14, |f''|<=400; |M|,|M'|,|M''|<9,78,1842.
    assert F(34)/F(3,5)**2+2*F(4)**2/F(3,5)**3<250
    assert 6*F(4)**2/F(3,5)**4+2*34/F(3,5)**3<1100
    m=1842*2+2*78*12+9*250
    ns=(614*3+2*26*12+3*102)*3+2*(26*3+3*12)*38+9*1100
    assert m==7806 and ns==26880 and 13*(m+ns)<455000
    # Linearized self-consistent geometry:
    # D'<=K, K'<=6K+8D+3 => D<=(9/2)u^2 for u<=.08.
    assert 1/(1-8*F(2,25))<3 and 13*(20+6)<350
    quad=F(455000,2)+3*350*F(9,2)
    assert quad==232225 and -F(3,4)+quad*F(1,1000000)<-F(1,2)
    return {
        'schema':'bass.ce1aj.finite_continuum_dark_alpha42.v1',
        'parent_pr':288,
        'parent_head':'06a89b70200c09e44711235ef6d01a0b797b2a03',
        'original_source_sha256':source.ORIGINAL_SOURCE_SHA,
        'source_signed_total_variation':str(T),
        'initial_jet_strict_upper_rational':str(jetupper),
        'certified_u_range':['0','1/1000000'],
        'claim':'for every 0<u<=1e-6, d_epsilon alpha42(u)|0 < -u/2',
        'comparison':'d_epsilon alpha42(u)|0 < -3u/4+232225*u^2',
        'quadratic_remainder_coefficient':str(quad),
        'finite_time_full_horizon_rank_certified':False,
        'numerical_GL_used_in_proof':False,
        'independent_author_R6_C9':'NOT_RUN',
        'upper_DAG':'9/15','CE1':'PARTIAL','new_upper_nodes':0,
        'production_ready':False,'merge_ready':False,'auto_next':False
    }

if __name__=='__main__':
    cert=certify()
    out=HERE.parent/'data';out.mkdir(parents=True,exist_ok=True)
    (out/'CE1AJ_CONTINUUM_FINITE_TRANSFER_CERTIFICATE.json').write_text(json.dumps(cert,indent=2)+'\n')
    print('CE1AJ_RATIONAL_COMPARISON_PASS',cert['claim'])

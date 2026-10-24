"""Source-only bridge to pinned, unchanged detached REC LINE01 owner."""
from itertools import product
import json
import math
from pathlib import Path
import sys
import numpy as np
from event_measure import Identity, PhotonEventMeasure, GrossEventBundle, real_array

ROOT = Path(__file__).resolve().parents[1]
REC = ROOT/'vendor/rec_line_source'
sys.path.insert(0,str(REC/'code'))
import line_source as owner
import escape_moments as angular

OWNER = 'REC_LINE01@93e1bdc8298db9a7c16f77d4bf64985a0c3f25aa:standalone_detached'
ORIGIN_FRAME = 'rest'
INVARIANT_CLOCK = 'proper_time_dt_dV_invariant'


def native_scalar_state(S):
    raw = json.loads((REC/'fixtures/STORED_NATIVE_LYA_STATE.json').read_text())
    m = {k:float(v) for k,v in raw['meta'].items()}
    if m['fsR'] != 1 or m['meR'] != 1:
        raise ValueError('frozen native scalar extract requires fsR=meR=1')
    xr = next(float(r['departure']) for r in raw['real_rows'] if r['index']=='1')
    w = math.exp(-10.198714553953742/m['TR_eV_rescaled'])
    x2p = xr+3*m['x1s']*w
    nH = m['nH_cm3']*1e6
    f = 1/math.expm1(10.198714553953742/m['TR_eV_rescaled'])+m['Dfplus_Lya']
    S = real_array(S,'S',(3,3))
    state = owner.LineState('H_LYA_EFFECTIVE_2P','collapsed_2p',nH*m['x1s'],nH*x2p,m['H_sInv'],f,S,
                            'STORED_NATIVE_SCALAR_EXTRACT; detached full-Planck/stimulated; NOT native LINE02/history parity',
                            'CONSTRUCTED_S_FIXTURE_NOT_NATIVE_ANGULAR_STATE',n_H_reference_m3=nH)
    return state, {'x2p_restored':x2p,'native_xr1':xr,'Planck_Wien_factor':w,'f_plus_total':f,
                   'source_snapshot_blob':raw['source_git_blob_sha1'],'new_native_solver_calls':0}


def event_bundle(state, identity, *, n_mu=12,n_phi=20):
    if not isinstance(state,owner.LineState) or not isinstance(identity,Identity) or identity.owner != OWNER:
        raise ValueError('selected compatible detached LINE01 owner required')
    if identity.frame != ORIGIN_FRAME or identity.clock != INVARIANT_CLOCK:
        raise ValueError('REC source construction requires canonical rest frame and invariant proper clock')
    owner.validate_owner(state.owner_mode,state.native_line_owner_active)
    # Reject bool/complex before unchanged donor's scalar/tensor conversions.
    real_array(state.S,'S',(3,3))
    c = state.card
    t = c.A_s_inv*c.wavelength_m**3*(c.g*state.n_l_m3-state.n_u_m3)/(8*math.pi*state.H_s_inv)
    data = angular.validate_inputs(t,state.S)
    n2, weights = angular._principal_rule(n_mu,n_phi)
    q = 1+n2@data.eigenvalues
    beta = angular.beta_vector(t,q)
    signs = np.array(list(product((-1.,1.),repeat=3)))
    principal = (np.sqrt(n2)[:,None,:]*signs[None,:,:]).reshape(-1,3)
    directions = principal@data.eigenvectors.T
    angular_rates = np.repeat(weights*beta/8,8)
    down = c.A_s_inv*state.n_u_m3*(1+state.f_plus)*angular_rates
    up = c.A_s_inv*c.g*state.n_l_m3*state.f_plus*angular_rates
    energy = np.full(len(down),c.energy_J)
    return GrossEventBundle(PhotonEventMeasure(energy,directions,down,identity),
                           PhotonEventMeasure(energy,directions,up,identity))

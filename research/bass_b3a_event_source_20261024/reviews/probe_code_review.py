"""New targeted reviewer probes for source identity and transfer-token semantics."""
import json
from dataclasses import replace
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from event_measure import Identity
from rec_adapter import owner,OWNER,event_bundle
from bass_binding import attach_source
state=owner.state_at_depth('H_LYA_EFFECTIVE_2P','emission',3.7,np.zeros((3,3)))
identity=Identity(OWNER,'reviewer_epoch','rest','proper_time_dt_dV_invariant','CONSTRUCTED_REVIEW_FIXTURE')
observations=[]
kwargs=dict(length_m=1e12,pressure=[0.,0.],pi=np.zeros((2,3,3)),transfer_id='physical_event_1',positive_domain=lambda rates: True)
for field,value in [('clock','ln_a'),('frame','already_boosted')]:
    bad=replace(identity,**{field:value})
    try:
        bundle=event_bundle(state,bad,n_mu=2,n_phi=2)
        attachment=attach_source(bundle,expected_identity=bad,**kwargs)
        observations.append(dict(id='F1_'+field,status='ACCEPTED_WRONG_SOURCE_METADATA',identity=bad.__dict__,U=attachment.rates.U.tolist(),expected='ValueError before source construction'))
    except ValueError as e:
        observations.append(dict(id='F1_'+field,status='REFUSED',error=str(e)))
bundle=event_bundle(state,identity,n_mu=2,n_phi=2)
first=attach_source(bundle,expected_identity=identity,**kwargs)
moved=bundle.boosted([.2,0,0],frame='other_observer')
try:
    second=attach_source(moved,expected_identity=moved.down.identity,applied_transfer_keys=first.applied_transfer_keys,**kwargs)
    observations.append(dict(id='F2_frame_duplicate',status='ACCEPTED_SAME_PHYSICAL_TOKEN_IN_NEW_FRAME',first_keys=sorted(first.applied_transfer_keys),second_keys=sorted(second.applied_transfer_keys),expected='ValueError: same owner/epoch/physical transfer token'))
except ValueError as e:
    observations.append(dict(id='F2_frame_duplicate',status='REFUSED',error=str(e)))
print(json.dumps({'scope':'three new contract probes; no IVP/old replay; synthetic successful callbacks only','observations':observations},indent=2))

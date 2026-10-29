"""Repropagate the immutable CE1-G MPFR192 per-panel evidence under CE1-H lemma.

This does NOT rerun the expensive CE1-G source/whole-panel residual computations.
Archive byte hash and every member SHA/CRC are checked before use. The archived
per-panel bounds are treated as previously computed proof obligations, not new
independent machine verification. No parent source is modified.
"""
import hashlib,json,zipfile,os
from pathlib import Path
from bianchi.nonperturbative.einstein_interval import Interval,propagate_interval
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from bianchi.nonperturbative.einstein_tabulated_sharp import initial_continuum_pressure_cap

ROOT=Path(__file__).resolve().parent
ZIP=Path(os.environ.get('BASS_CE1G_ARCHIVE', ROOT.parent.parent/'parent'/'BASS_CE1G_FINAL_20261029.zip'))
EXPECTED='8657f6e7ad51b516896c0a9988644b12790b6cdc48372e14945f8232c4942448'
assert hashlib.sha256(ZIP.read_bytes()).hexdigest()==EXPECTED
with zipfile.ZipFile(ZIP) as z:
 assert z.testzip() is None
 manifest=json.loads(z.read('MANIFEST.json'))
 for path,record in manifest['payloads'].items():
  raw=z.read(path)
  assert len(raw)==record['bytes']
  assert hashlib.sha256(raw).hexdigest()==record['sha256']
 old=json.loads(z.read('research/ce1g_20261029/evidence/SCIENCE_RESULTS.json'))
 print('PARENT_PAYLOAD_SHA_VERIFIED',len(manifest['payloads']),flush=True)

s=TabulatedRadiation([0,.5,1],[0,.25,.75,1],[[.1,.25,.05],[.2,.15,.15]],backend='python_oracle')
cert=initial_continuum_pressure_cap(s)
rows=[]
for record in old:
 assert record['status']=='SCOPED_MPFR_TABULATED_COMPUTED_PATH_ENCLOSURE'
 assert record['u_end']==.08 and record['steps']==4 and record['subcells']==1
 assert record['refinement'] in (1,2,4,8,16)
 assert record['rays']==6*record['refinement']**2
 Emax=record['Emax_upper']
 Ecomp=Interval(min(Emax,cert['pressure_max_upper']))
 # The parent initial-only final envelope is >= its initial h error since
 # its comparison semigroup is positive and cosh(kt)>=1. This conservative
 # reuse avoids re-evaluating all 1536 MPFR cells in the archived refinement16.
 ini=[Interval(0),Interval(record['initial_ell_h_upper'][1])]
 src=[Interval(0),Interval(0)]
 tim=[Interval(0),Interval(0)]
 prev=0.
 for panel in record['rows']:
  u=float(panel['u_right'])
  dt=Interval(u)-Interval(prev)
  ini=propagate_interval(ini,dt,Ecomp,Interval(0),Interval(0))
  src=propagate_interval(src,dt,Ecomp,Interval(0),Interval(record['source_pressure_upper']))
  tim=propagate_interval(tim,dt,Ecomp,Interval(panel['ell_defect_upper']),Interval(panel['h_defect_upper']))
  tim=[tim[0]+Interval(panel['knot_jump_ell_upper']),tim[1]+Interval(panel['knot_jump_h_upper'])]
  prev=u
 total=[sum((part[k] for part in (ini,src,tim)),Interval(0)).upper for k in range(2)]
 assert total[1] <= record['total_ell_h_upper'][1]
 row={'refinement':record['refinement'],'rays':record['rays'],
  'pmax_upper':cert['pressure_max_upper'],'Emax_upper':Emax,
  'pressure_comparison_ratio':min(Emax,cert['pressure_max_upper'])/Emax,
  'ce1g_h_upper':record['total_ell_h_upper'][1],
  'ce1h_repropagated_h_upper':total[1],
  'source_h_upper':src[1].upper,'time_jump_h_upper':tim[1].upper,'initial_h_upper':ini[1].upper,
  'h_upper_saved':record['total_ell_h_upper'][1]-total[1],
  'target_met':total[1]<1e-5,
  'evidence_level':'PARENT_MPFR_PANEL_REUSE_SHA_VERIFIED_NOT_FRESH_REF16'}
 rows.append(row)
 print(json.dumps(row),flush=True)
assert [x['refinement'] for x in rows]==[1,2,4,8,16]
result={'schema':'bass.ce1h.archived_repropagation.v1',
 'parent_archive_sha256':EXPECTED,'parent_manifest_payloads_verified':len(manifest['payloads']),
 'initial_pressure_certificate':cert,'rows':rows,'upper_dag':'9/15',
 'production_ready':False,'distinct_author_review':'NOT_RUN',
 'fresh_ref16_parent_residual':'NOT_RUN_CURRENT_TURN','method':'exact positive comparison with saved certified panel upper bounds'}
(ROOT/'REPLAY_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')

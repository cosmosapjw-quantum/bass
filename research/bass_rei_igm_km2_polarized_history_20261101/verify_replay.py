"""Check original immutable input and archived-vs-fresh physical scientific readback."""
from pathlib import Path
import hashlib,json,zipfile
from restore_source import ORIGINAL_SHA,OUTER_SHA
ROOT=Path(__file__).resolve().parent

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify():
 manifest=json.loads((ROOT/'SOURCE_INCLUSIVE_MANIFEST.json').read_text())
 assert manifest['original_bass_source_outer_sha256']==OUTER_SHA
 assert manifest['stage_record_count']==20
 assert manifest['source_owner_head']=='4137f942d2a95999f4e6627b71042e98f7afc1b7'
 for name,m in manifest['files'].items():
  p=ROOT/name
  assert p.is_file() and p.stat().st_size==m['bytes'] and digest(p)==m['sha256'],name
 for name,sha in ORIGINAL_SHA.items():
  assert digest(ROOT/'source_inputs'/name)==sha,('original physical input drift',name)
 for folder in ('results','figures'):
  paths=sorted((ROOT/folder).iterdir())
  for p in paths:
   assert p.is_file()
   replay=ROOT/('_replay_'+folder)/p.name
   assert replay.is_file() and digest(p)==digest(replay),('new physics data changed',p.name)
 assert len(list((ROOT/'results').iterdir()))==3
 assert len(list((ROOT/'figures').iterdir()))==6
 return dict(original_input_sha_pass=len(ORIGINAL_SHA),retained_object_sha_pass=len(manifest['files']),
             generated_exact_replay_pass=9,stage_records=20)
if __name__=='__main__':print('SOURCE_POL_REPRODUCIBILITY',json.dumps(verify(),sort_keys=True))

#!/usr/bin/env python3
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,re,subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def validate(root,repo=None):
 root=Path(root).resolve();d=root/'research/continuation_20260830';seen=set()
 for line in (d/'MANIFEST.sha256').read_text(encoding='ascii').splitlines():
  digest,name=line.split('  ',1);p=PurePosixPath(name)
  if not re.fullmatch('[0-9a-f]{64}',digest) or p.is_absolute() or '..' in p.parts or str(p)!=name or name in seen:raise ValueError('invalid manifest path/digest')
  target=root/p
  if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(root):raise ValueError('unsafe payload path')
  if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:raise ValueError('payload byte mismatch: '+name)
  seen.add(name)
 c=json.loads((d/'CONTRACT.json').read_bytes())
 if seen!=set(c['delivery_paths']):raise ValueError('delivery closure')
 if repo:
  def read(*args):return subprocess.check_output(['git','--no-replace-objects',*args],cwd=repo).decode().removesuffix('\n')
  if read('rev-parse',c['base']['commit']+'^{tree}')!=c['base']['tree']:raise ValueError('immutable source tree mismatch')
 return {'status':'PASS_DELIVERY_INTAKE_ONLY','files':len(seen),'next':c['exact_next_action'],'scientific_claim':c['current_scientific_claim']}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=ROOT);a.add_argument('--repo',type=Path);v=a.parse_args()
 print(json.dumps(validate(v.root,v.repo),sort_keys=True))

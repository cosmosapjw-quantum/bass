#!/usr/bin/env python3
"""Pack clean-checkout scientific files with local SHA256 CRC, no fabricated remote backups."""
import json,zipfile,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
dist=root/'dist';dist.mkdir(parents=True,exist_ok=True)
src=[p for p in root.rglob('*') if p.is_file() and 'dist' not in p.parts and '__pycache__' not in p.parts]
groups={'CE1AL_REMOTE_SOURCE_AND_STAGE.zip':[p for p in src if 'data' not in p.parts and 'figures' not in p.parts],
        'CE1AL_REMOTE_ACTUAL_PHYSICS.zip':[p for p in src if 'data' in p.parts or 'figures' in p.parts]}
for name,files in groups.items():
 manifest={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
 with zipfile.ZipFile(dist/name,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
  for p in sorted(files):z.write(p,str(p.relative_to(root)))
  z.writestr('MANIFEST_SHA256.json',json.dumps(manifest,sort_keys=True,indent=2)+'\n')
 with zipfile.ZipFile(dist/name) as z:
  assert z.testzip() is None
  check=json.loads(z.read('MANIFEST_SHA256.json'))
  assert all(hashlib.sha256(z.read(p)).hexdigest()==digest for p,digest in check.items())
 print(name, (dist/name).stat().st_size, len(files),flush=True)

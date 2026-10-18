"""Create-only portable bounded-stage backup, with actual full readback."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,zipfile
HERE=Path(__file__).resolve().parent
EXCLUDED={'.git','__pycache__','target','backups','.venv'}
def checkpoint(stage,destination):
    destination=Path(destination)
    if destination.exists():raise FileExistsError(destination)
    files={}
    for p in sorted(HERE.rglob('*')):
        rel=p.relative_to(HERE)
        if p.is_file() and not any(x in EXCLUDED for x in rel.parts) and p!=destination:
            files[rel.as_posix()]=p.read_bytes()
    manifest={k:hashlib.sha256(v).hexdigest() for k,v in files.items()}
    with zipfile.ZipFile(destination,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for path,data in files.items():z.writestr(path,data)
        z.writestr('STAGE_PAYLOAD_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(destination) as z:
        for name,digest in manifest.items():
            if hashlib.sha256(z.read(name)).hexdigest()!=digest:raise AssertionError('CHECKPOINT_READBACK:'+name)
    return {'stage':stage,'utc':datetime.now(timezone.utc).isoformat(),'path':str(destination),
            'bytes':destination.stat().st_size,'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
            'verified_payloads':len(manifest),'storage':'SANDBOX_ONLY_NOT_CLOUD','external_publication':'BLOCKED_NO_WRITE_ACTION'}
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('stage');p.add_argument('destination',type=Path);a=p.parse_args()
    print(json.dumps(checkpoint(a.stage,a.destination),indent=2))

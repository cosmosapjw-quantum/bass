"""Mechanical cumulative stage archive and Git API payloads. No remote writes."""
from pathlib import Path
import argparse,base64,datetime,hashlib,json,zipfile
LANE=Path(__file__).resolve().parents[1];WORK=LANE.parents[2];DELIVERY=WORK/'delivery'

def blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def files(root):
    return sorted(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.pyc','.tmp','.temp'} and not p.name.endswith('~'))
def stamp(stage,paths,archive,base):
    manifest=dict(unit='BASS_B3E_POSITIVE_ANGULAR_CONTROL_20261025',stage=stage,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=[])
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            data=p.read_bytes();name=str(p.relative_to(base));manifest['files'].append(dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),git_blob=blob(data)));z.writestr(name,data)
        z.writestr('SNAPSHOT_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    return manifest

def main():
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['S0','S1','S2']);parser.add_argument('--private-intake',action='store_true');args=parser.parse_args();DELIVERY.mkdir(exist_ok=True)
    labels=dict(S0='PREPARATION',S1='VALIDATED',S2='FINAL');archive=DELIVERY/f'BASS_B3E_{args.stage}_{labels[args.stage]}_20261025.zip'
    paths=files(LANE);manifest=stamp(args.stage,paths,archive,LANE.parent.parent)
    elements=[];binary=[]
    for p in paths:
        data=p.read_bytes();path=str(p.relative_to(LANE.parent.parent))
        try:text=data.decode('utf-8')
        except UnicodeDecodeError:
            binary.append(dict(path=path,git_blob=blob(data),base64=base64.b64encode(data).decode()));continue
        elements.append(dict(path=path,mode='100644',type='blob',content=text))
    prefix=DELIVERY/f'B3E_{args.stage}'
    for suffix,value in [('MANIFEST',manifest),('GIT_ELEMENTS',elements),('BINARY_PAYLOADS',binary)]:prefix.with_name(prefix.name+'_'+suffix+'.json').write_text(json.dumps(value,indent=2)+'\n')
    result=dict(stage=args.stage,archive=str(archive),archive_bytes=archive.stat().st_size,archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),files=len(paths),text_elements=len(elements),binary_payloads=len(binary),manifest=str(prefix.with_name(prefix.name+'_MANIFEST.json')),git_elements=str(prefix.with_name(prefix.name+'_GIT_ELEMENTS.json')),binary_payloads_path=str(prefix.with_name(prefix.name+'_BINARY_PAYLOADS.json')))
    if args.private_intake:
        private=DELIVERY/f'BASS_B3E_{args.stage}_PRIVATE_INTAKE_20261025.zip';intake=WORK/'intake_next_20261025'
        candidates=[p for p in files(intake) if p.suffix in {'.json','.md'} and not any(token in p.name.lower() for token in ['fulltext','full_text','article_text'])]
        private_manifest=stamp(args.stage,candidates,private,WORK)
        result['private_intake']=dict(archive=str(private),archive_bytes=private.stat().st_size,archive_sha256=hashlib.sha256(private.read_bytes()).hexdigest(),files=len(private_manifest['files']),publication='PRIVATE_BACKUP_ONLY_NOT_GIT')
    prefix.with_name(prefix.name+'_LOCAL_PACKAGING.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()

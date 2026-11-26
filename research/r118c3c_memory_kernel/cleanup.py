"""Compact only explicit old backup expansion directories with exact ZIP readback."""
import os,json,hashlib,stat,shutil,subprocess
from pathlib import Path
from zipfile import ZipFile
H=Path('/home/cosmosapjw');A=Path(__file__).resolve().parent;R=H/'research_backups'
root=R/'REI_BASS_HTT_REC_CHECKPOINT_20261102'
pairs=[(root/n,root/(n+'.zip'),'') for n in ('BASS_CR_MPRK_EFFECTIVE_TRANSFER_RECOVERY_20261102','BASS_REI_F08_NATIVE_ROOT_RECOVERY_20261102','WU_R58_BACKUP_RECEIPT_20261102','WU_R58_INCREMENTAL_RECOVERY_20261102')]
q=R/'BASS_HE_REI_F05_ELECTRON_SOURCE_20261101'
pairs.append((q/'original_rei348',q/'BASS_HE_REI_F05_H_HE_ELECTRON_ORIGINAL_SOURCE_INCLUSIVE_20261101.zip','ORIGINAL_REI348/'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def active(p):
 hits=[]
 for a in Path('/proc').iterdir():
  if not a.name.isdigit():continue
  links=[a/'cwd']
  try:links.extend((a/'fd').iterdir())
  except OSError:pass
  for v in links:
   try:s=os.readlink(v)
   except OSError:continue
   if s==str(p) or s.startswith(str(p)+'/'):hits.append((a.name,str(v.name)))
 return hits
out=[]
for d,z,prefix in pairs:
 row=dict(directory=str(d),archive=str(z),prefix=prefix,status='KEEP');out.append(row)
 if not d.is_dir() or d.is_symlink() or not z.is_file():row['reason']='missing or symlink';continue
 if d.resolve().parent!=d.parent.resolve() or z.resolve().is_relative_to(d.resolve()):row['reason']='path identity';continue
 hits=active(d)
 if hits:row['reason']='in use';row['hits']=hits;continue
 files=[p for p in d.rglob('*') if not p.is_dir() or p.is_symlink()]
 if not files or any(p.is_symlink() or not stat.S_ISREG(p.lstat().st_mode) for p in files):row['reason']='nonregular contents';continue
 try:
  records=[]
  with ZipFile(z) as f:
   if f.testzip() is not None:raise ValueError('ZIP integrity')
   names=f.namelist()
   for p in files:
    rel=str(p.relative_to(d));member=prefix+rel
    if names.count(member)!=1:raise ValueError('missing member '+member)
    with f.open(member) as stream:hh=hashlib.file_digest(stream,'sha256').hexdigest()
    if hh!=sha(p):raise ValueError('byte mismatch '+rel)
    records.append(dict(relative=rel,member=member,sha256=hh,bytes=p.stat().st_size,mode=stat.S_IMODE(p.stat().st_mode)))
  row.update(status='VERIFIED_DUPLICATE',archive_sha=sha(z),files=records,bytes=sum(x['bytes'] for x in records))
 except Exception as e:row['reason']=str(e)
(A/'CLEANUP_PLAN.json').write_text(json.dumps(out,indent=2)+'\n')
print('plan',[(x['directory'],x['status'],x.get('bytes'),x.get('reason')) for x in out],flush=True)
# User explicitly requested cleanup: remove only the exact verified expansions.
for row in out:
 if row['status']!='VERIFIED_DUPLICATE':continue
 d=Path(row['directory']);z=Path(row['archive'])
 if active(d) or sha(z)!=row['archive_sha']:row['status']='KEEP_CHANGED';continue
 actual={str(p.relative_to(d)) for p in d.rglob('*') if not p.is_dir() or p.is_symlink()}
 if actual!={r['relative'] for r in row['files']} or any((d/r['relative']).is_symlink() or sha(d/r['relative'])!=r['sha256'] for r in row['files']):
  row['status']='KEEP_CHANGED';continue
 shutil.rmtree(d)
 assert not d.exists() and sha(z)==row['archive_sha']
 row['status']='REMOVED_VERIFIED_EXPANSION'
w=H/'worktrees/bass-full-rii-wing-20261120-r1';wt={'path':str(w),'active':active(w),'status':'KEEP_ACTIVE' if active(w) else 'KEEP_UNREVIEWED'}
res=dict(rows=out,bytes_removed=sum(x['bytes'] for x in out if x['status']=='REMOVED_VERIFIED_EXPANSION'),worktree=wt,scope='explicit old recovery expansions; original archives intact and exact SHA256 readback; retain source-linked raw histories and active worktrees')
(A/'CLEANUP.json').write_text(json.dumps(res,indent=2)+'\n');print('final',res['bytes_removed'],[(x['directory'],x['status']) for x in out],wt,flush=True)

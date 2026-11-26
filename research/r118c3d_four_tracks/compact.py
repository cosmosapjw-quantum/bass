"""Remove only verified C3D duplicate raw resume expansion, preserve exact archive."""
import hashlib,json,gzip,os,subprocess,shutil
from pathlib import Path
D=Path(__file__).resolve().parent;B=D.parents[1];H=Path('/home/cosmosapjw')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def g(p,*args):return subprocess.check_output(['git','-C',str(p),*args],text=True).strip()
def active(p):
 out=[]
 for q in Path('/proc').iterdir():
  if not q.name.isdigit():continue
  ls=[q/'cwd']
  try:ls.extend((q/'fd').iterdir())
  except OSError:pass
  for f in ls:
   try:t=os.readlink(f)
   except OSError:continue
   if t==str(p) or t.startswith(str(p)+'/'):out.append((q.name,f.name))
 return out
head=g(B,'rev-parse','HEAD');branch=g(B,'branch','--show-current')
assert head==g(B,'ls-remote','--heads','origin','refs/heads/'+branch).split()[0]
m=json.loads((D/'resume_RAW.json').read_text());p=Path(m['raw']);assert p==H/'Downloads/bass_r118c3d_resume'
row=dict(path=str(p),status='KEEP',bytes_removed=0)
if p.is_dir() and not p.is_symlink() and not active(p):
 files={str(f.relative_to(p)) for f in p.rglob('*') if not f.is_dir() or f.is_symlink()}
 assert files==set(m['files'])
 for k,v in m['files'].items():
  q=p/k;z=D/v['compressed'];assert not q.is_symlink() and q.is_file() and not z.is_symlink()
  assert sha(q)==v['sha'] and sha(z)==v['compressed_sha'] and gzip.decompress(z.read_bytes())==q.read_bytes()
  blob=subprocess.check_output(['git','-C',str(B),'show',head+':'+str(z.relative_to(B))]);assert blob==z.read_bytes()
 assert not active(p)
 shutil.rmtree(p);assert not p.exists()
 row.update(status='REMOVED_VERIFIED_DUPLICATE_RAW_RESUME',bytes_removed=sum(v['size'] for v in m['files'].values()),archive_head=head,restore_manifest=str(D/'resume_RAW.json'))
elif not p.exists():row['status']='ALREADY_ABSENT'
else:row['active']=active(p)
w=H/'Downloads/bass_r118c3d_wrong'
if w.is_dir() and not w.is_symlink() and not any(w.iterdir()):w.rmdir()
repos=[B,H/'Downloads/htt_r109_original_rec',H/'worktrees/rei-htt-thomson-20261124']
wt=[]
for repo in repos:
 info=g(repo,'worktree','list','--porcelain')
 for line in info.splitlines():
  if line.startswith('worktree '):
   q=Path(line[9:]);wt.append(dict(path=str(q),active=active(q),status='KEEP_EXISTING'))
print(row)
out=dict(cleanup=row,worktrees=wt,worktrees_deleted=0,scope='exact archived redundant resume only; retain all source histories, split checkpoint and live terminal; no new worktrees')
(D/'CLEANUP.json').write_text(json.dumps(out,indent=2)+'\n');print(out)

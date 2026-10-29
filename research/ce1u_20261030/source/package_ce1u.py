"""Create deterministic S0/S1/S2 reproducible ZIPs with per-member SHA256."""
import hashlib,json,zipfile,sys
from pathlib import Path
root=Path(__file__).resolve().parents[3]; src=root/'research'/'ce1u_20261030';dist=root/'packages';dist.mkdir(exist_ok=True)
rel=lambda f:f.relative_to(root).as_posix()
base=[root/'research'/'ce1t_20261030'/'cellwise_gl_rust.py',root/'research'/'ce1t_20261030'/'local_GL40_history_authority.csv']
s0=[src/'S0_THEORY_KO.md',src/'source'/'ce1u_cert_source.py',src/'data'/'GL6_source_exact_bound.json',src/'data'/'GL8_source_exact_bound.json']+base
s1=s0+[src/'S1_IMPLEMENTATION_KO.md',src/'REPRODUCE.md']+list((src/'source').glob('*.py'))+list((src/'tests').glob('*.py'))+list((src/'data').glob('*'))+list((src/'figures').glob('*.png'))
s2=s1+list(src.glob('*.md'))+list(src.glob('*.json'))+list((src/'stage_checkpoints').glob('*.json'))+[root/'.github/workflows/ce1u-exact-rational-gl-science.yml']
for stage,files in [('S0',s0),('S1',s1),('S2',s2)]:
 if len(sys.argv)>1 and stage not in sys.argv[1:]:continue
 names={rel(f):f for f in files if f.is_file() and '__pycache__' not in str(f)}
 if stage in ('S1','S2'):
  names['checkpoint/CE1U_S0.zip']=dist/'BASS_CE1U_S0_20261030.zip'
 if stage=='S2':names['checkpoint/CE1U_S1.zip']=dist/'BASS_CE1U_S1_20261030.zip'
 manifest={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in sorted(names.items())}
 data=(json.dumps({'schema':'bass.ce1u.member_sha256.v1','members':manifest},indent=2,ensure_ascii=False)+'\n').encode()
 name=f'BASS_CE1U_{stage}_20261030.zip';dst=dist/name
 with zipfile.ZipFile(dst,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as fz:
  for k,p in sorted(names.items()):
   info=zipfile.ZipInfo(k,date_time=(2026,10,30,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;fz.writestr(info,p.read_bytes())
  info=zipfile.ZipInfo('MANIFEST_SHA256.json',date_time=(2026,10,30,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;fz.writestr(info,data)
 with zipfile.ZipFile(dst) as fz:
  assert fz.testzip() is None
  m=json.loads(fz.read('MANIFEST_SHA256.json'))['members']
  assert len(m)==len(names) and all(hashlib.sha256(fz.read(k)).hexdigest()==h for k,h in m.items())
 print(stage,len(names),dst.stat().st_size,hashlib.sha256(dst.read_bytes()).hexdigest(),flush=True)

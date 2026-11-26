import hashlib,json,gzip,sys
from pathlib import Path
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for n in sys.argv[1:]:
 p=H/('bass_r118c3e_'+n);out={}
 for f in sorted([q for q in p.rglob('*') if q.is_file()]):
    key=str(f.relative_to(p));z=D/(n+'_'+key.replace('/','_')+'.gz')
    b=f.read_bytes();z.write_bytes(gzip.compress(b,mtime=0));assert gzip.decompress(z.read_bytes())==b
    out[key]=dict(sha=sha(f),compressed=z.name,compressed_sha=sha(z),size=len(b))
 (D/(n+'_RAW.json')).write_text(json.dumps(dict(raw=str(p),files=out),indent=2)+'\n')
 print(n,len(out),sum(x['size'] for x in out.values()),flush=True)

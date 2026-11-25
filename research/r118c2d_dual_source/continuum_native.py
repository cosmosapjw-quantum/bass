"""Evaluate continuum audit inputs with current native executable."""
import argparse,pathlib,json,subprocess,hashlib
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--continuum',type=P,required=True);p.add_argument('--graph',type=P,required=True);p.add_argument('--binary',type=P,required=True);p.add_argument('--out',type=P,required=True);a=p.parse_args()
a.out.mkdir(exist_ok=False);r=json.loads((a.continuum/'CONTINUUM.json').read_text())
sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
for q in r:
 n=q['name'];dest=a.out/n;cmd=[str(a.binary.resolve()),str(a.graph.resolve()),str((a.continuum/(n+'.txt')).resolve()),str(dest.resolve())]
 subprocess.run(cmd,check=True,capture_output=True)
 m=dict(s.split('=',1) for s in (dest/'run.txt').read_text().splitlines())
 v=float(m['action_x']);q.update(native_x_per_s=v,native_command=cmd,input_sha256=sha(cmd[2]),native_vs_graph_per_photon_s=abs(v-q['graph_x_per_s'])/q['total_number_m3'],hashes={v.name:sha(v) for v in dest.iterdir()})
 assert q['native_vs_graph_per_photon_s']<1e-13
(a.out/'CONTINUUM_NATIVE.json').write_text(json.dumps(dict(binary_sha256=sha(a.binary),graph_sha256=sha(a.graph),cases=r),indent=2,allow_nan=False)+'\n')
print('native continuum oracle',max(q['native_vs_graph_per_photon_s'] for q in r),flush=True)

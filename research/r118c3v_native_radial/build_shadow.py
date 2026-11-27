"""Pinned BASS shadow; radial FD constructor only, native matter and sky unchanged."""
from pathlib import Path
import subprocess,tarfile,io,json,sys,hashlib
D=Path(__file__).resolve().parent;ROOT=D.parents[1];BASE='818b0e91e85c764a90944dc3c0ab6a4eb67736d6'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main(root):
 root=Path(root);root.mkdir(exist_ok=False)
 ar=subprocess.check_output(['git','-C',str(ROOT),'archive',BASE,'_rustcore','generated/rust/typeii','runtime/rust/typeii','research/r109_native_sky/hyrec_1100'])
 with tarfile.open(fileobj=io.BytesIO(ar)) as t:t.extractall(root,filter='data')
 p=root/'_rustcore/src/kinetic/owned_vlasov.rs';s=p.read_text();orig={str(p.relative_to(root)):sha(p)}
 a=s.index('    pub fn with_species(');b=s.index('    pub fn matter(',a);v=s[a:b]
 v=v.replace('pub fn with_species(','pub fn with_radial_species(').replace('[(f64, f64, [f64; 5])]','[(f64, f64, [f64; 5], [f64; 5])]')
 v=v.replace('|(m, w, j)|','|(m, w, j, k)|').replace('|| j.iter().any(|v| !v.is_finite())','|| j.iter().chain(k).any(|v| !v.is_finite())').replace('|| j.iter().map(|v| v * v).sum::<f64>() > 0.010000000000001','|| j.iter().map(|v| v * v).sum::<f64>().max(k.iter().map(|v|v*v).sum::<f64>()) > 0.010000000000001')
 v=v.replace('for &(mass, fraction, j) in specs {','for &(mass, fraction, j, k) in specs {').replace('let j = stf_matrix(j);','let j = stf_matrix(j);let k = stf_matrix(k);')
 old='let def = (-n.dot(&(j * n))).exp();\n                for (&y, &wr) in ys.iter().zip(&ww) {'
 new='''let j1=n.dot(&(j*n));let j2=n.dot(&(k*n));
                for (&y, &wr) in ys.iter().zip(&ww) {
                    let v=1./(1.+(-0.5*((y-8.)/1.4).powi(2)+0.5*((y-0.7)/1.4).powi(2)).clamp(-700.,700.).exp());
                    let def=(-(j2+(j1-j2)*v)).exp();'''
 assert old in v;v=v.replace(old,new);s=s[:b]+v+s[b:];p.write_text(s)
 q=root/'_rustcore/src/kinetic/owned_thomson.rs';s=q.read_text();orig[str(q.relative_to(root))]=sha(q);a=s.index('    pub fn with_species(');b=s.index('    pub fn initial(',a);v=s[a:b]
 v=v.replace('pub fn with_species(','pub fn with_radial_species(').replace('[(f64, f64, [f64; 5])]','[(f64, f64, [f64; 5], [f64; 5])]').replace('OwnedModel::with_species','OwnedModel::with_radial_species').replace('SPECIES_V1','RADIAL_SPECIES_V1').replace('for &(m, w, j) in specs','for &(m, w, j, k) in specs').replace('chain(j) {','chain(j).chain(k) {')
 q.write_text(s[:b]+v+s[b:])
 ex=root/'_rustcore/examples/c3v_radial.rs';ex.write_bytes((D/'native.rs').read_bytes())
 out=dict(base=BASE,archive_sha=hashlib.sha256(ar).hexdigest(),original_sha=orig,patched_sha={n:sha(root/n) for n in orig},example_sha=sha(ex),cargo_lock=sha(root/'_rustcore/Cargo.lock'))
 (D/'SHADOW_ID.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':main(sys.argv[1])

from r118c3g_stage_driver_20261126 import *
import shutil
if __name__=='__main__':
 assert len({(x['stage'],x['repo']) for x in map(json.loads,receipt.read_text().splitlines())})==42
 b=repos['BASS'][0];src=b/'_rustcore/examples/r118c3f_multi.rs';dest=b/'_rustcore/examples/r118c3g_controls.rs'
 t=src.read_text()
 t=t.replace('let specs = [','let mass: f64 = p[5].parse()?;\n    let w3: f64 = p[6].parse()?;\n    let s4: f64 = p[7].parse()?;\n    let orient: f64 = p[8].parse()?;\n    if !(mass.is_finite() && mass > 0. && w3 > 0. && w3 < 1. && s4.is_finite() && orient.is_finite()) { return Err("invalid controls".into()); }\n    let w = (1.-w3)/2.;\n    let specs = [')
 t=t.replace('(0.001, 1. / 3.,','(0.001, w,').replace('(0.006, 1. / 3.,','(0.006, w,').replace('(0.05, 1. / 3., [0., 0., 0., amp, 0.]),','(mass, w3, [amp * orient.sin(), 0., 0., amp * orient.cos(), 0.]),').replace('amp / 4.,','amp * s4,')
 assert 'let mass: f64' in t and '(mass, w3,' in t
 dest.write_text(t)
 for k,files in {'BASS':['memory_controls.py'],'REC':['shared_gas.py','canonical_stock.py'],'REI':['spectral_coupling.py']}.items():
  for f in files:shutil.copyfile(H/('r118c3g_'+f),folder(k)/f)
 batch('C5',extras={'BASS':('_rustcore/examples/r118c3g_controls.rs',)})

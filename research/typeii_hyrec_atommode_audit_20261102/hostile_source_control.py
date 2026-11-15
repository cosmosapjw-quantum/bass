#!/usr/bin/env python3
"""Single same-author review control: isolate native SWIFT refinement failure.
The control has no BASS density or external-grid modifications, and uses native
builtin FLRW H. Only the documented DLNA_SWIFT precision parameter is reduced.
"""
import json,re,shutil,subprocess
from native_modes import HERE,SRC,RUN,P0,check,verify_source,sha
verify_source();b=RUN/'unpatched_SWIFT_quarter_control';b.mkdir(exist_ok=True)
for p in SRC.iterdir():
    if p.suffix in ('.c','.h'):shutil.copyfile(p,b/p.name)
h=(b/'hydrogen.h').read_text()
h,n=re.subn(r'(^#define DLNA_SWIFT\s+)\S+',lambda m:m[1]+'1e-3',h,flags=re.M)
check(n==1,'step precision macro');(b/'hydrogen.h').write_text(h)
for p in SRC.glob('*.dat'):
    dest=b/p.name
    if not dest.exists():dest.symlink_to(p)
cmd=['gcc','-O3','-I'+str(b)]+[str(b/p) for p in ('hyrectools.c','helium.c','hydrogen.c','history.c','energy_injection.c','hyrec.c')]+['-lm','-o',str(b/'native_original')]
p=subprocess.run(cmd,capture_output=True,text=True,timeout=90);check(p.returncode==0,'unpatched control build')
p=subprocess.run([str(b/'native_original')],input=(P0/'HYREC2_FLRW_INPUT_20261102.dat').read_bytes(),cwd=b,capture_output=True,timeout=60)
err=p.stderr.decode(errors='replace');out=b/'output_xe.dat'
(HERE/'UNPATCHED_SWIFT_REFINEMENT_CONTROL.log').write_bytes(p.stdout+p.stderr)
failed=('ERROR HAS OCCURRED' in err or not out.exists() or out.stat().st_size==0)
res={'control':'original native builtin FLRW H; no BASS H/nH patches; only DLNA_SWIFT=0.001','exit':p.returncode,'native_reports_error':bool('ERROR HAS OCCURRED' in err),'scientific_output_valid':not failed,'stderr_tail':err[-1200:],'source_history_byte_exact':sha(b/'history.c')==sha(SRC/'history.c'),'source_hydrogen_c_byte_exact':sha(b/'hydrogen.c')==sha(SRC/'hydrogen.c'),'interpretation':'If the unmodified native control fails too, the observed refinement failure is not introduced by the BASS input adapters. A zero exit alone is insufficient because the original standalone main may return zero after reporting a solver error.'}
(HERE/'HOSTILE_NATIVE_CONTROL.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))

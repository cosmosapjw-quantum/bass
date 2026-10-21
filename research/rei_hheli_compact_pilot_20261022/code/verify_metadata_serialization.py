#!/usr/bin/env python3
"""Focused NumPy scalar serialization and unchanged scientific gate probe."""
import ast
import hashlib
import json
from pathlib import Path
import tempfile
import numpy as np
from compact_system import ROOT,verify_donor
from compact_run import native_scalar_metadata,atomic_json

def main():
    raw={'gates':{'true':np.bool_(True),'false':np.bool_(False)},
         'nested':[np.float64(.125),{'count':np.int64(193)}],
         'tuple':(np.float64(2e-8),np.int64(62))}
    native=native_scalar_metadata(raw)
    assert type(native['gates']['true']) is bool and native['gates']['true'] is True
    assert type(native['gates']['false']) is bool and native['gates']['false'] is False
    assert native['nested'][0]==raw['nested'][0] and native['nested'][1]['count']==193
    array=np.arange(3.);assert native_scalar_metadata(array) is array
    with tempfile.TemporaryDirectory(dir=ROOT/'evidence') as folder:
        path=Path(folder)/'scalar_metadata.json';atomic_json(path,raw)
        decoded=json.loads(path.read_text());assert decoded['gates']=={'true':True,'false':False}
        assert decoded['nested']==[.125,{'count':193}]
    def gates(path):
        tree=ast.parse(path.read_text())
        return next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='gates' for x in n.targets) and isinstance(n.value,ast.Call))
    donor=ROOT/'vendor/rec_hheli/code/coupled.py';adapter=ROOT/'code/compact_run.py'
    assert ast.dump(gates(donor))==ast.dump(gates(adapter))
    verify_donor()
    result={'status':'PASS','scope':'NumPy scalar metadata output compatibility only',
            'array_identity_preserved':True,'gate_values_preserved':True,'gate_expression_AST_identical':True,
            'vendor_git_blobs_unchanged':57,'adapter_sha256':hashlib.sha256(adapter.read_bytes()).hexdigest()}
    (ROOT/'evidence/METADATA_SERIALIZATION_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()

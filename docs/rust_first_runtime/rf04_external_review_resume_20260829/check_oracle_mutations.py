"""Disposable reference-code mutations; NOT compiled-native mutation evidence."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys, tempfile
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[3]
source=root/'tests/rf04/rf04_dense_oracle.py'
suite=root/'tests/rf04/test_dense_oracle.py'
out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else root/'artifacts/rust_first_runtime/rf04/reference_mutations'
out.mkdir(parents=True,exist_ok=True)
text=source.read_text()
cases=[
 ('normal_frame_rate_removed','rate=1-velocity*e[:,axis]\n    return (rate/D**4)',
  'rate=np.ones(len(e))\n    return (rate/D**4)',
  'test_paired_grid_conserves_independent_rate_dual_not_naive_weights'),
 ('kato_added_instead_of_subtracted','Aeff=scalar_transport(e,mid)-Km',
  'Aeff=scalar_transport(e,mid)+Km',
  'test_scalar_aem2_converges_to_A_plus_C_without_extra_K'),
 ('polarized_thomson_gain_halved',"gain=np.einsum('n,nab->ab',w,projected)*3/(8*PI)",
  "gain=np.einsum('n,nab->ab',w,projected)*3/(16*PI)",
  'test_rank9_rest_collision_and_complex_hermitian_psd'),
]
records=[]
for name,old,new,selector in cases:
    assert text.count(old)==1, (name,text.count(old))
    with tempfile.TemporaryDirectory(prefix='rf04_oracle_mutant_') as tmp:
        tmp=Path(tmp)
        (tmp/source.name).write_text(text.replace(old,new))
        shutil.copy2(suite,tmp/suite.name)
        report=tmp/'result.xml'
        command=[sys.executable,'-m','pytest','-q',str(tmp/suite.name)+'::'+selector,
                 '--tb=short','--junitxml='+str(report)]
        env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        run=subprocess.run(command,capture_output=True,text=True,timeout=30,env=env)
        log=run.stdout+run.stderr
        (out/('ORACLE_MUTANT_'+name+'.log')).write_text(log)
        data=ET.parse(report).getroot()
        suites=list(data.iter('testsuite'))
        failures=sum(int(s.attrib.get('failures',0)) for s in suites)
        errors=sum(int(s.attrib.get('errors',0)) for s in suites)
        assert run.returncode==1 and failures==1 and errors==0, (name,log)
        records.append({'mutation':name,'selector':selector,'exit_code':run.returncode,
                        'assertion_failures':failures,'collection_or_runtime_errors':errors,
                        'result':'KILLED_ORACLE_MUTANT',
                        'log_sha256':hashlib.sha256(log.encode()).hexdigest()})
result={'scope':'TEST_ONLY_PYTHON_ORACLE_MUTANTS_NOT_NATIVE',
        'native_mutation_claim':False,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'mutations':records}
(out/'ORACLE_MUTATIONS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

"""Read-only byte identity and saved-evidence verification; no solver executions."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path

def main() -> int:
    root=Path(__file__).resolve().parents[1]
    manifest=json.loads((root/'SHA256SUMS.json').read_text())
    failures=[]
    for name,expected in manifest['files'].items():
        p=root/name
        if not p.is_file():failures.append('missing '+name);continue
        if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:failures.append('hash '+name)
    saved_counts={}
    for name in ['FA03_CHECKS.json','REI_THEORY_CHECKS.json']:
        obj=json.loads((root/'evidence'/name).read_text())
        if obj.get('all_checks_passed') is not True or not all(obj['verdict'].values()):failures.append(name+' saved verdict')
        saved_counts[name]=len(obj['verdict'])
    x=json.loads((root/'evidence/xact_result.json').read_text())
    if x.get('AllCheckedZero') is not True or set(x['Checks'].values())!={'0'}:failures.append('xAct saved output')
    model=json.loads((root/'contracts/FA03_MODEL.json').read_text())
    if model['exact_derivative_base']!='epsilon=0 only':failures.append('derivative scope')
    overlay=json.loads((root/'contracts/THEORY_DAG_OVERLAY.json').read_text())
    if overlay['canonical_REI_status_mutated'] or overlay['parent_DAG_mutated']:failures.append('mutation firewall')
    expected={'SOURCE_CLOCKS.json':'3a1ac8baa12b612eec855fe78a986aca6db577d5625deab952836e2ccd421d8a',
      'ABUNDANCE_MODEL.json':'592c2243a6032b75111fb205ea3e103b229f48194d984e3216b2eb5c74ac9098',
      'THEORY_DAG.json':'d984d4d507794ea2362d40e3264e5d48127c25032b492644fab4e12a29aba59a'}
    checked_parent={}
    for name,sha in expected.items():
        p=root/'reference'/('PARENT_'+name)
        if p.exists():
            ok=hashlib.sha256(p.read_bytes()).hexdigest()==sha;checked_parent[name]=ok
            if not ok:failures.append('parent lock '+name)
    result={'verification':'read-only stored-evidence/identity, not a new scientific run',
      'manifest_files':len(manifest['files']),'saved_check_counts':saved_counts,'xAct_saved_zeros':len(x['Checks']),
      'parent_lock_copies_checked':checked_parent,'failures':failures,'pass':not failures}
    print(json.dumps(result,indent=2));return int(bool(failures))

if __name__=='__main__':sys.exit(main())

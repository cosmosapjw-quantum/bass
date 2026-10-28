"""Deterministic import-only migration of pinned BASS research kernels/tests.

No downloads, subprocesses, source deletion, physics edits, or git mutations.
Run with Python 3.13; --check verifies checked-in outputs without writing.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOSSIER = ROOT / 'research/integration_transition_20261028'
MANIFEST = json.loads((DOSSIER / 'CODEGEN.json').read_text())
NAMES = {m[1] for m in MANIFEST['modules']}


def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def rooted(path):
    p=(ROOT/path).resolve()
    if not p.is_relative_to(ROOT):
        raise ValueError('Manifest path escapes repository')
    return p


class KernelImports(ast.NodeTransformer):
    def visit_ImportFrom(self,node):
        if node.module=='pathlib': return None
        if node.module in NAMES:
            node.level=1
        elif node.module=='polarization':
            node.module='bianchi.q.polarization'; node.level=0
        elif node.module=='rest_volterra':
            node.module='volterra_solver'; node.level=1
        return node

    def visit_Import(self,node):
        out=[]; keep=[]
        for a in node.names:
            if a.name=='sys': continue
            if a.name=='polarization':
                out.append(ast.ImportFrom(module='bianchi.q',names=[a],level=0))
            elif a.name in NAMES:
                out.append(ast.ImportFrom(module=None,names=[a],level=1))
            else: keep.append(a)
        if keep: out.insert(0,ast.Import(names=keep))
        return out or None

    def visit_Assign(self,node):
        text=ast.unparse(node)
        if text.startswith('sys.path') or 'Path(__file__)' in text: return None
        return self.generic_visit(node)

    def visit_Expr(self,node):
        if isinstance(node.value,ast.Call) and ast.unparse(node.value.func).startswith('sys.path.'):
            return None
        return self.generic_visit(node)


class TestImports(KernelImports):
    def visit_ImportFrom(self,node):
        if node.module=='pathlib': return None
        if node.module=='legacy_boost':
            node.module='bianchi.q.polstate'; return node
        name={'fixtures':'km2b_fixtures','rest_volterra':'volterra_solver'}.get(node.module,node.module)
        if name in NAMES: node.module='bianchi.nonperturbative._core.'+name
        return node

    def visit_Import(self,node):
        out=[]; keep=[]
        for a in node.names:
            if a.name in ('sys','importlib.util'): continue
            if a.name=='polarization': out.append(ast.ImportFrom(module='bianchi.q',names=[a],level=0))
            elif a.name in NAMES: out.append(ast.ImportFrom(module='bianchi.nonperturbative._core',names=[a],level=0))
            else: keep.append(a)
        if keep: out.insert(0,ast.Import(names=keep))
        return out or None

    def visit_Assign(self,node):
        text=ast.unparse(node)
        if 'Path(__file__)' in text or text.startswith('sys.path') or text.startswith('spec ='): return None
        if text.startswith('p8 ='):
            return ast.ImportFrom(module='bianchi.q',names=[ast.alias(name='polarization',asname='p8')],level=0)
        return self.generic_visit(node)

    def visit_Expr(self,node):
        if isinstance(node.value,ast.Call) and (ast.unparse(node.value.func).startswith('sys.path.') or ast.unparse(node.value.func)=='spec.loader.exec_module'):
            return None
        return self.generic_visit(node)


METHOD = '''    def collide_normal_time(self, dt_s, rest_rate_s, *, beta,
                            panels=32, backend=None):
        """Opt-in fixed-beta collision substep in normal proper seconds.

        Explicit backend='python_oracle' only. rest_rate_s=n_e* sigma_T c
        excludes Doppler D. Geometry is held fixed; the original default
        Hubble-clock/Strang path is unchanged. No native or EFE promotion.
        """
        from bianchi.nonperturbative.polq_bridge import advance_polqstate_normal_time
        return advance_polqstate_normal_time(
            self, dt_s, rest_rate_s, beta=beta, panels=panels, backend=backend)

'''


def emit(path,data,check):
    p=rooted(path)
    if check:
        if not p.exists() or p.read_bytes()!=data:
            raise ValueError(f'Generated output differs: {path}')
    else:
        p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)


def main():
    args=argparse.ArgumentParser(); args.add_argument('--check',action='store_true'); check=args.parse_args().check
    for stage,name,source,source_blob,target_sha in MANIFEST['modules']:
        data=rooted(source).read_bytes()
        if blob(data)!=source_blob: raise ValueError(f'Source identity mismatch: {source}')
        tree=KernelImports().visit(ast.parse(data.decode()))
        output=(ast.unparse(ast.fix_missing_locations(tree))+'\n').encode()
        if hashlib.sha256(output).hexdigest()!=target_sha:
            raise ValueError(f'Unexpected AST transform output: {name}; use Python 3.13')
        emit(f'bianchi/nonperturbative/_core/{name}.py',output,check)
    emit('bianchi/nonperturbative/_core/__init__.py',b'"""Scoped kernels, mechanically relocated from pinned research sources."""\n',check)
    for stage,source,source_blob,target,target_sha in MANIFEST['tests']:
        data=rooted(source).read_bytes()
        if blob(data)!=source_blob: raise ValueError(f'Test source mismatch: {source}')
        tree=TestImports().visit(ast.parse(data.decode()))
        output=(ast.unparse(ast.fix_missing_locations(tree))+'\n').encode()
        if hashlib.sha256(output).hexdigest()!=target_sha:
            raise ValueError(f'Unexpected test transform output: {source}')
        emit(target,output,check)
    p=rooted('bianchi/q/polstate.py'); data=p.read_bytes()
    if '    def collide_normal_time(' not in data.decode():
        if blob(data)!=MANIFEST['polstate']['original_blob']:
            raise ValueError('Live PolQState changed; refusing automatic insertion')
        updated=data.decode().replace('    def collide(self, nu_dtau, v_b=None):',METHOD+'    def collide(self, nu_dtau, v_b=None):',1).encode()
        emit('bianchi/q/polstate.py',updated,check)
        data=updated
    if blob(data)!=MANIFEST['polstate']['integrated_blob']:
        raise ValueError('Integrated PolQState identity differs')
    for path,expected in MANIFEST['reports']:
        data=rooted(path).read_bytes()
        if blob(data)!=expected:
            # One known byte-level posting typo. Only accept exact original hash.
            repaired=data.replace(b'\n y,z translation',b'\ny,z translation')
            if blob(repaired)!=expected or check:
                raise ValueError(f'Original report bytes differ: {path}')
            emit(path,repaired,False)
    print(json.dumps({'modules':len(MANIFEST['modules']),'test_files':len(MANIFEST['tests']),
                      'original_reports':len(MANIFEST['reports']),'mode':'check' if check else 'assemble'},sort_keys=True))


if __name__=='__main__': main()

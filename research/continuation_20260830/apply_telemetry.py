#!/usr/bin/env python3
"""Apply the already compiled telemetry patch ONLY in an isolated Git worktree."""
from pathlib import Path
import argparse,hashlib,json,subprocess
HERE=Path(__file__).resolve().parent
REL='runtime/rust/typeii/typeii_polarized_liouville.rs'
OLD='da6fade06f717ab938b0ec4c712ab239e78c998a'
NEW='e4d0f9c44fc26740d3a1cad6938b522fe514ae37'
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);a=ap.parse_args();root=a.repo.resolve()
 if not (root/'.git').is_file():raise ValueError('require a linked isolated worktree; main checkout is not allowed')
 top=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=root,text=True).strip()).resolve()
 if top!=root:raise ValueError('worktree root required')
 branch=subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()
 if branch in ('main','master'):raise ValueError('canonical branch is forbidden')
 target=root/REL;before=blob(target.read_bytes())
 if target.is_symlink():raise ValueError('symlink source is forbidden')
 if before==NEW:print(json.dumps({'status':'ALREADY_APPLIED','blob':NEW}));return
 if before!=OLD:raise ValueError('source changed: preserve it, do not patch an unknown donor')
 patch=HERE/'liouville_telemetry.patch'
 subprocess.run(['git','apply','--check',str(patch)],cwd=root,check=True)
 subprocess.run(['git','apply',str(patch)],cwd=root,check=True)
 after=blob(target.read_bytes())
 if after!=NEW:raise ValueError('unexpected patched source identity; preserve worktree for diagnosis')
 print(json.dumps({'status':'APPLIED_EXACT_TESTED_PATCH','old_blob':before,'new_blob':after,'claim':'NO_PASS_RF04'}))
if __name__=='__main__':main()

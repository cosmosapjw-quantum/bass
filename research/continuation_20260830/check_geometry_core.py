#!/usr/bin/env python3
"""Compile the actual donor's numerical prefix against its pinned baseline.

The carrier/PyO3 wrappers are deliberately excluded. A declaration-only test
shim supplies the error/policy types; no mock physical guard runs. The real
advance_midpoint_interval, coefficients, rotations and normalization execute.
This is a scoped numerical-core test, NOT the full native extension build.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[2]
REL='runtime/rust/typeii/typeii_polarized_liouville.rs'
BASE='50b6e9f7a6741b7fd25b0421d2a674b9eb92cdda'
OLD='da6fade06f717ab938b0ec4c712ab239e78c998a'
NEW='e4d0f9c44fc26740d3a1cad6938b522fe514ae37'
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def prefix(text):
 x=text.split('/// Instantaneous bolometric tensor RHS')[0]
 a=x.index('use super::typeii_physical_guard::{');b=x.index('\n};',a)+3
 return x[:a]+'''#[derive(Clone, Debug, PartialEq)] pub struct PhysicalCarrierError;
#[derive(Clone, Copy)] pub enum ScreenInputPolicy { Reject { tolerance: f64 }, Project }
'''+x[b:]
def wrapper(new):
 stats='let mut work=CharacteristicWork::default();' if new else ''
 argument='&mut work,' if new else ''
 counts='(work.split_events,work.accepted_leaves,work.max_depth)' if new else '(0,0,0)'
 return '''
pub fn core_probe(strength:f64,step:f64,panels:usize,initial:[f64;3]) -> Result<(Vec<u64>,usize,(u64,u64,usize)),String> {
 let calls=std::cell::Cell::new(0usize);
 let bg=|f:f64| {calls.set(calls.get()+1);HomogeneousRayBackground{
 expansion:0.0,shear:[[-0.3*strength,0.0,0.04*strength],[0.0,0.1*strength,0.0],[0.04*strength,0.0,0.2*strength]],
 structure_n:[[strength*(1.0+0.1*f),0.0,0.0],[0.0;3],[0.0;3]],class_b_a:[0.0;3],triad_rotation:[0.0,0.04*strength,0.0]}};
 let mut direction=checked_normalize(initial).map_err(|e|format!("{:?}",e))?;
 let mut matrix=identity3();let mut transport=identity3();let mut energy=0.0;let mut screen=0.0;
 '''+stats+'''
 for i in 0..panels {advance_midpoint_interval(&mut direction,&mut matrix,&mut transport,&mut energy,&mut screen,step,i as f64/panels as f64,(i+1)as f64/panels as f64,i,0,'''+argument+'''&bg).map_err(|e|format!("{:?}",e))?;}
 let mut bits=Vec::new();for v in direction {bits.push(v.to_bits());}for v in matrix.into_iter().flatten(){bits.push(v.to_bits());}for v in transport.into_iter().flatten(){bits.push(v.to_bits());}bits.push(energy.to_bits());bits.push(screen.to_bits());
 Ok((bits,calls.get(),'''+counts+'''))
}
'''
TEST=r'''#![allow(dead_code)]
mod original;mod candidate;
#[test] fn actual_geometry_and_error_parity(){
 let mut successes=0;let mut failures=0;let mut split_cases=0;
 for a in [0.0,0.5,2.0,10.0,50.0,f64::NAN] {for h in [-1.0,0.01,0.25] {for panels in [1usize,4] {for direction in [[1.0,0.0,0.0],[0.3,0.4,0.8660254037844386],[0.6,0.8,0.0]] {
 let old=original::core_probe(a,h,panels,direction);let new=candidate::core_probe(a,h,panels,direction);
 match(old,new){
 (Ok((x,c,_)),Ok((y,d,(s,l,m))))=>{assert_eq!(x,y,"numerical output changed");assert_eq!(c,d,"background calls changed");assert_eq!(l,panels as u64+s);assert_eq!(d as u64,panels as u64+2*s);assert!(m<=8);if s>0{split_cases+=1;}successes+=1;},
 (Err(x),Err(y))=>{assert_eq!(x,y);failures+=1;},_=>panic!("success/error changed")}
 }}}}
 assert!(successes>20);assert!(split_cases>0);assert!(failures>0);println!("PARITY_SUCCESS={} SPLIT_CASES={} FAILURE_PARITY={}",successes,split_cases,failures);
}
#[test] fn split_count_is_not_recursion_depth(){
 let(_,calls,(s,l,d))=candidate::core_probe(100.0,4.0,4,[0.3,0.4,0.8660254037844386]).unwrap();
 assert!(s>d as u64);assert_eq!(l,4+s);assert_eq!(calls as u64,4+2*s);println!("TOTAL_SPLITS={} LEAVES={} DEPTH={}",s,l,d);
}
'''
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,default=ROOT);ap.add_argument('--baseline',type=Path);ap.add_argument('--candidate',type=Path);ap.add_argument('--rustc',default='rustc');ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 old=a.baseline.read_bytes() if a.baseline else subprocess.check_output(['git','show',BASE+':'+REL],cwd=a.repo)
 new=(a.candidate or a.repo/REL).read_bytes()
 assert blob(old)==OLD and blob(new)==NEW,'immutable numerical input mismatch'
 a.out.mkdir(parents=True,exist_ok=False)
 for name,text in [('original.rs',prefix(old.decode())+wrapper(False)),('candidate.rs',prefix(new.decode())+wrapper(True)),('test.rs',TEST)]: (a.out/name).write_text(text)
 build=subprocess.run([a.rustc,'--edition=2021','--test','test.rs','-o','tests'],cwd=a.out,capture_output=True,text=True)
 (a.out/'compile.log').write_text(build.stdout+build.stderr);build.check_returncode()
 p=subprocess.run([str((a.out/'tests').resolve()),'--nocapture'],capture_output=True,text=True)
 (a.out/'tests.log').write_text(p.stdout+p.stderr);p.check_returncode()
 receipt={'scope':'ACTUAL_DONOR_GEOMETRY_PREFIX_NOT_CARRIER_OR_PYO3','old_blob':OLD,'new_blob':NEW,'rustc':subprocess.check_output([a.rustc,'--version'],text=True).strip(),'tests_exit':p.returncode,'log_sha256':hashlib.sha256((a.out/'tests.log').read_bytes()).hexdigest(),'full_crate':'NOT_RUN','full_polarized':'NO_PASS_RF04'}
 (a.out/'GEOMETRY_CORE.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()

"""Bounded read-only snapshot of *live* rei_bianchi owner progress.

This utility never edits the REI checkout and never starts/restarts/kills a
solver. Terminal original checkpoints, execution receipts, live processes,
and potentially stale STATE text are separate evidence types.
"""
from __future__ import annotations
import argparse,hashlib,json,subprocess,datetime
from pathlib import Path

CASE_IDS=("SHEAR_PLUS","SHEAR_MINUS","SHEAR_HALF_PLUS","SHEAR_HALF_MINUS")
STATE_REL=Path("docs/fastest_track_chat/REI-AXBI-GOAL-20261014/STATE.json")
CASE_PARENT=Path("research/axbi_goal_20261014/runs/paired/32d11e733155")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git_info(repo):
    def run(*args):
        p=subprocess.run(["git","-C",str(repo),*args],text=True,capture_output=True)
        return p.stdout.strip() if p.returncode==0 else None
    return {"head":run("rev-parse","HEAD"),
            "tracked_status":run("status","--porcelain=v1","-uno"),
            "branch":run("branch","--show-current")}

def parse_kv(path):
    if not path.exists():return None
    out={}
    for line in path.read_text(errors="replace").splitlines():
        if "=" in line:
            k,v=line.split("=",1);out[k.strip()]=v.strip()
    return out

def process_inventory():
    p=subprocess.run(["ps","-eo","pid,ppid,comm,args"],text=True,capture_output=True)
    if p.returncode!=0:return {"status":"UNAVAILABLE","workers":[]}
    workers=[]
    for line in p.stdout.splitlines()[1:]:
        if any(k in line for k in ("axbi_plus_resource_continuation","axbi_reionization --config",
                "post_cap_epoch_recovery.py --observe","recover_plus.py --observe")):
            words=line.split(None,3)
            if len(words)>3 and "ps -eo" not in words[3] and "bash -l -c" not in words[3]:
                workers.append({"pid":int(words[0]),"ppid":int(words[1]),"process":words[2],
                 "type":next(x for x in ("axbi_plus_resource_continuation","axbi_reionization",
                      "post_cap_epoch_recovery","recover_plus") if x in words[3])})
    return {"status":"OBSERVED","workers":workers}

def build_snapshot(repo):
    repo=repo.expanduser().resolve()
    state_path=repo/STATE_REL
    if not state_path.is_file():raise FileNotFoundError(f"MISSING_REI_STATE:{state_path}")
    state=json.loads(state_path.read_text())
    cases=[]
    for name in CASE_IDS:
        d=repo/CASE_PARENT/name
        return_file=d/"RETURN.txt"
        record=parse_kv(return_file)
        checkpoint=d/"checkpoint.txt"
        receipt=repo/CASE_PARENT/(name+"_raw")/"execution_receipt.json"
        ri=json.loads(receipt.read_text()) if receipt.exists() else None
        cases.append({"name":name,
          "return_exists":record is not None,
          "return_sha256":sha(return_file) if record is not None else None,
          "status_from_return":record.get("status") if record is not None else None,
          "accepted_from_return":record.get("accepted") if record is not None else None,
          "resource_cap_from_return":("AXBI_RUNTIME_CAP" in record.get("result","")) if record else None,
          "checkpoint_exists":checkpoint.exists(),
          "checkpoint_sha256":sha(checkpoint) if checkpoint.exists() else None,
          "raw_receipt_exists":ri is not None,
          "raw_receipt_status":ri.get("status") if ri else None,
          "raw_receipt_exit_code":ri.get("exit_code") if ri else None,
          "scientific_admission_from_return":record.get("scientific_admission") if record else None,
          "scoped_science_pass":False})
    nodes=state.get("nodes",{})
    proc=process_inventory()
    stalled=[]
    if ("HALF_MINUS_ORIGINAL_LIVE" in str(nodes.get("AX08",{}).get("scientific_work_status"))) and any(x["name"]=="SHEAR_HALF_MINUS" and x["status_from_return"]=="STOPPED_CHECKPOINTED" for x in cases):
        stalled.append("AX08_DESCRIPTIVE_STATUS_STALE_WRT_HALF_MINUS_TERMINAL")
    pluserr=repo/"research/axbi_goal_20261014/driver/full/epoch_recovery_001/plus/recovery_001/observer.stderr"
    failed_plus=("LIVE_WORKERS_OR_CHILDREN_HOLD" in pluserr.read_text(errors="replace")) if pluserr.exists() else False
    pluscont=repo/CASE_PARENT/"SHEAR_PLUS_continuation_001"
    plusrecord=parse_kv(pluscont/"RETURN.txt")
    return {"schema":"rei.axbi.owner.readonly.snapshot.v1",
      "observed_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "git":git_info(repo),
      "state":{"sha256":sha(state_path),"goal_status":state.get("goal_status"),
         "global_scientific_admission":state.get("scientific_admission"),
         "AX07_status":nodes.get("AX07",{}).get("status"),
         "AX08_status":nodes.get("AX08",{}).get("status"),
         "AX11_status":nodes.get("AX11",{}).get("status"),
         "AX12_status":nodes.get("AX12",{}).get("status"),
         "next_command_precondition":state.get("next_command_precondition")},
      "original_signed_cases":cases,
      "plus_continuation":{"output_directory_exists":pluscont.exists(),
          "terminal_RETURN_exists":plusrecord is not None,
          "terminal_status":plusrecord.get("status") if plusrecord else None,
          "historical_observer_error_exists":failed_plus,
          "historical_error_type":"LIVE_WORKERS_OR_CHILDREN_HOLD" if failed_plus else None,
          "scientific_admission":"NOT_INFERRED_FROM_OBSERVER_OR_PROCESS_EXIT"},
      "liveness":proc,"staleness_findings":stalled,
      "actual_scientific_convergence_reviewed":False,
      "owner_files_modified":0,
      "owner_solver_started":0}

def write_snapshot(repo,out):
    repo=repo.expanduser().resolve()
    output=out.expanduser().resolve()
    if output.is_relative_to(repo):
        raise ValueError("REFUSE_WRITING_INSIDE_ACTIVE_REI_REPO")
    if output.exists():raise FileExistsError(str(output))
    snap=build_snapshot(repo)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(snap,indent=2,ensure_ascii=False)+"\n")
    return snap

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--rei-repo",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    r=write_snapshot(args.rei_repo,args.out)
    print(json.dumps({"saved":str(args.out),"owner_head":r["git"]["head"],
       "state":r["state"],"workers":r["liveness"],"staleness_findings":r["staleness_findings"]},indent=2))

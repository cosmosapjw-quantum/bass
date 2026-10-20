"""Bound one owned child process group and preserve its interrupted receipt.

This module never signals an existing/owner process group. Each child is born in
a new session here. Wrappers can therefore clean their own nested session when
the outer NCP scheduler terminates the wrapper's process group.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import time


class ChildInterrupted(Exception):
    def __init__(self, signum):
        self.signum = signum
        super().__init__('WRAPPER_SIGNAL:'+str(signum))


def atomic_json(path, value):
    path = Path(path);path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name+'.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    os.replace(tmp, path)


def cleanup_owned_group(proc, grace_s=0.6):
    """Only a Popen created by run_owned; bounded below outer 2-second grace."""
    actions = []
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(proc.pid, sig)
            actions.append(signal.Signals(sig).name)
        except ProcessLookupError:
            break
        if sig == signal.SIGTERM:
            try:proc.wait(timeout=grace_s)
            except subprocess.TimeoutExpired:pass
            # A parent can exit before its child. KILL the same owned group
            # even after parent exit, without ever using a guessed group id.
    try:proc.wait(timeout=0.2)
    except subprocess.TimeoutExpired:actions.append('REAP_PENDING')
    return actions


def run_owned(argv, *, stdout_path, stderr_path, receipt_path, timeout_s,
              stdin_bytes=None, cwd=None, env=None, as_bytes=None, file_bytes=None):
    """Run, log, and return an execution receipt, including launch/timeout errors."""
    stdout_path, stderr_path = Path(stdout_path), Path(stderr_path)
    for path in (stdout_path, stderr_path):path.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic();proc = None
    record = {'schema':'BASS_S12_OWNED_PROCESS_V1', 'argv':list(map(str, argv)),
        'cwd':str(Path(cwd).resolve()) if cwd else str(Path.cwd()),
        'started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'status':'STARTING', 'timeout_s':timeout_s, 'exit_code':None,
        'input_sha256':hashlib.sha256(stdin_bytes).hexdigest() if stdin_bytes is not None else None,
        'limits':{'address_space_bytes':as_bytes,'file_bytes':file_bytes},
        'cleanup_actions':[]}
    atomic_json(receipt_path, record)
    def interrupted(signum, frame):raise ChildInterrupted(signum)
    old_handlers={s:signal.getsignal(s) for s in (signal.SIGTERM, signal.SIGINT)}
    def limits():
        signal.pthread_sigmask(signal.SIG_SETMASK,mask)
        if as_bytes:resource.setrlimit(resource.RLIMIT_AS,(as_bytes,as_bytes))
        if file_bytes:resource.setrlimit(resource.RLIMIT_FSIZE,(file_bytes,file_bytes))
    try:
        for s in old_handlers:signal.signal(s,interrupted)
        with stdout_path.open('wb') as out, stderr_path.open('wb') as err:
            # Block wrapper signals until the new group's pid is assigned.
            mask=signal.pthread_sigmask(signal.SIG_BLOCK, set(old_handlers))
            try:
                proc=subprocess.Popen(list(map(str,argv)), cwd=cwd, env=env,
                    stdin=subprocess.PIPE if stdin_bytes is not None else subprocess.DEVNULL,
                    stdout=out, stderr=err, start_new_session=True, preexec_fn=limits)
            finally:signal.pthread_sigmask(signal.SIG_SETMASK,mask)
            record.update(status='RUNNING',pid=proc.pid,owned_process_group=proc.pid)
            atomic_json(receipt_path,record)
            proc.communicate(input=stdin_bytes,timeout=timeout_s)
            record.update(status='EXITED',exit_code=proc.returncode)
    except subprocess.TimeoutExpired:
        record.update(status='TIMED_OUT',exit_code=124)
    except ChildInterrupted as e:
        record.update(status='INTERRUPTED',exit_code=128+e.signum,signal=e.signum)
    except Exception as e:
        record.update(status='SPAWN_OR_IO_FAILED',exit_code=127,
            error={'type':type(e).__name__,'message':str(e)})
    finally:
        # Suppress a second outer signal during the bounded group cleanup.
        for s in old_handlers:signal.signal(s,signal.SIG_IGN)
        if proc is not None and record['status'] == 'EXITED':
            try:
                os.killpg(proc.pid,0)
                record.update(status='LEFTOVER_OWNED_CHILDREN',exit_code=125,
                    parent_returncode=proc.returncode)
            except ProcessLookupError:pass
        if proc is not None and record['status'] != 'EXITED':
            record['cleanup_actions']=cleanup_owned_group(proc)
            record['child_returncode']=proc.returncode
        record['elapsed_s']=time.monotonic()-start
        record['ended_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
        for label,path in [('stdout',stdout_path),('stderr',stderr_path)]:
            record[label+'_path']=str(path)
            record[label+'_sha256']=hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        atomic_json(receipt_path,record)
        for s,handler in old_handlers.items():signal.signal(s,handler)
    return record

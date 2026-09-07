#!/usr/bin/env python3
"""One unchanged local AUX launch; outer process logging only."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shlex
import subprocess
import time

run = Path(__file__).resolve().parent.parent
out = run / "execution"
def now():
    return datetime.now(timezone.utc).isoformat()
def save(name, value):
    (out / name).write_text(json.dumps(value, indent=2) + "\n")
before = json.loads((run / "identity/before.json").read_text())
for entry in before["files"]:
    assert hashlib.sha256((run / entry["path"]).read_bytes()).hexdigest() == entry["sha256"]
executables = json.loads((run / "identity/executables.json").read_text())
argv = [executables["timeout"]["resolved_path"], "--signal=TERM", "--kill-after=10s", "150s",
        executables["wolframscript"]["path"], "-local", executables["kernel"]["resolved_path"],
        "-file", str(run / "driver/BASS_AUX13_AUX14_V1.wls")]
record = {"task": "BG02_AUX13_AUX14_ACTUAL_CONSUMER_VALIDATION", "invocation_number": 1,
          "attempt_start_utc": now(), "argv": argv, "cwd": str(out),
          "environment_overrides": {"BASS_REPO": str(run / "source")},
          "inner_timeout_seconds": 120, "outer_timeout_seconds": 150, "kill_after_seconds": 10,
          "launch_wrapper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
with (out / "ATTEMPT_STARTED.json").open("x") as f:
    json.dump(record, f, indent=2)
    f.write("\n")
    f.flush()
    os.fsync(f.fileno())
(out / "command.txt").write_text("env " + shlex.quote("BASS_REPO=" + str(run / "source")) + " " +
    shlex.join(argv) + " >stdout.log 2>stderr.log\n")
environment = os.environ.copy()
environment["BASS_REPO"] = str(run / "source")
started = time.monotonic()
with (out / "stdout.log").open("xb") as stdout, (out / "stderr.log").open("xb") as stderr:
    try:
        process = subprocess.Popen(argv, cwd=out, env=environment, stdin=subprocess.DEVNULL,
                                   stdout=stdout, stderr=stderr)
    except OSError as exc:
        save("process.json", {**record, "launcher_started": False, "process_exit": None,
            "launch_error": repr(exc), "end_utc": now(), "timeout": False})
        raise
    save("process-start.json", {"pid": process.pid, "observed_start_utc": now(), "argv": argv})
    exit_code = process.wait()
save("process.json", {**record, "launcher_started": True, "pid": process.pid,
    "process_exit": exit_code, "end_utc": now(), "elapsed_seconds": time.monotonic() - started,
    "timeout": exit_code == 124, "termination_signal": -exit_code if exit_code < 0 else None,
    "exit_semantics": "GNU timeout status; equals wolframscript child exit when no timeout or launcher error"})
(out / "process_exit.txt").write_text(str(exit_code) + "\n")
print(json.dumps({"process_exit": exit_code, "elapsed_seconds": time.monotonic() - started}))

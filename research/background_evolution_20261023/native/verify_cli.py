"""End-to-end stdin/stdout checks of the dependency-free Rust executable."""
from pathlib import Path
import json
import math
import subprocess


def encode(sectors, state, pressure=None, pi5=None, energy=None, momentum=None,
           cosmological_constant=0.0, rotation=(0.0, 0.0, 0.0)):
    pressure = [0.0] * sectors if pressure is None else pressure
    pi5 = [[0.0] * 5 for _ in range(sectors)] if pi5 is None else pi5
    energy = [0.0] * sectors if energy is None else energy
    momentum = [[0.0] * 3 for _ in range(sectors)] if momentum is None else momentum
    values = (list(state) + pressure + [v for row in pi5 for v in row] + energy
              + [v for row in momentum for v in row] + [cosmological_constant]
              + list(rotation))
    return str(sectors) + " " + " ".join(format(x, ".17g") for x in values) + "\n"


def main():
    root = Path(__file__).resolve().parent
    binary = root / "target/release/bass-background-fixed-scale"
    state = [0.0] * 20
    state[0], state[16] = 2 / 3, 4 / 3
    good = encode(1, state)
    proc = subprocess.run([str(binary)], input=good + good, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    lines = proc.stdout.splitlines()
    assert len(lines) == 2
    for line in lines:
        values = list(map(float, line.split()))
        assert len(values) == 27
        assert math.isclose(values[0], -2/3, rel_tol=1e-14)
        assert math.isclose(values[16], -8/3, rel_tol=1e-14)
        assert max(map(abs, values[-7:])) < 1e-14
    failures = {
        "malformed_length": "1 0\n",
        "unbalanced_energy": encode(1, state, energy=[1.0]),
        "unbalanced_momentum": encode(1, state, momentum=[[0.0, 1.0, 0.0]]),
        "nonfinite_state": encode(0, [math.nan] + [0.0] * 15),
    }
    rejected = {}
    for name, request in failures.items():
        p = subprocess.run([str(binary)], input=request, capture_output=True, text=True)
        assert p.returncode != 0 and p.stderr.strip(), name
        rejected[name] = {"exit_code": p.returncode, "stderr": p.stderr.strip()}
    evidence = root.parent / "evidence/native"
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "cli_valid_input.txt").write_text(good + good)
    (evidence / "cli_valid_output.txt").write_text(proc.stdout)
    result = {"status": "pass_scoped", "valid_lines": 2, "values_per_line": 27,
              "invalid_cases": rejected}
    (evidence / "cli_verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()

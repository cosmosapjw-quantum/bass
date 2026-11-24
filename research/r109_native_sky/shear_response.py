"""Measure the finite-shear part of a native Bianchi sky at fixed observer and matter IC."""
import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path
import numpy as np


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one(binary, raw, family, steps, nmu, nphi, amplitude):
    out = raw / f"{family}_{steps}_{nmu}_{amplitude:+.4f}"
    cmd = [str(binary), "--out", str(out), "--family", family, "--shear", str(amplitude),
           "--duration", "0.5", "--steps", str(steps), "--nmu", str(nmu), "--nphi", str(nphi),
           "--lmax", "6", "--feedback", "recoil", "--tau", "0.2", "--dust-fraction", "0.22"]
    subprocess.run(cmd, check=True)
    with (out / "modes.tsv").open() as f:
        table = list(csv.DictReader(f, delimiter="\t"))
    keys = [(int(r["ell"]), int(r["m"])) for r in table]
    alm = np.array([[complex(float(r[x+"_re"]), float(r[x+"_im"])) for x in "TEB"] for r in table])
    return keys, alm, {"amplitude": amplitude, "argv": cmd[3:], "modes_sha256": digest(out/"modes.tsv")}


def norm(x):
    return float(np.linalg.norm(x))


def study(binary, raw, family, steps, nmu, nphi):
    eps = .0025
    amplitudes = [0.] + [sgn*s for s in (eps, 2*eps, .03, .06, .12, .24) for sgn in (1, -1)]
    samples, runs = {}, []
    for x in amplitudes:
        keys, alm, record = one(binary, raw, family, steps, nmu, nphi, x)
        samples[x] = alm
        runs.append(record)
    ell = np.array([k[0] for k in keys])
    # Fourth-order central derivative. This calibration is disjoint from the finite s tested below.
    d1 = (8*(samples[eps]-samples[-eps])-(samples[2*eps]-samples[-2*eps]))/(12*eps)
    metrics = []
    for s in (.03, .06, .12, .24):
        for i, field in enumerate("TEB"):
            mask = ell >= 2
            pos, neg, base = (samples[x][mask,i] for x in (s,-s,0.))
            signal = pos-base
            even = (pos+neg)*.5-base
            # Axisymmetric I in its rest frame has a parity-null B channel.
            # Report its numerical floor without forming a relative diagnostic.
            resolved = norm(signal) >= 1e-10 and not (family == "I" and field == "B")
            metrics.append({"shear":s,"field":field, "signal_norm":norm(signal),
                            "even_norm":norm(even), "resolved":resolved,
                            "linear_prediction_residual_fraction":norm(signal-s*d1[mask,i])/norm(signal) if resolved else None,
                            "l4_norm":norm((samples[s]-samples[0])[ell==4,i])})
    return {"family":family,"steps":steps,"nmu":nmu,"nphi":nphi,"lmax":6,"metrics":metrics,"runs":runs}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ("binary","raw","out"):
        p.add_argument("--"+arg, required=True, type=Path)
    a = p.parse_args()
    if not a.binary.is_file() or a.raw.exists():
        p.error("require an existing binary and a new raw directory")
    a.raw.mkdir(parents=True)
    cases = [study(a.binary.resolve(), a.raw, family,steps,nmu,nphi)
             for family,steps,nmu,nphi in (("I",32,12,28),("VIIh",32,12,28),("VIIh",64,16,36))]
    a.out.write_text(json.dumps({"definition":"Per-field complex alm L2 over ell=2..6, all signed m. Zero dust and observer velocities, isotropic emitting photons, proper depth .2, dust fraction .22. Active photon/host/geometry.",
                                 "derivative":"fourth-order symmetric at +/-0.0025,+/-0.005. Positive and negative shear matched. This is a controlled nonlinear response, not an observation.",
                                 "binary_sha256":digest(a.binary),"cases":cases}, indent=2)+"\n")


if __name__ == "__main__":
    main()

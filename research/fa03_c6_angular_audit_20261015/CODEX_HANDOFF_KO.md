# FA03 C6 -> REI Codex scoped handoff

Research owner: BASS branch research/fa03-c6-angular-audit-20261015, based exactly on C5 commit 26a289c4669382f7d25ddc12abc9bb9628bc542f. The BASS original FA02/FA03 sources and fixed-R8 36-ray theorem remain intact.

Reproduce under BASS repo root:

    python3 -m unittest discover -s research/fa03_c6_angular_audit_20261015 -p test_c6.py -v
    python3 research/fa03_c6_angular_audit_20261015/analytic_strip.py
    python3 research/fa03_c6_angular_audit_20261015/mp_cap_snapshot.py --dps 70 --output /tmp/C6_source_new.json
    python3 research/fa03_c6_angular_audit_20261015/mp_full_grey.py --dps 65 --steps 64 --output /tmp/C6_grey_new.json
    python3 research/fa03_c6_angular_audit_20261015/rei_owner_readonly.py --rei-repo /home/cosmosapjw/Dropbox/bianchi/rei_bianchi --out /tmp/REI_readonly_new.json

The REI helper is read-only by construction: refuses output inside active REI, refuses overwrite, records actual original signed terminal/checkpoints independently from potentially stale STATE text, and never starts/stops a worker.

At 2026-10-14T16:05Z, owner HEAD was 6cbdb57010a79eb3bbbc6a54b7f1a75d466702fd. AX07 conditional ZERO completed, AX08 IN_PROGRESS, AX11/AX12 PENDING, global scientific admission NOT_ISSUED. Actual four original signed cases recorded STOPPED_CHECKPOINTED at accepted200000/AXBI_RUNTIME_CAP. PLUS continuation lacked terminal RETURN, and earlier LIVE_WORKERS_OR_CHILDREN_HOLD observer exception remained. STATE still described HALF_MINUS original live despite terminal record. This is a stale descriptive discrepancy, not a new scientific failure or a permission to relaunch.

Relevant adjacent lanes: bass_cr PR65 has threshold-aware remapping including noncommuting redshift, rec_bianchi PR86 has clock-bound photon transport, BASS_HE PR57 has warm P01 H/He-photon Jacobian. None is an automatic replacement for original cold AXBI solver. No owner patch, scheduler action, SOURCE07 rate change, or native gas/ionizing scientific run was made.

C7 next: separately validate BASS full polarized Liouville/screen/source and exact geodesic invariants. C8 next: rigorous propagated complex-strip norm M4, validated radial Gauss3 angular cap bound, and roundoff/time error. The proven strip supports but does not finish that objective.
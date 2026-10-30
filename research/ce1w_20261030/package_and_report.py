"""CE1-W GH runner stage-wise immutable evidence ZIP and generated handoff.

No claims about Drive or Dropbox until their actual provider upload/readback.
Original source lives on the exact Git commit; this ZIP bundles the scoped change
and empirical outputs, not the whole BASS repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile


ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"research/ce1w_20261030"
META={
  "parent_pr":266,
  "parent_head":"2d5076ecb2307cea39c1b608396c34050021ebc3",
  "physical_source_sha256":"022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035",
  "top_dag":{"completed":9,"total":15,"edges":21,"CE1":"PARTIAL"},
  "original_bass_rust_blob":"a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84",
  "fixed_target_h":1e-5,"new_top_level_nodes_complete":0,
  "production_ready":False,"merge_ready":False,"auto_next":False,
}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def report(data, rust):
    header=(
        "# CE1-W | 동일 GL6/GL8 source의 4·8·16 RK4/Hermite MPFR192 시간 오차\n\n"
        "원본 6개 양의 angular cell, 8회 반사, 질량 없는 무충돌·팽창 대각 Bianchi I, "
        "Λ=0, (-,+,+,+), u=t/Tstar, 초기 shear(.2,-.13,-.07), 원래 고정 "
        "기하 h 오차 목표 1e-5를 변경하지 않았다. 실수 판정은 원래 CE1-C/G의 "
        "4차 시간잔차 MPFR192과 정확 이진 Hermite knot jump를 전부 포함한다. "
        "새 source 증명이나 MPFR 형식증명을 반복하지 않으며, BASS Rust는 독립 "
        "binary64 E/P/Eprime 진단이다.\n\n"
        "| GL | 패널 수 | 전체 MPFR h 상계 | 시간+knot | source | 계산 소요초 |\n"
        "|---|---:|---:|---:|---:|---:|\n"
    )
    rows=[]
    for n in (6,8):
        for steps in (4,8,16):
            d=data["cases"][str(n)]["cases"][str(steps)]
            rows.append(f"| {n} | {steps} | {d['final_h_upper']:.17g} | "
                        f"{d['time_jump_h_upper']:.17g} | "
                        f"{d['source_h_upper']:.17g} | "
                        f"{d['cost']['total_seconds']:.3f} |")
    ending=(
      "\n\n**범위:** 모든 수치는 그 실행에서 생성한 저장 경로·구간 잔차의 "
      "조건부 외향 인증이다. 시간 패널마다 저장한 SHA를 비교해 바이트 동일성을 "
      "추정하지 않는다. Rust 진단의 41개 시점·여섯 경로의 E/P/E' 대조는 "
      "독립 메서드의 물리적 parity이며 source/시간 오차를 인증하는 MPFR192 구간이 아니다. "
      "비교한 계산 소요시간은 동등한 GitHub runner·단일 실행에서의 측정값이지 "
      "장치 전반의 성능 보장은 아니다.\n\n"
      "상위 DAG 9/15(21 edges), CE-1 PARTIAL. 별도 저자 R6/C9, "
      "전체 Python/MPFR/Rust 공식검증, 생산용 solver 승인 및 자동 병합 모두 미완료.\n"
    )
    return header+"\n".join(rows)+ending


def handoff(data):
    bits=[
        "$physmath-research-loop",
        "PROJECT=BASS",
        "REPO=cosmosapjw-quantum/bass",
        "UNIT=CE1W_RK4_HERMITE_MPFR192_TIME_PANELS",
        "BRANCH=research/bass-ce1w-rk4-time-panels-rust-mpfr-20261030-r1",
        "PARENT_PR=266",
        "PARENT_HEAD=2d5076ecb2307cea39c1b608396c34050021ebc3",
        "UPPER_DAG=9/15","CE1=PARTIAL",
        "PHYSICS=exact_original_six_cells_positive_massless_collisionless_diagonal_Bianchi_I_Lambda0",
        "SIGNATURE=(-,+,+,+)","PROPER_U_HORIZON=0.08","INITIAL_SHEAR=(0.2,-0.13,-0.07)",
        "TARGET_H=1e-5","SOURCE_GL6_216_RAYS=FROZEN",
        "SOURCE_GL8_384_RAYS=FROZEN",
        "RUST_SOURCE=_rustcore/src/kinetic/comoving.rs",
        "RUST_SOURCE_BLOB=a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84",
        "MPFR_BITS=192","PANEL_COUNTS=4,8,16",
        "SAME_EXACT_RATIONAL_K12_PRESSURE_BOUND=TRUE",
        "RUST_41_EPOCH_E_P_EPRIME=EXECUTED_IN_CI",
    ]
    for n in (6,8):
        for st in (4,8,16):
            x=data["cases"][str(n)]["cases"][str(st)]
            bits.append(f"GL{n}_STEPS{st}_H={x['final_h_upper']:.17g}")
            bits.append(f"GL{n}_STEPS{st}_TIME={x['time_jump_h_upper']:.17g}")
            bits.append(f"GL{n}_STEPS{st}_COST_SECONDS={x['cost']['total_seconds']:.6f}")
    bits += [
        "NEXT:",
        "1. Read live PR current HEAD and GitHub CI logs/artifacts, verify archive receipts.",
        "2. Reuse GL source bounds, raw 4/8/16 panel MPFR residual and original BASS Rust parity.",
        "3. Examine whether 8/16 panel count yields optimal certified time tolerance/cost;",
        "   if time-residual saturation remains, research certified high-order time method.",
        "4. Keep exact six physical cells, source ray hashes, MPFR192 and fixed h target.",
        "5. Do not auto-merge, change physics, or promote production.",
        "6. Publish Git/Drive/Dropbox with actual upload receipts per stage.",
        "7. Keep upper DAG 9/15 until a real upper-node science gate closes.",
        "STOP_AFTER_ONE_BOUNDED_UNIT=true",
        "PRODUCTION_READY=false","MERGE_READY=false","AUTO_NEXT=false",
        "DISTINCT_AUTHOR_R6_C9=NOT_RUN","NATIVE_SUBAGENT=NOT_RUN"
    ]
    return "\n".join(bits)+"\n"


def pack(stage,runner):
    p=Path(runner)
    p.mkdir(parents=True,exist_ok=True)
    source_paths={
        "S0":{"research/ce1w_20261030/S0_THEORY_KO.md":BASE/"S0_THEORY_KO.md"},
        "S1":{
            "research/ce1w_20261030/S0_THEORY_KO.md":BASE/"S0_THEORY_KO.md",
            "research/ce1w_20261030/time_panels.py":BASE/"time_panels.py",
            "research/ce1w_20261030/rust_multistep.py":BASE/"rust_multistep.py",
            "research/ce1w_20261030/tests/test_panel_certificate.py":BASE/"tests/test_panel_certificate.py",
            "research/ce1w_20261030/package_and_report.py":BASE/"package_and_report.py",
            ".github/workflows/ce1w-time-panels.yml":ROOT/".github/workflows/ce1w-time-panels.yml",
            "results/science.json":p/"science.json",
            "results/rust_parity.json":p/"rust_parity.json",
        },
        "S2":{
            "checkpoints/S0.zip":p/"BASS_CE1W_S0.zip",
            "checkpoints/S1.zip":p/"BASS_CE1W_S1.zip",
            "research/ce1w_20261030/S2_FINAL_REPORT_KO.md":p/"S2_FINAL_REPORT_KO.md",
            "research/ce1w_20261030/HANDOFF_NEXT_KO.txt":p/"HANDOFF_NEXT_KO.txt",
            "research/ce1w_20261030/DAG_DELTA.json":p/"DAG_DELTA.json",
            "results/science.json":p/"science.json",
            "results/rust_parity.json":p/"rust_parity.json",
        },
    }
    paths=source_paths[stage]
    artifacts={name:path.read_bytes() for name,path in paths.items()}
    manifest={name:sha(raw) for name,raw in artifacts.items()}
    artifacts["MANIFEST_SHA256.json"]=(json.dumps(manifest,indent=2)+"\n").encode()
    destination=p/f"BASS_CE1W_{stage}.zip"
    with zipfile.ZipFile(destination,"w",zipfile.ZIP_DEFLATED) as z:
        for name,raw in artifacts.items():
            z.writestr(name,raw)
    with zipfile.ZipFile(destination) as z:
        assert z.testzip() is None
        for name,expected in manifest.items():
            assert sha(z.read(name))==expected
    print(f"CE1W_{stage}_ARCHIVE_CREATED",destination, destination.stat().st_size,sha(destination.read_bytes()),flush=True)
    return destination


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--stage",choices=["S0","S1","S2"],required=True)
    parser.add_argument("--runner",required=True)
    args=parser.parse_args()
    directory=Path(args.runner)
    directory.mkdir(parents=True,exist_ok=True)
    if args.stage=="S2":
        d=json.loads((directory/"science.json").read_text())
        rust=json.loads((directory/"rust_parity.json").read_text())
        (directory/"S2_FINAL_REPORT_KO.md").write_text(report(d,rust))
        (directory/"HANDOFF_NEXT_KO.txt").write_text(handoff(d))
        dag={**META,"unit":"CE1W","status":"SCOPED_CERTIFIED_TIME_PANELS",
             "source_science":d,"rust":rust,
             "distinct_author_R6_C9":"NOT_RUN",
             "formal_program_proof":"NOT_RUN"}
        (directory/"DAG_DELTA.json").write_text(json.dumps(dag,indent=2,allow_nan=False)+"\n")
    pack(args.stage,directory)


if __name__=="__main__":
    main()

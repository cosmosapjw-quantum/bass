from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path

GENERATOR_VERSION = "1.0.0"
POL_AUTHORITY_SHA256 = "b4becce7e7162991c63b7f065d56c6a29c4123b9b9030eb8eba1b30eee3a3a6b"
AUTHORITY_HASHES = {
    "_rustcore/src/kinetic/pol_collide.rs": "c6cb5099b139a4f04a5693d1f07ae8bffd90acc9b5ffd32579532a2dce5fe202",
    "audit/p3_polarized_thomson.py": "eb5ba68a22c88f88026bdd27898e5b6e03abae901f7aa9a0982389f5d7436255",
    "audit/p9_boost_screen.py": "8ab2545b535cf89a3cf2b3ae45d2d0a8e9df0d8a1e6695f979dd29dd60f8aed9",
    "bianchi/q/polstate.py": "3ebabbfe264a50dfe2fd0a2e39c279b201a6911a9711abd9f698f9ad53264da1",
    "docs/P-DERIVATION.md": "a25e1f897a71efbba02f3d971dd36fcff8c20f3b3abfb36c9cb06401681fd91d",
}

def sha256_bytes(x: bytes) -> str:
    return hashlib.sha256(x).hexdigest()

def generate(output_dir: Path, rustfmt: str = "rustfmt") -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    template = Path(__file__).with_name("templates") / "typeii_polarized.rs.in"
    source = template.read_text().replace("__POL_AUTHORITY_SHA256__", POL_AUTHORITY_SHA256)
    target = output_dir / "typeii_polarized.rs"
    target.write_text(source)
    subprocess.run([rustfmt, str(target)], check=True)
    module_sha = sha256_bytes(target.read_bytes())
    manifest = {
        "schema": "bass-generated-rust-polarization-v1",
        "stage": "G-POL-RUNTIME-II",
        "generator_version": GENERATOR_VERSION,
        "polarization_authority_sha256": POL_AUTHORITY_SHA256,
        "authority_hashes": AUTHORITY_HASHES,
        "generated_files": {"typeii_polarized.rs": module_sha},
        "semantics": {
            "carrier": "basis-free rank-9 coherency tensor: symmetric 6 + antisymmetric/V 3",
            "collision": "finite-electron-tilt rest-frame rank-9 Thomson generator, matrix-free O(Nang)",
            "boost": "canonical gauge-restored screen isometry plus D^4 amplitude and dOmega/D^2 weights",
            "projector": "rank-one boosted unpolarized equilibrium projector",
            "kato": "matrix-free [Pdot,P] action on the polarized moving equilibrium manifold",
        },
    }
    (output_dir / "polarized_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("output_dir", type=Path)
    ap.add_argument("--rustfmt", default="rustfmt")
    args = ap.parse_args()
    print(json.dumps(generate(args.output_dir, args.rustfmt), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()

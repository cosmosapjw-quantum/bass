"""Read-only extraction of four stored S8 births; no physics solver is imported."""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import struct

RAW_SHA256 = "fdc70eaaea45804aa16e60bba495b283eb5e4a18a576f52d5519bfd5a1f05839"
RAW_GIT_BLOB = "0dd1c3a13f393f9274c4e1a0d14409a28b1f9138"
SOURCE_COMMIT = "d0c0313d6c063037fd8e067744aee66235df1a58"


def sha_array(x):
    return hashlib.sha256(b"".join(struct.pack("<d", v) for v in x)).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raw", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    raw = args.raw.read_bytes()
    assert len(raw) == 959031 and hashlib.sha256(raw).hexdigest() == RAW_SHA256
    assert hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest() == RAW_GIT_BLOB
    lines = gzip.decompress(raw).splitlines()
    rows = [json.loads(s) for s in lines]
    lexemes = [json.loads(s, parse_float=str, parse_int=str) for s in lines]
    index = {r["case_id"]: i for i, r in enumerate(rows) if "case_id" in r}
    failure_i = index["b9_n64_P2P4"]
    failure = rows[failure_i]
    assert failure["status"] == "NUMERICAL_FAILURE" and failure["failed_birth"] == 11
    assert "INNER_P2_PRECISION_LIMIT" in str(failure["failure"])
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output/"ORIGINAL_S8_FAILURE.json").write_bytes(lines[failure_i]+b"\n")
    summaries = []
    for name in ("b9_n64", "b9_n128", "b9_n256", "b6_n64"):
        i = index[name+"_prior"]
        j = index[name+"_P2"]
        birth, paired = rows[i]["births"][11], rows[j]["births"][11]
        lexical_birth, lexical_paired = lexemes[i]["births"][11], lexemes[j]["births"][11]
        mu, prior = birth["mu"], birth["prior"]
        assert all(mu[k] == -mu[-1-k] for k in range(len(mu)))
        assert prior == prior[::-1] and min(prior) > 0
        assert all(a < b for a,b in zip(mu, mu[1:]))
        assert birth["u"] == 0.5750000000000001
        for field in ("mu", "prior"):
            assert sha_array(birth[field]) == sha_array(paired[field])
            assert lexical_birth[field] == lexical_paired[field]
        if name == "b9_n64":
            assert sha_array(failure["support_mu"]) == sha_array(mu)
            assert failure["failed_u"] == birth["u"]
            assert lexemes[failure_i]["support_mu"] == lexical_birth["mu"]
        meta = {
            "schema":"BASS_S11_ARCHIVED_BIRTH_INPUT_V1", "case":name,
            "source_commit":SOURCE_COMMIT, "source_raw_sha256":RAW_SHA256,
            "source_raw_git_blob":RAW_GIT_BLOB, "source_case_id":name+"_prior",
            "source_jsonl_line_1based":i+1, "independent_stored_P2_row_1based":j+1,
            "birth_index_0based":11, "u":birth["u"], "b":birth["b"],
            "usage":"Immutable saved input for a new explicitly isotropic birth candidate; no historical weight is overwritten.",
            "mu_sha256_le_f64":sha_array(mu), "prior_sha256_le_f64":sha_array(prior)
        }
        # Keep every original numeric token of mu/prior, not just rounded
        # decimal reformatting. JSON whitespace is newly formatted and is not
        # claimed identical to the archived row.
        head = json.dumps(meta, ensure_ascii=False, indent=2)[:-2]
        data = head+',\n  "mu": ['+", ".join(lexical_birth["mu"])+'],\n  "prior": ['+", ".join(lexical_birth["prior"])+']\n}\n'
        output = args.output/(name+"_birth11_input.json")
        output.write_text(data)
        readback = json.loads(output.read_text())
        assert sha_array(readback["mu"]) == sha_array(mu)
        assert sha_array(readback["prior"]) == sha_array(prior)
        summaries.append({"case":name,"input_file":output.name,"bytes":output.stat().st_size,
            "sha256":hashlib.sha256(output.read_bytes()).hexdigest(),"n_mu":len(mu),
            "u":birth["u"],"b":birth["b"],"max_mu_squared_float_diagnostic":max(mu)**2,
            "prior_fsum":math.fsum(prior),"prior_minimum":min(prior),
            "original_numeric_tokens_preserved":True,"stored_prior_P2_rows_match_bits_and_tokens":True,
            "mu_sha256_le_f64":sha_array(mu),"prior_sha256_le_f64":sha_array(prior)})
    receipt = {"schema":"BASS_S11_S8_READONLY_EXTRACTION_V1", "status":"PASS_EXACT_INPUT_IDENTITY",
        "source_commit":SOURCE_COMMIT,"raw_bytes":len(raw),"raw_sha256":RAW_SHA256,"raw_git_blob":RAW_GIT_BLOB,
        "source_metadata":rows[-1],"original_failure_row_1based":failure_i+1,
        "original_failure":"ORIGINAL_S8_FAILURE.json","failure_support_matches_b9_n64_birth11":True,
        "inputs":summaries,"normalization_or_reweighting_performed":False,
        "solver_imports":[],"historical_history_replays":0}
    (args.output/"INPUT_EXTRACTION.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"status":receipt["status"],"inputs":summaries},ensure_ascii=False))


if __name__ == "__main__":
    main()

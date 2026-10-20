#!/usr/bin/env python3
"""Exact fixed-support P24 feasibility observer; never calls a projector/ODE.

Reads the previously completed S8 prior row, preserving its actual binary64
support. No compiler, owner library, projector, geometry evaluator or ODE is
executed. New source must be published and fully read back before use.
"""
from __future__ import annotations
import argparse
import gzip
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import sys

HERE = Path(__file__).resolve().parent
UNIT = HERE.parent
OWNER = "0e25846433170d0f420c4cda44a0bedbf02cd177"
ORIGINAL_SHA = "d1a0cf8180da93f85d95296bf94a09b8da86f2b3f2c521f8adcf5eb4cb8447c6"
EPS = F(3, 10**15)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bits(value):
    return f"{struct.unpack('<Q', struct.pack('<d', float(value)))[0]:016x}"


def binary64(word):
    if not isinstance(word, str) or not re.fullmatch(r"[0-9a-f]{16}", word):
        raise ValueError("BINARY64_BITS")
    value = struct.unpack('<d', struct.pack('<Q', int(word, 16)))[0]
    if not math.isfinite(value):
        raise ValueError("NONFINITE_BINARY64")
    return value


def exact(value):
    return F.from_float(value)


def exp_interval(x, order=64):
    """Positive Taylor series and a rational geometric tail enclosure."""
    if not F(0) <= x < order+2:
        raise ValueError("EXP_TAYLOR_DOMAIN")
    term = total = F(1)
    for k in range(1, order+1):
        term *= x/k
        total += term
    next_term = term*x/(order+1)
    tail = next_term/(1-x/(order+2))
    return total, total+tail


def rational_record(x):
    return {"exact": str(x), "display_float": float(x)}


def facet(a0, a1, a2, label):
    # E[q(z)]=A*n+B*M2+C*M4 for q=a0+a1*z+a2*z^2.
    # A negative upper bound contradicts q>=0 on the actual support even at
    # the unchanged unnormalized norm/P2/P4 gate EPS.
    A = a0+a1/3+a2/5
    B = 2*a1/3+4*a2/7
    C = 8*a2/35
    upper = A+EPS*(abs(A)+abs(B)+abs(C))
    return {"facet": label, "polynomial": list(map(str, (a0, a1, a2))),
            "target_slack": rational_record(A),
            "maximum_under_existing_gates": rational_record(upper),
            "infeasible_at_existing_gates": upper < 0}


def certificate(mu, nu, b):
    z = sorted(set(exact(m)**2 for m in mu))
    if len(z) < 3:
        raise ValueError("P24_FULL_RANK_REQUIRED")
    facets = [facet(a*c, -a-c, F(1), f"adjacent_{i}")
              for i, (a, c) in enumerate(zip(z, z[1:]))]
    facets.append(facet(-z[0]*z[-1], z[0]+z[-1], F(-1), "endpoint_chord"))
    slacks = [F(f["target_slack"]["exact"]) for f in facets]
    at_gate = [f for f in facets if f["infeasible_at_existing_gates"]]
    cap = facet(F(0), z[-1], F(-1), "z_times_zmax_minus_z")
    # Ideal continuum-in-geometry map at these same represented nu and b:
    # z=nu^2/(exp(6*b)*(1-nu^2)+nu^2). We do not assume libm ulp accuracy.
    # Compare the observed native binary64 z to this rigorous rational interval.
    t = max(exact(m)**2 for m in nu)
    el, eh = exp_interval(6*exact(b))
    zl = t/(eh*(1-t)+t)
    zh = t/(el*(1-t)+t)
    discrepancy = max(abs(z[-1]-zl), abs(z[-1]-zh))
    return {"distinct_z": len(z), "z_min": rational_record(z[0]),
            "z_max": rational_record(z[-1]), "facets": facets,
            "exact_target_status": "STRICT_INTERIOR" if min(slacks)>0 else
                ("OUTSIDE" if min(slacks)<0 else "BOUNDARY"),
            "minimum_target_facet_slack": rational_record(min(slacks)),
            "infeasible_at_existing_gates": bool(at_gate) or cap["infeasible_at_existing_gates"],
            "negative_upper_bound_facets": [f["facet"] for f in at_gate],
            "simple_zmax_certificate": cap,
            "ideal_geometry_zmax_interval": {"lower": rational_record(zl),
                "upper": rational_record(zh), "exp_taylor_order": 64,
                "exp_interval_width": rational_record(eh-el)},
            "native_vs_ideal_zmax_absolute_error_upper": rational_record(discrepancy)}



def atomic_json(path, value):
    data=(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+"\n").encode()
    temporary=path.with_name(path.name+'.tmp-'+str(os.getpid()))
    try:
        with temporary.open('xb') as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        # Hard link is an atomic create-only publication in this same directory.
        os.link(temporary,path)
        temporary.unlink()
        directory_fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
        try: os.fsync(directory_fd)
        finally: os.close(directory_fd)
    finally:
        if temporary.exists(): temporary.unlink()


def no_constant(value):
    raise ValueError('NONFINITE_JSON_CONSTANT:'+value)


def load_json(data, tokens=False):
    return json.loads(data,parse_float=str if tokens else float,parse_constant=no_constant)


def verify_source_binding(path, source_commit):
    raw=path.read_bytes();binding=load_json(raw)
    if (binding.get('source_commit')!=source_commit
            or not re.fullmatch('[0-9a-f]{40}',str(binding.get('source_tree','')))
            or binding.get('git_readback_pass') is not True
            or binding.get('complete_tree') is not True):
        raise ValueError('FULL_REMOTE_READBACK_BINDING_REQUIRED')
    files=binding.get('files')
    if not isinstance(files,list): raise ValueError('BINDING_FILES')
    table={}
    for item in files:
        key=item['path']
        if key in table: raise ValueError('DUPLICATE_BOUND_PATH')
        table[key]=item
    manifest_raw=(HERE/'SOURCE_MANIFEST.json').read_bytes()
    manifest=load_json(manifest_raw)
    local_files=manifest['files']+[{'path':'SOURCE_MANIFEST.json','bytes':len(manifest_raw),'sha256':sha(manifest_raw)}]
    checked=[]
    for expected in local_files:
        rel=Path(expected['path'])
        if rel.is_absolute() or '..' in rel.parts: raise ValueError('SOURCE_PATH_SCOPE')
        data=(HERE/rel).read_bytes()
        key='research/bass_isotropy_response_20261018/s12_birth_memory/native_support/'+rel.as_posix()
        item=table.get(key)
        git_blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if (not item or item.get('pass') is not True
                or len(data)!=expected['bytes'] or sha(data)!=expected['sha256']
                or item.get('bytes')!=len(data) or item.get('sha256')!=sha(data)
                or item.get('git_blob')!=git_blob):
            raise ValueError('SOURCE_READBACK_IDENTITY:'+key)
        checked.append({'path':key,'bytes':len(data),'sha256':sha(data),'git_blob':git_blob})
    return {'binding_sha256':sha(raw),'source_tree':binding['source_tree'],
            'all_source_files_match_published_remote_readback':True,'files':checked}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-commit',required=True)
    p.add_argument('--binding',type=Path,required=True)
    p.add_argument('--original-gzip',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if not re.fullmatch('[0-9a-f]{40}',a.source_commit):
        raise ValueError('IMMUTABLE_OBSERVER_SOURCE_COMMIT_REQUIRED')
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
    result={'schema':'BASS_S12_STORED_NATIVE_SUPPORT_CERTIFICATE_V1','status':'FAILED',
        'observer_source_commit':a.source_commit,'original_evidence_archive_commit':'d0c0313d6c063037fd8e067744aee66235df1a58',
        'owner_commit':OWNER,'started_utc':datetime.now(timezone.utc).isoformat(),
        'geometry_calls':0,'compiler_calls':0,'projector_calls':0,'ODE_calls':0,
        'native_history_calls':0,'old_campaign_calls':0,'gate_exact':str(EPS),
        'activity':'Read previously completed raw support and compute exact rational feasibility certificates.'}
    try:
        result['source_binding']=verify_source_binding(a.binding.resolve(),a.source_commit)
        prov=load_json((HERE/'INPUT_PROVENANCE.json').read_bytes())
        gz=a.original_gzip.read_bytes()
        if (len(gz)!=prov['gzip_bytes'] or sha(gz)!=prov['gzip_sha256']
                or hashlib.sha1(b'blob '+str(len(gz)).encode()+b'\0'+gz).hexdigest()!=prov['gzip_git_blob']):
            raise ValueError('ORIGINAL_GZIP_IDENTITY')
        decompressed=gzip.decompress(gz)
        if len(decompressed)!=prov['decompressed_bytes'] or sha(decompressed)!=prov['decompressed_sha256']:
            raise ValueError('ORIGINAL_DECOMPRESSED_IDENTITY')
        raw=(HERE/'inputs/B9_N64_PRIOR_ORIGINAL_ROW.json').read_bytes()
        lines=decompressed.splitlines()
        footer=load_json(lines[-1])
        if len(lines)!=19 or footer!={'schema':'bass.native.angular.s8.complete.v1','rows':18,'owner_commit':OWNER,'source_id':'MD14_Z002_FESC_BB50K_13P6_100_V1'}:
            raise ValueError('ORIGINAL_NATIVE_COMPLETION_OWNER')
        if (len(raw)!=prov['row_bytes'] or sha(raw)!=prov['row_sha256']
                or lines[prov['row_index_zero_based']]!=raw):
            raise ValueError('EXTRACTED_ROW_IDENTITY')
        row=load_json(raw);tokens=load_json(raw,tokens=True)
        expected={'schema':'bass.native.angular.s8.row.v1','case_id':'b9_n64_prior','n_mu':64,
            'b0':0.9,'mode':'prior','n_energy':96,'cells_per_segment':32,'cohorts':16,
            'beta':0.2,'x_observe':1.0,'status':'MEASURED','source_id':'MD14_Z002_FESC_BB50K_13P6_100_V1'}
        if any(row.get(k)!=v for k,v in expected.items()): raise ValueError('ORIGINAL_FIXED_CONFIGURATION')
        if len(row['reference_nu'])!=64 or len(row['births'])!=16: raise ValueError('ORIGINAL_FIXED_COUNTS')
        old_raw=(HERE/'inputs/ORIGINAL_S8_FAILURE.json').read_bytes()
        if sha(old_raw)!=ORIGINAL_SHA: raise ValueError('ORIGINAL_FAILURE_IDENTITY')
        old=load_json(old_raw)
        if old['failed_birth']!=11 or old['failed_u']!=row['births'][11]['u']:
            raise ValueError('ORIGINAL_FAILURE_BIRTH')
        if list(map(bits,row['reference_nu']))!=list(map(bits,old['reference_nu'])):
            raise ValueError('REFERENCE_NU_BIT_IDENTITY')
        nu=row['reference_nu']
        if (any(not math.isfinite(m) or abs(m)>1 for m in nu)
                or any(x>=y for x,y in zip(nu,nu[1:])) or nu!=[-m for m in nu[::-1]]):
            raise ValueError('REFERENCE_GRID_DOMAIN_PARITY')
        certificates=[];support_tokens=[]
        for j,birth in enumerate(row['births']):
            u,b=birth['u'],birth['b']
            if bits(u)!=bits(0.8*(j+0.5)/16.0) or bits(b)!=bits(0.9+0.2*u):
                raise ValueError('FIXED_NATIVE_BIRTH_SCHEDULE')
            mu=birth['mu']
            if (len(mu)!=64 or any(not math.isfinite(m) or abs(m)>1 for m in mu)
                    or any(x>=y for x,y in zip(mu,mu[1:])) or mu!=[-m for m in mu[::-1]]):
                raise ValueError('ACTUAL_SUPPORT_DOMAIN_PARITY')
            item=certificate(mu,nu,b)
            item.update(birth=j,u=u,b=b,u_bits=bits(u),b_bits=bits(b),mu_bits=list(map(bits,mu)))
            certificates.append(item)
            support_tokens.append({'birth':j,'u_token':tokens['births'][j]['u'],
                'b_token':tokens['births'][j]['b'],'mu_tokens':tokens['births'][j]['mu'],
                'mu_bits':item['mu_bits']})
        old_bits=list(map(bits,old['support_mu']))
        matches=sum(x==y for x,y in zip(certificates[11]['mu_bits'],old_bits))
        if matches!=64 or len(old_bits)!=64: raise ValueError('ORIGINAL_BIRTH11_BINARY64_IDENTITY')
        # Fixed proof controls exercise exact facet and unchanged-gate arithmetic,
        # without calling the old or new projector on any support.
        controls=[]
        for name,z,expected_status in [
            ('rational_interior',[F(0),F(1,3),F(1)],'STRICT_INTERIOR'),
            ('rational_boundary',[F(0),F(3,5),F(1)],'BOUNDARY'),
            ('rational_outside',[F(0),F(1,5),F(1,2)],'OUTSIDE')]:
            fs=[facet(x*y,-x-y,F(1),str(i)) for i,(x,y) in enumerate(zip(z,z[1:]))]
            fs.append(facet(-z[0]*z[-1],z[0]+z[-1],F(-1),'endpoint'))
            slack=min(F(f['target_slack']['exact']) for f in fs)
            status='STRICT_INTERIOR' if slack>0 else ('OUTSIDE' if slack<0 else 'BOUNDARY')
            gate_outside=any(f['infeasible_at_existing_gates'] for f in fs)
            passed=status==expected_status and gate_outside==(expected_status=='OUTSIDE')
            controls.append({'id':name,'z':list(map(str,z)),'expected':expected_status,
                'actual':status,'infeasible_at_existing_gates':gate_outside,'pass':passed})
        if not all(c['pass'] for c in controls): raise ValueError('RATIONAL_PROOF_CONTROL')
        atomic_json(out/'ORIGINAL_NUMERIC_TOKEN_READBACK.json',{
            'reference_nu_tokens':tokens['reference_nu'],'reference_nu_bits':list(map(bits,nu)),
            'births':support_tokens})
        result.update(original_gzip_sha256=sha(gz),original_decompressed_sha256=sha(decompressed),
            original_row_sha256=sha(raw),original_failure_sha256=sha(old_raw),
            fixed_configuration_verified=expected,original_birth11_bit_matches=matches,
            original_birth11_ray_count=64,certificates=certificates,rational_proof_controls=controls,
            first_exact_target_outside=next((i for i,c in enumerate(certificates) if c['exact_target_status']=='OUTSIDE'),None),
            first_infeasible_at_existing_gate=next((i for i,c in enumerate(certificates) if c['infeasible_at_existing_gates']),None),
            native_history_completion_inferred=False,continuum_or_full_spectral_claim=False,
            old_physical_weights_mutated=False,new_projected_weights_produced=False)
        result['status']='PASS_SCOPED_STORED_SUPPORT_EXACT_CERTIFICATES'
    except Exception as exc:
        result['failure']={'type':type(exc).__name__,'message':str(exc)}
    result['finished_utc']=datetime.now(timezone.utc).isoformat()
    atomic_json(out/'RETURN_SUPPORT_PREFLIGHT.json',result)
    print(json.dumps({k:result.get(k) for k in ['status','first_exact_target_outside',
        'first_infeasible_at_existing_gate','original_birth11_bit_matches','failure']},allow_nan=False))
    return 0 if result['status'].startswith('PASS_') else 1


if __name__=='__main__':
    raise SystemExit(main())

"""Bind an actual locked binary build to its client, owner and upstream hashes.

A successful test or a merely existing executable cannot create this attestation.
Explicit prior-build reuse verifies the recorded source and actual executable
bytes, and labels reuse instead of claiming a new compilation.
"""
from __future__ import annotations
import copy
import hashlib
from pathlib import Path

CLIENT_FILES=('Cargo.toml','Cargo.lock','src/lib.rs','src/main.rs','tests/adapter_contracts.rs')
IDENTITY_FIELDS=('client_source_sha256','balance_owner_sha256','vigilode_source','vigilode_tree',
                 'source_files_verified','source_bytes')

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def exact_binary_build(record):
    command=record.get('command',[])
    return (record.get('exit_code')==0 and len(command)==5
            and command[1:]==['build','--locked','--bin','bass-s9-vigilode'])

def source_identity(receipt):
    identity={key:copy.deepcopy(receipt[key]) for key in IDENTITY_FIELDS}
    if set(identity['client_source_sha256'])!=set(CLIENT_FILES):
        raise ValueError('INCOMPLETE_COMPILED_CLIENT_IDENTITY')
    return identity

def prior_build_record(receipt):
    attestation=receipt.get('binary_attestation')
    if attestation is not None:
        record=attestation.get('build_command_record',{})
        if not exact_binary_build(record): raise ValueError('NO_SUCCESSFUL_LOCKED_BINARY_BUILD')
        if attestation.get('source_identity')!=source_identity(receipt):
            raise ValueError('ATTESTED_BUILD_SOURCE_MISMATCH')
        if attestation.get('binary_sha256')!=receipt.get('binary',{}).get('sha256'):
            raise ValueError('ATTESTED_BUILD_BINARY_MISMATCH')
        return record
    # Migration of the genuine prepublication v1 receipt is explicit only.
    records=[r for r in receipt.get('commands',[]) if exact_binary_build(r)]
    if not records: raise ValueError('NO_SUCCESSFUL_LOCKED_BINARY_BUILD')
    return records[-1]

def attest_build(receipt,binary,expected_identity,*,mode,origin_receipt_sha256=None):
    if mode not in ('fresh_build','verified_prior_build'): raise ValueError('BUILD_ATTESTATION_MODE')
    if receipt.get('status')!='prepared': raise ValueError('BUILD_RECEIPT_NOT_SUCCESSFUL')
    if source_identity(receipt)!=expected_identity: raise ValueError('COMPILED_CLIENT_OR_OWNER_SOURCE_MISMATCH')
    actual=sha(binary)
    if receipt.get('binary',{}).get('sha256')!=actual: raise ValueError('COMPILED_BINARY_BYTES_MISMATCH')
    record=prior_build_record(receipt)
    if mode=='fresh_build' and not any(exact_binary_build(r) for r in receipt.get('commands',[])):
        raise ValueError('NO_BINARY_BUILD_IN_CURRENT_INVOCATION')
    if mode=='verified_prior_build' and not origin_receipt_sha256:
        raise ValueError('PRIOR_BUILD_RECEIPT_HASH_REQUIRED')
    return {'schema':'BASS_S9_BINARY_ATTESTATION_V1','mode':mode,
            'source_identity':copy.deepcopy(expected_identity),'binary_sha256':actual,
            'build_command_record':copy.deepcopy(record),
            'origin_receipt_sha256':origin_receipt_sha256,
            'new_compilation_performed':mode=='fresh_build'}

def validate_attestation(receipt,binary):
    attestation=receipt.get('binary_attestation')
    if receipt.get('schema')!='BASS_S9_PREPARATION_V2' or not attestation:
        raise ValueError('EXPLICIT_BINARY_BUILD_ATTESTATION_REQUIRED')
    if attestation.get('schema')!='BASS_S9_BINARY_ATTESTATION_V1': raise ValueError('BINARY_ATTESTATION_SCHEMA')
    expected=source_identity(receipt)
    # Recheck the actual binary and every copied identity field, including when
    # the original genuine build is deliberately reused after runner-only edits.
    attest_build(receipt,binary,expected,mode=attestation['mode'],
                 origin_receipt_sha256=attestation.get('origin_receipt_sha256'))
    return attestation

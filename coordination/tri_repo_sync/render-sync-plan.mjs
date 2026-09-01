#!/usr/bin/env node

import fs from 'node:fs';
import process from 'node:process';
import { canonicalHash } from './compile-dag.mjs';

function parseArgs(argv) {
  const values = {};
  for (let index = 0; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!key?.startsWith('--') || value === undefined) throw new Error(`invalid argument sequence near ${key ?? '<end>'}`);
    values[key.slice(2)] = value;
  }
  for (const required of ['compiled', 'policy', 'output']) {
    if (!values[required]) throw new Error(`missing --${required}`);
  }
  return values;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const compiled = JSON.parse(fs.readFileSync(args.compiled, 'utf8'));
  const policy = JSON.parse(fs.readFileSync(args.policy, 'utf8'));
  const receipt = {
    schema_version: '1.0.0',
    program_id: 'BASS-REC-REI-FORMULA-SYNC-V1',
    stage_id: 'SYNC_01_AUTOMATED_AUDIT',
    status: compiled.status,
    compiled_dag_sha256: canonicalHash(compiled),
    source_lanes: compiled.source_lanes,
    grouped_states: compiled.grouped_states,
    stale_imports: compiled.stale_imports,
    global_errors: compiled.global_errors,
    manual_scientific_promotion: compiled.manual_scientific_promotion,
    destination_plan: {
      github: 'audit artifact and coordination-branch snapshot',
      dropbox: 'versioned connector publication after exact GitHub readback',
      atlassian: 'Confluence/Jira mirror after exact GitHub and Dropbox readback',
    },
    schedule: policy.cadence,
    activation_gate: policy.activation_gate,
    claim_boundary: 'CONTROL_PLANE_CLASSIFICATION_ONLY_NO_SCIENTIFIC_PROMOTION',
  };
  fs.writeFileSync(args.output, `${JSON.stringify(receipt, null, 2)}\n`, 'utf8');
  process.stdout.write(`${JSON.stringify({ status: receipt.status, output: args.output, compiled_dag_sha256: receipt.compiled_dag_sha256 })}\n`);
}

try {
  main();
} catch (error) {
  process.stderr.write(`${error.stack ?? error.message}\n`);
  process.exitCode = 1;
}

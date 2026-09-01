#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

function parseArgs(argv) {
  const values = {};
  for (let index = 0; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!key?.startsWith('--') || value === undefined) {
      throw new Error(`invalid argument sequence near ${key ?? '<end>'}`);
    }
    values[key.slice(2)] = value;
  }
  for (const required of ['rec-repo', 'rec-ref', 'rei-repo', 'rei-ref', 'output-dir']) {
    if (!values[required]) throw new Error(`missing --${required}`);
  }
  return values;
}

async function fetchManifest(repository, ref, expectedLane, token) {
  const api = new URL(`https://api.github.com/repos/${repository}/contents/coordination/tri_repo_sync/LANE_MANIFEST.json`);
  api.searchParams.set('ref', ref);
  const headers = {
    Accept: 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
    'User-Agent': 'bass-tri-repo-sync-audit',
  };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(api, { headers });
  if (!response.ok) {
    throw new Error(`failed to fetch ${repository}@${ref}: HTTP ${response.status}`);
  }
  const payload = await response.json();
  if (payload.encoding !== 'base64' || typeof payload.content !== 'string') {
    throw new Error(`unexpected GitHub contents payload for ${repository}`);
  }
  const manifest = JSON.parse(Buffer.from(payload.content.replace(/\n/g, ''), 'base64').toString('utf8'));
  if (manifest.lane !== expectedLane) {
    throw new Error(`expected lane ${expectedLane}, received ${manifest.lane}`);
  }
  if (manifest.repository !== repository) {
    throw new Error(`manifest repository mismatch: expected ${repository}, received ${manifest.repository}`);
  }
  return manifest;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const token = process.env.GITHUB_TOKEN ?? '';
  const outputDirectory = path.resolve(args['output-dir']);
  fs.mkdirSync(outputDirectory, { recursive: true });
  const [rec, rei] = await Promise.all([
    fetchManifest(args['rec-repo'], args['rec-ref'], 'rec_bianchi', token),
    fetchManifest(args['rei-repo'], args['rei-ref'], 'rei_bianchi', token),
  ]);
  const outputs = [
    ['REC_LANE_MANIFEST.json', rec],
    ['REI_LANE_MANIFEST.json', rei],
  ];
  for (const [name, value] of outputs) {
    fs.writeFileSync(path.join(outputDirectory, name), `${JSON.stringify(value, null, 2)}\n`, 'utf8');
  }
  process.stdout.write(`${JSON.stringify({
    status: 'PASS',
    rec_commit: rec.source.commit,
    rei_commit: rei.source.commit,
    output_dir: outputDirectory,
  })}\n`);
}

main().catch((error) => {
  process.stderr.write(`${error.stack ?? error.message}\n`);
  process.exitCode = 1;
});

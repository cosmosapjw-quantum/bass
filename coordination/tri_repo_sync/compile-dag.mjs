#!/usr/bin/env node

import fs from 'node:fs';
import crypto from 'node:crypto';
import process from 'node:process';
import { pathToFileURL } from 'node:url';

const ALLOWED_ROLES = new Set(['authority', 'consumer', 'adapter', 'oracle', 'audit']);
const ALLOWED_STATUSES = new Set([
  'not_started',
  'in_progress',
  'blocked',
  'validated_non_durable',
  'pass',
  'invalid',
]);

function isObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

export function canonicalize(value) {
  if (Array.isArray(value)) {
    return value.map(canonicalize);
  }
  if (isObject(value)) {
    return Object.fromEntries(
      Object.keys(value)
        .sort()
        .map((key) => [key, canonicalize(value[key])]),
    );
  }
  return value;
}

export function canonicalHash(value) {
  const text = JSON.stringify(canonicalize(value));
  return crypto.createHash('sha256').update(text, 'utf8').digest('hex');
}

function assertString(value, label) {
  if (typeof value !== 'string' || value.length === 0) {
    throw new TypeError(`${label} must be a non-empty string`);
  }
}

function validateRegistry(registry) {
  if (!isObject(registry)) throw new TypeError('registry must be an object');
  assertString(registry.schema_version, 'registry.schema_version');
  assertString(registry.registry_id, 'registry.registry_id');
  if (!Array.isArray(registry.maturity_order) || registry.maturity_order.length === 0) {
    throw new TypeError('registry.maturity_order must be a non-empty array');
  }
  const maturitySet = new Set(registry.maturity_order);
  if (maturitySet.size !== registry.maturity_order.length) {
    throw new TypeError('registry.maturity_order must not contain duplicates');
  }
  if (!Array.isArray(registry.formula_families) || registry.formula_families.length === 0) {
    throw new TypeError('registry.formula_families must be a non-empty array');
  }
  const ids = new Set();
  for (const family of registry.formula_families) {
    if (!isObject(family)) throw new TypeError('formula family must be an object');
    assertString(family.id, 'family.id');
    assertString(family.owner_lane, `${family.id}.owner_lane`);
    assertString(family.target_maturity, `${family.id}.target_maturity`);
    if (!maturitySet.has(family.target_maturity)) {
      throw new TypeError(`${family.id}.target_maturity is not declared`);
    }
    if (ids.has(family.id)) throw new TypeError(`duplicate family id: ${family.id}`);
    ids.add(family.id);
    if (!Array.isArray(family.promotion_requires)) {
      throw new TypeError(`${family.id}.promotion_requires must be an array`);
    }
    if (!Array.isArray(family.prerequisites)) {
      throw new TypeError(`${family.id}.prerequisites must be an array`);
    }
    for (const dependency of family.prerequisites) {
      if (!isObject(dependency)) throw new TypeError(`${family.id} dependency must be an object`);
      assertString(dependency.family, `${family.id}.dependency.family`);
      assertString(dependency.minimum_maturity, `${family.id}.dependency.minimum_maturity`);
      if (!maturitySet.has(dependency.minimum_maturity)) {
        throw new TypeError(`${family.id} dependency maturity is not declared`);
      }
    }
  }
  for (const family of registry.formula_families) {
    for (const dependency of family.prerequisites) {
      if (!ids.has(dependency.family)) {
        throw new TypeError(`${family.id} depends on unknown family ${dependency.family}`);
      }
    }
  }
}

function validateManifest(manifest, maturitySet) {
  if (!isObject(manifest)) throw new TypeError('lane manifest must be an object');
  assertString(manifest.schema_version, 'manifest.schema_version');
  assertString(manifest.lane, 'manifest.lane');
  assertString(manifest.repository, `${manifest.lane}.repository`);
  if (!isObject(manifest.source)) throw new TypeError(`${manifest.lane}.source must be an object`);
  for (const key of ['branch', 'commit', 'tree']) {
    assertString(manifest.source[key], `${manifest.lane}.source.${key}`);
  }
  if (!Array.isArray(manifest.families)) {
    throw new TypeError(`${manifest.lane}.families must be an array`);
  }
  const seen = new Set();
  for (const entry of manifest.families) {
    if (!isObject(entry)) throw new TypeError(`${manifest.lane} family entry must be an object`);
    assertString(entry.family, `${manifest.lane}.family`);
    assertString(entry.role, `${manifest.lane}.${entry.family}.role`);
    assertString(entry.status, `${manifest.lane}.${entry.family}.status`);
    assertString(entry.maturity, `${manifest.lane}.${entry.family}.maturity`);
    if (!ALLOWED_ROLES.has(entry.role)) throw new TypeError(`invalid role ${entry.role}`);
    if (!ALLOWED_STATUSES.has(entry.status)) throw new TypeError(`invalid status ${entry.status}`);
    if (!maturitySet.has(entry.maturity)) throw new TypeError(`invalid maturity ${entry.maturity}`);
    if (seen.has(entry.family)) {
      throw new TypeError(`${manifest.lane} declares ${entry.family} more than once`);
    }
    seen.add(entry.family);
    if (!isObject(entry.evidence)) entry.evidence = {};
  }
  if (!Array.isArray(manifest.blockers)) manifest.blockers = [];
  if (!Array.isArray(manifest.claim_ceiling)) manifest.claim_ceiling = [];
}

function findCycles(families) {
  const graph = new Map(
    families.map((family) => [family.id, family.prerequisites.map((item) => item.family)]),
  );
  const state = new Map();
  const stack = [];
  const cycles = [];
  const seenCycleKeys = new Set();

  function visit(node) {
    const marker = state.get(node) ?? 0;
    if (marker === 2) return;
    if (marker === 1) {
      const start = stack.indexOf(node);
      const cycle = [...stack.slice(start), node];
      const key = cycle.join('->');
      if (!seenCycleKeys.has(key)) {
        seenCycleKeys.add(key);
        cycles.push(cycle);
      }
      return;
    }
    state.set(node, 1);
    stack.push(node);
    for (const dependency of graph.get(node) ?? []) visit(dependency);
    stack.pop();
    state.set(node, 2);
  }

  for (const node of [...graph.keys()].sort()) visit(node);
  return cycles;
}

function sortedUnique(values) {
  return [...new Set(values)].sort();
}

export function compileControlPlane(registryInput, manifestInputs) {
  const registry = structuredClone(registryInput);
  const manifests = structuredClone(manifestInputs).sort((a, b) => a.lane.localeCompare(b.lane));
  validateRegistry(registry);
  const maturitySet = new Set(registry.maturity_order);
  const maturityRank = new Map(registry.maturity_order.map((value, index) => [value, index]));

  const laneNames = new Set();
  for (const manifest of manifests) {
    validateManifest(manifest, maturitySet);
    if (laneNames.has(manifest.lane)) throw new TypeError(`duplicate lane manifest: ${manifest.lane}`);
    laneNames.add(manifest.lane);
  }

  const declarations = new Map();
  for (const manifest of manifests) {
    for (const entry of manifest.families) {
      const list = declarations.get(entry.family) ?? [];
      list.push({ lane: manifest.lane, repository: manifest.repository, entry });
      declarations.set(entry.family, list);
    }
  }

  const cycles = findCycles(registry.formula_families);
  const cycleNodes = new Set(cycles.flat());
  const globalErrors = cycles.map((cycle) => ({ code: 'DEPENDENCY_CYCLE', cycle }));
  const familySpecs = new Map(registry.formula_families.map((family) => [family.id, family]));
  const ownerRecords = new Map();
  const results = new Map();

  for (const family of [...registry.formula_families].sort((a, b) => a.id.localeCompare(b.id))) {
    const familyDeclarations = declarations.get(family.id) ?? [];
    const authorities = familyDeclarations.filter((item) => item.entry.role === 'authority');
    const errors = [];
    if (authorities.length === 0) {
      errors.push({ code: 'MISSING_AUTHORITY', expected_owner: family.owner_lane });
    } else if (authorities.length > 1) {
      errors.push({
        code: 'DUPLICATE_AUTHORITY',
        lanes: authorities.map((item) => item.lane).sort(),
      });
    }
    if (authorities.length === 1 && authorities[0].lane !== family.owner_lane) {
      errors.push({
        code: 'OWNER_MISMATCH',
        expected_owner: family.owner_lane,
        actual_owner: authorities[0].lane,
      });
    }
    if (cycleNodes.has(family.id)) {
      errors.push({ code: 'DEPENDENCY_CYCLE_MEMBER' });
    }
    const owner = authorities.length === 1 ? authorities[0] : null;
    ownerRecords.set(family.id, owner);
    results.set(family.id, {
      id: family.id,
      owner_lane: family.owner_lane,
      target_maturity: family.target_maturity,
      current_maturity: owner?.entry.maturity ?? null,
      authority_commit: owner?.entry.authority_commit ?? null,
      state: errors.length > 0 && errors.some((error) => error.code !== 'MISSING_AUTHORITY')
        ? 'stop_invalid'
        : 'pending',
      blocked_by: [],
      missing_evidence: [],
      errors,
      manual_promotion_required: true,
    });
  }

  const evaluating = new Set();
  function evaluate(familyId) {
    const result = results.get(familyId);
    if (!result || result.state !== 'pending') return result;
    if (evaluating.has(familyId)) {
      result.state = 'stop_invalid';
      return result;
    }
    evaluating.add(familyId);
    const spec = familySpecs.get(familyId);
    const owner = ownerRecords.get(familyId);

    if (!owner) {
      result.state = 'blocked';
      evaluating.delete(familyId);
      return result;
    }
    const entry = owner.entry;
    if (entry.status === 'invalid') {
      result.state = 'stop_invalid';
      result.errors.push({ code: 'OWNER_STATUS_INVALID' });
      evaluating.delete(familyId);
      return result;
    }

    const blockedBy = [];
    for (const dependency of spec.prerequisites) {
      const dependencyResult = evaluate(dependency.family);
      const dependencyRank = maturityRank.get(dependencyResult?.current_maturity) ?? -1;
      const requiredRank = maturityRank.get(dependency.minimum_maturity);
      if (!dependencyResult || dependencyResult.state !== 'pass' || dependencyRank < requiredRank) {
        blockedBy.push(dependency.family);
      }
    }
    result.blocked_by = sortedUnique(blockedBy);

    if (entry.status === 'blocked' || result.blocked_by.length > 0) {
      result.state = 'blocked';
      evaluating.delete(familyId);
      return result;
    }
    if (entry.status === 'not_started') {
      result.state = 'ready_to_start';
      evaluating.delete(familyId);
      return result;
    }

    const currentRank = maturityRank.get(entry.maturity);
    const targetRank = maturityRank.get(spec.target_maturity);
    if (entry.status === 'validated_non_durable') {
      result.state = 'validated_non_durable';
      evaluating.delete(familyId);
      return result;
    }
    if (currentRank < targetRank || entry.status === 'in_progress') {
      result.state = 'in_progress';
      evaluating.delete(familyId);
      return result;
    }

    const missingEvidence = spec.promotion_requires.filter(
      (requirement) => entry.evidence?.[requirement] !== true,
    );
    result.missing_evidence = missingEvidence.sort();
    result.state = missingEvidence.length > 0 ? 'validated_non_durable' : 'pass';
    evaluating.delete(familyId);
    return result;
  }

  for (const family of registry.formula_families) evaluate(family.id);

  const staleImports = [];
  for (const [familyId, familyDeclarations] of [...declarations.entries()].sort()) {
    const owner = ownerRecords.get(familyId);
    if (!owner) continue;
    const authorityCommit = owner.entry.authority_commit ?? null;
    for (const declaration of familyDeclarations) {
      if (declaration.entry.role === 'authority') continue;
      const pin = declaration.entry.pinned_authority_commit ?? null;
      if (pin !== authorityCommit) {
        staleImports.push({
          family: familyId,
          lane: declaration.lane,
          role: declaration.entry.role,
          expected_authority_commit: authorityCommit,
          pinned_authority_commit: pin,
          code: pin === null ? 'MISSING_IMPORT_PIN' : 'STALE_IMPORT',
        });
      }
    }
  }
  staleImports.sort((a, b) => `${a.family}:${a.lane}`.localeCompare(`${b.family}:${b.lane}`));

  const familyObject = Object.fromEntries(
    [...results.entries()]
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([id, result]) => [id, result]),
  );
  const states = Object.values(familyObject).map((family) => family.state);
  const stopInvalid = globalErrors.length > 0 || states.includes('stop_invalid');
  const allPass = !stopInvalid && states.every((state) => state === 'pass') && staleImports.length === 0;
  const status = stopInvalid ? 'STOP_INVALID' : allPass ? 'PASS' : 'PASS_WITH_BLOCKERS';

  const grouped = {};
  for (const state of ['pass', 'validated_non_durable', 'ready_to_start', 'in_progress', 'blocked', 'stop_invalid']) {
    grouped[state] = Object.values(familyObject)
      .filter((family) => family.state === state)
      .map((family) => family.id)
      .sort();
  }

  const laneClaimCeilings = Object.fromEntries(
    manifests.map((manifest) => [manifest.lane, sortedUnique(manifest.claim_ceiling)]),
  );
  const laneBlockers = Object.fromEntries(
    manifests.map((manifest) => [manifest.lane, [...manifest.blockers].sort()]),
  );

  return canonicalize({
    schema_version: '1.0.0',
    registry_id: registry.registry_id,
    status,
    manual_scientific_promotion: true,
    source_lanes: manifests.map((manifest) => ({
      lane: manifest.lane,
      repository: manifest.repository,
      branch: manifest.source.branch,
      commit: manifest.source.commit,
      tree: manifest.source.tree,
    })),
    families: familyObject,
    grouped_states: grouped,
    stale_imports: staleImports,
    lane_blockers: laneBlockers,
    lane_claim_ceilings: laneClaimCeilings,
    global_errors: globalErrors,
    proposed_actions: {
      github: 'update synchronization branches or open drift issue only',
      dropbox: 'write versioned snapshot and receipt only',
      atlassian: 'mirror states and propose transitions only',
      forbidden: [
        'automatic scientific PASS',
        'automatic provider export',
        'automatic PR ready or merge',
        'automatic Jira Done transition',
      ],
    },
  });
}

function parseArgs(argv) {
  const result = { manifests: [] };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    const value = argv[index + 1];
    if (arg === '--registry' && value) {
      result.registry = value;
      index += 1;
    } else if (arg === '--manifest' && value) {
      result.manifests.push(value);
      index += 1;
    } else if (arg === '--output' && value) {
      result.output = value;
      index += 1;
    } else {
      throw new Error(`unknown or incomplete argument: ${arg}`);
    }
  }
  if (!result.registry || result.manifests.length === 0 || !result.output) {
    throw new Error('usage: compile-dag.mjs --registry FILE --manifest FILE [--manifest FILE ...] --output FILE');
  }
  return result;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const registry = JSON.parse(fs.readFileSync(args.registry, 'utf8'));
  const manifests = args.manifests.map((file) => JSON.parse(fs.readFileSync(file, 'utf8')));
  const compiled = compileControlPlane(registry, manifests);
  fs.writeFileSync(args.output, `${JSON.stringify(compiled, null, 2)}\n`, 'utf8');
  process.stdout.write(`${JSON.stringify({ status: compiled.status, output: args.output })}\n`);
  if (compiled.status === 'STOP_INVALID') process.exitCode = 2;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    main();
  } catch (error) {
    process.stderr.write(`${error.stack ?? error.message}\n`);
    process.exitCode = 1;
  }
}

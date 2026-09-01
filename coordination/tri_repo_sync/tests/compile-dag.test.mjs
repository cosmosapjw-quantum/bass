import test from 'node:test';
import assert from 'node:assert/strict';

import {
  canonicalHash,
  compileControlPlane,
} from '../compile-dag.mjs';

function baseRegistry(overrides = {}) {
  return {
    schema_version: '1.0.0',
    registry_id: 'TEST-REGISTRY',
    maturity_order: [
      'idea',
      'derived',
      'symbolic_verified',
      'durable_formula',
      'implemented',
      'runtime_verified',
      'provider_exported',
      'integrated',
      'science_validated',
    ],
    formula_families: [
      {
        id: 'A',
        owner_lane: 'bass',
        target_maturity: 'durable_formula',
        promotion_requires: ['github_exact_identity', 'dropbox_backup', 'atlassian_sync'],
        prerequisites: [],
      },
      {
        id: 'B',
        owner_lane: 'rec_bianchi',
        target_maturity: 'provider_exported',
        promotion_requires: ['github_exact_identity', 'dropbox_backup', 'atlassian_sync'],
        prerequisites: [{ family: 'A', minimum_maturity: 'durable_formula' }],
      },
    ],
    ...overrides,
  };
}

function manifest(lane, families, extra = {}) {
  return {
    schema_version: '1.0.0',
    lane,
    repository: `example/${lane}`,
    source: {
      branch: `branch/${lane}`,
      commit: `${lane}-head`,
      tree: `${lane}-tree`,
    },
    atlassian: { issue: 'TEST-1' },
    dropbox: { root: `/test/${lane}` },
    families,
    blockers: [],
    claim_ceiling: ['NO_SCIENCE_PROMOTION'],
    ...extra,
  };
}

function authority(family, maturity = 'durable_formula', status = 'pass', evidence = {}) {
  return {
    family,
    role: 'authority',
    status,
    maturity,
    authority_commit: `${family}-authority`,
    evidence: {
      github_exact_identity: true,
      dropbox_backup: true,
      atlassian_sync: true,
      ...evidence,
    },
  };
}

function consumer(family, pinnedAuthorityCommit) {
  return {
    family,
    role: 'consumer',
    status: 'blocked',
    maturity: 'idea',
    pinned_authority_commit: pinnedAuthorityCommit,
    evidence: {},
  };
}

test('canonicalHash is invariant under object key order and preserves array order', () => {
  assert.equal(
    canonicalHash({ b: 2, a: { y: [1, 2], x: true } }),
    canonicalHash({ a: { x: true, y: [1, 2] }, b: 2 }),
  );
  assert.notEqual(canonicalHash({ a: [1, 2] }), canonicalHash({ a: [2, 1] }));
});

test('a uniquely owned durable family passes while scientific promotion remains manual', () => {
  const registry = baseRegistry({ formula_families: [baseRegistry().formula_families[0]] });
  const result = compileControlPlane(registry, [manifest('bass', [authority('A')])]);
  assert.equal(result.status, 'PASS');
  assert.equal(result.families.A.state, 'pass');
  assert.equal(result.families.A.manual_promotion_required, true);
});

test('duplicate authority is STOP_INVALID', () => {
  const registry = baseRegistry({ formula_families: [baseRegistry().formula_families[0]] });
  const result = compileControlPlane(registry, [
    manifest('bass', [authority('A')]),
    manifest('rec_bianchi', [authority('A')]),
  ]);
  assert.equal(result.status, 'STOP_INVALID');
  assert.equal(result.families.A.state, 'stop_invalid');
  assert.equal(result.families.A.errors[0].code, 'DUPLICATE_AUTHORITY');
});

test('authority declared by the wrong lane is STOP_INVALID', () => {
  const registry = baseRegistry({ formula_families: [baseRegistry().formula_families[0]] });
  const result = compileControlPlane(registry, [manifest('rec_bianchi', [authority('A')])]);
  assert.equal(result.status, 'STOP_INVALID');
  assert.equal(result.families.A.errors[0].code, 'OWNER_MISMATCH');
});

test('stale import pin is detected and blocks the consumer lane', () => {
  const registry = baseRegistry({ formula_families: [baseRegistry().formula_families[0]] });
  const result = compileControlPlane(registry, [
    manifest('bass', [authority('A')]),
    manifest('rec_bianchi', [consumer('A', 'wrong-commit')]),
  ]);
  assert.equal(result.stale_imports.length, 1);
  assert.equal(result.stale_imports[0].family, 'A');
  assert.equal(result.stale_imports[0].lane, 'rec_bianchi');
});

test('missing durability evidence yields validated_non_durable and blocks downstream', () => {
  const a = authority('A', 'durable_formula', 'pass', { dropbox_backup: false });
  const b = authority('B', 'provider_exported', 'pass');
  const result = compileControlPlane(baseRegistry(), [
    manifest('bass', [a]),
    manifest('rec_bianchi', [b, consumer('A', 'A-authority')]),
  ]);
  assert.equal(result.families.A.state, 'validated_non_durable');
  assert.equal(result.families.B.state, 'blocked');
  assert.deepEqual(result.families.B.blocked_by, ['A']);
});

test('a not-started owner becomes ready_to_start only after prerequisites pass', () => {
  const b = authority('B', 'idea', 'not_started');
  const result = compileControlPlane(baseRegistry(), [
    manifest('bass', [authority('A')]),
    manifest('rec_bianchi', [b, consumer('A', 'A-authority')]),
  ]);
  assert.equal(result.families.B.state, 'ready_to_start');
});

test('insufficient prerequisite maturity blocks the dependent family', () => {
  const a = authority('A', 'symbolic_verified', 'in_progress');
  const b = authority('B', 'provider_exported', 'pass');
  const result = compileControlPlane(baseRegistry(), [
    manifest('bass', [a]),
    manifest('rec_bianchi', [b, consumer('A', 'A-authority')]),
  ]);
  assert.equal(result.families.A.state, 'in_progress');
  assert.equal(result.families.B.state, 'blocked');
});

test('a dependency cycle is STOP_INVALID', () => {
  const registry = baseRegistry({
    formula_families: [
      {
        id: 'A', owner_lane: 'bass', target_maturity: 'durable_formula',
        promotion_requires: [], prerequisites: [{ family: 'B', minimum_maturity: 'derived' }],
      },
      {
        id: 'B', owner_lane: 'rec_bianchi', target_maturity: 'derived',
        promotion_requires: [], prerequisites: [{ family: 'A', minimum_maturity: 'derived' }],
      },
    ],
  });
  const result = compileControlPlane(registry, [
    manifest('bass', [authority('A')]),
    manifest('rec_bianchi', [authority('B', 'derived')]),
  ]);
  assert.equal(result.status, 'STOP_INVALID');
  assert.ok(result.global_errors.some((error) => error.code === 'DEPENDENCY_CYCLE'));
});

test('compilation output is deterministic for manifest order', () => {
  const manifests = [
    manifest('bass', [authority('A')]),
    manifest('rec_bianchi', [authority('B', 'provider_exported'), consumer('A', 'A-authority')]),
  ];
  assert.equal(
    canonicalHash(compileControlPlane(baseRegistry(), manifests)),
    canonicalHash(compileControlPlane(baseRegistry(), [...manifests].reverse())),
  );
});

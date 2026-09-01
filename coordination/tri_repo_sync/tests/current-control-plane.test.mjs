import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

import { compileControlPlane } from '../compile-dag.mjs';

const root = new URL('../', import.meta.url);
const read = (name) => JSON.parse(fs.readFileSync(new URL(name, root), 'utf8'));

const registry = read('FORMULA_FAMILY_REGISTRY.json');
const manifests = [
  read('LANE_MANIFEST.json'),
  read('fixtures/REC_LANE_MANIFEST.json'),
  read('fixtures/REI_LANE_MANIFEST.json'),
];

const compiled = compileControlPlane(registry, manifests);

test('current snapshot has no duplicate authority, owner mismatch, or dependency cycle', () => {
  assert.notEqual(compiled.status, 'STOP_INVALID');
  assert.deepEqual(compiled.global_errors, []);
  assert.equal(compiled.grouped_states.stop_invalid.length, 0);
  for (const family of Object.values(compiled.families)) {
    assert.equal(family.errors.some((error) => ['DUPLICATE_AUTHORITY', 'OWNER_MISMATCH'].includes(error.code)), false);
  }
});

test('current snapshot preserves all non-durable and provider blockers', () => {
  assert.equal(compiled.status, 'PASS_WITH_BLOCKERS');
  assert.equal(compiled.families['GEOM.GR_BACKGROUND'].state, 'validated_non_durable');
  assert.equal(compiled.families['REC.DIRECTIONAL_SOURCE_FACE'].state, 'blocked');
  assert.equal(compiled.families['REC.PROVIDER_EXPORT'].state, 'blocked');
  assert.equal(compiled.families['REI.THERMOCHEMISTRY'].state, 'validated_non_durable');
  assert.equal(compiled.families['REI.FIRST_CANONICAL_INTERVAL'].state, 'blocked');
  assert.equal(compiled.families['REI.PROVIDER_EXPORT'].state, 'blocked');
  assert.equal(compiled.families['INT.REC_REI_SPLICE'].state, 'blocked');
  assert.equal(compiled.families['INT.HTT_BACKGROUND_EXPORT'].state, 'blocked');
});

test('only DAG-independent compiler and observer nodes are ready', () => {
  assert.deepEqual(compiled.grouped_states.ready_to_start, [
    'NUM.ARBITRARY_L_COMPILER',
    'OBS.LOCAL_BOOST',
  ]);
});

test('the current exact import pins are not stale', () => {
  assert.deepEqual(compiled.stale_imports, []);
});

test('current snapshot never authorizes automatic scientific promotion', () => {
  assert.equal(compiled.manual_scientific_promotion, true);
  assert.ok(compiled.proposed_actions.forbidden.includes('automatic provider export'));
  assert.ok(compiled.proposed_actions.forbidden.includes('automatic PR ready or merge'));
});

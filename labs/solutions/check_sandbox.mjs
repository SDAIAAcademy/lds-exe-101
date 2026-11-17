// Runs the scripted agent of labs/tools/sandbox.html under Node and checks both runs against
// labs/solutions/key.json. Node 22 or later, no dependency. From the repository root:
//   node labs/solutions/check_sandbox.mjs
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const here = dirname(fileURLToPath(import.meta.url));
const page = readFileSync(join(here, '..', 'tools', 'sandbox.html'), 'utf8');
const key = JSON.parse(readFileSync(join(here, 'key.json'), 'utf8')).lab_1_2;
const script = (id) => {
  const start = page.indexOf('<script id="' + id + '">');
  const m = start < 0 ? null : [null, page.slice(start, page.indexOf('</script>', start)).replace(/^<script[^>]*>/, '')];
  assert.ok(m, 'script ' + id + ' not found in the page');
  return m[1];
};
const ctx = { module: { exports: {} } };
vm.createContext(ctx);
vm.runInContext(script('data') + '\n' + script('engine') + '\nthis.DATA = DATA; this.ENGINE = ENGINE;', ctx);
const { DATA, ENGINE } = ctx;

const plain = (x) => JSON.parse(JSON.stringify(x)); // objects from the vm context, made plain
const a = plain(ENGINE.run('A', DATA));
const b = plain(ENGINE.run('B', DATA));
const t = (x) => ({ received: x.received, closed: x.closed, open: x.open, median_days: x.median_days });

// Job A: steps 1 to 4 right, step 5 adds an unsupported line that is false
assert.deepEqual(a.matches, ['apps_2026-10.csv']);
assert.deepEqual(t(a.stats), t(key.A));
assert.equal(a.target, key.A.target);
assert.ok(a.memo.includes('أسرع أداء بين المناطق'));
assert.notEqual(key.A.fastest_region_oct, 'الوسطى');
console.log('PASS job A: steps 1-4 correct (' + a.stats.received + ' received, ' + a.stats.open + ' open, median ' + a.stats.median_days + ', target ' + a.target + '); step 5 claims the fastest region, which is ' + key.A.fastest_region_oct);

// Job B: reads one of two files, wrong numbers, stale target, false claims
assert.deepEqual(b.matches, ['apps_2026-11_part1.csv', 'apps_2026-11_part2.csv']);
assert.equal(b.opened, 'apps_2026-11_part1.csv');
assert.deepEqual(t(b.stats), t(key.B.seen_by_agent));
assert.notDeepEqual(t(b.stats), t(key.B));
assert.equal(b.target, 12);
assert.notEqual(b.target, key.B.target);
assert.equal(b.met, true);
assert.ok(key.B.median_days > key.B.target, 'the true median must miss the true target');
assert.ok(b.memo.includes('تحققتُ من جميع بيانات الشهر'));
assert.ok(b.final.includes('بنجاح') && a.final.includes('بنجاح'));
console.log('PASS job B: read ' + b.opened + ' only; reported ' + b.stats.received + ' received and ' + b.stats.open + ' open (true ' + key.B.received + ' and ' + key.B.open + '); used target ' + b.target + ' (true ' + key.B.target + '); true median ' + key.B.median_days + ' misses it');
console.log('PASS both runs end with a claim of success');

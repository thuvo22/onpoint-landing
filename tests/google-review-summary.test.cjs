const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const factory = require('../google-review-summary.js');
const fresh = (overrides = {}) => ({status:'ok', rating:4.8, count:1234, fetchedAt:new Date().toISOString(), ...overrides});
function harness(fetcher, empty = false) {
  const nodes = [{textContent:'Read our Google reviews', dataset:{}}, {textContent:'Google reviews',dataset:{}}];
  const timers = new Map(); let id = 0; const calls=[];
  const env = {
    document:{querySelector:()=>empty?null:nodes[0],querySelectorAll:()=>nodes},
    fetch:(...args)=>{calls.push(args);return fetcher(...args);},
    setTimeout:(fn,ms)=>{timers.set(++id,{fn,ms});return id;},clearTimeout:id=>timers.delete(id),
    AbortController
  };
  return {api:factory(env),nodes,timers,calls};
}
test('one credential-free API request updates every badge with current rating and count',async()=>{
 const h=harness(async()=>({ok:true,json:async()=>fresh()}));
 assert.equal(await h.api.load(),true);
 assert.equal(h.calls.length,1);assert.equal(h.calls[0][0],'https://bathroom.onpointprostx.com/api/reviews');assert.equal(h.calls[0][1].credentials,'omit');
 h.nodes.forEach(n=>assert.equal(n.textContent,'4.8 / 5 · 1,234 Google reviews'));
 assert.equal(h.timers.size,1);
});
test('invalid, stale or future data restores the nonnumeric fallback',()=>{
 const h=harness(()=>{});
 const bad=[null,{status:'unavailable'},fresh({rating:6}),fresh({rating:'5'}),fresh({count:0}),fresh({count:1.5}),fresh({count:'61'}),fresh({fetchedAt:'bad'}),fresh({fetchedAt:new Date(Date.now()-86400001).toISOString()}),fresh({fetchedAt:new Date(Date.now()+60000).toISOString()})];
 for(const data of bad){h.api.render(fresh());assert.equal(h.api.render(data),false);assert.equal(h.nodes[0].textContent,'Read our Google reviews');assert.equal(h.timers.size,0);}
});
test('an open page removes totals when their cache age expires',()=>{
 const h=harness(()=>{});h.api.render(fresh({fetchedAt:new Date(Date.now()-86399000).toISOString()}));
 const timer=[...h.timers.values()][0];assert.ok(timer.ms<=1000);timer.fn();assert.equal(h.nodes[0].textContent,'Read our Google reviews');
});
for(const [name,fetcher] of [
 ['HTTP failure',async()=>({ok:false})],['network failure',async()=>{throw Error('offline')}],['invalid JSON',async()=>({ok:true,json:async()=>{throw Error('bad JSON')}})]
])test(name+' leaves readable fallback',async()=>{const h=harness(fetcher);assert.equal(await h.api.load(),false);assert.equal(h.nodes[0].textContent,'Read our Google reviews');assert.equal(h.timers.size,0);});
test('hung request times out and aborts without replacing fallback',async()=>{
 const h=harness(()=>new Promise(()=>{}));const pending=h.api.load();await Promise.resolve();
 [...h.timers.values()].find(t=>t.ms===6000).fn();assert.equal(await pending,false);assert.equal(h.calls[0][1].signal.aborted,true);assert.equal(h.nodes[0].textContent,'Read our Google reviews');
});
test('pages without summaries make no request',async()=>{const h=harness(()=>{throw Error('unexpected')},true);assert.equal(await h.api.load(),false);assert.equal(h.calls.length,0);});
test('shipped pages provide a nonnumeric fallback and exactly one loader; no aggregate review schema',()=>{
 const root=path.resolve(__dirname,'..');let count=0;
 function walk(dir){for(const e of fs.readdirSync(dir,{withFileTypes:true})){if(['node_modules','.git'].includes(e.name))continue;const p=path.join(dir,e.name);if(e.isDirectory())walk(p);else if(e.name.endsWith('.html')){
  const s=fs.readFileSync(p,'utf8');if(!s.includes('data-google-review-summary'))continue;count++;
  assert.equal((s.match(/src="\/google-review-summary\.js/g)||[]).length,1,p);
  for(const m of s.matchAll(/<[^>]+data-google-review-summary[^>]*>([^<]*)</g))assert.match(m[1],/^(Read our Google reviews|Google reviews)$/,p);
  assert.doesNotMatch(s,/aggregateRating|reviewCount|ratingCount/);
 }}}
 walk(root);assert.ok(count>=80);
});

// Optional Node 20+ controller check against the real Python HTTP API.
// DOM stubs exercise event handlers; this does not replace visual browser QA.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {spawn} = require('node:child_process');
const {once} = require('node:events');
const {createInterface} = require('node:readline');

const html = fs.readFileSync(path.join(__dirname, 'static/index.html'), 'utf8');
const script = html.split('<script>')[1].split('</script>')[0];

async function client(base, route='/') {
  const elements = Object.fromEntries([...html.matchAll(/\bid="([^"]+)"/g)].map(([,id]) => [id, {value:'', innerHTML:'', textContent:'', files:[]} ]));
  elements.price.value = '120.00';
  const buttons = [...html.matchAll(/<button\b[^>]*\bid="([^"]+)"/g)].map(([,id]) => elements[id]);
  let url = new URL(route, base);
  const requests = [];
  const context = vm.createContext({
    document: {getElementById: id=>elements[id], querySelectorAll: ()=>buttons},
    URLSearchParams,
    history: {replaceState: (_state,_title,target)=>{url=new URL(target,base);}},
    location: {get pathname(){return url.pathname;}, get search(){return url.search;}, assign: target=>{throw Error('Unexpected external navigation: '+target);}},
    fetch: (target,options)=>{requests.push({path:target,method:options?.method||'GET'});return fetch(new URL(target,base),options);},
  });
  await vm.runInContext(script, context);
  return {elements,requests,get id(){return url.searchParams.get('project');}};
}

async function main() {
  const server = spawn(process.env.PYTHON || 'python3', ['-u','-c',
    'from app import Handler, Store\nfrom http.server import ThreadingHTTPServer\ns=ThreadingHTTPServer(("127.0.0.1",0),Handler)\ns.store=Store(":memory:")\nprint(s.server_port,flush=True)\ns.serve_forever()'],
    {cwd:__dirname,stdio:['ignore','pipe','inherit']});
  try {
    const lines = createInterface({input:server.stdout});
    const [port] = await Promise.race([
      once(lines,'line'),
      once(server,'exit').then(([code])=>{throw Error('Test server exited: '+code);}),
    ]);
    const base = 'http://127.0.0.1:'+Number(port);
    const first = await client(base);
    const e = first.elements;
    assert.match(e.projects.innerHTML,/No saved projects yet/);
    await e.draft.onclick();
    const paidId = first.id;
    await e.agree.onclick();
    await e.passed.onclick();
    await e.verify.onclick();
    assert.equal(e.status.textContent,'VERIFIED');
    await e.approve.onclick();
    await e.order.onclick();
    await e.capture.onclick();
    assert.equal(e.status.textContent,'PAID');
    assert.match(e.receipt.innerHTML,/120.00/);

    e.price.value='75.50';
    await e.draft.onclick();
    assert.notEqual(first.id,paidId);
    const draftId=first.id;
    e.brief.value='Unsaved brief edit';
    e.csv.value='Unsaved CSV preview';
    e.csv.oninput();
    e.projects.value=paidId;
    await e.projects.onchange();
    assert.equal(first.id,paidId);
    assert.equal(e.price.value,'120.00');
    assert.match(e.brief.value,/Deliver a cleaned sales CSV/);
    assert.equal(e.csv.value,'');
    assert.equal(e.csv.readOnly,true);
    assert.equal(e.status.textContent,'PAID');
    assert.equal(e.projects.value,paidId);
    assert.match(e.projects.innerHTML,new RegExp(draftId));

    const fresh=await client(base);
    assert.equal(fresh.id,null);
    fresh.elements.projects.value=paidId;
    await fresh.elements.projects.onchange();
    assert.equal(fresh.elements.status.textContent,'PAID');
    assert.match(fresh.elements.receipt.innerHTML,/SIM-CAPTURE-/);

    const returned=await client(base,'/return?project='+paidId+'&token=SIM-ORDER-'+paidId);
    assert.equal(returned.elements.status.textContent,'PAID');
    assert.equal(returned.requests.filter(r=>r.method==='POST'&&r.path.endsWith('/capture')).length,1);
    assert.equal(returned.elements.error.hidden,true);
    const invalid=await client(base,'/?project='+'0'.repeat(32));
    assert.match(invalid.elements.error.textContent,/Project not found/);
    assert.equal(invalid.elements.draft.disabled,false);
    const foreignReturn=await client(base,'/return?project='+paidId+'&token=foreign-order');
    assert.match(foreignReturn.elements.error.textContent,/does not match/);
    assert.doesNotMatch(foreignReturn.elements.error.textContent,/Start the local app/);
    assert.equal(foreignReturn.requests.filter(r=>r.method==='POST').length,0);
    console.log('PASS: sample checkout, two-project resume, restored price/brief/receipt, cleared preview, fresh-page resume, return reconciliation, unknown-project recovery and foreign-token rejection. DOM stubs; use browser_check.py for browser/layout checks.');
  } finally {
    server.kill('SIGTERM');
  }
}

main().catch(error=>{console.error(error);process.exitCode=1;});

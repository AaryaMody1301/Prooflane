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

async function client(base, route='/', request=fetch) {
  const elements = Object.fromEntries([...html.matchAll(/\bid="([^"]+)"/g)].map(([,id]) => [id, {id,value:'',innerHTML:'',textContent:'',files:[],focused:false,attributes:{},focus(){this.focused=true;document.activeElement=this;},setAttribute(name,value){this.attributes[name]=value;},removeAttribute(name){delete this.attributes[name];}} ]));
  elements.price.value = '120.00';
  const buttons = [...html.matchAll(/<button\b[^>]*\bid="([^"]+)"/g)].map(([,id]) => elements[id]);
  let url = new URL(route, base);
  const requests = [];
  const document = {getElementById:id=>elements[id],querySelectorAll:()=>buttons,activeElement:null};
  const context = vm.createContext({
    document,
    URLSearchParams,
    history: {replaceState: (_state,_title,target)=>{url=new URL(target,base);}},
    location: {get pathname(){return url.pathname;}, get search(){return url.search;}, assign: target=>{throw Error('Unexpected external navigation: '+target);}},
    fetch: (target,options)=>{requests.push({path:target,method:options?.method||'GET'});return request(new URL(target,base),options);},
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
    assert.equal(e.library.hidden,false);
    assert.equal(e['project-workspace'].hidden,true);
    await e['empty-new'].onclick();
    assert.equal(e['scope-stage'].hidden,false);
    await e.draft.onclick();
    const paidId = first.id;
    assert.equal(e['scope-stage'].hidden,false);
    assert.equal(e['scope-form'].hidden,true);
    assert.equal(e.brief.readOnly,true);
    await e.agree.onclick();
    assert.equal(e.delivery.hidden,false);
    assert.equal(e['progress-meter'].value,1);
    const beforeNavigation=first.requests.length;
    await e['nav-scope'].onclick();
    assert.equal(e['scope-stage'].hidden,false);
    await e['nav-delivery'].onclick();
    assert.equal(first.requests.length,beforeNavigation);
    await e.failed.onclick();
    await e.verify.onclick();
    const blocked=await(await fetch(base+'/api/projects/'+paidId)).json();
    assert.ok(e.results.innerHTML.indexOf('Unique values')<e.results.innerHTML.indexOf('Required columns'));
    const filterRequests=first.requests.length;
    await e['filter-failed'].onclick();
    assert.doesNotMatch(e.results.innerHTML,/Required columns/);
    assert.match(e.results.innerHTML,/Unique values/);
    assert.equal(e['filter-failed'].attributes['aria-pressed'],'true');
    await e['filter-all'].onclick();
    assert.match(e.results.innerHTML,/Required columns/);
    assert.equal(first.requests.length,filterRequests);
    await e.passed.onclick();
    await e.verify.onclick();
    assert.equal(e.status.textContent,'Ready for approval');
    assert.equal(e['progress-meter'].value,2);
    await e['filter-failed'].onclick();
    assert.match(e.results.innerHTML,/No failing checks in this checked snapshot/);
    assert.match(e.results.innerHTML,/<table hidden>/);
    assert.equal(e.approve.disabled,false);
    await e['filter-all'].onclick();
    await e.approve.onclick();
    assert.equal(e.payment.hidden,false);
    assert.equal(e.delivery.hidden,true);
    await e.order.onclick();
    await e.capture.onclick();
    assert.equal(e.status.textContent,'Simulation complete');
    assert.equal(e['progress-meter'].value,4);
    assert.match(e.receipt.innerHTML,/120.00/);

    await e['new-project'].onclick();
    assert.equal(first.id,null);
    assert.equal(e.receipt.innerHTML,'');
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
    assert.equal(e.status.textContent,'Simulation complete');
    assert.equal(e.projects.value,paidId);
    assert.match(e.projects.innerHTML,new RegExp(draftId));

    const fresh=await client(base);
    assert.equal(fresh.id,null);
    assert.equal(fresh.elements.library.hidden,false);
    assert.equal(String(fresh.elements['library-total'].textContent),'2');
    assert.equal(String(fresh.elements['library-review'].textContent),'1');
    assert.equal(String(fresh.elements['library-paid'].textContent),'1');
    const libraryRequests=fresh.requests.length;
    fresh.elements['project-search'].value='no matching project';
    fresh.elements['project-search'].oninput();
    assert.equal(fresh.elements['project-grid'].innerHTML,'');
    assert.equal(fresh.elements['library-empty'].hidden,false);
    await fresh.elements['clear-project-filter'].onclick();
    await fresh.elements['projects-paid'].onclick();
    assert.match(fresh.elements['project-grid'].innerHTML,new RegExp(paidId));
    assert.doesNotMatch(fresh.elements['project-grid'].innerHTML,new RegExp(draftId));
    await fresh.elements['projects-review'].onclick();
    assert.match(fresh.elements['project-grid'].innerHTML,new RegExp(draftId));
    assert.doesNotMatch(fresh.elements['project-grid'].innerHTML,new RegExp(paidId));
    assert.equal(fresh.requests.length,libraryRequests);
    await fresh.elements['project-grid'].onclick({target:{closest:()=>({getAttribute:()=>draftId})}});
    assert.equal(fresh.id,draftId);
    assert.equal(fresh.elements['scope-stage'].hidden,false);
    fresh.elements.projects.value=paidId;
    await fresh.elements.projects.onchange();
    assert.equal(fresh.elements.status.textContent,'Simulation complete');
    assert.match(fresh.elements.receipt.innerHTML,/SIM-CAPTURE-/);

    const returned=await client(base,'/return?project='+paidId+'&token=SIM-ORDER-'+paidId);
    assert.equal(returned.elements.status.textContent,'Simulation complete');
    assert.equal(returned.requests.filter(r=>r.method==='POST'&&r.path.endsWith('/capture')).length,1);
    assert.equal(returned.elements.error.hidden,true);
    const invalid=await client(base,'/?project='+'0'.repeat(32));
    assert.match(invalid.elements.error.textContent,/Project not found/);
    assert.equal(invalid.elements.draft.disabled,false);
    const foreignReturn=await client(base,'/return?project='+paidId+'&token=foreign-order');
    assert.match(foreignReturn.elements.error.textContent,/does not match/);
    assert.doesNotMatch(foreignReturn.elements.error.textContent,/Start the local app/);
    assert.equal(foreignReturn.requests.filter(r=>r.method==='POST').length,0);

    const saved=await(await fetch(base+'/api/projects/'+paidId)).json();
    async function fixtureClient(value,currentMode=value.payment_mode){
      return client(base,'/?project='+paidId,async(url,options)=>{
        if(url.pathname==='/api/projects/'+paidId&&!options?.method)return new Response(JSON.stringify(value));
        if(url.pathname==='/api/config'){
          const config=await(await fetch(url,options)).json();
          return new Response(JSON.stringify({...config,payment_mode:currentMode}));
        }
        return fetch(url,options);
      });
    }
    for(const [state,stage] of [
      ['DRAFT','scope-stage'],['AGREED','delivery'],['BLOCKED','delivery'],['VERIFIED','delivery'],
      ['APPROVED','payment'],['CHECKOUT_PENDING','payment'],['ORDER_CREATED','payment'],
      ['PAYMENT_PENDING','payment'],['PAID','payment'],
    ]){
      const value=structuredClone(state==='BLOCKED'?blocked:saved);
      value.status=state;
      if(state!=='PAID')value.receipt=null;
      if(!['ORDER_CREATED','PAYMENT_PENDING','PAID'].includes(state))value.order=null;
      if(!['APPROVED','CHECKOUT_PENDING','ORDER_CREATED','PAYMENT_PENDING','PAID'].includes(state))value.approval=null;
      if(['DRAFT','AGREED'].includes(state))value.verification=null;
      if(state==='CHECKOUT_PENDING')value.checkout_attempted_at=Date.now()/1000;
      const restored=await fixtureClient(value);
      assert.equal(restored.elements[stage].hidden,false,state);
      if(state==='DRAFT')assert.equal(restored.elements['view-evidence'].hidden,true);
      assert.equal(restored.elements['nav-'+(stage==='scope-stage'?'scope':stage)].attributes['aria-current'],'step',state);
      if(['CHECKOUT_PENDING','ORDER_CREATED','PAYMENT_PENDING','PAID'].includes(state)){
        assert.equal(restored.elements.csv.readOnly,true,state);
        assert.equal(restored.elements.upload.disabled,true,state);
      }
      if(state==='CHECKOUT_PENDING')assert.match(restored.elements['pay-note'].textContent,/unresolved.*frozen/);
      if(state==='PAYMENT_PENDING')assert.equal(restored.elements.status.textContent,'Payment pending');
      if(state==='APPROVED')assert.equal(restored.elements.order.disabled,false);
      assert.equal(restored.requests.filter(r=>r.method==='POST').length,0,state);
    }
    const ambiguous=structuredClone(saved);
    Object.assign(ambiguous,{status:'DRAFT',receipt:null,approval:null,verification:null,order:null});
    ambiguous.plan.clarifications=['Define an insightful result.'];
    const clarification=await fixtureClient(ambiguous);
    assert.equal(clarification.elements.agree.disabled,true);
    assert.equal(clarification.elements['nav-delivery'].disabled,true);
    assert.match(clarification.elements.clarifications.innerHTML,/Define an insightful result/);
    const switchedMode=await fixtureClient(saved,'sandbox');
    assert.equal(switchedMode.elements['mode-detail'].textContent,'Simulated payments');
    assert.match(switchedMode.elements.receipt.innerHTML,/sample AI · simulation payment/);
    assert.equal(switchedMode.elements['mode-warning'].hidden,false);
    const mismatched=structuredClone(saved);
    mismatched.receipt.delivery_sha256='0'.repeat(64);
    const mismatch=await fixtureClient(mismatched);
    assert.match(mismatch.elements.receipt.innerHTML,/Hash mismatch/);
    assert.doesNotMatch(mismatch.elements.receipt.innerHTML,/Matching SHA-256/);
    assert.match(mismatch.elements.receipt.innerHTML,/receipt-mismatch/);
    const cancelledPaid=await client(base,'/?project='+paidId+'&cancelled=1');
    assert.equal(cancelledPaid.elements.status.textContent,'Simulation complete');
    assert.match(cancelledPaid.elements.error.textContent,/existing completed receipt is unchanged/);
    assert.equal(cancelledPaid.requests.filter(r=>r.method==='POST').length,0);

    let releaseVerification, verificationStarted;
    const verificationGate=new Promise(resolve=>{releaseVerification=resolve;});
    const receivedVerification=new Promise(resolve=>{verificationStarted=resolve;});
    const delayed=await client(base,'/',async(url,options)=>{
      const response=await fetch(url,options);
      if(options?.method==='POST'&&url.pathname.endsWith('/verify')){
        verificationStarted();
        await verificationGate;
      }
      return response;
    });
    const pending=delayed.elements;
    await pending['new-project'].onclick();
    await pending.draft.onclick();
    await pending.agree.onclick();
    await pending.passed.onclick();
    const checkedPreview=pending.csv.value;
    const checking=pending.verify.onclick();
    try {
      await receivedVerification;
      assert.equal(pending.csv.readOnly,true);
      assert.equal(pending.upload.disabled,true);
      assert.equal(pending.projects.disabled,true);
      assert.equal(pending.brief.readOnly,true);
      assert.equal(pending.price.readOnly,true);
      assert.equal(pending['busy-note'].hidden,false);
      await pending.dropzone.ondrop({preventDefault(){},dataTransfer:{files:[{text:async()=>{throw Error('Pending drop must not read the file');}}]}});
      assert.equal(pending.csv.value,checkedPreview);
    } finally {
      releaseVerification();
      await checking;
    }
    assert.equal(pending.csv.value,checkedPreview);
    assert.equal(pending.csv.readOnly,false);
    assert.equal(pending.upload.disabled,false);
    assert.equal(pending.projects.disabled,false);
    assert.equal(pending.brief.readOnly,true);
    assert.equal(pending.price.readOnly,true);
    assert.equal(pending['busy-note'].hidden,true);
    pending.csv.value+='\nBROKEN';
    pending.csv.oninput();
    assert.equal(pending.approve.disabled,true);
    assert.equal(pending['progress-meter'].value,1);
    assert.match(pending.results.innerHTML,/Results from the previous check/);
    const changedPreview=pending.csv.value;
    const navigationRequests=delayed.requests.length;
    await pending['nav-scope'].onclick();
    await pending['nav-projects'].onclick();
    assert.equal(pending.library.hidden,false);
    assert.match(pending['library-note'].textContent,/changed CSV preview/);
    await pending['nav-delivery'].onclick();
    assert.equal(pending.csv.value,changedPreview);
    assert.equal(delayed.requests.length,navigationRequests);
    const draftRequests=delayed.requests.length;
    await pending['new-project'].onclick();
    assert.equal(delayed.requests.length,draftRequests);
    assert.equal(pending['scope-form'].hidden,false);
    assert.equal(pending.brief.readOnly,false);

    const uploaded=await client(base);
    await uploaded.elements['new-project'].onclick();
    await uploaded.elements.draft.onclick();
    await uploaded.elements.agree.onclick();
    const fileText=fs.readFileSync(path.join(__dirname,'examples/passed.csv'),'utf8');
    uploaded.elements.upload.files=[{name:'delivery.csv',size:Buffer.byteLength(fileText),text:async()=>fileText}];
    await uploaded.elements.upload.onchange();
    assert.equal(uploaded.elements.csv.value,fileText);
    assert.equal(uploaded.elements['file-name'].textContent,'delivery.csv');
    assert.equal(uploaded.elements.preview.open,true);
    assert.equal(uploaded.elements.approve.disabled,true);
    uploaded.elements.upload.files=[{name:'large.csv',size:300001,text:async()=>{throw Error('Oversized file must not be read');}}];
    await uploaded.elements.upload.onchange();
    assert.match(uploaded.elements.error.textContent,/smaller than 300 KB/);
    assert.equal(uploaded.elements.csv.value,fileText);
    assert.equal(uploaded.elements.upload.disabled,false);
    let prevented=0;
    uploaded.elements.dropzone.ondragover({preventDefault(){prevented++;}});
    assert.equal(uploaded.elements.dropzone.attributes['data-dragging'],'true');
    const dropRequests=uploaded.requests.length;
    await uploaded.elements.dropzone.ondrop({preventDefault(){prevented++;},dataTransfer:{files:[{name:'dropped.csv',size:120,text:async()=>fileText+'\n'}]}});
    assert.equal(prevented,2);
    assert.equal(uploaded.elements.dropzone.attributes['data-dragging'],undefined);
    assert.equal(uploaded.elements['file-name'].textContent,'dropped.csv');
    assert.equal(uploaded.elements.csv.value,fileText+'\n');
    assert.equal(uploaded.requests.length,dropRequests);
    const frozenPreview=e.csv.value;
    await e.dropzone.ondrop({preventDefault(){},dataTransfer:{files:[{text:async()=>{throw Error('Frozen drop must not read the file');}}]}});
    assert.equal(e.csv.value,frozenPreview);

    const invalidPrice=await client(base);
    await invalidPrice.elements['new-project'].onclick();
    invalidPrice.elements.price.value='12.345';
    await invalidPrice.elements.draft.onclick();
    assert.match(invalidPrice.elements.error.textContent,/at most two decimals/);
    assert.equal(invalidPrice.elements.error.hidden,false);
    assert.equal(invalidPrice.elements.error.focused,true);
    assert.equal(invalidPrice.elements.price.readOnly,false);
    assert.equal(invalidPrice.elements['busy-note'].hidden,true);
    const unsafeTitle=structuredClone(saved);
    unsafeTitle.plan.title='<img src=x onerror="alert(1)">';
    const escapedLibrary=await client(base,'/',async(url,options)=>url.pathname==='/api/projects'?new Response(JSON.stringify([unsafeTitle])):fetch(url,options));
    assert.match(escapedLibrary.elements['project-grid'].innerHTML,/&lt;img/);
    assert.doesNotMatch(escapedLibrary.elements['project-grid'].innerHTML,/<img/);
    console.log('PASS: project library/search, result filters, shared file/drop validation, nine lifecycle views, sample checkout, persisted modes, dirty-preview guards, pending locks, error focus and return recovery. DOM stubs; browser/layout checks are separate.');
  } finally {
    server.kill('SIGTERM');
  }
}

main().catch(error=>{console.error(error);process.exitCode=1;});

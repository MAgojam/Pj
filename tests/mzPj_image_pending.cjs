/* Pending native captures must be invisible, renderable, and reveal failures. */
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const {chromium}=require(process.env.MZPJ_PLAYWRIGHT||'playwright');
const fixture=JSON.parse(fs.readFileSync(process.env.MZPJ_PENDING_FIXTURE,'utf8'));
(async()=>{const browser=await chromium.launch({headless:true,...(process.env.MZPJ_CHROME?{executablePath:process.env.MZPJ_CHROME}:{})});
try{
 for(const scenario of ['success','missing-bridge','ack-timeout','backend-error']){
  const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.route('**/*',r=>r.abort());
  await page.setContent('<style>jmv-results-html{display:block;margin:20px 0}</style><body><jmv-results-html class="jmv-results-html"><h2 id="title"></h2><div class="content"></div></jmv-results-html><p id="after">Following result</p>');
  await page.evaluate(({title,content,scenario})=>{
   document.getElementById('title').textContent=title;
   document.querySelector('.content').innerHTML=content;
   window.captures=[];
   if(scenario!=='missing-bridge')window.setOption=(name,text)=>window.captures.push(JSON.parse(text));
   if(scenario==='ack-timeout'){const original=window.setTimeout;window.setTimeout=(fn,delay,...args)=>original(fn,delay===30000?250:delay,...args);}
  },{...fixture,scenario});
  if(fixture.scripts)await page.addScriptTag({content:fs.readFileSync(path.join(process.env.MZPJ_TEST_ROOT,'inst/extdata/plotly.min.js'),'utf8')});
  // The initial CSS must already hide the result and heading before scripts run.
  assert(await page.locator('jmv-results-html').evaluate(el=>el.getBoundingClientRect().x<-90000));
  assert(await page.locator('[data-image-status]').evaluate(el=>el.hidden));
  assert(await page.locator('#after').evaluate(el=>el.getBoundingClientRect().y<50));
  await page.evaluate(()=>{for(const old of document.querySelector('.content').querySelectorAll('script')){const s=document.createElement('script');s.textContent=old.textContent;document.head.appendChild(s);s.remove();old.remove();}});
  if(scenario==='missing-bridge'||scenario==='ack-timeout'){
   await page.waitForFunction(()=>document.querySelector('[data-mzpj-image-capture]')?.dataset.mzpjImageCapture==='error');
   assert(await page.locator('[data-image-status]').isVisible());
   assert((await page.locator('[data-image-status]').innerText()).startsWith('Image preparation failed:'));
   assert(await page.locator('jmv-results-html').evaluate(el=>el.getBoundingClientRect().x>=0));
   if(scenario==='ack-timeout')assert((await page.locator('[data-image-status]').innerText()).includes('not acknowledged'));
  }else{
   await page.waitForFunction(()=>window.captures.length>0);
   assert(await page.locator('[data-image-status]').evaluate(el=>el.hidden&&el.textContent===''));
   const payload=await page.evaluate(()=>window.captures[0]);assert(payload.images[0].content.startsWith('iVBORw0KGgo'));
   assert(await page.locator('jmv-results-html').evaluate(el=>el.getBoundingClientRect().x<-90000));
   if(scenario==='backend-error'){
    await page.evaluate(()=>document.querySelector('.content').innerHTML='<p>Native Image preparation failed. Reduce the figure size and run again.</p>');
    assert(await page.locator('jmv-results-html').evaluate(el=>el.getBoundingClientRect().x>=0));
   }else await page.evaluate(()=>document.querySelector('jmv-results-html').remove());
   await page.waitForFunction(()=>window.mzPjNativeImageQueue.entries.size===0&&window.mzPjNativeImageQueue.ackTimers.size===0);
  }
  assert.deepEqual(errors,[]);await page.close();console.log(scenario+' quiet preparation, capture/error visibility and cleanup PASSED');
 }
}finally{await browser.close();}})().catch(error=>{console.error(error);process.exitCode=1;});

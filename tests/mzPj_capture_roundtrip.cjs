const fs=require('fs'),path=require('path'),assert=require('assert'),cp=require('child_process');
const {chromium}=require(process.env.MZPJ_PLAYWRIGHT);
const work=process.env.MZPJ_TEST_WORK,root=process.env.MZPJ_TEST_ROOT;
const linux=process.env.MZPJ_TEST_LINUX==='1';
function engine(folder,command,mode,prefix){
 const script=linux?root+'/tests/mzPj_capture_roundtrip.R':path.join(root,'tests/mzPj_capture_roundtrip.R');
 const args=linux?['-d','Ubuntu-26.04','--','flatpak','run','--devel','--filesystem='+root+':ro','--filesystem='+work+':rw','--command=Rscript','org.jamovi.jamovi',script,root,folder,command,mode,prefix]:['--vanilla',script,root,folder,command,mode,prefix];
 const result=cp.spawnSync(linux?'wsl.exe':'C:/Program Files/jamovi 28.18.0.0/Frameworks/R/bin/Rscript.exe',args,{encoding:'utf8',timeout:180000});
 fs.appendFileSync(process.env.MZPJ_TEST_LOG,result.stdout||'');fs.appendFileSync(process.env.MZPJ_TEST_LOG,result.stderr||'');
 if(result.status!==0)throw Error('Engine failed: '+result.status+' '+result.stderr+' '+result.stdout);
 const physical=linux?process.env.MZPJ_LINUX_WINDOWS_WORK+'/'+path.basename(folder):folder;
 return {folder,physical,...JSON.parse(fs.readFileSync(path.join(physical,'manifest.json'),'utf8'))};
}
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.MZPJ_CHROME});
 try{
 for(const prefix of ['Pj','Pjp'])for(const mode of ['bundled','external']){
  const folder=work+'/'+prefix+'_'+mode;
  let state=engine(folder,'init',mode,prefix);assert.equal(state.pending.length,2);
  const tableCount=state.tables;
  for(let step=0;state.pending.length&&step<4;step++){
   const page=await browser.newPage(),captures=[],errors=[];
   page.on('pageerror',e=>errors.push(e.message));await page.route('**/*',r=>r.abort());
   await page.exposeFunction('reportCapture',(name,text)=>captures.push(JSON.parse(text)));
   await page.setContent('<meta charset="utf-8"><body></body>');
   for(const item of state.pending){
    await page.evaluate(html=>{const frame=document.createElement('iframe');frame.width=1000;frame.height=500;frame.srcdoc='<meta charset="utf-8"><script>window.setOption=(name,text)=>parent.reportCapture(name,text);</script>'+html;document.body.append(frame);},item.content);
   }
   await page.waitForFunction(()=>Array.from(document.querySelectorAll('iframe')).every(f=>f.contentDocument&&f.contentDocument.querySelector('[data-image-status]')?.textContent==='Preparing native Image result…'),{timeout:45000});
   const until=Date.now()+45000;while(!captures.length&&Date.now()<until)await new Promise(r=>setTimeout(r,20));
   assert(captures.length);assert.deepEqual(errors,[]);
   // Deliberately handle one frame at a time, as independent Results iframes do.
   const payload=captures[0];fs.writeFileSync(path.join(state.physical,'capture.json'),JSON.stringify(payload));
   const previous=state.pending.length;await page.close();
   state=engine(folder,'capture',mode,prefix);
   assert(state.pending.length<previous);assert.equal(state.runs,1);assert.equal(state.tables,tableCount);
  }
  assert.equal(state.pending.length,0);assert.equal(state.imageNames.length,3);
  console.log((linux?'WSL Linux':'Windows'),prefix,mode,'Script 73: separate iframes, two captured figures + PNG control, one execution, tables retained PASSED');
 }
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});

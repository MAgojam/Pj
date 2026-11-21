const fs=require('fs'),path=require('path'),assert=require('assert'),cp=require('child_process');
const {chromium}=require(process.env.MZPJ_PLAYWRIGHT);
const work=process.env.MZPJ_TEST_WORK,root=process.env.MZPJ_TEST_ROOT;
const linux=process.env.MZPJ_TEST_LINUX==='1';
function engine(folder,command,mode,prefix){
 const script=linux?root+'/tests/mzPj_capture_roundtrip.R':path.join(root,'tests/mzPj_capture_roundtrip.R');
 const args=linux?['-d','Ubuntu-26.04','--','flatpak','run','--devel','--filesystem='+root+':ro','--filesystem='+work+':rw',...['MZPJ_CAPTURE_SCRIPT','MZPJ_CAPTURE_RESULT_TYPE','MZPJ_CAPTURE_RENDERER','MZPJ_EXPECTED_IMAGES'].filter(key=>process.env[key]).map(key=>'--env='+key+'='+process.env[key]),'--command=Rscript','org.jamovi.jamovi',script,root,folder,command,mode,prefix]:['--vanilla',script,root,folder,command,mode,prefix];
 const result=cp.spawnSync(linux?'wsl.exe':'C:/Program Files/jamovi 28.18.0.0/Frameworks/R/bin/Rscript.exe',args,{encoding:'utf8',timeout:180000});
 fs.appendFileSync(process.env.MZPJ_TEST_LOG,result.stdout||'');fs.appendFileSync(process.env.MZPJ_TEST_LOG,result.stderr||'');
 if(result.status!==0)throw Error('Engine failed: '+result.status+' '+result.stderr+' '+result.stdout);
 const physical=linux?process.env.MZPJ_LINUX_WINDOWS_WORK+'/'+path.basename(folder):folder;
 const state=JSON.parse(fs.readFileSync(path.join(physical,'manifest.json'),'utf8'));
 if(typeof state.imageNames==='string')state.imageNames=[state.imageNames];
 return {folder,physical,...state};
}
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.MZPJ_CHROME});
 try{
 for(const prefix of ['Pj','Pjp'])for(const mode of ['bundled','external']){
  const folder=work+'/'+prefix+'_'+mode;
  let state=engine(folder,'init',mode,prefix);assert.equal(state.pending.length,Number(process.env.MZPJ_EXPECTED_CAPTURES||2));const expectedTitles=new Map(state.pending.map(item=>[item.name,item.title]));assert(state.pending.every(item=>item.heading===''),'pending server headings must be empty');
  const tableCount=state.tables;
  for(let step=0;state.pending.length&&step<Number(process.env.MZPJ_EXPECTED_CAPTURES||2)+2;step++){
   const page=await browser.newPage(),captures=[],errors=[];
   page.on('pageerror',e=>errors.push(e.message));await page.route('**/*',r=>r.abort());
   await page.exposeFunction('reportCapture',(name,text)=>captures.push(JSON.parse(text)));
   await page.setContent('<meta charset="utf-8"><body></body>');
   for(const item of state.pending){
    await page.evaluate(html=>{const frame=document.createElement('iframe');frame.width=1000;frame.height=500;frame.srcdoc='<meta charset="utf-8"><script>window.setOption=(name,text)=>parent.reportCapture(name,text);</script>'+html;document.body.append(frame);},((process.env.MZPJ_CAPTURE_PLOTLY==='1'||process.env.MZPJ_CAPTURE_SCRIPT==='77_shared_graphics.py')?'<script>'+fs.readFileSync(path.join(process.env.MZPJ_RESOURCE_ROOT||root,'inst/extdata/plotly.min.js'),'utf8')+'</script>':'')+item.content);
   }
   await page.waitForFunction(()=>Array.from(document.querySelectorAll('iframe')).every(f=>f.contentDocument&&f.contentDocument.querySelector('[data-mzpj-image-capture]')?.dataset.mzpjImageReady==='true'),null,{timeout:45000});
   const until=Date.now()+45000;while(!captures.length&&Date.now()<until)await new Promise(r=>setTimeout(r,20));
   assert(captures.length);assert.deepEqual(errors,[]);
   // Deliberately handle one frame at a time, as independent Results iframes do.
   const payload=captures[0];fs.writeFileSync(path.join(state.physical,'capture.json'),JSON.stringify(payload));
   const previous=state.pending.length;await page.close();
   state=engine(folder,'capture',mode,prefix);
   assert(state.pending.length<previous);assert.equal(state.runs,1);assert.equal(state.tables,tableCount);
  }
  assert.equal(state.pending.length,0);assert.equal(state.imageNames.length,Number(process.env.MZPJ_EXPECTED_IMAGES||3));for(const image of state.imageTitles)if(expectedTitles.has(image.name))assert.equal(image.title,expectedTitles.get(image.name),'final Image title must be preserved');
  console.log((linux?'WSL Linux':'Windows'),prefix,mode,(process.env.MZPJ_CAPTURE_SCRIPT||'73_rust_repeated_measures.py')+': separate iframes, captured figures, one execution, tables retained PASSED');
 }
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});

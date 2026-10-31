/* Browser integration check; run with Node + Playwright + system Chromium. */
const {chromium} = require('playwright');
const path = require('path');
(async () => {
 const browser = await chromium.launch({headless:true,executablePath:process.env.CHROMIUM || '/usr/bin/chromium',args:['--no-sandbox','--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 try {
 const page = await browser.newPage({viewport:{width:1360,height:1100}}), errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 page.on('response',r=>{if(r.status()>=400 && !r.url().endsWith('favicon.ico')) errors.push(`${r.status()} ${r.url()}`);});
 await page.goto((process.env.RUNTIME_URL || 'http://127.0.0.1:8765/assets%20runtime/')+'demo.html');
 await page.waitForFunction(()=>window.runtimeDemoReady);
 const report = await page.evaluate(async()=>{
  const m=window.commanderMaterials, old=await fetch('../assets%20v2/manifest.json').then(r=>r.json());
  let stable=0;
  for(const model of m.catalog.models){
   const styles=m.styles(model.id);if(new Set(styles.map(s=>s.id)).size!==styles.length)throw Error('Duplicate IDs');
   styles.forEach((s,i)=>{if(s.id!==`${model.id}_${i+1}`)throw Error('Noncontiguous ID');});
   for(const row of old.filter(r=>r.model_id===model.id)){
    const s=styles[row.color_number-1];if(s.id!==row.id)throw Error('Legacy ID changed');
    if(row.texture_id && row.texture_id!==s.texture)throw Error('Legacy texture changed');
    if(row.solid_hex && row.solid_hex!==s.hex)throw Error('Legacy solid changed');
    stable++;
   }
  }
  const base=await m.data(m.models.get('uniform_1').base), mask=await m.data(m.models.get('uniform_1').mask);
  const region=await m.data(m.models.get('uniform_1').regions.sleeves.file);
  const output=await m.render('uniform_1',{kind:'camouflage',texture:'premium-02-06',region:'sleeves'});
  const pixels=output.getContext('2d').getImageData(0,0,1024,1024).data;
  let protectedPixels=0,changed=0;
  for(let i=0;i<pixels.length;i+=4){
   if(pixels[i+3]!==base.data[i+3])throw Error('Alpha changed');
   if(base.data[i+3]>=240 && (!region.data[i] || !mask.data[i])){
    if([0,1,2].some(k=>Math.abs(pixels[i+k]-base.data[i+k])>1))throw Error('Protected part changed');protectedPixels++;
   }
   if(base.data[i+3]>=240 && pixels[i]!==base.data[i])changed++;
  }
  if(changed<1000 || protectedPixels<10000)throw Error('Partial material ineffective');
  // Render all 216 choices in browser; covers six map samplers and all palettes.
  for(const t of m.catalog.textures)await m.render('helmet_1',{kind:'camouflage',texture:t.id});
  for(const color of m.catalog.solids)await m.render('uniform_1',{kind:'solid',hex:color.hex,region:'torso'});
  for(const [id,regionName] of [['cap_1','crown'],['vest_11',null]]){
   const model=m.models.get(id),b=await m.data(model.base),mm=await m.data(model.mask);
   const rr=regionName?await m.data(model.regions[regionName].file):null;
   const result=await m.render(id,{kind:'camouflage',texture:'pustinjska-01-01',region:regionName});
   const data=result.getContext('2d').getImageData(0,0,1024,1024).data;
   for(let i=0;i<data.length;i+=4){
    if(data[i+3]!==b.data[i+3])throw Error('Accessory alpha changed');
    if(b.data[i+3]>=240 && (!mm.data[i] || (rr && !rr.data[i])) && [0,1,2].some(k=>Math.abs(data[i+k]-b.data[i+k])>1))throw Error('Protected cap brim or medical mark changed');
   }
  }
  const legacy=await m.renderItem('helmet_1_3');if(legacy.width!==1024)throw Error('Legacy renderer failed');
  let rejected=false;try{await m.render('uniform_1',{kind:'camouflage',texture:'unknown'});}catch(e){rejected=true;}if(!rejected)throw Error('Invalid material accepted');
  // Exercise portable GPU core and compare opaque pixels to CPU implementation.
  const gpu=document.createElement('canvas');gpu.width=gpu.height=1024;
  const gl=gpu.getContext('webgl',{preserveDrawingBuffer:true});if(!gl)throw Error('No WebGL');
  const frag=await fetch('material.frag').then(r=>r.text());
  function compile(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;}
  const program=gl.createProgram();gl.attachShader(program,compile(gl.VERTEX_SHADER,'attribute vec2 position; varying vec2 vMaterialUV; void main(){vMaterialUV=vec2((position.x+1.0)*.5,(1.0-position.y)*.5);gl_Position=vec4(position,0.,1.);}'));
  gl.attachShader(program,compile(gl.FRAGMENT_SHADER,frag));gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));gl.useProgram(program);
  const buf=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buf);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);
  const loc=gl.getAttribLocation(program,'position');gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,2,gl.FLOAT,false,0,0);
  const tex=m.textures.get('premium-02-06'),model=m.models.get('uniform_1');
  const files=[model.base,model.mask,model.regions.sleeves.file,m.catalog.patterns[tex.pattern]];
  const names=['uBase','uMask','uRegion','uIndex'];
  for(let i=0;i<files.length;i++){
   const image=await m.image(files[i]);gl.activeTexture(gl.TEXTURE0+i);gl.bindTexture(gl.TEXTURE_2D,gl.createTexture());
   gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,i===0);gl.pixelStorei(gl.UNPACK_COLORSPACE_CONVERSION_WEBGL,gl.NONE);
   gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);
   gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
   gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,image);gl.uniform1i(gl.getUniformLocation(program,names[i]),i);
  }
  gl.uniform1f(gl.getUniformLocation(program,'uKind'),2);gl.uniform1f(gl.getUniformLocation(program,'uShadeDivisor'),160);
  const palette=m.palettes.get(tex.palette).colors.flatMap(h=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16)/255));gl.uniform3fv(gl.getUniformLocation(program,'uPalette[0]'),palette);
  gl.viewport(0,0,1024,1024);gl.drawArrays(gl.TRIANGLE_STRIP,0,4);
  const gpuPixels=new Uint8Array(1024*1024*4);gl.readPixels(0,0,1024,1024,gl.RGBA,gl.UNSIGNED_BYTE,gpuPixels);
  let compared=0,maxDelta=0;
  for(let y=0;y<1024;y+=3)for(let x=0;x<1024;x+=3){const i=(y*1024+x)*4,j=((1023-y)*1024+x)*4;if(pixels[i+3]<240)continue;for(let k=0;k<4;k++){const expected=k===3?pixels[i+k]:pixels[i+k]*pixels[i+3]/255;maxDelta=Math.max(maxDelta,Math.abs(expected-gpuPixels[j+k]));}compared++;}
  if(maxDelta>4 || compared<10000)throw Error(`GPU mismatch ${maxDelta} / ${compared}`);
  gl.getExtension('WEBGL_lose_context')?.loseContext();
  return {legacyIdsChecked:stable,browserCamouflagesRendered:216,browserSolidColorsRendered:m.catalog.solids.length,partialCapAndMedicalMark:'passed',alphaPreserved:true,protectedPixels,paintedPixels:changed,webglShader:'compiled and rendered',gpuComparedPixels:compared,gpuMaxByteDelta:maxDelta};
 });
 await page.selectOption('#uniformRegion','sleeves');
 await page.selectOption('#texture','premium-02-06');
 await page.waitForFunction(()=>document.getElementById('status').textContent==='Prikaz je spreman.');
 const qa=path.join(__dirname,'qa');require('fs').mkdirSync(qa,{recursive:true});
 await page.screenshot({path:path.join(qa,'runtime-desktop.jpg'),type:'jpeg',quality:90});
 await page.selectOption('#facewear','balaclava_1');await page.selectOption('#headgear','helmet_20');
 await page.waitForFunction(()=>document.getElementById('status').textContent.includes('Zatvoren šlem'));
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(qa,'runtime-mobile.jpg'),type:'jpeg',quality:85});
 if(errors.length)throw Error(errors.join('\n'));
 console.log(JSON.stringify({...report,closedHelmetRule:'passed',browserErrors:errors.length},null,2));
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});

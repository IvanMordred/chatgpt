import {CommanderMaterials} from './materials.js';
const $ = id => document.getElementById(id);
const slots = ['uniform', 'vest', 'facewear', 'headgear'];
let materials, ticket = 0;
function option(parent, value, text) { const o = new Option(text, value); parent.add(o); }
function regions(slot) {
  const select = $(slot + 'Region'); if (!select) return;
  const previous = select.value; select.replaceChildren(); option(select, '', 'Sav označeni materijal');
  const m = materials.models.get($(slot).value);
  for (const [id, r] of Object.entries(m?.regions || {})) option(select, id, r.label);
  if ([...select.options].some(o => o.value === previous)) select.value = previous;
}
async function draw() {
  const current = ++ticket; $('status').textContent = 'Primenjujem materijal…';
  try {
    const selected = $('texture').value;
    const style = selected.startsWith('#') ? {kind:'solid',hex:selected} : {kind:'camouflage',texture:selected};
    const excluded = new Set();
    const rules = await compatibility;
    for (const slot of slots) for (const rule of rules.rules) if (rule.models?.includes($(slot).value) || (rule.type && materials.models.get($(slot).value)?.type === rule.type)) {
      for (const blocked of rule.exclude_slots) if (blocked !== slot) excluded.add(blocked);
    }
    const head = await materials.image(materials.catalog.head);
    const layers = [];
    for (const slot of slots) {
      const id = $(slot).value; if (!id || excluded.has(slot)) continue;
      const model = materials.models.get(id);
      const paint = $(slot+'Paint').value === 'selected' && (style.kind === 'solid' || model.camouflageEnabled);
      layers.push(await materials.render(id, {...(paint ? style : {kind:'base'}),region:$(slot+'Region')?.value || null}));
    }
    if (current !== ticket) return;
    const ctx = $('portrait').getContext('2d');ctx.clearRect(0,0,1024,1024);ctx.drawImage(head,0,0);
    for (const layer of layers) ctx.drawImage(layer,0,0);
    $('status').textContent = excluded.has('facewear') && $('facewear').value ? 'Zatvoren šlem: maska je sakrivena.' : 'Prikaz je spreman.';
    window.runtimeDemoReady = true;
  } catch (e) { if (current === ticket) $('status').textContent = e.message; console.error(e); }
}
let compatibility;
try {
  materials = await CommanderMaterials.load('./');window.commanderMaterials=materials;
  compatibility = fetch(new URL(materials.catalog.compatibility,materials.root)).then(r=>r.json());
  const palette = new Map(materials.catalog.palettes.map(p=>[p.id,p]));
  for (const t of materials.catalog.textures) option($('texture'),t.id,`${palette.get(t.palette).category} · ${t.label}`);
  for (const c of materials.catalog.solids) option($('texture'),c.hex,`Boja · ${c.name}`);
  const categories={uniform:['uniform'],vest:['vest'],facewear:['balaclava','mask','scarf','gasmask'],headgear:['cap','helmet','hat','hood','beret']};
  for (const slot of slots) {
    if(slot!=='uniform')option($(slot),'','Bez');
    for(const m of materials.catalog.models)if(categories[slot].includes(m.type))option($(slot),m.id,`${m.id} · ${m.name}`);
  }
  $('uniform').value='uniform_1';$('vest').value='';$('headgear').value='cap_1';$('facewear').value='';
  regions('uniform');regions('headgear');
  for(const select of document.querySelectorAll('select'))select.addEventListener('change',()=>{if(['uniform','headgear'].includes(select.id))regions(select.id);draw();});
  $('download').onclick=()=> $('portrait').toBlob(blob=>{const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='commander_preview.png';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  await draw();
} catch(e){$('status').textContent=e.message;console.error(e);}

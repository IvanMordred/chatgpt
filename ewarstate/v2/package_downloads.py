"""Independent <=20MiB ZIP chunks with the requested folder structure intact."""
from pathlib import Path
from collections import defaultdict
import json,zipfile,hashlib,io
V=Path(__file__).resolve().parent;REPO=V.parent.parent;O=REPO/'assets v2';D=V.parent/'downloads/v2';D.mkdir(parents=True,exist_ok=True)
records=json.loads((O/'manifest.json').read_text());groups=defaultdict(list)
for r in records:groups[r['type']].append(r)
index=[];LIMIT=20*1024*1024
for typ,arr in groups.items():
 part=1;chunk=[];size=0
 def write_chunk(entries,part):
  p=D/(typ+'_part_'+str(part)+'.zip')
  with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for r in entries:z.write(REPO/r['file'],r['file'])
  assert p.stat().st_size<LIMIT,(p,p.stat().st_size)
  index.append({'file':p.name,'type':typ,'items':len(entries),'ids':[r['id'] for r in entries],'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 for r in sorted(arr,key=lambda r:(r['model_number'],r['color_number'])):
  n=(REPO/r['file']).stat().st_size
  if chunk and size+n>LIMIT-65536:write_chunk(chunk,part);part+=1;chunk=[];size=0
  chunk.append(r);size+=n
 if chunk:write_chunk(chunk,part)
meta=D/'catalog.zip'
with zipfile.ZipFile(meta,'w',zipfile.ZIP_DEFLATED) as z:
 for name in ['README.md','preview.html','catalog.js','manifest.json','validation.json','examples.json','compatibility.json','reference/head.png','previews/commanders_1.jpg','previews/commanders_2.jpg']:
  z.write(O/name,'assets v2/'+name)
assert meta.stat().st_size<LIMIT
index.append({'file':meta.name,'type':'catalog','items':0,'bytes':meta.stat().st_size,'sha256':hashlib.sha256(meta.read_bytes()).hexdigest()})
(D/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2))
lines=['# eWarState V2 — ZIP paketi','', 'Svaki ZIP je manji od 20 MiB. Paketi su samostalni ZIP fajlovi; raspakuj ih u isti direktorijum da bi se spojila struktura `assets v2/kategorija/model/predmet.png`. `catalog.zip` dodaje manifest, osnovnu glavu i lokalni preglednik. GitHub: otvori ZIP, zatim **Download raw file**.','', '| Paket | PNG | MiB |','|---|---:|---:|']
for x in index:lines.append(f"| [{x['file']}]({x['file']}) | {x['items']} | {x['bytes']/1024/1024:.2f} |")
(D/'README.md').write_text('\n'.join(lines)+'\n')
print('Packages:',len(index),'PNG:',sum(x['items'] for x in index),'total MiB:',round(sum(x['bytes'] for x in index)/1024/1024,2))

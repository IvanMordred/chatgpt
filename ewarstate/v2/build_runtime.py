"""Build lossless, masked browser materials; never export color permutations."""
from pathlib import Path
from collections import defaultdict
import json, hashlib
import numpy as np
from PIL import Image, ImageDraw
V=Path(__file__).resolve().parent
ROOT=V.parents[1]
OUT=ROOT/'assets runtime'
OUT.mkdir(exist_ok=True)
def write_json(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n')
def webp(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True)
 a=Image.open(src).convert('RGBA')
 if not dst.exists():a.save(dst,lossless=True,exact=True,method=4)
 assert np.array_equal(np.array(a),np.array(Image.open(dst).convert('RGBA'))),str(dst)
def relative(p):return p.relative_to(OUT).as_posix()
textures=json.loads((ROOT/'ewarstate/camouflage/manifest.json').read_text())
patterns={};palettes={};styles=[]
for t in textures:
 a=np.array(Image.open(ROOT/'ewarstate/camouflage'/t['file']).convert('RGB'))
 ix=np.full(a.shape[:2],255,dtype=np.uint8)
 colors=np.array([list(bytes.fromhex(h[1:])) for h in t['colors']],dtype=np.uint8)
 for k,c in enumerate(colors):ix[np.all(a==c,axis=2)]=k
 assert not (ix==255).any()
 assert np.array_equal(ix,np.repeat(np.repeat(ix[::2,::2],2,axis=0),2,axis=1))
 small=ix[::2,::2]
 if t['pattern'] in patterns:assert np.array_equal(small,patterns[t['pattern']])
 else:
  patterns[t['pattern']]=small
  p=OUT/'patterns'/(t['pattern']+'.png');p.parent.mkdir(exist_ok=True)
  Image.fromarray(small).save(p,optimize=True)
 # Verify all 216 reconstructed RGB textures, not only first palette.
 assert np.array_equal(colors[np.repeat(np.repeat(small,2,axis=0),2,axis=1)],a)
 palette='-'.join(t['id'].split('-')[:2])
 palettes[palette]={'id':palette,'name':t['palette'],'category':t['category'],'colors':t['colors']}
 styles.append({'id':t['id'],'palette':palette,'pattern':t['pattern'],'label':t['palette']+' / '+t['pattern']})
old=json.loads((ROOT/'assets v2/manifest.json').read_text())
groups=defaultdict(list)
for r in old:groups[r['model_id']].append(r)
file_tex={('ewarstate/camouflage/'+t['file']):t['id'] for t in textures}
models=[]
for id,rows in groups.items():
 rows.sort(key=lambda r:r['color_number']);r=rows[0];typ=r['type'];num=r['model_number']
 folder=Path(rows[0]['file']).parent.relative_to('assets v2')
 dest=OUT/folder;src=V/'models'/id
 webp(src/'base.png',dest/'base.webp')
 mask=Image.open(src/'material_mask.png').convert('L');mask.save(dest/'material_mask.png',optimize=True)
 eligible=(typ in ['uniform','vest','balaclava','scarf'] or (typ=='helmet' and num<=11) or (typ=='cap' and num!=10) or (typ=='hat' and num in [1,2,5]) or (typ=='hood' and num!=2) or (typ=='mask' and num in [1,3]))
 legacy=[]
 for row in rows:
  rec={'id':row['id'],'label':row['label']}
  texture=row.get('texture_id') or file_tex.get(row.get('texture_file'))
  if texture:rec.update(kind='camouflage',texture=texture)
  elif row.get('solid_hex'):rec.update(kind='solid',hex=row['solid_hex'])
  else:rec['kind']='base'
  legacy.append(rec)
 regions={}
 if id=='uniform_1':
  # Follow visible armhole seams; these maps change paint only, never alpha.
  sleeve=Image.new('L',(1024,1024));d=ImageDraw.Draw(sleeve)
  pts=[(0,770),(44,797),(68,849),(83,922),(123,1023),(0,1023)]
  d.polygon(pts,fill=255);d.polygon([(1023-x,y) for x,y in pts],fill=255)
  sleeve.save(dest/'region_sleeves.png');regions['sleeves']={'label':'Samo rukavi','file':relative(dest/'region_sleeves.png')}
  torso=Image.fromarray(255-np.array(sleeve));torso.save(dest/'region_torso.png')
  regions['torso']={'label':'Torzo i kragna','file':relative(dest/'region_torso.png')}
 if id=='cap_1':
  crown=Image.new('L',(1024,1024));d=ImageDraw.Draw(crown)
  d.polygon([(0,0),(1023,0),(1023,355),(717,333),(677,306),(641,284),(602,264),(557,249),(512,245),(470,249),(425,261),(383,280),(347,303),(307,331),(0,355)],fill=255)
  crown.save(dest/'region_crown.png');regions['crown']={'label':'Samo kruna kape','file':relative(dest/'region_crown.png')}
 models.append({'id':id,'type':typ,'name':r['name'],'base':relative(dest/'base.webp'),'mask':relative(dest/'material_mask.png'),'shadeDivisor':175 if id=='helmet_1' else 160,'camouflageEnabled':eligible,'legacyStyles':legacy,'regions':regions})
 print('base',id,flush=True)
webp(V/'reference/head.png',OUT/'reference/head.webp')
solids=json.loads((ROOT/'ewarstate/helmets/solid_colors.json').read_text())
catalog={'schema':1,'canvas':[1024,1024],'head':'reference/head.webp','models':models,'palettes':list(palettes.values()),'patterns':{k:'patterns/'+k+'.png' for k in patterns},'textures':styles,'solids':solids,'compatibility':'compatibility.json'}
write_json(OUT/'catalog.json',catalog)
compatibility=json.loads((ROOT/'assets v2/compatibility.json').read_text())
compatibility.pop('examples_file',None)
compatibility['reviewed_examples_reference']='../assets v2/examples.json'
write_json(OUT/'compatibility.json',compatibility)
old_bytes=sum((ROOT/r['file']).stat().st_size for r in old)
virtual=sum(len(m['legacyStyles'])+sum(t['id'] not in {x.get('texture') for x in m['legacyStyles']} for t in styles) if m['camouflageEnabled'] else len(m['legacyStyles']) for m in models)
report={'baseModels':len(models),'legacyItemIds':len(old),'camouflageModels':sum(m['camouflageEnabled'] for m in models),'virtualItemVariants':virtual,'sharedPatterns':len(patterns),'sharedPalettes':len(palettes),'reconstructedTextures':len(styles),'losslessBaseDecode':'all 171 bases and master head pixel-exact','textureReconstruction':'all 216 pixel-exact at 1024x1024','alpha':'base alpha retained; material and region masks affect RGB only','legacyPngBytes':old_bytes}
report['runtimePayloadBytesExcludingThisReport']=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file() and p.name!='validation.json')
report['payloadReductionPercent']=round(100*(1-report['runtimePayloadBytesExcludingThisReport']/old_bytes),2)
write_json(OUT/'validation.json',report)
print(json.dumps(report,indent=2))

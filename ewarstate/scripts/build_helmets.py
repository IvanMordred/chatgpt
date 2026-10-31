from pathlib import Path
from PIL import Image, ImageDraw, ImageFont,ImageFilter
import numpy as np,json,zipfile,hashlib,csv
R=Path(__file__).resolve().parents[1];O=R/'helmets'
base=Image.open(O/'model/helmet_base.png').convert('RGBA');a=np.array(base);gray=np.mean(a[:,:,:3],axis=2)
# Geometric exclusions keep the central mount, rails and lower rubber rim intact.
m=Image.new('L',(1024,1024));d=ImageDraw.Draw(m)
d.polygon([(327,214),(345,166),(385,120),(450,84),(510,71),(577,84),(644,123),(681,169),(700,213),(677,252),(666,319),(625,295),(574,281),(449,281),(393,296),(350,319),(346,252)],fill=255)
d.polygon([(474,158),(548,158),(554,173),(579,195),(582,263),(555,288),(472,288),(443,266),(440,196),(462,176)],fill=0)
d.polygon([(290,202),(326,202),(352,239),(362,279),(353,324),(291,330)],fill=0)
d.polygon([(674,201),(738,201),(738,331),(670,324),(662,282),(671,240)],fill=0)
mask=np.array(m.filter(ImageFilter.GaussianBlur(.7)),dtype='float32')/255
mask*=np.clip((gray-90)/35,0,1)*(a[:,:,3]>0)
Image.fromarray((mask*255).astype('uint8')).save(O/'model/shell_mask.png')
shade=np.clip(gray/185,.35,1.35)[...,None]
commander=Image.new('RGBA',(1024,1024),'#242c30')
# Use exact source layers from the user's original pack.
pack=next((R/'source-packs').glob('ewarstate_master_proba*.zip'))
with zipfile.ZipFile(pack) as z:
 import io
 for name in ['01_glava.png','02_uniforma.png','03_pancir.png']:
  commander.alpha_composite(Image.open(io.BytesIO(z.read(name))).convert('RGBA'))
records=json.loads((R/'camouflage/manifest.json').read_text())
solids=[('black','Crna','#171A1F'),('anthracite','Antracit','#343B43'),('graphite','Grafit','#565D63'),('steel','Celicna siva','#83909A'),('silver','Srebrna','#BBC4CB'),('white','Bela','#E4E8E7'),('ivory','Slonovaca','#DCD4BC'),('olive','Maslinasta','#697247'),('od_green','Vojnicka zelena','#495941'),('forest','Sumska zelena','#2D4736'),('sage','Zalfija','#89947A'),('coyote','Kojot braon','#9D8056'),('sand','Pescana','#D5BD8B'),('khaki','Kaki','#B2A175'),('brown','Braon','#71503B'),('navy','Mornarska plava','#20364F'),('cobalt','Kobalt','#2863A4'),('slate','Plavosiva','#60788D'),('teal','Petrolej','#2D716C'),('burgundy','Bordo','#692A3D'),('crimson','Grimizna','#A2373F'),('orange','Narandzasta','#D47B32'),('gold','Zlatna','#BCA15A'),('amethyst','Ametist','#8056A3')]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',26)
sheets={};manifest=[];samples=[]
for cat in ['sumska','pustinjska','urbana','tropska','snezna','premium','solid']:
 rows=4 if cat=='solid' else 6
 sh=Image.new('RGB',(1440,64+rows*264),'#151C23');ImageDraw.Draw(sh).text((14,15),f'eWarState / SLEM / {cat.upper()}',font=ft,fill='#E8DBB9');sheets[cat]=sh
variants=[]
for rec in records:variants.append((rec['category'],f"helmet_{rec['id'].replace('-','_')}",rec['palette']+' / '+rec['pattern'],rec,None))
for i,(code,name,hx) in enumerate(solids):variants.append(('solid',f'helmet_solid_{i+1:02d}_{code}',name,None,hx))
counts={k:0 for k in sheets}
for cat,stem,label,rec,hx in variants:
 if rec:
  tex=Image.open(R/'camouflage'/rec['file']).convert('RGB').resize((512,512),Image.Resampling.NEAREST)
  paint=Image.new('RGB',(1024,1024));paint.paste(tex,(256,0));rgb=np.array(paint,dtype='float32')
 else:rgb=np.full((1024,1024,3),tuple(bytes.fromhex(hx[1:])),dtype='float32')
 colored=np.clip(rgb*shade,0,255)
 mix=mask[...,None];out=a.copy();out[:,:,:3]=np.clip(a[:,:,:3]*(1-mix)+colored*mix,0,255).astype('uint8');out[a[:,:,3]==0,:3]=0
 im=Image.fromarray(out,'RGBA');dest=O/'assets'/cat;dest.mkdir(parents=True,exist_ok=True);p=dest/(stem+'.png');im.save(p)
 preview=commander.copy();preview.alpha_composite(im)
 n=counts[cat];counts[cat]+=1;x=(n%6)*240;y=64+(n//6)*264
 sheets[cat].paste(preview.convert('RGB').resize((236,236),Image.Resampling.LANCZOS),(x+2,y))
 ImageDraw.Draw(sheets[cat]).text((x+4,y+239),f'{n+1:02d} {label[:31]}',font=font,fill='#E8DBB9')
 mrec={'id':stem,'file':str(p.relative_to(O)),'category':cat,'label':label,'canvas':[1024,1024],'position':[0,0],'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 if rec:mrec.update(texture_file=rec['file'],texture_id=rec['id'],palette=rec['palette'])
 else:mrec['solid_hex']=hx
 manifest.append(mrec)
 if (cat!='solid' and n=={'sumska':0,'pustinjska':7,'urbana':14,'tropska':21,'snezna':28,'premium':35}[cat]) or (cat=='solid' and n in [0,7,12,17,20,22]):samples.append((stem,preview))
(O/'previews').mkdir(exist_ok=True)
for cat,sh in sheets.items():sh.save(O/'previews'/f'{cat}_helmets.jpg',quality=94)
sample_sheet=Image.new('RGB',(1536,3*408),'#151C23')
for n,(stem,im) in enumerate(samples[:12]):
 x=n%4*384;y=n//4*408;sample_sheet.paste(im.convert('RGB').resize((384,384),Image.Resampling.LANCZOS),(x,y));ImageDraw.Draw(sample_sheet).text((x+7,y+388),stem,font=font,fill='white')
sample_sheet.save(O/'previews/selection_12.jpg',quality=95)
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(O/'solid_colors.json').write_text(json.dumps([{'id':x,'name':y,'hex':z} for x,y,z in solids],ensure_ascii=False,indent=2))
(O/'README.md').write_text('''# eWarState: jedan model, 240 slemova

216 kamuflaznih varijanti (svih 216 tekstura iz camouflage/manifest.json) + 24 jednobojne varijante.

Svaki assets/**/*.png je transparentni RGBA sloj 1024x1024. Dodati na master komandira na x=0,y=0 bez skaliranja. Dizajn je proveren na prilozenoj osnovnoj glavi, uniformi i panciru. Nema tvrdnje o kompatibilnosti sa svakom kosom, kapuljacom, slusalicama ili drugim dodacima. Sakriti kosu koja izlazi ispod slema; ne slagati drugo pokrivalo za glavu preko njega.

Ista silueta i alfa kanal u svih 240 varijanti. Tekstura je primenjena na masku skoljke uz zadrzane senke i osvetljenje; centralni nosac, bocne sine i donja ivica ostaju neutralni. Jednobojne varijante imaju senke i materijal, nisu ravne ikone. Zlatna i srebrna su vizuelni tonovi, ne PBR materijali.

model/helmet_base.png: generisani osnovni model registrovan na master glavu. model/shell_mask.png: maska povrsine koja se boji, pogodna i za dodatnu rucnu doradu. previews/: svih 240 varijanti na komandiru. manifest.json: veza svakog slema sa izvorom teksture. solid_colors.json: HEX baze za jednobojne varijante.

Reprodukcija: Python + Pillow + NumPy, pokrenuti python ewarstate/scripts/build_helmets.py iz repozitorijuma. Osnovni model i korisnicki master paket su sacuvani u repozitorijumu.
''')
files=list((O/'assets').rglob('*.png'));assert len(files)==240
hashes=set()
for p in files:
 im=Image.open(p);b=np.array(im);assert im.mode=='RGBA' and im.size==(1024,1024)
 assert np.array_equal(b[:,:,3],a[:,:,3]);assert b[800:, :,3].max()==0
 hashes.add(hashlib.sha256(p.read_bytes()).hexdigest())
assert len(hashes)==240
assert {m['texture_id'] for m in manifest if 'texture_id' in m}=={r['id'] for r in records}
zip_path=R/'downloads/ewarstate_240_slemova.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(O.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(O))
 with_source=R/'scripts/build_helmets.py';z.write(with_source,'build_helmets.py')
print(json.dumps({'variants':len(files),'unique':len(hashes),'camouflage':216,'solid':len(solids),'zip_mb':round(zip_path.stat().st_size/1e6,2)}))

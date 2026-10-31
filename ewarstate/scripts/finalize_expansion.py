from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,zipfile,io,hashlib,re,shutil
R=Path(__file__).resolve().parents[1];O=R/'expansion';models=json.loads((O/'models.json').read_text());manifest=json.loads((O/'manifest.json').read_text())
with zipfile.ZipFile(next((R/'source-packs').glob('ewarstate_master_proba*.zip'))) as z:
 def get(n):return Image.open(io.BytesIO(z.read(n))).convert('RGBA')
 head=get('01_glava.png');uniform=get('02_uniforma.png');vest=get('03_pancir.png')
base=Image.new('RGBA',(1024,1024));base.alpha_composite(head);base.alpha_composite(uniform);armored=base.copy();armored.alpha_composite(vest)
# Preserve the medical emblem as a white marking, rather than recoloring it as fabric.
b=np.array(Image.open(O/'models/vest_11/base.png'));lum=b[:,:,:3].mean(2);yy,xx=np.indices((1024,1024));cross=(lum>210)&(xx>400)&(xx<625)&(yy>800)&(yy<955)
for rec in manifest:
 if rec['id'].startswith('vest_11_'):
  p=O/rec['file'];a=np.array(Image.open(p));a[cross,:3]=b[cross,:3];Image.fromarray(a).save(p);rec['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14);ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
def composite(rec):
 asset=Image.open(O/rec['file']);b=Image.new('RGBA',(1024,1024),'#3C3944')
 if rec['type']=='background':b.alpha_composite(asset);b.alpha_composite(armored)
 elif rec['type']=='uniform':b.alpha_composite(head);b.alpha_composite(asset)
 elif rec['type']=='vest':b.alpha_composite(base);b.alpha_composite(asset)
 else:b.alpha_composite(armored);b.alpha_composite(asset)
 return b
for group in dict.fromkeys(m['group'] for m in models):
 group_models=[m for m in models if m['group']==group];sheet=Image.new('RGB',(1800,60+((len(group_models)+5)//6)*330),'#182028');d=ImageDraw.Draw(sheet);d.text((15,13),'eWarState / '+group.upper(),font=ft,fill='#E8D9B8')
 for i,m in enumerate(group_models):
  entries=[r for r in manifest if r['type']==m['type'] and r['model_number']==m['number']];sh=Image.new('RGB',(250*len(entries),280),'#182028')
  for ci,rec in enumerate(entries):
   im=composite(rec);sh.paste(im.convert('RGB').resize((250,250),Image.Resampling.LANCZOS),(ci*250,0));ImageDraw.Draw(sh).text((ci*250+4,254),rec['id']+' / '+rec['color'],font=font,fill='#E8D9B8')
  sh.save(O/'previews'/(m['id']+'.jpg'),quality=92)
  rec=entries[min(2,len(entries)-1)];im=composite(rec);x=i%6*300;y=60+i//6*330;sheet.paste(im.convert('RGB').resize((300,300),Image.Resampling.LANCZOS),(x,y));d.text((x+5,y+302),rec['id']+' / '+m['name'][:18],font=font,fill='#E8D9B8')
 sheet.save(O/'qa'/(group+'_all.jpg'),quality=95)
# Representative combinations validate the separation of clothes from armor.
combos=Image.new('RGB',(1800,2*330+50),'#182028');d=ImageDraw.Draw(combos);d.text((10,10),'eWarState / 12 KOMBINACIJA ODVOJENIH SLOJEVA',font=ft,fill='white')
for i in range(12):
 uid=f'uniform_{i*2+1}_3';vid=f'vest_{(i*7)%30+1}_2';u=next(r for r in manifest if r['id']==uid);v=next(r for r in manifest if r['id']==vid)
 im=Image.new('RGBA',(1024,1024),'#3C3944');im.alpha_composite(head);im.alpha_composite(Image.open(O/u['file']));im.alpha_composite(Image.open(O/v['file']));x=i%6*300;y=50+i//6*330;combos.paste(im.convert('RGB').resize((300,300)),(x,y));d.text((x+4,y+302),uid+' + '+vid,font=font,fill='white')
combos.save(O/'qa/combinations_12.jpg',quality=95)
checks=[]
for rec in manifest:
 p=O/rec['file'];im=Image.open(p);a=np.array(im);assert im.mode=='RGBA' and im.size==(1024,1024);assert re.fullmatch(r'[a-z]+_[1-9][0-9]*_[1-9][0-9]*',rec['id']);assert p.stem==rec['id'];assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256']
 if rec['type']=='background':assert a[:,:,3].min()==255
 else:assert a[0,0,3]==0 and a[0,-1,3]==0
 if rec['type'] in ['uniform','vest']:assert a[:620,:,3].max()==0
 basealpha=np.array(Image.open(O/'models'/(rec['id'].rsplit('_',1)[0])/'base.png'))[:,:,3];assert np.array_equal(a[:,:,3],basealpha)
checks=['120 distinct model IDs','416 distinct variant IDs','all filenames follow type_model_color','1024x1024 RGBA','alpha identical across each models color variants','no opaque top corners in overlay assets','background alpha fully opaque','torso equipment does not intersect head above y620','all SHA256 values match']
assert len(models)==120 and len(manifest)==416 and len({r['sha256'] for r in manifest})==416
report={'models':120,'variants':416,'checks_passed':checks,'visual_review':{'base_models':[m['id'] for m in models],'scope':'Six contact sheets composite each base model on supplied master commander; collars and balaclava_7/_8/_10 re-registered and re-inspected. Color contact sheets and 12 uniform/vest combinations provided. Not every possible combination has been visually inspected.'},'hidden_back_surfaces':'Removed where occluded behind the supplied head/neck; no invisible rear layers exported.','limitations':['Only supplied master head registration. Other faces not tested.','Face slots may conflict: do not stack two full-face or lower-face items.','High collars, thick scarves, full-face masks and headset parts may require compatibility exclusions.','Generated art aligned from atlases; source detail is lower than 1024x1024 output resolution.']}
(O/'qa/report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));(O/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
readme='''# eWarState — odela, panciri, maske i detalji

120 novih modela / 416 pojedinacnih varijanti:
- 30 uniformi i odela BEZ pancira: 146 varijanti.
- 30 zasebnih prsluka, pancira i nosaca opreme: 120 varijanti.
- 30 predmeta za lice: 6 polumaski, 4 semage/marame/sala, 10 balaklava i 10 respiratora/gas maski: 120 varijanti.
- 10 dodataka: naocare, povez, dve slusalice sa mikrofonima, cigara, cigareta, tri oznake cina.
- 5 boja za lice i 5 oziljaka.
- 10 pozadina.

## Upotreba

Svaki predmet je zaseban RGBA PNG 1024x1024 na x=0,y=0 bez skaliranja. Naziv je vrsta_model_boja. Boja 1 je originalna neutralna/prirodna varijanta. Ostale boje navedene su u manifest.json.

Redosled: pozadina → glava → uniforma → pancir → boje/oziljci → oprema za lice → naocare/slusalice → cigara/cigareta → oznake cina. Ako se koristi pokrivalo za glavu sa zadnjim delom, taj deo ide iza glave. Puna maska i balaklava zauzimaju isti slot; ne slagati ih automatski. Boje za lice staviti PRE maski i naocara. Oznake cina su zasebni prednji slojevi na predvidjenom mestu na grudima.

Odela i panciri nisu spojeni. Ne dodavati staru uniformu ispod nove pri proveri kroja, jer stari rukavi mogu proviriti. Panciri su demonstrirani preko originalne odvojene uniforme, a 12 kombinacija preko novih odela je u qa/combinations_12.jpg.

Zadnje povrsine kragni, traka i otvora koje su skrivene glavom uklonjene su iz prednjeg sloja. Nisu crtane niti izvezene nevidljive zadnje povrsine. Otvori za vrat/lice/ruke su alfa-providni. Neki prednji delovi (kragne, salovi) namerno prekrivaju donji vrat.

## Provera i ogranicenja

Svih 120 osnovnih modela prikazano je na prilozenom master komandiru. Ispravljene su zadnje ivice kragni i registracija tri balaklave. Pregledi varijanti predstavljaju stvarne alfa kompozite. QA pozadina na pregledima nije deo PNG opreme.

Nisu pregledane sve moguce kombinacije. Visoke kragne, krupne semage, teski oklopi, pune maske, slusalice i pokrivala za glavu mogu zahtevati zabrane kombinovanja ili dalju rucnu doradu. Nema univerzalne kompatibilnosti sa buducim licima.

Osnove su generisane na 12 koncept tabli, izdvojene, registrovane na master, a odabrane boje i kamuflaze primenjene uz sacuvane senke. Izvorna rezolucija po predmetu manja je od izvoza 1024x1024; povecanje ne predstavlja novi izvorni detalj. Pozadine su centralno kropovane na kvadrat, ne razvucene.

assets/: PNG fajlovi. models/: radne neutralne baze. sources/: izvorne table. previews/: svaki model i njegove boje. qa/: provere uklapanja, kombinacije i izvestaj. manifest.json: svi ID-ovi, slotovi, boje i provere. models.json: izvor i registracija.

Ponovno generisanje iz klona: Python + Pillow + NumPy + SciPy; python ewarstate/scripts/build_expansion.py pa python ewarstate/scripts/finalize_expansion.py.

ZIP paketi sadrze predmete i preglede, bez radnih baza i izvornih tabli, koje su dostupne u Git repozitorijumu.
'''
(O/'README.md').write_text(readme)
packs=[]
for group in dict.fromkeys(m['group'] for m in models):
 gm=[m for m in models if m['group']==group]
 for start in range(0,len(gm),10):
  batch=gm[start:start+10];ids={m['id'] for m in batch};entries=[r for r in manifest if r['id'].rsplit('_',1)[0] in ids];name=f"ewarstate_{group}_{start//10+1:02d}.zip";path=R/'downloads'/name
  with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
   z.writestr('README.md',readme);z.writestr('manifest.json',json.dumps(entries,indent=2,ensure_ascii=False));z.writestr('models.json',json.dumps(batch,indent=2,ensure_ascii=False))
   for rec in entries:z.write(O/rec['file'],rec['file'])
   for m in batch:z.write(O/'previews'/(m['id']+'.jpg'),'previews/'+m['id']+'.jpg')
   z.write(O/'qa'/(group+'_all.jpg'),'qa/'+group+'_all.jpg')
  with zipfile.ZipFile(path) as z:assert z.testzip() is None
  assert path.stat().st_size<95*1024*1024
  packs.append({'file':'../downloads/'+name,'models':[m['id'] for m in batch],'variants':len(entries),'bytes':path.stat().st_size})
(O/'packages.json').write_text(json.dumps(packs,indent=2))
index=['# Preuzimanje paketa','', '| Paket | Modela | Varijanti | MB |','|---|---:|---:|---:|']
for p in packs:index.append(f"| [{Path(p['file']).name}]({p['file']}) | {len(p['models'])} | {p['variants']} | {p['bytes']/1e6:.1f} |")
(O/'DOWNLOADS.md').write_text('\n'.join(index)+'\n\nNa GitHub stranici ZIP fajla kliknuti Download raw file.\n')
print(json.dumps({'models':120,'variants':416,'packages':len(packs),'total_zip_mb':round(sum(p['bytes'] for p in packs)/1e6,1),'validation':'passed'}))

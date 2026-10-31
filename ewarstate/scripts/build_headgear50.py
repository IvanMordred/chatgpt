from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
from scipy.ndimage import label,find_objects,binary_dilation
import json,zipfile,io,hashlib,csv
R=Path(__file__).resolve().parents[1];O=R/'headgear50'
COL={'gray':'#96999B','black':'#252B32','olive':'#697447','sand':'#C6AB7C','navy':'#2D4563','white':'#D6DEDE','orange':'#D77B32','yellow':'#D8B548','brown':'#78553D','maroon':'#8A354B','red':'#AB3A43','blue':'#396DA5','gold':'#B49A58','green':'#3A6244'}
TEX={'woodland':R/'camouflage/textures/sumska/sumska_01_organic_woodland.png','desert':R/'camouflage/textures/pustinjska/pustinjska_01_pixel_digital.png','urban':R/'camouflage/textures/urbana/urbana_02_fragment.png'}
names={
'caps':['Takticki kacket','Patrolna kapa kratkog vizira','Mrezasti kacket','Ravna terenska kapa','Komando kapa sa usima','Kacket sa radiovezom','Prosivena zimska kapa','Placenička osmopanelna kapa','Oklopljeni kacket','Oficirska kapa sa stitnikom'],
'infantry':['Celicni pesadijski slem','Duboki kevlar slem','Modularni mid-cut slem','Ventilisani bump slem','Slem sa velikom ceonom plocom','Pustinjski slem sa stitnikom vrata','Zimski slem sa usima','Slem sa lisnatom mrezom','Padobranski slem','Segmentirani PMC slem'],
'specialist':['Helikopterska kaciga','Pilotska kaciga sa podignutim vizirom','Spasilacka kaciga sa lampom','Industrijska zastitna kaciga','Kozna avijaticarska kaciga','Palubna komunikaciona kaciga','Interventna kaciga sa stitom','Zatvoreni breacher slem','Motociklisticka kaciga','Egzoskeletna PMC kaciga'],
'hats':['Beretka Vuk','Beretka Stit','Oficirska beretka Pero','Padobranska beretka Krila','Boonie sesir','Dzungla sesir','Ekspedicijski sesir','Rendzerski sesir','Pletena strazarska kapa','Subara sa spustenim usima'],
'hoods':['Izvidjacka kisna kapuljaca','Zimska krznena kapuljaca','Pustinjska marama za glavu','Lisnata ghillie kapuljaca','Platnena placenicka kapuljaca','Oklopljena kapuljaca','Pletena komando kapa sa vizirom','Docker vunena kapa','Avijaticarska subara sa vezanim usima','Spasilacka kapa sa lampom']}
models=[]
for group in names:
 src=Image.open(O/'sources'/f'{group}.png').convert('RGBA');arr=np.array(src)
 lab,n=label(arr[:,:,3]>190);cnt=np.bincount(lab.ravel());objs=find_objects(lab)
 ids=[int(i) for i in np.argsort(cnt[1:])[-10:]+1];assert len(ids)==10
 ids.sort(key=lambda i:((objs[i-1][0].start+objs[i-1][0].stop)/2))
 # Sort each visual row by x, allowing nonuniform row heights in generated sheets.
 ids=[k for j in range(0,10,2) for k in sorted(ids[j:j+2],key=lambda i:objs[i-1][1].start)]
 for j,k in enumerate(ids):
  sl=objs[k-1];clean=arr.copy();keep=binary_dilation(lab==k,iterations=1)
  clean[:,:,3]=np.where(keep,arr[:,:,3],0);clean[clean[:,:,3]<180,3]=0
  patch=Image.fromarray(clean).crop((sl[1].start,sl[0].start,sl[1].stop,sl[0].stop))
  if group=='caps':typ='cap';number=j+1
  elif group=='infantry':typ='helmet';number=j+2
  elif group=='specialist':typ='helmet';number=j+12
  elif group=='hats':typ='beret' if j<4 else 'hat';number=j+1 if j<4 else j-3
  else:typ='hood' if j<6 else 'cap' if j in [6,7,9] else 'hat';number=j+1 if j<6 else {6:11,7:12,8:7,9:13}[j]
  model_id=f'{typ}_{number}';w,h=patch.size
  aa=np.array(patch)[:,:,3];cx=w//2;line=(aa[:,max(0,cx-5):cx+6]>180).mean(axis=1)>.3
  runs=[];start=None
  for y,b in enumerate(list(line)+[False]):
   if b and start is None:start=y
   if not b and start is not None:
    if y-start>8:runs.append((start,y))
    start=None
  feature=runs[0][1] if runs else int(h*.7)
  width=430;top=70;target=312
  if group=='caps':width=440 if j in [4,6,8] else 490 if j==5 else 490 if j==9 else 450 if j==7 else 405
  if group=='hats':width=450 if j<4 else 700 if j in [4,5,6,7] else 408 if j==8 else 500
  if group=='hoods':width=720 if j<6 else 450 if j==8 else 420
  if group=='infantry':width=510 if j in [5,7] else 450
  if group=='specialist':width=480
  target=325 if group=='hats' and j in [4,5,6,7] else 330 if group=='caps' and j==9 else target
  height=round(h*(target-top)/max(1,feature))
  if group=='specialist' and j==0:height=440;top=60
  if group=='specialist' and j in [6,7,8,9]:height=585;top=65;width=460
  # Keep the short wool/cap silhouettes from becoming disproportionately tall.
  if typ in ['cap','hat','beret'] and not (group=='hats' and j==9):height=min(height,360)
  height=min(height,760)
  overlay=Image.new('RGBA',(1024,1024));overlay.paste(patch.resize((width,height),Image.Resampling.LANCZOS),((1024-width)//2,top))
  md=O/'models'/model_id;md.mkdir(parents=True,exist_ok=True);# Move the cap radio microphone from eye level to the mouth.
  if group=='caps' and j==5:
   b=np.array(overlay);piece=b.copy();sel=np.zeros((1024,1024),dtype=bool);sel[322:400,490:810]=True
   piece[~sel,3]=0;b[sel,3]=0;overlay=Image.fromarray(b)
   moved=Image.new('RGBA',(1024,1024));moved.paste(Image.fromarray(piece),(0,155));overlay.alpha_composite(moved)
   dr=ImageDraw.Draw(overlay);dr.line([(737,312),(747,345),(747,452),(729,487)],fill='#17191D',width=7);dr.line([(737,312),(747,345),(747,452),(729,487)],fill='#62676A',width=3)
  overlay.save(md/'base.png')
  rear=np.array(overlay);rear[:315,:,3]=0
  split=(group=='hoods' and j<6) or (group=='infantry' and j==5)
  if not split:rear[:,:,3]=0
  front=np.array(overlay)
  if split:front[315:,:,3]=0
  front[front[:,:,3]==0,:3]=0;rear[rear[:,:,3]==0,:3]=0
  Image.fromarray(front).save(md/'front.png');Image.fromarray(rear).save(md/'rear.png')
  # Fit and material masks are retained independently for handoff and iteration.
  b=np.array(overlay);lum=b[:,:,:3].mean(axis=2);sat=b[:,:,:3].max(axis=2).astype(float)-b[:,:,:3].min(axis=2)
  mask=np.clip((lum-75)/65,0,1)*np.clip((30-sat)/15,0,1)*(b[:,:,3]>0)
  if group=='hats' and j<4:
   # Badges are on the right side of the worn beret, not part of its fabric.
   mask[140:300,590:715]=0
  Image.fromarray((mask*255).astype('uint8')).save(md/'color_mask.png')
  if group in ['caps','infantry']:
   choices=['gray','black','olive','sand','navy','woodland'] if group=='caps' else ['gray','black','olive','sand','white','woodland','desert']
   if group=='caps' and j==9:choices=['gray','black','navy','olive']
  elif group=='specialist':
   choices=[['gray','black','navy','white'],['gray','black','navy','white'],['gray','orange','yellow','white'],['gray','orange','yellow','white'],['gray','brown','black','sand'],['gray','navy','orange','white'],['gray','black','navy'],['gray','black','olive','sand','urban'],['gray','black','red','blue'],['gray','black','red','gold']][j]
  elif group=='hats':choices=['gray','black','olive','maroon','navy'] if j<4 else ['gray','black','olive','sand','woodland','desert'] if j<8 else ['gray','black','olive','navy'] if j==8 else ['gray','black','brown','white']
  else:choices=[['gray','black','olive','sand','woodland'],['gray','white','black','navy'],['gray','sand','brown','desert'],['gray','olive','green','woodland'],['gray','black','brown','woodland'],['gray','black','olive','sand','urban'],['gray','black','olive','navy'],['gray','black','navy','brown'],['gray','black','brown','white'],['gray','orange','navy','yellow']][j]
  models.append({'id':model_id,'type':typ,'model':number,'name':names[group][j],'group':group,'choices':choices,'source_cell':j+1,'split_layers':split,'source_bbox':[sl[1].start,sl[0].start,sl[1].stop,sl[0].stop],'registration':{'width':width,'height':height,'x':(1024-width)//2,'y':top}})
(O/'models.json').write_text(json.dumps(models,indent=2,ensure_ascii=False))
assert len({m['id'] for m in models})==50
# The model source atlas is only a concept sheet; every output asset below is an individual registered PNG.
commander=Image.new('RGBA',(1024,1024))
with zipfile.ZipFile(next((R/'source-packs').glob('ewarstate_master_proba*.zip'))) as z:
 for name in ['01_glava.png','02_uniforma.png','03_pancir.png']:commander.alpha_composite(Image.open(io.BytesIO(z.read(name))).convert('RGBA'))
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14);title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',26)
(O/'previews').mkdir(exist_ok=True)
manifest=[];model_sheet=Image.new('RGB',(2000,5*250+55),'#151D24');ImageDraw.Draw(model_sheet).text((10,10),'eWarState / 50 NOVIH MODELA',font=title,fill='#EADAB8')
for mi,model in enumerate(models):
 md=O/'models'/model['id'];base=Image.open(md/'base.png');b=np.array(base);mask=np.array(Image.open(md/'color_mask.png'),dtype=float)/255
 lum=np.mean(b[:,:,:3],axis=2)[...,None];shade=np.clip(lum/160,.15,1.5)
 variants_sheet=Image.new('RGB',(240*len(model['choices']),280),'#151D24')
 for ci,choice in enumerate(model['choices'],1):
  if choice=='gray':out=b.copy()
  else:
   if choice in TEX:
    paint=Image.new('RGB',(1024,1024));paint.paste(Image.open(TEX[choice]).convert('RGB').resize((768,768),Image.Resampling.NEAREST),(128,0));rgb=np.array(paint,dtype=float)
   else:rgb=np.full((1024,1024,3),tuple(bytes.fromhex(COL[choice][1:])),dtype=float)
   mixed=np.clip(rgb*shade,0,255);out=b.copy();out[:,:,:3]=np.clip(b[:,:,:3]*(1-mask[...,None])+mixed*mask[...,None],0,255).astype('uint8')
  out[out[:,:,3]==0,:3]=0;im=Image.fromarray(out,'RGBA');id=f"{model['id']}_{ci}";dest=O/'assets'/model['id'];dest.mkdir(parents=True,exist_ok=True);p=dest/(id+'.png');front=out.copy();rear=out.copy()
  if model['split_layers']:
   front[315:,:,3]=0;rear[:315,:,3]=0
  else:rear[:,:,3]=0
  front[front[:,:,3]==0,:3]=0;rear[rear[:,:,3]==0,:3]=0
  im=Image.fromarray(front,'RGBA');im.save(p)
  rear_image=Image.fromarray(rear,'RGBA');rear_path=None
  if model['split_layers']:
   rear_dest=O/'rear_assets'/model['id'];rear_dest.mkdir(parents=True,exist_ok=True);rear_path=rear_dest/(id+'.png');rear_image.save(rear_path)
  prev=Image.new('RGBA',(1024,1024),'#252E32');prev.alpha_composite(rear_image);prev.alpha_composite(commander);prev.alpha_composite(im)
  x=(ci-1)*240;variants_sheet.paste(prev.convert('RGB').resize((240,240),Image.Resampling.LANCZOS),(x,0));ImageDraw.Draw(variants_sheet).text((x+5,243),f'{id} / {choice}',font=font,fill='#EADAB8')
  if ci==min(3,len(model['choices'])):
   x=(mi%10)*200;y=55+(mi//10)*250
   # Grid is 10 columns x 5 rows, full portrait plus equipment name.
   model_sheet.paste(prev.convert('RGB').resize((200,200),Image.Resampling.LANCZOS),(x,y));ImageDraw.Draw(model_sheet).text((x+3,y+203),model['id'],font=font,fill='#EADAB8');ImageDraw.Draw(model_sheet).text((x+3,y+222),model['name'][:24],font=font,fill='#EADAB8')
  manifest.append({'id':id,'type':model['type'],'model_number':model['model'],'color_number':ci,'color':choice,'hex':COL.get(choice),'texture':str(TEX[choice].relative_to(R)) if choice in TEX else None,'file':str(p.relative_to(O)),'rear_file':str(rear_path.relative_to(O)) if rear_path else None,'layer_order':['background','rear_file','head','uniform','vest','file'],'canvas':[1024,1024],'position':[0,0],'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 variants_sheet.save(O/'previews'/(model['id']+'.jpg'),quality=92)
model_sheet.save(O/'previews/all_50_models.jpg',quality=95)
(O/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
files=list((O/'assets').rglob('*.png'));assert len(files)==len(manifest)
for model in models:
 alpha=np.array(Image.open(O/'models'/model['id']/'front.png'))[:,:,3]
 for rec in [m for m in manifest if m['model_number']==model['model'] and m['type']==model['type']]:
  im=Image.open(O/rec['file']);assert im.size==(1024,1024) and im.mode=='RGBA';assert np.array_equal(np.array(im)[:,:,3],alpha)
assert len({m['sha256'] for m in manifest})==len(manifest)
(O/'README.md').write_text(f'''# eWarState: 50 novih modela pokrivala za glavu

50 razlicitih osnovnih modela i {len(manifest)} transparentnih PNG varijanti. Platno 1024x1024, x=0,y=0 bez skaliranja na prilozenoj osnovnoj glavi. Za modele sa rear_file OBAVEZAN redosled: pozadina, rear_file (iza glave), glava, uniforma, pancir, file (prednji sloj). assets/ sadrzi prednje slojeve, rear_assets/ zadnje slojeve. Ime oba sloja je isti ID u razlicitim direktorijumima. Ne koristiti base.png kao gotov prednji sloj.

Oprema je izdvojena iz pet generisanih koncept atlasa i registrovana po ceonoj ivici. Pregledi su stvarni alfa kompoziti sa korisnickim master slojevima.

Modeli: cap_1–cap_13, helmet_2–helmet_21, beret_1–beret_4, hat_1–hat_7, hood_1–hood_6. Raniji helmet_1 nije menjan.

Boje su birane po nameni: kamuflaze za terenske modele, obicne boje za beretke i vecinu specijalistickih kaciga, signalna narandzasta/zuta za spasioce. Baze i maske za bojenje zadrzane su u models/ u Git repozitorijumu (radni modeli nisu ukljuceni u ZIP sa gotovim predmetima). Za kapuljace i pustinjski vratni zastitnik zadnji delovi ispod linije obrva razdvojeni su iza glave. Tamni detalji i hromatski detalji (npr. bronzane oznake i svetla) uglavnom su izuzeti iz maske za bojenje; maske su pocetna priprema za dalju rucnu doradu, ne zasebni fizicki materijali.

Ne kombinovati sa drugim kapama/slemovima. Sakriti kosu koja izlazi kroz pokrivalo. Kompatibilnost sa svakom postojecom maskom, slusalicama ili bradom nije garantovana. Zatvorene kacige namerno prekrivaju lice; providni vizir i tesne kapuljace mogu zahtevati dodatnu rucnu doradu. Nema univerzalne tvrdnje o uklapanju.

assets/: zasebni PNG predmeti tip_model_boja. manifest.json: svi ID-ovi, boje i izvori tekstura. models.json: dizajni i precizni parametri registracije. previews/: 50 pregleda varijanti i zajednicka tabla. sources/: originalne koncept table, nisu slojevi za direktno nosenje.

Reprodukcija: python ewarstate/scripts/build_headgear50.py (Pillow, NumPy, SciPy). Nazivi boja su stabilni po modelu.
''')
with zipfile.ZipFile(R/'downloads/ewarstate_50_novih_modela.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(O.rglob('*')):
  if p.is_file() and 'sources' not in p.parts and 'models' not in p.parts:z.write(p,p.relative_to(O))
 z.write(R/'scripts/build_headgear50.py','build_headgear50.py')
print(json.dumps({'models':50,'variants':len(manifest),'zip_mb':round((R/'downloads/ewarstate_50_novih_modela.zip').stat().st_size/1e6,2)}))

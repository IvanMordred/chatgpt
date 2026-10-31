from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np
from scipy.ndimage import label,find_objects,binary_dilation,binary_fill_holes
import json,zipfile,io,hashlib,re
R=Path(__file__).resolve().parents[1];O=R/'expansion';SRC=O/'sources'
COL={'black':'#252B32','olive':'#697447','sand':'#C6AB7C','navy':'#2D4563','brown':'#78553D','white':'#D6DEDE','red':'#A53A43','orange':'#D27B36'}
TEX=R/'camouflage/textures/sumska/sumska_01_organic_woodland.png'
with zipfile.ZipFile(next((R/'source-packs').glob('ewarstate_master_proba*.zip'))) as z:
 def get(n):return Image.open(io.BytesIO(z.read(n))).convert('RGBA')
 head=get('01_glava.png');olduniform=get('02_uniforma.png');oldvest=get('03_pancir.png')
head_a=np.array(head)[:,:,3]
def body_base():
 b=Image.new('RGBA',(1024,1024));b.alpha_composite(head);b.alpha_composite(olduniform);return b
base=body_base();base_armor=base.copy();base_armor.alpha_composite(oldvest)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15);ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',26)
UNAMES=['Terenska kosulja','Borbena majica','Combat zip majica','Vojna polo majica','Dzungla kosulja','Pustinjska utility kosulja','Raglan borbena majica','Zimska combat majica','Mrezasta sportska majica','Placenička radna kosulja','M65 jakna','Softshell jakna','Zimska parka','Kisna jakna','Kozna jakna','Ekspedicijska jakna','Komando dzemper','Prosivena jakna','Pilotska bomber jakna','Mornarski kaput','Oficirska bluza','Oficirsko odelo sa kravatom','Arkticki flis','Tehnicki zimski sloj','Tropska kosulja','Pustinjska lanena kosulja','Spasilacka radna kosulja','Mehanicarski kombinezon','Duks sa spustenom kapuljacom','Henley dzemper']
VNAMES=['Meki pancir','MOLLE plocasti nosac','Laki chest rig','Jurisni pancir','Mikro izvidjacki rig','Prikriveni prsluk','Fragmentacioni pancir','Crossdraw prsluk','Minimalni uprtac','Teski pesadijski oklop','Medicinski prsluk','Plutajuci pomorski prsluk','Spasilacki uprtac','Inzenjerijski prsluk','Radio operater','Dron operater','Breacher prsluk','Kozni ekspedicijski uprtac','Planinarski uprtac','Interventni oklop','Keramicki laki oklop','Izvidjacki segmentirani oklop','Teski breacher oklop','EOD oklop','Karbonski nosac','Keramicki egzoskelet','Oficirski premium oklop','Raider oklop','Arkticki pancir','Modularni oklopljeni uprtac']
MODELS=[]
def patches(tag,soft=False):
 im=Image.open(SRC/(tag+'.png')).convert('RGBA');a=np.array(im);H,W=a.shape[:2]
 if soft:
  ans=[]
  for j in range(10):
   x=j%2*W//2;y=j//2*H//5;crop=im.crop((x+3,y+3,(j%2+1)*W//2-3,(j//2+1)*H//5-3));b=np.array(crop);threshold=145 if tag=='face_a' else 180
   m=b[:,:,3]>threshold
   if tag=='face_a':
    # Remove diffuse generated color halos while retaining marks and soft edges.
    m=binary_dilation(m,iterations=1);b[:,:,3]=np.where(m,b[:,:,3],0)
   else:b[:,:,3]=np.where(m,b[:,:,3],0)
   ys,xs=np.where(m);assert len(xs), (tag,j)
   ans.append(Image.fromarray(b).crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1)))
  return ans
 a[:,W//2-1:W//2+1,3]=0;lab,n=label(a[:,:,3]>180);cnt=np.bincount(lab.ravel());obj=find_objects(lab);ids=np.argsort(cnt[1:])[-10:]+1
 ids=sorted(ids,key=lambda i:(obj[i-1][0].start+obj[i-1][0].stop)/2)
 ids=[k for j in range(0,10,2) for k in sorted(ids[j:j+2],key=lambda i:obj[i-1][1].start)]
 ans=[]
 for k in ids:
  sl=obj[k-1];m=binary_dilation(lab==k,iterations=1);b=a.copy();b[:,:,3]=np.where(m,a[:,:,3],0);b[b[:,:,3]<160,3]=0
  ans.append(Image.fromarray(b).crop((sl[1].start,sl[0].start,sl[1].stop,sl[0].stop)))
 return ans
def register(patch,box):
 x,y,w,h=map(int,box);im=Image.new('RGBA',(1024,1024));im.paste(patch.resize((w,h),Image.Resampling.LANCZOS),(x,y));return im

def add(typ,num,name,group,patch,box,choices,slot,source):
 im=register(patch,box)
 # Invisible back surfaces of torso collars/straps are removed, never drawn over the neck.
 if typ in ['uniform','vest']:
  a=np.array(im);yy,xx=np.indices((1024,1024));hidden=(head_a>0)&(yy<715)&(xx>335)&(xx<689)
  a[hidden,3]=0;im=Image.fromarray(a)
 if typ in ['facepaint','scar']:
  a=np.array(im);a[:,:,3]=np.minimum(a[:,:,3],head_a)
  if typ=='scar':a[:,:,3]=(a[:,:,3]*.68).astype('uint8')
  im=Image.fromarray(a)
 id=f'{typ}_{num}';d=O/'models'/id;d.mkdir(parents=True,exist_ok=True);im.save(d/'base.png')
 MODELS.append({'id':id,'type':typ,'number':num,'name':name,'group':group,'choices':choices,'slot':slot,'registration':list(box),'source':source})
for letter,offset in [('a',0),('b',10),('c',20)]:
 tag='uniform_'+letter
 for j,patch in enumerate(patches(tag)):
  num=offset+j+1;choices=['base','black','olive','sand','woodland'] if num not in [15,20,21,22] else ['base','black','navy','brown']
  add('uniform',num,UNAMES[num-1],'uniforms',patch,(-42,620,1108,485),choices,'uniform',tag+':'+str(j+1))
 tag='vest_'+letter
 for j,patch in enumerate(patches(tag)):
  num=offset+j+1;width=1050 if num in [10,20,23,24,26,27,29] else 830
  add('vest',num,VNAMES[num-1],'vests',patch,((1024-width)//2,665,width,465),['base','black','olive','sand'],'vest',tag+':'+str(j+1))
for j,patch in enumerate(patches('mask_a')):
 typ='mask' if j<6 else 'scarf';num=j+1 if j<6 else j-5
 add(typ,num,['Platnena polumaska','Mrezasta polumaska','Plisirana maska','Segmentirani stitnik vilice','Kozna polumaska','Lobanja oklopna polumaska','Semaga','Podignuti grejac vrata','Vezana marama','Zimski sal'][j],'facewear',patch,(302 if j<6 else 257,455,420 if j<6 else 510,205 if j<6 else 350),['base','black','olive','sand'],'lower_face','mask_a:'+str(j+1))
for j,patch in enumerate(patches('balaclava_a')):
 a=np.array(patch);solid=a[:,:,3]>180;holes=binary_fill_holes(solid)&~solid;ll,nn=label(holes);cc=np.bincount(ll.ravel());ss=find_objects(ll)
 hs=[s for i,s in enumerate(ss,1) if cc[i]>60];hs.sort(key=lambda s:s[0].start)
 if j==6:eyef=(hs[0][0].start if hs else patch.height*.25)+25
 else:
  eyeholes=[s for s in hs if s[0].start<patch.height*.6];eyef=np.mean([(s[0].start+s[0].stop)/2 for s in eyeholes[:2]]) if eyeholes else patch.height*.4
 sy=2.6 if j==9 else 2.1;height=round(patch.height*sy);top=round(360-eyef*sy)
 if j==6:height=700;top=85
 width=550 if j==7 else 520 if j==9 else 450
 left=round(512-((hs[0][1].start+hs[0][1].stop)/2)/patch.width*width) if j==7 and hs else (1024-width)//2
 add('balaclava',j+1,['Tropola fantomka','Jedan ocni prorez','Dva ocna otvora','Flis fantomka','Mrezasta balaklava','Ojacana balaklava','Otvoreno lice','Pustinjski omot','Neopren balaklava','Teska zimska balaklava'][j],'facewear',patch,(left,top,width,height),['base','black','olive','sand'],'full_face','balaclava_a:'+str(j+1))
for j,patch in enumerate(patches('gasmask_a')):
 box=(277,435,470,225) if j<4 else (277,190,470,475)
 add('gasmask',j+1,['Centralni filter','Dva bocna filtera','Industrijski respirator','Zimski respirator','Okrugla stakla','Panoramski gas maska','Ugaoni vojni respirator','Asimetricni respirator','Vatrogasni respirator','Oklopljeni respirator'][j],'facewear',patch,box,['base','black','olive','sand'],'lower_face' if j<4 else 'full_face','gasmask_a:'+str(j+1))
access=[('glasses',1,'Zlatne avijatorske naocare',(332,309,360,125),'eyes'),('glasses',2,'Balisticke naocare',(327,314,370,115),'eyes'),('eyepatch',1,'Povez za oko',(302,245,420,160),'eyes'),('headset',1,'Dvousne slusalice sa mikrofonom',(252,95,520,465),'ears'),('headset',2,'Jednousna radio-veza',(277,90,470,470),'ears'),('cigar',1,'Cigara',(568,525,112,64),'mouth'),('cigarette',1,'Cigareta',(570,528,102,53),'mouth'),('rank',1,'Dva sevrona',(724,805,88,72),'chest_badge'),('rank',2,'Dvostruka srebrna oznaka',(744,805,64,70),'chest_badge'),('rank',3,'Tri komandirske zvezde',(710,808,112,52),'chest_badge')]
for j,(typ,num,name,box,slot) in enumerate(access):add(typ,num,name,'accessories',patches('accessories_a',True)[j],box,['base'],slot,'accessories_a:'+str(j+1))
faceboxes=[(365,414,294,66),(366,330,292,205),(368,385,290,175),(355,405,314,150),(347,338,330,238),(592,315,30,105),(597,415,70,95),(585,415,90,105),(395,327,65,35),(592,446,78,45)]
for j,patch in enumerate(patches('face_a',True)):
 typ='facepaint' if j<5 else 'scar';num=j+1 if j<5 else j-4
 add(typ,num,'Boja za lice '+str(num) if j<5 else 'Zarastao oziljak '+str(num),'face_details',patch,faceboxes[j],['base'],'skin','face_a:'+str(j+1))
bg=Image.open(SRC/'backgrounds_a.png').convert('RGB');bw,bh=bg.size
for j in range(10):
 tile=bg.crop((j%2*bw//2,j//2*bh//5,(j%2+1)*bw//2,(j//2+1)*bh//5))
 # Center crop square avoids stretching the painted landscape.
 side=min(tile.size);x=(tile.width-side)//2;y=(tile.height-side)//2;tile=tile.crop((x,y,x+side,y+side)).convert('RGBA')
 add('background',j+1,['Vojno platno','Bunker','Cetinarska suma','Pustinja','Kisni industrijski grad','Tropska dzungla','Arktik','Pomorski hangar','Zlatna geometrija','Krvavi mesec'][j],'backgrounds',tile,(0,0,1024,1024),['base'],'background','backgrounds_a:'+str(j+1))
assert len(MODELS)==120 and len({m['id'] for m in MODELS})==120
(O/'models.json').write_text(json.dumps(MODELS,indent=2,ensure_ascii=False))
manifest=[];(O/'previews').mkdir(exist_ok=True);(O/'qa').mkdir(exist_ok=True)
sheets={g:Image.new('RGB',(1800,60+((sum(m['group']==g for m in MODELS)+5)//6)*330),'#182028') for g in ['uniforms','vests','facewear','accessories','face_details','backgrounds']};counters={g:0 for g in sheets}
for g,sh in sheets.items():ImageDraw.Draw(sh).text((15,13),'eWarState / '+g.upper(),font=ft,fill='#E8D9B8')
for model in MODELS:
 b=np.array(Image.open(O/'models'/model['id']/'base.png').convert('RGBA'));lum=b[:,:,:3].mean(2)[...,None];sat=b[:,:,:3].max(2).astype(float)-b[:,:,:3].min(2)
 # Color every neutral material pixel, including narrow seams and shaded panels.
 # Keep already colored material (lights, bronze, gold, leather) unchanged.
 mask=np.clip((35-sat)/20,0,1)*(b[:,:,3]>0)
 if model['id']=='vest_11':
  yy,xx=np.indices((1024,1024));mask[(lum[:,:,0]>210)&(xx>400)&(xx<625)&(yy>800)&(yy<955)]=0
 shade=np.clip(lum/160,.02,1.55);sheet=Image.new('RGB',(250*len(model['choices']),280),'#182028')
 for ci,choice in enumerate(model['choices'],1):
  out=b.copy()
  if choice!='base':
   rgb=np.array(Image.open(TEX).convert('RGB'),dtype=float) if choice=='woodland' else np.full((1024,1024,3),tuple(bytes.fromhex(COL[choice][1:])),dtype=float)
   colored=np.clip(rgb*shade,0,255);out[:,:,:3]=np.clip(b[:,:,:3]*(1-mask[...,None])+colored*mask[...,None],0,255).astype('uint8')
  out[out[:,:,3]==0,:3]=0;im=Image.fromarray(out,'RGBA');id=f"{model['id']}_{ci}";d=O/'assets'/model['type'];d.mkdir(parents=True,exist_ok=True);p=d/(id+'.png');im.save(p)
  preview=Image.new('RGBA',(1024,1024),'#29383D')
  if model['type']=='background':preview.alpha_composite(im);preview.alpha_composite(base_armor)
  elif model['type']=='uniform':preview.alpha_composite(head);preview.alpha_composite(im)
  elif model['type']=='vest':preview.alpha_composite(base);preview.alpha_composite(im)
  else:preview.alpha_composite(base_armor);preview.alpha_composite(im)
  x=(ci-1)*250;sheet.paste(preview.convert('RGB').resize((250,250),Image.Resampling.LANCZOS),(x,0));ImageDraw.Draw(sheet).text((x+4,254),id+' / '+choice,font=font,fill='#E8D9B8')
  if ci==min(3,len(model['choices'])):
   g=model['group'];n=counters[g];x=n%6*300;y=60+n//6*330;sheets[g].paste(preview.convert('RGB').resize((300,300),Image.Resampling.LANCZOS),(x,y));ImageDraw.Draw(sheets[g]).text((x+5,y+302),model['id']+' / '+model['name'][:21],font=font,fill='#E8D9B8');counters[g]+=1
  manifest.append({'id':id,'type':model['type'],'model_number':model['number'],'color_number':ci,'color':choice,'group':model['group'],'slot':model['slot'],'file':str(p.relative_to(O)),'canvas':[1024,1024],'position':[0,0],'layer':'background' if model['type']=='background' else 'front','sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 sheet.save(O/'previews'/(model['id']+'.jpg'),quality=92)
for g,sh in sheets.items():sh.save(O/'qa'/(g+'_all.jpg'),quality=95)
(O/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
for rec in manifest:
 im=Image.open(O/rec['file']);assert im.mode=='RGBA' and im.size==(1024,1024);assert re.fullmatch('[a-z]+_[1-9][0-9]*_[1-9][0-9]*',rec['id'])
 if rec['type']!='background':assert im.getpixel((0,0))[3]==0
assert len({m['sha256'] for m in manifest})==len(manifest)
print(json.dumps({'models':120,'variants':len(manifest),'groups':{g:sum(m['group']==g for m in MODELS) for g in sheets},'status':'generated_for_visual_review'}))

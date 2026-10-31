"""Rigid registration of independently generated headgear. No anisotropic resize.
Reject geometry that cannot contain the master scalp without exceeding plausible size.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,find_objects,binary_closing,binary_fill_holes
import numpy as np,json,zipfile,io,hashlib
V=Path(__file__).resolve().parent;R=V.parent
jobs=json.loads((V/'jobs.json').read_text());old={m['id']:m for m in json.loads((R/'headgear50/models.json').read_text())};ids=set(old)|{'helmet_1'}
regs=json.loads((V/'registration.json').read_text()) if (V/'registration.json').exists() else {}
source_reviews=json.loads((V/'source_reviews.json').read_text()) if (V/'source_reviews.json').exists() else {}
master_alpha=np.array(Image.open(V/'reference/head.png'))[:,:,3]>128
yy,xx=np.indices((1024,1024))
scalp=[(512,126),(445,155),(579,155),(390,235),(634,235)]
for j in jobs:
 id=j['id'];p=V/'sources'/(id+'.png')
 if id not in ids or not p.exists():continue
 src=Image.open(p).convert('RGBA');a=np.array(src)
 rr,gg,bb=[a[:,:,i].astype(float) for i in range(3)]
 skin=(rr>110)&(rr>gg+18)&(gg>bb+16)&(rr>bb*1.25)&(a[:,:,3]>128)
 sr=source_reviews.get(id,{})
 reviewed=sr.get('state')=='no_person_confirmed' and sr.get('source_sha256')==hashlib.sha256(p.read_bytes()).hexdigest()
 if skin.sum()>4500 and not reviewed:
  j['status']='requires_source_edit_person_in_layer'
  stale=V/'assets'/(id+'_1.png')
  if stale.exists():stale.unlink()
  continue
 ll,n=label(a[:,:,3]>128);counts=np.bincount(ll.ravel());bounds=find_objects(ll);valid=[i for i in range(1,n+1) if counts[i]>20]
 if not valid:j['status']='requires_regeneration_empty_alpha';continue
 x0=min(bounds[i-1][1].start for i in valid);x1=max(bounds[i-1][1].stop for i in valid);y0=min(bounds[i-1][0].start for i in valid);y1=max(bounds[i-1][0].stop for i in valid)
 patch=src.crop((max(0,x0-2),max(0,y0-2),min(src.width,x1+2),min(src.height,y1+2)));q=np.array(patch);h,w=q.shape[:2];cx=w//2
 line=(q[:,max(0,cx-5):cx+6,3]>128).mean(1)>.35;line=binary_closing(line,iterations=2);events=np.where(np.diff(np.r_[False,line,False].astype(int))!=0)[0];runs=list(zip(events[::2],events[1::2]));candidates=[(s,e) for s,e in runs if s<h*.4 and e-s>max(5,h*.05)]
 if not candidates:j['status']='requires_regeneration_no_front_rim';continue
 feature=max(candidates,key=lambda r:r[1]-r[0])[1];target=315
 if id in ['helmet_19','helmet_20','helmet_21','helmet_18']:feature=h;target=655
 elif id=='helmet_12':target=425
 typ=j['type'];width=480 if typ=='helmet' else 470 if typ=='beret' else 600 if typ=='hood' else 420
 if id=='hood_2':width=900
 if typ=='hat':width=640 if int(id.split('_')[1])<=4 else 440 if id=='hat_5' else 500
 if id in ['cap_7','cap_5','cap_11']:width=470
 limit=580 if typ in ['helmet','cap','beret'] else 820 if typ=='hood' else 820
 if id=='hood_2':limit=930
 attempts=[];accepted=False
 while width<=limit:
  scale=width/w;height=round(h*scale);top=round(target-feature*scale);left=(1024-round(width))//2
  overlay=Image.new('RGBA',(1024,1024));overlay.alpha_composite(patch.resize((round(width),height),Image.Resampling.LANCZOS),(left,top));aa=np.array(overlay)
  envelope=binary_fill_holes(aa[:,:,3]>128)
  missing=[(x,y) for x,y in scalp if not envelope[y,x]]
  scalp_region=master_alpha&(yy<(200 if typ=='hood' else 230))
  uncovered=int((scalp_region&~envelope).sum())
  eyes_clear=not any(aa[y,x,3]>100 for x,y in [(434,360),(590,360)]) if typ=='hood' else True
  attempts.append({'width':round(width),'top':top,'missing_scalp_points':missing,'uncovered_scalp_pixels':uncovered,'eyes_clear':eyes_clear})
  if not missing and uncovered<25 and eyes_clear and top>=3:
   accepted=True;break
  width*=1.025
 if not accepted:
  j['status']='requires_regeneration_anatomy';regs[id]={'review':'failed_geometry','attempts':attempts,'source_bbox':[x0,y0,x1,y1]}
  stale=V/'assets'/(id+'_1.png')
  if stale.exists():stale.unlink()
  continue
 overlay.save(V/'assets'/(id+'_1.png'));j['status']='registered_draft';regs[id]={'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'method':'uniform_object_scale_then_translation','source_bbox':[x0,y0,x1,y1],'scale':scale,'translation':[left,top],'canvas':[1024,1024],'review':'pending_visual','checks':attempts[-1]}
(V/'registration.json').write_text(json.dumps(regs,indent=2));(V/'jobs.json').write_text(json.dumps(jobs,ensure_ascii=False,indent=2))
with zipfile.ZipFile(next((R/'source-packs').glob('ewarstate_master_proba*.zip'))) as z:head=Image.open(io.BytesIO(z.read('01_glava.png'))).convert('RGBA')
selected=[j for j in jobs if j['id'] in ids and (V/'assets'/(j['id']+'_1.png')).exists()]
if selected:
 sh=Image.new('RGB',(1600,((len(selected)+3)//4)*430),'#293239');f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
 for i,j in enumerate(selected):
  im=Image.new('RGBA',(1024,1024),'#293239');im.alpha_composite(head);im.alpha_composite(Image.open(V/'assets'/(j['id']+'_1.png')));x=i%4*400;y=i//4*430;sh.paste(im.convert('RGB').resize((400,400)),(x,y));ImageDraw.Draw(sh).text((x+8,y+405),j['id']+' / DRAFT',font=f,fill='white')
 sh.save(V/'qa/headgear_drafts.jpg',quality=95)
print('Headgear registration drafts:',len(selected))

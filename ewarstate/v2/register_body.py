import hashlib
"""Normalize individual square body layers with uniform canvas scale + translation only.
Never stretch a cropped torso, remove neck rectangles, or synthesize hidden surfaces.
Every exported draft still requires visual inspection on the master.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,find_objects
import numpy as np,json,io,zipfile
V=Path(__file__).resolve().parent;R=V.parent
jobs=json.loads((V/'jobs.json').read_text());registrations=json.loads((V/'registration.json').read_text()) if (V/'registration.json').exists() else {}
for j in jobs:
 if j['type'] not in ['uniform','vest'] or not (V/'sources'/(j['id']+'.png')).exists():continue
 src=Image.open(V/'sources'/(j['id']+'.png')).convert('RGBA')
 if src.width!=src.height:
  j['status']='requires_review_non_square_canvas';continue
 im=src.resize((1024,1024),Image.Resampling.LANCZOS);a=np.array(im);ll,n=label(a[:,:,3]>128);counts=np.bincount(ll.ravel());counts[0]=0;k=int(counts.argmax());sl=find_objects(ll)[k-1]
 target=605 if j['type']=='uniform' else 665;anchor=sl[0].start
 if j['id']=='vest_15':
  # Register shoulder straps, not the thin radio antenna projecting above them.
  row=(a[:,:,3]>128).sum(1);anchor=int(np.where(row>90)[0][0])-8
 dy=target-anchor
 out=Image.new('RGBA',(1024,1024));out.paste(im,(0,dy));out.save(V/'assets'/(j['id']+'_1.png'))
 aa=np.array(out);line=(aa[500:1000,507:518,3]>80).mean(1)>.5;transitions=np.where(np.diff(np.r_[False,line,False].astype(int))!=0)[0];runs=list(zip(transitions[::2]+500,transitions[1::2]+500));runs=[(int(x),int(y)) for x,y in runs if y-x>3]
 registrations[j['id']]={'method':'uniform_whole_canvas_scale_then_translation','source_sha256':hashlib.sha256((V/'sources'/(j['id']+'.png')).read_bytes()).hexdigest(),'source_size':list(src.size),'canvas':[1024,1024],'translation':[0,int(dy)],'centerline_alpha_runs':runs,'review':'pending_visual'}
 if len(runs)>1:j['status']='requires_review_possible_rear_band'
 else:j['status']='registered_draft'
(V/'registration.json').write_text(json.dumps(registrations,indent=2));(V/'jobs.json').write_text(json.dumps(jobs,indent=2,ensure_ascii=False))
with zipfile.ZipFile(next((R/'source-packs').glob('ewarstate_master_proba*.zip'))) as z:head=Image.open(io.BytesIO(z.read('01_glava.png'))).convert('RGBA')
selected=[j for j in jobs if j['type']=='uniform' and (V/'assets'/(j['id']+'_1.png')).exists()];sh=Image.new('RGB',(1600,((len(selected)+3)//4)*430),'#293239');f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
for i,j in enumerate(selected):
 im=Image.new('RGBA',(1024,1024),'#293239');im.alpha_composite(head);im.alpha_composite(Image.open(V/'assets'/(j['id']+'_1.png')));x=i%4*400;y=i//4*430;sh.paste(im.convert('RGB').resize((400,400)),(x,y));ImageDraw.Draw(sh).text((x+8,y+405),j['id']+' / DRAFT',font=f,fill='white')
sh.save(V/'qa/uniform_drafts.jpg',quality=95)
print('Registered body drafts:',len(registrations),'Uniform previews:',len(selected))

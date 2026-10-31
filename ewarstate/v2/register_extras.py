import hashlib
"""Register individually reviewed accessories and isolated skin decals.
The entire cup/microphone silhouette uses a rigid transform. No clipping boxes.
"""
from pathlib import Path
from PIL import Image
from scipy.ndimage import label,find_objects
import numpy as np,json
V=Path(__file__).resolve().parent;jobs=json.loads((V/'jobs.json').read_text());regs=json.loads((V/'registration.json').read_text())
head_alpha=np.array(Image.open(V/'reference/head.png'))[:,:,3]
spec={
 'glasses_1':(350,.5,.53,512,360),'glasses_2':(355,.5,.5,512,360),
 'eyepatch_1':(300,.79,.72,590,360),'headset_2':(300,.78,.40,730,425),
 'cigar_1':(110,0,0,570,525),'cigarette_1':(100,0,0,570,530),
 'rank_1':(80,.5,.5,770,850),'rank_2':(65,.5,.5,770,850),'rank_3':(110,.5,.5,770,850),
 'facepaint_1':(285,.5,0,512,405),'facepaint_2':(290,.5,0,512,390),
 'facepaint_3':(290,.5,0,512,375),'facepaint_4':(30,.5,.5,405,445),
 'scar_1':(20,.5,.5,610,405),'scar_2':(48,.5,.5,620,465),
 'scar_3':(45,.5,.5,410,465),'scar_4':(10,.5,.5,610,330),'scar_5':(40,.5,.5,615,510),
}
for j in jobs:
 id=j['id'];typ=j['type'];p=V/'sources'/(id+'.png')
 if id not in spec and id!='facepaint_5':continue
 if not p.exists():continue
 if id in ['cigar_1','rank_1','rank_2','rank_3'] and not (V/'rejected'/(id+'_unwanted_gear_attempt.png')).exists():continue
 src=Image.open(p).convert('RGBA');a=np.array(src);ll,n=label(a[:,:,3]>30);cnt=np.bincount(ll.ravel());ss=find_objects(ll);ids=[i for i in range(1,n+1) if cnt[i]>15]
 x0=max(0,min(ss[i-1][1].start for i in ids)-2);x1=min(src.width,max(ss[i-1][1].stop for i in ids)+2);y0=max(0,min(ss[i-1][0].start for i in ids)-2);y1=min(src.height,max(ss[i-1][0].stop for i in ids)+2)
 patch=src.crop((x0,y0,x1,y1));w,h=patch.size
 if id=='facepaint_5':
  # Eye centers observed in the native isolated paint source, not invented
  # from a universal rectangle. Uniform scale fixes their spacing to156px.
  scale=156/450;feature=[625-x0,500-y0];target=[512,360];width=w*scale
 else:
  width,fx,fy,tx,ty=spec[id];scale=width/w;feature=[fx*w,fy*h];target=[tx,ty]
 left=round(target[0]-feature[0]*scale);top=round(target[1]-feature[1]*scale)
 out=Image.new('RGBA',(1024,1024));out.alpha_composite(patch.resize((round(width),round(h*scale)),Image.Resampling.LANCZOS),(left,top))
 if typ in ['facepaint','scar'] or id=='eyepatch_1':
  b=np.array(out);b[:,:,3]=np.minimum(b[:,:,3],head_alpha)
  if typ=='scar':b[:,:,3]=(b[:,:,3]*.75).astype('uint8')
  out=Image.fromarray(b)
 out.save(V/'assets'/(id+'_1.png'));regs[id]={'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'method':'uniform_object_scale_then_anatomical_translation','source_bbox':[x0,y0,x1,y1],'scale':scale,'source_feature':feature,'target_feature':target,'translation':[left,top],'canvas':[1024,1024],'review':'pending_visual'};j['status']='registered_draft'
(V/'registration.json').write_text(json.dumps(regs,indent=2));(V/'jobs.json').write_text(json.dumps(jobs,ensure_ascii=False,indent=2))
print('Extra registered drafts:',sum(id in regs for id in spec)+('facepaint_5' in regs))

import sys
import hashlib
"""Rigid, anatomically anchored registration of individual face/accessory art.
Only transparent canvas margins are cropped. Artwork is never stretched.
"""
from pathlib import Path
from PIL import Image
from scipy.ndimage import label,find_objects,binary_fill_holes
import numpy as np,json
V=Path(__file__).resolve().parent
jobs=json.loads((V/'jobs.json').read_text());regs=json.loads((V/'registration.json').read_text())

def patch_of(src):
    a=np.array(src);ll,n=label(a[:,:,3]>80);cnt=np.bincount(ll.ravel());ss=find_objects(ll)
    ids=[i for i in range(1,n+1) if cnt[i]>20]
    x0=max(0,min(ss[i-1][1].start for i in ids)-2);x1=min(src.width,max(ss[i-1][1].stop for i in ids)+2)
    y0=max(0,min(ss[i-1][0].start for i in ids)-2);y1=min(src.height,max(ss[i-1][0].stop for i in ids)+2)
    return src.crop((x0,y0,x1,y1)),[x0,y0,x1,y1]

def holes_of(patch):
    a=np.array(patch)[:,:,3]>128;ll,n=label(binary_fill_holes(a)&~a);cnt=np.bincount(ll.ravel());ss=find_objects(ll)
    return sorted([s for i,s in enumerate(ss,1) if cnt[i]>400],key=lambda s:s[0].start)

def rigid(patch,width,feature,target):
    scale=width/patch.width;left=round(target[0]-feature[0]*scale);top=round(target[1]-feature[1]*scale)
    out=Image.new('RGBA',(1024,1024));out.alpha_composite(patch.resize((round(width),round(patch.height*scale)),Image.Resampling.LANCZOS),(left,top))
    return out,{'scale':scale,'translation':[left,top]}

for j in jobs:
    typ=j['type'];id=j['id']
    if sys.argv[1:] and id not in sys.argv[1:]:continue
    p=V/'sources'/(id+'.png')
    if typ not in ['mask','scarf','balaclava','gasmask','background','glasses','eyepatch','headset','cigar','cigarette','rank','facepaint','scar'] or not p.exists():continue
    if id=='headset_1':continue # separately reviewed full-cup / boom component registration
    if typ in ['headset','glasses','eyepatch','cigar','cigarette','rank','facepaint','scar']:continue # explicitly registered after individual source review
    src=Image.open(p).convert('RGBA');patch,bbox=patch_of(src);w,h=patch.size;holes=holes_of(patch)
    feature=[w/2,0];target=[512,430];width=390
    if typ=='background':
        side=min(src.size);x=(src.width-side)//2;y=(src.height-side)//2;out=src.crop((x,y,x+side,y+side)).resize((1024,1024),Image.Resampling.LANCZOS);transform={'method':'uniform_square_background_scale'}
    else:
        if typ=='balaclava' or id=='scarf_1' or id=='mask_5':
            if not holes:j['status']='requires_regeneration_missing_eye_opening';continue
            eyes=holes[:2] if len(holes)>1 and abs(holes[0][0].start-holes[1][0].start)<50 else holes[:1]
            feature=[float(np.mean([(s[1].start+s[1].stop)/2 for s in eyes])),float(np.mean([(s[0].start+s[0].stop)/2 for s in eyes]))]
            if id=='balaclava_7':feature[1]=holes[0][0].start+70
            width=500 if id in ['scarf_1','mask_5'] else 500 if id in ['balaclava_7','balaclava_8','balaclava_10'] else 450
            target=[512,360]
        elif typ in ['mask','gasmask']:
            if typ=='mask':width=320 if id=='mask_3' else 380 if id!='mask_4' else 390
            else:width=430 if int(id.split('_')[1])<=3 else 480 if id=='gasmask_4' else 520
            if typ=='gasmask' and int(id.split('_')[1])>=4:
                if holes:
                    eyes=holes[:2] if len(holes)>1 else holes
                    feature=[float(np.mean([(s[1].start+s[1].stop)/2 for s in eyes])),float(np.mean([(s[0].start+s[0].stop)/2 for s in eyes]))]
                else:feature=[w/2,h*({'gasmask_5':.39,'gasmask_6':.34,'gasmask_7':.37,'gasmask_9':.37,'gasmask_10':.36}.get(id,.38))]
                target=[512,360]
            else:
                aa=np.array(patch);line=aa[:,int(w*.49):int(w*.51),3].mean(1)>128
                rows=np.where(line)[0];feature=[w/2,int(rows[0])];target=[512,430]
        else:
            width=450 if id!='scarf_3' else 530;target=[512,430 if id=='scarf_2' else 445]
        out,transform=rigid(patch,width,feature,target)
        transform.update(method='uniform_object_scale_then_anatomical_translation',source_bbox=bbox,source_feature=feature,target_feature=target)
    out.save(V/'assets'/(id+'_1.png'));regs[id]={'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),**transform,'canvas':[1024,1024],'review':'pending_visual'};j['status']='registered_draft'
    if typ=='balaclava' or id in ['mask_5','scarf_1']:
        a=np.array(out);clear=[a[360,x,3]<90 for x in [434,590]]
        if not all(clear):j['status']='requires_eye_alignment_review'
        regs[id]['eye_points_clear']=all(clear)
(V/'registration.json').write_text(json.dumps(regs,indent=2));(V/'jobs.json').write_text(json.dumps(jobs,indent=2,ensure_ascii=False))
print('Registered facewear/background drafts:',sum(j['type'] in ['mask','scarf','balaclava','gasmask','background'] and (V/'assets'/(j['id']+'_1.png')).exists() for j in jobs))

"""Flag skin contamination / opaque backgrounds before any registration.
Heuristic flags require visual review; they never erase pixels automatically.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
V=Path(__file__).resolve().parent
jobs=json.loads((V/'jobs.json').read_text());report=[]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
for j in jobs:
    p=V/'sources'/(j['id']+'.png')
    if not p.exists():continue
    im=Image.open(p).convert('RGBA');a=np.array(im);r,g,b=[a[:,:,i].astype(float) for i in range(3)]
    skin=(r>110)&(r>g+18)&(g>b+16)&(r>b*1.25)&(a[:,:,3]>128)
    flags=[]
    if j['type'] not in ['background','cigar','cigarette','rank','scar','facepaint'] and skin.sum()>4500:flags.append('possible_person_in_source')
    if j['type']!='background' and min(a[0,0,3],a[0,-1,3],a[-1,0,3],a[-1,-1,3])>128:flags.append('opaque_background')
    report.append({'id':j['id'],'skin_pixels':int(skin.sum()),'flags':flags})
(V/'qa/source_audit.json').write_text(json.dumps(report,indent=2))
selected=[r for r in report if r['flags']]
for start in range(0,len(selected),12):
    batch=selected[start:start+12];sh=Image.new('RGB',(1200,((len(batch)+3)//4)*330),'#293239')
    for k,r in enumerate(batch):
        im=Image.open(V/'sources'/(r['id']+'.png')).convert('RGBA');base=Image.new('RGBA',im.size,'#293239');base.alpha_composite(im);x=k%4*300;y=k//4*330;sh.paste(base.resize((300,300)).convert('RGB'),(x,y));ImageDraw.Draw(sh).text((x+7,y+305),r['id'],font=font,fill='white')
    sh.save(V/f'qa/flagged_sources_{start//12+1}.jpg',quality=95)
print('Source audit:',len(report),'files;',len(selected),'flagged:',[r['id'] for r in selected])

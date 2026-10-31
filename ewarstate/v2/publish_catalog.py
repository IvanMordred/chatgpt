"""Build portable previews and a local layer viewer for the reviewed PNG pack."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from collections import defaultdict
import json,shutil
V=Path(__file__).resolve().parent;REPO=V.parent.parent;O=REPO/'assets v2'
records=json.loads((V/'manifest.json').read_text());by_model=defaultdict(list)
for r in records:by_model[r['model_id']].append(r)
for arr in by_model.values():arr.sort(key=lambda r:r['color_number'])
head=Image.open(V/'reference/head.png').convert('RGBA');font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
(O/'reference').mkdir(parents=True,exist_ok=True);shutil.copy2(V/'reference/head.png',O/'reference/head.png')
def asset(id):return Image.open(REPO/next(r['file'] for r in records if r['id']==id)).convert('RGBA')
def composite(ids):
    im=Image.new('RGBA',(1024,1024),'#293239')
    backgrounds=[x for x in ids if x.startswith('background_')]
    for x in backgrounds:im.alpha_composite(asset(x))
    im.alpha_composite(head)
    for x in ids:
        if x not in backgrounds:im.alpha_composite(asset(x))
    return im
def single(r):
    ids=[]
    if r['type']=='background':ids.append(r['id'])
    if r['type']!='uniform':ids.append('uniform_1_4')
    if r['type']=='background':ids.append('vest_1_3')
    else:ids.append(r['id'])
    return composite(ids)
def sheet(arr,path,cols=5,side=250,face=False):
    path.parent.mkdir(parents=True,exist_ok=True);sh=Image.new('RGB',(cols*side,((len(arr)+cols-1)//cols)*(side+30)),'#293239')
    for k,r in enumerate(arr):
        im=single(r)
        if face:im=im.crop((285,235,740,690))
        x=k%cols*side;y=k//cols*(side+30);sh.paste(im.resize((side,side),Image.Resampling.LANCZOS).convert('RGB'),(x,y));ImageDraw.Draw(sh).text((x+5,y+side+5),r['id']+' / '+r['label'][:15],font=font,fill='white')
    sh.save(path,quality=94)
for id,arr in by_model.items():
    if id=='helmet_1':
        for cat in ['sumska','pustinjska','urbana','tropska','snezna','premium','solid']:
            sheet([r for r in arr if r['category']==cat],O/'previews/helmet 1'/(cat+'.jpg'),cols=6,side=240)
    else:sheet(arr,O/'previews/models'/(id+'.jpg'))
groups=defaultdict(list)
for id,arr in by_model.items():
    r=next((r for r in arr if r.get('color') in ['olive','navy']),arr[0])
    if id=='helmet_1':r=next(r for r in arr if r.get('solid_hex')=='#697247')
    groups[r['type']].append(r)
for typ,arr in groups.items():
    for start in range(0,len(arr),12):sheet(arr[start:start+12],O/'previews/overviews'/(typ+'_'+str(start//12+1)+'.jpg'),cols=4,side=300,face=typ in ['glasses','eyepatch','cigar','cigarette','facepaint','scar'])

# Cross-category examples are concrete reviewed combinations, not a claim that
# all equipment can be worn simultaneously with every other item.
cases=[
 ['background_3_1','uniform_1_5','vest_1_3','helmet_1_1','glasses_1_1','headset_1_1'],
 ['background_4_1','uniform_6_4','vest_2_4','helmet_1_224','headset_2_1'],
 ['background_10_1','uniform_11_2','vest_17_2','gasmask_6_2','helmet_1_210'],
 ['background_7_1','uniform_13_2','vest_29_2','balaclava_2_2','helmet_1_222'],
 ['background_6_1','facepaint_5_1','uniform_5_5','vest_3_3','cap_3_3'],
 ['background_5_1','scar_1_1','uniform_20_2','vest_20_2','helmet_19_2'],
 ['background_2_1','uniform_28_2','vest_14_2','mask_4_2','helmet_14_2'],
 ['background_8_1','uniform_19_4','vest_12_4','helmet_12_3'],
 ['background_9_1','uniform_21_4','vest_27_2','beret_2_4','rank_3_1'],
 ['background_3_1','uniform_10_3','vest_18_3','hat_3_4','eyepatch_1_1','cigar_1_1'],
 ['background_4_1','uniform_26_4','vest_9_4','scarf_1_4'],
 ['background_7_1','uniform_24_2','hood_2_2'],
 ['background_2_1','uniform_8_3','vest_11_2','cap_12_2','headset_2_1'],
 ['background_8_1','uniform_27_2','vest_13_4','helmet_15_2'],
 ['background_5_1','uniform_12_2','vest_21_2','helmet_18_2'],
 ['background_9_1','uniform_22_3','vest_28_2','cap_10_3','glasses_2_1','cigarette_1_1'],
 ['background_6_1','uniform_25_4','vest_5_3','hood_4_2'],
 ['background_7_1','uniform_17_2','balaclava_7_2'],
 ['background_5_1','uniform_14_3','vest_16_2','helmet_20_2'],
 ['background_10_1','uniform_30_2','vest_26_2','helmet_21_2'],
 ['background_4_1','uniform_2_4','vest_6_4','mask_3_4','helmet_2_4'],
 ['background_3_1','facepaint_2_1','uniform_7_3','vest_22_3','hat_2_3'],
 ['background_7_1','uniform_18_2','vest_23_2','hat_6_4','scarf_4_2'],
 ['background_8_1','uniform_15_2','vest_30_2','helmet_13_2'],
]
known={r['id'] for r in records};assert all(x in known for case in cases for x in case)
for start in range(0,len(cases),12):
    sh=Image.new('RGB',(1600,1290),'#293239')
    for k,ids in enumerate(cases[start:start+12]):
        im=composite(ids);x=k%4*400;y=k//4*430;sh.paste(im.resize((400,400),Image.Resampling.LANCZOS).convert('RGB'),(x,y));ImageDraw.Draw(sh).text((x+7,y+405),'eWarState / '+str(start+k+1),font=font,fill='white')
    sh.save(O/'previews'/('commanders_'+str(start//12+1)+'.jpg'),quality=95)
(O/'examples.json').write_text(json.dumps(cases,indent=2))
(O/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
models=[{'id':id,'type':arr[0]['type'],'name':arr[0]['name'],'variants':[{'id':r['id'],'label':r['label'],'file':str(Path(r['file']).relative_to('assets v2'))} for r in arr]} for id,arr in by_model.items()]
(O/'catalog.js').write_text('const MODELS='+json.dumps(models,ensure_ascii=False)+';\nconst EXAMPLES='+json.dumps(cases)+';\n')
print('Published catalog:',len(models),'models,',len(records),'variants,',len(cases),'combination examples')

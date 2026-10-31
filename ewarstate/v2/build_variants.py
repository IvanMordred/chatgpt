"""Export color variants from individually registered, visually reviewed bases.
Output is still draft until the material sheets and combinations are reviewed.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,sys
import numpy as np
from materials import material_mask,recolor,solid,COLORS
V=Path(__file__).resolve().parent;R=V.parent
REPO=R.parent;OUTPUT=REPO/'assets v2'
FOLDERS={'helmet':'helmets','cap':'caps','beret':'berets','hat':'hats','hood':'hoods',
         'uniform':'uniforms','vest':'vests','mask':'masks','scarf':'scarves',
         'balaclava':'balaclavas','gasmask':'gasmasks','glasses':'glasses',
         'eyepatch':'eyepatches','headset':'headsets','cigar':'cigars',
         'cigarette':'cigarettes','rank':'ranks','facepaint':'facepaints',
         'scar':'scars','background':'backgrounds'}
COLORS.update(yellow='#D8B548',maroon='#8A354B',blue='#396DA5',gold='#B49A58',green='#3A6244')
TEX={'woodland':R/'camouflage/textures/sumska/sumska_01_organic_woodland.png',
     'desert':R/'camouflage/textures/pustinjska/pustinjska_01_pixel_digital.png',
     'urban':R/'camouflage/textures/urbana/urbana_02_fragment.png'}
jobs=json.loads((V/'jobs.json').read_text());regs=json.loads((V/'registration.json').read_text())
types=sys.argv[1:];manifest=json.loads((V/'manifest.json').read_text()) if (V/'manifest.json').exists() else []
head=Image.open(V/'reference/head.png').convert('RGBA')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
processed=[]
for j in jobs:
    id=j['id'];p=V/'models'/id/'base.png'
    if types and j['type'] not in types and id not in types:continue
    if not p.exists() or id not in regs or 'visually_checked' not in regs[id].get('review',''):continue
    assert regs[id].get('source_sha256')==hashlib.sha256((V/'sources'/(id+'.png')).read_bytes()).hexdigest(), 'Source changed after registration: '+id
    assert regs[id].get('base_sha256')==hashlib.sha256(p.read_bytes()).hexdigest(), 'Base changed after review: '+id
    base=Image.open(p).convert('RGBA');md=V/'models'/id;md.mkdir(parents=True,exist_ok=True);base.save(md/'base.png')
    mask=material_mask(base,id);Image.fromarray((mask*255).astype('uint8')).save(md/'material_mask.png')
    variants=[]
    if id=='helmet_1':
        for t in json.loads((R/'camouflage/manifest.json').read_text()):variants.append((t['palette']+' / '+t['pattern'],Image.open(R/'camouflage'/t['file']),{'texture_id':t['id'],'texture_file':str(Path('ewarstate/camouflage')/t['file']),'category':t['category'],'palette':t['palette'],'pattern':t['pattern']}))
        for c in json.loads((R/'helmets/solid_colors.json').read_text()):variants.append((c['name'],solid(c['hex']),{'solid_hex':c['hex'],'category':'solid'}))
    else:
        for choice in j['choices']:
            paint=None if choice in ['base','gray'] else Image.open(TEX[choice]) if choice in TEX else solid(COLORS[choice])
            variants.append((choice,paint,{'color':choice,'solid_hex':COLORS.get(choice),'texture_file':str(TEX[choice].relative_to(REPO)) if choice in TEX else None}))
    manifest=[r for r in manifest if r['model_id']!=id]
    sheet=Image.new('RGB',(1250,((len(variants)+4)//5)*280),'#293239')
    dest=OUTPUT/FOLDERS[j['type']]/id.replace('_',' ');dest.mkdir(parents=True,exist_ok=True)
    for k,(name,paint,meta) in enumerate(variants,1):
        out=base.copy() if paint is None else recolor(base,paint,mask,id=='helmet_1')
        f=dest/(id+'_'+str(k)+'.png');out.save(f)
        assert np.array_equal(np.array(out)[:,:,3],np.array(base)[:,:,3])
        manifest.append({'id':f.stem,'model_id':id,'type':j['type'],'name':j['name'],'model_number':int(id.rsplit('_',1)[1]),'color_number':k,'label':name,'file':str(f.relative_to(REPO)),'canvas':[1024,1024],'position':[0,0],'layer':'background' if j['type']=='background' else 'front','review':'material_review_pending',**meta,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
        im=Image.new('RGBA',(1024,1024),'#293239')
        if j['type']=='background':im.alpha_composite(out)
        im.alpha_composite(head)
        if j['type']!='uniform':im.alpha_composite(Image.open(V/'models/uniform_1/base.png'))
        if j['type']=='background':im.alpha_composite(Image.open(V/'models/vest_1/base.png'))
        else:im.alpha_composite(out)
        x=(k-1)%5*250;y=(k-1)//5*280;sheet.paste(im.resize((250,250)).convert('RGB'),(x,y));ImageDraw.Draw(sheet).text((x+5,y+254),f.stem+' / '+name[:16],font=font,fill='white')
    (V/'previews').mkdir(exist_ok=True);sheet.save(V/'previews'/(id+'.jpg'),quality=94)
    processed.append(id)
(V/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Rebuilt variants for',len(processed),'models; total',len(manifest),'variant files. Material review remains required.')

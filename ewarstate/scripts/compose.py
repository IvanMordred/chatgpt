from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import random,json,zipfile
r=Path('/workspace/commander-preview'); out=Path('/workspace/commander-preview/output/komandiri');out.mkdir(exist_ok=True)
rng=random.Random(731904)
base=r/'ewarstate_master_proba (1)'
bgs=sorted((r/'backgrounds_accessories_8/backgrounds').glob('*.png'))
uniforms=sorted((r/'uniforms_10_additional/uniforms').glob('*.png'))+[base/'02_uniforma.png']
armors=sorted((r/'armor_extra_11_20/assets').glob('*.png'))+[base/'03_pancir.png']
facial=r/'facial_12/assets'; masks=sorted((r/'ewarstate_masks_30/assets').glob('*.png'));acc=r/'backgrounds_accessories_8/accessories'
rng.shuffle(uniforms);rng.shuffle(armors);rng.shuffle(masks)
sheet=Image.new('RGB',(2048,1700),'#111820');draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',32)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
draw.text((24,18),'eWarState / 12 nasumicnih komandira',font=font,fill='#eed9ac')
manifest=[]
for i in range(12):
 layers=[bgs[i%4],base/'01_glava.png',uniforms[i%len(uniforms)],armors[i%len(armors)]]
 if i%4!=0: layers.append(facial/f'hair_0{rng.randint(1,3)}_'+['','crop','swept','mohawk'][1]+'.png') if False else None
 if i%4!=0: layers.append(rng.choice(sorted(facial.glob('hair*.png'))))
 if i%3==0: layers.append(rng.choice(sorted(facial.glob('beard*.png'))))
 elif i%3==1: layers.append(masks[i])
 else: layers.append(rng.choice(sorted(facial.glob('moustache*.png'))))
 if i%3==2: layers.append(rng.choice(sorted(facial.glob('scar*.png'))))
 if i%4==0: layers.append(acc/'acc03_headset.png')
 elif i%4==1: layers.append(acc/'acc01_black_glasses.png')
 elif i%4==2: layers.append(acc/'acc02_gold_aviators.png')
 im=Image.new('RGBA',(1024,1024))
 for p in layers: im=Image.alpha_composite(im,Image.open(p).convert('RGBA'))
 im.save(out/f'komandir_{i+1:02d}.png')
 x=(i%4)*512;y=80+(i//4)*540
 sheet.paste(im.convert('RGB').resize((512,512),Image.Resampling.LANCZOS),(x,y))
 draw.rectangle((x,y+480,x+511,y+511),fill='#111820')
 draw.text((x+16,y+483),f'KOMANDIR {i+1:02d}',font=small,fill='#eed9ac')
 manifest.append({'komandir':i+1,'layers':[str(p.relative_to(r)) for p in layers]})
sheet.save('/workspace/commander-preview/output/komandiri_pregled.jpg',quality=95)
(out/'slojevi.json').write_text(json.dumps(manifest,indent=2))
with zipfile.ZipFile('/workspace/commander-preview/output/komandiri_12.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in out.iterdir():z.write(p,p.name)
print('Created 12 PNG portraits, overview and layer manifest.')

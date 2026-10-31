"""Contact sheets of real registered layers on the unchanged supplied head."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,sys
V=Path(__file__).resolve().parent
HEAD=Image.open(V/'reference/head.png').convert('RGBA')
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
jobs=json.loads((V/'jobs.json').read_text())
types=sys.argv[1:] or sorted({j['type'] for j in jobs})
for typ in types:
    selected=[j for j in jobs if j['type']==typ and (V/'assets'/(j['id']+'_1.png')).exists()]
    for start in range(0,len(selected),12):
        batch=selected[start:start+12];sh=Image.new('RGB',(1200,((len(batch)+3)//4)*330),'#293239')
        for k,j in enumerate(batch):
            im=Image.new('RGBA',(1024,1024),'#293239')
            if typ=='background':im.alpha_composite(Image.open(V/'assets'/(j['id']+'_1.png')))
            im.alpha_composite(HEAD)
            if typ!='uniform':im.alpha_composite(Image.open(V/'assets/uniform_1_1.png'))
            if typ=='background':im.alpha_composite(Image.open(V/'assets/vest_1_1.png'))
            else:im.alpha_composite(Image.open(V/'assets'/(j['id']+'_1.png')))
            if typ in ['glasses','eyepatch','cigar','cigarette','scar','facepaint']:im=im.crop((285,235,740,690))
            x=k%4*300;y=k//4*330;sh.paste(im.resize((300,300),Image.Resampling.LANCZOS).convert('RGB'),(x,y));ImageDraw.Draw(sh).text((x+7,y+305),j['id']+' / draft',font=FONT,fill='white')
        sh.save(V/f'qa/{typ}_page_{start//12+1}.jpg',quality=95)
    print(typ,len(selected))

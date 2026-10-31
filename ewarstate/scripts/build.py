from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np,json,csv,zipfile,hashlib
R=Path(__file__).resolve().parents[1]; O=R/'camouflage';O.mkdir(exist_ok=True)
# Colors run from darkest to lightest, shared by the six pattern stencils.
P={
'sumska':[
('Duboka suma','171F16 34432B 59633A 81724B B2A47B'),
('Hrast','24251A 454B2D 6D7044 928157 C1AE7C'),
('Bor','101F1C 244135 42624B 728069 A6AD8D'),
('Jesen','2B211B 50392A 785035 A87945 C4A16C'),
('Mahovina','1C251B 3D5030 657746 909260 BAB993'),
('Sumrak','172025 303D3C 4B5E51 74806C A0A28B')],
'pustinjska':[
('Pesak','514436 80694D AB8D62 D0B27F EBD8AF'),
('Dine','5B3928 885A37 B47C47 D6A664 F1D29A'),
('Kamenjar','393A36 64625A 918776 B6AB94 DDD3BD'),
('Slana pustinja','605E55 8B887B B7B29F D9D3BF F3EDD9'),
('Crveni kanjon','432C27 754334 A56244 C58D62 E1B68B'),
('Nocna pustinja','262A2B 474A44 70705E 9A9580 C5BBA0')],
'urbana':[
('Beton','23272B 464C50 737B7D A4ABAA D4D8D4'),
('Asfalt','11151B 29313A 485460 707D87 A7B2BA'),
('Rusevine','292825 514C46 7B7267 A79B8A D4C7B2'),
('Industrija','212A2D 3D5053 627575 91A09B C5CBC2'),
('Prasina','302D30 565157 817B80 B0A7AA DBD2D0'),
('Nocni grad','0C1220 202C40 3C4D65 66788F A6B5C7')],
'tropska':[
('Dzungla','102316 24512A 477638 78A14B B9C77A'),
('Mangrove','152C29 285046 4E7861 83A17B BBD0A0'),
('Bambus','27341A 4B6226 7D8D3A ADB65F D9D798'),
('Vulkansko ostrvo','1B2520 354E35 5B7744 89965B B7B184'),
('Monsun','102B30 24505A 477C7B 79A79A B7C9AB'),
('Palma','1B2F1C 37602E 618743 9AAC60 D4D191')],
'snezna':[
('Arktik','414F5C 738593 A2B4BE D0DDE2 F4F8F8'),
('Lednik','254458 537D94 8DAFC0 C5DDE5 F0FAFF'),
('Snezan bor','34433C 66786A 9CAD9A CCD6C8 F4F5EA'),
('Planinski kamen','43464D 747982 A6ADB3 D4DADF F7F8FA'),
('Polarna noc','182840 3D5673 7A94AF B6CBDF E8F2FA'),
('Prljavi sneg','4A4940 7C7A6B A9A898 D5D1C2 F4F0E4')],
'premium':[
('Zlatni pepeo','18191B 3D3B37 746545 B49A58 E5CE8A'),
('Krvavi mesec','170F18 3A1724 761F31 B33A43 E58B78'),
('Kobalt','0C162B 173764 235F9C 4E9DCD B2DEF0'),
('Ametist','1B122B 3E2459 704497 A77BC2 DCC7EE'),
('Patina','172C2A 305F56 599382 9BAD85 D3BF8D'),
('Obsidijan','0D1015 252B35 4A5361 87909D D2D8E1')]
}
patterns=['pixel_digital','organic_woodland','stripes_tiger','speckled_dot','hex','fragment']
labels=['PIXEL / DIGITAL','ORGANIC / WOODLAND','STRIPES / TIGER','SPECKLED / DOT','HEX','FRAGMENT']
src=Image.open(R/'concepts'/'camouflage_grayscale_atlas.png').convert('L')
w,h=src.size; stencils=[]
for n in range(6):
 x=n%3;y=n//3
 a=np.asarray(src.crop((x*w//3,y*h//2,(x+1)*w//3,(y+1)*h//2)),dtype=np.int16)
 # Assign all pixels to exactly five hard, flat grayscale classes.
 idx=np.abs(a[...,None]-np.array([16,72,128,184,238])).argmin(axis=2).astype('uint8')
 stencils.append(idx)
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
f=ImageFont.truetype(fontpath,17);fs=ImageFont.truetype(fontpath,12);title=ImageFont.truetype(fontpath,30)
manifest=[]; paletted=[]
for category,palettes in P.items():
 dest=O/'textures'/category;dest.mkdir(parents=True,exist_ok=True)
 sheet=Image.new('RGB',(1440,1660),'#14191F');d=ImageDraw.Draw(sheet)
 d.text((20,15),f'eWarState / {category.upper()} / 36 tekstura',font=title,fill='#E5D7B9')
 for j,lab in enumerate(labels):d.text((j*240+8,65),lab,font=fs,fill='#AEB9C5')
 for i,(name,hexstr) in enumerate(palettes):
  colors=['#'+c for c in hexstr.split()];rgb=[tuple(bytes.fromhex(c[1:])) for c in colors]
  paletted.append({'category':category,'palette_id':f'{i+1:02d}','name':name,'colors':colors})
  for j,pat in enumerate(patterns):
   im=Image.fromarray(np.array(rgb,dtype='uint8')[stencils[j]],'RGB').resize((1024,1024),Image.Resampling.NEAREST)
   filename=f'{category}_{i+1:02d}_{pat}.png';path=dest/filename;im.save(path,optimize=True)
   manifest.append({'id':f'{category}-{i+1:02d}-{j+1:02d}','category':category,'palette':name,'pattern':pat,'file':str(path.relative_to(O)),'width':1024,'height':1024,'colors':colors,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
   x=j*240;y=95+i*260
   sheet.paste(im.resize((232,216),Image.Resampling.NEAREST),(x+4,y))
   d.text((x+8,y+221),f'{i+1:02d} {name}',font=f,fill='#E5D7B9')
   for k,c in enumerate(colors):d.rectangle((x+8+k*44,y+246,x+49+k*44,y+252),fill=c)
 (O/'previews').mkdir(exist_ok=True);sheet.save(O/'previews'/f'{category}_36.jpg',quality=94)
(O/'palettes.json').write_text(json.dumps(paletted,indent=2,ensure_ascii=False))
(O/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
with (O/'palettes.csv').open('w',newline='') as fh:
 wr=csv.writer(fh);wr.writerow(['category','palette_id','name','dark_1','dark_2','mid','light_1','light_2'])
 for p in paletted:wr.writerow([p['category'],p['palette_id'],p['name'],*p['colors']])
# A separate compact sheet records all exact HEX values.
ps=Image.new('RGB',(1500,1740),'#14191F');d=ImageDraw.Draw(ps)
d.text((24,16),'eWarState / 36 PALETA / HEX',font=title,fill='#E5D7B9')
for n,p in enumerate(paletted):
 x=(n//12)*500+18;y=(n%12)*138+65
 d.text((x,y),f"{p['category']} {p['palette_id']} / {p['name']}",font=f,fill='white')
 for k,c in enumerate(p['colors']):
  xx=x+k*94;d.rectangle((xx,y+28,xx+88,y+83),fill=c);d.text((xx,y+91),c,font=fs,fill='#D9DFE7')
ps.save(O/'previews'/'palete_hex.png')
(O/'README.txt').write_text('eWarState: 216 kamuflaznih tekstura\n\n6 kategorija x 6 paleta x 6 dezena = 216 PNG fajlova.\nSvaki PNG je RGB, 1024x1024, sa tacno pet boja zadate palete.\nOsnove sest dezena generisane su kao koncept atlas; paneli su izdvojeni, kvantizovani na pet tonova i obojeni tacnim HEX paletama. Izvorni paneli su 512x512; PNG izvoz je uvecan nearest-neighbor metodom na 1024x1024.\nIsta osnova dezena koristi se kroz sve palete radi uporedivosti. Ovo nisu 216 nezavisno nacrtanih dezena nego 36 paleta x 6 osnova.\nTeksture nisu pripremljene niti verifikovane za seamless ponavljanje. Za kontinuirane UV povrsine dizajner treba da doradi spojeve. Nemaju alfa kanal: ovo su povrsinske teksture, a ne slojevi odece.\n\npalettes.csv i palettes.json: imena i HEX boje.\nmanifest.json: putanje, dimenzije, palete i SHA256 provere.\npreviews/: sest tabli i pregled svih paleta sa HEX oznakama.\nNaziv fajla: kategorija_paleta_dezen.png.\nPremium: Zlatni pepeo, Krvavi mesec, Kobalt, Ametist, Patina, Obsidijan.\n')
# Validate every delivered texture, rather than counting exports alone.
files=list((O/'textures').rglob('*.png'));assert len(files)==216
hashes=set()
for m in manifest:
 im=Image.open(O/m['file']);assert im.size==(1024,1024) and im.mode=='RGB'
 actual={tuple(c) for _,c in im.getcolors(maxcolors=6)}
 expected={tuple(bytes.fromhex(c[1:])) for c in m['colors']}
 assert actual==expected,(m['file'],actual)
 hashes.add(m['sha256'])
assert len(hashes)==216
with zipfile.ZipFile(R/'downloads'/'ewarstate_216_kamuflaza.zip','w',zipfile.ZIP_DEFLATED) as z:
 for path in sorted(O.rglob('*')):
  if path.is_file():z.write(path,path.relative_to(O))
print(json.dumps({'textures':len(files),'unique':len(hashes),'palettes':len(paletted),'dimensions':'1024x1024','colors_per_texture':5,'zip_bytes':(R/'downloads'/'ewarstate_216_kamuflaza.zip').stat().st_size}))

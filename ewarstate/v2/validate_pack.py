"""Structural and provenance checks for the production V2 deliverables."""
from pathlib import Path
from collections import Counter
from PIL import Image
import json,hashlib,re
V=Path(__file__).resolve().parent;R=V.parent;REPO=R.parent;O=REPO/'assets v2'
jobs=json.loads((V/'jobs.json').read_text());regs=json.loads((V/'registration.json').read_text());records=json.loads((V/'manifest.json').read_text())
assert len(jobs)==171 and len(records)==918
assert len({r['id'] for r in records})==918
base_alpha={}
for j in jobs:
 id=j['id'];reg=regs[id];source=V/'sources'/(id+'.png');base=V/'models'/id/'base.png'
 assert reg['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest(),('stale source',id)
 assert reg['base_sha256']==hashlib.sha256(base.read_bytes()).hexdigest(),('stale base',id)
 im=Image.open(base);assert im.mode=='RGBA' and im.size==(1024,1024)
 base_alpha[id]=hashlib.sha256(im.getchannel('A').tobytes()).hexdigest()
files=set();hashes=set()
for r in records:
 id=r['id'];mid=r['model_id'];assert re.fullmatch('[a-z]+_[1-9][0-9]*_[1-9][0-9]*',id),id
 p=REPO/r['file'];assert p.parent.name==mid.replace('_',' ') and p.name==id+'.png',p
 assert p.is_relative_to(O),p
 assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],id
 assert r['sha256'] not in hashes,('duplicate image',id)
 hashes.add(r['sha256']);files.add(p)
 im=Image.open(p);assert im.mode=='RGBA' and im.size==(1024,1024),id
 alpha=im.getchannel('A');assert hashlib.sha256(alpha.tobytes()).hexdigest()==base_alpha[mid],('alpha changed',id)
 if r['type']=='background':assert alpha.getextrema()==(255,255),id
 else:
  assert alpha.getpixel((0,0))==0,id
  if r['type'] not in ['uniform','vest']:
   assert max(alpha.crop((0,0,1024,1)).getextrema())<20,('top clipping',id)
   assert max(alpha.crop((0,1023,1024,1024)).getextrema())<20,('bottom clipping',id)
   assert max(alpha.crop((0,0,1,1024)).getextrema())<20,('left clipping',id)
   assert max(alpha.crop((1023,0,1024,1024)).getextrema())<20,('right clipping',id)
actual={p for p in O.rglob('*.png') if 'reference' not in p.relative_to(O).parts}
assert actual==files,('unlisted or missing production PNG',len(actual),len(files))
tex=json.loads((R/'camouflage/manifest.json').read_text());h=[r for r in records if r['model_id']=='helmet_1']
assert len(h)==240 and len([r for r in h if r.get('category')=='solid'])==24
assert {r['texture_id'] for r in h if 'texture_id' in r}=={r['id'] for r in tex}
for mid in {r['model_id'] for r in records}:
 nums=sorted(r['color_number'] for r in records if r['model_id']==mid);assert nums==list(range(1,len(nums)+1)),mid
report={'models':171,'variants':918,'unique_images':len(hashes),'canvas':[1024,1024],'alpha_matches_registered_base':True,'source_and_base_hashes_current':True,'requested_folder_hierarchy':True,'helmet_1':{'camouflage':216,'solid':24},'models_by_type':dict(Counter(j['type'] for j in jobs)),'variants_by_type':dict(Counter(r['type'] for r in records)),'visual_review':'Every base on supplied master; material sheets and 24 explicit cross-category examples. No claim of exhaustive combinatorial compatibility.'}
(O/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))

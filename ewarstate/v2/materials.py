"""Recolor registered artwork without changing alpha or silhouette.

The helmet shell mask follows the connected painted material, not a bounding
polygon. Other neutral fabric layers use continuous luminance modulation,
including seam highlights, while preserving colored leather/metal accents.
"""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import label, binary_dilation, binary_fill_holes, binary_closing

COLORS={'black':'#252B32','olive':'#697447','sand':'#C6AB7C',
        'navy':'#2D4563','brown':'#78553D','white':'#D6DEDE',
        'red':'#A53A43','orange':'#D27B36'}

def material_mask(base, model):
    a=np.array(base);rgb=a[:,:,:3].astype(float)
    lum=rgb.mean(2);sat=np.ptp(rgb,axis=2)
    if model=='helmet_1':
        ll,_=label((lum>95)&(sat<30)&(a[:,:,3]>128))
        seed=int(ll[130,512]);assert seed, 'Shell crown seed absent'
        core=ll==seed
        # The entire shell is a single material region; neighboring dark rails,
        # mount, rubber rim and hook-loop patches remain neutral hardware.
        edge=binary_dilation(core,iterations=1)&(lum>75)&(sat<35)&(a[:,:,3]>0)
        mask=core.astype(float);mask[edge&~core]=.8
        return mask
    # Warm gray highlights still belong to the fabric. A narrow neutrality
    # threshold would leave pale / brown slivers along seams after recoloring.
    mask=np.clip((75-sat)/20,0,1)*(a[:,:,3]>0)
    white_seeds={
        'uniform_27':[(300,945),(700,945),(40,975),(980,975)],
        'vest_13':[(178,715),(845,715),(309,930),(710,930),(293,1000),(730,1000)],
        'vest_11':[(512,932)],
    }
    if model in white_seeds:
        # Flood the actual light material bounded by its drawn seams, retaining
        # its darker facets too. Thresholding only white highlights makes a
        # reflective stripe look broken and leaves isolated white flecks.
        ll,n=label((lum>110)&(a[:,:,3]>128))
        ids={int(ll[y,x]) for x,y in white_seeds[model]}-{0}
        white=binary_fill_holes(np.isin(ll,list(ids)))
        white=binary_dilation(white,iterations=1)&(lum>70)&(a[:,:,3]>0)
        mask[white]=0
    if model in ['helmet_14','helmet_15','cap_13']:
        # Preserve the actual lamp lens enclosed by its gold ring. Painting
        # neutral whites indiscriminately would turn the lit bulb black.
        rr,gg,bb=[rgb[:,:,i] for i in range(3)]
        yy,xx=np.indices(lum.shape)
        gold=(rr>bb+50)&(gg>bb+30)&(a[:,:,3]>100)
        gold&=(xx>420)&(xx<605)&(yy>130)&(yy<315)
        ll,n=label(binary_closing(gold,iterations=3));counts=np.bincount(ll.ravel());counts[0]=0
        if counts.max():
            lamp=binary_fill_holes(ll==counts.argmax())
            mask[binary_dilation(lamp,iterations=1)]=0
    return mask

def recolor(base, paint, mask, shell=False):
    a=np.array(base);rgb=a[:,:,:3].astype(float)
    lum=rgb.mean(2)
    shade=np.clip(lum/(175 if shell else 160),.02,1.55)
    target=np.array(paint.convert('RGB').resize(base.size),dtype=float)
    out=a.copy();mix=mask[:,:,None]
    out[:,:,:3]=np.clip(rgb*(1-mix)+target*shade[:,:,None]*mix,0,255).astype('uint8')
    out[out[:,:,3]==0,:3]=0
    assert np.array_equal(out[:,:,3],a[:,:,3])
    return Image.fromarray(out)

def solid(hx):
    return Image.new('RGB',(1024,1024),hx)

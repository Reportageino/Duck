"""Extract character sprites from the hand-drawn kraft-paper photos.
Usage: python3 extract_sprites.py <uploads_dir> <out_dir>
Flood-fills the paper from the image border (dark ink lines act as walls),
drops small ink speckles, crops and saves transparent PNGs."""
import sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

SRC, OUT = sys.argv[1], sys.argv[2]
# name: (file, crop box in source px (l,t,r,b), keep-largest-N components)
JOBS = {
 'duck':  ('Cute_Duck_Skateboarding.png', (430, 280, 1250, 910), 3),
 'ghost': ('Quirky_Lavender_Ghost_with_Tea.png', (215, 370, 800, 1070), 6),
 'bear':  ('Adorable_Bear_on_Kraft_Paper.png', (270, 460, 800, 1130), 1),
 'dog':   ('Kraft_Paper_Puppy_with_a_Heart.png', (270, 400, 800, 1020), 4),
 'snail': ('Crayon_Snail_and_Playful_Frogs.png', (310, 420, 670, 770), 3),
 'frogs': ('Crayon_Snail_and_Playful_Frogs.png', (260, 1010, 850, 1280), 2),
 'glass': ('Melancholy_Coral_and_Teal_Creature.png', (180, 320, 720, 1290), 1),
 'worm':  ('Whimsical_Hat-Wearing_Worm_on_Kraft_Paper.png', (130, 410, 950, 1060), 1),
}
GAP = {'bear': 3, 'dog': 6}
SEALS = {'bear': [(132,262,122,322)]}
def lum(a): return 0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2]

for name,(f,box,keep) in JOBS.items():
    im = Image.open(f'{SRC}/{f}').convert('RGB').crop(box)
    a = np.asarray(im).astype(np.float32)
    # paper colour estimate from crop border
    border = np.concatenate([a[0],a[-1],a[:,0],a[:,-1]])
    paper = np.median(border,axis=0)
    dark = lum(a) < 95
    for (x0,y0,x1,y1) in SEALS.get(name, []):   # hand-drawn gaps to close
        for t in np.linspace(0,1,200):
            x=int(x0+(x1-x0)*t); y=int(y0+(y1-y0)*t); dark[y-3:y+4,x-3:x+4]=True
    # also treat strongly coloured (non-paper) pixels as walls for robustness
    dist = np.sqrt(((a-paper)**2).sum(-1))
    k = GAP.get(name, 2)
    wall = ndi.binary_dilation(dark, iterations=k) if k else dark
    open_ = ~wall
    lab,n = ndi.label(open_)
    edge = set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    bg = np.isin(lab, list(edge))
    if k: bg = ndi.binary_dilation(bg, iterations=k) & ~dark
    # small enclosed paper-coloured holes with paper colour (e.g. gaps between frogs' legs) -> bg too
    for i in range(1,n+1):
        if i in edge: continue
        m = lab==i
        if m.sum() < 4000 and dist[m].mean() < 22: bg |= m
    fg = ~bg
    lab2,n2 = ndi.label(fg)
    sizes = ndi.sum(fg,lab2,range(1,n2+1))
    order = np.argsort(sizes)[::-1]
    keepmask = np.zeros_like(fg)
    for k in order[:keep]:
        if sizes[k] > 150: keepmask |= lab2==(k+1)
    fg = ndi.binary_fill_holes(keepmask) if name not in ('frogs',) else keepmask
    alpha = Image.fromarray((fg*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    rgba = im.copy(); rgba.putalpha(alpha)
    bb = rgba.getbbox(); rgba = rgba.crop(bb)
    # downscale to max 360px tall/wide for game use
    s = 360/max(rgba.size)
    if s<1: rgba = rgba.resize((round(rgba.width*s), round(rgba.height*s)), Image.LANCZOS)
    rgba.save(f'{OUT}/{name}.png', optimize=True)
    print(name, rgba.size)

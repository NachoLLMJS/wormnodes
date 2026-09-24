from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import math

ROOT = Path(__file__).parent / "site" / "assets" / "media"
S = 4
W, H = 281*S, 357*S


def P(points):
    return [(int(x*S), int(y*S)) for x,y in points]


def apple_layer(size, body, accent, leaf, rotation=0):
    w,h=size
    im=Image.new("RGBA", (w,h), (0,0,0,0)); d=ImageDraw.Draw(im)
    # Apple silhouette: rounded lobes tapering to the base.
    body_poly=[(w*.18,h*.34),(w*.28,h*.18),(w*.46,h*.14),(w*.53,h*.23),(w*.61,h*.14),(w*.80,h*.20),(w*.88,h*.39),(w*.82,h*.68),(w*.64,h*.88),(w*.48,h*.93),(w*.29,h*.84),(w*.14,h*.60)]
    d.polygon(body_poly, fill=body, outline=(16,14,24,255), width=max(3,w//25))
    d.ellipse((w*.14,h*.17,w*.57,h*.66), fill=body)
    d.ellipse((w*.43,h*.16,w*.86,h*.66), fill=body)
    # Restore outline around combined body using a mask contour.
    mask=Image.new("L",(w,h),0); md=ImageDraw.Draw(mask)
    md.polygon(body_poly,fill=255); md.ellipse((w*.14,h*.17,w*.57,h*.66),fill=255); md.ellipse((w*.43,h*.16,w*.86,h*.66),fill=255)
    edge=mask.filter(ImageFilter.MaxFilter(max(3,(w//18)|1)))
    outline=Image.new("RGBA",(w,h),(14,12,22,255)); outline.putalpha(edge)
    inside=Image.new("RGBA",(w,h),body); inside.putalpha(mask)
    im=Image.alpha_composite(outline,inside); d=ImageDraw.Draw(im)
    # Comic shadow and highlights.
    d.ellipse((w*.48,h*.39,w*.79,h*.78), fill=accent)
    d.ellipse((w*.27,h*.26,w*.40,h*.43), fill=(255,255,255,235))
    d.ellipse((w*.23,h*.46,w*.29,h*.55), fill=(255,255,255,215))
    # Stem and leaf.
    d.line((w*.51,h*.22,w*.48,h*.04), fill=(18,14,20,255), width=max(8,w//13))
    d.line((w*.51,h*.22,w*.48,h*.04), fill=(110,56,27,255), width=max(4,w//22))
    leaf_poly=[(w*.50,h*.10),(w*.69,h*.01),(w*.88,h*.08),(w*.71,h*.22)]
    d.polygon(leaf_poly,fill=(14,18,17,255));
    inset=[(w*.53,h*.10),(w*.69,h*.035),(w*.83,h*.08),(w*.70,h*.18)]
    d.polygon(inset,fill=leaf)
    d.line((w*.57,h*.13,w*.78,h*.075),fill=(225,255,205,210),width=max(2,w//40))
    return im.rotate(rotation,Image.Resampling.BICUBIC,expand=True)


def make_pack(filename, color, dark, light, apples):
    im=Image.new("RGBA",(W,H),(0,0,0,0))
    # Drop shadow offset behind package.
    shadow=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(shadow)
    bag=P([(55,30),(224,40),(245,318),(40,326)])
    sd.polygon([(x+10*S,y+10*S) for x,y in bag],fill=(0,0,0,115))
    shadow=shadow.filter(ImageFilter.GaussianBlur(4*S)); im=Image.alpha_composite(im,shadow)
    # White sticker rim, black ink outline, then inner foil.
    d=ImageDraw.Draw(im)
    rim=P([(48,22),(232,32),(253,325),(32,335)])
    d.polygon(rim,fill=(255,255,255,255))
    d.line(rim+[rim[0]],fill=(255,255,255,255),width=7*S,joint="curve")
    d.polygon(bag,fill=(18,16,25,255))
    inner=P([(61,39),(218,47),(235,309),(49,317)])
    d.polygon(inner,fill=(184,188,194,255))
    # Bold two-tone split foil.
    right=P([(139,43),(218,47),(235,309),(140,313)])
    d.polygon(right,fill=color)
    d.polygon(P([(63,43),(139,47),(140,311),(51,314)]),fill=(190,193,198,255))
    # Zigzag crimp seams.
    top=[]; bottom=[]
    for x in range(57,225,9):
        top.append((x*S,(31+(4 if (x//9)%2 else 0))*S))
        bottom.append((x*S,(323-(4 if (x//9)%2 else 0))*S))
    d.line(top,fill=(16,14,22,255),width=4*S)
    d.line(bottom,fill=(16,14,22,255),width=4*S)
    d.line(P([(61,50),(218,57)]),fill=(255,255,255,130),width=2*S)
    d.line(P([(51,305),(234,297)]),fill=dark,width=3*S)
    # Diagonal gloss and halftone dots.
    d.polygon(P([(61,48),(106,50),(196,307),(155,310)]),fill=(255,255,255,32))
    for yy in range(74,292,13):
        for xx in range(154,222,13):
            if (xx+yy)//13%2==0:
                d.ellipse((xx*S,yy*S,(xx+3)*S,(yy+3)*S),fill=light)
    # Central badge, stars, and three apples; no lettering.
    d.ellipse((71*S,83*S,222*S,238*S),fill=(15,13,23,255))
    d.ellipse((78*S,90*S,215*S,231*S),fill=(255,247,226,255))
    d.ellipse((86*S,98*S,207*S,223*S),fill=dark)
    # Radial comic rays.
    cx,cy=146*S,160*S
    for a in range(0,360,30):
        r1,r2=50*S,60*S
        x1=cx+math.cos(math.radians(a))*r1; y1=cy+math.sin(math.radians(a))*r1
        x2=cx+math.cos(math.radians(a))*r2; y2=cy+math.sin(math.radians(a))*r2
        d.line((x1,y1,x2,y2),fill=(255,255,255,180),width=2*S)
    specs=[(82,116,66,78,-10),(125,102,72,85,7),(152,131,69,80,13)]
    for x,y,w,h,rot in specs:
        ap=apple_layer((w*S,h*S),*apples,rotation=rot)
        im.alpha_composite(ap,(x*S,y*S))
    # Tiny star highlights on the foil.
    for x,y in [(191,70),(66,267),(207,268)]:
        d=ImageDraw.Draw(im); r=7*S
        d.polygon([(x*S,(y-7)*S),((x+2)*S,(y-2)*S),((x+7)*S,y*S),((x+2)*S,(y+2)*S),(x*S,(y+7)*S),((x-2)*S,(y+2)*S),((x-7)*S,y*S),((x-2)*S,(y-2)*S)],fill=(255,255,255,225))
    # Downsample for crisp antialiasing and preserve alpha.
    im=im.resize((281,357),Image.Resampling.LANCZOS)
    im.save(ROOT/filename,optimize=True)
    print(filename,im.mode,im.size,im.getchannel('A').getextrema(),im.getbbox())

make_pack('apple-pack-route.png',(248,75,156,255),(184,26,102,255),(255,184,221,105),((245,52,62,255),(184,20,68,255),(70,190,51,255)))
make_pack('apple-pack-victory.png',(247,145,28,255),(209,78,17,255),(255,214,137,110),((252,185,46,255),(224,71,21,255),(80,183,44,255)))
make_pack('apple-pack-silver.png',(240,40,48,255),(166,14,36,255),(255,158,164,105),((213,20,37,255),(125,7,31,255),(60,172,48,255)))

from pathlib import Path
from PIL import Image
import numpy as np
import cv2

ROOT = Path(__file__).parent
MEDIA = ROOT / "site" / "assets" / "media"
SOURCES = {
    "wormnodes-logo.png": Path(r"C:\Users\nacho\AppData\Local\hermes\cache\images\openai_codex_gpt-image-2-medium_20260924_015737_916f21f9.png"),
    "node-pack-royal.png": Path(r"C:\Users\nacho\AppData\Local\hermes\cache\images\openai_codex_gpt-image-2-medium_20260924_015843_bf795f4e.png"),
    "node-pack-fuji.png": Path(r"C:\Users\nacho\AppData\Local\hermes\cache\images\openai_codex_gpt-image-2-medium_20260924_015915_5441a788.png"),
    "node-pack-golden.png": Path(r"C:\Users\nacho\AppData\Local\hermes\cache\images\openai_codex_gpt-image-2-medium_20260924_015948_abff99ef.png"),
}

def remove_checker(src: Path, dst: Path, target, pad=16):
    rgb = np.array(Image.open(src).convert("RGB"))
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    saturation = hsv[:,:,1]
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    # Build the silhouette from genuinely coloured art plus near-black ink.
    # The baked checkerboard is neutral mid-gray, so it never enters this seed.
    seed = np.logical_or(saturation > 42, gray < 58).astype(np.uint8) * 255
    seed = cv2.morphologyEx(seed, cv2.MORPH_CLOSE, np.ones((9,9),np.uint8))
    contours, hierarchy = cv2.findContours(seed, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    alpha = np.zeros(seed.shape, dtype=np.uint8)
    if hierarchy is None:
        raise RuntimeError(f"No artwork contours in {src}")
    min_area = rgb.shape[0] * rgb.shape[1] * 0.0008
    hierarchy = hierarchy[0]
    kept=[]
    for idx, contour in enumerate(contours):
        if hierarchy[idx][3] == -1 and cv2.contourArea(contour) >= min_area:
            cv2.drawContours(alpha, contours, idx, 255, thickness=cv2.FILLED)
            kept.append(idx)
    # Restore true transparent counters/holes only for the wordmark. Package
    # interiors intentionally contain neutral black/white ink and must remain.
    if dst.name == "wormnodes-logo.png":
        for idx, contour in enumerate(contours):
            parent=hierarchy[idx][3]
            if parent in kept and cv2.contourArea(contour) >= min_area * 0.25:
                cv2.drawContours(alpha, contours, idx, 0, thickness=cv2.FILLED)
    # Rebuild a crisp white sticker rim around the retained generated artwork.
    foreground = (alpha > 0).astype(np.uint8)
    kernel = np.ones((19,19), np.uint8)
    expanded = cv2.dilate(foreground, kernel, iterations=1)
    rim = np.logical_and(expanded > 0, foreground == 0)
    alpha[rim] = 255
    rgb[rim] = (255,255,255)
    rgba = Image.fromarray(np.dstack([rgb, alpha]), "RGBA")
    bbox = rgba.getbbox()
    if not bbox:
        raise RuntimeError(f"No foreground in {src}")
    x0,y0,x1,y1=bbox
    x0=max(0,x0-pad);y0=max(0,y0-pad);x1=min(rgba.width,x1+pad);y1=min(rgba.height,y1+pad)
    rgba=rgba.crop((x0,y0,x1,y1))
    canvas=Image.new("RGBA",target,(0,0,0,0))
    fit=rgba.copy(); fit.thumbnail((target[0]-12,target[1]-12),Image.Resampling.LANCZOS)
    canvas.alpha_composite(fit,((target[0]-fit.width)//2,(target[1]-fit.height)//2))
    canvas.save(dst,optimize=True)
    print(dst.name, canvas.size, canvas.mode, canvas.getchannel("A").getextrema(), canvas.getbbox())

remove_checker(SOURCES["wormnodes-logo.png"], MEDIA/"wormnodes-logo.png", (900,232), 20)
for name in ["node-pack-royal.png","node-pack-fuji.png","node-pack-golden.png"]:
    remove_checker(SOURCES[name], MEDIA/name, (281,357), 18)

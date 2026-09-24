from pathlib import Path
from PIL import Image
import cv2
import numpy as np

ROOT = Path(__file__).parent
SOURCE = ROOT / "source-assets" / "wormnodes-wordmark-generated.png"
OUTPUT = ROOT / "site" / "assets" / "media" / "wormnodes-logo.png"
TARGET = (1200, 300)

rgb = np.array(Image.open(SOURCE).convert("RGB"))
hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
# The baked checkerboard is neutral mid-gray. Keep yellow/orange color,
# black extrusion/outline and the bright white sticker border as seed art.
seed = ((hsv[:, :, 1] > 28) | (gray < 62) | (gray > 242)).astype(np.uint8) * 255
seed = cv2.morphologyEx(seed, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
contours, hierarchy = cv2.findContours(seed, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
if hierarchy is None:
    raise RuntimeError("No wordmark silhouette found")
hierarchy = hierarchy[0]
alpha = np.zeros(seed.shape, dtype=np.uint8)
min_area = rgb.shape[0] * rgb.shape[1] * 0.001
parents = []
for index, contour in enumerate(contours):
    if hierarchy[index][3] == -1 and cv2.contourArea(contour) >= min_area:
        cv2.drawContours(alpha, contours, index, 255, cv2.FILLED)
        parents.append(index)
for index, contour in enumerate(contours):
    if hierarchy[index][3] in parents and cv2.contourArea(contour) >= min_area * 0.08:
        cv2.drawContours(alpha, contours, index, 0, cv2.FILLED)
# Feather only the silhouette edge; RGB artwork itself is not altered
alpha = cv2.GaussianBlur(alpha, (3, 3), 0.55)
rgba = Image.fromarray(np.dstack([rgb, alpha]), "RGBA")
bbox = rgba.getbbox()
if not bbox:
    raise RuntimeError("Empty wordmark")
rgba = rgba.crop(bbox)
canvas = Image.new("RGBA", TARGET, (0, 0, 0, 0))
fit = rgba.copy()
fit.thumbnail((TARGET[0] - 20, TARGET[1] - 20), Image.Resampling.LANCZOS)
canvas.alpha_composite(fit, ((TARGET[0] - fit.width) // 2, (TARGET[1] - fit.height) // 2))
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
canvas.save(OUTPUT, optimize=True)
print(OUTPUT, canvas.size, canvas.mode, canvas.getchannel("A").getextrema(), canvas.getbbox())

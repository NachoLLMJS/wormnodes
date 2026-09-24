from pathlib import Path
from bs4 import BeautifulSoup
import shutil

ROOT = Path(__file__).parent
HTML = ROOT / "site" / "index.html"
BACKUP = ROOT / "site" / "index-before-apple-packs.html"

if not BACKUP.exists():
    shutil.copy2(HTML, BACKUP)

soup = BeautifulSoup(HTML.read_text("utf-8"), "html.parser")

pack_map = {
    "route one": "/assets/media/apple-pack-route.png?v=1",
    "victory road": "/assets/media/apple-pack-victory.png?v=1",
    "mt. silver": "/assets/media/apple-pack-silver.png?v=1",
}

removed_tiers = []
updated_packs = []
removed_card_backdrops = 0

for heading in list(soup.find_all("h3")):
    name = heading.get_text(" ", strip=True).lower()
    link = heading.find_parent("a")
    if not link:
        continue
    if name in {"champion", "legend"}:
        removed_tiers.append(name)
        link.decompose()
        continue
    if name not in pack_map:
        continue

    imgs = list(link.find_all("img"))
    pack_img = next((img for img in imgs if "tile-pack" in " ".join(img.get("class", []))), None)
    if pack_img is None:
        raise RuntimeError(f"Pack image not found for {name}")

    pack_img["src"] = pack_map[name]
    pack_img.attrs.pop("srcset", None)
    pack_img["alt"] = f"{heading.get_text(' ', strip=True)} apple pack"
    link.parent["id"] = "apple-pack-grid"

    # Keep only the comic tile background plus the new apple package.
    for img in imgs:
        if img is pack_img:
            continue
        classes = " ".join(img.get("class", []))
        if "tile-field" not in classes:
            img.decompose()
            removed_card_backdrops += 1
    updated_packs.append(name)

# Remove the complete Recent pulls section, including all cards and FMV prices.
recent = soup.find("img", attrs={"alt": "Recent pulls"})
removed_recent = False
if recent:
    section = recent.find_parent("section")
    if section:
        section.decompose()
        removed_recent = True

HTML.write_text(str(soup), "utf-8")
print("updated_packs", updated_packs)
print("removed_tiers", removed_tiers)
print("removed_card_backdrops", removed_card_backdrops)
print("removed_recent_section", removed_recent)

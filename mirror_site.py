from __future__ import annotations

import hashlib
import mimetypes
import re
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
ORIGIN = "https://pull.fun"
PAGE_URL = ORIGIN + "/en"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125 Safari/537.36"
URL_RE = re.compile(r"url\((['\"]?)(.*?)\1\)", re.I)

SITE.mkdir(parents=True, exist_ok=True)


def fetch(url: str) -> tuple[bytes, str]:
    req = Request(url, headers={"User-Agent": UA, "Accept": "*/*", "Referer": PAGE_URL})
    with urlopen(req, timeout=45) as response:
        return response.read(), response.headers.get_content_type()


def ext_for(content_type: str, url: str) -> str:
    ext = Path(urlparse(url).path).suffix.lower()
    if ext and len(ext) <= 6:
        return ext
    return {
        "image/avif": ".avif",
        "image/webp": ".webp",
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/svg+xml": ".svg",
        "text/css": ".css",
        "font/woff2": ".woff2",
        "audio/mpeg": ".mp3",
    }.get(content_type, mimetypes.guess_extension(content_type) or ".bin")


cache: dict[str, str] = {}
failures: list[tuple[str, str]] = []


def localize(url: str, kind: str = "asset") -> str:
    absolute = urljoin(PAGE_URL, url)
    if absolute.startswith("data:") or absolute.startswith("blob:") or absolute.startswith("#"):
        return url
    if absolute in cache:
        return cache[absolute]
    try:
        data, content_type = fetch(absolute)
        parsed = urlparse(absolute)
        if parsed.netloc == "pull.fun" and parsed.path.startswith(("/_next/static/", "/brand/", "/world/", "/icon")):
            relative = parsed.path.lstrip("/")
            if not Path(relative).suffix:
                relative += ext_for(content_type, absolute)
        else:
            digest = hashlib.sha256(absolute.encode()).hexdigest()[:18]
            relative = f"assets/{kind}/{digest}{ext_for(content_type, absolute)}"
        target = SITE / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        local = "/" + relative.replace("\\", "/")
        cache[absolute] = local
        return local
    except Exception as exc:
        failures.append((absolute, f"{type(exc).__name__}: {exc}"))
        cache[absolute] = absolute
        return absolute


html_data, _ = fetch(PAGE_URL)
(ROOT / "origin-en.html").write_bytes(html_data)
soup = BeautifulSoup(html_data, "html.parser")

# Preserve the server-rendered visual baseline and remove production runtime/tracking.
for tag in soup.find_all("script"):
    tag.decompose()
for tag in soup.find_all("link"):
    rel = {str(v).lower() for v in (tag.get("rel") or [])}
    href = tag.get("href")
    if not href:
        continue
    if "stylesheet" in rel:
        tag["href"] = localize(href, "css")
    elif "icon" in rel:
        tag["href"] = localize(href, "icons")
    elif rel.intersection({"preload", "modulepreload", "prefetch"}):
        tag.decompose()

# Localize all image/audio sources visible in the SSR homepage.
for tag in soup.find_all(True):
    if tag.name == "img":
        # The production runtime lazy-loads these and then removes its shimmer
        # placeholder. The static mirror has no hydration runtime, so finish that
        # visual state while keeping the real downloaded image.
        tag["loading"] = "eager"
        classes = list(tag.get("class") or [])
        if "opacity-0" in classes:
            tag["class"] = ["opacity-100" if c == "opacity-0" else c for c in classes]
            placeholder = tag.find_previous_sibling("div")
            if placeholder and {"absolute", "inset-0"}.issubset(set(placeholder.get("class") or [])):
                placeholder.decompose()
    for attr in ("src", "poster"):
        value = tag.get(attr)
        if value and not value.startswith(("data:", "blob:")):
            tag[attr] = localize(value, "media")
    for attr in ("srcset",):
        value = tag.get(attr)
        if value:
            entries = []
            for item in value.split(","):
                bits = item.strip().split()
                if bits:
                    bits[0] = localize(bits[0], "media")
                    entries.append(" ".join(bits))
            tag[attr] = ", ".join(entries)
    style = tag.get("style")
    if style and "url(" in style:
        tag["style"] = URL_RE.sub(lambda m: f"url('{localize(m.group(2), 'media')}')", style)

# Rewrite production page links to the original site, except the local home link.
for tag in soup.find_all("a", href=True):
    href = tag["href"]
    absolute = urljoin(PAGE_URL, href)
    if absolute.rstrip("/") == PAGE_URL.rstrip("/"):
        tag["href"] = "/"
    elif absolute.startswith(ORIGIN):
        tag["href"] = absolute

# Authentication state is client-rendered in production. Replace its SSR loading
# skeletons with inert links to the real login/register pages for visual parity.
header = soup.find("header")
if header:
    skeletons = header.select('[data-slot="skeleton"]')
    labels = [("Log in", ORIGIN + "/en/login", "local-auth-login"),
              ("Sign Up", ORIGIN + "/en/register", "local-auth-signup")]
    for skeleton, (label, href, css_class) in zip(skeletons[:2], labels):
        anchor = soup.new_tag("a", href=href)
        anchor["class"] = css_class
        anchor.string = label
        skeleton.replace_with(anchor)

# Make the page intentionally editable without touching minified CSS.
overrides = soup.new_tag("link", rel="stylesheet", href="/editable/overrides.css")
soup.head.append(overrides)
meta = soup.new_tag("meta", attrs={"name": "local-mirror", "content": "Static editable homepage baseline copied from public SSR output"})
soup.head.append(meta)

# Process downloaded CSS dependencies (fonts/background URLs).
for css_path in list((SITE / "_next" / "static" / "chunks").glob("*.css")) + list((SITE / "assets" / "css").glob("*.css")):
    text = css_path.read_text("utf-8", errors="replace")
    base_url = ORIGIN + "/" + css_path.relative_to(SITE).as_posix()
    def css_repl(match: re.Match[str]) -> str:
        raw = match.group(2).strip()
        if not raw or raw.startswith("data:"):
            return match.group(0)
        absolute = urljoin(base_url, raw)
        local = localize(absolute, "css-assets")
        rel = Path(local.lstrip("/")).relative_to(Path())
        target_abs = SITE / rel
        relative_from_css = target_abs.relative_to(SITE) if False else None
        import os
        rel_url = os.path.relpath(target_abs, css_path.parent).replace("\\", "/")
        return f"url('{rel_url}')"
    css_path.write_text(URL_RE.sub(css_repl, text), "utf-8")

(SITE / "editable").mkdir(exist_ok=True)
(SITE / "editable" / "overrides.css").write_text(
    "/* Put safe visual and copy-adjacent CSS changes here. Loaded after the original styles. */\n"
    ":root { --local-mirror-ready: 1; }\n"
    "img.opacity-0 { opacity: 1 !important; }\n"
    ".local-auth-login,.local-auth-signup{display:inline-flex;align-items:center;justify-content:center;"
    "height:2.25rem;padding:0 .95rem;border-radius:.7rem;color:#fff;font-size:.875rem;font-weight:600;"
    "text-decoration:none;white-space:nowrap}\n"
    ".local-auth-login{background:transparent}\n"
    ".local-auth-signup{background:#ff5ca8;box-shadow:0 8px 24px rgba(255,92,168,.35)}\n",
    "utf-8",
)
(SITE / "index.html").write_text(str(soup), "utf-8")

print(f"HTML: {SITE / 'index.html'}")
print(f"Downloaded assets: {len(cache)}")
print(f"Failures: {len(failures)}")
for url, reason in failures[:20]:
    print(f"FAIL {url} :: {reason}")

"""Baixa capa + legenda das publicações do Instagram listadas em POSTS e gera assets/posts.js.

Para atualizar: coloque os códigos das publicações novas em POSTS (o trecho depois de /p/ ou /reel/
na URL do post) e rode `python scripts/update_posts.py` na raiz do projeto.
"""
import html, json, re, time, urllib.request

POSTS = [
    ("reel", "DdqoFCYpL-1"), ("reel", "DdXjkQWp9AW"), ("reel", "DdsTG4KuPrW"),
    ("reel", "DdsQ4ECOkZ3"), ("reel", "DdsGcdBJGht"), ("reel", "DdsCYHAJ9Xr"),
    ("p", "DdsCKeMiWap"), ("reel", "DdsBIQAJv5z"), ("reel", "Ddq3jaQuK1O"),
    ("p", "DdqnwdrHHJj"),
]
UA = "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July",
                                       "August", "September", "October", "November", "December"], 1)}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=30).read()


def meta(page, prop):
    m = re.search(r'<meta property="og:%s" content="([^"]*)"' % prop, page)
    return html.unescape(m.group(1)) if m else ""


out = []
for kind, code in POSTS:
    page = get(f"https://www.instagram.com/{kind}/{code}/").decode("utf-8", "ignore")
    desc = meta(page, "description")
    m = re.search(r'on (\w+) (\d+), (\d{4}): "(.*)', desc, re.S)
    date = f"{m.group(3)}-{MONTHS[m.group(1)]:02d}-{int(m.group(2)):02d}" if m else ""
    caption = re.sub(r'"\.?\s*$', "", m.group(4) if m else desc).strip()
    price = re.search(r"R\$\s?\d+(?:,\d{2})?", caption)
    img = f"assets/posts/{code}.jpg"
    open(img, "wb").write(get(meta(page, "image")))
    out.append({"code": code, "url": f"https://www.instagram.com/{kind}/{code}/",
                "type": "video" if kind == "reel" else "photo", "img": img, "date": date,
                "price": price.group(0).replace("R$ ", "R$") if price else "", "caption": caption})
    print("ok", code)
    time.sleep(1)

profile = get("https://www.instagram.com/sarahboutique.sc/").decode("utf-8", "ignore")
open("assets/profile.jpg", "wb").write(get(meta(profile, "image")))
with open("assets/posts.js", "w", encoding="utf-8") as f:
    f.write("window.POSTS = " + json.dumps(out, ensure_ascii=False, indent=1) + ";\n")

import requests
import re
import os
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

SITEMAP_URLS = [
    "https://lecturia.org/post-sitemap1.xml",
    "https://lecturia.org/post-sitemap2.xml",
    "https://lecturia.org/post-sitemap3.xml",
]

CRAWL_PAGES = [
    "https://lecturia.org/",
    "https://lecturia.org/cuentos/",
    "https://lecturia.org/cuentos-completos/",
    "https://lecturia.org/ciencia-ficcion/",
    "https://lecturia.org/horror/",
    "https://lecturia.org/realismo/",
    "https://lecturia.org/poesia/",
]

OUTPUT_DIR = "cuentos"
STATE_FILE = "scraped_urls.json"
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; CuentosBot/1.0)"})


def load_scraped():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_scraped(urls):
    with open(STATE_FILE, "w") as f:
        json.dump(sorted(urls), f, indent=2)


def normalize_url(url):
    p = urlparse(url)
    path = p.path.rstrip("/") + "/"
    return f"{p.scheme}://{p.netloc}{path}"


def get_story_urls_from_sitemaps():
    urls = set()
    for sitemap_url in SITEMAP_URLS:
        try:
            resp = session.get(sitemap_url, timeout=30)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
            for url_elem in root.findall("s:url", NS):
                loc = url_elem.find("s:loc", NS).text
                path = urlparse(loc).path
                if "/cuentos-y-relatos/" in path and not path.startswith("/en/") and not path.startswith("/fr/"):
                    urls.add(normalize_url(loc))
        except Exception as e:
            print(f"  Error en {sitemap_url}: {e}")
    return urls


def get_story_urls_from_pages():
    urls = set()
    for page_url in CRAWL_PAGES:
        try:
            resp = session.get(page_url, timeout=15)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "lxml")
            for a in soup.find_all("a", href=True):
                href = urljoin(page_url, a["href"])
                path = urlparse(href).path
                if "/cuentos-y-relatos/" in path and not path.startswith("/en/") and not path.startswith("/fr/"):
                    # Only story URLs (have numeric ID at end)
                    if re.search(r'/cuentos-y-relatos/[^/]+/\d+/?$', path):
                        urls.add(normalize_url(href))
        except Exception as e:
            print(f"  Error en {page_url}: {e}")
    return urls


def scrape_story(url):
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        title_tag = soup.find("h1")
        if title_tag:
            title = title_tag.get_text(strip=True)
        else:
            og_title = soup.find("meta", property="og:title")
            title = og_title["content"] if og_title else "Sin titulo"

        author = "Desconocido"

        content_div = soup.find("div", class_="entry-content")
        if not content_div:
            content_div = soup.find("article")

        if content_div:
            for tag in content_div.find_all(["script", "style", "nav", "aside", "footer"]):
                tag.decompose()
            
            # Extract author from body text pattern: "AuthorName(Cuento completo)"
            for p in content_div.find_all("p")[:5]:
                text = p.get_text(strip=True)
                if text.startswith("Sinopsis"):
                    continue
                match = re.match(r'^(.+?)\s*\(', text)
                if match and len(match.group(1)) > 2:
                    author = match.group(1).strip()
                    break
            
            paras = content_div.find_all("p")
            text_parts = [p.get_text(strip=True) for p in paras if p.get_text(strip=True)]
            story_text = "\n\n".join(text_parts)
        else:
            story_text = ""

        img_url = None
        og_image = soup.find("meta", property="og:image")
        if og_image:
            img_url = og_image.get("content")

        return {"title": title, "author": author, "url": url, "text": story_text, "image_url": img_url}
    except Exception:
        return None


def sanitize_filename(name):
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', '-', name)
    return name[:100].lower()


def get_image_ext(url):
    ext = os.path.splitext(urlparse(url).path)[1].lower()
    return ext if ext in (".jpg", ".jpeg", ".png", ".gif", ".webp") else ".jpg"


def download_image(url, filepath):
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(resp.content)
        return True
    except Exception:
        return False


def save_story(story, index):
    basename = f"{index:04d}-{sanitize_filename(story['title'])}"
    filename = f"{basename}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    img_filename = None
    if story.get("image_url"):
        img_ext = get_image_ext(story["image_url"])
        img_filename = f"{basename}{img_ext}"
        img_path = os.path.join(OUTPUT_DIR, img_filename)
        if not download_image(story["image_url"], img_path):
            img_filename = None

    md = f"# {story['title']}\n\n**Autor:** {story['author']}\n\n**Fuente:** {story['url']}"
    if img_filename:
        md += f"\n\n**Imagen:** {img_filename}"
    md += f"\n\n---\n\n{story['text']}"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md)
    return filepath


def get_next_index():
    existing = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".md")]
    if not existing:
        return 1
    nums = []
    for f in existing:
        try:
            nums.append(int(f.split("-")[0]))
        except ValueError:
            continue
    return max(nums) + 1 if nums else 1


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    scraped = load_scraped()
    print(f"Ya raspados: {len(scraped)} cuentos")

    print("Obteniendo URLs del sitemap...")
    sitemap_urls = get_story_urls_from_sitemaps()
    print(f"  Sitemap: {len(sitemap_urls)} URLs unicas")

    print("Rastreando paginas de listado...")
    page_urls = get_story_urls_from_pages()
    print(f"  Paginas: {len(page_urls)} URLs encontradas")

    all_urls = sitemap_urls | page_urls
    print(f"  Total unico: {len(all_urls)}")

    new_urls = [u for u in all_urls if u not in scraped]
    print(f"Cuentos nuevos: {len(new_urls)}")

    if not new_urls:
        print("No hay cuentos nuevos. Todo actualizado.")
        return

    next_idx = get_next_index()
    saved = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(scrape_story, url): url for url in new_urls}
        for future in as_completed(futures):
            result = future.result()
            if result and result["text"]:
                save_story(result, next_idx + saved)
                scraped.add(result["url"])
                saved += 1
                print(f"[{saved}/{len(new_urls)}] {result['title']}")

    save_scraped(scraped)
    print(f"\nListo! {saved} cuentos nuevos agregados a '{OUTPUT_DIR}/'")


if __name__ == "__main__":
    main()

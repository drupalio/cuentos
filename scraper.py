import requests
import re
import os
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

SITEMAP_URLS = [
    "https://lecturia.org/post-sitemap1.xml",
    "https://lecturia.org/post-sitemap2.xml",
    "https://lecturia.org/post-sitemap3.xml",
]

OUTPUT_DIR = "cuentos"
STATE_FILE = "scraped_urls.json"
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}

session = requests.Session()

def load_scraped():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_scraped(urls):
    with open(STATE_FILE, "w") as f:
        json.dump(sorted(urls), f, indent=2)

def get_story_urls():
    urls = []
    for sitemap_url in SITEMAP_URLS:
        resp = session.get(sitemap_url, timeout=30)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        for url_elem in root.findall("s:url", NS):
            loc = url_elem.find("s:loc", NS).text
            path = urlparse(loc).path
            if "/cuentos-y-relatos/" in path and not path.startswith("/en/") and not path.startswith("/fr/"):
                urls.append(loc)
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
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if "author" in data:
                        a = data["author"]
                        author = a.get("name", a) if isinstance(a, dict) else str(a)
                    elif "@graph" in data:
                        for item in data["@graph"]:
                            if "author" in item:
                                a = item["author"]
                                author = a.get("name", a) if isinstance(a, dict) else str(a)
                                break
            except Exception:
                pass
        if author == "Desconocido":
            author_tag = soup.select_one('a[rel="author"]') or soup.select_one('.author-name')
            if author_tag:
                author = author_tag.get_text(strip=True)

        content_div = soup.find("div", class_="entry-content")
        if not content_div:
            content_div = soup.find("article")

        if content_div:
            for tag in content_div.find_all(["script", "style", "nav", "aside", "footer"]):
                tag.decompose()
            paras = content_div.find_all("p")
            text_parts = [p.get_text(strip=True) for p in paras if p.get_text(strip=True)]
            story_text = "\n\n".join(text_parts)
        else:
            story_text = ""

        return {"title": title, "author": author, "url": url, "text": story_text}
    except Exception as e:
        return None

def sanitize_filename(name):
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', '-', name)
    return name[:100].lower()

def save_story(story, index):
    filename = f"{index:04d}-{sanitize_filename(story['title'])}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    md = f"# {story['title']}\n\n**Autor:** {story['author']}\n\n**Fuente:** {story['url']}\n\n---\n\n{story['text']}"
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
    all_urls = get_story_urls()
    print(f"Total en sitemap: {len(all_urls)}")

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

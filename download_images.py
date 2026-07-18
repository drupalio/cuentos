import os
import re
import glob
import concurrent.futures
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

MD_DIR = "cuentos"
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; CuentosBot/1.0)"})

def get_image_url(story_url):
    try:
        resp = session.get(story_url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        og_image = soup.find("meta", property="og:image")
        if og_image:
            return og_image.get("content")
    except Exception:
        pass
    return None

def download_image(url, filepath):
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(resp.content)
        return True
    except Exception:
        return False

def get_img_ext(url):
    ext = os.path.splitext(urlparse(url).path)[1].lower()
    return ext if ext in (".jpg", ".jpeg", ".png", ".gif", ".webp") else ".jpg"

def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    if "**Imagen:**" in text:
        return None

    match = re.search(r'\*\*Fuente:\*\*\s*(.+?)(?:\n|$)', text)
    if not match:
        return None

    story_url = match.group(1).strip()
    basename = os.path.splitext(os.path.basename(filepath))[0]

    img_url = get_image_url(story_url)
    if not img_url:
        return None

    ext = get_img_ext(img_url)
    img_filename = f"{basename}{ext}"
    img_path = os.path.join(MD_DIR, img_filename)

    if not download_image(img_url, img_path):
        return None

    sep = text.find("\n---")
    if sep == -1:
        os.remove(img_path)
        return None

    new_text = text[:sep] + f"\n\n**Imagen:** {img_filename}" + text[sep:]
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_text)

    return img_filename

def main():
    files = sorted(glob.glob(os.path.join(MD_DIR, "*.md")))
    print(f"Total archivos: {len(files)}")

    to_process = []
    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            first_lines = f.read(500)
        if "**Imagen:**" not in first_lines:
            to_process.append(fpath)

    print(f"Archivos sin imagen: {len(to_process)}")

    if not to_process:
        print("Todos los cuentos ya tienen imagen.")
        return

    success = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_file, fpath): fpath for fpath in to_process}
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            result = future.result()
            fpath = futures[future]
            if result:
                success += 1
                print(f"[{i}/{len(to_process)}] {os.path.basename(fpath)} -> {result}")
            else:
                print(f"[{i}/{len(to_process)}] {os.path.basename(fpath)} -> SIN IMAGEN")

    print(f"\nListo! {success} imágenes descargadas de {len(to_process)}")

if __name__ == "__main__":
    main()

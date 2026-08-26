import os
import re
import json
import shutil

CUENTOS_DIR = os.path.join(os.path.dirname(__file__), "cuentos")
WEB_PUBLIC = os.path.join(os.path.dirname(__file__), "web", "public")
OUTPUT = os.path.join(WEB_PUBLIC, "cuentos.json")
IMAGES_OUTPUT = os.path.join(WEB_PUBLIC, "images")


def parse_story(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    basename = os.path.basename(filepath)
    slug = basename.replace(".md", "")

    lines = text.split("\n")
    title = ""
    author = ""
    source = ""
    image = ""
    content_start = 0

    for i, line in enumerate(lines):
        if line.startswith("# ") and not title:
            title = line.lstrip("# ").strip()
        elif line.startswith("**Autor:**"):
            author = line.replace("**Autor:**", "").strip()
        elif line.startswith("**Fuente:**"):
            source = line.replace("**Fuente:**", "").strip()
        elif line.startswith("**Imagen:**"):
            image = line.replace("**Imagen:**", "").strip()
        elif line.strip() == "---" and content_start == 0:
            content_start = i + 1

    body = "\n".join(lines[content_start:]).strip()
    body = re.sub(r"\n{3,}", "\n\n", body)

    num = int(slug.split("-")[0]) if slug.split("-")[0].isdigit() else 0

    return {
        "slug": slug,
        "num": num,
        "title": title,
        "author": author,
        "source": source,
        "image": image,
        "excerpt": body[:300].strip() + "..." if len(body) > 300 else body,
        "body": body,
    }


def main():
    os.makedirs(IMAGES_OUTPUT, exist_ok=True)

    files = sorted(
        [f for f in os.listdir(CUENTOS_DIR) if f.endswith(".md")],
        key=lambda x: int(x.split("-")[0]) if x.split("-")[0].isdigit() else 0,
    )

    stories = []
    for fname in files:
        fpath = os.path.join(CUENTOS_DIR, fname)
        story = parse_story(fpath)
        stories.append(story)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(stories, f, ensure_ascii=False, indent=2)

    copied = 0
    for fname in os.listdir(CUENTOS_DIR):
        if fname.endswith((".jpg", ".jpeg", ".png", ".webp")):
            src = os.path.join(CUENTOS_DIR, fname)
            dst = os.path.join(IMAGES_OUTPUT, fname)
            if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
                shutil.copy2(src, dst)
                copied += 1

    print(f"Generados {len(stories)} cuentos en {OUTPUT}")
    print(f"Imágenes: {copied} actualizadas en {IMAGES_OUTPUT}/")


if __name__ == "__main__":
    main()

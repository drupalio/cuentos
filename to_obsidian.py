import os
import re
import glob
import shutil
from collections import defaultdict

SOURCE_DIR = "cuentos"
VAULT_DIR = "obsidian-vault"
CUENTOS_OUT = os.path.join(VAULT_DIR, "Cuentos")
AUTORES_OUT = os.path.join(VAULT_DIR, "Autores")

author_stories = defaultdict(list)

def escape_yaml(s):
    if not s:
        return '""'
    s = str(s)
    if any(c in s for c in '":,\n[]{}'):
        return "'" + s.replace("'", "''") + "'"
    return '"' + s + '"'

NOT_AUTHOR_PREFIXES = ("El ", "La ", "Los ", "Las ", "Un ", "Una ", "Lo ")

def looks_like_author(name):
    name = name.strip()
    if not name or len(name) < 3:
        return False
    if name.startswith(NOT_AUTHOR_PREFIXES):
        return False
    if name.lower() in ("sinopsis", "cuento", "relato", "introducción", "feathertop"):
        return False
    parts = name.split()
    if len(parts) == 1 and len(name) > 20:
        return False
    return True

def extract_original_author(title, body):
    m = re.match(r'^(.+?):\s*(.*)', title)
    if m:
        candidate = m.group(1).strip()
        rest = m.group(2).strip()
        if rest and rest[0].islower():
            return None, title
        if looks_like_author(candidate):
            return candidate, rest
    m = re.search(r'^([^(\n]+?)\(Cuento completo\)', body, re.MULTILINE)
    if m:
        author = m.group(1).strip()
        if author and looks_like_author(author):
            return author, title
    return None, title

def parse_story(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    basename = os.path.basename(filepath)
    lines = text.split("\n")

    raw_title = ""
    blog_author = ""
    fuente = ""
    imagen = ""
    content_start = 0

    for i, line in enumerate(lines):
        if line.startswith("# ") and not raw_title:
            raw_title = line.lstrip("# ").strip()
        elif line.startswith("**Autor:**"):
            blog_author = line.replace("**Autor:**", "").strip()
        elif line.startswith("**Fuente:**"):
            fuente = line.replace("**Fuente:**", "").strip()
        elif line.startswith("**Imagen:**"):
            imagen = line.replace("**Imagen:**", "").strip()
        elif line.strip() == "---" and content_start == 0:
            content_start = i + 1

    body_lines = lines[content_start:]
    body = "\n".join(body_lines).strip()
    body = re.sub(r'\n{3,}', '\n\n', body)

    orig_author, clean_title = extract_original_author(raw_title, body)
    author = orig_author or blog_author or "Desconocido"

    return {
        "filename": basename,
        "title": clean_title or raw_title or basename.replace(".md", ""),
        "author": author,
        "source": fuente,
        "image": imagen,
        "body": body,
    }

def build_frontmatter(data):
    lines = ["---"]
    lines.append(f"title: {escape_yaml(data['title'])}")
    lines.append(f"author: {escape_yaml(data['author'])}")
    lines.append(f'source: {escape_yaml(data["source"])}')
    if data["image"]:
        lines.append(f'image: {escape_yaml(data["image"])}')
    lines.append("tags:")
    lines.append("  - cuento")
    author_tag = re.sub(r'[^\w\s-]', '', data['author']).strip().lower()
    author_tag = re.sub(r'[\s-]+', '-', author_tag)[:60]
    lines.append(f'  - autor/{author_tag}')
    lines.append("---")
    return "\n".join(lines)

def build_story_content(data):
    front = build_frontmatter(data)
    body = data["body"]
    return f"{front}\n\n# {data['title']}\n\n{body}"

def build_author_page(author, stories):
    tag = re.sub(r'[^\w\s-]', '', author).strip().lower()
    tag = re.sub(r'[\s-]+', '-', tag)[:60]

    lines = ["---"]
    lines.append(f"title: {escape_yaml(author)}")
    lines.append("tags:")
    lines.append("  - autor")
    lines.append(f"  - autor/{tag}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {author}")
    lines.append("")
    lines.append("## Cuentos")
    lines.append("")

    for s in sorted(stories, key=lambda x: x["title"].lower()):
        link_name = s["filename"].replace(".md", "")
        lines.append(f'- [[{link_name}|{s["title"]}]]')

    lines.append("")
    return "\n".join(lines)

def main():
    if os.path.exists(VAULT_DIR):
        shutil.rmtree(VAULT_DIR)
    os.makedirs(CUENTOS_OUT, exist_ok=True)
    os.makedirs(AUTORES_OUT, exist_ok=True)

    files = sorted(glob.glob(os.path.join(SOURCE_DIR, "*.md")))
    print(f"Procesando {len(files)} cuentos...")

    for fpath in files:
        story = parse_story(fpath)
        content = build_story_content(story)

        out_path = os.path.join(CUENTOS_OUT, story["filename"])
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        author_stories[story["author"]].append(story)

        if story["image"]:
            src_img = os.path.join(SOURCE_DIR, story["image"])
            if os.path.exists(src_img):
                dst_img = os.path.join(CUENTOS_OUT, story["image"])
                shutil.copy2(src_img, dst_img)

    for author, stories in sorted(author_stories.items()):
        page = build_author_page(author, stories)
        filename = re.sub(r'[^\w\s-]', '', author).strip().lower()
        filename = re.sub(r'[\s-]+', '-', filename)[:80] + ".md"
        out_path = os.path.join(AUTORES_OUT, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(page)

    print(f"\nVault creado en '{VAULT_DIR}/'")
    print(f"  Cuentos: {len(files)}")
    print(f"  Autores: {len(author_stories)}")
    print(f"\nAbre '{VAULT_DIR}' como una carpeta en Obsidian.")

if __name__ == "__main__":
    main()

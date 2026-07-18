import os
import re
import glob
from ebooklib import epub
import html

MD_DIR = "cuentos"
OUTPUT = "cuentos_lecturia.epub"

STYLE = """
body { font-family: 'Georgia', serif; line-height: 1.6; margin: 1em 2em; font-size: 1em; }
h1 { text-align: center; font-size: 1.6em; margin-bottom: 0.5em; }
p { text-indent: 1.5em; margin: 0.3em 0; text-align: justify; }
hr { margin: 1.5em 0; }
em { font-style: italic; }
strong { font-weight: bold; }
"""

def md_to_html(text):
    lines = text.split("\n")
    parts = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        line = html.escape(line)
        line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
        line = re.sub(r'\*(.+?)\*', r'<em>\1</em>', line)
        parts.append(f"<p>{line}</p>")
    return "\n".join(parts)

def build_epub():
    files = sorted(glob.glob(os.path.join(MD_DIR, "*.md")))
    if not files:
        print("No hay archivos .md en", MD_DIR)
        return

    book = epub.EpubBook()
    book.set_identifier("lecturia-cuentos-2026")
    book.set_title("Cuentos de Lecturia")
    book.set_language("es")
    book.add_author("Varios autores")

    spine = ["nav"]
    toc = []
    errors = []

    for i, fpath in enumerate(files):
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()

        lines = text.split("\n")
        title = "Sin titulo"
        author = ""
        content_start = 0

        for line in lines:
            if line.startswith("# ") and title == "Sin titulo":
                title = line.lstrip("# ").strip()
            elif line.startswith("**Autor:**"):
                author = line.replace("**Autor:**", "").strip()
            elif line.startswith("---") and content_start == 0:
                content_start = lines.index(line) + 1

        body = "\n".join(lines[content_start:]).strip()
        body_html = md_to_html(body) or "<p><em>(Sin contenido)</em></p>"

        author_html = f'<p style="text-align:center"><em>-- {html.escape(author)} --</em></p>' if author else ""

        ch = epub.EpubHtml(title=title, file_name=f"cap_{i+1:04d}.xhtml", lang="es")
        ch.content = f"""<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{html.escape(title)}</title><style>{STYLE}</style></head>
<body>
<h1>{html.escape(title)}</h1>
{author_html}
<hr/>
{body_html}
</body>
</html>""".encode("utf-8")

        try:
            book.add_item(ch)
            spine.append(ch)
            toc.append(epub.Link(f"cap_{i+1:04d}.xhtml", title, f"cap_{i+1:04d}"))
        except Exception as e:
            errors.append((fpath, str(e)))

    book.toc = toc
    book.spine = spine
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(OUTPUT, book)
    print(f"EPUB regenerado: {OUTPUT} ({os.path.getsize(OUTPUT)/1024/1024:.1f} MB, {len(files)} cuentos)")
    if errors:
        print(f"Errores: {len(errors)}")

if __name__ == "__main__":
    build_epub()

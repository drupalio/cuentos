#!/bin/bash
set -e

cd "$(dirname "$0")"

# Load nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

echo "=== 1. Descargando cuentos nuevos ==="
python3 scraper.py

echo -e "\n=== 2. Descargando imágenes faltantes ==="
python3 download_images.py

echo -e "\n=== 3. Actualizando vault de Obsidian ==="
python3 to_obsidian.py

echo -e "\n=== 4. Regenerando EPUB ==="
python3 build_epub.py

echo -e "\n=== 5. Generando datos para la web ==="
python3 generate_site_data.py

echo -e "\n=== 6. Construyendo la web ==="
cd web
npm run generate
cd ..

echo -e "\n=== 7. Commiteando cambios ==="
git add -A
if git diff --cached --quiet; then
    echo "No hay cambios para commitear."
else
    COUNT=$(git diff --cached --numstat | wc -l)
    git commit -m "update: ${COUNT} archivos actualizados"
    echo "Commit realizado."
fi

echo -e "\n=== Listo ==="
git status --short

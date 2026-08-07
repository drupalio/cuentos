import os
import re
import time
import sys
import json
import requests

PROMPTS_DIR = "historias_nuevas"
OUTPUT_DIR = "portadas"
API_URL = "https://orchestration.civitai.com/v2/consumer/workflows"
API_TOKEN = os.environ.get("CIVITAI_API_KEY")

WIDTH = 1024
HEIGHT = 1536

if not API_TOKEN:
    print("ERROR: CIVITAI_API_KEY no esta definida")
    print("Exportala con: export CIVITAI_API_KEY=tu_token")
    sys.exit(1)

session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
})

def parse_prompt(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    main_match = re.search(r'MAIN PROMPT:\s*(.*?)(?:\n\n|\Z)', text, re.DOTALL)
    neg_match = re.search(r'NEGATIVE PROMPT:\s*(.*?)(?:\n\n|\Z)', text, re.DOTALL)

    prompt = main_match.group(1).strip() if main_match else ""
    negative = neg_match.group(1).strip() if neg_match else ""

    prompt = prompt.replace("\n", ", ")
    prompt = re.sub(r'\s+', ' ', prompt).strip()
    negative = negative.replace("\n", ", ")
    negative = re.sub(r'\s+', ' ', negative).strip()
    prompt = re.sub(r'--ar\s+\S+', '', prompt).strip()
    prompt = re.sub(r'--style\s+\S+', '', prompt).strip()
    prompt = re.sub(r'--s\s+\S+', '', prompt).strip()
    prompt = re.sub(r'--v\s+\S+', '', prompt).strip()
    prompt = re.sub(r'\s{2,}', ' ', prompt).strip()
    prompt = prompt[:1000]

    return prompt, negative

def generate_image(prompt, negative, story_name):
    payload = {
        "steps": [{
            "$type": "imageGen",
            "input": {
                "engine": "flux2",
                "model": "klein",
                "modelVersion": "4b",
                "operation": "createImage",
                "prompt": prompt,
                "negativePrompt": negative,
                "width": WIDTH,
                "height": HEIGHT,
                "cfgScale": 5,
                "steps": 20,
                "quantity": 1,
                "outputFormat": "png",
            }
        }]
    }

    print(f"  Enviando a CivitAI...")
    resp = session.post(f"{API_URL}?wait=60", json=payload)

    if resp.status_code == 402:
        data = resp.json()
        print(f"  ERROR: Buzz insuficiente. Costo: {data.get('cost', '?')} buzz")
        return None

    if resp.status_code == 400:
        print(f"  ERROR 400: {resp.text[:500]}")
        return None

    if resp.status_code == 429:
        print(f"  ERROR 429: Rate limit. Esperando...")
        return None

    resp.raise_for_status()
    result = resp.json()

    step = result.get("steps", [{}])[0]
    status = step.get("status", "unknown")

    if status == "succeeded":
        images = step.get("output", {}).get("images", [])
        if images:
            img_url = images[0].get("url")
            if img_url:
                return download_image(img_url, story_name)

    if status == "failed":
        reason = step.get("reason", step.get("error", "unknown"))
        print(f"  ERROR: Fallo - {reason}")
        return None

    workflow_id = result.get("id")
    if workflow_id:
        return poll_workflow(workflow_id, story_name)

    print(f"  ERROR: Sin workflow id ni resultado")
    return None

def poll_workflow(workflow_id, story_name):
    poll_url = f"{API_URL}/{workflow_id}"
    for i in range(30):
        time.sleep(5)
        resp = session.get(poll_url)
        resp.raise_for_status()
        result = resp.json()

        status = result.get("status", "in_progress")
        if status == "succeeded":
            step = result.get("steps", [{}])[0]
            images = step.get("output", {}).get("images", [])
            if images:
                img_url = images[0].get("url")
                if img_url:
                    return download_image(img_url, story_name)
            return None
        elif status == "failed":
            print(f"  ERROR: Workflow fallo")
            return None

        if i % 6 == 0:
            print(f"  Esperando... ({i * 5}s)")

    print(f"  ERROR: Timeout esperando el workflow")
    return None

def download_image(url, story_name):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ext = "png"
    filename = f"{story_name}.{ext}"
    filepath = os.path.join(OUTPUT_DIR, filename)

    resp = session.get(url)
    resp.raise_for_status()

    with open(filepath, "wb") as f:
        f.write(resp.content)

    print(f"  Imagen guardada: {filepath}")
    return filepath

def main():
    txt_files = sorted([
        f for f in os.listdir(PROMPTS_DIR)
        if f.endswith(".txt")
    ])

    if not txt_files:
        print(f"No hay archivos .txt en '{PROMPTS_DIR}/'")
        return

    print(f"Generando {len(txt_files)} portadas...\n")

    for txt_file in txt_files:
        story_name = txt_file.replace(".txt", "")
        filepath = os.path.join(PROMPTS_DIR, txt_file)

        print(f"[{story_name}]")
        prompt, negative = parse_prompt(filepath)
        print(f"  Prompt: {len(prompt)} chars")

        result = generate_image(prompt, negative, story_name)
        if result:
            print(f"  OK\n")
        else:
            print(f"  FALLIDO\n")

if __name__ == "__main__":
    main()

"""
Разовый скрипт: читает tmp/photos_manifest.json и создаёт ACModelPhoto для моделей
без фото. Идемпотентен (если у модели уже есть photos — пропускает).

Запуск из backend/:
    DJANGO_SETTINGS_MODULE=config.settings.development ./venv/bin/python ../tmp/fetch_photos.py
"""
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import django  # noqa: E402
import requests  # noqa: E402

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.core.files.base import ContentFile  # noqa: E402

from catalog.models import ACModel, ACModelPhoto  # noqa: E402

MANIFEST = Path(__file__).parent / "photos_manifest.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"}
KINDS = [
    ("indoor", 1, "Внутренний блок"),
    ("outdoor", 2, "Наружный блок"),
    ("remote", 3, "Пульт ДУ"),
]


def ext_from_url(url: str) -> str:
    path = urlparse(url).path.lower()
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        if path.endswith(ext):
            return ext
    return ".jpg"


def download(url: str, source: str) -> bytes | None:
    try:
        r = requests.get(url, headers={**HEADERS, "Referer": source}, timeout=20)
    except Exception as exc:
        print(f"    ERROR network: {exc}")
        return None
    if r.status_code != 200:
        print(f"    ERROR http {r.status_code}")
        return None
    ct = r.headers.get("Content-Type", "")
    if not ct.startswith("image/"):
        print(f"    ERROR not image: Content-Type={ct}")
        return None
    if len(r.content) < 5 * 1024:
        print(f"    ERROR too small: {len(r.content)} bytes")
        return None
    return r.content


def main() -> int:
    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))
    models_done = 0
    photos_added = 0
    skipped_existing = 0
    skipped_empty = 0
    errors = 0

    for entry in entries:
        slug = entry["slug"]
        print(f"\n[{slug}]")

        try:
            model = ACModel.objects.get(slug=slug)
        except ACModel.DoesNotExist:
            print("  ERROR model not found")
            errors += 1
            continue

        if model.photos.exists():
            print(f"  SKIP already has {model.photos.count()} photos")
            skipped_existing += 1
            continue

        picks = [(k, o, a) for k, o, a in KINDS if entry.get(k)]
        if not picks:
            print("  SKIP no URLs in manifest")
            skipped_empty += 1
            continue

        added_here = 0
        for key, order, alt in picks:
            src = entry[key]
            url = src["url"]
            source = src.get("source", "")
            print(f"  [{key} order={order}] {url}")
            blob = download(url, source)
            if blob is None:
                errors += 1
                continue
            photo = ACModelPhoto(model=model, order=order, alt=alt)
            filename = f"{slug}-{order}{ext_from_url(url)}"
            photo.image.save(filename, ContentFile(blob), save=True)
            print(f"    OK saved → {photo.image.name} ({len(blob)} bytes)")
            photos_added += 1
            added_here += 1

        if added_here:
            models_done += 1

    print("\n=== SUMMARY ===")
    print(f"models processed: {models_done}")
    print(f"photos added:     {photos_added}")
    print(f"skipped (had photos): {skipped_existing}")
    print(f"skipped (empty manifest entry): {skipped_empty}")
    print(f"errors: {errors}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

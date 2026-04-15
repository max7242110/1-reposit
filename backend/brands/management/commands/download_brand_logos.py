"""Скачать логотипы брендов по URL и сохранить в Brand.logo.

По умолчанию обрабатывает только бренды с пустым логотипом.
URL-ы собраны из Wikimedia, официальных сайтов брендов и каталогов дилеров.

Использование:
    python manage.py download_brand_logos --dry-run
    python manage.py download_brand_logos
    python manage.py download_brand_logos --only AQUA
    python manage.py download_brand_logos --force   # перезаписать существующие
"""
from __future__ import annotations

import mimetypes
import subprocess
import tempfile

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from brands.models import Brand


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


# brand.name (как в БД) → URL к логотипу
LOGOS: dict[str, str] = {
    "AQUA": "https://pro-komfort.com/wa-data/public/shop/plugins/brand/brand_image/AQUA_Br_Blue.png",
    "AUX": "https://pro-komfort.com/wa-data/public/shop/plugins/brand/brand_image/11969.png",
    "CENTEK": "https://pro-komfort.com/wa-data/public/shop/plugins/brand/brand_image/centekairlogo_560x560.png",
    "Coolberg": "https://coolberg.pro/images/logo.png",
    "Energolux": "https://energolux.ru.com/local/templates/energolux/img/logo.png",
    "FeRRUM": "https://pro-komfort.com/wa-data/public/shop/plugins/brand/brand_image/logo609ccca3e764a.png",
    "Haier": "https://pro-komfort.com/wa-data/public/shop/plugins/brand/brand_image/111.png",
    "JAX": "https://www.jac.ru/include/retina_just_logo.png",
    "Just Aircon": "https://pro-komfort.com/wa-data/public/shop/plugins/brand/brand_image/6yf30bl95otl1785bjbwfbhu2hcl91j7.png",
    "Kalashnikov": "https://kalashnikov-climate.com/local/templates/tx/images/logo_md.png",
    "KEG": "https://s.alicdn.com/@img/tfs/TB1Ay1AVUz1gK0jSZLeXXb9kVXa-196-80.png",
    "Rovex": "https://pro-komfort.com/wa-data/public/shop/plugins/brand/brand_image/124.png",
    "Royal Clima": "https://pro-komfort.com/wa-data/public/shop/plugins/brand/brand_image/ROYALClima_logo_vertical5ffd94687b508.png",
    "THAICON": "https://ezk.kz/upload/iblock/87e/9goh12i7t746rwghqwh7f6ean7i27bus.png",
    "ULTIMACOMFORT": "https://pro-komfort.com/wa-data/public/shop/plugins/brand/brand_image/Logo_Ultima_comfort_color_280px.png",
    "Viomi": "https://pro-komfort.com/wa-data/public/shop/plugins/brand/brand_image/Bezymyannyy649145c89921a.jpg",
    "CASARTE": "https://pro-komfort.com/wa-data/public/shop/plugins/brand/brand_image/162b9afa539bab.png",
}


def _infer_extension(url: str, content_type: str | None) -> str:
    """Определить расширение файла по URL или Content-Type."""
    # Сначала — из URL (до query-string)
    path = url.split("?", 1)[0].lower()
    for ext in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"):
        if path.endswith(ext):
            return ".jpg" if ext == ".jpeg" else ext

    # Потом — из Content-Type
    if content_type:
        ext = mimetypes.guess_extension(content_type.split(";")[0].strip())
        if ext:
            return ".jpg" if ext == ".jpeg" else ext

    return ".png"


def _fetch(url: str) -> tuple[bytes, str]:
    """Скачать файл через curl, вернуть (содержимое, расширение).

    Используем curl, а не urllib — у python на macOS хронические проблемы
    с SSL-сертификатами в системном Python без установленного certifi.
    """
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # -L = follow redirects, -f = fail on 4xx/5xx, -sS = silent but show errors,
        # -D <file> = write response headers (нужны для Content-Type), -o = output body
        header_path = tmp_path + ".h"
        result = subprocess.run(
            [
                "curl", "-fsSL",
                "-A", USER_AGENT,
                "-D", header_path,
                "-o", tmp_path,
                "--max-time", "30",
                url,
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or f"curl exit {result.returncode}")

        with open(tmp_path, "rb") as f:
            data = f.read()
        content_type = ""
        try:
            with open(header_path) as f:
                for line in f:
                    if line.lower().startswith("content-type:"):
                        content_type = line.split(":", 1)[1].strip()
        except FileNotFoundError:
            pass
    finally:
        for p in (tmp_path, tmp_path + ".h"):
            try:
                import os
                os.unlink(p)
            except FileNotFoundError:
                pass

    ext = _infer_extension(url, content_type)
    return data, ext


class Command(BaseCommand):
    help = "Скачать и сохранить логотипы брендов"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Не сохранять, только показать")
        parser.add_argument("--only", type=str, default=None, help="Один бренд по name")
        parser.add_argument("--force", action="store_true", help="Перезаписать существующие")

    def handle(self, *args, **options):
        dry_run: bool = options["dry_run"]
        only: str | None = options["only"]
        force: bool = options["force"]

        saved = 0
        skipped = 0
        failed = 0
        missing_brand = 0

        for brand_name, url in LOGOS.items():
            if only and only != brand_name:
                continue

            try:
                brand = Brand.objects.get(name=brand_name)
            except Brand.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"MISS  {brand_name}  (нет в БД)"))
                missing_brand += 1
                continue

            if brand.logo and not force:
                self.stdout.write(self.style.WARNING(f"SKIP  {brand_name}  (уже есть: {brand.logo.name})"))
                skipped += 1
                continue

            try:
                data, ext = _fetch(url)
            except Exception as e:  # noqa: BLE001
                self.stdout.write(self.style.ERROR(f"FAIL  {brand_name}  {url} — {e}"))
                failed += 1
                continue

            size_kb = len(data) / 1024
            slug = brand_name.lower().replace(" ", "_").replace("/", "_")
            filename = f"{slug}{ext}"

            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"OK    {brand_name:<15} → brands/{filename}  ({size_kb:.1f} KB) [DRY-RUN]"
                    )
                )
                saved += 1
                continue

            brand.logo.save(filename, ContentFile(data), save=True)
            self.stdout.write(
                self.style.SUCCESS(
                    f"OK    {brand_name:<15} → {brand.logo.name}  ({size_kb:.1f} KB)"
                )
            )
            saved += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Итого: saved={saved}, skipped={skipped}, failed={failed}, "
                f"missing_brand={missing_brand}{' (DRY-RUN)' if dry_run else ''}"
            )
        )
        if failed or missing_brand:
            self.stdout.write(self.style.WARNING("Есть ошибки — проверь вывод выше."))

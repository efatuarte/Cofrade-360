"""A2: Generador de dataset normalizado de hermandades con provenance.

- Recorre HERMANDADES_SEVILLA_WEBS agrupadas por DAY_BLOCKS.
- Intenta extraer metadatos básicos desde cada web oficial (title, og:title, og:image).
- Genera un JSON normalizado reproducible en backend/app/db/ingestion/hermandades_dataset.normalized.json
"""

from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.db.ingestion.hermandades_sources import DAY_BLOCKS, HERMANDADES_SEVILLA_WEBS

OUTPUT_PATH = Path(__file__).resolve().parent / "hermandades_dataset.normalized.json"

USER_AGENT = (
    "Mozilla/5.0 (compatible; Cofrade360IngestionBot/1.0; "
    "+https://github.com/example/cofrade360)"
)

TIMEOUT_SECONDS = 12
MAX_WORKERS = 8


@dataclass
class FetchResult:
    url: str
    status_code: Optional[int]
    title: Optional[str]
    og_title: Optional[str]
    og_image: Optional[str]
    description: Optional[str]
    fetched_ok: bool
    error: Optional[str]


def _extract_meta(html: str, prop: str) -> Optional[str]:
    pattern = re.compile(
        rf'<meta[^>]+(?:property|name)=["\']{re.escape(prop)}["\'][^>]+content=["\']([^"\']+)["\']',
        re.IGNORECASE,
    )
    match = pattern.search(html)
    return match.group(1).strip() if match else None


def _extract_title(html: str) -> Optional[str]:
    match = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip()


def _fetch_once(url: str) -> FetchResult:
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "es-ES,es;q=0.9"}
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=TIMEOUT_SECONDS) as response:
            status_code = getattr(response, "status", 200)
            final_url = response.geturl()
            html = response.read(500_000).decode("utf-8", errors="ignore")
        return FetchResult(
            url=final_url,
            status_code=status_code,
            title=_extract_title(html),
            og_title=_extract_meta(html, "og:title"),
            og_image=_extract_meta(html, "og:image"),
            description=_extract_meta(html, "description") or _extract_meta(html, "og:description"),
            fetched_ok=status_code < 400,
            error=None if status_code < 400 else f"HTTP {status_code}",
        )
    except HTTPError as exc:
        return FetchResult(
            url=url,
            status_code=exc.code,
            title=None,
            og_title=None,
            og_image=None,
            description=None,
            fetched_ok=False,
            error=f"HTTP {exc.code}",
        )
    except URLError as exc:
        return FetchResult(
            url=url,
            status_code=None,
            title=None,
            og_title=None,
            og_image=None,
            description=None,
            fetched_ok=False,
            error=str(exc.reason),
        )
    except Exception as exc:  # noqa: BLE001
        return FetchResult(
            url=url,
            status_code=None,
            title=None,
            og_title=None,
            og_image=None,
            description=None,
            fetched_ok=False,
            error=str(exc),
        )


def _fetch_site(url: str) -> FetchResult:
    first = _fetch_once(url)
    if first.fetched_ok:
        return first

    # Fallback: algunos entornos bloquean HTTPS por túnel/proxy.
    if url.startswith("https://"):
        http_url = "http://" + url[len("https://"):]
        second = _fetch_once(http_url)
        if second.fetched_ok:
            return second
        return FetchResult(
            url=first.url,
            status_code=first.status_code,
            title=second.title,
            og_title=second.og_title,
            og_image=second.og_image,
            description=second.description,
            fetched_ok=False,
            error=f"https_error={first.error}; http_error={second.error}",
        )

    return first


def _build_item(name: str, ss_day: str, web_url: str, fetch: FetchResult) -> Dict:
    accessed_at = datetime.now(timezone.utc).isoformat()

    display_name = fetch.og_title or fetch.title or name
    fields_extracted: List[str] = ["name_short", "web_url", "ss_day"]
    if fetch.og_title or fetch.title:
        fields_extracted.append("name_full")
    if fetch.og_image:
        fields_extracted.append("media.logo_url")

    notes = []
    if fetch.error:
        notes.append(f"fetch_error: {fetch.error}")
    if not (fetch.og_title or fetch.title):
        notes.append("manual_review_required:name_full")

    return {
        "name_short": name,
        "name_full": display_name,
        "web_url": web_url,
        "ss_day": ss_day,
        "sede": {
            "temple_name": None,
            "address": None,
            "lat": None,
            "lng": None,
            "needs_geocode": True,
        },
        "titulares": [],
        "media": {
            "logo_url": fetch.og_image,
            "images": [fetch.og_image] if fetch.og_image else [],
        },
        "schedule": {
            "salida": None,
            "carrera_oficial_start": None,
            "carrera_oficial_end": None,
            "recogida": None,
            "itinerary_text": None,
        },
        "provenance": [
            {
                "url": fetch.url,
                "accessed_at": accessed_at,
                "fields_extracted": fields_extracted,
                "status_code": fetch.status_code,
            }
        ],
        "ingestion": {
            "fetched_ok": fetch.fetched_ok,
            "notes": notes,
            "description": fetch.description,
        },
    }


def build_dataset() -> Dict:
    jobs = []
    for day, names in DAY_BLOCKS.items():
        for name in names:
            jobs.append((day, name, HERMANDADES_SEVILLA_WEBS[name]))

    fetched: Dict[str, FetchResult] = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_job = {
            executor.submit(_fetch_site, web_url): (day, name, web_url)
            for day, name, web_url in jobs
        }
        for future in as_completed(future_to_job):
            day, name, web_url = future_to_job[future]
            fetched[f"{day}|{name}"] = future.result()
            print(f"[A2] {day} :: {name} -> done")

    items = []
    for day, names in DAY_BLOCKS.items():
        for name in names:
            web_url = HERMANDADES_SEVILLA_WEBS[name]
            fetch = fetched[f"{day}|{name}"]
            items.append(_build_item(name=name, ss_day=day, web_url=web_url, fetch=fetch))

    ok_count = len([item for item in items if item["ingestion"]["fetched_ok"]])
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "auto-web-scan-a2",
        "total_items": len(items),
        "fetched_ok": ok_count,
        "fetched_error": len(items) - ok_count,
        "items": items,
    }


def main() -> None:
    dataset = build_dataset()
    OUTPUT_PATH.write_text(json.dumps(dataset, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Dataset generado en: {OUTPUT_PATH}")
    print(f"Total: {dataset['total_items']} | OK: {dataset['fetched_ok']} | Error: {dataset['fetched_error']}")


if __name__ == "__main__":
    main()

"""A2: Generador de dataset normalizado de hermandades con provenance.

Estrategia de dos fuentes:
1. Datos curados (hermandades_curated_data.py): sedes, titulares, horarios verificados
2. Web scraping (webs oficiales): name_full (og:title), logo (og:image), description

El script merge ambas fuentes: los datos curados tienen prioridad para campos
estructurales (sede, titulares, schedule). El scraping enriquece con media y name_full
si consigue extraerlos.

Genera: hermandades_dataset.normalized.json (reproducible, idempotente)
"""

from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.db.ingestion.hermandades_curated_data import CURATED_DATA
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
            title=None, og_title=None, og_image=None, description=None,
            fetched_ok=False, error=f"HTTP {exc.code}",
        )
    except URLError as exc:
        return FetchResult(
            url=url, status_code=None,
            title=None, og_title=None, og_image=None, description=None,
            fetched_ok=False, error=str(exc.reason),
        )
    except Exception as exc:  # noqa: BLE001
        return FetchResult(
            url=url, status_code=None,
            title=None, og_title=None, og_image=None, description=None,
            fetched_ok=False, error=str(exc),
        )


def _fetch_site(url: str) -> FetchResult:
    first = _fetch_once(url)
    if first.fetched_ok:
        return first
    if url.startswith("https://"):
        http_url = "http://" + url[len("https://"):]
        second = _fetch_once(http_url)
        if second.fetched_ok:
            return second
        return FetchResult(
            url=first.url, status_code=first.status_code,
            title=second.title, og_title=second.og_title,
            og_image=second.og_image, description=second.description,
            fetched_ok=False,
            error=f"https_error={first.error}; http_error={second.error}",
        )
    return first


def _build_curated_index() -> Dict[str, Dict[str, Any]]:
    """Index curated data by name_short for fast lookup."""
    return {item["name_short"]: item for item in CURATED_DATA}


def _merge_item(
    name: str,
    ss_day: str,
    web_url: str,
    fetch: FetchResult,
    curated: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Merge curated data with web-scraped data. Curated wins for structure."""
    accessed_at = datetime.now(timezone.utc).isoformat()

    # Name: prefer curated name_full, then web og:title/title, then name_short
    if curated:
        name_full = curated.get("name_full") or name
    else:
        name_full = fetch.og_title or fetch.title or name

    # Fields tracking
    fields_extracted: List[str] = ["name_short", "web_url", "ss_day"]
    provenance_sources: List[Dict[str, Any]] = []

    # Curated provenance
    if curated:
        fields_extracted.extend(["name_full", "sede", "titulares", "schedule"])
        provenance_sources.append({
            "url": "curated:hermandades_curated_data.py",
            "accessed_at": accessed_at,
            "fields_extracted": ["name_full", "sede", "titulares", "schedule"],
            "status_code": None,
        })

    # Web provenance
    web_fields: List[str] = ["name_short", "web_url", "ss_day"]
    if fetch.og_title or fetch.title:
        web_fields.append("name_full_web")
    if fetch.og_image:
        web_fields.append("media.logo_url")
    provenance_sources.append({
        "url": fetch.url,
        "accessed_at": accessed_at,
        "fields_extracted": web_fields,
        "status_code": fetch.status_code,
    })

    # Sede: curated or empty
    if curated and curated.get("sede"):
        sede = curated["sede"]
    else:
        sede = {"temple_name": None, "address": None, "lat": None, "lng": None, "needs_geocode": True}

    # Titulares: curated or empty
    titulares = (curated.get("titulares") or []) if curated else []

    # Schedule: curated or empty
    if curated and curated.get("schedule"):
        schedule = curated["schedule"]
    else:
        schedule = {
            "salida": None,
            "carrera_oficial_start": None,
            "carrera_oficial_end": None,
            "recogida": None,
            "itinerary_text": None,
        }

    # Media: web scraping enriches
    logo_url = fetch.og_image
    images = [fetch.og_image] if fetch.og_image else []

    # Notes
    notes: List[str] = []
    if fetch.error:
        notes.append(f"fetch_error: {fetch.error}")
    if not curated:
        notes.append("no_curated_data:manual_review_required")
    if not (fetch.og_title or fetch.title) and not curated:
        notes.append("manual_review_required:name_full")

    return {
        "name_short": name,
        "name_full": name_full,
        "web_url": web_url,
        "ss_day": ss_day,
        "sede": sede,
        "titulares": titulares,
        "media": {"logo_url": logo_url, "images": images},
        "schedule": schedule,
        "provenance": provenance_sources,
        "ingestion": {
            "fetched_ok": fetch.fetched_ok,
            "has_curated_data": curated is not None,
            "notes": notes,
            "description": fetch.description,
        },
    }


def build_dataset(skip_web: bool = False) -> Dict[str, Any]:
    """Build the complete normalized dataset.

    Args:
        skip_web: If True, skip web scraping and use only curated data.
                  Useful for offline/CI environments.
    """
    curated_index = _build_curated_index()

    jobs = []
    for day, names in DAY_BLOCKS.items():
        for name in names:
            jobs.append((day, name, HERMANDADES_SEVILLA_WEBS[name]))

    # Web scraping (optional)
    fetched: Dict[str, FetchResult] = {}
    if not skip_web:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_job = {
                executor.submit(_fetch_site, web_url): (day, name, web_url)
                for day, name, web_url in jobs
            }
            for future in as_completed(future_to_job):
                day, name, web_url = future_to_job[future]
                fetched[f"{day}|{name}"] = future.result()
                print(f"[A2] {day} :: {name} -> done")
    else:
        # Create empty fetch results for all
        for day, name, web_url in jobs:
            fetched[f"{day}|{name}"] = FetchResult(
                url=web_url, status_code=None,
                title=None, og_title=None, og_image=None, description=None,
                fetched_ok=False, error="skipped:skip_web=True",
            )
        print("[A2] Web scraping skipped (--skip-web)")

    # Merge curated + web data
    items = []
    for day, names in DAY_BLOCKS.items():
        for name in names:
            web_url = HERMANDADES_SEVILLA_WEBS[name]
            fetch = fetched[f"{day}|{name}"]
            curated = curated_index.get(name)
            items.append(_merge_item(name=name, ss_day=day, web_url=web_url, fetch=fetch, curated=curated))

    ok_count = len([item for item in items if item["ingestion"]["fetched_ok"]])
    curated_count = len([item for item in items if item["ingestion"]["has_curated_data"]])
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "curated+web-scan-a2",
        "total_items": len(items),
        "curated_items": curated_count,
        "fetched_ok": ok_count,
        "fetched_error": len(items) - ok_count,
        "items": items,
    }


def main() -> None:
    import sys
    skip_web = "--skip-web" in sys.argv
    dataset = build_dataset(skip_web=skip_web)
    OUTPUT_PATH.write_text(json.dumps(dataset, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDataset generado en: {OUTPUT_PATH}")
    print(f"Total: {dataset['total_items']} | Curated: {dataset['curated_items']} | Web OK: {dataset['fetched_ok']} | Web Error: {dataset['fetched_error']}")


if __name__ == "__main__":
    main()

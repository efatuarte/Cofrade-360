"""A3: Full pipeline — build normalized JSON + import to database.

Usage:
    # Build dataset (skip web scraping) and import to DB:
    python -m app.db.ingestion.pipeline --skip-web

    # Build dataset with web scraping and import to DB:
    python -m app.db.ingestion.pipeline

    # Dry run (build JSON but don't import):
    python -m app.db.ingestion.pipeline --skip-web --dry-run

    # Import only (reuse existing JSON):
    python -m app.db.ingestion.pipeline --import-only
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.db.ingestion.build_hermandades_dataset import OUTPUT_PATH, build_dataset
from app.db.ingestion.import_hermandades_dataset import import_dataset
from app.db.session import SessionLocal


def run_pipeline(
    *,
    skip_web: bool = True,
    dry_run: bool = False,
    import_only: bool = False,
) -> dict:
    results: dict = {}

    # Step 1: Build
    if not import_only:
        print("=" * 60)
        print("[Pipeline] Step 1/2 — Building normalized dataset …")
        print("=" * 60)
        dataset = build_dataset(skip_web=skip_web)
        OUTPUT_PATH.write_text(
            json.dumps(dataset, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        results["build"] = {
            "total_items": dataset["total_items"],
            "curated_items": dataset["curated_items"],
            "fetched_ok": dataset["fetched_ok"],
            "output_path": str(OUTPUT_PATH),
        }
        print(
            f"[Pipeline] Dataset: {dataset['total_items']} items "
            f"({dataset['curated_items']} curated, {dataset['fetched_ok']} web OK)"
        )
        print(f"[Pipeline] Written to: {OUTPUT_PATH}")
    else:
        if not OUTPUT_PATH.exists():
            print(f"[Pipeline] ERROR: dataset not found at {OUTPUT_PATH}")
            print("[Pipeline] Run without --import-only first.")
            sys.exit(1)
        print("[Pipeline] Skipping build (--import-only)")

    # Step 2: Import
    if not dry_run:
        print()
        print("=" * 60)
        print("[Pipeline] Step 2/2 — Importing to database …")
        print("=" * 60)
        db = SessionLocal()
        try:
            summary = import_dataset(db, dataset_path=OUTPUT_PATH)
            results["import"] = summary
            print(f"[Pipeline] Import summary:")
            for key, value in summary.items():
                print(f"  {key}: {value}")
        finally:
            db.close()
    else:
        print("\n[Pipeline] Dry run — skipping database import.")
        results["import"] = "skipped (dry-run)"

    print()
    print("=" * 60)
    print("[Pipeline] Done.")
    print("=" * 60)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cofrade-360: Build + import hermandades pipeline"
    )
    parser.add_argument(
        "--skip-web",
        action="store_true",
        help="Skip web scraping, use only curated data",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build JSON only, don't import to DB",
    )
    parser.add_argument(
        "--import-only",
        action="store_true",
        help="Skip build, import existing JSON to DB",
    )
    args = parser.parse_args()

    results = run_pipeline(
        skip_web=args.skip_web,
        dry_run=args.dry_run,
        import_only=args.import_only,
    )
    print(json.dumps(results, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()

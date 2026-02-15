import json
from pathlib import Path

from app.db.ingestion.hermandades_sources import DAY_BLOCKS, HERMANDADES_SEVILLA_WEBS


def test_day_blocks_match_web_dictionary():
    flattened = [name for _, names in DAY_BLOCKS.items() for name in names]
    assert len(flattened) == len(set(flattened))
    assert set(flattened) == set(HERMANDADES_SEVILLA_WEBS.keys())


def test_normalized_dataset_exists_and_has_expected_shape():
    dataset_path = Path(__file__).resolve().parents[1] / "app" / "db" / "ingestion" / "hermandades_dataset.normalized.json"
    assert dataset_path.exists()

    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    assert payload["total_items"] == len(HERMANDADES_SEVILLA_WEBS)
    assert isinstance(payload["items"], list)
    assert len(payload["items"]) == len(HERMANDADES_SEVILLA_WEBS)

    sample = payload["items"][0]
    assert "name_short" in sample
    assert "web_url" in sample
    assert "ss_day" in sample
    assert "provenance" in sample


def test_normalized_dataset_items_have_provenance_and_ingestion_notes():
    dataset_path = Path(__file__).resolve().parents[1] / "app" / "db" / "ingestion" / "hermandades_dataset.normalized.json"
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))

    for item in payload["items"]:
        assert item["provenance"], "each item must have provenance"
        p0 = item["provenance"][0]
        assert "url" in p0
        assert "accessed_at" in p0
        assert "fields_extracted" in p0
        assert isinstance(p0["fields_extracted"], list)

        assert "ingestion" in item
        assert "fetched_ok" in item["ingestion"]
        assert "notes" in item["ingestion"]
        assert isinstance(item["ingestion"]["notes"], list)

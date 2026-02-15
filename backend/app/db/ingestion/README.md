# Ingestion pipeline (A1 → A4)

## Artefactos
- `hermandades_sources.py`: diccionario fuente por día (`DAY_BLOCKS`, `HERMANDADES_SEVILLA_WEBS`).
- `build_hermandades_dataset.py`: genera `hermandades_dataset.normalized.json`.
- `import_hermandades_dataset.py`: importa dataset normalizado a DB de forma idempotente.

## Comandos
```bash
cd backend
python -m app.db.ingestion.build_hermandades_dataset
python -m app.db.ingestion.import_hermandades_dataset
```

## Contrato mínimo por item normalizado
- `name_short`, `name_full`, `web_url`, `ss_day`
- `sede.{temple_name,address,lat,lng,needs_geocode}`
- `media.{logo_url,images[]}`
- `schedule.{salida,carrera_oficial_start,carrera_oficial_end,recogida,itinerary_text}`
- `provenance[]` con `{url, accessed_at, fields_extracted[], status_code}`

## Idempotencia esperada del import
- Hermandad: por `name_short`
- Media: por par `(brotherhood_id, path)`
- Procession: por `(brotherhood_id, date)`
- Provenance: por `(entity_type=brotherhood, entity_id, source_url)`

## Nota de entorno restringido
Si hay bloqueo de salida HTTP/HTTPS, el builder debe dejar evidencia en:
- `ingestion.fetched_ok = false`
- `ingestion.notes[]` (`fetch_error`, `manual_review_required:*`)

Se permite completar manualmente el dataset antes del import, manteniendo siempre `provenance`.

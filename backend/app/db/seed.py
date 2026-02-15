"""
Database seeding script
"""
import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.models import (
    DataProvenance,
    Evento,
    Hermandad,
    Location,
    MediaAsset,
    Procession,
    ProcessionItineraryText,
    ProcessionSchedulePoint,
    ProcessionSegmentOccupation,
    RestrictedArea,
    StreetSegment,
    User,
)


def load_normalized_ingestion_dataset() -> dict:
    """Carga dataset normalizado local para importar en fases A2/A3."""
    dataset_path = Path(__file__).resolve().parent / "ingestion" / "hermandades_dataset.normalized.json"
    if not dataset_path.exists():
        return {"items": []}
    with dataset_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def seed_database():
    db = SessionLocal()

    try:
        if db.query(Hermandad).first():
            print("Database already seeded. Skipping...")
            return

        normalized_dataset = load_normalized_ingestion_dataset()
        print(f"Ingestion dataset items available: {len(normalized_dataset.get('items', []))}")

        users = [
            User(id=str(uuid.uuid4()), email="test@cofrade360.com", hashed_password=get_password_hash("test1234"), role="user", is_active=True),
            User(id=str(uuid.uuid4()), email="editor@cofrade360.com", hashed_password=get_password_hash("test1234"), role="editor", is_active=True),
            User(id=str(uuid.uuid4()), email="admin@cofrade360.com", hashed_password=get_password_hash("test1234"), role="admin", is_active=True),
        ]
        db.add_all(users)
        db.commit()

        locations = [
            Location(id=str(uuid.uuid4()), name="Teatro de la Maestranza", address="Paseo de Cristóbal Colón, 22", lat=37.3838, lng=-5.9971, kind="theater"),
            Location(id=str(uuid.uuid4()), name="Plaza de San Francisco", address="Plaza de San Francisco, s/n", lat=37.3886, lng=-5.9953, kind="plaza"),
            Location(id=str(uuid.uuid4()), name="Catedral de Sevilla", address="Av. de la Constitución, s/n", lat=37.3862, lng=-5.9926, kind="church"),
            Location(id=str(uuid.uuid4()), name="Basílica del Gran Poder", address="Plaza de San Lorenzo, 13", lat=37.3935, lng=-5.9995, kind="church"),
            Location(id=str(uuid.uuid4()), name="Basílica de la Macarena", address="C. Bécquer, 1", lat=37.4008, lng=-5.9900, kind="church"),
            Location(id=str(uuid.uuid4()), name="Capilla del Patrocinio", address="C. Castilla, 182, Triana", lat=37.3835, lng=-6.0055, kind="church"),
            Location(id=str(uuid.uuid4()), name="Iglesia de la Magdalena", address="C. San Pablo, 10", lat=37.3895, lng=-5.9985, kind="church"),
        ]
        db.add_all(locations)
        db.commit()

        hermandades = [
            Hermandad(id=str(uuid.uuid4()), nombre="Hermandad del Gran Poder", descripcion="Real e Ilustre Hermandad", escudo="GP", sede="Basílica del Gran Poder", fecha_fundacion=datetime(1431, 1, 1), name_short="Gran Poder", name_full="Pontificia y Real Hermandad del Gran Poder", church_id=locations[3].id, ss_day="madrugada", history="Devoción histórica", highlights=json.dumps(["Madrugada", "Silencio"]), stats=json.dumps({"nazarenos": 2800, "pasos": 2})),
            Hermandad(id=str(uuid.uuid4()), nombre="Hermandad de la Macarena", descripcion="Hermandad popular", escudo="MC", sede="Basílica de la Macarena", fecha_fundacion=datetime(1595, 1, 1), name_short="Macarena", name_full="Hermandad de la Esperanza Macarena", church_id=locations[4].id, ss_day="madrugada", history="Corporación popular", highlights=json.dumps(["Esperanza", "Arco"]), stats=json.dumps({"nazarenos": 3600, "pasos": 2})),
            Hermandad(id=str(uuid.uuid4()), nombre="Hermandad del Cachorro", descripcion="Hermandad trianera", escudo="CA", sede="Capilla del Patrocinio", fecha_fundacion=datetime(1689, 1, 1), name_short="Cachorro", name_full="Hermandad del Santísimo Cristo de la Expiración", church_id=locations[5].id, ss_day="viernes_santo", history="Icono de Triana", highlights=json.dumps(["Triana", "Puente"]), stats=json.dumps({"nazarenos": 2400, "pasos": 2})),
        ]
        db.add_all(hermandades)
        db.commit()

        media_assets = []
        for h in hermandades:
            logo = MediaAsset(id=str(uuid.uuid4()), kind="image", mime="image/jpeg", path=f"brotherhoods/{h.name_short.lower()}-logo.jpg", brotherhood_id=h.id)
            img1 = MediaAsset(id=str(uuid.uuid4()), kind="image", mime="image/jpeg", path=f"brotherhoods/{h.name_short.lower()}-1.jpg", brotherhood_id=h.id)
            img2 = MediaAsset(id=str(uuid.uuid4()), kind="image", mime="image/jpeg", path=f"brotherhoods/{h.name_short.lower()}-2.jpg", brotherhood_id=h.id)
            media_assets.extend([logo, img1, img2])
            h.logo_asset_id = logo.id
        db.add_all(media_assets)
        db.commit()

        eventos = [
            Evento(id=str(uuid.uuid4()), titulo="Pregón de Semana Santa 2026", descripcion="Pregón oficial", tipo="otro", fecha_inicio=datetime(2026, 4, 3, 20, 0), fecha_fin=datetime(2026, 4, 3, 22, 0), location_id=locations[0].id, es_gratuito=False, precio=15.0, moneda="EUR", poster_asset_id="events/pregon-2026.jpg", estado="programado"),
            Evento(id=str(uuid.uuid4()), titulo="Vía Crucis Magno", descripcion="Vía Crucis", tipo="culto", fecha_inicio=datetime(2026, 4, 4, 18, 0), fecha_fin=datetime(2026, 4, 4, 21, 0), location_id=locations[1].id, hermandad_id=hermandades[1].id, es_gratuito=True, precio=0, poster_asset_id="events/via-crucis-magno.jpg", estado="programado"),
            Evento(id=str(uuid.uuid4()), titulo="Procesión del Silencio – Gran Poder", descripcion="Madrugada", tipo="procesion", fecha_inicio=datetime(2026, 4, 10, 1, 0), fecha_fin=datetime(2026, 4, 10, 7, 30), location_id=locations[3].id, hermandad_id=hermandades[0].id, es_gratuito=True, precio=0, estado="programado"),
            Evento(id=str(uuid.uuid4()), titulo="Salida Procesional La Macarena", descripcion="Madrugada", tipo="procesion", fecha_inicio=datetime(2026, 4, 10, 0, 0), fecha_fin=datetime(2026, 4, 10, 13, 0), location_id=locations[4].id, hermandad_id=hermandades[1].id, es_gratuito=True, precio=0, estado="programado"),
            Evento(id=str(uuid.uuid4()), titulo="Procesión del Cachorro – Viernes Santo", descripcion="Triana", tipo="procesion", fecha_inicio=datetime(2026, 4, 10, 17, 0), fecha_fin=datetime(2026, 4, 11, 1, 30), location_id=locations[5].id, hermandad_id=hermandades[2].id, es_gratuito=True, precio=0, estado="programado"),
            Evento(id=str(uuid.uuid4()), titulo="Besapiés al Señor del Gran Poder", descripcion="Culto", tipo="culto", fecha_inicio=datetime(2026, 4, 5, 8, 0), fecha_fin=datetime(2026, 4, 5, 22, 0), location_id=locations[3].id, hermandad_id=hermandades[0].id, es_gratuito=True, precio=0, estado="programado"),
            Evento(id=str(uuid.uuid4()), titulo="Función Principal – Macarena", descripcion="Función", tipo="culto", fecha_inicio=datetime(2026, 4, 6, 20, 0), fecha_fin=datetime(2026, 4, 6, 21, 30), location_id=locations[4].id, hermandad_id=hermandades[1].id, es_gratuito=True, precio=0, estado="programado"),
            Evento(id=str(uuid.uuid4()), titulo="Concierto de Marchas Procesionales", descripcion="Concierto", tipo="concierto", fecha_inicio=datetime(2026, 4, 7, 20, 30), fecha_fin=datetime(2026, 4, 7, 22, 30), location_id=locations[2].id, es_gratuito=False, precio=10.0, moneda="EUR", poster_asset_id="events/concierto-marchas.jpg", estado="programado"),
            Evento(id=str(uuid.uuid4()), titulo="Traslado al Paso – Cachorro", descripcion="Traslado", tipo="otro", fecha_inicio=datetime(2026, 4, 9, 22, 0), fecha_fin=datetime(2026, 4, 9, 23, 30), location_id=locations[5].id, hermandad_id=hermandades[2].id, es_gratuito=True, precio=0, estado="programado"),
            Evento(id=str(uuid.uuid4()), titulo="Exposición: Bordados de Semana Santa", descripcion="Muestra", tipo="exposicion", fecha_inicio=datetime(2026, 3, 20, 10, 0), fecha_fin=datetime(2026, 4, 12, 20, 0), location_id=locations[6].id, es_gratuito=False, precio=5.0, moneda="EUR", estado="programado"),
        ]
        db.add_all(eventos)
        db.commit()

        # FASE 6 operativo
        street_segments = [
            StreetSegment(id=str(uuid.uuid4()), name=f"Segmento {i+1}", geom=f"LINESTRING(-5.{990+i%7} 37.{380+i%9}, -5.{991+i%7} 37.{381+i%9})", width_estimate=2.5 + (i % 5), kind="street", is_walkable=True)
            for i in range(20)
        ]
        db.add_all(street_segments)
        db.commit()

        base_day = datetime(2026, 4, 10, 0, 0, 0)
        restrictions = [
            RestrictedArea(id=str(uuid.uuid4()), name="Carrera Oficial Centro", geom="POLYGON((-5.996 37.389,-5.992 37.389,-5.992 37.386,-5.996 37.386,-5.996 37.389))", start_datetime=base_day + timedelta(hours=16), end_datetime=base_day + timedelta(hours=23), reason="carrera_oficial"),
            RestrictedArea(id=str(uuid.uuid4()), name="Corte Puente Triana", geom="POLYGON((-6.003 37.386,-6.000 37.386,-6.000 37.383,-6.003 37.383,-6.003 37.386))", start_datetime=base_day + timedelta(hours=18), end_datetime=base_day + timedelta(hours=22), reason="corte"),
            RestrictedArea(id=str(uuid.uuid4()), name="Vallas Campana", geom="POLYGON((-5.998 37.393,-5.995 37.393,-5.995 37.391,-5.998 37.391,-5.998 37.393))", start_datetime=base_day + timedelta(hours=17), end_datetime=base_day + timedelta(hours=21), reason="valla"),
        ]
        db.add_all(restrictions)
        db.commit()

        processions = [
            Procession(id=str(uuid.uuid4()), brotherhood_id=hermandades[0].id, date=base_day + timedelta(hours=1), status="in_progress"),
            Procession(id=str(uuid.uuid4()), brotherhood_id=hermandades[1].id, date=base_day + timedelta(hours=0, minutes=30), status="in_progress"),
        ]
        db.add_all(processions)
        db.commit()

        schedule_points = [
            ProcessionSchedulePoint(
                id=str(uuid.uuid4()),
                procession_id=processions[0].id,
                point_type="salida",
                label="Cruz de Guía",
                scheduled_datetime=base_day + timedelta(hours=1),
            ),
            ProcessionSchedulePoint(
                id=str(uuid.uuid4()),
                procession_id=processions[0].id,
                point_type="recogida",
                label="Entrada templo",
                scheduled_datetime=base_day + timedelta(hours=7, minutes=30),
            ),
        ]
        db.add_all(schedule_points)

        itinerary_texts = [
            ProcessionItineraryText(
                id=str(uuid.uuid4()),
                procession_id=processions[0].id,
                raw_text="Plaza de San Lorenzo, Cardenal Spínola, Campana, Carrera Oficial, regreso a San Lorenzo",
                source_url="seed://synthetic",
                accessed_at=datetime.utcnow(),
            )
        ]
        db.add_all(itinerary_texts)

        provenance_rows = [
            DataProvenance(
                id=str(uuid.uuid4()),
                entity_type="brotherhood",
                entity_id=hermandades[0].id,
                source_url="seed://synthetic",
                accessed_at=datetime.utcnow(),
                fields_extracted=json.dumps(["name_short", "name_full", "ss_day"]),
            )
        ]
        db.add_all(provenance_rows)
        db.commit()

        occupations = []
        for i in range(16):
            occ = ProcessionSegmentOccupation(
                id=str(uuid.uuid4()),
                procession_id=processions[i % 2].id,
                street_segment_id=street_segments[i].id,
                start_datetime=base_day + timedelta(hours=17, minutes=i * 10),
                end_datetime=base_day + timedelta(hours=17, minutes=i * 10 + 8),
                direction="parallel" if i % 3 else "unknown",
                crowd_factor=1.0 + (i % 5) * 0.2,
            )
            occupations.append(occ)
        db.add_all(occupations)
        db.commit()

        print("Database seeded successfully!")
        print(f"   - users: {len(users)}")
        print(f"   - locations: {len(locations)}")
        print(f"   - hermandades: {len(hermandades)}")
        print(f"   - media_assets: {len(media_assets)}")
        print(f"   - eventos: {len(eventos)}")
        print(f"   - street_segments: {len(street_segments)}")
        print(f"   - restrictions: {len(restrictions)}")
        print(f"   - processions: {len(processions)}")
        print(f"   - schedule_points: {len(schedule_points)}")
        print(f"   - itinerary_texts: {len(itinerary_texts)}")
        print(f"   - provenance_rows: {len(provenance_rows)}")
        print(f"   - occupations: {len(occupations)}")

    except Exception as exc:
        print(f"Error seeding database: {exc}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

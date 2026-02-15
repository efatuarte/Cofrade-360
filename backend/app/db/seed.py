"""
Database seeding script
Seeds: test user, locations, 3 brotherhoods, media assets and 10 events
"""
import json
import uuid
from datetime import datetime

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.models import Evento, Hermandad, Location, MediaAsset, User


def seed_database():
    db = SessionLocal()

    try:
        existing = db.query(Hermandad).first()
        if existing:
            print("Database already seeded. Skipping...")
            return

        test_user = User(
            id=str(uuid.uuid4()),
            email="test@cofrade360.com",
            hashed_password=get_password_hash("test1234"),
            is_active=True,
        )
        db.add(test_user)
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
            Hermandad(
                id=str(uuid.uuid4()),
                nombre="Hermandad del Gran Poder",
                descripcion="Real e Ilustre Hermandad y Cofradía de Nazarenos de Nuestro Padre Jesús del Gran Poder",
                escudo="GP",
                sede="Basílica del Gran Poder",
                fecha_fundacion=datetime(1431, 1, 1),
                name_short="Gran Poder",
                name_full="Pontificia y Real Hermandad del Gran Poder",
                church_id=locations[3].id,
                ss_day="madrugada",
                history="Devoción histórica sevillana desde el siglo XV.",
                highlights=json.dumps(["Madrugada", "Silencio", "Gran afluencia"]),
                stats=json.dumps({"nazarenos": 2800, "pasos": 2}),
            ),
            Hermandad(
                id=str(uuid.uuid4()),
                nombre="Hermandad de la Macarena",
                descripcion="Real, Ilustre y Fervorosa Hermandad y Cofradía de Nazarenos",
                escudo="MC",
                sede="Basílica de la Macarena",
                fecha_fundacion=datetime(1595, 1, 1),
                name_short="Macarena",
                name_full="Hermandad de la Esperanza Macarena",
                church_id=locations[4].id,
                ss_day="madrugada",
                history="Una de las corporaciones más populares de Sevilla.",
                highlights=json.dumps(["Madrugada", "Esperanza", "Arco de la Macarena"]),
                stats=json.dumps({"nazarenos": 3600, "pasos": 2}),
            ),
            Hermandad(
                id=str(uuid.uuid4()),
                nombre="Hermandad del Cachorro",
                descripcion="Pontificia, Real e Ilustre Hermandad Sacramental",
                escudo="CA",
                sede="Capilla del Patrocinio (Triana)",
                fecha_fundacion=datetime(1689, 1, 1),
                name_short="Cachorro",
                name_full="Hermandad del Santísimo Cristo de la Expiración",
                church_id=locations[5].id,
                ss_day="viernes_santo",
                history="Icono de Triana y del Viernes Santo sevillano.",
                highlights=json.dumps(["Triana", "Cristo de la Expiración", "Puente"]),
                stats=json.dumps({"nazarenos": 2400, "pasos": 2}),
            ),
        ]
        db.add_all(hermandades)
        db.commit()

        media_assets: list[MediaAsset] = []
        for brotherhood in hermandades:
            logo = MediaAsset(
                id=str(uuid.uuid4()),
                kind="image",
                mime="image/jpeg",
                path=f"brotherhoods/{brotherhood.name_short.lower()}-logo.jpg",
                brotherhood_id=brotherhood.id,
            )
            gallery_1 = MediaAsset(
                id=str(uuid.uuid4()),
                kind="image",
                mime="image/jpeg",
                path=f"brotherhoods/{brotherhood.name_short.lower()}-1.jpg",
                brotherhood_id=brotherhood.id,
            )
            gallery_2 = MediaAsset(
                id=str(uuid.uuid4()),
                kind="image",
                mime="image/jpeg",
                path=f"brotherhoods/{brotherhood.name_short.lower()}-2.jpg",
                brotherhood_id=brotherhood.id,
            )
            media_assets.extend([logo, gallery_1, gallery_2])
            brotherhood.logo_asset_id = logo.id

        db.add_all(media_assets)
        db.commit()

        eventos = [
            Evento(id=str(uuid.uuid4()), titulo="Pregón de Semana Santa 2026", descripcion="Pregón oficial de la Semana Santa de Sevilla.", tipo="otro", fecha_inicio=datetime(2026, 4, 3, 20, 0), fecha_fin=datetime(2026, 4, 3, 22, 0), location_id=locations[0].id, es_gratuito=False, precio=15.0, moneda="EUR", poster_asset_id="events/pregon-2026.jpg", estado="programado"),
            Evento(id=str(uuid.uuid4()), titulo="Vía Crucis Magno", descripcion="Vía Crucis por las calles del centro.", tipo="culto", fecha_inicio=datetime(2026, 4, 4, 18, 0), fecha_fin=datetime(2026, 4, 4, 21, 0), location_id=locations[1].id, hermandad_id=hermandades[1].id, es_gratuito=True, precio=0, poster_asset_id="events/via-crucis-magno.jpg", estado="programado"),
            Evento(id=str(uuid.uuid4()), titulo="Procesión del Silencio – Gran Poder", descripcion="Madrugada del Viernes Santo.", tipo="procesion", fecha_inicio=datetime(2026, 4, 10, 1, 0), fecha_fin=datetime(2026, 4, 10, 7, 30), location_id=locations[3].id, hermandad_id=hermandades[0].id, es_gratuito=True, precio=0, estado="programado"),
            Evento(id=str(uuid.uuid4()), titulo="Salida Procesional La Macarena", descripcion="Salida de la Esperanza Macarena.", tipo="procesion", fecha_inicio=datetime(2026, 4, 10, 0, 0), fecha_fin=datetime(2026, 4, 10, 13, 0), location_id=locations[4].id, hermandad_id=hermandades[1].id, es_gratuito=True, precio=0, estado="programado"),
            Evento(id=str(uuid.uuid4()), titulo="Procesión del Cachorro – Viernes Santo", descripcion="El Cristo de la Expiración cruza Triana.", tipo="procesion", fecha_inicio=datetime(2026, 4, 10, 17, 0), fecha_fin=datetime(2026, 4, 11, 1, 30), location_id=locations[5].id, hermandad_id=hermandades[2].id, es_gratuito=True, precio=0, estado="programado"),
            Evento(id=str(uuid.uuid4()), titulo="Besapiés al Señor del Gran Poder", descripcion="Culto público previo a Semana Santa.", tipo="culto", fecha_inicio=datetime(2026, 4, 5, 8, 0), fecha_fin=datetime(2026, 4, 5, 22, 0), location_id=locations[3].id, hermandad_id=hermandades[0].id, es_gratuito=True, precio=0, estado="programado"),
            Evento(id=str(uuid.uuid4()), titulo="Función Principal – Macarena", descripcion="Función religiosa principal de la hermandad.", tipo="culto", fecha_inicio=datetime(2026, 4, 6, 20, 0), fecha_fin=datetime(2026, 4, 6, 21, 30), location_id=locations[4].id, hermandad_id=hermandades[1].id, es_gratuito=True, precio=0, estado="programado"),
            Evento(id=str(uuid.uuid4()), titulo="Concierto de Marchas Procesionales", descripcion="Interpretación de marchas clásicas.", tipo="concierto", fecha_inicio=datetime(2026, 4, 7, 20, 30), fecha_fin=datetime(2026, 4, 7, 22, 30), location_id=locations[2].id, es_gratuito=False, precio=10.0, moneda="EUR", poster_asset_id="events/concierto-marchas.jpg", estado="programado"),
            Evento(id=str(uuid.uuid4()), titulo="Traslado al Paso – Cachorro", descripcion="Traslado de imágenes al paso.", tipo="otro", fecha_inicio=datetime(2026, 4, 9, 22, 0), fecha_fin=datetime(2026, 4, 9, 23, 30), location_id=locations[5].id, hermandad_id=hermandades[2].id, es_gratuito=True, precio=0, estado="programado"),
            Evento(id=str(uuid.uuid4()), titulo="Exposición: Bordados de Semana Santa", descripcion="Muestra de bordados sevillanos.", tipo="exposicion", fecha_inicio=datetime(2026, 3, 20, 10, 0), fecha_fin=datetime(2026, 4, 12, 20, 0), location_id=locations[6].id, es_gratuito=False, precio=5.0, moneda="EUR", estado="programado"),
        ]
        db.add_all(provenance_rows)
        db.commit()

        db.add_all(eventos)
        db.commit()

        print("Database seeded successfully!")
        print(f"   - {len(locations)} locations")
        print(f"   - {len(hermandades)} hermandades")
        print(f"   - {len(media_assets)} media assets")
        print(f"   - {len(eventos)} eventos")

    except Exception as exc:
        print(f"Error seeding database: {exc}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

"""
Database seeding script
Seeds test user, locations, 3 hermandades and 10 eventos
"""
from datetime import datetime
from app.db.session import SessionLocal
from app.models.models import Hermandad, Evento, User, Location
from app.core.security import get_password_hash
import uuid


def seed_database():
    db = SessionLocal()

    try:
        # Check if already seeded
        existing = db.query(Hermandad).first()
        if existing:
            print("Database already seeded. Skipping...")
            return

        # Seed test user
        test_user = User(
            id=str(uuid.uuid4()),
            email="test@cofrade360.com",
            hashed_password=get_password_hash("test1234"),
            is_active=True,
        )
        db.add(test_user)
        db.commit()
        print("   - 1 test user (test@cofrade360.com / test1234)")

        # Seed Locations
        locations = [
            Location(id=str(uuid.uuid4()), name="Teatro de la Maestranza",
                     address="Paseo de Cristóbal Colón, 22", lat=37.3838, lng=-5.9971, kind="theater"),
            Location(id=str(uuid.uuid4()), name="Plaza de San Francisco",
                     address="Plaza de San Francisco, s/n", lat=37.3886, lng=-5.9953, kind="plaza"),
            Location(id=str(uuid.uuid4()), name="Catedral de Sevilla",
                     address="Av. de la Constitución, s/n", lat=37.3862, lng=-5.9926, kind="church"),
            Location(id=str(uuid.uuid4()), name="Basílica del Gran Poder",
                     address="Plaza de San Lorenzo, 13", lat=37.3935, lng=-5.9995, kind="church"),
            Location(id=str(uuid.uuid4()), name="Basílica de la Macarena",
                     address="C. Bécquer, 1", lat=37.4008, lng=-5.9900, kind="church"),
            Location(id=str(uuid.uuid4()), name="Capilla del Patrocinio",
                     address="C. Castilla, 182, Triana", lat=37.3835, lng=-6.0055, kind="church"),
            Location(id=str(uuid.uuid4()), name="Iglesia de la Magdalena",
                     address="C. San Pablo, 10", lat=37.3895, lng=-5.9985, kind="church"),
        ]
        for loc in locations:
            db.add(loc)
        db.commit()
        for loc in locations:
            db.refresh(loc)

        # Seed 3 Hermandades
        hermandades = [
            Hermandad(
                id=str(uuid.uuid4()),
                nombre="Hermandad del Gran Poder",
                descripcion="Real e Ilustre Hermandad y Cofradía de Nazarenos de Nuestro Padre Jesús del Gran Poder",
                escudo="GP",
                sede="Basílica del Gran Poder",
                fecha_fundacion=datetime(1431, 1, 1),
            ),
            Hermandad(
                id=str(uuid.uuid4()),
                nombre="Hermandad de la Macarena",
                descripcion="Real, Ilustre y Fervorosa Hermandad y Cofradía de Nazarenos de Nuestra Señora del Santo Rosario",
                escudo="MC",
                sede="Basílica de la Macarena",
                fecha_fundacion=datetime(1595, 1, 1),
            ),
            Hermandad(
                id=str(uuid.uuid4()),
                nombre="Hermandad del Cachorro",
                descripcion="Pontificia, Real e Ilustre Hermandad Sacramental y Cofradía de Nazarenos del Santísimo Cristo de la Expiración",
                escudo="CA",
                sede="Capilla del Patrocinio (Triana)",
                fecha_fundacion=datetime(1689, 1, 1),
            ),
        ]

        for hermandad in hermandades:
            db.add(hermandad)
        db.commit()
        for hermandad in hermandades:
            db.refresh(hermandad)

        # Seed 10 Eventos with expanded fields
        eventos = [
            Evento(
                id=str(uuid.uuid4()),
                titulo="Pregón de Semana Santa 2026",
                descripcion="Pregón oficial de la Semana Santa de Sevilla, acto solemne que da comienzo a los días grandes.",
                tipo="otro",
                fecha_inicio=datetime(2026, 4, 3, 20, 0),
                fecha_fin=datetime(2026, 4, 3, 22, 0),
                location_id=locations[0].id,
                es_gratuito=False, precio=15.0, moneda="EUR",
                estado="programado",
            ),
            Evento(
                id=str(uuid.uuid4()),
                titulo="Vía Crucis Magno",
                descripcion="Vía Crucis con todas las hermandades de Sevilla por las calles del centro.",
                tipo="culto",
                fecha_inicio=datetime(2026, 4, 4, 18, 0),
                fecha_fin=datetime(2026, 4, 4, 21, 0),
                location_id=locations[1].id,
                hermandad_id=hermandades[1].id,
                es_gratuito=True, precio=0, estado="programado",
            ),
            Evento(
                id=str(uuid.uuid4()),
                titulo="Procesión del Silencio – Gran Poder",
                descripcion="Madrugada del Viernes Santo. El Señor del Gran Poder recorre Sevilla en silencio absoluto.",
                tipo="procesion",
                fecha_inicio=datetime(2026, 4, 10, 1, 0),
                fecha_fin=datetime(2026, 4, 10, 7, 30),
                location_id=locations[3].id,
                hermandad_id=hermandades[0].id,
                es_gratuito=True, precio=0, estado="programado",
            ),
            Evento(
                id=str(uuid.uuid4()),
                titulo="Salida Procesional La Macarena",
                descripcion="Salida de la procesión de la Esperanza Macarena en la Madrugada.",
                tipo="procesion",
                fecha_inicio=datetime(2026, 4, 10, 0, 0),
                fecha_fin=datetime(2026, 4, 10, 13, 0),
                location_id=locations[4].id,
                hermandad_id=hermandades[1].id,
                es_gratuito=True, precio=0, estado="programado",
            ),
            Evento(
                id=str(uuid.uuid4()),
                titulo="Procesión del Cachorro – Viernes Santo",
                descripcion="El Cristo de la Expiración cruza el puente de Triana al atardecer.",
                tipo="procesion",
                fecha_inicio=datetime(2026, 4, 10, 17, 0),
                fecha_fin=datetime(2026, 4, 11, 1, 30),
                location_id=locations[5].id,
                hermandad_id=hermandades[2].id,
                es_gratuito=True, precio=0, estado="programado",
            ),
            Evento(
                id=str(uuid.uuid4()),
                titulo="Besapies al Señor del Gran Poder",
                descripcion="Culto público de besapies previo a la Semana Santa.",
                tipo="culto",
                fecha_inicio=datetime(2026, 4, 5, 8, 0),
                fecha_fin=datetime(2026, 4, 5, 22, 0),
                location_id=locations[3].id,
                hermandad_id=hermandades[0].id,
                es_gratuito=True, precio=0, estado="programado",
            ),
            Evento(
                id=str(uuid.uuid4()),
                titulo="Función Principal – Macarena",
                descripcion="Función religiosa principal de la Hermandad de la Macarena.",
                tipo="culto",
                fecha_inicio=datetime(2026, 4, 6, 20, 0),
                fecha_fin=datetime(2026, 4, 6, 21, 30),
                location_id=locations[4].id,
                hermandad_id=hermandades[1].id,
                es_gratuito=True, precio=0, estado="programado",
            ),
            Evento(
                id=str(uuid.uuid4()),
                titulo="Concierto de Marchas Procesionales",
                descripcion="La Banda del Sol interpreta marchas clásicas en la Catedral.",
                tipo="concierto",
                fecha_inicio=datetime(2026, 4, 7, 20, 30),
                fecha_fin=datetime(2026, 4, 7, 22, 30),
                location_id=locations[2].id,
                es_gratuito=False, precio=10.0, moneda="EUR",
                estado="programado",
            ),
            Evento(
                id=str(uuid.uuid4()),
                titulo="Traslado al Paso – Cachorro",
                descripcion="Traslado de las imágenes al paso procesional en la Capilla del Patrocinio.",
                tipo="otro",
                fecha_inicio=datetime(2026, 4, 9, 22, 0),
                fecha_fin=datetime(2026, 4, 9, 23, 30),
                location_id=locations[5].id,
                hermandad_id=hermandades[2].id,
                es_gratuito=True, precio=0, estado="programado",
            ),
            Evento(
                id=str(uuid.uuid4()),
                titulo="Exposición: Bordados de Semana Santa",
                descripcion="Muestra de mantos, palios y bordados de las hermandades sevillanas.",
                tipo="exposicion",
                fecha_inicio=datetime(2026, 3, 20, 10, 0),
                fecha_fin=datetime(2026, 4, 12, 20, 0),
                location_id=locations[6].id,
                es_gratuito=False, precio=5.0, moneda="EUR",
                estado="programado",
            ),
        ]

        for evento in eventos:
            db.add(evento)
        db.commit()

        print(f"Database seeded successfully!")
        print(f"   - {len(locations)} locations")
        print(f"   - {len(hermandades)} hermandades")
        print(f"   - {len(eventos)} eventos")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

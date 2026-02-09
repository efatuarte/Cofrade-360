"""
Database seeding script
Seeds 3 hermandades and 10 eventos
"""
from datetime import datetime
from app.db.session import SessionLocal
from app.models.models import Hermandad, Evento
import uuid


def seed_database():
    db = SessionLocal()
    
    try:
        # Check if already seeded
        existing = db.query(Hermandad).first()
        if existing:
            print("Database already seeded. Skipping...")
            return
        
        # Seed 3 Hermandades
        hermandades = [
            Hermandad(
                id=str(uuid.uuid4()),
                nombre="Hermandad del Gran Poder",
                descripcion="Real e Ilustre Hermandad y Cofradía de Nazarenos de Nuestro Padre Jesús del Gran Poder",
                escudo="🛡️",
                sede="Basílica del Gran Poder",
                fecha_fundacion=datetime(1431, 1, 1),
            ),
            Hermandad(
                id=str(uuid.uuid4()),
                nombre="Hermandad de la Macarena",
                descripcion="Real, Ilustre y Fervorosa Hermandad y Cofradía de Nazarenos de Nuestra Señora del Santo Rosario",
                escudo="🛡️",
                sede="Basílica de la Macarena",
                fecha_fundacion=datetime(1595, 1, 1),
            ),
            Hermandad(
                id=str(uuid.uuid4()),
                nombre="Hermandad del Cachorro",
                descripcion="Pontificia, Real e Ilustre Hermandad Sacramental y Cofradía de Nazarenos del Santísimo Cristo de la Expiración",
                escudo="🛡️",
                sede="Iglesia de San Lorenzo",
                fecha_fundacion=datetime(1682, 1, 1),
            ),
        ]
        
        for hermandad in hermandades:
            db.add(hermandad)
        
        db.commit()
        
        # Refresh to get IDs
        for hermandad in hermandades:
            db.refresh(hermandad)
        
        # Seed 10 Eventos
        eventos = [
            Evento(
                id=str(uuid.uuid4()),
                titulo="Pregón de Semana Santa",
                descripcion="Pregón oficial de la Semana Santa de Sevilla",
                fecha_hora=datetime(2026, 4, 3, 20, 0),
                hermandad_id=hermandades[0].id,
                ubicacion="Teatro de la Maestranza",
            ),
            Evento(
                id=str(uuid.uuid4()),
                titulo="Vía Crucis Magno",
                descripcion="Vía Crucis con todas las hermandades de Sevilla",
                fecha_hora=datetime(2026, 4, 4, 18, 0),
                hermandad_id=hermandades[1].id,
                ubicacion="Plaza de San Francisco",
            ),
            Evento(
                id=str(uuid.uuid4()),
                titulo="Procesión del Silencio",
                descripcion="Procesión del Viernes Santo en silencio",
                fecha_hora=datetime(2026, 4, 10, 22, 0),
                hermandad_id=hermandades[2].id,
                ubicacion="Catedral de Sevilla",
            ),
            Evento(
                id=str(uuid.uuid4()),
                titulo="Salida Procesional Gran Poder",
                descripcion="Salida de la procesión del Señor del Gran Poder",
                fecha_hora=datetime(2026, 4, 10, 0, 0),
                hermandad_id=hermandades[0].id,
                ubicacion="Basílica del Gran Poder",
            ),
            Evento(
                id=str(uuid.uuid4()),
                titulo="Salida Procesional La Macarena",
                descripcion="Salida de la procesión de la Esperanza Macarena",
                fecha_hora=datetime(2026, 4, 10, 1, 0),
                hermandad_id=hermandades[1].id,
                ubicacion="Basílica de la Macarena",
            ),
            Evento(
                id=str(uuid.uuid4()),
                titulo="Procesión del Cachorro",
                descripcion="Procesión del Cristo de la Expiración",
                fecha_hora=datetime(2026, 4, 10, 19, 0),
                hermandad_id=hermandades[2].id,
                ubicacion="Iglesia de San Lorenzo",
            ),
            Evento(
                id=str(uuid.uuid4()),
                titulo="Besapies al Señor del Gran Poder",
                descripcion="Culto del besapies",
                fecha_hora=datetime(2026, 4, 5, 18, 0),
                hermandad_id=hermandades[0].id,
                ubicacion="Basílica del Gran Poder",
            ),
            Evento(
                id=str(uuid.uuid4()),
                titulo="Función Principal de Instituto",
                descripcion="Función religiosa principal",
                fecha_hora=datetime(2026, 4, 6, 20, 0),
                hermandad_id=hermandades[1].id,
                ubicacion="Basílica de la Macarena",
            ),
            Evento(
                id=str(uuid.uuid4()),
                titulo="Traslado al Paso",
                descripcion="Traslado de las imágenes al paso procesional",
                fecha_hora=datetime(2026, 4, 9, 22, 0),
                hermandad_id=hermandades[2].id,
                ubicacion="Iglesia de San Lorenzo",
            ),
            Evento(
                id=str(uuid.uuid4()),
                titulo="Misa de Acción de Gracias",
                descripcion="Misa tras la Semana Santa",
                fecha_hora=datetime(2026, 4, 11, 12, 0),
                hermandad_id=hermandades[0].id,
                ubicacion="Basílica del Gran Poder",
            ),
        ]
        
        for evento in eventos:
            db.add(evento)
        
        db.commit()
        
        print(f"✅ Database seeded successfully!")
        print(f"   - {len(hermandades)} hermandades")
        print(f"   - {len(eventos)} eventos")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

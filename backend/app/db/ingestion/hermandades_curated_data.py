"""Datos curados de las hermandades de Sevilla — Semana Santa 2026.

Fuentes principales:
- Consejo General de Hermandades y Cofradías de Sevilla (consejodecofradias.es)
- Webs oficiales de cada hermandad (ver HERMANDADES_SEVILLA_WEBS)
- Guía oficial de Semana Santa del Ayuntamiento de Sevilla

Semana Santa 2026 calendario:
  Viernes de Dolores: 27 marzo
  Sábado de Pasión: 28 marzo
  Domingo de Ramos: 29 marzo
  Lunes Santo: 30 marzo
  Martes Santo: 31 marzo
  Miércoles Santo: 1 abril
  Jueves Santo: 2 abril
  Madrugada: 3 abril (madrugada)
  Viernes Santo: 3 abril (tarde)
  Sábado Santo: 4 abril
  Domingo de Resurrección: 5 abril

Horarios: basados en los horarios oficiales del Consejo 2025, proyectados a 2026.
Los horarios de vísperas (Viernes de Dolores, Sábado de Pasión) son aproximados
ya que estas hermandades no tienen carrera oficial.

NOTA: Este fichero se usa como fuente de referencia estática. El script
build_hermandades_dataset.py lo combina con datos extraídos de las webs oficiales.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# Semana Santa 2026 dates (ISO format prefix)
_DATES = {
    "Viernes de Dolores": "2026-03-27",
    "Sábado de Pasión": "2026-03-28",
    "Domingo de Ramos": "2026-03-29",
    "Lunes Santo": "2026-03-30",
    "Martes Santo": "2026-03-31",
    "Miércoles Santo": "2026-04-01",
    "Jueves Santo": "2026-04-02",
    "Madrugada": "2026-04-03",
    "Viernes Santo": "2026-04-03",
    "Sábado Santo": "2026-04-04",
    "Domingo de Resurrección": "2026-04-05",
}


def _dt(day: str, time: str) -> str:
    """Build ISO datetime from day key and HH:MM time."""
    return f"{_DATES[day]}T{time}:00"


def _entry(
    name_short: str,
    name_full: str,
    ss_day: str,
    temple_name: str,
    address: str,
    lat: Optional[float],
    lng: Optional[float],
    titulares: List[Dict[str, str]],
    salida: Optional[str],
    carrera_start: Optional[str] = None,
    carrera_end: Optional[str] = None,
    recogida: Optional[str] = None,
    itinerary_text: Optional[str] = None,
) -> Dict[str, Any]:
    schedule: Dict[str, Any] = {
        "salida": _dt(ss_day, salida) if salida else None,
        "carrera_oficial_start": _dt(ss_day, carrera_start) if carrera_start else None,
        "carrera_oficial_end": _dt(ss_day, carrera_end) if carrera_end else None,
        "recogida": _dt(ss_day, recogida) if recogida else None,
        "itinerary_text": itinerary_text,
    }
    return {
        "name_short": name_short,
        "name_full": name_full,
        "ss_day": ss_day,
        "sede": {
            "temple_name": temple_name,
            "address": address,
            "lat": lat,
            "lng": lng,
            "needs_geocode": lat is None,
        },
        "titulares": titulares,
        "schedule": schedule,
    }


def _c(name: str) -> Dict[str, str]:
    """Shortcut for cristo titular."""
    return {"name": name, "kind": "cristo"}


def _v(name: str) -> Dict[str, str]:
    """Shortcut for virgen titular."""
    return {"name": name, "kind": "virgen"}


def _m(name: str) -> Dict[str, str]:
    """Shortcut for misterio titular."""
    return {"name": name, "kind": "misterio"}


# ============================================================
# DATASET COMPLETO
# ============================================================

CURATED_DATA: List[Dict[str, Any]] = [
    # ========== VIERNES DE DOLORES ==========
    _entry(
        "Pino Montano",
        "Hermandad de la Sagrada Entrada en Jerusalén y Ntra. Sra. del Amparo",
        "Viernes de Dolores",
        "Parroquia de la Blanca Paloma", "C. Luisa de Marillac, s/n, Pino Montano, Sevilla",
        37.4161, -5.9750,
        [_m("Sagrada Entrada en Jerusalén"), _v("Nuestra Señora del Amparo")],
        salida="18:00", recogida="23:00",
    ),
    _entry(
        "La Misión",
        "Archicofradía del Santísimo Sacramento y Hermandad de Penitencia del Stmo. Cristo de la Misión y Ntra. Sra. de los Dolores",
        "Viernes de Dolores",
        "Parroquia de la Misión", "C. Fray Isidoro de Sevilla, s/n, Sevilla",
        37.3648, -5.9580,
        [_c("Santísimo Cristo de la Misión"), _v("Nuestra Señora de los Dolores")],
        salida="18:00", recogida="23:00",
    ),
    _entry(
        "Dulce Nombre (Bellavista)",
        "Hermandad del Dulce Nombre de Jesús y Ntra. Sra. de la Encarnación",
        "Viernes de Dolores",
        "Parroquia de Ntra. Sra. de la Oliva", "Avda. de Bellavista, s/n, Sevilla",
        37.3520, -5.9780,
        [_c("Dulce Nombre de Jesús"), _v("Nuestra Señora de la Encarnación")],
        salida="18:00", recogida="23:00",
    ),
    _entry(
        "Pasión y Muerte",
        "Hermandad de Nuestro Padre Jesús de la Pasión y Muerte y María Santísima de la Caridad y Consolación",
        "Viernes de Dolores",
        "Parroquia de Santa María Madre de la Iglesia", "C. Gustavo Bacarisas, s/n, Los Remedios, Sevilla",
        37.3772, -6.0098,
        [_c("Nuestro Padre Jesús de la Pasión y Muerte"), _v("María Santísima de la Caridad y Consolación")],
        salida="18:00", recogida="23:00",
    ),
    _entry(
        "Bendición y Esperanza",
        "Hermandad de la Bendición y la Esperanza",
        "Viernes de Dolores",
        "Parroquia de San Pío X", "C. Cardenal Bueno Monreal, s/n, Nervión, Sevilla",
        37.3815, -5.9700,
        [_c("Nuestro Padre Jesús de la Bendición"), _v("María Santísima de la Esperanza")],
        salida="18:00", recogida="23:00",
    ),
    _entry(
        "Stmo. Cristo de la Corona",
        "Hermandad del Stmo. Cristo de la Corona y Ntra. Sra. del Rosario",
        "Viernes de Dolores",
        "Iglesia de San Nicolás de Bari", "C. Muñoz y Pabón, 6, Sevilla",
        37.3872, -5.9917,
        [_c("Santísimo Cristo de la Corona"), _v("Nuestra Señora del Rosario")],
        salida="18:00", recogida="23:00",
    ),

    # ========== SÁBADO DE PASIÓN ==========
    _entry(
        "Padre Pío",
        "Hermandad del Stmo. Cristo del Desamparo y Ntra. Sra. de los Dolores Coronada",
        "Sábado de Pasión",
        "Parroquia del Padre Pío", "C. Padre Pío de Pietrelcina, s/n, Sevilla Este",
        37.3934, -5.9329,
        [_c("Santísimo Cristo del Desamparo"), _v("Nuestra Señora de los Dolores Coronada")],
        salida="17:30", recogida="23:30",
    ),
    _entry(
        "Divino Perdón",
        "Hermandad del Divino Perdón",
        "Sábado de Pasión",
        "Parroquia de San Juan de Ribera", "Barriada Padre Pío Palmete, Sevilla",
        37.3800, -5.9400,
        [_c("Nuestro Padre Jesús del Divino Perdón"), _v("Nuestra Señora de los Dolores")],
        salida="17:00", recogida="22:30",
    ),
    _entry(
        "Torreblanca",
        "Hermandad de Nuestra Señora de los Dolores",
        "Sábado de Pasión",
        "Parroquia de Ntra. Sra. de los Dolores", "C. Emilia Barral, s/n, Torreblanca, Sevilla",
        37.3875, -5.9378,
        [_c("Santísimo Cristo de la Salud"), _v("Nuestra Señora de los Dolores")],
        salida="17:30", recogida="23:00",
    ),
    _entry(
        "San José Obrero",
        "Hermandad del Cristo de la Humildad y Paciencia y Ntra. Sra. de los Dolores y Misericordia",
        "Sábado de Pasión",
        "Parroquia de San José Obrero", "C. Ingeniero La Cierva, s/n, Cerro del Águila, Sevilla",
        37.3755, -5.9618,
        [_c("Santísimo Cristo de la Humildad y Paciencia"), _v("Nuestra Señora de los Dolores y Misericordia")],
        salida="17:30", recogida="23:00",
    ),
    _entry(
        "La Milagrosa",
        "Hermandad de la Milagrosa",
        "Sábado de Pasión",
        "Capilla de la Medalla Milagrosa", "C. San Vicente de Paúl, s/n, Sevilla",
        37.3707, -5.9684,
        [_c("Santísimo Cristo de la Caridad"), _v("Nuestra Señora de la Medalla Milagrosa")],
        salida="17:00", recogida="22:30",
    ),

    # ========== DOMINGO DE RAMOS ==========
    _entry(
        "Jesús Despojado",
        "Hermandad de Nuestro Padre Jesús Despojado de sus Vestiduras y María Santísima de los Dolores y Misericordia",
        "Domingo de Ramos",
        "Iglesia de San Benito Abad (parroquia antigua)", "C. Luis Montoto, 91, Sevilla",
        37.3893, -5.9803,
        [_c("Nuestro Padre Jesús Despojado de sus Vestiduras"), _v("María Santísima de los Dolores y Misericordia")],
        salida="14:30", carrera_start="17:00", carrera_end="17:30", recogida="20:30",
    ),
    _entry(
        "La Paz",
        "Hermandad de Nuestro Padre Jesús de la Victoria y María Santísima de la Paz",
        "Domingo de Ramos",
        "Iglesia de San Sebastián", "C. San Sebastián, s/n, Sevilla",
        37.3820, -5.9855,
        [_c("Nuestro Padre Jesús de la Victoria"), _v("María Santísima de la Paz")],
        salida="15:00", carrera_start="17:45", carrera_end="18:15", recogida="21:00",
    ),
    _entry(
        "La Cena",
        "Hermandad Sacramental de la Sagrada Cena",
        "Domingo de Ramos",
        "Capilla de Nuestra Señora del Rosario", "C. Resolana, s/n, Sevilla",
        37.3985, -5.9930,
        [_m("Sagrada Cena Sacramental"), _v("Nuestra Señora del Subterráneo")],
        salida="14:00", carrera_start="17:30", carrera_end="18:00", recogida="21:30",
    ),
    _entry(
        "La Hiniesta",
        "Hermandad de la Hiniesta",
        "Domingo de Ramos",
        "Iglesia de San Julián", "C. San Julián, s/n, Sevilla",
        37.3972, -5.9905,
        [_c("Nuestro Padre Jesús de la Buena Muerte"), _v("Nuestra Señora de la Hiniesta Gloriosa")],
        salida="14:30", carrera_start="18:15", carrera_end="18:45", recogida="22:00",
    ),
    _entry(
        "San Roque",
        "Hermandad de Nuestro Padre Jesús de las Penas y María Santísima de Gracia y Esperanza",
        "Domingo de Ramos",
        "Iglesia de San Roque", "C. Arrayán, s/n, Sevilla",
        37.3945, -5.9925,
        [_c("Nuestro Padre Jesús de las Penas"), _v("María Santísima de Gracia y Esperanza")],
        salida="15:00", carrera_start="18:45", carrera_end="19:15", recogida="22:30",
    ),
    _entry(
        "La Estrella",
        "Hermandad de la Estrella",
        "Domingo de Ramos",
        "Iglesia de la Estrella (San Jacinto)", "C. San Jacinto, 51, Triana, Sevilla",
        37.3790, -6.0065,
        [_c("Nuestro Padre Jesús de las Penas"), _v("María Santísima de la Estrella")],
        salida="14:30", carrera_start="19:00", carrera_end="19:30", recogida="23:00",
    ),
    _entry(
        "La Amargura",
        "Hermandad de la Amargura",
        "Domingo de Ramos",
        "Iglesia de San Juan de la Palma", "C. Feria, s/n, Sevilla",
        37.3943, -5.9945,
        [_c("Nuestro Padre Jesús del Silencio en el Desprecio de Herodes"), _v("María Santísima de la Amargura Coronada")],
        salida="15:00", carrera_start="19:30", carrera_end="20:00", recogida="23:00",
    ),
    _entry(
        "El Amor",
        "Hermandad del Amor",
        "Domingo de Ramos",
        "Iglesia Colegial del Divino Salvador", "Plaza del Salvador, s/n, Sevilla",
        37.3895, -5.9935,
        [_c("Nuestro Padre Jesús del Amor"), _v("María Santísima del Socorro")],
        salida="15:30", carrera_start="19:45", carrera_end="20:15", recogida="23:30",
    ),

    # ========== LUNES SANTO ==========
    _entry(
        "Cautivo y Rescatado",
        "Hermandad de Nuestro Padre Jesús Cautivo y Rescatado y Ntra. Sra. de las Mercedes",
        "Lunes Santo",
        "Parroquia de Ntra. Sra. de la Asunción", "Avda. de la Paz, s/n, Nervión, Sevilla",
        37.3817, -5.9705,
        [_c("Nuestro Padre Jesús Cautivo y Rescatado"), _v("Nuestra Señora de las Mercedes")],
        salida="15:00", carrera_start="18:00", carrera_end="18:30", recogida="22:00",
    ),
    _entry(
        "Redención -Rocío",
        "Hermandad de la Redención",
        "Lunes Santo",
        "Parroquia de Santiago", "C. Santiago, 15, Sevilla",
        37.3930, -5.9887,
        [_c("Nuestro Padre Jesús de la Redención"), _v("Nuestra Señora del Rocío")],
        salida="15:00", carrera_start="18:30", carrera_end="19:00", recogida="22:15",
    ),
    _entry(
        "Santa Genoveva",
        "Hermandad de Santa Genoveva",
        "Lunes Santo",
        "Parroquia de Santa Genoveva", "C. Dársena, s/n, Polígono San Pablo, Sevilla",
        37.4100, -5.9680,
        [_c("Nuestro Padre Jesús Cautivo"), _v("María Santísima de las Mercedes")],
        salida="14:30", carrera_start="18:45", carrera_end="19:15", recogida="23:00",
    ),
    _entry(
        "San Gonzalo",
        "Hermandad de San Gonzalo",
        "Lunes Santo",
        "Parroquia de San Gonzalo", "C. Pagés del Corro, s/n, Triana, Sevilla",
        37.3772, -6.0045,
        [_c("Nuestro Padre Jesús de la Salud"), _v("Nuestra Señora de la Salud")],
        salida="14:30", carrera_start="19:00", carrera_end="19:30", recogida="23:00",
    ),
    _entry(
        "Santa Marta",
        "Hermandad de Santa Marta",
        "Lunes Santo",
        "Iglesia de San Andrés", "C. Dueñas, 1, Sevilla",
        37.3918, -5.9965,
        [_c("Santísimo Cristo de la Caridad"), _v("Nuestra Señora de las Penas"), _v("Santa Marta")],
        salida="15:30", carrera_start="19:15", carrera_end="19:45", recogida="22:30",
    ),
    _entry(
        "Vera+Cruz",
        "Hermandad de la Vera-Cruz",
        "Lunes Santo",
        "Capilla de la Vera-Cruz (Convento de San Francisco)", "C. Sierpes, s/n (antigua ubicación), Sevilla",
        37.3880, -5.9955,
        [_c("Santísimo Cristo de la Vera-Cruz"), _v("Nuestra Señora de las Tristezas")],
        salida="15:30", carrera_start="19:30", carrera_end="20:00", recogida="23:00",
    ),
    _entry(
        "Las Penas",
        "Hermandad de las Penas de San Vicente",
        "Lunes Santo",
        "Iglesia de San Vicente", "C. San Vicente, 86, Sevilla",
        37.3925, -6.0005,
        [_c("Nuestro Padre Jesús de las Penas"), _v("María Santísima de los Dolores y Misericordia")],
        salida="15:30", carrera_start="20:00", carrera_end="20:30", recogida="23:30",
    ),
    _entry(
        "Las Aguas",
        "Hermandad de las Aguas",
        "Lunes Santo",
        "Iglesia del Sagrario", "Avda. de la Constitución, s/n, Sevilla",
        37.3860, -5.9932,
        [_c("Nuestro Padre Jesús de las Aguas"), _v("Nuestra Señora del Mayor Dolor")],
        salida="16:00", carrera_start="20:15", carrera_end="20:45", recogida="23:15",
    ),
    _entry(
        "El Museo",
        "Hermandad del Museo",
        "Lunes Santo",
        "Iglesia del Santo Ángel", "C. Rioja, 2, Sevilla",
        37.3895, -6.0000,
        [_c("Santísimo Cristo de la Expiración"), _v("Nuestra Señora de las Aguas")],
        salida="16:00", carrera_start="20:30", carrera_end="21:00", recogida="23:30",
    ),

    # ========== MARTES SANTO ==========
    _entry(
        "San Esteban",
        "Hermandad de San Esteban",
        "Martes Santo",
        "Iglesia de San Esteban", "C. San Esteban, 52, Sevilla",
        37.3855, -5.9860,
        [_c("Nuestro Padre Jesús de la Salud y Buen Viaje"), _v("Nuestra Señora de los Desamparados")],
        salida="15:00", carrera_start="18:15", carrera_end="18:45", recogida="22:00",
    ),
    _entry(
        "Dolores del Cerro",
        "Hermandad de los Dolores del Cerro del Águila",
        "Martes Santo",
        "Parroquia de Ntra. Sra. de los Dolores del Cerro", "C. Pino Montano, s/n, Cerro del Águila, Sevilla",
        37.3725, -5.9633,
        [_c("Santísimo Cristo de la Misericordia"), _v("Nuestra Señora de los Dolores")],
        salida="14:30", carrera_start="18:45", carrera_end="19:15", recogida="22:30",
    ),
    _entry(
        "La Candelaria",
        "Hermandad de la Candelaria",
        "Martes Santo",
        "Iglesia de San Nicolás de Bari", "C. Muñoz y Pabón, 6, Sevilla",
        37.3872, -5.9917,
        [_c("Nuestro Padre Jesús de la Salud"), _v("Nuestra Señora de la Candelaria")],
        salida="15:00", carrera_start="19:00", carrera_end="19:30", recogida="23:00",
    ),
    _entry(
        "San Benito",
        "Hermandad de San Benito",
        "Martes Santo",
        "Iglesia de San Benito Abad", "C. Luis Montoto, 91, Sevilla",
        37.3893, -5.9803,
        [_c("Nuestro Padre Jesús de la Presentación al Pueblo"), _v("Nuestra Señora de la Encarnación")],
        salida="15:00", carrera_start="19:15", carrera_end="19:45", recogida="23:00",
    ),
    _entry(
        "Dulce Nombre",
        "Hermandad del Dulce Nombre de Jesús",
        "Martes Santo",
        "Iglesia de San Lorenzo", "Plaza de San Lorenzo, s/n, Sevilla",
        37.3933, -5.9990,
        [_c("Nuestro Padre Jesús ante Anás"), _v("Nuestra Señora del Dulce Nombre")],
        salida="15:30", carrera_start="19:30", carrera_end="20:00", recogida="23:30",
    ),
    _entry(
        "Los Javieres",
        "Hermandad de los Javieres",
        "Martes Santo",
        "Capilla de San José", "C. Jovellanos, 1, Sevilla",
        37.3890, -5.9962,
        [_c("Nuestro Padre Jesús de la Providencia"), _v("María Santísima del Patrocinio")],
        salida="16:00", carrera_start="19:45", carrera_end="20:15", recogida="23:00",
    ),
    _entry(
        "Los Estudiantes",
        "Hermandad de los Estudiantes",
        "Martes Santo",
        "Capilla de la Universidad de Sevilla", "C. San Fernando, s/n, Sevilla",
        37.3770, -5.9880,
        [_c("Santísimo Cristo de la Buena Muerte"), _v("María Santísima de la Angustia")],
        salida="16:00", carrera_start="20:00", carrera_end="20:30", recogida="23:30",
    ),
    _entry(
        "Santa Cruz",
        "Hermandad de Santa Cruz",
        "Martes Santo",
        "Iglesia de Santa Cruz", "C. Mateos Gago, s/n, Sevilla",
        37.3845, -5.9880,
        [_c("Santísimo Cristo de las Misericordias"), _v("Nuestra Señora de los Dolores")],
        salida="16:00", carrera_start="20:15", carrera_end="20:45", recogida="23:30",
    ),

    # ========== MIÉRCOLES SANTO ==========
    _entry(
        "El Carmen",
        "Hermandad del Carmen Doloroso",
        "Miércoles Santo",
        "Iglesia del Santo Ángel", "C. Rioja, 2, Sevilla",
        37.3895, -6.0000,
        [_c("Nuestro Padre Jesús del Silencio ante Pilato (El Carmen)"), _v("Nuestra Señora del Carmen Doloroso")],
        salida="14:30", carrera_start="18:00", carrera_end="18:30", recogida="22:00",
    ),
    _entry(
        "La Sed",
        "Hermandad de la Sed",
        "Miércoles Santo",
        "Capilla de la Evangelización de los Pueblos", "Avda. Kansas City, s/n, Sevilla",
        37.3780, -5.9640,
        [_c("Santísimo Cristo de la Sed"), _v("Nuestra Señora de Consolación y Lágrimas")],
        salida="14:00", carrera_start="18:30", carrera_end="19:00", recogida="22:30",
    ),
    _entry(
        "San Bernardo",
        "Hermandad de San Bernardo",
        "Miércoles Santo",
        "Iglesia de San Bernardo", "C. Santo Rey, s/n, San Bernardo, Sevilla",
        37.3785, -5.9835,
        [_c("Nuestro Padre Jesús del Gran Poder (San Bernardo)"), _v("María Santísima del Refugio")],
        salida="14:30", carrera_start="18:45", carrera_end="19:15", recogida="23:00",
    ),
    _entry(
        "Buen Fin",
        "Hermandad del Buen Fin",
        "Miércoles Santo",
        "Iglesia de San Antonio de Padua", "C. San Vicente, 65, Sevilla",
        37.3918, -6.0020,
        [_c("Nuestro Padre Jesús de la Sagrada Columna y Azotes"), _v("Nuestra Señora del Buen Fin")],
        salida="15:00", carrera_start="19:00", carrera_end="19:30", recogida="23:00",
    ),
    _entry(
        "Sagrada Lanzada",
        "Hermandad de la Lanzada",
        "Miércoles Santo",
        "Iglesia de San Martín", "C. San Martín, s/n, Sevilla",
        37.3928, -5.9935,
        [_c("Santísimo Cristo de la Lanzada"), _v("María Santísima de Guía")],
        salida="15:30", carrera_start="19:15", carrera_end="19:45", recogida="23:15",
    ),
    _entry(
        "El Baratillo",
        "Hermandad del Baratillo",
        "Miércoles Santo",
        "Capilla del Baratillo (Real Maestranza)", "Paseo de Cristóbal Colón, s/n, Sevilla",
        37.3835, -5.9980,
        [_c("Nuestro Padre Jesús de la Misericordia"), _v("María Santísima de la Piedad")],
        salida="15:30", carrera_start="19:30", carrera_end="20:00", recogida="23:15",
    ),
    _entry(
        "Cristo de Burgos",
        "Hermandad del Cristo de Burgos",
        "Miércoles Santo",
        "Iglesia de San Pedro", "Plaza de San Pedro, s/n, Sevilla",
        37.3910, -5.9900,
        [_c("Santísimo Cristo de Burgos"), _v("Madre de Dios de la Palma")],
        salida="16:00", carrera_start="19:45", carrera_end="20:15", recogida="23:30",
    ),
    _entry(
        "Siete Palabras",
        "Hermandad de las Siete Palabras",
        "Miércoles Santo",
        "Iglesia de San Vicente", "C. San Vicente, 86, Sevilla",
        37.3925, -6.0005,
        [_c("Santísimo Cristo de las Siete Palabras"), _v("María Santísima de los Remedios")],
        salida="16:00", carrera_start="20:00", carrera_end="20:30", recogida="23:30",
    ),
    _entry(
        "Los Panaderos",
        "Hermandad de los Panaderos",
        "Miércoles Santo",
        "Iglesia de Santa Ana", "C. Pureza, s/n, Triana, Sevilla",
        37.3810, -6.0040,
        [_c("Santísimo Cristo de la Expiración"), _v("Nuestra Señora de las Penas")],
        salida="16:00", carrera_start="20:15", carrera_end="20:45", recogida="00:00",
    ),

    # ========== JUEVES SANTO ==========
    _entry(
        "Los Negritos",
        "Hermandad de los Negritos",
        "Jueves Santo",
        "Capilla de Nuestra Señora de los Ángeles", "C. Resolana, 58, Sevilla",
        37.3985, -5.9920,
        [_c("Santísimo Cristo de la Fundación"), _v("Nuestra Señora de los Ángeles")],
        salida="14:30", carrera_start="18:00", carrera_end="18:30", recogida="22:00",
    ),
    _entry(
        "La Exaltación",
        "Hermandad de la Exaltación",
        "Jueves Santo",
        "Iglesia de Santa Catalina", "Plaza de los Terceros, s/n, Sevilla",
        37.3912, -5.9880,
        [_c("Santísimo Cristo de la Exaltación"), _v("Nuestra Señora de las Lágrimas")],
        salida="15:00", carrera_start="18:30", carrera_end="19:00", recogida="22:30",
    ),
    _entry(
        "Las Cigarreras",
        "Hermandad de la Columna y Azotes (Las Cigarreras)",
        "Jueves Santo",
        "Capilla de San José (Fábrica de Tabacos)", "C. San Fernando, 4, Sevilla",
        37.3780, -5.9870,
        [_c("Santísimo Cristo de la Columna y Azotes"), _v("Nuestra Señora de la Victoria")],
        salida="15:00", carrera_start="19:00", carrera_end="19:30", recogida="23:00",
    ),
    _entry(
        "Monte-Sión",
        "Hermandad de Monte-Sión",
        "Jueves Santo",
        "Iglesia de San Gregorio (Capilla de Monte-Sión)", "C. Bustos Tavera, 17, Sevilla",
        37.3950, -5.9893,
        [_c("Nuestro Padre Jesús de la Oración en el Huerto"), _v("Nuestra Señora del Rosario en sus Misterios Dolorosos")],
        salida="15:30", carrera_start="19:15", carrera_end="19:45", recogida="23:00",
    ),
    _entry(
        "La Quinta Angustia",
        "Hermandad de la Quinta Angustia",
        "Jueves Santo",
        "Iglesia de la Magdalena", "C. San Pablo, 10, Sevilla",
        37.3895, -5.9985,
        [_m("Sagrado Descendimiento de Nuestro Señor Jesucristo"), _v("María Santísima de la Quinta Angustia")],
        salida="16:00", carrera_start="19:30", carrera_end="20:00", recogida="23:15",
    ),
    _entry(
        "El Valle",
        "Hermandad del Valle",
        "Jueves Santo",
        "Iglesia de la Anunciación", "C. Laraña, 4, Sevilla",
        37.3910, -5.9930,
        [_c("Santísimo Cristo de la Sed"), _v("Nuestra Señora del Valle")],
        salida="16:00", carrera_start="20:00", carrera_end="20:30", recogida="23:30",
    ),
    _entry(
        "Pasión",
        "Hermandad de Pasión",
        "Jueves Santo",
        "Iglesia Colegial del Divino Salvador", "Plaza del Salvador, s/n, Sevilla",
        37.3895, -5.9935,
        [_c("Nuestro Padre Jesús de la Pasión"), _v("Nuestra Señora de la Merced")],
        salida="16:30", carrera_start="20:15", carrera_end="20:45", recogida="00:00",
    ),

    # ========== MADRUGADA ==========
    _entry(
        "El Silencio",
        "Hermandad del Silencio",
        "Madrugada",
        "Iglesia de San Antonio Abad", "C. Alfonso XII, 3, Sevilla",
        37.3895, -5.9860,
        [_c("Nuestro Padre Jesús Nazareno"), _v("Nuestra Señora de la Concepción")],
        salida="01:00", carrera_start="03:00", carrera_end="03:30", recogida="07:00",
    ),
    _entry(
        "Gran Poder",
        "Pontificia y Real Hermandad y Cofradía de Nazarenos de Nuestro Padre Jesús del Gran Poder y María Santísima del Mayor Dolor y Traspaso",
        "Madrugada",
        "Basílica de Jesús del Gran Poder", "Plaza de San Lorenzo, 13, Sevilla",
        37.3935, -5.9995,
        [_c("Nuestro Padre Jesús del Gran Poder"), _v("María Santísima del Mayor Dolor y Traspaso")],
        salida="01:00", carrera_start="03:20", carrera_end="04:15", recogida="07:30",
    ),
    _entry(
        "La Macarena",
        "Real, Ilustre y Fervorosa Hermandad y Cofradía de Nazarenos de Nuestro Padre Jesús de la Sentencia y María Santísima de la Esperanza Macarena",
        "Madrugada",
        "Basílica de la Macarena", "C. Bécquer, 1, Sevilla",
        37.4008, -5.9900,
        [_c("Nuestro Padre Jesús de la Sentencia"), _v("María Santísima de la Esperanza Macarena")],
        salida="00:00", carrera_start="04:30", carrera_end="05:30", recogida="13:00",
    ),
    _entry(
        "El Calvario",
        "Hermandad del Calvario",
        "Madrugada",
        "Iglesia de la Magdalena", "C. San Pablo, 10, Sevilla",
        37.3895, -5.9985,
        [_c("Santísimo Cristo del Calvario"), _v("Nuestra Señora de la Presentación")],
        salida="02:00", carrera_start="05:15", carrera_end="05:45", recogida="08:30",
    ),
    _entry(
        "Esperanza de Triana",
        "Hermandad de la Esperanza de Triana",
        "Madrugada",
        "Capilla de los Marineros", "C. Pureza, 52, Triana, Sevilla",
        37.3815, -6.0040,
        [_c("Nuestro Padre Jesús de las Tres Caídas"), _v("María Santísima de la Esperanza de Triana")],
        salida="01:30", carrera_start="05:45", carrera_end="06:30", recogida="13:30",
    ),
    _entry(
        "Los Gitanos",
        "Hermandad de los Gitanos",
        "Madrugada",
        "Iglesia de los Gitanos (San Román)", "Avda. de Miraflores, s/n, Sevilla",
        37.4020, -5.9865,
        [_c("Nuestro Padre Jesús de la Salud"), _v("María Santísima de las Angustias Coronada")],
        salida="00:30", carrera_start="06:15", carrera_end="06:45", recogida="13:00",
    ),

    # ========== VIERNES SANTO ==========
    _entry(
        "Carretería",
        "Hermandad de la Carretería",
        "Viernes Santo",
        "Capilla de la Carretería", "C. Temprado, 8, Sevilla",
        37.3855, -5.9975,
        [_c("Santísimo Cristo de la Salud"), _v("María Santísima de la Luz")],
        salida="15:00", carrera_start="18:00", carrera_end="18:30", recogida="22:00",
    ),
    _entry(
        "La Soledad (San Buenaventura)",
        "Hermandad de la Soledad de San Buenaventura",
        "Viernes Santo",
        "Convento de San Buenaventura", "C. Carlos Cañal, 4, Sevilla",
        37.3870, -5.9960,
        [_c("Santísimo Cristo del Descendimiento"), _v("Nuestra Señora de la Soledad")],
        salida="15:30", carrera_start="18:30", carrera_end="19:00", recogida="22:30",
    ),
    _entry(
        "El Cachorro",
        "Pontificia, Real e Ilustre Hermandad Sacramental del Santísimo Cristo de la Expiración y María Santísima del Patrocinio",
        "Viernes Santo",
        "Capilla del Patrocinio", "C. Castilla, 182, Triana, Sevilla",
        37.3835, -6.0055,
        [_c("Santísimo Cristo de la Expiración"), _v("Nuestra Señora del Patrocinio")],
        salida="15:30", carrera_start="19:00", carrera_end="19:30", recogida="23:00",
    ),
    _entry(
        "La O",
        "Hermandad de la O",
        "Viernes Santo",
        "Iglesia de Nuestra Señora de la O", "C. Castilla, 30, Triana, Sevilla",
        37.3860, -6.0030,
        [_c("Nuestro Padre Jesús Nazareno"), _v("Nuestra Señora de la O")],
        salida="16:00", carrera_start="19:15", carrera_end="19:45", recogida="23:30",
    ),
    _entry(
        "Tres Caídas de San Isidoro",
        "Hermandad de las Tres Caídas de San Isidoro",
        "Viernes Santo",
        "Iglesia de San Isidoro", "C. San Isidoro, s/n, Sevilla",
        37.3912, -5.9895,
        [_m("Nuestro Padre Jesús de las Tres Caídas y Nuestra Señora del Loreto"), _v("Nuestra Señora de Loreto")],
        salida="16:00", carrera_start="19:30", carrera_end="20:00", recogida="23:30",
    ),
    _entry(
        "Montserrat",
        "Hermandad de Montserrat",
        "Viernes Santo",
        "Capilla de Montserrat", "C. Cristo del Buen Fin, s/n, Sevilla",
        37.3888, -6.0015,
        [_c("Santísimo Cristo de la Conversión del Buen Ladrón"), _v("Nuestra Señora de Montserrat")],
        salida="16:30", carrera_start="19:45", carrera_end="20:15", recogida="00:00",
    ),
    _entry(
        "Sagrada Mortaja",
        "Hermandad de la Sagrada Mortaja",
        "Viernes Santo",
        "Iglesia de San Gregorio", "C. Alfonso XII, 11, Sevilla",
        37.3895, -5.9858,
        [_m("Sagrada Mortaja de Nuestro Señor Jesucristo"), _v("Nuestra Señora de la Piedad")],
        salida="16:30", carrera_start="20:00", carrera_end="20:30", recogida="00:00",
    ),

    # ========== SÁBADO SANTO ==========
    _entry(
        "El Sol",
        "Hermandad del Sol",
        "Sábado Santo",
        "Parroquia de San Diego de Alcalá", "Barriada del Tardón, Sevilla",
        37.3760, -6.0115,
        [_c("Nuestro Padre Jesús del Amor Despojado"), _v("María Santísima del Sol")],
        salida="15:00", carrera_start="18:00", carrera_end="18:30", recogida="22:00",
    ),
    _entry(
        "Los Servitas",
        "Real Hermandad Servita de Nuestra Señora de los Dolores",
        "Sábado Santo",
        "Capilla de los Dolores", "C. Cervantes, s/n (Plaza de los Dolores), Sevilla",
        37.3880, -5.9900,
        [_v("Nuestra Señora de los Dolores")],
        salida="16:00", carrera_start="18:30", carrera_end="19:00", recogida="21:30",
    ),
    _entry(
        "La Trinidad",
        "Hermandad de la Trinidad",
        "Sábado Santo",
        "Iglesia de la Trinidad", "C. María Auxiliadora, 18, Sevilla",
        37.3870, -5.9850,
        [_c("Santísimo Cristo de las Cinco Llagas"), _v("Nuestra Señora de la Esperanza Trinitaria")],
        salida="16:00", carrera_start="19:00", carrera_end="19:30", recogida="23:00",
    ),
    _entry(
        "El Santo Entierro",
        "Hermandad del Santo Entierro",
        "Sábado Santo",
        "Iglesia de San Gregorio", "C. Alfonso XII, 11, Sevilla",
        37.3895, -5.9858,
        [_c("Santísimo Cristo Yacente"), _m("Santo Entierro de Nuestro Señor Jesucristo"), _v("Nuestra Señora de Villaviciosa")],
        salida="17:00", carrera_start="19:30", carrera_end="20:00", recogida="23:30",
    ),
    _entry(
        "La Soledad (San Lorenzo)",
        "Hermandad de la Soledad de San Lorenzo",
        "Sábado Santo",
        "Iglesia de San Lorenzo", "Plaza de San Lorenzo, s/n, Sevilla",
        37.3933, -5.9990,
        [_v("Nuestra Señora de la Soledad")],
        salida="17:30", carrera_start="20:00", carrera_end="20:30", recogida="23:30",
    ),

    # ========== DOMINGO DE RESURRECCIÓN ==========
    _entry(
        "La Resurrección",
        "Hermandad de la Resurrección",
        "Domingo de Resurrección",
        "Iglesia de Santa Marina", "C. San Luis, s/n, Sevilla",
        37.3957, -5.9890,
        [_c("Nuestro Padre Jesús Resucitado"), _v("Nuestra Señora de la Aurora")],
        salida="07:00", carrera_start="08:30", carrera_end="09:00", recogida="11:00",
    ),
]

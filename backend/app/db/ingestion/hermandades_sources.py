"""Fuentes base para ingestión de hermandades de Sevilla (A1 infra)."""

from typing import Dict

# Mantener bloques por día para documentación e ingestión.
HERMANDADES_SEVILLA_WEBS: Dict[str, str] = {
    # Viernes de Dolores
    "Pino Montano": "https://hermandadpinomontano.es",
    "La Misión": "https://archicofradiamision.es",
    "Dulce Nombre (Bellavista)": "https://www.dulcenombrebellavista.es",
    "Pasión y Muerte": "https://hermandadpasionymuerte.es",
    "Bendición y Esperanza": "https://bendicionyesperanza.es",
    "Stmo. Cristo de la Corona": "https://www.hermandadcristocorona.org",

    # Sábado de Pasión
    "Padre Pío": "https://hermandadpadrepio.com",
    "Divino Perdón": "https://mobile.twitter.com/hdadivinoperdon",
    "Torreblanca": "https://hermandaddelosdolores.org",
    "San José Obrero": "https://hermandadsanjoseobrerosevilla.blogspot.com",
    "La Milagrosa": "https://www.hermandaddelamilagrosa.es",

    # Domingo de Ramos
    "Jesús Despojado": "https://www.jesusdespojado.org",
    "La Paz": "https://www.hermandaddelapaz.org",
    "La Cena": "https://lacenadesevilla.es",
    "La Hiniesta": "https://www.hermandaddelahiniesta.es",
    "San Roque": "https://hermandadsanroque.com",
    "La Estrella": "https://www.hermandad-estrella.org",
    "La Amargura": "https://www.amargura.org",
    "El Amor": "https://hermandaddelamor.net",

    # Lunes Santo
    "Cautivo y Rescatado": "https://jesuscautivoyrescatado.com",
    "Redención -Rocío": "https://hermandadredencion.com",
    "Santa Genoveva": "https://santagenoveva.com",
    "San Gonzalo": "https://hermandaddesangonzalo.es",
    "Santa Marta": "https://hermandaddesantamarta.org",
    "Vera+Cruz": "https://veracruzsevilla.org",
    "Las Penas": "https://www.hermandaddelaspenas.es",
    "Las Aguas": "https://www.hermandaddelasaguas.org",
    "El Museo": "https://www.hermandaddelmuseo.org",

    # Martes Santo
    "San Esteban": "https://www.hermandadsanesteban.org",
    "Dolores del Cerro": "https://www.doloresdelcerro.com",
    "La Candelaria": "https://www.hermandaddelacandelaria.com",
    "San Benito": "https://hermandaddesanbenito.net",
    "Dulce Nombre": "https://hermandaddeldulcenombre.org",
    "Los Javieres": "https://javieres.com",
    "Los Estudiantes": "https://hermandaddelosestudiantes.es",
    "Santa Cruz": "https://www.hermandaddesantacruz.com",

    # Miércoles Santo
    "El Carmen": "https://www.hermandaddelcarmen.es",
    "La Sed": "https://www.hermandaddelased.org",
    "San Bernardo": "https://www.hermandaddesanbernardo.com",
    "Buen Fin": "https://hermandadbuenfin.es",
    "Sagrada Lanzada": "https://lanzada.org",
    "El Baratillo": "https://www.hermandadelbaratillo.es",
    "Cristo de Burgos": "https://www.cristodeburgos.es",
    "Siete Palabras": "https://siete-palabras.com",
    "Los Panaderos": "https://www.hdadpanaderos.es",

    # Jueves Santo
    "Los Negritos": "https://www.hermandadlosnegritos.org",
    "La Exaltación": "https://www.laexaltacion.org",
    "Las Cigarreras": "https://www.columnayazotes.es",
    "Monte-Sión": "https://hermandaddemontesion.com",
    "La Quinta Angustia": "https://laquintaangustia.org",
    "El Valle": "https://www.elvalle.org",
    "Pasión": "https://www.hermandaddepasion.org",

    # Madrugada
    "El Silencio": "https://www.hermandaddeelsilencio.org",
    "Gran Poder": "https://www.gran-poder.es",
    "La Macarena": "https://www.hermandaddelamacarena.es",
    "El Calvario": "https://hermandaddelcalvario.org",
    "Esperanza de Triana": "https://esperanzadetriana.es",
    "Los Gitanos": "https://www.hermandaddelosgitanos.com",

    # Viernes Santo
    "Carretería": "https://hermandaddelacarreteria.org",
    "La Soledad (San Buenaventura)": "https://www.soledadsanbuenaventura.com",
    "El Cachorro": "https://www.hermandaddelcachorro.org",
    "La O": "https://www.hermandaddelao.es",
    "Tres Caídas de San Isidoro": "https://trescaidas.org",
    "Montserrat": "https://www.montserratsevilla.com",
    "Sagrada Mortaja": "https://www.hermandadsagradamortaja.org",

    # Sábado Santo
    "El Sol": "https://hermandaddelsol.org",
    "Los Servitas": "https://realhermandadservita.com",
    "La Trinidad": "https://hermandaddelatrinidad.es",
    "El Santo Entierro": "https://www.santoentierro.org",
    "La Soledad (San Lorenzo)": "https://www.hermandaddelasoledad.org",

    # Domingo de Resurrección
    "La Resurrección": "https://www.hermandaddelaresurreccion.com",
}

DAY_BLOCKS = {
    "Viernes de Dolores": [
        "Pino Montano",
        "La Misión",
        "Dulce Nombre (Bellavista)",
        "Pasión y Muerte",
        "Bendición y Esperanza",
        "Stmo. Cristo de la Corona",
    ],
    "Sábado de Pasión": ["Padre Pío", "Divino Perdón", "Torreblanca", "San José Obrero", "La Milagrosa"],
    "Domingo de Ramos": [
        "Jesús Despojado",
        "La Paz",
        "La Cena",
        "La Hiniesta",
        "San Roque",
        "La Estrella",
        "La Amargura",
        "El Amor",
    ],
    "Lunes Santo": [
        "Cautivo y Rescatado",
        "Redención -Rocío",
        "Santa Genoveva",
        "San Gonzalo",
        "Santa Marta",
        "Vera+Cruz",
        "Las Penas",
        "Las Aguas",
        "El Museo",
    ],
    "Martes Santo": [
        "San Esteban",
        "Dolores del Cerro",
        "La Candelaria",
        "San Benito",
        "Dulce Nombre",
        "Los Javieres",
        "Los Estudiantes",
        "Santa Cruz",
    ],
    "Miércoles Santo": [
        "El Carmen",
        "La Sed",
        "San Bernardo",
        "Buen Fin",
        "Sagrada Lanzada",
        "El Baratillo",
        "Cristo de Burgos",
        "Siete Palabras",
        "Los Panaderos",
    ],
    "Jueves Santo": [
        "Los Negritos",
        "La Exaltación",
        "Las Cigarreras",
        "Monte-Sión",
        "La Quinta Angustia",
        "El Valle",
        "Pasión",
    ],
    "Madrugada": ["El Silencio", "Gran Poder", "La Macarena", "El Calvario", "Esperanza de Triana", "Los Gitanos"],
    "Viernes Santo": [
        "Carretería",
        "La Soledad (San Buenaventura)",
        "El Cachorro",
        "La O",
        "Tres Caídas de San Isidoro",
        "Montserrat",
        "Sagrada Mortaja",
    ],
    "Sábado Santo": ["El Sol", "Los Servitas", "La Trinidad", "El Santo Entierro", "La Soledad (San Lorenzo)"],
    "Domingo de Resurrección": ["La Resurrección"],
}

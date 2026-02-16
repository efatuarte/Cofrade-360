import 'package:latlong2/latlong.dart';

/// Coordenadas hardcodeadas de la Carrera Oficial y puntos de interés
/// del centro histórico de Sevilla para Semana Santa.
class SevilleRoutes {
  SevilleRoutes._();

  /// Centro aproximado de la ruta (Plaza de San Francisco)
  static final LatLng routeCenter = LatLng(37.38870, -5.99460);

  /// Zoom para ver la ruta completa
  static const double defaultZoom = 16.0;

  /// Carrera Oficial completa:
  /// La Campana → Calle Sierpes → Plaza de San Francisco →
  /// Av. de la Constitución → Catedral
  static final List<LatLng> carreraOficial = [
    // ── La Campana (inicio) ──
    LatLng(37.39252, -5.99410),
    LatLng(37.39220, -5.99425),

    // ── Calle Sierpes (peatonal, hacia el sur) ──
    LatLng(37.39180, -5.99438),
    LatLng(37.39130, -5.99450),
    LatLng(37.39075, -5.99460),
    LatLng(37.39020, -5.99468),
    LatLng(37.38965, -5.99475),
    LatLng(37.38920, -5.99478),

    // ── Plaza de San Francisco ──
    LatLng(37.38875, -5.99480),
    LatLng(37.38840, -5.99472),

    // ── Calle Hernando Colón ──
    LatLng(37.38795, -5.99450),
    LatLng(37.38750, -5.99430),

    // ── Av. de la Constitución (hacia la Catedral) ──
    LatLng(37.38700, -5.99415),
    LatLng(37.38645, -5.99400),
    LatLng(37.38590, -5.99385),
    LatLng(37.38535, -5.99370),
    LatLng(37.38480, -5.99355),

    // ── Catedral (final) ──
    LatLng(37.38430, -5.99340),
    LatLng(37.38386, -5.99320),
  ];

  /// Ruta extendida por calles aledañas del casco antiguo:
  /// Catedral → Plaza del Triunfo → Archivo de Indias →
  /// Puerta de Jerez → vuelve por Calle Tetuán → La Campana
  static final List<LatLng> rutaCentroExtendida = [
    // ── Desde Catedral hacia el sur ──
    LatLng(37.38386, -5.99320),
    LatLng(37.38350, -5.99280),

    // ── Plaza del Triunfo ──
    LatLng(37.38320, -5.99220),
    LatLng(37.38290, -5.99180),

    // ── Archivo de Indias (bordeando) ──
    LatLng(37.38280, -5.99250),
    LatLng(37.38310, -5.99310),

    // ── Av. de la Constitución (subiendo de vuelta) ──
    LatLng(37.38400, -5.99350),
    LatLng(37.38500, -5.99380),
    LatLng(37.38600, -5.99400),
    LatLng(37.38700, -5.99420),

    // ── Plaza Nueva ──
    LatLng(37.38810, -5.99510),
    LatLng(37.38850, -5.99560),

    // ── Calle Tetuán (paralela a Sierpes, hacia el norte) ──
    LatLng(37.38910, -5.99550),
    LatLng(37.38970, -5.99540),
    LatLng(37.39040, -5.99530),
    LatLng(37.39110, -5.99510),
    LatLng(37.39170, -5.99490),

    // ── De vuelta a La Campana ──
    LatLng(37.39220, -5.99460),
    LatLng(37.39252, -5.99410),
  ];

  /// Landmarks a lo largo de la ruta
  static final List<MapLandmark> landmarks = [
    MapLandmark(
      position: LatLng(37.39252, -5.99410),
      label: 'La Campana',
      kind: LandmarkKind.start,
    ),
    MapLandmark(
      position: LatLng(37.39100, -5.99455),
      label: 'Calle Sierpes',
      kind: LandmarkKind.waypoint,
    ),
    MapLandmark(
      position: LatLng(37.38875, -5.99480),
      label: 'Plaza de San Francisco',
      kind: LandmarkKind.waypoint,
    ),
    MapLandmark(
      position: LatLng(37.38810, -5.99510),
      label: 'Plaza Nueva',
      kind: LandmarkKind.waypoint,
    ),
    MapLandmark(
      position: LatLng(37.38386, -5.99320),
      label: 'Catedral',
      kind: LandmarkKind.end,
    ),
    MapLandmark(
      position: LatLng(37.38290, -5.99180),
      label: 'Archivo de Indias',
      kind: LandmarkKind.waypoint,
    ),
  ];
}

enum LandmarkKind { start, waypoint, end }

class MapLandmark {
  final LatLng position;
  final String label;
  final LandmarkKind kind;

  const MapLandmark({
    required this.position,
    required this.label,
    required this.kind,
  });
}

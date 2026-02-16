import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../data/seville_routes.dart';

/// Colores de marca (evita dependencia directa de app_theme para reutilización)
const _kCrimson = Color(0xFF8B1538);
const _kGold = Color(0xFFD4AF37);

class ModoCalleMap extends StatefulWidget {
  /// Polyline recibida del backend ([lat, lng] pairs).
  final List<List<double>> backendPolyline;

  /// Si true, aplica perspectiva 3D con tilt.
  final bool is3DView;

  /// Posición simulada del usuario.
  final LatLng? userPosition;

  const ModoCalleMap({
    super.key,
    required this.backendPolyline,
    required this.is3DView,
    this.userPosition,
  });

  @override
  State<ModoCalleMap> createState() => ModoCalleMapState();
}

class ModoCalleMapState extends State<ModoCalleMap> {
  late final MapController _mapController;

  @override
  void initState() {
    super.initState();
    _mapController = MapController();
  }

  @override
  void dispose() {
    _mapController.dispose();
    super.dispose();
  }

  /// Centra el mapa en la ruta hardcodeada.
  void centerOnRoute() {
    _mapController.move(SevilleRoutes.routeCenter, SevilleRoutes.defaultZoom);
  }

  List<LatLng> _convertBackendPolyline() {
    return widget.backendPolyline
        .where((p) => p.length >= 2)
        .map((p) => LatLng(p[0], p[1]))
        .toList();
  }

  @override
  Widget build(BuildContext context) {
    final backendPoints = _convertBackendPolyline();

    final mapWidget = FlutterMap(
      mapController: _mapController,
      options: MapOptions(
        initialCenter: SevilleRoutes.routeCenter,
        initialZoom: SevilleRoutes.defaultZoom,
        minZoom: 13,
        maxZoom: 19,
        initialRotation: widget.is3DView ? -15.0 : 0.0,
      ),
      children: [
        // Tiles OpenStreetMap
        TileLayer(
          urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
          userAgentPackageName: 'com.cofrade360.app',
          maxZoom: 19,
        ),

        // Ruta extendida por el centro (fondo, más fina)
        PolylineLayer(
          polylines: [
            Polyline(
              points: SevilleRoutes.rutaCentroExtendida,
              color: _kGold.withValues(alpha: 0.5),
              strokeWidth: 3.0,
            ),
          ],
        ),

        // Carrera Oficial (ruta principal, gruesa)
        PolylineLayer(
          polylines: [
            Polyline(
              points: SevilleRoutes.carreraOficial,
              color: _kCrimson.withValues(alpha: 0.85),
              strokeWidth: 5.0,
            ),
          ],
        ),

        // Ruta del backend (si existe, punteada en gold)
        if (backendPoints.isNotEmpty)
          PolylineLayer(
            polylines: [
              Polyline(
                points: backendPoints,
                color: _kGold,
                strokeWidth: 4.0,
              ),
            ],
          ),

        // Markers de landmarks
        MarkerLayer(
          markers: [
            ...SevilleRoutes.landmarks.map(
              (lm) => Marker(
                point: lm.position,
                width: 36,
                height: 36,
                child: Tooltip(
                  message: lm.label,
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withValues(alpha: 0.3),
                          blurRadius: 4,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Icon(
                      _landmarkIcon(lm.kind),
                      color: _kCrimson,
                      size: 22,
                    ),
                  ),
                ),
              ),
            ),

            // Posición del usuario
            if (widget.userPosition != null)
              Marker(
                point: widget.userPosition!,
                width: 28,
                height: 28,
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.blue.withValues(alpha: 0.25),
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.blue, width: 2.5),
                  ),
                  child: const Icon(
                    Icons.navigation,
                    color: Colors.blue,
                    size: 16,
                  ),
                ),
              ),
          ],
        ),

        // Atribución OSM
        const RichAttributionWidget(
          attributions: [
            TextSourceAttribution('OpenStreetMap contributors'),
          ],
        ),
      ],
    );

    // Envolver con perspectiva 3D animada
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: widget.is3DView ? 1.0 : 0.0),
      duration: const Duration(milliseconds: 400),
      curve: Curves.easeInOut,
      builder: (context, t, child) {
        if (t < 0.01) return child!;

        return Transform(
          alignment: Alignment.bottomCenter,
          transform: Matrix4.identity()
            ..setEntry(3, 2, 0.001 * t) // perspectiva
            ..rotateX(0.5 * t), // tilt ~28°
          child: child,
        );
      },
      child: mapWidget,
    );
  }

  IconData _landmarkIcon(LandmarkKind kind) {
    switch (kind) {
      case LandmarkKind.start:
        return Icons.flag_rounded;
      case LandmarkKind.end:
        return Icons.church;
      case LandmarkKind.waypoint:
        return Icons.place;
    }
  }
}

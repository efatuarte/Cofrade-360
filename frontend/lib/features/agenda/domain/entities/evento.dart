import 'package:equatable/equatable.dart';

class LocationEntity extends Equatable {
  final String id;
  final String name;
  final String? address;
  final double? lat;
  final double? lng;
  final String? kind;

  const LocationEntity({
    required this.id,
    required this.name,
    this.address,
    this.lat,
    this.lng,
    this.kind,
  });

  @override
  List<Object?> get props => [id, name, address, lat, lng, kind];
}

class Evento extends Equatable {
  final String id;
  final String titulo;
  final String? descripcion;
  final String tipo;
  final DateTime fechaInicio;
  final DateTime? fechaFin;
  final String? locationId;
  final String? hermandadId;
  final double precio;
  final String moneda;
  final bool esGratuito;
  final String? posterAssetId;
  final String estado;
  final DateTime createdAt;
  final LocationEntity? location;

  const Evento({
    required this.id,
    required this.titulo,
    this.descripcion,
    required this.tipo,
    required this.fechaInicio,
    this.fechaFin,
    this.locationId,
    this.hermandadId,
    this.precio = 0,
    this.moneda = 'EUR',
    this.esGratuito = true,
    this.posterAssetId,
    this.estado = 'programado',
    required this.createdAt,
    this.location,
  });

  /// Atajo útil para UI (equivale a "ubicacion" antigua)
  String? get ubicacionTexto => location?.name ?? location?.address;

  @override
  List<Object?> get props => [id, titulo, tipo, fechaInicio, estado];
}

class PaginatedEventos {
  final List<Evento> items;
  final int page;
  final int pageSize;
  final int total;

  const PaginatedEventos({
    required this.items,
    required this.page,
    required this.pageSize,
    required this.total,
  });

  bool get hasNextPage => page * pageSize < total;
}

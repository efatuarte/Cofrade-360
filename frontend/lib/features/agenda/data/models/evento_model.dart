import '../../domain/entities/evento.dart';

class LocationModel {
  final String id;
  final String name;
  final String? address;
  final double? lat;
  final double? lng;
  final String? kind;

  LocationModel({
    required this.id,
    required this.name,
    this.address,
    this.lat,
    this.lng,
    this.kind,
  });

  factory LocationModel.fromJson(Map<String, dynamic> json) {
    return LocationModel(
      id: json['id'] as String,
      name: json['name'] as String,
      address: json['address'] as String?,
      lat: (json['lat'] as num?)?.toDouble(),
      lng: (json['lng'] as num?)?.toDouble(),
      kind: json['kind'] as String?,
    );
  }

  LocationEntity toEntity() => LocationEntity(
        id: id,
        name: name,
        address: address,
        lat: lat,
        lng: lng,
        kind: kind,
      );
}

class EventoModel {
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
  final LocationModel? location;

  EventoModel({
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

  factory EventoModel.fromJson(Map<String, dynamic> json) {
    return EventoModel(
      id: json['id'] as String,
      titulo: json['titulo'] as String,
      descripcion: json['descripcion'] as String?,
      tipo: (json['tipo'] as String?) ?? 'otro',
      fechaInicio: DateTime.parse(json['fecha_inicio'] as String),
      fechaFin: json['fecha_fin'] != null
          ? DateTime.parse(json['fecha_fin'] as String)
          : null,
      locationId: json['location_id'] as String?,
      hermandadId: json['hermandad_id'] as String?,
      precio: (json['precio'] as num?)?.toDouble() ?? 0,
      moneda: (json['moneda'] as String?) ?? 'EUR',
      esGratuito: (json['es_gratuito'] as bool?) ?? true,
      posterAssetId: json['poster_asset_id'] as String?,
      estado: (json['estado'] as String?) ?? 'programado',
      createdAt: DateTime.parse(json['created_at'] as String),
      location: json['location'] != null
          ? LocationModel.fromJson(json['location'] as Map<String, dynamic>)
          : null,
    );
  }

  Evento toEntity() => Evento(
        id: id,
        titulo: titulo,
        descripcion: descripcion,
        tipo: tipo,
        fechaInicio: fechaInicio,
        fechaFin: fechaFin,
        locationId: locationId,
        hermandadId: hermandadId,
        precio: precio,
        moneda: moneda,
        esGratuito: esGratuito,
        posterAssetId: posterAssetId,
        estado: estado,
        createdAt: createdAt,
        location: location?.toEntity(),
      );
}

/// Parse the paginated API response into domain [PaginatedEventos].
PaginatedEventos parsePaginatedEventos(Map<String, dynamic> json) {
  final rawItems = json['items'] as List<dynamic>;
  return PaginatedEventos(
    items: rawItems
        .map((e) => EventoModel.fromJson(e as Map<String, dynamic>).toEntity())
        .toList(),
    page: json['page'] as int,
    pageSize: json['page_size'] as int,
    total: json['total'] as int,
  );
}

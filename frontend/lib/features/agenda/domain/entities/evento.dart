import 'package:equatable/equatable.dart';

class Evento extends Equatable {
  final String id;
  final String titulo;
  final String descripcion;
  final DateTime fechaHora;
  final String hermandadId;
  final String? ubicacion;

  const Evento({
    required this.id,
    required this.titulo,
    required this.descripcion,
    required this.fechaHora,
    required this.hermandadId,
    this.ubicacion,
  });

  @override
  List<Object?> get props => [id, titulo, descripcion, fechaHora, hermandadId, ubicacion];
}

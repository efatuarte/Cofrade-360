import 'package:equatable/equatable.dart';

class Hermandad extends Equatable {
  final String id;
  final String nombre;
  final String descripcion;
  final String escudo;
  final String sede;
  final DateTime fechaFundacion;
  final List<String> imagenesTitulares;

  const Hermandad({
    required this.id,
    required this.nombre,
    required this.descripcion,
    required this.escudo,
    required this.sede,
    required this.fechaFundacion,
    required this.imagenesTitulares,
  });

  @override
  List<Object?> get props => [id, nombre, descripcion, escudo, sede, fechaFundacion, imagenesTitulares];
}

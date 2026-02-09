import 'package:dartz/dartz.dart';
import '../../../../core/errors/failures.dart';
import '../../domain/entities/evento.dart';
import '../../domain/repositories/agenda_repository.dart';

class AgendaRepositoryImpl implements AgendaRepository {
  // Mock data for now
  final List<Evento> _mockEventos = [
    Evento(
      id: '1',
      titulo: 'Pregón de Semana Santa',
      descripcion: 'Pregón oficial de la Semana Santa de Sevilla',
      fechaHora: DateTime(2026, 4, 3, 20, 0),
      hermandadId: '1',
      ubicacion: 'Teatro de la Maestranza',
    ),
    Evento(
      id: '2',
      titulo: 'Vía Crucis Magno',
      descripcion: 'Vía Crucis con todas las hermandades',
      fechaHora: DateTime(2026, 4, 4, 18, 0),
      hermandadId: '2',
      ubicacion: 'Plaza de San Francisco',
    ),
    Evento(
      id: '3',
      titulo: 'Procesión del Silencio',
      descripcion: 'Procesión de Viernes Santo',
      fechaHora: DateTime(2026, 4, 10, 22, 0),
      hermandadId: '3',
      ubicacion: 'Catedral de Sevilla',
    ),
  ];

  @override
  Future<Either<Failure, List<Evento>>> getEventos() async {
    try {
      // Simulate network delay
      await Future.delayed(const Duration(milliseconds: 500));
      return Right(_mockEventos);
    } catch (e) {
      return Left(ServerFailure(e.toString()));
    }
  }

  @override
  Future<Either<Failure, Evento>> getEventoById(String id) async {
    try {
      await Future.delayed(const Duration(milliseconds: 300));
      final evento = _mockEventos.firstWhere((e) => e.id == id);
      return Right(evento);
    } catch (e) {
      return Left(ServerFailure('Evento no encontrado'));
    }
  }
}

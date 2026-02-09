import 'package:dartz/dartz.dart';
import '../../../../core/errors/failures.dart';
import '../entities/evento.dart';

abstract class AgendaRepository {
  Future<Either<Failure, List<Evento>>> getEventos();
  Future<Either<Failure, Evento>> getEventoById(String id);
}

import 'package:dartz/dartz.dart';
import '../../../../core/errors/failures.dart';
import '../entities/evento.dart';

abstract class AgendaRepository {
  Future<Either<Failure, PaginatedEventos>> getEventos({
    int page = 1,
    int pageSize = 20,
    String? tipo,
    String? q,
    DateTime? fromDate,
    DateTime? toDate,
  });

  Future<Either<Failure, Evento>> getEventoById(String id);
}

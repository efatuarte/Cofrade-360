import 'package:dartz/dartz.dart';

import '../../../../core/errors/failures.dart';
import '../entities/evento.dart';
import '../repositories/agenda_repository.dart';

class GetEventos {
  final AgendaRepository repository;

  GetEventos(this.repository);

  /// Devuelve solo la lista de eventos (extraída de PaginatedEventos.items)
  Future<Either<Failure, List<Evento>>> call({
    int page = 1,
    int pageSize = 20,
    String? tipo,
    String? q,
    DateTime? fromDate,
    DateTime? toDate,
  }) async {
    final result = await repository.getEventos(
      page: page,
      pageSize: pageSize,
      tipo: tipo,
      q: q,
      fromDate: fromDate,
      toDate: toDate,
    );

    return result.map((paginated) => paginated.items);
  }
}

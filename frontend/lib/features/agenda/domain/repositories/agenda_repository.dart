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

  Future<Either<Failure, EventPoster>> getPosterUrl(String id);
}


class EventPoster {
  final String assetId;
  final String url;

  const EventPoster({required this.assetId, required this.url});
}

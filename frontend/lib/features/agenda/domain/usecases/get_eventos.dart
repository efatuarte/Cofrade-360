import '../entities/evento.dart';
import '../repositories/agenda_repository.dart';
import 'package:dartz/dartz.dart';
import '../../../../core/errors/failures.dart';

class GetEventos {
  final AgendaRepository repository;

  GetEventos(this.repository);

  Future<Either<Failure, List<Evento>>> call() {
    return repository.getEventos();
  }
}

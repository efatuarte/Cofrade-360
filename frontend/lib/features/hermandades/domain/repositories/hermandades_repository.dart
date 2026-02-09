import 'package:dartz/dartz.dart';
import '../../../../core/errors/failures.dart';
import '../entities/hermandad.dart';

abstract class HermandadesRepository {
  Future<Either<Failure, List<Hermandad>>> getHermandades();
  Future<Either<Failure, Hermandad>> getHermandadById(String id);
}

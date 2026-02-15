import 'package:dartz/dartz.dart';

import '../../../../core/errors/failures.dart';
import '../entities/hermandad.dart';

abstract class HermandadesRepository {
  Future<Either<Failure, PaginatedHermandades>> getHermandades({
    String? q,
    String? day,
    int page = 1,
    int pageSize = 20,
  });

  Future<Either<Failure, Hermandad>> getHermandadById(String id);

  Future<Either<Failure, List<BrotherhoodMedia>>> getMediaByBrotherhood(String id);

  Future<Either<Failure, String>> getSignedMediaByAsset(String assetId);
}

import 'package:dartz/dartz.dart';

import '../../../../core/errors/failures.dart';
import '../entities/plan.dart';

abstract class ItinerarioRepository {
  Future<Either<Failure, List<UserPlanEntity>>> getPlans({DateTime? fromDate, DateTime? toDate});

  Future<Either<Failure, UserPlanEntity>> createPlan({required String title, required DateTime planDate});

  Future<Either<Failure, AddItemResult>> addItem({
    required String planId,
    required String itemType,
    String? eventId,
    String? brotherhoodId,
    required DateTime desiredTimeStart,
    required DateTime desiredTimeEnd,
    double? lat,
    double? lng,
    String? notes,
  });

  Future<Either<Failure, List<PlanItemEntity>>> optimizePlan(String planId);
}

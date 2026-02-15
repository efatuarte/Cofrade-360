import 'package:dartz/dartz.dart';
import 'package:dio/dio.dart';

import '../../../../core/errors/failures.dart';
import '../../../../core/network/api_client.dart';
import '../../domain/entities/plan.dart';
import '../../domain/repositories/itinerario_repository.dart';

class ItinerarioRepositoryImpl implements ItinerarioRepository {
  final ApiClient apiClient;

  ItinerarioRepositoryImpl({required this.apiClient});

  String _messageFromDio(DioException e) {
    if (e.response == null) return 'No se pudo conectar con el servidor.';
    final data = e.response?.data;
    if (data is Map<String, dynamic> && data['detail'] != null) {
      return data['detail'].toString();
    }
    return 'Error HTTP ${e.response?.statusCode}';
  }

  PlanItemWarning _parseWarning(Map<String, dynamic> json) {
    return PlanItemWarning(
      itemId: json['item_id'] as String,
      conflictWithItemId: json['conflict_with_item_id'] as String,
      detail: json['detail'] as String,
    );
  }

  PlanItemEntity _parseItem(Map<String, dynamic> json) {
    return PlanItemEntity(
      id: json['id'] as String,
      planId: json['plan_id'] as String,
      itemType: json['item_type'] as String,
      eventId: json['event_id'] as String?,
      brotherhoodId: json['brotherhood_id'] as String?,
      desiredTimeStart: DateTime.parse(json['desired_time_start'] as String),
      desiredTimeEnd: DateTime.parse(json['desired_time_end'] as String),
      lat: (json['lat'] as num?)?.toDouble(),
      lng: (json['lng'] as num?)?.toDouble(),
      position: json['position'] as int,
      notes: json['notes'] as String?,
    );
  }

  UserPlanEntity _parsePlan(Map<String, dynamic> json) {
    final items = (json['items'] as List<dynamic>? ?? [])
        .map((item) => _parseItem(item as Map<String, dynamic>))
        .toList();
    return UserPlanEntity(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      title: json['title'] as String,
      planDate: DateTime.parse(json['plan_date'] as String),
      items: items,
    );
  }

  @override
  Future<Either<Failure, List<UserPlanEntity>>> getPlans({DateTime? fromDate, DateTime? toDate}) async {
    try {
      final response = await apiClient.dio.get(
        '/me/plans',
        queryParameters: {
          if (fromDate != null) 'from': fromDate.toIso8601String(),
          if (toDate != null) 'to': toDate.toIso8601String(),
        },
      );
      final plans = (response.data as List<dynamic>)
          .map((item) => _parsePlan(item as Map<String, dynamic>))
          .toList();
      return Right(plans);
    } on DioException catch (e) {
      return Left(ServerFailure(_messageFromDio(e)));
    } catch (e) {
      return Left(ServerFailure(e.toString()));
    }
  }

  @override
  Future<Either<Failure, UserPlanEntity>> createPlan({required String title, required DateTime planDate}) async {
    try {
      final response = await apiClient.dio.post(
        '/me/plans',
        data: {'title': title, 'plan_date': planDate.toIso8601String()},
      );
      return Right(_parsePlan(response.data as Map<String, dynamic>));
    } on DioException catch (e) {
      return Left(ServerFailure(_messageFromDio(e)));
    } catch (e) {
      return Left(ServerFailure(e.toString()));
    }
  }

  @override
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
  }) async {
    try {
      final response = await apiClient.dio.post(
        '/me/plans/$planId/items',
        data: {
          'item_type': itemType,
          if (eventId != null) 'event_id': eventId,
          if (brotherhoodId != null) 'brotherhood_id': brotherhoodId,
          'desired_time_start': desiredTimeStart.toIso8601String(),
          'desired_time_end': desiredTimeEnd.toIso8601String(),
          'lat': lat,
          'lng': lng,
          'notes': notes,
        },
      );
      final json = response.data as Map<String, dynamic>;
      return Right(
        AddItemResult(
          item: _parseItem(json['item'] as Map<String, dynamic>),
          warnings: (json['warnings'] as List<dynamic>)
              .map((w) => _parseWarning(w as Map<String, dynamic>))
              .toList(),
        ),
      );
    } on DioException catch (e) {
      return Left(ServerFailure(_messageFromDio(e)));
    } catch (e) {
      return Left(ServerFailure(e.toString()));
    }
  }

  @override
  Future<Either<Failure, List<PlanItemEntity>>> optimizePlan(String planId) async {
    try {
      final response = await apiClient.dio.post('/me/plans/$planId/optimize');
      final json = response.data as Map<String, dynamic>;
      final items = (json['items'] as List<dynamic>)
          .map((item) => _parseItem(item as Map<String, dynamic>))
          .toList();
      return Right(items);
    } on DioException catch (e) {
      return Left(ServerFailure(_messageFromDio(e)));
    } catch (e) {
      return Left(ServerFailure(e.toString()));
    }
  }
}

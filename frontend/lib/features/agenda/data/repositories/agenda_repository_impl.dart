import 'package:dartz/dartz.dart';
import 'package:dio/dio.dart';

import '../../../../core/errors/failures.dart';
import '../../../../core/network/api_client.dart';
import '../../domain/entities/evento.dart';
import '../../domain/repositories/agenda_repository.dart';
import '../models/evento_model.dart';

class AgendaRepositoryImpl implements AgendaRepository {
  final ApiClient apiClient;

  AgendaRepositoryImpl({required this.apiClient});

  String _messageFromDio(DioException e) {
    if (e.response == null) {
      return 'No se pudo conectar con el servidor.';
    }
    final data = e.response?.data;
    if (data is Map<String, dynamic> && data['detail'] != null) {
      return data['detail'].toString();
    }
    return 'Error HTTP ${e.response?.statusCode}';
  }

  @override
  Future<Either<Failure, PaginatedEventos>> getEventos({
    int page = 1,
    int pageSize = 20,
    String? tipo,
    String? q,
    DateTime? fromDate,
    DateTime? toDate,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'page_size': pageSize,
      };
      if (tipo != null) queryParams['tipo'] = tipo;
      if (q != null && q.isNotEmpty) queryParams['q'] = q;
      if (fromDate != null) queryParams['from'] = fromDate.toIso8601String();
      if (toDate != null) queryParams['to'] = toDate.toIso8601String();

      final response = await apiClient.dio.get(
        '/events',
        queryParameters: queryParams,
      );

      final paginated =
          parsePaginatedEventos(response.data as Map<String, dynamic>);
      return Right(paginated);
    } on DioException catch (e) {
      return Left(ServerFailure(_messageFromDio(e)));
    } catch (e) {
      return Left(ServerFailure(e.toString()));
    }
  }

  @override
  Future<Either<Failure, Evento>> getEventoById(String id) async {
    try {
      final response = await apiClient.dio.get('/events/$id');
      final modelo =
          EventoModel.fromJson(response.data as Map<String, dynamic>);
      return Right(modelo.toEntity());
    } on DioException catch (e) {
      return Left(ServerFailure(_messageFromDio(e)));
    } catch (e) {
      return Left(ServerFailure(e.toString()));
    }
  }
}

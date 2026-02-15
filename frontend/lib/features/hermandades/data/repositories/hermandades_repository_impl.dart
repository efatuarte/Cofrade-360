import 'package:dartz/dartz.dart';
import 'package:dio/dio.dart';

import '../../../../core/errors/failures.dart';
import '../../../../core/network/api_client.dart';
import '../../domain/entities/hermandad.dart';
import '../../domain/repositories/hermandades_repository.dart';

class HermandadesRepositoryImpl implements HermandadesRepository {
  final ApiClient apiClient;

  HermandadesRepositoryImpl({required this.apiClient});

  String _messageFromDio(DioException e) {
    if (e.response == null) return 'No se pudo conectar con el servidor.';
    final data = e.response?.data;
    if (data is Map<String, dynamic> && data['detail'] != null) {
      return data['detail'].toString();
    }
    return 'Error HTTP ${e.response?.statusCode}';
  }

  Hermandad _parseBrotherhood(Map<String, dynamic> json) {
    final church = json['church'] as Map<String, dynamic>?;
    return Hermandad(
      id: json['id'] as String,
      nameShort: (json['name_short'] as String?) ?? (json['nombre'] as String? ?? 'Hermandad'),
      nameFull: (json['name_full'] as String?) ?? (json['nombre'] as String? ?? 'Hermandad'),
      logoAssetId: json['logo_asset_id'] as String?,
      churchId: json['church_id'] as String?,
      ssDay: json['ss_day'] as String?,
      history: json['history'] as String?,
      highlights: json['highlights'] as String?,
      stats: json['stats'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      churchName: church?['name'] as String?,
    );
  }

  @override
  Future<Either<Failure, PaginatedHermandades>> getHermandades({
    String? q,
    String? day,
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final response = await apiClient.dio.get(
        '/brotherhoods',
        queryParameters: {
          'page': page,
          'page_size': pageSize,
          if (q != null && q.isNotEmpty) 'q': q,
          if (day != null && day.isNotEmpty) 'day': day,
        },
      );
      final data = response.data as Map<String, dynamic>;
      final items = (data['items'] as List<dynamic>)
          .map((item) => _parseBrotherhood(item as Map<String, dynamic>))
          .toList();
      return Right(
        PaginatedHermandades(
          items: items,
          page: data['page'] as int,
          pageSize: data['page_size'] as int,
          total: data['total'] as int,
        ),
      );
    } on DioException catch (e) {
      return Left(ServerFailure(_messageFromDio(e)));
    } catch (e) {
      return Left(ServerFailure(e.toString()));
    }
  }

  @override
  Future<Either<Failure, Hermandad>> getHermandadById(String id) async {
    try {
      final response = await apiClient.dio.get('/brotherhoods/$id');
      return Right(_parseBrotherhood(response.data as Map<String, dynamic>));
    } on DioException catch (e) {
      return Left(ServerFailure(_messageFromDio(e)));
    } catch (e) {
      return Left(ServerFailure(e.toString()));
    }
  }

  @override
  Future<Either<Failure, List<BrotherhoodMedia>>> getMediaByBrotherhood(String id) async {
    try {
      final response = await apiClient.dio.get('/brotherhoods/$id/media');
      final items = (response.data as List<dynamic>)
          .map(
            (item) => BrotherhoodMedia(
              assetId: (item as Map<String, dynamic>)['asset_id'] as String,
              url: item['url'] as String,
            ),
          )
          .toList();
      return Right(items);
    } on DioException catch (e) {
      return Left(ServerFailure(_messageFromDio(e)));
    } catch (e) {
      return Left(ServerFailure(e.toString()));
    }
  }

  @override
  Future<Either<Failure, String>> getSignedMediaByAsset(String assetId) async {
    try {
      final response = await apiClient.dio.get('/media/$assetId');
      return Right((response.data as Map<String, dynamic>)['url'] as String);
    } on DioException catch (e) {
      return Left(ServerFailure(_messageFromDio(e)));
    } catch (e) {
      return Left(ServerFailure(e.toString()));
    }
  }
}

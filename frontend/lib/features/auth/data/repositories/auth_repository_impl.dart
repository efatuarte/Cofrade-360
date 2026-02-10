import 'package:dartz/dartz.dart';
import 'package:dio/dio.dart';

import '../../../../core/errors/failures.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/storage/token_storage.dart';
import '../../domain/entities/user.dart';
import '../../domain/repositories/auth_repository.dart';
import '../models/user_model.dart';

class AuthRepositoryImpl implements AuthRepository {
  final ApiClient apiClient;
  final TokenStorage tokenStorage;

  AuthRepositoryImpl({
    required this.apiClient,
    required this.tokenStorage,
  });

  String _messageFromDio(DioException e) {
    // Sin response => conectividad / DNS / refused
    if (e.response == null) {
      return 'No se pudo conectar con el servidor. Revisa baseUrl y que FastAPI esté corriendo.';
    }
    final data = e.response?.data;
    if (data is Map<String, dynamic> && data['detail'] != null) {
      return data['detail'].toString();
    }
    return 'Error HTTP ${e.response?.statusCode}';
  }

  @override
  Future<Either<Failure, User>> register({
    required String email,
    required String password,
  }) async {
    try {
      final response = await apiClient.dio.post(
        '/auth/register',
        data: {'email': email, 'password': password},
      );

      final userModel = UserModel.fromJson(response.data);
      return Right(userModel.toEntity());
    } on DioException catch (e) {
      return Left(ServerFailure(_messageFromDio(e)));
    } catch (e) {
      return Left(ServerFailure(e.toString()));
    }
  }

  @override
  Future<Either<Failure, User>> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await apiClient.dio.post(
        '/auth/login',
        data: {'email': email, 'password': password},
      );

      final tokenResponse = TokenResponse.fromJson(response.data);

      await tokenStorage.saveTokens(
        accessToken: tokenResponse.accessToken,
        refreshToken: tokenResponse.refreshToken,
      );

      // OJO: esto requiere que tu API tenga /auth/me implementado.
      return await getCurrentUser();
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        return Left(ServerFailure('Incorrect email or password'));
      }
      return Left(ServerFailure(_messageFromDio(e)));
    } catch (e) {
      return Left(ServerFailure(e.toString()));
    }
  }

  @override
  Future<Either<Failure, User>> getCurrentUser() async {
    try {
      final response = await apiClient.dio.get('/auth/me');
      final userModel = UserModel.fromJson(response.data);
      return Right(userModel.toEntity());
    } on DioException catch (e) {
      return Left(ServerFailure(_messageFromDio(e)));
    } catch (e) {
      return Left(ServerFailure(e.toString()));
    }
  }

  @override
  Future<Either<Failure, void>> logout() async {
    try {
      await apiClient.dio.post('/auth/logout');
    } catch (_) {
      // Ignora fallo remoto, limpiamos tokens igual
    }
    await tokenStorage.clearTokens();
    return const Right(null);
  }

  @override
  Future<bool> isAuthenticated() async {
    return await tokenStorage.hasTokens();
  }
}

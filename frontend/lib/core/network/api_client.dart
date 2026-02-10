import 'dart:io';
import 'package:dio/dio.dart';
import '../storage/token_storage.dart';

class ApiClient {
  // Puedes sobreescribirlo al ejecutar:
  // flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
  static const String _envBaseUrl =
      String.fromEnvironment('API_BASE_URL', defaultValue: '');

  static String get baseUrl {
    if (_envBaseUrl.isNotEmpty) return _envBaseUrl;

    // Defaults por plataforma
    if (Platform.isAndroid) {
      // Android Emulator -> host machine
      return 'http://10.0.2.2:8000/api/v1';
    }

    // iOS Simulator suele poder usar localhost
    return 'http://localhost:8000/api/v1';
  }

  late final Dio _dio;
  late final Dio _dioNoAuth; // para refresh sin interceptores
  final TokenStorage _tokenStorage;

  ApiClient(this._tokenStorage) {
    _dio = Dio(
      BaseOptions(
        baseUrl: baseUrl,
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 15),
        headers: const {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    _dioNoAuth = Dio(
      BaseOptions(
        baseUrl: baseUrl,
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 15),
        headers: const {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final accessToken = await _tokenStorage.getAccessToken();
          if (accessToken != null && accessToken.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $accessToken';
          }
          handler.next(options);
        },
        onError: (error, handler) async {
          // Si no hay respuesta, es casi seguro un problema de conectividad
          final status = error.response?.statusCode;

          // Evita loops infinitos en reintento
          final alreadyRetried = (error.requestOptions.extra['retried'] == true);

          if (status == 401 && !alreadyRetried) {
            final refreshed = await _refreshToken();
            if (refreshed) {
              final options = error.requestOptions;
              options.extra['retried'] = true;

              final accessToken = await _tokenStorage.getAccessToken();
              if (accessToken != null && accessToken.isNotEmpty) {
                options.headers['Authorization'] = 'Bearer $accessToken';
              }

              try {
                final response = await _dio.fetch(options);
                return handler.resolve(response);
              } catch (_) {
                // cae al handler.next(error) abajo
              }
            } else {
              await _tokenStorage.clearTokens();
            }
          }

          handler.next(error);
        },
      ),
    );
  }

  Dio get dio => _dio;

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await _tokenStorage.getRefreshToken();
      if (refreshToken == null || refreshToken.isEmpty) return false;

      final response = await _dioNoAuth.post(
        '/auth/refresh',
        data: {'refresh_token': refreshToken},
      );

      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        await _tokenStorage.saveTokens(
          accessToken: data['access_token'] as String,
          refreshToken: data['refresh_token'] as String,
        );
        return true;
      }
      return false;
    } catch (_) {
      return false;
    }
  }
}

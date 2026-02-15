import 'package:cofrade360/core/errors/failures.dart';
import 'package:cofrade360/features/admin/presentation/admin_screen.dart';
import 'package:cofrade360/features/auth/domain/entities/user.dart';
import 'package:cofrade360/features/auth/domain/repositories/auth_repository.dart';
import 'package:cofrade360/features/auth/presentation/providers/auth_provider.dart';
import 'package:dartz/dartz.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('Admin screen blocks non-admin users', (tester) async {
    final state = AuthState(
      user: User(
        id: 'u1',
        email: 'user@test.com',
        isActive: true,
        role: 'user',
        createdAt: DateTime(2026, 1, 1),
      ),
      isAuthenticated: true,
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [authProvider.overrideWith((ref) => _FakeAuthNotifier(state))],
        child: const MaterialApp(home: AdminScreen()),
      ),
    );

    await tester.pumpAndSettle();
    expect(find.text('Solo administradores'), findsOneWidget);
  });
}

class _FakeAuthNotifier extends AuthNotifier {
  _FakeAuthNotifier(AuthState value) : super(_NoopAuthRepository()) {
    state = value;
  }
}

class _NoopAuthRepository implements AuthRepository {
  @override
  Future<Either<Failure, User>> getCurrentUser() async => Left(ServerFailure('noop'));

  @override
  Future<bool> isAuthenticated() async => false;

  @override
  Future<Either<Failure, User>> login({required String email, required String password}) async =>
      Left(ServerFailure('noop'));

  @override
  Future<Either<Failure, User>> register({required String email, required String password}) async =>
      Left(ServerFailure('noop'));

  @override
  Future<Either<Failure, void>> logout() async => const Right(null);
}

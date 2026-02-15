import 'package:cofrade360/core/network/api_client.dart';
import 'package:cofrade360/core/storage/token_storage.dart';
import 'package:cofrade360/features/modo_calle/presentation/modo_calle_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('renders connected state banner', (tester) async {
    await tester.pumpWidget(_buildWithState(
      const ModoCalleState(connectionStatus: StreetConnectionStatus.connected, etaSeconds: 300),
    ));
    expect(find.textContaining('Estado: Conectado'), findsOneWidget);
  });

  testWidgets('renders disconnected state banner', (tester) async {
    await tester.pumpWidget(_buildWithState(
      const ModoCalleState(connectionStatus: StreetConnectionStatus.disconnected),
    ));
    expect(find.textContaining('Estado: Desconectado'), findsOneWidget);
  });

  testWidgets('renders offline degraded message', (tester) async {
    await tester.pumpWidget(_buildWithState(
      const ModoCalleState(connectionStatus: StreetConnectionStatus.offline),
    ));
    expect(find.text('Última ruta disponible (polling ligero activo)'), findsOneWidget);
  });

  testWidgets('renders warning text', (tester) async {
    await tester.pumpWidget(_buildWithState(
      const ModoCalleState(warnings: ['Bulla alta en la ruta actual']),
    ));
    expect(find.textContaining('⚠ Bulla alta'), findsOneWidget);
  });

  testWidgets('reconnect button triggers notifier reconnect', (tester) async {
    final notifier = _TestModoCalleNotifier(const ModoCalleState());
    await tester.pumpWidget(
      ProviderScope(
        overrides: [modoCalleProvider.overrideWith((ref) => notifier)],
        child: const MaterialApp(home: ModoCalleScreen()),
      ),
    );

    await tester.tap(find.text('Reconectar'));
    await tester.pump();
    expect(notifier.reconnectCalled, isTrue);
  });
}

Widget _buildWithState(ModoCalleState state) {
  return ProviderScope(
    overrides: [modoCalleProvider.overrideWith((ref) => _TestModoCalleNotifier(state))],
    child: const MaterialApp(home: ModoCalleScreen()),
  );
}

class _TestModoCalleNotifier extends ModoCalleNotifier {
  bool reconnectCalled = false;

  _TestModoCalleNotifier(ModoCalleState initial)
      : super(ApiClient(TokenStorage(const FlutterSecureStorage()))) {
    state = initial;
  }

  @override
  Future<void> reconnect() async {
    reconnectCalled = true;
    state = state.copyWith(connectionStatus: StreetConnectionStatus.connected);
  }

  @override
  Future<void> startStreetMode() async {}

  @override
  Future<void> activatePlanB() async {}
}

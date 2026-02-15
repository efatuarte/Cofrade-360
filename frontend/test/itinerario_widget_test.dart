import 'package:cofrade360/features/itinerario/domain/entities/plan.dart';
import 'package:cofrade360/features/itinerario/presentation/itinerario_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('Itinerario screen shows plans list', (tester) async {
    final plans = [
      UserPlanEntity(
        id: 'p1',
        userId: 'u1',
        title: 'Viernes Santo',
        planDate: DateTime(2026, 4, 10),
        items: const [],
      ),
    ];

    await tester.pumpWidget(
      ProviderScope(
        overrides: [plansProvider.overrideWith((ref) async => plans)],
        child: const MaterialApp(home: ItinerarioScreen()),
      ),
    );

    await tester.pumpAndSettle();
    expect(find.textContaining('Viernes Santo'), findsOneWidget);
    expect(find.text('Añadir ítem'), findsOneWidget);
  });
}

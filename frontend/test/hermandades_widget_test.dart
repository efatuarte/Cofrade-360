import 'package:cofrade360/features/hermandades/domain/entities/hermandad.dart';
import 'package:cofrade360/features/hermandades/presentation/hermandades_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('Hermandades screen renders list from provider', (tester) async {
    final paginated = PaginatedHermandades(
      items: [
        Hermandad(
          id: 'h1',
          nameShort: 'Macarena',
          nameFull: 'Hermandad de la Macarena',
          createdAt: DateTime(2026, 1, 1),
          ssDay: 'madrugada',
          churchName: 'Basílica de la Macarena',
        ),
      ],
      page: 1,
      pageSize: 20,
      total: 1,
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          hermandadesProvider.overrideWith((ref) async => paginated),
        ],
        child: const MaterialApp(home: HermandadesScreen()),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('Macarena'), findsOneWidget);
    expect(find.text('Basílica de la Macarena'), findsOneWidget);
  });
}

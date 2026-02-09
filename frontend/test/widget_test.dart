import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cofrade360/main.dart';

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const ProviderScope(child: MyApp()));

    // Verify that the app starts
    expect(find.byType(MaterialApp), findsOneWidget);
  });

  testWidgets('Bottom navigation has 5 tabs', (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: MyApp()));
    await tester.pumpAndSettle();

    // Verify all 5 tabs are present
    expect(find.text('Agenda'), findsOneWidget);
    expect(find.text('Hermandades'), findsOneWidget);
    expect(find.text('Itinerario'), findsOneWidget);
    expect(find.text('Modo Calle'), findsOneWidget);
    expect(find.text('Perfil'), findsOneWidget);
  });

  testWidgets('Navigation between tabs works', (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: MyApp()));
    await tester.pumpAndSettle();

    // Initially on Agenda tab
    expect(find.text('Agenda'), findsNWidgets(2)); // In nav bar and app bar

    // Tap Hermandades tab
    await tester.tap(find.text('Hermandades'));
    await tester.pumpAndSettle();
    expect(find.text('Hermandades'), findsNWidgets(2));

    // Tap Perfil tab
    await tester.tap(find.text('Perfil'));
    await tester.pumpAndSettle();
    expect(find.text('Perfil'), findsNWidgets(2));
  });
}

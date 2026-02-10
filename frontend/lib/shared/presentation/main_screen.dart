import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/legacy.dart';

import '../../features/agenda/presentation/agenda_screen.dart';
import '../../features/hermandades/presentation/hermandades_screen.dart';
import '../../features/itinerario/presentation/itinerario_screen.dart';
import '../../features/modo_calle/presentation/modo_calle_screen.dart';
import '../../features/perfil/presentation/perfil_screen.dart';

final selectedIndexProvider = StateProvider<int>((ref) => 0);

class MainScreen extends ConsumerWidget {
  const MainScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedIndex = ref.watch(selectedIndexProvider);

    final screens = [
      const AgendaScreen(),
      const HermandadesScreen(),
      const ItinerarioScreen(),
      const ModoCalleScreen(),
      const PerfilScreen(),
    ];

    return Scaffold(
      body: IndexedStack(
        index: selectedIndex,
        children: screens,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: selectedIndex,
        onTap: (index) {
          ref.read(selectedIndexProvider.notifier).state = index;
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.calendar_today),
            label: 'Agenda',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.church),
            label: 'Hermandades',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.route),
            label: 'Itinerario',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.streetview),
            label: 'Modo Exploración',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Perfil',
          ),
        ],
      ),
    );
  }
}

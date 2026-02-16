import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/legacy.dart';

import '../../auth/presentation/providers/auth_provider.dart';
import '../data/repositories/hermandades_repository_impl.dart';
import '../domain/entities/hermandad.dart';
import 'hermandad_detail_screen.dart';

final hermandadesRepositoryProvider = Provider<HermandadesRepositoryImpl>((ref) {
  return HermandadesRepositoryImpl(apiClient: ref.watch(apiClientProvider));
});

class HermandadesFilter {
  final String? q;
  final String? day;

  const HermandadesFilter({this.q, this.day});
}

final hermandadesFilterProvider = StateProvider<HermandadesFilter>((ref) => const HermandadesFilter());

final hermandadesProvider = FutureProvider<PaginatedHermandades>((ref) async {
  final repo = ref.watch(hermandadesRepositoryProvider);
  final filter = ref.watch(hermandadesFilterProvider);
  final result = await repo.getHermandades(q: filter.q, day: filter.day);
  return result.fold((failure) => throw Exception(failure.message), (data) => data);
});

class HermandadesScreen extends ConsumerWidget {
  const HermandadesScreen({super.key});

  static const Map<String, String> _days = {
    'domingo_ramos': 'Domingo de Ramos',
    'lunes_santo': 'Lunes Santo',
    'martes_santo': 'Martes Santo',
    'miercoles_santo': 'Miércoles Santo',
    'jueves_santo': 'Jueves Santo',
    'madrugada': 'Madrugada',
    'viernes_santo': 'Viernes Santo',
  };

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dataAsync = ref.watch(hermandadesProvider);
    final filter = ref.watch(hermandadesFilterProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Hermandades'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () => _showSearch(context, ref),
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: DropdownButtonFormField<String>(
              value: filter.day,
              decoration: const InputDecoration(
                labelText: 'Filtrar por día',
                border: OutlineInputBorder(),
              ),
              items: [
                const DropdownMenuItem<String>(value: null, child: Text('Todos')),
                ..._days.entries
                    .map((entry) => DropdownMenuItem(value: entry.key, child: Text(entry.value))),
              ],
              onChanged: (value) {
                ref.read(hermandadesFilterProvider.notifier).state =
                    HermandadesFilter(q: filter.q, day: value);
              },
            ),
          ),
          Expanded(
            child: dataAsync.when(
              data: (paginated) {
                if (paginated.items.isEmpty) {
                  return const Center(child: Text('No hay hermandades para este filtro'));
                }
                return RefreshIndicator(
                  onRefresh: () async => ref.invalidate(hermandadesProvider),
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: paginated.items.length,
                    itemBuilder: (context, index) {
                      final item = paginated.items[index];
                      return Card(
                        margin: const EdgeInsets.only(bottom: 12),
                        child: ListTile(
                          leading: CircleAvatar(
                            child: Text(item.nameShort.characters.first.toUpperCase()),
                          ),
                          title: Text(item.nameShort),
                          subtitle: Text(item.churchName ?? item.nameFull),
                          trailing: item.ssDay != null
                              ? Chip(label: Text(_days[item.ssDay] ?? item.ssDay!))
                              : null,
                          onTap: () => Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) => HermandadDetailScreen(brotherhoodId: item.id),
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Text(
                    error.toString().replaceFirst('Exception: ', ''),
                    textAlign: TextAlign.center,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showSearch(BuildContext context, WidgetRef ref) {
    final filter = ref.read(hermandadesFilterProvider);
    final controller = TextEditingController(text: filter.q);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Buscar hermandad'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(hintText: 'Nombre corto o completo'),
        ),
        actions: [
          TextButton(
            onPressed: () {
              ref.read(hermandadesFilterProvider.notifier).state =
                  HermandadesFilter(day: filter.day);
              Navigator.pop(ctx);
            },
            child: const Text('Limpiar'),
          ),
          ElevatedButton(
            onPressed: () {
              ref.read(hermandadesFilterProvider.notifier).state = HermandadesFilter(
                    q: controller.text.isEmpty ? null : controller.text,
                    day: filter.day,
                  );
              Navigator.pop(ctx);
            },
            child: const Text('Buscar'),
          ),
        ],
      ),
    );
  }
}

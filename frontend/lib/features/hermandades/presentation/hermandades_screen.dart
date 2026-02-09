import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/repositories/hermandades_repository_impl.dart';
import '../domain/entities/hermandad.dart';

// Providers
final hermandadesRepositoryProvider = Provider((ref) => HermandadesRepositoryImpl());

final hermandadesProvider = FutureProvider<List<Hermandad>>((ref) async {
  final repo = ref.watch(hermandadesRepositoryProvider);
  final result = await repo.getHermandades();
  return result.fold(
    (failure) => throw Exception(failure.message),
    (hermandades) => hermandades,
  );
});

class HermandadesScreen extends ConsumerWidget {
  const HermandadesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final hermandadesAsync = ref.watch(hermandadesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Hermandades'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              // TODO: Implement search
            },
          ),
        ],
      ),
      body: hermandadesAsync.when(
        data: (hermandades) {
          return ListView.builder(
            itemCount: hermandades.length,
            padding: const EdgeInsets.all(16),
            itemBuilder: (context, index) {
              final hermandad = hermandades[index];
              return _HermandadCard(hermandad: hermandad);
            },
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Text('Error: $error'),
        ),
      ),
    );
  }
}

class _HermandadCard extends StatelessWidget {
  final Hermandad hermandad;

  const _HermandadCard({required this.hermandad});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: InkWell(
        onTap: () {
          // TODO: Navigate to detail
        },
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.primaryContainer,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Center(
                  child: Text(
                    hermandad.escudo,
                    style: const TextStyle(fontSize: 32),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      hermandad.nombre,
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      hermandad.sede,
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Fundada en ${hermandad.fechaFundacion.year}',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Theme.of(context).colorScheme.secondary,
                          ),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right),
            ],
          ),
        ),
      ),
    );
  }
}

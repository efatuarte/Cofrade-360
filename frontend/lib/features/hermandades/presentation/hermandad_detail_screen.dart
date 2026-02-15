import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../domain/entities/hermandad.dart';
import 'hermandades_screen.dart';

final brotherhoodDetailProvider = FutureProvider.family<Hermandad, String>((ref, id) async {
  final repo = ref.watch(hermandadesRepositoryProvider);
  final result = await repo.getHermandadById(id);
  return result.fold((failure) => throw Exception(failure.message), (data) => data);
});

final brotherhoodMediaProvider = FutureProvider.family<List<BrotherhoodMedia>, String>((ref, id) async {
  final repo = ref.watch(hermandadesRepositoryProvider);
  final result = await repo.getMediaByBrotherhood(id);
  return result.fold((failure) => throw Exception(failure.message), (data) => data);
});

class HermandadDetailScreen extends ConsumerWidget {
  final String brotherhoodId;

  const HermandadDetailScreen({super.key, required this.brotherhoodId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detailAsync = ref.watch(brotherhoodDetailProvider(brotherhoodId));
    final mediaAsync = ref.watch(brotherhoodMediaProvider(brotherhoodId));

    return Scaffold(
      appBar: AppBar(title: const Text('Detalle de Hermandad')),
      body: detailAsync.when(
        data: (brotherhood) => ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text(brotherhood.nameShort, style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 4),
            Text(brotherhood.nameFull),
            const SizedBox(height: 12),
            if (brotherhood.churchName != null)
              ListTile(
                contentPadding: EdgeInsets.zero,
                leading: const Icon(Icons.church),
                title: const Text('Sede canónica'),
                subtitle: Text(brotherhood.churchName!),
              ),
            if (brotherhood.ssDay != null)
              ListTile(
                contentPadding: EdgeInsets.zero,
                leading: const Icon(Icons.calendar_today),
                title: const Text('Día de salida'),
                subtitle: Text(brotherhood.ssDay!),
              ),
            const Divider(),
            const Text('Historia', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text(brotherhood.history ?? 'Sin historia disponible'),
            const SizedBox(height: 16),
            const Text('Media', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            mediaAsync.when(
              data: (media) {
                if (media.isEmpty) {
                  return const Text('No hay media disponible');
                }
                return SizedBox(
                  height: 130,
                  child: ListView.separated(
                    scrollDirection: Axis.horizontal,
                    itemCount: media.length,
                    separatorBuilder: (_, __) => const SizedBox(width: 8),
                    itemBuilder: (context, index) {
                      final item = media[index];
                      return ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.network(
                          item.url,
                          width: 180,
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => Container(
                            width: 180,
                            color: Colors.grey.shade300,
                            alignment: Alignment.center,
                            child: const Text('Media no disponible'),
                          ),
                        ),
                      );
                    },
                  ),
                );
              },
              loading: () => const Padding(
                padding: EdgeInsets.all(24),
                child: Center(child: CircularProgressIndicator()),
              ),
              error: (error, _) => Text(error.toString()),
            ),
          ],
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text(error.toString())),
      ),
    );
  }
}

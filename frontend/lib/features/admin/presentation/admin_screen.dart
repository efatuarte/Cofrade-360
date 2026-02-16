import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../auth/presentation/providers/auth_provider.dart';

final adminBrotherhoodsProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final response = await ref.watch(apiClientProvider).dio.get('/admin/brotherhoods');
  final items = (response.data['items'] as List<dynamic>).cast<Map<String, dynamic>>();
  return items;
});

class AdminScreen extends ConsumerStatefulWidget {
  const AdminScreen({super.key});

  @override
  ConsumerState<AdminScreen> createState() => _AdminScreenState();
}

class _AdminScreenState extends ConsumerState<AdminScreen> {
  final _processionIdController = TextEditingController();
  final _itineraryController = TextEditingController();
  final _confidenceController = TextEditingController(text: '0.7');
  final _scheduleController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    if (auth.user?.role != 'admin') {
      return const Scaffold(
        body: Center(child: Text('Solo administradores')),
      );
    }

    final brotherhoodsAsync = ref.watch(adminBrotherhoodsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Admin')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Editar hermandades', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          brotherhoodsAsync.when(
            data: (items) => Column(
              children: items.map((item) {
                final sedeController = TextEditingController(text: (item['sede'] as String?) ?? '');
                final dayController = TextEditingController(text: (item['ss_day'] as String?) ?? '');
                return Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(item['name_short']?.toString() ?? item['nombre'].toString()),
                        TextField(
                          controller: sedeController,
                          decoration: const InputDecoration(labelText: 'Sede'),
                        ),
                        TextField(
                          controller: dayController,
                          decoration: const InputDecoration(labelText: 'Día (enum)'),
                        ),
                        const SizedBox(height: 8),
                        ElevatedButton(
                          onPressed: () async {
                            await ref.watch(apiClientProvider).dio.patch(
                              '/admin/brotherhoods/${item['id']}',
                              data: {
                                'sede': sedeController.text,
                                'ss_day': dayController.text,
                              },
                            );
                            if (mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Hermandad actualizada')),
                              );
                            }
                            ref.invalidate(adminBrotherhoodsProvider);
                          },
                          child: const Text('Guardar'),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (e, _) => Text(e.toString()),
          ),
          const SizedBox(height: 24),
          const Text('Editor de procesión', style: TextStyle(fontWeight: FontWeight.bold)),
          TextField(
            controller: _processionIdController,
            decoration: const InputDecoration(labelText: 'Procession ID'),
          ),
          TextField(
            controller: _itineraryController,
            minLines: 3,
            maxLines: 5,
            decoration: const InputDecoration(labelText: 'Itinerario (texto)'),
          ),
          TextField(
            controller: _confidenceController,
            decoration: const InputDecoration(labelText: 'Confidence [0..1]'),
          ),
          TextField(
            controller: _scheduleController,
            minLines: 2,
            maxLines: 4,
            decoration: const InputDecoration(
              labelText: 'Schedule points JSON',
              hintText: '[{"point_type":"salida","scheduled_datetime":"2026-04-03T01:00:00"}]',
            ),
          ),
          ElevatedButton(
            onPressed: () async {
              await ref.watch(apiClientProvider).dio.patch(
                '/admin/processions/${_processionIdController.text}',
                data: {
                  'itinerary_text': _itineraryController.text,
                  'confidence': double.tryParse(_confidenceController.text) ?? 0.7,
                  'schedule_points': _scheduleController.text.isEmpty
                      ? []
                      : (jsonDecode(_scheduleController.text) as List<dynamic>),
                },
              );
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Procesión actualizada')),
                );
              }
            },
            child: const Text('Guardar procesión'),
          ),
        ],
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/legacy.dart';
import 'package:intl/intl.dart';

import '../../auth/presentation/providers/auth_provider.dart';
import '../data/repositories/itinerario_repository_impl.dart';
import '../domain/entities/plan.dart';

final itinerarioRepositoryProvider = Provider<ItinerarioRepositoryImpl>((ref) {
  return ItinerarioRepositoryImpl(apiClient: ref.watch(apiClientProvider));
});

final selectedPlanIdProvider = StateProvider<String?>((ref) => null);

final plansProvider = FutureProvider<List<UserPlanEntity>>((ref) async {
  final repo = ref.watch(itinerarioRepositoryProvider);
  final result = await repo.getPlans();
  return result.fold((failure) => throw Exception(failure.message), (plans) => plans);
});

final selectedPlanProvider = Provider<UserPlanEntity?>((ref) {
  final plans = ref.watch(plansProvider).value;
  final selectedId = ref.watch(selectedPlanIdProvider);
  if (plans == null || plans.isEmpty) return null;
  if (selectedId == null) return plans.first;
  return plans.firstWhere(
    (plan) => plan.id == selectedId,
    orElse: () => plans.first,
  );
});

class ItinerarioScreen extends ConsumerWidget {
  const ItinerarioScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final plansAsync = ref.watch(plansProvider);
    final selectedPlan = ref.watch(selectedPlanProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Itinerario')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _createPlanDialog(context, ref),
        icon: const Icon(Icons.add),
        label: const Text('Nuevo plan'),
      ),
      body: plansAsync.when(
        data: (plans) {
          if (plans.isEmpty) {
            return const Center(child: Text('Aún no tienes planes. Crea tu primer itinerario.'));
          }

          final currentPlan = selectedPlan ?? plans.first;
          return Column(
            children: [
              Padding(
                padding: const EdgeInsets.all(16),
                child: DropdownButtonFormField<String>(
                  value: currentPlan.id,
                  decoration: const InputDecoration(
                    border: OutlineInputBorder(),
                    labelText: 'Seleccionar día',
                  ),
                  items: plans
                      .map(
                        (plan) => DropdownMenuItem(
                          value: plan.id,
                          child: Text(
                            '${DateFormat('EEE d MMM', 'es_ES').format(plan.planDate)} · ${plan.title}',
                          ),
                        ),
                      )
                      .toList(),
                  onChanged: (value) {
                    ref.read(selectedPlanIdProvider.notifier).state = value;
                  },
                ),
              ),
              if (currentPlan.items.isEmpty)
                const Expanded(child: Center(child: Text('Este plan no tiene ítems todavía.')))
              else
                Expanded(
                  child: ListView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    itemCount: currentPlan.items.length,
                    itemBuilder: (context, index) {
                      final item = currentPlan.items[index];
                      return Card(
                        child: ListTile(
                          leading: CircleAvatar(child: Text('${item.position + 1}')),
                          title: Text(item.itemType == 'event' ? 'Evento' : 'Hermandad'),
                          subtitle: Text(
                            '${DateFormat('HH:mm').format(item.desiredTimeStart)} - ${DateFormat('HH:mm').format(item.desiredTimeEnd)}',
                          ),
                        ),
                      );
                    },
                  ),
                ),
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
                child: Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _addItemDialog(context, ref, currentPlan.id),
                        icon: const Icon(Icons.add_location_alt),
                        label: const Text('Añadir ítem'),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () => _optimize(context, ref, currentPlan.id),
                        icon: const Icon(Icons.auto_fix_high),
                        label: const Text('Optimizar'),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text(error.toString().replaceFirst('Exception: ', ''))),
      ),
    );
  }

  Future<void> _createPlanDialog(BuildContext context, WidgetRef ref) async {
    final titleCtrl = TextEditingController();
    DateTime selectedDate = DateTime.now();

    await showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Crear plan'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: titleCtrl,
              decoration: const InputDecoration(labelText: 'Título'),
            ),
            const SizedBox(height: 12),
            StatefulBuilder(
              builder: (context, setState) => Row(
                children: [
                  Expanded(
                    child: Text('Fecha: ${DateFormat('d MMM yyyy', 'es_ES').format(selectedDate)}'),
                  ),
                  TextButton(
                    onPressed: () async {
                      final picked = await showDatePicker(
                        context: context,
                        initialDate: selectedDate,
                        firstDate: DateTime(2025),
                        lastDate: DateTime(2027),
                      );
                      if (picked != null) setState(() => selectedDate = picked);
                    },
                    child: const Text('Cambiar'),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
          ElevatedButton(
            onPressed: () async {
              final repo = ref.read(itinerarioRepositoryProvider);
              final result = await repo.createPlan(
                title: titleCtrl.text.trim().isEmpty ? 'Plan Semana Santa' : titleCtrl.text.trim(),
                planDate: selectedDate,
              );
              result.fold(
                (failure) => ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(failure.message))),
                (_) => ref.invalidate(plansProvider),
              );
              if (context.mounted) Navigator.pop(ctx);
            },
            child: const Text('Guardar'),
          ),
        ],
      ),
    );
  }

  Future<void> _addItemDialog(BuildContext context, WidgetRef ref, String planId) async {
    DateTime start = DateTime.now();
    DateTime end = DateTime.now().add(const Duration(hours: 1));

    await showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Añadir ítem rápido'),
        content: const Text('Se añadirá un ítem demo para MVP. En siguientes fases se seleccionará evento/hermandad real.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
          ElevatedButton(
            onPressed: () async {
              final repo = ref.read(itinerarioRepositoryProvider);
              final result = await repo.addItem(
                planId: planId,
                itemType: 'event',
                eventId: 'demo-event',
                desiredTimeStart: start,
                desiredTimeEnd: end,
                lat: 37.389,
                lng: -5.995,
              );
              result.fold(
                (failure) => ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(failure.message))),
                (ok) {
                  if (ok.warnings.isNotEmpty) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Aviso: ${ok.warnings.first.detail}')),
                    );
                  }
                  ref.invalidate(plansProvider);
                },
              );
              if (context.mounted) Navigator.pop(ctx);
            },
            child: const Text('Añadir'),
          ),
        ],
      ),
    );
  }

  Future<void> _optimize(BuildContext context, WidgetRef ref, String planId) async {
    final repo = ref.read(itinerarioRepositoryProvider);
    final result = await repo.optimizePlan(planId);
    result.fold(
      (failure) => ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(failure.message))),
      (items) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Plan optimizado: ${items.length} ítems reordenados')),
        );
        ref.invalidate(plansProvider);
      },
    );
  }
}

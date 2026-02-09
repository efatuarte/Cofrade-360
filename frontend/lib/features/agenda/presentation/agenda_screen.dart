import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../data/repositories/agenda_repository_impl.dart';
import '../domain/entities/evento.dart';
import '../domain/usecases/get_eventos.dart';

// Providers
final agendaRepositoryProvider = Provider((ref) => AgendaRepositoryImpl());

final getEventosUseCaseProvider = Provider((ref) {
  return GetEventos(ref.watch(agendaRepositoryProvider));
});

final eventosProvider = FutureProvider<List<Evento>>((ref) async {
  final getEventos = ref.watch(getEventosUseCaseProvider);
  final result = await getEventos();
  return result.fold(
    (failure) => throw Exception(failure.message),
    (eventos) => eventos,
  );
});

class AgendaScreen extends ConsumerWidget {
  const AgendaScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final eventosAsync = ref.watch(eventosProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Agenda'),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: () {
              // TODO: Implement filtering
            },
          ),
        ],
      ),
      body: eventosAsync.when(
        data: (eventos) {
          if (eventos.isEmpty) {
            return const Center(
              child: Text('No hay eventos programados'),
            );
          }
          return ListView.builder(
            itemCount: eventos.length,
            padding: const EdgeInsets.all(16),
            itemBuilder: (context, index) {
              final evento = eventos[index];
              return _EventoCard(evento: evento);
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

class _EventoCard extends StatelessWidget {
  final Evento evento;

  const _EventoCard({required this.evento});

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('EEEE, d MMMM - HH:mm', 'es');
    
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              evento.titulo,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                const Icon(Icons.access_time, size: 16),
                const SizedBox(width: 4),
                Text(
                  dateFormat.format(evento.fechaHora),
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ],
            ),
            if (evento.ubicacion != null) ...[
              const SizedBox(height: 4),
              Row(
                children: [
                  const Icon(Icons.location_on, size: 16),
                  const SizedBox(width: 4),
                  Text(
                    evento.ubicacion!,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
            ],
            const SizedBox(height: 8),
            Text(
              evento.descripcion,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../domain/entities/evento.dart';
import 'agenda_screen.dart'; // tipoColor, tipoLabels, tipoIcons, agendaRepositoryProvider

// Provider that fetches a single event by ID
final eventoDetailProvider =
    FutureProvider.family<Evento, String>((ref, id) async {
  final repo = ref.watch(agendaRepositoryProvider);
  final result = await repo.getEventoById(id);
  return result.fold(
    (failure) => throw Exception(failure.message),
    (evento) => evento,
  );
});

class EventDetailScreen extends ConsumerWidget {
  final String eventoId;

  const EventDetailScreen({super.key, required this.eventoId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final eventoAsync = ref.watch(eventoDetailProvider(eventoId));

    return Scaffold(
      body: eventoAsync.when(
        data: (evento) => _EventDetailBody(evento: evento),
        loading: () => Scaffold(
          appBar: AppBar(),
          body: const Center(child: CircularProgressIndicator()),
        ),
        error: (error, _) => Scaffold(
          appBar: AppBar(),
          body: Center(
            child: Padding(
              padding: const EdgeInsets.all(32),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.error_outline, size: 48, color: Colors.red[300]),
                  const SizedBox(height: 16),
                  Text(
                    error.toString().replaceFirst('Exception: ', ''),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton.icon(
                    onPressed: () =>
                        ref.invalidate(eventoDetailProvider(eventoId)),
                    icon: const Icon(Icons.refresh),
                    label: const Text('Reintentar'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _EventDetailBody extends StatelessWidget {
  final Evento evento;

  const _EventDetailBody({required this.evento});

  @override
  Widget build(BuildContext context) {
    final color = tipoColor(evento.tipo);
    final dateFmt = DateFormat('EEEE d MMMM yyyy, HH:mm', 'es_ES');

    return CustomScrollView(
      slivers: [
        // Hero header
        SliverAppBar(
          expandedHeight: 180,
          pinned: true,
          flexibleSpace: FlexibleSpaceBar(
            background: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [color, color.withAlpha(180)],
                ),
              ),
              child: Center(
                child: Icon(
                  tipoIcons[evento.tipo] ?? Icons.event,
                  size: 64,
                  color: Colors.white.withAlpha(180),
                ),
              ),
            ),
            title: Text(
              evento.titulo,
              style: const TextStyle(fontSize: 16),
            ),
          ),
        ),

        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Badges row
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _Badge(
                      icon: tipoIcons[evento.tipo] ?? Icons.event,
                      label: tipoLabels[evento.tipo] ?? evento.tipo,
                      color: color,
                    ),
                    _Badge(
                      icon: Icons.circle,
                      label: _estadoLabel(evento.estado),
                      color: _estadoColor(evento.estado),
                    ),
                    if (!evento.esGratuito)
                      _Badge(
                        icon: Icons.euro,
                        label:
                            '${evento.precio.toStringAsFixed(evento.precio.truncateToDouble() == evento.precio ? 0 : 2)} ${evento.moneda}',
                        color: Colors.green[700]!,
                      ),
                    if (evento.esGratuito)
                      _Badge(
                        icon: Icons.check_circle,
                        label: 'Gratuito',
                        color: Colors.teal,
                      ),
                  ],
                ),

                const SizedBox(height: 24),

                // Date section
                _SectionRow(
                  icon: Icons.calendar_today,
                  title: 'Fecha y hora',
                  content: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(dateFmt.format(evento.fechaInicio)),
                      if (evento.fechaFin != null)
                        Text(
                          'Hasta: ${dateFmt.format(evento.fechaFin!)}',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      if (evento.fechaFin != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          'Duracion: ${_duration(evento.fechaInicio, evento.fechaFin!)}',
                          style: TextStyle(
                              color: Colors.grey[600], fontSize: 13),
                        ),
                      ],
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // Location section
                if (evento.location != null)
                  _SectionRow(
                    icon: Icons.location_on,
                    title: 'Ubicacion',
                    content: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          evento.location!.name,
                          style: const TextStyle(fontWeight: FontWeight.w600),
                        ),
                        if (evento.location!.address != null)
                          Text(
                            evento.location!.address!,
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        const SizedBox(height: 12),
                        // Map placeholder
                        Container(
                          height: 150,
                          width: double.infinity,
                          decoration: BoxDecoration(
                            color: Colors.grey[200],
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: Colors.grey[300]!),
                          ),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.map,
                                  size: 40, color: Colors.grey[400]),
                              const SizedBox(height: 8),
                              Text(
                                evento.location!.lat != null
                                    ? '${evento.location!.lat!.toStringAsFixed(4)}, ${evento.location!.lng!.toStringAsFixed(4)}'
                                    : 'Mapa proximamente',
                                style: TextStyle(
                                    color: Colors.grey[500], fontSize: 12),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),

                const SizedBox(height: 16),

                // Description
                if (evento.descripcion != null &&
                    evento.descripcion!.trim().isNotEmpty) ...[
                  _SectionRow(
                    icon: Icons.description,
                    title: 'Descripcion',
                    content: Text(
                      evento.descripcion!,
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ),
                  const SizedBox(height: 16),
                ],

                const SizedBox(height: 24),

                // "Ir ahora" button
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: ElevatedButton.icon(
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text(
                              'Modo Calle disponible en la siguiente fase'),
                        ),
                      );
                    },
                    icon: const Icon(Icons.navigation),
                    label: const Text('Ir ahora'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: color,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),

                const SizedBox(height: 40),
              ],
            ),
          ),
        ),
      ],
    );
  }

  static String _estadoLabel(String estado) {
    switch (estado) {
      case 'programado':
        return 'Programado';
      case 'en_curso':
        return 'En curso';
      case 'finalizado':
        return 'Finalizado';
      case 'cancelado':
        return 'Cancelado';
      default:
        return estado;
    }
  }

  static Color _estadoColor(String estado) {
    switch (estado) {
      case 'programado':
        return Colors.blue;
      case 'en_curso':
        return Colors.green;
      case 'finalizado':
        return Colors.grey;
      case 'cancelado':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  static String _duration(DateTime start, DateTime end) {
    final diff = end.difference(start);
    if (diff.inHours >= 24) {
      final days = diff.inDays;
      final hours = diff.inHours % 24;
      return hours > 0 ? '${days}d ${hours}h' : '${days}d';
    }
    final hours = diff.inHours;
    final mins = diff.inMinutes % 60;
    return mins > 0 ? '${hours}h ${mins}min' : '${hours}h';
  }
}

// --------------- Reusable widgets ---------------

class _Badge extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;

  const _Badge({
    required this.icon,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withAlpha(20),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withAlpha(60)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: color),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
                fontSize: 12, color: color, fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }
}

class _SectionRow extends StatelessWidget {
  final IconData icon;
  final String title;
  final Widget content;

  const _SectionRow({
    required this.icon,
    required this.title,
    required this.content,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 20, color: Theme.of(context).colorScheme.primary),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: Theme.of(context)
                    .textTheme
                    .titleSmall
                    ?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              content,
            ],
          ),
        ),
      ],
    );
  }
}

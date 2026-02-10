import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/legacy.dart';
import 'package:intl/intl.dart';

import '../../auth/presentation/providers/auth_provider.dart';
import '../data/repositories/agenda_repository_impl.dart';
import '../domain/entities/evento.dart';
import '../domain/repositories/agenda_repository.dart';
import 'event_detail_screen.dart';

// --------------- Filter State ---------------

class EventoFilter {
  final String? tipo;
  final String? q;
  final DateTime? fromDate;
  final DateTime? toDate;

  const EventoFilter({this.tipo, this.q, this.fromDate, this.toDate});

  EventoFilter copyWith({
    String? tipo,
    String? q,
    DateTime? fromDate,
    DateTime? toDate,
    bool clearTipo = false,
    bool clearQ = false,
    bool clearDates = false,
  }) {
    return EventoFilter(
      tipo: clearTipo ? null : (tipo ?? this.tipo),
      q: clearQ ? null : (q ?? this.q),
      fromDate: clearDates ? null : (fromDate ?? this.fromDate),
      toDate: clearDates ? null : (toDate ?? this.toDate),
    );
  }

  bool get hasFilters => tipo != null || fromDate != null || toDate != null;
}

// --------------- Providers ---------------

final eventoFilterProvider =
    StateProvider<EventoFilter>((ref) => const EventoFilter());

final agendaRepositoryProvider = Provider<AgendaRepository>((ref) {
  return AgendaRepositoryImpl(apiClient: ref.watch(apiClientProvider));
});

final eventosProvider = FutureProvider<PaginatedEventos>((ref) async {
  final filter = ref.watch(eventoFilterProvider);
  final repo = ref.watch(agendaRepositoryProvider);
  final result = await repo.getEventos(
    tipo: filter.tipo,
    q: filter.q,
    fromDate: filter.fromDate,
    toDate: filter.toDate,
    pageSize: 50,
  );
  return result.fold(
    (failure) => throw Exception(failure.message),
    (data) => data,
  );
});

// --------------- Tipo helpers ---------------

const tipoLabels = <String, String>{
  'procesion': 'Procesion',
  'culto': 'Culto',
  'concierto': 'Concierto',
  'exposicion': 'Exposicion',
  'ensayo': 'Ensayo',
  'otro': 'Otro',
};

const tipoIcons = <String, IconData>{
  'procesion': Icons.church,
  'culto': Icons.auto_awesome,
  'concierto': Icons.music_note,
  'exposicion': Icons.museum,
  'ensayo': Icons.groups,
  'otro': Icons.event,
};

Color tipoColor(String tipo) {
  switch (tipo) {
    case 'procesion':
      return const Color(0xFF8B1538);
    case 'culto':
      return const Color(0xFFD4AF37);
    case 'concierto':
      return const Color(0xFF1565C0);
    case 'exposicion':
      return const Color(0xFF2E7D32);
    case 'ensayo':
      return const Color(0xFF6A1B9A);
    default:
      return Colors.grey;
  }
}

// --------------- Screen ---------------

class AgendaScreen extends ConsumerWidget {
  const AgendaScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final eventosAsync = ref.watch(eventosProvider);
    final filter = ref.watch(eventoFilterProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Agenda'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () => _showSearchDialog(context, ref),
          ),
          Stack(
            children: [
              IconButton(
                icon: const Icon(Icons.filter_list),
                onPressed: () => _showFilterSheet(context, ref),
              ),
              if (filter.hasFilters)
                Positioned(
                  right: 8,
                  top: 8,
                  child: Container(
                    width: 8,
                    height: 8,
                    decoration: const BoxDecoration(
                      color: Colors.red,
                      shape: BoxShape.circle,
                    ),
                  ),
                ),
            ],
          ),
        ],
      ),
      body: Column(
        children: [
          // Active filter chips
          if (filter.hasFilters)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Wrap(
                spacing: 8,
                children: [
                  if (filter.tipo != null)
                    Chip(
                      label: Text(tipoLabels[filter.tipo] ?? filter.tipo!),
                      onDeleted: () => ref
                          .read(eventoFilterProvider.notifier)
                          .state = filter.copyWith(clearTipo: true),
                      deleteIcon: const Icon(Icons.close, size: 16),
                    ),
                  if (filter.fromDate != null || filter.toDate != null)
                    Chip(
                      label: Text(
                          _dateRangeLabel(filter.fromDate, filter.toDate)),
                      onDeleted: () => ref
                          .read(eventoFilterProvider.notifier)
                          .state = filter.copyWith(clearDates: true),
                      deleteIcon: const Icon(Icons.close, size: 16),
                    ),
                ],
              ),
            ),
          // Event list
          Expanded(
            child: eventosAsync.when(
              data: (paginated) {
                if (paginated.items.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.event_busy,
                            size: 64, color: Colors.grey[400]),
                        const SizedBox(height: 16),
                        Text(
                          filter.hasFilters
                              ? 'No hay eventos con estos filtros'
                              : 'No hay eventos programados',
                          style: Theme.of(context).textTheme.bodyLarge,
                        ),
                        if (filter.hasFilters) ...[
                          const SizedBox(height: 8),
                          TextButton(
                            onPressed: () => ref
                                .read(eventoFilterProvider.notifier)
                                .state = const EventoFilter(),
                            child: const Text('Limpiar filtros'),
                          ),
                        ],
                      ],
                    ),
                  );
                }
                return RefreshIndicator(
                  onRefresh: () async => ref.invalidate(eventosProvider),
                  child: ListView.builder(
                    itemCount: paginated.items.length,
                    padding: const EdgeInsets.all(16),
                    itemBuilder: (context, index) => _EventoCard(
                      evento: paginated.items[index],
                      onTap: () => Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => EventDetailScreen(
                            eventoId: paginated.items[index].id,
                          ),
                        ),
                      ),
                    ),
                  ),
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => Center(
                child: Padding(
                  padding: const EdgeInsets.all(32),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.error_outline,
                          size: 48, color: Colors.red[300]),
                      const SizedBox(height: 16),
                      Text(
                        error.toString().replaceFirst('Exception: ', ''),
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: () => ref.invalidate(eventosProvider),
                        icon: const Icon(Icons.refresh),
                        label: const Text('Reintentar'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showSearchDialog(BuildContext context, WidgetRef ref) {
    final controller =
        TextEditingController(text: ref.read(eventoFilterProvider).q);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Buscar eventos'),
        content: TextField(
          controller: controller,
          autofocus: true,
          decoration: const InputDecoration(
            hintText: 'Ej: procesion, concierto...',
            prefixIcon: Icon(Icons.search),
          ),
          onSubmitted: (value) {
            ref.read(eventoFilterProvider.notifier).state = ref
                .read(eventoFilterProvider)
                .copyWith(
                    q: value.isEmpty ? null : value,
                    clearQ: value.isEmpty);
            Navigator.pop(ctx);
          },
        ),
        actions: [
          TextButton(
            onPressed: () {
              ref.read(eventoFilterProvider.notifier).state =
                  ref.read(eventoFilterProvider).copyWith(clearQ: true);
              Navigator.pop(ctx);
            },
            child: const Text('Limpiar'),
          ),
          TextButton(
            onPressed: () {
              final value = controller.text;
              ref.read(eventoFilterProvider.notifier).state = ref
                  .read(eventoFilterProvider)
                  .copyWith(
                      q: value.isEmpty ? null : value,
                      clearQ: value.isEmpty);
              Navigator.pop(ctx);
            },
            child: const Text('Buscar'),
          ),
        ],
      ),
    );
  }

  void _showFilterSheet(BuildContext context, WidgetRef ref) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) => _FilterSheet(ref: ref),
    );
  }

  static String _dateRangeLabel(DateTime? from, DateTime? to) {
    final fmt = DateFormat('d MMM', 'es_ES');
    if (from != null && to != null) {
      return '${fmt.format(from)} - ${fmt.format(to)}';
    }
    if (from != null) return 'Desde ${fmt.format(from)}';
    return 'Hasta ${fmt.format(to!)}';
  }
}

// --------------- Filter Sheet ---------------

class _FilterSheet extends StatefulWidget {
  final WidgetRef ref;

  const _FilterSheet({required this.ref});

  @override
  State<_FilterSheet> createState() => _FilterSheetState();
}

class _FilterSheetState extends State<_FilterSheet> {
  String? _selectedTipo;
  DateTime? _fromDate;
  DateTime? _toDate;

  @override
  void initState() {
    super.initState();
    final current = widget.ref.read(eventoFilterProvider);
    _selectedTipo = current.tipo;
    _fromDate = current.fromDate;
    _toDate = current.toDate;
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Filtrar eventos',
                  style: Theme.of(context).textTheme.titleLarge),
              TextButton(
                onPressed: () {
                  widget.ref.read(eventoFilterProvider.notifier).state =
                      const EventoFilter();
                  Navigator.pop(context);
                },
                child: const Text('Limpiar todo'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text('Tipo de evento',
              style: Theme.of(context).textTheme.titleSmall),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: tipoLabels.entries.map((e) {
              final isSelected = _selectedTipo == e.key;
              return FilterChip(
                label: Text(e.value),
                selected: isSelected,
                selectedColor: tipoColor(e.key).withAlpha(50),
                avatar: Icon(tipoIcons[e.key], size: 18),
                onSelected: (selected) {
                  setState(() {
                    _selectedTipo = selected ? e.key : null;
                  });
                },
              );
            }).toList(),
          ),
          const SizedBox(height: 24),
          Text('Rango de fechas',
              style: Theme.of(context).textTheme.titleSmall),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  icon: const Icon(Icons.calendar_today, size: 16),
                  label: Text(
                    _fromDate != null
                        ? DateFormat('d MMM yyyy', 'es_ES').format(_fromDate!)
                        : 'Desde',
                  ),
                  onPressed: () async {
                    final picked = await showDatePicker(
                      context: context,
                      initialDate: _fromDate ?? DateTime(2026, 3, 20),
                      firstDate: DateTime(2025),
                      lastDate: DateTime(2027),
                    );
                    if (picked != null) setState(() => _fromDate = picked);
                  },
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: OutlinedButton.icon(
                  icon: const Icon(Icons.calendar_today, size: 16),
                  label: Text(
                    _toDate != null
                        ? DateFormat('d MMM yyyy', 'es_ES').format(_toDate!)
                        : 'Hasta',
                  ),
                  onPressed: () async {
                    final picked = await showDatePicker(
                      context: context,
                      initialDate: _toDate ?? DateTime(2026, 4, 12),
                      firstDate: DateTime(2025),
                      lastDate: DateTime(2027),
                    );
                    if (picked != null) setState(() => _toDate = picked);
                  },
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                widget.ref.read(eventoFilterProvider.notifier).state =
                    EventoFilter(
                  tipo: _selectedTipo,
                  q: widget.ref.read(eventoFilterProvider).q,
                  fromDate: _fromDate,
                  toDate: _toDate,
                );
                Navigator.pop(context);
              },
              child: const Text('Aplicar filtros'),
            ),
          ),
          const SizedBox(height: 8),
        ],
      ),
    );
  }
}

// --------------- Event Card ---------------

class _EventoCard extends StatelessWidget {
  final Evento evento;
  final VoidCallback onTap;

  const _EventoCard({required this.evento, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('EEE d MMM, HH:mm', 'es_ES');
    final ubicacion = evento.ubicacionTexto;
    final color = tipoColor(evento.tipo);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(height: 4, color: color),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        child: Text(
                          evento.titulo,
                          style: Theme.of(context)
                              .textTheme
                              .titleMedium
                              ?.copyWith(fontWeight: FontWeight.bold),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: color.withAlpha(25),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: color.withAlpha(80)),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(tipoIcons[evento.tipo] ?? Icons.event,
                                size: 14, color: color),
                            const SizedBox(width: 4),
                            Text(
                              tipoLabels[evento.tipo] ?? evento.tipo,
                              style: TextStyle(
                                  fontSize: 11,
                                  color: color,
                                  fontWeight: FontWeight.w600),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      const Icon(Icons.access_time, size: 16),
                      const SizedBox(width: 6),
                      Text(
                        dateFormat.format(evento.fechaInicio),
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ],
                  ),
                  if (ubicacion != null && ubicacion.trim().isNotEmpty) ...[
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        const Icon(Icons.location_on, size: 16),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            ubicacion,
                            style: Theme.of(context).textTheme.bodyMedium,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ],
                  if (!evento.esGratuito) ...[
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: Colors.green[50],
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        '${evento.precio.toStringAsFixed(evento.precio.truncateToDouble() == evento.precio ? 0 : 2)} ${evento.moneda}',
                        style: TextStyle(
                          color: Colors.green[800],
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

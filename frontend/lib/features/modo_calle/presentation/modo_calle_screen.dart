import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/legacy.dart';
import 'package:latlong2/latlong.dart';

import '../../../core/network/api_client.dart';
import '../../auth/presentation/providers/auth_provider.dart';
import 'widgets/map_overlays.dart';
import 'widgets/modo_calle_map.dart';

// ─────────────────────────── State ───────────────────────────

enum StreetConnectionStatus { connected, disconnected, offline }

class RouteAlternativeUi {
  final int etaSeconds;
  final List<List<double>> polyline;
  final List<String> explanation;

  const RouteAlternativeUi({
    required this.etaSeconds,
    required this.polyline,
    required this.explanation,
  });
}

class ModoCalleState {
  final bool isLoading;
  final String? error;
  final int? etaSeconds;
  final double bullaScore;
  final String nextStop;
  final List<String> warnings;
  final List<List<double>> polyline;
  final List<String> explanation;
  final List<RouteAlternativeUi> alternatives;
  final StreetConnectionStatus connectionStatus;
  final bool is3DView;

  const ModoCalleState({
    this.isLoading = false,
    this.error,
    this.etaSeconds,
    this.bullaScore = 0,
    this.nextStop = 'Siguiente punto',
    this.warnings = const [],
    this.polyline = const [],
    this.explanation = const [],
    this.alternatives = const [],
    this.connectionStatus = StreetConnectionStatus.disconnected,
    this.is3DView = false,
  });

  ModoCalleState copyWith({
    bool? isLoading,
    String? error,
    int? etaSeconds,
    double? bullaScore,
    String? nextStop,
    List<String>? warnings,
    List<List<double>>? polyline,
    List<String>? explanation,
    List<RouteAlternativeUi>? alternatives,
    StreetConnectionStatus? connectionStatus,
    bool? is3DView,
  }) {
    return ModoCalleState(
      isLoading: isLoading ?? this.isLoading,
      error: error,
      etaSeconds: etaSeconds ?? this.etaSeconds,
      bullaScore: bullaScore ?? this.bullaScore,
      nextStop: nextStop ?? this.nextStop,
      warnings: warnings ?? this.warnings,
      polyline: polyline ?? this.polyline,
      explanation: explanation ?? this.explanation,
      alternatives: alternatives ?? this.alternatives,
      connectionStatus: connectionStatus ?? this.connectionStatus,
      is3DView: is3DView ?? this.is3DView,
    );
  }
}

// ─────────────────────────── Notifier ───────────────────────────

class ModoCalleNotifier extends StateNotifier<ModoCalleState> {
  final ApiClient _apiClient;
  WebSocket? _ws;
  Timer? _locationTimer;
  Timer? _pollingTimer;
  int _tick = 0;
  DateTime _lastLocationSentAt = DateTime.fromMillisecondsSinceEpoch(0);

  ModoCalleNotifier(this._apiClient) : super(const ModoCalleState());

  /// Posicion simulada del usuario (basada en tick).
  LatLng get simulatedUserPosition => LatLng(
        37.3921 + (_tick % 8) * 0.0001,
        -5.9968 - (_tick % 8) * 0.0001,
      );

  void toggle3DView() {
    state = state.copyWith(is3DView: !state.is3DView);
  }

  Future<void> recalculateNow({bool avoidBulla = true}) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _apiClient.dio.post(
        '/routing/optimal',
        data: {
          'origin': [37.3921, -5.9968],
          'destination': [37.3938, -5.9994],
          'datetime': DateTime.now().toIso8601String(),
          'constraints': {'avoid_bulla': avoidBulla, 'max_walk_km': 5},
        },
      );
      _applyRoute(response.data as Map<String, dynamic>);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void _applyRoute(Map<String, dynamic> route) {
    final alternatives = (route['alternatives'] as List<dynamic>? ?? [])
        .map(
          (alt) => RouteAlternativeUi(
            etaSeconds: (alt as Map<String, dynamic>)['eta_seconds'] as int,
            polyline: (alt['polyline'] as List<dynamic>)
                .map((point) => (point as List<dynamic>).map((e) => (e as num).toDouble()).toList())
                .toList(),
            explanation: (alt['explanation'] as List<dynamic>).map((e) => e.toString()).toList(),
          ),
        )
        .toList();

    state = state.copyWith(
      isLoading: false,
      etaSeconds: route['eta_seconds'] as int,
      warnings: (route['warnings'] as List<dynamic>).map((e) => e.toString()).toList(),
      bullaScore: (route['bulla_score'] as num?)?.toDouble() ?? 0.0,
      polyline: (route['polyline'] as List<dynamic>)
          .map((point) => (point as List<dynamic>).map((e) => (e as num).toDouble()).toList())
          .toList(),
      explanation: (route['explanation'] as List<dynamic>).map((e) => e.toString()).toList(),
      alternatives: alternatives,
      nextStop: 'Punto ${((route['polyline'] as List<dynamic>).length).clamp(1, 99)}',
    );
  }

  Future<void> startStreetMode() async {
    await connectWs();
    await recalculateNow();
  }

  Future<void> connectWs() async {
    try {
      final httpBase = ApiClient.baseUrl.replaceFirst('/api/v1', '');
      final wsBase = httpBase.startsWith('https://')
          ? httpBase.replaceFirst('https://', 'wss://')
          : httpBase.replaceFirst('http://', 'ws://');
      final uri = Uri.parse('$wsBase/api/v1/routing/ws/mode-calle?plan_id=demo-plan');
      _ws = await WebSocket.connect(uri.toString());
      state = state.copyWith(connectionStatus: StreetConnectionStatus.connected);

      _ws!.listen((message) {
        final data = jsonDecode(message as String) as Map<String, dynamic>;
        if (data['type'] == 'route_update') {
          _applyRoute(data['route'] as Map<String, dynamic>);
        } else if (data['type'] == 'warning') {
          final warning = data['detail']?.toString() ?? 'Aviso';
          state = state.copyWith(warnings: [...state.warnings, warning]);
        }
      }, onDone: _onWsDisconnected, onError: (_) => _onWsDisconnected());

      _pollingTimer?.cancel();
      _locationTimer?.cancel();
      _locationTimer = Timer.periodic(const Duration(seconds: 5), (_) {
        _sendLocationUpdate(force: false);
      });
    } catch (e) {
      _onWsDisconnected();
      state = state.copyWith(error: e.toString());
    }
  }

  void _sendLocationUpdate({required bool force}) {
    final now = DateTime.now();
    if (!force && now.difference(_lastLocationSentAt).inSeconds < 5) return;

    _tick += 1;
    _lastLocationSentAt = now;
    _ws?.add(jsonEncode({
      'type': 'location_update',
      'location': {
        'lat': 37.3921 + (_tick % 8) * 0.0001,
        'lng': -5.9968 - (_tick % 8) * 0.0001,
      },
      'datetime': now.toIso8601String(),
      'target': {'type': 'event', 'id': 'macarena'},
      'constraints': {'avoid_bulla': true, 'max_walk_km': 5},
    }));
  }

  void _onWsDisconnected() {
    state = state.copyWith(connectionStatus: StreetConnectionStatus.offline);
    _startOfflinePolling();
  }

  void _startOfflinePolling() {
    _pollingTimer?.cancel();
    _pollingTimer = Timer.periodic(const Duration(seconds: 15), (_) async {
      try {
        final response = await _apiClient.dio.get('/routing/last', queryParameters: {'plan_id': 'demo-plan'});
        final route = (response.data as Map<String, dynamic>)['route'] as Map<String, dynamic>;
        _applyRoute(route);
      } catch (_) {
        // degrade silently
      }
    });
  }

  Future<void> reconnect() async {
    state = state.copyWith(connectionStatus: StreetConnectionStatus.disconnected);
    await connectWs();
  }

  Future<void> activatePlanB() async {
    await recalculateNow(avoidBulla: true);
  }

  Future<void> reportBulla() async {
    try {
      await _apiClient.dio.post(
        '/crowd/reports',
        data: {
          'lat': 37.3921,
          'lng': -5.9968,
          'severity': state.bullaScore >= 0.75 ? 5 : 3,
          'note': 'Reporte rapido desde Modo Calle',
        },
      );
      state = state.copyWith(warnings: [...state.warnings, 'Reporte enviado']);
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }

  @override
  void dispose() {
    _locationTimer?.cancel();
    _pollingTimer?.cancel();
    _ws?.close();
    super.dispose();
  }
}

final modoCalleProvider = StateNotifierProvider<ModoCalleNotifier, ModoCalleState>((ref) {
  return ModoCalleNotifier(ref.watch(apiClientProvider));
});

// ─────────────────────────── UI ───────────────────────────

class ModoCalleScreen extends ConsumerWidget {
  const ModoCalleScreen({super.key});

  String _statusLabel(StreetConnectionStatus status) {
    switch (status) {
      case StreetConnectionStatus.connected:
        return 'Conectado';
      case StreetConnectionStatus.offline:
        return 'Offline';
      case StreetConnectionStatus.disconnected:
        return 'Desconectado';
    }
  }

  Color _statusColor(StreetConnectionStatus status) {
    switch (status) {
      case StreetConnectionStatus.connected:
        return Colors.green;
      case StreetConnectionStatus.offline:
        return Colors.orange;
      case StreetConnectionStatus.disconnected:
        return Colors.red;
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(modoCalleProvider);
    final notifier = ref.read(modoCalleProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Modo Calle'),
        actions: [
          // Toggle 2D / 3D
          IconButton(
            icon: Icon(state.is3DView ? Icons.view_in_ar : Icons.map_outlined),
            tooltip: state.is3DView ? 'Vista 2D (cenital)' : 'Vista 3D',
            onPressed: notifier.toggle3DView,
          ),
        ],
      ),
      body: Column(
        children: [
          // ── Barra compacta de acciones ──
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surface,
              border: Border(
                bottom: BorderSide(color: Colors.grey.shade300, width: 0.5),
              ),
            ),
            child: Row(
              children: [
                _CompactActionButton(
                  icon: Icons.play_arrow,
                  label: 'Iniciar',
                  onPressed: notifier.startStreetMode,
                  filled: true,
                ),
                const SizedBox(width: 6),
                _CompactActionButton(
                  icon: Icons.sync,
                  label: 'Reconectar',
                  onPressed: notifier.reconnect,
                ),
                const SizedBox(width: 6),
                _CompactActionButton(
                  icon: Icons.alt_route,
                  label: 'Plan B',
                  onPressed: notifier.activatePlanB,
                ),
                const SizedBox(width: 6),
                _CompactActionButton(
                  icon: Icons.campaign,
                  label: 'Bulla',
                  onPressed: notifier.reportBulla,
                  filled: true,
                ),
              ],
            ),
          ),

          // ── Mapa con overlays ──
          Expanded(
            child: Stack(
              children: [
                // Mapa interactivo
                ModoCalleMap(
                  backendPolyline: state.polyline,
                  is3DView: state.is3DView,
                  userPosition: notifier.simulatedUserPosition,
                ),

                // Status chip (esquina superior izquierda)
                Positioned(
                  top: 12,
                  left: 12,
                  child: StatusChip(
                    statusLabel: _statusLabel(state.connectionStatus),
                    statusColor: _statusColor(state.connectionStatus),
                    etaSeconds: state.etaSeconds,
                    nextStop: state.nextStop,
                  ),
                ),

                // Bulla meter (esquina superior derecha)
                Positioned(
                  top: 12,
                  right: 12,
                  child: BullaMeterChip(score: state.bullaScore),
                ),

                // Warnings (parte inferior del mapa)
                if (state.warnings.isNotEmpty)
                  Positioned(
                    bottom: 70,
                    left: 12,
                    right: 12,
                    child: WarningsBanner(warnings: state.warnings),
                  ),

                // Alternativas (boton flotante izquierda)
                if (state.alternatives.isNotEmpty)
                  Positioned(
                    bottom: 16,
                    left: 12,
                    child: FloatingActionButton.extended(
                      heroTag: 'alternatives',
                      onPressed: () => _showAlternatives(context, state),
                      backgroundColor: const Color(0xFFD4AF37),
                      foregroundColor: Colors.black87,
                      icon: const Icon(Icons.swap_horiz, size: 18),
                      label: Text('${state.alternatives.length} rutas'),
                    ),
                  ),

                // Indicador de carga
                if (state.isLoading)
                  const Positioned(
                    top: 70,
                    left: 0,
                    right: 0,
                    child: LinearProgressIndicator(),
                  ),

                // Error
                if (state.error != null)
                  Positioned(
                    bottom: 70,
                    left: 12,
                    right: 12,
                    child: Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: Colors.red.shade50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.red.shade300),
                      ),
                      child: Text(
                        state.error!,
                        style: TextStyle(fontSize: 12, color: Colors.red.shade900),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _showAlternatives(BuildContext context, ModoCalleState state) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade400,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              const Text(
                'Rutas alternativas',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              ...state.alternatives.map(
                (alt) => Card(
                  child: ListTile(
                    leading: const Icon(Icons.alt_route),
                    title: Text('ETA ${alt.etaSeconds ~/ 60} min'),
                    subtitle: Text(
                      alt.explanation.join(' > '),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    trailing: const Icon(Icons.chevron_right),
                  ),
                ),
              ),
              const SizedBox(height: 8),
            ],
          ),
        );
      },
    );
  }
}

// ── Widget auxiliar: boton compacto para la barra de acciones ──

class _CompactActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onPressed;
  final bool filled;

  const _CompactActionButton({
    required this.icon,
    required this.label,
    required this.onPressed,
    this.filled = false,
  });

  @override
  Widget build(BuildContext context) {
    final primary = Theme.of(context).colorScheme.primary;

    if (filled) {
      return Expanded(
        child: SizedBox(
          height: 36,
          child: FilledButton.icon(
            onPressed: onPressed,
            icon: Icon(icon, size: 16),
            label: Text(label, style: const TextStyle(fontSize: 12)),
            style: FilledButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ),
      );
    }

    return Expanded(
      child: SizedBox(
        height: 36,
        child: OutlinedButton.icon(
          onPressed: onPressed,
          icon: Icon(icon, size: 16, color: primary),
          label: Text(label, style: TextStyle(fontSize: 12, color: primary)),
          style: OutlinedButton.styleFrom(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
      ),
    );
  }
}

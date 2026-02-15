import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/api_client.dart';
import '../../auth/presentation/providers/auth_provider.dart';

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
    );
  }
}

class ModoCalleNotifier extends StateNotifier<ModoCalleState> {
  final ApiClient _apiClient;
  WebSocket? _ws;
  Timer? _locationTimer;
  Timer? _pollingTimer;
  int _tick = 0;
  DateTime _lastLocationSentAt = DateTime.fromMillisecondsSinceEpoch(0);

  ModoCalleNotifier(this._apiClient) : super(const ModoCalleState());

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
          'note': 'Reporte rápido desde Modo Calle',
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
      appBar: AppBar(title: const Text('Modo Calle')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: _statusColor(state.connectionStatus).withOpacity(0.15),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                'Estado: ${_statusLabel(state.connectionStatus)} · ETA: ${state.etaSeconds != null ? '${state.etaSeconds! ~/ 60} min' : '--'} · ${state.nextStop}',
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: notifier.startStreetMode,
                    icon: const Icon(Icons.play_arrow),
                    label: const Text('Iniciar'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: notifier.reconnect,
                    icon: const Icon(Icons.sync),
                    label: const Text('Reconectar'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: notifier.activatePlanB,
                    icon: const Icon(Icons.alt_route),
                    label: const Text('Plan B'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: notifier.reportBulla,
                    icon: const Icon(Icons.campaign),
                    label: const Text('Reportar bulla'),
                  ),
                ),
              ],
            ),
            if (state.connectionStatus == StreetConnectionStatus.offline)
              const Padding(
                padding: EdgeInsets.only(top: 8.0),
                child: Text('Última ruta disponible (polling ligero activo)'),
              ),

            const SizedBox(height: 8),
            const Text('BullaMeter'),
            LinearProgressIndicator(value: state.bullaScore.clamp(0.0, 1.0)),
            Text('Score: ${(state.bullaScore * 100).toStringAsFixed(0)}%'),
            if (state.warnings.isNotEmpty)
              ...state.warnings.map((w) => Padding(
                    padding: const EdgeInsets.only(top: 6),
                    child: Text('⚠ $w'),
                  )),
            const SizedBox(height: 10),
            const Text('Turn-by-turn simplificado'),
            Expanded(
              child: ListView.builder(
                itemCount: state.polyline.length,
                itemBuilder: (context, index) {
                  final point = state.polyline[index];
                  return ListTile(
                    dense: true,
                    leading: Text('${index + 1}'),
                    title: Text('${point[0].toStringAsFixed(5)}, ${point[1].toStringAsFixed(5)}'),
                  );
                },
              ),
            ),
            if (state.alternatives.isNotEmpty) ...[
              const Divider(),
              const Text('Alternativas'),
              ...state.alternatives.map(
                (alt) => ListTile(
                  title: Text('ETA ${alt.etaSeconds ~/ 60} min'),
                  subtitle: Text(alt.explanation.join(' · ')),
                ),
              ),
            ],
            if (state.error != null) Text(state.error!, style: const TextStyle(color: Colors.red)),
          ],
        ),
      ),
    );
  }
}

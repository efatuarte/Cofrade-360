import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/api_client.dart';
import '../../auth/presentation/providers/auth_provider.dart';

class ModoCalleState {
  final bool isLoading;
  final String? error;
  final int? etaSeconds;
  final List<String> warnings;
  final List<List<double>> polyline;
  final List<String> explanation;
  final bool wsConnected;

  const ModoCalleState({
    this.isLoading = false,
    this.error,
    this.etaSeconds,
    this.warnings = const [],
    this.polyline = const [],
    this.explanation = const [],
    this.wsConnected = false,
  });

  ModoCalleState copyWith({
    bool? isLoading,
    String? error,
    int? etaSeconds,
    List<String>? warnings,
    List<List<double>>? polyline,
    List<String>? explanation,
    bool? wsConnected,
  }) {
    return ModoCalleState(
      isLoading: isLoading ?? this.isLoading,
      error: error,
      etaSeconds: etaSeconds ?? this.etaSeconds,
      warnings: warnings ?? this.warnings,
      polyline: polyline ?? this.polyline,
      explanation: explanation ?? this.explanation,
      wsConnected: wsConnected ?? this.wsConnected,
    );
  }
}

class ModoCalleNotifier extends StateNotifier<ModoCalleState> {
  final ApiClient _apiClient;
  WebSocket? _ws;
  Timer? _locationTimer;
  int _tick = 0;

  ModoCalleNotifier(this._apiClient) : super(const ModoCalleState());

  Future<void> recalculateNow() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _apiClient.dio.post(
        '/routing/optimal',
        data: {
          'origin': [37.3862 + (_tick % 5) * 0.0002, -5.9926 - (_tick % 5) * 0.0001],
          'datetime': DateTime.now().toIso8601String(),
          'target': {'type': 'event', 'id': 'macarena'},
          'constraints': {'avoid_bulla': true, 'max_walk_km': 5},
        },
      );
      final data = response.data as Map<String, dynamic>;
      state = state.copyWith(
        isLoading: false,
        etaSeconds: data['eta_seconds'] as int,
        warnings: (data['warnings'] as List<dynamic>).map((e) => e.toString()).toList(),
        polyline: (data['polyline'] as List<dynamic>)
            .map((point) => (point as List<dynamic>).map((e) => (e as num).toDouble()).toList())
            .toList(),
        explanation: (data['explanation'] as List<dynamic>).map((e) => e.toString()).toList(),
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> connectWs() async {
    try {
      final httpBase = ApiClient.baseUrl.replaceFirst('/api/v1', '');
      final wsBase = httpBase.startsWith('https://')
          ? httpBase.replaceFirst('https://', 'wss://')
          : httpBase.replaceFirst('http://', 'ws://');
      final uri = Uri.parse('$wsBase/api/v1/routing/ws/mode-calle?plan_id=demo-plan');
      _ws = await WebSocket.connect(uri.toString());
      state = state.copyWith(wsConnected: true);

      _ws!.listen((message) {
        final data = jsonDecode(message as String) as Map<String, dynamic>;
        final route = data['route'] as Map<String, dynamic>;
        state = state.copyWith(
          etaSeconds: route['eta_seconds'] as int,
          warnings: (route['warnings'] as List<dynamic>).map((e) => e.toString()).toList(),
          polyline: (route['polyline'] as List<dynamic>)
              .map((point) => (point as List<dynamic>).map((e) => (e as num).toDouble()).toList())
              .toList(),
          explanation: (route['explanation'] as List<dynamic>).map((e) => e.toString()).toList(),
        );
      }, onDone: () {
        state = state.copyWith(wsConnected: false);
      }, onError: (_) {
        state = state.copyWith(wsConnected: false);
      });

      _locationTimer?.cancel();
      _locationTimer = Timer.periodic(const Duration(seconds: 6), (_) {
        _tick += 1;
        _ws?.add(jsonEncode({
          'location': {
            'lat': 37.3862 + (_tick % 8) * 0.00015,
            'lng': -5.9926 - (_tick % 8) * 0.0001,
          },
          'datetime': DateTime.now().toIso8601String(),
          'target': {'type': 'event', 'id': 'macarena'},
          'constraints': {'avoid_bulla': true, 'max_walk_km': 5},
        }));
      });
    } catch (e) {
      state = state.copyWith(error: e.toString(), wsConnected: false);
    }
  }

  @override
  void dispose() {
    _locationTimer?.cancel();
    _ws?.close();
    super.dispose();
  }
}

final modoCalleProvider = StateNotifierProvider<ModoCalleNotifier, ModoCalleState>((ref) {
  return ModoCalleNotifier(ref.watch(apiClientProvider));
});

class ModoCalleScreen extends ConsumerWidget {
  const ModoCalleScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(modoCalleProvider);
    final notifier = ref.read(modoCalleProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Modo Calle'),
        actions: [
          Icon(
            state.wsConnected ? Icons.wifi : Icons.wifi_off,
            color: state.wsConnected ? Colors.green : Colors.red,
          ),
          const SizedBox(width: 12),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: state.isLoading ? null : notifier.recalculateNow,
                    icon: const Icon(Icons.route),
                    label: const Text('Recalcular'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: notifier.connectWs,
                    icon: const Icon(Icons.sync),
                    label: const Text('Conectar WS'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text('ETA: ${state.etaSeconds != null ? '${state.etaSeconds! ~/ 60} min' : '--'}',
                style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            if (state.warnings.isNotEmpty)
              ...state.warnings.map((w) => ListTile(
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    leading: const Icon(Icons.warning_amber, color: Colors.orange),
                    title: Text(w),
                  )),
            const SizedBox(height: 8),
            Text('Ruta (puntos): ${state.polyline.length}'),
            Expanded(
              child: ListView.builder(
                itemCount: state.polyline.length,
                itemBuilder: (context, index) {
                  final point = state.polyline[index];
                  return Text('• ${point[0].toStringAsFixed(5)}, ${point[1].toStringAsFixed(5)}');
                },
              ),
            ),
            if (state.explanation.isNotEmpty) ...[
              const Divider(),
              const Text('Explicación:'),
              ...state.explanation.map((e) => Text('- $e')),
            ],
            if (state.error != null) ...[
              const SizedBox(height: 8),
              Text(state.error!, style: const TextStyle(color: Colors.red)),
            ],
          ],
        ),
      ),
    );
  }
}

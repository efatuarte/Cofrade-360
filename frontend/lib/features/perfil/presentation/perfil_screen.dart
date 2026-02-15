import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../main.dart';
import '../../auth/presentation/providers/auth_provider.dart';

class PerfilScreen extends ConsumerStatefulWidget {
  const PerfilScreen({super.key});

  @override
  ConsumerState<PerfilScreen> createState() => _PerfilScreenState();
}

class _PerfilScreenState extends ConsumerState<PerfilScreen> {
  bool _notificationsProcessions = true;
  bool _notificationsRestrictions = true;
  bool _isLoadingPrefs = true;
  bool _isSavingPrefs = false;

  @override
  void initState() {
    super.initState();
    _loadNotificationSettings();
  }

  Future<void> _loadNotificationSettings() async {
    try {
      final response = await ref.read(apiClientProvider).dio.get('/auth/me/notifications');
      final data = response.data as Map<String, dynamic>;
      if (!mounted) return;
      setState(() {
        _notificationsProcessions = data['notifications_processions'] == true;
        _notificationsRestrictions = data['notifications_restrictions'] == true;
        _isLoadingPrefs = false;
      });
    } on DioException {
      if (!mounted) return;
      setState(() {
        _isLoadingPrefs = false;
      });
    }
  }

  Future<void> _saveNotificationSettings({
    bool? notificationsProcessions,
    bool? notificationsRestrictions,
  }) async {
    setState(() {
      _isSavingPrefs = true;
    });
    try {
      final payload = <String, dynamic>{};
      if (notificationsProcessions != null) {
        payload['notifications_processions'] = notificationsProcessions;
      }
      if (notificationsRestrictions != null) {
        payload['notifications_restrictions'] = notificationsRestrictions;
      }

      final response = await ref.read(apiClientProvider).dio.patch(
            '/auth/me/notifications',
            data: payload,
          );
      final data = response.data as Map<String, dynamic>;

      if (!mounted) return;
      setState(() {
        _notificationsProcessions = data['notifications_processions'] == true;
        _notificationsRestrictions = data['notifications_restrictions'] == true;
        _isSavingPrefs = false;
      });
    } on DioException {
      if (!mounted) return;
      setState(() {
        if (notificationsProcessions != null) {
          _notificationsProcessions = !_notificationsProcessions;
        }
        if (notificationsRestrictions != null) {
          _notificationsRestrictions = !_notificationsRestrictions;
        }
        _isSavingPrefs = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No se pudieron guardar tus preferencias.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final themeMode = ref.watch(themeModeProvider);
    final authState = ref.watch(authProvider);
    final user = authState.user;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Perfil'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await ref.read(authProvider.notifier).logout();
            },
            tooltip: 'Cerrar Sesión',
          ),
        ],
      ),
      body: ListView(
        children: [
          const SizedBox(height: 24),
          CircleAvatar(
            radius: 50,
            backgroundColor: Theme.of(context).colorScheme.primary,
            child: const Icon(Icons.person, size: 60, color: Colors.white),
          ),
          const SizedBox(height: 16),
          Center(
            child: Text(
              user?.email ?? 'Usuario Cofrade',
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ),
          const SizedBox(height: 32),
          _buildSection(
            context,
            title: 'Apariencia',
            children: [
              ListTile(
                leading: const Icon(Icons.brightness_6),
                title: const Text('Tema'),
                trailing: SegmentedButton<ThemeMode>(
                  segments: const [
                    ButtonSegment(
                      value: ThemeMode.light,
                      label: Text('Claro'),
                      icon: Icon(Icons.light_mode, size: 16),
                    ),
                    ButtonSegment(
                      value: ThemeMode.dark,
                      label: Text('Oscuro'),
                      icon: Icon(Icons.dark_mode, size: 16),
                    ),
                    ButtonSegment(
                      value: ThemeMode.system,
                      label: Text('Auto'),
                      icon: Icon(Icons.auto_awesome, size: 16),
                    ),
                  ],
                  selected: {themeMode},
                  onSelectionChanged: (Set<ThemeMode> newSelection) {
                    ref.read(themeModeProvider.notifier).state = newSelection.first;
                  },
                ),
              ),
            ],
          ),
          _buildSection(
            context,
            title: 'Notificaciones',
            children: [
              if (_isLoadingPrefs)
                const ListTile(
                  leading: SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                  title: Text('Cargando preferencias...'),
                ),
              SwitchListTile(
                secondary: const Icon(Icons.notifications),
                title: const Text('Alertas de Procesiones'),
                subtitle: const Text('Recibe notificaciones cuando una procesión esté cerca'),
                value: _notificationsProcessions,
                onChanged: (_isLoadingPrefs || _isSavingPrefs)
                    ? null
                    : (bool value) {
                        setState(() {
                          _notificationsProcessions = value;
                        });
                        _saveNotificationSettings(notificationsProcessions: value);
                      },
              ),
              SwitchListTile(
                secondary: const Icon(Icons.warning),
                title: const Text('Cortes de Tráfico'),
                subtitle: const Text('Avisos de cortes de calle en tu ruta'),
                value: _notificationsRestrictions,
                onChanged: (_isLoadingPrefs || _isSavingPrefs)
                    ? null
                    : (bool value) {
                        setState(() {
                          _notificationsRestrictions = value;
                        });
                        _saveNotificationSettings(notificationsRestrictions: value);
                      },
              ),
            ],
          ),
          _buildSection(
            context,
            title: 'Acerca de',
            children: [
              ListTile(
                leading: const Icon(Icons.info),
                title: const Text('Versión'),
                trailing: const Text('1.0.0'),
              ),
              ListTile(
                leading: const Icon(Icons.help),
                title: const Text('Ayuda y Soporte'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  // TODO: Navigate to help
                },
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSection(BuildContext context, {required String title, required List<Widget> children}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Text(
            title,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: Theme.of(context).colorScheme.primary,
                  fontWeight: FontWeight.bold,
                ),
          ),
        ),
        ...children,
        const Divider(),
      ],
    );
  }
}

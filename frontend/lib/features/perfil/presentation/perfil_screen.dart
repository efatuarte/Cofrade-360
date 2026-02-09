import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../main.dart';

class PerfilScreen extends ConsumerWidget {
  const PerfilScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeModeProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Perfil'),
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
              'Usuario Cofrade',
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
              SwitchListTile(
                secondary: const Icon(Icons.notifications),
                title: const Text('Alertas de Procesiones'),
                subtitle: const Text('Recibe notificaciones cuando una procesión esté cerca'),
                value: true,
                onChanged: (bool value) {
                  // TODO: Handle notification toggle
                },
              ),
              SwitchListTile(
                secondary: const Icon(Icons.warning),
                title: const Text('Cortes de Tráfico'),
                subtitle: const Text('Avisos de cortes de calle en tu ruta'),
                value: true,
                onChanged: (bool value) {
                  // TODO: Handle notification toggle
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

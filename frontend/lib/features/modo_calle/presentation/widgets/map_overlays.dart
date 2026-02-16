import 'package:flutter/material.dart';

/// Chip compacto de estado de conexión + ETA, superpuesto en el mapa.
class StatusChip extends StatelessWidget {
  final String statusLabel;
  final Color statusColor;
  final int? etaSeconds;
  final String nextStop;

  const StatusChip({
    super.key,
    required this.statusLabel,
    required this.statusColor,
    this.etaSeconds,
    required this.nextStop,
  });

  @override
  Widget build(BuildContext context) {
    final eta = etaSeconds != null ? '${etaSeconds! ~/ 60} min' : '--';

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.92),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.15),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 10,
            height: 10,
            decoration: BoxDecoration(
              color: statusColor,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 6),
          Text(
            '$statusLabel  |  ETA $eta',
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: Colors.black87,
            ),
          ),
        ],
      ),
    );
  }
}

/// Indicador circular de bulla superpuesto en el mapa.
class BullaMeterChip extends StatelessWidget {
  final double score;

  const BullaMeterChip({super.key, required this.score});

  Color get _color {
    if (score < 0.3) return Colors.green;
    if (score < 0.6) return Colors.orange;
    return Colors.red;
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 52,
      height: 52,
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.92),
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.15),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Stack(
        alignment: Alignment.center,
        children: [
          SizedBox(
            width: 40,
            height: 40,
            child: CircularProgressIndicator(
              value: score.clamp(0.0, 1.0),
              strokeWidth: 4,
              color: _color,
              backgroundColor: Colors.grey.shade200,
            ),
          ),
          Text(
            '${(score * 100).toStringAsFixed(0)}%',
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.bold,
              color: _color,
            ),
          ),
        ],
      ),
    );
  }
}

/// Banner de avisos/warnings superpuesto en la parte inferior del mapa.
class WarningsBanner extends StatelessWidget {
  final List<String> warnings;

  const WarningsBanner({super.key, required this.warnings});

  @override
  Widget build(BuildContext context) {
    if (warnings.isEmpty) return const SizedBox.shrink();

    // Mostrar solo el último aviso para no saturar
    final lastWarning = warnings.last;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.orange.shade50.withValues(alpha: 0.95),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.orange.shade300),
      ),
      child: Row(
        children: [
          Icon(Icons.warning_amber_rounded,
              color: Colors.orange.shade700, size: 18),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              lastWarning,
              style: TextStyle(
                fontSize: 12,
                color: Colors.orange.shade900,
                fontWeight: FontWeight.w500,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          if (warnings.length > 1)
            Container(
              margin: const EdgeInsets.only(left: 6),
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.orange.shade200,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                '+${warnings.length - 1}',
                style: TextStyle(
                  fontSize: 10,
                  color: Colors.orange.shade900,
                ),
              ),
            ),
        ],
      ),
    );
  }
}

import 'package:equatable/equatable.dart';

class BrotherhoodMedia extends Equatable {
  final String assetId;
  final String url;

  const BrotherhoodMedia({required this.assetId, required this.url});

  @override
  List<Object?> get props => [assetId, url];
}

class Hermandad extends Equatable {
  final String id;
  final String nameShort;
  final String nameFull;
  final String? logoAssetId;
  final String? churchId;
  final String? ssDay;
  final String? history;
  final String? highlights;
  final String? stats;
  final DateTime createdAt;
  final String? churchName;

  const Hermandad({
    required this.id,
    required this.nameShort,
    required this.nameFull,
    this.logoAssetId,
    this.churchId,
    this.ssDay,
    this.history,
    this.highlights,
    this.stats,
    required this.createdAt,
    this.churchName,
  });

  @override
  List<Object?> get props => [id, nameShort, nameFull, ssDay, churchId];
}

class PaginatedHermandades {
  final List<Hermandad> items;
  final int page;
  final int pageSize;
  final int total;

  const PaginatedHermandades({
    required this.items,
    required this.page,
    required this.pageSize,
    required this.total,
  });
}

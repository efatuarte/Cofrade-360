import 'package:equatable/equatable.dart';

class PlanItemWarning extends Equatable {
  final String itemId;
  final String conflictWithItemId;
  final String detail;

  const PlanItemWarning({
    required this.itemId,
    required this.conflictWithItemId,
    required this.detail,
  });

  @override
  List<Object?> get props => [itemId, conflictWithItemId, detail];
}

class PlanItemEntity extends Equatable {
  final String id;
  final String planId;
  final String itemType;
  final String? eventId;
  final String? brotherhoodId;
  final DateTime desiredTimeStart;
  final DateTime desiredTimeEnd;
  final double? lat;
  final double? lng;
  final int position;
  final String? notes;

  const PlanItemEntity({
    required this.id,
    required this.planId,
    required this.itemType,
    this.eventId,
    this.brotherhoodId,
    required this.desiredTimeStart,
    required this.desiredTimeEnd,
    this.lat,
    this.lng,
    required this.position,
    this.notes,
  });

  @override
  List<Object?> get props => [id, planId, itemType, desiredTimeStart, desiredTimeEnd, position];
}

class UserPlanEntity extends Equatable {
  final String id;
  final String userId;
  final String title;
  final DateTime planDate;
  final List<PlanItemEntity> items;

  const UserPlanEntity({
    required this.id,
    required this.userId,
    required this.title,
    required this.planDate,
    required this.items,
  });

  @override
  List<Object?> get props => [id, userId, title, planDate, items];
}

class AddItemResult extends Equatable {
  final PlanItemEntity item;
  final List<PlanItemWarning> warnings;

  const AddItemResult({required this.item, required this.warnings});

  @override
  List<Object?> get props => [item, warnings];
}

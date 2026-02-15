import 'package:equatable/equatable.dart';

class User extends Equatable {
  final String id;
  final String email;
  final bool isActive;
  final String role;
  final DateTime createdAt;

  const User({
    required this.id,
    required this.email,
    required this.isActive,
    required this.role,
    required this.createdAt,
  });

  @override
  List<Object?> get props => [id, email, isActive, role, createdAt];
}

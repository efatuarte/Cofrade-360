import 'package:dartz/dartz.dart';
import '../../../../core/errors/failures.dart';
import '../../domain/entities/hermandad.dart';
import '../../domain/repositories/hermandades_repository.dart';

class HermandadesRepositoryImpl implements HermandadesRepository {
  final List<Hermandad> _mockHermandades = [
    Hermandad(
      id: '1',
      nombre: 'Hermandad del Gran Poder',
      descripcion: 'Real e Ilustre Hermandad y Cofradía de Nazarenos de Nuestro Padre Jesús del Gran Poder',
      escudo: '🛡️',
      sede: 'Basílica del Gran Poder',
      fechaFundacion: DateTime(1431),
      imagenesTitulares: ['gran_poder.jpg'],
    ),
    Hermandad(
      id: '2',
      nombre: 'Hermandad de la Macarena',
      descripcion: 'Real, Ilustre y Fervorosa Hermandad y Cofradía de Nazarenos de Nuestra Señora del Santo Rosario, Nuestro Padre Jesús de la Sentencia y María Santísima de la Esperanza Macarena',
      escudo: '🛡️',
      sede: 'Basílica de la Macarena',
      fechaFundacion: DateTime(1595),
      imagenesTitulares: ['macarena.jpg'],
    ),
    Hermandad(
      id: '3',
      nombre: 'Hermandad del Cachorro',
      descripcion: 'Pontificia, Real e Ilustre Hermandad Sacramental y Cofradía de Nazarenos del Santísimo Cristo de la Expiración y María Santísima del Patrocinio',
      escudo: '🛡️',
      sede: 'Iglesia de San Lorenzo',
      fechaFundacion: DateTime(1682),
      imagenesTitulares: ['cachorro.jpg'],
    ),
  ];

  @override
  Future<Either<Failure, List<Hermandad>>> getHermandades() async {
    try {
      await Future.delayed(const Duration(milliseconds: 500));
      return Right(_mockHermandades);
    } catch (e) {
      return Left(ServerFailure(e.toString()));
    }
  }

  @override
  Future<Either<Failure, Hermandad>> getHermandadById(String id) async {
    try {
      await Future.delayed(const Duration(milliseconds: 300));
      final hermandad = _mockHermandades.firstWhere((h) => h.id == id);
      return Right(hermandad);
    } catch (e) {
      return Left(ServerFailure('Hermandad no encontrada'));
    }
  }
}

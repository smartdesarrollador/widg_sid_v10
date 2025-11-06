"""
Script de testing para SmartCollectionsManager
Prueba las operaciones CRUD y ejecución de filtros de Smart Collections
"""

import sys
from pathlib import Path
import logging

# Agregar src al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / 'src'))

from core.smart_collections_manager import SmartCollectionsManager
from database.db_manager import DBManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def test_create_collection():
    """Test de creación de Smart Collection"""
    print("\n" + "="*60)
    print("TEST 1: CREAR SMART COLLECTION")
    print("="*60)

    db_path = root_dir / "widget_sidebar.db"
    manager = SmartCollectionsManager(str(db_path))

    # Usar timestamp para nombre único
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_name = f"Test Collection - Python Items {timestamp}"

    # Crear una nueva colección
    try:
        collection_id = manager.create_collection(
            name=test_name,
            description="Colección de prueba para items relacionados con Python",
            icon="🐍",
            color="#3776ab",
            tags_include="python,fastapi",
            item_type="CODE",
            is_favorite=None,
            is_active_filter=True
        )

        if collection_id:
            print(f"  ✓ Smart Collection creada exitosamente con ID: {collection_id}")

            # Verificar que se creó correctamente
            collection = manager.get_collection(collection_id)
            if collection:
                print(f"\n  Detalles de la colección creada:")
                print(f"    - Nombre: {collection['name']}")
                print(f"    - Descripción: {collection['description']}")
                print(f"    - Tags incluir: {collection['tags_include']}")
                print(f"    - Tipo de item: {collection['item_type']}")
                print(f"    - Filtro activo: {collection['is_active_filter']}")
                print(f"    - Color: {collection['color']}")
                print(f"    - Icono: {collection['icon']}")

            return collection_id
        else:
            print("  ✗ Error al crear Smart Collection")
            return None
    except Exception as e:
        print(f"  ✗ Error al crear Smart Collection: {e}")
        return None


def test_read_collections():
    """Test de lectura de Smart Collections"""
    print("\n" + "="*60)
    print("TEST 2: LEER SMART COLLECTIONS")
    print("="*60)

    db_path = root_dir / "widget_sidebar.db"
    manager = SmartCollectionsManager(str(db_path))

    # Obtener todas las colecciones
    collections = manager.get_all_collections()
    print(f"\n  Total de colecciones: {len(collections)}")

    if collections:
        print("\n  Colecciones existentes:")
        for collection in collections[:5]:  # Mostrar solo las primeras 5
            print(f"\n    {collection['id']}. {collection['icon']} {collection['name']}")
            print(f"       Descripción: {collection['description']}")
            if collection['tags_include']:
                print(f"       Tags incluir: {collection['tags_include']}")
            if collection['item_type']:
                print(f"       Tipo: {collection['item_type']}")
            print(f"       Activa: {collection['is_active']}")

    # Obtener solo colecciones activas
    active_collections = manager.get_all_collections(active_only=True)
    print(f"\n  Colecciones activas: {len(active_collections)}")

    return len(collections) > 0


def test_search_collections():
    """Test de búsqueda de Smart Collections"""
    print("\n" + "="*60)
    print("TEST 3: BUSCAR SMART COLLECTIONS")
    print("="*60)

    db_path = root_dir / "widget_sidebar.db"
    manager = SmartCollectionsManager(str(db_path))

    # Buscar colecciones con "comando"
    search_term = "comando"
    results = manager.search_collections(search_term)

    print(f"\n  Búsqueda: '{search_term}'")
    print(f"  Resultados encontrados: {len(results)}")

    if results:
        print("\n  Colecciones encontradas:")
        for collection in results:
            print(f"    - {collection['name']}")
            if collection['description']:
                print(f"      {collection['description']}")
    else:
        print("  (No se encontraron coincidencias)")

    # Buscar con otro término
    search_term2 = "favor"
    results2 = manager.search_collections(search_term2)
    print(f"\n  Búsqueda: '{search_term2}'")
    print(f"  Resultados encontrados: {len(results2)}")

    return True


def test_update_collection():
    """Test de actualización de Smart Collection"""
    print("\n" + "="*60)
    print("TEST 4: ACTUALIZAR SMART COLLECTION")
    print("="*60)

    db_path = root_dir / "widget_sidebar.db"
    manager = SmartCollectionsManager(str(db_path))

    # Buscar cualquier colección existente o crear una nueva
    collections = manager.get_all_collections()

    if collections:
        # Usar la primera colección existente
        collection = collections[0]
        print(f"  ℹ Usando colección existente: {collection['name']}")
    else:
        # Crear una nueva con timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print("  ⚠ No hay colecciones. Creando una nueva...")
        try:
            collection_id = manager.create_collection(
                name=f"Test Collection for Update {timestamp}",
                description="Colección de prueba",
                tags_include="python"
            )
            collection = manager.get_collection(collection_id)
        except Exception as e:
            print(f"  ✗ Error al crear colección: {e}")
            return False

    if collection:
        print(f"\n  Colección a actualizar: {collection['name']}")
        print(f"  Tags originales: {collection.get('tags_include', 'N/A')}")

        # Actualizar la colección
        try:
            success = manager.update_collection(
                collection['id'],
                tags_include="python,django,flask",
                description="Colección actualizada con más frameworks Python",
                is_favorite=True
            )

            if success:
                print("  ✓ Smart Collection actualizada exitosamente")

                # Verificar cambios
                updated_collection = manager.get_collection(collection['id'])
                print(f"\n  Tags actualizados: {updated_collection['tags_include']}")
                print(f"  Descripción actualizada: {updated_collection['description']}")
                print(f"  Filtro favoritos: {updated_collection['is_favorite']}")

                return True
            else:
                print("  ✗ Error al actualizar Smart Collection")
                return False
        except Exception as e:
            print(f"  ✗ Error al actualizar Smart Collection: {e}")
            return False
    else:
        print("  ✗ No se pudo encontrar o crear la colección de prueba")
        return False


def test_execute_collection():
    """Test de ejecución de filtros de una colección"""
    print("\n" + "="*60)
    print("TEST 5: EJECUTAR COLECCIÓN (FILTROS)")
    print("="*60)

    db_path = root_dir / "widget_sidebar.db"
    manager = SmartCollectionsManager(str(db_path))

    # Obtener todas las colecciones
    collections = manager.get_all_collections()

    if not collections:
        print("  ⚠ No hay colecciones para ejecutar")
        return False

    # Ejecutar las primeras 3 colecciones
    print(f"\n  Ejecutando colecciones...")

    for collection in collections[:3]:
        print(f"\n  {collection['icon']} {collection['name']}")

        # Ejecutar la colección
        items = manager.execute_collection(collection['id'])

        print(f"    Items encontrados: {len(items)}")

        # Mostrar algunos items (máximo 3)
        if items:
            print(f"    Primeros items:")
            for item in items[:3]:
                print(f"      - [{item['item_type']}] {item['label']}")

    return True


def test_collection_count():
    """Test de conteo de items en colecciones"""
    print("\n" + "="*60)
    print("TEST 6: CONTEO DE ITEMS EN COLECCIONES")
    print("="*60)

    db_path = root_dir / "widget_sidebar.db"
    manager = SmartCollectionsManager(str(db_path))

    # Obtener todas las colecciones con conteo
    collections = manager.get_all_collections_with_count()

    print(f"\n  Colecciones con número de items:")

    for collection in collections:
        print(f"\n  {collection['icon']} {collection['name']}")
        print(f"    Items que cumplen filtros: {collection['item_count']}")

        # Mostrar criterios de filtro
        if collection['tags_include']:
            print(f"    Tags incluir: {collection['tags_include']}")
        if collection['tags_exclude']:
            print(f"    Tags excluir: {collection['tags_exclude']}")
        if collection['item_type']:
            print(f"    Tipo: {collection['item_type']}")
        if collection['is_favorite'] is not None:
            print(f"    Favoritos: {collection['is_favorite']}")

    return True


def test_complex_filters():
    """Test de filtros complejos"""
    print("\n" + "="*60)
    print("TEST 7: FILTROS COMPLEJOS")
    print("="*60)

    db_path = root_dir / "widget_sidebar.db"
    manager = SmartCollectionsManager(str(db_path))

    # Crear colección con filtros múltiples
    print("\n  Creando colección con múltiples filtros...")

    collection_id = manager.create_collection(
        name="Test - Filtros Complejos",
        description="Colección con múltiples criterios de filtrado",
        icon="🔬",
        color="#ff6600",
        tags_include="python,api",
        tags_exclude="deprecated,old",
        item_type="CODE",
        is_favorite=True,
        is_active_filter=True,
        is_archived_filter=False
    )

    if collection_id:
        print(f"  ✓ Colección creada con ID: {collection_id}")

        # Ejecutar la colección
        items = manager.execute_collection(collection_id)
        print(f"\n  Items que cumplen TODOS los criterios: {len(items)}")

        # Mostrar criterios aplicados
        collection = manager.get_collection(collection_id)
        print(f"\n  Criterios aplicados:")
        print(f"    - Tags incluir: {collection['tags_include']}")
        print(f"    - Tags excluir: {collection['tags_exclude']}")
        print(f"    - Tipo: {collection['item_type']}")
        print(f"    - Favoritos: {collection['is_favorite']}")
        print(f"    - Activos: {collection['is_active_filter']}")
        print(f"    - No archivados: {not collection['is_archived_filter']}")

        # Limpiar (eliminar colección de prueba)
        manager.delete_collection(collection_id)
        print("\n  ✓ Colección de prueba eliminada")

        return True
    else:
        print("  ✗ Error al crear colección de filtros complejos")
        return False


def test_statistics():
    """Test de estadísticas generales"""
    print("\n" + "="*60)
    print("TEST 8: ESTADÍSTICAS GENERALES")
    print("="*60)

    db_path = root_dir / "widget_sidebar.db"
    manager = SmartCollectionsManager(str(db_path))

    stats = manager.get_statistics()

    print(f"\n  Estadísticas de Smart Collections:")
    print(f"    Total de colecciones: {stats['total_collections']}")
    print(f"    Colecciones activas: {stats['active_collections']}")
    print(f"    Colecciones inactivas: {stats['inactive_collections']}")

    return stats['total_collections'] >= 0


def test_soft_delete():
    """Test de soft delete (marcar como inactiva)"""
    print("\n" + "="*60)
    print("TEST 9: SOFT DELETE")
    print("="*60)

    db_path = root_dir / "widget_sidebar.db"
    manager = SmartCollectionsManager(str(db_path))

    # Buscar cualquier colección activa
    collections = manager.get_all_collections(active_only=True)

    if not collections:
        # Crear una nueva si no hay ninguna
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print("  ⚠ No hay colecciones activas. Creando una nueva...")
        try:
            collection_id = manager.create_collection(
                name=f"Test Collection for Delete {timestamp}",
                description="Colección de prueba para soft delete",
                tags_include="test"
            )
            collection = manager.get_collection(collection_id)
        except Exception as e:
            print(f"  ✗ Error al crear colección: {e}")
            return False
    else:
        collection = collections[0]

    if collection:
        print(f"\n  Colección: {collection['name']}")
        print(f"  Estado actual: {'Activa' if collection['is_active'] else 'Inactiva'}")

        # Hacer soft delete
        try:
            success = manager.soft_delete_collection(collection['id'])

            if success:
                print("  ✓ Soft delete exitoso")

                # Verificar que está inactiva
                updated_collection = manager.get_collection(collection['id'])
                print(f"  Estado después: {'Activa' if updated_collection['is_active'] else 'Inactiva'}")

                # Reactivar la colección
                manager.update_collection(collection['id'], is_active=True)
                print("  ✓ Colección reactivada")

                return True
            else:
                print("  ✗ Error en soft delete")
                return False
        except Exception as e:
            print(f"  ✗ Error en soft delete: {e}")
            return False
    else:
        print("  ✗ No se pudo encontrar o crear colección de prueba")
        return False


def test_filter_by_dates():
    """Test de filtros por fechas"""
    print("\n" + "="*60)
    print("TEST 10: FILTROS POR FECHAS")
    print("="*60)

    db_path = root_dir / "widget_sidebar.db"
    manager = SmartCollectionsManager(str(db_path))

    from datetime import datetime, timedelta

    # Crear colección con filtro de fechas (últimos 30 días)
    date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    date_to = datetime.now().strftime("%Y-%m-%d")

    collection_id = manager.create_collection(
        name="Test - Últimos 30 días",
        description="Items creados en los últimos 30 días",
        icon="📅",
        date_from=date_from,
        date_to=date_to
    )

    if collection_id:
        print(f"  ✓ Colección con filtro de fechas creada")
        print(f"    Desde: {date_from}")
        print(f"    Hasta: {date_to}")

        # Ejecutar la colección
        items = manager.execute_collection(collection_id)
        print(f"\n  Items encontrados: {len(items)}")

        # Limpiar
        manager.delete_collection(collection_id)
        print("  ✓ Colección de prueba eliminada")

        return True
    else:
        print("  ✗ Error al crear colección con filtro de fechas")
        return False


def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "="*70)
    print("  SMART COLLECTIONS MANAGER - SUITE DE TESTS")
    print("="*70)

    db_path = root_dir / "widget_sidebar.db"

    if not db_path.exists():
        print("\n  ❌ Database no encontrada en:", db_path)
        print("  Por favor ejecuta la aplicación primero para crear la base de datos")
        return

    print(f"\n  Database: {db_path}")
    print(f"  Path root: {root_dir}\n")

    # Ejecutar todos los tests
    results = []

    try:
        results.append(("Crear Smart Collection", test_create_collection() is not None))
        results.append(("Leer Smart Collections", test_read_collections()))
        results.append(("Buscar Smart Collections", test_search_collections()))
        results.append(("Actualizar Smart Collection", test_update_collection()))
        results.append(("Ejecutar Colección", test_execute_collection()))
        results.append(("Conteo de items", test_collection_count()))
        results.append(("Filtros complejos", test_complex_filters()))
        results.append(("Estadísticas", test_statistics()))
        results.append(("Soft delete", test_soft_delete()))
        results.append(("Filtros por fechas", test_filter_by_dates()))
    except Exception as e:
        print(f"\n  ❌ Error durante los tests: {e}")
        import traceback
        traceback.print_exc()

    # Resumen final
    print("\n" + "="*70)
    print("  RESUMEN DE TESTS")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓" if result else "✗"
        print(f"  {status} {test_name}")

    print(f"\n  Tests pasados: {passed}/{total}")

    if passed == total:
        print("\n  🎉 ¡Todos los tests pasaron exitosamente!")
    else:
        print(f"\n  ⚠️  {total - passed} test(s) fallaron")


if __name__ == "__main__":
    run_all_tests()

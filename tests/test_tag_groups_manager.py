"""
Script de testing para TagGroupsManager
Prueba las operaciones CRUD de Tag Groups
"""

import sys
from pathlib import Path
import logging

# Agregar src al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / 'src'))

from core.tag_groups_manager import TagGroupsManager
from database.db_manager import DBManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def test_create_group():
    """Test de creación de Tag Group"""
    print("\n" + "="*60)
    print("TEST 1: CREAR TAG GROUP")
    print("="*60)

    db_path = root_dir / "widget_sidebar.db"
    manager = TagGroupsManager(str(db_path))

    # Usar timestamp para nombre único
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_name = f"Test Group Python Dev {timestamp}"

    # Crear un nuevo grupo
    try:
        group_id = manager.create_group(
            name=test_name,
            tags="python,pytest,unittest,testing,mock",
            description="Grupo de prueba para desarrollo Python",
            color="#3776ab",
            icon="🧪"
        )

        if group_id:
            print(f"  ✓ Tag Group creado exitosamente con ID: {group_id}")

            # Verificar que se creó correctamente
            group = manager.get_group(group_id)
            if group:
                print(f"\n  Detalles del grupo creado:")
                print(f"    - Nombre: {group['name']}")
                print(f"    - Tags: {group['tags']}")
                print(f"    - Descripción: {group['description']}")
                print(f"    - Color: {group['color']}")
                print(f"    - Icono: {group['icon']}")
                print(f"    - Activo: {group['is_active']}")

            return group_id
        else:
            print("  ✗ Error al crear Tag Group")
            return None
    except Exception as e:
        print(f"  ✗ Error al crear Tag Group: {e}")
        return None


def test_read_groups():
    """Test de lectura de Tag Groups"""
    print("\n" + "="*60)
    print("TEST 2: LEER TAG GROUPS")
    print("="*60)

    db_path = root_dir / "widget_sidebar.db"
    manager = TagGroupsManager(str(db_path))

    # Obtener todos los grupos
    groups = manager.get_all_groups()
    print(f"\n  Total de grupos: {len(groups)}")

    if groups:
        print("\n  Grupos existentes:")
        for group in groups[:5]:  # Mostrar solo los primeros 5
            print(f"    {group['id']}. {group['icon']} {group['name']}")
            print(f"       Tags: {group['tags']}")
            print(f"       Activo: {group['is_active']}")

    # Obtener solo grupos activos
    active_groups = manager.get_all_groups(active_only=True)
    print(f"\n  Grupos activos: {len(active_groups)}")

    return len(groups) > 0


def test_search_groups():
    """Test de búsqueda de Tag Groups"""
    print("\n" + "="*60)
    print("TEST 3: BUSCAR TAG GROUPS")
    print("="*60)

    db_path = root_dir / "widget_sidebar.db"
    manager = TagGroupsManager(str(db_path))

    # Buscar grupos con "python"
    search_term = "python"
    results = manager.search_groups(search_term)

    print(f"\n  Búsqueda: '{search_term}'")
    print(f"  Resultados encontrados: {len(results)}")

    if results:
        print("\n  Grupos encontrados:")
        for group in results:
            print(f"    - {group['name']}: {group['tags']}")

    return len(results) > 0


def test_update_group():
    """Test de actualización de Tag Group"""
    print("\n" + "="*60)
    print("TEST 4: ACTUALIZAR TAG GROUP")
    print("="*60)

    db_path = root_dir / "widget_sidebar.db"
    manager = TagGroupsManager(str(db_path))

    # Buscar cualquier grupo existente o crear uno nuevo
    groups = manager.get_all_groups()

    if groups:
        # Usar el primer grupo existente
        group = groups[0]
        print(f"  ℹ Usando grupo existente: {group['name']}")
    else:
        # Crear uno nuevo con timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print("  ⚠ No hay grupos. Creando uno nuevo...")
        try:
            group_id = manager.create_group(
                name=f"Test Group for Update {timestamp}",
                tags="python,pytest,unittest",
                description="Grupo de prueba"
            )
            group = manager.get_group(group_id)
        except Exception as e:
            print(f"  ✗ Error al crear grupo: {e}")
            return False

    if group:
        print(f"\n  Grupo a actualizar: {group['name']}")
        print(f"  Tags originales: {group['tags']}")

        # Actualizar el grupo
        try:
            success = manager.update_group(
                group['id'],
                tags="python,pytest,unittest,mock,fixtures,coverage",
                description="Grupo actualizado con más tags"
            )

            if success:
                print("  ✓ Tag Group actualizado exitosamente")

                # Verificar cambios
                updated_group = manager.get_group(group['id'])
                print(f"\n  Tags actualizados: {updated_group['tags']}")
                print(f"  Descripción actualizada: {updated_group['description']}")

                return True
            else:
                print("  ✗ Error al actualizar Tag Group")
                return False
        except Exception as e:
            print(f"  ✗ Error al actualizar Tag Group: {e}")
            return False
    else:
        print("  ✗ No se pudo encontrar o crear el grupo de prueba")
        return False


def test_get_tags_as_list():
    """Test de obtención de tags como lista"""
    print("\n" + "="*60)
    print("TEST 5: OBTENER TAGS COMO LISTA")
    print("="*60)

    db_path = root_dir / "widget_sidebar.db"
    manager = TagGroupsManager(str(db_path))

    # Obtener todos los grupos
    groups = manager.get_all_groups()

    if groups:
        first_group = groups[0]
        print(f"\n  Grupo: {first_group['name']}")
        print(f"  Tags string: {first_group['tags']}")

        # Obtener tags como lista
        tags_list = manager.get_tags_as_list(first_group['id'])
        print(f"\n  Tags como lista: {tags_list}")
        print(f"  Número de tags: {len(tags_list)}")

        return len(tags_list) > 0
    else:
        print("  ⚠ No hay grupos para probar")
        return False


def test_usage_count():
    """Test de conteo de uso de Tag Groups"""
    print("\n" + "="*60)
    print("TEST 6: CONTEO DE USO")
    print("="*60)

    db_path = root_dir / "widget_sidebar.db"
    manager = TagGroupsManager(str(db_path))

    # Obtener todos los grupos con estadísticas de uso
    groups = manager.get_all_groups_with_usage()

    print(f"\n  Grupos con estadísticas de uso:")

    for group in groups[:5]:  # Mostrar solo los primeros 5
        print(f"\n  {group['icon']} {group['name']}")
        print(f"    Tags: {group['tags']}")
        print(f"    Items que usan estos tags: {group['usage_count']}")

    return True


def test_statistics():
    """Test de estadísticas generales"""
    print("\n" + "="*60)
    print("TEST 7: ESTADÍSTICAS GENERALES")
    print("="*60)

    db_path = root_dir / "widget_sidebar.db"
    manager = TagGroupsManager(str(db_path))

    stats = manager.get_statistics()

    print(f"\n  Estadísticas de Tag Groups:")
    print(f"    Total de grupos: {stats['total_groups']}")
    print(f"    Grupos activos: {stats['active_groups']}")
    print(f"    Grupos inactivos: {stats['inactive_groups']}")
    print(f"    Tags únicos totales: {stats['unique_tags']}")

    if stats['all_tags']:
        print(f"\n  Primeros 10 tags únicos:")
        for tag in stats['all_tags'][:10]:
            print(f"    - {tag}")

    return stats['total_groups'] > 0


def test_validate_tags():
    """Test de validación de tags"""
    print("\n" + "="*60)
    print("TEST 8: VALIDACIÓN DE TAGS")
    print("="*60)

    db_path = root_dir / "widget_sidebar.db"
    manager = TagGroupsManager(str(db_path))

    # Test casos válidos
    test_cases = [
        ("python,fastapi,api", True),
        ("", False),
        ("python, python", False),  # Duplicados
        ("a"*51, False),  # Tag muy largo
        ("valid,tags,here", True),
    ]

    print("\n  Casos de prueba:")
    for tags, expected_valid in test_cases:
        is_valid, message = manager.validate_tags(tags)
        status = "✓" if (is_valid == expected_valid) else "✗"
        print(f"    {status} '{tags[:30]}...' → {message}")

    return True


def test_soft_delete():
    """Test de soft delete (marcar como inactivo)"""
    print("\n" + "="*60)
    print("TEST 9: SOFT DELETE")
    print("="*60)

    db_path = root_dir / "widget_sidebar.db"
    manager = TagGroupsManager(str(db_path))

    # Buscar cualquier grupo activo
    groups = manager.get_all_groups(active_only=True)

    if not groups:
        # Crear uno nuevo si no hay ninguno
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print("  ⚠ No hay grupos activos. Creando uno nuevo...")
        try:
            group_id = manager.create_group(
                name=f"Test Group for Delete {timestamp}",
                tags="test,delete",
                description="Grupo de prueba para soft delete"
            )
            group = manager.get_group(group_id)
        except Exception as e:
            print(f"  ✗ Error al crear grupo: {e}")
            return False
    else:
        group = groups[0]

    if group:
        print(f"\n  Grupo: {group['name']}")
        print(f"  Estado actual: {'Activo' if group['is_active'] else 'Inactivo'}")

        # Hacer soft delete
        try:
            success = manager.soft_delete_group(group['id'])

            if success:
                print("  ✓ Soft delete exitoso")

                # Verificar que está inactivo
                updated_group = manager.get_group(group['id'])
                print(f"  Estado después: {'Activo' if updated_group['is_active'] else 'Inactivo'}")

                # Reactivar el grupo
                manager.update_group(group['id'], is_active=True)
                print("  ✓ Grupo reactivado")

                return True
            else:
                print("  ✗ Error en soft delete")
                return False
        except Exception as e:
            print(f"  ✗ Error en soft delete: {e}")
            return False
    else:
        print("  ✗ No se pudo encontrar o crear grupo de prueba")
        return False


def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "="*70)
    print("  TAG GROUPS MANAGER - SUITE DE TESTS")
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
        results.append(("Crear Tag Group", test_create_group() is not None))
        results.append(("Leer Tag Groups", test_read_groups()))
        results.append(("Buscar Tag Groups", test_search_groups()))
        results.append(("Actualizar Tag Group", test_update_group()))
        results.append(("Tags como lista", test_get_tags_as_list()))
        results.append(("Conteo de uso", test_usage_count()))
        results.append(("Estadísticas", test_statistics()))
        results.append(("Validación de tags", test_validate_tags()))
        results.append(("Soft delete", test_soft_delete()))
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

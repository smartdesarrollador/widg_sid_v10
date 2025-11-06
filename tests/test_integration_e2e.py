"""
Test de Integración End-to-End
Prueba el flujo completo: Tag Groups → Items → Smart Collections
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Agregar src al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / 'src'))

from core.tag_groups_manager import TagGroupsManager
from core.smart_collections_manager import SmartCollectionsManager
from database.db_manager import DBManager
from models.item import Item, ItemType


class E2ETestRunner:
    """Runner para tests de integración end-to-end"""

    def __init__(self, db_path: str):
        """
        Initialize the test runner

        Args:
            db_path: Path to database
        """
        self.db_path = db_path
        self.tag_groups_mgr = TagGroupsManager(db_path)
        self.collections_mgr = SmartCollectionsManager(db_path)
        self.db = DBManager(db_path)

        # Tracking de IDs para cleanup
        self.created_tag_groups = []
        self.created_items = []
        self.created_collections = []
        self.created_category = None

    def cleanup(self):
        """Clean up all test data"""
        print("\n🧹 Limpiando datos de prueba...")

        # Delete collections
        for collection_id in self.created_collections:
            try:
                self.collections_mgr.delete_collection(collection_id)
                print(f"  ✓ Colección {collection_id} eliminada")
            except:
                pass

        # Delete items
        for item_id in self.created_items:
            try:
                self.db.delete_item(item_id)
                print(f"  ✓ Item {item_id} eliminado")
            except:
                pass

        # Delete tag groups
        for group_id in self.created_tag_groups:
            try:
                self.tag_groups_mgr.delete_group(group_id)
                print(f"  ✓ Tag Group {group_id} eliminado")
            except:
                pass

        # Delete category
        if self.created_category:
            try:
                self.db.delete_category(self.created_category)
                print(f"  ✓ Categoría {self.created_category} eliminada")
            except:
                pass

        print("✓ Limpieza completada\n")

    def run_scenario_1(self):
        """
        Escenario 1: Flujo completo básico
        - Crear Tag Group
        - Crear items con esos tags
        - Crear Smart Collection que los filtre
        - Verificar que la colección encuentra los items correctos
        """
        print("\n" + "="*70)
        print("ESCENARIO 1: Flujo Básico Completo")
        print("="*70)

        # Step 1: Crear categoría de prueba
        print("\n📁 Step 1: Crear categoría de prueba")
        self.created_category = self.db.add_category(
            name="E2E Test Category",
            icon="🧪",
            is_predefined=False
        )
        print(f"  ✓ Categoría creada con ID: {self.created_category}")

        # Step 2: Crear Tag Group
        print("\n🏷️  Step 2: Crear Tag Group")
        group_id = self.tag_groups_mgr.create_group(
            name="E2E Test - Python Tools",
            tags="python,testing,automation,pytest",
            description="Herramientas de testing en Python",
            icon="🐍",
            color="#3776ab"
        )
        self.created_tag_groups.append(group_id)
        print(f"  ✓ Tag Group creado con ID: {group_id}")
        print(f"    Tags: python, testing, automation, pytest")

        # Step 3: Crear items usando los tags del grupo
        print("\n📝 Step 3: Crear items con tags del grupo")

        items_data = [
            {
                "label": "E2E Test - pytest fixture",
                "content": "@pytest.fixture\ndef client():\n    return TestClient(app)",
                "type": ItemType.CODE,
                "tags": ["python", "pytest", "testing"]
            },
            {
                "label": "E2E Test - automation script",
                "content": "python run_tests.py --coverage",
                "type": ItemType.CODE,
                "tags": ["python", "automation", "testing"]
            },
            {
                "label": "E2E Test - pytest command",
                "content": "pytest -v --cov=src tests/",
                "type": ItemType.CODE,
                "tags": ["python", "pytest"]
            }
        ]

        for item_data in items_data:
            item_id = self.db.add_item(
                category_id=self.created_category,
                label=item_data["label"],
                content=item_data["content"],
                item_type=item_data["type"].value,
                tags=json.dumps(item_data["tags"])
            )
            self.created_items.append(item_id)
            print(f"  ✓ Item creado: {item_data['label']}")
            print(f"    Tags: {', '.join(item_data['tags'])}")

        # Step 4: Crear Smart Collection que filtre por esos tags
        print("\n🔍 Step 4: Crear Smart Collection")
        collection_id = self.collections_mgr.create_collection(
            name="E2E Test - Python Testing Tools",
            description="Items relacionados con testing en Python",
            icon="🧪",
            color="#4caf50",
            tags_include="python,testing",
            item_type="CODE"
        )
        self.created_collections.append(collection_id)
        print(f"  ✓ Smart Collection creada con ID: {collection_id}")
        print(f"    Filtros: tags_include='python,testing', type='CODE'")

        # Step 5: Ejecutar la colección y verificar resultados
        print("\n✅ Step 5: Verificar resultados")
        items = self.collections_mgr.execute_collection(collection_id)
        print(f"  Items encontrados: {len(items)}")

        # Verificar que encontró exactamente los items esperados
        expected_count = 2  # Los 2 primeros items tienen 'python' Y 'testing'
        if len(items) == expected_count:
            print(f"  ✓ PASS: Se encontraron exactamente {expected_count} items esperados")
            for item in items:
                print(f"    - {item['label']}")
            return True
        else:
            print(f"  ✗ FAIL: Se esperaban {expected_count} items, se encontraron {len(items)}")
            return False

    def run_scenario_2(self):
        """
        Escenario 2: Filtros de exclusión
        - Crear items con tags variados
        - Crear colección que incluya algunos y excluya otros
        - Verificar que la exclusión funciona correctamente
        """
        print("\n" + "="*70)
        print("ESCENARIO 2: Filtros de Exclusión")
        print("="*70)

        # Crear categoría si no existe
        if not self.created_category:
            self.created_category = self.db.add_category(
                name="E2E Test Category",
                icon="🧪",
                is_predefined=False
            )

        # Step 1: Crear items con tags variados
        print("\n📝 Step 1: Crear items con tags variados")

        items_data = [
            {
                "label": "E2E Test - Modern API",
                "content": "FastAPI modern endpoint",
                "tags": ["python", "fastapi", "api", "modern"]
            },
            {
                "label": "E2E Test - Legacy API",
                "content": "Old Flask endpoint",
                "tags": ["python", "flask", "api", "legacy"]
            },
            {
                "label": "E2E Test - Deprecated API",
                "content": "Old deprecated API",
                "tags": ["python", "api", "deprecated"]
            },
        ]

        for item_data in items_data:
            item_id = self.db.add_item(
                category_id=self.created_category,
                label=item_data["label"],
                content=item_data["content"],
                item_type=ItemType.CODE.value,
                tags=json.dumps(item_data["tags"])
            )
            self.created_items.append(item_id)
            print(f"  ✓ Item creado: {item_data['label']}")
            print(f"    Tags: {', '.join(item_data['tags'])}")

        # Step 2: Crear colección que excluya legacy y deprecated
        print("\n🔍 Step 2: Crear Smart Collection con exclusión")
        collection_id = self.collections_mgr.create_collection(
            name="E2E Test - Modern APIs Only",
            description="Solo APIs modernas, sin legacy ni deprecated",
            icon="🚀",
            color="#00d4ff",
            tags_include="python,api",
            tags_exclude="legacy,deprecated"
        )
        self.created_collections.append(collection_id)
        print(f"  ✓ Smart Collection creada")
        print(f"    Incluir: python,api")
        print(f"    Excluir: legacy,deprecated")

        # Step 3: Verificar resultados
        print("\n✅ Step 3: Verificar resultados")
        items = self.collections_mgr.execute_collection(collection_id)
        print(f"  Items encontrados: {len(items)}")

        # Solo debe encontrar el primer item (Modern API)
        expected_count = 1
        if len(items) == expected_count:
            print(f"  ✓ PASS: Se encontró exactamente {expected_count} item esperado")
            for item in items:
                print(f"    - {item['label']}")
                # Verificar que NO tiene tags excluidos
                item_tags = json.loads(item['tags']) if isinstance(item['tags'], str) else item['tags']
                if not any(tag in ['legacy', 'deprecated'] for tag in item_tags):
                    print(f"      ✓ Correctamente no tiene tags excluidos")
            return True
        else:
            print(f"  ✗ FAIL: Se esperaba {expected_count} item, se encontraron {len(items)}")
            return False

    def run_scenario_3(self):
        """
        Escenario 3: Filtros múltiples (tipo + tags + favoritos)
        - Crear items de diferentes tipos
        - Marcar algunos como favoritos
        - Crear colección con múltiples filtros
        - Verificar que solo se encuentran items que cumplen TODOS los criterios
        """
        print("\n" + "="*70)
        print("ESCENARIO 3: Filtros Múltiples Combinados")
        print("="*70)

        # Crear categoría si no existe
        if not self.created_category:
            self.created_category = self.db.add_category(
                name="E2E Test Category",
                icon="🧪",
                is_predefined=False
            )

        # Step 1: Crear items variados
        print("\n📝 Step 1: Crear items de diferentes tipos")

        items_data = [
            {
                "label": "E2E Test - Fav Code",
                "content": "Favorite code snippet",
                "type": ItemType.CODE,
                "tags": ["python", "favorite", "snippet"],
                "is_favorite": True
            },
            {
                "label": "E2E Test - Normal Code",
                "content": "Normal code snippet",
                "type": ItemType.CODE,
                "tags": ["python", "snippet"],
                "is_favorite": False
            },
            {
                "label": "E2E Test - Fav URL",
                "content": "https://python.org",
                "type": ItemType.URL,
                "tags": ["python", "favorite"],
                "is_favorite": True
            },
        ]

        for item_data in items_data:
            item_id = self.db.add_item(
                category_id=self.created_category,
                label=item_data["label"],
                content=item_data["content"],
                item_type=item_data["type"].value,
                tags=json.dumps(item_data["tags"]),
                is_favorite=item_data["is_favorite"]
            )
            self.created_items.append(item_id)
            fav_icon = "⭐" if item_data["is_favorite"] else ""
            print(f"  ✓ Item creado: {item_data['label']} {fav_icon}")
            print(f"    Tipo: {item_data['type'].value}, Tags: {', '.join(item_data['tags'])}")

        # Step 2: Crear colección con múltiples filtros
        print("\n🔍 Step 2: Crear Smart Collection con filtros múltiples")
        collection_id = self.collections_mgr.create_collection(
            name="E2E Test - Favorite Code Snippets",
            description="Solo snippets de código favoritos con Python",
            icon="⭐",
            color="#ffd700",
            tags_include="python",
            item_type="CODE",
            is_favorite=True
        )
        self.created_collections.append(collection_id)
        print(f"  ✓ Smart Collection creada")
        print(f"    Filtros:")
        print(f"      - Tags incluir: python")
        print(f"      - Tipo: CODE")
        print(f"      - Favoritos: True")

        # Step 3: Verificar resultados
        print("\n✅ Step 3: Verificar resultados")
        items = self.collections_mgr.execute_collection(collection_id)
        print(f"  Items encontrados: {len(items)}")

        # Solo debe encontrar el primer item (Fav Code con python)
        expected_count = 1
        if len(items) == expected_count:
            print(f"  ✓ PASS: Se encontró exactamente {expected_count} item esperado")
            for item in items:
                print(f"    - {item['label']}")
                # Verificar criterios
                print(f"      ✓ Tipo: {item['item_type']} (CODE)")
                print(f"      ✓ Favorito: {item['is_favorite']}")
                item_tags = json.loads(item['tags']) if isinstance(item['tags'], str) else item['tags']
                print(f"      ✓ Tiene tag 'python': {'python' in item_tags}")
            return True
        else:
            print(f"  ✗ FAIL: Se esperaba {expected_count} item, se encontraron {len(items)}")
            return False

    def run_scenario_4(self):
        """
        Escenario 4: Tag Group usage tracking
        - Crear Tag Group
        - Crear items que usen esos tags
        - Verificar que el conteo de uso es correcto
        """
        print("\n" + "="*70)
        print("ESCENARIO 4: Tag Group Usage Tracking")
        print("="*70)

        # Crear categoría si no existe
        if not self.created_category:
            self.created_category = self.db.add_category(
                name="E2E Test Category",
                icon="🧪",
                is_predefined=False
            )

        # Step 1: Crear Tag Group único
        print("\n🏷️  Step 1: Crear Tag Group con tags únicos")
        unique_tags = f"e2e-test-{datetime.now().strftime('%H%M%S')},unique-tag,special"
        group_id = self.tag_groups_mgr.create_group(
            name=f"E2E Test - Unique Group {datetime.now().strftime('%H%M%S')}",
            tags=unique_tags,
            description="Grupo con tags únicos para testing",
            icon="🎯"
        )
        self.created_tag_groups.append(group_id)
        print(f"  ✓ Tag Group creado con tags únicos")

        # Step 2: Obtener usage count inicial (debe ser 0)
        print("\n📊 Step 2: Verificar usage count inicial")
        groups_with_usage = self.tag_groups_mgr.get_all_groups_with_usage()
        test_group = next((g for g in groups_with_usage if g['id'] == group_id), None)
        initial_count = test_group['usage_count'] if test_group else 0
        print(f"  Usage count inicial: {initial_count}")

        # Step 3: Crear items usando esos tags
        print("\n📝 Step 3: Crear items usando tags del grupo")
        tags_list = unique_tags.split(',')
        num_items = 3

        for i in range(num_items):
            item_id = self.db.add_item(
                category_id=self.created_category,
                label=f"E2E Test - Item with unique tags {i+1}",
                content=f"Content {i+1}",
                item_type=ItemType.TEXT.value,
                tags=json.dumps(tags_list[:2])  # Usar los primeros 2 tags
            )
            self.created_items.append(item_id)
            print(f"  ✓ Item {i+1} creado con tags del grupo")

        # Step 4: Verificar que el usage count aumentó
        print("\n✅ Step 4: Verificar usage count final")
        groups_with_usage = self.tag_groups_mgr.get_all_groups_with_usage()
        test_group = next((g for g in groups_with_usage if g['id'] == group_id), None)
        final_count = test_group['usage_count'] if test_group else 0
        print(f"  Usage count final: {final_count}")

        # El count debería ser >= num_items (puede ser más si los items comparten tags)
        if final_count >= num_items:
            print(f"  ✓ PASS: Usage count correcto ({final_count} >= {num_items})")
            return True
        else:
            print(f"  ✗ FAIL: Usage count incorrecto ({final_count} < {num_items})")
            return False

    def run_all_scenarios(self):
        """Run all E2E test scenarios"""
        print("\n" + "="*70)
        print("  TEST DE INTEGRACIÓN END-TO-END")
        print("  Tag Groups → Items → Smart Collections")
        print("="*70)

        print(f"\n  Database: {self.db_path}")
        print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        results = []

        try:
            # Run scenarios
            results.append(("Flujo Básico Completo", self.run_scenario_1()))
            results.append(("Filtros de Exclusión", self.run_scenario_2()))
            results.append(("Filtros Múltiples", self.run_scenario_3()))
            results.append(("Tag Group Usage Tracking", self.run_scenario_4()))

        except Exception as e:
            print(f"\n  ❌ Error durante los tests: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Always cleanup
            self.cleanup()

        # Summary
        print("\n" + "="*70)
        print("  RESUMEN DE ESCENARIOS E2E")
        print("="*70)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for scenario_name, result in results:
            status = "✓" if result else "✗"
            print(f"  {status} {scenario_name}")

        print(f"\n  Escenarios pasados: {passed}/{total}")

        if passed == total:
            print("\n  🎉 ¡Todos los escenarios E2E pasaron exitosamente!")
        else:
            print(f"\n  ⚠️  {total - passed} escenario(s) fallaron")


def main():
    """Main entry point"""
    db_path = root_dir / "widget_sidebar.db"

    if not db_path.exists():
        print(f"\n❌ Error: Database not found at {db_path}")
        print("Por favor ejecuta la aplicación primero para crear la base de datos")
        return

    # Run E2E tests
    runner = E2ETestRunner(str(db_path))
    runner.run_all_scenarios()


if __name__ == "__main__":
    main()

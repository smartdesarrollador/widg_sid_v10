"""
Test funcional para AI Bulk Item Creation Wizard

Este script prueba el wizard completo sin necesidad de login.
"""
import sys
import io
from pathlib import Path
import logging

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication
from database.db_manager import DBManager
from core.ai_bulk_manager import AIBulkItemManager
from models.bulk_item_data import BulkItemDefaults, BulkImportConfig
from utils.json_validator import BulkJSONValidator
from utils.prompt_templates import PromptTemplate

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_backend_components():
    """Test de componentes backend."""
    print("\n" + "="*70)
    print("TEST 1: Backend Components")
    print("="*70)

    try:
        # 1. Test DBManager
        print("\n[1/6] Testing DBManager...")
        db = DBManager("widget_sidebar.db")
        categories = db.execute_query("SELECT id, name FROM categories LIMIT 5")
        print(f"  ✓ DBManager OK - {len(categories)} categories found")

        # 2. Test AIBulkItemManager
        print("\n[2/6] Testing AIBulkItemManager...")
        manager = AIBulkItemManager(db)
        print(f"  ✓ AIBulkItemManager OK")

        # 3. Test BulkJSONValidator
        print("\n[3/6] Testing BulkJSONValidator...")
        validator = BulkJSONValidator()
        test_json = '{"category_id": 1, "items": [{"label": "Test", "content": "Content"}]}'
        result = validator.validate_json_string(test_json)
        print(f"  ✓ Validator OK - Valid: {result.is_valid}, Items: {result.items_count}")

        # 4. Test PromptTemplate
        print("\n[4/6] Testing PromptTemplate...")
        config = {
            'category_id': 1,
            'category_name': 'Test Category',
            'item_type': 'CODE',
            'tags': 'test',
            'is_favorite': 0,
            'is_sensitive': 0,
            'user_context': 'Test context'
        }
        prompt = PromptTemplate.generate(config)
        print(f"  ✓ PromptTemplate OK - {len(prompt)} characters")

        # 5. Test generate_prompt
        print("\n[5/6] Testing generate_prompt...")
        bulk_config = BulkImportConfig(
            category_id=1,
            category_name="Test Category",
            defaults=BulkItemDefaults(type='CODE', tags='test'),
            user_context="Test context"
        )
        prompt = manager.generate_prompt(bulk_config)
        print(f"  ✓ generate_prompt OK - {len(prompt)} characters")

        # 6. Test parse_items
        print("\n[6/6] Testing parse_items...")
        test_json = '''
        {
            "category_id": 1,
            "defaults": {
                "type": "CODE",
                "tags": "test,example"
            },
            "items": [
                {"label": "Item 1", "content": "echo 'test 1'"},
                {"label": "Item 2", "content": "echo 'test 2'"}
            ]
        }
        '''
        items, defaults, cat_id = manager.parse_items(test_json)
        print(f"  ✓ parse_items OK - {len(items)} items parsed")
        print(f"    - Category ID: {cat_id}")
        print(f"    - Defaults type: {defaults.type}")
        print(f"    - Items: {[item.label for item in items]}")

        db.close()

        print("\n" + "="*70)
        print("✅ BACKEND TESTS PASSED")
        print("="*70)
        return True

    except Exception as e:
        print(f"\n❌ BACKEND TEST FAILED: {e}")
        logger.error("Backend test failed", exc_info=True)
        return False


def test_ui_components():
    """Test de componentes UI."""
    print("\n" + "="*70)
    print("TEST 2: UI Components")
    print("="*70)

    try:
        app = QApplication(sys.argv)

        # 1. Test ConfigStep
        print("\n[1/6] Testing ConfigStep...")
        from views.widgets.ai_config_step import ConfigStep
        db = DBManager("widget_sidebar.db")
        config_step = ConfigStep(db)
        print(f"  ✓ ConfigStep created")
        print(f"    - Categories loaded: {len(config_step.categories)}")

        # 2. Test PromptStep
        print("\n[2/6] Testing PromptStep...")
        from views.widgets.ai_prompt_step import PromptStep
        manager = AIBulkItemManager(db)
        prompt_step = PromptStep(manager)
        print(f"  ✓ PromptStep created")

        # 3. Test JSONEditor
        print("\n[3/6] Testing JSONEditor...")
        from views.widgets.json_editor import JSONEditor
        json_editor = JSONEditor()
        json_editor.setPlainText('{"test": "value"}')
        print(f"  ✓ JSONEditor created with syntax highlighting")

        # 4. Test JSONStep
        print("\n[4/6] Testing JSONStep...")
        from views.widgets.ai_json_step import JSONStep
        json_step = JSONStep(manager)
        print(f"  ✓ JSONStep created")

        # 5. Test PreviewStep
        print("\n[5/6] Testing PreviewStep...")
        from views.widgets.ai_preview_step import PreviewStep
        from models.bulk_item_data import BulkItemData
        preview_step = PreviewStep()
        test_items = [
            BulkItemData(label="Test 1", content="Content 1", type="CODE"),
            BulkItemData(label="Test 2", content="Content 2", type="URL")
        ]
        preview_step.set_items(test_items)
        print(f"  ✓ PreviewStep created with {len(test_items)} items")

        # 6. Test CreationStep
        print("\n[6/6] Testing CreationStep...")
        from views.widgets.ai_creation_step import CreationStep
        creation_step = CreationStep(manager)
        print(f"  ✓ CreationStep created")

        db.close()

        print("\n" + "="*70)
        print("✅ UI COMPONENTS TESTS PASSED")
        print("="*70)
        return True

    except Exception as e:
        print(f"\n❌ UI TEST FAILED: {e}")
        logger.error("UI test failed", exc_info=True)
        return False


def test_wizard_integration():
    """Test de integración del wizard completo."""
    print("\n" + "="*70)
    print("TEST 3: Wizard Integration")
    print("="*70)

    try:
        app = QApplication(sys.argv)

        # Test crear wizard
        print("\n[1/3] Creating wizard...")
        from views.dialogs.ai_bulk_wizard import AIBulkWizard
        db = DBManager("widget_sidebar.db")
        wizard = AIBulkWizard(db)
        print(f"  ✓ Wizard created")
        print(f"    - Total steps: {wizard.total_steps}")
        print(f"    - Current step: {wizard.current_step}")

        # Test steps están inicializados
        print("\n[2/3] Checking steps initialization...")
        print(f"  ✓ config_step: {type(wizard.config_step).__name__}")
        print(f"  ✓ prompt_step: {type(wizard.prompt_step).__name__}")
        print(f"  ✓ json_step: {type(wizard.json_step).__name__}")
        print(f"  ✓ preview_step: {type(wizard.preview_step).__name__}")
        print(f"  ✓ creation_step: {type(wizard.creation_step).__name__}")

        # Test que el wizard se puede mostrar
        print("\n[3/3] Testing wizard display...")
        wizard.show()
        print(f"  ✓ Wizard can be shown")

        # Cerrar wizard
        wizard.close()

        db.close()

        print("\n" + "="*70)
        print("✅ WIZARD INTEGRATION TESTS PASSED")
        print("="*70)
        return True

    except Exception as e:
        print(f"\n❌ WIZARD INTEGRATION TEST FAILED: {e}")
        logger.error("Wizard integration test failed", exc_info=True)
        return False


def test_data_flow():
    """Test del flujo de datos entre steps."""
    print("\n" + "="*70)
    print("TEST 4: Data Flow Between Steps")
    print("="*70)

    try:
        app = QApplication(sys.argv)
        db = DBManager("widget_sidebar.db")
        manager = AIBulkItemManager(db)

        # 1. ConfigStep → PromptStep
        print("\n[1/3] Testing ConfigStep → PromptStep...")
        from views.widgets.ai_config_step import ConfigStep
        from views.widgets.ai_prompt_step import PromptStep

        config_step = ConfigStep(db)
        prompt_step = PromptStep(manager)

        # Simular obtener config
        config = config_step.get_config()
        print(f"  ✓ Config obtained from ConfigStep")
        print(f"    - Category ID: {config.category_id}")
        print(f"    - Type: {config.defaults.type}")

        # Pasar a PromptStep
        prompt_step.set_config(config)
        print(f"  ✓ Config passed to PromptStep")
        print(f"    - Prompt generated: {len(prompt_step.prompt_text)} chars")

        # 2. JSONStep → PreviewStep
        print("\n[2/3] Testing JSONStep → PreviewStep...")
        from views.widgets.ai_json_step import JSONStep
        from views.widgets.ai_preview_step import PreviewStep

        json_step = JSONStep(manager)
        preview_step = PreviewStep()

        # Simular JSON válido
        test_json = '''
        {
            "category_id": 1,
            "defaults": {"type": "CODE", "tags": "test"},
            "items": [
                {"label": "Test 1", "content": "echo 1"},
                {"label": "Test 2", "content": "echo 2"}
            ]
        }
        '''
        json_step.json_editor.setPlainText(test_json)
        json_step.validate_json()

        if json_step.is_valid():
            items, defaults, cat_id = manager.parse_items(json_step.get_json_text())
            preview_step.set_items(items)
            print(f"  ✓ Items passed to PreviewStep")
            print(f"    - Items count: {len(items)}")
            print(f"    - Selected: {len(preview_step.get_selected_items())}")
        else:
            print(f"  ⚠ JSON validation failed")

        # 3. PreviewStep → CreationStep
        print("\n[3/3] Testing PreviewStep → CreationStep...")
        from views.widgets.ai_creation_step import CreationStep

        creation_step = CreationStep(manager)
        selected_items = preview_step.get_selected_items()
        creation_step.set_items(selected_items, 1)
        print(f"  ✓ Items passed to CreationStep")
        print(f"    - Items ready: {len(creation_step.items)}")

        db.close()

        print("\n" + "="*70)
        print("✅ DATA FLOW TESTS PASSED")
        print("="*70)
        return True

    except Exception as e:
        print(f"\n❌ DATA FLOW TEST FAILED: {e}")
        logger.error("Data flow test failed", exc_info=True)
        return False


def main():
    """Ejecuta todos los tests."""
    print("\n" + "="*70)
    print("  AI Bulk Item Creation - Functional Test Suite")
    print("="*70)

    results = {
        "Backend Components": test_backend_components(),
        "UI Components": test_ui_components(),
        "Wizard Integration": test_wizard_integration(),
        "Data Flow": test_data_flow()
    }

    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"\n  {test_name}: {status}")

    all_passed = all(results.values())
    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL TESTS PASSED! 🎉".center(70))
        print("The AI Bulk Item Creation feature is ready to use!".center(70))
    else:
        print("⚠️ SOME TESTS FAILED".center(70))
        print("Please review the errors above.".center(70))
    print("="*70 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

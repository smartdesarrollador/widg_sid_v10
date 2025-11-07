# Plan de Desarrollo: Creación Masiva de Items con IA

**Versión:** 1.0
**Fecha:** 2025-11-07
**Autor:** Claude Code
**Proyecto:** Widget Sidebar v3.0.0

---

## 📋 Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Análisis de Requerimientos](#análisis-de-requerimientos)
3. [Arquitectura de la Solución](#arquitectura-de-la-solución)
4. [Modelo de Datos JSON](#modelo-de-datos-json)
5. [Estructura de Archivos](#estructura-de-archivos)
6. [Fases de Desarrollo](#fases-de-desarrollo)
7. [Especificaciones Técnicas](#especificaciones-técnicas)
8. [Consideraciones UX/UI](#consideraciones-uxui)
9. [Testing y Validación](#testing-y-validación)
10. [Roadmap Temporal](#roadmap-temporal)

---

## 🎯 Resumen Ejecutivo

### Objetivo
Implementar un sistema de creación masiva de items mediante prompts generados dinámicamente para modelos de IA, permitiendo importar múltiples items desde JSON con previsualización y validación.

### Problema a Resolver
Actualmente, crear múltiples items desde conversaciones con IAs (ejemplo: pasos para clonar repo, deploy a VPS, etc.) requiere copiar y pegar manualmente cada paso, siendo un proceso lento y tedioso.

### Solución Propuesta
Sistema wizard de 5 pasos integrado en la UI principal:
1. **Configuración** → Selección de categoría, tags, opciones
2. **Generación de Prompt** → Prompt personalizado para IA
3. **Importación JSON** → Pegar respuesta JSON de la IA
4. **Previsualización** → Revisar y filtrar items antes de crear
5. **Creación Masiva** → Inserción batch en BD con feedback

### Beneficios
- ⚡ **Velocidad**: Reducción de 90% en tiempo de creación masiva
- 🎯 **Precisión**: Validación previa antes de insertar
- 🔄 **Flexibilidad**: Reutilización de prompts configurados
- 📊 **Escalabilidad**: Soporte para 100+ items simultáneos

---

## 📊 Análisis de Requerimientos

### Requerimientos Funcionales

#### RF-01: Acceso a la Funcionalidad
- **ID:** RF-01
- **Prioridad:** Alta
- **Descripción:** Botón de acceso rápido en MainWindow (sidebar o header)
- **Criterios de Aceptación:**
  - Icono visible tipo "🤖" o "✨" en zona superior de la UI
  - Click abre ventana wizard modal
  - Acceso desde hotkey opcional (Ctrl+Shift+I)

#### RF-02: Paso 1 - Configuración de Opciones
- **ID:** RF-02
- **Prioridad:** Alta
- **Descripción:** Formulario de configuración para personalizar prompt
- **Campos Requeridos:**
  - ComboBox de categorías (carga desde BD)
  - Tags input con autocompletado (desde tag_groups)
  - Selector de tipo de item (TEXT/URL/CODE/PATH)
  - Checkbox: is_favorite
  - Checkbox: is_sensitive
  - TextEdit: descripción por defecto (opcional)
  - ColorPicker: color por defecto (opcional)
- **Criterios de Aceptación:**
  - Al menos categoría debe estar seleccionada
  - Tags pueden ser múltiples (separados por coma)
  - Tipo de item tiene valor por defecto (CODE)

#### RF-03: Paso 2 - Generación de Prompt
- **ID:** RF-03
- **Prioridad:** Alta
- **Descripción:** Generación automática de prompt estructurado
- **Componentes:**
  - TextEdit de solo lectura con prompt generado
  - Botón "Copiar Prompt" al portapapeles
  - Botón "Regenerar" si se cambian opciones
- **Formato del Prompt:**
```
Genera un JSON con items para Widget Sidebar siguiendo esta estructura exacta:

{
  "category_id": [ID],
  "defaults": {
    "type": "[TYPE]",
    "tags": "[TAGS]",
    "is_favorite": [0/1],
    "is_sensitive": [0/1]
  },
  "items": [
    {
      "label": "nombre corto del paso",
      "content": "contenido/comando/url completo",
      "description": "descripción opcional del item"
    }
  ]
}

CONTEXTO:
- Categoría: [NOMBRE_CATEGORIA]
- Tipo de items: [TYPE]
- Tags: [TAGS]

Genera items basados en: [CONTEXTO DEL USUARIO]
```

#### RF-04: Paso 3 - Importación de JSON
- **ID:** RF-04
- **Prioridad:** Alta
- **Descripción:** Campo de texto para pegar JSON generado por IA
- **Componentes:**
  - TextEdit multilínea con syntax highlighting JSON
  - Botón "Validar JSON"
  - Indicador visual de validez (✓ / ✗)
  - Mensaje de error descriptivo si JSON inválido
- **Validaciones:**
  - JSON bien formado (syntax)
  - Estructura esperada (category_id, defaults, items[])
  - category_id existe en BD
  - Tipos de datos correctos
  - Items array no vacío

#### RF-05: Paso 4 - Previsualización
- **ID:** RF-05
- **Prioridad:** Alta
- **Descripción:** Vista previa editable de items a crear
- **Componentes:**
  - QTableWidget con columnas:
    - [✓] Checkbox selección
    - Label (editable)
    - Content (preview truncado, tooltip completo)
    - Type (editable via combo)
    - Tags (editable)
    - Description (editable)
  - Contador: "X de Y items seleccionados"
  - Botones: "Seleccionar Todos" / "Deseleccionar Todos"
  - Botón: "Eliminar Seleccionados"
- **Funcionalidades:**
  - Edición inline de celdas
  - Ordenamiento por columnas
  - Búsqueda/filtrado rápido
  - Doble click en content para ver completo

#### RF-06: Paso 5 - Creación Masiva
- **ID:** RF-06
- **Prioridad:** Alta
- **Descripción:** Inserción batch en BD con feedback
- **Componentes:**
  - Botón "Crear Items" (primary action)
  - ProgressBar durante inserción
  - Mensaje de confirmación con resumen
- **Proceso:**
  1. Iniciar transacción SQLite
  2. Insertar items seleccionados uno por uno
  3. Actualizar item_count de categoría
  4. Commit transacción
  5. Invalidar cache de filtros
  6. Mostrar notificación de éxito
  7. Refrescar UI (sidebar, floating panel si está abierto)

#### RF-07: Navegación entre Pasos
- **ID:** RF-07
- **Prioridad:** Media
- **Descripción:** Sistema de navegación tipo wizard
- **Componentes:**
  - Stepper visual mostrando paso actual (1/5, 2/5...)
  - Botones "Anterior" / "Siguiente"
  - Botón "Cancelar" (confirma antes de cerrar)
  - Validación antes de avanzar a siguiente paso
- **Lógica:**
  - Paso 1 → 2: Requiere categoría seleccionada
  - Paso 2 → 3: Prompt generado
  - Paso 3 → 4: JSON válido
  - Paso 4 → 5: Al menos 1 item seleccionado

#### RF-08: Persistencia de Configuración
- **ID:** RF-08
- **Prioridad:** Baja
- **Descripción:** Guardar última configuración usada
- **Implementación:**
  - Guardar en tabla `settings` como JSON:
    - `ai_bulk_last_category_id`
    - `ai_bulk_last_tags`
    - `ai_bulk_last_type`
  - Precargar valores al abrir wizard

### Requerimientos No Funcionales

#### RNF-01: Performance
- Importación de hasta 500 items en < 5 segundos
- Validación JSON en < 500ms para archivos < 1MB
- UI responsiva durante inserción (no bloquear)

#### RNF-02: Usabilidad
- Wizard completable en < 2 minutos
- Mensajes de error claros y accionables
- Tooltips explicativos en cada campo

#### RNF-03: Seguridad
- Items marcados como is_sensitive se encriptan automáticamente
- Validación de XSS en campos de texto
- Límite de tamaño JSON: 10MB

#### RNF-04: Compatibilidad
- Windows 10/11
- PyQt6 6.7.0+
- SQLite 3.x

---

## 🏗️ Arquitectura de la Solución

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                      MainWindow                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Sidebar                                                │ │
│  │  ┌──────────────┐                                       │ │
│  │  │ [🤖] AI Bulk │ ◄─── Nuevo botón                      │ │
│  │  └──────────────┘                                       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Click
                           ▼
┌─────────────────────────────────────────────────────────────┐
│          AIBulkItemCreationWizard (QDialog)                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  QStackedWidget (5 páginas)                            │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ Página 1: ConfigurationStep                      │ │ │
│  │  │   - CategorySelector                             │ │ │
│  │  │   - TagsInput                                    │ │ │
│  │  │   - TypeSelector                                 │ │ │
│  │  │   - OptionsCheckboxes                            │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ Página 2: PromptGenerationStep                   │ │ │
│  │  │   - PromptDisplay (QTextEdit readonly)           │ │ │
│  │  │   - CopyButton                                   │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ Página 3: JSONImportStep                         │ │ │
│  │  │   - JSONTextEdit (syntax highlighting)           │ │ │
│  │  │   - ValidateButton                               │ │ │
│  │  │   - ValidationStatus                             │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ Página 4: PreviewStep                            │ │ │
│  │  │   - ItemsTableWidget                             │ │ │
│  │  │   - SelectionControls                            │ │ │
│  │  │   - FilterBar                                    │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ Página 5: CreationStep                           │ │ │
│  │  │   - ProgressBar                                  │ │ │
│  │  │   - StatusLabel                                  │ │ │
│  │  │   - SummaryReport                                │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Navigation Bar (bottom)                               │ │
│  │  [Cancel] [< Previous] [Next >] [Create Items]         │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Usa
                           ▼
┌─────────────────────────────────────────────────────────────┐
│       AIBulkItemManager (src/core/ai_bulk_manager.py)        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  + generate_prompt(config: dict) -> str                │ │
│  │  + validate_json(json_str: str) -> ValidationResult    │ │
│  │  + parse_items(json_data: dict) -> List[ItemData]      │ │
│  │  + create_items_bulk(items: List[ItemData]) -> Result  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Accede a
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              DBManager (src/database/db_manager.py)          │
│  + add_item()                                                │
│  + add_items_bulk() ◄─── NUEVA FUNCIÓN                       │
│  + get_categories()                                          │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de Datos

```
[Usuario]
    │
    ├─► [1. Configura opciones] → ConfigData
    │
    ├─► [2. Genera prompt] → PromptTemplate + ConfigData = PromptText
    │                              │
    │                              ▼ (Usuario copia a IA externa)
    │                         [ChatGPT/Claude]
    │                              │
    │                              ▼
    ├─► [3. Pega JSON] → JSONString
    │          │
    │          ├─► Validación → ✓/✗
    │          │
    │          └─► Parse → List[ItemData]
    │
    ├─► [4. Previsualiza] → Edición → FilteredItemData
    │
    └─► [5. Crea items] → DB Transaction → Success/Failure
                                  │
                                  ▼
                          [UI Refresh] → Sidebar + FloatingPanel
```

---

## 📄 Modelo de Datos JSON

### Estructura Esperada

```json
{
  "category_id": 3,
  "defaults": {
    "type": "CODE",
    "tags": "git,deployment",
    "is_favorite": 0,
    "is_sensitive": 0,
    "icon": "🚀",
    "color": "#00d4ff",
    "working_dir": ""
  },
  "items": [
    {
      "label": "Clonar repositorio",
      "content": "git clone https://github.com/user/repo.git",
      "description": "Clonar repo desde GitHub",
      "type": "CODE",
      "tags": "git,clone",
      "icon": "📦"
    },
    {
      "label": "Instalar dependencias",
      "content": "cd repo && npm install",
      "description": "Instalar paquetes npm",
      "working_dir": "/path/to/repo"
    },
    {
      "label": "Configurar variables",
      "content": "cp .env.example .env",
      "is_sensitive": 1
    }
  ]
}
```

### Esquema JSON (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["category_id", "items"],
  "properties": {
    "category_id": {
      "type": "integer",
      "minimum": 1,
      "description": "ID de categoría existente en BD"
    },
    "defaults": {
      "type": "object",
      "description": "Valores por defecto para todos los items",
      "properties": {
        "type": {"enum": ["TEXT", "URL", "CODE", "PATH"]},
        "tags": {"type": "string"},
        "is_favorite": {"type": "integer", "enum": [0, 1]},
        "is_sensitive": {"type": "integer", "enum": [0, 1]},
        "icon": {"type": "string"},
        "color": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
        "description": {"type": "string"},
        "working_dir": {"type": "string"}
      }
    },
    "items": {
      "type": "array",
      "minItems": 1,
      "maxItems": 500,
      "items": {
        "type": "object",
        "required": ["label", "content"],
        "properties": {
          "label": {"type": "string", "minLength": 1, "maxLength": 200},
          "content": {"type": "string", "minLength": 1},
          "description": {"type": "string"},
          "type": {"enum": ["TEXT", "URL", "CODE", "PATH"]},
          "tags": {"type": "string"},
          "icon": {"type": "string"},
          "color": {"type": "string"},
          "is_favorite": {"type": "integer", "enum": [0, 1]},
          "is_sensitive": {"type": "integer", "enum": [0, 1]},
          "working_dir": {"type": "string"}
        }
      }
    }
  }
}
```

### Reglas de Merge (defaults + items)

1. Cada item hereda valores de `defaults` si no especifica el campo
2. Valores en `items[i]` sobreescriben `defaults`
3. Campos obligatorios en items: `label`, `content`
4. Tipo por defecto si no existe en ninguno: `TEXT`

**Ejemplo de Merge:**
```python
# Input JSON
defaults = {"type": "CODE", "tags": "python"}
item = {"label": "Test", "content": "pytest", "tags": "testing"}

# Resultado merged
merged_item = {
    "label": "Test",
    "content": "pytest",
    "type": "CODE",        # ← heredado de defaults
    "tags": "testing"      # ← sobreescribe defaults
}
```

---

## 📁 Estructura de Archivos

### Archivos Nuevos a Crear

```
widget_sidebar/
├── src/
│   ├── core/
│   │   └── ai_bulk_manager.py          # [NUEVO] Manager principal
│   │
│   ├── views/
│   │   ├── dialogs/
│   │   │   └── ai_bulk_wizard.py       # [NUEVO] Ventana wizard principal
│   │   │
│   │   └── widgets/
│   │       ├── ai_config_step.py       # [NUEVO] Paso 1: Configuración
│   │       ├── ai_prompt_step.py       # [NUEVO] Paso 2: Prompt
│   │       ├── ai_json_step.py         # [NUEVO] Paso 3: Import JSON
│   │       ├── ai_preview_step.py      # [NUEVO] Paso 4: Preview
│   │       ├── ai_creation_step.py     # [NUEVO] Paso 5: Creación
│   │       └── json_editor.py          # [NUEVO] Editor JSON con highlighting
│   │
│   ├── utils/
│   │   ├── json_validator.py           # [NUEVO] Validador JSON Schema
│   │   └── prompt_templates.py         # [NUEVO] Templates de prompts
│   │
│   └── models/
│       └── bulk_item_data.py           # [NUEVO] Dataclass para items bulk
│
└── tests/
    └── test_ai_bulk_manager.py         # [NUEVO] Tests unitarios
```

### Archivos a Modificar

```
widget_sidebar/
├── src/
│   ├── database/
│   │   └── db_manager.py               # [MODIFICAR] Agregar add_items_bulk()
│   │
│   ├── views/
│   │   └── main_window.py              # [MODIFICAR] Botón de acceso al wizard
│   │
│   └── controllers/
│       └── main_controller.py          # [MODIFICAR] Integrar refresh después de bulk
│
└── requirements.txt                    # [MODIFICAR] Agregar jsonschema
```

---

## 🚀 Fases de Desarrollo

### **FASE 1: Fundamentos y Arquitectura Base** ⏱️ 4-6 horas

#### Objetivo
Establecer la infraestructura base del sistema: modelos de datos, manager principal y validación JSON.

#### Tareas

##### 1.1. Crear Modelo de Datos
**Archivo:** `src/models/bulk_item_data.py`

```python
"""
Modelos de datos para creación masiva de items.
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class BulkItemDefaults:
    """Valores por defecto para items bulk."""
    type: str = 'TEXT'
    tags: str = ''
    is_favorite: int = 0
    is_sensitive: int = 0
    icon: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    working_dir: Optional[str] = None

@dataclass
class BulkItemData:
    """Datos de un item individual en bulk import."""
    label: str
    content: str
    type: str = 'TEXT'
    tags: str = ''
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_favorite: int = 0
    is_sensitive: int = 0
    working_dir: Optional[str] = None

    # Metadata
    selected: bool = True  # Para preview/deselección

    def merge_defaults(self, defaults: BulkItemDefaults):
        """Merge con valores por defecto."""
        if not self.type or self.type == 'TEXT':
            self.type = defaults.type
        if not self.tags:
            self.tags = defaults.tags
        if self.is_favorite == 0:
            self.is_favorite = defaults.is_favorite
        if self.is_sensitive == 0:
            self.is_sensitive = defaults.is_sensitive
        if not self.icon:
            self.icon = defaults.icon
        if not self.color:
            self.color = defaults.color
        if not self.description:
            self.description = defaults.description
        if not self.working_dir:
            self.working_dir = defaults.working_dir

@dataclass
class BulkImportConfig:
    """Configuración para generación de prompt."""
    category_id: int
    category_name: str
    defaults: BulkItemDefaults
    user_context: str = ''  # Contexto adicional del usuario

@dataclass
class ValidationResult:
    """Resultado de validación JSON."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    items_count: int = 0
```

**Checklist:**
- [ ] Crear archivo `bulk_item_data.py`
- [ ] Implementar dataclasses
- [ ] Documentar cada clase con docstrings
- [ ] Agregar type hints completos
- [ ] Test manual de instanciación

---

##### 1.2. Crear Validador JSON
**Archivo:** `src/utils/json_validator.py`

```python
"""
Validador de JSON para bulk import usando JSON Schema.
"""
import json
from typing import Dict, Any
from jsonschema import validate, ValidationError, Draft7Validator
from models.bulk_item_data import ValidationResult

class BulkJSONValidator:
    """Validador de estructura JSON para bulk import."""

    SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["category_id", "items"],
        "properties": {
            "category_id": {
                "type": "integer",
                "minimum": 1
            },
            "defaults": {
                "type": "object",
                "properties": {
                    "type": {"enum": ["TEXT", "URL", "CODE", "PATH"]},
                    "tags": {"type": "string"},
                    "is_favorite": {"type": "integer", "enum": [0, 1]},
                    "is_sensitive": {"type": "integer", "enum": [0, 1]},
                    "icon": {"type": "string"},
                    "color": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
                    "description": {"type": "string"},
                    "working_dir": {"type": "string"}
                }
            },
            "items": {
                "type": "array",
                "minItems": 1,
                "maxItems": 500,
                "items": {
                    "type": "object",
                    "required": ["label", "content"],
                    "properties": {
                        "label": {"type": "string", "minLength": 1, "maxLength": 200},
                        "content": {"type": "string", "minLength": 1},
                        "description": {"type": "string"},
                        "type": {"enum": ["TEXT", "URL", "CODE", "PATH"]},
                        "tags": {"type": "string"},
                        "icon": {"type": "string"},
                        "color": {"type": "string"},
                        "is_favorite": {"type": "integer", "enum": [0, 1]},
                        "is_sensitive": {"type": "integer", "enum": [0, 1]},
                        "working_dir": {"type": "string"}
                    }
                }
            }
        }
    }

    @staticmethod
    def validate_json_string(json_str: str) -> ValidationResult:
        """Valida string JSON."""
        result = ValidationResult(is_valid=False)

        # 1. Validar syntax JSON
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            result.errors.append(f"JSON inválido: {str(e)}")
            return result

        # 2. Validar contra schema
        try:
            validate(instance=data, schema=BulkJSONValidator.SCHEMA)
        except ValidationError as e:
            result.errors.append(f"Estructura inválida: {e.message}")
            return result

        # 3. Validaciones adicionales
        # ... (implementar)

        result.is_valid = True
        result.items_count = len(data.get('items', []))
        return result
```

**Checklist:**
- [ ] Crear archivo `json_validator.py`
- [ ] Implementar schema JSON
- [ ] Implementar método `validate_json_string()`
- [ ] Agregar validaciones adicionales (duplicados, etc.)
- [ ] Tests con JSONs válidos e inválidos

---

##### 1.3. Crear Templates de Prompts
**Archivo:** `src/utils/prompt_templates.py`

```python
"""
Templates para generación de prompts de IA.
"""
from typing import Dict

class PromptTemplate:
    """Generador de prompts para IAs."""

    MAIN_TEMPLATE = """Genera un archivo JSON para Widget Sidebar siguiendo EXACTAMENTE esta estructura:

{{
  "category_id": {category_id},
  "defaults": {{
    "type": "{item_type}",
    "tags": "{tags}",
    "is_favorite": {is_favorite},
    "is_sensitive": {is_sensitive}
  }},
  "items": [
    {{
      "label": "nombre corto del paso",
      "content": "comando/url/texto completo aquí",
      "description": "descripción opcional del item"
    }}
  ]
}}

CONTEXTO:
- Categoría: {category_name} (ID: {category_id})
- Tipo de items: {item_type} ({item_type_desc})
- Tags: {tags}
- Favoritos por defecto: {is_favorite_text}
- Sensibles por defecto: {is_sensitive_text}

REGLAS IMPORTANTES:
1. Cada item debe tener "label" (max 200 caracteres) y "content"
2. El "label" debe ser descriptivo pero conciso
3. El "content" debe ser el comando/url/texto completo y funcional
4. Puedes sobreescribir "type", "tags", etc. en items individuales si es necesario
5. Genera entre 1 y 50 items según el contexto
6. NO agregues comentarios en el JSON, solo estructura válida

CONTEXTO DEL USUARIO:
{user_context}

IMPORTANTE: Responde ÚNICAMENTE con el JSON válido, sin texto adicional antes o después.
"""

    @staticmethod
    def generate(config: Dict) -> str:
        """Genera prompt personalizado."""
        item_type_descs = {
            'TEXT': 'Texto plano general',
            'URL': 'Enlaces web',
            'CODE': 'Comandos de terminal o código',
            'PATH': 'Rutas de archivos/directorios'
        }

        return PromptTemplate.MAIN_TEMPLATE.format(
            category_id=config['category_id'],
            category_name=config['category_name'],
            item_type=config['item_type'],
            item_type_desc=item_type_descs.get(config['item_type'], ''),
            tags=config['tags'],
            is_favorite=config['is_favorite'],
            is_sensitive=config['is_sensitive'],
            is_favorite_text='SÍ' if config['is_favorite'] else 'NO',
            is_sensitive_text='SÍ (encriptados)' if config['is_sensitive'] else 'NO',
            user_context=config.get('user_context', 'No especificado')
        )
```

**Checklist:**
- [ ] Crear archivo `prompt_templates.py`
- [ ] Implementar template principal
- [ ] Agregar descripciones de tipos
- [ ] Test de generación con varios configs
- [ ] Copiar prompt generado a IA real para validar

---

##### 1.4. Crear Manager Principal
**Archivo:** `src/core/ai_bulk_manager.py`

```python
"""
Manager para creación masiva de items mediante IA.
"""
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.bulk_item_data import (
    BulkItemData, BulkItemDefaults,
    BulkImportConfig, ValidationResult
)
from utils.json_validator import BulkJSONValidator
from utils.prompt_templates import PromptTemplate
from database.db_manager import DBManager

logger = logging.getLogger(__name__)

class AIBulkItemManager:
    """Manager para creación masiva de items con IA."""

    def __init__(self, db_manager: DBManager):
        self.db = db_manager
        self.validator = BulkJSONValidator()

    def generate_prompt(self, config: BulkImportConfig) -> str:
        """Genera prompt personalizado para IA."""
        config_dict = {
            'category_id': config.category_id,
            'category_name': config.category_name,
            'item_type': config.defaults.type,
            'tags': config.defaults.tags,
            'is_favorite': config.defaults.is_favorite,
            'is_sensitive': config.defaults.is_sensitive,
            'user_context': config.user_context
        }

        prompt = PromptTemplate.generate(config_dict)
        logger.info(f"Prompt generado para categoría {config.category_name}")
        return prompt

    def validate_json(self, json_str: str) -> ValidationResult:
        """Valida JSON de import."""
        return self.validator.validate_json_string(json_str)

    def parse_items(self, json_str: str) -> tuple[List[BulkItemData], BulkItemDefaults, int]:
        """
        Parsea JSON y retorna lista de items con defaults aplicados.

        Returns:
            (items_list, defaults, category_id)
        """
        data = json.loads(json_str)

        # Parsear defaults
        defaults_dict = data.get('defaults', {})
        defaults = BulkItemDefaults(**defaults_dict)

        # Parsear items
        items = []
        for item_data in data['items']:
            item = BulkItemData(**item_data)
            item.merge_defaults(defaults)
            items.append(item)

        category_id = data['category_id']

        logger.info(f"Parseados {len(items)} items para categoría {category_id}")
        return items, defaults, category_id

    def create_items_bulk(
        self,
        items: List[BulkItemData],
        category_id: int
    ) -> Dict[str, Any]:
        """
        Crea items masivamente en BD.

        Returns:
            {
                'success': bool,
                'created_count': int,
                'failed_count': int,
                'errors': List[str]
            }
        """
        result = {
            'success': False,
            'created_count': 0,
            'failed_count': 0,
            'errors': []
        }

        # Validar que categoría existe
        category = self.db.get_category_by_id(category_id)
        if not category:
            result['errors'].append(f"Categoría {category_id} no existe")
            return result

        # Filtrar solo items seleccionados
        selected_items = [item for item in items if item.selected]

        if not selected_items:
            result['errors'].append("No hay items seleccionados")
            return result

        # Inserción en transacción
        try:
            with self.db.transaction() as conn:
                for item in selected_items:
                    try:
                        self.db.add_item(
                            category_id=category_id,
                            label=item.label,
                            content=item.content,
                            item_type=item.type,
                            tags=item.tags,
                            description=item.description,
                            icon=item.icon,
                            color=item.color,
                            is_sensitive=item.is_sensitive,
                            is_favorite=item.is_favorite,
                            working_dir=item.working_dir
                        )
                        result['created_count'] += 1
                    except Exception as e:
                        result['failed_count'] += 1
                        result['errors'].append(f"Error en '{item.label}': {str(e)}")
                        logger.error(f"Error creando item {item.label}: {e}")

                # Actualizar item_count de categoría
                self.db.update_category_item_count(category_id)

            result['success'] = result['created_count'] > 0
            logger.info(f"Bulk creation: {result['created_count']} creados, {result['failed_count']} fallidos")

        except Exception as e:
            result['errors'].append(f"Error en transacción: {str(e)}")
            logger.error(f"Error en bulk creation: {e}")

        return result
```

**Checklist:**
- [ ] Crear archivo `ai_bulk_manager.py`
- [ ] Implementar `__init__()` con DBManager
- [ ] Implementar `generate_prompt()`
- [ ] Implementar `validate_json()`
- [ ] Implementar `parse_items()`
- [ ] Implementar `create_items_bulk()`
- [ ] Agregar logging en cada método
- [ ] Tests unitarios básicos

---

##### 1.5. Extender DBManager
**Archivo:** `src/database/db_manager.py` (MODIFICAR)

Agregar métodos:

```python
def update_category_item_count(self, category_id: int):
    """Actualiza contador de items de una categoría."""
    with self.transaction() as conn:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM items WHERE category_id = ? AND is_active = 1",
            (category_id,)
        )
        count = cursor.fetchone()[0]

        conn.execute(
            "UPDATE categories SET item_count = ? WHERE id = ?",
            (count, category_id)
        )

    logger.debug(f"Updated item_count for category {category_id}: {count}")

def get_category_by_id(self, category_id: int) -> Optional[Dict]:
    """Obtiene categoría por ID."""
    cursor = self.conn.execute(
        "SELECT * FROM categories WHERE id = ?",
        (category_id,)
    )
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None
```

**Checklist:**
- [ ] Agregar método `update_category_item_count()`
- [ ] Agregar método `get_category_by_id()`
- [ ] Tests de estos métodos
- [ ] Verificar transacciones funcionan correctamente

---

##### 1.6. Actualizar requirements.txt
**Archivo:** `requirements.txt` (MODIFICAR)

Agregar:
```
jsonschema>=4.17.0
```

**Checklist:**
- [ ] Agregar jsonschema a requirements
- [ ] Ejecutar `pip install -r requirements.txt`
- [ ] Verificar importación funciona

---

### **FASE 2: UI - Wizard Principal y Navegación** ⏱️ 5-7 horas

#### Objetivo
Crear la ventana wizard modal con sistema de navegación entre pasos.

#### Tareas

##### 2.1. Crear Wizard Principal
**Archivo:** `src/views/dialogs/ai_bulk_wizard.py`

```python
"""
Wizard para creación masiva de items con IA.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from core.ai_bulk_manager import AIBulkItemManager
from database.db_manager import DBManager

# Importar steps (se crearán después)
# from views.widgets.ai_config_step import ConfigStep
# from views.widgets.ai_prompt_step import PromptStep
# from views.widgets.ai_json_step import JSONStep
# from views.widgets.ai_preview_step import PreviewStep
# from views.widgets.ai_creation_step import CreationStep

class AIBulkWizard(QDialog):
    """Wizard para creación masiva de items."""

    items_created = pyqtSignal(int)  # Señal con count de items creados

    def __init__(self, db_manager: DBManager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.manager = AIBulkItemManager(db_manager)

        self.current_step = 0
        self.total_steps = 5

        self.init_ui()
        self.load_last_config()

    def init_ui(self):
        """Inicializa UI."""
        self.setWindowTitle("Creación Masiva de Items con IA")
        self.setMinimumSize(800, 600)
        self.setModal(True)

        layout = QVBoxLayout()

        # Header con indicador de paso
        header = self._create_header()
        layout.addWidget(header)

        # Stacked widget para pasos
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # TODO: Agregar steps cuando se creen
        # self.config_step = ConfigStep(self.db)
        # self.stacked_widget.addWidget(self.config_step)

        # Navigation bar
        nav_bar = self._create_navigation_bar()
        layout.addLayout(nav_bar)

        self.setLayout(layout)

    def _create_header(self) -> QLabel:
        """Crea header con título y paso actual."""
        header = QLabel()
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        header.setFont(font)
        header.setStyleSheet("padding: 20px; background: #1e1e1e;")
        self.update_header_text()
        return header

    def update_header_text(self):
        """Actualiza texto del header."""
        step_names = [
            "Configuración",
            "Generar Prompt",
            "Importar JSON",
            "Previsualizar Items",
            "Crear Items"
        ]
        text = f"Paso {self.current_step + 1}/{self.total_steps}: {step_names[self.current_step]}"
        # self.header.setText(text)  # TODO: guardar referencia

    def _create_navigation_bar(self) -> QHBoxLayout:
        """Crea barra de navegación."""
        nav_layout = QHBoxLayout()

        # Botón cancelar
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.on_cancel)
        nav_layout.addWidget(self.btn_cancel)

        nav_layout.addStretch()

        # Botón anterior
        self.btn_previous = QPushButton("← Anterior")
        self.btn_previous.clicked.connect(self.go_previous)
        self.btn_previous.setEnabled(False)
        nav_layout.addWidget(self.btn_previous)

        # Botón siguiente
        self.btn_next = QPushButton("Siguiente →")
        self.btn_next.clicked.connect(self.go_next)
        nav_layout.addWidget(self.btn_next)

        # Botón crear (oculto inicialmente)
        self.btn_create = QPushButton("Crear Items")
        self.btn_create.clicked.connect(self.create_items)
        self.btn_create.setVisible(False)
        nav_layout.addWidget(self.btn_create)

        return nav_layout

    def go_next(self):
        """Avanza al siguiente paso."""
        # Validar paso actual antes de avanzar
        if not self.validate_current_step():
            return

        self.current_step += 1
        self.stacked_widget.setCurrentIndex(self.current_step)
        self.update_navigation_buttons()
        self.update_header_text()

    def go_previous(self):
        """Retrocede al paso anterior."""
        self.current_step -= 1
        self.stacked_widget.setCurrentIndex(self.current_step)
        self.update_navigation_buttons()
        self.update_header_text()

    def update_navigation_buttons(self):
        """Actualiza estado de botones de navegación."""
        # Anterior
        self.btn_previous.setEnabled(self.current_step > 0)

        # Siguiente / Crear
        if self.current_step == self.total_steps - 1:
            self.btn_next.setVisible(False)
            self.btn_create.setVisible(True)
        else:
            self.btn_next.setVisible(True)
            self.btn_create.setVisible(False)

    def validate_current_step(self) -> bool:
        """Valida que el paso actual se puede avanzar."""
        # TODO: Implementar validación según step
        return True

    def on_cancel(self):
        """Maneja cancelación del wizard."""
        reply = QMessageBox.question(
            self,
            "Cancelar",
            "¿Seguro que deseas cancelar? Se perderá el progreso.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.reject()

    def create_items(self):
        """Crea items en BD."""
        # TODO: Implementar cuando se tenga PreviewStep
        pass

    def load_last_config(self):
        """Carga última configuración usada."""
        # TODO: Implementar load desde settings
        pass
```

**Checklist:**
- [ ] Crear archivo `ai_bulk_wizard.py`
- [ ] Implementar estructura básica del dialog
- [ ] Crear header con indicador de paso
- [ ] Crear navigation bar con botones
- [ ] Implementar lógica de navegación
- [ ] Implementar confirmación de cancelación
- [ ] Test de apertura y navegación básica

---

##### 2.2. Integrar Botón en MainWindow
**Archivo:** `src/views/main_window.py` (MODIFICAR)

Agregar en la sección del sidebar o header:

```python
def init_ai_bulk_button(self):
    """Inicializa botón para AI Bulk Creation."""
    self.ai_bulk_btn = QPushButton("🤖")
    self.ai_bulk_btn.setToolTip("Creación masiva con IA")
    self.ai_bulk_btn.setFixedSize(40, 40)
    self.ai_bulk_btn.clicked.connect(self.open_ai_bulk_wizard)

    # Agregar a layout (ajustar según posición deseada)
    # self.header_layout.addWidget(self.ai_bulk_btn)

def open_ai_bulk_wizard(self):
    """Abre wizard de creación masiva."""
    from views.dialogs.ai_bulk_wizard import AIBulkWizard

    wizard = AIBulkWizard(self.controller.config_manager.db, self)
    wizard.items_created.connect(self.on_bulk_items_created)
    wizard.exec()

def on_bulk_items_created(self, count: int):
    """Callback después de crear items bulk."""
    # Refresh UI
    self.controller.load_categories()

    # Mostrar notificación
    # self.notification_manager.show_success(f"{count} items creados")
```

**Checklist:**
- [ ] Agregar botón en UI
- [ ] Implementar `open_ai_bulk_wizard()`
- [ ] Conectar señal `items_created`
- [ ] Implementar refresh de UI
- [ ] Test de apertura desde MainWindow

---

### **FASE 3: UI - Steps Individuales** ⏱️ 8-10 horas

#### Objetivo
Implementar cada uno de los 5 pasos del wizard con sus UIs específicas.

#### Tareas

##### 3.1. Step 1 - Configuración
**Archivo:** `src/views/widgets/ai_config_step.py`

**UI incluye:**
- QComboBox para categoría
- QLineEdit para tags con autocompletar
- QComboBox para tipo de item
- QCheckBox para is_favorite
- QCheckBox para is_sensitive
- QTextEdit para contexto del usuario

**Checklist:**
- [ ] Crear archivo y clase `ConfigStep(QWidget)`
- [ ] Diseñar layout con QFormLayout
- [ ] Cargar categorías desde BD
- [ ] Implementar autocompletar tags (desde tag_groups)
- [ ] Implementar getters para obtener config
- [ ] Validación: categoría requerida
- [ ] Persistir última selección

---

##### 3.2. Step 2 - Generación de Prompt
**Archivo:** `src/views/widgets/ai_prompt_step.py`

**UI incluye:**
- QTextEdit (readonly) mostrando prompt generado
- QPushButton "Copiar al Portapapeles"
- QLabel con instrucciones

**Checklist:**
- [ ] Crear archivo y clase `PromptStep(QWidget)`
- [ ] Recibir config del step anterior
- [ ] Llamar a `manager.generate_prompt()`
- [ ] Mostrar prompt en QTextEdit
- [ ] Implementar botón copiar (usando pyperclip)
- [ ] Agregar mensaje de confirmación al copiar
- [ ] Syntax highlighting opcional

---

##### 3.3. Step 3 - Importación JSON
**Archivo:** `src/views/widgets/ai_json_step.py`

**UI incluye:**
- QTextEdit para pegar JSON (con syntax highlighting)
- QPushButton "Validar JSON"
- QLabel con indicador de validez (✓ / ✗)
- QTextEdit pequeño con errores de validación

**Checklist:**
- [ ] Crear archivo y clase `JSONStep(QWidget)`
- [ ] Implementar QTextEdit para JSON
- [ ] Integrar syntax highlighting (usar `json_editor.py`)
- [ ] Botón validar llama a `manager.validate_json()`
- [ ] Mostrar resultado de validación visual
- [ ] Mostrar errores específicos si inválido
- [ ] No permitir avanzar si JSON inválido

---

##### 3.4. Step 4 - Previsualización
**Archivo:** `src/views/widgets/ai_preview_step.py`

**UI incluye:**
- QTableWidget con items parseados
- Columnas: [✓], Label, Content (preview), Type, Tags
- QLineEdit para filtrar items
- QPushButton "Seleccionar Todos"
- QPushButton "Deseleccionar Todos"
- QLabel contador "X de Y seleccionados"

**Checklist:**
- [ ] Crear archivo y clase `PreviewStep(QWidget)`
- [ ] Recibir lista de items del step anterior
- [ ] Poblar QTableWidget con items
- [ ] Implementar checkboxes en columna 1
- [ ] Contenido truncado con tooltip completo
- [ ] Edición inline de celdas
- [ ] Filtro de búsqueda
- [ ] Botones seleccionar/deseleccionar todos
- [ ] Contador dinámico
- [ ] Validación: mínimo 1 item seleccionado

---

##### 3.5. Step 5 - Creación
**Archivo:** `src/views/widgets/ai_creation_step.py`

**UI incluye:**
- QProgressBar
- QLabel con status actual
- QTextEdit con log de creación
- Resumen final con estadísticas

**Checklist:**
- [ ] Crear archivo y clase `CreationStep(QWidget)`
- [ ] Recibir items seleccionados
- [ ] Mostrar ProgressBar durante inserción
- [ ] Llamar a `manager.create_items_bulk()`
- [ ] Actualizar log en tiempo real
- [ ] Mostrar resumen: X creados, Y fallidos
- [ ] Mostrar errores si los hay
- [ ] Botón "Finalizar" que cierra wizard

---

##### 3.6. Widget de Editor JSON
**Archivo:** `src/views/widgets/json_editor.py`

**Funcionalidad:**
- QTextEdit con syntax highlighting para JSON
- Números de línea opcionales
- Colorear llaves, strings, números, booleans

**Checklist:**
- [ ] Crear clase `JSONEditor(QTextEdit)`
- [ ] Implementar syntax highlighter básico
- [ ] Usar fuente monospace
- [ ] Colores acorde al tema oscuro
- [ ] Integrar en JSONStep

---

### **FASE 4: Integración y Testing** ⏱️ 3-4 horas

#### Objetivo
Conectar todos los componentes y realizar testing integral.

#### Tareas

##### 4.1. Conectar Steps en Wizard

**En `ai_bulk_wizard.py`:**

```python
def init_steps(self):
    """Inicializa todos los steps."""
    self.config_step = ConfigStep(self.db)
    self.stacked_widget.addWidget(self.config_step)

    self.prompt_step = PromptStep(self.manager)
    self.stacked_widget.addWidget(self.prompt_step)

    self.json_step = JSONStep(self.manager)
    self.stacked_widget.addWidget(self.json_step)

    self.preview_step = PreviewStep()
    self.stacked_widget.addWidget(self.preview_step)

    self.creation_step = CreationStep(self.manager)
    self.stacked_widget.addWidget(self.creation_step)

def validate_current_step(self) -> bool:
    """Validación por paso."""
    if self.current_step == 0:
        return self.config_step.is_valid()
    elif self.current_step == 1:
        return True  # Prompt siempre válido
    elif self.current_step == 2:
        return self.json_step.is_valid()
    elif self.current_step == 3:
        return self.preview_step.has_selected_items()
    return True

def go_next(self):
    """Override con lógica de paso de datos."""
    if not self.validate_current_step():
        return

    # Pasar datos entre steps
    if self.current_step == 0:
        config = self.config_step.get_config()
        self.prompt_step.set_config(config)
    elif self.current_step == 2:
        items, defaults, cat_id = self.json_step.get_parsed_items()
        self.preview_step.set_items(items)
    elif self.current_step == 3:
        selected_items = self.preview_step.get_selected_items()
        self.creation_step.set_items(selected_items)

    super().go_next()
```

**Checklist:**
- [ ] Agregar todos los steps al stacked widget
- [ ] Implementar paso de datos entre steps
- [ ] Implementar validación por step
- [ ] Test de flujo completo mock

---

##### 4.2. Testing Unitario

**Archivo:** `tests/test_ai_bulk_manager.py`

```python
import pytest
from core.ai_bulk_manager import AIBulkItemManager
from models.bulk_item_data import BulkImportConfig, BulkItemDefaults

def test_generate_prompt():
    """Test generación de prompt."""
    # ...

def test_validate_json_valid():
    """Test validación JSON válido."""
    # ...

def test_validate_json_invalid():
    """Test validación JSON inválido."""
    # ...

def test_parse_items():
    """Test parseo de items."""
    # ...

def test_create_items_bulk():
    """Test creación masiva."""
    # ...
```

**Checklist:**
- [ ] Test de `generate_prompt()`
- [ ] Test de `validate_json()` con casos válidos e inválidos
- [ ] Test de `parse_items()`
- [ ] Test de `create_items_bulk()`
- [ ] Test de merge de defaults
- [ ] Ejecutar pytest y verificar cobertura

---

##### 4.3. Testing de Integración

**Escenarios:**
1. Flujo completo: Configuración → Prompt → JSON → Preview → Creación
2. Validación de JSON inválido bloquea avance
3. Deseleccionar todos items muestra error
4. Cancelar en medio del wizard
5. Crear 50+ items simultáneos
6. Items sensibles se encriptan correctamente

**Checklist:**
- [ ] Test flujo completo con datos reales
- [ ] Test con JSON de ChatGPT/Claude real
- [ ] Test con categoría inexistente (debe fallar)
- [ ] Test con 100+ items (performance)
- [ ] Test de encriptación de items sensibles
- [ ] Test de refresh UI después de crear

---

##### 4.4. Refinamiento UI/UX

**Checklist:**
- [ ] Revisar estilos acorde al tema oscuro
- [ ] Tooltips en todos los campos
- [ ] Mensajes de error claros
- [ ] Animaciones suaves entre pasos (opcional)
- [ ] Responsive en diferentes tamaños de ventana
- [ ] Keyboard shortcuts (Enter para siguiente, Esc para cancelar)

---

### **FASE 5: Optimización y Documentación** ⏱️ 2-3 horas

#### Objetivo
Optimizar performance, agregar logging completo y documentar.

#### Tareas

##### 5.1. Optimización

**Checklist:**
- [ ] Optimizar `create_items_bulk()` para grandes volúmenes
- [ ] Implementar batch insert (insertar múltiples en un query)
- [ ] Agregar timeout de validación JSON (evitar bloqueos)
- [ ] Cache de categorías en ConfigStep
- [ ] Debounce en filtro de PreviewStep

**Ejemplo batch insert:**
```python
def add_items_bulk(self, items_data: List[Dict]) -> int:
    """Inserta múltiples items en un batch."""
    with self.transaction() as conn:
        cursor = conn.executemany(
            """INSERT INTO items
            (category_id, label, content, type, tags, ...)
            VALUES (?, ?, ?, ?, ?, ...)""",
            [(i['category_id'], i['label'], ...) for i in items_data]
        )
        return cursor.rowcount
```

---

##### 5.2. Logging

**Checklist:**
- [ ] Logging en cada step de UI (debug level)
- [ ] Logging de errores de validación (error level)
- [ ] Logging de creación bulk con métricas (info level)
- [ ] Logging de excepciones con traceback completo

---

##### 5.3. Documentación

**Crear:** `util/AI_BULK_CREATION_USER_GUIDE.md`

**Contenido:**
- Guía de usuario paso a paso
- Screenshots de cada paso
- Ejemplos de prompts generados
- Ejemplos de JSONs válidos
- Troubleshooting de errores comunes
- FAQs

**Checklist:**
- [ ] Escribir guía de usuario
- [ ] Agregar ejemplos de uso
- [ ] Documentar formato JSON esperado
- [ ] Documentar errores comunes y soluciones

---

##### 5.4. Persistencia de Configuración

**Implementar en `settings` table:**

```python
def save_bulk_config(self, config: dict):
    """Guarda última configuración usada."""
    self.db.set_setting('ai_bulk_last_config', json.dumps(config))

def load_bulk_config(self) -> dict:
    """Carga última configuración."""
    value = self.db.get_setting('ai_bulk_last_config', '{}')
    return json.loads(value)
```

**Checklist:**
- [ ] Implementar save/load en DBManager
- [ ] Llamar save al completar wizard
- [ ] Llamar load al abrir wizard
- [ ] Precargar valores en ConfigStep

---

## 🎨 Consideraciones UX/UI

### Tema Oscuro
- Usar paleta de colores del proyecto:
  - Background: `#1e1e1e`, `#252525`
  - Text: `#ffffff`, `#cccccc`
  - Primary: `#00d4ff`
  - Success: `#00ff88`
  - Error: `#ff4444`

### Tipografía
- Headers: 14pt Bold
- Body: 10pt Regular
- Code/JSON: Monospace (Consolas, Courier New)

### Iconografía
- Usar emojis para consistencia:
  - 🤖 AI Bulk
  - ⚙️ Configuración
  - 📝 Prompt
  - 📋 JSON
  - 👁️ Preview
  - ✅ Crear

### Feedback Visual
- Loading spinners durante operaciones largas
- Checkmarks verdes para validaciones exitosas
- Íconos rojos para errores
- Progress bar en creación bulk

---

## 🧪 Testing y Validación

### Test Cases Críticos

#### TC-01: Flujo Completo Exitoso
**Precondiciones:** BD con al menos 1 categoría
**Pasos:**
1. Abrir wizard desde MainWindow
2. Seleccionar categoría "Git Commands"
3. Agregar tags "git,deploy"
4. Seleccionar tipo CODE
5. Generar prompt
6. Copiar prompt
7. Obtener JSON de ChatGPT
8. Pegar JSON en step 3
9. Validar JSON (debe ser ✓)
10. Avanzar a preview
11. Verificar items cargados
12. Deseleccionar 2 items
13. Crear items
14. Verificar creación exitosa

**Resultado esperado:** Items creados en BD, UI refrescada

---

#### TC-02: JSON Inválido
**Pasos:**
1. Llegar a step 3
2. Pegar JSON mal formado: `{category_id: 1,`
3. Validar

**Resultado esperado:** Error "JSON inválido: ...", no permite avanzar

---

#### TC-03: Categoría Inexistente
**Pasos:**
1. Configurar category_id = 9999 en JSON
2. Validar y avanzar
3. Intentar crear

**Resultado esperado:** Error "Categoría 9999 no existe"

---

#### TC-04: Items Sensibles
**Pasos:**
1. Configurar is_sensitive = 1 en defaults
2. Crear items
3. Verificar en BD que content está encriptado

**Resultado esperado:** Campo `content` encriptado en BD

---

#### TC-05: Edición en Preview
**Pasos:**
1. Llegar a preview con 10 items
2. Editar label de item 3
3. Editar tags de item 5
4. Crear items
5. Verificar en BD

**Resultado esperado:** Cambios aplicados correctamente

---

### Métricas de Performance

| Operación | Objetivo | Máximo Aceptable |
|-----------|----------|------------------|
| Validación JSON (100 items) | < 200ms | < 500ms |
| Parseo items (100 items) | < 100ms | < 300ms |
| Creación bulk (100 items) | < 2s | < 5s |
| Apertura wizard | < 500ms | < 1s |
| Carga categorías | < 100ms | < 300ms |

---

## 📅 Roadmap Temporal

### Timeline Estimado

```
Semana 1:
├─ Día 1-2: Fase 1 (Fundamentos) ⏱️ 6h
├─ Día 3: Fase 2 (Wizard base) ⏱️ 6h
└─ Día 4-5: Fase 3 Steps 1-3 ⏱️ 6h

Semana 2:
├─ Día 1-2: Fase 3 Steps 4-5 ⏱️ 4h
├─ Día 3: Fase 4 (Integración) ⏱️ 4h
└─ Día 4: Fase 5 (Optimización) ⏱️ 3h

Total: ~30 horas de desarrollo
```

### Milestones

| Milestone | Fecha Target | Entregable |
|-----------|--------------|------------|
| M1: Backend Completo | Día 2 | Manager + Validator + Templates |
| M2: Wizard Navegable | Día 3 | Wizard con navegación |
| M3: Steps 1-3 | Día 5 | Config + Prompt + JSON |
| M4: Steps 4-5 | Día 7 | Preview + Creation |
| M5: Testing | Día 9 | Todos los tests pasando |
| M6: Release | Día 10 | Documentación + Deploy |

---

## 🔧 Configuración y Deploy

### Variables de Configuración

```python
# En src/utils/constants.py agregar:
AI_BULK_CONFIG = {
    'MAX_ITEMS': 500,
    'JSON_MAX_SIZE_MB': 10,
    'VALIDATION_TIMEOUT_MS': 5000,
    'BATCH_INSERT_SIZE': 100,
    'ENABLE_SYNTAX_HIGHLIGHTING': True
}
```

### Feature Flags (Futuro)

```python
FEATURES = {
    'ai_bulk_creation': True,           # Habilitar feature
    'ai_bulk_advanced_editor': False,   # Editor JSON avanzado
    'ai_bulk_templates': False,         # Plantillas predefinidas
    'ai_bulk_export': False             # Exportar config a JSON
}
```

---

## 🚀 Mejoras Futuras (Post-MVP)

### V2.0 Features
1. **Templates Predefinidos**
   - Guardar configuraciones como templates
   - Librería de templates comunes (Docker, Git, DevOps)

2. **Editor Avanzado**
   - Autocompletado JSON
   - Linting en tiempo real
   - Formateo automático

3. **Validación Avanzada**
   - Detectar duplicados con items existentes
   - Sugerencias de mejora
   - Validación de URLs/paths reales

4. **Export/Import Config**
   - Exportar configuración a archivo
   - Compartir configs entre usuarios

5. **Integración Directa con APIs de IA**
   - Conectar directamente con OpenAI/Claude API
   - No requiere copiar/pegar manual

6. **Batch Operations**
   - Editar múltiples items simultáneamente
   - Operaciones en masa (cambiar tags, categoría)

---

## 📝 Notas de Implementación

### Decisiones de Diseño

1. **¿Por qué Wizard en lugar de Single Page?**
   - Proceso complejo con múltiples pasos
   - Validación incremental más clara
   - Mejor UX para usuarios no técnicos

2. **¿Por qué JSON y no CSV/Excel?**
   - IAs generan JSON naturalmente
   - Soporta estructura anidada
   - Fácil validación con JSON Schema

3. **¿Por qué no integración directa con API de IA?**
   - Requiere API keys (costo, seguridad)
   - Usuario puede usar cualquier IA (ChatGPT, Claude, Gemini)
   - Más flexible y sin vendor lock-in

### Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| IA genera JSON inválido | Alta | Medio | Validación robusta + mensajes claros |
| Performance con 500+ items | Media | Alto | Batch insert + progress feedback |
| Usuario no entiende el flujo | Media | Medio | Tooltips + guía de usuario |
| Encriptación falla | Baja | Alto | Tests exhaustivos + logging |

---

## ✅ Checklist Final de Completitud

### Backend
- [ ] `bulk_item_data.py` implementado y testeado
- [ ] `json_validator.py` implementado y testeado
- [ ] `prompt_templates.py` implementado y testeado
- [ ] `ai_bulk_manager.py` implementado y testeado
- [ ] DBManager extendido con métodos bulk
- [ ] Tests unitarios al 80%+ cobertura

### UI
- [ ] `ai_bulk_wizard.py` implementado
- [ ] `ai_config_step.py` implementado
- [ ] `ai_prompt_step.py` implementado
- [ ] `ai_json_step.py` implementado
- [ ] `ai_preview_step.py` implementado
- [ ] `ai_creation_step.py` implementado
- [ ] `json_editor.py` implementado
- [ ] Botón integrado en MainWindow

### Integración
- [ ] Flujo completo funcional end-to-end
- [ ] Paso de datos entre steps correcto
- [ ] Validaciones en cada paso
- [ ] Refresh UI después de crear
- [ ] Manejo de errores robusto

### Testing
- [ ] Tests unitarios pasando
- [ ] Tests de integración pasando
- [ ] Test con JSON real de ChatGPT
- [ ] Test de performance con 100+ items
- [ ] Test de encriptación

### Documentación
- [ ] Docstrings en todas las clases/métodos
- [ ] Guía de usuario creada
- [ ] Ejemplos de uso documentados
- [ ] Este plan actualizado con cambios

### Deploy
- [ ] Feature funciona en build de producción
- [ ] No hay regresiones en features existentes
- [ ] Logging configurado correctamente
- [ ] Performance aceptable

---

## 📚 Referencias

- **PyQt6 Docs:** https://doc.qt.io/qtforpython-6/
- **JSON Schema:** https://json-schema.org/
- **jsonschema Python:** https://python-jsonschema.readthedocs.io/
- **SQLite Transactions:** https://www.sqlite.org/lang_transaction.html

---

**FIN DEL PLAN**

---

*Última actualización: 2025-11-07*
*Versión del plan: 1.0*
*Estado: ✅ Listo para implementación*

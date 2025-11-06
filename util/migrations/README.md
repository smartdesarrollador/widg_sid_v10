# Scripts de Migración - Tag Groups

Este directorio contiene scripts para analizar, normalizar y migrar tags existentes al nuevo sistema de Tag Groups.

## 📋 Scripts Disponibles

### 1. `analyze_existing_tags.py`
Analiza todos los tags en la base de datos y genera un reporte detallado.

**Uso:**
```bash
python util/migrations/analyze_existing_tags.py
```

**Salida:**
- Genera reporte en: `util/migrations/tags_analysis_report.txt`
- Muestra estadísticas de uso de tags
- Detecta variaciones de mayúsculas/minúsculas
- Sugiere agrupaciones de tags por categoría

**Ejemplo de salida:**
```
📊 RESUMEN GENERAL
Total de items analizados: 156
Tags únicos (normalizados): 42

🏆 TOP 20 TAGS MÁS USADOS
python     → 45 items
api        → 32 items
react      → 28 items

⚠️ TAGS CON VARIACIONES
python: Python, python, PYTHON

💡 SUGERENCIAS DE TAG GROUPS
1. Python - Auto
   Tags: python, fastapi, api, database
```

---

### 2. `migrate_to_tag_groups.py`
Ejecuta la migración completa: normaliza tags y crea Tag Groups automáticos.

**Uso:**

**Modo DRY RUN (recomendado primero):**
```bash
python util/migrations/migrate_to_tag_groups.py --dry-run
```
- No aplica cambios
- Muestra qué haría el script
- Genera reporte de simulación

**Modo REAL (aplicar cambios):**
```bash
python util/migrations/migrate_to_tag_groups.py
```
- Crea backup automático de la base de datos
- Normaliza todos los tags (minúsculas)
- Crea Tag Groups predefinidos comunes
- Crea Tag Groups automáticos basados en análisis
- Genera reporte de migración

**Parámetros opcionales:**
```bash
python util/migrations/migrate_to_tag_groups.py --db-path C:\path\to\database.db --dry-run
```

**Salida:**
- Backup: `widget_sidebar_backup_YYYYMMDD_HHMMSS.db`
- Reporte: `util/migrations/migration_report.txt`

---

## 🚀 Flujo de Trabajo Recomendado

### Paso 1: Análisis
Ejecuta el análisis para entender el estado actual de tus tags:

```bash
python util/migrations/analyze_existing_tags.py
```

Revisa el reporte generado en `tags_analysis_report.txt`.

### Paso 2: Simulación
Ejecuta la migración en modo dry-run para ver qué cambios se aplicarían:

```bash
python util/migrations/migrate_to_tag_groups.py --dry-run
```

Revisa la salida en consola y el reporte.

### Paso 3: Migración Real
Si estás conforme con los cambios, ejecuta la migración real:

```bash
python util/migrations/migrate_to_tag_groups.py
```

**Nota:** El script crea un backup automático antes de hacer cambios.

### Paso 4: Verificación
Abre la aplicación y verifica:
- Settings → General → Gestionar Grupos de Tags
- Deberías ver los Tag Groups creados automáticamente
- Los items deberían tener tags normalizados

---

## ✨ ¿Qué hace la migración?

### 1. Normalización de Tags
- Convierte todos los tags a minúsculas
- Elimina espacios en blanco innecesarios
- Elimina duplicados (ej: "Python", "python" → "python")
- Actualiza todos los items con tags normalizados

**Ejemplo:**
```
Antes: ["Python", "FastAPI", "API"]
Después: ["python", "fastapi", "api"]
```

### 2. Tag Groups Predefinidos
Crea grupos comunes útiles:

- **🐍 Python Backend**: python, fastapi, django, flask, api, backend
- **🟨 JavaScript Frontend**: javascript, react, vue, angular, frontend, ui
- **🗄️ Database**: database, sql, mysql, postgresql, mongodb, orm
- **🚀 DevOps**: docker, kubernetes, ci-cd, deploy, nginx, devops
- **🌿 Git & Version Control**: git, github, gitlab, version-control, commit
- **✅ Testing**: test, pytest, jest, unit-test, integration-test

### 3. Tag Groups Automáticos
Crea grupos basados en análisis de tus categorías existentes:

- Analiza qué tags son más comunes en cada categoría
- Agrupa tags relacionados semánticamente
- Asigna iconos y colores apropiados
- Genera nombres descriptivos

**Ejemplo:**
Si tienes una categoría "Scripts Python" con items que usan frecuentemente:
`python`, `script`, `automation`, `cli`

El migrador creará:
- **Nombre:** "Scripts Python - Auto"
- **Tags:** python, script, automation, cli
- **Icon:** 🐍
- **Color:** #3776ab

---

## 🔒 Seguridad

### Backup Automático
El script de migración crea un backup automático antes de cualquier cambio:
```
widget_sidebar_backup_20251105_143022.db
```

### Restaurar desde Backup
Si algo sale mal:
```bash
# 1. Cerrar la aplicación
# 2. Reemplazar la base de datos actual con el backup
copy widget_sidebar_backup_YYYYMMDD_HHMMSS.db widget_sidebar.db
# 3. Reiniciar la aplicación
```

### Modo Dry Run
Siempre usa `--dry-run` primero para ver qué cambios se aplicarían.

---

## 📊 Interpretación de Reportes

### Tags Analysis Report

**Sección "TAGS CON VARIACIONES":**
Lista tags que tienen múltiples formas (mayúsculas/minúsculas).
Estos serán normalizados durante la migración.

**Sección "TAGS POR CATEGORÍA":**
Muestra qué tags son más usados en cada categoría.
Útil para entender patrones de uso.

**Sección "SUGERENCIAS DE TAG GROUPS":**
Grupos sugeridos basados en análisis automático.
Estos se crearán durante la migración.

### Migration Report

**Estadísticas:**
- Items actualizados: Número de items con tags modificados
- Variaciones corregidas: Número de tags normalizados
- Tag Groups creados: Número de grupos generados

**Log de Cambios:**
Detalle cronológico de cada operación realizada.

---

## ⚠️ Notas Importantes

1. **No rompe compatibilidad:** Los items sin tags funcionan normalmente.

2. **Idempotente:** Puedes ejecutar el script múltiples veces de forma segura.
   - No crea duplicados
   - Salta Tag Groups que ya existen

3. **Tags adicionales:** Los Tag Groups son plantillas, siempre puedes agregar tags custom a items.

4. **Reversible:** Puedes restaurar desde backup si es necesario.

5. **Performance:** El script está optimizado, pero con miles de items puede tomar algunos segundos.

---

## 🐛 Troubleshooting

### Error: "Database not found"
Verifica que estás ejecutando desde la raíz del proyecto:
```bash
cd C:\Users\ASUS\Desktop\proyectos_python\widget_sidebar
python util/migrations/analyze_existing_tags.py
```

### Error: "Database is locked"
Cierra la aplicación antes de ejecutar los scripts de migración.

### Tags no se actualizaron
Verifica que ejecutaste sin `--dry-run`:
```bash
python util/migrations/migrate_to_tag_groups.py
```

### Tag Groups no aparecen en la UI
1. Cierra y reabre la aplicación
2. Ve a Settings → General → Gestionar Grupos de Tags
3. Deberías ver los grupos creados

---

## 📝 Logs y Reportes

### Archivos generados:

```
util/migrations/
├── tags_analysis_report.txt      # Reporte de análisis
├── migration_report.txt           # Reporte de migración
└── README.md                      # Este archivo

/
└── widget_sidebar_backup_*.db    # Backups automáticos
```

### Ver logs en consola
Ambos scripts muestran progreso detallado en consola en tiempo real.

---

## 🎯 Próximos Pasos

Después de ejecutar la migración:

1. **Verifica Tag Groups creados:**
   - Abre Settings → General → Gestionar Grupos de Tags
   - Revisa los grupos generados

2. **Prueba creando un nuevo item:**
   - Usa el selector de Tag Groups
   - Verifica que los tags se aplican correctamente

3. **Crea Tag Groups personalizados:**
   - Según tus necesidades específicas
   - Basándote en los sugeridos en el análisis

4. **Crea Smart Collections:**
   - Filtra items por los tags normalizados
   - Settings → General → Gestionar Colecciones Inteligentes

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisa este README
2. Consulta los reportes generados
3. Revisa `FASE_4_COMPLETADA.md` para detalles técnicos
4. Verifica los logs en consola

---

**Versión:** 1.0
**Última actualización:** 2025-11-05
**Compatibilidad:** Widget Sidebar v3.1+

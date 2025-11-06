"""
Migración: Agregar tablas para Tag Groups y Smart Collections
Fecha: 2025-11-05
Descripción:
    - Crea tabla tag_groups para plantillas de tags reutilizables
    - Crea tabla smart_collections para búsquedas inteligentes guardadas
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def migrate_add_tag_groups_and_collections(db_path: str) -> bool:
    """
    Ejecuta la migración para agregar tablas de Tag Groups y Smart Collections

    Args:
        db_path: Ruta al archivo de base de datos SQLite

    Returns:
        True si la migración fue exitosa, False en caso contrario
    """
    try:
        logger.info("Starting migration: add_tag_groups_and_collections")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Habilitar foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")

        # ========== TABLA 1: tag_groups ==========
        logger.info("Creating table: tag_groups")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tag_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                tags TEXT NOT NULL,
                color TEXT DEFAULT '#007acc',
                icon TEXT DEFAULT '🏷️',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)

        # Índices para tag_groups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tag_groups_name
            ON tag_groups(name)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tag_groups_active
            ON tag_groups(is_active)
        """)

        logger.info("Table tag_groups created successfully")

        # ========== TABLA 2: smart_collections ==========
        logger.info("Creating table: smart_collections")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS smart_collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                icon TEXT DEFAULT '🔍',
                color TEXT DEFAULT '#00d4ff',

                -- Filtros
                tags_include TEXT,
                tags_exclude TEXT,
                category_id INTEGER,
                item_type TEXT CHECK(item_type IN ('TEXT', 'URL', 'CODE', 'PATH', NULL)),
                is_favorite BOOLEAN,
                is_sensitive BOOLEAN,
                is_active_filter BOOLEAN,
                is_archived_filter BOOLEAN,
                search_text TEXT,
                date_from TEXT,
                date_to TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,

                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
            )
        """)

        # Índices para smart_collections
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_smart_collections_name
            ON smart_collections(name)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_smart_collections_active
            ON smart_collections(is_active)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_smart_collections_category
            ON smart_collections(category_id)
        """)

        logger.info("Table smart_collections created successfully")

        # ========== DATOS DE EJEMPLO (OPCIONALES) ==========
        # Crear algunos Tag Groups predefinidos
        logger.info("Inserting sample data...")

        sample_tag_groups = [
            ("Python Backend", "Proyectos backend con Python/FastAPI", "python,fastapi,api,pydantic,uvicorn,database", "#3776ab", "🐍"),
            ("Laravel API", "APIs con Laravel y PHP", "laravel,php,mysql,api,eloquent,blade", "#ff2d20", "🔴"),
            ("React Frontend", "Proyectos frontend con React", "react,javascript,jsx,hooks,tailwind,frontend", "#61dafb", "⚛️"),
            ("Docker Deploy", "Deployment con Docker y Kubernetes", "docker,kubernetes,deployment,nginx,production", "#2496ed", "🐳"),
            ("Git Commands", "Comandos de Git", "git,version-control,github,gitlab", "#f05032", "📦"),
        ]

        for name, desc, tags, color, icon in sample_tag_groups:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO tag_groups (name, description, tags, color, icon)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, desc, tags, color, icon))
            except sqlite3.IntegrityError:
                logger.debug(f"Tag group '{name}' already exists, skipping")

        # Crear algunas Smart Collections predefinidas
        sample_collections = [
            ("Todos los Comandos", "Todos los items de tipo CODE", "⚡", "#ffaa00", None, None, None, "CODE"),
            ("Todas las URLs", "Todos los items de tipo URL", "🔗", "#00d4ff", None, None, None, "URL"),
            ("Favoritos", "Todos los items marcados como favoritos", "⭐", "#ffd700", None, None, None, None),
        ]

        for name, desc, icon, color, tags_inc, tags_exc, cat_id, item_type in sample_collections:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO smart_collections
                    (name, description, icon, color, tags_include, tags_exclude, category_id, item_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, desc, icon, color, tags_inc, tags_exc, cat_id, item_type))

                # Si es la colección de favoritos, agregar filtro is_favorite
                if name == "Favoritos":
                    cursor.execute("""
                        UPDATE smart_collections
                        SET is_favorite = 1
                        WHERE name = 'Favoritos'
                    """)
            except sqlite3.IntegrityError:
                logger.debug(f"Smart collection '{name}' already exists, skipping")

        # Commit cambios
        conn.commit()

        # Verificar que las tablas se crearon correctamente
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name IN ('tag_groups', 'smart_collections')
        """)
        tables = cursor.fetchall()

        if len(tables) == 2:
            logger.info("✅ Migration completed successfully!")
            logger.info("   - tag_groups table created")
            logger.info("   - smart_collections table created")
            logger.info("   - Sample data inserted")

            # Mostrar estadísticas
            cursor.execute("SELECT COUNT(*) FROM tag_groups")
            tag_groups_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM smart_collections")
            collections_count = cursor.fetchone()[0]

            logger.info(f"   - {tag_groups_count} tag groups initialized")
            logger.info(f"   - {collections_count} smart collections initialized")

            conn.close()
            return True
        else:
            logger.error("❌ Migration failed: Tables were not created")
            conn.close()
            return False

    except Exception as e:
        logger.error(f"❌ Migration failed with error: {e}", exc_info=True)
        return False


def rollback_migration(db_path: str) -> bool:
    """
    Revertir la migración (eliminar tablas)

    ADVERTENCIA: Esto eliminará TODOS los datos de tag_groups y smart_collections

    Args:
        db_path: Ruta al archivo de base de datos SQLite

    Returns:
        True si el rollback fue exitoso
    """
    try:
        logger.warning("⚠️  Rolling back migration: add_tag_groups_and_collections")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Eliminar tablas
        cursor.execute("DROP TABLE IF EXISTS smart_collections")
        cursor.execute("DROP TABLE IF EXISTS tag_groups")

        conn.commit()
        conn.close()

        logger.info("✅ Rollback completed successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Rollback failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    """
    Ejecutar migración directamente

    Uso:
        python -m src.database.migrations.add_tag_groups_and_collections
    """
    import sys
    from pathlib import Path

    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Determinar ruta de la base de datos
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # Por defecto, usar widget_sidebar.db en el directorio raíz del proyecto
        project_root = Path(__file__).parent.parent.parent.parent
        db_path = project_root / "widget_sidebar.db"

    logger.info(f"Database path: {db_path}")

    if not Path(db_path).exists():
        logger.error(f"❌ Database file not found: {db_path}")
        sys.exit(1)

    # Preguntar confirmación
    print("\n" + "="*60)
    print("  MIGRACIÓN: Tag Groups + Smart Collections")
    print("="*60)
    print(f"\nBase de datos: {db_path}")
    print("\nEsta migración creará:")
    print("  ✓ Tabla 'tag_groups' (plantillas de tags)")
    print("  ✓ Tabla 'smart_collections' (filtros guardados)")
    print("  ✓ Datos de ejemplo")
    print("\n⚠️  IMPORTANTE: Haz un backup de tu base de datos antes de continuar")

    response = input("\n¿Continuar con la migración? (s/n): ").lower().strip()

    if response == 's' or response == 'si' or response == 'yes' or response == 'y':
        success = migrate_add_tag_groups_and_collections(str(db_path))

        if success:
            print("\n✅ ¡Migración completada exitosamente!")
            sys.exit(0)
        else:
            print("\n❌ La migración falló. Revisa los logs para más información.")
            sys.exit(1)
    else:
        print("\n❌ Migración cancelada por el usuario")
        sys.exit(0)

"""
Script de Migración a Tag Groups
Normaliza tags existentes y crea Tag Groups automáticos
"""

import sqlite3
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from util.migrations.analyze_existing_tags import TagAnalyzer


class TagMigrator:
    """Migra tags existentes a sistema normalizado con Tag Groups"""

    def __init__(self, db_path: str, dry_run: bool = False):
        """
        Initialize the tag migrator

        Args:
            db_path: Path to SQLite database
            dry_run: If True, only show what would be done without applying changes
        """
        self.db_path = db_path
        self.dry_run = dry_run
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

        # Statistics
        self.stats = {
            'items_updated': 0,
            'tags_normalized': 0,
            'tag_groups_created': 0,
            'variations_fixed': 0
        }

        # Log of changes
        self.change_log = []

    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

    def log(self, message: str):
        """Log a change"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.change_log.append(log_entry)
        print(log_entry)

    def backup_database(self) -> bool:
        """
        Create backup of database before migration

        Returns:
            True if backup successful
        """
        if self.dry_run:
            self.log("🔵 DRY RUN: Would create database backup")
            return True

        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = Path(self.db_path).parent / f"widget_sidebar_backup_{timestamp}.db"

            shutil.copy2(self.db_path, backup_path)
            self.log(f"✅ Backup created: {backup_path}")
            return True

        except Exception as e:
            self.log(f"❌ Error creating backup: {e}")
            return False

    def normalize_tags_in_items(self, tag_case_variations: dict) -> int:
        """
        Normalize tags in all items (lowercase)

        Args:
            tag_case_variations: Dict mapping lowercase tag -> variations

        Returns:
            Number of items updated
        """
        self.log("\n📝 Normalizando tags en items...")

        # Get all items with tags
        cursor = self.conn.execute("""
            SELECT id, label, tags
            FROM items
            WHERE tags IS NOT NULL AND tags != ''
        """)
        items = cursor.fetchall()

        updated_count = 0

        for item in items:
            item_id = item['id']
            tags_str = item['tags']

            # Parse tags
            try:
                if tags_str.startswith('['):
                    tags = json.loads(tags_str)
                else:
                    tags = [t.strip() for t in tags_str.split(',') if t.strip()]
            except json.JSONDecodeError:
                tags = [t.strip() for t in tags_str.split(',') if t.strip()]

            # Normalize tags (lowercase, strip whitespace)
            normalized_tags = []
            changed = False

            for tag in tags:
                tag_clean = tag.strip()
                tag_normalized = tag_clean.lower()

                if tag_clean != tag_normalized:
                    changed = True
                    self.stats['variations_fixed'] += 1

                if tag_normalized and tag_normalized not in normalized_tags:
                    normalized_tags.append(tag_normalized)

            # Update if changed
            if changed or len(normalized_tags) != len(tags):
                # Store as JSON array
                new_tags_str = json.dumps(normalized_tags)

                if self.dry_run:
                    self.log(f"   🔵 Would update item {item_id}: {tags} → {normalized_tags}")
                else:
                    self.conn.execute(
                        "UPDATE items SET tags = ? WHERE id = ?",
                        (new_tags_str, item_id)
                    )
                    self.log(f"   ✅ Updated item {item_id} ({item['label'][:40]}): {len(normalized_tags)} tags")

                updated_count += 1

        if not self.dry_run:
            self.conn.commit()

        self.stats['items_updated'] = updated_count
        self.log(f"\n✅ Normalizados tags en {updated_count} items")

        return updated_count

    def create_tag_groups_from_suggestions(self, suggestions: list) -> int:
        """
        Create Tag Groups based on analysis suggestions

        Args:
            suggestions: List of suggested tag groups

        Returns:
            Number of tag groups created
        """
        self.log("\n🏷️  Creando Tag Groups automáticos...")

        created_count = 0

        # Icon mapping for common categories
        icon_map = {
            'python': '🐍',
            'javascript': '🟨',
            'react': '⚛️',
            'vue': '💚',
            'laravel': '🔴',
            'php': '🐘',
            'docker': '🐳',
            'database': '🗄️',
            'api': '🔌',
            'frontend': '🎨',
            'backend': '⚙️',
            'devops': '🚀',
            'git': '🌿'
        }

        # Color mapping
        color_map = {
            'python': '#3776ab',
            'javascript': '#f7df1e',
            'react': '#61dafb',
            'vue': '#42b883',
            'laravel': '#ff2d20',
            'php': '#777bb4',
            'docker': '#2496ed',
            'database': '#336791',
            'api': '#009688',
            'frontend': '#ff6f61',
            'backend': '#4caf50',
            'devops': '#ff9800',
            'git': '#f05032'
        }

        for suggestion in suggestions:
            name = suggestion['name']
            tags = suggestion['tags']
            category = suggestion.get('category', 'General')

            # Determine icon and color
            icon = '🏷️'
            color = '#007acc'

            # Try to find a matching icon based on tags
            for tag in tags:
                if tag in icon_map:
                    icon = icon_map[tag]
                    color = color_map.get(tag, '#007acc')
                    break

            # Check if group already exists
            cursor = self.conn.execute(
                "SELECT id FROM tag_groups WHERE name = ?",
                (name,)
            )
            existing = cursor.fetchone()

            if existing:
                self.log(f"   ⚠️  Tag Group '{name}' ya existe, saltando...")
                continue

            # Create tag group
            tags_str = ','.join(tags)
            description = f"Generado automáticamente desde categoría '{category}'"

            if self.dry_run:
                self.log(f"   🔵 Would create Tag Group: {name}")
                self.log(f"      Tags: {tags_str}")
                self.log(f"      Icon: {icon}, Color: {color}")
            else:
                self.conn.execute("""
                    INSERT INTO tag_groups (name, description, tags, icon, color)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, description, tags_str, icon, color))

                self.log(f"   ✅ Created Tag Group: {name}")
                self.log(f"      Tags: {tags_str}")
                self.log(f"      Icon: {icon}, Color: {color}")

            created_count += 1

        if not self.dry_run:
            self.conn.commit()

        self.stats['tag_groups_created'] = created_count
        self.log(f"\n✅ Creados {created_count} Tag Groups")

        return created_count

    def create_common_tag_groups(self):
        """Create some common useful tag groups manually"""
        self.log("\n🎯 Creando Tag Groups comunes predefinidos...")

        common_groups = [
            {
                'name': 'Python Backend',
                'tags': ['python', 'fastapi', 'django', 'flask', 'api', 'backend'],
                'icon': '🐍',
                'color': '#3776ab',
                'description': 'Desarrollo backend con Python'
            },
            {
                'name': 'JavaScript Frontend',
                'tags': ['javascript', 'react', 'vue', 'angular', 'frontend', 'ui'],
                'icon': '🟨',
                'color': '#f7df1e',
                'description': 'Desarrollo frontend con JavaScript'
            },
            {
                'name': 'Database',
                'tags': ['database', 'sql', 'mysql', 'postgresql', 'mongodb', 'orm'],
                'icon': '🗄️',
                'color': '#336791',
                'description': 'Trabajo con bases de datos'
            },
            {
                'name': 'DevOps',
                'tags': ['docker', 'kubernetes', 'ci-cd', 'deploy', 'nginx', 'devops'],
                'icon': '🚀',
                'color': '#ff9800',
                'description': 'DevOps y deployment'
            },
            {
                'name': 'Git & Version Control',
                'tags': ['git', 'github', 'gitlab', 'version-control', 'commit'],
                'icon': '🌿',
                'color': '#f05032',
                'description': 'Control de versiones con Git'
            },
            {
                'name': 'Testing',
                'tags': ['test', 'pytest', 'jest', 'unit-test', 'integration-test'],
                'icon': '✅',
                'color': '#4caf50',
                'description': 'Testing y QA'
            }
        ]

        created = 0
        for group in common_groups:
            # Check if exists
            cursor = self.conn.execute(
                "SELECT id FROM tag_groups WHERE name = ?",
                (group['name'],)
            )
            if cursor.fetchone():
                self.log(f"   ⚠️  Tag Group '{group['name']}' ya existe, saltando...")
                continue

            tags_str = ','.join(group['tags'])

            if self.dry_run:
                self.log(f"   🔵 Would create: {group['name']}")
            else:
                self.conn.execute("""
                    INSERT INTO tag_groups (name, description, tags, icon, color)
                    VALUES (?, ?, ?, ?, ?)
                """, (group['name'], group['description'], tags_str, group['icon'], group['color']))
                self.log(f"   ✅ Created: {group['name']}")

            created += 1

        if not self.dry_run and created > 0:
            self.conn.commit()

        self.stats['tag_groups_created'] += created
        self.log(f"\n✅ Creados {created} Tag Groups predefinidos")

    def generate_migration_report(self, output_path: str = None):
        """
        Generate migration report

        Args:
            output_path: Path to save report
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("REPORTE DE MIGRACIÓN A TAG GROUPS")
        report_lines.append(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if self.dry_run:
            report_lines.append("MODO: DRY RUN (no se aplicaron cambios)")
        else:
            report_lines.append("MODO: EJECUCIÓN REAL (cambios aplicados)")
        report_lines.append("=" * 80)
        report_lines.append("")

        # Statistics
        report_lines.append("📊 ESTADÍSTICAS")
        report_lines.append("-" * 80)
        report_lines.append(f"Items actualizados: {self.stats['items_updated']}")
        report_lines.append(f"Variaciones de tags corregidas: {self.stats['variations_fixed']}")
        report_lines.append(f"Tag Groups creados: {self.stats['tag_groups_created']}")
        report_lines.append("")

        # Change log
        report_lines.append("📝 LOG DE CAMBIOS")
        report_lines.append("-" * 80)
        for log_entry in self.change_log:
            report_lines.append(log_entry)
        report_lines.append("")

        report_lines.append("=" * 80)
        report_lines.append("FIN DEL REPORTE")
        report_lines.append("=" * 80)

        report = "\n".join(report_lines)

        # Save to file
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n✅ Reporte de migración guardado en: {output_path}")

        return report

    def migrate(self):
        """Execute full migration process"""
        self.log("=" * 80)
        self.log("🚀 INICIANDO MIGRACIÓN A TAG GROUPS")
        self.log("=" * 80)

        # Step 1: Backup
        if not self.backup_database():
            self.log("❌ No se pudo crear backup, abortando migración")
            return False

        # Step 2: Analyze current tags
        self.log("\n🔍 Analizando tags existentes...")
        analyzer = TagAnalyzer(self.db_path)
        analysis = analyzer.generate_report(output_path=None)  # Don't save intermediate report

        # Step 3: Normalize tags
        self.normalize_tags_in_items(analysis['stats']['tag_case_variations'])

        # Step 4: Create common tag groups
        self.create_common_tag_groups()

        # Step 5: Create tag groups from analysis
        if analysis['suggestions']:
            self.create_tag_groups_from_suggestions(analysis['suggestions'][:10])  # Top 10 suggestions

        # Step 6: Generate report
        report_path = project_root / "util" / "migrations" / "migration_report.txt"
        self.generate_migration_report(str(report_path))

        self.log("\n" + "=" * 80)
        if self.dry_run:
            self.log("✅ DRY RUN COMPLETADO - No se aplicaron cambios")
        else:
            self.log("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        self.log("=" * 80)

        return True


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Migrate existing tags to Tag Groups system')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without applying changes'
    )
    parser.add_argument(
        '--db-path',
        type=str,
        default=str(project_root / "widget_sidebar.db"),
        help='Path to database file'
    )

    args = parser.parse_args()

    # Check database exists
    db_path = Path(args.db_path)
    if not db_path.exists():
        print(f"❌ Error: Database not found at {db_path}")
        sys.exit(1)

    # Create migrator
    migrator = TagMigrator(str(db_path), dry_run=args.dry_run)

    # Run migration
    success = migrator.migrate()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

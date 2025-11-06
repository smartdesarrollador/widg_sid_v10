"""
Script de Análisis de Tags Existentes
Escanea todos los items en la base de datos y genera un reporte completo de tags
"""

import sqlite3
import sys
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TagAnalyzer:
    """Analiza tags existentes en la base de datos"""

    def __init__(self, db_path: str):
        """
        Initialize the tag analyzer

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

    def get_all_items(self):
        """Get all items from database"""
        cursor = self.conn.execute("""
            SELECT
                i.id,
                i.label,
                i.tags,
                i.item_type,
                i.category_id,
                c.name as category_name
            FROM items i
            LEFT JOIN categories c ON i.category_id = c.id
            WHERE i.tags IS NOT NULL AND i.tags != ''
        """)
        return cursor.fetchall()

    def extract_tags(self, items):
        """
        Extract all tags from items

        Returns:
            dict with tag statistics
        """
        # Statistics
        all_tags = []
        tags_by_category = defaultdict(list)
        tags_by_type = defaultdict(list)
        tag_case_variations = defaultdict(set)
        tag_item_mapping = defaultdict(list)  # tag -> [item_ids]

        for item in items:
            # Parse tags (stored as JSON array or comma-separated)
            tags_str = item['tags']
            try:
                # Try to parse as JSON first
                if tags_str.startswith('['):
                    tags = json.loads(tags_str)
                else:
                    # Fallback to comma-separated
                    tags = [t.strip() for t in tags_str.split(',') if t.strip()]
            except json.JSONDecodeError:
                # Fallback to comma-separated
                tags = [t.strip() for t in tags_str.split(',') if t.strip()]

            for tag in tags:
                tag_clean = tag.strip()
                if tag_clean:
                    all_tags.append(tag_clean)

                    # Track by category
                    if item['category_name']:
                        tags_by_category[item['category_name']].append(tag_clean)

                    # Track by type
                    tags_by_type[item['item_type']].append(tag_clean)

                    # Track case variations (python, Python, PYTHON)
                    tag_lower = tag_clean.lower()
                    tag_case_variations[tag_lower].add(tag_clean)

                    # Track tag->item mapping
                    tag_item_mapping[tag_lower].append(item['id'])

        # Count frequencies
        tag_counter = Counter(all_tags)
        tag_lower_counter = Counter([t.lower() for t in all_tags])

        return {
            'all_tags': all_tags,
            'tag_counter': tag_counter,
            'tag_lower_counter': tag_lower_counter,
            'tags_by_category': tags_by_category,
            'tags_by_type': tags_by_type,
            'tag_case_variations': tag_case_variations,
            'tag_item_mapping': tag_item_mapping,
            'total_items': len(items),
            'items_with_tags': len(items)
        }

    def detect_similar_tags(self, tag_case_variations):
        """
        Detect tags that are likely the same but with variations

        Returns:
            list of dictionaries with similar tags
        """
        similar_tags = []

        for tag_lower, variations in tag_case_variations.items():
            if len(variations) > 1:
                similar_tags.append({
                    'normalized': tag_lower,
                    'variations': sorted(list(variations)),
                    'count': len(variations)
                })

        # Sort by count (most variations first)
        similar_tags.sort(key=lambda x: x['count'], reverse=True)

        return similar_tags

    def suggest_tag_groups(self, tags_by_category, tag_lower_counter, min_tags=3):
        """
        Suggest tag groups based on category analysis

        Args:
            tags_by_category: Tags grouped by category
            tag_lower_counter: Tag frequency counter
            min_tags: Minimum number of tags to create a group

        Returns:
            list of suggested tag groups
        """
        suggestions = []

        for category, tags in tags_by_category.items():
            # Count tag frequencies in this category
            category_tag_counter = Counter([t.lower() for t in tags])

            # Get most common tags (at least 2 occurrences)
            common_tags = [tag for tag, count in category_tag_counter.items() if count >= 2]

            if len(common_tags) >= min_tags:
                suggestions.append({
                    'name': f"{category} - Auto",
                    'category': category,
                    'tags': sorted(common_tags[:15]),  # Limit to 15 tags
                    'tag_count': len(common_tags),
                    'usage_score': sum(category_tag_counter.values())
                })

        # Sort by usage score
        suggestions.sort(key=lambda x: x['usage_score'], reverse=True)

        return suggestions

    def generate_report(self, output_path: str = None):
        """
        Generate comprehensive analysis report

        Args:
            output_path: Path to save report (optional)
        """
        print("🔍 Analyzing tags in database...")

        # Get all items
        items = self.get_all_items()
        print(f"   Found {len(items)} items with tags")

        # Extract and analyze tags
        stats = self.extract_tags(items)

        # Detect similar tags
        similar_tags = self.detect_similar_tags(stats['tag_case_variations'])

        # Suggest tag groups
        suggestions = self.suggest_tag_groups(
            stats['tags_by_category'],
            stats['tag_lower_counter']
        )

        # Generate report
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("ANÁLISIS DE TAGS EXISTENTES")
        report_lines.append(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 80)
        report_lines.append("")

        # Summary
        report_lines.append("📊 RESUMEN GENERAL")
        report_lines.append("-" * 80)
        report_lines.append(f"Total de items analizados: {stats['total_items']}")
        report_lines.append(f"Items con tags: {stats['items_with_tags']}")
        report_lines.append(f"Total de tags (con duplicados): {len(stats['all_tags'])}")
        report_lines.append(f"Tags únicos (case-sensitive): {len(stats['tag_counter'])}")
        report_lines.append(f"Tags únicos (normalizados): {len(stats['tag_lower_counter'])}")
        report_lines.append("")

        # Most common tags
        report_lines.append("🏆 TOP 20 TAGS MÁS USADOS")
        report_lines.append("-" * 80)
        for tag, count in stats['tag_lower_counter'].most_common(20):
            report_lines.append(f"  {tag:30s} → {count:3d} items")
        report_lines.append("")

        # Similar tags (variations)
        if similar_tags:
            report_lines.append("⚠️  TAGS CON VARIACIONES DE MAYÚSCULAS/MINÚSCULAS")
            report_lines.append("-" * 80)
            report_lines.append("Estos tags deberían normalizarse:")
            report_lines.append("")
            for similar in similar_tags[:20]:  # Show top 20
                report_lines.append(f"  {similar['normalized']}:")
                report_lines.append(f"    Variaciones: {', '.join(similar['variations'])}")
                report_lines.append("")

        # Tags by category
        report_lines.append("📁 TAGS POR CATEGORÍA")
        report_lines.append("-" * 80)
        for category, tags in sorted(stats['tags_by_category'].items()):
            category_tag_counter = Counter([t.lower() for t in tags])
            report_lines.append(f"\n{category}:")
            report_lines.append(f"  Total tags: {len(tags)}")
            report_lines.append(f"  Tags únicos: {len(category_tag_counter)}")
            report_lines.append(f"  Top 10 tags:")
            for tag, count in category_tag_counter.most_common(10):
                report_lines.append(f"    - {tag} ({count} items)")
        report_lines.append("")

        # Tags by type
        report_lines.append("📋 TAGS POR TIPO DE ITEM")
        report_lines.append("-" * 80)
        for item_type, tags in sorted(stats['tags_by_type'].items()):
            type_tag_counter = Counter([t.lower() for t in tags])
            report_lines.append(f"\n{item_type}:")
            report_lines.append(f"  Total tags: {len(tags)}")
            report_lines.append(f"  Tags únicos: {len(type_tag_counter)}")
            report_lines.append(f"  Top 10 tags:")
            for tag, count in type_tag_counter.most_common(10):
                report_lines.append(f"    - {tag} ({count} items)")
        report_lines.append("")

        # Suggestions for tag groups
        if suggestions:
            report_lines.append("💡 SUGERENCIAS DE TAG GROUPS")
            report_lines.append("-" * 80)
            report_lines.append("Grupos de tags sugeridos basados en análisis de categorías:")
            report_lines.append("")
            for i, suggestion in enumerate(suggestions, 1):
                report_lines.append(f"{i}. {suggestion['name']}")
                report_lines.append(f"   Categoría: {suggestion['category']}")
                report_lines.append(f"   Tags sugeridos ({len(suggestion['tags'])}): {', '.join(suggestion['tags'])}")
                report_lines.append(f"   Score de uso: {suggestion['usage_score']}")
                report_lines.append("")

        # Recommendations
        report_lines.append("🎯 RECOMENDACIONES")
        report_lines.append("-" * 80)
        report_lines.append("1. Normalizar tags para eliminar variaciones de mayúsculas/minúsculas")
        report_lines.append(f"   → Se detectaron {len(similar_tags)} tags con variaciones")
        report_lines.append("")
        report_lines.append("2. Crear Tag Groups basados en las sugerencias anteriores")
        report_lines.append(f"   → Se sugieren {len(suggestions)} grupos automáticos")
        report_lines.append("")
        report_lines.append("3. Considerar agrupar tags relacionados semánticamente")
        report_lines.append("   → Ejemplo: 'python', 'fastapi', 'api' → 'Python Backend'")
        report_lines.append("")
        report_lines.append("4. Ejecutar script de migración para aplicar normalizaciones")
        report_lines.append("   → python util/migrations/migrate_to_tag_groups.py")
        report_lines.append("")

        report_lines.append("=" * 80)
        report_lines.append("FIN DEL REPORTE")
        report_lines.append("=" * 80)

        # Join all lines
        report = "\n".join(report_lines)

        # Print to console
        print("\n" + report)

        # Save to file
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n✅ Reporte guardado en: {output_path}")

        # Return stats for programmatic use
        return {
            'stats': stats,
            'similar_tags': similar_tags,
            'suggestions': suggestions,
            'report': report
        }


def main():
    """Main entry point"""
    # Get database path
    db_path = project_root / "widget_sidebar.db"

    if not db_path.exists():
        print(f"❌ Error: Database not found at {db_path}")
        sys.exit(1)

    # Create analyzer
    analyzer = TagAnalyzer(str(db_path))

    # Generate report
    output_path = project_root / "util" / "migrations" / "tags_analysis_report.txt"
    analyzer.generate_report(str(output_path))


if __name__ == "__main__":
    main()

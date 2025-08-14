#!/usr/bin/env python3
"""
Script Inventory Analyzer
Purpose: Deep analysis of script categories and dependencies
Status: [ACTIVE]
Created: 2025-01-27
Author: writeian

Usage:
    python analyze_inventory.py

Output:
    - Detailed category analysis
    - Dependency mapping
    - Consolidation recommendations
    - Reorganization plan
"""

import yaml
import json
from collections import defaultdict, Counter
from pathlib import Path

class InventoryAnalyzer:
    def __init__(self):
        self.inventory_file = "scripts_inventory.yaml"
        self.analysis_file = "inventory_analysis.yaml"
        self.inventory_data = None
        self.scripts = []
        
    def load_inventory(self):
        """Load the generated inventory"""
        try:
            with open(self.inventory_file, 'r', encoding='utf-8') as f:
                self.inventory_data = yaml.safe_load(f)
            self.scripts = self.inventory_data['scripts']
            print(f"✅ Loaded inventory with {len(self.scripts)} scripts")
            return True
        except Exception as e:
            print(f"❌ Error loading inventory: {e}")
            return False
    
    def analyze_categories(self):
        """Deep analysis of script categories"""
        print("\n🔍 Analyzing script categories...")
        
        category_analysis = {
            "by_category": defaultdict(list),
            "by_subcategory": defaultdict(list),
            "category_stats": {},
            "consolidation_opportunities": [],
            "category_dependencies": defaultdict(set)
        }
        
        # Group scripts by category and subcategory
        for script in self.scripts:
            category = script['category']
            subcategory = script['subcategory']
            full_category = f"{category}/{subcategory}"
            
            category_analysis["by_category"][category].append(script)
            category_analysis["by_subcategory"][full_category].append(script)
            
            # Track dependencies for each category
            for dep in script['dependencies']:
                category_analysis["category_dependencies"][full_category].add(dep)
        
        # Calculate statistics for each category
        for category, scripts in category_analysis["by_category"].items():
            total_size = sum(s['size_kb'] for s in scripts)
            total_lines = sum(s['lines']['total'] for s in scripts)
            avg_size = total_size / len(scripts) if scripts else 0
            
            category_analysis["category_stats"][category] = {
                "count": len(scripts),
                "total_size_kb": total_size,
                "total_lines": total_lines,
                "avg_size_kb": avg_size,
                "status_distribution": Counter(s['status'] for s in scripts),
                "subcategories": list(set(s['subcategory'] for s in scripts))
            }
        
        # Find consolidation opportunities
        for full_category, scripts in category_analysis["by_subcategory"].items():
            if len(scripts) >= 5:  # More than 5 scripts in same subcategory
                category_analysis["consolidation_opportunities"].append({
                    "category": full_category,
                    "count": len(scripts),
                    "total_size_kb": sum(s['size_kb'] for s in scripts),
                    "scripts": [s['name'] for s in scripts],
                    "status_distribution": Counter(s['status'] for s in scripts)
                })
        
        return category_analysis
    
    def analyze_dependencies(self):
        """Deep analysis of script dependencies"""
        print("🔗 Analyzing dependencies...")
        
        dependency_analysis = {
            "dependency_graph": defaultdict(set),
            "reverse_dependencies": defaultdict(set),
            "dependency_stats": {},
            "circular_dependencies": [],
            "orphaned_scripts": [],
            "highly_dependent_scripts": []
        }
        
        # Build dependency graph
        for script in self.scripts:
            script_name = script['name']
            for dep in script['dependencies']:
                dependency_analysis["dependency_graph"][script_name].add(dep)
                dependency_analysis["reverse_dependencies"][dep].add(script_name)
        
        # Find orphaned scripts (no dependencies on them)
        all_scripts = {s['name'] for s in self.scripts}
        all_dependencies = set()
        for deps in dependency_analysis["dependency_graph"].values():
            all_dependencies.update(deps)
        
        orphaned = all_scripts - all_dependencies
        dependency_analysis["orphaned_scripts"] = list(orphaned)
        
        # Find highly dependent scripts
        dependency_counts = {name: len(deps) for name, deps in dependency_analysis["reverse_dependencies"].items()}
        highly_dependent = sorted(dependency_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        dependency_analysis["highly_dependent_scripts"] = highly_dependent
        
        # Calculate dependency statistics
        dependency_analysis["dependency_stats"] = {
            "total_unique_dependencies": len(all_dependencies),
            "avg_dependencies_per_script": len(all_dependencies) / len(self.scripts) if self.scripts else 0,
            "most_common_dependencies": Counter(all_dependencies).most_common(10),
            "scripts_with_most_dependencies": sorted(
                [(s['name'], len(s['dependencies'])) for s in self.scripts],
                key=lambda x: x[1], reverse=True
            )[:10]
        }
        
        return dependency_analysis
    
    def analyze_test_scripts(self):
        """Special analysis for test scripts"""
        print("🧪 Analyzing test scripts...")
        
        test_analysis = {
            "test_categories": defaultdict(list),
            "test_patterns": {},
            "test_consolidation": [],
            "test_coverage": {}
        }
        
        test_scripts = [s for s in self.scripts if s['category'] == 'testing']
        
        # Group by subcategory
        for script in test_scripts:
            subcategory = script['subcategory']
            test_analysis["test_categories"][subcategory].append(script)
        
        # Analyze test patterns
        for subcategory, scripts in test_analysis["test_categories"].items():
            test_analysis["test_patterns"][subcategory] = {
                "count": len(scripts),
                "total_size_kb": sum(s['size_kb'] for s in scripts),
                "avg_size_kb": sum(s['size_kb'] for s in scripts) / len(scripts) if scripts else 0,
                "common_prefixes": self.find_common_prefixes([s['name'] for s in scripts]),
                "status_distribution": Counter(s['status'] for s in scripts)
            }
        
        # Find test consolidation opportunities
        for subcategory, scripts in test_analysis["test_categories"].items():
            if len(scripts) >= 3:  # More than 3 test scripts in same category
                test_analysis["test_consolidation"].append({
                    "subcategory": subcategory,
                    "count": len(scripts),
                    "scripts": [s['name'] for s in scripts],
                    "suggested_consolidation": self.suggest_test_consolidation(scripts)
                })
        
        return test_analysis
    
    def find_common_prefixes(self, filenames):
        """Find common prefixes in filenames"""
        if not filenames:
            return []
        
        # Find common prefixes
        prefixes = defaultdict(int)
        for filename in filenames:
            parts = filename.replace('.py', '').split('_')
            for i in range(1, len(parts) + 1):
                prefix = '_'.join(parts[:i])
                prefixes[prefix] += 1
        
        # Return prefixes that appear in multiple files
        return [prefix for prefix, count in prefixes.items() if count > 1]
    
    def suggest_test_consolidation(self, scripts):
        """Suggest how to consolidate test scripts"""
        suggestions = []
        
        # Group by common prefixes
        prefix_groups = defaultdict(list)
        for script in scripts:
            name = script['name'].replace('.py', '')
            parts = name.split('_')
            if len(parts) >= 2:
                prefix = '_'.join(parts[:2])  # First two parts
                prefix_groups[prefix].append(script)
        
        for prefix, group in prefix_groups.items():
            if len(group) >= 2:
                suggestions.append({
                    "type": "prefix_group",
                    "prefix": prefix,
                    "count": len(group),
                    "scripts": [s['name'] for s in group],
                    "suggestion": f"Consolidate into {prefix}_tests.py"
                })
        
        return suggestions
    
    def generate_reorganization_plan(self, category_analysis, dependency_analysis, test_analysis):
        """Generate a detailed reorganization plan"""
        print("📋 Generating reorganization plan...")
        
        plan = {
            "phase_1_immediate_actions": [],
            "phase_2_consolidation": [],
            "phase_3_reorganization": [],
            "new_directory_structure": {},
            "estimated_impact": {}
        }
        
        # Phase 1: Immediate actions
        plan["phase_1_immediate_actions"] = [
            "Archive 80 identified scripts",
            "Remove 7 duplicate scripts",
            "Add documentation to 23 scripts",
            "Create archive directory structure"
        ]
        
        # Phase 2: Consolidation
        for opportunity in category_analysis["consolidation_opportunities"]:
            plan["phase_2_consolidation"].append({
                "category": opportunity["category"],
                "action": f"Consolidate {opportunity['count']} scripts",
                "scripts": opportunity["scripts"][:5],  # Show first 5
                "estimated_savings": f"{opportunity['total_size_kb']:.1f} KB"
            })
        
        # Phase 3: Reorganization
        plan["phase_3_reorganization"] = [
            "Create src/ directory for core application",
            "Create tests/ directory with subcategories",
            "Create scripts/ directory for utilities",
            "Create tools/ directory for one-off scripts",
            "Update import statements across project"
        ]
        
        # New directory structure
        plan["new_directory_structure"] = {
            "src/": {
                "core/": ["app.py", "models.py", "config.py"],
                "blueprints/": ["auth.py", "room.py", "chat.py", "dashboard.py"],
                "ai/": ["openai_utils/", "rubric_templates.py"],
                "utils/": ["git_helper.py", "simple_test.py"]
            },
            "tests/": {
                "unit/": "Unit tests",
                "integration/": "Integration tests",
                "ui/": "UI tests",
                "mobile/": "Mobile tests",
                "ai/": "AI integration tests"
            },
            "scripts/": {
                "dev/": "Development utilities",
                "deploy/": "Deployment scripts",
                "maintenance/": "Maintenance scripts"
            },
            "tools/": "One-off tools and utilities",
            "archive/": "Archived scripts by date"
        }
        
        # Estimated impact
        total_scripts = len(self.scripts)
        archive_candidates = len([s for s in self.scripts if s['status'] in ['archived', 'deprecated', 'duplicate']])
        
        plan["estimated_impact"] = {
            "scripts_before": total_scripts,
            "scripts_after_cleanup": total_scripts - archive_candidates,
            "reduction_percentage": (archive_candidates / total_scripts) * 100 if total_scripts > 0 else 0,
            "estimated_time_savings": "30-50% faster navigation",
            "maintenance_improvement": "Significantly easier maintenance"
        }
        
        return plan
    
    def save_analysis(self, category_analysis, dependency_analysis, test_analysis, reorganization_plan):
        """Save the complete analysis"""
        analysis_data = {
            "metadata": {
                "generated": "2025-01-27",
                "inventory_file": self.inventory_file,
                "total_scripts_analyzed": len(self.scripts)
            },
            "category_analysis": category_analysis,
            "dependency_analysis": dependency_analysis,
            "test_analysis": test_analysis,
            "reorganization_plan": reorganization_plan
        }
        
        with open(self.analysis_file, 'w', encoding='utf-8') as f:
            yaml.dump(analysis_data, f, default_flow_style=False, indent=2, allow_unicode=True)
        
        print(f"✅ Analysis saved to {self.analysis_file}")
    
    def print_analysis_summary(self, category_analysis, dependency_analysis, test_analysis, reorganization_plan):
        """Print analysis summary to console"""
        print("\n" + "="*80)
        print("📊 DETAILED INVENTORY ANALYSIS SUMMARY")
        print("="*80)
        
        # Category Analysis Summary
        print(f"\n📁 CATEGORY ANALYSIS:")
        for category, stats in category_analysis["category_stats"].items():
            print(f"   {category}:")
            print(f"     - Scripts: {stats['count']}")
            print(f"     - Size: {stats['total_size_kb']:.1f} KB")
            print(f"     - Lines: {stats['total_lines']:,}")
            print(f"     - Subcategories: {', '.join(stats['subcategories'])}")
        
        # Consolidation Opportunities
        print(f"\n🔧 CONSOLIDATION OPPORTUNITIES:")
        for opportunity in category_analysis["consolidation_opportunities"][:5]:
            print(f"   • {opportunity['category']}: {opportunity['count']} scripts ({opportunity['total_size_kb']:.1f} KB)")
        
        # Dependency Analysis Summary
        print(f"\n🔗 DEPENDENCY ANALYSIS:")
        print(f"   Total unique dependencies: {dependency_analysis['dependency_stats']['total_unique_dependencies']}")
        print(f"   Average dependencies per script: {dependency_analysis['dependency_stats']['avg_dependencies_per_script']:.1f}")
        print(f"   Orphaned scripts: {len(dependency_analysis['orphaned_scripts'])}")
        
        # Test Analysis Summary
        print(f"\n🧪 TEST SCRIPT ANALYSIS:")
        for subcategory, patterns in test_analysis["test_patterns"].items():
            print(f"   {subcategory}: {patterns['count']} tests ({patterns['total_size_kb']:.1f} KB)")
        
        # Reorganization Plan Summary
        print(f"\n📋 REORGANIZATION PLAN:")
        print(f"   Phase 1 Actions: {len(reorganization_plan['phase_1_immediate_actions'])}")
        print(f"   Consolidation Opportunities: {len(reorganization_plan['phase_2_consolidation'])}")
        print(f"   Estimated Reduction: {reorganization_plan['estimated_impact']['reduction_percentage']:.1f}%")
        
        print("\n" + "="*80)

def main():
    """Main function to run the analysis"""
    print("🚀 Starting Detailed Inventory Analysis...")
    
    analyzer = InventoryAnalyzer()
    
    if not analyzer.load_inventory():
        return
    
    # Run analyses
    category_analysis = analyzer.analyze_categories()
    dependency_analysis = analyzer.analyze_dependencies()
    test_analysis = analyzer.analyze_test_scripts()
    reorganization_plan = analyzer.generate_reorganization_plan(
        category_analysis, dependency_analysis, test_analysis
    )
    
    # Save and display results
    analyzer.save_analysis(category_analysis, dependency_analysis, test_analysis, reorganization_plan)
    analyzer.print_analysis_summary(category_analysis, dependency_analysis, test_analysis, reorganization_plan)
    
    print(f"\n✅ Detailed analysis complete!")
    print(f"📄 Full analysis saved to: {analyzer.analysis_file}")
    print(f"📋 Ready for Phase 1.3: Identify duplicate and unused scripts")

if __name__ == "__main__":
    main() 
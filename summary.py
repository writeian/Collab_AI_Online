#!/usr/bin/env python3
"""
summary.py
Purpose: [AUTO-GENERATED] Script purpose needs to be documented
Status: [UNKNOWN]
Created: 2025-08-14
Author: writeian

TODO: Add proper documentation for this script
"""

import json

# Load the analysis results
with open('duplicate_analysis.json', 'r') as f:
    data = json.load(f)

print("📊 DUPLICATE ANALYSIS RESULTS")
print("="*50)
print(f"Duplicate Groups: {len(data['duplicate_groups'])}")
print(f"Unused Scripts: {len(data['unused_scripts'])}")
print(f"Total Savings: {data['estimated_savings']['total'] / 1024:.1f} KB")
print(f"Duplicate Savings: {data['estimated_savings']['duplicates'] / 1024:.1f} KB")
print(f"Unused Savings: {data['estimated_savings']['unused'] / 1024:.1f} KB")
print(f"Recommendations: {data['recommendations']}") 
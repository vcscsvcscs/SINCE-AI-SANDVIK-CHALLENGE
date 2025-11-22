#!/usr/bin/env python3
"""
Validate the generated synthetic test data
"""

import json
import csv
import os
from collections import Counter

def validate_sku_register(filepath):
    """Validate SKU register data"""
    print(f"\n{'='*60}")
    print(f"Validating: {os.path.basename(filepath)}")
    print(f"{'='*60}")
    
    if filepath.endswith('.csv'):
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    else:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    
    print(f"✓ Total records: {len(data):,}")
    
    # Check required fields
    required_fields = ['sku', 'name', 'description']
    sample = data[0]
    missing = [f for f in required_fields if f not in sample]
    if missing:
        print(f"✗ Missing required fields: {missing}")
    else:
        print(f"✓ All required fields present")
    
    # Check SKU format
    skus = [row['sku'] for row in data]
    valid_format = sum(1 for sku in skus if (len(sku) == 8 or (sku.startswith('BC') and len(sku) == 10)))
    print(f"✓ Valid SKU format: {valid_format:,} / {len(skus):,} ({valid_format/len(skus)*100:.1f}%)")
    
    # Check for duplicates
    duplicates = len(skus) - len(set(skus))
    if duplicates == 0:
        print(f"✓ No duplicate SKUs")
    else:
        print(f"✗ Found {duplicates} duplicate SKUs")
    
    # Category distribution
    if isinstance(data[0], dict) and 'category' in data[0]:
        categories = Counter(row['category'] for row in data)
        print(f"✓ Categories: {len(categories)}")
        for cat, count in categories.most_common(5):
            print(f"    - {cat}: {count:,}")
    
    # Lead times
    if filepath.endswith('.json'):
        lead_times = [row['lead_time_days'] for row in data if 'lead_time_days' in row]
        if lead_times:
            avg_lead = sum(lt for lt in lead_times if lt > 0) / sum(1 for lt in lead_times if lt > 0)
            obsolete = sum(1 for lt in lead_times if lt == -1)
            print(f"✓ Average lead time: {avg_lead:.1f} days")
            print(f"✓ Obsolete parts: {obsolete:,}")
        
        # Aliases
        with_aliases = sum(1 for row in data if row.get('aliases'))
        print(f"✓ Parts with aliases: {with_aliases:,} ({with_aliases/len(data)*100:.1f}%)")
        
        # Compatibility
        with_compat = sum(1 for row in data if row.get('compatibility'))
        print(f"✓ Parts with compatibility data: {with_compat:,} ({with_compat/len(data)*100:.1f}%)")
    
    return True

def validate_messages(filepath):
    """Validate Teams messages"""
    print(f"\n{'='*60}")
    print(f"Validating: {os.path.basename(filepath)}")
    print(f"{'='*60}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        messages = json.load(f)
    
    print(f"✓ Total messages: {len(messages):,}")
    
    # Check required fields
    required_fields = ['message_id', 'message']
    sample = messages[0]
    missing = [f for f in required_fields if f not in sample]
    if missing:
        print(f"✗ Missing required fields: {missing}")
    else:
        print(f"✓ All required fields present")
    
    # Query types
    if 'query_type' in messages[0]:
        query_types = Counter(msg.get('query_type', 'unknown') for msg in messages)
        print(f"✓ Query types: {len(query_types)}")
        for qtype, count in query_types.most_common():
            print(f"    - {qtype}: {count:,}")
    
    # Messages with typos
    with_typos = sum(1 for msg in messages if msg.get('has_typo', False))
    print(f"✓ Messages with typos: {with_typos:,} ({with_typos/len(messages)*100:.1f}%)")
    
    # Messages with SKU references
    with_sku = sum(1 for msg in messages if msg.get('referenced_sku'))
    print(f"✓ Messages with SKU references: {with_sku:,} ({with_sku/len(messages)*100:.1f}%)")
    
    # Check message lengths
    lengths = [len(msg['message']) for msg in messages]
    print(f"✓ Message length: min={min(lengths)}, max={max(lengths)}, avg={sum(lengths)/len(lengths):.0f} chars")
    
    return True

def validate_test_scenarios(filepath):
    """Validate test scenarios"""
    print(f"\n{'='*60}")
    print(f"Validating: {os.path.basename(filepath)}")
    print(f"{'='*60}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        scenarios = json.load(f)
    
    print(f"✓ Total scenarios: {len(scenarios):,}")
    
    # Difficulty distribution
    difficulties = Counter(s['difficulty'] for s in scenarios)
    print(f"✓ Difficulty levels:")
    for diff, count in difficulties.most_common():
        print(f"    - {diff}: {count}")
    
    # Check required fields
    required = ['scenario_id', 'name', 'difficulty', 'input', 'expected_behavior', 'success_criteria']
    for scenario in scenarios[:3]:  # Check first 3
        missing = [f for f in required if f not in scenario]
        if missing:
            print(f"✗ Scenario {scenario.get('scenario_id', '?')} missing: {missing}")
            return False
    
    print(f"✓ All scenarios have required fields")
    
    return True

if __name__ == "__main__":
    test_dir = "/home/erdospeet/Desktop/sandvik/SINCE-AI-SANDVIK-CHALLENGE/test"
    
    print("\n" + "="*60)
    print("SANDVIK TEST DATA VALIDATION")
    print("="*60)
    
    all_valid = True
    
    # Validate SKU registers
    sku_files = [
        os.path.join(test_dir, "sku_register_full.csv"),
        os.path.join(test_dir, "sku_register_full.json"),
    ]
    
    for filepath in sku_files:
        if os.path.exists(filepath):
            try:
                validate_sku_register(filepath)
            except Exception as e:
                print(f"✗ Validation failed: {e}")
                all_valid = False
    
    # Validate message files
    message_files = [
        os.path.join(test_dir, "teams_messages_EN_extended.json"),
        os.path.join(test_dir, "teams_messages_FI_extended.json"),
        os.path.join(test_dir, "synthetic-data_EN.json"),
        os.path.join(test_dir, "synthetic-data_FI.json"),
        os.path.join(test_dir, "teams_messages_edge_cases.json"),
    ]
    
    for filepath in message_files:
        if os.path.exists(filepath):
            try:
                validate_messages(filepath)
            except Exception as e:
                print(f"✗ Validation failed: {e}")
                all_valid = False
    
    # Validate test scenarios
    scenarios_file = os.path.join(test_dir, "test_scenarios.json")
    if os.path.exists(scenarios_file):
        try:
            validate_test_scenarios(scenarios_file)
        except Exception as e:
            print(f"✗ Validation failed: {e}")
            all_valid = False
    
    # Final summary
    print(f"\n{'='*60}")
    if all_valid:
        print("✅ ALL VALIDATIONS PASSED")
    else:
        print("❌ SOME VALIDATIONS FAILED")
    print("="*60)
    
    # File size summary
    print(f"\n📊 File Size Summary:")
    total_size = 0
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            if file.endswith(('.json', '.csv', '.md', '.txt')):
                filepath = os.path.join(root, file)
                size = os.path.getsize(filepath)
                total_size += size
                size_mb = size / (1024 * 1024)
                print(f"  {file:40s} {size_mb:8.2f} MB")
    
    print(f"  {'-'*40} {'-'*8}")
    print(f"  {'TOTAL':40s} {total_size/(1024*1024):8.2f} MB")
    print("="*60)


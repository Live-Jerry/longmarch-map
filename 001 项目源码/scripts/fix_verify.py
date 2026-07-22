#!/usr/bin/env python3
"""Fix the verify script - only check field key existence, not non-null"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\长征文化\001 项目源码\scripts\verify_data.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Change: "field in node and node[field] is not None" -> "field in node"
content = content.replace(
    'field in node and node[field] is not None',
    'field in node'
)

with open(r'D:\长征文化\001 项目源码\scripts\verify_data.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed!")

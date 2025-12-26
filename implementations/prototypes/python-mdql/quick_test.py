#!/usr/bin/env python3
"""Quick demonstration of MDQL queries on todo-test.md"""

import os
from mdql import MDQL

# Load the test file
todo_path = os.path.join(os.path.dirname(__file__), "../../../samples/notes-app/todo-test.md")
mdql = MDQL(todo_path)

print("=" * 80)
print("MDQL Query Demonstration on todo-test.md")
print("=" * 80)

# Query 1: All high-priority tasks
print("\n1️⃣  HIGH PRIORITY INCOMPLETE TASKS:\n")
high_priority = mdql.query(priority="High", completed=False, indent_level=0)
for i, task in enumerate(high_priority[:10], 1):
    print(f"   {i}. [{task.section[:30]}...] {task.text[:50]}...")

# Query 2: Tasks by specific section
print("\n2️⃣  OPEN MOSQUE PROJECT TASKS:\n")
open_mosque = mdql.query(section="Open Mosque Project")
for task in open_mosque:
    status = "✓" if task.completed else "☐"
    print(f"   {status} {task.text}")

# Query 3: Completed tasks
print("\n3️⃣  COMPLETED TASKS:\n")
completed = mdql.query(completed=True)
for task in completed:
    print(f"   ✓ {task.text}")
    print(f"      Section: {task.section}")

# Query 4: Search by text
print("\n4️⃣  TASKS CONTAINING 'camera':\n")
camera_tasks = mdql.query(text_contains="camera")
for task in camera_tasks:
    status = "✓" if task.completed else "☐"
    print(f"   {status} {task.text}")

# Section summary
print("\n5️⃣  TOP SECTIONS BY TASK COUNT:\n")
summary = mdql.get_section_summary()
summary_sorted = sorted(summary, key=lambda x: x['total_tasks'], reverse=True)

for item in summary_sorted[:5]:
    print(f"   {item['section'][:40]}")
    print(f"      Tasks: {item['completed']}/{item['total_tasks']} ({item['completion_pct']}%)")
    if item['priority']:
        print(f"      Priority: {item['priority']}")

print("\n" + "=" * 80)
print("✅ All queries executed successfully!")
print("=" * 80)

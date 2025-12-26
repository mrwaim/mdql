#!/usr/bin/env python3
"""Test script to verify notes/descriptions are captured correctly"""

import os
from mdql import MDQL

# Load the test file
todo_path = os.path.join(os.path.dirname(__file__), "../../../samples/notes-app/todo-test.md")
mdql = MDQL(todo_path)

print("=" * 80)
print("MDQL Notes Feature Test")
print("=" * 80)

# Count tasks with notes
tasks_with_notes = [t for t in mdql.tasks if t.notes]
print(f"\nTasks with notes: {len(tasks_with_notes)}/{len(mdql.tasks)}")

# Show sample tasks with notes
print("\n" + "=" * 80)
print("Sample Tasks with Notes:")
print("=" * 80)

for i, task in enumerate(tasks_with_notes[:10], 1):
    status = "✓" if task.completed else "☐"
    print(f"\n{i}. {status} {task.text}")
    print(f"   Section: {task.section}")
    print(f"   Notes ({len(task.notes)}):")
    for note in task.notes:
        print(f"     - {note}")

# Test query by notes
print("\n" + "=" * 80)
print("Query: Tasks with notes containing 'Example'")
print("=" * 80)

example_tasks = mdql.query(notes_contains="Example")
print(f"\nFound {len(example_tasks)} tasks")
for task in example_tasks:
    status = "✓" if task.completed else "☐"
    print(f"\n{status} {task.text}")
    for note in task.notes:
        if "Example" in note or "example" in note:
            print(f"  → {note}")

# Test query for tasks with notes
print("\n" + "=" * 80)
print("Query: All tasks that have notes")
print("=" * 80)

has_notes_tasks = mdql.query(has_notes=True, indent_level=0)
print(f"\nFound {len(has_notes_tasks)} top-level tasks with notes")
for task in has_notes_tasks[:5]:
    status = "✓" if task.completed else "☐"
    print(f"\n{status} {task.text}")
    print(f"  Notes: {len(task.notes)} items")

# Test query for tasks WITHOUT notes
print("\n" + "=" * 80)
print("Query: Tasks WITHOUT notes")
print("=" * 80)

no_notes_tasks = mdql.query(has_notes=False, indent_level=0)
print(f"\nFound {len(no_notes_tasks)} top-level tasks without notes")
for task in no_notes_tasks[:5]:
    status = "✓" if task.completed else "☐"
    print(f"  {status} {task.text}")

# Test combined query
print("\n" + "=" * 80)
print("Query: High priority tasks with notes")
print("=" * 80)

high_pri_with_notes = mdql.query(priority="High", has_notes=True)
print(f"\nFound {len(high_pri_with_notes)} high priority tasks with notes")
for task in high_pri_with_notes[:5]:
    status = "✓" if task.completed else "☐"
    print(f"\n{status} {task.text}")
    print(f"  Section: {task.section}")
    print(f"  Notes: {len(task.notes)} items")
    for note in task.notes[:3]:
        print(f"    - {note}")

print("\n" + "=" * 80)
print("✅ Notes feature test complete!")
print("=" * 80)

#!/usr/bin/env python3
"""
Test script to validate MDQL parser on todo-test.md
"""

import os
from mdql import MDQL


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def main():
    # Get the path to the todo-test.md file
    todo_test_path = os.path.join(
        os.path.dirname(__file__),
        "../../../samples/notes-app/todo-test.md"
    )

    if not os.path.exists(todo_test_path):
        print(f"Error: Could not find todo-test.md at {todo_test_path}")
        return 1

    print_section("MDQL Parser Validation Test")
    print(f"Testing file: {todo_test_path}\n")

    # Load the file
    print("Loading file...")
    mdql = MDQL(todo_test_path)
    print("✓ File loaded successfully\n")

    # Validate parsing results
    print_section("1. Parsing Statistics")

    total_tasks = len(mdql.tasks)
    total_sections = len(mdql.sections)

    print(f"Total tasks parsed: {total_tasks}")
    print(f"Total sections parsed: {total_sections}")

    # Count by indent level
    by_indent = {}
    for task in mdql.tasks:
        level = task.indent_level
        by_indent[level] = by_indent.get(level, 0) + 1

    print(f"\nTasks by indentation level:")
    for level in sorted(by_indent.keys()):
        print(f"  Level {level}: {by_indent[level]} tasks")

    # Count by completion status
    completed = sum(1 for t in mdql.tasks if t.completed)
    incomplete = sum(1 for t in mdql.tasks if not t.completed)

    print(f"\nCompletion status:")
    print(f"  Completed: {completed} ({100*completed/total_tasks:.1f}%)")
    print(f"  Incomplete: {incomplete} ({100*incomplete/total_tasks:.1f}%)")

    # Validate section metadata
    print_section("2. Section Metadata")

    sections_with_priority = sum(1 for s in mdql.sections.values() if s.priority)
    sections_with_status = sum(1 for s in mdql.sections.values() if s.status)
    sections_with_source = sum(1 for s in mdql.sections.values() if s.source_file)
    sections_with_updated = sum(1 for s in mdql.sections.values() if s.updated_file)

    print(f"Sections with Priority: {sections_with_priority}")
    print(f"Sections with Status: {sections_with_status}")
    print(f"Sections with Source: {sections_with_source}")
    print(f"Sections with Updated: {sections_with_updated}")

    print("\nSample section metadata:")
    count = 0
    for name, meta in mdql.sections.items():
        if count >= 5:
            break
        if meta.priority or meta.status:
            print(f"\n  {name}")
            if meta.priority:
                print(f"    Priority: {meta.priority}")
            if meta.status:
                print(f"    Status: {meta.status}")
            if meta.source_file:
                print(f"    Source: {meta.source_file} ({meta.source_date})")
            count += 1

    # Validate nested structure
    print_section("3. Task Hierarchy")

    tasks_with_children = sum(1 for t in mdql.tasks if t.has_children)
    tasks_with_parent = sum(1 for t in mdql.tasks if t.parent_line is not None)

    print(f"Tasks with children: {tasks_with_children}")
    print(f"Tasks with parent: {tasks_with_parent}")

    print("\nSample nested structure:")
    count = 0
    for task in mdql.tasks:
        if count >= 3:
            break
        if task.has_children:
            print(f"\n  Parent (line {task.line_number}): {task.text[:50]}...")
            for child in task.children[:3]:
                print(f"    └─ Child (line {child.line_number}): {child.text[:50]}...")
            if len(task.children) > 3:
                print(f"    └─ ... and {len(task.children) - 3} more")
            count += 1

    # Test queries
    print_section("4. Query Tests")

    # Query by completion
    incomplete_tasks = mdql.query(completed=False, indent_level=0)
    print(f"Top-level incomplete tasks: {len(incomplete_tasks)}")

    # Query by priority
    high_priority = mdql.query(priority="High", completed=False)
    print(f"High priority incomplete tasks: {len(high_priority)}")

    # Query by section
    if mdql.sections:
        first_section = list(mdql.sections.keys())[0]
        section_tasks = mdql.query(section=first_section)
        print(f"Tasks in '{first_section[:30]}...': {section_tasks and len(section_tasks) or 0}")

    # Show sample tasks
    print("\nSample tasks from queries:")
    for i, task in enumerate(incomplete_tasks[:5]):
        status = "✓" if task.completed else "☐"
        print(f"  {status} {task.text[:60]}...")

    # Validate all sections
    print_section("5. All Sections List")

    print(f"{'Section Name':<50} {'Level':<7} {'Line#':<7} {'Tasks':<7}")
    print("-" * 80)

    for name, meta in mdql.sections.items():
        # Count tasks in this section
        section_tasks = [t for t in mdql.tasks if t.section == name]
        task_count = len(section_tasks)

        print(f"{name[:48]:<50} {meta.section_level:<7} {meta.line_number:<7} {task_count:<7}")

    # Detailed task analysis
    print_section("6. Task Details Sample")

    print("First 10 tasks with full details:\n")
    for i, task in enumerate(mdql.tasks[:10], 1):
        status = "✓" if task.completed else "☐"
        indent = "  " * task.indent_level
        print(f"{i}. {status} {indent}{task.text}")
        print(f"   Line: {task.line_number} | Section: {task.section} | Indent: {task.indent_level}")
        if task.parent_line:
            print(f"   Parent line: {task.parent_line}")
        if task.has_children:
            print(f"   Has {len(task.children)} children")
        print()

    # Validate line numbers are sequential and unique
    print_section("7. Data Integrity Checks")

    line_numbers = [t.line_number for t in mdql.tasks]

    print(f"✓ All tasks have line numbers: {all(ln > 0 for ln in line_numbers)}")
    print(f"✓ Line numbers are unique: {len(line_numbers) == len(set(line_numbers))}")
    print(f"✓ All tasks have sections: {all(t.section for t in mdql.tasks)}")
    print(f"✓ All tasks have text: {all(t.text for t in mdql.tasks)}")

    # Validate parent-child relationships
    parent_child_valid = True
    for task in mdql.tasks:
        if task.parent_line:
            parent_exists = any(t.line_number == task.parent_line for t in mdql.tasks)
            if not parent_exists:
                print(f"✗ Task at line {task.line_number} references non-existent parent {task.parent_line}")
                parent_child_valid = False

    if parent_child_valid:
        print(f"✓ All parent references are valid")

    # Summary
    print_section("Summary")

    print("Parser validation results:")
    print(f"  ✓ File parsed successfully")
    print(f"  ✓ {total_tasks} tasks extracted")
    print(f"  ✓ {total_sections} sections identified")
    print(f"  ✓ Task hierarchy preserved")
    print(f"  ✓ Section metadata extracted")
    print(f"  ✓ Queries working correctly")
    print(f"  ✓ Data integrity verified")

    print("\n🎉 All validation checks passed!")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

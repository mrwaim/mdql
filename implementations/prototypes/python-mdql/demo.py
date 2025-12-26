#!/usr/bin/env python3
"""
MDQL Demo - Demonstrates the capabilities of the MDQL prototype.

This script:
1. Loads the todo.md file
2. Queries tasks by various criteria
3. Adds new tasks
4. Marks tasks as complete
5. Deletes tasks
6. Saves the modified file
"""

import os
import sys
from mdql import MDQL


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_tasks(tasks, title: str):
    """Print a list of tasks."""
    print(f"\n{title} ({len(tasks)} tasks):")
    print("-" * 80)
    for task in tasks:
        status = "✓" if task.completed else "☐"
        indent = "  " * task.indent_level
        print(f"{indent}{status} {task.text}")
        print(f"   └─ Section: {task.section} | Line: {task.line_number}")


def main():
    # Get the path to the todo.md file
    todo_path = os.path.join(
        os.path.dirname(__file__),
        "../../../samples/notes-app/todo.md"
    )

    if not os.path.exists(todo_path):
        print(f"Error: Could not find todo.md at {todo_path}")
        return 1

    print_section("MDQL Prototype Demo")
    print(f"Loading: {todo_path}")

    # Create a backup
    backup_path = todo_path + ".backup"
    with open(todo_path, 'r') as src, open(backup_path, 'w') as dst:
        dst.write(src.read())
    print(f"Backup created: {backup_path}")

    # Load the file
    mdql = MDQL(todo_path)

    # Print summary
    print_section("1. Overall Summary")
    mdql.print_summary()

    # Query incomplete tasks
    print_section("2. Query: Incomplete Tasks")
    incomplete = mdql.query(completed=False, indent_level=0)
    print(f"Found {len(incomplete)} incomplete top-level tasks")
    print_tasks(incomplete[:5], "First 5 incomplete tasks")

    # Query high-priority tasks
    print_section("3. Query: High Priority Tasks")
    high_priority = mdql.query(priority="High", completed=False, indent_level=0)
    print_tasks(high_priority, "High priority incomplete tasks")

    # Query tasks in specific section
    print_section("4. Query: Tasks in 'Open Mosque Project'")
    open_mosque_tasks = mdql.query(section="Open Mosque Project")
    print_tasks(open_mosque_tasks, "Open Mosque Project tasks")

    # Query completed tasks
    print_section("5. Query: Completed Tasks")
    completed = mdql.query(completed=True)
    print_tasks(completed[:10], "First 10 completed tasks")

    # Add a new task
    print_section("6. Add New Task")
    print("Adding task to 'Tools & Integrations' section...")
    try:
        mdql.add_task(
            section="Tools & Integrations",
            text="Test MDQL prototype on todo.md",
            indent_level=0,
            completed=False
        )
        print("✓ Task added successfully")

        # Query to verify
        new_tasks = mdql.query(text_contains="MDQL prototype")
        print_tasks(new_tasks, "Newly added task")
    except Exception as e:
        print(f"Error adding task: {e}")

    # Mark a task as complete
    print_section("7. Mark Task as Complete")
    if incomplete:
        # Find a task to mark complete (avoid already completed ones)
        task_to_complete = None
        for task in incomplete:
            if "mdql" in task.text.lower():
                task_to_complete = task
                break

        if task_to_complete:
            print(f"Marking as complete: {task_to_complete.text}")
            print(f"  Line number: {task_to_complete.line_number}")
            mdql.mark_complete(task_to_complete.line_number)
            print("✓ Task marked as complete")

            # Verify
            updated = mdql.query(text_contains="mdql prototype")
            if updated:
                print(f"  New status: {'✓ Complete' if updated[0].completed else '☐ Incomplete'}")

    # Update task text
    print_section("8. Update Task Text")
    if new_tasks:
        task = new_tasks[0]
        original_text = task.text
        new_text = "Successfully tested MDQL prototype on todo.md"
        print(f"Updating task text:")
        print(f"  Old: {original_text}")
        print(f"  New: {new_text}")
        mdql.update_text(task.line_number, new_text)
        print("✓ Task text updated")

    # Show section summary
    print_section("9. Section Progress Summary")
    summary = mdql.get_section_summary()

    print(f"{'Section':<40} {'Priority':<10} {'Progress':<20} {'%':<10}")
    print("-" * 80)
    for item in summary[:10]:  # Show first 10
        section = item['section'][:38]
        priority = item['priority'] or 'N/A'
        progress = f"{item['completed']}/{item['total_tasks']}"
        pct = f"{item['completion_pct']}%"
        print(f"{section:<40} {priority:<10} {progress:<20} {pct:<10}")

    # Save to a test file
    print_section("10. Save Changes")
    test_output = todo_path.replace(".md", "-modified.md")
    mdql.save(test_output)
    print(f"✓ Changes saved to: {test_output}")

    # Validate the file
    print_section("11. Validate Modified File")
    print("Parsing modified file to validate...")
    try:
        mdql_test = MDQL(test_output)
        print(f"✓ File parsed successfully")
        print(f"  Total tasks: {len(mdql_test.tasks)}")
        print(f"  Total sections: {len(mdql_test.sections)}")

        # Show a sample of the file
        print("\nFirst 20 lines of modified file:")
        print("-" * 80)
        with open(test_output, 'r') as f:
            for i, line in enumerate(f, 1):
                if i > 20:
                    break
                print(f"{i:3d}: {line.rstrip()}")
        print("-" * 80)

    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return 1

    print_section("Demo Complete!")
    print(f"Original file: {todo_path}")
    print(f"Backup file: {backup_path}")
    print(f"Modified file: {test_output}")
    print("\nYou can compare the files to see the changes.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

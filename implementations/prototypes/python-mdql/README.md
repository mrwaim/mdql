# MDQL Python Prototype

A simple Python implementation of MDQL (Markdown Query Language) for parsing and manipulating markdown task lists.

## Features

- ✅ Parse markdown files with task lists (`- [ ]` and `- [x]`)
- ✅ Extract section metadata (Priority, Status, Source, Updated)
- ✅ Query tasks by various criteria
- ✅ Add new tasks to sections
- ✅ Mark tasks as complete/incomplete
- ✅ Update task text
- ✅ Delete tasks
- ✅ Generate progress summaries
- ✅ Preserve file structure and formatting

## Installation

No external dependencies required! Uses only Python standard library.

```bash
# Requires Python 3.7+
python3 --version
```

## Usage

### Basic Example

```python
from mdql import MDQL

# Load a markdown file
mdql = MDQL("path/to/todo.md")

# Query incomplete tasks
incomplete = mdql.query(completed=False, indent_level=0)
for task in incomplete:
    print(f"☐ {task.text}")

# Query by priority
high_priority = mdql.query(priority="High", completed=False)

# Query by section
section_tasks = mdql.query(section="Open Mosque Project")

# Add a new task
mdql.add_task(
    section="My Section",
    text="New task to complete",
    indent_level=0,
    completed=False
)

# Mark task as complete
mdql.mark_complete(line_number=42)

# Update task text
mdql.update_text(line_number=42, new_text="Updated task description")

# Delete a task
mdql.delete(line_number=43)

# Save changes
mdql.save("path/to/output.md")
```

### Running the Demo

```bash
# From the python-mdql directory
python3 demo.py

# Or make it executable and run
chmod +x demo.py
./demo.py
```

The demo will:
1. Load the sample todo.md file
2. Run various queries
3. Add a new task
4. Mark tasks as complete
5. Update task text
6. Save to a new file
7. Validate the output

## API Reference

### MDQL Class

#### Constructor
```python
mdql = MDQL(filepath: str)
```

#### Properties
- `tasks` - List of all TaskItem objects
- `sections` - Dictionary of section metadata

#### Methods

**Query Tasks**
```python
mdql.query(**filters) -> List[TaskItem]
```
Supported filters:
- `completed: bool` - Filter by completion status
- `section: str` - Filter by section name
- `priority: str` - Filter by priority (High, Medium, Low)
- `status: str` - Filter by status
- `indent_level: int` - Filter by nesting level (0 = top-level)
- `text_contains: str` - Filter by text content
- `notes_contains: str` - Filter by content in notes/descriptions
- `has_notes: bool` - Filter tasks with/without notes

**Modify Tasks**
```python
mdql.mark_complete(line_number: int)
mdql.mark_incomplete(line_number: int)
mdql.update_text(line_number: int, new_text: str)
mdql.delete(line_number: int)
mdql.add_task(section: str, text: str, indent_level: int = 0, completed: bool = False)
```

**Save Changes**
```python
mdql.save(filepath: Optional[str] = None)
```

**Generate Reports**
```python
mdql.get_section_summary() -> List[Dict]
mdql.print_summary()
```

### TaskItem Class

Represents a single task with the following attributes:

- `text: str` - Task description
- `completed: bool` - Completion status
- `section: str` - Parent section name
- `section_level: int` - Heading level (2 for ##, 3 for ###)
- `indent_level: int` - Nesting depth (0 = top-level)
- `line_number: int` - Line number in file
- `parent_line: Optional[int]` - Parent task line number
- `has_children: bool` - Whether task has subtasks
- `children: List[TaskItem]` - List of child tasks
- `notes: List[str]` - Descriptive bullet points under this task (non-checkbox items)

### SectionMetadata Class

Represents section metadata with attributes:

- `section_name: str`
- `section_level: int`
- `line_number: int`
- `source_file: Optional[str]`
- `source_date: Optional[str]`
- `source_time: Optional[str]`
- `updated_file: Optional[str]`
- `updated_date: Optional[str]`
- `updated_time: Optional[str]`
- `priority: Optional[str]`
- `status: Optional[str]`
- `properties: Dict[str, str]`

## Examples

### Get All High Priority Incomplete Tasks

```python
from mdql import MDQL

mdql = MDQL("todo.md")

high_priority_tasks = mdql.query(
    priority="High",
    completed=False,
    indent_level=0
)

for task in high_priority_tasks:
    print(f"🔴 {task.text}")
    print(f"   Section: {task.section}")
```

### Section Progress Report

```python
from mdql import MDQL

mdql = MDQL("todo.md")
summary = mdql.get_section_summary()

for item in summary:
    print(f"{item['section']}")
    print(f"  Progress: {item['completed']}/{item['total_tasks']} ({item['completion_pct']}%)")
    print(f"  Priority: {item['priority']}")
    print(f"  Status: {item['status']}")
```

### Batch Complete Tasks in a Section

```python
from mdql import MDQL

mdql = MDQL("todo.md")

# Get all incomplete tasks in a section
tasks = mdql.query(section="Completed Project", completed=False)

# Mark them all as complete
for task in tasks:
    mdql.mark_complete(task.line_number)

# Save changes
mdql.save()
```

### Find Actionable Tasks (No Incomplete Children)

```python
from mdql import MDQL

mdql = MDQL("todo.md")

# Get all incomplete top-level tasks
incomplete = mdql.query(completed=False, indent_level=0)

# Filter to tasks with no incomplete children
actionable = [
    task for task in incomplete
    if not task.has_children or all(child.completed for child in task.children)
]

print(f"Actionable tasks: {len(actionable)}")
for task in actionable:
    print(f"☐ {task.text}")
```

### Query Tasks with Notes

```python
from mdql import MDQL

mdql = MDQL("todo.md")

# Find tasks that have notes/descriptions
tasks_with_notes = mdql.query(has_notes=True)
print(f"Found {len(tasks_with_notes)} tasks with notes")

# Search for specific content in notes
example_tasks = mdql.query(notes_contains="Example")
for task in example_tasks:
    print(f"☐ {task.text}")
    print(f"  Notes:")
    for note in task.notes:
        print(f"    - {note}")

# Get tasks with many notes (detailed tasks)
detailed_tasks = [t for t in mdql.tasks if len(t.notes) >= 3]
for task in detailed_tasks:
    print(f"☐ {task.text} ({len(task.notes)} notes)")
```

## Limitations

This is a prototype implementation with some limitations:

1. **Basic SQL Support** - No full SQL parser, uses Python method calls with filters
2. **No Joins** - Can't join multiple files together
3. **No Indexes** - Queries scan all tasks (fine for small files)
4. **Limited Validation** - Basic error checking
5. **No Transactions** - Changes are applied immediately
6. **Simple Metadata** - Only handles common metadata patterns

## Future Enhancements

Potential improvements for a production implementation:

- Full SQL query parser
- Support for joins across multiple files
- Indexing for faster queries
- More sophisticated metadata extraction
- Transaction support with rollback
- Watch mode for auto-reload on file changes
- CLI tool for running queries from command line
- Integration with git for version control

## Testing

```bash
# Run the demo to test all functionality
python3 demo.py

# The demo will create:
# - todo.md.backup (original backup)
# - todo-modified.md (with changes applied)
```

Compare the files to verify the changes are correct:

```bash
# View differences
diff samples/notes-app/todo.md samples/notes-app/todo-modified.md

# Or use your preferred diff tool
```

## Contributing

This is a prototype for demonstration purposes. For production use, consider:

- Adding comprehensive test suite
- Implementing full SQL parser
- Adding support for more markdown formats
- Performance optimizations for large files
- Better error handling and validation

## License

Part of the MDQL project. See main repository for license information.

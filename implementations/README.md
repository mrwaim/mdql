# MDQL Implementations

This directory contains implementations of the MDQL (Markdown Query Language) specification.

## Directory Structure

```
implementations/
├── prototypes/          # Proof-of-concept implementations
│   └── python-mdql/     # Python prototype implementation
└── README.md           # This file
```

## Prototypes

### Python MDQL (`prototypes/python-mdql/`)

A simple Python implementation demonstrating core MDQL functionality:

- ✅ Parse task lists with checkboxes (`- [ ]` and `- [x]`)
- ✅ Extract section metadata (Priority, Status, Source, Updated)
- ✅ Query tasks by multiple criteria
- ✅ Add, update, and delete tasks
- ✅ Generate progress reports
- ✅ Preserve file structure

**Quick Start:**

```bash
cd prototypes/python-mdql
python3 demo.py
```

See [prototypes/python-mdql/README.md](prototypes/python-mdql/README.md) for detailed documentation.

**Example Usage:**

```python
from mdql import MDQL

# Load and query
mdql = MDQL("todo.md")
high_priority = mdql.query(priority="High", completed=False)

# Modify
mdql.mark_complete(line_number=42)
mdql.add_task(section="My Section", text="New task")
mdql.save()
```

## Future Implementations

Potential future implementations:

- **TypeScript/JavaScript** - For browser and Node.js environments
- **Rust** - High-performance implementation with CLI
- **Go** - Standalone binary with built-in server
- **SQL Backend** - Full SQL parser with SQLite/PostgreSQL backend

## Implementation Guidelines

When creating a new MDQL implementation:

### Core Requirements

1. **Parser** - Extract structured data from markdown
   - Task lists (checkboxes)
   - Section metadata
   - Nested task hierarchies

2. **Query Engine** - Support filtering by:
   - Completion status
   - Section/subsection
   - Priority/status (from metadata)
   - Indentation level
   - Text content

3. **Writer** - Update markdown files while:
   - Preserving formatting
   - Maintaining indentation
   - Keeping metadata intact
   - Using atomic file operations

4. **Metadata Tracking**
   - Line numbers for precise updates
   - Parent-child relationships
   - Section context

### Recommended Features

- Transaction support (rollback on error)
- File watching for auto-reload
- Validation and error reporting
- Progress/summary generation
- CLI interface
- Backup before modifications

### Testing

Include tests for:
- Parsing various markdown formats
- Query correctness
- Update operations
- Edge cases (empty files, malformed markdown)
- File preservation (formatting, metadata)

### Documentation

Each implementation should include:
- README with installation and usage
- API reference
- Example code
- Demo script
- Limitations and known issues

## Contributing

To add a new implementation:

1. Create a subdirectory under `prototypes/` or create a new category
2. Implement core MDQL functionality
3. Add comprehensive documentation
4. Include a demo/test script
5. Update this README

## License

See main repository for license information.

# MDQL - Markdown Query Language

A SQL-like query language for querying and manipulating markdown files.

## Overview

MDQL treats markdown files and folders as databases, allowing you to query, insert, update, and delete content using familiar SQL syntax. Different markdown structures can be treated as tables:

- **Markdown Tables** → Each row in the table is a database row
- **List Items** → Each list item is a row
- **Paragraphs** → Each paragraph is a row
- **Folders** → Each markdown file in the folder is a row
- **Sections** → Each heading section is a row

## Quick Start

### Sample Query

```sql
-- Select all high-priority tasks
SELECT TaskID, Title, Assignee, DueDate
FROM "samples/tasks.md"
WHERE Priority = 'High'
ORDER BY DueDate ASC;

-- Get all engineering employees with their tasks
SELECT
  e.content->>'Employee ID' as emp_id,
  e.content->>'Role' as role,
  t.Title as task
FROM "samples/employees/" e
JOIN "samples/tasks.md" t
  ON e.content->>'Employee ID' = t.Assignee
WHERE e.content->>'Department' = 'Engineering';
```

## Documentation

### Core Documentation

- **[Query Language Reference](docs/queries.md)** - Complete guide to SELECT, INSERT, UPDATE, DELETE queries with examples
- **[Metadata Specification](docs/metadata-spec.md)** - How MDQL tracks and references row data
- **[Joins Reference](docs/joins.md)** - Comprehensive guide to joining markdown data sources

### Sample Data

The `samples/` directory contains example markdown files demonstrating different table types:

- `samples/employees/` - Folder as table (each file is a row)
- `samples/tasks.md` - Markdown table
- `samples/projects.md` - List items as rows
- `samples/notes.md` - Paragraphs as rows
- `samples/departments.md` - List items with structured data

## Features

### Query Operations

- **SELECT**: Query data with filtering, sorting, aggregation, and joins
- **INSERT**: Add new rows (table rows, list items, paragraphs, files)
- **UPDATE**: Modify existing content in place
- **DELETE**: Remove rows while preserving file structure
- **VIEWS**: Create virtual tables and materialized views

### Join Capabilities

- Multiple join types (INNER, LEFT, RIGHT, FULL, CROSS)
- Field-based joins
- Link-based joins (following markdown links)
- Pattern-based joins (regex matching)
- Hierarchical joins (folder/file relationships)
- Content-based joins (similarity matching)

### Advanced Features

- Aggregations (COUNT, SUM, AVG, MIN, MAX)
- Subqueries and CTEs (Common Table Expressions)
- Window functions
- Full-text search
- Transactions
- Materialized views

## Table Reference Syntax

```sql
-- Reference a markdown file
FROM "path/to/file.md"

-- Explicitly specify content type
FROM "path/to/file.md"::lists
FROM "path/to/file.md"::table
FROM "path/to/file.md"::paragraphs

-- Reference all files in a folder
FROM "path/to/folder/"
```

## Content Extraction

Use the `->` and `->>` operators to extract data from structured content:

```sql
-- Extract text value
SELECT content->>'Employee ID' as emp_id
FROM "samples/employees/";

-- Extract from list items with pattern
SELECT
  content->>'name' as project_name,
  content->>'status' as status
FROM "samples/projects.md"::lists;
```

## Example Queries

### Basic SELECT

```sql
-- All tasks in progress
SELECT * FROM "samples/tasks.md"
WHERE Status = 'In Progress';
```

### INSERT

```sql
-- Add a new task
INSERT INTO "samples/tasks.md" (TaskID, Title, Assignee, Priority, Status, DueDate)
VALUES ('T008', 'Setup CI/CD pipeline', 'E002', 'High', 'Not Started', '2024-02-01');
```

### UPDATE

```sql
-- Mark task as completed
UPDATE "samples/tasks.md"
SET Status = 'Completed'
WHERE TaskID = 'T001';
```

### DELETE

```sql
-- Remove completed tasks
DELETE FROM "samples/tasks.md"
WHERE Status = 'Completed';
```

### JOIN

```sql
-- Employees with their active tasks
SELECT
  e.content->>'Employee ID' as emp_id,
  e.filename as name,
  t.Title as task,
  t.DueDate
FROM "samples/employees/" e
JOIN "samples/tasks.md" t
  ON e.content->>'Employee ID' = t.Assignee
WHERE t.Status != 'Completed';
```

### Aggregation

```sql
-- Task count by status
SELECT Status, COUNT(*) as count
FROM "samples/tasks.md"
GROUP BY Status;

-- Average salary by department
SELECT
  content->>'Department' as department,
  AVG(CAST(content->>'Salary' as INTEGER)) as avg_salary
FROM "samples/employees/"
GROUP BY content->>'Department';
```

## Architecture

### Metadata System

MDQL maintains metadata for each row including:

- **Source location**: File path, line numbers, byte offsets
- **Position information**: Exact location for updates/deletes
- **Content type**: Table row, list item, paragraph, file, etc.
- **Structural context**: Parent headings, section hierarchy
- **Unique identifiers**: Row IDs and content hashes
- **Schema information**: Column names, types, primary keys
- **Link information**: Internal/external links, wiki links

See [Metadata Specification](docs/metadata-spec.md) for details.

### How Updates Work

1. Parse query to identify affected rows
2. Load metadata for matching rows
3. Use byte offsets to locate exact content
4. Apply changes to file content
5. Update metadata (hashes, offsets)
6. Write modified file back to disk

### How Joins Work

1. Load and parse both data sources
2. Extract join keys from structured content
3. Match rows based on join condition
4. Combine columns from both sources
5. Return joined result set

See [Joins Reference](docs/joins.md) for comprehensive join documentation.

## Use Cases

### Project Management

- Query tasks by status, priority, assignee
- Track sprint progress and burndown
- Generate reports on overdue items
- Analyze workload distribution

### Knowledge Management

- Search across documentation
- Find related documents via links
- Generate table of contents
- Track document updates and changes

### HR & Team Management

- Employee directories and skills matrices
- Workload and capacity planning
- Performance tracking
- Org chart generation

### Note-Taking Systems

- Query meeting notes by date, topic, attendees
- Extract action items and decisions
- Link notes to tasks and projects
- Build knowledge graphs

## Implementation Considerations

### Performance

- **Indexing**: Build indexes on commonly queried fields
- **Caching**: Cache parsed AST and compiled queries
- **Incremental updates**: Only re-parse changed files
- **Lazy loading**: Load files only when needed

### Storage Options

- **In-memory index**: Fast, rebuilt on each session
- **SQLite database**: Persistent metadata storage
- **Sidecar files**: `.mdql` files alongside markdown files

### File Operations

- **Atomic writes**: Use temp files and rename
- **Backup**: Optional backup before modifications
- **Version control**: Integrate with git for history
- **Watch mode**: Auto-reload on file changes

## Future Enhancements

### Advanced Features

- **Full-text search**: Inverted index for text queries
- **Semantic search**: Vector embeddings for similarity
- **Graph queries**: Query link relationships as graphs
- **Time-travel**: Query historical versions via git
- **Fuzzy matching**: Approximate string matching
- **OCR support**: Extract text from embedded images

### Integrations

- **Git integration**: Track changes, authors, history
- **Frontmatter**: YAML/TOML metadata support
- **External APIs**: Join with external data sources
- **Export formats**: CSV, JSON, Excel output
- **LSP support**: Language server for editor integration

### Performance

- **Parallel processing**: Multi-threaded file parsing
- **Streaming**: Handle large files efficiently
- **Compression**: Compress metadata storage
- **Distributed**: Scale across multiple machines

## License

TBD

## Contributing

TBD

---

## Getting Started

1. **Explore the samples**: Check out the `samples/` directory for example markdown files
2. **Read the docs**: Start with [Query Language Reference](docs/queries.md)
3. **Try queries**: Experiment with SELECT queries on the sample data
4. **Build something**: Use MDQL for your own markdown-based workflows

## Questions?

- Check the [Query Language Reference](docs/queries.md) for syntax
- Review the [Joins Reference](docs/joins.md) for combining data sources
- See the [Metadata Specification](docs/metadata-spec.md) for implementation details

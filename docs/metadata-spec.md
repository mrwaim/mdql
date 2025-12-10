# MDQL Metadata Specification

## Overview

To enable querying, updating, and deleting markdown content, MDQL needs to track metadata about each "row" (data unit) extracted from markdown files. This metadata allows the query engine to:

1. **Reference back** to the original location for UPDATE/DELETE operations
2. **Preserve structure** when modifying files
3. **Enable joins** between different data sources
4. **Track relationships** between rows and their context

---

## Core Metadata Fields

Every row extracted from markdown must have the following metadata:

### 1. Source Location

```json
{
  "source": {
    "file_path": "samples/tasks.md",
    "file_path_absolute": "/home/user/project/samples/tasks.md",
    "file_hash": "sha256:abc123...",
    "last_modified": "2024-01-08T10:30:00Z"
  }
}
```

**Fields:**
- `file_path` - Relative path from query root
- `file_path_absolute` - Absolute filesystem path
- `file_hash` - Hash of file content for change detection
- `last_modified` - File modification timestamp

### 2. Position Information

```json
{
  "position": {
    "start_line": 15,
    "end_line": 15,
    "start_column": 1,
    "end_column": 78,
    "start_offset": 456,
    "end_offset": 534
  }
}
```

**Fields:**
- `start_line` / `end_line` - Line numbers (1-indexed)
- `start_column` / `end_column` - Column positions (1-indexed)
- `start_offset` / `end_offset` - Byte offsets from file start (0-indexed)

**Note:** Both line numbers and byte offsets are tracked to support efficient updates:
- Line numbers for human-readable references
- Byte offsets for precise content replacement

### 3. Content Type

```json
{
  "content_type": {
    "type": "table_row",
    "subtype": "markdown_table",
    "format": "pipe_table"
  }
}
```

**Possible Values for `type`:**
- `table_row` - Row from a markdown table
- `list_item` - Item from a bullet or numbered list
- `paragraph` - A paragraph of text
- `file` - Entire file as a row (for folder queries)
- `heading` - A heading/section title
- `code_block` - A code block
- `blockquote` - A quoted block

**Possible Values for `subtype`:**
- For `table_row`: `markdown_table`, `html_table`
- For `list_item`: `unordered_list`, `ordered_list`, `task_list`
- For `paragraph`: `text`, `definition`
- For `code_block`: `fenced`, `indented`

### 4. Structural Context

```json
{
  "context": {
    "heading_path": ["Team Standup - 2024-01-08"],
    "heading_level": 2,
    "parent_heading": "Team Standup - 2024-01-08",
    "section_id": "team-standup-2024-01-08",
    "nesting_level": 0,
    "list_index": 3,
    "table_name": null,
    "table_row_index": 5
  }
}
```

**Fields:**
- `heading_path` - Array of ancestor headings (navigation breadcrumb)
- `heading_level` - Level of nearest parent heading (1-6)
- `parent_heading` - Direct parent heading text
- `section_id` - Slug/ID of the section (for linking)
- `nesting_level` - Depth in list hierarchy (for nested lists)
- `list_index` - Position in list (0-indexed)
- `table_name` - Name/caption of table if available
- `table_row_index` - Row index within table (0-indexed, excluding header)

### 5. Unique Row Identifier

```json
{
  "row_id": "mdql:samples/tasks.md:table:5:sha256:def456",
  "row_hash": "sha256:def456..."
}
```

**Fields:**
- `row_id` - Globally unique identifier for this row
  - Format: `mdql:{file_path}:{type}:{index}:{content_hash}`
- `row_hash` - Hash of the row content for change detection

**Purpose:**
- Enable stable references for JOINs
- Detect when content has changed
- Support incremental updates

### 6. Schema Information

For structured content (tables, lists with patterns), track the schema:

```json
{
  "schema": {
    "columns": ["TaskID", "Title", "Assignee", "Priority", "Status", "DueDate"],
    "column_types": {
      "TaskID": "string",
      "Title": "string",
      "Assignee": "string",
      "Priority": "enum",
      "Status": "enum",
      "DueDate": "date"
    },
    "primary_key": ["TaskID"],
    "nullable": ["DueDate"]
  }
}
```

**Fields:**
- `columns` - Ordered list of column names
- `column_types` - Inferred or declared types for each column
- `primary_key` - Columns that uniquely identify the row
- `nullable` - Columns that can be empty

### 7. Link Information

Track links within content for relationship mapping:

```json
{
  "links": {
    "internal": [
      {
        "target": "samples/employees/john.md",
        "anchor": null,
        "text": "John Doe"
      }
    ],
    "external": [
      {
        "url": "https://example.com/docs",
        "text": "Documentation"
      }
    ],
    "wiki_links": [
      {
        "target": "[[Projects/Authentication]]",
        "resolved": "samples/projects.md#authentication-system"
      }
    ]
  }
}
```

---

## Complete Metadata Example

### Example 1: Table Row

```json
{
  "row_id": "mdql:samples/tasks.md:table_row:5:sha256:a1b2c3",
  "row_hash": "sha256:a1b2c3...",

  "source": {
    "file_path": "samples/tasks.md",
    "file_path_absolute": "/home/user/project/samples/tasks.md",
    "file_hash": "sha256:abc123...",
    "last_modified": "2024-01-08T10:30:00Z"
  },

  "position": {
    "start_line": 9,
    "end_line": 9,
    "start_column": 1,
    "end_column": 95,
    "start_offset": 456,
    "end_offset": 551
  },

  "content_type": {
    "type": "table_row",
    "subtype": "markdown_table",
    "format": "pipe_table"
  },

  "context": {
    "heading_path": ["Task List", "Sprint 23 Tasks"],
    "heading_level": 2,
    "parent_heading": "Sprint 23 Tasks",
    "section_id": "sprint-23-tasks",
    "nesting_level": 0,
    "list_index": null,
    "table_name": "Sprint 23 Tasks",
    "table_row_index": 4
  },

  "schema": {
    "columns": ["TaskID", "Title", "Assignee", "Priority", "Status", "DueDate"],
    "column_types": {
      "TaskID": "string",
      "Title": "string",
      "Assignee": "string",
      "Priority": "enum",
      "Status": "enum",
      "DueDate": "date"
    },
    "primary_key": ["TaskID"]
  },

  "data": {
    "TaskID": "T005",
    "Title": "Database migration script",
    "Assignee": "E002",
    "Priority": "High",
    "Status": "Completed",
    "DueDate": "2024-01-10"
  },

  "links": {
    "internal": [],
    "external": [],
    "wiki_links": []
  }
}
```

### Example 2: List Item

```json
{
  "row_id": "mdql:samples/projects.md:list_item:2:sha256:x7y8z9",
  "row_hash": "sha256:x7y8z9...",

  "source": {
    "file_path": "samples/projects.md",
    "file_path_absolute": "/home/user/project/samples/projects.md",
    "file_hash": "sha256:def456...",
    "last_modified": "2024-01-08T09:15:00Z"
  },

  "position": {
    "start_line": 7,
    "end_line": 7,
    "start_column": 1,
    "end_column": 88,
    "start_offset": 234,
    "end_offset": 322
  },

  "content_type": {
    "type": "list_item",
    "subtype": "unordered_list",
    "format": "dash"
  },

  "context": {
    "heading_path": ["Projects", "Active Projects"],
    "heading_level": 2,
    "parent_heading": "Active Projects",
    "section_id": "active-projects",
    "nesting_level": 0,
    "list_index": 2,
    "table_name": null,
    "table_row_index": null
  },

  "schema": {
    "columns": ["content"],
    "parsed_fields": {
      "name": "Cloud Migration",
      "description": "Moving infrastructure to AWS",
      "status": "In Progress",
      "owner": "E002"
    }
  },

  "data": {
    "content": "**Cloud Migration** - Moving infrastructure to AWS - Status: In Progress - Owner: E002",
    "raw_content": "**Cloud Migration** - Moving infrastructure to AWS - Status: In Progress - Owner: E002"
  },

  "links": {
    "internal": [],
    "external": [],
    "wiki_links": []
  }
}
```

### Example 3: Paragraph

```json
{
  "row_id": "mdql:samples/notes.md:paragraph:1:sha256:p1q2r3",
  "row_hash": "sha256:p1q2r3...",

  "source": {
    "file_path": "samples/notes.md",
    "file_path_absolute": "/home/user/project/samples/notes.md",
    "file_hash": "sha256:ghi789...",
    "last_modified": "2024-01-08T11:45:00Z"
  },

  "position": {
    "start_line": 5,
    "end_line": 5,
    "start_column": 1,
    "end_column": 156,
    "start_offset": 145,
    "end_offset": 301
  },

  "content_type": {
    "type": "paragraph",
    "subtype": "text",
    "format": "plain"
  },

  "context": {
    "heading_path": ["Meeting Notes", "Team Standup - 2024-01-08"],
    "heading_level": 2,
    "parent_heading": "Team Standup - 2024-01-08",
    "section_id": "team-standup-2024-01-08",
    "nesting_level": 0,
    "list_index": null,
    "table_name": null,
    "table_row_index": null
  },

  "schema": null,

  "data": {
    "content": "The engineering team discussed the progress on the authentication system. John reported that the OAuth integration is 60% complete and should be ready for testing by end of week.",
    "word_count": 30,
    "char_count": 180
  },

  "links": {
    "internal": [],
    "external": [],
    "wiki_links": []
  }
}
```

### Example 4: File (from folder query)

```json
{
  "row_id": "mdql:samples/employees/:file:john.md:sha256:f1g2h3",
  "row_hash": "sha256:f1g2h3...",

  "source": {
    "file_path": "samples/employees/john.md",
    "file_path_absolute": "/home/user/project/samples/employees/john.md",
    "file_hash": "sha256:jkl012...",
    "last_modified": "2024-01-05T14:20:00Z"
  },

  "position": {
    "start_line": 1,
    "end_line": 19,
    "start_column": 1,
    "end_column": 1,
    "start_offset": 0,
    "end_offset": 456
  },

  "content_type": {
    "type": "file",
    "subtype": "markdown",
    "format": "markdown"
  },

  "context": {
    "heading_path": [],
    "heading_level": null,
    "parent_heading": null,
    "section_id": null,
    "nesting_level": 0,
    "list_index": null,
    "table_name": null,
    "table_row_index": null,
    "directory": "samples/employees/",
    "filename": "john.md",
    "basename": "john",
    "extension": ".md"
  },

  "schema": {
    "frontmatter": null,
    "parsed_fields": {
      "Employee ID": "E001",
      "Department": "Engineering",
      "Role": "Senior Developer",
      "Start Date": "2020-01-15",
      "Salary": "120000"
    },
    "sections": [
      "Personal Information",
      "Skills",
      "Current Projects"
    ]
  },

  "data": {
    "filename": "john.md",
    "title": "John Doe",
    "content": "# John Doe\n\n## Personal Information...",
    "excerpt": "Employee ID: E001, Department: Engineering, Role: Senior Developer"
  },

  "links": {
    "internal": [],
    "external": [],
    "wiki_links": []
  }
}
```

---

## Metadata Storage

### Storage Options

MDQL implementations can store metadata in several ways:

#### 1. In-Memory Index
- Fast querying
- Rebuilt on each query session
- Good for small to medium datasets

#### 2. SQLite Database
```sql
CREATE TABLE mdql_metadata (
  row_id TEXT PRIMARY KEY,
  row_hash TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_hash TEXT NOT NULL,
  start_line INTEGER NOT NULL,
  end_line INTEGER NOT NULL,
  start_offset INTEGER NOT NULL,
  end_offset INTEGER NOT NULL,
  content_type TEXT NOT NULL,
  context JSON,
  schema JSON,
  data JSON,
  links JSON,
  last_indexed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_file_path ON mdql_metadata(file_path);
CREATE INDEX idx_content_type ON mdql_metadata(content_type);
CREATE INDEX idx_file_hash ON mdql_metadata(file_hash);
```

#### 3. Sidecar Files
```
samples/
  tasks.md
  tasks.md.mdql          # Metadata sidecar
  employees/
    john.md
    john.md.mdql        # Metadata sidecar
```

Each `.mdql` file contains JSON metadata for all rows in the corresponding markdown file.

---

## Metadata Usage

### 1. UPDATE Operations

When executing an UPDATE query:

1. Parse the query to identify affected rows
2. Load metadata for matching rows
3. Use `start_offset` and `end_offset` to locate exact content
4. Replace content in file
5. Update metadata (new hash, new offsets for subsequent rows)
6. Write updated file

### 2. DELETE Operations

When executing a DELETE query:

1. Parse the query to identify affected rows
2. Load metadata for matching rows
3. Sort by `start_offset` (descending) to delete from bottom up
4. Use offsets to remove content from file
5. Update metadata for subsequent rows (adjust offsets)
6. Write updated file

### 3. JOIN Operations

When joining tables:

1. Load metadata for both sources
2. Use `row_id` for efficient matching
3. Use `links` metadata for link-based joins
4. Use `schema.parsed_fields` for field-based joins

### 4. Incremental Updates

To detect changes since last indexing:

1. Compare `file_hash` in metadata vs current file hash
2. If different, re-parse file and update metadata
3. Use `row_hash` to detect which specific rows changed
4. Only re-index changed files

---

## Metadata API

### Querying Metadata

MDQL provides special system tables for querying metadata:

```sql
-- View all indexed files
SELECT * FROM __mdql_files;

-- View metadata for specific table
SELECT * FROM __mdql_metadata
WHERE file_path = 'samples/tasks.md';

-- Find files modified recently
SELECT file_path, last_modified
FROM __mdql_files
WHERE last_modified > DATE_SUB(NOW(), INTERVAL 1 DAY);

-- Analyze content types
SELECT content_type, COUNT(*) as count
FROM __mdql_metadata
GROUP BY content_type;
```

### Metadata Functions

```sql
-- Get row metadata
SELECT MDQL_METADATA(row_id) FROM "samples/tasks.md";

-- Get file hash
SELECT MDQL_FILE_HASH('samples/tasks.md');

-- Get row hash
SELECT MDQL_ROW_HASH(row_id) FROM "samples/tasks.md";

-- Refresh metadata for a file
SELECT MDQL_REFRESH('samples/tasks.md');
```

---

## Performance Considerations

### Indexing Strategy

1. **Initial Indexing**: Full scan of all markdown files
2. **Incremental Indexing**: Only re-index changed files
3. **Lazy Indexing**: Index on first query
4. **Watch Mode**: Auto-reindex on file changes

### Caching

- Cache parsed AST for frequently accessed files
- Cache compiled queries
- Cache JOIN results for views

### Optimization

- Use byte offsets for fast content location
- Batch file writes to minimize I/O
- Index only queried files in large repositories
- Use bloom filters for fast existence checks

---

## Future Extensions

### Git Integration

Track git metadata for version control:

```json
{
  "git": {
    "commit": "abc123...",
    "author": "John Doe <john@example.com>",
    "date": "2024-01-08T10:30:00Z",
    "branch": "main"
  }
}
```

### Frontmatter Support

Extract YAML frontmatter as structured data:

```json
{
  "frontmatter": {
    "title": "Task List",
    "tags": ["project-management", "sprint-23"],
    "author": "Jane Smith",
    "date": "2024-01-01"
  }
}
```

### Full-Text Search Index

Build inverted index for fast text search:

```json
{
  "search_index": {
    "terms": ["authentication", "oauth", "system"],
    "tf_idf": {...}
  }
}
```

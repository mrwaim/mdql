# MDQL Task List Specification

## Overview

Task lists (checkbox lists) are a special type of list item in markdown that use checkbox syntax:
- `- [ ]` for incomplete tasks
- `- [x]` for completed tasks

MDQL provides specialized support for querying, filtering, and updating task lists, making it ideal for todo management, project tracking, and task organization systems.

---

## Basic Task List Structure

### Simple Task List

```markdown
## My Tasks

- [ ] Task one
- [x] Task two (completed)
- [ ] Task three
```

### Nested Task Lists

```markdown
## Project Tasks

- [ ] Main task
  - [ ] Subtask 1
  - [x] Subtask 2 (completed)
  - [ ] Subtask 3
    - [ ] Sub-subtask
```

### Task Lists with Notes/Descriptions

Tasks can have descriptive bullet points (without checkboxes) underneath them:

```markdown
## Development Tasks

- [ ] Implement authentication
  - Set up OAuth provider with Google
  - Create login page with email/password
  - Add password reset functionality
- [x] Design database schema
```

These non-checkbox bullets are captured as **notes** on the task and can be queried.

### Task Lists with Metadata

```markdown
## Development Tasks
*Source: notes-2025-12-16.md (2025-12-16 01:55)*
*Updated: notes-2025-12-25.md (2025-12-25 06:22)*

**Priority:** High
**Status:** In Progress

- [ ] Implement authentication
  - [ ] Set up OAuth provider
  - [ ] Create login page
- [x] Design database schema
```

---

## Querying Task Lists

### Table Reference

Use the `::task_lists` qualifier to specifically query task lists:

```sql
-- Query all task items from a file
SELECT * FROM "todo.md"::task_lists;

-- Alternative: Lists qualifier also includes task lists
SELECT * FROM "todo.md"::lists
WHERE is_task_item = true;
```

### Basic Selection

```sql
-- Select all incomplete tasks
SELECT text, section
FROM "todo.md"::task_lists
WHERE completed = false;

-- Select all completed tasks
SELECT text, section
FROM "todo.md"::task_lists
WHERE completed = true;

-- Select tasks from specific section
SELECT text, completed
FROM "todo.md"::task_lists
WHERE section = 'Task Notification System';
```

**Result:**
| text | section |
|------|---------|
| Design notification system architecture | Task Notification System |
| Implement job time estimates feature | Task Notification System |
| Build notification timing system | Task Notification System |

### Nested Task Queries

```sql
-- Select only top-level tasks (not nested)
SELECT text, section
FROM "todo.md"::task_lists
WHERE indent_level = 0 AND completed = false;

-- Select all nested tasks (exclude top-level)
SELECT text, section, indent_level
FROM "todo.md"::task_lists
WHERE indent_level > 0;

-- Select parent tasks with their children
SELECT
  parent.text as parent_task,
  child.text as child_task,
  child.completed as child_completed
FROM "todo.md"::task_lists parent
LEFT JOIN "todo.md"::task_lists child
  ON child.parent_line = parent.line_number
WHERE parent.indent_level = 0;
```

**Result:**
| parent_task | child_task | child_completed |
|-------------|------------|-----------------|
| Design notification system architecture | Decide: Does it just notify constantly or be smarter? | false |
| Design notification system architecture | Implement "is this active job done yet?" logic | false |

### Section Metadata Queries

```sql
-- Query tasks with section metadata
SELECT
  t.text,
  t.section,
  m.priority,
  m.status,
  m.source_file,
  m.source_date
FROM "todo.md"::task_lists t
JOIN "todo.md"::section_metadata m
  ON t.section = m.section_name
WHERE m.priority = 'High';
```

**Result:**
| text | section | priority | status | source_file | source_date |
|------|---------|----------|--------|-------------|-------------|
| Get kids camera to initial better version | Kids Camera with Aafiyah | High | In Progress | notes-2025-12-22.md | 2025-12-22 |
| Get pacemaker to a good spot | Pacemaker Development | High | In Progress | notes-2025-12-22.md | 2025-12-22 |

---

## Task List Metadata

### Row Metadata Fields

Each task list item has the following metadata:

```json
{
  "row_id": "mdql:todo.md:task_item:6:sha256:abc123",
  "row_hash": "sha256:abc123...",

  "content_type": {
    "type": "list_item",
    "subtype": "task_list",
    "format": "dash"
  },

  "task_data": {
    "completed": false,
    "text": "Design notification system architecture",
    "indent_level": 0,
    "parent_line": null,
    "has_children": true,
    "child_count": 2,
    "completed_children": 0,
    "notes": [
      "Decide: Does it just notify constantly or be smarter?",
      "Implement \"is this active job done yet?\" logic"
    ]
  },

  "context": {
    "section": "Task Notification System",
    "section_level": 2,
    "heading_path": ["Todos", "Task Notification System"]
  },

  "section_metadata": {
    "source": {
      "file": "notes-2025-12-16.md",
      "date": "2025-12-16",
      "time": "01:55"
    },
    "updated": {
      "file": "notes-2025-12-25.md",
      "date": "2025-12-25",
      "time": "06:22"
    },
    "properties": {
      "Priority": "High",
      "Status": "In Progress"
    }
  }
}
```

### Queryable Fields

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | Task description text |
| `completed` | boolean | Checkbox status (true if [x], false if [ ]) |
| `section` | string | Parent section heading |
| `section_level` | integer | Heading level (2 for ##, 3 for ###) |
| `indent_level` | integer | Nesting depth (0 for top-level) |
| `line_number` | integer | Line number in file |
| `parent_line` | integer | Line number of parent task (null if top-level) |
| `has_children` | boolean | Whether task has nested subtasks |
| `child_count` | integer | Number of direct children |
| `completed_children` | integer | Number of completed children |
| `notes` | array[string] | Descriptive bullet points under this task (non-checkbox items) |
| `is_task_item` | boolean | Always true for task lists |

### Section Metadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `source_file` | string | From `*Source: file.md*` |
| `source_date` | date | From `*Source: file.md (date)*` |
| `source_time` | time | Optional time from source |
| `updated_file` | string | From `*Updated: file.md*` |
| `updated_date` | date | From `*Updated: file.md (date)*` |
| `updated_time` | time | Optional time from updated |
| `priority` | string | From `**Priority:** value` |
| `status` | string | From `**Status:** value` |
| `properties` | object | All `**Key:** value` pairs |

---

## Advanced Queries

### Completion Statistics

```sql
-- Task completion summary by section
SELECT
  section,
  COUNT(*) as total_tasks,
  SUM(CASE WHEN completed THEN 1 ELSE 0 END) as completed_tasks,
  ROUND(100.0 * SUM(CASE WHEN completed THEN 1 ELSE 0 END) / COUNT(*), 2) as completion_rate
FROM "todo.md"::task_lists
WHERE indent_level = 0  -- Only count top-level tasks
GROUP BY section
ORDER BY completion_rate DESC;
```

**Result:**
| section | total_tasks | completed_tasks | completion_rate |
|---------|-------------|-----------------|-----------------|
| MAPS Community Organization | 3 | 1 | 33.33 |
| Task Notification System | 5 | 0 | 0.00 |
| Open Mosque Project | 4 | 1 | 25.00 |

### Tasks by Priority

```sql
-- Get incomplete tasks by priority
SELECT
  m.priority,
  t.section,
  t.text,
  m.status
FROM "todo.md"::task_lists t
JOIN "todo.md"::section_metadata m
  ON t.section = m.section_name
WHERE t.completed = false
  AND t.indent_level = 0
  AND m.priority IS NOT NULL
ORDER BY
  CASE m.priority
    WHEN 'High' THEN 1
    WHEN 'Medium' THEN 2
    WHEN 'Low' THEN 3
  END,
  t.line_number;
```

### Nested Task Analysis

```sql
-- Find parent tasks where all children are complete
SELECT
  parent.text as task,
  parent.section,
  COUNT(child.line_number) as total_children,
  SUM(CASE WHEN child.completed THEN 1 ELSE 0 END) as completed_children
FROM "todo.md"::task_lists parent
JOIN "todo.md"::task_lists child
  ON child.parent_line = parent.line_number
WHERE parent.completed = false
GROUP BY parent.text, parent.section, parent.line_number
HAVING COUNT(child.line_number) = SUM(CASE WHEN child.completed THEN 1 ELSE 0 END)
ORDER BY parent.section;
```

### Tasks by Source Date

```sql
-- Tasks created in the last week
SELECT
  t.text,
  t.section,
  m.source_date,
  m.source_file
FROM "todo.md"::task_lists t
JOIN "todo.md"::section_metadata m
  ON t.section = m.section_name
WHERE t.completed = false
  AND m.source_date >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY)
ORDER BY m.source_date DESC;
```

### Tasks with Notes

```sql
-- Find tasks with specific content in notes
SELECT
  t.text,
  t.section,
  t.notes
FROM "todo.md"::task_lists t
WHERE ARRAY_LENGTH(t.notes) > 0
  AND t.notes @> 'Example';

-- Find tasks that have notes
SELECT
  t.text,
  t.section,
  ARRAY_LENGTH(t.notes) as note_count
FROM "todo.md"::task_lists t
WHERE ARRAY_LENGTH(t.notes) > 0
ORDER BY note_count DESC;

-- Search across task text and notes
SELECT
  t.text,
  t.section,
  t.notes
FROM "todo.md"::task_lists t
WHERE t.text LIKE '%notification%'
   OR ANY(t.notes) LIKE '%notification%';
```

### Overdue/Stale Tasks

```sql
-- Tasks not updated in 30 days
SELECT
  t.section,
  t.text,
  COALESCE(m.updated_date, m.source_date) as last_modified,
  DATE_DIFF(CURRENT_DATE, COALESCE(m.updated_date, m.source_date)) as days_stale
FROM "todo.md"::task_lists t
JOIN "todo.md"::section_metadata m
  ON t.section = m.section_name
WHERE t.completed = false
  AND DATE_DIFF(CURRENT_DATE, COALESCE(m.updated_date, m.source_date)) > 30
ORDER BY days_stale DESC;
```

---

## Updating Tasks

### Mark Tasks as Complete

```sql
-- Mark a specific task as complete
UPDATE "todo.md"::task_lists
SET completed = true
WHERE text = 'Design notification system architecture';

-- Mark all tasks in a section as complete
UPDATE "todo.md"::task_lists
SET completed = true
WHERE section = 'Task Notification System';

-- Mark task by line number (most precise)
UPDATE "todo.md"::task_lists
SET completed = true
WHERE line_number = 6;
```

**Effect:** Changes `- [ ]` to `- [x]` in the file

### Mark Tasks as Incomplete

```sql
-- Uncheck a completed task
UPDATE "todo.md"::task_lists
SET completed = false
WHERE text LIKE '%Follow up with Sister Mallak%';
```

**Effect:** Changes `- [x]` to `- [ ]` in the file

### Update Task Text

```sql
-- Update task description
UPDATE "todo.md"::task_lists
SET text = 'Design and implement notification system architecture'
WHERE line_number = 6;
```

**Effect:** Updates the text while preserving checkbox and indentation

### Batch Updates

```sql
-- Mark all high-priority completed tasks as archived
UPDATE "todo.md"::task_lists t
SET text = '[ARCHIVED] ' || t.text
FROM "todo.md"::section_metadata m
WHERE t.section = m.section_name
  AND t.completed = true
  AND m.priority = 'High';
```

---

## Deleting Tasks

### Delete Completed Tasks

```sql
-- Delete all completed tasks
DELETE FROM "todo.md"::task_lists
WHERE completed = true;

-- Delete completed tasks from specific section
DELETE FROM "todo.md"::task_lists
WHERE completed = true
  AND section = 'Completed Projects';
```

### Delete Specific Tasks

```sql
-- Delete a task by text match
DELETE FROM "todo.md"::task_lists
WHERE text LIKE '%obsolete%';

-- Delete by line number
DELETE FROM "todo.md"::task_lists
WHERE line_number = 42;
```

### Delete with Children

```sql
-- Delete a parent task and all its children
DELETE FROM "todo.md"::task_lists
WHERE line_number = 6
   OR parent_line = 6;

-- Better: Using CTE to handle nested deletion
WITH RECURSIVE task_tree AS (
  -- Base: the task to delete
  SELECT line_number
  FROM "todo.md"::task_lists
  WHERE text = 'Obsolete feature'

  UNION ALL

  -- Recursive: all children
  SELECT child.line_number
  FROM "todo.md"::task_lists child
  JOIN task_tree parent ON child.parent_line = parent.line_number
)
DELETE FROM "todo.md"::task_lists
WHERE line_number IN (SELECT line_number FROM task_tree);
```

---

## Inserting New Tasks

### Add Task to Section

```sql
-- Add a new task to a section
INSERT INTO "todo.md"::task_lists
SECTION 'Task Notification System'
VALUES ('- [ ] Add push notification support');

-- Add multiple tasks
INSERT INTO "todo.md"::task_lists
SECTION 'Task Notification System'
VALUES
  ('- [ ] Add email notifications'),
  ('- [ ] Add SMS notifications');
```

### Add Nested Task

```sql
-- Add a subtask under an existing task
INSERT INTO "todo.md"::task_lists
AFTER line_number 6
INDENT 1
VALUES ('- [ ] Research notification libraries');

-- Or using parent reference
INSERT INTO "todo.md"::task_lists
PARENT (SELECT line_number FROM "todo.md"::task_lists WHERE text = 'Design notification system architecture')
VALUES ('- [ ] Create architecture diagram');
```

### Add Task with Specific Indent

```sql
-- Add a deeply nested task
INSERT INTO "todo.md"::task_lists
SECTION 'Task Notification System'
AFTER line_number 8
INDENT 2
VALUES ('- [ ] Configure timeout settings');
```

---

## Practical Examples

### Example 1: Daily Todo Report

```sql
-- Generate today's incomplete tasks
SELECT
  t.section,
  t.text,
  m.priority,
  CASE
    WHEN t.has_children THEN CONCAT(t.completed_children, '/', t.child_count, ' subtasks done')
    ELSE 'No subtasks'
  END as progress
FROM "todo.md"::task_lists t
LEFT JOIN "todo.md"::section_metadata m
  ON t.section = m.section_name
WHERE t.completed = false
  AND t.indent_level = 0
ORDER BY
  CASE COALESCE(m.priority, 'Low')
    WHEN 'High' THEN 1
    WHEN 'Medium' THEN 2
    ELSE 3
  END,
  t.section;
```

### Example 2: Section Progress Dashboard

```sql
-- Show progress for each major section
SELECT
  m.section_name as section,
  m.priority,
  m.status,
  COUNT(t.line_number) as total_tasks,
  SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) as completed,
  ROUND(100.0 * SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) / COUNT(t.line_number), 1) as pct_complete,
  m.source_date as created,
  m.updated_date as last_updated
FROM "todo.md"::section_metadata m
LEFT JOIN "todo.md"::task_lists t
  ON t.section = m.section_name
WHERE t.indent_level = 0 OR t.indent_level IS NULL
GROUP BY m.section_name, m.priority, m.status, m.source_date, m.updated_date
ORDER BY
  CASE COALESCE(m.priority, 'Low')
    WHEN 'High' THEN 1
    WHEN 'Medium' THEN 2
    ELSE 3
  END,
  pct_complete ASC;
```

### Example 3: Find Actionable Tasks

```sql
-- Tasks that are actionable (not blocked by incomplete children)
WITH blocked_tasks AS (
  SELECT DISTINCT parent.line_number
  FROM "todo.md"::task_lists parent
  JOIN "todo.md"::task_lists child
    ON child.parent_line = parent.line_number
  WHERE child.completed = false
)
SELECT
  t.text,
  t.section,
  m.priority
FROM "todo.md"::task_lists t
LEFT JOIN "todo.md"::section_metadata m
  ON t.section = m.section_name
WHERE t.completed = false
  AND t.indent_level = 0
  AND t.line_number NOT IN (SELECT line_number FROM blocked_tasks)
ORDER BY
  CASE COALESCE(m.priority, 'Low')
    WHEN 'High' THEN 1
    WHEN 'Medium' THEN 2
    ELSE 3
  END;
```

### Example 4: Archive Completed Sections

```sql
-- Move completed sections to archive file
BEGIN TRANSACTION;

-- Copy completed sections to archive
INSERT INTO "archive.md"::sections
SELECT section_name, content
FROM "todo.md"::sections s
WHERE NOT EXISTS (
  SELECT 1 FROM "todo.md"::task_lists t
  WHERE t.section = s.section_name
    AND t.completed = false
);

-- Delete completed sections from active todo
DELETE FROM "todo.md"::sections
WHERE section_name IN (
  SELECT section_name
  FROM "todo.md"::sections s
  WHERE NOT EXISTS (
    SELECT 1 FROM "todo.md"::task_lists t
    WHERE t.section = s.section_name
      AND t.completed = false
  )
);

COMMIT;
```

### Example 5: Task Dependency Report

```sql
-- Show parent tasks and their incomplete dependencies
SELECT
  parent.text as parent_task,
  parent.section,
  STRING_AGG(
    CASE WHEN child.completed THEN '✓ ' ELSE '☐ ' END || child.text,
    ', '
  ) as dependencies,
  COUNT(child.line_number) as total_deps,
  SUM(CASE WHEN child.completed THEN 1 ELSE 0 END) as completed_deps
FROM "todo.md"::task_lists parent
JOIN "todo.md"::task_lists child
  ON child.parent_line = parent.line_number
WHERE parent.completed = false
GROUP BY parent.text, parent.section, parent.line_number
ORDER BY completed_deps::FLOAT / COUNT(child.line_number) DESC;
```

---

## Views for Task Management

### Create Useful Views

```sql
-- View: Active high-priority tasks
CREATE VIEW active_high_priority AS
SELECT
  t.text,
  t.section,
  m.status,
  m.source_date
FROM "todo.md"::task_lists t
JOIN "todo.md"::section_metadata m ON t.section = m.section_name
WHERE t.completed = false
  AND m.priority = 'High'
  AND t.indent_level = 0
ORDER BY m.source_date;

-- View: Task completion by section
CREATE VIEW section_progress AS
SELECT
  section,
  COUNT(*) as total,
  SUM(CASE WHEN completed THEN 1 ELSE 0 END) as done,
  ROUND(100.0 * SUM(CASE WHEN completed THEN 1 ELSE 0 END) / COUNT(*), 1) as pct
FROM "todo.md"::task_lists
WHERE indent_level = 0
GROUP BY section;

-- Use the views
SELECT * FROM active_high_priority;
SELECT * FROM section_progress WHERE pct < 50;
```

---

## Integration Patterns

### Integration with Note-Taking Systems

```sql
-- Find tasks mentioned in daily notes
SELECT
  n.heading as note_date,
  t.text as task,
  t.section,
  t.completed
FROM "notes-app/daily/*.md"::paragraphs n
JOIN "notes-app/todo.md"::task_lists t
  ON n.content ~ (regexp_escape(t.text))
WHERE t.completed = false
ORDER BY n.heading DESC;
```

### Cross-File Task Aggregation

```sql
-- Aggregate tasks from multiple files
SELECT
  source_file,
  section,
  COUNT(*) as task_count,
  SUM(CASE WHEN completed THEN 1 ELSE 0 END) as completed_count
FROM (
  SELECT 'todo.md' as source_file, section, completed
  FROM "notes-app/todo.md"::task_lists

  UNION ALL

  SELECT 'questions.md' as source_file, section, completed
  FROM "notes-app/questions.md"::task_lists
) all_tasks
GROUP BY source_file, section
ORDER BY source_file, section;
```

---

## Best Practices

### 1. Use Line Numbers for Updates

When updating or deleting specific tasks, prefer line numbers over text matching:

```sql
-- Good: Precise
UPDATE "todo.md"::task_lists SET completed = true WHERE line_number = 42;

-- Risky: May match multiple tasks
UPDATE "todo.md"::task_lists SET completed = true WHERE text LIKE '%notification%';
```

### 2. Handle Nested Tasks Carefully

When deleting parent tasks, decide whether to delete children:

```sql
-- Option 1: Delete parent only (children become top-level)
DELETE FROM "todo.md"::task_lists WHERE line_number = 42;

-- Option 2: Delete parent and all descendants
DELETE FROM "todo.md"::task_lists
WHERE line_number = 42 OR parent_line = 42;
```

### 3. Leverage Section Metadata

Section metadata provides rich context for filtering:

```sql
SELECT t.*
FROM "todo.md"::task_lists t
JOIN "todo.md"::section_metadata m ON t.section = m.section_name
WHERE m.priority = 'High' AND m.status = 'In Progress';
```

### 4. Use Transactions for Multi-Step Updates

```sql
BEGIN TRANSACTION;

-- Mark parent complete
UPDATE "todo.md"::task_lists SET completed = true WHERE line_number = 10;

-- Mark all children complete
UPDATE "todo.md"::task_lists SET completed = true WHERE parent_line = 10;

COMMIT;
```

### 5. Regular Cleanup

```sql
-- Archive old completed tasks monthly
INSERT INTO "archive-2025-12.md"::task_lists
SELECT * FROM "todo.md"::task_lists
WHERE completed = true
  AND MONTH(COALESCE(updated_date, source_date)) = 12;

DELETE FROM "todo.md"::task_lists
WHERE completed = true
  AND MONTH(COALESCE(updated_date, source_date)) = 12;
```

---

## Implementation Notes

### Parsing Task Lists

Task list items must match the pattern:
- `^(\s*)- \[([ xX])\] (.+)$`
- Capture groups: (1) indentation, (2) checkbox status, (3) text

Indentation level calculation:
- Count leading spaces
- Divide by 2 (or indent width)
- This gives `indent_level`

Parent relationship:
- Track last seen task at each indent level
- When indent increases, previous task is parent
- When indent decreases or stays same, use appropriate level's parent

### Extracting Section Metadata

Patterns to match:
- `*Source: filename.md (date time)*`
- `*Updated: filename.md (date time)*`
- `**Key:** Value`

Associate metadata with current section (most recent heading above).

### Update Operations

When toggling checkbox:
1. Locate line by line_number
2. Use regex to toggle: `\[([ xX])\]` → `[x]` or `[ ]`
3. Preserve all other content (indentation, text)
4. Update row_hash in metadata

---

## Future Enhancements

### Smart Date Parsing

Extract due dates from task text:
```sql
SELECT
  text,
  MDQL_EXTRACT_DATE(text) as due_date
FROM "todo.md"::task_lists
WHERE MDQL_EXTRACT_DATE(text) < CURRENT_DATE;
```

### Task Dependencies

Support dependency syntax:
```markdown
- [ ] Task A
- [ ] Task B (depends on: Task A)
```

### Task Templates

```sql
-- Insert tasks from template
INSERT INTO "todo.md"::task_lists
SECTION 'New Project'
FROM TEMPLATE 'templates/project-tasks.md';
```

### Recurring Tasks

```sql
-- Mark as complete and create next occurrence
UPDATE "todo.md"::task_lists
SET completed = true
WHERE text LIKE '%Weekly review%'
RECURRING WEEKLY;
```

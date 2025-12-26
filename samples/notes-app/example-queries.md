# MDQL Query Examples for Notes App

This document demonstrates practical MDQL queries for managing the notes-app todo system.

## Sample Files

- `todo.md` - Main todo list with tasks organized by project/topic
- `questions.md` - Questions and decision tracking

---

## Basic Todo Queries

### Get All Incomplete Tasks

```sql
SELECT
  text as task,
  section,
  line_number
FROM "samples/notes-app/todo.md"::task_lists
WHERE completed = false
ORDER BY section, line_number;
```

### Get Completed Tasks

```sql
SELECT
  text as task,
  section,
  line_number
FROM "samples/notes-app/todo.md"::task_lists
WHERE completed = true
ORDER BY section, line_number;
```

### Get Tasks by Section

```sql
-- All tasks for Open Mosque Project
SELECT
  text as task,
  completed,
  indent_level
FROM "samples/notes-app/todo.md"::task_lists
WHERE section = 'Open Mosque Project'
ORDER BY line_number;
```

---

## Priority-Based Queries

### High Priority Tasks

```sql
SELECT
  t.text as task,
  t.section,
  m.status,
  m.source_date
FROM "samples/notes-app/todo.md"::task_lists t
JOIN "samples/notes-app/todo.md"::section_metadata m
  ON t.section = m.section_name
WHERE t.completed = false
  AND m.priority = 'High'
  AND t.indent_level = 0
ORDER BY m.source_date;
```

**Result:**
| task | section | status | source_date |
|------|---------|--------|-------------|
| Check on marketing status with Sr Mallak | Open Mosque Project | In Progress | 2025-12-22 |
| Begin inviting immediate circle to event | Open Mosque Project | In Progress | 2025-12-22 |
| Get kids camera to initial better version | Kids Camera with Aafiyah | In Progress | 2025-12-22 |
| Get pacemaker to a good spot | Pacemaker Development | In Progress | 2025-12-22 |

### Tasks by Priority Level

```sql
SELECT
  m.priority,
  COUNT(*) as total_tasks,
  SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) as completed_tasks,
  COUNT(*) - SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) as remaining_tasks
FROM "samples/notes-app/todo.md"::task_lists t
JOIN "samples/notes-app/todo.md"::section_metadata m
  ON t.section = m.section_name
WHERE t.indent_level = 0
GROUP BY m.priority
ORDER BY
  CASE m.priority
    WHEN 'High' THEN 1
    WHEN 'Medium' THEN 2
    WHEN 'Low' THEN 3
  END;
```

---

## Status-Based Queries

### Tasks In Progress

```sql
SELECT
  t.text as task,
  t.section,
  m.priority,
  m.source_date,
  m.updated_date
FROM "samples/notes-app/todo.md"::task_lists t
JOIN "samples/notes-app/todo.md"::section_metadata m
  ON t.section = m.section_name
WHERE t.completed = false
  AND m.status = 'In Progress'
  AND t.indent_level = 0
ORDER BY
  CASE COALESCE(m.priority, 'Low')
    WHEN 'High' THEN 1
    WHEN 'Medium' THEN 2
    ELSE 3
  END;
```

### Tasks Not Started

```sql
SELECT
  t.text as task,
  t.section,
  m.priority
FROM "samples/notes-app/todo.md"::task_lists t
JOIN "samples/notes-app/todo.md"::section_metadata m
  ON t.section = m.section_name
WHERE t.completed = false
  AND m.status = 'Not Started'
  AND t.indent_level = 0;
```

---

## Progress Tracking

### Section Progress Report

```sql
SELECT
  m.section_name as section,
  m.priority,
  m.status,
  COUNT(t.line_number) as total_tasks,
  SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) as completed_tasks,
  COUNT(t.line_number) - SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) as remaining_tasks,
  ROUND(100.0 * SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) / COUNT(t.line_number), 1) as completion_pct
FROM "samples/notes-app/todo.md"::section_metadata m
LEFT JOIN "samples/notes-app/todo.md"::task_lists t
  ON t.section = m.section_name AND t.indent_level = 0
GROUP BY m.section_name, m.priority, m.status
HAVING COUNT(t.line_number) > 0
ORDER BY
  CASE COALESCE(m.priority, 'Low')
    WHEN 'High' THEN 1
    WHEN 'Medium' THEN 2
    ELSE 3
  END,
  completion_pct ASC;
```

### Overall Progress

```sql
SELECT
  COUNT(*) as total_tasks,
  SUM(CASE WHEN completed THEN 1 ELSE 0 END) as completed,
  COUNT(*) - SUM(CASE WHEN completed THEN 1 ELSE 0 END) as remaining,
  ROUND(100.0 * SUM(CASE WHEN completed THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_complete
FROM "samples/notes-app/todo.md"::task_lists
WHERE indent_level = 0;
```

---

## Nested Task Analysis

### Parent Tasks with Child Progress

```sql
SELECT
  parent.text as parent_task,
  parent.section,
  COUNT(child.line_number) as total_children,
  SUM(CASE WHEN child.completed THEN 1 ELSE 0 END) as completed_children,
  ROUND(100.0 * SUM(CASE WHEN child.completed THEN 1 ELSE 0 END) / COUNT(child.line_number), 1) as child_completion_pct
FROM "samples/notes-app/todo.md"::task_lists parent
JOIN "samples/notes-app/todo.md"::task_lists child
  ON child.parent_line = parent.line_number
WHERE parent.completed = false
GROUP BY parent.text, parent.section, parent.line_number
ORDER BY child_completion_pct DESC;
```

### Tasks Ready to Complete (All Children Done)

```sql
SELECT
  parent.text as task,
  parent.section,
  COUNT(child.line_number) as child_count
FROM "samples/notes-app/todo.md"::task_lists parent
JOIN "samples/notes-app/todo.md"::task_lists child
  ON child.parent_line = parent.line_number
WHERE parent.completed = false
GROUP BY parent.text, parent.section, parent.line_number
HAVING COUNT(child.line_number) = SUM(CASE WHEN child.completed THEN 1 ELSE 0 END);
```

### All Subtasks for a Parent Task

```sql
SELECT
  text as subtask,
  completed,
  indent_level,
  line_number
FROM "samples/notes-app/todo.md"::task_lists
WHERE parent_line = (
  SELECT line_number
  FROM "samples/notes-app/todo.md"::task_lists
  WHERE text LIKE '%Design notification system architecture%'
)
ORDER BY line_number;
```

---

## Time-Based Queries

### Recently Added Tasks (Last 7 Days)

```sql
SELECT
  t.text as task,
  t.section,
  m.source_date,
  m.source_file
FROM "samples/notes-app/todo.md"::task_lists t
JOIN "samples/notes-app/todo.md"::section_metadata m
  ON t.section = m.section_name
WHERE t.completed = false
  AND m.source_date >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY)
  AND t.indent_level = 0
ORDER BY m.source_date DESC;
```

### Recently Updated Sections

```sql
SELECT
  section_name,
  priority,
  status,
  updated_date,
  updated_file
FROM "samples/notes-app/todo.md"::section_metadata
WHERE updated_date >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY)
ORDER BY updated_date DESC;
```

### Stale Tasks (Not Updated in 30 Days)

```sql
SELECT
  t.text as task,
  t.section,
  m.source_date,
  COALESCE(m.updated_date, m.source_date) as last_modified,
  DATE_DIFF(CURRENT_DATE, COALESCE(m.updated_date, m.source_date)) as days_stale
FROM "samples/notes-app/todo.md"::task_lists t
JOIN "samples/notes-app/todo.md"::section_metadata m
  ON t.section = m.section_name
WHERE t.completed = false
  AND t.indent_level = 0
  AND DATE_DIFF(CURRENT_DATE, COALESCE(m.updated_date, m.source_date)) > 30
ORDER BY days_stale DESC;
```

---

## Topic/Project Queries

### Open Mosque Project Tasks

```sql
-- All Open Mosque related tasks
SELECT
  text as task,
  completed,
  indent_level
FROM "samples/notes-app/todo.md"::task_lists
WHERE section LIKE '%Open Mosque%'
ORDER BY line_number;
```

### Personal vs Project Tasks

```sql
SELECT
  CASE
    WHEN section IN ('Personal Projects', 'Personal Management', 'Personal Health') THEN 'Personal'
    ELSE 'Project/Work'
  END as category,
  COUNT(*) as total_tasks,
  SUM(CASE WHEN completed THEN 1 ELSE 0 END) as completed_tasks
FROM "samples/notes-app/todo.md"::task_lists
WHERE indent_level = 0
GROUP BY
  CASE
    WHEN section IN ('Personal Projects', 'Personal Management', 'Personal Health') THEN 'Personal'
    ELSE 'Project/Work'
  END;
```

---

## Update Operations

### Mark Specific Task as Complete

```sql
-- By line number (most precise)
UPDATE "samples/notes-app/todo.md"::task_lists
SET completed = true
WHERE line_number = 175;

-- By text match
UPDATE "samples/notes-app/todo.md"::task_lists
SET completed = true
WHERE text = 'Schedule time with dad for interview';
```

### Mark All Tasks in Section as Complete

```sql
UPDATE "samples/notes-app/todo.md"::task_lists
SET completed = true
WHERE section = 'Dad Interview';
```

### Complete Task and All Children

```sql
BEGIN TRANSACTION;

-- Mark parent as complete
UPDATE "samples/notes-app/todo.md"::task_lists
SET completed = true
WHERE line_number = 60;

-- Mark all children as complete
UPDATE "samples/notes-app/todo.md"::task_lists
SET completed = true
WHERE parent_line = 60;

COMMIT;
```

### Update Task Text

```sql
UPDATE "samples/notes-app/todo.md"::task_lists
SET text = 'Try out mdql and write sample queries'
WHERE line_number = 235;
```

---

## Delete Operations

### Delete Completed Tasks

```sql
-- Delete all completed tasks
DELETE FROM "samples/notes-app/todo.md"::task_lists
WHERE completed = true;

-- Delete completed tasks from specific section
DELETE FROM "samples/notes-app/todo.md"::task_lists
WHERE completed = true AND section = 'Completed Projects';
```

### Archive Old Completed Tasks

```sql
BEGIN TRANSACTION;

-- Copy to archive
INSERT INTO "samples/notes-app/archive-2025.md"::task_lists
SELECT * FROM "samples/notes-app/todo.md"::task_lists
WHERE completed = true
  AND YEAR(COALESCE(updated_date, source_date)) = 2025;

-- Delete from active todo
DELETE FROM "samples/notes-app/todo.md"::task_lists
WHERE completed = true
  AND YEAR(COALESCE(updated_date, source_date)) = 2025;

COMMIT;
```

---

## Insert Operations

### Add New Task to Section

```sql
INSERT INTO "samples/notes-app/todo.md"::task_lists
SECTION 'Tools & Integrations'
VALUES ('- [ ] Write comprehensive MDQL documentation');
```

### Add Subtask

```sql
-- Add subtask under existing task
INSERT INTO "samples/notes-app/todo.md"::task_lists
PARENT (SELECT line_number FROM "samples/notes-app/todo.md"::task_lists WHERE text LIKE '%Try out mdql%')
VALUES ('- [ ] Run example queries on todo.md');
```

### Add Multiple Tasks

```sql
INSERT INTO "samples/notes-app/todo.md"::task_lists
SECTION 'Tools & Integrations'
VALUES
  ('- [ ] Test MDQL on large todo files'),
  ('- [ ] Benchmark query performance'),
  ('- [ ] Write CLI wrapper for MDQL');
```

---

## Reporting Queries

### Daily Todo Report

```sql
-- Generate a focused daily todo list
SELECT
  CASE COALESCE(m.priority, 'Medium')
    WHEN 'High' THEN '🔴 HIGH'
    WHEN 'Medium' THEN '🟡 MED'
    ELSE '🟢 LOW'
  END as priority,
  t.section,
  t.text as task,
  CASE
    WHEN t.has_children THEN CONCAT('(', t.completed_children, '/', t.child_count, ' subtasks done)')
    ELSE ''
  END as progress
FROM "samples/notes-app/todo.md"::task_lists t
LEFT JOIN "samples/notes-app/todo.md"::section_metadata m
  ON t.section = m.section_name
WHERE t.completed = false
  AND t.indent_level = 0
ORDER BY
  CASE COALESCE(m.priority, 'Medium')
    WHEN 'High' THEN 1
    WHEN 'Medium' THEN 2
    ELSE 3
  END,
  m.source_date DESC;
```

### Weekly Progress Report

```sql
SELECT
  m.section_name as project,
  m.priority,
  m.status,
  COUNT(t.line_number) as tasks,
  SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) as done,
  ROUND(100.0 * SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) / NULLIF(COUNT(t.line_number), 0), 1) as pct,
  m.updated_date as last_update
FROM "samples/notes-app/todo.md"::section_metadata m
LEFT JOIN "samples/notes-app/todo.md"::task_lists t
  ON t.section = m.section_name AND t.indent_level = 0
WHERE m.priority IN ('High', 'Medium')
GROUP BY m.section_name, m.priority, m.status, m.updated_date
ORDER BY
  CASE m.priority WHEN 'High' THEN 1 ELSE 2 END,
  pct ASC;
```

### Completion Velocity

```sql
-- Tasks completed per week
SELECT
  YEARWEEK(COALESCE(m.updated_date, m.source_date)) as week,
  COUNT(*) as tasks_completed
FROM "samples/notes-app/todo.md"::task_lists t
JOIN "samples/notes-app/todo.md"::section_metadata m
  ON t.section = m.section_name
WHERE t.completed = true
  AND COALESCE(m.updated_date, m.source_date) >= DATE_SUB(CURRENT_DATE, INTERVAL 8 WEEK)
GROUP BY YEARWEEK(COALESCE(m.updated_date, m.source_date))
ORDER BY week DESC;
```

---

## Views for Common Queries

### Create Useful Views

```sql
-- View: Today's focus tasks
CREATE VIEW todays_focus AS
SELECT
  t.text as task,
  t.section,
  m.priority,
  t.line_number
FROM "samples/notes-app/todo.md"::task_lists t
JOIN "samples/notes-app/todo.md"::section_metadata m
  ON t.section = m.section_name
WHERE t.completed = false
  AND t.indent_level = 0
  AND m.priority = 'High'
ORDER BY m.source_date;

-- View: Section progress summary
CREATE VIEW section_progress AS
SELECT
  m.section_name,
  m.priority,
  COUNT(t.line_number) as total,
  SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) as done,
  ROUND(100.0 * SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) / COUNT(t.line_number), 1) as pct
FROM "samples/notes-app/todo.md"::section_metadata m
LEFT JOIN "samples/notes-app/todo.md"::task_lists t
  ON t.section = m.section_name AND t.indent_level = 0
GROUP BY m.section_name, m.priority;

-- Use the views
SELECT * FROM todays_focus;
SELECT * FROM section_progress WHERE pct < 50 ORDER BY priority;
```

---

## Advanced Scenarios

### Find Actionable Tasks (No Blocking Dependencies)

```sql
-- Tasks that can be started now (no incomplete children)
WITH blocked_tasks AS (
  SELECT DISTINCT parent.line_number
  FROM "samples/notes-app/todo.md"::task_lists parent
  JOIN "samples/notes-app/todo.md"::task_lists child
    ON child.parent_line = parent.line_number
  WHERE child.completed = false
)
SELECT
  t.text as task,
  t.section,
  m.priority
FROM "samples/notes-app/todo.md"::task_lists t
LEFT JOIN "samples/notes-app/todo.md"::section_metadata m
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

### Cross-File Task Aggregation

```sql
-- Combine tasks from multiple files
SELECT
  'todo.md' as source,
  section,
  text,
  completed
FROM "samples/notes-app/todo.md"::task_lists
WHERE completed = false

UNION ALL

SELECT
  'questions.md' as source,
  section,
  text,
  completed
FROM "samples/notes-app/questions.md"::task_lists
WHERE completed = false

ORDER BY source, section;
```

### Suggest Next Actions

```sql
-- Smart next action suggestions based on priority, staleness, and progress
SELECT
  t.text as next_action,
  t.section,
  m.priority,
  CASE
    WHEN DATE_DIFF(CURRENT_DATE, COALESCE(m.updated_date, m.source_date)) > 30 THEN 'Stale - needs attention'
    WHEN t.has_children AND t.completed_children > 0 THEN 'In progress - finish it'
    WHEN m.priority = 'High' THEN 'High priority - start soon'
    ELSE 'Ready to start'
  END as reason
FROM "samples/notes-app/todo.md"::task_lists t
JOIN "samples/notes-app/todo.md"::section_metadata m
  ON t.section = m.section_name
WHERE t.completed = false
  AND t.indent_level = 0
ORDER BY
  CASE m.priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,
  DATE_DIFF(CURRENT_DATE, COALESCE(m.updated_date, m.source_date)) DESC
LIMIT 5;
```

---

## Integration Examples

### Export to CSV

```sql
-- Export incomplete high-priority tasks
SELECT
  t.text,
  t.section,
  m.priority,
  m.status,
  m.source_date
FROM "samples/notes-app/todo.md"::task_lists t
JOIN "samples/notes-app/todo.md"::section_metadata m
  ON t.section = m.section_name
WHERE t.completed = false
  AND m.priority = 'High'
INTO OUTFILE 'high-priority-tasks.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';
```

### Generate Markdown Report

```sql
-- Generate a markdown-formatted daily report
SELECT
  CONCAT('# Daily Tasks - ', CURRENT_DATE, '\n\n') ||
  STRING_AGG(
    CONCAT('## ', section, '\n',
           STRING_AGG('- [ ] ' || text, '\n' ORDER BY line_number),
           '\n\n'),
    ''
  ) as daily_report
FROM "samples/notes-app/todo.md"::task_lists
WHERE completed = false
  AND indent_level = 0;
```

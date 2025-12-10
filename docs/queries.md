# MDQL Query Language Specification

## Overview

MDQL (Markdown Query Language) is a SQL-like query language for querying and manipulating markdown files. Different markdown structures can be treated as tables:

- **Markdown Table** → Each row in the table is a database row
- **List Items** → Each list item is a row
- **Paragraphs** → Each paragraph is a row
- **Folder** → Each markdown file is a row
- **Sections** → Each heading section is a row

## Table References

### File-based Tables
```sql
-- Reference a markdown file with a table
FROM "samples/tasks.md"

-- Reference a markdown file with list items
FROM "samples/projects.md"

-- Reference a markdown file with paragraphs
FROM "samples/notes.md"

-- Reference all files in a folder (each file is a row)
FROM "samples/employees/"
```

### Qualified Table References
```sql
-- Explicitly specify the content type
FROM "samples/projects.md"::lists
FROM "samples/tasks.md"::table
FROM "samples/notes.md"::paragraphs
FROM "samples/employees/"::files
```

---

## SELECT Queries

### Basic SELECT from Markdown Table

```sql
-- Select all tasks
SELECT * FROM "samples/tasks.md";

-- Select specific columns
SELECT TaskID, Title, Status
FROM "samples/tasks.md"
WHERE Status = 'In Progress';

-- With ordering
SELECT TaskID, Title, Priority, DueDate
FROM "samples/tasks.md"
WHERE Priority = 'High'
ORDER BY DueDate ASC;
```

**Result:**
| TaskID | Title | Priority | DueDate |
|--------|-------|----------|---------|
| T001 | Implement OAuth login | High | 2024-01-15 |
| T002 | Set up AWS EKS cluster | High | 2024-01-20 |

### SELECT from List Items

```sql
-- Select all active projects
SELECT * FROM "samples/projects.md"::lists
WHERE section = 'Active Projects';

-- Extract structured data from list items
SELECT
  content->>'name' as project_name,
  content->>'status' as status,
  content->>'owner' as owner
FROM "samples/projects.md"::lists
WHERE section = 'Active Projects'
  AND content->>'status' = 'In Progress';
```

**Result:**
| project_name | status | owner |
|--------------|--------|-------|
| Authentication System | In Progress | E001 |
| Cloud Migration | In Progress | E002 |
| API Gateway | In Progress | E001 |

### SELECT from Paragraphs

```sql
-- Select meeting notes by date range
SELECT heading, content, date
FROM "samples/notes.md"::paragraphs
WHERE date >= '2024-01-05'
ORDER BY date DESC;

-- Full-text search
SELECT heading, content
FROM "samples/notes.md"::paragraphs
WHERE content LIKE '%authentication%';
```

**Result:**
| heading | content |
|---------|---------|
| Team Standup - 2024-01-08 | The engineering team discussed... |
| Client Meeting - 2024-01-03 | Met with the client to discuss... |

### SELECT from Folder (Files as Rows)

```sql
-- Select all employees
SELECT * FROM "samples/employees/";

-- Select employees from a specific department
SELECT
  filename,
  content->>'Employee ID' as emp_id,
  content->>'Department' as department,
  content->>'Role' as role,
  content->>'Salary' as salary
FROM "samples/employees/"
WHERE content->>'Department' = 'Engineering';
```

**Result:**
| filename | emp_id | department | role | salary |
|----------|--------|------------|------|--------|
| john.md | E001 | Engineering | Senior Developer | 120000 |
| jane.md | E002 | Engineering | Tech Lead | 150000 |

### Aggregation Queries

```sql
-- Count tasks by status
SELECT Status, COUNT(*) as count
FROM "samples/tasks.md"
GROUP BY Status;

-- Average salary by department
SELECT
  content->>'Department' as department,
  AVG(CAST(content->>'Salary' as INTEGER)) as avg_salary
FROM "samples/employees/"
GROUP BY content->>'Department';

-- Tasks per assignee
SELECT Assignee, COUNT(*) as task_count
FROM "samples/tasks.md"
GROUP BY Assignee
HAVING COUNT(*) > 1;
```

---

## INSERT Queries

### INSERT into Markdown Table

```sql
-- Insert a new task
INSERT INTO "samples/tasks.md" (TaskID, Title, Assignee, Priority, Status, DueDate)
VALUES ('T008', 'Setup CI/CD pipeline', 'E002', 'High', 'Not Started', '2024-02-01');

-- Insert multiple tasks
INSERT INTO "samples/tasks.md" (TaskID, Title, Assignee, Priority, Status, DueDate)
VALUES
  ('T009', 'Code review automation', 'E001', 'Medium', 'Not Started', '2024-02-05'),
  ('T010', 'Performance testing', 'E002', 'High', 'Not Started', '2024-02-10');
```

**Effect:** Adds new rows to the markdown table in tasks.md

### INSERT into List

```sql
-- Add a new project to the active projects list
INSERT INTO "samples/projects.md"::lists
SECTION 'Active Projects'
VALUES ('**Customer Analytics** - Real-time analytics dashboard - Status: Planning - Owner: E002');

-- Add multiple list items
INSERT INTO "samples/projects.md"::lists
SECTION 'Active Projects'
VALUES
  ('**Performance Monitoring** - APM integration - Status: Planning - Owner: E001'),
  ('**Documentation Portal** - Centralized docs - Status: Not Started - Owner: E003');
```

**Effect:** Adds new items to the "Active Projects" list

### INSERT into Paragraphs

```sql
-- Add a new meeting note
INSERT INTO "samples/notes.md"::paragraphs
SECTION 'Team Standup - 2024-01-09'
VALUES ('The team discussed the upcoming release. All critical bugs have been resolved and we are on track for the Friday deployment.');
```

**Effect:** Adds a new paragraph section to notes.md

### INSERT into Folder (Create New File)

```sql
-- Add a new employee file
INSERT INTO "samples/employees/" (filename, content)
VALUES ('sarah.md', '# Sarah Williams

## Personal Information
- Employee ID: E004
- Department: Sales
- Role: Sales Director
- Start Date: 2018-11-10
- Salary: 130000

## Skills
- B2B Sales
- CRM
- Negotiation
- Team Management
');
```

**Effect:** Creates a new file sarah.md in the employees folder

---

## UPDATE Queries

### UPDATE Markdown Table

```sql
-- Update a single task
UPDATE "samples/tasks.md"
SET Status = 'Completed'
WHERE TaskID = 'T001';

-- Update multiple columns
UPDATE "samples/tasks.md"
SET Status = 'In Progress',
    Priority = 'High'
WHERE Assignee = 'E001' AND Status = 'Not Started';

-- Update based on date
UPDATE "samples/tasks.md"
SET Priority = 'Critical'
WHERE DueDate < '2024-01-15' AND Status != 'Completed';
```

**Effect:** Modifies rows in the tasks.md table

### UPDATE List Items

```sql
-- Update project status
UPDATE "samples/projects.md"::lists
SET content = REPLACE(content, 'Status: Planning', 'Status: In Progress')
WHERE content LIKE '%Mobile App Redesign%';

-- Update owner for all projects in a section
UPDATE "samples/projects.md"::lists
SET content = REGEXP_REPLACE(content, 'Owner: E004', 'Owner: E001')
WHERE section = 'Active Projects';
```

**Effect:** Updates list items matching the criteria

### UPDATE Paragraphs

```sql
-- Update meeting notes
UPDATE "samples/notes.md"::paragraphs
SET content = content || '\n\nFollow-up: Review action items with team.'
WHERE heading = 'Team Standup - 2024-01-08';
```

**Effect:** Appends text to the matching paragraph

### UPDATE Files in Folder

```sql
-- Give all engineering employees a raise
UPDATE "samples/employees/"
SET content = REGEXP_REPLACE(
  content,
  '(Salary: )(\d+)',
  'Salary: ' || (CAST('\2' as INTEGER) * 1.10)
)
WHERE content LIKE '%Department: Engineering%';

-- Update role for specific employee
UPDATE "samples/employees/john.md"
SET content = REPLACE(content, 'Role: Senior Developer', 'Role: Principal Engineer');
```

**Effect:** Modifies content in matching files

---

## DELETE Queries

### DELETE from Markdown Table

```sql
-- Delete completed tasks
DELETE FROM "samples/tasks.md"
WHERE Status = 'Completed';

-- Delete tasks assigned to a specific person
DELETE FROM "samples/tasks.md"
WHERE Assignee = 'E003' AND Status = 'Not Started';

-- Delete overdue low-priority tasks
DELETE FROM "samples/tasks.md"
WHERE Priority = 'Low'
  AND DueDate < '2024-01-01'
  AND Status != 'Completed';
```

**Effect:** Removes rows from the tasks.md table

### DELETE List Items

```sql
-- Delete completed projects
DELETE FROM "samples/projects.md"::lists
WHERE section = 'Completed Projects'
  AND content LIKE '%2023%';

-- Delete specific project
DELETE FROM "samples/projects.md"::lists
WHERE content LIKE '%Mobile App Redesign%';
```

**Effect:** Removes list items from projects.md

### DELETE Paragraphs

```sql
-- Delete old meeting notes
DELETE FROM "samples/notes.md"::paragraphs
WHERE date < '2024-01-01';

-- Delete paragraphs by heading pattern
DELETE FROM "samples/notes.md"::paragraphs
WHERE heading LIKE '%Standup%' AND date < '2023-12-01';
```

**Effect:** Removes paragraphs/sections from notes.md

### DELETE Files from Folder

```sql
-- Delete terminated employees
DELETE FROM "samples/employees/"
WHERE content LIKE '%Status: Terminated%';

-- Delete specific file
DELETE FROM "samples/employees/"
WHERE filename = 'bob.md';
```

**Effect:** Deletes files from the employees folder

---

## VIEWS

Views provide virtual tables over markdown content with predefined queries.

### Creating Views

```sql
-- View of high-priority tasks
CREATE VIEW high_priority_tasks AS
SELECT TaskID, Title, Assignee, DueDate
FROM "samples/tasks.md"
WHERE Priority = 'High'
ORDER BY DueDate;

-- View of engineering team
CREATE VIEW engineering_team AS
SELECT
  filename,
  content->>'Employee ID' as emp_id,
  content->>'Role' as role,
  content->>'Salary' as salary
FROM "samples/employees/"
WHERE content->>'Department' = 'Engineering';

-- View combining multiple sources (with JOIN)
CREATE VIEW employee_tasks AS
SELECT
  e.content->>'Employee ID' as emp_id,
  e.filename as employee_name,
  t.Title as task_title,
  t.Status as task_status,
  t.DueDate as due_date
FROM "samples/employees/" e
JOIN "samples/tasks.md" t ON t.Assignee = e.content->>'Employee ID'
WHERE t.Status != 'Completed';
```

### Using Views

```sql
-- Query a view like a regular table
SELECT * FROM high_priority_tasks;

SELECT emp_id, role
FROM engineering_team
WHERE CAST(salary as INTEGER) > 120000;

-- Views can be joined with other tables
SELECT v.emp_id, v.task_title, d.budget
FROM employee_tasks v
JOIN "samples/departments.md"::lists d
  ON v.content->>'Department' = d.heading;
```

### Materialized Views

For better performance, views can be materialized (cached):

```sql
-- Create a materialized view
CREATE MATERIALIZED VIEW active_projects_summary AS
SELECT
  content->>'name' as project_name,
  content->>'owner' as owner,
  content->>'status' as status
FROM "samples/projects.md"::lists
WHERE section = 'Active Projects';

-- Refresh materialized view
REFRESH MATERIALIZED VIEW active_projects_summary;
```

---

## Advanced Features

### Transactions

```sql
BEGIN TRANSACTION;

UPDATE "samples/tasks.md"
SET Assignee = 'E002'
WHERE TaskID = 'T001';

INSERT INTO "samples/tasks.md" (TaskID, Title, Assignee, Priority, Status, DueDate)
VALUES ('T011', 'Knowledge transfer session', 'E001', 'Medium', 'Not Started', '2024-01-20');

COMMIT;
```

### Subqueries

```sql
-- Find employees working on high-priority tasks
SELECT * FROM "samples/employees/"
WHERE content->>'Employee ID' IN (
  SELECT DISTINCT Assignee
  FROM "samples/tasks.md"
  WHERE Priority = 'High'
);
```

### Common Table Expressions (CTEs)

```sql
WITH overdue_tasks AS (
  SELECT Assignee, COUNT(*) as overdue_count
  FROM "samples/tasks.md"
  WHERE DueDate < CURRENT_DATE AND Status != 'Completed'
  GROUP BY Assignee
)
SELECT
  e.filename,
  e.content->>'Employee ID' as emp_id,
  ot.overdue_count
FROM "samples/employees/" e
JOIN overdue_tasks ot ON e.content->>'Employee ID' = ot.Assignee;
```

---

## Operators and Functions

### Content Extraction Operators

- `content->>'field'` - Extract text value from structured content
- `content->'field'` - Extract JSON value from structured content
- `content @> 'text'` - Contains text operator
- `content ~ 'pattern'` - Regex match operator

### String Functions

- `UPPER(str)`, `LOWER(str)` - Case conversion
- `TRIM(str)` - Remove whitespace
- `REPLACE(str, from, to)` - String replacement
- `REGEXP_REPLACE(str, pattern, replacement)` - Regex replacement
- `LENGTH(str)` - String length
- `SUBSTRING(str, start, length)` - Extract substring
- `CONCAT(str1, str2, ...)` - Concatenate strings

### Date Functions

- `CURRENT_DATE` - Today's date
- `CURRENT_TIMESTAMP` - Current date and time
- `DATE(str)` - Parse date string
- `DATE_ADD(date, interval)` - Add time interval
- `DATE_DIFF(date1, date2)` - Difference between dates

### Aggregation Functions

- `COUNT(*)` - Count rows
- `SUM(column)` - Sum values
- `AVG(column)` - Average value
- `MIN(column)`, `MAX(column)` - Min/max values
- `STRING_AGG(column, delimiter)` - Concatenate values

---

## Examples by Use Case

### Project Management

```sql
-- Sprint burndown
SELECT Status, COUNT(*) as count
FROM "samples/tasks.md"
GROUP BY Status;

-- Overdue tasks report
SELECT TaskID, Title, Assignee, DueDate,
       DATE_DIFF(CURRENT_DATE, DueDate) as days_overdue
FROM "samples/tasks.md"
WHERE DueDate < CURRENT_DATE
  AND Status != 'Completed'
ORDER BY days_overdue DESC;
```

### HR Analytics

```sql
-- Headcount by department
SELECT
  content->>'Department' as department,
  COUNT(*) as headcount
FROM "samples/employees/"
GROUP BY content->>'Department';

-- Salary analysis
SELECT
  content->>'Department' as department,
  AVG(CAST(content->>'Salary' as INTEGER)) as avg_salary,
  MIN(CAST(content->>'Salary' as INTEGER)) as min_salary,
  MAX(CAST(content->>'Salary' as INTEGER)) as max_salary
FROM "samples/employees/"
GROUP BY content->>'Department';
```

### Documentation Management

```sql
-- Find all references to a topic
SELECT filename, heading, content
FROM "samples/"::paragraphs
WHERE content LIKE '%authentication%'
ORDER BY filename, line_number;

-- Generate table of contents
SELECT
  filename,
  heading,
  level,
  line_number
FROM "samples/"::headings
ORDER BY filename, line_number;
```

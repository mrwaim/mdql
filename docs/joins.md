# MDQL Joins Specification

## Overview

Joins in MDQL enable combining data from multiple markdown sources, just like SQL joins combine data from multiple database tables. The unique challenge in MDQL is that data sources can be heterogeneous (tables, lists, paragraphs, files) and relationships may be implicit rather than explicit.

---

## Join Types

### 1. INNER JOIN

Returns only rows where the join condition matches in both tables.

```sql
SELECT
  e.content->>'Employee ID' as emp_id,
  e.content->>'Role' as role,
  t.Title as task_title,
  t.Status as status
FROM "samples/employees/" e
INNER JOIN "samples/tasks.md" t
  ON e.content->>'Employee ID' = t.Assignee;
```

**Result:**
| emp_id | role | task_title | status |
|--------|------|------------|--------|
| E001 | Senior Developer | Implement OAuth login | In Progress |
| E001 | Senior Developer | Write API documentation | Not Started |
| E002 | Tech Lead | Set up AWS EKS cluster | In Progress |

### 2. LEFT (OUTER) JOIN

Returns all rows from the left table and matching rows from the right table. Non-matching rows from left table will have NULL for right table columns.

```sql
SELECT
  e.content->>'Employee ID' as emp_id,
  e.filename as name,
  COUNT(t.TaskID) as task_count
FROM "samples/employees/" e
LEFT JOIN "samples/tasks.md" t
  ON e.content->>'Employee ID' = t.Assignee
GROUP BY e.content->>'Employee ID', e.filename;
```

**Result:**
| emp_id | name | task_count |
|--------|------|------------|
| E001 | john.md | 3 |
| E002 | jane.md | 3 |
| E003 | bob.md | 0 |

### 3. RIGHT (OUTER) JOIN

Returns all rows from the right table and matching rows from the left table.

```sql
SELECT
  t.TaskID,
  t.Title,
  e.content->>'Role' as assignee_role
FROM "samples/employees/" e
RIGHT JOIN "samples/tasks.md" t
  ON e.content->>'Employee ID' = t.Assignee;
```

### 4. FULL (OUTER) JOIN

Returns all rows from both tables, with NULL values where matches don't exist.

```sql
SELECT
  COALESCE(e.content->>'Employee ID', t.Assignee) as id,
  e.filename as employee_file,
  t.TaskID as task_id
FROM "samples/employees/" e
FULL OUTER JOIN "samples/tasks.md" t
  ON e.content->>'Employee ID' = t.Assignee;
```

### 5. CROSS JOIN

Returns the Cartesian product of both tables (all possible combinations).

```sql
SELECT
  e.content->>'Employee ID' as emp_id,
  p.content->>'name' as project_name
FROM "samples/employees/" e
CROSS JOIN "samples/projects.md"::lists p
WHERE e.content->>'Department' = 'Engineering'
  AND p.section = 'Active Projects';
```

---

## Join Methods

### Method 1: Field-Based Joins

Join on extracted fields from structured content.

```sql
-- Join employees with their tasks
SELECT
  e.content->>'Employee ID' as emp_id,
  e.content->>'Role' as role,
  t.Title,
  t.Priority
FROM "samples/employees/" e
JOIN "samples/tasks.md" t
  ON e.content->>'Employee ID' = t.Assignee
WHERE t.Status = 'In Progress';
```

### Method 2: Link-Based Joins

Join based on markdown links between files.

```sql
-- Assuming employees/john.md links to tasks
SELECT
  e.filename as employee,
  t.Title as linked_task
FROM "samples/employees/" e
JOIN "samples/tasks.md" t
  ON t.__mdql_file_path = e.__mdql_links->'internal'->>'target';
```

**Example markdown with link:**
```markdown
# John Doe
Currently working on [OAuth implementation](../tasks.md#t001)
```

### Method 3: Pattern-Based Joins

Join using text patterns and regex matching.

```sql
-- Join meeting notes that mention employees
SELECT
  e.content->>'Employee ID' as emp_id,
  n.heading as meeting,
  n.content
FROM "samples/employees/" e
JOIN "samples/notes.md"::paragraphs n
  ON n.content ~ ('\\b' || SUBSTRING(e.filename FROM '(.+)\.md') || '\\b');
```

### Method 4: Hierarchical Joins

Join based on file/folder hierarchy.

```sql
-- Join department info with employees in that department
SELECT
  d.content->>'name' as department,
  d.content->>'Budget' as budget,
  e.filename as employee,
  e.content->>'Salary' as salary
FROM "samples/departments.md"::lists d
JOIN "samples/employees/" e
  ON e.content->>'Department' = d.heading;
```

### Method 5: Content-Based Joins

Join based on content similarity or keywords.

```sql
-- Find meeting notes related to specific projects
SELECT
  p.content->>'name' as project,
  n.heading as meeting,
  MDQL_SIMILARITY(p.content, n.content) as relevance
FROM "samples/projects.md"::lists p
JOIN "samples/notes.md"::paragraphs n
  ON MDQL_SIMILARITY(p.content, n.content) > 0.5
WHERE p.section = 'Active Projects';
```

### Method 6: Tag-Based Joins

Join based on tags or categories.

```sql
-- Assuming frontmatter with tags
SELECT
  doc1.title,
  doc2.title,
  doc1.__mdql_frontmatter->>'tags' as shared_tags
FROM "docs/"::files doc1
JOIN "docs/"::files doc2
  ON doc1.__mdql_frontmatter->>'tags' @> doc2.__mdql_frontmatter->>'tags'
WHERE doc1.filename != doc2.filename;
```

---

## Multi-Way Joins

Joining more than two tables:

```sql
-- Employees, their tasks, and department info
SELECT
  e.content->>'Employee ID' as emp_id,
  e.filename as name,
  d.content->>'Budget' as dept_budget,
  t.Title as task,
  t.DueDate
FROM "samples/employees/" e
JOIN "samples/departments.md"::lists d
  ON e.content->>'Department' = d.heading
JOIN "samples/tasks.md" t
  ON e.content->>'Employee ID' = t.Assignee
WHERE t.Status != 'Completed'
ORDER BY e.filename, t.DueDate;
```

**Result:**
| emp_id | name | dept_budget | task | DueDate |
|--------|------|-------------|------|---------|
| E001 | john.md | 2500000 | Implement OAuth login | 2024-01-15 |
| E001 | john.md | 2500000 | Write API documentation | 2024-01-25 |
| E002 | jane.md | 2500000 | Set up AWS EKS cluster | 2024-01-20 |

---

## Self-Joins

Joining a table with itself:

```sql
-- Find employees in the same department
SELECT
  e1.content->>'Employee ID' as emp1,
  e2.content->>'Employee ID' as emp2,
  e1.content->>'Department' as department
FROM "samples/employees/" e1
JOIN "samples/employees/" e2
  ON e1.content->>'Department' = e2.content->>'Department'
  AND e1.filename < e2.filename
ORDER BY department, emp1;
```

**Result:**
| emp1 | emp2 | department |
|------|------|------------|
| E001 | E002 | Engineering |

```sql
-- Find tasks with the same assignee
SELECT
  t1.TaskID as task1,
  t2.TaskID as task2,
  t1.Assignee,
  t1.Status as task1_status,
  t2.Status as task2_status
FROM "samples/tasks.md" t1
JOIN "samples/tasks.md" t2
  ON t1.Assignee = t2.Assignee
  AND t1.TaskID < t2.TaskID;
```

---

## Join Conditions

### Equality Joins

```sql
ON table1.column = table2.column
```

### Non-Equality Joins

```sql
-- Greater than
ON table1.salary > table2.min_salary

-- Range joins
ON table1.date BETWEEN table2.start_date AND table2.end_date

-- Not equal
ON table1.id != table2.id
```

### Complex Conditions

```sql
-- Multiple conditions
ON table1.dept = table2.dept
  AND table1.location = table2.location

-- With OR logic
ON (table1.email = table2.contact_email OR table1.phone = table2.contact_phone)

-- With functions
ON LOWER(table1.name) = LOWER(table2.employee_name)
```

---

## Special Join Scenarios

### 1. Joining Different Content Types

Join a markdown table with list items:

```sql
SELECT
  t.Title as task,
  p.content->>'name' as project,
  p.content->>'status' as project_status
FROM "samples/tasks.md" t
JOIN "samples/projects.md"::lists p
  ON t.Title LIKE ('%' || p.content->>'name' || '%')
WHERE p.section = 'Active Projects';
```

### 2. Joining Paragraphs with Tables

```sql
-- Find meeting notes that discuss specific tasks
SELECT
  n.heading as meeting,
  t.TaskID,
  t.Title
FROM "samples/notes.md"::paragraphs n
JOIN "samples/tasks.md" t
  ON n.content LIKE ('%' || t.TaskID || '%')
ORDER BY n.heading;
```

### 3. Folder-to-File Joins

```sql
-- Join all employee files with a summary table
SELECT
  s.EmployeeID,
  s.Performance,
  e.content->>'Role' as current_role,
  e.content->>'Salary' as salary
FROM "summaries/performance.md" s
JOIN "samples/employees/" e
  ON s.EmployeeID = e.content->>'Employee ID';
```

### 4. Cross-Repository Joins

```sql
-- Join files from different markdown repositories
SELECT
  hr.content->>'Employee ID' as emp_id,
  hr.content->>'Start Date' as start_date,
  proj.content->>'Project' as project
FROM "hr-repo/employees/" hr
JOIN "project-repo/assignments.md"::lists proj
  ON hr.content->>'Employee ID' = proj.content->>'Assignee';
```

---

## Implicit Relationships

MDQL can infer relationships without explicit foreign keys:

### 1. Wiki-Link Relationships

```sql
-- Auto-join based on wiki-style links [[...]]
SELECT
  source.__mdql_file_path as from_file,
  target.__mdql_file_path as to_file,
  link.text as link_text
FROM "docs/"::files source
JOIN MDQL_LINKS(source) link
JOIN "docs/"::files target
  ON target.__mdql_file_path = link.target;
```

### 2. Reference Extraction

```sql
-- Extract and join on ID references in text
SELECT
  n.heading as meeting,
  t.Title as mentioned_task
FROM "samples/notes.md"::paragraphs n
JOIN "samples/tasks.md" t
  ON MDQL_EXTRACT_IDS(n.content, 'T\d+') @> ARRAY[t.TaskID];
```

### 3. Tag Relationships

```sql
-- Join on shared tags (from frontmatter or inline)
SELECT
  doc1.title,
  doc2.title,
  ARRAY_AGG(tag) as shared_tags
FROM "docs/" doc1
CROSS JOIN UNNEST(doc1.__mdql_tags) as tag
JOIN "docs/" doc2
  ON tag = ANY(doc2.__mdql_tags)
WHERE doc1.filename != doc2.filename
GROUP BY doc1.title, doc2.title;
```

---

## Join Performance

### Optimization Strategies

#### 1. Index on Join Keys

```sql
-- Create index for faster joins
CREATE INDEX idx_employee_id
ON "samples/tasks.md" (Assignee);

CREATE INDEX idx_dept
ON "samples/employees/"::files (content->>'Department');
```

#### 2. Selective Filtering

```sql
-- Filter before joining (more efficient)
SELECT e.*, t.*
FROM (
  SELECT * FROM "samples/employees/"
  WHERE content->>'Department' = 'Engineering'
) e
JOIN "samples/tasks.md" t
  ON e.content->>'Employee ID' = t.Assignee;
```

#### 3. Materialized Views

```sql
-- Pre-compute expensive joins
CREATE MATERIALIZED VIEW employee_task_summary AS
SELECT
  e.content->>'Employee ID' as emp_id,
  e.filename as name,
  COUNT(t.TaskID) as total_tasks,
  SUM(CASE WHEN t.Status = 'Completed' THEN 1 ELSE 0 END) as completed_tasks
FROM "samples/employees/" e
LEFT JOIN "samples/tasks.md" t
  ON e.content->>'Employee ID' = t.Assignee
GROUP BY e.content->>'Employee ID', e.filename;
```

---

## Practical Examples

### Example 1: Employee Dashboard

```sql
-- Comprehensive employee view with tasks and department
SELECT
  e.content->>'Employee ID' as emp_id,
  e.filename as name,
  e.content->>'Role' as role,
  d.content->>'Budget' as dept_budget,
  COUNT(t.TaskID) as active_tasks,
  COUNT(CASE WHEN t.Priority = 'High' THEN 1 END) as high_priority_count
FROM "samples/employees/" e
JOIN "samples/departments.md"::lists d
  ON e.content->>'Department' = d.heading
LEFT JOIN "samples/tasks.md" t
  ON e.content->>'Employee ID' = t.Assignee
  AND t.Status != 'Completed'
GROUP BY
  e.content->>'Employee ID',
  e.filename,
  e.content->>'Role',
  d.content->>'Budget'
ORDER BY high_priority_count DESC, active_tasks DESC;
```

### Example 2: Project Progress Report

```sql
-- Projects with task completion rates
SELECT
  p.content->>'name' as project,
  p.content->>'owner' as owner,
  COUNT(t.TaskID) as total_tasks,
  SUM(CASE WHEN t.Status = 'Completed' THEN 1 ELSE 0 END) as completed,
  ROUND(100.0 * SUM(CASE WHEN t.Status = 'Completed' THEN 1 ELSE 0 END) / COUNT(t.TaskID), 2) as completion_rate
FROM "samples/projects.md"::lists p
LEFT JOIN "samples/tasks.md" t
  ON t.Title LIKE ('%' || p.content->>'name' || '%')
WHERE p.section = 'Active Projects'
GROUP BY p.content->>'name', p.content->>'owner'
ORDER BY completion_rate DESC;
```

### Example 3: Meeting Mentions Analysis

```sql
-- Which employees are mentioned most in meetings
SELECT
  e.content->>'Employee ID' as emp_id,
  e.filename as name,
  COUNT(n.heading) as mention_count,
  STRING_AGG(n.heading, ', ') as meetings
FROM "samples/employees/" e
JOIN "samples/notes.md"::paragraphs n
  ON n.content ILIKE ('%' || SUBSTRING(e.filename FROM '(.+)\.md') || '%')
GROUP BY e.content->>'Employee ID', e.filename
ORDER BY mention_count DESC;
```

### Example 4: Skills Matrix

```sql
-- Find employees with specific skills mentioned in projects
SELECT
  e.content->>'Employee ID' as emp_id,
  e.filename as name,
  s.skill,
  COUNT(p.content) as relevant_projects
FROM "samples/employees/" e
CROSS JOIN UNNEST(
  STRING_TO_ARRAY(
    REGEXP_REPLACE(e.content, '.*## Skills\n(.*?)\n\n##.*', '\1', 'ns'),
    '\n- '
  )
) as s(skill)
JOIN "samples/projects.md"::lists p
  ON p.content ILIKE ('%' || s.skill || '%')
WHERE s.skill != ''
GROUP BY e.content->>'Employee ID', e.filename, s.skill
ORDER BY relevant_projects DESC;
```

### Example 5: Workload Balance

```sql
-- Compare workload across departments
SELECT
  d.heading as department,
  COUNT(DISTINCT e.filename) as employee_count,
  COUNT(t.TaskID) as total_tasks,
  ROUND(COUNT(t.TaskID)::NUMERIC / COUNT(DISTINCT e.filename), 2) as tasks_per_employee
FROM "samples/departments.md"::lists d
LEFT JOIN "samples/employees/" e
  ON e.content->>'Department' = d.heading
LEFT JOIN "samples/tasks.md" t
  ON e.content->>'Employee ID' = t.Assignee
  AND t.Status != 'Completed'
GROUP BY d.heading
ORDER BY tasks_per_employee DESC;
```

---

## Advanced Join Techniques

### 1. Lateral Joins (Correlated Subqueries)

```sql
-- For each employee, get their 3 most urgent tasks
SELECT
  e.content->>'Employee ID' as emp_id,
  e.filename as name,
  recent_tasks.*
FROM "samples/employees/" e
CROSS JOIN LATERAL (
  SELECT Title, Priority, DueDate
  FROM "samples/tasks.md"
  WHERE Assignee = e.content->>'Employee ID'
  ORDER BY
    CASE Priority
      WHEN 'High' THEN 1
      WHEN 'Medium' THEN 2
      ELSE 3
    END,
    DueDate
  LIMIT 3
) recent_tasks;
```

### 2. Recursive Joins (For Hierarchies)

```sql
-- Build org chart from employee reports-to relationships
WITH RECURSIVE org_chart AS (
  -- Base case: top-level managers
  SELECT
    content->>'Employee ID' as emp_id,
    content->>'Role' as role,
    NULL::TEXT as manager_id,
    1 as level
  FROM "samples/employees/"
  WHERE content->>'Manager ID' IS NULL

  UNION ALL

  -- Recursive case: employees reporting to managers
  SELECT
    e.content->>'Employee ID',
    e.content->>'Role',
    e.content->>'Manager ID',
    oc.level + 1
  FROM "samples/employees/" e
  JOIN org_chart oc
    ON e.content->>'Manager ID' = oc.emp_id
)
SELECT * FROM org_chart
ORDER BY level, emp_id;
```

### 3. Join with Window Functions

```sql
-- Rank employees by task completion within their department
SELECT
  e.content->>'Employee ID' as emp_id,
  e.content->>'Department' as department,
  COUNT(CASE WHEN t.Status = 'Completed' THEN 1 END) as completed_tasks,
  RANK() OVER (
    PARTITION BY e.content->>'Department'
    ORDER BY COUNT(CASE WHEN t.Status = 'Completed' THEN 1 END) DESC
  ) as dept_rank
FROM "samples/employees/" e
LEFT JOIN "samples/tasks.md" t
  ON e.content->>'Employee ID' = t.Assignee
GROUP BY e.content->>'Employee ID', e.content->>'Department';
```

---

## Join Troubleshooting

### Common Issues

#### 1. Cartesian Product (Accidental CROSS JOIN)

```sql
-- Wrong: Missing join condition
SELECT * FROM "samples/employees/" e, "samples/tasks.md" t;

-- Correct: With join condition
SELECT * FROM "samples/employees/" e
JOIN "samples/tasks.md" t
  ON e.content->>'Employee ID' = t.Assignee;
```

#### 2. Type Mismatches

```sql
-- Wrong: Comparing different types
ON employee.id = task.assignee_id

-- Correct: Cast if needed
ON CAST(employee.id as TEXT) = task.assignee_id
```

#### 3. NULL Handling

```sql
-- Consider NULL values in joins
SELECT *
FROM "samples/employees/" e
LEFT JOIN "samples/tasks.md" t
  ON e.content->>'Employee ID' = t.Assignee
WHERE t.TaskID IS NOT NULL  -- Excludes employees with no tasks
   OR t.TaskID IS NULL;      -- Includes employees with no tasks
```

---

## Future Enhancements

### Graph-Based Joins

```sql
-- Query relationships as a graph
SELECT *
FROM MDQL_GRAPH('docs/')
WHERE relationship_type = 'links_to'
  AND depth <= 3;
```

### Semantic Joins

```sql
-- Join based on semantic similarity
SELECT *
FROM "docs/file1.md"::paragraphs p1
SEMANTIC JOIN "docs/file2.md"::paragraphs p2
  ON MDQL_EMBEDDING_SIMILARITY(p1.content, p2.content) > 0.8;
```

### Time-Travel Joins

```sql
-- Join with historical versions (git integration)
SELECT
  current.content as current_content,
  historical.content as last_week_content
FROM "docs/file.md"::paragraphs current
JOIN "docs/file.md"::paragraphs@'2024-01-01' historical
  ON current.row_id = historical.row_id;
```

# MDQL Query Examples

Sample queries for using `mdql-query.py` with the todo.md file.

## Basic Queries

### 1. All Todo Items

```bash
./mdql-query.py todo.md "SELECT * FROM todo.md"
```

**Output:**
```
status | text                                    | section                  | notes
-------+-----------------------------------------+--------------------------+------
☐      | Design notification system architecture | Task Notification System | 2
☐      | Implement job time estimates feature    | Task Notification System | 2
...
```

### 2. Incomplete Todo Items

```bash
./mdql-query.py todo.md "SELECT * FROM todo.md WHERE completed = false"
```

Shows all tasks with `- [ ]` (unchecked checkboxes).

### 3. Completed Todo Items

```bash
./mdql-query.py todo.md "SELECT text, section FROM todo.md WHERE completed = true"
```

**Output:**
```
text                                          | section
----------------------------------------------+---------------------------------
Explore mocktail event co-hosting with Saqib  | MAPS Community Organization
Follow up on final date confirmation from ... | Open Mosque Project
Schedule time with dad for interview          | Dad Interview
Complete first version with 30 challenges     | Photo Lab - Kids Camera Project
Integrate OpenAI for photo evaluation         | Photo Lab - Kids Camera Project

5 result(s)
```

## Filtered Queries

### 4. High Priority Incomplete Tasks

```bash
./mdql-query.py todo.md "SELECT text, section, priority FROM todo.md WHERE priority = 'High' AND completed = false"
```

**Output:**
```
text                                                          | section                  | priority
--------------------------------------------------------------+--------------------------+---------
Check on marketing status with Sr Mallak (deadline was 12/19) | Open Mosque Project      | High
Follow up with Sr Mallak on volunteer confirmations           | Open Mosque Project      | High
Begin inviting immediate circle to event                      | Open Mosque Project      | High
Get kids camera to initial better version                     | Kids Camera with Aafiyah | High
...
```

### 5. Tasks in Specific Section

```bash
./mdql-query.py todo.md "SELECT * FROM todo.md WHERE section = 'Open Mosque Project'"
```

### 6. Top-Level Incomplete Tasks

```bash
./mdql-query.py todo.md "SELECT text, section FROM todo.md WHERE completed = false AND indent_level = 0"
```

Shows only tasks at indent level 0 (not nested under other tasks).

## Search Queries

### 7. Search in Task Text

```bash
./mdql-query.py todo.md "SELECT text, section FROM todo.md WHERE text LIKE '%camera%'"
```

**Output:**
```
text                                      | section
------------------------------------------+---------------------------------
Show Aafiyah the candidate names for c... | Camera App Development
Get kids camera to initial better version | Kids Camera with Aafiyah
Add camera feature challenges             | Photo Lab - Kids Camera Project

3 result(s)
```

### 8. Tasks with Notes

```bash
./mdql-query.py todo.md "SELECT text, notes FROM todo.md WHERE has_notes = true"
```

Shows tasks that have descriptive bullet points underneath them.

### 9. Search in Notes

```bash
./mdql-query.py todo.md "SELECT text, section FROM todo.md WHERE text LIKE '%Example%'"
```

Searches within the notes/descriptions field.

## Output Formats

### Simple Format (List)

```bash
./mdql-query.py todo.md "SELECT * FROM todo.md WHERE priority = 'High'" --format simple
```

**Output:**
```
☐ Check on marketing status with Sr Mallak (deadline was 12/19)
☐ Follow up with Sr Mallak on volunteer confirmations
☐ Begin inviting immediate circle to event
...

20 result(s)
```

### Count Only

```bash
./mdql-query.py todo.md "SELECT * FROM todo.md WHERE has_notes = true" --format count
```

**Output:**
```
56
```

### Custom Columns

```bash
./mdql-query.py todo.md "SELECT status, text, priority FROM todo.md WHERE completed = false" --columns "status,text,priority,notes"
```

## Combined Filters

### 10. High Priority with Notes

```bash
./mdql-query.py todo.md "SELECT text, section, notes FROM todo.md WHERE priority = 'High' AND has_notes = true"
```

### 11. Incomplete Top-Level High Priority

```bash
./mdql-query.py todo.md "SELECT text, section FROM todo.md WHERE completed = false AND indent_level = 0 AND priority = 'High'"
```

## Advanced Examples

### 12. Tasks by Status

```bash
./mdql-query.py todo.md "SELECT text, section FROM todo.md WHERE status = 'In Progress'"
```

### 13. Limited Results

```bash
./mdql-query.py todo.md "SELECT * FROM todo.md" --limit 10
```

Shows only first 10 results.

### 14. Section-Specific Incomplete Tasks

```bash
./mdql-query.py todo.md "SELECT text FROM todo.md WHERE section = 'Photo Lab - Kids Camera Project' AND completed = false"
```

## Available Columns

- `status` - ✓ or ☐
- `text` - Task description
- `section` - Section name
- `line` - Line number in file
- `indent` - Indentation level
- `completed` - true/false
- `notes` - Number of note items
- `has_notes` - yes/no
- `priority` - Priority from section metadata
- `section_status` - Status from section metadata
- `notes_text` - Preview of notes content

## Available Filters (WHERE clause)

- `completed = true|false` - Completion status
- `section = 'name'` - Section name (exact match)
- `priority = 'High|Medium|Low'` - Priority level
- `status = 'name'` - Status value
- `indent_level = N` - Indentation level (0 = top-level)
- `has_notes = true|false` - Has descriptive notes
- `text LIKE '%search%'` - Search in task text
- `notes LIKE '%search%'` - Search in notes

## Tips

1. **Use quotes** around query strings with spaces
2. **Combine filters** with AND
3. **Use LIKE** with % wildcards for partial matches
4. **Limit results** with --limit for large files
5. **Choose format** with --format (table, simple, count)
6. **Select columns** to customize output

## Full Syntax

```
mdql-query.py <file.md> "SELECT <columns> FROM <file> [WHERE <conditions>]" [options]
```

**Options:**
- `--limit N` - Limit results to N items
- `--format table|simple|count` - Output format
- `--columns col1,col2,...` - Custom column selection

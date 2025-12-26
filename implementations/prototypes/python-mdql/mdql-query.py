#!/usr/bin/env python3
"""
MDQL Query CLI - Query markdown files using MDQL (SQL-like) syntax

Usage:
  mdql-query.py <file.md> <query>

MDQL Query Syntax:
  SELECT <columns> FROM <file>::task_lists WHERE <conditions>

Examples:
  # All tasks
  mdql-query.py todo.md "SELECT * FROM todo.md"

  # Incomplete tasks
  mdql-query.py todo.md "SELECT * FROM todo.md WHERE completed = false"

  # High priority incomplete tasks
  mdql-query.py todo.md "SELECT text, section FROM todo.md WHERE priority = 'High' AND completed = false"

  # Tasks in specific section
  mdql-query.py todo.md "SELECT * FROM todo.md WHERE section = 'Open Mosque Project'"

  # Tasks with notes
  mdql-query.py todo.md "SELECT text, notes FROM todo.md WHERE has_notes = true"

  # Search in text
  mdql-query.py todo.md "SELECT * FROM todo.md WHERE text LIKE '%camera%'"

  # Combined filters
  mdql-query.py todo.md "SELECT * FROM todo.md WHERE priority = 'High' AND indent_level = 0"
"""

import argparse
import sys
import os
import re
from typing import List, Any, Dict, Optional
from mdql import MDQL, TaskItem


def parse_mdql_query(query: str) -> Dict[str, Any]:
    """Parse a simple MDQL SELECT query."""
    query = query.strip()

    # Pattern: SELECT <columns> FROM <file> [WHERE <conditions>]
    select_pattern = r'SELECT\s+(.+?)\s+FROM\s+(.+?)(?:\s+WHERE\s+(.+))?$'
    match = re.match(select_pattern, query, re.IGNORECASE | re.DOTALL)

    if not match:
        raise ValueError("Invalid MDQL query. Expected: SELECT ... FROM ... [WHERE ...]")

    columns_str = match.group(1).strip()
    from_str = match.group(2).strip()
    where_str = match.group(3).strip() if match.group(3) else None

    # Parse columns
    if columns_str == '*':
        columns = ['status', 'text', 'section', 'notes']
    else:
        columns = [c.strip() for c in columns_str.split(',')]

    # Parse file (remove quotes and ::task_lists if present)
    file_path = from_str.replace('"', '').replace("'", '').split('::')[0]

    # Parse WHERE clause
    filters = {}
    if where_str:
        filters = parse_where_clause(where_str)

    return {
        'columns': columns,
        'file': file_path,
        'filters': filters
    }


def parse_where_clause(where_str: str) -> Dict[str, Any]:
    """Parse WHERE clause into filters."""
    filters = {}

    # Split by AND (simple parser, doesn't handle OR or complex expressions)
    conditions = re.split(r'\s+AND\s+', where_str, flags=re.IGNORECASE)

    for condition in conditions:
        condition = condition.strip()

        # Handle LIKE
        like_match = re.match(r"(\w+)\s+LIKE\s+['\"]%?(.+?)%?['\"]", condition, re.IGNORECASE)
        if like_match:
            field = like_match.group(1).lower()
            value = like_match.group(2)

            if field == 'text':
                filters['text_contains'] = value
            elif field == 'notes':
                filters['notes_contains'] = value
            continue

        # Handle = comparison
        eq_match = re.match(r"(\w+)\s*=\s*(.+)", condition, re.IGNORECASE)
        if eq_match:
            field = eq_match.group(1).strip().lower()
            value = eq_match.group(2).strip().strip("'\"")

            if field == 'completed':
                filters['completed'] = value.lower() in ('true', '1', 'yes')
            elif field == 'section':
                filters['section'] = value
            elif field == 'priority':
                filters['priority'] = value
            elif field == 'status':
                filters['status'] = value
            elif field in ('indent_level', 'indent'):
                filters['indent_level'] = int(value)
            elif field == 'has_notes':
                filters['has_notes'] = value.lower() in ('true', '1', 'yes')
            continue

    return filters


def format_table(data: List[Dict[str, Any]], columns: List[str]) -> str:
    """Format data as an ASCII table."""
    if not data:
        return "No results found."

    # Calculate column widths
    widths = {}
    for col in columns:
        widths[col] = len(col)
        for row in data:
            value = str(row.get(col, ''))
            widths[col] = max(widths[col], len(value))

    # Cap maximum width
    max_width = 70
    for col in columns:
        widths[col] = min(widths[col], max_width)

    # Build header
    header = " | ".join(col.ljust(widths[col]) for col in columns)
    separator = "-+-".join("-" * widths[col] for col in columns)

    # Build rows
    rows = []
    for row in data:
        row_str = " | ".join(
            str(row.get(col, ''))[:widths[col]].ljust(widths[col])
            for col in columns
        )
        rows.append(row_str)

    return "\n".join([header, separator] + rows)


def task_to_dict(task: TaskItem, mdql: MDQL) -> Dict[str, Any]:
    """Convert a TaskItem to a dictionary for display."""
    row = {
        'status': '✓' if task.completed else '☐',
        'text': task.text,
        'section': task.section,
        'line': task.line_number,
        'indent': task.indent_level,
        'completed': task.completed,
        'notes': len(task.notes) if task.notes else 0,
        'has_notes': 'yes' if task.notes else 'no',
        'priority': '',
    }

    # Add priority from section metadata if available
    if task.section in mdql.sections:
        section_meta = mdql.sections[task.section]
        if section_meta.priority:
            row['priority'] = section_meta.priority
        if section_meta.status:
            row['section_status'] = section_meta.status

    # Add notes text if requested (truncated)
    if task.notes:
        notes_preview = '; '.join(task.notes[:2])
        if len(notes_preview) > 100:
            notes_preview = notes_preview[:97] + '...'
        row['notes_text'] = notes_preview

    return row


def main():
    parser = argparse.ArgumentParser(
        description='Query markdown files using MDQL (SQL-like) syntax',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
MDQL Query Examples:

  All tasks:
    %(prog)s todo.md "SELECT * FROM todo.md"

  Incomplete tasks:
    %(prog)s todo.md "SELECT * FROM todo.md WHERE completed = false"

  High priority tasks:
    %(prog)s todo.md "SELECT text, section, priority FROM todo.md WHERE priority = 'High'"

  Incomplete high priority tasks:
    %(prog)s todo.md "SELECT * FROM todo.md WHERE priority = 'High' AND completed = false"

  Tasks in section:
    %(prog)s todo.md "SELECT * FROM todo.md WHERE section = 'Open Mosque Project'"

  Search in text:
    %(prog)s todo.md "SELECT * FROM todo.md WHERE text LIKE '%camera%'"

  Tasks with notes:
    %(prog)s todo.md "SELECT text, notes FROM todo.md WHERE has_notes = true"

  Top-level incomplete tasks:
    %(prog)s todo.md "SELECT * FROM todo.md WHERE completed = false AND indent_level = 0"
        """
    )

    parser.add_argument('file', help='Markdown file to query')
    parser.add_argument('query', help='MDQL query string')
    parser.add_argument('--limit', type=int,
                        help='Limit number of results')
    parser.add_argument('--format', choices=['table', 'simple', 'count'],
                        default='table',
                        help='Output format (default: table)')

    args = parser.parse_args()

    # Check file exists
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    # Parse query
    try:
        parsed = parse_mdql_query(args.query)
    except Exception as e:
        print(f"Error parsing query: {e}", file=sys.stderr)
        print("\nExpected format: SELECT <columns> FROM <file> [WHERE <conditions>]")
        return 1

    # Load file (use file from query or argument)
    query_file = parsed['file'] if parsed['file'] else args.file
    if not os.path.exists(query_file):
        # Try relative to args.file
        query_file = args.file

    try:
        mdql = MDQL(query_file)
    except Exception as e:
        print(f"Error loading file: {e}", file=sys.stderr)
        return 1

    # Execute query
    filters = parsed['filters']
    if filters:
        results = mdql.query(**filters)
    else:
        results = mdql.tasks

    # Apply limit
    if args.limit:
        results = results[:args.limit]

    # Output based on format
    if args.format == 'count':
        print(len(results))
        return 0

    if args.format == 'simple':
        for task in results:
            status = '✓' if task.completed else '☐'
            print(f"{status} {task.text}")
        print(f"\n{len(results)} result(s)")
        return 0

    # Table format
    columns = parsed['columns']

    # Convert tasks to dict format
    data = [task_to_dict(task, mdql) for task in results]

    print(format_table(data, columns))
    print(f"\n{len(results)} result(s)")

    return 0


if __name__ == '__main__':
    sys.exit(main())

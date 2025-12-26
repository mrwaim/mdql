"""
MDQL (Markdown Query Language) Prototype
A simple Python implementation for parsing and manipulating markdown task lists.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class SectionMetadata:
    """Metadata extracted from section headers."""
    section_name: str
    section_level: int
    line_number: int
    source_file: Optional[str] = None
    source_date: Optional[str] = None
    source_time: Optional[str] = None
    updated_file: Optional[str] = None
    updated_date: Optional[str] = None
    updated_time: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    properties: Dict[str, str] = field(default_factory=dict)


@dataclass
class TaskItem:
    """Represents a single task list item."""
    text: str
    completed: bool
    section: str
    section_level: int
    indent_level: int
    line_number: int
    parent_line: Optional[int] = None
    has_children: bool = False
    children: List['TaskItem'] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)  # Non-checkbox bullet points under this task

    def __repr__(self):
        status = "✓" if self.completed else "☐"
        indent = "  " * self.indent_level
        notes_str = f" [{len(self.notes)} notes]" if self.notes else ""
        return f"{indent}{status} {self.text}{notes_str} (line {self.line_number})"


class MDQLParser:
    """Parser for markdown files with task lists."""

    # Regular expressions
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$')
    TASK_PATTERN = re.compile(r'^(\s*)- \[([ xX])\]\s+(.+)$')
    NOTE_PATTERN = re.compile(r'^(\s*)- (.+)$')  # Regular bullet without checkbox
    SOURCE_PATTERN = re.compile(r'^\*Source:\s*(.+?\.md)\s*\((.+?)\)\*$')
    UPDATED_PATTERN = re.compile(r'^\*Updated:\s*(.+?\.md)\s*\((.+?)\)\*$')
    PROPERTY_PATTERN = re.compile(r'^\*\*(.+?):\*\*\s+(.+)$')

    def __init__(self):
        self.tasks: List[TaskItem] = []
        self.sections: Dict[str, SectionMetadata] = {}
        self.current_section: Optional[str] = None
        self.current_section_level: int = 0
        self.lines: List[str] = []

    def parse_file(self, filepath: str) -> Dict[str, Any]:
        """Parse a markdown file and extract task lists and metadata."""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.lines = f.readlines()

        self._parse_content()

        return {
            'tasks': self.tasks,
            'sections': self.sections,
            'lines': self.lines
        }

    def _parse_content(self):
        """Parse the content line by line."""
        parent_stack: List[tuple] = []  # Stack of (indent_level, task)
        current_section_meta: Optional[SectionMetadata] = None
        last_task: Optional[TaskItem] = None

        for line_num, line in enumerate(self.lines, start=1):
            line_stripped = line.rstrip('\n')

            # Check for heading
            heading_match = self.HEADING_PATTERN.match(line_stripped)
            if heading_match:
                level = len(heading_match.group(1))
                section_name = heading_match.group(2)
                self.current_section = section_name
                self.current_section_level = level

                current_section_meta = SectionMetadata(
                    section_name=section_name,
                    section_level=level,
                    line_number=line_num
                )
                self.sections[section_name] = current_section_meta
                parent_stack.clear()
                last_task = None
                continue

            # Check for source metadata
            if current_section_meta:
                source_match = self.SOURCE_PATTERN.match(line_stripped)
                if source_match:
                    current_section_meta.source_file = source_match.group(1)
                    date_time = source_match.group(2)
                    self._parse_datetime(date_time, current_section_meta, 'source')
                    continue

                # Check for updated metadata
                updated_match = self.UPDATED_PATTERN.match(line_stripped)
                if updated_match:
                    current_section_meta.updated_file = updated_match.group(1)
                    date_time = updated_match.group(2)
                    self._parse_datetime(date_time, current_section_meta, 'updated')
                    continue

                # Check for property metadata
                prop_match = self.PROPERTY_PATTERN.match(line_stripped)
                if prop_match:
                    key = prop_match.group(1)
                    value = prop_match.group(2)

                    # Special handling for known properties
                    if key == 'Priority':
                        current_section_meta.priority = value
                    elif key == 'Status':
                        current_section_meta.status = value
                    else:
                        current_section_meta.properties[key] = value
                    continue

            # Check for task item (checkbox)
            task_match = self.TASK_PATTERN.match(line_stripped)
            if task_match:
                indent = task_match.group(1)
                check = task_match.group(2)
                text = task_match.group(3)

                indent_level = len(indent) // 2
                completed = check.lower() == 'x'

                task = TaskItem(
                    text=text,
                    completed=completed,
                    section=self.current_section or "Untitled",
                    section_level=self.current_section_level,
                    indent_level=indent_level,
                    line_number=line_num
                )

                # Determine parent
                while parent_stack and parent_stack[-1][0] >= indent_level:
                    parent_stack.pop()

                if parent_stack:
                    parent_indent, parent_task = parent_stack[-1]
                    task.parent_line = parent_task.line_number
                    parent_task.has_children = True
                    parent_task.children.append(task)

                parent_stack.append((indent_level, task))
                self.tasks.append(task)
                last_task = task
                continue

            # Check for note items (regular bullets without checkbox)
            note_match = self.NOTE_PATTERN.match(line_stripped)
            if note_match and last_task:
                indent = note_match.group(1)
                note_text = note_match.group(2)
                note_indent_level = len(indent) // 2

                # Only add as note if it's indented more than the last task
                # This ensures we're capturing sub-items, not unrelated bullets
                if note_indent_level > last_task.indent_level:
                    last_task.notes.append(note_text)
                    continue

    def _parse_datetime(self, date_time_str: str, metadata: SectionMetadata, prefix: str):
        """Parse date and optional time from string."""
        parts = date_time_str.split()
        if parts:
            setattr(metadata, f"{prefix}_date", parts[0])
            if len(parts) > 1:
                setattr(metadata, f"{prefix}_time", parts[1])


class MDQLWriter:
    """Writer for updating markdown files."""

    def __init__(self, lines: List[str]):
        self.lines = lines.copy()

    def update_task_completion(self, line_number: int, completed: bool) -> None:
        """Toggle task completion status."""
        if 1 <= line_number <= len(self.lines):
            line = self.lines[line_number - 1]
            if completed:
                # Mark as complete
                self.lines[line_number - 1] = re.sub(r'- \[ \]', '- [x]', line)
            else:
                # Mark as incomplete
                self.lines[line_number - 1] = re.sub(r'- \[x\]', '- [ ]', line, flags=re.IGNORECASE)

    def update_task_text(self, line_number: int, new_text: str) -> None:
        """Update task text."""
        if 1 <= line_number <= len(self.lines):
            line = self.lines[line_number - 1]
            # Replace text after checkbox
            self.lines[line_number - 1] = re.sub(
                r'(- \[[ xX]\]\s+)(.+)$',
                r'\1' + new_text,
                line
            )

    def delete_task(self, line_number: int) -> None:
        """Delete a task line."""
        if 1 <= line_number <= len(self.lines):
            self.lines[line_number - 1] = None  # Mark for deletion

    def insert_task(self, line_number: int, text: str, indent_level: int = 0, completed: bool = False) -> None:
        """Insert a new task at specified line."""
        indent = "  " * indent_level
        check = "x" if completed else " "
        new_line = f"{indent}- [{check}] {text}\n"
        self.lines.insert(line_number - 1, new_line)

    def write_file(self, filepath: str) -> None:
        """Write the modified content back to file."""
        # Filter out deleted lines (marked as None)
        output_lines = [line for line in self.lines if line is not None]

        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(output_lines)


class MDQL:
    """Main MDQL interface for querying and manipulating markdown task lists."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.parser = MDQLParser()
        self.data = self.parser.parse_file(filepath)
        self.writer = MDQLWriter(self.data['lines'])

    @property
    def tasks(self) -> List[TaskItem]:
        """Get all tasks."""
        return self.data['tasks']

    @property
    def sections(self) -> Dict[str, SectionMetadata]:
        """Get all section metadata."""
        return self.data['sections']

    def query(self, **filters) -> List[TaskItem]:
        """
        Query tasks with filters.

        Supported filters:
        - completed: bool
        - section: str
        - priority: str (requires section metadata)
        - status: str (requires section metadata)
        - indent_level: int
        - text_contains: str
        - notes_contains: str - Search in task notes/descriptions
        - has_notes: bool - Filter tasks with/without notes
        """
        results = self.tasks

        if 'completed' in filters:
            results = [t for t in results if t.completed == filters['completed']]

        if 'section' in filters:
            section_filter = filters['section']
            results = [t for t in results if t.section == section_filter]

        if 'indent_level' in filters:
            results = [t for t in results if t.indent_level == filters['indent_level']]

        if 'text_contains' in filters:
            text = filters['text_contains'].lower()
            results = [t for t in results if text in t.text.lower()]

        if 'notes_contains' in filters:
            search_text = filters['notes_contains'].lower()
            results = [
                t for t in results
                if any(search_text in note.lower() for note in t.notes)
            ]

        if 'has_notes' in filters:
            has_notes = filters['has_notes']
            if has_notes:
                results = [t for t in results if t.notes]
            else:
                results = [t for t in results if not t.notes]

        if 'priority' in filters:
            priority = filters['priority']
            results = [
                t for t in results
                if t.section in self.sections and self.sections[t.section].priority == priority
            ]

        if 'status' in filters:
            status = filters['status']
            results = [
                t for t in results
                if t.section in self.sections and self.sections[t.section].status == status
            ]

        return results

    def mark_complete(self, line_number: int) -> None:
        """Mark a task as complete."""
        self.writer.update_task_completion(line_number, True)
        # Update in-memory task
        for task in self.tasks:
            if task.line_number == line_number:
                task.completed = True
                break

    def mark_incomplete(self, line_number: int) -> None:
        """Mark a task as incomplete."""
        self.writer.update_task_completion(line_number, False)
        # Update in-memory task
        for task in self.tasks:
            if task.line_number == line_number:
                task.completed = False
                break

    def update_text(self, line_number: int, new_text: str) -> None:
        """Update task text."""
        self.writer.update_task_text(line_number, new_text)
        # Update in-memory task
        for task in self.tasks:
            if task.line_number == line_number:
                task.text = new_text
                break

    def delete(self, line_number: int) -> None:
        """Delete a task."""
        self.writer.delete_task(line_number)
        # Remove from in-memory tasks
        self.data['tasks'] = [t for t in self.tasks if t.line_number != line_number]

    def add_task(self, section: str, text: str, indent_level: int = 0, completed: bool = False) -> None:
        """Add a new task to a section."""
        # Find the section and insert after it
        section_meta = self.sections.get(section)
        if not section_meta:
            raise ValueError(f"Section '{section}' not found")

        # Find the next section or end of current section
        insert_line = section_meta.line_number + 1
        for line_num in range(section_meta.line_number + 1, len(self.writer.lines) + 1):
            line = self.writer.lines[line_num - 1] if line_num <= len(self.writer.lines) else ""
            # Stop at next heading of same or higher level
            if re.match(r'^#{1,' + str(section_meta.section_level) + r'}\s+', line):
                break
            insert_line = line_num + 1

        self.writer.insert_task(insert_line, text, indent_level, completed)

    def save(self, filepath: Optional[str] = None) -> None:
        """Save changes to file."""
        output_path = filepath or self.filepath
        self.writer.write_file(output_path)

    def get_section_summary(self) -> List[Dict[str, Any]]:
        """Get summary statistics for each section."""
        summary = []

        for section_name, metadata in self.sections.items():
            section_tasks = [t for t in self.tasks if t.section == section_name and t.indent_level == 0]
            total = len(section_tasks)
            completed = sum(1 for t in section_tasks if t.completed)

            if total > 0:
                summary.append({
                    'section': section_name,
                    'priority': metadata.priority,
                    'status': metadata.status,
                    'total_tasks': total,
                    'completed': completed,
                    'remaining': total - completed,
                    'completion_pct': round(100 * completed / total, 1) if total > 0 else 0
                })

        return summary

    def print_summary(self) -> None:
        """Print a formatted summary."""
        print("\n" + "=" * 80)
        print("MDQL Task Summary")
        print("=" * 80)

        summary = self.get_section_summary()

        for item in summary:
            print(f"\n{item['section']}")
            if item['priority']:
                print(f"  Priority: {item['priority']}")
            if item['status']:
                print(f"  Status: {item['status']}")
            print(f"  Tasks: {item['completed']}/{item['total_tasks']} completed ({item['completion_pct']}%)")

        print("\n" + "=" * 80)
        print(f"Total Tasks: {len(self.tasks)}")
        print(f"Completed: {sum(1 for t in self.tasks if t.completed)}")
        print(f"Remaining: {sum(1 for t in self.tasks if not t.completed)}")
        print("=" * 80 + "\n")

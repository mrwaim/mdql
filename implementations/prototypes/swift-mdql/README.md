# MDQL Swift Prototype

A Swift implementation of MDQL (Markdown Query Language) for parsing and querying markdown task lists.

## Status

⚠️ **Work in Progress**: This prototype successfully compiles and demonstrates the core architecture, but currently has a runtime issue that requires further debugging before it can be used. The implementation serves as a foundation for a production-ready Swift MDQL library.

##  Features Implemented

- ✅ Parse markdown files with task lists (`- [ ]` and `- [x]`)
- ✅ Extract section metadata (Priority, Status, Source, Updated)
- ✅ Query tasks by various criteria
- ✅ Support for nested task lists
- ✅ Parse task notes/descriptions (non-checkbox bullet points)
- ✅ Generate progress summaries
- ✅ Type-safe Swift implementation
- ✅ Compiles successfully
- ⚠️ Runtime debugging needed

## Requirements

- Swift 5.9 or later
- macOS 13.0 or later

## Installation

No external dependencies required! Uses only Swift standard library.

```bash
# Clone the repository or navigate to this directory
cd implementations/prototypes/swift-mdql

# Build the project
swift build

# Run the demo
swift run mdql-demo
```

## Usage

### Basic Example

```swift
import MDQL

// Load a markdown file
let mdql = try MDQL(filepath: "path/to/todo.md")

// Query incomplete tasks
let incomplete = mdql.query(completed: false, indentLevel: 0)
for task in incomplete {
    print("☐ \(task.text)")
}

// Query by priority
let highPriority = mdql.query(priority: "High", completed: false)

// Query by section
let sectionTasks = mdql.query(section: "Open Mosque Project")

// Get section summary
let summary = mdql.getSectionSummary()
for item in summary {
    print("\(item.section): \(item.completed)/\(item.totalTasks) tasks")
}
```

### Running the Demo

```bash
# From the swift-mdql directory
swift run mdql-demo

# Or build first, then run
swift build
.build/debug/mdql-demo
```

The demo will:
1. Load the sample todo.md file
2. Display overall task summary
3. Run various queries (incomplete, high-priority, by section)
4. Show tasks with notes
5. Display section progress summary
6. Group tasks by priority

## API Reference

### MDQL Class

#### Initializer
```swift
let mdql = try MDQL(filepath: "path/to/file.md")
```

#### Properties
- `tasks: [TaskItem]` - Array of all task items
- `sections: [String: SectionMetadata]` - Dictionary of section metadata

#### Methods

**Query Tasks**
```swift
func query(
    completed: Bool? = nil,
    section: String? = nil,
    priority: String? = nil,
    status: String? = nil,
    indentLevel: Int? = nil,
    textContains: String? = nil,
    notesContains: String? = nil,
    hasNotes: Bool? = nil
) -> [TaskItem]
```

Supported filters:
- `completed: Bool` - Filter by completion status
- `section: String` - Filter by section name
- `priority: String` - Filter by priority (High, Medium, Low)
- `status: String` - Filter by status
- `indentLevel: Int` - Filter by nesting level (0 = top-level)
- `textContains: String` - Filter by text content
- `notesContains: String` - Search in task notes/descriptions
- `hasNotes: Bool` - Filter tasks with/without notes

**Generate Reports**
```swift
func getSectionSummary() -> [(
    section: String,
    priority: String?,
    status: String?,
    totalTasks: Int,
    completed: Int,
    remaining: Int,
    completionPct: Double
)]

func printSummary()
```

### TaskItem Struct

Represents a single task with the following properties:

- `text: String` - Task description
- `completed: Bool` - Completion status
- `section: String` - Parent section name
- `sectionLevel: Int` - Heading level (2 for ##, 3 for ###)
- `indentLevel: Int` - Nesting depth (0 = top-level)
- `lineNumber: Int` - Line number in file
- `parentLine: Int?` - Parent task line number
- `hasChildren: Bool` - Whether task has subtasks
- `children: [TaskItem]` - Array of child tasks
- `notes: [String]` - Descriptive bullet points under this task

### SectionMetadata Struct

Represents section metadata with properties:

- `sectionName: String`
- `sectionLevel: Int`
- `lineNumber: Int`
- `sourceFile: String?`
- `sourceDate: String?`
- `sourceTime: String?`
- `updatedFile: String?`
- `updatedDate: String?`
- `updatedTime: String?`
- `priority: String?`
- `status: String?`
- `properties: [String: String]`

## Examples

### Get All High Priority Incomplete Tasks

```swift
import MDQL

let mdql = try MDQL(filepath: "todo.md")

let highPriorityTasks = mdql.query(
    priority: "High",
    completed: false,
    indentLevel: 0
)

for task in highPriorityTasks {
    print("🔴 \(task.text)")
    print("   Section: \(task.section)")
}
```

### Section Progress Report

```swift
import MDQL

let mdql = try MDQL(filepath: "todo.md")
let summary = mdql.getSectionSummary()

for item in summary {
    print("\(item.section)")
    print("  Progress: \(item.completed)/\(item.totalTasks) (\(item.completionPct)%)")
    print("  Priority: \(item.priority ?? "N/A")")
    print("  Status: \(item.status ?? "N/A")")
}
```

### Find Actionable Tasks

```swift
import MDQL

let mdql = try MDQL(filepath: "todo.md")

// Get all incomplete top-level tasks
let incomplete = mdql.query(completed: false, indentLevel: 0)

// Filter to tasks with no incomplete children
let actionable = incomplete.filter { task in
    !task.hasChildren || task.children.allSatisfy { $0.completed }
}

print("Actionable tasks: \(actionable.count)")
for task in actionable {
    print("☐ \(task.text)")
}
```

### Query Tasks with Notes

```swift
import MDQL

let mdql = try MDQL(filepath: "todo.md")

// Find tasks that have notes/descriptions
let tasksWithNotes = mdql.query(hasNotes: true)
print("Found \(tasksWithNotes.count) tasks with notes")

// Search for specific content in notes
let exampleTasks = mdql.query(notesContains: "Example")
for task in exampleTasks {
    print("☐ \(task.text)")
    print("  Notes:")
    for note in task.notes {
        print("    - \(note)")
    }
}

// Get tasks with many notes (detailed tasks)
let detailedTasks = mdql.tasks.filter { $0.notes.count >= 3 }
for task in detailedTasks {
    print("☐ \(task.text) (\(task.notes.count) notes)")
}
```

## Limitations

This is a prototype implementation with some limitations:

1. **Read-Only** - No write/update operations (see Python prototype for write support)
2. **No Full SQL** - Uses method-based queries instead of SQL parser
3. **No Joins** - Can't join multiple files together
4. **No Indexes** - Queries scan all tasks (fine for small files)
5. **Basic Validation** - Limited error checking

## Comparison with Python Prototype

### Features Available in Both:
- ✅ Parse task lists with checkboxes
- ✅ Extract section metadata
- ✅ Query by completion, section, priority, indent level
- ✅ Support for nested tasks and notes
- ✅ Generate progress summaries

### Features in Python Only:
- ✅ Write operations (mark complete, update text, delete, add tasks)
- ✅ Save modified files back to disk
- ✅ In-memory modification with file writer

### Swift Advantages:
- ✅ Type safety at compile time
- ✅ Better performance for large files
- ✅ Memory efficient struct-based design
- ✅ Native macOS/iOS integration potential

## Future Enhancements

Potential improvements for a production implementation:

- Add write operations (mark complete, update, delete, add)
- Full SQL query parser
- Support for joins across multiple files
- Indexing for faster queries
- More sophisticated metadata extraction
- Watch mode for auto-reload on file changes
- iOS/iPadOS support
- SwiftUI views for task visualization
- Integration with git for version control

## Project Structure

```
swift-mdql/
├── Package.swift           # Swift Package Manager configuration
├── README.md              # This file
└── Sources/
    ├── MDQL/              # Main library
    │   ├── Models.swift   # Data structures (TaskItem, SectionMetadata)
    │   ├── Parser.swift   # Markdown parser
    │   └── MDQL.swift     # Main query interface
    └── MDQLDemo/          # Demo executable
        └── main.swift     # Demo program
```

## Building and Testing

### Build the Project

```bash
swift build
```

### Run the Demo

```bash
swift run mdql-demo
```

### Build for Release

```bash
swift build -c release
```

The release binary will be at `.build/release/mdql-demo`

## Contributing

This is a prototype for demonstration purposes. For production use, consider:

- Adding comprehensive test suite
- Implementing write operations
- Adding support for more markdown formats
- Performance optimizations for large files
- Better error handling and validation

## License

Part of the MDQL project. See main repository for license information.

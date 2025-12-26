import Foundation
import MDQL

func printSection(_ title: String) {
    print("\n" + String(repeating: "=", count: 80))
    print("  \(title)")
    print(String(repeating: "=", count: 80) + "\n")
}

func printTasks(_ tasks: [TaskItem], title: String) {
    print("\n\(title) (\(tasks.count) tasks):")
    print(String(repeating: "-", count: 80))
    for task in tasks {
        let status = task.completed ? "✓" : "☐"
        let indent = String(repeating: "  ", count: task.indentLevel)
        print("\(indent)\(status) \(task.text)")
        print("   └─ Section: \(task.section) | Line: \(task.lineNumber)")
    }
}

func main() -> Int32 {
    // Get the path to the todo.md file
    let currentPath = FileManager.default.currentDirectoryPath
    let todoPath = "\(currentPath)/../../../samples/notes-app/todo.md"

    // Resolve the path
    let resolvedPath: String
    if let url = URL(string: todoPath) {
        resolvedPath = url.path
    } else {
        resolvedPath = todoPath
    }

    printSection("MDQL Swift Prototype Demo")
    print("Loading: \(resolvedPath)")

    // Check if file exists
    if !FileManager.default.fileExists(atPath: resolvedPath) {
        print("Error: Could not find todo.md at \(resolvedPath)")
        print("\nTrying relative path from current directory...")

        // Try a few different paths
        let possiblePaths = [
            "../../../samples/notes-app/todo.md",
            "../../samples/notes-app/todo.md",
            "samples/notes-app/todo.md"
        ]

        var foundPath: String?
        for path in possiblePaths {
            let fullPath = "\(currentPath)/\(path)"
            if FileManager.default.fileExists(atPath: fullPath) {
                foundPath = fullPath
                break
            }
        }

        if let found = foundPath {
            print("Found at: \(found)")
            return runDemo(at: found)
        } else {
            print("Could not find todo.md in any expected location")
            print("Current directory: \(currentPath)")
            return 1
        }
    }

    return runDemo(at: resolvedPath)
}

func runDemo(at todoPath: String) -> Int32 {
    do {
        // Load the file
        let mdql = try MDQL(filepath: todoPath)

        // Print summary
        printSection("1. Overall Summary")
        mdql.printSummary()

        // Query incomplete tasks
        printSection("2. Query: Incomplete Tasks")
        let incomplete = mdql.query(completed: false, indentLevel: 0)
        print("Found \(incomplete.count) incomplete top-level tasks")
        printTasks(Array(incomplete.prefix(5)), title: "First 5 incomplete tasks")

        // Query high-priority tasks
        printSection("3. Query: High Priority Tasks")
        let highPriority = mdql.query(completed: false, priority: "High", indentLevel: 0)
        printTasks(highPriority, title: "High priority incomplete tasks")

        // Query tasks in specific section
        printSection("4. Query: Tasks by Section")
        let sectionNames = Array(mdql.sections.keys).sorted()
        if let firstSection = sectionNames.first, !firstSection.isEmpty {
            let sectionTasks = mdql.query(section: firstSection)
            printTasks(Array(sectionTasks.prefix(5)), title: "First 5 tasks in '\(firstSection)'")
        }

        // Query completed tasks
        printSection("5. Query: Completed Tasks")
        let completed = mdql.query(completed: true)
        printTasks(Array(completed.prefix(10)), title: "First 10 completed tasks")

        // Query tasks with notes
        printSection("6. Query: Tasks with Notes")
        let tasksWithNotes = mdql.query(hasNotes: true)
        print("Found \(tasksWithNotes.count) tasks with notes")
        for task in Array(tasksWithNotes.prefix(3)) {
            print("\n☐ \(task.text)")
            print("  Notes:")
            for note in task.notes {
                print("    - \(note)")
            }
        }

        // Show section summary
        printSection("7. Section Progress Summary")
        let summary = mdql.getSectionSummary()

        let widths = [40, 10, 20, 10]

        print("\("Section".padding(toLength: widths[0], withPad: " ", startingAt: 0))\("Priority".padding(toLength: widths[1], withPad: " ", startingAt: 0))\("Progress".padding(toLength: widths[2], withPad: " ", startingAt: 0))%")
        print(String(repeating: "-", count: 80))

        for item in Array(summary.prefix(10)) {
            let section = String(item.section.prefix(38)).padding(toLength: widths[0], withPad: " ", startingAt: 0)
            let priority = (item.priority ?? "N/A").padding(toLength: widths[1], withPad: " ", startingAt: 0)
            let progress = "\(item.completed)/\(item.totalTasks)".padding(toLength: widths[2], withPad: " ", startingAt: 0)
            let pct = String(format: "%.1f%%", item.completionPct)

            print("\(section)\(priority)\(progress)\(pct)")
        }

        // Statistics by priority
        printSection("8. Tasks by Priority")
        let priorities = ["High", "Medium", "Low"]
        for priority in priorities {
            let tasks = mdql.query(completed: false, priority: priority, indentLevel: 0)
            if !tasks.isEmpty {
                print("\n\(priority) Priority: \(tasks.count) tasks")
                for task in Array(tasks.prefix(3)) {
                    print("  ☐ \(task.text)")
                }
            }
        }

        printSection("Demo Complete!")
        print("Successfully parsed and queried todo.md")
        print("Total tasks: \(mdql.tasks.count)")
        print("Total sections: \(mdql.sections.count)")

        return 0

    } catch {
        print("Error: \(error)")
        return 1
    }
}

exit(main())

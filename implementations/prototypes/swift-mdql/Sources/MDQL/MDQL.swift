import Foundation

/// Main MDQL interface for querying markdown task lists
public class MDQL {
    public let filepath: String
    private let parser: MDQLParser
    private var data: (tasks: [TaskItem], sections: [String: SectionMetadata], lines: [String])

    public init(filepath: String) throws {
        self.filepath = filepath
        self.parser = MDQLParser()
        self.data = try parser.parseFile(at: filepath)
    }

    /// Get all tasks
    public var tasks: [TaskItem] {
        return data.tasks
    }

    /// Get all section metadata
    public var sections: [String: SectionMetadata] {
        return data.sections
    }

    /// Query tasks with filters
    ///
    /// Supported filters:
    /// - completed: Bool - Filter by completion status
    /// - section: String - Filter by section name
    /// - priority: String - Filter by priority (requires section metadata)
    /// - status: String - Filter by status (requires section metadata)
    /// - indentLevel: Int - Filter by nesting level (0 = top-level)
    /// - textContains: String - Filter by text content
    /// - notesContains: String - Search in task notes/descriptions
    /// - hasNotes: Bool - Filter tasks with/without notes
    public func query(
        completed: Bool? = nil,
        section: String? = nil,
        priority: String? = nil,
        status: String? = nil,
        indentLevel: Int? = nil,
        textContains: String? = nil,
        notesContains: String? = nil,
        hasNotes: Bool? = nil
    ) -> [TaskItem] {
        var results = tasks

        if let completed = completed {
            results = results.filter { $0.completed == completed }
        }

        if let section = section {
            results = results.filter { $0.section == section }
        }

        if let indentLevel = indentLevel {
            results = results.filter { $0.indentLevel == indentLevel }
        }

        if let textContains = textContains {
            let lowercased = textContains.lowercased()
            results = results.filter { $0.text.lowercased().contains(lowercased) }
        }

        if let notesContains = notesContains {
            let lowercased = notesContains.lowercased()
            results = results.filter { task in
                task.notes.contains { $0.lowercased().contains(lowercased) }
            }
        }

        if let hasNotes = hasNotes {
            if hasNotes {
                results = results.filter { !$0.notes.isEmpty }
            } else {
                results = results.filter { $0.notes.isEmpty }
            }
        }

        if let priority = priority {
            results = results.filter { task in
                guard let metadata = sections[task.section] else { return false }
                return metadata.priority == priority
            }
        }

        if let status = status {
            results = results.filter { task in
                guard let metadata = sections[task.section] else { return false }
                return metadata.status == status
            }
        }

        return results
    }

    /// Generate section summary statistics
    public func getSectionSummary() -> [(
        section: String,
        priority: String?,
        status: String?,
        totalTasks: Int,
        completed: Int,
        remaining: Int,
        completionPct: Double
    )] {
        var summary: [(String, String?, String?, Int, Int, Int, Double)] = []

        for (sectionName, metadata) in sections {
            let sectionTasks = tasks.filter { $0.section == sectionName && $0.indentLevel == 0 }
            let total = sectionTasks.count
            let completed = sectionTasks.filter { $0.completed }.count

            if total > 0 {
                let completionPct = Double(completed) / Double(total) * 100.0
                summary.append((
                    sectionName,
                    metadata.priority,
                    metadata.status,
                    total,
                    completed,
                    total - completed,
                    completionPct
                ))
            }
        }

        return summary
    }

    /// Print a formatted summary
    public func printSummary() {
        print("\n" + String(repeating: "=", count: 80))
        print("MDQL Task Summary")
        print(String(repeating: "=", count: 80))

        let summary = getSectionSummary()

        for item in summary {
            print("\n\(item.section)")
            if let priority = item.priority {
                print("  Priority: \(priority)")
            }
            if let status = item.status {
                print("  Status: \(status)")
            }
            print("  Tasks: \(item.completed)/\(item.totalTasks) completed (\(String(format: "%.1f", item.completionPct))%)")
        }

        let totalTasks = tasks.count
        let totalCompleted = tasks.filter { $0.completed }.count
        let totalRemaining = totalTasks - totalCompleted

        print("\n" + String(repeating: "=", count: 80))
        print("Total Tasks: \(totalTasks)")
        print("Completed: \(totalCompleted)")
        print("Remaining: \(totalRemaining)")
        print(String(repeating: "=", count: 80) + "\n")
    }
}

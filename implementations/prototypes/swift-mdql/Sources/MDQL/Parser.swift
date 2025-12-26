import Foundation

/// Parser for markdown files with task lists
public class MDQLParser {
    // Regular expression patterns
    private let headingPattern = try! NSRegularExpression(pattern: #"^(#{1,6})\s+(.+)$"#)
    private let taskPattern = try! NSRegularExpression(pattern: #"^(\s*)- \[([ xX])\]\s+(.+)$"#)
    private let notePattern = try! NSRegularExpression(pattern: #"^(\s*)- (.+)$"#)
    private let sourcePattern = try! NSRegularExpression(pattern: #"^\*Source:\s*(.+?\.md)\s*\((.+?)\)\*$"#)
    private let updatedPattern = try! NSRegularExpression(pattern: #"^\*Updated:\s*(.+?\.md)\s*\((.+?)\)\*$"#)
    private let propertyPattern = try! NSRegularExpression(pattern: #"^\*\*(.+?):\*\*\s+(.+)$"#)

    public var tasks: [TaskItem] = []
    public var sections: [String: SectionMetadata] = [:]
    private var currentSection: String?
    private var currentSectionLevel: Int = 0
    private var lines: [String] = []

    public init() {}

    /// Parse a markdown file and extract task lists and metadata
    public func parseFile(at filepath: String) throws -> (tasks: [TaskItem], sections: [String: SectionMetadata], lines: [String]) {
        let content = try String(contentsOfFile: filepath, encoding: .utf8)
        lines = content.components(separatedBy: .newlines)

        parseContent()

        return (tasks, sections, lines)
    }

    private func parseContent() {
        var parentStack: [(indentLevel: Int, lineNumber: Int)] = []
        var currentSectionMeta: SectionMetadata?
        var lastTaskLine: Int?
        var childrenCountMap: [Int: Int] = [:]
        var notesMap: [Int: [String]] = [:]

        for (index, line) in lines.enumerated() {
            let lineNumber = index + 1
            let lineStripped = line.trimmingCharacters(in: .newlines)

            // Check for heading
            if let headingMatch = match(pattern: headingPattern, in: lineStripped) {
                let level = headingMatch[0]?.count ?? 0
                let sectionName = headingMatch[1] ?? ""
                currentSection = sectionName
                currentSectionLevel = level

                currentSectionMeta = SectionMetadata(
                    sectionName: sectionName,
                    sectionLevel: level,
                    lineNumber: lineNumber
                )
                sections[sectionName] = currentSectionMeta
                parentStack.removeAll()
                lastTaskLine = nil
                continue
            }

            // Check for source metadata
            if currentSectionMeta != nil {
                if let sourceMatch = match(pattern: sourcePattern, in: lineStripped) {
                    let fileName = sourceMatch[0] ?? ""
                    let dateTime = sourceMatch[1] ?? ""
                    parseDatetime(dateTime, into: &currentSectionMeta!, prefix: "source")
                    currentSectionMeta?.sourceFile = fileName
                    sections[currentSectionMeta!.sectionName] = currentSectionMeta
                    continue
                }

                // Check for updated metadata
                if let updatedMatch = match(pattern: updatedPattern, in: lineStripped) {
                    let fileName = updatedMatch[0] ?? ""
                    let dateTime = updatedMatch[1] ?? ""
                    parseDatetime(dateTime, into: &currentSectionMeta!, prefix: "updated")
                    currentSectionMeta?.updatedFile = fileName
                    sections[currentSectionMeta!.sectionName] = currentSectionMeta
                    continue
                }

                // Check for property metadata
                if let propMatch = match(pattern: propertyPattern, in: lineStripped) {
                    let key = propMatch[0] ?? ""
                    let value = propMatch[1] ?? ""

                    // Special handling for known properties
                    if key == "Priority" {
                        currentSectionMeta?.priority = value
                    } else if key == "Status" {
                        currentSectionMeta?.status = value
                    } else {
                        currentSectionMeta?.properties[key] = value
                    }
                    sections[currentSectionMeta!.sectionName] = currentSectionMeta
                    continue
                }
            }

            // Check for task item (checkbox)
            if let taskMatch = match(pattern: taskPattern, in: lineStripped) {
                let indent = taskMatch[0] ?? ""
                let check = taskMatch[1] ?? " "
                let text = taskMatch[2] ?? ""

                let indentLevel = indent.count / 2
                let completed = check.lowercased() == "x"

                var task = TaskItem(
                    text: text,
                    completed: completed,
                    section: currentSection ?? "Untitled",
                    sectionLevel: currentSectionLevel,
                    indentLevel: indentLevel,
                    lineNumber: lineNumber
                )

                // Determine parent
                while !parentStack.isEmpty && parentStack.last!.indentLevel >= indentLevel {
                    parentStack.removeLast()
                }

                if let parent = parentStack.last {
                    task.parentLine = parent.lineNumber
                    // Track that parent has children
                    childrenCountMap[parent.lineNumber, default: 0] += 1
                }

                parentStack.append((indentLevel, lineNumber))
                tasks.append(task)
                lastTaskLine = lineNumber
                continue
            }

            // Check for note items (regular bullets without checkbox)
            if let noteMatch = match(pattern: notePattern, in: lineStripped),
               let lastLine = lastTaskLine {
                let indent = noteMatch[0] ?? ""
                let noteText = noteMatch[1] ?? ""
                let noteIndentLevel = indent.count / 2

                // Find the last task to check indent level
                if let lastTaskIndex = tasks.lastIndex(where: { $0.lineNumber == lastLine }) {
                    let lastTask = tasks[lastTaskIndex]

                    // Only add as note if it's indented more than the last task
                    if noteIndentLevel > lastTask.indentLevel {
                        notesMap[lastLine, default: []].append(noteText)
                        continue
                    }
                }
            }
        }

        // Second pass: update tasks with hasChildren and notes
        for index in tasks.indices {
            let lineNumber = tasks[index].lineNumber
            if childrenCountMap[lineNumber] != nil {
                tasks[index].hasChildren = true
            }
            if let notes = notesMap[lineNumber] {
                tasks[index].notes = notes
            }
        }
    }

    private func match(pattern: NSRegularExpression, in string: String) -> [Int: String]? {
        let range = NSRange(string.startIndex..., in: string)
        guard let match = pattern.firstMatch(in: string, range: range) else {
            return nil
        }

        var result: [Int: String] = [:]
        // Start from 1 to skip the full match (index 0)
        for i in 1..<match.numberOfRanges {
            if let range = Range(match.range(at: i), in: string) {
                // Store captured groups starting at index 0
                result[i - 1] = String(string[range])
            }
        }
        return result.isEmpty ? nil : result
    }

    private func parseDatetime(_ dateTimeStr: String, into metadata: inout SectionMetadata, prefix: String) {
        let parts = dateTimeStr.components(separatedBy: " ")
        if !parts.isEmpty {
            if prefix == "source" {
                metadata.sourceDate = parts[0]
                if parts.count > 1 {
                    metadata.sourceTime = parts[1]
                }
            } else if prefix == "updated" {
                metadata.updatedDate = parts[0]
                if parts.count > 1 {
                    metadata.updatedTime = parts[1]
                }
            }
        }
    }
}

import Foundation

/// Metadata extracted from section headers
public struct SectionMetadata {
    public let sectionName: String
    public let sectionLevel: Int
    public let lineNumber: Int
    public var sourceFile: String?
    public var sourceDate: String?
    public var sourceTime: String?
    public var updatedFile: String?
    public var updatedDate: String?
    public var updatedTime: String?
    public var priority: String?
    public var status: String?
    public var properties: [String: String]

    public init(
        sectionName: String,
        sectionLevel: Int,
        lineNumber: Int,
        sourceFile: String? = nil,
        sourceDate: String? = nil,
        sourceTime: String? = nil,
        updatedFile: String? = nil,
        updatedDate: String? = nil,
        updatedTime: String? = nil,
        priority: String? = nil,
        status: String? = nil,
        properties: [String: String] = [:]
    ) {
        self.sectionName = sectionName
        self.sectionLevel = sectionLevel
        self.lineNumber = lineNumber
        self.sourceFile = sourceFile
        self.sourceDate = sourceDate
        self.sourceTime = sourceTime
        self.updatedFile = updatedFile
        self.updatedDate = updatedDate
        self.updatedTime = updatedTime
        self.priority = priority
        self.status = status
        self.properties = properties
    }
}

/// Represents a single task list item
public struct TaskItem {
    public let text: String
    public var completed: Bool
    public let section: String
    public let sectionLevel: Int
    public let indentLevel: Int
    public let lineNumber: Int
    public var parentLine: Int?
    public var hasChildren: Bool
    public var notes: [String]

    public init(
        text: String,
        completed: Bool,
        section: String,
        sectionLevel: Int,
        indentLevel: Int,
        lineNumber: Int,
        parentLine: Int? = nil,
        hasChildren: Bool = false,
        notes: [String] = []
    ) {
        self.text = text
        self.completed = completed
        self.section = section
        self.sectionLevel = sectionLevel
        self.indentLevel = indentLevel
        self.lineNumber = lineNumber
        self.parentLine = parentLine
        self.hasChildren = hasChildren
        self.notes = notes
    }

    public var description: String {
        let status = completed ? "✓" : "☐"
        let indent = String(repeating: "  ", count: indentLevel)
        let notesInfo = notes.isEmpty ? "" : " [\(notes.count) notes]"
        return "\(indent)\(status) \(text)\(notesInfo) (line \(lineNumber))"
    }
}

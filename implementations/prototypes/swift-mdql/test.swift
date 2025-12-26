import Foundation

// Get path to todo.md
let todoPath = "/Users/klsandbox/Claude/mdql/samples/notes-app/todo.md"

print("Reading file: \(todoPath)")

do {
    let content = try String(contentsOfFile: todoPath, encoding: .utf8)
    let lines = content.components(separatedBy: .newlines)
    print("Total lines: \(lines.count)")

    // Print first 10 lines
    for (index, line) in lines.prefix(10).enumerated() {
        print("\(index + 1): \(line)")
    }

    // Test regex
    let headingPattern = try NSRegularExpression(pattern: #"^(#{1,6})\s+(.+)$"#)

    for (index, line) in lines.enumerated() {
        let range = NSRange(line.startIndex..., in: line)
        if let match = headingPattern.firstMatch(in: line, range: range) {
            print("\nFound heading at line \(index + 1):")
            print("  Full line: \(line)")
            print("  Number of ranges: \(match.numberOfRanges)")

            for i in 0..<match.numberOfRanges {
                if let range = Range(match.range(at: i), in: line) {
                    print("  Range \(i): '\(String(line[range]))'")
                }
            }
        }
    }

} catch {
    print("Error: \(error)")
}

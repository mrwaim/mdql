#!/usr/bin/env swift
import Foundation

// Minimal test to isolate the crash
// This loads a simple markdown file and tries to parse it

// Add the path to your minimal test file
let testFile = "/Users/klsandbox/Claude/mdql/implementations/prototypes/swift-mdql/minimal-test.md"

print("=== Minimal MDQL Test ===")
print("Reading: \(testFile)\n")

// Test 1: Can we read the file?
do {
    let content = try String(contentsOfFile: testFile, encoding: .utf8)
    print("✓ File read successfully")
    print("  Length: \(content.count) bytes")
    print("  Lines: \(content.components(separatedBy: .newlines).count)")
} catch {
    print("✗ Failed to read file: \(error)")
    exit(1)
}

print("\n=== Regex Tests ===\n")

// Test 2: Do the regex patterns work?
let patterns = [
    ("heading", #"^(#{1,6})\s+(.+)$"#),
    ("task", #"^(\s*)- \[([ xX])\]\s+(.+)$"#),
    ("property", #"^\*\*(.+?):\*\*\s+(.+)$"#)
]

for (name, patternStr) in patterns {
    do {
        let pattern = try NSRegularExpression(pattern: patternStr)
        print("✓ \(name) pattern compiled")

        // Test against sample lines
        let samples: [String]
        switch name {
        case "heading":
            samples = ["## Section One", "# Test"]
        case "task":
            samples = ["- [ ] Task 1", "- [x] Task 2"]
        case "property":
            samples = ["**Priority:** High"]
        default:
            samples = []
        }

        for sample in samples {
            let range = NSRange(sample.startIndex..., in: sample)
            if let match = pattern.firstMatch(in: sample, range: range) {
                print("  ✓ Matched: '\(sample)'")
                for i in 1..<match.numberOfRanges {
                    if let r = Range(match.range(at: i), in: sample) {
                        print("    Capture \(i-1): '\(String(sample[r]))'")
                    }
                }
            }
        }
    } catch {
        print("✗ \(name) pattern failed: \(error)")
    }
}

print("\n=== Attempting to load MDQL library ===")
print("Note: This will fail if you haven't built the library")
print("Run: swift build")
print("\nTo test with the library, use the actual demo program.")

// If you want to test with the actual library, you need to:
// 1. Build it: swift build
// 2. Import it properly (requires package context)
// 3. Or create an executable target that depends on MDQL

print("\n=== Test Complete ===")
print("If all regex tests passed, the issue is likely in:")
print("1. How the Parser class uses the match() function")
print("2. Dictionary/struct mutations during parsing")
print("3. The demo program's string formatting")
print("\nSee RUNTIME_ISSUE.md for detailed debugging steps.")

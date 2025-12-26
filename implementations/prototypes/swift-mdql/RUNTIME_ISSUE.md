# Swift MDQL Runtime Issue - Debug Notes

## Problem Summary

The Swift MDQL prototype compiles successfully but crashes with a segmentation fault (exit code 139) when running the demo program.

## Environment

- **Platform:** macOS (Darwin 23.5.0)
- **Swift Version:** 5.9+
- **Build Command:** `swift build` (successful)
- **Run Command:** `.build/debug/mdql-demo` (crashes)

## Symptoms

1. **Segmentation Fault:** Process terminates with signal 11 (SIGSEGV)
2. **Exit Code:** 139
3. **Partial Output:** The program does produce some output before crashing, indicating the parser runs but produces incorrect results

## Observed Behavior from Debug Output

When run with `lldb`, the program:

1. ✅ Successfully loads the file
2. ✅ Parses some tasks (reports 58 total tasks, 5 completed)
3. ⚠️ **Section names are EMPTY** - all tasks have `section: ""` instead of actual section names
4. ⚠️ Crashes during or after section 3/4 of the demo output

Example output before crash:
```
Found 53 incomplete top-level tasks

First 5 incomplete tasks (5 tasks):
--------------------------------------------------------------------------------
☐ Design notification system architecture
   └─ Section:  | Line: 6          <-- SECTION IS EMPTY!
☐ Implement job time estimates feature
   └─ Section:  | Line: 10         <-- SECTION IS EMPTY!
```

## Root Cause Hypothesis

### Primary Issue: Regex Capture Group Indexing

The crash appears related to how regex capture groups are being accessed. There was confusion about indexing:

**NSRegularExpression returns:**
- `match.range(at: 0)` = Full match
- `match.range(at: 1)` = First capture group
- `match.range(at: 2)` = Second capture group

**My `match()` helper function returns:**
- `result[0]` = First capture group (skipping full match)
- `result[1]` = Second capture group

**The Problem:**
- Initially, code accessed `headingMatch[1]` and `headingMatch[2]`
- Should access `headingMatch[0]` and `headingMatch[1]`
- Was partially fixed but section names still come out empty

### Test Results

Created `test.swift` to verify regex behavior:
```swift
let headingPattern = try NSRegularExpression(pattern: #"^(#{1,6})\s+(.+)$"#)
```

**Output from test:**
```
Found heading at line 1:
  Full line: # Todos
  Number of ranges: 3
  Range 0: '# Todos'      <-- Full match
  Range 1: '#'            <-- First capture group (the hashes)
  Range 2: 'Todos'        <-- Second capture group (the text)
```

This proves the regex works correctly, so the issue is in how the match results are being used.

## Code Locations to Investigate

### 1. Parser.swift - `match()` function (line ~170)

```swift
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
```

**Issue:** This function should correctly extract capture groups, but verify the dictionary is populated correctly.

### 2. Parser.swift - Heading parsing (line ~43)

```swift
if let headingMatch = match(pattern: headingPattern, in: lineStripped) {
    let level = headingMatch[0]?.count ?? 0        // First capture group = "#"
    let sectionName = headingMatch[1] ?? ""        // Second capture group = "Todos"
    currentSection = sectionName
    currentSectionLevel = level
```

**Issue:** If `headingMatch[0]` or `headingMatch[1]` are nil or empty, sections won't be set correctly.

### 3. Parser.swift - Struct mutation (line ~154-163)

```swift
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
```

**Potential Issue:** Swift structs are value types. Mutating array elements might be problematic if done incorrectly, though this code looks correct.

### 4. MDQL.swift - Dictionary iteration (line ~sections)

The demo tries to get the first section:
```swift
let sectionNames = Array(mdql.sections.keys).sorted()
if let firstSection = sectionNames.first, !firstSection.isEmpty {
```

**Potential Issue:** If sections dictionary has empty string keys, this could cause issues.

## Changes Made During Debugging

### Iteration 1: Fixed argument order in demo
- Swift requires named arguments in order
- Fixed `query(priority:completed:)` to `query(completed:priority:)`

### Iteration 2: Fixed regex indexing
- Changed all `match[1], match[2]` to `match[0], match[1]`
- Should have fixed section name extraction

### Iteration 3: Removed children array from TaskItem
- Original had `children: [TaskItem]` which created nested struct copies
- Removed to prevent potential issues with value type mutation
- Kept `hasChildren: Bool` flag and parent tracking via `parentLine`

## Debugging Steps Attempted

1. ✅ Built with `swift build` - successful
2. ✅ Ran with `lldb` - showed partial output then crash
3. ✅ Created standalone `test.swift` - regex works correctly
4. ❌ Tried to run `test2.swift` with library - linking issues
5. ❌ Direct execution - immediate segfault

## Files to Review

1. **`Sources/MDQL/Parser.swift`** - Core parsing logic, especially:
   - `match()` function
   - `parseContent()` function
   - Regex pattern usage

2. **`Sources/MDQL/Models.swift`** - Data structures:
   - Verify `TaskItem` and `SectionMetadata` are properly structured
   - Check for any computed properties that might crash

3. **`Sources/MDQLDemo/main.swift`** - Demo program:
   - Line where crash occurs (around section 4-5)
   - String formatting in `printTasks()` function

## Suggested Debugging Approach

### Step 1: Add Debug Logging

Add print statements to trace execution:
```swift
// In parseContent()
print("DEBUG: Parsing line \(lineNumber): \(lineStripped)")

// In match()
print("DEBUG: Match result for pattern: \(result)")

// After heading match
print("DEBUG: Found section: '\(sectionName)' at level \(level)")
```

### Step 2: Verify Section Extraction

Create minimal test:
```swift
let parser = MDQLParser()
let result = try parser.parseFile(at: "/path/to/todo.md")
print("Sections found: \(result.sections.count)")
for (name, meta) in result.sections {
    print("  - '\(name)' (level \(meta.sectionLevel))")
}
```

### Step 3: Check for Force Unwraps

Search for `!` in the code - these can cause crashes if nil:
```bash
grep -n "!" Sources/MDQL/*.swift
```

Pay special attention to:
- `currentSectionMeta!` (used multiple times)
- Dictionary force unwraps

### Step 4: Run with Memory Sanitizer

```bash
swift build -Xswiftc -sanitize=address
.build/debug/mdql-demo
```

This will show exactly where the memory issue occurs.

### Step 5: Simplify Demo

Create minimal demo that only:
1. Loads file
2. Prints sections
3. Prints first 5 tasks

If this works, gradually add complexity to find the crash point.

## Working Python Prototype Reference

The Python prototype (`implementations/prototypes/python-mdql/`) works correctly and can be used as a reference for the expected behavior:

```bash
cd implementations/prototypes/python-mdql
python3 demo.py  # Runs successfully
```

## Expected Behavior

When working correctly, the demo should:
1. Load `samples/notes-app/todo.md`
2. Parse ~58 tasks across ~13 sections
3. Display section names like:
   - "Todos" (level 1)
   - "Task Notification System" (level 2)
   - "LLM-Based Dinner Suggestion System" (level 2)
   - etc.
4. Show tasks with their proper sections
5. Generate progress summaries per section

## Quick Test Script

Created `simple-test.sh` to test with timeout:
```bash
./implementations/prototypes/swift-mdql/simple-test.sh
```

This runs the demo and kills it after 2 seconds if it hangs.

## Next Steps for Debugging

1. Add comprehensive debug logging to `Parser.swift`
2. Verify the `match()` function returns correct values
3. Check why section names are empty
4. Run with address sanitizer to find exact crash location
5. Create minimal test case that reproduces the issue
6. Consider using classes instead of structs for mutable state

## Solution (FIXED 2025-12-26)

### Root Cause

The crash was caused by using `String(format:)` with `%s` format specifiers and Swift String values in `main.swift` lines 123-134.

In Swift, `%s` expects a C string (`char*`), not a Swift `String`. Passing Swift strings to `%s` is undefined behavior and caused the segmentation fault when `_platform_strlen` tried to read invalid memory.

### The Fix

Replaced `String(format: "%-\(width)s", swiftString)` with Swift's native string padding:
```swift
// BEFORE (crashes):
print(String(format: "%-\(widths[0])s %-\(widths[1])s", section, priority))

// AFTER (works):
let section = String(item.section.prefix(38)).padding(toLength: widths[0], withPad: " ", startingAt: 0)
print("\(section)\(priority)")
```

### Files Changed

- `Sources/MDQLDemo/main.swift`: Replaced all `String(format: "%s")` calls with `String.padding(toLength:withPad:startingAt:)`

### Verification

After the fix, the demo runs successfully to completion:
```
$ .build/debug/mdql-demo
...
Demo Complete!
Successfully parsed and queried todo.md
Total tasks: 58
Total sections: 24
```

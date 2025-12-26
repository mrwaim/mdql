#!/bin/bash
# Helper script for debugging the Swift MDQL runtime issue

echo "=== MDQL Swift Debug Build Script ==="
echo ""

# Clean build
echo "1. Cleaning previous build..."
swift package clean
echo "   ✓ Clean complete"
echo ""

# Build with debug info
echo "2. Building with debug symbols..."
swift build -c debug
if [ $? -ne 0 ]; then
    echo "   ✗ Build failed!"
    exit 1
fi
echo "   ✓ Build successful"
echo ""

# Try with address sanitizer
echo "3. Building with AddressSanitizer (optional, may fail)..."
swift build -Xswiftc -sanitize=address 2>&1 | grep -v "warning:" | head -20
echo ""

# Test regex independently
echo "4. Testing regex patterns..."
cat > /tmp/test_regex.swift << 'EOF'
import Foundation

let headingPattern = try! NSRegularExpression(pattern: #"^(#{1,6})\s+(.+)$"#)
let testLine = "## Task Notification System"
let range = NSRange(testLine.startIndex..., in: testLine)

if let match = headingPattern.firstMatch(in: testLine, range: range) {
    print("✓ Regex works!")
    print("  Ranges: \(match.numberOfRanges)")
    for i in 0..<match.numberOfRanges {
        if let r = Range(match.range(at: i), in: testLine) {
            print("  [\(i)]: '\(String(testLine[r]))'")
        }
    }
} else {
    print("✗ Regex failed!")
}
EOF

swift /tmp/test_regex.swift
echo ""

# Info about the binary
echo "5. Binary information:"
echo "   Location: .build/debug/mdql-demo"
echo "   Size: $(ls -lh .build/debug/mdql-demo | awk '{print $5}')"
echo "   Type: $(file .build/debug/mdql-demo | cut -d: -f2)"
echo ""

# Suggest next steps
echo "=== Next Steps ==="
echo ""
echo "Run with lldb for detailed crash info:"
echo "  lldb .build/debug/mdql-demo"
echo "  (lldb) run"
echo "  (lldb) bt"
echo ""
echo "Run with environment variables for debugging:"
echo "  DYLD_PRINT_LIBRARIES=1 .build/debug/mdql-demo"
echo ""
echo "Check the RUNTIME_ISSUE.md file for detailed debugging guide"
echo ""

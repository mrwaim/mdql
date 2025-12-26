import Foundation

// Import our actual library
import MDQL

let todoPath = "/Users/klsandbox/Claude/mdql/samples/notes-app/todo.md"

print("Loading MDQL...")

do {
    let mdql = try MDQL(filepath: todoPath)
    print("✓ Loaded successfully!")
    print("Total tasks: \(mdql.tasks.count)")
    print("Total sections: \(mdql.sections.count)")

    print("\nSections:")
    for (name, meta) in mdql.sections {
        print("  - \(name) (level \(meta.sectionLevel))")
    }

    print("\nFirst 5 tasks:")
    for task in mdql.tasks.prefix(5) {
        print("  \(task.description)")
    }

} catch {
    print("Error: \(error)")
}

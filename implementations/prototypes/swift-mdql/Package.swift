// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MDQL",
    platforms: [
        .macOS(.v13)
    ],
    products: [
        .library(
            name: "MDQL",
            targets: ["MDQL"]),
        .executable(
            name: "mdql-demo",
            targets: ["MDQLDemo"])
    ],
    targets: [
        .target(
            name: "MDQL",
            dependencies: []),
        .executableTarget(
            name: "MDQLDemo",
            dependencies: ["MDQL"],
            path: "Sources/MDQLDemo")
    ]
)

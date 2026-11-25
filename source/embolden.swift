import CoreGraphics
import Foundation

// Offset the filled outline instead of the design skeleton. This keeps
// the hand-drawn joins and counters intact when adding a small web weight.
let width = Double(CommandLine.arguments[1])!
let input = try JSONSerialization.jsonObject(with: FileHandle.standardInput.readDataToEndOfFile()) as! [String: [[Double]]]
var result = [String: [[Double]]]()
for (name, commands) in input {
    let source = CGMutablePath()
    for row in commands {
        func point(_ i: Int) -> CGPoint { CGPoint(x: row[i], y: row[i+1]) }
        switch Int(row[0]) {
        case 0: source.move(to: point(1))
        case 1: source.addLine(to: point(1))
        case 2: source.addQuadCurve(to: point(3), control: point(1))
        case 3: source.addCurve(to: point(5), control1: point(1), control2: point(3))
        default: source.closeSubpath()
        }
    }
    if source.isEmpty {
        result[name] = []
        continue
    }
    let filled = source.normalized(using: .winding)
    let rim = filled.copy(strokingWithWidth: width, lineCap: .round, lineJoin: .round, miterLimit: 2)
    let thick = filled.union(rim, using: .winding).normalized(using: .winding)
    var outline = [[Double]]()
    thick.applyWithBlock { entry in
        let t = entry.pointee.type
        let count = t == .moveToPoint || t == .addLineToPoint ? 1 : t == .addQuadCurveToPoint ? 2 : t == .addCurveToPoint ? 3 : 0
        var row = [Double(t.rawValue)]
        for i in 0..<count { row += [entry.pointee.points[i].x, entry.pointee.points[i].y] }
        outline.append(row)
    }
    result[name] = outline
}
FileHandle.standardOutput.write(try JSONSerialization.data(withJSONObject: result))

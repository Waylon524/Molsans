import Foundation
import CoreGraphics
let input = try JSONSerialization.jsonObject(with: FileHandle.standardInput.readDataToEndOfFile()) as! [String:[[Double]]]
var result = [String:[[Double]]]()
for (name, commands) in input {
    let shape = CGMutablePath()
    for r in commands {
        func pt(_ i: Int) -> CGPoint { CGPoint(x:r[i], y:r[i+1]) }
        switch Int(r[0]) {
          case 0: shape.move(to:pt(1))
          case 1: shape.addLine(to:pt(1))
          case 2: shape.addQuadCurve(to:pt(3),control:pt(1))
          case 3: shape.addCurve(to:pt(5),control1:pt(1),control2:pt(3))
          default: shape.closeSubpath()
        }
    }
    var path = [[Double]]()
    shape.normalized(using:.winding).applyWithBlock { e in
        let t=e.pointee.type
        let n=t == .moveToPoint || t == .addLineToPoint ? 1 : t == .addQuadCurveToPoint ? 2 : t == .addCurveToPoint ? 3 : 0
        var a=[Double(t.rawValue)]
        for i in 0..<n { a += [e.pointee.points[i].x,e.pointee.points[i].y] }
        path.append(a)
    }
    result[name]=path
}
FileHandle.standardOutput.write(try JSONSerialization.data(withJSONObject:result))

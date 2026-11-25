import Foundation
import CoreGraphics
struct Operation: Decodable {let base:[[Double]];let fill:[[[Double]]];let cut:[[[Double]]]}
func make(_ commands:[[Double]]) -> CGPath {
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
    return shape
}
let input=try JSONDecoder().decode([String:Operation].self,from:FileHandle.standardInput.readDataToEndOfFile())
var result=[String:[[Double]]]()
for (name,op) in input {
    var shape=make(op.base)
    for (fill,cut) in zip(op.fill,op.cut) {
        shape=shape.union(make(fill),using:.winding).subtracting(make(cut),using:.winding)
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

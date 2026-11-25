import Foundation
import CoreGraphics

let input = try JSONSerialization.jsonObject(with: FileHandle.standardInput.readDataToEndOfFile()) as! [String: [[[Double]]]]
var result = [String: [[Double]]]()
for (key, paths) in input {
  var commands = [[Double]]()
  for path in paths {
    let p = CGMutablePath()
    func pt(_ r:[Double], _ i:Int) -> CGPoint { CGPoint(x:r[i], y:r[i+1]) }
    for r in path.dropFirst() {
      switch Int(r[0]) {
      case 0: p.move(to:pt(r,1))
      case 1: p.addLine(to:pt(r,1))
      case 2: p.addQuadCurve(to:pt(r,3),control:pt(r,1))
      case 3: p.addCurve(to:pt(r,5),control1:pt(r,1),control2:pt(r,3))
      default: p.closeSubpath()
      }
    }
    let s = p.copy(strokingWithWidth: path[0][0],lineCap: .butt,lineJoin: .round,miterLimit: 2)
    s.applyWithBlock { e in
      let t=e.pointee.type
      let n = t == .moveToPoint || t == .addLineToPoint ? 1 : t == .addQuadCurveToPoint ? 2 : t == .addCurveToPoint ? 3 : 0
      var v = [Double(t.rawValue)]
      for i in 0..<n { v += [e.pointee.points[i].x,e.pointee.points[i].y] }
      commands.append(v)
    }
  }
  result[key] = commands
}
FileHandle.standardOutput.write(try JSONSerialization.data(withJSONObject: result))

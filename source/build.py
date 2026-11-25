from fontTools.svgLib.path import parse_path
from fontTools.pens.basePen import BasePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.fontBuilder import FontBuilder
from fontTools.ttLib import TTFont
from fontTools.agl import UV2AGL
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
import json, subprocess, base64, html, pathlib, zipfile

# Coordinates in font space, 1000 UPM. Tube-like curves share tangent geometry
# but avoid apertures and terminals that look like literal molecule diagrams.
data = {}
widths = {}
class Pen(BasePen):
    def note(self,i,*coords): self.out.append([i,*[x for p in coords for x in p]])
    def _moveTo(self,p): self.note(0,p)
    def _lineTo(self,p): self.note(1,p)
    def _qCurveToOne(self,a,b): self.note(2,a,b)
    def _curveToOne(self,a,b,c): self.note(3,a,b,c)
    def _closePath(self): self.note(4)
    def _endPath(self): pass

def g(c, adv, *segments):
    widths[c]=adv
    data[c]=[]
    for seg in segments:
        n,s=seg if isinstance(seg,tuple) else (80,seg)
        p=Pen(None);p.out=[[n]]
        parse_path(s,p)
        # +6–8% over the first proof, with lighter joins and crossbars.
        p.out[0][0]=n+(6 if n>=75 else 4)
        data[c].append(p.out)

g('A',658,(82,'M72 8 L320 675 Q329 701 338 675 L586 8'),(69,'M170 220 H488'))
g('B',625,'M111 0 V680 H322 C437 680 503 619 503 520 C503 421 437 360 322 360 H111','M111 360 H350 C474 360 551 299 551 200 C551 101 474 40 350 40 H111')
g('C',668,'M568 590 C509 655 435 685 335 687 C181 687 88 543 88 360 C88 167 179 33 338 33 C438 33 522 68 586 139')
g('D',692,'M110 40 V680 H320 C499 680 596 550 596 360 C596 168 503 40 320 40 Z')
g('E',552,'M494 680 H111 V40 H500',(74,'M111 367 H449'))
g('F',533,'M110 0 V680 H493',(74,'M110 367 H444'))
g('G',715,'M596 586 C537 653 456 687 351 687 C180 687 89 545 89 361 C89 171 183 33 350 33 C480 33 613 87 613 188 V342 H374')
g('H',683,'M112 0 V720 M571 0 V720',(74,'M112 361 H571'))
g('I',228,'M143 0 V734')
g('J',484,'M371 720 V216 C371 92 312 31 209 31 C155 31 100 53 65 94')
g('K',613,'M112 0 V720','M533 699 L114 307 M293 474 L548 21')
g('L',516,'M112 720 V42 H476')
g('N',701,'M109 0 V679 Q109 715 132 681 L568 40 Q592 4 592 43 V720')
g('O',703,'M506 630 C463 668 407 689 345 688 C177 688 89 550 89 362 C89 173 184 32 350 32 C515 32 614 172 614 361 C614 480 578 568 503 633 Z')
g('P',602,'M111 0 V680 H322 C449 680 524 608 524 481 C524 355 449 286 321 286 H111')
g('Q',703,*[(s[0][0],'M503 633 C459 666 412 688 345 688 C177 688 89 550 89 362 C89 173 184 32 350 32 C515 32 614 172 614 361 C614 480 578 568 503 633 Z') for s in data['O']],(70,'M425 213 L618 -20'))
g('R',628,'M111 0 V680 H325 C455 680 528 610 528 487 C528 369 449 299 325 299 H111','M316 304 L557 21')
g('S',593,'M515 606 C460 657 385 684 301 684 C173 684 104 612 104 516 C104 421 185 376 305 351 C453 318 521 270 521 174 C522 89 441 34 310 34 C210 34 125 65 71 123')
g('T',598,(76,'M44 682 H554'),'M299 0 V682')
g('U',681,'M107 720 V276 C107 112 179 33 340 33 C496 33 574 110 574 276 V720')
g('V',648,(84,'M68 712 L315 47 Q326 16 337 47 L580 712'))
g('W',887,(84,'M69 712 L235 42 Q242 19 251 43 L270.191176 101'),(75,'M310.227941 222 L431 587 Q443 623 455 587 L576.443015 222'),(84,'M616.702206 101 L636 43 Q645 19 652 42 L818 712'))
g('X',616,'M79 696 L537 24 M537 696 L79 24')
g('Y',600,'M67 704 L300 350 L533 704 M300 350 V0')
g('Z',592,'M61 680 H519 L68 40 H545')
g('a',553,'M525 47 L504 40 C467 28 452 51 452 96 V353 C452 448 398 494 270 494 C158 494 82 396 82 261 C82 130 148 31 270 31 C381 31 452 115 452 261')
g('b',561,'M102 0 V754 M104 389 C133 451 194 493 282 493 C399 493 477 400 477 264 C477 129 400 31 283 31 C194 31 138 75 103 138')
g('c',494,'M412 435 C365 476 318 493 267 493 C156 493 82 396 82 263 C82 133 153 32 268 32 C327 32 380 55 423 97')
g('d',561,'M459 0 V754 M457 387 C430 449 371 494 281 494 C161 494 84 397 84 261 C84 127 159 31 281 31 C371 31 427 79 456 143')
g('e',532,'M88 226 L449 307 C452 421 381 493 272 493 C152 493 81 393 81 259 C81 125 155 32 274 32 C348 32 408 54 461 94')
g('f',374,'M143 0 V558 C143 670 180 725 257 725 C296 725 326 720 354 700',(74,'M32 483 H327'))
g('g',557,'M79 -105 C121 -145 174 -170 252 -170 C383 -170 454 -88 454 44 V351 C454 447 400 494 273 494 C156 494 82 399 82 264 C82 134 154 48 270 48 C381 48 454 137 454 253')
g('h',549,'M102 0 V754 M103 366 C147 447 209 491 294 491 C395 491 446 421 446 311 V0')
dot=(96,'M116 628 L116 714')
g('i',233,dot,'M116 0 V525')
g('j',255,(96,'M143 628 L143 714'),'M143 525 V-63 C143 -147 108 -189 56 -189 H37')
g('k',493,'M102 0 V754 M430 508 L104 217 M246 348 L466 16')
g('l',268,(78,'M113 754 V127 C113 65 142 21 196 34 L243 48'))
g('o',560,'M385 455 C351 482 306 495 271 495 C156 495 82 396 82 265 C82 131 153 30 277 30 C400 30 478 130 478 265 C478 350 446 411 385 455 Z')
g('p',561,'M102 -213 V525 M104 387 C134 450 194 493 282 493 C399 493 477 400 477 264 C477 129 400 31 283 31 C194 31 138 75 103 139')
g('q',561,'M459 -213 V525 M456 387 C429 450 370 493 281 493 C161 493 84 397 84 261 C84 127 159 31 281 31 C371 31 426 78 457 144')
g('s',470,'M385 437 C342 474 290 492 229 492 C139 492 81 447 81 375 C81 311 140 284 236 262 C345 238 395 205 395 141 C395 77 334 32 238 32 C161 32 109 55 64 93')
g('t',373,'M139 656 V158 C139 71 177 34 251 34 C277 34 306 41 328 53',(74,'M25 483 H332'))
g('u',548,'M446 0 V525 M445 154 C406 75 339 31 253 31 C154 31 102 103 102 212 V525')
g('v',496,'M59 509 L236 49 Q248 20 260 49 L437 509')
g('w',729,'M59 512 L185 46 Q192 22 201 47 L224 106',(74,'M215 83 L352 432 Q363 465 374 432 L513 82'),'M503 107 L527 47 Q536 22 543 46 L670 512')
g('x',494,'M58 508 L436 24 M436 508 L58 24')
g('y',497,'M58 507 L242 55 M438 507 L210 -76 C176 -157 141 -188 70 -185')
g('z',474,'M66 483 H404 L68 42 H427')
g('.',228,(93,'M113 0 L113 95'))
g(',',234,(78,'M135 96 L89 -63'))
g(':',236,(83,'M117 16 V93 M117 382 V459'))
g(';',236,(80,'M140 97 L94 -55 M117 382 V459'))
g('!',233,'M116 209 V720',(90,'M116 0 V96'))
g('?',482,'M73 590 C112 650 165 686 246 686 C339 686 403 628 403 544 C403 482 378 439 322 396 C256 347 237 309 237 226',(91,'M237 0 V94'))
g('-',395,(67,'M66 270 H329'))
g('–',555,(67,'M62 270 H493'))
g('+',555,(66,'M70 272 H485 M277 64 V482'))
g('=',555,(62,'M70 377 H485 M70 173 H485'))
g('/',427,(66,'M77 -110 L350 751'))
g('(',328,(66,'M262 -151 C151 -52 100 104 100 305 C100 493 150 656 262 754'))
g(')',328,(66,'M66 -151 C177 -52 228 104 228 305 C228 493 178 656 66 754'))
g('%',831,(61,'M155 32 L676 688 M325 547 C325 469 277 412 210 412 C144 412 96 470 96 547 C96 626 142 686 210 686 C276 686 325 626 325 547 Z M735 168 C735 90 687 33 620 33 C554 33 506 91 506 168 C506 247 552 307 620 307 C686 307 735 247 735 168 Z'))
g('0',610,'M316 687 C161 687 99 554 99 362 C99 168 164 32 316 32 C468 32 531 168 531 362 C531 556 467 687 316 687 Z',(53,'M239 262 L396 475'))
g('1',610,'M150 567 L316 681 V40',(74,'M151 39 H494'))
g('2',610,'M105 575 C156 647 220 686 317 686 C438 686 508 619 508 517 C508 439 466 384 357 283 L108 40 H535')
g('3',610,'M116 603 C172 659 236 685 321 685 C430 685 507 621 507 523 C507 427 436 365 321 365 H249 M324 365 C453 365 521 300 521 197 C521 90 437 33 315 33 C225 33 158 63 98 117')
g('4',610,'M430 0 V681 L87 225 H552')
g('5',610,'M505 679 H154 L129 374 C183 408 236 421 300 421 C434 421 521 347 521 224 C521 102 438 34 312 34 C225 34 157 61 101 115')
g('6',610,'M504 622 C452 664 401 686 325 686 C167 686 99 529 99 329 C99 109 173 33 313 33 C437 33 524 108 524 232 C524 355 439 428 321 428 C213 428 137 371 102 302')
g('7',610,'M91 679 H521 L234 12')
g('8',610,'M313 375 C193 375 119 435 119 526 C119 628 196 686 313 686 C430 686 506 629 506 526 C506 435 431 375 313 375 Z M313 375 C177 375 96 311 96 205 C96 96 179 33 313 33 C449 33 529 94 529 205 C529 311 447 375 313 375 Z')
g('9',610,'M92 83 C143 45 219 33 288 33 C447 33 516 169 516 383 C516 577 446 686 306 686 C187 686 103 607 103 489 C103 368 185 299 301 299 C394 299 462 339 510 414')
g(' ',273)
g('’',210,(77,'M126 710 L81 561'))
g("'",200,(77,'M100 711 V563'))
g('&',688,'M601 37 L259 363 C165 454 137 497 137 559 C137 635 195 688 280 688 C360 688 413 638 413 562 C413 490 362 443 269 395 C148 333 88 273 88 181 C88 93 167 33 273 33 C397 33 507 122 551 354')
g('_',511,(67,'M41 -78 H470'))

# Keep the original Bezier and stem geometry. Only the join's width profile changes.
from math import hypot
tapers={}
def lerp(p,q,t): return tuple(a+(b-a)*t for a,b in zip(p,q))
def split(curve,t):
    p,q,r,s=curve
    a,b,c=lerp(p,q,t),lerp(q,r,t),lerp(r,s,t)
    ab,bc=lerp(a,b,t),lerp(b,c,t)
    d=lerp(ab,bc,t)
    return (p,a,ab,d),(d,bc,c,s)
def path_tail(bez,extra):
    _,b=split(bez,.52)
    return 'M%.6f %.6f C%.6f %.6f %.6f %.6f %.6f %.6f '%tuple(v for p in b for v in p)+extra
def taper(c,bez,extra,first=27):
    tapers.setdefault(c,[]).append((bez,first))
    return path_tail(bez,extra)
m1=((102,374),(138,444),(199,491),(274,491))
m2=((402,371),(438,444),(500,491),(577,491))
n1=((103,375),(145,447),(207,491),(294,491))
r1=((103,364),(153,466),(238,501),(340,484))
g('m',804,'M101 0 V525',taper('m',m1,'C365 491 400 423 400 316 V0'),taper('m',m2,'C668 491 703 422 703 315 V0',28))
g('n',550,'M102 0 V525',taper('n',n1,'C396 491 447 421 447 311 V0'))
g('r',387,'M102 0 V525',taper('r',r1,'',27))

D1=((108,510),(152,604),(215,657),(289,657))
D2=((415,505),(456,601),(523,657),(599,657))
g('M',825,'M107 0 V699',taper('M',D1,'C376 657 414 589 414 464 V0',28),taper('M',D2,'C688 657 721 585 721 464 V0',28))

outlines=json.loads(subprocess.check_output(['./outline'],input=json.dumps(data).encode()))
# Smooth parallel outlines, expressed as cubic segments with shared endpoint
# tangents. The quintic width easing has zero slope and curvature at its ends.
def offset_point(bez,t,first,side):
    (_,a,b,p),_=split(bez,t)
    origin=b if abs(t)>1e-7 else bez[0]
    dx,dy=((p[0]-origin[0])/t,(p[1]-origin[1])/t) if abs(t)>1e-7 else (bez[1][0]-p[0],bez[1][1]-p[1])
    h=hypot(dx,dy)
    rise=(.12,.35) if side==1 else (.035,.27)
    u=max(0,min((t-rise[0])/rise[1],1))
    w=first+(43-first)*(u**3*(10+u*(-15+6*u)))
    return p[0]-side*w*dy/h,p[1]+side*w*dx/h
def tangent(bez,t,first,side):
    h=.00001
    a,b=offset_point(bez,t-h,first,side),offset_point(bez,t+h,first,side)
    return tuple((y-x)/(2*h) for x,y in zip(a,b))
def side_curves(bez,knots,first,side):
    cmds=[]
    for a,b in zip(knots,knots[1:]):
        p=offset_point(bez,a,first,side);q=offset_point(bez,b,first,side)
        u=tangent(bez,a,first,side);v=tangent(bez,b,first,side)
        h=(b-a)/3
        cmds.append([3,*(x+h*y for x,y in zip(p,u)),*(x-h*y for x,y in zip(q,v)),*q])
    return cmds
for ch,strips in tapers.items():
    for bez,first in strips:
        knots=(0,.06,.12,.18,.24,.30,.36,.42,.47,.52,.58)
        outlines[ch].extend([[0,*offset_point(bez,0,first,1)],
            *side_curves(bez,knots,first,1),[1,*offset_point(bez,.58,first,-1)],
            *side_curves(bez,knots[::-1],first,-1),[4]])
# Redraw the lower boundary, not a circular corner patch.  The polynomial
# positive-part matches value, slope and curvature both at the vertical
# stem edge and where it hands back to the original underside of the arch.
def soft_positive(z, radius):
    if z<=-radius: return 0.
    if z>=radius: return z
    u=(z+radius)/(2*radius)
    return radius*(2*u**3-u**4)
for ch,strips in tapers.items():
    for bez,first in strips:
        stem_x=bez[0][0]-(2 if ch=='m' and bez[0][0]==402 else 1)
        edge=stem_x+43
        radius=33 if ch!='M' else 37
        def at_x(x):
            lo,hi=-.16,.52
            for _ in range(48):
                mid=(lo+hi)/2
                if offset_point(bez,mid,first,-1)[0]<x: lo=mid
                else: hi=mid
            return (lo+hi)/2
        begin,end=at_x(edge-radius),at_x(edge+radius)
        def joint(t):
            x,y=offset_point(bez,t,first,-1)
            return edge+soft_positive(x-edge,radius),y
        def rate(t):
            h=.00001
            return tuple((y-x)/(2*h) for x,y in zip(joint(t-h),joint(t+h)))
        front,back=joint(begin),joint(end)
        rev=[end+(begin-end)*i/10 for i in range(11)]
        path=[[0,*front],[1,edge-8,front[1]],[1,edge-8,back[1]+10],
            [1,back[0]-5,back[1]+10],[1,*back]]
        for a,b in zip(rev,rev[1:]):
            p=joint(a);q=joint(b)
            h=(b-a)/3
            path.append([3,*(x+h*y for x,y in zip(p,rate(a))),*(x-h*y for x,y in zip(q,rate(b))),*q])
        outlines[ch].extend(path+[[4]])
# Remove contour overlaps. The four resulting glyphs use a unified outline.
clean=json.loads(subprocess.check_output(['./normalize'],input=json.dumps({c:outlines[c] for c in tapers}).encode()))
outlines.update(clean)

# Replace the exact span marked in the preview with one wide quarter-ellipse.
from math import sqrt
lo,hi=.55,.99
for _ in range(40):
    a=(2*lo+hi)/3;b=(lo+2*hi)/3
    if offset_point(r1,a,43,-1)[1] < offset_point(r1,b,43,-1)[1]: lo=a
    else: hi=b
r_peak=offset_point(r1,(lo+hi)/2,43,-1)
targets={'m':[(144,356,274,448),(443,353,577,448)],'n':[(145,357,294,448)],'r':[(145,346,*r_peak)]}
if 'M' in tapers: targets['M']=[(150,484,289,614),(457,481,599,614)]
k=4*(sqrt(2)-1)/3
ops={}
for c,arcs in targets.items():
    fill,cut=[],[]
    for x,y,u,v in arcs:
        rx,ry=u-x,v-y
        segment=[3,x,y+k*ry,u-k*rx,v,u,v]
        fill.append([[0,x,y],segment,[1,u,v+25],[3,u-k*rx,v+25,x,y+25+k*ry,x,y+25],
            [1,x-3,y+24],[1,x-3,y-12],[1,x,y-12],[4]])
        cut.append([[0,x,y],segment,[1,u,y-80],[1,x,y-80],[4]])
    ops[c]={'base':outlines[c],'fill':fill,'cut':cut}
outlines.update(json.loads(subprocess.check_output(['./boolean'],input=json.dumps(ops).encode())))

# The quarter-ellipse is rotated or reflected to match each shoulder.
# p and q keep their counters, and only the marked upper join is replaced.
shoulders={
    'p':(1,1,145,373,282,450),
    'q':(-1,1,-416,373,-281,450),
    'u':(-1,-1,-403,-172,-253,-74),
}
ops={}
for c,(sx,sy,x,y,u,v) in shoulders.items():
    rx,ry=u-x,v-y
    segment=[3,x,y+k*ry,u-k*rx,v,u,v]
    fill=[[0,x,y],segment,[1,u,v+25],[3,u-k*rx,v+25,x,y+25+k*ry,x,y+25],
          [1,x-3,y+24],[1,x-3,y-12],[1,x,y-12],[4]]
    cut=[[0,x,y],segment,[1,u,y-75],[1,x,y-75],[4]]
    def transform(path):
        return [[a[0],*(z*(sx if i%2==0 else sy) for i,z in enumerate(a[1:]))] for a in path]
    ops[c]={'base':outlines[c],'fill':[transform(fill)],'cut':[transform(cut)]}
outlines.update(json.loads(subprocess.check_output(['./boolean'],input=json.dumps(ops).encode())))
# The lower throats keep full outer weight. Ramp each straight inner
# diagonal from 90 to 81 drawing units with a tangent-matched cubic.
for x0,dx in [(251,180/544),(636,-181/544)]:
    normal=(-1/hypot(dx,1),dx/hypot(dx,1))
    def side(y,w,sign):
        return (x0+dx*(y-43)+sign*w*normal[0],y+sign*w*normal[1])
    low,high=101,224
    def run(a,b,wa,wb,sign):
        return [3,*side(a+(b-a)/3,wa,sign),*side(a+2*(b-a)/3,wb,sign),*side(b,wb,sign)]
    outlines['W'].extend([
        [0,*side(91,45,1)],[1,*side(low,45,1)],run(low,high,45,40.5,1),[1,*side(236,40.5,1)],
        [1,*side(236,40.5,-1)],[1,*side(high,40.5,-1)],run(high,low,40.5,45,-1),
        [1,*side(91,45,-1)],[4],
    ])
outlines.update(json.loads(subprocess.check_output(['./normalize'],input=json.dumps({'W':outlines['W']}).encode())))

# Keep the lower stem endpoints and lift the upper outline as a unit.
# The headstroke keeps its thickness and the advance remains identical.
def lift(cmd):
    return [cmd[0],*(v+(24 if v>=440 and i%2 else 0) for i,v in enumerate(cmd[1:]))]
outlines['M.low']=outlines['M']
outlines['M']=[lift(cmd) for cmd in outlines['M.low']]
outlines={c:outlines[c] for c in [*data,'M.low']}
font=FontBuilder(1000,isTTF=True)
names={c:UV2AGL.get(ord(c),f'uni{ord(c):04X}') if len(c)==1 else c for c in outlines}
bearings=dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ',[(26, 26), (64, 47), (42, 43), (63, 48), (65, 49), (65, 45), (42, 51), (64, 64), (71, 71), (50, 55), (63, 30), (62, 36), (61, 61), (61, 61), (42, 42), (63, 49), (42, 37), (63, 38), (34, 35), (37, 37), (58, 58), (23, 23), (23, 23), (36, 36), (25, 25), (44, 44)]))
bearings.update(zip('abcdefghijklmnopqrstuvwxyz',[(39, 39), (55, 40), (37, 37), (40, 55), (39, 39), (23, 21), (37, 52), (55, 54), (53, 53), (27, 50), (54, 28), (53, 35), (54, 55), (54, 55), (39, 39), (55, 40), (40, 55), (54, 26), (31, 34), (16, 29), (54, 54), (22, 22), (22, 22), (31, 31), (22, 25), (42, 41)]))
bearings['M.low']=bearings['M']
notdef=TTGlyphPen(None)
notdef.moveTo((59,0));notdef.lineTo((59,690));notdef.lineTo((510,690));notdef.lineTo((510,0));notdef.closePath()
notdef.moveTo((129,70));notdef.lineTo((440,70));notdef.lineTo((440,620));notdef.lineTo((129,620));notdef.closePath()
gs={'.notdef':notdef.glyph()}; metrics={'.notdef':(569,59)}
for c,path in outlines.items():
    pen=TTGlyphPen(None); conv=Cu2QuPen(pen,max_err=0.8,reverse_direction=True); bounds=BoundsPen(None)
    for r in path:
        getattr(bounds,['moveTo','lineTo','qCurveTo','curveTo','closePath'][int(r[0])])(*zip(r[1::2],r[2::2]))
    box=bounds.bounds
    delta=(bearings[c][0]-round(box[0])) if c in bearings else 0
    for r in path:
        method=['moveTo','lineTo','quadTo','curveTo','closePath'][int(r[0])]
        points=tuple(zip((x+delta for x in r[1::2]),r[2::2]))
        if method=='quadTo': method='qCurveTo'
        getattr(conv,method)(*points)
    name=names[c]
    gs[name]=pen.glyph()
    if getattr(gs[name],'flags',None):
        gs[name].flags[0] |= 0x40  # OVERLAP_SIMPLE, intentional in this drawing prototype
    if c in bearings:
        width=round(box[2])+delta+bearings[c][1]
    else:
        width=widths[c]
    metrics[name]=(width, (round(box[0])+delta) if box else 0)
font.setupGlyphOrder(list(gs))
font.setupCharacterMap({ord(c):n for c,n in names.items() if len(c)==1})
font.setupGlyf(gs)
font.setupHorizontalMetrics(metrics)
font.setupHorizontalHeader(ascent=900, descent=-235)
font.setupNameTable({
    'copyright': 'Copyright (c) 2026 Weilun Qian (Waylon524)',
    'familyName': 'MolSans',
    'styleName': 'Regular',
    'uniqueFontIdentifier': 'MolSans-Regular:1.000',
    'fullName': 'MolSans Regular',
    'psName': 'MolSans-Regular',
    'version': 'Version 1.000',
    'typographicFamily': 'MolSans',
    'typographicSubfamily': 'Regular',
    'licenseDescription': 'Licensed under the MIT License.',
    'licenseInfoURL': 'https://github.com/Waylon524/MolSans/blob/main/LICENSE',
})
font.setupOS2(version=4,sTypoAscender=900,sTypoDescender=-235,sTypoLineGap=0,usWinAscent=900,usWinDescent=235,usWeightClass=400,fsType=0,achVendID="MOLS",sxHeight=525,sCapHeight=720,fsSelection=192)
font.setupPost()
font.font['head'].macStyle=0
font.font['head'].fontRevision=1.0
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
pairs={'Mo':-12,'ol':-12,'lS':-9,'St':-11,'Ta':-53,'To':-56,'Te':-52,'Ty':-46,'Tr':-34,'Av':-33,'AV':-43,'VA':-43,'Wa':-32,'Wo':-27,'Ya':-46,'Yo':-47,'Ye':-49,'LT':-52,'LY':-44,'Fo':-27,'FA':-42,'Pa':-23,'PA':-41,'rt':-14,'fi':-16,'fa':-14,'ra':-12,'ry':-10,'Yo':-44,'Vi':-17,'Ve':-38,'No':-8,'g.':-22,'e.':-12,'s.':-13,'y.':-36,'e,':-12,'L.':-8,'rl':-10,'ry':-10,'Ve':-41,'Te':-54,'VA':-46,'TA':-37,'AW':-22,'AY':-40,'AT':-38,'YA':-39,'WA':-31,'LA':-12,'TL':-13,'y,':-35,'r,':-42,'r.':-45,'f.':-18,'oa':-9,'lo':-8,'vo':-19,'ro':-11,'va':-17,'we':-12,'wo':-12,'ff':-7,'fl':-14,'re':-34,'ls':-5,'li':-3}
pairs.update({'fa': -35, 'fc': -40, 'fd': -42, 'fe': -41, 'ff': -18, 'fg': -40, 'fj': -16, 'fm': -21, 'fn': -21, 'fo': -40, 'fp': -21, 'fq': -42, 'fr': -22, 'fs': -24, 'ft': -12, 'fu': -21, 'fz': -32, 'ra': -22, 'rc': -24, 'rd': -26, 'rg': -22, 'rj': -14, 'ro': -23, 'rq': -26, 'ta': -27, 'tc': -25, 'td': -29, 'te': -28, 'tg': -25, 'ti': -7, 'tj': -13, 'tl': -10, 'to': -27, 'tq': -29, 'tu': -12, 'il': 42})
pairs.update({'fl':18,'rl':17,'ol':2,'vl':18,'wl':18,'yl':16,'xl':11,'el':12,'sl':9,'tl':1,'it':30,'rt':-2})
features='feature kern {\n'+''.join(f'pos {names[a]} {names[b]} {i};\n' for (a,b),i in pairs.items())+'pos M.low o -12;\n} kern;'
lowercase=' '.join('abcdefghijklmnopqrstuvwxyz')
features='languagesystem DFLT dflt; languagesystem latn dflt;\n'+features
features+=f"\n@lower = [{lowercase}]; feature calt {{ sub M' @lower by M.low; }} calt;"
addOpenTypeFeaturesFromString(font.font,features)
out_dir=pathlib.Path(__file__).resolve().parent.parent/'dist'
out_dir.mkdir(exist_ok=True)
# Use fixed timestamps so rebuilding does not update the release metadata.
font.font.recalcTimestamp=False
font.font['head'].created=3878323200
font.font['head'].modified=3878323200
ttf=out_dir/'MolSans-Regular.ttf'
font.save(ttf)
checked=TTFont(ttf,recalcTimestamp=False)
assert len(checked.getBestCmap())==len(data)
checked.flavor='woff2'
checked.save(out_dir/'MolSans-Regular.woff2')
print('Built',ttf.name,'and MolSans-Regular.woff2')

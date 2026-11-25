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

# Publishing punctuation and technical symbols. Shared square dots and
# consistent horizontal levels keep them in the same visual family.
g('"',326,(68,'M101 711 V563 M225 711 V563'))
# Opening and closing quotations have distinct taper directions even at
# small sizes, using a short shoulder at the open end.
g('‘',210,(77,'M122 708 Q82 645 83 560'))
g('“',340,(77,'M119 708 Q79 645 80 560 M250 708 Q210 645 211 560'))
g('”',340,(77,'M132 708 Q133 644 95 560 M263 708 Q264 644 226 560'))
g('—',945,(67,'M66 270 H879'))
g('…',578,(93,'M116 0 V95 M289 0 V95 M462 0 V95'))
g('·',224,(83,'M112 229 V310'))
# Use a rounded outline for the list bullet; its apparent weight stays local.
g('•',355)
g('[',318,(66,'M258 754 H122 V-151 H258'))
g(']',318,(66,'M60 754 H196 V-151 H60'))
g('{',395,(66,'M334 754 C232 754 230 696 230 587 V460 C230 378 203 318 94 303 C203 288 230 229 230 147 V19 C230 -89 232 -151 334 -151'))
g('}',395,(66,'M61 754 C163 754 165 696 165 587 V460 C165 378 192 318 301 303 C192 288 165 229 165 147 V19 C165 -89 163 -151 61 -151'))
g('<',555,(65,'M474 485 L91 272 L474 59'))
g('>',555,(65,'M81 485 L464 272 L81 59'))
g('«',495,(65,'M229 438 L70 271 L229 104 M421 438 L262 271 L421 104'))
g('»',495,(65,'M74 438 L233 271 L74 104 M266 438 L425 271 L266 104'))
g(chr(92),427,(66,'M77 751 L350 -110')) # reverse solidus
g('|',227,(63,'M113 -151 V754'))
g('^',493,(66,'M76 472 L246 681 L416 472'))
g(chr(96),273,(68,'M95 747 L181 616'))
g('~',555,(60,'M75 246 C114 331 187 331 265 271 C339 212 419 208 478 293'))
g('*',462,(64,'M231 471 V739 M105 674 L357 536 M105 536 L357 674'))
g('#',647,(62,'M258 14 L361 697 M435 14 L538 697 M118 463 H636 M77 254 H595'))
g('$',600,'M515 605 C454 655 385 683 300 683 C173 683 104 611 104 516 C104 421 185 376 305 351 C453 318 521 270 521 174 C521 89 441 34 310 34 C210 34 125 65 71 123',(70,'M304 -43 V759'))
g('@',885,(64,'M687 29 C576 -54 433 -61 307 -24 C151 20 72 148 72 332 C72 535 216 688 432 688 C643 688 806 540 806 350 C806 238 756 156 664 156 C606 156 581 191 581 240 V514 M578 402 C557 463 510 504 434 504 C336 504 268 425 268 327 C268 228 330 159 429 159 C507 159 561 211 581 261'))
g('−',555,(67,'M70 272 H485'))
g('±',555,(62,'M72 392 H483 M277 202 V583 M72 99 H483'))
g('×',555,(62,'M107 103 L448 438 M448 103 L107 438'))
g('÷',555,(62,'M70 270 H485'),(83,'M277 415 V486 M277 55 V126'))
g('°',310,(49,'M154 490 C88 490 47 538 47 597 C47 658 88 704 154 704 C219 704 262 658 262 597 C262 538 219 490 154 490 Z'))
g('′',214,(59,'M138 711 L91 492'))
g('″',372,(59,'M137 711 L90 492 M291 711 L244 492'))

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
# Solid bullet, with no interior counter.
outlines['•']=[[0,177,355],[3,224,355,262,317,262,270],[3,262,223,224,185,177,185],
    [3,130,185,92,223,92,270],[3,92,317,130,355,177,355],[4]]
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
    'uniqueFontIdentifier': 'MolSans-Regular:1.100',
    'fullName': 'MolSans Regular',
    'psName': 'MolSans-Regular',
    'version': 'Version 1.100',
    'typographicFamily': 'MolSans',
    'typographicSubfamily': 'Regular',
    'licenseDescription': 'Licensed under the MIT License.',
    'licenseInfoURL': 'https://github.com/Waylon524/Molsans/blob/main/LICENSE',
})
font.setupOS2(version=4,sTypoAscender=900,sTypoDescender=-235,sTypoLineGap=0,usWinAscent=900,usWinDescent=235,usWeightClass=400,fsType=0,achVendID="MOLS",sxHeight=525,sCapHeight=720,fsSelection=192)
font.setupPost()
font.font['head'].macStyle=0
font.font['head'].fontRevision=1.1
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
pairs={'Mo':-12,'ol':-12,'lS':-9,'St':-11,'Ta':-53,'To':-56,'Te':-52,'Ty':-46,'Tr':-34,'Av':-33,'AV':-43,'VA':-43,'Wa':-32,'Wo':-27,'Ya':-46,'Yo':-47,'Ye':-49,'LT':-52,'LY':-44,'Fo':-27,'FA':-42,'Pa':-23,'PA':-41,'rt':-14,'fi':-16,'fa':-14,'ra':-12,'ry':-10,'Yo':-44,'Vi':-17,'Ve':-38,'No':-8,'g.':-22,'e.':-12,'s.':-13,'y.':-36,'e,':-12,'L.':-8,'rl':-10,'ry':-10,'Ve':-41,'Te':-54,'VA':-46,'TA':-37,'AW':-22,'AY':-40,'AT':-38,'YA':-39,'WA':-31,'LA':-12,'TL':-13,'y,':-35,'r,':-42,'r.':-45,'f.':-18,'oa':-9,'lo':-8,'vo':-19,'ro':-11,'va':-17,'we':-12,'wo':-12,'ff':-7,'fl':-14,'re':-34,'ls':-5,'li':-3}
pairs.update({'fa': -35, 'fc': -40, 'fd': -42, 'fe': -41, 'ff': -18, 'fg': -40, 'fj': -16, 'fm': -21, 'fn': -21, 'fo': -40, 'fp': -21, 'fq': -42, 'fr': -22, 'fs': -24, 'ft': -12, 'fu': -21, 'fz': -32, 'ra': -22, 'rc': -24, 'rd': -26, 'rg': -22, 'rj': -14, 'ro': -23, 'rq': -26, 'ta': -27, 'tc': -25, 'td': -29, 'te': -28, 'tg': -25, 'ti': -7, 'tj': -13, 'tl': -10, 'to': -27, 'tq': -29, 'tu': -12, 'il': 42})
pairs.update({'fl':18,'rl':17,'ol':2,'vl':18,'wl':18,'yl':16,'xl':11,'el':12,'sl':9,'tl':1,'it':30,'rt':-2})
pairs.update({'fa':-64,'fc':-67,'fd':-68,'fe':-68,'fg':-66,'fo':-70,'fq':-68,
              'fC':-21,'fG':-21,'fO':-21,'fQ':-21})
pairs.update({'“A':-44,'“T':-34,'“V':-32,'“W':-28,'‘A':-40,'’s':-22,
              'T.':-57,'V.':-54,'W.':-40,'A”':-40,'r”':-18})
# Positive spacing only where aligned vertical flanks are close; these
# are final per-pair values (in design units), not global tracking.
vertical_pairs = {'db': 22,
 'dh': 22,
 'di': 16,
 'dk': 23,
 'dl': 24,
 'dm': 23,
 'dn': 23,
 'dp': 22,
 'dr': 23,
 'du': 15,
 'dB': 13,
 'dD': 14,
 'dE': 12,
 'dF': 12,
 'dH': 13,
 'dI': 6,
 'dK': 14,
 'dL': 15,
 'dM': 16,
 'dN': 16,
 'dP': 14,
 'dR': 14,
 'dU': 19,
 'gb': 17,
 'gh': 17,
 'gi': 11,
 'gk': 18,
 'gl': 19,
 'gm': 18,
 'gn': 18,
 'gp': 17,
 'gr': 18,
 'gu': 18,
 'gB': 8,
 'gD': 9,
 'gE': 7,
 'gF': 7,
 'gH': 8,
 'gI': 1,
 'gK': 9,
 'gL': 10,
 'gM': 11,
 'gN': 11,
 'gP': 9,
 'gR': 9,
 'hb': 15,
 'hh': 15,
 'hi': 9,
 'hk': 16,
 'hm': 16,
 'hn': 16,
 'hp': 15,
 'hr': 16,
 'hu': 16,
 'hB': 6,
 'hD': 7,
 'hE': 5,
 'hF': 5,
 'hH': 6,
 'hK': 7,
 'hL': 8,
 'hM': 9,
 'hN': 9,
 'hP': 7,
 'hR': 7,
 'ib': 16,
 'ih': 16,
 'ii': 10,
 'ik': 17,
 'im': 17,
 'in': 17,
 'ip': 16,
 'ir': 17,
 'iu': 9,
 'iB': 7,
 'iD': 8,
 'iE': 6,
 'iF': 6,
 'iH': 7,
 'iK': 8,
 'iL': 9,
 'iM': 10,
 'iN': 10,
 'iP': 8,
 'iR': 8,
 'iU': 5,
 'jb': 19,
 'jh': 19,
 'ji': 13,
 'jk': 20,
 'jl': 21,
 'jm': 20,
 'jn': 20,
 'jp': 19,
 'jr': 20,
 'ju': 12,
 'jB': 10,
 'jD': 11,
 'jE': 9,
 'jF': 9,
 'jH': 10,
 'jI': 3,
 'jK': 11,
 'jL': 12,
 'jM': 13,
 'jN': 13,
 'jP': 11,
 'jR': 11,
 'jU': 8,
 'mb': 14,
 'mh': 14,
 'mi': 8,
 'mk': 15,
 'ml': 16,
 'mm': 15,
 'mn': 15,
 'mp': 14,
 'mr': 15,
 'mu': 15,
 'mB': 5,
 'mD': 6,
 'mE': 4,
 'mF': 4,
 'mH': 5,
 'mK': 6,
 'mL': 7,
 'mM': 8,
 'mN': 8,
 'mP': 6,
 'mR': 6,
 'nb': 14,
 'nh': 14,
 'ni': 8,
 'nk': 15,
 'nl': 16,
 'nm': 15,
 'nn': 15,
 'np': 14,
 'nr': 15,
 'nu': 15,
 'nB': 5,
 'nD': 6,
 'nE': 4,
 'nF': 4,
 'nH': 5,
 'nK': 6,
 'nL': 7,
 'nM': 8,
 'nN': 8,
 'nP': 6,
 'nR': 6,
 'qb': 22,
 'qh': 22,
 'qi': 16,
 'qk': 23,
 'ql': 24,
 'qm': 23,
 'qn': 23,
 'qp': 22,
 'qr': 23,
 'qu': 15,
 'qB': 13,
 'qD': 14,
 'qE': 12,
 'qF': 12,
 'qH': 13,
 'qI': 6,
 'qK': 14,
 'qL': 15,
 'qM': 16,
 'qN': 16,
 'qP': 14,
 'qR': 14,
 'qU': 11,
 'ub': 23,
 'uh': 23,
 'ui': 17,
 'uk': 24,
 'ul': 24,
 'um': 24,
 'un': 24,
 'up': 23,
 'ur': 24,
 'uu': 16,
 'uB': 14,
 'uD': 15,
 'uE': 13,
 'uF': 13,
 'uH': 14,
 'uI': 7,
 'uK': 15,
 'uL': 16,
 'uM': 17,
 'uN': 17,
 'uP': 15,
 'uR': 15,
 'uU': 12,
 'Gb': 18,
 'Gh': 18,
 'Gi': 12,
 'Gk': 19,
 'Gl': 20,
 'Gm': 19,
 'Gn': 19,
 'Gp': 18,
 'Gr': 19,
 'Gu': 19,
 'GB': 9,
 'GD': 10,
 'GE': 8,
 'GF': 8,
 'GH': 9,
 'GI': 2,
 'GK': 10,
 'GL': 11,
 'GM': 12,
 'GN': 12,
 'GP': 10,
 'GR': 10,
 'Hb': 13,
 'Hh': 13,
 'Hi': 7,
 'Hk': 14,
 'Hl': 15,
 'Hm': 14,
 'Hn': 14,
 'Hp': 13,
 'Hr': 14,
 'Hu': 6,
 'HB': 4,
 'HD': 5,
 'HE': 3,
 'HF': 3,
 'HH': 4,
 'HK': 5,
 'HL': 6,
 'HM': 7,
 'HN': 7,
 'HP': 5,
 'HR': 5,
 'HU': 10,
 'Ib': 6,
 'Ih': 6,
 'Ik': 7,
 'Il': 8,
 'Im': 7,
 'In': 7,
 'Ip': 6,
 'Ir': 7,
 'IU': 3,
 'Jb': 22,
 'Jh': 22,
 'Ji': 8,
 'Jk': 23,
 'Jl': 24,
 'Jm': 15,
 'Jn': 15,
 'Jp': 14,
 'Jr': 15,
 'Ju': 15,
 'JB': 13,
 'JD': 14,
 'JE': 12,
 'JF': 12,
 'JH': 13,
 'JI': 6,
 'JK': 14,
 'JL': 15,
 'JM': 16,
 'JN': 16,
 'JP': 14,
 'JR': 14,
 'JU': 19,
 'Mb': 16,
 'Mh': 16,
 'Mi': 10,
 'Mk': 17,
 'Ml': 18,
 'Mm': 17,
 'Mn': 17,
 'Mp': 16,
 'Mr': 17,
 'Mu': 9,
 'MB': 7,
 'MD': 8,
 'ME': 6,
 'MF': 6,
 'MH': 7,
 'MK': 8,
 'ML': 9,
 'MM': 10,
 'MN': 10,
 'MP': 8,
 'MR': 8,
 'MU': 5,
 'Nb': 16,
 'Nh': 16,
 'Ni': 10,
 'Nk': 17,
 'Nl': 18,
 'Nm': 17,
 'Nn': 17,
 'Np': 16,
 'Nr': 17,
 'Nu': 9,
 'NB': 7,
 'ND': 8,
 'NE': 6,
 'NF': 6,
 'NH': 7,
 'NK': 8,
 'NL': 9,
 'NM': 10,
 'NN': 10,
 'NP': 8,
 'NR': 8,
 'NU': 13,
 'Ub': 19,
 'Uh': 19,
 'Ui': 5,
 'Uk': 20,
 'Ul': 21,
 'Um': 12,
 'Un': 12,
 'Up': 11,
 'Ur': 12,
 'Uu': 12,
 'UB': 10,
 'UD': 11,
 'UE': 9,
 'UF': 9,
 'UH': 10,
 'UI': 3,
 'UK': 11,
 'UL': 12,
 'UM': 13,
 'UN': 13,
 'UP': 11,
 'UR': 11,
 'UU': 16}
pairs.update(vertical_pairs)
# Also open very narrow corridors whose curved faces run close for
# a substantial height. Previously balanced vertical pairs stay intact.
curve_pairs = {'ba': 24,
 'bb': 24,
 'bc': 24,
 'bd': 24,
 'be': 24,
 'bg': 24,
 'bh': 24,
 'bi': 18,
 'bk': 24,
 'bl': 24,
 'bm': 24,
 'bn': 24,
 'bo': 24,
 'bp': 24,
 'bq': 24,
 'br': 24,
 'bu': 24,
 'bw': 7,
 'bB': 15,
 'bC': 24,
 'bD': 16,
 'bE': 14,
 'bF': 14,
 'bG': 24,
 'bH': 15,
 'bI': 8,
 'bK': 16,
 'bL': 17,
 'bM': 18,
 'bN': 18,
 'bO': 24,
 'bP': 16,
 'bQ': 24,
 'bR': 16,
 'bU': 21,
 'da': 24,
 'dc': 24,
 'dd': 24,
 'de': 24,
 'dg': 24,
 'do': 24,
 'dq': 24,
 'dC': 24,
 'dG': 24,
 'dO': 24,
 'dQ': 24,
 'ew': 10,
 'ga': 24,
 'gc': 24,
 'gd': 24,
 'ge': 24,
 'gg': 24,
 'go': 24,
 'gq': 24,
 'gC': 24,
 'gG': 24,
 'gO': 24,
 'gQ': 24,
 'ha': 24,
 'hc': 24,
 'hd': 24,
 'he': 24,
 'hg': 24,
 'ho': 24,
 'hq': 24,
 'hC': 22,
 'hG': 22,
 'hO': 22,
 'hQ': 22,
 'ia': 19,
 'ic': 21,
 'id': 18,
 'ie': 19,
 'ig': 21,
 'io': 19,
 'iq': 18,
 'iC': 24,
 'iG': 24,
 'iO': 24,
 'iQ': 24,
 'ja': 22,
 'jc': 24,
 'jd': 21,
 'je': 22,
 'jg': 24,
 'jo': 22,
 'jq': 21,
 'jC': 24,
 'jG': 24,
 'jO': 24,
 'jQ': 24,
 'ma': 24,
 'mc': 24,
 'md': 24,
 'me': 24,
 'mg': 24,
 'mo': 24,
 'mq': 24,
 'mC': 22,
 'mG': 22,
 'mO': 21,
 'mQ': 21,
 'na': 24,
 'nc': 24,
 'nd': 24,
 'ne': 24,
 'ng': 24,
 'no': 24,
 'nq': 24,
 'nC': 21,
 'nG': 21,
 'nO': 21,
 'nQ': 21,
 'oa': 15,
 'ob': 24,
 'oc': 24,
 'od': 24,
 'oe': 24,
 'og': 24,
 'oh': 24,
 'oi': 19,
 'ok': 24,
 'ol': 26,
 'om': 24,
 'on': 24,
 'oo': 24,
 'op': 24,
 'oq': 24,
 'or': 24,
 'ou': 24,
 'ow': 6,
 'oB': 16,
 'oC': 24,
 'oD': 17,
 'oE': 15,
 'oF': 15,
 'oG': 24,
 'oH': 16,
 'oI': 9,
 'oK': 17,
 'oL': 18,
 'oM': 19,
 'oN': 19,
 'oO': 24,
 'oP': 17,
 'oQ': 24,
 'oR': 17,
 'oU': 22,
 'pa': 24,
 'pb': 24,
 'pc': 24,
 'pd': 24,
 'pe': 24,
 'pg': 24,
 'ph': 24,
 'pi': 18,
 'pk': 24,
 'pl': 24,
 'pm': 24,
 'pn': 24,
 'po': 24,
 'pp': 24,
 'pq': 24,
 'pr': 24,
 'pu': 24,
 'pw': 7,
 'pB': 15,
 'pC': 24,
 'pD': 16,
 'pE': 14,
 'pF': 14,
 'pG': 24,
 'pH': 15,
 'pI': 8,
 'pK': 16,
 'pL': 17,
 'pM': 18,
 'pN': 18,
 'pO': 24,
 'pP': 16,
 'pQ': 24,
 'pR': 16,
 'pU': 21,
 'qa': 24,
 'qc': 24,
 'qd': 24,
 'qe': 24,
 'qg': 24,
 'qo': 24,
 'qq': 24,
 'qC': 24,
 'qG': 24,
 'qO': 24,
 'qQ': 24,
 'sb': 23,
 'sh': 23,
 'si': 17,
 'sk': 24,
 'sm': 24,
 'sn': 24,
 'sp': 23,
 'sr': 24,
 'sB': 14,
 'sD': 15,
 'sE': 13,
 'sF': 13,
 'sH': 14,
 'sI': 7,
 'sK': 15,
 'sL': 16,
 'sM': 17,
 'sN': 17,
 'sP': 15,
 'sR': 15,
 'ua': 24,
 'uc': 24,
 'ud': 24,
 'ue': 24,
 'ug': 24,
 'uo': 24,
 'uq': 24,
 'uC': 24,
 'uG': 24,
 'uO': 24,
 'uQ': 24,
 'va': -12,
 'vo': -11,
 'wa': 7,
 'wc': 10,
 'wd': 6,
 'we': 7,
 'wg': 10,
 'wo': 7,
 'wq': 6,
 'wC': 24,
 'wG': 24,
 'wO': 24,
 'wQ': 24,
 'Ba': 24,
 'Bb': 10,
 'Bc': 24,
 'Bg': 24,
 'Bh': 10,
 'Bi': 4,
 'Bk': 11,
 'Bl': 12,
 'Bm': 11,
 'Bn': 11,
 'Bo': 23,
 'Bp': 10,
 'Br': 11,
 'Bu': 11,
 'BB': 3,
 'BC': 10,
 'BD': 4,
 'BE': 2,
 'BF': 2,
 'BH': 3,
 'BK': 4,
 'BL': 5,
 'BM': 6,
 'BN': 6,
 'BP': 4,
 'BR': 4,
 'BU': 6,
 'Da': 21,
 'Db': 24,
 'Dc': 23,
 'Dd': 20,
 'De': 20,
 'Dg': 23,
 'Dh': 24,
 'Di': 18,
 'Dk': 24,
 'Dl': 24,
 'Dm': 24,
 'Dn': 24,
 'Do': 21,
 'Dp': 24,
 'Dq': 20,
 'Dr': 24,
 'Du': 24,
 'Dw': 23,
 'DB': 23,
 'DC': 24,
 'DD': 24,
 'DE': 22,
 'DF': 22,
 'DG': 24,
 'DH': 23,
 'DI': 18,
 'DK': 24,
 'DL': 24,
 'DM': 24,
 'DN': 24,
 'DO': 24,
 'DP': 24,
 'DQ': 24,
 'DR': 24,
 'DU': 24,
 'Ga': 24,
 'Gc': 24,
 'Gd': 24,
 'Ge': 24,
 'Gg': 24,
 'Go': 24,
 'Gq': 24,
 'GC': 21,
 'GG': 21,
 'GO': 21,
 'GQ': 21,
 'GU': 14,
 'Ha': 16,
 'Hc': 18,
 'Hd': 15,
 'He': 16,
 'Hg': 18,
 'Ho': 16,
 'Hq': 15,
 'HC': 24,
 'HG': 24,
 'HO': 24,
 'HQ': 24,
 'Ia': 9,
 'Ic': 11,
 'Id': 8,
 'Ie': 9,
 'Ig': 11,
 'Io': 9,
 'Iq': 8,
 'IC': 22,
 'IG': 22,
 'IO': 22,
 'IQ': 22,
 'Ja': 24,
 'Jc': 24,
 'Jd': 24,
 'Je': 24,
 'Jg': 24,
 'Jo': 24,
 'Jq': 24,
 'Js': 24,
 'JC': 24,
 'JG': 24,
 'JO': 24,
 'JQ': 24,
 'JS': 4,
 'Ma': 19,
 'Mc': 21,
 'Md': 18,
 'Me': 19,
 'Mg': 21,
 'Mo': 12,
 'Mq': 18,
 'MC': 24,
 'MG': 24,
 'MO': 24,
 'MQ': 24,
 'Na': 19,
 'Nc': 21,
 'Nd': 18,
 'Ne': 19,
 'Ng': 21,
 'No': 16,
 'Nq': 18,
 'NC': 24,
 'NG': 24,
 'NO': 24,
 'NQ': 24,
 'Oa': 24,
 'Ob': 24,
 'Oc': 24,
 'Od': 24,
 'Oe': 24,
 'Og': 24,
 'Oh': 24,
 'Oi': 24,
 'Ok': 24,
 'Ol': 24,
 'Om': 24,
 'On': 24,
 'Oo': 24,
 'Op': 24,
 'Oq': 24,
 'Or': 24,
 'Ou': 24,
 'Ow': 24,
 'OB': 24,
 'OC': 24,
 'OD': 24,
 'OE': 24,
 'OF': 24,
 'OG': 24,
 'OH': 24,
 'OI': 22,
 'OK': 24,
 'OL': 24,
 'OM': 24,
 'ON': 24,
 'OO': 24,
 'OP': 24,
 'OQ': 24,
 'OR': 24,
 'OU': 24,
 'Pb': 8,
 'Ph': 8,
 'Pi': 2,
 'Pk': 9,
 'Pl': 10,
 'Pm': 9,
 'Pn': 9,
 'Pp': 8,
 'Pr': 9,
 'Pu': 9,
 'PB': 10,
 'PC': 15,
 'PD': 11,
 'PE': 9,
 'PF': 9,
 'PG': 16,
 'PH': 10,
 'PI': 3,
 'PK': 11,
 'PL': 12,
 'PM': 13,
 'PN': 13,
 'PO': 16,
 'PP': 11,
 'PQ': 16,
 'PR': 11,
 'PU': 16,
 'Qa': 24,
 'Qb': 24,
 'Qc': 24,
 'Qd': 24,
 'Qe': 24,
 'Qg': 24,
 'Qh': 24,
 'Qi': 24,
 'Qk': 24,
 'Ql': 24,
 'Qm': 24,
 'Qn': 24,
 'Qo': 24,
 'Qp': 24,
 'Qq': 24,
 'Qr': 24,
 'Qu': 24,
 'Qw': 24,
 'QB': 24,
 'QC': 24,
 'QD': 24,
 'QE': 24,
 'QF': 24,
 'QG': 24,
 'QH': 24,
 'QI': 24,
 'QK': 24,
 'QL': 24,
 'QM': 24,
 'QN': 24,
 'QO': 24,
 'QP': 24,
 'QQ': 24,
 'QR': 24,
 'QU': 24,
 'RC': 6,
 'RG': 6,
 'RO': 7,
 'RQ': 7,
 'Sb': 22,
 'Sh': 22,
 'Si': 16,
 'Sk': 23,
 'Sl': 24,
 'Sm': 23,
 'Sn': 23,
 'Sp': 22,
 'Sr': 23,
 'St': -10,
 'SB': 15,
 'SD': 16,
 'SE': 14,
 'SF': 14,
 'SH': 15,
 'SI': 8,
 'SK': 16,
 'SL': 17,
 'SM': 18,
 'SN': 18,
 'SP': 16,
 'SR': 16,
 'Ua': 22,
 'Uc': 24,
 'Ud': 21,
 'Ue': 22,
 'Ug': 24,
 'Uo': 22,
 'Uq': 21,
 'Us': 21,
 'UC': 24,
 'UG': 24,
 'UO': 24,
 'UQ': 24,
 'US': 1}
curve_pairs.pop("Mo",None)  # keep the approved brand/context pair
pairs.update(curve_pairs)
def variants(c):
    return ['M','M.low'] if c=='M' else [names[c]]
low_pairs=''.join(f'pos {x} {y} {value};\n'
    for (a,b),value in (vertical_pairs | curve_pairs).items() if 'M' in (a,b)
    for x in variants(a) for y in variants(b) if 'M.low' in (x,y))
features='feature kern {\n'+''.join(f'pos {names[a]} {names[b]} {i};\n' for (a,b),i in pairs.items())+'pos M.low o -12;\n'+low_pairs+'} kern;'
lowercase=' '.join('abcdefghijklmnopqrstuvwxyz')
features='languagesystem DFLT dflt; languagesystem latn dflt;\n'+features
features+=f"\n@lower = [{lowercase}]; feature calt {{ sub M' @lower by M.low; }} calt;"
addOpenTypeFeaturesFromString(font.font,features)
# Keep deterministic timestamps and derive the shipping family from this base.
import tempfile
from family import build_family
out_dir = pathlib.Path(__file__).resolve().parent.parent / 'dist'
font.font.recalcTimestamp = False
font.font['head'].created = 3878323200
font.font['head'].modified = 3878323200
with tempfile.TemporaryDirectory(prefix='molsans-base-') as tmp:
    ttf = pathlib.Path(tmp) / 'Molsans-base.ttf'
    font.save(ttf)
    checked = TTFont(ttf, recalcTimestamp=False)
    assert len(checked.getBestCmap()) == len(data)
    build_family(ttf, out_dir)

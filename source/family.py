"""Derive the three Molsans release faces from the base drawing."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.pens.basePen import BasePen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

# Extra bearing only where a preceding contour approaches the left end
# of the t/f crossbar. The values already allow for both thicker edges.
INCREASES = {
    'ut':24, 'dt':20, 'qt':20, 'ct':21, 'Ot':23, 'Dt':18, 'Qt':27,
    'rt':29, 'vt':30, 'wt':30, 'yt':28, 'xt':23, 'zt':23,
    'tt':24, 'ft':12, 'Pt':19, 'Jt':13, 'Rt':12, 'Ut':12, 'jt':12,
    'st':12, 'Mt':10, 'Nt':10,
    'vf':26, 'wf':26, 'yf':24, 'rf':22, 'xf':19, 'zf':17,
    'Qf':15, 'tf':14, 'Of':13, 'Pf':12, 'cf':12, 'uf':11,
    'df':10, 'qf':10, 'ff':10, 'Df':10, 'Jf':10,
}

class OutlinePen(BasePen):
    def __init__(self, glyphs):
        super().__init__(glyphs)
        self.data = []
    def store(self, op, *points):
        self.data.append([op, *(v for point in points for v in point)])
    def _moveTo(self, p):
        self.store(0, p)
    def _lineTo(self, p):
        self.store(1, p)
    def _qCurveToOne(self, p, q):
        self.store(2, p, q)
    def _curveToOne(self, p, q, r):
        self.store(3, p, q, r)
    def _closePath(self):
        self.store(4)
    def _endPath(self):
        self.store(4)

def embolden(font, width, extra_advance, helper):
    glyphset = font.getGlyphSet()
    outlines = {}
    for name in font.getGlyphOrder():
        if name == '.notdef':
            continue
        pen = OutlinePen(glyphset)
        glyphset[name].draw(pen)
        outlines[name] = pen.data

    bold = json.loads(subprocess.check_output([helper, str(width)], input=json.dumps(outlines).encode()))

    glyf = font['glyf']
    for name, commands in bold.items():
        if not commands:
            continue
        original_min = glyf[name].xMin
        advance, bearing = font['hmtx'][name]
        pen = TTGlyphPen(None)
        shift = extra_advance // 2
        convert = Cu2QuPen(TransformPen(pen, (1, 0, 0, 1, shift, 0)), max_err=.6, reverse_direction=True)
        for op, *coords in commands:
            getattr(convert, ['moveTo', 'lineTo', 'qCurveTo', 'curveTo', 'closePath'][op])(
                *zip(coords[::2], coords[1::2]))
        glyph = pen.glyph()
        glyph.recalcBounds(glyf)
        glyf[name] = glyph
        font['hmtx'][name] = advance + extra_advance, bearing + glyph.xMin - original_min


def adjust_pairs(font):
    pairs = {}
    for lookup in font['GPOS'].table.LookupList.Lookup:
        assert lookup.LookupType == 2
        for sub in lookup.SubTable:
            assert sub.Format == 1 and sub.ValueFormat1 == 4 and sub.ValueFormat2 == 0
            for first, ps in zip(sub.Coverage.glyphs, sub.PairSet):
                for item in ps.PairValueRecord:
                    pairs[first, item.SecondGlyph] = item.Value1.XAdvance
    cmap = font.getBestCmap()
    for (a, b), extra in INCREASES.items():
        key = cmap[ord(a)], cmap[ord(b)]
        pairs[key] = pairs.get(key, 0) + extra
        if a == 'M':
            low = 'M.low', key[1]
            pairs[low] = pairs.get(low, 0) + extra
    feature = 'languagesystem DFLT dflt; languagesystem latn dflt;\nfeature kern {\n'
    feature += ''.join(f'pos {a} {b} {v};\n' for (a, b), v in sorted(pairs.items()) if v)
    addOpenTypeFeaturesFromString(font, feature + '} kern;', tables=['GPOS'])


FACES = (('Regular', 400, 0, 0), ('Medium', 500, 8, 0), ('Bold', 700, 24, 16))

def identity(font, style, weight):
    legacy_family = 'Molsans Medium' if style == 'Medium' else 'Molsans'
    legacy_style = 'Bold' if style == 'Bold' else 'Regular'
    full_name = f'Molsans {style}'
    ps = f'Molsans-{style}'
    replacement = {1: legacy_family, 2: legacy_style, 3: f'{ps}:1.200',
                   4: full_name, 5: 'Version 1.200', 6: ps, 16: 'Molsans', 17: style}
    for record in font['name'].names:
        if record.nameID in replacement:
            record.string = replacement[record.nameID].encode(record.getEncoding())
    os2 = font['OS/2']
    os2.usWeightClass = weight
    os2.fsSelection = (os2.fsSelection & ~0x60) | (0x20 if style == 'Bold' else 0x40)
    head = font['head']
    head.macStyle = (head.macStyle & ~1) | (style == 'Bold')
    head.fontRevision = 1.2

def build_family(source, output):
    output.mkdir(exist_ok=True, parents=True)
    with tempfile.TemporaryDirectory(prefix='molsans-family-') as tmp:
        helper = str(Path(tmp) / 'embolden')
        swift = str(Path(__file__).with_name('embolden.swift'))
        subprocess.run(['swiftc', swift, '-o', helper], check=True)
        for style, weight, width, extra_advance in FACES:
            font = TTFont(source, recalcTimestamp=False)
            adjust_pairs(font)
            if width:
                embolden(font, width, extra_advance, helper)
            identity(font, style, weight)
            font.save(output / f'Molsans-{style}.ttf')
            font.flavor = 'woff2'
            font.save(output / f'Molsans-{style}.woff2')
            print(f'Built Molsans {style} as TTF and WOFF2')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    build_family(args.source, args.output)

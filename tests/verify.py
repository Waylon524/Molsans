from pathlib import Path
import string

from fontTools.pens.areaPen import AreaPen
from fontTools.ttLib import TTFont

dist = Path(__file__).resolve().parents[1] / 'dist'
sample = 'Molsans Molstage Molish'

def pair_values(font):
    return {
        (first, v.SecondGlyph): v.Value1.XAdvance
        for lookup in font['GPOS'].table.LookupList.Lookup
        for sub in lookup.SubTable
        for first, ps in zip(sub.Coverage.glyphs, sub.PairSet)
        for v in ps.PairValueRecord
    }

def ink(font, char):
    gs = font.getGlyphSet()
    pen = AreaPen(gs)
    gs[font.getBestCmap()[ord(char)]].draw(pen)
    return abs(pen.value)

faces = []
for style, weight in [('Regular', 400), ('Medium', 500), ('Bold', 700)]:
    ttf, woff = (TTFont(dist / f'Molsans-{style}.{ext}') for ext in ('ttf', 'woff2'))
    faces.append(ttf)
    assert woff.flavor == 'woff2'
    cmap = ttf.getBestCmap()
    assert cmap == woff.getBestCmap()
    assert len(cmap) == 113
    assert all(ord(c) in cmap for c in string.ascii_letters + string.digits + string.punctuation)
    assert all(ord(c) in cmap for c in '‘’“”«»–—…•·−±×÷°′″')
    assert len({ttf['hmtx'][cmap[ord(c)]][0] for c in string.digits}) == 1
    for font in (ttf, woff):
        pairs = pair_values(font)
        for pair, value in {'DI':18, 'OR':24, 'ge':24, 'fo':-70, 'il':42, 're':-34,
                            'ut':24, 'dt':20, 'rt':27, 'tt':24}.items():
            assert pairs[tuple(pair)] == value, (pair, pairs.get(tuple(pair)))
        assert pairs['M.low', 'o'] == -12
        assert font['name'].getDebugName(16) == 'Molsans'
        assert font['name'].getDebugName(17) == style
        assert font['name'].getDebugName(6) == f'Molsans-{style}'
        assert font['name'].getDebugName(5) == 'Version 1.200'
        assert font['name'].getDebugName(13) == 'Licensed under the MIT License.'
        assert font['OS/2'].usWeightClass == weight
        assert font['OS/2'].fsType == 0
        assert font['hmtx']['M'] == font['hmtx']['M.low']
        assert font['glyf']['M'].yMax - font['glyf']['M.low'].yMax == 24
        assert any(r.FeatureTag == 'calt' for r in font['GSUB'].table.FeatureList.FeatureRecord)
    assert ttf['hmtx'].metrics == woff['hmtx'].metrics
    assert pair_values(ttf) == pair_values(woff)
weights = [sum(ink(f, ch) for ch in sample) for f in faces]
assert weights[0] < weights[1] < weights[2], weights
assert all(v[0] == faces[1]['hmtx'][g][0] for g, v in faces[0]['hmtx'].metrics.items())
print('Molsans v1.2 verified: three real weights, glyph coverage, kerning, contextual M and embedding.')

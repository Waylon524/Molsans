from pathlib import Path
import string
from fontTools.ttLib import TTFont

dist = Path(__file__).resolve().parents[1] / 'dist'
ttf, woff = (TTFont(dist / ('MolSans-Regular.' + ext)) for ext in ('ttf', 'woff2'))
assert woff.flavor == 'woff2'
cmap = ttf.getBestCmap()
assert cmap == woff.getBestCmap()
assert all(ord(c) in cmap for c in string.ascii_letters + string.digits)
assert len({ttf['hmtx'][cmap[ord(c)]][0] for c in string.digits}) == 1
for f in (ttf, woff):
    assert f['name'].getDebugName(1) == 'MolSans'
    assert f['name'].getDebugName(5) == 'Version 1.000'
    assert f['name'].getDebugName(13) == 'Licensed under the MIT License.'
    assert f['OS/2'].fsType == 0
    assert f['hmtx']['M'] == f['hmtx']['M.low']
    assert f['glyf']['M'].yMax - f['glyf']['M.low'].yMax == 24
    assert any(r.FeatureTag == 'calt' for r in f['GSUB'].table.FeatureList.FeatureRecord)
print('Verified MolSans v1.0 TTF and WOFF2: metadata, embedding, glyph coverage and both M forms.')

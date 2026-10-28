"""Bundle the project into one self-contained HTML file: dist/duck-skate.html"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
css = open(os.path.join(ROOT, 'style.css'), encoding='utf-8').read()
html = html.replace('<link rel="stylesheet" href="style.css">', '<style>\n' + css + '\n</style>')
def inline(m):
    src = open(os.path.join(ROOT, m.group(1)), encoding='utf-8').read().replace('</script', '<\\/script')
    return '<script>\n' + src + '\n</script>'
html = re.sub(r'<script src="([^"]+)"></script>', inline, html)
# artifact pages are wrapped in their own skeleton: drop doctype/html/head/body tags
html = re.sub(r'<!doctype html>\s*|</?html[^>]*>|</?head>|</?body>', '', html, flags=re.I)
html = html.replace('<meta charset="utf-8">', '')
os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
out = os.path.join(ROOT, 'dist', 'duck-skate.html')
open(out, 'w', encoding='utf-8').write(html.strip() + '\n')
print(out, round(os.path.getsize(out) / 1e6, 2), 'MB')

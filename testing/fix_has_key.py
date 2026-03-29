import re
fp = r'f:\BKChem\BKChem3\bkchem\Pmw.py'
with open(fp, 'r', encoding='utf-8') as f:
    text = f.read()

# Pattern: self.'...' in _pending
# Replacement: '...' in self._pending
text = re.sub(r'self\.(\'[^\']+\'|\"[^\"]+\")\s+in\s+_pending', r'\1 in self._pending', text)

with open(fp, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)

print('Fixed all self.keys in _pending')

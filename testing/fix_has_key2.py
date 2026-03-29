import re
fp = r'f:\BKChem\BKChem3\bkchem\Pmw.py'
with open(fp, 'r', encoding='utf-8') as f:
    text = f.read()

# Pattern: self.'...' in _someWord
# Should be: '...' in self._someWord
text = re.sub(r'self\.(\'[^\']+\'|\"[^\"]+\")\s+in\s+(_\w+|\w+)', r'\1 in self.\2', text)
# And the other way: if something.'...' in _someWord -> '...' in something._someWord
text = re.sub(r'(\w+)\.(\'[^\']+\'|\"[^\"]+\")\s+in\s+(_\w+|\w+)', r'\2 in \1.\3', text)

with open(fp, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)

print('Fixed all obj.keys in dictionary')

import re
fp = r'f:\BKChem\BKChem3\bkchem\Pmw.py'
with open(fp, 'r', encoding='utf-8') as f: content = f.read()

content = re.sub(r'\bstring\.atol\b', 'int', content)
content = re.sub(r'\bstring\.atoi\b', 'int', content)
content = re.sub(r'\bstring\.atof\b', 'float', content)

with open(fp, 'w', encoding='utf-8', newline='\n') as f: f.write(content)
print('Fixed string numerical functions in Pmw.py')

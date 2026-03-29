import os, re

def fix_stringio(directory):
    for d, _, fs in os.walk(directory):
        for f in fs:
            if not f.endswith('.py'): continue
            fp = os.path.join(d, f)
            with open(fp, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # import cStringIO as StringIO -> import io \n StringIO = io.StringIO
            # from cStringIO import StringIO -> from io import StringIO
            # import StringIO -> import io \n StringIO = io.StringIO
            original = content
            content = re.sub(r'^from\s+(?:c|)StringIO\s+import\s+StringIO\b', 'from io import StringIO', content, flags=re.MULTILINE)
            content = re.sub(r'^import\s+(?:c|)StringIO\b', 'import io\nStringIO = io.StringIO', content, flags=re.MULTILINE)
            content = re.sub(r'^import\s+(?:c|)StringIO\s+as\s+StringIO\b', 'import io\nStringIO = io.StringIO', content, flags=re.MULTILINE)
            
            if original != content:
                with open(fp, 'w', encoding='utf-8') as file:
                    file.write(content)
                print(f"Fixed StringIO in {fp}")

fix_stringio(r'f:\BKChem\BKChem3')

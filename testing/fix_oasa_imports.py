import os, re

def fix_oasa_imports(directory):
    for d, _, fs in os.walk(directory):
        if d != directory: continue
        for f in fs:
            if not f.endswith('.py'): continue
            fp = os.path.join(d, f)
            with open(fp, 'r', encoding='utf-8') as file:
                content = file.read()
            
            new_content = content
            # import oasa -> from . import oasa
            new_content = re.sub(r'^(\s*)import\s+oasa\b', r'\1from . import oasa', new_content, flags=re.MULTILINE)
            # from oasa import ... -> from .oasa import ...
            new_content = re.sub(r'^(\s*)from\s+oasa(?=\b|\.)', r'\1from .oasa', new_content, flags=re.MULTILINE)
            
            if new_content != content:
                with open(fp, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"Fixed {fp}")

fix_oasa_imports(r'f:\BKChem\BKChem3\bkchem')
fix_oasa_imports(r'f:\BKChem\BKChem3\bkchem\plugins')
fix_oasa_imports(r'f:\BKChem\BKChem3\bkchem\oasa\oasa')

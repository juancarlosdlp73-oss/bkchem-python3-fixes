import os, re

def fix_pkg_imports(directory):
    for d, _, fs in os.walk(directory):
        for f in fs:
            if not f.endswith('.py'): continue
            fp = os.path.join(d, f)
            with open(fp, 'r', encoding='utf-8') as file:
                content = file.read()
            
            new_content = content
            new_content = re.sub(r'\bfrom\s+htmlentitydefs\s+import\b', 'from html.entities import', new_content)
            new_content = re.sub(r'\bimport\s+htmlentitydefs\b', 'import html.entities as htmlentitydefs', new_content)
            
            if new_content != content:
                with open(fp, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"Fixed {fp}")

fix_pkg_imports(r'f:\BKChem\BKChem3')

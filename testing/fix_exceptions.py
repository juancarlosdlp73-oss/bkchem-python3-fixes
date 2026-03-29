import os, re

def fix_pkg_imports(directory):
    for d, _, fs in os.walk(directory):
        for f in fs:
            if not f.endswith('.py'): continue
            fp = os.path.join(d, f)
            with open(fp, 'r', encoding='utf-8') as file:
                content = file.read()
            
            new_content = re.sub(r'^\s*import\s+exceptions\b.*\n', '', content, flags=re.MULTILINE)
            # also replace ValueError with ValueError
            new_content = re.sub(r'\bexceptions\.', '', new_content)
            
            if new_content != content:
                with open(fp, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"Fixed {fp}")

fix_pkg_imports(r'f:\BKChem\BKChem3')

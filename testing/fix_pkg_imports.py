import os, re

def fix_pkg_imports(directory):
    packages = ['graph', 'transform', 'coords_generator']
    
    for d, _, fs in os.walk(directory):
        for f in fs:
            if not f.endswith('.py'): continue
            fp = os.path.join(d, f)
            with open(fp, 'r', encoding='utf-8') as file:
                content = file.read()
            
            new_content = content
            for pkg in packages:
                # from graph.sub import something -> from .graph.sub import something
                new_content = re.sub(r'^(from\s+)' + pkg + r'(\.)', r'\1.' + pkg + r'\2', new_content, flags=re.MULTILINE)
                new_content = re.sub(r'^(import\s+)' + pkg + r'(\.)', r'\1.' + pkg + r'\2', new_content, flags=re.MULTILINE)
            
            if new_content != content:
                with open(fp, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"Fixed {fp}")

fix_pkg_imports(r'f:\BKChem\BKChem3\bkchem\oasa\oasa')
fix_pkg_imports(r'f:\BKChem\BKChem3\bkchem\plugins')
fix_pkg_imports(r'f:\BKChem\BKChem3\bkchem')

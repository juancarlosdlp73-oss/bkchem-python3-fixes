import os, re

def fix_imports(directory):
    modules = [f[:-3] for f in os.listdir(directory) if f.endswith('.py') and not f.startswith('__')]
    modules.extend(['graph', 'transform', 'coords_generator'])  # subpackages
    
    for d, _, fs in os.walk(directory):
        for f in fs:
            if not f.endswith('.py'): continue
            fp = os.path.join(d, f)
            with open(fp, 'r', encoding='utf-8') as file:
                content = file.read()
            
            new_content = content
            for mod in modules:
                # import mod -> from . import mod
                new_content = re.sub(r'^(import\s+)' + mod + r'\b', r'from . \1' + mod, new_content, flags=re.MULTILINE)
                # from mod import something -> from .mod import something
                new_content = re.sub(r'^(from\s+)' + mod + r'(\s+import\b)', r'\1.' + mod + r'\2', new_content, flags=re.MULTILINE)
            
            if new_content != content:
                with open(fp, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"Fixed {fp}")

fix_imports(r'f:\BKChem\BKChem3\bkchem\oasa\oasa')
fix_imports(r'f:\BKChem\BKChem3\bkchem\plugins')
fix_imports(r'f:\BKChem\BKChem3\bkchem\plugins\piddle')

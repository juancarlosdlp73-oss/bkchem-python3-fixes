import os, re

# Maps Python 2 Tkinter modules to Python 3
tk_modules = {
    'tkMessageBox': 'tkinter.messagebox',
    'tkFileDialog': 'tkinter.filedialog',
    'tkSimpleDialog': 'tkinter.simpledialog',
    'tkColorChooser': 'tkinter.colorchooser',
    'tkFont': 'tkinter.font',
    'Tkdnd': 'tkinter.dnd',
    'ScrolledText': 'tkinter.scrolledtext'
}

def fix_tk_imports(directory):
    for d, _, fs in os.walk(directory):
        for f in fs:
            if not f.endswith('.py'): continue
            fp = os.path.join(d, f)
            with open(fp, 'r', encoding='utf-8') as file:
                content = file.read()
            
            new_content = content
            for py2, py3 in tk_modules.items():
                # Replace exact imports: import tkinter.messagebox as tkMessageBox 
                new_content = re.sub(r'\bimport\s+' + py2 + r'\b', f'import {py3} as {py2}', new_content)
                # Replace comma imports ending with tkMessageBox: import something
import tkinter.messagebox as tkMessageBox
                new_content = re.sub(r'(\bimport\b\s+[^,\n]+(?:,\s*[^,\n]+)*),\s*' + py2 + r'\b', r'\1\nimport ' + py3 + ' as ' + py2, new_content)
                # Replace comma imports starting with tkMessageBox: import tkinter.messagebox as tkMessageBox, something
                new_content = re.sub(r'\bimport\s+' + py2 + r'\s*,\s*([^,\n]+)', r'import ' + py3 + r' as ' + py2 + r'\nimport \1', new_content)
            
            if new_content != content:
                with open(fp, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"Fixed {fp}")

fix_tk_imports(r'f:\BKChem\BKChem3')

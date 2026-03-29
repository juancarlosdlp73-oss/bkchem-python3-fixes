#!/usr/bin/env python3
"""Fix remaining syntax errors after initial automated conversion."""
import os
import re
import sys

root = os.path.dirname(os.path.abspath(__file__))


def fix_file(relpath, fixfunc):
    fp = os.path.join(root, relpath)
    try:
        with open(fp, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        content = fixfunc(content)
        with open(fp, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        print(f'  Fixed: {relpath}')
    except Exception as e:
        print(f'  ERROR fixing {relpath}: {e}')


def fix_geometry(content):
    """Fix tuple unpacking in function parameters - Py2 only feature."""
    # def func( (x1,y1,x2,y2)): → def func(coords): x1,y1,x2,y2 = coords
    # Find all such patterns
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]
        # Match def funcname( (var1, var2, ...)):
        m = re.match(r'^(def\s+\w+\s*\(\s*)\(([^)]+)\)(\s*\)\s*:\s*)$', stripped)
        if m:
            params = m.group(2).strip()
            new_lines.append(indent + m.group(1) + '_args_' + m.group(3))
            # Add unpacking line with extra indent
            body_indent = indent + '  '
            new_lines.append(body_indent + params + ' = _args_')
        else:
            new_lines.append(line)
        i += 1
    return '\n'.join(new_lines)


def fix_structure_database(content):
    """Fix double-comma print."""
    content = content.replace(
        'print("Ignoring line:", line,, file=sys.stderr)',
        'print("Ignoring line:", line, file=sys.stderr)'
    )
    return content


def fix_subsearch(content):
    """Fix multiline print >> out statements."""
    # The original code had print >> out, '''...''' which became broken
    # Let's find and fix the broken patterns
    # Pattern: print("""..., file=out) -> print("""...""", file=out)
    # We need to look at the actual content
    lines = content.split('\n')
    new_lines = []
    in_broken_print = False
    print_lines = []
    print_indent = ''

    for line in lines:
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]

        if in_broken_print:
            print_lines.append(line)
            # Check if this line closes the triple-quote
            if '"""' in stripped or "'''" in stripped:
                # End of the broken print block
                # Reconstruct: print("""...""", file=out)
                all_text = '\n'.join(print_lines)
                # Remove the broken ", file=out)" from the first line
                all_text = all_text.replace(', file=out)', '')
                # Add proper closing
                new_lines.append(all_text + ', file=out)')
                in_broken_print = False
                print_lines = []
            continue

        # Detect broken print with triple-quoted string
        if re.match(r'print\(""".*[^"]{3}.*$', stripped) and ', file=out)' in stripped and '"""' not in stripped[10:]:
            # The print started a triple-quoted string but the converter added , file=out) in the middle
            in_broken_print = True
            print_indent = indent
            print_lines = [line]
            continue

        new_lines.append(line)

    if in_broken_print:
        new_lines.extend(print_lines)

    content = '\n'.join(new_lines)

    # Simpler approach: find all print(..., file=out) where the string isn't closed
    # Actually let's just look at the specific broken patterns in subsearch.py
    # The original has: print >> out, """..."""
    # Which became: print("""..., file=out)
    # We need: print("""...""", file=out)

    # Let me do a targeted fix for what's in this file
    content = content.replace(
        'print("""#--------------------------------------------------------------------------, file=out)',
        'print("""#--------------------------------------------------------------------------""", file=out)'
    )

    return content


def fix_cml2(content):
    """Fix raise with dotted name."""
    content = content.replace(
        'raise plugin.import_exception, "unknown bond type %s" % self.order',
        'raise plugin.import_exception("unknown bond type %s" % self.order)'
    )
    return content


def fix_plugins_init(content):
    """Fix exec statement for dynamic imports."""
    # Original: exec 'import %s' % _name
    # Need to use importlib
    content = content.replace(
        "exec 'import %s' % _name",
        "import importlib; _mod = importlib.import_module('.' + _name, package=__name__)"
    )
    # Also fix the variable reference after the exec
    # The original code did: exec 'import X' then used X in the namespace
    # We need to add it to the local namespace
    content = content.replace(
        "import importlib; _mod = importlib.import_module('.' + _name, package=__name__)",
        "import importlib; _mod = importlib.import_module('.' + _name, package=__name__); globals()[_name] = _mod"
    )
    return content


def fix_pdfgen(content):
    """Fix <> operator."""
    content = content.replace(' <> ', ' != ')
    return content


def fix_pdfutils(content):
    """Fix long integer suffix."""
    content = re.sub(r'(\d+)L\b', r'\1', content)
    return content


def fix_piddle_pdf(content):
    """Fix <> operator."""
    content = content.replace(' <> ', ' != ')
    return content


def fix_piddle_ps(content):
    """Fix backtick repr."""
    content = re.sub(r'`([^`]+)`', r'repr(\1)', content)
    return content


def fix_piddle_wx(content):
    """Fix backtick repr."""
    content = re.sub(r'`([^`]+)`', r'repr(\1)', content)
    return content


def fix_piddle_gl(content):
    """Fix inline print statements after if."""
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]
        # if condition: print "string"
        m = re.match(r'^(if\s+.+?:\s*)print\s+(["\'].+)$', stripped)
        if m:
            new_lines.append(indent + m.group(1) + 'print(' + m.group(2).rstrip() + ')')
            continue
        new_lines.append(line)
    return '\n'.join(new_lines)


def fix_unittests(content):
    """Fix raw string issues in unittests.py."""
    # The issue is a raw-ish string with backslashes
    # "O\C(\N)=C/C=C\C=C\Cl" is a SMILES string, not a Python escape
    # But without r prefix, \C and \N are interpreted as escapes in Py3
    # In Py2 unknown escapes were kept as-is, in Py3 they'll produce DeprecationWarning
    # Let's add r prefix to SMILES strings
    content = content.replace(
        '"O\\C(\\N)=C/C=C\\C=C\\Cl"',
        'r"O\\C(\\N)=C/C=C\\C=C\\Cl"'
    )
    # Fix other SMILES patterns with backslashes
    # Actually let's just make all the test SMILES raw strings
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        # Fix strings containing backslash-letter patterns that are SMILES
        if '\\C' in line or '\\N' in line or '\\O' in line or '\\S' in line:
            if '"' in line and not line.strip().startswith('#'):
                # Add r prefix to the string
                line = re.sub(r'(?<!r)"([^"]*\\[CNOS][^"]*)"', r'r"\1"', line)
        new_lines.append(line)
    return '\n'.join(new_lines)


def fix_piddleFIG(content):
    """Fix backtick repr in piddleFIG.py."""
    content = re.sub(r'`([^`]+)`', r'repr(\1)', content)
    return content


def fix_stringformat(content):
    """Fix string continuation issues in stringformat.py."""
    # The issue is a backslash continuation inside a print call
    # print('...', \)  is invalid -> print('...',
    content = content.replace('\\)', ')')
    return content


# ============================================================
# Apply all fixes
# ============================================================

print("Applying targeted fixes...")

fix_file(os.path.join('bkchem', 'oasa', 'oasa', 'geometry.py'), fix_geometry)
fix_file(os.path.join('bkchem', 'oasa', 'oasa', 'structure_database.py'), fix_structure_database)
fix_file(os.path.join('bkchem', 'oasa', 'oasa', 'subsearch.py'), fix_subsearch)
fix_file(os.path.join('bkchem', 'oasa', 'oasa', 'unittests.py'), fix_unittests)
fix_file(os.path.join('bkchem', 'plugins', 'CML2.py'), fix_cml2)
fix_file(os.path.join('bkchem', 'plugins', '__init__.py'), fix_plugins_init)
fix_file(os.path.join('bkchem', 'plugins', 'piddle', 'pdfgen.py'), fix_pdfgen)
fix_file(os.path.join('bkchem', 'plugins', 'piddle', 'pdfutils.py'), fix_pdfutils)
fix_file(os.path.join('bkchem', 'plugins', 'piddle', 'piddlePDF.py'), fix_piddle_pdf)
fix_file(os.path.join('bkchem', 'plugins', 'piddle', 'piddlePS.py'), fix_piddle_ps)
fix_file(os.path.join('bkchem', 'plugins', 'piddle', 'piddleWX.py'), fix_piddle_wx)
fix_file(os.path.join('bkchem', 'plugins', 'piddle', 'piddleWxDc.py'), fix_piddle_wx)
fix_file(os.path.join('bkchem', 'plugins', 'piddle', 'piddleGL.py'), fix_piddle_gl)
fix_file(os.path.join('bkchem', 'plugins', 'piddle', 'piddleFIG.py'), fix_piddleFIG)
fix_file(os.path.join('bkchem', 'plugins', 'piddle', 'stringformat.py'), fix_stringformat)

print("\nAll targeted fixes applied.")

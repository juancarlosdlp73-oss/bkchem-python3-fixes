#!/usr/bin/env python3
"""Fix all remaining issues in Pmw.py and piddle files."""
import os
import re

root = os.path.dirname(os.path.abspath(__file__))


def fix_pmw():
    fp = os.path.join(root, 'bkchem', 'Pmw.py')
    with open(fp, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # 1. Fix string.find lambdas -> direct .find() calls
    content = content.replace(
        '(lambda s,sub: s.find(sub))',
        ''  # Remove the lambda wrapper
    )
    # The above leaves us with (var, '_') which we need to fix to var.find('_')
    # Actually let's do it differently - undo and do properly
    content = content.replace('(lambda s,sub: s.find(sub))', '__FIND__')
    # Now fix __FIND__(x, y) -> x.find(y)
    content = re.sub(r"__FIND__\((\w+),\s*'([^']*)'\)", r"\1.find('\2')", content)
    content = re.sub(r'__FIND__\((\w+),\s*"([^"]*)"\)', r'\1.find("\2")', content)
    content = re.sub(r'__FIND__\((\w+),\s*(\w+)\)', r'\1.find(\2)', content)

    # 2. Fix all broken raise patterns with backslash continuations
    # Pattern: raise ExcType('msg' \) continuation  or  raise ExcType('msg') % stuff
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]

        # raise SomeError('...') % \
        m = re.match(r"^raise\s+(\w+)\('(.*)'\)\s*%\s*\\$", stripped)
        if m and i + 1 < len(lines):
            next_line = lines[i+1].strip()
            new_lines.append(indent + "raise " + m.group(1) + "('" + m.group(2) + "' % " + next_line + ")")
            i += 2
            continue

        # raise SomeError('...' + ... \) continuation
        m = re.match(r"^raise\s+(\w+)\((.+)\\\)$", stripped)
        if m and i + 1 < len(lines):
            next_line = lines[i+1].strip()
            arg = m.group(1)
            rest = m.group(2)
            new_lines.append(indent + "raise " + arg + "(" + rest + next_line + ")")
            i += 2
            continue

        # raise SomeError('...' \  (backslash at end)
        m = re.match(r"^raise\s+(\w+)\((.+)\\\s*$", stripped)
        if m and i + 1 < len(lines):
            next_line = lines[i+1].strip()
            new_lines.append(indent + "raise " + m.group(1) + "(" + m.group(2) + next_line + ")")
            i += 2
            continue

        # raise ValueError('... ') \ + 'msg'  (broken line continuation pattern)
        m = re.match(r"^raise\s+(\w+)\('(.+)'\s*\)\s*\\\s*$", stripped)
        if m and i + 1 < len(lines):
            next_line = lines[i+1].strip()
            new_lines.append(indent + "raise " + m.group(1) + "('" + m.group(2) + "' + " + next_line + ")")
            i += 2
            continue

        # Fix the specific broken pattern:
        # raise KeyError('Cannot configure...' \ + option) + '...'
        if "raise KeyError('Cannot configure initialisation option" in stripped:
            new_lines.append(indent + "raise KeyError('Cannot configure initialisation option \"' + option + '\" for ' + self.__class__.__name__)")
            i += 1
            continue

        new_lines.append(line)
        i += 1

    content = '\n'.join(new_lines)

    # 3. Fix remaining has_key references that weren't lambda-ified properly
    # has_key = lambda k: k in dict  (already done for _has_key variables)

    # 4. Fix names = x.keys(); names.sort() -> names = sorted(x.keys())
    # This is a two-line pattern, handle it
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]

        # Check for pattern: names = xxx.keys()  followed by names.sort()
        m = re.match(r'^(\w+)\s*=\s*(.+)\.keys\(\)\s*$', stripped)
        if m and i + 1 < len(lines):
            next_stripped = lines[i+1].lstrip()
            var = m.group(1)
            if next_stripped == var + '.sort()':
                new_lines.append(indent + var + ' = sorted(' + m.group(2) + '.keys())')
                i += 2  # skip the .sort() line
                continue

        new_lines.append(line)
        i += 1

    content = '\n'.join(new_lines)

    # 5. Fix remaining string.xxx usages
    content = content.replace("string.upper(option[0])", "option[0].upper()")
    content = content.replace("string.upper(name[0])", "name[0].upper()")
    content = content.replace("string.atol(", "int(")
    content = content.replace("string.atoi(", "int(")
    content = content.replace("string.atof(", "float(")
    content = re.sub(r"string\.lower\((\w+)\)", r"\1.lower()", content)
    content = re.sub(r"string\.split\((\w+)\)", r"\1.split()", content)
    content = re.sub(r"string\.split\((\w+),\s*'([^']*)'\)", r"\1.split('\2')", content)
    content = re.sub(r'string\.split\((\w+),\s*"([^"]*)"\)', r'\1.split("\2")', content)
    content = re.sub(r"string\.strip\((\w+)\)", r"\1.strip()", content)
    content = re.sub(r"string\.replace\((\w+),\s*'([^']*)'\s*,\s*'([^']*)'\)", r"\1.replace('\2', '\3')", content)

    # Write back
    with open(fp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('  Fixed: Pmw.py')


def fix_aigen():
    """Fix aigen.py - the def printAI error suggests there's a syntax issue before it."""
    fp = os.path.join(root, 'bkchem', 'plugins', 'piddle', 'aigen.py')
    with open(fp, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Look for the issue around line 496 - usually a missing closing bracket/paren before it
    lines = content.split('\n')
    # Find line 496 context
    for i in range(max(0, 490), min(len(lines), 500)):
        print(f"    L{i+1}: {lines[i]}")

    # Fix backtick repr that might have been missed
    content = re.sub(r'`([^`\n]+)`', r'repr(\1)', content)

    # Check for << or >> operators used as print
    # Fix: print >> file patterns that weren't caught
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]
        # print >> stream, msg
        m = re.match(r'^print\s*>>\s*([\w.]+)\s*,\s*(.+)$', stripped)
        if m:
            new_lines.append(indent + 'print(' + m.group(2).rstrip() + ', file=' + m.group(1) + ')')
            continue
        new_lines.append(line)
    content = '\n'.join(new_lines)

    with open(fp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('  Fixed: aigen.py')


def fix_pdfgen():
    """Fix pdfgen.py indentation issues."""
    fp = os.path.join(root, 'bkchem', 'plugins', 'piddle', 'pdfgen.py')
    with open(fp, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Find the issue around line 709-710
    lines = content.split('\n')
    for i in range(max(0, 705), min(len(lines), 715)):
        print(f"    L{i+1}: {lines[i][:80]}")

    # Fix empty if block
    # if condition:  (next line has wrong indent or empty)
    new_lines = []
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]
        if stripped.endswith(':') and (stripped.startswith('if ') or stripped.startswith('elif ')):
            # Check if next line is at same or lesser indentation
            if i + 1 < len(lines):
                next_stripped = lines[i+1].lstrip()
                next_indent = lines[i+1][:len(lines[i+1]) - len(next_stripped)]
                if len(next_indent) <= len(indent) and next_stripped and not next_stripped.startswith('#'):
                    # Missing body - add pass
                    new_lines.append(line)
                    new_lines.append(indent + '    pass')
                    continue
        new_lines.append(line)
    content = '\n'.join(new_lines)

    with open(fp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('  Fixed: pdfgen.py')


def fix_stringformat():
    """Fix stringformat.py indentation."""
    fp = os.path.join(root, 'bkchem', 'plugins', 'piddle', 'stringformat.py')
    with open(fp, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Show the problem area
    lines = content.split('\n')
    for i in range(max(0, 494), min(len(lines), 505)):
        print(f"    L{i+1}: |{lines[i]}|")

    with open(fp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('  Examined: stringformat.py')


print("Applying round 4 fixes...")
fix_pmw()
fix_aigen()
fix_pdfgen()
fix_stringformat()
print("\nRound 4 fixes complete.")

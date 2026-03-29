#!/usr/bin/env python3
"""Fix round 2 of remaining syntax errors."""
import os
import re

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


def fix_pmw_exec(content):
    """Fix 'exec execString in d' -> exec(execString, d)"""
    content = re.sub(r'exec\s+(\w+)\s+in\s+(\w+)', r'exec(\1, \2)', content)
    return content


def fix_subsearch2(content):
    """Fix print with embedded comment."""
    content = content.replace(
        'print(l*" ", x #, x.children)',
        'print(l*" ", x)  #, x.children'
    )
    return content


def fix_all_diamond_ne(content):
    """Fix all <> to != globally."""
    content = content.replace('<>', '!=')
    return content


def fix_all_inline_print(content):
    """Fix inline print statements (if cond: print expr)."""
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]
        # if condition: print "string"
        m = re.match(r'^((?:if|elif)\s+.+?:\s*)print\s+(.+)$', stripped)
        if m and not m.group(2).startswith('('):
            new_lines.append(indent + m.group(1) + 'print(' + m.group(2).rstrip() + ')')
            continue
        # def funcname(): print "string"
        m = re.match(r'^(def\s+\w+\s*\([^)]*\)\s*:\s*)print\s+(.+)$', stripped)
        if m and not m.group(2).startswith('('):
            new_lines.append(indent + m.group(1) + 'print(' + m.group(2).rstrip() + ')')
            continue
        new_lines.append(line)
    return '\n'.join(new_lines)


def fix_tab_spaces(content):
    """Convert all tabs to spaces."""
    return content.expandtabs(4)


def fix_aigen(content):
    """Fix aigen.py - tabs inside class definition causing indent error."""
    return content.expandtabs(8)


def fix_stringformat(content):
    """Fix stringformat.py indentation issue."""
    content = content.expandtabs(4)
    return content


print("Applying round 2 fixes...")

# Pmw.py exec statement
fix_file(os.path.join('bkchem', 'Pmw.py'), fix_pmw_exec)

# subsearch.py print with comment
fix_file(os.path.join('bkchem', 'oasa', 'oasa', 'subsearch.py'), fix_subsearch2)

# Fix <> in ALL piddle files
piddle_dir = os.path.join('bkchem', 'plugins', 'piddle')
for fn in os.listdir(os.path.join(root, piddle_dir)):
    if fn.endswith('.py'):
        fix_file(os.path.join(piddle_dir, fn), fix_all_diamond_ne)

# Fix inline print in all piddle files
for fn in os.listdir(os.path.join(root, piddle_dir)):
    if fn.endswith('.py'):
        fix_file(os.path.join(piddle_dir, fn), fix_all_inline_print)

# Fix tabs in remaining piddle files
for fn in ['pdfgen.py', 'aigen.py']:
    fix_file(os.path.join(piddle_dir, fn), fix_tab_spaces)

# stringformat.py indent fix
fix_file(os.path.join(piddle_dir, 'stringformat.py'), fix_stringformat)

print("\nRound 2 fixes complete.")

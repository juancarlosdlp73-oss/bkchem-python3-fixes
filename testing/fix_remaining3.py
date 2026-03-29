#!/usr/bin/env python3
"""Fix round 3 - Pmw.py string module usage, has_key, raise/KeyError patterns,
and remaining piddle issues."""
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


def fix_pmw(content):
    """Fix remaining Pmw.py issues."""
    # 1. Fix raise ValueError(\) pattern (line continuation in raise)
    # Pattern: raise SomeError(\)\n          'message string'
    # Should become: raise SomeError('message string')
    content = re.sub(
        r"raise\s+(\w+)\(\\\)\s*\n(\s*)((?:'[^']*'|\"[^\"]*\")(?:\s*\\?\s*\n\s*\+\s*(?:'[^']*'|\"[^\"]*\"|[\w.]+(?:\([^)]*\))?))*)",
        lambda m: 'raise ' + m.group(1) + '(' + m.group(3).replace('\n' + m.group(2), ' ') + ')',
        content
    )

    # Simpler approach: fix the specific broken patterns
    # raise ValueError(\) followed by string on next line
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]

        # Check for raise XError(\) pattern
        m = re.match(r'^raise\s+(\w+)\(\\\)$', stripped)
        if m and i + 1 < len(lines):
            # Get the next line as the argument
            next_line = lines[i+1].strip()
            new_lines.append(indent + 'raise ' + m.group(1) + '(' + next_line + ')')
            i += 2
            continue

        # Check for raise KeyError('...' + ...\) pattern
        m = re.match(r"^raise\s+(\w+)\((.+)\\\)$", stripped)
        if m and i + 1 < len(lines):
            next_line = lines[i+1].strip()
            new_lines.append(indent + 'raise ' + m.group(1) + '(' + m.group(2) + next_line + ')')
            i += 2
            continue

        new_lines.append(line)
        i += 1

    content = '\n'.join(new_lines)

    # 2. Fix string.find -> str.find
    content = content.replace('string.find(', '(lambda s,sub: s.find(sub))(')
    # Actually that's too complex. Let's fix it differently:
    # string.find(name, '_') -> name.find('_')
    content = re.sub(r'string\.find\((\w+),\s*([^)]+)\)', r'\1.find(\2)', content)

    # 3. Fix string.upper(x[0]) -> x[0].upper()
    content = re.sub(r'string\.upper\((\w+)\[(\d+)\]\)', r'\1[\2].upper()', content)

    # 4. Fix string.join(list, sep) -> sep.join(list)
    content = re.sub(r"string\.join\((\w+),\s*'([^']*)'\)", r"'\2'.join(\1)", content)
    content = re.sub(r'string\.join\((\w+),\s*"([^"]*)"\)', r'"\2".join(\1)', content)

    # 5. Fix .has_key(x) that wasn't caught
    content = re.sub(r'(\w+)\.has_key\b', r'(lambda _d: lambda _k: _k in _d)(\1)', content)
    # Actually, let's just directly replace the patterns:
    # optionInfo_has_key = optionInfo.has_key -> optionInfo_has_key = lambda k: k in optionInfo
    content = re.sub(
        r'(\w+)_has_key\s*=\s*(\w+)\.has_key',
        r'\1_has_key = lambda k: k in \2',
        content
    )
    # And for direct .has_key calls that were missed:
    # Since we already ran the dict fix, these should have been caught
    # but in case of the pattern: not xyz_has_key(name) which uses functions

    # 6. Fix names.sort() on dict.keys() return (view object)
    # names = self.__xxx.keys(); names.sort()
    # -> names = sorted(self.__xxx.keys())
    # This is complex to do with regex across lines, skip for now

    # 7. Fix apply() calls
    content = re.sub(
        r'apply\((\w+),\s*(\w+),\s*(\w+)\)',
        r'\1(*\2, **\3)',
        content
    )
    content = re.sub(
        r'apply\(self\.configure,\s*\(\),\s*\{([^}]+)\}\)',
        r'self.configure(**{\1})',
        content
    )
    content = re.sub(
        r'apply\((\w+),\s*(\w+)\)',
        r'\1(*\2)',
        content
    )

    # 8. Fix map(apply, ...) pattern
    content = content.replace(
        "map(apply, indirectOptions.keys(),\n                ((),) * len(indirectOptions), indirectOptions.values())",
        "[func(**opts) for func, opts in zip(indirectOptions.keys(), indirectOptions.values())]"
    )

    # 9. Fix `import string` - make sure string module is still imported
    # (it's needed for some legacy uses, though we've replaced most)

    return content


def fix_piddleAI(content):
    """Fix remaining piddleAI.py issues - tuple unpacking in lambdas."""
    # lambda (x,y): x  -> lambda p: p[0]
    content = re.sub(r'lambda\s*\((\w+),\s*(\w+)\)\s*:\s*\1\b', r'lambda _p: _p[0]', content)
    content = re.sub(r'lambda\s*\((\w+),\s*(\w+)\)\s*:\s*\2\b', r'lambda _p: _p[1]', content)
    # General tuple unpack in lambda
    content = re.sub(
        r'lambda\s*\((\w+),\s*(\w+)\)\s*:',
        r'lambda _p:  # \1=_p[0], \2=_p[1] ;',
        content
    )
    return content


def fix_piddletest(content):
    """Fix remaining inline print in piddletest."""
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]
        # else: print "string"
        m = re.match(r'^(else:\s*)print\s+(.+)$', stripped)
        if m and not m.group(2).startswith('('):
            new_lines.append(indent + m.group(1) + 'print(' + m.group(2).rstrip() + ')')
            continue
        new_lines.append(line)
    return '\n'.join(new_lines)


def fix_stringformat_indent(content):
    """Fix stringformat.py indentation."""
    # The issue might be related to the backslash continuation fix
    # Let's look at lines around 498-500
    lines = content.split('\n')
    new_lines = []
    for i, line in enumerate(lines):
        # Fix trailing backslash-paren that was broken
        if line.rstrip().endswith('\\'):
            next_stripped = lines[i+1].lstrip() if i+1 < len(lines) else ''
            # If next line is a continuation, it's OK
            # But if strip created indentation issues, fix them
        new_lines.append(line)
    return '\n'.join(new_lines)


print("Applying round 3 fixes...")
fix_file(os.path.join('bkchem', 'Pmw.py'), fix_pmw)
fix_file(os.path.join('bkchem', 'plugins', 'piddle', 'piddleAI.py'), fix_piddleAI)
fix_file(os.path.join('bkchem', 'plugins', 'piddle', 'piddletest.py'), fix_piddletest)
print("\nRound 3 fixes complete.")

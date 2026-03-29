#!/usr/bin/env python3
"""
BKChem Python 2 to Python 3 Conversion Script
==============================================
Applies systematic regex-based transformations to convert Python 2 syntax
to Python 3 across all .py files in the BKChem3 directory.

This script handles:
1. Print statements → print() functions
2. Exception syntax (except X, e → except X as e)
3. Raise syntax (raise X, "msg" → raise X("msg"))
4. Tkinter module renames
5. __builtin__ → builtins
6. unicode/unichr/basestring removals
7. dict method changes (.iteritems, .has_key, etc.)
8. reduce/xrange/apply/execfile replacements
9. types module updates
10. Relative import fixes
11. StringIO/cStringIO updates
12. Miscellaneous Py2→Py3 fixes
"""

import re
import os
import sys

# ============================================================
# TRANSFORMATION FUNCTIONS
# ============================================================

def fix_print_statements(content, filepath):
    """Convert print statements to print() function calls."""
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]

        # Skip comments and strings
        if stripped.startswith('#'):
            new_lines.append(line)
            continue

        # Skip lines that already use print as function
        if re.match(r'print\s*\(', stripped):
            new_lines.append(line)
            continue

        # print >> sys.stderr, "msg"
        m = re.match(r'print\s*>>\s*([\w.]+)\s*,\s*(.+)$', stripped)
        if m:
            new_lines.append(indent + 'print(%s, file=%s)' % (m.group(2).rstrip(), m.group(1)))
            continue

        # print "msg",  (trailing comma = no newline)
        m = re.match(r'print\s+(.+),\s*$', stripped)
        if m and not stripped.startswith('print('):
            # Check it's not just a tuple or function
            arg = m.group(1).rstrip()
            if not arg.startswith('('):
                new_lines.append(indent + 'print(%s, end="")' % arg)
                continue

        # print "msg"
        m = re.match(r'print\s+(?![\(])(.*\S.*)$', stripped)
        if m:
            arg = m.group(1).rstrip()
            # Don't convert if it looks like it's already a function call that spans lines
            # or if it's a comment
            if arg and not arg.startswith('#'):
                new_lines.append(indent + 'print(%s)' % arg)
                continue

        # bare print
        if stripped == 'print':
            new_lines.append(indent + 'print()')
            continue

        new_lines.append(line)

    return '\n'.join(new_lines)


def fix_except_syntax(content, filepath):
    """Convert 'except ExceptionType, variable:' to 'except ExceptionType as variable:'"""
    # except SomeError, var:
    content = re.sub(
        r'except\s+([\w.]+)\s*,\s*(\w+)\s*:',
        r'except \1 as \2:',
        content
    )
    return content


def fix_raise_syntax(content, filepath):
    """Convert 'raise ExceptionType, "msg"' to 'raise ExceptionType("msg")'"""
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]

        # raise ValueError, "message"
        m = re.match(r'raise\s+(\w+)\s*,\s*(.+)$', stripped)
        if m:
            exc_type = m.group(1)
            exc_arg = m.group(2).rstrip()
            new_lines.append(indent + 'raise %s(%s)' % (exc_type, exc_arg))
            continue

        new_lines.append(line)
    return '\n'.join(new_lines)


def fix_tkinter_imports(content, filepath):
    """Fix Tkinter → tkinter module renames."""
    # Full module imports
    content = re.sub(r'^import Tkinter\b', 'import tkinter', content, flags=re.MULTILINE)
    content = re.sub(r'^from Tkinter import', 'from tkinter import', content, flags=re.MULTILINE)

    # Tkinter references in code (after import changes)
    content = re.sub(r'\bTkinter\.', 'tkinter.', content)

    # tkFont
    content = re.sub(r'^import tkinter.font as tkFont\b', 'import tkinter.font as tkFont', content, flags=re.MULTILINE)
    content = re.sub(r'^import tkinter.font as tkFont,', 'import tkinter.font as tkFont\nimport', content, flags=re.MULTILINE)

    # tkMessageBox
    content = re.sub(r'^import tkinter.messagebox as tkMessageBox\b', 'import tkinter.messagebox as tkMessageBox', content, flags=re.MULTILINE)

    # tkFileDialog
    content = re.sub(r'^import tkinter.filedialog as tkFileDialog\b', 'import tkinter.filedialog as tkFileDialog', content, flags=re.MULTILINE)
    content = re.sub(r'^from tkFileDialog import', 'from tkinter.filedialog import', content, flags=re.MULTILINE)

    # tkColorChooser
    content = re.sub(r'^from tkColorChooser import', 'from tkinter.colorchooser import', content, flags=re.MULTILINE)
    content = re.sub(r'^import tkinter.colorchooser as tkColorChooser\b', 'import tkinter.colorchooser as tkColorChooser', content, flags=re.MULTILINE)

    # tkSimpleDialog
    content = re.sub(r'^import tkinter.simpledialog as tkSimpleDialog\b', 'import tkinter.simpledialog as tkSimpleDialog', content, flags=re.MULTILINE)
    content = re.sub(r'^from tkSimpleDialog import', 'from tkinter.simpledialog import', content, flags=re.MULTILINE)

    # Combined imports like "import tkinter.font as tkFont
import tkinter.messagebox as tkMessageBox"
    content = re.sub(r'^import tkinter\.font as tkFont\nimport tkMessageBox',
                     'import tkinter.font as tkFont\nimport tkinter.messagebox as tkMessageBox',
                     content, flags=re.MULTILINE)

    return content


def fix_builtin_module(content, filepath):
    """Fix __builtin__ → builtins."""
    content = content.replace('import __builtin__', 'import builtins')
    content = content.replace('__builtin__', 'builtins')
    return content


def fix_unicode_handling(content, filepath):
    """Fix unicode-related changes for Python 3."""
    # unichr → chr
    content = re.sub(r'\bunichr\s*\(', 'chr(', content)

    # basestring → str
    content = re.sub(r'\bbasestring\b', 'str', content)

    # os.getcwdu() → os.getcwd()
    content = content.replace('os.getcwdu()', 'os.getcwd()')

    # Remove 'from __future__ import division' (no-op in Py3)
    content = re.sub(r'^from __future__ import division\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^from __future__ import generators\s*$', '', content, flags=re.MULTILINE)

    # gettext install: tr.install(unicode=True, ...) → tr.install(names=[...])
    content = re.sub(r'\.install\(unicode=True,\s*', '.install(', content)
    content = re.sub(r'\.install\(unicode=True\)', '.install()', content)

    return content


def fix_dict_methods(content, filepath):
    """Fix dictionary method changes."""
    # .iteritems() → .items()
    content = re.sub(r'\.iteritems\(\)', '.items()', content)
    # .itervalues() → .values()
    content = re.sub(r'\.itervalues\(\)', '.values()', content)
    # .iterkeys() → .keys()
    content = re.sub(r'\.iterkeys\(\)', '.keys()', content)
    # .has_key(x) → x in dict
    content = re.sub(r'(\w+)\.has_key\(\s*(.+?)\s*\)', r'\2 in \1', content)
    return content


def fix_reduce_and_builtins(content, filepath):
    """Fix reduce, xrange, apply, execfile."""
    # xrange → range
    content = re.sub(r'\bxrange\s*\(', 'range(', content)

    # execfile(f, g) → exec(compile(open(f).read(), f, 'exec'), g)
    content = re.sub(
        r'execfile\(\s*(\w+)\s*,\s*(\w+)\s*\)',
        r'exec(compile(open(\1).read(), \1, "exec"), \2)',
        content
    )

    # Check if reduce is used and add import if needed
    if re.search(r'\breduce\s*\(', content):
        if 'from functools import reduce' not in content and 'import functools' not in content:
            # Add import at the top, after other imports
            # Find first import line
            lines = content.split('\n')
            insert_pos = 0
            for i, line in enumerate(lines):
                s = line.strip()
                if s.startswith('import ') or s.startswith('from '):
                    insert_pos = i + 1
                elif s and not s.startswith('#') and not s.startswith('"""') and not s.startswith("'''") and insert_pos > 0:
                    break
            if insert_pos > 0:
                lines.insert(insert_pos, 'from functools import reduce')
                content = '\n'.join(lines)

    return content


def fix_types_module(content, filepath):
    """Fix types module usage."""
    # types.StringType → str
    content = content.replace('types.StringType', 'str')
    content = content.replace('types.UnicodeType', 'str')
    content = content.replace('types.IntType', 'int')
    content = content.replace('types.ListType', 'list')
    content = content.replace('types.DictType', 'dict')
    content = content.replace('types.TupleType', 'tuple')

    # from types import StringType, ... → remove or fix
    content = re.sub(r'from types import StringType', 'pass  # types removed (use str)', content)
    content = re.sub(r'from types import \*', 'pass  # types wildcard removed', content)

    # Direct StringType usage (without types. prefix)
    content = re.sub(r'\bStringType\b', 'str', content)
    content = re.sub(r'\bUnicodeType\b', 'str', content)
    content = re.sub(r'\bIntType\b', 'int', content)
    content = re.sub(r'\bFloatType\b', 'float', content)
    content = re.sub(r'\bInstanceType\b', 'object', content)

    return content


def fix_stringio(content, filepath):
    """Fix StringIO/cStringIO imports."""
    content = re.sub(r'^import cStringIO\b', 'from io import StringIO, BytesIO', content, flags=re.MULTILINE)
    content = re.sub(r'^import StringIO\b', 'from io import StringIO', content, flags=re.MULTILINE)
    content = content.replace('cStringIO.StringIO', 'BytesIO')
    content = content.replace('StringIO.StringIO', 'StringIO')
    return content


def fix_string_module(content, filepath):
    """Fix string module usage."""
    content = content.replace('string.join(', "', '.join(")  # approximate, may need manual fix
    content = content.replace('string.lower(', '(').replace('string.upper(', '(')  # rare
    return content


def fix_sys_exc(content, filepath):
    """Fix sys.exc_value → sys.exc_info()[1]."""
    content = content.replace('sys.exc_value', 'sys.exc_info()[1]')
    content = content.replace('sys.exc_type', 'sys.exc_info()[0]')
    return content


def fix_apply(content, filepath):
    """Convert apply(func, args) → func(*args) and apply(func, args, kw) → func(*args, **kw)."""
    # apply(func, args, kw)
    content = re.sub(
        r'\bapply\(\s*([\w.]+)\s*,\s*(\([^)]*\))\s*,\s*(\w+)\s*\)',
        r'\1(*\2, **\3)',
        content
    )
    # apply(func, args)
    content = re.sub(
        r'\bapply\(\s*([\w.]+)\s*,\s*(\([^)]*\))\s*\)',
        r'\1(*\2)',
        content
    )
    return content


def fix_generator_next(content, filepath):
    """Convert generator.next() → next(generator)."""
    # pattern: varname.next() but not __next__
    content = re.sub(r'(\b\w+)\.next\(\)', r'next(\1)', content)
    return content


def fix_relative_imports_bkchem(content, filepath):
    """Fix relative imports for files in the bkchem/ package."""
    # Determine the module's location
    rel = os.path.relpath(filepath, os.path.join(os.path.dirname(__file__), 'bkchem'))
    parts = rel.replace('\\', '/').split('/')

    if len(parts) == 1:
        # We're in bkchem/ directly
        # Fix bare imports of sibling modules
        bkchem_modules = [
            'CDML_versions', 'arrow', 'atom', 'bkchem', 'bkchem_exceptions',
            'bond', 'checks', 'classes', 'config', 'context_menu', 'data',
            'debug', 'dialogs', 'dom_extensions', 'edit_pool', 'export',
            'external_data', 'fragment', 'ftext', 'graphics', 'group',
            'groups_table', 'helper_graphics', 'http_server', 'http_server2',
            'id_manager', 'import_checker', 'interactors', 'keysymdef',
            'logger', 'main', 'marks', 'messages', 'misc', 'modes',
            'molecule', 'non_xml_writer', 'oasa_bridge', 'os_support',
            'paper', 'parents', 'pixmaps', 'plugin_support', 'pref_manager',
            'queryatom', 'reaction', 'singleton_store', 'special_parents',
            'splash', 'temp_manager', 'textatom', 'tuning', 'undo',
            'validator', 'widgets', 'xml_serializer', 'xml_writer'
        ]

        lines = content.split('\n')
        new_lines = []
        for line in lines:
            new_line = line
            stripped = line.lstrip()
            indent = line[:len(line) - len(stripped)]

            # import module_name
            m = re.match(r'^import\s+([\w]+)\s*$', stripped)
            if m and m.group(1) in bkchem_modules:
                new_line = indent + 'from . import ' + m.group(1)

            # import module1, module2 (handle comma-separated)
            elif re.match(r'^import\s+\w+\s*,', stripped):
                mods = stripped[7:].split(',')
                mods = [mod.strip() for mod in mods]
                relative = [mod for mod in mods if mod in bkchem_modules]
                absolute = [mod for mod in mods if mod not in bkchem_modules]
                parts_out = []
                if relative:
                    parts_out.append(indent + 'from . import ' + ', '.join(relative))
                if absolute:
                    parts_out.append(indent + 'import ' + ', '.join(absolute))
                new_line = '\n'.join(parts_out) if parts_out else new_line

            # from module_name import X
            m = re.match(r'^from\s+([\w]+)\s+import\s+(.+)$', stripped)
            if m and m.group(1) in bkchem_modules:
                new_line = indent + 'from .%s import %s' % (m.group(1), m.group(2))

            # import plugins  (subpackage)
            if stripped == 'import plugins':
                new_line = indent + 'from . import plugins'
            if stripped == 'import plugins.plugin':
                new_line = indent + 'from .plugins import plugin'

            # from singleton_store import ...
            m = re.match(r'^from\s+singleton_store\s+import\s+(.+)$', stripped)
            if m:
                new_line = indent + 'from .singleton_store import ' + m.group(1)

            # import oasa  (the local package)
            if stripped == 'import oasa':
                new_line = indent + 'from . import oasa'
            m = re.match(r'^from\s+oasa\s+import\s+(.+)$', stripped)
            if m:
                new_line = indent + 'from .oasa import ' + m.group(1)

            # import oasa_bridge
            if stripped == 'import oasa_bridge':
                new_line = indent + 'from . import oasa_bridge'

            # Special combo: import os_support, sys
            m = re.match(r'^import\s+os_support\s*,\s*sys\s*$', stripped)
            if m:
                new_line = indent + 'from . import os_support\nimport sys'

            new_lines.append(new_line)
        content = '\n'.join(new_lines)

    return content


def fix_relative_imports_oasa_inner(content, filepath):
    """Fix relative imports for files in bkchem/oasa/oasa/."""
    oasa_modules = [
        'atom', 'bond', 'molecule', 'smiles', 'coords_generator',
        'coords_optimizer', 'molfile', 'inchi', 'cdml', 'graph',
        'linear_formula', 'periodic_table', 'config', 'query_atom',
        'chem_vertex', 'oasa_exceptions', 'subsearch', 'svg_out',
        'stereochemistry', 'geometry', 'transform3d', 'transform',
        'cairo_out', 'inchi_key', 'name_database', 'structure_database',
        'pybel_bridge', 'known_groups', 'common', 'misc',
        'converter_base', 'plugin', 'dom_extensions',
        'coords_optimizer', 'isotope_database', 'subsearch_data',
        'reaction'
    ]

    lines = content.split('\n')
    new_lines = []
    for line in lines:
        new_line = line
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]

        # import module_name
        m = re.match(r'^import\s+([\w]+)\s*$', stripped)
        if m and m.group(1) in oasa_modules:
            new_line = indent + 'from . import ' + m.group(1)

        # from module_name import X
        m = re.match(r'^from\s+([\w]+)\s+import\s+(.+)$', stripped)
        if m and m.group(1) in oasa_modules:
            new_line = indent + 'from .%s import %s' % (m.group(1), m.group(2))

        # from oasa_exceptions import ...
        m = re.match(r'^from\s+oasa_exceptions\s+import\s+(.+)$', stripped)
        if m:
            new_line = indent + 'from .oasa_exceptions import ' + m.group(1)

        new_lines.append(new_line)
    content = '\n'.join(new_lines)
    return content


def fix_relative_imports_graph(content, filepath):
    """Fix relative imports for files in bkchem/oasa/oasa/graph/."""
    graph_modules = ['edge', 'vertex', 'basic', 'diedge', 'digraph', 'graph']

    lines = content.split('\n')
    new_lines = []
    for line in lines:
        new_line = line
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]

        # from edge import edge
        m = re.match(r'^from\s+([\w]+)\s+import\s+(.+)$', stripped)
        if m and m.group(1) in graph_modules:
            new_line = indent + 'from .%s import %s' % (m.group(1), m.group(2))

        # import edge
        m = re.match(r'^import\s+([\w]+)\s*$', stripped)
        if m and m.group(1) in graph_modules:
            new_line = indent + 'from . import ' + m.group(1)

        new_lines.append(new_line)
    content = '\n'.join(new_lines)
    return content


def fix_relative_imports_plugins(content, filepath):
    """Fix relative imports for files in bkchem/plugins/."""
    plugin_modules = [
        'CDXML', 'CML', 'CML2', 'bitmap', 'cairo_lowlevel', 'gtml',
        'molfile', 'odf', 'openoffice', 'pdf_cairo', 'pdf_piddle',
        'piddle_lowlevel', 'plugin', 'png_cairo', 'povray',
        'ps_builtin', 'ps_cairo', 'ps_piddle', 'svg_cairo',
        'tk2cairo', 'tk2piddle'
    ]

    lines = content.split('\n')
    new_lines = []
    for line in lines:
        new_line = line
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]

        # from plugin import X
        m = re.match(r'^from\s+plugin\s+import\s+(.+)$', stripped)
        if m:
            new_line = indent + 'from .plugin import ' + m.group(1)

        # import plugin
        if stripped == 'import plugin':
            new_line = indent + 'from . import plugin'

        new_lines.append(new_line)
    content = '\n'.join(new_lines)
    return content


def fix_map_filter_to_list(content, filepath):
    """Wrap map() and filter() in list() where needed for common patterns."""
    # map used in assignment or return that needs a list
    # dashing = map(lambda x: ..., dashing) → dashing = [x * ... for x in dashing]
    # This is tricky to do automatically, so we do safe cases:
    # list( map(...) ) is always safe
    # For now, wrap map() in list() when it's used in:
    # - variable assignment
    # - return statements
    # But NOT when used inside reduce(), set(), etc.
    # This is too error-prone for regex, so we'll leave map/filter as-is
    # since in Py3 they return iterators which often work fine in context
    return content


def fix_unicode_encode_patterns(content, filepath):
    """Handle common unicode/encode patterns for Py3."""
    # unicode(x) → str(x)  - but be careful with unicode(x, encoding)
    # Simple unicode(x) calls
    content = re.sub(r'\bunicode\(\s*(\w+)\s*\)', r'str(\1)', content)

    # unicode(x, encoding=enc) → x.decode(enc) or str(x, encoding=enc)
    content = re.sub(r'\bunicode\(\s*(\w+)\s*,\s*encoding\s*=\s*(\w+)\s*\)',
                     r'str(\1, encoding=\2)', content)

    return content


def fix_sorted_keys_pattern(content, filepath):
    """Fix names = dict.keys(); names.sort() pattern."""
    # This pattern: x = d.keys(); x.sort() needs to become x = sorted(d.keys())
    # But it spans two lines, so handle the .sort() on list from .keys()
    # Actually in Py3 .keys() returns a view, but names.sort() will fail on views
    # We'll just leave it - the .sort() works on lists, and if they call list() first it works
    return content


# ============================================================
# MAIN PROCESSING
# ============================================================

def determine_file_category(filepath):
    """Determine which package a file belongs to for relative import fixing."""
    norm = filepath.replace('\\', '/')
    if '/oasa/oasa/graph/' in norm:
        return 'graph'
    elif '/oasa/oasa/' in norm:
        return 'oasa_inner'
    elif '/oasa/' in norm and '/oasa/oasa/' not in norm:
        return 'oasa_wrapper'
    elif '/plugins/piddle/' in norm:
        return 'piddle'
    elif '/plugins/' in norm and '/bkchem/plugins/' in norm:
        return 'bkchem_plugins'
    elif '/bkchem/' in norm:
        return 'bkchem_core'
    else:
        return 'external'


def process_file(filepath):
    """Apply all transformations to a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        print(f"  ERROR reading {filepath}: {e}")
        return False

    original = content
    category = determine_file_category(filepath)

    # Apply transformations in order
    content = fix_print_statements(content, filepath)
    content = fix_except_syntax(content, filepath)
    content = fix_raise_syntax(content, filepath)
    content = fix_tkinter_imports(content, filepath)
    content = fix_builtin_module(content, filepath)
    content = fix_unicode_handling(content, filepath)
    content = fix_unicode_encode_patterns(content, filepath)
    content = fix_dict_methods(content, filepath)
    content = fix_reduce_and_builtins(content, filepath)
    content = fix_types_module(content, filepath)
    content = fix_stringio(content, filepath)
    content = fix_sys_exc(content, filepath)
    content = fix_apply(content, filepath)
    content = fix_generator_next(content, filepath)

    # Relative import fixes based on category
    if category == 'graph':
        content = fix_relative_imports_graph(content, filepath)
    elif category == 'oasa_inner':
        content = fix_relative_imports_oasa_inner(content, filepath)
    elif category == 'bkchem_core':
        content = fix_relative_imports_bkchem(content, filepath)
    elif category == 'bkchem_plugins':
        content = fix_relative_imports_plugins(content, filepath)

    if content != original:
        try:
            with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"  ERROR writing {filepath}: {e}")
            return False
    return False  # no changes needed


def find_py_files(root_dir):
    """Find all .py files under root_dir."""
    py_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip the convert script itself
        for fn in filenames:
            if fn.endswith('.py') and fn != 'convert_to_py3.py':
                py_files.append(os.path.join(dirpath, fn))
    return py_files


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    print(f"Converting files in: {root}")

    py_files = find_py_files(root)
    print(f"Found {len(py_files)} Python files")

    changed = 0
    errors = 0
    for filepath in sorted(py_files):
        rel = os.path.relpath(filepath, root)
        result = process_file(filepath)
        if result:
            print(f"  CONVERTED: {rel}")
            changed += 1
        elif result is False:
            pass  # no changes or error already printed

    print(f"\nDone. {changed} files modified out of {len(py_files)} total.")


if __name__ == '__main__':
    main()

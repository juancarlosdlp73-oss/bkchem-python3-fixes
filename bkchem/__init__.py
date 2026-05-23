#--------------------------------------------------------------------------
#     This file is part of BKChem - a chemical drawing program
#     Copyright (C) 2002-2004 Beda Kosata <beda@zirael.org>
#--------------------------------------------------------------------------

"""this is the bkchem package"""

import os
import sys

# Esto es vital: permite que los sub-módulos se encuentren entre sí
__all__ = ["atom", "bond", "molecule", "paper", "oasa", "data", "config"]

# Si ayer lo borramos, pon esto para asegurar la compatibilidad con Py3:
sys.path.insert(0, os.path.dirname(__file__))

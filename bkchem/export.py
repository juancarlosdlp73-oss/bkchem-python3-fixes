#--------------------------------------------------------------------------
#     This file is part of BKChem - a chemical drawing program
#     Copyright (C) 2002-2009 Beda Kosata <beda@zirael.org>

#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 2 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     Complete text of GNU GPL can be found in the file gpl.txt in the
#     main directory of the program

#--------------------------------------------------------------------------
"""Soporte para exportación de archivos en BKChem - Versión Python 3.12 Actualizada"""

"""Soporte para exportación de archivos en BKChem - Python 3.12"""

import os
from . import xml_writer
from . import dom_extensions

def get_target_directory():
    """Busca la carpeta Imágenes y crea la subcarpeta BKChem"""
    home = os.path.expanduser("~")
    for folder in ['Imágenes', 'Imagenes', 'Pictures', 'Images']:
        path = os.path.join(home, folder)
        if os.path.exists(path):
            target = os.path.join(path, 'BKChem')
            os.makedirs(target, exist_ok=True)
            return target
            
    return home

def export_CD_SVG(paper, filename, gzipped=0):
    try:
        if not filename.endswith('.svg'):
            filename += '.svg'
            
        paper.crop_svg = 1
        paper.crop_margin = 20
        
        exporter = xml_writer.SVG_writer(paper)
        exporter.construct_dom_tree(paper.top_levels)
        
        xml_data = exporter.document.toxml()
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(xml_data)
        print(f"ÉXITO: Archivo guardado en {filename}")
        return 1
    except Exception as e:
        print(f"--- ERROR AL EXPORTAR SVG ---")
        print(f"Causa: {e}")
        import traceback
        traceback.print_exc()
        return 0

def export_CDML(paper, filename, gzipped=0):
    try:
        doc = paper.get_package()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(doc.toxml())
        return 1
    except Exception as e:
        print(f"Error CDML: {e}")
        return 0
#!/usr/bin/env python3
"""
BKChem launcher script
This script sets up the Python path and launches BKChem properly.
"""

import sys
import os

def crear_lanzador_automatico():
    # 1. Detectamos la ruta donde está el proyecto actualmente
    ruta_proyecto = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Definimos la ruta del escritorio (Desktop)
    ruta_escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
    archivo_lanzador = os.path.join(ruta_escritorio, "bkchem.desktop")

    # 3. Solo lo creamos si no existe ya
    if os.path.exists(archivo_lanzador):
        return

    # 4. Contenido con la ruta corregida (sin el 'bkchem' de más en el icono)
    contenido = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=BKChem Pro
Comment=Editor de estructuras quimicas
Exec=python3 {os.path.join(ruta_proyecto, 'start_bkchem.py')}
Icon={os.path.join(ruta_proyecto, 'images', 'bkchem.png')}
Path={ruta_proyecto}
Terminal=false
StartupNotify=true
Categories=Science;Education;Chemistry;
"""

    try:
        with open(archivo_lanzador, "w") as f:
            f.write(contenido)
        # Dar permisos de ejecución (rwxr-xr-x)
        os.chmod(archivo_lanzador, 0o755)
        print(f"✅ Acceso directo creado en: {archivo_lanzador}")
    except Exception as e:
        print(f"⚠️ No se pudo crear el acceso directo: {e}")

# Ejecutar la función al inicio
crear_lanzador_automatico()

# Add the parent directory to Python path so we can import bkchem as a package
parent_dir = os.path.dirname(__file__)
sys.path.insert(0, parent_dir)

print("Starting BKChem...")

# Now we can run bkchem as a module
if __name__ == '__main__':
    print("Importing bkchem.bkchem...")
    import bkchem.bkchem
    print("BKChem imported successfully")
    print("Starting mainloop...")
    
    # Get the application instance and start the mainloop
    from bkchem.singleton_store import Store
    if hasattr(Store, 'app'):
        Store.app.mainloop()
        print("BKChem finished")
    else:
        print("Error: Application not initialized")

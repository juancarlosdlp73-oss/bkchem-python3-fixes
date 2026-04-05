#  BKChem - JuanCarlos Patched Version (Python 3.12)

This repository contains a fixed and adapted version of **BKChem**, specifically repaired to work correctly on modern systems with **Python 3.12** (tested on Lubuntu).

##  Improvements and Fixes Applied:

### 1. SVG Subscript Repair (Chemical Formulas)
* Fixed the critical error where subscripts (like the **3** in $CH_3$) caused invisible or corrupted SVG files.
* Now uses coordinate shifts (`dy`) instead of `baseline-shift`, ensuring perfect rendering in **Firefox, Chrome, and Linux image viewers**.

### 2. UI Icon Path Fix
* **Fixed Asset Loading:** Corrected the broken links between the UI buttons and the icon files. The program now correctly locates and renders the toolbar icons, fixing the "empty button" bug.

### 3. Smart Auto-Crop
* Modified the export engine so molecules automatically fit the drawing size.
* Eliminated the infinite white margins present in the original version.

### 4. Default "Pictures" Directory
* The program now automatically detects the user's `Pictures` or `Imágenes` folder.
* It creates a `BKChem` subfolder by default and opens the "Save As" dialog directly there.

### 5. Python 3.12 Compatibility
* Cleaned up `bytes` to `string` (UTF-8) encoding errors in critical export files that caused the app to crash.

### 6. Text Tool and Subscript Compatibility

* Resolved the NameError: name 'unicode' is not defined by migrating all text handling to Python 3 str in classes.py, enabling the "Text Tool" to work without crashes.

* Forced a fixed 8pt font size and 4px vertical displacement for subscripts and superscripts in xml_writer.py. This prevents the "Giant Subscript" bug in Linux image viewers like Nomacs or GPicView, ensuring formulas like H2​O or CH4​ render accurately.



---

#  BKChem - Versión Corregida por JuanCarlos (Python 3.12)

Este repositorio contiene una versión de **BKChem** adaptada y reparada para funcionar correctamente en sistemas modernos con **Python 3.12** (probado en Lubuntu).

##  Mejoras y Fixes Aplicados:

### 1. Reparación de Subíndices (Fórmulas Químicas)
* Se ha corregido el error crítico que hacía que los subíndices (como el **3** en $CH_3$) corrompieran el archivo SVG o se vieran deformados.
* Ahora utiliza desplazamientos de coordenadas `dy` en lugar de `baseline-shift`, garantizando que se vea bien en **Firefox, Chrome y visores de Linux**.

### 2. Reparación de Rutas de Iconos
* **Carga de Recursos:** Se han corregido los enlaces rotos entre los botones de la interfaz y los archivos de imagen. Ahora el programa localiza correctamente los iconos de la barra de herramientas, solucionando el fallo de los botones vacíos.

### 3. Auto-Crop (Recorte Automático)
* Se modificó el motor de exportación para que las moléculas se ajusten al tamaño real del dibujo.
* Se eliminaron los márgenes blancos infinitos de la versión original.

### 4. Guardado Inteligente en Imágenes
* El programa ahora detecta automáticamente la carpeta `Imágenes` (o `Pictures`) del usuario.
* Crea por defecto una subcarpeta llamada `BKChem` y abre el diálogo de guardado directamente allí.

### 5. Compatibilidad Python 3.12
* Limpieza de errores de codificación de `bytes` a `strings` (UTF-8) en los archivos críticos de exportación que provocaban el cierre del programa.

### 6. Herramienta de Texto y Compatibilidad de Subíndices
* Se resolvió el error NameError: name 'unicode' is not defined migrando todo el manejo de texto a str de Python 3 en el archivo classes.py, permitiendo que la "Herramienta de Texto" funcione sin cierres inesperados.

* Se forzó un tamaño de fuente fijo de 8pt y un desplazamiento vertical de 4px para subíndices y superíndices en xml_writer.py. Esto evita el error del "Subíndice Gigante" en visores de imágenes de Linux como Nomacs o GPicView, garantizando que fórmulas como H2​O o CH4​ se representen con precisión.

---
##  Modified Files / Archivos Modificados:
* `bkchem/xml_writer.py`
* `bkchem/paper.py`
* `bkchem/export.py`
* `bkchem/main.py`
* `bkchem/classes.py`
* `bkchem/pixmaps/` -> (Path & loading logic / Lógica de rutas)

*Maintained and repaired in 2026. / Mantenido y reparado en 2026.*
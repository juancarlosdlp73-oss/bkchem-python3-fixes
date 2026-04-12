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

### 7. Functional Group and Atom Editing Stability

* Fixed the AttributeError: 'NoneType' object has no attribute 'delete' error that occurred when typing groups with more than one element (like OH or NH2) and pressing Enter.

* Implemented a "triple-shield" protection using try/except blocks in special_parents.py, atom.py, and molecule.py. This ensures that if the chemical validation engine doesn't recognize a group as a pure periodic table atom, the program automatically processes it as a text group (textatom) instead of crashing.

* Result: Improved workflow when drawing fatty acids and complex molecules, allowing free editing of atom labels without unexpected shutdowns.

### 8. Automatic Desktop Launcher

* Auto-configuration implementation: Added a function in start_bkchem.py that automatically detects the project's installation path.

* Shortcut creation: Upon the first execution, the script generates a .desktop file on the user's desktop with the correct icon and environment paths.

* Portability: This removes the need to manually configure Python or system paths, making the software "portable" across different folders or users.

### 9. Usability and File Association

* Double-Click Support: Modified the program startup in main.py to handle system arguments. This allows .cdml files to open directly when double-clicked in the file manager.

* Chemical Data Persistence: Optimized the reading of native .cdml files. Using this format ensures all atomic information, bonds, and arrows are correctly recovered thanks to the new stability patches.

### 10. Template System & Metadata Validation

* Fixed Save-As-Template Error: Resolved the "1 molecule have no template atom specified" error that blocked users from creating custom templates.

* Metadata Injection: Implemented the mark_as_template_selected method in main.py, which physically links atoms and bonds to the molecule's template_atom and template_bond properties.

* ID Normalization: Added a cleaning layer for Atom/Bond IDs to ensure they are stored as pure strings, allowing the internal validator to correctly match markers during the save process.

### 11. XML Serialization & "Deep Clean" Engine

* Byte-Prefix Removal: Created a recursive DOM sanitizer (sanitize_node) that runs before saving any CDML file. This eliminates the nested b'...' literals in chemical labels (e.g., saving CH2OH instead of b'CH2OH').

* Binary Mode Writing: Switched the CDML export logic to use binary mode (wb) with explicit UTF-8 encoding, preventing serialization crashes in Python 3.12's minidom implementation.

* Graphic Refresh Fix: Added explicit .draw() calls to the template markers to ensure the visual feedback (red/blue circles) appears immediately on the canvas.

### 12. Default Values: Startup Arrow Tool and Safe Scaling Settings.

* Upon starting BKChem, the selection arrow is now chosen by default. Additionally, all checkboxes in the scaling dialog that previously triggered unstable modifications are now unchecked by default.





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

### 7. Estabilidad en Grupos Funcionales y Edición de Átomos.
* Se corrigió el error AttributeError: 'NoneType' object has no attribute 'delete' que ocurría al intentar escribir grupos con más de un elemento (como OH o NH2) y pulsar Enter.

* Implementación de un "triple escudo" de protección mediante bloques try/except en special_parents.py, atom.py y molecule.py. Esto permite que, si el motor de validación química no reconoce un grupo como un átomo puro de la tabla periódica, el programa lo procese automáticamente como un grupo de texto (textatom) en lugar de cerrarse inesperadamente.

* Resultado: Mayor fluidez al dibujar ácidos grasos y moléculas complejas, permitiendo la edición libre de etiquetas de átomos sin interrupciones.

### 8. Lanzador Automático de Escritorio.

* Implementación de autoconfiguración: Se añadió una función en start_bkchem.py que detecta automáticamente la ruta de instalación del proyecto.

* Creación de acceso directo: Al ejecutar el programa por primera vez, el script genera un archivo .desktop en el escritorio del usuario con el icono y las rutas correctas.

* Portabilidad: Esto elimina la necesidad de configurar manualmente las rutas de Python o del sistema, permitiendo que el software sea "portable" entre diferentes carpetas o usuarios.

### 9. Usabilidad y Asociación de Archivos

* Soporte de Doble Clic: Se ha modificado el arranque del programa en main.py para que acepte argumentos del sistema. Esto permite que, al asociar los archivos .cdml con BKChem en Linux, se abran directamente con un doble clic.

* Persistencia de Datos Químicos: Optimización de la lectura de archivos nativos .cdml. Al usar este formato, se garantiza que toda la información atómica, enlaces y flechas se recuperen correctamente gracias a los nuevos parches de estabilidad.


### 10. Sistema de Plantillas y Validación de Metadatos

* Corrección de Error de Guardado: Se eliminó el error "1 molecule have no template atom specified" que impedía crear plantillas personalizadas.

* Inyección de Metadatos: Se implementó el método mark_as_template_selected en main.py, que vincula físicamente los átomos y enlaces a las propiedades de la molécula padre.

* Normalización de IDs: Se añadió una capa de limpieza para los IDs de Átomos y Enlaces, garantizando que se almacenen como texto puro para que el validador interno los reconozca sin errores.

### 11. Serialización XML y Motor de "Limpieza Profunda"

* Eliminación de Prefijos b': Se creó un saneador recursivo de DOM (sanitize_node) que se ejecuta antes de guardar cualquier archivo CDML. Esto elimina los literales b'...' en las etiquetas químicas (ej: guarda CH2OH en lugar de b'CH2OH').

* Escritura en Modo Binario: Se cambió la lógica de exportación CDML para usar el modo binario (wb) con codificación UTF-8, evitando fallos de serialización en la implementación de minidom de Python 3.12.

* Corrección de Refresco Gráfico: Se añadieron llamadas explícitas a .draw() en los marcadores de plantilla para asegurar que el feedback visual (círculos rojo/azul) aparezca inmediatamente en el lienzo.

### 12. Valores por defecto: Flecha al inicio y valores de escalado seguros.
* Al iniciar BKChem selecciona la flecha por defecto y al escalar, , están desmarcados toas las pestañas que hacian las modificaciones más inseguras"

### 13. Plantilla cargada de aldohexosa en proyección de Haworth.
* Botón con D-aldohexosa con plantilla. La plantilla generada a mano en xml, con grandes problemas, punto de anclaje enlace. Es funcional aunque aún no se enlaza bien. Quedan mejoras
---
###  Modified Files / Archivos Modificados:

* bkchem/xml_writer.py (SVG Subscripts & Binary CDML Export)
* bkchem/paper.py (Viewport & Auto-Crop Fix)
* bkchem/export.py (Smart Directory Paths)
* bkchem/main.py (Double-click, Template Logic & XML Sanitizer)
* bkchem/classes.py (Text Tool & Unicode/Str Migration)
* bkchem/atom.py (Symbol Cleaning & Validation Shield)
* bkchem/molecule.py (Validation Shield & Template Properties)
* bkchem/special_parents.py (Group Editing Stability Shield)
* bkchem/ftext.py (Chemical Label Byte-Cleaning)
* bkchem/arrow.py (Arrow Scaling Stability Fix)
* bkchem/start_bkchem.py (Desktop Launcher & Auto-Path)
* bkchem/pixmaps/ (UI Icons & Path Asset Fix)
* bkchem/dialogs.py
* bkchem/templates.cdml  -->Aldohexose skeleton added in a button


Maintained and repaired in 2026. / Mantenido y reparado en 2026.
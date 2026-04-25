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


"""home for atom class"""

import sys
import os
from warnings import warn
from . import dom_extensions
import operator
from .oasa import periodic_table as PT
from . import marks
from .special_parents import drawable_chem_vertex
from . import data
import re
from . import debug

from . import oasa
from .singleton_store import Screen, Store
from functools import reduce
from bkchem.oasa import periodic_table as PT


def clean_text( t):
  """Asegura que el texto sea siempre string de Python 3, eliminando prefijos b' o b\" de forma recursiva."""
  if t is None:
    return ""
  if isinstance( t, bytes):
    try:
      return t.decode( 'utf-8', 'ignore')
    except:
      return str( t)
  
  s = str( t).strip()
  # Limpieza agresiva de representaciones de bytes convertidas a string por error (b'...')
  while len( s) >= 3 and s.startswith( "b") and s[1] in ( "'", '"') and s.endswith( s[1]):
    s = s[2:-1]
  return s


### Class ATOM --------------------------------------------------
class atom( drawable_chem_vertex, oasa.atom):

  object_type = 'atom'
  meta__undo_properties = drawable_chem_vertex.meta__undo_properties + \
                          ( 'show_hydrogens',
                            'multiplicity', 'valency', 'free_sites', 'symbol')


  def __init__( self, standard=None, xy=(), package=None, molecule=None):
    drawable_chem_vertex.__init__( self, standard=standard, xy=xy, molecule=molecule)
    if xy:
      oasa.atom.__init__( self, coords=(xy[0],xy[1],0))
    else:
      oasa.atom.__init__( self)

    # chemistry attrs
    self.show = 0
    self.show_hydrogens = 0
    self.multiplicity = 1

    if package:
      self.read_package( package)
    else:
      self.set_name( 'C')



  ## ---------------------------------------- PROPERTIES ------------------------------
      
  # symbol (overrides the oasa.atom.symbol property)
  def _get_symbol( self):
    try:
      res = self._symbol
    except AttributeError:
      res = 'C'
    return clean_text( res)

  def _set_symbol( self, symbol):
    symbol = clean_text( symbol)
    self._symbol = symbol
    # Pasamos a oasa siempre como string limpio
    oasa.atom._set_symbol( self, symbol)
    if self._symbol != 'C':
      self.show = True

  symbol = property( _get_symbol, _set_symbol, None, "the atom symbol")


  # show
  def _get_show( self):
    return self._show

  def _set_show( self, show):
    if show in data.booleans:
      self._show = data.booleans.index( show)
    else:
      try:
        self._show = int( show)
      except:
        self._show = 0
    self.dirty = 1
    self._reposition_on_redraw = 1

  show = property( _get_show, _set_show, None,
                   "should the atom symbol be displayed? accepts both 0|1 and yes|no")


  # show_hydrogens
  def _get_show_hydrogens( self):
    return self._show_hydrogens

  def _set_show_hydrogens( self, show_hydrogens):
    if show_hydrogens in data.on_off:
      self._show_hydrogens = data.on_off.index( show_hydrogens)
    else:
      try:
        self._show_hydrogens = int( show_hydrogens)
      except:
        self._show_hydrogens = 0
    self.dirty = 1
    self._reposition_on_redraw = 1

  show_hydrogens = property( _get_show_hydrogens, _set_show_hydrogens)


  # charge (override of oasa.chem_vertex.charge)
  def _get_charge( self):
    return drawable_chem_vertex._get_charge( self)

  def _set_charge( self, charge):
    drawable_chem_vertex._set_charge( self, charge)
    self.dirty = 1

  charge = property( _get_charge, _set_charge)



  # valency
  def _get_valency( self):
    try:
      return self._valency
    except AttributeError:
      self.set_valency_from_name()
      return self._valency

  def _set_valency( self, val):
    drawable_chem_vertex._set_valency( self, val)

  valency = property( _get_valency, _set_valency, None, "atoms (maximum) valency, used for hydrogen counting")



  # free-sites - replaces oasa.atom.free_sites
  def _set_free_sites( self, free_sites):
    self._free_sites = free_sites
    mks = self.get_marks_by_type( "free_sites")
    if self._free_sites:
      if not mks:
        self.create_mark( "free_sites", draw=self.drawn)
      elif self.drawn:
        mks[0].redraw()
    else:
      if mks:
        self.remove_mark( "free_sites")


  def _get_free_sites( self):
    return self._free_sites

  free_sites = property( _get_free_sites, _set_free_sites, None, "atoms free_sites")


  def _get_free_sites_text( self):
    """used by free-site mark"""
    if self.free_sites:
      return "[%d]" % self.free_sites
    else:
      return ""

  free_sites_text = property( _get_free_sites_text, None, None, "atoms free_sites as text")


  # oxidation number as text
  def _get_oxidation_number_text( self):
    return data.roman_numbers[ self._get_oxidation_number()]

  oxidation_number_text = property( _get_oxidation_number_text, None, None, "atoms oxidation number as text")



  # xml_ftext (override drawable_chem_vertex.xml_ftext)
  def _get_xml_ftext(self):
    """Genera el texto con subíndices y carga para el dibujo."""
    import re
    
    # 1. Prioridad: ¿Tiene un nombre especial (Alias)?
    if hasattr(self, '_name_alias') and self._name_alias:
        text = clean_text(self._name_alias)
        # Convertimos números en subíndices (Ej: CH3 -> CH<sub>3</sub>)
        ret = re.sub(r'(\d+)', r'<sub>\1</sub>', text)
    else:
        # 2. Si es un átomo normal (C, O, N...)
        ret = clean_text(self.symbol)
        if self.show_hydrogens:
            v = self.free_valency
            if v > 0:
                h = 'H' + (f'<sub>{v}</sub>' if v > 1 else '')
                # Decidimos si el H va a la izquierda o derecha
                if not self.pos:
                    self.decide_pos()
                ret = h + ret if self.pos == 'center-last' else ret + h

    # 3. Añadimos la carga (Si existe)
    diff = self.charge - self.get_charge_from_marks()
    if diff:
        ch_val = str(abs(diff)) if abs(diff) > 1 else ''
        sign = '+' if diff > 0 else (chr(8722) if self.paper.get_paper_property('use_real_minus') else "-")
        ret += f'<sup>{ch_val}{sign}</sup>'

    return ret

  xml_ftext = property( _get_xml_ftext, None, None, "the text used for rendering using the ftext class")



  ## -------------------- OVERRIDES OF CHEM_VERTEX METHODS --------------------

  def decide_pos( self):
    if self.show_hydrogens or self.free_valency:
      drawable_chem_vertex.decide_pos( self)
    else:
      self.pos = "center-first"
  

  def set_name(self, name, interpret=1, check_valency=1, occupied_valency=None):
    name = clean_text(name)
    self._name_alias = name
    
    try:
        # 1. Intentamos la validación química real
        # Si esto funciona, el átomo tendrá peso y valencia
        ret = self._set_name(name, interpret=interpret, check_valency=check_valency, occupied_valency=occupied_valency)
        
        if ret:
            # Si se reconoció como átomo, nos aseguramos de que NO sea tratado como texto inerte
            self.is_text_only = False 
            self.set_valency_from_name()
            return True
            
    except Exception as e:
        # Solo si falla catastróficamente imprimimos el error para saber qué pasó
        print(f"DEBUG: Error en validación química de '{name}': {e}")

    # 2. El "Escudo" (Fallback): Si no es un átomo reconocido, lo tratamos como texto
    # Pero le asignamos una masa de 0 solo si realmente no hay otra opción
    self.symbol = name 
    self.show = 1
    self.is_text_only = True
    return True


  def _set_name( self, name, interpret=1, check_valency=1, occupied_valency=None):
    name = clean_text( name)
    self.charge = self.get_charge_from_marks()
    self.dirty = 1
    
    # 1. Caso especial: Carbono (no se muestra por defecto)
    if name.lower() == 'c':
      self.symbol = 'C'
      self.show = 0
      self._name_alias = None
      return True

    # 2. Intentar separar elemento y carga (Ej: Na+)
    elch = self.split_element_and_charge( name)
    if elch:
      self.symbol = clean_text( elch[0])
      self.charge += elch[1]
      self.show = 1
      return True

    # 3. REPARACIÓN PARA PYTHON 3: Forzar reconocimiento del símbolo
    # Buscamos el primer símbolo químico válido en el texto (Ej: "OH" -> "O")
    match = re.search(r'([A-Z][a-z]?)', name)
    if match:
        main_symbol = match.group(1)
        if main_symbol in PT.periodic_table:
            # ESTA LÍNEA ES LA CLAVE: actualizamos el símbolo base para que tenga peso
            self.symbol = main_symbol 
            self.show = 1
            # Guardamos el texto completo para el dibujo (OH, CH2OH, etc.)
            self._name_alias = name 
            
            # Limpiamos caché para que recalculé el peso molecular inmediatamente
            if hasattr(self, '_clean_cache'):
                self._clean_cache()
            return True
            
    return False


  def draw( self, redraw=False):
    if self.show:
      drawable_chem_vertex.draw( self, redraw=redraw)
    else:
      if self.item:
        warn( "drawing atom that is probably drawn", UserWarning, 2)
      x, y = self.x, self.y
      self.item = self.paper.create_line( x, y, x, y, tags=("atom", 'nonSVG'), fill='')
      self.selector = None
      if not redraw:
        [m.draw() for m in self.marks]
      self.paper.register_id( self.item, self)
      self._reposition_on_redraw = 0


  def focus( self):
    if self.show:
      drawable_chem_vertex.focus( self)
    else:
      x, y = self.x, self.y
      self.focus_item = self.paper.create_oval( x-4, y-4, x+4, y+4, tags=('helper_f','no_export'))
      self.paper.lift( self.item)


  def unfocus( self):
    if self.show:
      drawable_chem_vertex.unfocus( self)
    if self.focus_item:
      self.paper.delete( self.focus_item)
      self.focus_item = None


  def select( self):
    if self.show:
      drawable_chem_vertex.select( self)
    else:
      x, y = self.x, self.y
      if self.selector:
        self.paper.coords( self.selector, x-2, y-2, x+2, y+2)
      else:
        self.selector = self.paper.create_rectangle( x-2, y-2, x+2, y+2)
      self.paper.lower( self.selector)
      self._selected = 1


  def unselect( self):
    if self.show:
      drawable_chem_vertex.unselect( self)
    else:
      self.paper.delete( self.selector)
      self.selector = None
      self._selected = 0


  def read_package( self, package):
    self.id = clean_text( package.getAttribute( 'id'))

    for m in package.getElementsByTagName( 'mark'):
      mrk = marks.mark.read_package( m, self)
      self.marks.add( mrk)
      
    self.pos = clean_text( package.getAttribute( 'pos'))
    
    position = package.getElementsByTagName( 'point')[0]
    x, y, z = Screen.read_xml_point( position)
    if z != None:
      self.z = z* self.paper.real_to_screen_ratio()
    x, y = self.paper.real_to_screen_coords( (x, y))
    self.x = x
    self.y = y
    
    ft = package.getElementsByTagName('ftext')
    if ft:
      # Corregido: Unión de nodos XML más robusta para Python 3
      parts = []
      for e in ft[0].childNodes:
          parts.append( clean_text( e.toxml()))
      content = "".join( parts)
      self.set_name( content, check_valency=0, interpret=0)
    else:
      self.set_name( clean_text( package.getAttribute( 'name')), check_valency=0)
      self._name_alias = clean_text( package.getAttribute( 'name'))
    # charge
    val_charge = clean_text( package.getAttribute('charge'))
    self.charge = int( val_charge or 0)
    
    # hydrogens
    self.show_hydrogens = clean_text( package.getAttribute( 'hydrogens') or 0)
      
    fnt_elements = package.getElementsByTagName('font')
    if fnt_elements:
      fnt = fnt_elements[0]
      self.font_size = int( fnt.getAttribute( 'size') or 12)
      self.font_family = clean_text( fnt.getAttribute( 'family'))
      color = clean_text( fnt.getAttribute( 'color'))
      if color:
        self.line_color = color
        
    show_attr = clean_text( package.getAttribute( 'show'))
    if show_attr:
      self.show = show_attr
    else:
      self.show = (self.symbol!='C')
      
    if package.getAttributeNode( 'background-color'):
      self.area_color = clean_text( package.getAttribute( 'background-color'))
      
    mult_attr = clean_text( package.getAttribute( 'multiplicity'))
    if mult_attr:
      self.multiplicity = int( mult_attr)
      
    val_attr = clean_text( package.getAttribute( 'valency'))
    if val_attr:
      self.valency = int( val_attr)
      
    show_num_attr = clean_text( package.getAttribute( 'show_number'))
    if show_num_attr:
      self.show_number = bool( data.booleans.index( show_num_attr))
      
    num_attr = clean_text( package.getAttribute( 'number'))
    if num_attr:
      self.number = num_attr
      
    fs_attr = clean_text( package.getAttribute( 'free_sites'))
    if fs_attr:
      self.free_sites = int( fs_attr)


  def get_package( self, doc):
    """returns a DOM element describing the object in CDML"""
    yes_no = ['no','yes']
    on_off = ['off','on']
    a = doc.createElement('atom')
    a.setAttribute( 'id', str( self.id))
    if self.charge:
      a.setAttribute( "charge", str( self.charge))
    if (bool(self.show) and self.symbol=='C') or (not bool(self.show) and self.symbol!='C'): 
      a.setAttribute('show', yes_no[ int(self.show) ])
    if self.show:
      a.setAttribute( 'pos', str(self.pos))
    if self.font_size != self.paper.standard.font_size \
       or self.font_family != self.paper.standard.font_family \
       or self.line_color != self.paper.standard.line_color:
      font = dom_extensions.elementUnder( a, 'font', attributes=(('size', str( self.font_size)), ('family', str(self.font_family))))
      if self.line_color != self.paper.standard.line_color:
        font.setAttribute( 'color', str(self.line_color))
    
    # REPARACIÓN: Guardamos el alias si existe, si no, el símbolo
    if hasattr(self, '_name_alias') and self._name_alias:
        a.setAttribute('name', clean_text(self._name_alias))
    else:
        a.setAttribute('name', clean_text(self.symbol))
    
    if self.show_hydrogens:
      a.setAttribute('hydrogens', on_off[ int(self.show_hydrogens) ])
    if self.area_color != self.paper.standard.area_color:
      a.setAttribute( 'background-color', str(self.area_color))
    x, y, z = map( Screen.px_to_text_with_unit, self.get_xyz( real=1))
    if self.z:
      dom_extensions.elementUnder( a, 'point', attributes=(('x', x), ('y', y), ('z', z)))
    else: 
      dom_extensions.elementUnder( a, 'point', attributes=(('x', x), ('y', y)))
    for o in self.marks:
      a.appendChild( o.get_package( doc))
    if self.multiplicity != 1:
      a.setAttribute( 'multiplicity', str( self.multiplicity))
    a.setAttribute( 'valency', str( self.valency))
    if self.number:
      a.setAttribute( 'number', str(self.number))
      a.setAttribute( 'show_number', data.booleans[ int( self.show_number)])
    if self.free_sites:
      a.setAttribute( 'free_sites', str( self.free_sites))
    return a

  ##  VARIAS REPARACIONES
  def get_formula_dict(self):
    from .oasa import periodic_table as PT
    print(f"DEBUG: Calculando formula para el atomo {self.symbol} con alias {getattr(self, '_name_alias', 'None')}")
    res = {}
    
    # 1. ¿Qué texto tiene el átomo? (Ej: "OH", "CH2OH", "O", "C")
    name = getattr(self, '_name_alias', None) or self.symbol
    
    # 2. Trituradora de texto: Extraemos TODO lo que parezca un elemento
    import re
    matches = re.findall(r'([A-Z][a-z]?)([0-9]*)', name)
    
    for sym, num in matches:
        if sym in PT.periodic_table:
            count = int(num) if num else 1
            res[sym] = res.get(sym, 0) + count

    # 3. SEGURIDAD: Si por alguna razón el nombre no dio resultado (ej: un símbolo raro)
    # añadimos el símbolo base si no está ya en el diccionario.
    if self.symbol not in res and self.symbol in PT.periodic_table:
        res[self.symbol] = 1

    # 4. HIDRÓGENOS AUTOMÁTICOS
    # Solo sumamos de la valencia libre si NO hemos encontrado 'H' en el texto
    # Esto evita que "OH" sume el H del texto + el H de valencia libre.
    if 'H' not in res:
        v = self.free_valency
        if v > 0:
            res['H'] = res.get('H', 0) + v
            
    return res


  def _set_mark_helper( self, mark, sign=1):
    drawable_chem_vertex._set_mark_helper( self, mark, sign=sign)
    mark_name, _ = self._mark_to_name_and_class( mark)
    if mark_name == 'plus':
      self.charge += 1*sign
    elif mark_name == 'minus':
      self.charge -= 1*sign
    elif mark_name == "radical":
      self.multiplicity += 1*sign
    elif mark_name == "biradical":
      self.multiplicity += 2*sign
    

  def update_after_valency_change( self):
    if self.free_valency <= 0:
      self.raise_valency_to_senseful_value()
    if self.show_hydrogens:
      self.redraw()


  def __str__( self):
    # Fix para ID como bytes en Py3
    return str(clean_text( self.id))


  def get_charge_from_marks( self):
    res = 0
    for m in self.marks:
      if m.__class__.__name__ == 'plus':
        res += 1
      elif m.__class__.__name__ == "minus":
        res -= 1
    return res


  def generate_marks_from_cheminfo( self):
    if self.charge == 1 and not self.get_marks_by_type( 'plus'):
      self.create_mark( 'plus', draw=0)
    elif self.charge == -1 and not self.get_marks_by_type( 'minus'):
      self.create_mark( 'minus', draw=0)
    if self.multiplicity == 2 and not self.get_marks_by_type( 'radical'):
      self.create_mark( 'radical', draw=0)
    elif self.multiplicity == 3 and not (self.get_marks_by_type( 'biradical') or len( self.get_marks_by_type( 'radical')) == 2):
      self.create_mark( 'biradical', draw=0)
  

  def set_valency_from_name( self):
    for val in PT.periodic_table[ self.symbol]['valency']:
      self.valency = val
      try:
        fv = self.free_valency
      except:
        return
      if fv >= 0:
        return

    

  def bbox( self, substract_font_descent=False):
    if self.show:
      return drawable_chem_vertex.bbox( self, substract_font_descent=substract_font_descent)
    else:
      if self.item:
        return self.paper.bbox( self.item)
      else:
        return self.x, self.y, self.x, self.y



  def split_element_and_charge( self, txt):
    txt = clean_text( txt)
    splitter = re.compile("^([a-zA-Z]+)([0-9]*)([+-]?)$")
    matcher = re.compile( "^([a-zA-Z]+)([0-9]*[+-])?$")
    if not matcher.match( txt.lower()):
      return None
    match = splitter.match( txt.lower())
    if match:
      if match.group(1).capitalize() not in PT.periodic_table or 'query' in PT.periodic_table[ match.group(1).capitalize()].keys():
        return None
      if match.group(3) == '+':
        charge = match.group(2) and int( match.group(2)) or 1
      elif match.group(3) == '-':
        charge = match.group(2) and -int( match.group(2)) or -1
      else:
        charge = 0
      return (match.group(1).capitalize(), charge)
    else:
      return None


  def after_undo( self):
    self._clean_cache()

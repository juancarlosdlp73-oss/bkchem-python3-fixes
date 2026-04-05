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


"""provides exporters to XML formats (SVG for now)"""

from .oasa import geometry
import xml.dom.minidom as dom
from xml.dom.minidom import Document
import re
from . import data
from . import dom_extensions
import operator
import os
from .tuning import Tuning
from .ftext import ftext as ftext_class
from .singleton_store import Screen

class XML_writer:
  def __init__( self, paper):
    self.paper = paper
    self.document = Document()
    self.top = None 

  def construct_dom_tree( self, top_levels):
    pass

  def get_nicely_formated_document( self):
    dom_extensions.safe_indent( self.top, dont_indent=("text","ftext","user-data","tspan"))
    return self.document.toxml()

pt_or_px="pt"

class SVG_writer( XML_writer):
  def __init__( self, paper):
    XML_writer.__init__( self, paper)
    self.full_size = not (paper.get_paper_property( 'crop_svg') and len( paper.stack))
    self.cc = self.paper.any_color_to_rgb_string
    self.convert = lambda x: "%.2f" % x

  def construct_dom_tree( self, top_levels):
    border_size = self.paper.get_paper_property( 'crop_margin')
    px_to_mm_txt = lambda x: Screen.px_to_text_with_unit( x, unit="mm", round_to=5)
    self._id = 0
    doc = self.document
    self.top = dom_extensions.elementUnder( doc, "svg", attributes=(("xmlns", "http://www.w3.org/2000/svg"), ("version", "1.1")))
    
    items = list( self.paper.find_all())
    if self.paper.background in items:
        items.remove( self.paper.background)
    
    if not items:
        return

    x1, y1, x2, y2 = self.paper.list_bbox( items)
    w = px_to_mm_txt( x2 -x1 +2*border_size)
    h = px_to_mm_txt( y2 -y1 +2*border_size)
    bx2, by2 = x2-x1+2*border_size, y2-y1+2*border_size
    dom_extensions.setAttributes( self.top, (("width", w), ("height", h), ("viewBox",'0 0 %d %d' % ( bx2, by2))))
    
    self.group = dom_extensions.elementUnder( self.top, 'g', (('font-size', '12pt'), ('font-family', 'Helvetica'), ('stroke-linecap', 'round')))
    self.group.setAttribute( 'transform', 'translate(%d,%d)' % (-x1+border_size, -y1+border_size))
      
    cs = [c for c in self.paper.stack if c in top_levels]
    for o in cs:
      if o.object_type == 'molecule':
        for b in o.bonds: self.add_bond( b)
        for a in o.atoms: self.add_atom( a)
      elif o.object_type == 'arrow': self.add_arrow( o)
      elif o.object_type == 'text': self.add_text( o)
      elif o.object_type == 'plus': self.add_plus( o)
      elif o.object_type in data.vector_graphics_types:
        if o.object_type == 'rect': self.add_rect( o)
        elif o.object_type == 'oval': self.add_oval( o)
        elif o.object_type == 'polygon': self.add_polygon( o)
        elif o.object_type == 'polyline': self.add_polyline( o)

  def add_bond( self, b):
    if not b.item: return
    line_width = (b.type == 'b') and b.wedge_width or b.type != 'w' and b.line_width or 1.0
    l_group = dom_extensions.elementUnder( self.group, 'g', (('stroke-width', str( line_width)), ('stroke', self.cc( b.line_color))))
    line_items, items = b.get_exportable_items()
    if b.type in 'nbhd':
      for i in items:
        coords = self.paper.coords( i)
        dom_extensions.elementUnder( l_group, 'line', (('x1', self.convert(coords[0])), ('y1', self.convert(coords[1])), ('x2', self.convert(coords[2])), ('y2', self.convert(coords[3]))))
    elif b.type == 'w':
      coords = self.paper.coords( b.item)
      dom_extensions.elementUnder( l_group, 'polygon', (('fill', self.cc( b.line_color)), ('stroke', self.cc( b.line_color)), ('points', list_to_svg_points( coords))))
    for i in line_items:
      coords = self.paper.coords( i)
      dom_extensions.elementUnder( l_group, 'line', (('x1', self.convert(coords[0])), ('y1', self.convert(coords[1])), ('x2', self.convert(coords[2])), ('y2', self.convert(coords[3])), ('stroke-width', str( b.line_width))))

  def add_atom( self, a):
    if a.show:
      x, y, x2, y2 = self.paper.bbox( a.selector)
      y1 = y + a.font.metrics('ascent') + Tuning.SVG.text_y_shift
      text = ftext_dom_to_svg_dom( dom.parseString( ftext_class.sanitize_text( a.xml_ftext)).childNodes[0], self.document)
      dom_extensions.setAttributes( text, (("x", self.convert( x)), ("y", self.convert( y1)), ("font-family", a.font_family), ("font-size", '%d%s' % (a.font_size, pt_or_px)), ('fill', self.cc( a.line_color))))
      self.group.appendChild( text)

  def add_text( self, t):
    x, y, x2, y2 = t.ftext.bbox( complete=True)
    y1 = y + (y2-y)*0.75
    text = ftext_dom_to_svg_dom( dom.parseString( t.ftext.sanitized_text()).childNodes[0], self.document, replace_minus=t.paper.get_paper_property('replace_minus'))
    dom_extensions.setAttributes( text, (("x", self.convert( x)), ("y", self.convert( y1)), ("font-family", t.font_family), ("font-size", '%d%s' % (t.font_size, pt_or_px)), ('fill', self.cc( t.line_color))))
    self.group.appendChild( text)

  def add_arrow(self, a): pass
  def add_plus(self, p): pass
  def add_rect(self, o): pass
  def add_oval(self, o): pass
  def add_polygon(self, o): pass
  def add_polyline(self, o): pass

def list_to_svg_points( l):
  return ' '.join( ["%.2f" % x for x in l])

def ftext_dom_to_svg_dom( ftext, doc, add_to=None, replace_minus=False):
  if not add_to:
    element = doc.createElement('text')
  else:
    element = add_to

  if ftext.nodeType != ftext.TEXT_NODE:
    name = str(ftext.nodeName)
    if name == "ftext":
      my_svg = element
    else:
      my_svg = doc.createElement('tspan')
      element.appendChild(my_svg)

    if name == 'b': my_svg.setAttribute('font-weight', 'bold')
    elif name == 'i': my_svg.setAttribute('font-style', 'italic')
    elif name == 'sup':
      # Fix Andrea: Superíndice forzado a 8pt y -4px
      my_svg.setAttribute('font-size', '8pt')
      my_svg.setAttribute('dy', '-4px')
    elif name == 'sub':
      # Fix Andrea: Subíndice forzado a 8pt y +4px
      my_svg.setAttribute('font-size', '8pt')
      my_svg.setAttribute('dy', '4px')

    for el in ftext.childNodes:
      ftext_dom_to_svg_dom(el, doc, add_to=my_svg, replace_minus=replace_minus)
  else:
    val = ftext.nodeValue
    if val:
      if isinstance(val, bytes): val = val.decode('utf-8')
      txt = str(val).replace("-", chr(8722)) if replace_minus else str(val)
      element.appendChild(doc.createTextNode(txt))
  return element
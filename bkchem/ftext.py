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


"""this module provides extended methods for formating of text items (for canvas)
ftext is XML based. Tags used for formating are:
sub - (sub)script, sup - (sup)erscript, b - bold, i - italic"""

"""this module provides extended methods for formating of text items (for canvas)
ftext is XML based. Tags used for formating are:
sub - (sub)script, sup - (sup)erscript, b - bold, i - italic"""

import tkinter.font as tkFont
from . import dom_extensions
import xml.sax
import copy
import re
import io
from html.entities import name2codepoint

from . import tuning


def clean_text(t):
    """Asegura que el texto sea siempre string de Python 3 y sin prefijo b'"""
    if t is None:
        return ""
    if isinstance(t, bytes):
        try:
            return t.decode('utf-8', 'ignore')
        except:
            return str(t)
    
    t = str(t)
    # Limpieza profunda de representaciones literales de bytes como "b'OH'"
    if len(t) >= 3 and t.startswith("b") and t[1] in ("'", '"') and t.endswith(t[1]):
        return t[2:-1]
    return t


class ftext:

  def __init__( self, canvas, xy, text, font=None, pos="center-first", fill='#000', big_charges=True, justify='right'):
    self.big_charges = big_charges
    self.canvas = canvas
    self.items = []
    self.tags = ('ftext'),
    
    # Limpieza inmediata del texto de entrada para evitar b'
    self.text = clean_text(text)
    
    if xy:
      self.x, self.y = xy
      
    if font:
      self.font = font
    else:
      self.font = tkFont.Font( family="Helvetica", size=12)
      
    self._font_family = self.font.actual('family')
    self._font_size = int( self.font.actual('size'))
    self.pos = pos
    self.fill = fill
    self.justify = justify

    
  def draw( self):
    # split text to chunks
    chs = self.get_chunks()
    if not chs:
      return None

    self.items = []
    self._current_x = self.x
    self._current_y = self.y

    self.items = chs
    last_attrs = set()
    last_x = self._current_x
    
    for ch in self.items:
      scale = 1
      if set(('sub','sup')) & ch.attrs:
        if not (ch.text in "-" and self.big_charges):
          scale = 0.7
        else:
          scale = 1
        ch.ignore_y = True
        ch.ignore_x = True
        if set(('sub','sup')) & last_attrs:
          self._current_x = last_x
      last_x = self._current_x
      last_attrs = ch.attrs
      bbox = self._draw_chunk( ch, scale=scale)
      if ch.newline_after:
        self._current_y = bbox[3] + self.font.metrics()['linespace'] / 2.0
        self._current_x = self.x

    if self.pos == 'center-first' and self.items:
      self.diff = self.font.measure( self.items[0].text[0])/2.0
    elif self.pos == 'center-last' and self.items:
      x1, y1, x2, y2 = self.bbox()
      self.diff = x2 -x1 -self.font.measure( self.items[0].text[-1])/2.0 -2
    else:
      self.diff = 0

    self.move( -self.diff, 0)
    return self.bbox()


  def _draw_chunk( self, chunk, scale=1):
    weight = ''
    canvas = self.canvas
    x = self._current_x
    y = self._current_y

    if 'b' in chunk.attrs:
      weight = "bold"
    if 'i' in chunk.attrs:
      weight += " italic"
    if not weight:
      weight = "normal"

    # Forzamos que el texto del chunk sea string puro para el Canvas
    display_text = clean_text(chunk.text)

    if 'sub' in chunk.attrs:
      item = canvas.create_text( x+tuning.Tuning.Screen.pick_best_value("supsubscript_x_shift",self._font_size),
                                 y+tuning.Tuning.Screen.pick_best_value("subscript_y_shift",self._font_size),
                                 tags=self.tags, text=display_text,
                                 font=(self._font_family, int( round( self._font_size*scale)), weight),
                                 anchor="nw", justify=self.justify, fill=self.fill)
    elif 'sup' in chunk.attrs:
      item = canvas.create_text( x+tuning.Tuning.Screen.pick_best_value("supsubscript_x_shift",self._font_size),
                                 y,
                                 tags=self.tags, text=display_text,
                                 font=(self._font_family, int( round( self._font_size*scale)), weight),
                                 anchor="sw", justify=self.justify, fill=self.fill)
    else:
      item = canvas.create_text( x, y, tags=self.tags, text=display_text,
                                 font=(self._font_family, int( round( self._font_size*scale)), weight),
                                 anchor="w",
                                 justify=self.justify,
                                 fill=self.fill)
    bbox = canvas.bbox( item)
    chunk.item = item
    chunk.dx = abs( bbox[0] - bbox[2])
    self._current_x = bbox[2]
    return bbox


  def get_chunks( self):
    text = self.sanitized_text()
    handler = FtextHandler()
    try:
      # Usamos io.StringIO para mayor compatibilidad con strings en Python 3 SAX
      xml.sax.parseString( text.encode('utf-8'), handler)
    except:
      # Si falla el parseo XML, devolvemos el texto plano como un solo bloque
      return [text_chunk(text=self.text)]
    
    chunks = []
    for ch in handler.chunks:
      parts = ch.text.split("\n")
      if len( parts) > 1:
        for i,part in enumerate( parts):
          if i < len( parts)-1:
            new_ch = text_chunk( text=part, attrs=ch.attrs, newline_after=True)
          else:
            new_ch = text_chunk( text=part, attrs=ch.attrs)
          chunks.append( new_ch)
      else:
        chunks.append( ch)
    return chunks


  def bbox( self, complete=False):
    """returns the bounding box of the object as a list of [x1,y1,x2,y2]"""
    items_to_bbox_x = [i.item for i in self.items if i.item and (complete or not i.ignore_x)]
    items_to_bbox_y = [i.item for i in self.items if i.item and (complete or not i.ignore_y)]
    
    if not items_to_bbox_x or not items_to_bbox_y:
        return [self.x, self.y, self.x, self.y]
        
    try:
        xbbox = list( self.canvas.list_bbox( items_to_bbox_x))
        ybbox = list( self.canvas.list_bbox( items_to_bbox_y))
        return [xbbox[0], ybbox[1], xbbox[2], ybbox[3]]
    except:
        return [self.x, self.y, self.x, self.y]
          

  def move( self, dx, dy):
    for i in self.items:
      if i.item:
        self.canvas.move( i.item, dx, dy)

  def move_to( self, x, y):
    if not hasattr(self, 'diff'): self.diff = 0
    dx = self.x - x - self.diff
    dy = self.y - y
    for i in self.items:
      if i.item:
        self.canvas.move( i.item, dx, dy)

  def lift( self):
    for i in self.items:
      if i.item:
        self.canvas.lift( i.item)

  def delete( self):
    for i in self.items:
      if i.item:
        self.canvas.delete( i.item)

      
  def sanitized_text( self):
    return self.__class__.sanitize_text( self.text)


  @classmethod
  def sanitize_text( cls, text):
    text = clean_text(text)
    text = unescape_html_entity_references( text)
    x = "<ftext>%s</ftext>" % text
    return x
    

class text_chunk:
  def __init__( self, text, attrs=None, newline_after=False):
    self.text = clean_text(text)
    self.attrs = attrs or set()
    self.item = None
    self.dx = 0
    self.ignore_y = False
    self.ignore_x = False
    self.newline_after = newline_after


class FtextHandler ( xml.sax.ContentHandler):
  def __init__( self):
    xml.sax.ContentHandler.__init__( self)
    self._above = []
    self.chunks = []
    self._text = ""

  def startElement( self, name, attrs):
    self._closeCurrentText()
    self._above.append( name)

  def endElement( self, name):
    self._closeCurrentText()
    self._above.pop( -1)

  def _closeCurrentText( self):
    if self._text:
      self.chunks.append( text_chunk( self._text, attrs = set( self._above)))
      self._text = ""

  def characters( self, data):
    # Aseguramos que los caracteres leídos por el parser SAX sean texto limpio
    self._text += clean_text(data)


def unescape_html_entity_references( text):
  text = clean_text(text)
  return re.sub( "&([a-zA-Z]+);", _unescape_one_html_entity_reference, text)

def _unescape_one_html_entity_reference( m):
  hit = m.group(1)
  if hit not in ["amp","gt","lt"] and hit in name2codepoint:
    return chr( name2codepoint[hit])
  else:
    return "&"+hit+";"

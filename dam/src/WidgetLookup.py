# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 CENATIC: Centro Nacional de Referencia de
# Aplicacion de las TIC basadas en Fuentes Abiertas, Spain.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#   Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
#
#   Neither the name of the CENATIC nor the names of its contributors
#   may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# You may contact the copyright holder at: Fundacion CENATIC, Edificio
# de Servicios Sociales: C/ Vistahermosa, 1, 3ra planta, 06200
# Almendralejo (Badajoz), Spain

import CTK
import PageLookup

from ComboboxSQL import ComboboxSQL
from consts import *
from config import *

def __get_interval_table (name):
    # Render interval input
    table = CTK.Table()
    table[(1,1)] = CTK.TextField({'name': "%s-" % name,
                                  'class':'required two_fields'})
    table[(1,2)] = CTK.RawHTML ("-")
    table[(1,3)] = CTK.TextField({'name': "%s+" % name,
                                  'class':'required two_fields'})
    return table

def __get_date_table (name):
    # Render interval input
    table = CTK.Table()
    table[(1,1)] = CTK.DatePicker({'name': "%s-" % name,
                                  'class':'required two_fields'})
    table[(1,2)] = CTK.RawHTML ("-")
    table[(1,3)] = CTK.DatePicker({'name': "%s+" % name,
                                  'class':'required two_fields'})
    return table

def get_text_form (redir = None):
    # Render fulltext search form
    simple = CTK.PropsTable ()
    simple.Add('Búsqueda',CTK.TextField({'name':'search', 'class':'required sole_field'}),'Introduzca los términos de la búsqueda.')

    form = CTK.Submitter("%s/apply" %(PageLookup.LOCATION))
    form += simple
    if redir:
        form += CTK.HiddenField ({'name': 'redir', 'value': redir})
    form += CTK.SubmitterButton('Buscar')

    return form


def get_fields_form (redir = None):
    # Render advanced search form
    q_types    = "SELECT id, type   FROM asset_types;"
    q_licenses = "SELECT id, name   FROM licenses;"
    q_formats  = "SELECT id, format FROM formats;"
    custom_option = ('','Elegir')
    lang_options  = [custom_option] + [(x,'(%s) %s' % (x,y)) for x,y in LANG]

    advanced = CTK.PropsTable ()
    advanced.Add ('ID',          CTK.TextField({'name':'id', 'class':'required one_field'}), 'Identificador del activo')
    advanced.Add ('Título',      CTK.TextField({'name':'title', 'class':'required one_field'}), 'Titulo del activo')
    advanced.Add ('Tema',        CTK.TextField({'name':'subject', 'class':'required one_field'}), 'El tema del contenido del activo')
    advanced.Add ('Autor',       CTK.TextField({'name':'creator_name', 'class':'required one_field'}), 'Nombre del creador del activo')
    advanced.Add ('Publicador',  CTK.TextField({'name':'publisher_name', 'class':'required one_field'}), 'Nombre del publicador del activo')
    advanced.Add ('Colección',   CTK.TextField({'name':'collection_name', 'class':'required one_field'}), 'Nombre de la colección en la que está el activo')
    advanced.Add ('Idioma',      CTK.Combobox ({'name':'language', 'class':'required one_field'}, lang_options), 'Idioma del activo')
    advanced.Add ('Licencia',    ComboboxSQL  ({'name':'licenses_id', 'class':'required one_field'}, q_licenses, custom_option), 'Licencia del activo')
    advanced.Add ('Tipo',        ComboboxSQL  ({'name':'asset_types_id', 'class':'required one_field'}, q_types, custom_option), 'Tipo de activo')
    advanced.Add ('Formato',     ComboboxSQL  ({'name':'formats_id', 'class':'required one_field'}, q_formats, custom_option), 'Formato del activo')

    advanced.Add ('Descripción', CTK.TextField({'name':'description', 'class':'required one_field'}), 'Descripcion del activo')
    advanced.Add ('Creación',    __get_date_table('date_created'),   'Fecha de creación del activo')
    advanced.Add ('Publicación', __get_date_table('date_available'), 'Fecha de publicación del activo')
    advanced.Add ('Versión',     __get_interval_table('version'), 'Versión del activo')
    advanced.Add ('Duración',    __get_interval_table('extent'),  'Duración del activo (hh:mm)')
    advanced.Add ('Vistas',      __get_interval_table('views'),   'Número de visualizaciones del activo')
    advanced.Add ('Tamaño',      __get_interval_table('size'), 'Tamaño de archivo (bytes)')
    advanced.Add ('Bitrate',     __get_interval_table('bitrate'), 'Bitrate de codificación (bps)')
    advanced.Add ('Anchura',     __get_interval_table('width'), 'Anchura en pixels')
    advanced.Add ('Altura',      __get_interval_table('height'), 'Altura en pixels')

    form = CTK.Submitter("%s/apply" %(PageLookup.LOCATION))
    form += advanced

    if redir:
        form += CTK.HiddenField ({'name': 'redir', 'value': redir})
    form += CTK.SubmitterButton('Buscar')

    return form


def test ():
    test_string  = '/redir/phony_string'

    text   = get_text_form ().Render().toStr()
    assert 'Buscar' in text
    print '#1 get_text_form() OK'

    text   = get_text_form (test_string).Render().toStr()
    assert test_string in text
    print '#2 get_text_form(test_string) OK'

    fields = get_fields_form ().Render().toStr()
    assert 'Buscar' in fields
    print '#1 get_fields_form() OK'

    fields = get_text_form (test_string).Render().toStr()
    assert test_string in fields
    print '#2 get_fields_form(test_string) OK'

    table  = __get_interval_table (test_string).Render().toStr()
    assert test_string in table and 'required two_fields' in table
    print '#1 __get_interval_table(test_string) OK'

    table  = __get_date_table (test_string).Render().toStr()
    assert test_string in table and 'required two_fields' in table
    print '#1 __get_date_table(test_string) OK'


if __name__ == '__main__':
    test()

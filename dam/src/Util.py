# -*- coding: utf-8 -*-
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

import os
import re
import threading
import Page
from CTK.Server import get_server
from config import *

#
# Utility functions
#

def get_es_substitutions (num):
    """Return Spanish substitutions for plurals"""
    subs = [{'n': '', 's': ''},
            {'n':'n', 's':'s'}][(num > 1)]
    subs['num'] = num
    return subs

def clear_params (req):
    """Removes the parameters (key=val;) from a request"""

    tmp = req.split('/')
    location = '/'.join(tmp[:-1])

    try:
        pre = tmp[-1].split(';')[0]
        if not '=' in pre:
            location += '/%s' % pre
    except IndexError:
        pass

    if location[-1] == '/':
        location = location[:-1]
    return location

def test_page (page_name):
    """Check if given Page*.py file is working properly"""
    basename = os.path.basename (page_name)
    name,ext = os.path.splitext (basename)

    test_string = 'phony'
    test   = Page.Default (body_id = test_string)
    render = test.Render()
    assert test_string in render
    print '#1 %s (data) OK' % name

    test   = Page.Default ()
    render = test.Render()
    assert len(render)
    print '#2 %s () OK' % name

    wp    = get_server()._web_paths
    print '#3 %s rutas publicadas' % len(wp)
    for i in range(len(wp)):
        url  = wp[i]._regex[1:]
        try:
            func = str(wp[i]._Publish_FakeClass__func).split()[1]
        except AttributeError:
            func = str(wp[i].__init__).split('.__init')[0].split('bound method ')[1]

        print "%24s --> %s" %(func, url)


def dump(obj):
    txt = ''
    for attr in dir(obj):
        txt += "obj.%s = %s\n" % (attr, getattr(obj, attr))
    return txt

def get_all_pages ():
    """Find existing Page.+\.py"""
    files = filter(lambda x: re.match('Page.+\.py$',x), os.listdir('.'))
    return [os.path.splitext(x)[0] for x in files]

def test ():
    test = get_es_substitutions (1)
    assert '1 objeto%(s)s' % test == '1 objeto'
    print '#1 get_es_substitutions (singular) OK'

    test = get_es_substitutions (2)
    assert '2 objeto%(s)s' % test == '2 objetos'
    print '#2 get_es_substitutions (plural) OK'

    test_string = "/phony/url/phony=param;"
    test_result = clear_params (test_string)
    assert test_result == "/phony/url"
    print '#1 clear_params ("%s") OK' % test_string

    test_string = "/phony/url/phony&param"
    test_result = clear_params (test_string)
    assert test_result == test_string
    print '#2 clear_params ("%s") OK' % test_string


if __name__ == '__main__':
    test()

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

import urllib
import CTK

from ACL import ACL
from CTK.consts import *
from config import *
from Util import *


class InterfaceWidget (CTK.Container):
    """Parent class of all interface widgets (those used by the
    paginator"""

    def __init__ (self):
        CTK.Container.__init__ (self)

class Paginate (InterfaceWidget):
    """Paginate given results using a given consume-widget"""

    def __init__ (self, contents, widget, **kwargs):
        InterfaceWidget.__init__ (self)

        self._check_referrer()

        pnum = self.pag['pnum']
        pmax = self.pag['pmax']
        total = (len(contents)-1) / pmax + 1

        while pnum > 1:
            contents = contents[pmax:]
            pnum -= 1
        contents = contents[:pmax]

        interface_widget = widget(**kwargs)
        for constructor,x in contents:
            content = constructor(x)
            interface_widget.Add(content)
        self += interface_widget

        if total > 1:
            table = CTK.Table({'class':'paginate'})
            links = self._get_links (self.pag['pnum'], pmax, total)
            table[(1,1)] = links
            self += table


    def _check_referrer(self):
        """Separate referrer line from pagination info"""
        req = urllib.unquote(CTK.request.url)
        location = clear_params (req)

        tmp = req[len(location):]
        while tmp.startswith('/'):
            tmp = tmp[1:]
        tmp = tmp.replace('/',';')

        params = {}
        pairs = tmp.split(';')
        for pair in pairs:
            pair = pair.split('=')
            if len(pair) > 1:
                key,value = pair[0], pair[1]
                params[key] = value

        try:
            self.pag = { 'pnum': int(params.get('pnum',1)),
                         'pmax': int(params.get('pmax',PAG_ITEMS)) }
        except ValueError:
            self.pag = { 'pnum': 1, 'pmax': PAG_ITEMS }

        for key in ['pnum','pmax']:
            if params.has_key(key):
                params.pop(key)

        aux = ["%s=%s" % (key,val) for key,val in params.items()]
        ref = '%s/%s' % (location,';'.join (aux))

        self.ref = ref


    def _get_links (self, pnum, pmax, total):
        first = '⇇'
        prev  = '←'
        curr  = 'Pág. %s / %s' % (pnum, total)
        next  = '→'
        last  = '⇉'

        if pnum != 1:
            url   = "%s;pnum=1;pmax=%s" %  (self.ref, pmax)
            first = LINK_HREF % (url, first)
            url   = "%s;pnum=%s;pmax=%s" % (self.ref, pnum-1, pmax)
            prev = LINK_HREF % (url, prev)
        if pnum < total:
            url   = "%s;pnum=%s;pmax=%s" % (self.ref, pnum+1, pmax)
            next  = LINK_HREF % (url, next)
            url   = "%s;pnum=%s;pmax=%s" % (self.ref, total,  pmax)
            last  = LINK_HREF % (url, last)

        links = [CTK.RawHTML(x) for x in [first, prev, curr, next, last]]
        return links


#
# Miscelaneous useful widgets
#

class Message (CTK.Dialog):
    def __init__ (self, msg, props={}):
        default_props = {
            'title':     'Aviso',
            'autoOpen':  True,
            'draggable': False}

        for key in default_props.keys():
            if key not in props:
                props[key] = default_props[key]

        CTK.Dialog.__init__ (self, props)
        self += CTK.RawHTML ('<p>%s</p>'%msg)


def test ():
    #ASCII
    test   = Message('ASCII')
    render = test.Render().toStr()
    assert 'ASCII' in render
    print '#1: Message("ASCII") OK'

    #UNICODE
    test   = Message('ユニコード')
    render = test.Render().toStr()
    assert 'ユニコード' in render
    print '#2: Message("ユニコード") OK'

    #Empty
    test   = Message('')
    render = test.Render().toStr()
    assert len(render)
    print '#3: Message("") OK'

    #InterfaceWidget
    test   = InterfaceWidget()
    render = test.Render().toStr()
    assert test
    print 'InterfaceWidget() OK'

    #Paginate
    try:
        test = Paginate([], InterfaceWidget)
    except AttributeError:
        print '#1: Paginate() OK: Behavior as expected'

if __name__ == '__main__':
    test()

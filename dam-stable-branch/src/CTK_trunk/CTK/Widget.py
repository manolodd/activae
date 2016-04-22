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
# You may contact the copyright holder at: Fundacion CENATIC, Avenida
# Clara Campoamor, s/n. 06200 Almendralejo (Badajoz), Spain
#
# NOTE: This version of CTK is a fork re-licensed by its author. The
#       mainstream version of CTK is available under a GPLv2 license
#       at the Cherokee Project source code repository.
#

from consts import *
from util import json_dump
from PageCleaner import Postprocess


widget_uniq_id = 1;


class RenderResponse:
    def __init__ (self, html='', js='', headers=[], helps=[]):
        self.html    = html
        self.js      = js
        self.headers = headers[:]
        self.helps   = helps[:]

    def clean_up_headers (self):
        noDupes = []
        [noDupes.append(i) for i in self.headers if not noDupes.count(i)]
        self.headers = noDupes

    def __add__ (self, other):
        assert isinstance(other, RenderResponse)

        # New response obj
        i = RenderResponse()

        # Append the new response
        i.html    = self.html    + other.html
        i.js      = self.js      + other.js
        i.headers = self.headers + other.headers
        i.helps   = self.helps   + other.helps

        # Sort the headers
        i.clean_up_headers()
        return i

    def toStr (self):
        txt = self.html

        for js_header in filter(lambda x: x.startswith('<script'), self.headers):
            txt += '%s\n'%(js_header)
        if self.js:
            txt += HTML_JS_ON_READY_BLOCK %(self.js)

        return Postprocess(txt)

    def toJSON (self):
        tmp = filter (lambda x: x, [x.toJSON() for x in self.helps])
        if tmp:
            help = []
            for e in reduce(lambda x,y: x+y, tmp):
                if not e[0] in [x[0] for x in help]:
                    help.append(e)
        else:
            help = []

        return json_dump({'html':    self.html,
                          'js':      Postprocess(self.js),
                          'headers': self.headers,
                          'helps':   help})


class Widget:
    def __init__ (self):
        global widget_uniq_id;

        widget_uniq_id += 1;
        self.uniq_id = widget_uniq_id;
        self.id      = "widget_%d" %(widget_uniq_id)
        self.binds   = []

    def Render (self):
        render = RenderResponse()

        for event, js in self.binds:
            render.js += "$('#%s').bind('%s', function(event){ %s });\n" %(self.id, event, js)

        return render

    # Javacript events
    #
    def bind (self, event, js):
        self.binds.append ((event, js))

    def JS_to_trigger (self, event, param=None, selector=None):
        if not selector:
            selector = "$('#%s')" %(self.id)

        if param:
            return "%s.trigger('%s', %s);" %(selector, event, param)
        else:
            return "%s.trigger('%s');" %(selector, event)


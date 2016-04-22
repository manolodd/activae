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

from Box import Box
from Table import Table
from Widget import Widget
from RawHTML import RawHTML
from Submitter import Submitter
from Container import Container
from HiddenField import HiddenField
from util import *

HTML_TABLE = """
<div class="propstable">%s</div>
"""

HTML_ENTRY = """
<div class="entry" id="%(id)s" %(props)s>
   <div class="title">%(title)s</div>
   <div class="widget">%(widget_html)s</div>
   <div class="comment">%(comment)s</div>
   <div class="after"></div>
</div>
"""

HEADERS = ['<link rel="stylesheet" type="text/css" href="/CTK/css/CTK.css" />']


class PropsTableEntry (Widget):
    """Property Table Entry"""

    def __init__ (self, title, widget, comment, props=None):
        Widget.__init__ (self)

        self.title   = title
        self.widget  = widget
        self.comment = comment
        self.props   = ({}, props)[bool(props)]

        if 'id' in self.props:
            self.id = self.props.pop('id')

    def Render (self):
        # Render child
        if self.widget:
            w_rend = self.widget.Render()
        else:
            w_rend = Container().Render()

        w_html = w_rend.html
        w_rend.html = ''

        # Mix both
        render = Widget.Render (self)
        render += w_rend

        props = {'id':           self.id,
                 'props':        props_to_str(self.props),
                 'title':        self.title,
                 'widget_html':  w_html,
                 'comment':      self.comment}

        render.html += HTML_ENTRY %(props)
        return render


class PropsTable (Box):
    """Property Table: Formatting"""

    def __init__ (self, **kwargs):
        Box.__init__ (self, {'class': "propstable"})

    def Add (self, title, widget, comment):
        self += PropsTableEntry (title, widget, comment)


class PropsTableAuto (PropsTable):
    """Property Table: Adds Submitters and constants"""

    def __init__ (self, url, **kwargs):
        PropsTable.__init__ (self, **kwargs)
        self._url      = url
        self.constants = {}

    def AddConstant (self, key, val):
        self.constants[key] = val

    def Add (self, title, widget, comment):
        submit = Submitter (self._url)

        if self.constants:
            box = Container()
            box += widget
            for key in self.constants:
                box += HiddenField ({'name': key, 'value': self.constants[key]})

            submit += box
        else:
            submit += widget

        return PropsTable.Add (self, title, submit, comment)


class PropsAuto (Widget):
    def __init__ (self, url, **kwargs):
        Widget.__init__ (self, **kwargs)
        self._url      = url
        self.constants = {}
        self.entries   = []

    def AddConstant (self, key, val):
        self.constants[key] = val

    def Add (self, title, widget, comment, use_submitter=True):
        # No constants, just the widget
        if not self.constants:
            self.entries.append ((title, widget, comment, use_submitter))
            return

        # Wrap it
        box = Container()
        box += widget
        for key in self.constants:
            box += HiddenField ({'name': key, 'value': self.constants[key]})
        self.entries.append ((title, box, comment, use_submitter))

    def Render (self):
        render = Widget.Render(self)

        for e in self.entries:
            title, widget, comment, use_submitter = e

            id    = self.id
            props = ''

            if use_submitter:
                submit = Submitter (self._url)
                submit += widget
            else:
                submit = widget

            widget_r    = submit.Render()
            widget_html = widget_r.html

            html = HTML_ENTRY %(locals())

            render.html    += html
            render.js      += widget_r.js
            render.headers += widget_r.headers
            render.helps   += widget_r.helps

        render.html     = HTML_TABLE %(render.html)
        render.headers += HEADERS
        return render

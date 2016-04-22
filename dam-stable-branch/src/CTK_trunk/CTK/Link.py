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

from Widget import Widget
from Container import Container
from util import formater

LINK_HTML      = '<a href="%(href)s" id="%(id)s">%(content)s</a>'
LINK_ICON_HTML = '<div id="%(id)s"><span class="ui-icon ui-icon-%(icon)s"></span>%(link)s</div>'


class Link (Container):
    def __init__ (self, href, content=None):
        Container.__init__ (self)
        self.href = href[:]

        if content:
            self += content

    def Render (self):
        render = Container.Render (self)

        props = {'id':      self.id,
                 'href':    self.href,
                 'content': render.html}

        render.html = formater (LINK_HTML, props)
        return render


class LinkIcon (Link):
    def __init__ (self, href="#", icon='newwin', content=None):
        Link.__init__ (self, href)
        self.icon = icon

        if content:
            self += content

    def Render (self):
        render = Link.Render (self)

        props = {'id':   self.id,
                 'icon': self.icon,
                 'link': render.html}

        render.html = formater (LINK_ICON_HTML, props)
        return render


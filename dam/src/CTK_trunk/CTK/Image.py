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

class Image (Widget):
    def __init__ (self, props={}, **kwargs):
        Widget.__init__ (self, **kwargs)
        self.props = props.copy()

    def Render (self):
        if not 'id' in self.props:
            self.props['id'] = self.id

        props = " ".join (['%s="%s"'%(k,self.props[k]) for k in self.props])

        render = Widget.Render (self)
        render.html = '<img %s />' %(props)
        return render

class ImageStock (Image):
    def __init__ (self, name, _props={}):
        props = _props.copy()

        if name == 'del':
            props['src']   = '/CTK/images/del.png'
            props['alt']   = _('Delete')
            props['title'] = _('Delete')

            if 'class' in props:
                props['class'] += ' del'
            else:
                props['class'] = 'del'

            Image.__init__ (self, props)

        elif name == 'on':
            props['src'] = '/CTK/images/on.png'
            props['alt'] = _('Active')
            Image.__init__ (self, props)

        elif name == 'off':
            props['src'] = '/CTK/images/off.png'
            props['alt'] = _('Inactive')
            Image.__init__ (self, props)

        elif name == 'loading':
            props['src'] = '/CTK/images/loader.gif'
            props['alt'] = _('Loading')
            Image.__init__ (self, props)

        elif name == 'tick':
            props['src'] = '/CTK/images/tick.png'
            props['alt'] = _('Enabled')
            Image.__init__ (self, props)

        else:
            assert False, "Unknown stock image: %s" %(name)

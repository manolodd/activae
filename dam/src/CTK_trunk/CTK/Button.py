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
from util import props_to_str

class Button (Widget):
    def __init__ (self, caption="Submit", props={}):
        Widget.__init__ (self)
        self.props = props.copy()

        if 'class' in props:
            self.props['class'] += " button"
        else:
            self.props['class'] = "button"

        if not 'href' in props:
            self.props['href'] = " #"

        self.id      = props.pop('id', "button_%d"%(self.uniq_id))
        self.caption = caption

    # Public interface
    #
    def Render (self):
        id      = self.id
        caption = self.caption
        props   = props_to_str (self.props)

        html = '<a id="%(id)s" %(props)s><span>%(caption)s</span></a>' %(locals())

        render = Widget.Render (self)
        render.html += html

        return render

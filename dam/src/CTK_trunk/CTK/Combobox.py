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
from Server import cfg
from util import props_to_str

class Combobox (Widget):
    def __init__ (self, props, options):
        Widget.__init__ (self)

        self.props    = props.copy()
        self._options = options

        if not 'id' in self.props:
            self.props['id'] = 'Combobox_%s' %(self.uniq_id)
        self.id = self.props['id']

    def Render (self):
        selected = self.props.get('selected')

        def render_str (o):
            if len(o) == 2:
                name, label = o
                props       = {}
            elif len(o) == 3:
                name, label, props = o

            props_str = props_to_str(props)
            if selected and str(selected) == str(name):
                return '<option value="%s" selected="true" %s>%s</option>' % (name, props_str, label)
            else:
                return '<option value="%s" %s>%s</option>' % (name, props_str, label)

        def render_list (o):
            if len(o) == 2:
                name, options = o
                props       = {}
            elif len(o) == 3:
                name, options, props = o

            props_str = props_to_str(props)
            txt = '<optgroup label="%s" %s>' %(name, props_str)
            for o in options:
                txt += render_str (o)
            txt += '</optgroup>'
            return txt

        # Render entries
        content = ''
        for o in self._options:
            if type(o[1]) == str:
                content += render_str (o)
            elif type(o[1]) == list:
                content += render_list (o)
            else:
                raise ValueError

        # Render the container
        header = ''
        for p in filter(lambda x: x!='selected', self.props):
            if self.props[p]:
                header += ' %s="%s"' %(p, self.props[p])
            else:
                header += ' %s' %(p)

        html = '<select%s>%s</select>' %(header, content)

        render = Widget.Render (self)
        render.html += html

        return render


class ComboCfg (Combobox):
    def __init__ (self, key, options, _props={}):
        props = _props.copy()

        # Read the key value
        val = cfg.get_val(key)
        sel = None

        # Look for the selected entry
        for v,k in options:
            if v == val:
                sel = val

        if sel:
            props['selected'] = sel

        # Other properties
        props['name'] = key

        # Init parent
        Combobox.__init__ (self, props, options)

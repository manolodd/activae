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

__author__ = 'Alvaro Lopez Ortega <alvaro@alobbs.com>'

from Widget import Widget
from Container import Container
from Server import cfg
from util import *


HTML = """
<input type="checkbox" id="%(id)s" %(props)s />
"""

class Checkbox (Widget):
    def __init__ (self, props={}):
        # Sanity check
        assert type(props) == dict

        Widget.__init__ (self)
        self._props = props.copy()

    def Render (self):
        # Deal with a couple of exceptions
        new_props = self._props.copy()

        if new_props.has_key('checked') and int(new_props.pop('checked')):
            new_props['checked'] = "checked"

        if new_props.has_key('disabled') and int(new_props.pop('disabled')):
            new_props['disabled'] = None

        # Render the widget
        render = Widget.Render (self)
        render.html += HTML % ({'id':    self.id,
                                'props': props_to_str (new_props)})
        return render


class CheckCfg (Checkbox):
    def __init__ (self, key, default, props=None):
        # Sanity checks
        assert type(key) == str
        assert type(default) == bool
        assert type(props) in (type(None), dict)

        if not props:
            props = {}

        # Read the key value
        val = cfg.get_val(key)
        if not val:
            props['checked'] = "01"[bool(int(default))]
        elif val.isdigit():
            props['checked'] = "01"[bool(int(val))]
        else:
            assert False, "Could not handle value: %s"%(val)

        # Other properties
        props['name'] = key

        # Init parent
        Checkbox.__init__ (self, props)


class CheckboxText (Checkbox):
    def __init__ (self, props=None, text='Enabled'):
        Checkbox.__init__ (self, props)
        self.text = text

    def Render (self):
        render = Checkbox.Render (self)
        render.html = '<div id="%s" class="checkbox-text">%s %s</div>' %(self.id, render.html, self.text)
        return render


class CheckCfgText (CheckCfg):
    def __init__ (self, key, default, text='Enabled', props=None):
        assert type(default) == bool
        assert type(text) == str
        assert type(props) in (dict, type(None))

        CheckCfg.__init__ (self, key, default, props)
        self.text = text

    def Render (self):
        render = CheckCfg.Render (self)
        render.html = '<div id="%s" class="checkbox-text">%s %s</div>' %(self.id, render.html, self.text)
        return render

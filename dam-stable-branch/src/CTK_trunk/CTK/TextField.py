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

from RawHTML import RawHTML
from Widget import Widget
from Server import cfg

HEADER = [
    '<script type="text/javascript" src="/CTK/js/jquery.form-defaults.js"></script>'
]


class TextField (Widget):
    def __init__ (self, props=None):
        Widget.__init__ (self)
        self.type = "text"
        self.id   = 'widget%d'%(self.uniq_id)

        if props:
            self._props = props
        else:
            self._props = {}

        if not 'id' in self._props:
            self._props['id'] = self.id

    def __get_input_props (self):
        render = ''
        for prop in self._props:
            render += " %s" %(prop)
            value = self._props[prop]
            if value:
                render += '="%s"' %(str(value))
        return render

    def __get_error_div_props (self):
        render = ' id="error_%s"' % (self.id)
        if self._props.get('name'):
            render += ' key="%s"' %(self._props.get('name'))
        return render

    def Render (self):
        # Watermark
        js = ''

        if self._props.get('optional'):
            optional_string = self._props.get('optional_string', _("Optional"))
            js += "$('#%s').DefaultValue('optional-grey','%s');" %(self.id, optional_string)

            if not self._props.get('class'):
                self._props['class'] = 'optional'
            else:
                self._props['class'] += ' optional'

        # Render the text field
        html = '<input type="%s"%s />' %(self.type, self.__get_input_props())

        # Render the error reporting field
        html += '<div class="error"%s></div>' %(self.__get_error_div_props())

        render = Widget.Render (self)
        render.html    += html
        render.js      += js
        render.headers += HEADER

        return render

    def JS_to_clean (self):
        return "$('#%s').attr('value', '');" %(self.id)
    def JS_to_focus (self):
        return "$('#%s').blur(); $('#%s').focus();" %(self.id, self.id)


class TextFieldPassword (TextField):
    def __init__ (self, *a, **kw):
        TextField.__init__ (self, *a, **kw)
        self.type = "password"


class TextCfg (TextField):
    def __init__ (self, key, optional=False, props={}):
        # Sanity checks
        assert type(key) == str
        assert type(optional) == bool
        assert type(props) in (type(None), dict)

        props = props.copy()

        # Read the key value
        val = cfg.get_val(key)
        if val:
            props['value'] = val

        if optional:
            props['optional'] = True

        # Other properties
        props['name'] = key

        # Init parent
        TextField.__init__ (self, props)


JS = """
$("#%(id)s")

.bind ("blur", function (event){
    var self  = $(this);
    var value = self.val();

    if (value != self.data('last_value')) {
       $("#activity").show();

       $.ajax ({type:     'POST',
                dataType: 'json',
                url:      '%(url)s',
                data:     '%(key)s='+value,
	 success: function (data) {
            self.data('last_value', value);

            var name = self.attr('name');
	    for (var key in data['updates']) {
               if (key == name) {
                  self.val (data['updates'][key]);
                  break;
               }
            }
         },
         error: function() {
            event.stopPropagation();
            self.val (self.data('last_value'));
         },
         complete: function (XMLHttpRequest, textStatus) {
	    $("#activity").fadeOut('fast');
         }
       });
    }
})

.data ('last_value', "%(value)s")

.bind ("keypress", function(event){
    if (event.keyCode == 13) {
        focus_next_input (this);
    }
});
"""

class TextCfgAuto (TextCfg):
    def __init__ (self, key, url, optional=False, props=None):
        self.key = key
        self.url = url
        TextCfg.__init__ (self, key, optional, props)

    def Render (self):
        value = cfg.get_val (self.key, '')

        render = TextCfg.Render(self)
        render.js += JS %({'id':    self.id,
                           'url':   self.url,
                           'key':   self.key,
                           'value': value})
        return render

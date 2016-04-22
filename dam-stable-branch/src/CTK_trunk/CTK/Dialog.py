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

import JS
from Container import Container
from Proxy import Proxy
from Server import get_scgi
from Image import ImageStock
from Box import Box
from PageCleaner import Uniq_Block
from util import props_to_str


HEADERS = [
    '<link type="text/css" href="/CTK/css/CTK.css" rel="stylesheet" />',
    '<script type="text/javascript" src="/CTK/js/jquery-ui-1.7.2.custom.min.js"></script>'
]

DIALOG_HTML = """
<div id="%(id)s" title="%(title)s" %(div_props)s>
%(content)s
</div>
"""

DIALOG_JS = """
var dialog_obj = $("#%(id)s");

/* Initialize */
dialog_obj.dialog (%(dialog_props)s);

/* Events */
dialog_obj.bind ('dialogopen', function(event, ui){
   $('.ui-dialog-buttonpane :button').each (function(){
       var html = $(this).html();
       if (! html || html.indexOf('<span') != 0) {
          $(this).wrapInner('<span class=\"button-outter\"><span class=\"button-inner\"></span></span>');
       }
   });
});

/* Positioning */
dialog_obj.dialog ('option', 'position', ['center', 85]);
"""

def py2js_dic (d):
    js_pairs = []

    for key in d:
        val = d[key]
        if type(val) == bool:
            js_pairs.append ("'%s': %s" %(key, ('false', 'true')[val]))
        elif type(val) == int:
            js_pairs.append ("'%s': %d" %(key, val))
        elif type(val) == str:
            if '/* code */' in val:
                js_pairs.append ("'%s': %s" %(key, val))
            else:
                js_pairs.append ("'%s': '%s'" %(key, val))
        else:
            assert false, "Unknown data type"

    return "{%s}" % (", ".join(js_pairs))


class Dialog (Container):
    def __init__ (self, js_props={}, props={}):
        Container.__init__ (self)

        self.js_props = js_props.copy()
        self.props    = props.copy()
        self.id       = 'dialog%d'%(self.uniq_id)
        self.title    = self.js_props.pop('title', '')
        self.buttons  = []

        # Defaults
        if 'modal' not in self.js_props:
            self.js_props['modal'] = True
        if 'resizable' not in self.js_props:
            self.js_props['resizable'] = False
        if 'autoOpen' not in self.js_props:
            self.js_props['autoOpen'] = False
        if 'draggable' not in self.js_props:
            self.js_props['draggable'] = False

        # Special cases
        if not self.js_props['autoOpen']:
            if 'class' in self.js_props:
                self.js_props['class'] += ' dialog-hidden'
            else:
                self.js_props['class'] = 'dialog-hidden'

            if 'style' in self.props:
                self.props['style'] += ' display:none;'
            else:
                self.props['style'] = 'display:none;'

    def AddButton (self, caption, action):
        self.buttons.append ((caption, action))

    def Render (self):
        # Build buttons
        if self.buttons:
            self.js_props['buttons'] = self._render_buttons_property()

        # Render
        render       = Container.Render (self)
        dialog_props = py2js_dic (self.js_props)
        div_props    = props_to_str (self.props)

        props = {'id':           self.id,
                 'title':        self.title,
                 'content':      render.html,
                 'dialog_props': dialog_props,
                 'div_props':    div_props}

        html = DIALOG_HTML %(props)
        js   = DIALOG_JS   %(props)

        render.html     = html
        render.js      += js
        render.headers += HEADERS

        return render

    def _render_buttons_property (self):
        buttons_js = []

        # Render the button entries
        for tmp in self.buttons:
            button_caption, action = tmp
            tmp = '"%(button_caption)s": function() {'
            if action == "close":
                tmp += '$(this).dialog("close");'
            elif action[0] == '/':
                tmp += 'window.location.replace("%(action)s")'
            else:
                tmp += action
            tmp += '}'
            buttons_js.append (tmp%(locals()))

        # Add the property
        js = '/* code */ { %s }' %(','.join(buttons_js))
        return js

    def JS_to_show (self):
        return "$('#%s').show().dialog('open');" % (self.id)

    def JS_to_close (self):
        return " $('#%s').dialog('close');" % (self.id)

    def JS_to_trigger (self, event, _params=[]):
        props = {'id': self.id, 'event': event}

        tmp = ["type: '%s'"%(event)]
        for p in _params:
            assert type(p) == tuple and len(p) == 2
            tmp.append ('%s:%s' %(p[0],p[1]))

        props['details'] = ','.join(tmp)
        return "$('#%(id)s .submitter').trigger({%(details)s});" %(props)


class DialogProxy (Dialog):
    def __init__ (self, url, props={}):
        Dialog.__init__ (self, props.copy())

        scgi = get_scgi()
        self += Proxy (scgi.env['HTTP_HOST'], url)


class DialogProxyLazy (Dialog):
    def __init__ (self, url, _props={}):
        # Properties
        props = _props.copy()
        Dialog.__init__ (self, props)

        # Widget content
        img = ImageStock('loading', {'class': 'no-see'})

        box = Box({'class': 'dialog-proxy-lazy-loader'})
        box += img
        self += box

        # Event
        self.bind ('dialogopen', "$('#%s').show();" %(img.id) + \
                                 JS.Ajax(url, type = 'GET',
                                         success = '$("#%s").html(data);'%(box.id)))


class Dialog2Buttons (Dialog):
    def __init__ (self, props, button_name, button_action):
        Dialog.__init__ (self, props.copy())
        self.AddButton (button_name, button_action)
        self.AddButton (_('Close'), "close")

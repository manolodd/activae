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
from Image import ImageStock

HTML = """
<div id="%(id)s" %(props)s>
  %(on_html)s
  %(off_html)s
  <input id="hidden_%(id)s" name="%(id)s" type="hidden" value="%(value)s" />
</div>
"""

JS = """
/* On click
 */
$('#%(id)s').click (function() {
   var self   = $(this);
   var hidden = self.find ('input:hidden');
   var val    = hidden.val();

   if (val == "0") {
       hidden.val("1");
       self.find('#%(on_id)s').show();
       self.find('#%(off_id)s').hide();
   } else {
       hidden.val("0");
       self.find('#%(off_id)s').show();
       self.find('#%(on_id)s').hide();
   }

   self.trigger({'type': "changed", 'value': val});
   return false;
});

/* Init
 */
var self = $('#%(id)s');
if ("%(value)s" == "1") {
   self.find('#%(on_id)s').show();
   self.find('#%(off_id)s').hide();
} else {
   self.find('#%(off_id)s').show();
   self.find('#%(on_id)s').hide();
}
"""


class ToggleButtonImages (Widget):
    def __init__ (self, on, off, active=True, props={}):
        Widget.__init__ (self)
        self.props      = props.copy()
        self.active     = active
        self.widget_on  = on
        self.widget_off = off

        if 'class' in props:
            self.props['class'] += " togglebutton"
        else:
            self.props['class'] = "togglebutton"

        self.id = props.pop('id', "togglebutton_%d"%(self.uniq_id))

    # Public interface
    #
    def Render (self):
        id      = self.id
        props   = props_to_str (self.props)
        on_id   = self.widget_on.id
        off_id  = self.widget_off.id
        value   = "01"[int(self.active)]

        # Render embedded images
        render_on  = self.widget_on.Render()
        render_off = self.widget_off.Render()
        on_html  = render_on.html
        off_html = render_off.html

        # Render
        render = Widget.Render (self)
        render.html += HTML %(locals())
        render.js   += JS   %(locals())

        # Merge the image renders, just in case
        render_on.html  = ''
        render_off.html = ''
        render += render_on
        render += render_off

        return render

class ToggleButtonOnOff (ToggleButtonImages):
    def __init__ (self, active=True, props={}):
        ToggleButtonImages.__init__ (self,
                                     ImageStock('on',  {'title': _("Disable")}),
                                     ImageStock('off', {'title': _("Enable")}),
                                     active, props.copy())


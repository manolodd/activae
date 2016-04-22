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
from Button import Button
from RawHTML import RawHTML
from Container import Container
from TextField import TextField
from PageCleaner import Uniq_Block

HEADER = ['<script type="text/javascript" src="/CTK/js/Submitter.js"></script>']

# Placeholder
HTML = """
<div id="%(id)s" class="submitter">
 %(content)s
 <div class="notice"></div>
</div>
"""

# Initialization
JS_INIT = """
  $("#%(id)s").Submitter ('%(url)s', '%(optional)s')
          .bind('submit', function() {
                $(this).data('submitter').submit_form();
          });
"""

# Focus on the first <input> of the page
JS_FOCUS = """
  if ($("input:first").hasClass('filter')) {
      $("input:first").next().focus();
  } else {
      $("input:first").focus();
  }
  $("#activity").hide();
"""

class Submitter (Container):
    def __init__ (self, submit_url):
        Container.__init__ (self)
        self.url = submit_url
        self.id  = "submitter%d" %(self.uniq_id)

    def Render (self):
        # Child render
        render = Container.Render(self)

        # Own render
        props = {'id':       self.id,
                 'id_uniq':  self.uniq_id,
                 'url':      self.url,
                 'content':  render.html,
                 'optional': _('Optional')}

        js = JS_INIT %(props) + Uniq_Block (JS_FOCUS %(props))

        render.html     = HTML %(props)
        render.js       = js + render.js
        render.headers += HEADER

        render.clean_up_headers()
        return render

    def JS_to_submit (self):
        return "$('#%s').data('submitter').submit_form();" %(self.id)
        #return "submit_%d.submit_form (submit_%d);" % (self.uniq_id, self.uniq_id)


FORCE_SUBMIT_JS = """
$("#%(id)s").click(function() {
    /* Figure the widget number of the Submitter */
    var submitter = $(this).parents('.submitter');
    $(submitter).data('submitter').submit_form();
});
"""

class SubmitterButton (Button):
    def __init__ (self, caption="Submit"):
        Button.__init__ (self, caption)

    def Render (self):
        render = Button.Render(self)
        render.js += FORCE_SUBMIT_JS %({'id': self.id})
        return render

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

import string
from Widget import Widget

# WARNING
# -------
# This class currently depends on a modified version of jQuery-UI. By
# some reason I cannot still quite comprehend, there is no way to stop
# jQuery's tab class from removing the active tab cookie when its
# destroy() method is executed.
#
# The following patch has been applied to our jquery-ui copy. It just
# removes three lines from the destroy() method, so the cookie is not
# wiped out:
#
# - if (o.cookie) {
# -   this._cookie(null, o.cookie);
# - }
#
# We ought to wrap the method to store the cookie value before the
# method execution, and to restore it afterwards. In that way we could
# use a standard version of jQuery-UI.


HEADER = [
    '<link type="text/css" href="/CTK/css/CTK.css" rel="stylesheet" />',
    '<script type="text/javascript" src="/CTK/js/jquery-ui-1.7.2.custom.min.js"></script>',
    '<script type="text/javascript" src="/CTK/js/jquery.cookie.js"></script>'
]

HTML = """
<div id="tab_%(id)s">
 %(html)s
</div> <!-- %(id)s -->
"""

HTML_UL = """<ul class="ui-tabs-nav">%(li_tabs)s</ul>"""
HTML_LI = """<li><a href="#%(tab_ref)s"><span>%(title)s</span></a></li>"""

HTML_TAB = """
<div id="%(tab_ref)s">
  %(widget)s
</div> <!-- %(tab_ref)s -->
"""

JS_INIT = """
$("#tab_%(id)s").each(function() {
   var this_tab   = $(this);
   var path_begin = location.href.indexOf('/', location.href.indexOf('://') + 3);
   var path       = location.href.substring (path_begin);

   this_tab.find("ul li:first").addClass("ui-tabs-first");
   this_tab.find("ul li:last").addClass("ui-tabs-last");


   this_tab.tabs({
      cookie: {path: path,
               name: 'opentab'}
   }).bind('tabsselect', function(event, ui) {
      /* Selection fixes for the tab theme */
      var tabslen  = this_tab.tabs('length');
      var nprevtab = parseInt(get_cookie('opentab')) + 2;
      var nnexttab = parseInt(ui.index) +2;

      if (nprevtab < tabslen) {
         this_tab.find("li:nth-child("+ nprevtab +")").removeClass("ui-tabs-selected-next");
      } else {
         this_tab.find("li:nth-child("+ nprevtab +")").removeClass("ui-tabs-selected-next-last");
      }

      if (nnexttab < tabslen) {
         this_tab.find("li:nth-child("+ nnexttab +")").addClass("ui-tabs-selected-next");
      } else {
         this_tab.find("li:nth-child("+ nnexttab +")").addClass("ui-tabs-selected-next-last");
      }
   });

   if (this_tab.tabs('option', 'selected') == 0) {
      if (this_tab.tabs('length') == 2) {
         this_tab.find("li:nth-child(2)").addClass("ui-tabs-selected-next-last");
      } else {
         this_tab.find("li:nth-child(2)").addClass("ui-tabs-selected-next");
      }
   }

   var ninitab = parseInt(get_cookie('opentab')) + 2;
   if (ninitab < this_tab.tabs('length')) {
         this_tab.find("li:nth-child("+ ninitab +")").addClass("ui-tabs-selected-next");
   } else {
         this_tab.find("li:nth-child("+ ninitab +")").addClass("ui-tabs-selected-next-last");
   }

});
"""


class Tab (Widget):
    def __init__ (self, props=None):
        Widget.__init__ (self)
        self._tabs  = []

        if props:
            self._props = props
        else:
            self._props = {}

        if not 'id' in self._props:
            self._props['id'] = 'widget%d'%(self.uniq_id)

    def Add (self, title, widget):
        assert type(title) == str
        assert isinstance(widget, Widget)

        self._tabs.append ((title, widget))

    def Render (self):
        render = Widget.Render(self)
        id     = self._props['id']

        ul_html  = ''
        tab_html = ''

        num  = 1
        for title, widget in self._tabs:
            r = widget.Render()

            # Keep record of dependencies
            render.js      += r.js
            render.headers += r.headers
            render.helps   += r.helps

            tab_ref = ''
            for c in title:
                if c in string.letters + string.digits:
                    tab_ref += c
                else:
                    tab_ref += '_'
            tab_ref += '-%d' %(num)

            # Render <ul>
            props = {'id':      id,
                     'tab_ref': tab_ref,
                     'widget':  r.html,
                     'title':   title}

            ul_html  += HTML_LI  %(props)
            tab_html += HTML_TAB %(props)

            num  += 1

        # Render the whole thing
        tmp  = HTML_UL %({'li_tabs': ul_html})
        tmp += tab_html

        html = HTML %({'id':   id,
                       'html': tmp})

        props = {'id':   id,
                 'tabs': html}

        render.html     = html
        render.js      += JS_INIT %(props)
        render.headers += HEADER

        return render

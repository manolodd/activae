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
from Widget import Widget
from Server import publish
from util import props_to_str

HTML = """
<div id="%(id)s" %(props)s>
  %(content)s
</div>
"""

REFRESHABLE_UPDATE_JS = """
$.ajax({
   type:    'GET',
   url:     '%(url)s',
   async:   true,
   success: function(msg){
      %(selector)s.html(msg);
      %(on_success)s
   }
});
"""

def render_plain_html (build_func, **kwargs):
    render = build_func (**kwargs)
    return render.toStr()


class Refreshable (Widget):
    def __init__ (self, _props={}):
        Widget.__init__ (self)

        assert 'id' in _props, "Property 'id' must be provided"

        self.props      = _props.copy()
        self.id         = self.props.pop('id')
        self.url        = "/refreshable/%s" %(self.id)
        self.build_func = None

    def register (self, build_func=None, **kwargs):
        self.build_func = build_func
        self.params     = kwargs

        # Register the public URL
        publish (self.url, render_plain_html, build_func=build_func, **kwargs)

    def Render (self):
        render = self.build_func (**self.params)

        props = {'id':      self.id,
                 'props':   props_to_str(self.props),
                 'content': render.html}

        render.html = HTML %(props)
        return render

    def JS_to_refresh (self, on_success='', selector=None):
        if not selector:
            selector = "$('#%s')" %(self.id)

        props = {'selector':   selector,
                 'url':        self.url,
                 'on_success': on_success}
        return REFRESHABLE_UPDATE_JS %(props)


JS_URL_LOAD = """
var refresh = $('#%(id)s');
refresh.data('url', "%(url)s");

if ("%(url)s".length > 0) {
  $.ajax({type: "GET", url: "%(url)s", async: true,
     success: function(msg){
        refresh.html(msg);
     }
  });
}
"""

JS_URL_INIT = """
refresh.bind('refresh_goto', function(event) {
  var refresh = $('#%(id)s');
  refresh.data('url', "%(url)s", event.goto);

  $.ajax({type: "GET", url: event.goto, async: true,
     success: function(msg){
        refresh.html(msg);
     }
  });
});
"""

class RefreshableURL (Widget):
    def __init__ (self, url='', _props={}):
        Widget.__init__ (self)

        # Properties
        props = _props.copy()
        if 'class' in props:
            props['class'] += ' refreshable-url'
        else:
            props['class'] = 'refreshable-url'

        self.props = props
        self.url   = url

    def Render (self):
        props = {'id':      self.id,
                 'url':     self.url,
                 'props':   props_to_str(self.props),
                 'content': ''}

        render = Widget.Render (self)
        render.html += HTML %(props)
        render.js   += JS_URL_LOAD %(props)
        render.js   += JS_URL_INIT %(props)
        return render

    def JS_to_load (self, url):
        props = {'id':  self.id,
                 'url': url}
        return JS_URL_LOAD %(props)

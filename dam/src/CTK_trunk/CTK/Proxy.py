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
from Server import publish, get_scgi

from httplib import HTTPConnection

HTML = """
<div id="%(id_widget)s"></div>
"""

JAVASCRIPT = """
$.ajax({
   url:     "%(proxy_url)s",
   type:    "GET",
   async:   %(async_bool)s,
   success: function(msg){
      $('#%(id_widget)s').html(msg);
   }
});
"""

class ProxyRequest:
   def __call__ (self, host, req):
      conn = HTTPConnection (host)
      conn.request ("GET", req)
      r = conn.getresponse()
      return r.read()


class Proxy (Widget):
    def __init__ (self, host, req, props=None):
        Widget.__init__ (self)
        self._url_local = '/proxy_widget_%d' %(self.uniq_id)

        if props:
            self.props = props
        else:
            self.props = {}

        if host == None:
           scgi = get_scgi()
           host =scgi.env['HTTP_HOST']

        self._async = self.props.pop('async', True)
        self._id    = 'widget%d'%(self.uniq_id)

        # Register the proxy path
        publish (self._url_local, ProxyRequest, host=host, req=req)

    def Render (self):
       render = Widget.Render(self)

       props = {'id_widget':  self._id,
                'proxy_url':  self._url_local,
                'async_bool': ['false','true'][self._async]}

       render.html += HTML       %(props)
       render.js   += JAVASCRIPT %(props)

       return render

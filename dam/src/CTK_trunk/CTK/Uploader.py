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

import os
import tempfile
from cgi import FieldStorage

from Server import publish, get_scgi
from Widget import Widget
from PageCleaner import Uniq_Block


HEADERS = [
    '<script type="text/javascript" src="/CTK/js/jquery.uploadProgress.js"></script>'
]

CSS = """
<style type="text/css">
.bar {
  width: 300px;
}

#progress {
  background: #eee;
  border: 1px solid #222;
  margin-top: 20px;
}

#progressbar {
  width: 0px;
  height: 24px;
  background: #333;
}
</style>
"""

HTML = """
 <form id="%(id)s_form" enctype="multipart/form-data" action="%(upload_url)s" method="post">
   <input name="file" type="file"/>
   <input type="submit" value="Upload"/>
 </form>

 <div id="uploading_%(id)s">
    <div id="progress" class="bar">
       <div id="progressbar">&nbsp;</div>
    </div>
 </div>
 <div id="%(id)s_percents"></div>
"""

JS = """
$('#%(id)s_form').uploadProgress({
	/* scripts locations for safari */
	jqueryPath:         "/CTK/js/jquery-1.3.2.min.js",
	uploadProgressPath: "/CTK/js/jquery.uploadProgress.js",
        progressBar:        "#uploading_%(id)s #progressbar",
        progressUrl:        "/upload_report/",
	interval:           2000,
	uploading:          function(upload) {$('#%(id)s_percents').html(upload.percents+'&#37;');},
        start:              function(upload) {$('#%(id)s_form').hide('slow');}
});
"""

# Field Storage classes
#
class FieldStorage_Direct(FieldStorage):
    def __init__ (self, fp=None, headers=None, outerboundary="",
                  environ=os.environ, keep_blank_values=0, strict_parsing=0):
        self.environ = environ
        FieldStorage.__init__ (self, fp, headers, outerboundary,
                               environ, keep_blank_values, strict_parsing)

    def make_file (self, binary=None):
        target_dir  = self.environ.get('CTK_hack__target_path')
        target_path = os.path.join (target_dir, self.filename)
        return open (target_path, 'w+b')


class FieldStorage_Temporal (FieldStorage):
    def __init__ (self, fp=None, headers=None, outerboundary="",
                  environ=os.environ, keep_blank_values=0, strict_parsing=0):
        self.environ = environ
        FieldStorage.__init__ (self, fp, headers, outerboundary,
                               environ, keep_blank_values, strict_parsing)

    def make_file (self, binary=None):
        os_fd_str  = self.environ.get('CTK_hack__os_fd')
        return os.fdopen (int(os_fd_str), 'w+b')


# Internal Proxy
#
class UploadRequest:
   def __call__ (self, handler, target_dir, params, direct):
       scgi = get_scgi()

       # *REMEMBER*: Do not print the 'form'. Python's cgi module will
       # parse the whole file to memory in order to print it, which is
       # certainly an issue for large file uploads.
       #
       # *NOTE*: The functionality is invoked from the constructor!
       #

       if direct:
           environ = scgi.env.copy()
           environ['CTK_hack__target_path'] = target_dir

           # Receive the POST
           form = FieldStorage_Direct (fp=scgi.rfile, environ=environ, keep_blank_values=1)

           # Callback
           return handler (form['file'].filename, target_dir,
                           form['file'].filename, params)

       # Upload to a temporal file
       os_fd, target_path = tempfile.mkstemp (prefix='CTK_upload_', dir=target_dir)

       environ = scgi.env.copy()
       environ['CTK_hack__os_fd'] = str(os_fd)

       form = FieldStorage_Temporal (fp=scgi.rfile, environ=environ, keep_blank_values=1)
       return handler (form['file'].filename, target_dir, target_path, params)



# Uploader CTK widget
#
class Uploader (Widget):
    def __init__ (self, props=None, params=None, direct=True):
        Widget.__init__ (self)
        self._url_local = '/uploader_widget_%d' %(self.uniq_id)

        if props:
            self.props = props
        else:
            self.props = {}

        self.id = 'uplodaer%d'%(self.uniq_id)
        handler    = self.props.get('handler')
        target_dir = self.props.get('target_dir')

        # Register the uploader path
        publish (self._url_local, UploadRequest,
                 handler=handler, target_dir=target_dir, params=params, direct=direct)

    def Render (self):
        props = {'id':         self.id,
                 'upload_url': self._url_local}

        raw_html  = Uniq_Block(CSS)
        raw_html += HTML

        render = Widget.Render (self)
        render.html    += raw_html %(props)
        render.js      += JS       %(props)
        render.headers += HEADERS

        return render

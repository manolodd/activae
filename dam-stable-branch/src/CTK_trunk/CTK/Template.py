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
import stat
import inspect

from Widget import Widget
from util import formater

class Template (Widget):
    cache = {}

    def __init__ (self, **kwargs):
        Widget.__init__ (self)
        self.filename = None
        self.content  = None
        self.vars     = {}

        if kwargs.has_key('filename'):
            self.filename = kwargs['filename']
        elif kwargs.has_key('content'):
            self.content  = kwargs['content']

    def _content_update (self):
        content = open(self.filename, 'r').read()
        mtime   = os.stat (self.filename)[stat.ST_MTIME]
        Template.cache[self.filename] = {'mtime':   mtime,
                                         'content': content}

    def _content_get (self):
        try:
            cached = Template.cache[self.filename]
            s = os.stat (self.filename)
            mtime = s[stat.ST_MTIME]
            if mtime <= cached['mtime']:
                # Hit
                return cached['content']
        except:
            pass

        # Miss
        if (self.filename and
            os.path.exists (self.filename)):
            self._content_update()
            return Template.cache[self.filename]['content']
        else:
            return self.content

    def __setitem__ (self, key, val):
        self.vars[key] = val

    def __getitem__ (self, key):
        return self.vars.get(key)

    def Render (self):
        content = self._content_get()
        while True:
            prev = content[:]
            content = formater (content, self.vars)

            if content == prev:
                break

        # Get rid of %%s
        return content %({})

    def _figure_vars (self):
        vars = globals()
        vars.update (inspect.currentframe(1).f_locals)
        return vars


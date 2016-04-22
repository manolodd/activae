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

from cgi import parse_qs
from urllib import unquote


class Post:
    def __init__ (self, raw=''):
        self._vars = {}

        tmp = parse_qs (raw, keep_blank_values=1)
        for key in tmp:
            self._vars[key] = []
            for n in range(len(tmp[key])):
                value = tmp[key][n]
                self._vars[key] += [unquote (value)]

    def _smart_chooser (self, key):
        if not key in self._vars:
            return None

        vals = filter(lambda x: len(x)>0, self._vars[key])
        if not len(vals) > 0:
            return self._vars[key][0]

        return vals[0]

    def get_val (self, key, not_found=None):
        tmp = self._smart_chooser(key)
        if not tmp:
            return not_found
        return tmp

    def get_all (self, key, not_found=[]):
        if not key in self._vars:
            return not_found[:]

        return filter(lambda x: len(x)>0, self._vars[key])

    def pop (self, key, not_found=None):
        val = self._smart_chooser(key)
        if val == None:
            return not_found
        if key in self._vars:
            del(self[key])
        return val

    def keys (self):
        return self._vars.keys()

    # Relay on the internal array methods
    #
    def __getitem__ (self, key):
        return self._vars[key]

    def __setitem__ (self, key, val):
        self._vars[key] = val

    def __delitem__ (self, key):
        del (self._vars[key])

    def __len__ (self):
        return len(self._vars)

    def __iter__ (self):
        return iter(self._vars)

    def __str__ (self):
        return str(self._vars)

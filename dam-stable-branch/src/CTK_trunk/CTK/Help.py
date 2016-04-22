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
from Container import Container


class HelpEntry (Widget):
    def __init__ (self, title, ref):
        Widget.__init__ (self)
        self.title = title
        self.ref   = ref

    def Render (self):
        if '://' in self.ref:
            url = self.ref
        else:
            url = "/help/%s.html" %(self.ref)

        render = Widget.Render(self)
        render.html = '<div class="help_entry"><a href="%s" target="cherokee_help">%s</a></div>' %(url, self.title)
        return render

    def __repr__ (self):
         return "<CTK.Help.HelpEntry: '%s', '%s', id=%d>"%(self.title, self.ref, id(self))


class HelpGroup (Widget):
    def __init__ (self, name, group=[]):
        Widget.__init__ (self)
        self.name    = name
        self.entries = []

        for entry in group:
            self += entry

    def __add__ (self, entry):
        assert (isinstance(entry, HelpEntry) or
                isinstance(entry, HelpGroup))

        # Add it
        self.entries.append (entry)
        return self

    def Render (self):
        render = Widget.Render(self)
        for entry in self.entries:
            render += entry.Render()

        render.html = '<div class="help_group" id="help_group_%s">%s</div>' %(self.name, render.html)
        return render

    def __repr__ (self):
        txt = ', '.join([e.__repr__() for e in self.entries])
        return "<CTK.Help.HelpGroup: id=%d, %s>"%(id(self), txt)

    def toJSON (self):
        all = []
        for entry in self.entries:
            if isinstance(entry, HelpEntry):
                all.append ((entry.title, entry.ref))
            else:
                all += entry.toJSON()
        return all


class HelpMenu (Widget):
    def __init__ (self, helps=None):
        Widget.__init__ (self)

        if not helps:
            self.helps = []
        else:
            self.helps = helps[:]

    def __add__ (self, helps):
        if type(helps) == list:
            for entry in helps:
                self._add_single (entry)
        else:
            self._add_single (entry)
        return self

    def _add_single (self, entry):
        assert (isinstance (entry, HelpEntry) or
                isinstance (entry, HelpGroup))
        self.helps.append (entry)

    def Render (self):
        # Empty response
        render = Widget.Render(self)

        # Render the help entries
        for entry in self.helps:
            render.html += entry.Render().html

        # Wrap the list of entries
        render.html = '<div class="help">%s</div>' %(render.html)
        return render


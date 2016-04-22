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
# You may contact the copyright holder at: Fundacion CENATIC, Edificio
# de Servicios Sociales: C/ Vistahermosa, 1, 3ra planta, 06200
# Almendralejo (Badajoz), Spain

import os
import CTK
from Menu import Menu

JS_REDIR = """
<script type="text/javascript">
<!--
window.location = "%s"
//-->
</script>
"""

class Default (CTK.Page):
    def __init__ (self, headers=None, body_id=None, **kwargs):

        srcdir = os.path.dirname (os.path.realpath (__file__))
        theme_file = os.path.join (srcdir, 'theme.html')

        template = CTK.Template(filename=theme_file)
        if body_id:
            template['body_props'] = ' id="%s"'%(body_id)

        CTK.Page.__init__ (self, template, headers, [], **kwargs)

    def Render (self):
        self.AddMenu ()
        return CTK.Page.Render (self)

    def AddMenu (self):
        menu = Menu ()
        html = CTK.Container.Render(menu).html
        self._template['menu'] = html

class Redir (CTK.Page):
    def __init__ (self, redir, headers=None):
        CTK.Page.__init__ (self, headers = headers)
        self += CTK.RawHTML(JS_REDIR % redir)

def test ():
    test_string = 'phony'

    test   = Default (body_id = test_string)
    render = test.Render()
    assert test_string in render
    print '#1 Default(test_string) OK'

    test   = Default ()
    render = test.Render()
    assert len(render)
    print '#2 Default() OK'

    test   = Redir (test_string)
    render = test.Render()
    assert test_string in render
    print '#1 Redir (test_string) OK'

if __name__ == '__main__':
    test()

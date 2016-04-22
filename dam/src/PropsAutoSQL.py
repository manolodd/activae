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

import CTK
from DBSlayer import Query
from PartChooser import PartChooser


class PropsAutoSQL (CTK.PropsAuto):
    def __init__ (self, url, sql_read, *args, **kw):
        CTK.PropsAuto.__init__ (self, url, *args, **kw)

        # SQL
        self.SQL_read   = sql_read
        self.SQL_result = Query(sql_read)

        # Submitter
        self.use_submitter = False
        if url:
            self.use_submitter = True
            
    def Add (self, title, widget, sql_field, desc):
        # Set initial value
        if isinstance (widget, CTK.TextField):
            if sql_field in self.SQL_result:
                widget._props['value'] = self.SQL_result[sql_field][0]
                widget._props['name'] = sql_field

        elif isinstance (widget, CTK.Combobox):
            if sql_field in self.SQL_result:
                widget.props['selected'] = str(self.SQL_result[sql_field][0])
                widget.props['name'] = sql_field

        elif isinstance (widget, PartChooser):
            if sql_field in self.SQL_result:
                widget.props['name'] = sql_field
                widget.props['value'] = self.SQL_result[sql_field][0]

        else:
            assert False, "Unknown type"

        # Add the widget
        return CTK.PropsAuto.Add (self, title, widget, desc, self.use_submitter)


def test ():
    sql   = 'show tables;'
    url   = '/phony/url'
    test  = PropsAutoSQL (url, sql)
    assert test.SQL_read == sql
    print '#1 PropsAutoSQL (url, sql) OK'

    assert 'acl_assets' in str(test.SQL_result.result)
    print '#2 PropsAutoSQL (url, sql) OK'

    test.Add ('Test',  CTK.TextField(), 'test', 'The test')
    render = test.Render().toStr()
    assert 'The test' in render
    print '#3 PropsAutoSQL (url, sql).Add(data_tuple) OK'


if __name__ == '__main__':
    test()

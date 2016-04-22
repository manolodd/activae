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

import CTK
import PageACL
import PageConsume
import Asset
import Collection
from CTK.consts import *
from Widget import *
from Error import *

class DefaultWidget (InterfaceWidget):
    """Produce the general overview"""

    def __init__ (self, **kwargs):
        InterfaceWidget.__init__ (self)
        self.table = CTK.Table()
        self.n     = 1
        title      = [CTK.RawHTML(x) for x in ['Tipo','ID', 'Autor','Título']]
        self.table[(self.n,1)] = title
        self.table.set_header (row=True, num=self.n)
        self  += self.table

    def Add (self, content):
        if isinstance (content, Asset.Asset):
            c_type   = 'Activo'
            link_acl = '%s/asset/%d' % (PageACL.LOCATION, content['id'])
        elif isinstance (content, Collection.Collection):
            c_type = 'Colección'
            link_acl = '%s/collection/%d' % (PageACL.LOCATION, content['id'])
        else:
            raise Invalid

        link_consume = '%s/%s=%d' % (PageConsume.LOCATION,
                                     c_type[0].lower(), content['id'])
        diz = content.get_diz()
        row     = [c_type,
                   LINK_HREF % (link_consume,str(content['id'])),
                   diz['creator'],
                   diz['title'],
                   LINK_HREF % (link_acl,'Editar ACL')]
        entries = [CTK.RawHTML(x) for x in row]
        self.n += 1
        self.table[(self.n, 1)] = entries


def test ():
    import sys

    try:
        asset_id      = sys.argv[1]
        collection_id = sys.argv[2]
        asset         = Asset.Asset(asset_id)
        collection    = Collection.Collection(collection_id)
    except IndexError:
        print 'Required test parameters: asset_id collection_id'
        sys.exit(1)

    test_string = 'phony'

    test   = DefaultWidget()
    asset._tags['Title'] = test_string
    test.Add(asset)
    render = test.Render().toStr()
    assert 'Activo'    in render
    assert test_string in render
    print '#1 DefaultWidget().Add(asset) OK'

    test   = DefaultWidget()
    collection['name'] = test_string
    test.Add(collection)
    render = test.Render().toStr()
    assert 'Colección' in render
    assert test_string in render
    print '#2 DefaultWidget().Add(collection) OK'

    test   = DefaultWidget()
    try:
        test.Add(None)
    except Invalid:
        print '#3 DefaultWidget().Add(None) OK: Invalid exception as expected'


if __name__ == '__main__':
    test()

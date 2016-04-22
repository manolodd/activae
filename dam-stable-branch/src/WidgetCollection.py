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
import Role
import Auth
import Error

import PageCollection
import Collection
from CTK.consts import *
from Widget import *
from ACL import ACL

NOTE_DELETE  = "<p>¿Confirmar eliminación?</p>"

class DefaultWidget (InterfaceWidget):
    """Produce the general overview"""

    def __init__ (self, **kwargs):
        InterfaceWidget.__init__ (self)
        self.table = CTK.Table()
        self.n     = 1
        self.collections_dict = Collection.get_collections_dict()

        title      = [CTK.RawHTML(x) for x in ['ID', 'Nombre', 'Creador']]
        self.table[(self.n,1)] = title
        self.table.set_header (row=True, num=self.n)
        self += self.table
        self.acl = ACL()

    def __get_del_dialog (self,url_params, msg):
        # Link to delete target
        dialog = CTK.Dialog ({'title': "Aviso", 'autoOpen': False})
        dialog += CTK.RawHTML (msg)
        dialog.AddButton ('Cancelar', "close")
        dialog.AddButton ('Borrar',   "%s/%s" %(PageCollection.LOCATION, url_params))

        return dialog


    def Add (self, collection):
        collection_id = collection['id']
        coll = self.collections_dict[collection_id]
        linkname, linkdel = str(collection_id),''

        if collection_id in self.acl.filter_collections ("co" , [collection_id]):
            url      = "%s/edit/%s" % (PageCollection.LOCATION, collection_id)
            linkname = LINK_HREF %(url, collection_id)

        # Delete collection link
        if collection_id in self.acl.filter_collections ("rm" , [collection_id]):
            dialog   = self.__get_del_dialog ("del/%s" %(collection_id), NOTE_DELETE)
            linkdel  = LINK_JS_ON_CLICK %(dialog.JS_to_show(), "Borrar")
            self += dialog

        entries = [CTK.RawHTML(linkname),
                   CTK.RawHTML(coll['name']),
                   CTK.RawHTML(coll['username']),
                   CTK.RawHTML(linkdel)]

        try:
            Auth.check_if_authorized (collection)
            link = LINK_HREF % ("/acl/collection/%d" % (collection['id']), 'Permisos')
            entries.append(CTK.RawHTML(link))
        except Error.Unauthorized:
            entries.append(CTK.RawHTML(''))
            pass


        if collection_id in self.acl.filter_collections ("ed" , [collection_id])\
                and Role.user_has_role (Role.ROLE_EDITOR):
            url  = '%s/edit/%d'%(PageCollection.LOCATION,collection_id)
            link = LINK_HREF%(url, 'Editar')
            entries.append(CTK.RawHTML (link))


        if collection_id in self.acl.filter_collections ("co" , [collection_id]):
            url  = "%s/meta/%s" % (PageCollection.LOCATION, collection_id)
            link = LINK_HREF%(url, 'Metadatos')
            entries.append(CTK.RawHTML (link))


        self.n += 1
        self.table[(self.n, 1)] = entries



class ClaimWidget (InterfaceWidget):
    """Produce the view to allow asset assignment to collections"""
    def __init__ (self, **kwargs):
        InterfaceWidget.__init__ (self)
        self.table = CTK.Table()
        self.n     = 1
        self += self.table
        self.collection_id = kwargs['c_id']

    def Add (self, asset):
        dialog  = DialogWidget(asset)
        self   += dialog
        link    = LINK_JS_ON_CLICK %(dialog.JS_to_show(), "ID#%d" % asset['id'])
        link    = CTK.RawHTML (link)
        title   = CTK.RawHTML (' %s'%asset['title'])
        action  = self._get_action (asset)

        self.n += 1
        self.table[(self.n, 1)] = [action, link, title]

    def _get_action (self, asset):
        flag    = asset['collections_id'] or 0
        c_id    = str(self.collection_id)
        a_id    = str(asset['id'])

        table   = CTK.Container()
        table  += CTK.HiddenField({'name':'asset_id',      'value': a_id})
        table  += CTK.HiddenField({'name':'collection_id', 'value': c_id})
        table  += CTK.Checkbox({'name': 'assigned', 'checked': flag})
        url     = '%s/include' % (PageCollection.LOCATION)
        submit  = CTK.Submitter (url)
        submit += table

        return submit


class DialogWidget (CTK.Dialog):
    """Produce Dialog"""

    def __init__ (self, asset, **kwargs):
        props = {'title': "Activo #%d"%(asset['id']),
                 'autoOpen': False,
                 'draggable': True}

        CTK.Dialog.__init__ (self, props)

        diz   = asset.get_diz()
        self += CTK.RawHTML('<p><img src="%(thumb)s" /></p>'
                            '<p>Título: %(title)s</p>'
                            '<p>Autor: %(creator)s</p>'
                            '<p>Licencia: %(license)s</p>' % diz)

def test ():
    import sys
    import Asset

    try:
        asset_id      = sys.argv[1]
        collection_id = sys.argv[2]
        asset         = Asset.Asset(asset_id)
        collection    = Collection.Collection(collection_id)
        test_string   = 'phony'
        asset._tags['Title'] = test_string
        collection['name']   = test_string
    except IndexError:
        print 'Required test parameters: asset_id collection_id'
        sys.exit(1)

    test   = DialogWidget (asset)
    render = test.Render().toStr()
    assert len(test)
    print '#1 DialogWidget() OK'
    assert 'Título: %s' %test_string in render
    print '#2 DialogWidget() OK'

    try:
        test   = DefaultWidget ()
    except AttributeError: # Expected
        pass
    print '#1 DefaultWidget() OK'

    try:
        test.Add (collection)
    except AttributeError: # Expected
        pass
    print '#2 DefaultWidget().Add(collection) OK'

    test   = ClaimWidget (c_id = 'a=%s' % asset['id'])
    print '#1 ClaimWidget() OK'

    test.Add (asset)
    print '#2 ClaimWidget().Add(asset) OK'

    render = test.Render().toStr()
    assert 'Título: %s'%test_string in render
    print '#3 ClaimWidget().Render() OK'

if __name__ == '__main__':
    test()

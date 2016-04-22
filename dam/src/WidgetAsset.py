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
import Auth
import Role
import PageAsset
import PageUpload
import Error
import Asset

from ACL import ACL
from CTK.consts import *
from Widget import *

NOTE_DELETE  = "<p>¿Confirmar eliminación?</p>"

class PublishWidget (InterfaceWidget):
    """Produces publication overview"""

    def __init__ (self, **kwargs):
        InterfaceWidget.__init__ (self)
        self.table = CTK.Table()
        self.n     = 1
        header     = ['Tipo', 'ID', 'Titulo', 'Fecha', 'Publicado']

        self.table[(self.n,1)] = [CTK.RawHTML(x) for x in header]
        self.table.set_header (row=True, num=self.n)
        self.sect_type = None

        form = CTK.Submitter('%s/publish/apply' % PageAsset.LOCATION)
        form += self.table
        self += form

    def Add (self, asset):
        assert isinstance(asset, Asset.Asset)
        flag = asset['published_flag']
        if not flag: flag = 0

        if self.sect_type != asset['Type']:
            self.sect_type = asset['Type']
            self.n   += 1
            self.table[(self.n,1)] = CTK.RawHTML ("<b>%s</b>" %(self.sect_type))

        linkname  = LINK_HREF %("/consume/a=%s" % (str(asset['id'])), str(asset['id']))
        linktrans = LINK_HREF %("/transcode/%s" % (str(asset['id'])), 'Transcodificar')

        row = [CTK.RawHTML(''),
               CTK.RawHTML(linkname),
               CTK.RawHTML(asset['title']),
               CTK.RawHTML(asset['date_created']),
               CTK.Checkbox ({'name':    'published_'+str(asset['id']),
                              'checked': '%d'%(flag)}),
               CTK.RawHTML(linktrans)]
        self.n +=1
        self.table[(self.n,1)] = row


class DefaultWidget (InterfaceWidget):
    """Produce the view for general overview"""

    def __init__ (self, **kwargs):
        InterfaceWidget.__init__ (self)
        self.table = CTK.Table()
        self.n     = 1

        title      = [CTK.RawHTML(x) for x in ['ID', 'Titulo', 'Tipo']]
        self.table[(self.n,1)] = title
        self.table.set_header (row=True, num=self.n)
        self  += self.table
        self.acl = ACL()


    def Add (self, asset):
        assert isinstance(asset, Asset.Asset)
        asset_id = asset['id']
        linkname, linkdel = str(asset_id),''

        if asset_id in self.acl.filter_assets ("co" , [asset_id]):
            linkname = LINK_HREF %("/consume/a=%s" % (asset_id), asset_id)

        # Delete asset link
        if asset_id in self.acl.filter_assets ("rm" , [asset_id]):
            dialog = CTK.Dialog ({'title': "Eliminar activo #%d?"%(asset_id), 'autoOpen': False})
            dialog += CTK.RawHTML (NOTE_DELETE)
            dialog.AddButton ('Cancelar', "close")
            dialog.AddButton ('Borrar',   "%s/del/%s" %(PageAsset.LOCATION, asset_id))
            linkdel  = LINK_JS_ON_CLICK %(dialog.JS_to_show(), "Borrar")
            self += dialog

        entries = [CTK.RawHTML(linkname),
                   CTK.RawHTML(asset['title']),
                   CTK.RawHTML(asset['Type']),
                   CTK.RawHTML(linkdel)]

        try:
            Auth.check_if_authorized (asset)
            link = LINK_HREF % ("/acl/asset/%d" % (asset['id']), 'Permisos')
            entries.append(CTK.RawHTML(link))
        except Error.Unauthorized:
            pass

        if Role.user_has_role (Role.ROLE_UPLOADER) and\
                asset_id in self.acl.filter_assets ("co" , [asset_id]):
            entries.append(CTK.RawHTML (LINK_HREF%('%s/evolve/parent=%d'  % (PageUpload.LOCATION,asset_id), 'Evolucionar')))
        if Role.user_has_role (Role.ROLE_EDITOR) and\
                asset_id in self.acl.filter_assets ("ed" , [asset_id]):
            entries.append(CTK.RawHTML (LINK_HREF%('%s/edit/%d'    % (PageAsset.LOCATION,asset_id), 'Editar')))


        self.n += 1
        self.table[(self.n, 1)] = entries


class EditWidget (InterfaceWidget):
    """Produce edition overview"""

    def __init__ (self, **kwargs):
        InterfaceWidget.__init__ (self)
        self.table = CTK.Table()
        self.n     = 1

        title      = [CTK.RawHTML(x) for x in ['ID', 'Titulo', 'Tipo']]
        self.table[(self.n,1)] = title
        self.table.set_header (row=True, num=self.n)
        self      += self.table


    def Add (self, asset):
        asset_id = asset['id']
        linkname = LINK_HREF %("/consume/a=%s" % (asset_id), asset_id)
        editlink = LINK_HREF%('%s/edit/%d'     % (PageAsset.LOCATION,asset_id), 'Editar')

        entries = [CTK.RawHTML(linkname),
                   CTK.RawHTML(asset['title']),
                   CTK.RawHTML(asset['Type']),
                   CTK.RawHTML(editlink)]

        self.n += 1
        self.table[(self.n, 1)] = entries


def test ():
    import sys

    try:
        first_asset_id = int(sys.argv[1])
        last_asset_id  = int(sys.argv[2])
    except IndexError:
        print 'Required test parameters: first_asset_id last_asset_id'
        sys.exit(1)

    n = 1
    test_string = 'phony'
    for i in range(first_asset_id, last_asset_id+1):
        test  = PublishWidget()
        asset = Asset.Asset(i)
        asset['title'] = "%s%s" % (test_string,i)
        test.Add(asset)
        render = test.Render().toStr()
        assert 'Transcodificar' in render and "%s%s" % (test_string,i) in render
        print '#%s PublishWidget().Add(asset_%s) OK' % (n,i)
        n+=1

    try:
        test.Add(None)
    except AssertionError:
        print '#%s PublishWidget().Add(None)  OK: Exception as expected'%n


if __name__ == '__main__':
    test()

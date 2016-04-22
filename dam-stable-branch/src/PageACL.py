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
import Page
import Error
import Asset
import Collection
import WidgetLookup
import WorkflowManager

from ACL import ACL
from Widget import *
from WidgetACL import *
from OpLookup import OpLookup
from CTK.consts import *
from consts import *

LOCATION   = '/acl'
ACL_ADMIN_LOOKUP = '/admin/acl/lookup'
URL_APPLY  = '%s/apply' % LOCATION
ADMIN_LINK  = LINK_HREF % ('/admin','Admin')

#
# Show assets/collections
#
def default_user (message = None):
    not_uploader = Auth.assert_is_role (Role.ROLE_UPLOADER)
    if not_uploader:
        return not_uploader

    # Render
    page = Page.Default()
    page += CTK.RawHTML ("<h1>Permisos de activos de usuario</h1>")
    contents = get_user_contents()
    if len(contents):
        page += Paginate(contents, DefaultWidget)
    else:
        page += CTK.RawHTML ("<h2>No hay activos.</h2>")
    if message:
        page += Message(message)

    return page.Render()


def default_admin (message = None, assets = None):
    not_admin    = Auth.assert_is_role (Role.ROLE_ADMIN)
    if not_admin:
        return not_admin

    # Render
    page = Page.Default()
    page += CTK.RawHTML ("<h1>%s: Permisos</h1>" % ADMIN_LINK)
    contents = get_admin_contents()

    main = CTK.Container()
    if len(contents):
        main += Paginate(contents, DefaultWidget)
    else:
        main += CTK.RawHTML ("<h2>No hay activos.</h2>")

    if assets != None:
        page += CTK.RawHTML ("<h2>Activos buscados</h2>")
        page += acl_get_custom (assets)

    tabs = CTK.Tab()
    tabs.Add ('Activos',  main)
    tabs.Add ('Búsqueda', WidgetLookup.get_fields_form(ACL_ADMIN_LOOKUP))
    page += tabs

    if message:
        page += Message(message)
    return page.Render()


def get_user_contents ():
    user_id = Auth.get_user_id()

    # List of collections
    result = Collection.get_collections_list()
    collections  = [c['id'] for c in result if c['creator_id'] == user_id]
    contents = [(Collection.Collection, x) for x in collections]

    # List of assets
    lookup = OpLookup()
    search = {'creator_id': user_id,
              '__order__': 'id'}
    try:
        result = lookup(search)
    except:
        result = []
    contents += [(Asset.Asset, x) for x in result]
    return contents


def get_admin_contents ():
    # List of collections
    collections  = [c['id'] for c in Collection.get_collections_list()]
    contents = [(Collection.Collection, x) for x in collections]

    # List of assets
    lookup = OpLookup()
    search = {'__order__': 'id'}
    try:
        result = lookup(search)
    except:
        result = []
    contents += [(Asset.Asset, x) for x in result]
    return contents


def acl_lookup ():
    result  = urllib.unquote_plus(CTK.request.url)
    result  = result.split('%s/'%ACL_ADMIN_LOOKUP)[1]
    results = result.split(',')
    assets  = []
    for x in results:
        try:
            assets.append(int(x))
        except ValueError:
            pass

    return default_admin (None, assets)


def acl_get_custom (perform):
    if not perform:
        assets = []
    elif type(perform) == list:
        assets = [(Asset.Asset, x) for x in perform]
    else:
        lookup   = OpLookup()
        try:
            results = lookup(perform)
        except:
            results = []
        acl      = ACL()
        results  = acl.filter_assets ("ad" , results)

        assets = [(Asset.Asset, x) for x in results]

    if not assets:
        table = CTK.Table()
        table[(1,1)] = CTK.RawHTML('<h3>La búsqueda no ha devuelto resultados.</h3>')
        return table
    return Paginate (assets, DefaultWidget)


def edit_acl ():
    req        = CTK.request.url.split('/')
    content_id = req[-1]
    c_type     = req[-2]
    try:
        if c_type == 'asset':
            content = Asset.Asset (content_id)
        else:
            content = Collection.Collection (content_id)
        Auth.check_if_authorized (content)
    except:
        return default_user ('Operación no autorizada')

    page = Page.Default()
    page += ACLWidget (content)
    return page.Render()


def get_id_and_type (content):
    if isinstance (content, Asset.Asset):
        c_type = 'asset'
    elif isinstance (content, Collection.Collection):
        c_type = 'collection'
    else:
        raise Error.Invalid
    c_id = str(content['id'])
    return (c_id, c_type)


class ACLWidget (CTK.Container):
    def __init__ (self, content):
        CTK.Container.__init__ (self)

        Auth.check_if_authorized (content)
        c_id, c_type = get_id_and_type (content)

        # List current ones
        refresh = CTK.Refreshable({'id': 'acl_%s' % content['id']})
        refresh.register (lambda: ACLTable(refresh, content).Render())

        self += CTK.RawHTML ("<h2>%s Permisos asociados</h2>" % BACK_LINK)
        self += refresh


class ACLTable (CTK.Container):
    def __init__ (self, refreshable, content,**kwargs):
        CTK.Container.__init__(self)

        self.table = CTK.Table()

        # Header
        row = ['','Añadir', 'Editar', 'Borrar', 'Consumir', 'Rol', 'Usuario']
        self.table[(1,1)] = [CTK.RawHTML(x) for x in row]
        self.table.set_header (row=True, num=1)

        # Entries
        self.n = 2
        acl = ACL()
        entries = acl.acl_generic(content, summarize=False)
        c_id, c_type = get_id_and_type (content)

        for entry in entries:
            user_id = entry.get('user_id')
            role_id = entry.get('role')
            id_acl  = entry.get('id_acl')

            user, role = 'Todos','Todos'
            if user_id: user = Auth.get_user_name (user_id)
            if role_id: role = Role.role_to_name (role_id)
            ad,ed,rm,co = entry['tuple']

            delete = CTK.Image ({'src': '/CTK/images/del.png', 'alt': 'Del'})
            delete.bind('click', CTK.JS.Ajax ('%s/del/%s/%s/%s' % (LOCATION, c_type, c_id, id_acl),
                                              data     = {'id_acl': id_acl},
                                              complete = refreshable.JS_to_refresh()))

            row = [delete] + [CTK.RawHTML(str(x)) for x in [ad,ed,rm,co,role,user]]
            self.table[(self.n,1)] = row
            self.n += 1

        self.add_new (content, refreshable)


    def add_new (self, content, refresh):
        # Add new entry
        c_id, c_type = get_id_and_type (content)
        url          = '%s/%s' % (URL_APPLY, c_type)
        roles        = ["Administrator", "Ingestador", "Editor", "Publicador", "Consumidor"]
        role_options = [(None,'Todos')] + [(Role.name_to_role(x), x) for x in roles]
        user_options = [(None,'Todos')] + Auth.get_users()

        entries = [CTK.RawHTML (''),
                   CTK.Checkbox ({'name': "ad", 'checked':False, 'class':'required'}),
                   CTK.Checkbox ({'name': "ed", 'checked':False, 'class':'required'}),
                   CTK.Checkbox ({'name': "rm", 'checked':False, 'class':'required'}),
                   CTK.Checkbox ({'name': "co", 'checked':False, 'class':'required'}),
                   CTK.Combobox ({'name':'role',    'class':'required'}, role_options),
                   CTK.Combobox ({'name':'user_id', 'class':'required'}, user_options)]

        self.table[(self.n,1)] = entries + [CTK.SubmitterButton('Enviar')]
        self.n += 1

        form = CTK.Submitter(url)
        form += self.table
        form += CTK.HiddenField({'name':'type', 'value':c_type})
        form += CTK.HiddenField({'name':'id',   'value':c_id})
        form.bind ('submit_success', refresh.JS_to_refresh())
        self += form


def del_acl():
    req     = CTK.request.url.split('/')
    id_acl  = req[-1]
    c_id    = req[-2]
    c_type  = req[-3]

    if c_type == 'asset':
        content = Asset.Asset(c_id)
    else:
        content = Collection.Collection (c_id)

    try:
        Auth.check_if_authorized (content)
        acl = ACL()
        acl.delete(content, {'id_acl':id_acl})
    except:
        return {'ret': 'fail'}
    return {'ret': 'ok'}


def apply_acl ():
    # Add a new entry
    c_type = CTK.post.pop('type')
    c_id   = CTK.post.pop('id')

    if c_type == 'asset':
        content = Asset.Asset(c_id)
    elif c_type == 'collection':
        content = Collection.Collection(c_id)
    else:
        return {'ret':'fail'}

    try:
        Auth.check_if_authorized(content)
    except Error.Unauthorized:
        return {'ret': 'fail'}

    ace = {}
    for key in CTK.post:
        if CTK.post[key] != 'None':
            ace[key] = CTK.post[key]

    acl = ACL()
    acl.add(content,ace)
    return {'ret': 'ok'}


def init ():
    """Workflow management"""
    return WorkflowManager.steer (__file__)


def test ():
    from Util import test_page
    test_page (__file__)


CTK.publish ('^%s/?'              % LOCATION, init)
CTK.publish ('^%s/general/?'      % LOCATION, default_user)
CTK.publish ('^/admin/acl/?'                , default_admin)
CTK.publish ('^/admin/acl/lookup/?.*'       , acl_lookup)
CTK.publish ('^%s/asset/\d+'      % LOCATION, edit_acl)
CTK.publish ('^%s/collection/\d+' % LOCATION, edit_acl)
CTK.publish ('^%s/apply/.+'       % LOCATION, apply_acl, method="POST")
CTK.publish ('^%s/del/.+/\d+/\d+' % LOCATION, del_acl)

if __name__ == '__main__':
    test()

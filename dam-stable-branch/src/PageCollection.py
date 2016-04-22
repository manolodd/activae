# -*- coding: utf-8 -*-
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
import Validations
import Page
import Collection
import Asset
import WidgetConsume
import WidgetCollection
import WorkflowManager

from CTK.consts import *
from Widget import *
from ACL import ACL
from DBSlayer import Query
from PropsAutoSQL import PropsAutoSQL
from OpCollection import OpCollection
from OpLookup import OpLookup
from OpAsset import OpAsset
from Util import *

LOCATION     = '/collection'
ADMIN_LINK   = LINK_HREF % ('/admin','Admin')
MENU_LINK    = '%s' %(LINK_HREF%(LOCATION,'Colecciones'))

#
# Validations
#
def __check_collection_id (collection_id):
    q = "SELECT id FROM collections WHERE id ='%s'" % str(collection_id)
    query = Query(q)

    if len(query) != 1:
        raise ValueError, "Colección inválida."
    return collection_id

def __check_collection_name (name):
    name = Validations.not_empty (name)

    collection_id = CTK.request.url.split('/')[-1]
    q = "SELECT name FROM collections WHERE name ='%s' AND id!='%(collection_id)s;" % locals()
    query = Query(q)

    if len(query) != 0:
        raise ValueError, "Ese nombre de colección ya está siendo utilizado."
    return name


def __check_parts (parts_list):
    if not parts_list:
        return []

    numeric_list = Validations.is_numeric_list(parts_list)
    q = "SELECT COUNT(*) FROM assets WHERE id IN (%s);" % (','.join(numeric_list))
    re = Query(q)

    if re['COUNT(*)'][0] != len(numeric_list):
        raise ValueError, "Hay activos invalidas."
    return parts_list


VALIDATIONS = [
    ('name',          __check_collection_name),
    ('parts',         __check_parts),
    ('collection_id', __check_collection_id),
]


#
# Delete collection
#
def del_collection():
    """Delete collection"""

    # Target collection
    collection_id = CTK.request.url.split('/')[-1]
    collection_id = __check_collection_id(collection_id)
    collection    = Collection.Collection (collection_id)
    if not collection['id']:
        return CTK.HTTP_Error(400)

    # Authentication
    acl = ACL()
    deletable = acl.filter_collections ("rm" , [collection_id])
    if not int(collection_id) in deletable:
        return CTK.HTTP_Error(401, 'Operación no autorizada.')

    op  = OpCollection (collection)
    ret = op.delete()

    if ret == False:
        return default ('Error al eliminar colección #%s.'%collection_id)

    return default()

#
# New collection
#
def add_collection_apply ():
    # Authentication
    ok = Role.user_has_roles([Role.ROLE_UPLOADER, Role.ROLE_ADMIN])
    if not ok:
        return CTK.HTTP_Redir('/')

    collection = Collection.Collection()
    collection['creator_id'] = Auth.get_user_id()
    if 'parts' in CTK.post:
        collection._assets = CTK.post['parts']
    if 'name' in CTK.post:
        collection['name'] = CTK.post['name']
    op = OpCollection (collection)
    ret = op.add()

    if ret == True:
        collection_id = op._collection['id']
        return {'ret':      "ok",
                'redirect': '%s/edit/%s'%(LOCATION,collection_id)}
    else:
        return {'ret': "error"}


def add_collection ():
    # Authentication
    ok = Role.user_has_roles([Role.ROLE_UPLOADER, Role.ROLE_ADMIN])
    if not ok:
        return CTK.HTTP_Redir('/')

    table = CTK.PropsTable ()
    table.Add ('Nombre',      CTK.TextField({'name':'name', 'class': "required"}), 'Nombre de la colección')

    form = CTK.Submitter("%s/new/apply"%LOCATION)
    form += table

    page = Page.Default()
    page += CTK.RawHTML ("<h1>%s: A&ntilde;adir colección</h1>"%(MENU_LINK))
    page += form
    return page.Render()


#
# Edit collection
#
def edit_collection_apply():
    # Authentication
    ok = Role.user_has_roles([Role.ROLE_UPLOADER, Role.ROLE_ADMIN])
    if not ok:
        return CTK.HTTP_Redir('/')

    collection_id = CTK.post.pop('collection_id')
    if not collection_id:
        return CTK.HTTP_Error(400)

    acl = ACL()
    editable = acl.filter_collections ("ed" , [collection_id])
    if not int(collection_id) in editable:
        return CTK.HTTP_Error(401)

    collection = Collection.Collection(collection_id)

    if 'name' in CTK.post:
        collection['name'] = CTK.post['name']
    if 'parts' in CTK.post:
        parts = CTK.post['parts']
        if parts:
            parts  = parts.replace(',',' ')
            result = parts.split()
            acl    = ACL()
            result = acl.filter_assets ("co" , result)
            collection['assets'] = [int(x) for x in result]

    oa = OpCollection(collection)
    ret = oa.update()

    if ret == True:
        return {'ret': "ok"}
    else:
        return {'ret': "error"}


def edit_collection():
    # Authentication
    ok = Role.user_has_roles([Role.ROLE_UPLOADER, Role.ROLE_ADMIN])
    if not ok:
        return CTK.HTTP_Redir('/')

    # Table
    url = clear_params (CTK.request.url)
    collection_id = url.split('/')[-1]

    acl = ACL()
    editable = acl.filter_collections ("ed" , [collection_id])
    if not int(collection_id) in editable:
        return CTK.HTTP_Error(401)

    q = "SELECT collections_id, collections.name,"\
        "GROUP_CONCAT(assets.id) AS parts "\
        "FROM assets JOIN collections ON collections.id=collections_id "\
        "WHERE collections_id='%(collection_id)s';" % locals()

    table = PropsAutoSQL ('%s/edit/apply' % LOCATION, q)
    table.AddConstant('collection_id',str(collection_id))
    table.Add ('Nombre',  CTK.TextField(), 'name',  'Nombre de la colección')

    page = Page.Default()
    page += CTK.RawHTML ("<h1>%s: Editar colección</h1>"%(MENU_LINK))
    page += table
    page += ClaimedWidget  (c_id = collection_id)
    page += UnclaimedWidget(c_id = collection_id)
    return page.Render()


class UnclaimedWidget (CTK.Container):
    """Display assets not claimed by any collection"""
    def __init__ (self, **kwargs):
        CTK.Container.__init__ (self)

        lookup   = OpLookup()
        search   = {'collections_id': 'NULL', '__order__': 'id'}

        try:
            result = lookup(search)
        except:
            result = []

        acl      = ACL()
        result   = acl.filter_assets ("co" , result)
        contents = [(Asset.Asset, x) for x in result]

        num = len(contents)
        if num == 0:
            self += CTK.RawHTML ("<h2>No hay activos sin colección asignada</h2>")
        else:
            self += CTK.RawHTML ("<h2>%d activos asignables a la colección</h2>" % num)
            self += Paginate(contents, WidgetCollection.ClaimWidget, **kwargs)


class ClaimedWidget (CTK.Container):
    """Display assets not claimed by any collection"""
    def __init__ (self, **kwargs):
        CTK.Container.__init__ (self)
        collection_id = kwargs['c_id']
        collection = Collection.Collection (collection_id)
        contents = [(Asset.Asset, x) for x in collection['assets']]

        num = len(contents)
        if num == 0:
            self += CTK.RawHTML ("<h2>No hay activos accesibles en esta colección</h2>")
        else:
            self += CTK.RawHTML ("<h2>%d activos asignados a la colección</h2>" % num)
            self += Paginate(contents, WidgetCollection.ClaimWidget, **kwargs)

            # Double pagination could be added with this code if
            # required
            #
            #claimed = WidgetCollection.ClaimWidget(**kwargs)
            #for asset_id in collection['assets']:
            #    asset = Asset.Asset (asset_id)
            #    claimed.Add (asset)
            #self += claimed

#
# Display meta information
#

def show_meta ():
    # Authentication
    collection_id = CTK.request.url.split('/')[-1]
    acl = ACL()
    consumable = acl.filter_collections ("co" , [collection_id])
    if not int(collection_id) in consumable:
        return CTK.HTTP_Error(401)

    # Render
    page = Page.Default()
    page += CTK.RawHTML ("<h1>%s: Metadatos de la colección</h1>"%(MENU_LINK))
    page += DescriptionWidget (collection_id)
    return page.Render()


class DescriptionWidget (CTK.Container):
    def __init__ (self, collection_id, **kwargs):
        CTK.Container.__init__ (self)

        collection = Collection.Collection (collection_id)
        tags = collection.get_tags()

        html = '<h2>ID#%s, %s</h2>\n' % (collection['id'], collection['name'])

        if len(tags)==0:
            html += 'No hay activos asociados.'
            self += CTK.RawHTML(html)
            return

        for key,vals in tags.items():
            vals  = [WidgetConsume.get_meta_link (key, x) for x in vals]
            val   = ', '.join(vals)
            html += '<dt>%s</dt><dd>%s</dd>\n' % (key, val)
        html = '<div class="collection_meta"><dl>\n%s\n</dl></div>' % html
        self += CTK.RawHTML(html)


#
# Include assets into collection
#
def include_apply ():
    collection_id = CTK.post.pop('collection_id')
    asset_id      = CTK.post.pop('asset_id')

    if not collection_id or not asset_id:
        return CTK.HTTP_Error(400)

    acl = ACL()
    addable = acl.filter_collections ("ad" , [collection_id])
    if not int(collection_id) in addable:
        return CTK.HTTP_Error(401, 'Sin permisos para añadir a esta colección')

    asset_id = int(asset_id)
    asset = Asset.Asset (asset_id)
    collection = Collection.Collection (collection_id)
    if asset['collections_id'] and not asset_id in collection:
        return CTK.HTTP_Error(400)

    if asset['collections_id']:
        asset['collections_id'] = None
    else:
        asset['collections_id'] = int(collection_id)

    op = OpAsset(asset)
    ret = op.update()

    if ret == True:
        return {'ret': "ok",
                'redirect': '%s/edit/%s' % (LOCATION, collection_id)}
    else:
        return {'ret': "error"}


#
# Collection list
#

def default (message = None):
    # Authentication
    ok = Role.user_has_roles([Role.ROLE_UPLOADER, Role.ROLE_ADMIN])
    if not ok:
        auth = Auth.Auth()
        if not auth.is_logged_in():
            return CTK.HTTP_Redir('/auth')
        return CTK.HTTP_Redir('/')

    collections_dict = Collection.get_collections_dict()
    collections_lst  = collections_dict.keys()
    acl = ACL()
    collections = acl.filter_collections ("co" , collections_lst)

    # Render
    page = Page.Default()
    if Role.user_has_role (Role.ROLE_ADMIN):
        page += CTK.RawHTML ("<h1>%s: Colecciones</h1>"%(ADMIN_LINK))
    else:
        page += CTK.RawHTML ("<h1>Administración de Colecciones</h1>")
    if len(collections):
        cols = [(Collection.Collection, x) for x in collections]
        page += Paginate (cols, WidgetCollection.DefaultWidget)

    page += CTK.RawHTML ("<p>%s</p>"%LINK_HREF%('%s/new'%LOCATION, 'Añadir colección'))

    if message:
        page += Message (message)

    return page.Render()


def init ():
    """Workflow management"""
    return WorkflowManager.steer (__file__)


def test ():
    from Util import test_page
    test_page (__file__)


CTK.publish ('^%s/?'          % LOCATION, init)
CTK.publish ('^%s/general/?'  % LOCATION, default)
CTK.publish ('^%s/del/.+'     % LOCATION, del_collection)
CTK.publish ('^%s/new$'       % LOCATION, add_collection)
CTK.publish ('^%s/new/apply'  % LOCATION, add_collection_apply, method="POST", validation=VALIDATIONS)
CTK.publish ('^%s/edit/.+'    % LOCATION, edit_collection)
CTK.publish ('^%s/edit/apply' % LOCATION, edit_collection_apply, method="POST", validation=VALIDATIONS)
CTK.publish ('^%s/include'    % LOCATION, include_apply, method="POST")
CTK.publish ('^%s/meta/\d+$'  % LOCATION, show_meta)


if __name__ == '__main__':
    test()


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
import Util
import WorkflowManager

from Widget import *
from CTK.consts import *
from DBSlayer import Query, query_check_success
from PropsAutoSQL import PropsAutoSQL

LOCATION    = '/admin/type'
ADMIN_LINK  = LINK_HREF % ('/admin','Admin')
MENU_LINK   = '%s: %s' % (ADMIN_LINK, LINK_HREF % (LOCATION, 'Tipos'))
NOTE_DELETE = "<p>¿Confirmar eliminación?</p>"

#
# Validations
#
def __check_name (name):
    Validations.not_empty(name)

    q = "SELECT COUNT(*) FROM asset_types WHERE type='%s';" %(name)
    re = Query(q)
    if re['COUNT(*)'][0] != 0:
        raise ValueError, "El tipo de activo ya existe"

    return name


VALIDATIONS = [
    ('type',        __check_name),
    ('description', Validations.not_empty),
]


#
# Delete asset_type
#
def del_type():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    # Target asset_type
    asset_type_id = CTK.request.url.split('/')[-1]

    # Check whether it can be deleted
    q = "SELECT COUNT(*) as total FROM assets WHERE asset_types_id = %(asset_type_id)s;" %(locals())
    re = Query(q)

    usage = re['total'][0]
    if usage != 0:
        subs = Util.get_es_substitutions (usage)
        msg  = ("No se puede eliminar. "
                "Existe%(n)s %(num)d activo%(s)s de este tipo." % subs)
        return default (msg)

    # Delete
    q = "DELETE FROM asset_types WHERE id = %(asset_type_id)s;" %(locals())
    ok = query_check_success (q)

    if not ok:
        return default ('No se pudo realizar la eliminación.')

    return CTK.HTTP_Redir(LOCATION)


#
# New asset_type
#
def new_type_apply():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    # Update the database
    if 'type' in CTK.post:
        q = "INSERT INTO asset_types (type) VALUES ('%s');"%(CTK.post['type'])
        if not query_check_success (q):
            return {'ret': "error"}

    return {'ret':      "ok",
            'redirect': LOCATION}

def new_type():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    table = CTK.PropsTable ()
    table.Add ('Tipo',    CTK.TextField({'name':'type', 'class': "required"}), 'Nombre del tipo de activo')

    form = CTK.Submitter("%s/new/apply"%LOCATION)
    form += table

    page = Page.Default()
    page += CTK.RawHTML ("<h1>%s: A&ntilde;adir tipo</h1>" %(MENU_LINK))
    page += form
    return page.Render()


#
# Edit asset_type
#
def edit_type_apply():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    asset_type_id = CTK.post.pop('asset_typeid')
    if not asset_type_id:
        return CTK.HTTP_Error(406)

    # Update the database
    if 'type' in CTK.post:
        q = "UPDATE asset_types SET type='%s' WHERE id = %s;"%(CTK.post['type'], asset_type_id)
        if not query_check_success (q):
            return {'ret': "error"}

    return {'ret': "ok"}


def edit_type():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    # Table
    asset_type_id = CTK.request.url.split('/')[-1]
    q = "SELECT * FROM asset_types WHERE id = '%(asset_type_id)s';" %(locals())

    table = PropsAutoSQL ('%s/edit/apply'%LOCATION, q)
    table.AddConstant ('asset_typeid', asset_type_id)
    table.Add ('Tipo',    CTK.TextField(), 'type', 'Nombre del tipo de activo')

    page = Page.Default()
    page += CTK.RawHTML ("<h1>%s: Edicion de tipos</h1>" %(MENU_LINK))
    page += table
    return page.Render()


#
# Asset_Type list
#
def default (message = None):
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    # List of types
    q = ("SELECT id,type FROM asset_types;")
    types = Query(q)

    table = CTK.Table()
    title = [CTK.RawHTML(x) for x in ['Tipo de activo']]
    table[(1,1)] = title
    table.set_header (row=True, num=1)

    page = Page.Default()

    n = 2
    for asset_type in types:
        type_id  = types[asset_type]['id']
        name     = types[asset_type]['type']

        # Delete asset_type link
        dialog = CTK.Dialog ({'title': "¿Quieres eliminar %s?"%(name), 'autoOpen': False})
        dialog += CTK.RawHTML (NOTE_DELETE)
        dialog.AddButton ('Cancelar', "close")
        dialog.AddButton ('Borrar',   "%s/del/%s" %(LOCATION, type_id))

        linkdel  = LINK_JS_ON_CLICK %(dialog.JS_to_show(), "Borrar")
        linkname = LINK_HREF %("%s/edit/%s"%(LOCATION, type_id), name)

        table[(n,1)] = [CTK.RawHTML(linkname), CTK.RawHTML(linkdel)]

        page += dialog
        n += 1

    # Render
    page += CTK.RawHTML ("<h1>%s: Tipos</h1>" % ADMIN_LINK)
    page += table
    page += CTK.RawHTML (LINK_HREF%('%s/new'%LOCATION, 'A&ntilde;adir tipo'))
    if message:
        page += Message(message)
    return page.Render()


def init ():
    """Workflow management"""
    return WorkflowManager.steer (__file__)


def test ():
    from Util import test_page
    test_page (__file__)


CTK.publish ('^%s/?'              % LOCATION, init)
CTK.publish ('^%s/general/?'      % LOCATION, default)
CTK.publish ('^%s/del/.+' % LOCATION, del_type)
CTK.publish ('^%s/new$' % LOCATION, new_type)
CTK.publish ('^%s/new/apply$' % LOCATION, new_type_apply, method="POST", validation=VALIDATIONS)
CTK.publish ('^%s/edit/.+' % LOCATION, edit_type)
CTK.publish ('^%s/edit/apply$' % LOCATION, edit_type_apply, method="POST", validation=VALIDATIONS)


if __name__ == '__main__':
    test()


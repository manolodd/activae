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
import Validations
import Page
import WorkflowManager

from Widget import *
from CTK.consts import *
from DBSlayer import Query, query_check_success

ADMIN_PREFIX    = LINK_HREF % ('/admin', 'Admin')
PROFILES_PREFIX = '%s: %s' %(ADMIN_PREFIX, LINK_HREF % ('/admin/profile', 'Profiles'))
NOTE_DELETE = "¿Confirmar eliminación del perfil?"


#
# Validations
#
def __check_profile_name (name):
    Validations.not_empty(name)

    q = "SELECT COUNT(*) FROM profiles WHERE name = '%s';" %(name)
    re = Query(q)
    if re['COUNT(*)'][0] != 0:
        raise ValueError, "Profile ya en uso"

    return name

VALIDATIONS = [
    ('name',        __check_profile_name),
    ('description', Validations.not_empty)
]


#
# Delete profile
#
def del_profile():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    # Target profile
    profile_id = CTK.request.url.split('/')[4]

    # Check whether it can be deleted
    q = "SELECT COUNT(*) FROM users WHERE profile_id = %(profile_id)s;" %(locals())
    re = Query(q)

    usage = re['COUNT(*)'][0]
    if usage != 0:
        return default ("El perfil está en uso por %d usuarios"%(usage))

    # Delete it
    q  = "DELETE FROM profiles_has_roles WHERE profiles_id = %(profile_id)s;" %(locals())
    q += "DELETE FROM profiles WHERE id = %(profile_id)s;" %(locals())
    ok = query_check_success (q)

    return CTK.HTTP_Redir('/admin/profile/')

#
# New user
#
def new_profile_apply():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    name = CTK.post['name']
    desc = CTK.post['description']

    q = ("INSERT INTO profiles (name, description) VALUES ('%s', '%s');") %(name, desc)
    query_check_success (q)

    q = "SELECT id FROM profiles WHERE name = '%s';" %(name)
    re = Query(q)
    new_id = re['id'][0]
    if not new_id:
        return {'ret': "error"}

    q = ("INSERT INTO profiles_has_roles VALUES (%s, %d);") %(new_id, Role.ROLE_CONSUMER)
    query_check_success (q)

    return {'ret':      "ok",
            'redirect': "/admin/profile/%s" %(new_id)}


def new_profile():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    table = CTK.PropsTable()
    table.Add ('Nuevo Profile', CTK.TextField({'name':'name',        'class': "required"}), "Nombre del nuevo profile")
    table.Add ('Descripcion',   CTK.TextField({'name':'description', 'class': "required"}), "Descripcion del profile que se esta dando de alta")

    form = CTK.Submitter("/admin/profile/new/apply")
    form += table

    page = Page.Default()
    page += CTK.RawHTML ("<h1>%s: A&ntilde;adir Profile</h1>" %(PROFILES_PREFIX))
    page += form
    return page.Render()


#
# Edit profile
#
def edit_profile_apply():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    profile_id = CTK.post.pop('profile_id')
    if not profile_id:
        return CTK.HTTP_Error(406)

    # Update: profiles
    sql_values = []
    for key in ['name', 'description']:
        if key in CTK.post:
            sql_values.append ("%s='%s'" %(key, CTK.post[key]))

    if sql_values:
        q = "UPDATE profiles SET %s WHERE id = %s;" %(','.join(sql_values), profile_id)
        if not query_check_success (q):
            return {'ret': "error"}

    # Update: profiles has roles
    q = ''
    for key in CTK.post:
        if not key.startswith('role_'):
            continue

        role_id = key[len('role_'):]

        if bool(int(CTK.post[key])):
            q += ("INSERT INTO profiles_has_roles " +
                  "   VALUES (%(profile_id)s, %(role_id)s);") %(locals())
        else:
            q += ("DELETE FROM profiles_has_roles " +
                  "   WHERE profiles_id = %(profile_id)s AND roles_id = %(role_id)s;") %(locals())
    if q:
        if not query_check_success (q):
            return {'ret': "error"}

    return {'ret': "ok"}


def edit_profile():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    # Table
    profile_id = CTK.request.url.split('/')[3]
    q = ("SELECT *, GROUP_CONCAT(roles_id) " +
         "  FROM profiles, profiles_has_roles " +
         "  WHERE profiles.id = %(profile_id)s AND " +
         "        profiles_has_roles.profiles_id = %(profile_id)s " +
         "  GROUP by profiles.id;") %(locals())

    p = Query(q)
    profile_roles = [int(x) for x in p['GROUP_CONCAT(roles_id)'][0].split(',')]

    table = CTK.PropsAuto ('/admin/profile/apply')
    table.AddConstant ('profile_id', profile_id)
    table.Add ('Nombre',              CTK.TextField ({'name': "name",        'value': p['name'][0]}),        "Nombre del profile")
    table.Add ('Description',         CTK.TextField ({'name': "description", 'value': p['description'][0]}), "Descripcion del profile")
    table.Add ('Role: Administrador', CTK.Checkbox  ({'name': "role_"+str(Role.ROLE_ADMIN),     'checked': '01'[Role.ROLE_ADMIN     in profile_roles]}), "Tiene permisos de administrador")
    table.Add ('Role: Ingestador',    CTK.Checkbox  ({'name': "role_"+str(Role.ROLE_UPLOADER),  'checked': '01'[Role.ROLE_UPLOADER  in profile_roles]}), "Puede dar de alta nuevos activos en el sistema")
    table.Add ('Role: Editor',        CTK.Checkbox  ({'name': "role_"+str(Role.ROLE_EDITOR),    'checked': '01'[Role.ROLE_EDITOR    in profile_roles]}), "Puede editar los activos que ya existen en el sistema")
    table.Add ('Role: Publicador',    CTK.Checkbox  ({'name': "role_"+str(Role.ROLE_PUBLISHER), 'checked': '01'[Role.ROLE_PUBLISHER in profile_roles]}), "Puede publicar activos")
    table.Add ('Role: Consumidor',    CTK.Checkbox  ({'name': "role_"+str(Role.ROLE_CONSUMER),  'checked': '01'[Role.ROLE_CONSUMER  in profile_roles]}), "El usuario puede consumir, ver, y descargar activos")

    page = Page.Default()
    page += CTK.RawHTML ("<h1>%s: Edici&oacute;n profile</h1>" %(PROFILES_PREFIX))
    page += table
    return page.Render()


#
# Profiles list
#
def default (message = None):
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    # List of profiles
    q = "SELECT * FROM profiles;"
    profiles = Query(q)

    table = CTK.Table()
    title = [CTK.RawHTML(x) for x in ['Profile', 'Descripcion', 'Role']]
    table[(1,1)] = title
    table.set_header (row=True, num=1)

    page = Page.Default()

    n = 2
    for profile in profiles:
        # Fetch data
        profile_id   = profiles[profile]['id']
        profile_name = profiles[profile]['name']
        profile_desc = profiles[profile]['description']

        # Role
        q = "SELECT * FROM profiles_has_roles WHERE profiles_id='%s';" %(profile_id)
        roles = Query(q)
        profile_roles_str = ', '.join([Role.role_to_name(roles[x]['roles_id']) for x in roles])

        # Delete profile
        dialog = CTK.Dialog ({'title': "Eliminando profile %s?"%(profile_name), 'autoOpen': False})
        dialog += CTK.RawHTML (NOTE_DELETE)
        dialog.AddButton ('Cancelar', "close")
        dialog.AddButton ('Borrar',   "/admin/profile/del/%s" %(profile_id))

        del_img  = '<img src="/CTK/images/del.png" alt="Borrar"'
        linkdel  = LINK_JS_ON_CLICK %(dialog.JS_to_show(), del_img)
        linkname = LINK_HREF %("/admin/profile/%s"%profile_id, profile_name)

        table[(n,1)] = [CTK.RawHTML(linkname),
                        CTK.RawHTML(profile_desc),
                        CTK.RawHTML(profile_roles_str),
                        CTK.RawHTML(linkdel)]

        page += dialog
        n += 1

    # Render
    page += CTK.RawHTML ("<h1>%s: Administraci&oacute;n de Profiles</h1>" %(ADMIN_PREFIX))
    page += CTK.RawHTML (LINK_HREF%('/admin/profile/new', 'A&ntilde;adir profile'))
    page += table

    if message:
        page += Message (message)

    return page.Render()


def init ():
    """Workflow management"""
    return WorkflowManager.steer (__file__)


def test ():
    from Util import test_page
    test_page (__file__)


CTK.publish ('^/admin/profile/?'              , init)
CTK.publish ('^/admin/profile/general/?'      , default)
CTK.publish ('^/admin/profile/.+', edit_profile)
CTK.publish ('^/admin/profile/del/.+', del_profile)
CTK.publish ('^/admin/profile/apply', edit_profile_apply, method="POST", validation=VALIDATIONS)
CTK.publish ('^/admin/profile/new', new_profile)
CTK.publish ('^/admin/profile/new/apply', new_profile_apply, method="POST", validation=VALIDATIONS)

if __name__ == '__main__':
    test()


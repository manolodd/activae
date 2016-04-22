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

try:
    from hashlib import sha256 as sha, md5
except:
    from md5 import md5
    from sha import sha

import CTK
import Auth
import Role
import Validations
import Page
import Profile
import WorkflowManager

from consts import *
from Widget import *
from CTK.consts import *
from DBSlayer import Query, query_check_success
from ComboboxSQL import ComboboxSQL
from PropsAutoSQL import PropsAutoSQL

NOTE_DELETE  = "<p>¿Confirmar eliminación?</p>"
LOCATION    = '/admin/user'
ADMIN_LINK  = LINK_HREF % ('/admin','Admin')
MENU_LINK   = '%s: %s' % (ADMIN_LINK, LINK_HREF % (LOCATION, 'Usuarios'))

#
# Validations
#
def __check_username (name):
    Validations.not_empty(name)

    q = "SELECT COUNT(*) FROM users WHERE username='%s' and id;" %(name)
    re = Query(q)
    if re['COUNT(*)'][0] != 0:
        raise ValueError, "Usuario ya en uso"

    return name


VALIDATIONS = [
    ('username', __check_username),
    ('password', Validations.not_empty),
    ('forename', Validations.not_empty),
    ('surname1', Validations.not_empty),
    ('surname2', Validations.not_empty),
    ('email',    Validations.is_email),
]


#
# Delete user
#
def del_user():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    # Target user
    user_id = CTK.request.url.split('/')[4]

    # Delete
    q = "DELETE FROM users WHERE id = %(user_id)s;" %(locals())
    ok = query_check_success (q)

    if ok:
        msg = None
    else:
        msg = ('Este usuario no puede ser eliminado ya que posee '
               'activos en el sistema.')

    return default (msg)


#
# New user
#
def new_user_apply():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    # Update the database
    fields = []
    values = []
    for key in ['username','forename', 'surname1', 'surname2', 'email']:
        if key in CTK.post:
            fields.append (key)
            values.append ("'%s'"%(CTK.post[key]))

    if 'password' in CTK.post:
        fields.append ('password')
        values.append ("'%s'"%(md5(CTK.post['password']).hexdigest()))

    for key in ['profile_id']:
        if key in CTK.post:
            fields.append (key)
            values.append ("%s" %(CTK.post[key]))

    q = "INSERT INTO users (%s) VALUES (%s);" %(", ".join(fields), ", ".join(values))
    if not query_check_success (q):
        return {'ret': "error"}

    return {'ret':      "ok",
            'redirect': "/admin/user"}


def new_user():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    q_profiles = "SELECT id, description FROM profiles;"

    table = CTK.PropsTable ()
    table.Add ('Profile',    ComboboxSQL  ({'name':'profile_id','class': "required"}, q_profiles), 'Profile del usuario')
    table.Add ('Login',      CTK.TextField({'name':'username',  'class': "required"}), 'Login de usuario')
    table.Add ('Password',   CTK.TextFieldPassword({'name':'password',  'class': "required"}), 'Clave de acceso')
    table.Add ('Nombre',     CTK.TextField({'name':'forename',  'class': "required"}), 'Nombre propio')
    table.Add ('Apellido 1', CTK.TextField({'name':'surname1',  'class': "required"}), 'Primer Apellido')
    table.Add ('Apellido 2', CTK.TextField({'name':'surname2',  'class': "required"}), 'Segundo Apellido')
    table.Add ('E-Mail',     CTK.TextField({'name':'email',     'class': "required"}), 'Cuenta de correo electronico')

    form = CTK.Submitter("/admin/user/new/apply")
    form += table

    page = Page.Default()
    page += CTK.RawHTML ("<h1>%s: Añadir usuario</h1>" % MENU_LINK)
    page += form
    return page.Render()


#
# Edit user
#
def edit_user_apply():
    # Authentication
    is_admin   = Role.user_has_role (Role.ROLE_ADMIN)

    user_id    = CTK.post['userid']
    current_id = Auth.get_user_id()
    try:
        is_self = (int(user_id) == current_id)
    except:
        is_self = False

    if not is_admin and not is_self:
        return CTK.HTTP_Error(403)

    if not user_id:
        return CTK.HTTP_Error(406)

    # Update the database
    sql_values = []
    for key in ['username', 'forename', 'surname1', 'surname2', 'email']:
        if key in CTK.post:
            sql_values.append ("%s='%s'" %(key, CTK.post[key]))

    if 'password' in CTK.post:
        password        = CTK.post['password']
        hashed_password = md5(password).hexdigest()
        old_password    = CTK.post['old_password']
        if not password == old_password:
            sql_values.append ("password='%s'"%(hashed_password))

    if is_admin:
        key = 'profile_id'
        if key in CTK.post:
            sql_values.append ("%s=%s" %(key, CTK.post[key]))

    q = "UPDATE users SET %s WHERE id = %s;" %(','.join(sql_values), user_id)
    if not query_check_success (q):
        return {'ret': "error"}
    return {'ret': "ok"}


def edit_user():
    # Authentication
    is_admin   = Role.user_has_role (Role.ROLE_ADMIN)
    user_id    = CTK.request.url.split('/')[3]
    profile_id = Profile.get_user_profile (user_id)
    current_id = Auth.get_user_id()
    try:
        is_self = (int(user_id) == current_id)
    except:
        is_self = False

    if not is_admin and not is_self:
        return CTK.HTTP_Redir('/')


    user_query = "SELECT * FROM users WHERE id = '%(user_id)s';" %(locals())
    profile_query = "SELECT id, description FROM profiles;"

    # Table
    table = PropsAutoSQL ('/admin/user/apply', user_query)
    table.AddConstant ('userid', user_id)
    table.AddConstant ('old_password', table.SQL_result['password'][0])

    if is_admin:
        props = {}
        if int(current_id) == int(user_id):
            props['disabled'] = ''
        props['selected']  = profile_id
        profiles           = ComboboxSQL (props, profile_query)
        table.Add ('Profile',profiles,        'profile_id', 'Profile del usuario')
    table.Add ('Login',      CTK.TextField({'disabled':True}), 'username',   'Login de usuario')
    table.Add ('Password',   CTK.TextFieldPassword(), 'password',   'Clave de acceso')
    table.Add ('Nombre',     CTK.TextField(), 'forename',   'Nombre propio')
    table.Add ('Apellido 1', CTK.TextField(), 'surname1',   'Primer Apellido')
    table.Add ('Apellido 2', CTK.TextField(), 'surname2',   'Segundo Apellido')
    table.Add ('E-Mail',     CTK.TextField(), 'email',      'Cuenta de correo electronico')

    page = Page.Default()
    if is_admin:
        title = '%s: %s' % (ADMIN_LINK, LINK_HREF % (LOCATION, 'Usuarios'))
    else:
        title = '%s Edición de usuario' % BACK_LINK

    page += CTK.RawHTML ("<h1>%s</h1>" % title)
    page += table
    return page.Render()


#
# User list
#
def default (message = None):
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    # List of users
    q = ("SELECT users.id as id, username, password, forename, surname1, surname2, email, description " +
         " FROM users JOIN profiles WHERE profiles.id = users.profile_id;")
    users = Query(q)

    table = CTK.Table()
    title = [CTK.RawHTML(x) for x in ['Login', 'Nombre', 'Apellido', 'Apellido', 'E-Mail', 'Profile']]
    table[(1,1)] = title
    table.set_header (row=True, num=1)

    page = Page.Default()

    n = 2
    for user in users:
        user_id  = users[user]['id']
        username = users[user]['username']

        # Delete user link
        dialog = CTK.Dialog ({'title': "Eliminando usuario %s"%(username), 'autoOpen': False})
        dialog += CTK.RawHTML (NOTE_DELETE)
        dialog.AddButton ('Cancelar', "close")
        dialog.AddButton ('Borrar',   "/admin/user/del/%s" %(user_id))

        del_img  = '<img src="/CTK/images/del.png" alt="Del"'
        linkdel  = LINK_JS_ON_CLICK %(dialog.JS_to_show(), del_img)
        linkname = LINK_HREF %("/admin/user/%s"%user_id, username)

        table[(n,1)] = [CTK.RawHTML(linkname),
                        CTK.RawHTML(users[user]['forename']),
                        CTK.RawHTML(users[user]['surname1']),
                        CTK.RawHTML(users[user]['surname2']),
                        CTK.RawHTML(users[user]['email']),
                        CTK.RawHTML(users[user]['description']),
                        CTK.RawHTML(linkdel)]

        page += dialog
        n += 1

    page += CTK.RawHTML ("<h1>%s: Administración de Usuarios</h1>" % ADMIN_LINK)
    page += CTK.RawHTML (LINK_HREF%('/admin/user/new', 'Añadir usuario'))
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


CTK.publish ('^/admin/user/?'              , init)
CTK.publish ('^/admin/user/general/?'      , default)
CTK.publish ('^/admin/user/\d+', edit_user)
CTK.publish ('^/admin/user/new', new_user)
CTK.publish ('^/admin/user/new/apply', new_user_apply, method="POST", validation=VALIDATIONS)
CTK.publish ('^/admin/user/apply', edit_user_apply, method="POST", validation=VALIDATIONS)
CTK.publish ('^/admin/user/del/\d+', del_user)


if __name__ == '__main__':
    test()

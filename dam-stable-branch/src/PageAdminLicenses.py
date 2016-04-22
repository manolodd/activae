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

LOCATION    = '/admin/license'
ADMIN_LINK  = LINK_HREF % ('/admin', 'Admin')
MENU_LINK   = '%s: %s' % (ADMIN_LINK, LINK_HREF % (LOCATION,'Licencias'))
NOTE_DELETE = "<p>¿Confirmar eliminación?</p>"

#
# Validations
#
def __check_licensename (name):
    Validations.not_empty(name)

    q = "SELECT COUNT(*) FROM licenses WHERE name='%s';" %(name)
    re = Query(q)
    if re['COUNT(*)'][0] != 0:
        raise ValueError, "La licencia ya existe"

    return name


VALIDATIONS = [
    ('name',        __check_licensename),
    ('description', Validations.not_empty),
]


#
# Delete license
#
def del_license():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    # Target license
    license_id = CTK.request.url.split('/')[-1]

    # Check whether it can be deleted
    q = "SELECT COUNT(*) as total FROM assets WHERE licenses_id = %(license_id)s;" %(locals())
    re = Query(q)

    usage = re['total'][0]
    if usage != 0:
        subs = Util.get_es_substitutions (usage)
        msg  = ("Imposible realizar la operación. La licencia está "
                "siendo usada por %(num)d activo%(s)s" % subs)
        return default (msg)

    # Delete
    q = "DELETE FROM licenses WHERE id = %(license_id)s;" %(locals())
    ok = query_check_success (q)
    if not ok:
        return default ('No se pudo eliminar la licencia.')
    return default ()


#
# New license
#
def new_license_apply():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    # Update the database
    fields = []
    values = []
    for key in ['name', 'description']:
        if key in CTK.post:
            fields.append (key)
            values.append ("'%s'"%(CTK.post[key]))

    q = "INSERT INTO licenses (%s) VALUES (%s);" %(", ".join(fields), ", ".join(values))
    if not query_check_success (q):
        return {'ret': "error"}

    return {'ret':      "ok",
            'redirect': LOCATION}


def new_license():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    table = CTK.PropsTable ()
    table.Add ('Licencia',    CTK.TextField({'name':'name', 'class': "required"}), 'Nombre de la licencia')
    table.Add ('Descripción', CTK.TextField({'name':'description', 'class': "required"}), 'Breve descripción')

    form = CTK.Submitter("%s/new/apply"%LOCATION)
    form += table

    page = Page.Default()
    page += CTK.RawHTML ("<h1>%s: A&ntilde;adir licencia</h1>" %(MENU_LINK))
    page += form
    return page.Render()


#
# Edit license
#
def edit_license_apply():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    license_id = CTK.post.pop('licenseid')
    if not license_id:
        return CTK.HTTP_Error(406)

    # Update the database
    sql_values = []
    for key in ['name', 'description']:
        if key in CTK.post:
            sql_values.append ("%s='%s'" %(key, CTK.post[key]))

    q = "UPDATE licenses SET %s WHERE id = %s;" %(','.join(sql_values), license_id)
    if not query_check_success (q):
        return {'ret': "error"}

    return {'ret': "ok"}


def edit_license():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    # Table
    license_id = CTK.request.url.split('/')[-1]
    q = "SELECT * FROM licenses WHERE id = '%(license_id)s';" %(locals())

    table = PropsAutoSQL ('%s/edit/apply'%LOCATION, q)
    table.AddConstant ('licenseid', license_id)
    table.Add ('Licencia',    CTK.TextField(), 'name', 'Nombre de la licencia')
    table.Add ('Descripción', CTK.TextField(), 'description', 'Breve descripción')

    page = Page.Default()
    page += CTK.RawHTML ("<h1>%s: Edicion de licencia</h1>" %(MENU_LINK))
    page += table
    return page.Render()


#
# License list
#
def default (message = None):
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    # List of licenses
    q = ("SELECT id, name, description FROM licenses;")
    licenses = Query(q)

    table = CTK.Table()
    title = [CTK.RawHTML(x) for x in ['Nombre', 'Descripción']]
    table[(1,1)] = title
    table.set_header (row=True, num=1)

    page = Page.Default()

    n = 2
    for license in licenses:
        license_id  = licenses[license]['id']
        licensename = licenses[license]['name']
        description = licenses[license]['description']
        if not description:
            description = ''

        # Delete license link
        dialog = CTK.Dialog ({'title': "¿Quieres eliminar %s?"%(licensename), 'autoOpen': False})
        dialog += CTK.RawHTML (NOTE_DELETE)
        dialog.AddButton ('Cancelar', "close")
        dialog.AddButton ('Borrar',   "%s/del/%s" %(LOCATION, license_id))

        linkdel  = LINK_JS_ON_CLICK %(dialog.JS_to_show(), "Borrar")
        linkname = LINK_HREF %("%s/edit/%s"%(LOCATION, license_id), licensename)

        table[(n,1)] = [CTK.RawHTML(linkname), CTK.RawHTML(description), CTK.RawHTML(linkdel)]

        page += dialog
        n += 1

    # Render
    page += CTK.RawHTML ("<h1>%s: Administraci&oacute;n de Licencias</h1>"%(ADMIN_LINK))
    page += table
    page += CTK.RawHTML (LINK_HREF%('%s/new'%LOCATION, 'A&ntilde;adir licencia'))

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
CTK.publish ('^%s/del/.+' % LOCATION, del_license)
CTK.publish ('^%s/new$' % LOCATION, new_license)
CTK.publish ('^%s/new/apply$' % LOCATION, new_license_apply, method="POST", validation=VALIDATIONS)
CTK.publish ('^%s/edit/.+' % LOCATION, edit_license)
CTK.publish ('^%s/edit/apply$' % LOCATION, edit_license_apply, method="POST", validation=VALIDATIONS)


if __name__ == '__main__':
    test()


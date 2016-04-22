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
import Format
import Page
import WorkflowManager

from CTK.consts import *
from DBSlayer import Query, transaction_check_success
from ComboboxSQL import ComboboxSQL
from Widget import *

LOCATION    = '/admin/format'
ADMIN_LINK  = LINK_HREF % ('/admin', 'Admin')
MENU_LINK   = '%s: %s' %(ADMIN_LINK, LINK_HREF % (LOCATION,'Formatos'))
NOTE_DELETE = "<p>¿Confirmar eliminación?</p>"
NOTE_DELETE_TARGET = "<p>¿Confirmar eliminación de la transcodificación?</p>"

#
# Validations
#
def __check_formatname (name):
    Validations.not_empty(name)

    q = "SELECT COUNT(*) FROM formats WHERE format='%s';" %(name)
    re = Query(q)
    if re['COUNT(*)'][0] != 0:
        raise ValueError, "La formato ya existe"

    return name


VALIDATIONS = [
    ('format',      __check_formatname),
]


#
# Delete format
#
def del_format():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    # Target format
    format_id = CTK.request.url.split('/')[-1]

    # Check whether it can be deleted
    q = ("SELECT COUNT(*) as total "
         "FROM view_asset_formats "
         "WHERE formats_id = %(format_id)s;" %(locals()))
    re = Query(q)

    usage = re['total'][0]
    if usage != 0:
        subs = [{'n':'','s':''},{'n':'n','s':''}][(usage > 1)]
        subs['num'] = usage
        msg  = ("Imposible realizar la operación ya que existe%(n)s "
                "%(num)d activo%(s)s en ese formato" % subs)

        return default (msg)

    # Delete
    q  = "DELETE FROM transcode_targets WHERE source_id = %(format_id)s OR target_id = %(format_id)s;" %(locals())
    q += "DELETE FROM formats WHERE id = %(format_id)s;" %(locals())
    q  = "START TRANSACTION; %s COMMIT;" % q

    ok = transaction_check_success (q)

    if not ok:
        msg = 'No se pudo eliminar el formato.'
        return default (msg)
    return default()


#
# New format
#
def new_format_apply():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    # Update the database
    fields = []
    values = []
    for key in ['format']:
        if key in CTK.post:
            fields.append (key)
            values.append ("'%s'"%(CTK.post[key]))

    q = "INSERT INTO formats (%s) VALUES (%s);" %(", ".join(fields), ", ".join(values))
    query = Query(q)

    try:
        format_id = query.result[0]['INSERT_ID']
    except TypeError,KeyError:
        return {'ret': "error"}

    return {'ret':      "ok",
            'redirect': '%s/edit/%s'%(LOCATION,format_id)}

def __get_new_format_form():
    q = 'SELECT format FROM formats;'
    query = Query(q)
    current = []
    if len(query) > 0:
        current = [query[x]['format'] for x in query]

    options  = [('','--')]
    options += [(x,x) for x in Format.FORMATS
                if x not in current]

    table   = CTK.PropsTable ()
    table.Add ('Formato', CTK.Combobox({'name': 'format'},  options), 'Nombre del formato')

    form = CTK.Submitter("%s/new/apply"%LOCATION)
    form += table
    return form


#
# Edit format
#
def edit_format_apply():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    format_id = CTK.post.pop('formatid')
    if not format_id:
        return CTK.HTTP_Error(406)

    # Update the database
    q = ''
    for key in ['lossy_flag', 'format']:
        if key in CTK.post:
            q += "UPDATE formats SET %s='%s' WHERE id = %s;" % \
                (key, CTK.post[key], format_id)

    if 'target' in CTK.post:
        q += "INSERT INTO transcode_targets (source_id, target_id) VALUES ('%s','%s');" % \
            (format_id,CTK.post['target'])
    if q:
        q = "START TRANSACTION; %s COMMIT;" % q
        if not transaction_check_success (q):
            return {'ret': "error"}

    return {'ret': "ok",
            'redirect': '%s/edit/%s'%(LOCATION,format_id)}


def edit_format():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    # Table
    format_id = CTK.request.url.split('/')[-1]
    f = Format.get_format (format_id)
    lossy_dict  = {'name': 'lossy_flag', 'checked': str(f['lossy_flag'])}

    table = CTK.PropsAuto ('%s/edit/apply'%LOCATION)
    table.AddConstant ('formatid', format_id)
    table.Add ('Formato',     CTK.RawHTML(f['name']), 'Nombre del formato')
    table.Add ('Con pérdida', CTK.Checkbox (lossy_dict),  'La transcodificación a este formato conlleva pérdida de calidad')

    page = Page.Default()
    page += CTK.RawHTML ("<h1>%s: Edicion de formato</h1>" %(MENU_LINK))
    page += table

    # New targets
    new_table = __get_new_targets_table (format_id)
    if new_table:
        page += CTK.RawHTML ("<h3>Agregar objetivos de transcodificación</h3>")
        page += new_table

    # Current targets
    target_table, dialogs = __get_current_targets_table (format_id)
    if target_table:
        page += CTK.RawHTML ("<h3>Objetivos de transcodificación existentes</h3>")
        page += target_table
        for dialog in dialogs:
            page += dialog
    return page.Render()


def __get_new_targets_table (format_id):
    q_formats = "SELECT id, format FROM formats WHERE id != %(format_id)s;" % locals()
    q_current = "SELECT id,format FROM transcode_targets "\
                "JOIN formats ON target_id = id WHERE source_id = '%(format_id)s';" % locals()
    q_name    = "SELECT * FROM formats WHERE id = %(format_id)s;" % locals()
    formats_query = Query(q_formats)
    current_query = Query(q_current)
    format_name   = Query(q_name)['format'][0]

    formats, current_targets = {}, []
    for x in formats_query:
        formats[formats_query[x]['format']] = formats_query[x]['id']

    if len(current_query) > 0:
        current_targets = [current_query[x]['format'] for x in current_query]

    targets = [(formats[x], x) for x in formats.keys() if x not in current_targets]

    if format_name in Format.AV:
        targets = [(value,label) for value,label in targets if label
                   in Format.AV]
    else:
        targets = [(value,label) for value,label in targets if label
                   in Format.IMG]

    if len(targets) == 0:
        return None

    options  = [('','--')] + targets
    table = CTK.PropsAuto ('%s/edit/apply'%LOCATION)
    table.AddConstant ('formatid', format_id)
    table.Add ('Objetivo', CTK.Combobox ({'name':'target'}, options), 'Destino de la transcodificación')
    return table


def __get_current_targets_table (format_id):
    # Targets
    q = "SELECT * FROM transcode_targets JOIN formats " \
        "ON target_id = id WHERE source_id = '%(format_id)s';" %(locals())
    targets = Query(q)

    if len(targets) == 0:
        return (None, None)

    row = 1
    table = CTK.Table()
    title = [CTK.RawHTML(x) for x in ['Formato']]
    table[(row,1)] = title
    table.set_header (row=True, num=1)

    dialogs = []
    for target in targets:
        row      += 1
        name      = targets[target]['format']
        target_id = targets[target]['id']
        dialog    = __get_del_dialog ("edit/del/%s/%s" %(format_id, target_id), NOTE_DELETE_TARGET)
        linkdel   = LINK_JS_ON_CLICK %(dialog.JS_to_show(), "Borrar")

        table[(row, 1)] = [CTK.RawHTML(name), CTK.RawHTML(linkdel)]
        dialogs.append(dialog)

    return (table, dialogs)


def __get_del_dialog (url_params, msg):
    # Link to delete target
    dialog = CTK.Dialog ({'title': "¿Confirmar eliminación?", 'autoOpen': False})
    dialog += CTK.RawHTML (msg)
    dialog.AddButton ('Cancelar', "close")
    dialog.AddButton ('Borrar',   "%s/%s" %(LOCATION, url_params))

    return dialog

#
# Delete format
#
def del_format_target():
    """Deletes transcode targets"""

    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    # Target format
    req = CTK.request.url.split('/')
    source_id = req[-2]
    target_id = req[-1]

    # Delete
    q = "DELETE FROM transcode_targets " \
        "WHERE source_id = %(source_id)s AND target_id = %(target_id)s;" %(locals())
    ok = transaction_check_success (q)
    return CTK.HTTP_Redir("%s/edit/%s" % (LOCATION, source_id))

#
# Format list
#
def default (message=None):
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    # List of formats
    q = ("SELECT * FROM formats;")
    formats = Query(q)

    table = CTK.Table()
    title = [CTK.RawHTML(x) for x in ['Nombre', 'Pérdida']]
    table[(1,1)] = title
    table.set_header (row=True, num=1)

    page = Page.Default()

    n = 2
    for format in formats:
        format_id  = str(formats[format]['id'])
        formatname = formats[format]['format']
        lossy      = ['No','Sí'][formats[format]['lossy_flag']]

        # Delete format link
        dialog   = __get_del_dialog ("del/%s" %(format_id), NOTE_DELETE)
        linkdel  = LINK_JS_ON_CLICK %(dialog.JS_to_show(), "Borrar")
        linkname = LINK_HREF %("%s/edit/%s"%(LOCATION, format_id), formatname)
        table[(n,1)] = [CTK.RawHTML(linkname), CTK.RawHTML(lossy), CTK.RawHTML(linkdel)]
        page += dialog
        n += 1

    # Render
    page += CTK.RawHTML ("<h1>%s: Administraci&oacute;n de Formatos</h1>"%(ADMIN_LINK))
    page += table
    page += CTK.RawHTML ("<h2>Añadir formato</h2>")
    page += __get_new_format_form()

    if message:
        page += Message(message)
    return page.Render()


def init ():
    """Workflow management"""
    return WorkflowManager.steer (__file__)


def test ():
    from Util import test_page
    test_page (__file__)

CTK.publish ('^%s/?'                 % LOCATION, init)
CTK.publish ('^%s/general/?'         % LOCATION, default)
CTK.publish ('^%s/del/.+'            % LOCATION, del_format)
CTK.publish ('^%s/new/apply$'        % LOCATION, new_format_apply, method="POST", validation=VALIDATIONS)
CTK.publish ('^%s/edit/.+'           % LOCATION, edit_format)
CTK.publish ('^%s/edit/apply$'       % LOCATION, edit_format_apply, method="POST", validation=VALIDATIONS)
CTK.publish ('^%s/edit/del/\d+/\d+$' % LOCATION, del_format_target)


if __name__ == '__main__':
    test()

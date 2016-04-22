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

import time
import CTK
import Auth
import Role
import Collection
import Validations
import Page
import Upload
import WorkflowManager
import File

import WidgetLookup
from ACL import ACL
from Widget import *
from WidgetAsset import *
from CTK.consts import *
from config import *
from consts import *
from DBSlayer import Query, query_check_success
from ComboboxSQL import ComboboxSQL
from PropsAutoSQL import PropsAutoSQL
from Asset import Asset
from OpAsset import OpAsset
from OpLookup import OpLookup
from OpCollection import OpCollection

LOCATION       = '/asset'
PUBLISH_LOOKUP = '%s/publish/lookup' % LOCATION
EDIT_LOOKUP    = '%s/edit/lookup' % LOCATION
MENU_LINK      = LINK_HREF % (LOCATION,'Activos')
ADMIN_LINK     = LINK_HREF % ('/admin','Admin')
ERROR_IN_USE   = "El activo interviene en el ciclo de vida de otros, por lo que solo se han purgado los ficheros asociados. Para eliminarlo completamente primero se deben borrar los activos que dependen de éste."

#
# Validations
#
def __check_asset_id (asset_id):
    q = "SELECT id FROM assets WHERE id ='%s'" % str(asset_id)
    query = Query(q)

    if len(query) != 1:
        raise ValueError, "Activo invalido."
    return asset_id

def __check_version (version):
    if not version:
        version=1
    Validations.is_number(version)
    return version

def __validate_number(value):
    if not value: return
    return Validations.is_number(value)

def __validate_extent(value):
    if not value: return
    return Validations.is_time(value)

def __validate_date(value):
    if not value: return
    return Validations.is_date(value)


VALIDATIONS = [
    ('version',   __check_version),
    ('language',  Validations.not_empty),
    ('subject',   Validations.not_empty),
    ('parent_id', __check_asset_id),
]


LOOKUP_VALIDATIONS = [
    ('id',             __validate_number),
    ('version',        __validate_number),
    ('views',          __validate_number),
    ('extent',         __validate_extent),
    ('date_created',   __validate_date),
    ('date_published', __validate_date),
]


#
# Delete asset
#
def del_asset():
    """Delete asset"""

    # Target asset
    asset_id = CTK.request.url.split('/')[-1]
    try:
        asset_id = __check_asset_id(asset_id)
        asset    = Asset (asset_id)
        if not asset['id']:
            return CTK.HTTP_Redir('/')
    except:
            return CTK.HTTP_Redir('/')

    # Authentication
    fail_admin = Auth.assert_is_role (Role.ROLE_ADMIN)
    user_id    = Auth.get_user_id()
    is_creator = (asset['creator_id'] == user_id)

    if fail_admin and not is_creator:
        return fail_admin

    op  = OpAsset (asset)
    result = op.delete()

    if result['ret'] == False:
        return default()

    if result['type'] == 'total':
        return CTK.HTTP_Redir(LOCATION)

    return default (ERROR_IN_USE)


#
# Edit asset
#
def edit_asset_apply():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_EDITOR)
    if fail: return fail

    asset_id = CTK.post.pop('asset_id')
    if not asset_id:
        return CTK.HTTP_Error(400)

    acl = ACL()
    editable = acl.filter_assets ("ed" , [asset_id])
    if not int(asset_id) in editable:
        return CTK.HTTP_Error(401)

   # Update the asset
    asset = Asset(asset_id)
    asset['edited_flag'] = 0
    asset['creator_id']    = "%s" % (Auth.get_user_id())
    sql_values = []
    for key in ['asset_types_id', 'licenses_id', 'title',
                'description', 'language', 'subject']:
        if CTK.post[key]:
            asset[key] = CTK.post[key]

    # Always evolve the version number
    post_version = asset['version']
    if 'version' in CTK.post:
        post_version = int(CTK.post['version'])
    if post_version <= asset['version']:
        asset['version'] += 1
    else:
        asset['version'] = post_version

    # Duplicate the attached file
    try:
        attachment  = File.clone_file (asset._file)
        asset._file = attachment
    except IOError,e:
        # If file copying is not possible, report and abort
        msg  = 'File duplication could not be performed while editing asset ID %s.' %(asset_id)
        msg += '\n%s\n' %(str(e))
        print msg
        return {'ret':"error"}

    # Add replacement info
    if not asset._parent_id:
        asset._parent_id = asset['id']
    asset._replacements['replaces'].append(asset['id'])

    # Add asset to database
    op  = OpAsset (asset)
    ret = op.add()

    if ret == True:
        # Update base asset
        asset = Asset(asset_id)
        asset['date_modified'] = None # unmark edition
        asset['edited_flag'] = 1 # mark as editted
        op  = OpAsset (asset)
        ret = op.update()

        return {'ret': "ok",
                'redirect': LOCATION}
    else:
        return {'ret': "error"}


def edit_asset ():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_EDITOR)
    if fail: return fail

    asset_id = CTK.request.url.split('/')[-1]
    acl = ACL()
    editable = acl.filter_assets ("ed" , [asset_id])

    if not int(asset_id) in editable:
        return CTK.HTTP_Error(401)

    asset    = Asset(asset_id)
    q        = "SELECT * "\
               "FROM assets WHERE id = '%(asset_id)s';" %(locals())

    # Prevent simultaneous editions
    editor_id   = int(Auth.get_user_id())
    try:
        strp    = time.strptime(asset['date_modified'], '%Y-%m-%d %H:%M:%S')
        edit_ts = int(time.mktime(strp))
    except (ValueError, TypeError):
        edit_ts = 0
    # Edition during edition-window is only allowed to the current editor.
    if time.time() - edit_ts < EDIT_WINDOW and asset['editor_id'] != editor_id:
        page = Page.Default()
        page += CTK.RawHTML ("<h1>%s: Editar activo</h1>"%(MENU_LINK))
        page += CTK.RawHTML ("<h2>El activo está siendo editado actualmente</h2>")
        return page.Render()

    # Mark it as 'being edited'
    asset['date_modified'] = "CURRENT_TIMESTAMP()"
    asset['editor_id']     = editor_id
    oa = OpAsset(asset)
    rc = oa.update()
    asset = Asset(asset_id)

    lang     = asset['language']
    languages= CTK.Combobox({'name':'language', 'selected': lang, 'class':'required'}, LANG)

    # Table
    types    = ComboboxSQL (props={'selected':asset['asset_types_id'], 'class':'required'}, sql="SELECT id, type FROM asset_types;")
    licenses = ComboboxSQL (props={'selected':asset['licenses_id'], 'class':'required'}, sql="SELECT id, name FROM licenses;")

    table = PropsAutoSQL (False, q)
    table.AddConstant ('asset_id',str(asset_id))
    table.Add ('Tipo',        types, 'asset_types_id', 'Tipo de activo')
    table.Add ('Licencia',    licenses, 'licenses_id', 'Licencia del activo')
    table.Add ('Título',      CTK.TextField({'class':'required', 'maxlength': LEN_TITL}), 'title', 'Titulo del activo')
    table.Add ('Descripción', CTK.TextField({'class':'required', 'maxlength': LEN_DESC}), 'description', 'Descripcion del activo')
    table.Add ('Versión',     CTK.TextField({'class':'required'}), 'version', 'Version del activo')
    table.Add ('Idioma',      languages, 'language', 'Idioma del activo')
    table.Add ('Tema',        CTK.TextField({'class':'required', 'maxlength': LEN_SUBJ}), 'subject', 'El tema del contenido del recurso')

    form = CTK.Submitter('%s/edit/apply'%LOCATION)
    form += table
    form += CTK.SubmitterButton('Enviar')

    page = Page.Default()
    page += CTK.RawHTML ("<h1>%s: Editar activo</h1>"%(MENU_LINK))
    page += form
    return page.Render()


def edit_asset_page (perform = None):
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_EDITOR)
    if fail: return fail

    lookup   = OpLookup()
    search   = {'edited_flag': 0, '__order__': 'date_created'}

    try:
        result   = lookup(search)
    except:
        result  = []

    acl      = ACL()
    result   = acl.filter_assets ("ed" , result)
    contents = [(Asset, x) for x in result]

    page = Page.Default()
    page += CTK.RawHTML ("<h1>%s: Editar activos</h1>" %(MENU_LINK))

    pending = CTK.Container()
    if len(contents) == 0:
        pending += CTK.RawHTML ("<h2>No hay activos pendientes de edición</h2>")
    else:
        pending += Paginate(contents, EditWidget)

    if perform or perform == []:
        page += CTK.RawHTML ("<h2>Activos buscados</h2>")
        page += edit_get_custom (perform)

    tabs = CTK.Tab()
    tabs.Add ('Pendientes',  pending)
    tabs.Add ('Búsqueda',    WidgetLookup.get_fields_form(EDIT_LOOKUP))
    page += tabs

    return page.Render()


def edit_get_custom (perform):
    if not perform:
        assets = []
    elif type(perform) == list:
        assets = [(Asset, x) for x in perform]
    else:
        lookup   = OpLookup()

        try:
            results  = lookup(perform)
        except:
            results  = []

        acl      = ACL()
        results  = acl.filter_assets ("ed" , results)
        assets   = [(Asset, x) for x in results]

    if not assets:
        table = CTK.Table()
        table[(1,1)] = CTK.RawHTML('<h3>La búsqueda no ha devuelto resultados.</h3>')
        return table
    return Paginate (assets, EditWidget)


def edit_lookup ():
    result  = urllib.unquote_plus(CTK.request.url)
    result  = result.split('%s/'%EDIT_LOOKUP)[1]
    results = result.split(',')
    assets  = []
    for x in results:
        try:
            assets.append(int(x))
        except ValueError:
            pass

    return edit_asset_page (assets)


#
# Publish asset
#
def publish_lookup ():
    result  = urllib.unquote_plus(CTK.request.url)
    result  = result.split('%s/'%PUBLISH_LOOKUP)[1]
    results = result.split(',')
    assets  = []
    for x in results:
        try:
            assets.append(int(x))
        except ValueError:
            pass

    return publish_asset (assets)


def publish_get_custom (perform):
    if not perform:
        assets = []
    elif type(perform) == list:
        assets = [(Asset, x) for x in perform]
    else:
        lookup   = OpLookup()

        try:
            results  = lookup(perform)
        except:
            results  = []

        acl      = ACL()
        results  = acl.filter_assets ("ad" , results)

        assets = [(Asset, x) for x in results]

    if not assets:
        table = CTK.Table()
        table[(1,1)] = CTK.RawHTML('<h3>La búsqueda no ha devuelto resultados.</h3>')
        return table
    return Paginate (assets, PublishWidget)


def publish_asset (perform = None):
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_PUBLISHER)
    if fail: return fail

    lookup = OpLookup()
    search = {'published_flag': 0, '__order__': 'type'}
    try:
        result = lookup(search)
    except:
        result = []
    acl    = ACL()
    result = acl.filter_assets ("ad" , result)

    contents = [(Asset, x) for x in result]

    page = Page.Default()
    page += CTK.RawHTML ("<h1>%s: Publicar activos</h1>" %(MENU_LINK))

    pending = CTK.Container()
    if len(contents) == 0:
        pending += CTK.RawHTML ("<h2>No hay activos pendientes de publicación</h2>")
    else:
        pending += Paginate(contents, PublishWidget)

    if perform or perform == []:
        page += CTK.RawHTML ("<h2>Activos buscados</h2>")
        page += publish_get_custom (perform)

    tabs = CTK.Tab()
    tabs.Add ('Pendientes',  pending)
    tabs.Add ('Búsqueda',    WidgetLookup.get_fields_form(PUBLISH_LOOKUP))
    page += tabs

    return page.Render()


def publish_asset_apply ():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_PUBLISHER)
    if fail: return fail

    acl = ACL()
    ret = []
    for key in CTK.post:
        if not key.startswith('published_'):
            continue
        flag     = int(CTK.post[key])
        asset_id = key[len('published_'):]
        asset    = Asset(asset_id)

        if asset['published_flag'] == flag:
            continue

        asset['published_flag'] = flag
        asset['publisher_id']   = Auth.get_user_id()
        asset['date_available'] = "CURRENT_TIMESTAMP()"
        op = OpAsset(asset)
        ret.append(op.update())

        if ret[-1] == False:
            break

        if asset['published_flag']:
            acl.set_published_asset_acl(asset, True)
        else:
            acl.set_published_asset_acl(asset, False)

    if False in ret:
        return {'ret': "error"}

    return {'ret': "ok"}


#
# Asset list
#
def default( message = None):
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_UPLOADER)
    if fail: return fail

    # List of assets
    lookup = OpLookup()
    search = {'creator_id': Auth.get_user_id(),
              '__order__': 'id'}

    if Role.user_has_role (Role.ROLE_ADMIN):
        search = {'__order__': 'id'}

    try:
        result = lookup(search)
    except:
        result = []
    contents = [(Asset, x) for x in result]

    page = Page.Default ()

    # Render
    if Role.user_has_role (Role.ROLE_ADMIN):
        page += CTK.RawHTML ("<h1>%s: Activos</h1>"%(ADMIN_LINK))
    else:
        page += CTK.RawHTML ("<h1>Administración de Activos</h1>")

    if Role.user_has_role (Role.ROLE_UPLOADER):
        page += CTK.RawHTML ("<p>%s</p>"%LINK_HREF%('%s/upload/new'%LOCATION, 'A&ntilde;adir activo'))

    if Role.user_has_role (Role.ROLE_PUBLISHER):
        page += CTK.RawHTML ("<p>%s</p>"%LINK_HREF%('%s/publish'%LOCATION, 'Publicar activos'))

    if Role.user_has_role (Role.ROLE_EDITOR):
        page += CTK.RawHTML ("<p>%s</p>"%LINK_HREF%('%s/edit'%LOCATION, 'Editar activos'))

    if len(contents):
        page += Paginate(contents, DefaultWidget)

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
CTK.publish ('^%s/del/.+'         % LOCATION, del_asset)
CTK.publish ('^%s/edit/?$'        % LOCATION, edit_asset_page)
CTK.publish ('^%s/edit/;.+'       % LOCATION, edit_asset_page)
CTK.publish ('^%s/edit/\d+'       % LOCATION, edit_asset)
CTK.publish ('^%s/edit/apply'     % LOCATION, edit_asset_apply, method="POST", validation=VALIDATIONS)
CTK.publish ('^%s/publish/?$'     % LOCATION, publish_asset)
CTK.publish ('^%s/publish/;.+'    % LOCATION, publish_asset)
CTK.publish ('^%s/publish/apply'  % LOCATION, publish_asset_apply, method="POST", validation=VALIDATIONS)
CTK.publish ('^%s/.*'             % EDIT_LOOKUP, edit_lookup)
CTK.publish ('^%s/.*'             % PUBLISH_LOOKUP, publish_lookup)


if __name__ == '__main__':
    test()

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
import Widget
import WorkflowManager

from ACL import ACL
from CTK.consts import *
from config import *
from consts import *
from PartChooser import *
from DBSlayer import Query, query_check_success
from ComboboxSQL import ComboboxSQL
from PropsAutoSQL import PropsAutoSQL
from Asset import Asset
from OpAsset import OpAsset
from OpCollection import OpCollection

LOCATION       = '/asset'
MENU_LINK      = LINK_HREF % (LOCATION,'Activos')
DEFAULT_LICENSE= 1

#
# Validations
#
def __check_asset_id (asset_id):
    q = "SELECT id FROM assets WHERE id ='%s'" % str(asset_id)
    query = Query(q)

    if len(query) != 1:
        raise ValueError, "Activo invalido."
    return asset_id

def __check_parts (parts_list):
    if not parts_list:
        return
    numeric_list = Validations.is_numeric_list(parts_list)
    numeric_list = list(set(numeric_list))

    q = "SELECT COUNT(*) FROM assets WHERE id IN (%s);" % (','.join(numeric_list))
    re = Query(q)

    if re['COUNT(*)'][0] != len(numeric_list):
        raise ValueError, "Hay partes invalidas."

    return parts_list

def __check_version (version):
    if not version:
        version=1
    Validations.is_number(version)
    return version


VALIDATIONS = [
    ('version',   __check_version),
    ('language',  Validations.not_empty),
    ('subject',   Validations.not_empty),
    ('parts',     __check_parts),
    ('parent_id', __check_asset_id),
]


#
# New asset
#
def page_broken_file ():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_UPLOADER)
    if fail: return fail

    page  = Page.Default()
    page += CTK.RawHTML ("<h1>%s: A&ntilde;adir activo</h1>"%(MENU_LINK))
    page += CTK.RawHTML ("<p>El fichero está corrupto. Pruebe con otro.</p><p>No se pudo crear el activo.</p>")

    return page.Render()

def create_collection (filename):
    user_id  = Auth.get_user_id()
    col_name = filename.split(os.path.sep)[-1]
    col = Collection.Collection()
    col['name'] = col_name
    col['creator_id'] = user_id
    op = OpCollection (col)
    op.add()
    col = Collection.Collection(name_collection=col_name)
    return col['id']

def create_assets (asset, filenames):
    """Create the assets immediately. Final info is added via callback
    once the task exits the processing queue."""

    ret = []
    if not filenames:
        filenames = [None]

    for filename in filenames:
        if filename:
            queue_flag = id(asset)
            asset._file = Upload.get_info (filename)
        op = OpAsset (asset)
        rc = op.add()
        ret.append(rc)
    return ret


def add_asset_apply ():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_UPLOADER)
    if fail: return fail

    asset = Asset()
    asset['creator_id'] = Auth.get_user_id()
    asset['version']    = 1

    if 'parts' in CTK.post:
        parts =  CTK.post['parts']
        if parts:
            parts =  Validations.split_list (CTK.post['parts'])
            asset._parts['has_parts_of'] = [int(p) for p in parts]

    if 'parent_id' in CTK.post:
        asset._parent_id = int(CTK.post['parent_id'])

    for key in ['asset_types_id', 'licenses_id', 'title',
                'description', 'version', 'language', 'subject']:
        if key in CTK.post:
            asset[key] = CTK.post[key]

    filenames = []
    if 'name' in CTK.post and 'ref' in CTK.post:
        tmp_name  = CTK.post['ref']
        src_name  = CTK.post['name']
        filenames = Upload.process_file (tmp_name, src_name)

    #Collection
    if len(filenames) > 1:
        col_id = create_collection (src_name)
        asset['collections_id'] = col_id
    elif len(filenames) == 1:
        info = Upload.get_info (filenames[0])
        #If unique file is broken
        if not info['filename']:
            return {'ret': "ok",
                    'redirect': '%s/broken' %(LOCATION)}

    ret = create_assets (asset, filenames)

    if False in ret:
        return {'ret': "error"}

    return {'ret': "ok",
            'redirect': LOCATION}


def add_asset (parent_id = None):
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_UPLOADER)
    if fail: return fail

    req = CTK.request.url.split('/')
    name, ref = None, None

    for r in req:
        try:
            if r.startswith('name='):
                name = r.split('name=')[1]
            elif r.startswith('ref='):
                ref = r.split('ref=')[1]
        except IndexError:
            pass

    q_types    = "SELECT id, type   FROM asset_types;"
    q_licenses = "SELECT id, name   FROM licenses;"
    q_formats  = "SELECT id, format FROM formats;"

    lang_options = [(x,'(%s) %s' % (x,y)) for x,y in LANG]

    table = CTK.PropsTable ()
    table.Add ('Tipo',        ComboboxSQL  ({'name':'asset_types_id', 'class': "required"}, q_types), 'Tipo de activo')
    table.Add ('Licencia',    ComboboxSQL  ({'name':'licenses_id', 'class': "required", 'selected': DEFAULT_LICENSE}, q_licenses), 'Licencia del activo')
    table.Add ('Título',      CTK.TextField({'name':'title',  'class': "required", 'maxlength': LEN_TITL}), 'Titulo del activo')
    table.Add ('Descripción', CTK.TextField({'name':'description', 'maxlength': LEN_DESC}), 'Descripcion del activo')
    table.Add ('Versión',     CTK.TextField({'name':'version'}), 'Version del activo')
    table.Add ('Partes',      PartChooser({'name':'parts'}), 'Otros activos que forman parte del actual')
    table.Add ('Idioma',      CTK.Combobox({'name':'language','class': "required"}, lang_options), 'Idioma del activo')
    table.Add ('Tema',        CTK.TextField({'name':'subject', 'class': "required", 'maxlength': LEN_SUBJ}), 'El tema del contenido del recurso')

    form = CTK.Submitter("%s/new/apply"%LOCATION)
    form += table
    if parent_id:
        form += CTK.HiddenField({'name':'parent_id','value':str(parent_id)})
    page = Page.Default()
    page += CTK.RawHTML ("<h1>%s: A&ntilde;adir activo</h1>"%(MENU_LINK))

    if name and ref:
        form += CTK.HiddenField({'name':'ref','value':ref})
        form += CTK.HiddenField({'name':'name','value':name})
        page += CTK.RawHTML ('<h3>Archivo: "%s"</h3>'%(name))

    page += form
    return page.Render()

#
# Evolve
#
def evolve_asset ():
    """Creates an asset attaching life-cycle information"""
    try:
        req = CTK.request.url.split('/')
        try:
            for r in req:
                if r.startswith('parent='):
                    parent_id = r.split('parent=')[1]
        except IndexError:
            pass

        parent_id = __check_asset_id(parent_id)
        return evolve_form (parent_id)
    except ValueError:
        return CTK.HTTP_Redir('/')


def evolve_form (parent_id):
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_UPLOADER)
    if fail: return fail

    req = CTK.request.url.split('/')
    name, ref = None, None

    for r in req:
        try:
            if r.startswith('name='):
                name = r.split('name=')[1]
            elif r.startswith('ref='):
                ref = r.split('ref=')[1]
        except IndexError:
            pass

    asset    = Asset(parent_id)
    lang     = asset['language']
    languages= CTK.Combobox({'name':'language', 'selected': lang}, LANG)

    # Table
    types    = ComboboxSQL (props={'name': 'asset_types_id', 'selected':asset['asset_types_id']}, sql="SELECT id, type FROM asset_types;")
    licenses = ComboboxSQL (props={'name':  'licenses_id', 'selected':asset['licenses_id']}, sql="SELECT id, name FROM licenses;")

    table = CTK.PropsTable()

    table.Add ('Tipo',        types, 'Tipo de activo')
    table.Add ('Licencia',    licenses, 'Licencia del activo')
    table.Add ('Título',      CTK.TextField({'value': asset['title'], 'name':'title', 'class':'required'}),'Titulo del activo')
    table.Add ('Descripción', CTK.TextField({'value': asset['description'], 'name': 'description','class':'required'}), 'Descripcion del activo')
    table.Add ('Versión',     CTK.TextField({'value': asset['version'], 'name': 'version', 'class':'required'}), 'Version del activo')
    table.Add ('Partes',      PartChooser({'name':'parts', 'value': asset['parts'], 'class':'required'}), 'Otros activos que forman parte del actual')
    table.Add ('Idioma',      languages, 'Idioma del activo')
    table.Add ('Tema',        CTK.TextField({'value': asset['subject'], 'name': 'subject', 'class':'required'}), 'El tema del contenido del recurso')

    form = CTK.Submitter("%s/new/apply"%LOCATION)
    form += table
    form += CTK.HiddenField ({'name': 'parent_id', 'value':parent_id})
    form += CTK.SubmitterButton('Crear activo')

    page = Page.Default()
    page += CTK.RawHTML ("<h1>%s: Evolucionar activo</h1>"%(MENU_LINK))
    if name and ref:
        form += CTK.HiddenField({'name':'ref','value':ref})
        form += CTK.HiddenField({'name':'name','value':name})
        page += CTK.RawHTML ('<h3>Archivo: "%s"</h3>'%(name))

    page += form
    return page.Render()




def init ():
    """Workflow management"""
    return WorkflowManager.steer (__file__)


def test ():
    from Util import test_page
    test_page (__file__)


CTK.publish ('^%s/create/?'      % LOCATION, init)
CTK.publish ('^%s/new/?'         % LOCATION, add_asset)
CTK.publish ('^%s/new/name=(.+)?/ref=(.+)?' % LOCATION, add_asset)
CTK.publish ('^%s/new/apply'     % LOCATION, add_asset_apply, method="POST", validation=VALIDATIONS)
CTK.publish ('^%s/evolve/.+'     % LOCATION, evolve_asset)
CTK.publish ('^%s/evolve/apply'  % LOCATION, add_asset_apply, method="POST", validation=VALIDATIONS)
CTK.publish ('^%s/broken'        % LOCATION, page_broken_file)


if __name__ == '__main__':
    test()

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
import PageAsset
import WorkflowManager

from Asset import Asset
from OpAsset import OpAsset
from DBSlayer import Query, query_check_success
from config import *
from CTK.consts import *
from Upload import get_info

LOCATION       = '/transcode'
ADMIN_LINK     = LINK_HREF % ('/admin','Admin')
MENU_LINK      = ADMIN_LINK + ': %s: Transcodificar' % (LINK_HREF % (PageAsset.LOCATION,'Activos'))
NOTE_NO_TRANSCODING = "No se han registrado conversiones para este tipo de archivo."
NOTE_NO_FORMAT = "No se ha podido determinar el tipo de archivo."
NOTE_NO_FILE   = "El activo no parece tener un archivo asociado."
LOSSY    = "Con pérdida de calidad"
LOSSLESS = "Sin pérdida de calidad"


def error_page (msg = NOTE_NO_TRANSCODING):
    page = Page.Default()
    page += CTK.RawHTML ('<h1>%s</h1>' % MENU_LINK)
    page += CTK.RawHTML ('<h3>%s</h3>' % msg)
    return page.Render()


def transcode_apply ():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_PUBLISHER)
    if fail: return fail

    asset_id   = CTK.post.pop('asset_id')
    asset      = Asset(asset_id)
    op         = OpAsset(asset)

    rets = []
    for key in CTK.post:
        if not key.startswith('target_id_'):
            continue

        val = int(CTK.post[key])
        if val:
            target_id = key[len('target_id_'):]
            ret = op.transcode(target_id)
            rets.append(ret)

    if False in rets:
        return {'ret': "error"}
    return {'ret': "ok",
            'redirect': '%s/publish' % PageAsset.LOCATION}


def transcode ():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_PUBLISHER)
    if fail: return fail

    asset_id  = CTK.request.url.split('/')[-1]
    asset     = Asset(asset_id)

    if not asset._file.get('filename'):
        return error_page(NOTE_NO_FILE)

    format_id = asset._file.get('formats_id')
    if not format_id:
        info = get_info (asset._file.get('filename'))
        format_id = info.get('formats_id',None)

    if not format_id:
        return error_page(NOTE_NO_FORMAT)

    sql = "SELECT * FROM transcode_targets "\
          "JOIN formats ON target_id=formats.id "\
          "WHERE source_id = %(format_id)s;" %(locals())
    q = Query(sql)

    if not len(q):
        return error_page(NOTE_NO_TRANSCODING)

    table = CTK.Table ()

    header     = ['Formato', 'Convertir', 'Calidad de conversión']
    table[(1,1)] = [CTK.RawHTML(x) for x in header]
    table.set_header (row=True, num=1)
    n = 2

    for x in q:
        if q[x]['lossy_flag']: text = LOSSY
        else:                  text = LOSSLESS
        opts  = {'name': 'target_id_%s'% str(q[x]['target_id']),
                 'class':'required',
                 'checked': 0}

        fields = [CTK.RawHTML(q[x]['format'].upper()),
                  CTK.Checkbox(opts),
                  CTK.RawHTML(text)]

        table[(n,1)] = fields
        n += 1

    form = CTK.Submitter("%s/apply"%LOCATION)
    form += table
    form += CTK.HiddenField({'name':'asset_id','value':str(asset_id)})
    form += CTK.SubmitterButton('Enviar')

    page = Page.Default()
    page += CTK.RawHTML ('<h1>%s</h1>'%MENU_LINK)
    page += form
    return page.Render()


def init ():
    """Workflow management"""
    return WorkflowManager.steer (__file__)


def test ():
    from Util import test_page
    test_page (__file__)


CTK.publish ('^%s/?'     % LOCATION, init)
CTK.publish ('^%s/\d+/?' % LOCATION, transcode)
CTK.publish ('^%s/apply' % LOCATION, transcode_apply, method="POST")


if __name__ == '__main__':
    test()

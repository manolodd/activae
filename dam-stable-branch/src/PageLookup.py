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

import time
import urllib
import CTK
import Auth
import Role
import Validations
import Page
import Asset
import WorkflowManager

from ACL import ACL
from Widget import *
import WidgetConsume
import WidgetLookup
from CTK.consts import *
from OpLookup import OpLookup

LOCATION     = '/lookup'
ADMIN_LINK   = LINK_HREF % ("/admin", 'Admin')

#
# Validations
#

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
    ('id',             __validate_number),
    ('version',        __validate_number),
    ('views',          __validate_number),
    ('extent',         __validate_extent),
    ('date_created',   __validate_date),
    ('date_published', __validate_date),
    ('search',         Validations.not_empty),
]

#
# Search by fields
#
def lookup_apply():
    params = ''
    for key in CTK.post:
        if CTK.post[key]:
            params += '%s=%s;' % (key, CTK.post[key])

    if params:
        params = urllib.quote(params)
        return {'ret': "ok",
                'redirect': "%s/%s" % (LOCATION, params)}
    else:
        return {'ret': "error"}


def parse_fields ():
    vals = urllib.unquote(CTK.request.url)
    vals = vals.split('%s/'%LOCATION)[1]
    # vals = vals.replace('/',';') # This breaks redirects
    search_vals = vals.split(';')
    search = {}

    for pair in search_vals:
        pair = pair.split('=')
        if len(pair) > 1:
            key,value = pair[0], pair[1]
            search[key] = value

    search = iso_dates (search)
    return search


def iso_dates (search):
    for key,val in search.items():
        if key.startswith('date'):
            val = val.replace('/','-')
            try:
                val = time.strptime(val, "%d-%m-%Y")
                val = time.strftime('%Y-%m-%d',val)
                search[key] = val
            except:
                search[key] = val
    return search


def lookup_perform ():
    search = parse_fields()
    redir  = search.pop('redir',None)

    if search.has_key('search'):
        search = search['search'] # Fulltext search only

    if redir:
        return redirect (search, redir)

    return default(search)


def redirect (search, redir):
    lookup = OpLookup()

    try:
        result = lookup(search)
    except:
        result = []

    data   = ','.join(map(str,result))

    return CTK.HTTP_Redir('%s/%s' % (redir,data))


def do_lookup (search):
    lookup = OpLookup()
    result = {}
    try:
        result['assets'] = lookup(search)
    except:
        result['assets'] = []

    if type(search) == str:
        result['type'] = 'texto'
    elif type(search) == dict:
        result['type'] = 'campos'
    return result


def __get_results (perform):
    results = do_lookup(perform)
    acl = ACL()
    results['assets'] = acl.filter_assets ("co" , results['assets'])
    assets  = [(Asset.Asset, x) for x in results['assets']]

    if not assets:
        table = CTK.Table()
        table[(1,1)] = CTK.RawHTML('<h3>La búsqueda no ha devuelto resultados. Pruebe de nuevo utilizando otros criterios de búsqueda.</h3>')
        return table

    return Paginate (assets, WidgetConsume.AbstractWidget)


def default (perform = None):
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_CONSUMER)
    if fail: return fail

    page = Page.Default()
    page += CTK.RawHTML ("<h1>Búsquedas</h1>")

    if perform:
        page += CTK.RawHTML ("<h2>Resultados</h2>")
        page += __get_results (perform)

    tabs = CTK.Tab()
    tabs.Add ('Por texto',  WidgetLookup.get_text_form())
    tabs.Add ('Por campos', WidgetLookup.get_fields_form())
    page += tabs

    return page.Render()


def init ():
    """Workflow management"""
    return WorkflowManager.steer (__file__)


def test ():
    from Util import test_page
    test_page (__file__)


CTK.publish ('^%s/?'          % LOCATION, init)
CTK.publish ('^%s/general/?'  % LOCATION, default)
CTK.publish ('^%s/apply'      % LOCATION, lookup_apply, method="POST", validation=VALIDATIONS)
CTK.publish ('^%s/?.+'        % LOCATION, lookup_perform)


if __name__ == '__main__':
    test()

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
import Page
import Type
import Asset
import OpLookup
import WidgetConsume
import WorkflowManager

from CTK.consts import *
from consts import *
from DBSlayer import *
from ACL import ACL
LOCATION     = '/report'
ADMIN_LINK   = LINK_HREF % ("/admin", 'Admin')
MENU_LINK    = '%s: %s' % (ADMIN_LINK, LINK_HREF % (LOCATION, 'Reportes'))

GRAPH_TEMPLATE = """
<div class="graphs">
<span>Tráfico</span>
<p><img src="/rrdgraphs/server_traffic_%(ext)s.png" alt="Gráfica %(desc)s" /></p>

<span>Conexiones / Peticiones</span>
<p><img src="/rrdgraphs/server_accepts_%(ext)s.png" alt="Gráfica %(desc)s" /></p>

<span>Tiempos de espera</span>
<p><img src="/rrdgraphs/server_timeouts_%(ext)s.png" alt="Gráfica %(desc)s" /></p>
</div>
"""


def get_section (report, extra = None):
    table        = CTK.Table()
    n=1
    for section in report:
        title  = section[0]
        assets = section[1]

        header = ["%s ID"%title, 'Autor', 'Formato']
        fields = ['Identifier', 'Creator', 'Format']
        if extra:
            header.append(extra[0])
            fields.append(extra[1])
        header.append('Título')
        fields.append('Title')

        table[(n,1)] = [CTK.RawHTML(x) for x in header]
        table.set_header (num=n)
        n+=1

        for asset_id in assets:
            asset = Asset.Asset(asset_id)
            data  = [str(asset[x])[:REPORT_MAX_CHAR] for x in fields]
            info  = [WidgetConsume.add_meta_ref(fields[x], data[x])[1]
                     for x in range(len(data))]
            table[(n,1)] = info
            n+=1

    return table


def get_views_task ():
    types  = Type.get_types()
    lookup = OpLookup.OpLookup()
    report = []
    for asset_type in types:
        search  = {'__order__':      'views DESC',
                   'asset_types_id':  asset_type['id']}

        try:
            results = lookup(search)
        except:
            results = []

        acl = ACL()
        results = acl.filter_assets ("co" , results)

        if not results:
            continue
        if len(results) > REPORT_ITEM_SZ:
            results = results[:REPORT_ITEM_SZ]

        report.append((asset_type['name'], results))
    return report


def get_24h_task ():
    types  = Type.get_types()
    lookup = OpLookup.OpLookup()
    report = []
    for asset_type in types:
        search  = {'__order__':      'date_created DESC',
                   'asset_types_id':  asset_type['id'],
                   'date_created-':  'DATE_SUB(NOW(),INTERVAL 1 DAY)'}

        try:
            results = lookup(search)
        except:
            results = []

        acl = ACL()
        results = acl.filter_assets ("co" , results)

        if not results:
            continue
        if len(results) > REPORT_ITEM_SZ:
            results = results[:REPORT_ITEM_SZ]

        report.append((asset_type['name'], results))
    return report


def report_assets ():
    """Report info for users"""

    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_CONSUMER)
    if fail: return fail

    page = Page.Default()

    if Role.user_has_role (Role.ROLE_ADMIN):
        page += CTK.RawHTML ("<h1>%s</h1>"%(MENU_LINK))

    report = get_24h_task()
    if report:
        page += CTK.RawHTML('<h2>Activos de las últimas 24 horas</h2>')
        page += get_section (report)

    report = get_views_task()
    if report:
        page += CTK.RawHTML('<h2>Activos más populares</h2>')
        page += get_section (report, ('Visitas','views'))

    return page.Render()


def report_system ():
    """Report info for system administration:"""

    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    pairs = [('1h','1 hora'), ('6h','6 horas'),
             ('1d','1 día'),  ('1w','1 semana')]

    tabs = CTK.Tab()
    for pair in pairs:
        mapping = {'ext': pair[0], 'desc': pair[1]}
        tabs.Add (pair[1], CTK.RawHTML(GRAPH_TEMPLATE % mapping))

    page  = Page.Default()
    page += CTK.RawHTML ("<h1>%s</h1>"%(MENU_LINK))
    page += tabs
    return page.Render()


def default ():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_CONSUMER)
    if fail: return fail

    if not Role.user_has_role(Role.ROLE_ADMIN):
        return report_assets()

    page = Page.Default()
    page += CTK.RawHTML ("<h1>%s: Reportes</h1>"%(ADMIN_LINK))

    table = CTK.Table()
    table[(1,1)] = CTK.RawHTML (LINK_HREF % ("%s/assets" % LOCATION, 'Reportes de activos'))
    table[(2,1)] = CTK.RawHTML (LINK_HREF % ("%s/system" % LOCATION, 'Reportes del sistema'))
    page += table
    return page.Render()


def init ():
    """Workflow management"""
    return WorkflowManager.steer (__file__)


def test ():
    from Util import test_page
    test_page (__file__)


CTK.publish ('^%s/?'         % LOCATION, init)
CTK.publish ('^%s/general/?' % LOCATION, default)
CTK.publish ('^%s/assets'    % LOCATION, report_assets)
CTK.publish ('^%s/system'    % LOCATION, report_system)


if __name__ == '__main__':
    test()


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
import Asset
import Collection

from ACL import ACL
from WidgetConsume import *
from CTK.consts import *
from consts import *
from DBSlayer import *
import PageLookup

LOCATION  = '/consume'

def parse_input ():
    """Parse input string and keep only ACL-consumable contents"""

    def parse_param (param):
        l = []
        for x in param[2:].split(','):
            try:
                l.append(int(x))
            except ValueError:
                pass
        return l

    params = CTK.request.url.split('/')[-1].split(';')

    col_ids, ass_ids, contents = [], [], []
    for param in params:
        if param.startswith('c='):
            for x in parse_param(param):
                col_ids.append(x)
        elif param.startswith('a='):
            for x in parse_param(param):
                ass_ids.append(x)

    acl = ACL()
    col_ids = acl.filter_collections ('co', col_ids)
    ass_ids = acl.filter_assets ('co', ass_ids)

    for x in col_ids:
        contents.append((Collection.Collection, x))
    for x in ass_ids:
        contents.append((Asset.Asset,x))
    return contents


def consume (contents = []):
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_CONSUMER)
    if fail: return fail

    page  = Page.Default()
    page += CTK.RawHTML ('<h2>%s</h2>' % BACK_LINK)

    if not contents:
        contents = parse_input()

    page += Paginate (contents, AbstractWidget)

    return page.Render()


def meta (contents = []):
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_CONSUMER)
    if fail: return fail

    page  = Page.Default()
    page += CTK.RawHTML ('<h2>%s Metadatos</h2>' % BACK_LINK)

    if not contents:
        contents = parse_input()

    page += Paginate (contents, MetaWidget)

    return page.Render()


def view (contents = []):
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_CONSUMER)
    if fail: return fail

    headers = ['<script type="text/javascript" src="%s"></script>'%FLOW_JS]
    page  = Page.Default(headers)
    if not contents:
        contents = parse_input()

    page += Paginate (contents, ViewWidget)

    return page.Render()


def test ():
    from Util import test_page
    test_page (__file__)


CTK.publish ('^%s/?'          % LOCATION, consume)
CTK.publish ('^%s/meta/.+?'   % LOCATION, meta)
CTK.publish ('^%s/view/.+?'   % LOCATION, view)


if __name__ == '__main__':
    test()

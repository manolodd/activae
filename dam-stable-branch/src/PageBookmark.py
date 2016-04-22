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

import urllib
import CTK
import Auth
import Role
import Page

from Bookmark import *
from WidgetConsume import *
from CTK.consts import *
from Asset import Asset

LOCATION   = '/bookmark'

#
# Toggle bookmark
#
def toggle_bookmark():
    """Bookmark asset"""

    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_CONSUMER)
    if fail: return fail

    params   = urllib.unquote_plus(CTK.request.url)
    params   = params.split('%s/'%LOCATION)[1].split(';')
    asset_id = int(params[0])
    asset    = Asset (asset_id)

    user_id  = Auth.get_user_id()
    if not asset['id']:
        return {'ret': "error"}

    bookmark = (asset_id, user_id)
    if bookmark_exists (bookmark):
        del_bookmark(bookmark)
    else:
        add_bookmark(bookmark)

    return {'ret': "ok"}

#
# Show bookmarks
#
def default ():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_CONSUMER)
    if fail: return fail

    # List of assets
    user_id = Auth.get_user_id()
    assets  = get_user_bookmarks (user_id)
    contents = [(Asset, x) for x in assets]

    page = Page.Default()
    page += CTK.RawHTML ("<h1>Favoritos</h1>")
    if len(contents):
        page += Paginate(contents, AbstractWidget)
    else:
        page += CTK.RawHTML ("<h2>No hay favoritos</h2>")
    return page.Render()


def test ():
    from Util import test_page
    test_page (__file__)


CTK.publish ('^%s/?'      % LOCATION, default)
CTK.publish ('^%s/\d+;.+' % LOCATION, toggle_bookmark)


if __name__ == '__main__':
    test()

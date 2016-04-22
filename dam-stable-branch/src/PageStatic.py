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
import Asset
import OpAsset
import Error
import os

from ACL import ACL
from OpLookup import OpLookup
from config import *


class XSendfile (CTK.HTTP_XSendfile):
    """Adds content-dispostion header to suggest a name to be saved"""
    def init_ (self, filename):
        CTK.HTTP_XSendfile.__init__ (self, filename)
        self['content-disposition'] = 'attachment; filename="%s"'%(os.path.basename(filename))


def update_views (asset_id):
    asset = Asset.Asset(asset_id)
    asset['views'] += 1
    oa = OpAsset.OpAsset(asset)
    rc = oa.update()
    if not rc:
        raise Error.SQLException


def match_asset (request):
    try:
        asset_id = int(request.split('/')[-1])
        asset = Asset.Asset(asset_id)
    except:
        return None

    if not asset['attachment']:
        return None

    if request.startswith('assets/'):
        update_views (asset_id)
        filename = '%s/%s/assets/%s'    % (STATIC_PATH, PRIVATE_PATH,
                                           asset['attachment'])
    elif request.startswith('thumbs/'):
        filename = '%s/%s/thumbs/%s.%s' % (STATIC_PATH, PRIVATE_PATH,
                                           asset['attachment'], THUMB_EXT)
    else:
        filename =  None
    return filename



def asset_link ():
    fail = Auth.assert_is_role (Role.ROLE_CONSUMER)
    if fail: return fail

    pre      = '%s/link/' % STATIC_PRIVATE
    request  = CTK.request.url[len(pre):]
    asset_id = request.split('/')[0]

    try:
        asset_id = int(asset_id)
        acl = ACL()
        asset_id = acl.filter_assets ("co" , [asset_id])[0]
        asset = Asset.Asset(asset_id)
    except:
        return CTK.HTTP_Error(403)

    if not asset['attachment']:
        return CTK.HTTP_Error(404)

    update_views (asset_id)
    filename = '%s/%s/assets/%s'    % (STATIC_PATH, PRIVATE_PATH,
                                       asset['attachment'])

    return XSendfile (filename)


def private ():
    fail = Auth.assert_is_role (Role.ROLE_CONSUMER)
    if fail: return fail

    request    = CTK.request.url[len(STATIC_PRIVATE)+1:]
    asset_id   = request.split('/')[-1]

    try:
        asset_id = int(asset_id)
        acl = ACL()
        asset_id = acl.filter_assets ("co" , [asset_id])[0]
    except:
        return CTK.HTTP_Error(403)

    filename = match_asset (request)
    if not filename:
        return CTK.HTTP_Error(404)

    return XSendfile (filename)


def public ():
    filename   = CTK.request.url[len(STATIC_URL)+1:]
    sendfile = "%s/%s" % (STATIC_PATH, filename)
    return XSendfile (sendfile)


def test ():
    from Util import test_page
    test_page (__file__)


CTK.publish ('^%s/link/\d+/.+' % STATIC_PRIVATE, asset_link)
CTK.publish ('^%s/.+'          % STATIC_PRIVATE, private)
CTK.publish ('^%s/.+'          % STATIC_PUBLIC,  public)

if __name__ == '__main__':
    test()


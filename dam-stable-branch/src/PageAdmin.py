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
import WorkflowManager

from CTK.consts import *
from config import *

LOCATION    = '/admin'

def wrap (entries):
    html = ''
    for entry in entries:
        url, icon, title, text = entry
        link = LINK_HREF % (url, '<img src="%s/%s" />%s' % (ICON_PATH, icon, title))
        elem = '<dt>%s</dt><dd>%s</dd>' % (link, text)
        html += elem
    return CTK.RawHTML ('<dl>%s</dl>'%(html))


def default():
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_ADMIN)
    if fail: return fail

    entries = [
               ('/report', 'icon_report.png', 'Reportes', 'Estadísticas del sistema'),
               ('/admin/user', 'icon_user.png', 'Usuarios', 'Gestionar cuentas de usuario'),
               ('/admin/profile', 'icon_profile.png', 'Perfiles', 'Configurar perfiles de negocio'),
               ('/admin/type', 'icon_type.png', 'Tipos', 'Gestionar tipos de activo'),
               ('/admin/format', 'icon_format.png', 'Formatos', 'Gestionar formatos de los activos'),
               ('/admin/license', 'icon_license.png', 'Licencias', 'Configuración de licencias'),
               ('/asset', 'icon_asset.png', 'Activos', 'Gestionar activos del sistema'),
               ('/collection', 'icon_collection.png', 'Colecciones', 'Gestionar colecciones del sistema'),
               ('/admin/acl', 'icon_permission.png', 'ACL', 'Gestionar permisos de activos y colecciones'),
               ]

    page  = Page.Default (body_id="admin_page")
    page += CTK.RawHTML('<h1>Administración Activae</h1>')
    page += wrap (entries)
    return page.Render()


def init ():
    """Workflow management"""
    return WorkflowManager.steer (__file__)


def test ():
    from Util import test_page
    test_page (__file__)


CTK.publish ('^%s/?'              % LOCATION, init)
CTK.publish ('^%s/general/?'      % LOCATION, default)


if __name__ == '__main__':
    test()

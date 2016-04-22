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

import os
import CTK
import Auth
import Role

class Menu (CTK.Container):
    def __init__ (self, **kwargs):
        CTK.Container.__init__ (self, **kwargs)
        try:
            auth = Auth.Auth()
            if not auth.is_logged_in ():
                return
        except AttributeError:
            return
        self.roles   = Role.get_user_roles ()
        self.user    = Auth.get_user()
        self.menu ()

    def menu (self):
        try:
            auth = Auth.Auth()
            if not auth.is_logged_in ():
                return
        except AttributeError:
            return
        self.menu_user ()
        if Role.ROLE_CONSUMER in self.roles:
            self.menu_consumer ()
        if Role.ROLE_UPLOADER in self.roles:
            self.menu_uploader ()
        if Role.ROLE_EDITOR in self.roles:
            self.menu_editor ()
        if Role.ROLE_PUBLISHER in self.roles:
            self.menu_publisher ()
        if Role.ROLE_ADMIN in self.roles:
            self.menu_admin ()

    def wrap (self, d):
        self += CTK.RawHTML ('<h2>%(name)s</h2>\n'%d)
        self += CTK.RawHTML ('<ul class="sidemenu">\n')

        entry = '<li><a href="%s">%s</a></li>\n'
        for link in d['links']:
            self += CTK.RawHTML (entry  % (link[0], link[1]))
        self += CTK.RawHTML ('</ul>\n')

    def menu_user (self):
        d = { 'name': self.user['username'],
              'links': [('/logout', 'Cerrar sesión')] }
        if self.user:
            link = ('/admin/user/%d' % self.user['id'], 'Editar usuario')
            d['links'].append (link)
        self.wrap(d)

    def menu_admin (self):
        d = { 'name': 'Administración',
              'links': [('/admin', 'Gestión de Activae'),
                        ] }
        self.wrap(d)

    def menu_uploader (self):
        d = { 'name': 'Creación',
              'links': [('/asset', 'Activos'),
                        ('/collection', 'Colecciones')] }
        self.wrap(d)

    def menu_editor (self):
        d = { 'name': 'Edición',
              'links': [('/asset/edit','Editar activos')] }
        self.wrap(d)

    def menu_publisher (self):
        d = { 'name': 'Publicación',
              'links': [('/asset/publish','Publicar activos')] }
        self.wrap(d)

    def menu_consumer (self):
        d = { 'name': 'Consumo',
              'links': [('/bookmark', 'Mis favoritos'),
                        ('/lookup', 'Buscar activos'),
                        ('/report', 'Estadísticas')] }
        self.wrap(d)

def test ():
    menu = Menu()
    menu.menu_consumer()
    menu.menu_uploader()
    menu.menu_editor()
    menu.menu_publisher()
    menu.menu_admin()
    render_str = menu.Render().toStr()
    for st in ['Consumo', 'Creación', 'Edición', 'Publicación',
    'Administración']:
        assert st in render_str
        print st, 'OK'

if __name__ == '__main__':
    test()

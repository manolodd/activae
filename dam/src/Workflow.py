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

import sys
import re
import Util

# Los flujos de trabajo para cada una de las páginas se pueden
# configurar fácilmente. Para cada página
SCRIPT = {
# Gestión de permisos
'PageACL':
    {'__default__':    '/', # Por defecto, no se proporciona acceso
     'admin':          '/admin/acl',
     'director':       '/acl/general',
     'editor':         '/acl/general',
     'guionista':      '/acl/general',
     'redactor':       '/acl/general',
     'documentalista': '/acl/general',
     'script':         '/acl/general',
     'disenador':      '/acl/general',
     'reportero':      '/acl/general',
     'efectos':        '/acl/general',
     'montador':       '/acl/general',
    },

# Gestión de formatos de activos
'PageAdmin':
    {'__default__':    '/', # Por defecto, no se proporciona acceso
     'admin':          '/admin/general',
    },

# Gestión de formatos de activos
'PageAdminFormats':
    {'__default__':    '/', # Por defecto, no se proporciona acceso
     'admin':          '/admin/format/general',
    },

#Gestión de licencias
'PageAdminLicenses':
    {'__default__':    '/', # Por defecto, no se proporciona acceso
     'admin':          '/admin/license/general',
    },

'PageAdminProfiles':
    {'__default__':    '/', # Por defecto, no se proporciona acceso
     'admin':          '/admin/profile/general',
    },

'PageAdminTypes':
    {'__default__':    '/', # Por defecto, no se proporciona acceso
     'admin':          '/admin/type/general',
    },

'PageAdminUsers':
    # Cada usuario puede modificar algunos de sus propios datos
    {'__default__':    '/admin/user/%(user_id)d',
     'admin':          '/admin/user/general',
    },

'PageAsset':
    {'__default__':    '/', # Por defecto, no se proporciona acceso
     'admin':          '/asset/general',
     'director':       '/asset/general',
     'productor':      '/asset/publish',
     'realizador':     '/asset/publish',
     'editor':         '/asset/general',
     'guionista':      '/asset/general',
     'redactor':       '/asset/general',
     'documentalista': '/asset/general',
     'script':         '/asset/general',
     'disenador':      '/asset/general',
     'reportero':      '/asset/general',
     'efectos':        '/asset/general',
     'montador':       '/asset/general',
    },

'PageAssetCreate':
    {'__default__':    '/asset', # Por defecto, lo que diga PageAsset
    },

'PageCollection':
    {'__default__':    '/', # Por defecto, no se proporciona acceso
     'admin':          '/collection/general',
     'director':       '/collection/general',
     'editor':         '/collection/general',
     'guionista':      '/collection/general',
     'redactor':       '/collection/general',
     'documentalista': '/collection/general',
     'script':         '/collection/general',
     'disenador':      '/collection/general',
     'reportero':      '/collection/general',
     'efectos':        '/collection/general',
     'montador':       '/collection/general',
    },


# Página de inicio
'PageIndex':
    {'__default__':    '/index', # Por defecto, indice
     'admin':          '/admin',
    },

'PageLookup':
    {'__default__':    '/lookup/general',
    },

'PageReport':
    {'__default__':    '/report/assets',
     'admin':          '/report/general',
    },

'PageTranscode':
    {'__default__':    '/', # Por defecto, no se proporciona acceso
     'admin':          '/transcode/%(param)s',
     'director':       '/transcode/%(param)s',
     'productor':      '/transcode/%(param)s',
     'realizador':     '/transcode/%(param)s',
     'guionista':      '/transcode/%(param)s',
    },

'PageUpload':
    {'__default__':    '/', # Por defecto, no se proporciona acceso
     'admin':          '/asset/upload/new',
     'director':       '/asset/upload/new',
     'editor':         '/asset/upload/new',
     'guionista':      '/asset/upload/new',
     'redactor':       '/asset/upload/new',
     'documentalista': '/asset/upload/new',
     'script':         '/asset/upload/new',
     'disenador':      '/asset/upload/new',
     'reportero':      '/asset/upload/new',
     'efectos':        '/asset/upload/new',
     'montador':       '/asset/upload/new',
    },
}

"""
Variables utilizables en las rutas:
-----------------------------------
%(request)s       url de entrada
%(profile_id)d    id del perfil del usuario
%(profile_name)d  nombre del perfil del usuario
%(user_id)d       id del usuario
%(user_name)s     nombre del usuario
%(param)s         parámetros (desde la última '/' en adelante)

Perfiles:
---------
    {
     '__default__':    '/', # Destino para perfil por defecto
     'admin':          '',
     'director':       '',
     'productor':      '',
     'realizador':     '',
     'editor':         '',
     'regidor':        '',
     'guionista':      '',
     'redactor':       '',
     'documentalista': '',
     'script':         '',
     'disenador':      '',
     'reportero':      '',
     'efectos':        '',
     'montador':       '',
     'actor':          '',
     'presentador':    '',
    },

Targets:
--------

PageACL
'/acl/general/?'        , default_user
'/acl/asset/\d+'        , edit_acl
'/acl/collection/\d+'   , edit_acl
'/admin/acl/?'          , default_admin

PageAdmin
'/admin/?'              , init
'/admingeneral/?'       , default

PageAdminFormats
'/admin/format/general' , default
'/admin/format/del/.+'  , del_format
'/admin/format/edit/.+' , edit_format
'/admin/format/edit/del/\d+/\d+$' , del_format_target

PageAdminLicenses
'/admin/license/general', default
'/admin/license/del/.+' , del_license
'/admin/license/new$' % , new_license
'/admin/license/edit/.+', edit_license

PageAdminProfiles
'/admin/profile/general', default
'/admin/profile/.+'     , edit_profile
'/admin/profile/del/.+' , del_profile
'/admin/profile/new'    , new_profile

PageAdminTypes
'/admin/type/general'   , default
'/admin/type/del/.+'    , del_type
'/admin/type/new$'      , new_type
'/admin/type/edit/.+'   , edit_type

PageAdminUsers
'/admin/user/general'   , default
'/admin/user/\d+'       , edit_user
'/admin/user/new'       , new_user
'/admin/user/del/\d+'   , del_user

PageAsset
/asset/general'        , default
/asset/del/.+'         , del_asset
/asset/new/?$'         , add_asset
/asset/new/name=(.+?/ref=(.+?' , add_asset
/asset/evolve/.+'      , evolve_asset
/asset/edit/?$'        , edit_asset_page
/asset/publish/?$'     , publish_asset

PageAssetCreate
'/asset/create/?'      , init)
'/asset/new/?'         , add_asset)
'/asset/new/name=(.+)?/ref=(.+)?', add_asset
'/asset/evolve/.+'     , evolve_asset

PageCollection
'/collection/general'  , default
'/collection/new$'     , add_collection
'/collection/edit/.+'  , edit_collection
'/collection/meta/\d+$', show_meta

PageIndex
'/index'               , default
'/'                    , init

PageLookup
'/lookup/general'      , default
'/lookup/?.+'          , lookup_perform

PageReport
'/report/?'            , default
'/report/assets'       , report_assets
'/report/system'       , report_system

PageTranscode
'/transcode/\d+/?'     , transcode

PageUpload
'/asset/upload/?'            , UploadNew
'/asset/upload/new/?'        , UploadNew
'/asset/upload/evolve/\d+/?' , UploadEvolve
"""

def get_pages ():
    txt   = open(__file__).read()
    supported  = SCRIPT.keys()
    documented = re.findall("\n(Page.+?)\n", txt)
    existing   = Util.get_all_pages()

    return (supported, documented, existing)

def test ():
    supported, documented, existing = get_pages()
    print '#1 Páginas con soporte de workflow: %d' % len(supported)
    print '#2 Páginas documentadas:            %d' % len(documented)
    print '#3 Páginas totales:                 %d' % len(existing)

    not_documented = list(set(supported) - set(documented))
    assert len(not_documented) == 0
    print '#4 Páginas sin documentar (0): OK'

    assert len(supported) == len(documented)
    print '#5 Documentadas todas las páginas con soporte de Workflow: OK'

    not_supported = list(set(existing) - set(supported))
    print '#6 Páginas sin workflow (%d): %s' % (len(not_supported),not_supported)


if __name__ == '__main__':
    test()

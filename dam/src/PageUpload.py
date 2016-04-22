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
import tempfile
import CTK
import Auth
import Role
import Page
import Upload
import WorkflowManager

from CTK.consts import *
from config import *

PAGEASSET_LOCATION = '/asset'
LOCATION    = '/asset/upload'
MENU_LINK   = LINK_HREF % (PAGEASSET_LOCATION,'Activos')
NO_LIMIT    = 'Sin límite'

def report_upload_new (filename, target_dir, target_file, params):
    operation = Limiter(os.path.join (target_file))
    if not operation.is_allowed():
        return page_forbidden (operation)

    target_file = target_file.split('/')[-1]
    location  = PAGEASSET_LOCATION
    redir = ('%(location)s/new/name='
             '%(filename)s/ref=%(target_file)s' % locals())
    return Page.Redir(redir).Render()

def report_upload_evolve (filename, target_dir, target_file, params):
    operation = Limiter(os.path.join (target_file))
    if not operation.is_allowed():
        return page_forbidden (operation)

    target_file = target_file.split('/')[-1]
    location  = PAGEASSET_LOCATION
    parent_id = params.get('parent_id')
    redir     = ('%(location)s/evolve/parent=%(parent_id)s/name='
                 '%(filename)s/ref=%(target_file)s' % locals())
    return Page.Redir(redir).Render()

def page_forbidden (limiter):
    # Authentication
    fail = Auth.assert_is_role (Role.ROLE_UPLOADER)
    if fail: return fail

    for key,value in limiter.limits.items():
        if value==0:
            limiter.limits[key] = NO_LIMIT

    rows = [('Número de archivos',       limiter.usage['files'], limiter.limits['files']),
            ('Total del sistema',        limiter.usage['total'], limiter.limits['total']),
            ('Tamaño máximo de archivo', limiter.usage['size'],  limiter.limits['size'])]

    header = ['Restricción', 'Uso', 'Límite']
    table = CTK.Table()
    table[(1,1)] = [CTK.RawHTML(x) for x in header]
    table.set_header (row=True, num=1)

    for x in range(len(rows)):
        table[(x+2,1)] = [CTK.RawHTML (str(column)) for column in rows[x]]

    page  = Page.Default()
    page += CTK.RawHTML ("<h1>%s: Subir ficheros</h1>" %(MENU_LINK))
    page += CTK.RawHTML ("<h2>Se han excedido los límites</h2>")
    page += table

    return page.Render()

class Limiter:
    """Determine if a system limit prevents from uploading files"""

    def __init__ (self, target_file = None):
        user_id      = Auth.get_user_id ()
        user_usage   = Upload.get_usage_user (user_id)
        system_usage = Upload.get_usage_system()
        self.limits  = {
            'size'  : LIMIT_ASSET_SIZE,
            'files' : LIMIT_ASSET_FILES,
            'total' : LIMIT_ASSET_TOTAL
            }
        self.usage   = {
            'size'  : 0,
            'files' : user_usage['files'],
            'total' : system_usage['size']
            }

        if target_file:
            self.usage['size'] = os.path.getsize (target_file)


    def is_allowed (self):
        self.allow = True

        if self.limits['total']:
            if self.limits['total'] <= self.usage['total']:
                self.allow = False

        if self.limits['files']:
            if self.limits['files'] <= self.usage['files']:
                self.allow = False

        if self.limits['size']:
            if self.limits['size'] <= self.usage['size']:
                self.allow = False

        return self.allow


class UploadNew:
    def __init__ (self):
        self.target_dir = UPLOAD_PATH

    def __call__ (self):
        # Authentication
        fail = Auth.assert_is_role (Role.ROLE_UPLOADER)
        if fail: return fail
        operation = Limiter()
        if not operation.is_allowed():
            return page_forbidden (operation)

        self.page  = Page.Default()
        self.page += CTK.RawHTML ("<h1>%s: Subir ficheros</h1>" %(MENU_LINK))
        self.page += CTK.Uploader({'handler':    report_upload_new,
                                   'target_dir': self.target_dir},
                                  direct = False)
        self.page += CTK.RawHTML (LINK_HREF % ('%s/new'%PAGEASSET_LOCATION,
                                               'Crear sin fichero adjunto'))
        return self.page.Render()


class UploadEvolve:
    def __init__ (self):
        self.target_dir = UPLOAD_PATH

    def __call__ (self):
        # Authentication
        fail = Auth.assert_is_role (Role.ROLE_UPLOADER)
        if fail: return fail

        operation = Limiter()
        if not operation.is_allowed():
            return page_forbidden (operation)

        parent_id  = CTK.request.url[len('%s/evolve/parent=' % LOCATION):].split('/')[0]
        self.params     = {'parent_id':parent_id}
        link = LINK_HREF % ('%s/evolve/parent=%s'%(PAGEASSET_LOCATION,parent_id),
                            'Crear sin fichero adjunto')

        self.page  = Page.Default()
        self.page += CTK.RawHTML ("<h1>%s: Subir ficheros</h1>" %(MENU_LINK))
        self.page += CTK.Uploader({'handler':    report_upload_evolve,
                                   'target_dir': self.target_dir},
                                   self.params, direct = False)
        self.page += CTK.RawHTML (link)

        return self.page.Render()


def init ():
    """Workflow management"""
    return WorkflowManager.steer (__file__)


def test ():
    from Util import test_page
    test_page (__file__)


CTK.publish ('^%s/?'                  % LOCATION, init)
CTK.publish ('^%s/new/?'               % LOCATION, UploadNew)
CTK.publish ('^%s/evolve/parent=\d+/?' % LOCATION, UploadEvolve)


if __name__ == '__main__':
    test()

#!/usr/bin/env python
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

from xmlrpclib import ServerProxy

import Asset
from Error import *
from DBSlayer import Query, query_check_success
from Upload import get_info
import OpAsset
import config

class Conversion():
    def __init__ (self):
        pass

    def transcode (self, asset_id, target_id):
        params = {'roles':config.LOOKUP_ROLES, 'user_id':config.LOOKUP_USERID}
        asset = Asset.Asset(asset_id)
        op  = OpAsset.OpAsset(asset, params)
        task_id = op.transcode (target_id, programatic=True)

        if not task_id:
            raise InternalError, 'Could not transcode asset'
        return task_id

    def lookup_formats (self, asset_id):
        formats = []
        asset = Asset.Asset(asset_id)

        if not asset._file.get('filename'):
            return formats

        format_id = asset._file.get('formats_id')
        if not format_id:
            info = get_info (asset._file.get('filename'))
            format_id = info.get('formats_id', None)

        if not format_id:
            return formats

        sql = "SELECT * FROM transcode_targets "\
              "JOIN formats ON target_id=formats.id "\
              "WHERE source_id = %(format_id)s;" %(locals())
        q = Query(sql)

        if not len(q):
            return formats

        for x in q:
            r = {'lossy':     q[x]['lossy_flag'],
                 'target_id': q[x]['target_id'],
                 'format':    q[x]['format'] }
            formats.append(r)
        return formats

    def task_status (self, task_id):
        try:
            client = ServerProxy ("http://%s:%s/"%(config.QUEUE_SERVER, config.QUEUE_PORT))
            ret = client.GetTaskStatus (task_id)
            if ret == -1:
                st = 'processing'
            elif ret == 1:
                st = 'processed'
            else:
                st = 'fail'
        except Exception,e:
            st = str(e)
        return st


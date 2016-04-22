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


MEDIA_PATH     = '/opt/activae/src/static/private/assets'
FORMATS        = ['mp3', 'ogg', 'avi', 'mp4', 'flv', 'h264']
TEST_PATH      = '/tmp/activae_queue_stressing'
QUEUE_SERVER   = "127.0.0.1"
QUEUE_PORT     = 8001

import os
import errno
from xmlrpclib import ServerProxy
import mimetypes

def mkdir_p(path):
    try:
        os.makedirs(path, mode=777)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

def main():
    mkdir_p (TEST_PATH)

    # Dispatcher
    http = "http://%s:%s/" % (QUEUE_SERVER, QUEUE_PORT)
    client = ServerProxy (http)

    for media in os.listdir(MEDIA_PATH):
        source = '%s/%s' %(MEDIA_PATH,media)

        if os.path.isfile(source):
            mimetype, encoding = mimetypes.guess_type (source)
            if not mimetype:
                continue
            type_name = mimetype.split('/')[0]

            if type_name not in ['video', 'audio']:
                continue

            convert = client.ConvertMedia
            thumb   = client.BuildThumbnailMedia
            name    = os.path.basename (source)

            for format in FORMATS:
                target  = '%s/%s.%s' % (TEST_PATH, name, format)
                task_id = convert (source, target, format)

                if not task_id:
                    raise ValueError, 'Fail: %s->%s' %(source,target)
                else:
                    print 'OK (%s): %s->%s' %(task_id,source,target)

if __name__ == "__main__":
    main()

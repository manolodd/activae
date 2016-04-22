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
import sys
import time
sys.path.append ("..")
import VFS
import converters
import status
import processors
import Error

class WorkerOperations:
    """Methods that enqueue will return a unique ID"""
    def __init__ (self, jobs):
        self.jobs   = jobs

    def ping (self, arg):
        assert arg == 'ping', "Did not receive a proper Ping"
        return "pong"

    # Media files
    #
    def ConvertMedia (self, source, target, format):
        # Download file input file, if needed
        local_in = VFS.local_reference (source)
        assert local_in[0] == '/', "A local copy of the file is required"

        # Video Converter
        vc = converters.VideoConverter()
        args = (local_in, target, format)

        task_id = (int(time.time()*10**6)) & 0xFFFFFFF
        callback = processors.FileCallback (task_id)

        self.jobs.put ((vc.convert, args, callback, task_id))
        status.status[task_id] = -1

        return task_id

    def BuildThumbnailMedia (self, source, target):
        # Download file input file, if needed
        local_in = VFS.local_reference (source)
        assert local_in[0] == '/', "A local copy of the file is required"

        # Video Converter
        thumbnailer = converters.VideoThumbnail()
        thumbnailer.generate (local_in, target)

        # Check the new file
        if not os.path.exists (target):
            return "failed"
        if os.path.getsize (target) < 1:
            return "failed"

        return "ok"

    def GetInfoMedia (self, source):
        # Download file input file, if needed
        local_in = VFS.local_reference (source)
        assert local_in[0] == '/', "A local copy of the file is required"

        # Video Converter
        infor = converters.VideoInfo()
        dict_info = infor.get (local_in)

        # Check the information retrieved
        if not dict_info:
            return "failed"

        return ("ok", dict_info)


    # Image
    #
    def ConvertImage (self, source, target, format):
        # Download file input file, if needed
        local_in = VFS.local_reference (source)
        assert local_in[0] == '/', "A local copy of the file is required"

        # Video Converter
        ic = converters.ImageConverter()
        args = (local_in, target, format)

        task_id = (int(time.time()*10**6)) & 0xFFFFFFF
        callback = processors.FileCallback (task_id)

        self.jobs.put ((ic.convert, args, callback, task_id))
        status.status[task_id] = -1

        return task_id

    def BuildThumbnailImage (self, source, target):
        # Download file input file, if needed
        local_in = VFS.local_reference (source)
        assert local_in[0] == '/', "A local copy of the file is required"

        # Video Converter
        thumbnailer = converters.ImageThumbnail()
        thumbnailer.generate (local_in, target)

        # Check the new file
        if not os.path.exists (target):
            return "failed"
        if os.path.getsize (target) < 1:
            return "failed"

        return "ok"

    def GetInfoImage (self, source):
        # Download file input file, if needed
        local_in = VFS.local_reference (source)
        assert local_in[0] == '/', "A local copy of the file is required"

        # Video Converter
        infor = converters.ImageInfo()
        dict_info = infor.get (local_in)

        # Check the information retrieved
        if not dict_info:
            return "failed"

        return ("ok", dict_info)

    # Misc Methods
    #
    def GetTaskStatus (self, task_id):
        """Find out the status of an enqueued task"""
        st = {}
        for k,v in status.status.items():
            st[int(k)]=v

        if st.has_key(int(task_id)):
            return st[int(task_id)]
        else:
            raise Error.Invalid

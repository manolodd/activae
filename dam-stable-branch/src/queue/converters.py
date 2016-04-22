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
import re
import sys
import shutil
sys.path.append("..")
import Upload
from config import *
from VFS import *

path      = "%s/bin:%s/sbin" % (BASE_DIR, BASE_DIR)
path_prev = os.getenv("PATH")

if path_prev and (not path in path_prev):
    os.putenv ("PATH", "%s/bin:%s/sbin:%s"%(BASE_DIR, BASE_DIR, path_prev))
else:
    os.putenv ("PATH", "%s/bin:%s/sbin"%(BASE_DIR, BASE_DIR))
os.putenv ("LD_LIBRARY_PATH","%s/lib"%(BASE_DIR))

# Video
#
VIDEO_OPTIONS = {'flv':  '-sameq -ar 44100',
                 'h264': '-sameq -vcodec libx264 -vpre hq',
                 'h261': '-sameq -s 352x288',
                 'dv':   '-sameq -target pal-dv',
                 'm4v':  '-sameq -vcodec mpeg4 -f m4v',
                 'vcd':  '-sameq -target pal-vcd',
                 'mpeg2video': '-sameq -vcodec mpeg2video -f mpeg',
                 'matroska':   '-sameq -f matroska',
                 'rawvideo':   '-sameq -f rawvideo',
                 }


class VideoConverter:
    def __init__ (self):
        None

    def convert (self, input, target, format):
        extra_options = VIDEO_OPTIONS.get(format, '')

        try:
            # Let ffmpeg work its magic
            rc = exe ("LD_LIBRARY_PATH=%s/lib %s/bin/ffmpeg -y -i '%s' %s '%s'" % (BASE_DIR, BASE_DIR, input, extra_options, target))
        except:
            print 'Could not convert: %s -> %s'%(input, target)
            rc = 1

        return rc


class VideoThumbnail:
    def __init__ (self):
        None

    def generate (self, input, target):
        target_base, target_ext = os.path.splitext (target)
        mtype = Upload.get_type(target_base)

        if mtype not in ['audio', 'image', 'text', 'video']:
            mtype = None

        icons = {'audio': THUMB_ABS_ASSET_AUDIO,
                 'image': THUMB_ABS_ASSET_IMAGE,
                 'text':  THUMB_ABS_ASSET_TEXT,
                 'video': THUMB_ABS_ASSET_VIDEO,
                 None   : THUMB_ABS_ASSET,}

        if mtype not in ['video','image']:
            shutil.copyfile (icons[mtype], target)
            return

        try:
            exe ("LD_LIBRARY_PATH=%s/lib %s/bin/ffmpeg -y -i '%s' -itsoffset -%d -vcodec mjpeg -vframes 1 -an -f rawvideo -s %s '%s'" % (
                    BASE_DIR, BASE_DIR, input, THUMB_VIDEO_OFFSET, THUMB_SIZE, target))
        except:
            print 'Could not convert: %s -> %s'%(input, target)


class VideoInfo:
    def __init__ (self):
        None

    def get (self, input):
        info = {}
        txt = exe_output ("LD_LIBRARY_PATH=%s/lib %s/bin/ffmpeg -i '%s' 2>&1" % (BASE_DIR, BASE_DIR, input))

        # Duration
        tmp = re.findall ("Duration: (.+?), ", txt)
        if tmp:
            # Raw duration: hh:mm:ss.ms
            info['duration_str'] = tmp[0]

            # Duration in seconds
            hms_str = tmp[0].split('.')[0]
            hms = hms_str.split(":")
            secs = (int(hms[0])*(60*60)) + (int(hms[1])*60) + int(hms[2])
            info['duration'] = str(secs)

        # Bitrate
        tmp = re.findall ("Duration: .*?, bitrate: (.*?)[,$\n\r]", txt)
        if tmp:
            info['bitrate'] = tmp[0]

        # Video size
        tmp = re.findall ("Video:.*? (\d+x\d+) ", txt)
        if tmp:
            info['size'] = tmp[0]

        # Format
        tmp = re.findall ("Input #0, (.*?), from .*?[,$\n\r]", txt)
        if tmp:
            info['formats'] = tmp[0].split(',')

        return info

# Image
#
class ImageConverter:
    def __init__ (self):
        None

    def convert (self, input, target, format):
        try:
            # Let imagegamick work its magic
            rc = exe ("%s/bin/convert '%s' '%s'" % (BASE_DIR, input, target))
        except:
            print 'Could not convert: %s -> %s'%(input, target)
            rc = 1

        return rc

class ImageThumbnail:
    def __init__ (self):
        None

    def generate (self, input, target):
        try:
            exe ("%s/bin/convert -size %s '%s' -strip -coalesce -resize %s -quality 85 '%s'" % (BASE_DIR, THUMB_SIZE, input, THUMB_SIZE, target))
        except:
            print 'Could not convert: %s -> %s'%(input, target)

class ImageInfo:
    def __init__ (self):
        None

    def get (self, input):
        info = {}
        txt = exe_output ("%s/bin/identify '%s' 2>&1" % (BASE_DIR, input))

        tmp = re.findall ("(.+?) (.*?) (\d+x\d+) .* (\d)*-bit ", txt)
        if tmp:
            info['format'] = tmp[0][1]
            info['size']   = tmp[0][2]
            info['bits']   = tmp[0][3]

        return info

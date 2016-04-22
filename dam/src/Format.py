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

from DBSlayer import Query

TRANSCODE_TYPES = ['audio','video','image']

# ffmpeg -formats|grep '^ .E [a-z]'|sed 's/ .. //'|cut -f1 -d' '
# Those are writeable formats
# For list of codecs it should be:
# ffmpeg -formats|grep '^ ...... [a-z]'|sed 's/^ ...... //'|cut -f1 -d' '
#
FFMPEG_FORMATS = [
'ac3',
'adts',
'aiff',
'alaw',
'alsa',
'amr',
'asf',
'ass',
'au',
'avi',
'avm2',
'crc',
'dirac',
'dnxhd',
'dv',
'dvd',
'eac3',
'ffm',
'flac',
'flv',
'framecrc',
'h261',
'h263',
'h264',
'ipod',
'm4v',
'matroska',
'mjpeg',
'mkv',
'mov',
'mp2',
'mp3',
'mp4',
'mpeg',
'mpeg1video',
'mpeg2video',
'mpg',
'mpjpeg',
'mulaw',
'mxf',
'mxf_d10',
'null',
'nut',
'ogg',
'ogv',
'oss',
'psp',
'rawvideo',
'rm',
'svcd',
'vcd',
'vob',
'voc',
'wav',
]

# `identify -list format|grep rw|sed 's/*/ /'|sed 's/^\s*//'|cut -f1 -d' '`
# Those are read-write formats
IMAGEMAGICK_FORMATS = [
'A',
'AI',
'ART',
'AVS',
'B',
'BGR',
'BMP',
'BRG',
'C',
'CIN',
'CMYK',
'CMYKA',
'DCX',
'DPX',
'EPDF',
'EPI',
'EPS',
'EPSF',
'EPSI',
'EPT',
'EPT2',
'EPT3',
'EXR',
'FAX',
'FITS',
'FTS',
'G',
'G3',
'GBR',
'GIF',
'GIF87',
'GRAY',
'GRB',
'HRZ',
'ICB',
'IPL',
'JNG',
'JP2',
'JPC',
'JPEG',
'JPG',
'K',
'M',
'M2V',
'MAP',
'MAT',
'MIFF',
'MNG',
'MONO',
'MPC',
'MSVG',
'MTV',
'NULL',
'O',
'OTB',
'PAL',
'PALM',
'PAM',
'PBM',
'PCD',
'PCDS',
'PCL',
'PCT',
'PCX',
'PDB',
'PDF',
'PDFA',
'PFM',
'PGM',
'PICON',
'PICT',
'PJPEG',
'PNG',
'PNG24',
'PNG32',
'PNG8',
'PNM',
'PPM',
'PS',
'PSD',
'PTIF',
'R',
'RAS',
'RBG',
'RGB',
'RGBA',
'RGBO',
'SGI',
'SUN',
'SVG',
'SVGZ',
'TEXT',
'TGA',
'TIFF',
'TXT',
'UYVY',
'VDA',
'VICAR',
'VID',
'VIFF',
'VST',
'WBMP',
'X',
'XBM',
'XPM',
'XV',
'XWD',
'Y',
'YCbCr',
'YCbCrA',
'YUV',
]

def _delete_duplicates (in_list):
    lowercase_list = [x.lower() for x in in_list]
    lst = {}.fromkeys(lowercase_list).keys()
    lst.sort()
    return lst

AV      = _delete_duplicates (FFMPEG_FORMATS)
IMG     = _delete_duplicates (IMAGEMAGICK_FORMATS)
FORMATS = _delete_duplicates (IMG + AV)



def get_format_name (format_id):
    if not format_id:
        return None
    f = get_format (format_id)
    if not f:
        return None
    return f['name'].upper()

def get_format (format_id):
    formats = get_formats()
    for f in formats:
        if f['id'] == int(format_id):
            return f
    return None

def get_format_id (format_name):
    formats = get_formats()
    for f in formats:
        if f['name'].lower() == format_name.lower():
            return f['id']
    return None

def get_formats ():
    q = "SELECT * "\
        "FROM formats;"

    query = Query(q)
    if len(query) == 0:
        return None

    formats = []
    for x in query:
        f = {'id':          query[x]['id'],
             'name':        query[x]['format'],
             'lossy_flag':  query[x]['lossy_flag']}
        formats.append(f)
    return formats



def test ():
    import sys

    try:
        format_id = sys.argv[1]
    except IndexError:
        print 'Required test parameters: format_id'
        sys.exit(1)

    format_name = get_format_name(format_id)
    print 'Formats:', get_formats()
    print '\nThis format:', get_format(format_id)
    print '\nformat_id %s, format_name %s' % (get_format_id(format_name.lower()), format_name)

if __name__ == '__main__':
    test()

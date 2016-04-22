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
import stat
import tempfile
import time
import zipfile
import mimetypes
import shutil
import queue.converters as converters
import queue.VFS as VFS
import Error
import File

from xmlrpclib import ServerProxy
from DBSlayer import Query
from config import *
from Format import get_format_id


def is_zipped (fullname):
   try:
      zf = zipfile.ZipFile(fullname)
      return True
   except:
      return False

def process_file (filename, original_name):
   """Return needed data for immediate asset creation and enqueue the
   rest of the process"""

   fullname = os.path.join (UPLOAD_PATH, filename)
   names = get_names (fullname, original_name)
   file_list = names.values()

   files = do_process (fullname, original_name, names)

   if not files:
      raise Error.Empty

   return file_list


def get_names (fullname, original_name):

   if UNZIP_COLLECTIONS and is_zipped (fullname):
      zf = zipfile.ZipFile(fullname)
      files = [f for f in zf.namelist() if not f.endswith('/')]
   else:
      files = [original_name]

   result = {}

   current_files = os.listdir (ASSET_PATH)
   for x in files:
      x = os.path.basename(x)
      result[x] = get_unused_name(x, current_files)
      current_files.append (result[x])

   return result


def get_unused_name (filename, current_files):
   """Return a file name that is not already in use"""

   filename = os.path.basename (filename)
   if filename not in current_files:
      return filename

   name,ext = os.path.splitext (filename)
   new_name = tempfile.mktemp(suffix=ext, prefix=PROJECT_NAME, dir=ASSET_PATH)
   return os.path.basename(new_name)


def get_usage_user (user_id):
    q = ("SELECT IFNULL(SUM(size),0) AS size, "
         "COUNT(size) AS files "
         "FROM files "
         "JOIN assets ON assets.id = files.id "
         "WHERE creator_id=%s;" % str(user_id))
    query = Query(q)
    return {'files': int(query['files'][0]),
            'size':  int(query['size'][0])}


def get_usage_system ():
    q = "SELECT IFNULL(SUM(size),0) AS size, COUNT(size) AS files FROM files;"
    query = Query(q)
    return {'files': int(query['files'][0]),
            'size':  int(query['size'][0])}


def get_thumbnail (filename):
   base_name= os.path.basename(filename)
   thumb    = '%s/%s.%s' % (THUMB_PATH, base_name, THUMB_EXT)

   filetype = get_type(filename)
   if filetype == 'video':
      worker = converters.VideoThumbnail()
      worker.generate(filename, thumb)
   elif filetype == 'image':
      worker = converters.ImageThumbnail()
      worker.generate(filename, thumb)


def get_type (filename):
   """Determine filetype"""

   mimetype, encoding = mimetypes.guess_type (filename)
   if not mimetype:
      return None
   type_name = mimetype.split('/')[0]
   if type_name not in ['video', 'image']:
      # Extra attention to the ones we actually do something with
      txt = VFS.exe_output ('file %s' % filename)
      txt = txt.lower()
      if 'video' in txt:
         type_name = 'video'
      elif 'image' in txt:
         type_name = 'image'
   return type_name

def is_video (filename):
   if get_type(filename) == 'video':
      return True
   return False

def is_image (filename):
   if get_type(filename) == 'image':
      return True
   return False

def determine_format_id (fullname):
   # Last resort: identify by mime and/or extension
   try:
      mime, enc = mimetypes.guess_type(fullname)
      ext       = mimetypes.guess_extension (mime)
      format_id = get_format_id (ext[1:])
   except:
      format_id = None

   if not format_id:
      _, ext = os.path.splitext(fullname)
      format_id = get_format_id (ext[1:])

   return format_id

def get_info (filename):
   info = {'size':0, 'filename': None}
   try:
      info = get_info_aux (filename)
   except:
      pass
   return info

def get_info_aux (filename):
   if not filename:
      raise AttributeError

   fullname = os.path.join (ASSET_PATH, filename)
   filesize = int(os.path.getsize(fullname))

   info = {'size':     filesize,
           'filename': filename }

   if is_video(fullname):
      worker = converters.VideoInfo()
      data = worker.get(fullname)

      bps = data.get('bitrate', None).split()[0]
      try:
         bps = 2**10 * int(bps)
         data['bitrate'] = bps
      except:
         pass

   elif is_image (fullname):
      worker = converters.ImageInfo()
      data = worker.get(fullname)
   else:
      format_id = determine_format_id (fullname)
      if format_id:
         info['formats_id'] = format_id
      return info

   try:
      dim = data['size'].split('x')
      x,y = dim[0], dim[1]
   except (KeyError,IndexError):
      x,y = 0,0

   format_id = None
   if data.get('format'):
      format = data['format']
      format_id = get_format_id (format)
   elif data.get('formats'):
      for format in data['formats']:
         format_id = get_format_id (format)
         if format_id:
            break

   info['width']   = x
   info['height']  = y
   info['extent']  = data.get('duration_str')
   info['bitrate'] = data.get('bitrate', None)

   # Last detection method for the format_id
   if not format_id:
      format_id = determine_format_id (fullname)

   if format_id:
      info['formats_id'] = format_id

   return info


def do_process (filename, original_name, name_conversions):
   """Process file and move it to ASSET_PATH. Unzip if
   necessary. Return the list of processed files"""
   tmp_dir  = tempfile.mkdtemp(dir=UPLOAD_PATH)
   src_name  = os.path.join(UPLOAD_PATH,filename)
   fullname  = os.path.join(tmp_dir, original_name)
   os.rename(src_name, fullname)

   if UNZIP_COLLECTIONS and extract (fullname):
      os.unlink (fullname)

   dir_name      = os.path.dirname(fullname)
   new_files     = []
   for subdir, dirs, files in os.walk(dir_name):
      for src_name in files:
         src = os.path.join(subdir, src_name)
         if src_name in name_conversions:
            dst_name = name_conversions[src_name]
         else:
            continue
         new_name = os.path.join(ASSET_PATH, dst_name)
         os.rename(src, new_name)
         get_thumbnail(new_name)
         new_files.append (new_name)

   shutil.rmtree(tmp_dir)
   return new_files


def extract (fullname):
   try:
      zf = zipfile.ZipFile(fullname)
   except (zipfile.BadZipfile, IOError):
      return False

   dir_name = os.path.dirname(fullname)
   tmp_dir = tempfile.mkdtemp(dir=dir_name)
   zf.extractall (tmp_dir)
   return True


def test ():
    import sys

    try:
        user_id = int(sys.argv[1])
        filename = sys.argv[2]
        test_name = 'Upload.py_unit_testing'
    except IndexError:
        print 'Required test parameters: user_id test_filename'
        sys.exit(1)

    print "#1 is_zipped (%s):" % filename, is_zipped(filename)

    names = get_names (filename, test_name)
    assert names[test_name] == test_name
    print "#2 get_names (): OK"
    print "#3 get_unused_name:", get_unused_name (filename, [])
    print "#4 get_usage_user():", get_usage_user (user_id)
    print "#5 get_usage_system():", get_usage_system()

    print "#6 get_type(%s):"  % filename, get_type (filename)
    print "#7 is_video (%s):" % filename, is_video (filename)
    print "#8 is_image (%s):" % filename, is_image (filename)
    try:
       info = get_info(filename)
    except OSError: # Expected
       pass
    print "#9 get_info(%s): OK" % filename

if __name__ == '__main__':
    test()

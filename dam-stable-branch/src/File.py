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

from DBSlayer import Query,transaction_check_success
from config import *
import Error
import Upload

def get_files_by_flag (flag):
    q = "SELECT * "\
        "FROM files "\
        "WHERE queue_flag = %s;" % flag

    query = Query(q)

    if len(query) == 0:
        return []

    files = []
    for x in query:
        f = {}
        for key in query.get_headers():
            f[key]= query[x][key]
        files.append(f)
    return files

def update_files (files):
    q = ''
    for f in files:
        sql_columns, sql_values = [], []
        for key,value in f.items():
            if value != None:
                sql_columns.append(key)
                sql_values.append("'%s'" % value)

        q += "REPLACE INTO files (%s) VALUES (%s);" \
            % (','.join(sql_columns), ','.join(sql_values))

    q = 'START TRANSACTION; %s COMMIT' % q
    ok = transaction_check_success (q)
    if not ok:
        raise Error.SQLException

def delete_file (the_file):
    q = 'DELETE FROM files WHERE id = %s;' % the_file['id']
    q = 'START TRANSACTION; %s COMMIT' % q

    ok = transaction_check_success (q)
    if not ok:
        raise Error.SQLException

    filename = the_file.get('filename')
    media = '%s/%s'    % (ASSET_PATH, filename)
    thumb = '%s/%s.%s' % (THUMB_PATH, filename, THUMB_EXT)
    try:
        os.unlink(media)
        os.unlink(thumb)
    except:
        return False

    return True

def get_files_by_name (filenames):
    assert type(filenames) == list

    names = ','.join(["'%s'"% f for f in filenames])
    q = "SELECT * "\
        "FROM files "\
        "WHERE filename IN (%s);" % names

    query = Query(q)
    if len(query) == 0:
        return []

    files = []
    for x in query:
        f = {}
        for key in query.get_headers():
            if query[x][key]:
                f[key]= query[x][key]
        files.append(f)
    return files

def unset_flag (flag):
    q = "UPDATE files SET queue_flag=0 WHERE queue_flag=%s;" %(flag);
    query = Query(q)

def clone_file (file_info):
    """Duplicate a file on disk, returning a file_info dict or raising an IOError"""
    assert type(file_info) in (dict, type(None))

    if not file_info:
        return None

    # Basic info
    new_file  = file_info.copy()
    old_name  = new_file.get('filename')
    full_name = os.path.join (ASSET_PATH, old_name)
    thumbnail = os.path.join (THUMB_PATH, old_name) + '.%s'%(THUMB_EXT)

    # Check file sizes
    stat       = os.statvfs(ASSET_PATH)
    free_space = stat.f_bavail * stat.f_bsize
    file_size  = os.path.getsize (full_name)
    if file_size > free_space:
        raise IOError, "Not enough free space to duplicate file."

    # Duplicate file & thumbnail on a subshell
    all_files = os.listdir (ASSET_PATH)
    new_name  = Upload.get_unused_name (full_name, all_files)
    new_fullname = os.path.join (ASSET_PATH, new_name)
    new_thumbnail= os.path.join (THUMB_PATH, new_name) + '.%s'%(THUMB_EXT)

    os.system ("cp %s %s &" %(full_name, new_fullname))
    os.system ("cp %s %s &" %(thumbnail, new_thumbnail))

    # Return
    file_info['filename'] = new_name
    return file_info


def test ():
    import sys
    import Asset
    import OpAsset

    try:
        asset_id = int(sys.argv[1])
        asset = Asset.Asset(asset_id)
    except:
        print 'Required test parameters: asset_id'
        sys.exit(1)

    flag        = id(__file__)
    old_file    = asset._file
    new_file    = {'id': asset_id, 'filename':flag, 'size':1024, 'queue_flag':flag}

    asset._file = new_file
    oa = OpAsset.OpAsset(asset)
    ret = oa.update ()
    assert ret == True
    print 'Test asset modified: OK'

    files = get_files_by_name([flag])
    assert int(files[0]['filename']) == flag
    print 'get_files_by_name: OK'

    files = get_files_by_flag(flag)
    assert int(files[0]['filename']) == flag
    print 'get_files_by_flag: OK'

    update_files ([asset._file])
    print 'update_files: OK'

    asset._file = old_file
    oa = OpAsset.OpAsset(asset)
    ret = oa.update ()
    assert ret == True
    print 'Test asset restore:', ret

    print type(old_file), old_file
    ret = clone_file (old_file)
    if ret:
        print 'clone_file result: OK', ret
    else:
        print 'clone_file result: ERROR'

if __name__ == '__main__':
    test()

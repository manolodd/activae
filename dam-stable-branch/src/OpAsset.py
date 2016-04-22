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
import Format
import Upload
import File
import Auth
from xmlrpclib import ServerProxy
from ACL import ACL
from Asset import Asset
from config import *
from DBSlayer import query_check_success, transaction_check_success, Query

DB_KEYS = ['description', 'collections_id', 'edited_flag',
           'published_flag','language', 'title', 'date_available',
           'views', 'asset_types_id','creator_id', 'licenses_id',
           'version', 'date_created','date_modified', 'publisher_id',
           'id', 'subject','editor_id']

class OpAsset:
    def __init__ (self, asset = None, debug_params = None):
        self.params = debug_params
        if isinstance (asset,Asset):
            self._asset = asset
        elif asset == None or type(asset) == int:
            self._asset = Asset (asset)
        else:
            raise TypeError


    def _check_existence (self):
        if not self._asset['id']:
            raise LookupError


    def _check_asset_usage (self):
        """Return number of relations of an asset"""

        asset_id = self._asset['id']
        q = "SELECT SUM(total) AS total FROM ("\
            "SELECT COUNT(*) AS total "\
            "FROM children WHERE parent_id='%(asset_id)d' UNION " \
            "SELECT COUNT(*) AS total FROM asset_versions " \
            "WHERE source_id ='%(asset_id)d' UNION " \
            "SELECT COUNT(*) AS total FROM parts " \
            "WHERE source_id='%(asset_id)d' UNION " \
            "SELECT COUNT(*) AS total FROM replacements " \
            "WHERE replacee_id='%(asset_id)d') AS relations;" % locals()

        re = Query(q)
        return re['total'][0]


    def add (self):
        """Feed asset to platform"""
        sql_columns = []
        sql_values  = []
        asset = self._asset
        db = asset._db

        if not db.has_key('published_flag'):
            db['published_flag'] = 0

        keys = DB_KEYS[:]
        keys.remove('id')
        for key in keys:
            if db.get(key):
                sql_columns.append(key)
                sql_values.append("'%s'" % db[key])

        q = "INSERT INTO assets (%s) VALUES (%s);" \
            % (','.join(sql_columns), ','.join(sql_values))
        query = Query(q)
        try:
            asset['id'] = query.result[0]['INSERT_ID']
        except KeyError:
            return False

        q = '';
        if asset._parent_id:
            q += "INSERT INTO children VALUES (%d, %d);" % \
                 (asset._parent_id, asset['id'])
            q += "INSERT INTO asset_versions VALUES (%d, %d);" % \
                 (asset._parent_id, asset['id'])

        replaces = asset._replacements.get('replaces')
        if replaces:
            for x in replaces:
                q += "INSERT INTO replacements VALUES (%d, %d);" % \
                    (asset['id'], x)

        # Populate attachment info
        if asset._file:
            asset._file['id'] = asset['id']
            keys, values = [], []
            for key,value in asset._file.items():
                if value:
                    keys.append(key)
                    values.append("'%s'" % str(value))
            q += ("INSERT INTO files (%s) VALUES (%s);" %
                 (','.join(keys), ','.join(values)))

        try:
            for x in asset._parts['has_parts_of']:
                q += "INSERT INTO parts VALUES (%d, %d);" % \
                    (int(x), asset['id'])
        except (KeyError, TypeError):
            pass

        # Populate 'asset_formats' table
        #
        insert = []
        for format in asset._formats:
            if len(format) < 3 and format.get('source'):
                # Insert incomplete references and remove them from
                # memory in case the object is reused. It should be
                # complete once it is reloaded
                insert.append(format)

        for format in insert:
            q += ("INSERT INTO asset_formats (source_id, target_id) "
                  "VALUES (%d,%d);" % (format['source'],
                                       asset['id']))
            asset._formats.remove(format)

        # Perform
        if q:
            q = "START TRANSACTION; %s COMMIT;" % q
            if not transaction_check_success (q):
                # Delete previous commit
                q = "DELETE FROM assets WHERE assets.id == '%s'" % asset['id']
                query = Query(q)
                return False

        acl = ACL(self.params)
        acl.set_default_asset_acl(self._asset)

        return True


    def update (self):
        """Re-ingest modified asset"""
        self._check_existence()
        asset = self._asset

        sql_values = self._process_update_values (DB_KEYS)

        # assets table
        q = "UPDATE assets SET %s WHERE id = %s;" %(','.join(sql_values), asset['id'])

        # relations: they should remain the same(children, versions, asset_formats)
        old_asset = Asset(asset['id'])

        if asset._parts != old_asset._parts and asset._parts.has_key('has_parts_of'):
            q += "DELETE FROM parts WHERE derivative_id='%d';" % \
                (asset['id'])

            if asset._parts.get('is_part_of', None):
                for x in asset._parts['is_part_of']:
                    q += "INSERT INTO parts VALUES (%d, %d);" % \
                        (x, asset['id'])

        q += "DELETE FROM files WHERE id='%d';" % asset['id']

        if asset._file:
            keys, values = [], []
            for key,value in asset._file.items():
                if value:
                    keys.append(key)
                    values.append("'%s'" % str(value))
            q += ("REPLACE INTO files (%s) VALUES (%s);" %
                 (','.join(keys), ','.join(values)))

        q = "START TRANSACTION; %s COMMIT;" % q

        if transaction_check_success (q):
            return True
        return False


    def _process_update_values (self, keys = DB_KEYS):
        sql_values = []
        asset = self._asset

        for key in keys:
            if asset._db.get(key) == None:
                sql_values.append ("%s=NULL" %(key))
            else:
                if str(asset[key]).endswith('()'):
                    val = "%s=%s" %(key, str(asset[key]))
                else:
                    val = "%s='%s'" %(key, str(asset[key]))
                sql_values.append (val)
        return sql_values


    def delete (self):
        self._check_existence()
        if self._check_asset_usage() != 0:
            return { 'type': 'partial',
                     'ret' : self.__delete_attachment()}
        else:
            return { 'type': 'total',
                     'ret' : self.__delete_asset()}


    def __delete_asset (self):
        if not self.__delete_attachment():
            return False
        self._asset._file = {}

        asset = self._asset
        q  = ("DELETE FROM parts WHERE derivative_id = '%(id)d';" +
              "DELETE FROM replacements WHERE replacer_id = '%(id)d';" +
              "DELETE FROM asset_versions WHERE derivative_id = '%(id)d';" +
              "DELETE FROM asset_formats WHERE target_id = '%(id)d' OR source_id = %(id)d;" +
              "DELETE FROM children WHERE child_id = '%(id)d';" +
              "DELETE FROM assets WHERE id = '%(id)s'") % ({'id': asset['id']})

        q = "START TRANSACTION; %s; COMMIT;" % q

        if not transaction_check_success (q):
            return False
        return True

    def __delete_attachment (self):
        """Delete files associated to assets.attachment"""
        target = self._asset._file
        if not target:
            return True

        return File.delete_file (target)

    def transcode (self, target_id, programatic=False):
        """Dispatch asset to transcoding queue, and reingest result as
        new asset"""

        try:
            filename = self._source_filename
        except AttributeError:
            filename = self._asset._file.get('filename')
            self._source_filename = filename

        if not filename:
            return False

        abs_source = os.path.join(ASSET_PATH, filename)
        src_type   = Upload.get_type (abs_source)

        if not src_type in Format.TRANSCODE_TYPES:
            return False

        # Dispatch
        http = "http://%s:%s/" % (QUEUE_SERVER, QUEUE_PORT)
        client = ServerProxy (http)

        if src_type in ['audio','video']:
            convert = client.ConvertMedia
            thumb   = client.BuildThumbnailMedia
        else:
            convert = client.ConvertImage
            thumb   = client.BuildThumbnailImage

        format     = Format.get_format (target_id)['name']
        name,ext   = os.path.splitext (abs_source)
        abs_target = '%s.%s' %(abs_source, format)

        try:
            task_id = convert (abs_source, abs_target, format)
        except Exception,e:
            print str(e)
            return False

        # Make thumbnail
        abs_thumb  = abs_target.replace(ASSET_PATH, THUMB_PATH)
        abs_thumb  = '%s.%s' % (abs_thumb, THUMB_EXT)
        thumb (abs_source, abs_thumb)

        # Reingest and anotate the format
        self._asset._file['filename'] = os.path.basename(abs_target)
        self._asset._file['queue_flag'] = task_id
        self._asset._formats.append({'source': self._asset['id']})
        self._parent_id = self._asset['id']

        # When not used through API
        if not programatic:
            self._asset['publisher_id'] = Auth.get_user_id()
            return self.add()

        # When used through API
        self._asset['publisher_id'] = LOOKUP_USERID
        ret = self.add()
        if ret==True:
            return task_id
        return ret

    def __allow_transcoding (self, abs_target):
        try:
            if os.path.getsize (abs_target):
                return False
        except:
            pass
        return True


def test():
    import sys
    import OpLookup
    import Auth
    import Role

    try:
        username = sys.argv[1]
        asset_id = int (sys.argv[2])
        asset    = Asset (asset_id)
        user     = Auth.get_user(username)
        roles    = Role.get_user_roles (username)
        params   = { 'roles': roles, 'user_id': user['id']}
    except IndexError:
        print 'Required test parameters: user sample_asset_id'
        sys.exit(1)

    # Create asset for testing
    new_asset       = Asset ()
    new_asset._db   = asset._db
    new_asset._tags = asset._tags
    flag            = id (new_asset)
    new_asset['title'] = flag

    oa = OpAsset (new_asset, params)
    assert oa
    print '#1 OpAsset (): Creation OK'

    ret = oa.add()
    assert ret == True
    print '#2 OpAsset.add(): Addition OK'

    ol = OpLookup.OpLookup ()
    new_asset_id = ol({'title': flag})[0]
    new_asset = Asset (new_asset_id)
    assert int(new_asset['title']) == int(flag)
    print '#3 OpAsset.add(): Retrieval after addition OK'

    oa = OpAsset (new_asset, params)
    assert oa
    print '#4 OpAsset (new_asset): Creation after retrieval OK'

    new_asset['description'] = flag
    oa = OpAsset (new_asset, params)
    ret = oa.update()
    assert ret == True
    print '#5 OpAsset.update(): Modification OK'

    ol = OpLookup.OpLookup ()
    updated_asset_id = ol({'description': int(flag)})[0]
    updated_asset = Asset (new_asset_id)
    assert int(updated_asset['description']) == int(flag)
    print '#6 OpAsset.update(): Retrieval after modification OK'

    assert updated_asset['id'] == new_asset['id']
    print '#7 OpAsset.update(): Comparison with original OK'

    ret = oa.delete()
    assert ret['ret'] == True
    print '#8 OpAsset.delete(): Deletion OK'


if __name__ == '__main__':
    test()

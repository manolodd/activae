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

import os
import Asset
import OpAsset
import Collection

from ACL import ACL
from DBSlayer import query_check_success, Query

class OpCollection:
    def __init__ (self, collection = None, debug_params = None):
        self.params = debug_params
        if isinstance (collection,Collection.Collection):
            self._collection = collection
        elif collection == None or type(collection) == int:
            self._collection = Collection.Collection(collection)
        else:
            raise TypeError


    def __update_assets (self, changes):
        """Update collections_id for all (asset_id,col_id) pairs specified."""

        reversions = []
        for asset_id, col_id in changes:
            a  = Asset.Asset (asset_id)
            old_col_id = a['collections_id']
            a['collections_id'] = col_id
            oa = OpAsset.OpAsset(a)
            ok = oa.update()
            if ok:
                reversions.append((asset_id, old_col_id))
            else:
                self.__revert_assets (reversions)
                return False

        return True


    def __revert_assets (self, changes):
        """Undo changes to the assets."""

        for asset_id, col_id in changes:
            a  = Asset.Asset (asset_id)
            a['collections_id'] = col_id
            oa = OpAsset.OpAsset(a)
            ok = oa.update()


    def add (self):
        """Feed collection to platform"""
        sql_columns = []
        sql_values  = []
        for key in ['name', 'creator_id']:
            if self._collection[key]:
                sql_columns.append(key)
                sql_values.append("'%s'" % self._collection[key])

        q = "INSERT INTO collections (%s) VALUES (%s);" \
            % (','.join(sql_columns), ','.join(sql_values))
        query = Query(q)

        try:
            self._collection['id'] = query.result[0]['INSERT_ID']
        except KeyError:
            return False

        changes = [(x,self._collection['id'])
                   for x in self._collection['assets']]
        ok = self.__update_assets (changes)

        if ok:
            acl = ACL(self.params)
            acl.set_default_collection_acl(self._collection)
            return True

        q = "DELETE FROM collections WHERE id = %s;" %\
            (self._collection['id'])
        query = Query(q)
        return False


    def update (self):
        """Update a collection"""

        col_id = self._collection['id']

        q = "UPDATE collections SET name = '%s' "\
            "WHERE id = %s;" % (self._collection['name'], col_id)

        if not query_check_success (q):
            return False

        old_assets     = Collection.Collection(col_id)['assets']
        new_assets     = self._collection['assets']
        mod_assets     = [x for x in old_assets if x not in new_assets]

        changes  = [(x, col_id) for x in new_assets]
        changes += [(x, None) for x in mod_assets]

        ok = self.__update_assets (changes)
        if not ok:
            return False
        return True


    def delete (self):
        """Delete the collection and all its assets (or their
        attachments if deletion is not possible."""

        changes = []
        for asset_id in self._collection['assets']:
            a   = Asset.Asset (asset_id)
            oa  = OpAsset.OpAsset(a)
            ret = oa.delete()
            if ret['type'] == 'partial' and ret['ret'] == True:
                changes.append((asset_id, None))
            if ret['ret'] == False:
                self.__update_assets (changes)
                return False

        q  = "DELETE FROM collections WHERE id = '%s';" % self._collection['id']
        if not query_check_success (q):
            return False
        return True


def test():
    import sys
    import OpLookup
    import Auth
    import Role

    try:
        username = sys.argv[1]
        asset_id = int (sys.argv[2])
        asset    = Asset.Asset (asset_id)
        user     = Auth.get_user(username)
        roles    = Role.get_user_roles (username)
        params   = { 'roles': roles, 'user_id': user['id']}
    except IndexError:
        print 'Required test parameters: user sample_asset_id'
        sys.exit(1)

    # Create asset for testing
    new_asset       = Asset.Asset ()
    new_asset._db   = asset._db
    new_asset._tags = asset._tags
    flag            = id (new_asset)
    new_asset['title'] = flag
    oa = OpAsset.OpAsset (new_asset, params)
    ret = oa.add()
    assert ret == True
    print '#1 OpCollection: Creation of test asset OK'

    ol = OpLookup.OpLookup ()
    new_asset_id = ol({'title': flag})[0]
    new_asset = Asset.Asset (new_asset_id)
    oa = OpAsset.OpAsset (new_asset, params)
    assert oa and int(new_asset['title']) == int(flag)
    print '#2 OpCollection: Retrieval of test asset OK'

    test = Collection.Collection ()
    flag = str(id(test))
    test._db['name'] = flag
    test._db['creator_id'] = user['id']
    test['assets'] = [new_asset['id']]

    oc = OpCollection (test, debug_params = params)
    assert oc
    print '#3 OpCollection (%d): OK' % test['id']

    ret = oc.add()
    assert ret == True
    print '#4 OpCollection.add (): OK'

    new = Collection.Collection (name_collection = test['name'])
    oc = OpCollection (new, debug_params = params)
    assert new['name'] == test['name']
    print '#5 OpCollection (%d): Retrieval after creation OK' % new['id']

    new['name'] = flag*2
    ret = oc.update()
    assert ret == True
    print '#6 OpCollection.update (): Modification OK'

    new = Collection.Collection (name_collection = new['name'])
    oc = OpCollection (new, debug_params=params)
    assert new['name'] == flag*2
    print '#7 OpCollection (%d): Retrieval after modification OK' % new['id']


    ret = oc.delete()
    assert ret == True
    print '#8 OpCollection.delete(): Deletion OK'


if __name__ == '__main__':
    test()


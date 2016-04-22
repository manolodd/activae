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

import Auth
import Asset
import Collection
import DBSlayer
import Role
import Error
from consts import *

ADMIN_ACL = {'role': Role.ROLE_ADMIN, 'tuple': (1,1,1,1)}

class ACL:
    """Each ACE is a dictionary where a boolean value indicates
    whether or not the operation/key is permitted. The keys are:
    user_id -> ID of user to which the ACE applies. NULL == All
    role    -> ID of role to which the ACE applies. NULL == All
    ad      -> Add
    ed      -> Edit
    rm      -> Remove
    co      -> Consume
    tuple   -> (ad,ed,rm,co). If present, tuple overrides the rest.

    Operations are interpreted as follows:
          Asset                        Collection
          ----------------------------------------------
    ad    publish: add to platform     add to collection
    ed    edit                         edit
    rm    delete                       delete
    co    read                         read
    """

    def __init__ (self, params = None):
        if params:
            self.roles   = params['roles']
            self.user_id = params['user_id']
        else:
            self.roles   = Role.get_user_roles()
            self.user_id = Auth.get_user_id()

    def __check (self, table, identifier):
        """Checks the evaluated ACL of an asset/collection"""

        assert(table in ['acl_assets', 'acl_collections'])
        assert(type(identifier) == int or type(identifier) == str)

        user_id = str(self.user_id)
        roles   = ','.join(map(str,self.roles))
        identifier = str(identifier)

        sql = ('SELECT BIT_OR(ad) AS ad, BIT_OR(ed) AS ed, '
               'BIT_OR(rm) AS rm, BIT_OR(co) AS co '
               'FROM %s '
               'WHERE id=%s '
               'AND ((role IN (0,%s) OR user_id=%s) '
                    'OR '
                    '(user_id IS NULL AND role IS NULL));' %
               (table, identifier, roles, user_id))

        q = DBSlayer.Query(sql)

        if len(q):
            ad,ed,rm,co = q['ad'][0], q['ed'][0], q['rm'][0], q['co'][0]
        else:
            ad,ed,rm,co = 0,0,0,0

        return {'ad': ad, 'ed': ed,
                'rm': rm, 'co': co, 'tuple': (ad,ed,rm,co)}


    def __get_all (self, table, identifier):
        """Get every ACE of a given asset/collection"""

        assert(table in ['acl_assets', 'acl_collections'])
        assert(type(identifier) == int or type(identifier) == str)

        identifier = str(identifier)
        sql = ('SELECT * '
               'FROM %s '
               'WHERE id=%s;' %
               (table, identifier))

        q = DBSlayer.Query(sql)
        result = []
        if len(q):
            for x in q:
                ace = q[x]
                for key in ace.keys():
                    if ace[key] == None:
                        del ace[key]
                ad,ed = ace.get('ad',0), ace.get('ed',0)
                rm,co = ace.get('rm',0), ace.get('co',0)
                ace['tuple'] = (ad,ed,rm,co)
                result.append(ace)
        return result


    def acl_asset (self, asset_id, summarize=True):
        table = 'acl_assets'
        if summarize:
            return self.__check (table, asset_id)
        return self.__get_all (table, asset_id)


    def acl_collection (self, collection_id, summarize=True):
        if not collection_id:
            return
        table = 'acl_collections'
        if summarize:
            return self.__check (table, collection_id)
        return self.__get_all (table, collection_id)


    def acl_generic (self, content, summarize=True):
        """Check an ACL of an asset or collection"""
        if isinstance (content, Asset.Asset):
            return self.acl_asset (content['id'], summarize)
        if isinstance (content, Collection.Collection):
            return self.acl_collection (content['id'], summarize)
        raise Error.Invalid


    def add (self, obj, acl):
        """Add ACL entry to a content"""

        if isinstance (obj, Asset.Asset):
            table = 'acl_assets'
        elif isinstance (obj, Collection.Collection):
            table = 'acl_collections'
        else:
            raise Error.Invalid

        keys = ['id']
        vals = [obj['id']]

        # The 'tuple' shorthand overrides the other values
        if 'tuple' in acl:
            acl['ad'], acl['ed'], acl['rm'], acl['co'] = acl['tuple']

        for key in ['user_id', 'role', 'ad','ed','rm','co']:
            if acl.get(key) != None:
                keys.append(key)
                vals.append(acl[key])

        q = ("REPLACE INTO %s (%s) VALUES (%s);" %
             (table, ','.join(keys), ','.join(map(str,vals))))

        if not DBSlayer.query_check_success (q):
            raise Error.SQLException


    def clear (self, obj):
        """Clears ACL for a given content"""

        if isinstance (obj, Asset.Asset):
            table = 'acl_assets'
        elif isinstance (obj, Collection.Collection):
            table = 'acl_collections'
        else:
            raise Error.Invalid

        q = ("DELETE FROM %s WHERE id=%d;" %
             (table, obj['id']))

        if not DBSlayer.query_check_success (q):
            raise Error.SQLException


    def delete (self, obj, acl):
        """Remove ACL entry from a content"""

        if isinstance (obj, Asset.Asset):
            table = 'acl_assets'
        elif isinstance (obj, Collection.Collection):
            table = 'acl_collections'
        else:
            raise Error.Invalid

        if 'id_acl' in acl:
            sql_values = ['id_acl=%s'%str(acl['id_acl'])]
        else:
            sql_values = ["id='%s'" % str(obj['id'])]
           # The 'tuple' shorthand overrides the other values
            if 'tuple' in acl:
                acl['ad'], acl['ed'], acl['rm'], acl['co'] = acl['tuple']

            for key in ['user_id', 'role', 'ad','ed','rm','co']:
                if key in acl:
                    sql_values.append("%s='%s'" % (key,acl[key]))

        q = ("DELETE FROM %s WHERE %s;" %
             (table, ' AND '.join(sql_values)))

        if not DBSlayer.query_check_success (q):
            raise Error.SQLException


    def __append_acl (self, table, ids):
        """Append evaluated ACL to a list of ids. The list has tuples
        (id, acl)"""
        assert(table in ['acl_assets', 'acl_collections'])
        if not ids:
            return []

        user_id = str(self.user_id)
        roles   = ','.join(map(str,self.roles))
        ids     = ','.join(map(str,ids))

        sql = ("SELECT id, BIT_OR(ad) AS ad, BIT_OR(ed) AS ed, "
               "BIT_OR(rm) AS rm, BIT_OR(co) AS co "
               "FROM %s "
               "WHERE id IN (%s) "
               "AND ((role IN (%s) OR user_id=%s) "
                    "OR "
                    "(role is NULL AND user_id IS NULL)) "
               "GROUP BY (id);" %
               (table, ids, roles, user_id))

        q = DBSlayer.Query(sql)

        result = []
        for x in q:
            col_id = q['id'][x]
            ad,ed,rm,co = q['ad'][x], q['ed'][x], q['rm'][x], q['co'][x]
            acl = {'ad': ad, 'ed': ed, 'rm': rm, 'co': co,
                   'tuple': (ad,ed,rm,co)}
            result.append((col_id, acl))

        return result


    def append_acl_collections (self, collection_ids):
        """Append evaluated ACL collection-info to a list of
        collections. The list has tuples (id, acl)"""
        return self.__append_acl ('acl_collections', collection_ids)


    def append_acl_assets (self, asset_ids):
        """Append evaluated ACL asset-info to a list of
        assets. The list has tuples (id, acl)"""
        return self.__append_acl ('acl_assets', asset_ids)


    def set_default_collection_acl (self, obj):
        """Set default ACL for a collection. Creator and Admin can do
        anything. The rest, nothing."""

        assert isinstance (obj, Collection.Collection)
        self.clear(obj)
        acl = [{'user_id': obj['creator_id'], 'tuple': (1,1,1,1)},
               {'role': Role.ROLE_ADMIN,      'tuple': (1,1,1,1)},
               {'tuple':(0,0,0,0)}] # default case

        for ace in acl:
            self.add(obj, ace)


    def set_default_asset_acl (self, obj):
        """Set default ACL for an asset. Owner can always access, and
        can delete while it is unpublished."""

        assert isinstance (obj, Asset.Asset)
        self.clear(obj)
        acl = [{'user_id': obj['creator_id'],'tuple': (0,0,1,1)}, # unpublished
               {'role': Role.ROLE_ADMIN,     'tuple': (1,1,1,1)},
               {'role': Role.ROLE_EDITOR,    'tuple': (0,1,0,1)},
               {'role': Role.ROLE_PUBLISHER, 'tuple': (1,0,0,1)},
               {'tuple':(0,0,0,0)}] # default case

        for ace in acl:
            self.add(obj, ace)


    def set_published_asset_acl (self, obj, publish = True):
        """Change ACL for published assets. Owner can no longer delete
        it, and consumers can have access. Revert process if 'publish'
        is False"""

        assert isinstance (obj, Asset.Asset)
        del_acl = [{'user_id': obj['id'],       'tuple': (0,0,1,1)}, # unpublished
                   {'role': Role.ROLE_CONSUMER, 'tuple': (0,0,0,0)}] # unpublished

        add_acl = [{'user_id': obj['id'],       'tuple': (0,0,0,1)}, # published
                   {'role': Role.ROLE_CONSUMER, 'tuple': (0,0,0,1)}] # published

        if not publish:
            add_acl, del_acl = del_acl, add_acl

        for ace in del_acl:
            self.delete (obj, ace)
        for ace in add_acl:
            self.add (obj, ace)


    def filter_collections (self, key, ids):
        """Return collections where ACL allows the given operation"""
        assert key in ['ad','ed','rm','co']

        ids = map(int,ids)
        res_acl = self.append_acl_collections (ids)

        # Maintain input order
        new_ids = [r[0] for r in res_acl if r[0] and r[1][key]]
        return filter(lambda x:x in new_ids, ids)


    def filter_assets (self, key, asset_ids):
        """Return assets where ACL allows the given operation"""
        assert key in ['ad','ed','rm','co']
        asset_ids = map(int,asset_ids)

        coll     = Asset.get_asset_collections (asset_ids)
        coll_ids = [x for x in coll.values() if x]

        # Filter by collection ACL (if there is a collection)
        valid_coll   = self.filter_collections (key, coll_ids)
        valid_coll.append(None)
        check_assets = [x for x in coll if coll[x] in valid_coll]

        # Then filter by asset ACL
        res_acl      = self.append_acl_assets (check_assets)

        # Maintain input order
        new_ids = [r[0] for r in res_acl if r[0] and r[1][key]]
        return filter(lambda x:x in new_ids,asset_ids)


    def compact_acl (self, acl):
        """Aggregates all ACEs of an ACL"""
        keys = ['ad','ed','rm','co']
        ace  = {}
        for key in keys:
            ace[key] = 0

        for x in acl:
            role = x.get('role')
            user_id = x.get('user_id')
            abort = False
            if role and role not in self.roles:
                abort = True
            elif user_id and user_id != self.user_id:
                abort = True
            if abort:
                continue
            for key in keys:
                ace[key] = ace[key] or x.get(key,0)

        ace['tuple'] = (ace['ad'],ace['ed'],ace['rm'],ace['co'])
        return ace


def test ():
    import sys

    try:
        username      = sys.argv[1]
        asset_id      = int(sys.argv[2])
        collection_id = int(sys.argv[3])
        user          = Auth.get_user(username)
        roles         = Role.get_user_roles (username)
        params        = { 'roles': roles, 'user_id': user['id']}
    except IndexError:
        print 'Required test parameters: user asset_id collection_id'
        sys.exit(1)

    acl = ACL(params)
    assert acl
    print '#1 ACL() --> OK'

    asset_acl_full    = acl.acl_asset (asset_id, summarize = False)
    assert asset_acl_full
    print '#2 ACL().acl_asset (asset_id, summarize = False) --> OK'

    asset_acl_compact = acl.acl_asset (asset_id, summarize = True)
    assert asset_acl_compact
    print '#3 ACL().acl_asset (asset_id, summarize = True) --> OK'

    assert asset_acl_compact == acl.compact_acl(asset_acl_full)
    print '#4 ACL().compact_acl (asset_acl_full) --> OK'

    collection_acl_full    = acl.acl_collection (collection_id, summarize = False)
    assert collection_acl_full
    print '#5 ACL().acl_asset (collection_id, summarize = False) --> OK'

    collection_acl_compact = acl.acl_collection (collection_id, summarize = True)
    assert collection_acl_compact
    print '#6 ACL().acl_asset (collection_id, summarize = True) --> OK'

    assert collection_acl_compact == acl.compact_acl(collection_acl_full)
    print '#7 ACL().compact_acl (collection_acl_full) --> OK'

    n=7
    for key in ['ad','ed','rm','co']:
        filtered = acl.filter_assets (key, [asset_id])
        if asset_acl_compact[key]:
            assert asset_id in filtered
        else:
            assert asset_id not in filtered
        n += 1
        print '#%s ACL().filter_assets (%s, [asset_id]) --> OK' % (n,key)

    for key in ['ad','ed','rm','co']:
        filtered = acl.filter_collections (key, [collection_id])
        if collection_acl_compact[key]:
            assert collection_id in filtered
        else:
            assert collection_id not in filtered
        n += 1
        print '#%s ACL().filter_collections (%s, [collection_id]) --> OK' % (n,key)

if __name__ == '__main__':
    test()

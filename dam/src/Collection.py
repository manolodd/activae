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

import Asset
import Auth
import Role
import Error

from config import *
from DBSlayer import Query

class Collection:
    def __init__ (self, id_collection = 0, name_collection = None):
        self._db           = {'id':int(id_collection)}
        self._assets       = []
        self._tags         = {}

        if name_collection:
            self._db['name'] = name_collection

        if id_collection or name_collection:
            self._load_collection()


    def __getitem__ (self, key):
        if self._db.has_key(key):
            return self._db[key]
        elif key == 'tags':
            return self.get_tags()
        elif key == 'assets':
            return self._assets


    def __setitem__ (self, key, value):
        if   key == 'assets':
            self._assets = value
        elif key == 'tags':
            self._tags = value
        else:
            self._db[key] = value

    def __iter__ (self):
        return iter(self._assets)


    def __len__ (self):
        return len(self._assets)

    def __contains__ (self, asset_id):
        return asset_id in self._assets

    def _load_collection (self):
        """Load the collection from the database."""

        assert(type(self['id']) == int)
        if self._db.get('id'):
            sql = "SELECT * FROM collections WHERE id=%d;" % self['id']
        elif self._db.get('name'):
            sql = "SELECT * FROM collections "\
                  "WHERE name='%s' ORDER BY id DESC "\
                  "LIMIT 1;" % self['name']
        else:
            raise Error.Invalid

        q = Query(sql)
        if not q['id']:
            self['id'] = None
            return False

        for key in q.get_headers():
            self._db[key] = q[key][0]

        sql = "SELECT id FROM assets " +\
              "WHERE collections_id=%d;" % self['id']
        q = Query(sql)
        if len(q):
            self._assets = [q[x]['id'] for x in q]


    def _lookup_tags (self, limit=None):
        """Agregate the tags of every asset, removing duplicates."""

        if not self['id']:
            return

        if not limit: #Limits amount of assets to inspect if needed
            limit = len(self['assets'])

        for asset_id in self['assets'][:limit]:
            a    = Asset.Asset(asset_id)
            tags = a.get_tags()
            for key, content in tags.items():
                if not self._tags.has_key(key):
                    self._tags[key] = []
                if type(content) == list:
                    self._tags[key] += [x for x in content]
                else:
                    new = self._tags[key]
                    new.append(content)
                    self._tags[key] = new

        for key, contents in self._tags.items():
            contents = {}.fromkeys(contents).keys()
            contents.sort()
            self._tags[key] = contents


    def __str__ (self):
        """Print the tag values"""
        txt = ''
        for tag, content in self._tags.items():
            for x in content:
                txt += '%s: %s\n' % (tag, str(x))
        return txt


    def get_tags (self):
        """Keep only non-nil tags"""

        if not self._tags:
            self._lookup_tags()

        tags = {}
        for tag, content in self._tags.items():
            if content:
                tags[tag] = content
        return tags


    def get_diz (self, limit=1):
        if not self._tags:
            self._lookup_tags(limit)

        desc, license_name = '',''
        if self['tags'].has_key('Description'):
            desc = self['tags']['Description'][0]
        if self['tags'].has_key('Rights'):
            license_name=self['tags']['Rights'][0]

        d = { 'thumb':   THUMB_COLLECTION,
              'creator': Auth.get_user_name (self['creator_id']),
              'license': license_name,
              'title':   self['name'],
              'desc':    desc,
             }
        return d


    # commodity
    def _dump (self):
        if not self._tags:
            self._lookup_tags()

        attr_lst = [x for x in dir(self) if not callable(getattr(self, x))]
        for x in attr_lst:
            print '\n%s:\n%s' % (x, str(getattr(self, x)))
        print self


def get_collections ():
    q = "SELECT collections.id, name, creator_id, username "\
        "FROM collections JOIN users ON creator_id=users.id;"
    collections = Query(q)
    return collections


def get_collections_dict ():
    collections = get_collections ()

    result = {}
    for x in collections:
        key = collections['id'][x]
        result[key] = {
            'name': collections['name'][x],
            'username': collections['username'][x],
            'creator_id': collections['creator_id'][x]
            }

    return result


def get_collections_list ():
    collections = get_collections ()
    if len(collections) == 0:
        return []

    result = [{'id': collections['id'][x],
               'name': collections['name'][x],
               'username': collections['username'][x],
               'creator_id': collections['creator_id'][x]
               }
              for x in collections]
    return result


def test ():
    """This loads the specified collection and displays all its
    contents and associated Metadata"""
    import sys
    try:
        c = Collection (sys.argv[1])
        c._dump()
    except IndexError:
        print 'No such collection'

if __name__ == '__main__':
    test()


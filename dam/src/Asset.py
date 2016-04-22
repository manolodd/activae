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
import License
import Format
import Type
import Role

from DBSlayer import Query
from config import *

class Asset:
    def __init__ (self, id_asset = 0):
        self._db           = {'id':int(id_asset)}
        self._formats      = []
        self._children     = []
        self._versions     = []
        self._replacements = {'replaces':[], 'replaced_by':None}
        self._parts        = {}
        self._tags         = {}
        self._parent_id    = None
        self._collection   = []
        self._file         = {}

        if id_asset:
            self._load_asset()

    def __getitem__ (self, key):
        if self._db.has_key(key):
            return self._db[key]
        elif key == 'tags':
            return self._tags
        elif self._tags.has_key(key):
            return self._tags[key]
        elif key == 'attachment':
            return self._file.get('filename')

    def __setitem__ (self, key, value):
        self._db[key] = value

    def _load_asset (self):
        assert(type(self['id']) == int)
        sql = "SELECT assets.* FROM assets "\
              "LEFT JOIN files ON assets.id=files.id "\
              "WHERE assets.id=%d" % self['id']

        q = Query(sql)

        if not q['id']:
            self['id'] = None
            return False

        for key in q.get_headers():
            self._db[key] = q[key][0]

        self._lookup_parent()
        self._lookup_children()
        self._lookup_versions()
        self._lookup_formats()
        self._lookup_parts()
        self._lookup_replacements()
        self._lookup_collection()
        self._lookup_file()
        self._compile_tags()

    def _lookup_parent (self):
        # Parent
        #
        sql = "SELECT parent_id FROM children " +\
              "WHERE child_id=%d" % self['id']
        q = Query(sql)
        if len(q):
            self._parent_id = q['parent_id'][0]


    def _lookup_children (self):
        # Children
        #
        sql = "SELECT child_id FROM children " +\
              "WHERE parent_id=%d" % self['id']
        q = Query(sql)
        if len(q):
            self._children = [q[x]['child_id'] for x in q]


    def _lookup_versions (self):
        # Versions
        #
        self._versions = [{'version': self['version'],
                           'id':      self['id']}]

        sql = "SELECT derivative_id, version "+\
              "FROM view_asset_versions " +\
              "WHERE source_id=%d;" % self['id']
        q = Query(sql)

        if len(q):
            self._versions += [{'version': q[x]['version'],
                               'id':      q[x]['derivative_id']}
                              for x in q]

    def _lookup_formats (self):
        # Formats
        #
        sql = ("SELECT id,source_id,formats_id,format " +
               "FROM view_asset_formats " +
               "WHERE source_id=%(id)d " +

               "UNION " +
               "SELECT assets.id,assets.id " +
               "AS source_id,formats_id,format " +
               "FROM assets " +
               "JOIN files ON assets.id = files.id " +
               "JOIN formats ON files.formats_id=formats.id " +
               "WHERE assets.id=%(id)d "+
               "UNION " +
               "SELECT id,source_id,formats_id,format "+
               "FROM view_asset_formats "+
               "WHERE id=%(id)d;") % ({'id': self['id']})


        q = Query(sql)
        if len(q):
            self._formats = [{'source': q[x]['source_id'],
                              'format': q[x]['format'],
                              'id':     q[x]['id']}
                             for x in q]

    def _lookup_parts (self):
        # Parts
        #
        sql = "SELECT derivative_id FROM parts "+\
              "WHERE source_id=%d;" % self['id']

        q = Query(sql)
        if len(q):
            self._parts['is_part_of'] = [q[x]['derivative_id']
                                              for x in q]
        sql = "SELECT source_id FROM parts "+\
              "WHERE derivative_id=%d;" % self['id']

        q = Query(sql)
        if len(q):
            self._parts['has_parts_of'] = [q[x]['source_id']
                                              for x in q]

    def _lookup_replacements (self):
        # Replacements
        #
        sql = "SELECT replacee_id FROM replacements "+\
              "WHERE replacer_id=%d;" % self['id']

        q = Query(sql)
        if len(q):
            self._replacements['replaces'] = [q[x]['replacee_id']
                                              for x in q]

        sql = "SELECT replacer_id FROM replacements "+\
              "WHERE replacee_id=%d;" % self['id']
        q = Query(sql)
        if len(q):
            self._replacements['replaced_by'] = q['replacer_id'][0]

    def _lookup_collection (self):
        collection_id = self['collections_id']
        if not collection_id:
            return

        sql = "SELECT id FROM assets " +\
              "WHERE collections_id=%d AND id!=%d;" % (collection_id,self['id'])
        q = Query(sql)
        if len(q):
            self._collection = [q[x]['id'] for x in q]

    def _lookup_file (self):
        sql = "SELECT * FROM files "+\
              "WHERE id=%d;" % self['id']

        q = Query(sql)
        if len(q):
            for x in q.get_headers():
                self._file[x] = q[x][0]


    def _compile_tags (self):
        # Versions & Source
        version_of = None
        version    = self._db.get('version', None)
        versions   = [x['id'] for x in self._versions if x['id']!=self['id']]
        source     = self._parent_id
        if self['version'] != 1:
            version_of = self._replacements.get('replaces')

        # Formats
        has_formats  = None
        is_format_of = None
        if self._formats:
            format_list  =[x['format'] for x in self._formats if x['id']!=self['id']]
            has_formats  = dict.fromkeys(format_list).keys()
            for f in self._formats:
                if f['source'] == None and f['id'] != self['id']:
                    is_format_of = f['id']

        self._tags = {
            'Creator':          self._db.get('creator_id'),
            'Date':             max(self._db.get('date_modified'), self._db.get('date_edited'), self._db.get('date_created')),
            'Date Created':     self._db.get('date_created'),
            'Date (Modified)':  self._db.get('date_modified'),
            'Date Available':   self._db.get('date_available'),
            'Description':      self._db.get('description'),
            'Extent':           self._file.get('extent'),
            'Format':           self._file.get('formats_id'),
            'Has Format':       has_formats,
            'Has Part':         self._parts.get('has_parts_of'),
            'Has Version':      versions,
            'Identifier':       self._db.get('id'),
            'Is Format Of':     is_format_of,
            'Is Part Of':       self._parts.get('is_part_of'),
            'Is Referenced By': self._db.get('collections_id'),
            'Is Replaced By':   self._replacements.get('replaced_by'),
            'Is Version Of':    version_of,
            'Language':         self._db.get('language'),
            'Publisher':        self._db.get('publisher_id'),
            'Relation':         self._collection,
            'Replaces':         self._replacements.get('replaces'),
            'Source':           source,
            'Subject':          self._db.get('subject'),
            'Title':            self._db.get('title'),
            'Type':             self._db.get('asset_types_id'),
            'Rights':           self._db.get('licenses_id'),
            }

        if self['Creator']:
            self._tags['Creator'] = Auth.get_user_name (self['tags']['Creator'])
        if self['Publisher']:
            self._tags['Publisher'] = Auth.get_user_name (self['tags']['Publisher'])
        if self['Rights']:
            self._tags['Rights']    = License.get_license_name(self['tags']['Rights'])
        if self['Format']:
            self._tags['Format']    = Format.get_format_name (self['tags']['Format'])
        if self['Type']:
            self._tags['Type']      = Type.get_type_name (self['tags']['Type'])

        for key in self._tags.keys():
            if key.startswith('Date') and self._tags[key] == '0000-00-00 00:00:00':
                self._tags[key] = None


    def get_diz (self):
        thumbnail = THUMB_ASSET
        fname = self._file.get('filename')
        if fname:
            try:
                f=open('%s/%s.%s' %(THUMB_PATH, fname,  THUMB_EXT))
                f.close()
                thumbnail = "%s/thumbs/%d" % (STATIC_PRIVATE, self['id'])
            except:
                pass

        d = { 'thumb':   thumbnail,
              'creator': self['tags']['Creator'],
              'license': self['tags']['Rights'],
              'title':   self['tags']['Title'],
              'desc':    self['tags']['Description']
             }
        return d


    def get_tags (self):
        """Keep only non-nil tags"""

        if not self._tags:
            return None

        tags = {}
        for tag, content in self._tags.items():
            if content:
                tags[tag] = content
        return tags


    def __str__ (self):
        """Print tags 1 to 1"""

        tags = self.get_tags()
        if not tags:
            return None

        txt = ''
        for tag, content in tags.items():
            if type(content) == list:
                for x in content:
                    txt += '%s: %s\n' % (tag, str(x))
            else:
                txt += '%s: %s\n' % (tag, str(content))

        return txt


    # commodity
    def _dump (self):

        attr_lst = [x for x in dir(self) if not callable(getattr(self, x))]
        for x in attr_lst:
            print '\n%s:\n%s' % (x, str(getattr(self, x)))
        print self


def get_asset_collections (asset_ids):
    """Get dictionary with pairs asset_id:collection_id"""

    d   = {}
    ids = ','.join(map(str,asset_ids))
    if len(ids)==0:
        return d

    sql = ('SELECT id,collections_id AS col_id '
           'FROM assets '
           'WHERE id IN (%s);' % ids)
    q = Query(sql)

    for x in q:
        key, value = q['id'][x], q['col_id'][x]
        d[key] = value
    return d

def test ():
    """This loads the specified asset and displays all its contents
    and associated Metadata."""
    import sys
    try:
        a = Asset (id_asset=int(sys.argv[1]))
        a._dump()
    except IndexError:
        print 'Required test parameters: asset_id'
        sys.exit(1)

if __name__ == '__main__':
    test()

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
import string
import re
import Asset
import OpAsset
import Collection
import Validations

from Error import *
from DBSlayer import *

class OpLookup:
    def __init__ (self):
        pass

    def __call__ (self, search):
        if isinstance (search,dict):
            self.result = self.lookup_dict (search)
        elif isinstance (search, str):
            self.result = self.lookup_text (search)
        else:
            raise TypeError

        self.search = search
        return self.result

    def __sanitize (self, param):
        if type(param) != str: return param
        trans = string.maketrans('%;','  ')
        param = param.translate(trans)
        return param

    def __sanitize_fullsearch (self, search):
        if type(search) != str: return search
        search = self.__sanitize(search)
        trans = string.maketrans('.,;:%','     ')
        return search.translate(trans)

    def __is_boolean (self, search):
        pattern = r'[+-<>()*~]'
        return re.search(pattern,search)

    def lookup_text (self, search):
        """Lookup by full search (use BOOLEAN MODE where needed"""
        if not search:
            raise Empty

        search = self.__sanitize_fullsearch(search)
        fields = ['publisher_name', 'creator_name',
                  'collection_name', 'title', 'subject', 'description']
        fields = ','.join(fields)
        if self.__is_boolean(search):
            boolean_mode = ' IN BOOLEAN MODE'
        else:
            boolean_mode = ''

        q = "SELECT assets_id, MATCH(%(fields)s) "\
            "AGAINST ('%(search)s%(boolean_mode)s') AS score "\
            "FROM fullsearch "\
            "WHERE "\
            "MATCH(%(fields)s) AGAINST('%(search)s%(boolean_mode)s');" % locals()

        lookup = Query(q)
        result = [x for x in lookup['assets_id']]
        return result


    def lookup_dict (self, search):
        if not search:
            raise Empty

        keys = search.keys()
        if '__order__' in keys:
            order = 'ORDER BY %s' % search.pop('__order__')
        else:
            order = ''

        """Lookup by specific fields"""
        sql_values   = []
        like_lst     = ['publisher_name', 'creator_name',
                        'collection_name', 'title', 'subject',
                        'description', 'type']
        interval_lst = ['extent','views','date_modified',
                        'date_created', 'date_available', 'version',
                        'size', 'bitrate','width','height']
        equal_lst    = ['asset_types_id', 'licenses_id',
                        'collections_id', 'formats_id', 'creator_id',
                        'publisher_id', 'published_flag',
                        'edited_flag', 'language', 'id','version',
                        'filename', 'transcoding_flag'] + interval_lst

        for key,value in search.items():
            if value != None:
                value = self.__sanitize(value)
                value = str(value)

                if value.upper() == 'NULL':
                    sql_values.append ("%s IS NULL" % key)
                elif key in equal_lst:
                    sql_values.append ("%s = '%s'" %(key, value))
                elif key in like_lst:
                    sql_values.append ("%s LIKE '%%%s%%'" %(key, value))
                elif key[:-1] in interval_lst:
                    if not value.endswith(')'):
                        value = "'%s'"%value
                    if key[-1] == '+':
                        sql_values.append ("%s <= %s" %(key[:-1],value))
                    elif key[-1] == '-' and key[:-1] in interval_lst:
                        sql_values.append ("%s >= %s" %(key[:-1], value))
                elif key in ['pnum','pmax']:
                    pass # these are valid but not for lookup
                else:
                    raise Invalid

        conditions  = ''
        if sql_values:
            conditions += 'WHERE %s ' % ' AND '.join(sql_values)

        q = "SELECT id FROM view_asset_lookup %s %s;" % \
            (conditions, order)

        lookup = Query(q)
        if not len(lookup):
            return []
        return lookup['id']


def test():
    import sys

    if len(sys.argv) < 2:
        print 'Required test parameters: search_string | search_dict'
        sys.exit(1)

    o = OpLookup()
    try:
        expression = ' '.join(sys.argv[1:])
        search     = eval(expression)
    except (NameError, SyntaxError):
        search = ' '.join(sys.argv[1:])

    print o(search)

if __name__ == '__main__':
    test()

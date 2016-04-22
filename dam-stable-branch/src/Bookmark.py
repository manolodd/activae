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

from DBSlayer import Query, query_check_success

def bookmark_exists (bookmark):
    asset_id, user_id = bookmark
    sql = "SELECT * FROM bookmarks " \
          "WHERE assets_id='%s' AND users_id='%s';" % \
          (str(asset_id), str(user_id))
    q   = Query(sql)
    if len(q):
        return True
    return False

def add_bookmark (bookmark):
    asset_id, user_id = bookmark
    sql = "INSERT INTO bookmarks VALUES (%s,%s);" % \
          (str(asset_id), str(user_id))
    if query_check_success(sql):
        return True
    return False

def del_bookmark (bookmark):
    asset_id, user_id = bookmark
    sql = "DELETE FROM bookmarks " \
          "WHERE assets_id='%s' AND users_id='%s';" % \
          (str(asset_id), str(user_id))
    if query_check_success(sql):
        return True
    return False

def get_user_bookmarks (user_id):
    sql = "SELECT assets_id FROM bookmarks " \
          "WHERE users_id='%s';" % (str(user_id))
    q   = Query(sql)
    return q['assets_id']


def test ():
    import sys

    try:
        asset_id, user_id = sys.argv[1:]
        bookmark = (asset_id, user_id)
    except ValueError:
        print 'Required test parameters: asset_id user_id'
        sys.exit(1)

    print 'asset_id: %s, user_id: %s' % (asset_id, user_id)
    print 'Existing bookmarks', get_user_bookmarks(user_id)

    if bookmark_exists (bookmark):
        print 'Bookmark %s exists' % str(bookmark)
    else:
        print "Adding   bookmark %s" % str(bookmark), ['Fail','OK'][add_bookmark (bookmark)]
        print "Checking bookmark %s" % str(bookmark), ['Fail','OK'][bookmark_exists (bookmark)]
        print "Deleting bookmark %s" % str(bookmark), ['Fail','OK'][del_bookmark (bookmark)]

if __name__ == '__main__':
    test()

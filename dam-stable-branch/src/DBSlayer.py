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

import pycurl
import urllib
import StringIO
from config import *

HEADERS=['Connection: Keep-Alive', 'X-Beautify: 0']


def query_check_success (sql):
    query = Query (sql)
    return query.result[0]['SUCCESS'] == 1

class Query:
    def __init__ (self, sql=None, debug=False):
        self.debug  = debug
        self.result = None
        self.sql    = None

        if sql:
            self.sql = urllib.quote(sql)
            self._perform()

    def _perform (self):
        b = StringIO.StringIO()
        c = pycurl.Curl()

        request = 'http://%s/%s' % (DB_HOST, urllib.quote(self.sql))

        c.setopt(pycurl.URL, request)
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        c.setopt(pycurl.HTTPHEADER,    HEADERS)
        c.perform()

        raw = b.getvalue()
        if raw:
            self.result = eval(raw)

    def __get_result (self):
        if not self.result:
            return None

        result = self.result[0]

        if not 'RESULT' in result:
            return None

        return result['RESULT']

    def __iter__ (self):
        result = self.__get_result()
        if not result:
            return []
        return iter(range(len(result['ROWS'])))

    def __len__ (self):
        result = self.__get_result()
        if not result:
            return 0
        return len(result['ROWS'])

    def __getitem__ (self, key):
        # Result of a field
        if type(key) == str:
            return self.__getitem_str__ (key)
        # All fields of a row
        elif type(key) == int:
            return self.__getitem_int__ (key)
        else:
            assert False, "Unknown key type"

    def __getitem_int__ (self, n):
        result = self.__get_result()
        if not result:
            return None

        # Build dict
        row  = result['ROWS'][n]
        hdrs = result['HEADER']

        re  = {}
        for k in range(len(hdrs)):
            re[hdrs[k]] = row[k]

        return re

    def __getitem_str__ (self, key):
        result = self.__get_result()
        if not result:
            return None

        headers = result['HEADER']
        pos = headers.index(key)
        if pos == -1:
            None

        return map (lambda x,p=pos: x[p], result['ROWS'])

    def __contains__ (self, key):
        "The result contains a column 'key'"

        result = self.__get_result()
        if not result:
            return False

        headers = result['HEADER']
        return key in headers

    def get_headers (self):
        result = self.__get_result()
        if not result:
            return []
        return result['HEADER']

    def get_values (self):
        result = self.__get_result()
        if not result:
            return []
        return result['ROWS']



def SQL(query):
    b = StringIO.StringIO()
    c = pycurl.Curl()

    request = 'http://%s/%s' % (DB_HOST, urllib.quote(query))

    c.setopt(pycurl.URL, request)
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.setopt(pycurl.HTTPHEADER,    HEADERS)
    c.perform()

    return b.getvalue()

def transaction_check_success (sql):
    query = Query (sql)
    return query.result[-1]['SUCCESS'] == 1


def test ():
    print SQL("show tables;")

if __name__ == '__main__':
    test()



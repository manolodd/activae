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

import re
import time

def not_empty (txt):
    if not txt:
        raise ValueError, "No puede estar vacio"
    return txt

def is_email (txt):
    not_empty(txt)

    if re.match (r"^\S+@\S+\.\S+$", txt) == None:
        raise ValueError, "No parece una direccion de correo"

    return txt

def split_list (value):
    ids = []
    for t1 in value.split(','):
        for t2 in t1.split(' '):
            id = t2.strip()
            if not id:
                continue
            ids.append(id)
    return ids

def is_list (values):
    tmp = split_list (values)
    if not tmp:
        raise ValueError, "No parece una lista"
    return tmp

def is_numeric_list (values):
    values = is_list (values)
    for value in values:
        try:
            int(value)
        except ValueError:
            raise ValueError("No parece una lista numerica")
    return values

def is_number (value):
    try:
        return str(int(value))
    except:
        raise ValueError('No parece un entero')

def is_date (val):
    value = val.replace('-','/')
    try:
        value = time.strptime(value, "%d/%m/%Y")
        value = time.strftime('%d/%m/%Y',value)
    except ValueError:
        try:
            value = time.strptime(value, "%Y/%m/%d")
            value = time.strftime('%d/%m/%Y',value)
        except:
            raise ValueError('No parece una fecha')
    return val

def is_time (value):
    if re.match (r"^([0-1][0-9]|[2][0-3]):([0-5][0-9])$", value) == None:
        raise ValueError, "No parece una cadena de tiempo"
    return value



def _run_test_ok   (func, val):
    print '%s(%s) -->' % (getattr(func,'func_name'),val), func(val)


def _run_test_fail (func, val):
    try:
        func (val)
    except ValueError:
        print '%s(%s) --> ValueError as expected' % (getattr(func,'func_name'),val)

def test ():
    _run_test_ok   (not_empty, 'Valid')
    _run_test_fail (not_empty, '')

    _run_test_ok   (is_email, 'valid@email.com')
    _run_test_fail (is_email, 'invalid@mail')

    _run_test_ok   (is_list, 'a,b')
    _run_test_fail (is_list, 'a,b')

    _run_test_ok   (is_numeric_list, '1,2')
    _run_test_fail (is_numeric_list, 'a,b')

    _run_test_ok   (is_number, 100)
    _run_test_fail (is_number, '1OO')

    _run_test_ok   (is_date, '20/10/2010')
    _run_test_fail (is_date, '30/02/3002')

    _run_test_ok   (is_time, '19:19')
    _run_test_fail (is_time, '39:39')


if __name__ == '__main__':
    test()

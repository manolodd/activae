# -*- coding: utf-8 -*-
#
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
# You may contact the copyright holder at: Fundacion CENATIC, Avenida
# Clara Campoamor, s/n. 06200 Almendralejo (Badajoz), Spain
#
# NOTE: This version of CTK is a fork re-licensed by its author. The
#       mainstream version of CTK is available under a GPLv2 license
#       at the Cherokee Project source code repository.
#

PAGE_CLEAN_DUP_BEGIN = "\n___MAY_BE_DUPPED_BEGIN___\n"
PAGE_CLEAN_DUP_END   = "\n___MAY_BE_DUPPED_END___\n"


def Uniq_Block (txt):
    ret  = PAGE_CLEAN_DUP_BEGIN
    ret += txt
    ret += PAGE_CLEAN_DUP_END
    return ret

def Postprocess (txt):
    return _remove_dupped_code (txt)



def _remove_dupped_code (txt):
    dups = {}

    while True:
        # Find begin and end
        n1 = txt.find(PAGE_CLEAN_DUP_BEGIN)
        if n1 == -1:
            return txt

        n2 = txt.find(PAGE_CLEAN_DUP_END)
        assert n2 != -1

        # Remove tags
        maybe_dupped = txt[n1+len(PAGE_CLEAN_DUP_BEGIN):n2]
        if maybe_dupped in dups:
            txt = txt[:n1] + txt[n2+len(PAGE_CLEAN_DUP_END):]
        else:
            txt = txt[:n1] + maybe_dupped + txt[n2+len(PAGE_CLEAN_DUP_END):]
            dups[maybe_dupped] = True

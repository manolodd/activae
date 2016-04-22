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
# You may contact the copyright holder at: Fundacion CENATIC, Edificio
# de Servicios Sociales: C/ Vistahermosa, 1, 3ra planta, 06200
# Almendralejo (Badajoz), Spain

import CTK
import Auth
import Bookmark
import Asset

APPEND_JS = """
$("#%s").val($.trim($("#%s").val() +' '+ $("#%s").val()));
"""

OPTIONS_JS = """
var renders = %s;
$('#%s').show().html(renders[$('#%s').val()]);
"""

class ComboTextField (CTK.Container):
    def __init__ (self, props={}, options=[], option_renders={}):
        CTK.Container.__init__ (self)

        self.props = props.copy()

        # Option View
        box = CTK.Box({'id': 'info_%s' % self.id, 'class': 'no-see part_info'})

        # TextField widget
        text_props = self.props.copy()
        text_props['class'] = '%s two_fields'%(text_props.get('class',''))
        text = CTK.TextField(text_props)

        # Combowidget
        combo_props = self.props.copy()
        combo_props['name'] = "%s_combo"%(props['name'])

        combo = CTK.Combobox (combo_props, options)
        combo.bind ('change', APPEND_JS % (text.id, text.id, combo.id))
        combo.bind ('change', OPTIONS_JS % (str(option_renders), box.id, combo.id))

        # Chooser
        table = CTK.Table()
        table[(1,1)] = text
        table[(1,2)] = CTK.RawHTML (" ")
        table[(1,3)] = combo

        self += table
        self += box


class PartChooser (ComboTextField):
    def __init__ (self, props={}):
        user_id   = Auth.get_user_id()
        bookmarks = Bookmark.get_user_bookmarks (user_id)
        options   = [('','--')]+[(b,'#%s'%b) for b in bookmarks]
        props['selected'] = ''
        renders = self._render_options (bookmarks)

        ComboTextField.__init__ (self, props, options, renders)

    def _render_options (self, bookmarks):
        renders = {}
        for asset_id in bookmarks:
            try:
                asset = Asset.Asset (asset_id)
                diz   = asset.get_diz()
                diz['id'] = asset_id
                info  = CTK.RawHTML('<p><img src="%(thumb)s" /></p>'
                                    '<p>Activo: #%(id)d</p>'
                                    '<p>T&iacute;tulo: %(title)s</p>'
                                    '<p>Autor: %(creator)s</p>'
                                    '<p>Licencia: %(license)s</p>'% (diz))
                renders[asset_id] = info.Render().html
            except IndexError:
                pass

        return renders

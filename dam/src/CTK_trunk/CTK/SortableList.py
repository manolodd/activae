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

from Table import Table
from Server import publish
from PageCleaner import Uniq_Block

HEADER = [
    '<script type="text/javascript" src="/CTK/js/jquery.tablednd_0_5.js"></script>'
]

JS_INIT = """
$("#%(id)s").tableDnD({
   onDrop: function (table, row) {
       $.ajax ({url:      "%(url)s",
                async:    true,
                type:     "POST",
		dataType: "text",
                data:     $.tableDnD.serialize_plain(),
	        success:   function (data_raw) {
                  var data = eval('(' + data_raw + ')');

		  if (data['ret'] == 'ok') {
                    /* Modified: Save button */
                    var modified     = data['modified'];
                    var not_modified = data['not-modified'];

                    if (modified != undefined) {
                       $(modified).show();
                       $(modified).removeClass('saved');
                    } else if (not_modified) {
                       $(not_modified).addClass('saved');
                    }
                  }

                  /* Signal */
                  $("#%(id)s").trigger ('reordered');
                }
              });
   },
   dragHandle: "dragHandle",
   containerDiv: $("#%(container)s")
});
"""

JS_INIT_FUNC = """
jQuery.tableDnD.serialize_plain = function() {
     var result = "";
     var table  = jQuery.tableDnD.currentTable;

     /* Serialize */
     for (var i=0; i<table.rows.length; i++) {
         if (result.length > 0) {
              result += ",";
         }
         result += table.rows[i].id;
     }
     return table.id + "_order=" + result;
};
"""

def changed_handler_func (callback, key_id, **kwargs):
    return callback (key_id, **kwargs)

class SortableList (Table):
    def __init__ (self, callback, container, *args, **kwargs):
        Table.__init__ (self, *args, **kwargs)
        self.id  = "sortablelist_%d" %(self.uniq_id)
        self.url = "/sortablelist_%d"%(self.uniq_id)
        self.container = container

        # Register the public URL
        publish (self.url, changed_handler_func, method='POST',
                 callback=callback, key_id='%s_order'%(self.id), **kwargs)

    def Render (self):
        render = Table.Render (self)

        props = {'id': self.id, 'url': self.url, 'container': self.container}

        render.js      += JS_INIT %(props) + Uniq_Block (JS_INIT_FUNC %(props))
        render.headers += HEADER
        return render

    def set_header (self, row_num):
        # Set the row properties
        self[row_num].props['class'] = "nodrag nodrop"

        # Let Table do the rest
        Table.set_header (self, num=row_num)

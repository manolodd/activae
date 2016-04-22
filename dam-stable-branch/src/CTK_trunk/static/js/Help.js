/*
 * Copyright (C) 2010 CENATIC: Centro Nacional de Referencia de
 * Aplicacion de las TIC basadas en Fuentes Abiertas, Spain.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   Redistributions of source code must retain the above copyright
 *   notice, this list of conditions and the following disclaimer.
 *
 *   Redistributions in binary form must reproduce the above copyright
 *   notice, this list of conditions and the following disclaimer in
 *   the documentation and/or other materials provided with the
 *   distribution.
 *
 *   Neither the name of the CENATIC nor the names of its contributors
 *   may be used to endorse or promote products derived from this
 *   software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 * ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *
 * You may contact the copyright holder at: Fundacion CENATIC, Avenida
 * Clara Campoamor, s/n. 06200 Almendralejo (Badajoz), Spain
 *
 * NOTE: This version of CTK is a fork re-licensed by its author. The
 *       mainstream version of CTK is available under a GPLv2 license
 *       at the Cherokee Project source code repository.
 */

function Help_update_group (group_prefix, active_value) {
    prefix = group_prefix.replace('!','_');

    /* Hide all the entries */
    selector = '.help #help_group_'+prefix;
    $(selector).children().each(function(){
	   $(this).hide();
    });

    /* Show the right group */
    selector = '.help #help_group_'+prefix+' #help_group_'+active_value;
    $(selector).show();
}

var help_a_size = 0;
function toggleHelp() {
    if ($("#help-a").width() == 230) {
        $("#help .help").fadeOut(200, function() {
            $("#help-a").animate({ width: help_a_size + 'px' }, 100);
        });
    } else {
        help_a_size = $("#help-a").width();
        $("#help-a").animate({ width: '230px' }, 100, function() {
            $("#help .help").fadeIn(200);
        });
    }
}

function Help_add_entries (helps) {
    var help = $('.help:first');

    /* Remove previously merged entries
     */
    $('.help_entry.merged').remove();

    /* Add new entries
     */
    for (var tmp in helps) {
	   var name = helps[tmp][0];
	   var file = helps[tmp][1];

	   if (file.search("://") == -1) {
		  url = '/help/'+file+'.html';
	   } else {
		  url = file;
	   }

	   help.append ('<div class="help_entry merged"><a href="'+url+'" target="cherokee_help">'+name+'</a></div>');
    }
}
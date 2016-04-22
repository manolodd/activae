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

// Workaround to prevent double inclussion
if ((typeof submitter_loaded) == 'undefined') {
    submitter_loaded = true;

 ;(function($) {
    var Submitter = function (element, url, optional) {
	   var optional_str = optional;
	   var key_pressed  = false;
	   var orig_values  = {};
	   var obj          = this;       //  Object {}
	   var self         = $(element); // .submitter

	   // PRIVATE callbacks
	   //
	   function input_keypress_cb (event) {
	       if (event.keyCode == 13) {
			 submit_form();
			 return;
	       }

		  key_pressed = true;
	   };

	   function input_blur_cb (event) {
		  /* Only proceed when something */
		  if (! key_pressed) {
			 return;
		  }

		  /* Procced on the last entry */
		  var last = self.find(":text,:password,textarea").filter(".required:last");
		  if ((last.attr('id') != undefined) &&
			 (last.attr('id') != event.currentTarget.id))
		  {
			 return;
		  }

		  /* Check fields fulfillness */
		  if (! is_fulfilled()) {
			 return;
		  }
		  submit_form();
	   };

	   function input_checkbox_cb (event) {
		  if (! is_fulfilled()) {
			 return;
		  }
		  submit_form();
	   }

	   function input_combobox_cb (event) {
		  if (! is_fulfilled()) {
			 return;
		  }
		  submit_form();
	   }

	   // PRIVATE
	   //
	   function is_fulfilled () {
		  var full = true;
		  self.find (".required:text, .required:password, textarea.required").not('.optional').each(function() {
			 if (! this.value) {
				full = false;
				return false; /* stops iteration */
			 }
		  });
		  return full;
	   }

	   function restore_orig_values () {
		  for (var key in orig_values) {
			 self.find("#"+key).attr ('value', orig_values[key]);
	       }
	   }

	   function submit_in() {
		  $("#activity").show();
		  self.find("input,select,textarea").attr("disabled", true);
	   }

	   function submit_out() {
		  $("#activity").fadeOut('fast');
		  self.find("input,select,textarea").removeAttr("disabled");
	   }

	   function submit_form() {
		  /* Block the fields */
		  submit_in();

		  /* Build the post */
		  info = {};
		  self.find ("input:text, input:password, input:hidden").each(function(){
			 if ((!$(this).hasClass('optional')) || (this.value != optional_str)) {
				info[this.name] = this.value;
			 }
		  });
		  self.find ("input:checkbox").each(function(){
			 info[this.name] = this.checked ? "1" : "0";
		  });
		  self.find ("select").each(function(){
			 info[this.name] = $(this).val();
		  });
		  self.find ("textarea").each(function(){
			 info[this.name] = $(this).val();
		  });

		  if (info.__count__ == 0) {
			 submit_out();
			 return;
		  }

		  /* Remove error messages */
		  self.find('div.error').html('');

		  /* Async POST */
		  $.ajax ({
			 type:     'POST',
			 url:       url,
			 async:     true,
			 dataType: 'json',
			 data:      info,
			 success:   function (data) {
				if (data['ret'] != "ok") {
				    /* Set the error messages */
				    for (var key in data['errors']) {
					   self.find ("div.error[key='"+ key +"']").html(data['errors'][key]);
					   had_errors = 1;
				    }

				    /* Update the fields */
				    for (var key in data['updates']) {
					   self.find ("input[name='"+ key +"']").attr('value', data['updates'][key]);
				    }
				}
				if (data['redirect'] != undefined) {
				    window.location.replace (data['redirect']);
				}

				/* Trigger events */
				var event_type;

				if (data['ret'] == "ok") {
				    event_type = 'submit_success';
				} else {
				    event_type = 'submit_fail';
				}
				self.trigger({type: event_type, url: url, ret: data['ret'], ret_data: data});

				/* Modified: Save button */
				var modified     = data['modified'];
				var not_modified = data['not-modified'];

				if (modified != undefined) {
				    $(modified).show();
				    $(modified).removeClass('saved');
				} else if (not_modified) {
				    $(not_modified).addClass('saved');
				}
			 },
			 error: function (xhr, ajaxOptions, thrownError) {
				restore_orig_values();
				// alert ("Error: " + xhr.status +"\n"+ xhr.statusText);
				self.trigger({type: 'submit_fail', url: url, status: xhr.status});
			 },
			 complete:  function (XMLHttpRequest, textStatus) {
				/* Unlock fields */
				submit_out();

				/* Update Optional fields */
				self.find('.optional').each(function() {
				    $(this).trigger('update');
				});
			 }
		  });
	   }

	   // PUBLIC
	   //
	   this.submit_form = function() {
		  submit_form (obj);
		  return obj;
	   };

	   this.init = function (self) {
		  /* Events */
		  self.find(":text, :password, textarea").not('.noauto').bind ('keypress', self, input_keypress_cb);
		  self.find(":text, :password, textarea").not('.noauto').bind ("blur", self, input_blur_cb);
		  self.find(":checkbox").not('.required,.noauto').bind ("change", self, input_checkbox_cb);
		  self.find("select").not('.required,.noauto').bind ("change", self, input_combobox_cb);

		  /* Original values */
		  self.find(":text,textarea").each(function(){
			 orig_values[this.id] = this.value;
		  });

		  return obj;
	   }
    };

    $.fn.Submitter = function (url, optional) {
	   var self = this;
	   return this.each(function() {
		  if ($(this).data('submitter')) return;
		  var submitter = new Submitter(this, url, optional);
		  $(this).data('submitter', submitter);
		  submitter.init(self);
	   });
    };

  })(jQuery);

} // Double inclusion

// REF: http://www.virgentech.com/code/view/id/3

odoo.define('implifie_app.trigger', function (require) {
    "use strict";

    var FormView = require('web.FormView');  // Ensure FormView is imported
    var core = require('web.core');  // Core is needed for qweb and other utilities
    var ajax = require('web.ajax');  // To make the ajax calls

    FormView.include({
        start: function () {
            this._super.apply(this, arguments);
            this._bind_template_name();
        },

        _bind_template_name: function () {
            var self = this;
            // Bind the template_name field to dynamically fetch data
            this.$('input[name="template_name"]').on('input', function () {
                var template_name = $(this).val();
                if (template_name) {
                    // Make an RPC call to fetch templates based on the template name
                    ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                        model: 'implifie.trigger',
                        method: 'fetch_templates',
                        args: [],
                    }).then(function (templates) {
                        var templateOptions = '';
                        templates.forEach(function (template) {
                            templateOptions += '<option value="'+ template.name +'">'+ template.name +'</option>';
                        });
                        // Populate template dropdown with fetched template names
                        self.$('input[name="template_name"]').html(templateOptions);
                    });
                }
            });
        }
    });
});

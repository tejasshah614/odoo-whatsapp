odoo.define('implifie_app.broadcast', ['web.ajax', 'web.core', 'web.Widget', 'web.field_registry', 'web.basic_fields'], function (require) {
    "use strict";

    const core = require('web.core');
    const Widget = require('web.Widget');
    const registry = require('web.field_registry');
    const FieldChar = require('web.basic_fields').FieldChar;
    const qweb = core.qweb;
    const _t = core._t;

    // Add template reference here
    qweb.add_template("/implifie_app/static/src/xml/broadcast_action_templates.xml");
    console.log("Template loaded:", qweb.templates);

    var BroadcastCSVField = Widget.extend({
        // Widget definition starts here
    
        // Initialize the widget
        init: function (parent, name, record, options) {
            this._super.apply(this, arguments);
            console.log("BroadcastCSVField widget initialized"); // Add this log
            this.csvHeaders = []; // Store CSV headers dynamically
        },

        /**
         * Render the widget and update its DOM based on the state.
         */
        _render: function () {
            const $el = this.$el.empty(); // Clear the element's contents
            // Append the file upload input
            const fileInput = $('<input>', {
                type: 'file',
                id: 'csv_file_upload',
                class: 'form-control',
                accept: '.csv',
            });
            $el.append(fileInput);

            if (this.csvHeaders.length) {
                // Render the dropdown using QWeb template if headers are available
                const selectDropdown = qweb.render('BroadcastCSVFieldDropdown', {
                    headers: this.csvHeaders,
                    
                });
                console.log("Rendered Dropdown:", selectDropdown); // Log the rendered dropdown
                $el.append(selectDropdown);
            } else {
                // Display a warning if no headers are available
                $el.append(
                    $('<div>', {
                        class: 'alert alert-warning mt-2',
                        text: _t('Please upload a valid CSV file to see contact fields.'),
                    })
                );
            }
        },

        /**
         * Handle CSV file upload and extract headers.
         */
        _onCSVFileUpload: function (event) {
            console.log("CSV file uploaded"); // Add this log
            const fileInput = event.target;
            if (fileInput.files.length === 0) return;

            const file = fileInput.files[0];
            const reader = new FileReader();

            reader.onload = (e) => {
                const content = btoa(e.target.result); // Base64 encode the content

                // Call the server-side method to extract CSV headers
                this._rpc({
                    model: this.record.model,
                    method: 'extract_csv_headers',
                    args: [content],
                })
                    .then((headers) => {
                        if (headers) {
                            this.csvHeaders = headers; // Update headers dynamically
                        } else {
                            this.csvHeaders = [];
                        }
                        this._render(); // Re-render widget with updated headers
                    })
                    .catch((error) => {
                        console.error('Error extracting CSV headers:', error);
                        this.csvHeaders = [];
                        this._render(); // Show an error message
                    });
            };

            reader.readAsText(file); // Read the uploaded file
        },
    });

    /**
     * Register the widget for the `contact_csv` field.
     */
    registry.add('broadcast_csv_field', BroadcastCSVField);

    return BroadcastCSVField;
});

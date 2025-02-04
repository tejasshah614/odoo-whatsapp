from odoo import models, fields, api, exceptions, _
import requests
import logging

_logger = logging.getLogger(__name__)

class Trigger(models.Model):
    _name = 'trigger.action'
    _description = 'Trigger Action'

    app_id = fields.Many2one('ir.module.module', string='Trigger App', required=True, help="Select the application.", ondelete='cascade')
    model_id = fields.Many2one('ir.model', string='Trigger Module', required=True, domain="[('transient', '=', False)]", help="Select the module.", ondelete='cascade')
    event = fields.Selection([('create', 'On Create'), ('write', 'On Update')], string='Trigger Event', required=True, help="Select the event to trigger on.")
    
    # Replace Many2one with a simple Char or Selection field to hold template data.
    template_name = fields.Selection(string="Select Whatsapp Template to send", required=True, 
                                      selection=lambda self: self._get_template_selection(),
                                      ondelete={'set null'})  # Dynamically populate dropdown

    active = fields.Boolean(string="Active", help="Toggle to activate or deactivate the trigger.")
    current_page = fields.Integer(default=1, help="Tracks the current page of templates fetched.")
    total_pages = fields.Integer(default=1, help="Tracks the total number of pages available.")
    template_data = fields.Text(string="Template Data", readonly=True, help="Stores fetched template data.")
    language = fields.Char(string="Language", help="Stores the language from the API response.", invisible=True)

    _template_language_mapping = {}  # Temporary storage for template-to-language mapping

    def _get_api_token(self):
        """
        Retrieve the API token from system settings.
        """
        token = self.env['ir.config_parameter'].sudo().get_param('implifie_app.implifie_api_token', default=False)
        if not token:
            raise exceptions.UserError(_("API token is not configured. Please set it in Settings."))
        return token

    @api.model
    def _get_template_selection(self):
        """Fetch templates dynamically for the dropdown selection."""
        api_token = self._get_api_token()
        url = "https://api.implifie.com/v1/template/?type=approved"
        headers = {
            "Authorization": f"Bearer {api_token}"
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                templates = response.json()
                unique_templates = {}
                for template in templates:
                    template_name = template['name']
                    template_language = template.get('language', 'en_US')  # Default language if not provided
                    if template_name not in unique_templates:
                        unique_templates[template_name] = template_language
                        self._template_language_mapping[template_name] = template_language  # Save in mapping

                # Save the template language for each selection
                self.language = ",".join(unique_templates.values())  # Store as a comma-separated string (if needed)
                return [(name, name) for name in unique_templates.keys()]
            else:
                _logger.error(f"Failed to fetch templates: {response.status_code} - {response.text}")
                return []
        except requests.exceptions.RequestException as e:
            _logger.error(f"Request exception: {str(e)}")
            return []

    def create(self, vals):
        """Override create to set language based on template_name."""
        if 'template_name' in vals:
            language = self._template_language_mapping.get(vals['template_name'], "en_US")
            print(f'language :::{language}')
            vals['language'] = language  # Add language to create values
        return super(Trigger, self).create(vals)


    def write(self, vals):
        """Override write to update language based on template_name."""
        if 'template_name' in vals:
            language = self._template_language_mapping.get(vals['template_name'], "en_US")
            print(f'language :::{language}')
            vals['language'] = language  # Update language in write values

        return super(Trigger, self).write(vals)

    

    def send_template(self, request_data):
        _logger.info(f"Sending template with data: {request_data}")

        """
        Send the selected template to the SaaS API with dynamically built request body.
        """
        if not request_data.get('template'):
            raise exceptions.UserError(_("Please select a template to send."))

        api_url = "https://api.implifie.com/v1/send_template/"
        headers = {
            "Authorization": f"Bearer {self._get_api_token()}",
            "Content-Type": "application/json",
        }

        try:
            _logger.info("Sending template with payload: %s", request_data)

            response = requests.post(api_url, json=request_data, headers=headers, timeout=10)
            if response.status_code != 200:
                _logger.error("Failed to send template: %s", response.text)
                raise exceptions.UserError(_("Error sending template: %s") % response.text)

            _logger.info("Template sent successfully.")
        except requests.RequestException as e:
            _logger.exception("Error sending template")
            raise exceptions.UserError(_('Error: %s') % str(e))
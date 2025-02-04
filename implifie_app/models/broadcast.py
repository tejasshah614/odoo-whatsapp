from odoo import models, fields, api, _
import logging
import csv
from datetime import datetime, timedelta
from io import StringIO
import requests
import base64
import json
_logger = logging.getLogger(__name__)


class CsvHeader(models.Model):
    _name = 'csv.header'
    _description = 'CSV Header'

    name = fields.Char(string='Header Name', required=True)

class BroadcastCharField(models.Model):
    _name = 'broadcast.charfield'
    _description = 'Broadcast Char Field'

    broadcast_id = fields.Many2one(
        'broadcast.action',
        string="Broadcast",
        ondelete='cascade'
    )
    name = fields.Char(
        string="Text Field",
        help="Dynamic text field for body samples."
    )

class BroadcastAction(models.Model):
    _name = 'broadcast.action'
    _description = 'Broadcast Action'

    name = fields.Char(string='Name', required=True, help="Name of the broadcast action.")
    template = fields.Selection(string="Template", required=True, selection=lambda self: self._fetch_templates(), help="Select the template.")
    header_text_sample = fields.Char(
    string="Header Text Sample",
    help="Dynamically populated header text sample."
)
    show_header_text_sample = fields.Boolean(
        string="Show Header Text Sample",
        default=False,
        help="Controls visibility of the header text sample field."
    )
    
    body_sample = fields.One2many(
        'broadcast.charfield',
        'broadcast_id',
        string="Text Fields",
        help="Dynamic text fields based on body samples."
    )
    show_body_sample = fields.Boolean(
        string="Show Body Sample",
        default=False,
        help="Controls visibility of body sample fields."
    )
    start_at = fields.Datetime(string="Start At", help="Scheduled start time for the broadcast.")
    end_at = fields.Datetime(string="End At", help="Scheduled end time for the broadcast.")
    # status = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('scheduled', 'Scheduled'),
    #     ('sent', 'Sent'),
    #     ('canceled', 'Canceled')
    # ], string="Status", default='draft', help="Status of the broadcast.")
    # recurring_period = fields.Selection([
    #     ('weekly', 'Weekly'),
    #     ('twice_a_month', 'Twice a Month'),
    #     ('monthly', 'Monthly')
    # ], string="Recurring Period", help="Choose a recurring period.")
    contact_source = fields.Selection([
        ('crm_tags', 'Contact CRM Tags'),
        ('csv_upload', 'CSV Upload')
    ], string="Contact Source", required=True, help="Select the source for contacts.")
    is_executed = fields.Boolean(string="Executed", default=False, help="Indicates whether the broadcast has been executed.")
    crm_tag_ids = fields.Many2many('crm.tag', string="Contact CRM Tags", help="Tags to filter contacts.")
    csv_file = fields.Binary(string="CSV Upload", help="Upload a CSV file for contacts.")
    contact_csv = fields.Many2one(
        'csv.header',  # Reference to the CSV header model
        string="Select Contact Field",
        help="Select a contact field from the CSV.",
    )
    csv_headers = fields.Char(
        string="CSV Headers",
        help="Store headers from the uploaded CSV file."
    )
    csv_filename = fields.Char(string="CSV Filename")
    crm_tags_visible = fields.Boolean(string="Show CRM Tags", default=False)
    csv_upload_visible = fields.Boolean(string="Show CSV Upload", default=False)
    status = fields.Integer(string="Status", default=0, help="Status of the trigger: 1 for Start, 0 for Stop")

    def _fetch_templates(self):
        """Fetch templates dynamically for the dropdown selection and store their body samples."""
        api_token = self.env['ir.config_parameter'].sudo().get_param('implifie_app.implifie_api_token', default=False)
        if not api_token:
            _logger.warning("API token is not configured. Please set it in Settings.")
            return []

        url = "https://api.implifie.com/v1/template/?type=approved"
        headers = {"Authorization": f"Bearer {api_token}"}

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                templates = response.json()

                # Ensure the names are unique
                seen_names = set()
                unique_templates = []
                for template in templates:
                    if template['name'] not in seen_names:
                        unique_templates.append((template['name'], template['name']))
                        seen_names.add(template['name'])

                return unique_templates
            else:
                _logger.error(f"Failed to fetch templates: {response.status_code} - {response.text}")
                return []
        except requests.exceptions.RequestException as e:
            _logger.error(f"Request exception: {str(e)}")
            return []
    @api.onchange('template')
    def _onchange_template(self):
        """Update char_fields based on the selected template's body_sample."""

        _logger.info(f"Context in onchange: {self.env.context}")

        if self.template:
            # Construct the URL using the selected template ID
            url = f"https://api.implifie.com/v1/template/{self.template}/"
            headers = {
                "Authorization": f"Bearer {self.env['ir.config_parameter'].sudo().get_param('implifie_app.implifie_api_token')}"
            }

            try:
                # Make the API call
                _logger.info(f'response ::{datetime.now()}')
                response = requests.get(url, headers=headers)
                _logger.info(f'response ::{datetime.now()}-{response}')

                # Check if the response is successful
                if response.status_code == 200:
                    # Parse the response to extract the body_sample
                    template_data = response.json()
                    body_samples = template_data.get('body_sample', {}).get('body_sample', [])
                    header_text_sample = template_data.get('header_text_sample')

                    # Log the body samples data
                    _logger.info(f"Body samples received: {body_samples}")

                    # Clear existing char fields before adding new ones
                    self.body_sample = [(5, 0, 0)]  # Deletes existing char_fields
                    if header_text_sample:
                    # Display the header_text_sample field dynamically
                        self.header_text_sample = header_text_sample
                        self.show_header_text_sample = True
                    else:
                        _logger.info(f"No header text sample data found for template {self.template}")
                        self.header_text_sample = False
                        self.show_header_text_sample = False

                    if body_samples:
                        # Dynamically create one char field per body_sample value
                        char_field_vals = [(0, 0, {'name': sample, 'broadcast_id': self.id}) for sample in body_samples]
                        self.body_sample = char_field_vals  # Assign new records
                        self.show_body_sample = True  # Set to True to show the body_sample fields
                    else:
                        _logger.warning(f"No body sample data found for template {self.template}")
                        self.show_body_sample = False  # Set to False if no body_sample data
                    

                else:
                    _logger.error(f"Failed to fetch template data: {response.status_code} - {response.text}")

            except requests.exceptions.RequestException as e:
                _logger.error(f"Request exception: {str(e)}")

   
    def create(self, vals):
        """Override create to log broadcasts."""
        _logger.info(f"Creating Broadcast Action with values: {vals}")
        return super(BroadcastAction, self).create(vals)



    @api.onchange('contact_source', 'csv_file')
    def _onchange_contact_source(self):
        """Dynamically control visibility of fields based on contact_source."""
        if self.contact_source == 'crm_tags':
            self.crm_tags_visible = True
            self.csv_upload_visible = False
            self.contact_csv = False  # Clear any previous selection
        elif self.contact_source == 'csv_upload':
            self.crm_tags_visible = False
            self.csv_upload_visible = True
            if self.csv_file:
            # Process the CSV file to extract headers
                
                _, headers = self.processed_csv()
                if headers:
                    
                    self._create_csv_header_records(headers)
                else:
                    self.csv_headers = []

        else:
            self.crm_tags_visible = False
            self.csv_upload_visible = False
            self.csv_headers = []

    @api.onchange('csv_file')
    def _clear_previous_csv_headers(self):
        """Clear previous CSV headers associated with this broadcast action."""
        # Only remove CsvHeader records related to this broadcast (or context)
        # Here you can use a context, or you can use a field on the record that ties it to a specific broadcast
        _logger.info("Clearing previous CSV headers for this broadcast.")
        self.env['csv.header'].search([]).unlink()  # Clear all existing CsvHeader records

    @api.depends('csv_headers')
    def _create_csv_header_records(self, headers):
        """Create CsvHeader records dynamically based on the CSV headers."""
        
        for header in headers:
            # Create a CsvHeader record for each CSV header
            self.csv_headers=header
            self.env['csv.header'].create({'name': header})
            
    def processed_csv(self):
        """Process the uploaded CSV file and extract headers."""
        if self.csv_file:
            try:
                # Decode the uploaded CSV file
                data = StringIO(base64.b64decode(self.csv_file).decode('utf-8'))
                csv_reader = csv.DictReader(data)
                contacts = []
                headers = csv_reader.fieldnames  # Extract headers from the CSV file
                if headers:
                    return contacts, headers
                else:
                    return [], []
            except Exception as e:
                _logger.error(f"Failed to process CSV: {str(e)}")
                return [], []
        return [], []

    def action_start(self):
        """Set status to 1 for Start and handle execution based on start_at."""
        # Ensure broadcast is not already executed
        if self.is_executed:
            _logger.info(f"Broadcast {self.id} has already been executed. No further action taken.")
            # raise exceptions.UserError(_("This broadcast has already been executed and cannot be started again."))

        # Set status to 1
        self.write({'status': 1})
        _logger.info(f"Broadcast {self.id} started successfully.")

        # Check if start_at is specified and valid
        if not self.start_at:
            # Execute immediately if start_at is not set
            _logger.info(f"No start date specified for Broadcast {self.id}. Executing immediately.")
            self.send_broadcast()
        else:
            # Convert start_at to datetime and check if it's in the past
            start_at_datetime = fields.Datetime.from_string(self.start_at)
            if start_at_datetime <= fields.Datetime.now():
                # Execute immediately if start_at is in the past
                _logger.info(f"Start date for Broadcast {self.id} is in the past. Executing immediately.")
                self.send_broadcast()
            else:
                model_id = self.env['ir.model'].search([('model', '=', 'broadcast.action')], limit=1)
                if not model_id:
                    # raise exceptions.UserError(_("Model for broadcast.action not found. Please ensure the model is defined correctly."))
                    _logger.info("Model for broadcast.action not found. Please ensure the model is defined correctly.")
                # Schedule cron job for future execution
                _logger.info(f"Scheduling Broadcast {self.id} for {self.start_at}.")
                self.env['ir.cron'].create({
                    'name': f'Scheduled Broadcast {self.id}',
                    'model_id': model_id.id,  # Replace 'module_name' with your module name
                    'state': 'code',
                    'code': f'model.browse({self.id}).send_broadcast()',
                    'nextcall': self.start_at,
                    'interval_number': 1,
                    'interval_type': 'days',
                    
                    
                })
    def action_stop(self):
        """Set status to 0 for Stop."""
        self.write({'status': 0})
        _logger.info(f"Trigger {self.id} stopped successfully.")

    def send_broadcast(self):
        """Send broadcast via API."""
        # Ensure the broadcast is not already executed
        if self.is_executed:
            _logger.info(f"Broadcast {self.id} has already been executed. No further action taken.")
            return

        _logger.info(f"Executing Broadcast {self.id}. Preparing to send messages.")

        # Prepare contacts based on contact_source
        if self.contact_source == 'crm_tags':
            # Filter CRM leads based on selected tags
            leads = self.env['crm.lead'].search([('tag_ids', 'in', self.crm_tag_ids.ids)])
            csv_data = [{'name': lead.name, 'phone': lead.phone} for lead in leads if lead.phone]
        elif self.contact_source == 'csv_upload':
            # Process CSV file for contacts
            if not self.contact_csv:
                _logger.warning("No contact field selected from CSV header.")
                return  # If no field is selected from the dropdown, do not continue
        
        # Pass the selected CSV header field to the process_csv method
            csv_data, headers = self.process_csv(self.csv_headers)
        else:
            csv_data = []

        if not csv_data:
            _logger.warning(f"No contacts found for Broadcast {self.id}.")
            return
        static_body_samples = [sample.name for sample in self.body_sample] if self.body_sample else []
        # _logger.info(f"Static body samples:::::::::::::::::::: {static_body_samples}")
        # Prepare payload
        template_placeholder = {
        "mapBody": [],  # Adjust as needed
        "mapHeader": None,
        "mapContactField": self.csv_headers or "phone",  # Use the selected CSV column or default to "phone"
        "staticBody":static_body_samples,
        "staticHeader":self.header_text_sample if self.header_text_sample else None
    }


        payload = json.dumps({
            "template": self.template,
            "csv_data": csv_data,
            "template_placeholder": template_placeholder
        })

        # Send API request
        api_url = "https://api.implifie.com/v1/send_bulk_message/"
        headers = {
            "Authorization": f"Bearer {self.env['ir.config_parameter'].sudo().get_param('implifie_app.implifie_api_token')}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(api_url, headers=headers, data=payload)
            if response.status_code == 201:
                _logger.info(f"Broadcast {self.id} sent successfully.")
                # Mark broadcast as executed
                self.write({'is_executed': True})
            else:
                _logger.error(f"Failed to send broadcast {self.id}: {response.text}")
        except Exception as e:
            _logger.error(f"Error during broadcast {self.id}: {str(e)}")

    def process_csv(self, contact_field):
        # """Process CSV and extract contacts based on selected contact_field."""
        if self.csv_file:
            try:
                data = StringIO(base64.b64decode(self.csv_file).decode('utf-8'))
                csv_reader = csv.DictReader(data)  # Use DictReader to handle headers dynamically
                contacts = []
                headers = csv_reader.fieldnames  # Get the headers from the CSV file
                _logger.info(f"headers {headers} contacts from CSV.")


                for row in csv_reader:
                    if row:  # Ensure the row is not empty
                        # Dynamically map based on the selected field (contact_field)
                        contact_data = {}
                        for header in headers:
                            contact_data[header] = row.get(header, '')  # Add all columns dynamically

                        contacts.append(contact_data)  # Add the entire row as contact data

                _logger.info(f"Processed {len(contacts)} contacts from CSV.")
                return contacts, headers  # Return both contacts and headers for the dropdown
            except Exception as e:
                _logger.error(f"Failed to process CSV: {str(e)}")
                return [], []  # Return empty if an error occurs
        return [], []

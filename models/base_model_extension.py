from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class BaseModelExtension(models.AbstractModel):
    _name = 'base.model.extension'
    _description = 'Base Model Extension for Trigger Actions'

    @api.model
    def _process_trigger_event(self, event):
        """Handle triggers dynamically."""
        model_name = self._name
        _logger.info(f'Processing trigger event for model: {model_name}, event: {event}')
        
        # Fetch triggers for this model and event
        triggers = self.env['trigger.action'].search([
            ('model_id.model', '=', model_name),
            ('event', '=', event),
            ('active', '=', True)
        ])
        _logger.info(f'triggers: {triggers}')

        if triggers:
            _logger.info(f'Found triggers: {len(triggers)}')
            for trigger in triggers:
                # Prepare record data for the request
                record_data = self._get_record_data(trigger)
                if record_data:
                    # _logger.info(f'Sending template for trigger: {trigger.name}')
                    trigger.send_template(record_data)
                else:
                    _logger.warning(f'No record data found for trigger: {trigger.name}')
        else:
            _logger.info(f'No active triggers found for event: {event} in model: {model_name}')

    def _get_record_data(self, trigger):
        """Build the request body dynamically based on trigger and record data."""
        contact_phone = getattr(self.partner_id, 'phone', "") if hasattr(self, 'partner_id') else ""
        email = getattr(self, 'email', None) or getattr(self, 'email_from', "")  # Safely get email or email_from
        template_name = trigger.steps.template_name  # Template name selected in the trigger
        language = trigger.steps.language or "en_US"  # Default to 'en_US' if not set
        contact_id = self.id  # Assuming the current record's ID is the contact ID

        placeholder_data = {
            'header_text': self.name,  # Example: record name as header text
            'body': [self.name],  # Example: using email for the body
        }

        # Construct the request body
        request_data = {
            'wa_number': contact_phone,
            'template': template_name,
            'language': language,
            'contact_phone': contact_phone,
            'contact_id': "",
            'placeholder': placeholder_data,
        }

        return request_data

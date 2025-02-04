from odoo import models, fields, api
import json
import requests

class WhatsAppMessage(models.Model):
    _name = 'whatsapp.message'
    _description = 'WhatsApp Chat Messages'
    _order = 'id desc'
    
    from_number = fields.Char(string="From Number")
    to_number = fields.Char(string="To Number")
    message = fields.Text(string="Message")
    status = fields.Selection([('sent', 'Sent'), ('received', 'Received')], string="Status")
    message_error = fields.Text(string="Error Message")
    partner_id = fields.Many2one('res.partner', string="Contact")

    def send_whatsapp_message(self, phone, message):
        """ Send a message via WhatsApp API """
        url = "https://api.implifie.com/v1/send_message/5/"
        payload = json.dumps({
            "number": 7,
            "phone": phone,
            "message_type": "text",
            "content": {
                "preview_url": True,
                "body": message
            }
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': '••••••'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()

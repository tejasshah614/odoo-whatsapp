from odoo import http
from odoo.http import request
import json

class ChatWebSocket(http.Controller):

    @http.route('/websocket/send_message', type='json', auth='user', methods=['POST'])
    def send_message(self, **post):
        """ Send message to WhatsApp API """
        message_text = post.get('message')
        if not message_text:
            return {'error': 'Message is empty'}

        # Send to API (mock)
        request.env['whatsapp.message'].sudo().create({
            'from_number': 'YOUR_NUMBER',
            'to_number': 'RECEIVER_NUMBER',
            'message': message_text,
            'status': 'sent',
            'partner_id': request.env.user.partner_id.id
        })

        request.env['bus.bus']._sendone('whatsapp.chat', {'message': message_text})
        return {'success': True}

    @http.route('/websocket/receive_message', type='json', auth='public', methods=['POST'], csrf=False)
    def receive_message(self, **post):
        """ Receive WhatsApp messages via Webhook """
        data = request.jsonrequest
        if data:
            message = request.env['whatsapp.message'].sudo().create({
                'from_number': data.get('from_number'),
                'to_number': data.get('to_number'),
                'message': data.get('message'),
                'status': 'received',
                'partner_id': request.env['res.partner'].sudo().search(
                    [('phone', '=', data.get('from_number'))], limit=1
                ).id
            })
            request.env['bus.bus']._sendone('whatsapp.chat', {'message': message.message})
            return {'status': 'success'}
        return {'status': 'error'}

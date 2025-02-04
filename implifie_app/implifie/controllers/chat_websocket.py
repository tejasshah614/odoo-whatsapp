import asyncio
import websockets
import json
from odoo import http
from odoo.http import request

clients = set()

async def handle_client(websocket, path):
    clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            request.env['implifie.chat.message'].sudo().create({
                'contact_id': data['contact_id'],
                'from_number': data['from_number'],
                'to_number': data['to_number'],
                'message': data['message'],
                'status': 'sent',
            })
            # Broadcast message to all clients
            await asyncio.wait([client.send(json.dumps(data)) for client in clients])
    finally:
        clients.remove(websocket)

async def start_server():
    async with websockets.serve(handle_client, "0.0.0.0", 8765):
        await asyncio.Future()  # Run forever

# Start WebSocket Server
asyncio.run(start_server())

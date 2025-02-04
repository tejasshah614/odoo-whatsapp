odoo.define('whatsapp_chat.websocket', function (require) {
    "use strict";

    var core = require('web.core');
    var rpc = require('web.rpc');
    var bus = require('bus.bus').bus;

    $(document).ready(function () {
        var input = $('#chat_input');
        var sendBtn = $('#send_msg');

        sendBtn.on('click', function () {
            var msg = input.val();
            if (msg.trim() !== '') {
                rpc.query({
                    route: '/websocket/send_message',
                    params: { message: msg }
                }).then(function (result) {
                    input.val('');
                });
            }
        });

        bus.on('notification', this, function (notifications) {
            _.each(notifications, function (notif) {
                if (notif.channel === 'whatsapp.chat') {
                    $('.o_mail_thread').append(
                        `<div class="o_message o_received">
                            <div class="o_msg_bubble">${notif.message}</div>
                        </div>`
                    );
                }
            });
        });

        bus.start_polling();
    });
});

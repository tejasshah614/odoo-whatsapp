{
    'name': 'Implifie App',
     'version': '1.8',
    'category': 'Implifie',
    'sequence': 15,
    'summary': '',
    'website': 'https://www.odoo.com/app/crm',
    'depends': ['base','crm','sale','account','product','contacts','web',],  # Make sure 'web' is listed as a dependency
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_view.xml', 
        'views/implifie_view.xml',
        'views/implifie_menu.xml',
        'views/broadcast_action_views.xml',
        # 'views/chat_menu.xml',
       
        
       
    ],
    

     'assets': {
    #    'web.assets_frontend': [
    #         #  'implifie_app/static/src/js/implifie_trigger.js',  # Path to your JavaScript file
    #          'implifie_app/static/src/js/broadcast.js',  # Path to your JavaScript file
    #      ],
         'web.assets_qweb': [  # For qweb templates
            'implifie_app/static/src/xml/broadcast_action_templates.xml',
            'implifie_app/static/js/chat.js',
             'implifie_app/static/src/css/chat.css',  # Custom styles
        ],
     },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

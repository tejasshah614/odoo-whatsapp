from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    implifie_api_token = fields.Char(
        string="Implifie API Token",
        config_parameter="implifie_app.implifie_api_token"  # This saves the token as a system parameter
    )

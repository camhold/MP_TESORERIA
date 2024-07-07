from odoo import _, api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Res Config Settings'
    
    account_debit_id = fields.Many2one('account.account', string='Cuenta Debito', domain="[('deprecated', '=', False)]", related='company_id.account_debit_id', readonly=False)
    account_credit_id = fields.Many2one('account.account', string='Cuenta Credito', domain="[('deprecated', '=', False)]", related='company_id.account_credit_id', readonly=False)
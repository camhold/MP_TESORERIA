from odoo import _, api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    _description = 'Res Company'
    
    account_debit_id = fields.Many2one('account.account', string='Cuenta Debito', domain="[('deprecated', '=', False)]")
    account_credit_id = fields.Many2one('account.account', string='Cuenta Credito', domain="[('deprecated', '=', False)]")
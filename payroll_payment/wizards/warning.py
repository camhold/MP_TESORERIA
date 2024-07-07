from odoo import _, api, fields, models

class Warning(models.TransientModel):
    _name = 'warning'
    _description = 'Warning'
    
    budget = fields.Monetary(string='Presupuesto', currency_field='currency_id')
    amount_total =  fields.Monetary(string='Total', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Moneda')
    symbol = fields.Char(string='Símbolo', related='currency_id.symbol')
    amount = fields.Monetary(string='Monto', currency_field='currency_id', compute='_compute_amount')
    payroll_payment_id = fields.Many2one('payroll.payment', string='Nómina')
    
    @api.depends('budget', 'amount_total')
    def _compute_amount(self):
        for record in self:
            record.amount = record.amount_total - record.budget
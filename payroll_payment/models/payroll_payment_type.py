from odoo import _, api, fields, models

class PayrollPaymentType(models.Model):
    _name = 'payroll.payment.type'
    _description = 'Payroll Payment Type'
        
    
    name = fields.Char(string='Nombre', required=True)
    is_remuneration = fields.Boolean(string='Es Remuneración')
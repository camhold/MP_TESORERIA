from odoo import _, api, fields, models

class ResBank(models.Model):
    _inherit = 'res.bank'
    _description = 'Res Bank'
    
    payroll_code = fields.Char(string='Código de nómina')
    format_template_xlsx = fields.Selection([
        ('bci', 'BCI'),
        ('scotiabank', 'Scotiabank'),
        ('itau', 'Itaú'),
        ], string='Plantilla XLSX', default='bci')
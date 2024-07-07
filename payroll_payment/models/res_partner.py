from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Res Partner'

    is_payroll = fields.Boolean(string='Es nómina', default=False)
    blocked_for_payments = fields.Boolean(string='Bloqueado para pagos', default=False)
    blocked_for_purchases = fields.Boolean(string='Bloqueado para compras', default=False) 
    subject_discount = fields.Boolean(string='Sujeto a descuento', default=False)
    percentage_discount = fields.Float(string='Porcentaje de descuento', default=0.0)
    retention_account_id = fields.Many2one(comodel_name="account.account", string="Cuenta de retención")
    conciliar_si = fields.Boolean(string="Conciliar SI?", default=False)
    
    @api.onchange('subject_discount')
    def _onchange_subject_discount(self):
        if not self.subject_discount:
            self.retention_account_id = False
            self.percentage_discount = 0.0
            
    @api.constrains('percentage_discount')
    def _constrains_percentage_discount(self):
        for record in self:
            if record.percentage_discount < 0 or record.percentage_discount > 100:
                raise ValidationError(_('El porcentaje de descuento debe estar entre 0 y 100.'))

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class PayrollPaymentLine(models.Model):
    _name = 'payroll.payment.line'
    _description = 'Payroll Payment Line'
    
    move_id = fields.Many2one('account.move', string='Factura')
    date = fields.Date(string='Fecha', related='move_id.date')
    currency_id = fields.Many2one('res.currency', string='Moneda', related='move_id.currency_id')
    amount_total = fields.Monetary(string='Total', currency_field='currency_id', related='move_id.amount_total')
    state = fields.Selection(string='Estado', related='move_id.state')
    mp_flujo_id = fields.Many2one(comodel_name="mp.flujo", related='move_id.mp_flujo_id', store=True, readonly=False, domain="[('grupo_flujo_ids', 'in', mp_grupo_flujo_id)]")
    mp_grupo_flujo_ids = fields.Many2many(related="mp_flujo_id.grupo_flujo_ids")
    # mp_grupo_flujo_id = fields.Many2one(comodel_name="mp.grupo.flujo", domain="[('id', 'in', mp_grupo_flujo_ids)]", related='move_id.mp_grupo_flujo_id', store=True, readonly=False)
    mp_grupo_flujo_id = fields.Many2one(comodel_name="mp.grupo.flujo", related='move_id.mp_grupo_flujo_id', store=True, readonly=False, domain="[]")
    payroll_payment_id = fields.Many2one('payroll.payment', string='Nómina')
    to_check = fields.Boolean(string='A revisar', related='move_id.to_check')
    partner_id = fields.Many2one('res.partner', string='Proveedor', related='move_id.partner_id', readonly=False)
    
    _sql_constraints = [
        ("move_unique", "unique(move_id)", "La factura ya se encuentra en una nómina."),
    ]
    
    @api.onchange('line_ids')
    def _onchange_line_ids(self):
        if self.line_ids and self.payroll_payment_id.amount_total > self.payroll_payment_id.budget:
            raise ValidationError(_('El monto total de las facturas es mayor al presupuesto.'))
    
    @api.onchange('move_id')
    def _onchange_move_id(self):
        if self.move_id and not self.move_id.for_payroll:
            raise ValidationError(_('La factura no se encuentra marcada para nómina.'))
        if self.move_id and self.move_id.payment_state != 'not_paid':
            raise ValidationError(_('La factura ya ha sido pagada.'))
        if self.move_id and self.move_id.currency_id != self.payroll_payment_id.currency_id:
            raise ValidationError(_('La factura no tiene la misma moneda que la nómina.'))
        if self.move_id and self.move_id.partner_id.blocked_for_payments:
            raise ValidationError(_('El proveedor se encuentra bloqueado para pagos.'))
        if self.move_id and len(self.move_id.partner_id.bank_ids) == 0:
            raise ValidationError(_('El proveedor no tiene bancos asociados.'))

    def unlink(self):
        for record in self:
            if not self.user_has_groups('base.group_system') and record.payroll_payment_id and record.payroll_payment_id.state != 'draft':
                raise ValidationError(_('No se puede eliminar una factura que ya ha sido enviada a menos que seas administrador.'))
            if record.move_id.payroll_payment_id:
                record.move_id.payroll_payment_id = False
        return super(PayrollPaymentLine, self).unlink()
    
    def action_review(self):
        self.ensure_one()
        context = {
            "default_move_id": self.move_id.id,
        }
        self.move_id.to_check = True
        context.update(self.env.context)
        self.unlink()
        view_id = self.env.ref("payroll_payment.account_move_observation_view_form").id
        return {
            "type": "ir.actions.act_window",
            "name": "Oservación",
            "res_model": "account.move.observation",
            "view_mode": "form",
            "views": [(view_id, "form")],
            "target": "new",
            "context": context,
        }
    
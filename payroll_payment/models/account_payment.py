from odoo import _, api, fields, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _description = 'Account Payment'
    
    mp_flujo_id = fields.Many2one(comodel_name="mp.flujo", domain="[('grupo_flujo_ids', 'in', mp_grupo_flujo_id)]")
    mp_grupo_flujo_ids = fields.Many2many(related="mp_flujo_id.grupo_flujo_ids")
    mp_grupo_flujo_id = fields.Many2one(comodel_name="mp.grupo.flujo", domain="[]")
    
    @api.onchange("mp_grupo_flujo_id")
    def _onchange_mp_flujo_id(self):
        for register_id in self:
            register_id.mp_flujo_id = self.env['mp.flujo']
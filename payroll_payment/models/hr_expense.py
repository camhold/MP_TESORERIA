from odoo import _, api, fields, models

class HrExpense(models.Model):
    _inherit = 'hr.expense'
    _description = 'Hr Expense'
    
    supplier_partner_id = fields.Many2one('res.partner', string='Proveedor')
    mp_flujo_id = fields.Many2one(comodel_name="mp.flujo")
    mp_grupo_flujo_ids = fields.Many2many(related="mp_flujo_id.grupo_flujo_ids")
    mp_grupo_flujo_id = fields.Many2one(comodel_name="mp.grupo.flujo", domain="[('id', 'in', mp_grupo_flujo_ids)]")
    
    @api.onchange("mp_flujo_id")
    def _onchange_mp_flujo_id(self):
        for register_id in self:
            register_id.mp_grupo_flujo_id = self.env['mp.grupo.flujo']
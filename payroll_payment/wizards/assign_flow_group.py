from odoo import _, api, fields, models

class AssignFlowGroup(models.TransientModel):
    _name = 'assign.flow.group'
    _description = 'Assign Flow Group'
    
    
    mp_flujo_id = fields.Many2one(comodel_name="mp.flujo", )
    mp_grupo_flujo_ids = fields.Many2many(related="mp_flujo_id.grupo_flujo_ids")
    mp_grupo_flujo_id = fields.Many2one(comodel_name="mp.grupo.flujo", domain="[('id', 'in', mp_grupo_flujo_ids)]")
    
    @api.onchange("mp_flujo_id")
    def _onchange_mp_flujo_id(self):
        for register_id in self:
            register_id.mp_grupo_flujo_id = self.env['mp.grupo.flujo']
            
    def action_assign(self):
        records = self.env['payroll.payment.line'].browse(self.env.context.get('active_ids', []))
        records.write({
            'mp_flujo_id': self.mp_flujo_id.id,
            'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id
            })
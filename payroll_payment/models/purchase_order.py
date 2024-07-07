from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _description = 'Purchase Order'
    
    
    @api.model
    def create(self, vals):
        if vals.get('partner_id'):
            partner = self.env['res.partner'].browse(vals['partner_id'])
            if partner.blocked_for_purchases:
                raise ValidationError(_('El proveedor se encuentra bloqueado para compras.'))
        return super().create(vals)
    
    def write(self, vals):
        if vals.get('partner_id'):
            partner = self.env['res.partner'].browse(vals['partner_id'])
            if partner.blocked_for_purchases:
                raise ValidationError(_('El proveedor se encuentra bloqueado para compras.'))
        return super().write(vals)
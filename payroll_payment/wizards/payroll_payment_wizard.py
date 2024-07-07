from odoo import _, api, fields, models

class PayrollPaymentWizard(models.TransientModel):
    _name = 'payroll.payment.wizard'
    _description = 'Payroll Payment Wizard'
    
    date = fields.Date('Fecha', related='payroll_payment_id.date')
    partner_bank_id = fields.Many2one('res.partner.bank', string='Banco', related='payroll_payment_id.partner_bank_id')
    payroll_payment_id = fields.Many2one('payroll.payment', string='Nómina', domain=[('state', '=', 'draft')])
    
    def process_payroll(self):
        move_ids = self.env.context.get('active_ids', [])
        moves = self.env['account.move'].browse(move_ids)
        moves_to_process = moves.filtered(
            lambda move: move.for_payroll
            and move.payment_state == 'not_paid' 
            and move.currency_id == self.payroll_payment_id.currency_id 
            and len(move.partner_id.bank_ids) > 0 
            and not move.partner_id.blocked_for_payments 
            and move.partner_id.is_payroll
            and not move.pending_payment_equal_move()
            )
        # if self.payroll_payment_id.state == 'draft':
        for move in moves_to_process:
            # line = self.env['payroll.payment.line'].create({
            #     'move_id': move.id,
            #     'payroll_payment_id': self.payroll_payment_id.id,
            #     # 'mp_flujo_id': move.mp_flujo_id.id if move.mp_flujo_id else False,
            #     # 'mp_grupo_flujo_id': move.mp_grupo_flujo_id.id if move.mp_grupo_flujo_id else False,
            #     # 'mp_grupo_flujo_ids': [(6, 0, move.mp_grupo_flujo_ids.ids)] if move.mp_grupo_flujo_ids else False,
            # })
        # moves_to_process.write({
        #     # 'for_payroll': True,
        #     'payroll_payment_id': self.payroll_payment_id.id
        #             })
            move.payroll_payment_id = self.payroll_payment_id.id
        if self.payroll_payment_id.amount_total > self.payroll_payment_id.budget:
            # warning = {}
            # warning['warning'] = {
            # 'title': 'Advertencia!',
            # 'message': f'Usted a excedido el presupuesto de la nómina {self.payroll_payment_id.name}.'
            # }
            # return warning
            record = self.env['warning'].create({
                'budget': self.payroll_payment_id.budget,
                'amount_total': self.payroll_payment_id.amount_total,
                'currency_id': self.payroll_payment_id.currency_id.id,
                'payroll_payment_id': self.payroll_payment_id.id
                })
            return {
                'name': _('Advertencia'),
                'view_mode': 'form',
                'res_model': 'warning',
                'type': 'ir.actions.act_window',
                'res_id': record.id,
                'target': 'new',
            }
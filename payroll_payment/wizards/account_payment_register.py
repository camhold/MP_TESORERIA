from odoo import _, api, fields, models
from odoo.exceptions import UserError
class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Account Payment Register'
    
    amount_total = fields.Monetary(string='Total', compute='_compute_amount_total')
    
    @api.depends('line_ids.amount_total', 'source_currency_id', 'currency_id')
    def _compute_amount_total(self):
        for wizard in self:
            wizard.amount_total = wizard.company_id.currency_id._convert(sum(wizard.line_ids.move_id.mapped('amount_total')), wizard.currency_id, wizard.company_id, wizard.payment_date or fields.Date.today()) if len(wizard.line_ids) else 0.0
    
    def _compute_amount(self):
        super(AccountPaymentRegister, self)._compute_amount()
        for wizard in self:
            wizard.amount = wizard.amount - wizard.amount_total * (wizard.partner_id.subject_discount and wizard.partner_id.percentage_discount/100 or 0)
    
    # @api.depends('amount')
    def _compute_payment_difference(self):
        for wizard in self:
            if wizard.source_currency_id == wizard.currency_id:
                # Same currency.
                wizard.payment_difference = wizard.source_amount_currency - wizard.amount - wizard.amount_total * (wizard.partner_id.subject_discount and wizard.partner_id.percentage_discount/100 or 0)
            elif wizard.currency_id == wizard.company_id.currency_id:
                # Payment expressed on the company's currency.
                wizard.payment_difference = wizard.source_amount  - wizard.amount - wizard.amount_total * (wizard.partner_id.subject_discount and wizard.partner_id.percentage_discount/100 or 0)
            else:
                # Foreign currency on payment different than the one set on the journal entries.
                amount_payment_currency = wizard.company_id.currency_id._convert(wizard.source_amount, wizard.currency_id, wizard.company_id, wizard.payment_date or fields.Date.today())
                wizard.payment_difference = amount_payment_currency - wizard.amount - wizard.amount_total * (wizard.partner_id.subject_discount and wizard.partner_id.percentage_discount/100 or 0)
                
    def _create_payment_vals_from_wizard(self):
        if self.payment_difference < 0 and self.payment_difference_handling == 'open':
            raise UserError(_("Lo restante corresponde a retenciones."))
        return super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
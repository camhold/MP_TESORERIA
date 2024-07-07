from odoo import _, api, fields, models

class ForeignCurrencyCentralization(models.Model):
    _name = 'foreign.currency.centralization'
    _description = 'Foreign Currency Centralization'

    account_account_ids = fields.Many2many('account.account', string='Account', required=True, domain=lambda self: [('currency_id', '!=', self.env.company.currency_id.id)])
    date = fields.Date(string='Date', required=True)
    currency_ids = fields.Many2many('res.currency', string='Currency', required=True, domain=lambda self: [('id', '!=', self.env.company.currency_id.id), ('active', '=', True)])
    
    def create_records(self):
        for record in self:
            for account in record.account_account_ids:
                for currency in record.currency_ids:
                    self.env['foreign.currency.centralization.line'].create({
                        'account_account_id': account.id,
                        'date': record.date,
                        # 'rate': 1,
                        'rate': self.env['res.currency']._get_conversion_rate(currency, account.currency_id or self.env.company.currency_id, account.company_id, record.date),
                        'currency_id': currency.id
                    })

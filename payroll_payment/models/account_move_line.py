from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("analytic_account_id")
    def _compute_analytic_tag_ids(self):
        for rec in self:
            if not rec._origin and rec.analytic_tag_ids:
                continue
            if rec.analytic_account_id.default_analytic_tag_ids:
                rec.analytic_tag_ids = rec.analytic_account_id.default_analytic_tag_ids
            else:
                rec.analytic_tag_ids = rec.analytic_tag_ids

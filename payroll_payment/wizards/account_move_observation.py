from odoo import _, api, fields, models

class AccountMoveObservation(models.TransientModel):
    _name = 'account.move.observation'
    _description = 'Account Move Observation'
    
    observation = fields.Text(string='Observación')
    move_id = fields.Many2one('account.move', string='Movimiento')
    
    def action_add_observation(self):
        # move_ids = self.env.context.get('active_ids', [])
        # moves = self.env['account.move'].browse(move_ids)
        self.move_id.write({
            'observation': self.observation
            })
        return True
from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    # Add clothing swap related fields to user
    clothing_profile_id = fields.One2many('user.profile', 'user_id', string='Clothing Swap Profile')
    points_balance = fields.Integer('Points Balance', related='clothing_profile_id.points_balance', readonly=True)
    
    @api.model
    def create(self, vals):
        """Create user profile when new user is created"""
        user = super().create(vals)
        self.env['user.profile'].create_profile_for_user(user.id)
        return user
    
    def get_or_create_profile(self):
        """Get or create user profile"""
        profile = self.env['user.profile'].search([('user_id', '=', self.id)], limit=1)
        if not profile:
            profile = self.env['user.profile'].create_profile_for_user(self.id)
        return profile

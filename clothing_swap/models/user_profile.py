from odoo import models, fields, api


class UserProfile(models.Model):
    _name = 'user.profile'
    _description = 'User Profile for Clothing Swap'
    _rec_name = 'user_id'

    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='cascade')
    points_balance = fields.Integer('Points Balance', default=50, help='Points available for redeeming items')
    total_items_listed = fields.Integer('Total Items Listed', compute='_compute_statistics')
    total_swaps_completed = fields.Integer('Total Swaps Completed', compute='_compute_statistics')
    total_points_earned = fields.Integer('Total Points Earned', default=50)
    total_points_spent = fields.Integer('Total Points Spent', default=0)
    
    # Profile information
    bio = fields.Text('Bio')
    location = fields.Char('Location')
    avatar = fields.Image('Avatar', related='user_id.image_1920')
    
    # Preferences
    preferred_brands = fields.Char('Preferred Brands', help='Comma-separated list')
    preferred_sizes = fields.Char('Preferred Sizes', help='Comma-separated list')
    preferred_categories = fields.Char('Preferred Categories', help='Comma-separated list')
    
    # Statistics
    items_listed_ids = fields.One2many('clothing.item', 'owner_id', string='Listed Items')
    swap_requests_made_ids = fields.One2many('swap.request', 'requester_id', string='Requests Made')
    swap_requests_received_ids = fields.One2many('swap.request', 'owner_id', string='Requests Received')
    
    # Ratings (for future implementation)
    average_rating = fields.Float('Average Rating', default=5.0)
    total_ratings = fields.Integer('Total Ratings', default=0)
    
    @api.depends('items_listed_ids', 'swap_requests_made_ids')
    def _compute_statistics(self):
        for record in self:
            record.total_items_listed = len(record.items_listed_ids)
            completed_swaps = record.swap_requests_made_ids.filtered(lambda r: r.state == 'completed')
            record.total_swaps_completed = len(completed_swaps)
    
    def add_points(self, points, reason=""):
        """Add points to user's balance"""
        self.points_balance += points
        self.total_points_earned += points
        if reason:
            self.message_post(body=f"Earned {points} points: {reason}")
    
    def deduct_points(self, points, reason=""):
        """Deduct points from user's balance"""
        if self.points_balance >= points:
            self.points_balance -= points
            self.total_points_spent += points
            if reason:
                self.message_post(body=f"Spent {points} points: {reason}")
            return True
        return False
    
    @api.model
    def create_profile_for_user(self, user_id):
        """Create a profile for a user if it doesn't exist"""
        existing = self.search([('user_id', '=', user_id)], limit=1)
        if not existing:
            return self.create({
                'user_id': user_id,
                'points_balance': 50,  # Welcome bonus
            })
        return existing

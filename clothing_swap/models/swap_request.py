from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SwapRequest(models.Model):
    _name = 'swap.request'
    _description = 'Swap Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char('Reference', required=True, readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('swap.request'))
    
    # Parties involved
    requester_id = fields.Many2one('res.users', string='Requester', required=True, default=lambda self: self.env.user)
    owner_id = fields.Many2one('res.users', string='Item Owner', required=True, related='item_id.owner_id', store=True)
    
    # Items
    item_id = fields.Many2one('clothing.item', string='Requested Item', required=True)
    offered_item_id = fields.Many2one('clothing.item', string='Offered Item', help='Item offered in exchange')
    
    # Request details
    request_type = fields.Selection([
        ('swap', 'Item Swap'),
        ('points', 'Points Redemption')
    ], string='Request Type', required=True, default='swap')
    
    points_used = fields.Integer('Points Used', default=0)
    message = fields.Text('Message to Owner')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    # Dates
    request_date = fields.Datetime('Request Date', default=fields.Datetime.now)
    response_date = fields.Datetime('Response Date', readonly=True)
    completion_date = fields.Datetime('Completion Date', readonly=True)
    
    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('swap.request') or '/'
        return super().create(vals)
    
    def action_submit(self):
        """Submit the swap request"""
        self.state = 'pending'
        self.request_date = fields.Datetime.now()
        
        # Validate points if it's a points redemption
        if self.request_type == 'points':
            user_profile = self.env['user.profile'].search([('user_id', '=', self.requester_id.id)], limit=1)
            if not user_profile or user_profile.points_balance < self.points_used:
                raise ValidationError("Insufficient points for this redemption.")
        
        # Notify the item owner
        self.message_post(
            body=f"New swap request from {self.requester_id.name}",
            message_type='notification',
            partner_ids=[self.owner_id.partner_id.id]
        )
    
    def action_accept(self):
        """Accept the swap request"""
        self.state = 'accepted'
        self.response_date = fields.Datetime.now()
        
        # Reserve the item
        self.item_id.action_reserve()
        
        if self.request_type == 'points':
            # Deduct points from requester
            requester_profile = self.env['user.profile'].search([('user_id', '=', self.requester_id.id)], limit=1)
            if requester_profile:
                requester_profile.points_balance -= self.points_used
            
            # Add points to owner
            owner_profile = self.env['user.profile'].search([('user_id', '=', self.owner_id.id)], limit=1)
            if owner_profile:
                owner_profile.points_balance += self.points_used
        
        self.message_post(body="Swap request accepted")
    
    def action_reject(self):
        """Reject the swap request"""
        self.state = 'rejected'
        self.response_date = fields.Datetime.now()
        self.message_post(body="Swap request rejected")
    
    def action_complete(self):
        """Mark the swap as completed"""
        self.state = 'completed'
        self.completion_date = fields.Datetime.now()
        
        # Mark item as swapped
        self.item_id.action_swap()
        
        # Award points to both parties
        requester_profile = self.env['user.profile'].search([('user_id', '=', self.requester_id.id)], limit=1)
        owner_profile = self.env['user.profile'].search([('user_id', '=', self.owner_id.id)], limit=1)
        
        if self.request_type == 'swap':
            # Both parties get points for successful swap
            if requester_profile:
                requester_profile.points_balance += 5
            if owner_profile:
                owner_profile.points_balance += 5
        
        self.message_post(body="Swap completed successfully")
    
    def action_cancel(self):
        """Cancel the swap request"""
        self.state = 'cancelled'
        
        # Release reserved item
        if self.item_id.state == 'reserved':
            self.item_id.state = 'available'
        
        self.message_post(body="Swap request cancelled")

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ClothingItem(models.Model):
    _name = 'clothing.item'
    _description = 'Clothing Item'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char('Title', required=True, tracking=True)
    description = fields.Text('Description', required=True)
    image_1920 = fields.Image('Main Image', required=True, max_width=1920, max_height=1920)
    image_128 = fields.Image('Small Image', related='image_1920', max_width=128, max_height=128, store=True)
    
    # Item details
    size = fields.Selection([
        ('xs', 'XS'),
        ('s', 'S'),
        ('m', 'M'),
        ('l', 'L'),
        ('xl', 'XL'),
        ('xxl', 'XXL'),
        ('other', 'Other')
    ], string='Size', required=True)
    
    condition = fields.Selection([
        ('new', 'New with tags'),
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ], string='Condition', required=True, default='good')
    
    category = fields.Selection([
        ('tops', 'Tops'),
        ('bottoms', 'Bottoms'),
        ('dresses', 'Dresses'),
        ('outerwear', 'Outerwear'),
        ('shoes', 'Shoes'),
        ('accessories', 'Accessories'),
        ('other', 'Other')
    ], string='Category', required=True)
    
    brand = fields.Char('Brand')
    color = fields.Char('Color')
    tags = fields.Char('Tags', help='Comma-separated tags')
    
    # Status and ownership
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('swapped', 'Swapped'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True)
    
    owner_id = fields.Many2one('res.users', string='Owner', required=True, default=lambda self: self.env.user)
    points_value = fields.Integer('Points Value', default=10, help='Points required to redeem this item')
    
    # Dates
    create_date = fields.Datetime('Created On', readonly=True)
    approval_date = fields.Datetime('Approved On', readonly=True)
    swap_date = fields.Datetime('Swapped On', readonly=True)
    
    # Relations
    swap_request_ids = fields.One2many('swap.request', 'item_id', string='Swap Requests')
    swap_request_count = fields.Integer('Swap Requests', compute='_compute_swap_request_count')
    
    # Additional images
    image_ids = fields.One2many('clothing.item.image', 'item_id', string='Additional Images')
    
    @api.depends('swap_request_ids')
    def _compute_swap_request_count(self):
        for record in self:
            record.swap_request_count = len(record.swap_request_ids)
    
    def action_submit_for_approval(self):
        self.state = 'pending'
        self.message_post(body="Item submitted for approval")
    
    def action_approve(self):
        self.state = 'available'
        self.approval_date = fields.Datetime.now()
        self.message_post(body="Item approved and is now available for swap")
    
    def action_reject(self):
        self.state = 'rejected'
        self.message_post(body="Item rejected")
    
    def action_reserve(self):
        self.state = 'reserved'
        self.message_post(body="Item reserved")
    
    def action_swap(self):
        self.state = 'swapped'
        self.swap_date = fields.Datetime.now()
        self.message_post(body="Item swapped successfully")
    
    @api.model
    def create(self, vals):
        if 'owner_id' not in vals:
            vals['owner_id'] = self.env.user.id
        return super().create(vals)


class ClothingItemImage(models.Model):
    _name = 'clothing.item.image'
    _description = 'Additional Clothing Item Images'
    
    item_id = fields.Many2one('clothing.item', string='Clothing Item', required=True, ondelete='cascade')
    image_1920 = fields.Image('Image', required=True, max_width=1920, max_height=1920)
    image_128 = fields.Image('Small Image', related='image_1920', max_width=128, max_height=128, store=True)
    sequence = fields.Integer('Sequence', default=10)

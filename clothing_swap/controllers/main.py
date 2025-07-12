from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
import base64
import json


class ClothingSwapController(http.Controller):

    @http.route('/', type='http', auth='public', website=True)
    def index(self, **kwargs):
        """Landing page"""
        # Get featured items (latest 6 available items)
        featured_items = request.env['clothing.item'].sudo().search([
            ('state', '=', 'available')
        ], limit=6, order='create_date desc')
        
        # Get statistics
        total_items = request.env['clothing.item'].sudo().search_count([('state', '=', 'available')])
        total_users = request.env['user.profile'].sudo().search_count([])
        total_swaps = request.env['swap.request'].sudo().search_count([('state', '=', 'completed')])
        
        values = {
            'featured_items': featured_items,
            'total_items': total_items,
            'total_users': total_users,
            'total_swaps': total_swaps,
        }
        return request.render('clothing_swap.landing_page', values)

    @http.route('/browse', type='http', auth='public', website=True)
    def browse_items(self, search='', category='', size='', condition='', page=1, **kwargs):
        """Browse available items"""
        domain = [('state', '=', 'available')]
        
        # Apply filters
        if search:
            domain.append('|')
            domain.append(('name', 'ilike', search))
            domain.append(('description', 'ilike', search))
        
        if category:
            domain.append(('category', '=', category))
        
        if size:
            domain.append(('size', '=', size))
        
        if condition:
            domain.append(('condition', '=', condition))
        
        # Pagination
        items_per_page = 12
        total_items = request.env['clothing.item'].sudo().search_count(domain)
        offset = (int(page) - 1) * items_per_page
        
        items = request.env['clothing.item'].sudo().search(
            domain, 
            limit=items_per_page, 
            offset=offset,
            order='create_date desc'
        )
        
        # Calculate pagination
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        values = {
            'items': items,
            'search': search,
            'category': category,
            'size': size,
            'condition': condition,
            'current_page': int(page),
            'total_pages': total_pages,
            'categories': request.env['clothing.item']._fields['category'].selection,
            'sizes': request.env['clothing.item']._fields['size'].selection,
            'conditions': request.env['clothing.item']._fields['condition'].selection,
        }
        return request.render('clothing_swap.browse_items', values)

    @http.route('/item/<int:item_id>', type='http', auth='public', website=True)
    def item_detail(self, item_id, **kwargs):
        """Item detail page"""
        item = request.env['clothing.item'].sudo().browse(item_id)
        if not item.exists() or item.state != 'available':
            return request.not_found()
        
        # Get user's items for swap offers (if logged in)
        user_items = []
        if request.env.user._is_public():
            can_request = False
        else:
            can_request = item.owner_id.id != request.env.user.id
            user_items = request.env['clothing.item'].search([
                ('owner_id', '=', request.env.user.id),
                ('state', '=', 'available'),
                ('id', '!=', item_id)
            ])
        
        # Get user profile for points balance
        user_profile = None
        if not request.env.user._is_public():
            user_profile = request.env.user.get_or_create_profile()
        
        values = {
            'item': item,
            'can_request': can_request,
            'user_items': user_items,
            'user_profile': user_profile,
        }
        return request.render('clothing_swap.item_detail', values)

    @http.route('/item/request', type='http', auth='user', methods=['POST'], website=True, csrf=False)
    def request_item(self, **kwargs):
        """Handle swap/points request"""
        item_id = int(kwargs.get('item_id'))
        request_type = kwargs.get('request_type')
        offered_item_id = kwargs.get('offered_item_id')
        points_used = int(kwargs.get('points_used', 0))
        message = kwargs.get('message', '')
        
        item = request.env['clothing.item'].browse(item_id)
        if not item.exists() or item.state != 'available':
            return json.dumps({'error': 'Item not available'})
        
        # Create swap request
        vals = {
            'item_id': item_id,
            'request_type': request_type,
            'message': message,
        }
        
        if request_type == 'swap' and offered_item_id:
            vals['offered_item_id'] = int(offered_item_id)
        elif request_type == 'points':
            vals['points_used'] = points_used
        
        swap_request = request.env['swap.request'].create(vals)
        swap_request.action_submit()
        
        return request.redirect(f'/my/requests')

    @http.route('/add-item', type='http', auth='user', website=True)
    def add_item_form(self, **kwargs):
        """Add new item form"""
        categories = request.env['clothing.item']._fields['category'].selection
        sizes = request.env['clothing.item']._fields['size'].selection
        conditions = request.env['clothing.item']._fields['condition'].selection
        
        values = {
            'categories': categories,
            'sizes': sizes,
            'conditions': conditions,
        }
        return request.render('clothing_swap.add_item_form', values)

    @http.route('/add-item/submit', type='http', auth='user', methods=['POST'], website=True, csrf=False)
    def submit_item(self, **kwargs):
        """Submit new item"""
        # Handle file upload
        image_file = kwargs.get('image')
        if image_file:
            image_data = base64.b64encode(image_file.read())
        else:
            return request.redirect('/add-item?error=image_required')
        
        # Create item
        vals = {
            'name': kwargs.get('name'),
            'description': kwargs.get('description'),
            'size': kwargs.get('size'),
            'category': kwargs.get('category'),
            'condition': kwargs.get('condition'),
            'brand': kwargs.get('brand'),
            'color': kwargs.get('color'),
            'tags': kwargs.get('tags'),
            'points_value': int(kwargs.get('points_value', 10)),
            'image_1920': image_data,
        }
        
        item = request.env['clothing.item'].create(vals)
        item.action_submit_for_approval()
        
        return request.redirect('/my/items?success=item_submitted')


class ClothingSwapPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'item_count' in counters:
            values['item_count'] = request.env['clothing.item'].search_count([
                ('owner_id', '=', request.env.user.id)
            ])
        if 'request_count' in counters:
            values['request_count'] = request.env['swap.request'].search_count([
                '|',
                ('requester_id', '=', request.env.user.id),
                ('owner_id', '=', request.env.user.id)
            ])
        return values

    @http.route(['/my/dashboard'], type='http', auth='user', website=True)
    def my_dashboard(self, **kwargs):
        """User dashboard"""
        user_profile = request.env.user.get_or_create_profile()
        
        # Get user's items
        my_items = request.env['clothing.item'].search([
            ('owner_id', '=', request.env.user.id)
        ], order='create_date desc', limit=5)
        
        # Get recent requests
        my_requests = request.env['swap.request'].search([
            '|',
            ('requester_id', '=', request.env.user.id),
            ('owner_id', '=', request.env.user.id)
        ], order='create_date desc', limit=5)
        
        values = {
            'user_profile': user_profile,
            'my_items': my_items,
            'my_requests': my_requests,
        }
        return request.render('clothing_swap.my_dashboard', values)

    @http.route(['/my/items'], type='http', auth='user', website=True)
    def my_items(self, **kwargs):
        """User's items"""
        items = request.env['clothing.item'].search([
            ('owner_id', '=', request.env.user.id)
        ], order='create_date desc')
        
        values = {
            'items': items,
        }
        return request.render('clothing_swap.my_items', values)

    @http.route(['/my/requests'], type='http', auth='user', website=True)
    def my_requests(self, **kwargs):
        """User's swap requests"""
        sent_requests = request.env['swap.request'].search([
            ('requester_id', '=', request.env.user.id)
        ], order='create_date desc')
        
        received_requests = request.env['swap.request'].search([
            ('owner_id', '=', request.env.user.id)
        ], order='create_date desc')
        
        values = {
            'sent_requests': sent_requests,
            'received_requests': received_requests,
        }
        return request.render('clothing_swap.my_requests', values)

    @http.route('/my/request/<int:request_id>/accept', type='http', auth='user', methods=['POST'], website=True, csrf=False)
    def accept_request(self, request_id, **kwargs):
        """Accept a swap request"""
        swap_request = request.env['swap.request'].browse(request_id)
        if swap_request.owner_id.id == request.env.user.id:
            swap_request.action_accept()
        return request.redirect('/my/requests')

    @http.route('/my/request/<int:request_id>/reject', type='http', auth='user', methods=['POST'], website=True, csrf=False)
    def reject_request(self, request_id, **kwargs):
        """Reject a swap request"""
        swap_request = request.env['swap.request'].browse(request_id)
        if swap_request.owner_id.id == request.env.user.id:
            swap_request.action_reject()
        return request.redirect('/my/requests')

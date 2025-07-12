{
    'name': 'Clothing Swap Platform',
    'version': '1.0.0',
    'category': 'Website',
    'summary': 'A platform for users to swap clothing items with points system',
    'description': """
        Clothing Swap Platform
        ======================
        
        A comprehensive platform where users can:
        - List clothing items for swap
        - Browse and request items from other users
        - Earn and spend points for swaps
        - Manage their clothing inventory
        - Admin moderation system
    """,
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'depends': [
        'base',
        'website',
        'portal',
        'website_slides',
        'website_sale',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/website_data.xml',
        'views/clothing_item_views.xml',
        'views/swap_request_views.xml',
        'views/user_profile_views.xml',
        'views/website_templates.xml',
        'views/portal_templates.xml',
        'views/user_portal_templates.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'clothing_swap/static/src/css/clothing_swap.css',
            'clothing_swap/static/src/js/clothing_swap.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}

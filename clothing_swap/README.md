# Clothing Swap Platform

A comprehensive Odoo module for creating a clothing swap website where users can exchange clothing items using a points-based system.

## Features

### 🌟 Core Features
- **User Authentication**: Built-in Odoo email/password login system
- **Landing Page**: Public-facing homepage with featured items and statistics
- **Item Management**: Users can list clothing items with images and detailed metadata
- **Swap System**: Users can request items through direct swaps or points redemption
- **Points System**: Earn and spend points for successful swaps
- **Admin Panel**: Comprehensive admin interface for moderation and management

### 👤 User Features
- **User Dashboard**: Personal dashboard showing profile details, items, and swap history
- **Browse Items**: Advanced filtering and search functionality
- **Add Items**: Easy-to-use form for listing new clothing items
- **Request Management**: Send and receive swap requests
- **Points Balance**: Track earned and spent points

### 🛡️ Admin Features
- **Item Approval**: Moderate and approve item listings
- **User Management**: View and manage user profiles
- **Request Monitoring**: Track all swap requests and their status
- **Content Moderation**: Remove inappropriate content

## Installation

### Prerequisites
- Odoo 15.0+ (compatible with Odoo 16.0 and 17.0)
- Python 3.8+
- PostgreSQL 12+

### Steps

1. **Clone or download the module**:
   ```bash
   cd /path/to/odoo/addons
   git clone <repository-url> clothing_swap
   ```

2. **Update Odoo addons path** (if needed):
   Add the module directory to your Odoo configuration file:
   ```ini
   addons_path = /path/to/odoo/addons,/path/to/clothing_swap
   ```

3. **Restart Odoo server**:
   ```bash
   ./odoo-bin -u all -d your_database
   ```

4. **Install the module**:
   - Go to Apps menu in Odoo
   - Search for "Clothing Swap Platform"
   - Click Install

## Configuration

### Initial Setup

1. **Enable Website App**: Make sure the Website app is installed
2. **Configure Email**: Set up email configuration for notifications
3. **Create Admin User**: Assign users to "Clothing Swap Admin" group
4. **Customize Homepage**: Edit the landing page content as needed

### User Groups

- **Clothing Swap User**: Regular users who can list and swap items
- **Clothing Swap Admin**: Administrators who can moderate content

### Settings

Access settings through: `Apps → Clothing Swap → Configuration`

## Usage

### For Users

1. **Sign Up/Login**: Create account or login to existing account
2. **Browse Items**: Visit `/browse` to see available items
3. **Add Items**: Use `/add-item` to list your clothing
4. **Make Requests**: Request items through swaps or points
5. **Manage Dashboard**: Access `/my/dashboard` for personal overview

### For Admins

1. **Access Admin Panel**: Go to `Apps → Clothing Swap`
2. **Approve Items**: Review and approve pending item listings
3. **Monitor Requests**: Track swap request activity
4. **Manage Users**: View user profiles and statistics

## API Endpoints

The module provides several web endpoints:

- `/` - Landing page
- `/browse` - Browse items with filtering
- `/item/<id>` - Item detail page
- `/add-item` - Add new item form
- `/my/dashboard` - User dashboard
- `/my/items` - User's items
- `/my/requests` - User's swap requests

## Database Schema

### Main Models

- **clothing.item**: Clothing items with images and metadata
- **swap.request**: Swap requests between users
- **user.profile**: Extended user profiles with points and statistics
- **clothing.item.image**: Additional images for items

### Key Fields

#### Clothing Item
- `name`: Item title
- `description`: Detailed description
- `category`: Clothing category (tops, bottoms, etc.)
- `size`: Clothing size
- `condition`: Item condition
- `points_value`: Points required for redemption
- `state`: Item status (draft, pending, available, swapped)

#### Swap Request
- `request_type`: Either 'swap' or 'points'
- `requester_id`: User making the request
- `owner_id`: Item owner
- `item_id`: Requested item
- `offered_item_id`: Item offered in exchange (for swaps)
- `points_used`: Points used (for points redemption)
- `state`: Request status

## Customization

### Adding Custom Fields

1. Inherit the models in a custom module
2. Add your fields to the forms and views
3. Update security rules if needed

Example:
```python
class ClothingItem(models.Model):
    _inherit = 'clothing.item'
    
    custom_field = fields.Char('Custom Field')
```

### Styling

Customize the appearance by modifying:
- `static/src/css/clothing_swap.css`
- Website theme settings
- QWeb templates in `views/website_templates.xml`

### Adding Categories

Modify the category selection in `models/clothing_item.py`:

```python
category = fields.Selection([
    ('tops', 'Tops'),
    ('bottoms', 'Bottoms'),
    # Add your categories here
], string='Category', required=True)
```

## Development

### Running Tests

```bash
./odoo-bin -d test_db -i clothing_swap --test-enable --log-level=test
```

### Code Structure

```
clothing_swap/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py
├── models/
│   ├── __init__.py
│   ├── clothing_item.py
│   ├── swap_request.py
│   ├── user_profile.py
│   └── res_users.py
├── views/
│   ├── website_templates.xml
│   ├── portal_templates.xml
│   ├── clothing_item_views.xml
│   ├── swap_request_views.xml
│   ├── user_profile_views.xml
│   └── menu_views.xml
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
├── data/
│   └── website_data.xml
└── static/
    └── src/
        ├── css/
        │   └── clothing_swap.css
        └── js/
            └── clothing_swap.js
```

## Troubleshooting

### Common Issues

1. **Images not loading**: Check file permissions and web server configuration
2. **Email notifications not working**: Verify email server settings
3. **Permission errors**: Check user groups and security rules
4. **Website not accessible**: Ensure website app is installed and configured

### Logs

Check Odoo logs for detailed error information:
```bash
tail -f /var/log/odoo/odoo.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This module is licensed under LGPL-3.0. See LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check Odoo community forums

## Roadmap

### Planned Features
- Mobile app support
- Advanced search with AI recommendations
- Social features (reviews, favorites)
- Integration with shipping services
- Multi-language support
- Payment gateway integration for premium features

### Version History
- v1.0.0: Initial release with core features
- v1.1.0: Added admin moderation features
- v1.2.0: Enhanced user interface and mobile responsiveness

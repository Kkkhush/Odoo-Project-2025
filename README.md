# 👕 Clothing Swap Platform - Odoo Project 2025

A comprehensive clothing swap platform built with Flask (demo) and a full Odoo module implementation. This project enables users to exchange clothing items through a points-based system or direct swaps, promoting sustainable fashion.

## 🌟 Features

### 🔥 Core Features
- **User Authentication**: Secure registration and login system
- **Clothing Item Management**: Add, browse, and manage clothing listings
- **Smart Swap System**: Points-based and direct item exchange
- **Admin Panel**: Comprehensive administrative interface
- **Image Upload**: Support for clothing item photos
- **Search & Filter**: Advanced filtering by category, size, condition
- **Responsive Design**: Mobile-friendly interface with Bootstrap 5

### 🛡️ Admin Features
- User management with role-based access
- Order/swap request moderation
- Listing management and content moderation
- Database optimization tools
- Analytics and reporting

### 🏗️ Technical Features
- **Dual Implementation**: Flask demo + Full Odoo module
- **Optimized SQLite Backend**: WAL mode, indexing, connection pooling
- **Database Management**: Automated backups, integrity checks, optimization
- **Error Handling**: Comprehensive error management and logging
- **Performance Optimized**: Lazy loading, query optimization, caching

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Flask and dependencies (for demo)
- Odoo 16+ (for full implementation)

### Flask Demo Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Kkkhush/Odoo-Project-2025.git
   cd Odoo-Project-2025
   ```

2. **Install dependencies**
   ```bash
   pip install flask flask-sqlalchemy flask-login werkzeug
   ```

3. **Run the application**
   ```bash
   python demo_app.py
   ```

4. **Access the application**
   - Open your browser to `http://localhost:5000`
   - Login with demo credentials:
     - **Admin**: `admin` / `admin123`
     - **Test Users**: `alice` / `password123`, `bob` / `password123`

### Odoo Module Setup

1. **Copy the module**
   ```bash
   cp -r clothing_swap /path/to/odoo/addons/
   ```

2. **Update Odoo addons list**
   ```bash
   ./odoo-bin -u all -d your_database
   ```

3. **Install the module**
   - Go to Apps → Search "Clothing Swap" → Install

## 📁 Project Structure

```
├── 📄 demo_app.py              # Flask demo application
├── 📄 database_config.py       # Database configuration
├── 📄 database_utils.py        # Database utilities and maintenance
├── 📄 .gitignore              # Git ignore rules
├── 📄 README.md               # This file
├── 📁 clothing_swap/          # Odoo module
│   ├── 📄 __manifest__.py     # Module manifest
│   ├── 📁 models/             # Data models
│   ├── 📁 views/              # XML views
│   ├── 📁 controllers/        # Web controllers
│   ├── 📁 security/           # Access rights
│   ├── 📁 data/               # Demo data
│   └── 📁 static/             # CSS/JS assets
├── 📁 templates/              # Flask templates
│   ├── 📄 base.html           # Base template
│   ├── 📄 index.html          # Landing page
│   ├── 📁 admin/              # Admin templates
│   └── 📄 ...                 # Other templates
├── 📁 static/                 # Static assets
└── 📁 instance/               # Database files (ignored)
```

## 🎯 Key Components

### Flask Demo (`demo_app.py`)
- **Models**: User, ClothingItem, SwapRequest with SQLAlchemy
- **Routes**: Complete web application with 15+ endpoints
- **Admin Panel**: Full administrative interface matching wireframe design
- **Database**: Optimized SQLite with WAL mode and indexing

### Odoo Module (`clothing_swap/`)
- **Models**: Integrated with Odoo ORM
- **Views**: List, form, and kanban views
- **Website Integration**: Portal and public pages
- **Security**: Role-based access control
- **Workflow**: Automated swap processing

### Database Architecture
```sql
Users (User Authentication & Points)
├── ClothingItems (Item Listings)
│   └── SwapRequests (Exchange Requests)
│       ├── Requester → User
│       ├── Owner → User
│       ├── Item → ClothingItem
│       └── OfferedItem → ClothingItem
```

## 🎨 UI/UX Features

### Landing Page
- Hero section with featured items
- Categories grid (6 clothing categories)
- Product listings (responsive card layout)
- How-it-works section

### Admin Panel
- Clean dashboard with tabbed navigation
- User management with avatar display
- Order tracking and moderation
- Listing management with image previews

### Responsive Design
- Mobile-first approach
- Bootstrap 5 components
- Hover effects and animations
- Clean, modern interface

## 🔧 Database Features

### Optimization
- **WAL Mode**: Better concurrency for SQLite
- **Indexing**: Strategic indexes on frequently queried columns
- **Connection Pooling**: Efficient database connections
- **Query Optimization**: Lazy loading and optimized relationships

### Maintenance
- **Automated Backups**: Daily backup creation with retention
- **Integrity Checks**: Regular database validation
- **Optimization**: ANALYZE and VACUUM operations
- **Monitoring**: Performance tracking and logging

## 📊 Performance Features

- **Lazy Loading**: Dynamic relationship loading
- **Caching**: Query result caching
- **Pagination**: Efficient large dataset handling
- **Image Optimization**: Secure file upload handling
- **Error Recovery**: Graceful error handling with rollback

## 🛠️ Development Tools

### Database Management
```python
# Check database health
python database_utils.py

# Manual optimization
from database_utils import optimize_database
optimize_database()
```

### Admin Features
- User role management
- Content moderation
- Analytics dashboard
- System maintenance tools

## 🔐 Security Features

- **SQL Injection Protection**: Parameterized queries
- **CSRF Protection**: Flask-WTF integration ready
- **File Upload Security**: Secure filename handling
- **Access Control**: Role-based permissions
- **Data Validation**: Input sanitization

## 📈 Scalability Considerations

- **Database**: Easily upgradeable to PostgreSQL/MySQL
- **Caching**: Redis integration ready
- **API**: RESTful endpoints for mobile apps
- **Microservices**: Modular architecture
- **Cloud Ready**: Docker deployment ready

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Bootstrap 5 for responsive design
- FontAwesome for icons
- Flask community for excellent documentation
- Odoo community for framework support

## 📞 Support

For support, email your-email@example.com or create an issue in this repository.

---

**Made with ❤️ for sustainable fashion and community sharing**

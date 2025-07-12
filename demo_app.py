"""
Clothing Swap Platform - Flask Demo
A simplified version of the Odoo clothing swap module for demonstration
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import sqlite3
from sqlalchemy import event
from sqlalchemy.engine import Engine
from database_config import DatabaseConfig
from database_utils import DatabaseManager

app = Flask(__name__)

# Enhanced SQLite Configuration
app.config['SECRET_KEY'] = 'clothing-swap-secret-key'
# Use absolute path for database
db_path = os.path.join(os.getcwd(), 'instance', 'clothing_swap.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {
        'check_same_thread': False,
        'timeout': 20
    }
}
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file upload

# Ensure necessary directories exist
os.makedirs('instance', exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
print(f"Database path: {db_path}")

# SQLite optimization: Enable WAL mode and foreign keys
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if 'sqlite' in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys=ON")
        # Enable WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        # Optimize for performance
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models with improved indexing and constraints
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(120), nullable=False)
    points_balance = db.Column(db.Integer, default=50, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships with improved lazy loading
    items = db.relationship('ClothingItem', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    sent_requests = db.relationship('SwapRequest', foreign_keys='SwapRequest.requester_id', 
                                  backref='requester', lazy='dynamic', cascade='all, delete-orphan')
    received_requests = db.relationship('SwapRequest', foreign_keys='SwapRequest.owner_id', 
                                      backref='item_owner', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class ClothingItem(db.Model):
    __tablename__ = 'clothing_item'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    size = db.Column(db.String(10), nullable=False, index=True)
    condition = db.Column(db.String(20), nullable=False, index=True)
    brand = db.Column(db.String(50), index=True)
    color = db.Column(db.String(30), index=True)
    points_value = db.Column(db.Integer, default=10, nullable=False)
    image_filename = db.Column(db.String(100))
    state = db.Column(db.String(20), default='available', nullable=False, index=True)  # available, reserved, swapped
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Foreign keys with proper constraints
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Relationships with improved lazy loading
    swap_requests = db.relationship('SwapRequest', foreign_keys='SwapRequest.item_id', 
                                  backref='item', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ClothingItem {self.name}>'

class SwapRequest(db.Model):
    __tablename__ = 'swap_request'
    
    id = db.Column(db.Integer, primary_key=True)
    request_type = db.Column(db.String(20), nullable=False, index=True)  # swap or points
    message = db.Column(db.Text)
    points_used = db.Column(db.Integer, default=0, nullable=False)
    state = db.Column(db.String(20), default='pending', nullable=False, index=True)  # pending, accepted, rejected, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Foreign keys with proper constraints
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('clothing_item.id', ondelete='CASCADE'), nullable=False, index=True)
    offered_item_id = db.Column(db.Integer, db.ForeignKey('clothing_item.id', ondelete='SET NULL'))
    
    def __repr__(self):
        return f'<SwapRequest {self.id} - {self.state}>'

# Database helper functions 
def get_db_connection():
    """Get a direct SQLite connection for raw queries if needed"""
    db_path = os.path.join('instance', 'clothing_swap.db')
    return sqlite3.connect(db_path)

def optimize_database():
    """Run database optimization queries"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("ANALYZE")
        cursor.execute("VACUUM")
        conn.commit()
        conn.close()
        print("Database optimized successfully")
        return True
    except Exception as e:
        print(f"Database optimization failed: {e}")
        return False

def check_database_integrity():
    """Check database integrity"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        conn.close()
        return result[0] == 'ok'
    except Exception as e:
        print(f"Database integrity check failed: {e}")
        return False

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        print(f"Error loading user {user_id}: {e}")
        return None

# Database operation error handling decorator
def handle_db_errors(f):
    """Decorator to handle database errors gracefully"""
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            db.session.rollback()
            print(f"Database error in {f.__name__}: {e}")
            flash('A database error occurred. Please try again.')
            return redirect(url_for('index'))
    wrapper.__name__ = f.__name__
    return wrapper

# Routes
@app.route('/')
def index():
    featured_items = ClothingItem.query.filter_by(state='available').limit(6).all()
    total_items = ClothingItem.query.filter_by(state='available').count()
    total_users = User.query.count()
    total_swaps = SwapRequest.query.filter_by(state='completed').count()
    
    return render_template('index.html', 
                         featured_items=featured_items,
                         total_items=total_items,
                         total_users=total_users,
                         total_swaps=total_swaps)

@app.route('/register', methods=['GET', 'POST'])
@handle_db_errors
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You received 50 welcome points.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    my_items = ClothingItem.query.filter_by(owner_id=current_user.id).limit(5).all()
    my_requests = SwapRequest.query.filter_by(requester_id=current_user.id).limit(5).all()
    
    return render_template('dashboard.html', 
                         my_items=my_items,
                         my_requests=my_requests)

@app.route('/browse')
def browse():
    category = request.args.get('category', '')
    size = request.args.get('size', '')
    search = request.args.get('search', '')
    
    query = ClothingItem.query.filter_by(state='available')
    
    if category:
        query = query.filter_by(category=category)
    if size:
        query = query.filter_by(size=size)
    if search:
        query = query.filter(ClothingItem.name.contains(search))
    
    items = query.all()
    
    categories = ['tops', 'bottoms', 'dresses', 'outerwear', 'shoes', 'accessories']
    sizes = ['xs', 's', 'm', 'l', 'xl', 'xxl']
    
    return render_template('browse.html', 
                         items=items,
                         categories=categories,
                         sizes=sizes,
                         current_category=category,
                         current_size=size,
                         current_search=search)

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    item = ClothingItem.query.get_or_404(item_id)
    can_request = current_user.is_authenticated and current_user.id != item.owner_id
    
    user_items = []
    if current_user.is_authenticated:
        user_items = ClothingItem.query.filter_by(
            owner_id=current_user.id, 
            state='available'
        ).filter(ClothingItem.id != item_id).all()
    
    return render_template('item_detail.html', 
                         item=item,
                         can_request=can_request,
                         user_items=user_items)

@app.route('/add-item', methods=['GET', 'POST'])
@login_required
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        size = request.form['size']
        condition = request.form['condition']
        brand = request.form.get('brand', '')
        color = request.form.get('color', '')
        points_value = int(request.form.get('points_value', 10))
        
        # Handle file upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                image_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        
        item = ClothingItem(
            name=name,
            description=description,
            category=category,
            size=size,
            condition=condition,
            brand=brand,
            color=color,
            points_value=points_value,
            image_filename=image_filename,
            owner_id=current_user.id
        )
        
        db.session.add(item)
        db.session.commit()
        
        flash('Item added successfully!')
        return redirect(url_for('dashboard'))
    
    categories = ['tops', 'bottoms', 'dresses', 'outerwear', 'shoes', 'accessories']
    sizes = ['xs', 's', 'm', 'l', 'xl', 'xxl']
    conditions = ['new', 'excellent', 'good', 'fair']
    
    return render_template('add_item.html',
                         categories=categories,
                         sizes=sizes,
                         conditions=conditions)

@app.route('/request-item', methods=['POST'])
@login_required
def request_item():
    item_id = int(request.form['item_id'])
    request_type = request.form['request_type']
    message = request.form.get('message', '')
    
    item = ClothingItem.query.get_or_404(item_id)
    
    if item.owner_id == current_user.id:
        flash('You cannot request your own item')
        return redirect(url_for('item_detail', item_id=item_id))
    
    swap_request = SwapRequest(
        requester_id=current_user.id,
        owner_id=item.owner_id,
        item_id=item_id,
        request_type=request_type,
        message=message
    )
    
    if request_type == 'points':
        points_used = int(request.form.get('points_used', 0))
        if points_used > current_user.points_balance:
            flash('Insufficient points')
            return redirect(url_for('item_detail', item_id=item_id))
        swap_request.points_used = points_used
    else:
        offered_item_id = request.form.get('offered_item_id')
        if offered_item_id:
            swap_request.offered_item_id = int(offered_item_id)
    
    db.session.add(swap_request)
    db.session.commit()
    
    flash('Request sent successfully!')
    return redirect(url_for('dashboard'))

@app.route('/my-requests')
@login_required
def my_requests():
    sent_requests = SwapRequest.query.filter_by(requester_id=current_user.id).all()
    received_requests = SwapRequest.query.filter_by(owner_id=current_user.id).all()
    
    return render_template('my_requests.html',
                         sent_requests=sent_requests,
                         received_requests=received_requests)

@app.route('/accept-request/<int:request_id>')
@login_required
def accept_request(request_id):
    swap_request = SwapRequest.query.get_or_404(request_id)
    
    if swap_request.owner_id != current_user.id:
        flash('Unauthorized')
        return redirect(url_for('my_requests'))
    
    swap_request.state = 'accepted'
    swap_request.item.state = 'reserved'
    
    if swap_request.request_type == 'points':
        # Transfer points
        current_user.points_balance += swap_request.points_used
        swap_request.requester.points_balance -= swap_request.points_used
    
    db.session.commit()
    flash('Request accepted!')
    return redirect(url_for('my_requests'))

@app.route('/reject-request/<int:request_id>')
@login_required
def reject_request(request_id):
    swap_request = SwapRequest.query.get_or_404(request_id)
    
    if swap_request.owner_id != current_user.id:
        flash('Unauthorized')
        return redirect(url_for('my_requests'))
    
    swap_request.state = 'rejected'
    db.session.commit()
    
    flash('Request rejected')
    return redirect(url_for('my_requests'))

# Admin Panel Routes
@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    # Get data for admin panel
    users = User.query.all()
    orders = SwapRequest.query.all()
    listings = ClothingItem.query.all()
    
    return render_template('admin/admin_panel.html', 
                         users=users, 
                         orders=orders, 
                         listings=listings)

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@app.route('/admin/orders')
@login_required
def admin_orders():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    orders = SwapRequest.query.all()
    return render_template('admin/manage_orders.html', orders=orders)

@app.route('/admin/listings')
@login_required
def admin_listings():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    listings = ClothingItem.query.all()
    return render_template('admin/manage_listings.html', listings=listings)

@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Cannot delete admin user.')
        return redirect(url_for('admin_users'))
    
    # Delete user's items and requests
    ClothingItem.query.filter_by(owner_id=user_id).delete()
    SwapRequest.query.filter((SwapRequest.requester_id == user_id) | (SwapRequest.owner_id == user_id)).delete()
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully.')
    return redirect(url_for('admin_users'))

@app.route('/admin/delete-listing/<int:item_id>', methods=['POST'])
@login_required
def admin_delete_listing(item_id):
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('index'))
    
    item = ClothingItem.query.get_or_404(item_id)
    # Delete related swap requests
    SwapRequest.query.filter_by(item_id=item_id).delete()
    db.session.delete(item)
    db.session.commit()
    
    flash('Listing deleted successfully.')
    return redirect(url_for('admin_listings'))

# Enhanced database initialization with error handling
def create_tables():
    """Create all database tables with proper error handling"""
    try:
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        # Check database integrity after creation
        if check_database_integrity():
            print("Database integrity check passed!")
        else:
            print("Warning: Database integrity check failed!")
            
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise

def init_sample_data():
    """Initialize sample data with transaction handling"""
    try:
        # Check if data already exists
        if User.query.count() > 0:
            print("Sample data already exists, skipping initialization.")
            return
            
        print("Creating sample data...")
        
        # Create sample users
        admin = User(
            username='admin',
            email='admin@clothing-swap.com',
            password_hash=generate_password_hash('admin123'),
            points_balance=100,
            is_admin=True
        )
        
        user1 = User(
            username='alice',
            email='alice@example.com',
            password_hash=generate_password_hash('password123'),
            points_balance=75
        )
        
        user2 = User(
            username='bob',
            email='bob@example.com',
            password_hash=generate_password_hash('password123'),
            points_balance=60
        )
        
        # Add users in a transaction
        db.session.add_all([admin, user1, user2])
        db.session.commit()
        print("Sample users created successfully!")
        
        # Create sample items
        items = [
            ClothingItem(
                name='Vintage Denim Jacket',
                description='Classic vintage denim jacket from the 90s. Perfect condition with minimal wear.',
                category='outerwear',
                size='m',
                condition='excellent',
                brand='Levi\'s',
                color='Blue',
                points_value=15,
                owner_id=user1.id
            ),
            ClothingItem(
                name='Summer Floral Dress',
                description='Beautiful summer dress with floral pattern. Light and comfortable.',
                category='dresses',
                size='s',
                condition='good',
                brand='Zara',
                color='Pink',
                points_value=12,
                owner_id=user2.id
            ),
            ClothingItem(
                name='Business Casual Shirt',
                description='Professional button-down shirt, perfect for office wear.',
                category='tops',
                size='l',
                condition='excellent',
                brand='Hugo Boss',
                color='White',
                points_value=18,
                owner_id=admin.id
            ),
            ClothingItem(
                name='Casual Sneakers',
                description='Comfortable casual sneakers, perfect for everyday wear.',
                category='shoes',
                size='9',
                condition='good',
                brand='Nike',
                color='White',
                points_value=14,
                owner_id=user1.id
            ),
            ClothingItem(
                name='Designer Handbag',
                description='Elegant designer handbag, barely used.',
                category='accessories',
                size='one-size',
                condition='excellent',
                brand='Coach',
                color='Black',
                points_value=25,
                owner_id=user2.id
            )
        ]
        
        db.session.add_all(items)
        db.session.commit()
        print("Sample items created successfully!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.session.rollback()
        raise

def initialize_database():
    """Initialize the complete database with error handling"""
    try:
        print("Initializing database...")
        create_tables()
        init_sample_data()
        print("Database initialization completed!")
        
        # Run optimization after initialization
        optimize_database()
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False
    return True

if __name__ == '__main__':
    print("=== Clothing Swap Platform Starting ===")
    
    with app.app_context():
        # Initialize database with proper error handling
        if not initialize_database():
            print("Failed to initialize database. Exiting...")
            exit(1)
    
    print("Starting Flask development server...")
    print("Admin login: admin / admin123")
    print("Test users: alice / password123, bob / password123")
    print("Access the application at: http://localhost:5000")
    print("========================================")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        print("Cleaning up...")
        with app.app_context():
            optimize_database()

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jewelry.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    metal_type = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    sub_category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    customer_name = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    gstin = db.Column(db.String(30))
    address = db.Column(db.String(200))
    state = db.Column(db.String(50))
    state_code = db.Column(db.String(10))
    bills = db.relationship('Bill', backref='customer', lazy=True)

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    customer_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    gstin = db.Column(db.String(30))
    address = db.Column(db.String(200))
    state = db.Column(db.String(50))
    state_code = db.Column(db.String(10))
    payment_method = db.Column(db.String(20))
    upi = db.Column(db.String(50))
    card = db.Column(db.String(50))
    gst = db.Column(db.Float, default=0.0)
    sgst = db.Column(db.Float, default=0.0)
    cgst = db.Column(db.Float, default=0.0)
    discount = db.Column(db.Float, default=0.0)
    making_charges = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    pdf_path = db.Column(db.String(200))
    items = db.relationship('BillItem', backref='bill', cascade='all, delete-orphan')

class BillItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    gross_wt = db.Column(db.Float, nullable=True)
    net_wt = db.Column(db.Float, nullable=True)
    rate = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
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
    return render_template('dashboard.html')

@app.route('/sales/new', methods=['GET', 'POST'])
@login_required
def new_sale():
    if request.method == 'POST':
        sale = Sale(
            date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
            metal_type=request.form['metal_type'],
            category=request.form['category'],
            sub_category=request.form['sub_category'],
            quantity=int(request.form['quantity']),
            unit_price=float(request.form['unit_price']),
            total_amount=float(request.form['quantity']) * float(request.form['unit_price']),
            payment_method=request.form['payment_method'],
            customer_name=request.form['customer_name'],
            notes=request.form['notes'],
            created_by=current_user.id
        )
        db.session.add(sale)
        db.session.commit()
        flash('Sale recorded successfully!')
        return redirect(url_for('dashboard'))
    return render_template('new_sale.html')

@app.route('/api/sales')
@login_required
def get_sales():
    sales = Sale.query.all()
    return jsonify([{
        'id': sale.id,
        'date': sale.date.strftime('%Y-%m-%d'),
        'metal_type': sale.metal_type,
        'category': sale.category,
        'sub_category': sale.sub_category,
        'quantity': sale.quantity,
        'unit_price': sale.unit_price,
        'total_amount': sale.total_amount,
        'payment_method': sale.payment_method,
        'customer_name': sale.customer_name
    } for sale in sales])

@app.route('/api/summary')
@login_required
def get_summary():
    sales = Sale.query.all()
    summary = {
        'total_sales': sum(sale.total_amount for sale in sales),
        'total_items': sum(sale.quantity for sale in sales),
        'gold_sales': sum(sale.total_amount for sale in sales if sale.metal_type == 'Gold'),
        'silver_sales': sum(sale.total_amount for sale in sales if sale.metal_type == 'Silver'),
        'gold_items': sum(sale.quantity for sale in sales if sale.metal_type == 'Gold'),
        'silver_items': sum(sale.quantity for sale in sales if sale.metal_type == 'Silver')
    }
    return jsonify(summary)

@app.route('/api/sales/<int:sale_id>', methods=['DELETE'])
@login_required
def delete_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    db.session.delete(sale)
    db.session.commit()
    return jsonify({'message': 'Sale deleted successfully'})

@app.route('/bills/new', methods=['GET', 'POST'])
@login_required
def new_bill():
    customers = Customer.query.all()
    if request.method == 'POST':
        # Handle bill creation (to be implemented)
        pass
    return render_template('new_bill.html', customers=customers)

@app.route('/api/customers/search')
@login_required
def search_customers():
    q = request.args.get('q', '')
    results = Customer.query.filter(
        (Customer.name.ilike(f'%{q}%')) | (Customer.phone.ilike(f'%{q}%'))
    ).all()
    return jsonify([
        {
            'id': c.id,
            'name': c.name,
            'phone': c.phone,
            'gstin': c.gstin,
            'address': c.address,
            'state': c.state,
            'state_code': c.state_code
        } for c in results
    ])

@app.route('/api/customers/<int:customer_id>')
@login_required
def get_customer(customer_id):
    c = Customer.query.get_or_404(customer_id)
    return jsonify({
        'id': c.id,
        'name': c.name,
        'phone': c.phone,
        'gstin': c.gstin,
        'address': c.address,
        'state': c.state,
        'state_code': c.state_code
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True) 
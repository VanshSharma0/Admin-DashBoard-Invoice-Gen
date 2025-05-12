from app import app, db, User, Customer, Bill, BillItem
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Drop all existing tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create admin user
        admin = User(
            username='admin',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create a sample customer
        customer = Customer(
            name='Sample Customer',
            phone='1234567890',
            gstin='22AAAAA0000A1Z5',
            address='123 Main Street',
            state='Delhi',
            state_code='07'
        )
        db.session.add(customer)
        
        # Commit the changes
        db.session.commit()
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
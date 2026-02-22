"""
Seed data script for initializing the database with sample data
Run: python seed_data.py
"""
from app import create_app, db
from app.models.user import User
from app.models.lost_item import LostItem
from app.models.found_item import FoundItem
from app.models.match import Match
from app.models.claim import Claim
from app.models.notification import Notification
from datetime import datetime, date, timedelta
import random

def seed_database():
    """Seed the database with initial data"""
    app = create_app()
    
    with app.app_context():
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("Clearing existing data...")
        Claim.query.delete()
        Match.query.delete()
        Notification.query.delete()
        LostItem.query.delete()
        FoundItem.query.delete()
        User.query.delete()
        db.session.commit()
        
        # Create admin user
        print("Creating admin user...")
        admin = User(
            name='Admin User',
            email='admin@seait.edu',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create staff user
        print("Creating staff user...")
        staff = User(
            name='Staff Officer',
            email='staff@seait.edu',
            role='staff'
        )
        staff.set_password('staff123')
        db.session.add(staff)
        
        # Create student users
        print("Creating student users...")
        students = []
        for i in range(5):
            student = User(
                name=f'Student {i+1}',
                email=f'student{i+1}@seait.edu',
                role='student'
            )
            student.set_password('student123')
            students.append(student)
            db.session.add(student)
        
        db.session.commit()
        print("Users created successfully!")
        
        # Create sample lost items
        print("Creating sample lost items...")
        lost_items_data = [
            {
                'item_name': 'Student ID Card',
                'description': 'Blue ID card with photo, student number 2023-001',
                'category': 'ID',
                'color': 'Blue',
                'date_lost': date.today() - timedelta(days=5),
                'location_lost': 'Library Building',
                'status': 'pending'
            },
            {
                'item_name': 'iPhone 13',
                'description': 'Black iPhone 13 with white case',
                'category': 'Phone',
                'color': 'Black',
                'date_lost': date.today() - timedelta(days=3),
                'location_lost': 'Cafeteria',
                'status': 'pending'
            },
            {
                'item_name': 'Leather Wallet',
                'description': 'Brown leather wallet with credit cards inside',
                'category': 'Wallet',
                'color': 'Brown',
                'date_lost': date.today() - timedelta(days=7),
                'location_lost': 'Parking Lot',
                'status': 'pending'
            },
            {
                'item_name': 'Backpack',
                'description': 'Red backpack with laptop compartment',
                'category': 'Bag',
                'color': 'Red',
                'date_lost': date.today() - timedelta(days=2),
                'location_lost': 'Classroom 101',
                'status': 'pending'
            },
            {
                'item_name': 'Keys',
                'description': 'Keychain with 5 keys and a car key',
                'category': 'Keys',
                'color': 'Silver',
                'date_lost': date.today() - timedelta(days=1),
                'location_lost': 'Gymnasium',
                'status': 'pending'
            }
        ]
        
        lost_items = []
        for i, data in enumerate(lost_items_data):
            lost_item = LostItem(
                user_id=students[i % len(students)].id,
                **data
            )
            lost_items.append(lost_item)
            db.session.add(lost_item)
        
        db.session.commit()
        print("Lost items created successfully!")
        
        # Create sample found items
        print("Creating sample found items...")
        found_items_data = [
            {
                'item_name': 'Student ID Card',
                'description': 'Blue ID card found near library entrance',
                'category': 'ID',
                'color': 'Blue',
                'date_found': date.today() - timedelta(days=4),
                'location_found': 'Library Entrance',
                'storage_location': 'Lost and Found Office - Drawer A',
                'priority_flag': True,
                'status': 'available'
            },
            {
                'item_name': 'Smartphone',
                'description': 'Black smartphone with cracked screen',
                'category': 'Phone',
                'color': 'Black',
                'date_found': date.today() - timedelta(days=2),
                'location_found': 'Cafeteria Table 5',
                'storage_location': 'Lost and Found Office - Safe',
                'priority_flag': True,
                'status': 'available'
            },
            {
                'item_name': 'Wallet',
                'description': 'Brown leather wallet, empty',
                'category': 'Wallet',
                'color': 'Brown',
                'date_found': date.today() - timedelta(days=6),
                'location_found': 'Parking Lot Area B',
                'storage_location': 'Lost and Found Office - Drawer B',
                'priority_flag': True,
                'status': 'available'
            },
            {
                'item_name': 'Water Bottle',
                'description': 'Blue water bottle with logo',
                'category': 'Other',
                'color': 'Blue',
                'date_found': date.today() - timedelta(days=1),
                'location_found': 'Gymnasium',
                'storage_location': 'Lost and Found Office - Shelf 1',
                'priority_flag': False,
                'status': 'available'
            },
            {
                'item_name': 'Notebook',
                'description': 'Spiral notebook with math notes',
                'category': 'Books',
                'color': 'Yellow',
                'date_found': date.today() - timedelta(days=3),
                'location_found': 'Classroom 205',
                'storage_location': 'Lost and Found Office - Shelf 2',
                'priority_flag': False,
                'status': 'available'
            }
        ]
        
        found_items = []
        for data in found_items_data:
            found_item = FoundItem(
                staff_id=staff.id,
                **data
            )
            found_items.append(found_item)
            db.session.add(found_item)
        
        db.session.commit()
        print("Found items created successfully!")
        
        # Create sample matches using AI matcher
        print("Creating sample matches...")
        from app.services.lost_found_matcher import LostFoundMatcher
        matcher = LostFoundMatcher()
        
        for lost_item in lost_items:
            for found_item in found_items:
                lost_dict = {
                    'id': lost_item.id,
                    'item_name': lost_item.item_name,
                    'description': lost_item.description or '',
                    'category': lost_item.category,
                    'color': lost_item.color or ''
                }
                found_dict = {
                    'id': found_item.id,
                    'item_name': found_item.item_name,
                    'description': found_item.description or '',
                    'category': found_item.category,
                    'color': found_item.color or ''
                }
                
                score = matcher.calculate_match_score(lost_dict, found_dict)
                
                if score >= 50.0:
                    match = Match(
                        lost_item_id=lost_item.id,
                        found_item_id=found_item.id,
                        score=score,
                        status='suggested'
                    )
                    db.session.add(match)
                    
                    # Create notification
                    notification = Notification(
                        user_id=lost_item.user_id,
                        message=f"Potential match found for '{lost_item.item_name}' (Match Score: {score}%)",
                        is_read=False
                    )
                    db.session.add(notification)
        
        db.session.commit()
        print("Matches and notifications created successfully!")
        
        print("\n" + "="*50)
        print("Seed data created successfully!")
        print("="*50)
        print("\nLogin credentials:")
        print("Admin: admin@seait.edu / admin123")
        print("Staff: staff@seait.edu / staff123")
        print("Student: student1@seait.edu / student123")
        print("="*50)

if __name__ == '__main__':
    seed_database()

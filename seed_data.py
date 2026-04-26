"""
High-volume seed data script for realistic lost-and-found operations.
Run: python seed_data.py
"""
from datetime import date, datetime, timedelta
import random

from app import create_app, db
from app.models.user import User
from app.models.lost_item import LostItem
from app.models.found_item import FoundItem
from app.models.match import Match
from app.models.claim import Claim
from app.models.notification import Notification
from app.models.interaction_log import InteractionLog


def random_date_between(start_date, end_date):
    """Return random date in [start_date, end_date]."""
    span_days = (end_date - start_date).days
    return start_date + timedelta(days=random.randint(0, max(span_days, 0)))


def random_dt_on(day):
    """Return datetime on a specific date."""
    return datetime.combine(day, datetime.min.time()) + timedelta(
        hours=random.randint(7, 18),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )


def seed_database():
    """Seed the database with 1,000+ timeline-rich records."""
    random.seed(20260426)
    app = create_app()

    with app.app_context():
        print("Clearing existing data...")
        InteractionLog.query.delete()
        Claim.query.delete()
        Match.query.delete()
        Notification.query.delete()
        LostItem.query.delete()
        FoundItem.query.delete()
        User.query.delete()
        db.session.commit()

        print("Creating users...")
        admin = User(name='Admin User', email='admin@seait.edu', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)

        staff_users = []
        for i in range(1, 11):
            email = 'staff@seait.edu' if i == 1 else f'staff{i}@seait.edu'
            staff = User(name=f'Staff Officer {i}', email=email, role='staff')
            staff.set_password('staff123')
            staff_users.append(staff)
            db.session.add(staff)

        students = []
        for i in range(1, 121):
            email = 'student1@seait.edu' if i == 1 else f'student{i}@seait.edu'
            student = User(name=f'Student {i}', email=email, role='student')
            student.set_password('student123')
            students.append(student)
            db.session.add(student)

        db.session.commit()

        start_date = date(2025, 11, 1)
        end_date = date.today()
        categories = ['ID', 'Phone', 'Wallet', 'Keys', 'Bag', 'Books', 'Laptop', 'Other']
        colors = ['Black', 'Blue', 'Red', 'Gray', 'White', 'Green', 'Brown', 'Silver']
        locations = [
            'Library', 'Cafeteria', 'Gymnasium', 'Main Gate', 'Computer Lab',
            'Classroom 101', 'Classroom 205', 'Parking Lot', 'Student Lounge', 'Auditorium'
        ]
        storage_locations = [
            'Lost and Found Office - Drawer A', 'Lost and Found Office - Drawer B',
            'Lost and Found Office - Shelf 1', 'Lost and Found Office - Shelf 2',
            'Lost and Found Office - Safe', 'Lost and Found Office - Cabinet C'
        ]

        print("Creating lost and found inventory...")
        lost_items = []
        found_items = []
        for i in range(520):
            cat = random.choice(categories)
            item = LostItem(
                user_id=random.choice(students).id,
                item_name=f'{cat} Item {i + 1}',
                description=f'{cat} reported missing by student',
                category=cat,
                color=random.choice(colors),
                date_lost=random_date_between(start_date, end_date),
                location_lost=random.choice(locations),
                status='pending',
                created_at=random_dt_on(random_date_between(start_date, end_date))
            )
            lost_items.append(item)
            db.session.add(item)

        for i in range(520):
            cat = random.choice(categories)
            found = FoundItem(
                staff_id=random.choice(staff_users).id,
                item_name=f'{cat} Item {i + 1}',
                description=f'{cat} turned over to the help desk',
                category=cat,
                color=random.choice(colors),
                date_found=random_date_between(start_date, end_date),
                location_found=random.choice(locations),
                storage_location=random.choice(storage_locations),
                priority_flag=cat in ['ID', 'Phone', 'Wallet'],
                status='available',
                created_at=random_dt_on(random_date_between(start_date, end_date))
            )
            found_items.append(found)
            db.session.add(found)

        db.session.commit()

        print("Generating transaction flow and interactions...")
        claims_created = 0
        interactions_created = 0
        matches_created = 0
        notifications_created = 0

        found_by_category = {}
        for item in found_items:
            found_by_category.setdefault(item.category, []).append(item)

        for lost_item in lost_items:
            candidates = found_by_category.get(lost_item.category, [])
            if not candidates:
                continue

            found_item = random.choice(candidates)
            score = round(random.uniform(55, 98), 2)
            match_status = random.choices(
                ['suggested', 'confirmed', 'rejected'],
                weights=[20, 65, 15],
                k=1
            )[0]
            match = Match(
                lost_item_id=lost_item.id,
                found_item_id=found_item.id,
                score=score,
                status=match_status,
                created_at=random_dt_on(random_date_between(start_date, end_date))
            )
            db.session.add(match)
            matches_created += 1

            notif = Notification(
                user_id=lost_item.user_id,
                message=f"Potential match found for '{lost_item.item_name}' ({score}%)",
                is_read=random.choice([True, False]),
                created_at=match.created_at + timedelta(minutes=random.randint(1, 120))
            )
            db.session.add(notif)
            notifications_created += 1

            log_report = InteractionLog(
                actor_id=lost_item.user_id,
                target_user_id=lost_item.user_id,
                action_type='lost_item_reported',
                title=f"Reported lost item: {lost_item.item_name}",
                description=f"Category: {lost_item.category}",
                reference_type='lost_item',
                reference_id=lost_item.id,
                created_at=lost_item.created_at
            )
            db.session.add(log_report)
            interactions_created += 1

            if match_status == 'confirmed':
                lost_item.status = 'matched'
                found_item.status = 'matched'

                claim = Claim(
                    claim_code=f'CLM-{lost_item.id:05d}-{found_item.id:05d}',
                    user_id=lost_item.user_id,
                    item_id=lost_item.id,
                    release_status='pending',
                    created_at=match.created_at + timedelta(hours=random.randint(1, 48))
                )
                db.session.add(claim)
                claims_created += 1

                db.session.add(InteractionLog(
                    actor_id=lost_item.user_id,
                    target_user_id=lost_item.user_id,
                    action_type='claim_qr_viewed',
                    title=f"Viewed QR for claim {claim.claim_code}",
                    description=f"Item: {lost_item.item_name}",
                    reference_type='claim',
                    reference_id=lost_item.id,
                    created_at=claim.created_at + timedelta(minutes=random.randint(1, 90))
                ))
                interactions_created += 1

                if random.random() < 0.75:
                    staff_actor = random.choice(staff_users)
                    claim.release_status = 'released'
                    claim.released_by = staff_actor.id
                    claim.release_date = claim.created_at + timedelta(days=random.randint(0, 10))
                    lost_item.status = 'claimed'
                    found_item.status = 'claimed'

                    db.session.add(InteractionLog(
                        actor_id=staff_actor.id,
                        target_user_id=lost_item.user_id,
                        action_type='claim_released',
                        title=f"Released item to student: {lost_item.item_name}",
                        description=f"Claim code: {claim.claim_code}",
                        reference_type='claim',
                        reference_id=lost_item.id,
                        created_at=claim.release_date
                    ))
                    interactions_created += 1

        db.session.commit()

        total_records = (
            User.query.count() +
            LostItem.query.count() +
            FoundItem.query.count() +
            Match.query.count() +
            Claim.query.count() +
            Notification.query.count() +
            InteractionLog.query.count()
        )

        print("\n" + "=" * 72)
        print("Seed data created successfully")
        print("=" * 72)
        print(f"Users: {User.query.count()}")
        print(f"Lost items: {LostItem.query.count()}")
        print(f"Found items: {FoundItem.query.count()}")
        print(f"Matches: {matches_created}")
        print(f"Claims: {claims_created}")
        print(f"Notifications: {notifications_created}")
        print(f"Interaction logs: {interactions_created}")
        print(f"TOTAL RECORDS: {total_records} (target: >= 1000)")
        print(f"Timeline coverage: {start_date} to {end_date}")
        print("-" * 72)
        print("Login credentials:")
        print("Admin: admin@seait.edu / admin123")
        print("Staff: staff@seait.edu / staff123")
        print("Student: student1@seait.edu / student123")
        print("=" * 72)


if __name__ == '__main__':
    seed_database()

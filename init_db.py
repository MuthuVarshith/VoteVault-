from app import app
from models import db, User, Candidate, Vote

with app.app_context():
    # Reset the database
    db.drop_all()
    db.create_all()

    # Create default admin account
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='admin', is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print("[✔] Admin user created (username: admin, password: admin)")
    else:
        print("[!] Admin user already exists")

    print("[✔] Database initialized successfully")

from app import db, app, User

with app.app_context():
    db.drop_all()
    db.create_all()

    admin = User(username="admin")
    admin.set_password("admin123")
    db.session.add(admin)
    db.session.commit()

    print("Database reset! Admin login = admin / admin123")

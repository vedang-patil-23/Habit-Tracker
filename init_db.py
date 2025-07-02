from app import app, db, User

def init_db():
    with app.app_context():
        db.create_all()

        # Check if users already exist to prevent duplicates
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin')
            admin_user.set_password('admin123')
            db.session.add(admin_user)

        if not User.query.filter_by(username='viewer').first():
            viewer_user = User(username='viewer')
            viewer_user.set_password('view123')
            db.session.add(viewer_user)

        db.session.commit()
        print("Database initialized and default users created.")

if __name__ == '__main__':
    init_db() 